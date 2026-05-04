"""
SHEtoken Pipeline — IPU Parline Data Fetcher
=============================================
Fetches women in parliament data from the IPU Parline database.

Data source: https://data.ipu.org
API: https://data.ipu.org/api/women-ranking.json

Usage:
    python data/fetch/fetch_ipu.py

Output:
    data/raw/ipu_raw.csv
"""

import requests
import pandas as pd
import time
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config import (
    SCORED_COUNTRIES, RAW_DIR,
    REQUEST_TIMEOUT, MAX_RETRIES, REQUEST_DELAY
)

IPU_URL = "https://data.ipu.org/api/women-ranking.json"


def fetch_parliament_data():
    """
    Fetch women in parliament percentage for all countries.

    Returns:
        dict: {iso3_code: percentage}
    """
    print("IPU Parline — fetching women in parliament data")

    params = {
        "load-entity-refs": "taxonomy_term,file",
        "_format": "json",
    }

    for attempt in range(MAX_RETRIES):
        try:
            resp = requests.get(IPU_URL, params=params, timeout=REQUEST_TIMEOUT)
            resp.raise_for_status()
            data = resp.json()

            results = {}
            for entry in data:
                # IPU uses ISO2 codes — convert or map directly
                iso2  = entry.get("country_isocode", "")
                pct   = entry.get("women_house_percent")

                if not iso2 or pct is None:
                    continue

                try:
                    results[iso2] = float(pct)
                except (TypeError, ValueError):
                    continue

            print(f"  → {len(results)} countries found")
            return results

        except requests.exceptions.RequestException as e:
            print(f"  Attempt {attempt + 1}/{MAX_RETRIES} failed: {e}")
            if attempt < MAX_RETRIES - 1:
                time.sleep(REQUEST_DELAY * 3)

    return {}


# ISO2 → ISO3 mapping for countries in our scored list
ISO2_TO_ISO3 = {
    "IS":"ISL","NO":"NOR","FI":"FIN","SE":"SWE","DK":"DNK","NZ":"NZL",
    "DE":"DEU","CH":"CHE","CA":"CAN","AU":"AUS","IE":"IRL","NL":"NLD",
    "BE":"BEL","AT":"AUT","FR":"FRA","GB":"GBR","ES":"ESP","PT":"PRT",
    "US":"USA","JP":"JPN","KR":"KOR","IL":"ISR","UY":"URY","AR":"ARG",
    "BR":"BRA","CL":"CHL","CO":"COL","MX":"MEX","ZA":"ZAF","CN":"CHN",
    "IN":"IND","ID":"IDN","PH":"PHL","LK":"LKA","VN":"VNM","TH":"THA",
    "MN":"MNG","BW":"BWA","NA":"NAM","TN":"TUN","MA":"MAR","KE":"KEN",
    "GH":"GHA","RW":"RWA","KZ":"KAZ","UA":"UKR","TR":"TUR","RU":"RUS",
    "BO":"BOL","HN":"HND","PE":"PER","BD":"BGD","NP":"NPL","MM":"MMR",
    "KH":"KHM","LA":"LAO","PG":"PNG","PK":"PAK","NG":"NGA","ET":"ETH",
    "TZ":"TZA","UG":"UGA","MZ":"MOZ","ZM":"ZMB","ZW":"ZWE","CM":"CMR",
    "CI":"CIV","GT":"GTM","HT":"HTI","EG":"EGY","JO":"JOR","IQ":"IRQ",
    "SD":"SDN","YE":"YEM","AF":"AFG","CD":"COD","SY":"SYR","ML":"MLI",
    "TD":"TCD","NE":"NER","CF":"CAF","SS":"SSD","SO":"SOM",
}


def fetch_all(countries=SCORED_COUNTRIES):
    """
    Fetch IPU data and map to ISO3 codes.

    Returns:
        pd.DataFrame
    """
    iso2_data = fetch_parliament_data()

    # Convert ISO2 → ISO3
    iso3_data = {}
    for iso2, val in iso2_data.items():
        iso3 = ISO2_TO_ISO3.get(iso2)
        if iso3:
            iso3_data[iso3] = val

    rows = []
    for iso in countries:
        rows.append({
            "iso_code":                  iso,
            "ipu_parliament_female_pct": iso3_data.get(iso, None),
        })

    df = pd.DataFrame(rows)
    found = df["ipu_parliament_female_pct"].notna().sum()
    print(f"  → Mapped to ISO3: {found}/{len(countries)} countries")

    return df


def main():
    df = fetch_all()

    out_path = RAW_DIR / "ipu_raw.csv"
    df.to_csv(out_path, index=False)

    print(f"\n✓ Saved: {out_path}")
    print(f"  Rows: {len(df)}")
    return df


if __name__ == "__main__":
    main()
