"""
SHEtoken — Historical India State WEI Generator
Generates state-level WEI for 2015-2024 using state-specific events.
"""
import csv, io, os, sys, argparse
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

HIST_DIR = OUTPUT_DIR / "historical"
HIST_DIR.mkdir(parents=True, exist_ok=True)

def wei(r):
    try:
        return round(
            float(r.get("empowerment_score",0))*0.15 +
            float(r.get("education_score",0))*0.12 +
            float(r.get("economic_score",0))*0.12 +
            float(r.get("health_score",0))*0.12 +
            float(r.get("bodily_autonomy_score",0))*0.15 +
            float(r.get("safety_justice_score",0))*0.14 +
            float(r.get("dignity_welfare_score",0))*0.10 +
            float(r.get("digital_social_score",0))*0.10 -
            float(r.get("violence_penalty_score",0))*0.10, 1)
    except: return 0.0

# India state-specific events
STATE_EVENTS = {
    2015: {
        "WB": {"education_score":1.0,"bodily_autonomy_score":1.0},  # Kanyashree scaling
        "KL": {"economic_score":1.0,"dignity_welfare_score":1.0},   # Kudumbashree 17yr
        "RJ": {"education_score":1.5},                               # Educate Girls scaling
    },
    2016: {
        "BR": {"economic_score":1.5},  # JEEViKA scaling
        "WB": {"education_score":0.5,"bodily_autonomy_score":1.0},  # Kanyashree UNESCO
    },
    2017: {
        "KL": {"economic_score":0.5,"safety_justice_score":0.5},
        "WB": {"empowerment_score":0.5},
    },
    2018: {
        "WB": {"education_score":1.0,"bodily_autonomy_score":1.5},  # Kanyashree expansion
        "KL": {"dignity_welfare_score":1.0,"economic_score":0.5},
        "BR": {"economic_score":1.0},  # JEEViKA growth
        "RJ": {"education_score":1.0,"bodily_autonomy_score":0.5},
    },
    2019: {
        "WB": {"bodily_autonomy_score":1.0},
        "KL": {"empowerment_score":1.0},
        "HR": {"bodily_autonomy_score":1.0},  # Sex ratio improvement
    },
    2020: {
        # COVID — all states
        "__ALL__": {
            "economic_score":-3.0, "safety_justice_score":-2.5,
            "education_score":-2.0,"dignity_welfare_score":-2.0,
        },
        "WB": {"dignity_welfare_score":0.5},  # Lakshmi Bhandar announced
    },
    2021: {
        "__ALL__": {
            "economic_score":1.5, "education_score":1.0,
        },  # Recovery + school reopen
        "WB": {
            "dignity_welfare_score":3.0,"economic_score":2.0,
            "bodily_autonomy_score":1.5,
        },  # Lakshmi Bhandar launches May 2021
        "KL": {"economic_score":1.0,"dignity_welfare_score":1.0},
        "OD": {"safety_justice_score":1.5},  # Mission Shakti expansion
    },
    2022: {
        "WB": {"education_score":1.5,"bodily_autonomy_score":1.5},
        "RJ": {"education_score":2.0,"bodily_autonomy_score":1.5},  # Educate Girls milestone
        "BR": {"economic_score":1.5},  # JEEViKA ₹11K crore
        "KL": {"economic_score":0.5},
        "UP": {"economic_score":1.0},  # UPSRLM scaling
    },
    2023: {
        "WB": {"economic_score":1.0,"bodily_autonomy_score":1.0},
        "IND_ALL": {"digital_social_score":2.0},  # India digital push
        "KL": {"health_score":0.5},
    },
    2024: {
        "WB": {"economic_score":0.5},
        "RJ": {"education_score":1.0},
        # Women's reservation bill — symbolic empowerment signal
        "__ALL__": {"empowerment_score":0.5},
    },
}

PILLAR_COLS = [
    "empowerment_score","education_score","economic_score","health_score",
    "bodily_autonomy_score","safety_justice_score","dignity_welfare_score",
    "digital_social_score","violence_penalty_score",
]

TRENDS = {
    "empowerment_score":0.15, "education_score":0.25, "economic_score":0.20,
    "health_score":0.20, "bodily_autonomy_score":0.20,
    "safety_justice_score":0.10, "dignity_welfare_score":0.20,
    "digital_social_score":0.45, "violence_penalty_score":-0.05,
}


def load_india_2025():
    path = OUTPUT_DIR / "india-states-2025.csv"
    rows = []
    with open(path,"r",encoding="utf-8") as f:
        lines=[l for l in f if not l.startswith("#")]
    for row in csv.DictReader(io.StringIO("".join(lines))):
        rows.append(dict(row))
    return rows


def generate_state_year(baseline_rows, target_year):
    years_back = 2025 - target_year
    rows = []
    for base in baseline_rows:
        code = base.get("state_code","")
        r    = dict(base)

        # 1. Reverse events after target_year
        for ev_year in sorted(STATE_EVENTS.keys(), reverse=True):
            if ev_year <= target_year: break
            for key, deltas in STATE_EVENTS[ev_year].items():
                if key in (code, "__ALL__", "IND_ALL"):
                    for col, delta in deltas.items():
                        try:
                            r[col] = round(max(0,min(100,
                                float(r.get(col,50)) - delta)),1)
                        except: pass

        # 2. Trend backwards
        for col in PILLAR_COLS:
            rate = TRENDS.get(col, 0.10)
            try:
                r[col] = round(max(0,min(100,
                    float(r.get(col,50)) - rate * years_back)),1)
            except: pass

        # 3. Apply events of target_year
        for key, deltas in STATE_EVENTS.get(target_year, {}).items():
            if key in (code, "__ALL__", "IND_ALL"):
                for col, delta in deltas.items():
                    try:
                        r[col] = round(max(0,min(100,
                            float(r.get(col,50)) + delta)),1)
                    except: pass

        r["wei_score"] = wei(r)
        r["year"]      = target_year
        r["change"]    = 0
        rows.append(r)

    rows.sort(key=lambda x: float(x.get("wei_score",0)), reverse=True)
    for i,r in enumerate(rows): r["rank"] = i+1
    return rows


def main(from_year=2015, to_year=2024):
    print(f"India States Historical WEI {from_year}-{to_year}")
    print("="*55)

    baseline = load_india_2025()
    fnames   = list(baseline[0].keys())
    all_rows = []

    for year in range(from_year, to_year+1):
        rows = generate_state_year(baseline, year)
        all_rows.extend(rows)

        top = rows[0]
        wb  = next((r for r in rows if r.get("state_code")=="WB"), {})
        br  = next((r for r in rows if r.get("state_code")=="BR"), {})
        print(f"  {year}: Top: {top['state']:<16} ({top['wei_score']}) | "
              f"WB: {wb.get('wei_score','?')} | "
              f"BR: {br.get('wei_score','?')}")

    # Save combined trend CSV
    out = HIST_DIR / "india-state-trends.csv"
    trend_flds = ["state","state_code","ticker","year","wei_score",
                  "empowerment_score","education_score","economic_score",
                  "health_score","bodily_autonomy_score","safety_justice_score",
                  "dignity_welfare_score","digital_social_score",
                  "violence_penalty_score"]
    hdr = ("# SHEtoken WEI India State Historical Trends 2015-2024\n"
           "# (c) 2026 SHE Foundation\n#\n")
    buf = io.StringIO()
    w   = csv.DictWriter(buf, fieldnames=trend_flds, extrasaction="ignore")
    w.writeheader(); w.writerows(all_rows)
    with open(out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())
    print(f"\n  Saved: {out} ({len(all_rows)} rows)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--from-year", type=int, default=2015)
    parser.add_argument("--to-year",   type=int, default=2024)
    args = parser.parse_args()
    main(args.from_year, args.to_year)
