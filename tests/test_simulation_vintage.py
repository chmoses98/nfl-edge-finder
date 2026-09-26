"""The manifest records how far the attached coherent simulation's market trails the ledger's capture.

Reporting only. At the 2026 week-3 Thursday T-30m horizon the packet paired a 23:45Z ledger with a simulation
whose market was observed at 18:18Z and said nothing about it. These tests pin the record, and pin that it is
informational: it never refuses a build (it has no return path into a gate).
"""
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.report_freshness import SIM_LAG_WARN_MIN, capture_vintage, simulation_vintage  # noqa: E402

NOW = datetime(2026, 9, 25, 0, 6, 33, tzinfo=timezone.utc)
CAP = capture_vintage({"snapshot_run_id": "20260924T234509Z"}, NOW)


def test_thursday_t30_case_is_flagged_as_lagging():
    sim = {"run_id": "20260924T183032Z", "sim_version": "sim-1.1.0",
           "market_observed_at": "2026-09-24T18:18:26.576665+00:00", "generated_at": "2026-09-24T19:07:45+00:00"}
    v = simulation_vintage(sim, CAP, NOW)
    assert v["status"] == "LAGS_LEDGER"
    assert v["run_id"] == "20260924T183032Z"
    assert abs(v["lag_vs_ledger_capture_min"] - 326.7) < 0.1
    assert abs(v["age_min"] - 348.1) < 0.1


def test_aligned_when_within_threshold():
    sim = {"run_id": "20260924T234509Z", "market_observed_at": "2026-09-24T23:45:09+00:00"}
    v = simulation_vintage(sim, CAP, NOW)
    assert v["status"] == "ALIGNED" and v["lag_vs_ledger_capture_min"] == 0.0


def test_threshold_boundary_is_strict():
    from datetime import timedelta
    obs = datetime(2026, 9, 24, 23, 45, 9, tzinfo=timezone.utc) - timedelta(minutes=SIM_LAG_WARN_MIN)
    assert simulation_vintage({"market_observed_at": obs.isoformat()}, CAP, NOW)["status"] == "ALIGNED"
    obs2 = obs - timedelta(minutes=1)
    assert simulation_vintage({"market_observed_at": obs2.isoformat()}, CAP, NOW)["status"] == "LAGS_LEDGER"


def test_missing_and_unknown_are_explicit_not_silent():
    assert simulation_vintage(None, CAP, NOW)["status"] == "MISSING"
    v = simulation_vintage({"run_id": "x"}, CAP, NOW)
    assert v["status"] == "UNKNOWN" and v["age_min"] is None and v["lag_vs_ledger_capture_min"] is None


def test_unknown_capture_gives_age_but_no_lag():
    v = simulation_vintage({"market_observed_at": "2026-09-24T18:18:26+00:00"}, {"queried_at": None}, NOW)
    assert v["lag_vs_ledger_capture_min"] is None and v["age_min"] is not None and v["status"] == "ALIGNED"


def test_build_report_wires_the_vintage_into_the_manifest():
    src = open(os.path.join(ROOT, "scripts", "handicap", "build_report.py")).read()
    assert '"simulation": simulation_vintage(packet["sources"].get("simulation"), cap_vintage, now)' in src
