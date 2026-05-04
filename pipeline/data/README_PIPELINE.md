# SHEtoken WEI Data Pipeline

This folder contains the complete data pipeline for generating the
Women's Empowerment Index (WEI) scores published at shetoken.org.

---

## Architecture

```
FETCH                    PROCESS                  GENERATE
─────────────────────    ─────────────────────    ─────────────────────
fetch_world_bank.py  →                        →
fetch_who.py         →   normalise.py         →   generate_baseline.py
fetch_ilo.py         →   build_pillars.py     →   generate_india_states.py
fetch_ipu.py         →   validate.py          →
fetch_unesco.py      →                        →
fetch_ncrb.py        →                        →
                         ↑                        ↑
manual/              →   manual CSV inputs    →   fallback estimates
```

---

## Quick Start

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. (Optional) Add API keys

Create a `.env` file in this directory:

```
UNESCO_API_KEY=your_key_here
```

Get a free UNESCO key at: https://apidata.uis.unesco.org/

### 3. Run the full pipeline

```bash
python run_pipeline.py
```

### 4. Use fallback estimates (no API calls needed)

```bash
python run_pipeline.py --fallback
```

---

## Folder Structure

```
data/
├── fetch/
│   ├── fetch_world_bank.py      World Bank API → raw/world_bank_raw.csv
│   ├── fetch_who.py             WHO GHO API → raw/who_raw.csv
│   ├── fetch_ilo.py             ILO STAT API → raw/ilo_raw.csv
│   ├── fetch_ipu.py             IPU Parline → raw/ipu_raw.csv
│   ├── fetch_unesco.py          UNESCO UIS API → raw/unesco_raw.csv
│   └── fetch_ncrb.py            NCRB PDF parser → raw/ncrb_raw.csv
│
├── process/
│   ├── normalise.py             Normalise indicators to 0–100
│   ├── build_pillars.py         Combine indicators into pillar scores
│   └── validate.py              Data quality validation
│
├── manual/
│   ├── un_women_manual.csv      UN Women indicators (no public API)
│   ├── oecd_sigi_manual.csv     OECD SIGI indicators (annual download)
│   └── ncrb_manual_template.csv India crime data (if PDF parse fails)
│
├── raw/                         Raw API responses (git-ignored)
├── processed/                   Normalised indicator files (git-ignored)
├── output/                      Final CSV files (committed to repo)
│   ├── baseline-2025.csv
│   └── india-states-2025.csv
│
├── config.py                    Shared constants and settings
├── generate_baseline.py         Generate global country CSV
├── generate_india_states.py     Generate India states CSV
└── sources.md                   Data source reference
```

---

## Data Sources

| Pillar | Source | API |
|---|---|---|
| Empowerment | IPU Parline, UN Women | ✅ IPU JSON, manual for UN Women |
| Education | UNESCO UIS, World Bank | ✅ Both have APIs (UNESCO needs key) |
| Economic | ILO STAT, World Bank | ✅ Both have APIs |
| Health | WHO GHO, World Bank | ✅ Both have APIs |
| Crime Penalty | UNODC, WHO, NCRB | ⚠ UNODC via manual; NCRB via PDF |

---

## Manual Data Updates

Some sources do not have public APIs and must be updated manually:

### UN Women (ministerial data)
1. Download from: https://data.unwomen.org/
2. Update: `data/manual/un_women_manual.csv`

### OECD SIGI
1. Download from: https://stats.oecd.org/Index.aspx?DataSetCode=SIGI2019
2. Update: `data/manual/oecd_sigi_manual.csv`

### NCRB (India crime data)
1. Download PDF from: https://ncrb.gov.in/crime-in-india.html
2. Run: `python data/fetch/fetch_ncrb.py --pdf path/to/report.pdf`
3. Or fill in: `data/manual/ncrb_manual_template.csv`

### UNODC (global crime data)
1. Download from: https://dataunodc.un.org/
2. Convert to CSV and add unodc_ columns to manual template

---

## Challenging a WEI Score

See: [wei-index/methodology.md](../wei-index/methodology.md#12-audit--challenge-process)

Open a GitHub Issue with label `wei-challenge`.

---

## Annual Update Schedule

```
Month 1 — Run pipeline with new year's data
Month 2 — Review validation report
Month 3 — Publish draft scores on GitHub (30-day review window)
Month 4 — Incorporate challenges, publish final scores
Month 5 — Smart contract execution (mint/burn)
```

---

## Contributing

See [CONTRIBUTING.md](../CONTRIBUTING.md) for how to suggest
new data sources or challenge existing scores.

---

*© 2026 SHE Foundation. Licensed under MIT.*
