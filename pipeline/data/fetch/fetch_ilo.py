"""
SHEtoken Pipeline — ILO STAT Data Fetcher
==========================================
Fetches labour force and wage data from the ILO STAT API.

API docs: https://ilostat.ilo.org/resources/ilostat-api/

Usage:
    python data/fetch/fetch_ilo.py

Output:
    data/raw/ilo_raw.csv
"""

import requests
import pandas as pd
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config import (
    SCORED_COUNTRIES, RAW_DIR,
    REQUEST_TIMEOUT, REQUEST_DELAY, MAX_RETRIES
)

# ILO REST API base
BASE_URL = "https://rplumber.ilo.org/data/indicator"

# Indicators to fetch
# classif1=SEX_F filters for female data where available
ILO_QUERIES = {
    "lfpr_female": {
        "id":        "EAP_DWAP_SEX_AGE_RT_A",
        "filters":   "sex=SEX_F&classif1=AGE_YTHADULT_YGE15",
        "desc":      "Female labour force participation rate (15+)",
    },
    "employment_female": {
        "id":        "EMP_DWAP_SEX_AGE_RT_A",
        "filters":   "sex=SEX_F&classif1=AGE_YTHADULT_YGE15",
        "desc":      "Female employment-to-population ratio",
    },
    "wage_gender_gap": {
        "id":        "EAR_INDE_SEX_OCU_NB_A",
        "filters":   "sex=SEX_F",
        "desc":      "Mean nominal wages — female (used to compute gap)",
    },
    "wage_gender_gap_male": {
        "id":        "EAR_INDE_SEX_OCU_NB_A",
        "filters":   "sex=SEX_M",
        "desc":      "Mean nominal wages — male (used to compute gap)",
    },
}


def fetch_indicator(query_name, query_config, countries):
    """
    Fetch a single ILO indicator.

    Returns:
        dict: {iso_code: value}
    """
    indicator_id = query_config["id"]
    filters      = query_config["filters"]

    # Build country filter string
    country_filter = "&".join(f"ref_area={c}" for c in countries)

    url = (
        f"{BASE_URL}/?id={indicator_id}&{filters}"
        f"&{country_filter}&timefrom=2018&timeto=2024"
        f"&type=label&decimals=1&lang=en&format=.json"
    )

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            obs = data.get("obs", [])
            results = {}

            for entry in obs:
                iso   = entry.get("ref_area", {}).get("id", "")
                val   = entry.get("obs_value", {}).get("value")
                year  = entry.get("time", {}).get("id", "0")

                if not iso or val is None:
                    continue
                val = float(val)
                if iso not in results or year > results[iso]["year"]:
                    results[iso] = {"value": val, "year": str(year)}

            return {k: v["value"] for k, v in results.items()}

        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * 3)

    return {}


def fetch_all(countries=SCORED_COUNTRIES):
    """
    Fetch all ILO indicators and compute gender wage gap.

    Returns:
        pd.DataFrame
    """
    print("ILO STAT API — fetching labour indicators")
    print(f"Countries: {len(countries)}")
    print("-" * 50)

    all_data = {iso: {"iso_code": iso} for iso in countries}
    raw = {}

    for name, config in ILO_QUERIES.items():
        print(f"  Fetching: {name}")
        print(f"    ({config['desc']})")
        results = fetch_indicator(name, config, countries)
        raw[name] = results

        for iso in countries:
            all_data[iso][f"ilo_{name}"] = results.get(iso, None)

        found = sum(1 for iso in countries if iso in results)
        print(f"    → {found}/{len(countries)} countries found")
        time.sleep(REQUEST_DELAY)

    # Compute gender wage gap percentage
    print("  Computing gender wage gap...")
    for iso in countries:
        f_wage = raw.get("wage_gender_gap", {}).get(iso)
        m_wage = raw.get("wage_gender_gap_male", {}).get(iso)
        if f_wage and m_wage and m_wage > 0:
            gap = round(((m_wage - f_wage) / m_wage) * 100, 1)
            all_data[iso]["ilo_wage_gap_pct"] = gap
        else:
            all_data[iso]["ilo_wage_gap_pct"] = None

    df = pd.DataFrame(list(all_data.values()))
    return df


def main():
    df = fetch_all()

    out_path = RAW_DIR / "ilo_raw.csv"
    df.to_csv(out_path, index=False)

    print(f"\n✓ Saved: {out_path}")
    print(f"  Rows: {len(df)} | Columns: {len(df.columns)}")
    return df


if __name__ == "__main__":
    main()
