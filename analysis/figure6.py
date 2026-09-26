"""Figure 6: angular velocity and acceleration of the head-torso vector.

These describe rotation of the line joining the head and torso tracking points,
not anatomical head rotation. Insets show each participant's peak magnitude.
"""
import matplotlib.pyplot as plt
from mpl_toolkits.axes_grid1.inset_locator import inset_axes

from plotting import clean_axes, inset_boxplot, plot_mean_sd, save
from processing import values


def panel(ax, passive, co, key, ylim, yticks, ylabel, title, legend=False):
    plot_mean_sd(ax, passive, co, key)
    ax.set_ylim(*ylim)
    ax.set_yticks(yticks)
    ax.set_ylabel(ylabel)
    ax.set_xlabel("Time (ms)")
    ax.set_title(title, fontsize=12)
    clean_axes(ax)
    ax.text(0, ylim[0] + 0.04 * (ylim[1] - ylim[0]), "Movement onset",
            rotation=90, va="bottom", ha="right", fontsize=9)
    if legend:
        ax.legend(loc="upper right", frameon=False, fontsize=10)


def make(passive, co, out_dir):
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 3.6))
    plt.subplots_adjust(wspace=0.28, left=0.08, right=0.98, top=0.90, bottom=0.16)
    panel(axes[0], passive, co, "omega", (-8, 2), range(-8, 3, 2),
          "Angular velocity (rad s$^{-1}$)", "Head-Torso Vector Angular Velocity")
    panel(axes[1], passive, co, "alpha", (-600, 200), range(-600, 201, 200),
          "Angular acceleration (rad s$^{-2}$)", "Head-Torso Vector Angular Acceleration",
          legend=True)
    for ax, metric, label in ((axes[0], "peak_omega", "Peak angular velocity\n(rad s$^{-1}$)"),
                              (axes[1], "peak_alpha", "Peak angular acceleration\n(rad s$^{-2}$)")):
        inset = inset_axes(ax, width="42%", height="46%", loc="lower right",
                           bbox_to_anchor=(0, 0.04, 0.98, 1.0), bbox_transform=ax.transAxes)
        inset_boxplot(inset, values(passive, metric), values(co, metric), label)
    save(fig, out_dir, "Figure6_Head_Torso_Vector_Angular_Kinematics")
    plt.close(fig)
