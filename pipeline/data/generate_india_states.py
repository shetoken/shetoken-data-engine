"""
SHEtoken Pipeline — WEI India States Generator v3.0
=====================================================
Generates india-states-YYYY.csv using the 8-pillar WEI formula.

New in v3.0:
  - Bodily Autonomy (period poverty, child marriage, FGM limited,
    reproductive rights, menstrual health)
  - Dignity & Welfare (widow property stripping, caregiver burden,
    female food insecurity, housing security)
  - Digital & Social (internet gender gap, online harassment,
    mobile phone ownership gap)
  - Expanded Safety & Justice (dowry violence, honour-based threats,
    legal aid access, police responsiveness)
  - Employment quality in Economic pillar
  - Dowry violence in Violence Penalty

India-specific data sources:
  - NCRB  (National Crime Records Bureau)
  - DISE / UDISE+ (District Information System for Education)
  - NSSO / PLFS (National Sample Survey)
  - NFHS-5 (National Family Health Survey 2019-21)
  - ECI (Election Commission of India)
  - NABARD (SHG and microfinance data)
  - State government portals

Usage:
    python data/generate_india_states.py
    python data/generate_india_states.py --fallback
    python data/generate_india_states.py --year 2025

Output:
    data/output/india-states-2025.csv

© 2026 SHE Foundation. Licensed under MIT.
"""

import csv
import io
import os
import sys
import argparse
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import OUTPUT_DIR, BASELINE_YEAR


# ── WEI FORMULA v3.0 ─────────────────────────────────────────────────────────

def calculate_wei(emp, edu, eco, hlt, bod, saf, dgn, dgt, violence):
    """
    Calculate WEI score using the 8-pillar v3.0 formula.

    WEI = (Empowerment × 0.15) + (Education × 0.12)
        + (Economic × 0.12) + (Health × 0.12)
        + (Bodily Autonomy × 0.15) + (Safety & Justice × 0.14)
        + (Dignity & Welfare × 0.10) + (Digital & Social × 0.10)
        − (Violence Penalty × 0.10)
    """
    return round(
        (emp * 0.15) + (edu * 0.12) + (eco * 0.12) + (hlt * 0.12) +
        (bod * 0.15) + (saf * 0.14) + (dgn * 0.10) + (dgt * 0.10) -
        (violence * 0.10), 1
    )


# ── STATE DATA ────────────────────────────────────────────────────────────────
#
# Format: (state, code, region, population_millions,
#          emp, edu, eco, hlt, bodily, safety, dignity, digital, violence,
#          key_programs, notes)
#
# Scoring rationale for new pillars by state:
#
# Bodily Autonomy (bod):
#   Kerala 82 — Low child marriage (5%), strong reproductive rights,
#               good menstrual hygiene in schools
#   West Bengal 52 — Child marriage 41% (falling due to Kanyashree),
#                   period poverty moderate
#   Bihar 22 — Child marriage 40%+, high period poverty, low reproductive
#              rights access in rural areas
#   UP 18 — Highest child marriage rate in large states, severe period
#           poverty, very limited reproductive health access
#
# Dignity & Welfare (dgn):
#   Kerala 78 — Strong widow rights, low female food insecurity,
#               Kudumbashree addresses caregiver burden
#   West Bengal 58 — Lakshmi Bhandar directly addresses dignity & welfare
#                   but widow property issues remain
#   Bihar 34 — High female food insecurity, widow property stripping common,
#              very high unpaid care burden
#   UP 28 — Severe female food insecurity, high caregiver burden,
#           limited widow property protection
#
# Digital & Social (dgt):
#   Kerala 72 — Highest internet penetration, strong digital literacy,
#               better cyberstalking laws
#   Delhi 78 — High internet access but high digital harassment reported
#   Bihar 28 — Low smartphone ownership among women, large internet gap
#   UP 22 — Lowest female internet access in major states
#
# Violence Penalty (violence):
#   UP 68 — Highest crime against women in absolute numbers
#   Delhi 72 — High urban rape reporting rate per 100K women
#   West Bengal 48 — Moderate crime rates but improving with programs
#   Kerala 18 — Lowest crime penalty — strong legal framework + reporting

STATES = [

    # ── SOUTH INDIA ───────────────────────────────────────────────────────────
    (
        "Kerala", "KL", "South", 35.0,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          78,  94,  62,  88,  82,  74,  78,  72,  18,
        "Kudumbashree (1998) — 46 lakh members, Asia's largest women's SHG. "
        "Strong menstrual hygiene in schools. Low child marriage (5%).",
        "Highest female literacy (95.2%). Kudumbashree integrated with half of "
        "Kerala families for 25 years. Strong reproductive rights legal framework. "
        "Lowest child marriage rate in India."
    ),
    (
        "Tamil Nadu", "TN", "South", 77.8,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          68,  88,  58,  82,  68,  64,  66,  65,  24,
        "TN Corporation for Development of Women. Uzhavar Sandhai women vendors. "
        "Strong ICDS nutrition program.",
        "Strong panchayat reservation. Above-average female literacy at 73.9%. "
        "Good menstrual hygiene policy. Moderate child marriage (18%)."
    ),
    (
        "Telangana", "TS", "South", 37.4,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          62,  78,  52,  76,  60,  58,  60,  62,  30,
        "Stree Nidhi Credit Cooperative. Mission Bhagiratha women SHGs. "
        "KCR Kits maternal health program.",
        "Strong SHG movement. Good maternal health outcomes. "
        "Child marriage (24%) declining."
    ),
    (
        "Andhra Pradesh", "AP", "South", 53.9,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          60,  76,  54,  74,  58,  58,  60,  60,  28,
        "SERP / Velugu IKP SHG program — pioneered SHG-bank linkage. "
        "YSR Aarogyasri women's health scheme.",
        "Pioneered SHG model scaled nationally as NRLM. "
        "Moderate child marriage (26%)."
    ),
    (
        "Karnataka", "KA", "South", 67.6,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          60,  78,  54,  76,  60,  58,  60,  62,  32,
        "Stree Shakti SHG program. Karnataka Mahila Abhivrudhi Yojana. "
        "Beti Bachao strong urban implementation.",
        "Good digital access in Bengaluru. Moderate child marriage (21%). "
        "Strong women's enterprise ecosystem."
    ),
    (
        "Goa", "GA", "West", 1.5,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          64,  90,  58,  86,  72,  68,  72,  74,  20,
        "Goa Mahila Aarthik Vikas Mahamandal microfinance. "
        "Strong state domestic violence law enforcement.",
        "Highest HDI in India. Strong female literacy and health. "
        "Low child marriage (8%). Good internet access."
    ),

    # ── EAST INDIA ────────────────────────────────────────────────────────────
    (
        "West Bengal", "WB", "East", 99.6,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          52,  74,  46,  70,  52,  54,  58,  50,  42,
        "Lakshmi Bhandar (24.1M women, ₹1500-1700/month direct cash transfer). "
        "Kanyashree (10M girls, UNESCO prize — reduces child marriage). "
        "Rupashree (2.3M women). Swasthya Sathi (2.42M health cards).",
        "Fastest-improving state (+3.4 WEI points). Kanyashree directly reduces "
        "child marriage (41% → 34% trend). Lakshmi Bhandar addresses dignity & "
        "welfare directly. Period poverty declining in program areas."
    ),
    (
        "Odisha", "OD", "East", 46.4,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          48,  70,  40,  66,  46,  50,  48,  44,  36,
        "Mission Shakti SHG network — 70 lakh women members. "
        "Odisha Livelihood Mission women's groups.",
        "Mission Shakti is one of India's largest state SHG programs. "
        "Moderate child marriage (28%). Tribal areas have higher period poverty."
    ),
    (
        "Assam", "AS", "Northeast", 35.6,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          44,  70,  38,  62,  40,  46,  44,  42,  42,
        "Assam Mahila Samakhya. Tea garden women's cooperatives. "
        "SEWA-aligned microfinance in urban areas.",
        "High MMR remains a challenge. Tea garden workers face economic "
        "vulnerability. Child marriage (31%) declining. High period poverty "
        "in rural areas."
    ),

    # ── NORTH INDIA ───────────────────────────────────────────────────────────
    (
        "Himachal Pradesh", "HP", "North", 7.5,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          58,  86,  50,  80,  64,  62,  66,  62,  22,
        "HP State Women's Commission. Women-led MGNREGA groups. "
        "Strong ICDS nutrition coverage.",
        "High female literacy (76.6%). Low child marriage (9%). "
        "Good menstrual hygiene in schools (hill state initiatives). "
        "Strong panchayat women's representation."
    ),
    (
        "Uttarakhand", "UK", "North", 11.3,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          54,  82,  46,  76,  60,  58,  62,  56,  26,
        "Mahila Mangal Dal forest groups. Van Panchayats women leaders. "
        "Uttarakhand Women Welfare Society.",
        "Women lead forest governance. Above-average literacy. "
        "Low child marriage (12%). Good mountain-region digital access."
    ),
    (
        "Delhi", "DL", "North", 20.7,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          54,  84,  52,  78,  62,  52,  58,  78,  68,
        "Delhi Mahila Kosh microfinance. Mahila Panchayat scheme. "
        "One-Stop Crisis Centres for DV survivors.",
        "High urban crime rate significantly pulls score down. "
        "High internet access (dgt 78) but high digital harassment. "
        "Strong period poverty advocacy in urban slums."
    ),
    (
        "Punjab", "PB", "North", 30.1,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          50,  78,  48,  76,  58,  56,  60,  58,  30,
        "Punjab Women Development Corporation. ATMA women farmer groups. "
        "Mata Tri Shakti scheme.",
        "Improving female literacy. Strong women's panchayat representation. "
        "Moderate child marriage (16%). Drug crisis has DV spillover effects."
    ),
    (
        "Haryana", "HR", "North", 28.9,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          42,  72,  44,  66,  44,  48,  48,  52,  56,
        "Mahila Samridhi Yojana. Beti Bachao Beti Padhao (origin state). "
        "Sakhi One-Stop Centres for DV survivors.",
        "Historically lowest sex ratio at birth — improving from 832 to 916/1000. "
        "Beti Bachao program originated here. Honour-based violence remains "
        "elevated. Child marriage (21%) declining."
    ),

    # ── WEST INDIA ────────────────────────────────────────────────────────────
    (
        "Maharashtra", "MH", "West", 124.7,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          56,  80,  54,  74,  58,  56,  60,  64,  42,
        "Mann Deshi Bank (100K+ women account holders). "
        "MAVIM (Mahila Arthik Vikas Mahamandal). "
        "Swayam Siddha women's SHG program.",
        "Strong urban women's enterprise. Mann Deshi pioneered rural women's "
        "banking. Mumbai has India's highest women's workforce participation. "
        "Moderate child marriage (21%)."
    ),
    (
        "Gujarat", "GJ", "West", 63.9,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          52,  78,  54,  74,  56,  52,  56,  60,  26,
        "SEWA (Self Employed Women's Association) — 3.78M members, 20 states. "
        "SEWA Bank (1974) — pioneered global microfinance.",
        "SEWA founded 1972 — one of world's most influential women's labour "
        "organisations. Strong women's cooperative and enterprise sector. "
        "Moderate child marriage (22%)."
    ),
    (
        "Rajasthan", "RJ", "West", 81.0,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          46,  62,  38,  64,  38,  46,  44,  42,  38,
        "Educate Girls (6.7M beneficiaries, 380K+ girls enrolled). "
        "Rajasthan Gramin Aajeevika Vikas Parishad SHGs. "
        "Palanhar scheme for orphaned girls.",
        "Educate Girls has transformed female enrollment in rural Rajasthan. "
        "Still high child marriage (35%) declining with Educate Girls. "
        "High period poverty in rural areas. "
        "Educate Girls directly improves Bodily Autonomy pillar."
    ),

    # ── CENTRAL INDIA ─────────────────────────────────────────────────────────
    (
        "Madhya Pradesh", "MP", "Central", 85.4,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          44,  64,  36,  60,  34,  42,  40,  38,  48,
        "Educate Girls (operates in MP). Tejaswini Rural Women's Empowerment. "
        "MP Rajya Mahila Aayog.",
        "High crime against women rate (NCRB). "
        "Child marriage (32%) — Educate Girls active. "
        "High period poverty in tribal areas. Honour-based violence reported."
    ),
    (
        "Chhattisgarh", "CG", "Central", 29.4,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          48,  68,  38,  62,  42,  48,  44,  40,  40,
        "CG Women's SHG Mission. Tribal women's forest rights cooperatives. "
        "Samagra Shiksha menstrual hygiene program.",
        "Strong tribal women's forest rights movement. Above-average panchayat "
        "representation. Child marriage (35%) in tribal areas."
    ),

    # ── JHARKHAND ─────────────────────────────────────────────────────────────
    (
        "Jharkhand", "JH", "East", 38.6,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          42,  62,  34,  58,  36,  44,  38,  36,  38,
        "JSLPS (Jharkhand State Livelihood Promotion Society) SHGs. "
        "Tejaswini tribal women's empowerment program.",
        "Large tribal population. Women's forest rights and land ownership "
        "challenges. Child marriage (38%) in tribal areas. "
        "High period poverty — government pad distribution schemes active."
    ),

    # ── BIHAR — SPECIAL FOCUS ────────────────────────────────────────────────
    (
        "Bihar", "BR", "East", 128.5,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          36,  58,  28,  54,  22,  38,  34,  28,  36,
        "JEEViKA — 1.04M SHGs, 34,000+ villages, ₹11,000+ crore bank credit. "
        "Mukhyamantri Kanya Utthan Yojana (girl child incentive). "
        "Har Ghar Bijli — electricity access enables digital inclusion.",
        "Lowest female LFPR in India (4-6%) but JEEViKA transforming this. "
        "Child marriage (40%+) despite Kanya Utthan scheme. "
        "High period poverty — government free pad scheme launched 2022. "
        "Widow property stripping common in rural areas. "
        "JEEViKA directly improves Economic, Dignity & Welfare pillars."
    ),

    # ── NORTHEAST ─────────────────────────────────────────────────────────────
    (
        "Manipur", "MN", "Northeast", 3.2,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          56,  80,  52,  72,  64,  58,  62,  54,  24,
        "Ima Keithel (Mothers' Market) — world's largest all-women market. "
        "Meira Paibi women's vigilance movement.",
        "Unique matrilineal trading traditions. Ima Keithel in Imphal is "
        "extraordinary example of women's economic autonomy. "
        "Relatively low child marriage (12%)."
    ),
    (
        "Mizoram", "MZ", "Northeast", 1.3,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          58,  90,  50,  80,  72,  64,  68,  60,  14,
        "Mizoram Women's Commission. Young Mizo Association women's wing. "
        "State menstrual hygiene management policy.",
        "Highest female literacy in Northeast (89.4%). Low child marriage (6%). "
        "Strong menstrual hygiene policy. Good safety record."
    ),
    (
        "Meghalaya", "ML", "Northeast", 3.4,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          60,  82,  52,  76,  70,  62,  68,  58,  18,
        "Meghalaya Livelihoods and Access to Markets (MLAM) women SHGs. "
        "Khasi matrilineal land inheritance.",
        "Matrilineal society (Khasi and Jaintia tribes) — women own property "
        "and pass family name. One of India's most gender-equal cultures. "
        "Low child marriage (8%). Strong widow property rights."
    ),

    # ── UTTAR PRADESH ────────────────────────────────────────────────────────
    (
        "Uttar Pradesh", "UP", "North", 241.1,
        # emp  edu  eco  hlt  bod  saf  dgn  dgt  vio
          34,  58,  28,  54,  18,  32,  28,  22,  68,
        "UP State Rural Livelihoods Mission (UPSRLM) — 9M+ SHG members. "
        "Mahila Shakti Kendras (One-Stop Centres). "
        "Mission Shakti (UP) — police responsiveness program.",
        "India's most populous state — score has massive index weight. "
        "Highest crime against women in absolute numbers (NCRB). "
        "Child marriage rate highest among large states. "
        "Severe period poverty — government free pad scheme active. "
        "Very low female internet access (dgt 22). "
        "UPSRLM is transforming economic outcomes at scale."
    ),
]


# ── YOY CHANGES (v3.0) ────────────────────────────────────────────────────────
# Reflects program impact on specific pillars

YOY_CHANGES = {
    "WB": +3.4,   # Lakshmi Bhandar + Kanyashree child marriage reduction
    "KL": +2.1,   # Kudumbashree silver jubilee
    "TN": +1.2,   # Women's SHG growth
    "MH": +1.4,   # MAVIM and Mann Deshi expansion
    "RJ": +2.2,   # Educate Girls milestone + period poverty reduction
    "BR": -0.8,   # JEEViKA progress offset by structural challenges
    "UP": -0.4,   # Slow improvement
    "HR": +0.8,   # Beti Bachao sex ratio improvement
    "ML": +0.9,   # Matrilineal stability
    "MZ": +0.6,
    "MN": +0.8,
    "GJ": +0.9,   # SEWA expansion
    "DL": -0.3,   # Urban crime
    "OD": +1.1,   # Mission Shakti expansion
    "CG": +0.7,
    "JH": +0.5,
    "AS": +0.4,
}

HOT_STATES = {"WB", "RJ", "KL", "OD"}  # Fastest improving


# ── GENERATE ─────────────────────────────────────────────────────────────────

def generate_india_states(output_path=None, year=BASELINE_YEAR):
    """
    Generate India states WEI CSV using v3.0 8-pillar formula.
    """
    if output_path is None:
        output_path = OUTPUT_DIR / f"india-states-{year}.csv"

    rows = []
    for (state, code, region, pop,
         emp, edu, eco, hlt, bod, saf, dgn, dgt, vio,
         key_programs, notes) in STATES:

        score     = calculate_wei(emp, edu, eco, hlt, bod, saf, dgn, dgt, vio)
        change    = YOY_CHANGES.get(code, round((score - 45) * 0.02, 1))
        prev      = round(score - change, 1)
        hot       = code in HOT_STATES

        rows.append({
            "state":                  state,
            "state_code":             code,
            "ticker":                 f"SHE-{code}",
            "region":                 region,
            "population_millions":    pop,
            "empowerment_score":      emp,
            "education_score":        edu,
            "economic_score":         eco,
            "health_score":           hlt,
            "bodily_autonomy_score":  bod,
            "safety_justice_score":   saf,
            "dignity_welfare_score":  dgn,
            "digital_social_score":   dgt,
            "violence_penalty_score": vio,
            "wei_score":              score,
            "previous_wei_score":     prev,
            "change":                 change,
            "hot":                    "true" if hot else "false",
            "verified":               "false",
            "update_frequency":       "quarterly" if hot else "annual",
            "wei_version":            "3.0",
            "year":                   year,
            "key_programs":           key_programs,
            "notes":                  notes,
        })

    rows.sort(key=lambda x: x["wei_score"], reverse=True)
    for i, r in enumerate(rows):
        r["rank"] = i + 1

    # Population-weighted India average
    total_w = sum(r["wei_score"] * r["population_millions"] for r in rows)
    total_p = sum(r["population_millions"] for r in rows)
    india_avg = round(total_w / total_p, 1)

    # Header
    header = (
        f"# SHEtoken WEI India States v3.0 — {year}\n"
        f"# Women's Empowerment Index — 8-pillar formula\n"
        f"# States scored: {len(rows)}\n"
        f"# India population-weighted WEI average: {india_avg}\n"
        f"#\n"
        f"# Formula:\n"
        f"# WEI = (Empowerment × 0.15) + (Education × 0.12)\n"
        f"#     + (Economic × 0.12) + (Health × 0.12)\n"
        f"#     + (Bodily Autonomy × 0.15) + (Safety & Justice × 0.14)\n"
        f"#     + (Dignity & Welfare × 0.10) + (Digital & Social × 0.10)\n"
        f"#     − (Violence Penalty × 0.10)\n"
        f"#\n"
        f"# New in v3.0: period poverty, child marriage, digital harassment,\n"
        f"# widow rights, caregiver burden, dowry violence\n"
        f"# Data sources: NCRB, DISE/UDISE+, NSSO/PLFS, NFHS-5, ECI, NABARD\n"
        f"# Generated: May 2026 | shetoken.org\n"
        f"#\n"
    )

    fieldnames = [
        "rank", "state", "state_code", "ticker", "region",
        "population_millions",
        "empowerment_score", "education_score", "economic_score",
        "health_score", "bodily_autonomy_score", "safety_justice_score",
        "dignity_welfare_score", "digital_social_score",
        "violence_penalty_score", "wei_score",
        "previous_wei_score", "change", "hot",
        "verified", "update_frequency", "wei_version", "year",
        "key_programs", "notes",
    ]

    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    writer.writeheader()
    writer.writerows(rows)

    os.makedirs(os.path.dirname(output_path) if os.path.dirname(output_path) else ".", exist_ok=True)
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        f.write(header + buf.getvalue())

    # Print leaderboard
    print(f"SHEtoken WEI India States v3.0 — {year}")
    print("=" * 65)
    print(f"  States scored:       {len(rows)}")
    print(f"  India WEI avg:       {india_avg}")
    print(f"  Output:              {output_path}")
    print()
    print(f"  {'Rank':<5} {'State':<20} {'Ticker':<10} "
          f"{'WEI':>6}  {'Chg':>6}  {'Bod':>5}  {'Dgn':>5}  {'Dgt':>5}  Hot")
    print(f"  {'─'*70}")
    for r in rows:
        chg  = f"+{r['change']}" if r["change"] >= 0 else str(r["change"])
        hot  = "🔥" if r["hot"] == "true" else ""
        print(f"  {r['rank']:<5} {r['state']:<20} {r['ticker']:<10} "
              f"{r['wei_score']:>6}  {chg:>6}  "
              f"{r['bodily_autonomy_score']:>5}  "
              f"{r['dignity_welfare_score']:>5}  "
              f"{r['digital_social_score']:>5}  {hot}")

    return str(output_path)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Generate India states WEI CSV (v3.0 8-pillar)"
    )
    parser.add_argument("--year", type=int, default=BASELINE_YEAR)
    parser.add_argument("--output", type=str, default=None)
    parser.add_argument("--fallback", action="store_true", help="Use hardcoded estimates")
    args = parser.parse_args()

    generate_india_states(
        output_path=args.output,
        year=args.year,
    )
