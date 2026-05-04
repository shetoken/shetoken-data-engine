"""
SHEtoken Pipeline — Pillar Score Builder
=========================================
Reads normalised indicator data and combines indicators
into the five WEI pillar scores using weighted averages.

Usage:
    python data/process/build_pillars.py

Input:
    data/processed/normalised_global.csv
    data/processed/normalised_india_states.csv

Output:
    data/processed/pillar_scores_global.csv
    data/processed/pillar_scores_india_states.csv
"""

import pandas as pd
import numpy as np
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config import PROCESSED_DIR, PILLAR_INDICATOR_WEIGHTS


# ── PILLAR INDICATOR MAPPINGS ─────────────────────────────────────────────────
#
# Maps each pillar to its normalised indicator columns and weights.
# The pipeline tries each column in priority order and uses the first
# available value. If multiple are available, takes a weighted average.
#
# Format: [(column_suffix, weight_fraction)]
# Looks for column: {column_suffix}_norm in the dataframe

PILLAR_COLUMNS = {

    "empowerment": [
        # Column name (without _norm suffix),  weight within pillar
        ("ipu_parliament_female_pct",           0.30),
        ("wb_parliament_female_pct",            0.30),   # fallback
        ("manual_ministerial_female_pct",       0.20),
        ("wb_women_business_law_index",         0.25),
        ("manual_freedom_movement_score",       0.15),
        ("wb_senior_mgmt_female_pct",           0.10),
    ],

    "education": [
        ("wb_literacy_female",                  0.35),
        ("unesco_literacy_female",              0.35),   # fallback
        ("wb_primary_enrollment_female",        0.20),
        ("wb_secondary_enrollment_female",      0.20),
        ("unesco_secondary_enrollment_female",  0.20),  # fallback
        ("wb_tertiary_enrollment_female",       0.15),
        ("manual_stem_female_pct",              0.10),
    ],

    "economic": [
        ("ilo_lfpr_female",                     0.25),
        ("wb_lfpr_female",                      0.25),   # fallback
        ("wb_account_ownership_female",         0.20),
        ("ilo_wage_gap_pct",                    0.30),
        ("wb_wage_equality_index",              0.30),   # fallback
        ("manual_property_rights_score",        0.15),
        ("manual_women_business_pct",           0.10),
    ],

    "health": [
        ("wb_maternal_mortality",               0.35),
        ("who_maternal_mortality",              0.35),   # fallback
        ("wb_life_expectancy_female",           0.25),
        ("who_life_expectancy_female",          0.25),   # fallback
        ("wb_adolescent_birth_rate",            0.20),
        ("wb_skilled_birth_attendant",          0.10),
        ("who_skilled_birth_attendant",         0.10),   # fallback
        ("manual_female_survival_ratio",        0.10),
    ],

    "crime_penalty": [
        ("unodc_rape_rate",                     0.30),
        ("ncrb_rape_rate_per_100k",             0.30),   # India states
        ("who_dv_prevalence",                   0.25),
        ("manual_dv_prevalence",                0.25),   # fallback
        ("ncrb_dv_cases_rate_per_100k",         0.25),   # India states
        ("unodc_femicide_rate",                 0.20),
        ("unodc_trafficking_rate",              0.15),
        ("ncrb_trafficking_rate_per_100k",      0.15),   # India states
        ("manual_acid_attacks_rate",            0.10),
        ("ncrb_acid_attacks_rate_per_100k",     0.10),   # India states
    ],
}


def build_pillar_score(df, pillar_name, indicator_list):
    """
    Build a single pillar score from available normalised indicators.

    Strategy:
    - For each indicator, check if the _norm column exists and has data
    - Use available indicators, re-normalising weights to sum to 1.0
    - If no indicators available, return NaN

    Args:
        df (pd.DataFrame): DataFrame with normalised indicator columns
        pillar_name (str): Name of the pillar
        indicator_list (list): [(col_name, weight), ...]

    Returns:
        pd.Series: Pillar scores 0–100
    """
    # Collect available normalised columns and their weights
    available = []
    for col, weight in indicator_list:
        norm_col = f"{col}_norm"
        if norm_col in df.columns:
            coverage = df[norm_col].notna().sum()
            if coverage > 0:
                available.append((norm_col, weight))

    if not available:
        print(f"  ⚠ {pillar_name}: no indicators available — pillar will be NaN")
        return pd.Series([np.nan] * len(df), index=df.index)

    # Deduplicate — if both primary and fallback available, use primary
    seen_purposes = {}
    deduped = []
    for col, weight in available:
        # Group primary/fallback by stripping source prefix
        purpose = col.replace("wb_", "").replace("who_", "").replace(
            "ilo_", "").replace("ipu_", "").replace(
            "unesco_", "").replace("manual_", "").replace(
            "ncrb_", "").replace("unodc_", "").replace("_norm", "")
        if purpose not in seen_purposes:
            seen_purposes[purpose] = True
            deduped.append((col, weight))

    available = deduped

    # Re-normalise weights to sum to 1.0
    total_weight = sum(w for _, w in available)
    if total_weight == 0:
        return pd.Series([np.nan] * len(df), index=df.index)

    # Compute weighted average (row-wise, ignoring NaN)
    result = pd.Series([0.0] * len(df), index=df.index)
    weight_used = pd.Series([0.0] * len(df), index=df.index)

    for col, weight in available:
        normalised_weight = weight / total_weight
        series = df[col]
        mask = series.notna()
        result[mask] += series[mask] * normalised_weight
        weight_used[mask] += normalised_weight

    # Where weight_used < 0.3, we have very sparse data — flag it
    sparse_mask = (weight_used > 0) & (weight_used < 0.3)
    if sparse_mask.sum() > 0:
        print(f"  ⚠ {pillar_name}: {sparse_mask.sum()} rows have sparse data (<30% weight coverage)")

    # Set NaN where no data at all
    result[weight_used == 0] = np.nan

    # Re-scale to 0–100 if needed
    result = result.clip(0, 100).round(1)

    used_cols = [c for c, _ in available]
    print(f"  ✓ {pillar_name:<20} using {len(used_cols)} indicators: {used_cols[:3]}{'...' if len(used_cols) > 3 else ''}")

    return result


def build_all_pillars(df):
    """
    Build all five pillar scores for a DataFrame.

    Args:
        df (pd.DataFrame): DataFrame with normalised indicator columns

    Returns:
        pd.DataFrame with pillar score columns added
    """
    for pillar, indicators in PILLAR_COLUMNS.items():
        col_name = f"pillar_{pillar}"
        df[col_name] = build_pillar_score(df, pillar, indicators)

    return df


def calculate_wei(df):
    """
    Apply the WEI formula to pillar scores.

    WEI = (Empowerment × 0.25) + (Education × 0.20)
        + (Economic × 0.20) + (Health × 0.15)
        - (Crime × 0.20)

    Returns:
        pd.DataFrame with wei_score column added
    """
    df["wei_score"] = (
        df["pillar_empowerment"].fillna(0)    * 0.25 +
        df["pillar_education"].fillna(0)      * 0.20 +
        df["pillar_economic"].fillna(0)       * 0.20 +
        df["pillar_health"].fillna(0)         * 0.15 -
        df["pillar_crime_penalty"].fillna(0)  * 0.20
    ).round(1)

    # Mark as NaN where too many pillars are missing
    pillar_cols = [f"pillar_{p}" for p in PILLAR_COLUMNS]
    missing_count = df[pillar_cols].isna().sum(axis=1)
    df.loc[missing_count >= 3, "wei_score"] = np.nan

    return df


def flag_data_quality(df):
    """
    Add data quality flags to help downstream users.
    """
    pillar_cols = [f"pillar_{p}" for p in PILLAR_COLUMNS]
    missing = df[pillar_cols].isna().sum(axis=1)

    df["data_quality"] = "good"
    df.loc[missing == 1, "data_quality"] = "partial"
    df.loc[missing == 2, "data_quality"] = "sparse"
    df.loc[missing >= 3, "data_quality"] = "insufficient"

    return df


def main():
    print("SHEtoken — Pillar Score Builder")
    print("=" * 60)

    # ── Global ────────────────────────────────────────────────────────────────
    global_path = PROCESSED_DIR / "normalised_global.csv"
    if not global_path.exists():
        print(f"✗ {global_path} not found. Run normalise.py first.")
    else:
        print("\nBuilding global pillar scores...")
        df = pd.read_csv(global_path)
        df = build_all_pillars(df)
        df = calculate_wei(df)
        df = flag_data_quality(df)

        out = PROCESSED_DIR / "pillar_scores_global.csv"
        df.to_csv(out, index=False)
        print(f"\n✓ Saved: {out}")
        print(f"  {len(df)} countries")

        # Summary stats
        print(f"\n  WEI score range: {df['wei_score'].min():.1f} – {df['wei_score'].max():.1f}")
        print(f"  WEI mean: {df['wei_score'].mean():.1f}")
        print(f"  Missing WEI: {df['wei_score'].isna().sum()}")
        print(f"\n  Data quality breakdown:")
        if "data_quality" in df.columns:
            for q, count in df["data_quality"].value_counts().items():
                print(f"    {q}: {count}")

    # ── India States ──────────────────────────────────────────────────────────
    india_path = PROCESSED_DIR / "normalised_india_states.csv"
    if not india_path.exists():
        print(f"\n✗ {india_path} not found. Run normalise.py first.")
    else:
        print("\nBuilding India state pillar scores...")
        df_india = pd.read_csv(india_path)
        df_india = build_all_pillars(df_india)
        df_india = calculate_wei(df_india)
        df_india = flag_data_quality(df_india)

        out_india = PROCESSED_DIR / "pillar_scores_india_states.csv"
        df_india.to_csv(out_india, index=False)
        print(f"\n✓ Saved: {out_india}")
        print(f"  {len(df_india)} states")


if __name__ == "__main__":
    main()
