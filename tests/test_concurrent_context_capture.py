"""The fresh context capture runs concurrently with the market-data fetch WITHOUT changing what it captures.

Profiled on week-3 horizon builds 36257597988 / 36268362044: the capture (~4.5-5.8 min) waited for the ~5 minute
market-data fetch though its only market-data input is data/context/state.json. The concurrent path must be
output-equivalent to the sequential one or fall back to it:

  * same input  -> the state.json it was given equals the fetched tree's, or the workflow reruns sequentially;
  * same failure semantics -> the capture's own nonzero exit still fails the run;
  * never started / hung -> sequential rerun (the old behaviour), never a silent pass.
"""
import json
import os
import subprocess
import sys
import time

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

import concurrent_context as CC  # noqa: E402


def _state(path, doc):
    with open(path, "w") as f:
        json.dump(doc, f)
    return str(path)


def _wait(d, tree, used, timeout_s=30):
    return CC.wait(str(d), tree_state=tree, used_state=used, timeout_s=timeout_s, poll_s=0.05)


def test_a_finished_capture_with_the_same_state_is_accepted(tmp_path):
    out = tmp_path / "out.txt"
    CC.start(str(tmp_path / "ctx"), ["bash", "-c", f"echo captured > {out}"])
    used = _state(tmp_path / "used.json", {"sleeper_sha1": "a", "espn_sha1": "b"})
    tree = _state(tmp_path / "tree.json", {"espn_sha1": "b", "sleeper_sha1": "a"})
    assert _wait(tmp_path / "ctx", tree, used) == 0
    assert out.read_text().strip() == "captured"


def test_a_state_the_tree_does_not_hold_forces_the_sequential_rerun(tmp_path):
    CC.start(str(tmp_path / "ctx"), ["true"])
    used = _state(tmp_path / "used.json", {"sleeper_sha1": "OLD"})
    tree = _state(tmp_path / "tree.json", {"sleeper_sha1": "NEW"})
    assert _wait(tmp_path / "ctx", tree, used) == CC.STATE_MISMATCH


def test_an_absent_state_on_both_sides_is_the_same_input(tmp_path):
    """The sequential step falls back to '{}' when the tree has no state.json; so does the prefetch."""
    CC.start(str(tmp_path / "ctx"), ["true"])
    used = _state(tmp_path / "used.json", {})
    assert _wait(tmp_path / "ctx", str(tmp_path / "missing.json"), used) == 0


def test_an_unreadable_state_is_never_equal(tmp_path):
    CC.start(str(tmp_path / "ctx"), ["true"])
    bad = tmp_path / "used.json"
    bad.write_text("{not json")
    assert _wait(tmp_path / "ctx", str(tmp_path / "missing.json"), str(bad)) == CC.STATE_MISMATCH


def test_a_capture_that_failed_closed_still_fails_with_its_own_exit_code(tmp_path):
    CC.start(str(tmp_path / "ctx"), ["bash", "-c", "exit 2"])
    used = _state(tmp_path / "used.json", {})
    assert _wait(tmp_path / "ctx", str(tmp_path / "missing.json"), used) == 2


def test_a_capture_that_never_started_falls_back_to_the_sequential_path(tmp_path):
    (tmp_path / "ctx").mkdir()
    assert _wait(tmp_path / "ctx", None, None) == CC.NOT_STARTED


def test_a_hung_capture_is_killed_and_falls_back_to_the_sequential_path(tmp_path):
    CC.start(str(tmp_path / "ctx"), ["sleep", "30"])
    t0 = time.time()
    assert _wait(tmp_path / "ctx", None, None, timeout_s=0.5) == CC.NOT_STARTED
    assert time.time() - t0 < 10
    pid = int((tmp_path / "ctx" / "pid").read_text())
    time.sleep(0.3)
    gone = subprocess.run(["bash", "-c", f"kill -0 {pid} 2>/dev/null"]).returncode != 0
    assert gone, "the hung capture was left running"


def test_the_default_command_is_the_canonical_capture_script():
    assert CC.CAPTURE.endswith(os.path.join("scripts", "data", "context_capture.py"))
    assert os.path.exists(CC.CAPTURE)


# ------------------------------------------------------------------ workflow wiring

def _steps():
    wf = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "run-nfl.yml")))
    return wf["jobs"]["report"]["steps"]


def test_the_capture_starts_before_the_market_data_fetch_and_cannot_fail_the_run():
    steps = _steps()
    start = next(i for i, s in enumerate(steps) if "concurrent_context.py start" in (s.get("run") or ""))
    fetch = next(i for i, s in enumerate(steps) if "origin market-data" in (s.get("run") or "")
                 and "worktree add" in (s.get("run") or ""))
    assert start < fetch
    assert steps[start].get("continue-on-error") is True
    assert "inputs.force_fresh" in steps[start]["if"]
    assert "state.used.json" in steps[start]["run"]


def test_the_context_step_waits_verifies_and_otherwise_reruns_sequentially():
    ctx = next(s for s in _steps() if "context_capture.py" in (s.get("run") or "")
               and "concurrent_context.py wait" in (s.get("run") or ""))
    run = ctx["run"]
    assert ctx.get("continue-on-error") is not True
    assert '--tree-state /tmp/md/data/context/state.json' in run
    assert '[ "$BG" -eq 3 ] || [ "$BG" -eq 4 ]' in run and "python3 scripts/data/context_capture.py" in run
    assert 'exit "$BG"' in run, "a failed capture must still fail the run"
    assert "context_run_id=" in run
