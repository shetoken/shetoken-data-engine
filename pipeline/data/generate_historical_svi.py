"""
SHEtoken — Historical SVI Generator (2015-2024)
================================================
Sexual Violence Index historical data.

Key events:
  2013: India Criminal Law Amendment Act (post-Nirbhaya)
  2017: #MeToo movement — reporting improved in Tier 1 countries
  2018: Ireland: 8th amendment repealed (reproductive rights)
  2019: Nigeria VAPP Act enforcement
  2020: COVID — DV/rape spike globally
  2021: Sarah Everard (UK) — national safety debate
  2022: USA Dobbs — reproductive rights link to SVI
  2022: Colombia abortion decrim — women's safety improved
  2023: Japan: consent-based rape law (long overdue)
  2023: UK Online Safety Act — image-based abuse criminalised

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, argparse
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

HIST_DIR = OUTPUT_DIR / "historical"
HIST_DIR.mkdir(parents=True, exist_ok=True)

SVI_DIMS = [
    "who_lifetime_prevalence_pct",
    "reporting_gap_pct",
    "legal_framework_score",
    "support_services_score",
    "impunity_score",
    "marital_rape_criminalised",
    "conflict_sv_risk_score",
]

# Annual trend rates (improvement going forward)
SVI_TRENDS = {
    "reporting_gap_pct":      {"T1":-0.5,"T2":-0.4,"T3":-0.2,"T4":-0.05},
    "legal_framework_score":  {"T1": 0.05,"T2": 0.08,"T3":0.06,"T4":0.02},
    "support_services_score": {"T1": 0.05,"T2": 0.10,"T3":0.07,"T4":0.02},
    "impunity_score":         {"T1":-0.5,"T2":-0.4,"T3":-0.2,"T4":-0.05},
    "who_lifetime_prevalence_pct": {"T1":-0.1,"T2":-0.15,"T3":-0.1,"T4":-0.05},
}

SVI_EVENTS = {
    2013: {
        # India: Criminal Law Amendment Act — improved legal framework
        "IND": {"legal_framework_score":0.8,"reporting_gap_pct":-3.0},
    },
    2016: {
        # USA: Campus SaVE Act full enforcement
        "USA": {"legal_framework_score":0.3,"support_services_score":0.3},
        # Nigeria VAPP Act 2015 — enforcement begins
        "NGA": {"legal_framework_score":0.5},
    },
    2017: {
        # MeToo — reporting gap reduces in countries with media freedom
        "__TIER1__": {
            "reporting_gap_pct":  -3.0,
            "support_services_score": 0.5,
        },
        "BRA": {"reporting_gap_pct":-2.0},
        "MEX": {"reporting_gap_pct":-1.5},
        "IND": {"reporting_gap_pct":-1.0},
    },
    2018: {
        # Ireland 8th amendment — women's bodily autonomy
        "IRL": {"legal_framework_score":1.0,"support_services_score":0.5},
        # Pakistan: anti-rape special courts
        "PAK": {"legal_framework_score":0.3},
    },
    2019: {
        # Nigeria VAPP enforcement improves
        "NGA": {"legal_framework_score":0.5,"support_services_score":0.3},
        # Mexico City feminist emergency — shelters + legal aid
        "MEX": {"support_services_score":0.5},
        # Kenya Gender Violence Recovery Centre expansion
        "KEN": {"support_services_score":0.5},
    },
    2020: {
        # COVID: rape/DV spike globally, services overwhelmed
        "__ALL__": {
            "impunity_score":         2.0,  # worse impunity
            "support_services_score":-0.5,  # services overwhelmed
        },
        # Conflict zones worsened
        "COD": {"conflict_sv_risk_score":1.0,"impunity_score":2.0},
        "ETH": {"conflict_sv_risk_score":2.0},  # Tigray conflict begins
        "MMR": {"conflict_sv_risk_score":1.0},
    },
    2021: {
        # Sarah Everard case — UK national debate
        "GBR": {
            "support_services_score":0.5,
            "legal_framework_score": 0.3,
            "reporting_gap_pct":    -1.5,
        },
        # Ethiopia Tigray — CRSV documented
        "ETH": {"conflict_sv_risk_score":2.0,"impunity_score":3.0},
        # Afghanistan Taliban — immediate regression
        "AFG": {
            "legal_framework_score": -3.0,
            "support_services_score":-3.0,
            "impunity_score":        10.0,
            "reporting_gap_pct":     5.0,
        },
        # India: POCSO enforcement improved
        "IND": {"legal_framework_score":0.3,"support_services_score":0.3},
    },
    2022: {
        # Colombia: abortion decrim linked to women's safety awareness
        "COL": {"legal_framework_score":0.5,"support_services_score":0.5,
                "reporting_gap_pct":-1.0},
        # Sudan civil war — CRSV begins
        "SDN": {"conflict_sv_risk_score":3.0,"impunity_score":5.0},
        # Palestine — conflict intensification
        "PSE": {"conflict_sv_risk_score":2.0},
        # UK: Police Crime Sentencing Act — image abuse criminalised
        "GBR": {"legal_framework_score":0.5},
    },
    2023: {
        # Japan: consent-based rape law — massive reform
        "JPN": {
            "legal_framework_score": 2.0,
            "reporting_gap_pct":    -3.0,
            "impunity_score":       -5.0,
        },
        # UK Online Safety Act
        "GBR": {"legal_framework_score":0.5,"support_services_score":0.3},
        # Sudan: escalation
        "SDN": {"conflict_sv_risk_score":2.0,"impunity_score":3.0},
        # Niger/Mali coups — women's legal protections eroded
        "NER": {"legal_framework_score":-0.5,"support_services_score":-0.5},
        "MLI": {"legal_framework_score":-0.5},
        # India: One-Stop Centres expansion
        "IND": {"support_services_score":0.5,"reporting_gap_pct":-1.0},
    },
    2024: {
        # Bangladesh: political instability
        "BGD": {"legal_framework_score":-0.3,"support_services_score":-0.3},
        # Pakistan: anti-rape law enforcement patchy
        "PAK": {"impunity_score":1.0},
        # Global: digital sexual violence laws improving
        "__TIER1__": {"legal_framework_score":0.3},
    },
}


def svi_score(row):
    try:
        prev_score  = max(0,min(100,(55-float(row.get("who_lifetime_prevalence_pct",30)))/55*100))
        gap_score   = max(0,min(100,100-float(row.get("reporting_gap_pct",90))))
        legal_score = float(row.get("legal_framework_score",5))*10
        support_score=float(row.get("support_services_score",5))*10
        imp_score   = max(0,min(100,100-float(row.get("impunity_score",80))))
        mr_score    = float(row.get("marital_rape_criminalised",0))*100
        conf_score  = max(0,min(100,(10-float(row.get("conflict_sv_risk_score",0)))/10*100))
        return round(prev_score*0.30+gap_score*0.15+legal_score*0.15+
                     imp_score*0.15+mr_score*0.10+conf_score*0.10+support_score*0.05,1)
    except: return 0.0


def load_svi_2025():
    path = OUTPUT_DIR / "sexual-violence-index-2025.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    rows=[]
    with open(path,"r",encoding="utf-8") as f:
        lines=[l for l in f if not l.startswith("#")]
    for row in csv.DictReader(io.StringIO("".join(lines))):
        rows.append(dict(row))
    return rows


def load_tier_lookup():
    path = OUTPUT_DIR / "baseline-2025.csv"
    if not path.exists(): return {}
    tiers={}
    with open(path,"r",encoding="utf-8") as f:
        lines=[l for l in f if not l.startswith("#")]
    for row in csv.DictReader(io.StringIO("".join(lines))):
        tiers[row.get("iso_code","")]=int(row.get("tier",2))
    return tiers


def generate_year(baseline_rows, tier_lookup, target_year):
    years_back = 2025 - target_year
    rows=[]
    for base in baseline_rows:
        iso  = base.get("iso_code","")
        tier = tier_lookup.get(iso,2)
        tk   = f"T{tier}"
        r    = dict(base)

        # 1. Reverse events after target year
        for ev_year in sorted(SVI_EVENTS.keys(), reverse=True):
            if ev_year <= target_year: break
            for key,deltas in SVI_EVENTS[ev_year].items():
                applies = (key==iso or key=="__ALL__" or
                           (key=="__TIER1__" and tier==1))
                if not applies: continue
                for dim,delta in deltas.items():
                    if dim in SVI_DIMS:
                        try:
                            r[dim]=round(max(0,min(100 if dim!="who_lifetime_prevalence_pct" else 80,
                                float(r.get(dim,50))-delta)),2)
                        except: pass

        # 2. Trend backwards
        for dim,rates in SVI_TRENDS.items():
            rate = rates.get(tk,0.1)
            try:
                r[dim]=round(max(0,float(r.get(dim,50))-rate*years_back),2)
            except: pass

        # 3. Apply target year events
        for key,deltas in SVI_EVENTS.get(target_year,{}).items():
            applies = (key==iso or key=="__ALL__" or
                       (key=="__TIER1__" and tier==1))
            if not applies: continue
            for dim,delta in deltas.items():
                if dim in SVI_DIMS:
                    try:
                        r[dim]=round(max(0,float(r.get(dim,50))+delta),2)
                    except: pass

        r["svi_score"] = svi_score(r)
        r["year"]      = target_year
        rows.append(r)

    rows.sort(key=lambda x: float(x.get("svi_score",0)), reverse=True)
    for i,r in enumerate(rows): r["rank"]=i+1
    return rows


def main(from_year=2015, to_year=2024):
    print("SVI Historical Generator")
    print("="*55)

    baseline = load_svi_2025()
    tiers    = load_tier_lookup()
    all_flat = []
    all_years= {}

    for year in range(from_year, to_year+1):
        rows = generate_year(baseline, tiers, year)
        all_years[year] = rows
        avg = round(sum(float(r.get("svi_score",0)) for r in rows)/len(rows),1)
        print(f"  {year}: avg {avg} | "
              f"Top: {rows[0]['country']:<12}({rows[0]['svi_score']}) | "
              f"Bottom: {rows[-1]['country']:<12}({rows[-1]['svi_score']})")
        for r in rows:
            all_flat.append({
                "iso_code":  r.get("iso_code",""),
                "country":   r.get("country",""),
                "year":      year,
                "svi_score": r.get("svi_score",""),
                "rank":      r.get("rank",""),
                **{d:r.get(d,"") for d in SVI_DIMS},
            })

    out=HIST_DIR/"svi-country-trends.csv"
    flds=["iso_code","country","year","svi_score","rank"]+SVI_DIMS
    hdr=(f"# SHEtoken SVI Historical Trends {from_year}-{to_year}\n"
         f"# Sexual Violence Index — WHO prevalence based\n"
         f"# Key events: India 2013 law reform, MeToo 2017,\n"
         f"#   Japan consent law 2023, Afghanistan collapse 2021\n"
         f"# (c) 2026 SHE Foundation\n#\n")
    buf=io.StringIO()
    w=csv.DictWriter(buf,fieldnames=flds,extrasaction="ignore")
    w.writeheader(); w.writerows(all_flat)
    with open(out,"w",newline="",encoding="utf-8") as f: f.write(hdr+buf.getvalue())

    print(f"\n  Notable SVI trends (2015→2024):")
    for iso,label in [("NOR","Norway"),("JPN","Japan"),("IND","India"),
                       ("PAK","Pakistan"),("AFG","Afghanistan"),("COL","Colombia")]:
        s15=next((r["svi_score"] for r in all_years.get(from_year,[])
                  if r.get("iso_code")==iso),"—")
        s21=next((r["svi_score"] for r in all_years.get(2021,[])
                  if r.get("iso_code")==iso),"—")
        s24=next((r["svi_score"] for r in all_years.get(to_year,[])
                  if r.get("iso_code")==iso),"—")
        print(f"    {label:<15} 2015:{s15:>5}  2021:{s21:>5}  2024:{s24:>5}")

    print(f"\n  Saved: {out} ({len(all_flat)} rows)")


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--from-year",type=int,default=2015)
    p.add_argument("--to-year",type=int,default=2024)
    p.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    args=p.parse_args()
    main(args.from_year, args.to_year)