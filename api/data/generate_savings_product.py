"""
SHEtoken — Women's Savings Account Product (Idea 8)
====================================================
The most accessible entry point for the token ecosystem.
A mobile savings product for the 2 billion women globally
with phones but no savings product.

Product: SHE-SAVE token
Backing: SHE_MFI bond basket (real yield)
Bonus:   WEI performance bonus (0-2% extra if global WEI improves)
Access:  $1 minimum. Works with UPI, M-Pesa, bKash, mobile money.
Chain:   Celo (mobile-first, ultra-low fees, $0.001 per transaction)

(c) 2026 SHE Foundation. MIT License.
"""

import json, os, sys
from datetime import datetime, timezone
from pathlib import Path
sys.path.insert(0, os.path.dirname(__file__))
from config_v3 import OUTPUT_DIR, BASELINE_YEAR

# ── TARGET MARKETS ─────────────────────────────────────────────────────────────
TARGET_MARKETS = [
    {
        "country":         "India",
        "iso":             "IND",
        "mobile_money_users_M": 400,
        "platform":        "UPI (Unified Payments Interface)",
        "entry_point":     "PhonePe, Paytm, Google Pay integration",
        "local_currency":  "INR",
        "min_deposit_local": "₹100 (~$1.20)",
        "target_user":     "Women with UPI but no investment account",
        "partner_orgs":    ["SEWA Bank", "Mann Deshi Bank",
                            "Kudumbashree digital expansion"],
        "regulatory":      "RBI Payment Aggregator licence needed",
        "wei_connection":  "Yield bonus when India WEI improves",
    },
    {
        "country":         "Kenya",
        "iso":             "KEN",
        "mobile_money_users_M": 30,
        "platform":        "M-Pesa",
        "entry_point":     "M-Pesa API integration (Safaricom partnership)",
        "local_currency":  "KES",
        "min_deposit_local": "KES 100 (~$0.75)",
        "target_user":     "M-Pesa users wanting savings yield",
        "partner_orgs":    ["Equity Bank Women", "M-KOPA"],
        "regulatory":      "CBK Digital Lending licence",
        "wei_connection":  "Yield bonus when Kenya WEI improves",
    },
    {
        "country":         "Bangladesh",
        "iso":             "BGD",
        "mobile_money_users_M": 50,
        "platform":        "bKash",
        "entry_point":     "bKash API (BRAC Bank subsidiary)",
        "local_currency":  "BDT",
        "min_deposit_local": "BDT 100 (~$0.90)",
        "target_user":     "Garment workers with bKash — transition savings",
        "partner_orgs":    ["BRAC", "Grameen Bank", "BNWLA"],
        "regulatory":      "Bangladesh Bank MFS licence",
        "wei_connection":  "Garment workers saving against automation displacement",
    },
    {
        "country":         "Nigeria",
        "iso":             "NGA",
        "mobile_money_users_M": 40,
        "platform":        "Opay / PalmPay / Kuda",
        "entry_point":     "Nigerian fintech API integration",
        "local_currency":  "NGN",
        "min_deposit_local": "NGN 500 (~$0.35)",
        "target_user":     "Market women, informal traders",
        "partner_orgs":    ["LAPO Microfinance", "Women's World Banking Nigeria"],
        "regulatory":      "CBN PSB licence",
        "wei_connection":  "Yield bonus when Nigeria WEI improves",
    },
    {
        "country":         "Global (crypto-native)",
        "iso":             "GLOBAL",
        "mobile_money_users_M": 50,
        "platform":        "Celo wallet / Valora app",
        "entry_point":     "Direct crypto wallet deposit",
        "local_currency":  "USDC / cUSD",
        "min_deposit_local": "$1 USDC",
        "target_user":     "Crypto-native women globally, diaspora savings",
        "partner_orgs":    ["Celo Foundation", "Impact Market"],
        "regulatory":      "No local licence needed — pure DeFi",
        "wei_connection":  "Full WEI bonus mechanism",
    },
]

# ── YIELD STRUCTURE ────────────────────────────────────────────────────────────
YIELD_STRUCTURE = {
    "base_yield": {
        "source":       "SHE_MFI microfinance bond basket",
        "current_pct":  7.5,
        "update":       "Daily NAV accrual",
        "description":  "Real yield from women's microfinance bonds",
    },
    "wei_performance_bonus": {
        "description":  "Extra yield when global WEI improves",
        "tiers": [
            {"wei_improvement": 0.0, "bonus_pct": 0.0,  "label": "No change"},
            {"wei_improvement": 0.5, "bonus_pct": 0.25, "label": "Small improvement"},
            {"wei_improvement": 1.0, "bonus_pct": 0.50, "label": "Moderate improvement"},
            {"wei_improvement": 2.0, "bonus_pct": 1.00, "label": "Strong improvement"},
            {"wei_improvement": 3.0, "bonus_pct": 2.00, "label": "Exceptional improvement"},
        ],
        "max_bonus_pct": 2.0,
        "update":       "Annual — when WEI is published",
    },
    "country_bonus": {
        "description":  "Extra 0.5% if user's country WEI improves this year",
        "bonus_pct":    0.5,
        "update":       "Annual",
    },
    "total_max_yield_pct": 10.0,
}

# ── PRODUCT SPECS ──────────────────────────────────────────────────────────────
PRODUCT_SPEC = {
    "token_name":       "SHE-SAVE",
    "blockchain":       "Celo (mobile-first, $0.001 gas fees)",
    "min_deposit_usd":  1.0,
    "withdrawal":       "Instant — no lock-up (unlike SHE staking)",
    "currencies_accepted": ["USDC", "cUSD", "ETH", "local via on-ramp"],
    "yield_structure":  YIELD_STRUCTURE,
    "use_of_funds": {
        "90%": "SHE_MFI bond basket (yield generation)",
        "8%":  "Liquidity reserve (instant withdrawals)",
        "2%":  "WEI Impact Fund (direct mission contribution)",
    },
    "insurance":        "First-loss tranche (senior/junior structure, Goldfinch model)",
    "transparency":     "Real-time dashboard: shetoken.org/savings",
    "reporting": {
        "daily":     "NAV per token",
        "monthly":   "Portfolio performance + impact report",
        "quarterly": "MFI audit results",
        "annually":  "Full impact report: women reached, WEI contribution",
    },
    "target_markets":   TARGET_MARKETS,
    "competitive_comparison": {
        "vs_bank_savings": "Banks: 0-2% in India. SHE-SAVE: 7.5-9.5%. Plus impact.",
        "vs_fixed_deposit": "FD: 6-7%. SHE-SAVE: 7.5-9.5%. Plus impact.",
        "vs_stock_market": "Higher risk there. SHE-SAVE: bond-backed, lower risk.",
        "vs_crypto":       "Most crypto: speculative. SHE-SAVE: real yield from real loans.",
    },
}


def generate():
    out = OUTPUT_DIR / "savings-product.json"
    with open(out,"w",encoding="utf-8") as f:
        json.dump({
            "product": PRODUCT_SPEC,
            "year": BASELINE_YEAR,
        }, f, indent=2, ensure_ascii=False)

    total_users = sum(m["mobile_money_users_M"] for m in TARGET_MARKETS)
    print(f"Women's Savings Account Product")
    print("="*55)
    print(f"\n  Total addressable users: {total_users}M women")
    print(f"\n  Markets:")
    for m in TARGET_MARKETS:
        print(f"    {m['country']:<20} {m['mobile_money_users_M']:>6}M users  "
              f"{m['platform']}")
    print(f"\n  Yield structure:")
    print(f"    Base (MFI bonds):    {YIELD_STRUCTURE['base_yield']['current_pct']}%")
    print(f"    WEI bonus (max):     {YIELD_STRUCTURE['wei_performance_bonus']['max_bonus_pct']}%")
    print(f"    Country bonus:       {YIELD_STRUCTURE['country_bonus']['bonus_pct']}%")
    print(f"    Total max:           {PRODUCT_SPEC['yield_structure']['total_max_yield_pct']}%")
    print(f"\n  vs competition:")
    for k,v in PRODUCT_SPEC["competitive_comparison"].items():
        print(f"    {k:<20} {v[:60]}")
    print(f"\n  Saved: {out}")


if __name__ == "__main__":
    generate()
