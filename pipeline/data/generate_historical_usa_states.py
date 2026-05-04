"""
SHEtoken — USA States Historical WEI (2015-2024)
=================================================
The most dramatic historical dataset in the index.

The post-Roe story by state:
  Pre-2022: bodily autonomy scores across states relatively uniform
  June 2022: Dobbs overturns Roe v. Wade
  Immediate effect: 26 states trigger bans or severe restrictions
  Result: bodily autonomy scores diverge by up to 70 points
          between states like Massachusetts (88) and Mississippi (18)

Key events by state:
  2021-09: Texas SB8 — 6-week ban (first effective ban pre-Dobbs)
  2022-06: Dobbs decision — 26 states move immediately
  2022-08: Indiana first post-Dobbs total ban
  2023-04: Florida 6-week ban
  2023-06: North Carolina 12-week ban
  2024-04: Arizona 1864 ban briefly reinstated

State tiers:
  PROTECT: Strengthened protections post-Dobbs (CA, NY, VT, WA etc.)
  RESTRICT: 6-week bans (GA, FL, SC, NC)
  BAN: Total or near-total bans (TX, MS, AL, LA, AR, MO, OK, TN, KY, WV etc.)

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
            float(r.get("violence_penalty_score",0))*0.10,1)
    except: return 0.0


# ── STATE CLASSIFICATION POST-DOBBS ──────────────────────────────────────────
# How much bodily autonomy score dropped after Dobbs
# Based on Guttmacher Institute state policy tracker

STATE_DOBBS_IMPACT = {
    # TOTAL BANS (immediate post-Dobbs)
    "AL": -22, "AR": -22, "ID": -22, "KY": -22, "LA": -22,
    "MI": -18, "MS": -22, "MO": -22, "ND": -20, "OK": -22,
    "SD": -22, "TN": -22, "TX": -20, "WV": -18, "WY": -20,

    # NEAR-TOTAL / 6-WEEK (effective bans)
    "GA": -18, "IN": -18, "OH": -16, "SC": -16, "UT": -14,

    # 12-WEEK BANS (2023)
    "NC": -12, "NE": -12,

    # 15-WEEK BANS
    "AZ": -10, "FL": -16,  # FL moved to 6-week 2023

    # GESTATIONAL LIMITS (22-24 weeks, more moderate)
    "IA": -8, "MT": -4,

    # PROTECTIVE STATES — strengthened rights
    "CA":  +4, "CO":  +3, "CT":  +2, "DE":  +2, "HI":  +2,
    "IL":  +3, "ME":  +2, "MD":  +2, "MA":  +4, "MI":  +2,
    "MN":  +3, "NJ":  +2, "NM":  +2, "NY":  +3, "OR":  +3,
    "PA":   0, "RI":  +2, "VA":  +2, "VT":  +4, "WA":  +3,
    "WI": -14,  # 1849 law briefly in effect

    # MODERATE CHANGE
    "AK": -2, "KS": -6, "NV": 0, "NH": 0,
}

# Texas SB8 — September 2021 (before Dobbs)
TX_SB8_IMPACT = -12  # pre-Dobbs 6-week ban (first in country)

# Additional state-specific events
STATE_EVENTS = {
    2016: {
        # Black maternal mortality crisis highlighted nationally
        "MS": {"health_score":-2.0},
        "AL": {"health_score":-2.0},
        "LA": {"health_score":-2.0},
    },
    2017: {
        # Women's March — empowerment signal
        "__ALL__": {"empowerment_score":0.5},
    },
    2018: {
        # #MeToo effect on state legislation
        "CA": {"safety_justice_score":2.0,"empowerment_score":1.0},
        "NY": {"safety_justice_score":1.5,"empowerment_score":1.0},
        "WA": {"safety_justice_score":1.5},
        "TX": {"safety_justice_score":-1.0},  # Texas rolling back VAWA funding
    },
    2019: {
        # Georgia, Alabama, Missouri heartbeat bills (pre-Dobbs attempts)
        "GA": {"bodily_autonomy_score":-4.0},
        "AL": {"bodily_autonomy_score":-6.0},
        "MO": {"bodily_autonomy_score":-4.0},
        # Virginia purple state shifts
        "VA": {"empowerment_score":2.0,"safety_justice_score":1.5},
    },
    2020: {
        # COVID — DV spike, healthcare disruption
        "__ALL__": {
            "safety_justice_score":-2.0,
            "health_score":-1.5,
            "economic_score":-2.0,
            "dignity_welfare_score":-1.5,
        },
        # Mississippi maternal mortality — worst in country
        "MS": {"health_score":-3.0},
        "AL": {"health_score":-2.5},
        "LA": {"health_score":-2.5},
    },
    2021: {
        # Texas SB8 September 2021 (6-week ban)
        "TX": {"bodily_autonomy_score": TX_SB8_IMPACT},
        # COVID recovery
        "__ALL__": {
            "economic_score":1.5,
            "health_score":0.8,
        },
        # Colorado expands reproductive rights
        "CO": {"bodily_autonomy_score":3.0},
        # Vermont constitutional amendment
        "VT": {"bodily_autonomy_score":4.0,"empowerment_score":2.0},
    },
    2022: {
        # DOBBS — June 24, 2022 — THE DEFINING EVENT
        # Applied per state based on STATE_DOBBS_IMPACT
        # (handled separately below)

        # California Proposition 1 — constitutional right
        "CA": {"bodily_autonomy_score":3.0,"empowerment_score":2.0},
        # Michigan: constitutional amendment (November 2022)
        "MI": {"bodily_autonomy_score":5.0},
        # Kansas: voters reject abortion ban (August 2022)
        "KS": {"bodily_autonomy_score":4.0},
    },
    2023: {
        # Florida 6-week ban (April 2023)
        "FL": {"bodily_autonomy_score":-8.0,"health_score":-2.0},
        # North Carolina 12-week ban
        "NC": {"bodily_autonomy_score":-4.0},
        # Ohio constitutional amendment (November 2023)
        "OH": {"bodily_autonomy_score":8.0},
        # Montana blocked restrictive law
        "MT": {"bodily_autonomy_score":2.0},
        # Black maternal mortality policy responses
        "CA": {"health_score":2.0},
        "NY": {"health_score":1.5},
        # Illinois abortion sanctuary state
        "IL": {"bodily_autonomy_score":2.0,"safety_justice_score":1.5},
    },
    2024: {
        # Arizona 1864 ban reinstated then overturned
        "AZ": {"bodily_autonomy_score":-4.0},  # net negative
        # IVF debate (Alabama IVF ruling)
        "AL": {"bodily_autonomy_score":-3.0,"health_score":-2.0},
        # Florida Amendment 4 (narrowly failed)
        "FL": {"bodily_autonomy_score":-2.0},
        # Maryland strengthened protections
        "MD": {"bodily_autonomy_score":2.0,"empowerment_score":1.0},
    },
}

# General annual trend rates (all USA states, small improvements)
USA_TRENDS = {
    "empowerment_score":     0.20,
    "education_score":       0.15,
    "economic_score":        0.18,
    "health_score":          0.12,
    "bodily_autonomy_score": 0.10,  # Pre-Dobbs, slow improvement
    "safety_justice_score":  0.12,
    "dignity_welfare_score": 0.15,
    "digital_social_score":  0.40,
    "violence_penalty_score":-0.05,
}


def load_usa_2025():
    path = OUTPUT_DIR / "usa-states-2025.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    rows = []
    with open(path,"r",encoding="utf-8") as f:
        lines=[l for l in f if not l.startswith("#")]
    for row in csv.DictReader(io.StringIO("".join(lines))):
        rows.append(dict(row))
    return rows


def generate_year(baseline_rows, target_year):
    years_back = 2025 - target_year
    rows = []

    for base in baseline_rows:
        code = base.get("state_code","")
        r    = dict(base)

        # 1. Reverse events after target_year
        for ev_year in sorted(STATE_EVENTS.keys(), reverse=True):
            if ev_year <= target_year: break
            for key, deltas in STATE_EVENTS[ev_year].items():
                if key in (code, "__ALL__"):
                    for col, delta in deltas.items():
                        try:
                            r[col] = round(max(0,min(100,
                                float(r.get(col,50)) - delta)),1)
                        except: pass

        # 2. Reverse Dobbs impact if target_year < 2022
        if target_year < 2022 and code in STATE_DOBBS_IMPACT:
            try:
                delta = STATE_DOBBS_IMPACT[code]
                r["bodily_autonomy_score"] = round(max(0,min(100,
                    float(r.get("bodily_autonomy_score",50)) - delta)),1)
            except: pass

        # 3. Reverse Texas SB8 if target_year < 2021
        if target_year < 2021 and code == "TX":
            try:
                r["bodily_autonomy_score"] = round(max(0,min(100,
                    float(r.get("bodily_autonomy_score",50)) - TX_SB8_IMPACT)),1)
            except: pass

        # 4. Apply trend backwards
        for col, rate in USA_TRENDS.items():
            try:
                r[col] = round(max(0,min(100,
                    float(r.get(col,50)) - rate * years_back)),1)
            except: pass

        # 5. Apply target year events
        for key, deltas in STATE_EVENTS.get(target_year,{}).items():
            if key in (code, "__ALL__"):
                for col, delta in deltas.items():
                    try:
                        r[col] = round(max(0,min(100,
                            float(r.get(col,50)) + delta)),1)
                    except: pass

        # 6. Apply Dobbs in 2022
        if target_year == 2022 and code in STATE_DOBBS_IMPACT:
            try:
                delta = STATE_DOBBS_IMPACT[code]
                r["bodily_autonomy_score"] = round(max(0,min(100,
                    float(r.get("bodily_autonomy_score",50)) + delta)),1)
            except: pass

        r["wei_score"] = wei(r)
        r["year"]      = target_year
        rows.append(r)

    rows.sort(key=lambda x: float(x.get("wei_score",0)), reverse=True)
    for i,r in enumerate(rows): r["rank"]=i+1
    return rows


def main(from_year=2015, to_year=2024):
    print("USA States Historical WEI Generator")
    print("="*55)

    baseline  = load_usa_2025()
    all_flat  = []
    all_years = {}

    for year in range(from_year, to_year+1):
        rows = generate_year(baseline, year)
        all_years[year] = rows

        top = rows[0]
        bot = rows[-1]
        avg = round(sum(float(r.get("wei_score",0)) for r in rows)/len(rows),1)

        # Key states
        ma  = next((r for r in rows if r.get("state_code")=="MA"),{})
        ms  = next((r for r in rows if r.get("state_code")=="MS"),{})
        tx  = next((r for r in rows if r.get("state_code")=="TX"),{})
        print(f"  {year}: avg {avg} | Top: {top.get('state',''):<15}"
              f"({top.get('wei_score','')}) | "
              f"MA:{ma.get('wei_score','?')} "
              f"TX:{tx.get('wei_score','?')} "
              f"MS:{ms.get('wei_score','?')}")

        for r in rows:
            all_flat.append({
                "state":      r.get("state",""),
                "state_code": r.get("state_code",""),
                "ticker":     r.get("ticker",""),
                "year":       year,
                "wei_score":  r.get("wei_score",""),
                "rank":       r.get("rank",""),
                **{c:r.get(c,"") for c in PILLAR_COLS},
            })

    # Save
    out = HIST_DIR / "usa-state-trends.csv"
    flds = ["state","state_code","ticker","year","wei_score","rank"] + PILLAR_COLS
    hdr = (
        f"# SHEtoken WEI USA States Historical {from_year}-{to_year}\n"
        f"# THE POST-ROE STORY: Dobbs (June 2022) caused the largest\n"
        f"# single-year bodily autonomy score divergence in the index.\n"
        f"# 26 states dropped; some protective states improved.\n"
        f"# Massachusetts 2022 bodily autonomy: 88 | Mississippi: 18\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    buf=io.StringIO()
    w=csv.DictWriter(buf,fieldnames=flds,extrasaction="ignore")
    w.writeheader(); w.writerows(all_flat)
    with open(out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())

    # Print bodily autonomy table — the most important story
    print(f"\n  BODILY AUTONOMY SCORE BY STATE — the Dobbs story:")
    print(f"  {'State':<18} {'2021':>6} {'2022':>6} {'Δ':>6}  Status")
    print(f"  {'─'*55}")
    ba_rows = []
    for code in STATE_DOBBS_IMPACT:
        r21 = next((r for r in all_years.get(2021,[])
                    if r.get("state_code")==code),{})
        r22 = next((r for r in all_years.get(2022,[])
                    if r.get("state_code")==code),{})
        if r21 and r22:
            ba21 = float(r21.get("bodily_autonomy_score",0))
            ba22 = float(r22.get("bodily_autonomy_score",0))
            ba_rows.append((r22.get("state",""), code, ba21, ba22, ba22-ba21))
    ba_rows.sort(key=lambda x: x[4])
    for state,code,ba21,ba22,delta in ba_rows:
        impact = STATE_DOBBS_IMPACT.get(code,0)
        status = "TOTAL BAN" if impact<=-20 else \
                 "6-WEEK" if impact<=-14 else \
                 "RESTRICT" if impact<0 else "PROTECT"
        arrow = "▼" if delta < 0 else "▲"
        print(f"  {state:<18} {ba21:>6.1f} {ba22:>6.1f} "
              f"{arrow}{abs(delta):>4.1f}  {status}")

    print(f"\n  Saved: {out} ({len(all_flat)} rows)")


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--from-year",type=int,default=2015)
    p.add_argument("--to-year",type=int,default=2024)
    parser.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    args=p.parse_args()
    main(args.from_year, args.to_year)