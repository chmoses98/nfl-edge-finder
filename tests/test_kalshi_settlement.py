"""Terminality: a `result` is not a settlement, and a failed read is not an absence.

Two confusions this file exists to prevent, both of which would put a number that can still change into a corpus
that cannot:

  * a **determined** market already has a result, and that result can be disputed and amended. Freezing it is
    freezing a draft;
  * a **failed or partial read** looks exactly like "there is no settlement" if the only thing recorded is what
    came back. One is retryable, the other is terminal, and they must never collapse into each other.
"""
import glob
import json
import os

import pytest

from nfl_edge.settlement import kalshi_settlement as KS

TICKER = "KXNFLREC-25SEP04DALPHI-PHIDRESSED88-2"
ARCHIVE = "/tmp/md/data/kalshi/backfill/markets"


def market(**kw):
    m = {"ticker": TICKER, "result": "scalar", "status": "finalized",
         "settlement_value_dollars": "0.0400", "settlement_ts": "2025-09-05T04:30:00Z",
         "event_ticker": "KXNFLREC-25SEP04DALPHI"}
    m.update(kw)
    return {k: v for k, v in m.items() if v is not None}


def book_with(*markets, source=KS.SOURCE_SNAPSHOT):
    b = KS.ExactSettlementBook()
    for m in markets:
        b.add(KS.settlement_record(m, source=source))
    return b


# ---------------------------------------------------------------- terminality
@pytest.mark.parametrize("status", ["determined", "disputed", "amended", "closed", "active", "open",
                                    "unopened", "initialized", "pending"])
def test_a_non_terminal_market_is_never_exact_settlement_evidence(status):
    rec = KS.settlement_record(market(status=status), source=KS.SOURCE_SNAPSHOT)
    terminal, why = KS.is_terminal(rec)
    assert terminal is False and status in why
    assert KS.exact_yes_payout(rec) == (None, "scalar"), (
        "a scalar value on a market that can still be amended is not a payout")
    look = book_with(market(status=status)).scalar_payout(TICKER)
    assert look.payout is None and look.retryable is True, "waiting could still change this"


@pytest.mark.parametrize("status", KS.TERMINAL_STATUSES)
def test_a_terminal_market_with_a_published_value_is_exact(status):
    rec = KS.settlement_record(market(status=status), source=KS.SOURCE_SNAPSHOT)
    assert KS.is_terminal(rec)[0] is True
    assert KS.exact_yes_payout(rec) == (0.04, "scalar")
    look = book_with(market(status=status)).scalar_payout(TICKER)
    assert look.payout == 0.04 and look.retryable is False and look.reason is None
    assert look.record["settlement_ts"] == "2025-09-05T04:30:00Z", "provenance is preserved"


def test_a_market_with_no_status_cannot_be_shown_to_be_terminal():
    rec = KS.settlement_record(market(status=None), source=KS.SOURCE_SNAPSHOT)
    terminal, why = KS.is_terminal(rec)
    assert terminal is False and "no status" in why
    assert book_with(market(status=None)).scalar_payout(TICKER).retryable is True


def test_an_unknown_status_is_treated_as_not_terminal():
    rec = KS.settlement_record(market(status="something_new"), source=KS.SOURCE_SNAPSHOT)
    assert KS.is_terminal(rec)[0] is False
    assert "not a known terminal state" in KS.is_terminal(rec)[1]


def test_a_terminal_scalar_with_no_value_is_a_terminal_deficiency_not_a_wait():
    look = book_with(market(settlement_value_dollars=None)).scalar_payout(TICKER)
    assert look.payout is None and look.retryable is False, (
        "the exchange finished and published no number; waiting cannot help, so this refuses permanently")
    assert "published no usable" in look.reason


@pytest.mark.parametrize("value", ["-0.01", "1.01", "abc", ""])
def test_a_value_outside_zero_to_one_is_not_a_payout(value):
    look = book_with(market(settlement_value_dollars=value)).scalar_payout(TICKER)
    assert look.payout is None and look.retryable is False


def test_a_terminal_non_scalar_market_is_not_a_scalar_source_and_is_not_retryable():
    look = book_with(market(result="no", settlement_value_dollars=None)).scalar_payout(TICKER)
    assert look.payout is None and look.retryable is False and "not scalar" in look.reason


def test_binary_payouts_also_require_terminality():
    assert KS.exact_yes_payout(KS.settlement_record(market(result="yes", status="finalized",
                                                          settlement_value_dollars=None),
                                                   source=KS.SOURCE_SNAPSHOT)) == (1.0, "binary")
    assert KS.exact_yes_payout(KS.settlement_record(market(result="yes", status="determined",
                                                          settlement_value_dollars=None),
                                                   source=KS.SOURCE_SNAPSHOT)) == (None, "binary")


def test_a_market_with_no_result_is_not_a_record_at_all():
    assert KS.settlement_record(market(result=""), source=KS.SOURCE_SNAPSHOT) is None
    assert KS.settlement_record({}, source=KS.SOURCE_SNAPSHOT) is None
    assert KS.exact_yes_payout(None) == (None, None)


# ---------------------------------------------------------------- snapshots
def test_a_snapshot_freezes_only_terminal_records_and_says_what_it_covers():
    snap = KS.build_snapshot("2025_01_DAL_PHI",
                             [market(), market(ticker="OTHER", status="determined")],
                             required_tickers=[TICKER])
    assert list(snap["markets"]) == [TICKER]
    assert snap["covers_required"] is True and snap["required_tickers_missing"] == []
    assert snap["n_non_terminal_seen"] == 1 and "OTHER" in snap["non_terminal_seen"]
    assert snap["terminal_statuses_accepted"] == list(KS.TERMINAL_STATUSES)


def test_a_snapshot_cannot_claim_to_cover_a_ticker_it_has_no_terminal_record_for():
    """Some markets coming back is not completeness."""
    snap = KS.build_snapshot("2025_01_DAL_PHI", [market(ticker="OTHER")], required_tickers=[TICKER, "OTHER"])
    assert snap["covers_required"] is False and snap["required_tickers_missing"] == [TICKER]


def test_a_snapshot_built_from_a_determined_market_covers_nothing():
    snap = KS.build_snapshot("G", [market(status="determined")], required_tickers=[TICKER])
    assert snap["markets"] == {} and snap["covers_required"] is False


# ---------------------------------------------------------------- reading
def test_the_live_read_asks_the_exchange_for_the_settled_set():
    """Asking for every status would hand us determined markets to sift; the terminal filter is the API's job."""
    calls = []

    class FakeClient:
        def markets(self, **kw):
            calls.append(kw)
            return [market()], True, None

        def market(self, ticker):
            raise AssertionError("the per-ticker fallback should not be needed here")

    out = KS.fetch_game_settlements(FakeClient(), ["KXNFLREC-25SEP04DALPHI"], [TICKER])
    assert calls and calls[0]["status"] == KS.LIVE_SETTLED_STATUS == "settled"
    assert out.complete is True and out.errors == 0 and len(out.markets) == 1


def test_an_incomplete_page_is_reported_as_incomplete():
    class FakeClient:
        def markets(self, **kw):
            return [market()], False, {"pages": 1}

        def market(self, ticker):
            return {"market": market()}

    out = KS.fetch_game_settlements(FakeClient(), ["EV"], [TICKER])
    assert out.complete is False, "a partial page must never be reported as a complete read"


def test_a_raising_client_is_reported_and_never_propagates():
    class FakeClient:
        def markets(self, **kw):
            raise OSError("connection reset")

        def market(self, ticker):
            raise OSError("connection reset")

    out = KS.fetch_game_settlements(FakeClient(), ["EV"], [TICKER])
    assert out.markets == [] and out.complete is False and out.errors >= 1
    assert any("OSError" in str(m.get("error")) for m in out.meta)


def test_the_per_ticker_fallback_still_has_to_pass_terminality():
    class FakeClient:
        def markets(self, **kw):
            return [], True, None

        def market(self, ticker):
            return {"market": market(status="determined")}

    out = KS.fetch_game_settlements(FakeClient(), ["EV"], [TICKER])
    snap = KS.build_snapshot("G", out.markets, required_tickers=[TICKER])
    assert snap["covers_required"] is False, "a fallback read of a determined market is not evidence"


def test_pinned_records_win_over_later_reads():
    b = KS.ExactSettlementBook()
    b.load_snapshot({"markets": {TICKER: {"ticker": TICKER, "result": "scalar", "status": "finalized",
                                          "settlement_value_dollars": "0.0400"}}})
    b.add(KS.settlement_record(market(settlement_value_dollars="0.9900"), source=KS.SOURCE_SNAPSHOT))
    assert b.scalar_payout(TICKER).payout == 0.04, "already-pinned evidence is never overwritten"


# ---------------------------------------------------------------- the archive's own guarantee
SAMPLE = os.path.join(os.path.dirname(__file__), "fixtures", "postgame", "kalshi_archive_sample.json")


def archive_sample():
    with open(SAMPLE) as f:
        return json.load(f)["records"]


def test_real_archived_records_all_satisfy_the_terminality_rule():
    """Runs everywhere, including CI: real exchange records, in-tree, so the rule is exercised against the shape
    the exchange actually returns rather than against a hand-written dict."""
    records = archive_sample()
    assert len(records) >= 25
    for m in records:
        rec = KS.settlement_record(m, source=KS.SOURCE_ARCHIVE)
        assert rec is not None, m.get("ticker")
        terminal, why = KS.is_terminal(rec)
        assert terminal is True, f"{m.get('ticker')} is not terminal: {why}"
        assert rec["status"] == "finalized", "the historical tier normalises terminal markets to `finalized`"


def test_real_archived_scalar_records_yield_their_exact_value():
    scalars = [m for m in archive_sample() if (m.get("result") or "").lower() == "scalar"]
    assert len(scalars) >= 10, "the sample must contain the branch this evidence exists for"
    for m in scalars:
        rec = KS.settlement_record(m, source=KS.SOURCE_ARCHIVE)
        payout, branch = KS.exact_yes_payout(rec)
        assert branch == "scalar" and payout is not None and 0.0 <= payout <= 1.0, m.get("ticker")
        assert abs(payout - float(m["settlement_value_dollars"])) < 1e-9, (
            "the payout is the exchange's published number, unmodified")


def test_the_archive_sample_is_real_and_says_where_it_came_from():
    with open(SAMPLE) as f:
        doc = json.load(f)
    assert "historical" in doc["source"] and "backfill" in doc["description"]



@pytest.mark.skipif(not os.path.isdir(ARCHIVE), reason="the market-data archive is not checked out here")
def test_every_archived_nfl_market_satisfies_the_terminality_rule():
    """The archive is written from GET /historical/markets, which Kalshi populates only for markets settled
    before its historical cutoff. That guarantee is asserted rather than assumed."""
    checked = non_terminal = 0
    for path in sorted(glob.glob(os.path.join(ARCHIVE, "*.jsonl"))):
        for line in open(path):
            m = json.loads(line)
            rec = KS.settlement_record(m, source=KS.SOURCE_ARCHIVE)
            if rec is None:
                continue
            checked += 1
            if not KS.is_terminal(rec)[0]:
                non_terminal += 1
    assert checked > 40000, f"only {checked} archived records were checked; is the archive complete?"
    assert non_terminal == 0, f"{non_terminal} archived records are not terminal, so the guarantee does not hold"


@pytest.mark.skipif(not os.path.isdir(ARCHIVE), reason="the market-data archive is not checked out here")
def test_every_archived_scalar_settlement_carries_a_usable_value():
    missing = []
    for path in sorted(glob.glob(os.path.join(ARCHIVE, "*.jsonl"))):
        for line in open(path):
            m = json.loads(line)
            if (m.get("result") or "").lower() != "scalar":
                continue
            rec = KS.settlement_record(m, source=KS.SOURCE_ARCHIVE)
            if KS.exact_yes_payout(rec)[0] is None:
                missing.append(m.get("ticker"))
    assert not missing, f"archived scalar settlements with no usable value: {missing[:5]}"
