"""
Cash drag calculator — entry point.

Usage:
    python main.py

Reads all data files in the current directory and prints cash drag results.
"""

import os
import sys

from src.calculators.cash_drag import compute
from src.readers import csv_reader, xlsx_reader

DATA_DIR = os.path.dirname(__file__)

FILES = {
    "spsa": os.path.join(DATA_DIR, "holdings-daily-emea-en-spsa-gy.xlsx"),
    "vt":   os.path.join(DATA_DIR, "Holdings_details_Total_World_Stock_ETF.csv"),
}


def run():
    results = []

    # SPSA — SSGA SPDR MSCI ACWI IMI UCITS ETF (xlsx)
    spsa_path = FILES["spsa"]
    if os.path.exists(spsa_path):
        snapshot = xlsx_reader.read(spsa_path)
        results.append(compute(snapshot))
    else:
        print(f"[warn] not found: {spsa_path}", file=sys.stderr)

    # VT — Vanguard Total World Stock ETF (csv)
    vt_path = FILES["vt"]
    if os.path.exists(vt_path):
        snapshot = csv_reader.read(vt_path)
        results.append(compute(snapshot))
    else:
        print(f"[warn] not found: {vt_path}", file=sys.stderr)

    for result in results:
        print()
        print(result.display())
        print()


if __name__ == "__main__":
    run()
