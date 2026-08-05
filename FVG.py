import streamlit as st
import pandas as pd
import plotly.express as px

# --- 1. CONFIGURAZIONE PAGINA E INTESTAZIONE ---
# Layout "wide" fondamentale per lo stile IEA
st.set_page_config(page_title="FVG Energy Data Explorer", layout="wide", page_icon="⚡")

st.title("🌍 FVG Energy Data Explorer")
st.markdown(
    """
    <div style='font-size:0.9em; color:#555; margin-top:-10px; margin-bottom:20px;'>
    Analisi dei consumi regionali e transizione energetica (Stile IEA).<br>
    Dati basati sul <b>Piano Energetico Regionale (PER)</b> del Friuli-Venezia Giulia.
    </div>
    """,
    unsafe_allow_html=True
)

# --- MAPPA COLORI COERENTE ---
color_map = {
    'Carbone': '#000000',
    'Petrolio': '#4B5563',
    'Gas Naturale': '#9CA3AF',
    'Idroelettrico': '#3B82F6',
    'Solare': '#FACC15',
    'Eolico': '#22C55E',
    'Biomasse/Geo': '#8B4513',
    'Import Elettricità': '#D1D5DB'
}

# --- 2. CARICAMENTO DATI (Mock iniziale basato sul PER FVG) ---
@st.cache_data
def load_regional_data():
    # Creiamo un dataset fittizio iniziale ma realistico per il FVG (es. in ktoe o GWh)
    # Successivamente potremo espanderlo leggendo i CSV estratti dai tuoi PDF
    anni = [2015, 2018, 2021, 2023]
    
    # Consumi primari (Dati di esempio in GWh equivalenti)
    data_primaria = []
    for y in anni:
        data_primaria.extend([
            {'Anno': y, 'Fonte': 'Gas Naturale', 'GWh': 25000 - (y-2015)*200},
            {'Anno': y, 'Fonte': 'Petrolio', 'GWh': 15000 - (y-2015)*300},
            {'Anno': y, 'Fonte': 'Carbone', 'GWh': 2000 - (y-2015)*150},
            {'Anno': y, 'Fonte': 'Idroelettrico', 'GWh': 3500 + (y-2015)*10},
            {'Anno': y, 'Fonte': 'Solare', 'GWh': 800 + (y-2015)*150},
            {'Anno': y, 'Fonte': 'Biomasse/Geo', 'GWh': 4000 + (y-2015)*50},
        ])
    df_primaria = pd.DataFrame(data_primaria)
    
    # Produzione elettrica locale vs Import
    data_elettrica = [
        {'Anno': 2023, 'Fonte': 'Termoelettrico (Gas/Bio)', 'TWh': 5.2},
        {'Anno': 2023, 'Fonte': 'Idroelettrico', 'TWh': 2.8},
        {'Anno': 2023, 'Fonte': 'Solare', 'TWh': 0.9},
        {'Anno': 2023, 'Fonte': 'Importazione', 'TWh': 3.1},
    ]
    df_elettrica = pd.DataFrame(data_elettrica)
    
    return df_primaria, df_elettrica

df_primaria, df_elettrica = load_regional_data()

# --- 3. SIDEBAR: FILTRI ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Friuli-Venezia_Giulia.svg/320px-Flag_of_Friuli-Venezia_Giulia.svg.png", width=150)
st.sidebar.header("Impostazioni Analisi")

# Selezione Anno
anni_disponibili = sorted(df_primaria['Anno'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Seleziona Anno di Riferimento:", anni_disponibili)

# Filtriamo i dati per l'anno selezionato
df_anno = df_primaria[df_primaria['Anno'] == selected_year]
totale_primaria = df_anno['GWh'].sum()
rinnovabili_primaria = df_anno[df_anno['Fonte'].isin(['Idroelettrico', 'Solare', 'Biomasse/Geo'])]['GWh'].sum()
perc_rinnovabili = (rinnovabili_primaria / totale_primaria) * 100

# --- 4. SEZIONE KPI (Stile IEA in alto) ---
st.subheader(f"Panoramica FVG - Anno {selected_year}")

# Colonne per i KPI principali
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("Fabbisogno Primario Totale", f"{totale_primaria:,.0f} GWh")
with m2:
    st.metric("Quota Rinnovabili (Primaria)", f"{perc_rinnovabili:.1f}%", f"{perc_rinnovabili - 18.0:.1f}% vs 2015")
with m3:
    st.metric("Produzione Elettrica Locale", f"{df_elettrica[df_elettrica['Fonte'] != 'Importazione']['TWh'].sum():.1f} TWh")
with m4:
    st.metric("Emissioni Stimate CO2", "12.4 Mt", "-1.2 Mt") # Placeholder per le emissioni

st.divider()

# --- 5. TABS PER L'ANALISI APPROFONDITA ---
tab_overview, tab_trend, tab_sankey = st.tabs(["📊 Overview & Mix", "📈 Transizione & Ternary", "🔄 Sankey & Flussi"])

with tab_overview:
    st.markdown("### Mix Energetico Primario")
    c1, c2 = st.columns([1, 1])
    
    with c1:
        # Grafico a torta del mix per l'anno selezionato
        fig_pie = px.pie(df_anno, values='GWh', names='Fonte', hole=0.4, 
                         color='Fonte', color_discrete_map=color_map)
        fig_pie.update_layout(margin=dict(t=0, b=0, l=0, r=0), showlegend=True)
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        # Grafico a barre andamento storico
        fig_bar = px.bar(df_primaria, x='Anno', y='GWh', color='Fonte', 
                         color_discrete_map=color_map, title="Evoluzione Consumi Primari")
        st.plotly_chart(fig_bar, use_container_width=True)

with tab_trend:
    st.info("Qui inseriremo il diagramma di Marchetti e il Ternary Plot riadattati ai dati FVG (Step 2).")

with tab_sankey:
    st.info("Qui integreremo il tuo diagramma di Sankey termodinamico (Step 3).")
