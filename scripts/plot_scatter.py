"""Scatterplots for Tableau 1-3 (masse, permeabilite, cisaillement), light + dark.

BFSP: raw points per position (fond/milieu/devant) from data/bfsp_raw.csv, plus the mean.
BBox / BF main: only means exist (read from the first tbl-1 / tbl-2 in index.html).
Colour = method (BFSP, BBox, BF main), marker = position.
Writes figures/{masse,permeabilite,cisaillement}_{light,dark}.png.
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


def html_means(table_id):
    t = re.search(rf'<table data-id="{table_id}">(.*?)</table>', html, re.S).group(1)
    rows = re.findall(r"<tr[^>]*><td>(.*?)</td><td>(.*?)</td></tr>", t)
    return {n: float(v.replace(",", ".")) for n, v in rows if re.match(r"^[\d,\.]+$", v)}


raw = {}
with open(root / "data" / "bfsp_raw.csv") as f:
    for r in csv.DictReader(f):
        raw.setdefault(r["quantity"], {})[int(r["pression"])] = {
            p: float(r[p]) for p in ("fond", "milieu", "devant")}

QUANTITIES = {
    "masse": dict(label="Masse [g]", means=html_means("tbl-1")),
    "permeabilite": dict(label="Perméabilité [GF]", means=html_means("tbl-2")),
    "cisaillement": dict(label=r"$\tau_{max}$ [N]", means={}),
}
SAMPLES = ([("BFSP", f"BFSP {i} bar") for i in range(1, 7)]
           + [("BBox", f"BBox {i}") for i in (1, 2)]
           + [("BF main", f"BF main {i}%") for i in (1, 2)])
COLORS = {"BFSP": "#42affa", "BBox": "#ff9f43", "BF main": "#4cd97b"}
POS = {"fond": ("o", -0.18), "milieu": ("s", 0.0), "devant": ("^", 0.18)}
THEMES = {
    "dark": dict(bg="#000000", fg="#ffffff", muted="#898781", grid=(1, 1, 1, 0.12)),
    "light": dict(bg="#ffffff", fg="#111111", muted="#6b6b6b", grid=(0, 0, 0, 0.12)),
}

for q, cfg in QUANTITIES.items():
    # samples with data for this quantity, keeping order
    pts = []  # (x, group, name, {pos: value} or None, mean)
    for group, name in SAMPLES:
        if group == "BFSP":
            i = int(name.split()[1])
            vals = raw[q][i]
            pts.append((group, name, vals, sum(vals.values()) / 3))
        elif name in cfg["means"]:
            pts.append((group, name, None, cfg["means"][name]))
    for theme, c in THEMES.items():
        fig, ax = plt.subplots(figsize=(9, 5.4), dpi=200, facecolor=c["bg"])
        ax.set_facecolor(c["bg"])
        for x, (group, name, vals, mean) in enumerate(pts):
            col = COLORS[group]
            if vals:
                for p, v in vals.items():
                    m, dx = POS[p]
                    ax.scatter(x + dx, v, s=45, marker=m, color=col, alpha=0.9, zorder=3)
            ax.hlines(mean, x - 0.3, x + 0.3, color=col, linewidth=2, zorder=4)
            if not vals:
                ax.scatter(x, mean, s=70, marker="D", color=col, zorder=3)
        ax.set_xticks(range(len(pts)), [p[1] for p in pts], rotation=40, ha="right",
                      color=c["fg"], fontsize=11)
        ax.tick_params(axis="y", colors=c["fg"], labelsize=11)
        ax.tick_params(axis="x", length=0)
        ax.set_ylabel(cfg["label"], color=c["fg"], fontsize=13)
        ax.grid(axis="y", color=c["grid"], linewidth=0.8)
        ax.set_axisbelow(True)
        for side in ("top", "right"):
            ax.spines[side].set_visible(False)
        for side in ("left", "bottom"):
            ax.spines[side].set_color(c["muted"])
        ax.set_xlim(-0.6, len(pts) - 0.4)
        handles = [Line2D([], [], marker="s", linestyle="", color=col, label=g)
                   for g, col in COLORS.items() if any(p[0] == g for p in pts)]
        handles += [Line2D([], [], marker=m, linestyle="", color=c["muted"], label=p)
                    for p, (m, _) in POS.items()]
        handles.append(Line2D([], [], color=c["muted"], linewidth=2, label="moyenne"))
        leg = ax.legend(handles=handles, loc="lower center", bbox_to_anchor=(0.5, 1.0), ncol=7,
                        frameon=False, fontsize=10, columnspacing=1.2, handletextpad=0.3, labelcolor=c["fg"])
        fig.tight_layout()
        fig.savefig(root / "figures" / f"{q}_{theme}.png", facecolor=c["bg"])
        plt.close(fig)
    print(q, [(p[1], round(p[3], 1)) for p in pts])
