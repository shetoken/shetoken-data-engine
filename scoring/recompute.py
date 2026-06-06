"""
Recompute a SHE Score from a frozen config + an archived pillar-scores input,
so any published score can be reproduced byte-for-byte (Track B5).

Usage:
    python scoring/recompute.py --config v2 --inputs path/to/pillars.json

`pillars.json` is either a single mapping {pillar: subscore, ...}
or a mapping of {iso_code: {pillar: subscore, ...}, ...}.
"""
import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from engine import load_config, score, supply_change, START_SUPPLY  # noqa: E402


def main():
    ap = argparse.ArgumentParser(description="Recompute SHE Score from config + inputs")
    ap.add_argument("--config", default="v2", help="config version name or path (default: v2)")
    ap.add_argument("--inputs", required=True, help="JSON of pillar sub-scores")
    ap.add_argument("--baseline", type=float, default=None,
                    help="optional baseline score to also report supply change")
    args = ap.parse_args()

    cfg = load_config(args.config)
    with open(args.inputs, "r", encoding="utf-8") as f:
        data = json.load(f)

    print(f"# config {cfg['version']} ({cfg['status']}, frozen={cfg.get('frozen')})  start_supply={START_SUPPLY:,}")
    if data and all(isinstance(v, dict) for v in data.values()):
        for iso, ps in data.items():
            r = score(ps, cfg)
            print(iso, r)
    else:
        r = score(data, cfg)
        print(r)
        if args.baseline is not None:
            delta = round(r["raw"] - args.baseline, 6)
            print(f"delta_vs_baseline={delta}  supply_change={supply_change(delta):,} SHE")


if __name__ == "__main__":
    main()
