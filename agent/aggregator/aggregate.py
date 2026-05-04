"""
SHEtoken Agent — Signal Aggregator
Rolls up individual signals into weekly WEI impact scores by region/pillar.
"""
import json, logging
from datetime import datetime, timezone
from collections import defaultdict
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import OUTPUT_DIR, CRISIS_THRESHOLD

logger = logging.getLogger(__name__)

PILLARS = [
    "empowerment","education","economic","health",
    "bodily_autonomy","safety_justice","dignity_welfare",
    "digital_social","violence_penalty"
]


def aggregate_signals(signals: list, week_str: str) -> dict:
    """
    Aggregate signals into weekly WEI impact report.

    Returns structured dict with:
      - global_summary
      - by_country
      - by_pillar
      - crisis_alerts
      - raw_signals
    """
    by_country  = defaultdict(lambda: defaultdict(list))
    by_pillar   = defaultdict(list)
    crisis_list = []

    for sig in signals:
        country = sig.get("country") or "UNKNOWN"
        state   = sig.get("state")
        pillar  = sig.get("pillar", "unknown")
        geo_key = f"{country}-{state}" if state else country

        by_country[geo_key][pillar].append(sig)
        by_pillar[pillar].append(sig)

        if sig.get("crisis"):
            crisis_list.append(sig)

    # Compute weighted scores per geo/pillar
    country_scores = {}
    for geo, pillars in by_country.items():
        scores = {}
        for pillar, sigs in pillars.items():
            if not sigs:
                continue
            # Weighted average: severity × direction × confidence
            total_weight = sum(s["severity"] * s["confidence"] for s in sigs)
            weighted_dir = sum(s["direction"] * s["severity"] * s["confidence"] for s in sigs)
            net_signal   = round(weighted_dir / total_weight, 3) if total_weight > 0 else 0
            scores[pillar] = {
                "net_signal":    net_signal,
                "signal_count":  len(sigs),
                "positive":      sum(1 for s in sigs if s["direction"] > 0),
                "negative":      sum(1 for s in sigs if s["direction"] < 0),
                "top_stories":   [s["summary_en"] for s in sorted(
                    sigs, key=lambda x: x["severity"], reverse=True)[:3]]
            }
        country_scores[geo] = scores

    # Pillar summary
    pillar_summary = {}
    for pillar, sigs in by_pillar.items():
        if not sigs:
            continue
        total_weight = sum(s["severity"] * s["confidence"] for s in sigs)
        weighted_dir = sum(s["direction"] * s["severity"] * s["confidence"] for s in sigs)
        pillar_summary[pillar] = {
            "net_signal":   round(weighted_dir / total_weight, 3) if total_weight > 0 else 0,
            "total_signals": len(sigs),
            "positive":     sum(1 for s in sigs if s["direction"] > 0),
            "negative":     sum(1 for s in sigs if s["direction"] < 0),
        }

    # Top movers (countries with strongest absolute signals)
    top_movers = []
    for geo, pillars in country_scores.items():
        net = sum(abs(p["net_signal"]) for p in pillars.values())
        top_movers.append({"geo": geo, "activity_score": round(net, 3),
                           "signals": sum(p["signal_count"] for p in pillars.values())})
    top_movers.sort(key=lambda x: x["activity_score"], reverse=True)

    report = {
        "week":            week_str,
        "generated_at":    datetime.now(timezone.utc).isoformat(),
        "total_articles_processed": len(signals),
        "total_signals":   len(signals),
        "crisis_count":    len(crisis_list),
        "crisis_alerts":   crisis_list,
        "global_pillar_summary": pillar_summary,
        "top_movers":      top_movers[:20],
        "by_geography":    dict(country_scores),
        "raw_signals":     signals,
    }

    # Save to JSON
    out_path = OUTPUT_DIR / f"signals_{week_str}.json"
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)

    logger.info(f"Saved signal report: {out_path}")
    logger.info(f"  Total signals: {len(signals)}")
    logger.info(f"  Crisis alerts: {len(crisis_list)}")
    logger.info(f"  Top mover:     {top_movers[0]['geo'] if top_movers else 'none'}")

    return report
