"""Regression tests for the two verified structural defects in the player mean projection (research/mean_defect)."""
import numpy as np
import pandas as pd

from nfl_edge.research import player_distributions as pdist
from nfl_edge.shadow import challenger as C


def _games(player="P1", seasons=(2025, 2026), weeks=(1, 2, 3, 4), targets=None):
    rows = []
    for s in seasons:
        for w in weeks:
            rows.append(dict(player_id=player, position="WR", season=s, week=w, game_id=f"{s}_{w:02d}_A_B", team="A",
                             opponent_team="B", targets=4.0 if targets is None else targets.get((s, w), 4.0),
                             receptions=2.0, receiving_yards=30.0, receiving_tds=0.0, completions=0.0, attempts=0.0,
                             passing_yards=0.0, passing_tds=0.0, passing_interceptions=0.0, carries=0.0, rushing_yards=0.0,
                             rushing_tds=0.0, any_td=0.0, touches=4.0, offense_snaps=50.0))
    return pd.DataFrame(rows)


def test_season_boundary_inflates_shrink_w_for_veterans_but_not_thinness():
    """D2: shrink_w is a calendar variable (the EWMA halves at the boundary); sample_thinness reads the player's own sample."""
    df = _games(seasons=tuple(range(2016, 2027)), weeks=tuple(range(1, 13)))
    f = pdist.add_ewma_features(df, halflife=6.0, season_carry=0.35, shrink_k=2.0)
    early = f[(f.season == 2026) & (f.week == 1)].iloc[0]
    late = f[(f.season == 2025) & (f.week == 12)].iloc[0]
    assert early.shrink_w > 1.2 * late.shrink_w            # the veteran "looks thin" in week 1
    th = C.sample_thinness(f)
    assert th[(f.season == 2026) & (f.week == 1)][0] < 0.2  # ... but his own sample is not thin
    assert abs(th[(f.season == 2026) & (f.week == 1)][0] - th[(f.season == 2025) & (f.week == 12)][0]) < 1e-9


def _toy(n=600, seed=0):
    rng = np.random.default_rng(seed)
    df = pd.DataFrame(dict(ewma_receptions=rng.uniform(1, 6, n), ewma_targets=rng.uniform(2, 9, n), implied_total=rng.normal(22, 3, n),
                           home=rng.integers(0, 2, n).astype(bool), shrink_w=rng.uniform(.3, .5, n), n_prior=rng.integers(0, 80, n)))
    df["receptions"] = rng.poisson(df.ewma_receptions)
    return df


def test_frozen_code_is_untouched_and_v2_lives_only_inside_the_context():
    spec = pdist.STAT_SPECS["receptions"]
    df = _toy()
    orig = (pdist._design, pdist.fit_mean_model, pdist.predict_mean)
    m1 = pdist.fit_mean_model(df, spec, "receptions", "count")
    assert len(m1) == 5                                   # the frozen model tuple, no marker
    with C.count_design_v2():
        m2 = pdist.fit_mean_model(df, spec, "receptions", "count")
        assert m2[5] == "v2"
        p2 = pdist.predict_mean(m2, df, spec, "receptions", .1)
    assert (pdist._design, pdist.fit_mean_model, pdist.predict_mean) == orig       # fully restored
    assert not np.allclose(pdist.predict_mean(m1, df, spec, "receptions", .1), p2)
    assert np.allclose(pdist.predict_mean(m1, df, spec, "receptions", .1), pdist.predict_mean(pdist.fit_mean_model(df, spec, "receptions", "count"), df, spec, "receptions", .1))


def test_v2_only_applies_to_count_specs():
    spec = pdist.STAT_SPECS["receiving_yards"]  # yards -> unchanged
    df = pd.DataFrame(dict(ewma_receiving_yards=[20., 40., 60., 30.] * 50, ewma_targets=[3., 5., 7., 4.] * 50, implied_total=[22.] * 200,
                           home=[True, False] * 100, shrink_w=[.4] * 200, n_prior=[30] * 200, receiving_yards=[25., 44., 58., 33.] * 50))
    with C.count_design_v2():
        assert len(pdist.fit_mean_model(df, spec, "receiving_yards", "yards")) == 5


def test_pit_history_keeps_completed_games_and_drops_the_slate():
    """D1: completed games of the target season must reach the features; the slate's own rows must not."""
    hist = _games(seasons=(2025, 2026), weeks=(1, 2, 3, 4))
    up = pd.DataFrame([dict(player_id="P1", season=2026, week=3, game_id="2026_03_A_B")])
    kept = C.pit_history(hist, up, 2026)
    assert set(kept[kept.season == 2026].week) == {1, 2}
    assert len(kept[kept.season == 2025]) == 4


def test_current_season_games_move_the_ewma_only_with_the_repair():
    big = {(2026, 1): 12.0, (2026, 2): 12.0}
    hist = _games(seasons=(2025, 2026), weeks=(1, 2, 3, 4), targets=big)
    up = pd.DataFrame([dict(player_id="P1", position="WR", season=2026, week=3, game_id="2026_03_A_B", team="A", opponent_team="B",
                            spread_line=-3.0, total_line=45.0, home=True, indoor=False, qb_starter=False)])
    from nfl_edge.shadow.prospective import build_prospective_rows
    old = build_prospective_rows(hist[hist.season < 2026], up)
    new = build_prospective_rows(C.pit_history(hist, up, 2026), up)
    kw = dict(halflife=6.0, season_carry=0.35, shrink_k=2.0)
    f_old = pdist.add_ewma_features(old, **kw); f_new = pdist.add_ewma_features(new, **kw)
    pick = lambda f, c: f[f.is_prospective == True][c].iloc[0]   # noqa: E712
    assert pick(f_new, "ewma_targets") > pick(f_old, "ewma_targets") + 1.5     # two 12-target games now count
    assert pick(f_new, "shrink_w") < pick(f_old, "shrink_w")


def test_challenger_install_extends_history_and_restores_nothing_for_the_incumbent_module():
    import types
    pricer = types.SimpleNamespace(build_prospective_rows=lambda hist, up: hist)
    pricer._CHALLENGER_TARGET = 2026
    seen = {}
    orig_load, orig = pdist.load_player_games, (pdist._design, pdist.fit_mean_model, pdist.predict_mean)
    pdist.load_player_games = lambda root, seasons, *a, **k: seen.setdefault("seasons", list(seasons)) or pd.DataFrame()
    try:
        C.install(pricer)
        pdist.load_player_games("root", range(2013, 2026))      # exactly what the incumbent pricer asks for
        assert seen["seasons"][-1] == 2026                       # the challenger also loads the target season
    finally:
        pricer._challenger_stack.close()
        pdist.load_player_games = orig_load
    assert (pdist._design, pdist.fit_mean_model, pdist.predict_mean) == orig


def test_challenger_pricer_script_wires_the_frozen_pricer_without_editing_it():
    import importlib.util, os, sys
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    spec = importlib.util.spec_from_file_location("price_slate_challenger", os.path.join(root, "scripts", "shadow", "price_slate_challenger.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    orig = (pdist._design, pdist.fit_mean_model, pdist.predict_mean, pdist.load_player_games)
    try:
        import pytest
        with pytest.raises(SystemExit) as e:
            mod.main(["--help"])
        assert e.value.code == 0
        assert pdist.fit_mean_model is not orig[1]          # patched for the life of the challenger process
    finally:
        sys.modules["_frozen_price_slate"]._challenger_stack.close()
        pdist.load_player_games = orig[3]
    assert (pdist._design, pdist.fit_mean_model, pdist.predict_mean) == orig[:3]
