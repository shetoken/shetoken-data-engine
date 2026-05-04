"""
SHEtoken — Historical GPI Generator (2015-2024)
================================================
Gender Poverty Index historical data using event-reversal model.

Key events encoded:
  2017: Saudi Vision 2030 (women's economic inclusion begins)
  2018: Iceland Equal Pay Certification law (first globally)
  2020: COVID-19 (women's economic regression globally)
  2020: India informal sector shock (women disproportionately affected)
  2021: COVID recovery — uneven (women recovered slower)
  2022: USA Dobbs — women leaving workforce in ban states
  2022: Colombia abortion decrim (women's economic mobility improved)
  2023: Japan equal pay reforms
  2024: Mexico first female president (economic signal)

GPI trend rates (annual improvement going forward):
  Most dimensions improve ~0.3-0.5 pts/year in Tier 2
  Time poverty (care work) barely changes — most stubborn
  Land ownership changes slowest
  Digital financial inclusion improving fastest

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, argparse
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

HIST_DIR = OUTPUT_DIR / "historical"
HIST_DIR.mkdir(parents=True, exist_ok=True)

# Annual improvement rates per dimension per tier
# Going backwards = subtract these
GPI_TRENDS = {
    "gpi_income_poverty":       {"T1":0.15,"T2":0.35,"T3":0.25,"T4":0.10},
    "gpi_wealth":               {"T1":0.20,"T2":0.40,"T3":0.30,"T4":0.10},
    "gpi_wage":                 {"T1":0.15,"T2":0.30,"T3":0.20,"T4":0.08},
    "gpi_labour_participation": {"T1":0.10,"T2":0.35,"T3":0.25,"T4":0.08},
    "gpi_financial_inclusion":  {"T1":0.10,"T2":0.50,"T3":0.45,"T4":0.20},
    "gpi_food_security":        {"T1":0.10,"T2":0.25,"T3":0.20,"T4":0.08},
    "gpi_time_poverty":         {"T1":0.05,"T2":0.10,"T3":0.08,"T4":0.03},
    "gpi_land_ownership":       {"T1":0.10,"T2":0.15,"T3":0.12,"T4":0.05},
    "gpi_social_protection":    {"T1":0.10,"T2":0.35,"T3":0.25,"T4":0.08},
}

GPI_DIMS = list(GPI_TRENDS.keys())

GPI_EVENTS = {
    2017: {
        "SAU": {"gpi_labour_participation":3.0,"gpi_wage":2.0,
                "gpi_financial_inclusion":3.0,"gpi_social_protection":1.5},
        "ISL": {"gpi_wage":2.0},  # Iceland equal pay discussions peak
    },
    2018: {
        "ISL": {"gpi_wage":3.0,"gpi_social_protection":1.5},  # Equal Pay Cert law
        "__TIER1__": {"gpi_wage":0.5},  # MeToo = wage awareness
    },
    2020: {
        # COVID: women hit harder (service sector, care burden)
        "__ALL__": {
            "gpi_income_poverty":    -3.5,
            "gpi_labour_participation": -2.5,
            "gpi_time_poverty":      -3.0,  # care burden exploded
            "gpi_food_security":     -2.0,
            "gpi_wage":              -1.0,
        },
        "IND": {"gpi_income_poverty":-2.0,"gpi_labour_participation":-3.0},
        "NGA": {"gpi_food_security":-3.0,"gpi_income_poverty":-2.5},
    },
    2021: {
        # Partial recovery — women slower to return to workforce
        "__ALL__": {
            "gpi_income_poverty":    2.0,
            "gpi_labour_participation": 1.5,
            "gpi_financial_inclusion": 1.0,
        },
        "SAU": {"gpi_labour_participation":2.0,"gpi_wage":1.5},
    },
    2022: {
        # USA: Dobbs — women leaving workforce in ban states
        "USA": {"gpi_labour_participation":-2.0,"gpi_income_poverty":-1.5,
                "gpi_wage":-1.0},
        # Colombia: abortion decrim — economic mobility
        "COL": {"gpi_labour_participation":2.0,"gpi_income_poverty":1.5},
        # Global digital financial inclusion improving rapidly
        "__ALL__": {"gpi_financial_inclusion":1.5},
    },
    2023: {
        # Japan equal pay reforms
        "JPN": {"gpi_wage":2.0,"gpi_labour_participation":1.5},
        # SAU continued improvement
        "SAU": {"gpi_wage":2.0,"gpi_labour_participation":1.5,
                "gpi_social_protection":1.5},
        # India digital financial inclusion (Jan Dhan)
        "IND": {"gpi_financial_inclusion":3.0},
    },
    2024: {
        # Mexico first female president signal
        "MEX": {"gpi_labour_participation":1.5,"gpi_wage":1.0},
        # Namibia first female president
        "NAM": {"gpi_labour_participation":1.0},
        "__ALL__": {"gpi_financial_inclusion":1.0},
    },
}

# GPI composite formula
def gpi_score(row):
    return round(sum(row.get(d,50) for d in GPI_DIMS) / len(GPI_DIMS), 1)


def tier_key(tier):
    return f"T{tier}"


def load_gpi_2025():
    path = OUTPUT_DIR / "gender-poverty-index-2025.csv"
    if not path.exists():
        raise FileNotFoundError(f"Run generate_gender_poverty_index.py first")
    rows = []
    with open(path,"r",encoding="utf-8") as f:
        lines=[l for l in f if not l.startswith("#")]
    for row in csv.DictReader(io.StringIO("".join(lines))):
        rows.append(dict(row))
    return rows


def load_tier_lookup():
    """Load tier from WEI baseline to apply tier-specific trends."""
    path = OUTPUT_DIR / "baseline-2025.csv"
    if not path.exists(): return {}
    tiers = {}
    with open(path,"r",encoding="utf-8") as f:
        lines=[l for l in f if not l.startswith("#")]
    for row in csv.DictReader(io.StringIO("".join(lines))):
        tiers[row.get("iso_code","")] = int(row.get("tier",2))
    return tiers


def generate_year(baseline_rows, tier_lookup, target_year):
    years_back = 2025 - target_year
    rows = []
    for base in baseline_rows:
        iso  = base.get("iso_code","")
        tier = tier_lookup.get(iso, 2)
        tk   = tier_key(tier)
        r    = dict(base)

        # 1. Reverse events after target_year
        for ev_year in sorted(GPI_EVENTS.keys(), reverse=True):
            if ev_year <= target_year: break
            for key, deltas in GPI_EVENTS[ev_year].items():
                applies = (key==iso or key=="__ALL__" or
                          (key=="__TIER1__" and tier==1))
                if not applies: continue
                for dim, delta in deltas.items():
                    try:
                        r[dim] = round(max(0,min(100,
                            float(r.get(dim,50)) - delta)),1)
                    except: pass

        # 2. Trend backwards
        for dim, rates in GPI_TRENDS.items():
            rate = rates.get(tk, 0.15)
            try:
                r[dim] = round(max(0,min(100,
                    float(r.get(dim,50)) - rate * years_back)),1)
            except: pass

        # 3. Apply target year events
        for key, deltas in GPI_EVENTS.get(target_year,{}).items():
            applies = (key==iso or key=="__ALL__" or
                      (key=="__TIER1__" and tier==1))
            if not applies: continue
            for dim, delta in deltas.items():
                try:
                    r[dim] = round(max(0,min(100,
                        float(r.get(dim,50)) + delta)),1)
                except: pass

        r["gpi_score"] = gpi_score(r)
        r["year"] = target_year
        rows.append(r)

    rows.sort(key=lambda x: float(x.get("gpi_score",0)), reverse=True)
    for i,r in enumerate(rows): r["rank"]=i+1
    return rows


def main(from_year=2015, to_year=2024):
    print("GPI Historical Generator")
    print("="*55)

    baseline   = load_gpi_2025()
    tiers      = load_tier_lookup()
    all_flat   = []
    all_years  = {}

    for year in range(from_year, to_year+1):
        rows = generate_year(baseline, tiers, year)
        all_years[year] = rows
        avg = round(sum(float(r.get("gpi_score",0)) for r in rows)/len(rows),1)
        top = rows[0]
        bot = rows[-1]
        print(f"  {year}: avg {avg} | Top: {top['country']:<12}({top['gpi_score']}) | "
              f"Bottom: {bot['country']:<12}({bot['gpi_score']})")
        for r in rows:
            all_flat.append({"iso_code":r.get("iso_code",""),
                             "country":r.get("country",""),
                             "year":year,
                             **{d:r.get(d,"") for d in GPI_DIMS},
                             "gpi_score":r.get("gpi_score",""),
                             "rank":r.get("rank","")})

    # Save trend CSV
    out = HIST_DIR / "gpi-country-trends.csv"
    flds = ["iso_code","country","year","gpi_score"]+GPI_DIMS+["rank"]
    hdr = (f"# SHEtoken GPI Historical Trends {from_year}-{to_year}\n"
           f"# Gender Poverty Index — 9 economic dimensions\n"
           f"# (c) 2026 SHE Foundation\n#\n")
    buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=flds,extrasaction="ignore")
    w.writeheader(); w.writerows(all_flat)
    with open(out,"w",newline="",encoding="utf-8") as f: f.write(hdr+buf.getvalue())

    # Print notable trends
    print(f"\n  Notable GPI trends (2015→2024):")
    for iso,label in [("ISL","Iceland"),("USA","USA"),("SAU","Saudi Arabia"),
                       ("IND","India"),("JPN","Japan"),("NGA","Nigeria")]:
        s15 = next((r["gpi_score"] for r in all_years.get(from_year,[])
                    if r.get("iso_code")==iso), "—")
        s22 = next((r["gpi_score"] for r in all_years.get(2022,[])
                    if r.get("iso_code")==iso), "—")
        s24 = next((r["gpi_score"] for r in all_years.get(to_year,[])
                    if r.get("iso_code")==iso), "—")
        print(f"    {label:<15} 2015:{s15:>5}  2022:{s22:>5}  2024:{s24:>5}")

    print(f"\n  Saved: {out} ({len(all_flat)} rows)")


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--from-year",type=int,default=2015)
    p.add_argument("--to-year",type=int,default=2024)
    args=p.parse_args()
    main(args.from_year, args.to_year)
