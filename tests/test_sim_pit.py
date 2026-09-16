"""Adversarial point-in-time tests: NOTHING about a game may reach a projection made before it.

The weaker property -- "a row's own outcome does not enter its own feature" -- is in test_sim_engine.py.
These tests are the strong one, and they exist because the first version of this layer failed it: the
shrinkage targets (league play-volume means, pooled position rates, rate denominators) were computed over
the whole assembled frame, so a week-1 projection's priors had seen week 18 of the same season.

Every test here perturbs the FUTURE by absurd amounts and asserts an earlier row does not move by a bit.
"""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.sim import features as F, training as T  # noqa: E402
import sim_fixtures as FX  # noqa: E402

TRAIN = (2020, 2021)
EVAL = 2022
CUT_WEEK = 3           # rows at or before this week of the evaluation season must be immovable


def _frames(seed=7):
    rng = np.random.default_rng(seed)
    tg = FX.team_frame(rng, n_games=240, seasons=TRAIN + (EVAL,))
    pg = FX.player_frame(rng, tg)
    return tg, pg


def _poison_future(tg: pd.DataFrame, pg: pd.DataFrame, factor=1000.0):
    """Make every evaluation-season game after CUT_WEEK absurd.  A projection for week <= CUT_WEEK that
    moves by any amount is reading the future."""
    tg, pg = tg.copy(), pg.copy()
    tm = (tg["season"] == EVAL) & (tg["week"] > CUT_WEEK)
    pm = (pg["season"] == EVAL) & (pg["week"] > CUT_WEEK)
    for c in ("plays", "dropbacks", "pass_att", "rush_att", "designed_rush", "targets", "completions",
              "pass_yards", "rush_yards", "points", "drives", "sacks", "scrambles", "pass_td", "rush_td",
              "off_td", "neutral_pass_rate", "pass_rate", "sec_per_play", "epa_play", "success_rate", "rz_trips"):
        if c in tg.columns:
            tg.loc[tm, c] = tg.loc[tm, c] * factor
    for c in ("carries", "designed_carries", "rush_yards", "rush_td", "targets", "receptions", "rec_yards",
              "rec_td", "air_yards", "attempts", "completions", "pass_yards", "pass_td", "offense_snaps",
              "rush_10plus", "rz_carries", "i5_carries", "ez_targets", "rz_targets", "ints", "sacks_taken"):
        if c in pg.columns:
            pg.loc[pm, c] = pg.loc[pm, c] * factor
    return tg, pg


def _build(tg, pg, priors):
    tf = F.team_features(tg, priors=priors)
    pf = F.player_features(pg, tg, priors=priors)
    return tf, pf


def _early(df):
    return df[(df["season"] == EVAL) & (df["week"] <= CUT_WEEK)].sort_values(
        [c for c in ("team", "player_id", "game_id") if c in df.columns]).reset_index(drop=True)


@pytest.fixture(scope="module")
def priors():
    """Frozen on the TRAINING seasons only -- the invariant under test."""
    tg, pg = _frames()
    tr = tg[tg["season"].isin(TRAIN)]; pr = pg[pg["season"].isin(TRAIN)]
    return F.fit_priors(tr, pr, fit_seasons=TRAIN)


# --------------------------------------------------------------------------------- the strong property
def test_poisoning_the_rest_of_the_evaluation_season_moves_no_earlier_feature(priors):
    tg, pg = _frames()
    tf0, pf0 = _build(tg, pg, priors)
    tgp, pgp = _poison_future(tg, pg)
    tf1, pf1 = _build(tgp, pgp, priors)
    for name, a, b in (("team", _early(tf0), _early(tf1)), ("player", _early(pf0), _early(pf1))):
        assert list(a.columns) == list(b.columns)
        assert len(a) == len(b) and len(a) > 0
        for c in a.columns:
            if a[c].dtype.kind not in "fiub":
                continue
            x, y = a[c].to_numpy(dtype=float), b[c].to_numpy(dtype=float)
            same = np.array_equal(x, y, equal_nan=True)
            assert same, f"{name} feature {c!r} moved when the FUTURE of the evaluation season changed"


def test_the_poison_does_move_later_rows_so_the_test_has_teeth(priors):
    """A no-future test that cannot fail is worthless: the same poison must move rows that legitimately
    see it."""
    tg, pg = _frames()
    tf0, _ = _build(tg, pg, priors)
    tgp, pgp = _poison_future(tg, pg)
    tf1, _ = _build(tgp, pgp, priors)
    late0 = tf0[(tf0["season"] == EVAL) & (tf0["week"] == tf0["week"].max())]["off_plays"].to_numpy()
    late1 = tf1[(tf1["season"] == EVAL) & (tf1["week"] == tf1["week"].max())]["off_plays"].to_numpy()
    assert not np.allclose(late0, late1), "the poison never reached any row; the test proves nothing"


def test_refitting_priors_on_the_evaluation_season_would_change_them(priors):
    """The negative control for the FIX: priors fitted over the whole frame DO move when the evaluation
    season is poisoned, which is exactly the leak that was found and removed."""
    tg, pg = _frames()
    tgp, pgp = _poison_future(tg, pg)
    leaky_clean = F.fit_priors(tg, pg)
    leaky_poisoned = F.fit_priors(tgp, pgp)
    assert leaky_clean.team_level["plays"] != leaky_poisoned.team_level["plays"]
    # ... while the frozen training-only priors are untouched by the same poison
    tr_clean = F.fit_priors(tg[tg["season"].isin(TRAIN)], pg[pg["season"].isin(TRAIN)], fit_seasons=TRAIN)
    tr_poisoned = F.fit_priors(tgp[tgp["season"].isin(TRAIN)], pgp[pgp["season"].isin(TRAIN)], fit_seasons=TRAIN)
    assert tr_clean.to_dict() == tr_poisoned.to_dict() == priors.to_dict()


# ------------------------------------------------------------------ the two mechanisms, named explicitly
def test_a_future_players_efficiency_cannot_move_an_earlier_position_prior(priors):
    """The pooled position rate was computed over the whole frame, so one future 10,000-yard game moved
    every earlier player's ``prior_ypc`` and hence his shrunk ``rt_ypc``."""
    tg, pg = _frames()
    pgp = pg.copy()
    late = (pgp["season"] == EVAL) & (pgp["week"] > CUT_WEEK) & (pgp["position"] == "RB")
    pgp.loc[late, "rush_yards"] = 10000.0
    _, pf0 = _build(tg, pg, priors)
    _, pf1 = _build(tg, pgp, priors)
    a, b = _early(pf0), _early(pf1)
    for c in ("prior_ypc", "rt_ypc", "rt_explosive_rate", "prior_ypt"):
        assert np.array_equal(a[c].to_numpy(dtype=float), b[c].to_numpy(dtype=float), equal_nan=True), c


def test_future_league_play_volume_cannot_move_an_earlier_team_shrink_target(priors):
    """``off_plays`` shrinks toward the league mean of plays; that mean must be a constant of the fit
    seasons, not a statistic of the season being predicted."""
    tg, pg = _frames()
    tgp = tg.copy()
    late = (tgp["season"] == EVAL) & (tgp["week"] > CUT_WEEK)
    tgp.loc[late, "plays"] = 5000.0
    tgp.loc[late, "rush_att"] = 4000.0
    tf0, _ = _build(tg, pg, priors)
    tf1, _ = _build(tgp, pg, priors)
    a, b = _early(tf0), _early(tf1)
    for c in ("off_plays", "def_plays", "off_ypc", "def_ypc", "off_td_per_drive"):
        assert np.array_equal(a[c].to_numpy(dtype=float), b[c].to_numpy(dtype=float), equal_nan=True), c


def test_features_refuse_to_invent_their_own_priors():
    tg, pg = _frames()
    with pytest.raises(F.MissingPriors):
        F.team_features(tg)
    with pytest.raises(F.MissingPriors):
        F.player_features(pg, tg)
    with pytest.raises(F.MissingPriors):
        T.assemble([2020])


def test_prior_seasons_never_reach_the_evaluation_season():
    for y in (2023, 2024, 2025, 2026):
        seasons = T.prior_seasons_for(y)
        assert seasons and max(seasons) == y - 1, (y, seasons)


def test_a_bundle_whose_priors_reach_the_evaluation_season_is_refused():
    tg, pg = _frames()
    leaky = F.fit_priors(tg, pg)            # fitted over 2020-2022, including the evaluation season
    frames = {"priors": leaky, "team": pd.DataFrame(), "eligible": pd.DataFrame(), "carries": pd.DataFrame(),
              "targets": pd.DataFrame(), "player": pd.DataFrame(), "outside": pd.DataFrame()}
    with pytest.raises(F.MissingPriors, match="reaches into or past"):
        T.fit_bundle(EVAL, frames, verbose=lambda *x: None)
