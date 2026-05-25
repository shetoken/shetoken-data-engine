"""
SHEtoken — Index History Snapshot Loader
==========================================
Appends a dated snapshot of every index score (per country) to the history
tables. Append-only: re-running on the same date overwrites only that date's
snapshot (idempotent per day), never previous dates.

ADD TO load_to_supabase.py:
  • paste these two functions
  • call snapshot_all_history(sb) at the END of main(), after all the
    load_* calls (so the score CSVs are present)

The WEEKLY snapshot (snapshot_history_weekly) belongs in the agent's
load_live_to_supabase.py instead — see the note at the bottom.
"""

from datetime import date

# (index_name, csv_filename, score_column) for each structural index.
# These mirror the load_* functions already in load_to_supabase.py.
HISTORY_INDEXES = [
    ("wei",        "baseline-2025.csv",                      "wei_score"),
    ("gpi",        "gender-poverty-index-2025.csv",          "gpi_score"),
    ("svi",        "sexual-violence-index-2025.csv",         "svi_score"),
    ("wadi",       "ai-displacement-index-2025.csv",         "wadi_score"),
    ("wevi",       "widow-elderly-index-2025.csv",           "wevi_score"),
    ("whi",        "womens-health-index-2025.csv",           "whi_score"),
    ("wvi",        "womens-voice-index-2025.csv",            "wvi_score"),
    ("compliance", "corporate-compliance-countries-2025.csv", "composite_score"),
]


def snapshot_all_history(sb) -> None:
    """Append today's snapshot of every index to she_index_history (monthly)."""
    # Snapshot date = first of the current month (one point per month).
    today = date.today()
    snap = today.replace(day=1).isoformat()
    print(f"\n[HIST] Monthly history snapshot for {snap}")

    for index_name, csv_file, score_col in HISTORY_INDEXES:
        try:
            df = read_csv(csv_file)              # uses the loader's own read_csv
        except Exception as e:
            print(f"  ⚠ {index_name}: CSV not found ({csv_file}) — skipped ({e})")
            continue
        if score_col not in df.columns:
            print(f"  ⚠ {index_name}: no '{score_col}' column — skipped")
            continue

        rows = []
        ranked = df.sort_values(score_col, ascending=False).reset_index(drop=True)
        for i, r in ranked.iterrows():
            iso = r.get("iso_code") or r.get("iso") or r.get("country_code")
            if not iso:
                continue
            score = r.get(score_col)
            rows.append({
                "index_name": index_name,
                "iso_code": str(iso).strip().upper(),
                "country": str(r.get("country", "")).strip() or None,
                "score": float(score) if score == score else None,  # NaN guard
                "rank": int(r["rank"]) if "rank" in r and r["rank"] == r["rank"] else int(i + 1),
                "snapshot_date": snap,
            })
        if rows:
            # on_conflict on the full PK → re-running same month updates that
            # month's point only; previous months are untouched (true history).
            upsert(sb, "she_index_history", rows,
                   on_conflict="index_name,iso_code,snapshot_date")
            print(f"  ✓ {index_name}: {len(rows)} rows → history ({snap})")


# ── WEEKLY snapshot — put this in load_live_to_supabase.py ──────────────────
def snapshot_history_weekly(sb, week: str, live_rows_by_index: dict) -> None:
    """
    Append weekly snapshots for news-sensitive indexes.
    live_rows_by_index: {'wei_live': [rows], 'svi': [rows], 'wvi': [rows]}
    where each row has iso_code, country, and a score field.
    """
    snap = date.today().isoformat()
    for index_name, rows_in in live_rows_by_index.items():
        out = []
        for r in rows_in:
            iso = r.get("iso_code")
            if not iso:
                continue
            # accept whichever score key the live row uses
            score = (r.get("score") or r.get(f"{index_name}_score")
                     or r.get("wei_score") or r.get("svi_score") or r.get("wvi_score"))
            out.append({
                "index_name": index_name,
                "iso_code": str(iso).strip().upper(),
                "country": r.get("country"),
                "score": float(score) if score is not None else None,
                "week": week,
                "snapshot_date": snap,
            })
        if out:
            upsert(sb, "she_index_history_weekly", out,
                   on_conflict="index_name,iso_code,week")
            print(f"  ✓ weekly history: {index_name} {len(out)} rows ({week})")
