"""
SHEtoken Pipeline — NCRB India Crime Data Fetcher
==================================================
Downloads and parses the National Crime Records Bureau (NCRB)
"Crime in India" annual report to extract state-level
crimes against women statistics.

Source: https://ncrb.gov.in/crime-in-india.html
Format: PDF (downloaded annually, usually released Sept-Oct)

Usage:
    # Download latest report first, then parse:
    python data/fetch/fetch_ncrb.py --pdf path/to/crime_in_india_2023.pdf

    # Or auto-download (if direct URL is known):
    python data/fetch/fetch_ncrb.py --download

Output:
    data/raw/ncrb_raw.csv

NOTE: NCRB publishes PDF reports annually. This script uses
pdfplumber to extract tables from the relevant chapters.
Chapter 5 covers "Crimes Against Women" with state-wise data.
"""

import argparse
import sys
import os
import re
import requests
import pandas as pd
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from config import INDIA_STATES, RAW_DIR, REQUEST_TIMEOUT

try:
    import pdfplumber
    PDF_AVAILABLE = True
except ImportError:
    PDF_AVAILABLE = False
    print("⚠ pdfplumber not installed. Run: pip install pdfplumber")


# Known NCRB report URLs (update annually)
NCRB_URLS = {
    2022: "https://ncrb.gov.in/uploads/nationalcrimerecordsbureau/custom/CII2022Complete202310011754566563.pdf",
    2023: "https://ncrb.gov.in/uploads/nationalcrimerecordsbureau/custom/CII_2023.pdf",
}

# State name mappings (NCRB uses full names, we need codes)
NCRB_STATE_MAP = {
    "andhra pradesh":       "AP",
    "assam":                "AS",
    "bihar":                "BR",
    "chhattisgarh":         "CG",
    "delhi":                "DL",
    "goa":                  "GA",
    "gujarat":              "GJ",
    "haryana":              "HR",
    "himachal pradesh":     "HP",
    "jharkhand":            "JH",
    "karnataka":            "KA",
    "kerala":               "KL",
    "madhya pradesh":       "MP",
    "maharashtra":          "MH",
    "manipur":              "MN",
    "meghalaya":            "ML",
    "mizoram":              "MZ",
    "odisha":               "OD",
    "punjab":               "PB",
    "rajasthan":            "RJ",
    "tamil nadu":           "TN",
    "telangana":            "TS",
    "uttar pradesh":        "UP",
    "uttarakhand":          "UK",
    "west bengal":          "WB",
}

# NCRB table columns we extract from Chapter 5
# Table 5A: State/UT-wise Crimes Against Women
TARGET_COLUMNS = {
    "rape":             ["rape", "section 376"],
    "kidnapping":       ["kidnapping", "abduction"],
    "dowry_deaths":     ["dowry death", "section 304b"],
    "dv_cases":         ["domestic violence", "section 498a", "cruelty by husband"],
    "acid_attacks":     ["acid attack"],
    "trafficking":      ["trafficking", "section 370"],
    "total_crimes_against_women": ["total"],
}


def download_ncrb_pdf(year=2023, output_dir=None):
    """
    Download the NCRB Crime in India PDF report.

    Args:
        year (int): Report year
        output_dir (Path): Where to save the PDF

    Returns:
        str: Path to downloaded PDF
    """
    if output_dir is None:
        output_dir = RAW_DIR / "ncrb_pdfs"
    os.makedirs(output_dir, exist_ok=True)

    url = NCRB_URLS.get(year)
    if not url:
        print(f"⚠ No known URL for NCRB {year} report.")
        print(f"  Manually download from: https://ncrb.gov.in/crime-in-india.html")
        print(f"  Then run: python fetch_ncrb.py --pdf <path_to_pdf>")
        return None

    out_path = output_dir / f"ncrb_crime_in_india_{year}.pdf"

    if out_path.exists():
        print(f"  PDF already exists: {out_path}")
        return str(out_path)

    print(f"  Downloading NCRB {year} report...")
    print(f"  URL: {url}")

    try:
        resp = requests.get(url, stream=True, timeout=120)
        resp.raise_for_status()
        total = int(resp.headers.get("content-length", 0))

        with open(out_path, "wb") as f:
            downloaded = 0
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)
                downloaded += len(chunk)
                if total:
                    pct = downloaded / total * 100
                    print(f"\r  Progress: {pct:.1f}%", end="")

        print(f"\n  ✓ Downloaded: {out_path}")
        return str(out_path)

    except requests.exceptions.RequestException as e:
        print(f"  ✗ Download failed: {e}")
        print(f"  Manually download from: https://ncrb.gov.in/crime-in-india.html")
        return None


def extract_table_from_page(page):
    """
    Extract structured table data from a single PDF page.

    Returns:
        list of lists: table rows
    """
    table = page.extract_table()
    if not table:
        return []
    return table


def find_crimes_against_women_pages(pdf_path):
    """
    Find page numbers containing the crimes against women state-wise table.

    Args:
        pdf_path (str): Path to NCRB PDF

    Returns:
        list: Page indices containing relevant tables
    """
    if not PDF_AVAILABLE:
        return []

    relevant_pages = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            text_lower = text.lower()
            if ("crimes against women" in text_lower and
                    "state" in text_lower and
                    ("rape" in text_lower or "376" in text_lower)):
                relevant_pages.append(i)
                if len(relevant_pages) > 10:
                    break

    return relevant_pages


def parse_state_crime_table(pdf_path):
    """
    Parse crime against women statistics from NCRB PDF.

    Args:
        pdf_path (str): Path to NCRB PDF

    Returns:
        pd.DataFrame: State-wise crime data
    """
    if not PDF_AVAILABLE:
        print("  ✗ pdfplumber not available — cannot parse PDF")
        return pd.DataFrame()

    print(f"  Parsing PDF: {pdf_path}")

    pages = find_crimes_against_women_pages(pdf_path)
    if not pages:
        print("  ✗ Could not find crimes against women pages")
        print("  Try manual extraction — see manual/ncrb_manual_template.csv")
        return pd.DataFrame()

    print(f"  Found relevant pages: {[p+1 for p in pages]}")

    all_rows = []
    with pdfplumber.open(pdf_path) as pdf:
        for page_idx in pages:
            page = pdf.pages[page_idx]
            tables = page.extract_tables()

            for table in tables:
                if not table or len(table) < 3:
                    continue

                # Look for header row containing state and crime columns
                header = [str(cell or "").lower() for cell in table[0]]
                has_state  = any("state" in h or "ut" in h for h in header)
                has_crimes = any(
                    any(kw in h for kw in ["rape", "total", "376", "cruelty"])
                    for h in header
                )

                if not (has_state and has_crimes):
                    continue

                print(f"    Found table on page {page_idx + 1}")

                for row in table[1:]:
                    if not row or not row[0]:
                        continue

                    state_name = str(row[0]).strip().lower()
                    state_name = re.sub(r'\s+', ' ', state_name)
                    state_code = NCRB_STATE_MAP.get(state_name)

                    if not state_code:
                        continue

                    # Extract values safely
                    def safe_int(val):
                        try:
                            return int(str(val).replace(",", "").strip())
                        except (ValueError, TypeError):
                            return None

                    row_data = {"state_code": state_code}

                    # Map columns to our target fields
                    for col_idx, header_cell in enumerate(header):
                        if col_idx >= len(row):
                            continue
                        for field, keywords in TARGET_COLUMNS.items():
                            if any(kw in header_cell for kw in keywords):
                                row_data[field] = safe_int(row[col_idx])

                    all_rows.append(row_data)

    if not all_rows:
        print("  ✗ No state data extracted — check PDF structure")
        return pd.DataFrame()

    df = pd.DataFrame(all_rows)
    df = df.drop_duplicates(subset=["state_code"])
    print(f"  ✓ Extracted {len(df)} states")
    return df


def compute_rates(df, population_file=None):
    """
    Convert raw crime counts to rates per 100,000 women.

    Args:
        df: DataFrame with crime counts and state_code
        population_file: Optional path to state population CSV

    Returns:
        pd.DataFrame with rate columns added
    """
    # State female population (2023 estimates, millions)
    female_pop_millions = {
        "KL": 17.2, "TN": 38.1, "TS": 18.4, "AP": 26.4, "KA": 32.9,
        "GA":  0.74,"WB": 48.2, "OD": 22.8, "AS": 17.2, "HP":  3.7,
        "UK":  5.6, "DL": 10.1, "PB": 14.7, "HR": 14.1, "MH": 61.0,
        "GJ": 31.2, "RJ": 39.8, "MP": 41.7, "CG": 14.5, "JH": 19.1,
        "BR": 63.0, "UP":118.4, "MN":  1.6, "MZ":  0.64,"ML":  1.7,
    }

    rate_cols = []
    count_cols = [c for c in df.columns if c != "state_code"]

    for col in count_cols:
        rate_col = f"{col}_rate_per_100k"
        df[rate_col] = df.apply(
            lambda row: round(
                (row[col] / (female_pop_millions.get(row["state_code"], 1) * 1_000_000))
                * 100_000, 2
            ) if pd.notna(row[col]) and row["state_code"] in female_pop_millions
            else None,
            axis=1
        )
        rate_cols.append(rate_col)

    return df


def create_manual_template():
    """
    Create a manual input template for states missing from PDF extraction.
    """
    template_path = RAW_DIR.parent / "manual" / "ncrb_manual_template.csv"

    rows = []
    for code, name in INDIA_STATES.items():
        rows.append({
            "state_code":    code,
            "state_name":    name,
            "year":          2023,
            "rape":          "",
            "dv_cases":      "",
            "dowry_deaths":  "",
            "acid_attacks":  "",
            "trafficking":   "",
            "total_crimes_against_women": "",
            "female_population_millions": "",
            "source":        "NCRB Crime in India 2023",
            "notes":         "",
        })

    df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(template_path), exist_ok=True)
    df.to_csv(template_path, index=False)
    print(f"  ✓ Manual template created: {template_path}")
    return template_path


def main():
    parser = argparse.ArgumentParser(
        description="Fetch and parse NCRB India crime data"
    )
    parser.add_argument(
        "--pdf",
        help="Path to downloaded NCRB PDF",
        default=None
    )
    parser.add_argument(
        "--download",
        action="store_true",
        help="Attempt to download latest NCRB PDF"
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2023,
        help="NCRB report year (default: 2023)"
    )
    parser.add_argument(
        "--template",
        action="store_true",
        help="Create manual input template CSV"
    )
    args = parser.parse_args()

    if args.template:
        create_manual_template()
        return

    pdf_path = args.pdf

    if args.download and not pdf_path:
        print(f"NCRB PDF Downloader — year {args.year}")
        pdf_path = download_ncrb_pdf(year=args.year)

    if not pdf_path:
        print("No PDF provided.")
        print("Options:")
        print("  1. Download manually from: https://ncrb.gov.in/crime-in-india.html")
        print("     Then run: python fetch_ncrb.py --pdf <path>")
        print("  2. Auto-download: python fetch_ncrb.py --download --year 2023")
        print("  3. Use manual template: python fetch_ncrb.py --template")
        print("     Fill in data/manual/ncrb_manual_template.csv")
        create_manual_template()
        return

    print(f"\nNCRB PDF Parser — {args.year}")
    print("-" * 50)

    df = parse_state_crime_table(pdf_path)
    if df.empty:
        print("\n✗ Extraction failed. Creating manual template...")
        create_manual_template()
        return

    df = compute_rates(df)
    df["year"] = args.year

    out_path = RAW_DIR / "ncrb_raw.csv"
    df.to_csv(out_path, index=False)

    print(f"\n✓ Saved: {out_path}")
    print(f"  States: {len(df)}")
    print(f"  Columns: {list(df.columns)}")


if __name__ == "__main__":
    main()
