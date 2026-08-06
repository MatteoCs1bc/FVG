"""
Dati puntuali estratti da documenti (audizioni, report ARPA, PER).

Non sono serie storiche ri-scaricabili come Terna: sono cifre lette da PDF e
presentazioni. Per questo ogni blocco porta con sé la fonte e la data, e l'app
le mostra accanto al numero. Se un dato non ha fonte, non sta qui.

Aggiornamento: sostituisci il valore e aggiorna `fonte`. Mai il contrario.
"""

from __future__ import annotations

# ---------------------------------------------------------------- reti
FONTE_EDIST = "E-Distribuzione, audizione IV Commissione, 21/04/2026 (dati al 31/12/2025)"
FONTE_TERNA_RETE = "Terna, Programmazione Territoriale Efficiente, Trieste 21/04/2026"

RETE_CONSISTENZA = {
    "Clienti in bassa tensione": (630_000, ""),
    "Clienti in media tensione": (2_700, ""),
    "Impianti primari": (45, ""),
    "Cabine secondarie": (10_607, ""),
    "Linee in media tensione": (7_940, "km"),
    "Linee in bassa tensione": (13_400, "km"),
}

RETE_POTENZA = {
    "Potenza installata totale": 2.7,
    "Potenza installata da fonti rinnovabili": 1.6,
}
RETE_FER_DETTAGLIO = {"Solare": 1.25, "Termica": 0.20, "Idraulica": 0.15}  # GW

HOSTING_CAPACITY_MW = 485  # 2025, senza richieste in pipeline

# Saturazione dei trasformatori AT/MT, effetto richieste in pipeline
TRASFORMATORI_STATO = {
    "Verde (sotto soglia)": 35,
    "Arancione (oltre 65%)": 27,
    "Giallo (sotto 65%)": 9,
    "Rosso (oltre 90%)": 4,
}
TRASFORMATORI_PROVINCIA = {"Udine": 44, "Pordenone": 21, "Gorizia": 7, "Trieste": 3}

# Aree "virtualmente" critiche, dicembre 2025
AREE_CRITICHE_COMUNI = {"Rosso": 65, "Arancio": 136, "Giallo": 1, "Bianco": 4}

RETE_SVILUPPO = {
    "Udine": {"ampliamenti": 15, "mva_ampliamenti": 620, "nuovi": 8, "mva_nuovi": 430},
    "Pordenone": {"ampliamenti": 7, "mva_ampliamenti": 240, "nuovi": 5, "mva_nuovi": 340},
    "Gorizia": {"ampliamenti": 1, "mva_ampliamenti": 60, "nuovi": 1, "mva_nuovi": 50},
}
RETE_CONNESSIONI = {"potenza_connessa_mw_2022_2025": 820, "richieste_2022_2025": 61_000}

# Burden sharing regionale: dove siamo rispetto al target 2030 (GW)
BURDEN_SHARING = {
    "Target 2030 (Decreto Aree Idonee)": 1.96,
    "In esercizio o autorizzato dal 2021": 1.60,
    "Richieste AAT/AT autorizzate": 0.31,
    "Richieste MT/BT autorizzate": 0.35,
    "Quota residua per il target": 0.36,
}

# ---------------------------------------------------------------- clima
FONTE_CLIMA = "ARPA FVG, «Segnali dal clima in FVG», edizioni 2024, 2025 e 2026"

MESI = ["gen", "feb", "mar", "apr", "mag", "giu", "lug", "ago", "set", "ott", "nov", "dic"]
# Anomalia termica mensile a Udine rispetto alla serie 1901-(anno-1)
ANOMALIE_MENSILI = {
    2024: [1.2, 3.8, 2.4, 1.3, 0.3, 1.8, 3.3, 4.3, 0.7, 2.2, 0.2, 1.0],
    2025: [3.3, 2.0, 1.9, 2.1, 0.1, 4.2, 0.7, 1.5, 1.3, -0.3, 0.6, 2.6],
}
ANOMALIA_ANNUA = {2023: 1.7, 2024: 1.9, 2025: 1.7}

CLIMA_SINTESI = {
    "anno_ultimo": 2025,
    "posizione_classifica": "terzo anno più caldo dal 1900",
    "superato_da": "2024 e 2022",
    "anomalia_vs_1991_2020": 1.2,
    "anomalia_vs_novecento": 1.8,
    "anomalia_vs_preindustriale": 2.2,  # rispetto al 1850-1900
    "soglia_globale_superata": 1.5,
}

CLIMA_2024 = {
    "giorni_caldi": 67,          # Tmax > 30 °C, media 14 stazioni di pianura
    "giorni_caldi_media": 42,    # media 1991-2020
    "mare_anomalia": 1.9,        # °C vs 1995-2023, Trieste a 2 m
    "piogge_vs_media": 25,       # % in più rispetto al 1991-2020
    "piogge_estive_mm": 251,     # media 29 stazioni pianura e costa
}

PIOGGE_ESTIVE_TREND = -20  # mm per decennio dal 1961, statisticamente significativo

CRIOSFERA = {
    "Alpi Giulie (volume, un secolo)": -96,
    "Ghiacciaio del Canin (volume)": -99,
    "Occidentale del Montasio (volume)": -78,
}

# ---------------------------------------------------------------- idroelettrico
FONTE_IDRO = "PER FVG 2024, situazione impianti al 31/12/2023"

IDRO_PARCO = {
    "Impianti": 268,
    "Potenza efficiente lorda (MW)": 528.7,
    "Producibilità media annua (GWh)": 1830.8,
}
