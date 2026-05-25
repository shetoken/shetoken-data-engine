# SHEtoken — Complete Index & API Reference
## What We've Built and How It All Works Together

---

## THE EIGHT INDEXES (+ POLICY ENGINE)

### 1. WEI — Women's Empowerment Index
**The master index. Drives the token.**

```
WEI = (Empowerment × 0.15) + (Education × 0.12)
    + (Economic × 0.12)    + (Health × 0.12)
    + (Bodily Autonomy × 0.15) + (Safety & Justice × 0.14)
    + (Dignity & Welfare × 0.10) + (Digital & Social × 0.10)
    − (Violence Penalty × 0.10)

Score: 0–100 | Global avg: 56.0 | Iceland: 93.4 | Somalia: 5.2
```

**What moves the token:**
- WEI rises +1 point → 10M SHE tokens minted to Impact Fund
- WEI falls -1 point → 10M SHE tokens permanently burned
- Crime spike >15% → DAO emergency governance vote

**Coverage:**
- 105 countries
- 174 sub-national regions (India 25, USA 50, Brazil 27, Nigeria 34, Mexico 31, Pakistan 7)
- 111 world cities
- Historical data 2015–2024

---

### 2. GPI — Gender Poverty Index
**Measures economic equality between women and men.**

```
GPI = avg(income_poverty + wealth + wage + labour_participation
        + financial_inclusion + food_security + time_poverty
        + land_ownership + social_protection)

Score: 0–100 | 100 = perfect equality | 50 = women at half of men
```

**The 9 dimensions:**
| Dimension | What it measures |
|---|---|
| Income poverty | Female poverty % vs male poverty % |
| Wealth | Women's median wealth as % of men's |
| Wage | Female wage as % of male wage |
| Labour participation | Female LFPR as % of male |
| Financial inclusion | Women with bank accounts |
| Food security | Gender gap in food insecurity |
| **Time poverty** | Women's unpaid care hours vs men's |
| Land ownership | % of landowners who are female |
| Social protection | % of women with coverage |

**Why time poverty matters:** In India women do 5.8× more unpaid care work
than men. In Japan 3.8×. This suppresses everything else — career, earnings,
political participation — yet no traditional poverty measure counts it.

---

### 3. SVI — Sexual Violence Index
**The only index that uses WHO prevalence — not police reports.**

```
SVI = (WHO_prevalence × 0.30) + (reporting_gap × 0.15)
    + (legal_framework × 0.15) + (impunity × 0.15)
    + (marital_rape_criminalised × 0.10)
    + (conflict_risk × 0.10) + (support_services × 0.05)

Score: 0–100 | Higher = safer
```

**Why this is different from all existing indices:**
- Uses WHO survey prevalence (not police statistics)
- Sweden reports 94× more rapes than Pakistan — yet scores far safer
- Tracks marital rape legal status (still legal in 20+ countries)
- Tracks conflict-related sexual violence separately
- Tracks impunity (% of reported rapes not convicted)
- Includes reporting gap as explicit indicator

---

### 4. WEVI — Widow & Elderly Vulnerability Index
**Tracks one of the most invisible crises globally.**

```
WEVI = poverty + legal_rights + enforcement
     + social_restrictions + abandonment
     + pension_coverage + elder_care

Score: 0–100 | Higher = more vulnerable
```

**India-specific crisis:**
- 42.4 million widows — largest widow population globally
- 55% live in poverty
- Only 18% receive any pension (₹200-500/month)
- 45,000+ abandoned at temple towns (Vrindavan, Varanasi, Puri, Mathura, Tirupati)
- True estimate: 200,000+ homeless widows at pilgrimage sites

---

### 5. WADI — Women's AI Displacement Index
**Tracks women's exposure to automation/AI job loss.**
0–100, higher = more vulnerable. Cambodia 86.3 (90% garment workers female).
Coverage: 28 countries.

### 6. WHI — Women's Health Index
**Health blind spots mainstream indices ignore.**
Female mental health (depression, suicide), anaemia in women 15–49,
menstrual health & dignity, contraceptive unmet need. 0–100, higher = better.
India 41.6 (57% anaemia). Coverage: 38 countries.
*Ships as transparent modeled estimates — see `data_source` column.*

### 7. WVI — Women's Voice Index
**The most neglected dimension.**
Online GBV, women in media, women in tech & AI, civil-society freedom
(maps to V-Dem WCSP / Georgetown WPS Index). 0–100, higher = stronger voice.
News-sensitive — updates weekly. Coverage: 38 countries.
*Ships as transparent modeled estimates — see `data_source` column.*

### 8. WRBCS — Corporate Compliance Score
**Outsourcing due-diligence rating.**
WRBCS = WEI(40%) + SVI(25%) + GPI(20%) + (100−WADI)(15%).
Ratings: PREFERRED / ACCEPTABLE / CAUTION / AVOID / EMBARGO.
Coverage: 30 countries + 36 US states.

---

### Policy Recommendation Engine
**Not an index — an output layer.**

Reads WEI + GPI pillar scores for any country and generates
ranked policy recommendations, each citing a proven real-world program.

```
Input:  Country ISO code + WEI pillar breakdown
Output: Top 5 policy priorities with:
        - Specific intervention
        - Estimated WEI impact
        - Cost tier
        - Time to impact
        - Proven example (Kanyashree, Kudumbashree, Iceland Equal Pay Act etc.)
```

---

## HOW THE INDEXES WORK TOGETHER

```
                    ┌─────────────────┐
                    │   WEI Score     │ ← master index → token mechanics
                    │   (0–100)       │
                    └────────┬────────┘
                             │
          ┌──────────────────┼──────────────────┐
          │                  │                  │
    ┌─────▼─────┐     ┌──────▼──────┐    ┌─────▼─────┐
    │    GPI    │     │    SVI      │    │   WEVI    │
    │ Economic  │     │  Violence   │    │  Widows   │
    │ equality  │     │  tracking   │    │ & elderly │
    └─────┬─────┘     └──────┬──────┘    └─────┬─────┘
          │                  │                  │
          └──────────────────▼──────────────────┘
                    ┌─────────────────┐
                    │  Policy Engine  │
                    │ Recommendations │
                    └─────────────────┘
```

**Combined score (CWPS):**
```
CWPS = (WEI × 0.60) + (GPI × 0.40)
```

**The four quadrants (for dashboard):**
```
         High WEI
              │
  Q2          │       Q1
  High WEI    │  High WEI
  Low GPI     │  High GPI  ← Nordic, Canada
  (Japan,     │
  S. Korea)   │
──────────────┼────────────── High GPI
              │
  Q3          │       Q4
  Low WEI     │  Low WEI
  Low GPI     │  High GPI
  (Afghanistan│  (Rwanda —
  Niger)      │  61% women
              │  in parliament
              │  but poor GPI)
         Low WEI
```

---

## SUPPORTING DATA LAYERS

| Dataset | What it tracks | Weekly estimates? |
|---|---|---|
| Vital Statistics | Girls born, maternal deaths, school enrollment | ✅ Yes |
| Rape Counts | Reported vs WHO-estimated actual | ✅ Yes |
| School Dropout Causes | 8 specific causes per country | No |
| Period Poverty | School days lost, product access, stigma | No |
| Historical WEI | 2015–2024 with COVID, Taliban, Roe events | No |

---

## ALL API ENDPOINTS

**Base URL:** `https://api.shetoken.org`
**Interactive docs:** `/docs`
**Public & keyless at a basic rate limit (60/min per IP). Free/paid tokens unlock higher daily quotas — email contact@shetoken.org.**

### Dashboard
```
GET /v1/summary
    → global_wei_score, countries_scored, latest_signals_count, crisis_count
    Use for: homepage hero section
```

### WEI Country Scores
```
GET /v1/wei/countries
    → 105 countries, all 8 pillar scores
    Params: ?tier=1 ?region=Europe ?sort=wei_score ?limit=20

GET /v1/wei/countries/{iso}
    → single country full breakdown
    Example: /v1/wei/countries/IND

GET /v1/wei/leaderboard
    → top performers or fastest movers
    Params: ?type=countries ?metric=change ?limit=10
```

### WEI State Scores
```
GET /v1/wei/states/{country}
    → state scores for india/usa/brazil/nigeria/mexico/pakistan
    Params: ?hot_only=true

GET /v1/wei/states/{country}/{code}
    → single state
    Example: /v1/wei/states/india/WB  (West Bengal)
             /v1/wei/states/usa/MS    (Mississippi)
```

### WEI City Scores
```
GET /v1/wei/cities
    → 111 world cities
    Params: ?country=IND ?region=Europe

GET /v1/wei/cities/{slug}
    → single city
    Example: /v1/wei/cities/mumbai
             /v1/wei/cities/oslo
             /v1/wei/cities/jackson-ms
```

### Historical Data
```
GET /v1/wei/history/global-trend
    → Global WEI 2015–2024 (shows COVID dip 2020, Taliban 2021, Roe 2022)
    Use for: main trend line chart

GET /v1/wei/history/country/{iso}
    → Single country 2015–2024
    Example: /v1/wei/history/country/AFG  (shows 2021 crash)
             /v1/wei/history/country/USA  (shows 2022 Dobbs drop)

GET /v1/wei/history/compare
    → Multiple countries on one chart
    Example: ?isos=IND,PAK,BGD,LKA
             ?isos=USA,GBR,DEU&pillar=bodily_autonomy_score

GET /v1/wei/history/india-states
    → India states 2015–2024
    Example: ?state_code=WB  (shows Lakshmi Bhandar 2021 jump)
```

### Gender Poverty Index
```
GET /v1/gpi
    → GPI for all countries, all 9 dimensions
    Params: ?country=IND

GET /v1/gpi/{iso}
    → Single country GPI breakdown
    Example: /v1/gpi/IND  → India (time poverty = women do 5.8x care work)
             /v1/gpi/ISL  → Iceland (near equality)
```

### Other Sister Indexes
```
GET /v1/svi      GET /v1/svi/{iso}    → Sexual Violence Index (WHO prevalence)
GET /v1/wevi     GET /v1/wevi/{iso}   → Widow & Elderly Vulnerability Index
GET /v1/whi      GET /v1/whi/{iso}    → Women's Health Index (mental, anaemia, menstrual)
GET /v1/wvi      GET /v1/wvi/{iso}    → Women's Voice Index (online GBV, media, civil society)
GET /v1/wadi     GET /v1/wadi/{iso}   → Women's AI Displacement Index
```

### Vital Statistics
```
GET /v1/vital/global-counters
    → Weekly estimates: girls born, maternal deaths, girls married under 18
    Use for: live counter widgets

GET /v1/vital/countries
    → Vital stats all countries
    Params: ?country=IND

GET /v1/vital/countries/{iso}
    → Single country: life expectancy, maternal mortality, school enrollment
```

### Signals (Weekly News Agent)
```
GET /v1/signals/latest
    → This week's classified news signals
    Params: ?pillar=bodily_autonomy ?country=IND ?crisis_only=true

GET /v1/signals/pillar-summary
    → Signal strength by WEI pillar (for pillar trend chart)

GET /v1/signals/top-movers
    → Most signal-active regions this week
```

### Token
```
GET /v1/token
    → SHE tokenomics, supply mechanics, mint/burn rules
```

---

## DATA LAYER — HOW LOVABLE READS THE DATA

The Lovable site reads from the **FastAPI** (`api.shetoken.org`). The data
engine and the UI are fully separate, connected only through HTTP. The UI
knows nothing about how data is produced — it just calls endpoints.

```
Data Engine (repo)        API boundary          UI (Lovable)
generators → CSVs   →   FastAPI (Railway)   →   fetch('/v1/...')
```

**Supabase is also populated** (the `she_*` tables below) as a parallel store
and fallback, but the Lovable site does NOT read it directly — it goes through
the API. Both are independent read layers over the same source CSVs and return
identical numbers, so Supabase remains available if you ever want the site to
switch to it.

| Supabase table (parallel store) | Holds |
|---|---|
| `she_wei_countries` | WEI hero + 8 pillars, 105 countries |
| `she_gpi_countries` / `she_svi_countries` / `she_wadi_countries` | GPI, SVI, WADI |
| `she_widow_elderly` / `she_corporate_compliance` | WEVI, WRBCS |
| `she_whi_countries` / `she_wvi_countries` | Women's Health, Women's Voice |
| `she_wei_live` / `she_svi_live` / `she_wvi_live` | weekly signal-adjusted scores |

---

## WHAT TO TELL LOVABLE

Copy this entire prompt into Lovable:

```
Build a website for SHEtoken (shetoken.org) — the world's first 
data-backed cryptocurrency tied to women's empowerment.

Connect to our live API at: https://api.shetoken.org
Public and keyless at a basic rate limit — no token needed for normal site
traffic. (Higher-volume third-party developers can request a token.)
See full docs at: https://api.shetoken.org/docs

Do NOT use any database directly — fetch everything from the API endpoints.

PAGES TO BUILD:

--- PAGE 1: HOMEPAGE ---
Hero section:
  Fetch GET /v1/summary
  Show: Global WEI Score (large number), Countries scored,
        Latest signals count, Crisis alerts

Live counters (update every 10 seconds with animated counter):
  Fetch GET /v1/vital/global-counters
  Show: Girls born this week, Maternal deaths this week,
        Girls married under 18 this week
  Style: Berry (#6D2E46) background, gold (#C9A84C) numbers

Global WEI trend line chart (2015-2024):
  Fetch GET /v1/wei/history/global-trend
  Annotate: COVID dip 2020, Afghanistan 2021, Roe 2022
  Show: global_wei by year

Top 10 country leaderboard table:
  Fetch GET /v1/wei/countries?limit=10&sort=wei_score
  Columns: Rank, Country, Ticker, WEI Score, vs Last Year

--- PAGE 2: WORLD MAP / LEADERBOARD ---
Country scores table (all 105):
  Fetch GET /v1/wei/countries
  Filter buttons: All Tiers | Tier 1 | Tier 2 | Tier 3 | Tier 4
  Sort by: WEI Score | Bodily Autonomy | Safety | Change
  Search bar to filter by country name

GPI vs WEI scatter chart:
  Fetch GET /v1/wei/countries AND GET /v1/gpi
  X axis: GPI score
  Y axis: WEI score
  Dot size: population_millions
  Colour by tier
  Label quadrants

--- PAGE 3: INDIA DEEP DIVE ---
India states table:
  Fetch GET /v1/wei/states/india
  Highlight HOT states in gold
  Columns: State, Ticker, WEI, Bodily Autonomy, Safety, Change, Key Program

India 10-year trend (line chart, multiple states):
  Fetch GET /v1/wei/history/india-states
  Show: Kerala, West Bengal, Bihar, UP lines
  Annotate Lakshmi Bhandar launch 2021 (WB jump)

India city scores:
  Fetch GET /v1/wei/cities?country=IND
  Show as ranked cards with pillar scores

--- PAGE 4: SIGNALS (weekly news) ---
Signal feed:
  Fetch GET /v1/signals/latest?limit=20
  Show: source, pillar tag, direction (+ or -), summary, link
  Crisis signals highlighted in red

Pillar signal chart (this week):
  Fetch GET /v1/signals/pillar-summary
  Bar chart showing net signal per pillar

--- PAGE 5: TOKEN ---
  Fetch GET /v1/token
  Show tokenomics, distribution pie chart, mint/burn mechanics

--- DESIGN SYSTEM ---
Primary:     Berry #6D2E46
Accent:      Gold #C9A84C
Background:  Dark #1A0A12
Text:        Cream #ECE2D0
Positive:    #1A6B34
Negative:    #8B0000
Font:        Arial / system-sans
Tagline:     "SHE GOES UP"
```

---

*© 2026 SHE Foundation | shetoken.org*
