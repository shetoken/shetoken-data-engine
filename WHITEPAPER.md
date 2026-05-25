# SHE — Women's Empowerment Index Token
## Whitepaper v3.0 — May 2026

**Where S is the Dollar — She Is the Currency**

| Ticker | SHE | Blockchain | Ethereum ERC-20 + Polygon L2 |
|---|---|---|---|
| Website | shetoken.org | GitHub | github.com/shetoken |
| Email | contact@shetoken.org | Twitter | @ShetokenDAO |

---

## Abstract

SHE (Women's Empowerment Index Token) is the world's first data-backed
cryptocurrency whose value is algorithmically tied to real-world women's
empowerment outcomes. When women's conditions improve globally, tokens are
minted. When conditions worsen, tokens are burned.

Version 3.0 expands the original single-index model into a comprehensive
**Women's Rights Intelligence Platform** — six interconnected indexes, 168+
data files, a weekly AI news agent, and a corporate compliance scoring system
that makes women's rights financially measurable at the country, state, and
city level.

---

## Table of Contents

1. The Problem
2. The Solution — Six Indexes
3. The WEI Formula
4. The Gender Poverty Index (GPI)
5. The Sexual Violence Index (SVI)
6. The Widow & Elderly Vulnerability Index (WEVI)
7. The Women's AI Displacement Index (WADI)
8. The Policy Recommendation Engine
9. Corporate Women's Rights Compliance Score (WRBCS)
10. US Trade Exposure Analysis
11. Women's Rights Partner Directory
12. Enhanced Token Ecosystem — v2.0
13. Historical Data (2015–2024)
14. The Weekly News Agent
15. Geographic Coverage
16. How to Invest
17. Tokenomics
18. Token Mechanics
19. Technology & Blockchain
20. Governance
21. Roadmap
22. Legal Disclaimer

---

## 1. The Problem

Despite decades of advocacy, women face profound structural disadvantages
globally — and these disadvantages are not random. They are concentrated,
measurable, and in many cases worsening.

| Indicator | Scale | Source |
|---|---|---|
| Violence against women | 1 in 3 women experience physical/sexual violence | WHO |
| Rape underreporting | Only 1 in 10 rapes reported globally | WHO |
| Marital rape | Legal in 20+ countries including India, Pakistan, Bangladesh | UNHCR |
| Female illiteracy | Two-thirds of world's illiterate adults are women | UNESCO |
| Feminisation of poverty | Women represent 55% of those in extreme poverty | UN Women |
| Political representation | Only 26% of parliamentary seats held by women | IPU 2024 |
| Gender pay gap | Women earn 20% less than men on average | ILO |
| AI displacement | Women 2-3× more concentrated in high-automation-risk jobs | McKinsey |
| Widow poverty | 258 million widows globally; 115 million in poverty | UN Women |
| Temple town widows | 200,000+ abandoned widows at India pilgrimage sites | NHRC |
| Child marriage | 12 million girls married under 18 every year | Girls Not Brides |
| Period poverty | Girls miss 18+ school days/year due to menstruation (India) | UNICEF |

No single financial instrument simultaneously measures, tracks, and
creates economic incentive for progress across all these dimensions.

---

## 2. The Solution — Eight Indexes

SHEtoken v3.0 introduces eight interlocking indexes:

| Index | What it measures | Coverage | Token linked? |
|---|---|---|---|
| **WEI** | Women's Empowerment Index — 8 pillars | 105 countries, 174 states, 111 cities | ✅ Yes |
| **GPI** | Gender Poverty Index — 9 economic dimensions | 34 countries | Signal |
| **SVI** | Sexual Violence Index — WHO prevalence based | 38 countries | Signal (weekly) |
| **WEVI** | Widow & Elderly Vulnerability Index | 35 countries + India states | Signal |
| **WADI** | Women's AI Displacement Index | 28 countries | Signal |
| **WHI** | Women's Health Index — mental health, anaemia, menstrual, contraception | 38 countries | Signal |
| **WVI** | Women's Voice Index — online GBV, media, tech, civil-society freedom | 38 countries | Signal (weekly) |
| **WRBCS** | Corporate Women's Rights Compliance Score | 30 countries + 36 US states | Due diligence |
| **Partner Directory** | Country, program + company finder for women's work | 15 countries, 14 programs, 6 registries | Discovery tool |

**The WEI drives the token.** The other seven indexes provide intelligence,
policy recommendations, and corporate due diligence data. Two of them —
**SVI and WVI** — are news-sensitive and update weekly from the agent's
signals; the rest are structural and refresh monthly. WHI and WVI currently
ship as transparent modeled estimates (each row carries a `data_source` flag),
with verified WHO / V-Dem / DHS data pulls on the roadmap.

---

## 3. The WEI Formula

```
WEI = (Empowerment × 0.15) + (Education × 0.12) + (Economic × 0.12)
    + (Health × 0.12) + (Bodily Autonomy × 0.15)
    + (Safety & Justice × 0.14) + (Dignity & Welfare × 0.10)
    + (Digital & Social × 0.10) − (Violence Penalty × 0.10)
```

**Score: 0–100 | Iceland: 93.4 | Global avg: 56.0 | Somalia: 5.2**

### The Eight Pillars

| Pillar | Weight | Key Indicators |
|---|---|---|
| Empowerment | 15% | Parliament seats, ministerial roles, legal rights, freedom of movement |
| Education | 12% | Female literacy, enrollment rates, STEM participation |
| Economic | 12% | Wage gap, LFPR, bank account access, property rights |
| Health | 12% | Maternal mortality, life expectancy, reproductive healthcare |
| Bodily Autonomy | 15% | Child marriage rate, FGM, period product access, reproductive rights |
| Safety & Justice | 14% | DV law, female police, legal aid access, reporting rate |
| Dignity & Welfare | 10% | Widow rights, food insecurity, housing, care burden |
| Digital & Social | 10% | Internet gender gap, online harassment law, women in tech |
| Violence Penalty | 10% | Rape rate, femicide, trafficking (subtracted) |

### Why Bodily Autonomy at 15%

The original v1.0 formula did not include Bodily Autonomy as a distinct
pillar. The post-Roe US data makes the case: Mississippi bodily autonomy
score 0/100 vs Vermont 94/100 — same country, same year. A formula that
doesn't capture this cannot reflect women's real conditions.

---

## 4. The Gender Poverty Index (GPI)

The GPI answers a different question from the WEI:
**Not "are women empowered?" but "how equal is women's economic position vs men's?"**

```
GPI = average(income_poverty + wealth + wage + labour_participation
            + financial_inclusion + food_security + time_poverty
            + land_ownership + social_protection)

Score: 100 = perfect equality | 50 = women at half of men | 0 = total exclusion
```

### The Time Poverty Innovation

No existing index tracks unpaid care work as an economic dimension.
The GPI does. Women in India perform 5.8× more unpaid care work than men.
In Japan 3.8×. This suppresses careers, wages, and political participation
— but is invisible in all traditional poverty statistics.

### Key GPI Findings

| Country | GPI | Weakest dimension | Notes |
|---|---|---|---|
| Iceland | 91.0 | Minor wage gap | Near-equality across all 9 dimensions |
| Japan | 77.3 | Time poverty 3.8× | High WEI but GPI reveals hidden inequality |
| India | 43.2 | Land ownership 14% | Women own 14% of land despite 50% of population |
| Afghanistan | 16.7 | Everything | Near-zero on all 9 dimensions |

---

## 5. The Sexual Violence Index (SVI)

### The Most Important Methodological Decision

**The SVI uses WHO survey-based prevalence — NOT police-reported crime statistics.**

All existing violence indices use police reports. This is a fundamental
methodological error: countries with better reporting infrastructure
(Sweden, Norway) appear more dangerous than countries where women
cannot report (Pakistan, Afghanistan).

```
Sweden UNODC rate:  188 per 100K | SVI score: 79.7 (safe)
Pakistan UNODC rate: 2 per 100K  | SVI score: 25.3 (dangerous)
```

Sweden reports 94× more rapes than Pakistan yet scores far safer —
because WHO lifetime prevalence, legal framework, and impunity are measured.

### What SVI Tracks That Others Don't

- **Marital rape legal status** — still legal in 20+ countries including
  India, Pakistan, Bangladesh, Indonesia, Egypt, Iran
- **Conflict SGBV** — DRC (48+ women raped per hour at conflict peak),
  Sudan, Myanmar, South Sudan
- **Reporting gap** — India: 98% of rapes never reported
- **Impunity** — UK: only 5.2% of reported rapes lead to conviction
- **Caste-based targeting** — India Dalit women, Canada/USA indigenous women
- **Digital sexual violence** — non-consensual images, sextortion, deepfakes

### India Rape Count

| Measure | Annual count |
|---|---|
| NCRB officially reported | 35,300 |
| WHO-estimated actual | **5,648,000** |
| Multiplier | 160× |
| Marital rape status | Not criminalised |

---

## 6. The Widow & Elderly Vulnerability Index (WEVI)

India has **42.4 million widows** — the largest widow population globally.
55% live in poverty. Only 18% receive any pension (₹200-500/month).

### The Temple Town Crisis

| City | Documented abandoned widows | Condition |
|---|---|---|
| Vrindavan | ~15,000 | Sing bhajans for 2kg rice/day |
| Varanasi | ~12,000 | Brought to die at Kashi, beg at ghats |
| Puri | ~8,000 | Shaved heads, denied temple entry |
| Mathura | ~6,000 | Abandoned at Krishna temples |
| Tirupati | ~4,000 | Beg outside world's wealthiest temple |
| **Total documented** | **~45,000** | True estimate: **200,000+** |

The WEVI score: India 69.2/100 (higher = more vulnerable).
Kerala: 28/100 — the Kudumbashree effect.

---

## 7. The Women's AI Displacement Index (WADI)

AI and automation are not gender-neutral. Women are 2–3× more concentrated
in high-automation-risk jobs than men.

### The Most Exposed Occupations

| Occupation | Automation risk | Female % |
|---|---|---|
| Medical transcriptionists | 98% | 89% |
| Secretaries | 96% | 94% |
| Receptionists | 96% | 93% |
| Bank tellers | 98% | 70% |
| Cashiers | 97% | 73% |
| Payroll clerks | 98% | 82% |

### The Care Economy Paradox

Nursing, childcare, social work — **automation-resistant but systematically
underpaid**. When women are displaced from admin and garment work, they
will flow into care work. Supply increases. Wages stay suppressed.
This is not a solution. It is a wage trap.

### Critical Countries

| Country | WADI | Why |
|---|---|---|
| Cambodia | 86.3 | 90% of garment workers female, near-zero reskilling |
| Bangladesh | 82.7 | 4M women garment workers face automation by 2030 |
| Ethiopia | 82.4 | Chinese-owned factories automating fastest |
| Philippines | 64.9 | 1.3M women in BPO — 79% automation risk |
| India | 69.8 | 230M+ women in high-risk sectors |

---

## 7b. The Women's Health Index (WHI)

Mainstream gender indices systematically ignore the dimensions of women's
health that matter most day to day. The WHI captures four:

| Dimension | Why it matters | Source (roadmap) |
|---|---|---|
| Female mental health | Depression, anxiety, suicide — almost never measured in gender indices | WHO GHO |
| Anaemia in women 15–49 | Sharp poverty-and-nutrition signal; India 57% (NFHS-5) | WHO |
| Menstrual health & dignity | Period poverty drives school dropout | UNICEF / DHS / MICS |
| Contraceptive unmet need | The clearest practical measure of bodily autonomy | UN Population Division |

WHI is scored 0–100, higher = better. It is a structural index (refreshes
monthly). It currently ships as transparent modeled estimates — solid global
data exists for anaemia, suicide, and contraceptive unmet need; menstrual
health is patchy and flagged as such via each row's `data_source`. The
verified-data version replaces estimates per indicator without changing the
schema.

---

## 7c. The Women's Voice Index (WVI)

Voice is the most neglected dimension of gender measurement and the one most
aligned with SHEtoken's mission. The WVI captures four:

| Dimension | Why it matters | Source (roadmap) |
|---|---|---|
| Online gender-based violence | Fastest-growing, least-measured form of abuse | EIU / regional |
| Women in media & journalism | Voice in the literal sense — who tells the story | GMMP |
| Women in tech & AI | Who builds the tools that shape the future | ILO |
| Civil-society freedom for women | Can women organise and protest? Maps to V-Dem WCSP and the Georgetown Women, Peace & Security Index | V-Dem |

WVI is scored 0–100, higher = stronger voice. It is **news-sensitive**: a
journalist crackdown or internet shutdown moves it within the week via the
agent (see Section 14). The civil-society dimension's alignment with the
Georgetown WPS framework gives the index academic grounding.

---

## 8. The Policy Recommendation Engine

Every country receives ranked, evidence-based policy recommendations
derived from all index scores combined — each citing a proven real-world program.

### Two-Section Output

Every country now has two separate recommendation sections:

**Section 1 — Government Policy Actions** — what governments must do to improve scores.

**Section 2 — Corporate Actions** — what companies sourcing from this country must do.
Driven by WRBCS rating: CAUTION → audit + NGO fund. AVOID → Supply Chain Accord. EMBARGO → exit plan.

### Sample Output — India Top Priorities

| Priority | Pillar | Intervention | Proven Example | Impact |
|---|---|---|---|---|
| 1 | GPI Land | Women's Land Title Campaign | Ethiopia — DV fell 33% after registration | GPI Land +4.0 |
| 2 | WADI | AI Reskilling Program | Singapore SkillsFuture | WADI -15 pts |
| 3 | WADI | Garment Just Transition Fund | ACT Fund (H&M, Zara) | Sector exposure -10 |
| 4 | SVI | Criminalise Marital Rape | UK 1991 — zero cost, law change only | SVI +8.0 |
| 5 | WEVI | Temple Town Rehabilitation | Guild of Service Vrindavan | WEVI -5 pts |

### Sample Output — Bangladesh Top Priorities

| Priority | Intervention | Impact |
|---|---|---|
| 1 | Garment Sector Just Transition Fund | 4M workers |
| 2 | Criminalise Marital Rape | SVI +8.0 |
| 3 | AI Reskilling Program | WADI -15 |
| 4 | Extend Social Protection to Gig Workers | GPI +3.0 |
| 5 | Female Police + Gender Training | SVI reporting gap -10% |

---

## 9. Corporate Women's Rights Compliance Score (WRBCS)

A due diligence rating for companies deciding where to outsource,
invest, or source from.

```
Composite = WEI(40%) + SVI(25%) + GPI(20%) + (100-WADI)(15%)
```

| Rating | Score | Meaning |
|---|---|---|
| ✅ PREFERRED | 75+ | Actively prioritise. Publish as ESG positive. |
| 🟢 ACCEPTABLE | 55+ | Standard due diligence. Annual monitoring. |
| 🟡 CAUTION | 35+ | Human Rights Impact Assessment required. Fund local NGO. |
| 🔴 AVOID | 20+ | No new contracts. 18-month remediation plan required. |
| ⛔ EMBARGO | 0+ | Exit existing operations. Report under UNGP Article 19. |

### Country Ratings

**PREFERRED ✅** — Iceland, Norway, Sweden, Germany, Canada, Australia

**ACCEPTABLE 🟢** — UK, Japan, South Korea, Brazil

**CAUTION 🟡** — India, China, Philippines, Vietnam, Indonesia, Mexico, South Africa

**AVOID 🔴** — Bangladesh, Pakistan, Cambodia, Nigeria, Ethiopia, Myanmar

**EMBARGO ⛔** — Afghanistan, DRC, Somalia

### USA State Ratings (Post-Dobbs)

**PREFERRED ✅** — Vermont (94), California (94), Massachusetts (91)

**AVOID 🔴** — Mississippi (0), Alabama (0), Texas (1), Louisiana (0), Kentucky (0)

---

## 10. US Trade Exposure Analysis

**$28.3 billion per year** flows from US companies to AVOID/EMBARGO countries.

| Country | US Trade/yr | Female % of workforce |
|---|---|---|
| Bangladesh | $8.8B | 72% — garment workers |
| Nigeria | $7.6B | 42% — oil sector |
| Pakistan | $4.8B | 54% — textiles |
| Cambodia | $4.0B | **90%** — garment workers |
| DRC | $1.0B | 28% — **cobalt in iPhones and EVs** |

### The 1% Commitment

If US companies sourcing from AVOID/EMBARGO countries committed just
**1% of contract value** to verified women's programs:

- Annual contribution: **$283 million**
- That equals 35% of UN Women's entire annual budget
- Generated from business that's already happening

### Four Policy Mechanisms

**1. Voluntary WRTC** (Women's Rights Trade Commitment) — companies commit
1% to WEI Impact Fund, earn certification badge. Model: 1% for the Planet.

**2. Supply Chain Accord** — binding 5-year commitment by major brands.
Model: Bangladesh Accord on Fire and Building Safety (200+ brands, legally
binding, 4,000 factories audited). Target: Walmart, H&M, Nike, Apple, Tesla.

**3. Trade Tariff (WRTA)** — import tariff on AVOID/EMBARGO goods, waived
if company shows women's rights certification. Model: EU Carbon Border
Adjustment Mechanism. Legislative path: amend US GSP statute (19 USC 2462).

**4. State Procurement Preference** — California, New York, Massachusetts
give procurement preference to WRTC-certified companies. Combined
procurement: $500B+/year. Model: California SB 657 supply chain law.

---


## 11. Women's Rights Partner Directory

The compliance score tells you where **not** to operate.
The partner directory tells you who to work **with**.

Three search tools:

### Country Partners
Which countries have the strongest ecosystems for women-focused work?

| Country | Best for | Flagship program |
|---|---|---|
| Kerala, India | SHG microfinance, elder care, health | Kudumbashree — 4.6M members |
| West Bengal, India | Girls education, cash transfer | Kanyashree — 10M girls |
| Gujarat, India | Labour rights, cooperatives | SEWA — 3.78M members |
| Rwanda | Women in governance, ICT | 61% women in parliament |
| Iceland | Equal pay law, corporate governance | Equal Pay Certification |
| Kenya | Mobile financial inclusion, tech | M-Pesa women agents |
| Colombia | Post-conflict rights, reproductive | Peace Agreement gender chapter |
| Uruguay | Care economy, reproductive rights | National Care System |

### Program Partners
Proven interventions available for funding, replication, or partnership.
Every program listed has verified outcome data.

| Program | Country | Sector | Scale | Cost per beneficiary |
|---|---|---|---|---|
| Kanyashree | India/WB | Girls education | 10M girls | ~$20/girl/year |
| Educate Girls | India/RJ | Girls education | 6.7M | Verified DI Bond |
| Kudumbashree | India/KL | Women's SHG | 4.6M members | Low |
| SEWA | India/GJ | Labour rights | 3.78M | Self-sustaining |
| Iceland Equal Pay | Iceland | Corporate pay | National | Law change only |
| NZ Pay Equity Act | NZ | Care economy | 55,000 workers | +15-49% wages |
| Ethiopia Land Cert | Ethiopia | Land rights | 6M women | DV fell 33% |
| Tostan FGM | Senegal | Bodily autonomy | 6,000+ communities | Community-led |

### Company Partners
Rather than naming specific companies — which creates legal risk if their
status changes — the directory points to six independently maintained
public registries:

- **EPIC** — Equal Pay International Coalition certified employers
- **ILO Better Work** — Garment sector buyer partners (publicly listed)
- **B Corp directory** — Gender lens filter, 6,000+ certified companies
- **2X Challenge** — Gender lens investor portfolio
- **UN WEPs** — Women's Empowerment Principles signatories (3,000+ companies)
- **GenderSmart** — Impact investors funding women's initiatives

## 12. Historical Data (2015–2024)

All major indexes include historical data using the event-reversal model:
start from 2025 verified baseline, reverse known events going backwards.

### Key Historical Events Encoded

| Year | Event | Countries affected | Score change |
|---|---|---|---|
| 2020 | COVID-19 global regression | All | -2 to -5 WEI pts |
| 2021 | Taliban takeover | Afghanistan | -40 WEI pts |
| 2021 | Myanmar coup | Myanmar | -8 WEI pts |
| 2021 | Lakshmi Bhandar launch | India/WB | +3 WEI pts |
| 2022 | Dobbs/Roe overturned | USA states | -20 to 0 bodily autonomy |
| 2023 | Japan consent-based rape law | Japan | SVI +7 pts |
| 2023 | Sudan civil war escalation | Sudan | -8 SVI pts |
| 2024 | Mexico first female president | Mexico | Empowerment +4 pts |

### Historical Coverage by Index

| Index | Coverage | Historical |
|---|---|---|
| WEI Countries | 105 | ✅ 2015–2024 |
| WEI India States | 25 | ✅ 2015–2024 |
| WEI USA States | 50 | ✅ 2015–2024 |
| WEI Top 20 Cities | 20 | ✅ 2015–2024 |
| GPI | 34 | ✅ 2015–2024 |
| SVI | 38 | ✅ 2015–2024 |
| WEVI | 35 | 2025 only |
| WADI | 28 | 2025 only |

---


## 13. Enhanced Token Ecosystem — v2.0

The original SHEtoken (v1.0) had one token with annual price discovery.
v2.0 adds four complementary instruments that provide price signals
at every frequency — from real-time to annual.

### The Problem v2.0 Solves

```
v1.0: Annual WEI update = 364-day price vacuum filled by speculation
v2.0: Price discovery at every frequency — real-time to annual
```

### Five Token Types

| Token | What it is | Yield | Update frequency |
|---|---|---|---|
| **SHE** | Master WEI index token | Staking rewards | Annual + Weekly signals |
| **SHE-MFI** | Microfinance bond basket | 6.2–11.2% APY | Daily (bond NAV) |
| **SHE-SAVE** | Women's savings account | 7.5–9.5% APY | Daily |
| **SHEETF** | She-Economy ETF basket | Dividend + growth | Real-time (stock prices) |
| **SHE-STAKE** | Corporate certification | 2–8% APY | Real-time (stake events) |

### SHE-MFI — Microfinance Bond Basket

Basket of bonds from 12 women-focused microfinance institutions.
Every institution: 70%+ female clients, independently audited, rated debt.

| Institution | Country | Yield | Female clients |
|---|---|---|---|
| Grameen Bank | Bangladesh | 6.2% | 97% |
| BRAC | Bangladesh | 6.8% | 95% |
| Women's World Banking | Global | 5.4% | 100% |
| SEWA Bank | India | 8.4% | 100% |
| JEEViKA bonds | India | 7.8% | 100% |
| Equity Bank Women | Kenya | 9.4% | 68% |

**Total:** 25.1M women borrowers | $9.78B portfolio | 7.5% weighted yield

Build on: Goldfinch, Centrifuge, or Maple Finance protocol.

### SHE-SAVE — Women's Savings Account

The most accessible entry point. $1 minimum deposit.

```
Yield = MFI bond yield (base 7.5%) + WEI performance bonus (0-2%)
      = up to 9.5% APY total

Comparison:
  Indian bank savings account:  2-3%
  Indian fixed deposit:         6-7%
  SHE-SAVE:                     7.5-9.5% + social impact
```

Target markets: 570M women across four countries.

| Country | Platform | Users | Entry point |
|---|---|---|---|
| India | UPI (PhonePe/Paytm) | 400M | ₹100 minimum |
| Kenya | M-Pesa | 30M | KES 100 minimum |
| Bangladesh | bKash | 50M | BDT 100 minimum |
| Nigeria | Opay/Kuda | 40M | NGN 500 minimum |

Chain: Celo (mobile-first, $0.001 gas fee).
Build on: Celo + Impact Market infrastructure.

### SHEETF — She-Economy ETF Token

Basket of 30 publicly traded companies meeting verified women's
rights criteria. NAV updates in real-time during market hours.

**Inclusion criteria:**
- Female board members ≥ 30% (public filing verified)
- Headquartered in WRBCS PREFERRED or ACCEPTABLE country
- At least one: B Corp, UN WEPs signatory, EPIC certified, ILO Better Work
- Not in AVOID country without WRTC certification

**Management fee:** 0.35% (0.20% → WEI Impact Fund | 0.15% → operations)

**vs MSCI Women's Leadership Index:**
SHEtoken adds WEI integration, WRBCS country screening, retail access from $1,
and routes fee to Impact Fund. MSCI is institutional only with no impact routing.

Build on: Synthetix or Set Protocol.

### SHE-STAKE — Corporate Certification Staking

Companies sourcing from CAUTION/AVOID countries stake SHE tokens
as proof of commitment. Slashed if certification lapses. Yield earned
when their supplier regions show WEI improvement.

| Tier | Country rating | Stake | Slash | Yield (if good) |
|---|---|---|---|---|
| Bronze | CAUTION | 10,000 SHE | 20% | 2% APY |
| Silver | AVOID | 50,000 SHE | 25% | 4% APY |
| Gold | AVOID + Accord | 250,000 SHE | 30% | 8% APY |

### Prediction Markets

15 live markets resolving on SHEtoken's own index publications.
Collateral: SHE tokens. Platform fee: 0.5% → WEI Impact Fund.

Example markets:
- "Will India criminalise marital rape by 2027?" — 22% yes
- "Will Kanyashree reach 12M girls by 2026?" — 58% yes
- "Will Texas bodily autonomy exceed 20 by 2028?" — 18% yes

Creates continuous trading activity between annual WEI updates.

### Price Discovery Calendar (v2.0)

```
Real-time  → SHEETF (stock prices), SHE-MFI (bond NAV)
Daily      → SHE-SAVE NAV, bond accrual
Weekly     → Community signals (±0.1M SHE burn/mint)
Monthly    → Prediction market resolutions
Quarterly  → ETF rebalancing, staking yield distribution
Annually   → Full WEI recalculation
```

### Community Signal Token Mechanic

The grievance app (shetoken.org/signal) directly moves the price:
```
Net positive signals this week → 0.1M SHE minted
Net negative signals this week → 0.1M SHE burned
Crisis threshold breached       → up to 1M SHE burned
Maximum weekly movement:         ±0.5% of supply
```

This is the only financial instrument in history where the people
it is meant to help are also the price discovery mechanism.

## 14. The Weekly News Agent

Every Sunday at 6am UTC, the agent automatically:

1. **Scans 139+ sources** — RSS feeds, YouTube, Reddit across 15 languages
2. **Classifies with SLM** — Phi-3.5 Mini + Qwen2.5:3b (Ollama, runs locally)
3. **Updates WEI live scores** — signals carry 10% weight in weekly update
4. **Moves the news-sensitive sister indexes** — SVI (from safety/violence signals) and WVI (from empowerment/digital signals) also update weekly, capped at ±2.0 points; structural indexes stay monthly
5. **Loads everything into Supabase** — live WEI + SVI + WVI written to the `she_*` tables the website reads, plus a dated history snapshot
6. **Writes to Google Sheets** — signals tab + live WEI tab
7. **Sends branded newsletter** — founder version + subscriber version + NGO version
8. **Posts Twitter thread** — 5-tweet weekly signal report to @ShetokenDAO
9. **Posts Instagram card** — branded weekly image

### Signal → Score Mechanics

```
WEI_live = WEI_annual_baseline (90%) + weekly_news_signals (10%)
SVI_live = SVI_baseline + capped signals from safety_justice + violence_penalty
WVI_live = WVI_baseline + capped signals from empowerment + digital_social
Maximum weekly movement: ±2.0 points per country (same engine for all three)
Signals decay over 12 weeks (half-life model)
```

### Crisis Trigger Protocol

If any country's crime index rises >15% in one year:
1. Automatic red flag on shetoken.org dashboard
2. DAO governance vote opens (72-hour emergency window)
3. Options: emergency NGO grants, additional token burn, or both

---

## 15. Geographic Coverage

| Level | Count | Indexes |
|---|---|---|
| Countries | 105 | WEI, GPI, SVI, WEVI, WADI, WHI, WVI, WRBCS |
| India states | 25 | WEI, WEVI |
| USA states | 50 | WEI, WRBCS |
| Brazil states | 27 | WEI |
| Nigeria states | 34 | WEI |
| Mexico states | 31 | WEI |
| Pakistan provinces | 7 | WEI |
| World cities | 111 | WEI |

---

## 16. How to Invest

### Step-by-Step

| Step | Action |
|---|---|
| 1 | Download MetaMask (free, 5 minutes) |
| 2 | Buy ETH on Coinbase, Binance, or WazirX |
| 3 | Swap ETH for SHE on Uniswap |
| 4 | Hold in your wallet. Track on CoinGecko. |

### Three Return Mechanisms

**1. Price Appreciation** — as WEI score improves globally, demand rises.

**2. Token Scarcity via Burns** — when WEI falls, tokens are permanently
burned. Less supply + same demand = each remaining token more valuable.

**3. Staking Rewards** — lock SHE tokens for 6–12 months, earn additional
tokens. Rewards long-term holders over short-term speculators.

### Geographic Sub-Tokens

| Tier | Format | Example | When |
|---|---|---|---|
| Global | SHE | Master token | Live |
| Country | SHE-IND, SHE-USA | National WEI | Year 2 |
| State | SHE-WB, SHE-KL | State WEI | Year 3 |

---

## 17. Tokenomics

| Parameter | Value |
|---|---|
| Token name | SHE (Women's Empowerment Index Token) |
| Ticker | SHE |
| Blockchain | Ethereum ERC-20 |
| Layer 2 | Polygon (low-fee transactions) |
| Initial supply | 1,000,000,000 SHE (1 billion) |
| Decimals | 18 |
| Smart contract | Audited by CertiK + OpenZeppelin |
| DEX listing | Uniswap V3 |

### Distribution

| Allocation | Amount |
|---|---|
| Public Sale / Community | 40% — 400M SHE |
| WEI Impact Fund | 25% — 250M SHE |
| Founding Team (3yr vesting) | 15% — 150M SHE |
| Ecosystem & Partnerships | 10% — 100M SHE |
| Reserve & Liquidity Pool | 10% — 100M SHE |

---

## 18. Token Mechanics

| Event | Token mechanism |
|---|---|
| Global WEI rises +1 point | 10M SHE minted → WEI Impact Fund |
| Global WEI falls -1 point | 10M SHE permanently burned |
| GPI rises +1 point | 5M SHE minted (secondary signal) |
| SHE-MFI bond repayment | NAV updates daily |
| SHEETF basket company price move | NAV updates real-time |
| Corporate stake slashed | Slashed tokens burned |
| Prediction market resolved | Payout in SHE tokens |
| Crime spike >15% in one year | DAO emergency governance vote |
| Country WEI improves significantly | Country sub-token appreciates |
| Government registers + improves | Quarterly updates, ESG investor signal |

---

## 19. Technology & Blockchain

| Layer | Technology |
|---|---|
| Primary blockchain | Ethereum ERC-20 |
| Layer 2 | Polygon — micro-transactions and NGO grants |
| Oracle | Chainlink — connects WEI data to smart contracts |
| Governance | Snapshot DAO — off-chain voting, on-chain execution |
| Data storage | IPFS — tamper-proof, permanent |
| Smart contract audit | CertiK + OpenZeppelin (dual audit pre-launch) |
| DEX listing | Uniswap V3 |
| API | FastAPI — serves live WEI data to dashboard |
| SLM classification | Phi-3.5 Mini + Qwen2.5:3b (Ollama) |

---

## 20. Governance

| Decision | Threshold |
|---|---|
| WEI methodology changes | 66% supermajority |
| New data source | 51% simple majority |
| Impact Fund grant allocations | 51% simple majority |
| Smart contract upgrades | 75% supermajority + 60-day timelock |
| Crisis trigger response | 51% majority, 72-hour window |
| New country/state sub-token | 66% supermajority |

### Advisory Council

Representatives from: UN Women, academic gender studies researchers,
SEWA, Kudumbashree, JEEViKA, state government program officers,
blockchain security experts.

---

## 21. Roadmap

| Phase | Timeline | Milestones |
|---|---|---|
| Foundation | Months 1–3 | Whitepaper, WEI baseline, shetoken.org, GitHub |
| Build | Months 4–6 | Smart contracts, NGO partnerships, Pivotal Ventures pitch |
| Testnet | Months 7–9 | Ethereum testnet, Chainlink oracle, DAO on Snapshot |
| Mainnet | Month 10–12 | Public token sale, Uniswap listing, first WEI Report |
| Country Tokens | Year 2 | SHE-IND, SHE-NGA, SHE-USA + 10 more |
| State Tokens | Year 3 | SHE-WB, SHE-KL, SHE-MH + NGO portal |
| Scale | Year 4+ | UN Women partnership, institutional ESG, 50+ countries |

---

## 22. Legal Disclaimer

This whitepaper is for informational purposes only and does not constitute
financial, legal, or investment advice. SHE is a utility token and is not
intended to be a security, investment product, or financial instrument in
any jurisdiction.

| Risk | Detail |
|---|---|
| Regulatory risk | Cryptocurrency regulation varies and may change |
| Data risk | WEI scores depend on quality of international data |
| Smart contract risk | Despite auditing, bugs may exist |
| Market risk | Token value may be volatile independently of WEI |
| Oracle risk | Real-world data feeds may be delayed or inaccurate |
| Liquidity risk | Early-stage tokens may have limited trading volume |

---

*© 2026 SHE Foundation. All rights reserved.*
*shetoken.org · github.com/shetoken · contact@shetoken.org*

**SHE GOES UP.**
