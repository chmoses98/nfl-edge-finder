"""PURE_PLAYER_V1: market independence at runtime, point-in-time guards and the kit sidecar contract.

Synthetic nflverse-shaped inputs (no network, no gitignored data). These tests prove properties of the CODE PATH;
the held-out accuracy evidence is research/pure_player_v1/ (real data), never these fixtures.

  * mutation invariance: the whole pipeline (schedule allowlist -> player games -> features -> fit -> forecast) is
    rerun with the schedule's market columns as published, removed, randomised and blanked for 30% of games, and the
    forecasts must be bit-identical;
  * negative control: DATA_PLAYER_V4's VolumeModel, fed the same mutated schedules, MUST change -- with
    market_env=True under randomisation, and with market_env=False under partial blanking (its training sample is
    filtered on implied_total.notna() whatever market_env says) -- so the test above has the power to fail;
  * point in time: every forecast's source observation precedes its cutoff, and changing a FUTURE game's box score
    cannot move an earlier forecast;
  * the module source never names a market column.
"""
from __future__ import annotations

import os

import numpy as np
import pandas as pd
import pytest

from nfl_edge.engines.player.pure_v1 import MODEL_NAME, VERSION
from nfl_edge.engines.player.pure_v1 import data as PD
from nfl_edge.engines.player.pure_v1 import features as PF
from nfl_edge.engines.player.pure_v1 import mutation as MU
from nfl_edge.engines.player.pure_v1 import pipeline as PP

TEAMS = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH"]
ROSTER = [("QB", 1), ("RB", 2), ("WR", 3), ("TE", 1)]
SEASONS = range(2013, 2018)
WEEKS = 10


def _schedule(rng) -> pd.DataFrame:
    rows = []
    for s in SEASONS:
        for w in range(1, WEEKS + 1):
            perm = rng.permutation(TEAMS)
            for i in range(0, len(TEAMS), 2):
                h, a = perm[i], perm[i + 1]
                day = pd.Timestamp(f"{s}-09-07") + pd.Timedelta(days=7 * (w - 1))
                rows.append({"game_id": f"{s}_{w:02d}_{a}_{h}", "season": s, "game_type": "REG", "week": w,
                             "gameday": day.strftime("%Y-%m-%d"), "gametime": "13:00" if i < 4 else "16:25",
                             "home_team": h, "away_team": a, "home_score": int(rng.integers(3, 45)), "away_score": int(rng.integers(3, 45)),
                             "roof": "dome" if h in ("AAA", "BBB") else "outdoors", "home_qb_id": f"{h}-QB0", "away_qb_id": f"{a}-QB0",
                             "spread_line": float(rng.normal(0, 6)), "total_line": float(rng.normal(44, 4)),
                             "home_moneyline": float(rng.normal(-110, 80)), "away_moneyline": float(rng.normal(100, 80)),
                             "under_odds": -110.0, "over_odds": -110.0, "home_spread_odds": -110.0, "away_spread_odds": -110.0})
    return pd.DataFrame(rows)


def _box(sched: pd.DataFrame, rng) -> tuple[pd.DataFrame, pd.DataFrame]:
    st, sn = [], []
    for g in sched.itertuples():
        for team, opp in ((g.home_team, g.away_team), (g.away_team, g.home_team)):
            for pos, n in ROSTER:
                for j in range(n):
                    pid = f"{team}-{pos}{j}"
                    snaps = int(rng.integers(40, 70)) if j == 0 else int(rng.integers(0, 35))
                    row = {"player_id": pid, "player_display_name": pid, "position": pos, "season": g.season, "week": g.week,
                           "game_id": g.game_id, "team": team, "opponent_team": opp,
                           "completions": 0.0, "attempts": 0.0, "passing_yards": 0.0, "passing_tds": 0.0, "passing_interceptions": 0.0,
                           "carries": 0.0, "rushing_yards": 0.0, "rushing_tds": 0.0, "receptions": 0.0, "targets": 0.0,
                           "receiving_yards": 0.0, "receiving_tds": 0.0}
                    if pos == "QB" and j == 0:
                        row["attempts"] = float(rng.integers(20, 45)); row["completions"] = float(rng.binomial(int(row["attempts"]), 0.64))
                        row["passing_yards"] = float(row["completions"] * rng.uniform(8, 13)); row["carries"] = float(rng.integers(0, 6))
                    if pos in ("RB", "WR", "TE"):
                        row["targets"] = float(rng.poisson(5 if j == 0 else 2)); row["receptions"] = float(rng.binomial(int(row["targets"]), 0.65))
                        row["receiving_yards"] = float(row["receptions"] * rng.uniform(5, 14))
                    if pos == "RB":
                        row["carries"] = float(rng.poisson(14 if j == 0 else 5)); row["rushing_yards"] = float(row["carries"] * rng.uniform(2, 6))
                    if snaps > 0:
                        st.append(row)
                        sn.append({"player_id": pid, "player_display_name": pid, "position": pos, "season": g.season, "week": g.week,
                                   "game_id": g.game_id, "team": team, "opponent_team": opp, "offense_snaps": float(snaps)})
    return pd.DataFrame(st), pd.DataFrame(sn)


@pytest.fixture(scope="module")
def world():
    rng = np.random.default_rng(11)
    sched = _schedule(rng)
    stats, snaps = _box(sched, rng)
    return sched, stats, snaps


def _pure(sched, stats, snaps, season=2017):
    pg = PD.build_player_games(stats, snaps, PD.sports_schedule(sched))
    rows, t = PF.build(pg)
    out = PP.run(rows, t, season)
    fc, _ = PP.sidecar_rows(out["player"][MODEL_NAME], VERSION, str(rows.loc[rows.season < season, "kickoff"].max()))
    return fc, out


def _v4_volume(sched, stats, snaps, season=2017, market_env=True):
    """The negative control: V4's team volume through a market-reading join of the same schedule."""
    from nfl_edge.engines.player.v4.volume import VolumeModel, team_game_table
    df = PD.build_player_games(stats, snaps, PD.sports_schedule(sched))
    g = sched.set_index("game_id")
    sp = g["spread_line"] if "spread_line" in g.columns else pd.Series(np.nan, index=g.index)
    tl = g["total_line"] if "total_line" in g.columns else pd.Series(np.nan, index=g.index)
    df["spread_team"] = np.where(df["home"], df["game_id"].map(sp), -df["game_id"].map(sp))
    df["implied_total"] = (df["game_id"].map(tl) + df["spread_team"]) / 2.0
    df["indoor"] = df["dome"]; df["qb_changed_recent"] = 0.0
    teams = team_game_table(df)
    vm = VolumeModel.fit(teams, season, market_env=market_env)
    return vm.info["n_team_games"], vm.predict(teams[teams.season == season]).vol_pa.to_numpy()


def test_forecasts_are_bit_identical_under_every_market_mutation(world):
    sched, stats, snaps = world
    base, _ = _pure(sched, stats, snaps)
    assert len(base) > 500
    d0 = MU.forecast_digest(base)
    for mode in ("removed", "randomized", "partial_blank"):
        fc, _ = _pure(MU.mutate_schedule(sched, mode), stats, snaps)
        assert MU.forecast_digest(fc) == d0, mode


def test_negative_control_v4_volume_changes_under_the_same_mutations(world):
    sched, stats, snaps = world
    n0, p0 = _v4_volume(sched, stats, snaps, market_env=True)
    _, p1 = _v4_volume(MU.mutate_schedule(sched, "randomized"), stats, snaps, market_env=True)
    assert not np.array_equal(p0, p1)
    # market_env=False still selects its training sample on implied_total.notna()
    m0, q0 = _v4_volume(sched, stats, snaps, market_env=False)
    m1, q1 = _v4_volume(MU.mutate_schedule(sched, "partial_blank"), stats, snaps, market_env=False)
    assert m1 < m0 and not np.array_equal(q0, q1)
    with pytest.raises(Exception):
        _v4_volume(MU.mutate_schedule(sched, "removed"), stats, snaps, market_env=False)


def test_sidecar_rows_meet_the_point_in_time_contract(world):
    sched, stats, snaps = world
    fc, _ = _pure(sched, stats, snaps)
    for r in fc[:400]:
        so, ao, ko = (pd.Timestamp(r[k]) for k in ("source_max_observed_at", "as_of", "kickoff"))
        assert so <= ao < ko
        p = r["projection"]
        assert p["p10"] <= p["median"] <= p["p90"]
        probs = [t["probability"] for t in p["thresholds"]]
        assert all(a >= b for a, b in zip(probs, probs[1:]))
        assert r["projection_mode"] == "PURE_INDEPENDENT" and r["conditional_on_playing"] is True
        assert not any(tok in k.lower() for k in r["model_features"]["lineage"] for tok in ("market", "odds", "implied", "spread", "price"))


def test_a_future_box_score_cannot_move_an_earlier_forecast(world):
    sched, stats, snaps = world
    _, out = _pure(sched, stats, snaps)
    late = stats.copy()
    m = (late.season == 2017) & (late.week == 6)
    late.loc[m, ["targets", "receptions", "receiving_yards", "carries", "rushing_yards", "attempts", "passing_yards"]] *= 3
    _, out2 = _pure(sched, late, snaps)
    a = out["player"][MODEL_NAME].sort_values(["game_id", "player_id", "statistic"])
    b = out2["player"][MODEL_NAME].sort_values(["game_id", "player_id", "statistic"])
    # forecasts up to and including week 6 cannot see week 6's box score; later ones must
    assert np.array_equal(a[a.week <= 6]["mean"].to_numpy(), b[b.week <= 6]["mean"].to_numpy())
    assert not np.array_equal(a[a.week > 6]["mean"].to_numpy(), b[b.week > 6]["mean"].to_numpy())


def test_schedule_allowlist_refuses_market_columns():
    with pytest.raises(PD.MarketColumnError):
        PD.attest_sports_only(["game_id", "spread_line"])
    PD.attest_sports_only(list(PD.SCHEDULE_ALLOWLIST) + list(PD.PLAYER_ALLOWLIST))


def test_module_source_never_reads_a_market_column():
    root = os.path.join(os.path.dirname(__file__), "..", "nfl_edge", "engines", "player", "pure_v1")
    for fn in ("data.py", "features.py", "model.py", "dists.py", "baseline.py", "pipeline.py"):
        src = open(os.path.join(root, fn)).read()
        for tok in ('"spread_line"', '"total_line"', '"implied_total"', '"spread_team"', '"home_moneyline"', '"away_moneyline"',
                    '"vegas_wp"', "player_kalshi_id", "env_known"):
            assert tok not in src, (fn, tok)


def test_module_source_never_reads_expected_pass_or_win_probability():
    # nflfastR's xpass model takes vegas_wp (closing-spread-conditioned) as an input, so xpass / pass_oe and every PROE
    # derived from them carry sportsbook information indirectly. See docs/research/PURE_PLAYER_V1_XPASS_VERIFICATION.md.
    root = os.path.join(os.path.dirname(__file__), "..", "nfl_edge", "engines", "player", "pure_v1")
    for fn in ("data.py", "features.py", "model.py", "dists.py", "baseline.py", "pipeline.py"):
        src = open(os.path.join(root, fn)).read().lower()
        for tok in ("xpass", "pass_oe", "proe", "vegas", '"wp"', "play_by_play", "pbp"):
            assert tok not in src, (fn, tok)
