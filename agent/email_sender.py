"""
SHEtoken WEI — Weekly Newsletter
===================================
Sends a branded weekly newsletter summarising:
  - Week in Review (3-sentence summary)
  - Crisis alerts (if any)
  - Top signal story of the week
  - Country/region movers
  - Pillar trends
  - What it means for $SHE token
  - WEI score updates

Can send to:
  1. Founder (always)
  2. Subscriber list (NEWSLETTER_SUBSCRIBERS in .env)
  3. NGO partners (NEWSLETTER_NGOS in .env)

(c) 2026 SHE Foundation. MIT License.
"""

import smtplib, logging, os, sys
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import GMAIL_USER, GMAIL_APP_PASS, REPORT_TO, REPORT_SUBJECT
from newsletter_cta import generate_cta, cta_text
from newsletter_archive import archive_newsletter

logger = logging.getLogger(__name__)

# Subscriber lists — comma-separated emails in .env
NEWSLETTER_SUBSCRIBERS = os.getenv("NEWSLETTER_SUBSCRIBERS", "")
NEWSLETTER_NGOS        = os.getenv("NEWSLETTER_NGOS", "")

# Brand colours
BERRY = "#6D2E46"
GOLD  = "#C9A84C"
CREAM = "#ECE2D0"
DARK  = "#1A0A12"
WHITE = "#FFFFFF"
GREEN = "#1A6B34"
RED   = "#8B0000"
GREY  = "#F5F5F5"


def build_week_in_review(report: dict) -> str:
    """
    Generate a 3-sentence human-readable summary of the week.
    """
    week       = report.get("week","")
    signals    = report.get("total_signals", 0)
    crises     = report.get("crisis_count", 0)
    movers     = report.get("top_movers", [])
    # LLM-generated summary + call-to-action (with safe fallback)
    cta = generate_cta(report)
    report["cta_html"] = cta["html"]      # builders inject this
    report["cta_text"] = cta_text(cta)    # text version

    pillars    = report.get("global_pillar_summary", {})

    top_geo    = movers[0]["geo"] if movers else "global"
    top_sigs   = movers[0]["signals"] if movers else 0

    # Find strongest pillar signal
    if pillars:
        top_pillar, pd = max(pillars.items(),
                              key=lambda x: abs(x[1].get("net_signal",0)))
        sig = pd.get("net_signal", 0)
        pillar_name = top_pillar.replace("_"," ").title()
        direction = "positive progress" if sig > 0 else "concerning regression"
        pillar_sentence = (
            f"The strongest signal came from <strong>{pillar_name}</strong> — "
            f"showing {direction} with a net score of {sig:+.3f}."
        )
    else:
        pillar_sentence = ""

    if crises > 0:
        crisis_sentence = (
            f"<span style='color:{RED};font-weight:bold;'>"
            f"⚠️ {crises} crisis alert{'s' if crises > 1 else ''} "
            f"triggered this week — see below for details."
            f"</span>"
        )
    else:
        crisis_sentence = (
            f"No crisis thresholds were breached this week."
        )

    summary = (
        f"This week the SHEtoken WEI agent scanned 100+ news sources across "
        f"15 languages and detected <strong>{signals} relevant signals</strong>. "
        f"The most active region was <strong>{top_geo}</strong> "
        f"with {top_sigs} stories tracked. "
        f"{pillar_sentence} {crisis_sentence}"
    )
    return summary


def build_crisis_section(crisis_list: list) -> str:
    if not crisis_list:
        return ""

    items = ""
    for c in crisis_list[:5]:
        country = c.get("country","Unknown")
        pillar  = c.get("pillar","").replace("_"," ").title()
        summary = c.get("summary_en","")[:200]
        url     = c.get("url","")
        source  = c.get("source","")

        items += f"""
        <div style="border-left:4px solid {RED};padding:12px 16px;
                    margin-bottom:12px;background:#FFF5F5;border-radius:0 4px 4px 0;">
          <div style="font-weight:bold;color:{RED};margin-bottom:4px;">
            🚨 {country} — {pillar}
          </div>
          <div style="color:#333;font-size:14px;line-height:1.5;margin-bottom:8px;">
            {summary}
          </div>
          <div style="font-size:12px;color:#888;">
            Source: {source} &nbsp;|&nbsp;
            <a href="{url}" style="color:{BERRY};">Read article →</a>
          </div>
        </div>"""

    return f"""
    <div style="margin:24px 0;">
      <h2 style="color:{RED};font-size:18px;margin:0 0 16px;
                 padding-bottom:8px;border-bottom:2px solid {RED};">
        ⚠️ Crisis Alerts This Week
      </h2>
      {items}
      <div style="background:#FFF3CD;padding:12px;border-radius:4px;
                  font-size:13px;color:#856404;margin-top:12px;">
        Crisis alerts may trigger a DAO governance vote on emergency grants
        or additional token burns. Monitor at shetoken.org/dashboard
      </div>
    </div>"""


def build_top_stories(signals: list) -> str:
    """Show top 5 stories by severity."""
    if not signals:
        return ""

    top = sorted(signals,
                 key=lambda x: x.get("severity",0) * abs(x.get("confidence",0)),
                 reverse=True)[:5]

    items = ""
    for s in top:
        direction = s.get("direction", 0)
        pillar    = s.get("pillar","").replace("_"," ").title()
        country   = s.get("country","") or ""
        state     = s.get("state","")
        geo       = f"{country}-{state}" if state else country
        summary   = s.get("summary_en","")[:180]
        source    = s.get("source","")
        url       = s.get("url","")
        severity  = s.get("severity", 0)

        arrow     = "📈" if direction > 0 else "📉"
        colour    = GREEN if direction > 0 else RED
        label     = "Positive signal" if direction > 0 else "Negative signal"
        bars      = "●" * round(severity * 5) + "○" * (5 - round(severity * 5))

        items += f"""
        <div style="padding:14px 0;border-bottom:1px solid #eee;">
          <div style="display:flex;justify-content:space-between;
                      align-items:flex-start;margin-bottom:6px;">
            <span style="background:{colour}22;color:{colour};
                         font-size:11px;font-weight:bold;padding:2px 8px;
                         border-radius:12px;">{arrow} {label}</span>
            <span style="font-size:11px;color:#aaa;">{bars}</span>
          </div>
          <div style="font-size:13px;color:#888;margin-bottom:4px;">
            <strong style="color:{BERRY};">{pillar}</strong>
            {f" · {geo}" if geo else ""} · {source}
          </div>
          <div style="font-size:14px;color:#333;line-height:1.5;
                      margin-bottom:6px;">{summary}</div>
          <a href="{url}" style="font-size:12px;color:{BERRY};
                                  text-decoration:none;">Read source →</a>
        </div>"""

    return f"""
    <div style="margin:24px 0;">
      <h2 style="color:{BERRY};font-size:18px;margin:0 0 16px;
                 padding-bottom:8px;border-bottom:2px solid {GOLD};">
        📰 Top Stories This Week
      </h2>
      {items}
    </div>"""


def build_region_movers(movers: list) -> str:
    if not movers:
        return ""

    rows = ""
    for i, m in enumerate(movers[:8]):
        geo      = m.get("geo","")
        sigs     = m.get("signals", 0)
        activity = m.get("activity_score", 0)
        medal    = ["🥇","🥈","🥉"][i] if i < 3 else f"{i+1}."

        rows += f"""
          <tr style="background:{'#FAF0F3' if i%2==0 else WHITE};">
            <td style="padding:10px 12px;font-size:14px;">{medal}</td>
            <td style="padding:10px 12px;font-size:14px;font-weight:bold;
                       color:{BERRY};">{geo}</td>
            <td style="padding:10px 12px;font-size:14px;text-align:center;">
              {sigs}</td>
            <td style="padding:10px 12px;font-size:14px;text-align:center;">
              {activity:.2f}</td>
          </tr>"""

    return f"""
    <div style="margin:24px 0;">
      <h2 style="color:{BERRY};font-size:18px;margin:0 0 16px;
                 padding-bottom:8px;border-bottom:2px solid {GOLD};">
        🌍 Most Active Regions This Week
      </h2>
      <table style="width:100%;border-collapse:collapse;font-family:Arial,sans-serif;">
        <thead>
          <tr style="background:{BERRY};">
            <th style="padding:10px 12px;color:white;text-align:left;
                       font-size:12px;">#</th>
            <th style="padding:10px 12px;color:white;text-align:left;
                       font-size:12px;">Region</th>
            <th style="padding:10px 12px;color:white;text-align:center;
                       font-size:12px;">Signals</th>
            <th style="padding:10px 12px;color:white;text-align:center;
                       font-size:12px;">Activity</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
    </div>"""


def build_pillar_table(pillars: dict) -> str:
    if not pillars:
        return ""

    rows = ""
    for pillar, data in sorted(pillars.items(),
                                key=lambda x: abs(x[1].get("net_signal",0)),
                                reverse=True):
        sig   = data.get("net_signal", 0)
        pos   = data.get("positive", 0)
        neg   = data.get("negative", 0)
        total = data.get("total_signals", 0)
        arrow = "▲" if sig > 0 else "▼"
        colour= GREEN if sig > 0 else RED
        name  = pillar.replace("_"," ").title()

        # Mini bar
        bar_w = min(100, abs(sig) * 100)

        rows += f"""
          <tr>
            <td style="padding:10px 12px;font-size:13px;
                       font-weight:bold;">{name}</td>
            <td style="padding:10px 12px;text-align:center;">
              <span style="color:{colour};font-weight:bold;">
                {arrow} {abs(sig):.3f}
              </span>
            </td>
            <td style="padding:10px 12px;text-align:center;
                       font-size:13px;">{total}</td>
            <td style="padding:10px 12px;text-align:center;
                       font-size:12px;color:{GREEN};">+{pos}</td>
            <td style="padding:10px 12px;text-align:center;
                       font-size:12px;color:{RED};">-{neg}</td>
          </tr>"""

    return f"""
    <div style="margin:24px 0;">
      <h2 style="color:{BERRY};font-size:18px;margin:0 0 16px;
                 padding-bottom:8px;border-bottom:2px solid {GOLD};">
        📊 WEI Pillar Signal Summary
      </h2>
      <table style="width:100%;border-collapse:collapse;
                    font-family:Arial,sans-serif;">
        <thead>
          <tr style="background:{BERRY};">
            <th style="padding:10px 12px;color:white;text-align:left;
                       font-size:12px;">Pillar</th>
            <th style="padding:10px 12px;color:white;text-align:center;
                       font-size:12px;">Net Signal</th>
            <th style="padding:10px 12px;color:white;text-align:center;
                       font-size:12px;">Stories</th>
            <th style="padding:10px 12px;color:white;text-align:center;
                       font-size:12px;">Positive</th>
            <th style="padding:10px 12px;color:white;text-align:center;
                       font-size:12px;">Negative</th>
          </tr>
        </thead>
        <tbody>{rows}</tbody>
      </table>
      <p style="font-size:11px;color:#aaa;margin-top:8px;">
        Net signal: weighted average of direction × severity × confidence.
        Range −1.0 to +1.0.
      </p>
    </div>"""


def build_sister_movers(report: dict) -> str:
    """
    SVI + WVI weekly movements, read from the agent's live files written this
    run (svi-live-{week}.csv / wvi-live-{week}.csv). Self-contained: if the
    sister update was skipped or no country moved, the section is omitted.
    """
    import csv as _csv
    week = report.get("week", "")
    if not week:
        return ""
    live_dir = Path(__file__).parent.parent / "output" / "live"

    blocks = ""
    for idx, score_col, label in [
        ("svi", "svi_score", "🛡️ Sexual Violence Index — weekly shift"),
        ("wvi", "wvi_score", "📣 Women's Voice Index — weekly shift"),
    ]:
        path = live_dir / f"{idx}-live-{week}.csv"
        if not path.exists():
            continue
        try:
            with open(path, newline="", encoding="utf-8") as f:
                lines = [l for l in f if not l.lstrip().startswith("#")]
            rows = list(_csv.DictReader(lines))
        except Exception:
            continue

        movers = []
        for r in rows:
            try:
                live = float(r.get(score_col) or 0)
                base = float(r.get(score_col + "_baseline") or 0)
            except (ValueError, TypeError):
                continue
            if round(live, 2) != round(base, 2):
                movers.append((r.get("country", ""), base, live, live - base))
        if not movers:
            continue
        movers.sort(key=lambda x: abs(x[3]), reverse=True)

        rows_html = ""
        for country, base, live, delta in movers[:5]:
            colour = GREEN if delta > 0 else RED
            arrow  = "▲" if delta > 0 else "▼"
            rows_html += f"""
              <tr>
                <td style="padding:8px 12px;font-size:14px;font-weight:bold;
                           color:{BERRY};">{country}</td>
                <td style="padding:8px 12px;font-size:13px;text-align:center;
                           color:#888;">{base:.1f} → {live:.1f}</td>
                <td style="padding:8px 12px;font-size:13px;text-align:center;
                           color:{colour};font-weight:bold;">{arrow} {delta:+.2f}</td>
              </tr>"""

        blocks += f"""
        <div style="margin-bottom:16px;">
          <div style="font-size:13px;font-weight:bold;color:{BERRY};
                      margin-bottom:6px;">{label}</div>
          <table style="width:100%;border-collapse:collapse;">
            <tbody>{rows_html}</tbody>
          </table>
        </div>"""

    if not blocks:
        return ""

    return f"""
    <div style="margin:24px 0;">
      <h2 style="color:{BERRY};font-size:18px;margin:0 0 16px;
                 padding-bottom:8px;border-bottom:2px solid {GOLD};">
        🔀 Sister Index Movers
      </h2>
      {blocks}
      <p style="font-size:11px;color:#aaa;margin-top:4px;">
        SVI and WVI move weekly from news signals (capped ±2.0 pts).
        Higher = better for both. Structural indexes update monthly.
      </p>
    </div>"""


def build_token_section(report: dict) -> str:
    pillars = report.get("global_pillar_summary", {})
    signals = report.get("total_signals", 0)
    crises  = report.get("crisis_count", 0)

    # Estimate overall direction
    if pillars:
        net = sum(d.get("net_signal",0) for d in pillars.values())
        if net > 0.5:
            token_outlook = (
                f"<span style='color:{GREEN};font-weight:bold;'>Bullish</span> — "
                f"overall signals lean positive this week. "
                f"If these signals reflect in annual WEI data, "
                f"it supports token minting."
            )
        elif net < -0.5:
            token_outlook = (
                f"<span style='color:{RED};font-weight:bold;'>Cautious</span> — "
                f"overall signals lean negative this week. "
                f"Sustained regression would trigger token burns."
            )
        else:
            token_outlook = (
                f"<span style='color:#856404;font-weight:bold;'>Neutral</span> — "
                f"mixed signals this week. Monitoring continues."
            )
    else:
        token_outlook = "Insufficient signal data this week."

    crisis_note = ""
    if crises:
        crisis_note = f"""
        <div style="background:#FFF3CD;border-radius:4px;padding:12px;
                    margin-top:12px;font-size:13px;color:#856404;">
          <strong>Crisis alert active:</strong> {crises} threshold
          breach{'es' if crises > 1 else ''} detected.
          A DAO governance vote may open. Token holders can vote at
          <a href="https://shetoken.org/dao" style="color:{BERRY};">
          shetoken.org/dao</a>
        </div>"""

    return f"""
    <div style="margin:24px 0;background:{DARK};border-radius:8px;
                padding:20px;">
      <h2 style="color:{GOLD};font-size:18px;margin:0 0 12px;">
        💰 $SHE Token Signal
      </h2>
      <p style="color:{CREAM};font-size:14px;line-height:1.6;margin:0 0 8px;">
        Weekly outlook: {token_outlook}
      </p>
      <p style="color:#888;font-size:12px;margin:0;">
        Weekly signals carry 10% weight in the WEI update cycle.
        Annual official data (WHO, UNODC, UNESCO) carries 90%.
        This newsletter reflects leading indicators only.
      </p>
      {crisis_note}
    </div>"""


def build_newsletter(report: dict, recipient_type: str = "founder") -> str:
    """
    Build full HTML newsletter.
    recipient_type: 'founder' | 'subscriber' | 'ngo'
    """
    week       = report.get("week","")
    signals    = report.get("total_signals", 0)
    crises     = report.get("crisis_count", 0)
    crisis_list= report.get("crisis_alerts", [])
    movers     = report.get("top_movers", [])
    pillars    = report.get("global_pillar_summary", {})
    raw_signals= report.get("raw_signals", [])

    now = datetime.now(timezone.utc).strftime("%B %d, %Y")

    # Week in review
    wir = build_week_in_review(report)

    # Sections
    crisis_html  = build_crisis_section(crisis_list)
    stories_html = build_top_stories(raw_signals)
    movers_html  = build_region_movers(movers)
    pillar_html  = build_pillar_table(pillars)
    sister_html  = build_sister_movers(report)
    token_html   = build_token_section(report)

    # Founder gets full technical data; subscribers get cleaner version
    extra_section = ""
    if recipient_type == "founder":
        extra_section = f"""
        <div style="background:{GREY};border-radius:6px;padding:16px;
                    margin:24px 0;font-size:12px;color:#666;">
          <strong>Internal data:</strong>
          Articles scanned: {report.get('total_articles_processed', signals)} &nbsp;|&nbsp;
          Signals classified: {signals} &nbsp;|&nbsp;
          Crisis alerts: {crises} &nbsp;|&nbsp;
          Datasets updated: {len(report.get('live_scores_summary',{}))}
          <br><br>
          <a href="https://api.shetoken.org/v1/admin/stats"
             style="color:{BERRY};">API stats</a> &nbsp;|&nbsp;
          <a href="https://api.shetoken.org/v1/signals/latest"
             style="color:{BERRY};">Raw signals JSON</a>
        </div>"""

    unsubscribe = ""
    if recipient_type in ("subscriber","ngo"):
        unsubscribe = f"""
        <p style="text-align:center;font-size:11px;color:#aaa;margin-top:8px;">
          You're receiving this because you subscribed to SHEtoken signals.
          <a href="mailto:contact@shetoken.org?subject=Unsubscribe"
             style="color:#aaa;">Unsubscribe</a>
        </p>"""

    html = f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width,initial-scale=1">
  <title>SHEtoken WEI Weekly — {week}</title>
</head>
<body style="margin:0;padding:0;background:#f4eef1;
             font-family:Arial,Helvetica,sans-serif;">

<div style="max-width:640px;margin:24px auto;background:white;
            border-radius:10px;overflow:hidden;
            box-shadow:0 2px 12px rgba(0,0,0,0.1);">

  <!-- HEADER -->
  <div style="background:{BERRY};padding:28px 32px;text-align:center;">
    <div style="font-size:32px;font-weight:900;letter-spacing:-1px;
                margin-bottom:4px;">
      <span style="color:{GOLD};">$</span><span style="color:white;">HE</span>
    </div>
    <div style="color:{GOLD};font-size:11px;letter-spacing:3px;
                text-transform:uppercase;margin-bottom:12px;">
      Women's Empowerment Index
    </div>
    <div style="color:{CREAM};font-size:14px;">
      Weekly Signal Report &nbsp;·&nbsp; {week} &nbsp;·&nbsp; {now}
    </div>
    <div style="margin-top:16px;display:inline-block;
                background:{GOLD};color:{DARK};font-size:11px;
                font-weight:bold;padding:6px 16px;border-radius:20px;
                letter-spacing:1px;">
      SHE GOES UP
    </div>
  </div>

  <!-- STAT BAR -->
  <div style="background:{DARK};padding:16px 32px;
              display:flex;gap:0;">
    <div style="flex:1;text-align:center;padding:0 16px;
                border-right:1px solid #333;">
      <div style="font-size:28px;font-weight:bold;color:{GOLD};">
        {signals}
      </div>
      <div style="font-size:11px;color:#888;text-transform:uppercase;
                  letter-spacing:1px;">Signals</div>
    </div>
    <div style="flex:1;text-align:center;padding:0 16px;
                border-right:1px solid #333;">
      <div style="font-size:28px;font-weight:bold;
                  color:{'#E07B00' if crises > 0 else GOLD};">
        {crises}
      </div>
      <div style="font-size:11px;color:#888;text-transform:uppercase;
                  letter-spacing:1px;">Crisis Alerts</div>
    </div>
    <div style="flex:1;text-align:center;padding:0 16px;
                border-right:1px solid #333;">
      <div style="font-size:28px;font-weight:bold;color:{GOLD};">
        {len(movers)}
      </div>
      <div style="font-size:11px;color:#888;text-transform:uppercase;
                  letter-spacing:1px;">Active Regions</div>
    </div>
    <div style="flex:1;text-align:center;padding:0 16px;">
      <div style="font-size:28px;font-weight:bold;color:{GOLD};">
        {len(pillars)}
      </div>
      <div style="font-size:11px;color:#888;text-transform:uppercase;
                  letter-spacing:1px;">Pillars Moved</div>
    </div>
  </div>

  <!-- BODY -->
  <div style="padding:28px 32px;">

    <!-- Week in Review -->
    <div style="background:{GREY};border-left:4px solid {GOLD};
                padding:16px 20px;border-radius:0 6px 6px 0;margin-bottom:24px;">
      <div style="font-size:11px;font-weight:bold;color:{GOLD};
                  text-transform:uppercase;letter-spacing:2px;margin-bottom:8px;">
        Week in Review
      </div>
      <div style="font-size:14px;color:#333;line-height:1.7;">
        {wir}
      </div>
    </div>

    {crisis_html}
    {stories_html}
    {movers_html}
    {pillar_html}
    {sister_html}
    {token_html}
    {report.get("cta_html", "")}
    {extra_section}

  </div>

  <!-- FOOTER -->
  <div style="background:{BERRY};padding:20px 32px;text-align:center;">
    <div style="margin-bottom:12px;">
      <a href="https://shetoken.org"
         style="color:{GOLD};text-decoration:none;font-size:12px;
                margin:0 12px;">shetoken.org</a>
      <a href="https://api.shetoken.org/docs"
         style="color:{GOLD};text-decoration:none;font-size:12px;
                margin:0 12px;">API Docs</a>
      <a href="https://github.com/shetoken"
         style="color:{GOLD};text-decoration:none;font-size:12px;
                margin:0 12px;">GitHub</a>
      <a href="https://twitter.com/ShetokenDAO"
         style="color:{GOLD};text-decoration:none;font-size:12px;
                margin:0 12px;">@ShetokenDAO</a>
    </div>
    <div style="color:{CREAM};font-size:11px;opacity:0.7;">
      © 2026 SHE Foundation · contact@shetoken.org
    </div>
    {unsubscribe}
  </div>

</div>
</body>
</html>"""

    return html


def get_all_recipients() -> list:
    """
    Build list of all recipients with their type.
    Subscribers come from Supabase (she_subscribers) first; if that's empty or
    unavailable, falls back to the NEWSLETTER_SUBSCRIBERS / NEWSLETTER_NGOS env
    vars (legacy behaviour). Founder always included.
    """
    recipients = []
    seen = set()

    # Always send to founder
    if REPORT_TO:
        recipients.append({"email": REPORT_TO, "type": "founder"})
        seen.add(REPORT_TO.lower())

    # Subscribers from Supabase (written by the website via POST /v1/subscribe)
    supa_subs = []
    try:
        from subscriber_source import get_subscribers
        supa_subs = get_subscribers()
    except Exception as e:
        logger.warning(f"subscriber load failed ({e}) — using env fallback")

    if supa_subs:
        for s in supa_subs:
            email = (s.get("email") or "").strip()
            if email and email.lower() not in seen:
                recipients.append({"email": email,
                                   "type": s.get("tier", "subscriber")})
                seen.add(email.lower())
        logger.info(f"Recipients from Supabase: {len(supa_subs)}")
    else:
        # ── Fallback: env-var lists (legacy) ─────────────────────────────────
        if NEWSLETTER_SUBSCRIBERS:
            for email in NEWSLETTER_SUBSCRIBERS.split(","):
                email = email.strip()
                if email and email.lower() not in seen:
                    recipients.append({"email": email, "type": "subscriber"})
                    seen.add(email.lower())
        if NEWSLETTER_NGOS:
            for email in NEWSLETTER_NGOS.split(","):
                email = email.strip()
                if email and email.lower() not in seen:
                    recipients.append({"email": email, "type": "ngo"})
                    seen.add(email.lower())

    return recipients


def send_report(report: dict) -> bool:
    """Send newsletter to all recipients."""
    if not GMAIL_USER or not GMAIL_APP_PASS:
        logger.error("Gmail credentials not set in .env")
        return False

    recipients = get_all_recipients()
    if not recipients:
        logger.warning("No recipients configured")
        return False

    week   = report.get("week","")
    crises = report.get("crisis_count", 0)

    subject = f"$SHE Weekly Signal Report — {week}"
    if crises > 0:
        subject = f"⚠️ $SHE Weekly Report — {crises} Crisis Alert{'s' if crises>1 else ''} — {week}"

    ok_count = 0
    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(GMAIL_USER, GMAIL_APP_PASS)

            for r in recipients:
                try:
                    html = build_newsletter(report, recipient_type=r["type"])
                    msg  = MIMEMultipart("alternative")
                    msg["Subject"] = subject
                    msg["From"]    = f"SHEtoken WEI <{GMAIL_USER}>"
                    msg["To"]      = r["email"]
                    msg.attach(MIMEText(html, "html"))
                    server.sendmail(GMAIL_USER, r["email"], msg.as_string())
                    logger.info(f"  Email sent → {r['email']} ({r['type']})")
                    ok_count += 1
                    # Archive this edition to Supabase (best-effort, non-fatal)
                    try:
                        archive_newsletter(week, r["type"], subject, html, "")
                    except Exception as ae:
                        logger.warning(f"  Archive skipped for {r['email']}: {ae}")
                except Exception as e:
                    logger.error(f"  Email failed → {r['email']}: {e}")

    except Exception as e:
        logger.error(f"SMTP connection failed: {e}")
        return False

    logger.info(f"Newsletter sent to {ok_count}/{len(recipients)} recipients")
    return ok_count > 0
