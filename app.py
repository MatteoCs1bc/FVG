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

PLOT = dict(
    template="plotly_white",
    margin=dict(t=30, b=10, l=10, r=10),
    legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0),
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


def anno_di(s: pd.DataFrame, a: int = None) -> pd.DataFrame:
    return s[s["anno"] == (a or anno)]


# ---------------------------------------------------------------- intestazione
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

k = st.columns(5)
k[0].metric("Produzione lorda", f"{p_tot:,.0f} GWh".replace(",", "."),
            f"{D.variazione(prod_fonte, anno) or 0:+.1f}%" if D.variazione(prod_fonte, anno) else None)
k[1].metric("Quota rinnovabile", f"{quota_fer:.1f}%")
k[2].metric("Potenza efficiente", f"{pot_tot:,.0f} MW".replace(",", "."))
k[3].metric("Emissioni CO₂ (elettrico)", f"{em_tot:.2f} Mt")
k[4].metric("Intensità carbonica", f"{intensita:.0f} g/kWh")

bil_kpi = D.carica_per("bilancio_2021")
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

tabs = st.tabs([
    "📊 Panoramica",
    "🔄 Bilancio",
    "🏭 Consumi finali",
    "⚡ Elettricità",
    "🔌 Reti",
    "☀️ Fotovoltaico",
    "🌱 Rinnovabili",
    "💧 Idroelettrico",
    "🔥 Gas",
    "🔥 Termo & CO₂",
    "🧪 Idrogeno",
    "🔮 Scenari",
    "🌡️ Clima",
    "📈 Transizione",
    "🗂 Dati",
])

# ================================================================ 1. PANORAMICA
with tabs[0]:
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
            st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("Produzione lorda per fonte")
        fig = px.area(prod_fonte.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_fonte["voce"]))
        fig.update_layout(height=380, yaxis_title="GWh", xaxis_title=None, **PLOT)
        fig.add_vline(x=anno, line_dash="dot", line_color="#111827")
        st.plotly_chart(fig, width="stretch")

    st.subheader("Quota rinnovabile sulla produzione lorda")
    tot_y = prod_fonte.groupby("anno")["valore"].sum()
    fer_y = prod_fer.groupby("anno")["valore"].sum()
    quota = (fer_y / tot_y * 100).dropna().reset_index(name="quota")
    fig = px.line(quota, x="anno", y="quota", markers=True,
                  color_discrete_sequence=["#22C55E"])
    fig.update_layout(height=300, yaxis_title="% FER", xaxis_title=None,
                      yaxis_range=[0, 100], **PLOT)
    fig.add_hline(y=quota["quota"].mean(), line_dash="dot", line_color="#9CA3AF",
                  annotation_text=f"media {quota['quota'].mean():.0f}%")
    st.plotly_chart(fig, width="stretch")

# ================================================================ 2. ELETTRICITÀ
with tabs[3]:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader(f"Produzione per fonte, {anno}")
        m = anno_di(prod_fonte).sort_values("valore", ascending=True)
        fig = px.bar(m, x="valore", y="voce", orientation="h", color="voce",
                     color_discrete_map=D.mappa_colori(m["voce"]), text_auto=".0f")
        fig.update_layout(showlegend=False, height=340, xaxis_title="GWh",
                          yaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader(f"Potenza efficiente {tipo_cap.lower()}, {anno}")
        m = anno_di(pot_fonte).sort_values("valore", ascending=True)
        fig = px.bar(m, x="valore", y="voce", orientation="h", color="voce",
                     color_discrete_map=D.mappa_colori(m["voce"]), text_auto=".0f")
        fig.update_layout(showlegend=False, height=340, xaxis_title="MW",
                          yaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Potenza installata nel tempo")
    fig = px.area(pot_fonte.sort_values("anno"), x="anno", y="valore", color="voce",
                  color_discrete_map=D.mappa_colori(pot_fonte["voce"]))
    fig.update_layout(height=340, yaxis_title="MW", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

    st.subheader("Ore equivalenti di utilizzo")
    st.caption("Produzione annua / potenza efficiente. Indica quanto intensamente lavora ogni parco.")
    merge = prod_fonte.merge(pot_fonte, on=["anno", "voce"], suffixes=("_gwh", "_mw"))
    merge = merge[merge["valore_mw"] > 1]
    merge["ore"] = merge["valore_gwh"] * 1000 / merge["valore_mw"]
    fig = px.line(merge.sort_values("anno"), x="anno", y="ore", color="voce", markers=True,
                  color_discrete_map=D.mappa_colori(merge["voce"]))
    fig.update_layout(height=340, yaxis_title="ore/anno", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

# ================================================================ 3. RINNOVABILI
with tabs[6]:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Produzione rinnovabile per fonte")
        fig = px.area(prod_fer.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_fer["voce"]))
        fig.update_layout(height=360, yaxis_title="GWh", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader(f"Potenza rinnovabile ({tipo_cap.lower()})")
        fig = px.area(pot_fer.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(pot_fer["voce"]))
        fig.update_layout(height=360, yaxis_title="MW", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Idroelettrico per tipologia di impianto")
    st.caption("Il fluente segue la piovosità, bacini e serbatoi modulano.")
    fig = px.bar(idrico.sort_values("anno"), x="anno", y="valore", color="voce",
                 color_discrete_map=D.mappa_colori(idrico["voce"]))
    fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, barmode="stack", **PLOT)
    st.plotly_chart(fig, width="stretch")

# ================================================================ 4. TERMO & CO2
with tabs[9]:
    c1, c2 = st.columns(2)

    with c1:
        st.subheader("Produzione termoelettrica per combustibile")
        fig = px.area(prod_comb.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(prod_comb["voce"]))
        fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.subheader("Emissioni di CO₂ per combustibile")
        fig = px.area(emissioni.sort_values("anno"), x="anno", y="valore", color="voce",
                      color_discrete_map=D.mappa_colori(emissioni["voce"]))
        fig.update_layout(height=340, yaxis_title="Mt CO₂", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    st.subheader("Intensità carbonica della generazione")
    st.caption("Emissioni totali del parco termoelettrico divise per la produzione elettrica lorda regionale.")
    tot_em = emissioni.groupby("anno")["valore"].sum()
    inten = (tot_em * 1e6 / tot_y).dropna().reset_index(name="g_kwh")
    fig = px.line(inten, x="anno", y="g_kwh", markers=True, color_discrete_sequence=["#DC2626"])
    fig.update_layout(height=300, yaxis_title="g CO₂/kWh", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

    c3, c4 = st.columns(2)
    with c3:
        st.subheader("Cogenerative vs non cogenerative")
        fig = px.bar(prod_cat.sort_values("anno"), x="anno", y="valore", color="voce",
                     color_discrete_map=D.mappa_colori(prod_cat["voce"]))
        fig.update_layout(height=340, yaxis_title="GWh elettrici", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    with c4:
        st.subheader("Calore utile da cogenerazione")
        cal = calore.copy()
        cal["voce"] = cal["voce"].map(IMPIANTI_COGEN).fillna(cal["voce"])
        fig = px.bar(cal.sort_values("anno"), x="anno", y="valore", color="voce")
        fig.update_layout(height=340, yaxis_title="GWh termici", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

# ================================================================ 5. SANKEY
with tabs[1]:
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
        st.plotly_chart(fig, width="stretch")

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

    # parco -> categorie di impianto (pro quota sulla produzione elettrica)
    tot_cat = sum(cat_y.get(c, 0) for c in categorie)
    for c in categorie:
        quota_c = cat_y[c] / tot_cat if tot_cat else 0
        link("Parco termoelettrico", c, (el_termo + cal_y) * quota_c, "rgba(75,85,99,0.35)")
    link("Parco termoelettrico", "Perdite di conversione", perdite, "rgba(239,68,68,0.3)")

    # categorie -> elettricità / calore
    for c in categorie:
        quota_c = cat_y[c] / tot_cat if tot_cat else 0
        link(c, "Energia elettrica", cat_y[c], "rgba(250,204,21,0.45)")
        if "Cogenerative" in c and "Non" not in c:
            link(c, "Calore utile", cal_y, "rgba(249,115,22,0.45)")

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
    st.plotly_chart(fig, width="stretch")

    st.info(
        f"Input di combustibile stimato: **{input_comb:,.0f} GWh** · "
        f"elettricità termoelettrica **{el_termo:,.0f} GWh** · "
        f"calore utile **{cal_y:,.0f} GWh** · "
        f"perdite **{perdite:,.0f} GWh**. "
        "L'input non è misurato da Terna: dipende dal rendimento impostato sopra."
        .replace(",", ".")
    )

# ================================================================ 6. TREND
with tabs[13]:
    st.subheader("Sostituzione tra fonti (grafico di Marchetti)")
    st.caption("Asse y: log₁₀(f / (1−f)), con f = quota della fonte. Una retta = sostituzione a ritmo costante.")

    m = prod_fonte.merge(tot_y.rename("tot"), on="anno")
    m = m[(m["tot"] > 0) & (m["valore"] > 0)]
    m["f"] = np.clip(m["valore"] / m["tot"], 1e-4, 1 - 1e-4)
    m["marchetti"] = np.log10(m["f"] / (1 - m["f"]))
    fig = px.line(m.sort_values("anno"), x="anno", y="marchetti", color="voce", markers=True,
                  color_discrete_map=D.mappa_colori(m["voce"]))
    fig.update_layout(height=400, yaxis_title="log(f / 1−f)", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

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
    st.plotly_chart(fig, width="stretch")

# ================================================================ 7. DATI
with tabs[14]:
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

st.divider()
st.caption("Fonte: Terna – Dati Statistici (dati.terna.it) · Elaborazione: FVG Energy Explorer")

# ================================================================ CONSUMI FINALI
with tabs[2]:
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
            st.plotly_chart(fig, width="stretch")
        with c2:
            fig = px.pie(per_vettore.reset_index(), values="valore", names="vettore", hole=0.55,
                         color="vettore", color_discrete_map={
                             "Combustibili gassosi": "#9CA3AF", "Energia elettrica": "#FACC15",
                             "Petrolio": "#4B5563", "Energie rinnovabili": "#22C55E",
                             "Calore derivato": "#F97316", "Combustibili solidi": "#111827",
                             "Rifiuti non rinnovabili": "#D1D5DB"})
            fig.update_traces(textinfo="percent+label", textposition="outside")
            fig.update_layout(showlegend=False, height=380, title="Per vettore", **PLOT)
            st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig, width="stretch")

        st.subheader("Composizione di ogni settore")
        fig = px.bar(consumi_f[consumi_f["valore"] > 0], x="settore", y="valore", color="vettore",
                     color_discrete_map={
                         "Combustibili gassosi": "#9CA3AF", "Energia elettrica": "#FACC15",
                         "Petrolio": "#4B5563", "Energie rinnovabili": "#22C55E",
                         "Calore derivato": "#F97316", "Combustibili solidi": "#111827"})
        fig.update_layout(height=400, yaxis_title="ktep", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

        el_share = per_vettore.get("Energia elettrica", 0) / tot_cf * 100
        st.info(
            f"L'elettricità copre il **{el_share:.0f}%** dei consumi finali. "
            "Industria e civile pesano quasi uguale (~40% ciascuno), ma con vettori diversi: "
            "l'industria va a elettricità e gas, il civile quasi solo a gas. "
            "I trasporti restano il settore meno elettrificato: petrolio all'86%."
        )

# ================================================================ SCENARI
with tabs[11]:
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
        st.plotly_chart(fig, width="stretch")

        emis = sc[sc["grandezza"] == "Emissioni CO2"]
        if not emis.empty:
            st.subheader("Emissioni di CO₂ per settore")
            fig = px.line(emis.sort_values("anno"), x="anno", y="valore",
                          color="scenario", line_dash="settore", markers=True,
                          color_discrete_map={"Storico": "#111827", "REF": "#6B7280",
                                              "A": "#2563EB", "B": "#22C55E", "PER": "#F97316"})
            fig.update_layout(height=380, yaxis_title="kt CO₂", xaxis_title=None, **PLOT)
            st.plotly_chart(fig, width="stretch")

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
            st.plotly_chart(fig, width="stretch")

        with c2:
            st.subheader("Industria: sostituzione dei vettori")
            fig = px.area(ind_v.sort_values("anno"), x="anno", y="valore", color="vettore",
                          color_discrete_map={"Gas": "#9CA3AF", "Elettricità": "#FACC15",
                                              "FER": "#22C55E", "Calore derivato": "#F97316",
                                              "Prodotti petroliferi": "#4B5563",
                                              "Solidi": "#111827"})
            fig.update_layout(height=380, yaxis_title="ktep", xaxis_title=None, **PLOT)
            st.plotly_chart(fig, width="stretch")

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
            st.plotly_chart(fig, width="stretch")
            st.caption(
                "Il PER assume −68.000 abitanti e +24% di PIL reale tra il 2021 e il 2045: "
                "il disaccoppiamento tra economia ed energia deve reggere su una base demografica "
                "che si assottiglia."
            )

# ================================================================ RETI
with tabs[4]:
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
        st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig, width="stretch")
    with c4:
        pr = pd.DataFrame(DOC.TRASFORMATORI_PROVINCIA.items(), columns=["Provincia", "Trasformatori"])
        fig = px.bar(pr, x="Provincia", y="Trasformatori", text_auto=True,
                     color_discrete_sequence=["#6B7280"])
        fig.update_layout(height=320, xaxis_title=None,
                          title="Trasformatori AT/MT per provincia", **PLOT)
        st.plotly_chart(fig, width="stretch")

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
    fig.update_traces(textposition="outside")
    fig.update_layout(height=340, xaxis_title=None,
                      yaxis_title="MVA di incremento", **PLOT)
    st.plotly_chart(fig, width="stretch")
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
                  annotation_text=f"Target 2030: {target} GW")
    fig.update_layout(showlegend=False, height=360, xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")
    st.info(
        f"Il Decreto Aree Idonee assegna al FVG **+{target} GW** di nuova capacità rinnovabile "
        f"al 2030 rispetto al 2021. Ne risultano in esercizio o autorizzati "
        f"**{DOC.BURDEN_SHARING['In esercizio o autorizzato dal 2021']} GW**: l'82% del percorso. "
        "Il collo di bottiglia non è più autorizzare impianti, è avere rete che li accolga."
    )

# ================================================================ IDROELETTRICO
with tabs[7]:
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
                      annotation_text=f"producibilità media {prod_media:.0f} GWh")
        fig.update_layout(height=400, yaxis_title="GWh", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

    with c2:
        st.markdown("**Composizione nell'anno selezionato**")
        m = anno_di(idrico)
        m = m[m["valore"] > 0]
        if not m.empty:
            fig = px.pie(m, values="valore", names="voce", hole=0.5,
                         color="voce", color_discrete_map=D.mappa_colori(m["voce"]))
            fig.update_traces(textinfo="percent")
            fig.update_layout(height=400, **PLOT)
            st.plotly_chart(fig, width="stretch")

    st.subheader("Quanto lavora il parco idroelettrico")
    st.caption(
        "Ore equivalenti annue: produzione divisa per la potenza installata. "
        "Sono la firma della variabilità idrologica, non dell'efficienza degli impianti."
    )
    pot_idro = pot_fonte[pot_fonte["voce"] == "Idrico"]
    ore_idro = (idro_tot / pot_idro.set_index("anno")["valore"] * 1000).dropna().reset_index(name="ore")
    fig = px.bar(ore_idro, x="anno", y="ore", color_discrete_sequence=["#2563EB"])
    fig.add_hline(y=ore_idro["ore"].mean(), line_dash="dot", line_color="#111827",
                  annotation_text=f"media {ore_idro['ore'].mean():.0f} ore")
    fig.update_layout(height=340, yaxis_title="ore/anno", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

    st.info(
        "Il PER stima una producibilità media di "
        f"{DOC.IDRO_PARCO['Producibilità media annua (GWh)']:,.0f} GWh e prevede di arrivare a ".replace(",", ".")
        + "2.231 GWh al 2045: un margine di crescita limitato, perché i siti migliori sono già "
        "sfruttati. L'espansione passa da efficientamento degli impianti esistenti e "
        "mini-idro, non da nuovi grandi invasi."
    )

# ================================================================ CLIMA
with tabs[12]:
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
    st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig, width="stretch")
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

# ================================================================ FOTOVOLTAICO
with tabs[5]:
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
        st.plotly_chart(fig, width="stretch")
    with c2:
        st.markdown("**Produzione annua**")
        fig = px.bar(pv_serie.sort_values("anno"), x="anno", y="valore",
                     color_discrete_sequence=["#F59E0B"])
        fig.update_layout(height=340, yaxis_title="GWh", xaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig, width="stretch")
    with c4:
        if not pv_prov.empty:
            dens = pv_prov.dropna(subset=["densita_potenza_w_ab"])
            fig = px.bar(dens.sort_values("densita_potenza_w_ab"), x="densita_potenza_w_ab",
                         y="provincia", orientation="h", text_auto=".0f",
                         color_discrete_sequence=["#F59E0B"])
            fig.update_layout(height=300, yaxis_title=None, xaxis_title="W per abitante",
                              title="Potenza per abitante", **PLOT)
            st.plotly_chart(fig, width="stretch")

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
        st.plotly_chart(fig, width="stretch")
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

# ================================================================ GAS
with tabs[8]:
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
        st.plotly_chart(fig, width="stretch")
        st.caption(
            f"Il rendimento applicato al ramo di trasformazione è quello medio del "
            f"sistema regionale ({rend_gas * 100:.0f}%), non misurato sul solo gas."
        )

        st.subheader("Dove va il gas che non passa dalla centrale")
        fig = px.bar(gas_finali.sort_values("valore"), x="valore", y="settore", orientation="h",
                     text_auto=".0f", color_discrete_sequence=["#9CA3AF"])
        fig.update_layout(height=300, xaxis_title="ktep", yaxis_title=None, **PLOT)
        st.plotly_chart(fig, width="stretch")

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
            st.plotly_chart(fig, width="stretch")
        with c2:
            em_gas = emissioni[emissioni["voce"].str.contains("gas", case=False, na=False)]
            fig = px.area(em_gas.sort_values("anno"), x="anno", y="valore",
                          color_discrete_sequence=["#EF4444"])
            fig.update_layout(height=340, yaxis_title="Mt CO₂", xaxis_title=None,
                              title="Emissioni dalla generazione a gas", **PLOT)
            st.plotly_chart(fig, width="stretch")

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

# ================================================================ IDROGENO
with tabs[10]:
    st.subheader("Idrogeno: a che punto è il Friuli-Venezia Giulia")
    st.caption(f"Fonte: {DOC.FONTE_H2}.")

    n = DOC.H2_NAHV
    h = st.columns(4)
    h[0].metric("Finanziamento NAHV", f"{n['Finanziamento europeo (mln €)']} mln €")
    h[1].metric("Organizzazioni partner", n["Organizzazioni partner"])
    h[2].metric("Durata del progetto", f"{n['Durata (mesi)']} mesi")
    h[3].metric("Autobus a idrogeno previsti", sum(DOC.H2_MEZZI_TPL.values()))

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
    st.plotly_chart(fig, width="stretch")

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

# ---- aggiunte alla scheda Scenari: il Sankey 2045
with tabs[11]:
    st.divider()
    st.subheader("Come cambiano i consumi finali: 2021 e 2045 a confronto")

    cons21 = D.carica_per("consumi_finali_2021")
    ind_v = D.carica_per("scenari_industria_vettori")
    tra_al = D.carica_per("trasporti_alimentazione")
    sc_all = D.carica_per("scenari_settori")

    if not (cons21.empty or ind_v.empty or tra_al.empty):
        st.caption(
            "A sinistra il vettore, a destra il settore. Il PER disaggrega i vettori al 2045 "
            "per industria e trasporti; per il civile fornisce solo il totale, quindi resta "
            "un flusso unico. Scenario: Policy B per l'industria."
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
            c45.append(("Vettori non disaggregati", "Civile", civ45))

        agg45: dict[tuple[str, str], float] = {}
        for v_, s_, val in c45:
            agg45[(v_, s_)] = agg45.get((v_, s_), 0) + val
        c45 = [(v_, s_, val) for (v_, s_), val in agg45.items()]

        cc1, cc2 = st.columns(2)
        with cc1:
            st.plotly_chart(sankey_consumi(c21, "2021 — dato di bilancio"), width="stretch")
        with cc2:
            st.plotly_chart(sankey_consumi(c45, "2045 — scenario del PER"), width="stretch")

        tot21 = sum(v for _, _, v in c21)
        tot45 = sum(v for _, _, v in c45)
        st.info(
            f"I consumi finali passano da **{tot21:,.0f}** a **{tot45:,.0f} ktep**, "
            f"circa {(1 - tot45 / tot21) * 100:.0f}% in meno. ".replace(",", ".")
            + "Nei trasporti compare l'idrogeno, che oggi vale zero. Nell'industria il gas "
            "arretra e crescono elettricità e rinnovabili dirette. Il confronto non è "
            "perfettamente simmetrico: il 2021 è un bilancio consuntivo, il 2045 uno scenario, "
            "e il civile resta aggregato perché il PER non ne disaggrega i vettori."
        )

# ---- aggiunte alla scheda Reti: avanzamento, accumuli, distributori
with tabs[4]:
    st.divider()
    st.subheader("Avanzamento verso il target 2030, in dettaglio")
    st.caption(f"Fonte: {DOC.FONTE_RETI_REPORT}.")

    bsm = pd.DataFrame(DOC.BURDEN_SHARING_MW.items(), columns=["Voce", "MW"])
    bsm["Quota"] = bsm["MW"] / DOC.BURDEN_SHARING_TARGET_MW * 100
    fig = px.bar(bsm, x="MW", y=["Target"] * len(bsm), color="Voce", orientation="h",
                 text=bsm.apply(lambda r: f"{r['Voce']}<br>{r['MW']} MW", axis=1),
                 color_discrete_sequence=["#22C55E", "#2563EB", "#60A5FA", "#E5E7EB"])
    fig.update_traces(textposition="inside", insidetextanchor="middle")
    fig.update_layout(height=220, barmode="stack", showlegend=False, yaxis_title=None,
                      xaxis_title=f"MW sul target di {DOC.BURDEN_SHARING_TARGET_MW} MW", **PLOT)
    st.plotly_chart(fig, width="stretch")
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
        st.plotly_chart(fig, width="stretch")
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
        st.plotly_chart(fig, width="stretch")
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
    st.plotly_chart(fig, width="stretch")
    st.markdown(
        f"Una parte della saturazione è **virtuale**: capacità prenotata da richieste che non "
        f"diventeranno mai impianti. Storicamente solo il **{DOC.TASSO_REALIZZAZIONE}%** "
        "di quanto viene autorizzato si costruisce davvero. "
        f"Il **{DOC.DECRETO_BOLLETTE['riferimento']}** interviene proprio su questo:"
    )
    for titolo, testo in DOC.DECRETO_BOLLETTE["misure"]:
        st.markdown(f"- **{titolo}** — {testo}")

# ---- mappa delle aree di influenza delle cabine primarie
with tabs[4]:
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
        st.plotly_chart(fig, width="stretch")

        c1, c2 = st.columns([1, 1])
        with c1:
            per_gest = (aree.groupby("gestore")
                        .agg(aree_n=("codice", "count"), km2=("area_km2", "sum"))
                        .reset_index().sort_values("km2"))
            fig = px.bar(per_gest, x="km2", y="gestore", orientation="h", text="aree_n",
                         color="gestore", color_discrete_map=colori_gestore)
            fig.update_traces(textposition="outside", texttemplate="%{text} aree")
            fig.update_layout(showlegend=False, height=280, xaxis_title="km²",
                              yaxis_title=None, title="Territorio per gestore", **PLOT)
            st.plotly_chart(fig, width="stretch")

        with c2:
            fig = px.histogram(aree, x="area_km2", nbins=25,
                               color_discrete_sequence=["#6B7280"])
            fig.update_layout(height=280, xaxis_title="km² per area", yaxis_title="aree",
                              title="Quanto sono grandi le aree", **PLOT)
            st.plotly_chart(fig, width="stretch")

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

# ---- Fotovoltaico: dove si potrebbe installare (dati RSE)
with tabs[5]:
    st.divider()
    aree_fv = D.carica_per("aree_disponibili_fv")
    geo_fv = D.carica_geojson("aree_disponibili_fv")

    if not aree_fv.empty:
        st.subheader("Dove si potrebbe installare")
        st.caption(
            "Elaborazione RSE sulla base della Corine Land Cover 2018, al netto dei vincoli "
            "ambientali, paesaggistici e culturali. Sono superfici *eleggibili*, non aree "
            "idonee ai sensi di legge: dicono dove il territorio lo permetterebbe, non dove "
            "è consentito o conveniente."
        )

        tot_com = aree_fv["areakmq"].sum()
        s = st.columns(4)
        s[0].metric("Superficie regionale", f"{tot_com:,.0f} km²".replace(",", "."))
        s[1].metric("Aree agricole", f"{aree_fv['areakmq2'].sum():,.0f} km²".replace(",", "."),
                    f"{aree_fv['areakmq2'].sum() / tot_com * 100:.0f}% del territorio")
        s[2].metric("Agricole al netto dei vincoli",
                    f"{aree_fv['area2netta'].sum():,.0f} km²".replace(",", "."))
        s[3].metric("Superficie costruita",
                    f"{aree_fv['areacnkm2'].sum():,.0f} km²".replace(",", "."),
                    "il potenziale sui tetti")

        categorie = [
            ("Aree agricole al netto dei vincoli", "area2netta", "#22C55E"),
            ("di cui seminativi non irrigui", "area211net", "#65A30D"),
            ("Superficie impermeabilizzata", "areacnkm2", "#6B7280"),
            ("Superficie costruita (CTR)", "areactrkm2", "#9CA3AF"),
            ("Aree industriali e commerciali", "areakmq121", "#4B5563"),
            ("Agricole entro 500 m da aree industriali", "areakmqaal", "#F97316"),
            ("Aree estrattive", "areakmq131", "#A855F7"),
            ("Discariche", "areakmq132", "#EF4444"),
        ]
        cat = pd.DataFrame([
            {"Categoria": nome, "km²": aree_fv[col].sum(), "colore": c}
            for nome, col, c in categorie
        ]).sort_values("km²")

        fig = px.bar(cat, x="km²", y="Categoria", orientation="h", text_auto=".0f",
                     color="Categoria",
                     color_discrete_map=dict(zip(cat["Categoria"], cat["colore"])))
        fig.update_layout(showlegend=False, height=380, yaxis_title=None,
                          xaxis_type="log", xaxis_title="km² (scala logaritmica)", **PLOT)
        st.plotly_chart(fig, width="stretch")
        st.caption(
            "Scala logaritmica: le categorie differiscono di tre ordini di grandezza. "
            "Cave e discariche insieme fanno 6,6 km², le agricole al netto dei vincoli 1.887."
        )

        vista = st.selectbox(
            "Cosa mostrare sulla mappa",
            ["Aree agricole al netto dei vincoli", "Seminativi non irrigui al netto dei vincoli",
             "Superficie impermeabilizzata", "Agricole entro 500 m da aree industriali"],
        )
        colmap = {"Aree agricole al netto dei vincoli": ("area2netta", "Greens"),
                  "Seminativi non irrigui al netto dei vincoli": ("area211net", "YlGn"),
                  "Superficie impermeabilizzata": ("areacnkm2", "Greys"),
                  "Agricole entro 500 m da aree industriali": ("areakmqaal", "Oranges")}
        col, scala = colmap[vista]
        mappa = aree_fv.copy()
        mappa["quota"] = mappa[col] / mappa["areakmq"] * 100

        if geo_fv is not None:
            fig = px.choropleth_map(
                mappa, geojson=geo_fv, locations="comune", color="quota",
                color_continuous_scale=scala, map_style="carto-positron", zoom=7.2,
                center={"lat": 46.11, "lon": 13.10}, opacity=0.7,
                hover_name="comune",
                hover_data={col: ":.1f", "quota": ":.1f", "provincia": True, "comune": False},
                labels={"quota": "% del comune"},
            )
            fig.update_layout(height=560, margin=dict(t=10, b=10, l=0, r=0),
                              coloraxis_colorbar=dict(title="% del<br>comune"))
            st.plotly_chart(fig, width="stretch")

        top = mappa.nlargest(10, col)[["comune", "provincia", col, "quota"]]
        top.columns = ["Comune", "Provincia", "km²", "% del comune"]
        c1, c2 = st.columns([1, 1])
        with c1:
            st.markdown(f"**I dieci comuni con più superficie: {vista.lower()}**")
            st.dataframe(top.round(1), hide_index=True, width="stretch")
        with c2:
            prov = mappa.groupby("provincia")[col].sum().reset_index()
            fig = px.bar(prov.sort_values(col), x=col, y="provincia", orientation="h",
                         text_auto=".0f", color_discrete_sequence=["#22C55E"])
            fig.update_layout(height=260, yaxis_title=None, xaxis_title="km²",
                              title="Per provincia", **PLOT)
            st.plotly_chart(fig, width="stretch")

        st.info(
            "Il confronto che conta è tra le due strade. Le **aree agricole disponibili** sono "
            f"**{aree_fv['area2netta'].sum():,.0f} km²**: sfruttarne anche solo l'1% con un ".replace(",", ".")
            + "coefficiente di 11 m²/kW darebbe circa 1,7 GW, cioè quasi l'intero target 2030. "
            f"La **superficie impermeabilizzata** è {aree_fv['areacnkm2'].sum():,.0f} km², ".replace(",", ".")
            + "un ottavo, ma non sottrae suolo agricolo. Le **aree agricole entro 500 m da zone "
            f"industriali** — la categoria che il D.Lgs. 199/2021 indica come prioritaria — sono "
            f"solo **{aree_fv['areakmqaal'].sum():.0f} km²**: da sole non bastano."
        )

# ---- Idroelettrico: la mappa delle centrali
with tabs[7]:
    st.divider()
    centrali = D.carica_per("centrali_idro")
    if not centrali.empty:
        st.subheader("Le centrali sul territorio")
        st.caption(
            "Censimento RSE: grandi impianti (rilevazione 2020) e impianti per potenza e "
            "tipologia (2024). Non è l'intero parco regionale — il PER conta 268 impianti — "
            "ma copre le centrali con dati tecnici documentati."
        )

        c = st.columns(4)
        c[0].metric("Impianti mappati", len(centrali))
        c[1].metric("Potenza mappata", f"{centrali['potenza_mw'].sum():,.1f} MW".replace(",", "."))
        c[2].metric("Il più grande", f"{centrali['potenza_mw'].max():,.0f} MW".replace(",", "."))
        anni = centrali["anno"].dropna()
        if len(anni):
            c[3].metric("Anno mediano di costruzione", f"{int(anni.median())}")

        mappa_cen = centrali.copy()
        mappa_cen["size_mw"] = mappa_cen["potenza_mw"].fillna(0).clip(lower=0)
        fig = px.scatter_map(
            mappa_cen, lat="lat", lon="lon", size="size_mw", color="tipo",
            hover_name="nome",
            hover_data={"comune": True, "potenza_mw": ":.2f", "anno": True,
                        "salto_m": ":.0f", "lat": False, "lon": False, "size_mw": False},
            size_max=32, zoom=7.2, center={"lat": 46.3, "lon": 13.0},
            map_style="carto-positron",
            labels={"potenza_mw": "MW", "salto_m": "salto (m)"},
        )
        fig.update_layout(height=560, margin=dict(t=10, b=10, l=0, r=0),
                          legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0, title=None))
        st.plotly_chart(fig, width="stretch")

        c1, c2 = st.columns(2)
        with c1:
            per_tipo = (centrali.groupby("tipo")
                        .agg(n=("nome", "count"), mw=("potenza_mw", "sum"))
                        .reset_index().sort_values("mw"))
            fig = px.bar(per_tipo, x="mw", y="tipo", orientation="h", text="n",
                         color_discrete_sequence=["#2563EB"])
            fig.update_traces(textposition="outside", texttemplate="%{text} impianti")
            fig.update_layout(height=300, xaxis_title="MW", yaxis_title=None,
                              title="Potenza per tipologia", **PLOT)
            st.plotly_chart(fig, width="stretch")
        with c2:
            con_anno = centrali.dropna(subset=["anno"])
            if len(con_anno):
                fig = px.scatter(con_anno, x="anno", y="potenza_mw", color="tipo",
                                 hover_name="nome", log_y=True)
                fig.update_layout(height=300, xaxis_title=None, yaxis_title="MW (log)",
                                  title="Quando sono stati costruiti", showlegend=False, **PLOT)
                st.plotly_chart(fig, width="stretch")

        grandi = centrali.nlargest(8, "potenza_mw")[
            ["nome", "comune", "provincia", "potenza_mw", "tipo", "anno", "salto_m"]]
        grandi.columns = ["Impianto", "Comune", "Prov.", "MW", "Tipo", "Anno", "Salto (m)"]
        st.markdown("**Gli impianti maggiori**")
        st.dataframe(grandi.round(1), hide_index=True, width="stretch")

        vecchi = centrali[centrali["anno"] < 1960]["potenza_mw"].sum()
        st.info(
            f"Il parco è vecchio e concentrato: gli impianti costruiti prima del 1960 valgono "
            f"**{vecchi:,.0f} MW** dei {centrali['potenza_mw'].sum():,.0f} mappati. ".replace(",", ".")
            + "Accanto a poche grandi centrali a serbatoio e bacino, costruite tra gli anni "
            "Trenta e Cinquanta, c'è una lunga coda di impianti ad acqua fluente sotto il "
            "megawatt, spesso su canali e rogge. È il motivo per cui il margine di crescita "
            "è limitato: i siti buoni sono occupati da quasi un secolo."
        )

# ---- Reti: le inversioni di flusso
with tabs[4]:
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
            st.plotly_chart(fig, width="stretch")
        with c2:
            top_cab = (inv.groupby(["cabina", "provincia"])
                       .agg(sezioni=("sezione", "count"), oltre5=("oltre_5_pct", "sum"))
                       .reset_index().nlargest(10, "sezioni"))
            fig = px.bar(top_cab.sort_values("sezioni"), x="sezioni", y="cabina",
                         orientation="h", color="provincia", text="sezioni")
            fig.update_layout(height=320, yaxis_title=None, xaxis_title="sezioni",
                              title="Le cabine più interessate", **PLOT)
            st.plotly_chart(fig, width="stretch")

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

# ---- Emissioni totali regionali (scheda Termo & CO2)
with tabs[9]:
    st.divider()
    st.subheader("Le emissioni di tutta la regione, non solo dell'elettrico")
    st.caption(f"Fonte: {DOC.FONTE_EMISSIONI}.")

    em_tot_df = pd.DataFrame(DOC.EMISSIONI_TOTALI_FVG.items(), columns=["anno", "kt"])
    ultimo_anno = em_tot_df["anno"].max()
    ultimo_val = em_tot_df.loc[em_tot_df["anno"].idxmax(), "kt"]

    e = st.columns(4)
    e[0].metric(f"Gas serra totali ({ultimo_anno})", f"{ultimo_val / 1000:.1f} Mt CO₂eq")
    e[1].metric("Pro capite", f"{DOC.EMISSIONI_PRO_CAPITE_2019:.1f} t/ab",
                "tra i più alti in Italia")
    e[2].metric("Dalla macrocategoria Energia", f"{DOC.INVENTARIO_ARPA['quota_energia']}%",
                f"inventario ARPA {DOC.INVENTARIO_ARPA['anno']}")
    e[3].metric("Dal trasporto su strada", f"{DOC.INVENTARIO_ARPA['quota_trasporto_strada']}%")

    fig = px.bar(em_tot_df, x="anno", y="kt", text_auto=".0f",
                 color_discrete_sequence=["#6B7280"])
    fig.add_scatter(x=[2045], y=[0], mode="markers+text", text=["neutralità 2045"],
                    textposition="top center", marker=dict(size=14, color="#22C55E"),
                    name="Obiettivo FVGreen")
    fig.update_layout(height=380, yaxis_title="kt CO₂eq", xaxis_title=None, **PLOT)
    st.plotly_chart(fig, width="stretch")

    st.warning(
        f"Attenzione a leggerla come una serie storica: ISPRA avverte che la metodologia è "
        f"cambiata nel tempo, quindi i confronti fra anni lontani sono indicativi. "
        f"Il dato solido è l'ordine di grandezza: **{ultimo_val / 1000:.1f} Mt CO₂eq** contro "
        f"gli **{em_tot:.2f} Mt** del solo settore elettrico nel {anno}. "
        "L'elettrico è circa un decimo del problema: il resto sono trasporti, riscaldamento "
        "e combustione industriale. La Legge FVGreen fissa la neutralità al 2045, cinque anni "
        "prima del termine europeo."
    )

# ---- Fotovoltaico: la pipeline autorizzativa e il suolo
with tabs[5]:
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
            fig.update_traces(textposition="outside", texttemplate="%{text} progetti")
            fig.update_layout(showlegend=False, height=320, xaxis_title="MW", yaxis_title=None,
                              title="Potenza per stato del procedimento", **PLOT)
            st.plotly_chart(fig, width="stretch")
        with c2:
            fv = prog[prog["superficie_ha"] > 0].copy()
            fv["ha_per_mw"] = fv["superficie_ha"] / fv["potenza_mw"].replace(0, pd.NA)
            fig = px.scatter(fv.dropna(subset=["ha_per_mw"]), x="potenza_mw", y="superficie_ha",
                             color="tipo", hover_name="nome", log_x=True, log_y=True,
                             color_discrete_map={"Fotovoltaico": "#FACC15",
                                                 "Agrivoltaico": "#65A30D"})
            fig.update_layout(height=320, xaxis_title="MW (log)", yaxis_title="ettari (log)",
                              title="Potenza contro suolo occupato", **PLOT)
            st.plotly_chart(fig, width="stretch")

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
            st.plotly_chart(fig, width="stretch")

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

# ---- Bioenergie: i progetti (scheda Rinnovabili)
with tabs[6]:
    st.divider()
    bio = D.carica_per("progetti_bioenergie")
    if not bio.empty:
        st.subheader("Biomasse e biometano: i progetti in corso")
        b = st.columns(4)
        b[0].metric("Progetti", len(bio))
        b[1].metric("Potenza", f"{bio['potenza_mw'].sum():.1f} MW")
        b[2].metric("Superficie", f"{bio['superficie_ha'].sum():,.0f} ha".replace(",", "."))
        b[3].metric("Quota biometano",
                    f"{(bio['tipo'] == 'Biometano').sum()}/{len(bio)}")

        c1, c2 = st.columns([1.2, 1])
        with c1:
            mappa_bio = bio.copy()
            mappa_bio["size_ha"] = mappa_bio["superficie_ha"].fillna(0).clip(lower=0)
            fig = px.scatter_map(
                mappa_bio, lat="lat", lon="lon", size="size_ha", color="tipo",
                hover_name="nome",
                hover_data={"potenza_mw": ":.2f", "superficie_ha": ":.0f", "stato": True,
                            "lat": False, "lon": False, "size_ha": False},
                size_max=26, zoom=7.4, center={"lat": 45.95, "lon": 13.10},
                map_style="carto-positron",
                color_discrete_map={"Biometano": "#8B4513", "Biomasse": "#A16207"})
            fig.update_layout(height=400, margin=dict(t=10, b=10, l=0, r=0),
                              legend=dict(orientation="h", yanchor="bottom", y=1.01, x=0,
                                          title=None))
            st.plotly_chart(fig, width="stretch")
        with c2:
            per_tipo = bio.groupby(["tipo", "stato"]).size().reset_index(name="n")
            fig = px.bar(per_tipo, x="tipo", y="n", color="stato", text="n",
                         color_discrete_map={"Autorizzato": "#22C55E",
                                             "In istruttoria": "#F97316"})
            fig.update_layout(height=400, xaxis_title=None, yaxis_title="progetti",
                              title="Stato dei procedimenti", **PLOT)
            st.plotly_chart(fig, width="stretch")

        st.caption(
            "Il biometano domina per numero di progetti ma pesa poco in potenza elettrica: "
            "è pensato per essere immesso in rete gas o usato nei trasporti pesanti, non per "
            "produrre elettricità. Sono impianti piccoli e diffusi nella pianura agricola."
        )
