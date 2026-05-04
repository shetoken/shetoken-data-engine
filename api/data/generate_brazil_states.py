"""SHEtoken — Brazil State WEI Generator v3.0"""
import csv,io,os,sys,argparse
sys.path.insert(0, os.path.join(os.path.dirname(__file__),'..'))
from config import OUTPUT_DIR, BASELINE_YEAR

def wei(e,ed,ec,h,b,s,d,dg,v):
    return round((e*.15)+(ed*.12)+(ec*.12)+(h*.12)+(b*.15)+(s*.14)+(d*.10)+(dg*.10)-(v*.10),1)

# state, code, region, pop_M, emp,edu,eco,hlt,bod,saf,dgn,dgt,vio
# Key: Femicide rates vary 4x. Maria da Penha law enforcement inconsistent.
# Para/Maranhao (north) = Tier 3 equivalent. Sao Paulo/RS = near Tier 2.
STATES = [
    ("Sao Paulo",        "SP","Southeast",  46.6, 62,86,64,80,68,58,60,70,42),
    ("Rio Grande do Sul","RS","South",      11.4, 64,86,62,80,68,60,62,68,38),
    ("Santa Catarina",   "SC","South",       7.7, 60,86,62,80,66,58,60,66,34),
    ("Minas Gerais",     "MG","Southeast",  21.3, 58,82,56,76,60,52,54,60,46),
    ("Parana",           "PR","South",      11.6, 58,84,58,78,62,56,58,64,40),
    ("Federal District", "DF","Center-West", 3.1, 68,90,66,82,68,60,62,72,36),
    ("Espirito Santo",   "ES","Southeast",   4.1, 58,82,56,76,60,54,56,62,48),
    ("Rio de Janeiro",   "RJ","Southeast",  17.4, 58,82,56,74,64,48,52,66,56),
    ("Goias",            "GO","Center-West", 7.2, 52,80,52,74,58,50,52,58,50),
    ("Mato Grosso do Sul","MS","Center-West",2.8, 52,80,50,74,56,50,50,56,52),
    ("Mato Grosso",      "MT","Center-West", 3.6, 50,78,50,72,54,48,48,52,54),
    ("Tocantins",        "TO","North",       1.6, 46,76,44,70,50,44,44,48,56),
    ("Rondonia",         "RO","North",       1.8, 46,76,44,70,48,44,44,46,56),
    ("Acre",             "AC","North",       0.9, 44,72,40,68,44,42,42,42,54),
    ("Roraima",          "RR","North",       0.6, 44,72,40,68,44,42,42,42,56),
    ("Amapa",            "AP","North",       0.9, 44,72,40,68,44,42,40,42,56),
    ("Amazonas",         "AM","North",       4.3, 44,72,38,68,44,40,40,42,56),
    ("Para",             "PA","North",       8.7, 42,70,38,66,40,38,38,40,58),
    ("Bahia",            "BA","Northeast",  14.9, 46,72,40,68,44,42,42,44,56),
    ("Ceara",            "CE","Northeast",   9.2, 46,74,40,68,44,42,42,44,54),
    ("Pernambuco",       "PE","Northeast",   9.6, 46,74,40,68,44,42,42,44,56),
    ("Rio Grande do Norte","RN","Northeast", 3.5, 48,74,40,68,46,44,42,46,54),
    ("Paraiba",          "PB","Northeast",   4.0, 46,72,38,66,44,42,40,44,54),
    ("Alagoas",          "AL","Northeast",   3.4, 42,68,36,64,40,38,38,40,62),
    ("Sergipe",          "SE","Northeast",   2.3, 44,72,38,66,42,40,40,42,58),
    ("Piaui",            "PI","Northeast",   3.3, 44,70,36,66,42,40,38,40,56),
    ("Maranhao",         "MA","Northeast",   7.2, 40,66,34,62,36,36,34,36,62),
]

YOY = {"SP":+0.8,"RS":+0.4,"RJ":-0.6,"PA":-0.4,"MA":-0.2,"DF":+0.5}
HOT = {"SP","RS","SC"}
WATCH = {"RJ","PA","MA","AL"}

def run(out=None, year=BASELINE_YEAR):
    if out is None: out = str(OUTPUT_DIR/f"brazil-states-{year}.csv")
    rows = []
    for (st,co,reg,pop,e,ed,ec,h,b,s,d,dg,v) in STATES:
        score = wei(e,ed,ec,h,b,s,d,dg,v)
        chg   = YOY.get(co, round((score-50)*0.01,1))
        rows.append({"rank":0,"state":st,"state_code":co,"ticker":f"SHE-BR-{co}",
            "region":reg,"population_millions":pop,
            "empowerment_score":e,"education_score":ed,"economic_score":ec,
            "health_score":h,"bodily_autonomy_score":b,"safety_justice_score":s,
            "dignity_welfare_score":d,"digital_social_score":dg,
            "violence_penalty_score":v,"wei_score":score,
            "previous_wei_score":round(score-chg,1),"change":chg,
            "hot":"true" if co in HOT else "false",
            "watch":"true" if co in WATCH else "false",
            "country":"Brazil","year":year,"wei_version":"3.0","verified":"false","notes":""})
    rows.sort(key=lambda x:x["wei_score"],reverse=True)
    for i,r in enumerate(rows): r["rank"]=i+1
    avg = round(sum(r["wei_score"]*r["population_millions"] for r in rows)/sum(r["population_millions"] for r in rows),1)
    hdr = (f"# SHEtoken WEI Brazil States v3.0 — {year}\n"
           f"# {len(rows)} states | Brazil avg WEI: {avg}\n"
           f"# Key: Femicide rates vary 4x between states. Maria da Penha\n"
           f"# law enforcement highly inconsistent. North vs South gap.\n"
           f"# Sources: IBGE, SSP state secretariats, Ministerio da Saude\n#\n")
    flds = ["rank","state","state_code","ticker","region","population_millions",
            "empowerment_score","education_score","economic_score","health_score",
            "bodily_autonomy_score","safety_justice_score","dignity_welfare_score",
            "digital_social_score","violence_penalty_score","wei_score",
            "previous_wei_score","change","hot","watch","country","year","wei_version","verified","notes"]
    buf = io.StringIO()
    w = csv.DictWriter(buf,fieldnames=flds,extrasaction="ignore"); w.writeheader(); w.writerows(rows)
    os.makedirs(os.path.dirname(out) or ".",exist_ok=True)
    with open(out,"w",newline="",encoding="utf-8") as f: f.write(hdr+buf.getvalue())
    print(f"Brazil States: {len(rows)} states | avg WEI {avg}\n+ Saved: {out}")

if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("--year",type=int,default=BASELINE_YEAR)
    run(year=p.parse_args().year)
