"""
ETL per i progetti FER autorizzati o in istruttoria in FVG (dati regionali).

Due dataset con lo stesso schema: impianti fotovoltaici e agrivoltaici, e
impianti a biomasse e biometano. Sono i progetti passati per il procedimento
autorizzativo regionale, con potenza e superficie occupata.

Attenzione alle unita': `potenza_el` e' in **kW** e `superficie` in **m2**.
Qui vengono convertite in MW ed ettari, che sono le scale in cui si ragiona.

Uso: python -m src.etl_progetti
"""

from __future__ import annotations

import json
import tempfile
import zipfile
from pathlib import Path

import pandas as pd

try:
    import geopandas as gpd
except ImportError:
    gpd = None

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "geo_progetti"
OUT = ROOT / "data" / "processed"
GEO_OUT = OUT / "geo"
TOLLERANZA = 0.0005   # progetti piccoli: serve piu' dettaglio delle aree comunali
DECIMALI = 5

# Lo stato arriva con grafie diverse ("autorizzato"/"autorizzata"/"conclusa"):
# raggrupparlo e' l'unico modo per farci sopra un conteggio sensato.
STATI = {
    "autorizzato": "Autorizzato", "autorizzata": "Autorizzato", "conclusa": "Autorizzato",
    "in corso": "In istruttoria", "in iter": "In istruttoria", "da avviare": "In istruttoria",
    "costruito": "Realizzato", "in esercizio": "Realizzato", "in costruzione": "In costruzione",
    "sospeso": "Sospeso o archiviato", "sospesa": "Sospeso o archiviato",
    "archiviato": "Sospeso o archiviato", "diniego": "Sospeso o archiviato",
}


def _arrotonda(o):
    if isinstance(o, list):
        return [_arrotonda(x) for x in o]
    return round(o, DECIMALI) if isinstance(o, float) else o


def apri(nome: str):
    diretti = sorted(RAW.glob(f"{nome}*.shp"))
    if diretti:
        return gpd.read_file(diretti[0])
    for archivio in RAW.glob(f"{nome}*.zip"):
        tmp = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(archivio) as z:
            z.extractall(tmp)
        trovati = sorted(tmp.rglob("*.shp"))
        if trovati:
            return gpd.read_file(trovati[0])
    return None


def normalizza(g, categoria: str) -> pd.DataFrame:
    w = g.to_crs(4326).copy()
    centro = w.geometry.representative_point()
    return pd.DataFrame({
        "categoria": categoria,
        "tipo": w["tipo"].astype("string"),
        "nome": w["nome_proge"].astype("string").str.strip(),
        "potenza_mw": pd.to_numeric(w["potenza_el"], errors="coerce") / 1000,
        "superficie_ha": pd.to_numeric(w["superficie"], errors="coerce") / 10_000,
        "stato_grezzo": w["stato"].astype("string"),
        "stato": w["stato"].astype("string").str.lower().map(STATI).fillna("Altro"),
        "lon": centro.x, "lat": centro.y,
    })


def salva_geo(g, nome: str, etichette: pd.DataFrame) -> None:
    GEO_OUT.mkdir(parents=True, exist_ok=True)
    w = g.to_crs(4326).copy()
    w = w[["geometry"]].assign(
        nome=etichette["nome"].values, tipo=etichette["tipo"].values,
        stato=etichette["stato"].values, potenza_mw=etichette["potenza_mw"].round(2).values,
        superficie_ha=etichette["superficie_ha"].round(1).values)
    w["geometry"] = w.geometry.simplify(TOLLERANZA, preserve_topology=True)
    dati = json.loads(w.to_json())
    for i, f in enumerate(dati["features"]):
        f["geometry"]["coordinates"] = _arrotonda(f["geometry"]["coordinates"])
        f["id"] = i
    testo = json.dumps(dati, separators=(",", ":"))
    (GEO_OUT / f"{nome}.geojson").write_text(testo)
    print(f"    mappa {len(testo) / 1024:.0f} KB")


def main() -> None:
    if gpd is None:
        raise SystemExit("Serve geopandas")
    OUT.mkdir(parents=True, exist_ok=True)
    pezzi = []

    for nome_file, categoria, slug in [
        ("imp_ftv_agriftv", "Solare", "progetti_solare"),
        ("prog_impaue_v_biomasse_biometano", "Bioenergie", "progetti_bioenergie"),
    ]:
        g = apri(nome_file)
        if g is None:
            print(f"  - {nome_file}: non trovato")
            continue
        df = normalizza(g, categoria)
        salva_geo(g, slug, df)
        df.to_csv(OUT / f"{slug}.csv", index=False)
        pezzi.append(df)
        print(f"  + {slug:22} {len(df):4d} progetti | "
              f"{df['potenza_mw'].sum():8,.1f} MW | {df['superficie_ha'].sum():7,.0f} ha")

    if pezzi:
        tutti = pd.concat(pezzi, ignore_index=True)
        tutti.to_csv(OUT / "progetti_fer.csv", index=False)
        print("\nPer stato:")
        print(tutti.groupby(["categoria", "stato"])
              .agg(n=("nome", "count"), mw=("potenza_mw", "sum"), ha=("superficie_ha", "sum"))
              .round(0).to_string())


if __name__ == "__main__":
    main()
