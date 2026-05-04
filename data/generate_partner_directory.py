"""
SHEtoken — Women's Rights Partner Directory
=============================================
A positive discovery tool answering three questions:

  1. COUNTRY: "Which countries should I partner with for
     women-focused work in my sector/region?"

  2. PROGRAM: "Which proven programs exist that I could
     fund, replicate, or partner with?"

  3. COMPANY: "Which companies have genuine women's rights
     commitments I could partner with or source from?"

This is the OPPOSITE of the compliance score.
The compliance score says: avoid these places.
The directory says: find these partners.

Data sources:
  UN Women Partner Directory
  ILO Better Work Programme
  B Corp Directory (gender lens)
  GenderSmart Investing database
  Criterion Institute
  Invest2Innovate
  Wharton Social Impact

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, json
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR


# ═════════════════════════════════════════════════════════════════════════════
# COUNTRY PROFILES FOR WOMEN'S WORK PARTNERSHIPS
# ═════════════════════════════════════════════════════════════════════════════

# Sectors where each country has proven capacity + strong WEI alignment
# country, iso, region, wei_score,
# strength_sectors,          what they are genuinely good at for women's work
# flagship_programs,         proven programs you can partner with
# best_for,                  what type of partner would benefit most
# contact_entry_points,      where to start a partnership
# language,
# notes

COUNTRY_PARTNERS = [

    # ── INDIA ─────────────────────────────────────────────────────────────────
    ("India — Kerala",  "IND-KL","South Asia", 73.6,
     ["Women's SHG / microfinance","Elder care","Digital inclusion",
      "Health community workers","Women's cooperative enterprise"],
     ["Kudumbashree (46 lakh members, Asia's largest SHG network)",
      "ASHA community health workers",
      "Kerala Startup Mission women's track"],
     "NGOs wanting SHG model replication, microfinance partners, "
     "health system strengthening, cooperative enterprise",
     ["Kerala State Planning Board — gender division",
      "Kudumbashree Mission (kudumbashree.org)",
      "Kerala Women's Commission"],
     "Malayalam / English",
     "Best state in India for women's partnership. "
     "Kudumbashree is the world's most replicable women's SHG model."),

    ("India — West Bengal","IND-WB","South Asia", 50.0,
     ["Girls education programs","Cash transfer delivery","Women's enterprise",
      "Cultural arts + women's voice"],
     ["Kanyashree (10M girls, UNESCO prize)",
      "Lakshmi Bhandar (24.1M beneficiaries)",
      "Rupashree (2.3M women)"],
     "Education NGOs, conditional cash transfer researchers, "
     "women's economic empowerment programs",
     ["West Bengal Women and Child Development Dept",
      "UNICEF India Kolkata office",
      "Pratichi Trust (Amartya Sen's organisation)"],
     "Bengali / English",
     "Strong government program infrastructure. "
     "Kanyashree is the most successful girls' education program in South Asia."),

    ("India — Gujarat",  "IND-GJ","South Asia", 57.8,
     ["Women's labour rights","Microfinance","Informal sector workers",
      "Legal aid","Women's cooperatives"],
     ["SEWA (Self Employed Women's Association — 3.78M members)",
      "SEWA Bank (pioneered global microfinance)",
      "Mann Deshi Bank (100K+ women account holders)"],
     "Labour rights organisations, microfinance partners, "
     "informal economy researchers, cooperative development",
     ["SEWA (sewa.org)",
      "Mann Deshi Foundation",
      "Gujarat Mahila Housing SEWA Trust"],
     "Gujarati / Hindi / English",
     "SEWA is one of the world's most influential women's labour organisations. "
     "Any microfinance or cooperative partner should start here."),

    ("India — Bihar",    "IND-BR","South Asia", 41.6,
     ["Rural women's enterprise","SHG banking","Village-level poverty reduction"],
     ["JEEViKA (1.04M SHGs, ₹11,000 crore credit leveraged)",
      "Jehan Ara (women in tech training)"],
     "Rural enterprise development, poverty reduction, "
     "SHG-linked banking, agricultural value chains",
     ["Bihar Rural Livelihoods Promotion Society (JEEViKA)",
      "BRLPS gender division",
      "UNICEF Bihar office"],
     "Hindi / English",
     "JEEViKA has the best data infrastructure for rural women's "
     "economic programs in India."),

    ("India — Rajasthan","IND-RJ","South Asia", 48.6,
     ["Girls education and enrollment","Child marriage prevention",
      "Desert women's enterprise"],
     ["Educate Girls (6.7M beneficiaries, 380K girls enrolled)",
      "Barefoot College (solar women engineers)"],
     "Girls education NGOs, child marriage prevention, "
     "rural women's skilling, solar/renewable energy sector",
     ["Educate Girls (educategirls.ngo)",
      "Barefoot College (barefootcollege.org)",
      "Rajasthan State Commission for Women"],
     "Hindi / English",
     "Educate Girls is the world's most cost-effective girls' "
     "education intervention with verified outcome data."),

    # ── KENYA ─────────────────────────────────────────────────────────────────
    ("Kenya",            "KEN",  "East Africa", 40.3,
     ["Women's mobile financial services","Agricultural cooperatives",
      "Women in tech","Legal aid","Sexual violence response"],
     ["M-Pesa women agents (financial inclusion model)",
      "UN Women Kenya Safe Cities program",
      "Ushahidi (women's crisis mapping)"],
     "Fintech for women, agricultural supply chain, "
     "women in tech, urban safety programs",
     ["UN Women Kenya office",
      "Kenya Women's Parliamentary Association",
      "Strathmore University Women in Tech",
      "Wangu Kanja Foundation (SGBV response)"],
     "Swahili / English",
     "East Africa's most sophisticated digital economy. "
     "M-Pesa model is the world's most replicated financial inclusion tool."),

    # ── RWANDA ────────────────────────────────────────────────────────────────
    ("Rwanda",           "RWA",  "East Africa", 57.2,
     ["Women in governance","Post-conflict women's rights",
      "Women's land rights","ICT for women"],
     ["61% women in parliament (world's highest)",
      "Itorero women's civic education",
      "Rwanda Girls in ICT (50K trained)"],
     "Political empowerment programs, post-conflict reconciliation, "
     "governance reform, women in tech",
     ["Rwanda Gender Monitoring Office",
      "Gender Is My Agenda Campaign (GIMAC)",
      "Rwanda Women's Network"],
     "Kinyarwanda / English / French",
     "Best governance model for women's political inclusion globally. "
     "Any program working on women in parliament should study Rwanda."),

    # ── BANGLADESH ────────────────────────────────────────────────────────────
    ("Bangladesh",       "BGD",  "South Asia", 44.0,
     ["Girls education via stipends","Garment worker rights",
      "Women's legal aid","Microfinance"],
     ["BRAC (world's largest NGO, 100M+ reached)",
      "Grameen Bank (Nobel Prize microfinance)",
      "BNWLA (legal aid for women)"],
     "Education stipends, garment worker welfare, microfinance, "
     "legal aid, disaster resilience",
     ["BRAC International (brac.net)",
      "Grameen Bank women's programs",
      "Bangladesh Legal Aid and Services Trust (BLAST)"],
     "Bengali / English",
     "Despite AVOID rating for sourcing, Bangladesh has the world's "
     "strongest NGO ecosystem for women's development. "
     "BRAC and Grameen are globally replicable models."),

    # ── ETHIOPIA ──────────────────────────────────────────────────────────────
    ("Ethiopia",         "ETH",  "East Africa", 32.0,
     ["Community health workers (female)","Girl child protection",
      "Women's land rights certification"],
     ["38,000 Health Extension Workers program",
      "Ethiopian Women Lawyers Association",
      "Land certification program (reduced DV 33%)"],
     "Health systems, land rights programs, women's legal aid",
     ["CARE Ethiopia women's programs",
      "Ethiopian Women Lawyers Association (EWLA)",
      "UN Women Ethiopia"],
     "Amharic / English",
     "Health Extension Workers program is the world's most "
     "successful community health model for women."),

    # ── COLOMBIA ──────────────────────────────────────────────────────────────
    ("Colombia",         "COL",  "South America", 51.0,
     ["Post-conflict women's rights","Reproductive rights",
      "Women in peace processes","Afro-Colombian women's rights"],
     ["Colombia Peace Agreement women's chapter",
      "Casa de la Mujer",
      "Ruta Pacífica de las Mujeres"],
     "Post-conflict reconciliation, reproductive rights advocacy, "
     "indigenous and Afro-Colombian women's programs",
     ["Casa de la Mujer (casmujer.org)",
      "Humanas Colombia",
      "UN Women Colombia"],
     "Spanish / English",
     "Colombia has the world's most sophisticated post-conflict "
     "women's rights framework. Peace agreement gender chapter "
     "is the model for conflict resolution."),

    # ── NORDIC ────────────────────────────────────────────────────────────────
    ("Sweden",           "SWE",  "Europe", 91.0,
     ["Equal pay legislation","Parental leave models",
      "Women's shelter infrastructure","Feminist foreign policy"],
     ["Sweden feminist foreign policy (2014, world's first)",
      "SIDA gender mainstreaming",
      "Swedish Equal Pay Standard"],
     "Policy advocacy, feminist foreign policy, equal pay law "
     "design, parental leave reform, shelter network models",
     ["SIDA (Swedish International Development Agency)",
      "Swedish Women's Lobby",
      "Nordic Information on Gender (NIKK)"],
     "Swedish / English",
     "Sweden's feminist foreign policy is the most comprehensive "
     "government gender framework globally. SIDA is a major funder."),

    ("Iceland",          "ISL",  "Europe", 93.4,
     ["Equal pay certification","Women in boardrooms",
      "Gender budgeting","Parental leave"],
     ["Equal Pay Standard (ISO certification model)",
      "Gender Equality Act (most comprehensive globally)",
      "Parental leave 12 months shared"],
     "Equal pay law design, corporate gender governance, "
     "gender-responsive budgeting, policy advocacy",
     ["Ministry of Social Affairs — gender equality division",
      "Centre for Gender Equality Iceland",
      "Confederation of Icelandic Employers"],
     "Icelandic / English",
     "Iceland's equal pay certification is the global gold standard. "
     "Any corporate equal pay initiative should replicate this model."),

    # ── URUGUAY ───────────────────────────────────────────────────────────────
    ("Uruguay",          "URY",  "South America", 68.0,
     ["National care system","Reproductive rights","Women in politics",
      "Gender-responsive budgeting"],
     ["Uruguay National Care System (SNIC) — state-funded care",
      "Abortion legalised 2012 model",
      "Gender parity electoral law"],
     "Care economy policy, reproductive rights advocacy, "
     "Latin America gender policy reform",
     ["Uruguay Ministry of Social Development — gender division",
      "Cotidiano Mujer",
      "Mysu (sexual and reproductive rights)"],
     "Spanish / English",
     "Uruguay's National Care System is the world's best model "
     "for reducing women's unpaid care burden at state level."),

    # ── SOUTH AFRICA ──────────────────────────────────────────────────────────
    ("South Africa",     "ZAF",  "Southern Africa", 50.8,
     ["Women in governance","Gender-based violence response",
      "Women's economic inclusion","Femicide tracking"],
     ["Commission for Gender Equality",
      "Sonke Gender Justice (men + gender equality)",
      "People Opposing Women Abuse (POWA)"],
     "GBV response infrastructure, gender commission model, "
     "men's engagement programs, femicide data methodology",
     ["Commission for Gender Equality (cge.org.za)",
      "Sonke Gender Justice",
      "Gender Links"],
     "English / Zulu / Xhosa",
     "South Africa has the world's most sophisticated GBV "
     "response infrastructure despite high violence rates. "
     "Sonke is the global leader in men + gender equality programs."),

    # ── NEW ZEALAND ───────────────────────────────────────────────────────────
    ("New Zealand",      "NZL",  "Oceania", 86.6,
     ["Indigenous women's rights (Māori)","Equal pay legislation",
      "Gender-responsive budgeting","Wellbeing economics"],
     ["NZ Wellbeing Budget (gender lens)",
      "Pay Equity Act 2020",
      "Māori women leadership programs"],
     "Gender-responsive budgeting, indigenous women's rights, "
     "wellbeing economics, equal pay law",
     ["NZ Ministry for Women",
      "Māori Women's Welfare League",
      "Pacific Women's Watch NZ"],
     "English / Māori",
     "NZ Wellbeing Budget is the world's most advanced "
     "gender-responsive national budget framework."),
]


# ═════════════════════════════════════════════════════════════════════════════
# PROGRAM DIRECTORY — Proven interventions available for partnership
# ═════════════════════════════════════════════════════════════════════════════

PROGRAMS = [

    # ── EDUCATION ─────────────────────────────────────────────────────────────
    {
        "name":        "Kanyashree",
        "country":     "India — West Bengal",
        "iso":         "IND",
        "sector":      "Girls Education",
        "pillar":      "education",
        "scale":       "10 million girls enrolled",
        "proven_outcome": "Reduced child marriage 40%, increased secondary enrollment 30%",
        "contact":     "West Bengal Women and Child Development Dept",
        "website":     "kanyashree.gov.in",
        "replicable":  True,
        "notes":       "UNESCO prize winner 2017. Conditional cash transfer model. "
                       "Cost: ~$20/girl/year. Most replicable girls education program globally.",
    },
    {
        "name":        "Educate Girls",
        "country":     "India — Rajasthan / MP",
        "iso":         "IND",
        "sector":      "Girls Education",
        "pillar":      "education",
        "scale":       "6.7 million beneficiaries, 380,000 girls enrolled",
        "proven_outcome": "97% retention rate. Development Impact Bond verified.",
        "contact":     "Educate Girls, Udaipur",
        "website":     "educategirls.ngo",
        "replicable":  True,
        "notes":       "World's first Development Impact Bond for girls' education. "
                       "Cost-per-girl among lowest verified globally.",
    },
    {
        "name":        "Scotland Period Products Act",
        "country":     "Scotland / UK",
        "iso":         "GBR",
        "sector":      "Period Poverty / Education",
        "pillar":      "bodily_autonomy",
        "scale":       "National — all of Scotland",
        "proven_outcome": "First country to make period products free by law (2021). "
                          "School attendance improved measurably.",
        "contact":     "Scottish Government — Period Products team",
        "website":     "gov.scot/period-products",
        "replicable":  True,
        "notes":       "Legislative model. Any government can replicate. "
                       "Cost: ~£9M/year for population of 5.4M.",
    },

    # ── ECONOMIC ──────────────────────────────────────────────────────────────
    {
        "name":        "Kudumbashree",
        "country":     "India — Kerala",
        "iso":         "IND",
        "sector":      "Women's SHG / Economic Empowerment",
        "pillar":      "economic",
        "scale":       "46 lakh (4.6M) members. Half of all Kerala families.",
        "proven_outcome": "Poverty reduction, women's income increase, "
                          "political participation increase.",
        "contact":     "Kudumbashree Mission, Thiruvananthapuram",
        "website":     "kudumbashree.org",
        "replicable":  True,
        "notes":       "World's most successful state-level women's SHG network. "
                       "25 years of data. Integrated with local government.",
    },
    {
        "name":        "SEWA (Self Employed Women's Association)",
        "country":     "India — Gujarat",
        "iso":         "IND",
        "sector":      "Informal Worker Rights / Microfinance",
        "pillar":      "economic",
        "scale":       "3.78 million members across 20 states",
        "proven_outcome": "Increased income, reduced vulnerability, "
                          "legal recognition of informal workers.",
        "contact":     "SEWA, Ahmedabad",
        "website":     "sewa.org",
        "replicable":  True,
        "notes":       "Founded 1972. Pioneered global microfinance via SEWA Bank 1974. "
                       "The model for informal worker organisation globally.",
    },
    {
        "name":        "Lakshmi Bhandar",
        "country":     "India — West Bengal",
        "iso":         "IND",
        "sector":      "Direct Cash Transfer",
        "pillar":      "dignity_welfare",
        "scale":       "24.1 million beneficiaries. ₹1,500-1,700/month.",
        "proven_outcome": "Direct financial autonomy for women. Poverty reduction. "
                          "Women named as primary beneficiary (account owner).",
        "contact":     "West Bengal Finance Department",
        "website":     "wb.gov.in",
        "replicable":  True,
        "notes":       "Largest state-level direct cash transfer to women globally. "
                       "Account in woman's name is the key design feature.",
    },
    {
        "name":        "Iceland Equal Pay Certification",
        "country":     "Iceland",
        "iso":         "ISL",
        "sector":      "Corporate Equal Pay",
        "pillar":      "economic",
        "scale":       "National mandate — all companies 25+ employees",
        "proven_outcome": "Measurable pay gap reduction. "
                          "First country to make equal pay certification mandatory.",
        "contact":     "Iceland Ministry of Social Affairs",
        "website":     "ministryofsocialaffairs.is",
        "replicable":  True,
        "notes":       "Companies must certify equal pay for equal work every 3 years. "
                       "ISO 30415 certification basis. Any country can adopt this.",
    },
    {
        "name":        "New Zealand Pay Equity Act",
        "country":     "New Zealand",
        "iso":         "NZL",
        "sector":      "Care Economy Pay Equity",
        "pillar":      "economic",
        "scale":       "55,000 care and support workers. 15-49% pay rise.",
        "proven_outcome": "Historic pay equity settlement 2017. "
                          "Care workers paid at par with comparable male-dominated work.",
        "contact":     "NZ Ministry for Women",
        "website":     "women.govt.nz",
        "replicable":  True,
        "notes":       "Best model globally for closing the care economy wage gap. "
                       "Directly addresses the time poverty and care trap issues.",
    },

    # ── SAFETY / SVI ──────────────────────────────────────────────────────────
    {
        "name":        "India One-Stop Crisis Centres (Sakhi)",
        "country":     "India",
        "iso":         "IND",
        "sector":      "GBV Response",
        "pillar":      "safety_justice",
        "scale":       "700+ centres operational nationally",
        "proven_outcome": "Legal aid, shelter, counselling, medical in one place. "
                          "Proven uptake and survivor satisfaction.",
        "contact":     "Ministry of Women and Child Development India",
        "website":     "wcddelhiportal.nic.in",
        "replicable":  True,
        "notes":       "One-stop model replicable globally. "
                       "Integrates police, legal, medical, and shelter in one facility.",
    },
    {
        "name":        "Tostan Community-Led FGM Abandonment",
        "country":     "Senegal",
        "iso":         "SEN",
        "sector":      "FGM Prevention",
        "pillar":      "bodily_autonomy",
        "scale":       "6,000+ communities abandoned FGM voluntarily",
        "proven_outcome": "No coercion. Community-owned. "
                          "Sustained abandonment verified 10+ years later.",
        "contact":     "Tostan, Dakar",
        "website":     "tostan.org",
        "replicable":  True,
        "notes":       "Only proven approach to FGM abandonment that lasts. "
                       "Community Empowerment Program model. UNICEF partner.",
    },

    # ── WEVI ──────────────────────────────────────────────────────────────────
    {
        "name":        "Ethiopia Land Certification Program",
        "country":     "Ethiopia",
        "iso":         "ETH",
        "sector":      "Women's Land Rights",
        "pillar":      "dignity_welfare",
        "scale":       "6 million women landholders registered",
        "proven_outcome": "Domestic violence fell 33% in areas with female land titles. "
                          "Women's investment in land increased 40%.",
        "contact":     "Ethiopian Ministry of Agriculture — land admin",
        "website":     "landportal.org/ethiopia",
        "replicable":  True,
        "notes":       "Single most impactful land rights intervention documented. "
                       "DV reduction from property rights is the counterintuitive finding.",
    },
    {
        "name":        "Guild of Service — Vrindavan Widows",
        "country":     "India — Uttar Pradesh",
        "iso":         "IND",
        "sector":      "Widow Rehabilitation",
        "pillar":      "dignity_welfare",
        "scale":       "1,500+ widows with income and housing support",
        "proven_outcome": "Vocational training, income generation, "
                          "family reintegration support.",
        "contact":     "Guild of Service, New Delhi",
        "website":     "guildofservice.org",
        "replicable":  True,
        "notes":       "Only documented scalable program for temple town widows. "
                       "Supreme Court 2018 order cited their work.",
    },

    # ── WADI / AI DISPLACEMENT ────────────────────────────────────────────────
    {
        "name":        "Rwanda Girls in ICT",
        "country":     "Rwanda",
        "iso":         "RWA",
        "sector":      "Digital Skills / AI Readiness",
        "pillar":      "digital_social",
        "scale":       "50,000+ girls trained in ICT",
        "proven_outcome": "Rwanda now has highest female ICT enrollment in Africa.",
        "contact":     "Rwanda Ministry of ICT",
        "website":     "rdb.rw",
        "replicable":  True,
        "notes":       "Best model in Africa for girls' digital skills. "
                       "Government-led, school-integrated, employer-linked.",
    },
    {
        "name":        "Digital Sakhi India",
        "country":     "India",
        "iso":         "IND",
        "sector":      "Rural Women's Digital Literacy",
        "pillar":      "digital_social",
        "scale":       "150,000 women digital champions in rural areas",
        "proven_outcome": "Women teaching women in villages. "
                          "Bank account access, government service access improved.",
        "contact":     "CSC e-Governance Services India",
        "website":     "csc.gov.in",
        "replicable":  True,
        "notes":       "Best model for rural women's digital inclusion. "
                       "Peer-to-peer model scales cheaply.",
    },
]


# ═════════════════════════════════════════════════════════════════════════════
# COMPANY DIRECTORY — Genuine women's rights commitments
# ═════════════════════════════════════════════════════════════════════════════
# NOTE: Only companies included here through public statements,
# certifications, or independent verified data.
# No accusations. No unverified claims.

COMPANY_CATEGORIES = {

    "certified_equal_pay": {
        "description": "Companies with verified equal pay certification",
        "how_to_find":
            "Equal Pay International Coalition (EPIC) employer register: "
            "equalpayinternationalcoalition.org/employer-recognition",
        "examples":
            "See EPIC registry. Iceland-certified companies listed at "
            "jafnlaunavottun.is. UK Gender Pay Gap data: gender-pay-gap.service.gov.uk",
        "partner_for": "Pay equity benchmarking, policy advocacy, employee recruitment",
    },

    "iloBetterWork": {
        "description": "Companies enrolled in ILO Better Work programme",
        "how_to_find":
            "ILO Better Work buyer partners publicly listed: "
            "betterwork.org/our-work/buyers",
        "examples":
            "Full list at betterwork.org. These companies have committed to "
            "factory-level gender audits in garment supply chains.",
        "partner_for": "Garment sector sourcing, worker welfare programs, "
                       "supply chain due diligence",
    },

    "b_corp_gender_lens": {
        "description": "B Corp certified companies with gender lens investing focus",
        "how_to_find":
            "B Corp directory with gender filter: bcorporation.net/en-us/find-a-b-corp "
            "Filter by: Community → Diversity, Equity + Inclusion",
        "examples":
            "Search B Corp directory. 6,000+ certified companies globally. "
            "Filter by country and sector relevant to your partnership.",
        "partner_for": "Social enterprise partnerships, impact investing, "
                       "supply chain partners with verified social standards",
    },

    "2x_challenge": {
        "description": "Companies backed by 2X Challenge gender lens investors",
        "how_to_find":
            "2X Collaborative portfolio: 2xcollaborative.org/portfolio",
        "examples":
            "Development finance-backed companies with women's "
            "ownership/leadership/employment criteria verified.",
        "partner_for": "Investment partnerships, market access, "
                       "enterprise development in emerging markets",
    },

    "weps_signatories": {
        "description": "UN Women's Empowerment Principles signatories",
        "how_to_find":
            "WEPs signatory database: weps.org/signatories "
            "Search by country and sector",
        "examples":
            "3,000+ companies have signed the UN Women's Empowerment Principles. "
            "Covers: workplace gender equality, community engagement, "
            "marketplace transparency.",
        "partner_for": "Corporate partnership, co-branding, "
                       "supply chain relationships, investor relations",
    },

    "genderSmart_investors": {
        "description": "Gender-lens investors actively funding women's initiatives",
        "how_to_find":
            "GenderSmart database: gendersmartinvesting.org/directory",
        "examples":
            "Verified gender-lens investors across asset classes. "
            "Useful for: funding women's programs, ESG investment partnerships.",
        "partner_for": "Funding, ESG alignment, impact measurement partnerships",
    },
}


def generate(year=BASELINE_YEAR):
    # Save country partner directory
    country_out = OUTPUT_DIR / f"partner-directory-countries-{year}.csv"
    c_flds = ["country","iso","region","wei_score","strength_sectors",
              "flagship_programs","best_for","contact_entry_points",
              "language","notes","year"]
    c_rows = []
    for p in COUNTRY_PARTNERS:
        (country,iso,region,wei,sectors,programs,
         best_for,contacts,lang,notes) = p
        c_rows.append({
            "country":             country,
            "iso":                 iso,
            "region":              region,
            "wei_score":           wei,
            "strength_sectors":    " | ".join(sectors),
            "flagship_programs":   " | ".join(programs),
            "best_for":            best_for,
            "contact_entry_points":" | ".join(contacts),
            "language":            lang,
            "notes":               notes,
            "year":                year,
        })
    c_rows.sort(key=lambda x: x["wei_score"], reverse=True)

    hdr = (
        f"# SHEtoken Women's Rights Partner Directory — Countries {year}\n"
        f"# Which countries should I partner with for women-focused work?\n"
        f"# Sorted by WEI score within region.\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    buf=io.StringIO(); w=csv.DictWriter(buf,fieldnames=c_flds,extrasaction="ignore")
    w.writeheader(); w.writerows(c_rows)
    with open(country_out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())

    # Save program directory
    prog_out = OUTPUT_DIR / f"partner-directory-programs-{year}.csv"
    p_flds = ["name","country","iso","sector","pillar","scale",
              "proven_outcome","contact","website","replicable","notes","year"]
    prog_rows = [{**p,"year":year} for p in PROGRAMS]

    hdr2=(f"# SHEtoken Women's Rights Partner Directory — Programs {year}\n"
          f"# Proven programs available for funding, replication, or partnership\n"
          f"# (c) 2026 SHE Foundation\n#\n")
    buf2=io.StringIO(); w2=csv.DictWriter(buf2,fieldnames=p_flds,extrasaction="ignore")
    w2.writeheader(); w2.writerows(prog_rows)
    with open(prog_out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr2+buf2.getvalue())

    # Save company categories JSON
    comp_out = OUTPUT_DIR / f"partner-directory-companies-{year}.json"
    with open(comp_out,"w",encoding="utf-8") as f:
        json.dump({
            "description": "How to find companies with genuine women's rights commitments",
            "note": "We direct to verified public registries rather than naming "
                    "specific companies. This ensures accuracy and legal safety.",
            "categories": COMPANY_CATEGORIES,
            "year": year,
        }, f, indent=2, ensure_ascii=False)

    # Print report
    print(f"Women's Rights Partner Directory — {year}")
    print("="*65)
    print(f"\n  Country Partners: {len(c_rows)}")
    print(f"  Proven Programs:  {len(prog_rows)}")
    print(f"  Company Categories: {len(COMPANY_CATEGORIES)}")
    print(f"\n  Top partner countries by WEI:")
    for r in c_rows[:8]:
        print(f"    {r['wei_score']:>5}  {r['country']:<25} "
              f"{r['strength_sectors'].split(' | ')[0]}")
    print(f"\n  Programs by sector:")
    sectors = {}
    for p in PROGRAMS:
        s = p["sector"]
        sectors[s] = sectors.get(s,0) + 1
    for s,n in sorted(sectors.items(), key=lambda x: x[1], reverse=True):
        print(f"    {n}  {s}")
    print(f"\n  Company registries covered:")
    for key, data in COMPANY_CATEGORIES.items():
        print(f"    {key}: {data['description']}")
    print(f"\n  Saved: {country_out}")
    print(f"  Saved: {prog_out}")
    print(f"  Saved: {comp_out}")


if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,default=BASELINE_YEAR)
    generate(p.parse_args().year)
