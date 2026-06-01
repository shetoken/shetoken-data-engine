"""
SHEtoken — Women's Health Index (WHI)
======================================
A sister index capturing women's health dimensions that mainstream gender
indices systematically ignore — especially mental health, menstrual dignity,
and death in childbirth.

Dimensions (each normalised 0-100, higher = better health outcome):
  1. Maternal mortality ratio per 100k live births (WHO GHO)     invert  ← NEW
  2. Female depression/anxiety prevalence   (WHO GHO)            invert
  3. Female suicide rate per 100k           (WHO GHO)            invert
  4. Anaemia in women 15-49 (%)             (WHO)                invert
  5. Menstrual hygiene access (%)           (UNICEF/DHS MICS)    positive
  6. Contraceptive unmet need (%)           (UN Pop Division)    invert
  7. Maternal mental-health support (0-10)  (modeled)            positive

WHI score: 0-100, HIGHER = BETTER (consistent with WEI direction).

Maternal mortality (death due to childbirth) is the single most direct
measure of whether a health system keeps women alive through pregnancy,
so it carries the largest single weight (20%).

DATA NOTE
---------
Maternal mortality ratios are WHO Global Health Observatory 2020 estimates
(maternal deaths per 100,000 live births). Mental-health and menstrual-health
datasets have patchy global coverage, so those values remain transparent
MODELED ESTIMATES grounded in known regional patterns and anchor points
(e.g. India anaemia ~57% from NFHS-5). Each row carries data_source so
verified vs modeled is auditable.

Sources to wire in for verified version:
  WHO Global Health Observatory (maternal mortality, depression, suicide, anaemia)
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
# maternal_mortality_per_100k, maternal deaths per 100k live births (WHO 2020)
# depression_prev_pct,         female depression/anxiety prevalence %
# suicide_rate_per_100k,       female suicide rate per 100k
# anaemia_pct,                 anaemia in women 15-49 %
# menstrual_access_pct,        % women with adequate menstrual hygiene access
# contraceptive_unmet_pct,     % unmet need for family planning
# maternal_mh_support,         0-10 postpartum / maternal mental-health support
# data_source
WHI_DATA = [
    ("Norway",      "NOR", "Europe",         2,  4.5,  4.0, 12, 98,  6, 9, "WHO-MMR-2020;modeled_rest"),
    ("Sweden",      "SWE", "Europe",         5,  5.0,  5.5, 13, 98,  6, 9, "WHO-MMR-2020;modeled_rest"),
    ("Denmark",     "DNK", "Europe",         5,  4.8,  4.5, 12, 98,  6, 9, "WHO-MMR-2020;modeled_rest"),
    ("Iceland",     "ISL", "Europe",         4,  4.2,  3.5, 11, 99,  5, 9, "WHO-MMR-2020;modeled_rest"),
    ("Finland",     "FIN", "Europe",         8,  5.2,  6.0, 14, 98,  6, 8, "WHO-MMR-2020;modeled_rest"),
    ("Germany",     "DEU", "Europe",         4,  5.5,  5.0, 15, 96,  7, 8, "WHO-MMR-2020;modeled_rest"),
    ("Australia",   "AUS", "Oceania",        3,  5.8,  4.8, 14, 96,  7, 8, "WHO-MMR-2020;modeled_rest"),
    ("UK",          "GBR", "Europe",        10,  6.0,  4.2, 16, 95,  8, 8, "WHO-MMR-2020;modeled_rest"),
    ("Canada",      "CAN", "N. America",    11,  5.6,  5.0, 15, 96,  8, 8, "WHO-MMR-2020;modeled_rest"),
    ("USA",         "USA", "N. America",    21,  6.5,  6.5, 13, 94, 10, 7, "WHO-MMR-2020;modeled_rest"),
    ("South Korea", "KOR", "East Asia",      8,  6.8, 18.0, 23, 92,  9, 6, "WHO-MMR-2020;modeled_rest"),
    ("Turkey",      "TUR", "Europe/Asia",   17,  6.2,  3.0, 32, 80, 14, 5, "WHO-MMR-2020;modeled_rest"),
    ("Brazil",      "BRA", "S. America",     72,  7.0,  4.0, 28, 78, 12, 6, "WHO-MMR-2020;modeled_rest"),
    ("Philippines", "PHL", "SE Asia",        78,  6.0,  3.5, 26, 70, 17, 5, "WHO-MMR-2020;modeled_rest"),
    ("Japan",       "JPN", "East Asia",       4,  5.5, 11.0, 22, 95,  8, 7, "WHO-MMR-2020;modeled_rest"),
    ("Colombia",    "COL", "S. America",     75,  6.5,  3.2, 27, 76, 13, 5, "WHO-MMR-2020;modeled_rest"),
    ("South Africa","ZAF", "Africa",        127,  7.5,  4.0, 31, 68, 15, 5, "WHO-MMR-2020;modeled_rest"),
    ("Mexico",      "MEX", "N. America",     59,  6.8,  3.0, 25, 75, 12, 5, "WHO-MMR-2020;modeled_rest"),
    ("Kenya",       "KEN", "Africa",        530,  7.0,  5.0, 27, 55, 18, 4, "WHO-MMR-2020;modeled_rest"),
    ("India",       "IND", "South Asia",    103,  7.5, 11.0, 57, 58, 13, 4, "WHO-MMR-2020;anchor:NFHS-5_anaemia"),
    ("Indonesia",   "IDN", "SE Asia",       173,  6.2,  3.0, 31, 64, 11, 5, "WHO-MMR-2020;modeled_rest"),
    ("Egypt",       "EGY", "Africa/ME",      17,  6.5,  2.5, 30, 62, 16, 4, "WHO-MMR-2020;modeled_rest"),
    ("Iran",        "IRN", "Middle East",    22,  7.0,  3.5, 28, 70, 14, 4, "WHO-MMR-2020;modeled_rest"),
    ("Nigeria",     "NGA", "Africa",       1047,  7.2,  4.5, 55, 48, 19, 3, "WHO-MMR-2020;modeled_rest"),
    ("Bangladesh",  "BGD", "South Asia",    123,  6.8,  5.5, 40, 52, 12, 4, "WHO-MMR-2020;modeled_rest"),
    ("Pakistan",    "PAK", "South Asia",    154,  7.0,  4.0, 42, 45, 17, 3, "WHO-MMR-2020;modeled_rest"),
    ("Iraq",        "IRQ", "Middle East",    76,  8.0,  3.0, 28, 58, 20, 3, "WHO-MMR-2020;modeled_rest"),
    ("Ethiopia",    "ETH", "Africa",        267,  7.0,  6.0, 24, 42, 22, 3, "WHO-MMR-2020;modeled_rest"),
    ("Niger",       "NER", "Africa",        441,  7.5,  5.0, 50, 32, 30, 2, "WHO-MMR-2020;modeled_rest"),
    ("Myanmar",     "MMR", "SE Asia",       179,  7.8,  6.5, 35, 50, 16, 3, "WHO-MMR-2020;modeled_rest"),
    ("Afghanistan", "AFG", "South Asia",    620, 12.0,  6.0, 45, 28, 28, 1, "WHO-MMR-2020;modeled_rest"),
    ("Palestine",   "PSE", "Middle East",    27, 10.0,  4.0, 32, 60, 18, 3, "WHO-MMR-2020;modeled_rest"),
    ("Yemen",       "YEM", "Middle East",   183, 11.0,  5.0, 70, 30, 32, 1, "WHO-MMR-2020;modeled_rest"),
    ("Sudan",       "SDN", "Africa",        270,  9.0,  5.5, 38, 35, 26, 2, "WHO-MMR-2020;modeled_rest"),
    ("Somalia",     "SOM", "Africa",        621, 10.5,  6.0, 44, 25, 30, 1, "WHO-MMR-2020;modeled_rest"),
    ("CAR",         "CAF", "Africa",        835, 10.0,  6.5, 46, 28, 28, 1, "WHO-MMR-2020;modeled_rest"),
    ("South Sudan", "SSD", "Africa",       1223, 10.5,  6.0, 42, 24, 30, 1, "WHO-MMR-2020;modeled_rest"),
    ("DRC",         "COD", "Africa",        547,  9.5,  6.0, 41, 30, 25, 2, "WHO-MMR-2020;modeled_rest"),
]


def _clamp(v): return max(0, min(100, v))


def compute_whi(row: dict) -> float:
    """Women's Health Index (0-100, higher = better)."""
    # Normalise each indicator to a 0-100 'goodness' sub-score
    # MMR ≥ 500 deaths/100k live births → goodness 0 (a maternal-health catastrophe)
    maternal_mort = _clamp(100 - (row["maternal_mortality_per_100k"] / 500.0 * 100))
    depression = _clamp(100 - (row["depression_prev_pct"] / 12.0 * 100))   # 12% ~ worst
    suicide    = _clamp(100 - (row["suicide_rate_per_100k"] / 18.0 * 100)) # 18 ~ worst
    anaemia    = _clamp(100 - (row["anaemia_pct"] / 70.0 * 100))           # 70% ~ worst
    menstrual  = _clamp(row["menstrual_access_pct"])
    contracept = _clamp(100 - (row["contraceptive_unmet_pct"] / 32.0 * 100))
    maternal   = _clamp(row["maternal_mh_support"] * 10)
    return round(
        maternal_mort * 0.20 +   # death in childbirth — highest single weight
        depression    * 0.15 +
        suicide       * 0.10 +
        anaemia       * 0.15 +
        menstrual     * 0.15 +
        contracept    * 0.15 +
        maternal      * 0.10, 1
    )


def generate(year=BASELINE_YEAR):
    rows = []
    for stat in WHI_DATA:
        (country, iso, region, mmr, dep, suic, anaemia, menstrual,
         unmet, maternal, source) = stat
        row = {
            "country": country, "iso_code": iso, "region": region,
            "maternal_mortality_per_100k": mmr,
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
        f"# Captures maternal mortality + mental health + menstrual dignity\n"
        f"# Maternal mortality = WHO GHO 2020 (deaths per 100k live births), weighted 20%\n"
        f"# Anchor data point: India anaemia 57% (NFHS-5)\n"
        f"# Mental-health / menstrual values are transparent MODELED ESTIMATES (see data_source col)\n"
        f"# Verified sources: WHO GHO, UNICEF/DHS, UN Population Division\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    fnames = ["rank", "country", "iso_code", "region", "whi_score",
              "maternal_mortality_per_100k",
              "depression_prev_pct", "suicide_rate_per_100k", "anaemia_pct",
              "menstrual_access_pct", "contraceptive_unmet_pct",
              "maternal_mh_support", "data_source", "year"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fnames, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    with open(out, "w", newline="", encoding="utf-8") as f:
        f.write(hdr + buf.getvalue())

    print(f"  Women's Health Index — {len(rows)} countries")
    print(f"  {'Rank':<5}{'Country':<16}{'WHI':>6}{'MMR':>7}{'Anaemia%':>10}")
    print(f"  {'─'*48}")
    for r in rows[:10]:
        print(f"  {r['rank']:<5}{r['country']:<16}{r['whi_score']:>6}"
              f"{r['maternal_mortality_per_100k']:>7}{r['anaemia_pct']:>9}%")
    india = next(r for r in rows if r["iso_code"] == "IND")
    print(f"\n  INDIA: WHI {india['whi_score']}/100 | maternal mortality "
          f"{india['maternal_mortality_per_100k']}/100k | anaemia {india['anaemia_pct']}%")
    print(f"  Saved: {out}")
    return rows


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=BASELINE_YEAR)
    p.add_argument("--fallback", action="store_true", help="Use modeled estimates (no API calls)")
    generate(p.parse_args().year)
