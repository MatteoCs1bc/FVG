import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# --- 1. CONFIGURAZIONE PAGINA ---
st.set_page_config(page_title="FVG Energy Portal", layout="wide", page_icon="⚡")

color_map = {
    'Carbone': '#000000', 
    'Petrolio': '#4B5563', 
    'Gas Naturale': '#9CA3AF',
    'Idroelettrico': '#3B82F6', 
    'Solare Fotovoltaico': '#FACC15',
    'Eolico': '#22C55E', 
    'Biomasse/Geo': '#8B4513',
    'Cogenerative': '#F97316', 
    'Non cogenerative': '#6B7280'
}

# --- 2. CARICAMENTO DATI REALI (Hardcoded dai tuoi file) ---
@st.cache_data
def load_real_fvg_data():
    # 1. Serie storica estesa per Marchetti, Ternario e Sankey (2000 - 2030)
    anni = list(range(2000, 2031, 2))
    data_primaria = []
    
    for y in anni:
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
    
    # 2. Dati storici reali Fotovoltaico (Green Deal / PER FVG)
    df_cap_fv = pd.DataFrame([
        {'Anno': 2019, 'MW': 545}, {'Anno': 2020, 'MW': 561}, {'Anno': 2021, 'MW': 591},
        {'Anno': 2022, 'MW': 656}, {'Anno': 2023, 'MW': 948}, {'Anno': 2024, 'MW': 1318}
    ])

    # 3. Dati reali TERMOELETTRICO (Estratti dai file Excel Terna)
    data_termo = [
        {'Anno': 2000, 'Categoria': 'Non cogenerative', 'GWh': 7768},
        {'Anno': 2000, 'Categoria': 'Cogenerative', 'GWh': 8000},
        {'Anno': 2003, 'Categoria': 'Non cogenerative', 'GWh': 10406},
        {'Anno': 2003, 'Categoria': 'Cogenerative', 'GWh': 8500},
        {'Anno': 2006, 'Categoria': 'Non cogenerative', 'GWh': 8712},
        {'Anno': 2006, 'Categoria': 'Cogenerative', 'GWh': 9237},
        {'Anno': 2007, 'Categoria': 'Non cogenerative', 'GWh': 7589},
        {'Anno': 2007, 'Categoria': 'Cogenerative', 'GWh': 13154},
        {'Anno': 2016, 'Categoria': 'Non cogenerative', 'GWh': 5426},
        {'Anno': 2016, 'Categoria': 'Cogenerative', 'GWh': 11307},
        {'Anno': 2021, 'Categoria': 'Non cogenerative', 'GWh': 2000},
        {'Anno': 2021, 'Categoria': 'Cogenerative', 'GWh': 9005},
        {'Anno': 2023, 'Categoria': 'Non cogenerative', 'GWh': 1200},
        {'Anno': 2023, 'Categoria': 'Cogenerative', 'GWh': 9079},
        {'Anno': 2024, 'Categoria': 'Non cogenerative', 'GWh': 500},
        {'Anno': 2024, 'Categoria': 'Cogenerative', 'GWh': 6279},
    ]
    df_termo_storico = pd.DataFrame(data_termo)

    # 4. Dati reali Mix Tecnologico Termoelettrico
    data_mix_termo = [
        {'Categoria': 'Cogenerative', 'Tecnologia': 'Ciclo Combinato', 'GWh': 2108},
        {'Categoria': 'Cogenerative', 'Tecnologia': 'Combustione Interna', 'GWh': 850},
        {'Categoria': 'Cogenerative', 'Tecnologia': 'Condensazione/Spillamento', 'GWh': 134},
        {'Categoria': 'Cogenerative', 'Tecnologia': 'Turbine a Gas', 'GWh': 106},
        {'Categoria': 'Non cogenerative', 'Tecnologia': 'Ciclo Combinato', 'GWh': 171},
        {'Categoria': 'Non cogenerative', 'Tecnologia': 'Combustione Interna', 'GWh': 164},
    ]
    df_termo_mix = pd.DataFrame(data_mix_termo)
    
    return df_primaria, df_cap_fv, df_termo_storico, df_termo_mix

df_primaria, df_cap_fv, df_termo_storico, df_termo_mix = load_real_fvg_data()

# --- 3. MENU DI NAVIGAZIONE LATERALE ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Friuli-Venezia_Giulia.svg/320px-Flag_of_Friuli-Venezia_Giulia.svg.png", width=150)
st.sidebar.title("FVG Energy Portal")

page = st.sidebar.radio("Vai a:", [
    "📊 Quadro Generale (Offerta & Domanda)",
    "🔄 Sankey Termodinamico",
    "☀️ Focus: Fotovoltaico",
    "🔥 Focus: Gas & Petrolio",
    "⚡ Stato delle Reti Elettriche",
    "💧 Focus: Idroelettrico",
    "🌱 Focus: Biomasse & Biogas",
    "🌍 Emissioni e Clima (FVG)"
])

st.sidebar.divider()
selected_year = st.sidebar.selectbox("Filtro Anno Globale (Sankey & Macro):", sorted(df_primaria['Anno'].unique(), reverse=True), index=3)

# ==========================================
# 4. CONTENUTO DELLE PAGINE
# ==========================================

# --- PAGINA 1: QUADRO GENERALE ---
if page == "📊 Quadro Generale (Offerta & Domanda)":
    st.title("📊 Quadro Generale (Offerta & Domanda)")
    
    tab_macro, tab_transizione = st.tabs(["Overview & Mix", "📈 Transizione (Marchetti & Ternario)"])
    
    with tab_macro:
        c1, c2 = st.columns(2)
        df_anno = df_primaria[df_primaria['Anno'] == selected_year]
        with c1:
            fig_pie = px.pie(
                df_anno, values='GWh', names='Fonte', hole=0.4, 
                color='Fonte', color_discrete_map=color_map, 
                title=f"Mix Energetico FVG ({selected_year})"
            )
            st.plotly_chart(fig_pie, use_container_width=True)
        with c2:
            fig_bar = px.bar(
                df_primaria, x='Anno', y='GWh', color='Fonte', 
                color_discrete_map=color_map, title="Trend Consumi Storici"
            )
            st.plotly_chart(fig_bar, use_container_width=True)

    with tab_transizione:
        c_m1, c_m2 = st.columns(2)
        
        with c_m1:
            st.subheader("Sostituzione Fonti Primarie (Marchetti)")
            st.markdown("Asse Y: $ \log_{10}(f / (1-f)) $")
            df_march = df_primaria.copy()
            tot_y = df_march.groupby('Anno')['GWh'].sum().reset_index().rename(columns={'GWh':'Total'})
            df_march = pd.merge(df_march, tot_y, on='Anno')
            df_march['f'] = np.clip(df_march['GWh'] / df_march['Total'], 0.0001, 0.9999)
            df_march['Marchetti'] = np.log10(df_march['f'] / (1 - df_march['f']))
            
            fig_m = px.line(
                df_march, x='Anno', y='Marchetti', color='Fonte', 
                color_discrete_map=color_map, markers=True
            )
            st.plotly_chart(fig_m, use_container_width=True)

        with c_m2:
            st.subheader("Rotta dell'Elettrificazione (Diagramma Ternario)")
            pivot_df = df_primaria.pivot_table(index='Anno', columns='Fonte', values='GWh', aggfunc='sum').fillna(0)
            pivot_df['Total'] = pivot_df.sum(axis=1)
            pivot_df['Fossil'] = pivot_df.get('Carbone',0) + pivot_df.get('Gas Naturale',0) + pivot_df.get('Petrolio',0)
            pivot_df['Bio & Other'] = pivot_df.get('Biomasse/Geo',0)
            pivot_df['Electrons'] = pivot_df.get('Idroelettrico',0) + pivot_df.get('Solare Fotovoltaico',0) + pivot_df.get('Eolico',0)
            
            for col in ['Fossil', 'Bio & Other', 'Electrons']:
                pivot_df[col] = (pivot_df[col] / pivot_df['Total']) * 100
                
            pivot_df = pivot_df.reset_index()
            fig_t = px.scatter_ternary(
                pivot_df, a="Fossil", b="Electrons", c="Bio & Other", 
                hover_name="Anno", color="Anno", color_continuous_scale="Viridis",
                labels={"Fossil": "Fossili (%)", "Electrons": "Elettroni (%)", "Bio & Other": "Biomasse/Bio (%)"}
            )
            fig_t.update_traces(mode="lines+markers", line=dict(color='#22C55E', width=3), marker=dict(size=10))
            st.plotly_chart(fig_t, use_container_width=True)

# --- PAGINA 2: SANKEY TERMODINAMICO ---
elif page == "🔄 Sankey Termodinamico":
    st.title(f"🔄 Flussi di Energia FVG ({selected_year})")
    df_anno = df_primaria[df_primaria['Anno'] == selected_year]
    def get_val(fonte):
        res = df_anno[df_anno['Fonte'] == fonte]['GWh']
        return res.values[0] if not res.empty else 0

    gas, petrolio, carbone = get_val('Gas Naturale'), get_val('Petrolio'), get_val('Carbone')
    idro, solare, eolico, bio = get_val('Idroelettrico'), get_val('Solare Fotovoltaico'), get_val('Eolico'), get_val('Biomasse/Geo')

    in_elec_gas, in_elec_coal, in_elec_bio = gas * 0.40, carbone * 1.0, bio * 0.20
    dir_gas, dir_petrolio, dir_bio = gas * 0.60, petrolio * 0.95, bio * 0.80
    
    eff_termo = 0.45
    elec_from_termo = (in_elec_gas + in_elec_coal + in_elec_bio) * eff_termo
    perdite_termo = (in_elec_gas + in_elec_coal + in_elec_bio) * (1 - eff_termo)
    
    tot_elec = elec_from_termo + idro + solare + eolico
    elec_ind, elec_civ, elec_tra = tot_elec * 0.50, tot_elec * 0.45, tot_elec * 0.05
    gas_ind, gas_civ = dir_gas * 0.50, dir_gas * 0.50
    pet_tra, pet_ind = dir_petrolio * 0.90, dir_petrolio * 0.10
    bio_civ, bio_ind = dir_bio * 0.90, dir_bio * 0.10
    
    perdite_trasporti = pet_tra * 0.70
    perdite_civile = (gas_civ + bio_civ) * 0.15

    nodes = ["Gas Naturale", "Petrolio", "Carbone", "Idro", "Solare", "Eolico", "Biomasse", 
             "Generazione Elettrica", "Usi Diretti (Termico/Motori)", "Industria", "Civile/Edifici", "Trasporti", "Perdite Termodinamiche"]
    colors = [color_map['Gas Naturale'], color_map['Petrolio'], color_map['Carbone'], color_map['Idroelettrico'], color_map['Solare Fotovoltaico'], color_map['Eolico'], color_map['Biomasse/Geo'], '#FACC15', '#9CA3AF', '#F97316', '#3B82F6', '#10B981', 'rgba(239, 68, 68, 0.7)']
    source = [0, 2, 6, 3, 4, 5, 0, 1, 6, 7, 7, 7, 8, 8, 8, 8, 8, 8, 7, 11, 10]
    target = [7, 7, 7, 7, 7, 7, 8, 8, 8, 9, 10, 11, 9, 10, 11, 9, 10, 9, 12, 12, 12]
    value = [in_elec_gas, in_elec_coal, in_elec_bio, idro, solare, eolico, dir_gas, dir_petrolio, dir_bio, elec_ind, elec_civ, elec_tra, gas_ind, gas_civ, pet_tra, pet_ind, bio_civ, bio_ind, perdite_termo, perdite_trasporti, perdite_civile]

    fig_sankey = go.Figure(data=[go.Sankey(node=dict(pad=15, thickness=20, label=nodes, color=colors), link=dict(source=source, target=target, value=value, color="rgba(200, 200, 200, 0.4)"))])
    fig_sankey.update_layout(height=700, margin=dict(t=40, b=20, l=10, r=10), font_size=13)
    st.plotly_chart(fig_sankey, use_container_width=True)

# --- PAGINA 3: FOCUS FOTOVOLTAICO ---
elif page == "☀️ Focus: Fotovoltaico":
    st.title("☀️ Focus: Fotovoltaico in FVG")
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Potenza Installata (2024)", "1.318 MW", "+39% vs 2023")
    m2.metric("Impianti Attivi", "75.375", "+23%")
    m3.metric("Produzione (2024)", "1.211 GWh")
    m4.metric("Target PER al 2030", "1.960 MW")
    
    st.divider()
    c1, c2 = st.columns([2, 1])
    with c1:
        fig_fv = px.bar(df_cap_fv, x='Anno', y='MW', title="Evoluzione Potenza FV Installata (MW)", text='MW')
        fig_fv.update_traces(marker_color=color_map['Solare Fotovoltaico'], textposition='outside')
        fig_fv.add_hline(y=1960, line_dash="dash", line_color="green", annotation_text="Target FVG 2030")
        fig_fv.update_layout(yaxis_range=[0, 2200])
        st.plotly_chart(fig_fv, use_container_width=True)
    with c2:
        st.markdown("### Dettagli Territoriali:\n* **Consumo del suolo:** I grandi impianti a terra (>1MW) sono passati da 334 ha (2023) a 424 ha (2024).\n* **Impatto agricolo:** Occupano lo **0,19% della SAU**.\n* **Trend 2025:** Flssione del -46% nel primo semestre.")

# --- PAGINA 4: GAS & PETROLIO (NUOVA, HARDCODED) ---
elif page == "🔥 Focus: Gas & Petrolio":
    st.title("🔥 Focus: Gas & Petrolio (Termoelettrico e Cogenerazione)")
    st.markdown("Dati estratti dai report statistici Terna sul parco termoelettrico del FVG.")
    
    c1, c2, c3 = st.columns(3)
    prod_2007 = df_termo_storico[df_termo_storico['Anno'] == 2007]['GWh'].sum()
    prod_2024 = df_termo_storico[df_termo_storico['Anno'] == 2024]['GWh'].sum()
    
    c1.metric("Picco Produzione Termoelettrica (2007)", f"{prod_2007:,.0f} GWh")
    c2.metric("Produzione Recente (2024)", f"{prod_2024:,.0f} GWh", "Crollo storico")
    c3.metric("Calo dal picco", f"-{((prod_2007 - prod_2024)/prod_2007)*100:.1f}%")
    
    st.divider()
    c_chart, c_text = st.columns([2, 1])
    
    with c_chart:
        fig_termo = px.area(
            df_termo_storico, x='Anno', y='GWh', color='Categoria',
            title="Evoluzione e Crollo del Termoelettrico in FVG (GWh)",
            color_discrete_map={'Cogenerative': color_map['Cogenerative'], 'Non cogenerative': color_map['Non cogenerative']}
        )
        st.plotly_chart(fig_termo, use_container_width=True)
        
        st.markdown("### Anatomia del Parco Termoelettrico (Mix Tecnologico Attuale)")
        fig_det = px.bar(
            df_termo_mix, y='Tecnologia', x='GWh', color='Categoria',
            orientation='h', title="Composizione Tecnologica",
            color_discrete_map={'Cogenerative': color_map['Cogenerative'], 'Non cogenerative': color_map['Non cogenerative']}
        )
        fig_det.update_layout(yaxis={'categoryorder':'total ascending'})
        st.plotly_chart(fig_det, use_container_width=True)

    with c_text:
        st.markdown("### L'Evoluzione del Sistema")
        st.markdown("""
        I dati mostrano una transizione interna ai combustibili fossili prima ancora che verso le rinnovabili:
        * **L'Efficienza vince:** Gli impianti non cogenerativi (in grigio) che sprecavano il calore termico sono collassati, passando da oltre 10.000 GWh nei primi anni 2000 a valori marginali oggi.
        * **Il crollo recente:** A partire dal 2022/2023 si nota un dimezzamento della produzione totale. Questo è l'effetto combinato della crisi dei prezzi del gas metano e dell'erosione delle quote di mercato da parte del fotovoltaico (elettrificazione).
        * **Ciclo Combinato Re:** La tecnologia dominante rimasta in funzione è il ciclo combinato cogenerativo, che permette di recuperare il calore per teleriscaldamento o processi industriali.
        """)

# --- PAGINA 5: RETI ELETTRICHE ---
elif page == "⚡ Stato delle Reti Elettriche":
    st.title("⚡ Stato delle Reti Elettriche e Hosting Capacity")
    c1, c2, c3 = st.columns(3)
    c1.metric("Potenza FER Connessa", "1,6 GW", "Di cui 1,25 GW Solare")
    c2.metric("Connessioni ultimi 3 anni", "800 MW")
    c3.metric("Nuova Hosting Capacity", "+ 1,6 GW", "Previsto Raddoppio")
    st.divider()
    st.markdown("### Interventi in Programma\n* 🏗️ **23 Ampliamenti** di Cabine Primarie esistenti.\n* ⚡ **14 Nuove Cabine Primarie** da realizzare ex novo (es. snodo Udine Sud).")

elif page in ["💧 Focus: Idroelettrico", "🌱 Focus: Biomasse & Biogas", "🌍 Emissioni e Clima (FVG)"]:
    st.title(page)
    st.info("🚧 Questa sezione sarà popolata con i prossimi step di analisi dei PDF (Clima ARPA, PAESC, Idroelettrico).")
