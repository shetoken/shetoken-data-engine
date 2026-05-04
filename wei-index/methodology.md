# WEI Methodology v3.0
## Women's Empowerment Index — Full Technical Specification

> **Version 3.0 | May 2026**
> Authoritative reference for all six SHEtoken indexes.

---

## Table of Contents

1. [WEI Formula](#1-wei-formula)
2. [The Eight Pillars](#2-the-eight-pillars)
3. [Sub-Score Normalisation](#3-sub-score-normalisation)
4. [Violence Penalty](#4-violence-penalty)
5. [Country Tiers](#5-country-tiers)
6. [Gender Poverty Index (GPI)](#6-gender-poverty-index)
7. [Sexual Violence Index (SVI)](#7-sexual-violence-index)
8. [Widow & Elderly Index (WEVI)](#8-widow--elderly-index)
9. [Women's AI Displacement Index (WADI)](#9-womens-ai-displacement-index)
10. [Corporate Compliance Score (WRBCS)](#10-corporate-compliance-score)
11. [Historical Model](#11-historical-model)
12. [Weekly Signal Mechanics](#12-weekly-signal-mechanics)
13. [Crisis Triggers](#13-crisis-triggers)
14. [Data Sources](#14-data-sources)
15. [Audit & Challenge Process](#15-audit--challenge-process)
16. [Worked Example — West Bengal](#16-worked-example--west-bengal)
17. [Changelog](#17-changelog)

---

## 1. WEI Formula

```
WEI = (Empowerment    × 0.15)
    + (Education      × 0.12)
    + (Economic       × 0.12)
    + (Health         × 0.12)
    + (Bodily Autonomy × 0.15)
    + (Safety & Justice × 0.14)
    + (Dignity & Welfare × 0.10)
    + (Digital & Social  × 0.10)
    − (Violence Penalty  × 0.10)
```

All sub-scores normalised 0–100 before applying weights.
Global WEI = population-weighted average of all country scores.

### Weight Rationale

| Pillar | Weight | Rationale |
|---|---|---|
| Empowerment | 15% | Political participation determines how all other pillars are resourced |
| Bodily Autonomy | 15% | Post-Dobbs analysis confirms this is the highest-variance pillar |
| Safety & Justice | 14% | Violence directly undermines every other pillar |
| Education | 12% | Foundation for economic participation and political voice |
| Economic | 12% | Most direct path out of structural disadvantage |
| Health | 12% | Maternal mortality and life expectancy are foundational |
| Dignity & Welfare | 10% | Widow rights, food security, care burden |
| Digital & Social | 10% | Internet access and online safety increasingly critical |
| Violence Penalty | 10% | Subtracted — cannot be compensated by other pillars |

---

## 2. The Eight Pillars

### Pillar 1 — Empowerment (15%)

| Indicator | Weight | Source |
|---|---|---|
| % parliamentary seats held by women | 30% | IPU Parline |
| % ministerial positions held by women | 20% | UN Women |
| Women's legal rights index | 25% | World Bank Women Business & the Law |
| Freedom of movement score | 15% | OECD SIGI |
| % women in senior management | 10% | ILO |

---

### Pillar 2 — Education & Literacy (12%)

| Indicator | Weight | Source |
|---|---|---|
| Female adult literacy rate (15+) | 35% | UNESCO UIS |
| Female primary enrollment | 20% | UNESCO |
| Female secondary enrollment | 20% | UNESCO |
| Female tertiary enrollment | 15% | UNESCO |
| Female STEM participation | 10% | UNESCO/OECD |

---

### Pillar 3 — Economic Inclusion (12%)

| Indicator | Weight | Source |
|---|---|---|
| Gender pay gap (% difference) | 30% | ILO Global Wage Report |
| Female LFPR | 25% | ILO |
| % women with bank account | 20% | World Bank Global Findex |
| Women's property ownership rights | 15% | World Bank WBL |
| % women-owned businesses | 10% | IFC/World Bank |

---

### Pillar 4 — Health & Survival (12%)

| Indicator | Weight | Source |
|---|---|---|
| Maternal mortality ratio (per 100K) | 35% | WHO GHO |
| Female life expectancy | 25% | WHO/World Bank |
| Adolescent birth rate | 20% | WHO |
| Skilled birth attendant access | 10% | WHO |
| Female-to-male survival ratio | 10% | World Bank |

---

### Pillar 5 — Bodily Autonomy (15%)

**New in v3.0.** Previously absent from the formula. Post-Dobbs analysis
showed this is the highest-variance pillar between states and over time.

| Indicator | Weight | Source |
|---|---|---|
| Child marriage rate (under 18) | 30% | UNICEF MICS |
| Reproductive rights legal score | 25% | Guttmacher/Human Rights Watch |
| FGM prevalence | 20% | UNICEF/WHO |
| Access to contraception | 15% | WHO/UNFPA |
| Menstrual health / period product access | 10% | UNICEF/Plan International |

**Post-Roe variation (USA):**

| State | Bodily Autonomy Score |
|---|---|
| Vermont | 94 |
| California | 94 |
| Massachusetts | 91 |
| Mississippi | 0 |
| Alabama | 0 |
| Texas | 1 |

---

### Pillar 6 — Safety & Justice (14%)

| Indicator | Weight | Source |
|---|---|---|
| DV law strength and enforcement | 30% | UN Women |
| % female police officers | 20% | UNODC |
| Free legal aid access | 20% | World Bank Justice |
| Rape reporting rate | 15% | UNODC/WHO |
| DV shelter coverage | 15% | UN Women |

---

### Pillar 7 — Dignity & Welfare (10%)

| Indicator | Weight | Source |
|---|---|---|
| Widow property rights enforcement | 25% | World Bank/HRW |
| Food insecurity gender gap | 25% | FAO SOFI |
| Unpaid care work hours ratio | 25% | ILO/OECD |
| Women's housing security | 15% | UN Habitat |
| Elder care access | 10% | HelpAge International |

---

### Pillar 8 — Digital & Social (10%)

| Indicator | Weight | Source |
|---|---|---|
| Internet gender gap | 30% | GSMA/ITU |
| Online harassment law strength | 25% | APC/ITU |
| % women in tech workforce | 25% | ILO/UNESCO |
| Mobile phone ownership gap | 20% | GSMA |

---

## 3. Sub-Score Normalisation

```python
def normalise(value, min_val, max_val, invert=False):
    if max_val == min_val:
        return 50
    score = (value - min_val) / (max_val - min_val) * 100
    if invert:
        score = 100 - score
    return max(0, min(100, score))
```

**Inverted indicators** (higher raw value = lower normalised score):
maternal mortality, adolescent birth rate, gender pay gap,
rape rate, domestic violence rate, femicide rate, trafficking rate.

---

## 4. Violence Penalty

The Violence Penalty pillar is subtracted rather than averaged.

```
Final WEI = Positive_Pillars_Sum − (Crime_Penalty_Score × 0.10)
```

**Why subtraction rather than averaging:**
A country cannot compensate for violence against women by performing
well in education. Safety is a non-negotiable floor.

**Penalty pillars:**

| Indicator | Weight | Source |
|---|---|---|
| Rape rate per 100K women | 30% | UNODC (+ WHO adjustment) |
| Domestic violence prevalence | 25% | WHO/UN Women |
| Femicide rate | 20% | UNODC |
| Trafficking rate | 15% | UNODC |
| Acid attacks / disfigurement | 10% | UNODC/national records |

**Underreporting adjustment:**
Where WHO survey-based prevalence estimates are available, they are
weighted at 70% vs 30% for UNODC reported crime to correct for
systematic underreporting bias.

---

## 5. Country Tiers

| Tier | WEI Score | Examples | Population Weight |
|---|---|---|---|
| 1 | 70–100 | Iceland, Norway, Sweden, NZ | 1.0× |
| 2 | 45–69 | India, Brazil, South Africa | 1.0× |
| 3 | 20–44 | Pakistan, Nigeria, Ethiopia | 0.8× |
| 4 | 0–19 | Afghanistan, Somalia | 0.6× |

Tier 3/4 receive reduced population weight due to higher data
uncertainty and underreporting.

---

## 6. Gender Poverty Index

```
GPI = average(d_income_poverty + d_wealth + d_wage
            + d_labour_participation + d_financial_inclusion
            + d_food_security + d_time_poverty
            + d_land_ownership + d_social_protection)
```

Each dimension scored 0–100 (100 = equality).

| Dimension | Raw measure | Formula |
|---|---|---|
| Income poverty | Female/male poverty headcount ratio | (2.0 − ratio) / 1.0 × 100 |
| Wealth | Female median wealth as % of male | Direct percentage |
| Wage | Female wage as % of male | Direct percentage |
| Labour | Female LFPR as % of male LFPR | Direct percentage |
| Financial inclusion | Female bank account % / male % | Direct percentage |
| Food security | Food insecurity gender gap % | (20 − gap) / 20 × 100 |
| Time poverty | Female unpaid hours / male unpaid hours | (10 − ratio) / 9 × 100 |
| Land ownership | Female landowners % of total | Score × 2 |
| Social protection | % women with coverage | Direct percentage |

**Coverage:** 34 countries | **Historical:** 2015–2024

---

## 7. Sexual Violence Index

**Primary measure: WHO lifetime prevalence surveys (NOT police reports)**

```
SVI = (WHO_prevalence_inverted × 0.30)
    + (reporting_gap_inverted   × 0.15)
    + (legal_framework          × 0.15)
    + (impunity_inverted        × 0.15)
    + (marital_rape_criminalised × 0.10)
    + (conflict_risk_inverted   × 0.10)
    + (support_services         × 0.05)
```

### Why WHO Prevalence — Not Police Reports

Police statistics systematically undercount rape. Countries with better
reporting infrastructure appear more dangerous than countries where women
cannot report.

```
Sweden UNODC: 188/100K | SVI: 79.7 — SAFE
Pakistan UNODC: 2/100K | SVI: 25.3 — DANGEROUS
```

Sweden reports 94× more rapes than Pakistan yet scores far safer because
WHO prevalence, legal framework, and impunity are measured correctly.

### Special Categories

| Category | Methodology |
|---|---|
| Marital rape | Binary: criminalised (1) / not (0) — affects 20+ countries |
| Conflict SGBV | 0–10 risk score from UNHCR/UN SGBV reports |
| Caste targeting | Binary flag — India (Dalit), Canada/USA (indigenous) |
| Digital SV | Separate indicator — image-based abuse, sextortion |

**Coverage:** 38 countries | **Historical:** 2015–2024

---

## 8. Widow & Elderly Index

```
WEVI = (poverty × 0.20) + (legal_inverted × 0.15)
     + (enforcement_inverted × 0.15) + (social_restrictions × 0.15)
     + (abandonment × 0.15) + (pension_inverted × 0.10)
     + (care_inverted × 0.10)
```

Higher WEVI = more vulnerable (inverted from WEI direction).

**Coverage:** 35 countries + India states + India temple towns
**Historical:** 2025 only

---

## 9. Women's AI Displacement Index

```
WADI = (sector_exposure     × 0.25)
     + (digital_gap_inverted × 0.15)
     + (reskilling_inverted  × 0.15)
     + (ai_capture_inverted  × 0.10)
     + (remote_inverted      × 0.10)
     + (social_protection_inverted × 0.10)
     + (gig_vulnerability    × 0.10)
     + (policy_gap_inverted  × 0.05)
```

Higher WADI = more vulnerable to AI displacement.

**Key data source:** McKinsey Global Institute Women in the Future
of Work (2021), WEF Future of Jobs Report 2023, ILO WESO 2024.

**Coverage:** 28 countries | **Historical:** 2025 only

---

## 10. Corporate Compliance Score

```
WRBCS = WEI(40%) + SVI(25%) + GPI(20%) + (100−WADI)(15%)
```

| Rating | Score range | Required actions |
|---|---|---|
| PREFERRED ✅ | 75+ | Standard code of conduct, publish as positive |
| ACCEPTABLE 🟢 | 55+ | Biennial audit, monitor WEI signals |
| CAUTION 🟡 | 35+ | HRIA required, NGO funding, board sign-off |
| AVOID 🔴 | 20+ | No new contracts, 18-month remediation plan |
| EMBARGO ⛔ | 0+ | Exit operations, UNGP Article 19 reporting |

---

## 11. Historical Model

### Methodology

Historical data (2015–2024) is generated using the **event-reversal model**:

```
1. Start from 2025 verified baseline
2. For target year T:
   a. REVERSE all events that happened AFTER year T
   b. Apply annual trend rates backwards (years_back = 2025 − T)
   c. Apply events OF year T
3. Recalculate composite score
```

This correctly shows:
- Afghanistan at ~28 WEI in 2020 (before Taliban), crashing to -3 in 2021
- USA bodily autonomy dropping in 2022 (post-Dobbs) by state
- COVID dip in 2020 across all countries
- West Bengal WEI jumping in 2021 (Lakshmi Bhandar launch)

### Annual Trend Rates (WEI, going forward per year)

| Pillar | Tier 1 | Tier 2 | Tier 3 | Tier 4 |
|---|---|---|---|---|
| Empowerment | 0.20 | 0.30 | 0.35 | 0.10 |
| Education | 0.15 | 0.40 | 0.50 | 0.25 |
| Economic | 0.15 | 0.25 | 0.20 | 0.10 |
| Digital | 0.40 | 0.60 | 0.55 | 0.30 |

Going backwards = subtract these rates × years_back.

---

## 12. Weekly Signal Mechanics

The weekly news agent provides **leading indicators** between annual
official data publications.

```
WEI_live = WEI_baseline × 0.90 + signal_adjustment × 0.10

signal_adjustment = weighted_signal × signal_weight × 100
signal_weight = 0.08 (max 8% of score per week)
max_weekly_delta = ±2.0 WEI points
decay_halflife = 12 weeks
```

### Signal Classification

Each article is classified by:
- **Pillar** (8 WEI pillars + violence penalty)
- **Direction** (+1 positive / -1 negative)
- **Severity** (0.0–1.0)
- **Confidence** (0.0–1.0)
- **Geography** (country + state code)

### Signal Weight by Confidence

```python
signal_value = direction × severity × confidence
delta = signal_value × 0.08 × 100
delta = max(-2.0, min(2.0, delta))
```

---

## 13. Crisis Triggers

Automatically flagged when any country's Crime Index rises >15% year-over-year.

```
Step 1: Oracle detects >15% spike
Step 2: Red flag on shetoken.org dashboard
Step 3: DAO vote opens (72-hour emergency window)
  Option A: Emergency grants from Impact Fund
  Option B: Additional token burn
  Option C: Both
  Option D: No action
Step 4: Execute on-chain within 24 hours of vote
```

---

## 14. Data Sources

| Index | Primary Sources |
|---|---|
| WEI Empowerment | IPU Parline, UN Women, World Bank WBL |
| WEI Education | UNESCO UIS, World Bank EdStats |
| WEI Economic | ILO, World Bank Findex, OECD |
| WEI Health | WHO GHO, UNICEF |
| WEI Bodily Autonomy | UNICEF MICS, Guttmacher, WHO/UNFPA |
| WEI Safety | UN Women, UNODC, World Bank Justice |
| WEI Dignity | FAO, ILO, World Bank, HelpAge |
| WEI Digital | GSMA, ITU, ILO |
| WEI Violence | UNODC, WHO (survey adjustment) |
| GPI | World Bank, ILO, OECD, FAO, Credit Suisse |
| SVI | WHO Multi-Country Study, UNODC, UNHCR, HRW |
| WEVI | UN Women, UNFPA, Loomba Foundation, HelpAge India |
| WADI | McKinsey, WEF, ILO, OECD, GSMA |
| India states | NCRB, DISE, NSSO, State Portals |
| USA states | CDC, FBI UCR, Guttmacher, BLS |

### Data Quality Standards

```
✓ Collected by recognised international or national body
✓ Methodology publicly documented
✓ Coverage ≥ 80% of scored nations
✓ Published within last 2 years
✓ Not self-reported by the government being scored
```

---

## 15. Audit & Challenge Process

Anyone — researcher, government, NGO, or token holder — can challenge a
published WEI score by opening a GitHub Issue with label `wei-challenge`.

**Required submission:**
- Country or state being challenged
- Specific indicator(s) in dispute
- Alternative data source with methodology
- Quantitative impact on score

**Review:** Advisory Council review → DAO vote if merit found
**Threshold:** Simple majority (51%) to accept challenge
**Window:** 30 days from draft publication

---

## 16. Worked Example — West Bengal

### 2025 Baseline

| Pillar | Raw Score | WEI contribution |
|---|---|---|
| Empowerment | 52 | 52 × 0.15 = 7.8 |
| Education | 67 | 67 × 0.12 = 8.0 |
| Economic | 52 | 52 × 0.12 = 6.2 |
| Health | 71 | 71 × 0.12 = 8.5 |
| Bodily Autonomy | 58 | 58 × 0.15 = 8.7 |
| Safety & Justice | 54 | 54 × 0.14 = 7.6 |
| Dignity & Welfare | 62 | 62 × 0.10 = 6.2 |
| Digital & Social | 48 | 48 × 0.10 = 4.8 |
| Violence Penalty | 42 | 42 × 0.10 = −4.2 |
| **WEI Total** | | **53.6** |

### Kanyashree Impact Simulation

If secondary enrollment rises from 78% → 85%:
- Education score: 67 → 76
- WEI: 53.6 → 54.7 (+1.1 points)
- Tokens minted: **11,000,000 SHE** to Impact Fund

### Lakshmi Bhandar Historical Impact

West Bengal WEI timeline:
```
2020: 45.9  (COVID dip)
2021: 49.3  ← Lakshmi Bhandar launches May 2021 (+3.4 pts)
2022: 49.2
2023: 50.0
2024: 50.0
```

---

## 17. Changelog

| Version | Date | Changes |
|---|---|---|
| v1.0 | Jan 2026 | Initial 5-pillar WEI |
| v2.0 | Mar 2026 | Added India state scoring, underreporting adjustment, crisis triggers |
| v3.0 | May 2026 | Added Bodily Autonomy pillar (was missing post-Roe), GPI, SVI, WEVI, WADI, WRBCS, historical model 2015–2024, weekly signal mechanics, corporate compliance, US trade exposure |

---

*© 2026 SHE Foundation. Licensed under MIT.*
*Open-source and freely auditable by any researcher, NGO, or government.*
*github.com/shetoken · methodology@shetoken.org*
