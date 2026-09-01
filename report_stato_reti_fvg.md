# Report Tecnico: Lo Stato delle Reti Elettriche di Trasmissione e Distribuzione in Friuli Venezia Giulia

Questo report analizza lo stato infrastrutturale, i progressi del mix energetico e la pianificazione dello sviluppo delle reti elettriche di trasmissione (TSO) e distribuzione (DSO) nella Regione Autonoma Friuli Venezia Giulia, basandosi sui dati consolidati emersi durante le audizioni ufficiali della IV Commissione Consiliare.

Il documento è corredato da uno script Python (`grid_status_fvg.py`) e da una visualizzazione grafica (`grid_status_fvg.png`) progettati per rappresentare in modo rigoroso e intuitivo lo stato di avanzamento rispetto ai target di Burden Sharing al 2030 e la capacità di accoglienza (*hosting capacity*) della rete di distribuzione.

---

## 1. Quadro di Riferimento e Target Regionali (Burden Sharing 2030)

La pianificazione energetica regionale, guidata dalla legge **FVGreen (L.R. 4/2023)**, si propone l'ambizioso obiettivo di raggiungere la **neutralità carbonica entro il 2045**, anticipando di cinque anni i target comunitari ed europei.

Per traguardare questa transizione, il quadro intermedio al 2030 — allineato alla bozza del **Decreto Ministeriale Aree Idonee** — impone alla Regione Friuli Venezia Giulia l'installazione di una **potenza aggiuntiva da fonti energetiche rinnovabili (FER) pari a 1.960 MW (circa 2 GW)** rispetto allo stato di fatto al 31 dicembre 2020. 

Lo stato di avanzamento e la pipeline di progetti pronti alla cantierizzazione (*ready-to-build*) registrano i seguenti dati:
*   **In esercizio (connessi 2021-2025):** **940 MW**, pari al **48%** dell'obiettivo totale al 2030.
*   **Autorizzati RTN (Rete di Trasmissione Nazionale):** **310 MW** di progetti già benestariati da Terna e autorizzati sul livello di Alta Tensione (AT).
*   **Autorizzati DSO (Rete di Distribuzione):** **350 MW** di progetti autorizzati e pronti alla connessione in Media Tensione (MT).
*   **Quota residua al 2030:** Soltanto **360 MW** separano la regione dal raggiungimento del target di Burden Sharing al 2030, a dimostrazione della validità della pipeline autorizzativa regionale.

---

## 2. Lo Stato della Rete di Trasmissione Nazionale (TSO - Terna S.p.A.)

La Rete di Trasmissione Nazionale (RTN) in Friuli Venezia Giulia gestisce i flussi in Alta (132 kV) e Altissima Tensione (220-380 kV). 
*   **Infrastruttura Esistente:** La rete si compone di un anello a 400 kV che si chiude a ovest nella stazione di Dugale (VR) e a est nella stazione di **Redipuglia (GO)**. Questo assetto rende la rete fortemente squilibrata sul nodo di Redipuglia, dove confluiscono i flussi transfrontalieri provenienti dalla Slovenia.
*   **Interconnessioni Transfrontaliere:** Il FVG gioca un ruolo strategico di "ponte" energetico europeo:
    *   La linea a 380 kV **Redipuglia - Divaccia (Slovenia)** e la linea in doppia terna a 220 kV **Padriciano (TS) - Divaccia** garantiscono una capacità commerciale di importazione limitata storicamente a 700 MW per motivi di sicurezza, ma destinata a salire a **1.200 MW** con il completamento della razionalizzazione della linea Redipuglia - Udine Ovest.
    *   È attiva la *Merchant Line* privata a 132 kV della società **Eneco Valcanale S.r.l.**, che collega Tarvisio con Arnoldstein (Austria), garantendo un incremento di **160 MW** della capacità di scambio e l'importazione di energia pulita al 90% da fonti rinnovabili austriache.
*   **Sistemi di Accumulo (BESS):** La gestione dell'intermittenza della generazione FER (specialmente solare) richiede una forte capacità di stoccaggio. Attualmente in FVG vi sono **26 impianti BESS autorizzati o in corso di autorizzazione** per complessivi **1.405,5 MW** di competenza regionale e ministeriale (tra cui un grande impianto da 200 MW già attivo a Pavia di Udine adiacente alla stazione Udine Sud). A fronte di un fabbisogno reale stimato in circa **300 MW**, le richieste superano i **1.300 MW**, evidenziando rischi di saturazione non coordinata che necessitano di una governance centralizzata.

---

## 3. Lo Stato della Rete di Distribuzione (DSO)

La distribuzione dell'energia elettrica a Media e Bassa Tensione (MT/BT) in FVG è gestita da molteplici concessionari territoriali, caratterizzati da contesti operativi profondamente diversificati.

### A. e-distribuzione S.p.A. (Gruppo Enel)
È il principale distributore regionale, gestendo circa **630.000 clienti** sulla quasi totalità del territorio non urbano.
*   **Capacità Connessa:** Registra **1,6 GW di potenza rinnovabile connessa**, di cui **1,25 GW provenienti da fonte fotovoltaica**. Ben la metà di questa potenza (800 MW) è stata connessa nell'ultimo triennio (2023-2025).
*   **Hosting Capacity Immediata:** Senza interventi strutturali sulle cabine primarie, la rete attuale può accogliere solo altri **500 MW** di nuova potenza.
*   **Piano di Sviluppo:** Per raddoppiare la capacità di accoglienza, e-distribuzione ha pianificato investimenti strutturali per un totale di **1,6 GW di nuova capacità**, che prevedono **23 adeguamenti/ampliamenti** di cabine primarie esistenti e la costruzione di **14 nuove cabine primarie**.

### B. AcegasApsAmga S.p.A. (Gruppo Hera)
Gestisce esclusivamente le aree urbane e industriali dei Comuni di **Trieste** e **Gorizia**, caratterizzate da carichi fortemente concentrati.
*   **Trieste:** Serve 142.000 abitanti con un'energia erogata di 615 GWh/anno e una potenza massima di picco di 130-140 MW. La sfida principale è legata alla transizione della portualità (richieste per **160 MW di connessioni passive**, di cui **80 MW destinate al cold ironing** delle banchine e 80 MW per le piattaforme logistiche e il polo ferroviario di Servola).
*   **Gorizia:** Serve 22.500 utenti con un'erogazione di 120 GWh/anno. Si registrano richieste per oltre **40 MW di nuovi impianti fotovoltaici** legati alle aree industriali/aeroportuali, una taglia che supera la potenza di picco dell'intera città e richiede infrastrutture dedicate in Alta Tensione.

### C. Le Cooperative Storiche Alpine (SECAB, Valcanale, Forni di Sopra)
Rappresentano eccellenze di auto-approvvigionamento energetico in territorio montano:
*   **SECAB (Alto Bût):** Serve 5.500 utenze (nei comuni di Paluzza, Ravascletto, Cercivento, Treppo Ligosullo, Sutrio) con una cabina primaria a 132 kV, 52 km di linee MT e 120 km in BT. Produce circa **45 GWh/anno** tramite 5 centrali idroelettriche, registrando un surplus strutturale immesso in rete di **38 MW** (58 MWh/anno immessi a fronte di 20 MW di prelievi).
*   **Idroelettrica Valcanale S.a.s.:** Gestisce 250 km di rete e 100 cabine nel Tarvisiano. Oltre alle utenze locali, gestisce la già citata *Merchant Line* transfrontaliera con l'Austria.
*   **Forni di Sopra:** Gestisce 70 km di linee MT/BT. Opera in una dinamica di rete attiva: assorbe 3 MW dalla rete nazionale in inverno e immette circa 3 MW in primavera grazie al forte apporto idroelettrico e fotovoltaico locale.

---

## 4. La Saturazione Virtuale e il Cambio di Paradigma ("Decreto Bollette")

Un collo di bottiglia strutturale evidenziato dai gestori è la **saturazione virtuale delle reti**. Molti sviluppatori speculativi "prenotano" la capacità di connessione presentando richieste cartacee che poi non si traducono in cantieri (secondo i dati regionali, **solo il 50% degli impianti autorizzati viene effettivamente costruito**).

La provincia di **Udine** è la più critica, con circa il **50% dei trasformatori AT/MT in zona rossa (saturazione virtuale)**, mentre a **Pordenone** la quota critica si attesta al **25%**.

Per scardinare questo blocco, il **Decreto Bollette (D.L. 21/2026, Articolo 7)** introduce misure rivoluzionarie che entreranno pienamente a regime a seguito dei regolamenti ARERA attesi entro fine agosto 2026:
1.  **Passaggio al modello "First Ready, First Connect":** La priorità di allacciamento non seguirà più l'ordine cronologico di presentazione della domanda (*first ask, first serve*), ma premierà i progetti concretamente autorizzati e pronti alla cantierizzazione. Le istanze speculative non autorizzate decadranno automaticamente.
2.  **Meccanismo di Overbooking:** Consente a Terna e ai distributori di rilasciare preventivi di connessione in eccedenza rispetto alla capacità reale dei nodi, basandosi sulla statistica del 50% di rinuncia dei proponenti.
3.  **Procedure di Open Season:** Assegnazione competitiva e trasparente della capacità di rete con cadenza trimestrale (prima edizione prevista a novembre 2026).

---

## 5. Script Python per la Generazione del Dashboard di Sintesi

Il codice Python sottostante è stato sviluppato per generare un dashboard a due pannelli che illustra chiaramente la situazione quantitativa descritta nel report.

*   Il pannello sinistro illustra la **Rete di Trasmissione (TSO - Terna)** e come la somma degli impianti in esercizio (940 MW) e della pipeline autorizzata RTN/DSO (660 MW) copra quasi interamente il target Burden Sharing 2030 di 1.960 MW, lasciando una quota residua di soli 360 MW.
*   Il pannello destro illustra la **Rete di Distribuzione (DSO - e-distribuzione)**, evidenziando lo stallo tra la capacità residua immediata (500 MW) e la massiccia mole di potenza connessa (1.600 MW) o programmata nei piani di raddoppio (1.600 MW).

```python
import matplotlib
matplotlib.use('Agg')  # Rendering headless obbligatorio per ambienti server
import matplotlib.pyplot as plt
import seaborn as sns
import os

# Creazione della cartella scratch per l'output intermedio
os.makedirs('/workspace/scratch', exist_ok=True)

# Impostazione del tema grafico conforme agli standard editoriali (Seaborn colorblind)
sns.set_theme(style='whitegrid', palette='colorblind', font='DejaVu Sans')
CHART_DPI = 150

# Set Dati 1: TSO Terna - Target Burden Sharing 2030 (Totale 1.960 MW)
tso_labels = [
    'In Esercizio (2021-2025)', 
    'Autorizzato RTN (Alta Tensione)', 
    'Autorizzato DSO (Media Tensione)', 
    'Quota Residua al 2030'
]
tso_values = [940, 310, 350, 360]

# Set Dati 2: DSO e-distribuzione - Capacità di Rete (MW)
dso_labels = [
    'FER Connessa (Totale)', 
    'di cui Solare', 
    'Connesso Ultimi 3 Anni', 
    'Capacità Residua Immediata', 
    'Nuovo Sviluppo Programmato'
]
dso_values = [1600, 1250, 800, 500, 1600]

# Configurazione del layout multi-chart (due pannelli affiancati)
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 7))

# Titolo principale del Dashboard (Insight-driven)
fig.suptitle('Friuli Venezia Giulia: Stato delle Reti Elettriche e Progressi FER', fontsize=18, fontweight='bold', y=0.98)

# Pannello Sinistro: TSO Progress (Terna)
tso_colors = sns.color_palette('colorblind', 4)
bars1 = sns.barplot(x=tso_values, y=tso_labels, palette=tso_colors, ax=ax1, orient='h')
ax1.set_title('Target Nazionale 2030 (Burden Sharing: 1.960 MW)\nStato Avanzamento e Pipeline "Ready-to-Build"', fontsize=13, fontweight='bold', pad=10)
ax1.set_xlabel('Potenza Nominale (MW)')
ax1.set_xlim(0, 1100)

# Inserimento delle etichette dei dati sulle barre orizzontali
for i, v in enumerate(tso_values):
    ax1.text(v + 15, i, f"{v} MW", va='center', fontweight='bold', fontsize=10)

# Pannello Destro: DSO Hosting Capacity (e-distribuzione)
dso_colors = sns.color_palette('muted', 5)
bars2 = sns.barplot(x=dso_labels, y=dso_values, palette=dso_colors, ax=ax2)
ax2.set_title('Capacità della Rete di Distribuzione (e-distribuzione)\nStato della Connessione FER e Piani di Raddoppio', fontsize=13, fontweight='bold', pad=10)
ax2.set_ylabel('Potenza (MW)')
ax2.set_xticklabels(dso_labels, rotation=15, ha='right', fontsize=9)
ax2.set_ylim(0, 1800)

# Inserimento delle etichette dei dati sulle barre verticali
for bar in ax2.patches:
    yval = bar.get_height()
    if yval > 0:
        ax2.text(bar.get_x() + bar.get_width()/2.0, yval + 25, f"{int(yval)} MW", ha='center', va='bottom', fontweight='bold', fontsize=10)

# Nota a pié di pagina con l'attribuzione delle fonti
plt.figtext(0.05, 0.01, "Fonti: Audizione IV Commissione (Terna S.p.A. - Paolo Cuccia; e-distribuzione S.p.A. - Giovanni Franzone)", fontsize=9, color='gray', style='italic')

# Rimozione degli elementi grafici superflui (spines) per un design pulito
sns.despine()
plt.tight_layout(rect=[0, 0.03, 1, 0.95])

# Salvataggio dell'immagine ad alta risoluzione
output_path = '/workspace/scratch/grid_status_fvg.png'
fig.savefig(output_path, dpi=CHART_DPI, bbox_inches='tight')
plt.close()
```


---

## 6. Aggiornamento: geometria reale della rete (OpenInfraMap, agosto 2026)

Il dashboard a barre della sezione precedente descrive *quantità* di potenza. Con
l'acquisizione del dataset OpenInfraMap (linee aeree, EPSG:6708, estrazione
27/08/2026) è ora disponibile anche la **geometria**: 4.955 tratte per 6.598 km
entro il confine regionale, riproiettate in WGS84 e ritagliate sul confine ISTAT.

### 6.1 Consistenza per livello di tensione

| Livello | Tratte | Lunghezza |
|---|---|---|
| 380 kV | 18 | 200 km |
| 220 kV | 30 | 234 km |
| 132 kV | 228 | 1.345 km |
| 60 kV | 8 | 197 km |
| MT/BT taggata (0,4-35 kV) | 65 | 110 km |
| **non classificate** | **4.606** | **4.512 km** |

Le linee prive di tag di tensione sono il 68% del totale e in larga parte
distribuzione MT: OSM le mappa geometricamente ma senza attributo `voltage`.
Vanno trattate come tracciato noto e tensione ignota, non come rete minore.

### 6.2 Assetto confermato dalla geometria

La carta conferma quanto emerso nelle audizioni. L'anello a 380 kV attraversa la
regione da **Cordignano** a **Redipuglia** passando per **Udine Ovest** (la
dorsale Udine Ovest - Cordignano è la tratta più lunga del dataset, 49 km in due
segmenti). La 220 kV **Somplago - Pordenone** e **Somplago - Salgareda** evacua
la produzione idroelettrica carnica verso ovest, mentre **Udine Nord Est - Buia**
la raccorda al nodo udinese. Verso est, **Monfalcone Termoelettrica - Padriciano**
e **Monfalcone Z.I. - Padriciano** portano a 220 kV la connessione con la
Slovenia, in doppia via.

La concentrazione su Redipuglia è visibile: vi convergono la 380 kV da Planais,
quella da Udine Ovest e i collegamenti verso il confine. È il collo di bottiglia
strutturale del sistema regionale.

### 6.3 Incrocio con la risorsa eolica

Con la geometria è possibile calcolare la distanza reale di ogni cella
dell'Atlante Eolico RSE dalla linea AT più vicina, invece di usare il campo
`Dist_cp` (distanza dalla cabina primaria) come proxy. I due valori correlano
solo a 0,59: sono grandezze diverse e non sostituibili.

| Zona | Celle ≥6 m/s | km² | v media | `Dist_cp` RSE | dist. rete ≥132 kV | dist. rete AAT |
|---|---|---|---|---|---|---|
| Carso / Trieste | 96 | 194 | 6,79 | 2,50 km | **0,91 km** | 2,06 km |
| Alpi Giulie | 40 | 81 | 6,26 | 11,12 km | 9,32 km | 28,63 km |
| Prealpi | 7 | 14 | 6,14 | 9,62 km | 9,52 km | 16,55 km |

**52 celle su 58 sopra la soglia di bancabilità (6,5 m/s) stanno entro 5 km da
una linea ad alta tensione**, e sono quasi tutte sul Carso triestino. Le celle
migliori — tra Basovizza, Monrupino e Opicina — hanno la linea a 180-300 metri.

Il vincolo alla realizzabilità dell'eolico in FVG **non è la rete**. È la
sovrapposizione di quelle stesse aree con Natura 2000, la landa carsica e il
vincolo paesaggistico. Il coefficiente di riduzione da applicare nella cascata
dei vincoli va quindi calibrato sui layer ambientali, non su quelli
infrastrutturali.

### 6.4 File prodotti

- `mappa_rete_fvg.png` — carta a due pannelli: rete per tensione, risorsa eolica con prossimità alla rete AT
- `rete_elettrica_fvg.geojson` — 4.955 tratte in WGS84 con attributi `name`, `operator`, `kV`, `livello`, `len_km`
- `rse_fvg_2026.csv` — celle RSE con i nuovi campi `dist_AT_km`, `dist_AAT_km`, `dist_linea_km`

**Avvertenza sulla fonte.** OpenInfraMap deriva da OpenStreetMap: dato
collaborativo, buona copertura su AT/AAT, incompleto sugli attributi e non
ufficiale. Va usato per analisi di prossimità e per la rappresentazione, non
come base per calcoli di capacità di trasporto o vincoli autorizzativi, per i
quali servono i dati Terna e e-distribuzione.
