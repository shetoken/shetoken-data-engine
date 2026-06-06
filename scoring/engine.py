"""
Versioned, config-driven SHE Score engine (Track B).

One engine, many versioned configs. Pillar definitions, weights, inverted-
indicator flags, normalization bounds and the aggregation formula all come from
config/{version}.json — nothing about a methodology version is hardcoded here.

  - config/v2.json  → official, frozen (regression-locked to West Bengal = 39.1)
  - config/v3.json  → shadow only (never affects published scores or $SHE supply)
"""
from __future__ import annotations

import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

# Documented supply mechanics (illustrative; not a price).
SUPPLY_UNITS_PER_POINT = 10_000_000
START_SUPPLY = 1_000_000_000

_CONFIG_DIR = Path(__file__).resolve().parent.parent / "config"


def load_config(version_or_path: str) -> dict:
    """Load a config by version name ('v2') or explicit path."""
    p = Path(version_or_path)
    if not p.exists():
        p = _CONFIG_DIR / f"{version_or_path}.json"
    with open(p, "r", encoding="utf-8") as f:
        return json.load(f)


def _round(x: float, rnd: dict) -> float:
    decimals = rnd.get("decimals", 1)
    if rnd.get("mode") == "half_up":
        q = Decimal(1).scaleb(-decimals)          # 0.1 for decimals=1
        return float(Decimal(str(x)).quantize(q, rounding=ROUND_HALF_UP))
    return round(x, decimals)


def normalize(value: float, indicator: str, config: dict) -> float:
    """Normalize a raw indicator value to 0-100, inverting if flagged."""
    bounds = config.get("normalization", {}).get("default", {"min": 0, "max": 100})
    lo, hi = float(bounds["min"]), float(bounds["max"])
    v = max(lo, min(hi, float(value)))
    norm = (v - lo) / (hi - lo) * 100 if hi > lo else 0.0
    if indicator in set(config.get("inverted_indicators", [])):
        norm = 100 - norm
    return norm


def score(pillar_scores: dict, config: dict) -> dict:
    """Compute a score from per-pillar 0-100 sub-scores using a config.

    Returns {version, status, score, raw, coverage{used, weighted, missing[]}}.
    Provisional pillars (weight == null) are excluded from the weighted set.
    For an 'official' config a missing weighted pillar raises (never imputed);
    for a 'shadow' config it is skipped and counted as insufficient coverage.
    """
    raw = 0.0
    used = 0
    weighted = 0
    missing = []
    for name, p in config["pillars"].items():
        w = p.get("weight")
        if w is None:
            continue                                  # provisional / not yet weighted
        weighted += 1
        v = pillar_scores.get(name)
        if v is None:
            if config.get("status") == "official":
                raise ValueError(f"missing pillar '{name}' required by official config {config['version']}")
            missing.append(name)                      # shadow: never impute
            continue
        raw += float(v) * float(w)
        used += 1
    value = _round(raw, config.get("rounding", {"decimals": 1, "mode": "half_up"}))
    return {
        "version": config["version"],
        "status": config["status"],
        "score": value,
        "raw": round(raw, 6),
        "coverage": {"used": used, "weighted": weighted, "missing": missing},
    }


def supply_change(delta_points: float) -> int:
    """SHE units minted (positive) or burned (negative) for a score change."""
    return round(delta_points * SUPPLY_UNITS_PER_POINT)
