"""
SHEtoken — WEI Live Score Updater
===================================
Applies weekly news signals to the WEI baseline scores,
producing a "live" WEI that updates between annual cycles.

Architecture:
  - Annual official data = 90% weight (baseline, from CSVs)
  - Weekly news signals  = 10% weight (leading indicator)
  - Signals decay over 12 weeks (half-life)
  - Maximum weekly movement: 2.0 WEI points per country

This creates real-time price discovery for sub-tokens
without compromising the integrity of the annual index.

Usage:
    from wei_updater import apply_signals_to_wei
    updated = apply_signals_to_wei(signals, baseline_csv, output_csv)
"""

import json, csv, io, logging, os, sys
from datetime import datetime, timezone
from pathlib import Path
from collections import defaultdict

sys.path.insert(0, str(Path(__file__).parent))
from config import (OUTPUT_DIR, SIGNAL_WEIGHT, MAX_WEEKLY_DELTA,
                    DECAY_HALFLIFE_WEEKS, GEOGRAPHY_KEYWORDS)

logger = logging.getLogger(__name__)

# Pillar → column name in baseline CSV
PILLAR_COLS = {
    "empowerment":    "empowerment_score",
    "education":      "education_score",
    "economic":       "economic_score",
    "health":         "health_score",
    "bodily_autonomy":"bodily_autonomy_score",
    "safety_justice": "safety_justice_score",
    "dignity_welfare":"dignity_welfare_score",
    "digital_social": "digital_social_score",
    "violence_penalty":"violence_penalty_score",
}

# WEI formula weights
PILLAR_WEIGHTS = {
    "empowerment":     0.15,
    "education":       0.12,
    "economic":        0.12,
    "health":          0.12,
    "bodily_autonomy": 0.15,
    "safety_justice":  0.14,
    "dignity_welfare": 0.10,
    "digital_social":  0.10,
    "violence_penalty":0.10,  # subtracted
}


def recalc_wei(row: dict) -> float:
    """Recalculate WEI score from pillar scores in a row dict."""
    try:
        score = (
            float(row.get("empowerment_score",0))    * 0.15 +
            float(row.get("education_score",0))       * 0.12 +
            float(row.get("economic_score",0))        * 0.12 +
            float(row.get("health_score",0))          * 0.12 +
            float(row.get("bodily_autonomy_score",0)) * 0.15 +
            float(row.get("safety_justice_score",0))  * 0.14 +
            float(row.get("dignity_welfare_score",0)) * 0.10 +
            float(row.get("digital_social_score",0))  * 0.10 -
            float(row.get("violence_penalty_score",0))* 0.10
        )
        return round(score, 1)
    except (ValueError, TypeError):
        return float(row.get("wei_score", 0))


def compute_signal_deltas(signals: list) -> dict:
    """
    Aggregate signals into pillar deltas per country/state.

    Returns:
        dict: {(country, state): {pillar: delta_value}}
    """
    geo_pillar_signals = defaultdict(lambda: defaultdict(list))

    for sig in signals:
        country = sig.get("country")
        state   = sig.get("state")
        pillar  = sig.get("pillar", "")
        if not country or not pillar or pillar not in PILLAR_WEIGHTS:
            continue

        # Weighted signal value
        direction  = float(sig.get("direction", 0))
        severity   = float(sig.get("severity", 0.3))
        confidence = float(sig.get("confidence", 0.6))
        value      = direction * severity * confidence

        geo_pillar_signals[(country, state)][pillar].append(value)
        # Also apply to national score if state-level
        if state:
            geo_pillar_signals[(country, None)][pillar].append(value * 0.5)

    # Collapse to single delta per geo/pillar
    deltas = {}
    for geo, pillars in geo_pillar_signals.items():
        deltas[geo] = {}
        for pillar, values in pillars.items():
            if not values:
                continue
            # Average signal, scaled by SIGNAL_WEIGHT
            avg_signal = sum(values) / len(values)
            # Convert to score delta (signal is -1 to +1, scale to score points)
            delta = avg_signal * SIGNAL_WEIGHT * 100
            # Cap at MAX_WEEKLY_DELTA
            delta = max(-MAX_WEEKLY_DELTA, min(MAX_WEEKLY_DELTA, delta))
            deltas[geo][pillar] = round(delta, 2)

    return deltas


def load_baseline(csv_path: str) -> list:
    """Load baseline CSV, skipping comment lines."""
    rows = []
    with open(csv_path, "r", encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    reader = csv.DictReader(io.StringIO("".join(lines)))
    for row in reader:
        rows.append(dict(row))
    return rows


def apply_signals_to_wei(signals: list,
                          baseline_csv: str,
                          output_csv: str = None,
                          week_str: str = None) -> list:
    """
    Apply weekly signals to WEI baseline scores.

    Args:
        signals:      list of classified signal dicts
        baseline_csv: path to baseline-YYYY.csv
        output_csv:   where to save updated scores (optional)
        week_str:     week identifier e.g. "2025-W22"

    Returns:
        list of updated country rows with live WEI scores
    """
    if not Path(baseline_csv).exists():
        logger.error(f"Baseline CSV not found: {baseline_csv}")
        return []

    week = week_str or datetime.now(timezone.utc).strftime("%Y-W%W")
    baseline_rows = load_baseline(baseline_csv)
    deltas        = compute_signal_deltas(signals)

    logger.info(f"  Baseline: {len(baseline_rows)} countries")
    logger.info(f"  Signal deltas computed for {len(deltas)} geographies")

    updated_rows = []
    countries_moved = 0

    for row in baseline_rows:
        iso   = row.get("iso_code", "")
        state = None   # global baseline has no state

        updated = dict(row)
        geo_key = (iso, state)
        country_deltas = deltas.get(geo_key, {})

        if country_deltas:
            countries_moved += 1
            for pillar, delta in country_deltas.items():
                col = PILLAR_COLS.get(pillar)
                if not col or col not in updated:
                    continue
                try:
                    old_val = float(updated[col])
                    new_val = round(max(0, min(100, old_val + delta)), 1)
                    updated[col] = new_val
                    logger.debug(f"  {iso} {pillar}: {old_val} → {new_val} (Δ{delta:+.2f})")
                except (ValueError, TypeError):
                    pass

        # Recalculate WEI from updated pillars
        old_wei = float(updated.get("wei_score", 0))
        new_wei = recalc_wei(updated)
        updated["wei_score_baseline"] = old_wei
        updated["wei_score"]          = new_wei
        updated["wei_score_live"]     = new_wei
        updated["signal_count_this_week"] = len(deltas.get(geo_key, {}))
        updated["last_signal_week"]   = week if country_deltas else updated.get("last_signal_week","")
        updated["wei_data_type"]      = "live_signal" if country_deltas else "baseline"

        updated_rows.append(updated)

    # Re-rank
    updated_rows.sort(key=lambda x: float(x.get("wei_score",0)), reverse=True)
    for i, row in enumerate(updated_rows):
        row["rank"] = i + 1

    logger.info(f"  {countries_moved} countries updated by signals")

    # Save if output path provided
    if output_csv:
        _save_live_csv(updated_rows, output_csv, week)

    return updated_rows


def apply_signals_to_states(signals: list,
                              states_csv: str,
                              country_iso: str,
                              output_csv: str = None,
                              week_str: str = None) -> list:
    """
    Apply weekly signals to a state-level CSV.
    Works for India, USA, Brazil, Nigeria, Mexico, Pakistan.
    """
    if not Path(states_csv).exists():
        logger.warning(f"States CSV not found: {states_csv}")
        return []

    week = week_str or datetime.now(timezone.utc).strftime("%Y-W%W")
    rows   = load_baseline(states_csv)
    deltas = compute_signal_deltas(signals)

    updated_rows = []
    for row in rows:
        state_code = row.get("state_code") or row.get("province_code", "")
        geo_key    = (country_iso, state_code)
        state_deltas = deltas.get(geo_key, {})

        updated = dict(row)
        if state_deltas:
            for pillar, delta in state_deltas.items():
                col = PILLAR_COLS.get(pillar)
                if col and col in updated:
                    try:
                        old = float(updated[col])
                        updated[col] = round(max(0, min(100, old + delta)), 1)
                    except (ValueError, TypeError):
                        pass

        old_wei = float(updated.get("wei_score", 0))
        new_wei = recalc_wei(updated)
        updated["wei_score_baseline"] = old_wei
        updated["wei_score"]          = new_wei
        updated["signal_count_this_week"] = len(state_deltas)
        updated["wei_data_type"]      = "live_signal" if state_deltas else "baseline"
        updated_rows.append(updated)

    updated_rows.sort(key=lambda x: float(x.get("wei_score",0)), reverse=True)
    for i, row in enumerate(updated_rows):
        row["rank"] = i + 1

    if output_csv:
        _save_live_csv(updated_rows, output_csv, week)

    return updated_rows


def _save_live_csv(rows: list, output_path: str, week: str):
    """Save updated rows to CSV with live header."""
    if not rows:
        return
    header = (
        f"# SHEtoken WEI Live Scores — Week {week}\n"
        f"# Generated: {datetime.now(timezone.utc).isoformat()}\n"
        f"# 90% baseline annual data + 10% weekly news signal adjustment\n"
        f"# Full methodology: wei-index/methodology.md\n#\n"
    )
    fieldnames = list(rows[0].keys())
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)
    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        f.write(header + buf.getvalue())
    logger.info(f"  Saved live scores: {output_path}")
