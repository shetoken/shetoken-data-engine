"""SHEtoken — Mexico State WEI Generator v3.0
8 states declared feminist emergency for femicide.
Highest femicide rates: Colima, Guerrero, Morelos.
Lowest: Yucatan, Hidalgo, Chiapas (despite poverty).
"""
import csv,io,os,sys,argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..'))
from config import OUTPUT_DIR, BASELINE_YEAR

def wei(e,ed,ec,h,b,s,d,dg,v):
    return round((e*.15)+(ed*.12)+(ec*.12)+(h*.12)+(b*.15)+(s*.14)+(d*.10)+(dg*.10)-(v*.10),1)

STATES = [
    # state, code, region, pop_M, emp,edu,eco,hlt,bod,saf,dgn,dgt,vio
    ("Mexico City",    "CDMX","Center",  9.2,  68,88,64,80,72,62,64,76,38),
    ("Nuevo Leon",     "NL",  "North",   5.8,  62,86,64,78,62,58,60,70,36),
    ("Jalisco",        "JA",  "West",    8.4,  58,84,58,76,60,54,58,64,42),
    ("Yucatan",        "YU",  "South",   2.3,  52,80,52,74,60,56,58,58,28),
    ("Coahuila",       "CO",  "North",   3.2,  58,84,58,76,58,52,56,62,38),
    ("Sonora",         "SO",  "North",   3.1,  56,82,56,74,56,50,54,60,40),
    ("Baja California","BC",  "North",   3.8,  52,80,54,72,54,48,52,58,42),
    ("Chihuahua",      "CH",  "North",   3.8,  52,80,52,72,52,44,50,56,48),
    ("San Luis Potosi","SL",  "Center",  2.8,  48,78,48,72,52,48,50,54,40),
    ("Aguascalientes", "AG",  "Center",  1.4,  52,82,52,74,54,50,52,58,36),
    ("Queretaro",      "QT",  "Center",  2.4,  52,82,54,76,54,52,54,60,34),
    ("Hidalgo",        "HI",  "Center",  3.1,  46,76,44,70,54,50,50,50,28),
    ("Tlaxcala",       "TL",  "Center",  1.4,  48,78,44,70,52,46,48,50,36),
    ("Tabasco",        "TB",  "South",   2.4,  46,76,42,68,50,44,46,48,42),
    ("Campeche",       "CM",  "South",   1.0,  46,76,44,70,50,48,48,50,34),
    ("Veracruz",       "VE",  "Gulf",    8.1,  44,74,42,68,48,42,44,46,48),
    ("Puebla",         "PU",  "Center",  6.6,  44,74,42,68,48,42,44,46,46),
    ("Estado de Mexico","ME", "Center", 17.4,  44,74,44,68,48,40,44,48,50),
    ("Michoacan",      "MI",  "West",    4.7,  42,72,40,66,44,38,40,42,54),
    ("Tamaulipas",     "TM",  "North",   3.6,  44,74,46,68,46,36,42,46,58),
    ("Sinaloa",        "SI",  "North",   3.0,  44,74,44,68,46,36,40,44,58),
    ("Zacatecas",      "ZA",  "North",   1.6,  42,72,40,66,44,36,40,40,52),
    ("Nayarit",        "NA",  "West",    1.2,  44,74,42,68,46,40,42,44,46),
    ("Durango",        "DU",  "North",   1.8,  42,72,40,66,44,38,40,40,50),
    ("Oaxaca",         "OA",  "South",   4.1,  38,68,34,62,44,38,38,36,46),
    ("Chiapas",        "CS",  "South",   5.7,  34,64,30,60,40,38,36,32,42),
    ("Guerrero",       "GR",  "South",   3.6,  34,64,30,56,36,28,32,30,66),
    ("Morelos",        "MO",  "Center",  2.0,  42,74,42,68,46,32,40,44,64),
    ("Colima",         "CL",  "West",    0.8,  42,74,44,70,46,30,40,46,70),
    ("Quintana Roo",   "QR",  "South",   1.9,  46,76,46,70,50,40,44,52,48),
    ("Baja California Sur","BS","North",  0.8,  48,78,48,72,52,44,48,54,44),
]

YOY = {"CDMX":+0.6,"NL":+0.4,"GR":-0.8,"MO":-0.6,"CL":-1.0,"YU":+0.5}
HOT = {"CDMX","YU","QT"}
WATCH = {"GR","MO","CL","CH","TM"}

def run(out=None, year=BASELINE_YEAR):
    if out is None: out = str(OUTPUT_DIR/f"mexico-states-{year}.csv")
    rows = []
    for (st,co,reg,pop,e,ed,ec,h,b,s,d,dg,v) in STATES:
        score=wei(e,ed,ec,h,b,s,d,dg,v); chg=YOY.get(co,0.0)
        rows.append({"rank":0,"state":st,"state_code":co,"ticker":f"SHE-MX-{co}",
            "region":reg,"population_millions":pop,
            "empowerment_score":e,"education_score":ed,"economic_score":ec,
            "health_score":h,"bodily_autonomy_score":b,"safety_justice_score":s,
            "dignity_welfare_score":d,"digital_social_score":dg,
            "violence_penalty_score":v,"wei_score":score,
            "previous_wei_score":round(score-chg,1),"change":chg,
            "hot":"true" if co in HOT else "false",
            "watch":"true" if co in WATCH else "false",
            "feminist_emergency":"true" if co in {"MO","GR","VE","BCS","ZA","ME","CDMX","SL"} else "false",
            "country":"Mexico","year":year,"wei_version":"3.0","verified":"false","notes":""})
    rows.sort(key=lambda x:x["wei_score"],reverse=True)
    for i,r in enumerate(rows): r["rank"]=i+1
    avg=round(sum(r["wei_score"]*r["population_millions"] for r in rows)/sum(r["population_millions"] for r in rows),1)
    hdr=(f"# SHEtoken WEI Mexico States v3.0 — {year}\n"
         f"# {len(rows)} states | Mexico avg WEI: {avg}\n"
         f"# 8 states declared Alerta de Genero (Feminist Emergency) for femicide\n"
         f"# Colima has Mexico's highest femicide rate. Yucatan lowest.\n"
         f"# Sources: INEGI, SESNSP, Secretaria de Salud, IMSS\n#\n")
    flds=["rank","state","state_code","ticker","region","population_millions",
          "empowerment_score","education_score","economic_score","health_score",
          "bodily_autonomy_score","safety_justice_score","dignity_welfare_score",
          "digital_social_score","violence_penalty_score","wei_score",
          "previous_wei_score","change","hot","watch","feminist_emergency",
          "country","year","wei_version","verified","notes"]
    buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=flds,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    os.makedirs(os.path.dirname(out) or ".",exist_ok=True)
    with open(out,"w",newline="",encoding="utf-8") as f: f.write(hdr+buf.getvalue())
    print(f"Mexico States: {len(rows)} states | avg WEI {avg}\n+ Saved: {out}")

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--year",type=int,default=BASELINE_YEAR)
    run(year=p.parse_args().year)
