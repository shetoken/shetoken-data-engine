"""
SHEtoken — Women's AI Displacement Index (WADI)
================================================
Tracks the gender-differentiated impact of AI and automation
on women's employment, income, and economic security.

AI displacement is not gender-neutral. Women are concentrated
in high-automation-risk sectors (admin, garment, data entry,
customer service) while being underrepresented in low-risk
sectors (engineering, trades, management).

Simultaneously, women face a digital skills gap that limits
their ability to transition into AI-adjacent roles.

Dimensions tracked:
  1. Sector exposure score    — % female workforce in high-risk jobs
  2. Digital skills gap       — women's digital literacy vs men's
  3. Reskilling access gap    — access to retraining programs
  4. Care economy wage trap   — % who will absorb into care sector
  5. AI opportunity capture   — % of women in AI/tech jobs
  6. Remote work access       — can they access remote AI-safe jobs?
  7. Social protection gap    — unemployment coverage if displaced
  8. Gig economy vulnerability — informal/gig = no safety net

WADI Score: 0-100 (higher = more vulnerable to AI displacement)

Sources:
  McKinsey Global Institute — Women in the Future of Work (2021)
  WEF Future of Jobs Report 2023
  ILO World Employment and Social Outlook 2024
  OECD Employment Outlook 2023
  Oxford Martin School Automation Risk by Occupation
  World Bank Digital Skills Report
  GSMA Mobile Gender Gap Report 2023

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, json
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

# ── HIGH-RISK OCCUPATIONS — female concentration ─────────────────────────────
HIGH_RISK_OCCUPATIONS = {
    "data_entry_clerks":           {"automation_risk": 96, "pct_female": 72},
    "administrative_assistants":   {"automation_risk": 96, "pct_female": 90},
    "bank_tellers":                {"automation_risk": 98, "pct_female": 70},
    "customer_service_reps":       {"automation_risk": 79, "pct_female": 65},
    "garment_textile_workers":     {"automation_risk": 83, "pct_female": 80},
    "cashiers_checkout":           {"automation_risk": 97, "pct_female": 73},
    "payroll_bookkeeping":         {"automation_risk": 98, "pct_female": 82},
    "receptionists":               {"automation_risk": 96, "pct_female": 93},
    "secretaries":                 {"automation_risk": 96, "pct_female": 94},
    "food_processing_workers":     {"automation_risk": 78, "pct_female": 55},
    "telemarketers":               {"automation_risk": 99, "pct_female": 61},
    "insurance_claims_handlers":   {"automation_risk": 98, "pct_female": 72},
    "medical_transcriptionists":   {"automation_risk": 98, "pct_female": 89},
    "travel_agents":               {"automation_risk": 97, "pct_female": 76},
    "retail_workers":              {"automation_risk": 92, "pct_female": 57},
}

# LOW-RISK — predominantly male
LOW_RISK_OCCUPATIONS = {
    "civil_engineers":             {"automation_risk":  8, "pct_female": 14},
    "electricians_plumbers":       {"automation_risk": 15, "pct_female":  3},
    "construction_managers":       {"automation_risk":  6, "pct_female": 10},
    "software_developers":         {"automation_risk":  4, "pct_female": 25},
    "mechanical_engineers":        {"automation_risk":  7, "pct_female": 12},
    "physical_therapists":         {"automation_risk":  2, "pct_female": 72},  # exception
    "physicians_doctors":          {"automation_risk":  3, "pct_female": 37},
    "teachers_professors":         {"automation_risk": 12, "pct_female": 53},
}

# CARE ECONOMY — automation-resistant but underpaid
CARE_ECONOMY = {
    "registered_nurses":           {"automation_risk":  1, "pct_female": 88},
    "home_health_aides":           {"automation_risk":  4, "pct_female": 89},
    "childcare_workers":           {"automation_risk":  2, "pct_female": 95},
    "social_workers":              {"automation_risk":  2, "pct_female": 79},
    "personal_care_aides":         {"automation_risk":  3, "pct_female": 84},
    "preschool_teachers":          {"automation_risk":  2, "pct_female": 97},
    "elder_care_workers":          {"automation_risk":  4, "pct_female": 92},
}


# ── COUNTRY DATA ──────────────────────────────────────────────────────────────
# country, iso, region,
# pct_female_workforce_in_high_risk_sectors,  % of working women in automation-exposed jobs
# digital_skills_gap_score,    women's digital skills as % of men's (100=equal)
# reskilling_access_score,     women's access to retraining (0-100)
# care_economy_wage_ratio,     care economy wages as % of national median
# pct_women_in_ai_tech,        % of AI/tech workforce who are women
# remote_work_access_pct,      % of women who can work remotely
# unemployment_coverage_pct,   % of women covered by unemployment insurance
# gig_worker_pct,              % of women in informal/gig work
# ai_policy_gender_inclusion,  0-10 (does country's AI strategy mention gender?)
# notes

COUNTRY_DATA = [
    # TIER 1 — Strong protections but still exposed
    ("Iceland",      "ISL","Europe",       28, 94, 80, 82, 38, 72, 85,  8, 8,  "Strong social protection. AI strategy includes gender clause. Low garment sector."),
    ("Norway",       "NOR","Europe",       30, 93, 78, 84, 32, 70, 84,  9, 8,  "Oil sector automation displacing women in admin. Strong retraining programs."),
    ("Sweden",       "SWE","Europe",       32, 92, 76, 82, 30, 68, 82, 10, 9,  "Automation commission includes gender. High digital literacy."),
    ("Germany",      "DEU","Europe",       38, 88, 70, 78, 22, 60, 80, 12, 7,  "Manufacturing automation. 4 million women in admin jobs at risk. Kurzarbeit protects."),
    ("UK",           "GBR","Europe",       42, 88, 68, 72, 24, 62, 76, 14, 6,  "2.4M women in admin at risk. Universal Credit inadequate. Taylor Review gaps."),
    ("USA",          "USA","N. America",   44, 86, 62, 68, 28, 64, 58, 18, 5,  "No federal reskilling mandate. Garment, admin, call centre exposure high. Gig economy vulnerable."),
    ("Japan",        "JPN","East Asia",    52, 80, 55, 74, 18, 44, 82, 22, 4,  "75% of at-risk admin jobs held by women. Lowest AI/tech female participation. 'Shufu' system traps women in part-time."),
    ("South Korea",  "KOR","East Asia",    48, 78, 52, 72, 20, 48, 78, 24, 4,  "High export manufacturing exposure. Women concentrated in textiles."),
    ("Australia",    "AUS","Oceania",      40, 88, 68, 70, 26, 62, 72, 14, 6,  "Strong protections but 1.8M women in high-risk roles."),
    ("Canada",       "CAN","N. America",   38, 90, 72, 72, 28, 64, 74, 12, 7,  "Strong reskilling programs. Indigenous women most exposed."),

    # TIER 2 — High exposure, weaker protection
    ("India",        "IND","South Asia",   58, 42, 22, 30, 12, 18, 12, 68, 3,
     "230M women in high-risk jobs: garment (8M), data entry (12M), "
     "domestic work (30M+). Digital skills gap severe. Only 3% female AI workforce. "
     "BPO sector (call centres) employs 2M women — 70% automation risk."),
    ("Bangladesh",   "BGD","South Asia",   72, 28, 12, 28, 4,  8,  4, 82, 1,
     "CRITICAL: 4M women garment workers — highest global automation risk. "
     "80% of export garment workforce is female. Automation of sewing = "
     "4M job losses projected by 2030. No reskilling infrastructure."),
    ("Vietnam",      "VNM","SE Asia",      64, 48, 28, 38, 8,  22, 8, 72, 2,
     "2.8M women in electronics/garment assembly. Samsung, Nike automation. "
     "Digital economy growing but women capture only 12% of tech jobs."),
    ("Indonesia",    "IDN","SE Asia",      60, 44, 24, 32, 6,  18, 8, 76, 2,
     "Batik, garment, tobacco processing — all high automation risk. "
     "Ojek (ride-share) gig workers — women excluded by safety concerns."),
    ("Philippines",  "PHL","SE Asia",      62, 52, 38, 42, 12, 32, 14, 64, 3,
     "1.3M women in BPO (call centres) — 75% female, 79% automation risk. "
     "Remittance-dependent economy: OFW (overseas workers) also exposed."),
    ("Brazil",       "BRA","S. America",   48, 62, 42, 52, 14, 38, 38, 44, 4,
     "Domestic workers (5.7M women) — informal, no safety net. "
     "Afro-Brazilian women most exposed. Gig platform workers unprotected."),
    ("Mexico",       "MEX","N. America",   52, 58, 36, 44, 10, 28, 22, 58, 3,
     "Maquiladora sector (export manufacturing) — 60% female, high automation. "
     "NAFTA reshoring + AI = double pressure. No federal retraining."),
    ("South Africa", "ZAF","Africa",       44, 52, 32, 48, 8,  28, 32, 48, 3,
     "Domestic work (1.4M women) — no labour protections. "
     "Mining sector automation minimal female impact (few women in mining)."),
    ("China",        "CHN","East Asia",    54, 68, 38, 60, 18, 36, 52, 38, 5,
     "Foxconn automation displacing 1M+ women. Wenzhou shoe factories. "
     "Strong government retraining programs but rural women excluded."),
    ("Turkey",       "TUR","Europe/Asia",  46, 62, 38, 52, 10, 32, 42, 42, 3,
     "Textile sector (85% female) — highest automation risk in manufacturing."),
    ("Kenya",        "KEN","Africa",       38, 44, 28, 38, 6,  18, 6, 72, 2,
     "M-Pesa disrupted women money handlers. Flower export sector at risk. "
     "Growing digital economy but women capture small share."),
    ("Nigeria",      "NGA","Africa",       46, 32, 18, 28, 4,  12, 4, 82, 1,
     "Market trader women — platform competition from Jumia/Konga. "
     "Fintech disrupting women's savings cooperatives (ajo/esusu)."),
    ("Ethiopia",     "ETH","Africa",       62, 22, 10, 22, 2,  8,  2, 86, 1,
     "Hawassa Industrial Park: 60,000 women garment workers. "
     "Chinese-owned factories automating fastest. Zero reskilling."),
    ("Pakistan",     "PAK","South Asia",   54, 32, 14, 28, 4,  8,  4, 84, 1,
     "Textile sector (70% female) — automation of spinning, weaving. "
     "Low digital literacy. No AI gender policy."),
    ("Ghana",        "GHA","Africa",       42, 38, 22, 36, 4,  14, 6, 74, 2,
     "Market women — platform competition. Cocoa processing automation."),
    ("Rwanda",       "RWA","Africa",       36, 48, 32, 34, 6,  18, 8, 62, 3,
     "Government digital inclusion programs for women. Tech hub growing."),
    ("Cambodia",     "KHM","SE Asia",      78, 24, 10, 24, 2,  8,  2, 88, 1,
     "MOST EXPOSED: 90% of garment workers are women. "
     "H&M, Zara factories automating. 700,000 jobs at risk by 2030. "
     "Entire female economy depends on one high-risk sector."),
    ("Sri Lanka",    "LKA","South Asia",   60, 48, 28, 38, 6,  22, 8, 64, 2,
     "Tea plucking (women) — robotisation beginning. Garment sector."),
]


def compute_wadi(row: dict) -> float:
    """
    WADI Score: higher = more vulnerable to AI displacement.
    0-100 scale.
    """
    # Sector exposure (higher = worse)
    d_sector   = row["pct_female_workforce_in_high_risk_sectors"]
    # Digital skills gap (lower = worse, invert)
    d_digital  = 100 - row["digital_skills_gap_score"]
    # Reskilling access (lower = worse, invert)
    d_reskill  = 100 - row["reskilling_access_score"]
    # AI opportunity capture (lower = worse, invert)
    d_ai_opp   = 100 - row["pct_women_in_ai_tech"] * 2  # *2 to scale
    # Remote work access (lower = worse, invert)
    d_remote   = 100 - row["remote_work_access_pct"]
    # Social protection (lower = worse, invert)
    d_social   = 100 - row["unemployment_coverage_pct"]
    # Gig vulnerability (higher = worse)
    d_gig      = row["gig_worker_pct"]
    # AI policy inclusion (lower = worse, invert)
    d_policy   = 100 - row["ai_policy_gender_inclusion"] * 10

    return round(
        d_sector  * 0.25 +
        d_digital * 0.15 +
        d_reskill * 0.15 +
        d_ai_opp  * 0.10 +
        d_remote  * 0.10 +
        d_social  * 0.10 +
        d_gig     * 0.10 +
        d_policy  * 0.05, 1
    )


def generate(year=BASELINE_YEAR):
    rows = []
    for stat in COUNTRY_DATA:
        (country, iso, region,
         sector_exp, dig_gap, reskill, care_wage,
         ai_women, remote, unemp, gig, ai_policy, notes) = stat

        row = {
            "country":                              country,
            "iso_code":                             iso,
            "region":                               region,
            "pct_female_workforce_in_high_risk_sectors": sector_exp,
            "digital_skills_gap_score":             dig_gap,
            "reskilling_access_score":              reskill,
            "care_economy_wage_ratio":              care_wage,
            "pct_women_in_ai_tech":                 ai_women,
            "remote_work_access_pct":               remote,
            "unemployment_coverage_pct":            unemp,
            "gig_worker_pct":                       gig,
            "ai_policy_gender_inclusion":           ai_policy,
            "notes":                                notes,
            "year":                                 year,
        }
        row["wadi_score"] = compute_wadi(row)
        rows.append(row)

    rows.sort(key=lambda x: x["wadi_score"], reverse=True)
    for i, r in enumerate(rows): r["rank"] = i + 1

    # Global stats
    avg_exposure = round(
        sum(r["pct_female_workforce_in_high_risk_sectors"] for r in rows) / len(rows), 1)

    out = OUTPUT_DIR / f"ai-displacement-index-{year}.csv"
    hdr = (
        f"# SHEtoken Women's AI Displacement Index (WADI) — {year}\n"
        f"# WADI: higher score = more vulnerable to AI/automation displacement\n"
        f"# Average % of female workforce in high-risk sectors: {avg_exposure}%\n"
        f"#\n"
        f"# CRITICAL CASES:\n"
        f"# Cambodia: 90% of garment workers female, 78% in high-risk sectors\n"
        f"# Bangladesh: 4M women garment workers face near-total automation by 2030\n"
        f"# Japan: 75% of at-risk admin jobs held by women, lowest AI female entry\n"
        f"# Philippines: 1.3M women in call centres — 79% automation risk\n"
        f"# India: 230M+ women in high-risk jobs across sectors\n"
        f"#\n"
        f"# Sources: McKinsey WFF 2021, WEF FoJ 2023, ILO WESO 2024,\n"
        f"#          OECD Employment Outlook 2023, GSMA Mobile Gender Gap 2023\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )

    fnames = [
        "rank","country","iso_code","region","wadi_score",
        "pct_female_workforce_in_high_risk_sectors",
        "digital_skills_gap_score","reskilling_access_score",
        "care_economy_wage_ratio","pct_women_in_ai_tech",
        "remote_work_access_pct","unemployment_coverage_pct",
        "gig_worker_pct","ai_policy_gender_inclusion",
        "notes","year",
    ]

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fnames, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    with open(out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr + buf.getvalue())

    # Save high-risk occupation reference
    occ_out = OUTPUT_DIR / "ai-high-risk-occupations.json"
    with open(occ_out,"w",encoding="utf-8") as f:
        json.dump({
            "description": "Occupations with high automation risk — female concentration",
            "sources": "McKinsey 2021, Oxford Martin School, WEF 2023",
            "high_risk_female_dominated": HIGH_RISK_OCCUPATIONS,
            "low_risk_male_dominated": LOW_RISK_OCCUPATIONS,
            "care_economy_automation_resistant": CARE_ECONOMY,
            "key_finding": (
                "Women are 2-3x more concentrated in high-automation-risk jobs than men. "
                "The care economy (nursing, childcare) is automation-resistant but "
                "systematically underpaid. Displaced women are likely to move into "
                "care work with no wage improvement."
            ),
        }, f, indent=2, ensure_ascii=False)

    # Print report
    print(f"Women's AI Displacement Index (WADI) — {year}")
    print("="*70)
    print(f"  Countries: {len(rows)} | Avg sector exposure: {avg_exposure}%")
    print()
    print(f"  {'Rk':<4} {'Country':<18} {'WADI':>6} "
          f"{'Sector%':>8} {'Digital':>8} {'Reskill':>8} {'AI Jobs%':>9}")
    print(f"  {'─'*65}")
    for r in rows[:20]:
        print(f"  {r['rank']:<4} {r['country']:<18} {r['wadi_score']:>6} "
              f"{r['pct_female_workforce_in_high_risk_sectors']:>7}% "
              f"{r['digital_skills_gap_score']:>7}% "
              f"{r['reskilling_access_score']:>7}% "
              f"{r['pct_women_in_ai_tech']:>8}%")
    print()
    print(f"  CRITICAL — Bangladesh garment sector:")
    bgd = next(r for r in rows if r["iso_code"]=="BGD")
    print(f"    % female workforce in high-risk:  {bgd['pct_female_workforce_in_high_risk_sectors']}%")
    print(f"    Digital skills gap score:          {bgd['digital_skills_gap_score']}/100")
    print(f"    Reskilling access:                 {bgd['reskilling_access_score']}/100")
    print(f"    Unemployment coverage:             {bgd['unemployment_coverage_pct']}%")
    print(f"    WADI score:                        {bgd['wadi_score']}/100 (higher=more vulnerable)")
    print()
    print(f"  HIGH-RISK OCCUPATIONS — female concentration:")
    for occ, data in sorted(HIGH_RISK_OCCUPATIONS.items(),
                             key=lambda x: x[1]['automation_risk'], reverse=True)[:8]:
        print(f"    {occ:<40} risk:{data['automation_risk']}%  female:{data['pct_female']}%")
    print(f"\n  Saved: {out}")
    print(f"  Saved: {occ_out}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=BASELINE_YEAR)
    generate(p.parse_args().year)
