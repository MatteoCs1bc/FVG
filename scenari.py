"""
Motore di scenario regionale: esplora combinazioni di parco e le confronta.

Usa il dispacciamento orario di `src.dispacciamento` su un anno di dati e
valuta ogni configurazione su tre assi: **costo del sistema**, **emissioni** e
**dipendenza dall'import**. Il terzo asse e' quello che distingue una regione
da un paese: importare non e' un fallimento, e' una scelta con un prezzo.

Rispetto al simulatore nazionale da cui deriva, qui:

* i **costi di rete** entrano nel conto, invece di essere un forfait
  proporzionale alla quota rinnovabile. Sotto l'hosting capacity si paga la
  connessione, sopra si paga anche il rinforzo;
* l'**idroelettrico a bacino** e' trattato come accumulo stagionale, che a
  scala regionale vale un ordine di grandezza piu' di qualunque batteria;
* niente nucleare, e l'eolico solo come ipotesi esplicita.

Il modulo non dipende da Streamlit.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from itertools import product

import numpy as np
import pandas as pd

from src.dispacciamento import Esito, Parco, costo_sistema, simula


@dataclass
class Prezzi:
    """Contratti per differenza e prezzi di riferimento, €/MWh."""
    cfd_pv: float = 60.0
    cfd_eolico: float = 80.0
    cfd_idro: float = 55.0
    gas: float = 130.0
    importazione: float = 115.9
    lcos: float = 90.0
    voll: float = 3000.0

    def come_dizionario(self) -> dict:
        return {"cfd_pv": self.cfd_pv, "cfd_eolico": self.cfd_eolico,
                "cfd_idro": self.cfd_idro, "gas": self.gas,
                "import": self.importazione, "lcos": self.lcos, "voll": self.voll}


@dataclass
class CostiRete:
    """Costi di connessione e rinforzo, €/kW di nuova potenza."""
    connessione_eur_kw: float = 90.0
    rinforzo_eur_kw: float = 220.0
    hosting_capacity_mw: float = 485.0
    vita_anni: int = 30
    wacc: float = 0.06

    def annualita(self) -> float:
        w = self.wacc
        return w / (1 - (1 + w) ** -self.vita_anni) if w else 1 / self.vita_anni

    def costo_annuo(self, nuova_potenza_mw: float) -> float:
        """Euro all'anno. Oltre l'hosting capacity il costo unitario sale."""
        entro = min(max(nuova_potenza_mw, 0.0), self.hosting_capacity_mw)
        oltre = max(0.0, nuova_potenza_mw - self.hosting_capacity_mw)
        capex = (entro * 1000 * self.connessione_eur_kw
                 + oltre * 1000 * (self.connessione_eur_kw + self.rinforzo_eur_kw))
        return capex * self.annualita()


def carica_serie(path) -> pd.DataFrame:
    d = pd.read_csv(path, index_col=0, parse_dates=True)
    return d


def valuta(
    domanda: np.ndarray,
    cf_pv: np.ndarray,
    cf_eolico: np.ndarray,
    parco: Parco,
    prezzi: Prezzi,
    rete: CostiRete,
    parco_base: Parco,
) -> dict:
    """Simula una configurazione e ne calcola costo, emissioni e import."""
    e: Esito = simula(domanda, cf_pv, cf_eolico, parco)
    c = costo_sistema(e, prezzi.come_dizionario())

    nuova_mw = max(0.0, (parco.pv_mw - parco_base.pv_mw)) + \
               max(0.0, (parco.eolico_mw - parco_base.eolico_mw)) + \
               max(0.0, (parco.bess_mw - parco_base.bess_mw))
    costo_rete = rete.costo_annuo(nuova_mw)
    totale = c["totale_eur"] + costo_rete

    return {
        # tutti i flussi annui in GWh: sono quelli che disegnano il Sankey
        "gwh_pv": e.pv / 1e3, "gwh_eolico": e.eolico / 1e3,
        "gwh_idro_fluente": e.idro_fluente / 1e3, "gwh_idro_bacino": e.idro_bacino / 1e3,
        "gwh_gas": e.gas / 1e3, "gwh_import": e.importato / 1e3,
        "gwh_bess_carica": e.bess_carica / 1e3, "gwh_bess_scarica": e.bess_scarica / 1e3,
        "gwh_export": e.esportato / 1e3, "gwh_curtailment": e.curtailment / 1e3,
        "gwh_spillamento": e.spillamento / 1e3, "gwh_domanda": e.domanda / 1e3,
        "gwh_non_servita": e.non_servita / 1e3,
        "pv_mw": parco.pv_mw, "eolico_mw": parco.eolico_mw,
        "bess_mw": parco.bess_mw, "bess_mwh": parco.bess_mwh,
        "nuova_potenza_mw": nuova_mw,
        "eur_mwh": totale / e.domanda if e.domanda else 0.0,
        "eur_mwh_senza_rete": c["eur_mwh"],
        "costo_rete_mln": costo_rete / 1e6,
        "gco2_kwh": e.intensita_carbonica(),
        "import_gwh": e.importato / 1e3,
        "quota_import": e.quota_import,
        "quota_fer": e.quota_rinnovabile,
        "gas_gwh": e.gas / 1e3,
        "export_gwh": e.esportato / 1e3,
        "curtailment_gwh": e.curtailment / 1e3,
        "non_servita_gwh": e.non_servita / 1e3,
        "spillamento_gwh": e.spillamento / 1e3,
    }


def scala_domanda(serie: pd.DataFrame, twh_obiettivo: float) -> np.ndarray:
    """Riscala il profilo di carico su un consumo annuo dichiarato.

    La forma oraria resta quella misurata, cambia solo il livello: e' il modo
    onesto di proiettare la domanda al 2045 senza inventarsi un profilo nuovo.
    """
    carico = serie["carico_totale_mw"].to_numpy(dtype=float)
    attuale_twh = carico.sum() / 1e6
    return carico * (twh_obiettivo / attuale_twh) if attuale_twh else carico


def cerca_autosufficienza(
    domanda: np.ndarray,
    cf_pv: np.ndarray,
    cf_eolico: np.ndarray,
    parco_base: Parco,
    quota_import_max: float,
    prezzi: Prezzi,
    rete: CostiRete,
    pv_max: float = 8000.0,
    eolico_max: float = 1500.0,
    bess_max: float = 20000.0,
    passi: int = 6,
) -> pd.DataFrame:
    """Configurazioni che rispettano un tetto all'import, ordinate per costo.

    E' il secondo passo del ragionamento: dopo aver visto quanto costa il
    sistema ottimizzato, si fissa quanto import si e' disposti ad accettare e
    si guarda cosa serve per starci dentro.
    """
    righe = []
    for pv, eo, bess in product(
        np.linspace(parco_base.pv_mw, pv_max, passi),
        np.linspace(0, eolico_max, passi),
        np.linspace(parco_base.bess_mwh, bess_max, passi),
    ):
        parco = replace(parco_base, pv_mw=pv, eolico_mw=eo,
                        bess_mwh=bess, bess_mw=bess / 4)
        r = valuta(domanda, cf_pv, cf_eolico, parco, prezzi, rete, parco_base)
        if r["quota_import"] <= quota_import_max:
            righe.append(r)
    return pd.DataFrame(righe).sort_values("eur_mwh") if righe else pd.DataFrame()


def profilo_orario(
    domanda: np.ndarray,
    cf_pv: np.ndarray,
    cf_eolico: np.ndarray,
    parco: Parco,
    giorno_inizio: int = 0,
    giorni: int = 7,
) -> pd.DataFrame:
    """Ricostruisce il dispacciamento ora per ora su una finestra di giorni."""
    e = simula(domanda, cf_pv, cf_eolico, parco, tenere_serie=True)
    a, b = giorno_inizio * 24, (giorno_inizio + giorni) * 24
    n = len(domanda)
    a, b = max(0, min(a, n - 1)), max(1, min(b, n))
    return pd.DataFrame({
        "ora": np.arange(a, b),
        "domanda": domanda[a:b],
        "fotovoltaico": e.serie["pv_mw"][a:b],
        "eolico": e.serie["eolico_mw"][a:b],
        "import": e.serie["import_mw"][a:b],
        "surplus": e.serie["surplus_mw"][a:b],
    })


def esplora(
    serie: pd.DataFrame,
    parco_base: Parco,
    pv_mw: list[float],
    eolico_mw: list[float],
    bess_mwh: list[float],
    prezzi: Prezzi | None = None,
    rete: CostiRete | None = None,
    ore_bess: float = 4.0,
    colonna_eolico: str = "cf_eolico_Carso_Basovizza",
) -> pd.DataFrame:
    """Griglia di configurazioni: una riga per combinazione."""
    prezzi = prezzi or Prezzi()
    rete = rete or CostiRete()

    domanda = serie["carico_totale_mw"].to_numpy(dtype=float)
    # Le perdite di sistema non sono nel fattore di capacita' PVGIS: 14% standard
    cf_pv = serie["cf_fv_regionale"].to_numpy(dtype=float) * 0.86
    cf_eo = (serie[colonna_eolico].to_numpy(dtype=float)
             if colonna_eolico in serie.columns else np.zeros(len(domanda)))

    righe = []
    for pv, eo, bess in product(pv_mw, eolico_mw, bess_mwh):
        parco = replace(parco_base, pv_mw=pv, eolico_mw=eo,
                        bess_mwh=bess, bess_mw=bess / ore_bess if ore_bess else bess)
        righe.append(valuta(domanda, cf_pv, cf_eo, parco, prezzi, rete, parco_base))
    return pd.DataFrame(righe)


def frontiera(df: pd.DataFrame, x: str = "gco2_kwh", y: str = "eur_mwh") -> pd.DataFrame:
    """Configurazioni non dominate: nessun'altra fa meglio su entrambi gli assi."""
    d = df.sort_values([x, y]).reset_index(drop=True)
    tenute, minimo = [], float("inf")
    for _, r in d.iterrows():
        if r[y] < minimo:
            tenute.append(r)
            minimo = r[y]
    return pd.DataFrame(tenute)


def migliore(df: pd.DataFrame, tolleranza: float = 0.05) -> pd.Series:
    """La configurazione meno emissiva fra quelle entro `tolleranza` dal minimo di costo."""
    soglia = df["eur_mwh"].min() * (1 + tolleranza)
    ammesse = df[df["eur_mwh"] <= soglia]
    if ammesse.empty:
        return df.sort_values("gco2_kwh").iloc[0]
    return ammesse.sort_values("gco2_kwh").iloc[0]
