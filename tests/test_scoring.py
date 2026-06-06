"""
Regression lock for the published v2 SHE Score (Track B3).

These tests MUST stay green. If a change makes any of them fail, the published
methodology has been altered — stop and report; do not "fix" by editing config.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "scoring"))
from engine import load_config, score, supply_change  # noqa: E402

V2 = load_config("v2")
V3 = load_config("v3")

# The published West Bengal worked example.
WEST_BENGAL = {
    "empowerment": 52,
    "education_literacy": 67,
    "economic_inclusion": 52,
    "health_survival": 71,
    "safety_crime_penalty": 42,
}


def test_v2_is_official_and_frozen():
    assert V2["version"] == "v2"
    assert V2["status"] == "official"
    assert V2["frozen"] is True


def test_west_bengal_v2_equals_39_1():
    r = score(WEST_BENGAL, V2)
    assert abs(r["raw"] - 39.05) < 1e-9, r            # 39.05 pre-rounding
    assert r["score"] == 39.1, r                       # rounded half-up


def test_kanyashree_scenario():
    base = score(WEST_BENGAL, V2)
    kanyashree = dict(WEST_BENGAL, education_literacy=76)   # 67 -> 76
    r = score(kanyashree, V2)
    assert r["score"] == 40.9, r
    delta = round(r["raw"] - base["raw"], 6)
    assert delta == 1.8, delta
    assert supply_change(delta) == 18_000_000, supply_change(delta)


def test_v2_weights_sum_to_one_including_penalty():
    # 0.25 + 0.20 + 0.20 + 0.15 + 0.20(penalty magnitude) = 1.00
    total = sum(abs(p["weight"]) for p in V2["pillars"].values())
    assert abs(total - 1.0) < 1e-9, total


def test_official_config_rejects_missing_pillar():
    bad = dict(WEST_BENGAL)
    del bad["health_survival"]
    try:
        score(bad, V2)
        assert False, "official config must reject missing pillar"
    except ValueError:
        pass


def test_v3_is_shadow_and_skips_provisional():
    assert V3["status"] == "shadow"
    assert V3["frozen"] is False
    r = score(WEST_BENGAL, V3)
    # only the 5 LIVE pillars carry weights today; the 4 provisional ones are excluded
    assert r["coverage"]["weighted"] == 5, r
    # v3 REWEIGHTS the 5 live pillars (heavier Economic + Crime penalty, lighter
    # Empowerment + Education), so it diverges from v2's 39.1:
    #   52*0.20 + 67*0.15 + 52*0.25 + 71*0.15 - 42*0.25 = 33.6
    assert abs(r["raw"] - 33.6) < 1e-9, r
    assert r["score"] == 33.6, r


def test_v3_reweight_is_stricter_than_v2():
    # The shadow reweight is a stricter lens: West Bengal falls vs the official v2.
    v2r = score(WEST_BENGAL, V2)
    v3r = score(WEST_BENGAL, V3)
    assert v3r["score"] < v2r["score"], (v3r, v2r)


def test_v3_weights_sum_to_one_including_penalty():
    total = sum(abs(p["weight"]) for p in V3["pillars"].values() if p.get("weight") is not None)
    assert abs(total - 1.0) < 1e-9, total


def test_v3_records_insufficient_coverage_never_imputes():
    # drop one LIVE pillar input -> shadow records it as missing, does not impute
    partial = dict(WEST_BENGAL)
    del partial["economic_inclusion"]
    r = score(partial, V3)
    assert "economic_inclusion" in r["coverage"]["missing"], r
    assert r["coverage"]["used"] == 4, r
