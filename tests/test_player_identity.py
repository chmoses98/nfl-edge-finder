"""PR #241 (2026-11-03): VERIFIED player identity and position (nfl_edge/postmortem/player_identity.py). Unknown / conflicting -> UNVERIFIED."""
import json
from datetime import datetime, timedelta, timezone

import pytest

from nfl_edge.postmortem import player_identity as PI

pytestmark = pytest.mark.owner_policy

DEC = datetime(2026, 10, 25, 12, 0, tzinfo=timezone.utc)
TEAMS = ["AAA", "BBB"]


def _book(players=(), rosters=None, ffids=None):
    return PI.book_from_rows(players=list(players), rosters=rosters, ffids=ffids, season=2026)


def _p(gsis="00-1", pos="QB", team="AAA", name="A Player"):
    return {"gsis_id": gsis, "position": pos, "latest_team": team, "display_name": name}


def _verify(book, pid="00-1", week=7, ticker_team=None, teams=TEAMS):
    return PI.verify(book, player_id=pid, game_teams=teams, game_week=week, ticker_team=ticker_team, as_of=DEC)


def test_a_player_in_the_players_table_with_a_recognised_position_and_a_team_in_the_game_is_verified_with_provenance():
    r = _verify(_book([_p()]))
    assert r["verified"] is True and r["is_qb"] is True and r["position_group"] == "QB" and r["team"] == "AAA" and r["gsis_id"] == "00-1"
    assert r["as_of"] == DEC.isoformat() and r["schema"] == PI.SCHEMA
    src = r["sources"][0]
    assert src["source"] == PI.SRC_PLAYERS and len(src["sha256"]) == 64 and src["snapshot_dated"] is False     # undated snapshot: said so


@pytest.mark.parametrize("pid,book,reason", [
    (None, _book([_p()]), PI.R_NO_PLAYER_ID),
    ("", _book([_p()]), PI.R_NO_PLAYER_ID),
    ("00-1", None, PI.R_NO_SOURCE),
    ("00-1", PI.IdentityBook(), PI.R_NO_SOURCE),
    ("00-9", _book([_p()]), PI.R_NOT_IN_SOURCE),
    ("00-1", _book([_p(pos=None)]), PI.R_POSITION_UNKNOWN),
    ("00-1", _book([_p(pos="")]), PI.R_POSITION_UNKNOWN),
    ("00-1", _book([_p(pos="WIDGET")]), PI.R_POSITION_UNKNOWN),
    ("00-1", _book([_p(team=None)]), PI.R_TEAM_UNKNOWN),
    ("00-1", _book([_p(team="CCC")]), PI.R_TEAM_NOT_IN_GAME),
])
def test_anything_missing_is_unverified_with_a_reason(pid, book, reason):
    r = PI.verify(book, player_id=pid, game_teams=TEAMS, game_week=7, as_of=DEC)
    assert r["verified"] is False and r["reason"] == reason and r["position_group"] is None and r["is_qb"] is None


def test_sources_that_disagree_on_quarterback_are_a_conflict_not_a_pick():
    b = _book([_p(pos="RB")], rosters=[{"gsis_id": "00-1", "position": "QB", "team": "AAA", "week": 6}])
    r = _verify(b)
    assert r["verified"] is False and r["reason"] == PI.R_POSITION_CONFLICT
    b = _book([_p(pos="QB")], ffids=[{"gsis_id": "00-1", "position": "WR", "team": "AAA", "name": "x"}])
    assert _verify(b)["reason"] == PI.R_POSITION_CONFLICT


def test_an_unrecognised_position_string_in_one_source_vetoes_even_if_another_says_running_back():
    b = _book([_p(pos="RB")], ffids=[{"gsis_id": "00-1", "position": "QB/RB", "team": "AAA", "name": "x"}])
    assert _verify(b)["verified"] is False and _verify(b)["reason"] == PI.R_POSITION_UNKNOWN


def test_roster_team_is_point_in_time_a_later_week_is_never_used():
    rosters = [{"gsis_id": "00-1", "position": "QB", "team": "CCC", "week": 5}, {"gsis_id": "00-1", "position": "QB", "team": "AAA", "week": 7},
               {"gsis_id": "00-1", "position": "QB", "team": "BBB", "week": 12}]
    r = _verify(_book([_p(team="BBB")], rosters=rosters), week=7)
    assert r["verified"] and r["team"] == "AAA"                       # week 7 row, not week 12 (future) and not week 5 (older)
    only_future = [{"gsis_id": "00-1", "position": "QB", "team": "AAA", "week": 12}]
    r = _verify(_book([_p(team="AAA")], rosters=only_future), week=7)
    assert r["verified"] and all(s["source"] != PI.SRC_ROSTER for s in r["sources"])       # the future row was not consulted at all


def test_players_and_ff_tables_must_agree_on_team_when_there_is_no_roster_row():
    b = _book([_p(team="AAA")], ffids=[{"gsis_id": "00-1", "position": "QB", "team": "BBB", "name": "x"}])
    r = _verify(b)
    assert r["verified"] is False and r["reason"] == PI.R_TEAM_CONFLICT


def test_a_team_the_ticker_contradicts_is_not_verified():
    r = _verify(_book([_p(team="AAA")]), ticker_team="BBB")
    assert r["verified"] is False and r["reason"] == PI.R_TEAM_MISMATCH_TICKER
    assert _verify(_book([_p(team="AAA")]), ticker_team="AAA")["verified"] is True


def test_team_code_aliases_normalise():
    assert PI.norm_team("LAR") == "LA" and PI.norm_team("jac") == "JAX" and PI.norm_team("WSH") == "WAS" and PI.norm_team(" ") is None
    r = PI.verify(_book([_p(team="LAR")]), player_id="00-1", game_teams=["LA", "JAX"], game_week=1, as_of=DEC)
    assert r["verified"] and r["team"] == "LA"


def test_game_teams_unknown_is_unverified():
    assert PI.verify(_book([_p()]), player_id="00-1", game_teams=[None, "BBB"], game_week=1, as_of=DEC)["reason"] == PI.R_NO_TEAMS


# ---------------------------------------------------------------------------------------------------------------- accept (the gate re-judges a block)
def _ok(**kw):
    return PI.verify(_book([_p()]), player_id="00-1", game_teams=TEAMS, game_week=7, as_of=DEC) | kw


def test_accept_takes_a_verified_block_and_normalises_it():
    ok, why, n = PI.accept(_ok(), teams=TEAMS, decision_time=DEC + timedelta(minutes=5), market_player_id="00-1")
    assert ok and why is None and n == {"gsis_id": "00-1", "position_group": "QB", "is_qb": True, "team": "AAA"}


@pytest.mark.parametrize("mutate,reason", [
    ({"verified": False, "reason": "POSITION_UNKNOWN"}, "POSITION_UNKNOWN"),
    ({"verified": "yes"}, PI.R_NO_SOURCE),
    ({"sources": []}, PI.R_NO_PROVENANCE),
    ({"sources": [{"source": "A_BLOG", "sha256": "x"}]}, PI.R_NO_PROVENANCE),
    ({"sources": [{"source": PI.SRC_PLAYERS}]}, PI.R_NO_PROVENANCE),
    ({"position_group": "WIDGET"}, PI.R_MALFORMED),
    ({"is_qb": False}, PI.R_MALFORMED),                       # claims not-QB while the group says QB
    ({"gsis_id": ""}, PI.R_MALFORMED),
    ({"schema": "other"}, PI.R_MALFORMED),
    ({"team": "CCC"}, PI.R_TEAM_NOT_IN_GAME),
    ({"as_of": None}, PI.R_NO_CLOCK),
    ({"as_of": "2026-10-25T12:00:00"}, PI.R_NO_CLOCK),        # naive timestamp: no provable instant
    ({"as_of": (DEC + timedelta(hours=1)).isoformat()}, PI.R_AFTER_DECISION),
    ({"as_of": (DEC - timedelta(hours=25)).isoformat()}, PI.R_STALE),
])
def test_accept_refuses_a_block_that_is_not_what_verify_would_have_produced(mutate, reason):
    ok, why, n = PI.accept(_ok(**mutate), teams=TEAMS, decision_time=DEC + timedelta(minutes=5), market_player_id="00-1")
    assert not ok and why == reason and n is None


def test_accept_of_nothing_is_a_refusal():
    for bad in (None, {}, [], "verified"):
        assert PI.accept(bad, teams=TEAMS, decision_time=DEC)[0] is False


def test_position_groups():
    assert [PI.position_group(x) for x in ("QB", "rb", "FB", "WR", "TE", "K", "PK", "LB", "CB", "FS", "DT", "T")] == \
        ["QB", "RB", "RB", "WR", "TE", "K", "K", "DEF", "DEF", "DEF", "DEF", "OL"]
    assert PI.position_group(None) is None and PI.position_group("  ") is None and PI.position_group("QB/RB") is None


# ---------------------------------------------------------------------------------------------------------------- the file loader
def test_load_book_reads_the_three_repository_tables_with_sha256_and_never_raises(tmp_path):
    import polars as pl
    root = tmp_path / "nflverse"
    (root / "players").mkdir(parents=True)
    (root / "weekly_rosters").mkdir()
    (root / "ff_playerids").mkdir()
    pl.DataFrame({"gsis_id": ["00-1", "00-2"], "display_name": ["A", "B"], "position": ["QB", "RB"], "latest_team": ["AAA", "BBB"]}
                 ).write_parquet(root / "players" / "players.parquet")
    pl.DataFrame({"gsis_id": ["00-1"], "full_name": ["A"], "position": ["QB"], "team": ["AAA"], "week": [7]}
                 ).write_parquet(root / "weekly_rosters" / "roster_weekly_2026.parquet")
    (root / "ff_playerids" / "db_playerids.csv").write_text("gsis_id,name,position,team\n00-1,A,QB,AAA\n")
    b = PI.load_book(str(root), 2026)
    assert b.errors == [] and {s["source"] for s in b.sources} == set(PI.SOURCES) and all(len(s["sha256"]) == 64 for s in b.sources)
    r = _verify(b)
    assert r["verified"] and {s["source"] for s in r["sources"]} == set(PI.SOURCES)
    assert json.loads(json.dumps(r)) == r                                  # the block travels inside a record: it must be JSON-clean
    assert PI.load_book(str(root / "missing"), 2026).errors == ["NO_RAW_ROOT"] and not PI.load_book(None, 2026)
    (root / "players" / "players.parquet").write_bytes(b"not parquet")
    bad = PI.load_book(str(root), 2026)
    assert any(e.startswith("NFLVERSE_PLAYERS:UNREADABLE") for e in bad.errors) and _verify(bad)["verified"] is True       # roster+ff still verify him
    (root / "weekly_rosters" / "roster_weekly_2026.parquet").unlink()
    (root / "ff_playerids" / "db_playerids.csv").unlink()
    assert not PI.load_book(str(root), 2026) and _verify(PI.load_book(str(root), 2026))["reason"] == PI.R_NO_SOURCE


# ---------------------------------------------------------------------------------------------------------------- MFL-style codes, same-week rows, names
@pytest.mark.parametrize("code,canon", [("KCC", "KC"), ("GBP", "GB"), ("SFO", "SF"), ("NEP", "NE"), ("NOS", "NO"), ("TBB", "TB"), ("LVR", "LV"), ("LAR", "LA"), ("JAC", "JAX"), ("WSH", "WAS")])
def test_every_alias_the_repository_knows_normalises(code, canon):
    assert PI.norm_team(code) == canon


def test_kc_and_kcc_do_not_conflict_across_sources():
    b = _book([_p(team="KC")], rosters=[{"gsis_id": "00-1", "position": "QB", "team": "KCC", "week": 6}], ffids=[{"gsis_id": "00-1", "position": "QB", "team": "KC", "name": "x"}])
    r = PI.verify(b, player_id="00-1", game_teams=["KC", "BUF"], game_week=7, as_of=DEC)
    assert r["verified"] and r["team"] == "KC"
    b = _book([_p(team="KCC")], ffids=[{"gsis_id": "00-1", "position": "QB", "team": "KC", "name": "x"}])
    assert PI.verify(b, player_id="00-1", game_teams=["KCC", "BUF"], game_week=7, as_of=DEC)["verified"]


@pytest.mark.parametrize("order", [0, 1])
def test_conflicting_rows_of_the_same_roster_week_block_whatever_the_file_order(order):
    rows = [{"gsis_id": "00-1", "position": "QB", "team": "AAA", "week": 7}, {"gsis_id": "00-1", "position": "RB", "team": "AAA", "week": 7}]
    r = _verify(_book([_p(pos="QB")], rosters=rows[::-1] if order else rows))
    assert r["verified"] is False and r["reason"] == PI.R_POSITION_CONFLICT
    rows = [{"gsis_id": "00-1", "position": "QB", "team": "AAA", "week": 7}, {"gsis_id": "00-1", "position": "QB", "team": "BBB", "week": 7}]
    r = _verify(_book([_p(pos="QB")], rosters=rows[::-1] if order else rows))
    assert r["verified"] is False and r["reason"] == PI.R_TEAM_CONFLICT


def test_a_market_name_that_the_tables_do_not_carry_blocks_and_a_matching_one_verifies():
    b = _book([_p(name="Patrick Mahomes II")])
    kw = dict(player_id="00-1", game_teams=TEAMS, game_week=7, as_of=DEC)
    r = PI.verify(b, player_name="Patrick Mahomes", **kw)
    assert r["verified"] and r["name_checked"] is True
    r = PI.verify(b, player_name="Josh Allen", **kw)
    assert r["verified"] is False and r["reason"] == PI.R_NAME_MISMATCH
    assert PI.verify(b, **kw)["name_checked"] is False                         # no market name supplied: not checked, said so
    assert PI.names_match("T.J. Hockenson", "TJ Hockenson") and PI.names_match("Kenneth Walker III", "Ken Walker") and not PI.names_match("", "x")


def test_accept_binds_the_block_to_the_markets_own_player_id():
    ok = PI.verify(_book([_p()]), player_id="00-1", game_teams=TEAMS, game_week=7, as_of=DEC)
    kw = dict(teams=TEAMS, decision_time=DEC + timedelta(minutes=1))
    assert PI.accept(ok, market_player_id="00-1", **kw)[0] is True
    assert PI.accept(ok, market_player_id="00-2", **kw)[1] == PI.R_ID_MISMATCH
    assert PI.accept(ok, market_player_id=None, **kw)[1] == PI.R_NO_PLAYER_ID
