"""
SHEtoken — Girls School Dropout Causes Generator
=================================================
Tracks 8 specific reasons girls drop out of school by country.
Each cause has a different policy intervention.

The 8 causes:
  1. Period poverty / menstrual health        → WASH in schools
  2. Child marriage / family pressure         → Legal + cash transfer
  3. Safety on route to school               → Infrastructure + police
  4. No female teachers                      → Teacher training
  5. Cost (fees, uniform, materials)         → Conditional cash transfer
  6. Domestic labour / care burden           → Social protection
  7. Early pregnancy                         → Sex education + healthcare
  8. School quality / no secondary nearby    → Infrastructure

Sources:
  UNICEF MICS, UNESCO UIS, World Bank, Plan International,
  UNGEI (UN Girls Education Initiative), Girls Not Brides

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

# country, iso,
# dropout_rate_secondary_pct,   % girls who don't complete secondary
# cause_period_poverty_pct,     % of dropouts where menstruation is a reason
# cause_child_marriage_pct,
# cause_safety_pct,             unsafe route to school
# cause_no_female_teacher_pct,
# cause_cost_pct,               fees, uniform, materials
# cause_domestic_labour_pct,
# cause_early_pregnancy_pct,
# cause_no_school_nearby_pct,
# period_products_access_pct,   % of girls who have access to sanitary products
# school_has_toilet_pct,        % of schools with separate female toilet
# school_has_changing_room_pct, % of schools with changing/washing facility
# missing_days_period_per_year, average days missed due to menstruation
# menstrual_stigma_score,       0-10 (10=extreme stigma)
# proven_intervention,          program that works in this country

DROPOUT_DATA = [
    # ── HIGH INCOME — nearly no dropout ──────────────────────────────────────
    ("Iceland",      "ISL",  1, 0, 0, 0, 0, 0, 0, 0,  1, 100, 100, 99, 0, 0, "Universal secondary education"),
    ("Norway",       "NOR",  1, 0, 0, 0, 0, 0, 0, 0,  1, 100, 100, 99, 0, 0, "Universal secondary education"),
    ("Germany",      "DEU",  2, 0, 0, 0, 0, 1, 0, 1,  1, 100, 100, 99, 0, 1, "Dual education system"),
    ("USA",          "USA",  3, 1, 0, 1, 0, 0, 0, 1,  1, 100,  98, 98, 1, 1, "Title IX protections"),
    ("UK",           "GBR",  3, 1, 0, 0, 0, 0, 0, 1,  1, 100,  98, 97, 2, 1, "Period Products Act (Scotland 2021)"),
    ("Japan",        "JPN",  2, 0, 0, 0, 0, 1, 0, 1,  1, 100,  99, 99, 1, 2, "Universal enrollment"),

    # ── MID INCOME — significant but improving ────────────────────────────────
    ("Brazil",       "BRA", 27, 6, 8, 8, 2, 12, 14, 22, 18,  72,  68, 44, 4, 4, "Bolsa Familia conditional cash transfer"),
    ("Mexico",       "MEX", 22, 8, 12, 10, 3, 14, 12, 18, 13,  68,  62, 40, 5, 4, "PROSPERA scholarship program"),
    ("India",        "IND", 26, 23, 18, 10, 8, 14, 12, 8,  5,  38,  52, 22,18, 6, "Kanyashree / Kishori Shakti Yojana"),
    ("Indonesia",    "IDN", 20, 12, 14, 8, 4, 18, 14, 12, 8,  52,  64, 38, 8, 5, "Program Indonesia Pintar"),
    ("Philippines",  "PHL", 14, 8, 6, 8, 2, 16, 10, 14, 6,  68,  74, 52, 6, 3, "4Ps conditional cash transfer"),
    ("South Africa", "ZAF", 18, 10, 4, 12, 2, 12, 8, 18, 8,  62,  72, 48, 6, 4, "National school nutrition + menstrual products"),
    ("Nigeria",      "NGA", 46, 28, 22, 14, 18, 16, 18, 12, 12,  24,  38, 18,22, 7, "UNICEF MENISCUS program"),
    ("Kenya",        "KEN", 34, 32, 18, 12, 6, 14, 16, 14, 8,  34,  46, 24,24, 7, "Sanitary towels program (Kenya)"),
    ("Bangladesh",   "BGD", 28, 18, 38, 8, 4, 18, 14, 8,  8,  48,  58, 32,14, 5, "BRAC girls education + stipend"),
    ("Ethiopia",     "ETH", 52, 22, 32, 16, 22, 16, 24, 10, 14,  18,  32, 12,28, 8, "Afar women's education initiative"),
    ("Pakistan",     "PAK", 54, 18, 28, 22, 28, 16, 18, 8,  12,  22,  36, 14,22, 8, "BISP conditional cash / Ehsaas"),
    ("Tanzania",     "TZA", 42, 30, 24, 12, 8, 14, 22, 14, 12,  22,  38, 16,26, 8, "MKUKUTA girls retention program"),
    ("Uganda",       "UGA", 48, 34, 28, 14, 10, 16, 24, 16, 10,  20,  34, 14,28, 8, "PIASCY / MHM in schools"),
    ("Ghana",        "GHA", 36, 26, 18, 10, 8, 14, 20, 14, 10,  28,  44, 20,20, 7, "School for Life / capitation grant"),
    ("Rwanda",       "RWA", 22, 18, 14, 8, 4, 12, 16, 12, 8,  52,  62, 36,14, 5, "Agaseke gender program"),
    ("Vietnam",      "VNM", 14, 8, 8, 6, 2, 10, 12, 8,  6,  62,  74, 52, 6, 3, "MOET school quality program"),
    ("Afghanistan",  "AFG", 78, 16, 24, 26, 38, 18, 22, 4, 18,  12,  18,  6,24, 9, "Taliban ban — no effective program available"),
    ("Yemen",        "YEM", 60, 18, 28, 22, 32, 16, 20, 6, 14,  16,  22,  8,22, 8, "UNICEF education in emergencies"),
    ("Niger",        "NER", 74, 24, 46, 14, 20, 16, 20, 6, 12,  12,  18,  6,28, 9, "Nigerienne Breakfast program (limited)"),
    ("Mali",         "MLI", 72, 24, 42, 14, 20, 16, 18, 6, 12,  12,  18,  6,28, 9, "USAID girls education — limited reach"),
]

FIELDNAMES = [
    "country","iso_code",
    "dropout_rate_secondary_pct",
    "cause_period_poverty_pct",
    "cause_child_marriage_pct",
    "cause_safety_pct",
    "cause_no_female_teacher_pct",
    "cause_cost_pct",
    "cause_domestic_labour_pct",
    "cause_early_pregnancy_pct",
    "cause_no_school_nearby_pct",
    "period_products_access_pct",
    "school_has_toilet_pct",
    "school_has_changing_room_pct",
    "missing_days_period_per_year",
    "menstrual_stigma_score",
    "proven_intervention",
    # Computed
    "top_cause",
    "top_cause_pct",
    "period_poverty_composite",
    "year",
]


def compute_top_cause(row: dict) -> tuple:
    causes = {
        "period_poverty":   row["cause_period_poverty_pct"],
        "child_marriage":   row["cause_child_marriage_pct"],
        "safety":           row["cause_safety_pct"],
        "no_female_teacher":row["cause_no_female_teacher_pct"],
        "cost":             row["cause_cost_pct"],
        "domestic_labour":  row["cause_domestic_labour_pct"],
        "early_pregnancy":  row["cause_early_pregnancy_pct"],
        "no_school_nearby": row["cause_no_school_nearby_pct"],
    }
    top = max(causes, key=causes.get)
    return top, causes[top]


def period_poverty_composite(row: dict) -> float:
    """Composite period poverty score for school impact (0-100, higher=worse)."""
    # Higher missing days, lower access, higher stigma = worse
    missing = min(row["missing_days_period_per_year"] / 30 * 100, 100)
    access  = 100 - row["period_products_access_pct"]
    toilet  = 100 - row["school_has_toilet_pct"]
    stigma  = row["menstrual_stigma_score"] * 10
    return round((missing * 0.35 + access * 0.30 + toilet * 0.20 + stigma * 0.15), 1)


def generate(year=BASELINE_YEAR):
    rows = []
    for stat in DROPOUT_DATA:
        (country, iso, dropout, pp, cm, safe, ft, cost, dl, ep, ns,
         ppa, sht, shc, miss, stig, interv) = stat
        row = {
            "country": country, "iso_code": iso,
            "dropout_rate_secondary_pct": dropout,
            "cause_period_poverty_pct": pp,
            "cause_child_marriage_pct": cm,
            "cause_safety_pct": safe,
            "cause_no_female_teacher_pct": ft,
            "cause_cost_pct": cost,
            "cause_domestic_labour_pct": dl,
            "cause_early_pregnancy_pct": ep,
            "cause_no_school_nearby_pct": ns,
            "period_products_access_pct": ppa,
            "school_has_toilet_pct": sht,
            "school_has_changing_room_pct": shc,
            "missing_days_period_per_year": miss,
            "menstrual_stigma_score": stig,
            "proven_intervention": interv,
            "year": year,
        }
        top_cause, top_pct = compute_top_cause(row)
        row["top_cause"]              = top_cause
        row["top_cause_pct"]          = top_pct
        row["period_poverty_composite"] = period_poverty_composite(row)
        rows.append(row)

    rows.sort(key=lambda x: x["dropout_rate_secondary_pct"], reverse=True)

    out = OUTPUT_DIR / f"school-dropout-causes-{year}.csv"
    hdr = (
        f"# SHEtoken Girls School Dropout Causes — {year}\n"
        f"# 8 specific causes tracked per country with proven interventions\n"
        f"# Sources: UNICEF MICS, UNESCO UIS, Plan International, UNGEI\n"
        f"# Period poverty composite: missing days (35%) + access (30%) + facilities (20%) + stigma (15%)\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=FIELDNAMES, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    with open(out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())

    # Print analysis
    print(f"Girls School Dropout Causes — {year}")
    print("="*65)
    print(f"\n  {'Country':<16} {'Dropout':>7} {'Top Cause':<20} {'Period Poverty':>14}")
    print(f"  {'─'*60}")
    for r in rows:
        print(f"  {r['country']:<16} {r['dropout_rate_secondary_pct']:>6}%  "
              f"{r['top_cause']:<20} {r['period_poverty_composite']:>12.1f}/100")

    # Period poverty breakdown for India
    print(f"\n  India period poverty detail:")
    india = next(r for r in rows if r["iso_code"]=="IND")
    print(f"    % girls citing period as dropout reason:    {india['cause_period_poverty_pct']}%")
    print(f"    Schools with female toilet:                 {india['school_has_toilet_pct']}%")
    print(f"    Schools with changing room:                 {india['school_has_changing_room_pct']}%")
    print(f"    Days missed per girl per year (period):     {india['missing_days_period_per_year']}")
    print(f"    Menstrual stigma score (0-10):              {india['menstrual_stigma_score']}")
    print(f"    Period poverty composite score:             {india['period_poverty_composite']}/100 (higher=worse)")
    print(f"    Access to period products:                  {india['period_products_access_pct']}%")
    print(f"\n  Proven intervention: {india['proven_intervention']}")
    print(f"\n  Saved: {out}")
    return rows


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=BASELINE_YEAR)
    parser.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    generate(p.parse_args().year)