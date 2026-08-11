"""
Costruzione della curva di carico oraria del Friuli-Venezia Giulia.

Terna pubblica il carico a 15 minuti per **zona di mercato**, non per regione:
il FVG sta dentro la zona Nord insieme a mezza Italia industriale. La curva
regionale non esiste come dato, va ricostruita — e il modo in cui la si
ricostruisce e' la principale fonte di incertezza di tutto il modello, quindi
qui il metodo e' esplicito e i pezzi restano separati e ispezionabili.

**Metodo.** Si compone la domanda da tre profili settoriali, pesati con la
struttura dei consumi elettrici regionali (Terna 2024: industria 61,8%,
servizi 23,5%, domestico 14,7%):

* **industria** — forma quasi piatta, con riduzione nel fine settimana e fermo
  agostano. E' la componente che distingue il FVG dalla media di zona: qui
  l'industria pesa il 62% contro il 39% nazionale;
* **servizi** — profilo diurno feriale, ricavato dalla parte "modulante" della
  curva Nord, cioe' da quanto la zona si discosta dal proprio minimo notturno;
* **domestico** — profilo **misurato** ARERA per il FVG, con il picco serale
  alle 21 e la stagionalita' reale.

Il risultato viene scalato sulla richiesta elettrica regionale Terna e
confrontato con la curva Nord semplicemente riscalata, che e' l'alternativa
piu' ingenua: la differenza fra le due dice quanto pesa la ricostruzione.

Uso: python -m src.etl_carico
"""

from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW = ROOT / "data" / "raw" / "carico"
PRELIEVI = ROOT / "data" / "processed" / "prelievi_orari_fvg.csv"
OUT = ROOT / "data" / "processed"

ANNO_RIFERIMENTO = 2024
RICHIESTA_FVG_GWH = 9814.7          # Terna 2024, richiesta regionale

# Struttura dei consumi elettrici regionali (Terna 2024)
PESI_SETTORE = {"industria": 0.618, "servizi": 0.235, "domestico": 0.147}

# Modulazione del profilo industriale. Non e' misurata: e' il comportamento
# tipico di un carico manifatturiero con turni, e va dichiarato come ipotesi.
INDUSTRIA_WEEKEND = 0.75            # sabato e domenica rispetto al feriale
INDUSTRIA_AGOSTO = 0.65             # fermo estivo
INDUSTRIA_NOTTE = 0.88              # dalle 22 alle 6


def carica_nord() -> pd.DataFrame:
    """Curva di carico della zona Nord, da 15 minuti a oraria."""
    pezzi = []
    for f in sorted(glob.glob(str(RAW / "*.xlsx"))):
        d = pd.read_excel(f)
        d = d[pd.to_datetime(d["Date"], errors="coerce").notna()].copy()
        d["Date"] = pd.to_datetime(d["Date"])
        pezzi.append(d[["Date", "Total Load [MW]"]])
    if not pezzi:
        raise SystemExit(f"Nessun file di carico in {RAW}")
    d = pd.concat(pezzi).sort_values("Date").drop_duplicates("Date")
    d = d.set_index("Date")["Total Load [MW]"].resample("h").mean().dropna()
    return d.to_frame("nord_mw")


def profilo_industria(indice: pd.DatetimeIndex) -> np.ndarray:
    """Carico manifatturiero: piatto, con weekend e agosto ridotti."""
    p = np.ones(len(indice))
    p[indice.dayofweek >= 5] *= INDUSTRIA_WEEKEND
    p[indice.month == 8] *= INDUSTRIA_AGOSTO
    p[(indice.hour >= 22) | (indice.hour < 6)] *= INDUSTRIA_NOTTE
    return p


def profilo_servizi(nord: pd.Series) -> np.ndarray:
    """Parte modulante della curva Nord: quanto si discosta dal minimo notturno.

    Il terziario e' ciò che accende e spegne con la giornata lavorativa, ed e'
    esattamente la componente che fa oscillare la curva di zona sopra la sua
    base. Usarla come forma evita di inventare un profilo.
    """
    base = nord.groupby(nord.index.date).transform("min")
    modulante = (nord - base).clip(lower=0)
    return modulante.to_numpy()


def profilo_domestico(indice: pd.DatetimeIndex) -> np.ndarray:
    """Profilo misurato ARERA per il FVG: mese x tipo di giorno x ora."""
    if not PRELIEVI.exists():
        return np.ones(len(indice))
    d = pd.read_csv(PRELIEVI)
    med = d.groupby(["mese_n", "tipo_giorno", "ora_n"])["kwh"].mean()
    feriale = [k for k in d["tipo_giorno"].unique() if "feriale" in str(k).lower()]
    festivo = [k for k in d["tipo_giorno"].unique() if "festiv" in str(k).lower()]
    f_key = feriale[0] if feriale else d["tipo_giorno"].iloc[0]
    s_key = festivo[0] if festivo else f_key

    valori = []
    for ts in indice:
        chiave = (ts.month, s_key if ts.dayofweek >= 5 else f_key, ts.hour)
        valori.append(med.get(chiave, np.nan))
    v = pd.Series(valori).ffill().bfill().to_numpy()
    return v


def normalizza(x: np.ndarray) -> np.ndarray:
    somma = x.sum()
    return x / somma if somma else x


def main() -> None:
    nord = carica_nord()
    anno = nord[nord.index.year == ANNO_RIFERIMENTO]
    if anno.empty:
        anno = nord[nord.index.year == nord.index.year.max()]
    serie_nord = anno["nord_mw"]
    indice = serie_nord.index
    print(f"Curva zona Nord {indice[0]:%Y}: {len(indice)} ore, "
          f"{serie_nord.sum() / 1e6:.1f} TWh")

    componenti = {
        "industria": normalizza(profilo_industria(indice)),
        "servizi": normalizza(profilo_servizi(serie_nord)),
        "domestico": normalizza(profilo_domestico(indice)),
    }
    energia_mwh = RICHIESTA_FVG_GWH * 1000
    carico = sum(componenti[k] * PESI_SETTORE[k] * energia_mwh for k in componenti)

    # alternativa ingenua: la curva Nord semplicemente riscalata
    carico_ingenuo = normalizza(serie_nord.to_numpy()) * energia_mwh

    out = pd.DataFrame({
        "carico_totale_mw": carico,
        "carico_scalato_nord_mw": carico_ingenuo,
        "quota_industria_mw": componenti["industria"] * PESI_SETTORE["industria"] * energia_mwh,
        "quota_servizi_mw": componenti["servizi"] * PESI_SETTORE["servizi"] * energia_mwh,
        "quota_domestico_mw": componenti["domestico"] * PESI_SETTORE["domestico"] * energia_mwh,
    }, index=indice)
    out.index.name = "ora"
    out.round(2).to_csv(OUT / "carico_fvg_orario.csv")

    scarto = (out["carico_totale_mw"] - out["carico_scalato_nord_mw"]).abs().mean()
    corr = np.corrcoef(out["carico_totale_mw"], out["carico_scalato_nord_mw"])[0, 1]
    print(f"\n  + carico_fvg_orario   {len(out)} ore, {out['carico_totale_mw'].sum() / 1e6:.2f} TWh")
    print(f"    punta {out['carico_totale_mw'].max():.0f} MW, "
          f"minimo {out['carico_totale_mw'].min():.0f} MW, "
          f"fattore di carico {out['carico_totale_mw'].mean() / out['carico_totale_mw'].max():.2f}")
    print(f"    scarto medio dalla curva Nord riscalata: {scarto:.0f} MW "
          f"({scarto / out['carico_totale_mw'].mean() * 100:.1f}%), correlazione {corr:.3f}")
    print(f"    punta della curva Nord riscalata: {out['carico_scalato_nord_mw'].max():.0f} MW")


if __name__ == "__main__":
    main()
