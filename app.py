"""
FVG Energy Explorer - il sistema elettrico del Friuli-Venezia Giulia, 2000-2024.

Fonte dati: Terna, Dati Statistici (dati.terna.it). Esecuzione: `streamlit run app.py`.
"""

from __future__ import annotations

import sys
from pathlib import Path

# La cartella dell'app deve stare sul path perche' `import src` funzioni anche
# quando Streamlit Cloud avvia il file da un'altra working directory.
sys.path.insert(0, str(Path(__file__).resolve().parent))

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

if not (Path(__file__).resolve().parent / "src" / "data.py").exists():
    st.error(
        "Manca la cartella `src/` accanto a questo file.\n\n"
        "Su Streamlit Cloud significa quasi sempre che il repository contiene solo "
        "lo script: carica anche `src/` (con `__init__.py`, `config.py`, `data.py`, "
        "`etl_terna.py`, `etl_per.py`) e la cartella `data/processed/`."
    )
    st.stop()

from src.scenari import CostiRete, Parco, Prezzi, esplora, frontiera, migliore
from src import dati_documentali as DOC
from src import data as D
from src.config import (
    COLORI,
    FOSSILI,
    GWH_TO_KTEP,
    IMPIANTI_COGEN,
    POPOLAZIONE,
    REGIONE,
    RINNOVABILI,
)

st.set_page_config(page_title="FVG Energy Explorer", page_icon="⚡", layout="wide")


def grafico(fig, fonte: str, nota: str = "") -> None:
    """Disegna un grafico e ne dichiara la fonte, sempre, subito sotto."""
    st.plotly_chart(fig, width="stretch")
    st.caption(f"Fonte: {fonte}." + (f" {nota}" if nota else ""))


def tabella(df, fonte: str, **kwargs) -> None:
    st.dataframe(df, width="stretch", **kwargs)
    st.caption(f"Fonte: {fonte}.")


PLOT = dict(
    template="plotly_white",
    margin=dict(t=48, b=10, l=10, r=24),
    legend=dict(orientation="h", yanchor="bottom", y=1.04, x=0),
)


@st.cache_data(show_spinner="Carico i dati Terna...")
def get_data() -> pd.DataFrame:
    return D.carica_lungo()


df = get_data()
anni = D.anni_disponibili(df)

# ---------------------------------------------------------------- sidebar
with st.sidebar:
    st.markdown(f"### {REGIONE}")
    anno = st.select_slider("Anno di riferimento", options=anni, value=max(anni))
    st.caption(f"Serie storica {min(anni)}–{max(anni)}")
    st.divider()
    tipo_cap = st.radio("Potenza efficiente", ["Lorda", "Netta"], horizontal=True)
    st.divider()
    st.caption(
        "Dati: **Terna – Dati Statistici** (dati.terna.it), export regionali. "
        "Per aggiornare: scarica i nuovi XLSX in `data/raw/terna/` e lancia "
        "`python -m src.etl_terna`."
    )

# ---------------------------------------------------------------- serie base
prod_fonte = D.serie(df, "produzione_per_fonte_gwh")
prod_fer = D.serie(df, "produzione_per_fonte_rinnovabile_gwh")
prod_comb = D.serie(df, "produzione_lorda_per_combustibile_gwh")
prod_cat = D.serie(df, "produzione_termoelettrica_per_categoria_gwh")
pot_fonte = D.serie(df, "potenza_efficiente_per_fonte_mw")
pot_fer = D.serie(df, "potenza_efficiente_nazionale_per_fonte_rinnovabile_mw", tipo_capacita=tipo_cap)
pot_cat = D.serie(df, "potenza_efficiente_per_categoria_mw")
calore = D.serie(df, "produzione_di_calore_per_impianto_cogenerativo_gwh")
emissioni = D.serie(df, "emissione_per_combustibile_mln_di_tonnellate")
idrico = D.serie(df, "produzione_per_impianto_idrico_gwh")

# L'eolico in FVG è a zero in tutta la serie: fuori dai grafici, ma detto a parole
# nella panoramica, perché la sua assenza è essa stessa un dato.
prod_fonte, prod_fer, pot_fonte, pot_fer = (
    D.senza_zeri(x) for x in (prod_fonte, prod_fer, pot_fonte, pot_fer)
)
prod_comb, prod_cat, idrico = (D.senza_zeri(x) for x in (prod_comb, prod_cat, idrico))

# Totali annui: servono in piu' schede (quota rinnovabile, intensita' carbonica,
# grafico di Marchetti), quindi stanno qui e non dentro una singola scheda.
tot_y = prod_fonte.groupby("anno")["valore"].sum()
fer_y = prod_fer.groupby("anno")["valore"].sum()


def anno_di(s: pd.DataFrame, a: int = None) -> pd.DataFrame:
    return s[s["anno"] == (a or anno)]


# ---------------------------------------------------------------- intestazione
st.markdown(
    f"""
<div style="border-bottom:1px solid #E5E7EB;padding-bottom:10px;margin-bottom:6px">
<span style="font-size:0.95em">Sviluppato da <b>{DOC.AUTORE['nome']}</b> —
<a href="{DOC.AUTORE['sito']}" target="_blank">{DOC.AUTORE['ente']}</a></span><br>
<span style="font-size:0.85em;color:#6B7280">
🏠 <a href="{DOC.AUTORE['sito']}" target="_blank">Sito dell'ente</a> ·
📧 <a href="mailto:{DOC.AUTORE['email']}">{DOC.AUTORE['email']}</a> ·
💼 <a href="{DOC.AUTORE['linkedin']}" target="_blank">LinkedIn</a> ·
🐙 <a href="{DOC.AUTORE['github']}" target="_blank">GitHub</a>
</span>
</div>
""",
    unsafe_allow_html=True,
)

st.title("⚡ FVG Energy Explorer")
st.markdown(
    f"<p style='margin-top:-12px;color:#6B7280'>Il sistema elettrico del "
    f"{REGIONE} — produzione, capacità, emissioni. Anno selezionato: "
    f"<b>{anno}</b>.</p>",
    unsafe_allow_html=True,
)


p_tot = anno_di(prod_fonte)["valore"].sum()
p_fer = anno_di(prod_fer)["valore"].sum()
pot_tot = anno_di(pot_fonte)["valore"].sum()
em_tot = anno_di(emissioni)["valore"].sum()
cal_tot = anno_di(calore)["valore"].sum()
pop = POPOLAZIONE.get(anno)

quota_fer = p_fer / p_tot * 100 if p_tot else 0
intensita = em_tot * 1e6 / p_tot if p_tot else 0  # tCO2 / GWh = gCO2/kWh


bil_kpi = D.carica_per("bilancio_2021")




def pagina_kpi():
    """Intestazione con i numeri chiave, mostrata solo nella pagina Esplora."""
    k = st.columns(5)
    k[0].metric("Produzione lorda", f"{p_tot:,.0f} GWh".replace(",", "."),
                f"{D.variazione(prod_fonte, anno) or 0:+.1f}%" if D.variazione(prod_fonte, anno) else None)
    k[1].metric("Quota rinnovabile", f"{quota_fer:.1f}%")
    k[2].metric("Potenza efficiente", f"{pot_tot:,.0f} MW".replace(",", "."))
    k[3].metric("Emissioni CO₂ (elettrico)", f"{em_tot:.2f} Mt")
    k[4].metric("Intensità carbonica", f"{intensita:.0f} g/kWh")
    if not bil_kpi.empty:
        _v = bil_kpi.set_index("voce")["valore"]
        _imp = _v.get("Import totale", 0) - _v.get("Export totale", 0)
        _cil = _v.get("Consumo interno lordo", 1)
        _em_tot = max(DOC.EMISSIONI_TOTALI_FVG.items())[1]
        _em_anno = max(DOC.EMISSIONI_TOTALI_FVG)
        k2 = st.columns(5)
        k2[0].metric("Energia importata", f"{_imp / _cil * 100:.0f}%",
                     f"{_imp:,.0f} ktep su {_cil:,.0f}".replace(",", "."),
                     help="Quota del consumo interno lordo che arriva da fuori regione. Bilancio 2021.")
        k2[1].metric("Risorse interne", f"{_v.get('Risorse interne totale', 0):,.0f} ktep".replace(",", "."))
        k2[2].metric(f"Emissioni totali ({_em_anno})", f"{_em_tot / 1000:.1f} Mt CO₂eq",
                     f"{DOC.EMISSIONI_QUOTA_NAZIONALE}% del totale italiano",
                     help="Tutti i settori e tutti i gas serra, non solo l'elettrico. Fonte ISPRA.")
        k2[3].metric("di cui settore elettrico", f"{em_tot:.2f} Mt CO₂",
                     f"{em_tot / (_em_tot / 1000) * 100:.0f}% del totale" if _em_tot else None)
        k2[4].metric("Neutralità carbonica", DOC.TARGET_FVGREEN["anno_neutralita"],
                     DOC.TARGET_FVGREEN["riferimento"].split("(")[0].strip())
    if pop:
        st.caption(
            f"Pro capite ({pop:,.0f} abitanti): ".replace(",", ".")
            + f"**{p_tot * 1000 / pop:,.0f} kWh** prodotti · ".replace(",", ".")
            + f"**{em_tot * 1e6 / pop:.2f} t CO₂** dal settore elettrico · "
            + f"**{p_tot * GWH_TO_KTEP:,.0f} ktep** di produzione totale".replace(",", ".")
        )
    st.divider()



def _scheda_0():
    st.markdown(
        """
    Il Friuli-Venezia Giulia è una regione piccola e industriale. Poco meno di
    **1,2 milioni di abitanti** su un territorio che va dalla laguna alle Alpi Giulie,
    e una struttura produttiva che pesa molto più della sua taglia demografica:
    oltre **8.300 imprese manifatturiere**, con siderurgia, meccanica, mezzi di
    trasporto, legno-arredo e cartario a fare circa tre quarti dell'export.

    Questo si vede nei consumi. L'industria assorbe da sola circa **il 62% dell'elettricità**
    regionale, e la sola siderurgia vale più di 2 TWh l'anno — più di tutto il settore
    domestico del Friuli-Venezia Giulia messo insieme. È un profilo energetico da regione
    manifatturiera, non da regione di servizi.

    Sul lato dell'offerta il quadro è particolare. L'**idroelettrico** alpino è la
    dorsale storica, il **fotovoltaico** è cresciuto in fretta fino a superarlo per
    potenza installata, le **bioenergie** hanno un peso non banale. E poi c'è
    un'assenza: **l'eolico in FVG è sostanzialmente zero**. Non pochi impianti —
    zero produzione in tutta la serie storica. È il motivo per cui non lo trovi nei
    grafici di questa app: non c'è una barra da disegnare. Per una regione che deve
    aggiungere quasi 2 GW di rinnovabili entro il 2030, significa che il peso ricade
    quasi interamente su solare e su quel poco di margine che resta all'idroelettrico.

    Infine il dato che tiene insieme tutto: il FVG **importa circa il 91%** della
    sua energia primaria, e consuma più elettricità di quanta ne produca.
        """
    )
    st.divider()

    c1, c2 = st.columns([1, 1.4])

    with c1:
        st.subheader(f"Mix di produzione {anno}")
        m = anno_di(prod_fonte)
        m = m[m["valore"] > 0]
        if not m.empty:
            fig = px.pie(m, values="valore", names="voce", hole=0.55,
                         color="voce", color_discrete_map=D.mappa_colori(m["voce"]))
            fig.update_traces(textinfo="percent+label", textposition="outside")
            fig.update_layout(showlegend=False, height=380, **PLOT)
            grafico(fig, DOC.F_TERNA)

    with c2:
        st.subheader("Produzione lorda per fonte")
        fig = px.area(prod_fonte.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_fonte["voce"]))
        fig.update_layout(height=380, yaxis_title="GWh", xaxis_title=None, **PLOT)
        fig.add_vline(x=anno, line_dash="dot", line_color="#111827")
        grafico(fig, DOC.F_TERNA)

    st.subheader("Quota rinnovabile sulla produzione lorda")
    quota = (fer_y / tot_y * 100).dropna().reset_index(name="quota")
    fig = px.line(quota, x="anno", y="quota", markers=True,
                  color_discrete_sequence=["#22C55E"])
    fig.update_layout(height=300, yaxis_title="% FER", xaxis_title=None,
                      yaxis_range=[0, 100], **PLOT)
    fig.add_hline(y=quota["quota"].mean(), line_dash="dot", line_color="#9CA3AF",
                  annotation_text=f"media {quota['quota'].mean():.0f}%",
                  annotation_position="bottom right")
    grafico(fig, DOC.F_TERNA)

    bil = D.carica_per("bilancio_2021")
    consumi_f = D.carica_per("consumi_finali_2021")

    if not bil.empty:
        v = bil.set_index("voce")["valore"]
        cil = v.get("Consumo interno lordo", 0)
        trasf_in = v.get("Input alla trasformazione", 0)
        trasf_out = v.get("Output della trasformazione", 0)
        perdite_t = v.get("Perdite di trasformazione", 0)
        autocons = v.get("Autoconsumi e perdite di rete", 0)
        cfe = consumi_f["valore"].sum()
        cfne = v.get("Consumi finali non energetici", 0)
        rendimento = v.get("Rendimento", 0)

        st.subheader("Bilancio energetico regionale 2021")
        st.caption(
            "Tutto il sistema energetico, non solo l'elettrico. Valori in ktep, "
            "dal Piano Energetico Regionale."
        )
        b = st.columns(5)
        b[0].metric("Consumo interno lordo", f"{cil:,.0f} ktep".replace(",", "."))
        b[1].metric("Import netto", f"{v.get('Import totale', 0) - v.get('Export totale', 0):,.0f} ktep".replace(",", "."))
        b[2].metric("Risorse interne", f"{v.get('Risorse interne totale', 0):,.0f} ktep".replace(",", "."))
        b[3].metric("Consumi finali", f"{cfe:,.0f} ktep".replace(",", "."))
        b[4].metric("Perdite di trasformazione", f"{perdite_t:,.0f} ktep".replace(",", "."))

        dip = (v.get("Import totale", 0) - v.get("Export totale", 0)) / cil * 100 if cil else 0
        st.caption(
            f"Dipendenza dall'estero e dalle altre regioni: **{dip:.0f}%** del consumo interno lordo. "
            f"Rendimento del sistema di trasformazione: **{rendimento * 100:.0f}%**."
        )

        # ---- Sankey del bilancio
        fonti = bil[bil["blocco"].isin(["Import", "Risorse interne"])]
        fonti = fonti[fonti["valore"] > 0]

        nodi_b = (
            [f"{r.voce} (import)" if r.blocco == "Import" else r.voce
             for r in fonti.itertuples()]
            + ["Consumo interno lordo", "Trasformazione", "Uso diretto",
               "Perdite di trasformazione", "Vettori derivati",
               "Autoconsumi e perdite di rete", "Consumi finali energetici",
               "Usi non energetici"]
        )
        ib = {n: i for i, n in enumerate(nodi_b)}
        colori_b = [
            "#EF4444" if r.blocco == "Import" else "#22C55E" for r in fonti.itertuples()
        ] + ["#111827", "#4B5563", "#9CA3AF", "#EF4444", "#FACC15", "#F97316", "#2563EB", "#A855F7"]

        sb, tb, vb, cb = [], [], [], []

        def lb(a, b_, val, colore):
            if val and val > 0:
                sb.append(ib[a]); tb.append(ib[b_]); vb.append(float(val)); cb.append(colore)

        for r in fonti.itertuples():
            nome = f"{r.voce} (import)" if r.blocco == "Import" else r.voce
            lb(nome, "Consumo interno lordo", r.valore,
               "rgba(239,68,68,0.28)" if r.blocco == "Import" else "rgba(34,197,94,0.35)")

        uso_diretto = max(0.0, cil - trasf_in)
        lb("Consumo interno lordo", "Trasformazione", trasf_in, "rgba(75,85,99,0.3)")
        lb("Consumo interno lordo", "Uso diretto", uso_diretto, "rgba(156,163,175,0.3)")
        lb("Trasformazione", "Perdite di trasformazione", perdite_t, "rgba(239,68,68,0.3)")
        lb("Trasformazione", "Vettori derivati", trasf_out, "rgba(250,204,21,0.45)")
        lb("Vettori derivati", "Autoconsumi e perdite di rete", autocons, "rgba(249,115,22,0.4)")
        lb("Vettori derivati", "Consumi finali energetici", max(0.0, trasf_out - autocons),
           "rgba(250,204,21,0.45)")
        lb("Uso diretto", "Consumi finali energetici", max(0.0, uso_diretto - cfne),
           "rgba(37,99,235,0.3)")
        lb("Uso diretto", "Usi non energetici", cfne, "rgba(168,85,247,0.4)")

        fig = go.Figure(go.Sankey(
            node=dict(pad=15, thickness=18, label=nodi_b, color=colori_b,
                      line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
            link=dict(source=sb, target=tb, value=vb, color=cb,
                      hovertemplate="%{value:.0f} ktep<extra></extra>"),
        ))
        fig.update_layout(height=600, font_size=12, margin=dict(t=20, b=20, l=10, r=10))
        grafico(fig, DOC.F_TERNA)

        st.caption(
            "In rosso ciò che entra da fuori regione, in verde le risorse interne. "
            "Il bilancio chiude con uno scarto di pochi ktep dovuto ai bunkeraggi "
            "dell'aviazione internazionale."
        )
        st.divider()

    st.subheader(f"Dal combustibile agli usi finali — {anno}")
    rend = st.slider(
        "Rendimento complessivo stimato del parco termoelettrico (elettrico + termico)",
        0.30, 0.85, 0.52, 0.01,
        help="Terna pubblica la produzione, non l'energia entrante. Questo parametro "
             "stima l'input di combustibile e quindi le perdite di conversione.",
    )

    comb_y = anno_di(prod_comb).set_index("voce")["valore"].to_dict()
    cat_y = anno_di(prod_cat).set_index("voce")["valore"].to_dict()
    fonte_y = anno_di(prod_fonte).set_index("voce")["valore"].to_dict()

    el_termo = sum(comb_y.values())
    cal_y = anno_di(calore)["valore"].sum()
    input_comb = (el_termo + cal_y) / rend if rend else 0
    perdite = max(0.0, input_comb - el_termo - cal_y)

    combustibili = [c for c, v in comb_y.items() if v > 0]
    fer_dirette = [f for f in ("Idrico", "Fotovoltaico", "Eolico") if fonte_y.get(f, 0) > 0]
    categorie = [c for c, v in cat_y.items() if v > 0]

    nodi = combustibili + ["Parco termoelettrico"] + categorie + fer_dirette + [
        "Energia elettrica", "Calore utile", "Perdite di conversione"
    ]
    idx = {n: i for i, n in enumerate(nodi)}
    colori_nodi = [COLORI.get(n, "#9CA3AF") for n in nodi]
    for n, c in {"Parco termoelettrico": "#4B5563", "Energia elettrica": "#FACC15",
                 "Calore utile": "#F97316", "Perdite di conversione": "#EF4444"}.items():
        colori_nodi[idx[n]] = c

    src, tgt, val, col = [], [], [], []

    def link(a: str, b: str, v: float, colore: str) -> None:
        if v and v > 0:
            src.append(idx[a]); tgt.append(idx[b]); val.append(float(v)); col.append(colore)

    # combustibile -> parco termoelettrico (scalato all'input stimato)
    scala = input_comb / el_termo if el_termo else 0
    for c in combustibili:
        link(c, "Parco termoelettrico", comb_y[c] * scala, "rgba(75,85,99,0.35)")

    # Parco -> categorie di impianto. L'input si ripartisce in proporzione
    # all'energia utile che ciascuna categoria produce (elettricita' piu' calore),
    # e le perdite si formano dentro la categoria, non prima: e' li' che avviene
    # la conversione. Cosi' ogni nodo chiude e spostare il rendimento fa vedere
    # subito le perdite crescere o calare.
    utile = {}
    for c in categorie:
        cogen = "Cogenerative" in c and "Non" not in c
        utile[c] = cat_y[c] + (cal_y if cogen else 0.0)
    tot_utile = sum(utile.values())

    for c in categorie:
        quota_c = utile[c] / tot_utile if tot_utile else 0
        input_c = input_comb * quota_c
        link("Parco termoelettrico", c, input_c, "rgba(75,85,99,0.35)")

        link(c, "Energia elettrica", cat_y[c], "rgba(250,204,21,0.45)")
        if "Cogenerative" in c and "Non" not in c:
            link(c, "Calore utile", cal_y, "rgba(249,115,22,0.45)")
        link(c, "Perdite di conversione", max(0.0, input_c - utile[c]),
             "rgba(239,68,68,0.3)")

    # rinnovabili non termiche -> elettricità
    for f in fer_dirette:
        link(f, "Energia elettrica", fonte_y[f], "rgba(37,99,235,0.35)")

    fig = go.Figure(go.Sankey(
        node=dict(pad=18, thickness=20, label=nodi, color=colori_nodi,
                  line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
        link=dict(source=src, target=tgt, value=val, color=col,
                  hovertemplate="%{value:.0f} GWh<extra></extra>"),
    ))
    fig.update_layout(height=520, font_size=13, margin=dict(t=20, b=20, l=10, r=10))
    grafico(fig, DOC.F_TERNA)

    st.info(
        f"Input di combustibile stimato: **{input_comb:,.0f} GWh** · "
        f"elettricità termoelettrica **{el_termo:,.0f} GWh** · "
        f"calore utile **{cal_y:,.0f} GWh** · "
        f"perdite **{perdite:,.0f} GWh**. "
        "L'input non è misurato da Terna: dipende dal rendimento impostato sopra."
        .replace(",", ".")
    )

    consumi_f = D.carica_per("consumi_finali_2021")
    if consumi_f.empty:
        st.info("Lancia `python -m src.etl_per` per generare i dati del Piano Energetico Regionale.")
    else:
        tot_cf = consumi_f["valore"].sum()
        st.subheader("Consumi finali energetici 2021, per settore e vettore")
        st.caption(f"{tot_cf:,.0f} ktep complessivi. Fonte: Piano Energetico Regionale.".replace(",", "."))

        per_settore = consumi_f.groupby("settore")["valore"].sum().sort_values(ascending=False)
        per_vettore = consumi_f.groupby("vettore")["valore"].sum().sort_values(ascending=False)

        c1, c2 = st.columns(2)
        with c1:
            fig = px.pie(per_settore.reset_index(), values="valore", names="settore", hole=0.55,
                         color_discrete_sequence=["#2563EB", "#F97316", "#22C55E", "#A855F7"])
            fig.update_traces(textinfo="percent+label", textposition="outside")
            fig.update_layout(showlegend=False, height=380, title="Per settore", **PLOT)
            grafico(fig, DOC.F_TERNA)
        with c2:
            fig = px.pie(per_vettore.reset_index(), values="valore", names="vettore", hole=0.55,
                         color="vettore", color_discrete_map={
                             "Combustibili gassosi": "#9CA3AF", "Energia elettrica": "#FACC15",
                             "Petrolio": "#4B5563", "Energie rinnovabili": "#22C55E",
                             "Calore derivato": "#F97316", "Combustibili solidi": "#111827",
                             "Rifiuti non rinnovabili": "#D1D5DB"})
            fig.update_traces(textinfo="percent+label", textposition="outside")
            fig.update_layout(showlegend=False, height=380, title="Per vettore", **PLOT)
            grafico(fig, DOC.F_TERNA)

        st.subheader("Chi consuma cosa")
        nodi_c = list(per_vettore.index) + list(per_settore.index)
        ic = {n: i for i, n in enumerate(nodi_c)}
        colori_c = ["#9CA3AF"] * len(per_vettore) + ["#2563EB"] * len(per_settore)
        for n, col in {"Energia elettrica": "#FACC15", "Energie rinnovabili": "#22C55E",
                       "Petrolio": "#4B5563", "Combustibili solidi": "#111827",
                       "Calore derivato": "#F97316"}.items():
            if n in ic:
                colori_c[ic[n]] = col

        att = consumi_f[consumi_f["valore"] > 0]
        fig = go.Figure(go.Sankey(
            node=dict(pad=18, thickness=20, label=nodi_c, color=colori_c,
                      line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
            link=dict(source=[ic[r.vettore] for r in att.itertuples()],
                      target=[ic[r.settore] for r in att.itertuples()],
                      value=list(att["valore"]),
                      color=["rgba(37,99,235,0.25)"] * len(att),
                      hovertemplate="%{value:.0f} ktep<extra></extra>"),
        ))
        fig.update_layout(height=460, font_size=13, margin=dict(t=20, b=20, l=10, r=10))
        grafico(fig, DOC.F_TERNA)

        st.subheader("Composizione di ogni settore")
        fig = px.bar(consumi_f[consumi_f["valore"] > 0], x="settore", y="valore", color="vettore",
                     color_discrete_map={
                         "Combustibili gassosi": "#9CA3AF", "Energia elettrica": "#FACC15",
                         "Petrolio": "#4B5563", "Energie rinnovabili": "#22C55E",
                         "Calore derivato": "#F97316", "Combustibili solidi": "#111827"})
        fig.update_layout(height=400, yaxis_title="ktep", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

        el_share = per_vettore.get("Energia elettrica", 0) / tot_cf * 100
        st.info(
            f"L'elettricità copre il **{el_share:.0f}%** dei consumi finali. "
            "Industria e civile pesano quasi uguale (~40% ciascuno), ma con vettori diversi: "
            "l'industria va a elettricità e gas, il civile quasi solo a gas. "
            "I trasporti restano il settore meno elettrificato: petrolio all'86%."
        )


def _scheda_1():
    c1, c2 = st.columns(2)

    with c1:
        st.subheader(f"Produzione per fonte, {anno}")
        m = anno_di(prod_fonte).sort_values("valore", ascending=True)
        fig = px.bar(m, x="valore", y="voce", orientation="h", color="voce",
                     color_discrete_map=D.mappa_colori(m["voce"]), text_auto=".0f")
        fig.update_layout(showlegend=False, height=340, xaxis_title="GWh",
                          yaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    with c2:
        st.subheader(f"Potenza efficiente {tipo_cap.lower()}, {anno}")
        m = anno_di(pot_fonte).sort_values("valore", ascending=True)
        fig = px.bar(m, x="valore", y="voce", orientation="h", color="voce",
                     color_discrete_map=D.mappa_colori(m["voce"]), text_auto=".0f")
        fig.update_layout(showlegend=False, height=340, xaxis_title="MW",
                          yaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    st.subheader("Potenza installata nel tempo")
    fig = px.area(pot_fonte.sort_values("anno"), x="anno", y="valore", color="voce",
                  color_discrete_map=D.mappa_colori(pot_fonte["voce"]))
    fig.update_layout(height=340, yaxis_title="MW", xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_TERNA)

    st.subheader("Ore equivalenti di utilizzo")
    st.caption("Produzione annua / potenza efficiente. Indica quanto intensamente lavora ogni parco.")
    merge = prod_fonte.merge(pot_fonte, on=["anno", "voce"], suffixes=("_gwh", "_mw"))
    merge = merge[merge["valore_mw"] > 1]
    merge["ore"] = merge["valore_gwh"] * 1000 / merge["valore_mw"]
    fig = px.line(merge.sort_values("anno"), x="anno", y="ore", color="voce", markers=True,
                  color_discrete_map=D.mappa_colori(merge["voce"]))
    fig.update_layout(height=340, yaxis_title="ore/anno", xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_TERNA)



    # ------------------------------------------------- il profilo della domanda
    st.divider()
    st.subheader("Quando consumano le famiglie friulane")
    pre = D.carica_per("prelievi_orari_fvg")
    fas = D.carica_per("prelievi_fasce_fvg")

    if not pre.empty:
        st.caption(
            "Prelievo medio orario dei clienti domestici, misurato. È l'unico profilo "
            "orario reale disponibile per la regione, e riguarda il solo settore "
            f"domestico (circa il 15% dei consumi elettrici). Fonte: {DOC.FONTE_ARERA}."
        )

        prof = (pre.groupby(["tipo_giorno", "ora_n"])["kwh"].mean().reset_index())
        prof["tipo_giorno"] = prof["tipo_giorno"].str.replace("_", " ").str.capitalize()
        fig = px.line(prof, x="ora_n", y="kwh", color="tipo_giorno", markers=True,
                      color_discrete_map={"Giorno feriale": "#2563EB",
                                          "Giorno festivo": "#F97316"})
        fig.add_vrect(x0=10, x1=16, fillcolor="#FACC15", opacity=0.18, line_width=0,
                      annotation_text="ore di sole", annotation_position="top left")
        fig.update_layout(height=380, xaxis_title="ora del giorno",
                          yaxis_title="kWh medi per cliente", **PLOT)
        grafico(fig, DOC.FONTE_ARERA)

        picco = prof.loc[prof["kwh"].idxmax()]
        solare = prof[(prof["ora_n"] >= 10) & (prof["ora_n"] <= 16)]["kwh"].mean()
        st.info(
            f"**Il picco domestico è alle {int(picco['ora_n'])}**, quando il fotovoltaico "
            f"ha ormai finito. Nelle ore centrali, quando il sole produce, il consumo medio "
            f"è di {solare:.3f} kWh contro i {picco['kwh']:.3f} della punta serale: "
            f"**{(1 - solare / picco['kwh']) * 100:.0f}% in meno**. "
            + (f"Il {fas['f3'].mean() * 100:.0f}% dell'energia domestica viene prelevato in "
               "fascia F3, cioè di sera, di notte e nei festivi. " if not fas.empty else "")
            + "È la ragione per cui l'autoconsumo fotovoltaico senza accumulo si ferma "
            "intorno al 30%, e perché batterie e comunità energetiche non sono un "
            "accessorio ma la condizione perché il solare residenziale serva a qualcosa."
        )

        st.markdown("**Come cambia nell'arco dell'anno**")
        mens = pre.groupby(["mese_n", "ora_n"])["kwh"].mean().reset_index()
        fig = px.density_heatmap(mens, x="ora_n", y="mese_n", z="kwh",
                                 color_continuous_scale="YlOrRd", nbinsx=24, nbinsy=12)
        fig.update_layout(height=360, xaxis_title="ora del giorno", yaxis_title="mese",
                          coloraxis_colorbar=dict(title="kWh"), template="plotly_white",
                          margin=dict(t=48, b=10, l=10, r=24))
        fig.update_yaxes(autorange="reversed", tickmode="array", tickvals=list(range(1, 13)),
                         ticktext=["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago",
                                   "set", "ott", "nov", "dic"])
        grafico(fig, DOC.FONTE_ARERA,
                "Più scuro significa più consumo. Si vedono la punta serale invernale "
                "e la coda estiva del condizionamento.")

        classi = (pre.groupby("classe")["kwh"].mean().reset_index()
                  .sort_values("kwh"))
        fig = px.bar(classi, x="kwh", y="classe", orientation="h", text_auto=".3f",
                     color_discrete_sequence=["#2563EB"])
        fig.update_traces(cliponaxis=False)
        fig.update_layout(height=300, yaxis_title=None,
                          xaxis_title="kWh medi orari per cliente", **PLOT)
        grafico(fig, DOC.FONTE_ARERA,
                "Classe di potenza impegnata: chi ha più potenza consuma di più, ed è "
                "il cliente per cui una pompa di calore o un'auto elettrica cambiano il profilo.")


def _scheda_2():
    st.subheader("La rete di distribuzione")
    st.caption(f"Fonte: {DOC.FONTE_EDIST}.")

    r = st.columns(4)
    r[0].metric("Potenza installata", f"{DOC.RETE_POTENZA['Potenza installata totale']:.1f} GW")
    r[1].metric("di cui rinnovabile", f"{DOC.RETE_POTENZA['Potenza installata da fonti rinnovabili']:.1f} GW")
    r[2].metric("Hosting capacity 2025", f"{DOC.HOSTING_CAPACITY_MW} MW", help="Senza le richieste già in pipeline.")
    r[3].metric("Connessi 2022–2025", f"{DOC.RETE_CONNESSIONI['potenza_connessa_mw_2022_2025']} MW",
                f"{DOC.RETE_CONNESSIONI['richieste_2022_2025']:,} richieste".replace(",", "."))

    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("**Consistenza dell'infrastruttura**")
        cons = pd.DataFrame(
            [{"Voce": k, "Valore": f"{v:,.0f} {u}".replace(",", ".").strip()}
             for k, (v, u) in DOC.RETE_CONSISTENZA.items()]
        )
        st.dataframe(cons, hide_index=True, width="stretch")

        fer_d = pd.DataFrame(DOC.RETE_FER_DETTAGLIO.items(), columns=["Fonte", "GW"])
        fig = px.bar(fer_d, x="GW", y="Fonte", orientation="h", text_auto=".2f",
                     color="Fonte", color_discrete_map={"Solare": "#FACC15", "Idraulica": "#2563EB",
                                                        "Termica": "#4B5563"})
        fig.update_layout(showlegend=False, height=220, title="Rinnovabili connesse (GW)",
                          yaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    with c2:
        st.markdown("**Saturazione dei trasformatori AT/MT**")
        st.caption("Effetto delle richieste in pipeline, dicembre 2025. 75 trasformatori in tutto.")
        tr = pd.DataFrame(DOC.TRASFORMATORI_STATO.items(), columns=["Stato", "Numero"])
        fig = px.pie(tr, values="Numero", names="Stato", hole=0.5, color="Stato",
                     color_discrete_map={"Verde (sotto soglia)": "#22C55E",
                                         "Giallo (sotto 65%)": "#FACC15",
                                         "Arancione (oltre 65%)": "#F97316",
                                         "Rosso (oltre 90%)": "#EF4444"})
        fig.update_traces(textinfo="value+percent")
        fig.update_layout(height=330, **PLOT)
        grafico(fig, DOC.F_AUDIZIONI)

    st.subheader("Dove la rete è già satura")
    st.caption(
        "Un'area è **rossa** quando la potenza in immissione richiesta supera il 90% "
        "della potenza nominale dei trasformatori che la alimentano: lì connettere "
        "nuovi impianti diventa difficile senza potenziare la rete."
    )
    c3, c4 = st.columns(2)
    with c3:
        ac = pd.DataFrame(DOC.AREE_CRITICHE_COMUNI.items(), columns=["Criticità", "Comuni"])
        fig = px.bar(ac, x="Criticità", y="Comuni", color="Criticità", text_auto=True,
                     color_discrete_map={"Rosso": "#EF4444", "Arancio": "#F97316",
                                         "Giallo": "#FACC15", "Bianco": "#D1D5DB"})
        fig.update_layout(showlegend=False, height=320, xaxis_title=None,
                          title="Comuni per livello di criticità", **PLOT)
        grafico(fig, DOC.F_AUDIZIONI)
    with c4:
        pr = pd.DataFrame(DOC.TRASFORMATORI_PROVINCIA.items(), columns=["Provincia", "Trasformatori"])
        fig = px.bar(pr, x="Provincia", y="Trasformatori", text_auto=True,
                     color_discrete_sequence=["#6B7280"])
        fig.update_layout(height=320, xaxis_title=None,
                          title="Trasformatori AT/MT per provincia", **PLOT)
        grafico(fig, DOC.F_AUDIZIONI)

    st.subheader("Il potenziamento in programma")
    sv = pd.DataFrame([
        {"Provincia": p, "Tipo": "Ampliamenti", "Impianti": d["ampliamenti"], "MVA": d["mva_ampliamenti"]}
        for p, d in DOC.RETE_SVILUPPO.items()
    ] + [
        {"Provincia": p, "Tipo": "Nuovi impianti", "Impianti": d["nuovi"], "MVA": d["mva_nuovi"]}
        for p, d in DOC.RETE_SVILUPPO.items()
    ])
    fig = px.bar(sv, x="Provincia", y="MVA", color="Tipo", text="Impianti", barmode="group",
                 color_discrete_map={"Ampliamenti": "#2563EB", "Nuovi impianti": "#22C55E"})
    fig.update_traces(textposition="outside", cliponaxis=False)
    fig.update_layout(height=380, xaxis_title=None, yaxis_title="MVA di incremento",
                      yaxis_range=[0, sv["MVA"].max() * 1.18], **PLOT)
    grafico(fig, DOC.F_AUDIZIONI)
    st.caption(
        f"In totale {sv['Impianti'].sum()} interventi per {sv['MVA'].sum():,.0f} MVA. "
        "L'etichetta sopra ogni barra è il numero di impianti.".replace(",", ".")
    )

    st.divider()
    st.subheader("Il target regionale al 2030")
    st.caption(f"Fonte: {DOC.FONTE_TERNA_RETE}. Valori in GW di capacità rinnovabile.")
    bs = pd.DataFrame(DOC.BURDEN_SHARING.items(), columns=["Voce", "GW"])
    target = bs.iloc[0]["GW"]
    fig = px.bar(bs.iloc[1:], x="Voce", y="GW", text_auto=".2f",
                 color="Voce", color_discrete_sequence=["#22C55E", "#2563EB", "#60A5FA", "#D1D5DB"])
    fig.add_hline(y=target, line_dash="dash", line_color="#111827",
                  annotation_text=f"Target 2030: {target} GW",
                  annotation_position="top left")
    fig.update_layout(showlegend=False, height=360, xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_AUDIZIONI)
    st.info(
        f"Il Decreto Aree Idonee assegna al FVG **+{target} GW** di nuova capacità rinnovabile "
        f"al 2030 rispetto al 2021. Ne risultano in esercizio o autorizzati "
        f"**{DOC.BURDEN_SHARING['In esercizio o autorizzato dal 2021']} GW**: l'82% del percorso. "
        "Il collo di bottiglia non è più autorizzare impianti, è avere rete che li accolga."
    )

    st.divider()
    st.subheader("Avanzamento verso il target 2030, in dettaglio")
    st.caption(f"Fonte: {DOC.FONTE_RETI_REPORT}.")

    bsm = pd.DataFrame(DOC.BURDEN_SHARING_MW.items(), columns=["Voce", "MW"])
    bsm["Quota"] = bsm["MW"] / DOC.BURDEN_SHARING_TARGET_MW * 100
    fig = px.bar(bsm, x="MW", y=["Target"] * len(bsm), color="Voce", orientation="h",
                 text=bsm.apply(lambda r: f"{r['Voce']}<br>{r['MW']} MW", axis=1),
                 color_discrete_sequence=["#22C55E", "#2563EB", "#60A5FA", "#E5E7EB"])
    fig.update_traces(textposition="inside", insidetextanchor="middle")
    fig.update_layout(height=260, barmode="stack", showlegend=False, yaxis_title=None,
                      xaxis_title=f"MW sul target di {DOC.BURDEN_SHARING_TARGET_MW} MW", **PLOT)
    grafico(fig, DOC.F_AUDIZIONI)
    st.caption(
        f"Gli impianti già in esercizio coprono il {bsm.iloc[0]['Quota']:.0f}% del target. "
        "Sommando la pipeline autorizzata si arriva a poco più dell'80%: "
        f"mancano {DOC.BURDEN_SHARING_MW['Quota residua al 2030']} MW."
    )

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Accumuli: richieste contro fabbisogno**")
        b = DOC.BESS
        bess = pd.DataFrame([
            {"Voce": "Richiesto", "MW": b["Potenza richiesta (MW)"]},
            {"Voce": "Fabbisogno stimato", "MW": b["Fabbisogno stimato dal piano (MW)"]},
            {"Voce": "Già attivo (Pavia di Udine)", "MW": b["Impianto già attivo a Pavia di Udine (MW)"]},
        ])
        fig = px.bar(bess, x="Voce", y="MW", text_auto=".0f",
                     color="Voce", color_discrete_sequence=["#A855F7", "#22C55E", "#2563EB"])
        fig.update_layout(showlegend=False, height=320, xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_AUDIZIONI)
        st.caption(
            f"{b['Impianti autorizzati o in istruttoria']} impianti tra autorizzati e in "
            "istruttoria. Le richieste valgono quasi cinque volte il fabbisogno stimato dal "
            "piano: è il segnale di una corsa a prenotare capacità più che di un bisogno reale."
        )

    with c2:
        st.markdown("**Interconnessioni transfrontaliere**")
        inter = pd.DataFrame([
            {"Linea": k.split(",")[0], "Attuale": v["attuale"], "Prevista": v["prevista"]}
            for k, v in DOC.INTERCONNESSIONI.items()
        ])
        fig = go.Figure()
        fig.add_bar(x=inter["Linea"], y=inter["Attuale"], name="Capacità attuale",
                    marker_color="#6B7280", text=inter["Attuale"])
        fig.add_bar(x=inter["Linea"], y=inter["Prevista"] - inter["Attuale"],
                    name="Incremento previsto", marker_color="#22C55E")
        fig.update_layout(barmode="stack", height=320, yaxis_title="MW", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_AUDIZIONI)
        st.caption(
            "Il FVG è un ponte elettrico verso Slovenia e Austria. La capacità di importazione "
            "da Redipuglia sale da 700 a 1.200 MW con la razionalizzazione della "
            "Redipuglia–Udine Ovest."
        )

    st.subheader("Chi distribuisce l'energia")
    st.caption(
        "La distribuzione non è di un solo operatore: accanto a e-distribuzione ci sono "
        "le utility urbane e le cooperative storiche alpine, con problemi opposti."
    )
    for nome, d in DOC.DISTRIBUTORI.items():
        riga = f"**{nome}** — {d['clienti']:,} utenze".replace(",", ".")
        if d["energia_gwh"]:
            riga += f", {d['energia_gwh']} GWh/anno"
        st.markdown(riga + f". {d['nota']}.")

    st.subheader("Il nodo della saturazione virtuale")
    sat = pd.DataFrame(DOC.SATURAZIONE_PROVINCE.items(),
                       columns=["Provincia", "% trasformatori in zona rossa"])
    fig = px.bar(sat, x="Provincia", y="% trasformatori in zona rossa", text_auto=".0f",
                 color_discrete_sequence=["#EF4444"])
    fig.update_layout(height=280, xaxis_title=None, yaxis_range=[0, 60], **PLOT)
    grafico(fig, DOC.F_TERNA)
    st.markdown(
        f"Una parte della saturazione è **virtuale**: capacità prenotata da richieste che non "
        f"diventeranno mai impianti. Storicamente solo il **{DOC.TASSO_REALIZZAZIONE}%** "
        "di quanto viene autorizzato si costruisce davvero. "
        f"Il **{DOC.DECRETO_BOLLETTE['riferimento']}** interviene proprio su questo:"
    )
    for titolo, testo in DOC.DECRETO_BOLLETTE["misure"]:
        st.markdown(f"- **{titolo}** — {testo}")

    st.divider()
    st.subheader("Le aree di influenza delle cabine primarie")

    aree = D.carica_per("aree_cabine_primarie")
    geo_cp = D.carica_geojson("aree_cabine_primarie")

    if aree.empty or geo_cp is None:
        st.info("Lancia `python -m src.etl_cabine` per generare la mappa delle cabine primarie.")
    else:
        st.caption(
            "Ogni poligono è il territorio sotteso a una cabina primaria. È la base "
            "geografica su cui si definisce l'appartenenza a una comunità energetica: "
            "produttori e consumatori devono stare sotto la stessa cabina."
        )

        a = st.columns(4)
        a[0].metric("Aree convenzionali", len(aree))
        a[1].metric("Superficie coperta", f"{aree['area_km2'].sum():,.0f} km²".replace(",", "."))
        a[2].metric("Gestori", aree["gestore"].nunique())
        a[3].metric("Area mediana", f"{aree['area_km2'].median():,.0f} km²".replace(",", "."))

        colori_gestore = {"e-distribuzione": "#2563EB", "AcegasApsAmga": "#F97316",
                          "SECAB": "#22C55E"}
        fig = px.choropleth_map(
            aree, geojson=geo_cp, locations="codice", color="gestore",
            color_discrete_map=colori_gestore,
            hover_name="codice",
            hover_data={"gestore": True, "area_km2": ":.0f", "codice": False},
            map_style="carto-positron", zoom=7.2,
            center={"lat": 46.11, "lon": 13.10}, opacity=0.55,
        )
        fig.update_layout(height=560, margin=dict(t=10, b=10, l=0, r=0),
                          legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0,
                                      title=None))
        grafico(fig, DOC.F_REGIONE)

        c1, c2 = st.columns([1, 1])
        with c1:
            per_gest = (aree.groupby("gestore")
                        .agg(aree_n=("codice", "count"), km2=("area_km2", "sum"))
                        .reset_index().sort_values("km2"))
            fig = px.bar(per_gest, x="km2", y="gestore", orientation="h", text="aree_n",
                         color="gestore", color_discrete_map=colori_gestore)
            fig.update_traces(textposition="outside", texttemplate="%{text} aree", cliponaxis=False)
            fig.update_layout(showlegend=False, height=280, xaxis_title="km²",
                              yaxis_title=None, title="Territorio per gestore", **PLOT)
            grafico(fig, DOC.F_TERNA)

        with c2:
            fig = px.histogram(aree, x="area_km2", nbins=25,
                               color_discrete_sequence=["#6B7280"])
            fig.update_layout(height=280, xaxis_title="km² per area", yaxis_title="aree",
                              title="Quanto sono grandi le aree", **PLOT)
            grafico(fig, DOC.F_TERNA)

        fuori = int(aree["fuori_regione"].sum())
        piu_grande = aree.loc[aree["area_km2"].idxmax()]
        st.info(
            f"Le aree sono **{len(aree)}** e coprono {aree['area_km2'].sum():,.0f} km². ".replace(",", ".")
            + f"Le dimensioni sono molto diseguali: la più estesa ({piu_grande['codice']}, "
            f"{piu_grande['area_km2']:,.0f} km²) vale quanto decine di aree urbane. ".replace(",", ".")
            + f"**{fuori}** sono a cavallo del confine regionale, cioè fanno capo a cabine "
            "che servono anche territorio fuori dal FVG. "
            "Questa geografia conta per le comunità energetiche: nelle aree montane, grandi e "
            "poco popolate, trovare produttori e consumatori sotto la stessa cabina è molto "
            "più difficile che in città."
        )

        with st.expander("Elenco delle aree"):
            st.dataframe(
                aree.rename(columns={"codice": "Codice", "gestore": "Gestore",
                                     "area_km2": "km²", "fuori_regione": "A cavallo del confine"})
                .sort_values("km²", ascending=False),
                hide_index=True, width="stretch", height=300,
            )

        st.caption(
            "Fonte: dataset regionale AREECONVENZIONALI_CP (aree di influenza delle cabine "
            "primarie di distribuzione). Geometrie semplificate a ~150 m per il web."
        )

    st.divider()
    inv = D.carica_per("inversioni_flusso")
    if not inv.empty:
        st.subheader("Quando la rete lavora al contrario")
        st.caption(
            "Elenco e-distribuzione delle sezioni AT/MT in cui, nel 2025, il flusso di energia "
            "si è invertito — la distribuzione ha immesso verso l'alta tensione invece di "
            "prelevare — per almeno l'1% o il 5% delle ore dell'anno."
        )

        i = st.columns(4)
        i[0].metric("Sezioni con inversione", len(inv))
        i[1].metric("Cabine primarie coinvolte", inv["cabina"].nunique())
        i[2].metric("Sezioni oltre il 5% del tempo", int(inv["oltre_5_pct"].sum()))
        i[3].metric("Province interessate", inv["provincia"].nunique())

        c1, c2 = st.columns(2)
        with c1:
            per_prov = (inv.groupby("provincia")
                        .agg(sezioni=("sezione", "count"),
                             oltre5=("oltre_5_pct", "sum"),
                             cabine=("cabina", "nunique")).reset_index())
            fig = go.Figure()
            fig.add_bar(x=per_prov["provincia"], y=per_prov["sezioni"],
                        name="Almeno l'1% del tempo", marker_color="#FACC15")
            fig.add_bar(x=per_prov["provincia"], y=per_prov["oltre5"],
                        name="Almeno il 5%", marker_color="#EF4444")
            fig.update_layout(height=320, barmode="overlay", yaxis_title="sezioni AT/MT",
                              xaxis_title=None, title="Sezioni per provincia", **PLOT)
            grafico(fig, DOC.F_AUDIZIONI)
        with c2:
            top_cab = (inv.groupby(["cabina", "provincia"])
                       .agg(sezioni=("sezione", "count"), oltre5=("oltre_5_pct", "sum"))
                       .reset_index().nlargest(10, "sezioni"))
            fig = px.bar(top_cab.sort_values("sezioni"), x="sezioni", y="cabina",
                         orientation="h", color="provincia", text="sezioni")
            fig.update_layout(height=320, yaxis_title=None, xaxis_title="sezioni",
                              title="Le cabine più interessate", **PLOT)
            grafico(fig, DOC.F_AUDIZIONI)

        with st.expander("Elenco completo delle sezioni"):
            tab = inv[["provincia", "cabina", "sezione", "oltre_1_pct", "oltre_5_pct"]].copy()
            tab.columns = ["Provincia", "Cabina primaria", "Sezione", "≥ 1% del tempo", "≥ 5% del tempo"]
            st.dataframe(tab.sort_values(["Provincia", "Cabina primaria"]),
                         hide_index=True, width="stretch", height=320)

        quota5 = inv["oltre_5_pct"].sum() / len(inv) * 100
        st.info(
            f"**{inv['cabina'].nunique()} cabine primarie su 45** hanno almeno una sezione che "
            f"si inverte, e nel **{quota5:.0f}%** dei casi succede per oltre il 5% delle ore. "
            "Non è un guasto: è la generazione distribuita che ha superato il consumo locale. "
            "Ma le cabine primarie sono state progettate per un flusso a senso unico, e "
            "l'inversione è il segnale fisico che il limite di quel progetto è stato raggiunto. "
            "Udine e Pordenone concentrano il fenomeno, le stesse province dove i trasformatori "
            "risultano più saturi."
        )



    # ------------------------------------- dove preme la pipeline sulle cabine
    st.divider()
    st.subheader("Dove la pipeline preme sulla rete")
    sat = D.carica_per("saturazione_aree")
    geo_cp2 = D.carica_geojson("aree_cabine_primarie")
    ppa = D.carica_per("progetti_per_area")

    if not sat.empty and geo_cp2 is not None:
        st.caption(
            "Incrocio tra le aree di influenza delle cabine primarie e i progetti "
            "autorizzati o in istruttoria. Misura la **pressione autorizzativa**, non la "
            "saturazione elettrica: la capacità residua vera dipende dai trasformatori e "
            "dalla contemporaneità delle immissioni, dati che non sono pubblici per area."
        )

        p = st.columns(4)
        p[0].metric("Domanda di connessione",
                    f"{sat['mw_richiesti'].sum():,.0f} MW".replace(",", "."))
        p[1].metric("Aree interessate",
                    f"{int((sat['mw_richiesti'] > 0).sum())} su {len(sat)}")
        top5 = sat.nlargest(5, "mw_richiesti")["mw_richiesti"].sum()
        p[2].metric("Concentrazione", f"{top5 / sat['mw_richiesti'].sum() * 100:.0f}%",
                    "nelle prime cinque aree")
        p[3].metric("Densità massima", f"{sat['mw_per_km2'].max():.1f} MW/km²")

        vista_sat = st.radio(
            "Cosa mostrare", ["MW richiesti", "MW per km²"], horizontal=True,
            key="vista_sat")
        col_sat = "mw_richiesti" if vista_sat == "MW richiesti" else "mw_per_km2"

        fig = px.choropleth_map(
            sat, geojson=geo_cp2, locations="codice", color=col_sat,
            color_continuous_scale="Reds", map_style="carto-positron", zoom=7.2,
            center={"lat": 46.05, "lon": 13.10}, opacity=0.72,
            hover_name="codice",
            hover_data={"gestore": True, "progetti": True, "mw_richiesti": ":.0f",
                        "mw_per_km2": ":.2f", "area_km2": ":.0f", "codice": False},
            labels={"mw_richiesti": "MW richiesti", "mw_per_km2": "MW per km²"})
        fig.update_layout(height=560, margin=dict(t=10, b=10, l=0, r=0))
        grafico(fig, DOC.F_REGIONE + " e portale progetti FER, " + DOC.F_ELAB)

        c1, c2 = st.columns(2)
        with c1:
            tecnologie = [c for c in ["Solare", "Accumuli", "Bioenergie", "Idroelettrico"]
                          if c in sat.columns]
            comp = sat[["codice"] + tecnologie].melt(
                id_vars="codice", var_name="Tecnologia", value_name="MW")
            comp = comp[comp["MW"] > 0]
            top = sat.nlargest(10, "mw_richiesti")["codice"]
            fig = px.bar(comp[comp["codice"].isin(top)], x="MW", y="codice",
                         color="Tecnologia", orientation="h",
                         color_discrete_map={"Solare": "#FACC15", "Accumuli": "#A855F7",
                                             "Bioenergie": "#8B4513",
                                             "Idroelettrico": "#2563EB"})
            fig.update_layout(height=380, yaxis_title=None,
                              title="Le dieci aree più sollecitate", **PLOT)
            grafico(fig, DOC.F_ELAB)
        with c2:
            fig = px.scatter(sat[sat["mw_richiesti"] > 0], x="area_km2", y="mw_richiesti",
                             size="progetti", color="gestore", hover_name="codice",
                             log_x=True, log_y=True,
                             color_discrete_map={"e-distribuzione": "#2563EB",
                                                 "AcegasApsAmga": "#F97316",
                                                 "SECAB": "#22C55E"})
            fig.update_layout(height=380, xaxis_title="km² dell'area (log)",
                              yaxis_title="MW richiesti (log)",
                              title="Aree grandi non vuol dire aree cariche", **PLOT)
            grafico(fig, DOC.F_ELAB)

        st.info(
            f"**{sat['mw_richiesti'].sum():,.0f} MW di richieste su 43 aree**, ma le prime "
            f"cinque ne assorbono il {top5 / sat['mw_richiesti'].sum() * 100:.0f}%. ".replace(",", ".")
            + "La pressione non è diffusa: si concentra in poche aree della bassa pianura "
            "friulana, dove c'è spazio, irraggiamento e vicinanza alle dorsali. "
            "Sono le stesse zone in cui e-distribuzione segnala i trasformatori in rosso, "
            "ed è il motivo per cui le nuove cabine primarie in programma stanno lì.\n\n"
            "Va ricordato il tasso di realizzazione storico: circa **metà** di ciò che "
            "viene autorizzato non si costruisce. Una parte di questa pressione è capacità "
            "prenotata che non diventerà mai un impianto — ed è esattamente ciò che il "
            "meccanismo *first ready, first connect* dovrebbe liberare."
        )

        with st.expander("Elenco delle aree per pressione"):
            e = sat[sat["mw_richiesti"] > 0].sort_values("mw_richiesti", ascending=False)
            e = e[["codice", "gestore", "area_km2", "progetti", "mw_richiesti", "mw_per_km2"]]
            e.columns = ["Codice", "Gestore", "km²", "Progetti", "MW richiesti", "MW/km²"]
            st.dataframe(e.round(2), hide_index=True, width="stretch", height=320)


def _scheda_3():
    pv_prov = D.carica_per("pv_province")
    pv_tra = D.carica_per("pv_traiettoria")

    pv_serie = prod_fer[prod_fer["voce"] == "Fotovoltaico"]
    pv_pot = pot_fonte[pot_fonte["voce"] == "Fotovoltaico"]
    pv_gwh = anno_di(pv_serie)["valore"].sum()
    pv_mw = anno_di(pv_pot)["valore"].sum()

    st.subheader("Il fotovoltaico in Friuli-Venezia Giulia")
    k = st.columns(4)
    k[0].metric(f"Potenza {anno}", f"{pv_mw:,.0f} MW".replace(",", "."))
    k[1].metric(f"Produzione {anno}", f"{pv_gwh:,.0f} GWh".replace(",", "."))
    if pv_mw:
        k[2].metric("Ore equivalenti", f"{pv_gwh * 1000 / pv_mw:,.0f} h".replace(",", "."))
    k[3].metric("Quota sulla produzione regionale", f"{pv_gwh / p_tot * 100:.1f}%" if p_tot else "—")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Crescita della potenza installata**")
        fig = px.bar(pv_pot.sort_values("anno"), x="anno", y="valore",
                     color_discrete_sequence=["#FACC15"])
        fig.update_layout(height=340, yaxis_title="MW", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_AUDIZIONI)
    with c2:
        st.markdown("**Produzione annua**")
        fig = px.bar(pv_serie.sort_values("anno"), x="anno", y="valore",
                     color_discrete_sequence=["#F59E0B"])
        fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_AUDIZIONI)

    st.subheader("Distribuzione sul territorio")
    st.caption(f"Fonte: {DOC.FONTE_PROVINCE}, integrata con il PER FVG 2024.")

    prov_pv = pd.DataFrame([
        {"Provincia": p, "Produzione (GWh)": v["Fotovoltaico"]}
        for p, v in DOC.PRODUZIONE_PROVINCE.items()
    ])
    c3, c4 = st.columns(2)
    with c3:
        fig = px.bar(prov_pv.sort_values("Produzione (GWh)"), x="Produzione (GWh)", y="Provincia",
                     orientation="h", text_auto=".0f", color_discrete_sequence=["#FACC15"])
        fig.update_layout(height=300, yaxis_title=None,
                          title="Produzione fotovoltaica 2024", **PLOT)
        grafico(fig, DOC.F_TERNA_REG)
    with c4:
        if not pv_prov.empty:
            dens = pv_prov.dropna(subset=["densita_potenza_w_ab"])
            fig = px.bar(dens.sort_values("densita_potenza_w_ab"), x="densita_potenza_w_ab",
                         y="provincia", orientation="h", text_auto=".0f",
                         color_discrete_sequence=["#F59E0B"])
            fig.update_layout(height=300, yaxis_title=None, xaxis_title="W per abitante",
                              title="Potenza per abitante", **PLOT)
            grafico(fig, DOC.F_TERNA_REG)

    if not pv_prov.empty:
        st.markdown("**Dettaglio provinciale**")
        tab = pv_prov.rename(columns={
            "provincia": "Provincia", "impianti": "Impianti",
            "produzione_gwh_2022": "Produzione 2022 (GWh)", "potenza_mw": "Potenza (MW)",
            "densita_potenza_w_ab": "W/abitante", "densita_potenza_kw_km2": "kW/km²",
            "produzione_specifica_kwh_kw": "kWh per kW installato"})
        st.dataframe(tab, hide_index=True, width="stretch")
        st.caption(
            "L'ultima colonna è la produttività specifica: quanto rende un kW installato. "
            "Varia poco tra province — l'irraggiamento in regione è abbastanza uniforme, "
            "le differenze vere sono di quanto si è installato, non di quanto rende."
        )

    if not pv_tra.empty:
        st.subheader("La traiettoria del PER")
        prod = pv_tra[pv_tra["grandezza"] == "Produzione annua"]
        pot = pv_tra[pv_tra["grandezza"] == "Potenza di picco"]
        sup = pv_tra[pv_tra["grandezza"] == "Superficie occupata"]
        fig = go.Figure()
        fig.add_bar(x=pot["anno"], y=pot["valore"], name="Potenza di picco (MWp)",
                    marker_color="#FACC15")
        fig.add_scatter(x=prod["anno"], y=prod["valore"], name="Produzione (GWh)",
                        mode="lines+markers", line=dict(color="#111827", width=3), yaxis="y2")
        fig.update_layout(height=380, template="plotly_white",
                          yaxis=dict(title="MWp"),
                          yaxis2=dict(title="GWh", overlaying="y", side="right"),
                          margin=dict(t=30, b=10, l=10, r=10),
                          legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0))
        grafico(fig, DOC.F_AUDIZIONI)
        if not sup.empty:
            st.caption(
                "Superficie stimata dal PER per ospitare questa crescita: "
                + " · ".join(f"**{int(r.anno)}: {r.valore:,.0f} ha**".replace(",", ".")
                             for r in sup.itertuples())
            )

    st.info(
        "**Cosa manca ancora.** Qui c'è la distribuzione per provincia, ma non la "
        "mappatura vera: georeferenziazione degli impianti, distinzione tra tetti "
        "e impianti a terra, superficie agricola occupata, prossimità alle cabine "
        "primarie. Quei dati stanno in Atlaimpianti del GSE e nel catasto regionale "
        "degli impianti: quando li recuperiamo, questa scheda diventa una mappa."
    )

    st.divider()
    aree_fv = D.carica_per("aree_disponibili_fv")
    geo_fv = D.carica_geojson("aree_disponibili_fv")

    if not aree_fv.empty:
        st.subheader("Il fotovoltaico occupa davvero il suolo agricolo?")
        st.caption(
            "È la domanda che blocca più progetti, e si può rispondere con i numeri. "
            f"Fonte del denominatore: {DOC.FONTE_SAU}."
        )

        prog_s = D.carica_per("progetti_solare")
        ha_terra = 0.0
        if not prog_s.empty:
            att = prog_s[prog_s["stato"].isin(
                ["Autorizzato", "In costruzione", "In istruttoria", "Realizzato"])]
            ha_terra = float(att["superficie_ha"].sum())

        q = st.columns(4)
        q[0].metric("Superficie agricola utilizzata",
                    f"{DOC.SAU_FVG_HA:,.0f} ha".replace(",", "."))
        q[1].metric("Suolo dei progetti fotovoltaici", f"{ha_terra:,.0f} ha".replace(",", "."),
                    "autorizzati, in costruzione o realizzati")
        q[2].metric("Quota sulla SAU", f"{ha_terra / DOC.SAU_FVG_HA * 100:.2f}%")
        q[3].metric("Quota sul territorio regionale",
                    f"{ha_terra / DOC.SUPERFICIE_FVG_HA * 100:.2f}%")

        st.success(
            f"**Tutti i progetti fotovoltaici della regione occupano lo "
            f"{ha_terra / DOC.SAU_FVG_HA * 100:.1f}% della superficie agricola.** "
            "Non è una quota trascurabile in assoluto, ma va confrontata con quello che "
            "sta davvero succedendo: nel 2026 il **89,6% della nuova potenza installata "
            "è residenziale**, su tetti. Il campo a terra che si vede dalla strada è "
            "l'eccezione visibile di un fenomeno che avviene quasi tutto sui tetti."
        )

        # ---- che cosa si sta installando davvero
        st.markdown("**Cosa si sta installando: le nuove connessioni del 2026**")
        nuove = pd.DataFrame([
            {"Categoria": k, "MW": v["mw"], "Impianti": v["impianti"],
             "kW medi": v["mw"] * 1000 / v["impianti"]}
            for k, v in DOC.PV_NUOVE_2026.items()
        ])
        cc1, cc2 = st.columns(2)
        with cc1:
            fig = px.pie(nuove, values="MW", names="Categoria", hole=0.5,
                         color_discrete_sequence=["#FACC15", "#F59E0B", "#F97316", "#65A30D"])
            fig.update_traces(textinfo="percent")
            fig.update_layout(height=340, title="Potenza per categoria",
                              legend=dict(orientation="h", yanchor="top", y=-0.05, x=0),
                              margin=dict(t=48, b=10, l=10, r=24), template="plotly_white")
            grafico(fig, DOC.F_TERNA)
        with cc2:
            fig = px.bar(nuove.sort_values("kW medi"), x="kW medi", y="Categoria",
                         orientation="h", text_auto=".0f", log_x=True,
                         color_discrete_sequence=["#F59E0B"])
            fig.update_traces(cliponaxis=False)
            fig.update_layout(height=340, yaxis_title=None,
                              xaxis_title="kW medi per impianto (scala log)", **PLOT)
            grafico(fig, DOC.F_TERNA)

        # ---- rese diverse per tipologia
        st.markdown("**Non tutti i tetti rendono uguale**")
        rese = pd.DataFrame([
            {"Tipologia": k, "Ore equivalenti": v} for k, v in DOC.PV_ORE_PER_TIPO.items()
        ])
        fig = px.bar(rese, x="Ore equivalenti", y="Tipologia", orientation="h",
                     text_auto=".0f", color="Ore equivalenti",
                     color_continuous_scale="YlOrRd")
        fig.update_traces(cliponaxis=False)
        fig.update_layout(height=300, yaxis_title=None, coloraxis_showscale=False,
                          xaxis_title="kWh per kWp all'anno", **PLOT)
        grafico(fig, "elaborazione su dati Terna 2019-2022 e letteratura",
                "Il residenziale rende meno per falde non ottimali e ombreggiamenti; "
                "l'utility scale usa inseguitori su una parte del campo.")

        st.caption(
            "La differenza tra 1.000 e 1.200 ore equivalenti è del 20%: per produrre la "
            "stessa energia servono il 20% di pannelli in più sui tetti residenziali che "
            "in un campo ben progettato. È il vero costo del «facciamoli solo sui tetti»."
        )

        # ---- termini di paragone
        st.markdown("**Quanto è grande quel suolo, in cose che si vedono**")
        par = pd.DataFrame([
            {"Termine di paragone": k, "Equivalenti": ha_terra / v}
            for k, v in DOC.PARAGONI_SUOLO.items()
        ])
        st.dataframe(par.round(0), hide_index=True, width="stretch")
        st.caption(
            f"Fonte: {DOC.FONTE_SAU}. I {ha_terra:,.0f} ettari dei progetti fotovoltaici "
            "equivalgono a circa 3.200 campi da calcio, o a un sesto della superficie "
            "già impermeabilizzata della regione (38.380 ettari). "
            "La competizione col cibo è reale solo se si guarda il singolo campo: "
            "sul totale regionale, il fattore che sottrae terreno all'agricoltura è "
            "l'urbanizzazione, non il solare.".replace(",", ".")
        )

    st.divider()
    prog = D.carica_per("progetti_solare")
    geo_prog = D.carica_geojson("progetti_solare")

    if not prog.empty:
        st.subheader("Cosa c'è in cantiere, e quanto suolo occupa")
        st.caption(
            "Progetti fotovoltaici e agrivoltaici passati per il procedimento autorizzativo "
            "regionale. Potenza convertita da kW in MW, superficie da m² in ettari."
        )

        attivi = prog[prog["stato"].isin(
            ["Autorizzato", "In costruzione", "In istruttoria", "Realizzato"])]
        p = st.columns(4)
        p[0].metric("Progetti", len(prog))
        p[1].metric("Potenza in pipeline", f"{attivi['potenza_mw'].sum():,.0f} MW".replace(",", "."),
                    help="Esclusi i procedimenti sospesi o archiviati.")
        p[2].metric("Superficie interessata",
                    f"{attivi['superficie_ha'].sum():,.0f} ha".replace(",", "."))
        p[3].metric("Quota agrivoltaico",
                    f"{(prog['tipo'] == 'Agrivoltaico').sum() / len(prog) * 100:.0f}%",
                    f"{(prog['tipo'] == 'Agrivoltaico').sum()} progetti")

        c1, c2 = st.columns(2)
        with c1:
            per_stato = (prog.groupby("stato")
                         .agg(n=("nome", "count"), mw=("potenza_mw", "sum"))
                         .reset_index().sort_values("mw"))
            fig = px.bar(per_stato, x="mw", y="stato", orientation="h", text="n",
                         color="stato",
                         color_discrete_map={"Autorizzato": "#22C55E", "Realizzato": "#2563EB",
                                             "In costruzione": "#FACC15",
                                             "In istruttoria": "#F97316",
                                             "Sospeso o archiviato": "#9CA3AF", "Altro": "#D1D5DB"})
            fig.update_traces(textposition="outside", texttemplate="%{text} progetti",
                              cliponaxis=False)
            fig.update_layout(showlegend=False, height=320, xaxis_title="MW", yaxis_title=None,
                              title="Potenza per stato del procedimento", **PLOT)
            grafico(fig, DOC.F_REGIONE)
        with c2:
            fv = prog[prog["superficie_ha"] > 0].copy()
            fv["ha_per_mw"] = fv["superficie_ha"] / fv["potenza_mw"].replace(0, pd.NA)
            fig = px.scatter(fv.dropna(subset=["ha_per_mw"]), x="potenza_mw", y="superficie_ha",
                             color="tipo", hover_name="nome", log_x=True, log_y=True,
                             color_discrete_map={"Fotovoltaico": "#FACC15",
                                                 "Agrivoltaico": "#65A30D"})
            fig.update_layout(height=320, xaxis_title="MW (log)", yaxis_title="ettari (log)",
                              title="Potenza contro suolo occupato", **PLOT)
            grafico(fig, DOC.F_AUDIZIONI)

        if geo_prog is not None:
            st.markdown("**Dove sono**")
            # alcuni progetti non dichiarano la potenza: senza questo la mappa
            # riceve NaN come dimensione del marcatore e va in errore
            mappa_prog = attivi.copy()
            mappa_prog["size_mw"] = mappa_prog["potenza_mw"].fillna(0).clip(lower=0)
            fig = px.scatter_map(
                mappa_prog, lat="lat", lon="lon", size="size_mw", color="tipo",
                hover_name="nome",
                hover_data={"potenza_mw": ":.1f", "superficie_ha": ":.0f", "stato": True,
                            "lat": False, "lon": False, "size_mw": False},
                size_max=30, zoom=7.2, center={"lat": 45.95, "lon": 13.10},
                map_style="carto-positron",
                color_discrete_map={"Fotovoltaico": "#FACC15", "Agrivoltaico": "#65A30D"},
                labels={"potenza_mw": "MW", "superficie_ha": "ha"})
            fig.update_layout(height=520, margin=dict(t=10, b=10, l=0, r=0),
                              legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0,
                                          title=None))
            grafico(fig, DOC.F_AUDIZIONI)

        installato = anno_di(pot_fonte[pot_fonte["voce"] == "Fotovoltaico"])["valore"].sum()
        ha_mw = attivi["superficie_ha"].sum() / attivi["potenza_mw"].sum()
        st.info(
            f"In pipeline ci sono **{attivi['potenza_mw'].sum():,.0f} MW**, ".replace(",", ".")
            + f"più di quanto sia installato oggi ({installato:,.0f} MW). ".replace(",", ".")
            + f"Occupano **{attivi['superficie_ha'].sum():,.0f} ettari**, ".replace(",", ".")
            + f"cioè circa **{ha_mw:.1f} ettari per MW**. "
            f"L'agrivoltaico è {(prog['tipo'] == 'Agrivoltaico').sum()} progetti su {len(prog)}: "
            "non marginale, ma neanche prevalente. Da tenere presente che una quota dei "
            "procedimenti non arriva mai in esercizio — le audizioni indicano storicamente "
            f"circa il {DOC.TASSO_REALIZZAZIONE}%."
        )


def _scheda_4():
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Produzione rinnovabile per fonte")
        fig = px.area(prod_fer.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_fer["voce"]))
        fig.update_layout(height=360, yaxis_title="GWh", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    with c2:
        st.subheader(f"Potenza rinnovabile ({tipo_cap.lower()})")
        fig = px.area(pot_fer.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(pot_fer["voce"]))
        fig.update_layout(height=360, yaxis_title="MW", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    st.subheader("Idroelettrico per tipologia di impianto")
    st.caption("Il fluente segue la piovosità, bacini e serbatoi modulano.")
    fig = px.bar(idrico.sort_values("anno"), x="anno", y="valore", color="voce",
                 color_discrete_map=D.mappa_colori(idrico["voce"]))
    fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, barmode="stack", **PLOT)
    grafico(fig, DOC.F_TERNA)


def _scheda_5():
    bosco = D.carica_per("bosco")
    disp = D.carica_per("biomassa_province")

    st.subheader("La risorsa forestale del Friuli-Venezia Giulia")
    st.caption(
        "Dati PRI.FOR.MAN dal portale dei consorzi forestali, ripresi nel PER FVG 2024. "
        "Il bosco è classificato su due assi: se è **gestito** (con un piano di gestione "
        "attivo) e se è **accessibile** al prelievo."
    )

    if not bosco.empty:
        tot = bosco[bosco["sigla"] == "TOT"].iloc[0]
        gest = bosco[bosco["sigla"] == "G"]["superficie_ha"].sum()
        acc = bosco[bosco["sigla"].isin(["G - A", "NG - A"])]["superficie_ha"].sum()

        b = st.columns(4)
        b[0].metric("Superficie boscata", f"{tot['superficie_ha']:,.0f} ha".replace(",", "."))
        b[1].metric("Volume in piedi", f"{tot['volume_totale_m3'] / 1e6:.1f} mln m³",
                    f"{tot['volume_medio_m3_ha']:.0f} m³/ha")
        b[2].metric("Bosco gestito", f"{gest / tot['superficie_ha'] * 100:.0f}%",
                    f"{gest:,.0f} ha".replace(",", "."))
        b[3].metric("Bosco accessibile", f"{acc / tot['superficie_ha'] * 100:.0f}%",
                    f"{acc:,.0f} ha".replace(",", "."))

        st.error(
            "**Due errori nel foglio di calcolo del PER, qui corretti.** Il totale sommava "
            "anche i subtotali, contando ogni categoria due volte: 653.742 ha invece di "
            f"{tot['superficie_ha']:,.0f}. ".replace(",", ".")
            + "E i ktep del potenziale erano sbagliati di un fattore mille (0,07 invece di 70). "
            "Vale la pena segnalarlo a chi ha curato il piano."
        )

        dett = bosco[bosco["sigla"].isin(["NG - NA", "NG - A", "G - NA", "G - A"])].copy()
        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(dett.sort_values("superficie_ha"), x="superficie_ha", y="categoria",
                         orientation="h", text_auto=".0f", color="categoria",
                         color_discrete_map={
                             "Gestito, accessibile": "#22C55E",
                             "Gestito, non accessibile": "#65A30D",
                             "Non gestito, accessibile": "#F97316",
                             "Non gestito, non accessibile": "#9CA3AF"})
            fig.update_layout(showlegend=False, height=320, yaxis_title=None,
                              xaxis_title="ettari", title="Superficie per categoria", **PLOT)
            grafico(fig, DOC.F_PER)
        with c2:
            fig = px.bar(dett.sort_values("volume_medio_m3_ha"), x="volume_medio_m3_ha",
                         y="categoria", orientation="h", text_auto=".0f",
                         color_discrete_sequence=["#8B4513"])
            fig.update_layout(height=320, yaxis_title=None, xaxis_title="m³ per ettaro",
                              title="Densità di massa legnosa", **PLOT)
            grafico(fig, DOC.F_PER)

        st.caption(
            "Il paradosso del bosco friulano: la densità più alta è nel **gestito ma non "
            "accessibile** (246 m³/ha), cioè dove il legname c'è ed è pianificato ma manca la "
            "viabilità per portarlo fuori. Il **non gestito accessibile** — 104.844 ha, la "
            "categoria più estesa — ha invece la densità più bassa: bosco raggiungibile ma "
            "abbandonato."
        )

    if not disp.empty:
        st.divider()
        st.subheader("Quanta energia ci sarebbe, e quanta se ne usa")
        st.caption(
            "Due scenari di prelievo dal PER. Conversione con i parametri dichiarati nel "
            "piano: 3,4 MWh per tonnellata, 0,085985 tep per MWh."
        )

        tot_sc = (disp[disp["provincia"] == "TOT"]
                  .set_index("scenario")[["tonnellate", "gwh", "ktep"]])
        prov = disp[disp["provincia"] != "TOT"]

        c1, c2 = st.columns([1.2, 1])
        with c1:
            fig = px.bar(prov, x="provincia", y="ktep", color="scenario", barmode="group",
                         text_auto=".0f",
                         color_discrete_map={"Boschi accessibili al prelievo": "#22C55E",
                                             "Totale regionale": "#065F46"})
            fig.update_layout(height=340, xaxis_title=None, yaxis_title="ktep/anno",
                              title="Potenziale per provincia", **PLOT)
            grafico(fig, DOC.F_PER)
        with c2:
            bil_b = D.carica_per("bilancio_2021")
            usato = 0.0
            if not bil_b.empty:
                usato = bil_b.set_index("voce")["valore"].get("Biomasse", 0)
            conf = pd.DataFrame([
                {"Voce": "Usato oggi (bilancio 2021)", "ktep": usato},
                {"Voce": "Scenario prudente", "ktep": tot_sc.loc["Boschi accessibili al prelievo", "ktep"]},
                {"Voce": "Scenario esteso", "ktep": tot_sc.loc["Totale regionale", "ktep"]},
            ])
            fig = px.bar(conf, x="ktep", y="Voce", orientation="h", text_auto=".0f",
                         color="Voce",
                         color_discrete_sequence=["#8B4513", "#22C55E", "#065F46"])
            fig.update_layout(showlegend=False, height=340, yaxis_title=None,
                              title="Potenziale contro consumo", **PLOT)
            grafico(fig, DOC.F_PER)

        prud = tot_sc.loc["Boschi accessibili al prelievo", "ktep"]
        est = tot_sc.loc["Totale regionale", "ktep"]
        st.info(
            f"Il bilancio 2021 registra **{usato:.0f} ktep** di biomasse tra le risorse interne. "
            f"Il potenziale forestale stimato va da **{prud:.0f} ktep** (solo boschi accessibili) "
            f"a **{est:.0f} ktep** (tutto il prelievo teorico). "
            f"Anche nell'ipotesi prudente ci sarebbe margine, ma il vincolo non è la risorsa: è "
            "l'accessibilità, la viabilità forestale e la filiera locale. Udine da sola vale i "
            "due terzi del potenziale regionale."
        )

    st.warning(
        "**Cautela su questi numeri.** Il potenziale teorico non è disponibilità reale: "
        "prelevare tutto l'incremento annuo non è sostenibile né dal punto di vista "
        "ecologico né economico, e una parte del legname ha usi più pregiati dell'energia "
        "(edilizia, arredo). Il PER non distingue tra incremento annuo e massa in piedi, "
        "distinzione che cambia radicalmente il senso della cifra."
    )



    # ---------------------------------------------------- gli impianti sul territorio
    st.divider()
    st.subheader("Le caldaie a biomassa finanziate con fondi pubblici")
    bio_c = D.carica_per("biomassa_comuni_2015")
    bio_i = D.carica_per("biomassa_impianti_2015")

    if not bio_i.empty:
        k = st.columns(4)
        k[0].metric("Impianti censiti", len(bio_i))
        k[1].metric("Potenza termica", f"{bio_i['kw'].sum() / 1000:.1f} MW")
        k[2].metric("Legname consumato",
                    f"{bio_i['massa_t'].sum():,.0f} t/anno".replace(",", "."))
        pub = bio_i[bio_i["proprietario"] == "Pubblico"]
        k[3].metric("Quota pubblica", f"{pub['kw'].sum() / bio_i['kw'].sum() * 100:.0f}%",
                    f"{len(pub)} impianti su {len(bio_i)}")

        if not bio_c.empty:
            mappa_b = bio_c.copy()
            fig = px.scatter_map(
                mappa_b, lat="lat", lon="lon", size="kw", color="combustibile",
                hover_name="comune",
                hover_data={"impianti": True, "kw": ":.0f", "massa_t": ":.0f",
                            "lat": False, "lon": False},
                size_max=34, zoom=7.1, center={"lat": 46.3, "lon": 13.1},
                map_style="carto-positron",
                color_discrete_map={"Cippato": "#8B4513", "Legna a ciocchi": "#A16207",
                                    "Pellet": "#D97706"},
                labels={"kw": "kW termici", "massa_t": "tonnellate/anno"})
            fig.update_layout(height=480, margin=dict(t=10, b=10, l=0, r=0),
                              legend=dict(orientation="h", yanchor="bottom", y=1.01,
                                          x=0, title=None))
            grafico(fig, DOC.FONTE_BIOMASSA_2015,
                    "Le coordinate sono i centroidi comunali: gli impianti dello stesso "
                    "comune sono aggregati in un punto.")

        c1, c2 = st.columns(2)
        with c1:
            per_comb = (bio_i.groupby("combustibile")
                        .agg(impianti=("kw", "count"), kw=("kw", "sum"),
                             legname=("massa_t", "sum")).reset_index())
            fig = px.bar(per_comb.sort_values("kw"), x="kw", y="combustibile",
                         orientation="h", text="impianti", color="combustibile",
                         color_discrete_map={"Cippato": "#8B4513",
                                             "Legna a ciocchi": "#A16207",
                                             "Pellet": "#D97706"})
            fig.update_traces(textposition="outside", texttemplate="%{text} impianti",
                              cliponaxis=False)
            fig.update_layout(showlegend=False, height=300, yaxis_title=None,
                              xaxis_title="kW termici", **PLOT)
            grafico(fig, DOC.FONTE_BIOMASSA_2015)
        with c2:
            grandi = bio_i.nlargest(10, "kw")[["comune", "kw", "combustibile", "proprietario"]]
            grandi.columns = ["Comune", "kW", "Combustibile", "Proprietà"]
            st.markdown("**Le dieci caldaie maggiori**")
            st.dataframe(grandi, hide_index=True, width="stretch", height=300)
            st.caption(f"Fonte: {DOC.FONTE_BIOMASSA_2015}.")

        st.info(
            f"**Diciannove impianti pubblici fanno il "
            f"{pub['kw'].sum() / bio_i['kw'].sum() * 100:.0f}% della potenza**, e sono quasi "
            "tutti a cippato: sono le reti di teleriscaldamento di valle — Arta Terme, "
            "Tarvisio, Forni di Sopra. Le 92 caldaie a legna a ciocchi sono quasi tutte da "
            "30 kW: singole abitazioni. Il cippato è la filiera vera, la legna è "
            "autoconsumo domestico incentivato.\n\n"
            "La geografia è netta: **Carnia, Canal del Ferro e Valli del Natisone**. "
            "Dove c'è bosco accessibile e non c'è metano."
        )

        st.warning(
            "**Il dato è fermo a settembre 2015 e copre solo gli impianti finanziati.** "
            "Non è il parco a biomassa regionale: le caldaie e le stufe domestiche non "
            "incentivate sono decine di migliaia e pesano molto di più sui consumi — e "
            "sulla qualità dell'aria invernale. Serve un censimento aggiornato."
        )


def _scheda_6():
    bio = D.carica_per("progetti_bioenergie")
    st.subheader("Biogas e biometano")

    if not bio.empty:
        b = st.columns(4)
        b[0].metric("Progetti autorizzati o in corso", len(bio))
        b[1].metric("Di cui biometano", int((bio["tipo"] == "Biometano").sum()))
        b[2].metric("Potenza elettrica", f"{bio['potenza_mw'].sum():.1f} MW")
        b[3].metric("Superficie degli impianti",
                    f"{bio['superficie_ha'].sum():,.0f} ha".replace(",", "."))

        bil_b = D.carica_per("bilancio_2021")
        if not bil_b.empty:
            vb = bil_b.set_index("voce")["valore"]
            st.caption(
                f"Nel bilancio 2021 il biogas vale **{vb.get('Biogas', 0):.0f} ktep** tra le "
                f"risorse interne, più delle biomasse solide ({vb.get('Biomasse', 0):.0f} ktep). "
                "È la bioenergia più rilevante della regione, e quasi tutta di origine agricola."
            )

        mappa_bio2 = bio.copy()
        mappa_bio2["size_ha"] = mappa_bio2["superficie_ha"].fillna(0).clip(lower=0)
        fig = px.scatter_map(
            mappa_bio2, lat="lat", lon="lon", size="size_ha", color="tipo",
            hover_name="nome",
            hover_data={"potenza_mw": ":.2f", "superficie_ha": ":.0f", "stato": True,
                        "lat": False, "lon": False, "size_ha": False},
            size_max=28, zoom=7.4, center={"lat": 45.95, "lon": 13.10},
            map_style="carto-positron",
            color_discrete_map={"Biometano": "#8B4513", "Biomasse": "#A16207"})
        fig.update_layout(height=460, margin=dict(t=10, b=10, l=0, r=0),
                          legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, title=None))
        grafico(fig, DOC.F_REGIONE)

        elenco = bio[["nome", "tipo", "potenza_mw", "superficie_ha", "stato"]].copy()
        elenco.columns = ["Impianto", "Tipo", "MW", "Ettari", "Stato"]
        st.dataframe(elenco.sort_values("Ettari", ascending=False).round(2),
                     hide_index=True, width="stretch", height=320)

    st.divider()
    st.subheader("Il nodo del suolo: quanto rende un ettaro")
    st.caption(
        "Confronto tra produrre elettricità da mais insilato e produrla dal fotovoltaico "
        "sulla stessa superficie. I parametri sono modificabili: servono a mostrare "
        "l'ordine di grandezza, non a stimare un impianto specifico."
    )

    m1, m2, m3 = st.columns(3)
    with m1:
        resa_mais = st.slider("Resa del mais (t/ha di insilato)", 30, 70, 50)
    with m2:
        metano_t = st.slider("Biogas (m³ di metano per t di insilato)", 80, 130, 105)
    with m3:
        rend_cog = st.slider("Rendimento elettrico del cogeneratore (%)", 30, 45, 38) / 100

    kwh_m3_metano = 9.97  # potere calorifico del metano, kWh per m3
    mwh_ha_bio = resa_mais * metano_t * kwh_m3_metano * rend_cog / 1000
    mwh_ha_pv = DOC.PV_ORE_EQUIVALENTI * (1000 / DOC.PV_ETTARI_PER_MWP) / 1000

    r = st.columns(3)
    r[0].metric("Biogas da mais", f"{mwh_ha_bio:,.0f} MWh/ha".replace(",", "."))
    r[1].metric("Fotovoltaico", f"{mwh_ha_pv:,.0f} MWh/ha".replace(",", "."))
    r[2].metric("Rapporto", f"{mwh_ha_pv / mwh_ha_bio:.0f}×",
                "a favore del fotovoltaico")

    conf = pd.DataFrame([
        {"Tecnologia": "Biogas da mais insilato", "MWh per ettaro": mwh_ha_bio},
        {"Tecnologia": "Fotovoltaico a terra", "MWh per ettaro": mwh_ha_pv},
    ])
    fig = px.bar(conf, x="MWh per ettaro", y="Tecnologia", orientation="h", text_auto=".0f",
                 color="Tecnologia",
                 color_discrete_map={"Biogas da mais insilato": "#8B4513",
                                     "Fotovoltaico a terra": "#FACC15"})
    fig.update_layout(showlegend=False, height=240, yaxis_title=None, **PLOT)
    grafico(fig, DOC.F_PER)

    st.info(
        "È il calcolo che David Pimentel e altri hanno reso familiare nel dibattito sui "
        "biocarburanti: la fotosintesi converte in biomassa una frazione minima "
        "dell'energia solare incidente, e ogni passaggio successivo — insilamento, "
        "digestione, combustione — ne perde ancora. Un pannello salta tutti quei passaggi. "
        f"Sulla stessa superficie il fotovoltaico rende circa **{mwh_ha_pv / mwh_ha_bio:.0f} volte** "
        "l'elettricità del mais da biogas.\n\n"
        "Questo **non** rende il biogas inutile: i digestori che trattano deiezioni zootecniche "
        "e scarti agroindustriali non occupano suolo dedicato, gestiscono un rifiuto che "
        "altrimenti emette metano, e producono digestato che torna al campo. Il confronto "
        "colpisce le colture dedicate, non la filiera degli scarti."
    )

    st.warning(
        "**Manca il dato che servirebbe davvero**: l'alimentazione di ciascun impianto — "
        "mais e colture dedicate, deiezioni, fanghi, FORSU, scarti agroindustriali. "
        "Lo shapefile regionale riporta solo tipo, potenza e superficie. Senza quella "
        "colonna non si può dire quanta parte del biogas friulano stia sul lato "
        "«colture dedicate» e quanta sul lato «scarti», che è la distinzione decisiva."
    )



    # ------------------------------------------------------- la dieta, per quel poco che si sa
    st.divider()
    st.subheader("Che cosa mangiano i digestori")
    dieta = D.carica_per("bio_impianti_dieta")
    pipe = D.carica_per("biometano_pipeline")

    st.caption(
        "È la domanda decisiva — colture dedicate o scarti — e la risposta oggi è "
        "parziale. Quella che segue è una ricognizione da fonti aperte, non un registro."
    )

    if not dieta.empty:
        tab = dieta[["impianto", "comune", "provincia", "tipologia", "dieta", "stato",
                     "fonte", "affidabilita"]].copy()
        tab.columns = ["Impianto", "Comune", "Prov.", "Tipologia", "Alimentazione",
                       "Stato", "Fonte", "Affidabilità"]
        st.dataframe(tab, hide_index=True, width="stretch")
        st.caption(
            "Fonte: ricognizione su fonti aperte (comunicati aziendali, stampa, "
            "documentazione regionale). La colonna «Affidabilità» dichiara quanto è solida "
            "ciascuna riga: nessuna arriva ad «alta»."
        )

        agri = dieta["dieta"].astype(str).str.contains("agricol|zootecnic|coltur", case=False).sum()
        scarti = dieta["dieta"].astype(str).str.contains("scart|FORSU|reflu|rifiut", case=False).sum()
        d1, d2, d3 = st.columns(3)
        d1.metric("Impianti tracciati", len(dieta))
        d2.metric("Con matrici agricole", int(agri))
        d3.metric("Con scarti o rifiuti", int(scarti))

    if not pipe.empty:
        st.markdown("**I comuni con progetti di biometano**")
        st.caption(
            f"{len(pipe)} comuni interessati da progetti in iter o realizzati. "
            "L'elenco dice dove, non con quale alimentazione."
        )
        st.dataframe(pipe.rename(columns={"comune": "Comune"}), hide_index=True,
                     width="stretch", height=240)

    st.error(
        "**Questo è il buco più serio dell'intera applicazione, e va detto chiaramente.** "
        "In regione ci sono **57 comuni con impianti a biogas per 120,6 MW**, ma di questi "
        "conosciamo l'alimentazione solo per una manciata. Senza sapere quanta parte va a "
        "**colture dedicate** e quanta a **reflui zootecnici e scarti**, la valutazione "
        "ambientale del biogas friulano resta sospesa: le due filiere hanno bilanci di "
        "suolo, di acqua e di carbonio completamente diversi, e il confronto per ettaro "
        "della sezione precedente colpisce solo la prima.\n\n"
        "**Tre strade per chiudere il buco**, in ordine di praticabilità:\n"
        "1. **Atlaimpianti del GSE** riporta la tipologia di alimentazione per gli impianti "
        "incentivati. L'accesso massivo richiede una richiesta formale, che APE FVG può "
        "presentare come ente pubblico.\n"
        "2. Le **autorizzazioni AIA regionali** contengono la matrice in ingresso impianto "
        "per impianto e sono pubbliche: 57 comuni sono un lavoro manuale ma finito.\n"
        "3. Il **registro biometano del GSE** copre gli impianti convertiti, che sono i più "
        "rilevanti per il futuro ma pochi per il presente."
    )


def _scheda_7():
    st.subheader("Il parco idroelettrico regionale")
    st.caption(f"Fonte: {DOC.FONTE_IDRO}, integrata con la serie storica Terna.")

    i = st.columns(4)
    i[0].metric("Impianti", f"{DOC.IDRO_PARCO['Impianti']}")
    i[1].metric("Potenza efficiente lorda", f"{DOC.IDRO_PARCO['Potenza efficiente lorda (MW)']:.0f} MW")
    i[2].metric("Producibilità media", f"{DOC.IDRO_PARCO['Producibilità media annua (GWh)']:,.0f} GWh".replace(",", "."))
    idro_anno = anno_di(idrico)["valore"].sum()
    i[3].metric(f"Prodotto nel {anno}", f"{idro_anno:,.0f} GWh".replace(",", "."))

    idro_tot = idrico.groupby("anno")["valore"].sum()
    if len(idro_tot) > 1:
        mn, mx = idro_tot.min(), idro_tot.max()
        st.caption(
            f"Tra il {idro_tot.idxmin()} e il {idro_tot.idxmax()} la produzione è oscillata da "
            f"**{mn:,.0f}** a **{mx:,.0f} GWh**: un fattore {mx / mn:.1f}. ".replace(",", ".")
            + "L'idroelettrico è rinnovabile ma non è costante — dipende da quanta acqua arriva."
        )

    c1, c2 = st.columns([1.5, 1])
    with c1:
        st.markdown("**Produzione per tipologia di impianto**")
        fig = px.bar(idrico.sort_values("anno"), x="anno", y="valore", color="voce",
                     color_discrete_map=D.mappa_colori(idrico["voce"]))
        prod_media = DOC.IDRO_PARCO["Producibilità media annua (GWh)"]
        fig.add_hline(y=prod_media, line_dash="dash", line_color="#111827",
                      annotation_text=f"producibilità media {prod_media:.0f} GWh",
                      annotation_position="top left")
        fig.update_layout(height=400, yaxis_title="GWh", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    with c2:
        st.markdown("**Composizione nell'anno selezionato**")
        m = anno_di(idrico)
        m = m[m["valore"] > 0]
        if not m.empty:
            fig = px.pie(m, values="valore", names="voce", hole=0.5,
                         color="voce", color_discrete_map=D.mappa_colori(m["voce"]))
            fig.update_traces(textinfo="percent")
            fig.update_layout(height=400, **PLOT)
            grafico(fig, DOC.F_TERNA)

    st.subheader("Quanto lavora il parco idroelettrico")
    st.caption(
        "Ore equivalenti annue: produzione divisa per la potenza installata. "
        "Sono la firma della variabilità idrologica, non dell'efficienza degli impianti."
    )
    pot_idro = pot_fonte[pot_fonte["voce"] == "Idrico"]
    ore_idro = (idro_tot / pot_idro.set_index("anno")["valore"] * 1000).dropna().reset_index(name="ore")
    fig = px.bar(ore_idro, x="anno", y="ore", color_discrete_sequence=["#2563EB"])
    fig.add_hline(y=ore_idro["ore"].mean(), line_dash="dot", line_color="#111827",
                  annotation_text=f"media {ore_idro['ore'].mean():.0f} ore",
                  annotation_position="top left")
    fig.update_layout(height=340, yaxis_title="ore/anno", xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_TERNA)

    st.info(
        "Il PER stima una producibilità media di "
        f"{DOC.IDRO_PARCO['Producibilità media annua (GWh)']:,.0f} GWh e prevede di arrivare a ".replace(",", ".")
        + "2.231 GWh al 2045: un margine di crescita limitato, perché i siti migliori sono già "
        "sfruttati. L'espansione passa da efficientamento degli impianti esistenti e "
        "mini-idro, non da nuovi grandi invasi."
    )

    st.divider()
    centrali = D.carica_per("centrali_idro")
    if not centrali.empty:
        st.subheader("Le centrali sul territorio")
        cat = D.carica_per("centrali_idro_catasto")
        mont = D.carica_per("idro_montagna")

        if not cat.empty:
            esist = cat[cat["stato"] == "Esistente"]
            st.caption(
                "Catasto regionale delle derivazioni idriche: ogni punto è una centrale "
                "con la sua concessione. Attenzione, la **potenza di concessione** non è "
                "la potenza efficiente — è la potenza nominale media legata alla portata "
                "derivabile, e la somma regionale sta molto sotto i 528,9 MW misurati da Terna."
            )
            c = st.columns(4)
            c[0].metric("Centrali censite", len(cat), f"{len(esist)} esistenti")
            c[1].metric("Potenza di concessione", f"{esist['potenza_mw'].sum():.0f} MW")
            c[2].metric("In progetto o realizzazione",
                        int((cat["stato"].isin(["In progetto", "In realizzazione"])).sum()),
                        f"{cat[cat['stato'].isin(['In progetto', 'In realizzazione'])]['potenza_mw'].sum():.1f} MW")
            mediana = esist["potenza_mw"].median()
            c[3].metric("Potenza mediana", f"{mediana * 1000:.0f} kW",
                        "metà delle centrali sta sotto")

            m = cat.copy()
            m["size_mw"] = m["potenza_mw"].fillna(0).clip(lower=0.01)
            fig = px.scatter_map(
                m, lat="lat", lon="lon", size="size_mw", color="stato",
                hover_name="nome",
                hover_data={"potenza_mw": ":.3f", "salto_m": ":.0f", "scadenza": True,
                            "lat": False, "lon": False, "size_mw": False},
                size_max=30, zoom=7.1, center={"lat": 46.3, "lon": 13.0},
                map_style="carto-positron",
                color_discrete_map={"Esistente": "#2563EB", "In progetto": "#F97316",
                                    "In realizzazione": "#FACC15", "Rinunciata": "#D1D5DB"},
                labels={"potenza_mw": "MW di concessione", "salto_m": "salto (m)"})
            fig.update_layout(height=540, margin=dict(t=10, b=10, l=0, r=0),
                              legend=dict(orientation="h", yanchor="bottom", y=1.01,
                                          x=0, title=None))
            grafico(fig, DOC.F_REGIONE + " — catasto derivazioni idriche")

            c1, c2 = st.columns(2)
            with c1:
                fig = px.histogram(esist[esist["potenza_mw"] > 0], x="potenza_mw", nbins=40,
                                   log_y=True, color_discrete_sequence=["#2563EB"])
                fig.update_layout(height=300, xaxis_title="MW di concessione",
                                  yaxis_title="centrali (scala log)",
                                  title="Quasi tutte piccolissime", **PLOT)
                grafico(fig, DOC.F_REGIONE)
            with c2:
                sal = esist.dropna(subset=["salto_m", "potenza_mw"])
                sal = sal[(sal["salto_m"] > 0) & (sal["potenza_mw"] > 0)]
                fig = px.scatter(sal, x="salto_m", y="potenza_mw", log_x=True, log_y=True,
                                 hover_name="nome", color_discrete_sequence=["#2563EB"],
                                 opacity=0.6)
                fig.update_layout(height=300, xaxis_title="salto (m, log)",
                                  yaxis_title="MW (log)",
                                  title="Il salto fa la potenza", **PLOT)
                grafico(fig, DOC.F_REGIONE)

            piccole = (esist["potenza_mw"] < 1).sum()
            st.info(
                f"**{piccole} centrali su {len(esist)} stanno sotto il megawatt**, e la "
                f"mediana è di {mediana * 1000:.0f} kW: il parco idroelettrico friulano è "
                "fatto di una lunga coda di micro-derivazioni su rogge, canali e acquedotti, "
                "più poche grandi centrali di montagna. "
                f"Le nuove concessioni in progetto valgono "
                f"{cat[cat['stato'] == 'In progetto']['potenza_mw'].sum():.1f} MW su 47 pratiche: "
                "meno di 200 kW l'una. Il grande idro è finito, resta il capillare."
            )

        if not mont.empty:
            st.markdown("**Le grandi centrali di montagna**")
            tab = mont[["impianto", "comune", "corso_acqua", "gestore", "potenza_MW",
                        "producibilita_GWh_anno", "tipo_impianto", "salto_m"]].copy()
            tab.columns = ["Impianto", "Comune", "Corso d'acqua", "Gestore", "MW",
                           "GWh/anno", "Tipo", "Salto (m)"]
            st.dataframe(tab.sort_values("MW", ascending=False), hide_index=True,
                         width="stretch")
            st.caption(
                f"Fonte: {DOC.F_PER}, dati di impianto. "
                f"Queste {len(mont)} centrali valgono {mont['potenza_MW'].sum():.0f} MW e "
                f"circa {mont['producibilita_GWh_anno'].sum():.0f} GWh l'anno: "
                "la dorsale storica del sistema, quasi tutta in Carnia e Canal del Ferro."
            )

def _scheda_8():
    st.subheader("Il gas naturale nel sistema energetico regionale")
    bil = D.carica_per("bilancio_2021")
    consumi_f = D.carica_per("consumi_finali_2021")

    if not bil.empty:
        v = bil.set_index("voce")["valore"]
        gas_import = v.get("Combustibili gassosi", 0)
        gas_finali = consumi_f[consumi_f["vettore"].str.contains("gassos", case=False, na=False)]
        gas_fin_tot = gas_finali["valore"].sum()
        gas_trasf = max(0.0, gas_import - gas_fin_tot)

        g = st.columns(4)
        g[0].metric("Gas in ingresso (2021)", f"{gas_import:,.0f} ktep".replace(",", "."))
        g[1].metric("Agli usi finali", f"{gas_fin_tot:,.0f} ktep".replace(",", "."),
                    f"{gas_fin_tot / gas_import * 100:.0f}% del totale" if gas_import else None)
        g[2].metric("Alla trasformazione", f"{gas_trasf:,.0f} ktep".replace(",", "."),
                    f"{gas_trasf / gas_import * 100:.0f}% del totale" if gas_import else None)
        g[3].metric("Quota sul consumo interno lordo",
                    f"{gas_import / v.get('Consumo interno lordo', 1) * 100:.0f}%")

        st.caption(
            "Il gas è il primo vettore del sistema regionale. Circa due terzi vanno "
            "direttamente agli usi finali — soprattutto riscaldamento civile e calore "
            "di processo — e un terzo entra in centrale per produrre elettricità e calore."
        )

        # Sankey del solo gas
        nodi_g = ["Gas naturale in ingresso", "Usi finali diretti", "Generazione e cogenerazione"]
        nodi_g += [f"{r.settore} (diretto)" for r in gas_finali.itertuples() if r.valore > 0]
        nodi_g += ["Elettricità e calore", "Perdite di conversione"]
        ig = {n: i for i, n in enumerate(nodi_g)}
        colori_g = ["#9CA3AF", "#6B7280", "#F97316"] + \
                   ["#2563EB"] * len([r for r in gas_finali.itertuples() if r.valore > 0]) + \
                   ["#FACC15", "#EF4444"]
        sg, tg, vg, cg = [], [], [], []

        def lg(a, b_, val, col):
            if val and val > 0:
                sg.append(ig[a]); tg.append(ig[b_]); vg.append(float(val)); cg.append(col)

        lg("Gas naturale in ingresso", "Usi finali diretti", gas_fin_tot, "rgba(107,114,128,0.35)")
        lg("Gas naturale in ingresso", "Generazione e cogenerazione", gas_trasf, "rgba(249,115,22,0.35)")
        for r in gas_finali.itertuples():
            lg("Usi finali diretti", f"{r.settore} (diretto)", r.valore, "rgba(37,99,235,0.3)")
        rend_gas = v.get("Rendimento", 0.64)
        utile = gas_trasf * rend_gas
        lg("Generazione e cogenerazione", "Elettricità e calore", utile, "rgba(250,204,21,0.45)")
        lg("Generazione e cogenerazione", "Perdite di conversione", gas_trasf - utile,
           "rgba(239,68,68,0.3)")

        fig = go.Figure(go.Sankey(
            node=dict(pad=18, thickness=20, label=nodi_g, color=colori_g,
                      line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
            link=dict(source=sg, target=tg, value=vg, color=cg,
                      hovertemplate="%{value:.0f} ktep<extra></extra>"),
        ))
        fig.update_layout(height=440, font_size=12, margin=dict(t=20, b=20, l=10, r=10))
        grafico(fig, DOC.F_TERNA)
        st.caption(
            f"Il rendimento applicato al ramo di trasformazione è quello medio del "
            f"sistema regionale ({rend_gas * 100:.0f}%), non misurato sul solo gas."
        )

        st.subheader("Dove va il gas che non passa dalla centrale")
        fig = px.bar(gas_finali.sort_values("valore"), x="valore", y="settore", orientation="h",
                     text_auto=".0f", color_discrete_sequence=["#9CA3AF"])
        fig.update_layout(height=300, xaxis_title="ktep", yaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    st.divider()
    st.subheader("Il lato elettrico: produzione da gas")
    gas_el = prod_comb[prod_comb["voce"].str.contains("gas", case=False, na=False)]
    if not gas_el.empty:
        c1, c2 = st.columns(2)
        with c1:
            fig = px.area(gas_el.sort_values("anno"), x="anno", y="valore",
                          color_discrete_sequence=["#9CA3AF"])
            fig.update_layout(height=340, yaxis_title="GWh elettrici", xaxis_title=None,
                              title="Produzione elettrica da gas naturale", **PLOT)
            grafico(fig, DOC.F_TERNA)
        with c2:
            em_gas = emissioni[emissioni["voce"].str.contains("gas", case=False, na=False)]
            fig = px.area(em_gas.sort_values("anno"), x="anno", y="valore",
                          color_discrete_sequence=["#EF4444"])
            fig.update_layout(height=340, yaxis_title="Mt CO₂", xaxis_title=None,
                              title="Emissioni dalla generazione a gas", **PLOT)
            grafico(fig, DOC.F_TERNA)

        picco = gas_el.loc[gas_el["valore"].idxmax()]
        ultimo = gas_el[gas_el["anno"] == gas_el["anno"].max()]["valore"].sum()
        st.info(
            f"La generazione elettrica a gas ha toccato il massimo nel **{int(picco['anno'])}** "
            f"con {picco['valore']:,.0f} GWh ed è scesa a **{ultimo:,.0f} GWh** nell'ultimo anno "
            "disponibile: circa ".replace(",", ".")
            + f"{(1 - ultimo / picco['valore']) * 100:.0f}% in meno. "
            "È il singolo fattore che spiega quasi tutto il calo delle emissioni elettriche "
            "regionali. La scheda «Termo & CO₂» disaggrega per categoria di impianto."
        )


def _scheda_9():
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Produzione termoelettrica per combustibile")
        fig = px.area(prod_comb.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_comb["voce"]))
        fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    with c2:
        st.subheader("Emissioni di CO₂ per combustibile")
        fig = px.area(emissioni.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(emissioni["voce"]))
        fig.update_layout(height=340, yaxis_title="Mt CO₂", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    st.subheader("Intensità carbonica della generazione")
    st.caption("Emissioni totali del parco termoelettrico divise per la produzione elettrica lorda regionale.")
    tot_em = emissioni.groupby("anno")["valore"].sum()
    inten = (tot_em * 1e6 / tot_y).dropna().reset_index(name="g_kwh")
    fig = px.line(inten, x="anno", y="g_kwh", markers=True, color_discrete_sequence=["#DC2626"])
    fig.update_layout(height=300, yaxis_title="g CO₂/kWh", xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_TERNA)

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Cogenerative vs non cogenerative")
        fig = px.bar(prod_cat.sort_values("anno"), x="anno", y="valore", color="voce",
                     color_discrete_map=D.mappa_colori(prod_cat["voce"]))
        fig.update_layout(height=340, yaxis_title="GWh elettrici", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    with c4:
        st.subheader("Calore utile da cogenerazione")
        cal = calore.copy()
        cal["voce"] = cal["voce"].map(IMPIANTI_COGEN).fillna(cal["voce"])
        fig = px.bar(cal.sort_values("anno"), x="anno", y="valore", color="voce")
        fig.update_layout(height=340, yaxis_title="GWh termici", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_TERNA)

    st.divider()
    st.subheader("Gli impianti termoelettrici della regione")
    cen = pd.DataFrame(DOC.CENTRALI_TERMO)

    t1, t2, t3, t4 = st.columns(4)
    t1.metric("Impianti censiti", len(cen))
    t2.metric("Potenza complessiva", f"{cen['mw'].sum():,.0f} MW".replace(",", "."))
    t3.metric("I due maggiori",
              f"{cen.nlargest(2, 'mw')['mw'].sum() / cen['mw'].sum() * 100:.0f}%",
              "della potenza termoelettrica")
    t4.metric("In dismissione",
              f"{cen[cen['stato'] == 'Dismissione']['mw'].sum():.0f} MW")

    fig = px.scatter_map(
        cen, lat="lat", lon="lon", size="mw", color="combustibile",
        hover_name="nome",
        hover_data={"comune": True, "mw": ":.1f", "tecnologia": True, "stato": True,
                    "lat": False, "lon": False},
        size_max=44, zoom=7.1, center={"lat": 45.95, "lon": 13.3},
        map_style="carto-positron",
        color_discrete_map={"Gas naturale": "#9CA3AF", "Carbone": "#111827",
                            "Rifiuti urbani e speciali": "#A855F7",
                            "Rifiuti speciali": "#C084FC",
                            "Gas naturale e off-gas siderurgico": "#4B5563"})
    fig.update_layout(height=500, margin=dict(t=10, b=10, l=0, r=0),
                      legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, title=None))
    grafico(fig, DOC.FONTE_CENTRALI,
            "Coordinate al centro del sito, non rilevate sul campo.")

    fig = px.bar(cen.sort_values("mw"), x="mw", y="nome", orientation="h", color="stato",
                 text_auto=".0f", log_x=True,
                 color_discrete_map={"In esercizio": "#2563EB", "Dismissione": "#EF4444"})
    fig.update_layout(height=380, yaxis_title=None, xaxis_title="MW (scala logaritmica)", **PLOT)
    grafico(fig, DOC.FONTE_CENTRALI)

    for r in cen.sort_values("mw", ascending=False).itertuples():
        with st.expander(f"{r.nome} — {r.mw:.0f} MW, {r.comune} ({r.prov})"):
            st.markdown(f"**{r.tecnologia}**, alimentata a {r.combustibile.lower()}. "
                        f"Stato: {r.stato.lower()}.\n\n{r.nota}")

    st.info(
        f"Il parco termoelettrico friulano è **concentratissimo**: Torviscosa e Monfalcone "
        f"insieme fanno {cen.nlargest(2, 'mw')['mw'].sum():.0f} MW su "
        f"{cen['mw'].sum():,.0f} censiti. ".replace(",", ".")
        + "La sola Torviscosa vale il 54% del termoelettrico tradizionale regionale. "
        "Monfalcone, a carbone, dal maggio 2024 non è più abilitata ai mercati: è la ragione "
        "principale del crollo delle emissioni elettriche che si vede nei grafici sopra. "
        f"Il censimento copre {cen['mw'].sum() / 1530.9 * 100:.0f}% della potenza "
        "termoelettrica che Terna registra per la regione: mancano gli autoproduttori minori."
    )


def _scheda_10():
    st.subheader("Idrogeno: a che punto è il Friuli-Venezia Giulia")
    st.caption(f"Fonte: {DOC.FONTE_H2}.")

    n = DOC.H2_NAHV
    h = st.columns(4)
    h[0].metric("Finanziamento NAHV", f"{n['Finanziamento europeo (mln €)']} mln €")
    h[1].metric("Organizzazioni partner", n["Organizzazioni partner"])
    h[2].metric("Durata del progetto", f"{n['Durata (mesi)']} mesi")
    h[3].metric("Autobus a idrogeno previsti", sum(DOC.H2_MEZZI_TPL.values()))

    t = DOC.TARGET_FER_ELETTRICA_2030
    st.info(
        f"**Il contesto in cui l'idrogeno regionale deve stare.** La Strategia dichiara "
        f"l'obiettivo di coprire il **{t['copertura_pct']}%** dell'elettricità regionale con "
        f"fonti rinnovabili entro il 2030, installando circa **{t['nuova_capacita_gw']} GW** "
        f"in più rispetto al 2020, in prevalenza fotovoltaico. "
        f"Oggi la quota rinnovabile sulla produzione è del {quota_fer:.0f}%, ma sulla "
        f"**domanda** regionale è molto più bassa, perché un terzo dell'elettricità viene "
        "importata. L'idrogeno rinnovabile deve trovare posto dentro quel numero, non "
        f"accanto. ({t['riferimento']}.)"
    )

    st.markdown(
        "La **North Adriatic Hydrogen Valley** è il progetto che tiene insieme "
        "Friuli-Venezia Giulia, Slovenia e Croazia, finanziato da Horizon Europe e "
        "avviato a settembre 2023. Attorno ci sono i progetti PNRR e una filiera "
        "industriale regionale già interessata: siderurgia, trasporti, chimica, "
        "oltre 120 attori mappati nella consultazione del 2022, polarizzati su Udine e Trieste."
    )

    st.subheader("I progetti concreti")
    prog = pd.DataFrame(DOC.H2_PROGETTI)
    hub = DOC.H2_PROGETTI[0]
    p1, p2, p3, p4 = st.columns(4)
    p1.metric("Elettrolisi Hydrogen Hub Trieste", f"{hub['elettrolisi_mw']:.0f} MW")
    p2.metric("Fotovoltaico dedicato", f"{hub['fv_dedicato_mwp']:.2f} MWp")
    p3.metric("Produzione attesa", f"{hub['produzione_ton_anno']} t/anno",
              f"di cui {hub['da_fv_ton_anno']} t da FV")
    p4.metric("Finanziamento PNRR", f"{hub['finanziamento_mln']} mln €")

    for pr in DOC.H2_PROGETTI:
        with st.expander(f"{pr['nome']} — {pr['soggetto']}"):
            st.markdown(f"**Stato:** {pr['stato']}\n\n{pr['nota']}")

    st.subheader("Le criticità dichiarate dalla Regione")
    for titolo, testo in DOC.H2_CRITICITA:
        st.markdown(f"**{titolo}** — {testo}")

    st.divider()
    # ------------------------------------------- dove l'idrogeno serve davvero
    st.divider()
    st.subheader("Dove l'idrogeno serve, e dove no")
    st.caption(
        "L'idrogeno non compete con la batteria né con la pompa di calore: è candidato "
        "solo dove l'elettrificazione diretta è difficile. Isolare quei settori serve a "
        "dimensionare il problema. Consumi elettrici per settore merceologico, Terna 2023."
    )

    # Niente accenti nei nomi di colonna: itertuples li rinomina in _1, _2...
    hta = pd.DataFrame(DOC.HARD_TO_ABATE,
                       columns=["Settore", "GWh elettrici", "motivo", "Rilevanza"])
    rilevanti = hta[hta["Rilevanza"] == "alto"]

    h = st.columns(4)
    h[0].metric("Settori a rilevanza alta", len(rilevanti))
    h[1].metric("Consumo elettrico dei settori",
                f"{rilevanti['GWh elettrici'].sum():,.0f} GWh".replace(",", "."))
    h[2].metric("Quota sull'industria",
                f"{rilevanti['GWh elettrici'].sum() / DOC.INDUSTRIA_TOTALE_GWH[2023] * 100:.0f}%")
    h[3].metric("Trasporto pesante",
                f"{DOC.TRASPORTO_PESANTE['quota_emissioni_trasporto_strada']}%",
                "delle emissioni del trasporto su strada")

    fig = px.bar(hta.sort_values("GWh elettrici"), x="GWh elettrici", y="Settore",
                 orientation="h", color="Rilevanza", text_auto=".0f",
                 hover_data={"motivo": False},
                 color_discrete_map={"alto": "#06B6D4", "basso": "#D1D5DB"})
    fig.update_traces(cliponaxis=False)
    fig.update_layout(height=340, yaxis_title=None, **PLOT)
    grafico(fig, DOC.F_TERNA,
            "I GWh misurano la taglia del settore, non il suo fabbisogno di idrogeno.")

    for r in hta.itertuples():
        icona = "🔵" if r.Rilevanza == "alto" else "⚪"
        st.markdown(f"{icona} **{r.Settore}** — {r.motivo}")

    st.markdown(f"🔵 **Trasporto pesante a lunga percorrenza** — {DOC.TRASPORTO_PESANTE['nota']}")

    st.info(
        f"**Il perimetro vero è più stretto di quanto si dica.** Dei "
        f"{DOC.INDUSTRIA_TOTALE_GWH[2023]:,.0f} GWh elettrici dell'industria friulana, i "
        f"settori dove l'idrogeno ha davvero senso ne rappresentano circa il "
        f"{rilevanti['GWh elettrici'].sum() / DOC.INDUSTRIA_TOTALE_GWH[2023] * 100:.0f}%: ".replace(",", ".")
        + "siderurgia, vetro e ceramica, chimica. Cartaria e prodotti in metallo lavorano "
        "a temperature che una pompa di calore industriale o una resistenza coprono meglio "
        "e a meno.\n\n"
        "Nella chimica il caso è ancora più netto: l'idrogeno **è già usato come materia "
        "prima**, prodotto da metano. Sostituirlo con idrogeno rinnovabile non richiede di "
        "cambiare processo, solo di cambiare fornitura — è il punto in cui la transizione "
        "costa meno e rende di più, e vale la pena partire da lì."
    )

    st.subheader("Quanto fotovoltaico servirebbe")
    st.caption(
        "L'idrogeno rinnovabile è elettricità rinnovabile trasformata. Qui si può vedere "
        "cosa costa, in termini di nuovo solare, produrre una data quantità di idrogeno."
    )

    cc = st.columns(3)
    with cc[0]:
        target_t = st.number_input("Idrogeno da produrre (t/anno)", 100, 100_000, 5_000, 100)
    with cc[1]:
        kwh_kg = st.slider("Consumo dell'elettrolisi (kWh/kg)", 45, 70, DOC.H2_KWH_PER_KG)
    with cc[2]:
        ore_eq = st.slider("Resa del fotovoltaico (kWh per kWp)", 700, 1300,
                           DOC.PV_ORE_EQUIVALENTI, 10)

    fabbisogno_gwh = target_t * kwh_kg / 1000
    mwp = fabbisogno_gwh * 1000 / ore_eq
    ettari = mwp * DOC.PV_ETTARI_PER_MWP
    pv_att_gwh = anno_di(prod_fer[prod_fer["voce"] == "Fotovoltaico"])["valore"].sum()
    pv_att_mw = anno_di(pot_fonte[pot_fonte["voce"] == "Fotovoltaico"])["valore"].sum()

    r = st.columns(4)
    r[0].metric("Elettricità necessaria", f"{fabbisogno_gwh:,.0f} GWh".replace(",", "."))
    r[1].metric("Nuovo fotovoltaico", f"{mwp:,.0f} MWp".replace(",", "."),
                f"{mwp / pv_att_mw * 100:.0f}% dell'installato" if pv_att_mw else None)
    r[2].metric("Superficie", f"{ettari:,.0f} ha".replace(",", "."))
    r[3].metric("Sulla produzione FV attuale",
                f"{fabbisogno_gwh / pv_att_gwh * 100:.0f}%" if pv_att_gwh else "—")

    confronto = pd.DataFrame([
        {"Voce": "Produzione FV attuale", "GWh": pv_att_gwh},
        {"Voce": "Per l'idrogeno impostato sopra", "GWh": fabbisogno_gwh},
        {"Voce": "Consumo elettrico della siderurgia",
         "GWh": DOC.CONSUMI_INDUSTRIA_MERCEOLOGICO[2023]["Siderurgia"]},
        {"Voce": "Consumo elettrico regionale", "GWh": DOC.CONSUMI_ELETTRICI_TOTALE},
    ])
    fig = px.bar(confronto.sort_values("GWh"), x="GWh", y="Voce", orientation="h",
                 text_auto=".0f", color="Voce",
                 color_discrete_sequence=["#06B6D4", "#FACC15", "#4B5563", "#9CA3AF"])
    fig.update_layout(showlegend=False, height=300, yaxis_title=None, **PLOT)
    grafico(fig, DOC.F_H2)

    # i conti sull'Hydrogen Hub, con gli stessi parametri
    hub_t = hub["produzione_ton_anno"]
    hub_gwh = hub_t * kwh_kg / 1000
    hub_mwp = hub_gwh * 1000 / ore_eq
    sider = DOC.CONSUMI_INDUSTRIA_MERCEOLOGICO[2023]["Siderurgia"]
    sider_mwp = sider * 1000 / ore_eq
    sider_ha = sider_mwp * DOC.PV_ETTARI_PER_MWP

    st.warning(
        f"Il vincolo più stringente è il primo, e si può quantificare. L'Hydrogen Hub di "
        f"Trieste produrrà **{hub_t} tonnellate l'anno**: servono circa **{hub_gwh:.0f} GWh** "
        f"di elettricità, cioè **{hub_mwp:.0f} MWp** di solare su circa "
        f"**{hub_mwp * DOC.PV_ETTARI_PER_MWP:.0f} ettari**. Il progetto ne dedica "
        f"{hub['fv_dedicato_mwp']:.2f} MWp, che coprono {hub['da_fv_ton_anno']} tonnellate su "
        f"{hub_t}: il resto viene dalla rete.\n\n"
        f"Per capire la scala: la sola siderurgia regionale consuma **{sider:,.0f} GWh** "
        f"l'anno. ".replace(",", ".")
        + f"Coprirli con nuovo fotovoltaico richiederebbe circa **{sider_mwp:,.0f} MWp** — "
        f"{sider_mwp / pv_att_mw:.1f} volte tutto il solare oggi installato in regione — su "
        f"**{sider_ha:,.0f} ettari**, cioè {sider_ha / 100:.0f} km². ".replace(",", ".")
        + "L'idrogeno qui è una scommessa industriale e infrastrutturale di lungo periodo, "
        "non una voce del bilancio energetico di oggi."
    )


def _scheda_11():
    sc = D.carica_per("scenari_settori")
    fer_sc = D.carica_per("scenari_fer_elettriche")
    ind_v = D.carica_per("scenari_industria_vettori")
    demo = D.carica_per("demografia_scenari")

    if sc.empty:
        st.info("Lancia `python -m src.etl_per` per generare gli scenari del PER.")
    else:
        st.subheader("Traiettorie di consumo al 2045")
        st.caption(
            "REF = scenario di riferimento (politiche vigenti); A = allineato al PNIEC; "
            "B = allineato a RePowerEU. I trasporti hanno un solo percorso nel PER."
        )

        cons = sc[sc["grandezza"] == "Consumi finali"]
        settore_sel = st.selectbox("Settore", sorted(cons["settore"].unique()))
        s = cons[cons["settore"] == settore_sel].sort_values("anno")
        fig = px.line(s, x="anno", y="valore", color="scenario", markers=True,
                      color_discrete_map={"Storico": "#111827", "REF": "#6B7280",
                                          "A": "#2563EB", "B": "#22C55E", "PER": "#F97316"})
        fig.update_layout(height=380, yaxis_title="ktep", xaxis_title=None, **PLOT)
        grafico(fig, DOC.F_PER)

        emis = sc[sc["grandezza"] == "Emissioni CO2"]
        if not emis.empty:
            st.subheader("Emissioni di CO₂ per settore")
            fig = px.line(emis.sort_values("anno"), x="anno", y="valore",
                          color="scenario", line_dash="settore", markers=True,
                          color_discrete_map={"Storico": "#111827", "REF": "#6B7280",
                                              "A": "#2563EB", "B": "#22C55E", "PER": "#F97316"})
            fig.update_layout(height=380, yaxis_title="kt CO₂", xaxis_title=None, **PLOT)
            grafico(fig, DOC.F_PER)

        c1, c2 = st.columns(2)
        with c1:
            st.subheader("Rinnovabili elettriche")
            f = fer_sc[fer_sc["fonte"] != "Totale FER elettriche"].sort_values("anno")
            tot_f = fer_sc[fer_sc["fonte"] == "Totale FER elettriche"].sort_values("anno")
            fig = px.bar(f, x="anno", y="valore", color="fonte",
                         color_discrete_map={"Fotovoltaico": "#FACC15", "Idroelettrico": "#2563EB",
                                             "Bioenergie": "#8B4513"})
            fig.add_scatter(x=tot_f["anno"], y=tot_f["valore"], mode="lines+markers",
                            name="Totale", line=dict(color="#111827", dash="dot"))
            fig.update_layout(height=380, yaxis_title="GWh", xaxis_title=None, **PLOT)
            grafico(fig, DOC.F_PER)

        with c2:
            st.subheader("Industria: sostituzione dei vettori")
            fig = px.area(ind_v.sort_values("anno"), x="anno", y="valore", color="vettore",
                          color_discrete_map={"Gas": "#9CA3AF", "Elettricità": "#FACC15",
                                              "FER": "#22C55E", "Calore derivato": "#F97316",
                                              "Prodotti petroliferi": "#4B5563",
                                              "Solidi": "#111827"})
            fig.update_layout(height=380, yaxis_title="ktep", xaxis_title=None, **PLOT)
            grafico(fig, DOC.F_PER)

        if not demo.empty:
            st.subheader("Il contesto: popolazione in calo, PIL in crescita")
            fig = go.Figure()
            fig.add_bar(x=demo["anno"], y=demo["popolazione"], name="Popolazione",
                        marker_color="#9CA3AF", yaxis="y")
            fig.add_scatter(x=demo["anno"], y=demo["pil_mln_eur_2015"], name="PIL (mln € 2015)",
                            mode="lines+markers", line=dict(color="#2563EB", width=3), yaxis="y2")
            fig.update_layout(
                height=340, template="plotly_white",
                yaxis=dict(title="abitanti", range=[1_050_000, 1_250_000]),
                yaxis2=dict(title="mln € 2015", overlaying="y", side="right"),
                margin=dict(t=30, b=10, l=10, r=10),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
            )
            grafico(fig, DOC.F_PER)
            st.caption(
                "Il PER assume −68.000 abitanti e +24% di PIL reale tra il 2021 e il 2045: "
                "il disaccoppiamento tra economia ed energia deve reggere su una base demografica "
                "che si assottiglia."
            )

    st.divider()
    st.subheader("Come cambiano i consumi finali: 2021 e 2045 a confronto")

    cons21 = D.carica_per("consumi_finali_2021")
    ind_v = D.carica_per("scenari_industria_vettori")
    tra_al = D.carica_per("trasporti_alimentazione")
    sc_all = D.carica_per("scenari_settori")

    if not (cons21.empty or ind_v.empty or tra_al.empty):
        st.caption(
            "A sinistra il vettore, a destra il settore. Il PER disaggrega i vettori al 2045 "
            "per industria e trasporti. Per il **civile** dà solo il totale: qui viene "
            "ripartito con le quote del 2021 e le voci sono marcate «(stima)» — è "
            "un'ipotesi di comodo, non uno scenario del piano. "
            "Scenario: Policy B per l'industria."
        )

        def sankey_consumi(coppie: list[tuple[str, str, float]], titolo: str) -> go.Figure:
            vettori = sorted({v for v, _, val in coppie if val > 0})
            settori = sorted({s for _, s, val in coppie if val > 0})
            nodi = vettori + settori
            idx_ = {n: i for i, n in enumerate(nodi)}
            palette = {"Gas": "#9CA3AF", "Combustibili gassosi": "#9CA3AF",
                       "Elettricità": "#FACC15", "Energia elettrica": "#FACC15",
                       "FER": "#22C55E", "Energie rinnovabili": "#22C55E",
                       "Calore derivato": "#F97316", "Solidi": "#111827",
                       "Combustibili solidi": "#111827", "Petrolio": "#4B5563",
                       "Prodotti petroliferi": "#4B5563", "Idrogeno": "#06B6D4"}
            colori = [palette.get(v, "#D1D5DB") for v in vettori] + ["#2563EB"] * len(settori)
            fig_ = go.Figure(go.Sankey(
                node=dict(pad=16, thickness=18, label=nodi, color=colori,
                          line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
                link=dict(source=[idx_[v] for v, s, val in coppie if val > 0],
                          target=[idx_[s] for v, s, val in coppie if val > 0],
                          value=[val for _, _, val in coppie if val > 0],
                          color=["rgba(37,99,235,0.22)"] * len([c for c in coppie if c[2] > 0]),
                          hovertemplate="%{value:.0f} ktep<extra></extra>"),
            ))
            fig_.update_layout(height=420, font_size=12, title=titolo,
                               margin=dict(t=40, b=20, l=10, r=10))
            return fig_

        c21 = [(r.vettore, r.settore, r.valore) for r in cons21.itertuples()]

        # 2045: industria e trasporti per vettore, civile aggregato
        c45 = [(r.vettore, "Industria", r.valore)
               for r in ind_v[ind_v["anno"] == 2045].itertuples()]
        agg_tra = {"ELETTRICITÁ": "Elettricità", "IDROGENO": "Idrogeno"}
        for r in tra_al[(tra_al["anno"] == 2045) & (tra_al["grandezza"] == "Consumi")].itertuples():
            nome = agg_tra.get(r.alimentazione.upper())
            if nome is None:
                nome = "Biocarburanti ed e-fuel" if any(
                    x in r.alimentazione.upper() for x in ("BIO", "E-", "HVO", "SAF")
                ) else "Prodotti petroliferi"
            c45.append((nome, "Trasporti", r.valore))
        civ45 = sc_all[(sc_all["settore"] == "Civile") & (sc_all["anno"] == 2045)
                       & (sc_all["scenario"] == "B")]["valore"].sum()
        if civ45:
            # Il PER da' il totale del civile al 2045 ma non la sua composizione.
            # Invece di inventarla, la si ripartisce con le quote del 2021 e lo si
            # dichiara: cosi' il flusso resta leggibile e l'assunzione e' esplicita.
            quote_civ = cons21[cons21["settore"] == "Civile"].set_index("vettore")["valore"]
            if quote_civ.sum() > 0:
                for vettore, quota in (quote_civ / quote_civ.sum()).items():
                    c45.append((f"{vettore} (stima)", "Civile", civ45 * quota))
            else:
                c45.append(("Civile, composizione non nota", "Civile", civ45))

        agg45: dict[tuple[str, str], float] = {}
        for v_, s_, val in c45:
            agg45[(v_, s_)] = agg45.get((v_, s_), 0) + val
        c45 = [(v_, s_, val) for (v_, s_), val in agg45.items()]

        cc1, cc2 = st.columns(2)
        with cc1:
            grafico(sankey_consumi(c21, "2021 — dato di bilancio"), DOC.F_PER)
        with cc2:
            grafico(sankey_consumi(c45, "2045 — scenario del PER"), DOC.F_PER)

        tot21 = sum(v for _, _, v in c21)
        tot45 = sum(v for _, _, v in c45)
        st.info(
            f"I consumi finali passano da **{tot21:,.0f}** a **{tot45:,.0f} ktep**, "
            f"circa {(1 - tot45 / tot21) * 100:.0f}% in meno. ".replace(",", ".")
            + "Nei trasporti compare l'idrogeno, che oggi vale zero. Nell'industria il gas "
            "arretra e crescono elettricità e rinnovabili dirette. Il confronto non è "
            "perfettamente simmetrico: il 2021 è un bilancio consuntivo, il 2045 uno scenario, "
            "e la composizione del civile al 2045 è una ripartizione a quote 2021, "
            "non una previsione del piano."
        )


def _scheda_12():
    st.subheader("Le emissioni di tutta la regione, non solo dell'elettrico")
    st.caption(f"Fonti: {DOC.FONTE_EMISSIONI}; {DOC.FONTE_INVENTARIO}.")

    em_tot_df = pd.DataFrame(DOC.EMISSIONI_TOTALI_FVG.items(), columns=["anno", "kt"])
    ultimo_anno = int(em_tot_df["anno"].max())
    ultimo_val = float(em_tot_df.loc[em_tot_df["anno"].idxmax(), "kt"])
    netto = ultimo_val * (1 - DOC.ASSORBIMENTI_FORESTALI / 100)

    e = st.columns(5)
    e[0].metric(f"Gas serra lordi ({ultimo_anno})", f"{ultimo_val / 1000:.1f} Mt CO₂eq")
    e[1].metric("Assorbimenti forestali", f"−{DOC.ASSORBIMENTI_FORESTALI}%",
                f"media italiana −{DOC.ASSORBIMENTI_ITALIA}%")
    e[2].metric("Emissioni nette", f"{netto / 1000:.1f} Mt CO₂eq")
    e[3].metric("Pro capite", f"{DOC.EMISSIONI_PRO_CAPITE_2019:.1f} t/ab")
    e[4].metric("Neutralità", DOC.TARGET_FVGREEN["anno_neutralita"], "Legge FVGreen")

    # ------------------------------------------------------------ Sankey
    st.subheader("Da dove vengono, e cosa le compensa")
    st.caption(
        "Ogni flusso è una quota del totale regionale. A sinistra le attività, al centro "
        "le quattro macrocategorie IPCC, a destra il bilancio netto dopo gli assorbimenti "
        "forestali. Inventario ARPA FVG, anno 2021."
    )

    voci, macro = [], []
    for k, v in DOC.EMISSIONI_ENERGIA.items():
        voci.append((k, "Energia", v))
    voci.append(("Agricoltura e uso del suolo", "AFOLU (agricoltura e uso del suolo)",
                 DOC.EMISSIONI_MACRO["AFOLU (agricoltura e uso del suolo)"]))
    voci.append(("Processi industriali", "IPPU (processi industriali)",
                 DOC.EMISSIONI_MACRO["IPPU (processi industriali)"]))
    voci.append(("Trattamento dei rifiuti", "Rifiuti", DOC.EMISSIONI_MACRO["Rifiuti"]))

    attivita = [v[0] for v in voci]
    macrocat = list(DOC.EMISSIONI_MACRO)
    nodi_e = attivita + macrocat + ["Emissioni lorde", "Assorbimenti forestali",
                                    "Emissioni nette in atmosfera"]
    ie = {n: i for i, n in enumerate(nodi_e)}
    palette = {"Trasporti": "#EF4444", "Riscaldamento": "#F97316",
               "Industrie manifatturiere": "#4B5563", "Industrie energetiche": "#FACC15",
               "Emissioni fuggitive": "#9CA3AF", "Agricoltura e uso del suolo": "#22C55E",
               "Processi industriali": "#A855F7", "Trattamento dei rifiuti": "#78716C"}
    colori_e = [palette.get(a, "#9CA3AF") for a in attivita] + \
               ["#DC2626", "#16A34A", "#7C3AED", "#78716C"][:len(macrocat)] + \
               ["#111827", "#16A34A", "#DC2626"]

    se, te, ve, ce = [], [], [], []

    def le(a, b, v, colore):
        if v > 0:
            se.append(ie[a]); te.append(ie[b]); ve.append(float(v)); ce.append(colore)

    for nome, mcat, quota in voci:
        le(nome, mcat, quota, "rgba(220,38,38,0.22)")
    for m in macrocat:
        le(m, "Emissioni lorde", DOC.EMISSIONI_MACRO[m], "rgba(17,24,39,0.20)")
    le("Emissioni lorde", "Assorbimenti forestali", DOC.ASSORBIMENTI_FORESTALI,
       "rgba(22,163,74,0.35)")
    le("Emissioni lorde", "Emissioni nette in atmosfera",
       100 - DOC.ASSORBIMENTI_FORESTALI, "rgba(220,38,38,0.28)")

    fig = go.Figure(go.Sankey(
        node=dict(pad=16, thickness=18, label=nodi_e, color=colori_e,
                  line=dict(color="rgba(0,0,0,0.15)", width=0.5)),
        link=dict(source=se, target=te, value=ve, color=ce,
                  hovertemplate="%{value:.1f}% del totale<extra></extra>"),
    ))
    fig.update_layout(height=520, font_size=12, margin=dict(t=20, b=20, l=10, r=10))
    grafico(fig, DOC.FONTE_INVENTARIO,
            "Le quote della macrocategoria Energia sommano a 84,5% e non a 86% per arrotondamenti.")

    # ------------------------------------------------- dettaglio e trasporti
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**I quattro ambiti dell'Energia si equivalgono quasi**")
        en = pd.DataFrame(DOC.EMISSIONI_ENERGIA.items(), columns=["Ambito", "% del totale"])
        fig = px.bar(en.sort_values("% del totale"), x="% del totale", y="Ambito",
                     orientation="h", text_auto=".1f", color="Ambito",
                     color_discrete_map=palette)
        fig.update_traces(cliponaxis=False)
        fig.update_layout(showlegend=False, height=320, yaxis_title=None, **PLOT)
        grafico(fig, DOC.FONTE_INVENTARIO)

    with c2:
        st.markdown("**Dentro il trasporto su strada comandano le automobili**")
        tr = pd.DataFrame(DOC.TRASPORTO_STRADA.items(), columns=["Mezzo", "quota"])
        tr["% del totale regionale"] = tr["quota"] * DOC.TRASPORTO_STRADA_QUOTA / 100
        fig = px.pie(tr, values="quota", names="Mezzo", hole=0.5,
                     color_discrete_sequence=["#EF4444", "#F97316", "#FBBF24", "#FCD34D"])
        fig.update_traces(textinfo="percent")
        fig.update_layout(height=320, **PLOT)
        grafico(fig, DOC.FONTE_INVENTARIO,
                f"Il trasporto su strada vale il {DOC.TRASPORTO_STRADA_QUOTA}% del totale regionale.")

    st.info(
        f"**Le automobili private da sole fanno circa il "
        f"{DOC.TRASPORTO_STRADA['Autovetture'] * DOC.TRASPORTO_STRADA_QUOTA / 100:.0f}% "
        "delle emissioni regionali** — più del settore elettrico intero. È il numero che "
        "spiega perché la decarbonizzazione del FVG non si gioca sulle centrali: quelle "
        "pesano per il 17,8%, e stanno già calando da sole con la chiusura di Monfalcone. "
        "Si gioca su come ci si muove e su come si scaldano le case."
    )

    # ------------------------------------------------------------ serie storica
    st.subheader("La serie storica, con le sue cautele")
    fig = px.bar(em_tot_df, x="anno", y="kt", text_auto=".0f",
                 color_discrete_sequence=["#6B7280"])
    fig.add_scatter(x=[2045], y=[0], mode="markers+text", text=["neutralità 2045"],
                    textposition="top center", marker=dict(size=14, color="#22C55E"),
                    name="Obiettivo FVGreen")
    fig.update_traces(cliponaxis=False)
    fig.update_layout(height=360, yaxis_title="kt CO₂eq", xaxis_title=None, **PLOT)
    grafico(fig, DOC.FONTE_EMISSIONI)

    st.warning(
        "ISPRA avverte che la metodologia è cambiata nel tempo: i confronti fra anni "
        f"lontani sono indicativi. Il dato solido è l'ordine di grandezza — "
        f"**{ultimo_val / 1000:.1f} Mt CO₂eq lordi** contro gli "
        f"**{em_tot:.2f} Mt** del solo settore elettrico nel {anno}. "
        f"Gli assorbimenti forestali ne compensano circa un quarto, contro un decimo della "
        "media nazionale: è l'effetto dei 327.000 ettari di bosco. Ma ARPA avverte che gli "
        "alberi non bastano, perché la loro azione può ridursi di colpo per incendi o "
        "parassitosi."
    )

    # ------------------------------------------------ consumi finali per settore
    st.subheader("Perché il FVG emette così: la struttura dei consumi")
    conf = pd.DataFrame([
        {"Settore": k, "Friuli-Venezia Giulia": v[0], "Italia": v[1]}
        for k, v in DOC.QUOTE_SETTORE_CONFRONTO.items()
    ]).melt(id_vars="Settore", var_name="Area", value_name="% dei consumi finali")
    fig = px.bar(conf, x="Settore", y="% dei consumi finali", color="Area", barmode="group",
                 text_auto=".1f",
                 color_discrete_map={"Friuli-Venezia Giulia": "#2563EB", "Italia": "#9CA3AF"})
    fig.update_traces(cliponaxis=False)
    fig.update_layout(height=340, xaxis_title=None, **PLOT)
    grafico(fig, "EUROSTAT ed ENEA, ripresi nel Piano Energetico Regionale FVG")

    st.caption(
        "L'industria assorbe il **40%** dei consumi finali contro il 22% italiano, i "
        "trasporti il **19,4%** contro il 31,2%. Il FVG non emette poco nei trasporti: "
        "emette molto nell'industria, e questo comprime la quota relativa degli altri settori."
    )


def _scheda_13():
    st.subheader("Il clima che cambia il sistema energetico")
    st.caption(f"Fonte: {DOC.FONTE_CLIMA}.")

    s = DOC.CLIMA_SINTESI
    k = st.columns(4)
    k[0].metric(f"Anno {s['anno_ultimo']}", s["posizione_classifica"].replace("terzo", "3°").title(),
                help=f"Superato solo dal {s['superato_da']}.")
    k[1].metric("Rispetto al 1991–2020", f"+{s['anomalia_vs_1991_2020']} °C")
    k[2].metric("Rispetto al Novecento", f"+{s['anomalia_vs_novecento']} °C")
    k[3].metric("Rispetto al preindustriale", f"+{s['anomalia_vs_preindustriale']} °C",
                help="Periodo 1850-1900, serie di Udine.")

    st.warning(
        f"In FVG la soglia di **+{s['soglia_globale_superata']} °C** sul preindustriale è già stata "
        f"superata più volte, e nel 2025 l'anomalia ha toccato **+{s['anomalia_vs_preindustriale']} °C**. "
        "A livello globale quella soglia è stata superata per la prima volta nel 2024. "
        "La regione si scalda più in fretta della media perché sta a cavallo di due hot spot: "
        "il Mediterraneo e le Alpi."
    )

    st.subheader("Anomalie termiche mensili a Udine")
    st.caption("Scostamento delle temperature medie mensili rispetto alla serie dal 1901.")
    an = pd.DataFrame([
        {"mese": DOC.MESI[i], "ordine": i, "anno": str(a), "anomalia": v}
        for a, vals in DOC.ANOMALIE_MENSILI.items() for i, v in enumerate(vals)
    ]).sort_values("ordine")
    fig = px.bar(an, x="mese", y="anomalia", color="anno", barmode="group",
                 color_discrete_map={"2024": "#F97316", "2025": "#EF4444"})
    fig.add_hline(y=0, line_color="#111827", line_width=1)
    fig.update_layout(height=360, yaxis_title="°C rispetto alla media", xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_ARPA)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Il 2024 in cifre**")
        d24 = DOC.CLIMA_2024
        st.markdown(
            f"- **{d24['giorni_caldi']} giorni caldi** in pianura (massima oltre 30 °C), "
            f"contro i {d24['giorni_caldi_media']} della media 1991–2020: quasi un mese in più.\n"
            f"- Mare a Trieste **+{d24['mare_anomalia']} °C** rispetto al 1995–2023.\n"
            f"- Piogge annue **+{d24['piogge_vs_media']}%** sopra la norma…\n"
            f"- …ma solo **{d24['piogge_estive_mm']} mm** d'estate."
        )
        st.caption(
            f"Le piogge estive calano di circa {abs(DOC.PIOGGE_ESTIVE_TREND)} mm ogni decennio "
            "dal 1961: il trend è statisticamente significativo. Più acqua in totale, "
            "meno acqua quando serve ai fiumi e all'agricoltura."
        )

    with c2:
        st.markdown("**Perdita di volume dei ghiacciai**")
        cr = pd.DataFrame(DOC.CRIOSFERA.items(), columns=["Corpo glaciale", "Variazione %"])
        fig = px.bar(cr, x="Variazione %", y="Corpo glaciale", orientation="h", text_auto=".0f",
                     color_discrete_sequence=["#60A5FA"])
        fig.update_layout(height=260, yaxis_title=None, xaxis_title="% di volume perso", **PLOT)
        grafico(fig, DOC.F_ARPA)
        st.caption(
            "Perdite misurate su circa un secolo. Il Canin è di fatto scomparso come ghiacciaio; "
            "il Montasio occidentale resiste grazie all'esposizione a nord e agli apporti di valanga."
        )

    st.divider()
    st.subheader("Perché tutto questo riguarda l'energia")
    st.markdown(
        "- **Idroelettrico**: la produzione regionale oscilla di un fattore due tra anni "
        "piovosi e anni secchi. Estati più asciutte spostano la produzione fuori dai mesi "
        "di maggior consumo per il condizionamento.\n"
        "- **Domanda**: più giorni sopra i 30 °C significa più raffrescamento estivo, cioè "
        "un picco di domanda elettrica che si sposta da inverno a estate.\n"
        "- **Termoelettrico**: acqua di raffreddamento più calda e più scarsa riduce il "
        "rendimento degli impianti proprio quando servono di più.\n"
        "- **Reti**: eventi intensi e concentrati mettono sotto stress le linee aeree, "
        "in una regione che ha 13.400 km di bassa tensione da mantenere."
    )

    # ------------------------------------------------------- scenari futuri
    st.divider()
    st.subheader("Cosa succede se: gli scenari climatici")
    st.caption(
        "Gli scenari RCP descrivono traiettorie di emissioni globali fino al 2100. "
        "Non sono previsioni: sono ipotesi su quanto il mondo deciderà di ridurre."
    )
    for nome, descr in DOC.SCENARI_RCP.items():
        st.markdown(f"- **{nome}** — {descr}")

    st.markdown("**L'effetto sull'energia si misura in gradi giorno**")
    st.caption(
        "I gradi giorno di riscaldamento (HDD) dicono quanta energia serve per scaldare, "
        "quelli di raffrescamento (CDD) quanta per raffrescare. Riferimento 1976-2005, "
        "proiezioni della piattaforma CLiNE di ARPA FVG."
    )

    gg = DOC.GRADI_GIORNO
    g = st.columns(4)
    g[0].metric("Riscaldamento in pianura, oggi",
                f"{gg['riscaldamento_pianura_oggi']:,} HDD".replace(",", "."))
    g[1].metric("A fine secolo (RCP8.5)",
                f"{gg['riscaldamento_pianura_2100_rcp85']:,} HDD".replace(",", "."),
                f"{gg['riscaldamento_pianura_2100_rcp85'] - gg['riscaldamento_pianura_oggi']:+,}"
                .replace(",", "."))
    g[2].metric("Raffrescamento a Fagagna", f"+{gg['cdd_fagagna_rcp85_2071_2100']} CDD",
                "anomalia 2071-2100, RCP8.5")
    g[3].metric("Riscaldamento a Malborghetto", f"{gg['hdd_malborghetto_rcp85_2071_2100']} HDD",
                "anomalia 2071-2100, RCP8.5")

    bilancio = pd.DataFrame([
        {"Voce": "Riscaldamento invernale (HDD)",
         "Variazione": gg["riscaldamento_pianura_2100_rcp85"] - gg["riscaldamento_pianura_oggi"]},
        {"Voce": "Raffrescamento estivo (CDD)", "Variazione": gg["cdd_fagagna_rcp85_2071_2100"]},
    ])
    fig = px.bar(bilancio, x="Variazione", y="Voce", orientation="h", text_auto="+.0f",
                 color="Variazione", color_continuous_scale=["#2563EB", "#F3F4F6", "#DC2626"],
                 color_continuous_midpoint=0)
    fig.add_vline(x=0, line_color="#111827")
    fig.update_traces(cliponaxis=False)
    fig.update_layout(height=240, yaxis_title=None, coloraxis_showscale=False,
                      xaxis_title="gradi giorno, anomalia a fine secolo (RCP8.5)", **PLOT)
    grafico(fig, "ARPA FVG, piattaforma CLiNE",
            "Le due grandezze sono misurate in punti diversi e non sono direttamente sommabili.")

    st.info(
        f"**Si scalderà molto meno e si raffrescherà molto di più.** In pianura i gradi "
        f"giorno di riscaldamento scendono da circa {gg['riscaldamento_pianura_oggi']:,} a "
        f"{gg['riscaldamento_pianura_2100_rcp85']:,} a fine secolo nello scenario peggiore. ".replace(",", ".")
        + "Sembra un risparmio, ed è un risparmio di **gas**. Ma l'aumento del raffrescamento "
        "è un aumento di **elettricità**, concentrato nelle ore più calde del pomeriggio "
        "estivo: proprio quando la rete è già sotto sforzo e il fotovoltaico comincia a "
        "calare. Il saldo energetico può migliorare mentre il saldo **di potenza** peggiora.\n\n"
        f"Sempre nello scenario RCP8.5, buona parte della pianura passerebbe dalla zona "
        f"climatica **{DOC.ZONA_CLIMATICA['oggi'].split('—')[0].strip()}** alla "
        f"**{DOC.ZONA_CLIMATICA['rcp85_fine_secolo'].split('—')[0].strip()}**, con due ore "
        "in meno di riscaldamento consentito al giorno e due settimane in meno di stagione."
    )

    # ------------------------------------------------------- eventi estremi
    st.divider()
    st.subheader("Il 2025, evento per evento")
    st.caption(
        "Cronologia dei fenomeni meteorologici rilevanti registrati da ARPA FVG. "
        "La colonna di destra indica la gravità relativa, non un indice ufficiale."
    )

    ev = pd.DataFrame(DOC.EVENTI_2025, columns=["quando", "cosa", "dettaglio", "gravita"])
    fig = px.bar(ev, x="gravita", y="quando", orientation="h", color="gravita",
                 color_continuous_scale=["#FCD34D", "#F97316", "#DC2626"],
                 hover_name="cosa", text="cosa")
    fig.update_traces(textposition="inside", insidetextanchor="start", cliponaxis=False)
    fig.update_yaxes(categoryorder="array", categoryarray=list(ev["quando"])[::-1])
    fig.update_layout(height=400, yaxis_title=None, xaxis_title="gravità relativa",
                      coloraxis_showscale=False, **PLOT)
    grafico(fig, DOC.FONTE_CLIMA)

    for r in ev.itertuples():
        if r.dettaglio:
            with st.expander(f"{r.quando} — {r.cosa}"):
                st.markdown(r.dettaglio)

    st.error(
        "**L'evento del 16-17 novembre 2025 merita di essere ricordato.** Un sistema "
        "convettivo autorigenerante è rimasto fermo quasi dodici ore sul bacino dello Judrio, "
        "scaricando oltre **200 mm di pioggia**. Il torrente ha esondato allagando Versa con "
        "uno-due metri d'acqua e fango; a Brazzano di Cormòns una collina è franata sul centro "
        "abitato, **due vittime** e tre case distrutte. I modelli non l'avevano previsto: "
        "attendevano piogge orografiche sulle Prealpi, non in pianura. "
        "Un evento simile non accadeva dal 29 agosto 2003, l'alluvione della Val Canale."
    )

    # ------------------------------------------- il confronto con le altre regioni
    st.divider()
    st.subheader("Come sta il FVG rispetto al resto d'Italia")
    st.caption(f"Fonte: {DOC.FONTE_CIRO}. Ventisei indicatori, qui i più rilevanti.")

    st.error(
        f"**Nel 2024 il Friuli-Venezia Giulia è stata la "
        f"{DOC.CIRO_SINTESI['eventi_estremi_2024']}.** "
        "Non è un'impressione costruita sui titoli dei giornali: è un conteggio, e mette "
        "in fila gli otto episodi della cronologia qui sopra. Una regione piccola, "
        "stretta fra mare e Alpi, dove i sistemi convettivi trovano tutto quello che "
        "serve per innescarsi."
    )

    ind = pd.DataFrame(DOC.CIRO_INDICATORI,
                       columns=["Ambito", "Indicatore", "FVG", "Italia", "um",
                                "alto_e_meglio", "nota"])
    conf = ind.dropna(subset=["Italia"]).copy()
    lungo = conf.melt(id_vars=["Indicatore", "alto_e_meglio"],
                      value_vars=["FVG", "Italia"], var_name="Area", value_name="Valore")
    fig = px.bar(lungo, x="Valore", y="Indicatore", color="Area", orientation="h",
                 barmode="group", text_auto=".1f",
                 color_discrete_map={"FVG": "#2563EB", "Italia": "#9CA3AF"})
    fig.update_traces(cliponaxis=False)
    fig.update_layout(height=380, yaxis_title=None, xaxis_title="%", **PLOT)
    grafico(fig, DOC.FONTE_CIRO)

    solo = ind[ind["Italia"].isna()][["Ambito", "Indicatore", "FVG", "um", "nota"]]
    solo.columns = ["Ambito", "Indicatore", "Valore", "Unità", "Nota"]
    st.markdown("**Indicatori senza confronto diretto**")
    st.dataframe(solo, hide_index=True, width="stretch")
    st.caption(f"Fonte: {DOC.FONTE_CIRO}.")

    st.info(
        "**Il quadro è a due facce.** Sulle rinnovabili elettriche il FVG va bene: è la "
        "**seconda regione d'Italia** per conseguimento del target 2030 (46% contro una "
        f"media del 31%), ha {DOC.CIRO_SINTESI['comunita_energetiche_2024']} comunità "
        "energetiche attive e una quota rinnovabile sopra la media. "
        "Sulla vulnerabilità va male: prima per eventi estremi, consumo di suolo all'8% "
        "sopra la media, perdite della rete idrica al 42%.\n\n"
        "In mezzo c'è la struttura: **gas al 48% del mix** e consumi finali pro capite "
        "fra i più alti d'Italia, per via del riscaldamento e dell'industria pesante. "
        "Il FVG sta costruendo bene l'offerta rinnovabile mentre porta con sé una domanda "
        "molto energivora — ed è la seconda parte a decidere se gli obiettivi si raggiungono."
    )

    # --------------------------------------------- catena di impatto energia
    st.divider()
    st.subheader("Come il clima colpisce il sistema energetico")
    st.caption(
        "Catena di impatto per produzione, trasporto e consumo di energia in Europa "
        "(EUCRA 2023, ripresa da ARPA FVG)."
    )
    cat = pd.DataFrame(DOC.CATENA_IMPATTO, columns=["Sottosistema", "Rischio", "Meccanismo"])
    for sotto in cat["Sottosistema"].unique():
        st.markdown(f"**{sotto}**")
        for r in cat[cat["Sottosistema"] == sotto].itertuples():
            st.markdown(f"- *{r.Rischio}* — {r.Meccanismo}")

    st.caption(
        "Fonte: EUCRA 2023 (Agenzia europea dell'ambiente), rielaborazione ARPA FVG. "
        "Il punto che tiene insieme tutta la catena è che i rischi si presentano insieme: "
        "l'ondata di calore riduce l'idroelettrico, abbassa il rendimento del termoelettrico, "
        "taglia la portata delle linee e alza la domanda, tutto nello stesso pomeriggio."
    )


def _scheda_14():
    st.subheader("Sostituzione tra fonti (grafico di Marchetti)")
    st.caption("Asse y: log₁₀(f / (1−f)), con f = quota della fonte. Una retta = sostituzione a ritmo costante.")

    m = prod_fonte.merge(tot_y.rename("tot"), on="anno")
    m = m[(m["tot"] > 0) & (m["valore"] > 0)]
    m["f"] = np.clip(m["valore"] / m["tot"], 1e-4, 1 - 1e-4)
    m["marchetti"] = np.log10(m["f"] / (1 - m["f"]))
    fig = px.line(m.sort_values("anno"), x="anno", y="marchetti", color="voce", markers=True,
                  color_discrete_map=D.mappa_colori(m["voce"]))
    fig.update_layout(height=400, yaxis_title="log(f / 1−f)", xaxis_title=None, **PLOT)
    grafico(fig, DOC.F_ELAB)

    st.subheader("Traiettoria del mix elettrico (diagramma ternario)")
    st.caption("Ogni punto è un anno. Le tre componenti sommano a 100% della produzione lorda.")

    piv = prod_fonte.pivot_table(index="anno", columns="voce", values="valore", aggfunc="sum").fillna(0)
    fer_piv = prod_fer.pivot_table(index="anno", columns="voce", values="valore", aggfunc="sum").fillna(0)
    bio = fer_piv.get("Bioenergie", pd.Series(0, index=piv.index)).reindex(piv.index).fillna(0)

    t = pd.DataFrame(index=piv.index)
    t["Rinnovabili variabili"] = piv.get("Fotovoltaico", 0) + piv.get("Eolico", 0)
    t["Idroelettrico"] = piv.get("Idrico", 0)
    t["Termoelettrico"] = piv.get("Termoelettrico", 0)
    tot_t = t.sum(axis=1)
    t = (t.div(tot_t, axis=0) * 100).dropna().reset_index()

    fig = px.scatter_ternary(t, a="Termoelettrico", b="Rinnovabili variabili", c="Idroelettrico",
                             hover_name="anno", color="anno", color_continuous_scale="Viridis")
    fig.update_traces(mode="lines+markers", line=dict(color="#22C55E", width=1.5), marker=dict(size=9))
    fig.update_layout(height=520, margin=dict(t=40, b=20))
    grafico(fig, DOC.F_ELAB)

    st.divider()
    st.subheader("Ipotesi di copertura: quanto costa e quanto suolo serve")
    st.caption(
        "Un modello parametrico, non una previsione. Si sceglie quanta domanda elettrica "
        "coprire con produzione regionale e con quale mix, e si vede cosa comporta in "
        "investimento, costo dell'energia e suolo occupato. Tutti i parametri sono modificabili."
    )

    dom_att = DOC.CONSUMI_ELETTRICI_TOTALE
    prod_att = anno_di(prod_fonte)["valore"].sum()
    fer_att = anno_di(prod_fer)["valore"].sum()

    q = st.columns(4)
    q[0].metric("Domanda elettrica attuale", f"{dom_att:,.0f} GWh".replace(",", "."))
    q[1].metric("Produzione regionale", f"{prod_att:,.0f} GWh".replace(",", "."),
                f"{prod_att / dom_att * 100:.0f}% della domanda")
    q[2].metric("di cui rinnovabile", f"{fer_att:,.0f} GWh".replace(",", "."),
                f"{fer_att / dom_att * 100:.0f}% della domanda")
    q[3].metric("Importato", f"{max(0, dom_att - prod_att):,.0f} GWh".replace(",", "."))

    st.markdown("**1. Quanta domanda coprire con rinnovabili regionali**")
    cc = st.columns(2)
    with cc[0]:
        domanda_2045 = st.slider("Domanda elettrica al 2045 (GWh)", 8000, 20000,
                                 int(dom_att * 1.35), 500,
                                 help="L'elettrificazione di trasporti e calore fa crescere "
                                      "la domanda anche se i consumi finali totali calano.")
    with cc[1]:
        copertura = st.slider("Quota da coprire con nuove rinnovabili regionali (%)",
                              0, 100, 60, 5)

    da_produrre = domanda_2045 * copertura / 100
    nuovo_gwh = max(0.0, da_produrre - fer_att)

    st.markdown("**2. Con quale mix**")
    mx = st.columns(4)
    tecnologie = list(DOC.CAPEX_DEFAULT)
    quote = {}
    default_quote = [50, 25, 15, 10]
    for col, tec, dq in zip(mx, tecnologie, default_quote):
        with col:
            quote[tec] = st.slider(tec.replace("Fotovoltaico ", "FV "), 0, 100, dq, 5,
                                   key=f"q_{tec}")
    somma_q = sum(quote.values()) or 1

    with st.expander("Parametri economici e tecnici"):
        pc = st.columns(3)
        with pc[0]:
            wacc = st.slider("Costo del capitale (%)", 2.0, 12.0, 6.0, 0.5) / 100
        with pc[1]:
            vita = st.slider("Vita utile (anni)", 15, 35, 25)
        with pc[2]:
            prezzo_rif = st.number_input("Prezzo di riferimento (€/MWh)", 40, 250,
                                         int(DOC.PUN_MEDIO_2025))
        capex = {}
        cx = st.columns(4)
        for col, tec in zip(cx, tecnologie):
            with col:
                capex[tec] = st.number_input(f"CAPEX {tec.split()[-1]} (€/kW)", 300, 3000,
                                             DOC.CAPEX_DEFAULT[tec], 50, key=f"c_{tec}")

    def annualita(w: float, n: int) -> float:
        return w / (1 - (1 + w) ** -n) if w else 1 / n

    righe = []
    for tec in tecnologie:
        quota = quote[tec] / somma_q
        gwh = nuovo_gwh * quota
        ore = DOC.ORE_EQUIVALENTI[tec]
        mw = gwh * 1000 / ore if ore else 0
        capex_tot = mw * 1000 * capex[tec] / 1e6            # milioni di €
        opex_anno = capex_tot * DOC.OPEX_QUOTA[tec] / 100
        lcoe = ((capex_tot * annualita(wacc, vita) + opex_anno) * 1e6 / (gwh * 1000)
                if gwh else 0)
        righe.append({
            "Tecnologia": tec, "GWh/anno": gwh, "MW": mw,
            "Investimento (mln €)": capex_tot, "LCOE (€/MWh)": lcoe,
            "Suolo (ha)": mw * DOC.SUOLO_HA_MW[tec],
        })
    mix = pd.DataFrame(righe)
    mix = mix[mix["GWh/anno"] > 0]

    if not mix.empty:
        inv_tot = mix["Investimento (mln €)"].sum()
        suolo_tot = mix["Suolo (ha)"].sum()
        lcoe_medio = ((mix["LCOE (€/MWh)"] * mix["GWh/anno"]).sum() / mix["GWh/anno"].sum())
        import_res = max(0.0, domanda_2045 - da_produrre - (prod_att - fer_att))

        r = st.columns(4)
        r[0].metric("Nuova potenza", f"{mix['MW'].sum():,.0f} MW".replace(",", "."))
        r[1].metric("Investimento", f"{inv_tot / 1000:,.1f} mld €".replace(",", "."))
        r[2].metric("Costo medio dell'energia", f"{lcoe_medio:.0f} €/MWh",
                    f"{lcoe_medio - prezzo_rif:+.0f} vs riferimento")
        r[3].metric("Suolo occupato", f"{suolo_tot:,.0f} ha".replace(",", "."),
                    f"{suolo_tot / 100:.0f} km²")

        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(mix, x="Tecnologia", y="GWh/anno", color="Tecnologia",
                         text_auto=".0f",
                         color_discrete_sequence=["#FACC15", "#F59E0B", "#FBBF24", "#22C55E"])
            fig.update_layout(showlegend=False, height=320, xaxis_title=None,
                              title="Produzione per tecnologia", **PLOT)
            fig.update_xaxes(tickangle=-20)
            grafico(fig, DOC.F_ELAB)
        with c2:
            fig = px.bar(mix, x="Tecnologia", y="LCOE (€/MWh)", color="Tecnologia",
                         text_auto=".0f",
                         color_discrete_sequence=["#FACC15", "#F59E0B", "#FBBF24", "#22C55E"])
            fig.add_hline(y=prezzo_rif, line_dash="dash", line_color="#111827",
                          annotation_text=f"prezzo di riferimento {prezzo_rif} €/MWh",
                          annotation_position="top left")
            fig.update_layout(showlegend=False, height=320, xaxis_title=None,
                              title="Costo dell'energia per tecnologia", **PLOT)
            fig.update_xaxes(tickangle=-20)
            grafico(fig, DOC.F_ELAB)

        st.markdown("**Il conto del suolo**")
        suolo = mix[["Tecnologia", "Suolo (ha)", "MW"]].copy()
        suolo["Su superfici già costruite"] = suolo["Suolo (ha)"] == 0
        aree_fv_t = D.carica_per("aree_disponibili_fv")
        fig = px.bar(suolo, x="Suolo (ha)", y="Tecnologia", orientation="h", text_auto=".0f",
                     color="Su superfici già costruite",
                     color_discrete_map={True: "#22C55E", False: "#F97316"})
        fig.update_layout(height=280, yaxis_title=None, **PLOT)
        grafico(fig, DOC.F_RSE)

        if not aree_fv_t.empty:
            agri_disp = aree_fv_t["area2netta"].sum() * 100      # km² -> ha
            costruito = aree_fv_t["areacnkm2"].sum() * 100
            st.caption(
                f"Il suolo richiesto è **{suolo_tot:,.0f} ha**, il ".replace(",", ".")
                + f"**{suolo_tot / agri_disp * 100:.1f}%** delle aree agricole disponibili al "
                f"netto dei vincoli ({agri_disp:,.0f} ha) e il ".replace(",", ".")
                + f"**{suolo_tot / costruito * 100:.1f}%** della superficie già impermeabilizzata "
                f"({costruito:,.0f} ha). ".replace(",", ".")
                + "Spostare quote verso capannoni e tetti azzera il consumo di suolo ma alza "
                "il costo dell'energia: è il vero scambio di questa scheda."
            )

        st.dataframe(mix.round(1), hide_index=True, width="stretch")

        st.info(
            f"Con questo mix il FVG coprirebbe il **{copertura}%** di una domanda di "
            f"{domanda_2045:,.0f} GWh, importando ancora circa ".replace(",", ".")
            + f"**{import_res:,.0f} GWh**. ".replace(",", ".")
            + f"L'investimento è di **{inv_tot / 1000:.1f} miliardi**, spalmato su vent'anni "
            f"fa circa {inv_tot / 20:.0f} milioni l'anno. "
            f"Il costo medio dell'energia prodotta è **{lcoe_medio:.0f} €/MWh** contro un "
            f"prezzo di riferimento di {prezzo_rif}: "
            + ("**sotto** il mercato, quindi l'autoproduzione conviene anche senza incentivo."
               if lcoe_medio < prezzo_rif else
               "**sopra** il mercato, quindi servirebbe un contratto per differenza o un "
               "incentivo per colmare il divario.")
        )

    st.warning(
        "**Cosa questo modello non fa.** Non considera l'intermittenza: coprire il 60% della "
        "domanda su base annua non significa coprirla ora per ora, e la quota di accumulo "
        "necessaria non è nel conto. Non include i costi di rete, che nel FVG sono il collo "
        "di bottiglia vero. Non tiene conto della curva di apprendimento sui costi né "
        "dell'inflazione. E il LCOE non è il prezzo pagato: un contratto per differenza "
        "sposta il rischio, non il costo. Serve a confrontare ordini di grandezza tra "
        "opzioni, non a valutare un investimento."
    )

    st.divider()
    st.subheader("La casella vuota: l'eolico")
    st.caption(
        "In FVG risultano 4 impianti eolici con potenza non rilevabile nelle statistiche "
        "Terna, e produzione nulla su tutta la serie. È l'unica regione del Nord con questa "
        "situazione, e pesa sul resto del ragionamento."
    )

    e1, e2, e3, e4 = st.columns(4)
    e1.metric("Impianti eolici in FVG", DOC.IMPIANTI_EOLICI_FVG, "potenza non rilevabile")
    e2.metric("Produzione eolica", "0 GWh")
    e3.metric("Deficit elettrico 2024", f"{DOC.DEFICIT_ELETTRICO_2024:,.0f} GWh".replace(",", "."),
              f"{DOC.DEFICIT_ELETTRICO_2024 / DOC.RICHIESTA_ELETTRICA_2024 * 100:.0f}% della richiesta")
    e4.metric("Richiesta 2024", f"{DOC.RICHIESTA_ELETTRICA_2024:,.0f} GWh".replace(",", "."))

    st.markdown("**Perché l'eolico cambierebbe il conto: il suolo**")
    energia_rif = st.slider("Energia annua da produrre (GWh)", 50, 2000, 500, 50,
                            key="suolo_eol")
    mw_eol = energia_rif * 1000 / DOC.ORE_EQUIVALENTI["Eolico onshore"]
    mw_pv = energia_rif * 1000 / DOC.ORE_EQUIVALENTI["Fotovoltaico utility scale"]
    ha_eol = mw_eol * DOC.SUOLO_HA_MW["Eolico onshore"]
    ha_eol_serv = mw_eol * DOC.EOLICO_SERVITU_HA_MW
    ha_pv = mw_pv * DOC.SUOLO_HA_MW["Fotovoltaico utility scale"]

    conf_suolo = pd.DataFrame([
        {"Opzione": "Eolico, suolo sottratto (plinti e piazzole)", "Ettari": ha_eol},
        {"Opzione": "Eolico, servitù di sorvolo", "Ettari": ha_eol_serv},
        {"Opzione": "Fotovoltaico a terra", "Ettari": ha_pv},
    ])
    fig = px.bar(conf_suolo, x="Ettari", y="Opzione", orientation="h", text_auto=".1f",
                 color="Opzione",
                 color_discrete_sequence=["#22C55E", "#86EFAC", "#FACC15"])
    fig.update_layout(showlegend=False, height=260, yaxis_title=None, **PLOT)
    grafico(fig, DOC.F_ELAB)

    s1, s2, s3 = st.columns(3)
    s1.metric("Potenza eolica", f"{mw_eol:,.0f} MW".replace(",", "."))
    s2.metric("Potenza fotovoltaica equivalente", f"{mw_pv:,.0f} MW".replace(",", "."))
    s3.metric("Suolo risparmiato", f"{ha_pv / max(ha_eol, 0.01):.0f}×",
              "a parità di energia")

    st.info(
        "A parità di energia prodotta, l'eolico sottrae al suolo una frazione minima di "
        "quello che serve al fotovoltaico a terra: contano solo plinti e piazzole, mentre "
        "la servitù di sorvolo resta terreno coltivabile. Ma il vantaggio più rilevante è un "
        "altro: **l'eolico produce d'inverno e di notte**, quando il fotovoltaico non c'è. "
        "In una regione che importa il 34% dell'elettricità e ha il picco di domanda nelle "
        "ore serali d'inverno, quella complementarità vale più del risparmio di suolo.\n\n"
        "Il costo è la visibilità: gli aerogeneratori si vedono da lontano, e i siti ventosi "
        "in FVG sono sui crinali alpini e prealpini, cioè in aree di pregio paesaggistico."
    )

    st.warning(
        "**Qui manca il dato decisivo e non l'ho voluto inventare.** Per dire se in FVG "
        "l'eolico sia possibile servono le mappe di ventosità e di producibilità specifica "
        "dell'**Atlante Eolico RSE** (atlanteeolico.rse-web.it), alle quote di 75, 100 e 125 m, "
        "incrociate con i vincoli. È lo stesso portale da cui provengono gli altri dati RSE "
        "già in questa app. Le 2.200 ore equivalenti usate qui sopra sono un valore di "
        "letteratura per un sito di crinale a 5,5 m/s su 100 metri: plausibile per le Prealpi "
        "Giulie e Carniche, ma da verificare sito per sito, non un dato regionale misurato."
    )

    st.divider()
    st.subheader("Quanto vento c'è davvero in Friuli-Venezia Giulia")
    st.caption(
        "Punti campionati sull'Atlante Eolico RSE a 100 metri sul livello del terreno. "
        "La producibilità specifica è espressa in ore equivalenti annue: quante ore "
        "all'anno un aerogeneratore lavorerebbe a piena potenza in quel punto."
    )

    eol = pd.DataFrame(DOC.EOLICO_PUNTI)
    e1, e2, e3, e4 = st.columns(4)
    best = eol.loc[eol["prod_100"].idxmax()]
    e1.metric("Sito migliore", best["nome"], f"{best['prod_100']:,.0f} h/anno".replace(",", "."))
    e2.metric("Velocità del vento", f"{best['vento_100']:.1f} m/s", "a 100 m")
    e3.metric("Densità di potenza", f"{best['dens_100']:.0f} W/m²")
    e4.metric("Siti sopra 2.000 h", f"{(eol['prod_100'] > 2000).sum()} su {len(eol)}")

    fig = px.bar(eol.sort_values("prod_100"), x="prod_100", y="nome", orientation="h",
                 color="prod_100", color_continuous_scale="Viridis", text_auto=".0f",
                 hover_data={"vento_100": ":.1f", "quota": True, "dens_100": ":.0f"},
                 labels={"prod_100": "ore equivalenti annue", "nome": ""})
    fig.add_vline(x=2000, line_dash="dash", line_color="#111827",
                  annotation_text="soglia indicativa",
                  annotation_position="top left")
    fig.update_layout(height=380, coloraxis_showscale=False, **PLOT)
    grafico(fig, DOC.FONTE_EOLICO,
            "Le soglie di convenienza dipendono da costi e prezzi, non sono un dato tecnico.")

    c1, c2 = st.columns(2)
    with c1:
        fig = px.scatter(eol, x="vento_100", y="prod_100", size="dens_100", color="quota",
                         hover_name="nome", color_continuous_scale="Earth",
                         labels={"vento_100": "velocità media a 100 m (m/s)",
                                 "prod_100": "ore equivalenti", "quota": "quota (m)"})
        fig.update_layout(height=340, title="Vento, quota e resa", **PLOT)
        grafico(fig, DOC.FONTE_EOLICO)
    with c2:
        mappa_eol = eol.copy()
        fig = px.scatter_map(mappa_eol, lat="lat", lon="lon", size="prod_100",
                             color="prod_100", color_continuous_scale="Viridis",
                             hover_name="nome",
                             hover_data={"vento_100": ":.1f", "quota": True,
                                         "lat": False, "lon": False},
                             size_max=28, zoom=6.9, center={"lat": 46.05, "lon": 13.3},
                             map_style="carto-positron")
        fig.update_layout(height=340, margin=dict(t=30, b=10, l=0, r=0),
                          coloraxis_showscale=False, title="Dove sta il vento")
        grafico(fig, DOC.FONTE_EOLICO)

    st.success(
        f"**Il vento in FVG c'è, ma non dove ce lo si aspetta.** Il punto migliore non è "
        f"in montagna: è il **Carso triestino**, a quota zero, con **{best['prod_100']:,.0f} ore "
        "equivalenti".replace(",", ".")
        + f" e {best['vento_100']:.1f} m/s a 100 metri — è la bora. "
        "Subito dopo vengono i **Colli Orientali** con circa 2.950-2.990 ore. "
        "Le creste alpine, a 1.300 e 1.900 metri, rendono **meno** del Carso: "
        "circa 2.030-2.100 ore.\n\n"
        "Per confronto, il fotovoltaico regionale sta intorno alle 1.040-1.200 ore. "
        "Un aerogeneratore sul Carso produrrebbe quasi **tre volte** le ore di un impianto "
        "solare, e le produrrebbe soprattutto d'inverno e di notte."
    )
    st.warning(
        "**Attenzione a cosa dicono e cosa non dicono questi numeri.** Sono otto punti "
        "campionati, non una mappa continua: servono a dire dove vale la pena guardare, "
        "non a progettare un impianto. E producibilità tecnica non significa fattibilità: "
        "il Carso e i Colli Orientali sono aree di alto pregio paesaggistico e naturalistico, "
        "e la distanza dalla cabina primaria più vicina (da 1,4 a 15,5 km secondo il punto) "
        "pesa sul costo di connessione."
    )


def _scheda_15():
    st.subheader("Dati sottostanti")
    st.caption(
        "Tutto quello che vedi nell'app viene da questa tabella unica, prodotta da "
        "`src/etl_terna.py` a partire dagli export XLSX di Terna."
    )
    ds = st.multiselect("Dataset", sorted(df["dataset"].unique()),
                        default=sorted(df["dataset"].unique())[:2])
    vista = df[df["dataset"].isin(ds)] if ds else df
    st.dataframe(vista, width="stretch", height=420)
    st.download_button("Scarica CSV", vista.to_csv(index=False).encode("utf-8"),
                       file_name=f"fvg_energia_{anno}.csv", mime="text/csv")

    with st.expander("Copertura e limiti dei dati"):
        st.markdown(
            "- I dati Terna coprono **solo il settore elettrico**: produzione, potenza, "
            "combustibili e CO₂ della generazione.\n"
            "- Non ci sono ancora: **richiesta elettrica regionale**, **consumi finali per settore** "
            "(industria, civile, trasporti), **vettori non elettrici** (gas, prodotti petroliferi), "
            "**saldo import/export** con le altre regioni e con la Slovenia/Austria.\n"
            "- Le emissioni sono quelle della sola generazione termoelettrica, non l'inventario "
            "regionale completo (ISPRA stima ~11,3 Mt CO₂eq per il FVG al 2019).\n"
            "- Il dataset `potenza_efficiente_per_sottocategoria_mw` non ha la dimensione anno: "
            "è un aggregato sull'intero periodo, quindi non è usato nei grafici temporali."
        )


# ------------------------------------------------------------- navigazione
# Due pagine, un file solo: `st.navigation` separa l'esplorazione dei dati dal
# motore di scenario, che ha esigenze diverse (gira una simulazione oraria e
# non serve a chi vuole solo consultare i numeri). Dentro l'esplorazione, le
# sedici schede sono raggruppate in sezioni ed eseguite una alla volta.
SEZIONI = [
    ('📊 Quadro generale', [0]),
    ('⚡ Elettricità e rinnovabili', [1, 3, 4, 7]),
    ('🔥 Termico, gas e bioenergie', [8, 9, 5, 6]),
    ('🔌 Reti e territorio', [2]),
    ('🌍 Clima ed emissioni', [12, 13]),
    ('🔮 Scenari e transizione', [11, 14, 10]),
    ('🗂 Dati e fonti', [15]),
]
NOMI_SCHEDE = ['📊 Panoramica', '⚡ Elettricità', '🔌 Reti', '☀️ Fotovoltaico', '🌱 Rinnovabili', '🌲 Biomasse', '♻️ Biometano', '💧 Idroelettrico', '🔥 Gas', '🔥 Termo & CO₂', '🧪 Idrogeno', '🔮 Scenari', '🌍 Emissioni', '🌡️ Clima', '📈 Transizione', '🗂 Dati']

_schede = {n: globals()[f"_scheda_{n}"] for n in range(len(NOMI_SCHEDE))}


def pagina_esplora():
    pagina_kpi()
    with st.sidebar:
        st.divider()
        st.markdown("**Sezione**")
        sezione = st.radio("Sezione", [s[0] for s in SEZIONI],
                           label_visibility="collapsed")
    indici = dict(SEZIONI)[sezione]
    if len(indici) == 1:
        _schede[indici[0]]()
    else:
        for t, i in zip(st.tabs([NOMI_SCHEDE[i] for i in indici]), indici):
            with t:
                _schede[i]()
    piede()


def pagina_motore():
    _motore_scenari()
    piede()



# ================================================================ 1. PANORAMICA

# ================================================================ 2. ELETTRICITÀ

# ================================================================ 3. RINNOVABILI

# ================================================================ 4. TERMO & CO2

# ================================================================ 5. SANKEY

# ================================================================ 6. TREND

# ================================================================ 7. DATI

def piede():
    st.divider()
    with st.expander("Fonti, licenze e limiti dei dati"):
        st.markdown(
            f"""
    **Da dove vengono i numeri.** Ogni grafico dichiara la propria fonte subito sotto.
    Le principali sono: **{DOC.F_TERNA}** per la serie storica del settore elettrico;
    **{DOC.F_TERNA_REG}** per il dettaglio provinciale; **{DOC.F_PER}** per il bilancio
    energetico e gli scenari; **{DOC.F_RSE}**; **{DOC.F_REGIONE}** per i progetti
    autorizzati e le aree delle cabine primarie; **{DOC.F_AUDIZIONI}** per lo stato
    delle reti; **{DOC.F_ARPA}** e **{DOC.F_ISPRA}** per clima ed emissioni.

    **Licenza dei dati RSE.** I dataset del Geoportale ETA sono distribuiti da RSE S.p.A.
    con licenza **Creative Commons BY-SA 4.0**: l'attribuzione va mantenuta e i dati
    derivati vanno rilasciati con la stessa licenza.

    **Sui dati GSE.** Il GSE è il detentore dei dati di dettaglio sugli impianti
    incentivati — Atlaimpianti contiene la georeferenziazione puntuale del fotovoltaico,
    la distinzione fra impianti a terra e su copertura, l'alimentazione dei digestori a
    biogas e la potenza per classe di taglia. **Questi dati non sono stati usati qui**:
    non sono liberamente scaricabili in forma massiva e richiedono una richiesta formale.
    Dove servirebbero, l'app usa aggregazioni comunali o provinciali e lo dichiara.
    Le conseguenze pratiche sono tre: la mappa del fotovoltaico si ferma al comune e non
    arriva al singolo impianto; la distinzione tetto/terra è ricostruita per classe di
    potenza e non per tipologia dichiarata; l'alimentazione degli impianti a biogas
    (colture dedicate contro scarti e deiezioni) è nota solo come categoria di fonte.
    Con l'accesso ai dati GSE queste tre limitazioni cadrebbero.

    **Cosa questo strumento non è.** Non è un modello previsionale né un documento di
    pianificazione. Gli scenari riproducono quelli del PER; i calcoli parametrici
    (copertura, idrogeno, dispacciamento) servono a confrontare ordini di grandezza fra
    opzioni, non a valutare investimenti. Dove un dato è stimato, è scritto.
            """
        )
    st.caption(
        f"Sviluppato da {DOC.AUTORE['nome']} — [{DOC.AUTORE['ente']}]({DOC.AUTORE['sito']}) · "
        f"[{DOC.AUTORE['email']}](mailto:{DOC.AUTORE['email']}) · "
        f"[LinkedIn]({DOC.AUTORE['linkedin']}) · [GitHub]({DOC.AUTORE['github']})"
    )

    # ================================================================ CONSUMI FINALI

    # ================================================================ SCENARI

    # ================================================================ RETI

    # ================================================================ IDROELETTRICO

    # ================================================================ CLIMA

    # ================================================================ FOTOVOLTAICO

    # ================================================================ GAS

    # ================================================================ IDROGENO

    # ---- aggiunte alla scheda Scenari: il Sankey 2045

    # ---- aggiunte alla scheda Reti: avanzamento, accumuli, distributori

    # ---- mappa delle aree di influenza delle cabine primarie

    # ---- Fotovoltaico: dove si potrebbe installare (dati RSE)

    # ---- Idroelettrico: la mappa delle centrali

    # ---- Reti: le inversioni di flusso

    # ---- Emissioni: il quadro completo

    # ---- Fotovoltaico: la pipeline autorizzativa e il suolo

    # ================================================================ BIOMASSE

    # ================================================================ BIOMETANO

    # ---- Ipotesi di copertura (scheda Transizione)

    # ---- Eolico: perché in FVG non c'è, e cosa cambierebbe

    # ---- Eolico misurato: l'Atlante RSE (scheda Transizione)

    # ---- Centrali termoelettriche (scheda Termo & CO2)


# ================================================================ MOTORE SCENARI
@st.cache_data(show_spinner=False)
def _serie_oraria() -> pd.DataFrame:
    dati = D.carica_per("orario_2023")
    dati = dati.rename(columns={dati.columns[0]: "ora"}).set_index("ora")
    dati.index = pd.to_datetime(dati.index)
    return dati


@st.cache_data(show_spinner="Simulo le configurazioni ora per ora...")
def _esplora(pv, eo, bess, prezzi_d, rete_d, colonna_eolico):
    base = Parco(**DOC.PARCO_BASE_FVG)
    return esplora(_serie_oraria(), base, list(pv), list(eo), list(bess),
                   prezzi=Prezzi(**prezzi_d), rete=CostiRete(**rete_d),
                   colonna_eolico=colonna_eolico)


def _motore_scenari():
    st.title("🔮 Motore di scenario")
    st.markdown(
        "Ogni configurazione viene simulata **ora per ora su un anno intero**: 8.760 "
        "passi in cui il carico va coperto con quello che c'è in quel momento. È la "
        "differenza fra dire «copriamo il 60% della domanda» e verificare se quel 60% "
        "arriva quando serve."
    )

    serie = _serie_oraria()
    st.caption(
        f"Anno simulato: {serie.index.year[0]} · {len(serie):,} ore · ".replace(",", ".")
        + f"carico {serie['carico_totale_mw'].sum() / 1000:,.0f} GWh. ".replace(",", ".")
        + "Profili fotovoltaico da PVGIS ed eolico dall'Atlante RSE; la **forma oraria "
        "del carico è un archetipo**, calibrato sui totali Terna ma non misurato."
    )

    with st.sidebar:
        st.divider()
        st.markdown("**Cosa esplorare**")
        pv_max = st.slider("Fotovoltaico massimo (MW)", 1500, 6000, 4000, 250)
        eo_max = st.slider("Eolico massimo (MW)", 0, 1500, 600, 100)
        bess_max = st.slider("Accumuli massimi (MWh)", 800, 12000, 6000, 400)
        passi = st.select_slider("Punti per asse", [3, 4, 5, 6], value=4)
        sito_eolico = st.selectbox(
            "Sito eolico di riferimento",
            {"cf_eolico_Carso_Basovizza": "Carso triestino (3.169 h)",
             "cf_eolico_Colli_Orientali": "Colli Orientali (2.945 h)"},
            format_func=lambda k: {"cf_eolico_Carso_Basovizza": "Carso triestino (3.169 h)",
                                   "cf_eolico_Colli_Orientali": "Colli Orientali (2.945 h)"}[k])

    base = DOC.PARCO_BASE_FVG
    pv_range = np.linspace(base["pv_mw"], pv_max, passi).round(0)
    eo_range = np.linspace(0, eo_max, passi).round(0) if eo_max else [0]
    bess_range = np.linspace(base["bess_mwh"], bess_max, passi).round(0)

    with st.expander("Prezzi, contratti per differenza e costi di rete"):
        c = st.columns(4)
        prezzi_d = {
            "cfd_pv": c[0].number_input("CfD fotovoltaico (€/MWh)", 20, 150, 60),
            "cfd_eolico": c[1].number_input("CfD eolico (€/MWh)", 30, 150, 80),
            "cfd_idro": c[2].number_input("CfD idroelettrico (€/MWh)", 20, 150, 55),
            "gas": c[3].number_input("Prezzo del gas (€/MWh)", 30, 300, 130),
        }
        c2 = st.columns(4)
        prezzi_d["importazione"] = c2[0].number_input(
            "Prezzo dell'energia importata (€/MWh)", 40, 250, int(DOC.PUN_MEDIO_2025))
        prezzi_d["lcos"] = c2[1].number_input("Costo dell'accumulo (€/MWh scaricato)", 30, 250, 90)
        prezzi_d["voll"] = 3000.0
        rete_d = {
            "connessione_eur_kw": c2[2].number_input(
                "Connessione (€/kW)", 20, 300, DOC.COSTI_RETE["connessione_eur_kw"]),
            "rinforzo_eur_kw": c2[3].number_input(
                "Rinforzo oltre hosting capacity (€/kW)", 0, 600,
                DOC.COSTI_RETE["rinforzo_eur_kw_oltre_hosting"]),
            "hosting_capacity_mw": float(DOC.HOSTING_CAPACITY_MW),
            "vita_anni": 30, "wacc": 0.06,
        }
        st.caption(
            f"Fonte dei costi di rete: {DOC.FONTE_COSTI_RETE}. Sotto i "
            f"{DOC.HOSTING_CAPACITY_MW} MW di hosting capacity si paga la sola connessione; "
            "oltre, anche il rinforzo. È la differenza che il modello nazionale non fa."
        )

    df = _esplora(tuple(pv_range), tuple(eo_range), tuple(bess_range),
                  prezzi_d, rete_d, sito_eolico)
    ott = migliore(df)

    st.subheader("La configurazione con meno emissioni, a parità di costo")
    st.caption("Fra tutte quelle entro il 5% dal costo minimo.")
    m = st.columns(5)
    m[0].metric("Fotovoltaico", f"{ott['pv_mw']:,.0f} MW".replace(",", "."),
                f"{ott['pv_mw'] - base['pv_mw']:+,.0f} rispetto a oggi".replace(",", "."))
    m[1].metric("Eolico", f"{ott['eolico_mw']:,.0f} MW".replace(",", "."))
    m[2].metric("Accumuli", f"{ott['bess_mwh']:,.0f} MWh".replace(",", "."))
    m[3].metric("Costo del sistema", f"{ott['eur_mwh']:.1f} €/MWh",
                f"di cui rete {ott['eur_mwh'] - ott['eur_mwh_senza_rete']:.1f}")
    m[4].metric("Intensità carbonica", f"{ott['gco2_kwh']:.0f} g/kWh")

    m2 = st.columns(4)
    m2[0].metric("Import residuo", f"{ott['quota_import']:.0f}%",
                 f"{ott['import_gwh']:,.0f} GWh".replace(",", "."))
    m2[1].metric("Quota rinnovabile", f"{ott['quota_fer']:.0f}%")
    m2[2].metric("Export di surplus", f"{ott['export_gwh']:,.0f} GWh".replace(",", "."))
    m2[3].metric("Costo annuo della rete", f"{ott['costo_rete_mln']:.0f} mln €")

    st.subheader("Frontiera di Pareto: costo contro emissioni")
    fr = frontiera(df)
    fig = px.scatter(df, x="gco2_kwh", y="eur_mwh", color="eolico_mw",
                     size="bess_mwh", hover_data=["pv_mw", "quota_import", "quota_fer"],
                     color_continuous_scale="Viridis",
                     labels={"gco2_kwh": "gCO₂/kWh (ciclo di vita)",
                             "eur_mwh": "€/MWh, rete inclusa", "eolico_mw": "eolico (MW)"})
    fig.add_scatter(x=fr["gco2_kwh"], y=fr["eur_mwh"], mode="lines",
                    line=dict(color="#111827", dash="dot"), name="Frontiera")
    fig.add_scatter(x=[ott["gco2_kwh"]], y=[ott["eur_mwh"]], mode="markers",
                    marker=dict(size=18, color="#22C55E", line=dict(color="#111827", width=2)),
                    name="Scelta")
    fig.update_layout(height=520, xaxis_autorange="reversed", template="plotly_white",
                      margin=dict(t=48, b=10, l=10, r=24))
    grafico(fig, DOC.F_ELAB,
            f"{len(df)} configurazioni simulate, {len(fr)} non dominate.")

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Quanto pesa l'eolico sull'import**")
        agg = df.groupby("eolico_mw", as_index=False).agg(
            import_min=("quota_import", "min"), costo_min=("eur_mwh", "min"),
            co2_min=("gco2_kwh", "min"))
        fig = px.line(agg, x="eolico_mw", y="import_min", markers=True,
                      color_discrete_sequence=["#22C55E"])
        fig.update_layout(height=320, xaxis_title="eolico installato (MW)",
                          yaxis_title="import minimo raggiungibile (%)", **PLOT)
        grafico(fig, DOC.F_ELAB)
    with c2:
        st.markdown("**Il costo della rete cresce a scalino**")
        fig = px.scatter(df, x="nuova_potenza_mw", y="costo_rete_mln",
                         color_discrete_sequence=["#F97316"])
        fig.add_vline(x=DOC.HOSTING_CAPACITY_MW, line_dash="dash", line_color="#111827",
                      annotation_text="hosting capacity", annotation_position="top left")
        fig.update_layout(height=320, xaxis_title="nuova potenza connessa (MW)",
                          yaxis_title="costo annuo di rete (mln €)", **PLOT)
        grafico(fig, DOC.FONTE_COSTI_RETE)

    with st.expander("Tutte le configurazioni simulate"):
        vista = df[["pv_mw", "eolico_mw", "bess_mwh", "eur_mwh", "costo_rete_mln",
                    "gco2_kwh", "quota_import", "quota_fer", "export_gwh",
                    "curtailment_gwh", "spillamento_gwh"]].copy()
        vista.columns = ["PV (MW)", "Eolico (MW)", "BESS (MWh)", "€/MWh", "Rete (mln €)",
                         "gCO₂/kWh", "Import %", "FER %", "Export (GWh)",
                         "Curtailment (GWh)", "Spillamento (GWh)"]
        st.dataframe(vista.round(1).sort_values("€/MWh"), hide_index=True,
                     width="stretch", height=340)

    st.warning(
        "**Cosa il motore non fa.** La forma oraria del carico è un archetipo calibrato "
        "sui totali Terna, non una misura: i risultati sono robusti sui confronti fra "
        "configurazioni, meno sui valori assoluti. Non c'è la rete interna alla regione, "
        "quindi la congestione locale non appare — e in FVG è il vincolo vero, come "
        "mostra la scheda Reti. I costi di rete sono ordini di grandezza, non preventivi. "
        "Serve a capire quale direzione conviene, non quanto costerà."
    )


# ------------------------------------------------------------- pagine
_navigazione = st.navigation([
    st.Page(pagina_esplora, title="Esplora i dati", icon="📊", default=True),
    st.Page(pagina_motore, title="Motore di scenario", icon="🔮"),
])
_navigazione.run()
