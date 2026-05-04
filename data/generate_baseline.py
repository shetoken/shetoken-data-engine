"""
SHEtoken Pipeline — WEI Baseline Generator v3.0
================================================
Generates baseline-YYYY.csv using the 8-pillar WEI formula.

New in v3.0:
  - Bodily Autonomy pillar (period poverty, FGM, child marriage,
    reproductive rights, forced marriage)
  - Dignity & Welfare pillar (widow rights, caregiver burden,
    food insecurity, housing security, mental health)
  - Digital & Social pillar (online harassment, internet gap,
    mobile gap)
  - Expanded Safety & Justice (honour violence, legal aid access)
  - Employment quality in Economic pillar
  - Dowry violence in Violence Penalty (India)

Usage:
    python data/generate_baseline.py            # reads from processed/
    python data/generate_baseline.py --fallback # uses estimates

Output:
    data/output/baseline-2025.csv

© 2026 SHE Foundation. Licensed under MIT.
"""

import csv
import io
import os
import sys
import argparse
import pandas as pd
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import (
    PROCESSED_DIR, OUTPUT_DIR,
    TIER_WEIGHTS, BASELINE_YEAR
)


# ── WEI FORMULA v3.0 ─────────────────────────────────────────────────────────

def calculate_wei(emp, edu, eco, hlt, bod, saf, dig_welf, dig_soc, violence):
    """
    Calculate WEI score using the 8-pillar formula.

    WEI = (Empowerment × 0.15) + (Education × 0.12)
        + (Economic × 0.12) + (Health × 0.12)
        + (Bodily Autonomy × 0.15) + (Safety & Justice × 0.14)
        + (Dignity & Welfare × 0.10) + (Digital & Social × 0.10)
        − (Violence Penalty × 0.10)
    """
    score = (
        (emp       * 0.15) +
        (edu       * 0.12) +
        (eco       * 0.12) +
        (hlt       * 0.12) +
        (bod       * 0.15) +
        (saf       * 0.14) +
        (dig_welf  * 0.10) +
        (dig_soc   * 0.10) -
        (violence  * 0.10)
    )
    return round(score, 1)


# ── FALLBACK DATA (8-pillar estimates) ────────────────────────────────────────
#
# Format: (country, iso, region, tier, pop_M,
#          emp, edu, eco, hlt, bodily, safety, dignity, digital, violence)
#
# Scoring notes for new pillars:
#
#   Bodily Autonomy:
#     Nordic = 90+ (strong reproductive rights, near-zero FGM/child marriage)
#     India  = 42  (child marriage 23%, period poverty high, FGM limited)
#     Niger  = 5   (child marriage 76%, FGM 2%, severe reproductive restrictions)
#
#   Dignity & Welfare:
#     Nordic = 88+ (strong widow rights, low food insecurity, caregiver support)
#     India  = 44  (widow property stripping, high female anaemia, unequal care burden)
#     DRC    = 8   (near-zero widow rights, extreme food insecurity)
#
#   Digital & Social:
#     Nordic = 90+ (high internet access, strong cyberstalking laws, lower harassment)
#     India  = 48  (growing internet but gender gap, rising digital harassment)
#     Afghanistan = 5 (internet ban on women, extreme digital exclusion)
#
#   Violence Penalty:
#     Same as before but now includes dowry violence for South Asia

FALLBACK_DATA = [

    # ── TIER 1 — WEI 70+ ─────────────────────────────────────────────────────
    # name,            iso,  region,       tier, pop,  emp, edu, eco, hlt, bod, saf, dgn, dgt, vio
    ("Iceland",        "ISL","Europe",        1,  0.4,  95,  98,  88,  97,  96,  92,  92,  95,  8),
    ("Norway",         "NOR","Europe",        1,  5.4,  93,  97,  86,  98,  95,  91,  91,  94,  8),
    ("Finland",        "FIN","Europe",        1,  5.5,  92,  98,  85,  97,  94,  90,  90,  93,  8),
    ("Sweden",         "SWE","Europe",        1, 10.4,  91,  97,  87,  97,  95,  89,  91,  94, 10),
    ("Denmark",        "DNK","Europe",        1,  5.9,  89,  96,  85,  96,  93,  88,  90,  92,  9),
    ("New Zealand",    "NZL","Oceania",       1,  5.1,  88,  97,  83,  96,  92,  87,  88,  90, 13),
    ("Germany",        "DEU","Europe",        1, 83.2,  84,  95,  81,  95,  90,  85,  87,  89, 12),
    ("Switzerland",    "CHE","Europe",        1,  8.7,  83,  96,  82,  97,  89,  84,  88,  88, 10),
    ("Canada",         "CAN","N. America",    1, 38.2,  85,  97,  80,  96,  91,  84,  87,  90, 14),
    ("Australia",      "AUS","Oceania",       1, 25.9,  82,  96,  79,  96,  90,  83,  86,  88, 16),
    ("Ireland",        "IRL","Europe",        1,  5.1,  82,  97,  80,  97,  88,  84,  87,  88, 11),
    ("Netherlands",    "NLD","Europe",        1, 17.5,  84,  96,  82,  97,  90,  85,  88,  90, 12),
    ("Belgium",        "BEL","Europe",        1, 11.5,  80,  96,  80,  96,  88,  83,  86,  87, 13),
    ("Austria",        "AUT","Europe",        1,  9.0,  79,  95,  79,  96,  87,  82,  85,  86, 12),
    ("France",         "FRA","Europe",        1, 67.4,  78,  95,  78,  95,  86,  81,  84,  86, 15),
    ("United Kingdom", "GBR","Europe",        1, 67.0,  79,  96,  78,  95,  87,  82,  84,  87, 16),
    ("Spain",          "ESP","Europe",        1, 47.4,  76,  96,  76,  95,  85,  81,  83,  85, 14),
    ("Portugal",       "PRT","Europe",        1, 10.3,  74,  95,  74,  94,  84,  80,  82,  83, 13),
    ("United States",  "USA","N. America",    1,331.0,  77,  96,  73,  93,  82,  78,  82,  86, 20),
    ("Japan",          "JPN","Asia",          1,125.7,  68,  97,  71,  98,  80,  78,  82,  85,  7),
    ("South Korea",    "KOR","Asia",          1, 51.7,  65,  97,  68,  97,  78,  76,  80,  82, 11),
    ("Israel",         "ISR","Middle East",   1,  9.3,  72,  96,  74,  95,  78,  76,  78,  82, 15),
    ("Uruguay",        "URY","S. America",    1,  3.5,  72,  95,  68,  93,  78,  74,  76,  78, 26),

    # ── TIER 2 — WEI 45–69 ───────────────────────────────────────────────────
    ("Argentina",      "ARG","S. America",    2, 45.4,  60,  93,  58,  91,  70,  62,  66,  70, 36),
    ("Brazil",         "BRA","S. America",    2,213.0,  55,  90,  54,  88,  64,  54,  58,  62, 44),
    ("Chile",          "CHL","S. America",    2, 19.1,  58,  92,  57,  90,  68,  60,  64,  68, 34),
    ("Colombia",       "COL","S. America",    2, 51.0,  52,  90,  50,  87,  60,  54,  58,  62, 42),
    ("Mexico",         "MEX","N. America",    2,128.9,  51,  88,  48,  85,  58,  50,  56,  60, 46),
    ("South Africa",   "ZAF","Africa",        2, 60.0,  56,  85,  50,  78,  54,  46,  52,  56, 70),
    ("China",          "CHN","Asia",          2,1412., 62,  93,  64,  90,  62,  62,  64,  68, 22),
    ("India",          "IND","Asia",          2,1408., 48,  74,  42,  68,  42,  48,  44,  48, 38),
    ("Indonesia",      "IDN","Asia",          2,273.5,  44,  82,  48,  78,  50,  48,  50,  54, 30),
    ("Philippines",    "PHL","Asia",          2,111.0,  65,  91,  58,  82,  60,  56,  58,  62, 32),
    ("Sri Lanka",      "LKA","Asia",          2, 22.2,  56,  92,  52,  85,  58,  54,  56,  58, 26),
    ("Vietnam",        "VNM","Asia",          2, 97.3,  58,  90,  56,  88,  56,  58,  58,  60, 20),
    ("Thailand",       "THA","Asia",          2, 71.6,  57,  88,  58,  88,  58,  56,  58,  62, 26),
    ("Mongolia",       "MNG","Asia",          2,  3.3,  55,  91,  52,  84,  54,  52,  54,  58, 36),
    ("Botswana",       "BWA","Africa",        2,  2.6,  56,  87,  52,  74,  52,  50,  52,  54, 46),
    ("Namibia",        "NAM","Africa",        2,  2.6,  58,  88,  50,  76,  52,  52,  52,  56, 50),
    ("Tunisia",        "TUN","Africa",        2, 12.0,  46,  85,  48,  82,  50,  50,  52,  56, 28),
    ("Morocco",        "MAR","Africa",        2, 37.1,  40,  76,  42,  80,  44,  46,  46,  48, 26),
    ("Kenya",          "KEN","Africa",        2, 54.0,  48,  80,  44,  68,  44,  44,  44,  46, 40),
    ("Ghana",          "GHA","Africa",        2, 32.4,  45,  82,  42,  70,  42,  44,  44,  46, 36),
    ("Rwanda",         "RWA","Africa",        2, 13.5,  64,  84,  48,  72,  52,  54,  52,  50, 34),
    ("Kazakhstan",     "KAZ","Central Asia",  2, 19.1,  54,  92,  60,  88,  60,  58,  60,  62, 26),
    ("Ukraine",        "UKR","Europe",        2, 43.5,  58,  93,  62,  90,  66,  60,  64,  68, 28),
    ("Turkey",         "TUR","Europe/Asia",   2, 84.3,  48,  82,  52,  86,  52,  50,  54,  58, 34),
    ("Russia",         "RUS","Europe",        2,144.1,  56,  92,  60,  88,  62,  56,  60,  64, 26),
    ("Bolivia",        "BOL","S. America",    2, 11.8,  52,  88,  48,  82,  52,  50,  52,  54, 40),
    ("Honduras",       "HND","C. America",    2, 10.3,  48,  85,  46,  80,  48,  46,  48,  50, 54),
    ("Peru",           "PER","S. America",    2, 32.9,  50,  88,  48,  82,  50,  50,  52,  54, 40),

    # ── TIER 3 — WEI 20–44 ───────────────────────────────────────────────────
    ("Bangladesh",     "BGD","Asia",          3,166.3,  38,  70,  36,  68,  32,  36,  34,  38, 38),
    ("Nepal",          "NPL","Asia",          3, 29.7,  36,  68,  34,  66,  30,  34,  32,  36, 34),
    ("Myanmar",        "MMR","Asia",          3, 54.4,  34,  72,  38,  70,  32,  32,  34,  36, 42),
    ("Cambodia",       "KHM","Asia",          3, 16.7,  32,  74,  38,  72,  34,  34,  34,  36, 32),
    ("Laos",           "LAO","Asia",          3,  7.3,  32,  72,  36,  70,  30,  32,  32,  34, 28),
    ("Papua New Guinea","PNG","Oceania",      3,  9.1,  26,  60,  28,  58,  22,  24,  24,  28, 58),
    ("Pakistan",       "PAK","Asia",          3,225.2,  24,  50,  28,  62,  18,  22,  20,  24, 42),
    ("Nigeria",        "NGA","Africa",        3,213.4,  28,  60,  30,  52,  20,  24,  22,  26, 46),
    ("Ethiopia",       "ETH","Africa",        3,117.9,  26,  55,  28,  52,  18,  24,  20,  24, 36),
    ("Tanzania",       "TZA","Africa",        3, 61.5,  30,  64,  32,  58,  22,  26,  22,  26, 44),
    ("Uganda",         "UGA","Africa",        3, 47.1,  34,  66,  30,  56,  24,  28,  24,  28, 50),
    ("Mozambique",     "MOZ","Africa",        3, 32.2,  28,  58,  28,  52,  20,  24,  20,  24, 44),
    ("Zambia",         "ZMB","Africa",        3, 18.9,  30,  64,  32,  56,  22,  26,  22,  26, 46),
    ("Zimbabwe",       "ZWE","Africa",        3, 15.1,  32,  72,  30,  58,  24,  28,  24,  28, 48),
    ("Cameroon",       "CMR","Africa",        3, 27.2,  28,  60,  28,  52,  18,  24,  20,  24, 42),
    ("Ivory Coast",    "CIV","Africa",        3, 26.4,  26,  58,  28,  50,  16,  22,  20,  22, 38),
    ("Guatemala",      "GTM","C. America",    3, 17.1,  34,  70,  36,  74,  30,  30,  30,  34, 50),
    ("Haiti",          "HTI","Caribbean",     3, 11.4,  24,  56,  26,  46,  20,  22,  20,  22, 46),
    ("Egypt",          "EGY","Middle East",   3,102.3,  24,  70,  32,  74,  22,  28,  28,  32, 30),
    ("Jordan",         "JOR","Middle East",   3, 10.2,  24,  80,  30,  80,  28,  30,  30,  36, 26),
    ("Iraq",           "IRQ","Middle East",   3, 40.2,  18,  58,  22,  70,  18,  22,  20,  22, 34),
    ("Sudan",          "SDN","Africa",        3, 44.9,  16,  42,  20,  48,  12,  18,  16,  18, 34),

    # ── TIER 4 — WEI <20 ─────────────────────────────────────────────────────
    ("Yemen",          "YEM","Middle East",   4, 33.7,  10,  28,  12,  38,   8,  10,   8,  10, 54),
    ("Afghanistan",    "AFG","Asia",          4, 40.1,   6,  18,   8,  32,   4,   8,   6,   5, 46),
    ("DRC",            "COD","Africa",        4, 95.9,  14,  38,  14,  36,  10,  12,   8,  14, 60),
    ("Syria",          "SYR","Middle East",   4, 21.3,  16,  44,  16,  46,  12,  12,  10,  14, 50),
    ("Mali",           "MLI","Africa",        4, 22.4,  14,  36,  16,  38,   8,  10,   8,  12, 38),
    ("Chad",           "TCD","Africa",        4, 16.9,  12,  28,  14,  32,   6,   8,   6,  10, 40),
    ("Niger",          "NER","Africa",        4, 25.1,  10,  24,  12,  30,   5,   8,   6,  10, 34),
    ("Central African Republic","CAF","Africa",4, 4.8, 12,  30,  14,  32,   8,   8,   6,  10, 54),
    ("South Sudan",    "SSD","Africa",        4, 11.2,  14,  28,  14,  30,   8,   8,   6,  10, 52),
    ("Somalia",        "SOM","Africa",        4, 17.1,   8,  20,  10,  28,   4,   6,   4,   8, 56),

    # ── NEW ADDITIONS v3.1 ───────────────────────────────────────────────────

    # ── TIER 1 additions ─────────────────────────────────────────────────────
    # name,              iso,  region,       tier, pop,  emp, edu, eco, hlt, bod, saf, dgn, dgt, vio
    ("Luxembourg",       "LUX","Europe",        1,  0.6,  84,  96,  82,  97,  90,  86,  88,  90, 11),
    ("Lithuania",        "LTU","Europe",        1,  2.8,  78,  96,  76,  94,  86,  82,  84,  86, 12),
    ("Latvia",           "LVA","Europe",        1,  1.8,  76,  96,  74,  94,  84,  80,  82,  84, 14),
    ("Slovenia",         "SVN","Europe",        1,  2.1,  80,  96,  76,  95,  86,  84,  85,  86, 10),
    ("Czech Republic",   "CZE","Europe",        1, 10.9,  76,  96,  74,  95,  84,  80,  82,  84, 12),
    ("Costa Rica",       "CRI","C. America",    1,  5.2,  72,  94,  66,  92,  76,  72,  74,  76, 22),
    ("Barbados",         "BRB","Caribbean",     1,  0.3,  74,  96,  70,  92,  78,  74,  76,  78, 18),

    # ── TIER 2 additions ─────────────────────────────────────────────────────
    ("Saudi Arabia",     "SAU","Middle East",   2, 35.9,  38,  84,  50,  86,  42,  40,  48,  58, 28),
    ("Iran",             "IRN","Middle East",   2, 87.9,  22,  78,  30,  80,  18,  22,  24,  30, 32),
    ("Cuba",             "CUB","Caribbean",     2, 11.3,  70,  94,  56,  88,  68,  64,  66,  64, 20),
    ("Venezuela",        "VEN","S. America",    2, 28.3,  44,  84,  30,  72,  46,  40,  40,  48, 48),
    ("El Salvador",      "SLV","C. America",    2,  6.5,  44,  82,  42,  78,  36,  40,  42,  48, 52),
    ("Senegal",          "SEN","Africa",        2, 17.2,  42,  66,  40,  68,  34,  40,  38,  40, 34),
    ("Timor-Leste",      "TLS","Asia",          2,  1.3,  42,  68,  34,  70,  36,  38,  36,  36, 38),
    ("Malawi",           "MWI","Africa",        2, 20.4,  44,  68,  34,  60,  28,  34,  30,  28, 40),
    ("Liberia",          "LBR","Africa",        2,  5.2,  44,  62,  34,  56,  26,  32,  28,  28, 38),

    # ── TIER 3 additions ─────────────────────────────────────────────────────
    ("Palestine",        "PSE","Middle East",   3,  5.4,  28,  72,  20,  68,  28,  24,  22,  28, 46),
    ("Libya",            "LBY","Middle East",   3,  7.0,  18,  64,  22,  68,  20,  18,  18,  24, 42),
    ("Guinea",           "GIN","Africa",        3, 13.5,  22,  38,  30,  46,   8,  18,  14,  18, 48),
    ("Sierra Leone",     "SLE","Africa",        3,  8.1,  26,  48,  28,  46,  12,  18,  16,  20, 44),
    ("Burkina Faso",     "BFA","Africa",        3, 22.1,  18,  38,  24,  46,  14,  14,  12,  14, 40),
    ("Eritrea",          "ERI","Africa",        3,  3.5,  12,  40,  22,  48,  10,  10,   8,  10, 42),
]


def generate_from_processed(year=BASELINE_YEAR):
    """Generate from processed pipeline data if available."""
    path = PROCESSED_DIR / "pillar_scores_global.csv"
    if not path.exists():
        return None

    df = pd.read_csv(path)
    required = [
        "pillar_empowerment", "pillar_education", "pillar_economic",
        "pillar_health", "pillar_bodily_autonomy", "pillar_safety_justice",
        "pillar_dignity_welfare", "pillar_digital_social",
        "pillar_violence_penalty", "wei_score"
    ]
    if not all(c in df.columns for c in required):
        print("  ⚠ Processed data missing v3.0 pillar columns — using fallback")
        return None

    print(f"  Using processed pipeline data")
    rows = []
    for _, r in df.iterrows():
        rows.append({
            "rank":                  0,
            "country":               r.get("country", r.get("iso_code", "")),
            "iso_code":              r.get("iso_code", ""),
            "region":                r.get("region", ""),
            "tier":                  r.get("tier", ""),
            "population_millions":   r.get("population_millions", ""),
            "empowerment_score":     round(r.get("pillar_empowerment", 0), 1),
            "education_score":       round(r.get("pillar_education", 0), 1),
            "economic_score":        round(r.get("pillar_economic", 0), 1),
            "health_score":          round(r.get("pillar_health", 0), 1),
            "bodily_autonomy_score": round(r.get("pillar_bodily_autonomy", 0), 1),
            "safety_justice_score":  round(r.get("pillar_safety_justice", 0), 1),
            "dignity_welfare_score": round(r.get("pillar_dignity_welfare", 0), 1),
            "digital_social_score":  round(r.get("pillar_digital_social", 0), 1),
            "violence_penalty_score":round(r.get("pillar_violence_penalty", 0), 1),
            "wei_score":             r.get("wei_score", ""),
            "population_weight":     TIER_WEIGHTS.get(r.get("tier", 2), 1.0),
            "ticker":               f"SHE-{r.get('iso_code', '')}",
            "year":                  year,
            "wei_version":           "3.0",
            "data_source":           "pipeline",
            "verified":              r.get("data_quality", "unverified"),
            "notes":                 "",
        })

    rows.sort(key=lambda x: (x["wei_score"] or 0), reverse=True)
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    return rows


def generate_from_fallback(year=BASELINE_YEAR):
    """Generate from hardcoded 8-pillar estimates."""
    print("  Using hardcoded v3.0 fallback estimates")
    rows = []

    for (country, iso, region, tier, pop,
         emp, edu, eco, hlt, bod, saf, dgn, dgt, vio) in FALLBACK_DATA:

        score = calculate_wei(emp, edu, eco, hlt, bod, saf, dgn, dgt, vio)
        rows.append({
            "rank":                  0,
            "country":               country,
            "iso_code":              iso,
            "region":                region,
            "tier":                  tier,
            "population_millions":   pop,
            "empowerment_score":     emp,
            "education_score":       edu,
            "economic_score":        eco,
            "health_score":          hlt,
            "bodily_autonomy_score": bod,
            "safety_justice_score":  saf,
            "dignity_welfare_score": dgn,
            "digital_social_score":  dgt,
            "violence_penalty_score":vio,
            "wei_score":             score,
            "population_weight":     TIER_WEIGHTS[tier],
            "ticker":               f"SHE-{iso}",
            "year":                  year,
            "wei_version":           "3.0",
            "data_source":           "fallback_estimates",
            "verified":              "false",
            "notes":                 "Baseline estimate — run pipeline for verified scores",
        })

    rows.sort(key=lambda x: x["wei_score"], reverse=True)
    for i, r in enumerate(rows):
        r["rank"] = i + 1
    return rows


def write_csv(rows, output_path, year, global_wei):
    """Write final CSV with header comment."""
    fieldnames = [
        "rank", "country", "iso_code", "region", "tier",
        "population_millions",
        "empowerment_score", "education_score", "economic_score",
        "health_score", "bodily_autonomy_score", "safety_justice_score",
        "dignity_welfare_score", "digital_social_score",
        "violence_penalty_score", "wei_score",
        "population_weight", "ticker", "year", "wei_version",
        "data_source", "verified", "notes",
    ]

    header = (
        f"# SHEtoken WEI Baseline Data v3.0 — {year}\n"
        f"# Women's Empowerment Index — 8-pillar formula\n"
        f"# Countries scored: {len(rows)}\n"
        f"# Global WEI {year} (population-weighted): {global_wei}\n"
        f"#\n"
        f"# Formula:\n"
        f"# WEI = (Empowerment x 0.15) + (Education x 0.12)\n"
        f"#     + (Economic x 0.12) + (Health x 0.12)\n"
        f"#     + (Bodily Autonomy x 0.15) + (Safety & Justice x 0.14)\n"
        f"#     + (Dignity & Welfare x 0.10) + (Digital & Social x 0.10)\n"
        f"#     - (Violence Penalty x 0.10)\n"
        f"#\n"
        f"# Full methodology: wei-index/methodology.md\n"
        f"# Data sources: data/sources.md\n"
        f"# Generated: May 2026 | shetoken.org | WEI v{3.0}\n"
        f"#\n"
    )

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        f.write(header + buf.getvalue())


def main(use_fallback=False, year=BASELINE_YEAR):
    print(f"SHEtoken WEI Baseline Generator v3.0 — {year}")
    print("=" * 55)

    rows = None
    if not use_fallback:
        rows = generate_from_processed(year)
    if rows is None:
        rows = generate_from_fallback(year)

    # Global WEI (population-weighted)
    total_w = sum(
        r["wei_score"] * r["population_millions"] * r["population_weight"]
        for r in rows if r["wei_score"]
    )
    total_p = sum(r["population_millions"] * r["population_weight"] for r in rows)
    global_wei = round(total_w / total_p, 1)

    out = OUTPUT_DIR / f"baseline-{year}.csv"
    write_csv(rows, out, year, global_wei)

    # Summary
    print(f"\n  Countries:    {len(rows)}")
    print(f"  Global WEI:   {global_wei}")
    print(f"  Highest:      {rows[0]['country']} ({rows[0]['wei_score']})")
    print(f"  Lowest:       {rows[-1]['country']} ({rows[-1]['wei_score']})")

    # Tier breakdown
    print(f"\n  Tier breakdown:")
    for t in [1, 2, 3, 4]:
        tr = [r for r in rows if r["tier"] == t]
        avg = round(sum(r["wei_score"] for r in tr) / len(tr), 1)
        print(f"    Tier {t}: {len(tr):2d} countries | avg WEI {avg}")

    # New pillars — world averages
    print(f"\n  New pillar world averages:")
    for pillar in ["bodily_autonomy_score", "dignity_welfare_score",
                   "digital_social_score", "safety_justice_score"]:
        vals = [r[pillar] for r in rows if r[pillar]]
        avg  = round(sum(vals) / len(vals), 1)
        print(f"    {pillar.replace('_score',''):<22} {avg}")

    print(f"\n✓ Saved: {out}")
    return str(out)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--fallback", action="store_true")
    parser.add_argument("--year", type=int, default=BASELINE_YEAR)
    args = parser.parse_args()
    main(use_fallback=args.fallback, year=args.year)
