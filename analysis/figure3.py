"""Figure 3: passive versus co-contracted peak displacement for each participant.

Points below the dashed equality line had smaller displacement with
co-contraction. The red line is a least-squares fit; the p-value is the paired
comparison between conditions (as in Table 2), not the test of the slope.
"""
import matplotlib.pyplot as plt
import numpy as np
from scipy import stats

from plotting import CO_COLOR, clean_axes, format_p, paired_stats, save
from processing import values


def panel(ax, passive, co, limit, title):
    shade = 1 - 0.10 * (1 - CO_COLOR)  # solid light red so EPS matches other formats
    ax.fill([0, limit, limit], [0, 0, limit], color=shade, edgecolor="none", zorder=0)
    ax.plot([0, limit], [0, limit], ls="--", color="0.5", lw=1.2)
    ax.scatter(passive, co, s=55, color="0.15", edgecolors="none", zorder=3)

    fit = stats.linregress(passive, co)
    xs = np.array([0, limit])
    ax.plot(xs, fit.intercept + fit.slope * xs, color=CO_COLOR, lw=2.5, zorder=2)

    p, _, _ = paired_stats(passive, co)
    sign = "-" if fit.intercept < 0 else "+"
    equation = f"y = {fit.slope:.2f}x {sign} {abs(fit.intercept):.2f}"
    ax.text(0.05, 0.95, f"{equation}\nR$^2$ = {fit.rvalue ** 2:.3f}\n{format_p(p)}",
            transform=ax.transAxes, va="top", ha="left", fontsize=11)
    ax.text(0.97, 0.04, "Co-contraction\nreduces displacement", transform=ax.transAxes,
            va="bottom", ha="right", fontsize=9, style="italic", color=CO_COLOR * 0.85)
    ax.set_xlim(0, limit)
    ax.set_ylim(0, limit)
    ax.set_xlabel("Passive (cm)")
    ax.set_ylabel("Co-contracted (cm)")
    ax.set_title(title, fontsize=12)
    ax.set_aspect("equal")
    clean_axes(ax)


def make(passive, co, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.4))
    plt.subplots_adjust(wspace=0.3, left=0.08, right=0.98, top=0.9, bottom=0.14)
    panel(axes[0], values(passive, "head_peak_disp"), values(co, "head_peak_disp"), 25, "Head Displacement")
    panel(axes[1], values(passive, "torso_peak_disp"), values(co, "torso_peak_disp"), 10, "Torso Displacement")
    save(fig, out_dir, "Figure3_Displacement_Scatter")
    plt.close(fig)
