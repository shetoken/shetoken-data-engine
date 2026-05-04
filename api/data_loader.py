"""
SHEtoken API — Data Loader
Reads WEI CSV files and signal JSONs, caches in memory.
Refreshes automatically when files change.
"""
import csv, io, json, os, glob, logging
from pathlib import Path
from datetime import datetime, timezone
from functools import lru_cache
from typing import Optional

logger = logging.getLogger(__name__)

# Resolve data paths relative to this file
API_DIR   = Path(__file__).parent
REPO_ROOT = API_DIR.parent
DATA_DIR  = REPO_ROOT / "data" / "output"
LIVE_DIR  = REPO_ROOT / "agent" / "output" / "live"
SIG_DIR   = REPO_ROOT / "agent" / "output" / "signals"


def load_csv(path: Path) -> list[dict]:
    """Load a WEI CSV, skipping comment lines."""
    if not path.exists():
        logger.warning(f"CSV not found: {path}")
        return []
    with open(path, "r", encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    reader = csv.DictReader(io.StringIO("".join(lines)))
    return [dict(row) for row in reader]


def safe_float(val, default=None):
    try: return float(val)
    except (TypeError, ValueError): return default


def safe_int(val, default=None):
    try: return int(val)
    except (TypeError, ValueError): return default


# ── In-memory cache ───────────────────────────────────────────────────────────

_cache: dict = {}
_cache_times: dict = {}
CACHE_TTL = 300  # 5 minutes


def cached(key: str, loader_fn):
    now = datetime.now(timezone.utc).timestamp()
    if key not in _cache or (now - _cache_times.get(key, 0)) > CACHE_TTL:
        _cache[key] = loader_fn()
        _cache_times[key] = now
    return _cache[key]


# ── Loaders ───────────────────────────────────────────────────────────────────

def get_global_scores() -> list[dict]:
    """Load global country WEI scores (live if available, else baseline)."""
    def _load():
        # Try latest live file first
        live_files = sorted(LIVE_DIR.glob("wei-live-global-*.csv"), reverse=True)
        path = live_files[0] if live_files else DATA_DIR / "baseline-2025.csv"
        rows = load_csv(path)
        result = []
        for r in rows:
            result.append({
                "rank":                  safe_int(r.get("rank")),
                "country":               r.get("country",""),
                "iso_code":              r.get("iso_code",""),
                "ticker":                r.get("ticker",""),
                "region":                r.get("region",""),
                "tier":                  safe_int(r.get("tier")),
                "population_millions":   safe_float(r.get("population_millions")),
                "wei_score":             safe_float(r.get("wei_score")),
                "wei_score_baseline":    safe_float(r.get("wei_score_baseline",
                                            r.get("wei_score"))),
                "weekly_delta":          safe_float(r.get("weekly_delta", 0)),
                "empowerment_score":     safe_float(r.get("empowerment_score")),
                "education_score":       safe_float(r.get("education_score")),
                "economic_score":        safe_float(r.get("economic_score")),
                "health_score":          safe_float(r.get("health_score")),
                "bodily_autonomy_score": safe_float(r.get("bodily_autonomy_score")),
                "safety_justice_score":  safe_float(r.get("safety_justice_score")),
                "dignity_welfare_score": safe_float(r.get("dignity_welfare_score")),
                "digital_social_score":  safe_float(r.get("digital_social_score")),
                "violence_penalty_score":safe_float(r.get("violence_penalty_score")),
                "data_type":             r.get("wei_data_type","baseline"),
                "year":                  safe_int(r.get("year", 2025)),
                "verified":              r.get("verified","false"),
            })
        return result
    return cached("global", _load)


def get_states(country: str) -> list[dict]:
    """Load state/province WEI scores for a given country."""
    country_lower = country.lower()
    file_map = {
        "india":    ("india-states-2025.csv",    "wei-live-india-*.csv"),
        "usa":      ("usa-states-2025.csv",       "wei-live-usa-*.csv"),
        "brazil":   ("brazil-states-2025.csv",    "wei-live-bra-*.csv"),
        "nigeria":  ("nigeria-states-2025.csv",   "wei-live-nga-*.csv"),
        "mexico":   ("mexico-states-2025.csv",    "wei-live-mex-*.csv"),
        "pakistan": ("pakistan-provinces-2025.csv","wei-live-pak-*.csv"),
    }
    if country_lower not in file_map:
        return []

    def _load():
        baseline_name, live_pattern = file_map[country_lower]
        live_files = sorted(LIVE_DIR.glob(live_pattern), reverse=True)
        path = live_files[0] if live_files else DATA_DIR / baseline_name
        rows = load_csv(path)
        result = []
        for r in rows:
            state_code = r.get("state_code") or r.get("province_code","")
            result.append({
                "rank":                  safe_int(r.get("rank")),
                "state":                 r.get("state") or r.get("province",""),
                "state_code":            state_code,
                "ticker":                r.get("ticker",""),
                "region":                r.get("region",""),
                "population_millions":   safe_float(r.get("population_millions")),
                "wei_score":             safe_float(r.get("wei_score")),
                "wei_score_baseline":    safe_float(r.get("wei_score_baseline",
                                             r.get("wei_score"))),
                "change":                safe_float(r.get("change", 0)),
                "hot":                   r.get("hot","false") == "true",
                "watch":                 r.get("watch","false") == "true",
                "empowerment_score":     safe_float(r.get("empowerment_score")),
                "education_score":       safe_float(r.get("education_score")),
                "economic_score":        safe_float(r.get("economic_score")),
                "health_score":          safe_float(r.get("health_score")),
                "bodily_autonomy_score": safe_float(r.get("bodily_autonomy_score")),
                "safety_justice_score":  safe_float(r.get("safety_justice_score")),
                "dignity_welfare_score": safe_float(r.get("dignity_welfare_score")),
                "digital_social_score":  safe_float(r.get("digital_social_score")),
                "violence_penalty_score":safe_float(r.get("violence_penalty_score")),
                "key_programs":          r.get("key_programs",""),
                "verified":              r.get("verified","false"),
                "data_type":             r.get("wei_data_type","baseline"),
            })
        return result
    return cached(f"states_{country_lower}", _load)


def get_latest_signals() -> dict:
    """Load the most recent weekly signal report."""
    def _load():
        sig_files = sorted(SIG_DIR.glob("signals_*.json"), reverse=True)
        if not sig_files:
            return {"week": None, "total_signals": 0, "signals": []}
        with open(sig_files[0], encoding="utf-8") as f:
            return json.load(f)
    return cached("latest_signals", _load)


def get_summary() -> dict:
    """Compute global summary stats for the dashboard."""
    def _load():
        countries = get_global_scores()
        if not countries:
            return {}
        scores    = [c["wei_score"] for c in countries if c["wei_score"]]
        tier_counts = {}
        for c in countries:
            t = str(c.get("tier",""))
            tier_counts[t] = tier_counts.get(t,0) + 1
        india = next((c for c in countries if c["iso_code"]=="IND"), {})
        sigs  = get_latest_signals()
        pop_weighted = sum(
            c["wei_score"] * (c["population_millions"] or 0)
            for c in countries if c["wei_score"]
        ) / max(sum(c["population_millions"] or 0 for c in countries), 1)

        return {
            "global_wei_score":        round(pop_weighted, 1),
            "countries_scored":        len(countries),
            "india_wei":               india.get("wei_score"),
            "tier_1_count":            tier_counts.get("1",0),
            "tier_2_count":            tier_counts.get("2",0),
            "tier_3_count":            tier_counts.get("3",0),
            "tier_4_count":            tier_counts.get("4",0),
            "highest_country":         countries[0]["country"] if countries else None,
            "highest_score":           countries[0]["wei_score"] if countries else None,
            "lowest_country":          countries[-1]["country"] if countries else None,
            "lowest_score":            countries[-1]["wei_score"] if countries else None,
            "latest_signal_week":      sigs.get("week"),
            "latest_signals_count":    sigs.get("total_signals",0),
            "latest_crisis_count":     sigs.get("crisis_count",0),
            "last_updated":            datetime.now(timezone.utc).isoformat(),
        }
    return cached("summary", _load)


def get_cities(country_iso: str = None, region: str = None) -> list[dict]:
    """Load world city WEI scores."""
    def _load():
        path = DATA_DIR / "city-scores-2025.csv"
        rows = load_csv(path)
        result = []
        for r in rows:
            result.append({
                "rank":                  safe_int(r.get("rank")),
                "city":                  r.get("city",""),
                "slug":                  r.get("slug",""),
                "ticker":                r.get("ticker",""),
                "country_iso":           r.get("country_iso",""),
                "state_code":            r.get("state_code",""),
                "region":                r.get("region",""),
                "population_millions":   safe_float(r.get("population_millions")),
                "wei_score":             safe_float(r.get("wei_score")),
                "empowerment_score":     safe_float(r.get("empowerment_score")),
                "education_score":       safe_float(r.get("education_score")),
                "economic_score":        safe_float(r.get("economic_score")),
                "health_score":          safe_float(r.get("health_score")),
                "bodily_autonomy_score": safe_float(r.get("bodily_autonomy_score")),
                "safety_justice_score":  safe_float(r.get("safety_justice_score")),
                "dignity_welfare_score": safe_float(r.get("dignity_welfare_score")),
                "digital_social_score":  safe_float(r.get("digital_social_score")),
                "violence_penalty_score":safe_float(r.get("violence_penalty_score")),
                "data_quality":          r.get("data_quality",""),
                "notes":                 r.get("notes",""),
                "year":                  safe_int(r.get("year", 2025)),
            })
        return result
    cities = cached("cities", _load)
    if country_iso:
        cities = [c for c in cities if c["country_iso"].upper() == country_iso.upper()]
    if region:
        cities = [c for c in cities if region.lower() in c["region"].lower()]
    return cities


def get_history(iso_code: str = None, country: str = None) -> list[dict]:
    """Load historical WEI trend data (2015-2024)."""
    def _load_global():
        path = DATA_DIR / "historical" / "wei-country-trends.csv"
        if not path.exists():
            return []
        rows = load_csv(path)
        return [{
            "iso_code": r.get("iso_code",""),
            "country":  r.get("country",""),
            "year":     safe_int(r.get("year")),
            "wei_score": safe_float(r.get("wei_score")),
            "empowerment_score":     safe_float(r.get("empowerment_score")),
            "education_score":       safe_float(r.get("education_score")),
            "economic_score":        safe_float(r.get("economic_score")),
            "health_score":          safe_float(r.get("health_score")),
            "bodily_autonomy_score": safe_float(r.get("bodily_autonomy_score")),
            "safety_justice_score":  safe_float(r.get("safety_justice_score")),
            "dignity_welfare_score": safe_float(r.get("dignity_welfare_score")),
            "digital_social_score":  safe_float(r.get("digital_social_score")),
            "violence_penalty_score":safe_float(r.get("violence_penalty_score")),
            "tier": safe_int(r.get("tier")),
        } for r in rows]
    all_rows = cached("history_global", _load_global)
    if iso_code:
        all_rows = [r for r in all_rows if r["iso_code"].upper() == iso_code.upper()]
    return all_rows


def get_global_trend() -> list[dict]:
    """Load global WEI trend by year."""
    def _load():
        path = DATA_DIR / "historical" / "wei-global-trend.csv"
        if not path.exists(): return []
        rows = load_csv(path)
        return [{
            "year":           safe_int(r.get("year")),
            "global_wei":     safe_float(r.get("global_wei")),
            "countries":      safe_int(r.get("countries")),
            "tier1_count":    safe_int(r.get("tier1")),
            "tier2_count":    safe_int(r.get("tier2")),
            "tier3_count":    safe_int(r.get("tier3")),
            "tier4_count":    safe_int(r.get("tier4")),
            "top_country":    r.get("top_country",""),
            "top_score":      safe_float(r.get("top_score")),
            "bottom_country": r.get("bottom_country",""),
            "bottom_score":   safe_float(r.get("bottom_score")),
        } for r in rows]
    return cached("global_trend", _load)


def get_india_state_history() -> list[dict]:
    """Load India state WEI history."""
    def _load():
        path = DATA_DIR / "historical" / "india-state-trends.csv"
        if not path.exists(): return []
        rows = load_csv(path)
        return [{
            "state":          r.get("state",""),
            "state_code":     r.get("state_code",""),
            "ticker":         r.get("ticker",""),
            "year":           safe_int(r.get("year")),
            "wei_score":      safe_float(r.get("wei_score")),
            "empowerment_score":     safe_float(r.get("empowerment_score")),
            "education_score":       safe_float(r.get("education_score")),
            "economic_score":        safe_float(r.get("economic_score")),
            "health_score":          safe_float(r.get("health_score")),
            "bodily_autonomy_score": safe_float(r.get("bodily_autonomy_score")),
            "safety_justice_score":  safe_float(r.get("safety_justice_score")),
            "dignity_welfare_score": safe_float(r.get("dignity_welfare_score")),
            "digital_social_score":  safe_float(r.get("digital_social_score")),
            "violence_penalty_score":safe_float(r.get("violence_penalty_score")),
        } for r in rows]
    return cached("india_history", _load)


def get_vital_stats(iso_code: str = None) -> list[dict]:
    """Load women's vital statistics by country."""
    def _load():
        path = DATA_DIR / "womens-vital-stats-2025.csv"
        rows = load_csv(path)
        return [{
            "country":                          r.get("country",""),
            "iso_code":                         r.get("iso_code",""),
            "region":                           r.get("region",""),
            "girls_born_per_1000_pop":          safe_float(r.get("girls_born_per_1000_pop")),
            "life_expectancy_female":           safe_float(r.get("life_expectancy_female")),
            "life_expectancy_male":             safe_float(r.get("life_expectancy_male")),
            "le_gap_years":                     safe_float(r.get("le_gap_years")),
            "maternal_mortality_per_100k":      safe_float(r.get("maternal_mortality_per_100k")),
            "girls_primary_enrollment_pct":     safe_float(r.get("girls_primary_enrollment_pct")),
            "girls_secondary_enrollment_pct":   safe_float(r.get("girls_secondary_enrollment_pct")),
            "women_tertiary_enrollment_pct":    safe_float(r.get("women_tertiary_enrollment_pct")),
            "child_marriage_rate_pct":          safe_float(r.get("child_marriage_rate_pct")),
            "fertility_rate":                   safe_float(r.get("fertility_rate")),
            "female_poverty_rate_pct":          safe_float(r.get("female_poverty_rate_pct")),
            "male_poverty_rate_pct":            safe_float(r.get("male_poverty_rate_pct")),
            "gender_poverty_gap_pct":           safe_float(r.get("gender_poverty_gap_pct")),
            "gender_wealth_gap_pct":            safe_float(r.get("gender_wealth_gap_pct")),
            "women_killed_by_partner_per_100k": safe_float(r.get("women_killed_by_partner_per_100k")),
            "female_labour_force_pct":          safe_float(r.get("female_labour_force_pct")),
            "gender_wage_gap_pct":              safe_float(r.get("gender_wage_gap_pct")),
            "women_with_bank_account_pct":      safe_float(r.get("women_with_bank_account_pct")),
            # Weekly estimates
            "girls_born_per_week_est":              safe_int(r.get("girls_born_per_week_est")),
            "maternal_deaths_per_week_est":         safe_int(r.get("maternal_deaths_per_week_est")),
            "girls_drop_out_school_per_week_est":   safe_int(r.get("girls_drop_out_school_per_week_est")),
            "girls_married_under18_per_week_est":   safe_int(r.get("girls_married_under18_per_week_est")),
            "women_killed_by_partner_per_week_est": safe_int(r.get("women_killed_by_partner_per_week_est")),
        } for r in rows]
    all_rows = cached("vital_stats", _load)
    if iso_code:
        all_rows = [r for r in all_rows if r["iso_code"].upper() == iso_code.upper()]
    return all_rows


def get_gpi(iso_code: str = None) -> list[dict]:
    """Load Gender Poverty Index by country."""
    def _load():
        path = DATA_DIR / "gender-poverty-index-2025.csv"
        rows = load_csv(path)
        return [{
            "rank":                         safe_int(r.get("rank")),
            "country":                      r.get("country",""),
            "iso_code":                     r.get("iso_code",""),
            "region":                       r.get("region",""),
            "gpi_score":                    safe_float(r.get("gpi_score")),
            "gpi_income_poverty":           safe_float(r.get("gpi_income_poverty")),
            "gpi_wealth":                   safe_float(r.get("gpi_wealth")),
            "gpi_wage":                     safe_float(r.get("gpi_wage")),
            "gpi_labour_participation":     safe_float(r.get("gpi_labour_participation")),
            "gpi_financial_inclusion":      safe_float(r.get("gpi_financial_inclusion")),
            "gpi_food_security":            safe_float(r.get("gpi_food_security")),
            "gpi_time_poverty":             safe_float(r.get("gpi_time_poverty")),
            "gpi_land_ownership":           safe_float(r.get("gpi_land_ownership")),
            "gpi_social_protection":        safe_float(r.get("gpi_social_protection")),
            "income_poverty_ratio_f_to_m":  safe_float(r.get("income_poverty_ratio_f_to_m")),
            "wealth_ratio_f_to_m_pct":      safe_float(r.get("wealth_ratio_f_to_m_pct")),
            "wage_ratio_f_to_m_pct":        safe_float(r.get("wage_ratio_f_to_m_pct")),
            "food_insecurity_gap_pct":      safe_float(r.get("food_insecurity_gap_pct")),
            "unpaid_care_hours_ratio_f_to_m": safe_float(r.get("unpaid_care_hours_ratio_f_to_m")),
            "female_land_ownership_pct":    safe_float(r.get("female_land_ownership_pct")),
        } for r in rows]
    all_rows = cached("gpi", _load)
    if iso_code:
        all_rows = [r for r in all_rows if r["iso_code"].upper() == iso_code.upper()]
    return all_rows


def get_global_weekly_counters() -> dict:
    """Load global weekly vital statistics counters."""
    def _load():
        import json
        path = DATA_DIR / "global-vital-weekly.json"
        if not path.exists(): return {}
        with open(path,"r",encoding="utf-8") as f:
            return json.load(f)
    return cached("weekly_counters", _load)


def get_history_gpi() -> list[dict]:
    def _load():
        path = DATA_DIR / "historical" / "gpi-country-trends.csv"
        if not path.exists(): return []
        rows = load_csv(path)
        return [{"iso_code":r.get("iso_code",""),"country":r.get("country",""),
                 "year":safe_int(r.get("year")),"gpi_score":safe_float(r.get("gpi_score")),
                 "rank":safe_int(r.get("rank")),
                 **{k:safe_float(r.get(k)) for k in
                    ["gpi_income_poverty","gpi_wealth","gpi_wage",
                     "gpi_labour_participation","gpi_financial_inclusion",
                     "gpi_food_security","gpi_time_poverty",
                     "gpi_land_ownership","gpi_social_protection"]}
                } for r in rows]
    return cached("history_gpi", _load)


def get_history_usa_states() -> list[dict]:
    def _load():
        path = DATA_DIR / "historical" / "usa-state-trends.csv"
        if not path.exists(): return []
        rows = load_csv(path)
        return [{"state":r.get("state",""),"state_code":r.get("state_code",""),
                 "ticker":r.get("ticker",""),"year":safe_int(r.get("year")),
                 "wei_score":safe_float(r.get("wei_score")),
                 "rank":safe_int(r.get("rank")),
                 "bodily_autonomy_score":safe_float(r.get("bodily_autonomy_score")),
                 "safety_justice_score":safe_float(r.get("safety_justice_score")),
                 "economic_score":safe_float(r.get("economic_score")),
                 "health_score":safe_float(r.get("health_score")),
                } for r in rows]
    return cached("history_usa", _load)


def get_history_cities() -> list[dict]:
    def _load():
        path = DATA_DIR / "historical" / "city-trends-top20.csv"
        if not path.exists(): return []
        rows = load_csv(path)
        return [{"city":r.get("city",""),"slug":r.get("slug",""),
                 "country_iso":r.get("country_iso",""),
                 "year":safe_int(r.get("year")),
                 "wei_score":safe_float(r.get("wei_score")),
                 "rank":safe_int(r.get("rank")),
                 "bodily_autonomy_score":safe_float(r.get("bodily_autonomy_score")),
                 "safety_justice_score":safe_float(r.get("safety_justice_score")),
                 "economic_score":safe_float(r.get("economic_score")),
                } for r in rows]
    return cached("history_cities", _load)


def get_history_svi(iso_code: str = None) -> list[dict]:
    def _load():
        path = DATA_DIR / "historical" / "svi-country-trends.csv"
        if not path.exists(): return []
        rows = load_csv(path)
        return [{"iso_code":r.get("iso_code",""),"country":r.get("country",""),
                 "year":safe_int(r.get("year")),"svi_score":safe_float(r.get("svi_score")),
                 "rank":safe_int(r.get("rank")),
                 "reporting_gap_pct":safe_float(r.get("reporting_gap_pct")),
                 "impunity_score":safe_float(r.get("impunity_score")),
                 "legal_framework_score":safe_float(r.get("legal_framework_score")),
                 "conflict_sv_risk_score":safe_float(r.get("conflict_sv_risk_score")),
                } for r in rows]
    all_rows = cached("history_svi", _load)
    if iso_code:
        all_rows = [r for r in all_rows if r["iso_code"].upper()==iso_code.upper()]
    return all_rows


def get_wadi(iso_code: str = None) -> list[dict]:
    """Load Women's AI Displacement Index."""
    def _load():
        import json as _json
        path = DATA_DIR / "ai-displacement-index-2025.csv"
        if not path.exists(): return []
        rows = load_csv(path)
        return [{
            "rank":        safe_int(r.get("rank")),
            "country":     r.get("country",""),
            "iso_code":    r.get("iso_code",""),
            "region":      r.get("region",""),
            "wadi_score":  safe_float(r.get("wadi_score")),
            "pct_female_workforce_in_high_risk_sectors":
                           safe_float(r.get("pct_female_workforce_in_high_risk_sectors")),
            "digital_skills_gap_score":
                           safe_float(r.get("digital_skills_gap_score")),
            "reskilling_access_score":
                           safe_float(r.get("reskilling_access_score")),
            "pct_women_in_ai_tech":
                           safe_float(r.get("pct_women_in_ai_tech")),
            "remote_work_access_pct":
                           safe_float(r.get("remote_work_access_pct")),
            "unemployment_coverage_pct":
                           safe_float(r.get("unemployment_coverage_pct")),
            "gig_worker_pct":safe_float(r.get("gig_worker_pct")),
            "ai_policy_gender_inclusion":
                           safe_float(r.get("ai_policy_gender_inclusion")),
            "notes":       r.get("notes",""),
        } for r in rows]
    all_rows = cached("wadi", _load)
    if iso_code:
        all_rows = [r for r in all_rows
                    if r["iso_code"].upper() == iso_code.upper()]
    return all_rows


def get_ai_occupations() -> dict:
    """Load high-risk occupation data."""
    def _load():
        import json as _json
        path = DATA_DIR / "ai-high-risk-occupations.json"
        if not path.exists(): return {}
        with open(path,"r",encoding="utf-8") as f:
            return _json.load(f)
    return cached("ai_occupations", _load)
