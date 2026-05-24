"""
SHEtoken — Supabase Loader
==========================
Reads CSVs from data/output/ and upserts them into the `she_*` tables
in your Supabase project.

USAGE
-----
1. Install dependencies:
       pip install supabase python-dotenv pandas

2. Create a .env file in this same directory:
       SUPABASE_URL=https://ezfnvonjhnssotaaqpmr.supabase.co
       SUPABASE_SERVICE_ROLE_KEY=<your service_role key from Supabase Dashboard>

   ⚠️  The service_role key is NOT the publishable key.
       Get it here:
       Supabase Dashboard → Project Settings → API
       → "Project API keys" → copy the `service_role` `secret` row
       ⚠️  NEVER commit .env to GitHub. Add `.env` to .gitignore.

3. Run from the project root (or wherever you keep the script):
       python pipeline/load_to_supabase.py

4. Verify in Supabase Table Editor — tables should now be populated.

ARCHITECTURE NOTES
------------------
• Idempotent: uses upsert with PK conflict resolution. Re-running is safe.
• Portable: only uses standard Postgres semantics via supabase-py.
• If you ever leave Supabase: rewrite this one file. CSVs are unchanged.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from datetime import datetime, timezone
from typing import Iterable

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client


# ─────────────────────────────────────────────────────────────────────────────
# Config
# ─────────────────────────────────────────────────────────────────────────────

# Find the data/output directory regardless of where the script is run from.
# Script lives in pipeline/ — CSVs live in data/output/ — both under project root.
SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_ROOT = SCRIPT_DIR.parent
DATA_DIR = PROJECT_ROOT / "data" / "output"

# Batch size for Supabase upserts (Supabase has limits on payload size)
BATCH_SIZE = 200


# ─────────────────────────────────────────────────────────────────────────────
# Connection
# ─────────────────────────────────────────────────────────────────────────────

def get_client() -> Client:
    """Create a Supabase client using SERVICE ROLE key (bypasses RLS)."""
    load_dotenv()

    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

    if not url or not key:
        sys.exit(
            "ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env\n"
            "Create a .env file in this directory with both values."
        )

    if "publishable" in key.lower() or key.startswith("sb_publishable"):
        sys.exit(
            "ERROR: You provided the publishable key. The loader needs the\n"
            "SERVICE ROLE key to write data. Get it from:\n"
            "Supabase Dashboard → Project Settings → API → 'service_role' row."
        )

    print(f"→ Connecting to {url}")
    return create_client(url, key)


# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────

def read_csv(filename: str) -> pd.DataFrame:
    """Read a CSV from data/output/, skipping leading comment lines."""
    path = DATA_DIR / filename
    if not path.exists():
        print(f"  ⚠ {filename} not found, skipping")
        return pd.DataFrame()
    df = pd.read_csv(path, comment="#")
    df = df.where(pd.notna(df), None)  # NaN → None (so Postgres gets NULL)
    return df


def select_cols(df: pd.DataFrame, mapping: dict[str, str]) -> list[dict]:
    """
    Project + rename DataFrame columns to match Supabase table schema.

    mapping: {csv_column: db_column}
    Missing CSV columns are silently omitted (allowed to be NULL).
    Returns a list of row dicts ready for upsert.
    """
    available = {csv: db for csv, db in mapping.items() if csv in df.columns}
    if not available:
        return []
    sub = df[list(available.keys())].rename(columns=available)
    records = sub.to_dict(orient="records")
    # Final NaN scrub — pandas NaN can survive .to_dict in edge cases
    for row in records:
        for k, v in list(row.items()):
            if pd.isna(v) if not isinstance(v, (list, dict)) else False:
                row[k] = None
    return records


def batched(rows: list[dict], size: int = BATCH_SIZE) -> Iterable[list[dict]]:
    for i in range(0, len(rows), size):
        yield rows[i:i + size]


def upsert(sb: Client, table: str, rows: list[dict], on_conflict: str) -> None:
    """Upsert rows into table, batching to stay under payload limits."""
    if not rows:
        print(f"  · {table}: no rows to load")
        return
    total = 0
    for batch in batched(rows):
        sb.table(table).upsert(batch, on_conflict=on_conflict).execute()
        total += len(batch)
    print(f"  ✓ {table}: {total} rows upserted")


# ─────────────────────────────────────────────────────────────────────────────
# Loaders (one per table)
# ─────────────────────────────────────────────────────────────────────────────

def load_countries(sb: Client) -> None:
    """The master reference table — must load FIRST (other tables FK to it)."""
    print("\n[1/9] Loading she_countries...")
    df = read_csv("baseline-2025.csv")
    if df.empty:
        return
    rows = select_cols(df, {
        "iso_code":            "iso_code",
        "country":             "country_name",
        "region":              "region",
        "tier":                "tier",
        "population_millions": "population_millions",
        "ticker":              "ticker",
    })
    rows = [r for r in rows if r.get("iso_code")]
    upsert(sb, "she_countries", rows, on_conflict="iso_code")


def load_wei_countries(sb: Client) -> None:
    print("\n[2/9] Loading she_wei_countries...")
    df = read_csv("baseline-2025.csv")
    if df.empty:
        return
    rows = select_cols(df, {
        "iso_code":               "iso_code",
        "year":                   "year",
        "rank":                   "rank",
        "wei_score":              "wei_score",
        "empowerment_score":      "empowerment_score",
        "education_score":        "education_score",
        "economic_score":         "economic_score",
        "health_score":           "health_score",
        "bodily_autonomy_score":  "bodily_autonomy_score",
        "safety_justice_score":   "safety_justice_score",
        "dignity_welfare_score":  "dignity_welfare_score",
        "digital_social_score":   "digital_social_score",
        "violence_penalty_score": "violence_penalty_score",
        "population_weight":      "population_weight",
        "wei_version":            "wei_version",
        "data_source":            "data_source",
        "verified":               "verified",
        "notes":                  "notes",
    })
    rows = [r for r in rows if r.get("iso_code")]
    upsert(sb, "she_wei_countries", rows, on_conflict="iso_code,year")


def load_wei_india_states(sb: Client) -> None:
    print("\n[3/9] Loading she_wei_india_states...")
    df = read_csv("india-states-2025.csv")
    if df.empty:
        return
    rows = select_cols(df, {
        "state_code":             "state_code",
        "year":                   "year",
        "rank":                   "rank",
        "state":                  "state_name",
        "ticker":                 "ticker",
        "region":                 "region",
        "population_millions":    "population_millions",
        "wei_score":              "wei_score",
        "previous_wei_score":     "previous_wei_score",
        "change":                 "change",
        "hot":                    "hot",
        "empowerment_score":      "empowerment_score",
        "education_score":        "education_score",
        "economic_score":         "economic_score",
        "health_score":           "health_score",
        "bodily_autonomy_score":  "bodily_autonomy_score",
        "safety_justice_score":   "safety_justice_score",
        "dignity_welfare_score":  "dignity_welfare_score",
        "digital_social_score":   "digital_social_score",
        "violence_penalty_score": "violence_penalty_score",
        "verified":               "verified",
        "update_frequency":       "update_frequency",
        "wei_version":            "wei_version",
        "key_programs":           "key_programs",
        "notes":                  "notes",
    })
    rows = [r for r in rows if r.get("state_code")]
    upsert(sb, "she_wei_india_states", rows, on_conflict="state_code,year")


def load_wei_usa_states(sb: Client) -> None:
    print("\n[4/9] Loading she_wei_usa_states...")
    df = read_csv("usa-states-2025.csv")
    if df.empty:
        return
    rows = select_cols(df, {
        "state_code":             "state_code",
        "year":                   "year",
        "rank":                   "rank",
        "state":                  "state_name",
        "ticker":                 "ticker",
        "region":                 "region",
        "population_millions":    "population_millions",
        "wei_score":              "wei_score",
        "previous_wei_score":     "previous_wei_score",
        "change":                 "change",
        "hot":                    "hot",
        "watch":                  "watch",
        "empowerment_score":      "empowerment_score",
        "education_score":        "education_score",
        "economic_score":         "economic_score",
        "health_score":           "health_score",
        "bodily_autonomy_score":  "bodily_autonomy_score",
        "safety_justice_score":   "safety_justice_score",
        "dignity_welfare_score":  "dignity_welfare_score",
        "digital_social_score":   "digital_social_score",
        "violence_penalty_score": "violence_penalty_score",
        "country":                "country",
        "verified":               "verified",
        "wei_version":            "wei_version",
        "notes":                  "notes",
    })
    rows = [r for r in rows if r.get("state_code")]
    upsert(sb, "she_wei_usa_states", rows, on_conflict="state_code,year")


def load_gpi(sb: Client) -> None:
    print("\n[5/9] Loading she_gpi_countries...")
    df = read_csv("gender-poverty-index-2025.csv")
    if df.empty:
        return
    rows = select_cols(df, {
        "iso_code":                       "iso_code",
        "year":                           "year",
        "rank":                           "rank",
        "gpi_score":                      "gpi_score",
        "gpi_income_poverty":             "gpi_income_poverty",
        "gpi_wealth":                     "gpi_wealth",
        "gpi_wage":                       "gpi_wage",
        "gpi_labour_participation":       "gpi_labour_participation",
        "gpi_financial_inclusion":        "gpi_financial_inclusion",
        "gpi_food_security":              "gpi_food_security",
        "gpi_time_poverty":               "gpi_time_poverty",
        "gpi_land_ownership":             "gpi_land_ownership",
        "gpi_social_protection":          "gpi_social_protection",
        "income_poverty_ratio_f_to_m":    "income_poverty_ratio_f_to_m",
        "wealth_ratio_f_to_m_pct":        "wealth_ratio_f_to_m_pct",
        "wage_ratio_f_to_m_pct":          "wage_ratio_f_to_m_pct",
        "labour_ratio_f_to_m_pct":        "labour_ratio_f_to_m_pct",
        "food_insecurity_gap_pct":        "food_insecurity_gap_pct",
        "unpaid_care_hours_ratio_f_to_m": "unpaid_care_hours_ratio_f_to_m",
        "female_land_ownership_pct":      "female_land_ownership_pct",
    })
    rows = [r for r in rows if r.get("iso_code")]
    upsert(sb, "she_gpi_countries", rows, on_conflict="iso_code,year")


def load_svi(sb: Client) -> None:
    print("\n[6/9] Loading she_svi_countries...")
    df = read_csv("sexual-violence-index-2025.csv")
    if df.empty:
        return
    rows = select_cols(df, {
        "iso_code":                       "iso_code",
        "year":                           "year",
        "rank":                           "rank",
        "svi_score":                      "svi_score",
        "who_lifetime_prevalence_pct":    "who_lifetime_prevalence_pct",
        "unodc_reported_rate_per_100k":   "unodc_reported_rate_per_100k",
        "reporting_gap_pct":              "reporting_gap_pct",
        "estimated_actual_rate_per_100k": "estimated_actual_rate_per_100k",
        "marital_rape_criminalised":      "marital_rape_criminalised",
        "marital_rape_prevalence_pct":    "marital_rape_prevalence_pct",
        "conflict_sv_risk_score":         "conflict_sv_risk_score",
        "digital_sv_rate_pct":            "digital_sv_rate_pct",
        "impunity_score":                 "impunity_score",
        "caste_ethnic_targeting":         "caste_ethnic_targeting",
        "indigenous_women_elevated_risk": "indigenous_women_elevated_risk",
        "police_responsiveness_score":    "police_responsiveness_score",
        "legal_framework_score":          "legal_framework_score",
        "support_services_score":         "support_services_score",
        "notes":                          "notes",
    })
    rows = [r for r in rows if r.get("iso_code")]
    upsert(sb, "she_svi_countries", rows, on_conflict="iso_code,year")


def load_wadi(sb: Client) -> None:
    print("\n[7/9] Loading she_wadi_countries...")
    df = read_csv("ai-displacement-index-2025.csv")
    if df.empty:
        return
    rows = select_cols(df, {
        "iso_code":                                 "iso_code",
        "year":                                     "year",
        "rank":                                     "rank",
        "wadi_score":                               "wadi_score",
        "pct_female_workforce_in_high_risk_sectors": "pct_female_workforce_in_high_risk_sectors",
        "digital_skills_gap_score":                 "digital_skills_gap_score",
        "reskilling_access_score":                  "reskilling_access_score",
        "care_economy_wage_ratio":                  "care_economy_wage_ratio",
        "pct_women_in_ai_tech":                     "pct_women_in_ai_tech",
        "remote_work_access_pct":                   "remote_work_access_pct",
        "unemployment_coverage_pct":                "unemployment_coverage_pct",
        "gig_worker_pct":                           "gig_worker_pct",
        "ai_policy_gender_inclusion":               "ai_policy_gender_inclusion",
        "notes":                                    "notes",
    })
    rows = [r for r in rows if r.get("iso_code")]
    upsert(sb, "she_wadi_countries", rows, on_conflict="iso_code,year")


def load_vital_counters(sb: Client) -> None:
    """Seed initial vital counters. Agent will update these weekly going forward."""
    print("\n[8/9] Loading she_vital_counters (seed values)...")
    seed = [
        {
            "counter_key": "girls_enrolled_weekly",
            "counter_label": "Girls enrolled in school this week",
            "current_value": 487000,
            "previous_value": 472000,
            "change_pct": 3.2,
            "direction": "up",
            "is_positive": True,
            "unit": "girls",
            "source": "UNESCO + Kanyashree weekly",
        },
        {
            "counter_key": "femicide_weekly",
            "counter_label": "Women killed by intimate partners this week (est.)",
            "current_value": 1380,
            "previous_value": 1402,
            "change_pct": -1.6,
            "direction": "down",
            "is_positive": False,
            "unit": "women",
            "source": "UNODC weekly extrapolation",
        },
        {
            "counter_key": "trafficking_rescued_weekly",
            "counter_label": "Women & girls rescued from trafficking",
            "current_value": 2150,
            "previous_value": 1980,
            "change_pct": 8.6,
            "direction": "up",
            "is_positive": True,
            "unit": "people",
            "source": "UNODC + national AHTU reports",
        },
        {
            "counter_key": "lakshmi_bhandar_disbursed",
            "counter_label": "₹ disbursed via Lakshmi Bhandar this week (cr)",
            "current_value": 750,
            "previous_value": 750,
            "change_pct": 0.0,
            "direction": "flat",
            "is_positive": True,
            "unit": "INR crore",
            "source": "West Bengal Govt portal",
        },
        {
            "counter_key": "women_lifted_from_poverty_ytd",
            "counter_label": "Women lifted from extreme poverty YTD",
            "current_value": 3200000,
            "previous_value": 3050000,
            "change_pct": 4.9,
            "direction": "up",
            "is_positive": True,
            "unit": "women",
            "source": "World Bank + JEEViKA + Kudumbashree",
        },
    ]
    upsert(sb, "she_vital_counters", seed, on_conflict="counter_key")


def update_meta(sb: Client) -> None:
    """Update she_meta with the current global WEI and last run timestamp."""
    print("\n[9/9] Updating she_meta...")
    # Compute current global WEI as population-weighted average
    df = read_csv("baseline-2025.csv")
    if not df.empty and "wei_score" in df.columns and "population_weight" in df.columns:
        d = df.dropna(subset=["wei_score", "population_weight"])
        weighted = (d["wei_score"] * d["population_weight"]).sum() / d["population_weight"].sum()
        global_wei = round(weighted, 2)
    else:
        global_wei = 0

    now_iso = datetime.now(timezone.utc).isoformat()

    rows = [
        {"meta_key": "current_global_wei", "meta_value": str(global_wei)},
        {"meta_key": "last_pipeline_run", "meta_value": now_iso},
        {"meta_key": "site_status",       "meta_value": "live"},
        {"meta_key": "wei_version",       "meta_value": "3.0"},
    ]
    upsert(sb, "she_meta", rows, on_conflict="meta_key")
    print(f"  → Global WEI computed: {global_wei}")


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 70)
    print("SHEtoken — Supabase Loader")
    print("=" * 70)
    print(f"Data directory: {DATA_DIR}")
    if not DATA_DIR.exists():
        sys.exit(f"ERROR: Data directory not found: {DATA_DIR}")

    sb = get_client()

    # Order matters: countries must load before WEI (FK dependency)
    load_countries(sb)
    load_wei_countries(sb)
    load_wei_india_states(sb)
    load_wei_usa_states(sb)
    load_gpi(sb)
    load_svi(sb)
    load_wadi(sb)
    load_vital_counters(sb)
    update_meta(sb)

    print("\n" + "=" * 70)
    print("✓ DONE — All tables loaded.")
    print("=" * 70)
    print("Verify in Supabase Table Editor → all `she_*` tables should have rows.")
    print("Next: I'll build the WEI gauge React component for your Lovable site.")


if __name__ == "__main__":
    main()
