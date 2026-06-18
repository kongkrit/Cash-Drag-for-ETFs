# CLAUDE.md — cash-drag-calc

## Project purpose

Ad-hoc analysis folder for calculating ETF cash drag from holdings files.

---

## Source files

### holdings-daily-emea-en-spsa-gy.xlsx
SPDR MSCI ACWI IMI UCITS ETF (SPSA GY) — SSGA daily holdings, as of 17-Jun-2026.

**Download**: [ssga.com SPSA GY product page](https://www.ssga.com/se/en_gb/intermediary/etfs/state-street-spdr-msci-all-country-world-investable-market-ucits-etf-dist-spsa-gy) → Holdings section → Daily Holdings (xlsx)

**Sheet**: `holdings` (single sheet)

**Row layout:**
- Row 1: `Fund Name:` | full name
- Row 2: `ISIN:` | fund ISIN
- Row 3: `Ticker Symbol:` | e.g. `SPSA GY`
- Row 4: `Holdings As Of:` | date string e.g. `17-Jun-2026`
- Row 5: blank
- Row 6: column headers — ISIN, SEDOL, Security Name, Currency, Number of Shares, Percent of Fund, Trade Country Name, Local Price, Sector Classification, Industry Classification, Base Market Value
- Row 7+: holdings, then a legal disclaimer paragraph as the final row

**Row classification (ISIN == "Unassigned"):**
- **Cash** — Security Name contains a currency keyword (Dollar, Yen, Won, Franc, etc.); no `:` in name; no futures keyword
- **FX forward** — Security Name contains `:` (e.g. `CNY:HKD 20250930`)
- **Equity futures** — Security Name contains `EMINI`, `FUTURE`, `SEP2`, `DEC2`, etc.
- **Tiny unclassified equity** — none of the above; numeric Percent of Fund; small BMV

**Key numbers (17 Jun 2026):**
- Total BMV: $7.06B
- Securities: $6.99B (98.97%)
- Net FX cash: $36.5M (0.52%) — USD $38.4M dominant; negative TWD (-$3.1M) and INR (-$1.8M)
- EMINI S&P 500 futures: $36.3M — nearly fully equitizes the cash position
- Gross cash drag: 0.52% | Net cash drag: ~0.00%

**Reader**: `src/readers/xlsx_reader.py`

---

### Holdings_details_Total_World_Stock_ETF.csv
Vanguard Total World Stock ETF (VT) — Vanguard holdings export, as of 05/31/2026.

**Download**: [advisors.vanguard.com VT product page](https://advisors.vanguard.com/investments/products/vt/vanguard-total-world-stock-etf#overview) → Portfolio tab → Export full holdings (csv)

**Sections** (identified by line pattern `SectionName,as of MM/DD/YYYY`):
- `Equity` — ~9,500 equity holdings; columns: SEDOL, HOLDINGS, TICKER, % OF FUNDS*, SUB-INDUSTRY, COUNTRY, SECURITYDEPOSITORYRECEIPTTYPE, MARKET VALUE*, SHARES
- `Fixed income` — empty (VT holds no bonds)
- `Short-term reserves` — columns: SEDOL, HOLDINGS, TICKER, % OF FUNDS*, MARKET VALUE*

**Short-term reserves row classification (use HOLDINGS column, not TICKER — TICKER is `---` for fund positions):**
- `MKTLIQ` → Vanguard Market Liquidity Fund (uninvested cash / MMF)
- `SLBBH*` (e.g. `SLBBH1142`) → securities-lending reinvestment vehicle; has an offsetting liability — excluded from primary cash drag, shown separately
- anything else → FX operational cash balance (settlement cash)

**Key numbers (31 May 2026):**
- Total NAV (sum of all positions): $95.74B
- MKTLIQ: $789.7M (Vanguard reports 0.82% of fund)
- SLBBH1142 (sec-lending collateral): $559.3M
- Net FX balances: $88.7M — dominated by CNH/CNY pair (~$1M net), USD ($40.3M), and 30+ other currencies
- Gross cash drag (MMF + FX): 0.92%
- Gross incl. sec-lending: 1.50%
- Futures not disclosed in this CSV format (Vanguard uses futures for equitization)

**Reader**: `src/readers/csv_reader.py`

---

## Cash drag methodology

```
NAV                   = sum of all position market values in the holdings file
Cash                  = MMF + net FX operational balances
Sec-lending collat.   = reinvested collateral (offsetting liability — excluded from gross drag)
Futures notional      = long equity futures for cash equitization

Gross cash drag       = Cash / NAV × 100
Net cash drag         = (Cash − futures notional) / NAV × 100
```

---

## Source code layout

```
src/
├── __init__.py
├── models.py                 FundSnapshot, CashDragResult
├── readers/
│   ├── __init__.py
│   ├── xlsx_reader.py        SSGA SPDR xlsx → FundSnapshot
│   └── csv_reader.py         Vanguard CSV → FundSnapshot
└── calculators/
    ├── __init__.py
    └── cash_drag.py          FundSnapshot → CashDragResult
main.py                       entry point
requirements.txt              openpyxl
```

Run: `python3 main.py`

---

## Dependencies

- `openpyxl` — read xlsx (`pip install openpyxl`)

## Conventions

- All monetary values are in USD
- Base Market Value in the xlsx is already USD-converted
- Percent of Fund values for equities sum to 100% in the xlsx
- Negative cash positions = FX settlement obligations (e.g. sold a currency, not yet settled)
- SLBBH1142 is an internal Vanguard identifier (~9 chars, not a valid 7-char SEDOL)
