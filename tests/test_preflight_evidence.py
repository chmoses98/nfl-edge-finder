"""Candidate-specific live evidence: fetched, stored, read back, gated, and replayable months later.

WHAT THIS FILE IS ABOUT
-----------------------
On 2026-09-13 the pre-trade worker checked out the whole `market-data` branch -- ~17,491 files, ~100 seconds
of runner time -- so that a gate could look up ONE ticker in a bulk capture stream whose most recent pass had
itself taken thirteen minutes to publish. The verdict landed after kickoff.

The live path now asks the venue about that one contract (two public GETs), writes the answer to an
append-only branch, reads it back, and gates against the stored bytes. Four properties have to hold, and
each of them is a way the rebuild could have gone wrong:

  FAST        no full-branch checkout on the live decision path, and no universe scan.
  HONEST      no midpoint as a price, no approximated depth, no transient failure passing as evidence.
  DURABLE     the evidence exists before the approval does, and it exists after the runner does not.
  REPLAYABLE  the same gate function, re-run against the same bytes, reaches the same verdict -- and notices
              if the bytes have changed.
"""
import hashlib
import json
import os
import shutil
import subprocess
import sys
from datetime import timedelta

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))
from nfl_edge.execution import quotes as Q               # noqa: E402
from nfl_edge.handicap import airtable_bridge as AB      # noqa: E402
from nfl_edge.handicap import approval as APPROVAL       # noqa: E402
from nfl_edge.handicap import evidence_store as ES       # noqa: E402
from nfl_edge.handicap import gates as G                 # noqa: E402
from nfl_edge.handicap import live_evidence as LE        # noqa: E402
from nfl_edge.handicap import preflight as P             # noqa: E402
from nfl_edge.handicap import risk as R                  # noqa: E402
from nfl_edge.handicap import schema as S                # noqa: E402

import preflight_airtable as W                           # noqa: E402
import replay_preflight_evidence as RP                   # noqa: E402
from preflight_fakes import DEEP, FakeKalshiClient, evidence_dir, fresh_client   # noqa: E402
from test_preflight import DECISION, TICKER, candidate, ledger                   # noqa: E402

APPROVAL_AT = DECISION + timedelta(minutes=2)
REQUEST_AT = DECISION
SIGNING_KEY = ("test-preflight-signing-key-0123456789abcdef" * 2).encode()
RID = "recoeC5wilnbBrvsT"           # the 2026-09-13 request record, kept as a reminder of what this is for


def collect_one(client=None, *, ticker=TICKER, **kw):
    client = client or fresh_client(APPROVAL_AT)
    return LE.collect(client, ticker, side="YES", airtable_record_id=RID, run_id="20260909T130000Z",
                      evidence_run_id="20260909T130200Z", **kw)


# ======================================================================================================
# FAST: one contract, two requests, no universe scan
# ======================================================================================================

def test_the_live_path_makes_exactly_two_public_gets_per_ticker():
    client = fresh_client(APPROVAL_AT)
    collect_one(client)
    assert client.calls == [("market", TICKER), ("orderbook", TICKER, 10)]


def test_it_never_scans_the_series_universe():
    """The 13-minute bulk pass is the conductor's job and must not be preflight's."""
    client = fresh_client(APPROVAL_AT)
    collect_one(client)
    for call in client.calls:
        assert call[0] in ("market", "orderbook"), call
    assert not hasattr(client, "_series_scanned")
    # And the module simply does not know how to ask for a universe.
    src = open(os.path.join(ROOT, "nfl_edge", "handicap", "live_evidence.py")).read()
    for forbidden in ("series_list", "paginate", ".markets(", ".events(", "with_nested_markets"):
        assert forbidden not in src, f"live evidence must not reach for {forbidden}"


def test_a_batch_naming_one_ticker_twice_asks_the_venue_once():
    client = fresh_client(APPROVAL_AT)
    collector = W.LiveEvidenceCollector(client)
    docs = collector.collect(
        [candidate(recommendation_id="rec_pf0000000000000001"),
         candidate(recommendation_id="rec_pf0000000000000002")],
        airtable_record_id=RID, run_id="r", evidence_run_id="e")
    assert len(docs) == 1 and collector.tickers_fetched == 1
    assert client.calls == [("market", TICKER), ("orderbook", TICKER, 10)]


def test_two_distinct_tickers_each_get_their_own_evidence():
    client = FakeKalshiClient(retrieved_at=APPROVAL_AT - timedelta(seconds=10),
                              per_ticker={"KXNFLGAME-OTHER-XXX": {"ask": 0.40}})
    docs = W.LiveEvidenceCollector(client).collect(
        [candidate(), candidate(recommendation_id="rec_pf0000000000000002",
                                market_ticker="KXNFLGAME-OTHER-XXX")],
        airtable_record_id=RID, run_id="r", evidence_run_id="e")
    assert {d["market_ticker"] for d in docs} == {TICKER, "KXNFLGAME-OTHER-XXX"}
    assert {d["market"]["yes_ask"] for d in docs} == {0.56, 0.40}


def test_LIVE_PREFLIGHT_DOES_NOT_REQUIRE_A_FULL_MARKET_DATA_CHECKOUT(tmp_path):
    """FIX 4, end to end: the whole leg runs with NO capture stream anywhere on disk."""
    store, root = evidence_dir(tmp_path)
    docs = [collect_one()]
    ctx_docs = docs
    result = P.preflight(candidate(), market_data_root=None, ledger_root=ledger(tmp_path), root=ROOT,
                         approval_as_of=APPROVAL_AT, request_created_at=REQUEST_AT,
                         capture_index=LE.EvidenceQuoteIndex(ctx_docs),
                         book_index=LE.EvidenceBookIndex(ctx_docs))
    assert result.verdict == P.APPROVED, result.blocking_reasons
    assert result.gates[G.G_QUOTE_FRESHNESS]["status"] == G.PASS
    assert result.gates[G.G_DEPTH]["status"] == G.PASS
    assert store is not None and root


def test_the_workers_own_argument_surface_no_longer_takes_market_data(capsys):
    """A muscle-memory invocation must fail loudly rather than quietly reinstating the slow path."""
    code = W.main(["--handicap-root", ROOT, "--market-data", "../market-data"])
    assert code == 2
    assert "no longer accepted" in capsys.readouterr().out


def test_the_confirmation_basis_says_the_evidence_was_a_focused_live_fetch():
    docs = [collect_one()]
    dq = Q.resolve_decision_quote(LE.EvidenceQuoteIndex(docs), TICKER, "YES", as_of=APPROVAL_AT)
    assert dq.state == Q.FRESH
    assert dq.confirmation_basis == Q.CONFIRM_LIVE
    assert dq.confirmation_basis not in (Q.CONFIRM_SERIES,), \
        "a series-completeness inference is what you need when reading someone else's bulk poll"


# ======================================================================================================
# HONEST: the price is an ask, the depth is the venue's, and a failure is a failure
# ======================================================================================================

def test_FRESH_FOCUSED_QUOTE_PASSES_FRESHNESS():
    docs = [collect_one()]
    dq = Q.resolve_decision_quote(LE.EvidenceQuoteIndex(docs), TICKER, "YES", as_of=APPROVAL_AT)
    assert dq.state == Q.FRESH and dq.is_actionable
    assert dq.age_minutes < 1.0
    assert dq.executable_price == pytest.approx(0.56)


def test_STALE_FOCUSED_QUOTE_BLOCKS():
    """The 15-minute window is unchanged. Evidence older than it is not tradable evidence."""
    old = collect_one(fresh_client(APPROVAL_AT, seconds_old=16 * 60))
    dq = Q.resolve_decision_quote(LE.EvidenceQuoteIndex([old]), TICKER, "YES", as_of=APPROVAL_AT)
    assert dq.state == Q.STALE and not dq.is_actionable
    assert dq.age_minutes > 15.0


def test_the_incident_quote_age_still_blocks():
    """17.1 minutes, the number from 2026-09-13. The gate that worked is not being loosened."""
    old = collect_one(fresh_client(APPROVAL_AT, seconds_old=int(17.1 * 60)))
    dq = Q.resolve_decision_quote(LE.EvidenceQuoteIndex([old]), TICKER, "YES", as_of=APPROVAL_AT)
    assert dq.state == Q.STALE
    assert dq.age_minutes == pytest.approx(17.1, abs=0.05)


def test_the_executable_price_is_the_ask_and_never_a_midpoint():
    doc = collect_one()
    dq = Q.resolve_decision_quote(LE.EvidenceQuoteIndex([doc]), TICKER, "YES", as_of=APPROVAL_AT)
    mid = (doc["market"]["yes_bid"] + doc["market"]["yes_ask"]) / 2.0
    assert dq.executable_price == doc["market"]["yes_ask"]
    assert dq.executable_price != pytest.approx(mid)


def test_cent_denominated_fields_are_never_read_as_probabilities():
    """`yes_ask` is 56 and `yes_ask_dollars` is 0.5600. Reading the wrong one prices a contract at $56."""
    doc = collect_one()
    assert doc["market"]["raw"]["yes_ask"] == 56, "the fake serves the API's real cents field"
    assert doc["market"]["yes_ask"] == pytest.approx(0.56)
    assert doc["quote_row"]["yes_ask_dollars"] == pytest.approx(0.56)
    assert "yes_ask" not in doc["quote_row"], "a bare cents key in the quote row would be read as dollars"


def test_FRESH_FOCUSED_BOOK_PASSES_DEPTH(tmp_path):
    r = fly(tmp_path)
    assert r.gates[G.G_DEPTH]["status"] == G.PASS, r.gates[G.G_DEPTH]
    assert r.depth["vwap"] == pytest.approx(0.56)


def test_STALE_FOCUSED_BOOK_BLOCKS(tmp_path):
    """The book has its own clock: a market fetched now and a book fetched 20 minutes ago is not a fill."""
    client = fresh_client(APPROVAL_AT, book_retrieved_at=APPROVAL_AT - timedelta(minutes=20))
    r = fly(tmp_path, client=client)
    assert r.gates[G.G_DEPTH]["status"] == G.FAIL
    assert "beyond the 15 min window" in r.gates[G.G_DEPTH]["reason"]
    assert not r.may_be_shown_as_a_bet


def test_INSUFFICIENT_DEPTH_BLOCKS(tmp_path):
    r = fly(tmp_path, client=fresh_client(APPROVAL_AT, ladder=[(0.56, 2.0)]),
            cand=candidate(proposed_stake=50, recommended_stake=50))
    assert r.gates[G.G_DEPTH]["status"] == G.FAIL
    assert "absorb only" in r.gates[G.G_DEPTH]["reason"]
    assert not r.may_be_shown_as_a_bet


def test_ASK_ABOVE_THE_CEILING_BLOCKS(tmp_path):
    """The candidate authorises up to 0.59. At 0.61 the position is not the one that was approved.

    The refreshed record is refused at the STRUCTURAL step -- a record whose own executable ask exceeds its
    own ceiling cannot be filed as a recommendation at all -- so the verdict names that rather than the
    ceiling gate. Either way it is NOT A BET, which is the property; the next test pins the gate directly.
    """
    r = fly(tmp_path, client=fresh_client(APPROVAL_AT, ask=0.61, ladder=[(0.61, 100000.0)]))
    assert not r.may_be_shown_as_a_bet
    assert any("ABOVE bet_up_to_probability" in b for b in r.blocking_reasons), r.blocking_reasons


def test_the_ceiling_gate_itself_fails_on_an_ask_above_the_ceiling():
    docs = [collect_one(fresh_client(APPROVAL_AT, ask=0.61, ladder=[(0.61, 100000.0)]))]
    rec = dict(candidate(), decision="RECOMMENDED", created_at=APPROVAL_AT.isoformat())
    ctx = P.build_context(None, root=ROOT, capture_index=LE.EvidenceQuoteIndex(docs),
                          book_index=LE.EvidenceBookIndex(docs))
    report = G.evaluate_gates(rec, ctx)
    assert report.gates[G.G_CEILING].status == G.FAIL
    assert report.gates[G.G_CEILING].evidence["executable_price"] == pytest.approx(0.61)


def test_a_walk_above_the_ceiling_blocks_even_when_the_top_is_under_it(tmp_path):
    r = fly(tmp_path, client=fresh_client(APPROVAL_AT, ladder=[(0.56, 5.0), (0.80, 100000.0)]),
            cand=candidate(proposed_stake=50, recommended_stake=50))
    assert r.gates[G.G_DEPTH]["status"] == G.FAIL
    assert "does not authorise" in r.gates[G.G_DEPTH]["reason"]


def test_an_untradable_market_status_blocks(tmp_path):
    for status in ("settled", "closed", "finalized", "paused"):
        r = fly(tmp_path, client=fresh_client(APPROVAL_AT, status=status))
        assert not r.may_be_shown_as_a_bet, status
        assert r.gates[G.G_QUOTE_FRESHNESS]["status"] in G.BLOCKING, status


def test_tradable_refusal_names_the_status():
    doc = collect_one(fresh_client(APPROVAL_AT, status="settled"))
    assert "settled" in LE.tradable_refusal(doc)
    assert LE.tradable_refusal(collect_one()) is None


# ---- API failure is never an empty market ------------------------------------------------------------

def test_AN_API_FAILURE_BLOCKS_and_is_never_an_empty_book():
    with pytest.raises(LE.EvidenceError) as e:
        collect_one(FakeKalshiClient(fail_market=True))
    assert "unreachable venue is not a fresh quote" in str(e.value)

    with pytest.raises(LE.EvidenceError) as e:
        collect_one(FakeKalshiClient(fail_book=True))
    assert "blocks rather than degrades" in str(e.value)


def test_an_empty_order_book_blocks_rather_than_degrading_to_top_of_book():
    with pytest.raises(LE.EvidenceError) as e:
        collect_one(FakeKalshiClient(empty_book=True))
    assert "not observable" in str(e.value)


def test_a_market_response_with_no_body_or_no_timestamp_blocks():
    with pytest.raises(LE.EvidenceError):
        collect_one(FakeKalshiClient(no_market=True))
    with pytest.raises(LE.EvidenceError) as e:
        collect_one(FakeKalshiClient(no_market_timestamp=True))
    assert "age cannot be established" in str(e.value)


def test_an_api_failure_answers_the_row_ERROR_and_never_APPROVED(tmp_path):
    code, fake = go(tmp_path, client=FakeKalshiClient(fail_market=True))
    assert code == 1
    assert fake.written[RID][AB.F_STATUS] == AB.STATUS_PREFLIGHT_ERROR
    assert AB.F_APPROVED_PAYLOAD not in fake.written[RID]
    assert json.loads(fake.written[RID][AB.F_PREFLIGHT_RESULT])["verdict"] == "ERROR"


# ======================================================================================================
# DURABLE: the evidence exists before the approval does
# ======================================================================================================

def test_the_evidence_path_is_immutable_by_construction():
    rel = LE.evidence_relpath(season=2026, week=1, airtable_record_id=RID, ticker=TICKER,
                              retrieved_at=APPROVAL_AT)
    assert rel.startswith("data/preflight_evidence/2026/week_01/" + RID + "/")
    assert rel.endswith(".json") and TICKER in rel


def test_a_hostile_ticker_or_record_id_cannot_escape_the_evidence_tree():
    rel = LE.evidence_relpath(season=2026, week=1, airtable_record_id="../../etc",
                              ticker="../../../root/.ssh/id_rsa", retrieved_at=APPROVAL_AT)
    assert ".." not in rel.split("/")
    assert rel.startswith("data/preflight_evidence/")
    with pytest.raises(ES.EvidenceStoreError):
        ES.DirectoryEvidenceStore("/tmp").stage("../../escape.json", "{}")
    with pytest.raises(ES.EvidenceStoreError):
        ES.DirectoryEvidenceStore("/tmp").stage("data/other/x.json", "{}")


def test_the_stored_bytes_hash_to_what_the_approval_records(tmp_path):
    code, fake = go(tmp_path)
    assert code == 0
    body = json.loads(fake.written[RID][AB.F_PREFLIGHT_RESULT])
    for entry in body["evidence"]["documents"]:
        on_disk = open(os.path.join(fake.evidence_root, entry["path"]), "rb").read()
        assert hashlib.sha256(on_disk).hexdigest() == entry["sha256"]


def test_the_evidence_contains_everything_needed_to_reproduce_the_decision(tmp_path):
    _code, fake = go(tmp_path)
    body = json.loads(fake.written[RID][AB.F_PREFLIGHT_RESULT])
    path = os.path.join(fake.evidence_root, body["evidence"]["documents"][0]["path"])
    doc = json.loads(open(path).read())
    assert doc["market_ticker"] == TICKER
    assert doc["market"]["retrieved_at"] and doc["orderbook"]["retrieved_at"]
    assert doc["market"]["yes_bid"] is not None and doc["market"]["yes_ask"] is not None
    assert doc["market"]["no_bid"] is not None and doc["market"]["no_ask"] is not None
    assert doc["market"]["status"] == "active"
    assert doc["orderbook"]["depth_requested"] == 10
    assert doc["orderbook"]["raw"]["no_dollars"]
    assert doc["request"]["airtable_record_id"] == RID and doc["request"]["run_id"]
    assert doc["evidence_run_id"]
    assert doc["market"]["raw_sha256"] and doc["orderbook"]["raw_sha256"]
    assert doc["source"]["access"].startswith("public read-only")


def test_the_evidence_carries_no_account_data_no_credentials_and_no_positions(tmp_path):
    _code, fake = go(tmp_path)
    blob = json.dumps([json.loads(open(os.path.join(fake.evidence_root, p), "rb").read())
                       for p in _all_evidence(fake.evidence_root)]).lower()
    # The prose disclaimer in `source.access` legitimately contains some of these words, so it is asserted
    # for separately and then removed before the scan.
    disclaimer = "public read-only get; no account, no credentials, no positions, no fills"
    assert disclaimer in blob
    blob = blob.replace(disclaimer, "")
    for forbidden in ("authorization", "api-key", "access_key", "private_key", "signing", "bearer",
                      "position", "fill", "order_id", "balance", "portfolio", "stake", "thesis",
                      "bankroll", "probability_mid", "airtable_token"):
        assert forbidden not in blob, f"preflight evidence must not carry {forbidden!r}"


def test_EVIDENCE_PERSISTENCE_FAILURE_BLOCKS(tmp_path):
    """A store that cannot keep the evidence must stop the approval, not shrug and carry on."""
    class Broken(ES.DirectoryEvidenceStore):
        def publish(self, message):
            raise ES.EvidenceStoreError("the evidence branch could not be pushed")

    code, fake = go(tmp_path, store=Broken(str(tmp_path / "broken")))
    assert code == 1
    assert fake.written[RID][AB.F_STATUS] == AB.STATUS_PREFLIGHT_ERROR
    assert AB.F_APPROVED_PAYLOAD not in fake.written[RID]
    assert "could not be pushed" in json.loads(fake.written[RID][AB.F_PREFLIGHT_RESULT])["error"]


def test_an_unreadable_store_blocks_even_when_the_write_appeared_to_succeed(tmp_path):
    """"We asked a store to keep this" and "this is kept" are different claims."""
    class Amnesiac(ES.DirectoryEvidenceStore):
        def read(self, relpath):
            raise ES.EvidenceStoreError("gone")

    code, fake = go(tmp_path, store=Amnesiac(str(tmp_path / "amnesiac")))
    assert code == 1 and fake.written[RID][AB.F_STATUS] == AB.STATUS_PREFLIGHT_ERROR


def test_a_store_that_returns_different_bytes_blocks(tmp_path):
    class Liar(ES.DirectoryEvidenceStore):
        def read(self, relpath):
            return super().read(relpath).replace('"yes_ask_dollars":0.56', '"yes_ask_dollars":0.10')

    code, fake = go(tmp_path, store=Liar(str(tmp_path / "liar")))
    assert code == 1 and fake.written[RID][AB.F_STATUS] == AB.STATUS_PREFLIGHT_ERROR


def test_the_store_refuses_to_rewrite_an_existing_document(tmp_path):
    store, root = evidence_dir(tmp_path)
    rel = "data/preflight_evidence/2026/week_01/x/a.json"
    store.stage(rel, '{"a":1}')
    store.stage(rel, '{"a":1}')          # identical bytes: an idempotent replay is fine
    with pytest.raises(ES.EvidenceStoreError) as e:
        store.stage(rel, '{"a":2}')
    assert "APPEND-ONLY VIOLATION" in str(e.value)


def test_the_approval_names_the_evidence_and_is_signed_over_it(tmp_path):
    _code, fake = go(tmp_path)
    written = fake.written[RID]
    body = json.loads(written[AB.F_PREFLIGHT_RESULT])
    assert body["verdict"] == "APPROVED"
    ev = body["evidence"]
    assert ev["documents"] and ev["manifest_sha256"] and ev["storage"]
    assert body["evidence_manifest_sha256"] == ev["manifest_sha256"]

    verified = APPROVAL.verify(
        body, key=SIGNING_KEY, airtable_record_id=RID, run_id="20260909T130000Z",
        candidate_payload=json.dumps([candidate()]),
        approved_payload=written[AB.F_APPROVED_PAYLOAD],
        evidence_manifest_sha256=ev["manifest_sha256"])
    assert verified.evidence_manifest_sha256 == ev["manifest_sha256"]


def test_an_approval_cannot_be_issued_without_an_evidence_manifest():
    with pytest.raises(APPROVAL.ApprovalError) as e:
        APPROVAL.issue(key=SIGNING_KEY, airtable_record_id=RID, run_id="r",
                       candidate_payload="[]", approved_payload="[]",
                       approval_as_of=APPROVAL_AT.isoformat(), evidence_manifest_sha256="")
    assert "without an evidence manifest" in str(e.value)


# ======================================================================================================
# REPLAYABLE: the same function, the same bytes, the same verdict -- and tamper-evident
# ======================================================================================================

def test_REPLAY_READS_THE_EXACT_PERSISTED_EVIDENCE(tmp_path):
    led = ledger(tmp_path)
    _code, fake = go(tmp_path, led=led)
    result = json.loads(fake.written[RID][AB.F_PREFLIGHT_RESULT])
    approved = json.loads(fake.written[RID][AB.F_APPROVED_PAYLOAD])

    documents, entries = RP.load_evidence(fake.evidence_root, result)
    assert len(entries) == 1
    assert documents[0]["market_ticker"] == TICKER

    reports = RP.replay(approved, documents, ledger_root=led, root=ROOT)
    assert reports[0].overall == G.PASS
    assert reports[0].as_of == APPROVAL_AT.isoformat(), "the replay judges at the approval instant"
    assert reports[0].decision_quote["executable_price"] == pytest.approx(
        result["candidates"][0]["executable_price"])
    assert reports[0].depth["vwap"] == pytest.approx(result["candidates"][0]["full_position_vwap"])


def test_the_replay_cli_agrees_with_the_approval(tmp_path):
    led = ledger(tmp_path)
    _code, fake = go(tmp_path, led=led)
    res_path = tmp_path / "result.json"
    pay_path = tmp_path / "approved.json"
    res_path.write_text(fake.written[RID][AB.F_PREFLIGHT_RESULT])
    pay_path.write_text(fake.written[RID][AB.F_APPROVED_PAYLOAD])
    code = RP.main(["--result", str(res_path), "--approved-payload", str(pay_path),
                    "--evidence-root", fake.evidence_root, "--handicap-root", led])
    assert code == 0


def test_CHANGING_THE_EVIDENCE_AFTER_APPROVAL_IS_DETECTED(tmp_path):
    """The whole reason the evidence is hashed. A single altered digit fails the replay."""
    _code, fake = go(tmp_path)
    result = json.loads(fake.written[RID][AB.F_PREFLIGHT_RESULT])
    path = os.path.join(fake.evidence_root, result["evidence"]["documents"][0]["path"])

    doc = json.loads(open(path).read())
    doc["market"]["yes_ask"] = 0.10                     # a price nobody was ever quoted
    doc["quote_row"]["yes_ask_dollars"] = 0.10
    with open(path, "w") as f:
        f.write(LE.canonical_json(doc))

    with pytest.raises(LE.EvidenceError) as e:
        RP.load_evidence(fake.evidence_root, result)
    assert "has been altered since" in str(e.value)


def test_a_deleted_evidence_document_fails_the_replay_loudly(tmp_path):
    _code, fake = go(tmp_path)
    result = json.loads(fake.written[RID][AB.F_PREFLIGHT_RESULT])
    os.unlink(os.path.join(fake.evidence_root, result["evidence"]["documents"][0]["path"]))
    with pytest.raises(LE.EvidenceError) as e:
        RP.load_evidence(fake.evidence_root, result)
    assert "cannot be independently replayed" in str(e.value)


def test_substituting_a_different_document_for_the_recorded_one_is_detected(tmp_path):
    """Pointing the manifest at other, genuine-looking evidence does not help either."""
    _code, fake = go(tmp_path)
    result = json.loads(fake.written[RID][AB.F_PREFLIGHT_RESULT])
    entry = result["evidence"]["documents"][0]
    other = LE.canonical_json(collect_one(fresh_client(APPROVAL_AT, ask=0.20)))
    with open(os.path.join(fake.evidence_root, entry["path"]), "w") as f:
        f.write(other)
    with pytest.raises(LE.EvidenceError):
        RP.load_evidence(fake.evidence_root, result)


def test_editing_the_manifest_to_match_tampered_evidence_breaks_the_signature(tmp_path):
    """Airtable is writable by the requester; the signing key is not. This is why the manifest is signed."""
    _code, fake = go(tmp_path)
    written = fake.written[RID]
    body = json.loads(written[AB.F_PREFLIGHT_RESULT])
    forged = "f" * 64
    body["evidence"]["manifest_sha256"] = forged
    body["evidence_manifest_sha256"] = forged
    with pytest.raises(APPROVAL.ApprovalError) as e:
        APPROVAL.verify(body, key=SIGNING_KEY, airtable_record_id=RID, run_id="20260909T130000Z",
                        candidate_payload=json.dumps([candidate()]),
                        approved_payload=written[AB.F_APPROVED_PAYLOAD])
    assert "signature does not verify" in str(e.value)


def test_the_verifier_refuses_when_the_recomputed_manifest_disagrees(tmp_path):
    _code, fake = go(tmp_path)
    written = fake.written[RID]
    body = json.loads(written[AB.F_PREFLIGHT_RESULT])
    with pytest.raises(APPROVAL.ApprovalError) as e:
        APPROVAL.verify(body, key=SIGNING_KEY, airtable_record_id=RID, run_id="20260909T130000Z",
                        candidate_payload=json.dumps([candidate()]),
                        approved_payload=written[AB.F_APPROVED_PAYLOAD],
                        evidence_manifest_sha256="0" * 64)
    assert "evidence has changed since the approval" in str(e.value)


def test_the_replay_agrees_with_the_live_verdict_gate_for_gate(tmp_path):
    """Not "both blocked" -- the same gate, with the same status, for the same reason."""
    led = ledger(tmp_path)
    docs = [collect_one()]
    live = P.preflight(candidate(), market_data_root=None, ledger_root=led, root=ROOT,
                       approval_as_of=APPROVAL_AT, request_created_at=REQUEST_AT,
                       capture_index=LE.EvidenceQuoteIndex(docs), book_index=LE.EvidenceBookIndex(docs))
    stored = [LE.load_document(LE.canonical_json(d)) for d in docs]
    replayed = RP.replay([live.approved_record], stored, ledger_root=led, root=ROOT)[0]
    for name in RP.DETERMINISTIC_GATES:
        if name in live.gates and name in replayed.gates:
            assert live.gates[name]["status"] == replayed.gates[name].status, name
            assert live.gates[name]["reason"] == replayed.gates[name].reason, name


# ======================================================================================================
# The git-backed store, which is what production actually uses
# ======================================================================================================

def _git(args, cwd):
    return subprocess.run(["git", *args], cwd=cwd, text=True, capture_output=True, check=True)


@pytest.mark.skipif(shutil.which("git") is None, reason="git is not installed")
def test_the_git_store_commits_and_pushes_to_its_own_branch_and_nothing_else(tmp_path):
    remote = tmp_path / "remote.git"
    _git(["init", "--bare", "-b", "main", str(remote)], cwd=str(tmp_path))
    work = tmp_path / "work"
    work.mkdir()
    _git(["init", "-b", "main", "."], cwd=str(work))
    _git(["config", "user.email", "t@t"], cwd=str(work))
    _git(["config", "user.name", "t"], cwd=str(work))
    (work / "README.md").write_text("x")
    _git(["add", "-A"], cwd=str(work))
    _git(["commit", "-m", "init"], cwd=str(work))
    _git(["remote", "add", "origin", str(remote)], cwd=str(work))
    _git(["push", "-u", "origin", "main"], cwd=str(work))

    store = ES.GitBranchEvidenceStore(str(work), worktree=str(tmp_path / "wt"))
    doc = collect_one()
    text = LE.canonical_json(doc)
    rel = LE.evidence_relpath(season=2026, week=1, airtable_record_id=RID, ticker=TICKER,
                              retrieved_at=doc["market"]["retrieved_at"])
    out = ES.store_batch(store, [(rel, text, LE.sha256_text(text))], message="evidence")
    assert out["storage"] == "git" and len(out["commit"]) == 40
    assert out["entries"][0]["sha256"] == LE.sha256_text(text)

    # It is genuinely on the remote, on the evidence branch, and main is untouched.
    listed = subprocess.run(["git", "ls-tree", "-r", "--name-only", "preflight-evidence"],
                            cwd=str(remote), text=True, capture_output=True, check=True).stdout
    assert rel in listed
    main_listed = subprocess.run(["git", "ls-tree", "-r", "--name-only", "main"],
                                 cwd=str(remote), text=True, capture_output=True, check=True).stdout
    assert "preflight_evidence" not in main_listed, "main must never receive evidence"


def test_the_git_store_refuses_any_branch_but_its_own(tmp_path):
    for branch in ("main", "market-data", "handicap-data", "gh-pages"):
        with pytest.raises(ES.EvidenceStoreError) as e:
            ES.GitBranchEvidenceStore(str(tmp_path), branch=branch)
        assert "and nowhere else" in str(e.value)
    assert ES.EVIDENCE_BRANCH == "preflight-evidence"


# ======================================================================================================
# TEST_ONLY stays safe
# ======================================================================================================

def test_a_TEST_ONLY_probe_never_touches_the_venue_and_never_approves(tmp_path):
    probe = candidate(recommendation_id="rec_test000000000001", test_only=True,
                      market_ticker="KXNFLGAME-99DEC31TSTTST-TST")
    client = FakeKalshiClient(fail_market=True)     # any fetch would raise
    code, fake = go(tmp_path, cand=probe, client=client)
    assert code == 0
    assert client.calls == []
    assert fake.written[RID][AB.F_STATUS] == AB.STATUS_PREFLIGHT_BLOCKED
    body = json.loads(fake.written[RID][AB.F_PREFLIGHT_RESULT])
    assert body["candidates"][0]["may_be_shown_as_a_bet"] is False
    assert AB.F_APPROVED_PAYLOAD not in fake.written[RID]
    assert not _all_evidence(fake.evidence_root), "a probe publishes nothing to a permanent branch"


def test_a_real_candidate_beside_a_probe_still_gets_its_evidence(tmp_path):
    probe = candidate(recommendation_id="rec_test000000000001", test_only=True,
                      market_ticker="KXNFLGAME-99DEC31TSTTST-TST")
    client = fresh_client(APPROVAL_AT)
    code, fake = go(tmp_path, cand=[candidate(), probe], client=client)
    assert code == 0
    assert client.calls == [("market", TICKER), ("orderbook", TICKER, 10)], \
        "only the real candidate's contract is fetched"
    assert len(_all_evidence(fake.evidence_root)) == 1


# ======================================================================================================
# observability
# ======================================================================================================

def test_the_run_summary_reports_where_the_time_went(tmp_path):
    summary = tmp_path / "summary.md"
    _code, fake = go(tmp_path, summary_path=str(summary), trigger="issues")
    text = summary.read_text()
    for expected in ("trigger: `issues`", "requests answered", "load code + start python",
                     "obtain live market evidence", "persist evidence durably",
                     "load ledger (outstanding exposure)", "run gates",
                     "TOTAL request-to-verdict", "min to kickoff", "quote age", "book age"):
        assert expected in text, expected


def test_the_run_summary_never_leaks_the_bet(tmp_path):
    """The repository is public and so is this page."""
    summary = tmp_path / "summary.md"
    _code, _fake = go(tmp_path, summary_path=str(summary))
    text = summary.read_text().lower()
    disclaimer = "no ticker, price, stake or thesis appears on this page"
    assert disclaimer in text, "the page must say what it deliberately omits"
    body = text.replace(disclaimer, "")
    for forbidden in ("kxnfl", "thesis", "0.56", "bankroll", "stake", "probability"):
        assert forbidden not in body, f"the summary page mentions {forbidden!r}"


def test_request_to_verdict_is_measured_from_airtables_own_clock(tmp_path):
    summary = tmp_path / "summary.md"
    timer = W.Timer()
    _code, _fake = go(tmp_path, summary_path=str(summary), timer=timer)
    # The row is stamped at REQUEST_AT and answered at APPROVAL_AT, two minutes later.
    assert timer.spans["request_to_verdict"] == pytest.approx(120.0, abs=1.0)


# ======================================================================================================
# helpers
# ======================================================================================================

class FakeAirtable:
    def __init__(self, rows):
        self.rows, self.written, self.request_count = rows, {}, 0
        self.evidence_root = None

    def list_by_status(self, status, sport=AB.SPORT_NFL):
        self.request_count += 1
        return [r for r in self.rows if (r["fields"] or {}).get(AB.F_STATUS) == status]

    def write_fields(self, updates, **kw):
        self.request_count += 1
        for rid, fields in updates.items():
            self.written.setdefault(rid, {}).update(fields)


def row(cands):
    return {"id": RID, "createdTime": REQUEST_AT.isoformat(),
            "fields": {AB.F_SPORT: AB.SPORT_NFL, AB.F_STATUS: AB.STATUS_PREFLIGHT_REQUESTED,
                       AB.F_RUN_ID: "20260909T130000Z", AB.F_PAYLOAD: json.dumps(cands)}}


def go(tmp_path, *, cand=None, client=None, store=None, led=None, **kw):
    """The whole live leg against a fake venue and a real (directory) store."""
    cands = cand if isinstance(cand, list) else [cand or candidate()]
    fake = FakeAirtable([row(cands)])
    if store is None:
        store, root = evidence_dir(tmp_path)
    else:
        root = store.root
    fake.evidence_root = root
    code = W.run(fake, ledger_root=led or ledger(tmp_path), now=APPROVAL_AT, signing_key=SIGNING_KEY,
                 evidence_collector=W.LiveEvidenceCollector(client or fresh_client(APPROVAL_AT)),
                 evidence_store=store, **kw)
    return code, fake


def fly(tmp_path, *, cand=None, client=None, at=None):
    at = at or APPROVAL_AT
    docs = [LE.collect(client or fresh_client(at), TICKER, side="YES", airtable_record_id=RID,
                       run_id="r", evidence_run_id="e")]
    return P.preflight(cand or candidate(), market_data_root=None, ledger_root=ledger(tmp_path),
                       root=ROOT, approval_as_of=at, request_created_at=at - timedelta(minutes=2),
                       capture_index=LE.EvidenceQuoteIndex(docs), book_index=LE.EvidenceBookIndex(docs))


def _all_evidence(root):
    out = []
    for base, _dirs, files in os.walk(root or ""):
        for f in files:
            if f.endswith(".json"):
                out.append(os.path.relpath(os.path.join(base, f), root))
    return sorted(out)


# ======================================================================================================
# The full loop: approve from live evidence, then ARCHIVE by replaying that same evidence
# ======================================================================================================

# The request payload as it reaches the ARCHIVAL leg carries `decision: RECOMMENDED` -- the candidate has
# by then been approved and the owner is filing it. Preflight overrides the decision either way, so the same
# row serves both legs, which is what makes the round trip below a real one.
FILED = candidate(decision=S.RECOMMENDED)


def _ready_row(fake, rid=RID):
    """The approved row, moved to READY_FOR_SYNC exactly as the owner would move it.

    The `Payload` is the SAME string the preflight request carried -- not a re-serialisation -- because the
    approval signature covers its hash.
    """
    written = fake.written[rid]
    return {"id": rid, "createdTime": REQUEST_AT.isoformat(),
            "fields": {AB.F_SPORT: AB.SPORT_NFL, AB.F_STATUS: AB.STATUS_READY,
                       AB.F_RUN_ID: "20260909T130000Z",
                       AB.F_PAYLOAD: fake.rows[0]["fields"][AB.F_PAYLOAD],
                       AB.F_APPROVED_PAYLOAD: written[AB.F_APPROVED_PAYLOAD],
                       AB.F_PREFLIGHT_RESULT: written[AB.F_PREFLIGHT_RESULT]}}


def test_the_importer_archives_by_replaying_the_preflight_evidence(tmp_path):
    """The whole point: the importer does not TRUST the approval, it REPRODUCES it.

    Note what is NOT on disk anywhere in this test -- a capture stream. The importer's gate replay reads the
    evidence documents the approval names, which are the ones the decision was actually made on.
    """
    led = ledger(tmp_path)
    _code, fake = go(tmp_path, led=led, cand=FILED)
    approved = json.loads(fake.written[RID][AB.F_APPROVED_PAYLOAD])
    plan = AB.plan_run(_ready_row(fake), led, now=APPROVAL_AT + timedelta(hours=12),
                       gate_context=_import_ctx(led, approved),
                       signing_key=SIGNING_KEY, evidence_root=fake.evidence_root)
    assert plan.payload_source.startswith("approved payload")
    assert len(plan.to_write) == 1
    gate_record = plan.gate_records[0][1]
    assert gate_record["overall"] == G.PASS
    assert gate_record["gates"][G.G_PRE_KICKOFF]["status"] == G.PASS
    assert gate_record["gates"][G.G_QUOTE_FRESHNESS]["status"] == G.PASS
    assert gate_record["decision_as_of"] == APPROVAL_AT.isoformat(), \
        "twelve hours later, judged at the approval instant"


def test_the_importer_refuses_a_row_whose_evidence_was_altered_after_approval(tmp_path):
    led = ledger(tmp_path)
    _code, fake = go(tmp_path, led=led, cand=FILED)
    result = json.loads(fake.written[RID][AB.F_PREFLIGHT_RESULT])
    path = os.path.join(fake.evidence_root, result["evidence"]["documents"][0]["path"])
    doc = json.loads(open(path).read())
    doc["quote_row"]["yes_ask_dollars"] = 0.10
    with open(path, "w") as f:
        f.write(LE.canonical_json(doc))

    with pytest.raises(AB.BridgeError) as e:
        AB.plan_run(_ready_row(fake), led, now=APPROVAL_AT + timedelta(hours=12),
                    gate_context=_import_ctx(led), signing_key=SIGNING_KEY,
                    evidence_root=fake.evidence_root)
    assert "altered since" in str(e.value)


def test_the_importer_refuses_a_row_whose_evidence_has_vanished(tmp_path):
    led = ledger(tmp_path)
    _code, fake = go(tmp_path, led=led, cand=FILED)
    result = json.loads(fake.written[RID][AB.F_PREFLIGHT_RESULT])
    os.unlink(os.path.join(fake.evidence_root, result["evidence"]["documents"][0]["path"]))
    with pytest.raises(AB.BridgeError) as e:
        AB.plan_run(_ready_row(fake), led, now=APPROVAL_AT + timedelta(hours=12),
                    gate_context=_import_ctx(led), signing_key=SIGNING_KEY,
                    evidence_root=fake.evidence_root)
    assert "cannot be re-read" in str(e.value)


def test_a_row_with_no_evidence_root_configured_still_imports_from_the_capture_stream(tmp_path):
    """Legacy rows and un-configured runners are not broken by the rebuild; they just replay the old way."""
    led = ledger(tmp_path)
    _code, fake = go(tmp_path, led=led, cand=FILED)
    from test_preflight import market_data                       # noqa: PLC0415
    md = market_data(tmp_path, minutes_before=-1.0)              # a capture just before the approval
    ctx = P.build_context(md, root=ROOT,
                          risk_report=R.report_for_batch(
                              json.loads(fake.written[RID][AB.F_APPROVED_PAYLOAD]),
                              R.RiskPolicy.load(ROOT), led))
    ctx.ledger_root = led
    plan = AB.plan_run(_ready_row(fake), led, now=APPROVAL_AT + timedelta(hours=12),
                       gate_context=ctx, signing_key=SIGNING_KEY, evidence_root=None)
    assert len(plan.to_write) == 1


def _import_ctx(led, records=None):
    """The importer's gate context with NO capture stream at all -- evidence is the only market input."""
    import glob                                                   # noqa: PLC0415
    ctx = P.build_context(None, root=ROOT)
    ctx.ledger_root = led
    assert ctx.capture_index is None and ctx.book_index is None, \
        "this context has no capture stream, so only the preflight evidence can answer the market gates"
    assert not glob.glob(os.path.join(led, "data", "kalshi", "capture", "*"))
    if records:
        ctx.risk_report = R.report_for_batch(records, R.RiskPolicy.load(ROOT), led)
    return ctx
