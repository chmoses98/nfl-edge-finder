"""The simulation layer's injury evidence is a DATED artifact, not whatever the release says today.

The nflverse injury file is rebuilt in place as designations are filed, so reading it directly makes an
old projection re-run against a newer report -- and in the other direction, it is how a game-day
designation could reach a projection made before it existed.  The layer resolves it through the
content-addressed vintage index and records the hash, the retrieval instant and the reason on every run's
manifest; Sleeper supplements that and never silently replaces it.

The Price / Stevenson failures in Week 1 were role redistribution after availability changed, so the
redistribution itself is tested here too.
"""
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import polars as pl
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.shadow_v2 import vintage_snapshots as VS  # noqa: E402
from nfl_edge.sim import features as F, prospective as P, simulate as S  # noqa: E402
import sim_fixtures as FX  # noqa: E402

SEASON = 2026


def _write_release(root: str, rows: list[dict]) -> str:
    d = os.path.join(root, "data", "raw", "nflverse", "injuries")
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"injuries_{SEASON}.parquet")
    pl.DataFrame(rows, schema={"season": pl.Int32, "game_type": pl.Utf8, "team": pl.Utf8, "week": pl.Int32,
                               "gsis_id": pl.Utf8, "position": pl.Utf8, "report_status": pl.Utf8,
                               "practice_status": pl.Utf8}).write_parquet(path)
    return path


def _row(pid, status, week=2, team="SEA", pos="RB"):
    return {"season": SEASON, "game_type": "REG", "team": team, "week": week, "gsis_id": pid,
            "position": pos, "report_status": status, "practice_status": None}


def _snapshot(root: str, at: str):
    rel = os.path.join("data", "raw", "nflverse", "injuries", f"injuries_{SEASON}.parquet")
    return VS.ensure_snapshot(root, rel, retrieved_at=at, source_url="test", season=SEASON)


# --------------------------------------------------------------- the vintage is what is read
def test_a_later_injury_report_cannot_reach_an_earlier_projection(tmp_path):
    root = str(tmp_path)
    _write_release(root, [_row("p_early", "Questionable")])
    v1 = _snapshot(root, "2026-09-15T12:00:00+00:00")
    # the release is rebuilt on game day with a new designation
    _write_release(root, [_row("p_early", "Questionable"), _row("p_late", "Out")])
    v2 = _snapshot(root, "2026-09-20T16:00:00+00:00")
    assert v1["sha256"] != v2["sha256"]

    early = datetime(2026, 9, 16, tzinfo=timezone.utc)
    path, row, why = P.injury_vintage(root, SEASON, early)
    assert path and row["sha256"] == v1["sha256"], why
    got = F.injury_designations(SEASON, 2, root=path)
    assert set(got["player_id"]) == {"p_early"}, "the game-day addition leaked into a Wednesday projection"

    late = datetime(2026, 9, 21, tzinfo=timezone.utc)
    path2, row2, _ = P.injury_vintage(root, SEASON, late)
    assert row2["sha256"] == v2["sha256"]
    assert set(F.injury_designations(SEASON, 2, root=path2)["player_id"]) == {"p_early", "p_late"}


def test_registering_a_newer_vintage_does_not_move_an_earlier_resolution(tmp_path):
    root = str(tmp_path)
    _write_release(root, [_row("a", "Out")])
    _snapshot(root, "2026-09-15T12:00:00+00:00")
    cut = datetime(2026, 9, 16, tzinfo=timezone.utc)
    before = P.injury_vintage(root, SEASON, cut)[1]["sha256"]
    for stamp, rows in (("2026-09-18T12:00:00+00:00", [_row("a", "Out"), _row("b", "Out")]),
                        ("2026-09-19T12:00:00+00:00", [_row("a", "Out"), _row("b", "Out"), _row("c", "Doubtful")])):
        _write_release(root, rows); _snapshot(root, stamp)
    after = P.injury_vintage(root, SEASON, cut)[1]["sha256"]
    assert before == after, "an earlier cutoff's injury evidence changed when later reports were filed"


def test_no_qualifying_vintage_reports_an_absence_and_never_reads_the_mutable_file(tmp_path):
    root = str(tmp_path)
    _write_release(root, [_row("a", "Out")])
    _snapshot(root, "2026-09-20T12:00:00+00:00")
    path, row, why = P.injury_vintage(root, SEASON, datetime(2026, 9, 10, tzinfo=timezone.utc))
    assert path is None and "after this cutoff" in why
    # the mutable file exists and says "a is Out"; the layer must NOT have used it
    assert os.path.exists(os.path.join(root, "data", "raw", "nflverse", "injuries", f"injuries_{SEASON}.parquet"))


def test_the_manifest_records_the_hash_vintage_and_reason(tmp_path):
    root = str(tmp_path)
    _write_release(root, [_row("a", "Out")])
    v = _snapshot(root, "2026-09-15T12:00:00+00:00")
    path, row, why = P.injury_vintage(root, SEASON, datetime(2026, 9, 16, tzinfo=timezone.utc))
    block = {"resolved": path is not None, "snapshot_path": row.get("snapshot_path"),
             "sha256": row.get("sha256"), "retrieved_at": row.get("retrieved_at"), "reason": why}
    assert block["sha256"] == v["sha256"] and block["retrieved_at"] and block["snapshot_path"]
    json.dumps(block)  # must be serialisable onto the run manifest


# ------------------------------------------------------- availability states and redistribution
@pytest.mark.parametrize("nfl,sleeper,expected", [
    ("Out", None, "OUT"),
    ("Doubtful", None, "DOUBTFUL"),
    ("Questionable", None, "QUESTIONABLE"),
    (None, None, "EXPECTED_ACTIVE"),
    (None, {"injury_status": "IR", "status": "Active"}, "OUT"),
    (None, {"injury_status": None, "status": "Inactive"}, "OUT"),
    (None, {"injury_status": "Questionable", "status": "Active"}, "QUESTIONABLE"),
    ("Questionable", {"injury_status": None, "status": "Active"}, "QUESTIONABLE"),
])
def test_sleeper_supplements_the_report_and_only_ever_tightens_it(nfl, sleeper, expected):
    assert P.avail_state(nfl, sleeper) == expected


def test_sleeper_cannot_clear_an_out_designation():
    assert P.avail_state("Out", {"injury_status": None, "status": "Active"}) == "OUT"


def test_an_out_starter_redistributes_his_carries_and_targets_to_eligible_teammates():
    from nfl_edge.pricing.game_env import ResidualBank
    b, tf, pf = FX.synthetic_bundle(seed=3)
    rng = np.random.default_rng(3); n = 600
    bank = ResidualBank(rng.normal(0, 13, n), rng.normal(0, 13, n), np.repeat([2020, 2021, 2022], n // 3),
                        ref_season=2023, spread_lines=np.full(n, 3.0), total_lines=np.full(n, 44.0),
                        overtime=rng.random(n) < 0.06, results=rng.normal(0, 13, n), rng=np.random.default_rng(1))
    gi = FX.game_input(tf, pf)
    team = gi.home.team
    rb1 = f"{team}_RB1"; rb2 = f"{team}_RB2"; wr1 = f"{team}_WR1"; te1 = f"{team}_TE1"
    base = S.simulate(gi, b, n=4000, bank=bank, seed=9)
    # the projection layer drops OUT and DOUBTFUL players from the eligible set entirely
    gi.home.players = gi.home.players[gi.home.players["player_id"] != rb1].reset_index(drop=True)
    out = S.simulate(gi, b, n=4000, bank=bank, seed=9)
    assert rb1 not in out.player
    assert out.player[rb2]["carries"].mean() > base.player[rb2]["carries"].mean() + 2.0, "carries did not move"
    assert out.player[rb2]["targets"].mean() >= base.player[rb2]["targets"].mean()
    for pid in (rb2, wr1, te1):
        assert out.player[pid]["targets"].sum() >= 0
    # the team's own volume is unchanged -- the share is redistributed, not created
    assert abs(out.team[team]["rush_att"].mean() - base.team[team]["rush_att"].mean()) < 1.0
    assert S.coherence_report(out)["ok"]


def test_a_questionable_starter_keeps_most_of_his_role_but_not_all_of_it():
    from nfl_edge.pricing.game_env import ResidualBank
    b, tf, pf = FX.synthetic_bundle(seed=3)
    rng = np.random.default_rng(3); n = 600
    bank = ResidualBank(rng.normal(0, 13, n), rng.normal(0, 13, n), np.repeat([2020, 2021, 2022], n // 3),
                        ref_season=2023, spread_lines=np.full(n, 3.0), total_lines=np.full(n, 44.0),
                        overtime=rng.random(n) < 0.06, results=rng.normal(0, 13, n), rng=np.random.default_rng(1))
    gi = FX.game_input(tf, pf)
    team = gi.home.team; rb1 = f"{team}_RB1"
    base = S.simulate(gi, b, n=4000, bank=bank, seed=11)
    gi.home.players.loc[gi.home.players["player_id"] == rb1, "avail_state"] = "QUESTIONABLE"
    q = S.simulate(gi, b, n=4000, bank=bank, seed=11)
    lo, hi = base.player[rb1]["carries"].mean() * 0.5, base.player[rb1]["carries"].mean() * 0.95
    assert lo < q.player[rb1]["carries"].mean() < hi
    assert q.player[rb1]["active"].mean() < 1.0
