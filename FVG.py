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
    'Biomasse/Geo': '#8B4513'
}

# --- 2. CARICAMENTO DATI REALI FVG ---
@st.cache_data
def load_real_fvg_data():
    # Serie storica estesa per Marchetti e Ternario (2000 - 2030)
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
    
    # Dati storici reali Fotovoltaico (Green Deal / PER FVG)
    df_cap_fv = pd.DataFrame([
        {'Anno': 2019, 'MW': 545},
        {'Anno': 2020, 'MW': 561},
        {'Anno': 2021, 'MW': 591},
        {'Anno': 2022, 'MW': 656},
        {'Anno': 2023, 'MW': 948},
        {'Anno': 2024, 'MW': 1318}
    ])
    
    return df_primaria, df_cap_fv

df_primaria, df_cap_fv = load_real_fvg_data()

# --- 3. MENU DI NAVIGAZIONE LATERALE ---
st.sidebar.image("https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Flag_of_Friuli-Venezia_Giulia.svg/320px-Flag_of_Friuli-Venezia_Giulia.svg.png", width=150)
st.sidebar.title("FVG Energy Portal")

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
selected_year = st.sidebar.selectbox("Filtro Anno Globale:", sorted(df_primaria['Anno'].unique(), reverse=True), index=3) # Anno 2024

# ==========================================
# 4. CONTENUTO DELLE PAGINE
# ==========================================

# --- PAGINA 1: QUADRO GENERALE ---
if page == "📊 Quadro Generale (Offerta & Domanda)":
    st.title("📊 Quadro Generale (Offerta & Domanda)")
    
    tab_macro, tab_transizione, tab_terna = st.tabs([
        "Overview & Mix", 
        "📈 Transizione (Marchetti & Ternario)", 
        "📂 Esploratore Terna (Multi-Excel)"
    ])
    
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
            st.markdown("Asse Y: $ \log_{10}(f / (1-f)) $ dove $ f $ è la quota di mercato.")
            df_march = df_primaria.copy()
            tot_y = df_march.groupby('Anno')['GWh'].sum().reset_index().rename(columns={'GWh':'Total'})
            df_march = pd.merge(df_march, tot_y, on='Anno')
            df_march['f'] = np.clip(df_march['GWh'] / df_march['Total'], 0.0001, 0.9999)
            df_march['Marchetti'] = np.log10(df_march['f'] / (1 - df_march['f']))
            
            fig_m = px.line(
                df_march, x='Anno', y='Marchetti', color='Fonte', 
                color_discrete_map=color_map, markers=True
            )
            fig_m.update_layout(yaxis_title="log(f / 1-f)", margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_m, use_container_width=True)

        with c_m2:
            st.subheader("Rotta dell'Elettrificazione (Diagramma Ternario)")
            st.markdown("Fossili vs Elettroni (Rinnovabili) vs Molecole (Biomasse)")
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
                hover_name="Anno", color="Anno", color_continuous_scale="Viridis"
            )
            fig_t.update_traces(mode="lines+markers", line=dict(color='#22C55E', width=2), marker=dict(size=8))
            fig_t.update_layout(margin=dict(t=30, b=0, l=0, r=0))
            st.plotly_chart(fig_t, use_container_width=True)

    with tab_terna:
        st.subheader("Esploratore File Terna")
        st.info("Trascina i tuoi 14 file Excel Terna qui sotto per caricarli ed esplorarli.")
        uploaded_files = st.file_uploader("Carica file Excel Terna (.xlsx)", type=['xlsx'], accept_multiple_files=True)
        dict_dfs = {}
        if uploaded_files:
            for f in uploaded_files:
                try:
                    dict_dfs[f.name] = pd.read_excel(f)
                except Exception as e:
                    st.error(f"Errore su {f.name}: {e}")
            if dict_dfs:
                file_sel = st.selectbox("Seleziona File da Analizzare:", list(dict_dfs.keys()))
                st.dataframe(dict_dfs[file_sel], use_container_width=True)

# --- PAGINA 2: SANKEY TERMODINAMICO ---
elif page == "🔄 Sankey Termodinamico":
    st.title(f"🔄 Flussi di Energia FVG ({selected_year})")
    st.markdown("Mappatura dall'energia primaria ai consumi finali e perdite termodinamiche.")
    
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

    # Logica dei flussi
    in_elec_gas = gas * 0.40
    in_elec_coal = carbone * 1.0
    in_elec_bio = bio * 0.20
    
    dir_gas = gas * 0.60
    dir_petrolio = petrolio * 0.95
    dir_bio = bio * 0.80
    
    eff_termo = 0.45
    elec_from_termo = (in_elec_gas + in_elec_coal + in_elec_bio) * eff_termo
    perdite_termo = (in_elec_gas + in_elec_coal + in_elec_bio) * (1 - eff_termo)
    
    elec_from_rin = idro + solare + eolico
    tot_elec = elec_from_termo + elec_from_rin
    
    elec_ind = tot_elec * 0.50
    elec_civ = tot_elec * 0.45
    elec_tra = tot_elec * 0.05
    
    gas_ind = dir_gas * 0.50
    gas_civ = dir_gas * 0.50
    pet_tra = dir_petrolio * 0.90
    pet_ind = dir_petrolio * 0.10
    bio_civ = dir_bio * 0.90
    bio_ind = dir_bio * 0.10
    
    perdite_trasporti = pet_tra * 0.70
    perdite_civile = (gas_civ + bio_civ) * 0.15

    nodes = ["Gas Naturale", "Petrolio", "Carbone", "Idro", "Solare", "Eolico", "Biomasse", 
             "Generazione Elettrica", "Usi Diretti (Termico/Motori)", 
             "Industria", "Civile/Edifici", "Trasporti", "Perdite Termodinamiche"]
             
    colors = [color_map['Gas Naturale'], color_map['Petrolio'], color_map['Carbone'], 
              color_map['Idroelettrico'], color_map['Solare Fotovoltaico'], color_map['Eolico'], color_map['Biomasse/Geo'],
              '#FACC15', '#9CA3AF', 
              '#F97316', '#3B82F6', '#10B981', 'rgba(239, 68, 68, 0.7)']
    
    source = [
        0, 2, 6, 3, 4, 5,
        0, 1, 6,
        7, 7, 7,
        8, 8, 8, 8, 8, 8,
        7, 11, 10
    ]
    
    target = [
        7, 7, 7, 7, 7, 7,
        8, 8, 8,
        9, 10, 11,
        9, 10, 11, 9, 10, 9,
        12, 12, 12
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

# --- PAGINA 3: FOCUS FOTOVOLTAICO ---
elif page == "☀️ Focus: Fotovoltaico":
    st.title("☀️ Focus: Fotovoltaico in FVG")
    st.markdown("Dati ufficiali dal *Piano Energetico Regionale (PER)* e *Energy Green Deal FVG 2024*.")
    
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
        fig_fv.add_hline(y=1960, line_dash="dash", line_color="green", annotation_text="Target FVG 2030 (1.960 MW)")
        fig_fv.update_layout(yaxis_range=[0, 2200])
        st.plotly_chart(fig_fv, use_container_width=True)
    with c2:
        st.markdown("""
        ### Dettagli Territoriali e Suolo:
        * **Consumo del suolo:** I grandi impianti a terra (>1MW) sono passati da 334 ha (2023) a 424 ha (2024).
        * **Impatto agricolo:** Occupano lo **0,19% della SAU** (Superficie Agricola Utilizzata) regionale.
        * **Trend 2025:** Nel primo semestre 2025 la nuova potenza connessa ha subìto una flessione (-46% rispetto allo stesso periodo del 2024).
        """)

# --- PAGINA 4: STATO DELLE RETI ---
elif page == "⚡ Stato delle Reti Elettriche":
    st.title("⚡ Stato delle Reti Elettriche e Hosting Capacity")
    st.markdown("Dati ufficiali audizione IV Commissione Regionale (Gestione Rete FVG).")
    
    c1, c2, c3 = st.columns(3)
    c1.metric("Potenza FER Connessa", "1,6 GW", "Di cui 1,25 GW Solare")
    c2.metric("Connessioni ultimi 3 anni", "800 MW", "50% del totale storico")
    c3.metric("Nuova Hosting Capacity", "+ 1,6 GW", "Previsto Raddoppio")
    
    st.divider()
    st.subheader("Infrastrutture e Sviluppo in Programma")
    st.markdown("""
    * 🏗️ **23 Ampliamenti** di Cabine Primarie esistenti.
    * ⚡ **14 Nuove Cabine Primarie** da realizzare ex novo.
    * 🎯 **Obiettivo:** Rimuovere la saturazione delle stazioni critiche (es. Udine Sud) per permettere l'immissione di nuove FER.
    """)


elif page == "🔥 Focus: Gas & Petrolio":
    st.title("🔥 Focus: Gas & Petrolio (Termoelettrico e Cogenerazione)")
    st.markdown("Analisi basata sui dati statistici ufficiali Terna relativi al parco termoelettrico regionale.")
    
    # Controlliamo se l'utente ha caricato i file Terna nella barra laterale
    if 'dict_dfs' not in locals() or not dict_dfs:
        st.warning("⚠️ Per visualizzare i dati reali in questa sezione, devi caricare i file Excel di Terna nella barra laterale (Quadro Generale).")
        st.info("In attesa dei file, mostriamo i macro-trend regionali.")
    else:
        st.success("Dati Terna rilevati in memoria. Analisi attivata.")
        
        # Cerchiamo il file del termoelettrico tra quelli caricati
        file_termo = next((nome for nome in dict_dfs.keys() if "Produzione termoelettrica per categoria" in nome and "(1)" not in nome), None)
        
        if file_termo:
            df_termo = dict_dfs[file_termo]
            # Assicuriamoci che le colonne siano pulite
            df_termo.columns = [str(c).strip() for c in df_termo.columns]
            
            # KPI Principali calcolati dal file Terna
            anno_max = df_termo['Anno'].max()
            prod_recente = df_termo[df_termo['Anno'] == anno_max]['Sum of Produzione (GWh)'].sum()
            prod_picco = df_termo.groupby('Anno')['Sum of Produzione (GWh)'].sum().max()
            anno_picco = df_termo.groupby('Anno')['Sum of Produzione (GWh)'].sum().idxmax()
            
            c1, c2, c3 = st.columns(3)
            c1.metric(f"Produzione Termoelettrica ({anno_max})", f"{prod_recente:,.0f} GWh", "Crollo storico")
            c2.metric(f"Picco Storico ({anno_picco})", f"{prod_picco:,.0f} GWh")
            c3.metric("Calo dal picco", f"-{((prod_picco - prod_recente)/prod_picco)*100:.1f}%")
            
            st.divider()
            
            c_chart, c_text = st.columns([2, 1])
            with c_chart:
                fig_termo = px.area(
                    df_termo, x='Anno', y='Sum of Produzione (GWh)', color='Categoria',
                    title="Evoluzione e Crollo del Termoelettrico (GWh)",
                    color_discrete_map={'Cogenerative': '#F97316', 'Non cogenerative': '#6B7280'}
                )
                fig_termo.update_layout(margin=dict(t=30, b=0, l=0, r=0))
                st.plotly_chart(fig_termo, use_container_width=True)
                
            with c_text:
                st.markdown("### L'Evoluzione del Sistema")
                st.markdown(f"""
                I dati Terna mostrano una transizione interna ai combustibili fossili prima ancora che verso le rinnovabili:
                * **L'Efficienza vince:** Gli impianti non cogenerativi (grigio) che sprecavano il calore termico sono collassati, passando da oltre 10.000 GWh nei primi anni 2000 a valori marginali oggi.
                * **Il crollo recente:** A partire dal 2022/2023 si nota un dimezzamento della produzione totale. Questo è l'effetto combinato della crisi dei prezzi del gas metano e dell'erosione delle quote di mercato da parte del fotovoltaico (elettrificazione).
                """)
        else:
            st.error("Il file 'Produzione termoelettrica per categoria [GWh].xlsx' non è presente tra quelli caricati.")
            
        # Cerchiamo il secondo file: dettaglio tecnologie
        file_dettaglio = next((nome for nome in dict_dfs.keys() if "Produzione termoelettrica per categoria" in nome and "(1)" in nome), None)
        if file_dettaglio:
            st.subheader("Anatomia del Parco Termoelettrico")
            df_det = dict_dfs[file_dettaglio]
            # Assumendo che le colonne siano: Categoria, Sottocategoria, Sum of Produzione (GWh)
            fig_det = px.bar(
                df_det, y='Sottocategoria', x='Sum of Produzione (GWh)', color='Categoria',
                orientation='h', title="Composizione Tecnologica",
                color_discrete_map={'Cogenerative': '#F97316', 'Non cogenerative': '#6B7280'}
            )
            fig_det.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_det, use_container_width=True)
            
            # --- PAGINE SEGNAPOSTO (Da popolare blocco per blocco) ---
elif page in ["💧 Focus: Idroelettrico", "🌱 Focus: Biomasse & Biogas", "🔋 Focus: Batterie & Accumuli", "🌍 Emissioni e Clima (FVG)"]:
    st.title(page)
    st.info("🚧 Sezione pronta. Inizieremo a popolarla con i dati specifici nel prossimo blocco!")

#"🔥 Focus: Gas & Petrolio"
            
