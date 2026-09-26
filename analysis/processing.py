"""Load the tracked head and torso coordinates and compute the kinematic outcomes.

Each trial is processed in the same order as described in the paper's Methods:

1. Fill short gaps in the digitized coordinates by linear interpolation.
2. Low-pass filter positions (4th-order Butterworth, 50 Hz, zero phase).
3. Differentiate to velocity and acceleration (central differences).
4. Define movement onset (t = 0) as the first frame where head resultant
   velocity reaches 30 cm/s.
5. Compute head and torso displacement from their onset positions, head
   excursion relative to the torso, and the angular velocity and acceleration
   of the line joining the two tracking points.
6. Resample every signal onto a common 1 ms grid from -50 to 500 ms and
   extract peak values, peak times, and values at 100 and 200 ms.
"""
import os

import numpy as np
from scipy.interpolate import interp1d
from scipy.signal import butter, filtfilt

G = 980.665                # cm/s^2, standard gravity
ONSET_VELOCITY = 30.0      # cm/s, head velocity that defines movement onset
CUTOFF_HZ = 50.0           # low-pass cutoff for positions and angular signals
SMOOTH_SAMPLES = 3         # moving-average width applied to resultant acceleration
WINDOW_S = (-0.05, 0.50)   # analysis window relative to onset
PATH_WINDOW_MS = 500       # path length is summed over this period after onset
TIME = np.arange(WINDOW_S[0], WINDOW_S[1] + 1e-9, 0.001)  # common grid, 551 points

CONDITIONS = ("Passive", "CoContracted")
PARTICIPANTS = [f"P{i:02d}" for i in range(1, 20)]
DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "data")


# ---------------------------------------------------------------- loading

def load_trial(participant, condition, data_dir=DATA_DIR):
    """Return one trial as a dict of 1-D arrays, or None if the file is absent."""
    path = os.path.join(data_dir, f"{participant}_{condition}.csv")
    if not os.path.exists(path):
        return None
    t, torso_x, torso_y, head_x, head_y = np.loadtxt(path, delimiter=",", skiprows=1).T
    return {"t": t, "torso_x": torso_x, "torso_y": torso_y, "head_x": head_x, "head_y": head_y}


# ---------------------------------------------------------------- signal helpers

def fill_gaps(values, t):
    """Linearly interpolate missing samples (NaN), extrapolating at the ends."""
    ok = np.isfinite(values)
    if ok.sum() < 2:
        return np.zeros_like(values)
    return interp1d(t[ok], values[ok], kind="linear", fill_value="extrapolate")(t)


def lowpass(values, order, fs):
    b, a = butter(order, CUTOFF_HZ / (fs / 2), btype="low")
    return filtfilt(b, a, values)


def moving_average(values, width):
    """Centered moving average; the window shrinks at the ends of the signal."""
    n = len(values)
    lo, hi = (width - 1) // 2, width // 2
    return np.array([values[max(0, i - lo):min(n, i + hi + 1)].mean() for i in range(n)])


def to_common_time(t_rel, values):
    return interp1d(t_rel, values, kind="linear", fill_value="extrapolate")(TIME)


# ---------------------------------------------------------------- one trial

def process_trial(trial):
    """Compute waveforms and outcome measures for one trial.

    Returns a dict with:
      waveforms   signals on the common time grid (keys listed in WAVEFORMS)
      metrics     scalar outcomes used in Tables 2 and 3
      trajectory  filtered head and torso paths from onset (for Figure 2),
                  shifted so the torso starts at the origin
    """
    t = trial["t"]
    dt = np.mean(np.diff(t))
    fs = 1.0 / dt

    head_x, head_y, torso_x, torso_y = (
        lowpass(fill_gaps(trial[k], t), 4, fs) for k in ("head_x", "head_y", "torso_x", "torso_y"))

    head_vx, head_vy = np.gradient(head_x, dt), np.gradient(head_y, dt)
    torso_vx, torso_vy = np.gradient(torso_x, dt), np.gradient(torso_y, dt)
    head_speed = np.hypot(head_vx, head_vy)

    moving = head_speed >= ONSET_VELOCITY
    if not moving.any():
        return None
    onset = int(np.argmax(moving))
    if len(t) - 1 - onset < 10:
        return None

    # Linear kinematics (displacement is measured from the onset position)
    head_disp = np.hypot(head_x - head_x[onset], head_y - head_y[onset])
    torso_disp = np.hypot(torso_x - torso_x[onset], torso_y - torso_y[onset])
    torso_speed = np.hypot(torso_vx, torso_vy)
    head_acc = np.hypot(np.gradient(head_vx, dt), np.gradient(head_vy, dt)) / G
    torso_acc = np.hypot(np.gradient(torso_vx, dt), np.gradient(torso_vy, dt)) / G
    head_acc = moving_average(head_acc, SMOOTH_SAMPLES)
    torso_acc = moving_average(torso_acc, SMOOTH_SAMPLES)

    # Head position relative to the torso, r = head - torso
    rx, ry = head_x - torso_x, head_y - torso_y
    excursion = np.hypot(rx - rx[onset], ry - ry[onset])

    # Angular velocity of r, using the relative velocity of head and torso
    vx_rel, vy_rel = head_vx - torso_vx, head_vy - torso_vy
    omega = (rx * vy_rel - ry * vx_rel) / (rx ** 2 + ry ** 2 + np.finfo(float).eps)
    alpha = np.gradient(omega, dt)
    omega, alpha = lowpass(omega, 2, fs), lowpass(alpha, 2, fs)

    # Resample onto the common time grid (-50 to 500 ms around onset)
    half = round(WINDOW_S[1] / dt)
    start, end = max(0, onset - half), min(len(t) - 1, onset + half)
    t_rel = t[start:end + 1] - t[onset]
    keep = (t_rel >= WINDOW_S[0]) & (t_rel <= WINDOW_S[1])
    if keep.sum() < 10:
        return None

    def resample(values):
        return to_common_time(t_rel[keep], values[start:end + 1][keep])

    w = {
        "head_disp": resample(head_disp), "head_vel": resample(head_speed),
        "head_acc": resample(head_acc),
        "torso_disp": resample(torso_disp), "torso_vel": resample(torso_speed),
        "torso_acc": resample(torso_acc),
        "excursion": resample(excursion),
        "rel_x": resample(rx - rx[onset]), "rel_y": resample(ry - ry[onset]),
        "omega": resample(omega), "alpha": resample(alpha),
    }

    # Outcome measures from the resampled signals
    peak = {k: int(np.argmax(w[k])) for k in
            ("head_disp", "head_vel", "head_acc", "torso_disp", "torso_vel", "torso_acc", "excursion")}
    at_100, at_200 = int(np.argmax(TIME >= 0.1)), int(np.argmax(TIME >= 0.2))
    ms = TIME * 1000.0

    m = {
        "head_peak_disp": w["head_disp"][peak["head_disp"]],
        "head_time_to_peak_disp": ms[peak["head_disp"]],
        "head_disp_100ms": w["head_disp"][at_100],
        "head_disp_200ms": w["head_disp"][at_200],
        "torso_peak_disp": w["torso_disp"][peak["torso_disp"]],
        "torso_time_to_peak_disp": ms[peak["torso_disp"]],
        "torso_disp_100ms": w["torso_disp"][at_100],
        "torso_disp_200ms": w["torso_disp"][at_200],
        "excursion_peak": w["excursion"][peak["excursion"]],
        "excursion_time_to_peak": ms[peak["excursion"]],
        "excursion_100ms": w["excursion"][at_100],
        "excursion_200ms": w["excursion"][at_200],
        # time lag = time of head peak minus time of torso peak (1 ms grid)
        "lag_disp": float(peak["head_disp"] - peak["torso_disp"]),
        "lag_vel": float(peak["head_vel"] - peak["torso_vel"]),
        "lag_acc": float(peak["head_acc"] - peak["torso_acc"]),
        "head_peak_vel": w["head_vel"][peak["head_vel"]],
        "head_peak_acc": w["head_acc"][peak["head_acc"]],
        "torso_peak_vel": w["torso_vel"][peak["torso_vel"]],
        "torso_peak_acc": w["torso_acc"][peak["torso_acc"]],
        "peak_omega": float(np.max(np.abs(w["omega"]))),
        "peak_alpha": float(np.max(np.abs(w["alpha"]))),
    }

    # Path length over the first 500 ms after onset, from the filtered positions
    n_path = min(round(PATH_WINDOW_MS / (dt * 1000)), len(t) - 1 - onset)
    if n_path > 10:
        seg = slice(onset, onset + n_path + 1)
        m["head_path_length"] = float(np.hypot(np.diff(head_x[seg]), np.diff(head_y[seg])).sum())
        m["torso_path_length"] = float(np.hypot(np.diff(torso_x[seg]), np.diff(torso_y[seg])).sum())

    seg = slice(onset, onset + max(n_path, 1) + 1)
    trajectory = {
        "head_x": head_x[seg] - torso_x[onset], "head_y": head_y[seg] - torso_y[onset],
        "torso_x": torso_x[seg] - torso_x[onset], "torso_y": torso_y[seg] - torso_y[onset],
    }
    return {"waveforms": w, "metrics": {k: float(v) for k, v in m.items()}, "trajectory": trajectory}


# ---------------------------------------------------------------- one condition

WAVEFORMS = ("head_disp", "head_vel", "head_acc", "torso_disp", "torso_vel", "torso_acc",
             "excursion", "omega", "alpha")


def process_condition(condition, data_dir=DATA_DIR):
    """Process every participant for one condition.

    Returns a dict with per-participant results ("trials"), and the mean and
    standard deviation of each waveform across participants.
    """
    trials = {}
    for p in PARTICIPANTS:
        trial = load_trial(p, condition, data_dir)
        result = process_trial(trial) if trial is not None else None
        if result is not None:
            trials[p] = result
    stack = {k: np.vstack([r["waveforms"][k] for r in trials.values()]) for k in WAVEFORMS}
    return {
        "condition": condition,
        "time": TIME,
        "trials": trials,
        "mean": {k: np.nanmean(v, axis=0) for k, v in stack.items()},
        "sd": {k: np.nanstd(v, axis=0, ddof=1) for k, v in stack.items()},
    }


def values(condition_result, metric):
    """One metric for every participant, in participant order."""
    return np.array([r["metrics"][metric] for r in condition_result["trials"].values()])
