"""The Wave-2 prospective scorer on SYNTHETIC records whose correct answers are known exactly. Written and frozen
before any real Wave-2 prospective record existed (PROSPECTIVE_PROTOCOL.md section 5)."""
import copy
import gzip
import hashlib
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.sim import backtest as Bt, baseline_report as BR, script_v2 as V, wave2_eval as E, wave2_score as W  # noqa: E402

UTC = timezone.utc
KO0 = datetime(2026, 10, 11, 17, 0, tzinfo=UTC)
QL = Bt.QLEVELS


# ------------------------------------------------------------------------------------------ synthetic records
def pmf_d(probs: dict) -> dict:
    lo, hi = min(probs), max(probs)
    return {"lo": lo, "p": [probs.get(k, 0.0) for k in range(lo, hi + 1)]}


def yard_d(mean: float, spread: float = 10.0) -> dict:
    return {"mean": mean, "q": [round(float(v), 1) for v in np.maximum(0, mean + spread * (QL - 0.5) * 3)]}


def players(t_shift=0, c_shift=0):
    """H1: a receiver (targets ~5, receptions ~3, rec_yards 40); H2: a back (carries ~10); H3: below every floor."""
    return {"H1": {"team": "HHH", "targets": pmf_d({4 + t_shift: 0.25, 5 + t_shift: 0.5, 6 + t_shift: 0.25}),
                   "receptions": pmf_d({2: 0.3, 3: 0.4, 4: 0.3}), "rec_yards": yard_d(40.0)},
            "H2": {"team": "HHH", "carries": pmf_d({9 + c_shift: 0.3, 10 + c_shift: 0.4, 11 + c_shift: 0.3}), "rush_yards": yard_d(45.0)},
            "H3": {"team": "HHH", "targets": pmf_d({0: 0.9, 1: 0.1})},
            "A1P": {"team": "AAA", "targets": pmf_d({3: 0.5, 4: 0.5})}}


def margin_block(m_probs: dict, t_probs: dict, cells):
    return {"margin_pmf": pmf_d({m + 80: p for m, p in m_probs.items()}), "total_pmf": pmf_d(t_probs), "v2_cells": list(cells)}


CELLS = [0.1, 0.1, 0.1, 0.1, 0.2, 0.1, 0.1, 0.1, 0.1]


def game_rec(gid, window, kickoff, cutoff, horizon="T24", arms=None, avail=None):
    base = {"players": players(), "teams": {}}
    a = {k: copy.deepcopy(base) for k in ("A0", "S1", "Q1", "A1", "M1")}
    for k in ("A0", "M1"):
        a[k].update(margin_block({3: 0.2, 7: 0.3, -3: 0.5}, {44: 0.5, 48: 0.5}, CELLS))
    for k, v in (arms or {}).items():
        a[k].update(v)
    return {"window": window, "state": "OK", "kickoff_utc": kickoff.isoformat(), "cutoff": cutoff.isoformat(),
            "minutes_to_kickoff": (kickoff - cutoff).total_seconds() / 60, "horizon": horizon,
            "home_team": "HHH", "away_team": "AAA", "centre": {"spread_home": -3.0, "total": 44.0, "source": "test"},
            "arms": a, "coherence": {k: True for k in a}, "a1_identical_to_a0": horizon != "T0_INACTIVES",
            "avail_state": avail or {"H1": "EXPECTED_ACTIVE", "H2": "QUESTIONABLE", "H3": "EXPECTED_ACTIVE", "A1P": "EXPECTED_ACTIVE"},
            "m1k_exact_margin_pmf": {"3": 0.25, "7": 0.25, "-3": 0.5}}


def write(root, gid, window, generated_at, kickoff, *, horizon="T24", arms=None, dry=False, comps=W.FROZEN_COMPONENTS_SHA256,
          version="wave2-prospective-1.1.0", avail=None):
    run = generated_at.strftime("%Y%m%dT%H%M%SZ")
    doc = {"wave2_version": version, "run_id": run, "generated_at": generated_at.isoformat(), "cutoff": generated_at.isoformat(),
           "season": 2026, "week": 6, "prospective_cutoff": W.PROSPECTIVE_CUTOFF, "dry_run": dry, "research_only": True,
           "betting_authority": "NONE", "inputs": {"components_sha256": comps},
           "games": {gid: game_rec(gid, window, kickoff, generated_at, horizon, arms, avail)}}
    d = os.path.join(root, "data", "research", "wave2", run[:4] + "-" + run[4:6] + "-" + run[6:8])
    os.makedirs(d, exist_ok=True)
    p = os.path.join(d, f"{gid}.{window}.{run}.wave2.json.gz")
    with open(p, "wb") as f:
        f.write(gzip.compress(json.dumps(doc).encode(), mtime=0))
    return p


def recs(root):
    import glob
    return [W.read_record(p) for p in sorted(glob.glob(os.path.join(root, "data", "research", "wave2", "*", "*.gz")))]


def final(home=24, away=21, **pl):
    base = {"H1": {"targets": 5, "receptions": 3, "rec_yards": 41}, "H2": {"carries": 10, "rush_yards": 44}, "A1P": {"targets": 4}}
    base.update(pl)
    return {"status": "FINAL", "home_score": home, "away_score": away, "players": base}


def gid(i):
    return f"2026_06_A{i:02d}_HHH"


def many(root, n, *, horizon="T24", arms=None):
    out = {}
    for i in range(n):
        ko = KO0 + timedelta(hours=i)
        write(root, gid(i), "LATE", ko - timedelta(minutes=60), ko, horizon=horizon, arms=arms)
        out[gid(i)] = final()
    return out


# ------------------------------------------------------------------------------------------ 1-5 selection
def test_late_is_selected_over_early(tmp_path):
    write(tmp_path, gid(0), "EARLY", KO0 - timedelta(minutes=150), KO0)
    pl = write(tmp_path, gid(0), "LATE", KO0 - timedelta(minutes=60), KO0)
    sel, sup = W.select(W.candidates(recs(tmp_path)))
    assert sel[gid(0)]["path"] == pl and sel[gid(0)]["window"] == "LATE" and len(sup) == 1


def test_early_is_used_when_late_is_absent(tmp_path):
    pe = write(tmp_path, gid(0), "EARLY", KO0 - timedelta(minutes=150), KO0)
    sel, _ = W.select(W.candidates(recs(tmp_path)))
    assert sel[gid(0)]["path"] == pe and sel[gid(0)]["window"] == "EARLY"


def test_post_kickoff_records_are_refused(tmp_path):
    write(tmp_path, gid(0), "LATE", KO0 + timedelta(minutes=1), KO0)                    # generated after kickoff
    write(tmp_path, gid(1), "LATE", KO0 - timedelta(minutes=60), KO0)                   # schedule kickoff moved earlier
    c = W.candidates(recs(tmp_path), kickoffs={gid(1): (KO0 - timedelta(minutes=90)).isoformat()})
    reasons = {x["game_id"]: x["reason"] for x in c}
    assert reasons[gid(0)] == "generated at or after kickoff"
    assert reasons[gid(1)] == "generated at or after kickoff"
    assert W.select(c)[0] == {}


def test_other_invalid_records_are_excluded_with_a_reason(tmp_path):
    write(tmp_path, gid(0), "LATE", KO0 - timedelta(minutes=60), KO0, dry=True)
    write(tmp_path, gid(1), "LATE", KO0 - timedelta(minutes=60), KO0, comps="0" * 64)
    old = datetime(2026, 10, 5, 12, 0, tzinfo=UTC)
    write(tmp_path, gid(2), "LATE", old - timedelta(minutes=60), old)
    write(tmp_path, gid(3), "LATE", KO0 - timedelta(minutes=60), KO0, version="wave2-prospective-1.0.0")
    r = {x["game_id"]: x["reason"] for x in W.candidates(recs(tmp_path))}
    assert r[gid(0)] == "dry-run record"
    assert r[gid(1)].startswith("components differ")
    assert r[gid(2)] == "game kicked off before the PROSPECTIVE CUTOFF"
    assert "not accepted" in r[gid(3)]


def test_a_missing_prediction_is_never_reconstructed(tmp_path):
    write(tmp_path, gid(0), "LATE", KO0 - timedelta(minutes=60), KO0)
    before = sorted(os.listdir(tmp_path / "data" / "research" / "wave2" / "2026-10-11"))
    out = W.score(recs(tmp_path), {gid(0): final(), gid(1): final()})
    assert set(out["records"]["used"]) == {gid(0)}
    assert out["arms"]["S1"]["n_eligible_games"] == 1, "a game without a record is missing, not imputed"
    assert sorted(os.listdir(tmp_path / "data" / "research" / "wave2" / "2026-10-11")) == before


def test_prediction_files_are_byte_identical_after_scoring(tmp_path):
    outs = many(tmp_path, 3)
    import glob
    paths = sorted(glob.glob(str(tmp_path / "data" / "research" / "wave2" / "*" / "*.gz")))
    h = {p: (hashlib.sha256(open(p, "rb").read()).hexdigest(), os.stat(p).st_mtime_ns) for p in paths}
    W.score(recs(tmp_path), outs, interim=True)
    assert {p: (hashlib.sha256(open(p, "rb").read()).hexdigest(), os.stat(p).st_mtime_ns) for p in paths} == h


# ------------------------------------------------------------------------------------------ 6-10 populations
def test_missing_outcomes_are_counted_never_guessed(tmp_path):
    outs = many(tmp_path, 3)
    outs[gid(1)] = {"status": "UNAVAILABLE", "reason": "no box score rows in player_games yet"}
    del outs[gid(2)]
    out = W.score(recs(tmp_path), outs)
    assert out["outcomes"]["games_with_outcome"] == [gid(0)]
    assert out["outcomes"]["games_missing_outcome"] == {gid(1): "no box score rows in player_games yet", gid(2): "no outcome supplied"}
    assert out["arms"]["S1"]["n_eligible_games"] == 1


def test_a_losing_observation_is_retained(tmp_path):
    good = {"S1": {"players": players()}}
    outs = many(tmp_path, 2, arms=good)
    ko = KO0 + timedelta(hours=5)
    write(tmp_path, gid(9), "LATE", ko - timedelta(minutes=60), ko, arms={"S1": {"players": players(t_shift=8, c_shift=8)}})
    outs[gid(9)] = final()
    out = W.score(recs(tmp_path), outs, interim=True)
    it = out["arms"]["S1"]["interim"]
    assert it["primary"]["n_games"] == 3 and it["primary"]["mean"] > 0, "the bad game stays in and makes S1 look worse"


def test_a1_t0_and_t24_populations_never_mix(tmp_path):
    ko1 = KO0 + timedelta(hours=1)
    # T0 game: A1 removes the questionable back's bias exactly; T24 game: A1 is far worse
    write(tmp_path, gid(0), "LATE", KO0 - timedelta(minutes=60), KO0, horizon="T0_INACTIVES", arms={"A1": {"players": players()}})
    write(tmp_path, gid(1), "LATE", ko1 - timedelta(minutes=60), ko1, horizon="T24", arms={"A1": {"players": players(c_shift=9)}})
    outs = {gid(0): final(H2={"carries": 13, "rush_yards": 44}), gid(1): final(H2={"carries": 13, "rush_yards": 44})}
    out = W.score(recs(tmp_path), outs, interim=True)
    a1 = out["arms"]["A1"]
    assert a1["n_eligible_games"] == 1 and a1["t24_diagnostic"]["n_games"] == 1
    assert a1["interim"]["primary"]["n_games"] == 1 and a1["interim"]["primary"]["mean"] == pytest.approx(0.0)
    assert a1["t24_diagnostic"]["primary"]["n_games"] == 1 and a1["t24_diagnostic"]["primary"]["mean"] > 0
    assert out["horizons"] == {"T0_INACTIVES": 1, "T24": 1}


def test_the_a0_floor_defines_the_player_population(tmp_path):
    cand = players(); cand["H3"]["targets"] = pmf_d({8: 1.0})       # candidate puts H3 far above the floor
    a0 = players(); a0["H1"]["targets"] = pmf_d({1: 1.0})          # A0 puts H1 below the floor
    outs = many(tmp_path, 1, arms={"A0": {"players": a0}, "S1": {"players": cand}})
    sel, _ = W.select(W.candidates(recs(tmp_path)))
    P, _ = W.player_frame(sel, outs)
    t = P[P["stat"] == "targets"]
    assert set(t["player_id"]) == {"A1P"}, "H3 (A0 below floor) is out; H1 is out because A0 is below the floor"
    assert (P["a0_mean"] >= P["stat"].map(Bt.FLOORS)).all()


def test_a_candidate_cannot_remove_a_row_where_it_does_badly(tmp_path, monkeypatch):
    monkeypatch.setitem(W.MIN_GAMES, "S1", 2)
    cand = players(); del cand["H2"]["carries"]
    outs = many(tmp_path, 2, arms={"S1": {"players": cand}})
    out = W.score(recs(tmp_path), outs)
    s1 = out["arms"]["S1"]
    assert out["integrity_failures"]["S1"] == {gid(0): ["H2:carries"], gid(1): ["H2:carries"]}
    assert s1["at_minimum"]["gates"]["zero_integrity_or_coherence_failures"] is False
    assert s1["promotion"] == "NOT_PROMOTED_AT_MINIMUM" and s1["n_eligible_games"] == 2


# ------------------------------------------------------------------------------------------ 11-15 metrics
def test_crps_of_a_point_mass_equals_the_absolute_error():
    q = W.pmf_quantiles(W.dense_pmf(pmf_d({5: 1.0}), 31))
    assert np.all(q == 5)
    assert BR.crps_rows(q[None, :], np.array([3.0]))[0] == pytest.approx(2.0)
    # a two-point pmf: exact pinball average over the 50 stored levels
    q2 = W.pmf_quantiles(W.dense_pmf(pmf_d({0: 0.5, 1: 0.5}), 31))
    assert list(q2) == [0.0] * 25 + [1.0] * 25
    expect = 2 * np.mean(np.where(1 - q2 >= 0, QL * (1 - q2), (QL - 1) * (1 - q2)))
    assert BR.crps_rows(q2[None, :], np.array([1.0]))[0] == pytest.approx(expect) == pytest.approx(np.mean(QL[:25])) == pytest.approx(0.25)


def test_pmf_randomized_pit_is_deterministic_and_exact():
    pm = np.vstack([W.dense_pmf(pmf_d({2: 1.0}), 31), W.dense_pmf(pmf_d({0: 0.5, 1: 0.5}), 31), W.dense_pmf(pmf_d({9: 1.0}), 31)])
    y = np.array([2.0, 1.0, 3.0])
    a, b = BR.randomized_pit(pm, y, "targets"), BR.randomized_pit(pm, y, "targets")
    u = np.random.default_rng(W.SEED).random(3)
    assert np.array_equal(a, b)
    assert a[0] == pytest.approx(u[0]) and a[1] == pytest.approx(0.5 + 0.5 * u[1]) and a[2] == 0.0


def _m1_row(tmp_path, home, away):
    outs = many(tmp_path, 1)
    outs[gid(0)] = final(home=home, away=away)
    sel, _ = W.select(W.candidates(recs(tmp_path)))
    return W.margin_frame(sel, outs).iloc[0]


def test_m1_exact_margin_log_score_is_the_hand_value(tmp_path):
    r = _m1_row(tmp_path, 24, 21)                    # margin +3
    assert r["M1_log_score"] == pytest.approx(np.log(0.25))      # exact M1-K pmf
    assert r["M0_log_score"] == pytest.approx(np.log(0.2))       # incumbent draws pmf


def test_the_log_score_floor_is_1e_4(tmp_path):
    r = _m1_row(tmp_path, 30, 10)                    # margin +20: zero probability under both
    assert r["M1_log_score"] == pytest.approx(np.log(1e-4)) and r["M0_log_score"] == pytest.approx(np.log(1e-4))
    assert r["M1_p_exact"] == 0.0


def test_game_script_v2_multiclass_brier_is_the_hand_value(tmp_path):
    r = _m1_row(tmp_path, 24, 21)
    cell = V.CELLS.index(V.classify(3.0, 45.0, -3.0, 44.0))
    p = np.array(CELLS); onehot = np.eye(9)[cell]
    assert r["cell"] == cell
    assert r["M1_v2_brier"] == pytest.approx(float(np.sum((p - onehot) ** 2)))


def test_total_ladder_brier_is_the_hand_value(tmp_path):
    r = _m1_row(tmp_path, 24, 21)                    # total 45; pmf 44 / 48 at 0.5
    ks = np.floor(44.0) + np.arange(-15, 15) + 0.5
    surv = np.where(ks < 44, 1.0, np.where(ks < 48, 0.5, 0.0))
    assert r["M0_total_ladder_brier"] == pytest.approx(float(np.mean((surv - (45 > ks)) ** 2)))


# ------------------------------------------------------------------------------------------ 16-17 bootstrap
def test_the_bootstrap_resamples_games_not_player_rows():
    rng = np.random.default_rng(1)
    rows = pd.DataFrame({"game_id": np.repeat(["g1", "g2", "g3", "g4"], [1, 40, 3, 7]),
                         "stat": "targets", "arm_crps": rng.random(51), "a0_crps": rng.random(51) + 0.5})
    games = ["g1", "g2", "g3", "g4"]
    G = W.ratio_game_sums(rows, games, "targets", "arm_crps", "a0_crps")
    b = W.game_boot(G, W.ratio_fn)
    assert b["n_games"] == 4
    # collapsing each game to ONE row with the same sums gives the identical interval: rows are not units
    one = rows.groupby("game_id", as_index=False)[["arm_crps", "a0_crps"]].sum().assign(stat="targets")
    b1 = W.game_boot(W.ratio_game_sums(one, games, "targets", "arm_crps", "a0_crps"), W.ratio_fn)
    assert {k: pytest.approx(v) for k, v in b1.items()} == b


def test_the_bootstrap_is_deterministic_with_seed_20261005():
    G = np.random.default_rng(3).random((30, 2)) + 0.1
    a, b = W.game_boot(G, W.ratio_fn), W.game_boot(G, W.ratio_fn)
    assert a == b and W.SEED == 20261005 and W.B == 2000
    rng = np.random.default_rng(20261005)
    bs = [W.ratio_fn(np.bincount(rng.integers(0, 30, 30), minlength=30) @ G) for _ in range(2000)]
    assert a["lo"] == pytest.approx(np.nanquantile(bs, 0.025)) and a["hi"] == pytest.approx(np.nanquantile(bs, 0.975))


def test_scorer_primaries_equal_the_development_evaluation_semantics(tmp_path):
    outs = many(tmp_path, 4, arms={"S1": {"players": players(t_shift=1)}})
    sel, _ = W.select(W.candidates(recs(tmp_path)))
    P, _ = W.player_frame(sel, outs)
    d = W.paired_arm(P, "S1"); games = sorted(sel)
    assert W.s1_primary_from_sums(W.s1_game_sums(d, games).sum(axis=0)) == pytest.approx(E.s1_primary(d))
    d1 = W.paired_arm(P, "A1").assign(questionable=lambda x: x["avail_state"] == "QUESTIONABLE")
    assert W.a1_primary_from_sums(W.a1_game_sums(d1, games).sum(axis=0)) == pytest.approx(E.a1_primary_delta(d1))


def test_scoring_is_deterministic(tmp_path):
    outs = many(tmp_path, 3, arms={"S1": {"players": players(t_shift=1)}})
    a = W.score(recs(tmp_path), outs, interim=True); b = W.score(recs(tmp_path), outs, interim=True)
    assert json.dumps(a, sort_keys=True, default=str) == json.dumps(b, sort_keys=True, default=str)


# ------------------------------------------------------------------------------------------ 18-21 gates and status
def test_below_the_minimum_no_promotion_is_possible(tmp_path):
    outs = many(tmp_path, 3, arms={"S1": {"players": players(t_shift=0)}})
    out = W.score(recs(tmp_path), outs, interim=True)
    for arm in ("S1", "A1", "M1"):
        a = out["arms"][arm]
        assert a["evidence_status"] == "COLLECTING" and a["promotion"] is None and "at_minimum" not in a
    assert out["arms"]["S1"]["interim"]["label"].startswith("INTERIM")


def test_exactly_reaching_the_minimum_applies_the_gate_once(tmp_path, monkeypatch):
    monkeypatch.setitem(W.MIN_GAMES, "S1", 3)
    outs = many(tmp_path, 3)
    out = W.score(recs(tmp_path), outs)
    s1 = out["arms"]["S1"]
    assert s1["evidence_status"] == "GATE_APPLIED_AT_MINIMUM" and s1["analysis_set"] == [gid(0), gid(1), gid(2)]
    assert s1["promotion"] in ("PROMOTION_CANDIDATE", "NOT_PROMOTED_AT_MINIMUM")
    assert s1["promotion"] == "NOT_PROMOTED_AT_MINIMUM", "an identical candidate cannot show an improvement"
    # a fourth game never changes the analysis set or the gate
    ko = KO0 + timedelta(hours=9)
    write(tmp_path, gid(9), "LATE", ko - timedelta(minutes=60), ko); outs[gid(9)] = final()
    out2 = W.score(recs(tmp_path), outs)
    assert out2["arms"]["S1"]["analysis_set"] == s1["analysis_set"]
    assert json.dumps(out2["arms"]["S1"]["at_minimum"], sort_keys=True) == json.dumps(s1["at_minimum"], sort_keys=True)
    assert out2["arms"]["S1"]["descriptive_all_eligible"]["label"].startswith("DESCRIPTIVE")


def test_q1_stays_rejected_whatever_it_does(tmp_path, monkeypatch):
    for k in W.MIN_GAMES:
        monkeypatch.setitem(W.MIN_GAMES, k, 1)
    outs = many(tmp_path, 2, arms={"Q1": {"players": players()}})
    q1 = W.score(recs(tmp_path), outs, interim=True)["arms"]["Q1"]
    assert q1["development_status"] == "REJECTED_AT_DEVELOPMENT" and q1["promotion"] is None
    assert q1["evidence_status"] == "DESCRIPTIVE_ONLY" and "gates" not in json.dumps(q1)


def test_risk1_refuses_its_registered_test_below_397_games():
    obs = pd.DataFrame({"game_id": ["g"] * 3, "y": [1, 0, 1]})
    with pytest.raises(PermissionError):
        W.risk1_registered_test(obs, 396)
    out = W.score([], {}, risk1_eligible=[(f"2026-10-{1 + i % 28:02d}T17:00:00+00:00", f"g{i}") for i in range(396)], risk1_obs=obs)
    assert out["RISK1"]["evidence_status"] == "COLLECTING" and out["RISK1"]["result"] is None and out["RISK1"]["n_required"] == 397


def test_frozen_constants_match_the_addendum():
    assert W.MIN_GAMES == {"S1": 64, "A1": 64, "M1": 672, "RISK1": 397}
    assert W.DEV_STATUS == {"S1": "PROSPECTIVE_CHALLENGER", "A1": "PROSPECTIVE_CHALLENGER", "M1": "PROSPECTIVE_CHALLENGER",
                            "Q1": "REJECTED_AT_DEVELOPMENT", "RISK1": "COLLECTING"}
    assert W.PROSPECTIVE_CUTOFF == "2026-10-05T16:14:02+00:00" and (W.B, W.SEED, W.NI_MARGIN) == (2000, 20261005, 0.005)
    comps = os.path.join(ROOT, "research", "game_script_v2", "wave2", "components_2026.json")
    assert hashlib.sha256(open(comps, "rb").read()).hexdigest() == W.FROZEN_COMPONENTS_SHA256
    add = open(os.path.join(ROOT, "research", "game_script_v2", "wave2", "PREREGISTRATION_ADDENDUM.md")).read()
    for n in ("**64** (floor)", "**672**", "**397**", W.FROZEN_COMPONENTS_SHA256):
        assert n in add


# ------------------------------------------------------------------------------------------ 22-23 authority
def test_scorer_output_carries_no_authority(tmp_path):
    out = W.score(recs(tmp_path), many(tmp_path, 2), interim=True)
    assert out["research_only"] is True
    for k in ("betting_authority", "staking_authority", "bet_pass_authority", "price_limit_authority", "unit_size_authority",
              "reconciliation_weight_authority", "model_probability_authority"):
        assert out[k] == "NONE"

    def walk(o):
        if isinstance(o, dict):
            for k, v in o.items():
                if "authority" in k:
                    assert v in ("NONE", None), (k, v)
                assert k not in ("stake", "units", "bet", "price_limit", "reconcile_weight", "decision"), k
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(out)


def test_no_decision_path_reads_the_scorer_or_its_output():
    keys = ("wave2_score", "wave2/prospective", "score_2026", "wave2_eval")
    for d in ("handicap", "pricing", "board", "evaluation"):
        base = os.path.join(ROOT, "nfl_edge", d)
        if not os.path.isdir(base):
            continue
        for f in os.listdir(base):
            if f.endswith(".py"):
                src = open(os.path.join(base, f)).read()
                for k in keys:
                    assert k not in src, f"nfl_edge/{d}/{f} reads {k}"


def test_the_runner_writes_the_record_version_the_scorer_accepts():
    import importlib.util
    spec = importlib.util.spec_from_file_location("w2p", os.path.join(ROOT, "scripts", "sim", "wave2_prospective.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    assert m.WAVE2_VERSION in W.ACCEPTED_RECORD_VERSIONS
    src = open(os.path.join(ROOT, "scripts", "sim", "wave2_prospective.py")).read()
    for field in ('"avail_state"', '"m1k_exact_margin_pmf"', '"total_pmf"', '"home_team"', '"away_team"'):
        assert field in src, f"the runner no longer writes {field}, which the scorer requires"
