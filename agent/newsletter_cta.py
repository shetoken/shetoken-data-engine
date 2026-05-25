"""
SHEtoken — Newsletter CTA & Summary Generator
==============================================
Uses the local LLM (already loaded by the agent) to write a short "what this
week means" summary + one call-to-action, from the weekly report data.

SAFETY / HONESTY:
  • The model only summarises the numbers it is GIVEN — the prompt forbids
    inventing statistics or naming specific organisations.
  • If the LLM is unavailable or returns junk, a DETERMINISTIC fallback built
    straight from the report data is used. The newsletter can never break or
    block on this.
  • Tone is gentle and advisory — a suggestion, not a directive.
"""

from __future__ import annotations
import json, logging

logger = logging.getLogger(__name__)

CTA_PROMPT = """You are writing a short closing section for a weekly women's-rights
data newsletter. Use ONLY the data below. Do NOT invent any statistics or numbers.
Do NOT name specific organisations or charities. Keep a calm, factual, hopeful tone.

This week's data:
- Global Women's Empowerment Index: {global_wei}
- Biggest movers: {movers}
- Crisis alerts: {crisis_count}
- Most active pillars: {pillars}

Return ONLY valid JSON, no other text:
{{
  "summary": "<2 sentences: what this week's data means, plainly>",
  "action": "<1 sentence: one constructive thing a reader could do this week>"
}}"""


def _fallback(report: dict) -> dict:
    """Deterministic summary + CTA built straight from the data. Never fails."""
    wei = report.get("global_wei", "—")
    movers = report.get("top_movers", [])
    crises = report.get("crisis_alerts", [])
    top = movers[0].get("geo") if movers else None
    summary = f"The global Women's Empowerment Index stands at {wei} this week."
    if top:
        summary += f" The most active region in the news was {top}."
    if crises:
        summary += f" {len(crises)} crisis alert(s) were flagged."
    action = ("Share this report with one person, and consider supporting a "
              "women's-rights organisation working on the issues above.")
    return {"summary": summary, "action": action}


def generate_cta(report: dict) -> dict:
    """
    Return {"summary", "action", "html", "source"} for the newsletter.
    Tries the local LLM; falls back to a deterministic version on any failure.
    """
    fb = _fallback(report)
    result, source = fb, "auto"
    try:
        import ollama
        from config import ENGLISH_MODEL

        movers = ", ".join(m.get("geo", "") for m in report.get("top_movers", [])[:3]) or "none"
        pillars = ", ".join(
            sorted(report.get("global_pillar_summary", {}).keys(),
                   key=lambda k: abs(report["global_pillar_summary"][k].get("net_signal", 0)),
                   reverse=True)[:3]) or "none"
        prompt = CTA_PROMPT.format(
            global_wei=report.get("global_wei", "—"),
            movers=movers,
            crisis_count=report.get("crisis_count", len(report.get("crisis_alerts", []))),
            pillars=pillars,
        )
        resp = ollama.chat(
            model=ENGLISH_MODEL,
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.4, "num_predict": 220},
        )
        raw = resp["message"]["content"]
        raw = raw[raw.find("{"): raw.rfind("}") + 1]   # strip any prose/fences
        parsed = json.loads(raw)
        summary = str(parsed.get("summary", "")).strip()
        action = str(parsed.get("action", "")).strip()
        if summary and action:                          # sane output only
            result, source = {"summary": summary, "action": action}, "llm"
        else:
            logger.warning("CTA: LLM output incomplete — using fallback")
    except Exception as e:
        logger.warning(f"CTA: LLM unavailable ({e}) — using fallback")

    result["source"] = source
    result["html"] = _render_html(result)
    return result


def _render_html(cta: dict) -> str:
    """Branded HTML block to drop into the newsletter templates."""
    return f"""
    <div style="margin-top:28px;padding:20px;border-radius:10px;
                background:#2A1320;border-left:4px solid #C9A84C">
      <h3 style="color:#C9A84C;margin:0 0 8px">What this week means</h3>
      <p style="color:#ECE2D0;margin:0 0 14px;line-height:1.5">{cta['summary']}</p>
      <h3 style="color:#C9A84C;margin:0 0 8px">Take action</h3>
      <p style="color:#ECE2D0;margin:0;line-height:1.5">{cta['action']}</p>
    </div>"""


def cta_text(cta: dict) -> str:
    """Plain-text version for the text/multipart email body."""
    return (f"\n\nWHAT THIS WEEK MEANS\n{cta['summary']}\n\n"
            f"TAKE ACTION\n{cta['action']}\n")
