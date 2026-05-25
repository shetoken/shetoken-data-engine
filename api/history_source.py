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
        logger.warning(f"history query failed: {e}")
        return []

def get_history(index_name, iso_code):
    """Monthly trend for one country+index, oldest→newest."""
    return _q("she_index_history", {
        "select": "snapshot_date,score,rank",
        "index_name": f"eq.{index_name}",
        "iso_code": f"eq.{iso_code.upper()}",
        "order": "snapshot_date.asc",
    })

def get_history_weekly(index_name, iso_code):
    """Weekly trend for one country+index, oldest→newest."""
    return _q("she_index_history_weekly", {
        "select": "week,score,snapshot_date",
        "index_name": f"eq.{index_name}",
        "iso_code": f"eq.{iso_code.upper()}",
        "order": "week.asc",
    })
