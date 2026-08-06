"""
ETL per gli shapefile scaricati dal Geoportale ETA di RSE (dbeta.rse-web.it).

Ogni download di RSE arriva come una cartella con lo stesso set di file
(`download.shp/.shx/.dbf/.prj/.cpg` + `leggimi.txt`): il nome del file non dice
nulla, quindi **il nome della cartella e' il nome della variabile**. Rinominare
le cartelle in modo parlante prima di lanciare questo script e' il passaggio che
determina la qualita' del risultato.

Lo script distingue da solo due casi molto diversi:

1. **Un'unica geometria regionale.** La mappa non aggiunge nulla a un numero:
   il valore finisce in `geo_indicatori.csv` e la geometria viene scartata.
2. **Piu' geometrie** (comuni, province, celle, impianti puntuali). Qui la
   posizione conta: la geometria viene riproiettata in WGS84, semplificata e
   salvata come GeoJSON pronto per la mappa.

Uso:
    data/raw/geo/<nome-variabile>/download.shp
    python -m src.etl_geo

Licenza dei dati: CC BY-SA 4.0, RSE S.p.A. L'attribuzione va mantenuta ovunque
i dati vengano mostrati o ridistribuiti.
"""

from __future__ import annotations

import json
import re
import unicodedata
from pathlib import Path

import pandas as pd

try:
    import geopandas as gpd
except ImportError:  # l'app non ha bisogno di geopandas, solo questo ETL
    gpd = None

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "geo"
OUT = ROOT / "data" / "processed"
GEO_OUT = OUT / "geo"

CRS_WEB = 4326
# Tolleranza di semplificazione in gradi. 0.001 ~ 80 m: invisibile su una mappa
# regionale, e taglia il peso di venti volte.
TOLLERANZA = 0.001
PESO_MAX_KB = 400

# Colonne che identificano il livello territoriale, dal piu' fine al piu' grosso
LIVELLI = [
    ("PRO_COM", "comune"), ("COD_COM", "comune"), ("DEN_COM", "comune"),
    ("COD_PROV", "provincia"), ("DEN_PROV", "provincia"), ("SIGLA", "provincia"),
    ("COD_REG", "regione"), ("DEN_REG", "regione"),
]
COL_VALORE = ["VALORE", "VALUE", "VAL"]
COL_DATA = ["DATA", "DATE", "ANNO"]

# Catalogo esportato dal geoportale: nome cartella -> VAR_ID, granularita', record
# attesi. Serve a etichettare le variabili e a verificare che il download sia intero.
CATALOGO = RAW / "CATALOGO_RSE.csv"


def slug(testo: str) -> str:
    testo = "".join(c for c in unicodedata.normalize("NFKD", str(testo))
                    if not unicodedata.combining(c)).lower()
    return re.sub(r"[^a-z0-9]+", "_", testo).strip("_")


def prima_colonna(df, candidate: list[str]) -> str | None:
    return next((c for c in candidate if c in df.columns), None)


def livello_territoriale(df) -> str:
    for col, nome in LIVELLI:
        if col in df.columns and df[col].nunique() > 1:
            return nome
    return "regione"


def etichetta(df) -> pd.Series:
    """Nome leggibile di ogni feature, per i tooltip della mappa."""
    for col in ("DEN_COM", "DEN_PROV", "DEN_REG", "NOME", "DENOMINAZI"):
        if col in df.columns:
            return df[col].astype("string")
    return pd.Series([f"Area {i + 1}" for i in range(len(df))], index=df.index, dtype="string")


def carica_catalogo() -> pd.DataFrame:
    if not CATALOGO.exists():
        return pd.DataFrame()
    cat = pd.read_csv(CATALOGO)
    cat.columns = ["nome", "var_id", "granularita", "record_attesi", "totale_regionale"]
    cat["chiave"] = cat["nome"].map(slug)
    return cat


def leggi_cartella(cartella: Path) -> tuple[pd.DataFrame, object | None, dict]:
    shp = next(iter(sorted(cartella.glob("*.shp"))), None)
    if shp is None:
        return pd.DataFrame(), None, {}

    g = gpd.read_file(shp)
    variabile = slug(cartella.name)
    col_val = prima_colonna(g, COL_VALORE)
    col_data = prima_colonna(g, COL_DATA)
    livello = livello_territoriale(g)

    tab = pd.DataFrame({
        "variabile": variabile,
        "etichetta_variabile": cartella.name,
        "livello": livello,
        "area": etichetta(g),
        "valore": pd.to_numeric(g[col_val], errors="coerce") if col_val else pd.NA,
    })
    if col_data:
        anni = pd.to_datetime(g[col_data], errors="coerce").dt.year
        tab["anno"] = anni.fillna(pd.to_numeric(g[col_data], errors="coerce")).astype("Int64")
    else:
        tab["anno"] = pd.NA
    for extra in ("VAR_ID", "COD_REG", "COD_PROV", "PRO_COM"):
        if extra in g.columns:
            tab[extra.lower()] = g[extra]

    meta = {
        "variabile": variabile,
        "cartella": cartella.name,
        "livello": livello,
        "feature": len(g),
        "crs_origine": str(g.crs),
        "colonne": [c for c in g.columns if c != "geometry"],
        "geometria_salvata": False,
    }
    return tab, g, meta


def salva_geometria(g, variabile: str, meta: dict) -> None:
    """Riproietta, semplifica e salva. Solo se le geometrie sono piu' di una."""
    GEO_OUT.mkdir(parents=True, exist_ok=True)
    w = g.to_crs(CRS_WEB).copy()
    w["geometry"] = w.geometry.simplify(TOLLERANZA, preserve_topology=True)
    testo = w.to_json()

    tolleranza = TOLLERANZA
    while len(testo) / 1024 > PESO_MAX_KB and tolleranza < 0.05:
        tolleranza *= 2
        w["geometry"] = g.to_crs(CRS_WEB).geometry.simplify(tolleranza, preserve_topology=True)
        testo = w.to_json()

    path = GEO_OUT / f"{variabile}.geojson"
    path.write_text(testo)
    meta["geometria_salvata"] = True
    meta["peso_kb"] = round(len(testo) / 1024)
    meta["tolleranza"] = tolleranza


def main() -> None:
    if gpd is None:
        raise SystemExit("Serve geopandas: pip install geopandas")
    if not RAW.exists():
        raise SystemExit(f"Manca {RAW}. Crea una sottocartella per ogni variabile scaricata.")

    cartelle = sorted(p for p in RAW.iterdir() if p.is_dir())
    if not cartelle:
        raise SystemExit(f"Nessuna sottocartella in {RAW}")

    cat = carica_catalogo()
    if not cat.empty:
        print(f"Catalogo: {len(cat)} indicatori attesi\n")

    tabelle, manifest = [], []
    for cartella in cartelle:
        tab, g, meta = leggi_cartella(cartella)
        if tab.empty:
            print(f"  - {cartella.name}: nessuno .shp, saltata")
            continue
        if meta["feature"] > 1:
            salva_geometria(g, meta["variabile"], meta)
            nota = f"mappa {meta['peso_kb']} KB"
        else:
            nota = "solo valore (geometria ridondante)"
        # confronto con il catalogo: se i record non tornano, il download e' parziale
        if not cat.empty:
            riga = cat[cat["chiave"] == meta["variabile"]]
            if not riga.empty:
                meta["var_id"] = riga.iloc[0]["var_id"]
                attesi = riga.iloc[0]["record_attesi"]
                if pd.notna(attesi) and int(attesi) != meta["feature"]:
                    nota += f"  ATTENZIONE: attesi {int(attesi)} record"
            else:
                nota += "  (non nel catalogo)"

        tabelle.append(tab)
        manifest.append(meta)
        print(f"  + {cartella.name:38} {meta['feature']:5d} aree | {meta['livello']:9} | {nota}")

    OUT.mkdir(parents=True, exist_ok=True)
    df = pd.concat(tabelle, ignore_index=True)
    df.to_csv(OUT / "geo_indicatori.csv", index=False)
    (OUT / "geo_manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print(f"\nScritto geo_indicatori.csv ({len(df)} righe, {df['variabile'].nunique()} variabili)")
    con_mappa = [m for m in manifest if m["geometria_salvata"]]
    print(f"GeoJSON salvati: {len(con_mappa)} su {len(manifest)}")
    if len(manifest) - len(con_mappa):
        print("Le altre sono regionali: il valore basta, la geometria e' stata scartata.")


if __name__ == "__main__":
    main()
