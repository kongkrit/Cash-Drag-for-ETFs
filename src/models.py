from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ReservePosition:
    name: str
    ticker: str
    market_value: float  # USD


@dataclass
class FundSnapshot:
    name: str
    ticker: Optional[str]
    as_of: str
    source_file: str
    # Aggregated values
    equity_market_value: float        # USD — sum of all equity/bond holdings
    total_market_value: float         # USD — equity + all reserves
    mmf_value: float                  # Vanguard Market Liquidity Fund or equivalent MMF
    sec_lending_collateral: float     # reinvested sec-lending collateral (offsetting liability exists)
    fx_balances_net: float            # net of all foreign-currency cash positions
    futures_notional: float           # long equity futures notional (equitization), 0 if none
    reserves: list[ReservePosition] = field(default_factory=list)


@dataclass
class CashDragResult:
    fund_name: str
    ticker: Optional[str]
    as_of: str
    nav: float                          # USD
    mmf_value: float                    # USD
    fx_net: float                       # USD
    sec_lending_value: float            # USD
    futures_notional: float             # USD
    # Gross: MMF + FX net / NAV
    gross_cash_drag_pct: float
    # Gross incl. sec-lending collateral / NAV
    gross_cash_drag_incl_sl_pct: float
    # Net: subtract equity futures equitization
    net_cash_drag_pct: float

    def display(self) -> str:
        nav_b = self.nav / 1e9
        lines = [
            f"{self.fund_name} ({self.ticker})  —  {self.as_of}",
            f"  NAV                         ${nav_b:>10,.2f}B",
            f"  Money market fund (MMF)     ${self.mmf_value/1e6:>10,.1f}M",
            f"  Net FX cash balances        ${self.fx_net/1e6:>10,.1f}M",
            f"  Sec. lending collateral     ${self.sec_lending_value/1e6:>10,.1f}M",
        ]
        if self.futures_notional:
            lines.append(f"  Equity futures (long)       ${self.futures_notional/1e6:>10,.1f}M")
        lines += [
            f"",
            f"  Gross cash drag (MMF+FX)    {self.gross_cash_drag_pct:>10.4f}%",
            f"  Gross incl. sec. lending    {self.gross_cash_drag_incl_sl_pct:>10.4f}%",
        ]
        if self.futures_notional:
            lines.append(f"  Net cash drag (post-futures){self.net_cash_drag_pct:>10.4f}%")
        return "\n".join(lines)
