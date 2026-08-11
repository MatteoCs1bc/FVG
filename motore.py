"""
Motore di decarbonizzazione del sistema elettrico del Friuli-Venezia Giulia.

Risponde a una domanda sola: **come si decarbonizza il FVG minimizzando costo e
import**. Il calcolo e' orario su un anno intero, e si articola in tre blocchi:

1. **ex ante** — il sistema com'e' oggi, simulato ora per ora;
2. **ottimo costo-import** — la frontiera di Pareto fra spesa, emissioni e
   dipendenza dall'estero, con la configurazione scelta;
3. **autosufficienza** — cosa serve per chiudere l'import, in due varianti:
   saldo annuo nullo (si puo' esportare d'estate e importare d'inverno) e
   import nullo in ogni ora (autarchia vera).

La regione non e' un'isola e non finge di esserlo: l'import resta una scelta
con un prezzo, non un fallimento da penalizzare al valore del carico non
servito. Tutti i prezzi sono contratti per differenza, coerenti con il modo in
cui la nuova capacita' viene effettivamente remunerata.

Il modulo non dipende da Streamlit e si puo' usare da solo.
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace
from itertools import product

import numpy as np
import pandas as pd

# ----------------------------------------------------------------- emissioni
# Ciclo di vita, gCO2 per kWh. I due riferimenti differiscono soprattutto sul
# fotovoltaico (19 contro 45): vale la pena poter cambiare e vedere se il
# risultato regge.
LCA = {
    "Politecnico di Milano (RER 2022)": {
        "pv": 19.0, "eolico": 12.0, "idro": 11.0, "gas": 436.0,
        "accumulo": 50.0, "import": 250.0},
    "IPCC": {
        "pv": 45.0, "eolico": 11.0, "idro": 24.0, "gas": 550.0,
        "accumulo": 50.0, "import": 250.0},
}

# Stagionalita' dell'idroelettrico ad acqua fluente, indice mensile sulla media
# annua. Regime alpino: magra invernale, piena di fusione fra aprile e giugno,
# magra estiva, ripresa autunnale. Ipotesi dichiarata, non misura.
IDRO_STAGIONALE = {
    1: 0.55, 2: 0.55, 3: 0.75, 4: 1.35, 5: 1.60, 6: 1.45,
    7: 1.05, 8: 0.80, 9: 0.85, 10: 1.05, 11: 1.15, 12: 0.75,
}


@dataclass
class Parco:
    """Capacita' installate. Potenze in MW, energia degli accumuli in MWh."""
    pv_mw: float = 0.0
    eolico_mw: float = 0.0
    idro_fluente_mw: float = 0.0
    idro_bacino_mw: float = 0.0
    idro_bacino_mwh: float = 0.0
    idro_afflusso_mw: float = 0.0
    bess_mw: float = 0.0
    bess_mwh: float = 0.0
    # Il termoelettrico friulano e' in larga parte cogenerazione industriale:
    # produce perche' serve vapore alla fabbrica, non perche' serve elettricita'
    # alla rete. Quella quota va trattata come must-run.
    termo_mw: float = 0.0
    termo_quota_mustrun: float = 0.5
    import_max_mw: float = 0.0
    export_max_mw: float = 0.0


# Obiettivi di calibrazione: i totali Terna 2024 per il FVG, in GWh. Il modello
# non e' credibile se non riproduce l'anno che conosciamo, quindi i coefficienti
# vengono tarati su questi valori invece che assunti.
TARGET_2024 = {
    "domanda": 9814.7, "pv": 961.4, "idro": 2163.1, "termo": 3565.6,
    "deficit": 3341.4,
}


def calibra(dati: dict, base: "Parco", target: dict | None = None,
            iterazioni: int = 12) -> tuple["Parco", dict]:
    """Tara resa fotovoltaica, afflusso idrico e must-run termoelettrico.

    Tre correzioni, ognuna con una ragione fisica:

    * **resa fotovoltaica** — PVGIS descrive un impianto nuovo e ben orientato,
      il parco reale ha falde storte, ombreggiamenti e moduli vecchi. E poi la
      produzione dell'anno si fa con la potenza *media*, non con quella di fine
      dicembre, e in FVG il parco e' raddoppiato in due anni;
    * **afflusso idrico** — la producibilita' dipende dall'idrologia dell'anno,
      che il modello non conosce: si scala sull'anno di riferimento;
    * **must-run termoelettrico** — quanta parte del parco produce comunque
      perche' e' cogenerazione industriale. E' il parametro che decide se la
      regione importa o brucia, e va misurato, non ipotizzato.
    """
    t = target or TARGET_2024
    p = replace(base)

    # 1. resa fotovoltaica: non dipende dal dispacciamento, si tara una volta
    e = simula(dati["domanda"], dati["cf_pv"], dati["cf_eolico"], p, mesi=dati.get("mesi"))
    resa_pv = t["pv"] * 1e3 / e.pv if e.pv else 1.0
    dati_pv = dict(dati, cf_pv=dati["cf_pv"] * resa_pv)

    # 2-3. idroelettrico e must-run si influenzano a vicenda: piu' cogenerazione
    # obbligata significa meno spazio per il bacino, e viceversa. Si alternano
    # le due tarature finche' non si stabilizzano.
    fattore_idro = 1.0
    for _ in range(6):
        e = simula(dati_pv["domanda"], dati_pv["cf_pv"], dati_pv["cf_eolico"], p,
                   mesi=dati.get("mesi"))
        idro = e.idro_fluente + e.idro_bacino
        if idro > 0:
            correzione = t["idro"] * 1e3 / idro
            fattore_idro *= correzione
            p = replace(p, idro_fluente_mw=p.idro_fluente_mw * correzione,
                        idro_afflusso_mw=p.idro_afflusso_mw * correzione)

        lo, hi = 0.0, 1.0
        for _ in range(iterazioni):
            quota = (lo + hi) / 2
            e = simula(dati_pv["domanda"], dati_pv["cf_pv"], dati_pv["cf_eolico"],
                       replace(p, termo_quota_mustrun=quota), mesi=dati.get("mesi"))
            if e.termo / 1e3 < t["termo"]:
                lo = quota
            else:
                hi = quota
        p = replace(p, termo_quota_mustrun=(lo + hi) / 2)

    diagnostica = {"resa_pv": resa_pv, "fattore_idro": fattore_idro,
                   "quota_mustrun": p.termo_quota_mustrun}
    return p, diagnostica


@dataclass
class Prezzi:
    """Contratti per differenza e prezzi di riferimento, €/MWh."""
    cfd_pv: float = 60.0
    cfd_eolico: float = 80.0
    cfd_idro: float = 55.0
    gas: float = 130.0
    importazione: float = 115.9
    lcos: float = 90.0


@dataclass
class CostiRete:
    """Connessione e rinforzo, €/kW di nuova potenza installata."""
    connessione_eur_kw: float = 90.0
    rinforzo_eur_kw: float = 220.0
    hosting_capacity_mw: float = 485.0
    vita_anni: int = 30
    wacc: float = 0.06

    def annualita(self) -> float:
        w = self.wacc
        return w / (1 - (1 + w) ** -self.vita_anni) if w else 1 / self.vita_anni

    def costo_annuo(self, nuova_mw: float) -> float:
        entro = min(max(nuova_mw, 0.0), self.hosting_capacity_mw)
        oltre = max(0.0, nuova_mw - self.hosting_capacity_mw)
        capex = (entro * 1000 * self.connessione_eur_kw
                 + oltre * 1000 * (self.connessione_eur_kw + self.rinforzo_eur_kw))
        return capex * self.annualita()


@dataclass
class Esito:
    """Energia annua per voce, in MWh, piu' le serie orarie se richieste."""
    domanda: float = 0.0
    pv: float = 0.0
    eolico: float = 0.0
    idro_fluente: float = 0.0
    idro_bacino: float = 0.0
    termo_mustrun: float = 0.0
    termo_modulante: float = 0.0
    bess_carica: float = 0.0
    bess_scarica: float = 0.0
    importato: float = 0.0
    esportato: float = 0.0
    curtailment: float = 0.0
    spillamento: float = 0.0
    non_servita: float = 0.0
    afflusso: float = 0.0
    ore_import: int = 0
    ore_deficit: int = 0
    import_max_orario: float = 0.0
    serie: dict = field(default_factory=dict)

    @property
    def termo(self) -> float:
        return self.termo_mustrun + self.termo_modulante

    @property
    def rinnovabile(self) -> float:
        return self.pv + self.eolico + self.idro_fluente + self.idro_bacino

    @property
    def quota_rinnovabile(self) -> float:
        return self.rinnovabile / self.domanda * 100 if self.domanda else 0.0

    @property
    def quota_import(self) -> float:
        return self.importato / self.domanda * 100 if self.domanda else 0.0

    @property
    def import_netto(self) -> float:
        return self.importato - self.esportato

    def intensita(self, riferimento: str = "Politecnico di Milano (RER 2022)") -> float:
        f = LCA.get(riferimento, LCA["Politecnico di Milano (RER 2022)"])
        g = (self.pv * f["pv"] + self.eolico * f["eolico"]
             + (self.idro_fluente + self.idro_bacino) * f["idro"]
             + self.termo * f["gas"] + self.bess_scarica * f["accumulo"]
             + self.importato * f["import"])
        return g / self.domanda if self.domanda else 0.0


def simula(
    domanda_mw: np.ndarray,
    cf_pv: np.ndarray,
    cf_eolico: np.ndarray,
    parco: Parco,
    mesi: np.ndarray | None = None,
    rendimento_bess: float = 0.90,
    serie: bool = False,
) -> Esito:
    """Dispacciamento orario.

    Ordine di merito: prima cio' che non si puo' spegnere (rinnovabili non
    programmabili, fluente, cogenerazione must-run), poi accumulo, bacino,
    import, termoelettrico modulante. L'import viene **prima** del
    termoelettrico perche' in FVG costa meno del combustibile: e' il motivo per
    cui la regione importa un terzo di quello che consuma pur avendo 1.531 MW
    termici installati.
    """
    n = len(domanda_mw)
    pv = np.clip(cf_pv, 0, 1) * parco.pv_mw
    eolico = np.clip(cf_eolico, 0, 1) * parco.eolico_mw

    if mesi is None:
        mesi = np.ones(n, dtype=int)
    stagionale = np.array([IDRO_STAGIONALE.get(int(m), 1.0) for m in mesi])
    fluente = np.minimum(parco.idro_fluente_mw * stagionale, parco.idro_fluente_mw * 1.6)
    afflusso = parco.idro_afflusso_mw * stagionale

    mustrun = parco.termo_mw * parco.termo_quota_mustrun
    modulante_max = parco.termo_mw - mustrun

    radice = np.sqrt(rendimento_bess)
    soc = 0.0
    invaso = parco.idro_bacino_mwh * 0.5

    e = Esito(domanda=float(domanda_mw.sum()), pv=float(pv.sum()),
              eolico=float(eolico.sum()), idro_fluente=float(fluente.sum()),
              termo_mustrun=float(mustrun * n))

    s_imp = np.zeros(n) if serie else None
    s_sur = np.zeros(n) if serie else None
    s_bac = np.zeros(n) if serie else None
    s_ter = np.zeros(n) if serie else None
    s_bes = np.zeros(n) if serie else None

    for t in range(n):
        invaso_pieno = invaso + afflusso[t]
        if invaso_pieno > parco.idro_bacino_mwh:
            e.spillamento += invaso_pieno - parco.idro_bacino_mwh
            invaso = parco.idro_bacino_mwh
        else:
            invaso = invaso_pieno
        e.afflusso += afflusso[t]

        saldo = pv[t] + eolico[t] + fluente[t] + mustrun - domanda_mw[t]

        if saldo > 0:
            spazio = (parco.bess_mwh - soc) / radice if radice else 0.0
            carica = min(saldo, parco.bess_mw, max(0.0, spazio))
            soc += carica * radice
            e.bess_carica += carica
            residuo = saldo - carica
            export = min(residuo, parco.export_max_mw)
            e.esportato += export
            e.curtailment += residuo - export
            if serie:
                s_sur[t] = residuo
                s_bes[t] = -carica
        else:
            manca = -saldo

            scarica = min(manca, parco.bess_mw, soc * radice)
            soc -= scarica / radice if radice else 0.0
            e.bess_scarica += scarica
            manca -= scarica
            if serie:
                s_bes[t] = scarica

            bacino = min(manca, parco.idro_bacino_mw, invaso)
            invaso -= bacino
            e.idro_bacino += bacino
            manca -= bacino
            if serie:
                s_bac[t] = bacino

            if manca > 0:
                imp = min(manca, parco.import_max_mw)
                e.importato += imp
                manca -= imp
                if imp > 0:
                    e.ore_import += 1
                    e.import_max_orario = max(e.import_max_orario, imp)
                if serie:
                    s_imp[t] = imp

            if manca > 0:
                term = min(manca, modulante_max)
                e.termo_modulante += term
                manca -= term
                if serie:
                    s_ter[t] = mustrun + term

            if manca > 0:
                e.non_servita += manca
                e.ore_deficit += 1

        if serie and s_ter[t] == 0:
            s_ter[t] = mustrun

    if serie:
        e.serie = {"pv": pv, "eolico": eolico, "fluente": fluente,
                   "import": s_imp, "surplus": s_sur, "bacino": s_bac,
                   "termo": s_ter, "accumulo": s_bes, "domanda": domanda_mw}
    return e


def costo(e: Esito, p: Prezzi, rete: CostiRete, nuova_mw: float) -> dict:
    """Costo annuo per voce, rete inclusa, e costo medio dell'energia."""
    voci = {
        "Fotovoltaico": e.pv * p.cfd_pv,
        "Eolico": e.eolico * p.cfd_eolico,
        "Idroelettrico": (e.idro_fluente + e.idro_bacino) * p.cfd_idro,
        "Termoelettrico": e.termo * p.gas,
        "Import": e.importato * p.importazione,
        "Accumulo": e.bess_scarica * p.lcos,
    }
    ricavo_export = e.esportato * p.importazione
    costo_rete = rete.costo_annuo(nuova_mw)
    totale = sum(voci.values()) + costo_rete - ricavo_export
    return {"voci": voci, "rete": costo_rete, "ricavo_export": ricavo_export,
            "totale": totale, "eur_mwh": totale / e.domanda if e.domanda else 0.0}


def valuta(dati: dict, parco: Parco, p: Prezzi, rete: CostiRete,
           base: Parco, lca: str) -> dict:
    """Simula una configurazione e restituisce tutte le grandezze di interesse."""
    e = simula(dati["domanda"], dati["cf_pv"], dati["cf_eolico"], parco,
               mesi=dati.get("mesi"))
    nuova = (max(0.0, parco.pv_mw - base.pv_mw)
             + max(0.0, parco.eolico_mw - base.eolico_mw)
             + max(0.0, parco.bess_mw - base.bess_mw))
    c = costo(e, p, rete, nuova)
    return {
        "pv_mw": parco.pv_mw, "eolico_mw": parco.eolico_mw,
        "bess_mw": parco.bess_mw, "bess_mwh": parco.bess_mwh,
        "nuova_potenza_mw": nuova,
        "eur_mwh": c["eur_mwh"], "costo_rete_mln": c["rete"] / 1e6,
        "ricavo_export_mln": c["ricavo_export"] / 1e6,
        "gco2_kwh": e.intensita(lca),
        "quota_import": e.quota_import, "quota_fer": e.quota_rinnovabile,
        "import_netto_gwh": e.import_netto / 1e3,
        "ore_import": e.ore_import, "ore_deficit": e.ore_deficit,
        "import_punta_mw": e.import_max_orario,
        "gwh_pv": e.pv / 1e3, "gwh_eolico": e.eolico / 1e3,
        "gwh_idro_fluente": e.idro_fluente / 1e3, "gwh_idro_bacino": e.idro_bacino / 1e3,
        "gwh_termo_mustrun": e.termo_mustrun / 1e3,
        "gwh_termo_modulante": e.termo_modulante / 1e3,
        "gwh_import": e.importato / 1e3, "gwh_export": e.esportato / 1e3,
        "gwh_bess_carica": e.bess_carica / 1e3, "gwh_bess_scarica": e.bess_scarica / 1e3,
        "gwh_curtailment": e.curtailment / 1e3, "gwh_spillamento": e.spillamento / 1e3,
        "gwh_domanda": e.domanda / 1e3, "gwh_non_servita": e.non_servita / 1e3,
    }


def prepara(serie: pd.DataFrame, domanda_twh: float | None = None,
            colonna_eolico: str = "cf_eolico_Carso_Basovizza",
            perdite_pv: float = 0.14) -> dict:
    """Estrae dalla serie oraria gli array che servono al motore."""
    carico = serie["carico_totale_mw"].to_numpy(dtype=float)
    if domanda_twh:
        attuale = carico.sum() / 1e6
        carico = carico * (domanda_twh / attuale) if attuale else carico
    cf_eo = (serie[colonna_eolico].to_numpy(dtype=float)
             if colonna_eolico in serie.columns else np.zeros(len(carico)))
    return {
        "domanda": carico,
        "cf_pv": serie["cf_fv_regionale"].to_numpy(dtype=float) * (1 - perdite_pv),
        "cf_eolico": cf_eo,
        "mesi": serie.index.month.to_numpy() if hasattr(serie.index, "month")
        else np.ones(len(carico), dtype=int),
    }


def esplora(dati: dict, base: Parco, pv: list[float], eolico: list[float],
            bess: list[float], p: Prezzi, rete: CostiRete,
            lca: str = "Politecnico di Milano (RER 2022)",
            ore_bess: float = 4.0) -> pd.DataFrame:
    """Griglia di configurazioni: una riga per combinazione."""
    righe = []
    for a, b, c in product(pv, eolico, bess):
        parco = replace(base, pv_mw=float(a), eolico_mw=float(b),
                        bess_mwh=float(c), bess_mw=float(c) / ore_bess if ore_bess else float(c))
        righe.append(valuta(dati, parco, p, rete, base, lca))
    return pd.DataFrame(righe)


def frontiera(df: pd.DataFrame, x: str = "gco2_kwh", y: str = "eur_mwh") -> pd.DataFrame:
    """Configurazioni non dominate su due assi."""
    d = df.sort_values([x, y]).reset_index(drop=True)
    tenute, minimo = [], float("inf")
    for _, r in d.iterrows():
        if r[y] < minimo:
            tenute.append(r)
            minimo = r[y]
    return pd.DataFrame(tenute)


def scegli(df: pd.DataFrame, tolleranza: float = 0.05,
           peso_import: float = 0.5) -> pd.Series:
    """La migliore fra quelle entro `tolleranza` dal costo minimo.

    Fra le configurazioni economicamente equivalenti si sceglie quella che fa
    meglio su emissioni e import insieme, con un peso regolabile: e' il modo di
    rendere esplicito il compromesso invece di nasconderlo in una formula.
    """
    soglia = df["eur_mwh"].min() * (1 + tolleranza)
    ok = df[df["eur_mwh"] <= soglia].copy()
    if ok.empty:
        ok = df.copy()

    def scala(s):
        lo, hi = s.min(), s.max()
        return (s - lo) / (hi - lo) if hi > lo else s * 0

    ok["punteggio"] = ((1 - peso_import) * scala(ok["gco2_kwh"])
                       + peso_import * scala(ok["quota_import"]))
    return ok.sort_values("punteggio").iloc[0]


def autosufficienza(dati: dict, base: Parco, p: Prezzi, rete: CostiRete,
                    modalita: str = "saldo annuo", lca: str = "Politecnico di Milano (RER 2022)",
                    pv_max: float = 9000.0, eolico_max: float = 2000.0,
                    bess_max: float = 30000.0, passi: int = 6) -> pd.DataFrame:
    """Configurazioni che azzerano l'import, in due letture diverse.

    * **saldo annuo**: si puo' importare d'inverno se si esporta altrettanto
      d'estate. E' l'autosufficienza contabile, quella di cui si parla di
      solito;
    * **ogni ora**: nessuna importazione in nessuna ora dell'anno. E' l'autarchia
      elettrica, e costa molto di piu' perche' impone di dimensionare il sistema
      sulla settimana peggiore.
    """
    righe = []
    for a, b, c in product(np.linspace(base.pv_mw, pv_max, passi),
                           np.linspace(0, eolico_max, passi),
                           np.linspace(base.bess_mwh, bess_max, passi)):
        parco = replace(base, pv_mw=float(a), eolico_mw=float(b),
                        bess_mwh=float(c), bess_mw=float(c) / 4)
        if modalita == "ogni ora":
            parco = replace(parco, import_max_mw=0.0)
        r = valuta(dati, parco, p, rete, base, lca)
        if modalita == "ogni ora":
            if r["gwh_non_servita"] <= 0.5:
                righe.append(r)
        else:
            if r["import_netto_gwh"] <= 0.0:
                righe.append(r)
    return pd.DataFrame(righe).sort_values("eur_mwh") if righe else pd.DataFrame()


def profilo(dati: dict, parco: Parco, ore: tuple[int, int] | None = None) -> pd.DataFrame:
    """Serie oraria del dispacciamento, per i grafici."""
    e = simula(dati["domanda"], dati["cf_pv"], dati["cf_eolico"], parco,
               mesi=dati.get("mesi"), serie=True)
    a, b = ore if ore else (0, len(dati["domanda"]))
    return pd.DataFrame({
        "ora": np.arange(a, b),
        "Domanda": e.serie["domanda"][a:b],
        "Fotovoltaico": e.serie["pv"][a:b],
        "Eolico": e.serie["eolico"][a:b],
        "Idro fluente": e.serie["fluente"][a:b],
        "Idro da bacino": e.serie["bacino"][a:b],
        "Termoelettrico": e.serie["termo"][a:b],
        "Import": e.serie["import"][a:b],
        "Accumulo": e.serie["accumulo"][a:b],
        "Surplus": e.serie["surplus"][a:b],
    })


# Alias esplicito: nell'app "costo" da solo sarebbe ambiguo.
costo_sistema_elettrico = costo
