"""GAME SCRIPT V2 (nfl_edge/sim/script_v2.py): the nine-cell lattice, the script x market matrix and thesis
dependency, all read from the SAME simulated rows the contracts are priced from. Synthetic frames only."""
import copy
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.pricing.game_env import ResidualBank  # noqa: E402
from nfl_edge.research import script_autopsy as SA  # noqa: E402
from nfl_edge.sim import script_v2 as V  # noqa: E402
from nfl_edge.sim import simulate as S  # noqa: E402
import sim_fixtures as FX  # noqa: E402


def _bank(seed=1, n=600):
    rng = np.random.default_rng(3)
    return ResidualBank(rng.normal(0, 13, n), rng.normal(0, 13, n), np.repeat([2020, 2021, 2022], n // 3), ref_season=2023,
                        spread_lines=np.where(rng.random(n) < 0.5, 3.0, 2.5), total_lines=np.where(rng.random(n) < 0.5, 44.0, 44.5),
                        overtime=rng.random(n) < 0.06, results=rng.normal(0, 13, n), rng=np.random.default_rng(seed))


@pytest.fixture(scope="module")
def fitted():
    return FX.synthetic_bundle(seed=1)


@pytest.fixture(scope="module")
def sim(fitted):
    b, tf, pf = fitted
    gi = FX.game_input(tf, pf)
    res = S.simulate(gi, b, n=6000, bank=_bank())
    return gi, res


def _snapshot(res):
    return {"margin": res.margin.copy(), "total": res.total.copy(), "hp": np.asarray(res.home_points).copy(),
            "team": {t: {k: np.asarray(v).copy() for k, v in d.items()} for t, d in res.team.items()},
            "player": {p: {k: np.asarray(v).copy() for k, v in d.items() if k != "team"} for p, d in res.player.items()}}


def _same(a, b):
    assert np.array_equal(a["margin"], b["margin"]) and np.array_equal(a["total"], b["total"]) and np.array_equal(a["hp"], b["hp"])
    for t in a["team"]:
        for k in a["team"][t]:
            assert np.array_equal(a["team"][t][k], b["team"][t][k]), (t, k)
    for p in a["player"]:
        for k in a["player"][p]:
            assert np.array_equal(a["player"][p][k], b["player"][p][k]), (p, k)


# ------------------------------------------------------------------------------------------ the lattice
def test_cells_are_exhaustive_and_mutually_exclusive():
    rng = np.random.default_rng(0)
    m = rng.integers(-60, 61, 50000).astype(float); t = rng.integers(0, 110, 50000).astype(float)
    for spread in (-7.5, -0.5, 0.0, 3.0, 13.5):
        c = V.cell_index(m, t, spread, 44.5)
        assert c.min() >= 0 and c.max() < V.N_CELLS
        # exactly one cell per row, by building every cell's membership independently from the rule table
        o = V.orientation(spread); fm = o["sign"] * m
        ctrl = [fm > 8, (fm >= -8) & (fm <= 8), fm < -8]
        scor = [t >= 54.5, (t < 54.5) & (t > 34.5), t <= 34.5]
        member = np.array([ctrl[i] & scor[j] for i in range(3) for j in range(3)])
        assert (member.sum(axis=0) == 1).all()
        assert (np.argmax(member, axis=0) == c).all()


def test_thresholds_are_the_autopsy_thresholds():
    assert (SA.ONE_SCORE, SA.SHOOTOUT_OVER, SA.LOW_SCORING_UNDER, SA.BLOWOUT_MARGIN) == (8, 10, 10, 17)
    s = V.script_v2_summary.__globals__
    assert s["ONE_SCORE"] is SA.ONE_SCORE and s["SHOOTOUT_OVER"] is SA.SHOOTOUT_OVER


def test_probabilities_sum_to_one_and_are_finite(sim):
    gi, res = sim
    out = V.script_v2_summary(res, gi, S.coherence_report(res))
    p = np.array([c["probability"] for c in out["cells"]])
    assert np.isfinite(p).all() and (p >= 0).all()
    assert abs(p.sum() - 1.0) < 1e-12 and abs(out["probability_sum"] - 1.0) < 1e-12
    assert sum(c["n_rows"] for c in out["cells"]) == res.n
    assert [c["cell"] for c in out["cells"]] == list(V.CELLS)
    assert out["provenance"] == "MARKET_CENTRED_GAME" and out["betting_authorized"] is False


def test_scoring_bucket_boundaries():
    T = 44.5
    f = lambda tot: V.classify(14.0, tot, 3.0, T).split("|")[1]
    assert f(T + 10) == "HIGH_SCORING" and f(T + 9) == "NORMAL_SCORING"
    assert f(T - 10) == "LOW_SCORING" and f(T - 9) == "NORMAL_SCORING"
    g = lambda m: V.classify(m, 44.0, 3.0, T).split("|")[0]
    assert g(9) == "FAVORITE_CONTROL" and g(8) == "COMPETITIVE" and g(0) == "COMPETITIVE"
    assert g(-8) == "COMPETITIVE" and g(-9) == "UNDERDOG_CONTROL"


def test_favorite_orientation_flips_home_and_away():
    m = np.array([14.0, -14.0, 3.0]); t = np.array([44.0, 44.0, 44.0])
    home_fav = [V.CELLS[i].split("|")[0] for i in V.cell_index(m, t, 3.5, 44.0)]
    away_fav = [V.CELLS[i].split("|")[0] for i in V.cell_index(m, t, -3.5, 44.0)]
    assert home_fav == ["FAVORITE_CONTROL", "UNDERDOG_CONTROL", "COMPETITIVE"]
    assert away_fav == ["UNDERDOG_CONTROL", "FAVORITE_CONTROL", "COMPETITIVE"]


def test_pickem_is_oriented_on_home_and_says_so(sim):
    gi, res = sim
    gi2 = copy.copy(gi); gi2.spread_home = 0.0
    out = V.script_v2_summary(res, gi2)
    assert out["orientation"]["pickem"] is True and out["orientation"]["favorite"] is None
    assert all(out["marginal_events"][k] is None for k in V.FAVORITE_EVENTS)
    labels = " ".join(c["labels"]["short"] + c["labels"]["long"] for c in out["cells"])
    assert "favourite" not in labels and "underdog" not in labels
    assert V.orientation(0.0)["sign"] == 1


def test_the_summary_draws_no_random_number_and_leaves_the_simresult_unchanged(sim, monkeypatch):
    gi, res = sim
    before = _snapshot(res)
    state = np.random.get_state()

    def boom(*a, **k):
        raise AssertionError("the reporting layer drew a random number")
    for name in ("default_rng", "random", "normal", "binomial", "choice", "poisson", "gamma", "standard_normal"):
        monkeypatch.setattr(np.random, name, boom)
    a = V.script_v2_summary(res, gi, S.coherence_report(res))
    b = V.script_v2_summary(res, gi, S.coherence_report(res))
    monkeypatch.undo()
    assert a == b, "deterministic from fixed rows"
    assert np.random.get_state()[1].tolist() == state[1].tolist()
    _same(before, _snapshot(res))
    assert a["rng_draws"] == 0


def test_labels_are_generated_from_the_cell_state(sim):
    gi, res = sim
    out = V.script_v2_summary(res, gi)
    fav = out["orientation"]["favorite"]
    for c in out["cells"]:
        ctrl = c["cell"].split("|")[0]
        if ctrl == "FAVORITE_CONTROL":
            assert c["labels"]["long"].startswith(fav)
        if c["n_rows"]:
            assert f"median total {c['total']['p50']:g}" in c["labels"]["long"]


def test_marginal_events_on_rows_and_on_a_realized_game_use_one_function(sim):
    gi, res = sim
    ev = V.sim_events(res, gi)
    H, A = res.team[gi.home.team], res.team[gi.away.team]
    r = 17
    one = V.event_indicators(res.margin[r:r + 1], res.total[r:r + 1], gi.spread_home, gi.total_line,
                             home_plays=H["plays"][r:r + 1], away_plays=A["plays"][r:r + 1],
                             home_pass_att=H["pass_att"][r:r + 1], away_pass_att=A["pass_att"][r:r + 1],
                             home_designed=H["designed_rush"][r:r + 1], away_designed=A["designed_rush"][r:r + 1])
    for k in V.EVENTS:
        assert bool(one[k][0]) == bool(ev[k][r]), k


# ------------------------------------------------------------------------------- script x market matrix
def _contracts(gi, res):
    home, away = gi.home.team, gi.away.team
    pid = next(p for p, v in res.player.items() if v["team"] == home and not p.startswith("OTHER") and np.mean(v["carries"]) > 5)
    return [{"ticker": "GW-H", "family": "GAME_WINNER", "team": home},
            {"ticker": "GW-A", "family": "GAME_WINNER", "team": away},
            {"ticker": "SP-H3", "family": "SPREAD", "team": home, "floor_strike": 3.5},
            {"ticker": "TOT44", "family": "TOTAL", "threshold": 44},
            {"ticker": "TOT44b", "family": "TOTAL", "threshold": 44.0},
            {"ticker": "TT-H24", "family": "TEAM_TOTAL", "team": home, "threshold": 24},
            {"ticker": "PL-RY50", "family": "PLAYER_STAT", "stat": "rushing_yards", "player_kalshi_id": "k1", "operator": ">=", "threshold": 50},
            {"ticker": "PL-C10", "family": "PLAYER_STAT", "stat": "carries", "player_kalshi_id": "k1", "operator": ">=", "threshold": 10}], {"k1": pid}


def test_conditional_probabilities_reconcile_exactly_to_the_unconditional(sim):
    gi, res = sim
    cs, pm = _contracts(gi, res)
    mx = V.script_market_matrix(res, gi, cs, pm)
    for c in mx["contracts"]:
        assert c["support_state"] in ("MARKET_CENTRED_GAME", "SIMULATED"), c
        tot = sum(r["p_script"] * (r["p_cash_given_script"] or 0.0) for r in c["by_script"])
        assert abs(tot - c["p_cash"]) < 1e-12 and c["reconciliation_error"] < 1e-12
        assert abs(sum(r["p_script"] for r in c["by_script"]) - 1) < 1e-12
        rob = c["script_robustness"]
        assert rob["0.50"] >= rob["0.55"] >= rob["0.60"]
        assert abs(rob["0.50"] + c["failure_script_mass"] - sum(r["p_script"] for r in c["by_script"] if r["n_rows"])) < 1e-12
        if c["major_script_floor"] is not None:
            mats = [r["p_cash_given_script"] for r in c["by_script"] if r["p_script"] >= V.MATERIAL_MASS and not r["thin"]]
            assert c["major_script_floor"] == min(mats)


def test_cash_values_are_exactly_the_pricers_probabilities(fitted, monkeypatch):
    """mean(cash rows) must equal price_slate's p_football for the same rows: one interpretation of a contract."""
    from nfl_edge.sim import inputs as I, prospective as P
    b, tf, pf = fitted
    gi = FX.game_input(tf, pf)
    monkeypatch.setattr(I, "historical_bank", lambda season, seed=11: _bank())
    res = S.simulate(gi, b, n=4000, bank=_bank())      # price_slate's own call: default seed, a fresh identical bank
    cs, pm = _contracts(gi, res)
    ledger = [{**c, "game_id": gi.game_id, "period": "FULL", "mid": 0.5, "yes_bid": 0.48, "yes_ask": 0.52} for c in cs]
    slate = {"games": {gi.game_id: {"input": gi, "kickoff": None}}}
    rows = P.price_slate(slate, ledger, b, None, n_sims=4000, run_id="20260101T000000Z", observed_at="x",
                         generated_at=datetime(2026, 1, 1, tzinfo=timezone.utc), player_map=pm, verbose=lambda *a: None)
    by = {r["ticker"]: r for r in rows}
    for c in cs:
        v, state, _ = V.contract_cash(c, res, gi, pm)
        assert abs(float(v.mean()) - by[c["ticker"]]["p_football"]) < 1e-12, c["ticker"]


def test_unsupported_contracts_are_refused_not_guessed(sim):
    gi, res = sim
    cases = [({"family": "PLAYER_STAT", "stat": "longest_reception", "player_kalshi_id": "k", "operator": ">=", "threshold": 20}, "UNSUPPORTED_STAT"),
             ({"family": "PLAYER_STAT", "stat": "rushing_yards", "player_kalshi_id": "nobody", "operator": ">=", "threshold": 20}, "UNSUPPORTED_IDENTITY"),
             ({"family": "PLAYER_STAT", "stat": "rushing_yards", "player_id": "NOT_ON_ROSTER", "operator": ">=", "threshold": 20}, "NOT_ELIGIBLE"),
             ({"family": "PLAYER_STAT", "stat": "rushing_yards", "player_id": next(iter(res.player)), "operator": "<=", "threshold": 20}, "UNSUPPORTED_RULES"),
             ({"family": "TOTAL", "period": "1H", "threshold": 20}, "UNSUPPORTED_PERIOD"),
             ({"family": "FIRST_TD_SCORER", "team": gi.home.team}, "UNSUPPORTED_FAMILY"),
             ({"family": "GAME_WINNER", "team": "ZZZ"}, "UNSUPPORTED_IDENTITY"),
             ({"family": "SPREAD", "team": gi.home.team}, "UNSUPPORTED_RULES")]
    for c, want in cases:
        v, state, why = V.contract_cash(c, res, gi, {})
        assert v is None and state == want and why, (c, state)


def test_player_availability_rows_are_respected(sim):
    gi, res = sim
    for pid, P in res.player.items():
        if pid.startswith("OTHER"):
            continue
        v, state, _ = V.contract_cash({"family": "PLAYER_STAT", "stat": "receptions", "player_id": pid, "operator": ">=", "threshold": 1}, res, gi)
        inactive = ~np.asarray(P["active"], bool)
        assert (v[inactive] == 0).all(), "a player who sits out a row cannot cash on it"


def test_the_same_simulated_row_settles_every_market(sim):
    gi, res = sim
    cs, pm = _contracts(gi, res)
    cash = V.script_market_matrix(res, gi, cs, pm)["_cash"]
    assert np.allclose(cash["GW-H"] + cash["GW-A"], 1.0), "home and away winner partition every row"
    # a home cover by 3.5 implies a home win on the same row
    assert (cash["GW-H"][cash["SP-H3"] == 1] == 1).all()
    # the home team total and the game total are read off one row
    assert (np.asarray(res.total)[cash["TT-H24"] == 1] >= 24).all()


# ----------------------------------------------------------------------------------- thesis dependency
def test_dependency_matrix_is_symmetric_and_flags_duplicates(sim):
    gi, res = sim
    cs, pm = _contracts(gi, res)
    d = V.dependency_matrix(V.script_market_matrix(res, gi, cs, pm)["_cash"])
    C = d["cash_correlation"]
    for i in range(len(C)):
        for j in range(len(C)):
            assert C[i][j] == C[j][i]
    top = d["pairs"][0]
    assert {top["a"], top["b"]} == {"TOT44", "TOT44b"} and abs(top["cash_correlation"] - 1) < 1e-12
    assert abs(top["jaccard_winning_rows"] - 1) < 1e-12 and abs(top["p_a_given_b"] - 1) < 1e-12
    gw = next(p for p in d["pairs"] if {p["a"], p["b"]} == {"GW-A", "GW-H"})
    assert gw["cash_correlation"] < -0.99 and gw["shared_failure_mass"] < 0.01


def test_independent_markets_do_not_look_dependent():
    rng = np.random.default_rng(5)
    a = (rng.random(200000) < 0.55).astype(float); b = (rng.random(200000) < 0.4).astype(float)
    d = V.pair_dependency(a, b)
    assert abs(d["cash_correlation"]) < 0.01 and abs(d["lift"] - 1) < 0.02
    with pytest.raises(ValueError):
        V.pair_dependency(a, b[:-1])


def test_weather_never_enters_and_is_labelled(sim):
    gi, res = sim
    a = V.script_v2_summary(res, gi)
    b = V.script_v2_summary(res, gi, weather={"wind_speed_10m": 30.0, "retrieved_at": "2026-09-10T00:00:00+00:00"})
    assert a["weather"]["weather_model_status"] == "NOT_IN_MODEL" and b["weather"]["state"] == "FORECAST_AT_CUTOFF"
    a.pop("weather"); b.pop("weather")
    assert a == b, "a forecast changes no probability"
