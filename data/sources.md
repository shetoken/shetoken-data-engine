# WEI Data Sources
## Complete Reference for Women's Empowerment Index Data

> All WEI calculations use publicly available, internationally recognised data sources. Every score can be independently replicated and audited.

---

## Primary International Sources

### UN Women
**URL:** [data.unwomen.org](https://data.unwomen.org)
**Used for:** Political empowerment indicators, legal rights scores, violence statistics
**Update frequency:** Annual
**Coverage:** 193 countries
**Indicators used:**
- % of parliamentary seats held by women
- % of ministerial positions held by women
- Proportion of women subjected to physical/sexual violence
- Legal framework scores for gender equality

---

### World Bank Gender Data Portal
**URL:** [genderdata.worldbank.org](https://genderdata.worldbank.org)
**Used for:** Economic participation, poverty rates, financial inclusion, property rights
**Update frequency:** Annual
**Coverage:** 189 countries
**Indicators used:**
- Female labour force participation rate
- % of women with a formal bank account (Global Findex)
- Women's property ownership rights score (Women Business & the Law)
- Gender pay gap (median wages)
- Female poverty headcount ratio

---

### UNESCO Institute for Statistics (UIS)
**URL:** [uis.unesco.org](http://uis.unesco.org)
**Used for:** Female literacy rates, school enrollment, education completion
**Update frequency:** Annual
**Coverage:** 200+ countries
**Indicators used:**
- Female adult literacy rate (15+)
- Female primary school enrollment rate
- Female secondary school enrollment rate
- Female tertiary enrollment rate
- Female STEM participation rate

---

### UNODC — UN Office on Drugs and Crime
**URL:** [unodc.org/unodc/en/data-and-analysis](https://www.unodc.org/unodc/en/data-and-analysis)
**Used for:** Crime statistics — all Safety / Crime Penalty pillar indicators
**Update frequency:** Annual
**Coverage:** 180+ countries
**Indicators used:**
- Reported rape rate (per 100,000 women)
- Female homicide / femicide rate (per 100,000 women)
- Human trafficking victims — female (per 100,000)
- Acid attack and disfigurement incidents

---

### WHO Global Health Observatory (GHO)
**URL:** [who.int/data/gho](https://www.who.int/data/gho)
**Used for:** Maternal mortality, reproductive health, life expectancy, violence prevalence surveys
**Update frequency:** Annual / Biennial
**Coverage:** 194 countries
**Indicators used:**
- Maternal mortality ratio (per 100,000 live births)
- Female life expectancy at birth
- Adolescent birth rate (per 1,000 women aged 15–19)
- Access to skilled birth attendants (%)
- Survey-based domestic violence prevalence estimates

---

### ILO — International Labour Organization
**URL:** [ilostat.ilo.org](https://ilostat.ilo.org)
**Used for:** Gender pay gap, labour force participation
**Update frequency:** Annual
**Coverage:** 190+ countries
**Indicators used:**
- Gender pay gap (% difference in median wages) — ILO Global Wage Report
- Female labour force participation rate
- % of women in senior management roles

---

### OECD SIGI — Social Institutions and Gender Index
**URL:** [oecd.org/dev/gender-development/sigi](https://www.oecd.org/dev/gender-development/sigi)
**Used for:** Social norms, inheritance rights, freedom of movement, legal discrimination
**Update frequency:** Every 4 years (supplemented with annual updates)
**Coverage:** 180 countries
**Indicators used:**
- Freedom of movement score
- Inheritance rights score
- Discrimination in family law index

---

### IPU Parline — Inter-Parliamentary Union
**URL:** [data.ipu.org](https://data.ipu.org)
**Used for:** Parliamentary representation data
**Update frequency:** Monthly (used in annual WEI calculation)
**Coverage:** 193 countries
**Indicators used:**
- % of parliamentary seats held by women
- % of ministerial positions held by women

---

## India-Specific Sources

### NCRB — National Crime Records Bureau
**URL:** [ncrb.gov.in](https://ncrb.gov.in)
**Used for:** State-level crime against women data in India
**Update frequency:** Annual (Crime in India report)
**Coverage:** All Indian states and UTs
**Indicators used:**
- State-level rape reporting rate
- Domestic violence cases filed
- Dowry deaths
- Acid attack incidents
- Human trafficking cases

---

### DISE — District Information System for Education
**URL:** [dise.in](http://dise.in) / UDISE+ portal
**Used for:** State-level female enrollment and dropout data in India
**Update frequency:** Annual
**Coverage:** All Indian states
**Indicators used:**
- Female enrollment by grade (primary, secondary, senior secondary)
- Female dropout rates by grade
- Female literacy rates at district level

---

### NSSO — National Sample Survey Office
**URL:** [mospi.gov.in](https://mospi.gov.in)
**Used for:** State-level economic participation, wages, poverty data in India
**Update frequency:** Periodic (major surveys every 5 years, supplemented by PLFS annual)
**Coverage:** All Indian states
**Indicators used:**
- Female labour force participation by state (PLFS — Periodic Labour Force Survey)
- Gender wage gap at state level
- Female poverty headcount by state

---

### NFHS — National Family Health Survey
**URL:** [rchiips.org/nfhs](http://rchiips.org/nfhs)
**Used for:** State-level health and violence data for India
**Update frequency:** Every 4–5 years (NFHS-5 released 2021)
**Coverage:** All Indian states and districts
**Indicators used:**
- State-level maternal mortality
- Domestic violence prevalence (survey-based)
- Adolescent birth rate by state
- Institutional delivery rates

---

### State Government Portals
**Used for:** Verified program beneficiary counts for registered states
**Examples:**
- West Bengal: [wb.gov.in](https://wb.gov.in) — Lakshmi Bhandar, Kanyashree, Rupashree data
- Kerala: [kerala.gov.in](https://kerala.gov.in) — Kudumbashree data
- Bihar: [jeevika.bih.nic.in](https://jeevika.bih.nic.in) — JEEViKA data
- Rajasthan: [rajasthan.gov.in](https://rajasthan.gov.in) — Educate Girls supplementary data

**Note:** State government data is only used when the state has formally registered with SHEtoken and data has been independently verified.

---

## Data Quality Standards

All sources must meet the following criteria to be included in WEI calculations:

```
✓ Collected by a recognised international or national statistical body
✓ Methodology publicly documented and reproducible
✓ Country/state coverage ≥ 80% of scored nations
✓ Published within the last 2 years
✓ Not self-reported by the government being scored (for Crime Penalty pillar)
✓ Available in machine-readable format (CSV, JSON, or API)
```

---

## Underreporting Adjustment

Crime statistics are known to significantly underreport actual prevalence. SHEtoken applies the following adjustment:

```python
def adjust_for_underreporting(reported_rate, who_survey_rate=None):
    """
    Adjust reported crime rate for known underreporting bias.
    
    Where WHO survey-based prevalence data is available,
    we use the higher of the two figures.
    
    Where no survey data is available, we apply a
    conservative 3x multiplier based on global research
    (Ellsberg et al., Lancet 2008).
    """
    if who_survey_rate:
        return max(reported_rate, who_survey_rate)
    else:
        return reported_rate * 3.0
```

---

## Suggesting a New Data Source

We welcome suggestions for additional data sources that could improve WEI accuracy.

To suggest a new source:
1. Open a GitHub Issue at [github.com/shetoken/issues](https://github.com/shetoken/issues)
2. Use the label `data-source`
3. Include: source name, URL, indicators available, coverage, update frequency
4. A DAO governance vote (simple majority) is required to add new sources

---

## Data Download

All baseline and annual WEI data is available for download:

- `data/baseline-2025.csv` — Full country scores for 2025 baseline year
- `data/india-states-2025.csv` — India state scores for 2025 baseline year
- `data/schema.json` — Data structure and field definitions

---

*© 2026 SHE Foundation. Licensed under MIT.*
*All source data remains the property of the respective organisations listed above.*
