# The Demographic Cost of Inaction
## A Concept & Methodology Document for the SHEtoken "World Without Women" Model

> **Status: DRAFT FOR REVIEW — not for publication.**
> **Version 0.1 (concept) | May 2026**
>
> This document lays out the *thesis, mechanisms, evidence base, modelling
> approach, and assumptions* for a demographic scenario model that projects the
> consequences of inaction on women's safety, health, and equality. It is
> written to be reviewed and challenged — ideally by a professional demographer —
> **before any code is written or any number is published.**
>
> Every specific figure below is marked with its source and a **[VERIFY]** flag.
> No figure here should be treated as final until checked against the primary
> source. The credibility of the entire SHEtoken platform depends on this model
> being conservative, sourced, and honest.

---

## 0. Why this document exists first

For the indexes, the method was well-trodden — we could build with confidence.
This model is different. Its credibility lives almost entirely in its
**assumptions**, and a single indefensible assumption could discredit not just
the model but the rigorous index work alongside it.

So this is deliberately a *paper* before it is *code*. It exists to:

1. State each mechanism and the published evidence behind it.
2. Separate what is well-established from what is scenario-dependent.
3. Make every assumption explicit and adjustable.
4. Be handed to an expert reviewer for challenge before launch.

**Guiding principle:** the real data is already sobering enough. We do not need
to inflate anything. Honest and conservative will persuade serious audiences;
alarmist will not, and will invite the dismissal of the whole platform.

---

## 1. The Thesis — and why the reframe matters

Issues like sex-selective abortion, dowry deaths, honour killings, femicide, and
the despair that drives some women out of marriage and childbearing are usually
filed under "women's issues" — and so they are compartmentalised, treated as a
moral concern for a specialist audience.

This model reframes them as what they demonstrably also are: a **population and
economic continuity problem** that affects entire societies, men included.

> When women are killed, never born, or so constrained that they opt out of
> family formation, the effect is not confined to women. It shrinks the next
> generation, distorts the sex ratio, removes workers and mothers from the
> economy, and destabilises the societies left with the imbalance.

This reframe is not rhetorical invention. It is the logic of an existing body of
demography — Amartya Sen's "missing women," the "bare branches" literature on
surplus-male societies, and the fertility-collapse research now preoccupying
governments from Seoul to Beijing. The model's job is to make that connection
**measurable and visible**, and to tie it to the SHEtoken WEI: *a better WEI
implies a better demographic trajectory; a worse WEI, a worse one.*

---

## 2. Design principles

| Principle | What it means in practice |
|---|---|
| **Conservative by default** | Where a range exists, use the low end. Under-claim. |
| **Sourced** | Every input traces to a named, public, reputable source. |
| **Confidence-tiered** | Each mechanism is labelled by how established it is (below). |
| **Transparent assumptions** | Every rate and elasticity is a visible, adjustable parameter — never hard-coded as hidden truth. |
| **Scenario-based, not predictive** | The output is "if these rates hold / worsen / improve, then…", never "this *will* happen." |
| **Respectful** | These are real deaths and real suffering. The numbers are presented soberly; we let them speak. |
| **Reproducible** | Like the indexes: open inputs, open formula, auditable. |

### Confidence tiers (used throughout)

| Tier | Meaning | Treatment in the model |
|---|---|---|
| 🟢 **Tier 1 — Established** | Mainstream demography; broad expert consensus | Forms the conservative core projection |
| 🟡 **Tier 2 — Documented but partial** | Real and sourced, but under-reported or regionally specific | Included, clearly labelled, conservative rates |
| 🟠 **Tier 3 — Scenario-dependent** | Real mechanism, but causal size is contested | Only ever shown as an explicit, labelled scenario |

---

## 3. Tier 1 — Missing Women 🟢 (the conservative core)

### 3.1 The concept

The foundational idea comes from Amartya Sen's 1990 essay *"More Than 100
Million Women Are Missing"* (New York Review of Books). "Missing women" are the
shortfall between the number of women who *should* be alive, given a natural sex
ratio and equal care, and the number actually alive.

- Natural sex ratio at birth ≈ **105 boys : 100 girls**. **[VERIFY — standard demographic baseline, e.g. UNFPA]**
- Where the ratio is more male-skewed, or where female mortality exceeds the
  natural pattern, women are "missing."

### 3.2 The mechanisms (all Tier 1)

| Sub-mechanism | What it is | Primary source to use |
|---|---|---|
| **Prenatal (sex selection)** | Sex-selective abortion skewing births male | UNFPA; published academic demography |
| **Postnatal child mortality** | Excess female infant/child death from neglect, unequal nutrition & healthcare | WHO; UNICEF; World Bank |
| **Excess adult mortality** | Women dying earlier than they should from unequal treatment | WHO; academic studies |

### 3.3 Anchoring figures (ALL require verification)

| Figure | Approx. value | Source | Flag |
|---|---|---|---|
| Sen's original estimate (1990) | ~100 million missing women | Sen 1990 | 🟢 attribution solid; **[VERIFY exact figure & framing]** |
| Updated global estimate | ~142 million missing women (cited around 2020) | Attributed to UNFPA *State of World Population* | **[VERIFY — confirm figure, year, and definition]** |
| Annual missing female births (sex selection) | ~1.2–1.5 million / year, concentrated in China & India | UNFPA | **[VERIFY]** |

> **Modelling note:** the core projection extrapolates the *annual deficit*
> (missing births + excess female deaths) forward under each scenario. Because
> these are the most established figures, they carry the main weight of the
> projection. Use the low end of every range.

---

## 4. Tier 2 — Excess Female Mortality from Specific Harms 🟡

These are the harms you named directly. They are real and documented, but
**severely under-reported**, so the model must use them carefully: report them
as *reported* counts (a known floor, not the true total), and never silently
inflate to "true" numbers without a sourced adjustment factor.

### 4.1 The mechanisms

| Harm | What it is | Primary source | Reporting caveat |
|---|---|---|---|
| **Dowry deaths** | Women killed over dowry disputes | India NCRB (annual) | Reported only; India-specific |
| **Honour killings** | Women murdered for perceived family "dishonour" | UNODC; national records; UN estimates | Drastically under-reported globally |
| **Femicide / intimate-partner killing** | Women killed by partners or family | UNODC & UN Women *Gender-related killings of women and girls* (annual) | Best global source; still a floor |
| **Female suicide / deaths of despair** | Excess female suicide linked to gendered pressures | WHO; *The Lancet* studies | Causality is partial — handle with care (see 4.3) |
| **Maternal mortality** | Women dying in preventable childbirth | WHO Global Health Observatory | Well-measured; already in WEI Health pillar |

### 4.2 Anchoring figures (ALL require verification)

| Figure | Approx. value | Source | Flag |
|---|---|---|---|
| Dowry deaths, India | ~6,000–7,000 reported / year | NCRB | **[VERIFY latest NCRB year]** |
| Honour killings, global | ~5,000 / year (old, contested UN figure) | UN (historical) | **[VERIFY — likely a large under-count; flag as floor]** |
| Female victims of intimate-partner/family femicide, global | ~48,000–50,000 in a recent year | UNODC / UN Women | **[VERIFY exact figure & year]** |
| India share of global female suicides | India has been reported to account for a large share (~36% in one *Lancet* analysis) of global female suicide deaths | Dandona et al., *The Lancet* (≈2018) | **[VERIFY figure, year, scope]** |

### 4.3 The suicide / "dying of depression" mechanism — handle with special care

You raised "women dying of depression." This is real — but it needs the most
careful treatment of anything in Tier 2, for two reasons:

1. **Global pattern vs. specific pattern.** In *most* countries, recorded male
   suicide rates exceed female. The striking, defensible story is **specific**:
   notably high *young female* suicide in places like India, linked to forced
   marriage, dowry stress, domestic violence, and constrained autonomy. The
   model should make the *specific, sourced* claim, not a sweeping global one.
2. **Causality.** "Dying of depression" as a *consequence of gender oppression*
   is partly established and partly inferred. Present it as **excess female
   suicide associated with gendered pressures**, citing the specific studies —
   not as a blanket mechanism.

> **Recommendation:** include excess female suicide as a Tier 2 mechanism scoped
> to the regions and age bands where the evidence is strong, with sources
> attached. Do not generalise it globally.

---

## 5. Tier 3 — Foregone Births & the "Opt-Out" 🟠 (labelled scenario only)

This is the part of your idea that is genuinely powerful **and** the part most
likely to be challenged — so it must be presented as an explicit scenario with a
visible assumption, never as fact.

### 5.1 The mechanism

The claim: as gender inequity rises (unequal domestic burden, career penalties
for mothers, unsafe environments, coercive marriage), a growing share of women
**delay or forgo marriage and childbearing** — depressing fertility below
replacement and shrinking future generations.

### 5.2 Why it is real…

There is a serious, growing literature here:

- **South Korea** — total fertility rate around **0.72** in a recent year (the
  world's lowest), with public discourse explicitly tying it to gender inequity
  and movements of women opting out. **[VERIFY TFR figure & year — World Bank / KOSTAT]**
- **Japan** — long-running decline in marriage and fertility.
- **China** — falling marriage rates and below-replacement fertility *on top of*
  a sex-ratio surplus of men.

### 5.3 …but why it must stay Tier 3

Fertility decline is **multi-causal** — housing costs, education, urbanisation,
career economics, and contraception access all contribute. Attributing a
specific share to "frustration / gender inequity" is an *assumption*, not a
measured fact. So:

> **Rule:** the opt-out / foregone-births effect is only ever shown with a
> slider or explicit parameter — e.g. "*assume gender inequity accounts for X%
> of below-replacement fertility*" — with X visible, adjustable, and defaulted
> low. The user sees it is an assumption.

---

## 6. Tier 3 — Population & Economic Knock-On 🟠 (the "world problem" layer)

This is the layer that completes the reframe: the consequences that hit
*everyone*.

| Consequence | Mechanism | Source base |
|---|---|---|
| **Surplus men ("bare branches")** | Sex-selective deficits leave millions of men unable to marry; linked in research to instability | Hudson & den Boer, *Bare Branches* (2004); academic demography |
| **Workforce & dependency ratio** | Fewer women + fewer births → smaller future workforce supporting more elderly | UN World Population Prospects; standard demographic accounting |
| **Economic output** | Lost female labour-force participation & lost human capital | World Bank; ILO; McKinsey-type gender-GDP studies **[VERIFY any GDP figure used]** |
| **Compounding** | Each missing generation reduces the *next* generation's potential mothers — the deficit compounds | Demographic momentum (standard) |

> **The bridge sentence the whole model exists to support:** *Inaction on
> women's safety and equality is not only a moral failure — it is a measurable
> subtraction from the human population and the economy that depends on it.*

---

## 7. The scenario structure

The model output is a comparison of trajectories, never a single prophecy.

| Scenario | Definition | Purpose |
|---|---|---|
| **Status Quo** | Current rates (deficit, excess mortality, fertility) held constant | The honest baseline |
| **Worsening** | Rates deteriorate per a stated, sourced assumption | The clearly-labelled "if we do nothing / it gets worse" case |
| **Intervention** | Rates improve toward Tier-1-nation benchmarks (the programs the WEI already rewards — Kanyashree, etc.) | Shows action *works*, and ties to WEI |

Output, per country and globally:
- Projected female population to a horizon (e.g. 2100)
- The **gap** between scenarios ("this many more women alive / born under
  Intervention than under Worsening")
- Knock-on: surplus-male count, dependency ratio, indicative workforce effect

The **gap between scenarios** is the headline — it is both the alarm and the
hope, and it is defensible because each scenario's assumptions are visible.

---

## 8. Connection to the WEI

This model is not a separate silo — it is the WEI's consequence engine.

- A country's **WEI pillars** (Safety, Health, Empowerment, etc.) map to the
  model's input rates (femicide → excess mortality; health → maternal mortality;
  empowerment & economic → opt-out pressure).
- Improving WEI → improving model trajectory.
- This lets you say: *"Here is what this country's WEI score means, projected
  forward, in human lives."*

That is the emotional and logical capstone on everything already built: indexes
measure now; Life Path makes now *felt*; this model makes the **future**
consequences of now visible.

---

## 9. Illustrative example (HYPOTHETICAL — not real output)

> *Purely to show the shape of an output. Numbers are placeholders, not claims.*

> Under **Status Quo**, Country X's annual female deficit (missing births +
> excess deaths) is ~N. Held to 2100, with demographic momentum, the projected
> female population is P₁. Under **Worsening** (deficit +Δ%), it is P₂. Under
> **Intervention** (deficit halved over 20 years, per programs the WEI rewards),
> it is P₃.
>
> The gap P₃ − P₂ = "**M more women alive or born by 2100 if we act**." That gap,
> with its assumptions on the page beside it, is the model's message.

---

## 10. Limitations & honesty (publish this section *with* the model)

A model like this is only trustworthy if it states its own limits plainly:

1. **Projections are scenarios, not forecasts.** They show the logic of current
   rates, not destiny.
2. **Under-reporting cuts both ways** — reported harm counts are floors; the
   model should say so rather than guess the ceiling.
3. **Fertility is multi-causal** — the opt-out layer is an assumption, shown as
   one.
4. **Aggregation hides variation** — national numbers mask regional extremes.
5. **This is not a substitute for primary demographic research** — it
   synthesises published work; it does not replace it.

---

## 11. What must happen before this is published

In order:

1. **Verify every [VERIFY] figure** against its primary source. Replace
   approximate values with cited exact ones (year, definition, scope).
2. **Have a demographer review this document.** This is the single most
   important step. An informal academic advisor (you already plan a UN
   Women / academic advisory council — this is exactly their role) should
   challenge the mechanisms and rates.
3. **Build the model as a transparent engine** — open inputs, open formula,
   adjustable parameters, audit trail (reuse the indicator-history pattern so
   every projection's inputs are reproducible).
4. **Publish the limitations section alongside it**, never separately.
5. **Default every adjustable assumption to its conservative end.**

---

## 12. Sources to verify and cite (starting list)

> Confirm each directly; do not cite from this document.

- Sen, A. (1990). *More Than 100 Million Women Are Missing.* NY Review of Books.
- UNFPA — *State of World Population* reports (missing women; sex selection).
- UNODC & UN Women — *Gender-related killings of women and girls* (femicide), annual.
- WHO — Global Health Observatory (maternal mortality; suicide).
- India NCRB — *Crime in India* (dowry deaths), annual.
- Dandona, R. et al. — female suicide in India, *The Lancet* (≈2018).
- Hudson, V. & den Boer, A. (2004). *Bare Branches.* MIT Press (surplus-male societies).
- UN DESA — *World Population Prospects* (projections, dependency ratios).
- World Bank / ILO — female labour-force participation; gender & GDP.

---

*© 2026 SHE Foundation. DRAFT concept document — for internal review and expert
challenge. Not for publication. All figures pending primary-source verification.*
