"""The pre-trade control has to be reachable from the interface that produces the recommendation.

`preflight_candidate.py` was the right check behind the wrong door. ChatGPT is what produces a candidate,
and in its runtime it can write Airtable and read GitHub -- it cannot run a script, clone a branch, or
dispatch a workflow. "ChatGPT runs preflight_candidate.py" was therefore a documented intention, and a
control the recommending interface cannot reach protects nothing.

    ChatGPT -> PREFLIGHT_REQUESTED row -> [Airtable Automation] -> workflow_dispatch
            -> this worker -> PREFLIGHT_APPROVED / PREFLIGHT_BLOCKED -> ChatGPT reads it

These tests cover the repository side of that leg end to end against a fake Airtable, including the
TEST_ONLY connectivity path. The Automation itself is a one-time owner setup and is documented, not
simulated: this file pins that the row NEVER lands in an approved state by accident, which is the property
that makes the missing half safe to be missing.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))
from nfl_edge.handicap import airtable_bridge as AB       # noqa: E402
from nfl_edge.handicap import gates as G                  # noqa: E402
from nfl_edge.handicap import preflight as P              # noqa: E402
from nfl_edge.handicap import risk as R                   # noqa: E402
from nfl_edge.handicap import schema as S                 # noqa: E402

import preflight_airtable as W                            # noqa: E402
from test_preflight import candidate, ledger, market_data  # noqa: E402,F401

NOW = datetime(2026, 9, 9, 13, 5, tzinfo=timezone.utc)


class FakeAirtable:
    """Records every request. Never a network."""

    def __init__(self, rows, *, fail_list=False, fail_write=False):
        self.rows = rows
        self.fail_list, self.fail_write = fail_list, fail_write
        self.written, self.request_count = {}, 0

    def list_by_status(self, status, sport=AB.SPORT_NFL):
        self.request_count += 1
        if self.fail_list:
            raise AB.TransientError("Airtable unreachable")
        return [r for r in self.rows
                if (r.get("fields") or {}).get(AB.F_STATUS) == status
                and (r.get("fields") or {}).get(AB.F_SPORT) == sport]

    def write_fields(self, updates, **kw):
        self.request_count += 1
        if self.fail_write:
            raise AB.TransientError("Airtable write failed")
        for rid, fields in updates.items():
            self.written.setdefault(rid, {}).update(fields)


def row(candidates, rid="recPF0000000001", status=AB.STATUS_PREFLIGHT_REQUESTED, run_id="20260909T130000Z"):
    return {"id": rid, "createdTime": NOW.isoformat(),
            "fields": {AB.F_SPORT: AB.SPORT_NFL, AB.F_STATUS: status, AB.F_RUN_ID: run_id,
                       AB.F_PAYLOAD: json.dumps(candidates)}}


def go(tmp_path, rows, *, md=None, led=None, **kw):
    fake = FakeAirtable(rows)
    code = W.run(fake, market_data_root=md or market_data(tmp_path),
                 ledger_root=led or ledger(tmp_path), now=NOW, **kw)
    return code, fake


def result_of(fake, rid="recPF0000000001"):
    return json.loads(fake.written[rid][AB.F_PREFLIGHT_RESULT])


# ---- the happy path ----------------------------------------------------------------------------------

def test_a_sound_candidate_comes_back_approved(tmp_path):
    code, fake = go(tmp_path, [row([candidate()])])
    assert code == 0
    assert fake.written["recPF0000000001"][AB.F_STATUS] == AB.STATUS_PREFLIGHT_APPROVED
    body = result_of(fake)
    assert body["verdict"] == "APPROVED" and body["n_approved"] == 1
    c = body["candidates"][0]
    assert c["may_be_shown_as_a_bet"] is True
    assert c["approved_stake"] == 10
    assert c["surface_as"] == S.RECOMMENDED
    assert c["approval_as_of"] == NOW.isoformat(), "the decision timestamp is the APPROVAL time"
    assert c["candidate_created_at"] == candidate()["created_at"], "the draft time is kept as lineage"


def test_the_answer_carries_what_the_owner_needs_to_act_on(tmp_path):
    _code, fake = go(tmp_path, [row([candidate()])])
    c = result_of(fake)["candidates"][0]
    for field in ("executable_price", "full_position_vwap", "worst_fill_price",
                  "net_ev_dollars", "conservative_net_ev_dollars", "gates"):
        assert c[field] is not None, f"the verdict must carry {field}"
    assert "may be surfaced as a BET" in result_of(fake)["note"]


def test_the_approved_stake_is_the_policy_stake_not_the_proposal(tmp_path):
    _code, fake = go(tmp_path, [row([candidate(proposed_stake=50, recommended_stake=50)])])
    c = result_of(fake)["candidates"][0]
    assert c["proposed_stake"] == 50 and c["approved_stake"] == 20


# ---- blocked is an ANSWER, and it is not an approval --------------------------------------------------

def test_a_thin_book_comes_back_blocked_with_reasons(tmp_path):
    md = market_data(tmp_path, ladder=[(0.56, 2.0)])
    code, fake = go(tmp_path, [row([candidate(proposed_stake=50, recommended_stake=50)])], md=md)
    assert code == 0, "a blocked candidate is the pipeline working, not a failure"
    assert fake.written["recPF0000000001"][AB.F_STATUS] == AB.STATUS_PREFLIGHT_BLOCKED
    body = result_of(fake)
    assert body["verdict"] == "BLOCKED" and body["n_approved"] == 0
    assert body["candidates"][0]["blocking_reasons"]


def test_one_blocked_candidate_blocks_the_row_but_keeps_the_others_verdicts(tmp_path):
    good = candidate(recommendation_id="rec_pf0000000000000001")
    bad = candidate(recommendation_id="rec_pf0000000000000002", probability_mid=0.5601,
                    probability_low=0.56, probability_high=0.57)
    _code, fake = go(tmp_path, [row([good, bad])])
    body = result_of(fake)
    assert body["verdict"] == "BLOCKED", "the ROW is approved only if every candidate is"
    by_id = {c["recommendation_id"]: c for c in body["candidates"]}
    assert by_id["rec_pf0000000000000001"]["may_be_shown_as_a_bet"] is True
    assert by_id["rec_pf0000000000000002"]["may_be_shown_as_a_bet"] is False


def test_an_unusable_payload_is_an_error_never_an_approval(tmp_path):
    bad = row([])
    bad["fields"][AB.F_PAYLOAD] = "{not json"
    code, fake = go(tmp_path, [bad])
    assert code == 1
    assert fake.written["recPF0000000001"][AB.F_STATUS] == AB.STATUS_PREFLIGHT_ERROR
    assert result_of(fake)["verdict"] == "ERROR"
    assert "NOT an approval" in result_of(fake)["note"]


# ---- silence is never yes ------------------------------------------------------------------------------

def test_an_unreachable_airtable_leaves_the_row_unanswered(tmp_path):
    fake = FakeAirtable([row([candidate()])], fail_list=True)
    code = W.run(fake, market_data_root=market_data(tmp_path), ledger_root=ledger(tmp_path), now=NOW)
    assert code == 3 and fake.written == {}, "an unanswered request stays REQUESTED, which is not approved"


def test_a_failed_writeback_leaves_the_row_unanswered(tmp_path):
    fake = FakeAirtable([row([candidate()])], fail_write=True)
    code = W.run(fake, market_data_root=market_data(tmp_path), ledger_root=ledger(tmp_path), now=NOW)
    assert code == 3, "a verdict that never reached Airtable has not been delivered"


def test_only_preflight_requested_rows_are_touched(tmp_path):
    others = [row([candidate()], rid=f"rec{st}", status=st)
              for st in (AB.STATUS_READY, AB.STATUS_SYNCED, AB.STATUS_PREFLIGHT_APPROVED,
                         AB.STATUS_PREFLIGHT_BLOCKED, AB.STATUS_TEST_ONLY)]
    code, fake = go(tmp_path, others)
    assert code == 0 and fake.written == {}
    assert "nothing to preflight" not in "" and len(fake.rows) == 5


def test_a_dry_run_answers_nothing(tmp_path):
    code, fake = go(tmp_path, [row([candidate()])], update_status=False)
    assert code == 0 and fake.written == {}


# ---- the payload is provenance and is never rewritten --------------------------------------------------

def test_the_worker_can_only_write_status_and_its_own_result_field():
    client = AB.AirtableClient("tok", "base", "table", opener=lambda *a, **k: None)
    with pytest.raises(AB.BridgeError) as e:
        client.write_fields({"rec1": {AB.F_PAYLOAD: "rewritten"}})
    assert "provenance" in str(e.value)
    with pytest.raises(AB.BridgeError):
        client.write_fields({"rec1": {AB.F_RUN_ID: "different"}})


def test_the_importer_still_writes_status_and_nothing_else():
    """The archival leg's invariant survives the new field."""
    import inspect                                                  # noqa: PLC0415
    src = inspect.getsource(AB.AirtableClient.set_status)
    assert "allowed={F_STATUS}" in src


# ---- the two transports stay separate ------------------------------------------------------------------

def test_the_archival_cadence_is_untouched():
    """The pre-trade leg exists so the twelve-hourly leg does not have to become a safety control."""
    import yaml                                                     # noqa: PLC0415
    sync = yaml.safe_load(open(os.path.join(ROOT, ".github/workflows/sync-handicap-airtable.yml")))
    crons = [c["cron"] for c in sync[True]["schedule"]]
    assert crons == ["23 */12 * 9-12,1-2 *"], "the archival cadence must not have been sped up"

    pre = yaml.safe_load(open(os.path.join(ROOT, ".github/workflows/preflight.yml")))
    assert "schedule" not in pre[True], "the pre-trade leg is event-driven; a cron here would be polling"
    assert "workflow_dispatch" in pre[True] and "repository_dispatch" in pre[True]
    assert pre["permissions"]["contents"] == "read", "preflight never writes a branch"


def test_the_preflight_workflow_reads_both_branches_it_needs():
    import yaml                                                     # noqa: PLC0415
    wf = yaml.safe_load(open(os.path.join(ROOT, ".github/workflows/preflight.yml")))
    refs = [s.get("with", {}).get("ref") for s in wf["jobs"]["preflight"]["steps"]]
    assert "market-data" in refs, "the quote and depth gates need the capture stream"
    assert "handicap-data" in refs, "cumulative exposure needs the committed ledger"


def test_the_worker_does_not_reimplement_preflight():
    """Transport carries the answer. It does not compute one.

    Scanned over the executable code with docstrings stripped, so prose that NAMES the gate module does not
    read as a call into it.
    """
    import ast                                                      # noqa: PLC0415
    import inspect                                                  # noqa: PLC0415

    tree = ast.parse(inspect.getsource(W))
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body.pop(0)
    code = ast.unparse(tree)

    assert "preflight_batch" in code, "the worker must delegate to the shared preflight module"
    # RELAYING a gate's number is transport. COMPUTING or COMPARING one is a decision, and there is exactly
    # one place those are allowed to happen.
    for smell in ("evaluate_gates", "max_exposure_per", "walk_book", "resolve_decision_quote",
                  "rounding_uncertainty", "net_ev_dollars <", "net_ev_dollars >",
                  "GateContext", "RiskPolicy("):
        assert smell not in code, f"{smell!r} looks like a decision made in the transport layer"

    # The only verdict the worker forms is a restatement of `may_be_shown_as_a_bet`, which preflight set.
    assert "may_be_shown_as_a_bet" in code
    assert code.count("PREFLIGHT_APPROVED") == 1, \
        "there must be exactly one place a row can become approved"


# ---- TEST_ONLY end to end ------------------------------------------------------------------------------

def test_a_test_only_candidate_round_trips_without_touching_a_live_market(tmp_path):
    """The connectivity check: the whole leg runs, and the verdict is an honest NOT-A-BET.

    A TEST_ONLY record risks no capital and is excluded from every report, so the situational gates do not
    apply to it -- which is exactly what makes it usable as an E2E probe against a ticker that does not
    exist. It must never come back approved.
    """
    probe = candidate(recommendation_id="rec_test000000000001", test_only=True,
                      market_ticker="KXNFLGAME-99DEC31TSTTST-TST")
    code, fake = go(tmp_path, [row([probe], run_id="E2E-PREFLIGHT")], md=str(tmp_path / "empty-md"))
    assert code == 0
    body = result_of(fake)
    assert body["run_id"] == "E2E-PREFLIGHT"
    assert body["candidates"][0]["may_be_shown_as_a_bet"] is False
    assert fake.written["recPF0000000001"][AB.F_STATUS] == AB.STATUS_PREFLIGHT_BLOCKED


# ---- approval time, not draft time -------------------------------------------------------------------
#
# A candidate drafted at 13:00 and preflighted at 13:30 is not a 13:00 decision. Approving it as one is an
# AUDIT of an opportunity that may no longer exist, delivered as though it were a live instruction.

DRAFT = datetime(2026, 9, 9, 13, 0, tzinfo=timezone.utc)


def at(minutes):
    return DRAFT + timedelta(minutes=minutes)


def go_at(tmp_path, rows, minutes, **kw):
    fake = FakeAirtable(rows)
    code = W.run(fake, market_data_root=kw.pop("md", None) or market_data(tmp_path),
                 ledger_root=kw.pop("led", None) or ledger(tmp_path), now=at(minutes), **kw)
    return code, fake


def test_A_an_immediate_request_may_be_approved(tmp_path):
    code, fake = go_at(tmp_path, [row([candidate()])], 2)
    assert code == 0
    assert fake.written["recPF0000000001"][AB.F_STATUS] == AB.STATUS_PREFLIGHT_APPROVED
    c = result_of(fake)["candidates"][0]
    assert c["approval_as_of"] == at(2).isoformat()
    assert c["request_age_minutes"] == pytest.approx(2.0)


def test_B_a_request_delayed_past_its_window_expires(tmp_path):
    code, fake = go_at(tmp_path, [row([candidate()])], 90)
    assert code == 0, "an expired request is an answer, not a pipeline failure"
    assert fake.written["recPF0000000001"][AB.F_STATUS] == AB.STATUS_PREFLIGHT_BLOCKED
    body = result_of(fake)
    assert body["verdict"] == "EXPIRED"
    c = body["candidates"][0]
    assert c["verdict"] == P.EXPIRED and c["may_be_shown_as_a_bet"] is False
    assert any("Submit a fresh request" in b for b in c["blocking_reasons"])
    assert AB.F_APPROVED_PAYLOAD not in fake.written["recPF0000000001"], \
        "an expired request produces no approved payload to archive"


def test_C_the_market_state_used_is_the_one_at_approval_not_at_draft(tmp_path):
    """Two captures: 0.56 near the draft, 0.58 just before approval. The approved record must say 0.58."""
    md = market_data(tmp_path, ask=0.56, minutes_before=4.0)
    market_data(tmp_path, ask=0.58, minutes_before=-18.0, name="md")   # 18 min AFTER the draft
    code, fake = go_at(tmp_path, [row([candidate()])], 20, md=md)
    assert code == 0
    approved = json.loads(fake.written["recPF0000000001"][AB.F_APPROVED_PAYLOAD])[0]
    assert approved["yes_ask"] == pytest.approx(0.58), "the record must carry the approval-time ask"
    assert approved["created_at"] == at(20).isoformat()
    assert approved["candidate_created_at"] == DRAFT.isoformat()
    assert approved["minutes_to_kickoff"] < candidate()["minutes_to_kickoff"], \
        "time to kickoff is recomputed at approval"


def test_D_a_worse_current_ask_above_the_ceiling_blocks(tmp_path):
    """The candidate's ceiling is 0.59. If the market has moved to 0.61 by approval time, it is not a bet."""
    md = market_data(tmp_path, ask=0.56, minutes_before=4.0)
    market_data(tmp_path, ask=0.61, minutes_before=-18.0, name="md",
                ladder=[(0.61, 100000.0)])
    code, fake = go_at(tmp_path, [row([candidate()])], 20, md=md)
    assert code == 0
    assert fake.written["recPF0000000001"][AB.F_STATUS] == AB.STATUS_PREFLIGHT_BLOCKED
    c = result_of(fake)["candidates"][0]
    assert c["may_be_shown_as_a_bet"] is False
    assert any("NOT ACTIONABLE" in b or "ceiling" in b or "bet_up_to" in b
               for b in c["blocking_reasons"]), c["blocking_reasons"]


def test_E_depth_that_thinned_out_by_approval_time_blocks(tmp_path):
    md = market_data(tmp_path, ask=0.56, minutes_before=4.0)
    market_data(tmp_path, ask=0.56, minutes_before=-18.0, name="md", ladder=[(0.56, 2.0)])
    code, fake = go_at(tmp_path, [row([candidate(proposed_stake=50, recommended_stake=50)])], 20, md=md)
    assert code == 0
    c = result_of(fake)["candidates"][0]
    assert c["may_be_shown_as_a_bet"] is False
    assert any("full_position_executable" in b or "absorb only" in b for b in c["blocking_reasons"]), \
        c["blocking_reasons"]


def test_F_an_improved_market_is_recorded_at_the_approval_price(tmp_path):
    """A better price is fine. What is not fine is a record that claims the price it was drafted at."""
    md = market_data(tmp_path, ask=0.56, minutes_before=4.0)
    market_data(tmp_path, ask=0.54, minutes_before=-18.0, name="md")
    code, fake = go_at(tmp_path, [row([candidate()])], 20, md=md)
    assert code == 0
    approved = json.loads(fake.written["recPF0000000001"][AB.F_APPROVED_PAYLOAD])[0]
    assert approved["yes_ask"] == pytest.approx(0.54)
    assert approved["yes_ask"] != candidate()["yes_ask"]


def test_G_the_delayed_archival_replay_reproduces_the_approval(tmp_path):
    """The importer replays the APPROVED record at ITS created_at -- which is the approval time."""
    md, led = market_data(tmp_path), ledger(tmp_path)
    _code, fake = go_at(tmp_path, [row([candidate()])], 2, md=md, led=led)
    approved = json.loads(fake.written["recPF0000000001"][AB.F_APPROVED_PAYLOAD])

    report = R.report_for_batch(approved, R.RiskPolicy.load(ROOT), led)
    ctx = P.build_context(md, root=ROOT, risk_report=report)
    replayed = G.evaluate_gates(approved[0], ctx)
    assert replayed.overall == G.PASS
    assert replayed.as_of == at(2).isoformat(), "the replay judges at the approval timestamp"
    assert replayed.decision_quote["executable_price"] == pytest.approx(
        result_of(fake)["candidates"][0]["executable_price"])


def test_the_handicap_is_carried_forward_untouched(tmp_path):
    """The MARKET is re-priced at approval. The model's opinion is not recomputed."""
    _code, fake = go_at(tmp_path, [row([candidate()])], 2)
    approved = json.loads(fake.written["recPF0000000001"][AB.F_APPROVED_PAYLOAD])[0]
    src = candidate()
    for field in ("probability_low", "probability_mid", "probability_high", "model_probability",
                  "model_version", "grade", "bet_up_to_probability", "primary_thesis", "artifact_hash"):
        assert approved[field] == src[field], f"{field} must not move between draft and approval"


# ---- the approved payload is bound to the approval ----------------------------------------------------

def test_A_the_approved_payload_carries_the_capped_stake(tmp_path):
    _code, fake = go_at(tmp_path, [row([candidate(proposed_stake=50, recommended_stake=50)])], 2)
    approved = json.loads(fake.written["recPF0000000001"][AB.F_APPROVED_PAYLOAD])[0]
    assert approved["recommended_stake"] == 20, "grade A caps at 2u = $20"
    assert approved["proposed_stake"] == 50, "what was wanted is preserved beside what was approved"


def test_B_the_original_payload_is_never_rewritten(tmp_path):
    original = row([candidate(proposed_stake=50, recommended_stake=50)])
    before = original["fields"][AB.F_PAYLOAD]
    _code, fake = go_at(tmp_path, [original], 2)
    assert AB.F_PAYLOAD not in fake.written["recPF0000000001"], "the request is provenance"
    assert original["fields"][AB.F_PAYLOAD] == before


def test_the_result_hashes_both_payloads(tmp_path):
    _code, fake = go_at(tmp_path, [row([candidate()])], 2)
    written = fake.written["recPF0000000001"]
    body = json.loads(written[AB.F_PREFLIGHT_RESULT])
    assert body["approved_payload_sha256"] == AB.payload_sha(written[AB.F_APPROVED_PAYLOAD])
    assert body["candidate_payload_sha256"]
    assert body["candidate_payload_sha256"] != body["approved_payload_sha256"], \
        "the approved batch is not the candidate batch"
    assert body["airtable_record_id"] == "recPF0000000001"
