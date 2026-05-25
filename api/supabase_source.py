"""
SHEtoken API — Supabase Source Layer
=====================================
Lets the FastAPI read index data from Supabase (the she_* tables), falling
back to the local CSVs if Supabase is unreachable. Used for the indexes that
previously had NO endpoint: SVI, WEVI, WHI, WVI.

Why Supabase-first with CSV fallback:
  • Supabase has every index (including the live weekly SVI/WVI) and is always
    reachable from Railway — fixes the "live files never reach Railway" gap.
  • CSV fallback means a momentary Supabase hiccup never takes the API down.

Reads use the publishable/anon key (these she_* tables are public-read).
Results are cached via data_loader.cached() so Supabase sees minimal traffic.
"""

from __future__ import annotations

import os
import logging

from data_loader import cached, load_csv, safe_float, safe_int, DATA_DIR

logger = logging.getLogger(__name__)

SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")


def _sb_rows(table: str, order: str | None = None) -> list[dict] | None:
    """Fetch all rows from a Supabase table via REST. Returns None on any failure."""
    if not SUPABASE_URL or not SUPABASE_KEY:
        return None
    try:
        import httpx
        params = {"select": "*"}
        if order:
            params["order"] = order
        resp = httpx.get(
            f"{SUPABASE_URL}/rest/v1/{table}",
            params=params,
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            timeout=4.0,
        )
        if resp.status_code == 200:
            return resp.json()
        logger.warning(f"supabase_source: {table} returned {resp.status_code}")
        return None
    except Exception as e:
        logger.warning(f"supabase_source: {table} fetch failed ({e})")
        return None


def _rows(table: str, csv_filename: str, order: str | None = "rank") -> list[dict]:
    """Supabase rows if available, else CSV rows. Same column names either way."""
    rows = _sb_rows(table, order=order)
    if rows is not None and len(rows) > 0:
        return rows
    return load_csv(DATA_DIR / csv_filename)


# ── The four previously-missing index getters ────────────────────────────────

def get_svi(iso_code: str | None = None) -> list[dict]:
    """Sexual Violence Index (main scores). Supabase she_svi_countries → CSV."""
    def _load():
        rows = _rows("she_svi_countries", "sexual-violence-index-2025.csv")
        return [{
            "rank":                          safe_int(r.get("rank")),
            "country":                       r.get("country", ""),
            "iso_code":                      r.get("iso_code", ""),
            "region":                        r.get("region", ""),
            "svi_score":                     safe_float(r.get("svi_score")),
            "who_lifetime_prevalence_pct":   safe_float(r.get("who_lifetime_prevalence_pct")),
            "unodc_reported_rate_per_100k":  safe_float(r.get("unodc_reported_rate_per_100k")),
            "reporting_gap_pct":             safe_float(r.get("reporting_gap_pct")),
            "estimated_actual_rate_per_100k": safe_float(r.get("estimated_actual_rate_per_100k")),
            "marital_rape_criminalised":     safe_int(r.get("marital_rape_criminalised")),
            "conflict_sv_risk_score":        safe_float(r.get("conflict_sv_risk_score")),
            "digital_sv_rate_pct":           safe_float(r.get("digital_sv_rate_pct")),
            "legal_framework_score":         safe_float(r.get("legal_framework_score")),
            "support_services_score":        safe_float(r.get("support_services_score")),
            "notes":                         r.get("notes", ""),
        } for r in rows]
    all_rows = cached("svi_main", _load)
    if iso_code:
        all_rows = [r for r in all_rows if r["iso_code"].upper() == iso_code.upper()]
    return all_rows


def get_wevi(iso_code: str | None = None) -> list[dict]:
    """Widow & Elderly Vulnerability Index. Supabase she_widow_elderly → CSV."""
    def _load():
        rows = _rows("she_widow_elderly", "widow-elderly-index-2025.csv")
        return [{
            "rank":                       safe_int(r.get("rank")),
            "country":                    r.get("country", ""),
            "iso_code":                   r.get("iso_code", ""),
            "region":                     r.get("region", ""),
            "wevi_score":                 safe_float(r.get("wevi_score")),
            "widow_population_millions":  safe_float(r.get("widow_population_millions")),
            "widows_in_poverty_pct":      safe_float(r.get("widows_in_poverty_pct")),
            "legal_inheritance_rights":   safe_int(r.get("legal_inheritance_rights")),
            "inheritance_enforcement":    safe_int(r.get("inheritance_enforcement")),
            "social_restrictions_score":  safe_float(r.get("social_restrictions_score")),
            "widow_abandonment_rate":     safe_float(r.get("widow_abandonment_rate")),
            "elderly_women_homeless_pct": safe_float(r.get("elderly_women_homeless_pct")),
            "pension_coverage_pct":       safe_float(r.get("pension_coverage_pct")),
            "elder_care_access_score":    safe_float(r.get("elder_care_access_score")),
            "notes":                      r.get("notes", ""),
        } for r in rows]
    all_rows = cached("wevi", _load)
    if iso_code:
        all_rows = [r for r in all_rows if r["iso_code"].upper() == iso_code.upper()]
    return all_rows


def get_whi(iso_code: str | None = None) -> list[dict]:
    """Women's Health Index. Supabase she_whi_countries → CSV."""
    def _load():
        rows = _rows("she_whi_countries", "womens-health-index-2025.csv")
        return [{
            "rank":                    safe_int(r.get("rank")),
            "country":                 r.get("country", ""),
            "iso_code":                r.get("iso_code", ""),
            "region":                  r.get("region", ""),
            "whi_score":               safe_float(r.get("whi_score")),
            "depression_prev_pct":     safe_float(r.get("depression_prev_pct")),
            "suicide_rate_per_100k":   safe_float(r.get("suicide_rate_per_100k")),
            "anaemia_pct":             safe_float(r.get("anaemia_pct")),
            "menstrual_access_pct":    safe_float(r.get("menstrual_access_pct")),
            "contraceptive_unmet_pct": safe_float(r.get("contraceptive_unmet_pct")),
            "maternal_mh_support":     safe_float(r.get("maternal_mh_support")),
            "data_source":             r.get("data_source", ""),
        } for r in rows]
    all_rows = cached("whi", _load)
    if iso_code:
        all_rows = [r for r in all_rows if r["iso_code"].upper() == iso_code.upper()]
    return all_rows


def get_wvi(iso_code: str | None = None) -> list[dict]:
    """Women's Voice Index. Supabase she_wvi_countries → CSV."""
    def _load():
        rows = _rows("she_wvi_countries", "womens-voice-index-2025.csv")
        return [{
            "rank":                 safe_int(r.get("rank")),
            "country":              r.get("country", ""),
            "iso_code":             r.get("iso_code", ""),
            "region":               r.get("region", ""),
            "wvi_score":            safe_float(r.get("wvi_score")),
            "online_gbv_pct":       safe_float(r.get("online_gbv_pct")),
            "media_leadership_pct": safe_float(r.get("media_leadership_pct")),
            "women_tech_pct":       safe_float(r.get("women_tech_pct")),
            "civil_society_score":  safe_float(r.get("civil_society_score")),
            "journalists_pct":      safe_float(r.get("journalists_pct")),
            "press_freedom_score":  safe_float(r.get("press_freedom_score")),
            "data_source":          r.get("data_source", ""),
        } for r in rows]
    all_rows = cached("wvi", _load)
    if iso_code:
        all_rows = [r for r in all_rows if r["iso_code"].upper() == iso_code.upper()]
    return all_rows
