"""A pregame position may not be authorised at or after kickoff. Explicitly, by name, and on both paths.

THE INCIDENT
------------
On 2026-09-13 a preflight for a 17:00:00Z kickoff answered at 17:01:30Z. The verdict was PREFLIGHT_BLOCKED
and it was the right one -- but it was reached because the newest confirmed quote was 17.1 minutes old, which
is a statement about the CAPTURE STREAM, not about the game having started. A minute earlier, with a capture
that had landed on time, exactly the same post-kickoff clock would have produced an APPROVAL.

That is the shape of a control that works by coincidence. Quote freshness asks "was this price real?" and is
satisfied by a four-minute-old capture -- which is perfectly compatible with a game that kicked off two
minutes ago. So the deadline gets its own gate, with its own name, and it is checked first.

WHY BOTH PATHS RUN THE SAME FUNCTION
------------------------------------
`gates.pre_kickoff_gate` is called by `evaluate_gates` (which the twelve-hourly importer replays) and by
`preflight._one` (which answers the owner in seconds). One function, so an archived record cannot be judged
by a different rule from the one that approved it. These tests pin both.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import gates as G          # noqa: E402
from nfl_edge.handicap import preflight as P      # noqa: E402
from nfl_edge.handicap import schema as S         # noqa: E402
from preflight_fakes import FakeKalshiClient, evidence_dir   # noqa: E402
from test_preflight import DECISION, KICKOFF, candidate, ledger  # noqa: E402

BLOCKER = "approval occurred at or after kickoff; a pregame position can no longer be authorized"


def gate(at, *, kickoff=KICKOFF, rec=None):
    r = rec if rec is not None else candidate(decision=S.RECOMMENDED, kickoff_utc=(
        kickoff.isoformat() if isinstance(kickoff, datetime) else kickoff))
    return G.pre_kickoff_gate(r, at)


# ---- the boundary, to the second ---------------------------------------------------------------------

def test_one_second_before_kickoff_passes_this_gate():
    """Late is not the same as too late. The gate is about the deadline and nothing else."""
    g = gate(KICKOFF - timedelta(seconds=1))
    assert g.status == G.PASS, g.reason
    assert g.evidence["minutes_to_kickoff"] > 0, "one second of headroom is still headroom"
    assert g.evidence["minutes_to_kickoff"] == pytest.approx(1 / 60.0, abs=0.01)


def test_exactly_at_kickoff_fails():
    """STRICTLY before. `as_of == kickoff` is not a tie we resolve in favour of the bet."""
    g = gate(KICKOFF)
    assert g.status == G.FAIL
    assert BLOCKER in g.reason


def test_after_kickoff_fails():
    g = gate(KICKOFF + timedelta(seconds=1))
    assert g.status == G.FAIL and BLOCKER in g.reason
    g = gate(KICKOFF + timedelta(minutes=90))
    assert g.status == G.FAIL and BLOCKER in g.reason


def test_the_incident_timeline_itself_fails_this_gate():
    """2026-09-13: kickoff 17:00:00Z, Airtable answered 17:01:30.488776Z."""
    ko = datetime(2026, 9, 13, 17, 0, tzinfo=timezone.utc)
    answered = datetime(2026, 9, 13, 17, 1, 30, 488776, tzinfo=timezone.utc)
    g = gate(answered, kickoff=ko)
    assert g.status == G.FAIL and BLOCKER in g.reason
    assert g.evidence["minutes_to_kickoff"] == pytest.approx(-1.508, abs=0.01)


# ---- fail closed on a deadline we cannot read ---------------------------------------------------------

def test_a_missing_kickoff_fails_closed():
    """UNAVAILABLE blocks a RECOMMENDED record exactly as FAIL does. An unknown deadline is never a far one."""
    g = gate(DECISION, rec=candidate(kickoff_utc=None))
    assert g.status == G.UNAVAILABLE
    assert "no kickoff_utc" in g.reason
    assert g.status in G.BLOCKING


def test_an_unparseable_kickoff_fails_closed():
    for bad in ("not a timestamp", "2026-13-45T99:99:99Z", "soon"):
        g = gate(DECISION, rec=candidate(kickoff_utc=bad))
        assert g.status == G.UNAVAILABLE, bad
        assert g.status in G.BLOCKING


def test_a_naive_kickoff_is_read_as_utc_rather_than_guessed_at():
    naive = KICKOFF.replace(tzinfo=None).isoformat()
    assert gate(KICKOFF - timedelta(minutes=1), rec=candidate(kickoff_utc=naive)).status == G.PASS
    assert gate(KICKOFF + timedelta(minutes=1), rec=candidate(kickoff_utc=naive)).status == G.FAIL


# ---- the gate is wired into the full gate report -------------------------------------------------------

def test_evaluate_gates_reports_it_as_a_blocking_reason_by_name():
    rec = candidate(decision=S.RECOMMENDED, created_at=(KICKOFF + timedelta(minutes=1)).isoformat())
    report = G.evaluate_gates(rec, G.GateContext())
    assert report.gates[G.G_PRE_KICKOFF].status == G.FAIL
    assert any(b.startswith(f"{G.G_PRE_KICKOFF}: ") and BLOCKER in b
               for b in report.blocking_reasons), report.blocking_reasons
    assert report.overall == G.FAIL


def test_a_sound_pregame_record_passes_it():
    rec = candidate(decision=S.RECOMMENDED)
    report = G.evaluate_gates(rec, G.GateContext())
    assert report.gates[G.G_PRE_KICKOFF].status == G.PASS


def test_it_does_not_depend_on_quote_freshness_at_all():
    """The point of the gate: no capture index, no book index, and it still answers."""
    rec = candidate(decision=S.RECOMMENDED, created_at=KICKOFF.isoformat())
    report = G.evaluate_gates(rec, G.GateContext())
    assert report.gates[G.G_QUOTE_FRESHNESS].status == G.UNAVAILABLE, "no evidence was supplied"
    assert report.gates[G.G_PRE_KICKOFF].status == G.FAIL, "and the deadline is answered anyway"


# ---- end to end through preflight, which is where the owner sees it -----------------------------------

def fly(tmp_path, *, at, cand=None, client=None):
    store, _root = evidence_dir(tmp_path)
    c = cand or candidate()
    client = client or FakeKalshiClient(retrieved_at=at - timedelta(seconds=30))
    from nfl_edge.handicap import live_evidence as LE      # noqa: PLC0415
    docs = [LE.collect(client, c["market_ticker"], side=c.get("side", "YES"),
                       airtable_record_id="recPFK00000000001", run_id="r", evidence_run_id="e")]
    return P.preflight(c, market_data_root=None, ledger_root=ledger(tmp_path), root=ROOT,
                       approval_as_of=at, request_created_at=at - timedelta(minutes=2),
                       capture_index=LE.EvidenceQuoteIndex(docs), book_index=LE.EvidenceBookIndex(docs))


def test_APPROVAL_BEFORE_KICKOFF_CAN_PROCEED(tmp_path):
    r = fly(tmp_path, at=DECISION + timedelta(minutes=2))
    assert r.verdict == P.APPROVED, r.blocking_reasons
    assert r.gates[G.G_PRE_KICKOFF]["status"] == G.PASS


def test_APPROVAL_ONE_SECOND_BEFORE_KICKOFF_CLEARS_THIS_GATE(tmp_path):
    r = fly(tmp_path, at=KICKOFF - timedelta(seconds=1))
    assert r.gates[G.G_PRE_KICKOFF]["status"] == G.PASS, r.gates[G.G_PRE_KICKOFF]
    assert not any(G.G_PRE_KICKOFF in b for b in r.blocking_reasons)


def test_APPROVAL_AT_KICKOFF_BLOCKS(tmp_path):
    r = fly(tmp_path, at=KICKOFF)
    assert r.verdict == P.BLOCKED and not r.may_be_shown_as_a_bet
    assert any(b == f"{G.G_PRE_KICKOFF}: {BLOCKER}" or b.startswith(f"{G.G_PRE_KICKOFF}: {BLOCKER}")
               for b in r.blocking_reasons), r.blocking_reasons


def test_APPROVAL_AFTER_KICKOFF_BLOCKS(tmp_path):
    r = fly(tmp_path, at=KICKOFF + timedelta(minutes=5))
    assert r.verdict == P.BLOCKED and not r.may_be_shown_as_a_bet
    assert any(BLOCKER in b for b in r.blocking_reasons), r.blocking_reasons


def test_a_post_kickoff_request_blocks_even_with_a_perfectly_fresh_quote(tmp_path):
    """This is the case the old architecture would have approved.

    The evidence is fetched seconds before the decision, so freshness, ceiling and depth are all satisfied.
    Only the deadline is wrong, and only the deadline gate notices.
    """
    at = KICKOFF + timedelta(seconds=30)
    r = fly(tmp_path, at=at)
    assert r.gates[G.G_PRE_KICKOFF]["status"] == G.FAIL
    assert not r.may_be_shown_as_a_bet
    assert r.blocking_reasons[0].startswith(G.G_PRE_KICKOFF), \
        "the deadline is reported first, not buried under a market complaint"


def test_a_missing_kickoff_blocks_a_real_candidate_end_to_end(tmp_path):
    r = fly(tmp_path, at=DECISION + timedelta(minutes=2), cand=candidate(kickoff_utc=None))
    assert not r.may_be_shown_as_a_bet
    assert any(G.G_PRE_KICKOFF in b for b in r.blocking_reasons), r.blocking_reasons


def test_the_importer_replays_the_same_verdict_from_the_archived_record(tmp_path):
    """The gate is a pure function of the record, so the replay needs no market evidence to reproduce it."""
    at = KICKOFF + timedelta(minutes=1)
    archived = candidate(decision=S.RECOMMENDED, created_at=at.isoformat())
    live = G.pre_kickoff_gate(archived, at)
    replayed = G.evaluate_gates(archived, G.GateContext()).gates[G.G_PRE_KICKOFF]
    assert live.status == replayed.status == G.FAIL
    assert live.reason == replayed.reason
    assert live.evidence == replayed.evidence


def test_a_test_only_probe_is_not_gated_on_a_kickoff_it_does_not_have(tmp_path):
    """TEST_ONLY risks no capital and is excluded from every report, so the live gates do not apply.

    It also can never be approved, which is the property that makes skipping them safe.
    """
    probe = candidate(test_only=True, kickoff_utc=(DECISION - timedelta(days=400)).isoformat(),
                      market_ticker="KXNFLGAME-99DEC31TSTTST-TST")
    r = P.preflight(probe, market_data_root=None, ledger_root=ledger(tmp_path), root=ROOT,
                    approval_as_of=DECISION + timedelta(minutes=1),
                    request_created_at=DECISION)
    assert r.may_be_shown_as_a_bet is False, "a TEST_ONLY probe is never a bet"
    assert G.G_PRE_KICKOFF not in (r.gates or {}), "the situational gates do not apply to a probe"
