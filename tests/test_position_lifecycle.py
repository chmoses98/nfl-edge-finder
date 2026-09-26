"""Position lifecycle: orders are transactions, episodes are positions; CLV is for entries; cash is for everything.

Fixtures use the real shapes of `imported_wager.v1` / `nfl_wager_settlement.v1` and, where named, the real
2026 figures (ATL@GB week 3; IND@KC week 2) from handicap-data.
"""
from __future__ import annotations

import pytest

from nfl_edge.handicap import actual_wager_postmortem as PM
from nfl_edge.handicap import position_lifecycle as PL
from nfl_edge.handicap.import_routed_wagers import IDENTITY_FIELDS, conflicting_fields
from nfl_edge.handicap.imported_wagers import ImportedWager, validate

KICK = "2026-09-25T00:15:00+00:00"
T = "KXNFLPASSYDS-26SEP24ATLGB-GBJLOVE10-275"


def wager(i, side, contracts, price, fee, at, ticker=T, action=None, week=3):
    w = {"imported_wager_id": f"routed-{i}", "source_bet_key": f"kalshi:v1:{i}", "season": 2026, "week": week,
         "game_date": "2026-09-24", "market_ticker": ticker, "side": side, "contracts": contracts,
         "actual_price": price, "stake": round(price * contracts + fee, 4), "fees_paid": fee,
         "executed_at": at, "fees_are_estimated": False}
    if action:
        w["execution_action"] = action
    return w


def settle(w, yes_value):
    per = yes_value if w["side"] == "YES" else 1 - yes_value
    gross = round(per * w["contracts"], 4)
    return {"source_bet_key": w["source_bet_key"], "settlement_status": "SETTLED", "settlement_id": "stl-" + w["imported_wager_id"],
            "result": "WON" if per > 0 else "LOST", "gross_return": gross,
            "net_profit_loss": round(gross - w["stake"], 4), "economics_version": "router-settlement-economics.v2"}


def close(ticker, yes_mid, kickoff=KICK, quality="EXCELLENT"):
    return {"ticker": ticker, "close_status": "CLOSE_OK", "close_quality": quality, "close_id": ticker,
            "mid": yes_mid, "no_mid": round(1 - yes_mid, 4), "kickoff_utc": kickoff}


def run(wagers, yes_value, closes, quote_at=None, week=3):
    return PM.build(wagers, [settle(w, yes_value) for w in wagers], closes, season=2026, week=week, quote_at=quote_at)


# ------------------------------------------------------------------ the Thursday cashout, exactly

def thursday():
    """The real ATL@GB Love 275 orders: 91.41 YES @0.26 (fee 1.2312), later 91.41 NO @0.67 (fee 1.4148)."""
    return [wager("yes", "YES", 91.41, 0.26, 1.2312, "2026-09-25T00:15:28Z"),
            wager("no", "NO", 91.41, 0.67, 1.4148, "2026-09-25T02:43:34Z")]


def test_cashout_is_one_episode_not_two_wagers():
    doc = run(thursday(), 1.0, [close(T, 0.245)])
    s = doc["position_lifecycle"]["summary"]
    assert s["independent_position_episodes"] == 1
    assert s["transactions"] == 2
    ep = doc["position_lifecycle"]["episodes"][0]
    assert [t["transaction_role"] for t in ep["transactions"]] == ["OPEN", "CASHOUT_CLOSE"]
    assert ep["cashout_state"] == "FULL_CASHOUT"
    assert ep["remaining_position"] == 0


def test_cashout_pnl_reconciles_with_order_settlements():
    ep = run(thursday(), 1.0, [close(T, 0.245)])["position_lifecycle"]["episodes"][0]
    # realized = (0.33 - 0.26) x 91.41 = 6.3987; fees 2.646; total 3.7527 == 91.41 - 24.9978 - 62.6595
    assert ep["realized_trading_pnl"] == pytest.approx(6.3987, abs=1e-4)
    assert ep["fees"] == pytest.approx(2.646, abs=1e-4)
    assert ep["total_episode_pnl"] == pytest.approx(3.7527, abs=1e-3)
    assert ep["reconciliation"] == "RECONCILED"
    assert ep["cashout_proceeds"] == pytest.approx(0.33 * 91.41, abs=1e-6)
    # hindsight is labelled and separate, never in P&L
    assert ep["hindsight_cashout_vs_hold"] == pytest.approx(0.33 * 91.41 - 91.41, abs=1e-4)


def test_cashout_is_never_a_clv_observation_and_live_entry_has_no_pregame_clv():
    doc = run(thursday(), 1.0, [close(T, 0.245)])
    rows = {r["imported_wager_id"]: r for r in doc["wagers"]}
    assert rows["routed-no"]["clv_state"] == PM.CLV_NOT_AN_ENTRY
    assert rows["routed-no"]["clv_per_contract"] is None
    assert rows["routed-no"]["order_clv_diagnostic"]["per_contract"] is not None  # kept, labelled, not counted
    # 00:15:28 is after the 00:15:00 scheduled kickoff: LIVE by the repository's standard, flagged as near it
    assert rows["routed-yes"]["transaction_phase"] == "LIVE"
    assert rows["routed-yes"]["clv_state"] == PM.CLV_LIVE_ENTRY
    assert doc["totals"]["clv"]["valid"] == 0
    ep = doc["position_lifecycle"]["episodes"][0]
    assert ep["entry_clv_state"] == "NOT_APPLICABLE_LIVE_ENTRY"
    assert "NEAR_SCHEDULED_KICKOFF" in ep["transactions"][0]["flags"]


def test_pregame_entry_keeps_its_clv_after_a_live_cashout():
    ws = [wager("a", "YES", 100, 0.40, 1.0, "2026-09-25T00:00:00Z"),
          wager("b", "NO", 100, 0.55, 1.0, "2026-09-25T01:30:00Z")]
    doc = run(ws, 0.0, [close(T, 0.43)])
    ep = doc["position_lifecycle"]["episodes"][0]
    assert ep["position_classification"] == "PREGAME_POSITION_FULL_CASHOUT_LIVE"
    assert ep["entry_clv_state"] == "CLV_VALID"
    assert ep["pregame_entry_clv_per_contract"] == pytest.approx(0.03)
    s = doc["position_lifecycle"]["summary"]
    assert s["pregame_entry_clv"]["valid"] == 1 and s["pregame_thesis_count"] == 1
    assert doc["totals"]["clv"]["valid"] == 1  # the exit is withdrawn from the order-level count too


# ------------------------------------------------------------------ roles

def test_open_add_reduce_close_roles_and_positions():
    ws = [wager("1", "YES", 100, 0.50, 1.0, "2026-09-24T20:00:00Z"),
          wager("2", "YES", 50, 0.40, 0.5, "2026-09-24T21:00:00Z"),
          wager("3", "NO", 60, 0.45, 0.6, "2026-09-25T01:00:00Z"),
          wager("4", "NO", 90, 0.30, 0.9, "2026-09-25T02:00:00Z")]
    ep = run(ws, 1.0, [close(T, 0.5)])["position_lifecycle"]["episodes"][0]
    roles = [(t["transaction_role"], t["position_before"], t["position_after"]) for t in ep["transactions"]]
    assert roles == [("OPEN", 0, 100), ("ADD", 100, 150), ("REDUCE", 150, 90), ("CASHOUT_CLOSE", 90, 0)]
    assert ep["reconciliation"] == "RECONCILED"


def test_partial_cashout_held_remainder_to_settlement():
    ws = [wager("1", "YES", 100, 0.50, 1.0, "2026-09-24T20:00:00Z"),
          wager("2", "NO", 40, 0.30, 0.4, "2026-09-25T01:00:00Z")]
    ep = run(ws, 1.0, [close(T, 0.5)])["position_lifecycle"]["episodes"][0]
    assert ep["cashout_state"] == "PARTIAL_CASHOUT"
    assert ep["remaining_position"] == 60
    assert ep["transactions"][-1]["transaction_role"] == "SETTLEMENT"
    assert ep["position_classification"] == "PREGAME_POSITION_PARTIAL_CASHOUT_LIVE" and ep["reductions"] == 1
    # (0.70 - 0.50) x 40 realized + (1 - 0.50) x 60 settlement - fees 1.4
    assert ep["total_episode_pnl"] == pytest.approx(8 + 30 - 1.4)
    assert ep["reconciliation"] == "RECONCILED"


def test_reversal_closes_one_episode_and_opens_another():
    ws = [wager("1", "YES", 100, 0.50, 1.0, "2026-09-24T20:00:00Z"),
          wager("2", "NO", 150, 0.40, 1.5, "2026-09-24T22:00:00Z")]
    lc = run(ws, 0.0, [close(T, 0.55)])["position_lifecycle"]
    assert lc["summary"]["independent_position_episodes"] == 2
    a, b = sorted(lc["episodes"], key=lambda e: e["direction"], reverse=True)
    assert a["direction"] == "LONG_YES" and a["cashout_state"] == "REVERSED"
    assert b["direction"] == "LONG_NO" and b["opened_quantity"] == 50
    assert a["fee_ambiguous"] and b["fee_ambiguous"]


# ------------------------------------------------------------------ buy / sell normalization

def test_reported_sell_is_replayed_by_its_exposure_and_labelled():
    # SELL YES @0.33 arrives, per the router, as the exposure it creates: NO @0.67 with execution_action=SELL.
    ws = [wager("1", "YES", 10, 0.26, 0.1, "2026-09-24T20:00:00Z", action="BUY"),
          wager("2", "NO", 10, 0.67, 0.1, "2026-09-25T01:00:00Z", action="SELL")]
    ep = run(ws, 1.0, [close(T, 0.3)])["position_lifecycle"]["episodes"][0]
    t0, t1 = ep["transactions"][:2]
    assert (t0["execution_action"], t0["action_source"]) == ("BUY", PL.ACTION_REPORTED)
    assert (t1["execution_action"], t1["transaction_role"]) == ("SELL", "CASHOUT_CLOSE")
    assert t1["yes_axis_price"] == pytest.approx(0.33)


def test_missing_verb_is_marked_as_an_assumption():
    ep = run(thursday(), 1.0, [close(T, 0.245)])["position_lifecycle"]["episodes"][0]
    assert {t["action_source"] for t in ep["transactions"] if "action_source" in t} == {PL.ACTION_ASSUMED}


def test_imported_wager_accepts_execution_action_without_changing_old_bytes():
    base = dict(imported_wager_id="routed-x", schema_version="imported_wager.v1", source_bet_key="k",
                import_batch_id="b", entry_method="IMPORTED_RECEIPT", season=2026, week=3, game_date="2026-09-24",
                market_ticker=T, side="YES", executed_at="2026-09-25T00:00:00Z", contracts=1.0, actual_price=0.5,
                stake=0.52)
    assert "execution_action" not in ImportedWager(**base).to_dict()
    rec = ImportedWager(**base, execution_action="SELL").to_dict()
    assert rec["execution_action"] == "SELL" and validate(rec) == []
    assert validate(dict(rec, execution_action="HOLD"))
    assert "execution_action" not in IDENTITY_FIELDS
    assert conflicting_fields(ImportedWager(**base).to_dict(), rec) == []


# ------------------------------------------------------------------ live exit benchmark

def quotes(yes_bid, yes_ask, age):
    def at(ticker, t):
        return {"yes_bid": yes_bid, "yes_ask": yes_ask, "age_s": age}
    return at


def test_live_exit_value_against_a_synchronized_quote():
    ep = run(thursday(), 1.0, [close(T, 0.245)], quote_at=quotes(0.32, 0.34, 18.0))["position_lifecycle"]["episodes"][0]
    x = ep["exit_quality"][0]
    assert x["state"] == "LIVE_EXIT_VALUE"
    assert x["live_exit_value_per_contract"] == pytest.approx(0.01)  # sold YES at 0.33 vs a 0.32 bid


def test_stale_or_absent_quote_is_no_valid_benchmark():
    for q in (None, quotes(0.32, 0.34, PL.LIVE_BENCHMARK_MAX_AGE_S + 1)):
        ep = run(thursday(), 1.0, [close(T, 0.245)], quote_at=q)["position_lifecycle"]["episodes"][0]
        assert ep["exit_quality"][0]["state"] == "NO_VALID_LIVE_EXIT_BENCHMARK"


def test_capture_quote_lookup_takes_latest_row_at_or_before():
    files = {"data/kalshi/capture/2026-09-25/20260925T024232Z.quotes.jsonl": [
        '{"ticker":"%s","observed_at":"2026-09-25T02:43:16+00:00","yes_bid_dollars":"0.3300","yes_ask_dollars":"0.3400"}' % T,
        '{"ticker":"%s","observed_at":"2026-09-25T02:44:00+00:00","yes_bid_dollars":"0.9900","yes_ask_dollars":"0.9950"}' % T]}
    look = PL.CaptureQuoteLookup(lambda d: [p for p in files if f"/{d}/" in p], lambda p: files[p])
    q = look(T, PL._dt("2026-09-25T02:43:34Z"))
    assert q["yes_bid"] == 0.33 and q["age_s"] == pytest.approx(18)


# ------------------------------------------------------------------ exposure: IND@KC, real figures

def test_ind_kc_turnover_is_not_capital_at_risk():
    kick = "2026-09-21T00:20:00+00:00"
    kc = "KXNFLSPREAD-26SEP20INDKC-KC5"
    td = "KXNFLTD-26SEP20INDKC-KCKWALKER9-1"
    ws = [dict(wager("kc", "YES", 1794.08, 0.54, 31.1955, "2026-09-21T00:18:22Z", ticker=kc, week=2), stake=999.9987),
          dict(wager("td", "YES", 79.78, 0.61, 1.3286, "2026-09-20T23:55:19Z", ticker=td, week=2), stake=49.9944),
          dict(wager("kcx", "NO", 1794.08, 0.97, 2.211, "2026-09-21T03:52:15Z", ticker=kc, week=2), stake=1742.4686)]
    doc = PM.build(ws, [settle(ws[0], 0.0), settle(ws[1], 0.0), settle(ws[2], 0.0)],
                   [close(kc, 0.55, kick), close(td, 0.6, kick)], season=2026, week=2)
    x = doc["position_lifecycle"]["exposure_by_game"]["26SEP20INDKC"]
    assert x["gross_transaction_volume"] == pytest.approx(2792.4617, abs=1e-3)
    assert x["original_cash_outlay"] == pytest.approx(1049.9931, abs=1e-3)
    assert x["max_simultaneous_capital_at_risk"] == pytest.approx(1049.9931, abs=1e-3)
    assert x["recycled_capital_in_volume"] == pytest.approx(1742.4686, abs=1e-3)
    s = doc["position_lifecycle"]["summary"]
    assert s["independent_position_episodes"] == 2 and s["full_cashout_count"] == 1
    assert s["total_pnl"] == pytest.approx(1794.08 - 999.9987 - 1742.4686 - 49.9944, abs=1e-3)


# ------------------------------------------------------------------ phase

@pytest.mark.parametrize("at,phase", [("2026-09-25T00:14:59Z", "PRE_GAME"), ("2026-09-25T00:15:00Z", "LIVE"),
                                      ("2026-09-25T02:00:00Z", "LIVE")])
def test_phase_boundary_is_scheduled_kickoff(at, phase):
    assert PL.phase_of(at, KICK)[0] == phase


def test_no_kickoff_is_unknown_phase_and_not_pregame_clv():
    assert PL.phase_of("2026-09-25T00:00:00Z", None)[0] == "UNKNOWN"
    assert PL.phase_of("2026-09-25T05:00:00Z", KICK, "2026-09-25T03:30:00Z")[0] == "POST_FINAL"


# ------------------------------------------------------------------ anti-chase (report only)

def test_anti_chase_flags_escalation_after_a_realized_loss_and_adverse_add():
    other = "KXNFLGAME-26SEP24ATLGB-GB"
    ws = [wager("1", "YES", 100, 0.50, 1.0, "2026-09-24T20:00:00Z"),
          wager("2", "NO", 100, 0.80, 1.0, "2026-09-24T21:00:00Z"),          # closed at 0.20: a loss
          wager("3", "YES", 400, 0.60, 4.0, "2026-09-24T22:00:00Z", ticker=other),
          wager("4", "YES", 100, 0.50, 1.0, "2026-09-24T23:00:00Z", ticker=other)]  # added below the average
    doc = PM.build(ws, [settle(w, 1.0) for w in ws], [close(T, 0.3), close(other, 0.6)], season=2026, week=3)
    codes = {f["code"] for f in doc["position_lifecycle"]["anti_chase"]["flags"]}
    assert {"CHASE_RISK", "STAKE_ESCALATION_AFTER_LOSS", "REPEATED_ADD_AFTER_ADVERSE_MOVE"} <= codes
    # report only: no stake, size or block field is ever produced
    for f in doc["position_lifecycle"]["anti_chase"]["flags"]:
        assert not ({"stake", "recommended_stake", "block", "size"} & set(f))


def test_render_leads_with_episodes_and_labels_orders_as_transactions():
    md = PM.render(run(thursday(), 1.0, [close(T, 0.245)]))
    assert md.index("POSITION EPISODES") < md.index("Orders (transactions -- NOT independent bets)")
    assert "CASHOUT_CLOSE" in md
