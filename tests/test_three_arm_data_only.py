"""DATA_ONLY cannot see the market, the future, or a later-season rating -- provably, not by convention."""
import ast
import json
import os

import numpy as np
import polars as pl
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from nfl_edge.arms import data_only as D, registry as R  # noqa: E402

ART = os.path.join(ROOT, "research", "three_arm", "data_only_artifact_2026.json")
FEAT = os.path.join(ROOT, "research", "game_model", "game_features.parquet")


def synthetic_team_games(seed=0, seasons=(2023, 2024, 2025), weeks=18):
    """A small league of 8 teams with the silver columns the ratings solver reads."""
    rng = np.random.default_rng(seed)
    teams = ["A", "B", "C", "D", "E", "F", "G", "H"]
    strength = {t: rng.normal(0, 0.1) for t in teams}
    rows = []
    for s in seasons:
        for w in range(1, weeks + 1):
            order = list(teams); rng.shuffle(order)
            for i in range(0, 8, 2):
                h, a = order[i], order[i + 1]
                gid = f"{s}_{w:02d}_{a}_{h}"
                for team, opp, is_home in ((h, a, True), (a, h, False)):
                    base = strength[team] - strength[opp] + (0.03 if is_home else -0.03)
                    rows.append({"season": s, "week": w, "game_id": gid, "team": team, "opp": opp, "is_home": is_home,
                                 "season_type": "REG", "off_epa_play": base + rng.normal(0, 0.15),
                                 "off_success_rate": 0.45 + base + rng.normal(0, 0.05), "off_dropback_epa": base + rng.normal(0, 0.2),
                                 "off_rush_epa": base + rng.normal(0, 0.15), "off_epa_play_ng": base + rng.normal(0, 0.15),
                                 "off_explosive_passes": rng.poisson(5), "off_explosive_runs": rng.poisson(3), "off_plays": 60,
                                 "off_sacks": rng.poisson(2), "off_dropbacks": 35, "off_turnovers": rng.poisson(1.3),
                                 "off_proe_early_ng": rng.normal(0, 5), "st_epa_for": rng.normal(0, 1), "off_early_down_epa": base + rng.normal(0, 0.15)})
    return pl.DataFrame(rows)


@pytest.fixture(scope="module")
def artifact():
    return D.DataOnlyArtifact.load(ART)


def test_the_frozen_artifact_trains_only_on_seasons_before_2026(artifact):
    assert artifact.target_season == 2026 and artifact.train_seasons == [2018, 2025]
    assert artifact.training_source["file"].startswith("research/game_model/")


def test_the_frozen_artifact_is_reproducible_from_the_frozen_features(artifact):
    """The same code on the same frozen features refits the same model.

    "Same" is numerical, not bitwise: the ridge solve goes through LAPACK, whose result differs in the last
    few ulps between BLAS builds and CPUs. The first CI run of this test refit a coefficient vector whose
    16-hex sha differed from the frozen one while every number agreed to far better than 1e-9. The sha is the
    identity of the frozen FILE (checked against its own content below, and pinned by the manifest of every
    snapshot); the refit is checked as a model: identical structure, and parameters and training-set
    predictions within 1e-9 of the frozen ones.
    """
    feats = pl.read_parquet(FEAT)
    refit = D.fit_artifact(feats, 2026)
    for key in ("version", "target_season", "train_seasons", "margin_features", "total_features",
                "n_train_games", "rating_hyperparams"):
        assert getattr(refit, key) == getattr(artifact, key), key
    for name in ("margin_model", "total_model"):
        got, want = getattr(refit, name), getattr(artifact, name)
        assert got["lam"] == want["lam"]
        for part in ("beta", "xm", "xs", "ym"):
            np.testing.assert_allclose(got[part], want[part], rtol=1e-9, atol=1e-9, err_msg=f"{name}.{part}")
    tr = feats.filter((pl.col("season") < 2026) & (pl.col("season") >= 2026 - D.TRAIN_WINDOW_SEASONS))
    for name, cols in (("margin_model", D.MARGIN_FEATURES), ("total_model", D.TOTAL_FEATURES)):
        X = tr.select([pl.col(c).cast(pl.Float64).fill_null(0.0).fill_nan(0.0) for c in cols]).to_numpy()
        np.testing.assert_allclose(D.ridge_pred(getattr(refit, name), X), D.ridge_pred(getattr(artifact, name), X),
                                   rtol=0, atol=1e-9, err_msg=name)
    assert artifact.sha() == json.load(open(ART))["artifact_sha"]


def test_the_design_matrix_is_a_whitelist_and_refuses_every_market_column():
    for bad in ("spread_line", "total_line", "home_moneyline", "yes_ask", "mid", "implied_total", "kalshi_spread"):
        with pytest.raises(D.MarketLeak):
            D.attest_market_free(D.MARGIN_FEATURES + [bad])
    with pytest.raises(D.MarketLeak):
        D.attest_market_free(D.TOTAL_FEATURES + ["anything_not_whitelisted"])
    assert D.attest_market_free(D.MARGIN_FEATURES + D.TOTAL_FEATURES)["attested"] is True


def test_poisoning_every_market_column_changes_nothing(artifact):
    row = {"game_id": "x", "home_rest": 7, "away_rest": 10, "div_game": 1, "location": "Home", "roof": "dome",
           "spread_line": 3.0, "total_line": 44.5, "home_moneyline": -150, "away_moneyline": 130}
    tg = synthetic_team_games()
    ratings, _ = D.ratings_for_week(D.prepare_team_games(tg), 2025, 10)
    mf, dropped = D.market_free_schedule(pl.DataFrame([row]))
    assert set(dropped) == {"spread_line", "total_line", "home_moneyline", "away_moneyline"}
    clean = D.project_game(artifact, ratings, mf.to_dicts()[0], "A", "B")
    poisoned_row = dict(row, spread_line=-40.0, total_line=99.0, home_moneyline=9999)
    mf2, _ = D.market_free_schedule(pl.DataFrame([poisoned_row]))
    poisoned = D.project_game(artifact, ratings, mf2.to_dicts()[0], "A", "B")
    assert clean["projected_home_margin"] == poisoned["projected_home_margin"]
    assert clean["projected_total"] == poisoned["projected_total"]
    with pytest.raises(D.MarketLeak):
        D.project_game(artifact, ratings, row, "A", "B")           # a row that still carries market columns is refused


def test_future_games_cannot_reach_a_rating():
    tg = synthetic_team_games()
    rows = D.prepare_team_games(tg)
    base, _ = D.ratings_for_week(rows, 2025, 10)
    future = tg.with_columns([pl.when((pl.col("season") > 2025) | ((pl.col("season") == 2025) & (pl.col("week") >= 10)))
                              .then(pl.col(c) + 50.0).otherwise(pl.col(c)).alias(c)
                              for c in ("off_epa_play", "off_success_rate", "off_dropback_epa", "off_rush_epa", "st_epa_for")])
    after, _ = D.ratings_for_week(D.prepare_team_games(future), 2025, 10)
    assert base == after
    # and the same through the timestamp cutoff: only games in the allowed set count
    allowed = set(tg.filter((pl.col("season") < 2025) | (pl.col("week") < 10))["game_id"].to_list())
    cut, _ = D.ratings_at_cutoff(D.prepare_team_games(future), 2025, allowed)
    assert cut == base


def test_a_later_season_rating_cannot_be_used_for_an_earlier_season():
    tg = synthetic_team_games(seasons=(2023, 2024, 2025, 2026))
    rows = D.prepare_team_games(tg)
    r24, _ = D.ratings_for_week(rows, 2024, 5)
    rows_no26 = D.prepare_team_games(tg.filter(pl.col("season") < 2026))
    r24b, _ = D.ratings_for_week(rows_no26, 2024, 5)
    assert r24 == r24b


def test_final_games_before_the_cutoff_exclude_games_in_progress_or_without_a_result():
    from datetime import datetime, timezone
    games = pl.DataFrame([
        {"game_id": "done", "gameday": "2026-09-13", "gametime": "13:00", "result": 3, "total": 40, "overtime": 0},
        {"game_id": "playing", "gameday": "2026-09-13", "gametime": "16:25", "result": 3, "total": 40, "overtime": 0},
        {"game_id": "scheduled", "gameday": "2026-09-14", "gametime": "20:15", "result": None, "total": None, "overtime": None}])
    ids, meta = D.final_game_ids_before(games, datetime(2026, 9, 13, 22, 0, tzinfo=timezone.utc))
    assert ids == {"done"}
    assert meta["latest_included_kickoff_utc"] == "2026-09-13T17:00:00+00:00"


def test_a_missing_rating_is_unavailable_never_a_market_fallback(artifact):
    tg = synthetic_team_games()
    ratings, _ = D.ratings_for_week(D.prepare_team_games(tg), 2025, 10)
    row = {"home_rest": 7, "away_rest": 7, "div_game": 0, "location": "Home", "roof": "outdoors"}
    pj = D.project_game(artifact, ratings, row, "A", "ZZZ")
    assert pj["status"] == R.UNAVAILABLE and "projected_home_margin" not in pj


def test_the_module_source_never_references_a_market_column_in_code():
    """Outside the deny-list literal itself, no name, attribute or string in data_only.py is a market column."""
    src = open(os.path.join(ROOT, "nfl_edge", "arms", "data_only.py")).read()
    tree = ast.parse(src)
    forbidden = set(D.FORBIDDEN_INPUT_COLUMNS)
    hits = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "FORBIDDEN_INPUT_COLUMNS" for t in node.targets):
            continue
        if isinstance(node, ast.Constant) and isinstance(node.value, str) and node.value in forbidden:
            hits.append((node.lineno, node.value))
        if isinstance(node, (ast.Name,)) and node.id in forbidden:
            hits.append((node.lineno, node.id))
        if isinstance(node, ast.Attribute) and node.attr in forbidden:
            hits.append((node.lineno, node.attr))
    # the deny-list assignment is the only legitimate place for these strings
    assign_lines = {n.lineno for n in ast.walk(tree) if isinstance(n, ast.Assign)
                    and any(isinstance(t, ast.Name) and t.id == "FORBIDDEN_INPUT_COLUMNS" for t in n.targets)}
    span = set()
    for n in ast.walk(tree):
        if isinstance(n, ast.Assign) and n.lineno in assign_lines:
            span.update(range(n.lineno, (n.end_lineno or n.lineno) + 1))
    hits = [h for h in hits if h[0] not in span]
    assert not hits, f"market columns referenced in DATA_ONLY code: {hits}"


def test_the_sign_convention_is_home_minus_away(artifact):
    """A stronger home side must raise the projected HOME margin, exactly as the incumbent's spread_home."""
    tg = synthetic_team_games()
    ratings, _ = D.ratings_for_week(D.prepare_team_games(tg), 2025, 10)
    row = {"home_rest": 7, "away_rest": 7, "div_game": 0, "location": "Home", "roof": "outdoors"}
    strong = dict(ratings["A"]); weak = dict(ratings["B"])
    for f in D.FEATS:
        strong[f"off_{f}"] = weak[f"off_{f}"] + 0.3
    pj_home = D.project_game(artifact, {"A": strong, "B": weak}, row, "A", "B")
    pj_away = D.project_game(artifact, {"A": strong, "B": weak}, row, "B", "A")
    assert pj_home["projected_home_margin"] > pj_away["projected_home_margin"]
