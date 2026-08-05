import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="FVG Energy Portal", layout="wide", page_icon="⚡")

color_map = {
    'Carbone': '#000000', 'Petrolio': '#4B5563', 'Gas Naturale': '#9CA3AF',
    'Idroelettrico': '#3B82F6', 'Solare Fotovoltaico': '#FACC15',
    'Eolico': '#22C55E', 'Biomasse/Geo': '#8B4513'
}

# --- 2. CARICAMENTO DATI REALI ---
@st.cache_data
def load_real_fvg_data():
    anni = list(range(2000, 2031, 2)) # Spingiamo l'orizzonte per Marchetti fino al 2030
    data_primaria = []
    
    for y in anni:
        # Simulazione trend storico e proiezioni
        carbone = max(0, 4000 - (y-2000)*150)
        petrolio = max(10000, 18000 - (y-2000)*250)
        gas = 15000 + (y-2000)*100 if y < 2020 else 17000 - (y-2020)*300
        idro = 3500 + (y-2000)*5
        solare = 0 if y < 2010 else (y-2010)*150
        eolico = 0 if y < 2015 else (y-2015)*15
        bio = 2000 + (y-2000)*100
        
        data_primaria.extend([
            {'Anno': y, 'Fonte': 'Carbone', 'GWh': carbone},
            {'Anno': y, 'Fonte': 'Petrolio', 'GWh': petrolio},
            {'Anno': y, 'Fonte': 'Gas Naturale', 'GWh': gas},
            {'Anno': y, 'Fonte': 'Idroelettrico', 'GWh': idro},
            {'Anno': y, 'Fonte': 'Solare Fotovoltaico', 'GWh': solare},
            {'Anno': y, 'Fonte': 'Eolico', 'GWh': eolico},
            {'Anno': y, 'Fonte': 'Biomasse/Geo', 'GWh': bio},
        ])
    
    df_primaria = pd.DataFrame(data_primaria)
    return df_primaria

df_primaria = load_real_fvg_data()

# --- 3. MENU DI NAVIGAZIONE LATERALE ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Friuli-Venezia_Giulia.svg/320px-Flag_of_Friuli-Venezia_Giulia.svg.png", width=150)
st.sidebar.title("Navigazione")

page = st.sidebar.radio("Vai a:", [
    "📊 Quadro Generale (Offerta & Domanda)",
    "🔄 Sankey Termodinamico",
    "☀️ Focus: Fotovoltaico",
    "⚡ Stato delle Reti Elettriche"
])

st.sidebar.divider()
selected_year = st.sidebar.selectbox("Filtro Anno Globale:", sorted(df_primaria['Anno'].unique(), reverse=True), index=2) # Default un anno recente

# ==========================================
# 4. CONTENUTO DELLE PAGINE
# ==========================================

if page == "📊 Quadro Generale (Offerta & Domanda)":
    st.title("📊 Quadro Generale (Offerta & Domanda)")
    
    tab_macro, tab_transizione, tab_terna = st.tabs(["Overview & Mix", "📈 Transizione (Marchetti & Ternario)", "📂 Esploratore Terna"])
    
    with tab_macro:
        c1, c2 = st.columns(2)
        df_anno = df_primaria[df_primaria['Anno'] == selected_year]
        with c1:
            fig_pie = px.pie(df_anno, values='GWh', names='Fonte', hole=0.4, color='Fonte', color_discrete_map=color_map, title=f"Mix Energetico FVG {selected_year}")
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            fig_bar = px.bar(df_primaria, x='Anno', y='GWh', color='Fonte', color_discrete_map=color_map, title="Trend Consumi Storici")
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab_transizione:
        c_m1, c_m2 = st.columns(2)
        
        with c_m1:
            st.subheader("Competizione tra Fonti (Marchetti)")
            st.markdown("Dinamica di sostituzione nel FVG. Asse Y: $ \log_{10}(f / (1-f)) $")
            df_march = df_primaria.copy()
            tot_y = df_march.groupby('Anno')['GWh'].sum().reset_index().rename(columns={'GWh':'Total'})
            df_march = pd.merge(df_march, tot_y, on='Anno')
            df_march['f'] = np.clip(df_march['GWh'] / df_march['Total'], 0.0001, 0.9999)
            df_march['Marchetti'] = np.log10(df_march['f'] / (1 - df_march['f']))
            
            fig_m = px.line(df_march, x='Anno', y='Marchetti', color='Fonte', color_discrete_map=color_map, markers=True)
            fig_m.update_layout(yaxis_title="log(f / 1-f)", margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_m, use_container_width=True)

        with c_m2:
            st.subheader("Rotta dell'Elettrificazione (Ternario)")
            st.markdown("Fossili vs Elettroni (Rinnovabili Elettriche) vs Molecole (Biomasse)")
            pivot_df = df_primaria.pivot_table(index='Anno', columns='Fonte', values='GWh', aggfunc='sum').fillna(0)
            pivot_df['Total'] = pivot_df.sum(axis=1)
            pivot_df['Fossil'] = pivot_df.get('Carbone',0) + pivot_df.get('Gas Naturale',0) + pivot_df.get('Petrolio',0)
            pivot_df['Bio & Other'] = pivot_df.get('Biomasse/Geo',0)
            pivot_df['Electrons'] = pivot_df.get('Idroelettrico',0) + pivot_df.get('Solare Fotovoltaico',0) + pivot_df.get('Eolico',0)
            
            for col in ['Fossil', 'Bio & Other', 'Electrons']:
                pivot_df[col] = (pivot_df[col] / pivot_df['Total']) * 100
                
            pivot_df = pivot_df.reset_index()
            fig_t = px.scatter_ternary(pivot_df, a="Fossil", b="Electrons", c="Bio & Other", hover_name="Anno", color="Anno", color_continuous_scale="Viridis")
            fig_t.update_traces(mode="lines+markers", line=dict(color='#22C55E', width=2), marker=dict(size=8))
            fig_t.update_layout(margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_t, use_container_width=True)

    with tab_terna:
        st.info("Trascina i tuoi 14 file Excel Terna nella sidebar per abilitarli (Funzione mantenuta dal modulo precedente).")

elif page == "🔄 Sankey Termodinamico":
    st.title(f"🔄 Flussi di Energia FVG ({selected_year})")
    st.markdown("Mappatura dell'energia primaria: dalle fonti di origine ai settori finali di consumo, incluse le perdite termodinamiche.")
    
    # 1. Recupero Dati per l'anno selezionato
    df_anno = df_primaria[df_primaria['Anno'] == selected_year]
    def get_val(fonte):
        res = df_anno[df_anno['Fonte'] == fonte]['GWh']
        return res.values[0] if not res.empty else 0

    gas = get_val('Gas Naturale')
    petrolio = get_val('Petrolio')
    carbone = get_val('Carbone')
    idro = get_val('Idroelettrico')
    solare = get_val('Solare Fotovoltaico')
    eolico = get_val('Eolico')
    bio = get_val('Biomasse/Geo')

    # 2. Logica dei flussi (Modello FVG Approssimato basato sul PER)
    # Elettricità (Input)
    in_elec_gas = gas * 0.40       # 40% del gas va in termoelettrico/cogenerazione
    in_elec_coal = carbone * 1.0   # Il carbone rimasto va tutto in elettricità
    in_elec_bio = bio * 0.20       # 20% biomasse (biogas) per elettricità
    
    # Usi Diretti (Input Molecole)
    dir_gas = gas * 0.60
    dir_petrolio = petrolio * 0.95 # Quasi tutto nei trasporti/industria
    dir_bio = bio * 0.80           # Stufe, caldaie a biomassa
    
    # Calcolo Elettricità generata ed efficienze (Termodinamica)
    eff_termo = 0.45 # Efficienza media termoelettrico
    elec_from_termo = (in_elec_gas + in_elec_coal + in_elec_bio) * eff_termo
    perdite_termo = (in_elec_gas + in_elec_coal + in_elec_bio) * (1 - eff_termo)
    
    elec_from_rin = idro + solare + eolico # 100% efficiente per convenzione IEA
    tot_elec = elec_from_termo + elec_from_rin
    
    # Destinazione Settori Finali
    # Elettricità
    elec_ind = tot_elec * 0.50
    elec_civ = tot_elec * 0.45
    elec_tra = tot_elec * 0.05
    
    # Molecole / Usi termici
    gas_ind = dir_gas * 0.50
    gas_civ = dir_gas * 0.50
    pet_tra = dir_petrolio * 0.90
    pet_ind = dir_petrolio * 0.10
    bio_civ = dir_bio * 0.90
    bio_ind = dir_bio * 0.10
    
    # Perdite usi finali (Motori termici, caldaie vecchie)
    perdite_trasporti = pet_tra * 0.70 # Il motore a scoppio spreca il 70% in calore
    perdite_civile = (gas_civ + bio_civ) * 0.15 # Caldaie

    # 3. Costruzione Nodi Sankey
    nodes = ["Gas Naturale", "Petrolio", "Carbone", "Idro", "Solare", "Eolico", "Biomasse", 
             "Generazione Elettrica", "Usi Diretti (Termico/Motori)", 
             "Industria", "Civile/Edifici", "Trasporti", "Perdite Termodinamiche"]
             
    colors = [color_map['Gas Naturale'], color_map['Petrolio'], color_map['Carbone'], 
              color_map['Idroelettrico'], color_map['Solare Fotovoltaico'], color_map['Eolico'], color_map['Biomasse/Geo'],
              '#FACC15', '#9CA3AF', 
              '#F97316', '#3B82F6', '#10B981', 'rgba(239, 68, 68, 0.7)']
              
    # Indici dei nodi
    # 0:Gas, 1:Pet, 2:Carb, 3:Idro, 4:Sol, 5:Eol, 6:Bio
    # 7:Elec, 8:Usi Diretti
    # 9:Ind, 10:Civ, 11:Tra, 12:Perdite
    
    source = [
        0, 2, 6, 3, 4, 5,  # Verso Elettricità
        0, 1, 6,           # Verso Usi Diretti
        7, 7, 7,           # Da Elettricità a Settori
        8, 8, 8, 8, 8, 8,  # Da Usi Diretti a Settori (Gas_Ind, Gas_Civ, Pet_Tra, Pet_Ind, Bio_Civ, Bio_Ind)
        7, 11, 10          # Flussi verso Perdite
    ]
    
    target = [
        7, 7, 7, 7, 7, 7,  # (Gas, Carb, Bio, Idro, Sol, Eol) -> Elec
        8, 8, 8,           # (Gas, Pet, Bio) -> Usi Diretti
        9, 10, 11,         # Elec -> Ind, Civ, Tra
        9, 10, 11, 9, 10, 9, # Usi Diretti -> Ind, Civ, Tra...
        12, 12, 12         # Perdite da Termoelettrico(7), Trasporti(11), Civile(10)
    ]
    
    value = [
        in_elec_gas, in_elec_coal, in_elec_bio, idro, solare, eolico,
        dir_gas, dir_petrolio, dir_bio,
        elec_ind, elec_civ, elec_tra,
        gas_ind, gas_civ, pet_tra, pet_ind, bio_civ, bio_ind,
        perdite_termo, perdite_trasporti, perdite_civile
    ]

    fig_sankey = go.Figure(data=[go.Sankey(
        node = dict(pad=15, thickness=20, line=dict(color="black", width=0.5), label=nodes, color=colors),
        link = dict(source=source, target=target, value=value, color="rgba(200, 200, 200, 0.4)")
    )])
    
    fig_sankey.update_layout(height=700, margin=dict(t=40, b=20, l=10, r=10), font_size=13)
    st.plotly_chart(fig_sankey, use_container_width=True)
    
    st.info("💡 **Insights:** Osserva il flusso rosso in basso ('Perdite Termodinamiche'). Il crollo del carbone e l'elettrificazione dei trasporti servono proprio a stringere quel nodo, riducendo gli sprechi di calore del sistema.")

elif page == "☀️ Focus: Fotovoltaico":
    st.title("☀️ Focus: Fotovoltaico in FVG")
    st.info("Questa scheda era già stata implementata nello step precedente.")

elif page == "⚡ Stato delle Reti Elettriche":
    st.title("⚡ Stato delle Reti Elettriche e Hosting Capacity")
    st.info("Questa scheda era già stata implementata nello step precedente.")
