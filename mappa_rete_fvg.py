"""
mappa_rete_fvg.py — mappa geografica della rete elettrica FVG.

Sostituisce il dashboard a barre `grid_status_fvg.png` con una carta vera,
costruita sulla geometria OpenInfraMap (linee aeree, EPSG:6708) incrociata
con la risorsa eolica RSE e il confine regionale.

Pannello sinistro : rete per livello di tensione
Pannello destro   : risorsa eolica + prossimita' alla rete AT
"""

import json
import pickle

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.patches import Patch

INK = "#1a1a1a"
ACC = "#0b5c4a"
COL = {380: "#c1272d", 220: "#e07b1f", 132: "#1f6fb2", 60: "#5aa0d0", 0: "#c9d3d0"}
LW = {380: 2.4, 220: 1.9, 132: 1.15, 60: 0.8, 0: 0.28}

geo = pickle.load(open("geo.pkl", "rb"))
lin = pd.read_pickle("linee_full.pkl")
rse = pd.read_csv("/mnt/user-data/outputs/rse_fvg_2026.csv")
bnd = json.load(open("/mnt/user-data/uploads/ITA_6_1.geojson"))["geometry"]["coordinates"]

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(17, 8.2))
fig.suptitle("Friuli Venezia Giulia — rete elettrica e risorsa eolica",
             fontsize=17, fontweight="bold", color=INK, y=0.97)


def confine(ax, lw=1.0):
    for poly in bnd:
        for r, ring in enumerate(poly):
            a = np.asarray(ring)
            ax.plot(a[:, 0], a[:, 1], color="#4a5a56", lw=lw if r == 0 else 0.5,
                    zorder=1, alpha=0.85)


def setup(ax, title, sub):
    confine(ax)
    ax.set_xlim(12.28, 13.98)
    ax.set_ylim(45.55, 46.68)
    ax.set_aspect(1 / np.cos(np.radians(46.1)))
    ax.set_title(f"{title}\n", fontsize=12.5, fontweight="bold", color=ACC, pad=16)
    ax.text(0.5, 1.012, sub, transform=ax.transAxes, ha="center", va="bottom",
            fontsize=8.5, color="#666")
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_edgecolor("#d8e0dd")


# ---------------------------------------------------------------- pannello 1
setup(ax1, "Rete di trasmissione e distribuzione aerea",
      "geometria OpenInfraMap (OSM), 6.598 km entro il confine regionale")

for kv in (0, 60, 132, 220, 380):
    idx = np.flatnonzero(lin.in_fvg.values & (lin.kV.values == kv))
    for i in idx:
        for s in geo[i]:
            ax1.plot(s[:, 0], s[:, 1], color=COL[kv], lw=LW[kv],
                     zorder=2 + (kv > 0) * 2 + kv / 1000, solid_capstyle="round",
                     alpha=0.55 if kv == 0 else 0.95)

km = lin[lin.in_fvg].groupby("kV").len_km.sum()
leg = [Line2D([], [], color=COL[k], lw=max(LW[k], 1.4),
              label=f"{lab} — {km.get(k, 0):,.0f} km".replace(",", "."))
       for k, lab in [(380, "380 kV"), (220, "220 kV"), (132, "132 kV"),
                      (60, "60 kV"), (0, "non classificate")]]
ax1.legend(handles=leg, loc="lower left", fontsize=8.4, frameon=True,
           facecolor="white", edgecolor="#d8e0dd", framealpha=0.94,
           title="Livello di tensione", title_fontsize=8.8)

nodi = {"Redipuglia": (13.49, 45.86), "Udine Ovest": (13.15, 46.03),
        "Planais": (13.20, 46.13), "Somplago": (13.00, 46.35),
        "Padriciano": (13.85, 45.68), "Monfalcone": (13.53, 45.79),
        "Cordignano": (12.42, 45.95), "Tarvisio": (13.58, 46.50)}
for n, (x, y) in nodi.items():
    ax1.plot(x, y, "o", ms=4.6, mfc="white", mec=INK, mew=1.15, zorder=9)
    ax1.annotate(n, (x, y), xytext=(4.5, 3.5), textcoords="offset points",
                 fontsize=7.4, color=INK, zorder=9,
                 bbox=dict(fc="white", ec="none", alpha=0.72, pad=0.9))

# ---------------------------------------------------------------- pannello 2
setup(ax2, "Risorsa eolica a 100 m e distanza dalla rete AT",
      "celle Atlante Eolico RSE 2026 (1,42 km) — soglia di bancabilita' 6,5 m/s")

lo = rse["long"].values
la = rse.lat.values
v = rse.vento_100.values
ax2.scatter(lo, la, c=v, s=4.0, cmap="YlOrRd", vmin=3.5, vmax=7.5,
            marker="s", alpha=0.75, linewidths=0, zorder=2)

for i in np.flatnonzero(lin.in_fvg.values & (lin.kV.values >= 132)):
    for s in geo[i]:
        ax2.plot(s[:, 0], s[:, 1], color="#2b3a36", lw=0.85, alpha=0.72, zorder=4)

hot = rse[(rse.vento_100 >= 6.5) & (rse.dist_AT_km <= 5)]
ax2.scatter(hot["long"], hot.lat, s=44, facecolors="none", edgecolors="#0b5c4a",
            linewidths=1.5, zorder=6,
            label=f"{len(hot)} celle >= 6,5 m/s entro 5 km dalla rete AT")

sm = plt.cm.ScalarMappable(cmap="YlOrRd", norm=plt.Normalize(3.5, 7.5))
cb = fig.colorbar(sm, ax=ax2, fraction=0.031, pad=0.015)
cb.set_label("velocita' media annua a 100 m (m/s)", fontsize=8.4)
cb.ax.tick_params(labelsize=7.6)

ax2.legend(handles=[
    Line2D([], [], color="#2b3a36", lw=1.2, label="rete >= 132 kV"),
    Line2D([], [], marker="o", color="none", mec="#0b5c4a", mew=1.5, ms=8,
           label=f"{len(hot)} celle bancabili entro 5 km dalla rete"),
], loc="lower left", fontsize=8.4, frameon=True, facecolor="white",
    edgecolor="#d8e0dd", framealpha=0.94)

ax2.annotate("Carso\ntriestino", (13.62, 45.63), fontsize=8.6, fontweight="bold",
             color="#8a2020", ha="center", zorder=9,
             bbox=dict(fc="white", ec="none", alpha=0.7, pad=1.2))

fig.text(0.012, 0.017,
         "Fonti: OpenInfraMap/OpenStreetMap (linee aeree, EPSG:6708) · Atlante Eolico RSE 2026 "
         "· confine ISTAT. Le linee non classificate sono in larga parte distribuzione MT "
         "priva di tag di tensione in OSM.",
         fontsize=7.6, color="#666", style="italic")

plt.tight_layout(rect=[0, 0.035, 1, 0.945])
fig.savefig("/mnt/user-data/outputs/mappa_rete_fvg.png", dpi=170, bbox_inches="tight")
print("ok")
