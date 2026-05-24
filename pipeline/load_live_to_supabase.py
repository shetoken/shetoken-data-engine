"""
SHEtoken — Weekly Live Loader
=============================
Runs at the END of the weekly agent workflow, in the SAME job, while the
freshly-generated live files still exist on disk (they're gitignored, so they
never get committed — we must read them in-run).

What it does:
  1. Finds the newest agent/output/live/wei-live-global-*.csv
  2. Upserts the live (signal-adjusted) scores into she_wei_live
  3. Computes the population-weighted global LIVE WEI
  4. Updates she_meta.current_global_wei  → dashboard hero dial shows LIVE
  5. Inserts ONE dated snapshot into she_wei_history_global
        → the dashboard's 1-week / 1-month comparison arrows light up

USAGE (local):
    pip install supabase pandas python-dotenv
    # .env must have SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY
    python pipeline/load_live_to_supabase.py

USAGE (CI): set the two env vars as GitHub secrets (already done for the
monthly loader) — this script reuses the exact same secrets.

PORTABILITY: standalone + deletable. Reads CSVs, writes Supabase. If you ever
leave Supabase, delete this file and the weekly workflow step.
"""

from __future__ import annotations

import os
import sys
import glob
from pathlib import Path
from datetime import datetime, timezone

import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
LIVE_DIR = REPO_ROOT / "agent" / "output" / "live"

PILLAR_COLS = [
    "empowerment_score", "education_score", "economic_score", "health_score",
    "bodily_autonomy_score", "safety_justice_score", "dignity_welfare_score",
    "digital_social_score", "violence_penalty_score",
]


def get_client() -> Client:
    load_dotenv()
    url = os.getenv("SUPABASE_URL")
    key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    if not url or not key:
        sys.exit("ERROR: Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY")
    if key.startswith("sb_publishable") or "publishable" in key.lower():
        sys.exit("ERROR: Use the service_role key, not the publishable key.")
    return create_client(url, key)


def newest_live_file(pattern: str) -> Path | None:
    """Return the most recently modified file matching agent/output/live/<pattern>."""
    matches = glob.glob(str(LIVE_DIR / pattern))
    if not matches:
        return None
    return Path(max(matches, key=os.path.getmtime))


def week_from_filename(path: Path) -> str:
    """Extract '2026-W21' from 'wei-live-global-2026-W21.csv'."""
    stem = path.stem  # wei-live-global-2026-W21
    parts = stem.split("-")
    # last two chunks are year and Wnn
    if len(parts) >= 2:
        return f"{parts[-2]}-{parts[-1]}"
    return datetime.now().strftime("%Y-W%U")


def clean(df: pd.DataFrame) -> pd.DataFrame:
    return df.where(pd.notna(df), None)


def load_global_live(sb: Client) -> tuple[float, dict[str, float], str] | None:
    """Load the global live file → she_wei_live. Return (global_wei, pillar_avgs, week)."""
    f = newest_live_file("wei-live-global-*.csv")
    if not f:
        print("  ⚠ No global live file found in agent/output/live/ — nothing to load.")
        return None

    week = week_from_filename(f)
    print(f"→ Loading global live file: {f.name}  (week {week})")
    df = clean(pd.read_csv(f, comment="#"))

    mapping = {
        "iso_code": "iso_code",
        "rank": "rank",
        "country": "country",
        "wei_score": "wei_score",
        "wei_score_baseline": "wei_score_baseline",
        "wei_score_live": "wei_score_live",
        "signal_count_this_week": "signal_count_this_week",
        "wei_data_type": "wei_data_type",
        "population_weight": "population_weight",
        **{c: c for c in PILLAR_COLS},
    }
    avail = {k: v for k, v in mapping.items() if k in df.columns}
    rows = df[list(avail.keys())].rename(columns=avail).to_dict(orient="records")
    for r in rows:
        r["week"] = week
        for k, v in list(r.items()):
            if v is not None and not isinstance(v, (list, dict)) and pd.isna(v):
                r[k] = None
    rows = [r for r in rows if r.get("iso_code")]

    for i in range(0, len(rows), 200):
        sb.table("she_wei_live").upsert(
            rows[i:i + 200], on_conflict="iso_code,week"
        ).execute()
    print(f"  ✓ she_wei_live: {len(rows)} rows upserted")

    # Population-weighted global live WEI
    d = df.dropna(subset=["wei_score"])
    if "population_weight" in d.columns and d["population_weight"].notna().any():
        gw = (d["wei_score"].astype(float) * d["population_weight"].astype(float)).sum()
        gw /= d["population_weight"].astype(float).sum()
    else:
        gw = d["wei_score"].astype(float).mean()
    global_wei = round(float(gw), 1)

    pillar_avgs = {}
    for c in PILLAR_COLS:
        if c in df.columns:
            vals = pd.to_numeric(df[c], errors="coerce").dropna()
            pillar_avgs[c] = round(float(vals.mean()), 1) if len(vals) else None

    return global_wei, pillar_avgs, week


def load_region_live(sb: Client, pattern: str, label: str) -> None:
    """India / USA live files → also stored in she_wei_live (keyed by iso/state code)."""
    f = newest_live_file(pattern)
    if not f:
        print(f"  · no {label} live file")
        return
    week = week_from_filename(f)
    df = clean(pd.read_csv(f, comment="#"))
    code_col = "state_code" if "state_code" in df.columns else "iso_code"
    if code_col not in df.columns:
        print(f"  · {label}: no id column, skipping")
        return
    rows = []
    for _, row in df.iterrows():
        rows.append({
            "iso_code": f"{label}-{row[code_col]}",
            "week": week,
            "rank": row.get("rank"),
            "country": row.get("state") or row.get("state_name") or label,
            "wei_score": row.get("wei_score"),
            "wei_score_baseline": row.get("wei_score_baseline"),
            **{c: row.get(c) for c in PILLAR_COLS if c in df.columns},
        })
    rows = [{k: (None if (v is not None and not isinstance(v, (list, dict)) and pd.isna(v)) else v)
             for k, v in r.items()} for r in rows]
    if rows:
        sb.table("she_wei_live").upsert(rows, on_conflict="iso_code,week").execute()
        print(f"  ✓ {label} live: {len(rows)} rows")


def update_meta_and_history(
    sb: Client, global_wei: float, pillars: dict[str, float], week: str
) -> None:
    """Update the hero number + append one history snapshot for the comparison strip."""
    now_iso = datetime.now(timezone.utc).isoformat()
    today = datetime.now(timezone.utc).date().isoformat()

    sb.table("she_meta").upsert([
        {"meta_key": "current_global_wei", "meta_value": str(global_wei)},
        {"meta_key": "last_live_run", "meta_value": now_iso},
        {"meta_key": "last_live_week", "meta_value": week},
    ], on_conflict="meta_key").execute()
    print(f"  ✓ she_meta: global live WEI = {global_wei}")

    snapshot = {"snapshot_date": today, "wei_score": global_wei, "notes": f"weekly live {week}"}
    for c in PILLAR_COLS:
        if pillars.get(c) is not None:
            snapshot[c] = pillars[c]
    sb.table("she_wei_history_global").upsert(
        [snapshot], on_conflict="snapshot_date"
    ).execute()
    print(f"  ✓ she_wei_history_global: snapshot for {today}")


def main() -> None:
    print("=" * 70)
    print("SHEtoken — Weekly Live Loader")
    print("=" * 70)
    if not LIVE_DIR.exists():
        sys.exit(f"ERROR: live dir not found: {LIVE_DIR}")

    sb = get_client()
    result = load_global_live(sb)
    if result is None:
        print("No global live data — exiting without changes.")
        return
    global_wei, pillars, week = result

    load_region_live(sb, "wei-live-india-*.csv", "IND")
    load_region_live(sb, "wei-live-usa-*.csv", "USA")

    update_meta_and_history(sb, global_wei, pillars, week)

    print("\n" + "=" * 70)
    print(f"✓ DONE — weekly live load complete for {week}")
    print(f"  Global live WEI: {global_wei}")
    print("=" * 70)


if __name__ == "__main__":
    main()
