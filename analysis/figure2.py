"""Figure 2: individual head and torso trajectories for all 19 participants.

Each panel shows one participant, with the torso start at the origin. Solid
lines trace each point from onset to its peak displacement, the dashed arrow is
the head's net displacement from start to peak, and the gray line joins the
head and torso start positions. Green labels give the head (H) and torso (T)
reduction in peak displacement with co-contraction.
"""
import matplotlib.pyplot as plt
import numpy as np

from plotting import CO_COLOR, PASSIVE_COLOR, save

GRAY = (0.5, 0.5, 0.5)
GREEN = (0.0, 0.5, 0.0)
XLIM = (-26, 26)
YLIM = (-8, 56)


def to_peak(trial):
    """Head and torso paths plus the sample index of each point's peak displacement."""
    tr = trial["trajectory"]
    hx, hy, tx, ty = tr["head_x"], tr["head_y"], tr["torso_x"], tr["torso_y"]
    head_peak = int(np.argmax(np.hypot(hx - hx[0], hy - hy[0])))
    torso_peak = int(np.argmax(np.hypot(tx - tx[0], ty - ty[0])))
    return hx, hy, tx, ty, head_peak, torso_peak


def draw(ax, trial, color):
    hx, hy, tx, ty, kh, kt = to_peak(trial)
    ax.plot([tx[0], hx[0]], [ty[0], hy[0]], color=GRAY, lw=1.0, zorder=1)
    ax.plot(hx[:kh + 1], hy[:kh + 1], color=color, lw=1.8, zorder=3)
    ax.plot(tx[:kt + 1], ty[:kt + 1], color=color, lw=1.5, zorder=3)
    ax.annotate("", xy=(hx[kh], hy[kh]), xytext=(hx[0], hy[0]),
                arrowprops=dict(arrowstyle="-|>", color=color, lw=1.3, ls="--",
                                shrinkA=0, shrinkB=0, alpha=0.9), zorder=4)
    ax.plot(hx[0], hy[0], "o", mfc="white", mec=color, ms=5, mew=1.2, zorder=5)
    ax.plot(hx[kh], hy[kh], "*", mfc=color, mec="k", ms=9, mew=0.8, zorder=6)


def make(passive, co, out_dir):
    fig, axes = plt.subplots(4, 5, figsize=(11, 12))
    plt.subplots_adjust(hspace=0.22, wspace=0.08, left=0.05, right=0.99, top=0.96, bottom=0.04)

    for i, p in enumerate(passive["trials"]):
        ax = axes.flat[i]
        tp, tc = passive["trials"][p], co["trials"][p]
        draw(ax, tp, PASSIVE_COLOR)
        draw(ax, tc, CO_COLOR)
        head_change = (tp["metrics"]["head_peak_disp"] - tc["metrics"]["head_peak_disp"]) \
            / tp["metrics"]["head_peak_disp"] * 100
        torso_change = (tp["metrics"]["torso_peak_disp"] - tc["metrics"]["torso_peak_disp"]) \
            / tp["metrics"]["torso_peak_disp"] * 100
        ax.set_title(p, fontsize=11, fontweight="bold")
        ax.text(0.97, 0.98, f"H:{head_change:.0f}%\nT:{torso_change:.0f}%", transform=ax.transAxes,
                ha="right", va="top", fontsize=8, color=GREEN, fontweight="bold")
        ax.set_xlim(*XLIM)
        ax.set_ylim(*YLIM)
        ax.set_aspect("equal")
        ax.axis("off")
        if i % 5 == 0:  # scale bars on the first panel of each row
            x0, y0 = XLIM[0] + 3, YLIM[0] + 6
            ax.plot([x0, x0], [y0, y0 + 20], "k-", lw=1.5)
            ax.text(x0 - 1.5, y0 + 10, "20 cm", rotation=90, va="center", ha="right", fontsize=8)
            ax.plot([x0, x0 + 25], [y0, y0], "k-", lw=1.5)
            ax.text(x0 + 12.5, y0 - 3.5, "25 cm", va="top", ha="center", fontsize=8)

    axes.flat[0].text(0.02, 0.62, "Head", transform=axes.flat[0].transAxes, fontsize=9, ha="left")
    axes.flat[0].text(0.02, 0.10, "Torso", transform=axes.flat[0].transAxes, fontsize=9, ha="left")
    axes.flat[19].axis("off")
    axes.flat[18].legend(handles=[
        plt.Line2D([], [], color=PASSIVE_COLOR, lw=2, label="Passive"),
        plt.Line2D([], [], color=CO_COLOR, lw=2, label="Co-contracted"),
    ], loc="center left", bbox_to_anchor=(1.05, 0.5), frameon=False, fontsize=11)

    fig.text(0.5, 0.005, "Medial-Lateral Movement (cm)", ha="center", fontsize=12)
    fig.text(0.008, 0.5, "Superior-Inferior Movement (cm)", va="center", rotation=90, fontsize=12)
    save(fig, out_dir, "Figure2_Individual_Trajectories")
    plt.close(fig)
