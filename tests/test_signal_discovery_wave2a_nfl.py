"""Football Signal Discovery Lab, Wave 2A (NFL): the retrospective replay uses the frozen Wave-2 rules and job stages
unchanged, reads no post-kickoff input, never substitutes a current injury report, never writes the prospective
store, and never lets an outcome decide membership.

Synthetic checks run everywhere; checks on the committed replay outputs run whenever those files exist; the
outcome-doctoring replay needs local nflverse data and the market-data checkout (skipped otherwise).
"""

from __future__ import annotations

import gzip
import importlib.util
import json
import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

import pytest

from nfl_edge.signal_discovery import wave2 as W
from nfl_edge.signal_discovery import wave2a as A

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "signal_discovery_wave2a"
REPORT = OUT / "replay_report_2026.json"
ROWS = OUT / "replay_rows_2026.jsonl.gz"
MD = os.environ.get("WAVE2A_MARKET_DATA", "")
HAVE_OUTPUTS = REPORT.exists() and ROWS.exists()


def _driver():
    spec = importlib.util.spec_from_file_location("signal_lab_wave2a", ROOT / "scripts" / "research" / "signal_lab_wave2a.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["signal_lab_wave2a"] = mod
    spec.loader.exec_module(mod)
    return mod


def _rows():
    with gzip.open(ROWS, "rt") as fh:
        return [json.loads(x) for x in fh]


def rung(t, yb, ya, nb=None, na=None, ticker=None):
    return {"threshold": t, "yes_bid": yb, "yes_ask": ya, "no_bid": nb, "no_ask": na, "ticker": ticker or f"T{t}"}


FEE = lambda p: (0.02, "KNOWN")  # noqa: E731


# --------------------------------------------------------------------------- RB receptions


def test_natural_rung_is_the_frozen_rule_with_lowest_threshold_tie_break():
    lad = W.ladder([rung(3.5, 0.375, 0.375, na=0.62), rung(2.5, 0.625, 0.625, na=0.45), rung(1.5, 0.80, 0.82, na=0.20),
                    rung(4.5, 0.10, 0.30, na=0.75)])  # 4.5 is invalid (width 0.20)
    assert lad["valid_rungs"] == 3
    # 3.5 (mid .375) and 2.5 (mid .625) tie exactly at |mid - .5| = .125 -> the LOWEST threshold wins
    assert lad["natural"]["threshold"] == 2.5


def test_no_is_bought_at_the_captured_no_ask_never_one_minus_yes():
    nat = W.ladder([rung(2.5, 0.48, 0.52, nb=0.46, na=0.55)])["natural"]
    c = W.contract(nat, "no", FEE)
    assert c["ask"] == 0.55 and c["ask"] != round(1 - nat["yes_ask"], 2)
    missing = W.contract({**nat, "no_ask": None}, "no", FEE)
    assert missing["status"] == W.ENTRY_UNAVAILABLE and missing["reason"] == "QUOTE_NOT_EXECUTABLE"
    assert W.contract(nat, "no", lambda p: (None, "DEGRADED"))["status"] == W.FEE_UNAVAILABLE


def test_always_no_every_valid_rung_uses_each_rungs_own_no_ask():
    rs = [rung(1.5, 0.80, 0.82, na=0.21), rung(2.5, 0.56, 0.60, na=0.45), rung(4.5, 0.10, 0.30, na=0.75)]
    out = A.no_every_valid_rung(rs, actual=2.0, fee_fn=FEE)
    assert [o["threshold"] for o in out] == [1.5, 2.5]  # the invalid rung is skipped
    assert [o["price"] for o in out] == [0.21, 0.45]
    assert [o["win"] for o in out] == [False, True]  # NO on 'stat >= t' pays iff actual < t


@pytest.mark.skipif(not HAVE_OUTPUTS, reason="replay outputs not generated")
def test_one_frozen_rb_row_per_player_game():
    rows = [r for r in _rows() if r["signal_id"] == W.PROP_001 and r["record"] == W.ENTRY]
    keys = [(r["game_id"], r["player_id"]) for r in rows]
    assert rows and len(keys) == len(set(keys))
    for r in rows:
        if r["status"] == W.ELIGIBLE:
            assert r["side"] == "no" and r["contract"]["contract_side"] == "no"
            assert r["ask"] == r["natural"]["no_ask"]  # the captured NO ask of the natural rung


# --------------------------------------------------------------------------- ROLE_CHANGE


def test_classifier_hash_is_the_frozen_one():
    assert W.classifier_sha() == W.CLASSIFIER_SHA256 == "eeec37774ca4309c018205aa0d4a7a3f3d122f86f197e4e98ac845b05936a981"


def test_paired_error_formula_and_unit():
    rows = [
        {"game_id": "g", "player_id": "p", "team": "T", "d": abs(50 - 40) - abs(44 - 40), "model_median": 44.0,
         "market_median": 50.0, "actual": 40.0},
        {"game_id": "g", "player_id": "p", "team": "T", "d": abs(5 - 7) - abs(3 - 7), "model_median": 3.0,
         "market_median": 5.0, "actual": 7.0},
    ]
    s = A.paired_summary(rows)
    assert rows[0]["d"] == 6 and rows[1]["d"] == -2
    assert s["n_player_games"] == 1 and s["mean_d"] == 2.0  # one averaged d per player-game
    assert A.paired_summary([])["display"] == W.NO_SETTLED_SAMPLE


@pytest.mark.skipif(not HAVE_OUTPUTS, reason="replay outputs not generated")
def test_injury_input_is_a_vintage_retrieved_before_the_cutoff_never_the_current_file():
    rep = json.loads(REPORT.read_text())
    seen = 0
    for gid, m in rep["pregame_inputs"].items():
        iv = m["injury_vintage"] or {}
        if iv.get("resolved"):
            seen += 1
            assert "_vintages/injuries/injuries_2026/" in iv["snapshot_path"]  # never the mutable release file
            assert datetime.fromisoformat(iv["retrieved_at"]) <= datetime.fromisoformat(m["cutoff"])
    assert seen > 0
    for r in _rows():
        if r["signal_id"] == W.PROP_002 and r["record"] == W.OBSERVATION and r["status"] == W.SYSTEM_FAILURE:
            assert r["reason"] == "INJURY_VINTAGE_UNAVAILABLE" and r["replay_exclusion"] == A.INJURY_VINTAGE_UNAVAILABLE


@pytest.mark.skipif(not HAVE_OUTPUTS, reason="replay outputs not generated")
def test_observations_precede_kickoff_and_use_only_earlier_games():
    rep = json.loads(REPORT.read_text())
    for r in _rows():
        if r["record"] == W.OBSERVATION:
            assert r["generated_at"] < r["kickoff_utc"]
            ko = datetime.fromisoformat(r["kickoff_utc"].replace("Z", "+00:00"))
            cut = datetime.fromisoformat(rep["pregame_inputs"][r["game_id"]]["cutoff"])
            assert cut == ko - timedelta(minutes=A.OBSERVE_MINUTES_BEFORE)
        if r["signal_id"] == W.PROP_002 and r.get("player_id"):
            assert r["player_id"].startswith("00-")  # stable GSIS identity


# --------------------------------------------------------------------------- totals


def test_totals_model_is_the_frozen_artifact_and_never_refit():
    frozen = W.load_frozen(ROOT)
    assert W.canonical_sha(frozen["wf_total"]) == W.WF_TOTAL_SHA256 == "37baf8ec94b569350f011cf0eefa5f1dcbff06bc45bfb8eb13083b07c786fe98"
    for p in (ROOT / "nfl_edge/signal_discovery/wave2a.py", ROOT / "scripts/research/signal_lab_wave2a.py"):
        text = p.read_text()
        assert "fit_wf_total" not in text and "lstsq" not in text and "fit_prop" not in text


@pytest.mark.skipif(not HAVE_OUTPUTS, reason="replay outputs not generated")
def test_totals_predictions_threshold_side_and_window():
    frozen = W.load_frozen(ROOT)
    n = 0
    for r in _rows():
        if r["signal_id"] != W.GAME_001 or r["record"] != W.ENTRY or r.get("prediction") is None:
            continue
        n += 1
        assert abs(W.total_prediction(frozen["wf_total"], r["football"], r["market_implied_total"]) - r["prediction"]) < 1e-9
        qualifies = abs(r["prediction"]) >= W.TOTAL_THRESHOLD
        assert (r["status"] == W.ELIGIBLE) is qualifies
        if qualifies:
            assert r["side"] == ("OVER" if r["prediction"] > 0 else "UNDER")
            assert r["contract"]["contract_side"] == ("yes" if r["side"] == "OVER" else "no")
            conf = datetime.fromisoformat(r["contract"]["quote_confirmed_at"].replace("Z", "+00:00"))
            ko = datetime.fromisoformat(r["kickoff_utc"].replace("Z", "+00:00"))
            assert ko - timedelta(minutes=180) <= conf <= ko - timedelta(minutes=60)
        else:
            assert r["replay_exclusion"] == "NOT_ELIGIBLE"
    assert n > 0


def test_totals_side_uses_the_bought_sides_own_ask():
    nat = {"threshold": 44.5, "ticker": "T", "yes_ask": 0.53, "no_ask": 0.50, "yes_bid": 0.49, "confirmed_at": None}
    assert W.contract(nat, "yes", FEE)["ask"] == 0.53 and W.contract(nat, "no", FEE)["ask"] == 0.50


# --------------------------------------------------------------------------- common


@pytest.mark.parametrize("path", ["/x/md/data/research/signal_lab_wave2/entries", "/x/market-data", "/repo/.git/objects"])
def test_replay_cannot_write_the_prospective_store(path):
    with pytest.raises(A.ReplayIntegrityError):
        A.assert_not_prospective_publish(path)
    A.assert_not_prospective_publish(str(OUT / "replay_rows_2026.jsonl.gz"))


@pytest.mark.skipif(not HAVE_OUTPUTS, reason="replay outputs not generated")
def test_replay_rows_are_labelled_and_membership_rows_carry_no_outcome():
    rep = json.loads(REPORT.read_text())
    for sid in W.STREAMS:
        assert rep["prospective"][sid] == {"status": W.PROSPECTIVE_TRACKING, "n": W.NO_SETTLED_SAMPLE}
        assert rep["streams"][sid]["independence"] == A.INDEPENDENCE[sid]
    for r in _rows():
        assert r["evidence_label"] == A.EVIDENCE_2026
        assert r["week"] <= 5  # never a Wave-2 population week
        if r["record"] in (W.OBSERVATION, W.ENTRY):
            assert "actual" not in r and "actual_total" not in r and "economics" not in r


def test_statistics_are_deterministic_and_missing_is_not_zero():
    rows = [{"game_id": f"g{i % 7}", "pnl": (0.47 if i % 3 else -0.53), "outlay": 0.53, "win": bool(i % 3), "price": 0.51,
             "fee": 0.02, "player_id": f"p{i}", "team": f"T{i % 4}", "week": 1 + i % 4} for i in range(40)]
    assert A.economics_summary(rows) == A.economics_summary(list(rows))
    assert A.economics_summary([])["display"] == W.NO_SETTLED_SAMPLE
    assert A.classify_prop001({"n": 0}) == "INSUFFICIENT_REPLAY_DATA"
    assert A.signed_summary([])["display"] == W.NO_SETTLED_SAMPLE


def test_interpretation_rules():
    assert A.classify_prop001({"n": 40, "roi": 0.05, "roi_ci95_game_cluster": [0.01, 0.1]}) == "STRONGLY_SUPPORTIVE"
    assert A.classify_prop001({"n": 40, "roi": 0.05, "roi_ci95_game_cluster": [-0.1, 0.2]}) == "SUPPORTIVE"
    assert A.classify_prop001({"n": 40, "roi": -0.2, "roi_ci95_game_cluster": [-0.3, -0.05]}) == "UNSUPPORTIVE"
    assert A.classify_prop001({"n": 40, "roi": -0.02, "roi_ci95_game_cluster": [-0.3, 0.2]}) == "MIXED"
    assert A.classify_game001({"n": 9, "mean_signed_residual": 5}) == "INSUFFICIENT_REPLAY_DATA"


@pytest.mark.skipif(
    not (MD and (ROOT / "data/raw/nflverse/pbp").exists()),
    reason="needs local nflverse data and a market-data checkout (WAVE2A_MARKET_DATA)",
)
def test_membership_does_not_depend_on_the_target_outcome(tmp_path, monkeypatch):
    """Doctor the target game's own player and team rows (and score): the frozen observation is unchanged."""
    import pandas as pd

    from nfl_edge.sim import data as D

    drv = _driver()
    J = drv.load_job()
    frozen = W.load_frozen(ROOT)
    games = drv.completed(J, J.population_games(weeks=[4]))
    g = games[games["game_id"] == "2026_04_TEN_BAL"]
    now = (g.iloc[0]["kickoff"] - pd.Timedelta(minutes=300)).to_pydatetime()

    def observe(out):
        have: set[str] = set()
        J.stage_observe(now, games, ["2026_04_TEN_BAL"], MD, out, have, frozen)
        p = next(out.rglob("*.json"))
        return json.loads(p.read_text())["rows"]

    base = observe(tmp_path / "a")
    original = D.load

    def doctored(name, seasons, *a, **k):
        df = original(name, seasons, *a, **k)
        if name in ("player_games", "team_games"):
            import polars as pl

            num = [c for c, t in zip(df.columns, df.dtypes, strict=True) if t.is_numeric() and c not in ("season", "week")]
            df = df.with_columns([pl.when(pl.col("game_id") == "2026_04_TEN_BAL").then(pl.col(c) * 3 + 7).otherwise(pl.col(c)).alias(c) for c in num])
        return df

    monkeypatch.setattr(D, "load", doctored)
    assert observe(tmp_path / "b") == base
