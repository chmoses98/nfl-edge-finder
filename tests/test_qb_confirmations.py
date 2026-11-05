"""PR #232: the point-in-time CONFIRMED-STARTER quarterback source.

Owner rule (2026-11-02): a depth chart, an active roster, an inactive list, an injury-report status or a model expectation is NOT
confirmation of the actual starter and must never be relabelled CONFIRMED_STARTER. A confirmation needs a source that names the
starter, a time, provenance and freshness; unknown stays blocked.
"""
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

from nfl_edge.postmortem import integration as PM
from nfl_edge.postmortem import qb_confirmations as Q

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KO = datetime(2026, 11, 8, 18, 0, tzinfo=timezone.utc)
NOW = KO - timedelta(hours=3)
GAME = "2026_09_SF_ATL"


def rec(team="SF", qb="00-QBSF", status=Q.CONFIRMED_STARTER, source="HEAD_COACH_STATEMENT_ON_RECORD", observed=None, captured=None, rid=None, **kw):
    observed = observed or (NOW - timedelta(hours=2))
    captured = captured or observed
    r = {"record_id": rid or f"r-{team}-{qb}-{status}-{observed.isoformat()}", "game_id": GAME, "team": team, "qb_player_id": qb, "status": status,
         "source_type": source, "source_ref": "https://example.org/source", "observed_at": observed.isoformat(), "captured_at": captured.isoformat(),
         "captured_by": "tester"}
    r.update(kw)
    return r


def valid(*records):
    v, rej = Q.validate_records(list(records))
    assert not rej, rej
    return v


def resolve(records, team="SF", as_of=NOW, **kw):
    return Q.resolve_team(records, game_id=GAME, team=team, kickoff=KO, as_of=as_of, **kw)


# ------------------------------------------------------------------------------------------------ validation (fail closed)
@pytest.mark.parametrize("source", sorted(Q.NON_CONFIRMING_SOURCE_TYPES))
def test_a_depth_chart_roster_inactive_list_injury_report_or_model_can_never_confirm_a_starter(source):
    v, rej = Q.validate_records([rec(source=source, status=Q.CONFIRMED_STARTER)])
    assert v == [] and rej[0]["code"] == Q.R_NONCONFIRMING_CANNOT_CONFIRM


@pytest.mark.parametrize("source", sorted(Q.NON_CONFIRMING_SOURCE_TYPES))
def test_the_same_sources_may_record_expected_or_out_but_that_is_not_a_confirmation(source):
    v = valid(rec(source=source, status=Q.EXPECTED_UNCONFIRMED))
    row = resolve(v)
    assert row["status"] == Q.EXPECTED_UNCONFIRMED and row["confirmed_at"] is None


def test_unknown_source_types_and_statuses_are_rejected():
    _, rej = Q.validate_records([rec(source="SLEEPER_VIBES"), rec(status="PROBABLY_STARTING", rid="x")])
    assert {r["code"] for r in rej} == {Q.R_BAD_SOURCE_TYPE, Q.R_BAD_STATUS}


@pytest.mark.parametrize("field", Q.REQUIRED_FIELDS)
def test_every_required_field_is_required(field):
    r = rec()
    r.pop(field)
    _, rej = Q.validate_records([r])
    assert rej and rej[0]["code"].startswith("MISSING_FIELD") and field in rej[0]["code"]


def test_missing_naive_or_garbled_timestamps_are_rejected_never_assumed_utc():
    for bad in ("2026-11-08T12:00:00", "yesterday", ""):
        _, rej = Q.validate_records([rec(observed_at=bad)])
        assert rej, bad
    r = rec()
    r["captured_at"] = "2026-11-08T12:00:00"
    assert Q.validate_records([r])[1][0]["code"] == "BAD_TIMESTAMP:captured_at"


def test_observed_after_captured_is_rejected():
    obs = NOW - timedelta(hours=1)
    _, rej = Q.validate_records([rec(observed=obs, captured=obs - timedelta(minutes=5))])
    assert rej[0]["code"] == Q.R_OBSERVED_AFTER_CAPTURED


def test_duplicate_record_ids_are_rejected():
    _, rej = Q.validate_records([rec(rid="same"), rec(rid="same", team="ATL", qb="00-QBATL")])
    assert [r["code"] for r in rej] == [Q.R_DUP_ID]


def test_the_old_team_keyed_file_without_provenance_is_refused(tmp_path):
    p = tmp_path / "old.json"
    p.write_text(json.dumps({"SF": {"status": "CONFIRMED_STARTER", "confirmed_at": NOW.isoformat(), "source": "inactive_list"}}))
    with pytest.raises(ValueError, match="no longer accepted"):
        Q.load_records_file(str(p))


def test_jsonl_ledger_and_directory_loading_round_trip(tmp_path):
    a, b = rec(), rec(team="ATL", qb="00-QBATL")
    (tmp_path / "2026.jsonl").write_text("\n".join(json.dumps(x) for x in (a, b)) + "\n")
    v, rej = Q.load_records_file(str(tmp_path))
    assert len(v) == 2 and not rej
    (tmp_path / "bad.jsonl").write_text("{not json\n")
    with pytest.raises(ValueError):
        Q.load_records_file(str(tmp_path))


# ------------------------------------------------------------------------------------------------ resolution
def test_a_fresh_named_starter_is_confirmed_with_the_time_the_source_said_it():
    obs = NOW - timedelta(hours=2)
    row = resolve(valid(rec(observed=obs)))
    assert row["status"] == Q.CONFIRMED_STARTER and row["confirmed_at"] == obs.isoformat() and row["source"] == "HEAD_COACH_STATEMENT_ON_RECORD"


def test_no_record_means_absent_so_the_gate_says_qb_unknown():
    assert resolve([]) is None and resolve(valid(rec(team="ATL", qb="00-QBATL"))) is None


def test_a_confirmation_older_than_the_freshness_window_is_stale_and_unknown():
    row = resolve(valid(rec(observed=NOW - timedelta(minutes=Q.CONFIRMATION_MAX_AGE_MIN + 1))))
    assert row["status"] == Q.UNKNOWN and row["reason"] == "STALE_CONFIRMATION" and row["confirmed_at"] is None


def test_a_record_captured_after_the_decision_time_is_invisible():
    later = NOW + timedelta(minutes=10)
    assert resolve(valid(rec(observed=NOW - timedelta(hours=1), captured=later))) is None


def test_nothing_is_usable_at_or_after_kickoff():
    r = valid(rec(observed=KO - timedelta(hours=4)))
    assert resolve(r, as_of=KO) is None and resolve(r, as_of=KO + timedelta(minutes=1)) is None


def test_a_record_captured_at_or_after_kickoff_is_never_pregame_evidence():
    r = valid(rec(observed=KO - timedelta(minutes=1), captured=KO + timedelta(minutes=1)))
    assert resolve(r, as_of=KO + timedelta(minutes=2)) is None


def test_a_later_out_or_expected_record_withdraws_an_earlier_confirmation():
    early = rec(observed=NOW - timedelta(hours=5))
    for status in (Q.OUT, Q.EXPECTED_UNCONFIRMED, Q.UNKNOWN):
        late = rec(status=status, source="INJURY_REPORT", observed=NOW - timedelta(hours=1), rid=f"late-{status}")
        row = resolve(valid(early, late))
        assert row["status"] == status and row["confirmed_at"] is None


def test_two_different_confirmed_quarterbacks_conflict_and_are_unknown():
    a = rec(qb="00-AAA", observed=NOW - timedelta(hours=5), rid="a")
    b = rec(qb="00-BBB", observed=NOW - timedelta(hours=1), rid="b")
    row = resolve(valid(a, b))
    assert row["status"] == Q.UNKNOWN and row["reason"] == "CONFLICTING_CONFIRMATIONS" and "a" in row["conflicts"]


def test_a_deliberate_supersession_resolves_the_conflict_with_an_audit_trail():
    a = rec(qb="00-AAA", observed=NOW - timedelta(hours=5), rid="a")
    b = rec(qb="00-BBB", observed=NOW - timedelta(hours=1), rid="b", supersedes=["a"])
    row = resolve(valid(a, b))
    assert row["status"] == Q.CONFIRMED_STARTER and row["qb_player_id"] == "00-BBB"


def test_simultaneous_confirmations_of_different_quarterbacks_conflict():
    t = NOW - timedelta(hours=1)
    row = resolve(valid(rec(qb="00-AAA", observed=t, rid="a"), rec(qb="00-BBB", observed=t, rid="b", supersedes=["a"])))
    assert row["status"] == Q.UNKNOWN


def test_the_same_quarterback_confirmed_twice_is_fine():
    row = resolve(valid(rec(observed=NOW - timedelta(hours=5), rid="a"), rec(observed=NOW - timedelta(hours=1), rid="b")))
    assert row["status"] == Q.CONFIRMED_STARTER


# ------------------------------------------------------------------------------------------------ slate coverage + gate bridge
GAMES = [{"game_id": GAME, "home_team": "ATL", "away_team": "SF", "kickoff_utc": KO.isoformat()},
         {"game_id": "2026_09_KC_BUF", "home_team": "BUF", "away_team": "KC", "kickoff_utc": KO.isoformat()}]


def test_coverage_counts_only_games_with_both_quarterbacks_confirmed():
    recs = valid(rec(), rec(team="ATL", qb="00-QBATL"),
                 dict(rec(team="KC", qb="00-QBKC"), game_id="2026_09_KC_BUF"))             # BUF absent
    res = Q.resolve_slate(recs, GAMES, as_of=NOW)
    cov = Q.coverage(res, GAMES, as_of=NOW)
    assert cov["games"] == 2 and cov["games_both_qbs_confirmed"] == 1 and cov["games_blocked_qb"] == 1
    assert cov["team_slots_not_confirmed_by_reason"] == {"ABSENT": 1}
    assert [g["both_confirmed"] for g in cov["per_game"]] == [True, False]


def test_with_no_source_every_game_is_blocked_and_the_report_says_so():
    cov = Q.coverage(Q.resolve_slate([], GAMES, as_of=NOW), GAMES, as_of=NOW)
    assert cov["games_both_qbs_confirmed"] == 0 and cov["team_slots_not_confirmed_by_reason"] == {"ABSENT": 4}


def test_the_gate_sees_only_resolved_rows_and_a_depth_chart_stays_unconfirmed():
    recs = valid(rec(), rec(team="ATL", qb="00-QBATL", status=Q.EXPECTED_UNCONFIRMED, source="DEPTH_CHART"))
    run = {"qb_confirmations": Q.resolve_slate(recs, GAMES[:1], as_of=NOW)}
    game = dict(GAMES[0], data_freshness={"ledger_feature_cutoff": NOW.isoformat(), "context_capture": NOW.strftime("%Y%m%dT%H%M%SZ")})
    pit = PM.build_pit_evidence(run=run, game=game, ev={"fair_basis": "x"})
    assert pit["qb"]["SF"]["status"] == Q.CONFIRMED_STARTER and pit["qb"]["ATL"]["status"] == Q.EXPECTED_UNCONFIRMED
    from nfl_edge.postmortem.guards import guard_candidate
    out = guard_candidate({"ticker": "KXNFLSPREAD-26NOV08SFATL-SF3", "side": "YES", "decision_time": NOW, "kickoff_utc": KO,
                           "projection_as_of": NOW, "injuries_as_of": NOW, "qb": pit["qb"], "teams": pit["teams"],
                           "quote": {"price": 0.5, "captured_at": NOW, "kind": "EXECUTABLE_ASK", "depth": 100}, "contracts": 10})
    assert out["blocks"] == ["QB_NOT_CONFIRMED:ATL"]


def test_props_are_not_blocked_by_the_game_level_quarterback_rule():
    from nfl_edge.postmortem.guards import guard_candidate
    out = guard_candidate({"ticker": "KXNFLRECYDS-26NOV08SFATL-SFWR1-60", "side": "YES", "decision_time": NOW, "kickoff_utc": KO,
                           "projection_as_of": NOW, "injuries_as_of": NOW, "qb": {}, "teams": ["ATL", "SF"],
                           "quote": {"price": 0.5, "captured_at": NOW, "kind": "EXECUTABLE_ASK", "depth": 100}, "contracts": 10})
    assert not any(b.startswith("QB_") for b in out["blocks"])


# ------------------------------------------------------------------------------------------------ the intake script
def _packet(tmp_path, kickoff=KO):
    p = tmp_path / "packet.json"
    p.write_text(json.dumps({"games": [{"game_id": GAME, "season": 2026, "home_team": "ATL", "away_team": "SF", "kickoff_utc": kickoff.isoformat()}]}))
    return str(p)


def _append(tmp_path, *extra, now=None, **over):
    sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))
    import importlib
    ap = importlib.import_module("qb_confirm_append")
    args = {"--ledger-dir": str(tmp_path / "ledger"), "--packet": _packet(tmp_path), "--game-id": GAME, "--team": "SF", "--qb-player-id": "00-QBSF",
            "--status": "CONFIRMED_STARTER", "--source-type": "HEAD_COACH_STATEMENT_ON_RECORD", "--source-ref": "https://example.org/pc",
            "--observed-at": (NOW - timedelta(hours=1)).isoformat(), "--captured-by": "owner", "--now": (now or NOW).isoformat()}
    args.update(over)
    argv = [x for kv in args.items() for x in kv] + list(extra)
    return ap.main(argv)


def test_intake_appends_one_validated_line_and_a_resubmission_is_a_noop(tmp_path, capsys):
    assert _append(tmp_path) == 0 and "APPENDED" in capsys.readouterr().out
    assert _append(tmp_path) == 0 and "DUPLICATE_NOOP" in capsys.readouterr().out
    lines = (tmp_path / "ledger" / "2026.jsonl").read_text().splitlines()
    assert len(lines) == 1 and json.loads(lines[0])["captured_by"] == "owner"
    v, rej = Q.load_records_file(str(tmp_path / "ledger"))
    assert len(v) == 1 and not rej


def test_intake_is_append_only_a_later_record_never_touches_earlier_lines(tmp_path):
    assert _append(tmp_path) == 0
    path = tmp_path / "ledger" / "2026.jsonl"
    first = path.read_text()
    assert _append(tmp_path, **{"--team": "ATL", "--qb-player-id": "00-QBATL"}) == 0
    after = path.read_text()
    assert after.startswith(first) and len(after.splitlines()) == 2        # the earlier bytes are untouched; only a line was added
    assert _append(tmp_path) == 0 and path.read_text() == after            # a repeat of an old assertion changes nothing


@pytest.mark.parametrize("over,why", [
    ({"--source-type": "DEPTH_CHART"}, "NON_CONFIRMING"),
    ({"--source-type": "NOT_A_SOURCE"}, "SOURCE_TYPE_NOT_ALLOWLISTED"),
    ({"--game-id": "2026_09_XX_YY"}, "GAME_NOT_IN_PACKET"),
    ({"--team": "KC"}, "TEAM_NOT_IN_GAME"),
    ({"--observed-at": "2026-11-08T10:00:00"}, "BAD_TIMESTAMP"),
    ({"--observed-at": (NOW + timedelta(hours=1)).isoformat()}, "OBSERVED_IN_THE_FUTURE"),
    ({"--now": (KO + timedelta(minutes=1)).isoformat()}, "AFTER_KICKOFF"),
])
def test_intake_refuses_and_writes_nothing(tmp_path, capsys, over, why):
    assert _append(tmp_path, **over) == 2
    assert why in capsys.readouterr().err
    assert not (tmp_path / "ledger").exists() or not any((tmp_path / "ledger").iterdir())


def test_intake_supersedes_must_name_an_existing_record(tmp_path, capsys):
    assert _append(tmp_path, **{"--supersedes": "qbc-nope"}) == 2
    assert "SUPERSEDES_UNKNOWN_RECORD" in capsys.readouterr().err
