"""The real-money gates, and the portfolio policy behind one of them.

Each test below is a way the desk could lose money that the system must make impossible rather than
unlikely. The uniting principle is that UNKNOWN is a FAILURE: a gate that cannot reach its evidence blocks a
RECOMMENDED record exactly as a gate that reached it and did not like what it saw. Treating "I could not
check" as "it is fine" is the failure mode all of this exists to prevent.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.execution import fees as F        # noqa: E402
from nfl_edge.execution import quotes as Q      # noqa: E402
from nfl_edge.handicap import gates as G        # noqa: E402
from nfl_edge.handicap import risk as R         # noqa: E402
from nfl_edge.handicap import schema as S       # noqa: E402

NOW = datetime(2026, 9, 7, 15, 40, tzinfo=timezone.utc)


class FakeIndex:
    """A capture index that confirms one ticker at a stated moment and price.

    `confirmed_minutes_ago` is relative to the DECISION time, not to wall clock -- which is the whole point
    of the architecture these tests pin.
    """

    def __init__(self, ask=0.62, confirmed_minutes_ago=2.0, no_ask=0.40, status="active", present=True,
                 anchor=None):
        self.ask, self.no_ask, self.status, self.present = ask, no_ask, status, present
        self.confirmed = (anchor or NOW) - timedelta(minutes=confirmed_minutes_ago)

    def confirmation(self, ticker, series_ticker, as_of=None):
        if not self.present:
            return None, None, None, "no capture run confirms this ticker"
        if as_of is not None and self.confirmed > as_of:
            return None, None, None, (f"the only capture for {ticker} is at {self.confirmed.isoformat()}, "
                                      f"AFTER the decision at {as_of.isoformat()}")
        return self.confirmed, Q.CONFIRM_TICKER, "run", None

    def last_quote_row(self, ticker, not_after=None):
        if not self.present:
            return None
        return {"ticker": ticker, "observed_at": self.confirmed.isoformat(), "status": self.status,
                "yes_bid": 0.60, "yes_ask": self.ask, "no_bid": 0.36, "no_ask": self.no_ask}


class FakeBook:
    """A book index with a stated ask ladder, deep enough to fill by default."""

    def __init__(self, ladder=None, observed_minutes_ago=2.0, present=True, anchor=None):
        # ladder is [(yes_ask, size)]; stored as the NO bids the real capture holds.
        self.ladder = ladder if ladder is not None else [(0.62, 100000.0)]
        self.observed = (anchor or NOW) - timedelta(minutes=observed_minutes_ago)
        self.present = present

    def latest_book(self, ticker, as_of):
        if not self.present or self.observed > as_of:
            return None
        return {"ticker": ticker, "observed_at": self.observed.isoformat(), "run_id": "run",
                "orderbook_fp": {"no_dollars": [[f"{1 - p:.4f}", f"{s}"] for p, s in
                                                sorted(self.ladder, key=lambda x: -x[0])],
                                 "yes_dollars": [["0.5000", "10"]]}}


def rec(**kw):
    """A complete, schema-valid RECOMMENDED record.

    Complete on purpose: several tests here assert that the SCHEMA refuses something, and a fixture that was
    already invalid for an unrelated reason would make those tests pass for the wrong one.
    """
    d = dict(recommendation_id="rec_g1", schema_version=S.HANDICAP_SCHEMA_VERSION,
             created_at="2026-09-07T15:38:00+00:00", handicap_run_id="20260907T153800Z",
             packet_sha="abc123", season=2026, week=1,
             decision=S.RECOMMENDED, side="YES",
             market_ticker="KXNFLGAME-26SEP09NESEA-SEA", market_family="GAME_WINNER",
             game_id="2026_01_NE_SEA", kickoff_utc="2026-09-10T00:20:00+00:00",
             yes_bid=0.60, yes_ask=0.62, no_bid=0.36, no_ask=0.40, mid=0.61,
             market_timestamp="2026-09-07T15:38:00+00:00", minutes_to_kickoff=2000.0,
             grade="B+", bet_up_to_probability=0.65,
             probability_low=0.66, probability_mid=0.70, probability_high=0.75,
             recommended_stake=10, proposed_stake=10, bankroll_snapshot=2000.0,
             primary_thesis="thesis", key_supporting_factors=["a"], counterarguments=["b"],
             uncertainties=["c"], source_freshness={"shadow_snapshot": "2026-09-07T15:00:00+00:00"},
             support_state=S.SUPPORT_SUPPORTED, model_version="shadow-0.4.0", artifact_hash="cafe",
             model_probability=0.68)
    d.update(kw)
    return d


def ctx(index=None, records=None, book=None, **kw):
    policy = R.RiskPolicy.load(ROOT)
    c = G.GateContext(capture_index=index if index is not None else FakeIndex(),
                      book_index=book if book is not None else FakeBook(),
                      fee_schedule=F.load_fee_schedule(ROOT), **kw)
    c.risk_report = policy.evaluate([R.Proposal.from_record(r) for r in (records or [rec()])], 2000.0)
    return c


def run(r=None, **kw):
    r = r or rec()
    return G.evaluate_gates(r, ctx(records=[r], **kw))


# ---- the happy path --------------------------------------------------------------------------------

def test_a_complete_recommendation_passes_every_gate():
    report = run()
    assert report.overall == G.PASS, report.blocking_reasons
    assert report.decision_quote["executable_price"] == 0.62
    assert report.net_ev["fee_state"] == F.KNOWN
    assert all(g.status in (G.PASS, G.NOT_APPLICABLE) for g in report.gates.values())


def test_the_gate_record_validates_and_is_deterministic_in_the_recommendation_id():
    """Gates run once. A second write must collide with the first, not quietly contradict it."""
    a, b = run().to_record(now=NOW), run().to_record(now=NOW + timedelta(hours=3))
    assert a["gates_id"] == b["gates_id"], "the id must not depend on when the gate ran"
    assert S.validate_decision_gates(a) == []


# ---- 1. stale price --------------------------------------------------------------------------------

def test_a_stale_decision_time_quote_fails_closed():
    report = run(index=FakeIndex(confirmed_minutes_ago=40))
    assert report.overall == G.FAIL
    assert report.gates[G.G_QUOTE_FRESHNESS].status == G.FAIL


def test_an_unreachable_capture_stream_blocks_rather_than_waves_through():
    """The critical asymmetry: 'I could not check' must never resolve to 'it is fine'."""
    report = G.evaluate_gates(rec(), G.GateContext(capture_index=None, book_index=FakeBook(),
                                                   fee_schedule=F.load_fee_schedule(ROOT)))
    assert report.overall == G.FAIL
    assert report.gates[G.G_QUOTE_FRESHNESS].status == G.UNAVAILABLE


def test_a_quiet_but_confirmed_market_is_not_treated_as_stale():
    """Change suppression again: confirmed 2 minutes ago, last moved hours ago. That is tradable."""
    idx = FakeIndex(confirmed_minutes_ago=2)
    assert run(index=idx).gates[G.G_QUOTE_FRESHNESS].status == G.PASS


def test_a_pass_record_is_not_gated_on_freshness():
    """A stale price is frequently the REASON for a pass. Gating it would delete that record."""
    report = G.evaluate_gates(rec(decision=S.PASS, grade="PASS"),
                              ctx(index=FakeIndex(confirmed_minutes_ago=600)))
    assert report.overall == G.NOT_APPLICABLE


# ---- 2. the live price above the ceiling -----------------------------------------------------------

def test_a_live_ask_above_the_ceiling_fails():
    """The recorded ask was fine when the packet was built. The live one is what you would pay."""
    report = run(index=FakeIndex(ask=0.71))
    assert report.gates[G.G_CEILING].status == G.FAIL
    assert "ABOVE bet_up_to_probability" in report.gates[G.G_CEILING].reason


def test_a_live_ask_exactly_at_the_ceiling_is_payable():
    assert run(index=FakeIndex(ask=0.65)).gates[G.G_CEILING].status == G.PASS


def test_the_no_side_is_gated_against_the_no_ask():
    r = rec(side="NO", bet_up_to_probability=0.35)
    report = G.evaluate_gates(r, ctx(index=FakeIndex(no_ask=0.40), records=[r]))
    assert report.gates[G.G_CEILING].status == G.FAIL


# ---- 3. player identity ----------------------------------------------------------------------------

def test_unresolved_player_identity_can_never_become_a_real_prop():
    """Coverage is never traded for identity integrity. Enforced in the schema AND at the gate."""
    r = rec(market_family="PLAYER_STAT", support_state=S.SUPPORT_UNSUPPORTED_IDENTITY,
            support_reason="kalshi id not in the crosswalk", player_name="J. Smith",
            availability_state="EXPECTED_ACTIVE", availability_as_of=NOW.isoformat(),
            model_version=None, model_probability=None)
    with pytest.raises(S.ValidationError, match="identity integrity"):
        S.validate_recommendation(r)
    assert G.evaluate_gates(r, ctx(records=[r])).gates[G.G_IDENTITY].status == G.FAIL


def test_a_supported_player_market_with_no_player_id_is_refused():
    """Claiming a quantitative price for a player the record cannot name."""
    r = rec(market_family="PLAYER_STAT", support_state=S.SUPPORT_SUPPORTED, player_id=None,
            availability_state="EXPECTED_ACTIVE", availability_as_of=NOW.isoformat())
    assert G.evaluate_gates(r, ctx(records=[r])).gates[G.G_IDENTITY].status == G.FAIL


def test_an_unresolved_identity_market_may_still_be_watchlisted():
    """The market stays visible and quotable. It just cannot become a bet."""
    r = rec(decision=S.WATCHLIST, grade=None, market_family="PLAYER_STAT",
            support_state=S.SUPPORT_UNSUPPORTED_IDENTITY, support_reason="unmapped",
            bet_up_to_probability=None, recommended_stake=None, proposed_stake=None)
    assert S.validate_recommendation(r) == []


# ---- 4. player availability ------------------------------------------------------------------------

def _prop(**kw):
    d = dict(market_family="PLAYER_STAT", player_id="00-0031234", player_name="J. Smith",
             availability_state="EXPECTED_ACTIVE", availability_as_of="2026-09-07T15:00:00+00:00",
             availability_stale_minutes=30.0, minutes_to_kickoff=2000.0)
    d.update(kw)
    return rec(**d)


def test_a_confirmed_inactive_cannot_carry_a_yes_prop():
    with pytest.raises(S.ValidationError, match="INACTIVE_CONFIRMED"):
        S.validate_recommendation(_prop(availability_state="INACTIVE_CONFIRMED"))


def test_out_and_expected_out_cannot_carry_a_yes_prop():
    for state in ("OUT", "EXPECTED_OUT"):
        with pytest.raises(S.ValidationError, match="RECOMMENDED YES player prop"):
            S.validate_recommendation(_prop(availability_state=state))


def test_unknown_availability_blocks_a_prop_outright():
    """Our sources did not find the player. Participation risk is unquantified, not small."""
    with pytest.raises(S.ValidationError, match="UNKNOWN"):
        S.validate_recommendation(_prop(availability_state="UNKNOWN"))


def test_stale_availability_cannot_silently_read_as_active():
    with pytest.raises(S.ValidationError, match="minutes old"):
        S.validate_recommendation(_prop(availability_stale_minutes=600.0))
    assert G.evaluate_gates(_prop(availability_stale_minutes=600.0),
                            ctx(records=[_prop()])).gates[G.G_AVAILABILITY].status == G.FAIL


def test_an_unresolved_questionable_near_kickoff_must_wait_for_the_inactive_list():
    """Inactives drop at T-90m. Inside that window the answer is knowable and we have not looked."""
    with pytest.raises(S.ValidationError, match="inactives are released|T-90m|90"):
        S.validate_recommendation(_prop(availability_state="QUESTIONABLE", minutes_to_kickoff=45.0))


def test_a_questionable_player_far_from_kickoff_is_allowed():
    assert S.validate_recommendation(_prop(availability_state="QUESTIONABLE",
                                           minutes_to_kickoff=2000.0)) == []


def test_a_prop_without_any_availability_record_is_refused():
    with pytest.raises(S.ValidationError, match="requires availability_state"):
        S.validate_recommendation(_prop(availability_state=None))


def test_availability_gates_do_not_apply_to_game_markets():
    """A moneyline is not gated on anybody's injury status."""
    assert S.validate_recommendation(rec(market_family="GAME_WINNER")) == []
    assert run().gates[G.G_AVAILABILITY].status == G.NOT_APPLICABLE


# ---- 5. transaction costs --------------------------------------------------------------------------

def test_an_unverified_fee_state_blocks_a_real_recommendation():
    """A trade whose cost cannot be established cannot be shown to survive its cost.

    KXNFLSPREAD charges a maker fee but is not listed in any schedule window we hold, so its maker
    multiplier is UNVERIFIED -- distinct from KXNFLGAME, whose maker multiplier IS published.
    """
    r = rec(market_ticker="KXNFLSPREAD-26SEP09NESEA-SEA")
    report = G.evaluate_gates(r, ctx(records=[r], execution_style=F.MAKER))
    assert report.gates[G.G_NET_EV].status == G.FAIL
    assert "unknown cost is never treated as zero" in report.gates[G.G_NET_EV].reason
    assert report.net_ev["fee_state"] == F.UNVERIFIED


def test_a_published_maker_multiplier_is_not_called_unknown():
    """KXNFLGAME's maker multiplier IS in the regulatory schedule. Silence in the API object is not doubt."""
    report = run(execution_style=F.MAKER)
    assert report.net_ev["fee_state"] == F.KNOWN
    assert report.gates[G.G_NET_EV].status in (G.PASS, G.FAIL)   # priced either way, never "unknown"


def test_a_missing_fee_schedule_blocks_rather_than_assuming_free():
    report = G.evaluate_gates(rec(), G.GateContext(capture_index=FakeIndex(), book_index=FakeBook(),
                                                   fee_schedule=None))
    assert report.gates[G.G_NET_EV].status == G.UNAVAILABLE


def test_a_gross_edge_erased_by_fees_blocks():
    """The case the desk must never record: fair > ask, and the trade is still worth nothing."""
    thin = rec(probability_mid=0.621)         # a hair over the 0.62 ask: gross positive, net negative
    report = G.evaluate_gates(thin, ctx(records=[thin]))
    assert report.net_ev["net_ev_dollars"] < 0
    assert report.gates[G.G_NET_EV].status == G.FAIL
    assert report.overall == G.FAIL
    assert "not a minimum-edge policy" in report.gates[G.G_NET_EV].reason


def test_a_clearly_positive_net_ev_passes():
    fat = rec(probability_mid=0.80)
    report = G.evaluate_gates(fat, ctx(records=[fat]))
    assert report.net_ev["net_ev_dollars"] > 0
    assert report.gates[G.G_NET_EV].status == G.PASS


def test_there_is_no_switch_to_turn_the_net_ev_gate_off():
    """A blocking rule with an off switch is a warning wearing a costume."""
    import inspect
    src = inspect.getsource(G)
    assert "require_net_ev_positive" not in src
    assert "require_net_ev_positive" not in [f for f in G.GateContext.__dataclass_fields__]


def test_no_positive_minimum_beyond_zero_is_invented():
    """Only <= 0 blocks. A trade worth a fraction of a cent is thin, not disallowed."""
    r = rec(probability_mid=0.62)
    # Sweep upward until net EV first turns positive; that record must PASS, not be held to a buffer.
    passed = None
    for mid in [0.62 + i * 0.0005 for i in range(1, 60)]:
        rr = rec(probability_mid=round(mid, 6))
        rep = G.evaluate_gates(rr, ctx(records=[rr]))
        if rep.net_ev.get("net_ev_dollars", 0) and rep.net_ev["net_ev_dollars"] > 0:
            passed = rep
            break
    assert passed is not None, "net EV never turned positive across the sweep"
    assert passed.gates[G.G_NET_EV].status == G.PASS, \
        "the first record with net EV above zero must pass; anything else is a hidden minimum"
    assert 0 < passed.net_ev["net_ev_dollars"] < 1.0, "the boundary case should be a thin one"
    assert r is not None


# ---- 6. portfolio risk -----------------------------------------------------------------------------

def test_the_recorded_stake_must_be_the_stake_the_policy_approved():
    oversized = rec(proposed_stake=500, recommended_stake=500)
    report = G.evaluate_gates(oversized, ctx(records=[oversized]))
    assert report.gates[G.G_RISK].status == G.FAIL
    assert "does not match the stake the risk policy approved" in report.gates[G.G_RISK].reason


def test_a_missing_risk_report_blocks():
    c = G.GateContext(capture_index=FakeIndex(), book_index=FakeBook(),
                      fee_schedule=F.load_fee_schedule(ROOT))
    assert G.evaluate_gates(rec(), c).gates[G.G_RISK].status == G.UNAVAILABLE


# ---- the risk policy itself ------------------------------------------------------------------------

@pytest.fixture(scope="module")
def policy():
    return R.RiskPolicy.load(ROOT)


def test_the_policy_is_configuration_not_code(policy):
    assert policy.policy_id == "pilot-2026-v1"
    assert policy.status == "PILOT"
    assert 0 < policy.unit_fraction_of_bankroll < 0.02, "a pilot unit must be a small bankroll fraction"


def test_a_missing_policy_file_is_an_error_not_a_default():
    with pytest.raises(R.RiskPolicyError, match="policy is configuration"):
        R.RiskPolicy.load("/nonexistent", "/nonexistent/risk_policy.json")


def test_limits_scale_with_the_bankroll_and_are_never_hardcoded_dollars(policy):
    assert policy.unit_dollars(1000) == pytest.approx(5.0)
    assert policy.unit_dollars(10000) == pytest.approx(50.0)


def test_correlated_positions_in_one_game_are_capped_as_a_group(policy):
    """Team ML + team spread + opponent under is one thesis bought three times."""
    group = "2026_01_NE_SEA::SCORING_UP"
    props = [R.Proposal(f"rec_{i}", 10.0, "2026_01_NE_SEA", group, "A") for i in range(4)]
    report = policy.evaluate(props, 2000.0)          # unit $10, group cap 3u = $30
    assert report.exposure_by_correlation_group[group] == pytest.approx(30.0)
    assert sum(1 for v in report.verdicts if v.status == R.REJECTED) >= 1
    assert any("correlation group" in " ".join(v.reasons) for v in report.verdicts)


def test_the_group_cap_binds_tighter_than_the_game_cap(policy):
    """A correlation you can name but cannot measure is handled with a tighter limit, not a covariance."""
    assert (policy.max_exposure_per_correlation_group_units
            < policy.max_exposure_per_game_units)


def test_uncorrelated_positions_in_one_game_still_hit_the_game_cap(policy):
    props = [R.Proposal(f"rec_{i}", 20.0, "2026_01_NE_SEA", f"group_{i}", "A") for i in range(5)]
    report = policy.evaluate(props, 2000.0)          # unit $10, game cap 4u = $40
    assert report.exposure_by_game["2026_01_NE_SEA"] == pytest.approx(40.0)


def test_the_slate_cap_takes_the_more_binding_of_its_two_expressions(policy):
    """Editing one expression may only ever tighten the policy, never loosen it through the other."""
    props = [R.Proposal(f"rec_{i}", 20.0, f"game_{i}", None, "A") for i in range(20)]
    report = policy.evaluate(props, 2000.0)
    cap = min(policy.max_slate_exposure_units * 10.0, 2000.0 * policy.max_slate_exposure_fraction_of_bankroll)
    assert report.total_exposure <= cap + 1e-9


def test_both_the_proposed_and_the_approved_stake_survive(policy):
    """If the policy silently overwrote the proposal there would be no evidence it ever bound."""
    v = policy.evaluate([R.Proposal("rec_a", 500.0, "g", None, "A")], 2000.0).verdicts[0]
    assert v.proposed_stake == 500.0
    assert v.approved_stake == 20.0 and v.status == R.CAPPED
    assert v.binding_limit


def test_caps_round_down_not_up(policy):
    """A risk cap that rounds up is not a cap."""
    small = R.RiskPolicy(unit_fraction_of_bankroll=0.005, max_stake_per_position_units=1.0,
                         grade_caps_units={"A": 1.0}, max_exposure_per_game_units=99,
                         max_exposure_per_correlation_group_units=99, max_slate_exposure_units=99,
                         max_slate_exposure_fraction_of_bankroll=None)
    v = small.evaluate([R.Proposal("rec_a", 100.0, None, None, "A")], 1970.0).verdicts[0]
    assert v.approved_stake == 9.0, "9.85 must floor to 9, not round to 10"


def test_an_unrecognised_grade_is_rejected_rather_than_sized(policy):
    v = policy.evaluate([R.Proposal("rec_a", 10.0, "g", None, "Z")], 2000.0).verdicts[0]
    assert v.status == R.REJECTED


def test_no_bankroll_is_an_error_not_an_assumed_default():
    with pytest.raises(R.RiskPolicyError, match="bankroll"):
        R.evaluate_records([rec(bankroll_snapshot=None)], R.RiskPolicy.load(ROOT))


def test_disagreeing_bankroll_snapshots_in_one_batch_are_an_error():
    batch = [rec(recommendation_id="a", bankroll_snapshot=1000.0),
             rec(recommendation_id="b", bankroll_snapshot=5000.0)]
    with pytest.raises(R.RiskPolicyError, match="more than one bankroll_snapshot"):
        R.evaluate_records(batch, R.RiskPolicy.load(ROOT))


def test_passes_do_not_consume_portfolio_budget():
    """A slate of passes must not crowd out the one bet that was actually taken."""
    batch = [rec(recommendation_id="a", decision=S.PASS, grade="PASS"),
             rec(recommendation_id="b", recommended_stake=10, proposed_stake=10)]
    report = R.evaluate_records(batch, R.RiskPolicy.load(ROOT))
    assert [v.recommendation_id for v in report.verdicts] == ["b"]


def test_test_only_records_never_consume_portfolio_budget():
    batch = [rec(recommendation_id="a", test_only=True, recommended_stake=500, proposed_stake=500),
             rec(recommendation_id="b", recommended_stake=10, proposed_stake=10)]
    report = R.evaluate_records(batch, R.RiskPolicy.load(ROOT))
    assert [v.recommendation_id for v in report.verdicts] == ["b"]
    assert report.verdicts[0].status == R.APPROVED


def test_the_policy_is_not_kelly():
    """Sizing must not react to the estimated edge. That calibration is what the ledger is measuring."""
    policy = R.RiskPolicy.load(ROOT)
    thin = policy.evaluate([R.Proposal("rec_a", 10.0, "g", None, "B")], 2000.0).verdicts[0]
    fat = policy.evaluate([R.Proposal("rec_b", 10.0, "g", None, "B")], 2000.0).verdicts[0]
    assert thin.approved_stake == fat.approved_stake, "the policy must not read an edge at all"


# ---- 7. full-position executability ------------------------------------------------------------------

def test_a_deep_book_lets_the_full_stake_pass():
    report = run()
    assert report.gates[G.G_DEPTH].status == G.PASS, report.blocking_reasons
    assert report.depth["vwap"] == pytest.approx(0.62)


def test_a_book_too_thin_for_the_approved_stake_blocks():
    """The top ask exists. The POSITION does not."""
    thin = FakeBook(ladder=[(0.62, 3.0)])          # $1.86 of liquidity against a $10 stake
    report = G.evaluate_gates(rec(), ctx(book=thin))
    assert report.gates[G.G_DEPTH].status == G.FAIL
    assert "can absorb only" in report.gates[G.G_DEPTH].reason
    assert report.overall == G.FAIL


def test_a_missing_book_blocks_rather_than_pricing_at_top_of_book():
    report = G.evaluate_gates(rec(), ctx(book=FakeBook(present=False)))
    assert report.gates[G.G_DEPTH].status in G.BLOCKING
    assert report.overall == G.FAIL


def test_a_walk_above_the_ceiling_blocks_even_when_the_top_ask_is_under_it():
    """The displayed price is affordable; the position is not. This is the case top-of-book hides."""
    stepped = FakeBook(ladder=[(0.62, 2.0), (0.80, 10000.0)])
    r = rec(bet_up_to_probability=0.65)
    report = G.evaluate_gates(r, ctx(records=[r], book=stepped))
    assert report.gates[G.G_CEILING].status == G.PASS, "the top ask is under the ceiling"
    assert report.gates[G.G_DEPTH].status == G.FAIL, "but the fill is not"
    assert "above bet_up_to_probability" in report.gates[G.G_DEPTH].reason


def test_net_ev_is_computed_at_the_full_position_vwap_not_the_top_ask():
    """Pricing the trade at its cheapest contract is how a losing position looks profitable."""
    stepped = FakeBook(ladder=[(0.62, 2.0), (0.645, 10000.0)])
    r = rec(probability_mid=0.66, bet_up_to_probability=0.66)
    report = G.evaluate_gates(r, ctx(records=[r], book=stepped))
    assert report.net_ev["price_basis"] == "full-position VWAP"
    assert report.net_ev["executable_price"] > 0.62, "the VWAP, not the 0.62 top ask"
    assert report.depth["slippage_dollars"] > 0


def test_the_depth_record_is_preserved_on_the_gate_record():
    report = run()
    body = report.to_record(now=NOW)
    assert body["depth"]["top_ask"] == pytest.approx(0.62)
    assert body["decision_as_of"] == report.as_of
