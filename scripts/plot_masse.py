"""Tableau 1 (Masse [g] per sample) as a scatterplot, light + dark.

Reads the first tbl-1 table in index.html so the slide and the plot share one source.
Writes figures/masse_light.png and figures/masse_dark.png.
"""
import re
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parent.parent
html = (root / "index.html").read_text()
table = re.search(r'<table data-id="tbl-1">(.*?)</table>', html, re.S).group(1)
rows = re.findall(r"<tr[^>]*><td>(.*?)</td><td>(.*?)</td></tr>", table)
names = [n for n, _ in rows]
mass = [float(m.replace(",", ".")) for _, m in rows]

ACCENT = "#42affa"
THEMES = {
    "dark": dict(bg="#000000", fg="#ffffff", muted="#898781", grid=(1, 1, 1, 0.12)),
    "light": dict(bg="#ffffff", fg="#111111", muted="#6b6b6b", grid=(0, 0, 0, 0.12)),
}

for theme, c in THEMES.items():
    fig, ax = plt.subplots(figsize=(9, 5.4), dpi=200, facecolor=c["bg"])
    ax.set_facecolor(c["bg"])
    x = range(len(names))
    ax.scatter(x, mass, s=90, color=ACCENT, zorder=3)
    ax.set_xticks(list(x), names, rotation=40, ha="right", color=c["fg"], fontsize=11)
    ax.tick_params(axis="y", colors=c["fg"], labelsize=11)
    ax.tick_params(axis="x", length=0)
    ax.set_ylabel("Masse [g]", color=c["fg"], fontsize=13)
    ax.grid(axis="y", color=c["grid"], linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(c["muted"])
    ax.set_xlim(-0.6, len(names) - 0.4)
    fig.tight_layout()
    fig.savefig(root / "figures" / f"masse_{theme}.png", facecolor=c["bg"])
    plt.close(fig)
print(names, mass)
