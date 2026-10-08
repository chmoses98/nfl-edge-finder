"""Football Signal Discovery Lab, Wave 1 (NFL): integrity / leakage tests.

Synthetic data only (no nflverse download needed). Proves that:
  * the opponent-adjusted snapshot for week W uses only games strictly before W (doctoring week W and later
    leaves every week-W feature unchanged; doctoring an earlier week changes it);
  * no current-season full-season statistic is used (appending future weeks changes nothing earlier);
  * the feature modules cannot import the market or outcome modules, and never name a line/odds column;
  * the schedule fields a game row reads exclude every line / odds / score column;
  * Kalshi ladder medians, identity resolution, fee and the evaluator arithmetic behave as specified;
  * the runner refuses hypothesis files that are not registered in the protocol.
"""

from __future__ import annotations

import ast
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from nfl_edge.signal_discovery import game_features as G
from nfl_edge.signal_discovery import markets as M
from nfl_edge.signal_discovery import stats
from nfl_edge.signal_discovery.evaluate_game import ats_summary, build_rows, side_rows, season_norms

ROOT = Path(__file__).resolve().parents[1]
PKG = ROOT / "nfl_edge" / "signal_discovery"
TEAMS = [f"T{i:02d}" for i in range(16)]


def _metric_table(seed=7, seasons=(2019, 2020), weeks=10):
    rng = np.random.default_rng(seed)
    strength = {t: rng.normal(0, 0.1) for t in TEAMS}
    rows = []
    for s in seasons:
        for w in range(1, weeks + 1):
            order = rng.permutation(TEAMS)
            for i in range(0, len(order), 2):
                h, a = order[i], order[i + 1]
                gid = f"{s}_{w:02d}_{a}_{h}"
                for team, opp, hs in ((h, a, 1.0), (a, h, -1.0)):
                    row = {"game_id": gid, "season": s, "week": w, "team": team, "opp": opp, "home_sign": hs}
                    for m in G.METRICS:
                        row[m] = float(strength[team] - strength[opp] + rng.normal(0, 0.05) + (60 if m == "plays" else 0))
                    rows.append(row)
    return pd.DataFrame(rows)


def _schedule(mt):
    g = mt[mt["home_sign"] == 1.0][["game_id", "season", "week", "team", "opp"]].rename(columns={"team": "home_team", "opp": "away_team"})
    g = g.assign(game_type="REG", gameday="2020-01-01", gametime="13:00", location="Home", home_rest=7, away_rest=7, div_game=0,
                 roof="outdoors", surface="grass", spread_line=99.0, total_line=999.0, home_score=99, away_score=0)
    return g.reset_index(drop=True)


LAMS = {m: 8.0 for m in G.METRICS}


def test_snapshot_uses_only_strictly_earlier_games():
    mt = _metric_table()
    sched = _schedule(mt)
    base = G.game_rows(mt, sched, [2020], {2020: LAMS})
    wk = base[base["week"] == 5].set_index("game_id")
    doctored = mt.copy()
    later = (doctored["season"] == 2020) & (doctored["week"] >= 5)
    for m in G.METRICS:
        doctored.loc[later, m] = doctored.loc[later, m] * 5 + 3
    again = G.game_rows(doctored, sched, [2020], {2020: LAMS}).set_index("game_id")
    cols = [c for c in wk.columns if c.startswith(("net.", "mx_", "q_", "env.", "baseline."))]
    pd.testing.assert_frame_equal(wk[cols].sort_index(), again.loc[wk.index, cols].sort_index())
    # non-vacuous: doctoring week 3 DOES move week-5 features
    early = doctored.copy()
    early.loc[(early["season"] == 2020) & (early["week"] == 3) & (early["team"] == "T00"), "epa_play"] += 1.0
    moved = G.game_rows(early, sched, [2020], {2020: LAMS}).set_index("game_id")
    assert not np.allclose(wk["net.epa_play"].to_numpy(float), moved.loc[wk.index, "net.epa_play"].to_numpy(float))


def test_appending_future_season_changes_nothing_earlier():
    mt = _metric_table()
    sched = _schedule(mt)
    a = G.game_rows(mt, sched, [2020], {2020: LAMS})
    fut = _metric_table(seed=9, seasons=(2021,))
    b = G.game_rows(pd.concat([mt, fut], ignore_index=True), pd.concat([sched, _schedule(fut)], ignore_index=True), [2020], {2020: LAMS})
    cols = [c for c in a.columns if c.startswith(("net.", "mx_"))]
    pd.testing.assert_frame_equal(a[cols].reset_index(drop=True), b[cols].reset_index(drop=True))


def test_game_rows_never_read_lines_or_scores():
    assert not any(k in G.SCHEDULE_FIELDS for k in ("spread_line", "total_line", "home_moneyline", "away_moneyline",
                                                    "home_spread_odds", "over_odds", "home_score", "away_score", "result", "total"))
    mt = _metric_table()
    rows = G.game_rows(mt, _schedule(mt), [2020], {2020: LAMS})
    assert not any(c in rows.columns for c in ("spread_line", "total_line", "home_score", "result"))
    assert 99.0 not in rows.select_dtypes("number").to_numpy()  # the poisoned line value never appears


def _imports(path: Path) -> set[str]:
    tree = ast.parse(path.read_text())
    out = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom) and node.module:
            out.add(node.module)
        elif isinstance(node, ast.Import):
            out.update(a.name for a in node.names)
    return out


@pytest.mark.parametrize("module", ["game_features.py", "player_features.py"])
def test_feature_modules_cannot_reach_markets_or_outcomes(module):
    imports = _imports(PKG / module)
    assert not any(m.endswith(("markets", "outcomes", "evaluate_game", "evaluate_props")) or "kalshi" in m for m in imports)
    tree = ast.parse((PKG / module).read_text())
    docs = {id(n.body[0].value) for n in ast.walk(tree)
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.ClassDef)) and n.body and isinstance(n.body[0], ast.Expr)}
    strings = [n.value for n in ast.walk(tree) if isinstance(n, ast.Constant) and isinstance(n.value, str) and id(n) not in docs]
    assert not any(b in s for s in strings for b in ("spread_line", "total_line", "moneyline", "_odds", "yes_ask"))


def test_player_features_reuse_point_in_time_primitive():
    # decayed_prior_sums never includes the row itself: perturbing a row's outcome leaves its own feature unchanged
    from nfl_edge.sim.features import decayed_prior_sums

    g = np.array(["a"] * 5)
    s = np.array([2020] * 5)
    X = np.arange(5, dtype=float)[:, None]
    S1, N1, _ = decayed_prior_sums(g, None, s, X, 3.0, 0.5)
    X2 = X.copy()
    X2[3, 0] = 1e6
    S2, _, _ = decayed_prior_sums(g, None, s, X2, 3.0, 0.5)
    assert S1[3, 0] == S2[3, 0] and S1[4, 0] != S2[4, 0]


def test_ladder_median_interpolates_and_refuses_to_extrapolate():
    assert M.ladder_median([(50.5, 0.7), (60.5, 0.5), (70.5, 0.3)]) == pytest.approx(60.5)
    assert M.ladder_median([(40.0, 0.8), (60.0, 0.4)]) == pytest.approx(55.0)
    assert M.ladder_median([(40.0, 0.4), (60.0, 0.2)]) is None


def test_quote_validity_and_fee():
    assert M._valid(0.45, 0.50) and not M._valid(0.30, 0.50) and not M._valid(0.0, 0.05) and not M._valid(0.5, 1.0)
    assert M.kalshi_fee(0.50) == pytest.approx(0.02)
    assert M.kalshi_fee(0.95) == pytest.approx(0.01)


def test_under_is_never_derived_from_over_when_no_ask_is_captured():
    agg = {"KXNFLRECYDS-X": {"family": "PLAYER_STAT", "stat": "receiving_yards", "game_id": "2026_03_A_B", "team": "B",
                             "player_name": "A Player", "player_kalshi_id": "k", "threshold": 50, "operator": ">=",
                             "kickoff_utc": "2026-09-20T17:00:00Z", "last_pre_q": (0.55, 0.52, 0.50, 0.45, 30.0)}}
    r = M.kalshi_2026(agg).iloc[0]
    assert r["no_ask"] == 0.52 and r["no_ask"] != 1 - r["yes_ask"]


def test_identity_never_joins_on_display_name_alone_when_team_disagrees(monkeypatch):
    roster = pd.DataFrame({"gsis_id": ["g1", "g2"], "full_name": ["Josh Allen", "Josh Allen"], "team": ["BUF", "JAX"],
                           "jersey_number": [17, 41], "position": ["QB", "LB"]})
    roster["name_key"] = roster["full_name"].map(M._norm_name)
    monkeypatch.setattr(M, "_roster", lambda season: roster)
    res = M.Resolver(2026)
    assert res.resolve("Josh Allen", "BUF", None) == ("g1", "RESOLVED_NAME_TEAM")
    assert res.resolve("Josh Allen", "KC", None)[0] is None  # ambiguous, no team match -> unresolved


def test_evaluator_orientation_and_arithmetic():
    s = ats_summary([3.0, -1.0, 0.0, 2.5])
    assert (s["covers"], s["losses"], s["pushes"]) == (2, 1, 1)
    feats = [{"game_id": "g", "season": 2020, "week": 3, "game_type": "REG", "home_team": "H", "away_team": "A", "neutral": False,
              "div_game": False, "net.epa_play": -0.2, "baseline.total": 44.0, "baseline.home_margin": -4.0, "mx_home.points": 20.0,
              "control_side": "away", "control_strength": "STRONG"}]
    lines = {"g": {"spread_home": 3.0, "total": 45.0, "ml_home_novig": 0.4, "home_ml": 140, "away_ml": -160}}
    outs = {"g": {"status": "OK", "home_points": 10.0, "away_points": 20.0, "home_margin": -10.0, "total_points": 30.0,
                  "home_1h": 3.0, "away_1h": 10.0, "overtime": False}}
    rows, _ = build_rows(feats, lines, outs)
    sr = side_rows(rows, {"population": {"rule": "control", "strength": "STRONG"}, "side": "control"}, season_norms(rows))[0]
    assert sr["side"] == "away" and sr["margin"] == 10.0 and sr["spread_s"] == -3.0 and sr["ats_resid"] == 7.0
    assert rows[0]["total_resid"] == -15.0


def test_bh_and_bootstrap_are_deterministic():
    assert stats.benjamini_hochberg([0.01, 0.5])[0] == pytest.approx(0.02)
    assert stats.bootstrap_mean_ci(list(range(50))) == stats.bootstrap_mean_ci(list(range(50)))


def test_runner_refuses_unregistered_hypotheses(tmp_path):
    import importlib.util

    spec = importlib.util.spec_from_file_location("sdw1", ROOT / "scripts" / "research" / "signal_discovery_wave1.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    p = tmp_path / "h.json"
    p.write_text(json.dumps({"tampered": True}))
    with pytest.raises(SystemExit):
        mod.check_frozen(p)
