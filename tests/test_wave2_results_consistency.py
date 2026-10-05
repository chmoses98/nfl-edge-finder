"""The committed Wave-2 reports must be exactly what their JSON renders, the preregistration must be byte-identical to
the commit that set the PROSPECTIVE CUTOFF, and the committed results must respect the evidence rule: no contaminated
season is called validation, statuses follow the preregistered rule, and nothing claims authority."""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.sim import wave2_render as R  # noqa: E402

W2 = os.path.join(ROOT, "research", "game_script_v2", "wave2")
# sha256 of PREREGISTRATION.md as committed in 0aea50fcd30b4eafc94c1228f716cd77e01f5db9 (the PROSPECTIVE CUTOFF commit)
PREREG_SHA256 = "2d4870e310b3db1ed948de1889579f4cc4b09d05e0350983fd363f4b90ded3e9"
CUTOFF = "2026-10-05T16:14:02+00:00"
STATUSES = {"PROSPECTIVE_CHALLENGER", "REJECTED_AT_DEVELOPMENT", "DIAGNOSTIC_FAIL"}


def _load(name):
    p = os.path.join(W2, name)
    if not os.path.exists(p):
        pytest.skip(f"{name} is not in this checkout")
    return json.load(open(p))


@pytest.mark.parametrize("name", sorted(R.RENDERERS))
def test_the_committed_report_is_exactly_what_its_json_renders(name):
    js = os.path.join(W2, name + ".json")
    if not os.path.exists(js):
        pytest.skip(f"{name}.json is not in this checkout")
    md = os.path.join(W2, name + ".md")
    assert os.path.exists(md), f"{name}.json exists but {name}.md was not rendered"
    assert open(md).read() == R.render_file(js), f"{name}.md disagrees with its JSON: python scripts/sim/wave2_render.py"


def test_the_preregistration_is_unchanged_since_the_cutoff_commit():
    import hashlib
    body = open(os.path.join(W2, "PREREGISTRATION.md"), "rb").read()
    assert hashlib.sha256(body).hexdigest() == PREREG_SHA256, "PREREGISTRATION.md may not be edited; record outputs in the addendum"


def test_the_cutoff_is_the_same_everywhere():
    from nfl_edge.sim import risk1
    assert risk1.PROSPECTIVE_CUTOFF == CUTOFF
    for f in ("PROSPECTIVE_PROTOCOL.md", "PREREGISTRATION_ADDENDUM.md", "README.md"):
        p = os.path.join(W2, f)
        if os.path.exists(p):
            assert "2026-10-05T16:14:02" in open(p).read(), f


@pytest.mark.parametrize("name", ["S1_SHARE_DISPERSION.json", "Q1_QB_EXIT_TAIL.json", "A1_AVAILABILITY_HORIZONS.json", "M1_KEY_NUMBERS.json"])
def test_projection_arms_use_only_development_and_contaminated_evidence(name):
    d = _load(name)
    assert d["status"] in STATUSES
    ev = d["evidence"]
    assert max(ev["development"]) <= 2020
    assert sorted(ev["contaminated_diagnostic"]) == [2021, 2022, 2023, 2024, 2025]
    text = json.dumps(d).lower()
    for word in ("validated", "prospective_evidence", "betting_authority\": \"full"):
        assert word not in text, (name, word)


def test_statuses_follow_the_preregistered_rule():
    for name, crit_keys in (("S1_SHARE_DISPERSION.json", ("section7_chi2_falls_for_at_least_3", "section2_all_five_toward_uniform",
                                                          "crps_of_each_of_the_five_not_worse")),
                            ("Q1_QB_EXIT_TAIL.json", ("section3_lower_decile_moves_toward_0.10_for_all_three",
                                                      "section3_crps_of_the_three_within_0.5pct",
                                                      "section7_regime_frequencies_inside_90pct_predictive_bands"))):
        p = os.path.join(W2, name)
        if not os.path.exists(p):
            continue
        d = json.load(open(p))
        crit = d["development_mechanism_check"]["criteria"]
        dev_ok = all(crit[k] for k in crit_keys)
        if name.startswith("S1"):
            dev_ok = dev_ok and all(f["status"] == "SELECTED" for f in d["selection"].values())
        diag_ok = d["contaminated_diagnostic"]["pooled"]["primary"]["mean"] <= 0
        want = "PROSPECTIVE_CHALLENGER" if dev_ok and diag_ok else ("DIAGNOSTIC_FAIL" if dev_ok else "REJECTED_AT_DEVELOPMENT")
        assert d["status"] == want, name
        if d["status"] == "PROSPECTIVE_CHALLENGER":
            assert d["minimum_prospective_sample"]["n_games"] >= 64


def test_risk1_has_no_result_before_its_minimum_sample():
    d = _load("RISK1_SCRIPT_ROBUSTNESS.json")
    assert d["prospective_cutoff"] == CUTOFF
    assert d["minimum_prospective_sample"]["n_games"] >= 64
    assert d["status"] == "COLLECTING" and d["results"] is None
    assert d["authority"].startswith("NONE")


@pytest.mark.parametrize("doc", ["README.md", "PREREGISTRATION_ADDENDUM.md"])
def test_hand_written_statuses_match_the_json(doc):
    p = os.path.join(W2, doc)
    if not os.path.exists(p):
        pytest.skip(f"{doc} is not in this checkout")
    text = open(p).read()
    for name, arm in (("S1_SHARE_DISPERSION.json", "S1"), ("Q1_QB_EXIT_TAIL.json", "Q1"), ("A1_AVAILABILITY_HORIZONS.json", "A1"),
                      ("M1_KEY_NUMBERS.json", "M1"), ("RISK1_SCRIPT_ROBUSTNESS.json", "RISK1")):
        js = os.path.join(W2, name)
        if os.path.exists(js):
            st = json.load(open(js))["status"]
            assert f"| {arm} | **{st}**" in text, (arm, st)
