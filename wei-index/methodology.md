# WEI Methodology
## Women's Empowerment Index — Full Technical Specification v3.0

> **Version 3.0 | May 2026**
> This document is the authoritative reference for how the Women's Empowerment Index (WEI) is calculated, weighted, and applied to SHEtoken's token supply mechanics.
>
> Version 3.0 expands the index from 5 to 8 pillars, adding Bodily Autonomy, Dignity & Welfare, and Digital & Social Inclusion — making SHEtoken the most comprehensive women's empowerment index ever published.

---

## Table of Contents

1. [Overview](#1-overview)
2. [The Eight Pillars](#2-the-eight-pillars)
3. [The WEI Formula](#3-the-wei-formula)
4. [Sub-Score Normalisation](#4-sub-score-normalisation)
5. [Violence Penalty — How It Works](#5-violence-penalty--how-it-works)
6. [Community Signal Layer](#6-community-signal-layer)
7. [Country Tiers](#7-country-tiers)
8. [India State-Level Scoring](#8-india-state-level-scoring)
9. [Data Sources Per Pillar](#9-data-sources-per-pillar)
10. [Annual Update Process](#10-annual-update-process)
11. [Token Supply Mechanics](#11-token-supply-mechanics)
12. [Crisis Triggers](#12-crisis-triggers)
13. [Audit & Challenge Process](#13-audit--challenge-process)
14. [Worked Example — West Bengal](#14-worked-example--west-bengal)
15. [Comparison to Existing Indices](#15-comparison-to-existing-indices)
16. [Changelog](#16-changelog)

---

## 1. Overview

The Women's Empowerment Index (WEI) is a composite annual score calculated for every UN-recognised country and major Indian state on a **0–100 scale**.

- **0** = worst possible outcomes for women across all dimensions
- **100** = perfect equality, safety, and dignity across all dimensions
- **Global WEI** = population-weighted average of all country scores

| Property | Description |
|---|---|
| **Reproducible** | Any researcher can replicate scores using published data and this formula |
| **Auditable** | All inputs, weights, and calculations published openly on GitHub |
| **Challengeable** | A 30-day public review window follows every annual publication |
| **Actionable** | Governments and NGOs can directly improve their score |
| **Comprehensive** | The only index measuring period poverty, FGM, digital violence, caregiver burden, and dowry violence alongside traditional indicators |

---

## 2. The Eight Pillars

The WEI v3.0 is built on **eight positive pillars** plus one **violence penalty**.

---

### Pillar 1 — Empowerment (15%)

Measures women's participation in political and civic life and their legal rights.

| Indicator | Weight | Source |
|---|---|---|
| % of parliamentary seats held by women | 30% | IPU Parline |
| % of ministerial positions held by women | 20% | UN Women |
| Women's legal rights index | 25% | World Bank Women Business & the Law |
| Freedom of movement score | 15% | OECD SIGI |
| % of women in senior management | 10% | ILO |

**Direction:** Positive.

---

### Pillar 2 — Education & Literacy (12%)

Measures women's access to education at all levels, including menstrual health barriers to attendance.

| Indicator | Weight | Source |
|---|---|---|
| Female adult literacy rate (15+) | 30% | UNESCO UIS |
| Female secondary enrollment rate | 20% | UNESCO |
| Female primary enrollment rate | 15% | UNESCO |
| Female tertiary enrollment rate | 15% | UNESCO |
| Female STEM participation rate | 10% | UNESCO / OECD |
| Girls missing school due to menstruation | 10% | UNICEF / UNESCO |

**Direction:** Positive.

> **Menstrual health & school attendance:** UNICEF tracks the percentage of girls missing school due to lack of menstrual hygiene products or facilities. In some countries this accounts for 20%+ of school days lost annually — a direct driver of female literacy gaps and dropout rates.

---

### Pillar 3 — Economic Inclusion (12%)

Measures women's economic participation, employment quality, and financial access.

| Indicator | Weight | Source |
|---|---|---|
| Gender pay gap (% difference in median wages) | 25% | ILO Global Wage Report |
| Female labour force participation rate | 20% | ILO |
| % of women with a formal bank account | 15% | World Bank Global Findex |
| Formal vs informal employment rate (women) | 15% | ILO |
| Women's property ownership rights score | 15% | World Bank WBL |
| Maternity protection coverage (% workforce) | 5% | ILO |
| % of women-owned businesses | 5% | IFC / World Bank |

**Direction:** Positive.

> **Formal vs informal employment:** Female LFPR counts any work including subsistence farming and street vending. This indicator captures whether women have formal contracts, social protection, and labour rights — a fundamentally different measure of economic empowerment.

---

### Pillar 4 — Health & Survival (12%)

Measures women's health outcomes, reproductive health access, and nutritional status.

| Indicator | Weight | Source |
|---|---|---|
| Maternal mortality ratio (per 100,000 live births) | 25% | WHO GHO |
| Female life expectancy at birth | 20% | WHO / World Bank |
| Adolescent birth rate (per 1,000 aged 15–19) | 15% | WHO |
| Access to modern contraception (% women 15–49) | 10% | WHO / UNFPA |
| Cervical and breast cancer screening coverage | 10% | WHO |
| Access to skilled birth attendants (%) | 10% | WHO |
| Women's anaemia rate (%) | 10% | WHO / UNICEF |

**Direction:** Positive.

> **Anaemia rate:** WHO data shows 40%+ of women in South Asia and Sub-Saharan Africa are anaemic — a direct proxy for nutritional deprivation and the cultural norm of women eating last. Anaemia during pregnancy contributes significantly to maternal mortality.

> **Cervical/breast cancer screening:** Preventable cancers disproportionately kill women in low-income countries due to lack of screening programs. WHO tracks screening coverage as a health systems quality indicator.

---

### Pillar 5 — Bodily Autonomy (15%) ★ NEW IN V3.0

Measures women's control over their own bodies — reproductive rights, harmful traditional practices, and freedom from coercion.

| Indicator | Weight | Source |
|---|---|---|
| Reproductive rights legal score | 20% | Center for Reproductive Rights |
| Child marriage rate (% girls married before 18) | 20% | UNICEF |
| FGM prevalence (% women 15–49 affected) | 15% | UNICEF / WHO |
| Access to safe abortion (legal framework + access) | 15% | WHO / Guttmacher Institute |
| Period poverty index | 15% | Plan International / UNICEF |
| Forced marriage prevalence | 10% | UNICEF / UNFPA |
| Contraception autonomy score | 5% | WHO / DHS |

**Direction:** Positive.

> **Period poverty:** Measured as a composite of: % of women/girls unable to afford sanitary products, % of schools without private female toilets, % of women using unsafe alternatives (cloth, ash, mud). Sources: Plan International annual survey, UNICEF WASH data, national DHS surveys.

> **FGM:** Affects an estimated 200 million women and girls globally across 30 countries. UNICEF tracks prevalence rates by country. Completely absent from all existing major gender indices — SHEtoken is the first global financial index to include this.

> **Child marriage:** UNICEF tracks rates by country and trends over time. Child marriage permanently suppresses a girl's education, economic prospects, health outcomes, and political participation — it is arguably the single highest-leverage indicator of female disempowerment in Tier 3 and 4 countries.

> **Reproductive rights legal score:** The Center for Reproductive Rights publishes a country-level legal score assessing whether women have the right to contraception, abortion, and reproductive healthcare without spousal or parental permission.

---

### Pillar 6 — Safety & Justice (14%) ★ EXPANDED IN V3.0

Measures not just crime rates but access to justice, legal frameworks, and institutional responsiveness.

| Indicator | Weight | Source |
|---|---|---|
| Domestic violence prevalence rate (%) | 20% | WHO / DHS surveys |
| Domestic violence legal framework score | 15% | UN Women / World Bank WBL |
| Female homicide / femicide rate | 15% | UNODC |
| Honour-based violence index | 10% | UNFPA |
| Access to legal aid for women (%) | 10% | World Justice Project |
| Police responsiveness to women's cases | 10% | World Justice Project |
| Rape reporting rate vs impunity index | 10% | UNODC |
| Human trafficking rate (female victims) | 10% | UNODC |

**Direction:** Positive (higher score = better safety and justice access).

> **Domestic violence legal framework:** A country where DV is not criminalised has a fundamentally different structural problem than one with good laws but poor enforcement. World Bank's Women Business & the Law tracks whether DV is criminalised, whether restraining orders are available, and whether there are dedicated DV courts.

> **Honour-based violence:** UNFPA specifically tracks this for the Middle East, North Africa, and South Asia. A country can have moderate rape statistics but high honour killing rates — the current index (and all existing major indices) misses this entirely. Estimated 5,000 honour killings per year globally, the vast majority of victims being women.

> **Access to legal aid:** The World Justice Project tracks whether women can access legal representation, whether courts are accessible in their language, and whether gender-based cases receive fair hearings. A woman who cannot access justice has no protection even where good laws exist.

---

### Pillar 7 — Dignity & Welfare (10%) ★ NEW IN V3.0

Measures basic dignity, welfare security, and social inclusion — issues that fall outside traditional economic or health metrics.

| Indicator | Weight | Source |
|---|---|---|
| Period poverty index | 20% | Plan International / UNICEF |
| Widow rights & inheritance security | 20% | World Bank WBL / OECD SIGI |
| Housing security for women (eviction protection) | 15% | UN Habitat |
| Caregiver burden index (unpaid care work hours) | 15% | OECD / ILO MTUS |
| Female food insecurity rate (%) | 15% | FAO SOFI |
| Women's mental health access | 15% | WHO Mental Health Atlas |

**Direction:** Positive.

> **Period poverty** appears in both Pillar 5 (Bodily Autonomy) and Pillar 7 (Dignity & Welfare) with different weights because it has dual impact — it affects bodily autonomy and dignity simultaneously. The two measures use different sub-indicators: Pillar 5 focuses on access/affordability, Pillar 7 focuses on social stigma and institutional support.

> **Widow rights & inheritance:** In many parts of Sub-Saharan Africa and South Asia, women are legally or culturally stripped of property and housing upon their husband's death. OECD SIGI and World Bank WBL both track inheritance laws. This is a primary driver of female poverty in older women that no other major index currently measures.

> **Caregiver burden:** OECD's Multinational Time Use Study tracks unpaid care work hours by gender. In many countries women do 5–6× more unpaid care work than men. This directly suppresses LFPR, earnings, political participation, and mental health — yet no financial gender index currently measures it.

> **Female food insecurity:** FAO's State of Food Insecurity report tracks gender-disaggregated food insecurity. The "women eat last" cultural norm in many societies means women are disproportionately affected by food insecurity even within households above the poverty line.

---

### Pillar 8 — Digital & Social Inclusion (10%) ★ NEW IN V3.0

Measures the digital gender gap and protection from online and technology-facilitated violence.

| Indicator | Weight | Source |
|---|---|---|
| Online harassment prevalence (women) | 30% | ITU / Plan International |
| Internet access gender gap | 25% | ITU |
| Mobile phone ownership gender gap | 20% | GSMA Connected Women |
| Social media harassment rate (women) | 15% | Plan International |
| Cyberstalking / image abuse legal framework | 10% | UN Women |

**Direction:** Positive.

> **Online harassment:** Plan International's 2023 survey of 14,000 young women across 22 countries found 58% had experienced online harassment. ITU tracks gender-disaggregated internet safety data. This pillar is completely absent from every existing major gender index — making SHEtoken the first financial instrument to price digital safety for women.

> **Internet access gender gap:** ITU data shows globally 259 million fewer women than men use the internet. In some countries the gap is 50%+. Digital exclusion locks women out of economic opportunity, political participation, and access to support resources.

> **Mobile phone ownership gender gap:** GSMA Connected Women programme tracks gender-disaggregated mobile ownership. In many developing countries, mobile phones are the primary internet access point — the phone ownership gap directly determines the internet gap.

---

### Violence Penalty (10%) — Subtracted

The Violence Penalty captures the most severe forms of physical violence against women. It is **subtracted** from the WEI score — higher violence = lower score. A country cannot compensate for violence against women by performing well in other pillars.

| Indicator | Weight | Source |
|---|---|---|
| Reported rape rate (per 100,000 women) | 30% | UNODC |
| Acid attack rate (per 100,000 women) | 20% | UNODC / national records |
| Dowry violence rate (per 100,000 women) | 20% | NCRB (India) / UNFPA (South Asia) |
| FGM prevalence (%) | 15% | UNICEF (penalty weight only) |
| Female homicide rate (per 100,000) | 15% | UNODC |

**Direction:** Negative (penalty — subtracted from total score).

> **Dowry violence** is included here specifically for the India sub-tokens. India's NCRB records dowry deaths separately — murders or burning of women for insufficient dowry. This is a distinct category of lethal gender-based violence completely absent from all existing global indices.

---

## 3. The WEI Formula

```
WEI Score = (Empowerment         × 0.15)
          + (Education            × 0.12)
          + (Economic Inclusion   × 0.12)
          + (Health & Survival    × 0.12)
          + (Bodily Autonomy      × 0.15)
          + (Safety & Justice     × 0.14)
          + (Dignity & Welfare    × 0.10)
          + (Digital & Social     × 0.10)
          − (Violence Penalty     × 0.10)
```

Weights sum to **1.00** ✓

### Weight Rationale

| Pillar | Weight | Rationale |
|---|---|---|
| Empowerment | 15% | Political participation determines how all other pillars are resourced |
| Bodily Autonomy | 15% | Control over one's own body is the foundation of all other freedoms |
| Safety & Justice | 14% | Safety enables participation in all other pillars |
| Education | 12% | Literacy is the gateway to economic and political voice |
| Economic Inclusion | 12% | Financial independence is the most direct path from structural disadvantage |
| Health & Survival | 12% | Physical survival is the prerequisite for all other outcomes |
| Dignity & Welfare | 10% | Basic dignity and welfare security support all other pillars |
| Digital & Social | 10% | Digital inclusion is increasingly the gateway to all other opportunities |
| Violence Penalty | 10% | Violence is a non-negotiable floor — no other pillar can compensate for it |

---

## 4. Sub-Score Normalisation

Every raw indicator is normalised to 0–100 before being combined into a pillar score.

```python
def normalise(value, min_val, max_val, invert=False):
    """
    Normalise a raw value to 0-100 scale.

    Args:
        value:    Raw indicator value
        min_val:  Worst observed value globally (baseline year)
        max_val:  Best observed value globally (baseline year)
        invert:   True for indicators where higher = worse

    Returns:
        Normalised score 0-100
    """
    if max_val == min_val:
        return 50

    score = (value - min_val) / (max_val - min_val) * 100

    if invert:
        score = 100 - score

    return max(0, min(100, score))
```

### Inverted Indicators

| Indicator | Why Inverted |
|---|---|
| Maternal mortality ratio | Higher = worse outcome |
| Adolescent birth rate | Higher = worse outcome |
| Women's anaemia rate | Higher = worse outcome |
| Gender pay gap | Higher = worse outcome |
| Child marriage rate | Higher = worse outcome |
| FGM prevalence | Higher = worse outcome |
| Period poverty index | Higher = worse outcome |
| Caregiver burden index | Higher = worse outcome |
| Female food insecurity | Higher = worse outcome |
| Online harassment rate | Higher = worse outcome |
| Internet access gender gap | Higher = worse outcome |
| Rape rate | Higher = worse outcome |
| DV prevalence | Higher = worse outcome |
| Femicide rate | Higher = worse outcome |
| Trafficking rate | Higher = worse outcome |
| Acid attack rate | Higher = worse outcome |
| Dowry violence rate | Higher = worse outcome |

---

## 5. Violence Penalty — How It Works

```
Final WEI = Positive_Pillars_Sum − Violence_Penalty_Score × 0.10
```

- Maximum possible WEI = **100** (all positive pillars max, violence = 0)
- Minimum possible WEI = **−10** (theoretically, all positive = 0, violence = 100)
- In practice, scores cluster between 15 and 85

### Why a Penalty Rather Than a Standard Pillar?

> A country cannot compensate for violence against women by performing well in education, digital inclusion, or any other pillar. Physical safety is a non-negotiable floor. The penalty architecture reflects this.

### Underreporting Adjustment

Crime statistics significantly underreport actual prevalence. Where WHO survey-based prevalence estimates are available, we use the **higher of** the two figures:

```python
def adjusted_violence_rate(reported_rate, survey_rate=None):
    if survey_rate:
        return max(reported_rate, survey_rate)
    else:
        return reported_rate * 3.0  # Conservative 3x multiplier
        # Based on Ellsberg et al., Lancet 2008
```

### Crime Spike Trigger

If any country's Violence Index rises more than **15% year-over-year**, a Crisis Trigger is automatically flagged. See [Section 12](#12-crisis-triggers).

---

## 6. Community Signal Layer

The Community Signal Layer captures distress events that go unreported to official sources. It forms a **third tier of evidence** alongside official statistics and NGO verified data.

### Architecture

```
LAYER 1 — Official data (annual)
          UNODC, NCRB, WHO crime surveys
          Weight: 70% of Violence Penalty

LAYER 2 — NGO verified data (quarterly)
          Registered NGO case volumes, helpline calls
          Weight: 20% of Violence Penalty

LAYER 3 — Community signals (real-time)     ← New in v3.0
          Anonymous reports via shetoken.org/signal
          Weight: 10% of Violence Penalty
```

### Signal Categories

| Category | Sub-types |
|---|---|
| Domestic violence | Physical, emotional, financial, sexual |
| Period poverty | No access to products, missing school/work |
| Honour-based threat | Threat, restriction of movement |
| Online harassment | Cyberstalking, image abuse, threats |
| Housing insecurity | Eviction threat, forced to leave home |
| Dowry pressure | Demand, threat |
| Forced marriage | Pressure, coercion |
| Access to justice denied | Police refused report, legal aid denied |

### Privacy Architecture

```
What IS recorded:
  - Type of incident (from dropdown)
  - Country / State (not address)
  - Week of report
  - Whether reported to police (yes/no/afraid to)
  - Outcome (seeking help/already safe/ongoing)

What is NEVER recorded:
  - IP address (checked for rate limiting, then discarded)
  - Device ID
  - Name, age, or any personal information
  - Location below state/province level
  - Free text (to prevent accidental PII capture)
```

### Five-Layer Integrity Framework

**Layer 1 — Structural Cap**
Community signals carry maximum 10% weight within the Violence Penalty pillar — limiting maximum WEI impact to 1 point from full manipulation.

**Layer 2 — Statistical Anomaly Detection**
```python
flags = []
if week_count > baseline_avg * 3:
    flags.append("VOLUME_SPIKE")
if hourly_rate > max_hourly * 5:
    flags.append("VELOCITY_ANOMALY")
if geographic_entropy < 0.3:
    flags.append("GEOGRAPHIC_CLUSTER")
if temporal_entropy < 0.4:
    flags.append("TEMPORAL_CLUSTER")
```

**Layer 3 — Credibility Scoring**
Each submission receives a credibility score (0–100) based on geographic diversity, temporal consistency, NGO corroboration, and historical accuracy of signals from that region.

**Layer 4 — Three-Source Triangulation**
Community signals only reach full weight when corroborated by NGO data or official statistics. Uncorroborated signals are applied at 20% weight pending review.

**Layer 5 — Human Review Gate**
All flagged signals go to the Advisory Council within 24 hours. Confirmed manipulation is published publicly as a deterrent.

### The Reporting Gap Indicator

```
Reporting Gap = (Community Signal Rate − Official Rate) / Community Signal Rate

High gap = women experiencing violence but not reporting to police
High gap = fear, stigma, institutional failure
High gap = increases the Violence Penalty score
```

This means a country with low official crime rates but high community signals scores **worse** than one with moderate official rates and low community signals — correctly capturing suppression of reporting as a failure mode.

### Distress Resources

Every reporting page leads with crisis helplines for that country. A woman landing on the signal page may be in immediate danger. Help resources are shown before and above the report form.

---

## 7. Country Tiers

| Tier | WEI Range | Examples | Population Weight |
|---|---|---|---|
| **Tier 1** | 70–100 | Iceland, Norway, NZ, Finland | 1.0× |
| **Tier 2** | 45–69 | India, Brazil, South Africa, Mexico | 1.0× |
| **Tier 3** | 20–44 | Pakistan, Nigeria, Ethiopia | 0.8× |
| **Tier 4** | 0–19 | Yemen, Afghanistan, DRC | 0.6× |

---

## 8. India State-Level Scoring

India receives both a national score (`$SHE-IND`) and state scores.

### Additional India-Specific Indicators

| Indicator | Pillar | Source |
|---|---|---|
| Dowry death rate (per 100,000 women) | Violence Penalty | NCRB |
| Child marriage rate by state | Bodily Autonomy | NFHS-5 |
| Period poverty by state | Bodily & Dignity | NFHS-5 / UNICEF |
| Menstrual hygiene management in schools | Education | DISE / UNICEF |
| Female anaemia rate by state | Health | NFHS-5 |
| Women's inheritance rights by state | Dignity & Welfare | World Bank / state laws |
| SHG membership rate by state | Economic | NABARD |

### India Key Programs → Pillar Mapping

| Program | State | Pillar Impact |
|---|---|---|
| Lakshmi Bhandar | West Bengal | Economic Inclusion, Dignity & Welfare |
| Kanyashree | West Bengal | Education, Bodily Autonomy (reduces child marriage) |
| Kudumbashree | Kerala | Economic Inclusion, Dignity & Welfare |
| JEEViKA | Bihar | Economic Inclusion |
| Educate Girls | Rajasthan/MP | Education, Bodily Autonomy |
| Swachh Bharat (girls' toilets) | National | Education (menstrual health) |
| Mission Shakti | Odisha | Safety & Justice |
| Beti Bachao Beti Padhao | Haryana origin | Bodily Autonomy, Education |

---

## 9. Data Sources Per Pillar

| Pillar | Primary Source | Secondary Source | Update Frequency |
|---|---|---|---|
| Empowerment | IPU Parline, UN Women | World Bank WBL | Annual |
| Education | UNESCO UIS | World Bank EdStats | Annual |
| Economic | ILO, World Bank Findex | OECD | Annual |
| Health | WHO GHO | UNICEF, UNFPA | Annual |
| Bodily Autonomy | UNICEF, Center for Reproductive Rights | Guttmacher, Plan International | Annual |
| Safety & Justice | UNODC, World Justice Project | UN Women, WHO | Annual |
| Dignity & Welfare | OECD, FAO, UN Habitat | World Bank WBL | Annual/Biennial |
| Digital & Social | ITU, GSMA | Plan International | Annual |
| Violence Penalty | UNODC, WHO | NCRB (India) | Annual |
| Community Signal | shetoken.org/signal | — | Real-time → Quarterly |
| India States | NCRB, DISE, NFHS-5 | State portals | Annual/Quarterly* |

---

## 10. Annual Update Process

```
MONTH 1  — Data collection
           Pull from all primary sources
           Community signals aggregated for the year
           Flag missing or anomalous data points

MONTH 2  — Calculation
           Run normalisation scripts
           Calculate all eight pillar scores
           Apply violence penalty
           Calculate country and state WEI scores
           Flag significant YOY changes (>10 points)

MONTH 3  — Draft publication
           Publish draft WEI scores on GitHub
           Open 30-day public review window
           Accept challenges via GitHub Issues

MONTH 4  — Challenge review
           DAO governance votes on disputed data
           51% majority required to accept a challenge
           Final scores locked

MONTH 5  — Smart contract execution
           Oracle submits final WEI scores to Chainlink
           Minting or burning executed automatically
           Annual WEI Report published at shetoken.org
```

---

## 11. Token Supply Mechanics

### Minting (Supply Expansion)
```
If Global_WEI_Current > Global_WEI_Previous:
    Tokens_Minted = (Global_WEI_Current - Global_WEI_Previous) × 10,000,000
    Destination = WEI Impact Fund (DAO treasury)
```

### Burning (Supply Contraction)
```
If Global_WEI_Current < Global_WEI_Previous:
    Tokens_Burned = (Global_WEI_Previous - Global_WEI_Current) × 10,000,000
    Source = Reserve & Liquidity Pool
```

### Real-Time Signal Events

Community signals and quarterly government data create **leading indicators** that allow price discovery ahead of the annual update:

```
Week 1:  Community signal spike in region X
         → Flagged on dashboard
         → Sub-token price softens

Week 3:  Signal sustained — quarterly confirmation
         → DAO notified, emergency grants considered

Month 3: Official data confirms trend
         → Annual WEI update reflects it
         → Burn executed
```

---

## 12. Crisis Triggers

A Crisis Trigger fires when any country's Violence Index rises **more than 15% year-over-year** OR when community signals show a **sustained 3-week spike of 300%+** above regional baseline.

### Protocol

```
Step 1 — Automatic flag
         Oracle or signal engine detects threshold breach
         Red Flag alert on shetoken.org dashboard
         DAO governance vote opened

Step 2 — DAO Vote (72-hour emergency window)
         Option A: Emergency grants to affected NGOs
         Option B: Additional token burn
         Option C: Both A and B
         Option D: No additional action

Step 3 — Execution
         Winning option executed on-chain within 24 hours
         Public report published explaining the crisis and response
```

---

## 13. Audit & Challenge Process

Anyone — researcher, government, NGO, or token holder — can challenge a published WEI score:

1. Open a GitHub Issue with label `wei-challenge`
2. Provide: country/state, specific indicator(s), alternative data source, quantitative impact
3. Advisory Council reviews
4. DAO vote if challenge has merit (51% required)
5. Challenges must be submitted within **30 days** of draft publication

---

## 14. Worked Example — West Bengal

### Input Data (Illustrative 2025 Baseline)

| Pillar | Score |
|---|---|
| Empowerment | 52 |
| Education (inc. menstrual health) | 67 |
| Economic Inclusion | 52 |
| Health & Survival | 71 |
| Bodily Autonomy | 48 |
| Safety & Justice | 55 |
| Dignity & Welfare | 58 |
| Digital & Social | 52 |
| Violence Penalty | 42 |

### WEI Calculation

```
WEI (West Bengal) = (52 × 0.15)
                  + (67 × 0.12)
                  + (52 × 0.12)
                  + (71 × 0.12)
                  + (48 × 0.15)
                  + (55 × 0.14)
                  + (58 × 0.10)
                  + (52 × 0.10)
                  − (42 × 0.10)

                = 7.8 + 8.04 + 6.24 + 8.52 + 7.2
                  + 7.7 + 5.8 + 5.2 − 4.2

                = 52.3 → rounded to 52.3
```

### Impact of Kanyashree on Bodily Autonomy

If Kanyashree reduces child marriage rate from 41% to 32%:

```
Bodily Autonomy Score improves: 48 → 58

New WEI = ... + (58 × 0.15) + ...
        = 52.3 − (48 × 0.15) + (58 × 0.15)
        = 52.3 − 7.2 + 8.7
        = 53.8

Net improvement: +1.5 points
→ Triggers minting of 15,000,000 SHE tokens to Impact Fund
```

---

## 15. Comparison to Existing Indices

| Feature | WEF GGI | OECD SIGI | UN GII | UNDP GDI | **SHEtoken WEI v3** |
|---|---|---|---|---|---|
| Pillars | 4 | 5 | 3 | 2 | **8** |
| Period poverty | ❌ | ❌ | ❌ | ❌ | **✅** |
| FGM | ❌ | ⚠️ Partial | ❌ | ❌ | **✅** |
| Child marriage | ❌ | ✅ | ❌ | ❌ | **✅** |
| Dowry violence | ❌ | ❌ | ❌ | ❌ | **✅** |
| Digital violence | ❌ | ❌ | ❌ | ❌ | **✅** |
| Caregiver burden | ❌ | ⚠️ Partial | ❌ | ❌ | **✅** |
| Widow rights | ❌ | ✅ | ❌ | ❌ | **✅** |
| Honour violence | ❌ | ❌ | ❌ | ❌ | **✅** |
| Community signals | ❌ | ❌ | ❌ | ❌ | **✅** |
| Reporting gap | ❌ | ❌ | ❌ | ❌ | **✅** |
| Financially investable | ❌ | ❌ | ❌ | ❌ | **✅** |

> SHEtoken WEI v3.0 is the most comprehensive women's empowerment index ever published. This is not a marketing claim — it is a structural comparison of indicator coverage.

---

## 16. Changelog

| Version | Date | Changes |
|---|---|---|
| v1.0 | January 2026 | Initial 5-pillar methodology |
| v2.0 | May 2026 | Added state-level scoring, underreporting adjustment, Crisis Trigger |
| v3.0 | May 2026 | Expanded to 8 pillars. Added Bodily Autonomy (period poverty, FGM, child marriage, reproductive rights), Dignity & Welfare (widow rights, caregiver burden, food insecurity), Digital & Social (online harassment, internet gap). Added Community Signal Layer with integrity framework. Added employment quality sub-indicators. Added dowry violence to Violence Penalty. |

---

## Questions & Contributions

- Challenge a score: GitHub Issue `wei-challenge`
- Suggest a data source: GitHub Issue `data-source`
- Email: contact@shetoken.org
- GitHub: [github.com/shetoken](https://github.com/shetoken)

---

*© 2026 SHE Foundation. Licensed under MIT.*
*WEI methodology is open-source and freely auditable.*
