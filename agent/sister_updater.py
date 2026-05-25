"""
SHEtoken — Sister Index Signal Updater
=======================================
Applies weekly news signals to the NEWS-SENSITIVE sister indexes only:
  • SVI (Sexual Violence Index)  ← safety_justice + violence_penalty signals
  • WVI (Women's Voice Index)    ← empowerment + digital_social signals

STRUCTURAL sister indexes (WHI, GPI, WEVI, WADI, FHI) are deliberately NOT
touched — nothing in a single week's news legitimately moves anaemia
prevalence or pension coverage. Forcing those weekly would be false precision.
They refresh on the MONTHLY pipeline instead.

Direction: the classifier uses a uniform convention (+1 good / -1 bad), so a
femicide (-1) yields a negative delta → SVI down. SVI and WVI are both
'higher = better', so signed deltas apply directly with NO inversion.

Reuses compute_signal_deltas() from wei_updater so signal scaling and the
±MAX_WEEKLY_DELTA cap stay identical to the WEI engine.

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, logging
from pathlib import Path

sys.path.insert(0, os.path.dirname(__file__))
from wei_updater import compute_signal_deltas   # reuse exact scaling + cap
from config import MAX_WEEKLY_DELTA

logger = logging.getLogger(__name__)

# WEI pillars that drive each news-sensitive sister index.
SISTER_PILLAR_MAP = {
    "SVI": ["safety_justice", "violence_penalty"],
    "WVI": ["empowerment", "digital_social"],
}

SISTER_CONFIG = {
    "SVI": {"baseline": "sexual-violence-index-2025.csv", "score_col": "svi_score"},
    "WVI": {"baseline": "womens-voice-index-2025.csv",    "score_col": "wvi_score"},
}


def _clamp(v, lo=0.0, hi=100.0):
    return max(lo, min(hi, v))


def _read_csv_skip_comments(path):
    with open(path, newline="", encoding="utf-8") as f:
        lines = [ln for ln in f if not ln.lstrip().startswith("#")]
    reader = csv.DictReader(lines)
    rows = list(reader)
    return rows, reader.fieldnames


def apply_signals_to_sister_indexes(signals, data_dir, live_dir, week):
    """
    Apply news signals to SVI and WVI; write {svi,wvi}-live-{week}.csv to live_dir.
    Returns {index_name: [rows]}.
    """
    deltas = compute_signal_deltas(signals)   # {(country, state): {pillar: delta}}
    live_dir = Path(live_dir)
    live_dir.mkdir(parents=True, exist_ok=True)
    results = {}

    for index_name, cfg in SISTER_CONFIG.items():
        baseline_path = Path(data_dir) / cfg["baseline"]
        if not baseline_path.exists():
            logger.warning(f"  {index_name}: baseline missing ({baseline_path.name}), skipping")
            continue

        score_col = cfg["score_col"]
        pillars = SISTER_PILLAR_MAP[index_name]
        rows, fieldnames = _read_csv_skip_comments(baseline_path)

        out_rows = []
        moved = 0
        for r in rows:
            country = r.get("country")
            base = float(r.get(score_col, 0) or 0)
            geo_deltas = deltas.get((country, None), {})
            # Sum mapped pillar deltas, then cap the COMBINED weekly move.
            sister_delta = sum(geo_deltas.get(p, 0.0) for p in pillars)
            sister_delta = max(-MAX_WEEKLY_DELTA, min(MAX_WEEKLY_DELTA, sister_delta))
            live = round(_clamp(base + sister_delta), 1)
            if live != base:
                moved += 1
            nr = dict(r)
            nr[f"{score_col}_baseline"] = base
            nr[score_col] = live
            nr["signal_count_this_week"] = sum(1 for p in pillars if p in geo_deltas)
            nr["week"] = week
            out_rows.append(nr)

        out_rows.sort(key=lambda x: float(x.get(score_col, 0) or 0), reverse=True)
        for i, nr in enumerate(out_rows):
            nr["rank"] = i + 1

        out_fields = list(fieldnames)
        for extra in (f"{score_col}_baseline", "signal_count_this_week", "week"):
            if extra not in out_fields:
                out_fields.append(extra)

        out_path = live_dir / f"{index_name.lower()}-live-{week}.csv"
        buf = io.StringIO()
        w = csv.DictWriter(buf, fieldnames=out_fields, extrasaction="ignore")
        w.writeheader()
        w.writerows(out_rows)
        hdr = (
            f"# SHEtoken {index_name} LIVE (signal-adjusted) — week {week}\n"
            f"# Baseline + capped weekly news signals from: {', '.join(pillars)}\n"
            f"# Higher = better. Structural sisters (WHI/GPI/WEVI/WADI/FHI) NOT adjusted.\n#\n"
        )
        with open(out_path, "w", newline="", encoding="utf-8") as f:
            f.write(hdr + buf.getvalue())

        logger.info(f"  {index_name}: {moved}/{len(out_rows)} countries moved → {out_path.name}")
        results[index_name] = out_rows

    return results
