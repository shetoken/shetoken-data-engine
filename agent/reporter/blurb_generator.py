"""
agent/reporter/blurb_generator.py
===================================
Generates a 2-sentence WEI performance summary per country using Phi-3.5 (Ollama).

Design:
  - Receives already-classified signals (in-memory, from run_agent.py) → no extra I/O
  - Filters signals by country code (single string field, matching slm_classifier output)
  - SLM writes prose from signal 'summary_en' snippets — URLs never enter the prompt
  - Python attaches the real article URLs from signal metadata → zero hallucination risk
  - Writes country_blurbs.json to agent/output/live/
  - Upserts to Supabase she_country_blurbs table if credentials present

Called from run_agent.py (Step 5c) after wei_updater and sister_updater,
before the distribution step.
"""

from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

# ── Paths ─────────────────────────────────────────────────────────────────────
_AGENT_DIR   = Path(__file__).resolve().parents[1]          # agent/
_LIVE_DIR    = _AGENT_DIR / "output" / "live"
_BLURBS_FILE = _LIVE_DIR / "country_blurbs.json"

# ── Model / Ollama ────────────────────────────────────────────────────────────
OLLAMA_HOST  = os.getenv("OLLAMA_HOST", "http://localhost:11434")
BLURB_MODEL  = "phi3.5"     # English output only — faster than qwen, plenty for prose
TEMPERATURE  = 0.15         # Slightly looser than classifier (0.1) for natural variation
MAX_SIGNALS  = 3            # Top signals per country fed into prompt
MAX_TOKENS   = 120          # Enough for 2 clean sentences

# ── Supabase ──────────────────────────────────────────────────────────────────
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY",
               os.getenv("SUPABASE_ANON_KEY", ""))

# ── Prompt ────────────────────────────────────────────────────────────────────
BLURB_PROMPT = """\
You are a concise gender-equality analyst writing for a financial intelligence platform.
Given the data and recent news signals below, write exactly 2 sentences in plain English:
  Sentence 1: The most significant recent WEI-relevant development for this country.
  Sentence 2: The single most impactful policy change that would raise this country's score.

Rules:
- No URLs, bullet points, headings, or markdown.
- Output the 2 sentences only — nothing else.
- Keep each sentence under 30 words.

Country:          {country}
WEI Score:        {wei_score:.1f} / 100  (Tier {tier})
Strongest pillar: {best_pillar} ({best_score:.1f})
Weakest pillar:   {worst_pillar} ({worst_score:.1f})
Weekly trend:     {weekly_delta:+.2f} pts

Recent classified signals:
{signal_summaries}
"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _signals_for_country(signals: list[dict], iso: str) -> list[dict]:
    """
    Filter and rank signals for one country.
    Signal 'country' field is a single ISO-3 string (set by resolve_geography).
    """
    iso_up = iso.upper()
    relevant = [
        s for s in signals
        if (s.get("country") or "").upper() == iso_up
        and s.get("pillar", "none") != "none"
        and s.get("direction", 0) != 0
        and s.get("url")
        and s.get("summary_en")     # classifier always writes summary_en
    ]
    # Sort by confidence × severity — highest relevance first
    relevant.sort(
        key=lambda s: float(s.get("confidence", 0)) * float(s.get("severity", 0)),
        reverse=True,
    )
    return relevant[:MAX_SIGNALS]


def _pillar_extremes(row: dict) -> tuple[str, float, str, float]:
    """Return (best_label, best_score, worst_label, worst_score)."""
    pillars = {
        "Empowerment":       float(row.get("empowerment_score")     or 0),
        "Education":         float(row.get("education_score")       or 0),
        "Economic":          float(row.get("economic_score")        or 0),
        "Health":            float(row.get("health_score")          or 0),
        "Safety & Justice":  float(row.get("safety_justice_score")  or 0),
        "Bodily Autonomy":   float(row.get("bodily_autonomy_score") or 0),
        "Dignity & Welfare": float(row.get("dignity_welfare_score") or 0),
        "Digital & Social":  float(row.get("digital_social_score")  or 0),
    }
    best  = max(pillars, key=pillars.__getitem__)
    worst = min(pillars, key=pillars.__getitem__)
    return best, pillars[best], worst, pillars[worst]


def _call_ollama(prompt: str) -> Optional[str]:
    """POST to Ollama /api/generate. Returns stripped text or None on error."""
    try:
        import httpx
        resp = httpx.post(
            f"{OLLAMA_HOST}/api/generate",
            json={
                "model":   BLURB_MODEL,
                "prompt":  prompt,
                "stream":  False,
                "options": {"temperature": TEMPERATURE, "num_predict": MAX_TOKENS},
            },
            timeout=30.0,
        )
        resp.raise_for_status()
        return resp.json().get("response", "").strip()
    except Exception as exc:
        logger.error("Ollama blurb call failed: %s", exc)
        return None


def _push_to_supabase(blurbs: dict[str, dict]) -> None:
    """
    Upsert all generated blurbs into Supabase she_country_blurbs.
    Uses the same httpx + REST pattern as supabase_source.py.
    Silent if credentials are missing.
    """
    if not SUPABASE_URL or not SUPABASE_KEY:
        logger.debug("Supabase not configured — skipping blurb push")
        return

    rows = [
        {
            "iso_code":            iso,
            "country":             d["country"],
            "performance_summary": d["performance_summary"],
            "sources":             json.dumps(d["sources"]),
            "generated_at":        datetime.now(timezone.utc).isoformat(),
            "model":               BLURB_MODEL,
        }
        for iso, d in blurbs.items()
    ]
    try:
        import httpx
        resp = httpx.post(
            f"{SUPABASE_URL}/rest/v1/she_country_blurbs",
            headers={
                "apikey":        SUPABASE_KEY,
                "Authorization": f"Bearer {SUPABASE_KEY}",
                "Content-Type":  "application/json",
                "Prefer":        "resolution=merge-duplicates",
            },
            json=rows,
            timeout=20.0,
        )
        resp.raise_for_status()
        logger.info("Pushed %d blurbs to Supabase she_country_blurbs", len(rows))
    except Exception as exc:
        logger.error("Supabase blurb push failed: %s", exc)


# ── Main entry point ──────────────────────────────────────────────────────────

def generate_blurbs(
    country_rows: list[dict],
    signals: list[dict],
    live_dir: Path = _LIVE_DIR,
    dry_run: bool = False,
) -> dict[str, dict]:
    """
    Generate 2-sentence performance blurbs for countries that have signal coverage.

    Args:
        country_rows: List of country dicts (from wei_updater live output).
        signals:      Classified signals already in memory from the pipeline.
        live_dir:     Where to write country_blurbs.json.
        dry_run:      Skip Ollama calls and Supabase writes.

    Returns:
        Dict of iso_code → { country, performance_summary, sources[] }.
        Countries with no signals are omitted — API/frontend falls back to template.
    """
    live_dir.mkdir(parents=True, exist_ok=True)

    logger.info(
        "Blurb generation: %d countries, %d signals available",
        len(country_rows), len(signals),
    )

    blurbs: dict[str, dict] = {}
    skipped = 0

    for i, row in enumerate(country_rows):
        iso     = str(row.get("iso_code", "")).upper()
        country = row.get("country", iso)
        if not iso:
            continue

        country_signals = _signals_for_country(signals, iso)
        if not country_signals:
            skipped += 1
            continue        # No signals → frontend uses template blurb, no SLM call

        signal_lines = "\n".join(
            f"- [{s.get('pillar', '?').upper()}] {s['summary_en']}"
            for s in country_signals
        )

        best_label, best_score, worst_label, worst_score = _pillar_extremes(row)
        prompt = BLURB_PROMPT.format(
            country          = country,
            wei_score        = float(row.get("wei_score") or 0),
            tier             = int(row.get("tier") or 0),
            best_pillar      = best_label,
            best_score       = best_score,
            worst_pillar     = worst_label,
            worst_score      = worst_score,
            weekly_delta     = float(row.get("weekly_delta") or 0),
            signal_summaries = signal_lines,
        )

        if dry_run:
            blurb_text = (
                f"[dry-run] {country} has recent signal activity in {country_signals[0]['pillar']}. "
                f"Improving {worst_label} would most raise the WEI score."
            )
        else:
            blurb_text = _call_ollama(prompt)

        if not blurb_text:
            skipped += 1
            continue

        blurbs[iso] = {
            "country":             country,
            "performance_summary": blurb_text,
            "sources": [
                {
                    "title":  s.get("title", ""),
                    "url":    s["url"],
                    "source": s.get("source", ""),
                    "date":   s.get("published", ""),
                    "pillar": s.get("pillar", ""),
                }
                for s in country_signals
            ],
        }

        if (i + 1) % 20 == 0:
            logger.info("  Blurbs: %d / %d processed", i + 1, len(country_rows))

    logger.info(
        "Blurbs complete: %d generated, %d skipped (no signals)",
        len(blurbs), skipped,
    )

    if not dry_run:
        blurbs_file = live_dir / "country_blurbs.json"
        with open(blurbs_file, "w", encoding="utf-8") as f:
            json.dump(blurbs, f, ensure_ascii=False, indent=2)
        logger.info("Written → %s", blurbs_file)
        _push_to_supabase(blurbs)

    return blurbs
