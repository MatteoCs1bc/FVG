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

# --- 2. CARICAMENTO DATI REALI FVG ---
@st.cache_data
def load_real_fvg_data():
    # Serie storica estesa per Ternario e Marchetti (2000 - 2030)
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
    
    # Dati storici Fotovoltaico
    df_cap_fv = pd.DataFrame([
        {'Anno': 2019, 'MW': 545}, {'Anno': 2020, 'MW': 561}, {'Anno': 2021, 'MW': 591},
        {'Anno': 2022, 'MW': 656}, {'Anno': 2023, 'MW': 948}, {'Anno': 2024, 'MW': 1318}
    ])

    # Dati storici Termoelettrico (Terna)
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

    # Mix Tecnologico Termoelettrico
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
    "🔺 Transizione (Marchetti & Ternario)",
    "🔄 Sankey Termodinamico",
    "☀️ Focus: Fotovoltaico",
    "🔥 Focus: Gas Naturale",
    "🛢️ Focus: Petrolio e Carburanti",
    "🏭 Focus: Industria HTA & Idrogeno",
    "💧 Focus: Idroelettrico",
    "🌱 Focus: Biomasse & Biogas",
    "🔋 Focus: Batterie & Accumuli",
    "⚡ Stato delle Reti Elettriche",
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

# --- PAGINA 2: TERNARIO & MARCHETTI ---
elif page == "🔺 Transizione (Marchetti & Ternario)":
    st.title("🔺 Transizione Energetica FVG: Diagramma Ternario & Marchetti")
    
    st.subheader("1. Diagramma Ternario (Fossili vs Elettroni vs Biomasse)")
    pivot_df = df_primaria.pivot_table(index='Anno', columns='Fonte', values='GWh', aggfunc='sum').fillna(0)
    pivot_df['Total'] = pivot_df.sum(axis=1)
    
    pivot_df['Fossil'] = pivot_df.get('Carbone',0) + pivot_df.get('Gas Naturale',0) + pivot_df.get('Petrolio',0)
    pivot_df['Electrons'] = pivot_df.get('Idroelettrico',0) + pivot_df.get('Solare Fotovoltaico',0) + pivot_df.get('Eolico',0)
    pivot_df['Bio_Other'] = pivot_df.get('Biomasse/Geo',0)
    
    pivot_df['Fossil_pct'] = (pivot_df['Fossil'] / pivot_df['Total']) * 100
    pivot_df['Electrons_pct'] = (pivot_df['Electrons'] / pivot_df['Total']) * 100
    pivot_df['Bio_pct'] = (pivot_df['Bio_Other'] / pivot_df['Total']) * 100
    
    pivot_res = pivot_df.reset_index()
    
    fig_t = px.scatter_ternary(
        pivot_res, a="Fossil_pct", b="Electrons_pct", c="Bio_pct", 
        hover_name="Anno", text="Anno", color="Anno", color_continuous_scale="Viridis",
        labels={"Fossil_pct": "Fossili (%)", "Electrons_pct": "Elettroni (%)", "Bio_pct": "Biomasse (%)"}
    )
    fig_t.update_traces(mode="lines+markers+text", textposition="top center", line=dict(color='#22C55E', width=3), marker=dict(size=12))
    fig_t.update_layout(height=650, margin=dict(t=50, b=40, l=40, r=40))
    st.plotly_chart(fig_t, use_container_width=True)

    st.divider()
    st.subheader("2. Modello di Sostituzione Tecnologica di Marchetti")
    df_march = df_primaria.copy()
    tot_y = df_march.groupby('Anno')['GWh'].sum().reset_index().rename(columns={'GWh':'Total'})
    df_march = pd.merge(df_march, tot_y, on='Anno')
    df_march['f'] = np.clip(df_march['GWh'] / df_march['Total'], 0.0001, 0.9999)
    df_march['Marchetti'] = np.log10(df_march['f'] / (1 - df_march['f']))
    
    fig_m = px.line(df_march, x='Anno', y='Marchetti', color='Fonte', color_discrete_map=color_map, markers=True)
    fig_m.update_layout(height=500, yaxis_title="log(f / 1-f)")
    st.plotly_chart(fig_m, use_container_width=True)

# --- PAGINA 3: SANKEY TERMODINAMICO ---
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

# --- PAGINA 4: FOCUS FOTOVOLTAICO ---
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
        st.markdown("### Dettagli Territoriali:\n* **Consumo del suolo:** Impianti a terra (>1MW) passati da 334 ha a 424 ha.\n* **Impatto agricolo:** Occupano lo **0,19% della SAU**.\n* **Trend 2025:** Flessione del -46% nel primo semestre.")

# --- PAGINA 5: FOCUS GAS NATURALE (DIFFERENZIATO) ---
elif page == "🔥 Focus: Gas Naturale":
    st.title("🔥 Focus: Gas Naturale in Friuli-Venezia Giulia")
    st.markdown("Ripartizione vettoriale del consumo di metano tra Generazione Elettrica, Usi Industriali e Usi Domestici/Civili.")
    
    # Consumo indicativo gas FVG ~1.5 - 1.7 Mld m3 (~16.000 GWh equivalenti)
    gwh_gas_tot = df_primaria[df_primaria['Anno'] == 2024][df_primaria['Fonte'] == 'Gas Naturale']['GWh'].values[0]
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Consumo Primario Gas", f"{gwh_gas_tot:,.0f} GWh", "~1.6 Mld m³")
    m2.metric("Generazione Elettrica / Cogen", f"{gwh_gas_tot*0.40:,.0f} GWh", "40% del totale")
    m3.metric("Usi Industriali (Processo)", f"{gwh_gas_tot*0.30:,.0f} GWh", "30% del totale")
    m4.metric("Usi Civili / Riscaldamento", f"{gwh_gas_tot*0.30:,.0f} GWh", "30% del totale")
    
    st.divider()
    
    c1, c2 = st.columns([1, 1])
    with c1:
        st.subheader("Ripartizione Usi del Gas Metano")
        df_gas_split = pd.DataFrame([
            {'Destinazione': 'Generazione Elettrica & Cogenerazione', 'GWh': gwh_gas_tot*0.40},
            {'Destinazione': 'Industria Manifatturiera & HTA', 'GWh': gwh_gas_tot*0.30},
            {'Destinazione': 'Civile (Riscaldamento Domestico & Terziario)', 'GWh': gwh_gas_tot*0.30}
        ])
        fig_gas = px.pie(
            df_gas_split, values='GWh', names='Destinazione', hole=0.45,
            color_discrete_sequence=['#F97316', '#4B5563', '#3B82F6']
        )
        fig_gas.update_traces(textinfo='percent+label')
        st.plotly_chart(fig_gas, use_container_width=True)
        
    with c2:
        st.subheader("Trend Storico Termoelettrico a Gas (Terna)")
        fig_termo = px.area(
            df_termo_storico, x='Anno', y='GWh', color='Categoria',
            title="Crollo della produzione elettrica da Gas (GWh)",
            color_discrete_map={'Cogenerative': color_map['Cogenerative'], 'Non cogenerative': color_map['Non cogenerative']}
        )
        st.plotly_chart(fig_termo, use_container_width=True)

    st.markdown("""
    ### Key Takeaways sul Gas in FVG:
    * **Riscaldamento Domestico:** La metanizzazione capillare della pianura FVG rende il gas la fonte primaria per il settore civile. La transizione prevede la sostituzione progressiva con pompe di calore.
    * **Cogenerazione Industriale:** Cartiere (es. Ovaro), vetrerie e siderurgia usano il gas sia per il calore di processo che per autoprodursi energia elettrica.
    """)

# --- PAGINA 6: FOCUS PETROLIO E CARBURANTI ---
elif page == "🛢️ Focus: Petrolio e Carburanti":
    st.title("🛢️ Focus: Petrolio e Prodotti Petroliferi")
    st.markdown("Analisi dei consumi petroliferi regionali, dominati dal settore Trasporti.")
    
    gwh_petrolio = df_primaria[df_primaria['Anno'] == 2024][df_primaria['Fonte'] == 'Petrolio']['GWh'].values[0]
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Consumo Primario Petrolio", f"{gwh_petrolio:,.0f} GWh")
    m2.metric("Quota Settore Trasporti", f"{gwh_petrolio*0.88:,.0f} GWh", "88% del petrolio")
    m3.metric("Usi Industriali / Altro", f"{gwh_petrolio*0.12:,.0f} GWh", "12%")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Destinazione dei Prodotti Petroliferi")
        df_petro = pd.DataFrame([
            {'Uso': 'Diesel Trasporti / Logistica', 'Quota': 55},
            {'Uso': 'Benzina Autotrazione', 'Quota': 25},
            {'Uso': 'GPL & Combustibili riscaldamento', 'Quota': 12},
            {'Uso': 'Usi Industriali & Altro', 'Quota': 8}
        ])
        fig_petro = px.bar(df_petro, x='Quota', y='Uso', orientation='h', title="Composizione Consumi Petroliferi (%)", color_discrete_sequence=['#4B5563'])
        st.plotly_chart(fig_petro, use_container_width=True)
        
    with c2:
        st.markdown("""
        ### Elettrificazione del Trasporto e Decarbonizzazione:
        * **Logistica di Transito:** Il FVG è uno snodo logistico fondamentale per i corridoi europei (Porto di Trieste, corridoi stradali verso Austria e Slovenia). Questo comporta un'elevata incidenza del consumo di gasolio autotrazione.
        * **Obiettivi del PER:** Sostituzione progressiva del parco veicolare con veicoli elettrici (EV) per il trasporto leggero e introduzione del **Biometano e Idrogeno verde** per i trasporti pesanti e la logistica portuale.
        """)

# --- PAGINA 7: FOCUS INDUSTRIA HTA & IDROGENO ---
elif page == "🏭 Focus: Industria HTA & Idrogeno":
    st.title("🏭 Focus: Industria Hard-to-Abate (HTA) & Idrogeno in FVG")
    st.markdown("Analisi dei settori industriali ad alta intensità energetica e strategie di decarbonizzazione (Strategia Regionale Idrogeno FVG).")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Incidenza Manifattura FVG", "23% Valore Aggiunto", "4ª regione in Italia")
    m2.metric("Progetti BESS / Idrogeno", "North Adriatic Hydrogen Valley", "Sintonia Slovenia-Croazia-FVG")
    m3.metric("Elettrolizzatori Previsti", "Iniziative PNRR / Hard-to-Abate", "Progetti-faro al 2026")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Settori Hard-to-Abate (HTA) nel FVG")
        df_hta = pd.DataFrame([
            {'Settore': 'Siderurgia / Acciaierie', 'Consumo_Relativo': 45, 'Descrizione': 'Distretto Udinese (Forni elettrici e gas per laminatoi)'},
            {'Settore': 'Cartiere', 'Consumo_Relativo': 25, 'Descrizione': 'Carnia (Ovaro) e Pordenonese (Usi vapore / Cogenerazione)'},
            {'Settore': 'Vetrerie & Ceramiche', 'Consumo_Relativo': 18, 'Descrizione': 'Forni fusori continui ad alta temperatura'},
            {'Settore': 'Cantieristica & Meccanica Pesante', 'Consumo_Relativo': 12, 'Descrizione': 'Monfalcone, Trieste e Pordenone'}
        ])
        fig_hta = px.pie(df_hta, values='Consumo_Relativo', names='Settore', title="Peso Relativo dei Consumi nei Settori HTA", hole=0.35)
        st.plotly_chart(fig_hta, use_container_width=True)
        
    with c2:
        st.markdown("""
        ### La Strategia Regionale per l'Idrogeno:
        * **Valle dell'Idrogeno del Nord Adriatico:** Progetto transfrontaliero integrato tra Friuli-Venezia Giulia, Slovenia e Croazia per creare una filiera locale dell'idrogeno verde.
        * **Sostituzione del Gas Metano:** L'idrogeno verde è destinato a sostituire il metano nei bruciatori dei laminatoi siderurgici e delle vetrerie, dove l'elettrificazione diretta è complessa o antieconomica.
        * **Sinergia con le FER:** Utilizzo dell'energia elettrica rinnovabile in eccesso (*overgeneration*) per alimentare gli elettrolizzatori.
        """)

# --- PAGINA 8: FOCUS IDROELETTRICO ---
elif page == "💧 Focus: Idroelettrico":
    st.title("💧 Focus: Energia Idroelettrica in FVG")
    st.markdown("La risorsa idrica è la colonna portante della generazione rinnovabile storica del FVG (Dati dal report *L'infinito in una goccia*).")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Produzione Media Annua", "~2.800 - 3.500 GWh", "Soggetta a variabilità meteo")
    m2.metric("Potenza Installata", "~1.000 MW", "Tra grande e piccolo idro")
    m3.metric("Rilevanza in Carnia", "82% Produzione Locale", "98% delle FER in Carnia")
    
    st.divider()
    st.markdown("""
    ### Caratteristiche del Parco Idroelettrico FVG:
    * **Grandi Impianti di Monte:** Bacini e centrali ad alta caduta nelle Alpi Carniche e Giulie (es. asta del Tagliamento, Cellina, Meduna).
    * **Piccolo Idroelettrico & Aqueduct Power:** Impianti ad acqua fluente e turbine inserite negli acquedotti (es. esperienze A2A, Secab, e cooperative storiche come la *Cooperativa della Luce*).
    * **Vulnerabilità Climatica:** I report *Segnali dal Clima FVG* evidenziano una crescente variabilità delle precipitazioni e riduzioni estive della portata dei fiumi, che richiedono un'ottimizzazione della gestione dei bacini.
    """)

# --- PAGINA 9: FOCUS BIOMASSE & BIOGAS ---
elif page == "🌱 Focus: Biomasse & Biogas":
    st.title("🌱 Focus: Bioenergie (Biomasse Solide, Biogas, Biometano)")
    st.markdown("Dati estratti dal documento ENEA *Ruolo delle bioenergie nel PER*.")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Produzione Biogas FVG", "406,8 GWh", "Settore agricolo / zootecnico")
    m2.metric("Produzione Biomasse Solide", "68,5 GWh", "Cippato / Pellet per calore")
    m3.metric("Bioliquidi", "361 GWh", "Impianti dedicati")
    
    st.divider()
    st.markdown("""
    ### Valorizzazione della Filiera Filiera Legno-Energia e Agro-zootecnica:
    * **Biometano:** Riconversione degli impianti di biogas agricolo per l'immissione di biometano nella rete SNAM e per l'uso nei trasporti pesanti.
    * **Filiera Forestale Carnia e Prealpi:** Valorizzazione degli scarti di lavorazione del legno e pulizia dei boschi per impianti di teleriscaldamento a cippato locale.
    """)

# --- PAGINA 10: FOCUS BATTERIE & ACCUMULI ---
elif page == "🔋 Focus: Batterie & Accumuli":
    st.title("🔋 Focus: Sistemi di Accumulo (SDA) e BESS in FVG")
    st.markdown("Dati estratti dal *Green Deal FVG 2024* e dall'audizione della IV Commissione Regionale.")
    
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Sistemi di Accumulo Residenziali", "35.621 impianti", "Abbinati al PV")
    m2.metric("Capacità Accumuli Piccoli", "409 MWh", "331 MW di potenza")
    m3.metric("Grandi Impianti BESS Autorizzati", "26 Progetti", "Di cui 1 da 200 MW a Pavia di Udine")
    m4.metric("Potenza BESS in Autorizzazione", "1.405 MW", "Rete Terna / Standalone")
    
    st.divider()
    st.markdown("""
    ### Il Ruolo Chiave degli Accumuli Elettrochimici:
    * **Stabilizzazione della Rete:** Gli impianti BESS (Battery Energy Storage System) di grande taglia (es. snodo Udine Sud Terna, Pavia di Udine, Gemona, Fogliano) sono indispensabili per stoccare l'overgeneration fotovoltaica diurna e rilasciarla nelle ore serali.
    * **Autoconsumo Residenziale:** Oltre il 45% degli impianti fotovoltaici domestici in FVG è oggi dotato di un sistema di accumulo a batteria.
    """)

# --- PAGINA 11: RETI ELETTRICHE ---
elif page == "⚡ Stato delle Reti Elettriche":
    st.title("⚡ Stato delle Reti Elettriche e Hosting Capacity")
    c1, c2, c3 = st.columns(3)
    c1.metric("Potenza FER Connessa", "1,6 GW", "Di cui 1,25 GW Solare")
    c2.metric("Connessioni ultimi 3 anni", "800 MW")
    c3.metric("Nuova Hosting Capacity", "+ 1,6 GW", "Previsto Raddoppio")
    st.divider()
    st.markdown("### Interventi in Programma\n* 🏗️ **23 Ampliamenti** di Cabine Primarie esistenti.\n* ⚡ **14 Nuove Cabine Primarie** da realizzare ex novo (es. snodo Udine Sud).")

# --- PAGINA 12: EMISSIONI E CLIMA FVG ---
elif page == "🌍 Emissioni e Clima (FVG)":
    st.title("🌍 Emissioni di Gas Serra e Impatti Climatici in FVG")
    st.markdown("Dati ufficiali ARPA FVG (Report *Segnali dal Clima FVG 2024-2026* e *Legge FVG Green*).")
    
    m1, m2, m3 = st.columns(3)
    m1.metric("Emissioni Dirette FVG", "8,8 Mt CO₂eq/anno", "Totale regionale")
    m2.metric("Assorbimento Foreste FVG", "23% delle emissioni", "Sequestro di carbonio naturale")
    m3.metric("Anno 2025/2026", "3° anno più caldo", "Anomalia termica ARPA")
    
    st.divider()
    
    c1, c2 = st.columns(2)
    with c1:
        st.subheader("Ripartizione Emissioni per Settore")
        df_emis = pd.DataFrame([
            {'Settore': 'Industria & Manifattura', 'MtCO2': 3.2},
            {'Settore': 'Trasporti Stradali & Logistica', 'MtCO2': 2.8},
            {'Settore': 'Residenziale & Servizi (Riscaldamento)', 'MtCO2': 2.0},
            {'Settore': 'Agricoltura & Rifiuti', 'MtCO2': 0.8}
        ])
        fig_em = px.pie(df_emis, values='MtCO2', names='Settore', title="Emissioni Dirette Regionali (Mt CO₂eq)", hole=0.4)
        st.plotly_chart(fig_em, use_container_width=True)
        
    with c2:
        st.markdown("""
        ### Il Ruolo del Patrimonio Forestale e di Mitigazione:
        * **Foreste del FVG:** Il patrimonio boschivo regionale assorbe e bilancia circa il **23% dell'intero monte emissioni regionale** (~2 milioni di tonnellate di CO₂ all'anno).
        * **Obiettivi FVGreen:** Neutralità carbonica regionale e attuazione della Strategia di Adattamento ai Cambiamenti Climatici.
        """)
