"""
SHEtoken Agent — LLM Scout
===========================
Uses Claude (with web_search tool) to gather signal intelligence for
high-priority countries that produced zero organic signals from RSS/GDELT
in a given week.

Why this matters
----------------
RSS and GDELT rely on news being published AND indexed. In a quiet news week,
countries in the Global South may genuinely have no English-language coverage
even though events are happening. The LLM Scout fills that gap by asking
Claude to search for recent events in specific countries/pillars.

How it works
------------
1. Given a list of countries with no signals this week
2. For each (country, pillar) pair below the priority threshold
3. Ask Claude with web_search: "find recent events about X in Y"
4. Parse Claude's response into article-like items
5. Feed those into the standard SLM classifier

Cost management
---------------
• Only runs for countries with ZERO organic signals (RSS + GDELT)
• Queries at most MAX_SCOUT_COUNTRIES countries per run
• Uses claude-haiku (cheapest model with web search)
• Each query costs ~$0.002–0.005 depending on response length
• Default: 10 countries × 3 pillars = ~30 queries ≈ $0.10–0.15/week

Setup
-----
Add to .env:
    ANTHROPIC_API_KEY=sk-ant-...

If key is absent, this scanner is silently skipped.

Alternative: Perplexity API
----------------------------
If you prefer Perplexity (better real-time search, different cost structure):
    PERPLEXITY_API_KEY=pplx-...
This file supports both — set whichever key you have.
"""

from __future__ import annotations

import json
import logging
import os
import re
import time
from datetime import datetime, timezone
from typing import Optional

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY  = os.getenv("ANTHROPIC_API_KEY", "")
PERPLEXITY_API_KEY = os.getenv("PERPLEXITY_API_KEY", "")

# Limit scout queries per run to control cost
MAX_SCOUT_COUNTRIES = int(os.getenv("LLM_SCOUT_MAX_COUNTRIES", "10"))
MAX_PILLARS_PER_RUN = int(os.getenv("LLM_SCOUT_MAX_PILLARS", "3"))

# High-priority countries to scout when organic signals are thin
# These are the countries where news coverage is sparser in English
PRIORITY_COUNTRIES = [
    "Afghanistan", "Ethiopia", "DRC", "Somalia", "Sudan",
    "Yemen", "Myanmar", "Cambodia", "Haiti", "Mali",
    "Niger", "Burkina Faso", "Chad", "Central African Republic",
    "Papua New Guinea", "Guatemala", "Bolivia",
]

# Pillars to scout (highest WEI impact first)
SCOUT_PILLARS = [
    ("safety_justice",   "violence against women, femicide, domestic violence, sexual assault, honour killing"),
    ("bodily_autonomy",  "child marriage, FGM, reproductive rights, forced marriage, abortion bans"),
    ("empowerment",      "women in parliament, female leadership, gender equality laws, women's rights legislation"),
]


# ── Anthropic backend ──────────────────────────────────────────────────────────

def _query_claude(country: str, pillar: str, pillar_desc: str,
                  week_str: str) -> list[dict]:
    """
    Ask Claude (with web search) for recent women's-rights events in a country.
    Returns article-like dicts.
    """
    if not ANTHROPIC_API_KEY:
        return []

    try:
        import anthropic
    except ImportError:
        logger.warning("  LLM Scout: 'anthropic' package not installed — pip install anthropic")
        return []

    client  = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    prompt  = (
        f"Search for news and events from the past 7 days ({week_str}) about "
        f"{pillar_desc} in {country}. "
        f"Focus on concrete events: laws passed or proposed, crimes reported with statistics, "
        f"policy changes, court rulings, government programs, or NGO reports. "
        f"For each event found, provide:\n"
        f"- A factual headline (not your summary — the actual article/event title)\n"
        f"- 1-2 sentence description of what happened\n"
        f"- Source name and URL if available\n"
        f"- Date\n\n"
        f"Return ONLY a JSON array in this exact format:\n"
        f'[{{"title": "...", "description": "...", "url": "...", "source": "...", "date": "..."}}]\n'
        f"If no relevant events found in the past 7 days, return an empty array []."
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5",  # cheapest model; good enough for search + structure
            max_tokens=1200,
            tools=[{"type": "web_search_20250305", "name": "web_search",
                    "max_uses": 3}],
            messages=[{"role": "user", "content": prompt}],
        )

        # Extract text from response
        text_parts = [
            block.text for block in response.content
            if hasattr(block, "text")
        ]
        full_text = "\n".join(text_parts)

        return _parse_scout_response(full_text, country, pillar)

    except anthropic.APIStatusError as exc:
        logger.warning(f"  LLM Scout Claude error ({country}/{pillar}): {exc.status_code}")
        return []
    except Exception as exc:
        logger.warning(f"  LLM Scout Claude failed ({country}/{pillar}): {exc}")
        return []


# ── Perplexity backend ─────────────────────────────────────────────────────────

def _query_perplexity(country: str, pillar: str, pillar_desc: str,
                      week_str: str) -> list[dict]:
    """
    Ask Perplexity (online model with web search) for recent events.
    Perplexity's 'sonar' models have live web access built in.
    """
    if not PERPLEXITY_API_KEY:
        return []

    try:
        import httpx
    except ImportError:
        logger.warning("  LLM Scout: 'httpx' not installed — pip install httpx")
        return []

    prompt = (
        f"Find news from the past 7 days ({week_str}) about {pillar_desc} "
        f"in {country}. Return a JSON array of up to 5 events:\n"
        f'[{{"title": "...", "description": "one sentence", '
        f'"url": "...", "source": "...", "date": "YYYY-MM-DD"}}]\n'
        f"Return [] if nothing found. JSON only, no other text."
    )

    try:
        resp = httpx.post(
            "https://api.perplexity.ai/chat/completions",
            json={
                "model":       "llama-3.1-sonar-small-128k-online",
                "messages":    [{"role": "user", "content": prompt}],
                "max_tokens":  800,
                "temperature": 0.1,
            },
            headers={
                "Authorization": f"Bearer {PERPLEXITY_API_KEY}",
                "Content-Type":  "application/json",
            },
            timeout=25.0,
        )
        resp.raise_for_status()
        content = resp.json()["choices"][0]["message"]["content"]
        return _parse_scout_response(content, country, pillar)

    except Exception as exc:
        logger.warning(f"  LLM Scout Perplexity failed ({country}/{pillar}): {exc}")
        return []


# ── Response parser ────────────────────────────────────────────────────────────

def _parse_scout_response(text: str, country: str, pillar: str) -> list[dict]:
    """
    Extract JSON array from LLM response and convert to pipeline article dicts.
    Handles markdown fences and partial JSON gracefully.
    """
    # Strip markdown fences
    text = re.sub(r"```(?:json)?\s*", "", text).strip()

    # Find the first [...] block
    match = re.search(r"\[.*?\]", text, re.DOTALL)
    if not match:
        return []

    try:
        items = json.loads(match.group())
    except json.JSONDecodeError:
        return []

    if not isinstance(items, list):
        return []

    results = []
    now_iso = datetime.now(timezone.utc).isoformat()

    for item in items:
        if not isinstance(item, dict):
            continue
        title = (item.get("title") or "").strip()
        desc  = (item.get("description") or title).strip()
        if not title or len(title) < 10:
            continue

        url    = (item.get("url") or "").strip()
        source = (item.get("source") or "LLM Scout").strip()
        date   = (item.get("date") or "").strip()

        results.append({
            "source":       f"LLMScout/{source}",
            "language":     "en",
            "region":       country,
            "tier":         "scout",
            "title":        title,
            "summary":      desc[:400],
            "text":         f"{title}. {desc}"[:900],
            "url":          url or f"llm-scout://{country}/{pillar}/{hash(title)}",
            "published":    date,
            "fetched_at":   now_iso,
            "platform":     "llm_scout",
            "scout_country": country,
            "scout_pillar":  pillar,
            # Flag so the classifier knows this came from LLM synthesis
            "llm_generated": True,
        })

    return results


# ── Main entry point ───────────────────────────────────────────────────────────

def _pick_backend(country: str, pillar: str, pillar_desc: str,
                  week_str: str) -> list[dict]:
    """Try Claude first, fall back to Perplexity."""
    if ANTHROPIC_API_KEY:
        results = _query_claude(country, pillar, pillar_desc, week_str)
        if results:
            return results

    if PERPLEXITY_API_KEY:
        return _query_perplexity(country, pillar, pillar_desc, week_str)

    return []


def fetch_llm_scout(
    zero_signal_countries: Optional[list[str]] = None,
    week_str: str = "",
) -> list[dict]:
    """
    Query LLM for intelligence on countries that produced no organic signals.

    Args:
        zero_signal_countries: countries with no signals from RSS/GDELT this week.
                               If None, uses the built-in PRIORITY_COUNTRIES list.
        week_str: e.g. "2026-W21" for logging

    Returns:
        list of article-like dicts ready for the SLM classifier.
    """
    if not ANTHROPIC_API_KEY and not PERPLEXITY_API_KEY:
        logger.debug("  LLM Scout: skipped (no ANTHROPIC_API_KEY or PERPLEXITY_API_KEY)")
        return []

    backend = "Claude" if ANTHROPIC_API_KEY else "Perplexity"

    # Which countries to scout
    candidates = zero_signal_countries or PRIORITY_COUNTRIES
    to_scout   = candidates[:MAX_SCOUT_COUNTRIES]
    pillars    = SCOUT_PILLARS[:MAX_PILLARS_PER_RUN]

    logger.info(
        f"  LLM Scout ({backend}): scouting {len(to_scout)} countries "
        f"× {len(pillars)} pillars..."
    )

    all_results: list[dict] = []
    seen_titles: set[str]   = set()

    for country in to_scout:
        for pillar, pillar_desc in pillars:
            items = _pick_backend(country, pillar, pillar_desc, week_str)
            for item in items:
                t = item["title"].lower()
                if t not in seen_titles:
                    seen_titles.add(t)
                    all_results.append(item)
            if items:
                logger.info(f"  LLM Scout: {country}/{pillar} → {len(items)} events")
            time.sleep(0.5)   # avoid API rate limits

    logger.info(f"  LLM Scout total: {len(all_results)} items")
    return all_results
