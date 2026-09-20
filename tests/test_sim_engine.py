"""The simulation layer: coherence, point-in-time integrity, reconciliation limits, packet wiring.

Everything here runs on synthetic frames (tests/sim_fixtures.py); CI carries no data files.
"""
import gzip
import json
import os
import sys
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from nfl_edge.sim import features as F, models as M, reconcile as R, simulate as S  # noqa: E402
from nfl_edge.sim.prospective import fast_implied_lines  # noqa: E402
from nfl_edge.engines.player.dist import LatticeDistribution  # noqa: E402
from nfl_edge.pricing.game_env import ResidualBank  # noqa: E402
import sim_fixtures as FX  # noqa: E402


@pytest.fixture(scope="module")
def bundle_and_frames():
    return FX.synthetic_bundle(seed=1)


@pytest.fixture(scope="module")
def bank():
    rng = np.random.default_rng(3)
    n = 600
    return ResidualBank(rng.normal(0, 13, n), rng.normal(0, 13, n), np.repeat([2020, 2021, 2022], n // 3), ref_season=2023,
                        spread_lines=np.where(rng.random(n) < 0.5, 3.0, 2.5), total_lines=np.where(rng.random(n) < 0.5, 44.0, 44.5),
                        overtime=rng.random(n) < 0.06, results=rng.normal(0, 13, n), rng=np.random.default_rng(1))


# ------------------------------------------------------------------------------------- coherence
def test_every_identity_holds_on_every_row(bundle_and_frames, bank):
    b, tf, pf = bundle_and_frames
    gi = FX.game_input(tf, pf)
    res = S.simulate(gi, b, n=3000, bank=bank)
    rep = S.coherence_report(res)
    assert rep["ok"], rep


def test_ladders_are_monotone_and_no_impossible_values(bundle_and_frames, bank):
    b, tf, pf = bundle_and_frames
    res = S.simulate(FX.game_input(tf, pf), b, n=3000, bank=bank)
    for pid, v in res.player.items():
        for st in ("carries", "targets", "receptions", "rush_td", "rec_td", "any_td"):
            assert (v[st] >= 0).all() and np.all(np.mod(v[st], 1) == 0), (pid, st)
        assert (v["receptions"] <= v["targets"]).all()
        d = LatticeDistribution.from_samples(v["rush_yards"], 300)
        lad = [d.survival(k) for k in (10, 30, 50, 70, 100)]
        assert all(a >= b_ - 1e-12 for a, b_ in zip(lad, lad[1:]))
    assert np.all(res.home_points + res.away_points == res.total)


def test_game_script_moves_the_pass_rate(bundle_and_frames, bank):
    """A team that leads by a lot on a row must pass less on that row than one that trails by a lot -- the
    game-script coupling is the point of simulating on common rows.  The synthetic generator built the
    script effect in, so the fitted model must reproduce its sign."""
    b, tf, pf = bundle_and_frames
    res = S.simulate(FX.game_input(tf, pf), b, n=6000, bank=bank)
    home = res.team[res.meta and next(iter(res.team))]
    m = home["margin"]; pr = home["pass_rate"]
    assert pr[m >= 10].mean() < pr[m <= -10].mean()


def test_an_out_player_receives_nothing_and_teammates_absorb_the_share(bundle_and_frames, bank):
    b, tf, pf = bundle_and_frames
    gi = FX.game_input(tf, pf)
    base = S.simulate(gi, b, n=3000, bank=bank, seed=5)
    rb1 = [p for p in gi.home.players["player_id"] if p.endswith("RB1")][0]
    rb2 = [p for p in gi.home.players["player_id"] if p.endswith("RB2")][0]
    gi.home.players = gi.home.players[gi.home.players["player_id"] != rb1].reset_index(drop=True)
    alt = S.simulate(gi, b, n=3000, bank=bank, seed=5)
    assert rb1 not in alt.player
    assert alt.player[rb2]["carries"].mean() > base.player[rb2]["carries"].mean() * 1.3
    assert S.coherence_report(alt)["ok"]


def test_questionable_players_sit_out_on_some_rows_only(bundle_and_frames, bank):
    b, tf, pf = bundle_and_frames
    gi = FX.game_input(tf, pf)
    gi.home.players.loc[gi.home.players["player_id"].str.endswith("WR1"), "avail_state"] = "QUESTIONABLE"
    res = S.simulate(gi, b, n=4000, bank=bank, seed=2)
    wr1 = [p for p in res.player if p.endswith(f"{gi.home.team}_WR1")][0]
    act = res.player[wr1]["active"].mean()
    assert 0.6 < act < 0.95
    assert (res.player[wr1]["targets"][~res.player[wr1]["active"]] == 0).all()


# ------------------------------------------------------------------------------- point in time
def test_a_rows_own_outcome_never_enters_its_feature():
    rng = np.random.default_rng(0)
    n = 40
    grp = np.array(["p"] * n); sea = np.repeat([2020, 2021], n // 2)
    X = rng.normal(5, 2, (n, 2))
    S0, N0, _ = F.decayed_prior_sums(grp, None, sea, X, 4.0, 0.5)
    X2 = X.copy(); X2[17] += 100.0
    S1, N1, _ = F.decayed_prior_sums(grp, None, sea, X2, 4.0, 0.5)
    assert np.array_equal(S0[:18], S1[:18]) and np.array_equal(N0[:18], N1[:18])
    assert not np.array_equal(S0[18:], S1[18:])


def test_a_phantom_row_reads_the_state_and_leaves_it_untouched():
    n = 6
    grp = np.array(["p"] * n); sea = np.array([2020] * n)
    X = np.array([[1.0], [2.0], [np.nan], [3.0], [4.0], [5.0]])
    ph = np.array([False, False, True, False, False, False])
    S_, N_, n_prior = F.decayed_prior_sums(grp, None, sea, X, 4.0, 0.5, phantom=ph)
    # the phantom row (index 2) sees the state after rows 0-1, and row 3 sees exactly the same state
    assert S_[2] == S_[3] and N_[2] == N_[3] and n_prior[2] == n_prior[3] == 2


def test_the_season_boundary_discounts_history():
    grp = np.array(["p"] * 3); X = np.array([[10.0], [10.0], [10.0]])
    S_same, _, _ = F.decayed_prior_sums(grp, None, np.array([2020, 2020, 2020]), X, 4.0, 0.5)
    S_new, _, _ = F.decayed_prior_sums(grp, None, np.array([2020, 2020, 2021]), X, 4.0, 0.5)
    assert S_new[2] == pytest.approx(0.5 * S_same[2])


def test_eligibility_excludes_reserve_and_out_players():
    depth = pd.DataFrame({"team": ["X", "X", "X"], "player_id": ["a", "b", "c"], "dc_pos": ["RB", "RB", "RB"], "dc_rank": [1, 2, 3], "dc_vintage": ["v"] * 3})
    roster = pd.DataFrame({"team": ["X", "X", "X", "X"], "player_id": ["a", "b", "c", "d"], "position": ["RB"] * 4,
                           "status": ["ACT", "RES", "ACT", "ACT"], "player_name": list("abcd")})
    inj = pd.DataFrame({"player_id": ["c", "d"], "report_status": ["Out", "Questionable"], "practice_status": [None, None]})
    e = F.eligible_players(2026, 2, "X", depth=depth, roster=roster, injuries=inj)
    states = dict(zip(e["player_id"], e["avail_state"]))
    assert "b" not in states, "a reserve-list player on the depth chart is not available"
    assert states.get("c") is None or states["c"] == "OUT"
    assert states["d"] == "QUESTIONABLE" and states["a"] == "EXPECTED_ACTIVE"


def test_the_bundle_records_its_training_seasons(bundle_and_frames):
    b, _, _ = bundle_and_frames
    assert b["train_seasons"] == [2020, 2021, 2022]
    assert "sim_version" in b and "models_version" in b


# ------------------------------------------------------------------------------- reconciliation
def test_reconciliation_weight_limits():
    rng = np.random.default_rng(0)
    d = LatticeDistribution.from_samples(rng.gamma(4, 15, 20000), 300)
    r0, a0 = R.reconcile_distribution(d, 50.0, 0.0)
    r1, a1 = R.reconcile_distribution(d, 50.0, 1.0)
    assert r0.mean() == pytest.approx(50.0, abs=0.6)
    assert r1.mean() == pytest.approx(d.mean(), abs=0.6)
    rh, ah = R.reconcile_distribution(d, 50.0, 0.5)
    assert rh.mean() == pytest.approx(50.0 + 0.5 * (d.mean() - 50.0), abs=0.6)
    assert ah["status"] == "RECONCILED"


def test_no_weight_means_no_reconciled_probability():
    rng = np.random.default_rng(0)
    d = LatticeDistribution.from_samples(rng.gamma(4, 15, 5000), 300)
    out, attr = R.reconcile_distribution(d, 50.0, None)
    assert attr["status"] == "NO_WEIGHT" and out.mean() == pytest.approx(d.mean())


def test_weights_are_fitted_only_on_the_fit_rows_and_confirmed_elsewhere():
    rng = np.random.default_rng(0)
    rows = []
    for i in range(400):
        pm = rng.uniform(0.2, 0.8); pf = np.clip(pm + rng.normal(0, 0.15), 0.01, 0.99)
        y = float(rng.random() < pm)   # the market is right; the football view is noise
        rec = {"ticker": f"t{i}", "game_id": f"g{i % 40}", "week": 1 + i % 18, "player_id": "p", "stat": "rush_yards", "k": 50.0, "y": y,
               "market_mono": pm, "p_football": pf, "football_mean": 50 + 100 * (pf - pm), "market_mean": 50.0}
        for w in R.WEIGHT_GRID:
            rec[f"p_w{w:.2f}"] = pm + w * (pf - pm)
        rows.append(rec)
    sc = pd.DataFrame(rows)
    fitted = R.fit_weights(sc[sc["week"] <= 9])
    assert fitted["rush_yards"]["weight"] <= 0.15, "noise must earn (almost) no weight"
    conf = R.confirm(sc[sc["week"] > 9], fitted)
    assert conf["rush_yards"]["n"] > 0 and "z" in conf["rush_yards"]


# ----------------------------------------------------------------------------------- pricing
def test_fast_implied_lines_reads_the_fifty_percent_crossing():
    rows = [{"family": "SPREAD", "period": "FULL", "team": "H", "floor_strike": -3.5, "yes_bid": 0.62, "yes_ask": 0.66},
            {"family": "SPREAD", "period": "FULL", "team": "H", "floor_strike": 0.5, "yes_bid": 0.46, "yes_ask": 0.50},
            {"family": "SPREAD", "period": "FULL", "team": "A", "floor_strike": 3.5, "yes_bid": 0.34, "yes_ask": 0.38},
            {"family": "TOTAL", "period": "FULL", "threshold": 41.0, "yes_bid": 0.68, "yes_ask": 0.72},
            {"family": "TOTAL", "period": "FULL", "threshold": 47.0, "yes_bid": 0.30, "yes_ask": 0.34}]
    s, t, diag = fast_implied_lines(rows, "H", "A")
    assert -3.5 < s < 0.5 and 41 < t < 47


def test_priority_is_not_boosted_by_raw_incumbent_disagreement():
    from nfl_edge.handicap import packet as P
    base = {"game_id": "g", "kickoff_utc": None, "injuries": {"records": []}, "weather": {}, "largest_moves": [], "markets": [],
            "data_health": [], "simulation": {}}
    quiet = dict(base, largest_disagreements=[])
    loud = dict(base, largest_disagreements=[{"disagreement_vs_mid": -0.44}])
    pq = P.game_priority([quiet])[0]; pl = P.game_priority([loud])[0]
    assert pl["priority_score"] == pq["priority_score"], "a raw 0.44 disagreement used to add 4 points; it must add nothing"
    assert any("NOT scored" in r for r in pl["reasons"])
    recon = dict(base, largest_disagreements=[], simulation={"largest_reconciled_disagreements": [{"disagreement_vs_mid": 0.12}]})
    pr = P.game_priority([recon])[0]
    assert 0 < pr["priority_score"] <= 2.0


def test_sim_block_loads_only_files_at_or_before_the_instant(tmp_path):
    from nfl_edge.handicap import sim_block
    d = tmp_path / "data" / "shadow" / "sim" / "2026-09-16"; d.mkdir(parents=True)
    for stamp, p in (("20260916T010000Z", 0.3), ("20260916T090000Z", 0.7)):
        with gzip.open(d / f"{stamp}.sim-1.0.0.projections.jsonl.gz", "wt") as f:
            f.write(json.dumps({"ticker": "T", "p_football": p, "mid": 0.5, "support_state": "PRICED", "p_reconciled": p}) + "\n")
        json.dump({"run_id": stamp, "sim_version": "sim-1.0.0"}, open(d / f"{stamp}.sim-1.0.0.manifest.json", "w"))
    rows, man = sim_block.load_latest([str(tmp_path)], at_or_before=datetime(2026, 9, 16, 5, tzinfo=timezone.utc))
    assert man["run_id"] == "20260916T010000Z" and rows["T"]["p_football"] == 0.3
    rows, man = sim_block.load_latest([str(tmp_path)], at_or_before=datetime(2026, 9, 16, 12, tzinfo=timezone.utc))
    assert man["run_id"] == "20260916T090000Z"
    assert sim_block.load_latest([str(tmp_path / "nowhere")]) == (None, None)


def test_projection_records_are_write_once(tmp_path):
    from nfl_edge.sim import prospective as P
    p = P.write_records(str(tmp_path), "20260916T010000Z", [{"ticker": "T"}], {"run_id": "20260916T010000Z"})
    assert os.path.exists(p)
    with pytest.raises(FileExistsError):
        P.write_records(str(tmp_path), "20260916T010000Z", [{"ticker": "T"}], {"run_id": "20260916T010000Z"})


def test_touchdown_relocation_is_poisson_not_a_stretched_lattice():
    d = LatticeDistribution.from_samples(np.r_[np.zeros(9995), np.ones(5)], 6)   # football mean 0.0005
    out, attr = R.reconcile_distribution(d, 0.046, 0.6, stat="any_td")
    assert out.mean() == pytest.approx(0.046 + 0.6 * (d.mean() - 0.046), abs=1e-3)
    assert 0.0 < out.survival(1) < 0.05


def test_yardage_relocation_never_uses_a_poisson():
    rng = np.random.default_rng(1)
    d = LatticeDistribution.from_samples(rng.gamma(2, 2.2, 20000), 300)      # football mean ~4.4 yards
    out = R.relocate(d, 37.2, stat="rec_yards")
    assert out.mean() == pytest.approx(37.2, rel=0.05)
    assert 0.6 < out.survival(15) < 0.95, "a 37-yard mean must leave real mass below 15 yards"
    near = R.relocate(d, 6.0, stat="rec_yards")
    assert near.meta.get("shift", "").startswith("scale"), "within the scale limit the football shape is kept"


def test_a_weight_whose_confirmation_points_the_wrong_way_is_not_deployed():
    """Inside the z gate is not enough: if the later-week confirmation is worse than the market in point
    estimate, no deviation is earned.  This is the condition that removed the rush_yards weight after the
    point-in-time correction moved its z from +1.05 to +0.93."""
    fitted_all = {"s": {"weight": 0.30}}
    fitted_fit = {"s": {"weight": 0.25, "n": 600}}
    adverse = {"s": {"z": 0.93, "diff_vs_market": +0.00157, "n": 2813}}
    favourable = {"s": {"z": -0.99, "diff_vs_market": -0.00020, "n": 2050}}
    assert R.deploy_weights(fitted_all, fitted_fit, adverse)["s"]["weight"] == 0.0
    assert R.deploy_weights(fitted_all, fitted_fit, adverse)["s"]["weight_under_z_gate_only"] == 0.25
    assert R.deploy_weights(fitted_all, fitted_fit, favourable)["s"]["weight"] == 0.25


def test_the_deployment_rule_can_only_remove_weights_never_invent_one():
    """Every gate is a conjunction, so tightening any of them moves a weight toward zero."""
    fitted_all = {"s": {"weight": 0.0}}
    fitted_fit = {"s": {"weight": 0.0, "n": 9999}}
    conf = {"s": {"z": -5.0, "diff_vs_market": -1.0, "n": 9999}}
    assert R.deploy_weights(fitted_all, fitted_fit, conf)["s"]["weight"] == 0.0


# ------------------------------------------------- Week 2 2026 production blockers (first live slate)
def _one_qb_game(tf, pf):
    """The fixture teams already carry exactly one quarterback -- which is precisely why the suite did not
    catch this: the synthetic bundle's qb_share is 1.0 everywhere, so the remainder was always zero."""
    gi = FX.game_input(tf, pf)
    assert int((gi.home.players["position"] == "QB").sum()) == 1
    return gi


def _two_qb_game(tf, pf):
    """The same game with a backup added behind the starter."""
    gi = FX.game_input(tf, pf)
    hp = gi.home.players
    j = int(np.flatnonzero((hp["position"] == "QB").to_numpy())[0])
    backup = hp.iloc[[j]].copy()                      # a one-row frame keeps every column's dtype
    backup.loc[backup.index[0], "player_id"] = str(hp["player_id"].iloc[j]) + "-QB2"
    if "dc_rank" in hp.columns:
        backup.loc[backup.index[0], "dc_rank"] = 2.0
    gi.home.players = pd.concat([hp, backup], ignore_index=True)
    assert int((gi.home.players["position"] == "QB").sum()) == 2
    return gi


def _bundle_with_a_starter_tail(b):
    """A qb_share with a real left tail, so the starter genuinely gives volume up on some rows.

    Without this the synthetic bundle's default share is 1.0 everywhere, the remainder is always zero and
    the identity would close for the wrong reason.
    """
    q = np.ones(201)
    q[:40] = np.linspace(0.05, 0.99, 40)
    return dict(b, qb_share={"quantiles": q.tolist()})


def test_a_team_with_one_available_quarterback_still_closes_the_passing_identity(bundle_and_frames, bank):
    """JAX and SEA, week 2 2026: the only two teams with one available QB and the only two games whose
    coherence failed.  The starter's fitted tail gave up volume that was credited to nobody."""
    b, tf, pf = bundle_and_frames
    b = _bundle_with_a_starter_tail(b)
    gi = _one_qb_game(tf, pf)
    res = S.simulate(gi, b, n=4000, bank=bank)
    rep = S.coherence_report(res)
    broken = {k: v for k, v in rep.items() if k != "ok" and v}
    assert rep["ok"], f"a single-quarterback team must still conserve the team's passing: {broken}"

    # ... and the teeth: the remainder is real, non-zero, and lands on the OTHER bucket
    other = res.player[f"OTHER:{gi.home.team}"]
    assert "attempts" in other, "the unclaimed attempts must be credited somewhere"
    assert other["attempts"].sum() > 0, "the starter tail never fired, so the identity closed trivially"
    assert (other["attempts"] < 0).sum() == 0
    qb = res.player[gi.home.qb1]
    assert np.all(qb["attempts"] + other["attempts"] == res.team[gi.home.team]["pass_att"])

    # why the existing suite never saw it: with the default share of 1.0 there is no remainder at all
    flat = S.simulate(gi, dict(b, qb_share={"quantiles": [1.0] * 201}), n=1500, bank=bank)
    assert flat.player[f"OTHER:{gi.home.team}"]["attempts"].sum() == 0


def test_the_starters_own_distribution_does_not_depend_on_having_a_backup(bundle_and_frames, bank):
    """The fix must not move the starter: only the destination of the remainder changes."""
    b, tf, pf = bundle_and_frames
    b = _bundle_with_a_starter_tail(b)
    two = _two_qb_game(tf, pf)
    one = _one_qb_game(tf, pf)
    a = S.simulate(two, b, n=4000, bank=bank).player[two.home.qb1]["attempts"]
    c = S.simulate(one, b, n=4000, bank=bank).player[one.home.qb1]["attempts"]
    assert abs(float(a.mean()) - float(c.mean())) < 0.75, "the starter's own volume must be unchanged"


def _sim_rows(weights_and_gaps):
    """One priced sim row per (stat, weight, reconciled gap against a 0.50 mid)."""
    out = []
    for i, (stat, w, gap) in enumerate(weights_and_gaps):
        out.append({"ticker": f"T{i}", "stat": stat, "threshold": 1, "player_id": f"p{i}", "game_id": "g",
                    "family": "PLAYER_STAT", "support_state": "PRICED", "mid": 0.50, "p_market": 0.50,
                    "p_football": 0.50 + gap, "p_reconciled": 0.50 + gap, "reconcile_weight": w,
                    "football_mean": 1.0, "market_mean": 1.0, "final_mean": 1.0, "football_sd": 1.0,
                    "p_active": 1.0, "center_source": "test", "center_spread_home": -1.0, "center_total": 44.0,
                    "football_disagreement_vs_mid": gap})
    return out


def test_the_reconciled_ranking_admits_only_families_with_a_deployed_weight():
    """Week 2 2026: zero-weight families supplied 41% of the top-15 reconciled disagreements and three of
    the four priority boosts.  At weight 0 the mean IS the market's, so the gap is the untested shape."""
    from nfl_edge.handicap import sim_block
    rows = _sim_rows([("receptions", 0.0, -0.12), ("rec_yards", 0.0, 0.10), ("any_td", 0.25, 0.02)])
    view = sim_block.game_view(rows, {"sim_version": "sim-1.0.0", "run_id": "r"})
    ranked = view["largest_reconciled_disagreements"]
    assert [r["stat"] for r in ranked] == ["any_td"], "only a family with a deployed weight may be ranked"
    assert all((r["reconcile_weight"] or 0) > 0 for r in ranked)
    # the information is kept, it just carries no authority
    unranked = {r["stat"] for r in view["unranked_zero_weight_disagreements"]}
    assert unranked == {"receptions", "rec_yards"}
    assert "no authority" in view["ranking_basis"] or "carry no authority" in view["ranking_basis"]


def test_a_zero_weight_disagreement_cannot_move_the_review_priority():
    from nfl_edge.handicap import packet as PK
    from nfl_edge.handicap import sim_block
    base = {"game_id": "g", "kickoff_utc": None, "injuries": {"records": []}, "weather": {},
            "largest_moves": [], "markets": [], "data_health": [], "largest_disagreements": []}
    zero = sim_block.game_view(_sim_rows([("receptions", 0.0, -0.30)]), {})
    earned = sim_block.game_view(_sim_rows([("any_td", 0.25, 0.30)]), {})
    pz = PK.game_priority([dict(base, simulation=zero)])[0]
    pe = PK.game_priority([dict(base, simulation=earned)])[0]
    assert pz["priority_score"] == 0.0, "a 0.30 gap on a zero-weight family must add nothing"
    assert not any("reconciled simulation disagreement" in r for r in pz["reasons"])
    assert pe["priority_score"] > 0.0, "a family that earned a weight must still be able to raise priority"


def test_an_incoherent_game_is_never_published_as_priced(bundle_and_frames, bank, monkeypatch):
    """The backtest raises on a coherence failure; the prospective path used to publish the rows as PRICED
    with coherence_ok=false beside them.  206 contracts of the first live Week 2 slate were in that state."""
    from nfl_edge.sim import prospective as PR
    b, tf, pf = bundle_and_frames
    gi = FX.game_input(tf, pf)
    monkeypatch.setattr(PR.I, "historical_bank", lambda season: bank)
    monkeypatch.setattr(PR.S, "coherence_report", lambda res, tol=0: {"ok": False, "X:carries==rush_att": 7})
    pid = gi.home.players[gi.home.players["position"] == "QB"]["player_id"].iloc[0]
    ledger = [
        {"game_id": gi.game_id, "family": "TOTAL", "period": "FULL", "threshold": 44.0, "ticker": "TOT-44",
         "yes_bid": 0.48, "yes_ask": 0.52, "mid": 0.50, "operator": ">="},
        {"game_id": gi.game_id, "family": "PLAYER_STAT", "period": "FULL", "stat": "passing_yards",
         "player_kalshi_id": "K1", "threshold": 200.0, "ticker": "PY-200", "yes_bid": 0.48, "yes_ask": 0.52,
         "mid": 0.50, "operator": ">="},
        {"game_id": gi.game_id, "family": "PLAYER_STAT", "period": "FULL", "stat": "passing_yards",
         "player_kalshi_id": "K1", "threshold": 250.0, "ticker": "PY-250", "yes_bid": 0.28, "yes_ask": 0.32,
         "mid": 0.30, "operator": ">="},
    ]
    slate = {"games": {gi.game_id: {"input": gi, "kickoff": None, "center_diag": {}}}}
    rows = PR.price_slate(slate, ledger, b, None, n_sims=1500, run_id="r", observed_at="2026-09-16T00:00:00Z",
                          generated_at=datetime(2026, 9, 16, tzinfo=timezone.utc), player_map={"K1": pid},
                          verbose=lambda *a: None)
    assert rows, "the fixture must produce rows for the assertion to mean anything"
    assert not any(r["support_state"] in PR.COHERENCE_DEPENDENT_STATES for r in rows), \
        "no row of an incoherent game may claim a support state that asserts the identities held"
    assert any(r["support_state"] == "UNSUPPORTED_COHERENCE" for r in rows)
    assert all(r["coherence_ok"] is False for r in rows)
    # and the negative control: coherent again, and the same rows price
    monkeypatch.setattr(PR.S, "coherence_report", lambda res, tol=0: {"ok": True})
    ok = PR.price_slate(slate, ledger, b, None, n_sims=1500, run_id="r", observed_at="2026-09-16T00:00:00Z",
                        generated_at=datetime(2026, 9, 16, tzinfo=timezone.utc), player_map={"K1": pid},
                        verbose=lambda *a: None)
    assert any(r["support_state"] in PR.COHERENCE_DEPENDENT_STATES for r in ok)


def test_a_gap_that_contradicts_its_own_football_view_is_not_ranked():
    """The reconciled probability sits on the market's ESTIMATED mean, which on a thin ladder can
    contradict the market's own mid.  The top-ranked Thursday row of the first live Week 2 slate was
    +0.096 above the mid on a football view of -0.029.  That is the estimator, not a football opinion."""
    from nfl_edge.handicap import sim_block
    rows = _sim_rows([("any_td", 0.25, 0.30), ("any_td", 0.25, 0.04)])
    rows[0]["football_disagreement_vs_mid"] = -0.03      # reconciled says +0.30, football says -0.03
    view = sim_block.game_view(rows, {})
    ranked = view["largest_reconciled_disagreements"]
    assert [r["disagreement_vs_mid"] for r in ranked] == [0.04], \
        "the larger gap contradicts its own football view and must not be ranked"
    flipped = view["earned_but_contradicts_football_view"]
    assert len(flipped) == 1 and flipped[0]["disagreement_vs_mid"] == 0.30
    assert "opposite" in view["ranking_basis"].lower()


def test_the_ranking_filters_can_only_remove_rows_never_invent_one():
    from nfl_edge.handicap import sim_block
    rows = _sim_rows([("any_td", 0.25, 0.20), ("receptions", 0.0, -0.30), ("any_td", 0.25, 0.05)])
    rows[0]["football_disagreement_vs_mid"] = -0.10
    view = sim_block.game_view(rows, {})
    tickers = {r["ticker"] for r in view["largest_reconciled_disagreements"]}
    assert tickers <= {r["ticker"] for r in rows}
    # every priced row lands in exactly one of the three lists, so nothing is silently dropped
    everywhere = (tickers
                  | {r["ticker"] for r in view["unranked_zero_weight_disagreements"]}
                  | {r["ticker"] for r in view["earned_but_contradicts_football_view"]})
    assert everywhere == {r["ticker"] for r in rows}


def test_the_latest_sim_artifact_is_chosen_by_run_stamp_not_by_root_path(tmp_path):
    """The packet passes (market_data_root, repo_root).  Sorting full paths made the root whose name
    sorts last win: on the runner "/tmp/md" sorts after "/home/runner/work/...", and the market-data
    clone is fetched before this cycle's projections are published, so the live packet of 2026-09-16
    22:19Z read sim run 20260916T213544Z while 20260916T215549Z sat in the repo -- two hours stale
    against the ledger it was pricing."""
    from nfl_edge.handicap import sim_block

    def write(root, run_id):
        d = tmp_path / root / "data" / "shadow" / "sim" / "2026-09-16"
        d.mkdir(parents=True, exist_ok=True)
        p = d / f"{run_id}.sim-1.0.0.projections.jsonl.gz"
        with gzip.open(p, "wt") as f:
            f.write(json.dumps({"ticker": "T", "run_id": run_id}) + "\n")
        (d / f"{run_id}.sim-1.0.0.manifest.json").write_text(json.dumps({"run_id": run_id}))
        return str(tmp_path / root)

    repo = write("home_runner_work", "20260916T215549Z")   # this cycle, sorts FIRST by path
    md = write("tmp_md", "20260916T213544Z")               # last cycle, sorts LAST by path
    at = datetime(2026, 9, 16, 22, 19, 39, tzinfo=timezone.utc)
    rows, man = sim_block.load_latest((md, repo), at_or_before=at)
    assert man["run_id"] == "20260916T215549Z", "the newest RUN STAMP must win, whatever root it is in"
    # order of the roots must not matter
    rows2, man2 = sim_block.load_latest((repo, md), at_or_before=at)
    assert man2["run_id"] == "20260916T215549Z"
    # and the cutoff still binds: at 21:40 only the 21:35:44 run is eligible, never the 21:55:49 one
    _, man3 = sim_block.load_latest((md, repo), at_or_before=datetime(2026, 9, 16, 21, 40, tzinfo=timezone.utc))
    assert man3["run_id"] == "20260916T213544Z", "an artifact stamped after the instant may not be selected"
    assert sim_block.load_latest((md, repo), at_or_before=datetime(2026, 9, 16, 21, 0, tzinfo=timezone.utc)) == (None, None)


def test_coherence_report_asserts_the_quarterback_passing_touchdown_identity(bundle_and_frames, bank):
    """The engine credits the starter a share of the team's passing touchdowns and routes the remainder
    to the next quarterback, or to OTHER when there is none, so this identity holds BY CONSTRUCTION --
    which is why it was never asserted.  An identity that holds by construction and is never checked is
    one a later change to that routing can break silently, and the fail-closed production path can only
    refuse a game whose failure coherence_report actually reports.  Attempts and passing yards were
    already covered; passing touchdowns were not."""
    b, tf, pf = bundle_and_frames
    b = _bundle_with_a_starter_tail(b)
    gi = _one_qb_game(tf, pf)
    res = S.simulate(gi, b, n=3000, bank=bank)
    rep = S.coherence_report(res)

    key = f"{gi.home.team}:qb_pass_td==pass_td"
    assert key in rep, "the quarterback passing-touchdown identity must be reported, not merely true"
    assert rep[key] == 0
    assert rep["ok"], "adding the check must not fail a game that satisfies it"

    # ... and the teeth: a violation is actually caught rather than reported as zero
    qb = res.player[gi.home.qb1]
    qb["pass_td"] = qb["pass_td"] + 1
    broken = S.coherence_report(res)
    assert broken[key] == 1
    assert not broken["ok"], "a broken passing-touchdown identity must fail the game"
