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

# ---------------------------------------------------------------- province
FONTE_PROVINCE = "Terna, Statistiche Regionali 2024 (dati al 31/12/2024)"

# Produzione lorda totale e rinnovabile per fonte, GWh, 2024
PRODUZIONE_PROVINCE = {
    "Gorizia": {"totale": 500.5, "Idrico": 52.2, "Fotovoltaico": 74.1, "Bioenergie": 191.4},
    "Pordenone": {"totale": 1511.8, "Idrico": 946.5, "Fotovoltaico": 286.9, "Bioenergie": 196.3},
    "Trieste": {"totale": 379.7, "Idrico": 0.0, "Fotovoltaico": 41.0, "Bioenergie": 70.9},
    "Udine": {"totale": 4342.7, "Idrico": 1164.4, "Fotovoltaico": 559.4, "Bioenergie": 223.3},
}

POTENZA_PROVINCE = {  # MW lordi, 2024
    "Gorizia": {"totale": 253.9, "rinnovabile": 147.1},
    "Pordenone": {"totale": 616.4, "rinnovabile": 600.8},
    "Trieste": {"totale": 349.4, "rinnovabile": 68.9},
    "Udine": {"totale": 2262.8, "rinnovabile": 1063.5},
}

# Consumi elettrici 2024, GWh
CONSUMI_ELETTRICI_PROVINCE = {"Gorizia": 691.9, "Pordenone": 2059.3,
                              "Trieste": 1042.9, "Udine": 5510.4}
CONSUMI_ELETTRICI_SETTORE = {"Industria": 5751.7, "Servizi": 2187.1, "Domestico": 1365.8}
CONSUMI_ELETTRICI_TOTALE = 9304.6
CONSUMI_FS_TRAZIONE = 190.9

POTENZA_FONTE_2024 = {  # MW lordi
    "Fotovoltaico": 1210.8, "Idrico": 528.9, "Termoelettrico": 1530.9,
    "Accumuli stand alone": 212.0,
}

# ---------------------------------------------------------------- reti, dettaglio
FONTE_RETI_REPORT = "Audizioni IV Commissione consiliare, 21/04/2026 (Terna, e-distribuzione, AcegasApsAmga, SECAB)"

# Avanzamento verso il target 2030, in MW
BURDEN_SHARING_MW = {
    "In esercizio (2021–2025)": 940,
    "Autorizzato in alta tensione": 310,
    "Autorizzato in media tensione": 350,
    "Quota residua al 2030": 360,
}
BURDEN_SHARING_TARGET_MW = 1960

BESS = {
    "Impianti autorizzati o in istruttoria": 26,
    "Potenza richiesta (MW)": 1405.5,
    "Fabbisogno stimato dal piano (MW)": 300,
    "Impianto già attivo a Pavia di Udine (MW)": 200,
}

INTERCONNESSIONI = {
    "Redipuglia–Divaccia (Slovenia), 380 kV": {"attuale": 700, "prevista": 1200},
    "Merchant line Tarvisio–Arnoldstein (Austria), 132 kV": {"attuale": 160, "prevista": 160},
}

DISTRIBUTORI = {
    "e-distribuzione": {"clienti": 630_000, "energia_gwh": None,
                        "nota": "quasi tutto il territorio non urbano"},
    "AcegasApsAmga – Trieste": {"clienti": 142_000, "energia_gwh": 615,
                                "nota": "picco 130–140 MW; il porto chiede 160 MW, di cui 80 per il cold ironing"},
    "AcegasApsAmga – Gorizia": {"clienti": 22_500, "energia_gwh": 120,
                                "nota": "oltre 40 MW di richieste fotovoltaiche, più della punta cittadina"},
    "SECAB (Alto Bût)": {"clienti": 5_500, "energia_gwh": 45,
                         "nota": "5 centrali idroelettriche, surplus strutturale immesso in rete"},
}

SATURAZIONE_PROVINCE = {"Udine": 50, "Pordenone": 25}  # % di trasformatori in zona rossa
TASSO_REALIZZAZIONE = 50  # % di impianti autorizzati che viene davvero costruito

DECRETO_BOLLETTE = {
    "riferimento": "D.L. 21/2026, art. 7",
    "misure": [
        ("First ready, first connect",
         "La priorità di allacciamento premia i progetti già autorizzati e pronti a partire, "
         "non chi ha presentato domanda per primo. Le istanze speculative decadono."),
        ("Overbooking",
         "Terna e i distributori possono rilasciare preventivi oltre la capacità reale del nodo, "
         "contando statisticamente sul 50% di rinunce."),
        ("Open season",
         "Assegnazione competitiva della capacità di rete a cadenza trimestrale, "
         "prima edizione attesa a novembre 2026."),
    ],
}

# ---------------------------------------------------------------- idrogeno
FONTE_H2 = "Regione FVG, Strategia Regionale per l'Idrogeno"

H2_NAHV = {
    "Finanziamento europeo (mln €)": 25,
    "Organizzazioni partner": 37,
    "Durata (mesi)": 72,
    "Paesi coinvolti": 3,
}

H2_PROGETTI = [
    {"nome": "Hydrogen Hub Trieste", "soggetto": "AcegasApsAmga",
     "finanziamento_mln": 15.8, "elettrolisi_mw": 5.0, "fv_dedicato_mwp": 4.85,
     "produzione_ton_anno": 370, "da_fv_ton_anno": 116, "stoccaggio_ton": 2,
     "stato": "AIA rilasciata a febbraio 2025, avvio previsto entro metà 2026",
     "nota": "Area ex Esso sul Canale Navigabile, acqua dal termovalorizzatore vicino."},
    {"nome": "Stazione di rifornimento di Monfalcone", "soggetto": "APT Gorizia",
     "finanziamento_mln": None, "elettrolisi_mw": None, "fv_dedicato_mwp": None,
     "produzione_ton_anno": None, "da_fv_ton_anno": None, "stoccaggio_ton": None,
     "stato": "PNRR investimento 3.3",
     "nota": "Alimenta 15 autobus a idrogeno sulla linea Monfalcone–Staranzano–Ronchi."},
    {"nome": "Stazione di rifornimento di Porpetto", "soggetto": "PNRR",
     "finanziamento_mln": None, "elettrolisi_mw": None, "fv_dedicato_mwp": None,
     "produzione_ton_anno": None, "da_fv_ton_anno": None, "stoccaggio_ton": None,
     "stato": "PNRR investimento 3.3", "nota": "Attivazione della domanda locale di idrogeno."},
]

H2_MEZZI_TPL = {"Trieste": 10, "Monfalcone": 15}

H2_CRITICITA = [
    ("Rinnovabili insufficienti",
     "La capacità FER regionale potrebbe non bastare per produrre idrogeno rinnovabile "
     "senza sottrarlo ad altri usi: serve coordinare nuova capacità, flessibilità di rete "
     "e priorità d'impiego."),
    ("Competenze nelle PMI",
     "Gestione e manutenzione di impianti complessi richiedono formazione mirata, "
     "che oggi manca soprattutto nelle piccole imprese."),
    ("Localizzazione e accettabilità",
     "Servono aree idonee individuate in anticipo, riuso di siti industriali e "
     "co-localizzazione con infrastrutture esistenti."),
    ("Rete gas disomogenea",
     "In alcune porzioni di territorio l'accesso alla rete gas è irregolare, "
     "il che impone soluzioni logistiche alternative con costi maggiori."),
]

# Consumi elettrici industriali per settore merceologico, GWh (Terna, elaborazione Regione FVG)
CONSUMI_INDUSTRIA_MERCEOLOGICO = {
    2022: {"Siderurgia": 1980.0, "Legno e mobilio": 741.1, "Cartaria": 514.1,
           "Prodotti in metallo": 348.4, "Plastica e gomma": 320.5, "Alimentari": 298.2,
           "Chimica": 258.9, "Ceramiche e vetrarie": 235.7},
    2023: {"Siderurgia": 2018.4, "Legno e mobilio": 650.0, "Cartaria": 277.8,
           "Prodotti in metallo": 337.3, "Plastica e gomma": 305.2, "Alimentari": 293.2,
           "Chimica": 246.0, "Ceramiche e vetrarie": 274.6},
}
INDUSTRIA_TOTALE_GWH = {2022: 5827.9, 2023: 5536.9}

# ---------------------------------------------------------------- contesto regionale
CONTESTO = {
    "popolazione_2021": 1_201_510,
    "popolazione_2045": 1_133_201,
    "aziende_manifatturiere": 8_300,
    "quota_export_top5": 75,  # % del valore dell'export da siderurgia, meccanica, mezzi di trasporto, ...
}

# ---------------------------------------------------------------- emissioni totali
FONTE_EMISSIONI = "ISPRA, annuario statistico (serie regionale); ARPA FVG, inventario GHG 2021"

# Gas serra totali regionali, kt CO2eq. Attenzione: ISPRA avverte che la sequenza
# non e' una vera serie storica, perche' la metodologia e' cambiata nel tempo.
EMISSIONI_TOTALI_FVG = {
    1990: 15015.9, 1995: 15129.2, 2000: 14312.5, 2005: 16208.3,
    2010: 14895.0, 2015: 11706.5, 2017: 11772.5, 2019: 11297.2,
}
EMISSIONI_QUOTA_NAZIONALE = 3          # % del totale italiano
EMISSIONI_PRO_CAPITE_2019 = 9.3        # t CO2eq per abitante

# Inventario ARPA FVG 2021, metodologia IPCC
INVENTARIO_ARPA = {
    "anno": 2021,
    "quota_energia": 86,               # % del totale dalla macrocategoria Energia
    "quota_trasporto_strada": 25,      # % del totale dal solo trasporto su strada
    "ambiti": ["Trasporti", "Combustione nell'industria", "Riscaldamento",
               "Industrie energetiche"],
}

TARGET_FVGREEN = {
    "riferimento": "Legge regionale 4/2023 (FVGreen)",
    "anno_neutralita": 2045,
}

# ---------------------------------------------------------------- idrogeno, conti
# Resa fotovoltaica regionale usata per i confronti: media FVG da Terna 2024
# (961,4 GWh su 1.210,8 MW installati). Serve a tradurre TWh in MWp e in ettari.
# Media FVG 2019-2022 (Terna), anni in cui il parco era stabile e il rapporto
# produzione/potenza non e' falsato dalla crescita. Dal 2023 il fotovoltaico
# regionale e' raddoppiato in due anni: dividere per la potenza di fine anno
# darebbe 794 kWh/kWp, che non e' la resa ma l'effetto degli impianti entrati
# in esercizio a dicembre. Coerente con le 1.100 kWh/kWp indicate da Giusti
# per il Nord Italia su tetto.
PV_ORE_EQUIVALENTI = 1040      # kWh per kWp installato, all'anno
PV_ETTARI_PER_MWP = 1.38       # da progetti autorizzati: 2.268 ha per 1.645,8 MW
H2_KWH_PER_KG = 55             # consumo elettrico dell'elettrolisi, stima corrente

# ---------------------------------------------------------------- costi ed energia
FONTE_PREZZI = "ARERA, Relazione annuale (PUN medio 2025); GSE, prezzi minimi garantiti"

PUN_MEDIO_2025 = 115.9      # €/MWh, il più alto tra le principali borse europee
PREZZO_MINIMO_GARANTITO = {2025: 46.4, 2026: 47.5}   # €/MWh, ritiro dedicato ARERA
RITIRO_DEDICATO_FV_NORD = (75, 115)                  # €/MWh percepiti al Nord nel 2026

# CAPEX di riferimento, €/kW. Valori d'uso corrente sul mercato italiano:
# vanno cambiati dall'interfaccia, non sono un dato ufficiale.
CAPEX_DEFAULT = {
    "Fotovoltaico utility scale": 700,
    "Fotovoltaico su capannoni": 1000,
    "Fotovoltaico residenziale": 1300,
    "Eolico onshore": 1500,
}
# Ore equivalenti annue. Il fotovoltaico è misurato sul FVG (Terna 2024);
# l'eolico è un valore di letteratura, perché in regione non ce n'è.
ORE_EQUIVALENTI = {
    "Fotovoltaico utility scale": 1200,     # a terra al Nord, con tracker su una parte
    "Fotovoltaico su capannoni": 1040,      # misurato in FVG, 2019-2022
    "Fotovoltaico residenziale": 1000,      # falde non ottimali, ombreggiamenti
    "Eolico onshore": 2200,                 # sito di crinale a 5,5 m/s su 100 m
}
OPEX_QUOTA = {  # % del CAPEX all'anno
    "Fotovoltaico utility scale": 1.5, "Fotovoltaico su capannoni": 1.8,
    "Fotovoltaico residenziale": 2.0, "Eolico onshore": 2.5,
}
# Suolo occupato, ha/MW. Il PV a terra viene dai 175 progetti autorizzati in FVG.
# Per l'eolico si contano solo piazzole e viabilità, non l'area interclusa.
SUOLO_HA_MW = {
    "Fotovoltaico utility scale": 1.38, "Fotovoltaico su capannoni": 0.0,
    "Fotovoltaico residenziale": 0.0, "Eolico onshore": 0.024,
}
# Per l'eolico il suolo davvero sottratto ad altri usi e' plinto piu' piazzola:
# circa 1.000 m2 per un aerogeneratore da 4,2 MW. La "servitu' di sorvolo" -
# la proiezione a terra del rotore - e' 15.000 m2, ma resta terreno coltivabile.
EOLICO_SERVITU_HA_MW = 0.36

# Emissioni di ciclo di vita, gCO2/kWh (Politecnico di Milano, Renewable Energy
# Report 2022). Piu' basse dei valori IPCC usati nel simulatore nazionale.
LCA_POLIMI = {
    "Carbone": 1023, "Gas": 436, "Fotovoltaico": 19,
    "Eolico": 12, "Idroelettrico": 11, "Nucleare": 5,
}
EPBT_ANNI = {"Fotovoltaico": 0.43, "Eolico": 1.04}   # tempo di ritorno energetico

# Bilancio elettrico regionale 2024 (Terna): la regione consuma molto piu' di
# quanto produce, ed e' il dato che rende concreta la parola "import".
RICHIESTA_ELETTRICA_2024 = 9814.7      # GWh
DEFICIT_ELETTRICO_2024 = -3341.4       # GWh, pari al -34,0% della richiesta
IMPIANTI_EOLICI_FVG = 4                # potenza non rilevabile nelle statistiche Terna
