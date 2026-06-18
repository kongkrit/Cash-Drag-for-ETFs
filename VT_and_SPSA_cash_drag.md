# Cash Drag Calculator

Calculates ETF cash drag from daily holdings files.

## What is Cash Drag?

Cash drag is the performance penalty from holding uninvested cash instead of equities:

```
Gross cash drag  = (MMF + net FX balances) / NAV × 100
Net cash drag    = (MMF + net FX − equity futures notional) / NAV × 100
```

Funds often use **cash equitization** — holding long equity index futures to synthetically invest idle cash — which reduces or eliminates net cash drag.

---

## Results

### SPDR MSCI ACWI IMI UCITS ETF (SPSA GY) — 17 Jun 2026

Source: `holdings-daily-emea-en-spsa-gy.xlsx` (SSGA daily holdings)

| Metric | Value |
|---|---|
| NAV | $7.06B |
| Net FX cash balances | $36.5M |
| Equity futures (EMINI S&P SEP26) | $36.3M |
| **Gross cash drag** | **0.52%** |
| **Net cash drag (post-futures)** | **~0.00%** |

The $36.5M cash position (dominated by $38.4M USD, offset by negative TWD and INR) is almost entirely equitized by a near-identical EMINI S&P 500 futures position.

---

### Vanguard Total World Stock ETF (VT) — 31 May 2026

Source: `Holdings_details_Total_World_Stock_ETF.csv` (Vanguard holdings export)

| Metric | Value |
|---|---|
| NAV | $95.74B |
| Vanguard Market Liquidity Fund (MKTLIQ) | $789.7M |
| Net FX cash balances | $88.7M |
| Sec. lending collateral (SLBBH1142) | $559.3M |
| **Gross cash drag (MMF + FX)** | **0.92%** |
| **Gross cash drag (incl. sec. lending)** | **1.50%** |
| Net cash drag (post-futures) | N/A — futures not disclosed in CSV |

**Notes:**
- Vanguard's own reported figure for MKTLIQ is **0.82%** of fund assets — the pure uninvested cash component. The calculated 0.92% adds the $88.7M net FX operational balances (settlement cash from global equity transactions).
- The $559.3M SLBBH1142 position is securities-lending reinvestment collateral; it carries an offsetting liability and is excluded from the primary gross cash drag figure.
- The CSV does not expose equity futures. Vanguard does use index futures for cash equitization, so true net cash drag is lower than the gross figure shown.
- The large CNH (+$257M) / CNY (−$256M) pair nearly cancels; net contribution to FX cash is ~$1M.
