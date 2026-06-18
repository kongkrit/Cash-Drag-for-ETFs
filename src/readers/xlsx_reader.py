"""
Reader for SSGA (State Street) SPDR daily holdings XLSX.

File format:
  Row 1  : "Fund Name:" | full name
  Row 2  : "ISIN:"      | fund ISIN
  Row 3  : "Ticker Symbol:" | ticker
  Row 4  : "Holdings As Of:" | date string (e.g. "17-Jun-2026")
  Row 5  : blank
  Row 6  : column headers
  Row 7+ : holdings data

Holdings columns (0-indexed):
  0 ISIN  1 SEDOL  2 Security Name  3 Currency  4 Shares
  5 Percent of Fund  6 Country  7 Local Price  8 Sector
  9 Industry  10 Base Market Value (USD)

Row classification for ISIN == "Unassigned":
  Cash     — Security Name contains a currency keyword, no ":" (FX fwd), no futures keyword
  Futures  — Security Name contains EMINI / FUTURE / expiry month codes
  FX fwd   — Security Name contains ":" (e.g. "CNY:HKD 20250930")
"""

import re
from typing import Optional

import openpyxl

from ..models import FundSnapshot, ReservePosition

_CURRENCY_KEYWORDS = {
    "Dollar", "Real", "Pound", "Franc", "Yen", "Won", "Euro", "Rupee",
    "Peso", "Lira", "Krona", "Krone", "Ringgit", "Baht", "Rupiah",
    "Shekel", "Dirham", "Riyal", "Dinar", "Koruna", "Forint", "Zloty",
    "Rand", "Renminbi", "CNH", "STIF", "Deposit",
}

_FUTURES_KEYWORDS = {"EMINI", "FUTURE", "SEP2", "DEC2", "MAR2", "JUN2"}


def _is_cash_row(name: str) -> bool:
    has_currency = any(kw in name for kw in _CURRENCY_KEYWORDS)
    has_colon = ":" in name  # FX forward e.g. "CNY:HKD 20250930"
    has_futures = any(kw in name.upper() for kw in _FUTURES_KEYWORDS)
    return has_currency and not has_colon and not has_futures


def _is_futures_row(name: str) -> bool:
    return any(kw in name.upper() for kw in _FUTURES_KEYWORDS)


def read(path: str) -> FundSnapshot:
    wb = openpyxl.load_workbook(path, read_only=True)
    ws = wb.active
    rows = list(ws.iter_rows(values_only=True))

    # Metadata rows (0-indexed)
    fund_name: str = str(rows[0][1]) if rows[0][1] else "Unknown"
    ticker_raw: str = str(rows[2][1]) if rows[2][1] else ""
    # Ticker cell is e.g. "SPSA GY" — keep as-is
    ticker: Optional[str] = ticker_raw.strip() or None
    as_of: str = str(rows[3][1]) if rows[3][1] else "Unknown"

    data_rows = rows[6:]  # skip 5 metadata + 1 header

    equity_mv = 0.0
    mmf_value = 0.0
    futures_notional = 0.0
    fx_forward_mv = 0.0
    cash_positions: list[ReservePosition] = []

    for row in data_rows:
        if row[0] is None or row[10] is None:
            continue
        bmv = row[10]
        if not isinstance(bmv, (int, float)):
            continue

        isin = str(row[0])
        name = str(row[2]) if row[2] else ""

        if isin != "Unassigned":
            equity_mv += bmv
        else:
            if ":" in name:
                fx_forward_mv += bmv
            elif _is_futures_row(name):
                futures_notional += bmv
            elif _is_cash_row(name):
                cash_positions.append(
                    ReservePosition(name=name, ticker=str(row[3]) if row[3] else "", market_value=bmv)
                )
            # else: tiny unclassified equity — counted in equity_mv via total

    fx_balances_net = sum(p.market_value for p in cash_positions)
    total_market_value = equity_mv + fx_balances_net + futures_notional + fx_forward_mv

    return FundSnapshot(
        name=fund_name,
        ticker=ticker,
        as_of=as_of,
        source_file=path,
        equity_market_value=equity_mv,
        total_market_value=total_market_value,
        mmf_value=0.0,                          # SSGA file has no dedicated MMF line
        sec_lending_collateral=0.0,
        fx_balances_net=fx_balances_net,
        futures_notional=futures_notional,
        reserves=cash_positions,
    )
