"""
SHEtoken — Women's Rights Business Compliance Score (WRBCS)
============================================================
A due diligence tool answering one question:

  "Should our company outsource to, invest in, or do
   business with this country or US state?"

Five ratings:
  ✅ PREFERRED  — actively prioritise
  🟢 ACCEPTABLE — standard due diligence
  🟡 CAUTION    — enhanced obligations required
  🔴 AVOID      — do not initiate new contracts
  ⛔ EMBARGO    — exit existing operations

Based on: WEI + GPI + SVI + WADI composite score
Updated:  Annually (annual data) + weekly (signal alerts)

Legal basis this score enforces:
  UN Guiding Principles on Business & Human Rights (UNGP)
  EU Corporate Sustainability Due Diligence Directive (CS3D)
  US Trafficking Victims Protection Act (supply chain)
  UK Modern Slavery Act 2015
  California Transparency in Supply Chains Act
  Uyghur Forced Labor Prevention Act (model for women's rights)

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, json
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

# ── RATING SYSTEM ─────────────────────────────────────────────────────────────

RATINGS = {
    "PREFERRED": {
        "score_min": 75,
        "symbol":    "✅",
        "colour":    "#C9A84C",
        "headline":  "Actively prioritise for outsourcing and investment",
        "what_it_means": (
            "Strong women's rights environment. Outsourcing here supports "
            "gender equality. Publish as a positive supply chain decision."
        ),
        "required_actions": [
            "Standard supplier code of conduct",
            "Annual WEI monitoring",
            "Publish in ESG report as positive example",
        ],
    },
    "ACCEPTABLE": {
        "score_min": 55,
        "symbol":    "🟢",
        "headline":  "Acceptable with standard due diligence",
        "colour":    "#1A6B34",
        "what_it_means": (
            "Adequate women's rights environment with improvement trajectory. "
            "Most responsible outsourcing decisions are defensible here."
        ),
        "required_actions": [
            "Supplier code of conduct covering gender equality",
            "Biennial audit of female workforce conditions",
            "Monitor WEI signal alerts",
        ],
    },
    "CAUTION": {
        "score_min": 35,
        "symbol":    "🟡",
        "headline":  "Proceed with enhanced obligations",
        "colour":    "#E07B00",
        "what_it_means": (
            "Significant women's rights gaps. Outsourcing here carries "
            "reputational, legal, and human rights risk. Enhanced due "
            "diligence required before signing any new contracts."
        ),
        "required_actions": [
            "Human Rights Impact Assessment before any new contract",
            "Annual third-party gender audit of all suppliers",
            "Fund local women's NGO partner (min 0.5% of contract value)",
            "Board-level sign-off on new outsourcing decisions",
            "Require supplier to publish female workforce data",
            "Include women's rights clauses in all contracts",
            "Provide female workers direct grievance access (shetoken.org/signal)",
        ],
    },
    "AVOID": {
        "score_min": 20,
        "symbol":    "🔴",
        "headline":  "Do not initiate new business — review existing",
        "colour":    "#8B0000",
        "what_it_means": (
            "Serious and systemic women's rights violations. New outsourcing "
            "contracts are indefensible under UNGP and CS3D. Existing "
            "relationships require immediate remediation review."
        ),
        "required_actions": [
            "CEO/Board approval required for any new contract",
            "Immediate audit of existing supplier female workforce conditions",
            "Set 18-month remediation timeline with measurable WEI targets",
            "If no improvement: exit plan required",
            "Disclose in Modern Slavery Act statement",
            "Do not expand existing relationships",
        ],
    },
    "EMBARGO": {
        "score_min": 0,
        "symbol":    "⛔",
        "headline":  "Exit existing operations — no new business",
        "colour":    "#1A0A12",
        "what_it_means": (
            "Active crisis, armed conflict SGBV, or fundamental denial "
            "of women's basic rights. No responsible business justification "
            "exists. Continuation violates UNGP Article 19."
        ),
        "required_actions": [
            "No new contracts under any circumstances",
            "Board-mandated exit strategy for existing operations",
            "Report under UNGP Pillar III (access to remedy)",
            "Disclose in annual report",
            "Support affected women workers through transition fund",
        ],
    },
}


def get_rating(score: float) -> dict:
    for key in ["PREFERRED","ACCEPTABLE","CAUTION","AVOID","EMBARGO"]:
        if score >= RATINGS[key]["score_min"]:
            return {"code": key, **RATINGS[key]}
    return {"code": "EMBARGO", **RATINGS["EMBARGO"]}


def composite_score(wei, gpi=None, svi=None, wadi=None):
    """
    Composite Women's Rights Business Compliance Score.
    WEI 40%, SVI 25%, GPI 20%, WADI 15% (inverted — higher WADI = worse)
    """
    total, weight = wei * 0.40, 0.40
    if svi  is not None: total += svi  * 0.25; weight += 0.25
    if gpi  is not None: total += gpi  * 0.20; weight += 0.20
    if wadi is not None: total += (100-wadi)*0.15; weight += 0.15
    return round(total / weight, 1) if weight else round(wei, 1)


# ── COUNTRY DATA ──────────────────────────────────────────────────────────────
# Drawn from generated indexes. Key outsourcing destinations prioritised.
# country, iso, region,
# wei, gpi, svi, wadi,
# main_outsourcing_sectors,
# key_risk,
# ngos_to_fund

COUNTRIES = [
    # ── TIER 1 — Preferred outsourcing destinations ──────────────────────────
    ("Iceland",      "ISL","Europe",       93, 91, 81, 18,
     "Tech, finance, creative",
     "None significant",
     "UN Women Iceland"),
    ("Norway",       "NOR","Europe",       92, 90, 81, 22,
     "Oil & gas services, tech, maritime",
     "None significant",
     "Plan International Norway"),
    ("Sweden",       "SWE","Europe",       91, 91, 79, 24,
     "Tech, manufacturing, design, finance",
     "Gender pay gap still 7%",
     "UN Women Sweden"),
    ("Germany",      "DEU","Europe",       84, 85, 73, 34,
     "Manufacturing, engineering, tech, automotive",
     "East-West wage gap. Admin automation risk.",
     "Terre des Femmes"),
    ("Canada",       "CAN","N. America",   82, 85, 67, 30,
     "Tech, finance, healthcare, creative",
     "Indigenous women face compounded risk — audit needed for remote ops",
     "Native Women's Association of Canada"),
    ("Australia",    "AUS","Oceania",      81, 82, 70, 32,
     "Tech, mining services, financial services",
     "Indigenous women vulnerability — disclose in Modern Slavery statement",
     "Our Watch Australia"),
    ("UK",           "GBR","Europe",       80, 78, 68, 36,
     "Finance, tech, creative, professional services",
     "Gender pay gap reporting law exists but enforcement weak",
     "Fawcett Society"),
    ("Japan",        "JPN","East Asia",    76, 77, 48, 38,
     "Manufacturing, tech, automotive, electronics",
     "Women in admin face high automation risk. 'Shufu' system limits careers.",
     "Japan Women's Network for Policy Change"),
    ("South Korea",  "KOR","East Asia",    74, 74, 61, 38,
     "Electronics, automotive, shipbuilding, K-industry",
     "High gender wage gap 30%. Women in textiles face automation.",
     "Korean Women's Development Institute"),
    ("Brazil",       "BRA","S. America",   62, 62, 51, 48,
     "Agriculture, mining, manufacturing, IT services",
     "Femicide rate high. Domestic workers (5.7M women) largely unprotected.",
     "Agencia Patricia Galvao, CEPIA"),
    ("Mexico",       "MEX","N. America",   60, 58, 42, 56,
     "Manufacturing (maquiladora), automotive, agriculture, nearshoring",
     "CRITICAL: Feminist emergency. 11 women killed daily. "
     "Maquiladora female workers face dual automation + violence risk.",
     "CIMAC Noticias, Red Mesa de Mujeres"),
    ("South Africa", "ZAF","Africa",       58, 52, 43, 52,
     "Mining services, financial services, agriculture, BPO",
     "World's highest femicide rate. Domestic workers unprotected.",
     "Sonke Gender Justice, People Opposing Women Abuse"),
    ("China",        "CHN","East Asia",    56, 62, 32, 48,
     "Electronics, garment, manufacturing, tech services",
     "Factory automation displacing women workers. Limited union rights.",
     "China Labour Bulletin (Hong Kong based)"),
    ("Philippines",  "PHL","SE Asia",      54, 55, 50, 58,
     "BPO/call centres, garment, electronics assembly, domestic workers",
     "CRITICAL: 1.3M women in BPO — 79% automation risk. "
     "Overseas domestic workers face exploitation.",
     "GABRIELA, Center for Women's Resources"),
    ("Vietnam",      "VNM","SE Asia",      52, 54, 38, 64,
     "Garment, electronics, footwear, furniture",
     "HIGH: 2.8M women in garment/electronics. Nike, Samsung automation.",
     "CARE Vietnam, ActionAid Vietnam"),
    ("Indonesia",    "IDN","SE Asia",      50, 48, 33, 66,
     "Garment, palm oil, electronics, domestic workers export",
     "HIGH: Marital rape legal. Garment automation. "
     "100,000+ women as domestic workers abroad — high exploitation risk.",
     "Kalyanamitra, LBH APIK"),
    ("India",        "IND","South Asia",   48, 43, 34, 64,
     "IT/BPO, garment, agriculture, manufacturing",
     "HIGH: Marital rape not criminalised. Caste-based targeting. "
     "2M women in BPO facing automation. Garment workers in Tirupur, "
     "Bangalore face WADI risk.",
     "SEWA, Majlis, Breakthrough India"),
    ("Bangladesh",   "BGD","South Asia",   44, 36, 26, 78,
     "Garment (world's #2 exporter), pharmaceuticals",
     "CRITICAL: 4M women garment workers face near-total automation by 2030. "
     "Marital rape legal. Acid attack reprisals against workers who organise.",
     "BNWLA, Naripokkho, Bangladesh Legal Aid"),
    ("Pakistan",     "PAK","South Asia",   38, 28, 25, 72,
     "Garment, textile, leather, agriculture",
     "HIGH: Marital rape legal. Honour killings. "
     "Female workers in textile cities (Faisalabad, Karachi) "
     "face violence when organising.",
     "Shirkat Gah, War Against Rape"),
    ("Cambodia",     "KHM","SE Asia",      36, 30, 28, 86,
     "Garment, tourism, agriculture",
     "CRITICAL: 90% garment workers are women. "
     "H&M, Gap, Zara sourcing here. Automation will eliminate "
     "most jobs by 2030 with zero transition support.",
     "LICADHO, Cambodian Women Crisis Centre"),
    ("Nigeria",      "NGA","Africa",       34, 32, 27, 68,
     "Oil services, agriculture, textiles",
     "HIGH: North-south divide. Kano state — Sharia law severely "
     "restricts women. Female oil workers face harassment.",
     "BAOBAB, Women's Rights Advancement and Protection Alternative"),
    ("Ethiopia",     "ETH","Africa",       32, 26, 23, 78,
     "Garment (Hawassa Industrial Park), agriculture, coffee",
     "HIGH: 60,000 women in Hawassa garment park — Chinese-owned, "
     "automating fastest. Tigray conflict SGBV ongoing.",
     "Ethiopian Women Lawyers Association"),
    ("Myanmar",      "MMR","SE Asia",      28, 24, 19, 62,
     "Garment, agriculture, jade mining",
     "AVOID: Military junta SGBV documented. "
     "Garment brands pulling out since 2021 coup.",
     "Gender Equality Network Myanmar"),
    ("Afghanistan",  "AFG","South Asia",    4,  8,  9, 72,
     "None — economy collapsed",
     "EMBARGO: Taliban have banned women from work, education, "
     "public life. No responsible business possible.",
     "Support Afghan Women (diaspora org)"),
    ("DRC",          "COD","Africa",       22, 18,  3, 62,
     "Mining (cobalt, coltan), agriculture",
     "AVOID: CRITICAL cobalt supply chain. Artisanal mining employs "
     "women and girls. Armed group SGBV at mine sites. "
     "iPhone, EV battery supply chain implicated.",
     "PILI-PILI, Organisation pour la Défense des Droits"),
    ("Sudan",        "SDN","Africa",       20, 18, 13, 58,
     "Agriculture, gum arabic, some manufacturing",
     "AVOID: Active civil war. Mass rape documented by RSF. "
     "No functioning legal system for women.",
     "Sudanese Women's Union"),
    ("Yemen",        "YEM","Middle East",  18, 12, 14, 54,
     "None — active conflict zone",
     "EMBARGO: Active conflict. Houthi SGBV documented. "
     "No functioning state. No responsible business possible.",
     "CARE Yemen emergency"),
    ("Somalia",      "SOM","Africa",       12,  8,  8, 52,
     "None — failed state",
     "EMBARGO: No functioning legal system. "
     "Al-Shabaab controls large territories. FGM near-universal. "
     "No responsible business possible.",
     "Somali Women Development Centre"),
    ("Iran",         "IRN","Middle East",  28, 22, 30, 62,
     "Petrochemicals, carpet weaving, some manufacturing",
     "AVOID: Women protesting at risk of death (Mahsa Amini). "
     "No independent trade unions. Morality police enforce dress code at work.",
     "Iran Human Rights (diaspora)"),
    ("Saudi Arabia", "SAU","Middle East",  44, 46, 40, 48,
     "Construction, finance, tech, entertainment (Vision 2030)",
     "CAUTION: Rapid improvement under Vision 2030 but guardianship "
     "system partially intact. Women now drive and work but "
     "dissidents imprisoned (Loujain al-Hathloul).",
     "DAWN (Democracy for Arab World Now)"),
]


# ── USA STATE COMPLIANCE ──────────────────────────────────────────────────────

USA_STATES = [
    # state, code, bodily_autonomy, maternal_mortality_tier,
    # pay_equity_law, wei_score, key_risk, recommendation
    ("Vermont",         "VT", 94, 1, "strong", 84,
     "No significant risks",
     "PREFERRED for remote hiring, HQ, events"),
    ("California",      "CA", 94, 1, "strong", 82,
     "High cost of living affects dignity score",
     "PREFERRED — strongest reproductive protections post-Dobbs"),
    ("Massachusetts",   "MA", 91, 1, "strong", 85,
     "No significant risks",
     "PREFERRED — Boston/Cambridge top choice"),
    ("Washington",      "WA", 90, 1, "strong", 81,
     "No significant risks",
     "PREFERRED — Seattle tech hub"),
    ("Oregon",          "OR", 90, 1, "strong", 80,
     "No significant risks",
     "PREFERRED"),
    ("Colorado",        "CO", 86, 1, "strong", 79,
     "No significant risks",
     "PREFERRED — Denver growing hub"),
    ("Minnesota",       "MN", 82, 1, "strong", 78,
     "No significant risks",
     "PREFERRED"),
    ("New York",        "NY", 88, 2, "strong", 80,
     "High cost of living",
     "ACCEPTABLE — NYC financial centre"),
    ("Illinois",        "IL", 80, 2, "strong", 76,
     "Chicago south side safety concerns",
     "ACCEPTABLE — Chicago major hub"),
    ("Michigan",        "MI", 80, 2, "strong", 74,
     "Constitutional amendment 2022",
     "ACCEPTABLE — improving trajectory"),
    ("Maryland",        "MD", 81, 2, "strong", 75,
     "No significant risks",
     "ACCEPTABLE — DC metro"),
    ("New Jersey",      "NJ", 85, 2, "strong", 76,
     "No significant risks",
     "ACCEPTABLE"),
    ("Connecticut",     "CT", 87, 2, "strong", 78,
     "No significant risks",
     "ACCEPTABLE"),
    ("Virginia",        "VA", 73, 2, "moderate", 72,
     "Access to reproductive care limited in rural areas",
     "ACCEPTABLE — Northern Virginia tech corridor"),
    ("Pennsylvania",    "PA", 73, 2, "moderate", 71,
     "Rural access gaps",
     "ACCEPTABLE — Philadelphia/Pittsburgh"),
    ("Nevada",          "NV", 77, 2, "moderate", 70,
     "Tourism sector exploitation risks",
     "ACCEPTABLE"),
    ("Florida",         "FL", 45, 3, "weak",   62,
     "6-week ban. High maternal mortality increase post-Dobbs.",
     "CAUTION — require enhanced employee benefits: "
     "out-of-state reproductive healthcare coverage + travel support"),
    ("Arizona",         "AZ", 49, 3, "weak",   64,
     "Unstable legal environment. 1864 ban briefly reinstated 2024.",
     "CAUTION — legal uncertainty. Monitor quarterly."),
    ("North Carolina",  "NC", 39, 3, "weak",   62,
     "12-week ban. Rural healthcare deserts.",
     "CAUTION — require reproductive travel benefits"),
    ("Ohio",            "OH", 31, 3, "weak",   60,
     "Constitutional amendment 2023 but contested.",
     "CAUTION — monitor legal landscape"),
    ("Wisconsin",       "WI", 41, 3, "weak",   61,
     "1849 law partially in effect",
     "CAUTION"),
    ("Georgia",         "GA", 13, 3, "weak",   55,
     "6-week ban. High Black maternal mortality. "
     "Atlanta HQ decisions require enhanced review.",
     "AVOID — do not expand Atlanta operations without "
     "comprehensive employee protection package. "
     "Maternal mortality increase +33% post-Dobbs."),
    ("Indiana",         "IN", 9,  3, "weak",   52,
     "Near-total ban. High maternal mortality.",
     "AVOID — do not initiate new operations"),
    ("South Carolina",  "SC", 11, 3, "weak",   50,
     "6-week ban. High maternal mortality.",
     "AVOID"),
    ("Utah",            "UT", 21, 3, "weak",   55,
     "Near-total ban with narrow exceptions.",
     "AVOID"),
    ("Texas",           "TX", 1,  4, "none",   48,
     "TOTAL BAN since 2021. Highest maternal mortality "
     "increase post-Dobbs (+13%). Criminal penalties for doctors. "
     "No exceptions for rape or incest.",
     "AVOID — no new Texas operations without: "
     "(1) out-of-state reproductive healthcare + travel coverage, "
     "(2) relocation support for affected employees, "
     "(3) CEO sign-off. Existing Austin/Dallas operations: "
     "board review required."),
    ("Louisiana",       "LA", 0,  4, "none",   44,
     "Total ban. No exceptions for rape or incest. "
     "Criminal penalties.",
     "AVOID — do not initiate. Review exit for existing."),
    ("Mississippi",     "MS", 0,  4, "none",   40,
     "Total ban. HIGHEST maternal mortality in USA. "
     "Jackson water crisis. Lowest female education indicators.",
     "AVOID — strongly recommend against any new operations"),
    ("Alabama",         "AL", 0,  4, "none",   40,
     "Total ban + IVF ruling 2024. No exceptions. "
     "Among worst maternal mortality in USA.",
     "AVOID — strongly recommend against any new operations"),
    ("Tennessee",       "TN", 1,  4, "none",   42,
     "Total ban. Criminal penalties.",
     "AVOID"),
    ("Kentucky",        "KY", 0,  4, "none",   42,
     "Total ban.",
     "AVOID"),
    ("Missouri",        "MO", 9,  4, "none",   44,
     "Total ban.",
     "AVOID"),
    ("Arkansas",        "AR", 0,  4, "none",   40,
     "Total ban. Lowest female education indicators.",
     "AVOID"),
    ("Idaho",           "ID", 5,  4, "none",   44,
     "Total ban + shield law criminalising travel.",
     "AVOID"),
    ("Oklahoma",        "OK", 0,  4, "none",   42,
     "Total ban + criminal penalties.",
     "AVOID"),
    ("West Virginia",   "WV", 5,  4, "none",   44,
     "Near-total ban. High poverty.",
     "AVOID"),
    ("South Dakota",    "SD", 0,  4, "none",   44,
     "Total ban.",
     "AVOID"),
    ("North Dakota",    "ND", 3,  4, "none",   44,
     "Near-total ban.",
     "AVOID"),
    ("Wyoming",         "WY", 9,  4, "none",   46,
     "Near-total ban.",
     "AVOID"),
]


def generate(year=BASELINE_YEAR):
    # ── COUNTRY SCORES ────────────────────────────────────────────────────────
    country_rows = []
    for c in COUNTRIES:
        (country, iso, region, wei, gpi, svi, wadi,
         sectors, risk, ngos) = c
        score   = composite_score(wei, gpi, svi, wadi)
        rating  = get_rating(score)
        country_rows.append({
            "country":          country,
            "iso_code":         iso,
            "region":           region,
            "composite_score":  score,
            "rating":           rating["code"],
            "rating_headline":  rating["headline"],
            "wei_score":        wei,
            "gpi_score":        gpi,
            "svi_score":        svi,
            "wadi_score":       wadi,
            "main_outsourcing_sectors": sectors,
            "key_risk":         risk,
            "required_actions": " | ".join(rating["required_actions"]),
            "ngo_partners_to_fund": ngos,
            "year":             year,
        })
    country_rows.sort(key=lambda x: x["composite_score"], reverse=True)
    for i, r in enumerate(country_rows): r["rank"] = i + 1

    # ── USA STATE SCORES ──────────────────────────────────────────────────────
    usa_rows = []
    for s in USA_STATES:
        (state, code, bodily, mmr_tier, pay_eq, wei_sc, risk, rec) = s
        # USA state composite focuses on bodily autonomy (post-Dobbs)
        # and overall WEI — no GPI/SVI at state level
        comp = round((bodily * 0.45) + (wei_sc * 0.35) +
                     ({"strong":100,"moderate":65,"weak":30,"none":0}
                      .get(pay_eq, 50) * 0.20), 1)
        rating = get_rating(comp)
        usa_rows.append({
            "state":            state,
            "state_code":       code,
            "composite_score":  comp,
            "rating":           rating["code"],
            "rating_headline":  rating["headline"],
            "wei_score":        wei_sc,
            "bodily_autonomy_score": bodily,
            "maternal_mortality_tier": mmr_tier,
            "pay_equity_law":   pay_eq,
            "key_risk":         risk,
            "recommendation":   rec,
            "required_actions": " | ".join(rating["required_actions"]),
            "year":             year,
        })
    usa_rows.sort(key=lambda x: x["composite_score"], reverse=True)
    for i, r in enumerate(usa_rows): r["rank"] = i + 1

    # ── SAVE ──────────────────────────────────────────────────────────────────
    # Countries
    country_out = OUTPUT_DIR / f"corporate-compliance-countries-{year}.csv"
    c_hdr = (
        f"# SHEtoken Women's Rights Business Compliance Score — Countries {year}\n"
        f"# RATING:  PREFERRED ✅ | ACCEPTABLE 🟢 | CAUTION 🟡 | AVOID 🔴 | EMBARGO ⛔\n"
        f"# Composite = WEI(40%) + SVI(25%) + GPI(20%) + (100-WADI)(15%)\n"
        f"# USE: Before signing any outsourcing, manufacturing, or service contract\n"
        f"# Legal basis: UNGP, EU CS3D, UK Modern Slavery Act, US TVPA\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    c_flds = ["rank","country","iso_code","region","composite_score","rating",
              "rating_headline","wei_score","gpi_score","svi_score","wadi_score",
              "main_outsourcing_sectors","key_risk","required_actions",
              "ngo_partners_to_fund","year"]
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=c_flds, extrasaction="ignore")
    w.writeheader(); w.writerows(country_rows)
    with open(country_out,"w",newline="",encoding="utf-8") as f:
        f.write(c_hdr + buf.getvalue())

    # USA states
    usa_out = OUTPUT_DIR / f"corporate-compliance-usa-states-{year}.csv"
    u_hdr = (
        f"# SHEtoken Women's Rights Business Compliance — USA States {year}\n"
        f"# Composite = Bodily Autonomy(45%) + WEI(35%) + Pay Equity Law(20%)\n"
        f"# Post-Dobbs analysis: which US states are safe for female employees?\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    u_flds = ["rank","state","state_code","composite_score","rating",
              "rating_headline","wei_score","bodily_autonomy_score",
              "maternal_mortality_tier","pay_equity_law","key_risk",
              "recommendation","required_actions","year"]
    buf2 = io.StringIO()
    w2 = csv.DictWriter(buf2, fieldnames=u_flds, extrasaction="ignore")
    w2.writeheader(); w2.writerows(usa_rows)
    with open(usa_out,"w",newline="",encoding="utf-8") as f:
        f.write(u_hdr + buf2.getvalue())

    # Save JSON for API
    json_out = OUTPUT_DIR / f"corporate-compliance-{year}.json"
    out_data = {
        "description": "Women's Rights Business Compliance Score",
        "rating_guide": {
            k: {"score_min":v["score_min"],"headline":v["headline"],
                "symbol":v["symbol"]}
            for k,v in RATINGS.items()
        },
        "countries": {r["iso_code"]: {
            "country":r["country"],"score":r["composite_score"],
            "rating":r["rating"],"rating_headline":r["rating_headline"],
            "key_risk":r["key_risk"],
            "required_actions":r["required_actions"].split(" | "),
            "ngo_partners":r["ngo_partners_to_fund"],
        } for r in country_rows},
        "usa_states": {r["state_code"]: {
            "state":r["state"],"score":r["composite_score"],
            "rating":r["rating"],"recommendation":r["recommendation"],
            "bodily_autonomy_score":r["bodily_autonomy_score"],
            "required_actions":r["required_actions"].split(" | "),
        } for r in usa_rows},
    }
    with open(json_out,"w",encoding="utf-8") as f:
        json.dump(out_data, f, indent=2, ensure_ascii=False)

    # ── PRINT REPORT ──────────────────────────────────────────────────────────
    print("Women's Rights Business Compliance Score")
    print("="*70)

    for code, label in [
        ("EMBARGO","⛔ EMBARGO — no business"),
        ("AVOID",  "🔴 AVOID — do not initiate new"),
        ("CAUTION","🟡 CAUTION — enhanced obligations"),
        ("ACCEPTABLE","🟢 ACCEPTABLE"),
        ("PREFERRED","✅ PREFERRED — actively source here"),
    ]:
        group = [r for r in country_rows if r["rating"]==code]
        if not group: continue
        print(f"\n  {label} ({len(group)} countries):")
        for r in group:
            print(f"    {r['composite_score']:>5}  {r['country']:<20} "
                  f"WEI:{r['wei_score']:>3} SVI:{r['svi_score']:>3} "
                  f"GPI:{r['gpi_score']:>3} WADI:{r['wadi_score']:>3}")

    print(f"\n  USA STATES — Bottom 10 for female employees:")
    avoid = [r for r in usa_rows if r["rating"] in ("AVOID","EMBARGO")]
    avoid.sort(key=lambda x: x["composite_score"])
    for r in avoid[:10]:
        print(f"    {r['composite_score']:>5}  {r['state']:<20} "
              f"Bodily:{r['bodily_autonomy_score']:>3}  "
              f"MMR tier:{r['maternal_mortality_tier']}  "
              f"Pay equity: {r['pay_equity_law']}")

    print(f"\n  USA STATES — Top 5 for female employees:")
    for r in usa_rows[:5]:
        print(f"    {r['composite_score']:>5}  {r['state']:<20} "
              f"Bodily:{r['bodily_autonomy_score']:>3}  "
              f"{r['recommendation'][:50]}")

    print(f"\n  Saved: {country_out}")
    print(f"  Saved: {usa_out}")
    print(f"  Saved: {json_out}")


if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--year", type=int, default=BASELINE_YEAR)
    p.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    generate(p.parse_args().year)