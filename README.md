# SHEtoken ($SHE) — Women's Empowerment Index Token

> **She is the currency. SHE GOES UP.**

The world's first data-backed cryptocurrency tied to real-world women's empowerment outcomes — and now a full token ecosystem with real yield, prediction markets, and a mobile savings product for 570M women.

**Website:** shetoken.org | **API:** api.shetoken.org | **Twitter:** @ShetokenDAO | **Email:** contact@shetoken.org

---

## The Token Ecosystem (v2.0)

Five complementary tokens solving the annual price discovery gap:

| Token | What it is | Yield | Price updates |
|---|---|---|---|
| **SHE** | Master WEI index token | Staking rewards | Annual + weekly signals |
| **SHE-MFI** | Microfinance bond basket | **7.5% APY** | Daily (bond NAV) |
| **SHE-SAVE** | Women's savings account | **7.5–9.5% APY** | Daily |
| **SHEETF** | She-Economy ETF (30 companies) | Dividend + growth | Real-time |
| **SHE-STAKE** | Corporate certification | 2–8% APY | Real-time |

**Prediction markets** on women's rights outcomes create continuous SHE trading between annual index updates.

---

## The Nine Data Tools

### 1. WEI — Women's Empowerment Index
**Drives the SHE token.** 8 pillars, 0–100 scale.

```
WEI = (Empowerment × 0.15) + (Education × 0.12) + (Economic × 0.12)
    + (Health × 0.12) + (Bodily Autonomy × 0.15) + (Safety & Justice × 0.14)
    + (Dignity & Welfare × 0.10) + (Digital & Social × 0.10)
    − (Violence Penalty × 0.10)
```

WEI +1 point → 10M SHE minted | WEI -1 point → 10M SHE burned

| Coverage | Count | Historical |
|---|---|---|
| Countries | 105 | 2015–2024 ✅ |
| India states | 25 | 2015–2024 ✅ |
| USA states | 50 | 2015–2024 ✅ (post-Roe story) |
| Brazil / Nigeria / Mexico / Pakistan | 27/34/31/7 | 2025 |
| Top 20 cities | 20 | 2015–2024 ✅ |
| All world cities | 111 | 2025 |

### 2. GPI — Gender Poverty Index
9 economic dimensions. Tracks time poverty (women do 5.8× more unpaid care than men in India — no other index measures this).
Coverage: 34 countries | Historical: 2015–2024 ✅

### 3. SVI — Sexual Violence Index
Uses WHO prevalence, not police reports. Sweden reports 94× more rapes than Pakistan but scores far safer. Tracks marital rape legal status (still legal in 20+ countries).
Coverage: 38 countries | Historical: 2015–2024 ✅

### 4. WEVI — Widow & Elderly Vulnerability Index
India: 42.4M widows, 55% poverty, 18% pension. 45,000+ abandoned at temple towns.
Coverage: 35 countries + India states

### 5. WADI — Women's AI Displacement Index
Women 2–3× more concentrated in high-automation-risk jobs. Cambodia 86.3 (90% garment workers female, near-zero reskilling). Bangladesh 82.7 (4M women garment workers).
Coverage: 28 countries

### 6. WHI — Women's Health Index
Captures the health blind spots mainstream gender indices ignore: female mental health (depression, suicide), anaemia in women 15–49, menstrual health & dignity, and contraceptive unmet need. India 41.6 (dragged by 57% anaemia, NFHS-5). 0–100, higher = better.
Coverage: 38 countries | Mostly modeled estimates (see `data_source` column); verified WHO/DHS/UN Population Division pulls on roadmap.

### 7. WVI — Women's Voice Index
The most neglected dimension: online gender-based violence, women in media/journalism, women in tech & AI, and civil-society freedom (maps to V-Dem WCSP / Georgetown Women, Peace & Security Index). 0–100, higher = stronger voice.
Coverage: 38 countries | Mostly modeled estimates (see `data_source` column); verified V-Dem/GMMP/ILO pulls on roadmap.

### 8. Corporate Women's Rights Compliance Score (WRBCS)
Due diligence for outsourcing decisions. WRBCS = WEI(40%) + SVI(25%) + GPI(20%) + (100−WADI)(15%).
Ratings: ✅ PREFERRED | 🟢 ACCEPTABLE | 🟡 CAUTION | 🔴 AVOID | ⛔ EMBARGO
US trade exposure: $28.3B/year to AVOID/EMBARGO. 1% commitment = $283M to Impact Fund.

### 9. Partner Directory
Find partners for women-focused work: 15 country profiles, 14 proven programs, 6 company registries.

---

## Repository Structure

```
pipeline/data/
  # Core WEI
  generate_baseline.py                ← 105 countries
  generate_india/usa/brazil/nigeria/mexico/pakistan_states.py
  generate_city_scores.py             ← 111 cities

  # Historical (2015-2024, event-reversal model)
  generate_historical_data.py
  generate_historical_india/usa_states.py
  generate_historical_cities.py       ← top 20
  generate_historical_gpi/svi.py

  # Other indexes
  generate_gender_poverty_index.py    ← GPI 9 dimensions
  generate_sexual_violence_index.py   ← WHO prevalence
  generate_widow_elderly_index.py     ← WEVI + temple towns
  generate_ai_displacement_index.py   ← WADI
  generate_womens_vital_stats.py      ← weekly estimates
  generate_rape_counts.py             ← reported vs estimated
  generate_school_dropout_data.py     ← 8 causes

  # Policy + compliance + discovery
  generate_policy_recommendations.py  ← govt + corporate actions
  generate_corporate_compliance_score.py
  generate_usa_trade_exposure.py      ← $28.3B to AVOID
  generate_partner_directory.py       ← who to work WITH

  # Token ecosystem (v2.0)
  generate_microfinance_bond_basket.py ← SHE-MFI (12 MFIs, 7.5% yield)
  generate_prediction_markets.py       ← 15 markets, SHE collateral
  generate_she_economy_etf.py          ← SHEETF criteria + NAV
  generate_enhanced_tokenomics.py      ← full v2.0 spec
  generate_savings_product.py          ← SHE-SAVE (570M women target)

agent/
  config.py           ← 139+ sources, 15 languages
  run_agent.py        ← runs every Sunday 6am UTC
  wei_updater.py      ← signals → live WEI scores
  scanner/            ← RSS + YouTube + Reddit
  classifier/         ← Phi-3.5 + Qwen2.5 (Ollama)
  reporter/           ← newsletter + Google Sheets
  social/             ← Twitter thread + Instagram

api/
  main.py             ← FastAPI, 35+ endpoints
  data_loader.py      ← CSV/JSON reader, 5-min cache
  analytics.py        ← API call tracking

docs/
  INDEXES_AND_API_SUMMARY.md  ← complete Lovable prompt
  grievance-app.md            ← anonymous reporting spec

wei-index/
  methodology.md      ← full technical spec v3.2
```

---

## All API Endpoints

```
# Dashboard
GET /v1/summary

# WEI Scores
GET /v1/wei/countries          GET /v1/wei/countries/{iso}
GET /v1/wei/states/{country}   GET /v1/wei/states/{country}/{code}
GET /v1/wei/cities             GET /v1/wei/cities/{slug}
GET /v1/wei/leaderboard

# Historical
GET /v1/wei/history/global-trend
GET /v1/wei/history/country/{iso}   → /AFG shows 2021 Taliban crash
GET /v1/wei/history/usa-states      → post-Roe bodily autonomy collapse
GET /v1/wei/history/india-states    → Lakshmi Bhandar 2021 jump
GET /v1/wei/history/cities          → top 20 cities 2015-2024
GET /v1/wei/history/compare?isos=IND,PAK,BGD
GET /v1/gpi/history
GET /v1/svi/history

# Other Indexes
GET /v1/gpi                  GET /v1/gpi/{iso}
GET /v1/wadi                 GET /v1/wadi/{iso}
GET /v1/wadi/occupations/high-risk
GET /v1/svi                  GET /v1/svi/{iso}        → Sexual Violence Index
GET /v1/wevi                 GET /v1/wevi/{iso}       → Widow & Elderly Index
GET /v1/whi                  GET /v1/whi/{iso}        → Women's Health Index
GET /v1/wvi                  GET /v1/wvi/{iso}        → Women's Voice Index
GET /v1/vital/global-counters
GET /v1/vital/countries/{iso}

# Corporate + Trade
GET /v1/compliance/countries              → WRBCS all countries
GET /v1/compliance/countries/{iso}        → e.g. /BGD → AVOID
GET /v1/compliance/usa-states             → post-Dobbs ratings
GET /v1/compliance/usa-states/{code}      → e.g. /MS /VT /TX

# Partner Directory
GET /v1/partners/countries?sector=microfinance
GET /v1/partners/programs?pillar=economic
GET /v1/partners/companies

# Token Ecosystem v2.0
GET /v1/token                 → SHE master tokenomics
GET /v1/token/ecosystem       → all 5 token types
GET /v1/mfi/basket            → bond basket NAV (7.5% yield)
GET /v1/markets               → 15 prediction markets
GET /v1/markets/{id}          → e.g. /WEI-IND-50-2026
GET /v1/savings               → SHE-SAVE product spec
GET /v1/etf                   → SHEETF basket criteria

# Signals + Admin
GET /v1/signals/latest
GET /v1/signals/pillar-summary
GET /v1/admin/stats           → API call analytics
GET /docs                     → interactive playground
```

---

## Setup

```bash
pip install -r requirements.txt

# Agent (dry run)
cd agent && python run_agent.py --dry-run

# API
cd api && uvicorn main:app --reload --port 8000
# Open: http://localhost:8000/docs

# Generate all data
cd pipeline && python run_pipeline.py --fallback

# Minimum .env
GMAIL_USER=your@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
REPORT_TO_EMAIL=your@gmail.com
```

Full .env guide: `agent/.env.example`

---

## Weekly Rhythm

**Sunday automated:** Scan 139+ sources → classify → update WEI → also move the two news-sensitive sister indexes (SVI, WVI) → load into Supabase → Sheets → newsletter → Twitter + Instagram

**Monday (15 min):** Read Gmail report → check crisis alerts → done

**Monthly:** `python run_pipeline.py && git add data/output/ && git push` — regenerates all nine tools and reloads Supabase (structural indexes WHI/GPI/WEVI/WADI refresh here, not weekly)

**Annually:** Full WEI recalculation when WHO/UNESCO/UNODC publish.

---

## Architecture

```
Data Engine (this repo)          Read layers              Frontend
pipeline/ → generates CSVs   →   FastAPI (api/, Railway) → Lovable site
agent/    → weekly agent      →   Supabase (she_* tables)   (fetch /v1/...)
api/      → serves CSVs           Chainlink oracle        → smart contract
```

The CSVs in `data/output/` are the single source of truth. The **Lovable site
reads the FastAPI** — the data engine and UI are fully separate, connected only
over HTTP. Supabase is populated in parallel (independent read layer over the
same CSVs) as a fallback/alternative store, but the site does not read it
directly. Loaders that keep Supabase in sync: `pipeline/load_to_supabase.py`
(monthly) and `pipeline/load_live_to_supabase.py` (weekly).

Full Lovable build prompt: `docs/INDEXES_AND_API_SUMMARY.md`

**Public API:** read endpoints are open and keyless at a basic rate limit
(60/min per IP). Free and paid tokens unlock higher daily quotas — request one
at contact@shetoken.org. Tier details in `docs/api-reference.md`.

---

## Token Distribution

| Allocation | Amount |
|---|---|
| Public Sale | 40% — 400M SHE |
| WEI Impact Fund | 25% — 250M SHE |
| Founding Team (3yr) | 15% — 150M SHE |
| Ecosystem | 10% — 100M SHE |
| Reserve | 10% — 100M SHE |

---

*© 2026 SHE Foundation. MIT License.*
*shetoken.org · github.com/shetoken · @ShetokenDAO*
**SHE GOES UP.**

---

## Cloud Setup (No Local Machine Needed)

### GitHub Actions Workflows

Three automated workflows in `.github/workflows/`:

| Workflow | Schedule | What it does |
|---|---|---|
| `weekly-agent.yml` | Every Sunday 6am UTC | Scans 139+ sources, updates WEI, sends newsletter |
| `monthly-pipeline.yml` | 1st of every month | Regenerates all CSVs, commits to repo |
| `deploy-api.yml` | On every push | Auto-deploys API to Railway |

### One-Time Setup

**1. Add GitHub Secrets**
Repo → Settings → Secrets and variables → Actions → New secret:
```
GMAIL_USER
GMAIL_APP_PASSWORD
REPORT_TO_EMAIL
YOUTUBE_API_KEY
GOOGLE_SHEET_ID
RAILWAY_TOKEN        ← from Railway dashboard → Account → Tokens
NEWSLETTER_SUBSCRIBERS
```

**2. Get Railway Token**
Railway dashboard → Account Settings → Tokens → Create token
Add as `RAILWAY_TOKEN` in GitHub Secrets

**3. Run monthly pipeline manually first**
GitHub → Actions tab → Monthly Data Refresh → Run workflow
This generates all CSVs before the API needs them.

**4. Trigger weekly agent manually to test**
GitHub → Actions tab → Weekly WEI Agent → Run workflow
Check your Gmail for the newsletter.

### After That — Everything is Automatic

```
Sunday 6am UTC    → agent runs, newsletter sent, scores updated
1st of month      → data refreshed, repo updated, API redeployed
Every push        → API auto-deploys to Railway
```

You only touch the repo when you want to add features.
