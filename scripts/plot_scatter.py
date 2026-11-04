"""Scatterplots for Tableau 1-3 (masse, permeabilite, cisaillement), light + dark.

Wide thick line = mean per sample, read from the first tbl-1 / tbl-2 / tbl-3 table in index.html.
Where data/raw.csv has the three measurements (fond, milieu, devant) for a sample, a
short horizontal line is drawn per measurement; a dot on its left / middle / right end
marks fond / milieu / devant.
Colour = method (BFSP, BBox, BF main).

Writes figures/{masse,permeabilite,cisaillement}_{light,dark}.png and
figures/cisaillement_bfsp_{light,dark}.png (BFSP only, so the y axis is not stretched
by the other methods).
"""
import csv
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

root = Path(__file__).resolve().parent.parent
html = (root / "index.html").read_text()

# (output name, table id, y label, methods kept)
PLOTS = [
    ("masse", "tbl-1", "Masse [g]", None),
    ("permeabilite", "tbl-2", "Perméabilité [GF]", None),
    ("cisaillement", "tbl-3", r"$F_{max}$ [N]", None),
    ("cisaillement_bfsp", "tbl-3", r"$F_{max}$ [N]", {"BFSP"}),
]
HALF = 0.18
MEAN_HALF = 0.28
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


raw = {}
with open(root / "data" / "raw.csv") as f:
    for r in csv.DictReader(f):
        raw.setdefault(r["quantity"], {})[r["sample"]] = [
            float(r[p]) for p in ("fond", "milieu", "devant")]


def group_of(name):
    return next(g for g in ("BFSP", "BBox", "BF main") if name.startswith(g))


for out_name, table_id, label, keep in PLOTS:
    q = out_name.split("_")[0]
    pts = [p for p in read_table(table_id) if keep is None or group_of(p[0]) in keep]
    for theme, c in THEMES.items():
        fig, ax = plt.subplots(figsize=(9, 5.4), dpi=200, facecolor=c["bg"])
        ax.set_facecolor(c["bg"])
        for x, (name, mean) in enumerate(pts):
            col = COLORS[group_of(name)]
            vals = raw.get(q, {}).get(name)
            if vals:
                # one short horizontal line per measurement; the dot sits on its left
                # (fond), middle (milieu) or right (devant) end
                for dot_x, v in zip((x - HALF, x, x + HALF), vals):
                    ax.hlines(v, x - HALF, x + HALF, color=col, linewidth=1.6, alpha=0.4,
                              zorder=3)
                    ax.scatter(dot_x, v, s=30, color=col, zorder=4)
            ax.hlines(mean, x - MEAN_HALF, x + MEAN_HALF, color=col, linewidth=3.5, zorder=5)
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
        ax.margins(y=0.1)
        handles = [Line2D([], [], marker="o", linestyle="", color=col, label=g)
                   for g, col in COLORS.items() if keep is None or g in keep]
        handles += [Line2D([], [], color=c["muted"], linewidth=3.5, label="moyenne"),
                    Line2D([], [], marker="_", markersize=14, linestyle="", color=c["muted"],
                           label="mesure : point à gauche = fond, milieu, droite = devant")]
        ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.0),
                  ncol=len(handles), frameon=False, fontsize=10, labelcolor=c["fg"],
                  columnspacing=1.8, handletextpad=0.5)
        fig.tight_layout()
        fig.savefig(root / "figures" / f"{out_name}_{theme}.png", facecolor=c["bg"])
        plt.close(fig)
    print(out_name, pts)
