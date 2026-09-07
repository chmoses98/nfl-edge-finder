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


def snapshot(retrieved, *, changes=(), differences=(), errors=None):
    return {"retrieved_at": retrieved.isoformat(), "differences": list(differences),
            "errors": errors or {}, "fee_changes": {"changes": list(changes)}}


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


def test_fee_changes_are_parsed_from_every_response_shape():
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415

    class Client:
        def __init__(self, body):
            self.body = body

        def series_fee_changes(self):
            return self.body

    payload = {"series_ticker": SERIES, "effective_at": "2026-11-01T00:00:00Z"}
    for body in ([payload], {"fee_changes": [payload]}, {"changes": [payload]},
                 {SERIES: {"effective_at": "2026-11-01T00:00:00Z"}}):
        got = CAP.fetch_fee_changes(Client(body))
        assert got["error"] is None
        assert len(got["changes"]) == 1, body


def test_a_failing_fee_changes_call_is_reported_not_fatal():
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415

    class Boom:
        def series_fee_changes(self):
            raise RuntimeError("503")

    got = CAP.fetch_fee_changes(Boom())
    assert got["changes"] == [] and "503" in got["error"]


def test_the_capture_script_never_writes_the_committed_config():
    """Capture, surface, block, review. An API response must not rewrite the ledger's pricing history."""
    import scripts.kalshi.capture_fee_metadata as CAP        # noqa: PLC0415
    src = open(CAP.__file__).read()
    for forbidden in ("open(REG_PATH, \"w\")", "kalshi_fee_schedule.json\", \"w\"", "json.dump(reg"):
        assert forbidden not in src


# ---- the rounding residual ------------------------------------------------------------------------------

def test_the_bound_is_the_ceiling_term_plus_one_accumulator_residual():
    u = F.rounding_uncertainty(100, F.CENT)
    assert u["max_fills"] == 100, "a Kalshi fill is at least one whole contract"
    assert u["trade_fee_ceiling_bound"] == pytest.approx(100 * 0.0001)
    assert u["accumulator_residual_bound"] == pytest.approx(0.01)
    assert u["bound_dollars"] == pytest.approx(0.02)


def test_the_bound_scales_with_size_not_with_price():
    small, large = F.rounding_uncertainty(10, F.CENT), F.rounding_uncertainty(1000, F.CENT)
    assert large["bound_dollars"] > small["bound_dollars"]
    assert small["bound_dollars"] == pytest.approx(0.01 + 10 * 0.0001)


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


def test_the_accumulator_residual_never_exceeds_one_cent():
    """The half of the derivation that makes the bound finite at all."""
    for n in (1, 2, 3, 7, 10, 50, 200):
        order = F.fee_for_order([(0.055, 1)] * n, 0.07, 1.0)
        assert 0 <= order["accumulator_final"] <= 0.01 + 1e-12, n


def test_conservative_net_ev_is_net_ev_less_the_bound(sched):
    nev = F.net_executable_ev(0.70, 0.62, 100, sched, series_ticker=SERIES, as_of=AS_OF)
    assert nev.is_known
    expected = F.rounding_uncertainty(100, F.CENT)["bound_dollars"]
    assert nev.fee_uncertainty_dollars == pytest.approx(expected)
    assert nev.conservative_net_ev_dollars == pytest.approx(nev.net_ev_dollars - expected)
    assert nev.fee_uncertainty["derivation"]


def test_the_bound_is_a_cost_bound_and_not_an_edge_buffer(sched):
    """Cents on a real position. A strategy buffer would scale with the edge; this scales with the FILLS."""
    nev = F.net_executable_ev(0.70, 0.62, 100, sched, series_ticker=SERIES, as_of=AS_OF)
    assert nev.fee_uncertainty_dollars < 0.05
    fat = F.net_executable_ev(0.95, 0.62, 100, sched, series_ticker=SERIES, as_of=AS_OF)
    assert fat.fee_uncertainty_dollars == pytest.approx(nev.fee_uncertainty_dollars), \
        "the bound must not move when the edge does"
