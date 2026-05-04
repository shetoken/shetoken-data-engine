"""
SHEtoken Pipeline — World Bank Data Fetcher
=============================================
Fetches gender indicator data from the World Bank API.

API docs: https://datahelpdesk.worldbank.org/knowledgebase/articles/898581

Usage:
    python data/fetch/fetch_world_bank.py

Output:
    data/raw/world_bank_raw.csv
"""

import requests
import pandas as pd
import time
import json
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config import (
    WB_INDICATORS, SCORED_COUNTRIES, RAW_DIR,
    REQUEST_TIMEOUT, REQUEST_DELAY, MAX_RETRIES, DATA_YEAR_RANGE
)

BASE_URL = "https://api.worldbank.org/v2"


def fetch_indicator(indicator_code, countries, year_range=DATA_YEAR_RANGE):
    """
    Fetch a single World Bank indicator for a list of countries.

    Args:
        indicator_code (str): World Bank indicator code (e.g. SG.GEN.PARL.ZS)
        countries (list): List of ISO3 country codes
        year_range (str): Year range in format 'YYYY:YYYY'

    Returns:
        dict: {iso_code: value} mapping of most recent available value
    """
    country_str = ";".join(countries)
    url = (
        f"{BASE_URL}/country/{country_str}/indicator/{indicator_code}"
        f"?format=json&per_page=500&date={year_range}&mrv=1"
    )

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            if len(data) < 2 or not data[1]:
                return {}

            results = {}
            for entry in data[1]:
                if entry.get("value") is not None:
                    iso = entry["countryiso3code"]
                    val = float(entry["value"])
                    # Keep most recent value
                    if iso not in results:
                        results[iso] = {"value": val, "year": entry["date"]}
                    elif entry["date"] > results[iso]["year"]:
                        results[iso] = {"value": val, "year": entry["date"]}

            return {k: v["value"] for k, v in results.items()}

        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * 3)

    return {}


def fetch_all(countries=SCORED_COUNTRIES):
    """
    Fetch all World Bank indicators for all scored countries.

    Returns:
        pd.DataFrame: One row per country, one column per indicator
    """
    print("World Bank API — fetching gender indicators")
    print(f"Countries: {len(countries)}")
    print(f"Indicators: {len(WB_INDICATORS)}")
    print("-" * 50)

    all_data = {iso: {"iso_code": iso} for iso in countries}

    for name, code in WB_INDICATORS.items():
        print(f"  Fetching: {name} ({code})")
        results = fetch_indicator(code, countries)

        for iso in countries:
            all_data[iso][f"wb_{name}"] = results.get(iso, None)

        found = sum(1 for iso in countries if iso in results)
        print(f"    → {found}/{len(countries)} countries found")
        time.sleep(REQUEST_DELAY)

    df = pd.DataFrame(list(all_data.values()))
    return df


def main():
    df = fetch_all()

    out_path = RAW_DIR / "world_bank_raw.csv"
    df.to_csv(out_path, index=False)

    print(f"\n✓ Saved: {out_path}")
    print(f"  Rows: {len(df)}")
    print(f"  Columns: {len(df.columns)}")

    # Coverage report
    print("\nCoverage report:")
    for col in df.columns:
        if col == "iso_code":
            continue
        filled = df[col].notna().sum()
        pct = round(filled / len(df) * 100)
        bar = "█" * (pct // 5) + "░" * (20 - pct // 5)
        print(f"  {col:<35} {bar} {pct:3d}%")

    return df


if __name__ == "__main__":
    main()
