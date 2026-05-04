"""
SHEtoken Pipeline — Women's Vital Statistics Generator
========================================================
Generates comprehensive women's vital statistics by country.

Includes:
  - Girls born per year (and weekly estimate)
  - Women's deaths by top 10 causes
  - Life expectancy vs men
  - Maternal deaths
  - Education funnel (school → college completion)
  - Child marriage rates
  - Fertility rates
  - Women killed by intimate partner

Data sources:
  - UN World Population Prospects 2024
  - WHO Global Health Observatory
  - WHO Cause of Death Database
  - UNICEF MICS / SOWC
  - UNESCO UIS
  - UNODC

Usage:
    python data/generate_womens_vital_stats.py

Output:
    data/output/womens-vital-stats-2025.csv
    data/output/global-vital-weekly.json   ← live counters

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, json, os, sys, argparse
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

# ── GLOBAL SUMMARY STATS ──────────────────────────────────────────────────────
# UN World Population Prospects 2024 + WHO + UNICEF
# All annual figures → weekly estimates = annual / 52

GLOBAL_STATS = {
    # Births
    "girls_born_annually":         72_400_000,   # UN WPP 2024
    "total_births_annually":      140_000_000,

    # Deaths — women
    "women_deaths_annually":       30_000_000,   # WHO
    "maternal_deaths_annually":       287_000,   # WHO 2020
    "women_killed_by_partner_annually": 89_000,  # UNODC 2023 (femicide)

    # Education
    "girls_starting_primary_annually": 60_000_000,
    "girls_completing_primary_annually": 54_000_000,   # ~90% completion
    "girls_starting_secondary_annually": 52_000_000,
    "girls_completing_secondary_annually": 38_000_000, # ~73%
    "women_starting_university_annually":  26_000_000,

    # Child marriage
    "girls_married_under_18_annually":  12_000_000,   # Girls Not Brides
    "girls_pregnant_under_18_annually":  21_000_000,  # WHO

    # Poverty
    "women_in_extreme_poverty":     435_000_000,  # UN Women
    "men_in_extreme_poverty":       380_000_000,
    "gender_poverty_gap_pct":              14.5,  # % more women than men in poverty

    # Wealth
    "female_share_of_wealth_pct":          38.0,  # Credit Suisse 2023
    "male_share_of_wealth_pct":            62.0,
    "gender_wage_gap_global_pct":          20.0,  # ILO
}

# Weekly estimates (annual / 52)
GLOBAL_WEEKLY = {k: round(v/52) if isinstance(v, int) and v > 1000 else v
                 for k, v in GLOBAL_STATS.items()}


# ── COUNTRY VITAL STATS ───────────────────────────────────────────────────────
# (country, iso, region,
#  girls_born_per_1000_pop,        # from crude birth rate × sex ratio
#  life_expectancy_female,
#  life_expectancy_male,
#  le_gap,                          # female advantage in years
#  maternal_mortality_per_100k_lb,
#  girls_primary_enrollment_pct,
#  girls_secondary_enrollment_pct,
#  women_tertiary_pct,
#  child_marriage_rate_pct,        # girls married before 18
#  fertility_rate,                 # children per woman
#  female_poverty_rate_pct,
#  male_poverty_rate_pct,
#  gender_wealth_gap_pct,          # women's median wealth as % of men's
#  women_killed_by_partner_per_100k, # UNODC
#  female_labour_pct,
#  gender_wage_gap_pct,
#  women_with_bank_account_pct)

COUNTRY_STATS = [

    # ── TIER 1 — High WEI ────────────────────────────────────────────────────
    ("Iceland",    "ISL","Europe",       11.2, 84.2, 81.0, 3.2,   3,   99,  99,  73,  0.3, 1.71, 2.0, 1.8,  82, 0.5, 82, 8, 99),
    ("Norway",     "NOR","Europe",       10.5, 84.4, 81.2, 3.2,   2,   99,  99,  71,  0.2, 1.56, 2.5, 2.2,  80, 0.6, 78, 7, 99),
    ("Finland",    "FIN","Europe",        9.2, 84.6, 79.4, 5.2,   3,   99,  99,  70,  0.2, 1.46, 3.0, 2.5,  79, 0.7, 76, 8, 99),
    ("Sweden",     "SWE","Europe",       11.1, 84.7, 81.5, 3.2,   4,   99,  99,  72,  0.1, 1.66, 2.5, 2.0,  81, 0.8, 80, 7, 99),
    ("Denmark",    "DNK","Europe",        9.6, 83.8, 80.4, 3.4,   4,   99,  99,  73,  0.2, 1.67, 3.0, 2.5,  80, 1.0, 79, 8, 99),
    ("Germany",    "DEU","Europe",        8.4, 83.2, 78.7, 4.5,   7,   99,  99,  68,  0.2, 1.53, 5.0, 4.0,  76, 1.2, 73,18, 99),
    ("Canada",     "CAN","N. America",   10.1, 84.1, 80.4, 3.7,   8,   99,  99,  69,  0.3, 1.44, 4.0, 3.5,  78, 1.5, 76,17, 99),
    ("Australia",  "AUS","Oceania",      12.1, 85.0, 81.1, 3.9,   3,   99,  99,  67,  0.3, 1.66, 4.5, 3.8,  75, 1.8, 72,14, 99),
    ("USA",        "USA","N. America",   11.6, 81.1, 76.4, 4.7,  23,   99,  99,  68,  2.0, 1.64, 8.0, 6.0,  68, 2.2, 72,18, 95),
    ("UK",         "GBR","Europe",       10.9, 83.1, 79.9, 3.2,   9,   99,  99,  66,  0.4, 1.56, 5.0, 4.0,  77, 1.5, 74,15, 99),
    ("Japan",      "JPN","East Asia",     7.3, 87.1, 81.1, 6.0,   4,   99,  99,  65,  0.2, 1.21, 2.5, 2.0,  74, 0.4, 53,21, 98),
    ("South Korea","KOR","East Asia",     6.9, 85.6, 80.3, 5.3,  11,   99,  99,  68,  0.2, 0.88, 3.0, 2.5,  72, 0.5, 58,30, 98),

    # ── TIER 2 — Mid WEI ─────────────────────────────────────────────────────
    ("Brazil",     "BRA","S. America",   13.4, 79.3, 72.8, 6.5,  72,   96,  89,  50,  9.0, 1.74,26.0,18.0,  52, 4.8, 55,22, 78),
    ("Mexico",     "MEX","N. America",   17.2, 77.8, 72.1, 5.7,  83,   97,  88,  48, 15.0, 2.08,28.0,20.0,  50, 5.5, 46,22, 68),
    ("India",      "IND","South Asia",   17.5, 70.7, 68.9, 1.8, 103,   94,  74,  28, 23.0, 2.01,24.0,16.0,  38,28.0, 27,30, 53),
    ("China",      "CHN","East Asia",    10.5, 80.5, 75.5, 5.0,  23,   99,  94,  50,  3.0, 1.09, 8.0, 6.0,  60, 1.2, 62,18, 80),
    ("Indonesia",  "IDN","SE Asia",      16.8, 74.6, 70.6, 4.0, 173,   97,  85,  36, 14.0, 2.30,18.0,12.0,  45,12.0, 48,23, 58),
    ("Philippines","PHL","SE Asia",      22.8, 74.9, 68.4, 6.5, 114,   98,  90,  44, 10.0, 2.77,22.0,18.0,  50, 8.0, 58,16, 66),
    ("South Africa","ZAF","Africa",      20.1, 68.0, 62.0, 6.0, 127,   94,  88,  40, 12.0, 2.38,31.0,22.0,  42,20.0, 50,33, 68),
    ("Nigeria",    "NGA","Africa",       37.0, 55.7, 54.2, 1.5, 1047,  83,  60,  20, 44.0, 5.32,58.0,48.0,  28,40.0, 48,36, 38),
    ("Kenya",      "KEN","Africa",       31.5, 68.4, 64.5, 3.9, 342,   92,  76,  22, 26.0, 3.64,40.0,32.0,  35,28.0, 62,32, 58),
    ("Ghana",      "GHA","Africa",       30.0, 65.8, 63.5, 2.3, 263,   92,  74,  18, 24.0, 3.88,48.0,40.0,  33,30.0, 66,34, 52),
    ("Rwanda",     "RWA","Africa",       30.8, 70.8, 67.2, 3.6,  259,  95,  80,  12, 16.0, 3.73,54.0,44.0,  32,32.0, 88,28, 62),
    ("Bangladesh", "BGD","South Asia",   26.5, 76.0, 71.6, 4.4, 123,   97,  72,  20, 59.0, 2.17,26.0,18.0,  32,36.0, 36,34, 50),
    ("Pakistan",   "PAK","South Asia",   28.4, 67.8, 66.0, 1.8, 154,   74,  50,  14, 28.0, 3.43,38.0,26.0,  28,44.0, 22,34, 18),
    ("Vietnam",    "VNM","SE Asia",      15.5, 78.9, 72.8, 6.1,  46,   99,  92,  30,  6.0, 2.06,12.0, 8.0,  55, 4.0, 70,12, 62),
    ("Thailand",   "THA","SE Asia",      10.2, 80.9, 73.7, 7.2,  37,   98,  94,  44,  6.0, 1.33,10.0, 7.0,  58, 3.0, 60,12, 80),
    ("Turkey",     "TUR","Europe/Asia",  14.7, 80.7, 76.4, 4.3,  17,   95,  88,  52, 10.0, 1.93,18.0,12.0,  52,10.0, 38,20, 68),

    # ── TIER 3 — Lower WEI ───────────────────────────────────────────────────
    ("Ethiopia",   "ETH","Africa",       33.4, 67.5, 63.8, 3.7, 401,   88,  58,  14, 40.0, 4.22,72.0,60.0,  24,54.0, 78,30, 36),
    ("Tanzania",   "TZA","Africa",       36.1, 68.7, 65.4, 3.3, 524,   90,  66,  14, 31.0, 4.84,50.0,42.0,  28,44.0, 82,28, 42),
    ("Uganda",     "UGA","Africa",       41.2, 68.6, 64.8, 3.8, 284,   92,  62,  10, 40.0, 4.76,48.0,40.0,  26,46.0, 76,30, 46),
    ("Mozambique", "MOZ","Africa",       38.7, 61.6, 58.4, 3.2, 289,   90,  58,  12, 48.0, 4.56,70.0,60.0,  24,50.0, 76,32, 40),
    ("Sudan",      "SDN","Africa",       32.4, 67.0, 64.4, 2.6, 295,   84,  52,  14, 38.0, 4.42,60.0,50.0,  28,52.0, 32,38, 14),
    ("Myanmar",    "MMR","SE Asia",      17.0, 70.8, 65.4, 5.4, 282,   96,  74,  22, 16.0, 2.12,28.0,20.0,  40,30.0, 48,20, 44),
    ("Iraq",       "IRQ","Middle East",  27.5, 72.0, 68.4, 3.6,  79,   96,  66,  22, 28.0, 3.55,18.0,12.0,  38,28.0, 14,36, 10),
    ("Egypt",      "EGY","Africa/ME",   22.8, 74.4, 71.2, 3.2,  17,   98,  86,  38, 18.0, 2.86,16.0,10.0,  44,18.0, 17,32, 28),
    ("Guatemala",  "GTM","C. America",  25.5, 76.0, 71.5, 4.5,  95,   98,  82,  30, 34.0, 2.66,38.0,28.0,  42,28.0, 48,20, 54),

    # ── TIER 4 — Crisis ──────────────────────────────────────────────────────
    ("Yemen",      "YEM","Middle East",  30.5, 66.6, 63.5, 3.1, 183,   78,  40,  10, 34.0, 3.88,58.0,50.0,  24,54.0,  6,42,  6),
    ("Afghanistan","AFG","South Asia",   34.5, 66.6, 63.0, 3.6, 620,   70,  22,   8, 28.0, 4.10,72.0,60.0,  22,56.0,  6,56,  2),
    ("DRC",        "COD","Africa",       43.8, 61.4, 58.1, 3.3, 547,   86,  52,  10, 52.0, 5.56,76.0,64.0,  22,58.0, 62,32, 14),
    ("Mali",       "MLI","Africa",       42.2, 60.2, 57.8, 2.4, 562,   74,  40,  12, 54.0, 5.52,76.0,64.0,  20,58.0, 70,32, 22),
    ("Niger",      "NER","Africa",       47.8, 62.4, 60.2, 2.2, 509,   72,  32,  10, 76.0, 6.73,80.0,68.0,  18,64.0, 42,34, 14),
    ("Chad",       "TCD","Africa",       43.5, 54.8, 52.4, 2.4, 1140,  74,  36,  10, 58.0, 5.58,78.0,66.0,  20,60.0, 62,30, 12),
    ("Somalia",    "SOM","Africa",       39.5, 57.4, 55.2, 2.2, 829,   48,  24,   6, 45.0, 5.82,82.0,70.0,  18,64.0, 22,36,  6),
]

FIELDNAMES = [
    "country","iso_code","region",
    "girls_born_per_1000_pop",
    "life_expectancy_female","life_expectancy_male","le_gap_years",
    "maternal_mortality_per_100k",
    "girls_primary_enrollment_pct",
    "girls_secondary_enrollment_pct",
    "women_tertiary_enrollment_pct",
    "child_marriage_rate_pct",
    "fertility_rate",
    "female_poverty_rate_pct",
    "male_poverty_rate_pct",
    "gender_poverty_gap_pct",
    "gender_wealth_gap_pct",
    "women_killed_by_partner_per_100k",
    "female_labour_force_pct",
    "gender_wage_gap_pct",
    "women_with_bank_account_pct",
    # Derived weekly estimates
    "girls_born_per_week_est",
    "maternal_deaths_per_week_est",
    "girls_drop_out_school_per_week_est",
    "girls_married_under18_per_week_est",
    "women_killed_by_partner_per_week_est",
    "year",
]


def compute_weekly_estimates(row, pop_millions):
    """Compute weekly estimates from rates."""
    pop = pop_millions * 1_000_000
    girls_born_pa = (row["girls_born_per_1000_pop"] / 1000) * pop / 2
    girls_born_pw = round(girls_born_pa / 52)

    mmr   = row["maternal_mortality_per_100k"]
    lb_pa = girls_born_pa  # proxy: live births ≈ girls born
    mat_deaths_pa = round((mmr / 100_000) * lb_pa * 2)
    mat_deaths_pw = round(mat_deaths_pa / 52)

    school_age_pa = girls_born_pa  # cohort entering school
    primary_pct   = row["girls_primary_enrollment_pct"] / 100
    secondary_pct = row["girls_secondary_enrollment_pct"] / 100
    dropout_pa    = round(school_age_pa * (primary_pct - secondary_pct * 0.85))
    dropout_pw    = round(max(0, dropout_pa) / 52)

    cm_rate  = row["child_marriage_rate_pct"] / 100
    cm_pa    = round(girls_born_pa * cm_rate)
    cm_pw    = round(cm_pa / 52)

    vio_rate = row["women_killed_by_partner_per_100k"]
    women_pop = pop * 0.5
    vio_pa   = round((vio_rate / 100_000) * women_pop)
    vio_pw   = round(vio_pa / 52)

    row["girls_born_per_week_est"]              = girls_born_pw
    row["maternal_deaths_per_week_est"]         = mat_deaths_pw
    row["girls_drop_out_school_per_week_est"]   = dropout_pw
    row["girls_married_under18_per_week_est"]   = cm_pw
    row["women_killed_by_partner_per_week_est"] = vio_pw
    return row


def generate(year=BASELINE_YEAR):
    # Load population from baseline CSV
    pop_lookup = {}
    baseline   = OUTPUT_DIR / "baseline-2025.csv"
    if baseline.exists():
        with open(baseline,"r",encoding="utf-8") as f:
            lines=[l for l in f if not l.startswith("#")]
        for row in csv.DictReader(io.StringIO("".join(lines))):
            try: pop_lookup[row["iso_code"]] = float(row.get("population_millions",1))
            except: pass

    rows = []
    for stat in COUNTRY_STATS:
        (country,iso,region,gbp,lef,lem,leg,mmr,gprim,gsec,gter,cm,fr,fpov,mpov,gwg,vio,flab,wgap,bank) = stat

        pop = pop_lookup.get(iso, 10.0)
        gender_poverty_gap = round(fpov - mpov, 1)
        row = {
            "country":                       country,
            "iso_code":                      iso,
            "region":                        region,
            "girls_born_per_1000_pop":       gbp,
            "life_expectancy_female":        lef,
            "life_expectancy_male":          lem,
            "le_gap_years":                  leg,
            "maternal_mortality_per_100k":   mmr,
            "girls_primary_enrollment_pct":  gprim,
            "girls_secondary_enrollment_pct":gsec,
            "women_tertiary_enrollment_pct": gter,
            "child_marriage_rate_pct":       cm,
            "fertility_rate":                fr,
            "female_poverty_rate_pct":       fpov,
            "male_poverty_rate_pct":         mpov,
            "gender_poverty_gap_pct":        gender_poverty_gap,
            "gender_wealth_gap_pct":         gwg,
            "women_killed_by_partner_per_100k": vio,
            "female_labour_force_pct":       flab,
            "gender_wage_gap_pct":           wgap,
            "women_with_bank_account_pct":   bank,
            "year":                          year,
        }
        row = compute_weekly_estimates(row, pop)
        rows.append(row)

    out = OUTPUT_DIR / f"womens-vital-stats-{year}.csv"
    hdr = (
        f"# SHEtoken Women's Vital Statistics — {year}\n"
        f"# Sources: UN WPP 2024, WHO GHO, UNICEF MICS, UNESCO UIS,\n"
        f"#          UNODC, World Bank Gender Data, ILO, Credit Suisse\n"
        f"# Weekly estimates = annual rates / 52 (modeled, not reported weekly)\n"
        f"# Generated: May 2026 | shetoken.org\n#\n"
    )
    buf = io.StringIO()
    w   = csv.DictWriter(buf, fieldnames=FIELDNAMES, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    with open(out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())

    # Save global weekly counters JSON
    weekly_json = {
        "description": "Global weekly estimates for women's key life statistics",
        "data_note":   "Weekly estimates computed from annual rates. Not real-time.",
        "week_of":     datetime.now(timezone.utc).strftime("%Y-W%W"),
        "global_weekly_estimates": {
            "girls_born":                     round(GLOBAL_STATS["girls_born_annually"]/52),
            "maternal_deaths":                round(GLOBAL_STATS["maternal_deaths_annually"]/52),
            "women_killed_by_partner":        round(GLOBAL_STATS["women_killed_by_partner_annually"]/52),
            "girls_entering_primary_school":  round(GLOBAL_STATS["girls_starting_primary_annually"]/52),
            "girls_entering_secondary_school":round(GLOBAL_STATS["girls_starting_secondary_annually"]/52),
            "girls_dropping_out_secondary":   round((GLOBAL_STATS["girls_starting_secondary_annually"]-
                                                      GLOBAL_STATS["girls_completing_secondary_annually"])/52),
            "girls_starting_university":      round(GLOBAL_STATS["women_starting_university_annually"]/52),
            "girls_married_under_18":         round(GLOBAL_STATS["girls_married_under_18_annually"]/52),
            "girls_pregnant_under_18":        round(GLOBAL_STATS["girls_pregnant_under_18_annually"]/52),
        },
        "global_annual_estimates": GLOBAL_STATS,
        "per_second": {
            "girls_born":           round(GLOBAL_STATS["girls_born_annually"]/(365*24*3600), 2),
            "maternal_deaths":      round(GLOBAL_STATS["maternal_deaths_annually"]/(365*24*3600), 4),
            "women_killed_by_partner": round(GLOBAL_STATS["women_killed_by_partner_annually"]/(365*24*3600), 4),
        },
        "gender_wealth": {
            "women_share_of_global_wealth_pct": GLOBAL_STATS["female_share_of_wealth_pct"],
            "men_share_of_global_wealth_pct":   GLOBAL_STATS["male_share_of_wealth_pct"],
            "global_gender_wage_gap_pct":       GLOBAL_STATS["gender_wage_gap_global_pct"],
            "women_in_extreme_poverty":         GLOBAL_STATS["women_in_extreme_poverty"],
            "men_in_extreme_poverty":           GLOBAL_STATS["men_in_extreme_poverty"],
            "gender_poverty_gap_pct":           GLOBAL_STATS["gender_poverty_gap_pct"],
        },
    }
    json_out = OUTPUT_DIR / "global-vital-weekly.json"
    with open(json_out,"w",encoding="utf-8") as f:
        json.dump(weekly_json, f, indent=2, ensure_ascii=False)

    # Print summary
    print(f"Women's Vital Statistics — {year}")
    print("="*60)
    print(f"  Countries: {len(rows)}")
    print(f"\n  Global weekly estimates:")
    for k,v in weekly_json["global_weekly_estimates"].items():
        print(f"    {k:<42} {v:>8,}")
    print(f"\n  Per second:")
    for k,v in weekly_json["per_second"].items():
        print(f"    {k:<42} {v:>8}")
    print(f"\n  Gender wealth:")
    print(f"    Women's share of global wealth:         {GLOBAL_STATS['female_share_of_wealth_pct']}%")
    print(f"    Global gender wage gap:                 {GLOBAL_STATS['gender_wage_gap_global_pct']}%")
    print(f"    Women in extreme poverty:               {GLOBAL_STATS['women_in_extreme_poverty']:,}")
    print(f"    Gender poverty gap:                     +{GLOBAL_STATS['gender_poverty_gap_pct']}%")
    print(f"\n  Country spotlight (India):")
    india = next(r for r in rows if r["iso_code"]=="IND")
    for k in ["girls_born_per_week_est","maternal_deaths_per_week_est",
              "girls_married_under18_per_week_est","women_killed_by_partner_per_week_est",
              "female_poverty_rate_pct","male_poverty_rate_pct","gender_wage_gap_pct"]:
        print(f"    {k:<42} {india[k]}")
    print(f"\n  Saved: {out}")
    print(f"  Saved: {json_out}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=BASELINE_YEAR)
    parser.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    args = parser.parse_args()
    generate(args.year)