"""Issue #231: reconciliation, canonical settlement, CLV, loss labels, redaction. Synthetic ledger rows only."""
import json

from nfl_edge.postmortem import loss_eval as LE
from nfl_edge.postmortem import reconcile as R
from nfl_edge.postmortem import report as RP


def wager(key, ticker, side, price, contracts, stake, fees, when="2026-10-25T15:04:44Z", day="2026-10-25"):
    return {"source_bet_key": key, "market_ticker": ticker, "side": side, "actual_price": price, "contracts": contracts, "stake": stake,
            "fees_paid": fees, "fee_state": "ACTUAL_API_FILL", "fees_are_estimated": False, "executed_at": when, "game_date": day, "test_only": False}


def settle(key, result, net, gross):
    return {"source_bet_key": key, "settlement_status": "SETTLED", "result": result, "net_profit_loss": net, "gross_return": gross,
            "economics_version": "router-settlement-economics.v2"}


T1, T2, T3 = "KXNFLSPREAD-26OCT25SFATL-SF3", "KXNFLSPREAD-26OCT25SFATL-SF4", "KXNFLTOTAL-26OCT25SFATL-45"
CLOSE = {"yes_bid": 0.40, "yes_ask": 0.42, "no_bid": 0.58, "no_ask": 0.60, "quality": "CANONICAL"}


def make(closes=None):
    ws = [wager("k1", T1, "YES", 0.50, 100, 51.75, 1.75), wager("k2", T2, "YES", 0.45, 100, 46.75, 1.75, when="2026-10-25T15:04:52Z"),
          wager("k3", T3, "NO", 0.50, 100, 51.75, 1.75), wager("k4", "KXMVECROSSCATEGORY0-S2026XXXX-ABC", "YES", 0.1, 100, 11.0, 1.0)]
    ss = [settle("k1", "LOST", -51.75, 0.0), settle("k2", "LOST", -46.75, 0.0), settle("k3", "WON", 48.25, 100.0), settle("k4", "LOST", -11.0, 0.0)]
    return R.reconcile(ws, ss, [], closes=closes)


def test_missing_evidence_is_flagged_not_inferred():
    recs = {r.source_bet_key: r for r in make()}
    f = set(recs["k1"].flags)
    assert {"MISSING_RECOMMENDATION", "MISSING_ORDER_FILL_DETAIL", "MISSING_CLOSE", "MISSING_AVAILABILITY_EVIDENCE", "MISSING_KICKOFF"} <= f
    assert recs["k1"].recommendation["state"] == "NO_RECOMMENDATION_ON_RECORD" and recs["k1"].recommendation["recommendation_id"] is None
    assert recs["k4"].kind == "COMBO_UNDECODED" and "COMBO_REPORTED_SEPARATELY" in recs["k4"].flags and recs["k4"].clv["state"] == "NOT_APPLICABLE_COMBO"


def test_records_are_immutable_and_hash_is_stable():
    a, b = make()[0], make()[0]
    assert a.record_sha256 == b.record_sha256
    try:
        a.price = 0.9
        raise AssertionError("record was mutable")
    except Exception as e:  # frozen dataclass
        assert "cannot assign" in str(e) or isinstance(e, AttributeError)


def test_amendment_changes_canonical_net_but_preserves_the_filed_figure():
    ws = [wager("k1", T1, "YES", 0.50, 100, 51.75, 1.75)]
    st = [dict(settle("k1", "LOST", -53.5, 0.0))]
    am = [{"source_bet_key": "k1", "amendment_id": "amd-1", "superseded_fields": {"net_profit_loss": {"prior": -53.5, "corrected": -51.75}}}]
    (r,) = R.reconcile(ws, st, am)
    assert r.settlement["net_canonical"] == -51.75 and r.settlement["net_as_filed"] == -53.5 and r.settlement["amended"]


def test_clv_is_fee_inclusive_and_side_correct():
    recs = {r.source_bet_key: r for r in make({T1: CLOSE, T2: CLOSE, T3: CLOSE})}
    assert abs(recs["k1"].clv["clv"] - (0.41 - 0.50)) < 1e-9 and abs(recs["k1"].clv["clv_net_of_fee"] - (0.41 - 0.50 - 0.0175)) < 1e-9
    assert abs(recs["k3"].clv["close_mid_side"] - 0.59) < 1e-9          # NO side uses the NO book


def test_after_kickoff_execution_is_flagged():
    ws = [wager("k1", T1, "YES", 0.50, 100, 51.75, 1.75)]
    (r,) = R.reconcile(ws, [], [], kickoffs={"26OCT25SFATL": "2026-10-25T15:00:00+00:00"})
    assert "EXECUTED_AFTER_KICKOFF" in r.flags and "MISSING_SETTLEMENT" in r.flags


def test_loss_labels_follow_the_decision_tree():
    # no closes: ladder rung 2 is a BAD_EXPRESSION, rung 1 and the combo are INSUFFICIENT_EVIDENCE
    ev = LE.evaluate(make())
    cats = {l["source_bet_key"]: l["category"] for l in ev["losses"]}
    assert cats == {"k1": "INSUFFICIENT_EVIDENCE", "k2": "BAD_EXPRESSION", "k4": "INSUFFICIENT_EVIDENCE"}
    # with closes: k1 paid 0.50 vs close 0.41 -> BAD_PRICING; k2 stays BAD_EXPRESSION (stacked on the held thesis)
    ev = LE.evaluate(make({T1: CLOSE, T2: CLOSE, T3: CLOSE}))
    cats = {l["source_bet_key"]: l["category"] for l in ev["losses"]}
    assert cats["k1"] == "BAD_PRICING" and cats["k2"] == "BAD_EXPRESSION"
    # a loss bought at/below the close is VARIANCE
    good = {T1: {"yes_bid": 0.55, "yes_ask": 0.57, "no_bid": 0.43, "no_ask": 0.45}, T2: CLOSE, T3: CLOSE}
    assert {l["source_bet_key"]: l["category"] for l in LE.evaluate(make(good))["losses"]}["k1"] == "VARIANCE"


def test_bad_handicap_requires_a_recorded_projection():
    closes = {T1: CLOSE, T2: CLOSE, T3: CLOSE}
    ev = LE.evaluate(make(closes), model_probability={"k1": 0.60})
    assert {l["source_bet_key"]: l["category"] for l in ev["losses"]}["k1"] == "BAD_HANDICAP"
    ev = LE.evaluate(make(closes))
    row = next(l for l in ev["losses"] if l["source_bet_key"] == "k1")
    assert "HANDICAP_UNASSESSABLE_NO_PROJECTION" in row["reasons"]


def test_no_family_claim_from_a_short_window():
    ev = LE.evaluate(make({T1: CLOSE, T2: CLOSE, T3: CLOSE}))
    assert all(not v["claim_allowed"] for v in ev["family_claims"].values())
    assert ev["window"]["roi_on_outlay"]["lo90"] <= ev["window"]["roi_on_outlay"]["point"] <= ev["window"]["roi_on_outlay"]["hi90"]


def test_redacted_report_has_no_money_tickers_or_keys(tmp_path):
    led = {"wagers": [wager("k1", T1, "YES", 0.50, 100, 51.75, 1.75), wager("k2", T2, "YES", 0.45, 100, 46.75, 1.75)],
           "settlements": [settle("k1", "LOST", -51.75, 0.0), settle("k2", "LOST", -46.75, 0.0)], "amendments": [], "recommendations": []}
    rep = RP.build(led, "2026-10-22", "2026-11-01")
    blob = json.dumps(rep) + RP.dashboard(rep)
    for needle in ("KXNFL", "k1", "51.75", "46.75", "-98", "SF3"):
        assert needle not in blob, needle
    assert "private" not in rep and RP.build(led, "2026-10-22", "2026-11-01", redact=False)["private"]["records"]
    assert {i["status"] for i in rep["items"]} >= {"DONE", "UNRESOLVED", "NOT_DEMONSTRATED"}
