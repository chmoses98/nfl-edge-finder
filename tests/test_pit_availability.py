"""PIT availability: refusing loaders, append-only capture, and the PURE_PLAYER_V1_1 ablation's guards.

Synthetic inputs only (no network). The certification evidence is research/pit_availability/certification.json.
"""
from __future__ import annotations

import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import polars as pl
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.availability_pit import capture as CAP  # noqa: E402
from nfl_edge.availability_pit import loaders as L  # noqa: E402
from nfl_edge.availability_pit import store  # noqa: E402
from nfl_edge.engines.player.pure_v1 import MODEL_NAME  # noqa: E402
from nfl_edge.engines.player.pure_v1 import data as PD  # noqa: E402
from nfl_edge.engines.player.pure_v1 import features as PF  # noqa: E402
from nfl_edge.engines.player.pure_v1 import model as PM  # noqa: E402
from nfl_edge.engines.player.pure_v1 import pipeline as PP  # noqa: E402
from nfl_edge.engines.player.pure_v1_1 import features as F11  # noqa: E402
from nfl_edge.engines.player.pure_v1_1 import model as M11  # noqa: E402
from test_pure_player_v1 import _box, _schedule, _v4_volume  # noqa: E402

NV = os.path.join("data", "raw", "nflverse")


def _pq(df, path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    def clean(v):
        return None if v is None or v is pd.NaT or (isinstance(v, float) and np.isnan(v)) else v
    pl.DataFrame({c: [clean(v) for v in df[c].tolist()] for c in df.columns}).write_parquet(path)


@pytest.fixture
def root(tmp_path):
    """Schedule with two games (2024 wk1 Sunday 13:00 ET, 2026 wk1) and an injury file per season."""
    r = tmp_path / "root"
    sched = pd.DataFrame([{"game_id": "2024_01_AAA_BBB", "season": 2024, "week": 1, "game_type": "REG", "gameday": "2024-09-08",
                           "gametime": "13:00", "home_team": "BBB", "away_team": "AAA"},
                          {"game_id": "2026_01_AAA_BBB", "season": 2026, "week": 1, "game_type": "REG", "gameday": "2026-09-13",
                           "gametime": "13:00", "home_team": "BBB", "away_team": "AAA"}])
    os.makedirs(r / NV / "schedules")
    sched.to_csv(r / NV / "schedules" / "games.csv", index=False)
    k24 = pd.Timestamp("2024-09-08 17:00", tz="UTC")
    inj24 = pd.DataFrame({"season": [2024] * 4, "game_type": ["REG"] * 4, "team": ["AAA"] * 4, "week": [1] * 4,
                          "gsis_id": ["p1", "p2", "p3", "p4"], "position": ["WR"] * 4, "full_name": ["a", "b", "c", "d"],
                          "report_status": ["Out", "Questionable", "Doubtful", None], "practice_status": ["Did Not Participate In Practice"] * 4,
                          "report_primary_injury": ["Knee"] * 4,
                          "date_modified": [k24 - pd.Timedelta(hours=48), k24 - pd.Timedelta(hours=1), k24 + pd.Timedelta(hours=3), pd.NaT]})
    _pq(inj24, str(r / NV / "injuries" / "injuries_2024.parquet"))
    inj26 = inj24.drop(columns=["date_modified"]).assign(season=2026)
    _pq(inj26, str(r / NV / "injuries" / "injuries_2026.parquet"))
    return r


def test_row_timestamp_loader_returns_only_rows_known_before_the_cutoff(root):
    rows, rep = L.injuries_certified(str(root), [2024])
    assert set(rows.gsis_id) == {"p1"}                       # 48 h before: kept
    assert rep["refused"]["DATE_MODIFIED_AT_OR_AFTER_CUTOFF"] == 2   # 1 h before (inside T-90m) and post-kickoff
    assert rep["refused"]["DATE_MODIFIED_MISSING"] == 1
    assert (pd.to_datetime(rows.observed_at, utc=True) < pd.to_datetime(rows.cutoff, utc=True)).all()
    rows0, _ = L.injuries_certified(str(root), [2024], lead=timedelta(0))
    assert set(rows0.gsis_id) == {"p1", "p2"}               # a zero lead admits the T-1h row, never the post-kickoff one


def test_seasons_without_row_time_need_a_vintage_before_the_cutoff(root, tmp_path):
    rows, rep = L.injuries_certified(str(root), [2026])
    assert len(rows) == 0 and rep["refused"]["NO_ROW_TIMESTAMP_AND_NO_VINTAGE"] == 4
    st = tmp_path / "store"
    k = pd.Timestamp("2026-09-13 17:00", tz="UTC")
    early = pl.read_parquet(str(root / NV / "injuries" / "injuries_2026.parquet")).head(2)
    os.makedirs(st / "nflverse_injuries" / "2026")
    early.write_parquet(str(st / "nflverse_injuries" / "2026" / "a.parquet"))
    json.dump({"file": "a.parquet", "sha256": "x" * 64, "retrieved_at": (k - pd.Timedelta(hours=30)).isoformat()},
              open(st / "nflverse_injuries" / "2026" / "a.capture.json", "w"))
    late = pl.read_parquet(str(root / NV / "injuries" / "injuries_2026.parquet"))
    late.write_parquet(str(st / "nflverse_injuries" / "2026" / "b.parquet"))
    json.dump({"file": "b.parquet", "sha256": "y" * 64, "retrieved_at": (k + pd.Timedelta(hours=2)).isoformat()},
              open(st / "nflverse_injuries" / "2026" / "b.capture.json", "w"))
    rows, rep = L.injuries_certified(str(root), [2026], vintage_roots=[str(st)])
    assert set(rows.gsis_id) == {"p1", "p2"}                # only what the pre-kickoff vintage held
    assert rep["refused"]["NOT_IN_PRE_CUTOFF_VINTAGE"] == 2
    assert (rows.pit_basis == "vintage_snapshot_retrieved_at").all()


def test_depth_charts_before_2025_are_refused(root):
    with pytest.raises(L.PITRefusal):
        L.depth_chart_certified(str(root), 2024)


def test_depth_chart_loader_takes_the_newest_snapshot_before_the_cutoff(root):
    k = pd.Timestamp("2026-09-13 17:00", tz="UTC")
    d = pd.DataFrame({"dt": [(k - pd.Timedelta(hours=h)).strftime("%Y-%m-%dT%H:%M:%SZ") for h in (30, 10, 1)],
                      "team": ["AAA"] * 3, "player_name": ["x"] * 3, "espn_id": ["1"] * 3, "gsis_id": ["g1", "g2", "g3"],
                      "pos_grp_id": ["o"] * 3, "pos_grp": ["Offense"] * 3, "pos_id": ["1"] * 3, "pos_name": ["WR"] * 3,
                      "pos_abb": ["WR"] * 3, "pos_slot": [1] * 3, "pos_rank": [1] * 3})
    _pq(d, str(root / NV / "depth_charts" / "depth_charts_2026.parquet"))
    rows, rep = L.depth_chart_certified(str(root), 2026)
    a = rows[rows.team == "AAA"]
    assert list(a.gsis_id) == ["g2"]                          # 10 h before; the T-1h snapshot is inside T-90m
    assert rep["refused"].get("TEAM_ABSENT") == 1             # BBB has no chart


def test_espn_loader_refuses_ambiguous_identity_and_post_cutoff_rows(tmp_path):
    k = pd.Timestamp("2026-09-13 17:00", tz="UTC")
    cap = {"run_id": "r", "retrieved_at": (k - pd.Timedelta(hours=3)).isoformat(), "injuries": [
        {"team": "Arizona Cardinals", "name": "Joe Smith Jr.", "status": "Out", "date": (k - pd.Timedelta(hours=20)).isoformat()},
        {"team": "Arizona Cardinals", "name": "Dup Name", "status": "Out", "date": (k - pd.Timedelta(hours=20)).isoformat()},
        {"team": "Arizona Cardinals", "name": "Late Guy", "status": "Out", "date": (k + pd.Timedelta(hours=1)).isoformat()}]}
    f = tmp_path / "c.espn_injuries.json"; f.write_text(json.dumps(cap))
    later = dict(cap, retrieved_at=(k - pd.Timedelta(minutes=30)).isoformat(), injuries=[])
    f2 = tmp_path / "d.espn_injuries.json"; f2.write_text(json.dumps(later))
    ros = pd.DataFrame({"gsis_id": ["g1", "g2", "g3", "g4"], "full_name": ["Joe Smith", "Dup Name", "Dup Name", "Late Guy"], "team": ["ARI"] * 4})
    tg = pd.DataFrame({"team": ["ARI"], "game_id": ["2026_01_ARI_X"], "kickoff": [k]})
    rows, rep = L.espn_injuries_captured([str(f), str(f2)], ros, tg)
    assert list(rows.gsis_id) == ["g1"]                       # the T-30m capture is inside T-90m and is not used
    assert rep["refused"] == {"IDENTITY_AMBIGUOUS": 1, "ROW_DATE_MISSING_OR_AFTER_CUTOFF": 1}


# ------------------------------------------------------------------------------------------------ capture
class _Resp(io.BytesIO):
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _opener(now):
    ko = (now + timedelta(minutes=80)).strftime("%Y-%m-%dT%H:%MZ")

    def op(req, timeout=0):
        u = req.full_url
        if u.endswith("/injuries"):
            return _Resp(json.dumps({"injuries": [{"injuries": [{"athlete": {"id": "1"}}]}]}).encode())
        if "scoreboard" in u:
            return _Resp(json.dumps({"events": [{"id": "9", "date": ko, "shortName": "A @ B",
                                                 "competitions": [{"competitors": [{"id": "1", "team": {"abbreviation": "A"}}]}]}]}).encode())
        if u.endswith("/roster"):
            return _Resp(json.dumps({"entries": [{"playerId": i, "active": i > 6, "didNotPlay": False} for i in range(50)]}).encode())
        raise AssertionError(u)
    return op


def test_capture_is_write_once_deduplicated_and_records_retrieval_times(root, tmp_path):
    nv = root / NV
    p = nv / "injuries" / "injuries_2026.parquet"
    with open(nv / "_manifest.jsonl", "w") as fh:
        fh.write(json.dumps({"path": "data/raw/nflverse/injuries/injuries_2026.parquet", "retrieved_at": "2026-09-12T10:00:00+00:00",
                             "sha256": store.sha256_file(str(p)), "url": "u"}) + "\n")
    st = str(tmp_path / "st")
    now = datetime(2026, 9, 13, 15, 40, tzinfo=timezone.utc)
    s1 = CAP.run(str(root), st, season=2026, now=now, opener=_opener(now))
    assert s1["nflverse_injuries"]["state"] == "NEW_CONTENT"
    assert s1["espn_injuries"]["state"] == "CAPTURED"
    assert s1["espn_event_rosters"]["events"] == 1 and s1["espn_event_rosters"]["teams"][0][2][0][1] == 7
    s2 = CAP.run(str(root), st, season=2026, now=now + timedelta(hours=1), network=False)
    assert s2["nflverse_injuries"]["state"] == "UNCHANGED"
    assert store.verify_store(st) == []
    # the captured vintage is what the loader reads for a season without row time
    rows, rep = L.injuries_certified(str(root), [2026], vintage_roots=[st])
    assert rep["by_season"][2026]["returned"] == 4 and (rows.pit_basis == "vintage_snapshot_retrieved_at").all()


# ------------------------------------------------------------------------------------------------ PURE_PLAYER_V1_1
@pytest.fixture(scope="module")
def world():
    rng = np.random.default_rng(11)
    sched = _schedule(rng)
    stats, snaps = _box(sched, rng)
    return sched, stats, snaps


def _v11(sched, stats, snaps, inj, season=2017):
    pg = PD.build_player_games(stats, snaps, PD.sports_schedule(sched))
    rows, t = PF.build(pg)
    r11 = F11.add(rows, t, inj)
    m = M11.fit(r11, t, season)
    te = r11[(r11.season == season) & r11.played].reset_index(drop=True)
    d = m.intermediates(te, t)
    return PP._long(d, m.dist, m.means(d), PM.LINEAGE), rows, t, r11


def _empty_inj():
    return pd.DataFrame(columns=["season", "week", "team", "gsis_id", "report_status", "practice_status", "position", "kickoff"])


def _inj(world):
    sched, stats, _ = world
    g = PD.sports_schedule(sched)
    rng = np.random.default_rng(3)
    rows = []
    for x in g.itertuples():
        for team in (x.home_team, x.away_team):
            pid = f"{team}-WR{int(rng.integers(0, 3))}"
            rows.append({"season": x.season, "week": x.week, "team": team, "gsis_id": pid, "position": "WR", "kickoff": x.kickoff,
                         "report_status": rng.choice(["Out", "Questionable", "Doubtful"]), "practice_status": "Limited Participation in Practice"})
    return pd.DataFrame(rows)


def test_v1_1_without_injury_rows_reproduces_v1(world):
    sched, stats, snaps = world
    l11, rows, t, _ = _v11(sched, stats, snaps, _empty_inj())
    v1 = PP.run(rows, t, 2017)["player"][MODEL_NAME]
    j = v1.merge(l11, on=["game_id", "player_id", "statistic"], suffixes=("_a", "_b"))
    assert len(j) == len(v1) and np.allclose(j.mean_a, j.mean_b, atol=1e-9)


def test_v1_1_features_are_teammates_only_and_prior_only(world):
    sched, stats, snaps = world
    inj = _inj(world)
    _, rows, t, r11 = _v11(sched, stats, snaps, inj)
    listed = set(zip(inj.season, inj.week, inj.team, inj.gsis_id))
    me = r11[[(s, w, tm, p) in listed for s, w, tm, p in zip(r11.season, r11.week, r11.team, r11.player_id)]]
    assert len(me)
    # one player is listed per team-week in this fixture, so a listed player has no listed teammate: vac must be 0
    assert (me["vac_t"] == 0).all() and (me["vac_c"] == 0).all()
    out_tw = set((s_, w, tm) for s_, w, tm, rs in zip(inj.season, inj.week, inj.team, inj.report_status) if rs in ("Out", "Doubtful"))
    mates = r11[[(s_, w, tm) in out_tw for s_, w, tm in zip(r11.season, r11.week, r11.team)] & ~r11.index.isin(me.index)]
    assert (mates["vac_t"] > 0).mean() > 0.5
    # a future box score cannot move a feature: zero out a late game's targets and recompute
    late = sched[(sched.season == 2017) & (sched.week == 10)].game_id.iloc[0]
    stats2 = stats.copy(); stats2.loc[stats2.game_id == late, "targets"] = 0.0
    _, _, _, r11b = _v11(sched, stats2, snaps, inj)
    early = r11.season < 2017
    assert np.allclose(r11.loc[early, "vac_t"].to_numpy(), r11b.loc[early, "vac_t"].to_numpy())


def test_v1_1_is_bit_identical_under_market_mutation_and_v4_control_responds(world):
    sched, stats, snaps = world
    inj = _inj(world)
    base, *_ = _v11(sched, stats, snaps, inj)
    removed = sched.drop(columns=[c for c in sched.columns if "spread" in c or "total" in c or "moneyline" in c or "odds" in c])
    rnd = sched.copy(); rng = np.random.default_rng(99)
    for c in ("spread_line", "total_line", "home_moneyline", "away_moneyline"):
        rnd[c] = rng.permutation(rnd[c].to_numpy())
    for mut in (removed, rnd):
        other, *_ = _v11(mut, stats, snaps, inj)
        pd.testing.assert_frame_equal(base[["game_id", "player_id", "statistic", "mean", "p10", "p90"]].reset_index(drop=True),
                                      other[["game_id", "player_id", "statistic", "mean", "p10", "p90"]].reset_index(drop=True), check_exact=True)
    _, va = _v4_volume(sched, stats, snaps)
    _, vb = _v4_volume(rnd, stats, snaps)
    assert not np.allclose(va, vb)
