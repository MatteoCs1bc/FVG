import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. CONFIGURAZIONE PAGINA E INTESTAZIONE ---
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

# --- MAPPA COLORI ---
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

# --- 2. CARICAMENTO DATI (Dati storici estesi per FVG) ---
@st.cache_data
def load_regional_data():
    # Simulazione trend storico e proiezioni PER FVG (2000 - 2030)
    anni = list(range(2000, 2031, 5))
    data_primaria = []
    
    for y in anni:
        # Dinamiche di sostituzione (Carbone sparisce, Gas fa da ponte, Rinnovabili salgono)
        carbone = max(0, 4000 - (y-2000)*150)
        petrolio = max(10000, 18000 - (y-2000)*250)
        gas = 15000 + (y-2000)*100 if y < 2020 else 17000 - (y-2020)*300
        idro = 3500 + (y-2000)*15
        solare = 0 if y < 2010 else (y-2010)*150
        eolico = 0 if y < 2015 else (y-2015)*30
        bio = 2000 + (y-2000)*100
        
        data_primaria.extend([
            {'Anno': y, 'Fonte': 'Carbone', 'GWh': carbone},
            {'Anno': y, 'Fonte': 'Petrolio', 'GWh': petrolio},
            {'Anno': y, 'Fonte': 'Gas Naturale', 'GWh': gas},
            {'Anno': y, 'Fonte': 'Idroelettrico', 'GWh': idro},
            {'Anno': y, 'Fonte': 'Solare', 'GWh': solare},
            {'Anno': y, 'Fonte': 'Eolico', 'GWh': eolico},
            {'Anno': y, 'Fonte': 'Biomasse/Geo', 'GWh': bio},
        ])
    
    df_primaria = pd.DataFrame(data_primaria)
    
    # Elettricità fissa per l'anno di overview
    data_elettrica = [
        {'Anno': 2025, 'Fonte': 'Termoelettrico (Gas/Bio)', 'TWh': 5.0},
        {'Anno': 2025, 'Fonte': 'Idroelettrico', 'TWh': 3.0},
        {'Anno': 2025, 'Fonte': 'Solare', 'TWh': 1.2},
        {'Anno': 2025, 'Fonte': 'Importazione', 'TWh': 2.8},
    ]
    df_elettrica = pd.DataFrame(data_elettrica)
    
    return df_primaria, df_elettrica

df_primaria, df_elettrica = load_regional_data()

# --- 3. SIDEBAR: FILTRI ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Friuli-Venezia_Giulia.svg/320px-Flag_of_Friuli-Venezia_Giulia.svg.png", width=150)
st.sidebar.header("Impostazioni Analisi")

anni_disponibili = sorted(df_primaria['Anno'].unique(), reverse=True)
selected_year = st.sidebar.selectbox("Seleziona Anno di Riferimento:", anni_disponibili)

df_anno = df_primaria[df_primaria['Anno'] == selected_year]
totale_primaria = df_anno['GWh'].sum()
rinnovabili_primaria = df_anno[df_anno['Fonte'].isin(['Idroelettrico', 'Solare', 'Eolico', 'Biomasse/Geo'])]['GWh'].sum()
perc_rinnovabili = (rinnovabili_primaria / totale_primaria) * 100 if totale_primaria > 0 else 0

# --- 4. KPI ---
st.subheader(f"Panoramica FVG - Anno {selected_year}")
m1, m2, m3, m4 = st.columns(4)
m1.metric("Fabbisogno Primario", f"{totale_primaria/1000:,.1f} TWh")
m2.metric("Quota Rinnovabili", f"{perc_rinnovabili:.1f}%")
m3.metric("Generazione Elettrica", f"{df_elettrica[df_elettrica['Fonte'] != 'Importazione']['TWh'].sum():.1f} TWh")
m4.metric("Dato di Riferimento", "Step 2 Attivo")
st.divider()

# --- 5. TABS ---
tab_overview, tab_trend, tab_sankey = st.tabs(["📊 Overview & Mix", "📈 Transizione (Marchetti & Ternario)", "🔄 Sankey & Flussi"])

with tab_overview:
    c1, c2 = st.columns([1, 1])
    with c1:
        st.markdown("### Mix Energetico Primario")
        fig_pie = px.pie(df_anno, values='GWh', names='Fonte', hole=0.4, color='Fonte', color_discrete_map=color_map)
        fig_pie.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_pie, use_container_width=True)
        
    with c2:
        st.markdown("### Evoluzione Consumi Primari")
        fig_bar = px.bar(df_primaria, x='Anno', y='GWh', color='Fonte', color_discrete_map=color_map)
        fig_bar.update_layout(margin=dict(t=30, b=0, l=0, r=0))
        st.plotly_chart(fig_bar, use_container_width=True)

with tab_trend:
    c_m1, c_m2 = st.columns(2)
    
    with c_m1:
        st.subheader("Competizione tra Fonti (Marchetti)")
        st.markdown("Asse Y: $ \log_{10}(f / (1-f)) $ dove $ f $ è la quota di mercato.")
        
        # Calcolo per Marchetti
        df_march = df_primaria.copy()
        tot_y = df_march.groupby('Anno')['GWh'].sum().reset_index().rename(columns={'GWh':'Total'})
        df_march = pd.merge(df_march, tot_y, on='Anno')
        df_march = df_march[df_march['Total'] > 0]
        
        # Frazione f e limite per evitare log(0)
        df_march['f'] = np.clip(df_march['GWh'] / df_march['Total'], 0.0001, 0.9999)
        df_march['Marchetti'] = np.log10(df_march['f'] / (1 - df_march['f']))
        
        fig_m = px.line(df_march, x='Anno', y='Marchetti', color='Fonte', color_discrete_map=color_map, markers=True)
        fig_m.update_layout(yaxis_title="log(f / 1-f)", margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig_m, use_container_width=True)

    with c_m2:
        st.subheader("Rotta dell'Elettrificazione (Ternario)")
        st.markdown("Evoluzione del mix: Fossili vs Elettroni vs Biomasse.")
        
        # Preparazione dati Ternario
        pivot_df = df_primaria.pivot_table(index='Anno', columns='Fonte', values='GWh', aggfunc='sum').fillna(0)
        pivot_df['Total'] = pivot_df.sum(axis=1)
        pivot_df['Fossil'] = pivot_df.get('Carbone',0) + pivot_df.get('Gas Naturale',0) + pivot_df.get('Petrolio',0)
        pivot_df['Bio & Other'] = pivot_df.get('Biomasse/Geo',0)
        pivot_df['Electrons'] = pivot_df.get('Idroelettrico',0) + pivot_df.get('Solare',0) + pivot_df.get('Eolico',0)
        
        # Percentuali
        for col in ['Fossil', 'Bio & Other', 'Electrons']:
            pivot_df[col] = (pivot_df[col] / pivot_df['Total']) * 100
            
        pivot_df = pivot_df.reset_index()
        
        fig_t = px.scatter_ternary(pivot_df, a="Fossil", b="Electrons", c="Bio & Other", 
                                   hover_name="Anno", color="Anno", color_continuous_scale="Viridis")
        fig_t.update_traces(mode="lines+markers", line=dict(color='#22C55E', width=2), marker=dict(size=8))
        fig_t.update_layout(margin=dict(t=20, b=0, l=0, r=0))
        st.plotly_chart(fig_t, use_container_width=True)

with tab_sankey:
    st.info("Step 3: Qui integreremo il diagramma di Sankey termodinamico mappando le efficienze!")
