"""Paired comparisons and the rows of Tables 2 and 3.

Every outcome is compared between conditions with a two-sided paired t-test.
Effect size is Cohen's d for paired data (mean difference divided by the SD of
the differences). Percent change is (co-contracted - passive) / |passive|.
"""
import csv

import numpy as np
from scipy import stats

from processing import values

# (section, row label, metric, decimals) in the order they appear in the paper
TABLE_2 = [
    ("Head path", "Peak displacement (cm)", "head_peak_disp", 2),
    ("Head path", "Time to peak displacement (ms)", "head_time_to_peak_disp", 0),
    ("Head path", "Displacement at 100 ms (cm)", "head_disp_100ms", 2),
    ("Head path", "Displacement at 200 ms (cm)", "head_disp_200ms", 2),
    ("Head path", "Path length (cm)", "head_path_length", 2),
    ("Torso path", "Peak displacement (cm)", "torso_peak_disp", 2),
    ("Torso path", "Time to peak displacement (ms)", "torso_time_to_peak_disp", 0),
    ("Torso path", "Displacement at 100 ms (cm)", "torso_disp_100ms", 2),
    ("Torso path", "Displacement at 200 ms (cm)", "torso_disp_200ms", 2),
    ("Torso path", "Path length (cm)", "torso_path_length", 2),
    ("Head excursion relative to the torso", "Peak (cm)", "excursion_peak", 2),
    ("Head excursion relative to the torso", "At 100 ms (cm)", "excursion_100ms", 2),
    ("Head excursion relative to the torso", "At 200 ms (cm)", "excursion_200ms", 2),
    ("Time lag between head and torso peaks", "Displacement (ms)", "lag_disp", 1),
    ("Time lag between head and torso peaks", "Velocity (ms)", "lag_vel", 1),
]

TABLE_3 = [
    ("Head", "Peak velocity (cm/s)", "head_peak_vel", 1),
    ("Head", "Peak acceleration (g)", "head_peak_acc", 2),
    ("Head", "Peak vector angular velocity (rad/s)", "peak_omega", 2),
    ("Head", "Peak vector angular acceleration (rad/s^2)", "peak_alpha", 0),
    ("Torso", "Peak velocity (cm/s)", "torso_peak_vel", 1),
    ("Torso", "Peak acceleration (g)", "torso_peak_acc", 2),
]


def describe(x):
    """Mean, SD, and 95% confidence interval of the mean."""
    n = len(x)
    mean, sd = x.mean(), x.std(ddof=1)
    half = stats.t.ppf(0.975, n - 1) * sd / np.sqrt(n)
    return mean, sd, mean - half, mean + half


def compare(passive, co):
    """Paired comparison of one outcome between conditions."""
    diff = co - passive
    return {
        "passive": describe(passive),
        "co": describe(co),
        "pct_change": (co.mean() - passive.mean()) / abs(passive.mean()) * 100.0,
        "p": stats.ttest_rel(co, passive).pvalue,
        "d": diff.mean() / diff.std(ddof=1),
    }


def format_p(p):
    return "<0.001" if p < 0.001 else f"{p:.3f}"


def format_group(summary, decimals):
    mean, sd, lo, hi = summary
    f = f"{{:.{decimals}f}}"
    return f"{f.format(mean)} ± {f.format(sd)} [{f.format(lo)}, {f.format(hi)}]"


def build(rows, passive, co):
    """Return table rows as dicts with both formatted text and raw numbers."""
    out = []
    for section, label, metric, decimals in rows:
        c = compare(values(passive, metric), values(co, metric))
        out.append({
            "section": section, "parameter": label, "metric": metric,
            "passive": format_group(c["passive"], decimals),
            "co_contracted": format_group(c["co"], decimals),
            "pct_change": f"{c['pct_change']:.1f}%",
            "p": format_p(c["p"]),
            "d": f"{c['d']:.2f}",
            "passive_mean": c["passive"][0], "co_contracted_mean": c["co"][0],
            "p_value": c["p"], "cohens_d": c["d"],
        })
    return out


def write_csv(table, path):
    with open(path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=list(table[0]))
        writer.writeheader()
        writer.writerows(table)


def print_table(title, table):
    print(f"\n{title}")
    section = None
    for row in table:
        if row["section"] != section:
            section = row["section"]
            print(f"  {section}")
        print(f"    {row['parameter']:<42} {row['passive']:<30} {row['co_contracted']:<30} "
              f"{row['pct_change']:>7}  p = {row['p']:<6}  d = {row['d']}")
