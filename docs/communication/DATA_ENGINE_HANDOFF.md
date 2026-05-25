SHEtoken Data Engine — Architecture & Handoff
> **Purpose of this document:** a single, complete reference for the SHEtoken
> data engine, so it can run without active attention while focus moves to the
> Lovable app. If you're reading this cold months from now, start here.
>
> **Last updated:** May 2026 · **Status:** live (API deployed on Railway)
---
1. What this is, in one paragraph
The SHEtoken data engine turns the state of women's lives around the world into
numbers, refreshes those numbers automatically, and serves them over a public
API. At its centre is the Women's Empowerment Index (WEI) — an 8-pillar,
0–100 score for 105 countries (current global population-weighted score ≈ 55.4).
Around it sit seven sister indexes covering poverty, sexual violence, AI job
displacement, widows/elderly, health, voice, and corporate compliance. A weekly
news agent nudges the news-sensitive scores between annual data releases. All
data is committed to GitHub as auditable CSVs, mirrored into Supabase, and
served by a FastAPI on Railway. The website (Lovable) reads only the API.
---
2. The mental model
```
  generators (Python)              ← you rarely touch these
        │  produce
        ▼
  data/output/*.csv                ← SINGLE SOURCE OF TRUTH (auditable, on GitHub)
        │  loaded into
        ▼
  Supabase  (she_* tables)         ← the store the API reads
        │  read by
        ▼
  FastAPI  (api/, on Railway)      ← the public API, api.shetoken.org
        │  read by
        ▼
  Lovable website                  ← the UI (next iteration's focus)
```
The one rule that keeps this sane: the CSVs are the source of truth.
Supabase and the API are read layers over them. The CSVs stay on GitHub
because open, auditable data is the project's core credibility claim — anyone
can replicate or challenge a score. Don't delete them.
---
3. The indexes
All scored 0–100. Unless noted, higher = better.
Index	Measures	Coverage	Token-linked	Update cadence
WEI — Women's Empowerment	8 pillars (below)	105 countries + states + cities	✅ drives the token	annual + weekly signals
GPI — Gender Poverty	9 economic dimensions incl. time poverty	34 countries	signal	monthly
SVI — Sexual Violence	WHO prevalence (not police reports)	38 countries	signal	weekly
WADI — AI Displacement	women's exposure to automation (higher = more exposed)	28 countries	signal	monthly
WEVI — Widow & Elderly	widow poverty, inheritance, abandonment (higher = more vulnerable)	35 countries + India states	signal	monthly
WHI — Women's Health	mental health, anaemia, menstrual, contraception	38 countries	signal	monthly
WVI — Women's Voice	online GBV, media, tech, civil-society freedom	38 countries	signal	weekly
WRBCS — Corporate Compliance	outsourcing due-diligence rating	30 countries + 36 US states	due diligence	monthly
The 8 WEI pillars (with weights)
```
WEI = Empowerment(0.15) + Education(0.12) + Economic(0.12) + Health(0.12)
    + Bodily Autonomy(0.15) + Safety & Justice(0.14)
    + Dignity & Welfare(0.10) + Digital & Social(0.10)
    − Violence Penalty(0.10)
```
Violence is a penalty (subtracted), not a pillar — a country cannot offset
violence against women with strong economics. Full weights and per-indicator
sources live in `wei-index/methodology.md`.
Data honesty (important for credibility)
WHI and WVI currently ship as transparent modeled estimates. Every record
carries a `data_source` field marking modeled vs verified. The roadmap replaces
estimates with verified WHO / V-Dem / DHS pulls per indicator without changing
the schema. Never present modeled numbers as measured — the `data_source` flag
is the integrity mechanism.
---
4. Repository structure
```
shetoken-data-engine/
├── pipeline/
│   └── data/
│       ├── generate_*.py        ← one generator per index → writes a CSV
│       ├── config_v3.py         ← OUTPUT_DIR, BASELINE_YEAR, shared constants
│       └── README_PIPELINE.md
├── data/output/*.csv            ← SOURCE OF TRUTH (committed to GitHub)
├── agent/
│   ├── run_agent.py             ← weekly news agent entry point
│   ├── scanner/, classifier/, aggregator/
│   ├── wei_updater.py           ← turns signals into capped WEI deltas
│   ├── sister_updater.py        ← moves SVI + WVI weekly (reuses the same engine)
│   └── output/live/*.csv        ← live weekly scores (gitignored, ephemeral)
├── api/
│   ├── main.py                  ← FastAPI app + all routes
│   ├── data_loader.py           ← reads CSVs (cached 5 min)
│   ├── supabase_source.py       ← reads Supabase for SVI/WEVI/WHI/WVI (CSV fallback)
│   ├── api_keys.py              ← token validation + tier quotas
│   ├── rate_limiter.py          ← public IP limits + token tiers
│   └── analytics.py
├── pipeline/load_to_supabase.py        ← monthly: CSVs → Supabase
├── pipeline/load_live_to_supabase.py   ← weekly: live scores → Supabase
├── db/*.sql                     ← Supabase schema files
├── .github/workflows/*.yml      ← the 3 automated jobs
└── docs/, wei-index/, WHITEPAPER.md, README.md
```
---
5. The three automated workflows
Everything runs on GitHub Actions (not on a server) — that's why the data
engine needs no babysitting.
Workflow	File	Schedule	What it does
Monthly Data Refresh	`monthly-pipeline.yml`	`0 4 1 * *` (1st of month)	Re-runs all generators → commits fresh CSVs → loads Supabase baselines
Weekly News Agent	`weekly-agent.yml`	`0 6 * * 0` (Sundays)	Scans news → classifies → moves WEI + SVI + WVI live scores → loads Supabase → newsletter/social
Deploy / Load	`deploy-api.yml`, load workflows	on push / manual	Keeps the API + Supabase in sync
All three can be run manually: Actions tab → pick workflow → Run workflow.
---
6. The weekly news agent (how scores move between data releases)
Scan 139+ sources (RSS, YouTube, Reddit) across ~15 languages.
Classify each article with a local small language model (Phi-3.5 / Qwen2.5
via Ollama): pillar, direction (+1 good / −1 bad), severity, confidence, geo.
Aggregate into a net signal per country per pillar.
Apply to scores:
```
   delta = avg_signal × SIGNAL_WEIGHT(0.08) × 100, capped at ±2.0 points
   WEI_live = baseline + delta
   SVI_live = baseline + (safety_justice + violence_penalty signals)
   WVI_live = baseline + (empowerment + digital_social signals)
   ```
Direction is uniform (+good / −bad) and all three indexes are higher = better,
so a femicide pushes SVI down; a new digital-rights law pushes WVI up.
Structural indexes (WHI, GPI, WEVI, WADI) are NOT moved weekly — nothing
in a week's news legitimately changes anaemia prevalence. Fast data looks
fast, slow data looks slow. That mixed cadence is a deliberate credibility
choice.
Live files land in `agent/output/live/` (gitignored) and are pushed to Supabase
by `load_live_to_supabase.py`, which is why the API must read Supabase to serve
live weekly numbers.
---
7. The public API
Base URL: `https://api.shetoken.org` · Docs: `/docs` (lists every live route)
Key endpoints
```
/v1/summary                       global headline numbers
/v1/wei/countries  /{iso}         WEI + 8 pillars
/v1/wei/states/{country}          sub-national WEI
/v1/gpi   /v1/svi   /v1/wadi      sister indexes (+ /{iso})
/v1/wevi  /v1/whi   /v1/wvi       sister indexes (+ /{iso})
/v1/compliance/countries          WRBCS
/v1/signals/latest                weekly news signals
/v1/admin/keys (POST)             mint a developer token (admin only)
```
Access tiers
Tier	Token	Limit
Public	none	60 req/min per IP
Free	yes	5,000 / day
Paid	yes	100,000 / day
Admin	yes	unlimited
Tokens live in the `she_api_keys` Supabase table. Pass as
`Authorization: Bearer <token>` or `?token=<token>`.
Testing as admin
```bash
# bypass all limits with your admin token
curl -H "Authorization: Bearer YOUR_ADMIN_TOKEN" https://api.shetoken.org/v1/summary

# prove the public limit works (expect 429s near request 60)
for i in $(seq 1 65); do curl -s -o /dev/null -w "%{http_code}\n" \
  https://api.shetoken.org/v1/summary; done

# mint a developer key
curl -X POST "https://api.shetoken.org/v1/admin/keys?owner_email=dev@x.com&tier=free&token=YOUR_ADMIN_TOKEN"
```
---
8. Supabase
Project: `https://ezfnvonjhnssotaaqpmr.supabase.co`
Tables: prefixed `she_*` (one per index, plus `she_wei_live`, `she_svi_live`,
`she_wvi_live`, `she_wei_history_global`, `she_api_keys`, `she_api_usage`).
Data tables have public-read RLS (safe to read with the publishable key).
`she_api_keys` is private — RLS-locked, no public policy. The API reads it
with the service-role key. Never expose that key.
Schema files are in `db/`. All idempotent — safe to re-run. If a loader
ever errors with `PGRST205 — table not found`, the table's schema SQL hasn't
been run yet.
---
9. Railway (the deployment)
The FastAPI runs as one Railway service — the one with the public domain
(`api.shetoken.org`). (A second, domainless service was a duplicate and can be
ignored/deleted; it serves nothing.)
Auto-deploy: Railway watches the GitHub repo. Commit to GitHub →
Railway redeploys in ~1–2 minutes. No manual deploy step. Watch progress in
the service's Deployments tab.
Required env vars (Variables tab on the live service):
```
  SUPABASE_URL                = https://ezfnvonjhnssotaaqpmr.supabase.co
  SUPABASE_ANON_KEY           = sb_publishable_...      (reads public she_* tables)
  SUPABASE_SERVICE_ROLE_KEY   = <service role>          (reads she_api_keys)
  ADMIN_TOKEN                 = <optional legacy admin token>
  ```
Endpoints work via CSV fallback even with no Supabase env vars — but live
weekly SVI/WVI numbers only flow when the Supabase vars are set.
---
10. If something breaks
Symptom	Likely cause	Fix
`/v1/<new>` returns `{"detail":"Not Found"}`	route not deployed	commit the route to `main.py`; wait for Railway redeploy; check `/docs`
An old endpoint works, a new one 404s	server healthy, new code not shipped	same as above
ALL endpoints 404 / no response	Railway service down	check Railway Deployments tab for a failed build + its log
Loader: `PGRST205 table not found`	schema SQL not run	run the matching `db/*.sql` in Supabase
Endpoint returns `[]`	Supabase empty + CSV missing	run the loader; confirm the CSV exists in `data/output/`
Weekly agent `[5b]` "skipped"	sister_updater hit an error (non-fatal)	check the agent log; WVI baseline CSV may be missing
Node.js 20 deprecation warning	GitHub runner update	bump `actions/checkout@v4→v5`, `setup-python@v5→v6`, `cache@v4→v5` (before Jun 2 2026)
---
11. Not built yet (backlog)
Migrate existing endpoints (WEI/GPI/WADI/compliance) from CSV → Supabase
read (low priority — they work; route their `_load()` through `supabase_source._rows()`).
Trafficking index + hotspot map (UNODC/NCRB corridors).
Female Hunger Index (FHI) generator (FAO + WHO anaemia). (Note: FHI is one
letter from WHI — keep them distinct.)
Verified-data upgrades for WHI and WVI (replace modeled estimates).
Persistent token usage counting (currently in-memory; resets on Railway
restart — fine for launch, upgrade for exact paid enforcement).
---
12. Cheat-sheet for future-you
Source of truth = CSVs in `data/output/`. Everything else reads from them.
Commit to GitHub → API updates automatically (~2 min).
The live API service is the one with the public domain.
Higher = better for every index (even SVI — it rewards safety, not violence).
Docs that go stale are the ones that hold lists (index count, endpoint list,
tier table). Narrative docs (CONTRIBUTING, methodology rationale) don't.
WHI/WVI are modeled estimates — the `data_source` flag is the honesty layer.
Run any job manually: Actions tab → workflow → Run workflow.
```

*© 2026 SHE Foundation. Data engine documentation. MIT-licensed methodology.*
