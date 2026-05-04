"""
SHEtoken — Top 20 Cities Historical WEI (2015-2024)
=====================================================
Historical WEI scores for the 20 most significant cities.

City selection: highest population + most data available.
  Mumbai, Delhi, Kochi, Bengaluru, Kolkata (India)
  New York, Los Angeles, Jackson MS (USA)
  London, Berlin, Oslo (Europe)
  São Paulo, Rio de Janeiro (Brazil)
  Lagos, Nairobi, Johannesburg (Africa)
  Mexico City (Mexico)
  Karachi, Dhaka (South Asia)
  Tokyo (Japan)

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, argparse
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

HIST_DIR = OUTPUT_DIR / "historical"
HIST_DIR.mkdir(parents=True, exist_ok=True)

TOP_20_SLUGS = [
    "mumbai","delhi","kochi","bengaluru","kolkata",
    "new-york","los-angeles","jackson-ms",
    "london","berlin","oslo",
    "sao-paulo","rio",
    "lagos","nairobi","johannesburg",
    "mexico-city","karachi","dhaka","tokyo",
]

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


# City-specific events
CITY_EVENTS = {
    2012: {
        # Delhi gang rape December 2012 — immediate aftermath into 2013
        "delhi": {"safety_justice_score":-4.0,"empowerment_score":2.0},
    },
    2013: {
        # India Criminal Law Amendment Act (post-Nirbhaya)
        "delhi":    {"safety_justice_score":3.0,"legal awareness":0},
        "mumbai":   {"safety_justice_score":1.5},
        "bengaluru":{"safety_justice_score":1.5},
    },
    2015: {
        # India POCSO enforcement begins
        "delhi":   {"safety_justice_score":1.0},
        "mumbai":  {"safety_justice_score":1.0},
    },
    2016: {
        # Nigeria — Lagos relatively stable, Kano troubles
        "lagos": {"safety_justice_score":1.0,"economic_score":0.5},
    },
    2017: {
        # MeToo effect — cities with strong media presence
        "new-york":   {"safety_justice_score":2.0,"empowerment_score":1.5},
        "los-angeles":{"safety_justice_score":2.0,"empowerment_score":1.5},
        "london":     {"safety_justice_score":1.5,"empowerment_score":1.0},
        "berlin":     {"safety_justice_score":1.5},
        "tokyo":      {"safety_justice_score":0.5},  # minimal Japan MeToo
        "mumbai":     {"safety_justice_score":1.0},
    },
    2018: {
        # Sabarimala temple verdict — women's access (India)
        "kochi":   {"empowerment_score":2.0,"bodily_autonomy_score":1.5},
        # Berlin anti-femicide initiatives
        "berlin":  {"safety_justice_score":1.5},
        # Brazil — femicide law enforcement
        "sao-paulo":{"safety_justice_score":1.0},
        "rio":      {"safety_justice_score":0.5},
    },
    2019: {
        # Mexico City feminist emergency declared
        "mexico-city":{"safety_justice_score":-2.0,"empowerment_score":3.0},
        # Delhi metro women's coaches, safety
        "delhi":  {"safety_justice_score":1.0,"digital_social_score":1.0},
        # Nairobi DV shelter expansion
        "nairobi":{"safety_justice_score":1.0},
    },
    2020: {
        # COVID global DV spike
        "__ALL__": {
            "safety_justice_score":-2.5,
            "economic_score":-2.5,
            "health_score":-1.5,
            "dignity_welfare_score":-2.0,
        },
        # Mumbai — healthcare
        "mumbai":   {"health_score":-2.0},
        "delhi":    {"health_score":-2.0,"safety_justice_score":-1.5},
        # São Paulo — favela DV spike
        "sao-paulo":{"safety_justice_score":-2.0},
        "rio":      {"safety_justice_score":-2.5},
    },
    2021: {
        # COVID recovery — cities recover faster than rural
        "__ALL__": {
            "economic_score":2.0,
            "health_score":1.0,
        },
        # West Bengal — Lakshmi Bhandar helps Kolkata women
        "kolkata":  {"dignity_welfare_score":3.0,"economic_score":2.0},
        # Oslo — ranked world's safest city for women
        "oslo":     {"safety_justice_score":1.5,"empowerment_score":1.0},
        # Lagos — women's enterprise hub growing
        "lagos":    {"economic_score":1.5},
        # Sarah Everard case — London safety awareness
        "london":   {"safety_justice_score":-1.0,"empowerment_score":2.0},
    },
    2022: {
        # USA cities — Dobbs impact
        "new-york":    {"bodily_autonomy_score":4.0},  # NY strengthened rights
        "los-angeles": {"bodily_autonomy_score":3.0},  # CA strengthened
        "jackson-ms":  {"bodily_autonomy_score":-18.0, # Mississippi total ban
                        "health_score":-3.0},
        # Mexico City — feminist emergency ongoing
        "mexico-city": {"safety_justice_score":-1.0,"empowerment_score":1.5},
        # Karachi — floods disproportionately affected women
        "karachi":     {"dignity_welfare_score":-2.0,"health_score":-1.5},
        # Berlin — Ukraine refugee women support
        "berlin":      {"dignity_welfare_score":1.0},
        # Johannesburg femicide rate worsens
        "johannesburg":{"violence_penalty_score":3.0,"safety_justice_score":-1.5},
    },
    2023: {
        # Delhi — violence against women cases rising
        "delhi":   {"safety_justice_score":-1.5,"violence_penalty_score":1.5},
        # Mumbai — SafeCity improvements
        "mumbai":  {"safety_justice_score":1.0,"digital_social_score":1.5},
        # Tokyo — Japan consent-based rape law reform
        "tokyo":   {"safety_justice_score":2.0,"bodily_autonomy_score":1.5},
        # Nairobi — women's economic programs
        "nairobi": {"economic_score":1.5},
        # Oslo continues best performer
        "oslo":    {"safety_justice_score":0.5},
        # Jackson MS — continued healthcare crisis
        "jackson-ms":{"health_score":-2.0,"dignity_welfare_score":-1.5},
    },
    2024: {
        # Global digital access improving fast
        "__ALL__": {"digital_social_score":1.5},
        # Mumbai — women in fintech/startup growing
        "mumbai":   {"economic_score":1.5,"digital_social_score":2.0},
        # Bengaluru — tech hub women's employment
        "bengaluru":{"economic_score":2.0,"digital_social_score":2.0},
        # Mexico City — first female mayor continues
        "mexico-city":{"empowerment_score":2.0},
        # Delhi — continued challenges
        "delhi":    {"safety_justice_score":-1.0},
    },
}

# Annual trend rates for cities
CITY_TRENDS = {
    "empowerment_score":     0.15,
    "education_score":       0.20,
    "economic_score":        0.18,
    "health_score":          0.15,
    "bodily_autonomy_score": 0.12,
    "safety_justice_score":  0.10,
    "dignity_welfare_score": 0.15,
    "digital_social_score":  0.45,
    "violence_penalty_score":-0.05,
}


def load_cities_2025():
    path = OUTPUT_DIR / "city-scores-2025.csv"
    if not path.exists():
        raise FileNotFoundError(f"Missing: {path}")
    rows = []
    with open(path,"r",encoding="utf-8") as f:
        lines=[l for l in f if not l.startswith("#")]
    for row in csv.DictReader(io.StringIO("".join(lines))):
        if row.get("slug","") in TOP_20_SLUGS:
            rows.append(dict(row))
    return rows


def generate_year(baseline_rows, target_year):
    years_back = 2025 - target_year
    rows = []
    for base in baseline_rows:
        slug = base.get("slug","")
        r    = dict(base)

        # 1. Reverse events after target year
        for ev_year in sorted(CITY_EVENTS.keys(), reverse=True):
            if ev_year <= target_year: break
            for key, deltas in CITY_EVENTS[ev_year].items():
                if key in (slug,"__ALL__"):
                    for col,delta in deltas.items():
                        if col in PILLAR_COLS:
                            try:
                                r[col]=round(max(0,min(100,
                                    float(r.get(col,50))-delta)),1)
                            except: pass

        # 2. Trend backwards
        for col,rate in CITY_TRENDS.items():
            try:
                r[col]=round(max(0,min(100,
                    float(r.get(col,50))-rate*years_back)),1)
            except: pass

        # 3. Apply target year events
        for key,deltas in CITY_EVENTS.get(target_year,{}).items():
            if key in (slug,"__ALL__"):
                for col,delta in deltas.items():
                    if col in PILLAR_COLS:
                        try:
                            r[col]=round(max(0,min(100,
                                float(r.get(col,50))+delta)),1)
                        except: pass

        r["wei_score"] = wei(r)
        r["year"]      = target_year
        rows.append(r)

    rows.sort(key=lambda x: float(x.get("wei_score",0)), reverse=True)
    for i,r in enumerate(rows): r["rank"]=i+1
    return rows


def main(from_year=2015, to_year=2024):
    print("Top 20 Cities Historical WEI Generator")
    print("="*55)

    baseline  = load_cities_2025()
    print(f"  Cities loaded: {len(baseline)}")

    all_flat  = []
    all_years = {}

    for year in range(from_year, to_year+1):
        rows = generate_year(baseline, year)
        all_years[year] = rows

        oslo  = next((r for r in rows if r.get("slug")=="oslo"),{})
        delhi = next((r for r in rows if r.get("slug")=="delhi"),{})
        jxms  = next((r for r in rows if r.get("slug")=="jackson-ms"),{})
        print(f"  {year}: Oslo:{oslo.get('wei_score','?'):>5} "
              f"Delhi:{delhi.get('wei_score','?'):>5} "
              f"JacksonMS:{jxms.get('wei_score','?'):>5}")

        for r in rows:
            all_flat.append({
                "city":       r.get("city",""),
                "slug":       r.get("slug",""),
                "country_iso":r.get("country_iso",""),
                "ticker":     r.get("ticker",""),
                "year":       year,
                "wei_score":  r.get("wei_score",""),
                "rank":       r.get("rank",""),
                **{c:r.get(c,"") for c in PILLAR_COLS},
            })

    out = HIST_DIR / "city-trends-top20.csv"
    flds = ["city","slug","country_iso","ticker","year","wei_score","rank"]+PILLAR_COLS
    hdr = (
        f"# SHEtoken WEI City Historical Trends {from_year}-{to_year}\n"
        f"# Top 20 cities by population and data availability\n"
        f"# Key events: Delhi 2012/13 rape law reform, COVID 2020,\n"
        f"#   Jackson MS Dobbs 2022 (-18 bodily autonomy),\n"
        f"#   Kolkata Lakshmi Bhandar 2021, Mexico City feminist emergency 2019\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    buf=io.StringIO()
    w=csv.DictWriter(buf,fieldnames=flds,extrasaction="ignore")
    w.writeheader(); w.writerows(all_flat)
    with open(out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())

    # Notable comparison
    print(f"\n  Jackson MS bodily autonomy: 2021→2022")
    r21=next((r for r in all_years.get(2021,[]) if r.get("slug")=="jackson-ms"),{})
    r22=next((r for r in all_years.get(2022,[]) if r.get("slug")=="jackson-ms"),{})
    print(f"    2021: {r21.get('bodily_autonomy_score','?')} → "
          f"2022: {r22.get('bodily_autonomy_score','?')}")
    print(f"\n  Saved: {out} ({len(all_flat)} rows)")


if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--from-year",type=int,default=2015)
    p.add_argument("--to-year",type=int,default=2024)
    p.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    args=p.parse_args()
    main(args.from_year, args.to_year)