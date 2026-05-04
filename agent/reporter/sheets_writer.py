"""
SHEtoken Agent — Google Sheets Signal Writer
Writes weekly signals to the Signals tab.
"""
import logging, sys
from datetime import datetime
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from config import GOOGLE_SHEET_ID, GOOGLE_SA_JSON, SIGNALS_TAB

logger = logging.getLogger(__name__)

try:
    import gspread
    from google.oauth2.service_account import Credentials
    GSPREAD_OK = True
except ImportError:
    GSPREAD_OK = False


def write_signals_to_sheet(report: dict) -> bool:
    if not GSPREAD_OK:
        logger.warning("gspread not installed — skipping sheets write")
        return False
    if not GOOGLE_SHEET_ID or not GOOGLE_SA_JSON:
        logger.warning("Google Sheets not configured — skipping")
        return False

    try:
        scopes = ["https://spreadsheets.google.com/feeds",
                  "https://www.googleapis.com/auth/spreadsheets"]
        if isinstance(GOOGLE_SA_JSON, dict):
            creds = Credentials.from_service_account_info(GOOGLE_SA_JSON, scopes=scopes)
        else:
            creds = Credentials.from_service_account_file(GOOGLE_SA_JSON, scopes=scopes)

        client = gspread.authorize(creds)
        sheet  = client.open_by_key(GOOGLE_SHEET_ID)

        # Get or create signals tab
        try:
            ws = sheet.worksheet(SIGNALS_TAB)
        except gspread.WorksheetNotFound:
            ws = sheet.add_worksheet(title=SIGNALS_TAB, rows=2000, cols=20)

        week    = report.get("week","")
        signals = report.get("raw_signals", [])

        # Headers (only write if sheet is empty)
        if ws.row_count == 0 or not ws.cell(1,1).value:
            headers = ["Week","Published","Source","Language","Country","State",
                       "Pillar","Direction","Severity","Confidence","Crisis",
                       "Summary","URL","Model"]
            ws.update("A1", [headers])
            ws.format("A1:N1", {
                "backgroundColor": {"red":0.427,"green":0.180,"blue":0.275},
                "textFormat": {"foregroundColor":{"red":1,"green":1,"blue":1},"bold":True}
            })

        # Append signal rows
        rows = []
        for s in signals:
            rows.append([
                week,
                s.get("published",""),
                s.get("source",""),
                s.get("language",""),
                s.get("country",""),
                s.get("state",""),
                s.get("pillar",""),
                s.get("direction",0),
                s.get("severity",0),
                s.get("confidence",0),
                "YES" if s.get("crisis") else "",
                s.get("summary_en",""),
                s.get("url",""),
                s.get("model_used",""),
            ])

        if rows:
            ws.append_rows(rows, value_input_option="RAW")
            logger.info(f"Wrote {len(rows)} signal rows to Google Sheets")

        return True

    except Exception as e:
        logger.error(f"Sheets write failed: {e}")
        return False


def write_live_wei_to_sheet(updated_rows: list, week: str) -> bool:
    """
    Write live WEI scores tab — shows baseline vs signal-adjusted scores.
    """
    if not GSPREAD_OK or not GOOGLE_SHEET_ID or not GOOGLE_SA_JSON:
        logger.warning("Google Sheets not configured")
        return False

    try:
        from config import WEI_LIVE_TAB
        scopes = ["https://spreadsheets.google.com/feeds",
                  "https://www.googleapis.com/auth/spreadsheets"]
        if isinstance(GOOGLE_SA_JSON, dict):
            creds = Credentials.from_service_account_info(GOOGLE_SA_JSON, scopes=scopes)
        else:
            creds = Credentials.from_service_account_file(GOOGLE_SA_JSON, scopes=scopes)

        client = gspread.authorize(creds)
        sheet  = client.open_by_key(GOOGLE_SHEET_ID)

        try:
            ws = sheet.worksheet(WEI_LIVE_TAB)
            ws.clear()
        except Exception:
            ws = sheet.add_worksheet(title=WEI_LIVE_TAB, rows=300, cols=20)

        ws.update("A1", [[
            f"SHEtoken WEI Live Scores — Week {week} | "
            f"Baseline + news signal adjustment | shetoken.org"
        ]])
        ws.merge_cells("A1:N1")
        ws.format("A1:N1", {
            "backgroundColor": {"red":0.427,"green":0.180,"blue":0.275},
            "textFormat": {"foregroundColor":{"red":0.788,"green":0.659,"blue":0.298},
                           "bold":True,"fontSize":11}
        })

        headers = ["Rank","Country","ISO","Tier","WEI (Live)","WEI (Baseline)",
                   "Weekly Δ","Signals","Empowerment","Education","Economic",
                   "Health","Bodily Autonomy","Safety & Justice"]
        ws.update("A2", [headers])
        ws.format("A2:N2", {
            "backgroundColor": {"red":0.427,"green":0.180,"blue":0.275},
            "textFormat": {"foregroundColor":{"red":1,"green":1,"blue":1},"bold":True}
        })

        rows = []
        for r in updated_rows[:100]:   # top 100 countries
            live     = float(r.get("wei_score", 0))
            baseline = float(r.get("wei_score_baseline", live))
            delta    = round(live - baseline, 2)
            rows.append([
                r.get("rank",""),
                r.get("country",""),
                r.get("iso_code",""),
                r.get("tier",""),
                live,
                baseline,
                f"+{delta}" if delta >= 0 else str(delta),
                r.get("signal_count_this_week", 0),
                r.get("empowerment_score",""),
                r.get("education_score",""),
                r.get("economic_score",""),
                r.get("health_score",""),
                r.get("bodily_autonomy_score",""),
                r.get("safety_justice_score",""),
            ])

        if rows:
            ws.update("A3", rows)

        # Colour delta column
        for i, row_data in enumerate(rows):
            row_num = i + 3
            delta_val = row_data[6]
            try:
                d = float(str(delta_val).replace("+",""))
                if d > 0:
                    ws.format(f"G{row_num}", {
                        "backgroundColor": {"red":0.863,"green":0.980,"blue":0.871}
                    })
                elif d < 0:
                    ws.format(f"G{row_num}", {
                        "backgroundColor": {"red":0.996,"green":0.878,"blue":0.878}
                    })
            except ValueError:
                pass

        logger.info(f"Wrote {len(rows)} rows to Live WEI tab")
        return True

    except Exception as e:
        logger.error(f"Live WEI sheets write failed: {e}")
        return False
