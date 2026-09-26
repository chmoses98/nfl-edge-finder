"""starter-regime-0.1.0 (DATA_ONLY_SRA): research-only, point-in-time, and unreachable from the report path."""
import os
import re
import sys

import numpy as np
import polars as pl
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.research import starter_regime as SR  # noqa: E402
from nfl_edge.research.team_ratings import solve_ratings  # noqa: E402

TEAMS = ["AAA", "BBB", "CCC", "DDD", "EEE", "FFF", "GGG", "HHH"]
HP = {"halflife_games": 10.0, "season_carry": 0.4, "ridge": 4.0}
METRICS = {"epa": "off_epa_play", "st_epa": "st_epa_for"}


def synthetic_rows(weeks=10, seed=0):
    rng = np.random.default_rng(seed)
    recs = []
    for wk in range(1, weeks + 1):
        order = list(rng.permutation(TEAMS))
        for i in range(0, len(order), 2):
            h, a = order[i], order[i + 1]
            gid = f"2026_{wk:02d}_{a}_{h}"
            for team, opp, home in ((h, a, True), (a, h, False)):
                recs.append({"season": 2026, "week": wk, "week_no": wk, "game_id": gid, "team": team, "opp": opp,
                             "is_home": home, "off_epa_play": float(rng.normal(0, 0.15)),
                             "st_epa_for": float(rng.normal(0, 1.0))})
    return pl.DataFrame(recs)


def test_identical_to_production_solver_without_weights():
    rows = synthetic_rows()
    a = solve_ratings(rows, "off_epa_play", cur_season=2026, **HP)
    b = SR.solve_ratings_weighted(rows, "off_epa_play", cur_season=2026, **HP)
    assert a["ratings"].keys() == b["ratings"].keys()
    for t in a["ratings"]:
        assert a["ratings"][t] == pytest.approx(b["ratings"][t], abs=1e-12)
    assert a["hfa"] == pytest.approx(b["hfa"], abs=1e-12)


def test_w_regime_one_is_a_no_op():
    rows = synthetic_rows()
    allowed = set(rows["game_id"].to_list())
    starters = {(g, t): f"QB_{t}_OLD" for g, t in zip(rows["game_id"], rows["team"])}
    proj = {t: f"QB_{t}_NEW" for t in TEAMS}
    r1, _ = SR.ratings_at_cutoff_sra(rows, 2026, allowed, starters, proj, 1.0, METRICS, HP)
    for t in TEAMS:
        o, d = solve_ratings(rows, "off_epa_play", cur_season=2026, **HP)["ratings"][t]
        assert r1[t]["off_epa"] == pytest.approx(o, abs=1e-12)
        assert r1[t]["def_epa"] == pytest.approx(d, abs=1e-12)


def test_only_the_changed_team_offence_rows_are_downweighted():
    rows = synthetic_rows()
    allowed = set(rows["game_id"].to_list())
    starters = {(g, t): f"QB_{t}" for g, t in zip(rows["game_id"], rows["team"])}
    for g, t in starters:                      # AAA's first five weeks were started by a different QB
        if t == "AAA" and int(g[5:7]) <= 5:
            starters[(g, t)] = "QB_AAA_BACKUP"
    proj = {t: f"QB_{t}" for t in TEAMS}
    out, audit = SR.regime_weights(rows, allowed, starters, proj, 0.25)
    w = dict(zip(zip(out["game_id"], out["team"]), out["regime_w"]))
    assert all(v == 0.25 for (g, t), v in w.items() if t == "AAA" and int(g[5:7]) <= 5)
    assert all(v == 1.0 for (g, t), v in w.items() if not (t == "AAA" and int(g[5:7]) <= 5))
    assert sorted(audit["downweighted"]) == ["AAA"] and len(audit["downweighted"]["AAA"]) == 5


def test_special_teams_is_never_regime_weighted():
    rows = synthetic_rows()
    allowed = set(rows["game_id"].to_list())
    starters = {(g, t): "OLD" for g, t in zip(rows["game_id"], rows["team"])}
    proj = {t: "NEW" for t in TEAMS}
    r0, meta = SR.ratings_at_cutoff_sra(rows, 2026, allowed, starters, proj, 0.0, METRICS, HP)
    st = solve_ratings(rows, "st_epa_for", cur_season=2026, **HP)["ratings"]
    assert meta["metrics"]["st_epa"]["regime_weighted"] is False
    for t in TEAMS:
        assert r0[t]["off_st_epa"] == pytest.approx(st[t][0], abs=1e-12)


def test_unknown_projected_starter_means_no_adjustment():
    rows = synthetic_rows()
    allowed = set(rows["game_id"].to_list())
    starters = {(g, t): "OLD" for g, t in zip(rows["game_id"], rows["team"])}
    out, audit = SR.regime_weights(rows, allowed, starters, {}, 0.0)
    assert set(out["regime_w"].to_list()) == {1.0}
    assert audit["teams_without_projected_starter"] == sorted(TEAMS)


def test_rows_after_the_cutoff_are_refused():
    rows = synthetic_rows()
    allowed = {g for g in rows["game_id"].to_list() if int(g[5:7]) <= 8}
    with pytest.raises(SR.LeakageError):
        SR.regime_weights(rows, allowed, {}, {}, 0.5)


def test_starters_for_games_after_the_cutoff_are_refused():
    rows = synthetic_rows()
    allowed = {g for g in rows["game_id"].to_list() if int(g[5:7]) <= 8}
    prior = rows.filter(pl.col("game_id").is_in(list(allowed)))
    late = next(g for g in rows["game_id"].to_list() if int(g[5:7]) == 9)
    with pytest.raises(SR.LeakageError):
        SR.regime_weights(prior, allowed, {(late, "AAA"): "X"}, {"AAA": "Y"}, 0.5)


def test_ratings_ignore_post_cutoff_games_entirely():
    """Poison every post-cutoff row: the point-in-time ratings must not move by a bit."""
    rows = synthetic_rows()
    allowed = {g for g in rows["game_id"].to_list() if int(g[5:7]) <= 8}
    starters = {(g, t): "OLD" for g, t in zip(rows["game_id"], rows["team"]) if g in allowed}
    proj = {t: "NEW" for t in TEAMS}
    a, _ = SR.ratings_at_cutoff_sra(rows, 2026, allowed, starters, proj, 0.25, METRICS, HP)
    poisoned = rows.with_columns(pl.when(pl.col("week") > 8).then(99.0).otherwise(pl.col("off_epa_play"))
                                 .alias("off_epa_play"))
    b, _ = SR.ratings_at_cutoff_sra(poisoned, 2026, allowed, starters, proj, 0.25, METRICS, HP)
    assert a == b


def test_starters_from_pbp_never_reads_the_target_game():
    pbp = pl.DataFrame({
        "game_id": ["G1"] * 5 + ["TARGET"] * 5,
        "posteam": ["AAA"] * 10,
        "qb_dropback": [1] * 10,
        "passer_player_id": ["QB_OLD", "QB_OLD", "QB_OLD", "QB_NEW", None, "QB_NEW", "QB_NEW", "QB_NEW", "QB_NEW", "QB_NEW"],
    })
    s = SR.starters_from_pbp(pbp, {"G1"})
    assert s == {("G1", "AAA"): "QB_OLD"}


def test_research_only_and_unreachable_from_the_report_path():
    assert SR.AUTHORITY == "RESEARCH_ONLY" and SR.VERSION == "starter-regime-0.1.0"
    pat = re.compile(r"starter_regime")
    for sub in ("nfl_edge/handicap", "nfl_edge/arms", "nfl_edge/shadow", "nfl_edge/shadow_v2", "nfl_edge/execution",
                "nfl_edge/pricing", "scripts/handicap", "scripts/shadow"):
        base = os.path.join(ROOT, sub)
        for dp, _dn, fns in os.walk(base):
            for fn in fns:
                if fn.endswith(".py"):
                    assert not pat.search(open(os.path.join(dp, fn)).read()), f"{sub}/{fn} imports starter_regime"
