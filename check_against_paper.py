"""Check that a fresh run reproduces the values printed in Tables 2 and 3.

Run `python run_all.py` first, then `python check_against_paper.py`.
The published values are stored in reference/paper_table2.csv and
reference/paper_table3.csv.
"""
import csv
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
COLUMNS = ("passive", "co_contracted", "pct_change", "p", "d")


def read(path):
    with open(path, newline="") as f:
        return {row["metric"]: row for row in csv.DictReader(f)}


def main():
    mismatches = 0
    for table in ("table2", "table3"):
        paper = read(os.path.join(HERE, "reference", f"paper_{table}.csv"))
        result = read(os.path.join(HERE, "results", f"{table}.csv"))
        for metric, expected in paper.items():
            for col in COLUMNS:
                if result[metric][col] != expected[col]:
                    mismatches += 1
                    print(f"{table} {expected['parameter']} [{col}]: "
                          f"paper {expected[col]}, this run {result[metric][col]}")
        print(f"{table}: {len(paper)} rows checked")
    if mismatches:
        print(f"{mismatches} values differ from the paper")
        sys.exit(1)
    print("All table values match the paper.")


if __name__ == "__main__":
    main()
