# SHEtoken ($SHE) — Women's Empowerment Index Token

> **She is the currency. SHE GOES UP.**

The world's first data-backed cryptocurrency whose value is algorithmically tied to real-world women's empowerment outcomes. When women's conditions improve — tokens are minted. When conditions worsen — tokens are burned.

**Website:** shetoken.org &nbsp;|&nbsp; **API:** api.shetoken.org &nbsp;|&nbsp; **Twitter:** @ShetokenDAO &nbsp;|&nbsp; **Email:** contact@shetoken.org

---

## What This Repository Contains

This is the **data engine** — the backend that powers everything.
The Lovable website reads from the API. This repo generates the data.

```
shetoken_repo/
├── agent/          ← Weekly news scanner + WEI updater
├── api/            ← FastAPI serving all data to Lovable
├── pipeline/       ← Data generators for all indexes
├── data/output/    ← Generated CSV and JSON files
└── docs/           ← API reference, grievance app spec
```

---

## The Six Indexes

### 1. WEI — Women's Empowerment Index (master index)
**Drives the $SHE token.** Composite score for 105 countries, 174 states, 111 cities.

```
WEI = (Empowerment × 0.15) + (Education × 0.12) + (Economic × 0.12)
    + (Health × 0.12) + (Bodily Autonomy × 0.15) + (Safety & Justice × 0.14)
    + (Dignity & Welfare × 0.10) + (Digital & Social × 0.10)
    − (Violence Penalty × 0.10)

Score: 0–100 | Iceland: 93.4 | Global avg: 56.0 | Somalia: 5.2
```

**Token mechanics:**
- WEI rises +1 point → 10M SHE tokens **minted** to Impact Fund
- WEI falls -1 point → 10M SHE tokens permanently **burned**
- Crime spike >15% → DAO emergency governance vote

**Coverage:**
| Geography | Count | Historical |
|---|---|---|
| Countries | 105 | 2015–2024 ✅ |
| India states | 25 | 2015–2024 ✅ |
| USA states | 50 | 2015–2024 ✅ |
| Brazil states | 27 | 2025 only |
| Nigeria states | 34 | 2025 only |
| Mexico states | 31 | 2025 only |
| Pakistan provinces | 7 | 2025 only |
| World cities (top 20) | 20 | 2015–2024 ✅ |
| World cities (all) | 111 | 2025 only |

---

### 2. GPI — Gender Poverty Index
Measures economic equality between women and men across 9 dimensions.

| Dimension | What it measures |
|---|---|
| Income poverty | Female poverty rate vs male |
| Wealth | Women's median wealth as % of men's |
| Wage | Female wage as % of male wage |
| Labour participation | Female LFPR as % of male |
| Financial inclusion | Women with bank accounts |
| Food security | Gender gap in food insecurity |
| **Time poverty** | Women's unpaid care hours vs men's |
| Land ownership | % of landowners who are female |
| Social protection | % of women with coverage |

**Score: 100 = equality | 50 = women at half of men**
Coverage: 34 countries | Historical: 2015–2024 ✅

---

### 3. SVI — Sexual Violence Index
**Uses WHO prevalence surveys — NOT police reports.**

Why: Sweden reports 94× more rapes than Pakistan yet scores safer.
Pakistan's near-zero reports reflect suppression, not safety.

Tracks: WHO lifetime prevalence, reporting gap, marital rape status,
conflict-related SGBV, impunity, legal framework, digital SV.

**Marital rape still legal in 20+ countries including India, Pakistan, Bangladesh, Indonesia.**

Coverage: 38 countries | Historical: 2015–2024 ✅

---

### 4. WEVI — Widow & Elderly Vulnerability Index
Tracks one of the most invisible crises globally.

**India:** 42.4 million widows — largest widow population globally.
55% in poverty. Only 18% receive any pension (₹500/month).
45,000+ abandoned at temple towns (Vrindavan, Varanasi, Puri, Mathura, Tirupati).

Coverage: 35 countries + India states | Historical: 2025 only

---

### 5. WADI — Women's AI Displacement Index
Tracks gender-differentiated impact of AI and automation on women's employment.

Women are 2–3× more concentrated in high-automation-risk jobs than men:
- Medical transcriptionists: 98% automation risk, 89% female
- Secretaries: 96% automation risk, 94% female
- Bank tellers: 98% automation risk, 70% female

**Cambodia (86.3):** 90% of garment workers female, near-zero reskilling.
**Bangladesh (82.7):** 4M women garment workers facing automation by 2030.

Coverage: 28 countries | Historical: 2025 only

---

### 6. Policy Recommendation Engine
Reads ALL index scores and generates ranked, evidence-based policy priorities
for every country — each citing a proven real-world program.

Covers: WEI pillars, AI displacement, widow rights, marital rape,
reporting gap, conflict SGBV, period poverty, land ownership,
time poverty, caste targeting, indigenous women, temple towns.

**Example — India top priorities:**
1. Women's land title registration → cites Ethiopia (DV fell 33%)
2. AI reskilling program → cites Singapore SkillsFuture
3. Garment sector just transition → cites ACT Fund (H&M, Zara)
4. Marital rape criminalisation → very low cost, law change only
5. Temple town widow rehabilitation → cites Guild of Service Vrindavan

---

## Supporting Data Layers

| Dataset | Countries | Weekly estimates |
|---|---|---|
| Women's Vital Statistics | 36 | ✅ Girls born, maternal deaths, child marriage |
| Rape Counts (reported vs estimated) | 38 | ✅ India: 35K reported vs 5.6M estimated |
| School Dropout Causes (8 causes) | 25 | No |
| Gender Poverty Index | 34 | No |
| AI High-Risk Occupations | Global | No |
| India Temple Town Widows | 5 cities | No |

---

## Repository Structure

```
agent/
  config.py                 ← 139+ news sources (multilingual)
  run_agent.py              ← Combined agent v2 — runs every Sunday
  wei_updater.py            ← Applies signals to WEI scores
  scanner/
    fetch_rss.py            ← RSS feeds (139 sources)
    fetch_youtube.py        ← YouTube Data API v3
    fetch_reddit.py         ← Reddit public RSS
  classifier/
    slm_classifier.py       ← Phi-3.5 Mini + Qwen2.5:3b via Ollama
  aggregator/
    aggregate.py            ← Signal aggregation
  reporter/
    email_sender.py         ← Branded weekly newsletter
    sheets_writer.py        ← Google Sheets (signals + live WEI)
  social/
    twitter_poster.py       ← Weekly 5-tweet thread
    instagram_poster.py     ← Weekly branded image

api/
  main.py                   ← FastAPI — 25+ endpoints
  data_loader.py            ← CSV reader with cache
  analytics.py              ← API call tracking middleware
  README_API.md             ← How to connect Lovable
  README_ANALYTICS.md       ← How to track API usage

pipeline/
  data/
    generate_baseline.py              ← 105 country WEI
    generate_india_states.py          ← 25 India states
    generate_usa_states.py            ← 50 USA states
    generate_brazil_states.py         ← 27 Brazil states
    generate_nigeria_states.py        ← 34 Nigeria states
    generate_mexico_states.py         ← 31 Mexico states
    generate_pakistan_provinces.py    ← 7 Pakistan provinces
    generate_city_scores.py           ← 111 world cities
    generate_historical_data.py       ← Countries 2015–2024
    generate_historical_india_states.py
    generate_historical_usa_states.py ← Post-Roe story
    generate_historical_cities.py     ← Top 20 cities
    generate_historical_gpi.py
    generate_historical_svi.py
    generate_gender_poverty_index.py  ← GPI 9 dimensions
    generate_sexual_violence_index.py ← WHO prevalence based
    generate_widow_elderly_index.py   ← WEVI + temple towns
    generate_womens_vital_stats.py    ← Weekly estimates
    generate_rape_counts.py           ← Reported vs estimated
    generate_school_dropout_data.py   ← 8 causes per country
    generate_ai_displacement_index.py ← WADI
    generate_policy_recommendations.py ← All indexes combined

data/output/
  baseline-2025.csv
  india-states-2025.csv
  usa-states-2025.csv
  city-scores-2025.csv
  gender-poverty-index-2025.csv
  sexual-violence-index-2025.csv
  widow-elderly-index-2025.csv
  womens-vital-stats-2025.csv
  rape-counts-reported-vs-estimated-2025.csv
  school-dropout-causes-2025.csv
  ai-displacement-index-2025.csv
  ai-high-risk-occupations.json
  policy-recommendations-2025.csv
  policy-recommendations-2025.json
  global-vital-weekly.json
  global-rape-counters.json
  india-widow-states-2025.csv
  india-temple-town-widows.json
  historical/
    baseline-2015.csv → baseline-2024.csv
    wei-global-trend.csv
    wei-country-trends.csv
    india-state-trends.csv
    usa-state-trends.csv
    gpi-country-trends.csv
    svi-country-trends.csv
    city-trends-top20.csv

docs/
  INDEXES_AND_API_SUMMARY.md   ← Complete Lovable prompt + API reference
  grievance-app.md             ← Anonymous reporting app technical spec
  api-reference.md
  how-to-invest.md
```

---

## API Endpoints

**Base URL:** `https://api.shetoken.org`
**Docs:** `https://api.shetoken.org/docs`

### WEI Scores
```
GET /v1/summary                          → dashboard hero stats
GET /v1/wei/countries                    → 105 countries
GET /v1/wei/countries/{iso}              → single country (e.g. /IND)
GET /v1/wei/states/{country}             → india/usa/brazil/nigeria/mexico/pakistan
GET /v1/wei/states/{country}/{code}      → single state (e.g. /india/WB)
GET /v1/wei/cities                       → 111 cities
GET /v1/wei/cities/{slug}               → single city (e.g. /mumbai /oslo)
GET /v1/wei/leaderboard                  → top performers / fastest movers
```

### Historical Data
```
GET /v1/wei/history/global-trend         → Global WEI 2015–2024
GET /v1/wei/history/country/{iso}        → Single country trend
GET /v1/wei/history/compare?isos=IND,PAK → Multi-country comparison
GET /v1/wei/history/india-states         → India states 2015–2024
GET /v1/wei/history/usa-states           → USA post-Roe story
GET /v1/wei/history/cities               → Top 20 cities 2015–2024
GET /v1/gpi/history                      → GPI 2015–2024
GET /v1/svi/history                      → SVI 2015–2024
```

### Gender Poverty Index
```
GET /v1/gpi                              → all countries
GET /v1/gpi/{iso}                        → single country
```

### Vital Statistics
```
GET /v1/vital/global-counters            → weekly estimates (live counters)
GET /v1/vital/countries                  → all countries
GET /v1/vital/countries/{iso}           → single country
```

### Sexual Violence
```
GET /v1/svi                             → coming soon
```

### AI Displacement
```
GET /v1/wadi                            → all countries
GET /v1/wadi/{iso}                      → single country
GET /v1/wadi/occupations/high-risk      → occupation risk data
```

### Signals & News
```
GET /v1/signals/latest                  → this week's signals
GET /v1/signals/pillar-summary          → signal strength by pillar
GET /v1/signals/top-movers              → most active regions
```

### Admin
```
GET /v1/token                           → $SHE tokenomics
GET /v1/admin/stats                     → API call analytics
GET /docs                               → interactive API playground
```

---

## Setup

### Install dependencies
```bash
pip install -r requirements.txt
```

### Run agent (dry run — no email/social)
```bash
cd agent
python run_agent.py --dry-run
```

### Run API locally
```bash
cd api
uvicorn main:app --reload --port 8000
# Open: http://localhost:8000/docs
```

### Generate all data
```bash
cd pipeline
python run_pipeline.py --fallback --excel --sheets
```

### Environment variables
```bash
cp agent/.env.example agent/.env
# Fill in values — see agent/.env.example for full guide
```

**Minimum required to run:**
```
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
REPORT_TO_EMAIL=your@gmail.com
```

---

## Weekly Rhythm

**Sunday 6am UTC (automated):**
Agent scans 139+ sources → classifies with Phi-3.5 + Qwen2.5 →
updates WEI live scores → writes to Google Sheets →
sends newsletter → posts Twitter thread + Instagram

**Monday morning (you, 15 minutes):**
Read Gmail newsletter → check crisis alerts → done

**Monthly (30 minutes):**
```bash
python run_pipeline.py --fallback --excel --sheets
git add data/output/ && git commit -m "Monthly refresh" && git push
```

**Annually (2–3 hours):**
Full WEI recalculation when WHO/UNESCO/UNODC publish new data.

---

## Architecture

```
Data Engine Repo (this repo)          Lovable Website
─────────────────────────────         ───────────────
pipeline/ → generates CSVs            React components
agent/    → weekly news scan     →    Pages + routes
api/      → serves data          API  Design system
data/     → CSV files             ←   fetch('/v1/...')
```

The website only reads from the API. This repo never touches Lovable.

---

## Technology Stack

| Component | Technology |
|---|---|
| Blockchain | Ethereum ERC-20 + Polygon L2 |
| Oracle | Chainlink |
| Governance | Snapshot DAO |
| API | FastAPI + Python |
| SLM Classification | Phi-3.5 Mini + Qwen2.5:3b (Ollama) |
| Data Storage | CSV + IPFS |
| Smart Contract Audit | CertiK + OpenZeppelin |
| DEX Listing | Uniswap V3 |

---

## Token Distribution

| Allocation | Amount |
|---|---|
| Public Sale / Community | 40% — 400M SHE |
| WEI Impact Fund (NGO grants) | 25% — 250M SHE |
| Founding Team (3yr vesting) | 15% — 150M SHE |
| Ecosystem & Partnerships | 10% — 100M SHE |
| Reserve & Liquidity Pool | 10% — 100M SHE |

---

## Legal

This repository is for informational and research purposes.
SHE is a utility token. Not a security or investment product.
See `docs/legal-disclaimer.md` for full disclosure.

---

*© 2026 SHE Foundation. Licensed under MIT.*
*WEI methodology is open-source and freely auditable.*

**shetoken.org · github.com/shetoken · @ShetokenDAO**
