"""SHEtoken — Pakistan Province WEI Generator v3.0
Punjab vs Balochistan = one of world's most extreme sub-national gaps.
Balochistan: child marriage 36%, honour killings, extreme female illiteracy.
"""
import csv,io,os,sys,argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..'))
from config import OUTPUT_DIR, BASELINE_YEAR

def wei(e,ed,ec,h,b,s,d,dg,v):
    return round((e*.15)+(ed*.12)+(ec*.12)+(h*.12)+(b*.15)+(s*.14)+(d*.10)+(dg*.10)-(v*.10),1)

PROVINCES = [
    # province, code, pop_M, emp,edu,eco,hlt,bod,saf,dgn,dgt,vio
    ("Islamabad (ICT)",   "ICT", 2.4, 40,72,40,72,32,30,34,46,30),
    ("Punjab",            "PJ", 110.0,28,56,30,66,20,24,22,26,42),
    ("Sindh",             "SI",  55.7,26,52,28,62,16,22,20,22,44),
    ("Khyber Pakhtunkhwa","KP",  40.5,18,44,22,58,12,16,14,14,44),
    ("Balochistan",       "BL",  14.9,12,30,16,48, 8,10, 8, 8,46),
    ("Gilgit-Baltistan",  "GB",   2.4,14,46,18,56,10,12,10,10,40),
    ("Azad Kashmir",      "AK",   4.6,18,52,20,60,14,14,12,14,38),
]

YOY={"ICT":+0.3,"PJ":+0.1,"BL":-0.2}
HOT=set(); WATCH={"BL","KP"}

def run(out=None,year=BASELINE_YEAR):
    if out is None: out=str(OUTPUT_DIR/f"pakistan-provinces-{year}.csv")
    rows=[]
    for (st,co,pop,e,ed,ec,h,b,s,d,dg,v) in PROVINCES:
        score=wei(e,ed,ec,h,b,s,d,dg,v); chg=YOY.get(co,0.0)
        rows.append({"rank":0,"province":st,"province_code":co,"ticker":f"SHE-PK-{co}",
            "population_millions":pop,
            "empowerment_score":e,"education_score":ed,"economic_score":ec,
            "health_score":h,"bodily_autonomy_score":b,"safety_justice_score":s,
            "dignity_welfare_score":d,"digital_social_score":dg,
            "violence_penalty_score":v,"wei_score":score,
            "previous_wei_score":round(score-chg,1),"change":chg,
            "watch":"true" if co in WATCH else "false",
            "country":"Pakistan","year":year,"wei_version":"3.0","verified":"false",
            "notes":"Balochistan: female literacy 20%, honour killings, extreme child marriage"})
    rows.sort(key=lambda x:x["wei_score"],reverse=True)
    for i,r in enumerate(rows): r["rank"]=i+1
    avg=round(sum(r["wei_score"]*r["population_millions"] for r in rows)/sum(r["population_millions"] for r in rows),1)
    hdr=(f"# SHEtoken WEI Pakistan Provinces v3.0 — {year}\n"
         f"# {len(rows)} provinces | Pakistan avg WEI: {avg}\n"
         f"# Islamabad vs Balochistan = 25+ point WEI gap\n"
         f"# Honour killings: 1000+ reported annually (HRCP)\n"
         f"# Sources: PBS Pakistan, PDHS, HRCP, UNESCO\n#\n")
    flds=["rank","province","province_code","ticker","population_millions",
          "empowerment_score","education_score","economic_score","health_score",
          "bodily_autonomy_score","safety_justice_score","dignity_welfare_score",
          "digital_social_score","violence_penalty_score","wei_score",
          "previous_wei_score","change","watch","country","year","wei_version","verified","notes"]
    buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=flds,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    os.makedirs(os.path.dirname(out) or ".",exist_ok=True)
    with open(out,"w",newline="",encoding="utf-8") as f: f.write(hdr+buf.getvalue())
    print(f"Pakistan Provinces: {len(rows)} | avg WEI {avg}\n+ Saved: {out}")

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--year",type=int,default=BASELINE_YEAR)
    parser.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    run(year=p.parse_args().year)