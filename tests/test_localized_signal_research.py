"""WS3: prospective localized-signal research -- registry order, preregistration, future-only evaluation.

The failure this file guards against is the oldest one in the programme: a pattern noticed in one week, then
"confirmed" by numbers that include the same week, a window chosen after watching it, a bar set after seeing
the result, or a sample counted in contracts instead of games. Each test below pins one of those doors shut.
"""
from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import random
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from nfl_edge.arms import registry as R                                   # noqa: E402
from nfl_edge.arms import scorecard as AS                                  # noqa: E402
from nfl_edge.arms.report import render_deviation_signal                   # noqa: E402
from nfl_edge.evaluation import scorecard_v3 as S3                         # noqa: E402
from nfl_edge.research import hypothesis_registry_v2 as HR                 # noqa: E402
from nfl_edge.research import localized_signals as LS                      # noqa: E402

W = lambda s, lo, hi: {"season": s, "week_lo": lo, "week_hi": hi}         # noqa: E731


def _add(path, hid="H", gen=W(2026, 2, 2), fut=W(2026, 3, 18), **kw):
    return HR.add(hid=hid, market_family="f", condition="c", direction="d", expected_mechanism="m", evaluation_metric="e",
                  minimum_sample=1, generation_window=gen, future_test_window=fut, generated_by="test", path=path, **kw)


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


# ============================================================================ window ordering
def test_a_test_window_before_the_generation_window_is_refused_even_without_overlap(tmp_path):
    p = str(tmp_path / "h.jsonl")
    with pytest.raises(HR.RegistryError, match="AFTER"):
        _add(p, gen=W(2026, 5, 5), fut=W(2026, 1, 4))           # no overlap, still a hindcast
    with pytest.raises(HR.RegistryError):
        _add(p, gen=W(2026, 5, 5), fut=W(2025, 10, 18))         # an earlier season is never after
    with pytest.raises(HR.RegistryError):
        _add(p, gen=W(2026, 2, 3), fut=W(2026, 3, 18))          # overlap at week 3
    assert _add(p, hid="OK1", gen=W(2026, 5, 5), fut=W(2026, 6, 18))["status"] == "GENERATED"
    assert _add(p, hid="OK2", gen=W(2026, 17, 18), fut=W(2027, 1, 4))["status"] == "GENERATED"


def test_transition_enforces_order_and_the_binding_registered_window(tmp_path):
    p = str(tmp_path / "h.jsonl")
    _add(p, gen=W(2026, 5, 5), fut=W(2026, 6, 12))
    pre = lambda win: HR.preregister("H", test_window=win, thresholds=HR.PREREGISTERED_THRESHOLDS,   # noqa: E731
                                     evaluation_plan="p", path=p)
    with pytest.raises(HR.RegistryError, match="only through preregister"):
        HR.transition("H", "PREREGISTERED", test_window=W(2026, 7, 10), path=p)      # a bare transition freezes nothing
    with pytest.raises(HR.RegistryError):
        pre(W(2026, 1, 4))                                                            # before generation
    with pytest.raises(HR.RegistryError, match="binding"):
        pre(W(2026, 6, 18))                                                           # outside the registered window
    r = pre(W(2026, 7, 10))
    assert r["registered_future_test_window"] == W(2026, 6, 12) and r["test_window"] == W(2026, 7, 10)
    HR.transition("H", "TESTING", path=p)
    with pytest.raises(HR.RegistryError):
        HR.transition("H", "SUPPORTED", test_window=W(2026, 6, 10), result={"z": 3}, path=p)   # wider than the chosen window
    assert HR.current(p)["H"]["status"] == "TESTING"


# ============================================================================ preregistration
def test_preregistration_at_or_after_the_first_test_kickoff_is_refused(tmp_path):
    p = str(tmp_path / "h.jsonl")
    _add(p)
    kick = "2026-09-25T00:15:00Z"
    for late in ("2026-09-25T00:15:00Z", "2026-09-25T03:00:00+00:00"):
        with pytest.raises(HR.RegistryError, match="not before the first test kickoff"):
            HR.preregister("H", test_window=W(2026, 3, 18), thresholds=HR.PREREGISTERED_THRESHOLDS, evaluation_plan="p",
                           preregistered_at=late, first_test_kickoff_utc=kick, path=p)
    assert HR.current(p)["H"]["status"] == "GENERATED", "a refused preregistration wrote a line"
    r = HR.preregister("H", test_window=W(2026, 3, 18), thresholds=HR.PREREGISTERED_THRESHOLDS, evaluation_plan="p",
                       preregistered_at="2026-09-24T05:00:00Z", first_test_kickoff_utc=kick, path=p)
    assert r["status"] == "PREREGISTERED"
    assert r["preregistration"]["thresholds_sha"] == HR.thresholds_sha(HR.PREREGISTERED_THRESHOLDS)
    with pytest.raises(HR.RegistryError):                                              # only GENERATED can be preregistered
        HR.preregister("H", test_window=W(2026, 3, 18), thresholds=HR.PREREGISTERED_THRESHOLDS, evaluation_plan="p", path=p)


def test_preregistration_window_must_sit_inside_the_registered_window(tmp_path):
    p = str(tmp_path / "h.jsonl")
    _add(p, fut=W(2026, 3, 10))
    with pytest.raises(HR.RegistryError):
        HR.preregister("H", test_window=W(2026, 3, 18), thresholds={"x": 1}, evaluation_plan="p", path=p)
    with pytest.raises(HR.RegistryError):
        HR.preregister("H", test_window=W(2026, 2, 5), thresholds={"x": 1}, evaluation_plan="p", path=p)


def test_thresholds_are_conservative_and_consistent_with_the_eligibility_floors():
    t = HR.PREREGISTERED_THRESHOLDS
    assert t[HR.KIND_SLICE]["min_new_independent_games"] >= 16                 # WATCH floor
    assert t[HR.KIND_GAME_CENTRE]["min_directional_observations"] >= 20
    assert t[HR.KIND_GAME_CENTRE]["meaningful_deviation_points"] == 1.0
    assert t["no_automatic_promotion"] and t["generation_window_never_counts"]
    mc = HR.multiplicity(2)
    assert mc["alpha_adjusted"] == 0.025 and mc["z_adjusted"] > mc["z_95"]


# ============================================================================ register_candidates
def _cand(hid, week=2, eff=-0.02):
    return {"id": hid, "market_family": "model_arm*family_group", "segment": "model_arm*family_group", "segment_value": "A|F",
            "condition": "x", "direction": "model beats market", "effect_size": eff, "uncertainty": 0.005, "sample_size": 40,
            "game_count": 20, "minimum_sample": 30, "generation_window": W(2026, week, week), "future_test_window": W(2026, week + 1, 18),
            "hypothesis_kind": HR.KIND_SLICE}


def test_register_candidates_is_idempotent_and_writes_generated_only(tmp_path):
    p = str(tmp_path / "h.jsonl")
    got = HR.register_candidates([_cand("A"), _cand("B")], path=p)
    assert got["added"] == ["A", "B"]
    before = _sha(p)
    again = HR.register_candidates([_cand("A"), _cand("B")], path=p)
    assert again["added"] == [] and sorted(again["skipped_existing"]) == ["A", "B"]
    assert _sha(p) == before, "a re-run rewrote the registry"
    assert {r["status"] for r in HR.load(p)} == {"GENERATED"}
    bad = _cand("C"); bad["future_test_window"] = W(2026, 1, 1)
    out = HR.register_candidates([bad], path=p)
    assert out["refused"] and out["refused"][0]["id"] == "C" and "C" not in HR.current(p)


def test_seed_registry_copies_the_published_history_once(tmp_path):
    pub, loc = tmp_path / "pub.jsonl", tmp_path / "local" / "h.jsonl"
    HR.register_candidates([_cand("A")], path=str(pub))
    assert HR.seed_registry(str(loc), str(pub)) == "SEEDED_FROM_PUBLISHED"
    HR.register_candidates([_cand("B")], path=str(loc))
    assert HR.seed_registry(str(loc), str(pub)) == "LOCAL_EXISTS"
    assert set(HR.current(str(loc))) == {"A", "B"}, "the published history was lost"
    assert HR.seed_registry(str(tmp_path / "x.jsonl"), str(tmp_path / "missing.jsonl")) == "NEW_REGISTRY"


# ============================================================================ evaluate_prospective
def _slice_week(week, games=20, paired=60, eff=-0.03, se=0.005, clv=0.01):
    return {"season": 2026, "week": week, "games": games, "paired_n": paired, "effect": eff, "se": se,
            "mean_clv_mid": clv, "n_clv_ok": paired, "positive_clv_rate": 0.6, "market_toward_model_rate": 0.6,
            "pnl_net_per_contract": 0.01, "n_fee_known": paired}


def _preregistered_slice(tmp_path):
    p = str(tmp_path / "h.jsonl")
    HR.register_candidates([_cand("S")], path=p)
    HR.preregister("S", test_window=W(2026, 3, 18), thresholds=HR.PREREGISTERED_THRESHOLDS, evaluation_plan="p", path=p)
    return p


def test_the_generation_week_can_never_count(tmp_path):
    p = _preregistered_slice(tmp_path)
    h = HR.current(p)["S"]
    only_gen = HR.evaluate_prospective(h, {"by_week": [_slice_week(2, games=200, paired=2000)]})
    assert only_gen["new_independent_games"] == 0 and only_gen["evaluated_weeks"] == []
    assert only_gen["excluded_weeks"][0]["reason"].startswith("GENERATION_WINDOW")
    assert only_gen["suggested_status"] == "INCONCLUSIVE"
    mixed = HR.evaluate_prospective(h, {"by_week": [_slice_week(1), _slice_week(2, games=200), _slice_week(3, games=7)]})
    assert mixed["new_independent_games"] == 7 and [w for _, w in mixed["evaluated_weeks"]] == [3]
    assert {x["week"] for x in mixed["excluded_weeks"]} == {1, 2}


def test_evaluate_prospective_never_writes_and_never_promotes(tmp_path):
    p = _preregistered_slice(tmp_path)
    h = HR.current(p)["S"]
    snapshot, before = copy.deepcopy(h), _sha(p)
    overwhelming = {"by_week": [_slice_week(w, games=16, eff=-0.05, se=0.002) for w in range(3, 9)]}
    ev = HR.evaluate_prospective(h, overwhelming, n_under_test=1)
    assert ev["suggested_status"] == "SUPPORTED" and ev["trend"] == "PERSISTING"
    assert ev["suggestion_is_binding"] is False and ev["suggestion_note"] == HR.SUGGESTION_ONLY
    assert _sha(p) == before, "evaluate_prospective wrote to the registry"
    assert h == snapshot, "evaluate_prospective mutated its input"
    assert HR.current(p)["S"]["status"] == "PREREGISTERED", "a suggestion was applied"


def test_slice_trend_labels_and_the_game_floor(tmp_path):
    p = _preregistered_slice(tmp_path)
    h = HR.current(p)["S"]                                                # generation effect -0.02
    few = HR.evaluate_prospective(h, {"by_week": [_slice_week(3, games=15, eff=-0.05)]})
    assert few["trend"] == "INCONCLUSIVE" and few["direction_so_far"] == "PERSISTING" and few["suggested_status"] == "INCONCLUSIVE"
    rev = HR.evaluate_prospective(h, {"by_week": [_slice_week(3, games=16, eff=0.004, se=0.01)]})
    assert rev["trend"] == "REVERSING" and rev["suggested_status"] == "NOT_SUPPORTED"
    weak = HR.evaluate_prospective(h, {"by_week": [_slice_week(3, games=16, eff=-0.005, se=0.01)]})
    assert weak["trend"] == "WEAKENING" and weak["suggested_status"] == "INCONCLUSIVE"
    neg_clv = HR.evaluate_prospective(h, {"by_week": [_slice_week(3, games=40, eff=-0.05, se=0.002, clv=-0.01)]})
    assert neg_clv["suggested_status"] == "INCONCLUSIVE", "a model-edge suggestion needs mean CLV >= 0"


def test_a_generated_hypothesis_gets_description_but_no_suggestion(tmp_path):
    p = str(tmp_path / "h.jsonl")
    HR.register_candidates([_cand("G")], path=p)
    ev = HR.evaluate_prospective(HR.current(p)["G"], {"by_week": [_slice_week(3, games=100, eff=-0.05, se=0.001)]})
    assert ev["suggested_status"] is None and ev["new_independent_games"] == 100
    assert "not preregistered" in ev["suggestion_reason"]


# ============================================================================ game-centre deviation signal
def _gc_row(g, dev, move, *, week=3, mtk=40.0, arm_margin=None, snap=3.0, actual=0.0):
    dm = snap + dev if arm_margin is None else arm_margin
    close = None if move is None else snap + move
    data = {"status": R.OK, "projected_home_margin": dm, "projected_total": 44.0 + dev,
            "margin_error": dm - actual, "total_error": 0.0}
    hyb = {"status": R.OK, "projected_home_margin": snap + 0.3 * dev, "projected_total": 44.0 + 0.3 * dev,
           "margin_error": snap + 0.3 * dev - actual, "total_error": 0.0}
    return {"game_id": g, "season": 2026, "week": week, "minutes_to_kickoff": mtk, "prediction_id": f"{g}-{mtk}",
            "observed_at": f"t{1000 - mtk}", "actual": {"margin": actual, "total": 44.0},
            "market_at_snapshot": {"margin": snap, "total": 44.0},
            "close": {"status": "OK" if close is not None else "MISSING_CLOSE", "margin": close,
                      "total": None if move is None else 44.0 + move},
            "arms": {R.DATA_ONLY: data, R.HYBRID: hyb, R.CURRENT: {"status": R.OK, "projected_home_margin": snap,
                                                                   "projected_total": 44.0, "margin_error": snap - actual, "total_error": 0.0}}}


def test_unchanged_and_no_close_are_never_in_the_toward_denominator():
    rows = ([_gc_row("T1", 2.0, 0.5), _gc_row("T2", -1.5, -1.0), _gc_row("A1", 2.0, -0.5)]
            + [_gc_row(f"U{i}", 3.0, 0.0) for i in range(10)] + [_gc_row("N1", 2.0, None)] + [_gc_row("B1", 0.4, 0.5)])
    sig = AS.deviation_signal(rows)
    b = sig["views"]["latest_pregame"][R.DATA_ONLY]["margin"]
    assert (b["toward"], b["away"], b["unchanged"], b["no_close"], b["below_threshold"]) == (2, 1, 10, 1, 1)
    assert b["directional"] == 3 and b["toward_rate"] == pytest.approx(2 / 3)
    assert b["n_games"] == 15
    lo, hi = b["toward_rate_wilson95"]
    assert lo < 2 / 3 < hi
    # signed close move in the arm's direction: +0.5, +1.0, -0.5, and zeros for the unchanged games
    assert b["mean_signed_close_move_points"] == pytest.approx(1.0 / 13)


def test_hybrid_is_labelled_derived_and_its_split_mirrors_data_only():
    rows = [_gc_row("T1", 4.0, 0.5), _gc_row("A1", 4.0, -0.5), _gc_row("T2", -5.0, -1.0)]
    sig = AS.deviation_signal(rows)
    assert sig["arms"][R.HYBRID]["role"] == AS.HYBRID_DERIVED_LABEL
    assert "not independent" in AS.HYBRID_DERIVED_LABEL
    d, h = sig["views"]["latest_pregame"][R.DATA_ONLY]["margin"], sig["views"]["latest_pregame"][R.HYBRID]["margin"]
    assert (d["toward"], d["away"]) == (h["toward"], h["away"]), "0.3 x the same deviation points the same way"
    md = render_deviation_signal(sig)
    assert "LOCALIZED SIGNAL (GAME CENTRE)" in md and "HYBRID_30 (derived)" in md and "not independent" in md


def test_a_game_counts_once_per_horizon_however_many_snapshots_it_has():
    rows = []
    for g in ("G1", "G2", "G3"):
        for mtk in (500.0, 200.0, 95.0, 40.0, 10.0):                 # five snapshots per game
            rows.append(_gc_row(g, 2.0, 0.5, mtk=mtk))
    sig = AS.deviation_signal(rows)
    assert "raw" not in sig["views"], "raw snapshots are never a sample"
    for view in ("latest_pregame", "T-90m", "T-30m"):
        assert sig["views"][view][R.DATA_ONLY]["margin"]["n_games"] == 3
    assert sig["views"]["latest_pregame"][R.DATA_ONLY]["margin"]["toward"] == 3


def _gc_hypothesis(tmp_path):
    p = str(tmp_path / "h.jsonl")
    _add(p, hid="GC", hypothesis_kind=HR.KIND_GAME_CENTRE,
         locator={"kind": HR.KIND_GAME_CENTRE, "arm": R.DATA_ONLY, "target": "margin", "primary_horizon": "latest_pregame"},
         generation_evidence={"horizons": {"latest_pregame": {"toward_rate": 1.0}}})
    HR.preregister("GC", test_window=W(2026, 3, 18), thresholds=HR.PREREGISTERED_THRESHOLDS, evaluation_plan="p", path=p)
    return p


def test_game_centre_evaluation_uses_future_weeks_and_directional_counts_only(tmp_path):
    p = _gc_hypothesis(tmp_path)
    h = HR.current(p)["GC"]
    wk = lambda w, t, a, u: {"season": 2026, "week": w, "horizons": {"latest_pregame": {   # noqa: E731
        "n_games": t + a + u, "toward": t, "away": a, "unchanged": u, "no_close": 0, "below_threshold": 0}}}
    ev = HR.evaluate_prospective(h, {"by_week": [wk(2, 50, 0, 0), wk(3, 5, 1, 30)]})
    p_ = ev["metrics"]["horizons"]["latest_pregame"]
    assert (p_["toward"], p_["directional"], p_["unchanged"]) == (5, 6, 30), "week 2 leaked in or unchanged entered"
    assert ev["new_independent_games"] == 36 and ev["suggested_status"] == "INCONCLUSIVE"      # 6 < 20 directional
    big = HR.evaluate_prospective(h, {"by_week": [wk(w, 6, 1, 5) for w in range(3, 7)]})    # 24 toward / 28
    assert big["suggested_status"] == "SUPPORTED" and big["trend"] in ("PERSISTING", "WEAKENING")
    against = HR.evaluate_prospective(h, {"by_week": [wk(w, 2, 5, 5) for w in range(3, 7)]})
    assert against["suggested_status"] == "NOT_SUPPORTED" and against["trend"] == "REVERSING"


# ============================================================================ slices: games, arms, synchronization
def _research_row(i, *, game, arm="DATA_PLAYER_V3", fam="player_rec_yards", sync=True, edge=0.3, rng=None):
    rng = rng or random.Random(i)
    y = float(i % 2)
    market = min(max(0.5 + (0.25 if y else -0.25) + rng.uniform(-0.08, 0.08), 0.02), 0.98)
    model = min(max(market - (edge if y else -edge) + rng.uniform(-0.05, 0.05), 0.02), 0.98)
    return {"evidence_class": "PROSPECTIVE_FROZEN", "synchronization_state": "SYNCHRONIZED" if sync else "ASYNC_MODEL_NEWER_THAN_MARKET",
            "model_arm": arm, "family_group": fam, "horizon_label": "T-90m", "model_version": f"{arm}-1",
            "game_id": game, "ticker": f"T{i}", "contract_value": model, "h_mid": market, "c_mid": market,
            "settled_yes": y, "clv_status": "NO_VIEW"}


def test_many_contracts_on_few_games_count_as_games_not_rows():
    rng = random.Random(1)
    rows = [_research_row(i, game=f"G{i % 10}", rng=rng) for i in range(400)]        # 400 contracts, 10 games
    sc = S3.build(rows, min_segment_n=5)
    cands = HR.candidates_from_scorecard(sc, season=2026, week=2)
    assert cands == [], "400 contracts on 10 games cleared a 16-game floor"
    lowered = HR.candidates_from_scorecard(sc, season=2026, week=2, min_games=2)
    crossed = [c for c in lowered if c["segment"] == "model_arm*family_group"]
    assert crossed and crossed[0]["independent_games"] == 10 and crossed[0]["paired_settled_rows"] == 400
    assert crossed[0]["unique_contracts"] == 400 and crossed[0]["model_arm"] == "DATA_PLAYER_V3"
    assert crossed[0]["family_group"] == "player_rec_yards" and crossed[0]["model_versions"] == ["DATA_PLAYER_V3-1"]
    assert crossed[0]["executable_pnl"]["state"] == "UNAVAILABLE"
    assert crossed[0]["ci95"][0] < crossed[0]["effect_size"] < crossed[0]["ci95"][1]


def test_crossed_segments_keep_arms_apart_and_pooled_slices_are_refused(tmp_path):
    rng = random.Random(2)
    rows = ([_research_row(i, game=f"G{i % 20}", arm="ARM_A", rng=rng) for i in range(200)]
            + [_research_row(i + 1000, game=f"G{i % 20}", arm="ARM_B", edge=-0.2, rng=rng) for i in range(200)])
    sc = S3.build(rows, min_segment_n=5)
    blk = sc["by_synchronization"]["PROSPECTIVE_FROZEN"]["SYNCHRONIZED"]
    assert set(blk["segments"]["model_arm*family_group"]) == {"ARM_A|player_rec_yards", "ARM_B|player_rec_yards"}
    assert "model_arm*family_group*horizon_label" in blk["segments"]
    single_only = sum(len({str(r.get(k)) for r in rows}) for k in S3.SEGMENTS)
    assert blk["candidate_slices_considered"] > single_only, "the crossed slices must be counted as comparisons"
    out = tmp_path / "c.json"
    cands = HR.candidates_from_scorecard(sc, season=2026, week=2, path_out=str(out))
    assert cands and all(c["model_arms"] and len(c["model_arms"]) == 1 for c in cands)
    refused = json.load(open(str(out).replace(".json", ".refused.json")))
    assert any(r["reason"] == "POOLS_MODEL_ARMS" and r["slice"] == "family_group=player_rec_yards" for r in refused)


def test_synchronized_and_unsynchronized_slices_are_never_pooled():
    rng = random.Random(3)
    rows = ([_research_row(i, game=f"G{i % 20}", sync=False, edge=0.4, rng=rng) for i in range(300)]
            + [_research_row(i + 1000, game=f"H{i % 20}", sync=True, edge=0.0, rng=rng) for i in range(60)])
    sc = S3.build(rows, min_segment_n=5)
    e = LS.slice_week_entry(sc, "model_arm*family_group", "DATA_PLAYER_V3|player_rec_yards", 2026, 3)
    assert e["paired_n"] == 60 and e["games"] == 20, "asynchronous rows reached the future-evidence entry"
    only_async = S3.build([r for r in rows if r["synchronization_state"] != "SYNCHRONIZED"], min_segment_n=5)
    e2 = LS.slice_week_entry(only_async, "model_arm*family_group", "DATA_PLAYER_V3|player_rec_yards", 2026, 3)
    assert e2["games"] == 0 and e2["effect"] is None


# ============================================================================ the committed preregistration
def test_the_committed_game_centre_preregistration_is_intact():
    path = os.path.join(ROOT, HR.DEFAULT_PATH)
    rows = HR.load(path)
    cur = HR.current(path)
    for target in ("MARGIN", "TOTAL"):
        h = cur[f"H2-GC-{target}-2026W02"]
        assert h["status"] == "PREREGISTERED" and h["hypothesis_kind"] == HR.KIND_GAME_CENTRE
        assert h["generation_window"] == W(2026, 2, 2) and h["registered_future_test_window"] == W(2026, 3, 18)
        pre = h["preregistration"]
        assert HR._parse_ts(pre["preregistered_at"]) < HR._parse_ts(pre["first_test_kickoff_utc"])
        assert HR._parse_ts(pre["first_test_kickoff_utc"]) == HR._parse_ts("2026-09-25T00:15:00Z")
        assert pre["thresholds_sha"] == HR.thresholds_sha(pre["thresholds"]) == HR.thresholds_sha(HR.PREREGISTERED_THRESHOLDS), \
            "PREREGISTERED_THRESHOLDS changed after the preregistration was written"
        assert h["generation_evidence"]["evidence_type"] == "HYPOTHESIS_GENERATING"
    lp = cur["H2-GC-MARGIN-2026W02"]["generation_evidence"]["published_all_deviations_no_threshold"]["latest_pregame"]
    assert (lp["toward"], lp["away"], lp["unchanged"]) == (2, 1, 13)
    lt = cur["H2-GC-TOTAL-2026W02"]["generation_evidence"]["published_all_deviations_no_threshold"]["latest_pregame"]
    assert (lt["toward"], lt["away"], lt["unchanged"]) == (3, 1, 12)
    by_id = {}
    for r in rows:                                   # the hash chain is intact
        want = {k: v for k, v in r.items() if k != "line_hash"}
        assert HR._line_hash(want) == r["line_hash"]
        assert r["previous_hash"] == by_id.get(r["id"])
        by_id[r["id"]] = r["line_hash"]


def test_the_preregistration_script_is_idempotent(tmp_path):
    spec = importlib.util.spec_from_file_location("_prereg_gc", os.path.join(ROOT, "scripts", "research", "preregister_game_centre_v2.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    p = str(tmp_path / "h.jsonl")
    assert mod.main(["--registry", p, "--now", "2026-09-24T05:00:00Z"]) == 0
    before = _sha(p)
    assert mod.main(["--registry", p, "--now", "2026-09-24T06:00:00Z"]) == 0
    assert _sha(p) == before and len(HR.load(p)) == 4
    with pytest.raises(HR.RegistryError):
        mod.main(["--registry", str(tmp_path / "late.jsonl"), "--now", "2026-09-25T01:00:00Z"])


# ============================================================================ rendering with missing inputs
def test_the_section_renders_with_empty_and_partial_inputs(tmp_path):
    empty = "\n".join(LS.render(None))
    assert "LOCALIZED SIGNAL RESEARCH" in empty and "owner approval required" in empty
    doc = LS.build({}, season=2026, week=3, label="2026_wk03")
    assert "no hypotheses registered yet" in "\n".join(LS.render(doc))
    p = _gc_hypothesis(tmp_path)
    HR.register_candidates([_cand("S")], path=p)
    hyps, _ = LS.load_hypotheses([p, str(tmp_path / "missing.jsonl")])
    doc = LS.build(hyps, season=2026, week=3, label="2026_wk03", slice_scorecards={(2026, 3): {}}, gc_signals={})
    text = "\n".join(LS.render(doc))
    assert "GC" in text and "| S |" in text and "suggestion only; owner approval required" in text
    json.dumps(doc, default=str)                                            # the machine-readable copy serialises
    assert render_deviation_signal(None).startswith("## LOCALIZED SIGNAL (GAME CENTRE)")


def test_game_centre_evidence_is_read_from_the_newest_arm_report_batch_that_carries_it(tmp_path):
    root = tmp_path / "arm_reports"
    old, new, legacy = root / "20260920T000000Z", root / "20260930T000000Z", root / "20261001T000000Z"
    for d in (old, new, legacy):
        d.mkdir(parents=True)
    rows = [_gc_row("T1", 2.0, 0.5, week=3), _gc_row("A1", 2.0, -0.5, week=3)]
    sig = AS.deviation_signal(rows)
    json.dump({"season": 2026, "week": 3, "deviation_signal": sig}, open(new / "week03.scorecard.json", "w"))
    json.dump({"season": 2026, "week": 2, "deviation_signal": sig}, open(old / "week02.scorecard.json", "w"))
    json.dump({"week": 3}, open(legacy / "week03.scorecard.json", "w"))          # written before the signal existed
    got, src = LS.load_gc_signals(str(root), 2026)
    assert src == str(new) and set(got) == {(2026, 3)}
    e = LS.gc_week_entry(got[(2026, 3)], R.DATA_ONLY, "margin", 2026, 3)
    assert e["horizons"]["latest_pregame"]["toward"] == 1 and e["horizons"]["latest_pregame"]["away"] == 1
    assert LS.load_gc_signals(str(tmp_path / "absent"), 2026) == ({}, None)


def test_the_weekly_report_assembles_slice_and_game_centre_evidence_from_published_files(tmp_path):
    import types
    spec = importlib.util.spec_from_file_location("_wr_ws3b", os.path.join(ROOT, "scripts", "shadow_v2", "weekly_report_v2.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    md_root = tmp_path / "md"
    md = md_root / "data" / "shadow" / "v2"
    (md / "research").mkdir(parents=True)
    rng = random.Random(9)
    wk = lambda w, pre: [_research_row(i, game=f"{pre}{i % 20}", rng=rng) for i in range(120)]   # noqa: E731
    json.dump(S3.build(wk(2, "A"), min_segment_n=5), open(md / "research" / "2026_wk02.scorecard_v3.json", "w"), default=str)
    auto = tmp_path / "auto.jsonl"
    HR.register_candidates(HR.candidates_from_scorecard(S3.build(wk(1, "Z"), min_segment_n=5), season=2026, week=1), path=str(auto))
    assert HR.current(str(auto)), "fixture must register at least one week-1 slice"
    args = types.SimpleNamespace(hypotheses=str(auto), registry=os.path.join(ROOT, HR.DEFAULT_PATH), research=str(tmp_path / "none"),
                                 season=2026, week=3, arm_reports="", market_data=str(md_root))
    doc = mod.localized_signals(S3.build(wk(3, "C"), min_segment_n=5), args, str(md), "2026_wk03")
    by_id = {e["id"]: e for e in doc["evaluations"]}
    slice_ev = next(e for e in by_id.values() if e["kind"] == HR.KIND_SLICE and e["id"].endswith("DATA_PLAYER_V3|player_rec_yards"))
    assert [w for _, w in slice_ev["evaluated_weeks"]] == [2, 3] and slice_ev["new_independent_games"] == 40
    assert slice_ev["excluded_weeks"] == [] or all(x["week"] == 1 for x in slice_ev["excluded_weeks"])
    assert by_id["H2-GC-MARGIN-2026W02"]["new_independent_games"] == 0     # no arm report on this market-data
    assert doc["n_under_test"] == 2 and doc["multiple_comparisons"]["m"] == 2
    text = mod.render(S3.build(wk(3, "C")), mod.health(wk(3, "C"), [], [], 2026, 3), wk(3, "C"), "2026_wk03", doc)
    assert "H2-GC-TOTAL-2026W02" in text and "suggestion only; owner approval required" in text


def test_the_weekly_report_places_the_section_before_the_autopsy_and_drops_the_stale_header():
    spec = importlib.util.spec_from_file_location("_wr_ws3", os.path.join(ROOT, "scripts", "shadow_v2", "weekly_report_v2.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    rows = [_research_row(i, game=f"G{i % 4}") for i in range(12)]
    h = mod.health(rows, [], [], 2026, 3)
    text = mod.render(S3.build(rows), h, rows, "2026_wk03")
    assert "Week-1 patterns cannot be confirmed on Week 1" not in text
    assert "can never be confirmed on 2026_wk03" in text
    assert text.index("## LOCALIZED SIGNAL RESEARCH") < text.index("## Player autopsy")
