"""Player engine v2: one distribution object, market ladders that are valid distributions, hybrids that refuse, no leakage."""
import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.engines.player import data_dist as DD, hybrid_dist as HD, market_dist as MD  # noqa: E402
from nfl_edge.engines.player.dist import InvalidDistribution, LatticeDistribution         # noqa: E402
from nfl_edge.engines.player.features_v2 import V2_FEATURES, add_v2_features              # noqa: E402


def test_lattice_refuses_invalid_pmf_and_repairs_a_non_monotone_cdf():
    with pytest.raises(InvalidDistribution):
        LatticeDistribution([0.5, 0.6])
    with pytest.raises(InvalidDistribution):
        LatticeDistribution([1.2, -0.2])
    d = LatticeDistribution.from_cdf([0.2, 0.1, 0.9, 1.0])       # dips at k=1: clamped by running max
    ok, why = d.check_valid()
    assert ok, why
    S = d.survival_curve()
    assert np.all(np.diff(S) <= 1e-12) and S[0] == pytest.approx(1.0)
    assert d.survival(2) == pytest.approx(1 - 0.2) and d.range_prob(0, 1) == pytest.approx(0.2)


def _rungs(ks, mids, width=0.04):
    return [{"threshold": k, "yes_bid": m - width / 2, "yes_ask": m + width / 2} for k, m in zip(ks, mids)]


def test_market_distribution_is_monotone_bracketed_by_bid_and_ask_and_identified():
    rec = MD.market_distribution("receiving_yards", _rungs([30, 40, 50, 60, 70], [0.85, 0.62, 0.55, 0.30, 0.12]))
    assert rec["identification"] == MD.FULL and rec["raw_violations"] == 0
    mono = [r["mid_monotone"] for r in rec["rungs"]]
    assert all(a >= b for a, b in zip(mono, mono[1:]))
    for r in rec["rungs"]:
        assert r["bid_monotone"] <= r["mid_monotone"] <= r["ask_monotone"]
    ok, why = rec["_dist"].check_valid()
    assert ok, why
    assert abs(rec["_dist"].survival(50) - 0.55) < 0.10


def test_market_distribution_fixes_crossed_ladders_and_reports_them():
    rec = MD.market_distribution("receptions", _rungs([3, 4, 5], [0.70, 0.75, 0.30]))   # 4+ quoted above 3+: impossible
    assert rec["raw_violations"] == 1
    mono = [r["mid_monotone"] for r in rec["rungs"]]
    assert mono[0] >= mono[1] >= mono[2]


def test_wide_or_one_sided_quotes_are_excluded_and_thin_ladders_are_underidentified():
    rec = MD.market_distribution("rushing_yards", [{"threshold": 50, "yes_bid": 0.10, "yes_ask": 0.90}])
    assert rec["identification"] == MD.NONE and rec["n_rungs_excluded"] == 1
    rec = MD.market_distribution("rushing_yards", _rungs([50], [0.55]))
    assert rec["identification"] == MD.UNDERIDENTIFIED and rec["dispersion_source"].startswith("stat prior")
    assert rec["_dist"].check_valid()[0]


def test_hybrid_refuses_without_an_identified_market_and_never_falls_back():
    data = LatticeDistribution.from_cdf(np.clip(np.arange(0, 150) / 100.0, 0, 1))
    assert HD.hybrid(data, None, market_identification=None)["status"] == "UNAVAILABLE"
    under = MD.market_distribution("rushing_yards", _rungs([50], [0.55]))
    assert HD.hybrid(data, under["_dist"], market_identification=under["identification"])["status"] == "UNAVAILABLE"
    full = MD.market_distribution("rushing_yards", _rungs([30, 40, 50, 60, 70], [0.85, 0.65, 0.5, 0.3, 0.1]))
    for structure in (HD.LOCATION_BLEND, HD.MIXTURE):
        h = HD.hybrid(data, full["_dist"], market_identification=full["identification"], w_market=0.7, structure=structure)
        assert h["status"] == "OK" and h["dist"].check_valid()[0]
        # the blend sits between its parents in location
        lo, hi = sorted([data.mean(), full["_dist"].mean()])
        assert lo - 1e-9 <= h["dist"].mean() <= hi + 1e-9


def test_study_decisions_are_the_ones_in_code():
    res = json.load(open(os.path.join(ROOT, "research", "player_engine_v2", "results.json")))
    for stat, r in res["study_a"].items():
        key = DD.STATS.get(stat, stat)
        assert DD.DEFAULT_FAMILY[key] == r["chosen_v2"], f"{stat}: code says {DD.DEFAULT_FAMILY[key]}, study chose {r['chosen_v2']}"
    ws = res["study_b"]["weight_selection"]
    assert ws["selected"] == "market_mono", "the study selected the market; the hybrid must not be presented as a winner"
    assert HD.STUDY_VERDICT.startswith("market_mono selected")
    conf = ws["confirmation_paired_vs_market"]
    best = min((k for k in conf if k.startswith("hyb")), key=lambda k: conf[k]["diff"])
    assert best == f"hyb_{'mix' if HD.DEFAULT_STRUCTURE == HD.MIXTURE else 'loc'}_{HD.DEFAULT_WEIGHT_MARKET}"


def _frame(n_games=8, seed=0):
    """Three filler seasons (the league-prior window) and one test season 2023; every id below refers to 2023."""
    rng = np.random.default_rng(seed)
    rows = []
    for season in (2019, 2020, 2021, 2023):
      for g in range(n_games):
        for team, home in (("H", 1), ("A", 0)):
            qb = "qbH1" if team == "H" else ("qbA1" if g < 4 else "qbA2")
            gid = f"g{g}" if season == 2023 else f"{season}g{g}"
            rows.append({"player_id": qb, "position": "QB", "team": team, "game_id": gid, "season": season, "week": g + 1, "home": home,
                         "attempts": 33.0, "carries": 3.0, "targets": 0.0, "receptions": 0.0, "receiving_yards": 0.0, "passing_yards": 250.0,
                         "rushing_yards": 10.0, "offense_snaps": 60.0, "any_td": 0.0})
            for i in range(3):
                rows.append({"player_id": f"{team}wr{i}", "position": "WR", "team": team, "game_id": gid, "season": season, "week": g + 1, "home": home,
                             "attempts": 0.0, "carries": 1.0, "targets": float(rng.poisson(7)), "receptions": 4.0, "receiving_yards": float(rng.normal(55, 20)),
                             "passing_yards": 0.0, "rushing_yards": 5.0, "offense_snaps": float(rng.integers(40, 60)), "any_td": 0.0})
    return pd.DataFrame(rows)


def test_v2_features_are_prior_only_no_same_row_leakage_and_detect_qb_changes():
    df = _frame()
    f0 = add_v2_features(df)
    own = [c for c in V2_FEATURES if c not in ("n_prior", "shrink_w")]        # those two come from the v1 EWMA pass
    assert all(c in f0.columns for c in own)
    df2 = df.copy()
    idx = df2.index[(df2.player_id == "Hwr1") & (df2.game_id == "g5")][0]
    df2.loc[idx, ["targets", "receiving_yards", "offense_snaps"]] = [40.0, 300.0, 70.0]
    f1 = add_v2_features(df2)
    for c in own:
        assert f0.loc[idx, c] == pytest.approx(f1.loc[idx, c]), f"{c} moved when the row's own outcome changed"
    later = f1.index[(f1.player_id == "Hwr1") & (f1.game_id == "g6")][0]
    assert f1.loc[later, "ewma_target_share"] > f0.loc[later, "ewma_target_share"], "the NEXT game does see the change"
    # team A changed quarterback between g3 and g4: the flag is on the game after the change is observed
    chg = f0[(f0.team == "A") & (f0.season == 2023)].groupby("game_id")["qb_changed_recent"].first()
    assert chg["g5"] == 1.0 and chg["g2"] == 0.0


def test_lattice_mixture_and_shift_keep_validity():
    a = LatticeDistribution.from_cdf(np.clip(np.arange(0, 80) / 60.0, 0, 1))
    b = LatticeDistribution.from_cdf(np.clip(np.arange(0, 80) / 40.0, 0, 1))
    m = a.mixture(b, 0.3)
    assert m.check_valid()[0] and m.mean() == pytest.approx(0.3 * a.mean() + 0.7 * b.mean(), rel=1e-6)
    s = a.shifted_to_mean(20.0)
    assert s.check_valid()[0] and abs(s.mean() - 20.0) < 1.0
