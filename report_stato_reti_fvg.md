# Report Tecnico: Lo Stato delle Reti Elettriche di Trasmissione e Distribuzione in Friuli Venezia Giulia

Questo report analizza lo stato infrastrutturale, i progressi del mix energetico e la pianificazione dello sviluppo delle reti elettriche di trasmissione (TSO) e distribuzione (DSO) nella Regione Autonoma Friuli Venezia Giulia, basandosi sui dati consolidati emersi durante le audizioni ufficiali della IV Commissione Consiliare.

*Aggiornamento agosto 2026*: al quadro quantitativo delle audizioni è ora affiancata la **geometria reale della rete**, ricavata dal dataset OpenInfraMap (linee aeree, EPSG:6708, estrazione 27/08/2026) e ritagliata sul confine regionale ISTAT. Il documento è corredato dalla carta `mappa_rete_fvg.png`, dallo script che la genera (`mappa_rete_fvg.py`) e dal tracciato vettoriale `rete_elettrica_fvg.geojson`.

---

## 1. Quadro di Riferimento e Target Regionali (Burden Sharing 2030)

La pianificazione energetica regionale, guidata dalla legge **FVGreen (L.R. 4/2023)**, si propone l'obiettivo di raggiungere la **neutralità carbonica entro il 2045**, anticipando di cinque anni i target comunitari.

Il quadro intermedio al 2030 — allineato alla bozza del **Decreto Ministeriale Aree Idonee** — impone alla Regione l'installazione di una **potenza aggiuntiva da FER pari a 1.960 MW (circa 2 GW)** rispetto allo stato di fatto al 31 dicembre 2020.

| Voce | MW | Quota del target |
|---|---|---|
| In esercizio (connessi 2021-2025) | 940 | 48% |
| Autorizzati RTN (Alta Tensione, benestare Terna) | 310 | 16% |
| Autorizzati DSO (Media Tensione) | 350 | 18% |
| **Quota residua al 2030** | **360** | **18%** |

Soltanto 360 MW separano la regione dal target, a dimostrazione della validità della pipeline autorizzativa. Il vincolo si sta spostando dall'autorizzazione alla connessione.

---

## 2. La Rete di Trasmissione Nazionale (TSO — Terna S.p.A.)

### 2.1 Consistenza fisica

La geometria OpenInfraMap restituisce **4.955 tratte per 6.598 km** di linee aeree entro il confine regionale.

| Livello | Tratte | Lunghezza | Note |
|---|---|---|---|
| 380 kV | 18 | 200 km | anello di trasmissione primario |
| 220 kV | 30 | 234 km | evacuazione idroelettrico e confine sloveno |
| 132 kV | 228 | 1.345 km | sub-trasmissione, ossatura regionale |
| 60 kV | 8 | 197 km | **rete di trazione RFI**, non distribuzione |
| MT/BT taggata (0,4–35 kV) | 65 | 110 km | distribuzione con attributo di tensione |
| Non classificate | 4.606 | 4.512 km | tracciato noto, tensione non taggata in OSM |
| **Totale** | **4.955** | **6.598 km** | |

Due precisazioni necessarie. Le linee a **60 kV appartengono a RFI**: sono la rete di trazione ferroviaria e vanno tenute fuori dai conteggi sulla distribuzione. Le **4.606 tratte non classificate** (68% del totale) non sono rete minore: sono in larga parte distribuzione MT che OpenStreetMap mappa geometricamente ma senza attributo `voltage`. Vanno trattate come tracciato noto a tensione ignota.

Delle 276 tratte a 132 kV e oltre, **181 hanno una denominazione** per complessivi 1.399 km, il che rende il dataset utilizzabile per l'analisi nodo-per-nodo e non solo per la rappresentazione.

### 2.2 Assetto della rete e squilibrio su Redipuglia

La carta conferma quanto emerso nelle audizioni. L'anello a **400 kV** si chiude a ovest sulla stazione di Dugale (VR) e a est su **Redipuglia (GO)**; la dorsale **Udine Ovest – Cordignano** è la tratta più estesa del dataset con 49 km su due segmenti, affiancata dalla **Planais – Redipuglia** (18,5 km, operatore Terna dichiarato).

La **220 kV Somplago – Pordenone** (72 km su due tratte) e la **Somplago – Salgareda** (17,5 km) evacuano verso ovest la produzione idroelettrica carnica dei 235 MW di Somplago e Ampezzo, mentre la **Udine Nord Est – Buia** (28 km) la raccorda al nodo udinese. Verso est, **Monfalcone Termoelettrica – Padriciano** (27,6 km) e **Monfalcone Z.I. – Padriciano** (26,3 km) portano in doppia via la connessione con la Slovenia.

Lo squilibrio strutturale su Redipuglia è leggibile geometricamente: vi convergono la 380 kV da Planais, quella da Udine Ovest e i collegamenti transfrontalieri. Quattro tratte risultano in **doppia terna**, tutte a 380 kV tranne una a 380/220 kV.

### 2.3 Interconnessioni transfrontaliere

Il FVG svolge un ruolo di ponte energetico europeo:

* La linea a **380 kV Redipuglia – Divaccia (Slovenia)** e la doppia terna a **220 kV Padriciano (TS) – Divaccia** garantiscono una capacità commerciale di importazione storicamente limitata a **700 MW** per motivi di sicurezza, destinata a salire a **1.200 MW** con il completamento della razionalizzazione Redipuglia – Udine Ovest.
* La *Merchant Line* privata a **132 kV di Eneco Valcanale S.r.l.** collega Tarvisio con Arnoldstein (Austria) per **160 MW** di capacità aggiuntiva, con energia importata rinnovabile al 90%. Nel dataset compare come tratta **Greuth – Tarvisio**, 9,1 km, unica linea con operatore diverso da Terna, ENEL o RFI.

### 2.4 Sistemi di accumulo (BESS)

In FVG risultano **26 impianti BESS autorizzati o in corso di autorizzazione** per complessivi **1.405,5 MW** di competenza regionale e ministeriale, tra cui un impianto da 200 MW già attivo a **Pavia di Udine**, adiacente alla stazione Udine Sud. A fronte di un fabbisogno reale stimato in circa **300 MW**, le richieste superano i 1.300 MW: un rapporto di oltre 4 a 1 che segnala rischi di saturazione non coordinata e richiede una governance centralizzata.

---

## 3. La Rete di Distribuzione (DSO)

La distribuzione MT/BT in FVG è gestita da concessionari territoriali con contesti operativi profondamente diversificati.

### A. e-distribuzione S.p.A. (Gruppo Enel)

Principale distributore regionale, **630.000 clienti** sulla quasi totalità del territorio non urbano.

* **Capacità connessa:** 1,6 GW di potenza rinnovabile, di cui **1,25 GW fotovoltaici**. Metà di questa potenza (800 MW) è stata connessa nel solo triennio 2023-2025.
* **Hosting capacity immediata:** senza interventi strutturali sulle cabine primarie la rete accoglie **altri 500 MW**.
* **Piano di sviluppo:** 1,6 GW di nuova capacità tramite **23 adeguamenti** di cabine primarie esistenti e **14 nuove cabine primarie**.

### B. AcegasApsAmga S.p.A. (Gruppo Hera)

Gestisce le aree urbane e industriali di **Trieste** e **Gorizia**, con carichi fortemente concentrati.

* **Trieste:** 142.000 abitanti, 615 GWh/anno erogati, picco 130-140 MW. La sfida è la transizione della portualità: **160 MW di richieste di connessione passiva**, di cui 80 MW per il *cold ironing* delle banchine e 80 MW per piattaforme logistiche e polo ferroviario di Servola.
* **Gorizia:** 22.500 utenti, 120 GWh/anno. Richieste per oltre **40 MW di nuovo fotovoltaico** su aree industriali e aeroportuali — una taglia che supera la potenza di picco dell'intera città e richiede infrastrutture dedicate in AT.

### C. Le cooperative storiche alpine

* **SECAB (Alto Bût):** 5.500 utenze nei comuni di Paluzza, Ravascletto, Cercivento, Treppo Ligosullo e Sutrio, con una cabina primaria a 132 kV, 52 km di linee MT e 120 km in BT. Produce circa **45 GWh/anno** da 5 centrali idroelettriche (Enfretors 2.583 kW, Noiaris 2.576 kW, Museis 1.800 kW, Mieli 1.880 kW, Fontanone 380 kW), con surplus strutturale immesso in rete.
* **Idroelettrica Valcanale S.a.s.:** 250 km di rete e 100 cabine nel Tarvisiano, oltre alla merchant line transfrontaliera.
* **Forni di Sopra:** 70 km di linee MT/BT in dinamica di rete attiva — assorbe 3 MW in inverno, ne immette circa 3 in primavera.

---

## 4. La Saturazione Virtuale e il Cambio di Paradigma ("Decreto Bollette")

Il collo di bottiglia strutturale evidenziato dai gestori è la **saturazione virtuale**: sviluppatori speculativi "prenotano" capacità di connessione con richieste che non si traducono in cantieri. Secondo i dati regionali **solo il 50% degli impianti autorizzati viene effettivamente costruito**.

La provincia di **Udine** è la più critica, con circa il **50% dei trasformatori AT/MT in zona rossa**; a **Pordenone** la quota critica si attesta al **25%**.

Il **Decreto Bollette (D.L. 21/2026, art. 7)** introduce tre misure, pienamente operative dopo i regolamenti ARERA attesi entro fine agosto 2026:

1. **"First ready, first connect":** la priorità di allacciamento premia i progetti autorizzati e pronti alla cantierizzazione invece dell'ordine cronologico di domanda. Le istanze speculative decadono.
2. **Overbooking:** Terna e i distributori possono rilasciare preventivi in eccedenza rispetto alla capacità reale dei nodi, sulla statistica del 50% di rinuncia.
3. **Open Season:** assegnazione competitiva della capacità con cadenza trimestrale, prima edizione novembre 2026.

---

## 5. Prossimità della risorsa rinnovabile alla rete

La disponibilità della geometria consente di calcolare la **distanza reale** di ogni cella dell'Atlante Eolico RSE 2026 (griglia 1,42 km) dalla linea più vicina, sostituendo il campo `Dist_cp` (distanza dalla cabina primaria) finora usato come proxy.

I due indicatori **correlano solo a 0,59**: misurano cose diverse — una cabina di trasformazione contro un conduttore — e non sono intercambiabili. Dove serve valutare l'allacciamento di un impianto di taglia industriale, conta la distanza dalla linea AT.

| Zona | Celle ≥6 m/s | km² | v media | `Dist_cp` RSE | dist. ≥132 kV | dist. AAT |
|---|---|---|---|---|---|---|
| **Carso / Trieste** | 96 | 194 | 6,79 m/s | 2,50 km | **0,91 km** | 2,06 km |
| Alpi Giulie | 40 | 81 | 6,26 m/s | 11,12 km | 9,32 km | 28,63 km |
| Prealpi | 7 | 14 | 6,14 m/s | 9,62 km | 9,52 km | 16,55 km |

**52 celle su 58 sopra la soglia di bancabilità (6,5 m/s) si trovano entro 5 km da una linea ad alta tensione**, e sono quasi tutte concentrate sul Carso triestino. Le celle migliori — l'altopiano tra Basovizza, Monrupino e Opicina, con velocità fino a 7,99 m/s — hanno la linea a 180-300 metri.

Ne discende una conclusione controintuitiva rispetto all'impostazione corrente: **per l'eolico la rete non è il fattore limitante**. Il vincolo si sposta interamente sulla sovrapposizione di quelle aree con Natura 2000, la landa carsica e il vincolo paesaggistico. Nella cascata di riduzione del potenziale installabile, il coefficiente da calibrare con cura è quello ambientale, non quello infrastrutturale.

Vale l'inverso per la montagna: le Alpi Giulie hanno risorsa discreta (6,26 m/s medi) ma stanno a 28 km dalla rete AAT e 9 dalla AT, su terreno dove una nuova linea richiede tempi da 5 a 15 anni. Lì il vincolo di rete è reale e dirimente.

---

## 6. Indirizzo operativo per i tecnici comunali

1. **Pianificazione spaziale coordinata.** Nel definire le "Aree Idonee" comunali ai sensi del D.M. Aree Idonee, mappare le superfici FER e agrivoltaiche in **stretta prossimità di cabine primarie e linee esistenti**. Il file `rete_elettrica_fvg.geojson` è direttamente caricabile in QGIS per costruire i buffer.
2. **Distinguere i due indicatori di prossimità.** Per impianti MT conta la distanza dalla cabina primaria; per taglie industriali conta la distanza dalla linea AT. Usare l'uno al posto dell'altro introduce un errore sistematico (correlazione 0,59).
3. **Semplificazione amministrativa.** Portare i progetti locali — in particolare le Comunità Energetiche Rinnovabili — allo stato *ready-to-build* prima di novembre 2026, per accedere alle prime Open Season di Terna.

---

## Nota sulle fonti

I dati quantitativi su potenza, hosting capacity e pipeline autorizzativa derivano dalle audizioni della IV Commissione Consiliare (Terna S.p.A. — Paolo Cuccia; e-distribuzione S.p.A. — Giovanni Franzone; AcegasApsAmga; SECAB) e dal Piano Energetico Regionale.

La geometria della rete deriva da **OpenInfraMap / OpenStreetMap**, dato collaborativo con buona copertura su AT e AAT ma attributi incompleti e nessun carattere ufficiale. È adeguata all'analisi di prossimità e alla rappresentazione cartografica; **non** è utilizzabile per calcoli di capacità di trasporto, valutazioni di congestione o verifiche di vincolo autorizzativo, per i quali restano necessari i dati Terna e e-distribuzione.

I dati di risorsa eolica provengono dall'Atlante Eolico RSE, edizione 2026, griglia nazionale a 1,42 km.

### File allegati

| File | Contenuto |
|---|---|
| `mappa_rete_fvg.png` | carta a due pannelli: rete per livello di tensione, risorsa eolica con prossimità alla rete AT |
| `mappa_rete_fvg.py` | script di generazione della carta (sostituisce `grid_status_fvg.py`) |
| `rete_elettrica_fvg.geojson` | 4.955 tratte in WGS84 con attributi `name`, `operator`, `kV`, `livello`, `len_km` |
| `rse_fvg_2026.csv` | 3.823 celle RSE del FVG con i campi `dist_AT_km`, `dist_AAT_km`, `dist_linea_km` |
