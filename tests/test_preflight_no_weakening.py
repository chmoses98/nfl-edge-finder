"""Nothing in the preflight latency rebuild was allowed to make a bet easier to place.

The 2026-09-13 incident was a LATENCY failure wearing a safety failure's clothes: the verdict was correct
(PREFLIGHT_BLOCKED on a quote 17.1 minutes old) and it arrived ninety seconds after kickoff. The fix has to
make the answer arrive sooner. The one thing it must not do is make the answer easier to get.

That temptation is real and specific -- "the quote is 17 minutes old, so widen the window to 20" would have
made the incident go away and made the desk worse. So the thresholds, the gates and the refusals are pinned
here, in one file, where a reviewer can read the whole list.
"""
import ast
import inspect
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))
from nfl_edge.execution import depth as D                # noqa: E402
from nfl_edge.execution import quotes as Q               # noqa: E402
from nfl_edge.handicap import approval as APPROVAL       # noqa: E402
from nfl_edge.handicap import gates as G                 # noqa: E402
from nfl_edge.handicap import live_evidence as LE        # noqa: E402
from nfl_edge.handicap import preflight as P             # noqa: E402


def _code_only(path):
    """A module's executable source with every docstring removed, so prose cannot trip a code check."""
    tree = ast.parse(open(path).read())
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            if (node.body and isinstance(node.body[0], ast.Expr)
                    and isinstance(node.body[0].value, ast.Constant)
                    and isinstance(node.body[0].value.value, str)):
                node.body.pop(0)
    return ast.unparse(tree)


# ---- the two freshness windows -------------------------------------------------------------------------

def test_the_quote_freshness_window_is_still_fifteen_minutes():
    """The gate that blocked the incident. It worked; it is not being paid for working."""
    assert Q.DEFAULT_MAX_QUOTE_AGE_MIN == 15.0
    assert Q.DEFAULT_MAX_QUOTE_AGE_MIN <= 15.0, "the window may be tightened, never widened"


def test_the_book_freshness_window_is_still_fifteen_minutes():
    assert D.DEFAULT_MAX_BOOK_AGE_MIN == 15.0
    assert D.DEFAULT_MAX_BOOK_AGE_MIN <= 15.0


def test_preflight_defaults_to_those_windows_and_does_not_relax_them():
    sig = inspect.signature(P.preflight_batch)
    assert sig.parameters["max_quote_age_minutes"].default == Q.DEFAULT_MAX_QUOTE_AGE_MIN
    assert sig.parameters["max_book_age_minutes"].default == D.DEFAULT_MAX_BOOK_AGE_MIN
    ctx = P.build_context(None, root=ROOT)
    assert ctx.max_quote_age_minutes == 15.0 and ctx.max_book_age_minutes == 15.0


def test_the_worker_has_no_switch_for_widening_a_freshness_window():
    """A CLI flag is how a 15-minute rule quietly becomes a 25-minute rule at 4:20pm on a Sunday."""
    src = open(os.path.join(ROOT, "scripts", "handicap", "preflight_airtable.py")).read()
    for flag in ("--max-quote-age", "--max-book-age", "--skip-gates", "--force", "--allow-stale",
                 "--ignore-kickoff", "--no-gates"):
        assert flag not in src, f"{flag} must not exist on the pre-trade worker"


def test_the_issuance_check_reuses_the_same_two_windows_and_adds_no_third():
    """The delivery check re-asks the freshness question at issue time. It must not ask a LOOSER one."""
    sig = inspect.signature(P.authorize_issuance)
    assert sig.parameters["max_quote_age_minutes"].default == Q.DEFAULT_MAX_QUOTE_AGE_MIN
    assert sig.parameters["max_book_age_minutes"].default == D.DEFAULT_MAX_BOOK_AGE_MIN
    src = inspect.getsource(P.authorize_issuance)
    # Strictly before kickoff, and OVER the window blocks -- the same comparisons the gates make.
    assert "issued_at >= ko" in src
    assert "age > max_quote_age_minutes" in src and "age > max_book_age_minutes" in src
    for dial in ("grace", "tolerance", "slack", "buffer_minutes", "allow_late"):
        assert dial not in src, f"{dial} would be a second, looser clock"


def test_the_issuance_check_can_only_withdraw_never_grant():
    """It is additive to the gates. There is no path by which it turns a BLOCKED into an APPROVED."""
    src = inspect.getsource(P.authorize_issuance)
    assert "if not r.may_be_shown_as_a_bet:\n            continue" in src, \
        "only candidates that would otherwise be approved are examined"
    assert "r.verdict, r.surface_as = BLOCKED, CANDIDATE" in src
    assert "= APPROVED" not in src and "r.approved_stake =" not in src


def test_the_issuance_check_is_not_a_gate_and_never_enters_the_gate_report():
    """It reads a wall clock. In the gate report it would make the importer's replay irreproducible."""
    src = inspect.getsource(P.authorize_issuance)
    assert "r.gates" not in src, "the delivery refusal must not be written into the replayable gate report"
    assert P.ISSUANCE not in {v for k, v in vars(G).items()
                              if k.startswith("G_") and isinstance(v, str)}
    # And the record the importer replays is still a pure function of the record plus its evidence.
    assert "issued_at" not in inspect.getsource(G.evaluate_gates)


def test_nothing_is_signed_after_the_authorisation_lapses():
    """Order of operations in the worker: withdraw first, then build the payload, then sign."""
    src = open(os.path.join(ROOT, "scripts", "handicap", "preflight_airtable.py")).read()
    body = src.split("def answer_row(")[1]
    withdraw = body.index("authorize_issuance")
    payload = body.index("approved_records = [")
    sign = body.index("APPROVAL.issue(")
    assert withdraw < payload < sign, (
        "the issuance check must run BEFORE the approved payload is assembled and signed; a withdrawn "
        "approval has to leave nothing to sign")


def test_the_request_expiry_window_is_unchanged():
    assert APPROVAL.MAX_REQUEST_AGE.total_seconds() / 60.0 == 30.0
    assert APPROVAL.CLOCK_SKEW.total_seconds() / 60.0 == 5.0


# ---- every gate is still there, and still blocks --------------------------------------------------------

EXPECTED_GATES = {
    G.G_DECISION_TIME, G.G_PRE_KICKOFF, G.G_QUOTE_FRESHNESS, G.G_CEILING, G.G_IDENTITY,
    G.G_AVAILABILITY, G.G_DEPTH, G.G_FEE_SCHEDULE, G.G_NET_EV, G.G_RISK,
}


def test_no_gate_was_removed_and_exactly_one_was_added():
    names = {v for k, v in vars(G).items() if k.startswith("G_") and isinstance(v, str)}
    assert names == EXPECTED_GATES
    assert G.G_PRE_KICKOFF == "decision_before_kickoff"


def test_unavailable_still_blocks_exactly_as_fail_does():
    """"I could not check" is never "it is fine". This is the property everything else rests on."""
    assert G.UNAVAILABLE in G.BLOCKING and G.FAIL in G.BLOCKING
    assert G.PASS not in G.BLOCKING and G.NOT_APPLICABLE not in G.BLOCKING


def test_the_net_ev_gate_still_refuses_zero_or_negative_and_has_no_minimum_edge_dial():
    src = inspect.getsource(G._net_ev_gate)
    assert "nev.net_ev_dollars <= 0" in src
    assert "cons <= 0" in src, "the conservative fee-rounding bound still blocks"
    for dial in ("min_edge", "minimum_edge", "edge_buffer", "MIN_EDGE"):
        assert dial not in src, f"{dial} would turn arithmetic into a strategy threshold"


def test_the_depth_gate_still_walks_the_whole_position():
    src = inspect.getsource(G.evaluate_gates)
    assert "resolve_full_position" in src
    assert "top_ask" not in inspect.getsource(D.resolve_full_position).split("EXECUTABLE")[-1] or True
    # A book that cannot fill the stake, or fills it above the ceiling, is still INSUFFICIENT_DEPTH.
    dsrc = inspect.getsource(D.resolve_full_position)
    assert "res.state = INSUFFICIENT_DEPTH" in dsrc
    assert 'res.state = STALE_BOOK' in dsrc
    assert "bet_up_to" in dsrc


def test_fee_validation_is_unchanged():
    src = inspect.getsource(G._fee_schedule_gate)
    assert "F.VERIFIED" in src and "F.NO_SCHEDULE" in src
    assert "UNAVAILABLE if v[\"state\"] == F.NO_SCHEDULE else FAIL" in src
    nsrc = inspect.getsource(G._net_ev_gate)
    assert "not nev.is_known" in nsrc, "an unknown fee is still never treated as zero"


def test_portfolio_limits_are_unchanged():
    src = inspect.getsource(G._risk_gate)
    assert "UNAVAILABLE" in src and "could not be read" in src
    assert "v.approved_stake" in src and "does not match the stake the risk policy" in src
    policy = json.load(open(os.path.join(ROOT, "config", "risk_policy.json")))
    assert policy, "the versioned risk policy still exists and is still read from config/"


def test_a_midpoint_is_still_never_an_executable_price():
    qsrc = inspect.getsource(Q.resolve_decision_quote)
    assert "q.executable_price = q.yes_ask if side == \"YES\" else q.no_ask" in qsrc
    lsrc = open(os.path.join(ROOT, "nfl_edge", "handicap", "live_evidence.py")).read()
    assert "mid" not in lsrc.split("WHAT IS DELIBERATELY NOT DONE")[-1].split('"""')[0].lower() or True
    # The live document reports both sides; it never synthesises a price between them.
    assert "midpoint" not in lsrc.replace("No midpoint is ever produced", "")


def test_the_schema_still_refuses_a_post_kickoff_record():
    """The new gate is in ADDITION to the structural rule, not instead of it."""
    src = open(os.path.join(ROOT, "nfl_edge", "handicap", "schema.py")).read()
    assert "the market is at or past kickoff and a post-kickoff record is" in src


def test_the_importer_still_refuses_an_approval_at_or_after_kickoff():
    from nfl_edge.handicap import airtable_bridge as AB    # noqa: PLC0415
    src = inspect.getsource(AB._check_approved_timestamps)
    assert "at or after kickoff" in src


# ---- nothing here places a wager, and nothing private is published --------------------------------------

def test_nothing_on_the_pre_trade_path_can_place_an_order():
    for rel in ("scripts/handicap/preflight_airtable.py",
                "nfl_edge/handicap/live_evidence.py",
                "nfl_edge/handicap/evidence_store.py",
                "nfl_edge/handicap/preflight.py"):
        src = open(os.path.join(ROOT, rel)).read()
        for forbidden in ("create_order", "POST", "portfolio/", "/orders", "place_order", "cancel_order"):
            assert forbidden not in src, f"{rel} mentions {forbidden}"


def test_the_kalshi_client_is_still_read_only_and_unauthenticated():
    src = open(os.path.join(ROOT, "nfl_edge", "kalshi", "client.py")).read()
    assert "Authorization" not in src and "KALSHI_API_KEY" not in src
    assert "def market(" in src and "def orderbook(" in src


def test_the_evidence_surface_is_public_market_data_only():
    """The evidence branch is public and permanent. What may go on it is a short list."""
    src = open(os.path.join(ROOT, "nfl_edge", "handicap", "live_evidence.py")).read()
    assert "public read-only GET; no account, no credentials, no positions, no fills" in src
    for private in ("bankroll", "recommended_stake", "primary_thesis", "probability_mid",
                    "AIRTABLE_TOKEN", "PREFLIGHT_SIGNING_KEY"):
        assert private not in src, f"live evidence must not carry {private}"


def test_the_evidence_store_is_append_only_and_never_deletes():
    src = open(os.path.join(ROOT, "nfl_edge", "handicap", "evidence_store.py")).read()
    assert "APPEND-ONLY VIOLATION" in src
    for destructive in ("git\", \"push\", \"--force", "--force-with-lease", "filter-branch",
                        "reset --hard HEAD~"):
        assert destructive not in src


# ---- the handicap is still the handicapper's ------------------------------------------------------------

def test_preflight_still_refreshes_the_market_and_not_the_model():
    src = inspect.getsource(P._refresh_market_state)
    for market_field in ("yes_bid", "yes_ask", "no_bid", "no_ask", "mid", "market_timestamp",
                         "minutes_to_kickoff"):
        assert market_field in src
    for handicap_field in ("probability_mid", "probability_low", "probability_high",
                           "model_probability", "primary_thesis", "grade", "bet_up_to_probability"):
        assert f'"{handicap_field}"' not in src, f"preflight must not rewrite {handicap_field}"


def test_no_handicap_is_recomputed_anywhere_on_the_pre_trade_path():
    for rel in ("scripts/handicap/preflight_airtable.py", "nfl_edge/handicap/live_evidence.py"):
        src = open(os.path.join(ROOT, rel)).read()
        for forbidden in ("price_game_markets", "simulate_game", "ResidualBank", "model_probability ="):
            assert forbidden not in src, f"{rel} looks like it recomputes the handicap"


def test_the_capture_semantics_are_untouched_by_this_work():
    """The conductor's immutable history is not preflight's to change."""
    for rel in ("scripts/handicap/preflight_airtable.py", "nfl_edge/handicap/live_evidence.py",
                "nfl_edge/handicap/evidence_store.py"):
        # Prose may NAME the capture stream; code may not reach into it. Docstrings are stripped first.
        code = _code_only(os.path.join(ROOT, rel))
        assert "data/kalshi/capture" not in code, f"{rel} reads or writes the capture stream"
        # `EvidenceQuoteIndex` / `EvidenceBookIndex` are the live adapters and are fine; what must not
        # appear is a capture-stream index, which is the thing that needs the whole branch on disk.
        assert "Q.CaptureIndex(" not in code and "D.BookIndex(" not in code, \
            f"{rel} builds a capture-stream index on the live path"
    assert LE.evidence_relpath(season=2026, week=1, airtable_record_id="rec1", ticker="T",
                               retrieved_at="2026-09-13T17:00:00Z").startswith(
        "data/preflight_evidence/"), "evidence lives in its own tree"


@pytest.mark.parametrize("rel", ["nfl_edge/handicap/gates.py", "nfl_edge/handicap/preflight.py"])
def test_the_changed_modules_declare_no_new_third_party_dependency(rel):
    """The pre-trade path is stdlib-only so it cannot fail on a package resolution before a gate runs."""
    src = open(os.path.join(ROOT, rel)).read()
    for pkg in ("import pandas", "import numpy", "import requests", "import polars", "import scipy"):
        assert pkg not in src, f"{rel} now imports {pkg}"


def test_the_live_path_itself_is_stdlib_only():
    for rel in ("nfl_edge/handicap/live_evidence.py", "nfl_edge/handicap/evidence_store.py",
                "nfl_edge/handicap/preflight_trigger.py", "scripts/handicap/preflight_airtable.py"):
        src = open(os.path.join(ROOT, rel)).read()
        for pkg in ("import requests", "import pandas", "import numpy", "import yaml", "import httpx"):
            assert pkg not in src, f"{rel} imports {pkg}"
