"""Football Signal Discovery Lab, Wave 2 (NFL): registration, frozen artifacts, ladders, checkpoints, side-specific
asks, fees, write-once records, due rule, verdicts and isolation. Synthetic and offline (CI has no nflverse data).
"""

from __future__ import annotations

import importlib.util
import json
import os
import sys
from datetime import UTC, datetime, timedelta
from pathlib import Path

import pandas as pd
import pytest

from nfl_edge.signal_discovery import wave2 as W
from nfl_edge.signal_discovery import wave2_due as WD
from nfl_edge.signal_discovery import wave2_models as M

ROOT = Path(__file__).resolve().parents[1]
KO = datetime(2026, 10, 18, 17, 0, tzinfo=UTC)
GID = "2026_06_AAA_BBB"


def _runner():
    spec = importlib.util.spec_from_file_location("signal_lab_wave2", ROOT / "scripts" / "research" / "signal_lab_wave2.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["signal_lab_wave2"] = mod
    spec.loader.exec_module(mod)
    return mod


# --------------------------------------------------------------------------- registration and frozen artifacts


def test_candidates_artifacts_and_classifier_are_pinned():
    frozen = W.load_frozen(ROOT)
    doc = (ROOT / "docs" / "research" / "FOOTBALL_SIGNAL_DISCOVERY_WAVE2_PROTOCOL.md").read_text()
    assert "Status: **PRE-REGISTERED**" in doc and W.CANDIDATES_SHA256 in doc
    assert frozen["wf_total"]["train_seasons"] == list(range(2015, 2026))
    assert frozen["props"]["train_seasons"] == [2016, 2025]
    assert set(W.ROLE_FAMILIES) <= set(frozen["props"]["families"])
    manifest = json.loads((ROOT / W.MODELS_DIR / "manifest.json").read_text())
    assert manifest["wf_total_2026_sha256"] == W.WF_TOTAL_SHA256 and manifest["prop_models_2026_sha256"] == W.PROP_MODELS_SHA256
    assert all(f["max_abs_coef_diff"] == 0.0 for f in manifest["reproduction_proof"]["wf_total_folds"])
    assert all(f["max_abs_pred_diff_vs_wave1"] == 0.0 for f in manifest["reproduction_proof"]["prop_families"])


@pytest.mark.parametrize("target", ["candidates", "wf_total", "props"])
def test_any_frozen_edit_is_refused(tmp_path, target):
    for rel in (W.CANDIDATES_PATH, W.MODELS_DIR / "wf_total_2026.json", W.MODELS_DIR / "prop_models_2026.json"):
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / rel).write_text((ROOT / rel).read_text())
    path = {"candidates": W.CANDIDATES_PATH, "wf_total": W.MODELS_DIR / "wf_total_2026.json",
            "props": W.MODELS_DIR / "prop_models_2026.json"}[target]
    doc = json.loads((tmp_path / path).read_text())
    if target == "candidates":
        doc["population"]["week_on_or_after"] = 5
    elif target == "wf_total":
        doc["pick_threshold_points"] = 1.5
    else:
        doc["families"]["RB_receptions"]["median_offset"] += 0.01
    (tmp_path / path).write_text(json.dumps(doc))
    with pytest.raises(W.FrozenMismatch):
        W.load_frozen(tmp_path)


def test_wf_total_artifact_is_the_wave1_procedure_and_threshold():
    set1 = json.loads((ROOT / "research" / "signal_discovery_wave1" / "hypotheses_set1.json").read_text())
    spec = set1["walk_forward"]["WF-TOTAL"]
    art = json.loads((ROOT / W.MODELS_DIR / "wf_total_2026.json").read_text())
    assert art["features"] == spec["features"] and art["target"] == spec["target"] == "total_resid"
    assert art["pick_threshold_points"] == spec["pick_threshold_points"] == 2.0
    feats = {"baseline.total": 46.0, "env.plays": 125.0, "env.sec_per_play": 28.0, "def_quality_sum.epa": 0.4, "off_quality_sum.epa": -0.2}
    p = W.total_prediction(art, feats, 44.5)
    c = art["coef"]
    manual = c["intercept"] + c["gap.total"] * (46.0 - 44.5) + sum(c[k] * v for k, v in feats.items() if k != "baseline.total")
    assert p == pytest.approx(manual)
    assert W.total_prediction(art, feats, None) is None  # no market center -> no prediction (never imputed)


@pytest.mark.skipif(not (ROOT / "research/signal_discovery_wave1/player_features.parquet").exists(), reason="Wave-1 player table is rebuilt locally, not committed")
def test_prop_artifact_reproduces_the_wave1_2026_predictions():
    from nfl_edge.signal_discovery import evaluate_props as EP

    set1 = json.loads((ROOT / "research/signal_discovery_wave1/hypotheses_set1.json").read_text())
    pf = EP.add_baselines(pd.read_parquet(ROOT / "research/signal_discovery_wave1/player_features.parquet"), set1["prop_families"])
    oos = pd.read_parquet(ROOT / "research/signal_discovery_wave1/prop_oos_predictions.parquet")
    art = json.loads((ROOT / W.MODELS_DIR / "prop_models_2026.json").read_text())
    fam = next(f for f in set1["prop_families"] if f["id"] == "RB_receptions")
    d = EP.family_rows(pf, fam)
    te = d[d["season"] == 2026]
    got = te.assign(pred=M.predict_prop(art["families"]["RB_receptions"], te))
    ref = oos[(oos["family"] == "RB_receptions") & (oos["season"] == 2026)]
    m = got.merge(ref, on=["game_id", "player_id"], suffixes=("", "_w1"))
    assert len(m) == len(ref) and (m["pred"] - m["pred_w1"]).abs().max() == 0.0


# --------------------------------------------------------------------------- ladders and contracts


def _r(t, yb, ya, nb=None, na=None, tk=None):
    return {"ticker": tk or f"KXNFLREC-26OCT18AAABBB-AAAP1-{t}", "threshold": t, "yes_bid": yb, "yes_ask": ya, "no_bid": nb, "no_ask": na}


def test_natural_rung_tie_break_is_the_lowest_threshold():
    lad = W.ladder([_r(4, 0.38, 0.42, 0.57, 0.63), _r(3, 0.58, 0.62, 0.37, 0.43), _r(2, 0.78, 0.82, 0.17, 0.23)])
    assert lad["natural"]["threshold"] == 3.0  # |0.60-0.5| == |0.40-0.5|: the lower threshold wins
    assert lad["market_median"] == pytest.approx(3.5)


def test_ladder_validity_and_missing_median_stay_missing():
    lad = W.ladder([_r(3, 0.30, 0.45)])  # 15c wide: not a valid mid (Wave-1 MAX_WIDTH 0.10)
    assert lad["valid_rungs"] == 0 and lad["market_median"] is None and lad["natural"] is None
    one = W.ladder([_r(3, 0.30, 0.32)])
    assert one["market_median"] is None and one["natural"]["threshold"] == 3.0


def _fee_known(price):
    return (0.02, "KNOWN")


def test_no_is_never_one_minus_yes():
    nat = W.ladder([_r(3, 0.58, 0.62, 0.36, 0.45)])["natural"]
    c = W.contract(nat, "no", _fee_known)
    assert c["ask"] == 0.45 and c["ask"] != pytest.approx(1 - 0.58)
    missing = W.ladder([_r(3, 0.58, 0.62, None, None)])["natural"]
    c2 = W.contract(missing, "no", _fee_known)
    assert c2["status"] == W.ENTRY_UNAVAILABLE and c2["reason"] == "QUOTE_NOT_EXECUTABLE" and c2["fee"] is None


def test_fee_unavailable_is_never_zero():
    nat = W.ladder([_r(3, 0.58, 0.62, 0.36, 0.45)])["natural"]
    c = W.contract(nat, "no", lambda p: (None, "DEGRADED"))
    assert c["status"] == W.FEE_UNAVAILABLE and c["fee"] is None
    assert W.economics(c, 1.0) == {"available": False, "reason": "FEE_DEGRADED"}
    from nfl_edge.execution.fees import load_fee_schedule

    q = load_fee_schedule(str(ROOT)).taker_fee(0.45, 1.0, "KXNFLREC", as_of="2026-10-18T16:50:00Z")
    assert q.state == "KNOWN" and q.amount == 0.02


def test_contract_payouts_and_exchange_values():
    yes = {"contract_side": "yes", "threshold": 3.0}
    no = {"contract_side": "no", "threshold": 3.0}
    assert W.contract_pays_by_stat(yes, 3) and not W.contract_pays_by_stat(yes, 2)
    assert W.contract_pays_by_stat(no, 2) and not W.contract_pays_by_stat(no, 3)
    assert W.contract_value_by_exchange(no, 0.0) == 1.0 and W.contract_value_by_exchange(yes, 0.37) == 0.37


def test_prop_checkpoint_is_the_last_24h_before_kickoff():
    k = KO.timestamp()
    ok = {"close_status": "CLOSE_OK", "confirmed_at": (KO - timedelta(minutes=10)).isoformat()}
    assert W.prop_checkpoint_ok(ok, k)
    assert not W.prop_checkpoint_ok({**ok, "confirmed_at": (KO - timedelta(hours=25)).isoformat()}, k)
    assert not W.prop_checkpoint_ok({**ok, "confirmed_at": KO.isoformat()}, k)
    assert not W.prop_checkpoint_ok({**ok, "close_status": "CLV_CLOSE_MISSING"}, k)


# --------------------------------------------------------------------------- the due rule (shared with the conductor)


def _games(week=6, ko=KO):
    return [{"game_id": GID, "season": 2026, "week": week, "game_type": "REG", "kickoff_utc": ko,
             "away_team": "AAA", "home_team": "BBB", "gameday": "2026-10-18", "has_result": False}]


def test_due_windows_and_population():
    assert WD.due(_games(), KO - timedelta(minutes=200), set())["observe"] == [GID]
    assert WD.due(_games(), KO - timedelta(minutes=10), set())["observe"] == []  # too late to observe
    assert WD.due(_games(), KO - timedelta(minutes=400), set())["observe"] == []
    assert WD.due(_games(week=5), KO - timedelta(minutes=200), set()) == {"observe": [], "enter": [], "settle": []}
    seen = {("OBSERVATION", GID), ("ENTRY", GID)}
    assert WD.due(_games(), KO + timedelta(minutes=10), {("OBSERVATION", GID)})["enter"] == [GID]
    assert WD.due(_games(), KO + timedelta(hours=4), seen)["settle"] == []
    assert WD.due(_games(), KO + timedelta(hours=6), seen)["settle"] == [GID]
    names = [WD.record_name("OBSERVATION", GID), WD.record_name("ENTRY", GID)]
    assert WD.seen_from_names(names) == seen


def test_conductor_and_gate_share_the_rule():
    src = (ROOT / "scripts" / "handicap" / "horizon_conductor.py").read_text()
    assert '"SIGNAL_LAB": {"workflow": "signal-lab-wave2.yml"}' in src and "signal_lab_due.due(" in src
    hc = (ROOT / ".github" / "workflows" / "horizon-conductor.yml").read_text()
    assert "RUN_NFL,THREE_ARM,WAVE2,POSTGAME,SIGNAL_LAB" in hc
    assert "wave2_due as WD" in (ROOT / "scripts" / "research" / "signal_lab_wave2.py").read_text()


def test_horizon_conductor_dispatches_an_owed_stage():
    spec = importlib.util.spec_from_file_location("hc", ROOT / "scripts" / "handicap" / "horizon_conductor.py")
    hc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(hc)
    calls = []
    lines = hc.one_pass(["SIGNAL_LAB"], _games(), "test", KO - timedelta(minutes=200), {},
                        state_readers={"SIGNAL_LAB": lambda: set()}, active=lambda wf: 0,
                        dispatcher=lambda wf, ref: (calls.append(wf) or (True, "ok")))
    assert lines[0]["decision"] == "dispatch" and calls == ["signal-lab-wave2.yml"]
    assert lines[0]["due"] == [f"observe:{GID}"]
    quiet = hc.one_pass(["SIGNAL_LAB"], _games(), "test", KO - timedelta(minutes=200), {},
                        state_readers={"SIGNAL_LAB": lambda: {("OBSERVATION", GID)}}, active=lambda wf: 0,
                        dispatcher=lambda wf, ref: (True, "ok"))
    assert quiet[0]["decision"] == "wait" and quiet[0]["due"] == []


def test_workflow_never_publishes_a_rehearsal():
    import yaml

    wf = yaml.safe_load((ROOT / ".github" / "workflows" / "signal-lab-wave2.yml").read_text())
    steps = {s.get("name"): s for s in wf["jobs"]["lab"]["steps"]}
    pub = steps["Publish the write-once records"]
    assert "inputs.rehearsal_weeks == ''" in pub["if"] and "steps.run.outcome == 'success'" in pub["if"]
    reh = steps["Rehearsal (never published)"]["run"]
    assert "/tmp/rehearsal" in reh and "publish_market_data" not in reh and "--rehearsal-weeks" in reh


# --------------------------------------------------------------------------- the enter stage on a synthetic capture


def _capture(root: Path):
    day = root / "data" / "kalshi" / "capture" / "2026-10-18"
    day.mkdir(parents=True)

    def q(run, at, ticker, series, family, stat, thr, yb, ya, nb, na, name=None, team=None):
        return {"run_id": run, "observed_at": at.isoformat(), "ticker": ticker, "event_ticker": ticker.rsplit("-", 1)[0],
                "series_ticker": series, "family": family, "period": "FULL", "stat": stat, "team": team, "player_name": name,
                "player_kalshi_id": "uuid-p1" if name else None, "threshold": thr, "operator": ">=", "game_id": GID,
                "kickoff_utc": KO.isoformat(), "status": "active", "yes_bid_dollars": f"{yb:.4f}", "yes_ask_dollars": f"{ya:.4f}",
                "no_bid_dollars": None if nb is None else f"{nb:.4f}", "no_ask_dollars": None if na is None else f"{na:.4f}"}

    r1, r2 = "20261018T153000Z", "20261018T165000Z"
    t1, t2 = KO - timedelta(minutes=90), KO - timedelta(minutes=10)
    rows1 = [
        q(r1, t1, "KXNFLREC-26OCT18AAABBB-AAAP1-2", "KXNFLREC", "PLAYER_STAT", "receptions", 2, 0.78, 0.82, 0.17, 0.23, "Pat One", "AAA"),
        q(r1, t1, "KXNFLREC-26OCT18AAABBB-AAAP1-3", "KXNFLREC", "PLAYER_STAT", "receptions", 3, 0.50, 0.54, 0.44, 0.52, "Pat One", "AAA"),
        q(r1, t1, "KXNFLREC-26OCT18AAABBB-AAAP1-4", "KXNFLREC", "PLAYER_STAT", "receptions", 4, 0.38, 0.42, 0.57, 0.63, "Pat One", "AAA"),
        q(r1, t1, "KXNFLTOTAL-26OCT18AAABBB-44", "KXNFLTOTAL", "TOTAL", "total_points", 44, 0.60, 0.64, 0.35, 0.41),
        q(r1, t1, "KXNFLTOTAL-26OCT18AAABBB-47", "KXNFLTOTAL", "TOTAL", "total_points", 47, 0.48, 0.52, 0.47, 0.53),
        q(r1, t1, "KXNFLTOTAL-26OCT18AAABBB-50", "KXNFLTOTAL", "TOTAL", "total_points", 50, 0.36, 0.40, 0.59, 0.65),
        q(r1, t1, "KXNFLREC-26OCT18AAABBB-AAAZZ9-3", "KXNFLREC", "PLAYER_STAT", "receptions", 3, 0.5, 0.52, 0.47, 0.5, "Nobody Known", "AAA"),
        q(r1, t1, "KXNFLREC-26OCT18AAABBB-BBBS2-4", "KXNFLREC", "PLAYER_STAT", "receptions", 4, 0.68, 0.72, 0.27, 0.33, "Sam Two", "BBB"),
        q(r1, t1, "KXNFLREC-26OCT18AAABBB-BBBS2-5", "KXNFLREC", "PLAYER_STAT", "receptions", 5, 0.53, 0.57, 0.42, 0.48, "Sam Two", "BBB"),
        q(r1, t1, "KXNFLREC-26OCT18AAABBB-BBBS2-6", "KXNFLREC", "PLAYER_STAT", "receptions", 6, 0.33, 0.37, 0.62, 0.68, "Sam Two", "BBB"),
    ]
    rows2 = [  # later pregame moves: the props take these; the 60-180 total checkpoint must NOT
        q(r2, t2, "KXNFLREC-26OCT18AAABBB-AAAP1-3", "KXNFLREC", "PLAYER_STAT", "receptions", 3, 0.58, 0.62, 0.36, 0.45, "Pat One", "AAA"),
        q(r2, t2, "KXNFLREC-26OCT18AAABBB-AAAP1-4", "KXNFLREC", "PLAYER_STAT", "receptions", 4, 0.38, 0.42, 0.55, 0.61, "Pat One", "AAA"),
        q(r2, t2, "KXNFLTOTAL-26OCT18AAABBB-47", "KXNFLTOTAL", "TOTAL", "total_points", 47, 0.68, 0.72, 0.27, 0.33),
    ]
    post = [q("20261018T173000Z", KO + timedelta(minutes=30), "KXNFLREC-26OCT18AAABBB-AAAP1-3", "KXNFLREC", "PLAYER_STAT",
              "receptions", 3, 0.95, 0.97, 0.02, 0.04, "Pat One", "AAA")]  # after kickoff: never read
    for run, rows in ((r1, rows1), (r2, rows2), ("20261018T173000Z", post)):
        (day / f"{run}.quotes.jsonl").write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    for run, at in ((r1, t1), (r2, t2)):
        (day / f"{run}.manifest.json").write_text(json.dumps({"run_id": run, "finished_at": at.isoformat(), "series": {
            "KXNFLREC": {"n": 4, "complete": True, "observed_at": at.isoformat()},
            "KXNFLTOTAL": {"n": 3, "complete": True, "observed_at": at.isoformat()}}}))
    (root / "data" / "kalshi" / "capture" / "state.json").write_text(json.dumps({"last_seen": {}}))


class FakeResolver:
    IDS = {("Pat One", "AAA"): "00-P1", ("Sam Two", "BBB"): "00-P2"}

    def __init__(self, season):
        pass

    def resolve(self, name, team, jersey):
        gid = self.IDS.get((name, team))
        return (gid, "RESOLVED_NAME_TEAM") if gid else (None, "UNRESOLVED")


def _population():
    return pd.DataFrame([{"game_id": GID, "season": 2026, "week": 6, "game_type": "REG", "home_team": "BBB",
                          "away_team": "AAA", "kickoff": pd.Timestamp(KO)}])


def _observation(runner, out, frozen, have):
    g = next(_population().itertuples())
    doc = runner.header(W.OBSERVATION, g, KO - timedelta(minutes=200), frozen)
    doc["rows"] = [
        {"signal_id": W.PROP_001, "status": W.PENDING, "player_id": "00-P1", "team": "AAA", "position": "RB", "family": W.RB_FAMILY},
        {"signal_id": W.PROP_002, "status": W.PENDING, "player_id": "00-P2", "team": "BBB", "position": "WR", "family": "WR_receptions",
         "stat": "receptions", "kalshi_stat": "receptions", "pred": 4.9, "median_offset": 0.1, "model_median": 5.0},
        {"signal_id": W.GAME_001, "status": W.PENDING, "football": {"baseline.total": 49.0, "env.plays": 126.0, "env.sec_per_play": 27.5,
                                                                    "def_quality_sum.epa": -0.6, "off_quality_sum.epa": 0.9}},
    ]
    assert runner.write_record(out, W.OBSERVATION, GID, doc, have)


def test_enter_stage_reads_only_pre_kickoff_quotes_and_freezes_side_specific_asks(tmp_path, monkeypatch):
    runner = _runner()
    from nfl_edge.signal_discovery import markets

    monkeypatch.setattr(markets, "Resolver", FakeResolver)
    md, out = tmp_path / "md", tmp_path / "out"
    _capture(md)
    frozen = W.load_frozen(ROOT)
    have: set[str] = set()
    _observation(runner, out, frozen, have)
    res = runner.stage_enter(KO + timedelta(minutes=5), _population(), [GID], str(md), out, have, frozen)
    assert res == {"entered": 1}
    ent = json.loads((out / runner.record_path(W.ENTRY, GID)).read_text())
    rb = next(r for r in ent["rows"] if r["signal_id"] == W.PROP_001)
    assert rb["status"] == W.ELIGIBLE and rb["side"] == "no"
    assert rb["natural"]["threshold"] == 3.0 and rb["ask"] == 0.45  # the 16:50 NO ask, not the post-kickoff 0.04
    assert rb["fee"] == 0.02 and rb["market_median"] == pytest.approx(3.5)
    tot = next(r for r in ent["rows"] if r["signal_id"] == W.GAME_001)
    assert tot["market_implied_total"] == pytest.approx(47.0)  # the 15:30 in-window ladder, not the 16:50 move
    p = W.total_prediction(frozen["wf_total"], tot["football"], 47.0)
    assert tot["prediction"] == pytest.approx(p)
    assert tot["status"] == (W.ELIGIBLE if abs(p) >= 2 else W.EXCLUDED_PROTOCOL)
    assert [f["player_name"] for f in ent["identity_failures"]] == ["Nobody Known"]
    assert len([r for r in ent["rows"] if r["signal_id"] == W.PROP_001 and r["player_id"] == "00-P1"]) == 1  # one rung per player-game
    assert rb["ticker"].endswith(f"-{int(rb['rung'])}")  # threshold identity: the ticker's own strike
    assert rb["clv"]["clv"] == 0.0  # the 24 h checkpoint IS the canonical close
    rc = next(r for r in ent["rows"] if r["signal_id"] == W.PROP_002)
    assert rc["status"] == W.ELIGIBLE and rc["market_median"] == pytest.approx(5.25) and rc["model_median"] == 5.0
    if tot["status"] == W.ELIGIBLE:  # side-aware CLV against the canonical close (the 16:50 move on the 47 rung)
        assert tot["rung"] == 47.0
        assert tot["clv"]["clv"] == pytest.approx(0.20 if tot["side"] == "OVER" else -0.20)
    # write-once: a second entry for the same game is refused
    again = runner.stage_enter(KO + timedelta(minutes=6), _population(), [GID], str(md), out, have, frozen)
    assert again == {"entered": 0}


def test_a_population_game_without_an_observation_is_a_system_failure(tmp_path, monkeypatch):
    runner = _runner()
    md, out = tmp_path / "md", tmp_path / "out"
    _capture(md)
    have: set[str] = set()
    runner.stage_enter(KO + timedelta(minutes=5), _population(), [GID], str(md), out, have, W.load_frozen(ROOT))
    obs = json.loads((out / runner.record_path(W.OBSERVATION, GID)).read_text())
    assert {r["status"] for r in obs["rows"]} == {W.SYSTEM_FAILURE}
    assert {r["reason"] for r in obs["rows"]} == {"NO_OBSERVATION_BEFORE_KICKOFF"}
    assert not (out / runner.record_path(W.ENTRY, GID)).exists()  # never reconstructed


# --------------------------------------------------------------------------- verdicts


def test_no_settled_sample_is_never_zero():
    for sid in W.STREAMS:
        s = W.summarize(sid, [])
        assert s["n"] == 0 and s["display"] == "NO SETTLED SAMPLE" and s["verdict"] == W.PROSPECTIVE_TRACKING


def _rb(n, value, price=0.45):
    return [{"signal_id": W.PROP_001, "status": W.SETTLED, "game_id": f"g{i % 40}", "player_id": f"p{i}", "played": True,
             "economics": W.economics({"status": W.ELIGIBLE, "ask": price, "fee": 0.02}, value)} for i in range(n)]


def test_reads_and_falsification_follow_the_registration():
    assert W.summarize(W.PROP_001, _rb(49, 1.0))["verdict"] == W.PROSPECTIVE_TRACKING
    assert W.summarize(W.PROP_001, _rb(50, 1.0))["verdict"] == W.EARLY_READ
    assert W.summarize(W.PROP_001, _rb(299, 0.0))["verdict"] == W.INTERIM  # never rejected before 300
    assert W.summarize(W.PROP_001, _rb(300, 0.0))["verdict"] == W.REJECTED
    assert W.summarize(W.PROP_001, _rb(300, 1.0))["verdict"] == W.REVIEW_REQUIRED
    rc = [{"signal_id": W.PROP_002, "status": W.SETTLED, "game_id": f"g{i % 30}", "player_id": f"p{i}", "team": "AAA", "position": "WR",
           "family": "WR_receptions", "d": 0.5, "actual": 5.0, "market_median": 4.5, "model_median": 5.0} for i in range(200)]
    assert W.summarize(W.PROP_002, rc)["verdict"] == W.REVIEW_REQUIRED
    assert W.summarize(W.PROP_002, [{**r, "d": -0.5} for r in rc])["verdict"] == W.REJECTED
    tot = [{"signal_id": W.GAME_001, "status": W.SETTLED, "game_id": f"g{i}", "side": "OVER", "signed_residual": 1.0,
            "economics": {"available": False}} for i in range(25)]
    assert W.summarize(W.GAME_001, tot)["verdict"] == W.EARLY_READ
    assert "EDGE_CONFIRMED" not in W.VERDICT_STATES


def test_role_change_primary_unit_is_one_value_per_player_game():
    rows = [{"signal_id": W.PROP_002, "status": W.SETTLED, "game_id": "g1", "player_id": "p1", "team": "T", "position": "WR",
             "family": f, "d": d, "actual": 5, "market_median": 4, "model_median": 5} for f, d in (("WR_receptions", 1.0), ("WR_rec_yards", -3.0))]
    s = W.summarize(W.PROP_002, rows)
    assert s["n"] == 1 and s["n_ladders"] == 2 and s["mean_d_per_player_game"] == pytest.approx(-1.0)


# --------------------------------------------------------------------------- isolation


def test_wave2_code_never_touches_production_decision_paths():
    banned = ("nfl_edge.handicap", "nfl_edge.execution.router", "nfl_edge.board", "nfl_edge.staking", "bankroll",
              "nfl_edge.shadow_v2.publish", "nfl_edge.app_export", "recommend")
    for rel in ("nfl_edge/signal_discovery/wave2.py", "nfl_edge/signal_discovery/wave2_pregame.py",
                "nfl_edge/signal_discovery/wave2_models.py", "nfl_edge/signal_discovery/wave2_due.py",
                "scripts/research/signal_lab_wave2.py"):
        text = (ROOT / rel).read_text()
        imports = [ln for ln in text.splitlines() if ln.strip().startswith(("import ", "from "))]
        for b in banned:
            assert not any(b in ln for ln in imports), (rel, b)
    wf = (ROOT / ".github" / "workflows" / "signal-lab-wave2.yml").read_text()
    assert "--src data/research/signal_lab_wave2" in wf and "handicap-data" not in wf and "handicap-reports" not in wf


def test_records_carry_every_provenance_hash(tmp_path):
    runner = _runner()
    g = next(_population().itertuples())
    h = runner.header(W.OBSERVATION, g, KO - timedelta(minutes=100), W.load_frozen(ROOT))
    for k in ("candidates_sha256", "wf_total_sha256", "prop_models_sha256", "classifier_sha256", "code_sha", "generated_at", "kickoff_utc"):
        assert k in h
    assert h["generated_at"] < h["kickoff_utc"]
    assert os.path.basename(runner.record_path(W.SETTLEMENT, GID)) == f"{GID}.json"


def test_settle_stage_is_append_only_and_uses_the_stat_of_a_player_who_played(tmp_path, monkeypatch):
    import polars as pl

    runner = _runner()
    from nfl_edge.signal_discovery import markets
    from nfl_edge.sim import data as D

    monkeypatch.setattr(markets, "Resolver", FakeResolver)
    md, out = tmp_path / "md", tmp_path / "out"
    _capture(md)
    frozen = W.load_frozen(ROOT)
    have: set[str] = set()
    _observation(runner, out, frozen, have)
    runner.stage_enter(KO + timedelta(minutes=5), _population(), [GID], str(md), out, have, frozen)
    entry_text = (out / runner.record_path(W.ENTRY, GID)).read_text()
    pg = pl.DataFrame([{"game_id": GID, "player_id": "00-P1", "offense_snaps": 30, "receptions": 2.0},
                       {"game_id": GID, "player_id": "00-P2", "offense_snaps": 50, "receptions": 7.0}])
    sched = pl.DataFrame([{"game_id": GID, "home_score": 27, "away_score": 24}])
    monkeypatch.setattr(D, "load", lambda name, seasons: pg)
    monkeypatch.setattr(D, "schedule", lambda: sched)
    res = runner.stage_settle(KO + timedelta(hours=6), _population(), [GID], str(md), out, have, frozen, fetch_exchange=False)
    assert res == {"settled": 1}
    st = json.loads((out / runner.record_path(W.SETTLEMENT, GID)).read_text())
    rb = next(r for r in st["rows"] if r["signal_id"] == W.PROP_001)
    assert rb["status"] == W.SETTLED and rb["played"] and rb["actual"] == 2.0 and rb["settlement_source"] == "NFLVERSE_STAT"
    assert rb["economics"]["settlement_value"] == 1.0 and rb["economics"]["fee_adjusted_pnl"] == pytest.approx(1 - 0.45 - 0.02)
    rc = next(r for r in st["rows"] if r["signal_id"] == W.PROP_002)
    assert rc["actual"] == 7.0 and rc["d"] == pytest.approx(abs(5.25 - 7.0) - abs(5.0 - 7.0))  # model loses here
    tot = [r for r in st["rows"] if r["signal_id"] == W.GAME_001]
    for r in tot:
        assert r["actual_total"] == 51.0
        assert r["signed_residual"] == pytest.approx((1 if r["side"] == "OVER" else -1) * (51.0 - 47.0))
    assert (out / runner.record_path(W.ENTRY, GID)).read_text() == entry_text  # the frozen entry is untouched
    assert runner.stage_settle(KO + timedelta(hours=7), _population(), [GID], str(md), out, have, frozen, fetch_exchange=False) == {"settled": 0}


def test_settlement_waits_when_a_result_is_missing(tmp_path, monkeypatch):
    import polars as pl

    runner = _runner()
    from nfl_edge.signal_discovery import markets
    from nfl_edge.sim import data as D

    monkeypatch.setattr(markets, "Resolver", FakeResolver)
    md, out = tmp_path / "md", tmp_path / "out"
    _capture(md)
    frozen = W.load_frozen(ROOT)
    have: set[str] = set()
    _observation(runner, out, frozen, have)
    runner.stage_enter(KO + timedelta(minutes=5), _population(), [GID], str(md), out, have, frozen)
    monkeypatch.setattr(D, "load", lambda name, seasons: pl.DataFrame({"game_id": [], "player_id": [], "offense_snaps": [], "receptions": []}))
    monkeypatch.setattr(D, "schedule", lambda: pl.DataFrame([{"game_id": GID, "home_score": None, "away_score": None}]))
    assert runner.stage_settle(KO + timedelta(hours=6), _population(), [GID], str(md), out, have, frozen, fetch_exchange=False) == {"settled": 0}
    assert not (out / runner.record_path(W.SETTLEMENT, GID)).exists()  # nothing invented; retried later


def test_clv_missing_close_stays_missing():
    c = {"status": W.ELIGIBLE, "contract_side": "no", "ask": 0.45}
    assert W.clv(None, c) == {"clv": None, "close_ask": None, "reason": "CLV_CLOSE_MISSING"}
    assert W.clv({"close_status": "CLV_CLOSE_MISSING"}, c)["clv"] is None
    assert W.clv({"close_status": "CLOSE_OK", "no_ask": None, "yes_ask": 0.6}, c)["clv"] is None  # never from YES
    assert W.clv({"close_status": "CLOSE_OK", "no_ask": 0.41}, c)["clv"] == pytest.approx(-0.04)


def test_the_prospective_job_never_refits_a_model():
    text = (ROOT / "scripts" / "research" / "signal_lab_wave2.py").read_text()
    for banned in ("fit_wf_total", "fit_prop", "_fit_predict", "walk_forward", "np.linalg.solve", "stats.ols"):
        assert banned not in text, banned
    assert "W.load_frozen(ROOT)" in text


@pytest.mark.skipif(not (ROOT / "data/raw/nflverse/pbp").exists() or not (ROOT / "research/signal_discovery_wave1/player_features.parquet").exists(),
                    reason="needs the local nflverse corpus and the Wave-1 player table")
def test_pregame_features_reproduce_wave1_and_ignore_the_future():
    """Phantom rows at a cutoff before week-4 kickoffs equal the Wave-1 rows of the players who played; anything at or
    after the cutoff (the week's own results, later weeks) is excluded by construction."""
    from nfl_edge.signal_discovery import evaluate_props as EP
    from nfl_edge.signal_discovery import wave2_pregame as WP
    from nfl_edge.sim import data as D

    set1 = json.loads((ROOT / "research/signal_discovery_wave1/hypotheses_set1.json").read_text())
    sched = pd.DataFrame(D.schedule().to_dicts())
    gids = sched[(sched.season == 2026) & (sched.week == 4)]["game_id"].tolist()
    gr = WP.game_rows(2026, 4, gids)
    out, meta = WP.player_rows(2026, 4, gr, datetime(2026, 10, 1, 12, 0, tzinfo=UTC), None, set1["prop_families"])
    assert meta["latest_history_game"] < "2026_04"  # nothing from week 4 or later entered the history
    w1 = EP.add_baselines(pd.read_parquet(ROOT / "research/signal_discovery_wave1/player_features.parquet"), set1["prop_families"])
    w1 = w1[(w1.season == 2026) & (w1.week == 4)]
    m = out.merge(w1, on=["game_id", "player_id"], suffixes=("", "_w1"))
    assert len(m) == len(w1)
    for c in ("sh_target_s", "sh_carry_l", "snap_share_l", "n_prior", "rt_ypc", "ctx.expected_script", "b_ewma.receptions",
              "b_season.receptions", "b_usage.rec_yards"):
        a, b = m[c].astype(float), m[f"{c}_w1"].astype(float)
        assert ((a - b).abs().fillna(0) == 0).all() and (a.isna() == b.isna()).all(), c
    assert out[["receptions", "rec_yards", "pass_yards"]].isna().all().all()  # a phantom row carries no outcome
