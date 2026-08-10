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

# ---------------------------------------------------------------- eolico misurato
FONTE_EOLICO = "RSE, Atlante Eolico (dbeta.rse-web.it), dati a 100 m sul livello del terreno"

# Punti campionati sull'Atlante Eolico RSE. `prod_100` e' la producibilita'
# specifica in ore equivalenti annue a 100 m, `dens_100` la densita' di potenza
# in W/m2, `weib_100` il fattore di forma di Weibull.
EOLICO_PUNTI = [
    {"nome": "Carso triestino", "lat": 45.607, "lon": 13.813, "quota": 0,
     "vento_100": 6.46, "dens_100": 591.34, "prod_100": 3168.9, "weib_100": 1.18, "dist_cp": 1.4},
    {"nome": "Colli Orientali (alto)", "lat": 46.091, "lon": 13.542, "quota": 470,
     "vento_100": 6.18, "dens_100": 448.64, "prod_100": 2994.0, "weib_100": 1.31, "dist_cp": 11.0},
    {"nome": "Colli Orientali", "lat": 46.079, "lon": 13.541, "quota": 185,
     "vento_100": 6.11, "dens_100": 439.13, "prod_100": 2945.1, "weib_100": 1.31, "dist_cp": 11.0},
    {"nome": "Laguna di Grado", "lat": 45.710, "lon": 13.474, "quota": 3,
     "vento_100": 5.25, "dens_100": 296.40, "prod_100": 2279.6, "weib_100": 1.33, "dist_cp": 7.7},
    {"nome": "Alpi Giulie", "lat": 46.352, "lon": 13.416, "quota": 1304,
     "vento_100": 4.67, "dens_100": 289.60, "prod_100": 2098.2, "weib_100": 1.05, "dist_cp": 9.6},
    {"nome": "Alpi Carniche", "lat": 46.571, "lon": 13.044, "quota": 1897,
     "vento_100": 4.87, "dens_100": 232.70, "prod_100": 2032.9, "weib_100": 1.20, "dist_cp": 15.5},
    {"nome": "Pianura isontina", "lat": 45.900, "lon": 13.526, "quota": 26,
     "vento_100": 3.28, "dens_100": 64.42, "prod_100": 1009.7, "weib_100": 1.31, "dist_cp": 5.4},
    {"nome": "Bassa friulana", "lat": 45.901, "lon": 13.508, "quota": 44,
     "vento_100": 3.29, "dens_100": 63.17, "prod_100": 977.3, "weib_100": 1.34, "dist_cp": 5.5},
]

# ---------------------------------------------------------------- centrali termoelettriche
FONTE_CENTRALI = "Piano Energetico Regionale FVG, cap. 4, integrato con documentazione di impianto"

# Le coordinate sono al centro del sito, non rilevate: servono a collocare
# l'impianto sul territorio, non a identificarne il perimetro.
CENTRALI_TERMO = [
    {"nome": "Torviscosa (Edison)", "comune": "Torviscosa", "prov": "UD",
     "mw": 790, "combustibile": "Gas naturale", "tecnologia": "Ciclo combinato cogenerativo",
     "lat": 45.817, "lon": 13.283, "stato": "In esercizio",
     "nota": "Il 54,1% del termoelettrico tradizionale regionale. Fornisce vapore allo "
             "stabilimento Caffaro e alle industrie chimiche limitrofe."},
    {"nome": "Monfalcone (A2A)", "comune": "Monfalcone", "prov": "GO",
     "mw": 336, "combustibile": "Carbone", "tecnologia": "Termoelettrico tradizionale",
     "lat": 45.795, "lon": 13.545, "stato": "Dismissione",
     "nota": "Da maggio 2024 non più abilitata ai mercati dell'energia. Accordo con la Regione "
             "per la conversione a ciclo combinato a gas, predisposto per l'idrogeno."},
    {"nome": "Servola (Elettra Produzione)", "comune": "Trieste", "prov": "TS",
     "mw": 175, "combustibile": "Gas naturale e off-gas siderurgico",
     "tecnologia": "Ciclo combinato cogenerativo", "lat": 45.617, "lon": 13.800,
     "stato": "In esercizio",
     "nota": "Brucia una miscela di metano e gas di processo dell'ex stabilimento siderurgico."},
    {"nome": "Elettrogorizia", "comune": "Gorizia", "prov": "GO",
     "mw": 49.9, "combustibile": "Gas naturale", "tecnologia": "Ciclo combinato",
     "lat": 45.933, "lon": 13.617, "stato": "In esercizio",
     "nota": "In esercizio dal 2004, immette direttamente in alta tensione a 132 kV."},
    {"nome": "Termovalorizzatore di Trieste (Hestambiente)", "comune": "Trieste", "prov": "TS",
     "mw": 14.9, "combustibile": "Rifiuti urbani e speciali", "tecnologia": "Co-incenerimento a griglia",
     "lat": 45.633, "lon": 13.800, "stato": "In esercizio",
     "nota": "Tre linee, 197.000 t/anno autorizzate."},
    {"nome": "Cartiera di Tolmezzo", "comune": "Tolmezzo", "prov": "UD",
     "mw": 17.1, "combustibile": "Gas naturale", "tecnologia": "Cogenerazione industriale",
     "lat": 46.400, "lon": 13.017, "stato": "In esercizio", "nota": "Autoproduzione di stabilimento."},
    {"nome": "Cartiera di Ovaro", "comune": "Ovaro", "prov": "UD",
     "mw": 11.2, "combustibile": "Gas naturale", "tecnologia": "Cogenerazione industriale",
     "lat": 46.483, "lon": 12.888, "stato": "In esercizio", "nota": "Autoproduzione di stabilimento."},
    {"nome": "Mistral FVG (Spilimbergo)", "comune": "Spilimbergo", "prov": "PN",
     "mw": 3.0, "combustibile": "Rifiuti speciali", "tecnologia": "Forno a tamburo rotante",
     "lat": 46.117, "lon": 12.900, "stato": "In esercizio",
     "nota": "Il 20% della produzione copre l'autoconsumo, il resto va in rete."},
]

# ---------------------------------------------------------------- intestazione e note
AUTORE = {
    "nome": "Matteo De Piccoli",
    "ente": "APE FVG",
    "sito": "https://www.ape.fvg.it/",
    "email": "matteo.depiccoli@ape.fvg.it",
    "github": "https://github.com/matteo-dep",
    "linkedin": "https://www.linkedin.com/in/matteo-de-piccoli-2a17a5163",
}

# Etichette di fonte usate sotto i grafici
F_TERNA = "Terna, Dati Statistici (dati.terna.it)"
F_TERNA_REG = "Terna, Statistiche Regionali 2024"
F_PER = "Piano Energetico Regionale FVG 2024"
F_RSE = "RSE, Geoportale ETA (dbeta.rse-web.it) — CC BY-SA 4.0"
F_REGIONE = "Portale cartografico regionale FVG (EAGLE)"
F_AUDIZIONI = "Audizioni IV Commissione consiliare, 21/04/2026"
F_ARPA = "ARPA FVG, «Segnali dal clima in FVG»"
F_ISPRA = "ISPRA, annuario statistico; ARPA FVG, inventario GHG"
F_ELAB = "elaborazione propria sui dati citati"

# Alias di comodo usati dall'app
F_H2 = FONTE_H2
F_EOLICO = FONTE_EOLICO
F_CENTRALI = FONTE_CENTRALI
F_CLIMA = FONTE_CLIMA
F_PROVINCE = FONTE_PROVINCE

# ---------------------------------------------------------------- emissioni, dettaglio
FONTE_INVENTARIO = "ARPA FVG, inventario regionale dei gas serra 2021 (metodologia IPCC)"

# Quote sul totale regionale, %. Le quattro macrocategorie IPCC.
EMISSIONI_MACRO = {"Energia": 86, "AFOLU (agricoltura e uso del suolo)": 7,
                   "IPPU (processi industriali)": 5, "Rifiuti": 2}

# Dettaglio della macrocategoria Energia, in % del totale regionale.
EMISSIONI_ENERGIA = {
    "Trasporti": 27.4,
    "Riscaldamento": 18.6,
    "Industrie manifatturiere": 18.6,
    "Industrie energetiche": 17.8,
    "Emissioni fuggitive": 2.1,
}

# Composizione del trasporto su strada, in % del solo trasporto su strada
# (che a sua volta vale il 25% del totale regionale).
TRASPORTO_STRADA = {
    "Autovetture": 69.3, "Veicoli industriali oltre 3,5 t e autobus": 13.4,
    "Veicoli industriali sotto 3,5 t": 10.8, "Motocicli": 6.6,
}
TRASPORTO_STRADA_QUOTA = 25   # % del totale regionale

# Gli assorbimenti forestali sono di segno opposto: si sottraggono.
ASSORBIMENTI_FORESTALI = 25   # % delle emissioni regionali compensate, 2021
ASSORBIMENTI_ITALIA = 10      # % media nazionale, per confronto

# Consumi finali per settore, ktep (EUROSTAT/ENEA, ripresi nel PER)
CONSUMI_SETTORE_STORICO = {
    2010: {"Industria": 1325, "Civile": 1307, "Trasporti": 715, "Agricoltura e pesca": 34},
    2015: {"Industria": 1152, "Civile": 1219, "Trasporti": 550, "Agricoltura e pesca": 55},
    2019: {"Industria": 1272, "Civile": 1285, "Trasporti": 604, "Agricoltura e pesca": 59},
    2020: {"Industria": 1202, "Civile": 1239, "Trasporti": 533, "Agricoltura e pesca": 61},
    2021: {"Industria": 1333, "Civile": 1288, "Trasporti": 649, "Agricoltura e pesca": 76},
}
QUOTE_SETTORE_CONFRONTO = {   # % dei consumi finali, FVG contro Italia (2021)
    "Industria": (40.0, 22.0), "Civile": (38.5, 43.7), "Trasporti": (19.4, 31.2),
}

# ---------------------------------------------------------------- clima, scenari
# Gradi giorno: quanto si scalda e quanto si raffresca, oggi e a fine secolo.
# HDD = riscaldamento, CDD = raffrescamento. Fonte: piattaforma CLiNE (ARPA FVG),
# riferimento 1976-2005.
GRADI_GIORNO = {
    "riscaldamento_pianura_oggi": 4500,
    "riscaldamento_pianura_2100_rcp85": 3000,
    "hdd_malborghetto_rcp85_2071_2100": -1381,   # anomalia, °C
    "cdd_fagagna_rcp85_2071_2100": 472,          # anomalia, °C
}
SCENARI_RCP = {
    "RCP2.6": "Forte riduzione delle emissioni, Accordo di Parigi rispettato",
    "RCP4.5": "Scenario intermedio",
    "RCP8.5": "Emissioni in continua crescita, «business as usual»",
}
ZONA_CLIMATICA = {
    "oggi": "E (zona fredda) — riscaldamento dal 15 ottobre al 15 aprile, fino a 14 ore al giorno",
    "rcp85_fine_secolo": "D (zona fresca) — dal 1° novembre al 15 aprile, fino a 12 ore",
}

# Eventi meteorologici rilevanti del 2025 in FVG (ARPA FVG)
EVENTI_2025 = [
    ("13 marzo", "Stagione convettiva precocissima", "Grandinate e quattro supercelle.", 2),
    ("22 maggio", "Temporali in pianura", "Piogge intense localizzate e alcune trombe d'aria.", 2),
    ("26 giugno", "Caldo intenso e temporali forti",
     "Grandine di grosse dimensioni su tutta la pianura, vento forte.", 3),
    ("11 e 27 luglio", "Temporali e grandinate in pianura", "", 2),
    ("29 agosto e 2 settembre", "Temporali stazionari nel Triestino",
     "Tra 100 e 200 mm in poche ore, allagamenti e danni.", 3),
    ("16 settembre", "Supercella temporalesca",
     "Raffiche forti e grandine media, danni notevoli da Udine a Trieste.", 3),
    ("24 ottobre", "Temporale a Trieste",
     "Grandine minuta con accumuli al suolo di alcuni centimetri.", 2),
    ("16-17 novembre", "Alluvione del bacino dello Judrio",
     "Oltre 200 mm in 12 ore da un sistema autorigenerante stazionario. "
     "Lo Judrio esonda e allaga Versa con 1-2 m d'acqua e fango; una collina frana "
     "su Brazzano di Cormòns causando due vittime e distruggendo tre abitazioni. "
     "Un evento simile non accadeva dal 29 agosto 2003, l'alluvione della Val Canale.", 5),
]

# Rischi climatici per il sistema energetico (EUCRA 2023, ripreso da ARPA FVG)
CATENA_IMPATTO = [
    ("Generazione", "Meno idroelettrico",
     "Siccità e riduzione delle precipitazioni estive tagliano la producibilità."),
    ("Generazione", "Meno termoelettrico",
     "Acqua di raffreddamento più calda e più scarsa abbassa il rendimento."),
    ("Generazione", "Danni agli impianti rinnovabili",
     "Grandine ed eventi estremi colpiscono soprattutto il fotovoltaico."),
    ("Trasmissione", "Meno capacità di linee e trasformatori",
     "Il calore riduce la portata delle linee proprio nelle ore di punta."),
    ("Trasmissione", "Danni all'infrastruttura",
     "Alluvioni e frane interrompono la fornitura."),
    ("Domanda", "Più energia per il raffrescamento",
     "Il picco di domanda si sposta dall'inverno all'estate."),
    ("Domanda", "Domanda in crescita per l'elettrificazione",
     "Mobilità, riscaldamento e industria aggiungono carico."),
]


# ---------------------------------------------------------------- uso del suolo
FONTE_SAU = "ISTAT, censimento generale dell'agricoltura 2020; ISPRA, consumo di suolo"

SAU_FVG_HA = 218_000          # superficie agricola utilizzata
SUPERFICIE_FVG_HA = 793_240   # superficie regionale
# Termini di paragone per capire quanto sia grande una superficie
PARAGONI_SUOLO = {
    "Un campo da calcio regolamentare": 0.71,
    "Un ipermercato con parcheggio": 2.5,
    "L'aeroporto di Ronchi dei Legionari": 200.0,
}

# Nuove installazioni fotovoltaiche per categoria, primi mesi del 2026 (Terna).
# Serve a rispondere alla domanda «il fotovoltaico mangia i campi?» con i numeri
# di cosa si sta installando davvero, non con le impressioni.
PV_NUOVE_2026 = {
    "Residenziale (fino a 20 kW)": {"mw": 28.21, "impianti": 4644},
    "Tetti commerciali e artigianali (20-200 kW)": {"mw": 1.33, "impianti": 78},
    "Tetti industriali e piccoli campi (200 kW-1 MW)": {"mw": 0.73, "impianti": 9},
    "Utility scale (oltre 1 MW)": {"mw": 1.22, "impianti": 1},
}

# Ore equivalenti per tipologia di installazione. Il residenziale rende meno:
# falde non ottimali, ombreggiamenti, nessun inseguimento. L'utility scale usa
# tracker su una parte del campo.
PV_ORE_PER_TIPO = {
    "Residenziale (fino a 20 kW)": 1000,
    "Tetti commerciali e artigianali (20-200 kW)": 1040,
    "Tetti industriali e piccoli campi (200 kW-1 MW)": 1100,
    "Utility scale (oltre 1 MW)": 1200,
}

FONTE_BIOMASSA_2015 = ("Regione FVG, Direzione risorse agricole e forestali, "
                       "database impianti a biomassa legnosa da finanziamenti pubblici, "
                       "settembre 2015")
FONTE_ARERA = "ARERA, dati di prelievo dei clienti domestici, anno 2022"


# Obiettivo di copertura elettrica rinnovabile al 2030 dichiarato nella
# Strategia Regionale per l'Idrogeno: e' il vincolo dentro cui l'idrogeno
# regionale deve trovare la propria elettricita'.
TARGET_FER_ELETTRICA_2030 = {
    "copertura_pct": 79,          # % dell'elettricita' da fonti rinnovabili
    "nuova_capacita_gw": 3.3,     # GW aggiuntivi rispetto al 2020
    "riferimento": "Strategia Regionale per l'Idrogeno, in coerenza con il PNIEC",
}

# ---------------------------------------------------------------- confronto nazionale
FONTE_CIRO = ("Italy for Climate, database CIRO delle regioni sul clima, "
              "aggiornamento febbraio 2026")

# Indicatori del FVG confrontati con la media italiana. Il segno dice se il
# valore piu' alto e' un pregio o un difetto.
CIRO_INDICATORI = [
    ("Rinnovabili", "Conseguimento del target 2030", 46, 31, "%", True,
     "Seconda regione d'Italia."),
    ("Rinnovabili", "Quota di energia da fonti rinnovabili", 22.5, 19, "%", True, ""),
    ("Energia", "Gas naturale sul mix energetico", 48, None, "%", False,
     "Piu' di meta' del fabbisogno."),
    ("Energia", "Carbone sul mix energetico", 4, None, "%", False, ""),
    ("Edifici", "Edifici in classe A", 11, None, "%", True, ""),
    ("Edifici", "Quota elettrica dei consumi degli edifici", 25, 31, "%", True, ""),
    ("Industria", "Quota elettrica dei consumi industriali", 43, 39, "%", True, ""),
    ("Agricoltura", "Superficie agricola biologica", 10, 20, "%", True, ""),
    ("Vulnerabilita", "Consumo di suolo", 8, None, "%", False,
     "Sopra la media nazionale."),
    ("Vulnerabilita", "Perdite della rete idrica", 42, None, "%", False, ""),
]

CIRO_SINTESI = {
    "eventi_estremi_2024": "prima regione d'Italia per numero di eventi estremi "
                           "in rapporto alla superficie",
    "comunita_energetiche_2024": 28,
    "impianti_biogas_stimati": 90,
}

# ---------------------------------------------------------------- hard to abate
# Settori in cui l'idrogeno e' candidato perche' l'elettrificazione diretta e'
# difficile: alta temperatura di processo, riduzione chimica, trasporto pesante
# a lunga percorrenza. I consumi elettrici sono Terna 2023, per settore
# merceologico: misurano la taglia del settore, non il suo fabbisogno di idrogeno.
HARD_TO_ABATE = [
    ("Siderurgia", 2018.4, "Forni elettrici e laminatoi. Il gas nei forni di "
     "riscaldo e' sostituibile con idrogeno; la fusione e' gia' elettrica.", "alto"),
    ("Ceramiche, vetrarie e minerali non metalliferi", 274.6,
     "Forni fusori continui oltre i 1.500 °C: l'elettrificazione diretta e' "
     "tecnicamente possibile ma costosa e non matura.", "alto"),
    ("Cartaria", 277.8, "Vapore di processo a media temperatura: qui la pompa di "
     "calore industriale e' spesso piu' conveniente dell'idrogeno.", "basso"),
    ("Chimica", 246.0, "Usa gia' idrogeno come materia prima, non come combustibile: "
     "sostituirlo con idrogeno rinnovabile e' la via piu' diretta.", "alto"),
    ("Prodotti in metallo", 337.3, "Trattamenti termici diffusi ma a temperatura "
     "moderata: in gran parte elettrificabili.", "basso"),
]
# Trasporto pesante: l'altro candidato, fuori dall'industria
TRASPORTO_PESANTE = {
    "quota_emissioni_trasporto_strada": 13.4,   # % dei mezzi oltre 3,5 t e autobus
    "nota": "Sul trasporto leggero e sulle autovetture la batteria ha gia' vinto: "
            "l'idrogeno resta candidato per la lunga percorrenza pesante e per la "
            "logistica portuale, dove peso e tempi di ricarica contano.",
}

# ---------------------------------------------------------------- costi di rete
FONTE_COSTI_RETE = ("stime su interventi dichiarati da e-distribuzione e Terna, "
                    "audizioni IV Commissione 21/04/2026")

# Il costo di rete non e' pubblicato per intervento: qui si parte da quanto e'
# stato dichiarato in audizione (36 interventi per 1.740 MVA) e da costi unitari
# di letteratura. Sono ordini di grandezza, modificabili dall'interfaccia.
COSTI_RETE = {
    "nuova_cabina_primaria_mln": 18.0,     # milioni di euro per nuova CP
    "ampliamento_cabina_mln": 5.0,         # milioni per ampliamento
    "connessione_eur_kw": 90,              # costo medio di allacciamento in MT
    "rinforzo_eur_kw_oltre_hosting": 220,  # costo aggiuntivo oltre l'hosting capacity
}
INTERVENTI_PROGRAMMATI = {"nuove_cabine": 14, "ampliamenti": 23, "mva": 1740}

# Parametri del parco elettrico regionale usati dal motore di scenario.
# Idro: potenza efficiente Terna 2024 ripartita fra fluente e modulabile;
# invaso dalle 12 grandi dighe, convertito in energia con un salto medio.
PARCO_BASE_FVG = {
    "pv_mw": 1210.8,
    "idro_fluente_mw": 200.0,
    "idro_bacino_mw": 330.0,
    "idro_bacino_mwh": 155_000.0,   # 167,6 mln m3 con salto medio 400 m
    "idro_afflusso_mw": 247.0,      # 2.163 GWh/anno di producibilita' media
    "bess_mw": 206.0,               # Pavia di Udine, unico in esercizio
    "bess_mwh": 824.0,              # 4 ore di scarica
    "gas_mw": 1530.9,
    "import_max_mw": 1500.0,
    "export_max_mw": 800.0,
}

# ---------------------------------------------------------------- agrifood FVG
FONTE_AGRIFOOD = "Agrifood FVG, sezione Bioeconomia e Dati statistici"

AGRIFOOD = {
    "seminativi_ha": 130_000,
    "biogas_impianti": 71,
    "biogas_taglia_media_kw": 700,
    "paglie_stoppie_t_ha": (3.5, 4.5),
    "foresta_certificata_pefc_ha": 81_913,
    "pioppeti_certificati_ha": 1_960,
    "quota_pefc_italia_pct": 9,
    "quota_pioppeti_italia_pct": 35,
    "legno_da_foresta_mc_2014": 19_544,
    "legno_totale_mc_2014": 35_351,
    "quota_uso_energetico_pct": 19.12,
    "quota_legname_da_lavoro_pct": 80.88,
}

# ---------------------------------------------------------------- eventi estremi
FONTE_EVENTI = ("Legambiente, Osservatorio CittàClima; Italy for Climate, database CIRO; "
                "ARPA FVG per gli eventi del 2025")

# Conteggio degli eventi meteorologici estremi registrati in FVG.
# Attenzione: la crescita riflette anche il miglioramento della rilevazione,
# non solo l'aumento reale della frequenza.
EVENTI_ESTREMI_SERIE = {
    2015: 3, 2016: 2, 2017: 4, 2018: 6, 2019: 5, 2020: 7,
    2021: 6, 2022: 9, 2023: 14, 2024: 19, 2025: 8,
}
EVENTI_NOTA = (
    "Serie ricostruita da rassegne su base regionale: gli anni recenti sono rilevati "
    "meglio dei primi, quindi la pendenza va letta con cautela. Il 2025 conta i soli "
    "episodi documentati da ARPA FVG nel bilancio annuale, con criteri piu' stretti."
)
EVENTI_MEMORABILI = [
    (2003, "Alluvione della Val Canale", "29 agosto: due vittime, danni ingenti."),
    (2018, "Tempesta Vaia", "Ottobre: schianti forestali diffusi su Carnia e Prealpi."),
    (2023, "Stagione grandinigena record",
     "Grandinate ripetute su pianura friulana e Pordenonese."),
    (2024, "Prima regione d'Italia per eventi estremi per superficie",
     "Conteggio Italy for Climate su base CittaClima."),
    (2025, "Alluvione dello Judrio",
     "16-17 novembre: oltre 200 mm in 12 ore, due vittime a Brazzano di Cormons."),
]

# ---------------------------------------------------------------- idroelettrico
FONTE_IDRO_PER = ("Piano Energetico Regionale FVG, cap. 4; Terna e GSE; "
                  "Distretto Idrografico delle Alpi Orientali")

IDRO_QUADRO = {
    "impianti_2022": 247, "mw_2022": 528.3,
    "impianti_2023": 268, "mw_lordi_2023": 528.7, "mw_netti_2023": 522.6,
    "quota_su_fer_regionali": 94,     # % della produzione rinnovabile primaria
    "quota_su_produzione_lorda": 20,  # % della produzione elettrica lorda
    "posizione_italia_impianti": 5, "posizione_italia_potenza": 9,
    "quota_potenza_nazionale": (2.3, 2.8),
}

# La potenza e' concentrata dove ci sono i salti: Udine e Pordenone.
IDRO_PROVINCE_MW = {"Udine": 324.7, "Pordenone": 193.8, "Gorizia": 9.8, "Trieste": 0.0}

# Il parco e' polarizzato: pochi grandi impianti fanno quasi tutta la potenza.
IDRO_CONCENTRAZIONE = {
    "impianti_oltre_10mw": 12, "quota_potenza_oltre_10mw": 75,
    "quota_numero_oltre_1mw": 24, "quota_potenza_oltre_1mw": 93,
}

# Produzione lorda per anno: e' la firma della variabilita' idrologica.
IDRO_PRODUZIONE = {
    2021: {"gwh": 1983.66, "quota_mix": 25.5, "quota_fer": 57.7, "nota": "anno umido"},
    2022: {"gwh": 887.27, "quota_mix": 9.9, "quota_fer": None, "nota": "siccità estrema"},
    2023: {"gwh": 1506.30, "quota_mix": None, "quota_fer": None, "nota": "ripresa"},
    2024: {"gwh": 2177.70, "quota_mix": None, "quota_fer": None, "nota": "anno record"},
}
IDRO_MEDIA_2000_2022 = 1650    # GWh/anno
IDRO_CALO_2022 = -55.3         # % rispetto al 2021
IDRO_DEFICIT_PIOGGE_2022 = (30, 50)   # % sotto la media 1991-2020

# Produzione 2023 per tipologia di impianto, GWh
IDRO_TIPOLOGIE_2023 = {
    "Acqua fluente": 900.7, "Bacino": 428.1, "Serbatoio": 177.5,
}
IDRO_POMPAGGIO_2023 = 15.9     # GWh assorbiti per i cicli di accumulo

# I grandi sistemi di generazione
IDRO_SISTEMI = [
    {"nome": "A2A — asta del Tagliamento", "mw": 235.0, "gwh": 600,
     "impianti": "Ampezzo (62,1 MW) e Somplago (172,8 MW)",
     "nota": "Eredità delle opere SADE degli anni Quaranta e Cinquanta. Somplago è "
             "scavata in caverna a 600 m di profondità, tre turbine Francis da 60 MW, "
             "salto di 285 m. Restituisce al lago di Cavazzo, che fa da bacino di "
             "demodulazione ed evita l'hydropeaking sul Tagliamento. Gruppi rinnovati "
             "fra il 2011 e il 2015."},
    {"nome": "Edison — asta del Cellina", "mw": 140.0, "gwh": 500,
     "impianti": "30 impianti, fra cui Meduno e Barcis",
     "nota": "Il bacino di Barcis svolge un ruolo plurimo: regimazione delle piene "
             "autunnali, riserva irrigua estiva e generazione."},
    {"nome": "SECAB — Alto Bût", "mw": 10.8, "gwh": 44.5,
     "impianti": "5 centrali ad acqua fluente",
     "nota": "Cooperativa fondata a Paluzza nel 1911, serve 5.500 utenze su 170 km² con "
             "rete propria. I soci pagano il 40-43% in meno delle tariffe di mercato."},
]

IDRO_SECAB = {
    "Enfretors (Paluzza)": {"kw": 2583, "gwh": 11.5},
    "Noiariis (Sutrio)": {"kw": 2576, "gwh": 9.8},
    "Mieli (Comeglians)": {"kw": 1880, "gwh": 14.0},
    "Museis (Cercivento)": {"kw": 1800, "gwh": 7.2},
    "Fontanon (Timau)": {"kw": 380, "gwh": 1.7},
}

# Il Deflusso Ecologico ha sostituito il Deflusso Minimo Vitale dal 2021
DEFLUSSO_ECOLOGICO = {
    "riferimento": "Direttiva Acque 2000/60/CE, Distretto Idrografico delle Alpi Orientali",
    "obbligo_dal": 2021,
    "moltiplicatore_rilasci": (2, 3),   # volte il vecchio DMV
    "effetto": "Le micro-centrali e i mulini storici sono costretti a fermarsi per mesi "
               "nei periodi di magra estivi e invernali, rilasciando l'intera portata "
               "in alveo. È il vincolo che pesa di più sui piani di ammortamento dei "
               "piccoli produttori.",
}

# Dove può ancora crescere: non nuovi sbarramenti, ma efficientamento e reti minori
IDRO_POTENZIALE = {
    "revamping_mw": 44, "nuovi_mini_micro_mw": 45,
    "target_2030_gwh": 2837, "target_2045_gwh": 2693,
    "fonte_potenziale": "studi A2A ed ENEA ripresi nel PER",
}
IDRO_AZIONI = [
    ("Repowering degli impianti esistenti",
     "Sostituzione di turbine obsolete con modelli ad alto rendimento: è la sola strada "
     "per crescere, esaurita la disponibilità di grandi salti vergini."),
    ("Micro-idro su acquedotti",
     "Turbine sui salti geodetici delle condotte montane e civili: producono sfruttando "
     "la pressione dell'acqua potabile in discesa, senza alcun impatto sui fiumi."),
    ("Rilasci degli invasi irrigui",
     "Generazione sui rilasci già previsti per l'agricoltura, senza nuove derivazioni."),
    ("Turbine cinetiche sui canali di bonifica",
     "Moduli da 10 kW immersi nei canali artificiali, che sfruttano lo scorrimento "
     "superficiale senza dighe né deviazioni."),
    ("Nuovi pompaggi su invasi esistenti",
     "Al 2045 il fotovoltaico regionale triplicherà, generando forti eccedenze diurne: "
     "pompare di giorno e turbinare di notte è il modo per assorbirle."),
]
