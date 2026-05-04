"""
SHEtoken Pipeline — Historical WEI Data Generator v2
======================================================
Generates WEI scores for 2015–2024 using event-reversal modeling.

Method:
  Start from 2025 baseline.
  Going backwards year by year:
    1. REVERSE events that happened in years after the target year
       (e.g. for 2020, undo Taliban 2021, undo Roe 2022 etc.)
    2. Apply baseline trend (each year back, slightly worse)
  This correctly shows:
    - Afghanistan at ~32 WEI in 2020 (before Taliban)
    - USA at ~77 in 2021 (before Dobbs)
    - COVID dip in 2020 across all countries
    - Saudi Arabia lower in 2015 (before Vision 2030)

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, argparse
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

HIST_DIR = OUTPUT_DIR / "historical"
HIST_DIR.mkdir(parents=True, exist_ok=True)

PILLAR_COLS = [
    "empowerment_score","education_score","economic_score","health_score",
    "bodily_autonomy_score","safety_justice_score","dignity_welfare_score",
    "digital_social_score","violence_penalty_score",
]

# Annual improvement rate per pillar (going forward = this much better per year)
# Going backwards = subtract this per year
TRENDS = {
    "empowerment_score":      {"T1":0.20,"T2":0.30,"T3":0.35,"T4":0.10},
    "education_score":        {"T1":0.15,"T2":0.40,"T3":0.50,"T4":0.25},
    "economic_score":         {"T1":0.15,"T2":0.25,"T3":0.20,"T4":0.10},
    "health_score":           {"T1":0.10,"T2":0.35,"T3":0.45,"T4":0.30},
    "bodily_autonomy_score":  {"T1":0.15,"T2":0.20,"T3":0.25,"T4":0.10},
    "safety_justice_score":   {"T1":0.10,"T2":0.15,"T3":0.15,"T4":0.05},
    "dignity_welfare_score":  {"T1":0.15,"T2":0.25,"T3":0.20,"T4":0.10},
    "digital_social_score":   {"T1":0.40,"T2":0.60,"T3":0.55,"T4":0.30},
    "violence_penalty_score": {"T1":-0.05,"T2":-0.08,"T3":-0.05,"T4":-0.02},
}

# Events: {year: {iso or __ALL__: {pillar: net_delta_from_that_year_onward}}}
# Positive = improvement that year, Negative = regression
# When going BEFORE this year, we REVERSE the delta

EVENTS = {
    2015: {
        "__ALL__": {"empowerment_score":0.3, "education_score":0.2},  # SDG launch
    },
    2017: {
        "SAU": {"economic_score":2.0,"empowerment_score":1.0,
                "bodily_autonomy_score":1.5,"digital_social_score":2.0},
        "IND": {"economic_score":-0.5},  # demonetization
    },
    2018: {
        "SAU": {"empowerment_score":1.5,"economic_score":1.5},  # women driving
        "__TIER1__": {"safety_justice_score":0.5},  # MeToo
    },
    2019: {
        "SDN": {"empowerment_score":3.0,"safety_justice_score":2.0},
        "ETH": {"empowerment_score":2.0},
    },
    2020: {
        "__ALL__": {
            "economic_score":-2.5, "safety_justice_score":-2.0,
            "health_score":-1.5,   "education_score":-1.5,
            "dignity_welfare_score":-2.0,
        },
    },
    2021: {
        # Taliban takeover
        "AFG": {
            "empowerment_score":-28.0, "education_score":-35.0,
            "economic_score":-22.0,    "bodily_autonomy_score":-22.0,
            "safety_justice_score":-18.0,"dignity_welfare_score":-18.0,
            "digital_social_score":-22.0,"violence_penalty_score":25.0,
        },
        # Myanmar coup
        "MMR": {
            "empowerment_score":-8.0,"safety_justice_score":-6.0,
            "economic_score":-4.0,
        },
        # COVID recovery
        "__ALL__": {
            "economic_score":1.5,"safety_justice_score":0.8,"health_score":0.8,
        },
        # Lakshmi Bhandar WB
        "IND": {"dignity_welfare_score":2.5,"economic_score":1.0},
        "SAU": {"economic_score":1.5,"empowerment_score":1.0},
        "ETH": {"safety_justice_score":-4.0,"dignity_welfare_score":-3.0},
    },
    2022: {
        # Dobbs/Roe overturned
        "USA": {"bodily_autonomy_score":-10.0,"safety_justice_score":-1.0},
        # Colombia abortion decrim
        "COL": {"bodily_autonomy_score":4.0},
        # Chile feminist process
        "CHL": {"empowerment_score":2.0,"bodily_autonomy_score":2.0},
        # Iran Mahsa Amini
        "IRN": {"safety_justice_score":-1.5},
        # Pakistan crisis
        "PAK": {"dignity_welfare_score":-2.0,"economic_score":-1.5},
        # Nigeria VAPP
        "NGA": {"safety_justice_score":1.5},
        "__ALL__": {"digital_social_score":1.0},
    },
    2023: {
        "NER": {"empowerment_score":-4.0,"safety_justice_score":-3.0},
        "BFA": {"empowerment_score":-3.0,"safety_justice_score":-2.0},
        "MLI": {"empowerment_score":-2.0},
        "SDN": {"safety_justice_score":-5.0,"dignity_welfare_score":-4.0},
        "PSE": {"safety_justice_score":-8.0,"dignity_welfare_score":-6.0,
                "health_score":-5.0},
        "USA": {"bodily_autonomy_score":-2.0},
        "SAU": {"empowerment_score":1.5,"economic_score":1.0,
                "bodily_autonomy_score":1.0},
        "IND": {"digital_social_score":2.0,"economic_score":0.5},
    },
    2024: {
        "BGD": {"empowerment_score":-1.5},
        "SDN": {"safety_justice_score":-3.0,"dignity_welfare_score":-3.0},
        "PSE": {"health_score":-5.0,"dignity_welfare_score":-4.0},
        "IND": {"empowerment_score":1.5},
        "NAM": {"empowerment_score":3.0},
        "MEX": {"empowerment_score":4.0},
        "__ALL__": {"digital_social_score":0.5},
    },
}


def wei(row):
    try:
        return round(
            float(row.get("empowerment_score",0))    * 0.15 +
            float(row.get("education_score",0))       * 0.12 +
            float(row.get("economic_score",0))        * 0.12 +
            float(row.get("health_score",0))          * 0.12 +
            float(row.get("bodily_autonomy_score",0)) * 0.15 +
            float(row.get("safety_justice_score",0))  * 0.14 +
            float(row.get("dignity_welfare_score",0)) * 0.10 +
            float(row.get("digital_social_score",0))  * 0.10 -
            float(row.get("violence_penalty_score",0))* 0.10, 1
        )
    except: return 0.0


def tier_key(row):
    return f"T{row.get('tier','2')}"


def reverse_events_for_year(row, target_year):
    """
    Undo all events that happened AFTER target_year.
    e.g. for target_year=2020: undo 2021, 2022, 2023, 2024 events
    """
    iso  = row.get("iso_code","")
    tier = int(row.get("tier",2))
    r    = dict(row)

    for event_year in sorted(EVENTS.keys(), reverse=True):
        if event_year <= target_year:
            break
        for key, deltas in EVENTS[event_year].items():
            applies = (
                key == iso or
                key == "__ALL__" or
                (key == "__TIER1__" and tier == 1)
            )
            if not applies:
                continue
            for col, delta in deltas.items():
                try:
                    r[col] = round(max(0, min(100,
                        float(r.get(col, 50)) - delta)), 1)
                except: pass
    return r


def apply_events_for_year(row, target_year):
    """
    Apply events that happened IN target_year.
    """
    iso  = row.get("iso_code","")
    tier = int(row.get("tier",2))
    r    = dict(row)

    for key, deltas in EVENTS.get(target_year, {}).items():
        applies = (
            key == iso or
            key == "__ALL__" or
            (key == "__TIER1__" and tier == 1)
        )
        if not applies:
            continue
        for col, delta in deltas.items():
            try:
                r[col] = round(max(0, min(100,
                    float(r.get(col, 50)) + delta)), 1)
            except: pass
    return r


def apply_trend_backward(row, years_back):
    """Subtract trend improvement for years_back years."""
    tk = tier_key(row)
    r  = dict(row)
    for col in PILLAR_COLS:
        rate = TRENDS.get(col, {}).get(tk, 0.1)
        try:
            r[col] = round(max(0, min(100,
                float(r.get(col, 50)) - rate * years_back)), 1)
        except: pass
    return r


def load_baseline():
    path = OUTPUT_DIR / "baseline-2025.csv"
    rows = []
    with open(path, "r", encoding="utf-8") as f:
        lines = [l for l in f if not l.startswith("#")]
    reader = csv.DictReader(io.StringIO("".join(lines)))
    for row in reader:
        rows.append(dict(row))
    return rows


def generate_year(baseline_rows, target_year):
    years_back = 2025 - target_year
    rows = []
    for base in baseline_rows:
        # 1. Undo events after target_year
        r = reverse_events_for_year(base, target_year)
        # 2. Apply trend backwards
        r = apply_trend_backward(r, years_back)
        # 3. Apply events of target_year itself
        r = apply_events_for_year(r, target_year)
        # 4. Recalculate WEI
        r["wei_score"]   = wei(r)
        r["year"]        = target_year
        r["wei_version"] = "3.0"
        r["data_source"] = "historical_model"
        rows.append(r)

    rows.sort(key=lambda x: float(x.get("wei_score",0)), reverse=True)
    for i,r in enumerate(rows): r["rank"] = i+1
    return rows


def global_wei(rows):
    tw = sum(float(r.get("wei_score",0))*float(r.get("population_millions",0))
             *{1:1.0,2:1.0,3:0.8,4:0.6}.get(int(r.get("tier",2)),1.0)
             for r in rows)
    tp = sum(float(r.get("population_millions",0))
             *{1:1.0,2:1.0,3:0.8,4:0.6}.get(int(r.get("tier",2)),1.0)
             for r in rows)
    return round(tw/tp, 1) if tp else 0


def save_csv(rows, year, fieldnames):
    gwei = global_wei(rows)
    out  = HIST_DIR / f"baseline-{year}.csv"
    hdr  = (f"# SHEtoken WEI Historical — {year} | Global WEI: {gwei}\n"
            f"# Event-reversal model from 2025 baseline\n"
            f"# (c) 2026 SHE Foundation\n#\n")
    buf  = io.StringIO()
    w    = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    with open(out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())
    return gwei


def save_trend_files(all_years):
    # Global trend
    global_rows = []
    for yr,(gwei,rows) in sorted(all_years.items()):
        tc = {}
        for r in rows:
            t=str(r.get("tier","")); tc[t]=tc.get(t,0)+1
        global_rows.append({
            "year":yr,"global_wei":gwei,"countries":len(rows),
            "tier1":tc.get("1",0),"tier2":tc.get("2",0),
            "tier3":tc.get("3",0),"tier4":tc.get("4",0),
            "top_country":rows[0]["country"],"top_score":rows[0]["wei_score"],
            "bottom_country":rows[-1]["country"],"bottom_score":rows[-1]["wei_score"],
        })
    buf=io.StringIO()
    w=csv.DictWriter(buf,fieldnames=list(global_rows[0].keys()))
    w.writeheader(); w.writerows(global_rows)
    hdr="# SHEtoken WEI Global Trend 2015-2024\n# (c) 2026 SHE Foundation\n#\n"
    with open(HIST_DIR/"wei-global-trend.csv","w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())

    # Country trends (all pillars)
    flat=[]
    for yr,(_,rows) in sorted(all_years.items()):
        for r in rows:
            flat.append({
                "iso_code":r.get("iso_code",""),"country":r.get("country",""),
                "year":yr,"wei_score":r.get("wei_score",""),
                "empowerment_score":r.get("empowerment_score",""),
                "education_score":r.get("education_score",""),
                "economic_score":r.get("economic_score",""),
                "health_score":r.get("health_score",""),
                "bodily_autonomy_score":r.get("bodily_autonomy_score",""),
                "safety_justice_score":r.get("safety_justice_score",""),
                "dignity_welfare_score":r.get("dignity_welfare_score",""),
                "digital_social_score":r.get("digital_social_score",""),
                "violence_penalty_score":r.get("violence_penalty_score",""),
                "tier":r.get("tier",""),
            })
    buf2=io.StringIO()
    flds=["iso_code","country","year","wei_score","empowerment_score",
          "education_score","economic_score","health_score",
          "bodily_autonomy_score","safety_justice_score",
          "dignity_welfare_score","digital_social_score",
          "violence_penalty_score","tier"]
    w2=csv.DictWriter(buf2,fieldnames=flds); w2.writeheader(); w2.writerows(flat)
    hdr2="# SHEtoken WEI Country Trends 2015-2024 — all pillars\n# (c) 2026 SHE Foundation\n#\n"
    with open(HIST_DIR/"wei-country-trends.csv","w",newline="",encoding="utf-8") as f:
        f.write(hdr2+buf2.getvalue())
    print(f"  Country trends: {len(flat)} rows")


def main(from_year=2015, to_year=2024):
    print("SHEtoken WEI Historical Generator v2")
    print(f"Years: {from_year} to {to_year}")
    print("="*55)

    baseline = load_baseline()
    fnames   = list(baseline[0].keys()) + ["data_source"]
    all_years = {}

    for year in range(from_year, to_year+1):
        rows = generate_year(baseline, year)
        gwei = save_csv(rows, year, fnames)
        all_years[year] = (gwei, rows)
        print(f"  {year}: Global WEI {gwei:>5} | "
              f"Top: {rows[0]['country']:<14}({rows[0]['wei_score']}) | "
              f"Bottom: {rows[-1]['country']:<14}({rows[-1]['wei_score']})")

    save_trend_files(all_years)

    print(f"\n  Key country trends:")
    showcase = [("AFG","Afghanistan"),("USA","USA"),
                ("SAU","Saudi Arabia"),("IND","India"),
                ("IRN","Iran"),("MEX","Mexico"),("NGA","Nigeria")]
    for iso, label in showcase:
        scores = {}
        for yr,(_,rows) in all_years.items():
            r = next((r for r in rows if r.get("iso_code")==iso), None)
            if r: scores[yr] = float(r.get("wei_score",0))
        if scores:
            s15 = scores.get(from_year, list(scores.values())[0])
            s20 = scores.get(2020, scores.get(from_year))
            s21 = scores.get(2021, s20)
            s22 = scores.get(2022, s21)
            s24 = scores.get(to_year, list(scores.values())[-1])
            print(f"    {label:<15} "
                  f"{from_year}:{s15:>5}  "
                  f"2020:{s20:>5}  "
                  f"2021:{s21:>5}  "
                  f"2022:{s22:>5}  "
                  f"{to_year}:{s24:>5}")

    print(f"\n  Files: {len(list(HIST_DIR.glob('*.csv')))} CSVs in {HIST_DIR}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-year", type=int, default=2015)
    parser.add_argument("--to-year",   type=int, default=2024)
    p.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    args = parser.parse_args()
    main(args.from_year, args.to_year)