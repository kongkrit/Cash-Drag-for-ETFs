# Cash Drag for ETFs

Calculates ETF cash drag from daily holdings files. See [VT_and_SPSA_cash_drag.md](VT_and_SPSA_cash_drag.md) for results.

---

## Source Files

| File | Fund | Date | Format | Source |
|---|---|---|---|---|
| `holdings-daily-emea-en-spsa-gy.xlsx` | SPDR MSCI ACWI IMI UCITS ETF (SPSA GY) | 17 Jun 2026 | SSGA daily holdings | [ssga.com — SPSA GY product page](https://www.ssga.com/se/en_gb/intermediary/etfs/state-street-spdr-msci-all-country-world-investable-market-ucits-etf-dist-spsa-gy) → "Daily Holdings" download |
| `Holdings_details_Total_World_Stock_ETF.csv` | Vanguard Total World Stock ETF (VT) | 31 May 2026 | Vanguard holdings export | [advisors.vanguard.com — VT product page](https://advisors.vanguard.com/investments/products/vt/vanguard-total-world-stock-etf#overview) → Portfolio tab → "Export full holdings" |

### How to refresh data

**SPSA (SSGA xlsx):**
1. Go to the [SPSA GY product page](https://www.ssga.com/se/en_gb/intermediary/etfs/state-street-spdr-msci-all-country-world-investable-market-ucits-etf-dist-spsa-gy)
2. Scroll to the Holdings section → click **Daily Holdings** to download the xlsx
3. Replace `holdings-daily-emea-en-spsa-gy.xlsx` in this directory

**VT (Vanguard CSV):**
1. Go to the [VT product page](https://advisors.vanguard.com/investments/products/vt/vanguard-total-world-stock-etf#overview)
2. Click the **Portfolio** tab
3. Click **Export full holdings** → saves as `Holdings_details_Total_World_Stock_ETF.csv`
4. Replace the CSV in this directory

---

## Source Code

```
src/
├── models.py                 FundSnapshot and CashDragResult dataclasses
├── readers/
│   ├── xlsx_reader.py        Parse SSGA SPDR daily holdings xlsx
│   └── csv_reader.py         Parse Vanguard holdings CSV export
└── calculators/
    └── cash_drag.py          Compute CashDragResult from FundSnapshot
main.py                       Entry point — reads both files and prints results
requirements.txt              openpyxl
```

### Run

```bash
pip install openpyxl
python3 main.py
```
