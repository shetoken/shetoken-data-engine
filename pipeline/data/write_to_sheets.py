"""
SHEtoken Pipeline — Google Sheets Writer
==========================================
Writes WEI scores and data to a Google Sheet.
The sheet is publicly viewable but only editable
by the service account (you).

Setup (one time only):
    1. Create a Google Sheet at sheets.google.com
    2. Create a Service Account at console.cloud.google.com
       - Enable Google Sheets API + Google Drive API
       - Create credentials → Service Account → download JSON key
       - Share your Google Sheet with the service account email (Editor)
    3. Add to your .env file:
         GOOGLE_SHEET_ID=your_spreadsheet_id_here
         GOOGLE_SERVICE_ACCOUNT_JSON=path/to/service_account.json

Usage:
    python data/write_to_sheets.py

    # Or as part of full pipeline:
    python run_pipeline.py --sheets

Sheet tabs created:
    📊 WEI Scores          Global country scores + pillar breakdown
    🇮🇳 India States        State-level WEI scores
    🏆 Leaderboard         Top 20 + fastest movers
    📈 Summary Dashboard   Global stats, tier breakdown, last updated
    ℹ️  Methodology         Formula and data sources

© 2026 SHE Foundation. Licensed under MIT.
"""

import os
import sys
import json
import time
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_AVAILABLE = True
except ImportError:
    GSPREAD_AVAILABLE = False

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

import pandas as pd

from config import OUTPUT_DIR, BASELINE_YEAR


# ── COLOURS (Google Sheets hex, no #) ────────────────────────────────────────

BERRY       = {"red": 0.427, "green": 0.180, "blue": 0.275}
GOLD        = {"red": 0.788, "green": 0.659, "blue": 0.298}
GOLD_LIGHT  = {"red": 0.976, "green": 0.937, "blue": 0.812}
DARK        = {"red": 0.102, "green": 0.039, "blue": 0.071}
WHITE       = {"red": 1.0,   "green": 1.0,   "blue": 1.0}
CREAM       = {"red": 0.925, "green": 0.886, "blue": 0.816}
GREEN_LIGHT = {"red": 0.863, "green": 0.980, "blue": 0.871}
RED_LIGHT   = {"red": 0.996, "green": 0.878, "blue": 0.878}
GREY_LIGHT  = {"red": 0.960, "green": 0.960, "blue": 0.960}


def rgb(r, g, b):
    return {"red": r/255, "green": g/255, "blue": b/255}


# ── GOOGLE SHEETS CONNECTION ──────────────────────────────────────────────────

def connect(service_account_path=None, sheet_id=None):
    """
    Connect to Google Sheets using service account credentials.

    Args:
        service_account_path (str): Path to service account JSON file
        sheet_id (str): Google Spreadsheet ID

    Returns:
        gspread.Spreadsheet object
    """
    if not GSPREAD_AVAILABLE:
        raise ImportError(
            "gspread not installed. Run: pip install gspread google-auth"
        )

    sa_path  = service_account_path or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
    s_id     = sheet_id             or os.getenv("GOOGLE_SHEET_ID")

    if not sa_path:
        raise ValueError(
            "No service account JSON found.\n"
            "Set GOOGLE_SERVICE_ACCOUNT_JSON in your .env file\n"
            "or pass service_account_path= to connect()"
        )

    if not s_id:
        raise ValueError(
            "No Google Sheet ID found.\n"
            "Set GOOGLE_SHEET_ID in your .env file\n"
            "or pass sheet_id= to connect()"
        )

    scopes = [
        "https://spreadsheets.google.com/feeds",
        "https://www.googleapis.com/auth/spreadsheets",
        "https://www.googleapis.com/auth/drive",
    ]

    if isinstance(sa_path, dict):
        creds = Credentials.from_service_account_info(sa_path, scopes=scopes)
    else:
        creds = Credentials.from_service_account_file(sa_path, scopes=scopes)

    client = gspread.authorize(creds)
    sheet  = client.open_by_key(s_id)

    print(f"  ✓ Connected to: {sheet.title}")
    return sheet


# ── SHEET HELPERS ─────────────────────────────────────────────────────────────

def get_or_create_tab(sheet, title, index=None):
    """Get existing worksheet or create new one."""
    try:
        ws = sheet.worksheet(title)
        ws.clear()
        print(f"  ↺ Cleared tab: {title}")
        return ws
    except gspread.WorksheetNotFound:
        if index is not None:
            ws = sheet.add_worksheet(title=title, rows=500, cols=30, index=index)
        else:
            ws = sheet.add_worksheet(title=title, rows=500, cols=30)
        print(f"  + Created tab: {title}")
        return ws


def format_header_row(ws, row_num, num_cols):
    """Format a header row with berry background and white text."""
    ws.format(
        f"A{row_num}:{chr(64 + num_cols)}{row_num}",
        {
            "backgroundColor": BERRY,
            "textFormat": {
                "foregroundColor": WHITE,
                "bold": True,
                "fontSize": 10,
            },
            "horizontalAlignment": "CENTER",
        }
    )


def format_title_row(ws, cell, text=None):
    """Format a title/banner row."""
    ws.format(cell, {
        "backgroundColor": DARK,
        "textFormat": {
            "foregroundColor": GOLD,
            "bold": True,
            "fontSize": 13,
        },
    })


def set_column_widths(ws, widths_dict):
    """
    Set column widths.
    widths_dict: {col_index_0based: width_pixels}
    """
    requests = []
    for col_idx, width in widths_dict.items():
        requests.append({
            "updateDimensionProperties": {
                "range": {
                    "sheetId":    ws.id,
                    "dimension":  "COLUMNS",
                    "startIndex": col_idx,
                    "endIndex":   col_idx + 1,
                },
                "properties": {"pixelSize": width},
                "fields": "pixelSize",
            }
        })
    if requests:
        ws.spreadsheet.batch_update({"requests": requests})


def freeze_rows(ws, num_rows=2):
    """Freeze top rows."""
    ws.spreadsheet.batch_update({"requests": [{
        "updateSheetProperties": {
            "properties": {
                "sheetId": ws.id,
                "gridProperties": {"frozenRowCount": num_rows},
            },
            "fields": "gridProperties.frozenRowCount",
        }
    }]})


# ── TAB 1: WEI SCORES (GLOBAL) ────────────────────────────────────────────────

def write_global_scores(sheet, df, year=BASELINE_YEAR):
    """Write global country WEI scores tab."""
    ws = get_or_create_tab(sheet, "📊 WEI Scores", index=0)

    # Title row
    ws.update("A1", [[f"SHEtoken — Women's Empowerment Index {year} | Global Country Scores | shetoken.org"]])
    ws.merge_cells("A1:R1")
    format_title_row(ws, "A1:R1")

    # Headers
    headers = [
        "Rank", "Country", "ISO", "Region", "Tier",
        "Population (M)", "WEI Score", "Empowerment",
        "Education", "Economic", "Health", "Crime Penalty",
        "Ticker", "Data Source", "Verified", "Year", "Notes"
    ]
    ws.update("A2", [headers])
    format_header_row(ws, 2, len(headers))
    freeze_rows(ws, 2)

    # Data
    rows = []
    for _, r in df.iterrows():
        rows.append([
            r.get("rank", ""),
            r.get("country", ""),
            r.get("iso_code", ""),
            r.get("region", ""),
            r.get("tier", ""),
            r.get("population_millions", ""),
            r.get("wei_score", ""),
            r.get("empowerment_score", ""),
            r.get("education_score", ""),
            r.get("economic_score", ""),
            r.get("health_score", ""),
            r.get("crime_penalty_score", ""),
            r.get("ticker", ""),
            r.get("data_source", ""),
            r.get("verified", ""),
            r.get("year", year),
            r.get("notes", ""),
        ])

    if rows:
        ws.update(f"A3", rows)

    # Alternating row colours
    n = len(rows)
    for i in range(0, n, 2):
        row_num = i + 3
        ws.format(f"A{row_num}:Q{row_num}", {
            "backgroundColor": GREY_LIGHT
        })

    # Colour WEI score column by tier
    for i, row_data in enumerate(rows):
        row_num = i + 3
        score = row_data[6]
        if isinstance(score, (int, float)):
            if score >= 70:
                bg = GREEN_LIGHT
            elif score >= 45:
                bg = GOLD_LIGHT
            elif score >= 20:
                bg = {"red": 1.0, "green": 0.95, "blue": 0.80}
            else:
                bg = RED_LIGHT
            ws.format(f"G{row_num}", {"backgroundColor": bg})

    set_column_widths(ws, {
        0: 50,   # Rank
        1: 160,  # Country
        2: 50,   # ISO
        3: 110,  # Region
        4: 45,   # Tier
        5: 90,   # Population
        6: 85,   # WEI Score
        7: 90,   # Empowerment
        8: 80,   # Education
        9: 80,   # Economic
        10: 65,  # Health
        11: 100, # Crime Penalty
        12: 90,  # Ticker
    })

    print(f"    ✓ WEI Scores tab: {len(rows)} countries")
    time.sleep(1)


# ── TAB 2: INDIA STATES ───────────────────────────────────────────────────────

def write_india_states(sheet, df, year=BASELINE_YEAR):
    """Write India state WEI scores tab."""
    ws = get_or_create_tab(sheet, "🇮🇳 India States", index=1)

    ws.update("A1", [[f"SHEtoken — India State WEI Scores {year} | shetoken.org"]])
    ws.merge_cells("A1:T1")
    format_title_row(ws, "A1:T1")

    headers = [
        "Rank", "State", "Code", "Ticker", "Region",
        "Population (M)", "WEI Score", "vs Last Year", "HOT",
        "Empowerment", "Education", "Economic", "Health", "Crime Penalty",
        "Key Programs", "Verified", "Year"
    ]
    ws.update("A2", [headers])
    format_header_row(ws, 2, len(headers))
    freeze_rows(ws, 2)

    rows = []
    for _, r in df.iterrows():
        change = r.get("change", "")
        change_str = f"+{change}" if isinstance(change, (int, float)) and change > 0 else str(change)
        hot = "🔥 HOT" if str(r.get("hot", "")).lower() == "true" else ""

        rows.append([
            r.get("rank", ""),
            r.get("state", ""),
            r.get("state_code", ""),
            r.get("ticker", ""),
            r.get("region", ""),
            r.get("population_millions", ""),
            r.get("wei_score", ""),
            change_str,
            hot,
            r.get("empowerment_score", ""),
            r.get("education_score", ""),
            r.get("economic_score", ""),
            r.get("health_score", ""),
            r.get("crime_penalty_score", ""),
            r.get("key_programs", "")[:80] if r.get("key_programs") else "",
            r.get("verified", ""),
            r.get("year", year),
        ])

    if rows:
        ws.update("A3", rows)

    # Highlight HOT states
    for i, row_data in enumerate(rows):
        row_num = i + 3
        if row_data[8] == "🔥 HOT":
            ws.format(f"A{row_num}:Q{row_num}", {
                "backgroundColor": GOLD_LIGHT,
                "textFormat": {"bold": True},
            })
        elif i % 2 == 0:
            ws.format(f"A{row_num}:Q{row_num}", {
                "backgroundColor": GREY_LIGHT,
            })

    set_column_widths(ws, {
        0: 50,   # Rank
        1: 140,  # State
        2: 50,   # Code
        3: 90,   # Ticker
        4: 80,   # Region
        5: 90,   # Population
        6: 85,   # WEI Score
        7: 90,   # Change
        8: 70,   # HOT
        14: 250, # Key Programs
    })

    print(f"    ✓ India States tab: {len(rows)} states")
    time.sleep(1)


# ── TAB 3: LEADERBOARD ────────────────────────────────────────────────────────

def write_leaderboard(sheet, global_df, india_df, year=BASELINE_YEAR):
    """Write leaderboard tab — top scores and fastest movers."""
    ws = get_or_create_tab(sheet, "🏆 Leaderboard", index=2)

    ws.update("A1", [[f"SHEtoken — WEI Leaderboard {year} | shetoken.org"]])
    ws.merge_cells("A1:N1")
    format_title_row(ws, "A1:N1")

    row = 2

    # ── Top 10 Countries ──
    ws.update(f"A{row}", [["TOP 10 COUNTRIES — Highest WEI Score"]])
    ws.merge_cells(f"A{row}:G{row}")
    ws.format(f"A{row}:G{row}", {
        "backgroundColor": BERRY,
        "textFormat": {"foregroundColor": GOLD, "bold": True, "fontSize": 11},
    })
    row += 1

    top10_headers = ["Rank", "Country", "Ticker", "WEI Score",
                     "Empowerment", "Education", "Crime Penalty"]
    ws.update(f"A{row}", [top10_headers])
    format_header_row(ws, row, len(top10_headers))
    row += 1

    top10 = global_df.nlargest(10, "wei_score")
    for _, r in top10.iterrows():
        ws.update(f"A{row}", [[
            r.get("rank"), r.get("country"), r.get("ticker"),
            r.get("wei_score"), r.get("empowerment_score"),
            r.get("education_score"), r.get("crime_penalty_score"),
        ]])
        ws.format(f"D{row}", {"backgroundColor": GREEN_LIGHT})
        row += 1

    row += 1

    # ── India State Leaderboard ──
    ws.update(f"A{row}", [["INDIA STATE LEADERBOARD — WEI Rankings"]])
    ws.merge_cells(f"A{row}:G{row}")
    ws.format(f"A{row}:G{row}", {
        "backgroundColor": BERRY,
        "textFormat": {"foregroundColor": GOLD, "bold": True, "fontSize": 11},
    })
    row += 1

    india_headers = ["Rank", "State", "Ticker", "WEI Score",
                     "vs Last Year", "HOT", "Key Driver"]
    ws.update(f"A{row}", [india_headers])
    format_header_row(ws, row, len(india_headers))
    row += 1

    india_sorted = india_df.sort_values("wei_score", ascending=False)
    for _, r in india_sorted.iterrows():
        change = r.get("change", 0) or 0
        change_str = f"+{change}" if change > 0 else str(change)
        hot = "🔥" if str(r.get("hot", "")).lower() == "true" else ""
        programs = str(r.get("key_programs", ""))
        driver = programs.split("—")[0].strip()[:40] if "—" in programs else programs[:40]

        ws.update(f"A{row}", [[
            r.get("rank"), r.get("state"), r.get("ticker"),
            r.get("wei_score"), change_str, hot, driver,
        ]])

        if hot == "🔥":
            ws.format(f"A{row}:G{row}", {
                "backgroundColor": GOLD_LIGHT,
                "textFormat": {"bold": True},
            })
        elif change < 0:
            ws.format(f"E{row}", {"backgroundColor": RED_LIGHT})
        elif change > 0:
            ws.format(f"E{row}", {"backgroundColor": GREEN_LIGHT})

        row += 1

    set_column_widths(ws, {
        0: 50, 1: 150, 2: 100, 3: 90, 4: 90, 5: 60, 6: 220
    })

    print(f"    ✓ Leaderboard tab written")
    time.sleep(1)


# ── TAB 4: SUMMARY DASHBOARD ─────────────────────────────────────────────────

def write_summary(sheet, global_df, india_df, year=BASELINE_YEAR):
    """Write summary dashboard tab."""
    ws = get_or_create_tab(sheet, "📈 Summary", index=3)

    now = datetime.now().strftime("%B %d, %Y at %H:%M UTC")

    # Global stats
    global_wei  = round((
        global_df["wei_score"] * global_df["population_millions"]
    ).sum() / global_df["population_millions"].sum(), 1)

    tier_counts = global_df["tier"].value_counts().to_dict()
    highest     = global_df.loc[global_df["wei_score"].idxmax()]
    lowest      = global_df.loc[global_df["wei_score"].idxmin()]
    india_row   = global_df[global_df["iso_code"] == "IND"]
    india_wei   = india_row["wei_score"].values[0] if len(india_row) else "N/A"

    data = [
        [f"SHEtoken — WEI Summary Dashboard {year}"],
        [""],
        ["GLOBAL WEI INDEX", "", ""],
        ["Global WEI Score (pop-weighted)",  global_wei,       "Population-weighted average across all countries"],
        ["Countries Scored",                 len(global_df),   "UN-recognised countries in the index"],
        ["India WEI Score",                  india_wei,        "$SHE-IND tracker"],
        ["Last Updated",                     now,              "Automated pipeline"],
        [""],
        ["TIER BREAKDOWN", "", ""],
        ["Tier 1 Countries (WEI 70+)",       tier_counts.get(1, 0), "High performing — Nordic, Anglosphere"],
        ["Tier 2 Countries (WEI 45–69)",     tier_counts.get(2, 0), "Mid performing — developing with progress"],
        ["Tier 3 Countries (WEI 20–44)",     tier_counts.get(3, 0), "Developing — significant gender gaps"],
        ["Tier 4 Countries (WEI <20)",       tier_counts.get(4, 0), "Crisis level — minimum index weight"],
        [""],
        ["TOP & BOTTOM", "", ""],
        ["Highest WEI",  f"{highest['country']} ({highest['wei_score']})",  "Top performing country"],
        ["Lowest WEI",   f"{lowest['country']} ({lowest['wei_score']})",    "Lowest performing country"],
        [""],
        ["INDIA STATES", "", ""],
        ["States Scored",        len(india_df), "Major Indian states in the index"],
        ["Highest WEI State",    "", ""],
        ["Fastest Improving",    "", ""],
        [""],
        ["TOKEN MECHANICS", "", ""],
        ["Mint trigger",  "+1 WEI point = 10M SHE tokens minted",  "Added to WEI Impact Fund"],
        ["Burn trigger",  "-1 WEI point = 10M SHE tokens burned",  "Permanently removed from supply"],
        [""],
        ["LINKS", "", ""],
        ["Website",      "shetoken.org",                   ""],
        ["GitHub",       "github.com/shetoken",            "Open source methodology"],
        ["Whitepaper",   "shetoken.org/whitepaper",        ""],
        ["Contact",      "contact@shetoken.org",           ""],
    ]

    # Fill India state info
    if len(india_df) > 0:
        top_state  = india_df.loc[india_df["wei_score"].idxmax()]
        fast_state = india_df.loc[india_df["change"].idxmax()] if "change" in india_df.columns else top_state

        for i, row_data in enumerate(data):
            if row_data[0] == "Highest WEI State":
                data[i][1] = f"{top_state['state']} ({top_state['wei_score']})"
            if row_data[0] == "Fastest Improving":
                change = fast_state.get("change", "")
                data[i][1] = f"{fast_state['state']} (+{change} pts)"

    ws.update("A1", data)
    ws.merge_cells("A1:C1")
    format_title_row(ws, "A1:C1")

    # Format section headers
    section_rows = [3, 9, 15, 19, 23, 27]
    for r in section_rows:
        ws.format(f"A{r}:C{r}", {
            "backgroundColor": BERRY,
            "textFormat": {"foregroundColor": GOLD, "bold": True},
        })

    # Format value cells
    ws.format("B4:B35", {
        "textFormat": {"bold": True},
        "horizontalAlignment": "CENTER",
    })

    # Highlight global WEI
    ws.format("B4", {
        "backgroundColor": GOLD_LIGHT,
        "textFormat": {"bold": True, "fontSize": 14},
    })

    set_column_widths(ws, {0: 260, 1: 200, 2: 320})

    print(f"    ✓ Summary tab: Global WEI {global_wei}")
    time.sleep(1)


# ── TAB 5: METHODOLOGY ───────────────────────────────────────────────────────

def write_methodology(sheet):
    """Write methodology reference tab."""
    ws = get_or_create_tab(sheet, "ℹ️ Methodology", index=4)

    data = [
        ["SHEtoken — WEI Methodology Reference | shetoken.org"],
        [""],
        ["THE WEI FORMULA", ""],
        ["WEI = (Empowerment × 0.25) + (Education × 0.20) + (Economic × 0.20) + (Health × 0.15) − (Crime Penalty × 0.20)", ""],
        ["All pillar scores normalised 0–100. Crime Penalty is subtracted (higher crime = lower WEI).", ""],
        [""],
        ["PILLAR", "WEIGHT", "KEY INDICATORS", "PRIMARY SOURCE"],
        ["Empowerment",      "25%", "Women in parliament, ministerial roles, legal rights, freedom of movement", "IPU Parline, UN Women"],
        ["Education",        "20%", "Female literacy rate, school enrollment (primary, secondary, tertiary)", "UNESCO UIS, World Bank"],
        ["Economic",         "20%", "Gender wage gap, female LFPR, bank account ownership, property rights", "ILO, World Bank"],
        ["Health",           "15%", "Maternal mortality, female life expectancy, adolescent birth rate", "WHO GHO, World Bank"],
        ["Crime Penalty",    "20%", "Rape rate, domestic violence, femicide, trafficking, acid attacks", "UNODC, WHO, NCRB (India)"],
        [""],
        ["COUNTRY TIERS", "WEI RANGE", "EXAMPLES", "POPULATION WEIGHT"],
        ["Tier 1 — High performing",  "70–100", "Iceland, Norway, NZ",     "1.0×"],
        ["Tier 2 — Mid performing",   "45–69",  "India, Brazil, Kenya",    "1.0×"],
        ["Tier 3 — Developing",       "20–44",  "Pakistan, Nigeria",       "0.8×"],
        ["Tier 4 — Crisis level",     "0–19",   "Yemen, Afghanistan",      "0.6×"],
        [""],
        ["TOKEN MECHANICS", "", "", ""],
        ["Global WEI rises +1 point",  "→ 10,000,000 SHE tokens minted to WEI Impact Fund", "", ""],
        ["Global WEI falls −1 point",  "→ 10,000,000 SHE tokens permanently burned",        "", ""],
        ["Crime spike >15% in 1 year", "→ Crisis Trigger: DAO governance vote opens",        "", ""],
        [""],
        ["DATA TRANSPARENCY", "", "", ""],
        ["All calculations open-source", "github.com/shetoken",       "", ""],
        ["Challenge a score",            "Open GitHub Issue: wei-challenge", "", ""],
        ["Annual update cycle",          "30-day public review window after publication", "", ""],
        [""],
        ["Full methodology:  github.com/shetoken/blob/main/wei-index/methodology.md", ""],
    ]

    ws.update("A1", data)
    ws.merge_cells("A1:D1")
    format_title_row(ws, "A1:D1")

    ws.format("A3:D3", {"backgroundColor": BERRY,
                         "textFormat": {"foregroundColor": GOLD, "bold": True}})
    ws.format("A7:D7", {"backgroundColor": BERRY,
                         "textFormat": {"foregroundColor": GOLD, "bold": True}})
    ws.format("A14:D14", {"backgroundColor": BERRY,
                           "textFormat": {"foregroundColor": GOLD, "bold": True}})
    ws.format("A20:D20", {"backgroundColor": BERRY,
                           "textFormat": {"foregroundColor": GOLD, "bold": True}})
    ws.format("A24:D24", {"backgroundColor": BERRY,
                           "textFormat": {"foregroundColor": GOLD, "bold": True}})

    for r in [8, 9, 10, 11, 12]:
        ws.format(f"A{r}:D{r}", {
            "backgroundColor": GOLD_LIGHT if r % 2 == 0 else WHITE,
        })

    set_column_widths(ws, {0: 220, 1: 260, 2: 300, 3: 160})

    print(f"    ✓ Methodology tab written")
    time.sleep(1)


# ── SET PUBLIC READ PERMISSION ────────────────────────────────────────────────

def make_public_readable(sheet, service_account_path=None):
    """
    Make the Google Sheet publicly viewable (read only).
    No Google account needed to view it.
    """
    try:
        import googleapiclient.discovery
        sa_path = service_account_path or os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON")
        from google.oauth2.service_account import Credentials

        scopes = ["https://www.googleapis.com/auth/drive"]
        if isinstance(sa_path, dict):
            creds = Credentials.from_service_account_info(sa_path, scopes=scopes)
        else:
            creds = Credentials.from_service_account_file(sa_path, scopes=scopes)

        drive = googleapiclient.discovery.build("drive", "v3", credentials=creds)
        drive.permissions().create(
            fileId=sheet.id,
            body={"type": "anyone", "role": "reader"},
        ).execute()
        print(f"  ✓ Sheet is now publicly readable (view only)")
        print(f"    URL: https://docs.google.com/spreadsheets/d/{sheet.id}")
    except Exception as e:
        print(f"  ⚠ Could not set public permission automatically: {e}")
        print(f"  Manual steps:")
        print(f"    1. Open your Google Sheet")
        print(f"    2. Click Share → Change to anyone with the link → Viewer")
        print(f"    3. Copy the link to share publicly")


# ── MAIN ──────────────────────────────────────────────────────────────────────

def write_all(service_account_path=None, sheet_id=None, year=BASELINE_YEAR):
    """
    Main entry point — write all data to Google Sheets.

    Args:
        service_account_path: Path to service account JSON (or dict)
        sheet_id: Google Spreadsheet ID
        year: Data year
    """
    print("\nSHEtoken — Writing to Google Sheets")
    print("=" * 60)

    # Load data
    baseline_path = OUTPUT_DIR / f"baseline-{year}.csv"
    india_path    = OUTPUT_DIR / f"india-states-{year}.csv"

    if not baseline_path.exists():
        print(f"✗ {baseline_path} not found.")
        print("  Run: python run_pipeline.py --generate-only first")
        return False

    # Skip comment lines starting with #
    global_df = pd.read_csv(baseline_path, comment="#")
    india_df  = pd.read_csv(india_path, comment="#") if india_path.exists() else pd.DataFrame()

    print(f"  Loaded: {len(global_df)} countries, {len(india_df)} India states")

    # Connect
    print("\nConnecting to Google Sheets...")
    try:
        sheet = connect(service_account_path, sheet_id)
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        return False

    # Write all tabs
    print("\nWriting tabs...")
    write_global_scores(sheet, global_df, year)
    write_india_states(sheet, india_df, year)
    write_leaderboard(sheet, global_df, india_df, year)
    write_summary(sheet, global_df, india_df, year)
    write_methodology(sheet)

    # Make publicly readable
    print("\nSetting permissions...")
    make_public_readable(sheet, service_account_path)

    print(f"\n{'='*60}")
    print(f"✓ Google Sheet updated successfully")
    print(f"  URL: https://docs.google.com/spreadsheets/d/{sheet_id or os.getenv('GOOGLE_SHEET_ID')}")
    print(f"  Tabs: 📊 WEI Scores | 🇮🇳 India States | 🏆 Leaderboard | 📈 Summary | ℹ️ Methodology")
    print(f"{'='*60}")
    return True


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--sa",       help="Service account JSON path")
    parser.add_argument("--sheet-id", help="Google Spreadsheet ID")
    parser.add_argument("--year",     type=int, default=BASELINE_YEAR)
    args = parser.parse_args()

    write_all(
        service_account_path=args.sa,
        sheet_id=args.sheet_id,
        year=args.year,
    )
