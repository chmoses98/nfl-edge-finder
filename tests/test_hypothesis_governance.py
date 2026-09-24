"""THREE-STAGE HYPOTHESIS GOVERNANCE: discovery pool, preregistered tests, confirmatory results.

The failure this file guards against: a pool of hundreds of mined slices being read -- by a person or by the
code -- as hundreds of tests. Either it silently inflates the multiplicity family (so the real tests lose all
power) or, worse, a mined slice gets a SUPPORTED suggestion without anyone having chosen and frozen it first.
Each test below pins one of those doors shut, and pins the shortlist / owner-preregistration path that is the
only way from Stage A to Stage B.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import random
import re
import sys

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT)

from nfl_edge.research import hypothesis_registry_v2 as HR                 # noqa: E402
from nfl_edge.research import localized_signals as LS                      # noqa: E402
from nfl_edge.research import preregistration_shortlist as PS              # noqa: E402

W = lambda s, lo, hi: {"season": s, "week_lo": lo, "week_hi": hi}         # noqa: E731
KICK_W3 = "2026-09-25T00:15:00Z"
BEFORE = "2026-09-24T05:00:00Z"


def _sha(path):
    return hashlib.sha256(open(path, "rb").read()).hexdigest()


def _cand(hid, *, eff=-0.02, se=0.002, games=20, clv=0.01, arm="ARM_A", fam="fam_x", horizon="T-90m", seg=None,
          value=None, k=422, sync="SYNCHRONIZED", arms=None, week=2, paired=400):
    seg = seg or "model_arm*family_group*horizon_label"
    value = value or f"{arm}|{fam}|{horizon}"
    return {"id": hid, "market_family": seg, "segment": seg, "segment_value": value, "condition": f"{seg} == {value}",
            "hypothesis_kind": HR.KIND_SLICE, "direction": "model beats market" if eff < 0 else "market beats model",
            "effect_size": eff, "uncertainty": se, "ci95": [eff - 1.96 * se, eff + 1.96 * se], "z": eff / se,
            "sample_size": paired, "game_count": games, "independent_games": games, "paired_settled_rows": paired,
            "unique_contracts": 50, "mean_clv_mid": clv, "se_clv_mid_clustered": 0.004, "positive_clv_rate": 0.55,
            "market_toward_model_rate": 0.6, "n_clv_ok": paired if clv is not None else 0,
            "executable_pnl": {"state": "UNAVAILABLE", "reason": "no fee-known rows"},
            "model_arm": arm, "model_arms": arms if arms is not None else [arm], "model_versions": [f"{arm}-1"],
            "family_group": fam, "horizon_label": horizon, "candidate_slices_considered": k,
            "synchronization_basis": sync, "evidence_class": "PROSPECTIVE_FROZEN", "minimum_sample": 30, "minimum_games": 16,
            "generation_window": W(2026, week, week), "future_test_window": W(2026, week + 1, 18)}


def _slice_week(week, games=40, paired=400, eff=-0.05, se=0.001, clv=0.02):
    return {"season": 2026, "week": week, "games": games, "paired_n": paired, "effect": eff, "se": se,
            "mean_clv_mid": clv, "n_clv_ok": paired, "positive_clv_rate": 0.7, "market_toward_model_rate": 0.7,
            "pnl_net_per_contract": 0.01, "n_fee_known": paired}


def _prereg(p, hid, win=W(2026, 3, 18)):
    return HR.preregister(hid, test_window=win, thresholds=HR.PREREGISTERED_THRESHOLDS, evaluation_plan="p",
                          preregistered_at=BEFORE, first_test_kickoff_utc=KICK_W3, path=p)


def _load_script(name, rel):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, *rel))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    return mod


# ============================================================================ stage derivation
def test_stage_follows_status_and_the_record_behind_it(tmp_path):
    p = str(tmp_path / "h.jsonl")
    HR.register_candidates([_cand("A")], path=p)
    assert HR.stage(HR.current(p)["A"]) == HR.STAGE_DISCOVERY
    _prereg(p, "A")
    assert HR.stage(HR.current(p)["A"]) == HR.STAGE_PREREGISTERED
    HR.transition("A", "TESTING", path=p)
    assert HR.governance(HR.current(p)["A"]) == {"stage": HR.STAGE_PREREGISTERED, "defects": [], "in_family": True}
    HR.transition("A", "SUPPORTED", test_window=W(2026, 3, 8), result={"new_games": 80, "effect": -0.03}, path=p)
    assert HR.stage(HR.current(p)["A"]) == HR.STAGE_CONFIRMATORY
    HR.transition("A", "RETIRED", path=p)
    assert HR.governance(HR.current(p)["A"]) == {"stage": HR.STAGE_RETIRED, "defects": [], "in_family": False}


def test_stage_b_and_c_cannot_be_declared_without_their_record(tmp_path):
    p = str(tmp_path / "h.jsonl")
    HR.register_candidates([_cand("A")], path=p)
    with pytest.raises(HR.RegistryError, match="only through preregister"):
        HR.transition("A", "PREREGISTERED", path=p)
    with pytest.raises(HR.RegistryError, match="only through preregister"):
        HR.transition("A", "PREREGISTERED", extra={"preregistration": {"test_window": W(2026, 3, 18)}}, path=p)
    assert HR.current(p)["A"]["status"] == "GENERATED", "a refused transition wrote a line"
    _prereg(p, "A")
    HR.transition("A", "TESTING", path=p)
    with pytest.raises(HR.RegistryError, match="future evidence"):
        HR.transition("A", "SUPPORTED", path=p)                                   # a verdict needs its evidence
    assert HR.current(p)["A"]["status"] == "TESTING"


def test_a_legacy_bare_preregistered_line_is_a_discovery_candidate_with_its_defects_listed(tmp_path):
    """A line written before the rule (a bare transition) claims Stage B and has no frozen bar: it is not a test."""
    p = str(tmp_path / "h.jsonl")
    HR.register_candidates([_cand("L")], path=p)
    cur = HR.current(p)["L"]
    legacy = {**cur, "status": "PREREGISTERED", "evidence_type": "PREREGISTERED_TEST", "test_window": W(2026, 3, 18),
              "previous_hash": cur["line_hash"]}
    legacy.pop("line_hash")
    HR._append(p, legacy)
    h = HR.current(p)["L"]
    g = HR.governance(h)
    assert g["stage"] == HR.STAGE_DISCOVERY and not g["in_family"] and "NO_PREREGISTRATION_RECORD" in g["defects"]
    ev = HR.evaluate_prospective(h, {"by_week": [_slice_week(w) for w in range(3, 10)]}, n_under_test=1)
    assert ev["suggested_status"] is None and ev["suggestion_reason"].startswith("not preregistered")
    audit = HR.audit_registry(HR.load(p))
    assert audit["improper"] == [{"id": "L", "status": "PREREGISTERED", "defects": g["defects"]}]
    assert audit["multiplicity_family"] == [] and audit["hash_chain_ok"]


def test_a_preregistration_record_with_a_tampered_bar_or_late_time_is_not_stage_b(tmp_path):
    p = str(tmp_path / "h.jsonl")
    HR.register_candidates([_cand("A")], path=p)
    row = _prereg(p, "A")
    bad = json.loads(json.dumps(row))
    bad["preregistration"]["thresholds"]["KIND_SLICE_EXTRA"] = 1                  # bar edited after the hash
    assert "THRESHOLDS_HASH_MISMATCH" in HR.governance(bad)["defects"]
    late = json.loads(json.dumps(row))
    late["preregistration"]["preregistered_at"] = "2026-09-26T00:00:00+00:00"
    assert "PREREGISTERED_AT_OR_AFTER_FIRST_TEST_KICKOFF" in HR.governance(late)["defects"]
    back = json.loads(json.dumps(row))
    back["preregistration"]["test_window"] = W(2026, 2, 5)
    assert "TEST_WINDOW_NOT_STRICTLY_AFTER_GENERATION" in HR.governance(back)["defects"]
    assert all(HR.stage(x) == HR.STAGE_DISCOVERY for x in (bad, late, back))


# ============================================================================ the multiplicity family
def test_263_discovery_candidates_cannot_inflate_m_nor_produce_a_supported_suggestion(tmp_path):
    """The published Week-2 registry holds 263 GENERATED LOCALIZED_SLICE lines. However strong their generation
    numbers -- and however strong their later evidence -- they are not tests."""
    p = str(tmp_path / "auto.jsonl")
    rng = random.Random(263)
    cands = [_cand(f"HG-{i:03d}", eff=-rng.uniform(0.02, 0.2), se=0.001, games=40, arm=f"ARM_{i % 4}", fam=f"fam_{i}")
             for i in range(263)]
    assert HR.register_candidates(cands, path=p)["added"] == [c["id"] for c in cands]
    committed = str(tmp_path / "committed.jsonl")
    HR.register_candidates([_cand("H-TEST")], path=committed)
    _prereg(committed, "H-TEST")
    hyps, _ = LS.load_hypotheses([committed, p])
    assert len(hyps) == 264
    assert HR.multiplicity_family(hyps) == ["H-TEST"]
    assert {HR.stage(h) for hid, h in hyps.items() if hid != "H-TEST"} == {HR.STAGE_DISCOVERY}

    overwhelming = {"by_week": [_slice_week(w, games=60, eff=-0.3, se=0.0005) for w in range(3, 12)]}
    evs = [HR.evaluate_prospective(hyps[hid], overwhelming, n_under_test=len(HR.multiplicity_family(hyps)))
           for hid in sorted(hyps)]
    disc = [e for e in evs if e["id"] != "H-TEST"]
    assert len(disc) == 263
    assert all(e["suggested_status"] is None for e in disc), "a discovery candidate received a suggested status"
    assert all(e["suggestion_reason"].startswith("not preregistered") for e in disc)
    assert all(not e["in_multiplicity_family"] for e in disc)
    test_ev = next(e for e in evs if e["id"] == "H-TEST")
    assert test_ev["multiple_comparisons"]["m"] == 1 and test_ev["suggested_status"] == "SUPPORTED"

    doc = LS.build(hyps, season=2026, week=2, label="2026_wk02")
    assert doc["multiple_comparisons"]["m"] == 1 and doc["n_under_test"] == 1 and doc["multiplicity_family"] == ["H-TEST"]
    g = doc["governance"]
    assert g["n_discovery"] == 263 and g["n_preregistered"] == 1 and g["multiplicity"]["m"] == 1
    assert g["multiplicity"]["alpha_per_test"] == 0.05
    assert not any(e.get("suggested_status") == "SUPPORTED" for e in doc["evaluations"] if e["id"] != "H-TEST")


def test_the_arm_report_family_counts_stage_b_and_c_only(tmp_path):
    mod = _load_script("_arm_report_gov", ("scripts", "shadow", "arm_report.py"))
    p = str(tmp_path / "h.jsonl")
    HR.register_candidates([_cand(f"G{i}") for i in range(30)], path=p)
    HR.add(hid="GC", market_family="GAME_CENTRE_MARGIN", condition="c", direction="d", expected_mechanism="m",
           evaluation_metric="e", minimum_sample=20, generation_window=W(2026, 2, 2), future_test_window=W(2026, 3, 18),
           generated_by="t", hypothesis_kind=HR.KIND_GAME_CENTRE,
           locator={"kind": HR.KIND_GAME_CENTRE, "arm": "DATA_ONLY", "target": "margin", "primary_horizon": "latest_pregame"},
           path=p)
    _prereg(p, "GC")
    out = mod.game_centre_evaluations(p, {})
    assert [e["id"] for e in out] == ["GC"] and out[0]["multiple_comparisons"]["m"] == 1


# ============================================================================ audit of a published registry
def test_audit_counts_stages_and_catches_a_tampered_line(tmp_path):
    p = str(tmp_path / "h.jsonl")
    HR.register_candidates([_cand(f"G{i}") for i in range(5)], path=p)
    a = HR.audit_registry(HR.load(p))
    assert a["ids_by_status"] == {"GENERATED": 5} and a["ids_by_stage"] == {HR.STAGE_DISCOVERY: 5}
    assert a["improper"] == [] and a["hash_chain_ok"] and a["ids_with_transitions"] == []
    rows = HR.load(p)
    rows[2]["status"] = "TESTING"                                               # edited in place: never allowed
    t = HR.audit_registry(rows)
    assert not t["hash_chain_ok"] and t["chain_breaks"][0]["reason"] == "LINE_HASH_MISMATCH"
    assert t["improper"] and t["improper"][0]["id"] == "G2"


def test_registries_merge_by_governance_not_by_path_order(tmp_path):
    """An owner-preregistered mined slice lives PREREGISTERED in the committed registry and GENERATED in the
    automatic one; the GENERATED copy must never shadow the preregistration."""
    auto, committed = str(tmp_path / "auto.jsonl"), str(tmp_path / "committed.jsonl")
    HR.register_candidates([_cand("S")], path=auto)
    with open(committed, "w") as f:
        f.write(open(auto).read())
    _prereg(committed, "S")
    for order in ([committed, auto], [auto, committed]):
        hyps, notes = LS.load_hypotheses(order)
        assert hyps["S"]["status"] == "PREREGISTERED" and notes, order


# ============================================================================ shortlist rules
def _shortlist(cands, *, week=2, tmp_path=None):
    p = str(tmp_path / "sl.jsonl")
    HR.register_candidates(cands, path=p)
    return PS.build(HR.current(p), season=2026, week=week, label="2026_wk02"), p


def test_shortlist_applies_every_rule_and_says_why(tmp_path):
    k = 422
    bar = PS.search_adjusted_z(k)
    assert 3.8 < bar < 3.9
    cands = [
        _cand("OK", eff=-0.02, se=0.002, fam="f_ok"),                               # |z| 10, CLV agrees
        _cand("FEW_GAMES", eff=-0.02, se=0.002, games=15, fam="f_few"),
        _cand("BELOW_BAR", eff=-0.007, se=0.002, fam="f_bar"),                      # |z| 3.5 < 3.85
        _cand("CLV_WRONG", eff=-0.02, se=0.002, clv=-0.01, fam="f_clv"),
        _cand("NO_CLV", eff=-0.02, se=0.002, clv=None, fam="f_noclv"),
        _cand("POOLED", eff=-0.02, se=0.002, arms=["ARM_A", "ARM_B"], fam="f_pool"),
        _cand("ASYNC", eff=-0.02, se=0.002, sync="ASYNC_MODEL_NEWER_THAN_MARKET", fam="f_async"),
        _cand("MARKET_SIDE", eff=0.02, se=0.002, clv=-0.01, fam="f_mkt"),           # market-better, CLV agrees
    ]
    doc, _ = _shortlist(cands, tmp_path=tmp_path)
    assert [e["id"] for e in doc["shortlist"]] == ["MARKET_SIDE", "OK"]        # equal |z|: ties break by id
    reasons = doc["not_qualifying_by_reason"]
    assert reasons == {"BELOW_SEARCH_ADJUSTED_BAR": 1, "CLV_DISAGREES_WITH_BRIER_EFFECT": 1, "CLV_MISSING": 1,
                       "FEWER_THAN_MIN_INDEPENDENT_GAMES": 1, "NOT_SYNCHRONIZED_PROSPECTIVE_FROZEN": 1,
                       "POOLS_OR_LACKS_MODEL_ARM": 1}
    e = next(x for x in doc["shortlist"] if x["id"] == "OK")
    for key in ("market_family", "condition", "model_arm", "model_versions", "generation_week", "independent_games",
                "effect_size", "clustered_se", "ci95", "mean_clv_mid", "positive_clv_rate", "toward_close_rate",
                "executable_economics", "multiplicity", "proposed_confirmatory_window", "reason_qualifies"):
        assert key in e, key
    assert e["executable_economics"]["state"] == "UNAVAILABLE"
    assert e["multiplicity"]["slices_searched"] == k and e["multiplicity"]["z_required"] == pytest.approx(bar)
    assert e["proposed_confirmatory_window"] == W(2026, 3, 18) and e["stage"] == HR.STAGE_DISCOVERY
    assert "not preregistered" in e["label"]


def test_the_search_denominator_moves_the_bar(tmp_path):
    """The same |z| = 3.5 qualifies after searching 10 slices and not after searching 422."""
    doc10, _ = _shortlist([_cand("S", eff=-0.007, se=0.002, k=10)], tmp_path=tmp_path)
    assert doc10["n_shortlisted"] == 1
    (tmp_path / "sl.jsonl").unlink()
    doc422, _ = _shortlist([_cand("S", eff=-0.007, se=0.002, k=422)], tmp_path=tmp_path)
    assert doc422["n_shortlisted"] == 0


def test_shortlist_offers_one_per_arm_and_family_and_one_per_identical_row_set(tmp_path):
    cands = [_cand("X-CYCLE", eff=-0.03, se=0.002, fam="fam", horizon="CYCLE"),
             _cand("X-T90", eff=-0.02, se=0.002, fam="fam", horizon="T-90m"),
             _cand("X-ALL", eff=-0.025, se=0.002, seg="model_arm*family_group", value="ARM_A|fam", fam="fam"),
             _cand("OTHER_ARM", eff=-0.02, se=0.002, arm="ARM_B", fam="fam"),
             _cand("MF", eff=-0.01, se=0.002, seg="market_family", value="TEAM_TOTAL", fam=None, arm="ARM_C"),
             _cand("SF", eff=-0.01, se=0.002, seg="stat_family", value="team_points", fam=None, arm="ARM_C")]
    doc, _ = _shortlist(cands, tmp_path=tmp_path)
    ids = [e["id"] for e in doc["shortlist"]]
    assert ids == ["X-CYCLE", "OTHER_ARM", "MF"]
    d = {x["id"]: x for x in doc["near_duplicates_not_offered"]}
    assert d["X-T90"]["reason"] == d["X-ALL"]["reason"] == "SAME_ARM_AND_FAMILY" and d["X-ALL"]["kept"] == "X-CYCLE"
    assert d["SF"]["reason"] == "IDENTICAL_ROW_SET" and d["SF"]["kept"] == "MF"
    assert [e["rank"] for e in doc["shortlist"]] == [1, 2, 3]


def test_shortlist_is_deterministic_writes_nothing_and_skips_non_discovery(tmp_path):
    cands = [_cand(f"C{i}", eff=-0.01 - 0.001 * i, se=0.002, fam=f"f{i}") for i in range(12)]
    doc, p = _shortlist(cands, tmp_path=tmp_path)
    before = _sha(p)
    shuffled = dict(sorted(HR.current(p).items(), key=lambda kv: random.Random(5).random()))
    again = PS.build(shuffled, season=2026, week=2, label="2026_wk02")
    assert json.dumps(again, sort_keys=True, default=str) == json.dumps(doc, sort_keys=True, default=str)
    assert _sha(p) == before, "building the shortlist wrote to the registry"
    _prereg(p, "C11")
    after = PS.build(HR.current(p), season=2026, week=2, label="2026_wk02")
    assert "C11" not in [e["id"] for e in after["shortlist"]], "a Stage-B hypothesis was offered for preregistration"


def test_the_proposed_window_starts_after_the_report_week_and_ends_inside_the_registered_one(tmp_path):
    doc, p = _shortlist([_cand("S", eff=-0.02, se=0.002)], week=5, tmp_path=tmp_path)
    assert doc["shortlist"][0]["proposed_confirmatory_window"] == W(2026, 6, 18)
    late = PS.build(HR.current(p), season=2026, week=18, label="2026_wk18")
    assert late["n_shortlisted"] == 0 and late["not_qualifying_by_reason"] == {"NO_REMAINING_CONFIRMATORY_WINDOW": 1}


# ============================================================================ report language
BANNED = re.compile(r"\b(edge|edges|profitable|profit|best bets?|lock|guaranteed|beats the market)\b", re.I)


def test_the_section_splits_discovery_from_tests_and_states_the_governance_header(tmp_path):
    p = str(tmp_path / "auto.jsonl")
    HR.register_candidates([_cand(f"HG-{i:03d}", eff=-0.005 - 0.0002 * i, se=0.002, fam=f"f{i}") for i in range(40)], path=p)
    committed = str(tmp_path / "c.jsonl")
    HR.register_candidates([_cand("H-TEST", fam="t")], path=committed)
    _prereg(committed, "H-TEST")
    hyps, _ = LS.load_hypotheses([committed, p])
    doc = LS.build(hyps, season=2026, week=2, label="2026_wk02")
    text = "\n".join(LS.render(doc))
    heads = ["### GOVERNANCE: three stages", "### PREREGISTERED CONFIRMATORY TESTS",
             "### DISCOVERY POOL (hypothesis-generating; not tests)",
             "### SHORTLIST FOR OWNER REVIEW (not tests; owner must preregister)"]
    assert [text.index(h) for h in heads] == sorted(text.index(h) for h in heads)
    for line in ("| candidate slices examined (search denominator) | 422 (2026 W2: 422) |",
                 "| generated (Stage A discovery candidates; not tests) | 40 |",
                 f"| shortlisted for owner review (still Stage A; not preregistered) | {doc['governance']['n_shortlisted']} |",
                 "| preregistered (Stage B) | 1 |", "| actively tested (Stage B with a future week evaluated, or TESTING) | 0 |",
                 "| multiplicity | BONFERRONI over m = 1 (Stage B/C members only) -> per-test alpha 0.0500"):
        assert line in text, line
    tests_part = text[text.index(heads[1]):text.index(heads[2])]
    disc_part = text[text.index(heads[2]):text.index(heads[3])]
    assert "H-TEST" in tests_part and "HG-0" not in tests_part, "a discovery candidate was listed among the tests"
    assert "suggested" not in disc_part.lower() and "SUPPORTED" not in disc_part and "PERSISTING" not in disc_part
    assert sum(1 for l in disc_part.splitlines() if l.startswith("| HG-")) == LS.MAX_DISCOVERY_ROWS
    assert "30 further discovery candidates are in `2026_wk02.localized_signals.json`" in disc_part
    assert len([e for e in doc["evaluations"] if e["stage"] == HR.STAGE_DISCOVERY]) == 40      # full list in JSON
    assert not BANNED.search(text), BANNED.search(text)
    json.dumps(doc, default=str)


def test_shortlist_markdown_and_json_never_use_promotional_language(tmp_path):
    cands = [_cand(f"C{i}", eff=-0.02 - 0.001 * i, se=0.002, fam=f"f{i}") for i in range(15)]
    doc, _ = _shortlist(cands, tmp_path=tmp_path)
    md = "\n".join(PS.render(doc))
    assert md.startswith("### SHORTLIST FOR OWNER REVIEW (not tests; owner must preregister)")
    assert sum(1 for l in md.splitlines() if re.match(r"\| \d+ \| C", l)) == PS.MAX_MARKDOWN_ROWS
    assert "5 further shortlisted candidates are in `2026_wk02.preregistration_shortlist.json`" in md
    blob = json.dumps(doc, default=str)
    assert not BANNED.search(md) and not BANNED.search(blob)
    src = open(os.path.join(ROOT, "nfl_edge", "research", "preregistration_shortlist.py")).read()
    assert not BANNED.search(src.split('"""', 2)[2]), "the shortlist module's code uses promotional language"


def test_the_weekly_report_writes_the_shortlist_json(tmp_path):
    mod = _load_script("_wr_gov", ("scripts", "shadow_v2", "weekly_report_v2.py"))
    auto = tmp_path / "auto.jsonl"
    HR.register_candidates([_cand("S1", fam="a"), _cand("S2", fam="b", eff=-0.001)], path=str(auto))
    reg = tmp_path / "reg.jsonl"
    reg.write_text("")
    out = tmp_path / "out"
    rc = mod.main(["--market-data", str(tmp_path / "md"), "--research", str(tmp_path / "none"), "--season", "2026",
                   "--week", "2", "--hypotheses", str(auto), "--registry", str(reg), "--out", str(out),
                   "--arm-reports", str(tmp_path / "none")])
    assert rc == 0
    sl = json.load(open(out / "2026_wk02.preregistration_shortlist.json"))
    assert [e["id"] for e in sl["shortlist"]] == ["S1"] and sl["not_qualifying_by_reason"] == {"BELOW_SEARCH_ADJUSTED_BAR": 1}
    md = open(out / "2026_wk02.WEEKLY_REPORT.md").read()
    assert "### DISCOVERY POOL (hypothesis-generating; not tests)" in md and "### SHORTLIST FOR OWNER REVIEW" in md
    assert HR.current(str(auto))["S1"]["status"] == "GENERATED", "the report changed a status"


# ============================================================================ the owner CLI
def _cli_setup(tmp_path):
    auto = str(tmp_path / "auto.jsonl")
    HR.register_candidates([_cand("S", fam="a"), _cand("NOT_LISTED", fam="b", eff=-0.001)], path=auto)
    sl = PS.build(HR.current(auto), season=2026, week=2, label="2026_wk02")
    slp = str(tmp_path / "sl.json")
    json.dump(sl, open(slp, "w"))
    reg = str(tmp_path / "committed.jsonl")
    return auto, slp, reg


def _args(auto, slp, reg, hid="S", *more):
    return ["--id", hid, "--source-registry", auto, "--shortlist", slp, "--registry", reg, "--test-week-lo", "3",
            "--first-test-kickoff", KICK_W3, "--now", BEFORE, *more]


def test_the_owner_cli_is_a_dry_run_unless_confirmed_and_then_appends_only(tmp_path):
    mod = _load_script("_prereg_cand", ("scripts", "research", "preregister_candidate_v2.py"))
    auto, slp, reg = _cli_setup(tmp_path)
    auto_before = _sha(auto)
    assert mod.main(_args(auto, slp, reg)) == 0
    assert not os.path.exists(reg), "a dry run wrote the registry"
    assert mod.main(_args(auto, slp, reg, "S", "--confirm")) == 0
    rows = HR.load(reg)
    assert [r["status"] for r in rows] == ["GENERATED", "PREREGISTERED"]
    assert rows[0] == HR.load(auto)[0], "the GENERATED line was not copied verbatim"
    assert HR.stage(rows[1]) == HR.STAGE_PREREGISTERED
    assert rows[1]["preregistration"]["thresholds_sha"] == HR.thresholds_sha(HR.PREREGISTERED_THRESHOLDS)
    assert HR.audit_registry(rows)["hash_chain_ok"]
    assert _sha(auto) == auto_before, "the source registry was modified"
    before = _sha(reg)
    assert mod.main(_args(auto, slp, reg, "S", "--confirm")) == 0             # idempotent
    assert _sha(reg) == before
    hyps, _ = LS.load_hypotheses([reg, auto])
    assert HR.multiplicity_family(hyps) == ["S"]


def test_the_owner_cli_refuses_after_kickoff_off_shortlist_and_outside_the_window(tmp_path):
    mod = _load_script("_prereg_cand2", ("scripts", "research", "preregister_candidate_v2.py"))
    auto, slp, reg = _cli_setup(tmp_path)
    late = _args(auto, slp, reg, "S", "--confirm")
    late[late.index("--now") + 1] = "2026-09-25T00:15:00Z"                        # at the first test kickoff
    with pytest.raises(SystemExit, match="observed"):
        mod.main(late)
    with pytest.raises(SystemExit, match="not on the shortlist"):
        mod.main(_args(auto, slp, reg, "NOT_LISTED", "--confirm"))
    early = _args(auto, slp, reg, "S", "--confirm")
    early[early.index("--test-week-lo") + 1] = "2"                                # the generation week
    with pytest.raises((SystemExit, HR.RegistryError)):
        mod.main(early)
    no_kick = [a for a in _args(auto, slp, reg, "S", "--confirm") if a not in ("--first-test-kickoff", KICK_W3)]
    with pytest.raises(SystemExit, match="first-test-kickoff"):
        mod.main(no_kick)
    assert not os.path.exists(reg), "a refused preregistration wrote a line"
