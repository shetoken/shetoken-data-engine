"""
SHEtoken — WEI Data Pipeline Runner
======================================
Master script that runs the complete data pipeline
from API fetching through to final CSV output.

Usage:
    # Full pipeline (fetch + process + generate):
    python run_pipeline.py

    # Skip fetching (use existing raw data):
    python run_pipeline.py --skip-fetch

    # Only generate CSVs (use existing processed data):
    python run_pipeline.py --generate-only

    # Use fallback estimates (no API calls):
    python run_pipeline.py --fallback

    # Specific year:
    python run_pipeline.py --year 2025

Prerequisites:
    pip install -r requirements.txt

Optional:
    Create a .env file with:
        UNESCO_API_KEY=your_key_here

© 2026 SHE Foundation. Licensed under MIT.
"""

import argparse
import subprocess
import sys
import os
import time
from datetime import datetime
from pathlib import Path

BASE_DIR = Path(__file__).parent


def run_step(script_path, args=None, description=""):
    """Run a pipeline step and return success/failure."""
    cmd = [sys.executable, str(script_path)]
    if args:
        cmd.extend(args)

    print(f"\n{'─'*60}")
    print(f"▶  {description}")
    print(f"   {' '.join(cmd)}")
    print(f"{'─'*60}")

    start = time.time()
    result = subprocess.run(cmd, cwd=str(BASE_DIR))
    elapsed = round(time.time() - start, 1)

    if result.returncode == 0:
        print(f"\n   ✓ Completed in {elapsed}s")
        return True
    else:
        print(f"\n   ✗ FAILED (exit code {result.returncode})")
        return False


def check_requirements():
    """Check required packages are installed."""
    required = ["requests", "pandas", "numpy"]
    missing  = []
    for pkg in required:
        try:
            __import__(pkg)
        except ImportError:
            missing.append(pkg)

    if missing:
        print(f"✗ Missing packages: {', '.join(missing)}")
        print(f"  Install with: pip install -r requirements.txt")
        return False
    return True


def print_banner():
    print("""
╔══════════════════════════════════════════════════════════╗
║           SHEtoken — WEI Data Pipeline                  ║
║      Women's Empowerment Index Annual Update             ║
╚══════════════════════════════════════════════════════════╝
""")


def main():
    parser = argparse.ArgumentParser(
        description="Run the SHEtoken WEI data pipeline"
    )
    parser.add_argument(
        "--skip-fetch",
        action="store_true",
        help="Skip API fetching, use existing raw data"
    )
    parser.add_argument(
        "--generate-only",
        action="store_true",
        help="Only generate final CSVs from existing processed data"
    )
    parser.add_argument(
        "--fallback",
        action="store_true",
        help="Use hardcoded fallback estimates (no API calls needed)"
    )
    parser.add_argument(
        "--year",
        type=int,
        default=2025,
        help="Baseline year (default: 2025)"
    )
    parser.add_argument(
        "--sheets",
        action="store_true",
        help="Write final output to Google Sheets (requires .env setup)"
    )
    parser.add_argument(
        "--excel",
        action="store_true",
        help="Generate local Excel backup file in data/output/"
    )
    parser.add_argument(
        "--ncrb-pdf",
        type=str,
        default=None,
        help="Path to NCRB Crime in India PDF (for India state crime data)"
    )
    args = parser.parse_args()

    print_banner()
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Year:    {args.year}")
    print(f"Mode:    {'fallback' if args.fallback else 'live API'}")

    if not check_requirements():
        sys.exit(1)

    results = {}

    # ── STEP 1: FETCH ─────────────────────────────────────────────────────────
    if not args.skip_fetch and not args.generate_only and not args.fallback:
        print("\n\n══ PHASE 1: FETCHING DATA FROM APIS ══")

        fetch_scripts = [
            ("data/fetch/fetch_world_bank.py", [],
             "World Bank — economic, education, health indicators"),
            ("data/fetch/fetch_who.py",         [],
             "WHO GHO — health and violence indicators"),
            ("data/fetch/fetch_ilo.py",          [],
             "ILO STAT — labour force and wage data"),
            ("data/fetch/fetch_ipu.py",          [],
             "IPU Parline — women in parliament data"),
            ("data/fetch/fetch_unesco.py",       [],
             "UNESCO UIS — education and literacy data"),
        ]

        # NCRB (India states only — requires PDF)
        if args.ncrb_pdf:
            fetch_scripts.append((
                "data/fetch/fetch_ncrb.py",
                ["--pdf", args.ncrb_pdf],
                "NCRB — India state crime data (PDF parser)"
            ))
        else:
            print("\n  ℹ NCRB: No PDF provided")
            print("    India state crime data will use manual template")
            print("    To include: python run_pipeline.py --ncrb-pdf path/to/report.pdf")
            run_step(
                BASE_DIR / "data/fetch/fetch_ncrb.py",
                ["--template"],
                "NCRB — creating manual input template"
            )

        for script, script_args, desc in fetch_scripts:
            ok = run_step(BASE_DIR / script, script_args, desc)
            results[script] = ok
            if not ok:
                print(f"\n  ⚠ {script} failed — continuing with available data")

    # ── STEP 2: PROCESS ───────────────────────────────────────────────────────
    if not args.generate_only and not args.fallback:
        print("\n\n══ PHASE 2: PROCESSING & NORMALISING ══")

        process_steps = [
            ("data/process/normalise.py",    [],
             "Normalise raw indicators to 0–100 scale"),
            ("data/process/build_pillars.py", [],
             "Build five WEI pillar scores"),
            ("data/process/validate.py",     [],
             "Validate processed data quality"),
        ]

        for script, script_args, desc in process_steps:
            ok = run_step(BASE_DIR / script, script_args, desc)
            results[script] = ok
            if not ok and "validate" not in script:
                print(f"\n  ✗ Critical step failed: {script}")
                print("  Pipeline cannot continue. Check errors above.")
                sys.exit(1)

    # ── STEP 3: GENERATE OUTPUTS ──────────────────────────────────────────────
    print("\n\n══ PHASE 3: GENERATING OUTPUT FILES ══")

    fallback_flag = ["--fallback"] if args.fallback else []
    year_flag     = ["--year", str(args.year)]

    generate_steps = [
        ("data/generate_baseline.py",      fallback_flag + year_flag,
         f"Generate baseline-{args.year}.csv (global countries)"),
        ("data/generate_india_states.py",  fallback_flag + year_flag,
         f"Generate india-states-{args.year}.csv (Indian states)"),
    ]

    for script, script_args, desc in generate_steps:
        ok = run_step(BASE_DIR / script, script_args, desc)
        results[script] = ok

    # ── STEP 4: WRITE TO GOOGLE SHEETS ───────────────────────────────────────
    if args.sheets:
        print("\n\n══ PHASE 4: WRITING TO GOOGLE SHEETS ══")
        ok = run_step(
            BASE_DIR / "data/write_to_sheets.py", [],
            "Write WEI scores to Google Sheets (public view)"
        )
        results["data/write_to_sheets.py"] = ok
        if not ok:
            print("  ⚠ Google Sheets write failed.")
            print("  Check your .env file has GOOGLE_SHEET_ID and GOOGLE_SERVICE_ACCOUNT_JSON set.")

    # ── STEP 5: GENERATE EXCEL BACKUP ────────────────────────────────────────
    if args.excel:
        print("\n\n══ PHASE 5: GENERATING EXCEL BACKUP ══")
        ok = run_step(
            BASE_DIR / "data/write_to_excel.py",
            ["--year", str(args.year)],
            f"Generate SHEtoken_WEI_{args.year}.xlsx backup"
        )
        results["data/write_to_excel.py"] = ok

    # ── SUMMARY ───────────────────────────────────────────────────────────────
    print(f"\n\n{'═'*60}")
    print("PIPELINE SUMMARY")
    print(f"{'═'*60}")

    passed = sum(1 for v in results.values() if v)
    total  = len(results)

    for step, ok in results.items():
        status = "✓" if ok else "✗"
        print(f"  {status}  {step}")

    print(f"\n  {passed}/{total} steps completed successfully")

    output_dir = BASE_DIR / "data" / "output"
    if output_dir.exists():
        print(f"\n  Output files:")
        for f in sorted(output_dir.glob("*.csv")):
            size = round(f.stat().st_size / 1024, 1)
            print(f"    {f.name} ({size} KB)")

    print(f"\nFinished: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'═'*60}")

    if passed < total:
        print("\n⚠ Some steps failed. Review output above.")
        print("  To run with fallback estimates: python run_pipeline.py --fallback")
    else:
        print("\n✓ Pipeline completed successfully")
        print(f"  Data ready in: data/output/")


if __name__ == "__main__":
    main()
