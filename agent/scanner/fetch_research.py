"""
SHEtoken Agent — Academic Research Scanner
===========================================
Pulls weekly signals from two free academic databases:

  • arXiv   — open-access preprints (social science, economics, CS)
  • PubMed  — MEDLINE abstracts (public health, medicine, global health)

Why research papers?
--------------------
Academic papers arrive months after events but carry high credibility:
  • Systematic reviews give prevalence estimates (femicide rates, GBV stats)
  • Policy evaluations confirm/deny what news claims
  • Emerging topics surface here before mainstream media picks them up
  • Authors often cite country-level data → WEI country signal

Rate limits
-----------
arXiv:  no hard limit; be polite (≤3 req/3 s). No key required.
PubMed: 3 req/sec without API key.
        Set NCBI_API_KEY in .env for 10 req/sec (free, sign up at NCBI).

Output schema
-------------
Each item matches the standard pipeline article dict:
  source, language, region, tier, title, summary, text, url,
  published, fetched_at  +  platform ("arxiv" | "pubmed")

The SLM classifier scores these exactly like news articles; the tier
"research" will be surfaced in reports as a separate section.
"""

from __future__ import annotations

import logging
import os
import time
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta, timezone
from pathlib import Path
import sys

import feedparser
import requests

sys.path.insert(0, str(Path(__file__).parent.parent))
from config import REQUEST_TIMEOUT, MAX_ARTICLES_PER_SOURCE

logger = logging.getLogger(__name__)

NCBI_API_KEY = os.getenv("NCBI_API_KEY", "")

_UA = "SHEtoken-WEI-Research/2.0 (+https://shetoken.org)"

# ── arXiv query definitions ────────────────────────────────────────────────────
# Each tuple: (region_hint, pillar_hint, search_query)
# arXiv query syntax: ti:title  abs:abstract  cat:category
# Relevant categories: econ.GN, cs.CY, q-bio.PE, physics.soc-ph
# All queries use date-range via days_back at call time.

ARXIV_QUERIES: list[tuple[str, str, str]] = [

    # Safety & violence
    ("global", "safety_justice",
     "ti:gender+AND+ti:violence"),
    ("global", "safety_justice",
     "ti:domestic+AND+ti:violence+AND+abs:women"),
    ("global", "safety_justice",
     "ti:femicide+OR+ti:feminicide"),
    ("global", "safety_justice",
     "ti:intimate+AND+ti:partner+AND+ti:violence"),

    # Bodily autonomy
    ("global", "bodily_autonomy",
     "ti:child+AND+ti:marriage+AND+abs:gender"),
    ("global", "bodily_autonomy",
     "ti:reproductive+AND+ti:rights"),
    ("global", "bodily_autonomy",
     "ti:female+AND+ti:genital+AND+ti:mutilation"),
    ("global", "bodily_autonomy",
     "ti:abortion+AND+abs:policy"),

    # Economic empowerment
    ("global", "economic",
     "ti:gender+AND+ti:pay+AND+ti:gap"),
    ("global", "economic",
     "ti:women+AND+ti:labor+AND+abs:developing"),
    ("global", "economic",
     "ti:microfinance+AND+abs:women"),
    ("global", "economic",
     "ti:women+AND+ti:entrepreneurship"),

    # Education
    ("global", "education",
     "ti:girls+AND+ti:education+AND+abs:gender"),
    ("global", "education",
     "ti:female+AND+ti:literacy"),
    ("global", "education",
     "ti:gender+AND+ti:gap+AND+ti:education"),

    # Political empowerment
    ("global", "empowerment",
     "ti:women+AND+ti:political+AND+ti:participation"),
    ("global", "empowerment",
     "ti:gender+AND+ti:quota+AND+abs:parliament"),

    # Health
    ("global", "health",
     "ti:maternal+AND+ti:mortality"),
    ("global", "health",
     "ti:women+AND+ti:mental+AND+ti:health"),
    ("global", "health",
     "ti:gender+AND+ti:health+AND+abs:inequality"),

    # Digital violence
    ("global", "digital_social",
     "ti:online+AND+ti:harassment+AND+abs:women"),
    ("global", "digital_social",
     "ti:gender+AND+ti:digital+AND+ti:violence"),
]


# ── PubMed query definitions ────────────────────────────────────────────────────
# PubMed MeSH terms + free text; [Title/Abstract] restricts to title+abstract.
# Returns PMID list → fetch abstracts in bulk.

PUBMED_QUERIES: list[tuple[str, str, str]] = [

    # Safety
    ("global", "safety_justice",
     "gender based violence[Title/Abstract] OR domestic violence[Title/Abstract]"),
    ("global", "safety_justice",
     "femicide[Title/Abstract] OR feminicide[Title/Abstract]"),
    ("global", "safety_justice",
     "intimate partner violence[MeSH Terms]"),

    # Bodily autonomy
    ("global", "bodily_autonomy",
     "child marriage[Title/Abstract] AND women[Title/Abstract]"),
    ("global", "bodily_autonomy",
     "female genital mutilation[MeSH Terms]"),
    ("global", "bodily_autonomy",
     "reproductive rights[Title/Abstract] OR abortion access[Title/Abstract]"),

    # Maternal health
    ("global", "health",
     "maternal mortality[MeSH Terms]"),
    ("global", "health",
     "obstetric fistula[Title/Abstract]"),
    ("global", "health",
     "adolescent pregnancy[Title/Abstract] AND low income[Title/Abstract]"),

    # Education + economic
    ("global", "education",
     "girls education[Title/Abstract] AND developing countries[Title/Abstract]"),
    ("global", "economic",
     "gender pay gap[Title/Abstract] OR gender wage gap[Title/Abstract]"),
    ("global", "economic",
     "women economic empowerment[Title/Abstract]"),

    # Digital
    ("global", "digital_social",
     "technology facilitated abuse[Title/Abstract] OR cyber violence[Title/Abstract] AND women[Title/Abstract]"),
]


# ── arXiv fetcher ──────────────────────────────────────────────────────────────

def _arxiv_date_filter(entry, cutoff: datetime) -> bool:
    """True if entry is recent enough to include."""
    for attr in ("updated_parsed", "published_parsed"):
        raw = getattr(entry, attr, None)
        if raw:
            try:
                dt = datetime(*raw[:6], tzinfo=timezone.utc)
                return dt >= cutoff
            except Exception:
                pass
    return True  # no date → include


def fetch_arxiv_query(
    region: str,
    pillar: str,
    query: str,
    days_back: int = 7,
    max_results: int = 15,
) -> list[dict]:
    """
    Fetch one arXiv Atom feed query.
    Returns article-like dicts.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(days=days_back)
    url = (
        f"http://export.arxiv.org/api/query"
        f"?search_query={query}"
        f"&start=0"
        f"&max_results={max_results}"
        f"&sortBy=lastUpdatedDate"
        f"&sortOrder=descending"
    )

    try:
        resp = requests.get(url, headers={"User-Agent": _UA},
                            timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        feed = feedparser.parse(resp.text)

        results = []
        for entry in feed.entries:
            if not _arxiv_date_filter(entry, cutoff):
                continue

            title   = (getattr(entry, "title", "") or "").strip().replace("\n", " ")
            summary = (getattr(entry, "summary", "") or "").strip().replace("\n", " ")
            summary = re.sub(r"\s+", " ", summary)

            link = getattr(entry, "link", "") or ""
            if not title:
                continue

            # Publication date
            pub_raw = getattr(entry, "updated_parsed", None) or \
                      getattr(entry, "published_parsed", None)
            pub_iso = ""
            if pub_raw:
                try:
                    pub_iso = datetime(*pub_raw[:6], tzinfo=timezone.utc).isoformat()
                except Exception:
                    pass

            # Author list (first two authors)
            authors = [
                a.get("name", "") if isinstance(a, dict) else getattr(a, "name", "")
                for a in (getattr(entry, "authors", []) or [])[:2]
            ]
            author_str = "; ".join(a for a in authors if a)
            if author_str:
                summary = f"{author_str}. {summary}"

            results.append({
                "source":     f"arXiv/{query[:30]}",
                "language":   "en",
                "region":     region,
                "tier":       "research",
                "title":      title,
                "summary":    summary[:400],
                "text":       f"{title}. {summary}"[:900],
                "url":        link,
                "published":  pub_iso,
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "platform":   "arxiv",
                "pillar_hint": pillar,
            })

        time.sleep(1.0)   # polite delay
        return results

    except requests.exceptions.Timeout:
        logger.debug(f"  arXiv timeout: '{query[:40]}' (skipped)")
        return []
    except Exception as exc:
        logger.warning(f"  arXiv query failed '{query[:40]}': {exc}")
        return []


def fetch_all_arxiv(days_back: int = 7) -> list[dict]:
    """Run all arXiv queries; return deduplicated flat list."""
    all_articles: list[dict] = []
    seen_urls: set[str] = set()

    logger.info(f"  arXiv: running {len(ARXIV_QUERIES)} queries ({days_back}d lookback)...")
    for region, pillar, query in ARXIV_QUERIES:
        for art in fetch_arxiv_query(region, pillar, query, days_back):
            url = art.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_articles.append(art)

    logger.info(f"  arXiv total: {len(all_articles)} unique papers")
    return all_articles


# ── PubMed fetcher ─────────────────────────────────────────────────────────────

_ESEARCH = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
_EFETCH  = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

# PubMed XML namespaces
_NS: dict[str, str] = {}


def _ncbi_params(extra: dict) -> dict:
    """Base params for every NCBI call."""
    p: dict = {"retmode": "json", **extra}
    if NCBI_API_KEY:
        p["api_key"] = NCBI_API_KEY
    return p


def _fetch_pubmed_abstracts(pmids: list[str]) -> list[dict]:
    """
    Fetch abstracts for a list of PubMed IDs.
    Returns list of {pmid, title, abstract, pub_date, url}.
    """
    if not pmids:
        return []

    try:
        resp = requests.get(
            _EFETCH,
            params={
                "db":      "pubmed",
                "id":      ",".join(pmids),
                "rettype": "abstract",
                "retmode": "xml",
                **({"api_key": NCBI_API_KEY} if NCBI_API_KEY else {}),
            },
            headers={"User-Agent": _UA},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()

        root     = ET.fromstring(resp.content)
        articles = []

        for article_el in root.findall(".//PubmedArticle"):
            # Title
            title_el = article_el.find(".//ArticleTitle")
            title = (title_el.text or "").strip() if title_el is not None else ""
            if not title:
                continue

            # Abstract
            abstract_parts = article_el.findall(".//AbstractText")
            abstract = " ".join(
                (el.text or "") for el in abstract_parts if el.text
            ).strip()

            # PMID
            pmid_el = article_el.find(".//PMID")
            pmid    = pmid_el.text.strip() if pmid_el is not None else ""

            # Publication date
            year_el  = article_el.find(".//PubDate/Year")
            month_el = article_el.find(".//PubDate/Month")
            pub_iso  = ""
            if year_el is not None and year_el.text:
                pub_iso = year_el.text
                if month_el is not None and month_el.text:
                    # Month may be "Jan", "Feb", etc.
                    try:
                        m = datetime.strptime(month_el.text[:3], "%b").month
                        pub_iso = f"{year_el.text}-{m:02d}-01"
                    except Exception:
                        pub_iso = f"{year_el.text}-01-01"

            articles.append({
                "pmid":     pmid,
                "title":    title,
                "abstract": abstract,
                "pub_iso":  pub_iso,
                "url":      f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
            })

        time.sleep(0.35 if NCBI_API_KEY else 0.35)  # ≤3/s without key
        return articles

    except Exception as exc:
        logger.warning(f"  PubMed efetch error: {exc}")
        return []


def fetch_pubmed_query(
    region: str,
    pillar: str,
    term: str,
    days_back: int = 7,
    max_results: int = 20,
) -> list[dict]:
    """
    Search PubMed for recent articles matching *term*.
    Returns pipeline-compatible article dicts.
    """
    try:
        resp = requests.get(
            _ESEARCH,
            params=_ncbi_params({
                "db":       "pubmed",
                "term":     term,
                "datetype": "pdat",
                "reldate":  str(days_back),
                "retmax":   str(max_results),
                "retmode":  "json",
            }),
            headers={"User-Agent": _UA},
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data  = resp.json()
        pmids = data.get("esearchresult", {}).get("idlist", [])

        if not pmids:
            time.sleep(0.35)
            return []

        time.sleep(0.35)
        raw = _fetch_pubmed_abstracts(pmids)

        results = []
        now_iso = datetime.now(timezone.utc).isoformat()

        for art in raw:
            title    = art["title"]
            abstract = art["abstract"] or title
            results.append({
                "source":     f"PubMed/{term[:30]}",
                "language":   "en",
                "region":     region,
                "tier":       "research",
                "title":      title,
                "summary":    abstract[:400],
                "text":       f"{title}. {abstract}"[:900],
                "url":        art["url"],
                "published":  art["pub_iso"],
                "fetched_at": now_iso,
                "platform":   "pubmed",
                "pillar_hint": pillar,
            })

        return results

    except Exception as exc:
        logger.warning(f"  PubMed query failed '{term[:40]}': {exc}")
        return []


def fetch_all_pubmed(days_back: int = 7) -> list[dict]:
    """Run all PubMed queries; return deduplicated flat list."""
    all_articles: list[dict] = []
    seen_urls: set[str] = set()

    logger.info(f"  PubMed: running {len(PUBMED_QUERIES)} queries ({days_back}d lookback)...")
    for region, pillar, term in PUBMED_QUERIES:
        for art in fetch_pubmed_query(region, pillar, term, days_back):
            url = art.get("url", "")
            if url and url not in seen_urls:
                seen_urls.add(url)
                all_articles.append(art)

    logger.info(f"  PubMed total: {len(all_articles)} unique papers")
    return all_articles


# ── Combined entry point ───────────────────────────────────────────────────────

def fetch_all_research(days_back: int = 7) -> list[dict]:
    """
    Run arXiv + PubMed scanners and return combined deduplicated list.

    Args:
        days_back: how many days of papers to retrieve (default 7 = weekly run)

    Returns:
        list of pipeline-compatible article dicts with tier="research"
    """
    arxiv_arts  = fetch_all_arxiv(days_back=days_back)
    pubmed_arts = fetch_all_pubmed(days_back=days_back)

    total = arxiv_arts + pubmed_arts
    logger.info(
        f"  Research total: {len(total)} papers "
        f"(arXiv: {len(arxiv_arts)}, PubMed: {len(pubmed_arts)})"
    )
    return total
