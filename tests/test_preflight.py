"""A candidate cannot be surfaced as a BET without passing the same checks the ledger will replay.

The sequence this file exists to make impossible:

    13:00  ChatGPT says BET
    13:01  the owner places it
    01:00  the importer runs and discovers the book was too thin to fill the stake

Every finding there is correct and twelve hours late. So the gates now run at the FRONT of the pipeline, on
the candidate, before anything is shown as an instruction -- and the importer's later run is a REPLAY of the
same computation from the capture stream, not the first time anybody looked.

Two properties are pinned throughout:

  * a candidate that would fail any gate cannot reach the user-visible RECOMMENDED/BET state;
  * preflight and the importer produce the SAME verdict, because they run the same function on the same
    clock. If they could differ, one of them would be a second implementation of the rules.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.handicap import gates as G          # noqa: E402
from nfl_edge.handicap import preflight as P      # noqa: E402
from nfl_edge.handicap import risk as R           # noqa: E402
from nfl_edge.handicap import schema as S         # noqa: E402
from nfl_edge.handicap import store               # noqa: E402

DECISION = datetime(2026, 9, 9, 13, 0, tzinfo=timezone.utc)
IMPORT = DECISION + timedelta(hours=12)
KICKOFF = DECISION + timedelta(hours=7)
TICKER = "KXNFLGAME-26SEP09NESEA-SEA"
SERIES = "KXNFLGAME"
DEEP = [(0.56, 100000.0)]


# ---- a real capture tree and a real ledger ----------------------------------------------------------

def market_data(tmp_path, *, ask=0.56, ladder=DEEP, minutes_before=4.0, name="md"):
    """A capture tree in the on-disk shape the real indexes read: manifest, quotes, books."""
    when = DECISION - timedelta(minutes=minutes_before)
    root = tmp_path / name
    rid = when.strftime("%Y%m%dT%H%M%SZ")
    day = root / "data" / "kalshi" / "capture" / when.strftime("%Y-%m-%d")
    day.mkdir(parents=True, exist_ok=True)
    (day / f"{rid}.manifest.json").write_text(json.dumps({
        "run_id": rid, "started_at": when.isoformat(), "finished_at": when.isoformat(),
        "series": {SERIES: {"n": 40, "complete": True, "tier": "FULL", "observed_at": when.isoformat()}},
        "partial": False}))
    (day / f"{rid}.quotes.jsonl").write_text(json.dumps({
        "ticker": TICKER, "series_ticker": SERIES, "observed_at": when.isoformat(), "status": "active",
        "yes_bid": round(ask - 0.02, 4), "yes_ask": ask,
        "no_bid": round(1 - ask - 0.02, 4), "no_ask": round(1 - ask, 4)}) + "\n")
    if ladder:
        (day / f"{rid}.books.jsonl").write_text(json.dumps({
            "run_id": rid, "observed_at": when.isoformat(), "ticker": TICKER,
            "orderbook_fp": {"no_dollars": [[f"{1 - p:.4f}", f"{s}"] for p, s in
                                            sorted(ladder, key=lambda x: -x[0])],
                             "yes_dollars": [["0.5000", "10"]]}}) + "\n")
    return str(root)


def ledger(tmp_path, records=(), name="ledger"):
    root = tmp_path / name
    for r in records:
        path = store.record_path(str(root), "recommendations", r["season"], r["week"],
                                 r["recommendation_id"])
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(r, f)
    root.mkdir(parents=True, exist_ok=True)
    return str(root)


def candidate(**kw):
    """A complete candidate, in the recommendation schema, with a decision that is NOT yet RECOMMENDED."""
    d = dict(
        recommendation_id="rec_pf0000000000000001", schema_version=S.HANDICAP_SCHEMA_VERSION,
        created_at=DECISION.isoformat(), handicap_run_id="20260909T130000Z", packet_sha="abc",
        season=2026, week=1, game_id="2026_01_NE_SEA", kickoff_utc=KICKOFF.isoformat(),
        market_ticker=TICKER, market_family="GAME_WINNER", side="YES",
        correlation_group="NE_SEA_home",
        yes_bid=0.54, yes_ask=0.56, no_bid=0.42, no_ask=0.44, mid=0.55,
        market_timestamp=DECISION.isoformat(), minutes_to_kickoff=420.0,
        support_state=S.SUPPORT_SUPPORTED, model_version="shadow-0.4.0", artifact_hash="cafe",
        model_probability=0.60, probability_low=0.60, probability_mid=0.66, probability_high=0.72,
        decision=P.CANDIDATE, grade="A", bet_up_to_probability=0.59,
        proposed_stake=10, recommended_stake=10, bankroll_snapshot=2000.0,
        primary_thesis="thesis", key_supporting_factors=["a"], counterarguments=["b"],
        uncertainties=["c"], source_freshness={"shadow_snapshot": DECISION.isoformat()})
    d.update(kw)
    return d


# Approval happens a couple of minutes after the draft, which is the ordinary case: an Automation fires,
# a runner starts, the gates run. `approval_as_of` is what everything is judged at.
APPROVAL = DECISION + timedelta(minutes=2)


def fly(tmp_path, cand=None, *, md=None, led=None, prior=(), at=None, **kw):
    return P.preflight(cand or candidate(), market_data_root=md or market_data(tmp_path),
                       ledger_root=led or ledger(tmp_path, prior), root=ROOT,
                       approval_as_of=at or APPROVAL, **kw)


# ---- the happy path ----------------------------------------------------------------------------------

def test_a_sound_candidate_is_approved_as_a_bet(tmp_path):
    r = fly(tmp_path)
    assert r.verdict == P.APPROVED, r.blocking_reasons
    assert r.surface_as == S.RECOMMENDED and r.may_be_shown_as_a_bet
    assert r.approved_stake == 10.0
    assert r.as_of == APPROVAL.isoformat(), "evaluated at the APPROVAL, not at the draft time"
    assert r.candidate_created_at == DECISION.isoformat(), "the draft's own timestamp is kept as lineage"


def test_a_candidate_is_evaluated_as_the_recommendation_it_would_become(tmp_path):
    """`decision: CANDIDATE` must not slip past gates that only apply to RECOMMENDED records."""
    r = fly(tmp_path, candidate(decision=P.CANDIDATE))
    assert r.gates[G.G_DEPTH]["status"] == G.PASS
    assert r.gates[G.G_NET_EV]["status"] == G.PASS
    assert r.gates[G.G_QUOTE_FRESHNESS]["status"] == G.PASS, \
        "a candidate that is not gated is a candidate that is not checked"


def test_the_stake_shown_is_the_stake_the_policy_approved(tmp_path):
    """Grade A caps at 2u = $20, so a $50 proposal is approved at $20 -- and $20 is what gets gated."""
    r = fly(tmp_path, candidate(proposed_stake=50, recommended_stake=50))
    assert r.approved_stake == 20.0
    assert r.proposed_stake == 50
    assert r.may_be_shown_as_a_bet
    assert r.depth["requested_stake"] == 20.0, \
        "the book walk must size the APPROVED stake; gating the proposal would check a position nobody takes"


# ---- each gate blocks the BET state ------------------------------------------------------------------

def test_a_thin_book_cannot_reach_the_bet_state(tmp_path):
    md = market_data(tmp_path, ladder=[(0.56, 3.0)])
    r = fly(tmp_path, candidate(proposed_stake=50, recommended_stake=50), md=md)
    assert not r.may_be_shown_as_a_bet
    assert r.surface_as == P.CANDIDATE
    assert any(G.G_DEPTH in b for b in r.blocking_reasons), r.blocking_reasons


def test_a_walk_above_the_ceiling_cannot_reach_the_bet_state(tmp_path):
    md = market_data(tmp_path, ladder=[(0.56, 1.0), (0.70, 100000.0)])
    r = fly(tmp_path, md=md)
    assert not r.may_be_shown_as_a_bet
    assert any("bet_up_to_probability" in b for b in r.blocking_reasons), r.blocking_reasons


def test_a_price_above_the_ceiling_cannot_reach_the_bet_state(tmp_path):
    """The schema refuses this outright, and preflight surfaces the refusal instead of a bet."""
    md = market_data(tmp_path, ask=0.66, ladder=[(0.66, 100000.0)])
    r = fly(tmp_path, candidate(yes_ask=0.66, no_ask=0.34), md=md)
    assert not r.may_be_shown_as_a_bet
    assert any("NOT ACTIONABLE" in b or G.G_CEILING in b for b in r.blocking_reasons), r.blocking_reasons


def test_an_unknown_fee_regime_cannot_reach_the_bet_state(tmp_path):
    """A series the registry does not know has no computable cost, so it has no computable net EV."""
    r = fly(tmp_path, candidate(market_ticker="KXMADEUP-26SEP09NESEA-SEA"))
    assert not r.may_be_shown_as_a_bet
    assert any(G.G_NET_EV in b or G.G_DEPTH in b or G.G_QUOTE_FRESHNESS in b
               for b in r.blocking_reasons), r.blocking_reasons


def test_a_negative_net_ev_cannot_reach_the_bet_state(tmp_path):
    """A gross edge that its fees consume is not a bet, and the owner must never see it as one."""
    r = fly(tmp_path, candidate(probability_mid=0.5601, probability_low=0.5600,
                                probability_high=0.5700))
    assert not r.may_be_shown_as_a_bet
    assert any(G.G_NET_EV in b for b in r.blocking_reasons), r.blocking_reasons


def test_an_unresolved_player_identity_cannot_reach_the_bet_state(tmp_path):
    r = fly(tmp_path, candidate(market_family="PLAYER_STAT",
                                support_state=S.SUPPORT_UNSUPPORTED_IDENTITY))
    assert not r.may_be_shown_as_a_bet
    assert any(G.G_IDENTITY in b or "identity" in b.lower() for b in r.blocking_reasons), \
        r.blocking_reasons


def test_a_missing_player_availability_cannot_reach_the_bet_state(tmp_path):
    r = fly(tmp_path, candidate(market_family="PLAYER_STAT", player_id="00-0012345",
                                support_state=S.SUPPORT_SUPPORTED))
    assert not r.may_be_shown_as_a_bet
    assert any(G.G_AVAILABILITY in b or "availability" in b.lower()
               for b in r.blocking_reasons), r.blocking_reasons


def test_a_cumulative_cap_breach_cannot_reach_the_bet_state(tmp_path):
    """The correlation cap is already full from an EARLIER run, so this candidate is not a bet."""
    prior = [dict(candidate(recommendation_id=f"rec_prior{i}", recommended_stake=15,
                            proposed_stake=15, decision=S.RECOMMENDED),
                  ) for i in range(2)]
    r = fly(tmp_path, candidate(proposed_stake=20, recommended_stake=20), prior=prior)
    assert not r.may_be_shown_as_a_bet
    assert any(G.G_RISK in b or "risk policy" in b for b in r.blocking_reasons), r.blocking_reasons


def test_a_stale_price_cannot_reach_the_bet_state(tmp_path):
    md = market_data(tmp_path, minutes_before=200.0)
    r = fly(tmp_path, md=md)
    assert not r.may_be_shown_as_a_bet
    assert any(G.G_QUOTE_FRESHNESS in b for b in r.blocking_reasons), r.blocking_reasons


def test_an_unreadable_ledger_cannot_reach_the_bet_state(tmp_path):
    """Cumulative caps against a book we cannot see are not caps. Fail closed."""
    rec = candidate(decision=S.RECOMMENDED, created_at=APPROVAL.isoformat())
    report = R.report_for_batch([rec], R.RiskPolicy.load(ROOT), None)
    ctx = P.build_context(market_data(tmp_path), root=ROOT, risk_report=report)
    gr = G.evaluate_gates(rec, ctx)
    assert gr.gates[G.G_RISK].status == G.UNAVAILABLE
    assert "could not be read" in gr.gates[G.G_RISK].reason


# ---- preflight and the import replay must agree ------------------------------------------------------

def test_preflight_and_the_delayed_import_reach_the_same_verdict(tmp_path):
    """The importer is a REPLAY. If it could disagree, one of the two is a second set of rules.

    Both are run here against the same evidence -- and the import is deliberately performed with no clock
    argument at all, hours after the fact, exactly as the twelve-hourly job does.
    """
    md, led = market_data(tmp_path), ledger(tmp_path)
    for cand, expect_bet in [(candidate(), True),
                             (candidate(probability_mid=0.5601, probability_low=0.56,
                                        probability_high=0.57), False)]:
        pre = P.preflight(cand, market_data_root=md, ledger_root=led, root=ROOT,
                          approval_as_of=APPROVAL)
        # The importer replays the APPROVED RECORD, which is what the ledger archives.
        rec_as_filed = pre.approved_record or dict(cand, decision=S.RECOMMENDED,
                                                   created_at=APPROVAL.isoformat())
        report = R.report_for_batch([rec_as_filed], R.RiskPolicy.load(ROOT), led)
        ctx = P.build_context(md, root=ROOT, risk_report=report)
        imported = G.evaluate_gates(rec_as_filed, ctx)
        assert pre.may_be_shown_as_a_bet is expect_bet
        assert (imported.overall == G.PASS) is expect_bet, \
            "the delayed replay must reach the verdict preflight reached"
        assert imported.as_of == pre.as_of, "both must judge at the APPROVAL timestamp"


def test_the_import_replay_does_not_depend_on_when_it_runs(tmp_path):
    md, led = market_data(tmp_path), ledger(tmp_path)
    rec_as_filed = candidate(decision=S.RECOMMENDED, created_at=APPROVAL.isoformat())
    report = R.report_for_batch([rec_as_filed], R.RiskPolicy.load(ROOT), led)
    first = G.evaluate_gates(rec_as_filed, P.build_context(md, root=ROOT, risk_report=report))
    second = G.evaluate_gates(rec_as_filed, P.build_context(md, root=ROOT, risk_report=report))
    assert first.overall == second.overall == G.PASS
    assert IMPORT > DECISION, "the import genuinely happens later; nothing in the verdict knows that"


def test_preflight_does_not_reimplement_the_gates():
    """The rules live in one module. A second copy would drift, and the replay would stop meaning anything."""
    import inspect
    src = inspect.getsource(P)
    assert "G.evaluate_gates" in src, "preflight must delegate to the gate module"
    assert "R.report_for_batch" in src, "preflight must use the shared cumulative portfolio report"
    # Forwarding a default is fine; RE-DECIDING with it is not. These are the shapes of a copied rule.
    for smell in ("max_exposure_per", "bet_up_to_probability >", "net_ev_dollars <=",
                  "vwap >", "walk_book", "entry_fee("):
        assert smell not in src, f"{smell!r} looks like gate arithmetic copied into preflight"


def test_preflight_writes_nothing(tmp_path):
    md, led = market_data(tmp_path), ledger(tmp_path)
    before = sorted(os.walk(led))
    P.preflight(candidate(), market_data_root=md, ledger_root=led, root=ROOT,
                approval_as_of=APPROVAL)
    assert sorted(os.walk(led)) == before, "preflight is a check, not a write"


# ---- what a blocked candidate may be called ----------------------------------------------------------

def test_a_blocked_candidate_is_never_labelled_recommended(tmp_path):
    md = market_data(tmp_path, ladder=[(0.56, 2.0)])
    r = fly(tmp_path, candidate(proposed_stake=50, recommended_stake=50), md=md)
    assert r.surface_as != S.RECOMMENDED
    assert r.surface_as in (P.CANDIDATE, S.PASS, S.WATCHLIST)
    assert "NOT A BET" in P.summarise([r])


def test_the_summary_shows_the_approved_stake_not_the_proposal(tmp_path):
    r = fly(tmp_path, candidate(proposed_stake=50, recommended_stake=50))
    line = P.summarise([r])
    assert line.startswith("BET") and "$20.00" in line and "proposed $50.00" in line


def test_a_batch_is_sized_together_not_one_at_a_time(tmp_path):
    """Three candidates in one group: individually fine, jointly over the 3u cap."""
    md, led = market_data(tmp_path), ledger(tmp_path)
    cands = [candidate(recommendation_id=f"rec_pf000000000000000{i}", proposed_stake=15,
                       recommended_stake=15) for i in (1, 2, 3)]
    results = P.preflight_batch(cands, market_data_root=md, ledger_root=led, root=ROOT,
                                approval_as_of=APPROVAL)
    approved = sum(r.approved_stake or 0 for r in results if r.may_be_shown_as_a_bet)
    assert approved <= 30.0, "the correlation group cap is 3u = $30 across the whole slate"
    assert not all(r.may_be_shown_as_a_bet for r in results)
