"""The exchange cross-check is TIME-EVOLVING EVIDENCE published into a WRITE-ONCE corpus.

A ticker is EXCHANGE_MISSING at the first postgame run and terminal AGREE two days later. Both readings are
true; they are true of different moments. Filing them under one corpus identity made the later one contradict
the earlier one and the scheduled settlement died on

    EvaluationConflict: 3420 evaluation(s) contradict an already-published truth; nothing was written.
      ... agreement: existing='EXCHANGE_MISSING' new='AGREE' ...

These tests pin the lifecycle that fixes it, against the real EvaluationCorpus rather than a stand-in, because
what broke was the interaction between the two. The derived football settlement is untouched throughout: it is
immutable and nothing here writes to it.
"""
import itertools
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from nfl_edge.settlement import crosscheck as XC                                              # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                            # noqa: E402

GAME = "2026_02_A_H"
PID = "pred-1"
T1 = "2026-09-14T01:00:00+00:00"
T2 = "2026-09-16T01:00:00+00:00"
T3 = "2026-09-18T01:00:00+00:00"


def exch(result, *, status="finalized", value="1.0000", ticker="T"):
    return {"ticker": ticker, "result": result, "status": status, "settlement_value_dollars": value,
            "settlement_ts": "2026-09-14T01:00:00Z", "source": "kalshi_discovery_settled_bucket"}


class FakeResults:
    """ExchangeResults' whole surface, as the settlement driver uses it: get(ticker) -> record or None."""

    def __init__(self, records=None):
        self.by_ticker = dict(records or {})

    def get(self, ticker):
        return self.by_ticker.get(ticker)


def settlement_row(pid=PID, ticker="T", settled_yes=1.0):
    """A derived football settlement -- immutable, and the left-hand side of every cross-check below."""
    return {"prediction_id": pid, "ticker": ticker, "settled_yes": settled_yes, "settlement_status": "SETTLED",
            "settlement_kind": "binary", "market_family": "GAME_WINNER", "game_id": GAME}


def corpus(tmp_path):
    return ST.EvaluationCorpus(str(tmp_path / "crosscheck"), suffix="crosscheck_v2")


def run(tmp_path, exchange, *, now, rows=None, batch=None):
    """One postgame cross-check pass over the given settlement rows. Returns (manifest, rows offered).

    Each pass gets its own batch label. A real run takes one from the wall clock, but ST.batch_id() is only
    second-granular and successive passes here land inside the same second; the batch label is a file name, not
    an identity, so naming it explicitly changes nothing these tests are about.
    """
    c = corpus(tmp_path)
    p = c.planner(GAME)
    offered = []
    for s in (rows or [settlement_row()]):
        x = XC.versioned(XC.crosscheck_rows([s], exchange)[0], now=now)
        offered.append(x)
        p.offer(x)
    if p.conflicts:
        raise ST.EvaluationConflict(p.conflicts)
    plan = p.plan()
    man = c.write_batch(GAME, [], evaluation_version=XC.CROSSCHECK_VERSION, batch=batch or _next_batch(),
                        plan=plan, manifest_extra=XC.batch_manifest(plan["new"]))
    return man, offered


_BATCH = itertools.count(1)


def _next_batch():
    return f"20260914T{next(_BATCH):06d}Z"


def published(tmp_path):
    return ST.read_corpus(str(tmp_path / "crosscheck"), GAME, suffix="crosscheck_v2")


def for_pid(tmp_path, pid=PID):
    return [r for r in published(tmp_path) if r["prediction_id"] == pid]


# ------------------------------------------------------------------ 1. the first run: the exchange is silent
def test_a_first_run_with_no_exchange_record_publishes_a_provisional_observation(tmp_path):
    man, (x,) = run(tmp_path, FakeResults(), now=T1)
    assert man["written"] == 1
    assert x["agreement"] == XC.EXCHANGE_MISSING
    assert x["evidence_tier"] == XC.PROVISIONAL and x["provisional"] is True
    assert x["evaluation_version"].startswith(XC.PROVISIONAL_PREFIX), \
        "an observation that the exchange has not resolved this is not a conclusion and must not claim one"
    assert x["evaluation_version"] != XC.TERMINAL_VERSION


# ------------------------------------------------------------------ 2. the exchange resolves: AGREE
def test_terminal_agreement_arriving_later_is_recorded_without_a_conflict(tmp_path):
    run(tmp_path, FakeResults(), now=T1)
    man, (x,) = run(tmp_path, FakeResults({"T": exch("yes")}), now=T2)
    assert x["agreement"] == XC.AGREE and x["evidence_tier"] == XC.TERMINAL
    assert x["evaluation_version"] == XC.TERMINAL_VERSION
    assert man["written"] == 1, "the truthful terminal reading must be publishable, not refused"
    assert man["by_evidence_tier"] == {XC.TERMINAL: 1}


# ------------------------------------------------------------------ 3. the exchange resolves: DISAGREE
def test_terminal_disagreement_arriving_later_is_recorded_and_stays_a_hard_warning(tmp_path):
    run(tmp_path, FakeResults(), now=T1)
    _man, (x,) = run(tmp_path, FakeResults({"T": exch("no", value="0.0000")}), now=T2)
    assert x["agreement"] == XC.DISAGREE and x["hard_warning"] is True
    assert x["evidence_tier"] == XC.TERMINAL and x["evaluation_version"] == XC.TERMINAL_VERSION
    assert "RESEARCH-QUALITY WARNING" in x["reason"], \
        "the lifecycle must not soften what a disagreement means for every projection priced on that reading"


# ------------------------------------------------------------------ 4. nothing is rewritten or deleted
def test_the_provisional_history_survives_the_terminal_verdict(tmp_path):
    run(tmp_path, FakeResults(), now=T1)                                        # missing
    run(tmp_path, FakeResults({"T": exch("yes", status="determined")}), now=T2)  # non-terminal
    run(tmp_path, FakeResults({"T": exch("yes")}), now=T3)                       # terminal
    rows = for_pid(tmp_path)
    by_agreement = sorted(r["agreement"] for r in rows)
    assert by_agreement == [XC.AGREE, XC.EXCHANGE_MISSING, XC.EXCHANGE_NON_TERMINAL], \
        "every observation stays readable; a later truth is filed BESIDE the earlier one, never over it"
    assert len({r["evaluation_version"] for r in rows}) == 3
    # and the corpus's own verifier still holds: no identity appears twice with different content
    assert ST.verify_batches(str(tmp_path / "crosscheck"), suffix="crosscheck_v2")["ok"]


def test_two_different_provisional_states_are_two_observations_not_a_contradiction(tmp_path):
    run(tmp_path, FakeResults(), now=T1)
    man, (x,) = run(tmp_path, FakeResults({"T": exch("yes", status="determined")}), now=T2)
    assert x["agreement"] == XC.EXCHANGE_NON_TERMINAL and man["written"] == 1
    assert len(for_pid(tmp_path)) == 2


def test_a_terminal_verdict_lands_beside_a_row_published_before_the_lifecycle_existed(tmp_path):
    """The migration case, which is what the next scheduled run actually meets.

    The published corpus holds EXCHANGE_MISSING rows written with no evaluation_version at all -- that is the
    state that produced `existing='EXCHANGE_MISSING' new='AGREE'` on 3420 predictions. Those rows are historical
    observations and are never rewritten, so the terminal verdict must file itself alongside them.
    """
    c = corpus(tmp_path)
    p = c.planner(GAME)
    legacy = XC.crosscheck_rows([settlement_row()], FakeResults())[0]        # exactly what the old code offered
    assert "evaluation_version" not in legacy and legacy["agreement"] == XC.EXCHANGE_MISSING
    p.offer(legacy)
    c.write_batch(GAME, [], evaluation_version=XC.CROSSCHECK_VERSION, batch=_next_batch(), plan=p.plan())

    man, (x,) = run(tmp_path, FakeResults({"T": exch("yes")}), now=T2)
    assert man["written"] == 1 and x["agreement"] == XC.AGREE
    rows = for_pid(tmp_path)
    assert sorted(r["agreement"] for r in rows) == [XC.AGREE, XC.EXCHANGE_MISSING]
    assert any("evaluation_version" not in r for r in rows), "the pre-lifecycle row is left exactly as published"
    assert max(rows, key=XC.rank)["agreement"] == XC.AGREE


# ------------------------------------------------------------------ 5. research picks the authoritative reading
def test_research_selects_the_terminal_reading_over_every_provisional_one(tmp_path):
    run(tmp_path, FakeResults(), now=T1)
    run(tmp_path, FakeResults({"T": exch("yes", status="determined")}), now=T2)
    run(tmp_path, FakeResults({"T": exch("yes")}), now=T3)
    chosen = max(for_pid(tmp_path), key=XC.rank)
    assert chosen["agreement"] == XC.AGREE and chosen["evidence_tier"] == XC.TERMINAL


def test_the_terminal_reading_wins_even_when_a_provisional_one_was_observed_later(tmp_path):
    """Order of arrival must not decide authority: a terminal verdict outranks a provisional observation."""
    terminal = XC.versioned(XC.crosscheck_rows([settlement_row()], FakeResults({"T": exch("yes")}))[0], now=T1)
    later_missing = XC.versioned(XC.crosscheck_rows([settlement_row()], FakeResults())[0], now=T3)
    assert max([later_missing, terminal], key=XC.rank) is terminal


def test_among_provisional_observations_the_later_one_wins(tmp_path):
    first = XC.versioned(XC.crosscheck_rows([settlement_row()], FakeResults())[0], now=T1)
    later = XC.versioned(XC.crosscheck_rows([settlement_row()],
                                            FakeResults({"T": exch("yes", status="determined")}))[0], now=T2)
    assert max([first, later], key=XC.rank) is later


def test_a_row_written_before_the_lifecycle_existed_is_ranked_on_its_substance(tmp_path):
    """Published rows carry no evaluation_version. They are never rewritten, so rank() must read them as they are."""
    legacy_agree = {**XC.crosscheck_one("T", 1.0, "SETTLED", exch("yes")), "prediction_id": PID}
    fresh_missing = XC.versioned(XC.crosscheck_rows([settlement_row()], FakeResults())[0], now=T3)
    assert "evaluation_version" not in legacy_agree
    assert max([fresh_missing, legacy_agree], key=XC.rank) is legacy_agree


# ------------------------------------------------------------------ 6. a real contradiction still fails closed
def test_two_contradictory_terminal_results_still_fail_the_run(tmp_path):
    """The exchange amending a SETTLED result is exactly what the corpus exists to catch. It must still stop."""
    run(tmp_path, FakeResults({"T": exch("yes")}), now=T1)
    with pytest.raises(ST.EvaluationConflict) as e:
        run(tmp_path, FakeResults({"T": exch("no", value="0.0000")}), now=T2)
    (c,) = e.value.conflicts
    assert c["prediction_id"] == PID and c["evaluation_version"] == XC.TERMINAL_VERSION
    assert c["fields"]["agreement"] == (XC.AGREE, XC.DISAGREE)


def test_a_terminal_reading_that_reverses_a_terminal_reading_is_never_silently_replaced(tmp_path):
    run(tmp_path, FakeResults({"T": exch("yes")}), now=T1)
    with pytest.raises(ST.EvaluationConflict):
        run(tmp_path, FakeResults({"T": exch("no", value="0.0000")}), now=T2)
    rows = for_pid(tmp_path)
    assert len(rows) == 1 and rows[0]["agreement"] == XC.AGREE, "nothing was written; the published truth stands"


# ------------------------------------------------------------------ 7. an idle rerun changes nothing
def test_rerunning_against_unchanged_terminal_evidence_is_a_no_op(tmp_path):
    run(tmp_path, FakeResults({"T": exch("yes")}), now=T1)
    man, _ = run(tmp_path, FakeResults({"T": exch("yes")}), now=T2)
    assert man["status"] == "NO_OP" and man["written"] == 0 and man["unchanged"] == 1


def test_rerunning_against_unchanged_missing_evidence_is_a_no_op(tmp_path):
    """The provisional corpus must not grow a row per run while the exchange stays silent."""
    run(tmp_path, FakeResults(), now=T1)
    man, _ = run(tmp_path, FakeResults(), now=T2)
    assert man["status"] == "NO_OP" and man["written"] == 0 and man["unchanged"] == 1
    assert len(for_pid(tmp_path)) == 1


def test_the_evidence_vintage_is_deterministic_and_carries_no_wall_clock():
    a = XC.versioned(XC.crosscheck_rows([settlement_row()], FakeResults())[0], now=T1)
    b = XC.versioned(XC.crosscheck_rows([settlement_row()], FakeResults())[0], now=T3)
    assert a["evaluation_version"] == b["evaluation_version"]
    assert ST.content_hash(a) == ST.content_hash(b), "evaluated_at names when, not what; it is not part of the claim"


# ------------------------------------------------------------------ coverage accounting
def test_provisional_observations_stay_visible_in_coverage_accounting():
    rows = [XC.versioned(XC.crosscheck_rows([settlement_row("a", "A")], FakeResults({"A": exch("yes")}))[0], now=T1),
            XC.versioned(XC.crosscheck_rows([settlement_row("b", "B")], FakeResults())[0], now=T1),
            XC.versioned(XC.crosscheck_rows([settlement_row("c", "C")],
                                            FakeResults({"C": exch("yes", status="determined")}))[0], now=T1)]
    s = XC.summarize(rows)
    assert s["n"] == 3 and s["by_evidence_tier"] == {XC.PROVISIONAL: 2, XC.TERMINAL: 1}
    assert s["provisional"] == 2 and s["terminal"] == 1
    assert s["by_agreement"][XC.EXCHANGE_MISSING] == 1 and s["by_agreement"][XC.EXCHANGE_NON_TERMINAL] == 1, \
        "a ticker the exchange has not resolved is a coverage gap; it must never vanish into the agreement rate"
    assert s["agreement_rate"] == 1.0 and s["comparable"] == 1


def test_a_legacy_row_without_a_tier_is_still_counted_by_substance():
    s = XC.summarize([XC.crosscheck_one("T", 1.0, "SETTLED", None)])
    assert s["by_evidence_tier"] == {XC.PROVISIONAL: 1}


# ------------------------------------------------------------------ the comparison rule itself is unchanged
def test_the_lifecycle_changes_no_settlement_semantics():
    """Every verdict crosscheck_one reaches is the verdict it reached before; only its filing changed."""
    cases = [(exch("yes"), 1.0, XC.AGREE), (exch("no", value="0.0000"), 1.0, XC.DISAGREE),
             (exch("yes", status="determined"), 1.0, XC.EXCHANGE_NON_TERMINAL), (None, 1.0, XC.EXCHANGE_MISSING),
             (exch("yes"), None, XC.DERIVED_MISSING)]
    for rec, derived, want in cases:
        row = XC.crosscheck_one("T", derived, "SETTLED", rec)
        assert row["agreement"] == want
        assert XC.versioned(row, now=T1)["agreement"] == want, "versioning is filing, never a re-judgement"
        assert row["derived_settled_yes"] == derived, "the derived football settlement is never touched"
