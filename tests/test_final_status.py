"""A populated score is not a final status, and elapsed time is not evidence.

The failure this file exists to prevent: nflverse rebuilds `games.csv` on a schedule, so a row can carry a score
while the game is still being played. Settling from that row would write a permanent evaluation of a game that
had not finished -- and because the corpus is immutable, the later correction would be a conflict, not a fix.

So FINAL needs the postgame-only fields to agree with the scores AND something independent to say the game is
complete. ESPN can add that proof or expose a contradiction; it can never be required, because a source whose
outage stops settlement is a source whose failure mode is unsafe.
"""
import copy
import json
import os

import pytest

from nfl_edge.settlement import settle as S
from nfl_edge.settlement.final_status import (
    ESPN_SCOREBOARD, POSTGAME_TABLES, attestations_from_espn_scoreboard, fetch_espn_scoreboard, verify_final,
)
from nfl_edge.settlement.results import (
    DEFER_FINAL_UNPROVEN, DEFER_NOT_FINAL, DEGRADED_INCONSISTENT, FINAL, NOT_FINAL, READY,
    game_from_schedule_row, result_book_from_records,
)

GAME = "2025_01_DAL_PHI"
ESPN_ID = "401772510"                   # the real espn id on the fixture's schedule row
FIXTURE = os.path.join(os.path.dirname(__file__), "fixtures", "postgame", "dal_phi_2025_w1.results.json")
LONG_AFTER = "2025-09-06T00:00:00+00:00"          # a full day after kickoff


@pytest.fixture
def records():
    with open(FIXTURE) as f:
        rec = json.load(f)
    rec["game_id"] = GAME
    return rec


def with_schedule(records, **cells):
    """Rewrite named columns of the fixture's schedule row for this game."""
    rec = copy.deepcopy(records)
    lines = rec["schedule_csv"].splitlines()
    header = lines[0].split(",")
    out = []
    for line in lines[1:]:
        c = line.split(",")
        if c[0] == GAME:
            for name, value in cells.items():
                c[header.index(name)] = "" if value is None else str(value)
        out.append(",".join(c))
    rec["schedule_csv"] = "\n".join([lines[0]] + out)
    return rec


def row(**cells):
    base = {"game_id": GAME, "season": "2025", "week": "1", "game_type": "REG", "gameday": "2025-09-04",
            "gametime": "20:20", "away_team": "DAL", "home_team": "PHI", "away_score": "20",
            "home_score": "24", "result": "4", "total": "44", "overtime": "0", "espn": ESPN_ID}
    base.update(cells)
    return base


def espn_payload(*, completed=True, state="post", home=24, away=20, event_id=ESPN_ID, detail="Final"):
    """The shape ESPN's scoreboard actually returns (see scripts/data/probe_sources.py)."""
    return {"events": [{"id": event_id, "shortName": "DAL @ PHI", "date": "2025-09-05T00:20Z",
                        "competitions": [{"id": event_id,
                                          "status": {"type": {"completed": completed, "state": state,
                                                              "detail": detail, "name": "STATUS_FINAL"}},
                                          "competitors": [
                                              {"homeAway": "home", "score": str(home),
                                               "team": {"abbreviation": "PHI"}},
                                              {"homeAway": "away", "score": str(away),
                                               "team": {"abbreviation": "DAL"}}]}]}]}


# ---------------------------------------------------------------- provisional rows
def test_a_score_without_the_postgame_only_fields_is_not_final():
    """This is what a live or provisional schedule row looks like: scores, nothing computed beside them."""
    g = game_from_schedule_row(row(result=None, total=None, overtime=None))
    assert g.status == NOT_FINAL
    assert g.home_score == 24.0 and g.away_score == 20.0, "the scores are still read and reported"
    assert "postgame-only field" in g.provisional_reason


@pytest.mark.parametrize("missing", ["result", "total", "overtime"])
def test_any_missing_postgame_field_blocks_final(missing):
    g = game_from_schedule_row(row(**{missing: None}))
    assert g.status == NOT_FINAL and missing in g.provisional_reason


def test_a_provisional_row_still_defers_a_full_day_after_kickoff(records):
    """Elapsed time is a plausibility guard, never proof. Four hours -- or twenty-four -- changes nothing."""
    from datetime import datetime
    rec = with_schedule(records, result=None, total=None, overtime=None)
    book = result_book_from_records(rec, min_hours_after_kickoff=4.0)
    state, reason = book.readiness(GAME, needs_player_stats=True, now=datetime.fromisoformat(LONG_AFTER))
    assert state == DEFER_NOT_FINAL
    assert "postgame-only field" in reason
    # and nothing settles from it, whatever else is available
    st = S.settle_observation({"family": "TOTAL", "period": "FULL", "threshold": 40, "operator": ">=",
                               "game_id": GAME, "direction": "YES"}, book)
    assert st.status == S.REFUSED_GAME_NOT_FINAL and st.settled_yes is None


def test_a_row_whose_result_contradicts_its_scores_is_degraded(records):
    from datetime import datetime
    book = result_book_from_records(with_schedule(records, result="99"), min_hours_after_kickoff=4.0)
    state, reason = book.readiness(GAME, needs_player_stats=True, now=datetime.fromisoformat(LONG_AFTER))
    assert state == DEGRADED_INCONSISTENT and "result 99.0" in reason


# ---------------------------------------------------------------- ESPN attestations
def test_the_espn_scoreboard_is_parsed_into_an_explicit_completion_flag():
    atts = attestations_from_espn_scoreboard(espn_payload())
    att = atts[ESPN_ID]
    assert att.source == ESPN_SCOREBOARD and att.completed is True and att.state == "post"
    assert (att.home_team, att.home_score) == ("PHI", 24.0)
    assert (att.away_team, att.away_score) == ("DAL", 20.0)


def test_an_event_with_no_completion_flag_proves_nothing():
    payload = {"events": [{"id": ESPN_ID, "competitions": [{"status": {"type": {"state": "post"}}}]}]}
    att = attestations_from_espn_scoreboard(payload)[ESPN_ID]
    assert att.completed is None, "absence of a flag is not a False"
    v = verify_final(_game(), in_postgame_tables=False, attestation=att)
    assert not v.proven and not v.contradictions


def test_espn_completion_is_a_proof_on_its_own(records):
    """A game with no postgame tables yet can still be proven complete by ESPN."""
    from datetime import datetime
    rec = dict(records, games_with_player_stats=[], games_with_snaps=[])
    book = result_book_from_records(rec, min_hours_after_kickoff=4.0)
    assert book.readiness(GAME, needs_player_stats=False,
                          now=datetime.fromisoformat(LONG_AFTER))[0] == DEFER_FINAL_UNPROVEN
    book.add_final_attestations(attestations_from_espn_scoreboard(espn_payload()))
    state, reason = book.readiness(GAME, needs_player_stats=False, now=datetime.fromisoformat(LONG_AFTER))
    assert state == READY and ESPN_SCOREBOARD in reason


def test_espn_saying_the_game_is_still_running_fails_closed(records):
    from datetime import datetime
    book = result_book_from_records(records, min_hours_after_kickoff=4.0)
    book.add_final_attestations(attestations_from_espn_scoreboard(
        espn_payload(completed=False, state="in", detail="3rd Quarter")))
    state, reason = book.readiness(GAME, needs_player_stats=True, now=datetime.fromisoformat(LONG_AFTER))
    assert state == DEGRADED_INCONSISTENT, (
        "the postgame tables attest, but a source saying the game is live must block settlement, not be outvoted")
    assert "not complete" in reason and "3rd Quarter" in reason


def test_espn_agreeing_it_is_over_but_disagreeing_about_the_score_fails_closed(records):
    """The most dangerous kind of agreement: both sources say final and the numbers differ."""
    from datetime import datetime
    book = result_book_from_records(records, min_hours_after_kickoff=4.0)
    book.add_final_attestations(attestations_from_espn_scoreboard(espn_payload(home=27)))
    state, reason = book.readiness(GAME, needs_player_stats=True, now=datetime.fromisoformat(LONG_AFTER))
    assert state == DEGRADED_INCONSISTENT and "home score 27" in reason


def test_an_unreachable_espn_never_blocks_a_game_the_tables_attest(records):
    from datetime import datetime
    book = result_book_from_records(records, min_hours_after_kickoff=4.0)      # no attestations added at all
    state, reason = book.readiness(GAME, needs_player_stats=True, now=datetime.fromisoformat(LONG_AFTER))
    assert state == READY and POSTGAME_TABLES in reason


def test_the_espn_fetch_never_raises_and_records_why_it_failed(monkeypatch):
    import urllib.request

    def boom(*a, **k):
        raise urllib.error.URLError("no route to host")
    monkeypatch.setattr(urllib.request, "urlopen", boom)
    atts, meta = fetch_espn_scoreboard(["20250904"])
    assert atts == {} and len(meta) == 1
    assert "URLError" in meta[0]["error"] and meta[0]["url"].endswith("dates=20250904")


def test_the_final_verdict_records_which_source_proved_it():
    v = verify_final(_game(), in_postgame_tables=True,
                     attestation=attestations_from_espn_scoreboard(espn_payload())[ESPN_ID])
    assert v.proven and set(v.proofs) == {POSTGAME_TABLES, ESPN_SCOREBOARD} and not v.contradictions
    d = v.to_dict()
    assert d["final_proven"] is True and sorted(d["final_proofs"]) == sorted(v.proofs)


def test_the_game_evidence_carries_the_proofs_into_the_settlement_row(records):
    from datetime import datetime
    book = result_book_from_records(records, min_hours_after_kickoff=4.0)
    book.readiness(GAME, needs_player_stats=True, now=datetime.fromisoformat(LONG_AFTER))
    st = S.settle_observation({"family": "TOTAL", "period": "FULL", "threshold": 40, "operator": ">=",
                               "game_id": GAME, "direction": "YES"}, book)
    assert st.is_settled
    assert st.evidence["final_proofs"] == [POSTGAME_TABLES], (
        "what proved the game was over travels with the settlement")


def test_the_engine_refuses_an_unproven_final_game_even_without_the_readiness_gate(records):
    """Defence in depth: a caller that skips readiness must still not be able to settle an unproven game."""
    rec = dict(records, games_with_player_stats=[], games_with_snaps=[])
    book = result_book_from_records(rec, min_hours_after_kickoff=4.0)
    st = S.settle_observation({"family": "TOTAL", "period": "FULL", "threshold": 40, "operator": ">=",
                               "game_id": GAME, "direction": "YES"}, book)
    assert st.status == S.REFUSED_GAME_NOT_FINAL and st.settled_yes is None
    assert "nothing independent attests" in st.reason
    book.add_final_attestations(attestations_from_espn_scoreboard(espn_payload()))
    assert S.settle_observation({"family": "TOTAL", "period": "FULL", "threshold": 40, "operator": ">=",
                                 "game_id": GAME, "direction": "YES"}, book).is_settled


def test_the_engine_refuses_when_sources_contradict_even_without_the_readiness_gate(records):
    book = result_book_from_records(records, min_hours_after_kickoff=4.0)
    book.add_final_attestations(attestations_from_espn_scoreboard(espn_payload(home=27)))
    st = S.settle_observation({"family": "TOTAL", "period": "FULL", "threshold": 40, "operator": ">=",
                               "game_id": GAME, "direction": "YES"}, book)
    assert st.status == S.REFUSED_RESULT_INCONSISTENT and st.settled_yes is None


def _game():
    with open(FIXTURE) as f:
        rec = json.load(f)
    rec["game_id"] = GAME
    return result_book_from_records(rec).games[GAME]
