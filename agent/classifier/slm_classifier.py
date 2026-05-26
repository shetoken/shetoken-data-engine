"""
SHEtoken Agent — SLM Classifier
Uses Phi-3.5 Mini (English) and Qwen2.5:3b (multilingual)
via Ollama to classify articles into WEI signals.
"""
import json, logging, re, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (ENGLISH_MODEL, MULTILINGUAL_MODEL,
                    LANGUAGE_MODEL_MAP, OLLAMA_HOST,
                    MIN_CONFIDENCE, GEOGRAPHY_KEYWORDS, WEI_KEYWORDS)
from classifier.prompts import CLASSIFICATION_PROMPT, MULTILINGUAL_PROMPT

logger = logging.getLogger(__name__)

# Platforms already filtered by curated queries — skip keyword check for these
_CURATED_PLATFORMS = {"gdelt", "arxiv", "pubmed"}

# Flat keyword list built once at import time
_WEI_KEYWORDS_FLAT = [kw.lower()
                       for kws in WEI_KEYWORDS.values()
                       for kw in kws]


def _has_wei_signal(article: dict) -> bool:
    """Return True if the article contains at least one WEI keyword."""
    text = " ".join([
        article.get("title", ""),
        article.get("summary", ""),
    ]).lower()
    return any(kw in text for kw in _WEI_KEYWORDS_FLAT)


try:
    import ollama
    OLLAMA_AVAILABLE = True
except ImportError:
    OLLAMA_AVAILABLE = False
    logger.warning("ollama package not installed — run: pip install ollama")


def get_model(language: str) -> str:
    return LANGUAGE_MODEL_MAP.get(language, ENGLISH_MODEL)


def extract_json(text: str) -> dict:
    """Extract JSON from SLM response, handling markdown fences."""
    text = text.strip()
    # Remove markdown fences
    text = re.sub(r"```json\s*", "", text)
    text = re.sub(r"```\s*", "", text)
    # Find first { ... }
    match = re.search(r"\{.*\}", text, re.DOTALL)
    if match:
        try:
            return json.loads(match.group())
        except json.JSONDecodeError:
            pass
    return {}


def resolve_geography(article: dict, slm_result: dict) -> tuple:
    """
    Resolve country/state codes from article region and SLM hints.
    Returns (country_code, state_code)
    """
    # Try SLM hints first
    country_hint = slm_result.get("country_hint", "")
    state_hint   = slm_result.get("state_hint", "")

    for keyword, (country, state) in GEOGRAPHY_KEYWORDS.items():
        if keyword.lower() in state_hint.lower():
            return country, state
        if keyword.lower() in country_hint.lower():
            return country, state

    # Fall back to article region field
    region = article.get("region", "")
    for keyword, (country, state) in GEOGRAPHY_KEYWORDS.items():
        if keyword.lower() in region.lower():
            return country, state

    return None, None


def classify_article(article: dict) -> dict | None:
    """
    Classify a single article using the appropriate SLM.
    Returns signal dict or None if below confidence threshold.
    """
    if not OLLAMA_AVAILABLE:
        return None

    language = article.get("language", "en")
    model    = get_model(language)
    prompt_template = (MULTILINGUAL_PROMPT if language != "en"
                       else CLASSIFICATION_PROMPT)
    prompt = prompt_template.format(text=article["text"])

    try:
        response = ollama.chat(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            options={
                "temperature": 0.1,   # Low temp for consistent classification
                "num_predict": 256,   # Short response
            }
        )
        raw = response["message"]["content"]
        result = extract_json(raw)

        if not result:
            logger.debug(f"  No JSON from SLM for: {article['title'][:60]}")
            return None

        # Filter by confidence and relevance
        confidence = float(result.get("confidence", 0))
        pillar     = result.get("pillar", "none")
        direction  = int(result.get("direction", 0))

        if confidence < MIN_CONFIDENCE:
            return None
        if pillar == "none" or direction == 0:
            return None

        country_code, state_code = resolve_geography(article, result)

        return {
            "title":       article["title"],
            "url":         article["url"],
            "source":      article["source"],
            "language":    language,
            "published":   article.get("published", ""),
            "pillar":      pillar,
            "direction":   direction,
            "severity":    float(result.get("severity", 0.3)),
            "confidence":  confidence,
            "country":     country_code,
            "state":       state_code,
            "crisis":      bool(result.get("crisis", False)),
            "summary_en":  result.get("summary_en", article["title"]),
            "model_used":  model,
        }

    except Exception as e:
        logger.warning(f"  Classify error ({article['title'][:40]}): {e}")
        return None


def classify_all(articles: list) -> list:
    """Classify all articles. Returns list of valid signals."""
    # ── Keyword pre-filter ────────────────────────────────────────────────────
    # Curated platforms (GDELT, arXiv, PubMed) are pre-filtered by their
    # queries and bypass the keyword check. All other sources must contain at
    # least one WEI keyword in title+summary to reach the SLM.
    to_classify, skipped = [], 0
    for a in articles:
        if a.get("platform", "") in _CURATED_PLATFORMS or _has_wei_signal(a):
            to_classify.append(a)
        else:
            skipped += 1
    logger.info(
        f"Pre-filter: {skipped} articles dropped (no WEI keywords), "
        f"{len(to_classify)}/{len(articles)} sent to SLM"
    )
    # ─────────────────────────────────────────────────────────────────────────

    total = len(to_classify)
    logger.info(f"Classifying {total} articles (parallel, 4 workers)...")
    signals = []
    completed = 0

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(classify_article, art): art for art in to_classify}
        for fut in as_completed(futures):
            completed += 1
            try:
                signal = fut.result()
                if signal:
                    signals.append(signal)
            except Exception as e:
                art = futures[fut]
                logger.warning(f"  Worker error ({art['title'][:40]}): {e}")
            if completed % 20 == 0:
                logger.info(f"  {completed}/{total} classified, {len(signals)} signals so far")

    logger.info(f"Classification complete: {len(signals)} signals from {total} articles")
    return signals
