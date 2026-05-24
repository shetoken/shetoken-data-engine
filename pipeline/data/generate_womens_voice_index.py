"""
SHEtoken — Women's Voice Index (WVI)
=====================================
A sister index capturing women's VOICE — the most neglected dimension of
gender measurement, and the one most aligned with the SHEtoken brand.

Dimensions (each normalised 0-100, higher = stronger voice):
  1. Online gender-based violence rate (%)   (EIU / regional)   invert
  2. Women in media leadership (%)            (GMMP / Reuters)   positive
  3. Women in tech & AI workforce (%)         (ILO / WADI link)  positive
  4. Civil-society freedom for women (0-10)   (V-Dem WCSP)       positive
  5. Women journalists / bylines (%)          (GMMP)             positive
  6. Press / expression freedom for women (0-10) (V-Dem/RSF)     positive

WVI score: 0-100, HIGHER = STRONGER VOICE (consistent with WEI direction).

CREDIBILITY ANCHOR
------------------
Dimension 4 (civil-society freedom for women) maps to V-Dem's Women's Civil
Society Participation index and Georgetown's Women, Peace & Security Index —
citing those frameworks gives this index academic grounding for investors.

DATA NOTE
---------
Online GBV and women-in-media have weak global comparability. Values are
transparent MODELED ESTIMATES (see data_source col), grounded in regional
patterns and V-Dem orderings. Replace with verified pulls as coverage allows.

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR


# ── WOMEN'S VOICE DATA ────────────────────────────────────────────────────────
# country, iso, region,
# online_gbv_pct,        % women experiencing online harassment/abuse
# media_leadership_pct,  % of media leadership roles held by women
# women_tech_pct,        % of tech/AI workforce that is women
# civil_society_score,   0-10 freedom for women's CSOs to organise (V-Dem WCSP)
# journalists_pct,       % of journalists/bylines that are women
# press_freedom_score,   0-10 expression freedom for women
# data_source
WVI_DATA = [
    ("Norway",      "NOR", "Europe",      18, 45, 32, 10, 48, 10, "modeled_estimate"),
    ("Sweden",      "SWE", "Europe",      20, 44, 31, 10, 47, 10, "modeled_estimate"),
    ("Denmark",     "DNK", "Europe",      19, 42, 30, 10, 46,  9, "modeled_estimate"),
    ("Iceland",     "ISL", "Europe",      17, 46, 33, 10, 49, 10, "modeled_estimate"),
    ("Finland",     "FIN", "Europe",      19, 43, 30, 10, 47, 10, "modeled_estimate"),
    ("Germany",     "DEU", "Europe",      24, 38, 27,  9, 42,  9, "modeled_estimate"),
    ("Australia",   "AUS", "Oceania",     26, 40, 28,  9, 44,  9, "modeled_estimate"),
    ("UK",          "GBR", "Europe",      28, 39, 26,  9, 43,  9, "modeled_estimate"),
    ("Canada",      "CAN", "N. America",  25, 41, 28,  9, 45,  9, "modeled_estimate"),
    ("USA",         "USA", "N. America",  33, 40, 26,  8, 41,  8, "modeled_estimate"),
    ("South Korea", "KOR", "East Asia",   38, 26, 20,  7, 30,  7, "modeled_estimate"),
    ("Turkey",      "TUR", "Europe/Asia", 45, 20, 16,  4, 24,  3, "modeled_estimate"),
    ("Brazil",      "BRA", "S. America",  40, 30, 21,  7, 36,  6, "modeled_estimate"),
    ("Philippines", "PHL", "SE Asia",     38, 32, 24,  6, 38,  5, "modeled_estimate"),
    ("Japan",       "JPN", "East Asia",   30, 22, 18,  8, 28,  8, "modeled_estimate"),
    ("Colombia",    "COL", "S. America",  42, 28, 20,  6, 34,  5, "modeled_estimate"),
    ("South Africa","ZAF", "Africa",      44, 34, 22,  7, 37,  6, "modeled_estimate"),
    ("Mexico",      "MEX", "N. America",  43, 30, 20,  6, 35,  5, "modeled_estimate"),
    ("Kenya",       "KEN", "Africa",      48, 26, 16,  5, 30,  5, "modeled_estimate"),
    ("India",       "IND", "South Asia",  58, 22, 25,  5, 26,  5, "modeled_estimate"),
    ("Indonesia",   "IDN", "SE Asia",     46, 24, 18,  5, 28,  4, "modeled_estimate"),
    ("Egypt",       "EGY", "Africa/ME",   60, 16, 14,  3, 20,  2, "modeled_estimate"),
    ("Iran",        "IRN", "Middle East", 62, 14, 13,  2, 18,  2, "modeled_estimate"),
    ("Nigeria",     "NGA", "Africa",      52, 24, 15,  5, 28,  4, "modeled_estimate"),
    ("Bangladesh",  "BGD", "South Asia",  55, 18, 14,  4, 22,  4, "modeled_estimate"),
    ("Pakistan",    "PAK", "South Asia",  60, 14, 12,  3, 18,  3, "modeled_estimate"),
    ("Iraq",        "IRQ", "Middle East", 64, 12, 10,  2, 15,  2, "modeled_estimate"),
    ("Ethiopia",    "ETH", "Africa",      54, 20, 12,  4, 24,  3, "modeled_estimate"),
    ("Niger",       "NER", "Africa",      58, 14,  9,  3, 18,  3, "modeled_estimate"),
    ("Myanmar",     "MMR", "SE Asia",     60, 16, 12,  2, 20,  1, "modeled_estimate"),
    ("Afghanistan", "AFG", "South Asia",  78,  4,  3,  1,  5,  1, "modeled_estimate"),
    ("Palestine",   "PSE", "Middle East", 62, 18, 14,  3, 22,  2, "modeled_estimate"),
    ("Yemen",       "YEM", "Middle East", 75,  6,  4,  1,  8,  1, "modeled_estimate"),
    ("Sudan",       "SDN", "Africa",      66, 12,  8,  2, 16,  2, "modeled_estimate"),
    ("Somalia",     "SOM", "Africa",      72,  8,  5,  1, 10,  1, "modeled_estimate"),
    ("CAR",         "CAF", "Africa",      68, 10,  6,  2, 14,  2, "modeled_estimate"),
    ("South Sudan", "SSD", "Africa",      70,  8,  5,  1, 12,  1, "modeled_estimate"),
    ("DRC",         "COD", "Africa",      66, 12,  8,  2, 16,  2, "modeled_estimate"),
]


def _clamp(v): return max(0, min(100, v))


def compute_wvi(row: dict) -> float:
    """Women's Voice Index (0-100, higher = stronger voice)."""
    online   = _clamp(100 - (row["online_gbv_pct"] / 78.0 * 100))  # 78% ~ worst
    media    = _clamp(row["media_leadership_pct"] / 50.0 * 100)    # 50% = parity
    tech     = _clamp(row["women_tech_pct"] / 33.0 * 100)          # 33% ~ best observed
    civil    = _clamp(row["civil_society_score"] * 10)
    journos  = _clamp(row["journalists_pct"] / 50.0 * 100)
    press    = _clamp(row["press_freedom_score"] * 10)
    return round(
        online  * 0.20 +
        media   * 0.15 +
        tech    * 0.15 +
        civil   * 0.25 +
        journos * 0.10 +
        press   * 0.15, 1
    )


def generate(year=BASELINE_YEAR):
    rows = []
    for stat in WVI_DATA:
        (country, iso, region, online, media, tech,
         civil, journos, press, source) = stat
        row = {
            "country": country, "iso_code": iso, "region": region,
            "online_gbv_pct": online,
            "media_leadership_pct": media,
            "women_tech_pct": tech,
            "civil_society_score": civil,
            "journalists_pct": journos,
            "press_freedom_score": press,
            "data_source": source,
            "year": year,
        }
        row["wvi_score"] = compute_wvi(row)
        rows.append(row)

    rows.sort(key=lambda x: x["wvi_score"], reverse=True)
    for i, r in enumerate(rows):
        r["rank"] = i + 1

    out = OUTPUT_DIR / f"womens-voice-index-{year}.csv"
    hdr = (
        f"# SHEtoken Women's Voice Index (WVI) — {year}\n"
        f"# WVI: 0-100, HIGHER = STRONGER voice for women\n"
        f"# Civil-society dimension maps to V-Dem WCSP + Georgetown WPS Index\n"
        f"# Captures online GBV, media, tech, civil-society freedom\n"
        f"# Most values are transparent MODELED ESTIMATES (see data_source col)\n"
        f"# Verified sources to wire in: V-Dem, GMMP, ILO, RSF\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    fnames = ["rank", "country", "iso_code", "region", "wvi_score",
              "online_gbv_pct", "media_leadership_pct", "women_tech_pct",
              "civil_society_score", "journalists_pct", "press_freedom_score",
              "data_source", "year"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fnames, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    with open(out, "w", newline="", encoding="utf-8") as f:
        f.write(hdr + buf.getvalue())

    print(f"  Women's Voice Index — {len(rows)} countries")
    print(f"  {'Rank':<5}{'Country':<16}{'WVI':>6}{'CivSoc':>8}{'Tech%':>7}")
    print(f"  {'─'*44}")
    for r in rows[:10]:
        print(f"  {r['rank']:<5}{r['country']:<16}{r['wvi_score']:>6}"
              f"{r['civil_society_score']:>7}/10{r['women_tech_pct']:>6}%")
    india = next(r for r in rows if r["iso_code"] == "IND")
    print(f"\n  INDIA: WVI {india['wvi_score']}/100 | civil-society {india['civil_society_score']}/10 "
          f"| women in tech {india['women_tech_pct']}%")
    print(f"  Saved: {out}")
    return rows


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=BASELINE_YEAR)
    p.add_argument("--fallback", action="store_true", help="Use modeled estimates (no API calls)")
    generate(p.parse_args().year)
