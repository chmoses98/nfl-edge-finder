"""The Airtable -> handicap-data bridge, pinned at every point where it could lose or corrupt a decision.

The bridge is the only unattended writer this ledger has. Nobody reads its output before it lands, so every
guarantee it makes has to be enforced here rather than trusted: that a batch is atomic, that a record is
never overwritten, that SYNCED is only ever claimed after a push, that a dropped socket is not mistaken for
bad data, and that the token never reaches a log.

Airtable is mocked at the urlopen boundary, so the client's own retry, batching, filtering and error
classification are exercised rather than stubbed past.
"""
import io
import json
import os
import sys
import urllib.error
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.execution import fees as FEES          # noqa: E402
from nfl_edge.execution import quotes as Q            # noqa: E402
from nfl_edge.handicap import airtable_bridge as AB   # noqa: E402
from nfl_edge.handicap import gates as G              # noqa: E402
from nfl_edge.handicap import risk as RISK            # noqa: E402
from nfl_edge.handicap import schema as S             # noqa: E402
from nfl_edge.handicap import store                   # noqa: E402
import sync_airtable                                  # noqa: E402

TOKEN = "patFAKE0000000000.deadbeefdeadbeefdeadbeefdeadbeefdeadbeefdeadbeef"
CREATED = "2026-09-05T05:30:00.000Z"
AIRTABLE_CREATED = datetime(2026, 9, 5, 5, 30, tzinfo=timezone.utc)
NOW = AIRTABLE_CREATED + timedelta(minutes=2)
RUN_ID = "20260905T052459Z"


# ---- fixtures --------------------------------------------------------------------------------------

def rec(rid="rec_bridge0000000000001", **kw):
    d = dict(
        recommendation_id=rid, schema_version=S.HANDICAP_SCHEMA_VERSION,
        created_at="2026-09-05T05:25:01+00:00", handicap_run_id=RUN_ID, packet_sha="9328642968522db8ddcd",
        season=2026, week=1, game_id="2026_01_NE_SEA", kickoff_utc="2026-09-10T00:20:00+00:00",
        market_ticker="KXNFLGAME-26SEP09NESEA-SEA", market_family="GAME_WINNER", side="YES",
        yes_bid=0.60, yes_ask=0.62, no_bid=0.38, no_ask=0.40, mid=0.61,
        market_timestamp="2026-09-05T05:24:59+00:00", minutes_to_kickoff=6890.0,
        support_state=S.SUPPORT_SUPPORTED, model_version="shadow-0.4.0", artifact_hash="deadbeefcafe",
        model_probability=0.64,
        decision=S.RECOMMENDED, grade="B+", bet_up_to_probability=0.65,
        proposed_stake=25, recommended_stake=25,
        probability_low=0.61, probability_mid=0.66, probability_high=0.71,
        primary_thesis="TEST_ONLY: role expansion not yet priced.",
        key_supporting_factors=["TEST_ONLY: snap share up"],
        counterarguments=["TEST_ONLY: the market may already know"],
        uncertainties=["TEST_ONLY: game script"],
        source_freshness={"shadow_snapshot": "2026-09-05T05:00:00+00:00"},
        reasoning_tags=["ROLE_EXPANSION"], test_only=True,
    )
    d.update(kw)
    return d


def a_pass(rid="rec_bridge0000000000002", **kw):
    d = dict(decision=S.PASS, grade="PASS", bet_up_to_probability=None, recommended_stake=None,
             proposed_stake=None,
             primary_thesis="TEST_ONLY: price already reflects the news.",
             reasoning_tags=["MARKET_ALREADY_PRICED"])
    d.update(kw)
    return rec(rid, **d)


def row(records, *, rid="recE2E00000000001", run_id=RUN_ID, created=CREATED, payload=None):
    body = payload if payload is not None else json.dumps(records)
    return {"id": rid, "createdTime": created,
            "fields": {AB.F_RUN_ID: run_id, AB.F_SPORT: "NFL", AB.F_STATUS: AB.STATUS_READY,
                       AB.F_PAYLOAD: body}}


@pytest.fixture
def ledger(tmp_path):
    """A handicap-data checkout: a real git repo, because commit/push behaviour is part of what is tested."""
    root = tmp_path / "ledger"
    (root / "data" / "recommendations").mkdir(parents=True)
    os.system(f"cd {root} && git init -q && git config user.email t@t && git config user.name t "
              f"&& git add -A && git commit -q --allow-empty -m init")
    return str(root)


class FakeAirtable:
    """urlopen stand-in. Records requests so API footprint can be asserted, not assumed."""

    def __init__(self, list_pages=None, list_error=None, patch_error=None):
        self.list_pages = list_pages if list_pages is not None else [{"records": []}]
        # Errors are FACTORIES, not instances: an HTTPError's body is a one-shot stream, so a retry that
        # re-raised the same object would see an empty body and silently weaken every scrubbing assertion.
        self.list_error, self.patch_error = list_error, patch_error
        self.requests, self.patches = [], []
        self._page = 0
        self._once = False

    @staticmethod
    def _raise(factory):
        raise factory() if callable(factory) else factory

    def __call__(self, req, timeout=None):
        self.requests.append((req.get_method(), req.full_url,
                              req.headers.get("Authorization") or req.headers.get("Authorization".title())))
        if req.get_method() == "GET":
            if self.list_error:
                err, self.list_error = self.list_error, (None if self._once else self.list_error)
                self._raise(err)
            page = self.list_pages[min(self._page, len(self.list_pages) - 1)]
            self._page += 1
            return _resp(page)
        body = json.loads(req.data)
        self.patches.append(body["records"])
        if self.patch_error:
            self._raise(self.patch_error)
        return _resp({"records": body["records"]})

    @property
    def status_updates(self):
        return {r["id"]: r["fields"][AB.F_STATUS] for batch in self.patches for r in batch}


def _resp(payload):
    class R(io.BytesIO):
        def __enter__(self):
            return self

        def __exit__(self, *a):
            return False
    return R(json.dumps(payload).encode())


def http_error(code, body=b"{}", headers=None):
    """A factory, so every retry gets a fresh, readable response body."""
    return lambda: urllib.error.HTTPError("https://api.airtable.com", code, "err", headers or {},
                                          io.BytesIO(body))


def client(fake, **kw):
    return AB.AirtableClient(TOKEN, opener=fake, sleep=lambda *_: None, **kw)


def run_sync(fake, ledger, *, pusher=None, **kw):
    """sync() with a push that succeeds by default and records that it was called."""
    calls = []

    def default_pusher(root, message):
        calls.append(message)
    c = client(fake)
    code = sync_airtable.sync(c, ledger, now=NOW, pusher=pusher or default_pusher, **kw)
    return code, calls, c


# ---- gate context ----------------------------------------------------------------------------------

class _FreshIndex:
    """A CaptureIndex stand-in that confirms one ticker, right now, at a stated ask.

    Real capture files are not needed to test the bridge's ATOMICITY; they are needed to test the gate
    itself, which tests/test_decision_quotes.py does against real capture layouts. Here the point is that a
    real recommendation cannot land without a gate context at all.
    """

    def __init__(self, ask=0.62, confirmed=None, ticker=None):
        self.ask, self.confirmed, self.ticker = ask, confirmed or NOW, ticker

    def confirmation(self, ticker, series_ticker):
        return self.confirmed, Q.CONFIRM_TICKER, "run", None

    def last_quote_row(self, ticker, not_after=None):
        return {"ticker": ticker, "observed_at": self.confirmed.isoformat(), "status": "active",
                "yes_bid": 0.60, "yes_ask": self.ask, "no_bid": 1 - self.ask, "no_ask": 0.40}


def gate_ctx(ask=0.62, **kw):
    ctx = G.GateContext(capture_index=_FreshIndex(ask=ask), fee_schedule=FEES.load_fee_schedule(ROOT),
                        now=NOW, **kw)
    ctx.risk_policy = RISK.RiskPolicy.load(ROOT)
    return ctx


def ledger_recs(ledger):
    return sorted(os.path.basename(p) for p in
                  __import__("glob").glob(os.path.join(ledger, "data", "recommendations", "*", "*", "*.json")))


# ---- 1. nothing pending ----------------------------------------------------------------------------

def test_no_pending_rows_is_a_clean_no_op(ledger):
    fake = FakeAirtable([{"records": []}])
    code, pushes, c = run_sync(fake, ledger)
    assert code == 0
    assert pushes == [], "an idle poll must not commit"
    assert ledger_recs(ledger) == []
    assert c.request_count == 1, "an idle poll must cost exactly one Airtable request"
    assert not fake.patches, "an idle poll must not write any status"


def test_idle_poll_filters_server_side_for_nfl_and_ready(ledger):
    fake = FakeAirtable([{"records": []}])
    run_sync(fake, ledger)
    url = fake.requests[0][1]
    assert "READY_FOR_SYNC" in url and "NFL" in url
    # TEST_ONLY is excluded by the filter itself, so the connectivity probe never reaches the importer.
    assert AB.STATUS_TEST_ONLY not in url.replace("READY_FOR_SYNC", "")


# ---- 2-5. valid payloads ---------------------------------------------------------------------------

def test_single_valid_recommendation_is_imported(ledger):
    fake = FakeAirtable([{"records": [row([rec()])]}])
    code, pushes, _ = run_sync(fake, ledger)
    assert code == 0
    assert ledger_recs(ledger) == ["rec_bridge0000000000001.json"]
    assert len(pushes) == 1
    assert fake.status_updates == {"recE2E00000000001": AB.STATUS_SYNCED}


def test_a_bare_object_payload_is_accepted_as_a_one_record_batch(ledger):
    fake = FakeAirtable([{"records": [row(None, payload=json.dumps(rec()))]}])
    code, _, _ = run_sync(fake, ledger)
    assert code == 0 and ledger_recs(ledger) == ["rec_bridge0000000000001.json"]


def test_multi_recommendation_batch_lands_as_one_file_each(ledger):
    batch = [rec("rec_b1"), rec("rec_b2"), rec("rec_b3")]
    fake = FakeAirtable([{"records": [row(batch)]}])
    code, pushes, _ = run_sync(fake, ledger)
    assert code == 0
    assert ledger_recs(ledger) == ["rec_b1.json", "rec_b2.json", "rec_b3.json"]
    assert len(pushes) == 1, "one handicap run is one commit, not one commit per record"


def test_mixed_recommended_and_pass_batch(ledger):
    batch = [rec("rec_r1"), a_pass("rec_p1"), a_pass("rec_p2", decision=S.WATCHLIST, grade=None),
             a_pass("rec_p3", decision=S.RESEARCH_ALERT, grade=None)]
    fake = FakeAirtable([{"records": [row(batch)]}])
    code, pushes, _ = run_sync(fake, ledger)
    assert code == 0
    assert len(ledger_recs(ledger)) == 4
    msg = pushes[0]
    assert "recommended" in msg and "pass" in msg


def test_test_only_payload_is_importable_and_stays_test_only(ledger):
    fake = FakeAirtable([{"records": [row([rec(test_only=True)])]}])
    code, _, _ = run_sync(fake, ledger)
    assert code == 0
    written = json.load(open(os.path.join(ledger, "data", "recommendations", "2026", "week_01",
                                          "rec_bridge0000000000001.json")))
    assert written["test_only"] is True


def test_scorecard_readers_still_exclude_imported_test_only_records(ledger):
    """The whole point of a TEST_ONLY E2E: proving the path without contaminating performance history."""
    fake = FakeAirtable([{"records": [row([rec(test_only=True), _real(rec, rid="rec_real")])]}])
    run_sync(fake, ledger, gate_context=gate_ctx())
    visible = store.read_kind(ledger, "recommendations")
    assert [r["recommendation_id"] for r in visible] == ["rec_real"]
    assert len(store.read_kind(ledger, "recommendations", include_test=True)) == 2


# ---- 6-10. permanent data problems -> ERROR, nothing written ----------------------------------------

def _expect_error(ledger, rows, *, contains=None):
    fake = FakeAirtable([{"records": rows}])
    code, pushes, _ = run_sync(fake, ledger)
    assert code == 1, "a permanent data problem must be reported as a failure"
    assert ledger_recs(ledger) == [], "nothing may be written for a rejected batch"
    assert pushes == [], "a rejected batch must not produce a commit"
    assert set(fake.status_updates.values()) == {AB.STATUS_ERROR}
    return fake


def test_malformed_json_is_an_error_and_writes_nothing(ledger):
    _expect_error(ledger, [row(None, payload="{not json")])


def test_empty_payload_is_an_error(ledger):
    _expect_error(ledger, [row(None, payload="   ")])


def test_schema_invalid_recommendation_is_an_error(ledger):
    # RECOMMENDED with no price ceiling: the existing schema rejects it, and the bridge must not soften that.
    _expect_error(ledger, [row([rec(bet_up_to_probability=None)])])


def test_inside_out_probability_band_is_an_error(ledger):
    _expect_error(ledger, [row([rec(probability_low=0.8, probability_high=0.3)])])


def test_non_whole_dollar_stake_is_an_error(ledger):
    _expect_error(ledger, [row([rec(recommended_stake=25.5)])])


def test_one_invalid_member_rejects_the_entire_batch(ledger):
    """Atomicity. Seven good decisions and one bad one import as zero decisions, not seven."""
    batch = [rec(f"rec_ok{i}") for i in range(7)] + [rec("rec_bad", decision="MAYBE")]
    _expect_error(ledger, [row(batch)])


def test_duplicate_recommendation_ids_within_a_batch_are_rejected(ledger):
    _expect_error(ledger, [row([rec("rec_same"), rec("rec_same", grade="A")])])


def test_inconsistent_handicap_run_id_is_rejected(ledger):
    _expect_error(ledger, [row([rec(), rec("rec_other", handicap_run_id="20260101T000000Z")])])


def test_payload_run_id_must_match_the_airtable_row(ledger):
    """Provenance: a ledger record has to be traceable to the row that carried it."""
    _expect_error(ledger, [row([rec()], run_id="some_other_run")])


def test_batch_spanning_two_slates_is_rejected(ledger):
    _expect_error(ledger, [row([rec(), rec("rec_wk2", week=2)])])


def test_missing_season_or_week_is_rejected(ledger):
    _expect_error(ledger, [row([rec(season=None)])])
    _expect_error(ledger, [row([rec(week=None)])])


def test_an_evaluation_or_execution_payload_is_refused(ledger):
    """Only recommendation batches ride this bridge; evaluations are derived, never transported."""
    _expect_error(ledger, [row([dict(rec(), evaluation_id="evl_x")])])
    _expect_error(ledger, [row([dict(rec(), execution_id="exe_x")])])


def test_unsafe_recommendation_id_is_refused(ledger):
    _expect_error(ledger, [row([rec("../../../../etc/passwd")])])


def test_a_row_with_no_run_id_is_refused(ledger):
    _expect_error(ledger, [row([rec()], run_id="")])


# ---- timestamp / anti-backfill integrity -----------------------------------------------------------

def test_backfilled_recommendation_is_refused(ledger):
    """A row created today carrying a decision claiming to be from last month is not prospective evidence."""
    _expect_error(ledger, [row([rec(created_at="2026-08-01T12:00:00+00:00")])])


def test_recommendation_created_after_its_own_airtable_row_is_refused(ledger):
    _expect_error(ledger, [row([rec(created_at="2026-09-05T09:00:00+00:00")])])


def test_small_clock_skew_is_tolerated(ledger):
    """ChatGPT writes the payload, then submits the row: created_at slightly after is ordinary skew."""
    fake = FakeAirtable([{"records": [row([rec(created_at="2026-09-05T05:32:00+00:00")])]}])
    code, _, _ = run_sync(fake, ledger)
    assert code == 0


def test_post_kickoff_recommendation_is_refused(ledger):
    _expect_error(ledger, [row([rec(created_at="2026-09-05T05:25:00+00:00",
                                    kickoff_utc="2026-09-05T00:00:00+00:00")])])


def test_naive_timestamp_is_refused(ledger):
    _expect_error(ledger, [row([rec(created_at="2026-09-05T05:25:01")])])


# ---- 8. independence between rows ------------------------------------------------------------------

def test_one_corrupt_run_does_not_block_the_others(ledger):
    """Run A valid, Run B corrupt, Run C valid: A and C land, B goes ERROR."""
    rows = [
        row([rec("rec_a1")], rid="recA"),
        row(None, rid="recB", payload="{broken"),
        row([rec("rec_c1", handicap_run_id="RUNC")], rid="recC", run_id="RUNC"),
    ]
    fake = FakeAirtable([{"records": rows}])
    code, pushes, _ = run_sync(fake, ledger)
    assert code == 1
    assert ledger_recs(ledger) == ["rec_a1.json", "rec_c1.json"]
    assert len(pushes) == 1, "the two good runs share one commit"
    assert fake.status_updates == {"recA": AB.STATUS_SYNCED, "recB": AB.STATUS_ERROR,
                                   "recC": AB.STATUS_SYNCED}


# ---- 11-12. idempotency and conflict ---------------------------------------------------------------

def test_identical_existing_record_is_idempotent_and_needs_no_commit(ledger):
    """The heal path: a previous run pushed but never got to update the status."""
    fake1 = FakeAirtable([{"records": [row([rec()])]}])
    run_sync(fake1, ledger)

    fake2 = FakeAirtable([{"records": [row([rec()])]}])
    code, pushes, _ = run_sync(fake2, ledger)
    assert code == 0
    assert pushes == [], "re-importing an identical batch must not create an empty commit"
    assert fake2.status_updates == {"recE2E00000000001": AB.STATUS_SYNCED}
    assert ledger_recs(ledger) == ["rec_bridge0000000000001.json"]


def test_conflicting_existing_record_is_a_hard_failure_and_never_overwrites(ledger):
    fake1 = FakeAirtable([{"records": [row([rec()])]}])
    run_sync(fake1, ledger)
    path = os.path.join(ledger, "data", "recommendations", "2026", "week_01",
                        "rec_bridge0000000000001.json")
    before = open(path).read()

    # Same id, different opinion, submitted under a new Airtable row.
    fake2 = FakeAirtable([{"records": [row([rec(grade="A+", bet_up_to_probability=0.80)],
                                           rid="recCONFLICT")]}])
    code, pushes, _ = run_sync(fake2, ledger)
    assert code == 1
    assert open(path).read() == before, "the original record must survive byte for byte"
    assert pushes == []
    assert fake2.status_updates == {"recCONFLICT": AB.STATUS_ERROR}


def test_amendment_is_how_a_changed_mind_is_recorded(ledger):
    """Immutability does not block revision: a NEW id carrying `amends` is accepted alongside the original."""
    run_sync(FakeAirtable([{"records": [row([rec("rec_v1")])]}]), ledger)
    amended = rec("rec_v2", grade="A", amends="rec_v1", handicap_run_id="RUN2")
    code, _, _ = run_sync(FakeAirtable([{"records": [row([amended], rid="recAMEND", run_id="RUN2")]}]), ledger)
    assert code == 0
    assert ledger_recs(ledger) == ["rec_v1.json", "rec_v2.json"]
    live = store.latest_amendment_chain(store.read_kind(ledger, "recommendations", include_test=True))
    assert [r["recommendation_id"] for r in live] == ["rec_v2"]


def test_editing_a_synced_row_payload_is_detected_as_a_conflict(ledger):
    """Run ID, Sport and Payload are source-immutable once READY_FOR_SYNC. The receipt hash proves it."""
    run_sync(FakeAirtable([{"records": [row([rec("rec_x1")])]}]), ledger)
    # Same Airtable record id, different payload -- i.e. somebody edited the row rather than adding a new one.
    edited = row([rec("rec_x2")], rid="recE2E00000000001")
    code, pushes, _ = run_sync(FakeAirtable([{"records": [edited]}]), ledger)
    assert code == 1
    assert ledger_recs(ledger) == ["rec_x1.json"], "the edited payload must not be imported"
    assert pushes == []


# ---- 13-16. transient failures never become permanent -----------------------------------------------

def test_airtable_read_failure_leaves_rows_ready_for_sync(ledger):
    fake = FakeAirtable(list_error=http_error(503))
    code, pushes, _ = run_sync(fake, ledger)
    assert code == 3, "a transient failure is not an ERROR condition"
    assert pushes == []
    assert not fake.patches, "no status may be changed when Airtable could not even be read"


def test_rate_limit_is_retried_then_reported_transient(ledger):
    fake = FakeAirtable(list_error=http_error(429, headers={"Retry-After": "1"}))
    c = client(fake, max_attempts=3)
    with pytest.raises(AB.TransientError):
        c.list_ready()
    assert c.request_count == 3, "429 must be retried, bounded"


def test_server_error_recovers_when_a_retry_succeeds(ledger):
    fake = FakeAirtable([{"records": [row([rec()])]}], list_error=http_error(500))
    fake._once = True
    code, _, c = run_sync(fake, ledger)
    assert code == 0 and c.request_count >= 2


def test_a_rejected_token_is_transient_not_an_error(ledger):
    """A misconfigured secret must never mark a real recommendation permanently ERROR."""
    fake = FakeAirtable(list_error=http_error(403, b'{"error":"NOT_AUTHORIZED"}'))
    code, _, _ = run_sync(fake, ledger)
    assert code == 3
    assert not fake.patches


def test_push_failure_must_not_mark_synced(ledger):
    def failing_push(root, message):
        raise AB.TransientError("remote hung up")
    fake = FakeAirtable([{"records": [row([rec()])]}])
    code, _, _ = run_sync(fake, ledger, pusher=failing_push)
    assert code == 3
    assert AB.STATUS_SYNCED not in fake.status_updates.values(), \
        "SYNCED asserts durability on the remote; a failed push has not earned it"
    assert not fake.patches


def test_push_precedes_the_status_update(ledger):
    """Ordering, asserted directly rather than inferred."""
    order = []
    fake = FakeAirtable([{"records": [row([rec()])]}])
    real_patch = fake.__call__

    def tracking(req, timeout=None):
        if req.get_method() == "PATCH":
            order.append("status")
        return real_patch(req, timeout=timeout)

    def push(root, message):
        order.append("push")
    c = AB.AirtableClient(TOKEN, opener=tracking, sleep=lambda *_: None)
    assert sync_airtable.sync(c, ledger, now=NOW, pusher=push) == 0
    assert order == ["push", "status"]


def test_status_update_failure_after_a_good_push_heals_on_the_next_run(ledger):
    """The exact split-brain the design exists for: ledger durable, Airtable still says READY_FOR_SYNC."""
    fake1 = FakeAirtable([{"records": [row([rec()])]}], patch_error=http_error(503))
    code, pushes, _ = run_sync(fake1, ledger)
    assert code == 3 and len(pushes) == 1, "the push happened; only the status update failed"
    assert ledger_recs(ledger) == ["rec_bridge0000000000001.json"]

    # Next scheduled run: the row is still READY_FOR_SYNC and is offered again.
    fake2 = FakeAirtable([{"records": [row([rec()])]}])
    code, pushes, _ = run_sync(fake2, ledger)
    assert code == 0, "the identical record must be recognised, not treated as an overwrite"
    assert pushes == [], "healing must not manufacture a commit"
    assert fake2.status_updates == {"recE2E00000000001": AB.STATUS_SYNCED}


# ---- 17. the connectivity probe -------------------------------------------------------------------

def test_the_chatgpt_connectivity_probe_is_never_imported(ledger):
    """`test_nfl_chatgpt_write_001` proved ChatGPT can write to Airtable. Its payload is not a recommendation.

    It carries Status=TEST_ONLY, so the server-side filter excludes it and the importer never sees it. If it
    ever were offered, its payload would be refused rather than half-imported.
    """
    probe = {"id": "recfB9h7TJeNRk2EF", "createdTime": CREATED,
             "fields": {AB.F_RUN_ID: "test_nfl_chatgpt_write_001", AB.F_SPORT: "NFL",
                        AB.F_STATUS: AB.STATUS_TEST_ONLY,
                        AB.F_PAYLOAD: "connectivity probe only - not a recommendation"}}
    # Normal polling: the filter is the exclusion, so an empty result is what the importer actually sees.
    fake = FakeAirtable([{"records": []}])
    code, pushes, _ = run_sync(fake, ledger)
    assert code == 0 and pushes == [] and ledger_recs(ledger) == []

    # And defence in depth if it were ever flipped to READY_FOR_SYNC by hand.
    with pytest.raises(AB.BridgeError):
        AB.plan_run(dict(probe, fields=dict(probe["fields"], **{AB.F_STATUS: AB.STATUS_READY})),
                    ledger, now=NOW)


# ---- 18. the token never escapes -------------------------------------------------------------------

def test_the_token_never_appears_in_logs_or_errors(ledger, capsys):
    body = json.dumps({"error": {"message": f"bad token {TOKEN}"}}).encode()
    fake = FakeAirtable([{"records": [row([rec()])]}], patch_error=http_error(500, body))
    code, _, _ = run_sync(fake, ledger)
    assert code == 3
    out = capsys.readouterr()
    assert TOKEN not in out.out and TOKEN not in out.err
    assert TOKEN[:12] not in out.out


def test_the_token_is_never_placed_on_a_command_line():
    """argv is world-readable on a shared runner; the token travels in the environment only."""
    src = open(os.path.join(ROOT, "scripts", "handicap", "sync_airtable.py")).read()
    assert 'os.environ.get("AIRTABLE_TOKEN"' in src
    assert "--token" not in src, "a --token flag would put the secret in argv and in shell history"


def test_transient_errors_from_the_client_are_scrubbed():
    fake = FakeAirtable(list_error=http_error(500, f"leaked {TOKEN}".encode()))
    c = client(fake, max_attempts=2)
    with pytest.raises(AB.TransientError) as e:
        c.list_ready()
    assert TOKEN not in str(e.value) and "***" in str(e.value)


# ---- 19-21. workflow shape and commit behaviour -----------------------------------------------------

WORKFLOW = os.path.join(ROOT, ".github", "workflows", "sync-handicap-airtable.yml")


def _workflow():
    import yaml
    with open(WORKFLOW) as f:
        return yaml.safe_load(f)


def test_workflow_exists_and_parses():
    doc = _workflow()
    assert "sync" in doc["jobs"]


def test_workflow_declares_concurrency_without_cancelling():
    doc = _workflow()
    assert doc["concurrency"]["group"]
    assert doc["concurrency"]["cancel-in-progress"] is False, \
        "cancelling mid-push is the one moment worth not being in"


def test_workflow_permissions_are_contents_write_only():
    doc = _workflow()
    assert doc["permissions"] == {"contents": "write"}


def test_workflow_polls_twice_daily_in_season_and_supports_manual_dispatch():
    """Cadence is an API-budget decision, so it is pinned rather than left to drift.

    The bridge archives already-made decisions and the prospective timestamp is Airtable's server-side
    createdTime, so ingestion latency is free. Airtable's free tier meters requests per month and is shared
    with ChatGPT's own writes, so polling faster spends a scarce resource to buy latency nobody reads.
    """
    doc = _workflow()
    on = doc.get(True, doc.get("on"))
    cron = on["schedule"][0]["cron"]
    minute, hour, _dom, month, _dow = cron.split()
    assert hour == "*/12" and minute.isdigit(), f"expected 12-hourly polling, got {cron!r}"
    assert month == "9-12,1-2", f"expected a September-February window, got {month!r}"
    assert "workflow_dispatch" in on, "manual immediate ingestion must stay available"


def test_idle_polling_stays_inside_a_modest_monthly_api_budget():
    """Derived from the cron rather than asserted in prose, so a cadence change cannot silently blow the budget."""
    on = _workflow().get(True, _workflow().get("on"))
    hour = on["schedule"][0]["cron"].split()[1]
    per_day = 24 // int(hour.lstrip("*/")) if hour.startswith("*/") else 24
    idle_per_month = per_day * 30          # one Airtable request per idle poll, asserted elsewhere
    assert idle_per_month <= 100, (
        f"{idle_per_month} idle Airtable reads/month leaves too little headroom for ChatGPT's writes, "
        "status updates, retries and E2E testing on the free tier")


def test_workflow_checks_out_code_ledger_and_market_data_separately():
    """Three checkouts, one writable.

    `market-data` is now checked out deliberately: the decision-time price gate resolves the freshest
    CONFIRMED executable quote from the capture stream, and without it every real recommendation would fail
    the gate for a reason that is really a missing checkout. It is READ-ONLY here -- the next test pins that.
    """
    doc = _workflow()
    steps = doc["jobs"]["sync"]["steps"]
    checkouts = [s for s in steps if str(s.get("uses", "")).startswith("actions/checkout")]
    paths = {s["with"]["path"] for s in checkouts}
    assert paths == {"code", "ledger", "market-data"}, "code, ledger and market-data must be separate"
    ledger_step = next(s for s in checkouts if s["with"]["path"] == "ledger")
    assert ledger_step["with"]["ref"] == store.BRANCH


def test_the_workflow_never_writes_to_the_collector_branch():
    """Reading the capture stream is required. Writing to it is not, and never becomes so by accident.

    A high-frequency collector branch and a human-paced decision log must not share a writer: a commit from
    this workflow landing on `market-data` would fight the conductor and blur when a decision was recorded
    against when a price was.
    """
    steps = _workflow()["jobs"]["sync"]["steps"]
    md = next(s for s in steps
              if str(s.get("uses", "")).startswith("actions/checkout")
              and s["with"]["path"] == "market-data")
    assert md["with"]["ref"] == "market-data"
    assert md["with"].get("fetch-depth") == 1, \
        "a shallow checkout cannot rebase-and-push; depth 1 is itself part of the read-only guarantee"

    for step in steps:
        assert step.get("working-directory") != "market-data", \
            f"step {step.get('name')!r} runs inside the collector checkout"
        run = step.get("run") or ""
        for verb in ("git -C ../market-data", "git push", "git commit"):
            if verb in run:
                assert "market-data" not in run, \
                    f"step {step.get('name')!r} appears to write to the collector branch: {run[:120]}"


def test_workflow_sets_a_git_identity_before_the_sync_step():
    steps = _workflow()["jobs"]["sync"]["steps"]
    identity = next(i for i, s in enumerate(steps) if "git config user.name" in (s.get("run") or ""))
    sync_at = next(i for i, s in enumerate(steps) if "sync_airtable.py" in (s.get("run") or ""))
    assert identity < sync_at, "committing without an identity fails with 'Author identity unknown'"


def test_workflow_passes_the_token_only_through_env():
    src = open(WORKFLOW).read()
    assert "secrets.AIRTABLE_TOKEN" in src
    for line in src.splitlines():
        if "secrets.AIRTABLE_TOKEN" in line:
            assert "AIRTABLE_TOKEN:" in line, f"token used outside an env mapping: {line.strip()!r}"


def test_no_empty_commit_when_nothing_changed(ledger):
    """Asserted against real git: `commit_and_push` on an unchanged tree must create no commit."""
    before = os.popen(f"cd {ledger} && git rev-list --count HEAD").read().strip()
    sync_airtable.commit_and_push(ledger, "should not happen", sleep=lambda *_: None)
    after = os.popen(f"cd {ledger} && git rev-list --count HEAD").read().strip()
    assert before == after, "an empty commit claims work that did not happen"


def test_commit_and_push_never_force_pushes():
    src = open(os.path.join(ROOT, "scripts", "handicap", "sync_airtable.py")).read()
    assert "--force" not in src and "-f\"" not in src, \
        "handicap-data's audit value is that nothing on it is ever rewritten"


# ---- API budget ------------------------------------------------------------------------------------

def test_a_successful_sync_costs_one_list_plus_one_batched_patch(ledger):
    rows = [row([rec(f"rec_n{i}", handicap_run_id=f"RUN{i}")], rid=f"recRow{i}", run_id=f"RUN{i}")
            for i in range(8)]
    fake = FakeAirtable([{"records": rows}])
    code, _, c = run_sync(fake, ledger)
    assert code == 0
    assert c.request_count == 2, f"expected 1 list + 1 batched patch, got {c.request_count}"
    assert len(fake.patches) == 1 and len(fake.patches[0]) == 8


def test_status_updates_are_chunked_at_airtables_limit_of_ten(ledger):
    fake = FakeAirtable()
    c = client(fake)
    c.set_status({f"rec{i}": AB.STATUS_SYNCED for i in range(23)})
    assert [len(b) for b in fake.patches] == [10, 10, 3]


def test_pagination_only_costs_extra_when_airtable_actually_paginates(ledger):
    fake = FakeAirtable([{"records": [row([rec("rec_p1")], rid="recP1")], "offset": "itr123"},
                         {"records": [row([rec("rec_p2", handicap_run_id="R2")], rid="recP2",
                                          run_id="R2")]}])
    code, _, c = run_sync(fake, ledger)
    assert code == 0
    assert sorted(ledger_recs(ledger)) == ["rec_p1.json", "rec_p2.json"]
    assert c.request_count == 3, "two list pages plus one batched patch"


# ---- receipts / provenance --------------------------------------------------------------------------

def test_a_receipt_records_where_the_batch_came_from(ledger):
    fake = FakeAirtable([{"records": [row([rec(), a_pass()])]}])
    run_sync(fake, ledger)
    path = os.path.join(ledger, "data", "import_receipts", "2026", "week_01", "recE2E00000000001.json")
    r = json.load(open(path))
    assert r["airtable_base_id"] == AB.BASE_ID
    assert r["airtable_table_id"] == AB.TABLE_ID
    assert r["airtable_record_id"] == "recE2E00000000001"
    assert r["airtable_created_time"] == CREATED
    assert r["run_id"] == RUN_ID
    assert len(r["payload_sha256"]) == 64
    assert r["record_count"] == 2 and r["imported_at"]
    assert r["recommendation_ids"] == ["rec_bridge0000000000001", "rec_bridge0000000000002"]


def test_a_receipt_never_stands_in_for_a_recommendation(ledger):
    """Receipts document transport. They must not appear anywhere a decision is counted."""
    run_sync(FakeAirtable([{"records": [row([_real(rec)])]}]), ledger,
             gate_context=gate_ctx())
    recs = store.read_kind(ledger, "recommendations")
    assert len(recs) == 1
    assert all("payload_sha256" not in r for r in recs)


def _real(factory, **kw):
    """A non-test_only record, sized so the pilot risk policy approves it as proposed.

    The policy caps a B+ at 1.5 units and a unit is 0.5% of bankroll, so $10 on a $2,000 bankroll is exactly
    at the cap and passes uncapped. Choosing a size the policy would trim would make every test that uses
    this fixture also a test of the risk gate.
    """
    return factory(test_only=False, bankroll_snapshot=2000.0, proposed_stake=10, recommended_stake=10, **kw)


def test_a_real_recommendation_needs_a_gate_context(ledger):
    """The unattended writer must never materialise a real bet without checking the world.

    A missing gate context is a misconfiguration, and the fail-closed answer to a misconfiguration is to
    refuse the batch -- not to write the bet and hope somebody notices the missing gate record later.
    """
    code, _calls, _c = run_sync(FakeAirtable([{"records": [row([_real(rec)])]}]), ledger)
    assert code == 1, "a real recommendation with no gate context must fail the row"
    assert ledger_recs(ledger) == [], "nothing may be written"


def test_gates_are_recorded_beside_the_recommendation(ledger):
    """Passing the gates is evidence, and evidence is a record."""
    run_sync(FakeAirtable([{"records": [row([_real(rec)])]}]), ledger, gate_context=gate_ctx())
    g = store.read_kind(ledger, "decision_gates")
    assert len(g) == 1
    assert g[0]["overall"] == "PASS"
    assert g[0]["decision_quote"]["executable_price"] == 0.62
    assert g[0]["gates"][G.G_QUOTE_FRESHNESS]["status"] == "PASS"
    assert g[0]["net_ev"]["fee_state"] == "KNOWN"


def test_a_live_ask_above_the_ceiling_fails_the_whole_batch(ledger):
    """The recorded ask was fine; the LIVE ask is not. The batch is refused, not trimmed."""
    payload = [_real(rec, rid="rec_ok1"), _real(a_pass, rid="rec_ok2")]
    code, _calls, _c = run_sync(FakeAirtable([{"records": [row(payload)]}]), ledger,
                                gate_context=gate_ctx(ask=0.90))
    assert code == 1
    assert ledger_recs(ledger) == [], "the valid PASS in the same batch must not land either"


def test_a_stale_decision_time_quote_blocks_a_real_recommendation(ledger):
    """15 minutes is the window. 40 minutes is not a price, it is a memory."""
    stale = gate_ctx()
    stale.capture_index = _FreshIndex(confirmed=NOW - timedelta(minutes=40))
    code, _calls, _c = run_sync(FakeAirtable([{"records": [row([_real(rec)])]}]), ledger,
                                gate_context=stale)
    assert code == 1
    assert ledger_recs(ledger) == []


def test_a_pass_still_lands_on_a_stale_quote(ledger):
    """A PASS is not gated on price freshness -- staleness is frequently the reason for the pass."""
    stale = gate_ctx()
    stale.capture_index = _FreshIndex(confirmed=NOW - timedelta(minutes=400))
    code, _calls, _c = run_sync(FakeAirtable([{"records": [row([_real(a_pass, rid="rec_p1")])]}]), ledger,
                                gate_context=stale)
    assert code == 0
    assert ledger_recs(ledger) == ["rec_p1.json"]


def test_the_bridge_never_rewrites_source_fields(ledger):
    """Status is the only field the importer writes back."""
    fake = FakeAirtable([{"records": [row([rec()])]}])
    run_sync(fake, ledger)
    for batch in fake.patches:
        for r in batch:
            assert set(r["fields"]) == {AB.F_STATUS}, \
                f"the importer wrote {set(r['fields'])}; Run ID, Sport and Payload are source data"


# ---- the batch is atomic on disk, not just in intent -------------------------------------------------

def test_a_failure_midway_through_writing_rolls_the_batch_back(ledger, monkeypatch):
    """If the 3rd of 4 files cannot be written, the first 2 are removed rather than left as a partial run."""
    plan = AB.plan_run(row([rec("rec_w1"), rec("rec_w2"), rec("rec_w3"), rec("rec_w4")]), ledger, now=NOW)
    real = S.write_record
    calls = {"n": 0}

    def flaky(path, payload, **kw):
        calls["n"] += 1
        if calls["n"] == 3:
            raise OSError("disk full")
        return real(path, payload, **kw)
    monkeypatch.setattr(S, "write_record", flaky)
    monkeypatch.setattr(AB.S, "write_record", flaky)
    with pytest.raises(AB.BridgeError):
        AB.apply_plan(plan)
    assert ledger_recs(ledger) == [], "a half-written handicap run must not survive"


def test_planning_never_touches_the_ledger(ledger):
    AB.plan_run(row([rec()]), ledger, now=NOW)
    assert ledger_recs(ledger) == [], "planning must be free of side effects"


def test_dry_run_writes_nothing_and_changes_no_status(ledger):
    fake = FakeAirtable([{"records": [row([rec()])]}])
    code, pushes, _ = run_sync(fake, ledger, dry_run=True)
    assert code == 0 and pushes == [] and ledger_recs(ledger) == []
    assert not fake.patches


# ---- the documented example must stay valid ---------------------------------------------------------

def test_the_worked_example_in_the_docs_actually_validates():
    """A copy-pasteable example that the validator rejects is worse than no example.

    ChatGPT is told to build the live E2E row from this payload, so it is checked the way the bridge would
    check it: against a row created moments after the recommendation was written.
    """
    import re
    doc = open(os.path.join(ROOT, "docs", "AIRTABLE_BRIDGE.md")).read()
    blocks = re.findall(r"```json\n(.*?)\n```", doc, re.S)
    records = json.loads(blocks[-1])
    created = datetime(2026, 9, 7, 18, 5, tzinfo=timezone.utc)
    assert AB.check_batch(records, run_id="20260907T180000Z_e2e",
                          airtable_created=created, now=created + timedelta(minutes=1)) == []


def test_a_stale_copy_of_the_example_is_refused():
    """And the same example submitted weeks later is refused: the anti-backfill rule is not decorative."""
    import re
    doc = open(os.path.join(ROOT, "docs", "AIRTABLE_BRIDGE.md")).read()
    records = json.loads(re.findall(r"```json\n(.*?)\n```", doc, re.S)[-1])
    late = datetime(2026, 10, 17, 18, 5, tzinfo=timezone.utc)
    with pytest.raises(AB.BridgeError, match="backfilled"):
        AB.check_batch(records, run_id="20260907T180000Z_e2e", airtable_created=late, now=late)


def test_the_docs_never_contain_a_token():
    doc = open(os.path.join(ROOT, "docs", "AIRTABLE_BRIDGE.md")).read()
    assert not __import__("re").search(r"\bpat[A-Za-z0-9]{14}\b", doc), "an Airtable PAT is in the docs"


# ---- malformed rows from the wire --------------------------------------------------------------------

def test_a_row_with_no_record_id_is_skipped_not_written(ledger):
    """An id-less row cannot be status-updated, so it must not be planned as though it could."""
    bad = row([rec()])
    del bad["id"]
    fake = FakeAirtable([{"records": [bad]}])
    code, pushes, _ = run_sync(fake, ledger)
    assert ledger_recs(ledger) == [] and pushes == []
    assert not fake.patches, "there is no id to PATCH; the importer must not invent one"


def test_an_empty_recommendation_id_cannot_produce_a_dotjson_file(ledger):
    """`""` resolves to "<week>/.json", whose basename still ends in .json -- the extension check is not enough."""
    with pytest.raises(AB.BridgeError):
        AB._safe_record_path(ledger, "recommendations", 2026, 1, "")
    with pytest.raises(AB.BridgeError):
        AB._safe_record_path(ledger, "recommendations", 2026, 1, "a/b")


def test_a_row_with_a_missing_createdtime_is_refused(ledger):
    bad = row([rec()])
    del bad["createdTime"]
    _expect_error(ledger, [bad])
