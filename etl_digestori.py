"""
ETL per il dossier sui digestori anaerobici del FVG.

Il file JSON e' una ricognizione da fonti eterogenee, non un registro: copre 29
impianti su 71-92 stimati, e ogni voce porta il proprio livello di affidabilita'.
Qui viene appiattito in tabelle, mantenendo le colonne che dichiarano quanto e'
solido ciascun dato.

Il numero che conta: gli impianti a **colture dedicate** sono 14 su 29 per
numero, ma valgono il 79,4% della potenza censita, e sono quasi tutti da
999-1000 kWe - la taglia disegnata attorno al vecchio incentivo.

Uso: python -m src.etl_digestori
"""

from __future__ import annotations

import json
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
SORGENTE = ROOT / "data" / "raw" / "bio" / "digestori_fvg.json"
OUT = ROOT / "data" / "processed"


def main() -> None:
    if not SORGENTE.exists():
        raise SystemExit(f"Manca {SORGENTE}")
    d = json.loads(SORGENTE.read_text(encoding="utf-8"))
    OUT.mkdir(parents=True, exist_ok=True)

    # impianti
    imp = pd.json_normalize(d["impianti"])
    imp.to_csv(OUT / "digestori_impianti.csv", index=False)
    print(f"  + digestori_impianti     {len(imp)} impianti")

    # sintesi per classe di dieta
    s = d["sintesi_censimento"]
    diete = pd.DataFrame([
        {"classe": k.replace("_", " ").capitalize(), "impianti": v["n"],
         "kwe": v["kWe"], "quota_potenza_pct": v["quota_potenza_pct"]}
        for k, v in s["per_classe_dieta"].items()
    ])
    diete.to_csv(OUT / "digestori_diete.csv", index=False)

    # aggregati regionali, con i loro perimetri diversi
    fonti = pd.DataFrame([
        {"fonte": f["fonte"], "perimetro": f["perimetro"],
         "impianti": f.get("n_impianti"),
         "mw": f.get("potenza_MWe") or (f.get("potenza_kWe", 0) / 1000) or f.get("potenza_MW"),
         "affidabilita": f["affidabilita"]}
        for f in d["aggregati_regionali"]["fonti"]
    ])
    fonti.to_csv(OUT / "digestori_fonti.csv", index=False)

    # stima superficie a mais energetico
    m = d["stima_superficie_mais_energetico"]
    mais = pd.DataFrame([{
        "minimo_ha": m["risposta"]["minimo_ha"],
        "centrale_ha": m["risposta"]["centrale_ha"],
        "massimo_ha": m["risposta"]["massimo_ha"],
        "resa_kwh_ha": m["metodo"]["resa_kWh_elettrici_per_ha_silomais"],
    }])
    mais.to_csv(OUT / "digestori_mais.csv", index=False)

    # sintesi in un unico record, comoda per l'app
    pd.DataFrame([{
        "schedati": s["n_impianti_schedati"],
        "digestione_anaerobica": s["n_digestione_anaerobica"],
        "kwe_noti": s["con_potenza_elettrica_nota"]["totale_kWe"],
        "copertura_su_71": s["copertura_stimata_del_parco_pct"]["su_71_impianti"],
        "copertura_su_92": s["copertura_stimata_del_parco_pct"]["su_92_impianti"],
        "quota_colture_dedicate": s["per_classe_dieta"]["colture_dedicate"]["quota_potenza_pct"],
        "operativi": s["per_stato"].get("operativo", 0),
        "in_riconversione": s["per_stato"].get("in riconversione", 0),
    }]).to_csv(OUT / "digestori_sintesi.csv", index=False)

    print(f"  + digestori_diete        {len(diete)} classi di alimentazione")
    print(f"  + digestori_fonti        {len(fonti)} fonti con perimetri diversi")
    print(f"  + digestori_mais         stima {m['risposta']['centrale_ha']:,} ha centrali")
    print()
    print(diete.to_string(index=False))


if __name__ == "__main__":
    main()
