"""
SHEtoken Pipeline — Configuration v3
Shared config imported by all data generators.
"""
from pathlib import Path

# All generators run from pipeline/data/
# So __file__ = pipeline/data/config_v3.py
# Output goes to pipeline/data/output/
OUTPUT_DIR    = Path(__file__).parent / "output"
BASELINE_YEAR = 2025

# Ensure output directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
(OUTPUT_DIR / "historical").mkdir(parents=True, exist_ok=True)
