"""PR #241 (2026-11-03): GAME-SPECIFIC quarterback confirmation validity (replaces the blanket 48 h age).

A confirmation counts for ONE game_id and ONE of that game's teams, from an accepted source, observed before kickoff and before the decision,
fresh on two clocks (24 h before the decision, inside the last 48 h before kickoff), not withdrawn by a later OUT / non-confirming record,
not in conflict with a different quarterback. Every non-confirmed outcome carries a reason code and provenance. Time is always explicit.
"""
from datetime import datetime, timedelta, timezone

import pytest

from nfl_edge.postmortem import guards as GD
from nfl_edge.postmortem import integration as PM
from nfl_edge.postmortem import qb_confirmations as Q

KO = datetime(2026, 11, 8, 18, 0, tzinfo=timezone.utc)
NOW = KO - timedelta(hours=3)
GAME = "2026_09_SF_ATL"
H = timedelta(hours=1)


def rec(team="SF", qb="00-QBSF", status=Q.CONFIRMED_STARTER, source="HEAD_COACH_STATEMENT_ON_RECORD", observed=None, captured=None, rid=None, game=GAME, **kw):
    observed = observed or (NOW - 2 * H)
    captured = captured or observed
    r = {"record_id": rid or f"r-{game}-{team}-{qb}-{status}-{observed.isoformat()}", "game_id": game, "team": team, "qb_player_id": qb, "status": status,
         "source_type": source, "source_ref": "https://example.org/source", "observed_at": observed.isoformat(), "captured_at": captured.isoformat(),
         "captured_by": "tester"}
    r.update(kw)
    return r


def valid(*records):
    v, rej = Q.validate_records(list(records))
    assert not rej, rej
    return v


def resolve(records, team="SF", as_of=NOW, kickoff=KO, game=GAME, **kw):
    return Q.resolve_team(records, game_id=game, team=team, kickoff=kickoff, as_of=as_of, **kw)


# ---- the windows -------------------------------------------------------------------------------------------------------------
def test_the_windows_are_tighter_than_the_old_blanket_and_documented():
    assert Q.MAX_AGE_AT_DECISION_MIN == 24 * 60 < 48 * 60 and Q.MAX_LEAD_BEFORE_KICKOFF_MIN == 48 * 60
    assert not hasattr(Q, "CONFIRMATION_MAX_AGE_MIN"), "the blanket 48 h age is gone"


@pytest.mark.parametrize("age_h,ok", [(0.1, True), (23.9, True), (24.0, True), (24.01, False), (30, False)])
def test_age_at_decision_boundary(age_h, ok):
    # decision 3 h before kickoff, so the 48 h lead window is never the binding one here
    row = resolve(valid(rec(observed=NOW - timedelta(hours=age_h))))
    assert (row["status"] == Q.CONFIRMED_STARTER) is ok, row
    if not ok:
        assert row["status"] == Q.UNKNOWN and row["reason"] == Q.REASON_STALE and row["confirmed_at"] is None


@pytest.mark.parametrize("lead_h,ok", [(5, True), (47.9, True), (48.0, True), (48.01, False), (60, False)])
def test_lead_before_kickoff_boundary_is_the_final_report_window(lead_h, ok):
    # decision 1 h after the observation: age is tiny, so only the kickoff window can bind
    obs = KO - timedelta(hours=lead_h)
    row = resolve(valid(rec(observed=obs)), as_of=obs + H)
    assert (row["status"] == Q.CONFIRMED_STARTER) is ok, row
    if not ok:
        assert row["reason"] == Q.REASON_TOO_EARLY and row["lead_before_kickoff_min"] > 48 * 60


def test_a_confirmation_can_be_fresh_for_one_decision_and_stale_for_a_later_one():
    r = valid(rec(observed=KO - timedelta(hours=30)))
    assert resolve(r, as_of=KO - timedelta(hours=20))["status"] == Q.CONFIRMED_STARTER
    assert resolve(r, as_of=KO - timedelta(hours=2))["reason"] == Q.REASON_STALE        # same record, later decision


def test_windows_are_parameters_that_can_only_tighten_the_default_behaviour():
    r = valid(rec(observed=NOW - 2 * H))
    assert resolve(r, max_age_min=60)["reason"] == Q.REASON_STALE
    assert resolve(r, max_lead_min=60)["reason"] == Q.REASON_TOO_EARLY


# ---- game and team specificity -------------------------------------------------------------------------------------------------
def test_a_confirmation_for_another_game_never_confirms_this_one():
    r = valid(rec(game="2026_09_KC_BUF"))
    assert resolve(r) is None


def test_a_confirmation_for_a_team_not_in_the_game_never_confirms_either_side():
    r = valid(rec(team="KC", qb="00-QBKC"))
    res = Q.resolve_game(r, game_id=GAME, teams=["ATL", "SF"], kickoff=KO, as_of=NOW)
    assert res == {}


def test_each_team_is_resolved_on_its_own_records_only():
    r = valid(rec(), rec(team="ATL", qb="00-QBATL", status=Q.OUT, source="INJURY_REPORT"))
    res = Q.resolve_game(r, game_id=GAME, teams=["ATL", "SF"], kickoff=KO, as_of=NOW)
    assert res["SF"]["status"] == Q.CONFIRMED_STARTER and res["ATL"]["status"] == Q.OUT


def test_the_guard_rejudges_a_row_for_another_game_or_team():
    base = {"status": "CONFIRMED_STARTER", "confirmed_at": (NOW - H).isoformat(), "source": "HEAD_COACH_STATEMENT_ON_RECORD"}
    kw = dict(dec=NOW, ko=KO, max_age=Q.MAX_AGE_AT_DECISION_MIN, max_lead=Q.MAX_LEAD_BEFORE_KICKOFF_MIN)
    assert GD._qb_blocks("SF", dict(base, game_id=GAME, team="SF"), game_id=GAME, **kw) == []
    assert GD._qb_blocks("SF", dict(base, game_id="other"), game_id=GAME, **kw) == ["QB_WRONG_GAME:SF"]
    assert GD._qb_blocks("SF", dict(base), game_id=GAME, **kw) == ["QB_WRONG_GAME:SF"]            # a row that does not say which game proves nothing
    assert GD._qb_blocks("SF", dict(base, game_id=GAME, team="ATL"), game_id=GAME, **kw) == ["QB_WRONG_TEAM:SF"]


# ---- time ordering ------------------------------------------------------------------------------------------------------------
def test_a_record_observed_or_captured_after_the_decision_is_invisible_so_history_is_not_rewritten():
    late = valid(rec(observed=NOW - H, captured=NOW + 10 * timedelta(minutes=1)))
    assert resolve(late) is None
    assert resolve(late, as_of=NOW + H)["status"] == Q.CONFIRMED_STARTER                  # visible only to a decision made after it was captured


def test_resolution_is_point_in_time_a_later_withdrawal_does_not_change_an_earlier_verdict():
    conf = rec(observed=NOW - 5 * H, rid="c")
    out = rec(status=Q.OUT, source="INJURY_REPORT", observed=NOW - H, rid="o")
    both = valid(conf, out)
    before = resolve(both, as_of=NOW - 2 * H)
    after = resolve(both, as_of=NOW)
    assert before["status"] == Q.CONFIRMED_STARTER and after["status"] == Q.OUT


def test_nothing_is_usable_without_an_explicit_clock_or_kickoff_and_no_wall_clock_default_exists():
    r = valid(rec())
    assert resolve(r, as_of=None) is None and resolve(r, kickoff=None) is None and resolve(r, as_of="2026-11-08T15:00:00") is None   # naive time refused
    import inspect
    assert inspect.signature(Q.resolve_team).parameters["as_of"].default is inspect.Parameter.empty


def test_a_statement_at_or_after_kickoff_is_not_pregame_evidence():
    r = valid(rec(observed=KO - timedelta(minutes=1), captured=KO + timedelta(minutes=1)))
    assert resolve(r, as_of=KO - timedelta(seconds=1)) is None and resolve(r, as_of=KO + timedelta(minutes=2)) is None


# ---- accepted sources only -----------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("source", sorted(Q.NON_CONFIRMING_SOURCE_TYPES))
def test_no_non_accepted_source_can_confirm_at_the_resolver_or_the_guard(source):
    assert Q.validate_records([rec(source=source)])[0] == []
    row = {"status": "CONFIRMED_STARTER", "confirmed_at": (NOW - H).isoformat(), "source": source, "game_id": GAME}
    out = GD._qb_blocks("SF", row, dec=NOW, ko=KO, game_id=GAME, max_age=1e9, max_lead=1e9)
    assert out == ["QB_SOURCE_NOT_ACCEPTED:SF"]
    assert GD._qb_blocks("SF", dict(row, source=None), dec=NOW, ko=KO, game_id=GAME, max_age=1e9, max_lead=1e9) == ["QB_SOURCE_NOT_ACCEPTED:SF"]


@pytest.mark.parametrize("source", sorted(Q.CONFIRMING_SOURCE_TYPES))
def test_each_accepted_source_confirms(source):
    assert resolve(valid(rec(source=source)))["status"] == Q.CONFIRMED_STARTER


# ---- superseded / conflicting / withdrawn -----------------------------------------------------------------------------------
def test_a_later_out_withdraws_with_its_own_reason_and_names_the_withdrawn_record():
    row = resolve(valid(rec(observed=NOW - 5 * H, rid="c"), rec(status=Q.OUT, source="INACTIVE_LIST", observed=NOW - H, rid="o")))
    assert row["status"] == Q.OUT and row["reason"] == Q.REASON_WITHDRAWN_OUT and row["withdrawn_record_ids"] == ["c"] and row["record_id"] == "o"


@pytest.mark.parametrize("status", [Q.EXPECTED_UNCONFIRMED, Q.UNKNOWN])
def test_a_later_non_confirming_record_withdraws_with_its_own_reason(status):
    row = resolve(valid(rec(observed=NOW - 5 * H, rid="c"), rec(status=status, source="DEPTH_CHART", observed=NOW - H, rid="d")))
    assert row["status"] == status and row["reason"] == Q.REASON_WITHDRAWN and row["confirmed_at"] is None


def test_a_non_confirming_record_alone_is_never_a_confirmation():
    row = resolve(valid(rec(status=Q.EXPECTED_UNCONFIRMED, source="DEPTH_CHART")))
    assert row["status"] == Q.EXPECTED_UNCONFIRMED and row["reason"] == Q.REASON_NOT_CONFIRMED


def test_a_confirmation_after_the_out_reinstates_it():
    row = resolve(valid(rec(status=Q.OUT, source="INJURY_REPORT", observed=NOW - 5 * H, rid="o"), rec(observed=NOW - H, rid="c")))
    assert row["status"] == Q.CONFIRMED_STARTER and row["record_id"] == "c"


def test_on_an_exact_time_tie_the_restrictive_record_wins_whatever_order_it_was_captured():
    t = NOW - 2 * H
    for cap_conf, cap_out in ((t, t + timedelta(minutes=1)), (t + timedelta(minutes=1), t)):
        row = resolve(valid(rec(observed=t, captured=cap_conf, rid="c"), rec(status=Q.OUT, source="INJURY_REPORT", observed=t, captured=cap_out, rid="o")))
        assert row["status"] == Q.OUT, (cap_conf, cap_out)


def test_conflicting_quarterbacks_are_unknown_with_both_record_ids_unless_deliberately_superseded():
    a, b = rec(qb="00-AAA", observed=NOW - 5 * H, rid="a"), rec(qb="00-BBB", observed=NOW - H, rid="b")
    row = resolve(valid(a, b))
    assert row["status"] == Q.UNKNOWN and row["reason"] == Q.REASON_CONFLICT and set(row["conflicts"]) == {"a"}
    assert resolve(valid(a, dict(b, supersedes=["a"])))["status"] == Q.CONFIRMED_STARTER


# ---- reason codes and provenance on every outcome --------------------------------------------------------------------------
PROVENANCE = ("game_id", "team", "record_id", "source", "source_ref", "observed_at", "captured_at", "as_of", "kickoff_utc", "qb_player_id", "window")


def _every_outcome():
    return {
        "confirmed": resolve(valid(rec())),
        "stale": resolve(valid(rec(observed=NOW - 30 * H))),
        "too_early": resolve(valid(rec(observed=KO - 60 * H)), as_of=KO - 59 * H),
        "conflict": resolve(valid(rec(qb="00-A", rid="a", observed=NOW - 3 * H), rec(qb="00-B", rid="b", observed=NOW - 2 * H))),
        "out": resolve(valid(rec(status=Q.OUT, source="INJURY_REPORT"))),
        "withdrawn": resolve(valid(rec(observed=NOW - 5 * H, rid="c"), rec(status=Q.OUT, source="INJURY_REPORT", observed=NOW - H, rid="o"))),
        "expected": resolve(valid(rec(status=Q.EXPECTED_UNCONFIRMED, source="DEPTH_CHART"))),
    }


def test_every_outcome_carries_provenance_and_the_clocks_it_was_judged_against():
    for name, row in _every_outcome().items():
        assert row is not None and all(k in row for k in PROVENANCE), (name, [k for k in PROVENANCE if k not in row])
        assert row["as_of"] == NOW.isoformat() or name == "too_early"
        assert row["game_id"] == GAME and row["team"] == "SF"
        assert (row["reason"] is None) == (row["status"] == Q.CONFIRMED_STARTER), name


def test_every_non_confirmed_outcome_blocks_at_the_gate_with_its_reason_code():
    for name, row in _every_outcome().items():
        if row["status"] == Q.CONFIRMED_STARTER:
            continue
        blocks = GD._qb_blocks("SF", row, dec=NOW, ko=KO, game_id=GAME, max_age=Q.MAX_AGE_AT_DECISION_MIN, max_lead=Q.MAX_LEAD_BEFORE_KICKOFF_MIN)
        assert "QB_NOT_CONFIRMED:SF" in blocks and f"QB_REASON:SF:{row['reason']}" in blocks, (name, blocks)


def test_the_pit_evidence_record_keeps_the_provenance_so_the_decision_can_be_audited():
    games = [{"game_id": GAME, "home_team": "ATL", "away_team": "SF", "kickoff_utc": KO.isoformat()}]
    recs = valid(rec(), rec(team="ATL", qb="00-QBATL", observed=NOW - 5 * H, rid="c"), rec(team="ATL", qb="00-QBATL", status=Q.OUT, source="INJURY_REPORT", observed=NOW - H, rid="o"))
    run = {"qb_confirmations": Q.resolve_slate(recs, games, as_of=NOW)}
    game = dict(games[0], data_freshness={"ledger_feature_cutoff": NOW.isoformat(), "context_capture": NOW.strftime("%Y%m%dT%H%M%SZ")})
    pit = PM.build_pit_evidence(run=run, game=game, ev={"fair_basis": "x"})
    assert pit["game_id"] == GAME and pit["qb_policy"]["max_age_at_decision_min"] == 24 * 60 and pit["qb_policy"]["max_lead_before_kickoff_min"] == 48 * 60
    assert pit["qb"]["SF"]["source_ref"] == "https://example.org/source" and pit["qb"]["SF"]["observed_at"] and pit["qb"]["SF"]["as_of"] == NOW.isoformat()
    assert pit["qb"]["ATL"]["reason"] == Q.REASON_WITHDRAWN_OUT and pit["qb"]["ATL"]["withdrawn_record_ids"] == ["c"]


def test_the_guard_rejudges_clocks_on_a_row_that_arrived_by_another_road():
    base = {"status": "CONFIRMED_STARTER", "source": "HEAD_COACH_STATEMENT_ON_RECORD", "game_id": GAME}
    kw = dict(dec=NOW, ko=KO, game_id=GAME, max_age=Q.MAX_AGE_AT_DECISION_MIN, max_lead=Q.MAX_LEAD_BEFORE_KICKOFF_MIN)
    assert GD._qb_blocks("SF", dict(base, confirmed_at=(NOW - 25 * H).isoformat()), **kw) == ["QB_CONFIRMATION_STALE:SF"]
    assert GD._qb_blocks("SF", dict(base, confirmed_at=(KO - 49 * H).isoformat()), **dict(kw, max_age=1e9)) == ["QB_CONFIRMATION_TOO_EARLY_BEFORE_KICKOFF:SF"]
    assert GD._qb_blocks("SF", dict(base, confirmed_at=(NOW + H).isoformat()), **kw) == ["QB_CONFIRMED_AFTER_DECISION:SF"]
    assert GD._qb_blocks("SF", dict(base, confirmed_at=(KO + H).isoformat()), **dict(kw, dec=KO + 2 * H)) == ["QB_CONFIRMED_AT_OR_AFTER_KICKOFF:SF"]
    assert GD._qb_blocks("SF", dict(base, confirmed_at=None), **kw) == ["QB_CONFIRMATION_TIME_MISSING:SF"]
    assert GD._qb_blocks("SF", None, **kw) == ["QB_UNKNOWN:SF"] and GD._qb_blocks("SF", {}, **kw) == ["QB_UNKNOWN:SF"]
