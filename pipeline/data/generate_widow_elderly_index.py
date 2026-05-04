"""
SHEtoken — Widow & Elderly Women Vulnerability Index
======================================================
Tracks the situation of widows and elderly women globally,
with deep focus on India where the crisis is most visible
and most undercounted.

India-specific crisis:
  - 40+ million widows (UNFPA)
  - Widow abandonment at temple towns (Vrindavan, Varanasi,
    Haridwar, Mathura, Tirupati)
  - Property stripping by in-laws after husband's death
  - Social exclusion (considered inauspicious)
  - Forced to beg at temples
  - "White widow" — stripped of colour, jewellery, identity
  - Kashi labh — widows brought to die in Varanasi
  - Remarriage socially forbidden in many communities

Dimensions tracked:
  1. Widow population estimate
  2. % widows in poverty
  3. Legal property rights enforcement
  4. Social restrictions (remarriage, dress, participation)
  5. Widow abandonment rate
  6. Elderly women homelessness
  7. Access to pension / social protection
  8. Elder care access

India city-level data for temple town widow concentrations.

Sources:
  UN Women (258 million widows globally 2021)
  UNFPA Ageing Population Reports
  HelpAge India State of Elderly 2021
  Loomba Foundation Widow Report
  India Census 2011 (widow data)
  National Sample Survey Organisation
  Society for the Promotion of Area Resource Centres (SPARC)

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, json
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR


# ── GLOBAL WIDOW DATA ─────────────────────────────────────────────────────────
# country, iso, region,
# widow_population_millions,
# widows_in_poverty_pct,
# legal_inheritance_rights,      0-10 (10=strongest)
# inheritance_enforcement,       0-10 (10=best enforcement)
# social_restrictions_score,     0-10 (10=most restrictive)
# widow_abandonment_rate,        0-10 (10=most common)
# elderly_women_homeless_pct,    % of homeless who are elderly women
# pension_coverage_pct,          % widows receiving any pension
# elder_care_access_score,       0-10 (10=best access)
# notes

WIDOW_DATA = [
    # TIER 1 — Strong protections
    ("Iceland",      "ISL","Europe",       0.004, 5, 10,10, 0, 0, 10, 95,10, "Universal pension, full inheritance, no social restrictions"),
    ("Norway",       "NOR","Europe",       0.11,  5, 10,10, 0, 0, 10, 94,10, "State pension covers all widows"),
    ("Sweden",       "SWE","Europe",       0.22,  6, 10,10, 0, 0, 10, 93,10, "Gender-equal inheritance since 1987"),
    ("Germany",      "DEU","Europe",       3.40,  8, 10,10, 0, 0, 12, 92, 9, "Widower's pension + full inheritance rights"),
    ("UK",           "GBR","Europe",       2.80,  8, 10,10, 0, 0, 14, 90, 9, "Bereavement Support Payment. Care home gap for women."),
    ("Australia",    "AUS","Oceania",      0.80,  9, 10,10, 0, 0, 15, 88, 9, "Age Pension + superannuation gap (women save less)"),
    ("Canada",       "CAN","N. America",   0.90, 10, 10,10, 0, 0, 14, 87, 9, "CPP Survivor Benefit. Indigenous widows face different reality."),
    ("USA",          "USA","N. America",   11.60, 12, 10,10, 0, 0, 18, 85, 8, "Social Security survivor benefits. 1.4M elderly women in poverty."),
    ("Japan",        "JPN","East Asia",    10.20,  8, 10,10, 1, 0, 16, 89, 9, "Strong pension. Cultural expectation widows care for in-laws. Low remarriage."),
    ("South Korea",  "KOR","East Asia",    2.80,  9, 10,10, 2, 0, 18, 86, 8, "Strong pension but cultural restrictions remain. Ppal-li ppal-li culture."),

    # TIER 2
    ("Brazil",       "BRA","S. America",   5.20, 28, 9, 7, 1, 1, 28, 68, 5, "INSS pension but many widows informal workers. Urban elderly homelessness rising."),
    ("Mexico",       "MEX","N. America",   3.80, 32, 8, 6, 2, 2, 30, 62, 4, "IMSS pension. Indigenous widows face stronger social restrictions."),
    ("India",        "IND","South Asia",  42.40, 55, 6, 3, 9, 8, 38, 18, 2, "40-42M widows (largest globally). See India detail below."),
    ("China",        "CHN","East Asia",   35.20, 14, 8, 7, 2, 1, 20, 72, 6, "Rural/urban divide. Rural elderly women left behind as youth migrate."),
    ("Indonesia",    "IDN","SE Asia",      5.80, 38, 6, 5, 4, 3, 32, 42, 3, "Islamic inheritance: widows receive 1/8 of estate. Social restrictions in conservative areas."),
    ("Philippines",  "PHL","SE Asia",      2.10, 30, 8, 6, 2, 1, 25, 52, 4, "SSS pension. Strong family support culture but financial dependence."),
    ("South Africa", "ZAF","Africa",       1.80, 40, 7, 5, 2, 3, 35, 55, 5, "Social grant but property stripping common. Ukungena (levirate marriage) still practiced."),
    ("Nigeria",      "NGA","Africa",       4.20, 68, 3, 2, 8, 7, 42, 12, 2, "Widow inheritance by in-laws. Forced levirate marriage. Property stripping near-universal."),
    ("Kenya",        "KEN","Africa",       1.60, 58, 5, 4, 6, 6, 38, 18, 2, "Property grabbing by in-laws common. Wife inheritance practiced in some communities."),
    ("Bangladesh",   "BGD","South Asia",   5.80, 62, 4, 2, 8, 6, 40, 14, 2, "Widow remarriage socially stigmatised. Property stripping common. No widow pension."),
    ("Pakistan",     "PAK","South Asia",   5.20, 72, 3, 1, 9, 7, 42, 10, 1, "Islamic law gives 1/8 inheritance but rarely enforced. Extreme social restrictions."),
    ("Turkey",       "TUR","Europe/Asia",  1.90, 22, 8, 7, 3, 1, 22, 64, 5, "SGK pension. Rural vs urban gap significant."),
    ("Vietnam",      "VNM","SE Asia",      2.10, 25, 7, 6, 3, 2, 24, 56, 4, "War widows policy (post-1975). Social support but rural gap."),
    ("Rwanda",       "RWA","Africa",       0.48, 42, 7, 5, 4, 3, 35, 28, 3, "Post-genocide: 300K+ war widows. Gacaca courts addressed some property cases."),
    ("Colombia",     "COL","S. America",   1.20, 34, 8, 6, 2, 2, 28, 52, 4, "COLPENSIONES pension. Conflict widows face additional displacement."),

    # TIER 3
    ("Ethiopia",     "ETH","Africa",       4.10, 72, 3, 2, 7, 7, 44, 8,  1, "Widow inheritance (Gudifecha). Property stripping. No widow-specific pension."),
    ("Tanzania",     "TZA","Africa",       2.20, 68, 3, 2, 7, 6, 40, 10, 1, "Widow disinheritance common. Forced shaving, isolation rituals in some regions."),
    ("Uganda",       "UGA","Africa",       1.80, 66, 3, 2, 7, 6, 40, 10, 1, "Property grabbing documented by HRW. Wife inheritance practiced."),
    ("Myanmar",      "MMR","SE Asia",      1.20, 58, 4, 3, 5, 4, 36, 12, 2, "Military widows face particular vulnerability. Conflict displacement."),
    ("Egypt",        "EGY","Africa/ME",    2.60, 38, 5, 4, 7, 3, 28, 32, 3, "Islamic inheritance 1/8 share. Khul divorce makes widows more vulnerable."),
    ("Iraq",         "IRQ","Middle East",  1.40, 52, 4, 2, 7, 4, 34, 18, 2, "War widows: 2-3M (Iraq War + ISIS). No functioning widow support system."),

    # TIER 4
    ("Afghanistan",  "AFG","South Asia",   1.80, 85, 1, 0,10,10, 50,  2, 0, "Taliban: widows banned from going outside without male guardian. Begging only option. No pension. Burqa mandatory."),
    ("Yemen",        "YEM","Middle East",  0.90, 80, 1, 0, 9, 8, 46,  4, 0, "Active conflict: hundreds of thousands of war widows. No support system."),
    ("Somalia",      "SOM","Africa",       0.48, 84, 1, 0,10,10, 50,  2, 0, "No functioning legal system. Widows dependent on clan. Extreme vulnerability."),
    ("Niger",        "NER","Africa",       0.64, 82, 1, 1, 9, 8, 46,  4, 0, "Child widows (child marriage + early death). Levirate marriage."),
    ("DRC",          "COD","Africa",       2.20, 80, 2, 1, 8, 7, 48,  4, 0, "War widows. Property stripping. No functioning state protection."),
    ("Sudan",        "SDN","Africa",       1.20, 78, 2, 1, 8, 7, 46,  4, 0, "Conflict widows. Darfur crisis widows. No support."),
]


# ── INDIA DEEP DIVE ───────────────────────────────────────────────────────────
# State-level widow data + temple town concentrations

INDIA_WIDOW_STATES = [
    # state, code, widow_millions, poverty_pct, property_stripping_common,
    # pension_coverage_pct, temple_town_abandonment,
    # key_note
    ("Uttar Pradesh",     "UP",  8.2, 68, True,  12, True,  "Vrindavan (15-20K abandoned widows), Varanasi, Mathura. Hindi belt worst for widow abandonment."),
    ("West Bengal",       "WB",  4.1, 52, True,  18, True,  "Vrindavan: many Bengali widows. Kalighat, Tarapith temples. Kanyashree helps girls avoid early widowhood."),
    ("Bihar",             "BR",  3.8, 72, True,  10, False, "Highest widow poverty. Child widows from early marriage. Gaya temples. JEEViKA helps some."),
    ("Rajasthan",         "RJ",  2.8, 62, True,  14, False, "Sati tradition history. Pushkar temple town. Widow remarriage highly stigmatised."),
    ("Maharashtra",       "MH",  3.4, 38, True,  24, False, "Urban widows better protected. Pandharpur temple. Pandharpur widows documented."),
    ("Andhra Pradesh",    "AP",  2.1, 44, True,  22, True,  "Tirupati abandoned widows documented. Srisailam. Telugu widow property cases."),
    ("Tamil Nadu",        "TN",  2.2, 32, False, 28, False, "Better state support. Tiruvannamalai some concentration. Stronger property laws."),
    ("Kerala",            "KL",  1.1, 18, False, 42, False, "Best widow protection in India. Kudumbashree includes widows. Strong property rights."),
    ("Karnataka",         "KA",  1.8, 38, True,  22, False, "Dharmasthala, Udupi pilgrim towns. Moderate protection."),
    ("Odisha",            "OD",  1.4, 58, True,  14, True,  "Puri (Jagannath) — widows come to die here. Significant temple town population."),
    ("Madhya Pradesh",    "MP",  1.9, 62, True,  12, False, "Ujjain, Chitrakoot temple towns. High poverty."),
    ("Gujarat",           "GJ",  1.4, 38, False, 24, False, "Dwarka, Somnath temple towns. SEWA includes widows in programs."),
    ("Haryana",           "HR",  0.8, 44, True,  18, False, "Honour-related widow restrictions. Kurukshetra."),
    ("Assam",             "AS",  0.9, 56, True,  14, False, "Kamakhya temple. High widow poverty in tea garden communities."),
    ("Jharkhand",         "JH",  0.8, 68, True,  10, False, "Deoghar (Baba Dham) temple town. Tribal widow land rights particularly vulnerable."),
]

# Temple towns with documented widow populations
TEMPLE_TOWNS = [
    {
        "city":          "Vrindavan",
        "state":         "UP",
        "estimated_widows": 15000,
        "origin_states":  ["West Bengal","Odisha","Bihar","UP"],
        "condition":     "Abandoned by families. Many beg or sing bhajans for rice. Live in ashrams. Average age 60-80. Many arrived after being 'donated' to temple by families.",
        "who_documents": "Loomba Foundation, HelpAge India, Guild of Service",
        "programs":      "Ma Dham Ashram, Sulabh International, Guild of Service",
        "source":        "Loomba Foundation 2018, HelpAge India 2019",
    },
    {
        "city":          "Varanasi",
        "state":         "UP",
        "estimated_widows": 12000,
        "origin_states":  ["Bengal","Bihar","UP","MP"],
        "condition":     "Kashi labh — tradition of dying in Varanasi. Many widows wait to die. Live in dharamshalas, begging at ghats. Moksha Bhavan (liberation house) for dying.",
        "who_documents": "Jonathan Parry (anthropologist), IGNOU studies",
        "programs":      "Varanasi Municipal Corporation widow hostels (inadequate)",
        "source":        "Academic studies + UNFPA India",
    },
    {
        "city":          "Puri",
        "state":         "OD",
        "estimated_widows": 8000,
        "origin_states":  ["Odisha","West Bengal"],
        "condition":     "Jagannath temple widows. Shaved heads, white saris. Many denied entry to temple itself. Live outside temple precincts begging.",
        "who_documents": "Odisha State Commission for Women",
        "programs":      "Limited state ashram support",
        "source":        "Odisha State Commission for Women 2020",
    },
    {
        "city":          "Mathura",
        "state":         "UP",
        "estimated_widows": 6000,
        "origin_states":  ["UP","Bengal","Rajasthan"],
        "condition":     "Krishna pilgrimage town. Many widows abandoned here. Sing bhajans for 2kg rice/day.",
        "who_documents": "Supreme Court of India 2018 order on abandoned widows",
        "programs":      "UP government widow homes (capacity inadequate)",
        "source":        "Supreme Court 2018 + NHRC",
    },
    {
        "city":          "Tirupati",
        "state":         "AP",
        "estimated_widows": 4000,
        "origin_states":  ["Andhra Pradesh","Tamil Nadu"],
        "condition":     "Wealthiest temple in world (Balaji). Yet widows beg at its gates. Tonsured widows (head-shaving ritual). Criminalised in AP in 2018 but persists.",
        "who_documents": "Andhra Pradesh Women's Commission",
        "programs":      "AP government hostel (limited)",
        "source":        "AP Women's Commission 2019",
    },
]


def compute_wevi(row: dict) -> float:
    """Widow & Elderly Vulnerability Index (0-100, higher=more vulnerable)."""
    poverty    = row["widows_in_poverty_pct"]
    legal      = (10 - row["legal_inheritance_rights"]) * 10
    enforce    = (10 - row["inheritance_enforcement"]) * 10
    social     = row["social_restrictions_score"] * 10
    abandon    = row["widow_abandonment_rate"] * 10
    pension    = 100 - row["pension_coverage_pct"]
    care       = (10 - row["elder_care_access_score"]) * 10
    return round((poverty*0.20 + legal*0.15 + enforce*0.15 +
                  social*0.15 + abandon*0.15 + pension*0.10 + care*0.10), 1)


def generate(year=BASELINE_YEAR):
    rows = []
    for stat in WIDOW_DATA:
        (country, iso, region, widows, pov, legal, enforce,
         social, abandon, homeless_pct, pension, care, notes) = stat
        row = {
            "country":                    country,
            "iso_code":                   iso,
            "region":                     region,
            "widow_population_millions":  widows,
            "widows_in_poverty_pct":      pov,
            "legal_inheritance_rights":   legal,
            "inheritance_enforcement":    enforce,
            "social_restrictions_score":  social,
            "widow_abandonment_rate":     abandon,
            "elderly_women_homeless_pct": homeless_pct,
            "pension_coverage_pct":       pension,
            "elder_care_access_score":    care,
            "notes":                      notes,
            "year":                       year,
        }
        row["wevi_score"] = compute_wevi(row)
        rows.append(row)

    rows.sort(key=lambda x: x["wevi_score"], reverse=True)
    for i, r in enumerate(rows): r["rank"] = i + 1

    # India states
    state_rows = []
    for stat in INDIA_WIDOW_STATES:
        (state, code, widows, pov, stripping, pension, temple, note) = stat
        state_rows.append({
            "state": state, "state_code": code,
            "widow_millions": widows,
            "poverty_pct": pov,
            "property_stripping_common": "yes" if stripping else "no",
            "pension_coverage_pct": pension,
            "temple_town_abandonment": "yes" if temple else "no",
            "vulnerability_score": round(pov*0.4 + (100-pension)*0.3 + (80 if stripping else 20)*0.3, 1),
            "note": note,
            "year": year,
        })
    state_rows.sort(key=lambda x: x["vulnerability_score"], reverse=True)

    # Save global CSV
    out = OUTPUT_DIR / f"widow-elderly-index-{year}.csv"
    hdr = (
        f"# SHEtoken Widow & Elderly Women Vulnerability Index (WEVI) — {year}\n"
        f"# WEVI: higher score = more vulnerable\n"
        f"# Global widows: 258 million (UN Women 2021)\n"
        f"# India: 40-42 million widows (largest widow population globally)\n"
        f"# 115 million widows globally live in poverty\n"
        f"#\n"
        f"# India temple town crisis: 45,000-50,000 abandoned widows documented\n"
        f"# in Vrindavan, Varanasi, Puri, Mathura, Tirupati alone.\n"
        f"# True figure likely 200,000+ across all pilgrimage sites.\n"
        f"#\n"
        f"# Sources: UN Women, UNFPA, Loomba Foundation, HelpAge India,\n"
        f"#          NHRC, Supreme Court of India orders, HRW country reports\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    fnames = ["rank","country","iso_code","region","widow_population_millions",
              "widows_in_poverty_pct","legal_inheritance_rights",
              "inheritance_enforcement","social_restrictions_score",
              "widow_abandonment_rate","elderly_women_homeless_pct",
              "pension_coverage_pct","elder_care_access_score",
              "wevi_score","notes","year"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fnames, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    with open(out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())

    # Save India states CSV
    india_out = OUTPUT_DIR / f"india-widow-states-{year}.csv"
    shdr = (f"# SHEtoken India Widow Vulnerability by State — {year}\n"
            f"# (c) 2026 SHE Foundation\n#\n")
    sfnames = ["state","state_code","widow_millions","poverty_pct",
               "property_stripping_common","pension_coverage_pct",
               "temple_town_abandonment","vulnerability_score","note","year"]
    sbuf = io.StringIO()
    sw = csv.DictWriter(sbuf, fieldnames=sfnames, extrasaction="ignore")
    sw.writeheader(); sw.writerows(state_rows)
    with open(india_out,"w",newline="",encoding="utf-8") as f:
        f.write(shdr+sbuf.getvalue())

    # Save temple towns JSON
    temple_out = OUTPUT_DIR / "india-temple-town-widows.json"
    temple_data = {
        "description": "Documented widow populations in Indian temple towns",
        "total_documented": sum(t["estimated_widows"] for t in TEMPLE_TOWNS),
        "note": "True figure likely 200,000+ across all pilgrimage sites. These are only the most documented.",
        "source": "Loomba Foundation, NHRC, Supreme Court orders, State Women's Commissions",
        "towns": TEMPLE_TOWNS,
    }
    with open(temple_out,"w",encoding="utf-8") as f:
        json.dump(temple_data, f, indent=2, ensure_ascii=False)

    # Print summary
    total_widows  = sum(r["widow_population_millions"] for r in rows)
    total_poverty = sum(r["widow_population_millions"]*r["widows_in_poverty_pct"]/100
                        for r in rows)
    print(f"Widow & Elderly Women Vulnerability Index — {year}")
    print("="*70)
    print(f"  Countries: {len(rows)}")
    print(f"  Total widows (countries covered): {total_widows:.1f} million")
    print(f"  Widows in poverty (est.):         {total_poverty:.1f} million")
    print()
    print(f"  {'Rk':<4} {'Country':<18} {'WEVI':>6} {'Widows(M)':>10} "
          f"{'Poverty%':>9} {'Pension%':>9}")
    print(f"  {'─'*60}")
    for r in rows[:15]:
        print(f"  {r['rank']:<4} {r['country']:<18} {r['wevi_score']:>6} "
              f"{r['widow_population_millions']:>10.2f} "
              f"{r['widows_in_poverty_pct']:>8}% "
              f"{r['pension_coverage_pct']:>8}%")
    print()
    print(f"  INDIA DETAIL:")
    india = next(r for r in rows if r["iso_code"]=="IND")
    print(f"    Widow population:       {india['widow_population_millions']}M (largest globally)")
    print(f"    Widows in poverty:      {india['widows_in_poverty_pct']}%")
    print(f"    Pension coverage:       {india['pension_coverage_pct']}% (₹200-500/month)")
    print(f"    Legal rights score:     {india['legal_inheritance_rights']}/10")
    print(f"    Enforcement score:      {india['inheritance_enforcement']}/10")
    print(f"    Social restrictions:    {india['social_restrictions_score']}/10")
    print(f"    Abandonment rate:       {india['widow_abandonment_rate']}/10")
    print(f"    WEVI score:             {india['wevi_score']}/100 (higher=more vulnerable)")
    print()
    print(f"  INDIA TEMPLE TOWNS (documented abandoned widows):")
    for t in TEMPLE_TOWNS:
        print(f"    {t['city']:<15} (~{t['estimated_widows']:,} widows) — {t['state']}")
    print(f"    TOTAL documented:    ~{sum(t['estimated_widows'] for t in TEMPLE_TOWNS):,}")
    print(f"    True estimate:       200,000+ across all sites")
    print()
    print(f"  INDIA STATES (most vulnerable):")
    for s in state_rows[:5]:
        print(f"    {s['state']:<20} {s['widow_millions']}M widows | "
              f"{s['poverty_pct']}% poverty | pension {s['pension_coverage_pct']}%")
    print(f"\n  Saved: {out}")
    print(f"  Saved: {india_out}")
    print(f"  Saved: {temple_out}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=BASELINE_YEAR)
    generate(p.parse_args().year)
