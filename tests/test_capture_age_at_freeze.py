"""The Kalshi capture-age gate measures the market the packet froze, not how long our own build took.

Readiness audit 2026-09-26: run-nfl.yml fetched market-data at the start of the job and checked the capture's
age ~18-20 minutes later against a 30-minute limit. Captures land every ~15.5 minutes (+~2 to publish), so the
age at the check ranged ~20-36 minutes; the Saturday T-24h builds passed at 22.0 and 26.5. A capture that landed
exactly on schedule could be refused, and a refused T-30m horizon has no time left to retry -- MISSED.

The fix has two halves, both pinned here:

* the workflow refreshes market-data IMMEDIATELY before pricing and records that instant as the freeze;
* the gate measures the capture at that freeze, records the build-time age beside it, and falls back to the
  stricter build-time reading whenever the reference is doubtful.

The limit itself (30 minutes) is unchanged.
"""
import gzip
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.report_freshness import (  # noqa: E402
    MAX_FREEZE_REFERENCE_AGE_MIN, capture_vintage, check_capture_age,
)

NOW = datetime(2026, 9, 27, 16, 45, tzinfo=timezone.utc)
BUILD = os.path.join(ROOT, "scripts", "handicap", "build_report.py")


def ledger(snapshot):
    return {"run_id": "x", "snapshot_run_id": snapshot.strftime("%Y%m%dT%H%M%SZ")}


# ------------------------------------------------------------------ unit: what the gate measures

def test_a_capture_that_was_fresh_at_the_freeze_passes_even_though_the_build_took_eleven_minutes():
    snap, freeze = NOW - timedelta(minutes=33), NOW - timedelta(minutes=11)
    v = capture_vintage(ledger(snap), NOW, reference=freeze)
    assert v["age_min"] == 33.0                       # build-time age: still recorded, unchanged meaning
    assert v["age_at_freeze_min"] == 22.0
    assert v["gate_age_min"] == 22.0 and v["age_reference"] == "PRICING_INPUT_FREEZE"
    assert v["age_reference_at"] == freeze.isoformat()
    assert check_capture_age(v, 30) is None


def test_a_capture_that_was_already_stale_at_the_freeze_is_still_refused():
    v = capture_vintage(ledger(NOW - timedelta(minutes=50)), NOW, reference=NOW - timedelta(minutes=11))
    problem = check_capture_age(v, 30)
    assert problem and "39m before this build froze its pricing inputs" in problem
    assert "the ledger is fresh but the market it quotes is not" in problem


def test_without_a_reference_the_gate_is_exactly_the_build_time_gate():
    v = capture_vintage(ledger(NOW - timedelta(minutes=31)), NOW)
    assert v["age_reference"] == "BUILD_TIME" and v["gate_age_min"] == v["age_min"] == 31.0
    assert check_capture_age(v, 30)
    assert check_capture_age(capture_vintage(ledger(NOW - timedelta(minutes=29)), NOW), 30) is None


def _falls_back(reference, snap_age=33.0):
    v = capture_vintage(ledger(NOW - timedelta(minutes=snap_age)), NOW, reference=reference)
    assert v["age_reference"] == "BUILD_TIME" and v["gate_age_min"] == snap_age
    assert v.get("age_reference_rejected")
    return v


def test_a_reference_in_the_future_is_ignored_and_the_stricter_build_time_age_is_gated():
    assert check_capture_age(_falls_back(NOW + timedelta(minutes=5)), 30)


def test_a_reference_older_than_any_plausible_freeze_is_ignored():
    _falls_back(NOW - timedelta(minutes=MAX_FREEZE_REFERENCE_AGE_MIN + 1))


def test_a_reference_before_the_capture_itself_cannot_be_this_builds_freeze():
    _falls_back(NOW - timedelta(minutes=40), snap_age=33.0)


def test_an_unknown_capture_is_still_a_refusal_with_a_reference():
    v = capture_vintage({}, NOW, reference=NOW - timedelta(minutes=5))
    assert check_capture_age(v, 30) and "cannot be established" in check_capture_age(v, 30)


# ------------------------------------------------------------------ end to end through build_report.py

def _md(tmp_path, snap):
    md = tmp_path / "md"
    day = md / "data" / "shadow" / "ledger" / "2026-09-09"
    day.mkdir(parents=True)
    stem = day / "20260909T000000Z.shadow-0.4.0"
    with gzip.open(str(stem) + ".observations.jsonl.gz", "wt") as f:
        pass                                           # no rows: the gate after the capture gate stops it (4)
    json.dump({"run_id": "20260909T000000Z", "model_version": "shadow-0.4.0",
               "written_at": datetime.now(timezone.utc).isoformat(),
               "snapshot_run_id": snap.strftime("%Y%m%dT%H%M%SZ")}, open(str(stem) + ".ledger_manifest.json", "w"))
    return str(md)


def _build(md, tmp_path, extra):
    return subprocess.run([sys.executable, BUILD, "--market-data", md, "--out", str(tmp_path / "out"),
                           "--season", "2026", "--week", "1", "--max-capture-age-min", "30", *extra],
                          cwd=ROOT, text=True, capture_output=True)


def test_build_report_gates_at_the_freeze_when_told_and_at_build_time_when_not(tmp_path):
    now = datetime.now(timezone.utc)
    md = _md(tmp_path, now - timedelta(minutes=34))
    freeze = (now - timedelta(minutes=12)).strftime("%Y-%m-%dT%H:%M:%SZ")
    refused = _build(md, tmp_path, [])
    assert refused.returncode == 9, refused.stderr
    passed = _build(md, tmp_path, ["--capture-age-reference", freeze])
    assert passed.returncode == 4, passed.stderr      # past the capture gate; stopped by "no rows" instead
    assert "PRICING_INPUT_FREEZE" in passed.stdout


def test_build_report_ignores_an_unreadable_reference_and_stays_strict(tmp_path):
    now = datetime.now(timezone.utc)
    md = _md(tmp_path, now - timedelta(minutes=34))
    r = _build(md, tmp_path, ["--capture-age-reference", "not-a-time"])
    assert r.returncode == 9, r.stderr


# ------------------------------------------------------------------ the workflow wiring

def _steps():
    wf = yaml.safe_load(open(os.path.join(ROOT, ".github", "workflows", "run-nfl.yml")))
    return wf["jobs"]["report"]["steps"]


def test_market_data_is_refreshed_immediately_before_pricing_and_the_instant_is_recorded():
    steps = _steps()
    idx = {s.get("name"): i for i, s in enumerate(steps)}
    freeze = next(s for s in steps if s.get("id") == "freeze")
    ctx = next(i for i, s in enumerate(steps) if "context_capture.py" in (s.get("run") or ""))
    price = next(i for i, s in enumerate(steps) if "price_slate.py" in (s.get("run") or ""))
    assert ctx < idx[freeze["name"]] < price, "the refresh must sit between the context capture and pricing"
    assert "inputs.force_fresh" in freeze["if"]
    assert "git fetch --depth=1 origin market-data" in freeze["run"]
    assert "checkout -q --detach origin/market-data" in freeze["run"]
    assert "frozen_at=" in freeze["run"]


def test_a_failed_refresh_degrades_to_the_tree_fetched_at_the_start_rather_than_failing_the_build():
    freeze = next(s for s in _steps() if s.get("id") == "freeze")
    assert freeze.get("continue-on-error") is not True   # it cannot fail: the refresh is inside an if/else
    assert "if git fetch" in freeze["run"] and "::warning::could not refresh market-data" in freeze["run"]


def test_the_build_gates_the_capture_at_the_freeze_and_the_limit_is_unchanged():
    build = next(s for s in _steps() if "build_report.py" in (s.get("run") or ""))
    assert "--max-capture-age-min 30" in build["run"]
    assert "--capture-age-reference ${{ steps.freeze.outputs.frozen_at }}" in build["run"]
