"""
SHEtoken Pipeline — Configuration v3
Shared config imported by all data generators.
"""
from pathlib import Path

# Output directory — relative to this file's location
OUTPUT_DIR   = Path(__file__).parent.parent / "data" / "output"
BASELINE_YEAR = 2025

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "historical").mkdir(parents=True, exist_ok=True)
