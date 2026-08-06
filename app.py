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
    "🌱 Rinnovabili",
    "💧 Idroelettrico",
    "🔥 Termo & CO₂",
    "🔮 Scenari",
    "🌡️ Clima",
    "📈 Transizione",
    "🗂 Dati",
])

# ================================================================ 1. PANORAMICA
with tabs[0]:
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
with tabs[5]:
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
with tabs[7]:
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
with tabs[10]:
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
with tabs[11]:
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
with tabs[8]:
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
with tabs[6]:
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
with tabs[9]:
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
