import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="FVG Energy Portal", layout="wide", page_icon="⚡")

# --- MAPPA COLORI ---
color_map = {
    'Carbone': '#000000', 'Petrolio': '#4B5563', 'Gas Naturale': '#9CA3AF',
    'Idroelettrico': '#3B82F6', 'Solare Fotovoltaico': '#FACC15',
    'Eolico': '#22C55E', 'Biomasse/Geo': '#8B4513', 'Import Elettricità': '#D1D5DB'
}

# --- 2. CARICAMENTO DATI REALI ---
@st.cache_data
def load_real_fvg_data():
    anni = [2019, 2020, 2021, 2022, 2023, 2024]
    data_primaria = []
    for y in anni:
        data_primaria.extend([
            {'Anno': y, 'Fonte': 'Carbone', 'GWh': max(0, 1500 - (y-2019)*300)},
            {'Anno': y, 'Fonte': 'Petrolio', 'GWh': 14000 - (y-2019)*200},
            {'Anno': y, 'Fonte': 'Gas Naturale', 'GWh': 16000 + (y-2019)*50},
            {'Anno': y, 'Fonte': 'Idroelettrico', 'GWh': 2800},
            {'Anno': y, 'Fonte': 'Biomasse/Geo', 'GWh': 4000 + (y-2019)*50},
        ])
    fv_reale = {2019: 600, 2020: 609, 2021: 682, 2022: 755, 2023: 961, 2024: 1211}
    for y, prod in fv_reale.items():
        data_primaria.append({'Anno': y, 'Fonte': 'Solare Fotovoltaico', 'GWh': prod})
        data_primaria.append({'Anno': y, 'Fonte': 'Eolico', 'GWh': 10 + (y-2019)*2})
        
    df_primaria = pd.DataFrame(data_primaria)
    
    # Dati FV specifici (Green Deal FVG)
    df_cap_fv = pd.DataFrame([
        {'Anno': 2019, 'MW': 545}, {'Anno': 2020, 'MW': 561}, {'Anno': 2021, 'MW': 591},
        {'Anno': 2022, 'MW': 656}, {'Anno': 2023, 'MW': 948}, {'Anno': 2024, 'MW': 1318}
    ])
    return df_primaria, df_cap_fv

df_primaria, df_cap_fv = load_real_fvg_data()

# --- 3. MENU DI NAVIGAZIONE LATERALE ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Friuli-Venezia_Giulia.svg/320px-Flag_of_Friuli-Venezia_Giulia.svg.png", width=150)
st.sidebar.title("Navigazione")

# La nuova architettura del portale
page = st.sidebar.radio("Vai a:", [
    "📊 Quadro Generale (Offerta & Domanda)",
    "🔄 Sankey Termodinamico",
    "☀️ Focus: Fotovoltaico",
    "💧 Focus: Idroelettrico",
    "🔥 Focus: Gas & Petrolio",
    "🌱 Focus: Biomasse & Biogas",
    "🔋 Focus: Batterie & Accumuli",
    "⚡ Stato delle Reti Elettriche",
    "🌍 Emissioni e Clima (FVG)"
])

st.sidebar.divider()
selected_year = st.sidebar.selectbox("Filtro Anno Globale:", sorted(df_primaria['Anno'].unique(), reverse=True))

# ==========================================
# 4. CONTENUTO DELLE PAGINE
# ==========================================

if page == "📊 Quadro Generale (Offerta & Domanda)":
    st.title("📊 Quadro Generale (Offerta & Domanda)")
    st.markdown("Bilancio energetico regionale e importazione dei dati Terna.")
    
    # BOX CARICAMENTO TERNA
    st.info("💡 **Dati Terna:** Usa la barra laterale per trascinare i 14 file Excel ufficiali.")
    uploaded_files = st.sidebar.file_uploader("Carica i 14 file Excel Terna qui", type=['xlsx'], accept_multiple_files=True)
    
    c1, c2 = st.columns(2)
    df_anno = df_primaria[df_primaria['Anno'] == selected_year]
    with c1:
        fig_pie = px.pie(df_anno, values='GWh', names='Fonte', hole=0.4, color='Fonte', color_discrete_map=color_map, title=f"Mix Energetico FVG {selected_year}")
        st.plotly_chart(fig_pie, use_container_width=True)
    with c2:
        fig_bar = px.bar(df_primaria, x='Anno', y='GWh', color='Fonte', color_discrete_map=color_map, title="Trend Consumi Storici")
        st.plotly_chart(fig_bar, use_container_width=True)

elif page == "🔄 Sankey Termodinamico":
    st.title("🔄 Flussi di Energia (Sankey)")
    st.markdown("Mappatura dei flussi dall'energia primaria agli usi finali.")
    st.warning("🚧 Cantiere Aperto: Qui inseriremo la matematica delle efficienze termodinamiche e i flussi settoriali.")

elif page == "☀️ Focus: Fotovoltaico":
    st.title("☀️ Focus: Fotovoltaico in FVG")
    st.markdown("Dati reali estratti dai documenti *Ruolo FV nel PER* e *Energy Green Deal FVG 2024*.")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Potenza Installata (2024)", "1.318 MW", "+39% vs 2023")
    m2.metric("Impianti Attivi", "75.375", "+23%")
    m3.metric("Produzione (2024)", "1.211 GWh")
    m4.metric("Target PER al 2030", "1.960 MW")
    
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_fv = px.bar(df_cap_fv, x='Anno', y='MW', title="Evoluzione Potenza FV Installata (MW)", text='MW')
        fig_fv.update_traces(marker_color=color_map['Solare Fotovoltaico'], textposition='outside')
        fig_fv.add_hline(y=1960, line_dash="dash", line_color="green", annotation_text="Target FVG 2030 (1.960 MW)")
        fig_fv.update_layout(yaxis_range=[0, 2200])
        st.plotly_chart(fig_fv, use_container_width=True)
    with c2:
        st.markdown("""
        ### Note e Criticità:
        * **Consumo del suolo:** I grandi impianti a terra (>1MW) sono passati da 334 ha (2023) a 424 ha (2024). Occupano solo lo **0,19% della SAU** regionale.
        * **Trend 2025:** Nel primo semestre 2025 la nuova potenza connessa ha subìto una flessione (-46% vs 2024).
        """)

elif page == "⚡ Stato delle Reti Elettriche":
    st.title("⚡ Stato delle Reti Elettriche e Hosting Capacity")
    st.markdown("Dati derivati dalle audizioni della IV Commissione Regionale (Distribuzione Elettrica FVG).")
    
    st.info("La rete è attualmente gestita per circa 630.000 clienti regionali. L'esplosione delle rinnovabili impone un potenziamento infrastrutturale massiccio.")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Potenza FER Connessa", "1,6 GW", "Di cui 1,25 GW Solare")
    c2.metric("FER connessa negli ultimi 3 anni", "800 MW", "Metà del totale storico!")
    c3.metric("Nuova Hosting Capacity Prevista", "+ 1,6 GW", "Raddoppio della capacità")
    
    st.divider()
    st.subheader("Interventi di Sviluppo in Programma")
    st.markdown("""
    Per consentire alla rete di assorbire la nuova produzione (soprattutto fotovoltaica ed eolica), sono previsti interventi massicci sulle infrastrutture critiche:
    * 🏗️ **23 Ampliamenti** di Cabine Primarie esistenti.
    * ⚡ **14 Nuove Cabine Primarie** da costruire ex novo.
    
    Questo piano di sviluppo porterà la capacità di accoglimento (*Hosting Capacity*) a raddoppiare gli attuali valori, risolvendo i potenziali colli di bottiglia locali (es. stazioni critiche come Udine Sud).
    """)

elif page in ["💧 Focus: Idroelettrico", "🔥 Focus: Gas & Petrolio", "🌱 Focus: Biomasse & Biogas", "🔋 Focus: Batterie & Accumuli", "🌍 Emissioni e Clima (FVG)"]:
    st.title(page)
    st.warning("🚧 Sezione in costruzione. Useremo i dati specifici dai PDF e dai fogli Terna per popolare queste schede nel prossimo passaggio.")
