"""PURE_PLAYER_V1_2 (research challenger): market independence at runtime, point in time, and V1 left frozen.

Synthetic nflverse-shaped inputs from tests/test_pure_player_v1.py (no network, no gitignored data). The held-out
accuracy evidence is research/pure_player_v1_2/ (real data), never these fixtures.
"""
from __future__ import annotations

import hashlib
import os

import numpy as np
import pandas as pd
import pytest

from nfl_edge.engines.player.pure_v1 import data as PD
from nfl_edge.engines.player.pure_v1 import features as PF
from nfl_edge.engines.player.pure_v1 import mutation as MU
from nfl_edge.engines.player.pure_v1 import pipeline as P1
from nfl_edge.engines.player.pure_v1_2 import MODEL_NAME, VERSION
from nfl_edge.engines.player.pure_v1_2 import features as F
from nfl_edge.engines.player.pure_v1_2 import model as M
from nfl_edge.engines.player.pure_v1_2 import pipeline as P12
from test_pure_player_v1 import _box, _schedule

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
# PURE_PLAYER_V1's package at the commit this challenger was built against (origin/main d4cdcb3): V1_2 must not edit it
PURE_V1_SOURCE_SHA256 = "23a7ce16e1b596722736e8d2ca776ba2c883c0b7ee8d3fe0600f6cbd05dc39b8"


@pytest.fixture(scope="module")
def world():
    rng = np.random.default_rng(11)
    sched = _schedule(rng)
    stats, snaps = _box(sched, rng)
    return sched, stats, snaps


def _v12(sched, stats, snaps, season=2017):
    pg = PD.build_player_games(stats, snaps, PD.sports_schedule(sched))
    rows, t = PF.build(pg)
    out = P12.run(P12.add_features(rows, t), t, season)
    fc, _ = P1.sidecar_rows(out["player"][MODEL_NAME], VERSION, str(rows.loc[rows.season < season, "kickoff"].max()))
    return fc, out, rows, t


def test_pure_v1_package_is_untouched():
    d = os.path.join(ROOT, "nfl_edge", "engines", "player", "pure_v1")
    blob = b"".join(open(os.path.join(d, f), "rb").read() for f in sorted(os.listdir(d)) if f.endswith(".py"))
    assert hashlib.sha256(blob).hexdigest() == PURE_V1_SOURCE_SHA256


def test_forecasts_are_bit_identical_under_every_market_mutation(world):
    sched, stats, snaps = world
    base, out, _, _ = _v12(sched, stats, snaps)
    assert len(base) > 500 and all(r["model_version"] == VERSION for r in base)
    d0 = MU.forecast_digest(base)
    for mode in ("removed", "randomized", "partial_blank"):
        fc, _, _, _ = _v12(MU.mutate_schedule(sched, mode), stats, snaps)
        assert MU.forecast_digest(fc) == d0, mode


def test_a_future_box_score_cannot_move_an_earlier_forecast(world):
    sched, stats, snaps = world
    base, out, _, _ = _v12(sched, stats, snaps)
    st2 = stats.copy()
    late = st2["game_id"].str.startswith("2017_10")              # the last week of the target season
    st2.loc[late, "receiving_yards"] = st2.loc[late, "receiving_yards"] * 3 + 50
    st2.loc[late, "targets"] = st2.loc[late, "targets"] + 7
    fc, _, _, _ = _v12(sched, st2, snaps)
    early = lambda rows: [r for r in rows if not r["game_id"].startswith("2017_10")]   # noqa: E731
    assert MU.forecast_digest(early(fc)) == MU.forecast_digest(early(base))


def test_defence_features_use_only_the_defences_prior_games(world):
    sched, stats, snaps = world
    pg = PD.build_player_games(stats, snaps, PD.sports_schedule(sched))
    rows, t = PF.build(pg)
    dg = F.defence_by_group(rows, t)
    st2 = stats.copy()
    g = st2["game_id"].str.startswith("2016_05")
    st2.loc[g, "receiving_yards"] = st2.loc[g, "receiving_yards"] + 200
    rows2, t2 = PF.build(PD.build_player_games(st2, snaps, PD.sports_schedule(sched)))
    dg2 = F.defence_by_group(rows2, t2)
    k = dg.merge(t[["game_id", "kickoff"]].drop_duplicates("game_id"), on="game_id")
    cut = t.loc[t.game_id.str.startswith("2016_05"), "kickoff"].min()
    m = k.merge(dg2, on=["opponent_team", "game_id"], suffixes=("", "_2"))
    before = m[m.kickoff <= cut]
    after = m[m.kickoff > cut]
    assert np.allclose(before["dg_ypt_WR"], before["dg_ypt_WR_2"], equal_nan=True)
    assert not np.allclose(after["dg_ypt_WR"], after["dg_ypt_WR_2"], equal_nan=True)


def test_available_pool_drops_when_a_share_holder_stops_playing(world):
    sched, stats, snaps = world
    # WR0 of team AAA stops playing after 2016 week 4 (no box score, no snaps)
    out_g = stats["game_id"].str.match(r"2016_(0[5-9]|10)") & (stats["player_id"] == "AAA-WR0")
    st2 = stats[~out_g]; sn2 = snaps[~(snaps["game_id"].str.match(r"2016_(0[5-9]|10)") & (snaps["player_id"] == "AAA-WR0"))]
    rows, t = PF.build(PD.build_player_games(st2, sn2, PD.sports_schedule(sched)))
    pool = F.available_pool(rows, t)
    d = pd.concat([rows[["player_id", "season", "week", "team", "played"]], pool], axis=1)
    mate = d[(d.player_id == "AAA-WR1") & (d.season == 2016) & d.played]
    wk5, wk7 = mate[mate.week == 5], mate[mate.week == 7]
    assert len(wk5) == 1 and len(wk7) == 1
    # week 5's pool still holds WR0 (he played week 4); week 7's does not, so the active pool shrinks
    assert wk7["pool_t"].iloc[0] < wk5["pool_t"].iloc[0]
    assert wk7["norm_t"].iloc[0] > 0
    assert ((pool["pool_t"] >= 0) & (pool["norm_t"] >= 0) & (pool["norm_t"] <= 1)).all()


def test_model_reads_no_market_or_injury_column():
    src = ""
    d = os.path.join(ROOT, "nfl_edge", "engines", "player", "pure_v1_2")
    for f in sorted(os.listdir(d)):
        if f.endswith(".py"):
            code = [ln for ln in open(os.path.join(d, f)).read().splitlines() if not ln.lstrip().startswith(("#", '"', "'"))]
            src += "\n".join(code)
    for tok in ("spread_line", "total_line", "moneyline", "implied_total", "spread_team", "vegas_wp", "xpass", "pass_oe", "proe",
                "report_status", "injuries_", "roster_weekly", "kalshi"):
        assert tok not in src, tok
    feats = set(M.NEW_FEATURES)
    PD.attest_sports_only(feats)
