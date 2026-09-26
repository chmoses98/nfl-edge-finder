"""SNAPSHOT vs PACKET latency: four numbers where there used to be one.

Thursday 2026-09-24 ATL@GB: every RUN NFL horizon read 22-23 minutes "late" while the snapshots were frozen on
time; the T-30m packet reached `latest/` with 7.1 minutes to kickoff. `late_by_min` could not say which part was
the scheduler and which was a twenty-minute pipeline.
"""
import json
import os
import subprocess
import sys
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.handicap.horizons import mark_captured, parse_horizon_id  # noqa: E402
from nfl_edge.handicap.latency import (  # noqa: E402
    context_frozen_at, manifest_latency, publication_latency, snapshot_frozen_at,
)

import horizon_capture_health as HCH  # noqa: E402

UTC = timezone.utc
HID = "2026-REG-03|20260925T0015Z|T-30m"                       # trigger 23:45Z, kickoff 00:15Z
TRIG = datetime(2026, 9, 24, 23, 45, tzinfo=UTC)
KO = datetime(2026, 9, 25, 0, 15, tzinfo=UTC)


def test_the_four_metrics_and_their_identity():
    frz, pub = TRIG + timedelta(minutes=8.7), TRIG + timedelta(minutes=22.9)
    m = publication_latency(trigger_utc=TRIG, kickoff_utc=KO, snapshot_frozen=frz, published_at=pub)
    assert m["snapshot_capture_latency_min"] == 8.7
    assert m["pipeline_processing_min"] == 14.2
    assert m["packet_publish_latency_min"] == 22.9
    assert m["time_remaining_to_kickoff_at_publication_min"] == 7.1
    assert round(m["snapshot_capture_latency_min"] + m["pipeline_processing_min"], 1) == m["packet_publish_latency_min"]


def test_an_unknown_freeze_nulls_only_the_metrics_that_need_it():
    m = publication_latency(trigger_utc=TRIG, kickoff_utc=KO, snapshot_frozen=None,
                            published_at=TRIG + timedelta(minutes=20))
    assert m["snapshot_capture_latency_min"] is None and m["pipeline_processing_min"] is None
    assert m["packet_publish_latency_min"] == 20.0 and m["time_remaining_to_kickoff_at_publication_min"] == 10.0


def test_the_freeze_is_the_later_of_the_market_and_context_vintages():
    early_market = TRIG - timedelta(minutes=5)             # a capture from before the trigger...
    ctx = TRIG + timedelta(minutes=6)
    assert snapshot_frozen_at(early_market.isoformat(), ctx) == ctx   # ...does not make the snapshot "early"
    assert snapshot_frozen_at(None, None) is None
    assert snapshot_frozen_at("20260924T234900Z", None) == datetime(2026, 9, 24, 23, 49, tzinfo=UTC)


def test_the_context_freeze_is_its_last_retrieval_not_its_start(tmp_path):
    p = tmp_path / "20260924T235300Z.manifest.json"
    p.write_text(json.dumps({"run_id": "20260924T235300Z", "sources": {
        "schedule": {"retrieved_at": "2026-09-24T23:53:00+00:00"},
        "espn_injuries": {"retrieved_at": "2026-09-24T23:57:31+00:00"}, "weather_games": 31}}))
    assert context_frozen_at(str(p), "20260924T235300Z") == datetime(2026, 9, 24, 23, 57, 31, tzinfo=UTC)
    assert context_frozen_at(None, "20260924T235300Z") == datetime(2026, 9, 24, 23, 53, tzinfo=UTC)


def test_the_manifest_block_is_labelled_as_measured_at_the_packet_build():
    blk = manifest_latency([parse_horizon_id(HID)], kalshi_queried_at="2026-09-24T23:45:00+00:00",
                           context_frozen=TRIG + timedelta(minutes=8), packet_built_at=TRIG + timedelta(minutes=22))
    assert blk["reporting_only"] is True and "PACKET_BUILD" in blk["publish_side_measured_at"]
    h = blk["horizons"][0]
    assert h["horizon_id"] == HID and h["snapshot_capture_latency_min"] == 8.0 and h["pipeline_processing_min"] == 14.0


def test_a_capture_record_carries_the_split_and_keeps_late_by_min_unchanged():
    pub = TRIG + timedelta(minutes=18)
    state = mark_captured({}, [parse_horizon_id(HID)], now=pub, run_id="1",
                          snapshot_frozen_at=(TRIG + timedelta(minutes=6)).isoformat())
    r = state["captured"][HID]
    assert r["late_by_min"] == r["packet_publish_latency_min"] == 18.0
    assert r["snapshot_capture_latency_min"] == 6.0 and r["pipeline_processing_min"] == 12.0
    assert r["time_remaining_to_kickoff_at_publication_min"] == 12.0 and r["status"] == "CAPTURED"


def test_an_existing_record_is_never_rewritten_by_a_later_split():
    first = mark_captured({}, [parse_horizon_id(HID)], now=TRIG + timedelta(minutes=20))
    again = mark_captured(first, [parse_horizon_id(HID)], now=TRIG + timedelta(minutes=25),
                          snapshot_frozen_at=TRIG.isoformat())
    assert again["captured"][HID] == first["captured"][HID]


def test_mark_horizons_reads_the_freeze_from_the_manifest(tmp_path):
    man = tmp_path / "manifest.json"
    man.write_text(json.dumps({"latency": {"snapshot_frozen_at": (TRIG + timedelta(minutes=7)).isoformat()}}))
    out = tmp_path / "h.json"
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "handicap", "mark_horizons.py"),
                        "--out", str(out), "--horizon-ids", HID, "--run-id", "9", "--manifest", str(man),
                        "--now", (TRIG + timedelta(minutes=19)).isoformat()], capture_output=True, text=True)
    assert r.returncode == 0, r.stderr
    rec = json.load(open(out))["captured"][HID]
    assert rec["snapshot_capture_latency_min"] == 7.0 and rec["pipeline_processing_min"] == 12.0


def test_mark_horizons_still_marks_when_the_manifest_is_unreadable(tmp_path):
    out = tmp_path / "h.json"
    r = subprocess.run([sys.executable, os.path.join(ROOT, "scripts", "handicap", "mark_horizons.py"),
                        "--out", str(out), "--horizon-ids", HID, "--manifest", str(tmp_path / "nope.json"),
                        "--now", (TRIG + timedelta(minutes=19)).isoformat()], capture_output=True, text=True)
    assert r.returncode == 0
    assert json.load(open(out))["captured"][HID]["status"] == "CAPTURED"


def test_capture_health_reports_the_split_and_never_invents_it_for_old_records():
    state = {"captured": {
        HID: {"status": "CAPTURED", "trigger_utc": TRIG.isoformat(), "kickoff_utc": KO.isoformat(),
              "captured_at": (TRIG + timedelta(minutes=22.9)).isoformat(), "late_by_min": 22.9},
        "2026-REG-03|20260927T1700Z|T-1440m": {
            "status": "CAPTURED", "trigger_utc": "2026-09-26T17:00:00+00:00",
            "kickoff_utc": "2026-09-27T17:00:00+00:00", "captured_at": "2026-09-26T17:18:00+00:00",
            "late_by_min": 18.0, "snapshot_capture_latency_min": 6.5, "pipeline_processing_min": 11.5,
            "packet_publish_latency_min": 18.0, "time_remaining_to_kickoff_at_publication_min": 1422.0}}}
    lat = HCH.run_nfl_latency(state)
    old = next(r for r in lat["rows"] if r["horizon_id"] == HID)
    assert old["snapshot_capture_latency_min"] is None and old["packet_publish_latency_min"] == 22.9
    assert old["time_remaining_to_kickoff_at_publication_min"] == 7.1
    doc = {"season": 2026, "as_of": "x", "conductor_deployed_utc": "x", "targets": {}, "run_nfl_latency": lat}
    md = HCH.render(doc)
    assert "snapshot vs packet latency" in md and "| 6.5 | 11.5 | 18.0 | 1422.0 |" in md


def test_the_workflow_hands_the_manifest_to_the_horizon_marker():
    wf = open(os.path.join(ROOT, ".github", "workflows", "run-nfl.yml")).read()
    assert "--manifest data/handicap_report/manifest.json" in wf


def _build_report_module():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_br", os.path.join(ROOT, "scripts", "handicap", "build_report.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_build_report_writes_the_latency_block_from_its_own_vintages(tmp_path):
    import argparse
    br = _build_report_module()
    man = tmp_path / "20260924T235300Z.manifest.json"
    man.write_text(json.dumps({"sources": {"espn_injuries": {"retrieved_at": "2026-09-24T23:53:40+00:00"}}}))
    a = argparse.Namespace(horizon_ids=HID + ",not-an-id", require_context_run_id="20260924T235300Z")
    blk = br._latency_block(a, {"queried_at": "2026-09-24T23:44:00+00:00"}, {"path": str(man)},
                            TRIG + timedelta(minutes=20))
    assert blk["snapshot_frozen_at"] == "2026-09-24T23:53:40+00:00"
    assert [h["horizon_id"] for h in blk["horizons"]] == [HID]
    assert blk["horizons"][0]["snapshot_capture_latency_min"] == 8.7


def test_build_report_latency_can_never_fail_a_build():
    import argparse
    br = _build_report_module()
    blk = br._latency_block(argparse.Namespace(horizon_ids=None, require_context_run_id=None), None, None, "garbage")
    assert blk.get("reporting_only") is True
