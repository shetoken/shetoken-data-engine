"""
SHEtoken Pipeline — Shared Configuration v3.0
===============================================
Constants, country lists, indicator mappings, and
directory paths used across all pipeline scripts.

Version 3.0 — expanded to 8 pillars.
"""

import os
from pathlib import Path

# ── DIRECTORY PATHS ───────────────────────────────────────────────────────────

BASE_DIR       = Path(__file__).parent
RAW_DIR        = BASE_DIR / "raw"
PROCESSED_DIR  = BASE_DIR / "processed"
MANUAL_DIR     = BASE_DIR / "manual"
OUTPUT_DIR     = BASE_DIR / "output"

for d in [RAW_DIR, PROCESSED_DIR, MANUAL_DIR, OUTPUT_DIR]:
    d.mkdir(parents=True, exist_ok=True)


# ── WEI FORMULA WEIGHTS v3.0 ─────────────────────────────────────────────────

PILLAR_WEIGHTS = {
    "empowerment":      0.15,
    "education":        0.12,
    "economic":         0.12,
    "health":           0.12,
    "bodily_autonomy":  0.15,   # NEW in v3.0
    "safety_justice":   0.14,   # EXPANDED in v3.0
    "dignity_welfare":  0.10,   # NEW in v3.0
    "digital_social":   0.10,   # NEW in v3.0
    "violence_penalty": 0.10,   # subtracted
}

# Verify weights sum to 1.0
_positive_sum = sum(v for k, v in PILLAR_WEIGHTS.items() if k != "violence_penalty")
assert abs(_positive_sum - 1.00) < 0.001, f"Pillar weights error: {_positive_sum}"


# ── TIER POPULATION WEIGHTS ───────────────────────────────────────────────────

TIER_WEIGHTS = {1: 1.0, 2: 1.0, 3: 0.8, 4: 0.6}

TIER_RANGES = {
    1: (70, 100),
    2: (45, 69.9),
    3: (20, 44.9),
    4: (0,  19.9),
}


# ── WORLD BANK INDICATOR CODES ────────────────────────────────────────────────

WB_INDICATORS = {
    # Empowerment
    "parliament_female_pct":       "SG.GEN.PARL.ZS",
    "women_business_law_index":    "SG.LAW.INDX",
    "senior_mgmt_female_pct":      "IC.FRM.FEMM.ZS",

    # Education
    "literacy_female":             "SE.ADT.LITR.FE.ZS",
    "primary_enrollment_female":   "SE.PRM.ENRR.FE",
    "secondary_enrollment_female": "SE.SEC.ENRR.FE",
    "tertiary_enrollment_female":  "SE.TER.ENRR.FE",

    # Economic
    "lfpr_female":                 "SL.TLF.CACT.FE.ZS",
    "account_ownership_female":    "FX.OWN.TOTL.FE.ZS",
    "wage_equality_index":         "IC.LGL.CRED.XQ",

    # Health
    "maternal_mortality":          "SH.STA.MMRT",
    "life_expectancy_female":      "SP.DYN.LE00.FE.IN",
    "adolescent_birth_rate":       "SP.ADO.TFRT",
    "skilled_birth_attendant":     "SH.STA.BRTC.ZS",
    "contraception_modern":        "SP.DYN.CONU.ZS",   # NEW
    "anaemia_female":              "SH.ANM.ALLW.ZS",   # NEW

    # Bodily Autonomy
    "child_marriage_rate":         "SP.M18.2024.FE.ZS", # NEW — girls married before 18

    # Economic quality
    "formal_employment_female":    "SL.EMP.WORK.FE.ZS", # NEW
    "maternity_protection":        "SH.MMR.RISK.ZS",    # proxy

    # Digital
    "internet_access_female":      "IT.NET.USER.ZS",    # disaggregated via ITU
}


# ── WHO GHO INDICATOR CODES ───────────────────────────────────────────────────

WHO_INDICATORS = {
    "maternal_mortality":          "MDG_0000000026",
    "life_expectancy_female":      "WHOSIS_000001",
    "skilled_birth_attendant":     "WHS8_110",
    "dv_prevalence":               "VIOLENCE_PARTNER",
    "anaemia_female":              "NUTRITION_ANAEMIA_REPRODUCTIVEAGE_PREVALENCE",  # NEW
    "contraception_modern":        "RHRSTAT_25",                                    # NEW
    "cervical_cancer_screening":   "NCD_CERVICAL_SCREEN",                           # NEW
}


# ── ILO STAT INDICATOR CODES ──────────────────────────────────────────────────

ILO_INDICATORS = {
    "lfpr_female":             "EAP_DWAP_SEX_AGE_RT",
    "wage_gap":                "EAR_INEE_SEX_OCU_NB",
    "employment_female":       "EMP_DWAP_SEX_AGE_RT",
    "formal_employment":       "EMP_TEMP_SEX_ECO_NB_A",  # NEW — formal vs informal
    "maternity_protection":    "SOC_PROT_SEX_AGE_NB_A",  # NEW
    "unpaid_care_work":        "SDG_T531",                # NEW — caregiver burden
}


# ── UNESCO UIS INDICATOR CODES ────────────────────────────────────────────────

UNESCO_INDICATORS = {
    "literacy_female":              "LR.AG15T99.F",
    "primary_completion_female":    "COMP.PRIMAR.F",
    "secondary_gpi":                "GER.L2.F",
    "tertiary_gpi":                 "GER.L5T8.F",
    "menstrual_school_absence":     "MENSTR.SCH.F",   # NEW — girls missing school
}


# ── UNICEF INDICATOR CODES ────────────────────────────────────────────────────

UNICEF_INDICATORS = {
    "child_marriage_rate":    "CM_MRG_W18",        # Girls married before 18
    "fgm_prevalence":         "FG_MUTL_WLTH_Q1",   # FGM prevalence (15-49)
    "period_poverty":         "WS_HYG_BSIG_SCH",   # Menstrual hygiene in schools
    "girls_out_of_school":    "ED_ROFST_L2_GPI",   # Secondary out-of-school rate
}


# ── UNODC INDICATOR CODES ─────────────────────────────────────────────────────

UNODC_INDICATORS = {
    "rape_rate":              "UNODC_RAPE",
    "femicide_rate":          "UNODC_FEMICIDE",
    "trafficking_female":     "UNODC_TIP_FEMALE",
    "acid_attacks":           "UNODC_ACID",         # where available
}


# ── ITU DIGITAL INDICATORS ────────────────────────────────────────────────────

ITU_INDICATORS = {
    "internet_female":        "i99H",               # Female internet users (%)
    "internet_male":          "i99",                # Male internet users (for gap)
    "mobile_female":          "ITU_D_MOB_SUBSC_F",  # Female mobile subscribers
}


# ── PLAN INTERNATIONAL / MANUAL INDICATORS ────────────────────────────────────
# No public API — updated manually each year from published reports

MANUAL_INDICATORS = {
    # Empowerment
    "ministerial_female_pct":    "UN Women annual data",
    "freedom_movement_score":    "OECD SIGI",

    # Bodily Autonomy
    "reproductive_rights_score": "Center for Reproductive Rights",
    "forced_marriage_rate":      "UNICEF / UNFPA",
    "contraception_autonomy":    "DHS Program",
    "period_poverty_index":      "Plan International",

    # Safety & Justice
    "honour_violence_index":     "UNFPA",
    "legal_aid_access":          "World Justice Project",
    "police_responsiveness":     "World Justice Project",

    # Dignity & Welfare
    "widow_rights_score":        "World Bank WBL / OECD SIGI",
    "housing_security_score":    "UN Habitat",
    "female_food_insecurity":    "FAO SOFI",
    "mental_health_access":      "WHO Mental Health Atlas",
    "caregiver_burden_hours":    "OECD MTUS",

    # Digital & Social
    "online_harassment_rate":    "Plan International / ITU",
    "social_media_harassment":   "Plan International",
    "cyberstalking_law_score":   "UN Women",

    # India specific
    "dowry_violence_rate":       "NCRB India",
    "shg_membership_rate":       "NABARD India",
}


# ── PILLAR INDICATOR WEIGHTS ──────────────────────────────────────────────────

PILLAR_INDICATOR_WEIGHTS = {
    "empowerment": {
        "parliament_female_pct":    0.30,
        "ministerial_female_pct":   0.20,
        "women_business_law_index": 0.25,
        "freedom_movement_score":   0.15,
        "senior_mgmt_female_pct":   0.10,
    },
    "education": {
        "literacy_female":              0.30,
        "secondary_enrollment_female":  0.20,
        "primary_enrollment_female":    0.15,
        "tertiary_enrollment_female":   0.15,
        "stem_female_pct":              0.10,
        "menstrual_school_absence":     0.10,
    },
    "economic": {
        "wage_gap":                 0.25,
        "lfpr_female":              0.20,
        "account_ownership_female": 0.15,
        "formal_employment_female": 0.15,
        "property_rights_score":    0.15,
        "maternity_protection":     0.05,
        "women_business_owners":    0.05,
    },
    "health": {
        "maternal_mortality":       0.25,
        "life_expectancy_female":   0.20,
        "adolescent_birth_rate":    0.15,
        "contraception_modern":     0.10,
        "cervical_cancer_screening":0.10,
        "skilled_birth_attendant":  0.10,
        "anaemia_female":           0.10,
    },
    "bodily_autonomy": {
        "reproductive_rights_score":0.20,
        "child_marriage_rate":      0.20,
        "fgm_prevalence":           0.15,
        "safe_abortion_access":     0.15,
        "period_poverty_index":     0.15,
        "forced_marriage_rate":     0.10,
        "contraception_autonomy":   0.05,
    },
    "safety_justice": {
        "dv_prevalence":            0.20,
        "dv_legal_framework":       0.15,
        "femicide_rate":            0.15,
        "honour_violence_index":    0.10,
        "legal_aid_access":         0.10,
        "police_responsiveness":    0.10,
        "rape_impunity_index":      0.10,
        "trafficking_female":       0.10,
    },
    "dignity_welfare": {
        "period_poverty_index":     0.20,
        "widow_rights_score":       0.20,
        "housing_security_score":   0.15,
        "caregiver_burden_hours":   0.15,
        "female_food_insecurity":   0.15,
        "mental_health_access":     0.15,
    },
    "digital_social": {
        "online_harassment_rate":   0.30,
        "internet_gender_gap":      0.25,
        "mobile_gender_gap":        0.20,
        "social_media_harassment":  0.15,
        "cyberstalking_law_score":  0.10,
    },
    "violence_penalty": {
        "rape_rate":                0.30,
        "acid_attack_rate":         0.20,
        "dowry_violence_rate":      0.20,
        "fgm_prevalence":           0.15,
        "femicide_rate":            0.15,
    },
}


# ── INVERTED INDICATORS ───────────────────────────────────────────────────────

INVERTED_INDICATORS = {
    # Health
    "maternal_mortality", "adolescent_birth_rate", "anaemia_female",
    # Economic
    "wage_gap",
    # Bodily Autonomy
    "child_marriage_rate", "fgm_prevalence", "period_poverty_index",
    "forced_marriage_rate",
    # Safety
    "dv_prevalence", "femicide_rate", "trafficking_female",
    "honour_violence_index",
    # Dignity & Welfare
    "caregiver_burden_hours", "female_food_insecurity",
    # Digital
    "online_harassment_rate", "internet_gender_gap", "mobile_gender_gap",
    "social_media_harassment",
    # Violence Penalty
    "rape_rate", "acid_attack_rate", "dowry_violence_rate",
}


# ── SCORED COUNTRIES ──────────────────────────────────────────────────────────

SCORED_COUNTRIES = [
    "ISL","NOR","FIN","SWE","DNK","NZL","DEU","CHE","CAN","AUS",
    "IRL","NLD","BEL","AUT","FRA","GBR","ESP","PRT","USA","JPN",
    "KOR","ISR","URY","ARG","BRA","CHL","COL","MEX","ZAF","CHN",
    "IND","IDN","PHL","LKA","VNM","THA","MNG","BWA","NAM","TUN",
    "MAR","KEN","GHA","RWA","KAZ","UKR","TUR","RUS","BOL","HND",
    "PER","BGD","NPL","MMR","KHM","LAO","PNG","PAK","NGA","ETH",
    "TZA","UGA","MOZ","ZMB","ZWE","CMR","CIV","GTM","HTI","EGY",
    "JOR","IRQ","SDN","YEM","AFG","COD","SYR","MLI","TCD","NER",
    "CAF","SSD","SOM",
]


# ── INDIA STATE CODES ─────────────────────────────────────────────────────────

INDIA_STATES = {
    "KL": "Kerala",       "TN": "Tamil Nadu",    "TS": "Telangana",
    "AP": "Andhra Pradesh","KA": "Karnataka",    "GA": "Goa",
    "WB": "West Bengal",  "OD": "Odisha",        "AS": "Assam",
    "HP": "Himachal Pradesh","UK": "Uttarakhand","DL": "Delhi",
    "PB": "Punjab",       "HR": "Haryana",       "MH": "Maharashtra",
    "GJ": "Gujarat",      "RJ": "Rajasthan",     "MP": "Madhya Pradesh",
    "CG": "Chhattisgarh", "JH": "Jharkhand",     "BR": "Bihar",
    "UP": "Uttar Pradesh","MN": "Manipur",       "MZ": "Mizoram",
    "ML": "Meghalaya",
}


# ── API SETTINGS ──────────────────────────────────────────────────────────────

REQUEST_TIMEOUT   = 30
REQUEST_DELAY     = 0.5
MAX_RETRIES       = 3
BASELINE_YEAR     = 2025
DATA_YEAR_RANGE   = "2018:2024"
WEI_VERSION       = "3.0"
