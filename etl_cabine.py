"""
ETL per le aree convenzionali delle cabine primarie (dataset AREECONVENZIONALI_CP).

Sono i poligoni che delimitano il territorio sotteso a ciascuna cabina primaria
di distribuzione: la base geografica su cui si definisce l'appartenenza a una
comunita' energetica rinnovabile. Attenzione: **non sono le linee di rete ne' le
cabine come punti**, sono le aree di influenza.

Il file arriva come zip dal portale regionale. Puo' essere lasciato zippato in
data/raw/geo_cp/ oppure gia' scompattato: lo script gestisce entrambi i casi.

Produce:
    data/processed/geo/aree_cabine_primarie.geojson   geometrie per la mappa
    data/processed/aree_cabine_primarie.csv           tabella degli attributi

Uso: python -m src.etl_cabine
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
RAW = ROOT / "data" / "raw" / "geo_cp"
OUT = ROOT / "data" / "processed"
GEO_OUT = OUT / "geo"

# ~150 m: sotto la soglia percepibile a scala regionale, e taglia il peso di sei volte
TOLLERANZA = 0.002
DECIMALI = 4  # ~11 m; arrotondare aiuta molto la compressione


def _arrotonda(o):
    if isinstance(o, list):
        return [_arrotonda(x) for x in o]
    if isinstance(o, float):
        return round(o, DECIMALI)
    return o


def trova_shapefile(cartella: Path) -> Path | None:
    diretti = sorted(cartella.rglob("*.shp"))
    if diretti:
        return diretti[0]
    for archivio in sorted(cartella.glob("*.zip")):
        tmp = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(archivio) as z:
            z.extractall(tmp)
        estratti = sorted(tmp.rglob("*.shp"))
        if estratti:
            return estratti[0]
    return None


def main() -> None:
    if gpd is None:
        raise SystemExit("Serve geopandas: pip install geopandas")
    shp = trova_shapefile(RAW) if RAW.exists() else None
    if shp is None:
        raise SystemExit(f"Nessuno shapefile (o zip che lo contenga) in {RAW}")

    g = gpd.read_file(shp)
    print(f"Letto {shp.name}: {len(g)} aree, CRS {g.crs}")

    # area in km2 calcolata in proiezione metrica, prima di passare a WGS84
    superfici = g.to_crs(32632).area / 1e6
    w = g.to_crs(4326).copy()
    w["area_km2"] = superfici.round(1)
    w["gestore"] = w["GESTORE"].astype("string").str.strip()
    w["codice"] = w["AC_CODICE"].astype("string").str.strip()
    w["fuori_regione"] = w["EXTRAFVG"].fillna(0).astype(int).astype(bool)
    w = w[["codice", "gestore", "area_km2", "fuori_regione", "geometry"]]

    # tabella
    OUT.mkdir(parents=True, exist_ok=True)
    w.drop(columns="geometry").to_csv(OUT / "aree_cabine_primarie.csv", index=False)

    # geometrie semplificate
    s = w.copy()
    s["geometry"] = w.geometry.simplify(TOLLERANZA, preserve_topology=True)
    dati = json.loads(s.to_json())
    for f in dati["features"]:
        f["geometry"]["coordinates"] = _arrotonda(f["geometry"]["coordinates"])
        f["id"] = f["properties"]["codice"]
    GEO_OUT.mkdir(parents=True, exist_ok=True)
    testo = json.dumps(dati, separators=(",", ":"))
    (GEO_OUT / "aree_cabine_primarie.geojson").write_text(testo)

    print(f"  + aree_cabine_primarie.csv       {len(w)} righe")
    print(f"  + aree_cabine_primarie.geojson   {len(testo) / 1024:.0f} KB")
    print()
    print(w.groupby("gestore")["area_km2"].agg(["count", "sum"]).round(0).to_string())
    print(f"\nSuperficie coperta: {w['area_km2'].sum():,.0f} km²".replace(",", "."))


if __name__ == "__main__":
    main()
