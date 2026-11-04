"""PR #241 (2026-11-03): a quarterback's OWN rushing / receiving / touchdown prop, classified from the VERIFIED identity and position of the player
in the market (nflverse players table via --raw-root), THROUGH THE REAL RUN NFL ENTRY POINT (scripts/handicap/run_card.py main).

The ticker names a team and a slot ("AAARB1"), never a position. These tests pin that the ticker is not trusted for it:
* a QB under an "RB1" ticker is gated; an RB under a "QB1" ticker is not;
* a QB prop needs his team's quarterback CONFIRMED_STARTER *and* to be that quarterback (a backup's prop is blocked);
* identity or position that cannot be verified (no table, player missing, position blank/unrecognised, sources disagree, wrong team) is blocked,
  even with BOTH quarterbacks confirmed - a confirmation cannot show the player is not the quarterback;
* RB / WR / TE / K / defender props keep their existing classes once verified.
"""
import pytest

from card_fixtures import AS_OF
from test_qb_run_nfl_families import BET, _line, _reasons, _recs, _run, write_identity_tables

pytestmark = pytest.mark.owner_policy

RUSH = "KXNFLRSHYDS-26OCT25AAABBB-AAARB1-45"           # the ticker says RB1 for the AAA player
RUSH_KW = dict(subject="A Rusher", stat="rushing_yards", thr=45.0)
REC_KW = dict(subject="A Receiver", stat="receiving_yards", thr=40.0)
REC = "KXNFLRECYDS-26OCT25AAABBB-AAAWR1-40"
ATD = "KXNFLANYTD-26OCT25AAABBB-AAAWR1"
ATD_KW = dict(subject="A Receiver", stat="touchdowns", thr=1.0)


def QB(team="AAA", gsis=None):
    return (gsis or f"00-QB{team}", "QB", team, f"{team} QB")


def go(tmp_path, ticker, kw, player, recs=None, family="PLAYER_STAT"):
    if isinstance(player, tuple) and player[3] != kw.get("subject") and not player[3].endswith(" QB"):
        player = player[:3] + (kw.get("subject"),)
    if isinstance(player, tuple) and player[3].endswith(" QB"):
        player = player[:3] + (kw.get("subject"),)          # the market's player name is checked against the table's
    return _run(tmp_path, ticker, family, recs, player=player, **kw)


# ---------------------------------------------------------------------------------------------------------------- the quarterback's own prop
def test_a_quarterbacks_rushing_prop_is_blocked_without_his_teams_confirmed_starter_even_under_a_running_back_ticker(tmp_path):
    card = go(tmp_path, RUSH, RUSH_KW, QB(), None)
    assert _line(card)["status"] == "BLOCKED"
    r = _reasons(card)
    assert "QB_UNKNOWN:AAA" in r and "QB_UNKNOWN:BBB" not in r                   # his own team only
    gate = card["lines"][0]["preflight"]["gates"]["game_level_pit_evidence"]
    assert gate["status"] == "FAIL" and "point-in-time evidence not established" in gate["reason"]
    assert "PLAYER_IDENTITY_UNVERIFIED" not in r                                   # he WAS verified; it is the starter that is missing


def test_the_same_prop_is_a_bet_when_his_own_team_confirms_him_as_the_starter_and_the_opposing_quarterback_is_not_needed(tmp_path):
    card = go(tmp_path, RUSH, RUSH_KW, QB(), _recs(teams=("AAA",)))
    line = _line(card)
    assert line["status"] == BET, _reasons(card)
    assert line["stake_dollars"] <= 375
    assert card["lines"][0]["preflight"]["gates"]["game_level_pit_evidence"]["status"] == "PASS"
    # the owner's sizing and review policy is untouched by the new gate: 1U = $75, at most 5U a bet, exposure FLAGS (not caps) at $375 / game and $1,125 / day
    assert line["stake_dollars"] == line["stake_units"] * 75 and line["stake_units"] <= 5
    ef = card["exposure_flags"]
    assert ef["unit_dollars"] == 75.0 and ef["game_flag_dollars"] == 375.0 and ef["daily_flag_dollars"] == 1125.0 and "flags only" in ef["policy_note"]


def test_the_opposing_teams_confirmation_does_not_help_a_quarterbacks_own_prop(tmp_path):
    card = go(tmp_path, RUSH, RUSH_KW, QB(), _recs(teams=("BBB",)))
    assert _line(card)["status"] == "BLOCKED" and "QB_UNKNOWN:AAA" in _reasons(card)


def test_a_backup_quarterbacks_rushing_prop_is_blocked_when_the_confirmed_starter_is_somebody_else(tmp_path):
    card = go(tmp_path, RUSH, RUSH_KW, QB(gsis="00-BACKUP"), _recs())            # confirmations name 00-QBAAA as AAA's starter
    assert _line(card)["status"] == "BLOCKED" and "QB_PLAYER_NOT_CONFIRMED_STARTER:AAA" in _reasons(card)


@pytest.mark.parametrize("ticker,kw", [(REC, REC_KW), (ATD, ATD_KW)])
def test_a_quarterbacks_receiving_or_touchdown_prop_is_qb_gated_on_his_own_team_too(tmp_path, ticker, kw):
    card = go(tmp_path / "n", ticker, kw, QB(), None)
    assert _line(card)["status"] == "BLOCKED" and "QB_UNKNOWN:AAA" in _reasons(card) and "QB_UNKNOWN:BBB" not in _reasons(card)
    card = go(tmp_path / "bk", ticker, kw, QB(gsis="00-BACKUP"), _recs(teams=("AAA",)))
    assert _line(card)["status"] == "BLOCKED" and "QB_PLAYER_NOT_CONFIRMED_STARTER:AAA" in _reasons(card)
    card = go(tmp_path / "ok", ticker, kw, QB(), _recs(teams=("AAA",)))
    assert _line(card)["status"] == BET, _reasons(card)


def test_the_ticker_is_not_trusted_for_the_position_a_running_back_under_a_qb_ticker_is_not_gated(tmp_path):
    ticker = "KXNFLRSHYDS-26OCT25AAABBB-AAAQB1-45"                               # the ticker says QB1; the table says RB
    card = go(tmp_path, ticker, RUSH_KW, ("00-RB1", "RB", "AAA", "A Rusher"), None)
    assert _line(card)["status"] == BET, _reasons(card)
    req = card["lines"][0]["preflight"]["gates"]["game_level_pit_evidence"]
    assert req["status"] in ("NOT_APPLICABLE", "PASS")


# ---------------------------------------------------------------------------------------------------------------- RB / WR / TE / K / defender keep their classes
@pytest.mark.parametrize("pos,ticker,kw", [
    ("RB", RUSH, RUSH_KW),
    ("FB", RUSH, RUSH_KW),
    ("WR", RUSH, RUSH_KW),                       # a receiver's rushing (jet sweep) prop: existing class, rushing volume
    ("TE", RUSH, RUSH_KW),
    ("K", "KXNFLFG-26OCT25AAABBB-AAAK1-2", dict(subject="A Kicker", stat="field_goals", thr=2.0)),
    ("LB", "KXNFLTKL-26OCT25AAABBB-BBBLB1-8", dict(subject="B Backer", stat="tackles", thr=8.0)),
])
def test_verified_non_quarterbacks_keep_their_existing_class_and_need_no_confirmation(tmp_path, pos, ticker, kw):
    team = ticker.split("-")[2][:3]
    card = go(tmp_path, ticker, kw, (f"00-{pos}1", pos, team, kw["subject"]), None)
    assert _line(card)["status"] == BET, _reasons(card)


@pytest.mark.parametrize("pos", ["WR", "TE"])
def test_a_verified_pass_catcher_receiving_prop_still_needs_only_his_own_teams_quarterback(tmp_path, pos):
    card = go(tmp_path / "n", REC, REC_KW, (f"00-{pos}1", pos, "AAA", "A Receiver"), None)
    assert _line(card)["status"] == "BLOCKED" and "QB_UNKNOWN:AAA" in _reasons(card) and "QB_UNKNOWN:BBB" not in _reasons(card)
    card = go(tmp_path / "ok", REC, REC_KW, (f"00-{pos}1", pos, "AAA", "A Receiver"), _recs(teams=("AAA",)))
    assert _line(card)["status"] == BET, _reasons(card)


# ---------------------------------------------------------------------------------------------------------------- unverified identity or position fails CLOSED
def _blocked_unverified(card, reason):
    assert _line(card)["status"] == "BLOCKED"
    assert f"PLAYER_IDENTITY_UNVERIFIED:{reason}" in _reasons(card), _reasons(card)
    assert card["lines"][0]["preflight"]["gates"]["game_level_pit_evidence"]["status"] == "FAIL"


def test_no_player_table_at_all_blocks_even_a_plain_running_back_prop_with_both_quarterbacks_confirmed(tmp_path):
    card = go(tmp_path, RUSH, RUSH_KW, None, _recs())                            # no --raw-root, the market carries no player id
    _blocked_unverified(card, "NO_PLAYER_ID")


def test_a_player_absent_from_the_table_is_blocked(tmp_path):
    from test_qb_run_nfl_families import _tree
    _tree(tmp_path, RUSH, "PLAYER_STAT", player=("00-X", "RB", "AAA", "A Rusher"), **RUSH_KW)
    write_identity_tables(tmp_path, [("00-SOMEONE-ELSE", "QB", "AAA", "Other")])       # the table has a different player
    import json
    from test_postmortem_wiring import _run_entry_point
    from nfl_edge.postmortem import qb_confirmations as QBC
    f = tmp_path / "qb.json"
    f.write_text(json.dumps({"schema": QBC.SCHEMA, "records": _recs()}))
    card, _ = _run_entry_point(tmp_path, "out", "--raw-root", str(tmp_path / "raw"), "--qb-confirmations", str(f))
    _blocked_unverified(card, "PLAYER_NOT_IN_IDENTITY_SOURCE")


@pytest.mark.parametrize("pos,reason", [("", "POSITION_UNKNOWN"), (None, "POSITION_UNKNOWN"), ("QB/RB", "POSITION_UNKNOWN"), ("WIDGET", "POSITION_UNKNOWN")])
def test_a_blank_or_unrecognised_position_is_blocked_even_with_both_quarterbacks_confirmed(tmp_path, pos, reason):
    card = go(tmp_path, RUSH, RUSH_KW, ("00-P1", pos, "AAA", "A Rusher"), _recs())
    _blocked_unverified(card, reason)


def test_a_player_whose_team_is_not_in_the_game_or_contradicts_the_ticker_is_blocked(tmp_path):
    card = go(tmp_path / "x", RUSH, RUSH_KW, ("00-P1", "RB", "CCC", "A Rusher"), _recs())
    _blocked_unverified(card, "TEAM_NOT_IN_GAME")
    card = go(tmp_path / "y", RUSH, RUSH_KW, ("00-P1", "RB", "BBB", "A Rusher"), _recs())          # the ticker's subject is AAA...
    _blocked_unverified(card, "TEAM_MISMATCH_WITH_TICKER")


def test_sources_that_disagree_about_quarterback_block_him(tmp_path):
    from test_qb_run_nfl_families import _tree
    _tree(tmp_path, RUSH, "PLAYER_STAT", player=("00-P1", "RB", "AAA", "A Rusher"), **RUSH_KW)         # players table says RB
    ff = tmp_path / "raw" / "ff_playerids"
    ff.mkdir()
    (ff / "db_playerids.csv").write_text("gsis_id,name,position,team\n00-P1,A Rusher,QB,AAA\n")      # ff_playerids says QB
    import json
    from test_postmortem_wiring import _run_entry_point
    from nfl_edge.postmortem import qb_confirmations as QBC
    f = tmp_path / "qb.json"
    f.write_text(json.dumps({"schema": QBC.SCHEMA, "records": _recs()}))
    card, _ = _run_entry_point(tmp_path, "out", "--raw-root", str(tmp_path / "raw"), "--qb-confirmations", str(f))
    _blocked_unverified(card, "POSITION_CONFLICT")


def test_the_card_records_the_verified_identity_with_provenance_on_the_bet_record(tmp_path):
    import json
    card = go(tmp_path, RUSH, RUSH_KW, ("00-RB1", "RB", "AAA", "A Rusher"), None)
    rid = _line(card)["recommendation_id"]
    rec = json.load(open(tmp_path / "out" / "records" / f"{rid}.json"))
    pi = rec["pit_evidence"]["player_identity"]
    assert pi["verified"] is True and pi["position_group"] == "RB" and pi["team"] == "AAA" and pi["gsis_id"] == "00-RB1" and pi["as_of"] == AS_OF.isoformat()
    assert pi["sources"][0]["source"] == "NFLVERSE_PLAYERS" and len(pi["sources"][0]["sha256"]) == 64
    cov = json.load(open(tmp_path / "out" / "qb_coverage.json"))["player_identity"]
    assert cov["players"] == 3 and cov["errors"] != [] and cov["sources"][0]["rows"] == 3      # the two tables not supplied are listed, not hidden


# ---------------------------------------------------------------------------------------------------------------- empty book, names, workflow, warning
@pytest.mark.parametrize("ticker,kw,pos", [(RUSH, RUSH_KW, "RB"), ("KXNFLFG-26OCT25AAABBB-AAAK1-2", dict(subject="A Kicker", stat="field_goals", thr=2.0), "K"),
                                           ("KXNFLTKL-26OCT25AAABBB-BBBLB1-8", dict(subject="B Backer", stat="tackles", thr=8.0), "LB")])
def test_with_an_EMPTY_identity_book_rushing_kicker_and_defender_props_block_NO_IDENTITY_SOURCE(tmp_path, ticker, kw, pos):
    """DOCUMENTED CONSEQUENCE: a workflow that passes no player tables turns every formerly NOT_GATED player prop into a BLOCK (fail closed). Every workflow that
    runs run_card.py must therefore supply the tables (tests/test_qb_player_identity_workflows.py pins that)."""
    import shutil
    from test_qb_run_nfl_families import _tree
    team = ticker.split("-")[2][:3]
    _tree(tmp_path, ticker, "PLAYER_STAT", player=(f"00-{pos}1", pos, team, kw["subject"]), **kw)
    shutil.rmtree(tmp_path / "raw")                                              # the market carries a player id; there is no table at all
    import json
    from nfl_edge.postmortem import qb_confirmations as QBC
    from test_postmortem_wiring import _run_entry_point
    f = tmp_path / "qb.json"
    f.write_text(json.dumps({"schema": QBC.SCHEMA, "records": _recs()}))
    card, _ = _run_entry_point(tmp_path, "out", "--qb-confirmations", str(f))
    _blocked_unverified(card, "NO_IDENTITY_SOURCE")


def test_a_market_player_name_the_table_does_not_carry_for_that_id_is_blocked(tmp_path):
    from test_qb_run_nfl_families import _tree
    _tree(tmp_path, RUSH, "PLAYER_STAT", player=("00-RB1", "RB", "AAA", "Somebody Else"), **RUSH_KW)       # id matches, the NAME does not
    import json
    from nfl_edge.postmortem import qb_confirmations as QBC
    from test_postmortem_wiring import _run_entry_point
    f = tmp_path / "qb.json"
    f.write_text(json.dumps({"schema": QBC.SCHEMA, "records": _recs()}))
    pk = json.load(open(tmp_path / "a" / "packet.json"))
    for m in pk["games"][0]["markets"]:
        if m["ticker"] == RUSH:
            m["player_name"] = "A Rusher"
    json.dump(pk, open(tmp_path / "a" / "packet.json", "w"))
    card, _ = _run_entry_point(tmp_path, "out", "--raw-root", str(tmp_path / "raw"), "--qb-confirmations", str(f))
    _blocked_unverified(card, "PLAYER_NAME_MISMATCH")


def test_a_confirmation_naming_a_starter_the_tables_do_not_show_as_a_qb_blocks_a_game_level_market(tmp_path):
    import json
    from nfl_edge.postmortem import qb_confirmations as QBC
    from test_postmortem_wiring import _run_entry_point
    from test_qb_run_nfl_families import _tree
    _tree(tmp_path, "KXNFLTEAMTOTAL-26OCT25AAABBB-BBB24", "TEAM_TOTAL", subject="BBB", stat="team_points", thr=24.0)
    write_identity_tables(tmp_path, [("00-QBAAA", "QB", "AAA", "AAA Starter"), ("00-QBBBB", "RB", "BBB", "Not A QB")])         # BBB's "starter" is a running back
    f = tmp_path / "qb.json"
    f.write_text(json.dumps({"schema": QBC.SCHEMA, "records": _recs()}))
    card, _ = _run_entry_point(tmp_path, "out", "--raw-root", str(tmp_path / "raw"), "--qb-confirmations", str(f))
    assert _line(card)["status"] == "BLOCKED" and "QB_NAMED_STARTER_NOT_VERIFIED:BBB:NAMED_STARTER_NOT_A_QUARTERBACK" in _reasons(card)


def test_the_record_binds_the_markets_player_id(tmp_path):
    import json
    card = go(tmp_path, RUSH, RUSH_KW, ("00-RB1", "RB", "AAA", "A Rusher"), None)
    rec = json.load(open(tmp_path / "out" / "records" / f"{_line(card)['recommendation_id']}.json"))
    assert rec["pit_evidence"]["market_player_id"] == "00-RB1" == rec["pit_evidence"]["player_identity"]["gsis_id"]


def test_live_mode_with_an_empty_or_incomplete_book_prints_a_prominent_warning(tmp_path, capsys):
    from test_qb_run_nfl_families import _tree
    _tree(tmp_path, RUSH, "PLAYER_STAT", player=("00-RB1", "RB", "AAA", "A Rusher"), **RUSH_KW)
    from test_postmortem_wiring import _run_entry_point
    _run_entry_point(tmp_path, "empty")                                          # no --raw-root: empty book
    err = capsys.readouterr().err
    assert "WARNING: PLAYER IDENTITY BOOK EMPTY" in err and "::warning::player identity book empty" in err
    _run_entry_point(tmp_path, "partial", "--raw-root", str(tmp_path / "raw"))   # only players.parquet exists: incomplete
    err = capsys.readouterr().err
    assert "WARNING: PLAYER IDENTITY BOOK INCOMPLETE" in err and "weekly_rosters" in err
