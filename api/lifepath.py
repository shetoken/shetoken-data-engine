"""
SHEtoken API — Life Path Model ("100 Girls")
==============================================
Turns the indexes into a felt narrative: pick a country, and walk a cohort of
100 girls born there today through life, stage by stage, using REAL data.

HONEST FRAMING (must carry through to the UI):
  • This is a COHORT of 100, never "you". "27 of 100 will face violence" — not
    "you will face violence". Avoids false personal prediction + trauma-at-you.
  • Every number is a real, sourced, cross-sectional statistic.
  • Assembling them into one "life" is a NARRATIVE DEVICE, not a validated
    longitudinal life-course projection. The endpoint says so, and the UI must.

Reads the committed CSVs (vital-stats, rape-counts, widow-elderly) — these are
stable annual figures, safe to read from the Railway filesystem.
"""

from __future__ import annotations
import logging
from data_loader import load_csv, safe_float, safe_int, DATA_DIR

logger = logging.getLogger(__name__)

DISCLAIMER = (
    "An illustrative cohort of 100 girls born today, walked through life using "
    "current cross-sectional statistics for this country. Each figure is real "
    "and sourced. This is a narrative device to make the data felt — not a "
    "personal prediction or a validated life-course forecast."
)


def _find(rows: list[dict], iso: str) -> dict | None:
    iso = iso.upper()
    for r in rows:
        if (r.get("iso_code") or "").upper() == iso:
            return r
    return None


def _pct_of_100(pct) -> int | None:
    """Convert a percentage to a count out of 100 (rounded)."""
    v = safe_float(pct)
    return round(v) if v is not None else None


def _every_x_time(annual) -> str | None:
    """Convert an annual count into a 'every X' felt-time phrase."""
    n = safe_float(annual)
    if not n or n <= 0:
        return None
    minutes = (365 * 24 * 60) / n
    if minutes < 1:
        secs = round(minutes * 60)
        return f"every {secs} seconds"
    if minutes < 90:
        return f"every {round(minutes)} minutes"
    hours = minutes / 60
    if hours < 36:
        return f"every {round(hours)} hours"
    return f"every {round(hours/24)} days"


def get_life_path(iso_code: str) -> dict | None:
    """Assemble the staged life journey for one country from real data."""
    vital = _find(load_csv(DATA_DIR / "womens-vital-stats-2025.csv"), iso_code)
    rape  = _find(load_csv(DATA_DIR / "rape-counts-reported-vs-estimated-2025.csv"), iso_code)
    widow = _find(load_csv(DATA_DIR / "widow-elderly-index-2025.csv"), iso_code)
    if not vital and not rape:
        return None

    v = vital or {}
    r = rape or {}
    w = widow or {}
    stages = []

    # ── Stage 1 — Born ───────────────────────────────────────────────────────
    born_week = safe_float(v.get("girls_born_per_week_est"))
    le_f = safe_float(v.get("life_expectancy_female"))
    stages.append({
        "stage": "Born",
        "age_band": "0",
        "headline": "She is born",
        "felt": f"A girl is born here roughly {_every_x_time(born_week*52) or 'often'}"
                if born_week else None,
        "detail": f"Female life expectancy here is {le_f:.0f} years." if le_f else None,
        "source": "UN Population Division / national vital statistics",
    })

    # ── Stage 2 — School ─────────────────────────────────────────────────────
    prim = _pct_of_100(v.get("girls_primary_enrollment_pct"))
    sec  = _pct_of_100(v.get("girls_secondary_enrollment_pct"))
    stages.append({
        "stage": "Childhood",
        "age_band": "5–17",
        "headline": "Will she stay in school?",
        "cohort": (f"{prim} of 100 start primary school; {sec} reach secondary."
                   if prim and sec else None),
        "felt": (f"A girl drops out of school here {_every_x_time(safe_float(v.get('girls_drop_out_school_per_week_est'))*52)}"
                 if safe_float(v.get("girls_drop_out_school_per_week_est")) else None),
        "source": "UNESCO UIS",
    })

    # ── Stage 3 — Adolescence / child marriage ───────────────────────────────
    cm = _pct_of_100(v.get("child_marriage_rate_pct"))
    stages.append({
        "stage": "Adolescence",
        "age_band": "10–18",
        "headline": "Will she choose when to marry?",
        "cohort": f"{cm} of 100 are married before 18." if cm is not None else None,
        "felt": (f"A girl here is married before 18 {_every_x_time(safe_float(v.get('girls_married_under18_per_week_est'))*52)}"
                 if safe_float(v.get("girls_married_under18_per_week_est")) else None),
        "source": "UNICEF",
    })

    # ── Stage 4 — Sexual violence (lifetime) ─────────────────────────────────
    prev = _pct_of_100(r.get("who_lifetime_prevalence_pct"))
    stages.append({
        "stage": "Womanhood",
        "age_band": "15+",
        "headline": "Will she be safe?",
        "cohort": (f"{prev} of 100 will face sexual or physical violence in their lifetime."
                   if prev is not None else None),
        "felt": (f"A woman here is raped {_every_x_time(safe_float(r.get('estimated_annual')))} (estimated, incl. unreported)"
                 if safe_float(r.get("estimated_annual")) else None),
        "note": ("Marital rape is not a crime here." if str(r.get("marital_rape_criminalised", "1")) in ("0", "0.0", "false", "False") else None),
        "source": "WHO prevalence surveys + UNODC",
    })

    # ── Stage 5 — Work ───────────────────────────────────────────────────────
    lab = _pct_of_100(v.get("female_labour_force_pct"))
    wage = safe_float(v.get("gender_wage_gap_pct"))
    bank = _pct_of_100(v.get("women_with_bank_account_pct"))
    stages.append({
        "stage": "Working life",
        "age_band": "18–60",
        "headline": "Will she earn — and control — her own money?",
        "cohort": (f"{lab} of 100 join the formal labour force; {bank} of 100 have their own bank account."
                   if lab is not None and bank is not None else None),
        "detail": f"Women here earn about {wage:.0f}% less than men." if wage else None,
        "source": "ILO / World Bank Findex",
    })

    # ── Stage 6 — Motherhood ─────────────────────────────────────────────────
    mm = safe_float(v.get("maternal_mortality_per_100k"))
    stages.append({
        "stage": "Motherhood",
        "age_band": "20–45",
        "headline": "Will she survive childbirth?",
        "detail": (f"{mm:.0f} mothers die per 100,000 births here"
                   + (f" — about 1 in {round(100000/mm):,}." if mm else ".")
                   if mm else None),
        "felt": (f"A mother dies in childbirth here {_every_x_time(safe_float(v.get('maternal_deaths_per_week_est'))*52)}"
                 if safe_float(v.get("maternal_deaths_per_week_est")) else None),
        "source": "WHO Global Health Observatory",
    })

    # ── Stage 7 — Violence at home (femicide) ────────────────────────────────
    fem = safe_float(v.get("women_killed_by_partner_per_100k"))
    stages.append({
        "stage": "Partnership",
        "age_band": "18+",
        "headline": "Will home be safe?",
        "detail": f"{fem:.1f} of every 100,000 women here are killed by a partner each year." if fem else None,
        "felt": (f"A woman here is killed by her partner {_every_x_time(safe_float(v.get('women_killed_by_partner_per_week_est'))*52)}"
                 if safe_float(v.get("women_killed_by_partner_per_week_est")) else None),
        "source": "UNODC femicide data",
    })

    # ── Stage 8 — Old age / widowhood ────────────────────────────────────────
    wp = _pct_of_100(w.get("widows_in_poverty_pct"))
    pen = _pct_of_100(w.get("pension_coverage_pct"))
    stages.append({
        "stage": "Old age",
        "age_band": "60+",
        "headline": "Will she be cared for?",
        "cohort": (f"Of widows here, {wp} of 100 live in poverty; only {pen} of 100 receive any pension."
                   if wp is not None and pen is not None else None),
        "source": "WEVI — national + World Bank pension data",
    })

    name = (vital or rape or {}).get("country", iso_code)
    return {
        "iso_code": iso_code.upper(),
        "country": name,
        "disclaimer": DISCLAIMER,
        "cohort_size": 100,
        "stages": [s for s in stages if any(s.get(k) for k in ("cohort", "felt", "detail"))],
    }
