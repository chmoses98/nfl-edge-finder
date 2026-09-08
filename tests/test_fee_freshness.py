"""The fee schedule as an OPERATIONAL control, not a documented intention.

Two things were true at once and should not have been:

  * config/kalshi_fee_schedule.json documented a three-source hierarchy;
  * the live capture script only ever read one of the three.

A hierarchy whose third source is never ingested cannot detect the one failure it exists for -- a change
Kalshi has ANNOUNCED and we have not yet modelled. And a registry nobody has confirmed for months is not a
fee schedule, it is a memory, so a real-money preflight must not be able to rest on one indefinitely.

The other half of this file is the pre-trade rounding residual. The fee estimate prices the order as ONE
fill; the venue may fragment it. The accumulator makes fragmentation converge on the equivalent order
without equalling it, and the gap has a derivable worst case. Everything here checks that the bound is
DERIVED -- reproduced independently, and empirically never exceeded -- rather than chosen.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.execution import fees as F        # noqa: E402
from nfl_edge.handicap import gates as G        # noqa: E402

AS_OF = datetime(2026, 9, 9, 13, 0, tzinfo=timezone.utc)
SERIES = "KXNFLGAME"


@pytest.fixture(scope="module")
def sched():
    return F.load_fee_schedule(ROOT)


def observations(tmp_path, *snapshots):
    root = tmp_path / "md"
    d = root / "data" / "kalshi" / "fees"
    d.mkdir(parents=True, exist_ok=True)
    for i, snap in enumerate(snapshots):
        (d / f"snap_{i:03d}.json").write_text(json.dumps(snap))
    return F.FeeObservations(str(root))


def snapshot(retrieved, *, changes=(), differences=(), errors=None, parsed=True, fc_error=None):
    return {"retrieved_at": retrieved.isoformat(), "differences": list(differences),
            "errors": errors or {},
            "fee_changes": {"changes": list(changes), "parsed": parsed, "error": fc_error,
                            "show_historical": True}}


# ---- the verification state ---------------------------------------------------------------------------

def test_the_committed_attestation_verifies_a_recent_decision(sched):
    v = sched.verification(SERIES, AS_OF)
    assert v["state"] == F.VERIFIED
    assert v["window_id"] == "2026-07-07"
    assert v["age_days"] < sched.max_verification_age_days()


def test_a_months_old_unchecked_registry_is_stale(sched):
    v = sched.verification(SERIES, AS_OF + timedelta(days=120))
    assert v["state"] == F.STALE_VERIFICATION
    assert "unchecked registry" in v["reason"]


def test_a_clean_live_capture_refreshes_the_verification(tmp_path, sched):
    """This is what the weekly job buys: the attestation ages, the captures do not have to."""
    late = AS_OF + timedelta(days=120)
    obs = observations(tmp_path, snapshot(late - timedelta(days=3)))
    v = sched.verification(SERIES, late, obs)
    assert v["state"] == F.VERIFIED
    assert "clean live capture" in v["basis"]


def test_a_capture_that_found_differences_does_not_count_as_verification(tmp_path, sched):
    late = AS_OF + timedelta(days=120)
    dirty = observations(tmp_path, snapshot(
        late - timedelta(days=3), differences=[{"series": SERIES, "field": "fee_multiplier"}]))
    assert sched.verification(SERIES, late, dirty)["state"] == F.STALE_VERIFICATION


def test_a_capture_taken_after_the_decision_is_not_evidence_about_it(tmp_path, sched):
    """The same decision-time rule as every other gate. A later look does not verify an earlier call."""
    late = AS_OF + timedelta(days=120)
    obs = observations(tmp_path, snapshot(late + timedelta(days=1)))
    assert sched.verification(SERIES, late, obs)["state"] == F.STALE_VERIFICATION


def test_an_announced_change_already_in_force_blocks(tmp_path, sched):
    eff = AS_OF - timedelta(days=1)
    obs = observations(tmp_path, snapshot(
        AS_OF - timedelta(hours=2),
        changes=[{"series_ticker": SERIES, "effective_at": eff.isoformat(), "taker_multiplier": 2.0}]))
    v = sched.verification(SERIES, AS_OF, obs)
    assert v["state"] == F.PENDING_CHANGE
    assert "does not carry a window" in v["reason"]
    assert len(v["pending_changes"]) == 1


def test_an_announced_future_change_does_not_block_a_decision_made_before_it(tmp_path, sched):
    """A future change is a deadline, not a defect in today's pricing."""
    obs = observations(tmp_path, snapshot(
        AS_OF - timedelta(hours=2),
        changes=[{"series_ticker": SERIES, "effective_at": (AS_OF + timedelta(days=30)).isoformat()}]))
    assert sched.verification(SERIES, AS_OF, obs)["state"] == F.VERIFIED


def test_an_announced_change_that_has_a_reviewed_window_does_not_block(tmp_path, sched):
    """Once the operator writes the window, the same announcement is modelled rather than pending."""
    window_start = sched.windows[-1]["effective_from"]
    obs = observations(tmp_path, snapshot(
        AS_OF - timedelta(hours=2),
        changes=[{"series_ticker": SERIES, "effective_at": window_start}]))
    assert sched.verification(SERIES, AS_OF, obs)["state"] == F.VERIFIED


def test_a_timestamp_no_window_covers_has_no_schedule(sched):
    before_everything = datetime(2020, 1, 1, tzinfo=timezone.utc)
    v = sched.verification(SERIES, before_everything)
    assert v["state"] == F.NO_SCHEDULE
    assert "cannot be established" in v["reason"]


def test_verification_requires_a_decision_timestamp(sched):
    with pytest.raises(F.FeeStateError):
        sched.verification(SERIES, None)


# ---- the gate -----------------------------------------------------------------------------------------

def gate_of(state_source, series=SERIES, at=AS_OF):
    class Ctx:
        fee_schedule = state_source
        fee_observations = None
    report = type("R", (), {"fee_schedule": None})()
    return G._fee_schedule_gate(Ctx(), report, series, at)


def test_the_gate_passes_a_verified_schedule(sched):
    assert gate_of(sched).status == G.PASS


def test_the_gate_blocks_a_stale_schedule(sched):
    assert gate_of(sched, at=AS_OF + timedelta(days=120)).status == G.FAIL


def test_the_gate_blocks_when_no_window_applies(sched):
    r = gate_of(sched, at=datetime(2020, 1, 1, tzinfo=timezone.utc))
    assert r.status in G.BLOCKING


def test_the_gate_blocks_without_a_schedule_at_all():
    assert gate_of(None).status == G.UNAVAILABLE


def test_the_config_declares_the_freshness_policy(sched):
    """The tolerance is configuration, reviewed and versioned, not a constant buried in code."""
    p = sched.verification_policy
    assert p.get("max_verification_age_days")
    assert "CAPTURE" in p.get("on_change", "") and "BLOCK" in p.get("on_change", "")
    assert "never modified" in p.get("historical_windows", "")


# ---- ingesting the third source ------------------------------------------------------------------------

def test_the_capture_script_reads_the_fee_changes_endpoint():
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415
    src = open(CAP.__file__).read()
    assert "series_fee_changes" in src
    assert "fee_changes" in src


# The response shape the official documentation gives, verbatim.
DOCUMENTED = {
    "series_fee_change_arr": [
        {"id": "sfc_0001", "series_ticker": SERIES, "fee_type": "quadratic_with_maker_fees",
         "fee_multiplier": 2.0, "scheduled_ts": "2026-11-01T00:00:00Z"},
    ]
}


class FakeChangesClient:
    def __init__(self, body):
        self.body, self.calls = body, []

    def series_fee_changes(self, show_historical=True):
        self.calls.append(show_historical)
        return self.body


def test_the_documented_response_shape_is_parsed():
    """`series_fee_change_arr` was not in the key list, so the documented live response was discarded."""
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415
    got = CAP.fetch_fee_changes(FakeChangesClient(DOCUMENTED))
    assert got["parsed"] is True and got["error"] is None
    assert got["shape"] == "series_fee_change_arr"
    assert len(got["changes"]) == 1
    ch = got["changes"][0]
    assert ch["id"] == "sfc_0001" and ch["fee_multiplier"] == 2.0, "every raw field is preserved"


def test_scheduled_ts_is_the_effective_timestamp():
    """`scheduled_ts` was not in the effective-time key list either, so a parsed change had no date."""
    ch = DOCUMENTED["series_fee_change_arr"][0]
    assert F._change_effective(ch) == datetime(2026, 11, 1, tzinfo=timezone.utc)


def test_an_epoch_scheduled_ts_is_also_understood():
    """Kalshi's `_ts` suffix is epoch seconds elsewhere in the API; both forms are accepted."""
    epoch = int(datetime(2026, 11, 1, tzinfo=timezone.utc).timestamp())
    assert F._change_effective({"scheduled_ts": epoch}) == datetime(2026, 11, 1, tzinfo=timezone.utc)
    assert F._change_effective({"scheduled_ts": str(epoch)}) == datetime(2026, 11, 1, tzinfo=timezone.utc)


def test_show_historical_is_requested():
    """A weekly job can miss the week a change is announced in; upcoming-only would lose the evidence."""
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415
    client = FakeChangesClient(DOCUMENTED)
    got = CAP.fetch_fee_changes(client)
    assert client.calls == [True]
    assert got["show_historical"] is True


def test_a_historical_change_is_parsed_the_same_way():
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415
    past = {"series_fee_change_arr": [dict(DOCUMENTED["series_fee_change_arr"][0],
                                           scheduled_ts="2026-08-01T00:00:00Z")]}
    got = CAP.fetch_fee_changes(FakeChangesClient(past))
    assert got["parsed"] and F._change_effective(got["changes"][0]) == \
        datetime(2026, 8, 1, tzinfo=timezone.utc)


def test_alternate_shapes_still_work_defensively():
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415
    payload = {"series_ticker": SERIES, "effective_at": "2026-11-01T00:00:00Z"}
    for body in ([payload], {"fee_changes": [payload]}, {"changes": [payload]},
                 {SERIES: {"effective_at": "2026-11-01T00:00:00Z"}}):
        got = CAP.fetch_fee_changes(FakeChangesClient(body))
        assert got["parsed"] and len(got["changes"]) == 1, body


def test_an_unrecognised_shape_is_inconclusive_never_no_changes():
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415
    got = CAP.fetch_fee_changes(FakeChangesClient({"unexpected": "payload", "n": 3}))
    assert got["parsed"] is False
    assert got["changes"] == []
    assert "INCONCLUSIVE" in got["error"]


def test_a_failing_fee_changes_call_is_reported_not_fatal():
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415

    class Boom:
        def series_fee_changes(self, show_historical=True):
            raise RuntimeError("503")

    got = CAP.fetch_fee_changes(Boom())
    assert got["changes"] == [] and "503" in got["error"] and got["parsed"] is False


def test_an_unreadable_fee_change_feed_cannot_produce_verified(tmp_path, sched):
    """The operational half: a run that could not read the third source does not confirm the schedule."""
    late = AS_OF + timedelta(days=120)
    good = observations(tmp_path / "ok", snapshot(late - timedelta(days=3)))
    assert sched.verification(SERIES, late, good)["state"] == F.VERIFIED

    blind = observations(tmp_path / "blind",
                         snapshot(late - timedelta(days=3), parsed=False, fc_error="503"))
    v = sched.verification(SERIES, late, blind)
    assert v["state"] == F.STALE_VERIFICATION
    assert v["fee_changes_state"] == "INCONCLUSIVE"


def test_an_unmodelled_change_at_its_scheduled_ts_blocks(tmp_path, sched):
    obs = observations(tmp_path, snapshot(
        AS_OF - timedelta(hours=2),
        changes=[dict(DOCUMENTED["series_fee_change_arr"][0],
                      scheduled_ts=(AS_OF - timedelta(days=1)).isoformat())]))
    v = sched.verification(SERIES, AS_OF, obs)
    assert v["state"] == F.PENDING_CHANGE


def test_a_committed_window_at_the_exact_scheduled_ts_covers_the_change(tmp_path, sched):
    obs = observations(tmp_path, snapshot(
        AS_OF - timedelta(hours=2),
        changes=[dict(DOCUMENTED["series_fee_change_arr"][0],
                      scheduled_ts=sched.windows[-1]["effective_from"])]))
    assert sched.verification(SERIES, AS_OF, obs)["state"] == F.VERIFIED


def test_the_check_fails_on_an_unreadable_fee_change_feed():
    """`--check` must not exit 0 on 'we could not tell'."""
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415
    src = open(CAP.__file__).read()
    assert "COULD NOT BE READ" in src
    assert 'not snapshot["fee_changes"].get("parsed")' in src


def test_the_capture_script_never_writes_the_committed_config():
    """Capture, surface, block, review. An API response must not rewrite the ledger's pricing history."""
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415
    src = open(CAP.__file__).read()
    for forbidden in ("open(REG_PATH, \"w\")", "kalshi_fee_schedule.json\", \"w\"", "json.dump(reg"):
        assert forbidden not in src


# ---- the rounding residual ------------------------------------------------------------------------------

def test_the_bound_is_the_ceiling_term_plus_one_accumulator_residual():
    """N is set by the venue's MINIMUM FILL; the ceiling term uses the ACTUAL trade-fee increment."""
    u = F.rounding_uncertainty(100, F.CENT)
    assert u["contract_increment"] == pytest.approx(0.01)
    assert u["max_fills"] == 10000, "100 contracts can arrive as 10000 fills of 0.01"
    assert u["trade_fee_increment"] == pytest.approx(1e-06)
    assert u["trade_fee_ceiling_bound"] == pytest.approx(10000 * 1e-06)
    assert u["accumulator_residual_bound"] == pytest.approx(0.01)
    assert u["bound_dollars"] == pytest.approx(0.02)


def test_the_residual_term_dominates_at_ordinary_sizes():
    """With the correct $0.000001 increment the accumulator residual is most of the bound, not the ceiling.

    Under the increment this file previously asserted, a 16-contract position carried a $0.17 bound; the
    ceiling term was a hundred times too large and swamped everything. Those magnitudes are discarded.
    """
    u = F.rounding_uncertainty(16.13, F.CENT)
    assert u["bound_dollars"] == pytest.approx(0.011613, abs=1e-6)
    assert u["trade_fee_ceiling_bound"] < u["accumulator_residual_bound"]


def test_a_direct_member_gets_a_smaller_residual_term():
    """The residual is one BALANCE PRECISION, so a direct member's bound is dominated by the ceiling."""
    ordinary = F.rounding_uncertainty(100, F.NON_DIRECT_BALANCE_PRECISION)
    direct = F.rounding_uncertainty(100, F.DIRECT_BALANCE_PRECISION)
    assert direct["accumulator_residual_bound"] == pytest.approx(0.0001)
    assert direct["bound_dollars"] < ordinary["bound_dollars"]


def test_a_whole_contract_market_gets_the_much_smaller_bound():
    """The lever that shrinks this is EVIDENCE, not preference."""
    whole = F.rounding_uncertainty(100, F.CENT, granularity_state=F.GRANULARITY_WHOLE)
    assert whole["max_fills"] == 100
    assert whole["bound_dollars"] == pytest.approx(0.0101)


def test_unknown_granularity_is_priced_exactly_as_fractional():
    """'We could not establish that fractional trading is off' may never shrink a cost bound."""
    unknown = F.rounding_uncertainty(7.5, F.CENT, granularity_state=F.GRANULARITY_UNKNOWN)
    fractional = F.rounding_uncertainty(7.5, F.CENT, granularity_state=F.GRANULARITY_FRACTIONAL)
    assert unknown["bound_dollars"] == fractional["bound_dollars"]
    assert unknown["max_fills"] == 750
    assert F.contract_increment(F.GRANULARITY_UNKNOWN) == F.CONTRACT_INCREMENT_FRACTIONAL


def test_a_fractional_order_is_not_limited_to_one_fill():
    """The defect this replaces: 0.90 contracts was bounded at ONE fill, and it is ninety."""
    u = F.rounding_uncertainty(0.90, F.CENT)
    assert u["max_fills"] == 90
    assert F.rounding_uncertainty(0.09, F.CENT)["max_fills"] == 9
    assert F.rounding_uncertainty(0.01, F.CENT)["max_fills"] == 1


def test_a_whole_dollar_stake_does_not_imply_a_whole_contract_quantity():
    """$10 at 62c is 16.13 contracts. Nothing about our sizing makes the venue's fills integral."""
    contracts = F.contracts_for_stake(10.0, 0.62)
    assert contracts != pytest.approx(round(contracts))
    assert F.rounding_uncertainty(contracts, F.CENT)["max_fills"] == 1613


def test_the_bound_is_summed_per_price_level_and_never_double_charges_the_walk():
    """A fill cannot span two levels, so the levels fragment independently.

    The VWAP movement ACROSS levels is already priced exactly by the fee estimate, which is computed from
    these same levels. This term bounds only the fragmentation WITHIN each level's known quantity.
    """
    levels = [(0.56, 1.0), (0.59, 2.5), (0.60, 0.30)]
    per_level = F.rounding_uncertainty(3.8, F.CENT, levels=levels)
    assert per_level["max_fills"] == 100 + 250 + 30
    assert "3 observed price level(s)" in per_level["levels_basis"]
    # Without the book the whole quantity is treated as one level: a WEAKER bound, never a smaller one.
    blind = F.rounding_uncertainty(3.8, F.CENT)
    assert blind["bound_dollars"] <= per_level["bound_dollars"] + 1e-9


def test_the_bound_scales_with_size_not_with_price():
    small, large = F.rounding_uncertainty(10, F.CENT), F.rounding_uncertainty(1000, F.CENT)
    assert large["bound_dollars"] > small["bound_dollars"]
    assert small["bound_dollars"] == pytest.approx(0.01 + 1000 * 1e-06)


def test_no_fragmentation_can_exceed_the_bound():
    """The empirical check on the derivation, over the shapes a real order actually takes."""
    for price in (0.05, 0.17, 0.5, 0.62, 0.93):
        for contracts in (1, 7, 40, 100, 250):
            one = F.fee_for_order([(price, contracts)], 0.07, 1.0)["net_fee"]
            bound = F.rounding_uncertainty(contracts, F.CENT)["bound_dollars"]
            for pieces in (2, 5, contracts):
                if pieces > contracts:
                    continue
                size = contracts / pieces
                many = F.fee_for_order([(price, size)] * pieces, 0.07, 1.0)["net_fee"]
                assert many - one <= bound + 1e-9, \
                    f"{pieces} fills at {price} cost {many} vs {one}; bound was {bound}"


@pytest.mark.parametrize("contracts,pieces", [(0.90, 3), (0.09, 3), (0.30, 30), (0.03, 3), (2.5, 250)])
def test_official_style_fractional_fill_shapes_stay_within_the_bound(contracts, pieces):
    """0.90 split into three 0.30s, 0.09 into three 0.03s, and full 0.01-granularity shredding."""
    for price in (0.05, 0.5, 0.62, 0.93):
        one = F.fee_for_order([(price, contracts)], 0.07, 1.0)["net_fee"]
        bound = F.rounding_uncertainty(contracts, F.CENT)["bound_dollars"]
        many = F.fee_for_order([(price, contracts / pieces)] * pieces, 0.07, 1.0)["net_fee"]
        assert many - one <= bound + 1e-9, \
            f"{pieces} x {contracts / pieces} at {price}: {many} vs {one}, bound {bound}"


def test_a_worst_case_penny_granularity_sweep_stays_within_the_bound():
    """The adversarial case: every fill is the minimum the venue permits."""
    for price in (0.05, 0.5, 0.93):
        for contracts in (0.5, 2.0, 5.0):
            n = int(round(contracts / 0.01))
            one = F.fee_for_order([(price, contracts)], 0.07, 1.0)["net_fee"]
            shredded = F.fee_for_order([(price, 0.01)] * n, 0.07, 1.0)["net_fee"]
            bound = F.rounding_uncertainty(contracts, F.CENT)["bound_dollars"]
            assert shredded - one <= bound + 1e-9, \
                f"{n} penny fills at {price}: {shredded} vs {one}, bound {bound}"
            # Not asserted the other way round: with the per-fill rebate cap, shredding can occasionally
            # come out CHEAPER than the equivalent fill. The bound exists to cap the expensive direction,
            # which is the only one that can make a trade look better than it is.


def test_a_whole_contract_fill_count_is_still_an_unsound_derivation():
    """The fractional-granularity correction remains necessary, and the honest magnitude is smaller.

    Under the WRONG $0.0001 increment this violation showed up at five contracts. With the correct
    $0.000001 increment the ceiling term is a hundred times smaller and the accumulator residual dominates,
    so the assumption has to be pushed harder before it breaks -- but it does break, which is what makes it
    a wrong derivation rather than a loose one. Reported honestly: at ordinary pilot sizes the two bounds
    are close, and the reason to keep the fractional one is that it is TRUE, not that it is bigger.
    """
    contracts, price = 150.0, 0.15
    whole_contract_bound = contracts * float(F.TRADE_FEE_INCREMENT) + 0.01
    n = int(round(contracts / 0.01))
    one = F.fee_for_order([(price, contracts)], 0.07, 1.0)["net_fee"]
    shredded = F.fee_for_order([(price, 0.01)] * n, 0.07, 1.0)["net_fee"]
    assert shredded - one > whole_contract_bound, \
        "a fill count derived from whole contracts is not a bound the mechanism respects"
    assert shredded - one <= F.rounding_uncertainty(contracts, F.CENT)["bound_dollars"] + 1e-9


def test_the_per_fill_rebate_cap_is_modelled_and_the_identity_survives_it():
    """The venue caps a fill's rebate so its net fee cannot go negative -- and the bound still holds.

    A previous version let a fill's net go negative and floored only the order total. That models a more
    generous exchange than the real one. With the cap restored, `net_order == SUM(trade_fee) + accumulator`
    holds exactly with no flooring anywhere, which is what the bound rests on.
    """
    capped = F.fee_for_fill(0.5, 0.01, 0.07, 1.0, accumulator=0.0098)
    assert capped.net_fee >= 0.0 and capped.rebate_capped is True

    for fills in ([(0.5, 0.01)] * 200, [(0.62, 1.0)] * 13, [(0.05, 0.3)] * 40):
        order = F.fee_for_order(fills, 0.07, 1.0)
        assert order["net_fee"] == pytest.approx(
            order["trade_fee"] + order["accumulator_final"], abs=1e-9)
        assert order["net_fee"] >= 0.0

    one = F.fee_for_order([(0.5, 2.0)], 0.07, 1.0)["net_fee"]
    many = F.fee_for_order([(0.5, 0.01)] * 200, 0.07, 1.0)["net_fee"]
    assert many - one <= F.rounding_uncertainty(2.0, F.CENT)["bound_dollars"] + 1e-9


def test_a_multi_level_walk_stays_within_the_per_level_bound():
    levels = [(0.56, 1.3), (0.59, 2.2), (0.61, 0.5)]
    one = F.fee_for_order(levels, 0.07, 1.0)["net_fee"]
    bound = F.rounding_uncertainty(4.0, F.CENT, levels=levels)["bound_dollars"]
    shredded = []
    for price, qty in levels:
        n = int(round(qty / 0.01))
        shredded.extend([(price, 0.01)] * n)
    many = F.fee_for_order(shredded, 0.07, 1.0)["net_fee"]
    assert many - one <= bound + 1e-9, f"{many} vs {one}, bound {bound}"


def test_the_accumulator_residual_never_exceeds_one_cent():
    """The half of the derivation that makes the bound finite at all."""
    for n in (1, 2, 3, 7, 10, 50, 200):
        order = F.fee_for_order([(0.055, 1)] * n, 0.07, 1.0)
        assert 0 <= order["accumulator_final"] <= 0.01 + 1e-12, n


def test_conservative_net_ev_is_net_ev_less_the_bound(sched):
    nev = F.net_executable_ev(0.70, 0.62, 100, sched, series_ticker=SERIES, as_of=AS_OF)
    assert nev.is_known
    expected = F.rounding_uncertainty(
        100, F.CENT, granularity_state=sched.granularity_state_for(SERIES))["bound_dollars"]
    assert nev.fee_uncertainty_dollars == pytest.approx(expected)
    assert nev.conservative_net_ev_dollars == pytest.approx(nev.net_ev_dollars - expected)
    assert nev.fee_uncertainty["derivation"]
    assert nev.fee_uncertainty["granularity_state"] == F.GRANULARITY_UNKNOWN


def test_net_ev_uses_the_observed_levels_so_the_walk_is_not_charged_twice(sched):
    """The bound must cover fragmentation within the levels, not the VWAP movement across them."""
    levels = [(0.60, 40.0), (0.62, 60.0)]
    with_levels = F.net_executable_ev(0.70, 0.62, 100, sched, series_ticker=SERIES, as_of=AS_OF,
                                      fills=levels)
    assert with_levels.fee_uncertainty["levels_basis"].startswith("2 observed")
    assert with_levels.fee_uncertainty["max_fills"] == 4000 + 6000


def test_the_bound_is_a_cost_bound_and_not_an_edge_buffer(sched):
    """A strategy buffer would scale with the EDGE. This scales only with the FILL COUNT."""
    nev = F.net_executable_ev(0.70, 0.62, 100, sched, series_ticker=SERIES, as_of=AS_OF)
    fat = F.net_executable_ev(0.95, 0.62, 100, sched, series_ticker=SERIES, as_of=AS_OF)
    assert fat.fee_uncertainty_dollars == pytest.approx(nev.fee_uncertainty_dollars), \
        "the bound must not move when the edge does"
    bigger = F.net_executable_ev(0.70, 0.62, 200, sched, series_ticker=SERIES, as_of=AS_OF)
    assert bigger.fee_uncertainty_dollars > nev.fee_uncertainty_dollars, \
        "it must move when the SIZE does"


def test_the_schedule_defaults_to_unknown_granularity_and_says_why(sched):
    assert sched.granularity_state_for(SERIES) == F.GRANULARITY_UNKNOWN
    assert sched.granularity_state_for("KXANYTHING") == F.GRANULARITY_UNKNOWN
    g = sched.granularity
    assert g["fractional_increment"] == 0.01
    assert "0.01-contract minimum" in g["why_unknown_is_the_default"]
    assert "PROVES" in g["how_to_set_a_series_to_whole_contracts"]


# ---- fee-change identity: one series can carry several changes ---------------------------------------
#
# Keying observations on the series alone collapses every change for that series into whichever the loop saw
# last -- and because `show_historical=true` is deliberate, one series routinely carries a past change and a
# scheduled one at the same time. That is exactly how an applicable unmodelled change gets hidden behind a
# later, harmless one.

def ch(cid=None, *, series=SERIES, ts="2026-11-01T00:00:00Z", fee_type="quadratic", mult=2.0):
    d = {"series_ticker": series, "scheduled_ts": ts, "fee_type": fee_type, "fee_multiplier": mult}
    if cid is not None:
        d["id"] = cid
    return d


def test_the_official_id_is_the_identity_when_present():
    assert F.change_identity(ch("sfc_1")) == ("id", "sfc_1")
    assert F.change_identity(ch("sfc_1")) != F.change_identity(ch("sfc_2"))


def test_A_two_changes_for_one_series_both_survive(tmp_path, sched):
    obs = observations(tmp_path, snapshot(AS_OF - timedelta(hours=1), changes=[
        ch("sfc_1", ts="2026-10-01T00:00:00Z"),
        ch("sfc_2", ts="2026-12-01T00:00:00Z"),
    ]))
    got = obs.announced_changes(AS_OF)
    assert len(got) == 2
    assert {c["id"] for c in got} == {"sfc_1", "sfc_2"}


def test_B_a_historical_and_a_future_change_on_one_series_both_survive(tmp_path, sched):
    past, future = AS_OF - timedelta(days=30), AS_OF + timedelta(days=30)
    obs = observations(tmp_path, snapshot(AS_OF - timedelta(hours=1), changes=[
        ch("sfc_past", ts=past.isoformat()), ch("sfc_future", ts=future.isoformat()),
    ]))
    got = obs.announced_changes(AS_OF)
    assert len(got) == 2
    effs = sorted(F._change_effective(c) for c in got)
    assert effs == [past, future]


def test_C_the_same_change_across_weekly_snapshots_is_one_logical_change(tmp_path):
    weeks = [snapshot(AS_OF - timedelta(days=d), changes=[ch("sfc_1")]) for d in (21, 14, 7)]
    got = observations(tmp_path, *weeks).announced_changes(AS_OF)
    assert len(got) == 1
    assert got[0]["_observed_at"] == (AS_OF - timedelta(days=7)).isoformat(), \
        "the newest observation of a change wins"


def test_D_the_no_id_fallback_is_deterministic_and_still_distinguishes():
    a = ch(ts="2026-10-01T00:00:00Z")
    b = ch(ts="2026-12-01T00:00:00Z")
    assert F.change_identity(a) == F.change_identity(dict(a)), "same change -> same identity, every time"
    assert F.change_identity(a) != F.change_identity(b), "different scheduled_ts -> different change"
    assert F.change_identity(a) != F.change_identity(ch(ts="2026-10-01T00:00:00Z", mult=3.0))
    assert F.change_identity(a) != F.change_identity(ch(ts="2026-10-01T00:00:00Z", fee_type="other"))
    assert F.change_identity(a)[0] == "derived"


def test_D_two_undated_changes_on_one_series_do_not_collapse():
    """The old key was `(series, effective_at)`; with no `effective_at` both became `(series, None)`."""
    bare_a = {"series_ticker": SERIES, "fee_multiplier": 2.0}
    bare_b = {"series_ticker": SERIES, "fee_multiplier": 3.0}
    assert F.change_identity(bare_a) != F.change_identity(bare_b)


def test_E_an_applicable_unmodelled_change_cannot_be_hidden_behind_a_later_one(tmp_path, sched):
    """The failure this identity fix exists to prevent, end to end at the gate.

    An unmodelled change that took effect BEFORE this decision must still block, even when the same series
    also carries a later change that does not apply yet.
    """
    live = AS_OF - timedelta(days=2)
    future = AS_OF + timedelta(days=60)
    obs = observations(tmp_path, snapshot(AS_OF - timedelta(hours=1), changes=[
        ch("sfc_live", ts=live.isoformat()),
        ch("sfc_later", ts=future.isoformat()),
    ]))
    v = sched.verification(SERIES, AS_OF, obs)
    assert v["state"] == F.PENDING_CHANGE
    assert [c["id"] for c in v["pending_changes"]] == ["sfc_live"], \
        "the live change must survive the presence of a later one"
