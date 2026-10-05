"""Five-season study plumbing (research/game_script_v2): the script hook draws nothing, the bundle never trains on
the evaluation season, a poisoned future cannot move an earlier prediction, and the research-arm switches leave the
incumbent bundle unchanged when they are off. Synthetic frames only."""
import os
import sys

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.pricing.game_env import ResidualBank  # noqa: E402
from nfl_edge.sim import features as F, five_year as FY, models as M, opponent_adjust as O, simulate as S, training as T  # noqa: E402
import sim_fixtures as FX  # noqa: E402


def _bank(seed=1, n=600):
    rng = np.random.default_rng(3)
    return ResidualBank(rng.normal(0, 13, n), rng.normal(0, 13, n), np.repeat([2020, 2021, 2022], n // 3), ref_season=2023,
                        spread_lines=np.where(rng.random(n) < 0.5, 3.0, 2.5), total_lines=np.where(rng.random(n) < 0.5, 44.0, 44.5),
                        overtime=rng.random(n) < 0.06, results=rng.normal(0, 13, n), rng=np.random.default_rng(seed))


def test_the_script_hook_changes_no_later_game():
    """The bank's generator is shared across a season's games: a hook that drew from it would move every later
    game. Simulate two games with and without the collector between them."""
    b, tf, pf = FX.synthetic_bundle(seed=2)
    gids = list(tf["game_id"].drop_duplicates())[-2:]
    out = []
    for hook in (None, FY.ScriptCollector()):
        bank = _bank()
        res = []
        for i, g in enumerate(gids):
            gi = FX.game_input(tf, pf, g)
            r = S.simulate(gi, b, n=3000, bank=bank, seed=11 + i)
            if hook is not None:
                hook(r, gi)
            res.append(r)
        out.append(res)
    for a, c in zip(*out):
        assert np.array_equal(a.margin, c.margin) and np.array_equal(a.total, c.total)
        for pid in a.player:
            assert np.array_equal(a.player[pid]["rec_yards"], c.player[pid]["rec_yards"])
    col = hook
    assert len(col.games) == 2 and sum(col.games[0]["cell_counts"]) == 3000
    assert col.rows[gids[0]].shape == (8, 3000)


def _frames(seed=5, seasons=(2019, 2020, 2021, 2022), factor=1.0):
    rng = np.random.default_rng(seed)
    tg = FX.team_frame(rng, n_games=160, seasons=seasons)
    pg = FX.player_frame(rng, tg)
    if factor != 1.0:                         # poison the evaluation season
        for c in ("plays", "pass_att", "designed_rush", "targets", "points", "pass_yards", "rush_yards"):
            tg.loc[tg["season"] == seasons[-1], c] = tg.loc[tg["season"] == seasons[-1], c] * factor
        for c in ("carries", "designed_carries", "rush_yards", "targets", "receptions", "rec_yards"):
            pg.loc[pg["season"] == seasons[-1], c] = pg.loc[pg["season"] == seasons[-1], c] * factor
    pri = F.fit_priors(tg[tg["season"] < seasons[-1]], pg[pg["season"] < seasons[-1]], fit_seasons=seasons[:-1])
    tf = F.team_features(tg, priors=pri); pf = F.player_features(pg, tg, priors=pri)
    pf["dc_rank"] = pf["player_id"].str[-1].map({"B": 1, "1": 1, "2": 2}).fillna(1); pf["avail_state"] = "EXPECTED_ACTIVE"
    e = FX.eligible_frame(pf)
    opp = tf[["game_id", "team", "opp"]]
    def touch(kind):
        r = np.random.default_rng(seed + 1)
        rows = []
        for x in pf.itertuples():
            for _ in range(3):
                if kind == "c":
                    rows.append(dict(game_id=x.game_id, player_id=x.player_id, yards=float(r.normal(4, 5)), qb_scramble=0, qb_kneel=0))
                else:
                    c = int(r.random() < 0.65)
                    rows.append(dict(game_id=x.game_id, player_id=x.player_id, complete=c, yards=float(c * max(0, r.normal(11, 8)))))
        d = pd.DataFrame(rows).merge(pf[["game_id", "player_id", "team", "season", "position", "rt_ypc", "prior_ypc", "rt_explosive_rate", "rt_ypc_n",
                                         "rt_ypt", "prior_ypt", "rt_catch_rate", "rt_adot", "rt_ypt_n"]], on=["game_id", "player_id"])
        d = d.merge(opp, on=["game_id", "team"]).merge(
            tf[["game_id", "team", "off_ypc", "off_ypa", "off_comp_rate", "margin", "home"]].rename(columns={"margin": "team_margin"}), on=["game_id", "team"])
        return d.merge(tf[["game_id", "team", "def_ypc", "def_ypa", "def_comp_rate"]].rename(columns={"team": "opp"}), on=["game_id", "opp"])
    out = e.groupby(["game_id", "team"]).agg(elig_carries=("designed_carries", "sum"), elig_targets=("targets", "sum"),
                                             team_designed_rush=("team_designed_rush", "first"), team_targets=("team_targets", "first")).reset_index()
    return {"team": tf, "player": pf, "eligible": e, "outside": out, "carries": touch("c"), "targets": touch("t"), "priors": pri}


def test_the_bundle_never_trains_on_the_evaluation_season_and_ignores_its_poison():
    clean, poisoned = _frames(), _frames(factor=1000.0)
    b0 = T.fit_bundle(2022, clean, history_start=2017, verbose=lambda *a: None)
    b1 = T.fit_bundle(2022, poisoned, history_start=2017, verbose=lambda *a: None)
    assert b0["train_seasons"] == [2019, 2020, 2021] and max(b0["priors"]["fit_seasons"]) < 2022
    for k in ("game_env", "carry_share", "target_share", "carry", "target", "td", "other_share", "qb_share"):
        assert b0[k] == b1[k], f"{k} moved when only the evaluation season was poisoned"
    leaky = dict(clean); leaky["priors"] = F.fit_priors(clean["team"], clean["player"], fit_seasons=(2019, 2020, 2021, 2022))
    with pytest.raises(F.MissingPriors):
        T.fit_bundle(2022, leaky, history_start=2017, verbose=lambda *a: None)


def test_research_arm_switches_off_reproduce_the_incumbent_bundle():
    fr = _frames()
    b0 = T.fit_bundle(2022, fr, history_start=2017, verbose=lambda *a: None)
    b_none = T.fit_bundle(2022, fr, history_start=2017, verbose=lambda *a: None, arm=None)
    assert b0 == b_none and "research_arm" not in b0 and "plays_features" not in b0["game_env"]
    fix = T.fit_bundle(2022, fr, history_start=2017, verbose=lambda *a: None, arm={"opponent_def": True})
    assert fix["game_env"]["opponent_def"] is True and fix["game_env"]["plays"] != b0["game_env"]["plays"]
    # the opponent join is really the opponent's: for every row the served def_plays is the other team's own
    d = M._with_opponent_def(fr["team"])
    own = fr["team"].set_index(["game_id", "team"])["def_plays"]
    for r in d.head(40).itertuples():
        assert r.def_plays == own[(r.game_id, r.opp)]


# ------------------------------------------------------------------------------ opponent adjustment (PIT)
def _metric_table(seed=3, poison_from=None):
    rng = np.random.default_rng(seed)
    teams = [f"T{i:02d}" for i in range(8)]
    strength = {t: rng.normal(0, 0.1) for t in teams}; dstr = {t: rng.normal(0, 0.1) for t in teams}
    rows = []
    for s in (2019, 2020, 2021, 2022):
        for w in range(1, 13):
            perm = rng.permutation(teams)
            for h, a in zip(perm[::2], perm[1::2]):
                g = f"{s}_{w:02d}_{a}_{h}"
                for t, o, hs in ((h, a, 1.0), (a, h, -1.0)):
                    v = {m: strength[t] + dstr[o] + 0.02 * hs + rng.normal(0, 0.15) for m in O.METRICS}
                    if poison_from and (s, w) >= poison_from:
                        v = {m: x * 1000 for m, x in v.items()}
                    rows.append({"game_id": g, "season": s, "week": w, "team": t, "opp": o, "home_sign": hs, **v})
    return pd.DataFrame(rows)


def test_opponent_adjusted_snapshot_reads_only_strictly_earlier_weeks():
    clean = _metric_table(); poisoned = _metric_table(poison_from=(2022, 6))
    lams = {m: 4.0 for m in O.METRICS}
    for w in (1, 3, 6):          # week 6 itself is poisoned: its own outcome must not enter its own snapshot
        a = O.snapshot_matchups(clean, 2022, w, lams, O._last_weeks(clean)).reset_index(drop=True)
        b = O.snapshot_matchups(poisoned, 2022, w, lams, O._last_weeks(clean)).reset_index(drop=True)
        pd.testing.assert_frame_equal(a, b)
    a = O.snapshot_matchups(clean, 2022, 8, lams, O._last_weeks(clean))
    b = O.snapshot_matchups(poisoned, 2022, 8, lams, O._last_weeks(clean))
    assert not np.allclose(a["mx_plays"], b["mx_plays"]), "negative control: the poison does reach later weeks"


def test_lambda_selection_never_sees_the_evaluation_season():
    clean = _metric_table(); poisoned = _metric_table(poison_from=(2022, 1))
    a = O.select_lambdas(clean, 2022, metrics=("plays", "epa_play"))
    b = O.select_lambdas(poisoned, 2022, metrics=("plays", "epa_play"))
    assert a == b and a["tune_seasons"] == [2020, 2021]


def test_opponent_adjustment_removes_schedule_strength():
    """Noise-free, deliberately unbalanced schedule: the two average defences D1/D2 face only the strong
    offences (S1/S2) or only the weak ones (W1/W2). The raw allowed average calls D1 bad and D2 good; the
    adjusted defence ratings must call them equal."""
    off = {"S1": 0.3, "S2": 0.3, "W1": -0.3, "W2": -0.3, "D1": 0.0, "D2": 0.0}
    dfn = {t: 0.0 for t in off}
    pairs = [("S1", "D1"), ("S2", "D1"), ("W1", "D2"), ("W2", "D2"), ("S1", "W1"), ("S2", "W2"), ("S1", "W2"), ("S2", "W1"),
             ("D1", "D2"), ("S1", "S2"), ("W1", "W2"), ("D1", "W1"), ("D2", "S2")]
    rows = []
    for w in range(1, 16):
        for k, (a, b) in enumerate(pairs):
            g = f"2021_{w:02d}_{k}"
            for t, o in ((a, b), (b, a)):
                rows.append({"game_id": g, "season": 2021, "week": w, "team": t, "opp": o, "home_sign": 0.0,
                             **{m: off[t] + dfn[o] for m in O.METRICS}})
    mt = pd.DataFrame(rows)
    raw = mt.groupby("opp")["epa_play"].mean()
    assert raw["D1"] - raw["D2"] > 0.1, "the raw allowed average inherits the schedule"
    sol = O.solve(mt, "epa_play", 0.01, 2021, 16, O._last_weeks(mt))
    assert abs(sol["def"]["D1"] - sol["def"]["D2"]) < 0.01
    assert sol["off"]["S1"] - sol["off"]["W1"] == pytest.approx(0.6, abs=0.01)
