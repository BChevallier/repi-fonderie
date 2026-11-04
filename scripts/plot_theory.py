"""Rough, idealised curves of the three measured quantities against the shooting pressure.

Qualitative sketch (redrawn from the whiteboard drawing), not measured data:
  M  mass          rises fast, then flattens
  R  resistance    rises like M, peaks, then falls (dashed: what it would do without the drop)
  P  permeability  falls steeply, then slowly
Writes figures/courbes_theoriques_{light,dark}.png.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

root = Path(__file__).resolve().parent.parent
THEMES = {
    "dark": dict(bg="#000000", fg="#ffffff", muted="#898781"),
    "light": dict(bg="#ffffff", fg="#111111", muted="#6b6b6b"),
}
BLUE, RED, GREEN = "#42affa", "#ff5a5f", "#4cd97b"

X_PEAK = 0.42


def mass(x):
    return 0.95 * (1 - np.exp(-x / 0.25))


def resistance_ideal(x):
    return 0.85 * (1 - np.exp(-x / 0.3))


def resistance(x):
    drop = 0.39 * (1 - np.exp(-np.clip(x - X_PEAK, 0, None) / 0.25))
    return resistance_ideal(x) - drop


def permeability(x):
    return 0.15 + 0.85 * (0.08 / x) ** 0.9


x = np.linspace(0.08, 1.0, 400)
x_r = np.linspace(0.12, 1.0, 400)
x_d = np.linspace(X_PEAK, 1.0, 200)

for theme, c in THEMES.items():
    fig, ax = plt.subplots(figsize=(9, 5.4), dpi=200, facecolor=c["bg"])
    ax.set_facecolor(c["bg"])
    ax.plot(x, mass(x), color=BLUE, linewidth=3)
    ax.plot(x_r, resistance(x_r), color=RED, linewidth=3)
    ax.plot(x_d, resistance_ideal(x_d), color=RED, linewidth=2.2, linestyle=(0, (5, 4)))
    ax.plot(x, permeability(x), color=GREEN, linewidth=3)
    for label, color, y in (("M", BLUE, mass(1.0)), ("R", RED, resistance(1.0)),
                            ("P", GREEN, permeability(1.0))):
        ax.text(1.03, y, label, color=color, fontsize=18, fontweight="bold", va="center")
    ax.set_xlim(0, 1.12)
    ax.set_ylim(0, 1.08)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel(r"$P_{tir}$", color=c["fg"], fontsize=16, loc="right")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(c["muted"])
    fig.tight_layout()
    fig.savefig(root / "figures" / f"courbes_theoriques_{theme}.png", facecolor=c["bg"])
    plt.close(fig)
print("ok")
