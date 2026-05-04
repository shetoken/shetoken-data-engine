"""
SHEtoken Pipeline — Indicator Normalisation
============================================
Reads all raw data files, merges them, and normalises
every indicator to a 0–100 scale for WEI calculation.

Usage:
    python data/process/normalise.py

Input:
    data/raw/world_bank_raw.csv
    data/raw/who_raw.csv
    data/raw/ilo_raw.csv
    data/raw/ipu_raw.csv
    data/raw/unesco_raw.csv
    data/raw/ncrb_raw.csv          (India only)
    data/manual/un_women_manual.csv
    data/manual/oecd_sigi_manual.csv

Output:
    data/processed/normalised_global.csv
    data/processed/normalised_india_states.csv
"""

import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config import (
    RAW_DIR, PROCESSED_DIR, MANUAL_DIR,
    SCORED_COUNTRIES, INDIA_STATES, INVERTED_INDICATORS
)


# ── NORMALISATION ─────────────────────────────────────────────────────────────

def normalise(series, invert=False, min_val=None, max_val=None):
    """
    Normalise a pandas Series to 0–100 scale.

    Uses observed min/max from the series unless overridden.
    Inverts the scale for indicators where higher = worse.

    Args:
        series (pd.Series): Raw indicator values
        invert (bool): True if higher value = worse outcome
        min_val (float): Override minimum (worst value)
        max_val (float): Override maximum (best value)

    Returns:
        pd.Series: Normalised values 0–100
    """
    s = pd.to_numeric(series, errors="coerce")

    lo = min_val if min_val is not None else s.min()
    hi = max_val if max_val is not None else s.max()

    if hi == lo:
        return pd.Series([50.0] * len(s), index=s.index)

    normalised = (s - lo) / (hi - lo) * 100

    if invert:
        normalised = 100 - normalised

    return normalised.clip(0, 100).round(1)


# ── INDICATOR NORMALISTION RULES ──────────────────────────────────────────────
# Each entry: (column_name, invert, min_override, max_override, description)
# min/max overrides are used for indicators with known theoretical bounds

NORMALISATION_RULES = [

    # ── Empowerment indicators ────────────────────────────────────────────────
    ("ipu_parliament_female_pct",        False, 0,    100,  "Women in parliament (%)"),
    ("wb_parliament_female_pct",         False, 0,    100,  "Women in parliament WB (%)"),
    ("wb_women_business_law_index",      False, 0,    100,  "Women Business & Law score"),
    ("wb_senior_mgmt_female_pct",        False, 0,    100,  "Women in senior management"),
    ("manual_ministerial_female_pct",    False, 0,    100,  "Women in ministerial roles"),
    ("manual_freedom_movement_score",    False, 0,    100,  "Freedom of movement score"),

    # ── Education indicators ──────────────────────────────────────────────────
    ("wb_literacy_female",               False, 0,    100,  "Female literacy rate (%)"),
    ("unesco_literacy_female",           False, 0,    100,  "Female literacy UNESCO (%)"),
    ("wb_primary_enrollment_female",     False, 0,    100,  "Female primary enrollment"),
    ("wb_secondary_enrollment_female",   False, 0,    100,  "Female secondary enrollment"),
    ("wb_tertiary_enrollment_female",    False, 0,    100,  "Female tertiary enrollment"),
    ("unesco_secondary_enrollment_female",False,0,   100,  "Secondary enrollment UNESCO"),
    ("manual_stem_female_pct",           False, 0,    100,  "Female STEM participation"),

    # ── Economic indicators ───────────────────────────────────────────────────
    ("ilo_lfpr_female",                  False, 0,    100,  "Female LFPR (%)"),
    ("wb_lfpr_female",                   False, 0,    100,  "Female LFPR World Bank (%)"),
    ("wb_account_ownership_female",      False, 0,    100,  "Women with bank account (%)"),
    ("ilo_wage_gap_pct",                 True,  0,    100,  "Gender wage gap (% inverted)"),
    ("manual_property_rights_score",     False, 0,    100,  "Property rights score"),
    ("wb_wage_equality_index",           False, 0,    100,  "Wage equality index"),
    ("manual_women_business_pct",        False, 0,    100,  "Women-owned businesses (%)"),

    # ── Health indicators ─────────────────────────────────────────────────────
    ("wb_maternal_mortality",            True,  0,   2000,  "Maternal mortality (inverted)"),
    ("who_maternal_mortality",           True,  0,   2000,  "Maternal mortality WHO (inv)"),
    ("wb_life_expectancy_female",        False, 40,   90,   "Female life expectancy"),
    ("who_life_expectancy_female",       False, 40,   90,   "Female life expectancy WHO"),
    ("wb_adolescent_birth_rate",         True,  0,   200,   "Adolescent birth rate (inv)"),
    ("wb_skilled_birth_attendant",       False, 0,   100,   "Skilled birth attendants (%)"),
    ("who_skilled_birth_attendant",      False, 0,   100,   "Skilled birth attendants WHO"),
    ("manual_female_survival_ratio",     False, 0,   100,   "Female survival ratio"),

    # ── Crime / Safety indicators ─────────────────────────────────────────────
    ("unodc_rape_rate",                  True,  0,   200,   "Rape rate per 100K (inv)"),
    ("who_dv_prevalence",                True,  0,   100,   "DV prevalence (inv)"),
    ("manual_dv_prevalence",             True,  0,   100,   "DV prevalence manual (inv)"),
    ("unodc_femicide_rate",              True,  0,    20,   "Femicide rate (inv)"),
    ("unodc_trafficking_rate",           True,  0,    10,   "Trafficking rate (inv)"),
    ("manual_acid_attacks_rate",         True,  0,     5,   "Acid attacks rate (inv)"),

    # ── India NCRB indicators (states only) ───────────────────────────────────
    ("ncrb_rape_rate_per_100k",          True,  0,   100,   "NCRB rape rate (inv)"),
    ("ncrb_dv_cases_rate_per_100k",      True,  0,   200,   "NCRB DV rate (inv)"),
    ("ncrb_dowry_deaths_rate_per_100k",  True,  0,    10,   "NCRB dowry deaths (inv)"),
    ("ncrb_acid_attacks_rate_per_100k",  True,  0,     5,   "NCRB acid attacks (inv)"),
    ("ncrb_trafficking_rate_per_100k",   True,  0,    10,   "NCRB trafficking (inv)"),
]


# ── MERGE RAW DATA ────────────────────────────────────────────────────────────

def load_raw_file(filename, key_col="iso_code"):
    """Load a raw CSV file if it exists, else return empty DataFrame."""
    path = RAW_DIR / filename
    if path.exists():
        df = pd.read_csv(path)
        print(f"  ✓ Loaded {filename}: {len(df)} rows, {len(df.columns)} cols")
        return df
    else:
        print(f"  ⚠ Not found: {filename} (run fetch scripts first)")
        return pd.DataFrame(columns=[key_col])


def load_manual_file(filename, key_col="iso_code"):
    """Load a manual CSV file if it exists."""
    path = MANUAL_DIR / filename
    if path.exists():
        df = pd.read_csv(path)
        # Prefix all non-key columns with 'manual_'
        rename = {
            c: f"manual_{c}" for c in df.columns
            if c != key_col and not c.startswith("manual_")
        }
        df = df.rename(columns=rename)
        print(f"  ✓ Loaded manual/{filename}: {len(df)} rows")
        return df
    else:
        print(f"  ⚠ Not found: manual/{filename}")
        return pd.DataFrame(columns=[key_col])


def merge_global_data(countries=SCORED_COUNTRIES):
    """
    Merge all raw sources into a single global DataFrame.

    Returns:
        pd.DataFrame: Merged raw data, one row per country
    """
    print("\nMerging global data sources...")

    base = pd.DataFrame({"iso_code": countries})

    sources = [
        load_raw_file("world_bank_raw.csv"),
        load_raw_file("who_raw.csv"),
        load_raw_file("ilo_raw.csv"),
        load_raw_file("ipu_raw.csv"),
        load_raw_file("unesco_raw.csv"),
    ]

    manual_sources = [
        load_manual_file("un_women_manual.csv"),
        load_manual_file("oecd_sigi_manual.csv"),
    ]

    df = base.copy()
    for src in sources + manual_sources:
        if src.empty or "iso_code" not in src.columns:
            continue
        df = df.merge(src, on="iso_code", how="left")

    print(f"\n  Merged: {len(df)} countries × {len(df.columns)} columns")
    return df


def merge_india_state_data():
    """
    Merge India-specific state data sources.

    Returns:
        pd.DataFrame: Merged state data
    """
    print("\nMerging India state data sources...")

    base = pd.DataFrame({
        "state_code": list(INDIA_STATES.keys()),
        "state_name": list(INDIA_STATES.values()),
    })

    ncrb = load_raw_file("ncrb_raw.csv", key_col="state_code")
    if not ncrb.empty and "state_code" in ncrb.columns:
        # Prefix NCRB columns
        rename = {c: f"ncrb_{c}" for c in ncrb.columns if c != "state_code"}
        ncrb = ncrb.rename(columns=rename)
        base = base.merge(ncrb, on="state_code", how="left")

    manual_ncrb = load_manual_file("ncrb_manual_template.csv", key_col="state_code")
    if not manual_ncrb.empty and "state_code" in manual_ncrb.columns:
        base = base.merge(manual_ncrb, on="state_code", how="left")

    print(f"  Merged: {len(base)} states × {len(base.columns)} columns")
    return base


# ── APPLY NORMALISATION ───────────────────────────────────────────────────────

def apply_normalisation(df):
    """
    Apply normalisation rules to all indicator columns.

    Adds a normalised column (suffix _norm) for each raw indicator found.

    Returns:
        pd.DataFrame with _norm columns added
    """
    print("\nApplying normalisation...")
    normed_count = 0

    for col, invert, min_v, max_v, desc in NORMALISATION_RULES:
        if col not in df.columns:
            continue

        norm_col = f"{col}_norm"
        df[norm_col] = normalise(df[col], invert=invert,
                                 min_val=min_v, max_val=max_v)
        normed_count += 1

        coverage = df[norm_col].notna().sum()
        pct = round(coverage / len(df) * 100)
        print(f"  ✓ {col:<45} → {pct:3d}% coverage")

    print(f"\n  Normalised: {normed_count} indicators")
    return df


# ── MAIN ──────────────────────────────────────────────────────────────────────

def main():
    print("SHEtoken — Data Normalisation")
    print("=" * 60)

    # Global data
    global_df = merge_global_data()
    global_df = apply_normalisation(global_df)

    out_global = PROCESSED_DIR / "normalised_global.csv"
    global_df.to_csv(out_global, index=False)
    print(f"\n✓ Saved: {out_global}")
    print(f"  {len(global_df)} countries × {len(global_df.columns)} columns")

    # India states
    india_df = merge_india_state_data()
    india_df = apply_normalisation(india_df)

    out_india = PROCESSED_DIR / "normalised_india_states.csv"
    india_df.to_csv(out_india, index=False)
    print(f"\n✓ Saved: {out_india}")
    print(f"  {len(india_df)} states × {len(india_df.columns)} columns")

    # Coverage summary
    print("\n" + "=" * 60)
    print("COVERAGE SUMMARY")
    print("=" * 60)
    norm_cols = [c for c in global_df.columns if c.endswith("_norm")]
    for col in norm_cols:
        filled = global_df[col].notna().sum()
        total  = len(global_df)
        bar    = "█" * (filled * 20 // total) + "░" * (20 - filled * 20 // total)
        print(f"  {col.replace('_norm',''):<40} {bar} {filled}/{total}")


if __name__ == "__main__":
    main()
