"""Figure 5: head and torso displacement, velocity, and acceleration.

Lines are condition means and bands are ±1 SD. Insets show each participant's
peak value with the paired p-value, Cohen's d, and percent change.
"""
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from plotting import clean_axes, inset_boxplot, plot_mean_sd, save
from processing import values

# row, column, waveform, y-limits, y-ticks, y-label, peak metric, inset label, title
PANELS = [
    (0, 0, "head_disp", (-1, 35), range(0, 36, 5), "Position (cm)",
     "head_peak_disp", "Peak Displacement (cm)", "Head"),
    (0, 1, "torso_disp", (-1, 35), range(0, 36, 5), "Position (cm)",
     "torso_peak_disp", "Peak Displacement (cm)", "Torso"),
    (1, 0, "head_vel", (0, 160), range(0, 161, 40), "Velocity (cm s$^{-1}$)",
     "head_peak_vel", "Peak Velocity (cm s$^{-1}$)", None),
    (1, 1, "torso_vel", (0, 160), range(0, 161, 40), "Velocity (cm s$^{-1}$)",
     "torso_peak_vel", "Peak Velocity (cm s$^{-1}$)", None),
    (2, 0, "head_acc", (0, 12), range(0, 13, 3), "Acceleration (g)",
     "head_peak_acc", "Peak Acceleration (g)", None),
    (2, 1, "torso_acc", (0, 12), range(0, 13, 3), "Acceleration (g)",
     "torso_peak_acc", "Peak Acceleration (g)", None),
]


def make(passive, co, out_dir):
    fig, axes = plt.subplots(3, 2, figsize=(7.2, 8.6))
    plt.subplots_adjust(hspace=0.32, wspace=0.28, left=0.09, right=0.97, top=0.95, bottom=0.07)

    for row, col, key, ylim, yticks, ylabel, metric, inset_label, title in PANELS:
        ax = axes[row, col]
        plot_mean_sd(ax, passive, co, key)
        ax.set_ylim(*ylim)
        ax.set_yticks(list(yticks))
        ax.set_ylabel(ylabel)
        if title:
            ax.set_title(title, fontsize=12)
        clean_axes(ax)
        if (row, col) == (0, 1):
            ax.legend(loc="center right", frameon=False, fontsize=10)
        if row == 0:
            ax.text(-12, 0.06, "Movement onset", transform=ax.get_xaxis_transform(), rotation=90,
                    va="bottom", ha="right", fontsize=9)
        if row == 2:
            ax.set_xlabel("Time (ms)")
        inset = inset_axes(ax, width="46%", height="52%", loc="upper right",
                           bbox_to_anchor=(0, 0, 0.98, 0.98), bbox_transform=ax.transAxes)
        inset_boxplot(inset, values(passive, metric), values(co, metric), inset_label)

    save(fig, out_dir, "Figure5_Head_Torso_Kinematics")
    plt.close(fig)
