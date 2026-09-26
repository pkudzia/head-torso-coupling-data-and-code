"""Shared figure style and helpers used by all figure scripts."""
import os

import matplotlib as mpl
import numpy as np
from scipy import stats

PASSIVE_COLOR = np.array([0.20, 0.20, 0.80])
CO_COLOR = np.array([0.80, 0.20, 0.20])

mpl.rcParams["font.family"] = "sans-serif"
mpl.rcParams["font.sans-serif"] = ["Arial", "Helvetica", "DejaVu Sans"]
mpl.rcParams["pdf.fonttype"] = 42   # keep text editable in vector files
mpl.rcParams["ps.fonttype"] = 42
mpl.rcParams["svg.fonttype"] = "none"
mpl.rcParams["axes.linewidth"] = 0.75
mpl.rcParams["xtick.direction"] = "out"
mpl.rcParams["ytick.direction"] = "out"

FORMATS = ("png", "pdf", "eps", "tiff")


def save(fig, out_dir, name, dpi=300):
    """Save a figure in every journal format."""
    os.makedirs(out_dir, exist_ok=True)
    for ext in FORMATS:
        fig.savefig(os.path.join(out_dir, f"{name}.{ext}"), dpi=dpi,
                    bbox_inches="tight", facecolor="white")


def clean_axes(ax):
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.tick_params(direction="out", length=3)


def paired_stats(passive, co):
    """p-value, paired Cohen's d, and percent change for an inset annotation."""
    passive, co = np.asarray(passive, float), np.asarray(co, float)
    diff = co - passive
    p = stats.ttest_rel(co, passive).pvalue
    d = diff.mean() / diff.std(ddof=1)
    pct = (co.mean() - passive.mean()) / abs(passive.mean()) * 100.0
    return p, d, pct


def format_p(p):
    return "p < 0.001" if p < 0.001 else f"p = {p:.3f}"


def inset_boxplot(ax, passive, co, ylabel, jitter=0.06, seed=0):
    """Passive (left) and co-contracted (right) boxplots with individual points.

    Boxes show the median and interquartile range; whiskers span the full range.
    The annotation gives the paired p-value, Cohen's d, and percent change.
    """
    rng = np.random.default_rng(seed)
    groups = [np.asarray(passive, float), np.asarray(co, float)]
    colors = [PASSIVE_COLOR, CO_COLOR]
    bp = ax.boxplot(groups, positions=[1, 2], widths=0.55, whis=(0, 100),
                    patch_artist=True, showcaps=True, showfliers=False,
                    medianprops=dict(color="0.15", lw=1.3),
                    whiskerprops=dict(color="0.15", lw=1.0, ls="--"),
                    capprops=dict(color="0.15", lw=1.0),
                    boxprops=dict(lw=1.0))
    for box, c in zip(bp["boxes"], colors):
        box.set_facecolor(np.append(c, 0.35))
        box.set_edgecolor(c)
    for pos, vals, c in zip([1, 2], groups, colors):
        x = pos + rng.uniform(-jitter, jitter, size=len(vals))
        ax.scatter(x, vals, s=16, color=c, alpha=0.75, edgecolors="none", zorder=3)

    ax.set_xlim(0.4, 2.6)
    ax.set_xticks([])
    ax.set_ylabel(ylabel, fontsize=8)
    ax.tick_params(labelsize=8)
    clean_axes(ax)

    p, d, pct = paired_stats(*groups)
    top = max(g.max() for g in groups)
    span = top - min(g.min() for g in groups)
    bracket = top + 0.06 * span
    ax.set_ylim(top=bracket + 0.70 * span)
    ax.plot([1, 1, 2, 2], [bracket, bracket + 0.03 * span, bracket + 0.03 * span, bracket],
            color="0.2", lw=0.9)
    ax.text(1.5, bracket + 0.05 * span, format_p(p), ha="center", va="bottom",
            fontsize=7.5, style="italic")
    ax.text(0.99, 0.99, f"d = {d:.2f}\nΔ = {pct:.1f}%", ha="right", va="top",
            fontsize=7.5, transform=ax.transAxes)


def plot_mean_sd(ax, passive, co, key):
    """Condition mean waveforms with shaded ±1 SD bands."""
    t = passive["time"] * 1000.0
    for cond, color, label in ((passive, PASSIVE_COLOR, "Passive"), (co, CO_COLOR, "Co-contracted")):
        m, s = cond["mean"][key], cond["sd"][key]
        ax.fill_between(t, m - s, m + s, color=color, alpha=0.2, linewidth=0)
        ax.plot(t, m, color=color, lw=1.5, label=label)
    ax.axvline(0, ls="--", color="k", lw=1)
    ax.set_xlim(-50, 500)
