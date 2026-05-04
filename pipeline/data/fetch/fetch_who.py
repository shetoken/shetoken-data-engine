"""
SHEtoken Pipeline — WHO Global Health Observatory Fetcher
==========================================================
Fetches women's health indicator data from the WHO GHO OData API.

API docs: https://www.who.int/data/gho/info/gho-odata-api

Usage:
    python data/fetch/fetch_who.py

Output:
    data/raw/who_raw.csv
"""

import requests
import pandas as pd
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config import (
    WHO_INDICATORS, SCORED_COUNTRIES, RAW_DIR,
    REQUEST_TIMEOUT, REQUEST_DELAY, MAX_RETRIES
)

BASE_URL = "https://ghoapi.azureedge.net/api"


def fetch_indicator(indicator_code, countries):
    """
    Fetch a single WHO GHO indicator for all countries.

    Args:
        indicator_code (str): WHO indicator code (e.g. MDG_0000000026)
        countries (list): List of ISO3 country codes

    Returns:
        dict: {iso_code: value} mapping
    """
    url = f"{BASE_URL}/{indicator_code}"
    params = {
        "$filter": "Dim1 eq 'FMLE' or Dim1 eq 'SEX_FMLE' or Dim1 eq 'BTSX'",
        "$orderby": "TimeDimensionValue desc",
        "$top": 1000,
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json().get("value", [])

            if not data:
                # Try without sex filter (some indicators not sex-disaggregated)
                resp2 = requests.get(
                    url,
                    params={"$orderby": "TimeDimensionValue desc", "$top": 2000},
                    timeout=REQUEST_TIMEOUT
                )
                resp2.raise_for_status()
                data = resp2.json().get("value", [])

            results = {}
            country_set = set(countries)
            for entry in data:
                iso = entry.get("SpatialDim", "")
                val = entry.get("NumericValue")
                year = entry.get("TimeDimensionValue", "0")

                if iso not in country_set or val is None:
                    continue

                if iso not in results or year > results[iso]["year"]:
                    results[iso] = {"value": float(val), "year": str(year)}

            return {k: v["value"] for k, v in results.items()}

        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * 3)

    return {}


def fetch_all(countries=SCORED_COUNTRIES):
    """
    Fetch all WHO indicators for all scored countries.

    Returns:
        pd.DataFrame: One row per country, one column per indicator
    """
    print("WHO GHO API — fetching health indicators")
    print(f"Countries: {len(countries)}")
    print(f"Indicators: {len(WHO_INDICATORS)}")
    print("-" * 50)

    all_data = {iso: {"iso_code": iso} for iso in countries}

    for name, code in WHO_INDICATORS.items():
        print(f"  Fetching: {name} ({code})")
        results = fetch_indicator(code, countries)

        for iso in countries:
            all_data[iso][f"who_{name}"] = results.get(iso, None)

        found = sum(1 for iso in countries if iso in results)
        print(f"    → {found}/{len(countries)} countries found")
        time.sleep(REQUEST_DELAY)

    df = pd.DataFrame(list(all_data.values()))
    return df


def main():
    df = fetch_all()

    out_path = RAW_DIR / "who_raw.csv"
    df.to_csv(out_path, index=False)

    print(f"\n✓ Saved: {out_path}")
    print(f"  Rows: {len(df)} | Columns: {len(df.columns)}")
    return df


if __name__ == "__main__":
    main()
