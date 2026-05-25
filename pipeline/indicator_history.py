"""
SHEtoken — Indicator History Snapshotter
=========================================
Captures the RAW INPUT INDICATORS behind every index into she_indicator_history,
dated per run. This is the audit trail: it lets anyone reconstruct how a score
was calculated for any country in any month.

KEY INSIGHT: the generators ALREADY build row dicts containing every raw
indicator (e.g. who_lifetime_prevalence_pct, reporting_gap_pct, ...) before
computing the score. This snapshotter "melts" those rows into long format —
one record per indicator per country — so NO generator rewrite is needed.

HOW TO USE — two integration styles, pick one:

  STYLE A (preferred, exact): in each generator's generate(), after building
  `rows`, also return them, and have the pipeline call:
        snapshot_indicators(sb, "svi", rows, score_key="svi_score")
  This captures the precise in-memory inputs the score was computed from.

  STYLE B (zero generator change): read the output CSV and snapshot its numeric
  columns:
        snapshot_indicators_from_csv(sb, "svi", "sexual-violence-index-2025.csv",
                                     score_key="svi_score")
  Captures whatever the CSV persisted (pillar scores + any raw columns saved).

Both are append-only: re-running on the same date refreshes that date only.
"""

from datetime import date

# Columns that are identifiers, not indicators — never snapshot these as values.
_NON_INDICATOR = {
    "iso_code", "iso", "country_code", "country", "region", "tier", "ticker",
    "year", "rank", "wei_version", "version", "data_source", "verified",
    "notes", "source", "source_note", "population_weight", "state_code",
}


def _melt_row(index_name, row, score_key, snap):
    """Turn one country's row dict into long-format indicator records."""
    iso = row.get("iso_code") or row.get("iso") or row.get("country_code")
    if not iso:
        return []
    iso = str(iso).strip().upper()
    country = str(row.get("country", "")).strip() or None
    out = []
    for key, val in row.items():
        if key in _NON_INDICATOR or key == score_key:
            continue
        # only numeric indicators
        try:
            num = float(val)
        except (TypeError, ValueError):
            continue
        if num != num:   # NaN
            continue
        out.append({
            "index_name": index_name,
            "iso_code": iso,
            "country": country,
            "indicator_key": key,
            "indicator_value": num,
            "snapshot_date": snap,
        })
    return out


def snapshot_indicators(sb, index_name, rows, score_key=None) -> int:
    """STYLE A — snapshot raw indicators from in-memory generator rows."""
    snap = date.today().replace(day=1).isoformat()
    records = []
    for row in rows:
        records.extend(_melt_row(index_name, row, score_key, snap))
    if records:
        upsert(sb, "she_indicator_history", records,
               on_conflict="index_name,iso_code,indicator_key,snapshot_date")
        print(f"  ✓ indicator history: {index_name} {len(records)} records ({snap})")
    return len(records)


def snapshot_indicators_from_csv(sb, index_name, csv_file, score_key=None) -> int:
    """STYLE B — snapshot indicators by reading the output CSV (no gen change)."""
    snap = date.today().replace(day=1).isoformat()
    try:
        df = read_csv(csv_file)
    except Exception as e:
        print(f"  ⚠ indicator history: {index_name} CSV missing ({csv_file}) — {e}")
        return 0
    records = []
    for _, r in df.iterrows():
        records.extend(_melt_row(index_name, r.to_dict(), score_key, snap))
    if records:
        upsert(sb, "she_indicator_history", records,
               on_conflict="index_name,iso_code,indicator_key,snapshot_date")
        print(f"  ✓ indicator history (csv): {index_name} {len(records)} records ({snap})")
    return len(records)


def snapshot_formula(sb, index_name, weights: dict, version: str = "v3.0") -> None:
    """Optional — record the weights/formula used this run, for full reproducibility."""
    import json
    snap = date.today().replace(day=1).isoformat()
    sb.table("she_formula_history").upsert(
        [{"index_name": index_name, "snapshot_date": snap,
          "formula_json": json.dumps(weights), "version": version}],
        on_conflict="index_name,snapshot_date",
    ).execute()
    print(f"  ✓ formula history: {index_name} {version} ({snap})")


# Map of indexes → (csv, score_key) for the STYLE B one-shot capture of all.
ALL_INDEX_CSVS = [
    ("wei",        "baseline-2025.csv",                       "wei_score"),
    ("gpi",        "gender-poverty-index-2025.csv",           "gpi_score"),
    ("svi",        "sexual-violence-index-2025.csv",          "svi_score"),
    ("wadi",       "ai-displacement-index-2025.csv",          "wadi_score"),
    ("wevi",       "widow-elderly-index-2025.csv",            "wevi_score"),
    ("whi",        "womens-health-index-2025.csv",            "whi_score"),
    ("wvi",        "womens-voice-index-2025.csv",             "wvi_score"),
    ("compliance", "corporate-compliance-countries-2025.csv", "composite_score"),
]


def snapshot_all_indicators(sb) -> None:
    """STYLE B for every index — call at the end of main() after load_*."""
    print("\n[IND-HIST] Indicator audit snapshot")
    total = 0
    for index_name, csv_file, score_key in ALL_INDEX_CSVS:
        total += snapshot_indicators_from_csv(sb, index_name, csv_file, score_key)
    print(f"[IND-HIST] {total} indicator records captured")
