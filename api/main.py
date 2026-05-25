"""
SHEtoken WEI Data API
======================
FastAPI-based REST API serving WEI scores, state data,
and weekly signals to the Lovable website and third parties.

Run locally:
    uvicorn main:app --reload --port 8000

API docs (auto-generated):
    http://localhost:8000/docs

Deploy to Railway/Render/Cloud Run — see README_API.md
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import logging

import os, secrets
import httpx

from supabase_source import get_svi, get_wevi, get_whi, get_wvi
from lifepath import get_life_path

from analytics import AnalyticsMiddleware, get_stats
from rate_limiter import rate_limit_middleware
from data_loader import (
    get_mfi_basket, get_prediction_markets, get_enhanced_tokenomics,
    get_savings_product, get_etf_spec,
    get_partner_countries, get_partner_programs, get_partner_companies,
    get_compliance, get_usa_compliance,
    get_global_scores, get_states, get_cities,
    get_latest_signals, get_summary,
    get_history, get_global_trend, get_india_state_history,
    get_vital_stats, get_gpi, get_global_weekly_counters,
    get_history_gpi, get_history_usa_states,
    get_history_cities, get_history_svi,
    get_wadi, get_ai_occupations
)

logger = logging.getLogger(__name__)

app = FastAPI(
    title="SHEtoken WEI API",
    description=(
        "The Women's Empowerment Index API. "
        "Live WEI scores for 105 countries and 174 sub-national regions. "
        "Data updates weekly via the SHEtoken news agent."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    contact={"email": "contact@shetoken.org",
             "url": "https://shetoken.org"},
    license_info={"name": "MIT",
                  "url": "https://github.com/shetoken"},
)

# ── Analytics middleware
app.add_middleware(AnalyticsMiddleware)

# ── Rate limiting middleware
app.middleware("http")(rate_limit_middleware)

# ── CORS — allow Lovable and any browser to call this API ─────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],           # Open for public API
    allow_credentials=False,
    allow_methods=["GET"],
    allow_headers=["*"],
)


# ── Root ──────────────────────────────────────────────────────────────────────



@app.get("/v1/admin/stats", tags=["Admin"],
         summary="API usage statistics")
def api_stats():
    """
    Returns API call counts, top endpoints, response times.

    Shows:
      - Total calls since last deploy
      - Calls per hour
      - Top 20 most-called endpoints
      - Error rates per endpoint
      - Average response time per endpoint
    """
    return get_stats()

@app.get("/", tags=["Info"])
def root():
    return {
        "name":    "SHEtoken WEI API",
        "version": "1.0.0",
        "docs":    "/docs",
        "endpoints": {
            "summary":          "/v1/summary",
            "global_scores":    "/v1/wei/countries",
            "country_detail":   "/v1/wei/countries/{iso_code}",
            "state_scores":     "/v1/wei/states/{country}",
            "city_scores":      "/v1/wei/cities",
            "leaderboard":      "/v1/wei/leaderboard",
            "latest_signals":   "/v1/signals/latest",
            "token_info":       "/v1/token",
        },
        "website": "https://shetoken.org",
        "github":  "https://github.com/shetoken",
    }


@app.get("/health", tags=["Info"])
def health():
    return {"status": "ok"}


# ── Summary Dashboard ─────────────────────────────────────────────────────────

@app.get("/v1/summary", tags=["Dashboard"],
         summary="Global WEI summary stats for dashboard")
def summary():
    """
    Returns key summary statistics for the SHEtoken dashboard.
    Use this to populate the homepage hero section.
    """
    data = get_summary()
    if not data:
        raise HTTPException(503, "Data not available")
    return data


# ── WEI Country Scores ────────────────────────────────────────────────────────

@app.get("/v1/wei/countries", tags=["WEI Scores"],
         summary="All country WEI scores")
def get_countries(
    tier: Optional[int] = Query(None, description="Filter by tier (1-4)"),
    region: Optional[str] = Query(None, description="Filter by region"),
    sort: Optional[str] = Query("wei_score", description="Sort field"),
    order: Optional[str] = Query("desc", description="asc or desc"),
    limit: Optional[int] = Query(None, ge=1, le=200, description="Max results"),
):
    """
    Returns WEI scores for all scored countries (105 countries).

    **Lovable usage:**
    ```js
    const res = await fetch('https://api.shetoken.org/v1/wei/countries')
    const { data } = await res.json()
    ```
    """
    countries = get_global_scores()

    if tier:
        countries = [c for c in countries if c.get("tier") == tier]
    if region:
        countries = [c for c in countries
                     if region.lower() in (c.get("region","")).lower()]

    reverse = (order == "desc")
    if sort in ("wei_score","rank","empowerment_score","bodily_autonomy_score",
                "population_millions"):
        countries = sorted(
            countries,
            key=lambda x: (x.get(sort) or 0),
            reverse=reverse
        )

    if limit:
        countries = countries[:limit]

    return {
        "count": len(countries),
        "data":  countries,
    }


@app.get("/v1/wei/countries/{iso_code}", tags=["WEI Scores"],
         summary="Single country WEI detail")
def get_country(iso_code: str):
    """
    Returns full WEI breakdown for a single country including all pillar scores.

    Example: `/v1/wei/countries/IND` for India
    """
    countries = get_global_scores()
    iso_upper = iso_code.upper()
    match = next((c for c in countries if c["iso_code"] == iso_upper), None)
    if not match:
        raise HTTPException(404, f"Country '{iso_code}' not found")
    return match


# ── WEI State / Province Scores ───────────────────────────────────────────────

SUPPORTED_COUNTRIES = ["india","usa","brazil","nigeria","mexico","pakistan"]

@app.get("/v1/wei/states/{country}", tags=["WEI Scores"],
         summary="State-level WEI scores")
def get_state_scores(
    country: str,
    hot_only: bool = Query(False, description="Only return HOT (fastest improving) states"),
    sort: Optional[str] = Query("wei_score", description="Sort field"),
):
    """
    Returns WEI scores for states/provinces of a country.

    Supported: `india`, `usa`, `brazil`, `nigeria`, `mexico`, `pakistan`

    **Lovable usage:**
    ```js
    const res = await fetch('https://api.shetoken.org/v1/wei/states/india')
    const { data } = await res.json()
    ```
    """
    if country.lower() not in SUPPORTED_COUNTRIES:
        raise HTTPException(404,
            f"Country '{country}' not supported. "
            f"Supported: {', '.join(SUPPORTED_COUNTRIES)}")

    states = get_states(country)
    if not states:
        raise HTTPException(503, f"No data for {country}")

    if hot_only:
        states = [s for s in states if s.get("hot")]

    if sort in ("wei_score","change","empowerment_score","bodily_autonomy_score"):
        states = sorted(states, key=lambda x: (x.get(sort) or 0), reverse=True)

    return {
        "country": country.title(),
        "count":   len(states),
        "data":    states,
    }


@app.get("/v1/wei/states/{country}/{state_code}", tags=["WEI Scores"],
         summary="Single state WEI detail")
def get_state(country: str, state_code: str):
    """
    Returns full WEI breakdown for a single state.

    Example: `/v1/wei/states/india/WB` for West Bengal
    """
    states = get_states(country)
    code_upper = state_code.upper()
    match = next(
        (s for s in states
         if (s.get("state_code","")).upper() == code_upper), None
    )
    if not match:
        raise HTTPException(404, f"State '{state_code}' not found in {country}")
    return match










# ── AI Displacement Index ─────────────────────────────────────────────────────

@app.get("/v1/wadi", tags=["AI Displacement"],
         summary="Women's AI Displacement Index — all countries")
def wadi_all(country: Optional[str] = Query(None, description="ISO code")):
    """
    Women's AI Displacement Index (WADI).
    Higher score = more vulnerable to AI/automation job losses.

    Key findings:
    - Cambodia (86.3): 90% of garment workers female, near-zero reskilling
    - Bangladesh (82.7): 4M garment women facing automation by 2030
    - Japan (41.8): high exposure but strong social protection
    - USA (moderate): 44% female workforce in high-risk sectors, weak coverage

    Tracks 8 dimensions: sector exposure, digital skills gap, reskilling
    access, AI opportunity capture, remote work access, social protection,
    gig vulnerability, AI policy inclusion.
    """
    rows = get_wadi(iso_code=country)
    if not rows: raise HTTPException(404, "No WADI data found")
    return {"count": len(rows), "data": rows}


@app.get("/v1/wadi/{iso_code}", tags=["AI Displacement"],
         summary="Single country AI displacement detail")
def wadi_country(iso_code: str):
    rows = get_wadi(iso_code=iso_code)
    if not rows: raise HTTPException(404, f"No WADI data for {iso_code}")
    return rows[0]


@app.get("/v1/wadi/occupations/high-risk", tags=["AI Displacement"],
         summary="High-risk occupations with female concentration data")
def ai_occupations():
    """
    Returns all occupations tracked, their automation risk %,
    and the % of that workforce who are female.

    Medical transcriptionists: 98% automation risk, 89% female.
    Secretaries: 96% automation risk, 94% female.
    Bank tellers: 98% automation risk, 70% female.
    """
    data = get_ai_occupations()
    if not data: raise HTTPException(503, "Occupation data unavailable")
    return data

# ── Women's Vital Statistics ─────────────────────────────────────────────────

@app.get("/v1/vital/global-counters", tags=["Vital Stats"],
         summary="Global weekly women's life statistics counters")
def global_counters():
    """
    Returns global weekly estimates for key women's life statistics.
    These are annual figures divided by 52 — not real-time, but presented
    as weekly rates for dashboard display (the same method UNICEF and
    WHO use publicly: "a woman dies in childbirth every 2 minutes").

    Use for live counter widgets on the dashboard.
    """
    data = get_global_weekly_counters()
    if not data: raise HTTPException(503, "Data unavailable")
    return data


@app.get("/v1/vital/countries", tags=["Vital Stats"],
         summary="Women's vital statistics by country")
def vital_stats_all(country: Optional[str] = Query(None, description="ISO code")):
    """
    Returns women's vital statistics for all countries including:
    - Girls born per week (estimate)
    - Maternal deaths per week (estimate)
    - Girls dropping out of school per week (estimate)
    - Girls married under 18 per week (estimate)
    - Women killed by partner per week (estimate)
    - Life expectancy gap vs men
    - Education funnel (primary → secondary → university)
    - Fertility rate
    - Female vs male poverty rates
    """
    rows = get_vital_stats(iso_code=country)
    if not rows: raise HTTPException(404, "No data found")
    return {"count": len(rows), "data": rows}


@app.get("/v1/vital/countries/{iso_code}", tags=["Vital Stats"],
         summary="Single country vital statistics")
def vital_stats_country(iso_code: str):
    rows = get_vital_stats(iso_code=iso_code)
    if not rows: raise HTTPException(404, f"No data for {iso_code}")
    return rows[0]


@app.get("/v1/gpi", tags=["Gender Poverty Index"],
         summary="Gender Poverty Index — women vs men across 9 economic dimensions")
def gender_poverty_index(
    country: Optional[str] = Query(None, description="Filter by ISO code")
):
    """
    Returns the Gender Poverty Index (GPI) for all countries.

    GPI measures equality across 9 dimensions:
    - Income poverty gap (female vs male headcount)
    - Wealth ratio (women's median wealth as % of men's)
    - Wage ratio
    - Labour participation ratio
    - Financial inclusion (bank account ownership)
    - Food security gap
    - Time poverty (unpaid care work hours)
    - Land ownership
    - Social protection coverage

    Score: 100 = perfect equality | 50 = women at half of men | 0 = full exclusion
    """
    rows = get_gpi(iso_code=country)
    if not rows: raise HTTPException(404, "No data found")
    return {"count": len(rows), "data": rows}


@app.get("/v1/gpi/{iso_code}", tags=["Gender Poverty Index"],
         summary="Single country GPI breakdown")
def gpi_country(iso_code: str):
    """
    Full GPI breakdown for a single country.
    Example: /v1/gpi/IND  → India gender poverty detail
    Example: /v1/gpi/AFG  → Afghanistan (near-zero on most dimensions)
    """
    rows = get_gpi(iso_code=iso_code)
    if not rows: raise HTTPException(404, f"No GPI data for {iso_code}")
    return rows[0]

# ── Historical Data ───────────────────────────────────────────────────────────

@app.get("/v1/wei/history/global-trend", tags=["Historical"],
         summary="Global WEI trend 2015-2024")
def global_trend():
    """
    Returns the population-weighted Global WEI score for each year 2015-2024.
    Use this for the main trend line chart on the dashboard.

    Key events visible in the data:
    - 2020: COVID-19 dip (-2 points globally)
    - 2021: Afghanistan crash (Taliban takeover)
    - 2022: USA Dobbs decision (Roe overturned)
    - 2024: Mexico + Namibia first female presidents
    """
    data = get_global_trend()
    if not data:
        raise HTTPException(503, "Historical data not available")
    return {"data": data, "years": len(data)}


@app.get("/v1/wei/history/country/{iso_code}", tags=["Historical"],
         summary="Single country WEI history 2015-2024")
def country_history(iso_code: str):
    """
    Returns year-by-year WEI scores and all pillar scores for a country.

    Example: /v1/wei/history/country/AFG  → Afghanistan (shows 2021 crash)
    Example: /v1/wei/history/country/USA  → USA (shows 2022 Dobbs drop)
    Example: /v1/wei/history/country/SAU  → Saudi Arabia (shows Vision 2030 rise)
    Example: /v1/wei/history/country/IND  → India (steady improvement)
    """
    rows = get_history(iso_code=iso_code)
    if not rows:
        raise HTTPException(404, f"No historical data for '{iso_code}'")
    country = rows[0].get("country","") if rows else iso_code
    return {
        "iso_code":     iso_code.upper(),
        "country":      country,
        "years":        len(rows),
        "from_year":    min(r["year"] for r in rows if r["year"]),
        "to_year":      max(r["year"] for r in rows if r["year"]),
        "data":         sorted(rows, key=lambda x: x["year"] or 0),
    }


@app.get("/v1/wei/history/compare", tags=["Historical"],
         summary="Compare multiple countries over time")
def compare_countries(
    isos: str = Query(..., description="Comma-separated ISO codes: IND,CHN,BRA,USA"),
    pillar: Optional[str] = Query(None, description="Specific pillar to compare"),
):
    """
    Compare WEI trends for multiple countries on one chart.

    Example: /v1/wei/history/compare?isos=IND,PAK,BGD,LKA
    Example: /v1/wei/history/compare?isos=USA,GBR,DEU&pillar=bodily_autonomy_score
    """
    iso_list = [i.strip().upper() for i in isos.split(",")][:8]
    result   = {}
    for iso in iso_list:
        rows = get_history(iso_code=iso)
        if rows:
            key = rows[0].get("country", iso)
            if pillar:
                result[key] = {r["year"]: r.get(pillar) for r in rows if r["year"]}
            else:
                result[key] = {r["year"]: r.get("wei_score") for r in rows if r["year"]}
    return {
        "pillar":    pillar or "wei_score",
        "countries": len(result),
        "data":      result,
    }


@app.get("/v1/wei/history/india-states", tags=["Historical"],
         summary="India state WEI history 2015-2024")
def india_state_history(
    state_code: Optional[str] = Query(None, description="Filter by state code e.g. WB, KL, BR"),
):
    """
    Returns year-by-year WEI history for Indian states.

    Key stories visible in the data:
    - WB (West Bengal): jump in 2021 when Lakshmi Bhandar launches
    - WB: steady education rise from Kanyashree scaling
    - KL (Kerala): consistent top performer since 2015
    - BR (Bihar): JEEViKA-driven economic improvement
    - 2020: COVID dip across all states
    """
    rows = get_india_state_history()
    if state_code:
        rows = [r for r in rows if r["state_code"].upper() == state_code.upper()]
    if not rows:
        raise HTTPException(404, "No data found")
    return {
        "states":    len(set(r["state_code"] for r in rows)),
        "years":     len(set(r["year"] for r in rows if r["year"])),
        "data":      sorted(rows, key=lambda x: (x.get("state_code",""), x.get("year") or 0)),
    }



@app.get("/v1/gpi/history", tags=["Historical"],
         summary="GPI trend 2015-2024 all countries")
def gpi_history(country: Optional[str] = Query(None)):
    rows = get_history_gpi()
    if country:
        rows = [r for r in rows if r["iso_code"].upper()==country.upper()]
    if not rows: raise HTTPException(404,"No GPI history found")
    return {"count":len(rows),"data":rows}


@app.get("/v1/wei/history/usa-states", tags=["Historical"],
         summary="USA state WEI 2015-2024 — the post-Roe story")
def usa_state_history(state_code: Optional[str] = Query(None)):
    """
    The most dramatic chart in the index.
    Dobbs (June 2022) caused bodily autonomy scores to diverge
    by 94 points between states in a single year.

    Jackson MS bodily autonomy: 35.5 (2021) → 0 (2022)
    California bodily autonomy: 80.6 (2021) → 94.7 (2022)
    """
    rows = get_history_usa_states()
    if state_code:
        rows = [r for r in rows if r["state_code"].upper()==state_code.upper()]
    if not rows: raise HTTPException(404,"No USA state history found")
    return {"count":len(rows),"data":sorted(rows, key=lambda x:(x.get("state_code",""),x.get("year") or 0))}


@app.get("/v1/wei/history/cities", tags=["Historical"],
         summary="Top 20 city WEI trend 2015-2024")
def city_history(slug: Optional[str] = Query(None,
                  description="City slug e.g. oslo, delhi, jackson-ms")):
    """
    Historical WEI for the 20 most significant world cities.
    Key events visible: Delhi 2013 law reform, COVID 2020,
    Jackson MS Dobbs 2022, Kolkata Lakshmi Bhandar 2021.
    """
    rows = get_history_cities()
    if slug:
        rows = [r for r in rows if r["slug"]==slug.lower()]
    if not rows: raise HTTPException(404,"No city history found")
    return {"count":len(rows),
            "cities":list(set(r["slug"] for r in get_history_cities())),
            "data":sorted(rows, key=lambda x:(x.get("slug",""),x.get("year") or 0))}


@app.get("/v1/svi/history", tags=["Historical"],
         summary="Sexual Violence Index trend 2015-2024")
def svi_history(country: Optional[str] = Query(None)):
    """
    SVI historical — key events:
    - Japan 2023: consent-based law finally passed (+7 points)
    - Afghanistan 2021: Taliban collapse (-9 points)
    - MeToo 2017: reporting gap reduced in Tier 1 countries
    - Colombia 2022: abortion decrim improved SVI
    """
    rows = get_history_svi(iso_code=country)
    if not rows: raise HTTPException(404,"No SVI history found")
    return {"count":len(rows),"data":sorted(rows, key=lambda x:(x.get("iso_code",""),x.get("year") or 0))}

# ── WEI City Scores ───────────────────────────────────────────────────────────

@app.get("/v1/wei/cities", tags=["WEI Scores"],
         summary="World city WEI scores")
def get_city_scores(
    country: Optional[str] = Query(None, description="Filter by ISO country code (e.g. IND, USA, BRA)"),
    region:  Optional[str] = Query(None, description="Filter by region (e.g. South Asia, Europe)"),
    sort:    Optional[str] = Query("wei_score", description="Sort field"),
    order:   Optional[str] = Query("desc", description="asc or desc"),
    limit:   Optional[int] = Query(None, ge=1, le=200),
):
    """
    Returns WEI scores for 111 world cities.

    Cities are scored on the same 8-pillar formula as countries,
    using city-specific data sources (NCRB city tables, FBI UCR,
    UN Habitat, SafeCity, CDC PLACES, Numbeo, EU Urban Audit).

    **Key insight:** The bodily autonomy gap between cities is huge.
    Oslo (94) vs Jackson MS (18) vs Kano (12) — within a single index.

    **Lovable usage:**
    ```js
    const res = await fetch('/v1/wei/cities?country=IND')
    const { data } = await res.json()
    ```
    """
    cities = get_cities(country_iso=country, region=region)
    if not cities:
        raise HTTPException(404, "No city data found for these filters")

    reverse = (order == "desc")
    valid_sorts = ("wei_score","rank","bodily_autonomy_score",
                   "safety_justice_score","population_millions")
    if sort in valid_sorts:
        cities = sorted(cities, key=lambda x: (x.get(sort) or 0), reverse=reverse)

    if limit:
        cities = cities[:limit]

    return {
        "count":  len(cities),
        "data":   cities,
    }


@app.get("/v1/wei/cities/{slug}", tags=["WEI Scores"],
         summary="Single city WEI detail")
def get_city(slug: str):
    """
    Returns full WEI breakdown for a single city.

    Use the city slug (lowercase, hyphenated):
    - `/v1/wei/cities/mumbai`
    - `/v1/wei/cities/new-york`
    - `/v1/wei/cities/sao-paulo`
    - `/v1/wei/cities/jackson-ms`
    """
    all_cities = get_cities()
    match = next((c for c in all_cities if c["slug"] == slug.lower()), None)
    if not match:
        all_slugs = [c["slug"] for c in all_cities]
        raise HTTPException(404,
            f"City '{slug}' not found. "
            f"Available slugs: {', '.join(sorted(all_slugs)[:20])}..."
        )
    return match

# ── Leaderboard ───────────────────────────────────────────────────────────────

@app.get("/v1/wei/leaderboard", tags=["WEI Scores"],
         summary="Top and fastest-moving countries/states")
def leaderboard(
    type: str = Query("countries", description="countries or states"),
    country: Optional[str] = Query(None, description="For states: which country"),
    metric: str = Query("wei_score", description="wei_score or change"),
    limit: int = Query(10, ge=1, le=50),
):
    """
    Returns the top WEI performers or fastest-improving regions.

    Used for the leaderboard table on shetoken.org.
    """
    if type == "countries":
        rows = get_global_scores()
    elif type == "states" and country:
        rows = get_states(country)
    else:
        raise HTTPException(400, "Specify type=states with country=india/usa/etc")

    if metric == "change":
        rows = [r for r in rows if r.get("change") is not None]
        rows = sorted(rows, key=lambda x: abs(x.get("change") or 0), reverse=True)
    else:
        rows = sorted(rows, key=lambda x: (x.get("wei_score") or 0), reverse=True)

    return {
        "type":   type,
        "metric": metric,
        "data":   rows[:limit],
    }


# ── Signals ───────────────────────────────────────────────────────────────────

@app.get("/v1/signals/latest", tags=["Signals"],
         summary="Latest weekly WEI signals from news")
def latest_signals(
    pillar: Optional[str] = Query(None,
        description="Filter by pillar: empowerment, education, economic, health, "
                    "bodily_autonomy, safety_justice, dignity_welfare, "
                    "digital_social, violence_penalty"),
    country: Optional[str] = Query(None, description="Filter by ISO country code"),
    crisis_only: bool = Query(False, description="Only return crisis signals"),
    limit: int = Query(20, ge=1, le=100),
):
    """
    Returns the most recent week's classified news signals.

    Each signal represents a news event with:
    - pillar affected
    - direction (positive/negative)
    - severity and confidence
    - country/state
    - source article URL
    """
    report = get_latest_signals()
    signals = report.get("raw_signals", [])

    if pillar:
        signals = [s for s in signals if s.get("pillar") == pillar]
    if country:
        signals = [s for s in signals
                   if s.get("country","").upper() == country.upper()]
    if crisis_only:
        signals = [s for s in signals if s.get("crisis")]

    return {
        "week":          report.get("week"),
        "total_signals": len(signals),
        "crisis_count":  sum(1 for s in signals if s.get("crisis")),
        "data":          signals[:limit],
    }


@app.get("/v1/signals/pillar-summary", tags=["Signals"],
         summary="Weekly signal summary by pillar")
def pillar_summary():
    """
    Returns aggregate signal strength for each WEI pillar this week.
    Use this for the pillar trend chart on the dashboard.
    """
    report = get_latest_signals()
    return {
        "week": report.get("week"),
        "data": report.get("global_pillar_summary", {}),
    }


@app.get("/v1/signals/top-movers", tags=["Signals"],
         summary="Most signal-active regions this week")
def top_movers(limit: int = Query(10, ge=1, le=50)):
    """Returns the regions with the most news signal activity this week."""
    report = get_latest_signals()
    return {
        "week": report.get("week"),
        "data": report.get("top_movers", [])[:limit],
    }


# ── Token Info ────────────────────────────────────────────────────────────────

@app.get("/v1/token", tags=["Token"],
         summary="SHE token information")
def token_info():
    """Returns SHEtoken tokenomics and current supply information."""
    return {
        "name":           "SHE (Women's Empowerment Index Token)",
        "ticker":         "SHE",
        "blockchain":     "Ethereum ERC-20",
        "layer2":         "Polygon",
        "total_supply":   1_000_000_000,
        "decimals":       18,
        "website":        "https://shetoken.org",
        "github":         "https://github.com/shetoken",
        "whitepaper":     "https://shetoken.org/whitepaper",
        "distribution": {
            "public_sale":    "40% — 400M SHE",
            "impact_fund":    "25% — 250M SHE",
            "founding_team":  "15% — 150M SHE (3yr vesting)",
            "ecosystem":      "10% — 100M SHE",
            "reserve":        "10% — 100M SHE",
        },
        "mechanics": {
            "mint_trigger": "+1 WEI point = 10M SHE minted to Impact Fund",
            "burn_trigger": "-1 WEI point = 10M SHE permanently burned",
            "crisis_trigger": ">15% crime spike = DAO emergency vote",
        },
    }


# ── Corporate Compliance ──────────────────────────────────────────────────────

@app.get("/v1/compliance/countries", tags=["Corporate Compliance"],
         summary="Women's Rights Business Compliance Score — all countries")
def compliance_countries(
    rating: Optional[str] = Query(None,
        description="Filter by rating: PREFERRED, ACCEPTABLE, CAUTION, AVOID, EMBARGO"),
    country: Optional[str] = Query(None, description="ISO code"),
):
    """
    Should your company outsource to this country?

    Five ratings:
    - ✅ PREFERRED  — actively prioritise (Iceland, Norway, Sweden, Germany, Canada, Australia)
    - 🟢 ACCEPTABLE — standard due diligence (UK, Japan, South Korea, Brazil)
    - 🟡 CAUTION    — enhanced obligations required (India, China, Philippines, Mexico, Indonesia)
    - 🔴 AVOID      — do not initiate new contracts (Bangladesh, Pakistan, Cambodia, Nigeria, Ethiopia)
    - ⛔ EMBARGO    — exit existing operations (Afghanistan, DRC, Somalia)

    Composite = WEI(40%) + SVI(25%) + GPI(20%) + (100-WADI)(15%)
    """
    rows = get_compliance(iso_code=country)
    if rating:
        rows = [r for r in rows if r["rating"]==rating.upper()]
    if not rows: raise HTTPException(404, "No data found")
    return {"count": len(rows), "data": rows}


@app.get("/v1/compliance/countries/{iso_code}", tags=["Corporate Compliance"],
         summary="Single country compliance detail")
def compliance_country(iso_code: str):
    """
    Full compliance profile for a single country.
    Includes: rating, required actions, NGO partners to fund, key risks.

    Example: /v1/compliance/countries/BGD  → Bangladesh (AVOID)
             /v1/compliance/countries/IND  → India (CAUTION)
             /v1/compliance/countries/ISL  → Iceland (PREFERRED)
    """
    rows = get_compliance(iso_code=iso_code)
    if not rows: raise HTTPException(404, f"No compliance data for {iso_code}")
    return rows[0]


@app.get("/v1/compliance/usa-states", tags=["Corporate Compliance"],
         summary="USA state compliance — post-Dobbs business risk")
def compliance_usa(
    rating: Optional[str] = Query(None,
        description="Filter: PREFERRED, ACCEPTABLE, CAUTION, AVOID"),
    state_code: Optional[str] = Query(None, description="2-letter state code"),
):
    """
    Which US states are safe for female employees?

    Based on: bodily autonomy score, maternal mortality, pay equity law.

    PREFERRED: Vermont, California, Massachusetts, Washington, Oregon, Colorado
    AVOID: Texas, Mississippi, Alabama, Louisiana, Arkansas, Kentucky, Oklahoma,
           Tennessee, Missouri, Idaho, West Virginia, South Dakota, North Dakota

    Texas bodily autonomy: 1/100. Mississippi: 0/100. Vermont: 94/100.
    """
    rows = get_usa_compliance(state_code=state_code)
    if rating:
        rows = [r for r in rows if r["rating"]==rating.upper()]
    if not rows: raise HTTPException(404, "No data found")
    return {"count": len(rows), "data": rows}


@app.get("/v1/compliance/usa-states/{state_code}", tags=["Corporate Compliance"],
         summary="Single US state compliance detail")
def compliance_usa_state(state_code: str):
    rows = get_usa_compliance(state_code=state_code.upper())
    if not rows: raise HTTPException(404, f"No data for state {state_code}")
    return rows[0]


# ── Partner Directory ─────────────────────────────────────────────────────────

@app.get("/v1/partners/countries", tags=["Partner Directory"],
         summary="Find countries to partner with for women-focused work")
def partner_countries(
    sector: Optional[str] = Query(None,
        description="Filter by sector e.g. 'education', 'microfinance', 'GBV', 'digital'"),
    region: Optional[str] = Query(None,
        description="Filter by region e.g. 'South Asia', 'Africa', 'Europe'"),
):
    """
    Positive discovery tool: which countries have the strongest ecosystems
    for women-focused partnership work?

    Returns country profiles with:
    - Strength sectors (what they are genuinely good at)
    - Flagship programs (proven programs you can partner with)
    - Who benefits most from partnering here
    - Entry point contacts

    Examples:
    - /v1/partners/countries?sector=microfinance → India Kerala, Bangladesh
    - /v1/partners/countries?sector=education → West Bengal, Rajasthan
    - /v1/partners/countries?region=Africa → Kenya, Rwanda, Ethiopia
    - /v1/partners/countries?sector=equal+pay → Iceland, Sweden, NZ
    """
    rows = get_partner_countries(sector=sector, region=region)
    if not rows: raise HTTPException(404, "No matching partners found")
    return {"count": len(rows), "data": rows}


@app.get("/v1/partners/programs", tags=["Partner Directory"],
         summary="Find proven programs to fund, replicate, or partner with")
def partner_programs(
    sector: Optional[str] = Query(None,
        description="e.g. 'education', 'microfinance', 'GBV', 'land rights', 'digital'"),
    pillar: Optional[str] = Query(None,
        description="WEI pillar: education, economic, bodily_autonomy, safety_justice, etc."),
    country: Optional[str] = Query(None, description="ISO code e.g. IND"),
):
    """
    Returns proven women's rights programs available for:
    - Direct funding
    - Replication in other countries
    - Research partnership
    - Co-branding

    Every program listed has verified outcome data and a replicable model.

    Examples:
    - /v1/partners/programs?sector=education → Kanyashree, Educate Girls
    - /v1/partners/programs?pillar=economic → Kudumbashree, SEWA, Iceland Equal Pay
    - /v1/partners/programs?country=IND → all India programs
    """
    rows = get_partner_programs(sector=sector, pillar=pillar, iso=country)
    if not rows: raise HTTPException(404, "No matching programs found")
    return {"count": len(rows), "data": rows}


@app.get("/v1/partners/companies", tags=["Partner Directory"],
         summary="Find companies with genuine women's rights commitments")
def partner_companies():
    """
    Directs to verified public registries of companies with women's rights
    commitments — rather than naming specific companies directly.

    Registries covered:
    - Equal Pay International Coalition (EPIC) certified employers
    - ILO Better Work buyer partners (garment sector)
    - B Corp directory with gender lens filter
    - 2X Challenge portfolio (gender lens investing)
    - UN Women's Empowerment Principles signatories (3,000+ companies)
    - GenderSmart investing directory

    Each registry is independently maintained and publicly verified.
    """
    data = get_partner_companies()
    if not data: raise HTTPException(503, "Data unavailable")
    return data


# ── Enhanced Token Ecosystem ──────────────────────────────────────────────────

@app.get("/v1/token/ecosystem", tags=["Token"],
         summary="Full enhanced token ecosystem — all 5 token types")
def token_ecosystem():
    """Full SHEtoken v2.0 ecosystem: SHE, SHE-MFI, SHE-SAVE, SHEETF, SHE-STAKE."""
    data = get_enhanced_tokenomics()
    if not data: raise HTTPException(503, "Data unavailable")
    return data


@app.get("/v1/mfi/basket", tags=["Microfinance"],
         summary="Microfinance bond basket — current NAV and portfolio")
def mfi_basket():
    """
    Women's microfinance bond basket powering the SHE-SAVE savings token.
    12 MFI institutions. 25.1M women borrowers. 7.5% weighted yield.
    NAV updates daily via bond accrual.
    """
    data = get_mfi_basket()
    if not data: raise HTTPException(503, "Data unavailable")
    return data


@app.get("/v1/markets", tags=["Prediction Markets"],
         summary="Women's rights prediction markets")
def prediction_markets(
    category: Optional[str] = Query(None,
        description="WEI_COUNTRY, WEI_STATE, SVI_LAW, GPI_CORP, WADI_SECTOR, IMPACT"),
):
    """
    15 prediction markets resolving on SHEtoken index publications.
    Collateral: SHE tokens. Creates continuous trading between annual WEI updates.

    Categories:
    - WEI_COUNTRY: Will India WEI exceed 50 by 2026? (28% yes)
    - SVI_LAW:     Will India criminalise marital rape by 2027? (22% yes)
    - IMPACT:      Will Kanyashree reach 12M girls by 2026? (58% yes)
    """
    markets = get_prediction_markets(category=category)
    if not markets: raise HTTPException(404, "No markets found")
    return {
        "count": len(markets),
        "categories": list(set(m["category"] for m in markets)),
        "data": markets,
    }


@app.get("/v1/markets/{market_id}", tags=["Prediction Markets"],
         summary="Single prediction market detail")
def prediction_market(market_id: str):
    markets = get_prediction_markets()
    m = next((x for x in markets if x["id"]==market_id), None)
    if not m: raise HTTPException(404, f"Market {market_id} not found")
    return m


@app.get("/v1/savings", tags=["Savings Product"],
         summary="Women's Savings Account — product spec and yield")
def savings_product():
    """
    SHE-SAVE: Women's savings account token.
    $1 minimum. 7.5-9.5% APY. Backed by microfinance bonds.
    Target: 570M women in India, Kenya, Bangladesh, Nigeria with mobile money.

    Yield = MFI bond yield (7.5%) + WEI performance bonus (0-2%)
    """
    data = get_savings_product()
    if not data: raise HTTPException(503, "Data unavailable")
    return data


@app.get("/v1/etf", tags=["ETF"],
         summary="She-Economy ETF — basket criteria and NAV mechanics")
def etf_spec():
    """
    SHEETF: Basket of publicly traded companies meeting women's rights criteria.
    NAV updates in real-time during market hours.
    Management fee: 0.35% (0.20% → WEI Impact Fund).
    Differentiator vs MSCI Women's Index: WEI integration + WRBCS screening + tokenised.
    """
    data = get_etf_spec()
    if not data: raise HTTPException(503, "Data unavailable")
    return data

@app.post("/v1/admin/keys")
async def create_api_key(
    owner_email: str,
    tier: str = "free",
    token: str | None = None, ):         # admin auth, ?token=..
    """
    Mint a new developer API key. Admin only.
    Call: POST /v1/admin/keys?owner_email=dev@x.com&tier=free&token=<ADMIN_TOKEN>
    """
    # The rate-limit middleware already enforces admin on /v1/admin/* —
    # if we got here, the caller is admin.
    if tier not in ("free", "paid", "admin"):
        raise HTTPException(400, "tier must be free, paid, or admin")

    new_token = secrets.token_urlsafe(32)
    supabase_url = os.getenv("SUPABASE_URL")
    service_key  = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not supabase_url or not service_key:
        raise HTTPException(500, "Supabase service credentials not configured")

    resp = httpx.post(
        f"{supabase_url}/rest/v1/she_api_keys",
        headers={
            "apikey":        service_key,
            "Authorization": f"Bearer {service_key}",
            "Content-Type":  "application/json",
            "Prefer":        "return=minimal",
        },
        json={"token": new_token, "owner_email": owner_email, "tier": tier,
              "active": True},
        timeout=5.0,
    )
    if resp.status_code not in (200, 201, 204):
        raise HTTPException(500, f"Could not create key: {resp.text}")

    return {
        "token": new_token,
        "owner_email": owner_email,
        "tier": tier,
        "message": "Store this token securely — it won't be shown again.",
    }
@app.get("/v1/svi")
def svi_scores():
    """Sexual Violence Index — all countries (WHO-prevalence based)."""
    return {"count": len(get_svi()), "data": get_svi()}

@app.get("/v1/svi/{iso_code}")
def svi_country(iso_code: str):
    rows = get_svi(iso_code)
    if not rows:
        raise HTTPException(404, f"No SVI data for {iso_code}")
    return rows[0]

@app.get("/v1/wevi")
def wevi_scores():
    """Widow & Elderly Vulnerability Index — all countries."""
    return {"count": len(get_wevi()), "data": get_wevi()}

@app.get("/v1/wevi/{iso_code}")
def wevi_country(iso_code: str):
    rows = get_wevi(iso_code)
    if not rows:
        raise HTTPException(404, f"No WEVI data for {iso_code}")
    return rows[0]

@app.get("/v1/whi")
def whi_scores():
    """Women's Health Index — mental health, anaemia, menstrual, contraception."""
    return {"count": len(get_whi()), "data": get_whi()}

@app.get("/v1/whi/{iso_code}")
def whi_country(iso_code: str):
    rows = get_whi(iso_code)
    if not rows:
        raise HTTPException(404, f"No WHI data for {iso_code}")
    return rows[0]

@app.get("/v1/wvi")
def wvi_scores():
    """Women's Voice Index — online GBV, media, tech, civil-society freedom."""
    return {"count": len(get_wvi()), "data": get_wvi()}

@app.get("/v1/wvi/{iso_code}")
def wvi_country(iso_code: str):
    rows = get_wvi(iso_code)
    if not rows:
        raise HTTPException(404, f"No WVI data for {iso_code}")
    return rows[0]
@app.get("/v1/lifepath/{iso_code}")
def life_path(iso_code: str):
    """
    The '100 Girls' life journey for one country — a cohort of 100 girls walked
    through life using real, sourced statistics. A narrative device to make the
    data felt, NOT a personal prediction (see the 'disclaimer' field).
    """
    lp = get_life_path(iso_code)
    if not lp:
        raise HTTPException(404, f"No life-path data for {iso_code}")
    return lp
