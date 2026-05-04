"""
SHEtoken — Comprehensive Policy Recommendation Engine v2
=========================================================
Generates evidence-based policy recommendations for every
country based on ALL indexes: WEI, GPI, SVI, WEVI, WADI.

Updated to cover:
  ✅ WEI 8 pillars
  ✅ AI job displacement (WADI)
  ✅ Widow/elderly vulnerability (WEVI)
  ✅ Sexual violence underreporting + marital rape
  ✅ Conflict SGBV
  ✅ Period poverty + school dropout causes
  ✅ GPI time poverty / care work burden
  ✅ GPI land/property ownership gap
  ✅ Digital sexual violence
  ✅ Caste/ethnic targeting
  ✅ Indigenous women vulnerability
  ✅ Temple town / abandoned widows (India)
  ✅ Garment sector automation risk

Each recommendation cites a proven real-world program
with estimated impact, cost tier, and time to effect.

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, json
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

# ═════════════════════════════════════════════════════════════════════════════
# EVIDENCE DATABASE — Complete intervention library
# ═════════════════════════════════════════════════════════════════════════════

INTERVENTIONS = {

    # ── WEI PILLAR: EDUCATION ─────────────────────────────────────────────────
    "education_low": [
        {
            "name":     "Conditional Cash Transfer for Girls",
            "description": "Monthly cash payment to families contingent on girl's attendance",
            "impact":   "WEI Education +2.5/yr",
            "cost":     "low",
            "time":     "1-2 years",
            "example":  "Kanyashree India — 10M girls, UNESCO prize 2017",
            "applies_to": ["dropout_cost","dropout_domestic_labour"],
        },
        {
            "name":     "Free Menstrual Products + School WASH",
            "description": "Sanitary products + female toilets + changing rooms in every school",
            "impact":   "WEI Education +1.8, Bodily Autonomy +2.0",
            "cost":     "low",
            "time":     "6-12 months",
            "example":  "Scotland Period Products Act 2021 — first country, free by law",
            "applies_to": ["dropout_period_poverty","period_poverty"],
        },
        {
            "name":     "Female Teacher Recruitment Drive",
            "description": "Targeted recruitment + incentive pay for female teachers in under-served areas",
            "impact":   "WEI Education +1.5",
            "cost":     "medium",
            "time":     "2-3 years",
            "example":  "BRAC Bangladesh — 70% female teachers in rural schools",
            "applies_to": ["dropout_no_female_teacher"],
        },
        {
            "name":     "Safe School Route Program",
            "description": "Lighting, community wardens, subsidised transport for girls",
            "impact":   "WEI Education +1.2, Safety +1.5",
            "cost":     "medium",
            "time":     "1-2 years",
            "example":  "Safe Schools Initiative Kenya, Uganda — 40% dropout reduction",
            "applies_to": ["dropout_safety"],
        },
    ],

    # ── WEI PILLAR: BODILY AUTONOMY ───────────────────────────────────────────
    "bodily_autonomy_low": [
        {
            "name":     "Child Marriage Prevention — Legal + Community",
            "description": "Enforce minimum age 18, community awareness, girls' empowerment clubs",
            "impact":   "WEI Bodily Autonomy +3.0",
            "cost":     "low-medium",
            "time":     "3-5 years",
            "example":  "Kanyashree WB — child marriage fell 40% in 5 years",
            "applies_to": ["child_marriage"],
        },
        {
            "name":     "Period Poverty Elimination Program",
            "description": "Free products + menstrual health education + school WASH + stigma reduction",
            "impact":   "WEI Bodily Autonomy +2.0, Dignity +2.5",
            "cost":     "low",
            "time":     "6-12 months",
            "example":  "Plan International — 20+ countries. Kenya government free pads 2017",
            "applies_to": ["period_poverty","dropout_period_poverty"],
        },
        {
            "name":     "Criminalise Marital Rape",
            "description": "Legal reform to remove marital exemption from rape law + enforcement",
            "impact":   "WEI Bodily Autonomy +3.5, SVI +8.0",
            "cost":     "very low (law change)",
            "time":     "immediate (law) + 3-5 years (enforcement)",
            "example":  "UK criminalised 1991. Nepal 2006. Turkey 2005. Still legal in India, Bangladesh, Pakistan",
            "applies_to": ["marital_rape","svi_low"],
        },
        {
            "name":     "Reproductive Health Community Workers",
            "description": "Trained community health workers providing contraception + reproductive info",
            "impact":   "WEI Bodily Autonomy +2.0, Health +1.5",
            "cost":     "low",
            "time":     "1-2 years",
            "example":  "Ethiopia Health Extension Workers — 38,000 deployed, MMR halved",
            "applies_to": ["reproductive_rights"],
        },
        {
            "name":     "FGM Community Abandonment Program",
            "description": "Community-led abandonment with alternative rites of passage",
            "impact":   "WEI Bodily Autonomy +3.5",
            "cost":     "low",
            "time":     "3-7 years",
            "example":  "Tostan Senegal — 6,000+ communities abandoned FGM voluntarily",
            "applies_to": ["fgm"],
        },
    ],

    # ── WEI PILLAR: ECONOMIC ──────────────────────────────────────────────────
    "economic_low": [
        {
            "name":     "Women's Self Help Group Network",
            "description": "Microfinance SHGs with business training and collective bargaining",
            "impact":   "WEI Economic +3.0, GPI Wage +1.5",
            "cost":     "low",
            "time":     "2-4 years",
            "example":  "Kudumbashree Kerala — 46 lakh members, half of all Kerala families",
            "applies_to": ["wage_gap","labour_participation","gpi_economic"],
        },
        {
            "name":     "Direct Cash Transfer to Women",
            "description": "Unconditional monthly cash directly to women's bank accounts",
            "impact":   "WEI Economic +2.5, GPI Income Poverty +3.0",
            "cost":     "medium",
            "time":     "immediate",
            "example":  "Lakshmi Bhandar WB — 24.1M women, ₹1500/month, direct autonomy",
            "applies_to": ["female_poverty","wealth_gap","gpi_economic"],
        },
        {
            "name":     "Equal Pay Legislation + Mandatory Reporting",
            "description": "Require employers to publish gender pay gap + enforce penalties",
            "impact":   "WEI Economic +2.5, GPI Wage +3.0",
            "cost":     "low (law)",
            "time":     "2-4 years",
            "example":  "Iceland Equal Pay Certification 2018 — first country to mandate it",
            "applies_to": ["wage_gap","gpi_wage"],
        },
        {
            "name":     "Maternity + Shared Parental Leave",
            "description": "Generous shared parental leave — incentivise men to take it",
            "impact":   "WEI Economic +1.5, GPI Time Poverty +2.0",
            "cost":     "medium",
            "time":     "immediate (law) + culture shift 3-5 yrs",
            "example":  "Sweden 16-month shared leave — men now take 30% of leave days",
            "applies_to": ["care_burden","gpi_time_poverty"],
        },
        {
            "name":     "Women's Digital Financial Inclusion",
            "description": "Mobile banking + digital literacy for unbanked women",
            "impact":   "WEI Economic +2.0, GPI Financial Inclusion +3.0",
            "cost":     "low",
            "time":     "1-2 years",
            "example":  "M-Pesa Kenya women agents — transformed rural financial access",
            "applies_to": ["financial_exclusion","gpi_financial"],
        },
    ],

    # ── WEI PILLAR: SAFETY & JUSTICE ─────────────────────────────────────────
    "safety_justice_low": [
        {
            "name":     "Domestic Violence Law + One-Stop Centres",
            "description": "Criminalise DV + integrated centres with legal aid, shelter, counselling",
            "impact":   "WEI Safety +3.0",
            "cost":     "low-medium",
            "time":     "1-3 years",
            "example":  "India Sakhi One-Stop Centres — 700+ operational",
            "applies_to": ["domestic_violence"],
        },
        {
            "name":     "Female Police Officers + Gender Training",
            "description": "30% female police target + mandatory DV/SGBV training + women's desks",
            "impact":   "WEI Safety +2.0, SVI reporting gap -5%",
            "cost":     "low",
            "time":     "2-3 years",
            "example":  "Rwanda 43% female police — highest reporting rates in Africa",
            "applies_to": ["police_responsiveness","reporting_gap"],
        },
        {
            "name":     "Free Legal Aid for Women's Cases",
            "description": "Free legal representation for DV, divorce, custody, property disputes",
            "impact":   "WEI Safety +2.5",
            "cost":     "low",
            "time":     "1-2 years",
            "example":  "SEWA Legal Services Gujarat — 50,000+ cases supported",
            "applies_to": ["legal_aid"],
        },
    ],

    # ── WEI PILLAR: EMPOWERMENT ───────────────────────────────────────────────
    "empowerment_low": [
        {
            "name":     "Gender Quota in Parliament + Local Government",
            "description": "Reserved seats or candidate quotas for women in all legislative bodies",
            "impact":   "WEI Empowerment +4.0",
            "cost":     "very low (law change)",
            "time":     "immediate (law) + 1 election cycle",
            "example":  "Rwanda 61% women parliament via quota — highest globally",
            "applies_to": ["parliament"],
        },
        {
            "name":     "Women's Political Leadership Pipeline",
            "description": "Mentorship, training, networking for women entering public life",
            "impact":   "WEI Empowerment +1.5",
            "cost":     "low",
            "time":     "3-5 years",
            "example":  "UN Women leadership programs — 50+ countries active",
            "applies_to": ["leadership"],
        },
    ],

    # ── WEI PILLAR: DIGNITY & WELFARE ─────────────────────────────────────────
    "dignity_welfare_low": [
        {
            "name":     "Widow Property Rights Enforcement",
            "description": "Legal aid + community paralegal network to prevent property stripping",
            "impact":   "WEI Dignity +3.0, WEVI -8 pts vulnerability",
            "cost":     "low",
            "time":     "2-5 years",
            "example":  "Kenya Succession Act enforcement campaign — 10,000 widows assisted",
            "applies_to": ["widow_rights","wevi_high"],
        },
        {
            "name":     "Widow Pension and Social Support",
            "description": "Meaningful widow pension (not symbolic ₹500/month) + social reintegration",
            "impact":   "WEI Dignity +2.5, WEVI -10 pts",
            "cost":     "medium",
            "time":     "immediate (law) + 1-2 years rollout",
            "example":  "Kerala widow pension ₹1,400/month + Kudumbashree inclusion — WEVI 28 vs India avg 69",
            "applies_to": ["widow_pension","wevi_high"],
        },
        {
            "name":     "Temple Town Widow Rehabilitation",
            "description": "Repatriation support + skill training + income + family mediation for abandoned widows",
            "impact":   "WEI Dignity +1.5 (India states)",
            "cost":     "low",
            "time":     "1-3 years",
            "example":  "Guild of Service Vrindavan — 1,500 widows with income. Sulabh International vocational training",
            "applies_to": ["temple_town_widows","india_widows"],
        },
        {
            "name":     "Subsidised Childcare",
            "description": "State-funded childcare enabling women to work and reducing care burden",
            "impact":   "WEI Dignity +2.0, GPI Time Poverty +3.0, Economic +1.5",
            "cost":     "high",
            "time":     "2-4 years",
            "example":  "Quebec $10/day childcare — female LFPR increased 12 percentage points",
            "applies_to": ["care_burden","gpi_time_poverty"],
        },
    ],

    # ── WEI PILLAR: DIGITAL & SOCIAL ──────────────────────────────────────────
    "digital_social_low": [
        {
            "name":     "Digital Literacy for Women + AI Skills",
            "description": "Community digital training including AI tools, not just basic internet",
            "impact":   "WEI Digital +2.5, WADI Digital Gap -8 pts",
            "cost":     "low",
            "time":     "1-2 years",
            "example":  "Digital Sakhi India — 150,000 women digital champions in rural areas",
            "applies_to": ["internet_gap","wadi_digital"],
        },
        {
            "name":     "Criminalise Image-Based Sexual Abuse",
            "description": "Law against non-consensual intimate images, deepfakes, sextortion",
            "impact":   "WEI Digital +1.5, SVI Digital +2.0",
            "cost":     "very low (law)",
            "time":     "immediate (law)",
            "example":  "UK Online Safety Act 2023 — intimate image abuse criminalised with up to 2yr sentence",
            "applies_to": ["online_harassment","digital_sv"],
        },
        {
            "name":     "Affordable Mobile Internet for Women",
            "description": "Subsidised data + handsets targeted at women in low-income areas",
            "impact":   "WEI Digital +2.0",
            "cost":     "low-medium",
            "time":     "1-2 years",
            "example":  "GSMA Connected Women — 30+ operators with women-specific programs",
            "applies_to": ["internet_gap","mobile_gap"],
        },
    ],

    # ── WEI PILLAR: HEALTH ────────────────────────────────────────────────────
    "health_low": [
        {
            "name":     "Community Midwife Deployment",
            "description": "Train and deploy skilled birth attendants in underserved areas",
            "impact":   "WEI Health +3.0 (MMR reduction)",
            "cost":     "low-medium",
            "time":     "2-3 years",
            "example":  "Ethiopia 38,000 Health Extension Workers — MMR halved 2000-2015",
            "applies_to": ["maternal_mortality"],
        },
        {
            "name":     "Iron Supplementation + Nutrition",
            "description": "Free iron tablets + nutritional support for women and girls in schools",
            "impact":   "WEI Health +1.5",
            "cost":     "very low",
            "time":     "6-12 months",
            "example":  "India Anaemia Mukt Bharat — weekly iron-folic acid in all schools",
            "applies_to": ["anaemia"],
        },
        {
            "name":     "HPV Vaccination + Cervical Screening",
            "description": "National HPV vaccination for girls + cervical cancer screening program",
            "impact":   "WEI Health +1.5",
            "cost":     "medium",
            "time":     "2-5 years",
            "example":  "Rwanda 93% HPV coverage — highest in Africa. UK 83% coverage.",
            "applies_to": ["cancer_screening"],
        },
    ],

    # ── GPI SPECIFIC ──────────────────────────────────────────────────────────
    "gpi_time_poverty": [
        {
            "name":     "Unpaid Care Work Recognition + Redistribution",
            "description": "Measure, reduce, and redistribute unpaid care: public services + men's share",
            "impact":   "GPI Time Poverty +5.0, WEI Economic +1.5",
            "cost":     "medium",
            "time":     "3-5 years",
            "example":  "Uruguay National Care System 2015 — state-funded care, men required to share",
            "applies_to": ["gpi_time_poverty","care_burden"],
        },
        {
            "name":     "Paternity Leave — Non-Transferable",
            "description": "Mandatory paternity leave that fathers cannot transfer to mothers",
            "impact":   "GPI Time Poverty +2.0",
            "cost":     "low (law)",
            "time":     "immediate + culture shift",
            "example":  "Sweden — 3 months non-transferable 'daddy quota'. 90% uptake.",
            "applies_to": ["gpi_time_poverty"],
        },
    ],

    "gpi_land_ownership": [
        {
            "name":     "Women's Land Title + Registration Campaign",
            "description": "Legal aid + paralegal support to register land in women's names",
            "impact":   "GPI Land +4.0, WEI Dignity +2.0",
            "cost":     "low",
            "time":     "2-4 years",
            "example":  "Ethiopia Land Certification — 6M women landholders registered, domestic violence fell 33%",
            "applies_to": ["gpi_land","land_ownership"],
        },
        {
            "name":     "Inheritance Law Reform + Enforcement",
            "description": "Amend inheritance law to ensure equal shares + community courts to enforce",
            "impact":   "GPI Land +3.0, WEVI -6 pts",
            "cost":     "very low (law)",
            "time":     "2-5 years",
            "example":  "India Hindu Succession Amendment 2005 — equal ancestral property rights",
            "applies_to": ["gpi_land","inheritance"],
        },
    ],

    "gpi_food_security": [
        {
            "name":     "Women-Led Agricultural Extension",
            "description": "Female agricultural extension workers + women's farming cooperatives",
            "impact":   "GPI Food Security +3.0",
            "cost":     "low",
            "time":     "2-3 years",
            "example":  "FAO gender-responsive agriculture — 150+ countries, 17% yield increase",
            "applies_to": ["gpi_food","food_insecurity"],
        },
    ],

    # ── SVI SPECIFIC ──────────────────────────────────────────────────────────
    "svi_low": [
        {
            "name":     "Marital Rape Criminalisation",
            "description": "Remove marital exemption from rape law — most overdue legal reform globally",
            "impact":   "SVI +8.0, WEI Bodily Autonomy +3.5",
            "cost":     "very low (law)",
            "time":     "immediate (law) + enforcement culture 5-10 yrs",
            "example":  "Still legal in India, Bangladesh, Pakistan, Indonesia, Egypt, Iran + 16 others. UK criminalised 1991.",
            "applies_to": ["marital_rape","svi_legal"],
        },
        {
            "name":     "Reduce Reporting Gap — Anonymous Reporting",
            "description": "Anonymous online/app reporting + guaranteed no police referral option",
            "impact":   "SVI reporting gap -10%, WEI Safety +1.5",
            "cost":     "very low",
            "time":     "6-12 months",
            "example":  "SHEtoken grievance app (shetoken.org/signal) — zero PII, immediate resources",
            "applies_to": ["reporting_gap","svi_underreporting"],
        },
        {
            "name":     "Rape Kit Processing + Forensic Capacity",
            "description": "Clear rape kit backlog + fund forensic labs + victim-friendly examination",
            "impact":   "SVI impunity -10%, WEI Safety +2.0",
            "cost":     "medium",
            "time":     "1-2 years",
            "example":  "End the Backlog USA campaign — 200,000 untested rape kits processed",
            "applies_to": ["impunity","svi_impunity"],
        },
        {
            "name":     "Consent-Based Rape Law Reform",
            "description": "Replace 'force-based' rape law with 'absence of consent' standard",
            "impact":   "SVI legal framework +2.0",
            "cost":     "very low (law)",
            "time":     "immediate",
            "example":  "Japan 2023 — consent law passed after decades of campaigning. Sweden 2018.",
            "applies_to": ["svi_legal","consent_law"],
        },
        {
            "name":     "Conflict SGBV Response Protocol",
            "description": "UNHCR-standard SGBV response teams in all conflict zones + mobile courts",
            "impact":   "SVI conflict score -3.0",
            "cost":     "high",
            "time":     "immediate deployment",
            "example":  "UN MONUSCO DRC — SGBV mobile courts. IRC emergency response DRC/Sudan.",
            "applies_to": ["conflict_sgbv","svi_conflict"],
        },
        {
            "name":     "Caste-Targeted Sexual Violence Law",
            "description": "Specific legal framework and fast-track courts for caste-based SGBV",
            "impact":   "SVI impunity -5% (India/similar), WEI Safety +1.5",
            "cost":     "low (law + courts)",
            "time":     "1-3 years",
            "example":  "India SC/ST Prevention of Atrocities Act — needs stronger enforcement",
            "applies_to": ["caste_targeting","dalit_women"],
        },
        {
            "name":     "Indigenous Women Protection Framework",
            "description": "Dedicated law enforcement for indigenous communities + MMIW inquiry",
            "impact":   "SVI +3.0 (indigenous populations)",
            "cost":     "medium",
            "time":     "2-4 years",
            "example":  "Canada MMIW National Inquiry 2019 — 231 calls to action. Implementation ongoing.",
            "applies_to": ["indigenous_women","mmiw"],
        },
    ],

    # ── WEVI SPECIFIC — WIDOWS ────────────────────────────────────────────────
    "wevi_high": [
        {
            "name":     "Widow Rights Legal Aid Network",
            "description": "Community paralegals trained to prevent property stripping at point of bereavement",
            "impact":   "WEVI -12 pts, GPI Land +2.0",
            "cost":     "low",
            "time":     "1-2 years",
            "example":  "ActionAid Kenya widow property program — 80% property retention rate",
            "applies_to": ["widow_rights","wevi_high"],
        },
        {
            "name":     "Widow Livelihood Program",
            "description": "Targeted skill training + microfinance + SHG membership for widows",
            "impact":   "WEVI -8 pts, GPI Income +2.0",
            "cost":     "low",
            "time":     "1-2 years",
            "example":  "Kudumbashree Kerala — explicitly includes widows in all programs",
            "applies_to": ["widow_livelihood","wevi_high"],
        },
        {
            "name":     "Anti-Widow Stigma Community Program",
            "description": "Community education on widow remarriage rights + removing inauspicious labelling",
            "impact":   "WEVI social restrictions -4 pts",
            "cost":     "very low",
            "time":     "3-5 years (culture change)",
            "example":  "Lokniti India widow remarriage campaigns, Maharashtra 'White Wedding' initiative",
            "applies_to": ["widow_stigma","wevi_social"],
        },
        {
            "name":     "Abandon Widows at Temples — Prevention + Repatriation",
            "description": "Family counselling + repatriation support + ashram income programs for temple towns",
            "impact":   "WEVI abandonment rate -3 pts (India)",
            "cost":     "low",
            "time":     "ongoing",
            "example":  "Guild of Service Vrindavan + Sulabh International — 2,000 widows with vocational income. Supreme Court 2018 order requiring state action.",
            "applies_to": ["temple_town_widows"],
        },
        {
            "name":     "Elder Women Care Homes + Day Centres",
            "description": "State-funded residential care + community day centres for elderly women without family",
            "impact":   "WEVI elder care +3.0",
            "cost":     "medium",
            "time":     "2-3 years",
            "example":  "HelpAge India state homes. Japan Silver Centre — elder women employment.",
            "applies_to": ["elderly_homeless","wevi_elder"],
        },
    ],

    # ── WADI SPECIFIC — AI DISPLACEMENT ──────────────────────────────────────
    "wadi_high": [
        {
            "name":     "Women's AI Reskilling Program",
            "description": "Funded AI/digital skills training targeted at women in high-risk sectors",
            "impact":   "WADI reskilling +15, WEI Digital +2.0",
            "cost":     "medium",
            "time":     "1-3 years",
            "example":  "Singapore SkillsFuture — S$500 credit for every adult, targeted at displaced workers",
            "applies_to": ["wadi_reskilling","ai_displacement"],
        },
        {
            "name":     "Garment Sector Just Transition Fund",
            "description": "Brand-funded transition support for garment workers displaced by automation",
            "impact":   "WADI sector exposure -10 (garment countries)",
            "cost":     "medium (brand-funded)",
            "time":     "2-5 years",
            "example":  "ACT (Action Collaboration Transformation) — multi-brand initiative for living wages via collective bargaining. See: actonlivingwages.com for full signatory list",
            "applies_to": ["garment_automation","wadi_sector"],
        },
        {
            "name":     "Care Economy Wage Parity Policy",
            "description": "Raise minimum wages in care sectors to manufacturing equivalent",
            "impact":   "GPI Wage +2.0, WADI care trap -8 pts",
            "cost":     "medium",
            "time":     "immediate (law) + enforcement",
            "example":  "New Zealand Care and Support Worker Pay Equity Settlement 2017 — 55,000 workers, 15-49% pay rise",
            "applies_to": ["care_wage_trap","wadi_care"],
        },
        {
            "name":     "Mandate Women in AI Workforce",
            "description": "30% female quota in public AI projects + STEM scholarships for girls",
            "impact":   "WADI AI capture +8, WEI Digital +1.5",
            "cost":     "low-medium",
            "time":     "3-5 years",
            "example":  "Germany Parity Act 2015 — 30% female boards. AI-specific: UNESCO AI gender roadmap",
            "applies_to": ["wadi_ai_capture","stem_girls"],
        },
        {
            "name":     "Extend Social Protection to Gig Workers",
            "description": "Portable benefits + unemployment insurance for platform/gig workers",
            "impact":   "WADI social protection +15, GPI Social Protection +3.0",
            "cost":     "medium",
            "time":     "1-2 years (law)",
            "example":  "France auto-entrepreneur + portabilité sociale — 3M gig workers covered",
            "applies_to": ["gig_vulnerability","wadi_gig"],
        },
        {
            "name":     "AI Strategy Gender Inclusion Mandate",
            "description": "Require national AI strategy to include gender impact assessment + women targets",
            "impact":   "WADI policy score +2.0",
            "cost":     "very low",
            "time":     "immediate",
            "example":  "UNESCO Recommendation on AI Ethics 2021 — 193 countries, gender chapter",
            "applies_to": ["wadi_policy","ai_gender_policy"],
        },
        {
            "name":     "Digital Skills in School Curriculum — Girls Priority",
            "description": "Compulsory coding + AI literacy in schools with girls-first enrollment",
            "impact":   "WADI digital gap -10, WEI Digital +2.5",
            "cost":     "low",
            "time":     "2-4 years",
            "example":  "Rwanda Girls in ICT — 50,000 girls trained. Estonia coding curriculum.",
            "applies_to": ["wadi_digital","stem_girls"],
        },
    ],


    # ── CORPORATE & TRADE INTERVENTIONS ──────────────────────────────────────
    # For countries rated CAUTION/AVOID/EMBARGO on WRBCS
    # These are recommendations TO GOVERNMENTS to mandate corporate behaviour
    # AND recommendations FOR COMPANIES operating in low-scoring countries

    "corporate_sourcing_caution": [
        {
            "name":     "Mandatory Supply Chain Gender Audit",
            "description": (
                "Require all companies sourcing from this country to conduct "
                "annual third-party gender audits of Tier 1 suppliers and "
                "publish results. Model: EU Corporate Sustainability Due "
                "Diligence Directive (CS3D)."
            ),
            "impact":   "WEI Safety +1.5, GPI Labour +1.0 (enforcement signal)",
            "cost":     "low (law — companies bear audit cost)",
            "time":     "1-2 years",
            "example":  "EU CS3D 2024 — mandatory for companies >1,000 employees "
                        "sourcing from high-risk countries",
            "applies_to": ["corporate_caution","wrbcs_caution"],
        },
        {
            "name":     "Women's Rights Trade Commitment (WRTC) Mandate",
            "description": (
                "Require companies sourcing from CAUTION-rated countries to "
                "commit 0.5% of annual contract value to a verified women's "
                "NGO in the origin country. Earns SHEtoken WRTC certification."
            ),
            "impact":   "Direct funding: $283M/year if 1% of US AVOID trade committed",
            "cost":     "very low (law mandating private sector commitment)",
            "time":     "immediate",
            "example":  "1% for the Planet — 5,000+ companies, $500M+ donated. "
                        "Fair Trade Premium — mandatory 1-2% on certified products.",
            "applies_to": ["corporate_caution","wrbcs_caution","wrbcs_avoid"],
        },
        {
            "name":     "Female Workforce Data Disclosure",
            "description": (
                "Require all suppliers to publish: % female workforce, "
                "gender pay ratio, female manager %, and maternity policy. "
                "Data feeds directly into WEI economic pillar."
            ),
            "impact":   "WEI Economic +0.5 (transparency signal), GPI Wage +0.5",
            "cost":     "very low",
            "time":     "immediate",
            "example":  "UK Gender Pay Gap Reporting 2017 — 10,000+ companies publishing. "
                        "Australia Workplace Gender Equality Act reporting.",
            "applies_to": ["corporate_caution","transparency"],
        },
    ],

    "corporate_sourcing_avoid": [
        {
            "name":     "Supply Chain Accord — Women's Rights",
            "description": (
                "Binding 5-year accord for major brands sourcing from "
                "AVOID-rated countries. Commits to: annual gender audit, "
                "1% of FOB to women's programs, WEI improvement targets, "
                "remediation plan, exit plan if EMBARGO triggered."
            ),
            "impact":   "Direct: funds women's programs. Indirect: WEI signal +1-2 pts",
            "cost":     "medium (brand-funded)",
            "time":     "6-12 months to negotiate",
            "example":  "Bangladesh Accord on Fire and Building Safety 2013 — "
                        "200+ brands, legally binding, 4,000 factories audited, "
                        "150,000 hazards fixed. Most successful supply chain "
                        "accountability mechanism ever created.",
            "applies_to": ["wrbcs_avoid","corporate_avoid"],
        },
        {
            "name":     "Garment Sector Just Transition Fund",
            "description": (
                "Brand-funded transition support for garment workers displaced "
                "by automation. Minimum $50/worker/year into country-level "
                "reskilling fund. Administered by ILO Better Work."
            ),
            "impact":   "WADI reskilling -10, WEI Dignity +1.5",
            "cost":     "medium (brand-funded)",
            "time":     "2-5 years",
            "example":  "ACT (Action Collaboration Transformation) — multi-brand initiative. "
                        "Full signatory list at actonlivingwages.com. "
                        "Bangladesh: $8.8B US imports, $44M/year at 0.5% would fund "
                        "reskilling for 880,000 workers.",
            "applies_to": ["wadi_high","garment_automation","wrbcs_avoid"],
        },
        {
            "name":     "Trade Tariff Adjustment — Women's Rights",
            "description": (
                "Government-level: import tariff on goods from AVOID countries, "
                "waived if importer shows women's rights certification or "
                "payment into WEI Impact Fund. "
                "Rate: 1-3% ad valorem scaled to WRBCS score gap."
            ),
            "impact":   "Revenue: $283M+/year at 1% of AVOID trade. "
                        "Incentive: companies self-certify to avoid tariff.",
            "cost":     "very low (legislative — companies pay)",
            "time":     "2-4 years (legislative path)",
            "example":  "EU Carbon Border Adjustment Mechanism (CBAM) 2023 — "
                        "carbon tariff on steel/cement/aluminium. "
                        "Uyghur Forced Labor Prevention Act 2021 — "
                        "import ban unless supply chain proven clean. "
                        "US GSP statute (19 USC 2462) — already conditions "
                        "trade preferences on labour rights: one amendment needed.",
            "applies_to": ["wrbcs_avoid","trade_policy"],
        },
        {
            "name":     "State Procurement Women's Rights Preference",
            "description": (
                "State and city governments give procurement preference to "
                "companies with WRTC certification. Companies sourcing from "
                "AVOID countries without certification excluded from "
                "state/city contracts."
            ),
            "impact":   "Market signal: $500B+ state procurement as incentive",
            "cost":     "very low",
            "time":     "1-2 years (state legislation)",
            "example":  "California SB 657 (2010) — supply chain transparency "
                        "for all companies doing business with California. "
                        "Massachusetts anti-sweatshop procurement. "
                        "NYC Fair Trade Resolution.",
            "applies_to": ["wrbcs_avoid","trade_policy","usa_state"],
        },
    ],

    "corporate_sourcing_embargo": [
        {
            "name":     "Mandatory Supply Chain Exit Plan",
            "description": (
                "Companies must publish a credible 18-month exit plan for "
                "all operations in EMBARGO-rated countries. Report under "
                "UNGP Pillar III (access to remedy). Failure to exit = "
                "exclusion from ESG indices and state procurement."
            ),
            "impact":   "Reputational: prevents brand from ESG index inclusion",
            "cost":     "very low (disclosure requirement)",
            "time":     "immediate",
            "example":  "Following 2021 Myanmar coup, major garment brands publicly announced exits "
                        "(widely reported in Reuters, FT, BBC). "
                        "For cobalt: several EV and technology companies have publicly "
                        "committed to zero artisanal DRC cobalt — see company ESG reports.",
            "applies_to": ["wrbcs_embargo"],
        },
        {
            "name":     "Critical Mineral Women's Rights Certification",
            "description": (
                "For DRC cobalt, coltan, and conflict minerals: require "
                "supply chain certification showing no SGBV at mine sites "
                "and female worker protections. Model: Dodd-Frank 1502 "
                "conflict minerals reporting, extended to women's rights."
            ),
            "impact":   "SVI conflict risk -2.0 (if enforced)",
            "cost":     "medium (certification infrastructure)",
            "time":     "2-4 years",
            "example":  "Dodd-Frank Section 1502 — conflict minerals reporting "
                        "for SEC-registered companies. "
                        "RMI Responsible Minerals Assurance Process — "
                        "needs women's rights rider added.",
            "applies_to": ["wrbcs_embargo","conflict_sgbv","drc_cobalt"],
        },
    ],

    # ── SPECIAL CASES: CONFLICT ───────────────────────────────────────────────
    "conflict_sgbv": [
        {
            "name":     "Deploy UN SGBV Response Teams",
            "description": "UNHCR-standard sexual and gender-based violence response in all active conflict zones",
            "impact":   "SVI conflict risk -3.0",
            "cost":     "high",
            "time":     "immediate",
            "example":  "IRC emergency SGBV programs — DRC, South Sudan, Syria. MSF safe spaces.",
            "applies_to": ["conflict_sgbv","svi_conflict"],
        },
        {
            "name":     "ICC Prosecution of Conflict SGBV",
            "description": "Pursue International Criminal Court prosecution of CRSV as war crime",
            "impact":   "SVI impunity -5.0 (signal effect)",
            "cost":     "medium",
            "time":     "3-10 years (legal process)",
            "example":  "ICC Ntaganda conviction 2019 (DRC) — first ICC SGBV conviction.",
            "applies_to": ["conflict_sgbv","impunity"],
        },
    ],

    # ── SPECIAL CASES: INDIA SPECIFIC ────────────────────────────────────────
    "india_specific": [
        {
            "name":     "Dalit Women's Legal Protection Unit",
            "description": "Fast-track courts + dedicated prosecutors for SC/ST Act cases involving women",
            "impact":   "SVI caste targeting -3.0, WEI Safety +1.5",
            "cost":     "low",
            "time":     "1-2 years",
            "example":  "NAVSARJAN Gujarat — Dalit women paralegal network, 10,000+ cases",
            "applies_to": ["dalit_women","caste_targeting"],
        },
        {
            "name":     "BPO/Call Centre Worker Transition Fund",
            "description": "Funded reskilling for 2M women in call centres facing automation",
            "impact":   "WADI reskilling +10 (India BPO sector)",
            "cost":     "medium",
            "time":     "2-4 years",
            "example":  "NASSCOM FutureSkills — needs gender targeting. IL&FS Skills reskilling.",
            "applies_to": ["wadi_india","bpo_automation"],
        },
    ],
}

# ── PILLAR → INTERVENTION MAPPING ────────────────────────────────────────────

PILLAR_TO_INTERVENTION = {
    # WEI pillars
    "empowerment":     "empowerment_low",
    "education":       "education_low",
    "economic":        "economic_low",
    "health":          "health_low",
    "bodily_autonomy": "bodily_autonomy_low",
    "safety_justice":  "safety_justice_low",
    "dignity_welfare": "dignity_welfare_low",
    "digital_social":  "digital_social_low",
    # Special indexes
    "gpi_time_poverty": "gpi_time_poverty",
    "gpi_land":         "gpi_land_ownership",
    "gpi_food":         "gpi_food_security",
    "svi":              "svi_low",
    "wevi":             "wevi_high",
    "wadi":             "wadi_high",
    "conflict":         "conflict_sgbv",
    # Corporate
    "corporate_caution": "corporate_sourcing_caution",
    "corporate_avoid":   "corporate_sourcing_avoid",
    "corporate_embargo": "corporate_sourcing_embargo",
}

WEI_PILLAR_COLS = {
    "empowerment":    "empowerment_score",
    "education":      "education_score",
    "economic":       "economic_score",
    "health":         "health_score",
    "bodily_autonomy":"bodily_autonomy_score",
    "safety_justice": "safety_justice_score",
    "dignity_welfare":"dignity_welfare_score",
    "digital_social": "digital_social_score",
}

# Country-specific flags that trigger additional recommendations
COUNTRY_FLAGS = {
    # Pillar-based + corporate/trade flags
    # corporate_caution = requires enhanced due diligence + NGO funding
    # corporate_avoid   = supply chain accord + just transition fund required
    # corporate_embargo = mandatory exit plan required
    "IND": ["india_specific","svi_low","wevi_high","wadi_high","corporate_caution"],
    "BGD": ["svi_low","wadi_high","garment_automation","corporate_avoid"],
    "KHM": ["svi_low","wadi_high","garment_automation","corporate_avoid"],
    "VNM": ["wadi_high","corporate_caution"],
    "PHL": ["wadi_high","corporate_caution"],
    "PAK": ["svi_low","wevi_high","wadi_high","corporate_avoid"],
    "AFG": ["svi_low","wevi_high","conflict_sgbv","corporate_embargo"],
    "NGA": ["svi_low","wevi_high","wadi_high","corporate_avoid"],
    "COD": ["conflict_sgbv","svi_low","corporate_embargo"],
    "SDN": ["conflict_sgbv","svi_low","corporate_avoid"],
    "YEM": ["conflict_sgbv","svi_low","wevi_high","corporate_embargo"],
    "ETH": ["conflict_sgbv","wadi_high","corporate_avoid"],
    "MMR": ["conflict_sgbv","corporate_avoid"],
    "JPN": ["gpi_time_poverty","wadi_high","corporate_caution"],
    "KOR": ["gpi_time_poverty","wadi_high","corporate_caution"],
    "CHN": ["wadi_high","corporate_caution"],
    "IDN": ["svi_low","corporate_caution"],
    "MEX": ["svi_low","corporate_caution"],
    "ZAF": ["svi_low","corporate_caution"],
    "USA": ["svi_low"],
    "KEN": ["svi_low","gpi_land_ownership","wevi_high","corporate_caution"],
    "TZA": ["wevi_high","gpi_land_ownership"],
    "UGA": ["wevi_high","gpi_land_ownership"],
    "CAN": ["svi_low"],
    "AUS": ["svi_low"],
    "NZL": ["wevi_high"],
    "BRA": ["svi_low","corporate_caution"],
    "LKA": ["wadi_high","corporate_caution"],
}


def generate_recommendations(country_row: dict, all_scores: dict,
                               max_recs: int = 8) -> list:
    """Generate ranked, de-duplicated policy recommendations."""
    iso = country_row.get("iso_code","")

    # Score each pillar
    pillar_scores = {
        pillar: float(country_row.get(col, 50))
        for pillar, col in WEI_PILLAR_COLS.items()
    }

    # Augment with other index scores if available
    if "gpi_time_poverty" in all_scores.get(iso,{}):
        gpi = all_scores[iso]
        if float(gpi.get("gpi_time_poverty",100)) < 50:
            pillar_scores["gpi_time_poverty"] = float(gpi["gpi_time_poverty"])
        if float(gpi.get("gpi_land_ownership",100)) < 40:
            pillar_scores["gpi_land"] = float(gpi["gpi_land_ownership"])
        if float(gpi.get("gpi_food_security",100)) < 40:
            pillar_scores["gpi_food"] = float(gpi["gpi_food_security"])

    if "svi_score" in all_scores.get(iso,{}):
        svi = float(all_scores[iso].get("svi_score",100))
        if svi < 45: pillar_scores["svi"] = svi

    if "wevi_score" in all_scores.get(iso,{}):
        wevi = float(all_scores[iso].get("wevi_score",0))
        if wevi > 55: pillar_scores["wevi"] = 100 - wevi

    if "wadi_score" in all_scores.get(iso,{}):
        wadi = float(all_scores[iso].get("wadi_score",0))
        if wadi > 55: pillar_scores["wadi"] = 100 - wadi

    if "conflict_sv_risk_score" in all_scores.get(iso,{}):
        conf = float(all_scores[iso].get("conflict_sv_risk_score",0))
        if conf >= 5: pillar_scores["conflict"] = 100 - (conf * 10)

    # Sort by weakness
    weakest = sorted(pillar_scores.items(), key=lambda x: x[1])

    recs = []
    seen = set()

    # From weakness-ranked pillars
    for pillar, score in weakest:
        if len(recs) >= max_recs: break
        key = PILLAR_TO_INTERVENTION.get(pillar)
        if not key or key not in INTERVENTIONS: continue
        for interv in INTERVENTIONS[key]:
            if interv["name"] in seen: continue
            seen.add(interv["name"])
            recs.append({
                "priority":       len(recs)+1,
                "pillar":         pillar,
                "pillar_score":   round(score,1),
                "intervention":   interv["name"],
                "description":    interv["description"],
                "impact":         interv["impact"],
                "cost":           interv["cost"],
                "time_to_impact": interv["time"],
                "proven_example": interv["example"],
            })
            if len(recs) >= max_recs: break

    # Country-specific flags
    for flag in COUNTRY_FLAGS.get(iso,[]):
        if len(recs) >= max_recs: break
        key = PILLAR_TO_INTERVENTION.get(flag, flag)
        if key not in INTERVENTIONS: continue
        for interv in INTERVENTIONS[key][:1]:
            if interv["name"] not in seen:
                seen.add(interv["name"])
                recs.append({
                    "priority":       len(recs)+1,
                    "pillar":         f"special:{flag}",
                    "pillar_score":   None,
                    "intervention":   interv["name"],
                    "description":    interv["description"],
                    "impact":         interv["impact"],
                    "cost":           interv["cost"],
                    "time_to_impact": interv["time"],
                    "proven_example": interv["example"],
                })

    # Separate corporate actions (always shown for CAUTION/AVOID/EMBARGO)
    corporate_recs = []
    corp_seen = set()
    for flag in COUNTRY_FLAGS.get(iso,[]):
        if not flag.startswith("corporate_"): continue
        key = PILLAR_TO_INTERVENTION.get(flag, flag)
        if key not in INTERVENTIONS: continue
        for interv in INTERVENTIONS[key]:
            if interv["name"] in corp_seen: continue
            corp_seen.add(interv["name"])
            corporate_recs.append({
                "priority":       len(corporate_recs)+1,
                "pillar":         f"corporate:{flag.replace('corporate_','')}",
                "pillar_score":   None,
                "intervention":   interv["name"],
                "description":    interv["description"],
                "impact":         interv["impact"],
                "cost":           interv["cost"],
                "time_to_impact": interv["time"],
                "proven_example": interv["example"],
            })

    return recs, corporate_recs


def load_scores(filename: str, key_col: str, score_cols: list) -> dict:
    path = OUTPUT_DIR / filename
    if not path.exists(): return {}
    result = {}
    with open(path,"r",encoding="utf-8") as f:
        lines=[l for l in f if not l.startswith("#")]
    for row in csv.DictReader(io.StringIO("".join(lines))):
        iso = row.get(key_col,"")
        if iso:
            result[iso] = {c:row.get(c,"") for c in score_cols}
    return result


def generate_all(year=BASELINE_YEAR):
    # Load all index scores
    baseline_path = OUTPUT_DIR / "baseline-2025.csv"
    if not baseline_path.exists():
        print("Run generate_baseline.py first"); return

    with open(baseline_path,"r",encoding="utf-8") as f:
        lines=[l for l in f if not l.startswith("#")]
    baseline = list(csv.DictReader(io.StringIO("".join(lines))))

    # Load supplementary indexes
    all_scores = {}
    for iso_col, fname, cols in [
        ("iso_code","gender-poverty-index-2025.csv",
         ["gpi_score","gpi_time_poverty","gpi_land_ownership","gpi_food_security"]),
        ("iso_code","sexual-violence-index-2025.csv",
         ["svi_score","conflict_sv_risk_score","marital_rape_criminalised"]),
        ("iso_code","widow-elderly-index-2025.csv",
         ["wevi_score"]),
        ("iso_code","ai-displacement-index-2025.csv",
         ["wadi_score","pct_female_workforce_in_high_risk_sectors"]),
    ]:
        scores = load_scores(fname, iso_col, cols)
        for iso, data in scores.items():
            all_scores.setdefault(iso, {}).update(data)

    # Generate recommendations
    all_recs = []
    by_country = {}

    for country_row in baseline:
        iso  = country_row.get("iso_code","")
        recs, corp_recs = generate_recommendations(country_row, all_scores)
        by_country[iso] = {
            "country":   country_row.get("country",""),
            "iso_code":  iso,
            "tier":      country_row.get("tier",""),
            "wei_score": country_row.get("wei_score",""),
            "recommendations": recs,
            "corporate_actions": corp_recs,
        }
        for rec in recs:
            all_recs.append({
                "country":  country_row.get("country",""),
                "iso_code": iso,
                "tier":     country_row.get("tier",""),
                "wei_score":country_row.get("wei_score",""),
                "section":  "policy",
                **rec,
                "year": year,
            })
        for rec in corp_recs:
            all_recs.append({
                "country":  country_row.get("country",""),
                "iso_code": iso,
                "tier":     country_row.get("tier",""),
                "wei_score":country_row.get("wei_score",""),
                "section":  "corporate",
                **rec,
                "year": year,
            })

    # Save CSV
    out = OUTPUT_DIR / f"policy-recommendations-{year}.csv"
    fnames = ["country","iso_code","tier","wei_score","priority","pillar",
              "pillar_score","intervention","description","impact",
              "cost","time_to_impact","proven_example","year"]
    hdr = (
        f"# SHEtoken Policy Recommendations v2 — {year}\n"
        f"# NOW COVERS: WEI all pillars, GPI, SVI, WEVI, WADI\n"
        f"# Marital rape, conflict SGBV, AI displacement, widow rights,\n"
        f"# period poverty, caste targeting, indigenous women, temple towns\n"
        f"# Every recommendation cites a proven real-world program\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    buf=io.StringIO()
    w=csv.DictWriter(buf,fieldnames=fnames,extrasaction="ignore")
    w.writeheader(); w.writerows(all_recs)
    with open(out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())

    # Save JSON
    json_out = OUTPUT_DIR / f"policy-recommendations-{year}.json"
    with open(json_out,"w",encoding="utf-8") as f:
        json.dump(by_country, f, indent=2, ensure_ascii=False)

    # Print sample outputs
    print(f"Policy Recommendations v2 — {year}")
    print("="*65)
    print(f"  Countries: {len(by_country)} | Total recommendations: {len(all_recs)}")
    print(f"\n  INDIA top 8 (all indexes):")
    for r in by_country.get("IND",{}).get("recommendations",[])[:8]:
        print(f"    {r['priority']}. [{r['pillar']:<22}] {r['intervention']}")
        print(f"       Impact: {r['impact']}")
    print(f"\n  BANGLADESH top 5:")
    for r in by_country.get("BGD",{}).get("recommendations",[])[:5]:
        print(f"    {r['priority']}. [{r['pillar']:<22}] {r['intervention']}")
    print(f"\n  DRC top 5:")
    for r in by_country.get("COD",{}).get("recommendations",[])[:5]:
        print(f"    {r['priority']}. [{r['pillar']:<22}] {r['intervention']}")
    print(f"\n  Saved: {out}")
    print(f"  Saved: {json_out}")


if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,default=BASELINE_YEAR)
    parser.add_argument("--fallback", action="store_true", help="Use hardcoded estimates (no API calls)")
    generate_all(p.parse_args().year)