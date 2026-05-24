"""
SHEtoken — Women's Health Index (WHI)
======================================
A sister index capturing women's health dimensions that mainstream gender
indices systematically ignore — especially mental health and menstrual dignity.

Dimensions (each normalised 0-100, higher = better health outcome):
  1. Female depression/anxiety prevalence   (WHO GHO)        invert
  2. Female suicide rate per 100k           (WHO GHO)        invert
  3. Anaemia in women 15-49 (%)             (WHO)            invert
  4. Menstrual hygiene access (%)           (UNICEF/DHS MICS) positive
  5. Contraceptive unmet need (%)           (UN Pop Division) invert
  6. Maternal mental-health support (0-10)  (modeled)        positive

WHI score: 0-100, HIGHER = BETTER (consistent with WEI direction).

DATA NOTE
---------
Mental-health and menstrual-health datasets have patchy global coverage.
Values here are transparent MODELED ESTIMATES grounded in known regional
patterns and anchor data points (e.g. India anaemia ~57% from NFHS-5).
Each row carries data_source so verified vs modeled is auditable. Replace
with verified WHO/DHS pulls as coverage allows — structure stays identical.

Sources to wire in for verified version:
  WHO Global Health Observatory (depression, suicide, anaemia)
  UNICEF / DHS / MICS (menstrual hygiene management)
  UN Population Division (unmet need for family planning)

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR


# ── WOMEN'S HEALTH DATA ───────────────────────────────────────────────────────
# country, iso, region,
# depression_prev_pct,        female depression/anxiety prevalence %
# suicide_rate_per_100k,      female suicide rate per 100k
# anaemia_pct,                anaemia in women 15-49 %
# menstrual_access_pct,       % women with adequate menstrual hygiene access
# contraceptive_unmet_pct,    % unmet need for family planning
# maternal_mh_support,        0-10 postpartum / maternal mental-health support
# data_source
WHI_DATA = [
    ("Norway",      "NOR", "Europe",       4.5,  4.0, 12, 98,  6, 9, "modeled_estimate"),
    ("Sweden",      "SWE", "Europe",       5.0,  5.5, 13, 98,  6, 9, "modeled_estimate"),
    ("Denmark",     "DNK", "Europe",       4.8,  4.5, 12, 98,  6, 9, "modeled_estimate"),
    ("Iceland",     "ISL", "Europe",       4.2,  3.5, 11, 99,  5, 9, "modeled_estimate"),
    ("Finland",     "FIN", "Europe",       5.2,  6.0, 14, 98,  6, 8, "modeled_estimate"),
    ("Germany",     "DEU", "Europe",       5.5,  5.0, 15, 96,  7, 8, "modeled_estimate"),
    ("Australia",   "AUS", "Oceania",      5.8,  4.8, 14, 96,  7, 8, "modeled_estimate"),
    ("UK",          "GBR", "Europe",       6.0,  4.2, 16, 95,  8, 8, "modeled_estimate"),
    ("Canada",      "CAN", "N. America",   5.6,  5.0, 15, 96,  8, 8, "modeled_estimate"),
    ("USA",         "USA", "N. America",   6.5,  6.5, 13, 94, 10, 7, "modeled_estimate"),
    ("South Korea", "KOR", "East Asia",    6.8, 18.0, 23, 92,  9, 6, "modeled_estimate"),
    ("Turkey",      "TUR", "Europe/Asia",  6.2,  3.0, 32, 80, 14, 5, "modeled_estimate"),
    ("Brazil",      "BRA", "S. America",   7.0,  4.0, 28, 78, 12, 6, "modeled_estimate"),
    ("Philippines", "PHL", "SE Asia",      6.0,  3.5, 26, 70, 17, 5, "modeled_estimate"),
    ("Japan",       "JPN", "East Asia",    5.5, 11.0, 22, 95,  8, 7, "modeled_estimate"),
    ("Colombia",    "COL", "S. America",   6.5,  3.2, 27, 76, 13, 5, "modeled_estimate"),
    ("South Africa","ZAF", "Africa",       7.5,  4.0, 31, 68, 15, 5, "modeled_estimate"),
    ("Mexico",      "MEX", "N. America",   6.8,  3.0, 25, 75, 12, 5, "modeled_estimate"),
    ("Kenya",       "KEN", "Africa",       7.0,  5.0, 27, 55, 18, 4, "modeled_estimate"),
    ("India",       "IND", "South Asia",   7.5, 11.0, 57, 58, 13, 4, "anchor:NFHS-5_anaemia"),
    ("Indonesia",   "IDN", "SE Asia",      6.2,  3.0, 31, 64, 11, 5, "modeled_estimate"),
    ("Egypt",       "EGY", "Africa/ME",    6.5,  2.5, 30, 62, 16, 4, "modeled_estimate"),
    ("Iran",        "IRN", "Middle East",  7.0,  3.5, 28, 70, 14, 4, "modeled_estimate"),
    ("Nigeria",     "NGA", "Africa",       7.2,  4.5, 55, 48, 19, 3, "modeled_estimate"),
    ("Bangladesh",  "BGD", "South Asia",   6.8,  5.5, 40, 52, 12, 4, "modeled_estimate"),
    ("Pakistan",    "PAK", "South Asia",   7.0,  4.0, 42, 45, 17, 3, "modeled_estimate"),
    ("Iraq",        "IRQ", "Middle East",  8.0,  3.0, 28, 58, 20, 3, "modeled_estimate"),
    ("Ethiopia",    "ETH", "Africa",       7.0,  6.0, 24, 42, 22, 3, "modeled_estimate"),
    ("Niger",       "NER", "Africa",       7.5,  5.0, 50, 32, 30, 2, "modeled_estimate"),
    ("Myanmar",     "MMR", "SE Asia",      7.8,  6.5, 35, 50, 16, 3, "modeled_estimate"),
    ("Afghanistan", "AFG", "South Asia",  12.0,  6.0, 45, 28, 28, 1, "modeled_estimate"),
    ("Palestine",   "PSE", "Middle East", 10.0,  4.0, 32, 60, 18, 3, "modeled_estimate"),
    ("Yemen",       "YEM", "Middle East", 11.0,  5.0, 70, 30, 32, 1, "modeled_estimate"),
    ("Sudan",       "SDN", "Africa",       9.0,  5.5, 38, 35, 26, 2, "modeled_estimate"),
    ("Somalia",     "SOM", "Africa",      10.5,  6.0, 44, 25, 30, 1, "modeled_estimate"),
    ("CAR",         "CAF", "Africa",      10.0,  6.5, 46, 28, 28, 1, "modeled_estimate"),
    ("South Sudan", "SSD", "Africa",      10.5,  6.0, 42, 24, 30, 1, "modeled_estimate"),
    ("DRC",         "COD", "Africa",       9.5,  6.0, 41, 30, 25, 2, "modeled_estimate"),
]


def _clamp(v): return max(0, min(100, v))


def compute_whi(row: dict) -> float:
    """Women's Health Index (0-100, higher = better)."""
    # Normalise each indicator to a 0-100 'goodness' sub-score
    depression = _clamp(100 - (row["depression_prev_pct"] / 12.0 * 100))   # 12% ~ worst
    suicide    = _clamp(100 - (row["suicide_rate_per_100k"] / 18.0 * 100)) # 18 ~ worst
    anaemia    = _clamp(100 - (row["anaemia_pct"] / 70.0 * 100))           # 70% ~ worst
    menstrual  = _clamp(row["menstrual_access_pct"])
    contracept = _clamp(100 - (row["contraceptive_unmet_pct"] / 32.0 * 100))
    maternal   = _clamp(row["maternal_mh_support"] * 10)
    return round(
        depression * 0.20 +
        suicide    * 0.15 +
        anaemia    * 0.20 +
        menstrual  * 0.15 +
        contracept * 0.20 +
        maternal   * 0.10, 1
    )


def generate(year=BASELINE_YEAR):
    rows = []
    for stat in WHI_DATA:
        (country, iso, region, dep, suic, anaemia, menstrual,
         unmet, maternal, source) = stat
        row = {
            "country": country, "iso_code": iso, "region": region,
            "depression_prev_pct": dep,
            "suicide_rate_per_100k": suic,
            "anaemia_pct": anaemia,
            "menstrual_access_pct": menstrual,
            "contraceptive_unmet_pct": unmet,
            "maternal_mh_support": maternal,
            "data_source": source,
            "year": year,
        }
        row["whi_score"] = compute_whi(row)
        rows.append(row)

    rows.sort(key=lambda x: x["whi_score"], reverse=True)
    for i, r in enumerate(rows):
        r["rank"] = i + 1

    out = OUTPUT_DIR / f"womens-health-index-{year}.csv"
    hdr = (
        f"# SHEtoken Women's Health Index (WHI) — {year}\n"
        f"# WHI: 0-100, HIGHER = BETTER health outcomes for women\n"
        f"# Captures mental health + menstrual dignity — usually ignored by gender indices\n"
        f"# Anchor data point: India anaemia 57% (NFHS-5)\n"
        f"# Most values are transparent MODELED ESTIMATES (see data_source col)\n"
        f"# Verified sources to wire in: WHO GHO, UNICEF/DHS, UN Population Division\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    fnames = ["rank", "country", "iso_code", "region", "whi_score",
              "depression_prev_pct", "suicide_rate_per_100k", "anaemia_pct",
              "menstrual_access_pct", "contraceptive_unmet_pct",
              "maternal_mh_support", "data_source", "year"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fnames, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    with open(out, "w", newline="", encoding="utf-8") as f:
        f.write(hdr + buf.getvalue())

    print(f"  Women's Health Index — {len(rows)} countries")
    print(f"  {'Rank':<5}{'Country':<16}{'WHI':>6}{'Anaemia%':>10}{'Suicide':>9}")
    print(f"  {'─'*48}")
    for r in rows[:10]:
        print(f"  {r['rank']:<5}{r['country']:<16}{r['whi_score']:>6}"
              f"{r['anaemia_pct']:>9}%{r['suicide_rate_per_100k']:>9}")
    india = next(r for r in rows if r["iso_code"] == "IND")
    print(f"\n  INDIA: WHI {india['whi_score']}/100 | anaemia {india['anaemia_pct']}% "
          f"| unmet need {india['contraceptive_unmet_pct']}%")
    print(f"  Saved: {out}")
    return rows


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=BASELINE_YEAR)
    p.add_argument("--fallback", action="store_true", help="Use modeled estimates (no API calls)")
    generate(p.parse_args().year)
