"""Simulation freshness at decision horizons: eligible selection by INFORMATION time, a real freshness gate, and
a frozen-bundle local run inside RUN NFL. Publication time is never evidence of information time."""
from __future__ import annotations

import gzip
import json
import os
from datetime import datetime, timedelta, timezone

import pytest
import yaml

from nfl_edge.handicap import sim_block as SB

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
UTC = timezone.utc


def _t(s):
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def write_sim(root, stamp, cutoff, observed, origin=None, tickers=("T1",)):
    day = f"{stamp[:4]}-{stamp[4:6]}-{stamp[6:8]}"
    d = os.path.join(root, "data", "shadow", "sim", day)
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{stamp}.sim-1.1.0.projections.jsonl.gz")
    with gzip.open(p, "wt") as f:
        for t in tickers:
            f.write(json.dumps({"ticker": t, "run_id": stamp, "support_state": "PRICED"}) + "\n")
    man = {"run_id": stamp, "sim_version": "sim-1.1.0", "market_observed_at": observed}
    if cutoff is not None:
        man["cutoff"] = cutoff
    if origin:
        man["origin"] = origin
    json.dump(man, open(p.replace(".projections.jsonl.gz", ".manifest.json"), "w"))
    return p


FREEZE = _t("2026-09-27T16:38:00Z")        # a T-30 freeze for the 17:00 cluster
LEDGER = "20260927T163300Z"                # the board the packet prices


def test_newest_eligible_run_is_selected(tmp_path):
    write_sim(tmp_path, "20260927T120000Z", "2026-09-27T12:40:00Z", "2026-09-27T11:55:00Z")
    write_sim(tmp_path, "20260927T150000Z", "2026-09-27T15:40:00Z", "2026-09-27T14:55:00Z")
    rows, man, rec = SB.select_eligible([str(tmp_path)], market_stamp=LEDGER, info_cutoff=FREEZE)
    assert rec["selected"] == "20260927T150000Z" and rows and man["run_id"] == "20260927T150000Z"


def test_a_run_that_saw_a_later_market_is_refused(tmp_path):
    write_sim(tmp_path, "20260927T150000Z", "2026-09-27T15:40:00Z", "2026-09-27T14:55:00Z")
    write_sim(tmp_path, "20260927T164500Z", "2026-09-27T16:37:00Z", "2026-09-27T16:44:00Z")
    _, _, rec = SB.select_eligible([str(tmp_path)], market_stamp=LEDGER, info_cutoff=FREEZE)
    assert rec["selected"] == "20260927T150000Z" and rec["refused"]["MARKET_AFTER_LEDGER"] == 1


def test_a_newer_publication_with_inputs_after_the_freeze_is_refused(tmp_path):
    """The TNF/Sunday hazard: a shadow-cycle run of the SAME board whose inputs were resolved ~40 minutes later
    (its cutoff is 'now' at sim time). Its stamp passes; its inputs do not."""
    write_sim(tmp_path, "20260927T150000Z", "2026-09-27T15:40:00Z", "2026-09-27T14:55:00Z")
    write_sim(tmp_path, LEDGER, "2026-09-27T17:12:00Z", "2026-09-27T16:30:00Z")
    _, _, rec = SB.select_eligible([str(tmp_path)], market_stamp=LEDGER, info_cutoff=FREEZE)
    assert rec["selected"] == "20260927T150000Z" and rec["refused"]["INPUTS_AFTER_CUTOFF"] == 1


def test_a_run_with_no_provable_cutoff_is_refused(tmp_path):
    write_sim(tmp_path, "20260927T150000Z", None, "2026-09-27T14:55:00Z")
    rows, man, rec = SB.select_eligible([str(tmp_path)], market_stamp=LEDGER, info_cutoff=FREEZE)
    assert rows is None and man is None and rec["refused"]["NO_PROVABLE_CUTOFF"] == 1


def test_same_board_prefers_the_frozen_bundle_run_deterministically(tmp_path):
    md, repo = tmp_path / "md", tmp_path / "repo"
    write_sim(md, LEDGER, "2026-09-27T16:10:00Z", "2026-09-27T16:30:00Z")               # earlier-cutoff copy
    write_sim(repo, LEDGER, FREEZE.isoformat(), "2026-09-27T16:30:00Z", origin="RUN_NFL_FROZEN_BUNDLE")
    for roots in ([str(md), str(repo)], [str(repo), str(md)]):
        _, man, rec = SB.select_eligible(roots, market_stamp=LEDGER, info_cutoff=FREEZE)
        assert man["origin"] == "RUN_NFL_FROZEN_BUNDLE" and rec["selected_origin"] == "RUN_NFL_FROZEN_BUNDLE"


def test_cutoff_equal_to_the_freeze_is_admissible(tmp_path):
    write_sim(tmp_path, LEDGER, FREEZE.isoformat(), "2026-09-27T16:30:00Z")
    _, man, _ = SB.select_eligible([str(tmp_path)], market_stamp=LEDGER, info_cutoff=FREEZE)
    assert man is not None


@pytest.mark.parametrize("horizons,target", [([30], 20.0), ([90], 45.0), ([360], 90.0), ([1440], 180.0),
                                             ([1440, 30], 20.0), ([], 180.0)])
def test_lag_targets_per_horizon(horizons, target):
    assert SB.lag_target_for(horizons) == target


@pytest.mark.parametrize("sim_obs,target,state", [
    ("2026-09-27T16:30:00Z", 20.0, "SIM_CURRENT"),
    ("2026-09-27T16:15:00Z", 20.0, "SIM_ACCEPTABLE"),
    ("2026-09-27T16:05:00Z", 20.0, "SIM_STALE"),
    ("2026-09-27T16:05:00Z", 45.0, "SIM_ACCEPTABLE"),
    ("2026-09-26T21:06:00Z", 90.0, "SIM_UNUSABLE"),
])
def test_freshness_states(sim_obs, target, state):
    f = SB.freshness({"run_id": "x", "market_observed_at": sim_obs}, board_observed_at=_t("2026-09-27T16:30:00Z"),
                     target_min=target)
    assert f["state"] == state
    assert f["usable_as_current"] is (state in ("SIM_CURRENT", "SIM_ACCEPTABLE"))


def test_missing_and_unmeasurable():
    assert SB.freshness(None, board_observed_at=FREEZE, target_min=20)["state"] == "SIM_MISSING"
    f = SB.freshness({"run_id": "x"}, board_observed_at=FREEZE, target_min=20)
    assert f["state"] == "SIM_UNUSABLE" and f["usable_as_current"] is False


def test_tnf_t30_would_have_been_stale():
    """TNF T-30: the attached run's market was 327 minutes behind the board."""
    board = _t("2026-09-24T23:45:09Z")
    f = SB.freshness({"run_id": "20260924T183032Z", "market_observed_at": (board - timedelta(minutes=327)).isoformat()},
                     board_observed_at=board, target_min=SB.lag_target_for([30]))
    assert f["state"] == "SIM_STALE"


# ------------------------------------------------------------------ rendering: stale never reads as current

def test_stale_simulation_is_labelled_on_the_game_section():
    from nfl_edge.handicap.render import _sim_projection_section
    sv = {"run_id": "r", "player_projections": [], "coverage": {},
          "freshness": {"state": "SIM_STALE", "lag_min": 200.0, "target_lag_min": 20.0, "reason": "x"}}
    md = "\n".join(_sim_projection_section(sv, compact=False, max_rows=10))
    assert "SIM_STALE — THIS SIMULATION IS NOT CURRENT" in md
    assert "This is the current projection system" not in md


def test_current_simulation_keeps_its_label():
    from nfl_edge.handicap.render import _sim_projection_section
    sv = {"run_id": "r", "player_projections": [], "coverage": {},
          "freshness": {"state": "SIM_CURRENT", "lag_min": 0.0, "target_lag_min": 20.0, "reason": "x"}}
    md = "\n".join(_sim_projection_section(sv, compact=False, max_rows=10))
    assert "This is the current projection system" in md and "NOT CURRENT" not in md


# ------------------------------------------------------------------ build_report and the workflow

def test_build_report_derives_the_tightest_horizon_target():
    import importlib.util
    spec = importlib.util.spec_from_file_location("br", os.path.join(ROOT, "scripts", "handicap", "build_report.py"))
    br = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(br)
    assert br._sim_target("2026-REG-03|20260927T1700Z|T-30m") == 20.0
    assert br._sim_target("2026-REG-03|20260927T2005Z|T-360m,2026-REG-03|20260928T0020Z|T-1440m") == 90.0
    assert br._sim_target("") == 180.0


def _steps():
    wf = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "run-nfl.yml")))
    job = next(iter(wf["jobs"].values())) if "report" not in wf["jobs"] else wf["jobs"]["report"]
    return job["steps"]


def test_frozen_bundle_simulation_step_is_point_in_time_and_unpublished():
    steps = _steps()
    names = [s.get("name") for s in steps]
    i_sim = names.index("Fresh LOCAL coherent simulation from the frozen bundle")
    i_freeze = names.index("Refresh market-data and freeze the pricing inputs")
    i_price = names.index("Fresh LOCAL shadow-pricing snapshot")
    i_build = names.index("Build the handicap packet")
    assert i_freeze < i_price < i_sim < i_build
    s = steps[i_sim]
    run = s["run"]
    assert "--cutoff '${{ steps.freeze.outputs.frozen_at }}'" in run
    assert "--origin RUN_NFL_FROZEN_BUNDLE" in run and "--out ." in run
    assert s["env"]["PYTHONHASHSEED"] == "0"
    assert s.get("continue-on-error") is True
    # never published: nothing in RUN NFL publishes data/shadow/sim
    for st in steps:
        assert "publish_market_data.py --src data/shadow/sim" not in (st.get("run") or "")


def test_build_passes_initial_sim_and_freeze():
    b = next(s for s in _steps() if s.get("name") == "Build the handicap packet")["run"]
    assert "--initial-sim-run-id" in b and "--capture-age-reference" in b
