"""CLV sign convention, YES/NO symmetry, no-view, fee once, and the close selector's fail-closed edge cases."""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.evaluation import close as C, clv as V                                        # noqa: E402
from nfl_edge.execution import fees as F                                                    # noqa: E402
from nfl_edge.projection import quality as Q                                                # noqa: E402

KO = datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc)
GAME = "2026_01_ATL_PIT"


def proj(cv, yb=0.50, ya=0.54, **kw):
    r = {"record_id": "r1", "ticker": "KXNFLTOTAL-26SEP13ATLPIT-44", "series_ticker": "KXNFLTOTAL", "model_arm": "BOARD_V2", "horizon_label": "T-6h",
         "contract_value": cv, "yes_bid": yb, "yes_ask": ya, "no_bid": 1 - ya, "no_ask": 1 - yb}
    r.update(kw)
    return r


def close(yb, ya, quality="EXCELLENT", status="CLOSE_OK"):
    return {"close_status": status, "close_id": "c1", "close_quality": quality, "close_age_seconds": 300.0, "yes_bid": yb, "yes_ask": ya,
            "no_bid": 1 - ya, "no_ask": 1 - yb, "mid": (yb + ya) / 2, "no_mid": 1 - (yb + ya) / 2}


def test_positive_clv_means_the_market_moved_toward_the_model_side_for_both_sides():
    # model likes YES (0.60 vs mid 0.52); the market rises to 0.58 -> positive
    r = V.clv_record(proj(0.60), close(0.56, 0.60))
    assert r["model_side"] == "YES" and r["clv_mid_toward_model"] == pytest.approx(0.06) and r["movement"] == "toward"
    assert r["move_yes_mid"] == pytest.approx(0.06) and r["move_no_mid"] == pytest.approx(-0.06)
    # model likes NO (0.40 vs 0.52); the YES market rises to 0.58 -> NO fell -> negative
    r = V.clv_record(proj(0.40), close(0.56, 0.60))
    assert r["model_side"] == "NO" and r["clv_mid_toward_model"] == pytest.approx(-0.06) and r["movement"] == "away"
    # symmetry: mirroring prices and the model flips the side and keeps the magnitude
    a = V.clv_record(proj(0.60, 0.50, 0.54), close(0.56, 0.60))
    b = V.clv_record(proj(0.40, 0.46, 0.50), close(0.40, 0.44))
    assert a["clv_mid_toward_model"] == pytest.approx(b["clv_mid_toward_model"])
    assert V.SIGN_CONVENTION.startswith("POSITIVE = the market subsequently moved toward")


def test_no_view_and_missing_close_never_produce_a_number():
    r = V.clv_record(proj(0.52), close(0.56, 0.60))
    assert r["clv_status"] == "NO_VIEW" and r["clv_mid_toward_model"] is None and r["move_yes_mid"] == pytest.approx(0.06)
    r = V.clv_record(proj(0.60), {"close_status": "CLV_CLOSE_MISSING", "close_reason": "no pre-kickoff quote row", "close_quality": "MISSING"})
    assert r["clv_status"] == "CLV_CLOSE_MISSING" and "clv_mid_toward_model" not in r
    r = V.clv_record(proj(0.60), None)
    assert r["clv_status"] == "CLV_CLOSE_MISSING"


def test_entry_to_close_uses_the_ask_never_the_mid_and_the_fee_exactly_once():
    sched = F.load_fee_schedule(ROOT)
    as_of = datetime(2026, 9, 12, tzinfo=timezone.utc)
    r = V.clv_record(proj(0.60, 0.50, 0.54), close(0.56, 0.60), schedule=sched, as_of=as_of)
    assert r["entry_executable_price"] == 0.54 and r["clv_exec_toward_model"] == pytest.approx(0.58 - 0.54)
    assert r["entry_fee_state"] == "KNOWN" and r["entry_fee_per_contract"] > 0
    assert r["entry_break_even"] == pytest.approx(0.54 + r["entry_fee_per_contract"])
    assert r["clv_net_of_fee"] == pytest.approx(r["clv_exec_toward_model"] - r["entry_fee_per_contract"])
    fee_direct = -float(F.net_executable_ev(0.54, 0.54, 1.0, sched, series_ticker="KXNFLTOTAL", as_of=as_of).net_ev_dollars)
    assert r["entry_fee_per_contract"] == pytest.approx(fee_direct), "one fee, from the committed schedule, not twice"
    assert r["model_to_close"] == pytest.approx(0.60 - 0.58) and r["model_closer_than_horizon"] is True


# ------------------------------------------------------------------------------------------ close selection
def _capture(tmp_path, rows, manifests, last_seen=None):
    root = tmp_path / "capture"
    for run_id, obs, series, ticker, yb, ya, status in rows:
        day = root / obs[:10]
        day.mkdir(parents=True, exist_ok=True)
        with open(day / f"{run_id}.quotes.jsonl", "a") as f:
            f.write(json.dumps({"run_id": run_id, "observed_at": obs, "ticker": ticker, "series_ticker": series, "game_id": GAME, "kickoff_utc": KO.isoformat(),
                                "status": status, "yes_bid_dollars": yb, "yes_ask_dollars": ya, "no_bid_dollars": (None if ya is None else f"{1-float(ya):.4f}"),
                                "no_ask_dollars": (None if yb is None else f"{1-float(yb):.4f}"), "volume_fp": "10", "liquidity_dollars": "5"}) + "\n")
    for run_id, finished, series_map, partial in manifests:
        day = root / finished[:10]
        day.mkdir(parents=True, exist_ok=True)
        json.dump({"run_id": run_id, "finished_at": finished, "partial": partial, "series": series_map}, open(day / f"{run_id}.manifest.json", "w"))
    if last_seen is not None:
        json.dump({"last_seen": last_seen}, open(root / "state.json", "w"))
    return str(root)


T = "KXNFLTOTAL-26SEP13ATLPIT-44"
S = "KXNFLTOTAL"


def _iso(dt):
    return dt.isoformat()


def test_close_is_the_last_prekickoff_row_confirmed_by_the_last_complete_prekickoff_run(tmp_path):
    t1, t2, t3 = KO - timedelta(hours=5), KO - timedelta(minutes=50), KO - timedelta(minutes=8)
    root = _capture(tmp_path,
                    [("r1", _iso(t1), S, T, "0.40", "0.44", "active"), ("r2", _iso(t2), S, T, "0.50", "0.54", "active"), ("r4", _iso(KO + timedelta(minutes=30)), S, T, "0.90", "0.94", "active")],
                    [("r1", _iso(t1), {S: {"complete": True, "observed_at": _iso(t1)}}, False), ("r2", _iso(t2), {S: {"complete": True, "observed_at": _iso(t2)}}, False),
                     ("r3", _iso(t3), {S: {"complete": True, "observed_at": _iso(t3)}}, False), ("r4", _iso(KO + timedelta(minutes=30)), {S: {"complete": True, "observed_at": _iso(KO + timedelta(minutes=30))}}, False)],
                    last_seen={T: "r4"})
    idx = C.CloseIndex(root, GAME, KO.isoformat())
    c = idx.select(T, series_ticker=S)
    assert c["close_status"] == "CLOSE_OK" and c["mid"] == pytest.approx(0.52), "post-kickoff rows never become the close"
    assert c["price_source_run"] == "r2" and c["close_source_snapshot"] == "r3", "price = last change; confirmation = last complete pre-kickoff run"
    assert c["close_age_seconds"] == pytest.approx(8 * 60) and c["close_quality"] == "EXCELLENT"
    assert c["price_change_age_seconds"] == pytest.approx(50 * 60)
    assert c["close_id"] and c["close_rule_version"] == C.CLOSE_RULE_VERSION


def test_close_edge_cases_fail_closed(tmp_path):
    t1 = KO - timedelta(minutes=30)
    # capture stamped exactly at kickoff is not pre-kickoff
    root = _capture(tmp_path / "a", [("r1", _iso(KO), S, T, "0.50", "0.54", "active")], [("r1", _iso(KO), {S: {"complete": True, "observed_at": _iso(KO)}}, False)])
    assert C.CloseIndex(root, GAME, KO.isoformat()).select(T, series_ticker=S)["close_status"] == "CLV_CLOSE_MISSING"
    # kickoff moved after the projection
    root = _capture(tmp_path / "b", [("r1", _iso(t1), S, T, "0.50", "0.54", "active")], [("r1", _iso(t1), {S: {"complete": True, "observed_at": _iso(t1)}}, False)])
    c = C.CloseIndex(root, GAME, KO.isoformat()).select(T, series_ticker=S, projection_kickoff_utc=(KO + timedelta(days=1)).isoformat())
    assert c["close_status"] == "CLV_CLOSE_MISSING" and "KICKOFF_CHANGED" in c["flags"]
    # settled / closed before the game
    root = _capture(tmp_path / "c", [("r1", _iso(t1), S, T, "0.50", "0.54", "settled")], [("r1", _iso(t1), {S: {"complete": True, "observed_at": _iso(t1)}}, False)])
    assert C.CloseIndex(root, GAME, KO.isoformat()).select(T, series_ticker=S)["close_status"] == "CLV_CLOSE_MISSING"
    # one-sided book: a close exists but is flagged and the missing side is unpriced
    root = _capture(tmp_path / "d", [("r1", _iso(t1), S, T, None, "0.54", "active")], [("r1", _iso(t1), {S: {"complete": True, "observed_at": _iso(t1)}}, False)])
    c = C.CloseIndex(root, GAME, KO.isoformat()).select(T, series_ticker=S)
    assert c["close_status"] == "CLOSE_ONE_SIDED" and "ONE_SIDED" in c["flags"] and c["mid"] is None
    # huge spread flagged, kept
    root = _capture(tmp_path / "e", [("r1", _iso(t1), S, T, "0.10", "0.90", "active")], [("r1", _iso(t1), {S: {"complete": True, "observed_at": _iso(t1)}}, False)])
    assert "HUGE_SPREAD" in C.CloseIndex(root, GAME, KO.isoformat()).select(T, series_ticker=S)["flags"]
    # series partially fetched at the confirming run
    root = _capture(tmp_path / "f", [("r1", _iso(t1), S, T, "0.50", "0.54", "active")], [("r1", _iso(t1), {S: {"complete": False, "observed_at": _iso(t1)}}, True)])
    assert "SERIES_FETCH_INCOMPLETE" in C.CloseIndex(root, GAME, KO.isoformat()).select(T, series_ticker=S)["flags"]
    # market vanished long before kickoff: the last confirmation is the last run it was seen open -> STALE / MISSING by age
    t_old = KO - timedelta(days=3)
    root = _capture(tmp_path / "g", [("r1", _iso(t_old), S, T, "0.50", "0.54", "active")],
                    [("r1", _iso(t_old), {S: {"complete": True, "observed_at": _iso(t_old)}}, False), ("r2", _iso(t1), {S: {"complete": True, "observed_at": _iso(t1)}}, False)], last_seen={T: "r1"})
    c = C.CloseIndex(root, GAME, KO.isoformat()).select(T, series_ticker=S)
    assert c["close_status"] == "CLV_CLOSE_MISSING" and "TOO_OLD" in c["flags"]
    # duplicate capture rows collapse
    root = _capture(tmp_path / "h", [("r1", _iso(t1), S, T, "0.50", "0.54", "active"), ("r1", _iso(t1), S, T, "0.50", "0.54", "active")], [("r1", _iso(t1), {S: {"complete": True, "observed_at": _iso(t1)}}, False)])
    idx = C.CloseIndex(root, GAME, KO.isoformat())
    assert len(idx.quotes[T]) == 1 and idx.select(T, series_ticker=S)["close_status"] == "CLOSE_OK"
    # no rows at all
    assert C.CloseIndex(root, GAME, KO.isoformat()).select("KXNFLTOTAL-26SEP13ATLPIT-99", series_ticker=S)["close_status"] == "CLV_CLOSE_MISSING"


def test_quality_tiers_are_named_thresholds():
    assert C.quality_tier(5 * 60) == "EXCELLENT" and C.quality_tier(60 * 60) == "GOOD" and C.quality_tier(5 * 3600) == "STALE" and C.quality_tier(None) == "MISSING"


def test_horizon_quality_classes_and_flags():
    ko = KO.isoformat()
    h = Q.horizon_quality("T-24h", 1440, ko, (KO - timedelta(minutes=1440 - 3)).isoformat(), (KO - timedelta(minutes=1430)).isoformat())
    assert h["horizon_quality"] == Q.ON_TIME and h["observation_lateness_min"] == pytest.approx(3.0)
    assert Q.horizon_quality("T-24h", 1440, ko, (KO - timedelta(minutes=1440 - 30)).isoformat(), None)["horizon_quality"] == Q.LATE_ACCEPTABLE
    assert Q.horizon_quality("T-24h", 1440, ko, (KO - timedelta(minutes=1440 - 120)).isoformat(), None)["horizon_quality"] == Q.LATE_DEGRADED
    assert Q.horizon_quality("T-30m", 30, ko, KO.isoformat(), None)["horizon_quality"] == Q.MISSED
    assert Q.horizon_quality("CYCLE", None, ko, ko, None)["horizon_quality"] == Q.CYCLE
    f = Q.status_flags(support_state="PROJECTABLE_NOT_YET_VALIDATED", semantic_confidence="PROVEN", identity_confidence="RESOLVED", subject_kind="player", settlement_support="SUPPORTED", engine="PLAYER")
    assert f["has_probability"] and f["semantics_proven"] and f["identity_resolved"] and f["settlement_supported"] and f["historically_validated"]
    assert not f["prospectively_validated"] and not f["execution_supported"] and not f["betting_authorized"]
    f = Q.status_flags(support_state="RESEARCH_REQUIRED", semantic_confidence="LIKELY", identity_confidence=None, subject_kind="team", settlement_support="PLANNED", engine="SEASON")
    assert not f["has_probability"] and not f["settlement_supported"] and not f["historically_validated"]
