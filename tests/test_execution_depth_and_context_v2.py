"""Depth, size, inactives, availability transitions and the exchange cross-check, tested on their refusals.

Almost every test here is about what the system must NOT do: invent liquidity it never observed, call a player
active because a feed went quiet, replace a football result with the exchange's, count a dome's missing wind as
missing data, or let a size calculation touch canonical CLV.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.evaluation import availability_events as AE                    # noqa: E402
from nfl_edge.evaluation import coverage as CV                               # noqa: E402
from nfl_edge.evaluation import execution_depth as XD                        # noqa: E402
from nfl_edge.settlement import crosscheck as XC                             # noqa: E402
from nfl_edge.shadow_v2 import inactives as IN                               # noqa: E402

BOOK_TS = "2026-09-13T15:30:00+00:00"
AS_OF = "2026-09-13T15:40:00+00:00"
KICK = "2026-09-13T17:00:00+00:00"


def book(no_levels, yes_levels=(("0.0100", "500.00"),), observed_at=BOOK_TS):
    return {"ticker": "T", "run_id": "R1", "observed_at": observed_at,
            "orderbook_fp": {"no_dollars": [list(x) for x in no_levels], "yes_dollars": [list(x) for x in yes_levels]}}


# ---------------------------------------------------------------------------------- depth: no book, no number
def test_a_missing_book_yields_no_number_and_a_named_reason():
    t = XD.execution_table(None, "YES", fair=0.6, as_of=AS_OF, not_captured_reason="DROPPED_BY_BUDGET")
    assert t["state"] == XD.DEPTH_NOT_CAPTURED and t["rows"] == [] and t["reason_code"] == "DROPPED_BY_BUDGET"
    assert XD.record_block(t) == {"state": XD.DEPTH_NOT_CAPTURED, "why": "DROPPED_BY_BUDGET"}


def test_an_empty_side_is_not_the_same_as_an_uncaptured_book():
    t = XD.execution_table(book([]), "YES", fair=0.6, as_of=AS_OF)
    assert t["state"] == XD.DEPTH_EMPTY_SIDE and t["state"] != XD.DEPTH_NOT_CAPTURED


def test_the_top_level_size_is_never_extrapolated_down_the_ladder():
    """One contract at 0.35 and the rest far worse: a 10-contract walk must not price at the top of book."""
    t = XD.execution_table(book([("0.6500", "1.00"), ("0.6000", "9.00"), ("0.5000", "200.00")]), "YES", as_of=AS_OF)
    r1 = next(r for r in t["rows"] if r["size"] == 1)
    r10 = next(r for r in t["rows"] if r["size"] == 10)
    assert r1["vwap"] == pytest.approx(0.35) and r1["worst_price"] == pytest.approx(0.35)
    assert r10["vwap"] > r1["vwap"], "ten contracts must cost more than one when the top level holds one"
    # 1 @ 0.35 then 9 @ 0.40: the walk pays 0.395 on average and 0.40 at the worst fill
    assert r10["vwap"] == pytest.approx(0.395, abs=1e-6) and r10["worst_price"] == pytest.approx(0.40)
    assert r10["slippage_vs_top"] == pytest.approx(0.05, abs=1e-6)


def test_a_partial_fill_is_reported_as_partial_and_never_priced_as_complete():
    t = XD.execution_table(book([("0.6000", "37.00")]), "YES", as_of=AS_OF)
    r100 = next(r for r in t["rows"] if r["size"] == 100)
    assert r100["fill_state"] == XD.PARTIAL and r100["filled"] == 37.0 and r100["shortfall"] == 63.0
    assert r100["vwap"] == pytest.approx(0.40), "the vwap is of what would actually have filled"


def test_an_unfillable_size_produces_no_price_at_all():
    t = XD.execution_table(book([]), "YES", as_of=AS_OF)
    assert t["state"] == XD.DEPTH_EMPTY_SIDE and not t.get("rows")
    w = XD.walk_contracts([], 10)
    assert w["fill_state"] == XD.UNFILLED and w["vwap"] is None and w["cost_dollars"] is None


def test_a_book_older_than_the_horizon_ceiling_is_labelled_stale_not_dropped():
    t = XD.execution_table(book([("0.6000", "500.00")], observed_at="2026-09-13T14:00:00+00:00"), "YES",
                           as_of=AS_OF, max_age_minutes=30.0)
    assert t["state"] == XD.DEPTH_STALE and t["rows"], "a stale book is still evidence, labelled"
    assert t["book_age_minutes"] == pytest.approx(100.0)


def test_an_unknown_fee_never_becomes_zero():
    t = XD.execution_table(book([("0.6000", "500.00")]), "YES", fair=0.7, as_of=AS_OF, schedule=None)
    r = t["rows"][0]
    assert r["fee_dollars"] is None and r["fee_state"] == "UNKNOWN" and r["net_ev_dollars"] is None


def test_size_adjusted_clv_needs_a_captured_book_at_both_ends():
    entry = XD.execution_table(book([("0.6000", "500.00")]), "YES", as_of=AS_OF)
    missing = XD.execution_table(None, "YES", as_of=AS_OF)
    out = XD.clv_after_depth(entry, missing)
    assert out["state"] == XD.DEPTH_NOT_CAPTURED and out["by_size"] == {}
    close = XD.execution_table(book([("0.5500", "500.00")]), "YES", as_of=AS_OF)
    ok = XD.clv_after_depth(entry, close)
    assert ok["state"] == XD.DEPTH_CAPTURED
    # the same purchase became more expensive at the close: positive, i.e. the market moved toward the model
    assert ok["by_size"]["10"]["clv_exec_after_depth"] == pytest.approx(0.05, abs=1e-6)


def test_the_depth_module_never_defines_or_overwrites_canonical_clv():
    """Part Q: top-of-book CLV keeps its own definition; size-adjusted execution lives in its own block."""
    src = open(os.path.join(ROOT, "nfl_edge", "evaluation", "execution_depth.py")).read()
    for forbidden in ("clv_mid_toward_model", "clv_exec_toward_model", "clv_net_of_fee", "SIGN_CONVENTION ="):
        assert forbidden not in src, f"{forbidden} must stay owned by nfl_edge/evaluation/clv.py"


# ---------------------------------------------------------------------------------- inactives: can only add
def summary_with(teams):
    return {"inactives": [{"team": {"abbreviation": t}, "athletes": [{"athlete": {"displayName": f"P{i}", "id": 100 + i},
                                                                     "status": {"name": "out"}} for i in range(n)]}
                          for t, n in teams]}


def test_an_empty_or_broken_response_produces_no_rows_at_all():
    for body in (None, {}, {"inactives": []}):
        rec = IN.observations(game_id="G", event_id="1", kickoff_utc=KICK, summary=body,
                              fetch_meta={}, observed_at="2026-09-13T15:30:00+00:00")
        assert rec["rows"] == [] and rec["usable"] is False
        assert all(t["state"] == IN.TEAM_ABSENT for t in rec["teams"])


def test_an_implausible_count_makes_the_whole_team_unusable_rather_than_half_true():
    rec = IN.observations(game_id="G", event_id="1", kickoff_utc=KICK, summary=summary_with([("KC", 40), ("DEN", 7)]),
                          fetch_meta={}, observed_at="2026-09-13T15:30:00+00:00")
    st = {t["team"]: t["state"] for t in rec["teams"]}
    assert st["KC"] == IN.TEAM_UNUSABLE and st["DEN"] == IN.TEAM_USABLE
    assert all(r["team"] == "DEN" for r in rec["rows"]), "no player rows survive an implausible team block"


def test_the_module_can_never_emit_an_active_state():
    rec = IN.observations(game_id="G", event_id="1", kickoff_utc=KICK, summary=summary_with([("KC", 7)]),
                          fetch_meta={}, observed_at="2026-09-13T15:30:00+00:00")
    assert {r["state"] for r in rec["rows"]} == {IN.INACTIVE_CONFIRMED}
    # the state cannot appear anywhere the module could emit it; the docstring explains why it is absent
    src = open(os.path.join(ROOT, "nfl_edge", "shadow_v2", "inactives.py")).read()
    code = src.split('"""', 2)[2]
    assert "EXPECTED_ACTIVE" not in code, "a source outage must never be able to say everyone is playing"
    assert "ACTIVE" not in code.replace("INACTIVE", "")


def test_absence_from_the_list_answers_unknown_not_active():
    rec = IN.observations(game_id="G", event_id="1", kickoff_utc=KICK, summary=summary_with([("KC", 7)]),
                          fetch_meta={}, observed_at="2026-09-13T15:30:00+00:00")
    bk = IN.InactivesBook([rec])
    assert bk.state("G", espn_id="100")["official_inactive_state"] == IN.INACTIVE_CONFIRMED
    miss = bk.state("G", player_name="Somebody Else")
    assert miss["official_inactive_state"] == "UNKNOWN" and "ABSENCE IS NOT EVIDENCE" in miss["reason"]


def test_an_observation_after_kickoff_is_labelled_postgame_and_freezes_nothing():
    rec = IN.observations(game_id="G", event_id="1", kickoff_utc=KICK, summary=summary_with([("KC", 7)]),
                          fetch_meta={}, observed_at="2026-09-13T18:30:00+00:00")
    assert rec["evidence_class"] == IN.POSTGAME and rec["rows"] == [] and rec["usable"] is False


def test_the_publication_window_drives_confidence():
    near = IN.observations(game_id="G", event_id="1", kickoff_utc=KICK, summary=summary_with([("KC", 7)]),
                           fetch_meta={}, observed_at="2026-09-13T15:30:00+00:00")
    early = IN.observations(game_id="G", event_id="1", kickoff_utc=KICK, summary=summary_with([("KC", 7)]),
                            fetch_meta={}, observed_at="2026-09-13T09:00:00+00:00")
    assert near["confidence"] == IN.HIGH and early["confidence"] == IN.MEDIUM


def test_inactives_are_not_wired_into_the_real_money_availability_gate():
    for rel in ("nfl_edge/settlement/availability.py", "nfl_edge/handicap/gates.py"):
        assert "shadow_v2.inactives" not in open(os.path.join(ROOT, rel)).read()


# ---------------------------------------------------------------------------------- availability transitions
def prec(h, obs, **pc):
    return {"record_id": f"r{h}", "subject_id": "P1", "game_id": "G1", "horizon_label": h, "observed_at": obs,
            "subject_kind": "player", "player_context": pc}


def test_a_downgrade_between_horizons_is_detected_with_both_raw_states_kept():
    recs = [prec("T-24h", "2026-09-12T17:00:00Z", availability_state="QUESTIONABLE"),
            prec("T-90m", "2026-09-13T15:30:00Z", availability_state="OUT")]
    (e,) = AE.transitions(recs)
    assert e["availability_direction"] == AE.DOWNGRADE and e["availability_changed_since_prior_horizon"]
    assert e["availability_from"] == "QUESTIONABLE" and e["availability_to"] == "OUT"


def test_a_source_going_quiet_is_not_a_downgrade():
    recs = [prec("T-24h", "2026-09-12T17:00:00Z", availability_state="EXPECTED_ACTIVE"),
            prec("T-6h", "2026-09-13T11:00:00Z", availability_state="UNKNOWN")]
    (e,) = AE.transitions(recs)
    assert e["availability_direction"] == AE.EVIDENCE_LOST
    s = AE.summarize([e])
    assert s["downgrades"] == 0 and s["upgrades"] == 0


def test_a_teammate_removal_and_a_qb_change_are_their_own_events():
    recs = [prec("T-24h", "2026-09-12T17:00:00Z", availability_state="EXPECTED_ACTIVE", teammates_out_or_doubtful=1, qb_schedule="QB_A"),
            prec("T-90m", "2026-09-13T15:30:00Z", availability_state="EXPECTED_ACTIVE", teammates_out_or_doubtful=3, qb_schedule="QB_B")]
    (e,) = AE.transitions(recs)
    assert e["key_teammate_removed"] and e["qb_status_changed"] and e["availability_direction"] == AE.NO_CHANGE


def test_an_unchanged_player_produces_no_event():
    recs = [prec("T-24h", "2026-09-12T17:00:00Z", availability_state="EXPECTED_ACTIVE", teammates_out_or_doubtful=1),
            prec("T-90m", "2026-09-13T15:30:00Z", availability_state="EXPECTED_ACTIVE", teammates_out_or_doubtful=1)]
    assert AE.transitions(recs) == []


def test_transitions_follow_observation_time_not_file_order():
    late = prec("T-90m", "2026-09-13T15:30:00Z", availability_state="OUT")
    early = prec("T-24h", "2026-09-12T17:00:00Z", availability_state="EXPECTED_ACTIVE")
    (e,) = AE.transitions([late, early])
    assert e["from_horizon"] == "T-24h" and e["to_horizon"] == "T-90m" and e["availability_direction"] == AE.DOWNGRADE


# ---------------------------------------------------------------------------------- exchange cross-check
def exch(result, status="finalized", value="1.0000"):
    return {"ticker": "T", "result": result, "status": status, "settlement_value_dollars": value,
            "settlement_ts": "2026-09-14T01:00:00Z", "source": "kalshi_discovery_settled_bucket"}


def test_agreement_and_disagreement_are_both_recorded_with_provenance():
    ok = XC.crosscheck_one("T", 1.0, "SETTLED", exch("yes"))
    assert ok["agreement"] == XC.AGREE and ok["hard_warning"] is False and ok["exchange_settlement_ts"]
    bad = XC.crosscheck_one("T", 1.0, "SETTLED", exch("no", value="0.0000"))
    assert bad["agreement"] == XC.DISAGREE and bad["hard_warning"] is True
    assert "RESEARCH-QUALITY WARNING" in bad["reason"] and bad["derived_settled_yes"] == 1.0


def test_the_exchange_never_rescues_a_failed_football_settlement():
    r = XC.crosscheck_one("T", None, "REFUSED_GAME_IDENTITY", exch("yes"), derived_reason="player identity unresolved")
    assert r["agreement"] == XC.DERIVED_MISSING and r["derived_settled_yes"] is None
    assert r["exchange_payout"] == 1.0, "the exchange value is recorded alongside, never substituted"


def test_a_non_terminal_exchange_status_is_not_a_disagreement():
    r = XC.crosscheck_one("T", 1.0, "SETTLED", exch("no", status="determined", value="0.0000"))
    assert r["agreement"] == XC.EXCHANGE_NON_TERMINAL and r["hard_warning"] is False


def test_a_missing_exchange_record_is_its_own_state():
    r = XC.crosscheck_one("T", 1.0, "SETTLED", None)
    assert r["agreement"] == XC.EXCHANGE_MISSING and r["hard_warning"] is False


def test_the_summary_names_the_families_that_disagree():
    rows = [XC.crosscheck_one("A", 1.0, "SETTLED", exch("no", value="0.0000"), market_family="PERIOD_WINNER"),
            XC.crosscheck_one("B", 1.0, "SETTLED", exch("yes"), market_family="GAME_WINNER")]
    s = XC.summarize(rows)
    assert s["n_disagreements"] == 1 and s["families_with_disagreement"] == ["PERIOD_WINNER"]
    assert s["agreement_rate"] == pytest.approx(0.5)


# ---------------------------------------------------------------------------------- coverage honesty
def test_a_dome_has_no_missing_wind():
    recs = [{"game_context": {"roof": "dome"}, "player_context": {"weather_state": "KNOWN", "wind_mph": None}},
            {"game_context": {"roof": "outdoors"}, "player_context": {"weather_state": "KNOWN", "wind_mph": 11.0}}]
    row = next(r for r in CV.audit(recs)["fields"] if r["field"] == "weather_wind")
    assert row[CV.NOT_APPLICABLE] == 1 and row[CV.KNOWN] == 1 and row[CV.UNKNOWN] == 0 and row["known_pct"] == 100.0


def test_an_unpublished_injury_report_is_not_counted_as_known():
    recs = [{"player_context": {"injury_state": "NOT_LISTED", "report_status": None}},
            {"player_context": {"injury_state": "LISTED", "report_status": "Questionable"}},
            {"player_context": {"injury_state": "LISTED", "report_status": None}}]
    row = next(r for r in CV.audit(recs)["fields"] if r["field"] == "injury_report_status")
    assert row[CV.NOT_APPLICABLE] == 1 and row[CV.KNOWN] == 1 and row[CV.UNKNOWN] == 1
    assert row["known_pct"] == 50.0, "a listed player with no status is a genuine gap and must not be hidden"


def test_depth_coverage_is_reported_by_disagreement_band_so_selection_bias_is_visible():
    recs = [{"contract_value": 0.50, "mid": 0.50, "depth": {"state": "DEPTH_CAPTURED"}},
            {"contract_value": 0.80, "mid": 0.50, "depth": {"state": "DEPTH_NOT_CAPTURED", "why": "DROPPED_BY_BUDGET"}}]
    d = CV.depth_coverage(recs)
    assert d["by_disagreement_band"]["0-0.5pp"]["captured_pct"] == 100.0
    assert d["by_disagreement_band"][">10pp"]["captured_pct"] == 0.0
    assert d["not_captured_reasons"] == {"DROPPED_BY_BUDGET": 1}
