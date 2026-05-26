"""
SHEtoken Agent — GDELT v2 Document API Scanner
===============================================
GDELT (Global Database of Events, Language, and Tone) monitors every
news article published online across 100+ languages in 65+ countries.

Why GDELT is better than scraping news sites
---------------------------------------------
• No API key required — completely free
• Zero 403s / timeouts — designed for machine access
• Returns structured country + language metadata on every article
• Indexes sources that actively block scrapers (The Hindu, HT, Times of India...)
• GKG theme codes let you query `theme:WOMEN_RIGHTS` directly
• Processes 100M+ events per day — nothing slips through

GDELT DOC API docs: https://blog.gdeltproject.org/gdelt-doc-2-0-api-debuts/
Theme list: https://www.gdeltproject.org/data/lookups/GKG.Themes.txt

Rate limit: ~1 request/second (GDELT asks nicely, no hard block)
Response: article title + URL + domain + language + country + date

Note: artlist mode returns TITLES only, not full article text.
The SLM classifier works purely from the title for GDELT items.
This is intentional — GDELT's 65-language coverage is the value,
not full article text.
"""

from __future__ import annotations

import logging
import time
from datetime import datetime, timedelta, timezone

import requests

logger = logging.getLogger(__name__)

GDELT_DOC_API = "https://api.gdeltproject.org/api/v2/doc/doc"

# Polite but honest user-agent
_UA = "SHEtoken-WEI-Research/2.0 (+https://shetoken.org)"

# ── Query definitions ──────────────────────────────────────────────────────────
# Each tuple: (pillar_hint, query_string)
# GKG theme codes (theme:X) bypass language barriers — GDELT applies them
# across all languages automatically.
# Free-text terms catch headlines that aren't tagged by GKG yet.

GDELT_QUERIES: list[tuple[str, str]] = [

    # ── Women's safety & violence ─────────────────────────────────────────────
    ("safety_justice",
     'theme:HUMAN_RIGHTS_GENDER "domestic violence" OR "femicide" OR "rape"'),
    ("safety_justice",
     '"acid attack" OR "honour killing" OR "dowry death" OR "trafficking women"'),
    ("safety_justice",
     '"gender based violence" OR "violence against women" '
     'sourcecountry:India OR sourcecountry:Pakistan OR sourcecountry:Bangladesh'),
    ("safety_justice",
     '"feminicidio" OR "violencia doméstica" OR "feminicídio"'),   # LatAm
    ("safety_justice",
     '"sexual violence" OR "gender violence" '
     'sourcecountry:Nigeria OR sourcecountry:Kenya OR sourcecountry:Ethiopia'),

    # ── Bodily autonomy ───────────────────────────────────────────────────────
    ("bodily_autonomy",
     'theme:HUMAN_RIGHTS_ABUSES "child marriage" OR "child bride"'),
    ("bodily_autonomy",
     '"FGM" OR "female genital" OR "reproductive rights" OR "abortion ban"'),
    ("bodily_autonomy",
     '"period poverty" OR "menstrual" sourcelang:English'),
    ("bodily_autonomy",
     '"बाल विवाह" OR "गर्भपात" sourcelang:Hindi'),           # child marriage / abortion Hindi
    ("bodily_autonomy",
     '"زواج الأطفال" OR "ختان الإناث" sourcelang:Arabic'),    # child marriage / FGM Arabic

    # ── Economic empowerment ──────────────────────────────────────────────────
    ("economic",
     '"gender pay gap" OR "women workforce" OR "female unemployment"'),
    ("economic",
     '"women entrepreneur" OR "microfinance women" OR "self help group"'),
    ("economic",
     '"mahila" OR "kudumbashree" OR "jeevika" sourcelang:Hindi OR sourcelang:Tamil'),

    # ── Education ─────────────────────────────────────────────────────────────
    ("education",
     '"girl education" OR "female literacy" OR "girls school closed"'),
    ("education",
     '"kanyashree" OR "beti bachao" OR "ladki" sourcelang:Hindi'),
    ("education",
     '"girls dropout" OR "school girls" sourcecountry:Afghanistan '
     'OR sourcecountry:Pakistan OR sourcecountry:Mali'),

    # ── Political empowerment ─────────────────────────────────────────────────
    ("empowerment",
     '"women parliament" OR "female president" OR "gender quota" OR "women elected"'),
    ("empowerment",
     '"महिला सांसद" OR "नारी शक्ति" sourcelang:Hindi'),       # women MP / women power
    ("empowerment",
     '"female minister" OR "women cabinet" sourcecountry:India '
     'OR sourcecountry:Nigeria OR sourcecountry:Kenya'),

    # ── Health ────────────────────────────────────────────────────────────────
    ("health",
     '"maternal mortality" OR "maternal death" OR "obstetric fistula"'),
    ("health",
     '"women mental health" OR "postpartum depression" OR "anaemia women"'),
    ("health",
     '"मातृ मृत्यु" OR "प्रसव" sourcelang:Hindi'),             # maternal mortality Hindi
    ("health",
     '"cervical cancer" OR "breast cancer screening" sourcelang:English'),

    # ── Digital & online violence ─────────────────────────────────────────────
    ("digital_social",
     '"deepfake women" OR "revenge porn" OR "cyber harassment women"'),
    ("digital_social",
     '"online abuse women" OR "image-based abuse" OR "sextortion"'),

    # ── Dignity & welfare ─────────────────────────────────────────────────────
    ("dignity_welfare",
     '"widow rights" OR "widow property" OR "widows evicted"'),
    ("dignity_welfare",
     '"unpaid care work" OR "women poverty" OR "female homelessness"'),

    # ── Global institution releases (high credibility) ────────────────────────
    ("empowerment",
     'domain:unwomen.org OR domain:unfpa.org OR domain:un.org "women"'),
    ("health",
     'domain:who.int "women" OR "maternal" OR "reproductive"'),
    ("economic",
     'domain:worldbank.org "women" OR "gender"'),
    ("safety_justice",
     'domain:hrw.org OR domain:amnesty.org "women" OR "gender"'),
]


# ── Language code mapping ──────────────────────────────────────────────────────

_LANG_MAP = {
    "English": "en", "Hindi": "hi", "Bengali": "bn", "Urdu": "ur",
    "Arabic": "ar", "Portuguese": "pt", "Spanish": "es", "French": "fr",
    "Tamil": "ta", "Telugu": "te", "Marathi": "mr", "Swahili": "sw",
    "Indonesian": "id", "Malay": "id",
}


def _parse_date(gdelt_date: str) -> str:
    """Convert GDELT date '20260519T120000Z' → ISO 8601."""
    try:
        return datetime.strptime(gdelt_date, "%Y%m%dT%H%M%SZ").replace(
            tzinfo=timezone.utc
        ).isoformat()
    except Exception:
        return ""


def _date_str(dt: datetime) -> str:
    return dt.strftime("%Y%m%d%H%M%S")


def fetch_gdelt_query(
    pillar: str,
    query: str,
    days_back: int = 7,
    max_records: int = 50,
) -> list[dict]:
    """
    Run one GDELT DOC API query.
    Returns list of article dicts compatible with the rest of the pipeline.
    """
    end_dt   = datetime.now(timezone.utc)
    start_dt = end_dt - timedelta(days=days_back)

    try:
        resp = requests.get(
            GDELT_DOC_API,
            params={
                "query":         query,
                "mode":          "artlist",
                "maxrecords":    str(max_records),
                "format":        "json",
                "startdatetime": _date_str(start_dt),
                "enddatetime":   _date_str(end_dt),
                "sort":          "DateDesc",
            },
            headers={"User-Agent": _UA},
            timeout=20,
        )
        if resp.status_code == 429:
            logger.debug(f"  GDELT 429 on '{query[:55]}' — backing off 15s")
            time.sleep(15)
            return []
        resp.raise_for_status()

        raw_text = resp.text.strip()
        if not raw_text:
            time.sleep(2.0)
            return []

        try:
            data = resp.json()
        except ValueError:
            logger.debug(f"  GDELT non-JSON response ({len(resp.text)}B): {resp.text[:80]!r}")
            time.sleep(2.0)
            return []
        raw_arts = data.get("articles") or []

        results = []
        for art in raw_arts:
            title = (art.get("title") or "").strip()
            url   = (art.get("url") or "").strip()
            if not title or not url:
                continue

            lang_name = art.get("language", "English")
            lang_code = _LANG_MAP.get(lang_name, "en")
            country   = art.get("sourcecountry", "")
            domain    = art.get("domain", "gdelt")
            published = _parse_date(art.get("seendate", ""))

            results.append({
                "source":            f"GDELT/{domain}",
                "language":          lang_code,
                "region":            country or "global",
                "tier":              "global",
                "title":             title,
                "summary":           title,
                "text":              title,
                "url":               url,
                "published":         published,
                "fetched_at":        datetime.now(timezone.utc).isoformat(),
                "platform":          "gdelt",
                "gdelt_pillar_hint": pillar,
            })

        time.sleep(1.5)   # GDELT asks for ~1 req/sec; 1.5s gives headroom
        logger.debug(f"  GDELT | '{query[:55]}' → {len(results)} articles")
        return results

    except requests.exceptions.Timeout:
        logger.debug(f"  GDELT timeout: '{query[:55]}' (skipped)")
        time.sleep(2.0)
        return []
    except Exception as exc:
        logger.warning(f"  GDELT query failed '{query[:55]}': {exc}")
        time.sleep(2.0)   # always sleep so failures don't pile up
        return []


def fetch_all_gdelt(days_back: int = 7) -> list[dict]:
    """
    Run all GDELT queries and return a deduplicated flat list.
    Deduplication here is by URL only; the pipeline-level dedup.py handles
    cross-week deduplication.
    """
    all_articles: list[dict] = []
    seen_urls:    set[str]   = set()

    # Quick probe — skip all queries if GDELT is unreachable or returning non-JSON
    try:
        probe = requests.get(
            GDELT_DOC_API,
            params={"query": "women", "mode": "artlist", "maxrecords": "1", "format": "json"},
            headers={"User-Agent": _UA},
            timeout=10,
        )
        if probe.status_code != 200:
            logger.warning(f"  GDELT API probe returned {probe.status_code} — skipping all {len(GDELT_QUERIES)} queries")
            return []
        probe.json()  # raises ValueError if response isn't JSON
    except ValueError:
        logger.warning("  GDELT API returning non-JSON — skipping all queries")
        return []
    except Exception as exc:
        logger.warning(f"  GDELT API unreachable ({exc}) — skipping all queries")
        return []

    logger.info(f"  GDELT: running {len(GDELT_QUERIES)} queries ({days_back}d lookback)...")

    for pillar, query in GDELT_QUERIES:
        for art in fetch_gdelt_query(pillar, query, days_back):
            url = art.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_articles.append(art)

    logger.info(f"  GDELT total: {len(all_articles)} unique articles")
    return all_articles
