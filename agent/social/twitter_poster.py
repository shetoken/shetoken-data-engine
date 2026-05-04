"""
SHEtoken Agent — Twitter/X Weekly Report Poster
=================================================
Auto-posts the weekly WEI signal summary to @ShetokenDAO.

Posts a thread:
  Tweet 1: Weekly summary (signals, crises, top mover)
  Tweet 2: Top pillar signal with most activity
  Tweet 3: India state movers (if any)
  Tweet 4: Crisis alert (if any)
  Tweet 5: CTA to dashboard

Setup:
    1. Create Twitter Developer account at developer.twitter.com
    2. Create a Project + App with Read/Write permissions
    3. Generate Access Token + Secret (for your @ShetokenDAO account)
    4. Add all 4 keys to .env

Cost: Free tier allows 1,500 tweets/month writes. More than enough.

API used: Twitter API v2 via tweepy
"""
import os, logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

TWITTER_API_KEY            = os.getenv("TWITTER_API_KEY")
TWITTER_API_SECRET         = os.getenv("TWITTER_API_SECRET")
TWITTER_ACCESS_TOKEN       = os.getenv("TWITTER_ACCESS_TOKEN")
TWITTER_ACCESS_TOKEN_SECRET= os.getenv("TWITTER_ACCESS_TOKEN_SECRET")


def get_twitter_client():
    try:
        import tweepy
        if not all([TWITTER_API_KEY, TWITTER_API_SECRET,
                    TWITTER_ACCESS_TOKEN, TWITTER_ACCESS_TOKEN_SECRET]):
            logger.info("Twitter: credentials not set in .env — skipping")
            return None
        client = tweepy.Client(
            consumer_key=TWITTER_API_KEY,
            consumer_secret=TWITTER_API_SECRET,
            access_token=TWITTER_ACCESS_TOKEN,
            access_token_secret=TWITTER_ACCESS_TOKEN_SECRET,
        )
        return client
    except ImportError:
        logger.warning("tweepy not installed — run: pip install tweepy")
        return None
    except Exception as e:
        logger.warning(f"Twitter client error: {e}")
        return None


def build_thread(report: dict) -> list[str]:
    """
    Build a 4-5 tweet thread from the weekly report.
    Each tweet must be under 280 characters.
    """
    week      = report.get("week","")
    signals   = report.get("total_signals", 0)
    crises    = report.get("crisis_count", 0)
    movers    = report.get("top_movers", [])
    pillars   = report.get("global_pillar_summary", {})

    tweets = []

    # ── Tweet 1: Weekly summary ───────────────────────────────────────────────
    top_geo = movers[0]["geo"] if movers else "—"
    crisis_str = f" | {crises} crisis alerts" if crises else ""
    t1 = (
        f"$SHE Weekly Signal Report — {week}\n\n"
        f"Scanned 100+ sources this week:\n"
        f"📊 {signals} WEI signals detected{crisis_str}\n"
        f"🌍 Top active region: {top_geo}\n\n"
        f"She goes up. shetoken.org"
    )
    tweets.append(t1[:280])

    # ── Tweet 2: Strongest pillar signal ─────────────────────────────────────
    if pillars:
        top_pillar, pdata = max(
            pillars.items(),
            key=lambda x: abs(x[1]["net_signal"])
        )
        sig     = pdata["net_signal"]
        arrow   = "📈" if sig > 0 else "📉"
        pos     = pdata.get("positive", 0)
        neg     = pdata.get("negative", 0)
        pillar_name = top_pillar.replace("_"," ").title()
        t2 = (
            f"{arrow} Strongest signal this week:\n\n"
            f"Pillar: #{pillar_name}\n"
            f"Net signal: {sig:+.3f}\n"
            f"Positive stories: {pos} | Negative: {neg}\n\n"
            f"#WomenEmpowerment #GenderEquality #SHEtoken"
        )
        tweets.append(t2[:280])

    # ── Tweet 3: India movers (if any India signals) ──────────────────────────
    india_movers = [m for m in movers if m.get("geo","").startswith("IND")]
    if india_movers:
        top_india = india_movers[0]
        t3 = (
            f"🇮🇳 India this week:\n\n"
            f"Most active: {top_india['geo']}\n"
            f"Signals: {top_india['signals']}\n\n"
            f"Programs tracked: Kanyashree, Lakshmi Bhandar, "
            f"JEEViKA, Kudumbashree\n\n"
            f"$SHE-IND $SHE-WB"
        )
        tweets.append(t3[:280])

    # ── Tweet 4: Crisis alert ─────────────────────────────────────────────────
    if crises:
        crisis_list = report.get("crisis_alerts", [])
        if crisis_list:
            c = crisis_list[0]
            country = c.get("country","")
            pillar  = c.get("pillar","").replace("_"," ").title()
            summary = c.get("summary_en","")[:100]
            t4 = (
                f"⚠️ Crisis Alert — {country}\n\n"
                f"Pillar: {pillar}\n"
                f"{summary}\n\n"
                f"DAO governance vote may open.\n"
                f"shetoken.org/signals"
            )
            tweets.append(t4[:280])

    # ── Tweet 5: CTA ──────────────────────────────────────────────────────────
    t5 = (
        f"Track every WEI signal in real time:\n\n"
        f"🌐 shetoken.org — live WEI dashboard\n"
        f"📊 105 countries + 174 states scored\n"
        f"🏙️ 111 world cities\n"
        f"📡 Weekly news signal updates\n\n"
        f"$SHE #SHEtoken #WEI #ImpactInvesting"
    )
    tweets.append(t5[:280])

    return tweets


def post_thread(report: dict) -> bool:
    """Post weekly report as a Twitter thread."""
    client = get_twitter_client()
    if not client:
        return False

    tweets = build_thread(report)
    posted = []

    try:
        for i, tweet_text in enumerate(tweets):
            if i == 0:
                resp = client.create_tweet(text=tweet_text)
            else:
                # Reply to previous tweet
                resp = client.create_tweet(
                    text=tweet_text,
                    in_reply_to_tweet_id=posted[-1]
                )
            posted.append(resp.data["id"])
            logger.info(f"  Twitter: posted tweet {i+1}/{len(tweets)}")
            import time
            time.sleep(2)   # short delay between tweets

        logger.info(f"Twitter thread posted: {len(posted)} tweets")
        return True

    except Exception as e:
        logger.error(f"Twitter post failed: {e}")
        return False
