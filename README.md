# SHEtoken ($SHE) — Women's Empowerment Index Token

> **She is the currency. SHE GOES UP.**

The world's first data-backed cryptocurrency tied to women's empowerment outcomes.
When women's conditions improve — tokens are minted. When conditions worsen — tokens are burned.

**Website:** shetoken.org | **API:** api.shetoken.org | **Twitter:** @ShetokenDAO | **Email:** contact@shetoken.org

---

## What This Repository Contains

The **data engine** — backend that powers everything. The Lovable website reads from the API. This repo generates the data, runs the weekly agent, and serves the API.

```
shetoken_repo/
├── agent/          ← Weekly news scanner + WEI live updater
├── api/            ← FastAPI serving all data to Lovable
├── pipeline/       ← All data generators
├── data/output/    ← Generated CSVs and JSONs
├── docs/           ← API reference, Lovable prompt, grievance app spec
└── wei-index/      ← methodology.md (full technical spec)
```

---

## Seven Tools

### 1. WEI — Women's Empowerment Index
**The master index. Drives the $SHE token.**

```
WEI = (Empowerment × 0.15) + (Education × 0.12) + (Economic × 0.12)
    + (Health × 0.12) + (Bodily Autonomy × 0.15) + (Safety & Justice × 0.14)
    + (Dignity & Welfare × 0.10) + (Digital & Social × 0.10)
    − (Violence Penalty × 0.10)
```

Token mechanics: WEI +1 point = 10M SHE minted | WEI -1 point = 10M SHE burned

| Coverage | Count | Historical |
|---|---|---|
| Countries | 105 | 2015–2024 ✅ |
| India states | 25 | 2015–2024 ✅ |
| USA states | 50 | 2015–2024 ✅ (post-Roe story) |
| Brazil / Nigeria / Mexico states | 27 / 34 / 31 | 2025 only |
| Pakistan provinces | 7 | 2025 only |
| World cities (top 20) | 20 | 2015–2024 ✅ |
| World cities (all) | 111 | 2025 only |

---

### 2. GPI — Gender Poverty Index
9 economic dimensions. Score: 100 = equality | 50 = women at half of men.

Key innovation: **time poverty** — women do 5.8× more unpaid care work than men in India. No other index tracks this.

Coverage: 34 countries | Historical: 2015–2024 ✅

---

### 3. SVI — Sexual Violence Index
**Uses WHO prevalence — NOT police reports.**

Sweden reports 94× more rapes than Pakistan yet scores far safer. Our index is the only one that gets this right.

Tracks: marital rape legal status (still legal in 20+ countries including India), conflict SGBV, reporting gap (India: 98% unreported), impunity, digital sexual violence.

Coverage: 38 countries | Historical: 2015–2024 ✅

---

### 4. WEVI — Widow & Elderly Vulnerability Index
India: 42.4M widows, 55% in poverty, 18% pension coverage.
45,000+ abandoned at temple towns (Vrindavan, Varanasi, Puri, Mathura, Tirupati).

Coverage: 35 countries + India states | Historical: 2025 only

---

### 5. WADI — Women's AI Displacement Index
Women are 2–3× more concentrated in high-automation-risk jobs.
Cambodia (86.3): 90% garment workers female, near-zero reskilling.
Bangladesh (82.7): 4M women garment workers face automation by 2030.

Coverage: 28 countries | Historical: 2025 only

---

### 6. Corporate Women's Rights Compliance Score (WRBCS)
**Should your company outsource to or do business with this country?**

```
WRBCS = WEI(40%) + SVI(25%) + GPI(20%) + (100−WADI)(15%)
```

| Rating | Countries |
|---|---|
| ✅ PREFERRED | Iceland, Norway, Sweden, Germany, Canada, Australia |
| 🟢 ACCEPTABLE | UK, Japan, South Korea, Brazil |
| 🟡 CAUTION | India, China, Philippines, Vietnam, Indonesia, Mexico |
| 🔴 AVOID | Bangladesh, Pakistan, Cambodia, Nigeria, Ethiopia, Myanmar |
| ⛔ EMBARGO | Afghanistan, DRC, Somalia |

**USA Post-Dobbs:** Vermont (94) ✅ vs Mississippi (0) 🔴 vs Texas (1) 🔴

**US Trade Exposure:** $28.3B/year flows to AVOID/EMBARGO countries.
If companies committed 1% to women's programs: **$283M/year** — 35% of UN Women's annual budget.

**Policy mechanisms:** WRTC voluntary commitment | Supply Chain Accord (Bangladesh Accord model) | Trade tariff (CBAM model) | State procurement preference (California SB 657 model)

---

### 7. Partner Directory
**Who should I work WITH for women-focused work?**
The opposite of the compliance score — positive discovery.

- **Country Partners:** 15 countries with strongest women's program ecosystems
- **Program Partners:** 14 proven programs available for funding/replication
- **Company Registries:** 6 verified public registries (UN WEPs: 3,000+ companies)

---

## Supporting Data

| Dataset | Countries | Weekly estimates |
|---|---|---|
| Women's Vital Statistics | 36 | ✅ Girls born, maternal deaths, child marriage |
| Rape Counts (reported vs WHO-estimated) | 38 | ✅ India: 35K reported vs 5.6M estimated |
| School Dropout Causes (8 causes) | 25 | — |
| Period Poverty Index | within dropout data | — |
| AI High-Risk Occupations | global | — |
| India Temple Town Widows | 5 cities | — |
| Policy Recommendations (govt + corporate) | 83 | — |
| Corporate Compliance Countries | 30 | — |
| Corporate Compliance USA States | 36 | — |
| US Trade Exposure vs WEI | 28 | — |
| Partner Directory — Countries | 15 | — |
| Partner Directory — Programs | 14 | — |

---

## Repository Structure

```
pipeline/data/
  # Core WEI
  generate_baseline.py                ← 105 country WEI
  generate_india_states.py            ← 25 India states
  generate_usa_states.py              ← 50 USA states
  generate_brazil/nigeria/mexico/pakistan_states.py
  generate_city_scores.py             ← 111 world cities

  # Historical (2015-2024)
  generate_historical_data.py         ← Countries + event-reversal model
  generate_historical_india_states.py ← Lakshmi Bhandar 2021 jump visible
  generate_historical_usa_states.py   ← Post-Roe bodily autonomy collapse
  generate_historical_cities.py       ← Top 20 cities
  generate_historical_gpi.py
  generate_historical_svi.py

  # Other indexes
  generate_gender_poverty_index.py    ← GPI 9 dimensions
  generate_sexual_violence_index.py   ← WHO prevalence, not police reports
  generate_widow_elderly_index.py     ← WEVI + India temple towns
  generate_ai_displacement_index.py   ← WADI
  generate_womens_vital_stats.py      ← Weekly estimates
  generate_rape_counts.py             ← Reported vs estimated
  generate_school_dropout_data.py     ← 8 causes per country

  # Policy + compliance + discovery
  generate_policy_recommendations.py  ← Govt actions + corporate actions
  generate_corporate_compliance_score.py  ← WRBCS ratings
  generate_usa_trade_exposure.py          ← $28.3B to AVOID countries
  generate_partner_directory.py           ← Who to work WITH

agent/
  config.py           ← 139+ news sources (15 languages)
  run_agent.py        ← Combined agent — runs every Sunday
  wei_updater.py      ← News signals → live WEI scores
  scanner/
    fetch_rss.py      ← 139 RSS feeds
    fetch_youtube.py  ← YouTube Data API v3
    fetch_reddit.py   ← Reddit public RSS
  classifier/
    slm_classifier.py ← Phi-3.5 Mini + Qwen2.5:3b via Ollama
  reporter/
    email_sender.py   ← Branded weekly newsletter (3 versions)
    sheets_writer.py  ← Google Sheets
  social/
    twitter_poster.py    ← Weekly 5-tweet thread
    instagram_poster.py  ← Weekly branded image

api/
  main.py             ← FastAPI — 30+ endpoints
  data_loader.py      ← CSV reader with 5-min cache
  analytics.py        ← API call tracking middleware
  README_API.md       ← How to connect Lovable
  README_ANALYTICS.md ← How to track API usage

docs/
  INDEXES_AND_API_SUMMARY.md  ← Complete Lovable prompt + API reference
  grievance-app.md            ← Anonymous reporting app technical spec

wei-index/
  methodology.md      ← Full technical spec for all 7 tools
```

---

## All API Endpoints

Base URL: `https://api.shetoken.org` | Docs: `/docs`

```
# Dashboard
GET /v1/summary                          → hero stats

# WEI Scores
GET /v1/wei/countries                    → 105 countries
GET /v1/wei/countries/{iso}              → e.g. /IND
GET /v1/wei/states/{country}             → india/usa/brazil/nigeria/mexico/pakistan
GET /v1/wei/states/{country}/{code}      → e.g. /india/WB
GET /v1/wei/cities                       → 111 cities
GET /v1/wei/cities/{slug}               → e.g. /mumbai /oslo /jackson-ms
GET /v1/wei/leaderboard                  → top/fastest movers

# Historical
GET /v1/wei/history/global-trend         → 2015-2024 global WEI
GET /v1/wei/history/country/{iso}        → single country trend
GET /v1/wei/history/compare?isos=IND,PAK → multi-country
GET /v1/wei/history/india-states         → Lakshmi Bhandar jump visible
GET /v1/wei/history/usa-states           → post-Roe bodily autonomy collapse
GET /v1/wei/history/cities               → top 20 cities 2015-2024
GET /v1/gpi/history                      → GPI 2015-2024
GET /v1/svi/history                      → SVI 2015-2024

# Other Indexes
GET /v1/gpi                              → Gender Poverty Index
GET /v1/gpi/{iso}                        → e.g. /IND (time poverty: 5.8x)
GET /v1/vital/global-counters            → weekly estimates live counters
GET /v1/vital/countries/{iso}           → country vital stats
GET /v1/wadi                             → AI Displacement Index
GET /v1/wadi/{iso}                       → e.g. /BGD (82.7 — garments)
GET /v1/wadi/occupations/high-risk       → 98% risk occupations, 89% female

# Corporate Compliance
GET /v1/compliance/countries             → WRBCS all countries
GET /v1/compliance/countries/{iso}       → e.g. /BGD → AVOID + required actions
GET /v1/compliance/usa-states            → post-Dobbs state ratings
GET /v1/compliance/usa-states/{code}     → e.g. /MS → AVOID detail

# Partner Directory
GET /v1/partners/countries               → who to partner WITH
GET /v1/partners/countries?sector=microfinance → filtered
GET /v1/partners/programs                → proven programs to fund/replicate
GET /v1/partners/programs?pillar=economic → filtered by WEI pillar
GET /v1/partners/companies               → 6 verified company registries

# Signals + Policy
GET /v1/signals/latest                   → this week's news signals
GET /v1/signals/pillar-summary           → pillar trend chart data
GET /v1/admin/stats                      → API call analytics
GET /v1/token                            → $SHE tokenomics
GET /docs                                → interactive playground
```

---

## Setup

```bash
# Install
pip install -r requirements.txt

# Run agent (dry run)
cd agent && python run_agent.py --dry-run

# Run API locally
cd api && uvicorn main:app --reload --port 8000
# → http://localhost:8000/docs

# Generate all data
cd pipeline && python run_pipeline.py --fallback --excel --sheets
```

**Minimum .env to start:**
```
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
REPORT_TO_EMAIL=your@gmail.com
```

Full .env guide: `agent/.env.example`

---

## Weekly Rhythm

**Sunday 6am UTC (automated):**
Scans 139+ sources → classifies with Phi-3.5 + Qwen2.5 → updates WEI live scores → writes Google Sheets → sends newsletter → posts Twitter + Instagram

**Monday morning (15 min):**
Read Gmail report → check crisis alerts → done

**Monthly (30 min):**
```bash
python run_pipeline.py --fallback && git add data/output/ && git commit -m "Monthly refresh" && git push
```

**Annually (2-3 hrs):**
Full WEI recalculation when WHO/UNESCO/UNODC publish new data.

---

## Architecture

```
Data Engine (this repo)                 Lovable Website
─────────────────────────               ──────────────────
pipeline/ → generates CSVs              React components
agent/    → weekly news       →  API →  Pages + routes
api/      → serves data                 Design system
data/     → CSV/JSON files    ←  fetch('/v1/...')
```

Full Lovable integration prompt: `docs/INDEXES_AND_API_SUMMARY.md`

---

## Technology Stack

| Layer | Technology |
|---|---|
| Blockchain | Ethereum ERC-20 + Polygon L2 |
| Oracle | Chainlink |
| Governance | Snapshot DAO |
| API | FastAPI + Python |
| SLM | Phi-3.5 Mini + Qwen2.5:3b (Ollama) |
| News sources | 139+ RSS feeds + YouTube + Reddit |
| Audit | CertiK + OpenZeppelin |
| DEX | Uniswap V3 |

---

## Token Distribution

| Allocation | Amount |
|---|---|
| Public Sale | 40% — 400M SHE |
| WEI Impact Fund | 25% — 250M SHE |
| Founding Team (3yr vesting) | 15% — 150M SHE |
| Ecosystem | 10% — 100M SHE |
| Reserve | 10% — 100M SHE |

---

*© 2026 SHE Foundation. MIT License.*
*shetoken.org · github.com/shetoken · @ShetokenDAO*

**SHE GOES UP.**
