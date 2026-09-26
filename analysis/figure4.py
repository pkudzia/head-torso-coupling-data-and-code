"""Figure 4: head position relative to the torso, from onset to peak excursion.

Light lines are individual participants; the bold line is the mean path. The
vertical axis is flipped so that superior is up and inferior is down.
"""
import matplotlib.pyplot as plt
import numpy as np

from plotting import CO_COLOR, PASSIVE_COLOR, clean_axes, save
from processing import values


def panel(ax, cond, color, note):
    xs, ys = [], []
    for trial in cond["trials"].values():
        x = trial["waveforms"]["rel_x"]
        y = -trial["waveforms"]["rel_y"]  # downward head motion plotted as positive
        k = int(np.argmax(trial["waveforms"]["excursion"]))
        ax.plot(x[:k + 1], y[:k + 1], color=color, lw=0.8, alpha=0.30)
        xs.append(x)
        ys.append(y)

    mean_x, mean_y = np.mean(np.vstack(xs), axis=0), np.mean(np.vstack(ys), axis=0)
    k = int(np.argmax(cond["mean"]["excursion"]))
    ax.plot(mean_x[:k + 1], mean_y[:k + 1], color=color, lw=3.0, zorder=4)
    ax.plot(0, 0, "o", mfc="white", mec="0.3", ms=9, mew=1.5, zorder=5)
    ax.plot(mean_x[k], mean_y[k], "*", mfc=color, mec="k", ms=16, mew=1.0, zorder=6)

    ax.axvline(0, ls="--", color="0.4", lw=1.2)
    ax.axhline(0, color="0.6", lw=1.5, zorder=1)
    ax.set_xlim(-5, 18)
    ax.set_ylim(8, -2)
    ax.set_xlabel("Medial-Lateral (cm)")
    ax.set_ylabel("Superior-inferior (cm)")
    ax.text(0, 0.03, " Movement onset", transform=ax.get_xaxis_transform(), rotation=90,
            va="bottom", ha="right", fontsize=11)
    ax.text(0.98, 0.97, note, transform=ax.transAxes, ha="right", va="top", fontsize=11, color=color)
    clean_axes(ax)


def make(passive, co, out_dir):
    mean_p = values(passive, "excursion_peak").mean()
    mean_c = values(co, "excursion_peak").mean()
    change = (mean_c - mean_p) / mean_p * 100.0

    fig, axes = plt.subplots(1, 2, figsize=(9.5, 4.6), sharey=True)
    plt.subplots_adjust(wspace=0.12, left=0.09, right=0.98, top=0.95, bottom=0.13)
    panel(axes[0], passive, PASSIVE_COLOR, f"Mean: {mean_p:.1f} cm")
    panel(axes[1], co, CO_COLOR, f"Mean: {mean_c:.1f} cm\nReduction: {change:.0f}%")
    axes[1].legend(handles=[
        plt.Line2D([], [], color=PASSIVE_COLOR, lw=3, label="Passive"),
        plt.Line2D([], [], color=CO_COLOR, lw=3, label="Co-contracted"),
    ], loc="lower right", frameon=False, fontsize=10)
    save(fig, out_dir, "Figure4_Head_Relative_Torso")
    plt.close(fig)
