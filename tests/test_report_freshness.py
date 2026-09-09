"""A report that is stale must fail, not merely be labelled. Both ways past the ledger-age gate.

The build already refused a stale LEDGER. That left two doors open, and both of them produce a report that
looks current:

* **A fresh ledger is not a fresh market.** `price_slate.py` prices the newest Kalshi capture it can find.
  A ledger written sixty seconds ago from a capture taken ninety minutes ago has a flawless `written_at`.
  The gate therefore reads `snapshot_run_id` -- the capture manifest's `finished_at`, i.e. when Kalshi was
  last successfully QUERIED. Deliberately not `minutes_since_price_change`, which is the time since a price
  last MOVED and is a microstructure signal, not staleness.

* **A failed context capture was survivable.** `force_fresh` ran the capture with `continue-on-error`, so a
  dead ESPN or NWS meant falling back to older published context, building successfully, replacing
  `latest/` and marking a decision horizon captured. At T-30m that is the difference between having the
  inactive release and silently predating it.

The context proof honours change-suppression: `context_capture.py` always writes `<run_id>.manifest.json`
and writes the ESPN/Sleeper blobs only when their content hash changed. So the proof is that this run's
manifest exists, nothing failed closed, and the packet actually read that capture -- never a timestamp
invented for somebody else's file.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.handicap.report_freshness import (  # noqa: E402
    DEFAULT_MAX_CAPTURE_AGE_MIN, capture_vintage, check_capture_age, check_context_reached_packet,
    check_fresh_context, find_context_run,
)

NOW = datetime(2026, 9, 9, 12, 0, tzinfo=timezone.utc)


def ledger(snapshot="20260909T115000Z", written="2026-09-09T11:59:30+00:00"):
    return {"run_id": "20260909T115930Z", "written_at": written, "snapshot_run_id": snapshot}


# ------------------------------------------------------------------ Kalshi capture age

def test_the_gated_vintage_is_when_kalshi_was_queried_not_when_the_ledger_was_written():
    v = capture_vintage(ledger(), NOW)
    assert v["snapshot_run_id"] == "20260909T115000Z"
    assert v["queried_at"] == "2026-09-09T11:50:00+00:00"
    assert v["age_min"] == 10.0
    assert "finished_at" in v["basis"] and "price last moved" in v["basis"]


def test_a_fresh_ledger_priced_from_a_stale_capture_is_refused():
    """The whole point: `written_at` is 30 seconds old and the market is 90 minutes old."""
    v = capture_vintage(ledger(snapshot="20260909T103000Z"), NOW)
    assert v["age_min"] == 90.0
    problem = check_capture_age(v, 30)
    assert problem and "90m ago" in problem
    assert "the ledger is fresh but the market it quotes is not" in problem


def test_a_fresh_capture_passes():
    assert check_capture_age(capture_vintage(ledger(), NOW), 30) is None


@pytest.mark.parametrize("age_min,limit,refused", [(29.9, 30, False), (30.0, 30, False), (30.1, 30, True)])
def test_the_boundary_is_the_limit_itself(age_min, limit, refused):
    stamp = (NOW - timedelta(minutes=age_min)).strftime("%Y%m%dT%H%M%SZ")
    v = capture_vintage(ledger(snapshot=stamp), NOW)
    assert (check_capture_age(v, limit) is not None) == refused


def test_an_unknown_capture_vintage_is_a_refusal_not_a_pass():
    """"I could not check" must never resolve to "it is fine"."""
    problem = check_capture_age(capture_vintage({}, NOW), 30)
    assert problem and "cannot be established" in problem


def test_no_limit_means_no_gate():
    assert check_capture_age(capture_vintage(ledger(snapshot="20200101T000000Z"), NOW), None) is None


def test_the_default_policy_is_three_missed_capture_passes():
    assert DEFAULT_MAX_CAPTURE_AGE_MIN == 30.0


# ------------------------------------------------------------------ fresh context proof

def context_capture(tmp_path, run_id, *, failed_closed=(), day="2026-09-09", espn=True):
    d = tmp_path / "data" / "context" / day
    d.mkdir(parents=True, exist_ok=True)
    json.dump({"run_id": run_id, "sources": {"schedule": {}, "espn_injuries": {}},
               "failed_closed": list(failed_closed)},
              open(d / f"{run_id}.manifest.json", "w"))
    if espn:
        json.dump({"run_id": run_id, "injuries": []}, open(d / f"{run_id}.espn_injuries.json", "w"))
    return str(tmp_path)


def test_a_capture_that_never_wrote_a_manifest_fails_the_run(tmp_path):
    md = context_capture(tmp_path, "20260909T115500Z")
    problem = check_fresh_context(md, "20260909T115900Z")
    assert problem and "wrote no manifest" in problem


def test_a_capture_that_failed_closed_fails_the_run(tmp_path):
    md = context_capture(tmp_path, "20260909T115500Z", failed_closed=["espn injuries unavailable"])
    problem = check_fresh_context(md, "20260909T115500Z")
    assert problem and "failed closed" in problem
    assert "espn injuries unavailable" in problem


def test_a_change_suppressed_capture_still_counts_as_fresh(tmp_path):
    """The capture writes no ESPN blob when the content hash is unchanged. That is the architecture, not a
    failure: the manifest is the marker, and re-confirmed identical content is current content."""
    md = context_capture(tmp_path, "20260909T115500Z", espn=False)
    assert check_fresh_context(md, "20260909T115500Z") is None


def test_a_good_capture_passes(tmp_path):
    md = context_capture(tmp_path, "20260909T115500Z")
    assert check_fresh_context(md, "20260909T115500Z") is None
    rec = find_context_run(md, "20260909T115500Z")
    assert rec["found"] and rec["failed_closed"] == []


def test_an_old_required_capture_can_be_age_limited_too(tmp_path):
    md = context_capture(tmp_path, "20260909T090000Z", day="2026-09-09")
    assert check_fresh_context(md, "20260909T090000Z", now=NOW, max_age_min=30) is not None
    assert check_fresh_context(md, "20260909T090000Z", now=NOW, max_age_min=1000) is None


def test_the_packet_must_actually_have_read_the_fresh_capture():
    """Present on disk is not the same as used. If the packet read the two previous captures, the report
    carries older context while claiming to be fresh."""
    problem = check_context_reached_packet(
        "20260909T115500Z", {"context_captures": ["20260908T232623Z", "20260909T045003Z"]})
    assert problem and "does not include this run's fresh capture" in problem


def test_the_proof_passes_when_the_packet_read_it():
    assert check_context_reached_packet(
        "20260909T115500Z", {"context_captures": ["20260909T045003Z", "20260909T115500Z"]}) is None


def test_no_requirement_means_no_proof_demanded():
    assert check_context_reached_packet(None, {"context_captures": []}) is None
