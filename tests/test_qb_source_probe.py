"""The QB source probe (REPORT ONLY): it asks public sources whether any field designates a starter and writes nothing.

Extracted unchanged from tests/test_decision_evidence_and_source_probe.py on the postmortem branch (#232) so the probe can be
dispatched from `main` without merging the rest of that PR.
"""
import importlib.util
import json
import os

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def _probe():
    spec = importlib.util.spec_from_file_location("qb_source_probe", os.path.join(ROOT, "scripts", "handicap", "qb_source_probe.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_probe_reports_candidate_paths_and_sets_depth_charts_and_inactives_aside():
    P = _probe()
    payload = {"athletes": [{"depthChart": {"starter": True}, "inactive": True, "name": "x"}],
               "game": {"startingLineup": [{"pos": "QB"}], "probables": []}}
    r = P.analyse("fake", payload, fetched_at="t")
    assert any(p.endswith("startingLineup") for p in r["starter_designation_candidates"])
    assert not any("depthChart" in p for p in r["starter_designation_candidates"])
    assert any("depthChart" in p for p in r["set_aside_paths"])
    assert r["verdict"] == "CANDIDATE_FIELDS_PRESENT_REVIEW_BY_A_HUMAN"


def test_probe_with_no_designation_field_says_so():
    r = _probe().analyse("fake", {"events": [{"id": "1", "name": "A at B"}]}, fetched_at="t")
    assert r["verdict"] == "NO_STARTER_DESIGNATION_FIELD" and r["starter_designation_candidates"] == []


def test_probe_never_raises_on_an_unreachable_source_and_never_writes_confirmations():
    P = _probe()

    def down(url, timeout=30):
        raise OSError("tunnel failed 403")
    rep = P.run(fetcher=down)
    assert rep["writes_confirmations"] is False
    assert all(r["answered"] is False for r in rep["results"])
    assert {r["reason"] for r in rep["results"]} <= {"OSError", "NO_EVENT_ID_FROM_SCOREBOARD"}


def test_probe_output_holds_key_paths_and_counts_only():
    P = _probe()
    secret = "SOME-PLAYER-NAME-OR-TEXT"
    r = P.analyse("fake", {"lineup": {"note": secret}}, fetched_at="t")
    assert secret not in json.dumps(r)
