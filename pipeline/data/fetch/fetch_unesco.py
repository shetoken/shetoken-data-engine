"""
SHEtoken Pipeline — UNESCO UIS Data Fetcher
============================================
Fetches female education and literacy data from the UNESCO UIS API.

API docs: https://apidata.uis.unesco.org/sdmx/v2/
API key required — register free at: https://apidata.uis.unesco.org/

Set your API key in .env file:
    UNESCO_API_KEY=your_key_here

Or pass via environment variable:
    export UNESCO_API_KEY=your_key_here

Usage:
    python data/fetch/fetch_unesco.py

Output:
    data/raw/unesco_raw.csv
"""

import requests
import pandas as pd
import time
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from config import (
    SCORED_COUNTRIES, RAW_DIR,
    REQUEST_TIMEOUT, REQUEST_DELAY, MAX_RETRIES
)

BASE_URL = "https://apidata.uis.unesco.org/sdmx/v2/data/UNESCO,SDG4"
API_KEY  = os.getenv("UNESCO_API_KEY", "")

# UNESCO indicator codes for female education
UNESCO_QUERIES = {
    "literacy_female": {
        "indicator": "LR.AG15T99",
        "sex":       "F",
        "desc":      "Female adult literacy rate (15+)",
    },
    "primary_enrollment_female": {
        "indicator": "GER.L1",
        "sex":       "F",
        "desc":      "Female gross enrollment ratio — primary",
    },
    "secondary_enrollment_female": {
        "indicator": "GER.L2",
        "sex":       "F",
        "desc":      "Female gross enrollment ratio — secondary",
    },
    "tertiary_enrollment_female": {
        "indicator": "GER.L5T8",
        "sex":       "F",
        "desc":      "Female gross enrollment ratio — tertiary",
    },
}


def fetch_indicator(indicator_code, sex_code, countries):
    """
    Fetch a single UNESCO indicator.

    Returns:
        dict: {iso_code: value}
    """
    country_str = "+".join(countries)

    url = f"{BASE_URL}/{indicator_code}.{sex_code}.{country_str}/all"
    headers = {"Accept": "application/json"}
    if API_KEY:
        headers["Ocp-Apim-Subscription-Key"] = API_KEY

    params = {
        "startPeriod": "2018",
        "endPeriod":   "2024",
        "lastNObservations": 1,
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(
                url, headers=headers, params=params, timeout=REQUEST_TIMEOUT
            )

            if resp.status_code == 401:
                print("  ⚠ UNESCO API key required.")
                print("  Register free at: https://apidata.uis.unesco.org/")
                print("  Add to .env: UNESCO_API_KEY=your_key")
                return {}

            resp.raise_for_status()
            data = resp.json()

            results = {}
            series = (
                data.get("data", {})
                    .get("dataSets", [{}])[0]
                    .get("series", {})
            )

            structures = data.get("data", {}).get("structure", {})
            dimensions = structures.get("dimensions", {}).get("series", [])

            # Find country dimension index
            country_dim_idx = None
            country_values  = []
            for i, dim in enumerate(dimensions):
                if dim.get("id") in ("REF_AREA", "COUNTRY"):
                    country_dim_idx = i
                    country_values  = [v["id"] for v in dim.get("values", [])]
                    break

            if country_dim_idx is None:
                return {}

            for series_key, series_data in series.items():
                parts = series_key.split(":")
                if country_dim_idx >= len(parts):
                    continue
                country_idx = int(parts[country_dim_idx])
                if country_idx >= len(country_values):
                    continue
                iso = country_values[country_idx]

                obs = series_data.get("observations", {})
                if obs:
                    latest_val = list(obs.values())[0][0]
                    if latest_val is not None:
                        results[iso] = float(latest_val)

            return results

        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * 3)

    return {}


def fetch_all(countries=SCORED_COUNTRIES):
    """
    Fetch all UNESCO indicators.

    Returns:
        pd.DataFrame
    """
    if not API_KEY:
        print("⚠ No UNESCO API key found.")
        print("  Returning empty frame — manual data from manual/un_women_manual.csv")
        print("  Get a free key at: https://apidata.uis.unesco.org/")
        rows = [{"iso_code": iso} for iso in countries]
        for name in UNESCO_QUERIES:
            for row in rows:
                row[f"unesco_{name}"] = None
        return pd.DataFrame(rows)

    print("UNESCO UIS API — fetching education indicators")
    print(f"Countries: {len(countries)}")
    print("-" * 50)

    all_data = {iso: {"iso_code": iso} for iso in countries}

    for name, config in UNESCO_QUERIES.items():
        print(f"  Fetching: {name}")
        print(f"    ({config['desc']})")
        results = fetch_indicator(
            config["indicator"], config["sex"], countries
        )

        for iso in countries:
            all_data[iso][f"unesco_{name}"] = results.get(iso, None)

        found = sum(1 for iso in countries if iso in results)
        print(f"    → {found}/{len(countries)} countries found")
        time.sleep(REQUEST_DELAY)

    return pd.DataFrame(list(all_data.values()))


def main():
    df = fetch_all()

    out_path = RAW_DIR / "unesco_raw.csv"
    df.to_csv(out_path, index=False)

    print(f"\n✓ Saved: {out_path}")
    print(f"  Rows: {len(df)} | Columns: {len(df.columns)}")
    return df


if __name__ == "__main__":
    main()
