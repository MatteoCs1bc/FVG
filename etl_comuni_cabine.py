"""
Corrispondenza fra comuni e aree di influenza delle cabine primarie.

Serve a rispondere a una domanda pratica: **sotto quale cabina primaria ricade
questo comune, e quanta pressione c'e' gia' su quella porzione di rete**.

Attenzione a un fatto che cambia il modo di leggere il risultato: le aree delle
cabine **non seguono i confini comunali**. Solo 35 comuni su 215 ricadono
interamente sotto una sola cabina; gli altri 180 sono divisi fra due e sei aree
diverse. Per un comune diviso, la comunita' energetica non puo' coprire tutto il
territorio: due frazioni dello stesso comune possono stare su cabine diverse e
non poter condividere energia fra loro.

Per ogni coppia comune-area si calcola la superficie di sovrapposizione, cosi'
si distingue l'area principale dalle porzioni marginali.

Uso: python -m src.etl_comuni_cabine
"""

from __future__ import annotations

from pathlib import Path

import pandas as pd

try:
    import geopandas as gpd
except ImportError:
    gpd = None

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "data" / "processed" / "geo"
OUT = ROOT / "data" / "processed"

# Sotto questa quota la sovrapposizione e' probabilmente un effetto di bordo
# fra geometrie semplificate, non una porzione reale di territorio.
SOGLIA_MARGINALE = 0.02


def main() -> None:
    if gpd is None:
        raise SystemExit("Serve geopandas")

    comuni = gpd.read_file(GEO / "comuni_fvg.geojson")[["comune", "geometry"]]
    aree = gpd.read_file(GEO / "aree_cabine_primarie.geojson")[
        ["codice", "gestore", "geometry"]]

    inter = gpd.overlay(comuni, aree, how="intersection", keep_geom_type=True)
    inter["km2"] = inter.to_crs(32633).area / 1e6
    superficie_comune = (comuni.to_crs(32633).area / 1e6).rename("km2_comune")
    comuni_km2 = pd.concat([comuni["comune"], superficie_comune], axis=1)
    inter = inter.merge(comuni_km2, on="comune", how="left")
    inter["quota_comune"] = (inter["km2"] / inter["km2_comune"]).round(3)
    inter = inter[inter["quota_comune"] >= SOGLIA_MARGINALE].copy()

    # pressione autorizzativa gia' calcolata per area
    sat = OUT / "saturazione_aree.csv"
    if sat.exists():
        s = pd.read_csv(sat)
        colonne = [c for c in ["codice", "progetti", "mw_richiesti", "mw_per_km2",
                               "area_km2", "Solare", "Accumuli", "Bioenergie",
                               "Idroelettrico"] if c in s.columns]
        inter = inter.merge(s[colonne], on="codice", how="left")

    # inversioni di flusso: non sono agganciabili all'area, ma alla provincia
    inv = OUT / "inversioni_flusso.csv"
    if inv.exists():
        i = pd.read_csv(inv)
        per_prov = i.groupby("provincia").agg(
            sezioni_invertite=("sezione", "count"),
            cabine_invertite=("cabina", "nunique")).reset_index()
        per_prov.to_csv(OUT / "inversioni_per_provincia.csv", index=False)

    fuori = inter.drop(columns="geometry").sort_values(
        ["comune", "quota_comune"], ascending=[True, False])
    fuori.to_csv(OUT / "comuni_cabine.csv", index=False)

    per_comune = fuori.groupby("comune").agg(
        aree=("codice", "nunique"),
        area_principale=("codice", "first"),
        quota_principale=("quota_comune", "first"),
        gestori=("gestore", lambda x: ", ".join(sorted(set(x)))),
        mw_richiesti=("mw_richiesti", "sum") if "mw_richiesti" in fuori.columns
        else ("codice", "size"),
    ).reset_index()
    per_comune.to_csv(OUT / "comuni_cabine_sintesi.csv", index=False)

    print(f"  + comuni_cabine           {len(fuori)} coppie comune-area")
    print(f"  + comuni_cabine_sintesi   {len(per_comune)} comuni")
    print()
    distribuzione = per_comune["aree"].value_counts().sort_index()
    for n, quanti in distribuzione.items():
        print(f"    {quanti:3d} comuni ricadono su {n} area")
    print(f"\n    comuni su una sola cabina: "
          f"{(per_comune['aree'] == 1).sum()} su {len(per_comune)} "
          f"({(per_comune['aree'] == 1).sum() / len(per_comune) * 100:.0f}%)")


if __name__ == "__main__":
    main()
