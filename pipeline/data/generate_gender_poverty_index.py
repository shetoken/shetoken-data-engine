"""
SHEtoken Pipeline — Gender Poverty & Wealth Index
===================================================
Generates a Gender Poverty Index (GPI) comparing women's
poverty and wealth position vs men, by country.

Dimensions:
  1. Income poverty gap (female vs male poverty headcount)
  2. Wealth gap (female median wealth as % of male)
  3. Financial exclusion gap (unbanked women vs men)
  4. Labour income gap (female earned income as % of male)
  5. Food insecurity gap (FAO gender-disaggregated)
  6. Time poverty (unpaid care work hours — women vs men)
  7. Asset ownership gap (land, property)
  8. Social protection coverage gap

Composite GPI score: 0-100
  100 = perfect equality
  50  = women at half the wealth/income of men
  0   = women completely excluded

Sources: World Bank, FAO, ILO, OECD, Credit Suisse, ICRW

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, argparse
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR


# country, iso, region,
# income_poverty_gap,      # female poverty % / male poverty % ratio (1.0 = equal)
# wealth_ratio,            # female median wealth / male median wealth (%)
# wage_ratio,              # female wage / male wage (%)
# labour_participation_ratio, # female LFPR / male LFPR (%)
# bank_account_ratio,      # female banked % / male banked %
# food_insecurity_gap,     # extra % of women food insecure vs men
# unpaid_care_hours_ratio, # female unpaid hours / male unpaid hours
# land_ownership_ratio,    # female landowners / total landowners (%)
# social_protection_gap,   # % women covered / % men covered

GPI_DATA = [
    # TIER 1 — Near equality
    ("Iceland",      "ISL","Europe",       1.02, 78, 88, 84, 98,  0.5, 1.8, 44, 97),
    ("Norway",       "NOR","Europe",       1.03, 76, 86, 82, 98,  0.6, 1.9, 43, 96),
    ("Finland",      "FIN","Europe",       1.04, 74, 84, 80, 98,  0.8, 2.1, 42, 96),
    ("Sweden",       "SWE","Europe",       1.02, 79, 87, 83, 99,  0.5, 1.7, 45, 97),
    ("Germany",      "DEU","Europe",       1.08, 70, 78, 75, 98,  1.2, 2.4, 40, 95),
    ("Canada",       "CAN","N. America",   1.10, 68, 76, 78, 98,  1.0, 2.2, 40, 94),
    ("Australia",    "AUS","Oceania",      1.12, 66, 72, 74, 98,  1.2, 2.5, 38, 93),
    ("USA",          "USA","N. America",   1.18, 62, 74, 74, 94,  1.5, 2.6, 36, 90),
    ("UK",           "GBR","Europe",       1.14, 65, 74, 75, 98,  1.2, 2.4, 37, 93),
    ("Japan",        "JPN","East Asia",    1.05, 65, 74, 62, 97,  0.5, 3.8, 22, 92),
    ("South Korea",  "KOR","East Asia",    1.06, 60, 66, 58, 97,  0.8, 3.5, 18, 90),
    # TIER 2
    ("Brazil",       "BRA","S. America",   1.32, 48, 68, 58, 75,  3.5, 3.2, 22, 72),
    ("Mexico",       "MEX","N. America",   1.38, 44, 64, 48, 64,  4.0, 4.5, 20, 68),
    ("India",        "IND","South Asia",   1.52, 32, 64, 28, 48,  8.0, 5.8, 14, 36),
    ("China",        "CHN","East Asia",    1.28, 58, 78, 72, 78,  2.0, 2.8, 28, 82),
    ("Indonesia",    "IDN","SE Asia",      1.42, 40, 72, 52, 52, 5.0, 3.8, 18, 56),
    ("Philippines",  "PHL","SE Asia",      1.22, 48, 78, 62, 62,  3.2, 3.2, 26, 64),
    ("South Africa", "ZAF","Africa",       1.38, 38, 58, 52, 62,  5.5, 3.5, 18, 65),
    ("Nigeria",      "NGA","Africa",       1.55, 28, 56, 52, 34, 10.0, 4.8, 12, 28),
    ("Kenya",        "KEN","Africa",       1.45, 32, 58, 64, 52,  8.0, 4.2, 16, 42),
    ("Bangladesh",   "BGD","South Asia",   1.48, 26, 60, 36, 46, 8.5, 5.2, 10, 34),
    ("Pakistan",     "PAK","South Asia",   1.65, 20, 56, 22, 16, 10.0, 7.2,  6, 18),
    ("Vietnam",      "VNM","SE Asia",      1.30, 45, 80, 72, 58,  3.0, 3.0, 22, 72),
    ("Thailand",     "THA","SE Asia",      1.22, 52, 82, 64, 78,  2.5, 2.8, 24, 80),
    # TIER 3
    ("Ethiopia",     "ETH","Africa",       1.62, 18, 58, 82, 30, 12.0, 5.5,  8, 18),
    ("Tanzania",     "TZA","Africa",       1.55, 20, 62, 86, 36, 10.0, 5.2, 10, 24),
    ("Myanmar",      "MMR","SE Asia",      1.42, 30, 66, 52, 40,  6.0, 4.2, 12, 38),
    ("Egypt",        "EGY","Africa/ME",   1.52, 30, 62, 20, 24,  6.5, 5.0,  8, 45),
    # TIER 4
    ("Afghanistan",  "AFG","South Asia",   1.72, 10, 38, 18,  2, 14.0, 8.5,  2,  4),
    ("Niger",        "NER","Africa",       1.75,  8, 44, 44, 10, 16.0, 7.0,  4,  8),
    ("Mali",         "MLI","Africa",       1.68, 10, 46, 72, 18, 14.0, 6.5,  4, 10),
    ("Chad",         "TCD","Africa",       1.70, 10, 44, 64, 10, 15.0, 7.0,  4,  8),
    ("Somalia",      "SOM","Africa",       1.72,  8, 42, 22,  4, 16.0, 8.0,  2,  4),
    ("Yemen",        "YEM","Middle East",  1.68, 10, 42, 10,  4, 14.0, 7.5,  4,  6),
]


def compute_gpi(row_data: tuple) -> dict:
    (country, iso, region,
     income_gap, wealth_ratio, wage_ratio, labour_ratio,
     bank_ratio, food_gap, care_ratio, land_pct, social_pct) = row_data

    # GPI dimensions — each scored 0-100 where 100=equality
    # Income poverty: 1.0 ratio = 100, 2.0 ratio = 0
    d_income  = round(max(0, min(100, (2.0 - income_gap) / 1.0 * 100)), 1)
    d_wealth  = round(wealth_ratio, 1)
    d_wage    = round(wage_ratio, 1)
    d_labour  = round(labour_ratio, 1)
    d_bank    = round(bank_ratio, 1)
    # Food insecurity: 0 gap=100, 20 gap=0
    d_food    = round(max(0, min(100, (20 - food_gap) / 20 * 100)), 1)
    # Care work: 1.0 ratio=100, 10.0 ratio=0
    d_care    = round(max(0, min(100, (10 - care_ratio) / 9 * 100)), 1)
    d_land    = round(land_pct * 2, 1)   # land_pct already % of owners who are female (ideal=50)
    d_social  = round(social_pct, 1)

    # Composite GPI (equal weights)
    gpi = round(sum([d_income, d_wealth, d_wage, d_labour, d_bank,
                     d_food, d_care, d_land, d_social]) / 9, 1)

    return {
        "country":                      country,
        "iso_code":                     iso,
        "region":                       region,
        "gpi_score":                    gpi,
        "gpi_income_poverty":           d_income,
        "gpi_wealth":                   d_wealth,
        "gpi_wage":                     d_wage,
        "gpi_labour_participation":     d_labour,
        "gpi_financial_inclusion":      d_bank,
        "gpi_food_security":            d_food,
        "gpi_time_poverty":             d_care,
        "gpi_land_ownership":           d_land,
        "gpi_social_protection":        d_social,
        # Raw values
        "income_poverty_ratio_f_to_m":  income_gap,
        "wealth_ratio_f_to_m_pct":      wealth_ratio,
        "wage_ratio_f_to_m_pct":        wage_ratio,
        "labour_ratio_f_to_m_pct":      labour_ratio,
        "bank_account_ratio_f_to_m_pct":bank_ratio,
        "food_insecurity_gap_pct":      food_gap,
        "unpaid_care_hours_ratio_f_to_m": care_ratio,
        "female_land_ownership_pct":    land_pct,
        "social_protection_coverage_f_pct": social_pct,
        "year": BASELINE_YEAR,
    }


def generate(year=BASELINE_YEAR):
    rows = [compute_gpi(stat) for stat in GPI_DATA]
    rows.sort(key=lambda x: x["gpi_score"], reverse=True)
    for i,r in enumerate(rows): r["rank"] = i+1

    avg = round(sum(r["gpi_score"] for r in rows) / len(rows), 1)
    out = OUTPUT_DIR / f"gender-poverty-index-{year}.csv"

    hdr = (
        f"# SHEtoken Gender Poverty Index (GPI) — {year}\n"
        f"# GPI measures gender equality across 9 economic dimensions\n"
        f"# Score 100=equality, 50=women half of men, 0=total exclusion\n"
        f"# Simple average GPI across all countries: {avg}\n"
        f"# Sources: World Bank, FAO, ILO, OECD, Credit Suisse, ICRW\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    flds = ["rank","country","iso_code","region","gpi_score",
            "gpi_income_poverty","gpi_wealth","gpi_wage",
            "gpi_labour_participation","gpi_financial_inclusion",
            "gpi_food_security","gpi_time_poverty","gpi_land_ownership",
            "gpi_social_protection",
            "income_poverty_ratio_f_to_m","wealth_ratio_f_to_m_pct",
            "wage_ratio_f_to_m_pct","labour_ratio_f_to_m_pct",
            "food_insecurity_gap_pct","unpaid_care_hours_ratio_f_to_m",
            "female_land_ownership_pct","year"]
    buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=flds,extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    with open(out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())

    print(f"Gender Poverty Index — {year}")
    print("="*60)
    print(f"  Countries: {len(rows)} | Global avg GPI: {avg}")
    print(f"\n  Top 5 (most equal):")
    for r in rows[:5]:
        print(f"    {r['rank']:>3}. {r['country']:<18} GPI: {r['gpi_score']:>5}")
    print(f"\n  Bottom 5 (most unequal):")
    for r in rows[-5:]:
        print(f"    {r['rank']:>3}. {r['country']:<18} GPI: {r['gpi_score']:>5}")
    print(f"\n  India breakdown:")
    india = next(r for r in rows if r["iso_code"]=="IND")
    for k in ["gpi_score","gpi_income_poverty","gpi_wealth","gpi_wage",
              "gpi_time_poverty","gpi_food_security","gpi_land_ownership"]:
        print(f"    {k:<35} {india[k]}")
    print(f"\n  Saved: {out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year",type=int,default=BASELINE_YEAR)
    p.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    args = parser.parse_args()
    generate(args.year)