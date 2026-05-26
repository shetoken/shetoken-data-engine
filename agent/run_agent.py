"""
SHEtoken WEI Combined Agent v2.0
==================================
Weekly pipeline:
  1. Fetch news from 100+ sources (multilingual)
  2. Classify with Phi-3.5 Mini + Qwen2.5:3b (Ollama)
  3. Aggregate signals by region and pillar
  4. Apply signals to WEI baseline scores (live index update)
  5. Write signals + live scores to Google Sheets
  6. Send Gmail weekly report
  7. Save all outputs locally

Run:
    python run_agent.py              # full run
    python run_agent.py --dry-run    # no email/sheets
    python run_agent.py --days-back 14

(c) 2026 SHE Foundation. MIT License.
"""

import argparse, json, logging, os, sys, time, io
from datetime import datetime, timezone
from pathlib import Path

# Force UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding="utf-8", errors="replace")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(Path(__file__).parent / "agent.log", encoding="utf-8"),
    ]
)
logger = logging.getLogger(__name__)

# Baseline CSV paths (relative to agent folder — adjust if needed)
AGENT_DIR    = Path(__file__).parent
REPO_ROOT    = AGENT_DIR.parent
DATA_DIR     = REPO_ROOT / "data" / "output"

BASELINE_GLOBAL = DATA_DIR / "baseline-2025.csv"
BASELINE_INDIA  = DATA_DIR / "india-states-2025.csv"
BASELINE_USA    = DATA_DIR / "usa-states-2025.csv"
BASELINE_BRAZIL = DATA_DIR / "brazil-states-2025.csv"
BASELINE_NIGERIA= DATA_DIR / "nigeria-states-2025.csv"
BASELINE_MEXICO = DATA_DIR / "mexico-states-2025.csv"

LIVE_OUTPUT_DIR = AGENT_DIR / "output" / "live"
LIVE_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def get_week_str():
    now = datetime.now(timezone.utc)
    return f"{now.year}-W{now.isocalendar()[1]:02d}"


def save_scan_stats(stats: dict) -> None:
    """
    Persist weekly scan statistics to output/signals/scan_stats.json.

    The file is a JSON array of weekly stat dicts, newest first.
    A maximum of 26 weeks (6 months) of history is kept.
    If an entry for the same week already exists it is overwritten.

    Supabase DDL (run once, backend team):
        CREATE TABLE IF NOT EXISTS she_scan_stats (
            week             TEXT PRIMARY KEY,
            scanned_at       TIMESTAMPTZ NOT NULL,
            rss_count        INTEGER DEFAULT 0,
            youtube_count    INTEGER DEFAULT 0,
            reddit_count     INTEGER DEFAULT 0,
            gdelt_count      INTEGER DEFAULT 0,
            research_count   INTEGER DEFAULT 0,
            social_count     INTEGER DEFAULT 0,
            llm_scout_count  INTEGER DEFAULT 0,
            total_fetched    INTEGER DEFAULT 0,
            total_after_dedup INTEGER DEFAULT 0,
            signals_found    INTEGER DEFAULT 0,
            crisis_signals   INTEGER DEFAULT 0
        );
    """
    path = AGENT_DIR / "output" / "signals" / "scan_stats.json"
    path.parent.mkdir(parents=True, exist_ok=True)

    existing: list[dict] = []
    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                existing = json.load(f)
            if not isinstance(existing, list):
                existing = []
        except Exception:
            existing = []

    # Replace existing entry for this week (idempotent)
    existing = [e for e in existing if e.get("week") != stats.get("week")]
    existing.insert(0, stats)      # newest first
    existing = existing[:26]       # keep ≤ 26 weeks

    with open(path, "w", encoding="utf-8") as f:
        json.dump(existing, f, ensure_ascii=False, indent=2)
    logger.info(f"  Scan stats saved → {path.name} ({len(existing)} weeks on record)")

    # Persist to Supabase so stats survive Cloud Run container recycling
    _sb_upsert_scan_stats(stats)


def _sb_upsert_scan_stats(stats: dict) -> None:
    """Upsert weekly scan stats to Supabase she_scan_stats (no-op if env vars absent)."""
    supabase_url = os.getenv("SUPABASE_URL", "")
    supabase_key = (
        os.getenv("SUPABASE_SERVICE_ROLE_KEY")
        or os.getenv("SUPABASE_ANON_KEY")
        or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")
    )
    if not (supabase_url and supabase_key):
        return

    import httpx

    row = {
        "week":               stats.get("week"),
        "scanned_at":         stats.get("scanned_at"),
        "rss_count":          stats.get("rss_count", 0),
        "youtube_count":      stats.get("youtube_count", 0),
        "reddit_count":       stats.get("reddit_count", 0),
        "gdelt_count":        stats.get("gdelt_count", 0),
        "research_count":     stats.get("research_count", 0),
        "social_count":       stats.get("social_count", 0),
        "llm_scout_count":    stats.get("llm_scout_count", 0),
        "total_fetched":      stats.get("total_fetched", 0),
        "total_after_dedup":  stats.get("total_after_dedup", 0),
        "signals_found":      stats.get("signals_found", 0),
        "crisis_signals":     stats.get("crisis_signals", 0),
    }
    headers = {
        "apikey":        supabase_key,
        "Authorization": f"Bearer {supabase_key}",
        "Content-Type":  "application/json",
        "Prefer":        "resolution=merge-duplicates,return=minimal",
    }
    try:
        resp = httpx.post(
            f"{supabase_url}/rest/v1/she_scan_stats",
            json=row,
            headers=headers,
            timeout=15.0,
        )
        if resp.status_code in (200, 201):
            logger.info("  Scan stats upserted → Supabase she_scan_stats")
        else:
            logger.warning(f"  Supabase scan_stats upsert {resp.status_code}: {resp.text[:200]}")
    except Exception as exc:
        logger.warning(f"  Supabase scan_stats upsert failed ({exc})")


def check_ollama():
    """Verify Ollama is running and models are available."""
    try:
        import ollama
        raw    = ollama.list()
        mlist  = raw.get("models", raw) if isinstance(raw, dict) else raw.models
        models = []
        for m in mlist:
            name = (m.get("name", m.get("model","")) if isinstance(m, dict)
                    else getattr(m, "model", getattr(m, "name","")))
            if name:
                models.append(name)
        logger.info(f"Ollama models: {models}")
        for needed in ["phi3.5", "qwen2.5:3b"]:
            if not any(needed in m for m in models):
                logger.warning(f"Pulling missing model: {needed}")
                import subprocess
                subprocess.run(["ollama", "pull", needed], check=True)
        return True
    except Exception as e:
        logger.error(f"Ollama check failed: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description="SHEtoken WEI Combined Agent v2.0")
    parser.add_argument("--week",       default=None)
    parser.add_argument("--dry-run",    action="store_true")
    parser.add_argument("--days-back",  type=int, default=7)
    parser.add_argument("--skip-fetch", action="store_true")
    parser.add_argument("--skip-wei",   action="store_true",
                        help="Skip WEI update step")
    parser.add_argument("--no-dedup",   action="store_true",
                        help="Disable URL deduplication (re-classify all fetched articles)")
    args = parser.parse_args()

    week       = args.week or get_week_str()
    start_time = time.time()

    logger.info("=" * 60)
    logger.info(f"SHEtoken WEI Combined Agent v2.0 -- {week}")
    logger.info("=" * 60)

    # ── STEP 1: Ollama check ─────────────────────────────────────────────────
    logger.info("\n[1/6] Checking Ollama SLM runtime...")
    if not check_ollama():
        logger.error("Cannot proceed without Ollama.")
        sys.exit(1)

    # ── STEP 2: Fetch articles ───────────────────────────────────────────────
    cache_path = AGENT_DIR / f"output/signals/articles_{week}.json"
    cache_path.parent.mkdir(parents=True, exist_ok=True)

    # Scan stats dict — populated during the fetch else-branch (not cache hits)
    _scan_counts: dict = {}

    if args.skip_fetch and cache_path.exists():
        logger.info(f"\n[2/6] Loading cached articles...")
        with open(cache_path, encoding="utf-8") as f:
            articles = json.load(f)
        logger.info(f"  {len(articles)} articles loaded from cache")
    else:
        logger.info(f"\n[2/6] Fetching news ({args.days_back} days back)...")
        from scanner.fetch_rss import fetch_all_sources
        from scanner.fetch_youtube import fetch_all_youtube
        from scanner.fetch_reddit import fetch_all_reddit

        rss_articles = fetch_all_sources(days_back=args.days_back)
        yt_articles  = fetch_all_youtube(days_back=args.days_back)
        rd_articles  = fetch_all_reddit(days_back=args.days_back)

        # GDELT — structured global news, no scraping, no 403s
        from scanner.fetch_gdelt import fetch_all_gdelt
        gdelt_articles = fetch_all_gdelt(days_back=args.days_back)

        # Academic research papers (arXiv + PubMed)
        from scanner.fetch_research import fetch_all_research
        research_articles = fetch_all_research(days_back=args.days_back)

        # Substack newsletters + Medium tag feeds
        from scanner.fetch_social import fetch_all_social
        social_articles = fetch_all_social(days_back=args.days_back)

        articles = (rss_articles + yt_articles + rd_articles
                    + gdelt_articles + research_articles + social_articles)
        logger.info(
            f"  RSS: {len(rss_articles)} | YouTube: {len(yt_articles)} "
            f"| Reddit: {len(rd_articles)} | GDELT: {len(gdelt_articles)} "
            f"| Research: {len(research_articles)} | Social: {len(social_articles)}"
        )

        # ── Record source counts for scan stats ──────────────────────────────
        _scan_counts = {
            "week":            week,
            "scanned_at":      datetime.now(timezone.utc).isoformat(),
            "rss_count":       len(rss_articles),
            "youtube_count":   len(yt_articles),
            "reddit_count":    len(rd_articles),
            "gdelt_count":     len(gdelt_articles),
            "research_count":  len(research_articles),
            "social_count":    len(social_articles),
            "llm_scout_count": 0,   # updated below after LLM Scout
            "total_fetched":   len(articles),
            "total_after_dedup": len(articles),  # updated after dedup
            "signals_found":   0,   # updated after classify
            "crisis_signals":  0,   # updated after aggregate
        }
        # ─────────────────────────────────────────────────────────────────────

        # ── Deduplicate against previously-seen article URLs ─────────────────
        # Drops articles whose URL was already processed in an earlier run so
        # the SLM classifier never wastes time on the same piece twice.
        # Pass --no-dedup to skip (useful when intentionally re-processing).
        if not args.no_dedup:
            from dedup import filter_new, stats as dedup_stats
            articles, n_skipped = filter_new(articles, week)
            if n_skipped:
                ds = dedup_stats()
                logger.info(
                    f"  Dedup: {n_skipped} already-seen articles filtered out "
                    f"→ {len(articles)} new to classify"
                )
                logger.info(
                    f"  Dedup store: {ds['total_urls']} total URLs, "
                    f"{ds['weeks_covered']} weeks on record "
                    f"[{ds.get('backend','?')}]"
                )
            else:
                logger.info(
                    f"  Dedup: all {len(articles)} articles are new this week"
                )
            if _scan_counts:
                _scan_counts["total_after_dedup"] = len(articles)
        # ─────────────────────────────────────────────────────────────────────

        with open(cache_path, "w", encoding="utf-8") as f:
            json.dump(articles, f, ensure_ascii=False, indent=2)
        logger.info(f"  {len(articles)} new articles cached")

    if not articles:
        logger.warning("No articles fetched — check network/sources")

    # ── LLM Scout: fill gaps for countries with no organic signals ───────────
    # Runs AFTER dedup so it only fires for countries genuinely not covered.
    # Requires ANTHROPIC_API_KEY or PERPLEXITY_API_KEY in environment.
    if not args.no_dedup:  # skip in no-dedup (manual re-run) mode
        try:
            from scanner.fetch_llm_scout import fetch_llm_scout
            # Find countries already represented in the organic articles
            covered = {a.get("region", "").lower() for a in articles if a.get("region")}
            scout_arts = fetch_llm_scout(week_str=week)
            # Filter to countries not already covered
            scout_new = [a for a in scout_arts
                         if a.get("scout_country", "").lower() not in covered]
            if scout_new:
                logger.info(f"  LLM Scout added {len(scout_new)} items for uncovered countries")
                articles = articles + scout_new
            if _scan_counts:
                _scan_counts["llm_scout_count"] = len(scout_arts)
        except Exception as exc:
            logger.info(f"  LLM Scout skipped: {exc}")
    # ─────────────────────────────────────────────────────────────────────────

    # ── STEP 3: Classify ─────────────────────────────────────────────────────
    logger.info(f"\n[3/6] Classifying {len(articles)} articles with SLM...")
    from classifier.slm_classifier import classify_all
    signals = classify_all(articles)
    logger.info(f"  {len(signals)} signals from {len(articles)} articles")
    if _scan_counts:
        _scan_counts["signals_found"] = len(signals)

    # ── STEP 4: Aggregate signals ────────────────────────────────────────────
    logger.info(f"\n[4/6] Aggregating signals...")
    from aggregator.aggregate import aggregate_signals
    report = aggregate_signals(signals, week)

    # ── Mark processed URLs as seen (after successful aggregation) ───────────
    # We wait until here — not at fetch time — so a mid-run crash doesn't
    # permanently suppress articles that were never actually classified.
    if not args.no_dedup:
        try:
            from dedup import mark_seen, prune_old
            n_marked = mark_seen(articles, week)
            n_pruned = prune_old(days_keep=90)
            logger.info(
                f"  Dedup: recorded {n_marked} new URLs; "
                f"pruned {n_pruned} entries older than 90 days"
            )
        except Exception as exc:
            logger.warning(f"  Dedup mark_seen failed (non-fatal): {exc}")
    # ─────────────────────────────────────────────────────────────────────────

    # ── Save scan stats (runs after successful classify + aggregate) ──────────
    if _scan_counts:
        _scan_counts["crisis_signals"] = report.get("crisis_count", 0)
        try:
            save_scan_stats(_scan_counts)
        except Exception as exc:
            logger.warning(f"  Scan stats save failed (non-fatal): {exc}")
    # ─────────────────────────────────────────────────────────────────────────

    # ── STEP 5: Update WEI scores ────────────────────────────────────────────
    live_scores = {}

    if args.skip_wei:
        logger.info("\n[5/6] Skipping WEI update (--skip-wei)")
    else:
        logger.info("\n[5/6] Updating WEI scores with signals...")
        from wei_updater import apply_signals_to_wei, apply_signals_to_states

        # Global countries
        if BASELINE_GLOBAL.exists():
            logger.info("  Updating global country scores...")
            live_global = apply_signals_to_wei(
                signals,
                str(BASELINE_GLOBAL),
                str(LIVE_OUTPUT_DIR / f"wei-live-global-{week}.csv"),
                week
            )
            live_scores["global"] = live_global
            moved = sum(1 for r in live_global
                        if float(r.get("wei_score",0)) !=
                           float(r.get("wei_score_baseline",0)))
            logger.info(f"  Global: {moved} countries moved by signals")
        else:
            logger.warning(f"  Baseline not found: {BASELINE_GLOBAL}")

        # India states
        if BASELINE_INDIA.exists():
            logger.info("  Updating India state scores...")
            live_india = apply_signals_to_states(
                signals, str(BASELINE_INDIA), "IND",
                str(LIVE_OUTPUT_DIR / f"wei-live-india-{week}.csv"), week
            )
            live_scores["india"] = live_india

        # USA states
        if BASELINE_USA.exists():
            logger.info("  Updating USA state scores...")
            live_usa = apply_signals_to_states(
                signals, str(BASELINE_USA), "USA",
                str(LIVE_OUTPUT_DIR / f"wei-live-usa-{week}.csv"), week
            )
            live_scores["usa"] = live_usa

        # Brazil, Nigeria, Mexico
        for country, iso, path in [
            ("Brazil",  "BRA", BASELINE_BRAZIL),
            ("Nigeria", "NGA", BASELINE_NIGERIA),
            ("Mexico",  "MEX", BASELINE_MEXICO),
        ]:
            if path.exists():
                logger.info(f"  Updating {country} state scores...")
                live = apply_signals_to_states(
                    signals, str(path), iso,
                    str(LIVE_OUTPUT_DIR / f"wei-live-{iso.lower()}-{week}.csv"),
                    week
                )
                live_scores[country.lower()] = live

        # Print WEI movers
        if "global" in live_scores:
            movers = [(r["country"], float(r.get("wei_score",0)),
                       float(r.get("wei_score_baseline",0)))
                      for r in live_scores["global"]
                      if float(r.get("wei_score",0)) !=
                         float(r.get("wei_score_baseline",0))]
            movers.sort(key=lambda x: abs(x[1]-x[2]), reverse=True)
            if movers:
                logger.info(f"\n  WEI movers this week (top 10):")
                for country, live, base in movers[:10]:
                    delta = live - base
                    arrow = "+" if delta >= 0 else ""
                    logger.info(f"    {country:<22} {base:.1f} -> {live:.1f}  ({arrow}{delta:.2f})")
        # ── STEP 5b: News-sensitive sister indexes (SVI, WVI) ────────────────────
        # Structural sisters (WHI/GPI/WEVI/WADI/FHI) are NOT touched — monthly only.
        logger.info("\n[5b] Updating news-sensitive sister indexes (SVI, WVI)...")
        try:
            from sister_updater import apply_signals_to_sister_indexes
            apply_signals_to_sister_indexes(
                signals,
                data_dir=str(DATA_DIR),
                live_dir=str(LIVE_OUTPUT_DIR),
                week=week,
            )
        except Exception as e:
            logger.warning(f"  Sister index update skipped (non-fatal): {e}")


    # ── STEP 5c: Generate SLM country blurbs ────────────────────────────────
    # Uses Phi-3.5 via Ollama to write a 2-sentence performance summary per country.
    # Only countries that have classified signals get a blurb — others fall back to
    # the template in the frontend. Writes country_blurbs.json + Supabase.
    logger.info("\n[5c] Generating SLM performance blurbs...")
    try:
        from reporter.blurb_generator import generate_blurbs
        blurb_rows = live_scores.get("global", [])
        if blurb_rows:
            blurbs = generate_blurbs(
                country_rows = blurb_rows,
                signals      = signals,
                live_dir     = LIVE_OUTPUT_DIR,
                dry_run      = args.dry_run,
            )
            logger.info(f"  {len(blurbs)} countries received signal-backed blurbs")
        else:
            logger.info("  Skipped — no live global scores available (--skip-wei?)")
    except Exception as e:
        logger.warning(f"  Blurb generation skipped (non-fatal): {e}")

    # ── STEP 6: Report ───────────────────────────────────────────────────────
    # Summary printout
    logger.info("\n" + "-" * 60)
    logger.info(f"WEEK SUMMARY -- {week}")
    logger.info(f"  Articles scanned:  {len(articles)}")
    logger.info(f"  Signals detected:  {len(signals)}")
    logger.info(f"  Crisis alerts:     {report['crisis_count']}")
    logger.info(f"  WEI datasets updated: {len(live_scores)}")
    if report.get("top_movers"):
        logger.info(f"  Top signal region: {report['top_movers'][0]['geo']}")
    for pillar, data in sorted(
        report.get("global_pillar_summary",{}).items(),
        key=lambda x: abs(x[1]["net_signal"]), reverse=True
    )[:5]:
        sig = data["net_signal"]
        arrow = "^" if sig >= 0 else "v"
        logger.info(f"  {pillar:<22} {arrow} {abs(sig):.3f}  ({data['total_signals']} signals)")
    logger.info("-" * 60)

    if args.dry_run:
        logger.info("\n[6/6] Dry run -- skipping email, Sheets and social")
    else:
        logger.info("\n[6/6] Writing to Google Sheets, email and social...")

        from reporter.sheets_writer import (write_signals_to_sheet,
                                             write_live_wei_to_sheet)
        from reporter.email_sender import send_report
        from social.twitter_poster import post_thread
        from social.instagram_poster import post_to_instagram

        # Google Sheets
        sheets_ok = write_signals_to_sheet(report)
        logger.info(f"  Signals tab:    {'OK' if sheets_ok else 'FAIL'}")

        if "global" in live_scores:
            wei_ok = write_live_wei_to_sheet(live_scores["global"], week)
            logger.info(f"  Live WEI tab:   {'OK' if wei_ok else 'FAIL'}")

        # Email
        report["live_scores_summary"] = {
            k: len(v) for k, v in live_scores.items()
        }
        email_ok = send_report(report)
        logger.info(f"  Email:          {'sent' if email_ok else 'FAIL'}")

        # Social media
        tw_ok = post_thread(report)
        ig_ok = post_to_instagram(report)
        logger.info(f"  Twitter:        {'posted' if tw_ok else 'skipped/fail'}")
        logger.info(f"  Instagram:      {'posted' if ig_ok else 'skipped/fail'}")

    elapsed = round(time.time() - start_time, 1)
    logger.info(f"\nAgent completed in {elapsed}s")
    logger.info(f"Outputs: agent/output/signals/ and agent/output/live/")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()
