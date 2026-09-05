"""H-20260904-019 is preregistered. Its rule must not drift.

The whole value of a preregistered candidate is that nobody -- including us, six sessions later, with 2025
outcomes in view -- can quietly move the buckets, add a subgroup, or relax the sample gate until it looks
better. These tests fail if any of that happens.
"""
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
H = json.load(open(os.path.join(ROOT, "research/hypothesis_registry/H-20260904-019.json")))
TRACKER = open(os.path.join(ROOT, "scripts/shadow/track_h019.py")).read()


def test_hypothesis_still_registered_prospective():
    assert H["status"] == "REGISTERED_PROSPECTIVE"
    assert H["oos_result"] is None, "out-of-sample result recorded; the hypothesis should then be resolved"


def test_preregistered_price_window_is_unchanged():
    assert "0.20" in H["expected_direction"] and "0.50" in H["expected_direction"]
    assert re.search(r"PRIMARY_LO,\s*PRIMARY_HI\s*=\s*0\.20,\s*0\.50", TRACKER), \
        "the tracker's primary window must remain [0.20, 0.50)"


def test_sample_gate_is_unchanged():
    assert "250 games" in H["test_plan"]
    assert re.search(r"MIN_GAMES\s*=\s*250", TRACKER), "the 250-game gate must not be relaxed"


def test_endpoint_is_still_net_return_after_fees():
    assert "net return after fees" in H["test_plan"]
    assert "clustered" in H["test_plan"] and "excluding zero" in H["test_plan"]


def test_the_two_buckets_are_documented_as_one_test():
    assert "ONE test" in H["test_plan"] or "one test" in H["test_plan"], \
        "the mirrored-buckets caveat must survive; they are ~110 games seen from both sides"


def test_tracker_refuses_to_report_before_the_gate():
    assert "MUST NOT be reported" in TRACKER or "forbids reading the result" in TRACKER


def test_no_subgroup_split_was_added():
    for banned in ("home", "away", "conference", "favorite_quality", "team_strength"):
        assert f'"{banned}"' not in TRACKER, f"a {banned} split would violate the preregistration"
