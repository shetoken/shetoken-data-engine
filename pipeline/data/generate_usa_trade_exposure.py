"""
SHEtoken — USA Trade Exposure vs Women's Rights Scores
========================================================
Maps US trade and outsourcing flows to WRBCS compliance ratings.

Shows:
  1. How much US business flows to AVOID/EMBARGO countries
  2. Which sectors are most exposed
  3. Where trade could realistically be redirected
  4. What a 0.5% Women's Rights Commitment would generate
  5. Policy mechanisms that have worked (Bangladesh Accord model)

Data sources:
  US Census Bureau — Goods trade by country 2023
  BEA — US direct investment abroad 2023
  USTR — US trade statistics
  Gartner/IDC — IT services outsourcing estimates
  ILO — Garment/manufacturing supply chain data

NOTE: Trade figures are 2023 estimates in USD billions.
Services (IT outsourcing, BPO) are estimated from industry sources.

(c) 2026 SHE Foundation. MIT License.
"""

import csv, io, os, sys, json
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

# ── US TRADE + OUTSOURCING FLOWS ──────────────────────────────────────────────
# country, iso, wrbcs_rating,
# us_goods_imports_bn,      USD billions — US Census 2023
# us_services_imports_bn,   IT, BPO, professional services
# us_fdi_stock_bn,          US investment stock — BEA
# main_sectors,             what the US actually buys
# female_share_pct,         % of workforce in those sectors who are women
# redirect_to,              better-scoring countries for same goods

TRADE_DATA = [
    # ── PREFERRED / ACCEPTABLE ────────────────────────────────────────────────
    ("Iceland",     "ISL","PREFERRED",   0.4,  0.3,  0.8,
     "Fish, aluminum, creative services",         30,
     None,  # already preferred
     "N/A — already best practice"),
    ("Norway",      "NOR","PREFERRED",   4.2,  2.1, 12.4,
     "Oil, seafood, maritime services",           32,
     None,
     "N/A — already best practice"),
    ("Sweden",      "SWE","PREFERRED",   6.8,  3.2, 18.6,
     "Machinery, pharma, tech, Volvo/Ikea",       34,
     None,
     "N/A — already best practice"),
    ("Germany",     "DEU","PREFERRED",  158.4, 42.1,142.8,
     "Vehicles, machinery, pharma, chemicals",    36,
     None,
     "N/A — already best practice"),
    ("Canada",      "CAN","PREFERRED",  421.1, 68.4,422.6,
     "Energy, vehicles, lumber, financial services",38,
     None,
     "N/A — already best practice"),
    ("Australia",   "AUS","PREFERRED",  17.2,  14.8, 52.4,
     "Mining, agriculture, education services",   36,
     None,
     "N/A — already best practice"),
    ("UK",          "GBR","ACCEPTABLE", 68.4,  86.2,750.8,
     "Finance, pharma, aerospace, creative",      38,
     None,
     "N/A — acceptable"),
    ("Japan",       "JPN","ACCEPTABLE", 148.6, 28.4,142.2,
     "Vehicles, electronics, machinery",          28,
     None,
     "N/A — acceptable"),
    ("South Korea", "KOR","ACCEPTABLE",  70.8, 14.2, 42.8,
     "Electronics, vehicles, steel",              26,
     None,
     "N/A — acceptable"),
    ("Brazil",      "BRA","ACCEPTABLE",  36.2,  8.4, 72.4,
     "Agri (soy, coffee, beef), iron ore, aircraft",42,
     None,
     "N/A — acceptable with standard due diligence"),

    # ── CAUTION — large flows, enhanced obligations needed ────────────────────
    ("Mexico",      "MEX","CAUTION",    475.6, 28.4, 98.4,
     "Vehicles, electronics, agriculture, maquiladora",62,
     None,  # USMCA makes redirect impractical
     "USMCA partner — cannot redirect. Require WRBCS compliance "
     "clauses in all supplier contracts. Fund Cimac + Red Mesa."),
    ("China",       "CHN","CAUTION",    427.2, 18.4,118.4,
     "Electronics, machinery, garments, furniture, toys",54,
     ["Vietnam","Malaysia","Thailand","India","Morocco"],
     "Diversify electronics to Vietnam/Malaysia. Garments to "
     "Bangladesh alternative — but note Bangladesh is AVOID, "
     "redirect garments to Morocco, Peru, Turkey instead."),
    ("India",       "IND","CAUTION",     84.2, 42.8, 44.2,
     "IT services, pharma, garments, gems, steel",62,
     None,  # IT services — India dominates, hard to redirect
     "IT outsourcing — India CAUTION. Require suppliers to publish "
     "female workforce data. Fund SEWA + Majlis. "
     "Consider Philippines or Eastern Europe for some IT."),
    ("Vietnam",     "VNM","CAUTION",    114.8,  4.2, 14.8,
     "Electronics (Samsung), garments, footwear, furniture",64,
     ["Malaysia","Thailand","Morocco"],
     "Electronics: acceptable CAUTION. Garments: redirect premium "
     "lines to Morocco or Turkey. Require ILO Better Work enrollment."),
    ("Indonesia",   "IDN","CAUTION",     24.2,  2.8, 12.4,
     "Electronics, palm oil, garments, rubber",60,
     ["Malaysia","Vietnam"],
     "Palm oil — require RSPO certification with gender rider. "
     "Fund Kalyanamitra. Require female workforce % disclosure."),
    ("Philippines", "PHL","CAUTION",     11.4,  8.4,  8.2,
     "Electronics, business services, garments",62,
     ["Vietnam","India","Poland"],
     "BPO — 1.3M women facing automation. Fund GABRIELA. "
     "Require suppliers to publish female worker transition plan."),
    ("Saudi Arabia","SAU","CAUTION",     18.2,  4.2, 14.8,
     "Oil, petrochemicals, construction",         28,
     ["UAE","Bahrain"],
     "Energy imports — limited redirect. Require gender equality "
     "reporting for all Saudi JV partners. Vision 2030 monitoring."),

    # ── AVOID — significant flows, require immediate action ───────────────────
    ("Bangladesh",  "BGD","AVOID",        8.4,  0.4,  2.2,
     "Garments (H&M, Gap, Primark, Walmart suppliers)",72,
     ["Morocco","Peru","Turkey","Sri Lanka","Portugal"],
     "Redirect garment sourcing to Morocco (55 WEI), Peru (62), "
     "Turkey (58 — CAUTION but better). "
     "For existing contracts: require Bangladesh Accord equivalent. "
     "Fund BNWLA + Naripokkho. Commit 1% to WEI Impact Fund."),
    ("Pakistan",    "PAK","AVOID",         4.2,  0.6,  1.8,
     "Textiles, sporting goods, leather",         54,
     ["Turkey","India","Sri Lanka"],
     "Redirect textiles to Turkey or India (both CAUTION but better). "
     "For existing: require female worker safety audit. "
     "Fund Shirkat Gah. Commit 1% to WEI Impact Fund."),
    ("Cambodia",    "KHM","AVOID",         3.8,  0.2,  0.8,
     "Garments (Nike, H&M, Gap suppliers)",        90,
     ["Vietnam","Sri Lanka","Peru","Morocco"],
     "CRITICAL: 90% female garment workforce faces full automation. "
     "Redirect to Vietnam or Peru. "
     "For existing: fund LICADHO. Commit 1% to transition fund. "
     "Set 3-year exit or remediation timeline."),
    ("Nigeria",     "NGA","AVOID",         6.8,  0.8,  8.4,
     "Oil, agricultural commodities",             42,
     ["Ghana","South Africa","Kenya"],
     "Oil imports — limited redirect. Require gender reporting for "
     "all Nigerian JV partners. Fund BAOBAB + WARPA."),
    ("Ethiopia",    "ETH","AVOID",         0.6,  0.1,  0.4,
     "Garments (Hawassa Industrial Park), coffee",62,
     ["Kenya","Rwanda","Morocco"],
     "Hawassa garments — require ACT Fund enrollment. "
     "Fund Ethiopian Women Lawyers Association. "
     "Coffee: require gender-inclusive cooperative certification."),
    ("Myanmar",     "MMR","AVOID",         0.8,  0.1,  0.2,
     "Garments (US has some sanctions), jade",    60,
     ["Vietnam","Cambodia (itself AVOID) → Morocco"],
     "US already has some Myanmar sanctions. "
     "Full exit from garment supply chain recommended. "
     "Fund Gender Equality Network Myanmar (diaspora)."),
    ("Iran",        "IRN","AVOID",         0.2,  0.1,  0.1,
     "Limited — US sanctions largely in place",   20,
     ["Turkey","UAE"],
     "Existing sanctions reduce exposure. "
     "Women leading protest movement — support diaspora orgs."),

    # ── EMBARGO ───────────────────────────────────────────────────────────────
    ("DRC",         "COD","EMBARGO",       0.9,  0.1,  0.4,
     "Cobalt (EV batteries, iPhones), coltan",    28,
     ["Zambia","Australia","Chile"],
     "CRITICAL SUPPLY CHAIN: iPhone and EV battery cobalt. "
     "Armed group SGBV at mine sites. Girls work as mineral carriers. "
     "Redirect to Zambian cobalt (lower SGBV) or recycled/Australian. "
     "Apple, Tesla, GM have existing commitments — enforce them."),
    ("Afghanistan", "AFG","EMBARGO",       0.1,  0.0,  0.1,
     "Minimal — Taliban sanctions",               10,
     ["Pakistan (also AVOID)"],
     "No US business justification. Support Afghan women's diaspora orgs."),
    ("Somalia",     "SOM","EMBARGO",       0.1,  0.0,  0.0,
     "None",                                       10,
     None,
     "No business. Support Somali Women Development Centre."),
]


def compute_avoid_embargo_totals(rows):
    """Calculate total US trade exposure to AVOID + EMBARGO countries."""
    totals = {"AVOID": {"goods":0,"services":0,"fdi":0,"countries":[]},
              "EMBARGO":{"goods":0,"services":0,"fdi":0,"countries":[]},
              "CAUTION":{"goods":0,"services":0,"fdi":0,"countries":[]},
              "PREFERRED_ACCEPTABLE":{"goods":0,"services":0,"fdi":0,"countries":[]}}

    for r in rows:
        rating = r["wrbcs_rating"]
        key = ("PREFERRED_ACCEPTABLE" if rating in ("PREFERRED","ACCEPTABLE")
               else rating)
        if key not in totals: continue
        totals[key]["goods"]    += r["us_goods_imports_bn"]
        totals[key]["services"] += r["us_services_imports_bn"]
        totals[key]["fdi"]      += r["us_fdi_stock_bn"]
        totals[key]["countries"].append(r["country"])

    return totals


def compute_commitment_fund(rows, pct=0.005):
    """
    If companies committed pct% of contract value for AVOID/EMBARGO
    countries, how much would flow to the WEI Impact Fund?
    """
    total_avoid_embargo = sum(
        r["us_goods_imports_bn"] + r["us_services_imports_bn"]
        for r in rows
        if r["wrbcs_rating"] in ("AVOID","EMBARGO")
    )
    return {
        "total_trade_to_avoid_embargo_bn": round(total_avoid_embargo, 1),
        "commitment_pct":                  pct * 100,
        "annual_fund_contribution_bn":     round(total_avoid_embargo * pct, 3),
        "annual_fund_contribution_mn":     round(total_avoid_embargo * pct * 1000, 1),
        "comparison": {
            "world_bank_gender_fund_annual_bn": 0.4,
            "un_women_annual_budget_bn":         0.8,
            "gates_foundation_gender_annual_bn": 0.6,
        },
    }


def generate(year=BASELINE_YEAR):
    rows = []
    for stat in TRADE_DATA:
        (country, iso, rating, goods, services, fdi,
         sectors, female_pct, redirect_isos, redirect_note) = stat
        rows.append({
            "country":              country,
            "iso_code":             iso,
            "wrbcs_rating":         rating,
            "us_goods_imports_bn":  goods,
            "us_services_imports_bn": services,
            "us_fdi_stock_bn":      fdi,
            "total_trade_exposure_bn": round(goods+services, 1),
            "main_sectors":         sectors,
            "female_workforce_pct": female_pct,
            "redirect_to_countries": ", ".join(redirect_isos) if redirect_isos else "",
            "redirect_action":      redirect_note,
            "women_at_stake_est_millions": round(
                (goods+services)*1000 * female_pct/100 / 50000, 1),  # rough: $50K avg contract per worker
            "year": year,
        })

    totals   = compute_avoid_embargo_totals(rows)
    fund_05  = compute_commitment_fund(rows, 0.005)
    fund_10  = compute_commitment_fund(rows, 0.010)
    fund_20  = compute_commitment_fund(rows, 0.020)

    # ── SAVE TRADE CSV ────────────────────────────────────────────────────────
    out = OUTPUT_DIR / f"usa-trade-exposure-{year}.csv"
    hdr = (
        f"# SHEtoken — US Trade Exposure vs Women's Rights Scores {year}\n"
        f"# Shows how much US business flows to AVOID/EMBARGO countries\n"
        f"# and where it could be redirected to better-scoring countries.\n"
        f"# Trade figures: USD billions, 2023 estimates\n"
        f"# Sources: US Census Bureau, BEA, USTR, Gartner, ILO\n"
        f"# (c) 2026 SHE Foundation\n#\n"
    )
    flds = ["country","iso_code","wrbcs_rating",
            "us_goods_imports_bn","us_services_imports_bn",
            "us_fdi_stock_bn","total_trade_exposure_bn",
            "main_sectors","female_workforce_pct",
            "women_at_stake_est_millions",
            "redirect_to_countries","redirect_action","year"]
    buf = io.StringIO()
    w   = csv.DictWriter(buf, fieldnames=flds, extrasaction="ignore")
    w.writeheader(); w.writerows(rows)
    with open(out,"w",newline="",encoding="utf-8") as f:
        f.write(hdr+buf.getvalue())

    # ── SAVE POLICY JSON ──────────────────────────────────────────────────────
    policy_out = OUTPUT_DIR / "usa-trade-policy-brief.json"
    avoid_countries = [r for r in rows if r["wrbcs_rating"] in ("AVOID","EMBARGO")]

    policy = {
        "title": "US Business with Countries Rated AVOID or EMBARGO on Women's Rights",
        "year": year,
        "summary": {
            "total_us_trade_to_avoid_embargo_bn":
                round(sum(r["total_trade_exposure_bn"]
                          for r in avoid_countries), 1),
            "avoid_countries": len([r for r in rows if r["wrbcs_rating"]=="AVOID"]),
            "embargo_countries":len([r for r in rows if r["wrbcs_rating"]=="EMBARGO"]),
            "largest_avoid_trade_flow": sorted(
                avoid_countries, key=lambda x: x["total_trade_exposure_bn"],
                reverse=True)[:5],
        },
        "totals_by_rating": totals,

        "commitment_fund_scenarios": {
            "0.5pct_of_avoid_embargo_trade": fund_05,
            "1.0pct_of_avoid_embargo_trade": fund_10,
            "2.0pct_of_avoid_embargo_trade": fund_20,
        },

        "policy_mechanisms": {

            "mechanism_1_voluntary_commitment": {
                "name": "Women's Rights Trade Commitment (WRTC)",
                "model": "1% for the Planet",
                "how_it_works": (
                    "Companies sourcing from AVOID/EMBARGO countries commit "
                    "0.5-2% of annual contract value to the WEI Impact Fund "
                    "OR to a verified local women's NGO partner. "
                    "Compliance earns a SHEtoken WRTC certification badge. "
                    "Non-compliance disclosed in ESG report."
                ),
                "precedents": [
                    "1% for the Planet — 5,000+ companies, $500M+ donated",
                    "Fair Trade Premium — mandatory 1-2% on certified products",
                    "ILO Better Work — companies pay per-factory fee, women benefit",
                ],
                "revenue_estimate": fund_10,
                "how_to_launch": (
                    "SHEtoken publishes WRTC standard. Companies sign online. "
                    "Payments go to verified WEI Impact Fund wallet. "
                    "Annual audit verifies payment. Badge displayed on products."
                ),
            },

            "mechanism_2_tariff_equivalent": {
                "name": "Women's Rights Trade Adjustment (WRTA)",
                "model": "EU Carbon Border Adjustment Mechanism (CBAM)",
                "how_it_works": (
                    "Import tariff applied to goods from AVOID/EMBARGO countries "
                    "unless importer can show either: "
                    "(a) supply chain women's rights certification, or "
                    "(b) payment into WEI Impact Fund. "
                    "Rate: 1-3% ad valorem, scaled to WRBCS score gap vs ACCEPTABLE threshold."
                ),
                "precedents": [
                    "EU CBAM 2023 — carbon tariff on steel, cement, aluminium",
                    "US Uyghur FLPA 2021 — import ban without clean supply chain proof",
                    "GSP conditions — US already conditions trade preferences on labour rights",
                    "Bangladesh Accord 2013 — brands legally bound after Rana Plaza",
                ],
                "estimated_annual_revenue_bn": round(
                    fund_10["total_trade_to_avoid_embargo_bn"] * 0.02, 2),
                "where_revenue_goes": (
                    "70% → WEI Impact Fund (NGO grants in origin country) "
                    "20% → Reskilling programs for displaced women workers "
                    "10% → SHEtoken data infrastructure"
                ),
                "legislative_path": (
                    "Amend US GSP statute to include Women's Rights Index threshold. "
                    "Requires Senate Finance Committee action. "
                    "Precedent: GSP already conditions benefits on labour rights (19 USC 2462)."
                ),
            },

            "mechanism_3_supply_chain_accord": {
                "name": "Women's Rights Supply Chain Accord (WRSCA)",
                "model": "Bangladesh Accord on Fire and Building Safety",
                "how_it_works": (
                    "Major brands sourcing from AVOID countries sign a binding 5-year accord. "
                    "Commits to: "
                    "(1) Annual third-party gender audit of all Tier 1 suppliers, "
                    "(2) Minimum 1% of FOB value to women's programs in country, "
                    "(3) Transparent female workforce data publication, "
                    "(4) WEI score improvement targets for supplier regions, "
                    "(5) Remediation plan if WEI falls, exit plan if EMBARGO triggered."
                ),
                "precedents": [
                    "Bangladesh Accord 2013 — 200+ brands, legally binding, "
                    "4,000 factories audited, 150,000 hazards fixed",
                    "Better Work Bangladesh — ILO programme, proven female "
                    "worker outcome improvements",
                    "ACT Initiative — brands funding living wages via collective bargaining",
                ],
                "target_brands": [
                    "Walmart (Bangladesh, Cambodia, Vietnam sourcing)",
                    "Amazon (Bangladesh, Vietnam, India)",
                    "Gap Inc (Bangladesh, Cambodia, Vietnam)",
                    "H&M (Bangladesh, Cambodia, India, Pakistan)",
                    "Nike (Vietnam, Indonesia, Cambodia)",
                    "Apple (China — CAUTION, supply chain gender audit needed)",
                    "Tesla/GM (DRC cobalt — EMBARGO level risk)",
                ],
                "shetoken_role": (
                    "SHEtoken provides the WEI score infrastructure that "
                    "brands need to verify compliance. The WRBCS is the "
                    "measurable target that replaces vague ESG commitments."
                ),
            },

            "mechanism_4_state_level_usa": {
                "name": "US State Government Women's Rights Procurement Preference",
                "model": "Buy American Act / Fair Trade city resolutions",
                "how_it_works": (
                    "State and city governments give procurement preference "
                    "to companies that source from PREFERRED/ACCEPTABLE countries "
                    "OR have signed the WRTC commitment. "
                    "Companies sourcing from AVOID/EMBARGO without WRTC "
                    "commitment are excluded from state contracts."
                ),
                "precedents": [
                    "California SB 657 (2010) — supply chain transparency required "
                    "for all companies doing business with California",
                    "NYC Fair Trade Resolution — city gives preference to fair trade",
                    "Oregon SB 926 — supply chain human rights due diligence",
                    "Massachusetts anti-sweatshop procurement",
                ],
                "immediate_action": (
                    "California, New York, Massachusetts — all PREFERRED states — "
                    "can implement this immediately without federal action. "
                    "Combined procurement: $500B+/year."
                ),
            },
        },

        "redirect_opportunities": {
            "bangladesh_garments_8bn": {
                "current": "Bangladesh AVOID — $8.4B garment imports",
                "redirect_to": {
                    "Morocco":    "55 WEI — CAUTION, improving. $2-3B capacity.",
                    "Turkey":     "58 WEI — CAUTION. $3-4B garment capacity.",
                    "Peru":       "62 WEI — CAUTION. Quality garments, growing.",
                    "Sri Lanka":  "55 WEI — CAUTION. $5B garment industry.",
                    "Portugal":   "80 WEI — ACCEPTABLE. Premium garments.",
                },
                "note": "Full redirect unrealistic in 1 year. 5-year transition plan needed.",
            },
            "cambodia_garments_4bn": {
                "current": "Cambodia AVOID — $3.8B garment imports (90% female workers)",
                "redirect_to": {
                    "Vietnam":    "52 WEI — CAUTION, better than Cambodia.",
                    "Sri Lanka":  "55 WEI — CAUTION.",
                    "Peru":       "62 WEI — CAUTION.",
                },
            },
            "drc_cobalt": {
                "current": "DRC EMBARGO — cobalt in every iPhone and EV battery",
                "redirect_to": {
                    "Zambia":     "Better governance, lower conflict SGBV risk.",
                    "Australia":  "PREFERRED — highest cost but clean.",
                    "Recycled":   "Battery recycling programs — no new mining.",
                },
                "key_companies": "Apple, Tesla, GM, Ford, Samsung — all sourcing DRC cobalt",
            },
            "china_electronics": {
                "current": "China CAUTION — $427B total. Electronics: ~$100B",
                "redirect_to": {
                    "Vietnam":    "52 WEI — CAUTION but better. Samsung already moved.",
                    "Malaysia":   "62 WEI — CAUTION. Strong electronics base.",
                    "India":      "48 WEI — CAUTION. Apple moving iPhone production.",
                    "Mexico":     "60 WEI — CAUTION. Nearshoring trend.",
                },
            },
        },

        "what_1pct_generates": {
            "description": (
                "If every US company sourcing from AVOID/EMBARGO countries "
                "committed just 1% of that contract value to verified "
                "women's programs in those countries:"
            ),
            "total_avoid_embargo_trade_bn": fund_10["total_trade_to_avoid_embargo_bn"],
            "annual_women_fund_mn":         fund_10["annual_fund_contribution_mn"],
            "comparison": {
                "un_women_annual_budget_mn":        800,
                "world_bank_gender_fund_mn":        400,
                "gates_pvt_ventures_annual_mn":     600,
                "shetoken_1pct_fund_mn":            fund_10["annual_fund_contribution_mn"],
            },
            "what_it_would_fund": [
                f"Free menstrual products in every school in Bangladesh for 10 years",
                f"Train 500,000 garment workers for digital/AI roles",
                f"Fund 50,000 women lawyers in AVOID countries",
                f"Run Kudumbashree-equivalent SHG networks in 5 countries",
                f"Build 1,000 women's shelters across AVOID countries",
            ],
        },
    }

    with open(policy_out,"w",encoding="utf-8") as f:
        json.dump(policy, f, indent=2, ensure_ascii=False)

    # ── PRINT SUMMARY ─────────────────────────────────────────────────────────
    avoid_total = sum(r["total_trade_exposure_bn"]
                      for r in rows if r["wrbcs_rating"] in ("AVOID","EMBARGO"))
    caution_total = sum(r["total_trade_exposure_bn"]
                        for r in rows if r["wrbcs_rating"]=="CAUTION")
    pref_total = sum(r["total_trade_exposure_bn"]
                     for r in rows if r["wrbcs_rating"] in ("PREFERRED","ACCEPTABLE"))

    print("US Trade Exposure vs Women's Rights Compliance")
    print("="*65)
    print(f"\n  Trade flows by rating:")
    print(f"  ✅ PREFERRED/ACCEPTABLE:  ${pref_total:>8.1f}B/year")
    print(f"  🟡 CAUTION:               ${caution_total:>8.1f}B/year")
    print(f"  🔴 AVOID + ⛔ EMBARGO:    ${avoid_total:>8.1f}B/year  ← THE PROBLEM")
    print()
    print(f"  AVOID/EMBARGO breakdown:")
    avoid_rows = sorted([r for r in rows if r["wrbcs_rating"] in ("AVOID","EMBARGO")],
                         key=lambda x: x["total_trade_exposure_bn"], reverse=True)
    for r in avoid_rows:
        print(f"    {r['wrbcs_rating']:<8} {r['country']:<15} "
              f"${r['total_trade_exposure_bn']:>6.1f}B  "
              f"Female: {r['female_workforce_pct']}%  "
              f"Sectors: {r['main_sectors'][:40]}")
    print()
    print(f"  If companies committed 1% of AVOID/EMBARGO trade to women's programs:")
    print(f"    Total AVOID+EMBARGO trade:  ${avoid_total:.1f}B")
    print(f"    1% commitment:              ${avoid_total*0.01*1000:.0f}M/year")
    print(f"    UN Women annual budget:     $800M/year")
    print(f"    → 1% commitment = "
          f"{round(avoid_total*0.01*1000/800*100)}% of UN Women's entire budget")
    print()
    print(f"  Largest redirect opportunity:")
    print(f"    Bangladesh $8.4B garments → Morocco, Turkey, Peru, Sri Lanka")
    print(f"    Cambodia   $3.8B garments → Vietnam, Sri Lanka, Peru")
    print(f"    DRC        $0.9B cobalt   → Zambia, Australia, recycled")
    print()
    print(f"  Saved: {out}")
    print(f"  Saved: {policy_out}")


if __name__ == "__main__":
    import argparse
    p=argparse.ArgumentParser()
    p.add_argument("--year",type=int,default=BASELINE_YEAR)
    generate(p.parse_args().year)
