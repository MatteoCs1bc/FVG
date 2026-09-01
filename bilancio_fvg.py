"""
bilancio_fvg.py — bilancio orario domanda/generazione per il FVG.

Lavora sul dataset orario 2005-2023 (166.536 ore) e calcola, per uno scenario
di potenza installata:
  - carico residuo ora per ora
  - ore e energia di surplus (curtailment potenziale)
  - dimensionamento dell'accumulo per assorbire il surplus
  - copertura FER e picco residuo

Uso:
    from bilancio_fvg import Scenario, bilancio, dimensiona_accumulo
    r = bilancio(df, Scenario(fv_mw=2500, eolico_mw=300))
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

# Idroelettrico FVG: produzione media annua e ripartizione stagionale
# (fusione nivale primaverile, magra invernale). Fonte: PER FVG / Terna.
IDRO_GWH_ANNO = 1750.0
IDRO_PROFILO_MENSILE = np.array([0.62, 0.60, 0.78, 1.18, 1.42, 1.38,
                                 1.20, 1.02, 1.02, 1.02, 0.92, 0.84])

# Bioenergie: profilo piatto, funzionamento baseload
BIO_GWH_ANNO = 700.0


@dataclass
class Scenario:
    nome: str = "scenario"
    fv_mw: float = 1250.0          # e-distribuzione: 1,25 GW FV connessi
    eolico_mw: float = 0.0
    sito_eolico: str = "Carso_Basovizza"
    idro_gwh: float = IDRO_GWH_ANNO
    bio_gwh: float = BIO_GWH_ANNO
    accumulo_mw: float = 0.0
    accumulo_mwh: float = 0.0
    rendimento_accumulo: float = 0.88   # round-trip


def _idro(idx: pd.DatetimeIndex, gwh: float) -> np.ndarray:
    m = IDRO_PROFILO_MENSILE[idx.month - 1]
    return m / m.mean() * (gwh * 1e3 / 8766.0)


def bilancio(df: pd.DataFrame, sc: Scenario) -> pd.DataFrame:
    """Serie oraria di generazione, carico residuo e surplus (MW)."""
    out = pd.DataFrame(index=df.index)
    out["carico_mw"] = df["carico_totale_mw"]
    out["fv_mw"] = df["cf_fv_regionale"] * sc.fv_mw

    col = f"cf_eolico_{sc.sito_eolico}"
    out["eolico_mw"] = (df[col] * sc.eolico_mw) if (col in df and sc.eolico_mw) else 0.0

    out["idro_mw"] = _idro(df.index, sc.idro_gwh)
    out["bio_mw"] = sc.bio_gwh * 1e3 / 8766.0

    out["fer_mw"] = out[["fv_mw", "eolico_mw", "idro_mw", "bio_mw"]].sum(axis=1)
    out["residuo_mw"] = out["carico_mw"] - out["fer_mw"]
    out["surplus_mw"] = (-out["residuo_mw"]).clip(lower=0)
    out["deficit_mw"] = out["residuo_mw"].clip(lower=0)
    return out


def simula_accumulo(bil: pd.DataFrame, sc: Scenario) -> pd.DataFrame:
    """Dispacciamento greedy: carica sul surplus, scarica sul deficit."""
    if sc.accumulo_mwh <= 0:
        bil = bil.copy()
        bil["soc_mwh"] = 0.0
        bil["residuo_post_mw"] = bil["residuo_mw"]
        bil["curtailment_mw"] = bil["surplus_mw"]
        return bil

    eta = np.sqrt(sc.rendimento_accumulo)
    surp = bil["surplus_mw"].to_numpy()
    defi = bil["deficit_mw"].to_numpy()
    soc = np.zeros(len(bil))
    curt = np.zeros(len(bil))
    scar = np.zeros(len(bil))
    s = 0.0
    for i in range(len(bil)):
        if surp[i] > 0:
            carica = min(surp[i], sc.accumulo_mw, (sc.accumulo_mwh - s) / eta)
            s += carica * eta
            curt[i] = surp[i] - carica
        elif defi[i] > 0:
            scarica = min(defi[i], sc.accumulo_mw, s * eta)
            s -= scarica / eta
            scar[i] = scarica
        soc[i] = s

    out = bil.copy()
    out["soc_mwh"] = soc
    out["curtailment_mw"] = curt
    out["scarica_mw"] = scar
    out["residuo_post_mw"] = out["residuo_mw"] - scar + (out["surplus_mw"] - curt)
    return out


def indicatori(bil: pd.DataFrame, sc: Scenario) -> dict:
    anni = len(bil) / 8766.0
    car = bil["carico_mw"].sum() / 1e3 / anni
    fer = bil["fer_mw"].sum() / 1e3 / anni
    surp = bil["surplus_mw"].sum() / 1e3 / anni
    autoc = (bil["fer_mw"] - bil["surplus_mw"]).sum() / 1e3 / anni

    d = {
        "scenario": sc.nome,
        "potenza_fv_mw": sc.fv_mw,
        "potenza_eolico_mw": sc.eolico_mw,
        "domanda_gwh_anno": round(car),
        "generazione_fer_gwh_anno": round(fer),
        "fer_utilizzabile_gwh_anno": round(autoc),
        "copertura_lorda_pct": round(fer / car * 100, 1),
        "copertura_effettiva_pct": round(autoc / car * 100, 1),
        "surplus_gwh_anno": round(surp, 1),
        "surplus_su_generazione_pct": round(surp / fer * 100, 1),
        "ore_surplus_anno": round(float((bil["surplus_mw"] > 0).sum()) / anni),
        "surplus_max_mw": round(float(bil["surplus_mw"].max())),
        "picco_residuo_mw": round(float(bil["residuo_mw"].max())),
        "picco_carico_mw": round(float(bil["carico_mw"].max())),
    }
    if "curtailment_mw" in bil and sc.accumulo_mwh > 0:
        curt = bil["curtailment_mw"].sum() / 1e3 / anni
        d["accumulo_mw"] = sc.accumulo_mw
        d["accumulo_mwh"] = sc.accumulo_mwh
        d["curtailment_residuo_gwh_anno"] = round(curt, 1)
        d["surplus_recuperato_pct"] = round((1 - curt / surp) * 100, 1) if surp else 0.0
        d["picco_residuo_post_mw"] = round(float(bil["residuo_post_mw"].max()))
    return d


def dimensiona_accumulo(df: pd.DataFrame, sc: Scenario,
                        tagli_mwh=(500, 1000, 2000, 4000, 8000),
                        ore_scarica: float = 4.0) -> pd.DataFrame:
    """Curva di rendimento marginale dell'accumulo: quanto surplus recupera."""
    base = bilancio(df, sc)
    righe = []
    for e in tagli_mwh:
        s2 = Scenario(**{**sc.__dict__, "accumulo_mwh": e,
                         "accumulo_mw": e / ore_scarica})
        r = simula_accumulo(base, s2)
        i = indicatori(r, s2)
        righe.append({"accumulo_mwh": e, "accumulo_mw": round(e / ore_scarica),
                      "surplus_recuperato_pct": i["surplus_recuperato_pct"],
                      "curtailment_gwh": i["curtailment_residuo_gwh_anno"],
                      "copertura_effettiva_pct": round(
                          (base["fer_mw"].sum() / 1e3 - r["curtailment_mw"].sum() / 1e3)
                          / (base["carico_mw"].sum() / 1e3) * 100, 1)})
    return pd.DataFrame(righe)


if __name__ == "__main__":
    df = pd.read_parquet("/mnt/user-data/outputs/fvg_orario_2005_2023.parquet")

    scenari = [
        Scenario("attuale (2025)", fv_mw=1250, eolico_mw=0),
        Scenario("target 2030 senza eolico", fv_mw=2900, eolico_mw=0),
        Scenario("target 2030 con 300 MW eolici", fv_mw=2600, eolico_mw=300),
        Scenario("target 2030 con 500 MW eolici", fv_mw=2400, eolico_mw=500),
    ]
    res = pd.DataFrame([indicatori(bilancio(df, s), s) for s in scenari])
    print(res.to_string(index=False))
