# FVG Energy Explorer

Esploratore del sistema energetico del **Friuli-Venezia Giulia**, in stile
[IEA Country Profile](https://www.iea.org/countries/italy): serie storiche 2000–2024,
mix di generazione, capacità installata, emissioni, Sankey dei flussi e diagramma ternario.

Fonte dei dati: **Terna – Dati Statistici** ([dati.terna.it](https://dati.terna.it)).

---

## Avvio rapido

```bash
git clone https://github.com/<tuo-utente>/fvg-energy.git
cd fvg-energy

python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python -m src.etl_terna        # export Terna  -> tabella lunga
python -m src.etl_per          # PER FVG 2024   -> tabelle tematiche
streamlit run app.py
```

L'app si apre su <http://localhost:8501>.

---

## Struttura

```
fvg-energy/
├── app.py                     # interfaccia Streamlit (12 schede)
├── fvg_energy_app.py          # stessa app in un file solo, dati inclusi
├── requirements.txt
├── .streamlit/config.toml     # tema
├── src/
│   ├── etl_terna.py           # da XLSX Terna a tabella lunga
│   ├── etl_per.py             # dal foglio PER a tabelle tematiche
│   ├── build_single.py        # genera la versione a file singolo
│   ├── config.py              # palette, etichette, popolazione
│   ├── dati_documentali.py    # cifre da PDF e audizioni, con le fonti
│   └── data.py                # accesso ai dati processati
└── data/
    ├── raw/terna/*.xlsx       # export scaricati da dati.terna.it
    ├── raw/per/*.xlsx         # PER FVG 2024
    └── processed/             # terna_long.* + i CSV del PER
```

Le due sorgenti restano separate perché sono di natura diversa. Terna è una serie
storica annuale del solo settore elettrico, regolare e ri-scaricabile. Il PER è
una fotografia del sistema energetico completo (bilancio 2021, scenari al 2045):
un foglio compilato a mano, con celle sparse e numeri scritti come testo. Il primo
si legge da solo, il secondo ha le posizioni scritte in cima a `etl_per.py`.

### Il formato dati

Tutta l'app legge **una sola tabella lunga**. Aggiungere un grafico non richiede
mai di toccare l'ETL:

| colonna | esempio |
|---|---|
| `dataset` | `produzione_per_fonte_gwh` |
| `misura` | `Produzione` |
| `anno` | `2024` |
| `dimensione` / `voce` | `Fonte` / `Idrico` |
| `dimensione2` / `voce2` | `Sottocategoria` / `Ciclo combinato` |
| `valore` | `2163.13` |
| `unita` | `GWh` |
| `regione`, `tipo_capacita`, `tipo_produzione` | letti dai filtri dell'export |

---

## Aggiornare i dati

Gli export di Terna hanno tutti la stessa anatomia (riga 1 = filtri applicati,
riga 3 = intestazioni). L'ETL li riconosce da solo: identifica colonna anno,
colonna valore e dimensioni, legge l'unità dal nome del file e i metadati
(regione, tipo capacità, tipo produzione) dalla riga dei filtri.

Quindi, per aggiornare:

1. Vai su [dati.terna.it](https://dati.terna.it), scegli il dataset, filtra per
   `Regione = Friuli-Venezia Giulia` ed esporta in XLSX.
2. Metti il file in `data/raw/terna/` (sostituisci il vecchio o affiancalo).
3. Lancia `python -m src.etl_terna`.

Non serve modificare il codice: nomi di colonna nuovi o filtri diversi vengono
gestiti automaticamente. Scaricando anche altre regioni, la colonna `regione` le
distingue già — servirà solo aggiungere un selettore nella sidebar.

---

## Deploy su Streamlit Community Cloud

1. Fai push del repo su GitHub **includendo `src/` e `data/processed/`**, così
   l'app parte anche senza rilanciare l'ETL.
2. Vai su [share.streamlit.io](https://share.streamlit.io) → **New app**.
3. Seleziona il repo, branch `main`, file `app.py`. Deploy.

### Se non vuoi gestire le cartelle: versione a file singolo

`fvg_energy_app.py` è la stessa app in un unico file, con i dati incorporati
(compressi, ~54 KB in tutto). Non importa nulla di locale e non legge nulla da
disco. Metti nel repository solo quel file e `requirements.txt`, punta Streamlit
Cloud su `fvg_energy_app.py` e funziona.

È generato, non si modifica a mano: le modifiche vanno in `app.py` e `src/`, poi

```bash
python -m src.build_single
```

Conviene usare questa versione per pubblicare e la versione modulare per lavorare.

### `ModuleNotFoundError: src`

Quasi sempre significa che su GitHub c'è solo lo script e non la cartella `src/`.
Verifica sul repo che esistano, allo stesso livello del file dell'app:

```
src/__init__.py     <- deve esserci, anche vuoto
src/config.py
src/data.py
src/etl_terna.py
src/etl_per.py
data/processed/
```

Se `src/` c'è ma l'errore resta, il problema è la working directory: le prime
righe dell'app la aggiungono già a `sys.path`, quindi assicurati di aver
pushato anche quella versione. Attenzione a caricare i file trascinandoli nella
UI di GitHub: le cartelle vuote e i file che iniziano per punto vengono ignorati.

---

## Cosa c'è e cosa manca

**Coperto oggi** — il perimetro dei dati Terna, cioè il solo settore elettrico:
produzione lorda per fonte e combustibile, potenza efficiente (lorda e netta),
idroelettrico per tipo di impianto, cogenerazione e calore utile, CO₂ della
generazione termoelettrica.

Dal PER arrivano il **bilancio energetico regionale 2021** (3.957 ktep di consumo
interno lordo, il 91% importato), la **matrice consumi finali vettore × settore**,
gli **scenari REF / PNIEC / RePowerEU al 2045** per civile, industria e trasporti,
la traiettoria delle rinnovabili elettriche e il parco impianti al 31/12/2023.

Dalle audizioni della IV Commissione (21/04/2026) e dai report ARPA arrivano i
dati su **rete di distribuzione e saturazione**, **burden sharing regionale** e
**clima**. Queste cifre non sono serie ri-scaricabili ma valori letti da PDF:
stanno in `src/dati_documentali.py`, ognuna accanto alla propria fonte, e l'app
mostra la fonte insieme al numero.

**Non ancora coperto**, e quindi il lavoro successivo:

- **richiesta elettrica regionale** e saldo import/export orario (Terna, dataset separato);
- **serie storica del bilancio energetico**: oggi c'è il solo 2021, quindi i consumi
  finali sono una fotografia e non una tendenza;
- **inventario emissivo completo**: ISPRA stima ~11,3 Mt CO₂eq per il FVG al 2019,
  contro gli ~1,2 Mt della sola generazione elettrica;
- **approfondimento idroelettrico** (concentrazione per bacino, deflusso ecologico,
  potenziale residuo);
- **accumuli e BESS regionali**: i numeri circolano nelle audizioni ma servono i
  documenti primari prima di metterli in pagina;
- **idrogeno e industria hard-to-abate**: la North Adriatic Hydrogen Valley è nel
  PER, ma senza dati quantitativi utilizzabili;
- confronto **FVG vs Italia** e vs altre regioni.

Il diagramma ternario descrive ancora il mix di generazione, non la domanda finale:
per farlo sulla domanda serve la serie storica del bilancio, non il solo 2021.

---

## Note metodologiche

- **Produzione lorda**: ai morsetti dei generatori, prima dei servizi ausiliari.
- **Potenza efficiente lorda vs netta**: la netta esclude gli assorbimenti dei
  servizi ausiliari. Selezionabile dalla sidebar.
- L'`Idrico` nella scheda Elettricità include i pompaggi; nella scheda
  Rinnovabili no — da qui la piccola differenza tra le due serie.
- Nel Sankey, l'**input di combustibile non è un dato misurato**: Terna pubblica
  la produzione, non l'energia entrante. Viene stimato dal rendimento complessivo
  impostato con lo slider (default 0,52). Cambiando quel valore cambiano input e
  perdite, non la produzione.
- Le **ore equivalenti** sono produzione annua / potenza efficiente di fine anno:
  sovrastimano leggermente gli anni di forte crescita del parco (il fotovoltaico
  installato a dicembre non ha prodotto per dodici mesi).
- Il **bilancio 2021** chiude con uno scarto di +3 ktep su 3.957: sono i bunkeraggi
  dell'aviazione internazionale, contabilizzati fuori dagli impieghi.
- I dati Terna e quelli del PER **non sono perfettamente allineati**: il PER usa la
  potenza al 31/12/2023 comprensiva di autoproduttori (1.848,8 MW termoelettrici
  lordi), Terna espone la serie regionale. Le differenze sono di perimetro, non
  errori.
- Nel foglio `Power&2050` ci sono due serie etichettate `CIL FVG [ktep]` e
  `Emissioni CO2 stimate [ktCO2]` con valori (151 e 333 al 2021) incompatibili con
  il bilancio regionale: perimetro o unità non sono chiari, quindi **non sono usate
  nell'app**.
