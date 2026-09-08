"""A tripwire over the corrections that have already been reviewed and accepted.

Each of these is pinned in detail somewhere else. This file exists because the last four changes reached
into every one of those modules -- the gate context, the fee engine, the risk policy, the evaluation
arithmetic -- and a refactor that quietly undid an accepted correction would otherwise show up as a subtly
wrong number months later rather than as a red build now.

It is deliberately structural and cheap: does the property still EXIST, in the place the review put it.
The behavioural proofs live in test_decision_time_gates, test_decision_quotes, test_depth, test_fees,
test_multi_fill_accounting, test_gates_and_risk, test_airtable_bridge, test_append_only_guard and
test_h019_preserved.
"""
import inspect
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.execution import depth as D       # noqa: E402
from nfl_edge.execution import fees as F        # noqa: E402
from nfl_edge.execution import quotes as Q      # noqa: E402
from nfl_edge.handicap import evaluate as E     # noqa: E402
from nfl_edge.handicap import gates as G        # noqa: E402
from nfl_edge.handicap import preflight as P    # noqa: E402
from nfl_edge.handicap import risk as R         # noqa: E402
from nfl_edge.handicap import schema as S       # noqa: E402

AS_OF = datetime(2026, 9, 9, 13, 0, tzinfo=timezone.utc)


# ---- 1-2. the clock is the decision, and later evidence is invisible ---------------------------------

def test_no_gate_context_carries_a_wall_clock():
    assert "now" not in G.GateContext.__dataclass_fields__
    assert "now" not in P.build_context.__code__.co_varnames


def test_every_time_sensitive_resolver_still_refuses_to_default_to_now():
    with pytest.raises(ValueError):
        Q.resolve_decision_quote(None, "T", "YES", as_of=None)
    with pytest.raises(F.FeeStateError):
        F.load_fee_schedule(ROOT).entry_fee(0.5, 10, "KXNFLGAME")
    with pytest.raises(R.RiskPolicyError):
        R.outstanding_exposure([], [], [], None)


def test_preflight_and_the_importer_share_one_context_assembly():
    """If these diverge, the twelve-hourly run stops being a replay of the pre-trade check."""
    import scripts.handicap.sync_airtable as SY                      # noqa: PLC0415
    assert "PF.build_context" in inspect.getsource(SY.build_gate_context)


# ---- 3-5. freshness, per-series observation, change-suppressed confirmation --------------------------

def test_the_freshness_windows_are_still_fifteen_minutes():
    assert Q.DEFAULT_MAX_QUOTE_AGE_MIN == 15.0
    assert D.DEFAULT_MAX_BOOK_AGE_MIN == 15.0


def test_confirmation_is_still_separate_from_the_last_price_move():
    for field in ("quote_moved_at", "confirmed_at", "confirmation_basis", "age_minutes"):
        assert field in Q.DecisionQuote.__dataclass_fields__


def test_the_capture_still_writes_per_series_observation_times_and_last_seen():
    src = open(os.path.join(ROOT, "scripts", "kalshi", "capture.py")).read()
    assert '"observed_at"' in src and 'last_seen' in src


# ---- 6-8. depth, VWAP, the ceiling -------------------------------------------------------------------

def test_the_depth_record_still_separates_top_ask_from_vwap_from_worst():
    for field in ("top_ask", "vwap", "worst_price", "slippage_dollars", "fillable_stake"):
        assert field in D.DepthResult.__dataclass_fields__


def test_the_ceiling_is_still_a_hard_error_in_the_schema():
    src = inspect.getsource(S)
    assert "NOT ACTIONABLE" in src, "an ask above bet_up_to_probability must raise, not warn"


# ---- 9-11. the fee engine ----------------------------------------------------------------------------

def test_the_fixed_point_fee_mechanics_are_intact():
    """The decomposition survives; the INCREMENTS are pinned in test_fees against the current venue rules."""
    from decimal import Decimal                                          # noqa: PLC0415
    assert F.TRADE_FEE_INCREMENT == Decimal("0.000001")
    assert F.NON_DIRECT_BALANCE_PRECISION == Decimal("0.01")
    assert F.DIRECT_BALANCE_PRECISION == Decimal("0.0001")
    assert not hasattr(F, "CENTICENT"), "the misnamed increment must not come back"
    comp = F.fee_for_fill(0.055, 1, 0.07, 1.0)
    for part in ("raw_quadratic", "trade_fee", "rounding_fee", "rebate", "net_fee", "rebate_capped"):
        assert hasattr(comp, part)


def test_kxnflgame_still_has_both_multipliers_known():
    m = F.load_fee_schedule(ROOT).multipliers_for("KXNFLGAME", AS_OF)
    assert (m.taker, m.maker) == (1.0, 1.0)
    assert m.taker_state == m.maker_state == F.KNOWN


def test_an_unknown_or_conflicted_fee_still_fails_closed():
    sched = F.load_fee_schedule(ROOT)
    q = sched.taker_fee(0.5, 10, "KXNOTAREALSERIES", as_of=AS_OF)
    assert not q.is_known and q.amount is None
    nev = F.net_executable_ev(0.7, 0.5, 10, sched, series_ticker="KXNOTAREALSERIES", as_of=AS_OF)
    assert nev.net_ev_dollars is None and not nev.is_known


def test_net_ev_at_or_below_zero_still_blocks():
    src = inspect.getsource(G._net_ev_gate)
    assert "net_ev_dollars <= 0" in src
    assert "not a minimum-edge policy" in src


# ---- 12-13. multi-fill economics ---------------------------------------------------------------------

def test_fills_are_still_summed_per_fill_rather_than_blended():
    agg = E.aggregate_executions(
        [dict(execution_id="a", recommendation_id="r", executed_at="x", side="YES",
              actual_price=0.54, stake=20, fees_paid=0.0),
         dict(execution_id="b", recommendation_id="r", executed_at="x", side="YES",
              actual_price=0.55, stake=30, fees_paid=0.0)], won=True)
    assert agg["n_executions"] == 2
    assert agg["gross_pnl"] == pytest.approx(41.58, abs=0.01)
    assert agg["average_execution_price"] is not None


# ---- 14-15. identity and availability ----------------------------------------------------------------

def test_identity_and_availability_still_fail_closed():
    src = inspect.getsource(G)
    assert "not resolved to a GSIS id" in src
    assert "MAX_AVAILABILITY_STALE_MIN" in inspect.getsource(G._availability_gate)


# ---- 16. non-Kelly -----------------------------------------------------------------------------------

def test_sizing_is_still_flat_and_not_edge_proportional():
    src = inspect.getsource(R)
    for banned in ("kelly", "Kelly * ", "edge *", "probability_mid"):
        assert f"{banned}(" not in src
    assert "It is not Kelly" in src
    for f in ("proposed_stake", "grade", "game_id", "correlation_group"):
        assert f in R.Proposal.__dataclass_fields__
    assert "probability" not in R.Proposal.__dataclass_fields__


# ---- 17-19. bridge, append-only, TEST_ONLY -----------------------------------------------------------

def test_the_bridge_still_plans_before_it_writes_and_pushes_before_it_marks_synced():
    import nfl_edge.handicap.airtable_bridge as AB                   # noqa: PLC0415
    assert hasattr(AB, "plan_run") and hasattr(AB, "apply_plan")
    src = open(os.path.join(ROOT, "scripts", "handicap", "sync_airtable.py")).read()
    assert "PUSH SUCCEEDS -> mark SYNCED" in src


def test_the_append_only_guard_still_exists_and_covers_the_new_kind():
    src = open(os.path.join(ROOT, "scripts", "handicap", "verify_append_only.py")).read()
    assert "--diff-filter=MDR" in src
    assert "decision_gates" in src or "IMMUTABLE_KINDS" in src


def test_test_only_records_are_still_excluded_from_money_and_from_exposure():
    from nfl_edge.handicap import store                              # noqa: PLC0415
    assert "include_test" in inspect.signature(store.read_kind).parameters
    out = R.outstanding_exposure(
        [dict(recommendation_id="t", decision=S.RECOMMENDED, test_only=True, recommended_stake=100,
              created_at=AS_OF.isoformat(), kickoff_utc=(AS_OF + timedelta(days=1)).isoformat())],
        [], [], AS_OF)
    assert out.total == 0.0


# ---- 20-21. CI and governance ------------------------------------------------------------------------

def test_ci_still_runs_the_suite_on_pull_requests():
    wf = open(os.path.join(ROOT, ".github", "workflows", "tests.yml")).read()
    assert "pull_request" in wf and "pytest" in wf


def test_the_h019_governance_correction_is_intact():
    """H-019 is the favourite/long-shot hypothesis and is about nothing else.

    The game-market execution result belongs to Milestone K (research/passive), and the still-open prop-book
    question is H-023. Attributing the first result to the first hypothesis was a naming error, never a
    change to any hypothesis' status.
    """
    std = open(os.path.join(ROOT, "docs", "DECISION_STANDARD.md")).read()
    assert "not* by H-019" in std or "*not* by H-019" in std
    assert "favourite/longshot" in std or "favourite" in std
    roadmap = open(os.path.join(ROOT, "docs", "ROADMAP.md")).read()
    assert "REJECTED on game markets" in roadmap, "Milestone K owns the passive-execution result"
    assert "H-023" in roadmap and "prop book" in roadmap


# ---- 22-25. the closure round ------------------------------------------------------------------------

def test_settlement_still_cannot_release_exposure_retroactively():
    src = inspect.getsource(R)
    assert "SETTLEMENT RELEASES EXPOSURE ONLY AS OF A MOMENT THE OUTCOME WAS AVAILABLE" in src
    assert "settlement_observed_at" in R.SETTLEMENT_AVAILABILITY_FIELDS
    assert R.SETTLEMENT_AVAILABILITY_FIELDS[-1] == "evaluated_at", "the fallback must stay the LAST resort"
    assert R._settlement_available_at({}) == (None, "none")


def test_the_rounding_bound_still_assumes_fractional_fills_by_default():
    assert F.contract_increment(F.GRANULARITY_UNKNOWN) == F.CONTRACT_INCREMENT_FRACTIONAL
    assert F.CONTRACT_INCREMENT_FRACTIONAL == __import__("decimal").Decimal("0.01")
    assert F.rounding_uncertainty(0.9, F.CENT)["max_fills"] == 90, \
        "a fractional order is not limited to one fill"
    assert F.load_fee_schedule(ROOT).granularity_state_for("KXNFLGAME") == F.GRANULARITY_UNKNOWN


def test_a_fills_net_fee_is_still_never_negative():
    """The venue caps the rebate per fill. The unabsorbed credit is deferred, not forfeited."""
    capped = F.fee_for_fill(0.5, 0.01, 0.07, 1.0, accumulator=0.0098)
    assert capped.net_fee >= 0.0 and capped.rebate_capped is True
    assert capped.accumulator_after > 0
    order = F.fee_for_order([(0.5, 0.01)] * 3, 0.07, 1.0)
    assert order["net_fee"] >= 0.0
    assert order["net_fee"] == pytest.approx(order["trade_fee"] + order["accumulator_final"], abs=1e-9)


def test_the_documented_fee_change_keys_are_still_first():
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415
    assert CAP.FEE_CHANGE_ARRAY_KEYS[0] == "series_fee_change_arr"
    assert F.CHANGE_EFFECTIVE_KEYS[0] == "scheduled_ts"


def test_the_pre_trade_leg_is_still_reachable_from_airtable():
    from nfl_edge.handicap import airtable_bridge as AB      # noqa: PLC0415
    for st in ("PREFLIGHT_REQUESTED", "PREFLIGHT_APPROVED", "PREFLIGHT_BLOCKED", "PREFLIGHT_ERROR"):
        assert getattr(AB, f"STATUS_{st}") == st
    assert os.path.exists(os.path.join(ROOT, ".github", "workflows", "preflight.yml"))
    assert os.path.exists(os.path.join(ROOT, "scripts", "handicap", "preflight_airtable.py"))


def test_the_airtable_payload_is_still_never_rewritten():
    from nfl_edge.handicap import airtable_bridge as AB      # noqa: PLC0415
    client = AB.AirtableClient("tok", "b", "t", opener=lambda *a, **k: None)
    with pytest.raises(AB.BridgeError):
        client.write_fields({"rec1": {AB.F_PAYLOAD: "rewritten"}})


# ---- 29-32. the final closure round -------------------------------------------------------------------

def test_the_trade_fee_increment_is_still_six_decimal_dollars():
    from decimal import Decimal                                          # noqa: PLC0415
    assert F.TRADE_FEE_INCREMENT == Decimal("0.000001")
    assert F.rounding_uncertainty(100, F.CENT)["trade_fee_increment"] == pytest.approx(1e-06)


def test_fee_change_identity_is_still_per_change_not_per_series():
    a = {"series_ticker": "K", "scheduled_ts": "2026-10-01T00:00:00Z"}
    b = {"series_ticker": "K", "scheduled_ts": "2026-12-01T00:00:00Z"}
    assert F.change_identity(a) != F.change_identity(b)
    assert F.change_identity({"id": "x"}) == ("id", "x")


def test_preflight_still_refuses_to_default_its_own_clock():
    with pytest.raises(ValueError):
        P.preflight_batch([], market_data_root=None, ledger_root=None, root=ROOT, approval_as_of=None)
    assert P.MAX_REQUEST_AGE_MIN > 0


def test_a_real_recommendation_still_needs_a_hash_bound_approval():
    from nfl_edge.handicap import airtable_bridge as AB                  # noqa: PLC0415
    src = inspect.getsource(AB._canonical_records)
    assert "approved_payload_sha256" in src
    assert "verdict" in src
    assert AB.F_APPROVED_PAYLOAD == "Approved Payload"
    # And the whitelist still cannot reach the candidate request.
    client = AB.AirtableClient("tok", "b", "t", opener=lambda *a, **k: None)
    with pytest.raises(AB.BridgeError):
        client.write_fields({"rec1": {AB.F_PAYLOAD: "rewritten"}})
