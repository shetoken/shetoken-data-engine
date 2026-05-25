# Lovable Brief — "100 Girls": The Life Path Experience

> A design + build brief for the emotional centrepiece of shetoken.org.
> Goal: make a visitor *feel* the data, not read it — by walking a cohort of
> 100 girls born in a chosen country through an entire life, one stage at a time.

---

## The core idea

The visitor picks a country. The screen then walks them through the life of
**100 girls born there today** — Born → Childhood → Adolescence → Womanhood →
Working life → Motherhood → Partnership → Old age. At each stage, real numbers
show how many of the 100 make it through, and what they face.

It is the difference between *"India's female secondary enrollment is 74%"* and
*"of 100 girls, 74 reach secondary school — 26 don't."* Same data. Completely
different feeling.

---

## The non-negotiable framing rule

**Always the cohort of 100. Never "you."**

- ✅ "28 of 100 will face violence in their lifetime."
- ❌ "You will face violence." / "You have a 28% chance…"

This single rule is what makes the feature powerful *and* responsible. It
creates empathy (you watch 100 real-scale lives) without making a false
personal prediction or aiming trauma at the individual viewer.

**Show the disclaimer.** The API returns a `disclaimer` field. Display it —
near the top or as a persistent footnote: *"An illustrative cohort of 100 girls,
walked through life using current statistics. Each figure is real and sourced.
A narrative device — not a personal prediction or life-course forecast."*

---

## Data source

Single endpoint:
```
GET https://api.shetoken.org/v1/lifepath/{iso_code}
```
Returns:
```json
{
  "country": "India",
  "cohort_size": 100,
  "disclaimer": "...",
  "stages": [
    {
      "stage": "Womanhood", "age_band": "15+",
      "headline": "Will she be safe?",
      "cohort": "28 of 100 will face sexual or physical violence in their lifetime.",
      "felt": "A woman here is raped every 6 seconds (estimated, incl. unreported)",
      "note": "Marital rape is not a crime here.",
      "source": "WHO prevalence surveys + UNODC"
    }
  ]
}
```
Each stage may have: `cohort` (the X-of-100 line), `felt` (the "every X" live
phrase), `detail` (context), `note` (a flag like marital-rape status), `source`.

---

## The experience (scroll-driven)

A full-screen, vertical scroll story. One stage per "screen," revealed as the
visitor scrolls down — like descending through a life.

**Top / entry:**
- Country selector (search or map). Default to a high-impact country (e.g. India)
  or detect the visitor's own.
- A line: *"Meet 100 girls born in [country] today. Scroll to walk their lives."*
- 100 small dots/figures appear — the cohort.

**Each stage (one viewport):**
- Large age band on the side ("0", "5–17", "15+", "60+") — a life advancing.
- The `headline` as the emotional question ("Will she stay in school?").
- The `cohort` line rendered as an **animated visual**: of the 100 dots, the
  relevant number changes colour / falls away / lights up. E.g. at "Childhood,"
  26 of the 100 dots dim and drop — the girls who don't reach secondary.
- The `felt` phrase shown as a **live ticker** where present: "A girl is married
  before 18 — every 11 seconds" with a counter that actually ticks. Watching a
  number tick up in real time is the gut-punch.
- `source` in small type — always visible. Credibility is the brand.
- `note` (e.g. "Marital rape is not a crime here") as a stark callout when present.

**The dots carry through.** The same 100 figures persist down the scroll, so by
"Old age" the visitor has watched the cohort thin and change across a whole life.
That continuity is the emotional engine.

**End:**
- A summary: "This was 100 girls in [country]." 
- Two CTAs: *"Compare another country"* and *"See how SHEtoken tracks this."*
- A contrast hook: *"In Iceland, the same 100 girls live a very different life →"*
  (loads `/v1/lifepath/ISL`). The contrast between a high-WEI and low-WEI country
  is the most persuasive single moment — build for it.

---

## Visual language

- Use the SHEtoken palette: deep berry-burgundy (#6D2E46) background, warm gold
  (#C9A84C) for the living/surviving figures, muted tone for those who fall away.
- The 100 dots can be simple circles, or subtle figure silhouettes. Keep it
  dignified — never cartoonish, never gratuitous. This is real lives.
- Motion: gentle. Figures fade/settle, they don't explode or shatter. The
  tone is solemn and clear, not horror.
- The live "every X" tickers are the one place for kinetic energy.

---

## Tone & responsibility

- Factual, dignified, sourced. The data is devastating enough; let it speak.
  No melodramatic copy on top of it.
- This is **awareness and advocacy**, presented at a population level. Keep the
  violence stages at the correct age bands (the API already sets "15+", "18+").
- Every screen shows a source. If a number is a modeled estimate elsewhere in
  the system, it's labelled — carry that same honesty here.
- Offer an exit / "skip to data" affordance for visitors who don't want the
  full emotional walk.

---

## Why this is the centrepiece

Every other page on the site answers *"what are the numbers?"* This page answers
*"what do the numbers mean for a life?"* It's the page people will share, the one
that turns a statistic into something felt — which is the entire thesis of
SHEtoken: making women's progress something the world *values*, not just reads.

Build the country contrast (India vs Iceland) first — it's the demo that sells
the whole project in 30 seconds.
