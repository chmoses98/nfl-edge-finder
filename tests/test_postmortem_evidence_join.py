"""PR #232: router execution-evidence digests join the reconciliation record when present and change nothing when absent;
a capture-based close is labelled a PROXY, never a true close. Synthetic rows only; this repository is public, so no raw id is used."""
import json

from nfl_edge.postmortem import reconcile as R
from test_postmortem_reconcile_losses import CLOSE, T1, make, settle, wager

KEY = "k1"
SIDECAR = {"schema_version": R.EXECUTION_EVIDENCE_SCHEMA, "source_bet_key": KEY, "order_id_digest": "a" * 32, "fill_id_digests": ["b" * 32, "c" * 32],
           "fill_count": 2, "first_fill_ts": 1793000000, "last_fill_ts": 1793000005, "execution_action": "BUY", "all_taker": True, "flags": []}


def one(evidence=None, closes=None):
    ws = [wager(KEY, T1, "YES", 0.50, 100, 51.75, 1.75)]
    return R.reconcile(ws, [settle(KEY, "LOST", -51.75, 0.0)], [], closes=closes, execution_evidence=evidence)[0]


def test_without_a_sidecar_the_record_is_exactly_what_it_was_and_still_flags_missing_detail():
    r = one()
    assert "MISSING_ORDER_FILL_DETAIL" in r.flags and r.execution == {} and "execution" not in r.to_dict()
    assert r.record_sha256 == one().record_sha256


def test_a_matching_sidecar_clears_the_flag_and_carries_digests_and_the_fill_window():
    r = one({KEY: SIDECAR})
    assert "MISSING_ORDER_FILL_DETAIL" not in r.flags
    assert r.execution["order_id_digest"] == "a" * 32 and r.execution["first_fill_ts"] == 1793000000 and r.execution["fill_count"] == 2
    assert r.record_sha256 != one().record_sha256            # evidence is part of the immutable record's hash


def test_a_sidecar_with_no_fill_digests_does_not_clear_the_flag():
    r = one({KEY: {**SIDECAR, "fill_id_digests": [], "flags": ["FILL_IDS_MISSING"]}})
    assert "MISSING_ORDER_FILL_DETAIL" in r.flags and r.execution["evidence_flags"] == ["FILL_IDS_MISSING"]


def test_a_sidecar_for_another_wager_or_another_schema_is_ignored():
    assert one({KEY: {**SIDECAR, "source_bet_key": "someone-else"}}).execution == {}
    assert one({KEY: {**SIDECAR, "schema_version": "v0"}}).execution == {}
    assert "MISSING_ORDER_FILL_DETAIL" in one({"other": SIDECAR}).flags


def test_no_raw_identifier_field_is_ever_copied_from_a_sidecar():
    leaky = {**SIDECAR, "order_id": "RAW-ORDER", "fill_ids": ["RAW-FILL"], "kalshi_order_id": "RAW"}
    dumped = json.dumps(one({KEY: leaky}).to_dict())
    assert "RAW" not in dumped


def test_a_capture_is_a_proxy_and_never_a_true_close():
    r = one(closes={T1: CLOSE})
    assert r.clv["state"] == "OK" and r.clv["close_kind"] == R.CAPTURE_PROXY and r.close["kind"] == R.CAPTURE_PROXY


def test_only_an_exchange_close_source_is_reported_as_a_true_close():
    r = one(closes={T1: {**CLOSE, "source": "EXCHANGE_CLOSE_CANDLE"}})
    assert r.clv["close_kind"] == R.TRUE_CLOSE
    assert one(closes={T1: {**CLOSE, "source": "capture"}}).clv["close_kind"] == R.CAPTURE_PROXY


def test_a_missing_close_has_no_kind():
    r = one()
    assert r.close["kind"] is None and "close_kind" not in r.clv


def test_existing_make_fixture_still_reconciles():
    assert len(make()) == 4
