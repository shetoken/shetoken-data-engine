"""
SHEtoken Pipeline — Data Validation
=====================================
Validates processed data before WEI scores are published.
Flags missing data, anomalies, and year-over-year outliers.

Usage:
    python data/process/validate.py

Input:
    data/processed/pillar_scores_global.csv
    data/processed/pillar_scores_india_states.csv

Output:
    data/processed/validation_report.txt
    data/processed/flagged_anomalies.csv
"""

import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config import PROCESSED_DIR, SCORED_COUNTRIES, INDIA_STATES


# ── VALIDATION RULES ──────────────────────────────────────────────────────────

# Maximum plausible year-over-year change for each pillar
MAX_YOY_CHANGE = {
    "pillar_empowerment":   15.0,  # Political change can be quick (elections)
    "pillar_education":      8.0,  # Literacy changes slowly
    "pillar_economic":      10.0,  # Economic shifts
    "pillar_health":         6.0,  # Health outcomes change slowly
    "pillar_crime_penalty": 20.0,  # Reporting changes can spike
    "wei_score":            12.0,  # Overall index
}

# Minimum expected coverage (% of countries with data)
MIN_COVERAGE = {
    "pillar_empowerment":   0.80,
    "pillar_education":     0.75,
    "pillar_economic":      0.70,
    "pillar_health":        0.80,
    "pillar_crime_penalty": 0.65,
}

# Expected WEI score ranges by tier
TIER_WEI_RANGES = {
    1: (60, 100),
    2: (35, 75),
    3: (15, 50),
    4: (0,  25),
}


class ValidationReport:
    """Collects and formats validation findings."""

    def __init__(self):
        self.errors   = []
        self.warnings = []
        self.info     = []
        self.anomalies = []

    def error(self, msg, row=None):
        self.errors.append(msg)
        if row is not None:
            self.anomalies.append({"severity": "ERROR", "message": msg, **row})

    def warning(self, msg, row=None):
        self.warnings.append(msg)
        if row is not None:
            self.anomalies.append({"severity": "WARNING", "message": msg, **row})

    def info(self, msg):
        self.info.append(msg)

    def summary(self):
        return (
            f"Errors:   {len(self.errors)}\n"
            f"Warnings: {len(self.warnings)}\n"
        )


def check_coverage(df, report, dataset_name="global"):
    """Check that enough countries have data for each pillar."""
    print(f"\n  Coverage checks ({dataset_name})...")
    n = len(df)

    for pillar, min_cov in MIN_COVERAGE.items():
        if pillar not in df.columns:
            report.warning(f"Pillar column missing: {pillar}")
            continue

        coverage = df[pillar].notna().sum() / n
        status = "✓" if coverage >= min_cov else "✗"
        print(f"    {status} {pillar:<30} {coverage:.0%} (min {min_cov:.0%})")

        if coverage < min_cov:
            report.warning(
                f"{dataset_name}: {pillar} coverage {coverage:.0%} below minimum {min_cov:.0%}"
            )


def check_score_ranges(df, report, dataset_name="global"):
    """Check pillar scores are within 0–100."""
    print(f"\n  Range checks ({dataset_name})...")
    pillar_cols = [c for c in df.columns if c.startswith("pillar_")]

    for col in pillar_cols:
        out_of_range = df[
            (df[col].notna()) & ((df[col] < 0) | (df[col] > 100))
        ]
        if len(out_of_range) > 0:
            print(f"    ✗ {col}: {len(out_of_range)} values out of range [0,100]")
            report.error(f"{col}: {len(out_of_range)} out-of-range values",
                         row={"column": col, "count": len(out_of_range)})
        else:
            print(f"    ✓ {col}: all values in [0,100]")


def check_tier_consistency(df, report):
    """Check WEI scores are broadly consistent with tier assignments."""
    if "tier" not in df.columns or "wei_score" not in df.columns:
        return

    print("\n  Tier consistency checks...")
    for tier, (lo, hi) in TIER_WEI_RANGES.items():
        tier_df = df[df["tier"] == tier]
        if tier_df.empty:
            continue
        out = tier_df[
            tier_df["wei_score"].notna() &
            ((tier_df["wei_score"] < lo - 15) | (tier_df["wei_score"] > hi + 15))
        ]
        if len(out) > 0:
            for _, row in out.iterrows():
                country = row.get("country", row.get("state", "?"))
                score   = row["wei_score"]
                report.warning(
                    f"Tier {tier} country {country} has WEI {score} "
                    f"(expected {lo}–{hi})",
                    row={"country": country, "tier": tier, "wei_score": score,
                         "expected_range": f"{lo}–{hi}"}
                )
                print(f"    ⚠ {country}: WEI {score} outside Tier {tier} range {lo}–{hi}")
        else:
            print(f"    ✓ Tier {tier}: all scores consistent")


def check_missing_countries(df, report):
    """Check all expected countries are present."""
    print("\n  Missing country checks...")
    if "iso_code" not in df.columns:
        return

    present = set(df["iso_code"].dropna())
    expected = set(SCORED_COUNTRIES)
    missing  = expected - present

    if missing:
        print(f"    ⚠ Missing {len(missing)} countries: {sorted(missing)[:10]}...")
        report.warning(f"{len(missing)} expected countries missing from dataset")
    else:
        print(f"    ✓ All {len(expected)} expected countries present")


def check_yoy_anomalies(current_df, previous_path, report, dataset_name="global"):
    """
    Compare current scores to previous year for anomalous changes.
    Only runs if a previous year file exists.
    """
    if not previous_path or not os.path.exists(previous_path):
        print(f"\n  YOY check: no previous year file found — skipping")
        return

    prev_df = pd.read_csv(previous_path)
    key_col = "iso_code" if "iso_code" in current_df.columns else "state_code"

    merged = current_df.merge(
        prev_df[[key_col, "wei_score"]].rename(columns={"wei_score": "prev_wei"}),
        on=key_col, how="left"
    )

    merged["yoy_change"] = merged["wei_score"] - merged["prev_wei"]
    threshold = MAX_YOY_CHANGE.get("wei_score", 12)

    flagged = merged[merged["yoy_change"].abs() > threshold]

    print(f"\n  Year-over-year anomalies ({dataset_name})...")
    if flagged.empty:
        print(f"    ✓ No YOY changes > {threshold} points")
    else:
        for _, row in flagged.iterrows():
            entity = row.get("country", row.get("state", row[key_col]))
            change = row["yoy_change"]
            direction = "↑" if change > 0 else "↓"
            print(f"    ⚠ {entity}: {direction}{abs(change):.1f} points YOY")
            report.warning(
                f"Large YOY change: {entity} moved {change:+.1f} points",
                row={key_col: row[key_col], "yoy_change": change,
                     "current_wei": row["wei_score"], "prev_wei": row["prev_wei"]}
            )


def check_wei_formula(df, report, dataset_name="global"):
    """Verify the WEI formula is applied correctly."""
    print(f"\n  Formula verification ({dataset_name})...")

    required = ["pillar_empowerment", "pillar_education", "pillar_economic",
                "pillar_health", "pillar_crime_penalty", "wei_score"]

    if not all(c in df.columns for c in required):
        print("    ⚠ Not all pillar columns present — skipping formula check")
        return

    recalculated = (
        df["pillar_empowerment"].fillna(0)    * 0.25 +
        df["pillar_education"].fillna(0)      * 0.20 +
        df["pillar_economic"].fillna(0)       * 0.20 +
        df["pillar_health"].fillna(0)         * 0.15 -
        df["pillar_crime_penalty"].fillna(0)  * 0.20
    ).round(1)

    diff = (df["wei_score"] - recalculated).abs()
    mismatches = diff[diff > 0.2].count()

    if mismatches > 0:
        print(f"    ✗ {mismatches} rows have WEI scores not matching formula")
        report.error(f"Formula mismatch: {mismatches} rows in {dataset_name}")
    else:
        print(f"    ✓ All WEI scores match formula")


def write_report(report, output_path):
    """Write validation report to text file."""
    lines = [
        "SHEtoken WEI Data Validation Report",
        f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        "=" * 60,
        "",
        f"SUMMARY",
        f"  Errors:   {len(report.errors)}",
        f"  Warnings: {len(report.warnings)}",
        "",
    ]

    if report.errors:
        lines += ["ERRORS", "-" * 40]
        lines += [f"  ✗ {e}" for e in report.errors]
        lines += [""]

    if report.warnings:
        lines += ["WARNINGS", "-" * 40]
        lines += [f"  ⚠ {w}" for w in report.warnings]
        lines += [""]

    lines += [
        "STATUS",
        "  PASS" if not report.errors else "  FAIL — resolve errors before publishing",
    ]

    with open(output_path, "w") as f:
        f.write("\n".join(lines))

    print(f"\n✓ Report saved: {output_path}")


def main():
    print("SHEtoken — Data Validation")
    print("=" * 60)

    report = ValidationReport()

    # ── Validate global data ──────────────────────────────────────────────────
    global_path = PROCESSED_DIR / "pillar_scores_global.csv"
    if global_path.exists():
        df = pd.read_csv(global_path)
        print(f"\nValidating global data ({len(df)} countries)...")
        check_coverage(df, report, "global")
        check_score_ranges(df, report, "global")
        check_tier_consistency(df, report)
        check_missing_countries(df, report)
        check_wei_formula(df, report, "global")
        check_yoy_anomalies(df, None, report, "global")
    else:
        print(f"✗ {global_path} not found — run build_pillars.py first")

    # ── Validate India states ─────────────────────────────────────────────────
    india_path = PROCESSED_DIR / "pillar_scores_india_states.csv"
    if india_path.exists():
        df_india = pd.read_csv(india_path)
        print(f"\nValidating India states ({len(df_india)} states)...")
        check_coverage(df_india, report, "india_states")
        check_score_ranges(df_india, report, "india_states")
        check_wei_formula(df_india, report, "india_states")

    # ── Write report ──────────────────────────────────────────────────────────
    report_path = PROCESSED_DIR / "validation_report.txt"
    write_report(report, report_path)

    if report.anomalies:
        anomaly_df = pd.DataFrame(report.anomalies)
        anomaly_path = PROCESSED_DIR / "flagged_anomalies.csv"
        anomaly_df.to_csv(anomaly_path, index=False)
        print(f"✓ Anomalies saved: {anomaly_path}")

    print(f"\n{'='*60}")
    print(f"VALIDATION {'PASSED ✓' if not report.errors else 'FAILED ✗'}")
    print(f"  Errors: {len(report.errors)} | Warnings: {len(report.warnings)}")
    print(f"{'='*60}")

    return len(report.errors) == 0


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
