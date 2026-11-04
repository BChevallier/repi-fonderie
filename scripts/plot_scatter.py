"""Scatterplots for Tableau 1-3 (masse, permeabilite, cisaillement), light + dark.

One dot per sample, read from the first tbl-1 / tbl-2 / tbl-3 table in index.html
so the slides and the plots share one source. Colour = method (BFSP, BBox, BF main).
Writes figures/{masse,permeabilite,cisaillement}_{light,dark}.png.
"""
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

root = Path(__file__).resolve().parent.parent
html = (root / "index.html").read_text()

QUANTITIES = {
    "masse": ("tbl-1", "Masse [g]"),
    "permeabilite": ("tbl-2", "Perméabilité [GF]"),
    "cisaillement": ("tbl-3", r"$\tau_{max}$ [N]"),
}
COLORS = {"BFSP": "#42affa", "BBox": "#ff9f43", "BF main": "#4cd97b"}
THEMES = {
    "dark": dict(bg="#000000", fg="#ffffff", muted="#898781", grid=(1, 1, 1, 0.12)),
    "light": dict(bg="#ffffff", fg="#111111", muted="#6b6b6b", grid=(0, 0, 0, 0.12)),
}


def read_table(table_id):
    t = re.search(rf'<table data-id="{table_id}">(.*?)</table>', html, re.S).group(1)
    rows = re.findall(r"<tr[^>]*><td>(.*?)</td><td>(.*?)</td></tr>", t)
    out = []
    for name, v in rows:
        v = v.replace(" ", "").replace(" ", "").replace(",", ".")
        if re.fullmatch(r"[\d.]+", v):
            out.append((name, float(v)))
    return out


def group_of(name):
    return next(g for g in ("BFSP", "BBox", "BF main") if name.startswith(g))


for q, (table_id, label) in QUANTITIES.items():
    pts = read_table(table_id)
    for theme, c in THEMES.items():
        fig, ax = plt.subplots(figsize=(9, 5.4), dpi=200, facecolor=c["bg"])
        ax.set_facecolor(c["bg"])
        for x, (name, v) in enumerate(pts):
            ax.scatter(x, v, s=110, color=COLORS[group_of(name)], zorder=3)
        ax.set_xticks(range(len(pts)), [n for n, _ in pts], rotation=40, ha="right",
                      color=c["fg"], fontsize=11)
        ax.tick_params(axis="y", colors=c["fg"], labelsize=11)
        ax.tick_params(axis="x", length=0)
        ax.set_ylabel(label, color=c["fg"], fontsize=13)
        ax.grid(axis="y", color=c["grid"], linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(c["muted"])
        ax.set_xlim(-0.6, len(pts) - 0.4)
        handles = [Line2D([], [], marker="o", linestyle="", color=col, label=g)
                   for g, col in COLORS.items()]
        ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=3,
                  frameon=False, fontsize=11, labelcolor=c["fg"])
        fig.tight_layout()
        fig.savefig(root / "figures" / f"{q}_{theme}.png", facecolor=c["bg"])
        plt.close(fig)
    print(q, pts)
