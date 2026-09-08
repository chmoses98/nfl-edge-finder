"""Gates evaluate the DECISION, not the import.

The Airtable bridge is retrospective archival transport on a twelve-hour cadence. GitHub ingestion is when a
decision is FILED, not when it is MADE. So the question a gate asks is "was this sound at 13:00?", and the
answer must not depend on whether the importer got to it at 13:01 or at 01:00 the next morning.

    13:00   decision made, YES ask 0.56, recorded
    01:00   importer runs; the game has kicked off, the market is closed, the ask is gone

Judged at 01:00 that recommendation fails everything, which answers a question nobody asked. Judged at 13:00
it either was or was not a sound call. This file pins the six cases from the review, plus the invariant they
add up to: import latency changes nothing.

Two failure directions, and both matter:

    using post-decision evidence   rescues a bet that was stale when it was made
    using import-time freshness    destroys a bet that was fine when it was made

The first loses money. The second loses the experiment. Neither is acceptable.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.execution import depth as D      # noqa: E402
from nfl_edge.execution import fees as F       # noqa: E402
from nfl_edge.execution import quotes as Q     # noqa: E402
from nfl_edge.handicap import gates as G       # noqa: E402
from nfl_edge.handicap import risk as R        # noqa: E402
from nfl_edge.handicap import schema as S      # noqa: E402

DECISION = datetime(2026, 9, 9, 13, 0, tzinfo=timezone.utc)
IMPORT = DECISION + timedelta(hours=12)                      # the next scheduled sync
KICKOFF = DECISION + timedelta(hours=7)                      # kicks off BETWEEN decision and import
TICKER = "KXNFLGAME-26SEP09NESEA-SEA"
SERIES = "KXNFLGAME"


# ---- capture fixtures ------------------------------------------------------------------------------

def capture(tmp_path, runs, books=()):
    """A real capture tree: manifest + change-suppressed quotes + order books, per run."""
    root = tmp_path / "md"
    for when, complete, rows in runs:
        rid = when.strftime("%Y%m%dT%H%M%SZ")
        day = root / "data" / "kalshi" / "capture" / when.strftime("%Y-%m-%d")
        day.mkdir(parents=True, exist_ok=True)
        (day / f"{rid}.manifest.json").write_text(json.dumps({
            "run_id": rid, "started_at": when.isoformat(), "finished_at": when.isoformat(),
            "series": {SERIES: {"n": 40, "complete": complete, "tier": "FULL",
                                "observed_at": when.isoformat()}},
            "partial": not complete}))
        if rows:
            (day / f"{rid}.quotes.jsonl").write_text("".join(json.dumps(r) + "\n" for r in rows))
    for when, ladder in books:
        rid = when.strftime("%Y%m%dT%H%M%SZ")
        day = root / "data" / "kalshi" / "capture" / when.strftime("%Y-%m-%d")
        day.mkdir(parents=True, exist_ok=True)
        (day / f"{rid}.books.jsonl").write_text(json.dumps({
            "run_id": rid, "observed_at": when.isoformat(), "ticker": TICKER,
            "orderbook_fp": {"no_dollars": [[f"{1 - p:.4f}", f"{s}"] for p, s in
                                            sorted(ladder, key=lambda x: -x[0])],
                             "yes_dollars": [["0.5000", "10"]]}}) + "\n")
    return str(root)


def quote(when, yes_ask=0.56):
    return {"ticker": TICKER, "series_ticker": SERIES, "observed_at": when.isoformat(), "status": "active",
            "yes_bid": round(yes_ask - 0.02, 4), "yes_ask": yes_ask,
            "no_bid": round(1 - yes_ask - 0.02, 4), "no_ask": round(1 - yes_ask, 4)}


def rec(**kw):
    d = dict(
        recommendation_id="rec_dt0000000000000001", schema_version=S.HANDICAP_SCHEMA_VERSION,
        created_at=DECISION.isoformat(), handicap_run_id="20260909T130000Z", packet_sha="abc",
        season=2026, week=1, game_id="2026_01_NE_SEA", kickoff_utc=KICKOFF.isoformat(),
        market_ticker=TICKER, market_family="GAME_WINNER", side="YES",
        yes_bid=0.54, yes_ask=0.56, no_bid=0.42, no_ask=0.44, mid=0.55,
        market_timestamp=DECISION.isoformat(), minutes_to_kickoff=420.0,
        support_state=S.SUPPORT_SUPPORTED, model_version="shadow-0.4.0", artifact_hash="cafe",
        model_probability=0.60,
        probability_low=0.60, probability_mid=0.66, probability_high=0.72,
        decision=S.RECOMMENDED, grade="B", bet_up_to_probability=0.59,
        proposed_stake=10, recommended_stake=10, bankroll_snapshot=2000.0,
        primary_thesis="thesis", key_supporting_factors=["a"], counterarguments=["b"],
        uncertainties=["c"], source_freshness={"shadow_snapshot": DECISION.isoformat()})
    d.update(kw)
    return d


def gate(md, r=None, **kw):
    r = r or rec()
    ctx = G.GateContext(capture_index=Q.CaptureIndex(md), book_index=D.BookIndex(md),
                        fee_schedule=F.load_fee_schedule(ROOT), **kw)
    ctx.risk_report = R.RiskPolicy.load(ROOT).evaluate([R.Proposal.from_record(r)], 2000.0)
    return G.evaluate_gates(r, ctx)


DEEP = [(0.56, 100000.0)]


# ---- A: valid at T, imported 12 hours later --------------------------------------------------------

def test_A_quote_valid_at_the_decision_passes_when_imported_twelve_hours_later(tmp_path):
    """The headline case. The importer's lateness is not evidence about the decision."""
    t = DECISION - timedelta(minutes=4)
    md = capture(tmp_path, [(t, True, [quote(t)])], books=[(t, DEEP)])
    report = gate(md)
    assert report.gates[G.G_QUOTE_FRESHNESS].status == G.PASS, report.blocking_reasons
    assert report.as_of == DECISION.isoformat()
    assert report.decision_quote["age_minutes"] == pytest.approx(4.0, abs=0.1)


def test_the_verdict_is_identical_whenever_the_import_happens(tmp_path):
    """The invariant the other five cases are instances of.

    Nothing in the gate path reads a wall clock, so running the same gates a year later is the same
    computation. If this ever fails, some gate has grown a `now()`.
    """
    t = DECISION - timedelta(minutes=4)
    md = capture(tmp_path, [(t, True, [quote(t)])], books=[(t, DEEP)])
    first = gate(md)
    second = gate(md)
    assert first.overall == second.overall == G.PASS
    assert first.decision_quote["age_minutes"] == second.decision_quote["age_minutes"]
    assert first.as_of == second.as_of == DECISION.isoformat()


# ---- B: evidence only after T must not be used -----------------------------------------------------

def test_B_a_quote_that_only_exists_after_the_decision_is_not_used(tmp_path):
    """Post-decision capture is information the handicapper did not have."""
    after = DECISION + timedelta(minutes=30)
    md = capture(tmp_path, [(after, True, [quote(after)])], books=[(after, DEEP)])
    report = gate(md)
    assert report.gates[G.G_QUOTE_FRESHNESS].status in G.BLOCKING
    assert report.overall == G.FAIL
    assert report.decision_quote["state"] == Q.UNCONFIRMED


def test_B_a_later_capture_cannot_rescue_a_decision_that_was_stale_when_made(tmp_path):
    """The money-losing direction: a bet stale at 13:00 must not pass because of a 13:30 capture."""
    stale = DECISION - timedelta(hours=3)
    fresh_after = DECISION + timedelta(minutes=5)
    md = capture(tmp_path, [(stale, True, [quote(stale)]), (fresh_after, True, [quote(fresh_after)])],
                 books=[(stale, DEEP), (fresh_after, DEEP)])
    report = gate(md)
    assert report.gates[G.G_QUOTE_FRESHNESS].status == G.FAIL
    assert report.decision_quote["state"] == Q.STALE
    assert report.decision_quote["confirmed_at"].startswith(stale.isoformat()[:16]), \
        "the confirmation used must be the pre-decision one"


# ---- C: valid at T, stale by import time -----------------------------------------------------------

def test_C_a_quote_fresh_at_the_decision_but_ancient_by_import_still_passes(tmp_path):
    """12 hours old at import, 4 minutes old at the decision. Only the second number is a question."""
    t = DECISION - timedelta(minutes=4)
    md = capture(tmp_path, [(t, True, [quote(t)])], books=[(t, DEEP)])
    report = gate(md)
    age_at_import = (IMPORT - t).total_seconds() / 60.0
    assert age_at_import > 700, "the fixture must actually be ancient by import time"
    assert report.gates[G.G_QUOTE_FRESHNESS].status == G.PASS
    assert report.decision_quote["age_minutes"] < 15


# ---- D: stale at T, fresher later ------------------------------------------------------------------

def test_D_a_quote_stale_at_the_decision_fails_even_though_later_ones_exist(tmp_path):
    stale = DECISION - timedelta(minutes=45)
    later = DECISION + timedelta(hours=2)
    md = capture(tmp_path, [(stale, True, [quote(stale)]), (later, True, [quote(later)])],
                 books=[(stale, DEEP), (later, DEEP)])
    report = gate(md)
    assert report.gates[G.G_QUOTE_FRESHNESS].status == G.FAIL
    assert report.decision_quote["age_minutes"] == pytest.approx(45.0, abs=0.1)


# ---- E: kickoff between decision and import --------------------------------------------------------

def test_E_a_game_that_kicked_off_before_the_import_is_still_prospectively_valid(tmp_path):
    """Kickoff at T+7h, import at T+12h. The decision was prospective; archiving it later does not
    retroactively make it a live bet."""
    t = DECISION - timedelta(minutes=4)
    md = capture(tmp_path, [(t, True, [quote(t)])], books=[(t, DEEP)])
    assert KICKOFF < IMPORT, "the fixture must actually kick off before the import"
    report = gate(md)
    assert report.overall == G.PASS, report.blocking_reasons


def test_E_no_gate_compares_kickoff_against_wall_clock(tmp_path):
    """A kickoff long past is not a gate failure. It is the normal state of an archived decision."""
    old = rec(created_at=(DECISION - timedelta(days=30)).isoformat(),
              kickoff_utc=(DECISION - timedelta(days=30) + timedelta(hours=7)).isoformat())
    t = DECISION - timedelta(days=30, minutes=4)
    md = capture(tmp_path, [(t, True, [quote(t)])], books=[(t, DEEP)])
    report = gate(md, old)
    assert report.overall == G.PASS, report.blocking_reasons


# ---- F: created after kickoff still fails ----------------------------------------------------------

def test_F_a_recommendation_created_after_kickoff_is_still_refused(tmp_path):
    """Unchanged. minutes_to_kickoff <= 0 is a structural failure and does not need the market."""
    with pytest.raises(S.ValidationError, match="post-kickoff|minutes_to_kickoff"):
        S.validate_recommendation(rec(minutes_to_kickoff=-30.0))


def test_F_the_bridge_anti_backfill_bound_is_unchanged():
    """Airtable's createdTime keeps its own job: independent proof of when the handoff happened."""
    from nfl_edge.handicap import airtable_bridge as AB
    assert AB.MAX_HANDICAP_LEAD.total_seconds() <= 24 * 3600
    ko = DECISION + timedelta(hours=2)
    with pytest.raises(AB.BridgeError, match="not a prediction"):
        AB.check_timestamps({"created_at": (ko + timedelta(minutes=1)).isoformat(),
                             "kickoff_utc": ko.isoformat()},
                            ko + timedelta(minutes=2), ko + timedelta(minutes=3))


# ---- the decision timestamp itself ------------------------------------------------------------------

def test_a_record_with_no_decision_timestamp_cannot_be_gated(tmp_path):
    t = DECISION - timedelta(minutes=4)
    md = capture(tmp_path, [(t, True, [quote(t)])], books=[(t, DEEP)])
    report = gate(md, rec(created_at=None))
    assert report.gates[G.G_DECISION_TIME].status == G.UNAVAILABLE
    assert report.overall == G.FAIL


def test_a_naive_decision_timestamp_is_refused(tmp_path):
    t = DECISION - timedelta(minutes=4)
    md = capture(tmp_path, [(t, True, [quote(t)])], books=[(t, DEEP)])
    report = gate(md, rec(created_at="2026-09-09T13:00:00"))
    assert report.gates[G.G_DECISION_TIME].status == G.UNAVAILABLE
    assert "timezone" in report.gates[G.G_DECISION_TIME].reason


def test_the_resolver_refuses_to_default_to_wall_clock():
    """No accidental `now()`: omitting the decision time is an error, not a silent default."""
    with pytest.raises(ValueError, match="DECISION timestamp"):
        Q.resolve_decision_quote(Q.CaptureIndex("/nonexistent"), TICKER, "YES")


def test_the_gate_context_carries_no_wall_clock():
    assert "now" not in G.GateContext.__dataclass_fields__, \
        "a `now` on the gate context is how import time leaks back into the market gates"


# ---- information-availability timestamps ------------------------------------------------------------

def test_per_series_observed_at_is_preferred_over_run_start(tmp_path):
    """A run works through ~270 series over minutes; its start is not when this series became knowable."""
    start = DECISION - timedelta(minutes=20)
    actual = DECISION - timedelta(minutes=3)
    root = tmp_path / "md" / "data" / "kalshi" / "capture" / start.strftime("%Y-%m-%d")
    root.mkdir(parents=True)
    rid = start.strftime("%Y%m%dT%H%M%SZ")
    (root / f"{rid}.manifest.json").write_text(json.dumps({
        "run_id": rid, "started_at": start.isoformat(), "finished_at": actual.isoformat(),
        "series": {SERIES: {"n": 1, "complete": True, "observed_at": actual.isoformat()}}}))
    (root / f"{rid}.quotes.jsonl").write_text(json.dumps(quote(actual)) + "\n")

    q = Q.resolve_decision_quote(Q.CaptureIndex(str(tmp_path / "md")), TICKER, "YES",
                                 series_ticker=SERIES, as_of=DECISION)
    assert q.age_minutes == pytest.approx(3.0, abs=0.1), \
        "freshness must use the series' own fetch time, not the run start 20 minutes earlier"
    assert q.state == Q.FRESH


def test_without_per_series_times_the_conservative_bounds_are_used(tmp_path):
    """Old captures have only run-level timestamps. Both directions must round against the recommendation.

    Here the run STARTED before the decision but FINISHED after it. The late bound decides visibility, so
    this run is treated as possibly-after and is not used -- rather than being admitted on the strength of
    its start time.
    """
    start = DECISION - timedelta(minutes=5)
    finish = DECISION + timedelta(minutes=5)
    root = tmp_path / "md" / "data" / "kalshi" / "capture" / start.strftime("%Y-%m-%d")
    root.mkdir(parents=True)
    rid = start.strftime("%Y%m%dT%H%M%SZ")
    (root / f"{rid}.manifest.json").write_text(json.dumps({
        "run_id": rid, "started_at": start.isoformat(), "finished_at": finish.isoformat(),
        "series": {SERIES: {"n": 1, "complete": True}}}))          # no per-series observed_at
    (root / f"{rid}.quotes.jsonl").write_text(json.dumps(quote(start)) + "\n")

    q = Q.resolve_decision_quote(Q.CaptureIndex(str(tmp_path / "md")), TICKER, "YES",
                                 series_ticker=SERIES, as_of=DECISION)
    assert q.state == Q.UNCONFIRMED, \
        "a run that may have fetched this series after the decision must not confirm it"


def test_mutable_ticker_state_is_not_used_when_it_postdates_the_decision(tmp_path):
    """`last_seen` holds only the LATEST run per ticker, so it cannot answer a historical question.

    When its run is after the decision it is simply not usable evidence, and resolution falls through to the
    immutable per-run manifests -- which can answer it exactly.
    """
    early = DECISION - timedelta(minutes=6)
    late = DECISION + timedelta(hours=4)
    md = capture(tmp_path, [(early, True, [quote(early)]), (late, True, [quote(late)])])
    state = tmp_path / "md" / "data" / "kalshi" / "capture" / "state.json"
    state.write_text(json.dumps({"fingerprints": {},
                                 "last_seen": {TICKER: late.strftime("%Y%m%dT%H%M%SZ")}}))

    q = Q.resolve_decision_quote(Q.CaptureIndex(str(tmp_path / "md")), TICKER, "YES",
                                 series_ticker=SERIES, as_of=DECISION)
    assert q.state == Q.FRESH
    assert q.confirmation_basis == Q.CONFIRM_SERIES, "must fall back to the immutable manifests"
    assert q.age_minutes == pytest.approx(6.0, abs=0.1)


# ---- the fee schedule is also read as of the decision ------------------------------------------------

def test_the_fee_schedule_in_force_at_the_decision_is_the_one_used():
    """A schedule that took effect after the decision must not price it."""
    fs = F.load_fee_schedule(ROOT)
    fs.windows = list(fs.windows) + [{
        "window_id": "future", "effective_from": (DECISION + timedelta(days=1)).isoformat(),
        "effective_to": None, "taker_base_coefficient": 0.99, "maker_base_coefficient": 0.99,
        "series": {SERIES: {"taker_multiplier": 1.0, "maker_multiplier": 1.0}}}]
    at_decision, _ = fs.coefficients(DECISION)
    later, _ = fs.coefficients(DECISION + timedelta(days=2))
    assert at_decision == pytest.approx(0.07), "the decision must be priced with the schedule then in force"
    assert later == pytest.approx(0.99), "and the later window must still be reachable for later decisions"


def test_the_pricing_path_refuses_to_default_to_wall_clock():
    """The same trap as the quote resolver's, closed the same way.

    A silent `now()` in the fee lookup would price a 13:00 decision with whatever schedule is in force when
    the importer runs. `window_for` keeps a wall-clock default for diagnostics; `entry_fee` does not.
    """
    fs = F.load_fee_schedule(ROOT)
    with pytest.raises(F.FeeStateError, match="DECISION timestamp"):
        fs.entry_fee(0.50, 100, "KXNFLGAME", F.TAKER)
    # the diagnostic path is still allowed to mean "now"
    assert fs.describe("KXNFLGAME")


def test_no_market_gate_reads_a_wall_clock():
    """An audit of the gate module: the only `now()` may be the one stamping when the gates RAN."""
    import inspect
    src = inspect.getsource(G).splitlines()
    hits = [(i, ln.strip()) for i, ln in enumerate(src, 1)
            if "datetime.now" in ln or "utcnow" in ln]
    assert len(hits) == 1, f"unexpected wall-clock reads in the gate module: {hits}"
    # and it is inside to_record, which records evaluated_at -- not inside any gate
    assert "now = now or" in hits[0][1]
