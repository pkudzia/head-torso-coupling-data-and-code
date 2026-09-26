"""Reproduce Tables 2-3 and Figures 2-6 of the paper from the coordinate data.

Usage:
    python run_all.py                 # read data/, write results/
    python run_all.py --out my_results
"""
import argparse
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "analysis"))

import figure2, figure3, figure4, figure5, figure6  # noqa: E402
import tables  # noqa: E402
from processing import DATA_DIR, process_condition  # noqa: E402


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--data", default=DATA_DIR, help="folder with the coordinate CSV files")
    parser.add_argument("--out", default=os.path.join(HERE, "results"), help="output folder")
    args = parser.parse_args()

    passive = process_condition("Passive", args.data)
    co = process_condition("CoContracted", args.data)
    print(f"Processed {len(passive['trials'])} passive and {len(co['trials'])} co-contracted trials")

    os.makedirs(args.out, exist_ok=True)
    table2 = tables.build(tables.TABLE_2, passive, co)
    table3 = tables.build(tables.TABLE_3, passive, co)
    tables.write_csv(table2, os.path.join(args.out, "table2.csv"))
    tables.write_csv(table3, os.path.join(args.out, "table3.csv"))
    tables.print_table("Table 2. Displacement and coupling metrics", table2)
    tables.print_table("Table 3. Peak kinematics", table3)

    figures = os.path.join(args.out, "figures")
    for module in (figure2, figure3, figure4, figure5, figure6):
        module.make(passive, co, figures)
    print(f"\nTables and figures written to {args.out}")


if __name__ == "__main__":
    main()
