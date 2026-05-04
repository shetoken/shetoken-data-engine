"""
SHEtoken Agent — YouTube Scanner
===================================
Searches YouTube for WEI-relevant video content using
the YouTube Data API v3 (free, 10,000 units/day).

Setup:
    1. Go to console.cloud.google.com
    2. Enable YouTube Data API v3
    3. Create API Key (no OAuth needed for search)
    4. Add YOUTUBE_API_KEY to .env

What it scans:
    - News channels posting about women's rights
    - Documentary content on WEI pillars
    - Government program announcement videos
    - NGO campaign content

Why YouTube for WEI signals:
    - Multilingual — covers Hindi, Bengali, Tamil, Spanish, Portuguese
    - High-credibility sources (BBC, Al Jazeera, UN Women channels)
    - Video descriptions contain detailed information for SLM classification
    - Comments section signals community sentiment
"""
import requests, time, logging, sys, re
from datetime import datetime, timezone, timedelta
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import WEI_KEYWORDS, MAX_ARTICLE_LENGTH, REQUEST_TIMEOUT
import os

logger = logging.getLogger(__name__)

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY")
YOUTUBE_BASE    = "https://www.googleapis.com/youtube/v3"

# Trusted channels to specifically monitor
# These are high-signal, low-noise sources
TRUSTED_CHANNELS = {
    "UNWomen":         "UCGRMcSCCVAerNFKepALXx8A",  # UN Women
    "WHO":             "UCy7-iCzM0FAkDAOqMb1OI-Q",   # World Health Organization
    "UNICEF":          "UCp-X9bQE0cEcmHXtHUMpkGg",   # UNICEF
    "HRW":             "UCfPDHa6LONClDy7mAUq0J8Q",   # Human Rights Watch
    "BBCNews":         "UC16niRr50-MSBwiO3YDb3RA",   # BBC News
    "AlJazeera":       "UCNye-wNBqNL5ZzHSJj3l8Bg",   # Al Jazeera
    "NDTVNews":        "UCZFMm1mMw0F81Z37aaEzTUA",   # NDTV
    "TheHindu":        "UCDNfv_M2kMGbGHGBP3WNEMA",   # The Hindu
    "PlanIntl":        "UCBcRF18a7Qf58cCRy5xuWwQ",   # Plan International
    "ActionAid":       "UCbf5GeEpBHuumxqL9cBt2CQ",   # ActionAid
}

# Search queries for each WEI pillar
PILLAR_QUERIES = {
    "bodily_autonomy":  [
        "child marriage india 2025",
        "FGM female genital mutilation africa",
        "period poverty school girls",
        "abortion rights women 2025",
        "reproductive rights law",
        "बाल विवाह भारत",      # child marriage India Hindi
        "مشكلة زواج الأطفال",  # child marriage Arabic
    ],
    "safety_justice": [
        "domestic violence women india 2025",
        "femicide women killed",
        "violence against women india",
        "honour killing pakistan",
        "acid attack women",
        "घरेलू हिंसा महिला",   # domestic violence Hindi
        "violência doméstica mulher brasil", # Brazil
    ],
    "economic": [
        "women entrepreneur india 2025",
        "self help group women india",
        "kudumbashree success story",
        "jeevika women bihar",
        "gender pay gap 2025",
        "महिला स्वयं सहायता समूह",  # SHG Hindi
    ],
    "education": [
        "girl education india 2025",
        "female literacy india",
        "kanyashree scheme west bengal",
        "educate girls rajasthan",
        "girls school dropout",
        "लड़कियों की शिक्षा भारत",  # girl education Hindi
    ],
    "empowerment": [
        "women parliament india",
        "female politician elected 2025",
        "women leadership africa",
        "gender equality policy 2025",
        "women rights movement",
    ],
    "dignity_welfare": [
        "widow rights india",
        "lakshmi bhandar women bengal",
        "women poverty india",
        "food insecurity women",
        "housing rights women",
    ],
    "digital_social": [
        "online harassment women 2025",
        "cyber violence women india",
        "deepfake women",
        "internet access women developing countries",
    ],
    "health": [
        "maternal mortality india 2025",
        "women health india rural",
        "anaemia women india",
        "reproductive health access",
        "cervical cancer screening india",
    ],
}


def search_youtube(query: str, days_back: int = 7,
                   max_results: int = 10) -> list:
    """
    Search YouTube for videos matching a query.
    Returns list of video dicts.
    """
    if not YOUTUBE_API_KEY:
        return []

    published_after = (
        datetime.now(timezone.utc) - timedelta(days=days_back)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        resp = requests.get(
            f"{YOUTUBE_BASE}/search",
            params={
                "key":            YOUTUBE_API_KEY,
                "q":              query,
                "type":           "video",
                "part":           "snippet",
                "maxResults":     max_results,
                "publishedAfter": published_after,
                "relevanceLanguage": "en",
                "safeSearch":     "moderate",
            },
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])

        results = []
        for item in items:
            snippet = item.get("snippet", {})
            title   = snippet.get("title","")
            desc    = snippet.get("description","")
            channel = snippet.get("channelTitle","")
            vid_id  = item.get("id",{}).get("videoId","")

            text = f"{title}. {desc}"[:MAX_ARTICLE_LENGTH]
            results.append({
                "source":     f"YouTube/{channel}",
                "language":   "en",
                "region":     "global",
                "tier":       "social",
                "title":      title,
                "summary":    desc[:300],
                "text":       text,
                "url":        f"https://youtube.com/watch?v={vid_id}",
                "published":  snippet.get("publishedAt",""),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "platform":   "youtube",
                "channel":    channel,
                "video_id":   vid_id,
            })

        time.sleep(0.5)   # respect rate limits
        return results

    except Exception as e:
        logger.warning(f"YouTube search '{query[:40]}': {e}")
        return []


def fetch_channel_videos(channel_id: str, channel_name: str,
                          days_back: int = 7) -> list:
    """Fetch latest videos from a specific trusted channel."""
    if not YOUTUBE_API_KEY:
        return []

    published_after = (
        datetime.now(timezone.utc) - timedelta(days=days_back)
    ).strftime("%Y-%m-%dT%H:%M:%SZ")

    try:
        resp = requests.get(
            f"{YOUTUBE_BASE}/search",
            params={
                "key":            YOUTUBE_API_KEY,
                "channelId":      channel_id,
                "type":           "video",
                "part":           "snippet",
                "maxResults":     15,
                "publishedAfter": published_after,
                "order":          "date",
            },
            timeout=REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])

        results = []
        for item in items:
            snippet = item.get("snippet", {})
            title   = snippet.get("title","")
            desc    = snippet.get("description","")
            vid_id  = item.get("id",{}).get("videoId","")

            text = f"{title}. {desc}"[:MAX_ARTICLE_LENGTH]
            results.append({
                "source":     f"YouTube/{channel_name}",
                "language":   "en",
                "region":     "global",
                "tier":       "social",
                "title":      title,
                "summary":    desc[:300],
                "text":       text,
                "url":        f"https://youtube.com/watch?v={vid_id}",
                "published":  snippet.get("publishedAt",""),
                "fetched_at": datetime.now(timezone.utc).isoformat(),
                "platform":   "youtube",
                "channel":    channel_name,
                "video_id":   vid_id,
            })

        time.sleep(0.5)
        logger.info(f"  YouTube/{channel_name}: {len(results)} videos")
        return results

    except Exception as e:
        logger.warning(f"YouTube channel {channel_name}: {e}")
        return []


def fetch_all_youtube(days_back: int = 7) -> list:
    """
    Run all YouTube searches and channel monitors.
    Returns flat list of relevant video articles.
    """
    if not YOUTUBE_API_KEY:
        logger.info("  YouTube: skipped (no YOUTUBE_API_KEY in .env)")
        return []

    all_results = []
    seen_ids    = set()

    # Search by pillar query
    logger.info("  YouTube: searching pillar queries...")
    for pillar, queries in PILLAR_QUERIES.items():
        for query in queries[:2]:   # limit to 2 queries per pillar
            results = search_youtube(query, days_back=days_back, max_results=8)
            for r in results:
                if r["video_id"] not in seen_ids:
                    seen_ids.add(r["video_id"])
                    all_results.append(r)

    # Monitor trusted channels
    logger.info("  YouTube: scanning trusted channels...")
    for name, channel_id in TRUSTED_CHANNELS.items():
        results = fetch_channel_videos(channel_id, name, days_back)
        for r in results:
            if r["video_id"] not in seen_ids:
                seen_ids.add(r["video_id"])
                all_results.append(r)

    logger.info(f"  YouTube total: {len(all_results)} videos")
    return all_results
