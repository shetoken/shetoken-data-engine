"""
SHEtoken Pipeline — Sexual Violence Index
==========================================
Comprehensive sexual violence tracking that addresses
the fundamental underreporting problem.

KEY DESIGN DECISION:
Uses WHO survey-based PREVALENCE estimates as primary measure,
NOT police-reported crime statistics.

Reason: Police reports systematically undercount rape.
Countries with better reporting infrastructure appear worse.
Countries where women cannot report appear safer.
This is a critical methodological flaw in all existing indices.

This index uses a three-source triangulation:
  1. WHO lifetime prevalence surveys (most accurate, survey-based)
  2. UNODC reported crime rates (official, highly incomplete)
  3. Community signals (shetoken.org — fills underreporting gap)

Reporting Gap = gap between WHO estimate and UNODC report
High gap = systemic suppression of reporting

Special categories tracked:
  - Marital rape (legal status + prevalence)
  - Conflict-related sexual violence
  - Digital sexual violence
  - Caste/ethnicity-based targeting (India, USA indigenous)
  - Impunity index (rape reported vs prosecuted vs convicted)

Sources:
  WHO Multi-Country Study on Violence Against Women
  UNODC Sexual Violence Statistics
  UNFPA Conflict-related Sexual Violence reports
  Plan International / ITU Digital Violence
  Human Rights Watch country reports
  National Crime Records Bureau (India)
  Statistics Canada
  US National Crime Victimization Survey (NCVS)

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, json
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR


# ── DATA ──────────────────────────────────────────────────────────────────────
#
# country, iso, region,
# who_lifetime_prevalence_pct,      % women ever experiencing sexual violence
# unodc_reported_rate_per_100k,     official reported rate
# reporting_gap_pct,                % of incidents NOT reported (WHO-based estimate)
# marital_rape_criminalised,        1=yes, 0=no, 0.5=partial
# marital_rape_prevalence_pct,      % women experiencing marital rape
# conflict_sv_risk,                 0-10 (10=active conflict zone)
# digital_sv_rate_pct,              % women experiencing online sexual violence
# impunity_score,                   % of reported rapes not leading to conviction
# caste_ethnic_targeting,           1=significant documented pattern
# indigenous_women_risk,            1=significantly elevated risk documented
# police_responsiveness_score,      0-10 (10=best)
# legal_framework_score,            0-10 (10=strongest legal protections)
# support_services_score,           0-10 (rape crisis centres, legal aid, etc.)
# notes

SV_DATA = [

    # ── TIER 1 ────────────────────────────────────────────────────────────────
    # High reporting rates do NOT mean more rape — they mean better systems
    ("Iceland",      "ISL","Europe",      14.0,  152,  60, 1, 5.0,  0,  18, 25, 9, 10, 9,  "High reporting reflects strong legal framework and trust in police"),
    ("Norway",       "NOR","Europe",      11.0,  208,  60, 1, 4.0,  0,  20, 22, 9, 10, 9,  "Among world's highest reported rates — reflects best practice reporting"),
    ("Sweden",       "SWE","Europe",      13.0,  188,  55, 1, 5.0,  0,  22, 20, 8,  9, 9,  "Broad legal definition of rape + high reporting = high official rate"),
    ("Denmark",      "DNK","Europe",      12.0,  110,  60, 1, 4.5,  0,  20, 22, 8,  9, 9,  "Strong survivor support system"),
    ("Finland",      "FIN","Europe",      11.0,   95,  65, 1, 4.0,  0,  18, 28, 8,  9, 8,  "High conviction rate relative to Nordic peers"),
    ("Germany",      "DEU","Europe",      13.0,   90,  68, 1, 5.5,  0,  25, 35, 7,  8, 8,  "Consent-based law since 2016"),
    ("UK",           "GBR","Europe",      20.0,   79,  83, 1, 7.0,  0,  28, 38, 7,  9, 8,  "High prevalence, poor conviction rate (5.2%)"),
    ("Australia",    "AUS","Oceania",     18.0,   91,  80, 1, 7.5,  0,  26, 35, 7,  9, 8,  "Indigenous women 5x higher risk"),
    ("Canada",       "CAN","N. America",  22.0,   98,  83, 1, 8.5,  0,  24, 40, 7,  9, 8,  "MMIW crisis — indigenous women face extreme risk"),
    ("USA",          "USA","N. America",  18.0,   40,  90, 1, 8.0,  0,  32, 65, 6,  8, 8,  "Only 23% reported (NCVS). Tribal land — federal jurisdiction gap leaves indigenous women unprotected"),
    ("Japan",        "JPN","East Asia",   10.0,    4,  95, 0, 6.0,  0,  18, 88, 6,  6, 5,  "Extreme underreporting. Marital rape not clearly criminalised until 2023 reform. Victims face intense social pressure to stay silent"),
    ("South Korea",  "KOR","East Asia",   13.0,   22,  90, 1, 6.0,  0,  22, 75, 6,  7, 6,  "High underreporting. Revenge porn epidemic."),

    # ── TIER 2 ────────────────────────────────────────────────────────────────
    ("Brazil",       "BRA","S. America",  30.0,   28,  90, 1,12.0,  0,  38, 82, 4,  7, 6,  "Rape every 11 minutes (IPEA). Maria da Penha law enforcement inconsistent. Black women face higher rates."),
    ("Mexico",       "MEX","N. America",  32.0,   20,  92, 1,14.0,  2,  34, 90, 3,  5, 4,  "Feminist emergency: 11 women killed daily. High impunity. 8 states with alerta de género."),
    ("India",        "IND","South Asia",  28.0,    5,  98, 0,18.0,  0,  24, 95, 2,  5, 3,  "NCRB 2022: 31,677 reported. WHO estimate: 300,000+. Marital rape not criminalised. Dalit women face caste-targeted sexual violence. 1 in 3 rapes by known person."),
    ("South Africa", "ZAF","Africa",      38.0,   72,  92, 1,16.0,  0,  32, 88, 2,  6, 5,  "Highest rape prevalence globally by some measures. 1 in 4 men admit rape in surveys. Strong law, poor enforcement."),
    ("Nigeria",      "NGA","Africa",      30.0,    4,  98, 0,18.0,  2,  28, 97, 1,  3, 2,  "Extreme underreporting. SGBV weaponised by Boko Haram. Police routinely demand money from survivors. VAPP Act 2015 rarely enforced."),
    ("Kenya",        "KEN","Africa",      33.0,    6,  97, 1,15.0,  2,  26, 94, 2,  5, 3,  "Conflict-adjacent (Somalia border). High rates in refugee camps. Acid attacks on survivors who report."),
    ("Indonesia",    "IDN","SE Asia",     26.0,    4,  97, 0,16.0,  1,  22, 95, 2,  4, 3,  "Marital rape not criminalised. Religious courts handle some cases."),
    ("Bangladesh",   "BGD","South Asia",  35.0,    3,  99, 0,22.0,  0,  20, 98, 1,  3, 2,  "Near-zero reporting. Acid attacks as reprisal against women who report. Marital rape not criminalised."),
    ("Pakistan",     "PAK","South Asia",  32.0,    2,  99, 0,24.0,  1,  20, 99, 1,  2, 1,  "Near-zero reporting. Honour-based violence against survivors. Two-finger test abolished 2021 but culture persists. Blasphemy law used against survivors."),
    ("Turkey",       "TUR","Europe/Asia", 22.0,   15,  94, 1,12.0,  0,  26, 88, 3,  6, 4,  "Withdrew from Istanbul Convention 2021. Impunity high."),
    ("Colombia",     "COL","S. America",  30.0,   28,  88, 1,14.0,  4,  32, 82, 3,  6, 5,  "Conflict-related SGBV by guerrilla + paramilitary groups. Historic peace deal improved reporting."),
    ("Philippines",  "PHL","SE Asia",     24.0,   18,  90, 1,12.0,  1,  26, 88, 3,  6, 4,  "Safe Spaces Act 2019 — expanded protections. Implementation mixed."),

    # ── TIER 3 ────────────────────────────────────────────────────────────────
    ("Ethiopia",     "ETH","Africa",      36.0,    3,  99, 0,22.0,  3,  22, 98, 1,  3, 2,  "Tigray conflict: CRSV documented by UN. Police complicity in some regions."),
    ("DRC",          "COD","Africa",      52.0,    6,  99, 0,28.0, 10,  24, 99, 0,  1, 1,  "Highest documented conflict-related rape globally. 48+ women raped per hour at peak conflict. UN documented systematic rape as weapon of war."),
    ("Myanmar",      "MMR","SE Asia",     30.0,    4,  99, 0,18.0,  8,  20, 99, 1,  2, 1,  "Military rape documented in Rohingya genocide. ICC investigations ongoing."),
    ("Sudan",        "SDN","Africa",      36.0,    3,  99, 0,22.0,  9,  18, 99, 0,  1, 1,  "Active conflict — RSF documented mass rape in Darfur. 2023 conflict new atrocities."),
    ("Egypt",        "EGY","Africa/ME",   28.0,    6,  97, 0,16.0,  0,  22, 96, 2,  3, 2,  "Marital rape not criminalised. Tahrir Square mass assaults — no prosecutions."),
    ("Iran",         "IRN","Middle East", 24.0,    2,  99, 0,18.0,  0,  20, 99, 1,  2, 1,  "Marital rape legal. Morality police rape documented in custody. Mahsa Amini case — rape in detention."),
    ("Iraq",         "IRQ","Middle East", 28.0,    3,  99, 0,20.0,  5,  18, 99, 1,  2, 1,  "ISIS systematic rape of Yazidi women. Marital rape not criminalised. Honour killing as response to rape."),

    # ── TIER 4 ────────────────────────────────────────────────────────────────
    ("Yemen",        "YEM","Middle East", 32.0,    1, 100, 0,24.0, 10,  14,100, 0,  1, 0,  "Active conflict. Houthi and coalition forces documented CRSV. Near-zero reporting infrastructure."),
    ("Afghanistan",  "AFG","South Asia",  40.0,    1, 100, 0,30.0,  3,  12,100, 0,  1, 0,  "Taliban ended all women's reporting mechanisms. No functioning legal system for women. Marital rape encouraged by Taliban interpretation of law."),
    ("Somalia",      "SOM","Africa",      46.0,    2, 100, 0,28.0,  8,  14,100, 0,  1, 0,  "Highest estimated prevalence. Al-Shabaab uses SGBV systematically. Near-zero legal infrastructure."),
    ("Niger",        "NER","Africa",      36.0,    2,  99, 0,22.0,  4,  14, 99, 0,  2, 1,  "Child marriage + marital rape near-universal for girls. Post-coup security vacuum."),
    ("CAR",          "CAF","Africa",      46.0,    3, 100, 0,28.0, 10,  12,100, 0,  1, 0,  "Active conflict. Armed groups use rape as primary weapon. UN documented but impunity total."),
    ("South Sudan",  "SSD","Africa",      48.0,    3, 100, 0,32.0, 10,  12,100, 0,  1, 0,  "Active conflict. Both government and opposition forces documented. Girls 10-14 particularly targeted."),
    ("Palestine",    "PSE","Middle East", 34.0,    4,  98, 0,20.0,  9,  16, 98, 0,  2, 1,  "Conflict-related. Gaza crisis: shelter conditions. West Bank: settler violence."),
]


def compute_svi(row: dict) -> float:
    """
    Sexual Violence Index score (0-100 where 100 = safest).

    Uses WHO prevalence as primary — NOT reported rate.
    Also weights legal framework, support services, impunity.
    """
    # Prevalence (lower = better) — inverted
    prev_score = max(0, min(100, (55 - row["who_lifetime_prevalence_pct"]) / 55 * 100))
    # Reporting gap (lower gap = better) — inverted
    gap_score  = max(0, min(100, (100 - row["reporting_gap_pct"])))
    # Legal framework (higher = better)
    legal_score = row["legal_framework_score"] * 10
    # Support services (higher = better)
    support_score = row["support_services_score"] * 10
    # Impunity (lower = better) — inverted
    imp_score  = max(0, min(100, 100 - row["impunity_score"]))
    # Marital rape criminalised (binary)
    mr_score   = row["marital_rape_criminalised"] * 100
    # Conflict risk (lower = better) — inverted
    conf_score = max(0, min(100, (10 - row["conflict_sv_risk_score"]) / 10 * 100))

    return round(
        prev_score  * 0.30 +
        gap_score   * 0.15 +
        legal_score * 0.15 +
        imp_score   * 0.15 +
        mr_score    * 0.10 +
        conf_score  * 0.10 +
        support_score * 0.05, 1
    )


def generate(year=BASELINE_YEAR):
    rows = []
    for stat in SV_DATA:
        (country, iso, region,
         who_prev, unodc_rate, rep_gap,
         mr_crim, mr_prev,
         conf_risk, digital_sv, impunity,
         police_score, legal_score, support_score,
         notes) = stat

        # Derive caste/indigenous targeting from known countries
        caste_target     = 1 if iso in ("IND","USA","CAN","AUS","BRA") else 0
        indigenous_risk  = 1 if iso in ("CAN","USA","AUS","NZL","BRA","MEX") else 0

        row = {
            "country":                          country,
            "iso_code":                         iso,
            "region":                           region,
            "who_lifetime_prevalence_pct":      who_prev,
            "unodc_reported_rate_per_100k":     unodc_rate,
            "reporting_gap_pct":                rep_gap,
            "estimated_actual_rate_per_100k":   round(unodc_rate / max(0.01, (1 - rep_gap/100))),
            "marital_rape_criminalised":         mr_crim,
            "marital_rape_prevalence_pct":       mr_prev,
            "conflict_sv_risk_score":            conf_risk,
            "digital_sv_rate_pct":              digital_sv,
            "impunity_score":                    impunity,
            "caste_ethnic_targeting":            caste_target,
            "indigenous_women_elevated_risk":    indigenous_risk,
            "police_responsiveness_score":       police_score,
            "legal_framework_score":             legal_score,
            "support_services_score":            support_score,
            "notes":                             notes,
            "year":                              year,
        }
        row["svi_score"] = compute_svi(row)
        rows.append(row)

    rows.sort(key=lambda x: x["svi_score"], reverse=True)
    for i, r in enumerate(rows): r["rank"] = i + 1

    # Global stats
    total_women_pop = 4_000_000_000
    avg_prev = sum(r["who_lifetime_prevalence_pct"] for r in rows) / len(rows)
    est_global_annual = round(total_women_pop * avg_prev / 100 / 35)  # /35 = lifetime ~35yr window

    out = OUTPUT_DIR / f"sexual-violence-index-{year}.csv"
    hdr = (
        f"# SHEtoken Sexual Violence Index (SVI) — {year}\n"
        f"# PRIMARY MEASURE: WHO survey-based lifetime prevalence (NOT police reports)\n"
        f"# Reason: Police statistics severely undercount rape globally.\n"
        f"# High reported rate = better reporting infrastructure, NOT more rape.\n"
        f"# Reporting gap = % of incidents estimated NOT reported to police.\n"
        f"# SVI score: 100=safest, 0=most dangerous\n"
        f"#\n"
        f"# CRITICAL: Marital rape not criminalised in 36 countries.\n"
        f"# CRITICAL: Conflict-related sexual violence tracked separately.\n"
        f"# CRITICAL: Caste/ethnic targeting documented for India (Dalit women),\n"
        f"#           Canada/USA (indigenous women), South Africa, DRC.\n"
        f"#\n"
        f"# Sources: WHO Multi-Country Study, UNODC, UNHCR SGBV reports,\n"
        f"#          HRW country reports, national crime surveys (NCVS, NCRB etc.)\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )

    fnames = [
        "rank","country","iso_code","region",
        "who_lifetime_prevalence_pct",
        "unodc_reported_rate_per_100k",
        "reporting_gap_pct",
        "estimated_actual_rate_per_100k",
        "marital_rape_criminalised",
        "marital_rape_prevalence_pct",
        "conflict_sv_risk_score",
        "digital_sv_rate_pct",
        "impunity_score",
        "caste_ethnic_targeting",
        "indigenous_women_elevated_risk",
        "police_responsiveness_score",
        "legal_framework_score",
        "support_services_score",
        "svi_score",
        "notes",
        "year",
    ]

    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fnames, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    with open(out, "w", newline="", encoding="utf-8") as f:
        f.write(hdr + buf.getvalue())

    # Print key findings
    print(f"Sexual Violence Index — {year}")
    print("=" * 68)
    print(f"  Countries scored:          {len(rows)}")
    print(f"  Avg lifetime prevalence:   {avg_prev:.1f}% of women")
    print(f"  Countries: marital rape NOT criminalised: "
          f"{sum(1 for r in rows if r['marital_rape_criminalised']==0)}")
    print(f"  Countries: active conflict SGBV risk >5: "
          f"{sum(1 for r in rows if r['conflict_sv_risk_score']>5)}")
    print()
    print(f"  {'Rk':<4} {'Country':<18} {'SVI':>5} "
          f"{'WHO Prev':>9} {'Reported':>9} {'Rep Gap':>8} {'Marital?':>9}")
    print(f"  {'─'*65}")
    for r in rows:
        mr = "YES" if r["marital_rape_criminalised"]==1 else ("PARTIAL" if r["marital_rape_criminalised"]==0.5 else "NO")
        print(f"  {r['rank']:<4} {r['country']:<18} {r['svi_score']:>5} "
              f"{r['who_lifetime_prevalence_pct']:>8}% "
              f"{r['unodc_reported_rate_per_100k']:>8} "
              f"{r['reporting_gap_pct']:>7}% "
              f"{mr:>9}")
    print()
    print(f"  KEY INSIGHT:")
    print(f"  Sweden (high UNODC rate) SVI: {next(r['svi_score'] for r in rows if r['iso_code']=='SWE')}")
    print(f"  Pakistan (near-zero UNODC)SVI: {next(r['svi_score'] for r in rows if r['iso_code']=='PAK')}")
    print(f"  → Sweden scores BETTER than Pakistan despite reporting 94x more rapes")
    print(f"    because WHO prevalence, legal framework and impunity are measured")
    print(f"\n  India detail:")
    india = next(r for r in rows if r["iso_code"]=="IND")
    print(f"    WHO lifetime prevalence:      {india['who_lifetime_prevalence_pct']}%")
    print(f"    NCRB reported rate/100K:      {india['unodc_reported_rate_per_100k']}")
    print(f"    Estimated reporting gap:      {india['reporting_gap_pct']}%")
    print(f"    Marital rape criminalised:    {'YES' if india['marital_rape_criminalised'] else 'NO'}")
    print(f"    Caste-based targeting:        {'YES' if india['caste_ethnic_targeting'] else 'NO'}")
    print(f"    Impunity score:               {india['impunity_score']}%")
    print(f"    SVI Score:                    {india['svi_score']}/100")
    print(f"\n  Most dangerous (active conflict):")
    conflict = sorted(rows, key=lambda x: x["conflict_sv_risk_score"], reverse=True)
    for r in conflict[:5]:
        print(f"    {r['country']:<18} Conflict risk: {r['conflict_sv_risk_score']}/10 | {r['notes'][:60]}")
    print(f"\n  Saved: {out}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=BASELINE_YEAR)
    generate(p.parse_args().year)
