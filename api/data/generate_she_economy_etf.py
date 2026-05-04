"""
SHEtoken — She-Economy ETF Token (Idea 4)
==========================================
Basket of publicly traded companies meeting verified
women's rights criteria. NAV updates daily with stock prices.

Basket criteria (all verifiable, all public, no naming risk):
  ✓ Listed on major exchange (NYSE, NASDAQ, LSE, TSX, ASX)
  ✓ Female board membership ≥ 30% (Bloomberg data, public filings)
  ✓ Published gender pay gap report showing improvement trend
  ✓ Headquartered in WRBCS PREFERRED or ACCEPTABLE country
  ✓ At least one: B Corp, UN WEPs signatory, ILO Better Work, EPIC certified
  ✓ Not in WRBCS AVOID sector in AVOID country without WRTC

Basket composition: 30 companies initially
Rebalancing: Quarterly — triggered by WEI/WRBCS score updates

NAV = weighted sum of basket company share prices × component weights

(c) 2026 SHE Foundation. MIT License.
"""

import json, os, sys
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

# ── ETF BASKET CRITERIA ───────────────────────────────────────────────────────
# We define the criteria and sectors — NOT specific companies.
# Actual company list populated from public registries quarterly.

ETF_CRITERIA = {
    "name":        "She-Economy ETF Token",
    "ticker":      "SHEETF",
    "description": (
        "A token tracking a basket of publicly listed companies "
        "meeting verified women's rights criteria. "
        "NAV updates daily. Rebalances quarterly with WEI updates."
    ),
    "inclusion_criteria": {
        "mandatory": [
            "Listed on NYSE, NASDAQ, LSE, TSX, ASX, Euronext, or SGX",
            "Female board members ≥ 30% (verified from public filings)",
            "Headquartered in WRBCS PREFERRED or ACCEPTABLE country",
            "Market cap ≥ $500M USD",
            "No material ESG controversies in last 24 months",
        ],
        "at_least_one_of": [
            "B Corp certified (bcorporation.net)",
            "UN Women's Empowerment Principles signatory (weps.org)",
            "Equal Pay International Coalition certified employer",
            "ILO Better Work programme participant",
            "2X Challenge portfolio company",
            "GenderSmart certified investment target",
        ],
    },
    "exclusion_criteria": [
        "Headquarters in WRBCS AVOID or EMBARGO country",
        "Primary revenue from AVOID country without WRTC certification",
        "Weapons manufacturing",
        "Tobacco",
        "Gender pay gap worsening trend (3yr)",
    ],
    "sector_targets": {
        "Technology":            "20% — female leadership + digital inclusion",
        "Financial Services":    "20% — women's financial inclusion products",
        "Healthcare":            "15% — women's health focus",
        "Consumer Goods":        "15% — fair trade, B Corp, ethical supply chain",
        "Professional Services": "10% — equal pay certified firms",
        "Renewable Energy":      "10% — clean energy with gender programs",
        "Education":             "10% — women's education focus",
    },
    "where_to_find_basket_companies": {
        "B_Corp_directory":     "bcorporation.net/en-us/find-a-b-corp",
        "WEPs_signatories":     "weps.org/signatories",
        "EPIC_employers":       "equalpayinternationalcoalition.org",
        "2X_portfolio":         "2xcollaborative.org/portfolio",
        "ILO_better_work":      "betterwork.org/our-work/buyers",
        "Bloomberg_gender":     "bloomberg.com/genderequality",
        "MSCI_women_index":     "msci.com/our-solutions/indexes/women-leadership",
    },
    "nav_mechanics": {
        "update_frequency":    "Daily — from exchange price feeds via Chainlink",
        "rebalancing":         "Quarterly — aligned with WEI score publications",
        "rebalancing_trigger": "WEI score change OR WRBCS rating change for any basket member",
        "exit_trigger":        "Company drops below criteria → automatic replacement",
        "wei_link":            (
            "30% of rebalancing weight given to companies whose "
            "headquarter country shows WEI improvement. "
            "Companies in PREFERRED countries get +5% tilt."
        ),
    },
    "token_mechanics": {
        "token_name":          "She-Economy ETF Token",
        "backing":             "Each token = fractional ownership of basket",
        "mint":                "Investor deposits ETH/USDC → receives SHEETF at NAV",
        "redeem":              "Burn SHEETF → receive underlying basket value",
        "management_fee_pct":  0.35,
        "fee_destination":     "0.20% → WEI Impact Fund | 0.15% → operations",
        "protocol":            "Synthetix or Set Protocol for basket management",
    },
    "performance_thesis": (
        "Research from McKinsey, MSCI, and Harvard shows companies "
        "with gender-diverse leadership outperform peers by 15-25% "
        "over 5-year horizons. The She-Economy ETF captures this "
        "'gender alpha' while directly incentivising women's rights progress."
    ),
    "sector_baskets": {
        "SHEETF-TECH":    "Technology companies only",
        "SHEETF-FINANCE": "Women's financial inclusion companies",
        "SHEETF-CARE":    "Healthcare + care economy companies",
        "SHEETF-GLOBAL":  "Full diversified basket (primary token)",
    },
}

# ── MSCI WOMEN'S LEADERSHIP INDEX AS PROXY ───────────────────────────────────
# MSCI Women's Leadership Index is the closest existing instrument.
# SHEtoken differentiates by:
#   1. Adding WEI score as a component (MSCI doesn't)
#   2. Including WRBCS country screening (MSCI doesn't)
#   3. Tokenising for global retail access (MSCI is institutional)
#   4. Routing management fee to WEI Impact Fund (MSCI doesn't)

MSCI_COMPARISON = {
    "MSCI_Women_Leadership_Index": {
        "exists":       True,
        "bloomberg_ticker": "MXWOMEN",
        "components":   500,
        "rebalance":    "Semi-annual",
        "fee_destination": "None (institutional ETF)",
        "she_advantage": [
            "WEI score integration",
            "WRBCS supply chain screening",
            "Tokenised — accessible with $5",
            "Management fee → Impact Fund",
            "Prediction market built on top",
        ],
    },
}


def generate():
    out = OUTPUT_DIR / "she-economy-etf.json"
    with open(out,"w",encoding="utf-8") as f:
        json.dump({
            "etf": ETF_CRITERIA,
            "msci_comparison": MSCI_COMPARISON,
            "year": BASELINE_YEAR,
        }, f, indent=2, ensure_ascii=False)

    print(f"She-Economy ETF Token")
    print("="*55)
    print(f"  Mandatory criteria: {len(ETF_CRITERIA['inclusion_criteria']['mandatory'])}")
    print(f"  Optional criteria:  {len(ETF_CRITERIA['inclusion_criteria']['at_least_one_of'])}")
    print(f"  Sector targets:     {len(ETF_CRITERIA['sector_targets'])}")
    print(f"  Sub-tokens:         {len(ETF_CRITERIA['sector_baskets'])}")
    print(f"  Management fee:     {ETF_CRITERIA['token_mechanics']['management_fee_pct']}%")
    print(f"  → Impact Fund:      0.20%")
    print(f"\n  Company registries to populate basket from:")
    for k,v in ETF_CRITERIA["where_to_find_basket_companies"].items():
        print(f"    {k}: {v}")
    print(f"\n  Saved: {out}")


if __name__ == "__main__":
    generate()
