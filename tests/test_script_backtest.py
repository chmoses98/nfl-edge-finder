"""Script calibration backtest scoring (nfl_edge/sim/script_backtest.py). Synthetic only."""
import os
import sys

import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.sim import script_backtest as SB, script_v2 as V  # noqa: E402


def _realized(n=400, seasons=(2019, 2020, 2021), seed=0):
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        s = seasons[i % len(seasons)]
        sp = float(rng.choice([-7.5, -3.0, 0.0, 2.5, 6.5, 10.5])); tl = 44.5
        m = float(np.round(sp + rng.normal(0, 13))); t = float(np.round(tl + rng.normal(0, 13)))
        cell = V.classify(m, t, sp, tl)
        ev = V.event_indicators([m], [t], sp, tl, home_plays=[60], away_plays=[60], home_pass_att=[35], away_pass_att=[35],
                                home_designed=[25], away_designed=[25])
        rows.append({"game_id": f"{s}_{i:04d}", "season": s, "week": 1 + i % 17, "spread_line": sp, "total_line": tl,
                     "margin": m, "total": t, "cell": cell, **{f"ev_{k}": (None if v is None else bool(v[0])) for k, v in ev.items()}})
    return pd.DataFrame(rows)


def test_baselines_use_only_the_rows_they_are_given():
    r = _realized()
    train = r[r["season"] < 2021]
    b = SB.baselines(train)
    poisoned = r.copy(); poisoned.loc[poisoned["season"] == 2021, "cell"] = V.CELLS[0]
    b2 = SB.baselines(poisoned[poisoned["season"] < 2021])
    assert np.array_equal(b["B0"], b2["B0"]) and b["train_seasons"] == [2019, 2020]
    assert abs(b["B0"].sum() - 1) < 1e-12 and all(abs(v.sum() - 1) < 1e-12 for v in b["B1"].values())


def test_multiclass_scores_on_known_cases():
    Y = np.eye(V.N_CELLS)[[0, 4, 8]]
    perfect = SB.multiclass_scores(Y.copy(), Y)
    assert np.allclose(perfect["brier"], 0) and np.allclose(perfect["top_hit"], 1)
    flat = np.full((3, V.N_CELLS), 1 / V.N_CELLS)
    s = SB.multiclass_scores(flat, Y)
    assert np.allclose(s["brier"], 1 - 1 / V.N_CELLS) and np.allclose(s["entropy"], np.log(V.N_CELLS))
    counts = np.array([[10, 0, 0, 0, 0, 0, 0, 0, 0]] * 3, float)
    ll = SB.multiclass_scores(counts / 10, Y, counts)["log_loss"]
    assert np.isfinite(ll).all(), "a zero-count cell does not make the log loss infinite"


def test_ece_of_a_calibrated_forecaster_is_inside_its_null():
    rng = np.random.default_rng(1)
    P = rng.dirichlet(np.ones(V.N_CELLS) * 2, size=1500)
    k = np.array([rng.choice(V.N_CELLS, p=p) for p in P])
    Y = np.eye(V.N_CELLS)[k]
    e = SB.reliability(P, Y)["ece"]
    null = SB.ece_null(P, B_=300)
    assert e <= null["p99"]
    biased = np.roll(P, 1, axis=1)
    assert SB.reliability(biased, Y)["ece"] > null["p99"], "a mis-assigned forecast fails the null"


def test_bootstrap_is_deterministic_and_centred():
    a = np.random.default_rng(2).normal(0, 1, 500); b = a + 0.1
    d1, d2 = SB.boot_diff(a, b), SB.boot_diff(a, b)
    assert d1 == d2 and abs(d1["mean"] + 0.1) < 1e-12 and d1["lo"] <= d1["mean"] <= d1["hi"]


def test_season_table_classifies_with_the_same_function_and_flags_missing():
    r = _realized()
    base = SB.baselines(r[r["season"] < 2021])
    ev = r[r["season"] == 2021].head(20)
    games = [{"game_id": g.game_id, "season": 2021, "week": g.week, "spread_home": g.spread_line, "total_line": g.total_line,
              "cell_counts": [1000] * 9, "events": {e: 0.5 for e in V.EVENTS}} for g in ev.itertuples()]
    games.append({"game_id": "NOT_PLAYED", "season": 2021, "week": 1, "spread_home": 3.0, "total_line": 44.0,
                  "cell_counts": [1] * 9, "events": {}})
    t = SB.season_table(games, ev, base)
    assert t["missing_realized"].sum() == 1
    ok = t[~t["missing_realized"]]
    assert (ok["y"].to_numpy() == [V.CELLS.index(c) for c in ev["cell"]]).all()
    assert ok["centre_matches_close"].all()
    blk = SB.score_block(t, with_null=False)
    assert blk["n_games"] == 20 and abs(blk["model"]["brier"] - (1 - 1 / 9)) < 1e-12
