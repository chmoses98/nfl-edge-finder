"""GAME SCRIPT V2 -- WAVE 2 research arms (S1, Q1, M1, A1), RISK1 and the prospective runner.

Synthetic frames only (tests/sim_fixtures.py), so CI needs no data. Each test pins a property the preregistration
(research/game_script_v2/wave2/PREREGISTRATION.md) or the evidence rule depends on."""
import copy
import gzip
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.pricing.game_env import ResidualBank  # noqa: E402
from nfl_edge.sim import (availability_horizons as AH, key_numbers as K, qb_regimes as QR, risk1 as R,  # noqa: E402
                          script_v2 as V, share_dispersion as SD, simulate as S)
import sim_fixtures as FX  # noqa: E402

UTC = timezone.utc


def _bank(seed=1, n=600):
    rng = np.random.default_rng(3)
    return ResidualBank(rng.normal(0, 13, n), rng.normal(0, 13, n), np.repeat([2020, 2021, 2022], n // 3), ref_season=2023,
                        spread_lines=np.where(rng.random(n) < 0.5, 3.0, 2.5), total_lines=np.where(rng.random(n) < 0.5, 44.0, 44.5),
                        overtime=rng.random(n) < 0.06, results=rng.normal(0, 13, n), rng=np.random.default_rng(seed))


@pytest.fixture(scope="module")
def base():
    b, tf, pf = FX.synthetic_bundle(seed=1)
    return b, FX.game_input(tf, pf)


def _sim(bundle, gi, n=6000, seed=11):
    return S.simulate(gi, bundle, n=n, bank=_bank(), seed=seed)


def _s1_bundle(b, beta_hhi=-1.0, b0=np.log(30.0)):
    m = {"version": SD.S1_VERSION, "form": "S1-1", "b0": float(b0), "beta": [beta_hhi] + [0.0] * (len(SD.FEATURES) - 1),
         "mu": [0.3] + [0.0] * (len(SD.FEATURES) - 1), "sd": [0.1] + [1.0] * (len(SD.FEATURES) - 1), "features": list(SD.FEATURES)}
    out = copy.deepcopy(b)
    out["carry_share"]["alpha_model"] = m; out["target_share"]["alpha_model"] = copy.deepcopy(m)
    return out


# ------------------------------------------------------------------------------------------------ S1
def test_s1_changes_only_dispersion_and_keeps_every_identity(base):
    b, gi = base
    a = _sim(b, gi, n=20000); s = _sim(_s1_bundle(b), gi, n=20000)
    assert S.coherence_report(s)["ok"]
    for pid in a.player:
        if pid.startswith("OTHER"):
            continue
        for st in ("targets", "designed_carries"):
            ma, ms = a.player[pid][st].mean(), s.player[pid][st].mean()
            assert abs(ma - ms) < 0.06 * max(1.0, ma), (pid, st, ma, ms)   # expected shares unchanged
    for team, T in s.team.items():
        assert np.array_equal(sum(v["targets"] for v in s.player.values() if v["team"] == team), T["targets"])
        assert np.array_equal(T["rush_att"], a.team[team]["rush_att"]), "team volume is untouched by S1"


def test_s1_dirichlet_mean_is_the_expected_share_whatever_the_concentration():
    rng = np.random.default_rng(0)
    p = np.array([0.5, 0.3, 0.15, 0.05]); N = np.full(40000, 30)
    act = np.ones((40000, 4), bool)
    for alpha in (2.0, 30.0, 300.0):
        c = S._dirichlet_multinomial(rng, N, p, alpha, act)
        assert np.allclose(c.mean(axis=0) / 30, p, atol=0.006)
        assert (c.sum(axis=1) == 30).all()


def test_s1_concentration_follows_the_fitted_relationship(base):
    b, gi = base
    m = _s1_bundle(b, beta_hhi=-1.0)["carry_share"]["alpha_model"]
    f = {k: 0.0 for k in SD.FEATURES}
    lo, hi = dict(f, hhi=0.2), dict(f, hhi=0.5)
    assert SD.alpha_of(m, hi) < SD.alpha_of(m, lo), "a negative hhi coefficient lowers the concentration as hhi rises"
    wide = _sim(_s1_bundle(b, b0=np.log(3.0)), gi); narrow = _sim(_s1_bundle(b, b0=np.log(300.0)), gi)
    pid = max((p for p in wide.player if not p.startswith("OTHER")), key=lambda p: wide.player[p]["targets"].mean())
    assert wide.player[pid]["targets"].std() > narrow.player[pid]["targets"].std()


def test_s1_is_deterministic_under_a_fixed_seed(base):
    b, gi = base
    x, y = _sim(_s1_bundle(b), gi, seed=5), _sim(_s1_bundle(b), gi, seed=5)
    for pid in x.player:
        assert np.array_equal(x.player[pid]["rec_yards"], y.player[pid]["rec_yards"])


def test_s1_likelihood_recovers_alpha_where_the_moment_estimator_double_counts():
    """Counts drawn from a known Dirichlet-multinomial: the likelihood fit recovers alpha; the incumbent's moment
    estimator on realised SHARES (which already contain the multinomial noise) lands far lower."""
    rng = np.random.default_rng(1)
    true_alpha, p = 30.0, np.array([0.4, 0.25, 0.2, 0.1, 0.05])
    counts, shares = [], []
    for _ in range(800):
        N = int(rng.integers(25, 45))
        w = rng.dirichlet(true_alpha * p)
        counts.append(rng.multinomial(N, w).astype(float)); shares.append(p)
    fit = SD.fit(counts, shares, None)
    assert abs(np.exp(fit["b0"]) - true_alpha) / true_alpha < 0.2
    y = np.vstack([c / c.sum() for c in counts]); P = np.tile(p, (len(y), 1))
    msk = (P > 0.02) & (P < 0.98)
    moment = ((P * (1 - P))[msk].sum() / ((y - P) ** 2)[msk].sum()) - 1.0
    assert moment < 0.6 * true_alpha, "the share-moment estimator under-states concentration (over-dispersion)"


# ------------------------------------------------------------------------------------------------ Q1
def _q1_bundle(b, pi=(0.7, 0.15, 0.15)):
    # every regime above QR.fit's 20-row minimum, so each keeps its own distribution
    q = pd.DataFrame({"share": np.r_[np.ones(140), np.linspace(0.3, 0.85, 30), np.zeros(20), np.linspace(0.02, 0.2, 10)]})
    q["regime"] = QR.regime_of(q["share"])
    m = QR.fit(q, conditional=False)
    out = copy.deepcopy(b)
    out["qb_share"] = {"quantiles": QR.mixture_quantiles(m, np.asarray(pi)), "n": m["n"], "p_below_half": 0.0, "regime_model": m}
    return out


def test_q1_qb_identities_hold_and_partial_games_go_to_the_backup(base):
    b, gi = base
    r = _sim(_q1_bundle(b), gi)
    coh = S.coherence_report(r)
    assert coh["ok"], coh
    for ti in (gi.home, gi.away):
        T = r.team[ti.team]
        qbs = [v for v in r.player.values() if v["team"] == ti.team and "attempts" in v]
        assert np.array_equal(sum(v["attempts"] for v in qbs), T["pass_att"])
        assert np.allclose(sum(v["pass_yards"] for v in qbs), T["pass_yards"])
        for v in qbs:
            assert (v["attempts"] >= 0).all() and np.array_equal(v["attempts"], np.round(v["attempts"]))
        starter = r.player[ti.qb1]
        low = starter["starter_share"] < 0.25
        assert low.any(), "the LOW regime produces rows where the starter barely throws"
        rest = sum(v["attempts"] for k, v in r.player.items() if v["team"] == ti.team and "attempts" in v and k != ti.qb1)
        assert np.array_equal(rest[low], T["pass_att"][low] - starter["attempts"][low])


def test_q1_moves_the_low_tail_without_exploding_the_mean_or_touching_receivers(base):
    b, gi = base
    a, q = _sim(b, gi), _sim(_q1_bundle(b), gi)
    qa, qq = a.player[gi.home.qb1]["attempts"], q.player[gi.home.qb1]["attempts"]
    assert np.mean(qq < 0.25 * np.median(qa)) > np.mean(qa < 0.25 * np.median(qa)) + 0.05
    assert abs(qq.mean() - qa.mean()) < 0.35 * qa.mean()
    # Receivers' targets depend on team volume, not on who throws. Row-for-row identity holds for the team simulated
    # FIRST (home); numpy's binomial consumes a p-dependent number of draws in the incumbent's quarterback TD split, so
    # the second team's rows are re-drawn -- same distribution, different rows (documented in S1/Q1 reports).
    for pid, v in a.player.items():
        if "attempts" in v or pid.startswith("OTHER"):
            continue
        if v["team"] == gi.home.team:
            assert np.array_equal(v["targets"], q.player[pid]["targets"])
        else:
            assert abs(v["targets"].mean() - q.player[pid]["targets"].mean()) < 0.15 * max(1.0, v["targets"].mean())


def test_q1_mixture_quantiles_are_the_mixture():
    q = pd.DataFrame({"share": np.r_[np.ones(50), np.full(30, 0.5), np.zeros(20)]}); q["regime"] = QR.regime_of(q["share"])
    m = QR.fit(q, conditional=False)
    qs = np.asarray(QR.mixture_quantiles(m, np.array([0.5, 0.3, 0.2])))
    assert (np.diff(qs) >= -1e-12).all()
    assert abs(np.mean(qs < 0.25) - 0.2) < 0.02 and abs(np.mean(qs >= 0.9) - 0.5) < 0.02


# ------------------------------------------------------------------------------------------------ M1
def _hist(n=1500, seed=4):
    rng = np.random.default_rng(seed)
    s = rng.choice([-7.5, -3.0, -2.5, 1.5, 3.0, 3.5, 6.5, 9.5], n); t = rng.choice([40.5, 44.0, 47.5, 51.0], n)
    key = rng.choice([3, 7, 10, 14, 1, 2, 4, 6], n, p=[0.3, 0.2, 0.08, 0.07, 0.1, 0.1, 0.1, 0.05])
    m = np.round(np.sign(s + rng.normal(0, 13, n)) * key).astype(int)
    tot = np.round(t + rng.normal(0, 12, n)).astype(int)
    tot = np.where((tot + m) % 2 != 0, tot + 1, tot)
    tot = np.maximum(tot, np.abs(m))
    return pd.DataFrame({"game_id": [f"g{i}" for i in range(n)], "season": rng.choice([2018, 2019, 2020], n), "week": 1,
                         "spread_line": s, "total_line": t, "result": m, "total": tot, "overtime": 0})


def test_m1_pmf_sums_to_one_and_means_are_the_centre_exactly():
    h = _hist()
    for s, T in ((3.0, 44.0), (-6.5, 47.5), (9.5, 40.5)):
        pk = K.m1k_pmf(h, s, T, 2021)
        assert abs(sum(pk["margin"].values()) - 1) < 1e-12
        q = pk["weights"]
        assert abs((q * h["result"]).sum() - s) < 1e-8 and abs((q * h["total"]).sum() - T) < 1e-8


def test_m1_draws_are_coherent_scores_and_ladders_are_monotone():
    h = _hist()
    d = K.m1k_draws(h, 3.0, 44.0, 2021, 20000)
    assert np.all(d["home"] + d["away"] == d["total"]) and np.all(d["home"] - d["away"] == d["margin"])
    assert np.all(np.mod(d["home"], 1) == 0) and np.all(d["home"] >= 0) and np.all(d["away"] >= 0)
    surv = [np.mean(d["margin"] > k) for k in np.arange(-20.5, 21)]
    assert all(a >= b for a, b in zip(surv, surv[1:]))


def test_m1_key_number_mass_is_kept_and_stable_across_centres():
    h = _hist()
    real3 = np.mean(np.abs(h["result"]) == 3)
    for s in (2.5, 3.0, 3.5):
        p3 = sum(p for m, p in K.m1k_pmf(h, s, 44.0, 2021)["margin"].items() if abs(m) == 3)
        assert p3 > 0.6 * real3, "the empirical key-number mass survives the tilt"


# ------------------------------------------------------------------------------------------------ A1
def test_a1_known_active_at_t0_gets_no_second_questionable_discount():
    st = pd.Series(["QUESTIONABLE", "EXPECTED_ACTIVE", "QUESTIONABLE"])
    assert list(AH.availability_states(st, "T0_INACTIVES")) == ["EXPECTED_ACTIVE"] * 3
    assert list(AH.availability_states(st, "T24")) == list(st), "T24 keeps the uncertainty"


def test_a1_horizon_cannot_be_claimed_early_or_from_a_later_roster():
    ko = datetime(2026, 10, 11, 17, 0, tzinfo=UTC)
    ros = pd.DataFrame({"team": ["AAA", "AAA"], "status": ["ACT", "INA"], "player_id": ["x", "y"]})
    early = ko - timedelta(hours=3)
    assert AH.prospective_horizon(early, ko, ros, "AAA", early - timedelta(minutes=5))[0] == "T24"
    late = ko - timedelta(minutes=60)
    assert AH.prospective_horizon(late, ko, ros, "AAA", late - timedelta(minutes=5))[0] == "T0_INACTIVES"
    assert AH.prospective_horizon(late, ko, ros, "AAA", late + timedelta(hours=2))[0] == "T24", \
        "a roster retrieved after the cutoff cannot teach a replay the inactive list"
    assert AH.prospective_horizon(late, ko, ros, "AAA", None)[0] == "T24"
    assert AH.prospective_horizon(late, ko, ros.assign(status="ACT"), "AAA", late)[0] == "T24"


def test_a1_t0_changes_only_the_evaluation_season():
    e = pd.DataFrame({"season": [2024, 2025, 2025], "avail_state": ["QUESTIONABLE"] * 3})
    out = AH.apply_horizon({"eligible": e}, 2025, "T0_INACTIVES")["eligible"]
    assert list(out["avail_state"]) == ["QUESTIONABLE", "EXPECTED_ACTIVE", "EXPECTED_ACTIVE"]


# ------------------------------------------------------------------------------------------------ RISK1
@pytest.fixture(scope="module")
def doc(base):
    b, gi = base
    res = _sim(b, gi)
    home, away = gi.home.team, gi.away.team
    cs = [{"ticker": "W-H", "family": "GAME_WINNER", "team": home}, {"ticker": "S-H3", "family": "SPREAD", "team": home, "floor_strike": 3.5},
          {"ticker": "S-H3b", "family": "SPREAD", "team": home, "floor_strike": 3.0},
          {"ticker": "T44", "family": "TOTAL", "threshold": 44}, {"ticker": "TT", "family": "TEAM_TOTAL", "team": away, "threshold": 20}]
    return V.game_document(res, gi, S.coherence_report(res), cs, {}, fingerprint_rows=1024), res, gi, cs


def test_risk1_numbers_come_only_from_the_frozen_pregame_document(doc):
    d, res, gi, cs = doc
    frozen = json.loads(json.dumps(d, default=float))
    proj = [{"ticker": c["ticker"], "mid": 0.5, "yes_bid": 0.48, "yes_ask": 0.52, "p_football": 0.5, "reconcile_weight": 0} for c in cs]
    o1 = R.observations(frozen, proj)
    o1["y"] = 1.0                                          # "settlement" happens
    o2 = R.observations(frozen, proj)
    assert json.loads(json.dumps(d, default=float)) == frozen, "settling never mutates the frozen document"
    assert o2.drop(columns=[]).equals(R.observations(frozen, proj)) and "y" not in o2
    for c in frozen["contracts"]:
        tot = sum(p * (pc or 0) for p, pc in zip(frozen["p_script"], c["p_cash_given_script"]))
        assert abs(tot - c["p_cash"]) < 2e-3, "rounded conditionals still reconcile to the unconditional probability"


def test_fingerprints_round_trip_and_identical_worlds_are_one_thesis(doc):
    d, res, gi, cs = doc
    fp = {c["ticker"]: c["fingerprint"] for c in d["contracts"]}
    cash, *_ = V.contract_cash(cs[0], res, gi)
    assert np.array_equal(V.decode_fingerprint(fp["W-H"]), cash[:1024])
    groups = R.thesis_groups(fp)
    together = next(g for g in groups if "S-H3" in g)
    assert "S-H3b" in together, "x > 3.5 and x > 3.0 settle identically on integer margins: one thesis, two tickers"
    eff = R.effective_theses({"S-H3": 3.0, "S-H3b": 3.0}, groups)
    assert abs(eff["effective_theses"] - 1.0) < 1e-12
    dep = V.dependency_matrix({k: V.decode_fingerprint(v) for k, v in fp.items()})
    C = dep["cash_correlation"]
    assert all(C[i][j] == C[j][i] for i in range(len(C)) for j in range(len(C)))


def test_realized_settlement_uses_the_pricers_semantics():
    game = {"game_id": "G", "home_team": "AAA", "away_team": "BBB", "home_score": 24.0, "away_score": 21.0}
    st = {"p1": {"team": "AAA", "rush_yards": 49.6, "receptions": 3.0}}
    assert R.realized_cash({"family": "SPREAD", "team": "AAA", "floor_strike": 2.5}, game, st) == 1.0
    assert R.realized_cash({"family": "SPREAD", "team": "AAA", "floor_strike": 3.0}, game, st) == 0.0
    assert R.realized_cash({"family": "TOTAL", "threshold": 45}, game, st) == 1.0
    assert R.realized_cash({"family": "PLAYER_STAT", "stat": "rushing_yards", "player_id": "p1", "operator": ">=", "threshold": 50}, game, st) == 1.0
    assert R.realized_cash({"family": "PLAYER_STAT", "stat": "longest_reception", "player_id": "p1", "operator": ">=", "threshold": 5}, game, st) is None


def test_risk1_uses_the_last_pre_kickoff_capture_of_post_cutoff_games_only():
    idx = pd.DataFrame([
        {"run_id": "a", "game_id": "OLD", "generated_at": "2026-10-04T10:00:00+00:00", "state": "OK"},
        {"run_id": "b", "game_id": "NEW", "generated_at": "2026-10-11T10:00:00+00:00", "state": "OK"},
        {"run_id": "c", "game_id": "NEW", "generated_at": "2026-10-11T15:00:00+00:00", "state": "OK"},
        {"run_id": "d", "game_id": "NEW", "generated_at": "2026-10-11T17:30:00+00:00", "state": "OK"}])
    ko = {"OLD": "2026-10-04T17:00:00+00:00", "NEW": "2026-10-11T17:00:00+00:00"}
    sel = R.select_captures(idx, ko)
    assert list(sel["run_id"]) == ["c"], "pre-cutoff games are out; a capture at or after kickoff is never used"


# ------------------------------------------------------------------------------------------------ the runner
def _runner():
    import importlib.util
    spec = importlib.util.spec_from_file_location("w2p", os.path.join(ROOT, "scripts", "sim", "wave2_prospective.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m


def test_runner_grafts_only_the_arm_component(base):
    b, _ = base
    W = _runner()
    comps = {"S1": {"carry": {"x": 1}, "target": {"y": 2}}, "Q1": {"qb_share": {"quantiles": [0.5] * 201}}}
    arms = W.arm_bundles(b, comps)
    for arm, changed in (("S1", {"carry_share", "target_share"}), ("Q1", {"qb_share"})):
        diff = {k for k in b if json.dumps(b[k], sort_keys=True, default=str) != json.dumps(arms[arm][k], sort_keys=True, default=str)}
        assert diff == changed, (arm, diff)
    assert arms["A0"] is b and "alpha_model" not in b["carry_share"], "the incumbent bundle is never mutated"


def test_runner_windows_cutoff_and_write_once(tmp_path):
    W = _runner()
    sched = pd.DataFrame([{"game_id": "2026_05_A_B", "season": 2026, "week": 5, "gameday": "2026-10-11", "gametime": "13:00"},
                          {"game_id": "2026_04_C_D", "season": 2026, "week": 4, "gameday": "2026-10-04", "gametime": "13:00"}])
    ko = datetime(2026, 10, 11, 17, 0, tzinfo=UTC)
    assert W.due_games(sched, ko - timedelta(minutes=120), set()) == {"2026_05_A_B": ("EARLY", 2026, 5)}
    assert W.due_games(sched, ko - timedelta(minutes=60), set()) == {"2026_05_A_B": ("LATE", 2026, 5)}
    assert W.due_games(sched, ko - timedelta(minutes=60), {("2026_05_A_B", "LATE")}) == {}
    assert W.due_games(sched, ko - timedelta(minutes=10), set()) == {}, "inside 30 minutes nothing is captured"
    assert W.due_games(sched, datetime(2026, 10, 4, 15, 0, tzinfo=UTC), set()) == {}, "a pre-cutoff game is never captured"
    doc = {"run_id": "20261011T160000Z", "games": {}}
    p = W.write_record(str(tmp_path), doc, "2026_05_A_B", "LATE")
    assert W._parse_name(p) == ("2026_05_A_B", "LATE")
    with pytest.raises(FileExistsError):
        W.write_record(str(tmp_path), doc, "2026_05_A_B", "LATE")


def test_no_wave2_module_is_read_by_a_decision_path():
    for name in ("gates.py", "preflight.py", "risk.py", "wager_risk.py", "approval.py", "evaluate.py", "scorecard.py",
                 "analysis.py", "packet.py", "render.py", "script_block.py"):
        src = open(os.path.join(ROOT, "nfl_edge", "handicap", name)).read()
        for key in ("risk1", "share_dispersion", "qb_regimes", "key_numbers", "availability_horizons", "research/wave2", "wave2"):
            assert key not in src, f"{name} reads {key}"
