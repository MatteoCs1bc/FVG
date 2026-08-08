"""
ETL per il catasto regionale delle derivazioni idriche (IDR_GIS).

Due strati puntuali: le **opere** (2.531, di cui 447 centrali idroelettriche) e
le **sorgenti captate** (663). E' la fonte piu' completa sull'idroelettrico
regionale: il portale EAGLE ne aggregava 206 per comune, qui ci sono le singole
centrali con salto, portata e potenza di concessione.

Attenzione a due cose:

* la **potenza di concessione** non e' la potenza efficiente. E' la potenza
  nominale media di concessione, legata alla portata media derivabile: la somma
  regionale (255 MW) e' molto sotto i 528,9 MW di potenza efficiente misurati da
  Terna, e le due grandezze non vanno confrontate;
* lo stato dell'opera distingue esistente, in progetto, in realizzazione e
  rinunciata: solo la prima categoria e' parco in esercizio.

Uso: python -m src.etl_catasto
"""

from __future__ import annotations

import tempfile
import zipfile
from pathlib import Path

import pandas as pd

try:
    import geopandas as gpd
except ImportError:
    gpd = None

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "catasto"
OUT = ROOT / "data" / "processed"


def apri(prefisso: str):
    for archivio in sorted(RAW.glob(f"{prefisso}*.zip")):
        tmp = Path(tempfile.mkdtemp())
        with zipfile.ZipFile(archivio) as z:
            z.extractall(tmp)
        trovati = sorted(tmp.rglob("*.shp"))
        if trovati:
            return gpd.read_file(trovati[0])
    diretti = sorted(RAW.rglob(f"{prefisso}*.shp"))
    return gpd.read_file(diretti[0]) if diretti else None


def main() -> None:
    if gpd is None:
        raise SystemExit("Serve geopandas")
    OUT.mkdir(parents=True, exist_ok=True)

    g = apri("IDR_GIS_IMPIANTI")
    if g is None:
        raise SystemExit(f"Nessuno shapefile in {RAW}")

    idro = g[g["USO"].astype(str).str.contains("droelettric", na=False)].copy()
    idro = idro[idro["TIPO_OPERA"] == "Centrale idroelettrica"]
    w = idro.to_crs(4326)

    df = pd.DataFrame({
        "nome": idro["NOME"].astype("string").fillna("(senza denominazione)"),
        "stato": idro["STATO_OPER"].astype("string"),
        "potenza_kw": pd.to_numeric(idro["POTENZA_CO"], errors="coerce"),
        "salto_m": pd.to_numeric(idro["SALTO_IMPI"], errors="coerce"),
        "salto_concessione_m": pd.to_numeric(idro["SALTO_CONC"], errors="coerce"),
        "portata_media": pd.to_numeric(idro["PORTATA_ME"], errors="coerce"),
        "portata_massima": pd.to_numeric(idro["PORTATA_MA"], errors="coerce"),
        "scadenza": idro["DATA_SCADE"].astype("string"),
        "lon": w.geometry.x, "lat": w.geometry.y,
    })
    df["potenza_mw"] = df["potenza_kw"] / 1000
    df = df.dropna(subset=["lon", "lat"])
    df.to_csv(OUT / "centrali_idro_catasto.csv", index=False)

    esistenti = df[df["stato"] == "Esistente"]
    print(f"  + centrali_idro_catasto   {len(df)} centrali "
          f"({len(esistenti)} esistenti, {df['potenza_mw'].sum():.1f} MW di concessione)")
    print(df.groupby("stato").agg(n=("nome", "count"), mw=("potenza_mw", "sum")).round(1).to_string())

    s = apri("IDR_GIS_SORGENTI")
    if s is not None:
        si = s[s["USO"].astype(str).str.contains("droelettric", na=False)].copy()
        if not si.empty:
            ws = si.to_crs(4326)
            pd.DataFrame({
                "nome": si["NOME"].astype("string").fillna("(senza denominazione)"),
                "comune": si["COMUNE"].astype("string"),
                "stato": si["STATO_OPER"].astype("string"),
                "portata_media": pd.to_numeric(si["PORTATA_ME"], errors="coerce"),
                "lon": ws.geometry.x, "lat": ws.geometry.y,
            }).to_csv(OUT / "sorgenti_idro_catasto.csv", index=False)
            print(f"  + sorgenti_idro_catasto   {len(si)} captazioni a uso idroelettrico")

    # i due CSV compilati a mano su grandi impianti e bioenergie
    for nome, sorgente in [("idro_montagna", "impianti_idro_fvg_montagna.csv"),
                           ("bio_impianti_dieta", "impianti_bio_fvg.csv"),
                           ("biometano_pipeline", "biometano_comuni_pipeline_fvg.csv")]:
        path = ROOT / "data" / "raw" / "bio" / sorgente
        if path.exists():
            d = pd.read_csv(path)
            d.to_csv(OUT / f"{nome}.csv", index=False)
            print(f"  + {nome:24} {len(d)} righe")


if __name__ == "__main__":
    main()
