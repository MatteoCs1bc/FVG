import pandas as pd
import numpy as np
import plotly.express as px
import streamlit as st

def genera_diagramma_ternario(df_primaria):
    st.subheader("🔺 Rotta dell'Elettrificazione (Diagramma Ternario FVG)")
    st.markdown("""
    Ogni punto rappresenta l'equilibrio del mix energetico regionale per un dato anno:
    * **In basso a sinistra**: Dominanza delle fonti fossili (Gas, Petrolio, Carbone)
    * **In basso a destra**: Dominanza degli elettroni rinnovabili (Idro, Solare, Eolico)
    * **In alto**: Dominanza delle molecole rinnovabili (Biomasse, Biogas)
    """)
    
    # 1. Raggruppamento per Anno e Fonte
    pivot_df = df_primaria.pivot_table(index='Anno', columns='Fonte', values='GWh', aggfunc='sum').fillna(0)
    
    # 2. Aggregazione nelle 3 Macro-Categorie
    pivot_df['Fossil'] = pivot_df.get('Carbone', 0) + pivot_df.get('Gas Naturale', 0) + pivot_df.get('Petrolio', 0)
    pivot_df['Electrons'] = pivot_df.get('Idroelettrico', 0) + pivot_df.get('Solare Fotovoltaico', 0) + pivot_df.get('Eolico', 0)
    pivot_df['Bio & Other'] = pivot_df.get('Biomasse/Geo', 0)
    
    # 3. Calcolo Totale e Normalizzazione a 100%
    pivot_df['Total'] = pivot_df['Fossil'] + pivot_df['Electrons'] + pivot_df['Bio & Other']
    
    for col in ['Fossil', 'Electrons', 'Bio & Other']:
        pivot_df[col] = (pivot_df[col] / pivot_df['Total']) * 100
        
    pivot_df = pivot_df.reset_index()
    
    # 4. Creazione del Grafico Ternario con Plotly Express
    fig = px.scatter_ternary(
        pivot_df, 
        a="Fossil", 
        b="Electrons", 
        c="Bio & Other", 
        hover_name="Anno", 
        color="Anno",
        color_continuous_scale="Viridis",
        labels={
            "Fossil": "Fossili (%)",
            "Electrons": "Elettroni (%)",
            "Bio & Other": "Biomasse/Altro (%)"
        },
        title="Traiettoria Storica e Proiettata (2000 - 2030)"
    )
    
    # Personalizzazione grafica della linea di traiettoria e dei marcatori
    fig.update_traces(
        mode="lines+markers", 
        line=dict(color='#22C55E', width=3), 
        marker=dict(size=10, symbol="circle")
    )
    
    fig.update_layout(
        margin=dict(t=50, b=20, l=20, r=20),
        ternary=dict(
            sum=100,
            aaxis_title="Fossili",
            baxis_title="Elettroni FER",
            caxis_title="Biomasse / Bio"
        )
    )
    
    return fig
