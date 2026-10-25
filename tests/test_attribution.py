from nfl_edge.handicap import attribution as AT


def rec(i="rec_1", ticker="KXNFLSPREAD-26OCT25AAABBB-BBB3", side="YES", created="2026-10-25T09:00:00+00:00", ko="2026-10-25T13:00:00+00:00", ceil=0.55, ask=0.50, **kw):
    d = {"recommendation_id": i, "decision": "RECOMMENDED", "market_ticker": ticker, "side": side, "created_at": created, "kickoff_utc": ko,
         "bet_up_to_probability": ceil, "yes_ask": ask, "no_ask": 1 - ask, "recommended_stake": 75, "test_only": False, "reasoning_tags": ["thesis:T1"]}
    d.update(kw)
    return d


def fill(i="w1", ticker="KXNFLSPREAD-26OCT25AAABBB-BBB3", side="YES", at="2026-10-25T09:20:00+00:00", price=0.52, action="BUY"):
    return {"imported_wager_id": i, "market_ticker": ticker, "side": side, "executed_at": at, "actual_price": price, "execution_action": action}


def test_a_fill_matching_ticker_side_window_and_ceiling_is_linked_with_its_slippage():
    a = AT.attribute([fill()], [rec()])
    r = a["rows"][0]
    assert r["state"] == AT.LINKED and r["recommendation_id"] == "rec_1" and r["lag_minutes"] == 20.0 and r["slippage_vs_recorded_ask"] == 0.02


def test_no_record_means_owner_selected_never_a_model_pick():
    a = AT.attribute([fill()], [])
    assert a["rows"][0]["state"] == AT.NONE and a["owner_selected_share"] == 1.0
    assert "no claim is made" in a["statement"]


def test_wrong_side_ticker_time_or_price_is_not_linked():
    cases = [fill(side="NO"), fill(ticker="KXNFLSPREAD-26OCT25AAABBB-BBB4"), fill(at="2026-10-25T08:00:00+00:00"), fill(at="2026-10-25T13:05:00+00:00"), fill(price=0.60)]
    out = [AT.attribute([c], [rec()])["rows"][0]["state"] for c in cases]
    assert out == [AT.NONE, AT.NONE, AT.OUTSIDE, AT.OUTSIDE, AT.OUTSIDE]


def test_two_fitting_recommendations_are_ambiguous_and_none_is_chosen():
    a = AT.attribute([fill()], [rec("rec_1"), rec("rec_2")])
    assert a["rows"][0]["state"] == AT.AMBIGUOUS and "recommendation_id" not in a["rows"][0]


def test_cashouts_are_not_matched_as_new_theses():
    assert AT.attribute([fill(action="SELL")], [rec()])["rows"][0]["state"] == "NOT_AN_ENTRY"


def test_test_only_rehearsal_and_superseded_records_never_attribute():
    recs = [rec("rec_t", test_only=True), rec("rec_r", reasoning_tags=["mode:REHEARSAL"]), rec("rec_old"), rec("rec_new", amends="rec_old")]
    real = AT.real_recommendations(recs)
    assert [r["recommendation_id"] for r in real] == ["rec_new"]


def test_roll_up_by_thesis_and_unfilled_recommendations():
    recs = [rec("rec_1"), rec("rec_2", ticker="KXNFLTOTAL-26OCT25AAABBB-44")]
    a = AT.attribute([fill()], recs)
    assert a["recommendations_filled"] == 1 and a["recommendations_unfilled"] == 1 and AT.by_thesis(a, recs) == {"T1": {"fills": 1}}
