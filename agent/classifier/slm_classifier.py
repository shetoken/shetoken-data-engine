"""
SHEtoken Agent — SLM Classifier
Uses Phi-3.5 Mini (English) and Qwen2.5:3b (multilingual)
via Ollama to classify articles into WEI signals.
"""
import concurrent.futures as _cf
import json, logging, re, sys, time as _time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import (ENGLISH_MODEL, MULTILINGUAL_MODEL,
                    LANGUAGE_MODEL_MAP, OLLAMA_HOST,
                    MIN_CONFIDENCE, GEOGRAPHY_KEYWORDS, WEI_KEYWORDS,
                    ANTHROPIC_API_KEY, ANTHROPIC_FALLBACK_MODEL,
                    CLASSIFY_TIMEOUT_SECS)
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

try:
    import anthropic as _anthropic_sdk
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

# Lazy Anthropic client — created once on first use (thread-safe: harmless if
# two threads race, both produce an equivalent client object)
_anthropic_client: "_anthropic_sdk.Anthropic | None" = None  # type: ignore[name-defined]

def _get_anthropic_client():
    global _anthropic_client
    if _anthropic_client is None and ANTHROPIC_AVAILABLE and ANTHROPIC_API_KEY:
        _anthropic_client = _anthropic_sdk.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _anthropic_client


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


def _classify_article_anthropic(article: dict) -> dict | None:
    """
    Classify one article via Anthropic Claude.
    Mirrors classify_article() but calls the Anthropic API instead of Ollama.
    Used as fallback when Ollama exceeds CLASSIFY_TIMEOUT_SECS.
    """
    client = _get_anthropic_client()
    if client is None:
        return None

    language = article.get("language", "en")
    prompt_template = MULTILINGUAL_PROMPT if language != "en" else CLASSIFICATION_PROMPT
    prompt = prompt_template.format(text=article["text"])

    try:
        msg = client.messages.create(
            model=ANTHROPIC_FALLBACK_MODEL,
            max_tokens=256,
            temperature=0.1,
            messages=[{"role": "user", "content": prompt}],
        )
        raw    = msg.content[0].text
        result = extract_json(raw)

        if not result:
            logger.debug(f"  Anthropic: no JSON for: {article['title'][:60]}")
            return None

        confidence = float(result.get("confidence", 0))
        pillar     = result.get("pillar", "none")
        direction  = int(result.get("direction", 0))

        if confidence < MIN_CONFIDENCE or pillar == "none" or direction == 0:
            return None

        country_code, state_code = resolve_geography(article, result)

        return {
            "title":      article["title"],
            "url":        article["url"],
            "source":     article["source"],
            "language":   language,
            "published":  article.get("published", ""),
            "pillar":     pillar,
            "direction":  direction,
            "severity":   float(result.get("severity", 0.3)),
            "confidence": confidence,
            "country":    country_code,
            "state":      state_code,
            "crisis":     bool(result.get("crisis", False)),
            "summary_en": result.get("summary_en", article["title"]),
            "model_used": f"anthropic/{ANTHROPIC_FALLBACK_MODEL}",
        }

    except Exception as e:
        logger.warning(f"  Anthropic classify error ({article['title'][:40]}): {e}")
        return None


def _classify_batch_anthropic(articles: list) -> list:
    """
    Classify a list of articles via Anthropic API using 8 parallel workers.
    Returns list of valid signals. Called when Ollama times out.
    """
    if not ANTHROPIC_AVAILABLE or not ANTHROPIC_API_KEY:
        logger.warning(
            "  Anthropic fallback unavailable — "
            "install the 'anthropic' package and set ANTHROPIC_API_KEY in .env"
        )
        return []

    total     = len(articles)
    signals   = []
    completed = 0

    logger.info(
        f"  Anthropic fallback: classifying {total} articles "
        f"(model={ANTHROPIC_FALLBACK_MODEL}, 8 workers)..."
    )

    with ThreadPoolExecutor(max_workers=8) as pool:
        futures = {pool.submit(_classify_article_anthropic, art): art for art in articles}
        for fut in as_completed(futures):
            completed += 1
            try:
                signal = fut.result()
                if signal:
                    signals.append(signal)
            except Exception as e:
                art = futures[fut]
                logger.warning(f"  Anthropic worker error ({art['title'][:40]}): {e}")
            if completed % 20 == 0:
                logger.info(
                    f"  Anthropic: {completed}/{total} done, "
                    f"{len(signals)} signals so far"
                )

    logger.info(f"  Anthropic fallback complete: {len(signals)} signals from {total} articles")
    return signals


def classify_all(articles: list, timeout_secs: int | None = None) -> list:
    """
    Classify all articles. Returns list of valid signals.

    Ollama (local SLM) is always tried first with 4 parallel workers.
    If it doesn't finish within *timeout_secs* (default: CLASSIFY_TIMEOUT_SECS,
    600 s = 10 minutes), any remaining articles are sent to Anthropic Claude
    (claude-haiku-4-5-20251001 by default) via the Anthropic API.

    Set ANTHROPIC_API_KEY in .env to enable the fallback.
    Set CLASSIFY_TIMEOUT_SECS in .env to override the 10-minute deadline.
    """
    if timeout_secs is None:
        timeout_secs = CLASSIFY_TIMEOUT_SECS

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

    total           = len(to_classify)
    signals: list   = []
    completed_count = 0
    classified_idxs: set[int] = set()
    timed_out       = False

    logger.info(
        f"Classifying {total} articles "
        f"(Ollama, 4 workers, {timeout_secs}s timeout)..."
    )

    # Use a manual pool so we can shut it down and cancel queued futures on timeout
    pool = ThreadPoolExecutor(max_workers=4)
    future_to_idx = {pool.submit(classify_article, art): i
                     for i, art in enumerate(to_classify)}
    try:
        for fut in as_completed(future_to_idx, timeout=float(timeout_secs)):
            idx = future_to_idx[fut]
            classified_idxs.add(idx)
            completed_count += 1
            try:
                signal = fut.result()
                if signal:
                    signals.append(signal)
            except Exception as e:
                logger.warning(
                    f"  Worker error ({to_classify[idx]['title'][:40]}): {e}"
                )
            if completed_count % 20 == 0:
                logger.info(
                    f"  {completed_count}/{total} classified, "
                    f"{len(signals)} signals so far"
                )

    except _cf.TimeoutError:
        n_remaining = total - len(classified_idxs)
        logger.warning(
            f"  Ollama timeout after {timeout_secs}s — "
            f"{completed_count}/{total} done, "
            f"{n_remaining} articles unclassified. "
            f"Switching to Anthropic API fallback..."
        )
        timed_out = True

    finally:
        # cancel_futures=True drops queued (not yet running) tasks immediately
        pool.shutdown(wait=False, cancel_futures=True)

    # ── Anthropic fallback for articles Ollama didn't reach ───────────────────
    if timed_out:
        remaining = [art for i, art in enumerate(to_classify)
                     if i not in classified_idxs]
        if remaining:
            anthropic_signals = _classify_batch_anthropic(remaining)
            signals.extend(anthropic_signals)
        else:
            logger.info("  No remaining articles for Anthropic fallback")
    # ─────────────────────────────────────────────────────────────────────────

    logger.info(
        f"Classification complete: {len(signals)} signals from {total} articles"
        + (f" (Ollama: {completed_count}, Anthropic: {total - completed_count})"
           if timed_out else "")
    )
    return signals
