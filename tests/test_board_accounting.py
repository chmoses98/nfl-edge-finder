"""Board Accounting v1: every discovered contract terminates, unknown series are captured provisionally, drift is reported."""
import json
import os
import sys
from datetime import datetime, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.board import accounting as A, drift as D, provisional as P, states as S  # noqa: E402

FIX = json.load(open(os.path.join(ROOT, "tests", "fixtures", "kalshi_market_samples.json")))
REG = json.load(open(os.path.join(ROOT, "config", "kalshi_nfl_series.json")))["series"]
NOW = datetime(2026, 9, 5, 12, 0, tzinfo=timezone.utc)


def _disc():
    by_series = {}
    for m in FIX:
        by_series.setdefault(m.get("series_ticker") or m["ticker"].split("-")[0], []).append(m)
    # a brand-new unknown series, exactly the shape of the drift the audit found
    by_series["KXNFLPOTM"] = [{"ticker": "KXNFLPOTM-SEP26NFCOFFENSE-TMCMILLAN4", "event_ticker": "KXNFLPOTM-SEP26NFCOFFENSE", "series_ticker": "KXNFLPOTM",
                               "title": "NFC Offensive Player of the Month in September: Tetairoa McMillan", "strike_type": "structured",
                               "custom_strike": {"football_player": "u1"}, "status": "active"}]
    series_nfl = [{"ticker": s, "title": (REG.get(s) or {}).get("title") or ("NFL Player of the Month" if s == "KXNFLPOTM" else s), "tags": ["Football"],
                   "product_metadata": {"scope": "Monthly Awards"} if s == "KXNFLPOTM" else None} for s in by_series]
    markets = {s: {"open": {"n": len(ms), "markets": ms}} for s, ms in by_series.items()}
    return {"run_id": "20260905T120000Z", "series_nfl": series_nfl, "markets": markets, "summary": {}}


def test_every_contract_terminates_and_unknown_series_are_not_captured_as_is():
    disc = _disc()
    board = A.build_board(disc, registry_series=REG, capture_state={"last_seen": {}}, kickoffs={}, player_status={}, now=NOW)
    assert board["unexplained"]["n"] == 0
    rows = {r["ticker"]: r for r in board["rows"]}
    potm = rows["KXNFLPOTM-SEP26NFCOFFENSE-TMCMILLAN4"]
    assert potm["terminal_state"] == S.NOT_CAPTURED and "KXNFLPOTM" in potm["terminal_reason"] or "absent" in potm["terminal_reason"]
    assert all(r["terminal_state"] in S.TERMINAL_STATES for r in board["rows"])
    assert board["denominator"]["nfl_board_contracts"] + board["denominator"]["excluded_not_nfl"] == board["denominator"]["discovered_contracts"]
    # the soccer / Starbucks fixture series are excluded, and say so
    excluded = [r for r in board["rows"] if r["terminal_state"] == S.EXCLUDED]
    assert excluded and all("not an NFL series" in r["terminal_reason"] for r in excluded)


def test_provisional_capture_turns_not_captured_into_capture_only():
    disc = _disc()
    series = next(s for s in disc["series_nfl"] if s["ticker"] == "KXNFLPOTM")
    rec = P.provisional_record(series, open_markets=1, now=NOW)
    assert rec["tier"] == "LIGHT" and rec["provisional_family"] == "AWARD" and rec["semantic_confidence"] == "UNKNOWN"
    assert rec["tier"] != "FULL_MICROSTRUCTURE"
    merged = P.merge_provisional(None, [rec], REG, now=NOW)
    prov = {t: {"tier": tier} for t, tier in P.capturable_provisional(merged, REG).items()}
    board = A.build_board(disc, registry_series=REG, provisional=prov, capture_state=None, kickoffs={}, player_status={}, now=NOW)
    potm = next(r for r in board["rows"] if r["ticker"].startswith("KXNFLPOTM"))
    assert potm["terminal_state"] == S.CAPTURE_ONLY and "provisionally" in potm["terminal_reason"]
    # promotion: once the registry holds it the provisional record is retired, never deleted
    merged2 = P.merge_provisional(merged, [], {**REG, "KXNFLPOTM": {"tier": "DAILY"}}, now=NOW)
    assert merged2["series"]["KXNFLPOTM"]["status"] == "PROMOTED_TO_REGISTRY" and merged2["series"]["KXNFLPOTM"]["first_seen"] == rec["first_seen"]


def test_drift_report_names_new_series_lag_and_capture_gap():
    disc = _disc()
    rep = D.drift_report(disc, REG, capture_state={"last_seen": {}, "fingerprints": {}}, first_seen={"KXNFLPOTM": "20260901T090000Z"}, now=NOW)
    new = {r["series"]: r for r in rep["NEW_SERIES"]}
    assert "KXNFLPOTM" in new and new["KXNFLPOTM"]["registry_lag_days"] > 4
    assert any(r["series"] == "KXNFLPOTM" for r in rep["UNCLASSIFIED"])
    assert any(r["series"] == "KXNFLPOTM" and not r["in_registry"] for r in rep["CAPTURE_GAP"])
    assert rep["totals"]["new_series"] >= 1
    md = D.render_drift(rep)
    assert "KXNFLPOTM" in md


def test_post_kickoff_and_identity_states():
    disc = _disc()
    kick = {("2026-09-14", "DEN", "KC"): {"kickoff_utc": "2026-09-15T00:15:00+00:00", "game_id": "2026_01_DEN_KC"}}
    after = A.build_board(disc, registry_series=REG, capture_state=None, kickoffs=kick, player_status={}, now=datetime(2026, 9, 16, tzinfo=timezone.utc))
    kc = [r for r in after["rows"] if r["ticker"] == "KXNFLSPREAD-26SEP14DENKC-KC8"][0]
    assert kc["terminal_state"] == S.POST_KICKOFF
    before = A.build_board(disc, registry_series=REG, capture_state=None, kickoffs=kick, player_status={}, now=NOW)
    kc = [r for r in before["rows"] if r["ticker"] == "KXNFLSPREAD-26SEP14DENKC-KC8"][0]
    assert kc["terminal_state"] == S.PRICED and S.SETTLEMENT_CAPABLE in kc["stages"]
    players = [r for r in before["rows"] if r["family"] == "PLAYER_STAT" and r["terminal_state"] == S.IDENTITY_UNRESOLVED]
    assert players, "player contracts with no identity map must be IDENTITY_UNRESOLVED, not priced"


def test_projection_snapshot_drives_projected_stage():
    disc = _disc()
    kick = {("2026-09-14", "DEN", "KC"): {"kickoff_utc": "2026-09-15T00:15:00+00:00", "game_id": "2026_01_DEN_KC"}}
    proj = [{"ticker": "KXNFLSPREAD-26SEP14DENKC-KC8", "snapshot_id": "s1", "support_state": "PRICED"},
            {"ticker": "KXNFLTOTAL-26SEP14DENKC-64", "snapshot_id": "s1", "support_state": "STALE_MARKET", "support_reason": "series not confirmed"}]
    b = A.build_board(disc, registry_series=REG, capture_state=None, kickoffs=kick, player_status={}, projections=proj, now=NOW)
    rows = {r["ticker"]: r for r in b["rows"]}
    assert rows["KXNFLSPREAD-26SEP14DENKC-KC8"]["terminal_state"] == S.PRICED and S.PROJECTED in rows["KXNFLSPREAD-26SEP14DENKC-KC8"]["stages"]
    assert rows["KXNFLTOTAL-26SEP14DENKC-64"]["terminal_state"] == S.CAPTURE_ONLY and "STALE_MARKET" in rows["KXNFLTOTAL-26SEP14DENKC-64"]["terminal_reason"]
    other = [r for r in b["rows"] if r["family"] == "SPREAD" and r["ticker"] not in rows or False]
    assert b["stages"]["PROJECTED"]["n"] == 1
