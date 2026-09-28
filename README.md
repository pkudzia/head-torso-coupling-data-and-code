# Head-torso coupling during lateral head impacts

De-identified coordinate data and Python code to reproduce Tables 2–3 and Figures 2–6 for the manuscript below.

> Kudzia P, Booth GR, Reynier K, Panzer M, Cripton PA. *Video-based analysis of head-torso coupling during lateral impacts under passive and co-contracted conditions.* Annals of Biomedical Engineering (under review).

[Read the paper (author-hosted PDF)](https://pawelkudzia.com/files/papers/2025_TorsoCoupling_JBiomechEng.pdf). This is an earlier manuscript version; the code and reference tables here reflect the September 2026 revision.

We analyzed high-speed footage (500 Hz) from [Reynier et al. (2020)](https://doi.org/10.1007/s10439-020-02609-7). We tracked one point on the head and one on the upper torso in 19 male volunteers during controlled lateral head impacts (3.7 kg padded impactor, 2.0 m/s) under passive and bilateral co-contracted neck muscle conditions.

## Quick start

Clone the repository and run these commands from its root directory. Python 3.14.6 with NumPy 2.5.3, SciPy 1.18.1, and Matplotlib 3.11.2 was tested on macOS. Other environments have not been verified.

```sh
git clone https://github.com/pkudzia/head-torso-coupling-data-and-code.git
cd head-torso-coupling-data-and-code
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_all.py
python check_against_paper.py
```

On Windows, create the environment with `python -m venv .venv` and activate it with `.venv\Scripts\Activate.ps1` in PowerShell.

A full run processes 19 passive and 19 co-contracted trials. It writes `results/table2.csv`, `results/table3.csv`, and Figures 2–6 in PNG, PDF, EPS, and TIFF formats under `results/figures/`. Generated results are excluded from Git.

The check compares 105 formatted values across 21 rows with the manuscript reference tables in [`reference/`](reference/). A successful run ends with `All table values match the paper.` This checks numerical reproduction, not the accuracy of the original digitization. Use the default output folder before running the check.

For a custom output folder, run `python run_all.py --out my_results`. On a machine without a display, set `MPLBACKEND=Agg`.

## Folder layout

| Path | Contents |
|---|---|
| [`data/`](data/) | 38 de-identified coordinate files, one per participant and condition (`P01_Passive.csv` ... `P19_CoContracted.csv`) |
| [`analysis/processing.py`](analysis/processing.py) | Loading, filtering, movement onset, kinematics, and outcome measures |
| [`analysis/tables.py`](analysis/tables.py) | Paired comparisons and the rows of Tables 2 and 3 |
| [`analysis/plotting.py`](analysis/plotting.py) | Shared figure style and the inset boxplots |
| `analysis/figure2.py` ... `figure6.py` | One script per paper figure |
| [`run_all.py`](run_all.py) | Runs the full analysis |
| [`check_against_paper.py`](check_against_paper.py) | Compares a run with the manuscript reference tables |
| [`reference/`](reference/) | Expected Table 2 and Table 3 values from the September 2026 revision |

## Data format

The 38 CSVs contain paired trials for 19 participants. Match conditions by the participant label in each filename. Each CSV has a header row and five columns, sampled at 500 Hz.

| Column | Unit | Meaning |
|---|---|---|
| `time_s` | s | Time from the start of the recording |
| `torso_x_cm`, `torso_y_cm` | cm | Torso tracking point |
| `head_x_cm`, `head_y_cm` | cm | Head tracking point (dot on the protective cap) |

Coordinates are in the frontal plane: x is medial-lateral (impact direction) and y is superior-inferior (positive up). `NaN` marks frames where a point was not digitized; the analysis fills these gaps by linear interpolation.

**De-identification.** Participants are labelled P01-P19, as in the paper figures; original study identifiers are not included. Each trial is shifted so that the first digitized torso position is the origin, which removes absolute image position. This translation preserves the position differences used by the analysis. No video, images, or demographic data are included.

## Analysis summary

1. Gaps are filled by linear interpolation, then positions are low-pass filtered (4th-order Butterworth, 50 Hz, zero phase).
2. Velocity and acceleration come from central differences; resultant acceleration is smoothed with a 3-sample moving average.
3. Movement onset (t = 0) is the first frame where head resultant velocity reaches 30 cm/s. It is a velocity reference, not a direct measurement of impactor contact.
4. Displacement is measured from each point's onset position. Head-torso relative excursion is the change in the head-minus-torso position vector from onset.
5. Angular velocity is that of the head-minus-torso vector, computed from the relative position and relative velocity of the two points; it describes rotation of the line joining them, not anatomical head rotation. Angular signals are filtered with a 2nd-order Butterworth (50 Hz, zero phase).
6. All signals are resampled to a 1 ms grid from -50 to 500 ms. Peaks, peak times, values at 100 and 200 ms, and head-torso time lags (head peak time minus torso peak time) are taken from this grid. Path length is summed over the first 500 ms after onset.
7. Conditions are compared with two-sided paired t-tests; Cohen's d is the mean paired difference divided by the SD of the differences.

Torso tracking points were visible anatomical or clothing landmarks and were not standardized between participants, and tracking repeatability was not quantified. See the paper for limitations.

## Citation and licenses

Please cite the manuscript above and [Reynier et al. (2020)](https://doi.org/10.1007/s10439-020-02609-7) when using this repository. The manuscript is under review; the reference CSVs describe the September 2026 revision.

Code: [MIT License](LICENSE). Data in `data/`: [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).
