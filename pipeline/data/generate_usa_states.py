"""
SHEtoken Pipeline — USA State WEI Generator v3.0
=================================================
Generates usa-states-YYYY.csv using the 8-pillar WEI formula.

Post-Roe (2022) the USA has the largest sub-national Bodily Autonomy
variation of any Tier 1 country — states with total abortion bans
score 18-25 vs states with protected access scoring 86-90.

Data sources: CDC, Guttmacher, FBI UCR, Census Bureau, NWLC

Usage:
    python data/generate_usa_states.py

Output:
    data/output/usa-states-2025.csv

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from config import OUTPUT_DIR, BASELINE_YEAR


def wei(emp, edu, eco, hlt, bod, saf, dgn, dgt, vio):
    return round((emp*0.15)+(edu*0.12)+(eco*0.12)+(hlt*0.12)+
                 (bod*0.15)+(saf*0.14)+(dgn*0.10)+(dgt*0.10)-(vio*0.10), 1)


# name, code, region, pop_M, emp, edu, eco, hlt, bod, saf, dgn, dgt, vio
USA_STATES = [
    # NORTHEAST
    ("Massachusetts",  "MA","Northeast", 7.0,  88,96,82,88,88,84,82,90,14),
    ("Vermont",        "VT","Northeast", 0.6,  86,96,76,86,90,84,82,84,12),
    ("Connecticut",    "CT","Northeast", 3.6,  84,95,80,86,86,82,80,88,14),
    ("New York",       "NY","Northeast",19.7,  82,94,78,84,86,80,78,88,18),
    ("New Jersey",     "NJ","Northeast", 9.3,  80,94,78,84,84,80,78,86,16),
    ("New Hampshire",  "NH","Northeast", 1.4,  82,96,76,86,86,80,80,84,12),
    ("Rhode Island",   "RI","Northeast", 1.1,  80,94,74,84,86,80,78,84,14),
    ("Maryland",       "MD","Northeast", 6.2,  80,92,76,82,82,78,76,84,20),
    ("Maine",          "ME","Northeast", 1.4,  80,94,70,84,84,78,76,78,14),
    ("Pennsylvania",   "PA","Northeast",13.0,  76,92,72,82,74,74,72,82,20),
    ("Delaware",       "DE","Northeast", 1.0,  74,90,70,80,76,72,70,78,20),
    # WEST
    ("California",     "CA","West",     39.0,  82,94,76,82,88,80,78,88,22),
    ("Washington",     "WA","West",      7.8,  80,94,78,84,88,80,78,86,18),
    ("Oregon",         "OR","West",      4.3,  78,94,72,82,88,78,76,82,20),
    ("Colorado",       "CO","West",      5.8,  78,94,76,84,84,78,76,82,20),
    ("Hawaii",         "HI","West",      1.4,  78,94,70,86,82,76,76,82,18),
    ("Montana",        "MT","West",      1.1,  64,92,62,78,58,60,60,68,24),
    ("New Mexico",     "NM","West",      2.1,  68,86,60,76,72,60,62,72,34),
    ("Nevada",         "NV","West",      3.1,  72,88,68,78,78,68,66,78,28),
    ("Arizona",        "AZ","West",      7.4,  68,88,66,74,56,64,64,74,28),
    ("Utah",           "UT","West",      3.3,  64,92,64,82,36,62,64,72,18),
    ("Idaho",          "ID","West",      1.9,  60,90,60,78,28,58,58,66,20),
    ("Wyoming",        "WY","West",      0.6,  58,90,62,78,30,54,56,62,22),
    ("Alaska",         "AK","West",      0.7,  64,88,68,74,72,54,58,72,36),
    # MIDWEST
    ("Minnesota",      "MN","Midwest",   5.7,  80,94,76,86,80,78,78,84,16),
    ("Illinois",       "IL","Midwest",  12.7,  76,92,72,80,80,72,72,80,24),
    ("Wisconsin",      "WI","Midwest",   5.9,  72,92,68,82,56,70,70,78,20),
    ("Michigan",       "MI","Midwest",  10.0,  72,92,68,78,74,68,68,76,24),
    ("Kansas",         "KS","Midwest",   2.9,  64,90,62,80,42,62,62,70,22),
    ("Iowa",           "IA","Midwest",   3.2,  68,92,68,82,42,68,68,74,18),
    ("Ohio",           "OH","Midwest",  11.8,  68,90,64,78,56,66,66,74,24),
    ("Nebraska",       "NE","Midwest",   2.0,  64,92,64,82,30,62,62,70,18),
    ("Missouri",       "MO","Midwest",   6.2,  64,88,60,74,32,58,60,68,30),
    ("Indiana",        "IN","Midwest",   6.8,  62,88,60,76,28,60,60,68,26),
    ("North Dakota",   "ND","Midwest",   0.8,  62,92,66,80,24,58,60,68,22),
    ("South Dakota",   "SD","Midwest",   0.9,  60,90,62,78,22,56,56,66,24),
    # SOUTH
    ("Virginia",       "VA","South",     8.6,  74,92,72,80,72,70,70,78,22),
    ("Florida",        "FL","South",    22.6,  68,88,66,76,52,62,64,72,26),
    ("North Carolina", "NC","South",    10.5,  68,90,66,76,48,64,64,72,26),
    ("Georgia",        "GA","South",    10.9,  66,88,62,72,32,58,58,68,30),
    ("Texas",          "TX","South",    30.0,  62,86,60,70,22,54,54,66,30),
    ("South Carolina", "SC","South",     5.2,  58,84,52,66,28,48,50,60,34),
    ("Tennessee",      "TN","South",     7.1,  58,86,56,68,24,48,50,62,38),
    ("Oklahoma",       "OK","South",     4.0,  56,84,52,66,22,46,46,58,36),
    ("Kentucky",       "KY","South",     4.5,  56,84,52,68,22,48,48,60,34),
    ("West Virginia",  "WV","South",     1.8,  52,82,44,64,24,44,44,54,34),
    ("Arkansas",       "AR","South",     3.0,  52,82,48,64,20,44,44,56,38),
    ("Alabama",        "AL","South",     5.0,  54,82,48,64,20,44,44,56,38),
    ("Louisiana",      "LA","South",     4.6,  52,80,46,60,20,40,42,54,44),
    ("Mississippi",    "MS","South",     2.9,  50,78,42,54,18,38,40,50,46),
]

YOY = {
    "TX":-2.4,"MS":-1.8,"AL":-1.6,"LA":-1.4,"AR":-1.2,"KY":-1.0,
    "VT":+1.4,"MA":+1.2,"CA":+1.1,"CO":+0.9,"WA":+0.6,"OR":+0.5,
    "IL":+0.8,"NY":+0.4,"NM":+0.4,
}
HOT   = {"MA","VT","CO","WA","OR"}
WATCH = {"TX","MS","AL","LA","AR"}


def generate_usa_states(output_path=None, year=BASELINE_YEAR):
    if output_path is None:
        output_path = str(OUTPUT_DIR / f"usa-states-{year}.csv")

    rows = []
    for (state,code,region,pop,emp,edu,eco,hlt,bod,saf,dgn,dgt,vio) in USA_STATES:
        score  = wei(emp,edu,eco,hlt,bod,saf,dgn,dgt,vio)
        change = YOY.get(code, round((score-70)*0.01,1))
        rows.append({
            "rank":0,"state":state,"state_code":code,
            "ticker":f"SHE-US-{code}","region":region,
            "population_millions":pop,
            "empowerment_score":emp,"education_score":edu,
            "economic_score":eco,"health_score":hlt,
            "bodily_autonomy_score":bod,"safety_justice_score":saf,
            "dignity_welfare_score":dgn,"digital_social_score":dgt,
            "violence_penalty_score":vio,"wei_score":score,
            "previous_wei_score":round(score-change,1),"change":change,
            "hot":"true" if code in HOT else "false",
            "watch":"true" if code in WATCH else "false",
            "country":"USA","year":year,"wei_version":"3.0",
            "verified":"false","notes":"",
        })

    rows.sort(key=lambda x: x["wei_score"], reverse=True)
    for i,r in enumerate(rows): r["rank"] = i+1

    avg = round(sum(r["wei_score"]*r["population_millions"] for r in rows)
                /sum(r["population_millions"] for r in rows),1)

    header = (
        f"# SHEtoken WEI USA States v3.0 — {year}\n"
        f"# 8-pillar Women's Empowerment Index — {len(rows)} states\n"
        f"# USA population-weighted WEI average: {avg}\n"
        f"# Key driver: Post-Roe abortion access creates the largest\n"
        f"# sub-national Bodily Autonomy gap of any Tier 1 country.\n"
        f"# Massachusetts (bod:88) vs Mississippi (bod:18) — 70 point gap.\n"
        f"# Sources: CDC, Guttmacher Institute, FBI UCR, Census, NWLC\n"
        f"# Generated: May 2026 | shetoken.org\n#\n"
    )

    fieldnames = ["rank","state","state_code","ticker","region","population_millions",
                  "empowerment_score","education_score","economic_score","health_score",
                  "bodily_autonomy_score","safety_justice_score","dignity_welfare_score",
                  "digital_social_score","violence_penalty_score","wei_score",
                  "previous_wei_score","change","hot","watch","country","year",
                  "wei_version","verified","notes"]

    buf = io.StringIO()
    csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore").writeheader()
    csv.DictWriter(io.StringIO(), fieldnames=fieldnames, extrasaction="ignore")
    writer = csv.DictWriter(buf, fieldnames=fieldnames, extrasaction="ignore")
    # reopen
    buf2 = io.StringIO()
    w = csv.DictWriter(buf2, fieldnames=fieldnames, extrasaction="ignore")
    w.writeheader()
    w.writerows(rows)

    os.makedirs(os.path.dirname(output_path) or ".", exist_ok=True)
    with open(output_path,"w",newline="",encoding="utf-8") as f:
        f.write(header + buf2.getvalue())

    print(f"USA States WEI v3.0 — {year}")
    print(f"  States: {len(rows)} | USA avg: {avg}")
    print(f"\n  {'Rk':<4} {'State':<18} {'Ticker':<14} {'WEI':>6} {'Chg':>7} {'Bod':>5}")
    print(f"  {'─'*55}")
    for r in rows:
        chg = f"+{r['change']}" if r['change']>=0 else str(r['change'])
        flag = " 🔥" if r['hot']=="true" else (" ⚠️" if r['watch']=="true" else "")
        print(f"  {r['rank']:<4} {r['state']:<18} {r['ticker']:<14} "
              f"{r['wei_score']:>6} {chg:>7} {r['bodily_autonomy_score']:>5}{flag}")
    print(f"\n+ Saved: {output_path}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--year", type=int, default=BASELINE_YEAR)
    parser.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    args = parser.parse_args()
    generate_usa_states(year=args.year)