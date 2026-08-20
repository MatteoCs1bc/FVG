"""
Inversioni di flusso alle sezioni AT/MT, dall'elenco nazionale e-distribuzione.

Il documento elenca le sezioni in cui, nell'anno, il flusso di energia si e'
invertito - la distribuzione ha immesso verso l'alta tensione invece di
prelevare - per almeno l'1% o il 5% delle ore. E' l'indicatore piu' diretto di
generazione distribuita che supera il consumo locale.

Due usi oltre al conteggio:

* **confronto fra regioni**, che colloca il FVG nel quadro nazionale;
* **geolocalizzazione approssimata delle cabine primarie**. I nomi delle cabine
  sono toponimi: incrociandoli con i comuni si ottiene una posizione. Non e' la
  posizione dell'impianto, e' il centro del comune che gli da' il nome - serve
  a capire *dove* accade il fenomeno, non a progettare.

Uso: python -m src.etl_inversioni
"""

from __future__ import annotations

import json
import re
import subprocess
import unicodedata
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "reti"
GEO = ROOT / "data" / "processed" / "geo"
OUT = ROOT / "data" / "processed"
ANNO = 2025
REGIONE = "Friuli Venezia Giulia"

RIGA = re.compile(
    r"^\s*([A-Z][A-Za-zàèéìòù'. ]+?)\s{2,}([A-Z]{2})\s+(.+?)\s{2,}(\d+)\s+(x?)\s*(x?)\s*$")
PROVINCE = {"UD": "Udine", "PN": "Pordenone", "GO": "Gorizia", "TS": "Trieste"}

# Cabine il cui nome non coincide con un comune: abbreviazioni, frazioni,
# zone industriali. Risolte sul comune che le ospita.
ALIAS_COMUNE = {
    "S.DANIELE": "San Daniele del Friuli",
    "S.GIOVANNI": "San Giovanni al Natisone",
    "S.QUIRINO": "San Quirino",
    "SESTO REGHENA": "Sesto al Reghena",
    "UDINE NORD EST": "Udine",
    "UDINE SUD": "Udine",
    "ZAULE": "Trieste",
    "SCHIAVETTI": "Monfalcone",
    "REDIPUGLIA": "Fogliano Redipuglia",
    "GIAIS": "Aviano",
    "PONTEROSSO": "San Vito al Tagliamento",
    "STRADALTA": "Basiliano",
    "CA' POIA": "Rigolato",
    "PLANAIS": "Villa Santina",
    "BUIA": "Buja",
}


def leggi_testo(path: Path) -> str:
    dati = path.read_bytes()
    if dati[:4] == b"%PDF":
        tmp = path.with_suffix(".txt")
        subprocess.run(["pdftotext", "-layout", str(path), str(tmp)], check=True)
        return tmp.read_text(encoding="utf-8", errors="replace")
    return dati.decode("utf-8", errors="replace")


def norm(s: str) -> str:
    s = "".join(c for c in unicodedata.normalize("NFKD", s) if not unicodedata.combining(c))
    return re.sub(r"[^A-Z]", "", s.upper())


def centroidi() -> dict:
    path = GEO / "comuni_fvg.geojson"
    if not path.exists():
        return {}
    fuori = {}
    for f in json.loads(path.read_text())["features"]:
        punti: list = []

        def racc(c):
            if isinstance(c, list) and c and isinstance(c[0], (int, float)):
                punti.append(c)
            elif isinstance(c, list):
                for x in c:
                    racc(x)

        racc(f["geometry"]["coordinates"])
        nome = f["properties"]["comune"]
        if punti:
            fuori[norm(nome)] = (nome, sum(p[0] for p in punti) / len(punti),
                                 sum(p[1] for p in punti) / len(punti))
    return fuori


def main() -> None:
    sorgenti = sorted(RAW.glob("Inversioni*.pdf"))
    if not sorgenti:
        raise SystemExit(f"Nessun elenco inversioni in {RAW}")
    testo = leggi_testo(sorgenti[-1])

    righe = []
    for l in testo.splitlines():
        m = RIGA.match(l)
        if not m:
            continue
        regione, sigla, cabina, sezione, oltre1, oltre5 = m.groups()
        righe.append({"regione": regione.strip(), "sigla": sigla,
                      "cabina": cabina.strip(), "sezione": int(sezione),
                      "oltre_1_pct": bool(oltre1), "oltre_5_pct": bool(oltre5),
                      "anno": ANNO})
    if not righe:
        raise SystemExit("Nessuna riga riconosciuta")

    naz = pd.DataFrame(righe)
    per_regione = (naz.groupby("regione")
                   .agg(sezioni=("sezione", "count"), cabine=("cabina", "nunique"),
                        oltre_5=("oltre_5_pct", "sum")).reset_index()
                   .sort_values("sezioni", ascending=False))
    per_regione["quota_oltre_5"] = (per_regione["oltre_5"] / per_regione["sezioni"] * 100).round(1)
    per_regione.to_csv(OUT / "inversioni_regioni.csv", index=False)

    fvg = naz[naz["regione"] == REGIONE].copy()
    fvg["provincia"] = fvg["sigla"].map(PROVINCE).fillna(fvg["sigla"])

    cen = centroidi()

    def posizione(cabina: str):
        chiave = norm(ALIAS_COMUNE.get(cabina, cabina))
        if chiave in cen:
            return cen[chiave]
        candidati = [v for k, v in cen.items() if k.startswith(chiave[:6]) and len(chiave) >= 5]
        return candidati[0] if len(candidati) == 1 else (None, None, None)

    pos = list(fvg["cabina"].map(posizione))
    fvg["comune_riferimento"] = [p[0] for p in pos]
    fvg["lon"] = [p[1] for p in pos]
    fvg["lat"] = [p[2] for p in pos]
    fvg["cabina"] = fvg["cabina"].str.title()
    fvg.to_csv(OUT / "inversioni_flusso.csv", index=False)

    per_cabina = (fvg.dropna(subset=["lon"])
                  .groupby(["cabina", "provincia", "comune_riferimento", "lon", "lat"],
                           as_index=False)
                  .agg(sezioni=("sezione", "count"), oltre_5=("oltre_5_pct", "sum")))
    per_cabina.to_csv(OUT / "inversioni_cabine.csv", index=False)

    senza = int(fvg["lon"].isna().sum())
    print(f"  + inversioni_regioni    {len(per_regione)} regioni, {len(naz)} sezioni in Italia")
    print(f"  + inversioni_flusso     {len(fvg)} sezioni FVG su {fvg['cabina'].nunique()} cabine")
    print(f"  + inversioni_cabine     {len(per_cabina)} cabine localizzate"
          + (f" ({senza} sezioni senza posizione)" if senza else ""))
    ordinate = per_regione.reset_index(drop=True)
    riga = ordinate[ordinate["regione"] == REGIONE]
    if not riga.empty:
        p = int(riga.index[0]) + 1
        print(f"\nFVG: {p}° in Italia per sezioni invertite "
              f"({int(riga['sezioni'].iat[0])} su {len(naz)}), "
              f"{riga['quota_oltre_5'].iat[0]:.0f}% oltre il 5% del tempo")


if __name__ == "__main__":
    main()
