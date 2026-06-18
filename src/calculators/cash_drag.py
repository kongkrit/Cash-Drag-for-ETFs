"""
Cash drag calculator.

Definitions
-----------
NAV                  = total_market_value (sum of all positions in the holdings file)
Cash                 = MMF + net FX cash balances (uninvested cash, settleable to equities)
Sec. lending coll.   = reinvested securities-lending collateral (has offsetting liability —
                       excluded from gross drag but shown separately)
Futures notional     = long equity futures used for cash equitization

Gross cash drag      = Cash / NAV
                       The drag before accounting for synthetic equity exposure.

Net cash drag        = (Cash − futures notional) / NAV
                       Negative means the fund is *over-equitized* via futures.
                       Only meaningful when futures_notional > 0.
"""

from ..models import CashDragResult, FundSnapshot


def compute(snapshot: FundSnapshot) -> CashDragResult:
    nav = snapshot.total_market_value
    if nav == 0:
        raise ValueError(f"NAV is zero for {snapshot.name!r}")

    cash = snapshot.mmf_value + snapshot.fx_balances_net
    cash_incl_sl = cash + snapshot.sec_lending_collateral

    gross_pct = cash / nav * 100
    gross_incl_sl_pct = cash_incl_sl / nav * 100
    net_pct = (cash - snapshot.futures_notional) / nav * 100

    return CashDragResult(
        fund_name=snapshot.name,
        ticker=snapshot.ticker,
        as_of=snapshot.as_of,
        nav=nav,
        mmf_value=snapshot.mmf_value,
        fx_net=snapshot.fx_balances_net,
        sec_lending_value=snapshot.sec_lending_collateral,
        futures_notional=snapshot.futures_notional,
        gross_cash_drag_pct=gross_pct,
        gross_cash_drag_incl_sl_pct=gross_incl_sl_pct,
        net_cash_drag_pct=net_pct,
    )
