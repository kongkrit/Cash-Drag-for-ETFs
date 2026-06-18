"""
Reader for Vanguard holdings CSV export.

File format (as exported from Vanguard):
  Row 1  : blank / BOM
  Row 2  : "Holdings details"
  Row 3  : "Total World Stock ETF (VT)"
  Row 4-5: blank
  Row 6  : "Equity,as of MM/DD/YYYY"
  Row 7  : blank
  Row 8  : column header for equity section
  ...    : equity data rows (comma-separated, SEDOL is col 1, market value is quoted "$NNN")
  ...    : "Fixed income,as of MM/DD/YYYY" section (may be empty)
  ...    : "Short-term reserves,as of MM/DD/YYYY" section
  ...    : legal disclaimers

Short-term reserves tickers:
  MKTLIQ    — Vanguard Market Liquidity Fund (uninvested cash / MMF)
  SLBBH*    — securities-lending reinvestment vehicle (has offsetting liability)
  currency  — FX operational balances (e.g. "US Dollar", "Japanese Yen")
"""

import csv
import re
from io import StringIO
from typing import Optional

from ..models import FundSnapshot, ReservePosition

# Tickers that represent securities-lending reinvestment (not pure uninvested cash)
_SEC_LENDING_PREFIXES = ("SLBBH",)

# Market Liquidity Fund ticker used by Vanguard
_MMF_TICKER = "MKTLIQ"


def _parse_dollar(raw: str) -> float:
    """Convert '$1,234,567.89' or '-$256,005,248.60' to float."""
    cleaned = raw.strip().replace("$", "").replace(",", "")
    return float(cleaned) if cleaned and cleaned not in ("-", "") else 0.0


def _is_sec_lending(ticker: str) -> bool:
    return any(ticker.upper().startswith(p) for p in _SEC_LENDING_PREFIXES)


def read(path: str) -> FundSnapshot:
    with open(path, encoding="utf-8-sig") as f:
        raw = f.read()

    lines = raw.splitlines()

    # --- Extract fund metadata ---
    fund_name = "Unknown"
    ticker: Optional[str] = None
    as_of = "Unknown"

    for line in lines[:10]:
        m = re.match(r"^(.+?)\s+\(([A-Z]+)\)\s*$", line.strip())
        if m:
            fund_name = m.group(1).strip()
            ticker = m.group(2)

    # --- Locate sections ---
    equity_start = fixed_start = reserves_start = None
    equity_date = reserves_date = None

    for i, line in enumerate(lines):
        m_eq = re.match(r"^Equity,as of (\d{2}/\d{2}/\d{4})", line)
        m_fi = re.match(r"^Fixed income,as of", line)
        m_rs = re.match(r"^Short-term reserves,as of (\d{2}/\d{2}/\d{4})", line)
        if m_eq:
            equity_start = i
            equity_date = m_eq.group(1)
        if m_fi:
            fixed_start = i
        if m_rs:
            reserves_start = i
            reserves_date = m_rs.group(1)

    as_of = equity_date or reserves_date or "Unknown"

    # --- Parse equity section ---
    equity_end = fixed_start if fixed_start else (reserves_start if reserves_start else len(lines))
    equity_mv = 0.0

    if equity_start is not None:
        # Header row is 2 lines after section label
        header_idx = None
        for i in range(equity_start, equity_end):
            if lines[i].startswith(",SEDOL,"):
                header_idx = i
                break
        if header_idx is not None:
            reader = csv.reader(StringIO("\n".join(lines[header_idx : equity_end])))
            headers = [h.strip() for h in next(reader)]
            mv_col = next(
                (j for j, h in enumerate(headers) if "MARKET VALUE" in h.upper()), None
            )
            if mv_col is not None:
                for row in reader:
                    if len(row) > mv_col and row[mv_col].strip().startswith("$"):
                        equity_mv += _parse_dollar(row[mv_col])

    # --- Parse short-term reserves ---
    reserves: list[ReservePosition] = []
    mmf_value = 0.0
    sec_lending_collateral = 0.0
    fx_balances: list[float] = []

    if reserves_start is not None:
        header_idx = None
        for i in range(reserves_start, len(lines)):
            if lines[i].startswith(",SEDOL,"):
                header_idx = i
                break
        if header_idx is not None:
            reader = csv.reader(StringIO("\n".join(lines[header_idx:])))
            headers = [h.strip() for h in next(reader)]
            name_col = next(
                (j for j, h in enumerate(headers) if h.upper() == "HOLDINGS"), None
            )
            ticker_col = next(
                (j for j, h in enumerate(headers) if h.upper() == "TICKER"), None
            )
            mv_col = next(
                (j for j, h in enumerate(headers) if "MARKET VALUE" in h.upper()), None
            )
            for row in reader:
                if not any(row):
                    continue
                if len(row) <= max(filter(None, [name_col, ticker_col, mv_col])):
                    continue
                name = row[name_col].strip() if name_col is not None else ""
                tkr = row[ticker_col].strip() if ticker_col is not None else ""
                raw_mv = row[mv_col].strip() if mv_col is not None else ""

                if not raw_mv or not raw_mv.startswith(("$", "-$")):
                    continue

                mv = _parse_dollar(raw_mv)
                reserves.append(ReservePosition(name=name, ticker=tkr, market_value=mv))

                # Classify by HOLDINGS column (name), not TICKER — in the reserves
                # section TICKER is "---" for funds; the meaningful id is in HOLDINGS.
                holdings_id = name
                if holdings_id == _MMF_TICKER:
                    mmf_value += mv
                elif _is_sec_lending(holdings_id):
                    sec_lending_collateral += mv
                else:
                    fx_balances.append(mv)

    fx_balances_net = sum(fx_balances)
    total_reserves_mv = sum(r.market_value for r in reserves)
    total_market_value = equity_mv + total_reserves_mv

    return FundSnapshot(
        name=fund_name,
        ticker=ticker,
        as_of=as_of,
        source_file=path,
        equity_market_value=equity_mv,
        total_market_value=total_market_value,
        mmf_value=mmf_value,
        sec_lending_collateral=sec_lending_collateral,
        fx_balances_net=fx_balances_net,
        futures_notional=0.0,  # VT CSV does not expose futures separately
        reserves=reserves,
    )
