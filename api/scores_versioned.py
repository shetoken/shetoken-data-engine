"""
Versioned scores API (Track B6).

  GET /api/v2/scores          official v2 scores  (frozen, published)
  GET /api/scores             alias -> v2
  GET /api/v2/scores/{iso}    one country, v2
  GET /api/v3-preview/scores  SHADOW v3 scores only; every response carries
                              version="v3", status="shadow" and per-pillar
                              coverage counts. v3 is exposed NOWHERE else.

The dashboard consumes only the v2 endpoint.
"""
from __future__ import annotations

import sys
from pathlib import Path

from fastapi import APIRouter, HTTPException

# Make the config-driven engine importable (lives in repo_root/scoring).
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scoring"))
from engine import load_config, score  # noqa: E402

from data_loader import get_global_scores  # noqa: E402

V2 = load_config("v2")
V3 = load_config("v3")

# v3 candidate pillars that are not yet weighted (data still being gathered).
_V3_CANDIDATES = {
    "bodily_autonomy": "bodily_autonomy_score",
    "dignity_welfare": "dignity_welfare_score",
    "digital_social": "digital_social_score",
    "safety_justice_expanded": "safety_justice_score",
}

router = APIRouter()


def _pillar_inputs(row: dict) -> dict:
    """Map a country row to the v2 LIVE pillar inputs (0-100)."""
    crime = row.get("crime_penalty_score")
    if crime is None:
        crime = row.get("violence_penalty_score", 0)
    return {
        "empowerment": row.get("empowerment_score", 0),
        "education_literacy": row.get("education_score", 0),
        "economic_inclusion": row.get("economic_score", 0),
        "health_survival": row.get("health_score", 0),
        "safety_crime_penalty": crime,
    }


def _v2_row(row: dict) -> dict:
    r = score(_pillar_inputs(row), V2)
    return {
        "iso_code": row.get("iso_code"), "country": row.get("country"),
        "rank": row.get("rank"), "tier": row.get("tier"),
        "version": "v2", "status": "official", "score": r["score"],
    }


def _v3_row(row: dict) -> dict:
    inputs = _pillar_inputs(row)
    r = score(inputs, V3)
    # which candidate pillars have data for this country
    candidate_coverage = {
        name: (row.get(field) not in (None, 0)) for name, field in _V3_CANDIDATES.items()
    }
    return {
        "iso_code": row.get("iso_code"), "country": row.get("country"),
        "version": "v3", "status": "shadow", "score": r["score"],
        "coverage": r["coverage"], "candidate_pillars_with_data": candidate_coverage,
    }


@router.get("/api/v2/scores", tags=["Scores (v2 official)"])
@router.get("/api/scores", tags=["Scores (v2 official)"])
def v2_scores():
    rows = get_global_scores()
    if not rows:
        raise HTTPException(503, "Data not available")
    return {"version": "v2", "status": "official", "count": len(rows),
            "data": [_v2_row(r) for r in rows]}


@router.get("/api/v2/scores/{iso_code}", tags=["Scores (v2 official)"])
def v2_score_one(iso_code: str):
    iso = iso_code.upper()
    for r in get_global_scores():
        if str(r.get("iso_code", "")).upper() == iso:
            return _v2_row(r)
    raise HTTPException(404, f"Country '{iso_code}' not found")


@router.get("/api/v3-preview/scores", tags=["Scores (v3 shadow)"])
def v3_preview_scores():
    """SHADOW ONLY — does not affect published scores or $SHE supply mechanics."""
    rows = get_global_scores()
    if not rows:
        raise HTTPException(503, "Shadow data unavailable")
    total = len(rows)
    pillar_totals = {name: 0 for name in _V3_CANDIDATES}
    out = []
    for r in rows:
        vr = _v3_row(r)
        for name, has in vr["candidate_pillars_with_data"].items():
            pillar_totals[name] += 1 if has else 0
        out.append(vr)
    return {
        "version": "v3", "status": "shadow",
        "notice": "SHADOW — v3 in validation. Does not affect published scores or $SHE supply mechanics.",
        "count": total,
        "pillar_coverage": {name: f"{n}/{total}" for name, n in pillar_totals.items()},
        "data": out,
    }
