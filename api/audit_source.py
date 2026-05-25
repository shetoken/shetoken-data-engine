import os, logging
logger = logging.getLogger(__name__)
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_KEY = os.getenv("SUPABASE_ANON_KEY") or os.getenv("SUPABASE_PUBLISHABLE_KEY", "")

def _q(table, params):
    if not SUPABASE_URL or not SUPABASE_KEY:
        return []
    try:
        import httpx
        r = httpx.get(f"{SUPABASE_URL}/rest/v1/{table}", params=params,
            headers={"apikey": SUPABASE_KEY, "Authorization": f"Bearer {SUPABASE_KEY}"},
            timeout=5.0)
        return r.json() if r.status_code == 200 else []
    except Exception as e:
        logger.warning(f"audit query failed: {e}")
        return []

def get_audit(index_name, iso_code, snapshot_date=None):
    """All raw indicators behind one country+index. Latest month, or a given one."""
    params = {
        "select": "indicator_key,indicator_value,snapshot_date,country",
        "index_name": f"eq.{index_name}",
        "iso_code": f"eq.{iso_code.upper()}",
        "order": "snapshot_date.desc,indicator_key.asc",
    }
    if snapshot_date:
        params["snapshot_date"] = f"eq.{snapshot_date}"
    rows = _q("she_indicator_history", params)
    if not snapshot_date and rows:                 # keep only the latest month
        latest = rows[0]["snapshot_date"]
        rows = [r for r in rows if r["snapshot_date"] == latest]
    return rows

def get_indicator_trend(index_name, iso_code, indicator_key):
    """One indicator's value over time for a country."""
    return _q("she_indicator_history", {
        "select": "snapshot_date,indicator_value",
        "index_name": f"eq.{index_name}",
        "iso_code": f"eq.{iso_code.upper()}",
        "indicator_key": f"eq.{indicator_key}",
        "order": "snapshot_date.asc",
    })
