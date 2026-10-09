"""Wave 2B (NFL): RB receptions market-mechanism study -- integrity.

The study is explanatory: it leaves every Wave-2 file and pin untouched, never writes the prospective store, imports
the frozen natural rung, uses the captured NO ask in 2026 and labels the reconstructed 2025 one, decides membership
without outcomes, reads only pre-kickoff quotes and strictly earlier games, and is deterministic.

Synthetic checks run everywhere. Checks on the committed study outputs run whenever those files exist.
"""

from __future__ import annotations

import gzip
import hashlib
import inspect
import json
from datetime import datetime
from pathlib import Path

import pytest

from nfl_edge.signal_discovery import rb_mechanism as R
from nfl_edge.signal_discovery import wave2 as W

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "research" / "rb_receptions_mechanism"
WAVE2A = ROOT / "research" / "signal_discovery_wave2a"
ROWS26, ROWS25 = OUT / "rows_2026.jsonl.gz", OUT / "rows_2025.jsonl.gz"
LAD26, QH = OUT / "ladders_2026.jsonl.gz", OUT / "quote_history_2026.jsonl.gz"
REPORT = OUT / "mechanism_report.json"
HAVE = ROWS26.exists() and ROWS25.exists() and LAD26.exists()
need_outputs = pytest.mark.skipif(not HAVE, reason="study outputs not built")

#: SHA-256 of the frozen Wave-2 / Wave-2A files at the study's base commit (ad32b19). Never edit them.
FROZEN_FILES = {
    "nfl_edge/signal_discovery/wave2.py": "9a3c5c73a690ae8d00f33f63aa8481f8052dda1a3633ef9d5c9ae998eea3b874",
    "nfl_edge/signal_discovery/wave2_models.py": "ad8fc8521681b11438f3832adaa290293ccd31ae122145d1e933ef184070cd86",
    "nfl_edge/signal_discovery/wave2_pregame.py": "dbee8ac1af2334ae8b7d05c5ecb5b476c21dc7950ee5786b09f01f4165d0c609",
    "nfl_edge/signal_discovery/wave2_due.py": "514be47278348ea9246481fffb51af7c21679157acceeed09efa03b93fdab376",
    "nfl_edge/signal_discovery/wave2a.py": "bc0ee9c14226e1549198a3862e887d6ce1f55763f9d8f1d3d9fd4242b62be915",
    "scripts/research/signal_lab_wave2.py": "464b56a57b0d0d12e8cb6f3c12889aedfebe569b3c16ac690fcf356d8c408697",
    "scripts/research/signal_lab_wave2_artifacts.py": "b75cd35a8e4838f6b9d6d7d439d64009b37be55285feec5f5094272d0b5f88bb",
    "scripts/research/signal_lab_wave2a.py": "53f155ab3b50d12cc05701d18d3ea0e6fd4d9ee8c23a488249331ce64dcb5164",
    "research/signal_discovery_wave2/candidates.json": "e08896f629836a34430e5b52b16e79903dc69e30c00051cc1208cb05e6c65b88",
    "docs/research/FOOTBALL_SIGNAL_DISCOVERY_WAVE2_PROTOCOL.md": "49e4e3e8413530f1b3fd4d28c9008a6b1a424e76c07142ee25acba08f7d483ee",
    ".github/workflows/signal-lab-wave2.yml": "4512263efff14a0d7796606ef7a6e8de0239ea72bbe857c95ba0af694a9e6026",
}


def _gz(p: Path) -> list[dict]:
    with gzip.open(p, "rt") as fh:
        return [json.loads(line) for line in fh]


def _build_module():
    import importlib.util
    import sys

    spec = importlib.util.spec_from_file_location("rb_mech_build", ROOT / "scripts" / "research" / "rb_receptions_mechanism.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["rb_mech_build"] = mod
    spec.loader.exec_module(mod)
    return mod


def _ts(s: str) -> datetime:
    return datetime.fromisoformat(str(s).replace("Z", "+00:00"))


# --------------------------------------------------------------------------- Wave 2 untouched


@pytest.mark.parametrize("rel,sha", sorted(FROZEN_FILES.items()))
def test_prospective_wave2_files_unchanged(rel, sha):
    assert hashlib.sha256((ROOT / rel).read_bytes()).hexdigest() == sha, f"{rel} changed"


def test_frozen_pins_still_load():
    frozen = W.load_frozen(ROOT)  # raises FrozenMismatch on any change
    assert frozen["candidates"]["streams"][W.PROP_001]
    assert W.CANDIDATES_SHA256.startswith("5f31bd3b") and W.PROP_MODELS_SHA256.startswith("7e308d26")


def test_protocol_hash_is_the_registered_one():
    p = ROOT / "docs" / "research" / "RB_RECEPTIONS_MECHANISM_PROTOCOL.md"
    assert hashlib.sha256(p.read_bytes()).hexdigest() == R.PROTOCOL_SHA256


@pytest.mark.parametrize("path", [
    "/x/market-data/data/research/signal_lab_wave2/entries/2026/a.json",
    "/x/market-data",
    "/home/user/md/data/kalshi/x.json",
    "/tmp/data/research/wave2/x.json",
])
def test_no_write_into_prospective_store(path):
    with pytest.raises(R.MechanismIntegrityError):
        R.assert_not_prospective(path)


def test_study_writers_are_guarded():
    src = (ROOT / "scripts" / "research" / "rb_receptions_mechanism.py").read_text()
    assert src.count("R.assert_not_prospective(") >= 3
    assert "signal_lab_wave2/" not in src.replace("signal_lab_wave2.py", "")
    an = (ROOT / "scripts" / "research" / "rb_receptions_mechanism_analyze.py").read_text()
    assert an.count(".write_text(") == 1 and '(OUT / "mechanism_report.json").write_text' in an  # one output, inside OUT


# --------------------------------------------------------------------------- frozen natural rung


def _rung(t, yb, ya, nb=None, na=None, tk=None):
    return {"threshold": t, "yes_bid": yb, "yes_ask": ya, "no_bid": nb, "no_ask": na, "ticker": tk or f"T-{t}"}


def test_natural_rung_is_the_frozen_w_ladder():
    rungs = [_rung(2, 0.70, 0.72), _rung(3, 0.45, 0.47), _rung(4, 0.20, 0.22), _rung(5, 0.08, 0.30)]
    nr = R.natural_and_rungs(rungs)
    assert nr["natural"] == W.ladder(rungs)["natural"]
    assert nr["natural"]["threshold"] == 3.0
    assert [r["offset"] for r in nr["valid_rungs"]] == [-1, 0, 1]  # the 22c-wide rung is not valid
    assert "W.ladder(" in inspect.getsource(R.natural_and_rungs)


def test_tie_break_lowest_threshold_unchanged():
    rungs = [_rung(3, 0.74, 0.76), _rung(4, 0.24, 0.26)]  # |mid - 0.5| ties exactly at 0.25
    assert R.natural_and_rungs(rungs)["natural"]["threshold"] == 3.0
    assert W.ladder(list(reversed(rungs)))["natural"]["threshold"] == 3.0


def test_membership_ignores_outcome_fields():
    rungs = [_rung(2, 0.70, 0.72), _rung(3, 0.45, 0.47), _rung(4, 0.20, 0.22)]
    a = R.natural_and_rungs(rungs)
    b = R.natural_and_rungs([{**r, "result": "yes", "actual": 9, "settlement_value_dollars": "1.0"} for r in rungs])
    assert a["natural"]["ticker"] == b["natural"]["ticker"]
    assert [r["ticker"] for r in a["valid_rungs"]] == [r["ticker"] for r in b["valid_rungs"]]
    row = {"pop": "P1", "game_id": "g", "player_id": "p", "stat": "receptions", "ticker": "t", "y": 1, "actual": 5}
    assert R.membership_key(row) == R.membership_key(R.strip_outcomes(row))
    assert not set(R.OUTCOME_FIELDS) & set(R.strip_outcomes(row))


# --------------------------------------------------------------------------- settlement semantics


def test_settlement_semantics_ge_threshold_no_push_and_non_binary():
    row = {"threshold": 3.0}
    assert R.settle(row, {"result": "yes", "settlement_value_dollars": "1.0000"}, 3.0)["y"] == 1
    assert R.settle(row, {"result": "no", "settlement_value_dollars": "0.0000"}, 2.0)["y"] == 0
    assert R.settle(row, {"result": "yes", "settlement_value_dollars": "1.0000"}, 2.0)["stat_agrees"] is False
    nb = R.settle(row, {"result": "", "settlement_value_dollars": "0.4300"}, None)
    assert nb["y"] is None and nb["settle_source"] == R.NON_BINARY_SETTLEMENT
    assert R.settle(row, None, 3.0)["settle_source"] == R.SETTLEMENT_UNAVAILABLE
    c = {"threshold": 3.0, "contract_side": "yes"}
    assert W.contract_pays_by_stat(c, 3.0) and not W.contract_pays_by_stat({**c, "contract_side": "no"}, 3.0)


def test_economics_yes_no_complement():
    e = R.economics_row({"y": 0, "no_ask": 0.48, "fee_no": 0.02, "yes_ask": 0.53, "fee_yes": 0.02})
    assert e["no_win"] and not e["yes_win"]
    assert e["no_pnl"] == pytest.approx(0.50) and e["yes_pnl"] == pytest.approx(-0.55)


def test_representations_and_missing_stays_missing():
    p = R.representations(0.47, 0.48, 0.52, 0.53)
    assert p["B_yes_mid"] == pytest.approx(0.475) and p["C_norm_mid"] == pytest.approx(0.475)
    assert p["ask_sum"] == 1.01 and p["yes_spread"] == 0.01
    assert R.representations(0.47, 0.48, None, None)["C_norm_mid"] is None


def test_implied_bins_and_discrete_helpers():
    S = {1: 0.9, 2: 0.7, 3: 0.48, 4: 0.25, 5: 0.10}
    ib = R.implied_bins(S, 3)
    assert ib == pytest.approx({"<=t-2": 0.3, "t-1": 0.22, "t": 0.23, "t+1": 0.15, ">=t+2": 0.10})
    assert sum(ib.values()) == pytest.approx(1.0)
    assert R.implied_bins({2: 0.5, 3: 0.3}, 3) is None  # t+1/t+2 missing -> not covered
    assert R.implied_bins({1: 0.6, 2: 0.3, 3: 0.1}, 1)["<=t-2"] == 0.0  # S(0) = 1
    assert R.realized_bins(2, 3)["t-1"] == 1.0 and R.realized_bins(0, 3)["<=t-2"] == 1.0
    assert R.rel_bin(0, 3) == "<=t-3" and R.rel_bin(2, 3) == "t-1" and R.rel_bin(6, 3) == ">=t+3"
    assert R.miss_class(2, 3, 0, "EXCHANGE") == "YES_LOSS_NEAR_MISS" and R.miss_class(0, 3, 0, "EXCHANGE") == "YES_LOSS_ZERO"
    assert R.monotone_violations([(2, 0.6), (3, 0.62), (4, 0.2)]) == 1
    assert R.poisson_sf(0, 2.0) == 1.0 and R.nb_sf(2, 2.0, 0.0) == pytest.approx(R.poisson_sf(2, 2.0), abs=1e-9)


def test_bootstrap_and_bh_deterministic():
    rows = [{"game_id": f"g{i % 7}", "x": (i % 5) - 2.0} for i in range(40)]
    a, b = R.boot_stat(rows, R.mean_of("x"), n_boot=300), R.boot_stat(rows, R.mean_of("x"), n_boot=300)
    assert a == b
    q = R.bh({"a": 0.01, "b": 0.04, "c": 0.5, "d": None})
    assert q["a"] == pytest.approx(0.03) and q["b"] == pytest.approx(0.06) and q["d"] is None


def test_case_study_selection_is_the_declared_ranking():
    rows = [{"player_id": p, "no_pnl": v, "no_outlay": 0.5, "no_win": v > 0, "threshold": 3, "no_ask": 0.5}
            for p, v in [("a", 0.5), ("a", 0.5), ("b", 0.5), ("c", -0.5), ("d", -0.5), ("d", -0.5), ("e", 0.0)]]
    sel = R.case_study_selection(rows, k=2)
    assert sel["top"] == ["a", "b"] and sel["bottom"] == ["d", "c"]
    assert list(inspect.signature(R.case_study_selection).parameters) == ["p1_rows", "k"]


def test_history_features_use_strictly_earlier_games():
    import pandas as pd

    B = _build_module()
    pg = pd.DataFrame([
        {"game_id": f"g{i}", "player_id": "p", "team": "T", "position": "RB", "receptions": r, "targets": r + 1, "carries": 10,
         "offense_snaps": 30, "team_targets": 30, "season": 2026, "season_type": "REG", "gameday": f"2026-09-{10 + i:02d}"}
        for i, r in enumerate([1, 2, 3, 9])])
    h = B.History(pg)
    f = h.features("p", "T", pd.Timestamp("2026-09-13"), 3.0)  # the 9-reception game is ON this date: excluded
    assert f["n_hist"] == 3 and f["last1"] == 3 and f["long16"] == pytest.approx(2.0)


# --------------------------------------------------------------------------- committed outputs


@need_outputs
def test_p1_is_exactly_the_frozen_wave2a_population_with_captured_no_ask():
    recs = _gz(WAVE2A / "replay_records_2026.jsonl.gz")
    settled = {(d["game_id"], r["player_id"]): r for d in recs if d["record"] == W.SETTLEMENT for r in d["rows"]
               if r["signal_id"] == W.PROP_001 and r["status"] == W.SETTLED}
    entries = {(d["game_id"], r["player_id"]): r for d in recs if d["record"] == W.ENTRY for r in d["rows"]
               if r["signal_id"] == W.PROP_001 and r["status"] == W.ELIGIBLE}
    p1 = [r for r in _gz(ROWS26) if r["pop"] == "P1"]
    assert {(r["game_id"], r["player_id"]) for r in p1} == set(settled) and len(p1) == 83
    for r in p1:
        e = entries[(r["game_id"], r["player_id"])]["natural"]
        assert r["ticker"] == e["ticker"] and r["threshold"] == e["threshold"]
        assert r["no_ask"] == e["no_ask"] and r["yes_ask"] == e["yes_ask"] and r["price_basis"] == R.CAPTURED_NO_ASK
        assert r["no_ask"] == settled[(r["game_id"], r["player_id"])]["economics"]["entry_price"]


@need_outputs
def test_2025_pricing_is_labelled_reconstructed():
    rows = _gz(ROWS25)
    assert rows and all(r["price_basis"] == R.RECONSTRUCTED_NO_ASK for r in rows)
    assert all(r["no_ask"] == pytest.approx(1 - r["yes_bid"]) for r in rows)
    assert all(r.get("C_norm_mid") is None and r.get("no_bid") is None for r in rows)


@need_outputs
def test_quotes_are_pre_kickoff():
    rows = _gz(ROWS26)
    for r in rows:
        assert _ts(r["confirmed_at"]) < _ts(r["kickoff_utc"])
        for q in (r.get("timeline") or {}).values():
            if q and q.get("observed_at"):
                assert _ts(q["observed_at"]) < _ts(r["kickoff_utc"])
    if QH.exists():
        for q in _gz(QH):
            assert _ts(q["observed_at"]) < _ts(q["kickoff_utc"])


@need_outputs
def test_no_future_role_data():
    from datetime import timedelta

    kickoff = {b["game_id"]: _ts(b["kickoff_utc"]) for b in _gz(WAVE2A / "baseline_ladders_2026.jsonl.gz")}
    for r in _gz(ROWS26):
        if r["pop"] != "P1":
            continue
        assert _ts(r["pre_cutoff"]) < _ts(r["kickoff_utc"])
        last = r.get("pre_latest_history_game")
        if last:
            # the frozen builder admits a game into history only once it is final (kickoff + 4 h <= cutoff); a same-week
            # Thursday game can qualify for a Sunday cutoff, a 2025 game always does
            if last.startswith("2026_"):
                assert kickoff[last] + timedelta(hours=4) <= _ts(r["pre_cutoff"])
            assert last != r["game_id"]
        if r.get("pre_injury_vintage"):
            assert _ts(r["pre_injury_vintage"]) <= _ts(r["pre_cutoff"])


@need_outputs
def test_ladders_ordered_and_identity_stable():
    for lad in _gz(LAD26):
        ts = [x[0] for x in lad["rungs"]]
        assert ts == sorted(ts)
    owner = {}
    for r in _gz(ROWS26):
        assert owner.setdefault(r["ticker"], r["player_id"]) == r["player_id"]


@need_outputs
def test_negative_control_membership_is_deterministic_and_outcome_blind():
    base = _gz(WAVE2A / "baseline_ladders_2026.jsonl.gz")
    expect = set()
    for b in base:
        for key, rungs in b["ladders"].items():
            nr = R.natural_and_rungs([{k: v for k, v in r.items()} for r in rungs])
            if nr["natural"] is not None and nr["market_median"] is not None:
                expect.add(nr["natural"]["ticker"])
    got = {r["ticker"] for r in _gz(ROWS26) if r["is_natural"] and r["pop"] != "P3"}
    assert got == expect


@need_outputs
def test_report_matches_rows_and_protocol():
    if not REPORT.exists():
        pytest.skip("report not built")
    rep = json.loads(REPORT.read_text())
    assert rep["schema"] == R.VERSION and rep["protocol"]["sha256"] == R.PROTOCOL_SHA256 == rep["protocol"]["sha256_now"]
    rows = _gz(ROWS26)
    assert rep["populations"]["P1"]["n"] == sum(1 for r in rows if r["pop"] == "P1")
    assert rep["settlement"]["yes_no_complement_failures"] == 0
    assert rep["positive_controls"]["threshold_order_failures"] == 0
    assert set(rep["formal_tests"]) >= {"T2", "T3", "T5", "T12_top5_share_of_pnl", "T14", "T27_t-1", "T27_le_t-2"}


@need_outputs
def test_deterministic_rerun_of_the_p1_headline():
    if not REPORT.exists():
        pytest.skip("report not built")
    rep = json.loads(REPORT.read_text())
    p1 = [r for r in _gz(ROWS26) if r["pop"] == "P1" and r.get("y") is not None]
    a, b = R.calib_summary(p1), R.calib_summary(p1)
    assert a == b
    assert a["no_roi"]["est"] == pytest.approx(rep["headline"]["P1"]["no_roi"]["est"])
    assert a["no_roi"]["ci95"] == pytest.approx(rep["headline"]["P1"]["no_roi"]["ci95"])
    assert a["B_yes_mid"]["residual"]["ci95"] == pytest.approx(rep["headline"]["P1"]["B_yes_mid"]["residual"]["ci95"])
