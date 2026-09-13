"""One build serves every due horizon, and each record takes the horizon of ITS OWN kickoff cluster.

The gate can return several due horizon ids at once. They are ids for different KICKOFF CLUSTERS
(`<slate>|<cluster>|T-<n>m`), not several freezes of one game. The horizons workflow used to loop them --
one projector process per id -- and each process stamped its single id onto every record on the board. That
was wrong twice:

  * a DAL@NYG contract kicking off at 00:20Z was labelled with the 17:00Z cluster's trigger, 678 minutes
    "late" against a horizon that was never its own;
  * the second process then met the first one's rows under the same `record_id` -- which is
    sha1(snapshot|ticker|arm|engine|distribution), with no horizon in it -- and the append-only store
    correctly refused to rewrite them. Exit 4, nothing published, three valid horizons lost.

The store was right. These tests pin the orchestration: one build, per-cluster labels, markers only for
horizons that actually reached accepted rows, and the immutability guard still refusing a real mutation.
"""
import os
from datetime import datetime, timedelta, timezone

import pytest

from nfl_edge.projection import horizons as HZ, record as R
from nfl_edge.projection.store import ProjectionConflict, ProjectionStore, read_rows

SNAP = "20260913T041754Z"
OBS = datetime(2026, 9, 13, 4, 17, 54, tzinfo=timezone.utc)
SLATE = "2026-REG-01"
# three clusters, exactly the shape the live gate returned
KO = {"1700": datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc),
      "2025": datetime(2026, 9, 13, 20, 25, tzinfo=timezone.utc),
      "0020": datetime(2026, 9, 14, 0, 20, tzinfo=timezone.utc)}
HID = {"1700": f"{SLATE}|20260913T1700Z|T-1440m",
       "2025": f"{SLATE}|20260913T2025Z|T-1440m",
       "0020": f"{SLATE}|20260914T0020Z|T-1440m"}
TICKER = {"1700": "CHICAR-TKR", "2025": "GBMIN-TKR", "0020": "DALNYG-TKR"}


def _row(ticker, kickoff, horizon_id, *, snapshot=SNAP, p_yes=0.55):
    """One record as the projector builds it, labelled for exactly one horizon."""
    base = {"snapshot_id": snapshot, "ticker": ticker, "model_arm": "BOARD_V2",
            "engine_version": "e1", "distribution_version": "d1",
            "kickoff_utc": kickoff.isoformat(), "observed_at": OBS.isoformat(), "p_yes": p_yes,
            "information_sync": {"synchronization_state": "SYNCHRONIZED",
                                 "market_observed_at": OBS.isoformat()}}
    base.update(HZ.label_snapshot(OBS, kickoff, horizon_id))
    base["record_id"] = R.record_id(snapshot, ticker, "BOARD_V2", "e1", "d1")
    base["content_hash"] = R.content_hash(base)
    return base


def _per_cluster_batch(clusters, snapshot=SNAP):
    """What ONE build produces: every record carries the horizon of its own cluster."""
    return [_row(TICKER[c], KO[c], HID[c], snapshot=snapshot) for c in clusters]


def _store(tmp_path):
    return ProjectionStore(str(tmp_path / "projections"))


# ---------------------------------------------------------------- identity semantics


def test_the_horizon_is_not_part_of_the_record_identity_so_one_build_must_label_once():
    """Why looping is unfixable without this change: two horizons cannot share a snapshot and an arm."""
    a = _row(TICKER["0020"], KO["0020"], HID["1700"])
    b = _row(TICKER["0020"], KO["0020"], HID["0020"])
    assert a["record_id"] == b["record_id"], "record_id has no horizon in it"
    assert a["content_hash"] != b["content_hash"], "but the horizon fields are inside the content hash"


def test_a_record_takes_its_own_clusters_trigger_not_another_clusters():
    """The mislabel underneath the crash: a 00:20Z game is not 678 minutes late for the 17:00Z horizon."""
    own = _row(TICKER["0020"], KO["0020"], HID["0020"])
    borrowed = _row(TICKER["0020"], KO["0020"], HID["1700"])
    assert own["horizon_id"] == HID["0020"]
    assert borrowed["horizon_lateness_min"] > own["horizon_lateness_min"] + 400
    # minutes_to_kickoff is a property of the row's own game either way
    assert own["minutes_to_kickoff"] == pytest.approx(borrowed["minutes_to_kickoff"])


def test_two_horizons_of_the_same_contract_are_distinct_observations_via_distinct_snapshots():
    """T-6h and T-90m fire at different times against different captures, so they never collide."""
    t6 = _row(TICKER["1700"], KO["1700"], f"{SLATE}|20260913T1700Z|T-360m", snapshot="20260913T110000Z")
    t90 = _row(TICKER["1700"], KO["1700"], f"{SLATE}|20260913T1700Z|T-90m", snapshot="20260913T153000Z")
    assert t6["record_id"] != t90["record_id"], "different freezes must be different immutable observations"
    assert t6["horizon_label"] == "T-6h" and t90["horizon_label"] == "T-90m"


# ---------------------------------------------------------------- CASES A-G


def test_case_a_one_horizon_due_publishes(tmp_path):
    store = _store(tmp_path)
    rows = _per_cluster_batch(["1700"])
    assert store.write(SNAP, "BOARD_V2", rows)["status"] == "WRITTEN"
    assert len(read_rows(store.path(SNAP, "BOARD_V2"))) == 1


def test_case_b_three_horizons_in_one_firing_all_publish(tmp_path):
    """The live failure. One build, one write, three horizons served."""
    store = _store(tmp_path)
    rows = _per_cluster_batch(["1700", "2025", "0020"])
    assert store.write(SNAP, "BOARD_V2", rows)["status"] == "WRITTEN"
    got = read_rows(store.path(SNAP, "BOARD_V2"))
    assert len(got) == 3
    assert {r["horizon_id"] for r in got} == set(HID.values())


def test_case_c_each_cluster_keeps_its_own_distinct_horizon_observation(tmp_path):
    store = _store(tmp_path)
    store.write(SNAP, "BOARD_V2", _per_cluster_batch(["1700", "2025", "0020"]))
    by_ticker = {r["ticker"]: r for r in read_rows(store.path(SNAP, "BOARD_V2"))}
    for c in ("1700", "2025", "0020"):
        assert by_ticker[TICKER[c]]["horizon_id"] == HID[c]
        # and its lateness is measured against its OWN trigger
        trigger = KO[c] - timedelta(minutes=1440)
        assert by_ticker[TICKER[c]]["horizon_lateness_min"] == pytest.approx(
            (OBS - trigger).total_seconds() / 60.0)


def test_case_d_rerunning_the_exact_same_batch_is_idempotent(tmp_path):
    store = _store(tmp_path)
    rows = _per_cluster_batch(["1700", "2025", "0020"])
    assert store.write(SNAP, "BOARD_V2", rows)["status"] == "WRITTEN"
    assert store.write(SNAP, "BOARD_V2", _per_cluster_batch(["1700", "2025", "0020"]))["status"] == "NO_OP"
    assert len(read_rows(store.path(SNAP, "BOARD_V2"))) == 3, "a rerun must not duplicate rows"


def test_case_e_the_append_only_guard_still_refuses_a_real_mutation(tmp_path):
    """The fix must not have bought multi-fire by weakening immutability."""
    store = _store(tmp_path)
    store.write(SNAP, "BOARD_V2", _per_cluster_batch(["1700"]))
    mutated = [_row(TICKER["1700"], KO["1700"], HID["1700"], p_yes=0.91)]
    with pytest.raises(ProjectionConflict):
        store.write(SNAP, "BOARD_V2", mutated)
    assert read_rows(store.path(SNAP, "BOARD_V2"))[0]["p_yes"] == 0.55, "nothing was overwritten"


def test_case_f_the_full_board_cycle_run_is_unchanged(tmp_path):
    """horizon_id absent -> CYCLE, exactly as the 2-hourly run has always behaved."""
    cyc = _row(TICKER["1700"], KO["1700"], None)
    assert cyc["horizon_label"] == HZ.CYCLE
    assert cyc["horizon_id"] is None and cyc["horizon_target_min"] is None
    assert cyc["horizon_lateness_min"] is None
    store = _store(tmp_path)
    assert store.write(SNAP, "BOARD_V2", [cyc])["status"] == "WRITTEN"


def test_case_g_a_marker_is_only_written_for_a_horizon_that_reached_accepted_rows(tmp_path):
    """A due horizon whose cluster contributed nothing must stay due, not be claimed."""
    served = [HID["1700"], HID["2025"]]
    HZ.write_markers(str(tmp_path), served, snapshot_id=SNAP, status="CAPTURED")
    names = sorted(os.listdir(tmp_path / HZ.MARKER_DIR))
    assert names == sorted(HZ.marker_name(h) for h in served)
    assert HZ.marker_name(HID["0020"]) not in names, "an unserved horizon must not be marked captured"
    # and the unserved one is still reported due by the gate's own captured-state view
    captured = HZ.captured_state(names)["captured"]
    assert HID["0020"] not in captured and HID["1700"] in captured


def test_markers_are_append_only_and_a_rerun_does_not_rewrite_them(tmp_path):
    HZ.write_markers(str(tmp_path), [HID["1700"]], snapshot_id=SNAP, status="CAPTURED")
    p = os.path.join(str(tmp_path), HZ.MARKER_DIR, HZ.marker_name(HID["1700"]))
    first = open(p).read()
    HZ.write_markers(str(tmp_path), [HID["1700"]], snapshot_id="20260913T999999Z", status="CAPTURED")
    assert open(p).read() == first, "an existing marker is never rewritten by a later build"


# ---------------------------------------------------------------- the orchestration itself


def _projector_src():
    return open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                             "scripts", "shadow_v2", "project_slate_v2.py")).read()


def test_the_workflow_runs_ONE_build_for_all_due_horizons():
    """The loop is the bug. One process, every due id, or the store conflict returns."""
    import yaml
    wf = yaml.safe_load(open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                          ".github", "workflows", "shadow-v2-horizons.yml")))
    step = next(s for j in wf["jobs"].values() for s in j.get("steps", [])
                if "project_slate_v2.py" in (s.get("run") or ""))
    body = step["run"]
    assert "for h in" not in body and "IFS=" not in body, "the per-horizon loop is back"
    assert body.count("project_slate_v2.py") == 1, "exactly one projector invocation"
    assert '--horizon-id "$HORIZON_IDS"' in body, "all due ids must go to the one build"


def test_the_projector_selects_the_horizon_per_cluster_not_per_invocation():
    """Pins the fix at the call site: the label comes from the record's own cluster."""
    src = _projector_src()
    assert "horizon_by_cluster.get(cluster_of_game.get(gid))" in src
    assert "cluster_kickoffs(" in src, "cluster membership is computed, not assumed"
    # the old blanket application must be gone
    assert "HZ.label_snapshot(obs, ko, horizon_id)" not in src


def test_the_projector_marks_only_the_horizons_it_served():
    src = _projector_src()
    assert "if horizon_ids_applied and written:" in src
    assert "sorted(horizon_ids_applied)" in src


def test_cluster_assignment_maps_each_sunday_game_to_its_own_horizon():
    """Behavioural: real Week 1 kickoffs -> the right cluster -> the right horizon id."""
    from nfl_edge.handicap.horizons import cluster_kickoffs, parse_horizon_id
    games = [{"game_id": "2026_01_CHI_CAR", "kickoff_utc": KO["1700"]},
             {"game_id": "2026_01_TB_CIN", "kickoff_utc": KO["1700"]},
             {"game_id": "2026_01_GB_MIN", "kickoff_utc": KO["2025"]},
             {"game_id": "2026_01_DAL_NYG", "kickoff_utc": KO["0020"]}]
    cluster_of_game = {g: c["cluster_key"] for c in cluster_kickoffs(games) for g in c["game_ids"]}
    by_cluster = {parse_horizon_id(h)["cluster_key"]: h for h in HID.values()}
    assert by_cluster[cluster_of_game["2026_01_CHI_CAR"]] == HID["1700"]
    assert by_cluster[cluster_of_game["2026_01_TB_CIN"]] == HID["1700"]
    assert by_cluster[cluster_of_game["2026_01_GB_MIN"]] == HID["2025"]
    assert by_cluster[cluster_of_game["2026_01_DAL_NYG"]] == HID["0020"]


def test_within_one_cluster_the_tightest_due_horizon_wins():
    """After an outage two horizons of one cluster can be due; the observation serves the nearer one,
    never the looser one, because labelling it T-6h would backdate a T-90m observation."""
    from nfl_edge.handicap.horizons import parse_horizon_id
    due = [f"{SLATE}|20260913T1700Z|T-360m", f"{SLATE}|20260913T1700Z|T-90m"]
    chosen = {}
    for hid in due:
        h = parse_horizon_id(hid)
        cur = chosen.get(h["cluster_key"])
        if cur is None or h["horizon_min"] < cur["horizon_min"]:
            chosen[h["cluster_key"]] = h
    assert chosen["20260913T1700Z"]["horizon_id"].endswith("T-90m")
