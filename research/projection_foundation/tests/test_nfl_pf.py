"""Tests for the NFL Projection Foundation code (research/projection_foundation/nfl)."""
import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

PF = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PF)

from nfl import evaluate as EV  # noqa: E402
from nfl import ladder as L  # noqa: E402
from nfl import pipeline as P  # noqa: E402
from nfl import features as F  # noqa: E402

RESULTS = os.path.join(PF, "results")


def _toy_players(n_players=3, n_games=12, seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for p in range(n_players):
        for g in range(n_games):
            season = 2020 + g // 6
            week = g % 6 + 1
            t = float(rng.poisson(5 + p))
            rows.append({"player_id": f"p{p}", "team": "AAA", "season": season, "week": week, "block": season * 100 + week,
                         "game_id": f"{season}_{week}", "kickoff_utc": pd.Timestamp(f"{season}-09-0{week}", tz="UTC"),
                         "targets": t, "receptions": t * 0.6, "receiving_yards": t * 8, "carries": 1.0, "rushing_yards": 4.0,
                         "attempts": 0.0, "completions": 0.0, "passing_yards": 0.0, "passing_tds": 0.0, "receiving_tds": 0.0,
                         "rushing_tds": 0.0, "any_td": 0.0, "n_td": 0.0, "offense_pct": 0.7, "tm_attempts": 35.0,
                         "carry_share": 0.05, "pass_share": 0.0, "receiving_air_yards": t * 9})
    return pd.DataFrame(rows)


def test_player_features_are_point_in_time():
    """Changing the outcome of game g must not change any feature attached to game g or earlier."""
    a = _toy_players()
    b = a.copy()
    target = (b.player_id == "p1") & (b.season == 2021) & (b.week == 3)
    b.loc[target, "targets"] = 99.0
    fa = F.player_features(a, halflives=(2, 4))
    fb = F.player_features(b, halflives=(2, 4))
    cols = [c for c in fa.columns if c.startswith("targets_") and fa[c].dtype.kind == "f"]
    key = ["player_id", "season", "week"]
    fa = fa.sort_values(key).reset_index(drop=True)
    fb = fb.sort_values(key).reset_index(drop=True)
    upto = (fa.player_id == "p1") & ((fa.season < 2021) | ((fa.season == 2021) & (fa.week <= 3)))
    for c in cols:
        if c in ("targets_prev", "targets_prev_n"):
            continue  # previous-season mean; game g is in the current season
        pd.testing.assert_series_equal(fa.loc[upto, c], fb.loc[upto, c], check_names=False)
    after = (fa.player_id == "p1") & (fa.season == 2021) & (fa.week == 4)
    assert not np.allclose(fa.loc[after, "targets_ewm2"].to_numpy(), fb.loc[after, "targets_ewm2"].to_numpy())


def test_splits_and_embargo():
    s = pd.Series([2015, 2016, 2021, 2022, 2023, 2024, 2025, 2026, 2026, 2026])
    w = pd.Series([1, 1, 1, 1, 1, 1, 1, 4, 5, 9])
    up = pd.Series([False] * 9 + [True])
    out = L.split_of(s, w, up).tolist()
    assert out == ["warmup", "development", "development", "validation", "validation", "holdout", "holdout",
                   "check2026", "embargo2026", "forward"]


def test_fit_loglinear_recovers_elasticity():
    rng = np.random.default_rng(3)
    n = 20000
    base = rng.uniform(2, 8, n)
    x = rng.normal(0, 0.3, n)
    y = rng.poisson(base * np.exp(0.8 * x))
    b = L.fit_loglinear(y, base, x[:, None], np.ones(n, bool))
    assert abs(b[0] - 0.8) < 0.05


def test_bernoulli_crps_is_brier():
    p = np.array([0.1, 0.5, 0.9])
    y = np.array([0, 1, 1])
    d = EV.make({"kind": "bernoulli"}, p)
    assert np.allclose(d.crps(y), (p - y) ** 2)


def test_population_uses_prior_games_only():
    df = pd.DataFrame({"position": ["WR"] * 3, "targets_r4": [np.nan, 1.0, 3.0], "carries_r4": [np.nan, 0, 0],
                       "qb_starter": [False] * 3})
    assert P.population(df, "REC").tolist() == [False, False, True]


def test_dist_fitting_shapes():
    rng = np.random.default_rng(0)
    mu = rng.uniform(1, 8, 3000)
    y = rng.negative_binomial(5, 5 / (5 + mu))
    for k in ("poisson", "nb", "nb_binned", "empirical_ratio"):
        prm = EV.fit_dist(k, "count", y, mu, 0, 40)
        d = EV.make(prm, mu[:10])
        assert not d.coherence_violations().any()
        th = [d.prob_ge(t) for t in range(0, 15)]
        assert all((th[i] >= th[i + 1] - 1e-12).all() for i in range(14))


@pytest.mark.skipif(not os.path.exists(os.path.join(RESULTS, "summary.json")), reason="summary not generated")
def test_summary_contract():
    s = json.load(open(os.path.join(RESULTS, "summary.json")))
    assert s["schema"] == "sift.projection_foundation.sport_summary.v1" and s["sport"] == "NFL"
    for k in ("generated_utc", "code_sha", "pf_core_version", "splits", "inventory", "families", "experiments",
              "error_investigations", "opponent_adjustment", "opportunity", "calibration", "failed_experiments", "gate", "priorities"):
        assert k in s, k
    ok = {"READY", "SHADOW VALIDATION", "NEEDS IMPROVEMENT", "INSUFFICIENT DATA"}
    for f in s["families"]:
        assert f["readiness"] in ok
        assert f["best_model"] in [m["model"] for m in f["models"]]
        for m in f["models"]:
            for k in ("model", "split", "n_obs", "n_clusters", "mae", "rmse", "bias", "crps", "verdict"):
                assert k in m


@pytest.mark.skipif(not os.path.exists(os.path.join(RESULTS, "projections_latest.json")), reason="no projections")
def test_projection_contract():
    o = json.load(open(os.path.join(RESULTS, "projections_latest.json")))
    assert o["schema"] == "sift.projections.v1" and o["model"]["authority"] == "research_only"
    for p in o["players"][:500]:
        th = [p["thresholds"][k] for k in sorted(p["thresholds"], key=float)]
        assert all(th[i] >= th[i + 1] - 1e-9 for i in range(len(th) - 1))
        assert p["gate"]["status"] in ("PASS", "REVIEW", "BLOCK")
        assert p["p10"] <= p["median"] <= p["p90"]
        q = p.get("quantiles")  # additive (contract 3.1b); rows written before it existed simply lack it
        if q:
            vals = [q[k] for k in ("p05", "p25", "p50", "p75", "p95")]
            assert vals == sorted(vals) and q["p05"] <= p["p10"] and p["p90"] <= q["p95"]
