"""Rough, idealised force-displacement curves of the shear test for several pressures.

Not measured data: a qualitative model. Each curve rises, peaks at F_max(p), then softens
to a residual plateau. F_max grows with pressure and saturates (denser sand, then
diminishing returns); the curve shape is the same for every pressure.
Writes figures/courbes_theoriques_{light,dark}.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import to_rgb

root = Path(__file__).resolve().parent.parent
PRESSURES = [1, 2, 3, 4, 5, 6]
THEMES = {
    "dark": dict(bg="#000000", fg="#ffffff", muted="#898781", low="#1d4568"),
    "light": dict(bg="#ffffff", fg="#111111", muted="#6b6b6b", low="#c3dff5"),
}
HIGH = "#42affa"


X_PEAK = 1.0
RESIDUAL = 0.45


def f_max(p):
    return 1 - np.exp(-p / 4)


def curve(x, p):
    u = x / X_PEAK
    return f_max(p) * ((1 - RESIDUAL) * u * np.exp(1 - u) + RESIDUAL * (1 - np.exp(-3 * u)))


x = np.linspace(0, 4, 400)
for theme, c in THEMES.items():
    lo, hi = np.array(to_rgb(c["low"])), np.array(to_rgb(HIGH))
    fig, ax = plt.subplots(figsize=(9, 5.4), dpi=200, facecolor=c["bg"])
    ax.set_facecolor(c["bg"])
    for p in PRESSURES:
        col = lo + (hi - lo) * (p - 1) / (len(PRESSURES) - 1)
        y = curve(x, p)
        ax.plot(x, y, color=col, linewidth=2.6)
        ax.text(1.3, float(curve(1.3, p)) + 0.025, f"{p} bar", color=col, ha="center", va="bottom",
                fontsize=11)
    ax.set_xlim(0, 4)
    ax.set_ylim(0, 0.95)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("Déplacement (u.a.)", color=c["fg"], fontsize=13)
    ax.set_ylabel(r"Force $F$ (u.a.)", color=c["fg"], fontsize=13)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(c["muted"])
    fig.tight_layout()
    fig.savefig(root / "figures" / f"courbes_theoriques_{theme}.png", facecolor=c["bg"])
    plt.close(fig)
print("ok")
