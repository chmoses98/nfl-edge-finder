"""PR #241 (2026-11-03): the QB-dependency table and the game-specific validity rules, THROUGH THE REAL RUN NFL ENTRY POINT
(scripts/handicap/run_card.py main): a declared-fair candidate on each kind of family is priced by the card, goes through the real preflight, and is
a BET only when the quarterback requirement of its family is met.
"""
import json
from datetime import timedelta

import pytest

import test_card as T
from card_fixtures import AS_OF, GAME, _row, build_run, qb_records, schedule_text, thesis
from nfl_edge.postmortem import qb_confirmations as QBC
from test_postmortem_wiring import _run_entry_point

pytestmark = pytest.mark.owner_policy

BET = "BET (preflight approved)"


def write_identity_tables(tmp, players):
    """data/raw/nflverse/players/players.parquet for the run (the repository's own player table): rows (gsis_id, position, latest_team, display_name)."""
    import polars as pl
    d = tmp / "raw" / "players"
    d.mkdir(parents=True, exist_ok=True)
    rows = list(players)
    pl.DataFrame({"gsis_id": [r[0] for r in rows], "display_name": [r[3] for r in rows], "position": [r[1] for r in rows],
                  "latest_team": [r[2] for r in rows]}, schema={"gsis_id": pl.Utf8, "display_name": pl.Utf8, "position": pl.Utf8, "latest_team": pl.Utf8}
                 ).write_parquet(d / "players.parquet")
    return str(tmp / "raw")


#: position by statistic for the cases below; the QB passing stats name the quarterback the confirmation fixtures name (00-QB<team>)
def _default_player(ticker, subject, stat):
    series, parts = ticker.split("-")[0], ticker.split("-")
    team = parts[2][:3] if len(parts) > 2 else "AAA"
    if stat in ("passing_yards", "attempts"):
        return (f"00-QB{team}", "QB", team, subject)
    pos = {"rushing_yards": "RB", "field_goals": "K", "tackles": "LB"}.get(stat, "WR")
    return (f"00-P{series}{team}", pos, team, subject)


def _tree(tmp, ticker, family, *, subject=None, stat=None, thr=None, per="FULL", p=0.45, player="auto"):
    """The one-game capture plus ONE extra row (the contract under test), a declared-fair candidate on it, and the capture/ledger/bankroll files."""
    build_run(tmp / "a")
    shard = tmp / "a" / "analysis" / "games" / f"{GAME}.json"
    d = json.load(open(shard))
    row = _row(ticker, family, subject, thr, p, per=per, stat=stat, meaning=f"YES iff {ticker}")
    d["rows"].append(row)
    json.dump(d, open(shard, "w"))
    pk = json.load(open(tmp / "a" / "packet.json"))
    pid = None
    if family == "PLAYER_STAT" and player is not None:
        pl_row = _default_player(ticker, subject, stat) if player == "auto" else player
        if pl_row is not None:
            pid = pl_row[0]
            write_identity_tables(tmp, [pl_row])
    pk["games"][0]["markets"].append({"ticker": ticker, "player_id": pid, "movement": {"total_move_since_first_capture": 0.0}, "book_depth_yes": 500000.0, "book_depth_no": 500000.0,
                                      "availability_state": "EXPECTED_ACTIVE" if family == "PLAYER_STAT" else None})
    json.dump(pk, open(tmp / "a" / "packet.json", "w"))
    th = thesis(shift=None, candidates=[{"ticker": ticker, "side": "YES", "fair": {"low": 0.64, "high": 0.72, "basis": "declared for the test"},
                                         "usage": {"projected_opportunity": "x", "recent_usage": "x", "role_stability": "x", "teammate_context": "x"},
                                         "winning_scripts": 4, "major_scripts": 4, "single_script_dependent": False,
                                         "script_results": {"COMPETITIVE|NORMAL_SCORING": 0.7, "FAVORITE_CONTROL|NORMAL_SCORING": 0.7, "UNDERDOG_CONTROL|NORMAL_SCORING": 0.7}}])
    th["shift"] = None
    md = T._capture_for(tmp, row, "YES")
    (tmp / "ledger" / "data").mkdir(parents=True)
    from nfl_edge.handicap import bankroll as BK
    (tmp / "bankroll.json").write_text(json.dumps({"bankroll": 5000, "observedAt": (AS_OF - timedelta(minutes=5)).isoformat(), "valueType": BK.VALUE_TYPE}))
    (tmp / "theses.json").write_text(json.dumps([th]))
    (tmp / "schedule.csv").write_text(schedule_text())
    return md


def _run(tmp, ticker, family, recs, name="out", **tree):
    _tree(tmp, ticker, family, **tree)
    extra = ["--raw-root", str(tmp / "raw")] if (tmp / "raw").exists() else []
    if recs is not None:
        f = tmp / "qb.json"
        f.write_text(json.dumps({"schema": QBC.SCHEMA, "records": recs}))
        extra += ["--qb-confirmations", str(f)]
    card, _ = _run_entry_point(tmp, name, *extra)
    return card


def _recs(teams=("AAA", "BBB"), **kw):
    return qb_records(AS_OF, teams=teams, minutes_before_cap=kw.pop("minutes_before_cap", 6), **kw)


def _reasons(card):
    return " | ".join(card["lines"][0]["preflight"]["blocking_reasons"])


def _line(card):
    assert len(card["lines"]) == 1, (card["theses"][0].get("outcome"), card["theses"][0].get("pass_reasons"))
    return card["lines"][0]


#  (id, ticker, family, tree kwargs, classification, teams the card must have confirmed)
CASES = [
    ("team_total", "KXNFLTEAMTOTAL-26OCT25AAABBB-BBB24", "TEAM_TOTAL", dict(subject="BBB", stat="team_points", thr=24.0), "QB_GATED", ("AAA", "BBB")),
    ("both_teams_score_n", "KXNFLBOTH-26OCT25AAABBB-20", "BOTH_TEAMS_SCORE_N", dict(stat="min_team_points", thr=20.0), "QB_GATED", ("AAA", "BBB")),
    ("win_margin", "KXNFLWINMARGIN-26OCT25AAABBB-BBB1", "WIN_MARGIN_BUCKET", dict(subject="BBB", stat="margin"), "QB_GATED", ("AAA", "BBB")),
    ("race_to_n", "KXNFLRACE-26OCT25AAABBB-10-BBB", "RACE_TO_N", dict(stat="race", thr=10.0), "QB_GATED", ("AAA", "BBB")),
    ("total_td", "KXNFLTOTALTD-26OCT25AAABBB-5", "TOTAL_TD", dict(stat="total_touchdowns", thr=5.0), "QB_GATED", ("AAA", "BBB")),
    ("first_td_team", "KXNFLFIRSTTDTEAM-26OCT25AAABBB-BBB", "FIRST_TD_TEAM", dict(subject="BBB", stat="first_td_team"), "QB_GATED", ("AAA", "BBB")),
    ("first_td_time", "KXNFLFIRSTTDTIME-26OCT25AAABBB-10", "FIRST_TD_TIME", dict(stat="first_td_time", thr=10.0), "QB_GATED", ("AAA", "BBB")),
    ("period_winner_1h", "KXNFL1HWINNER-26OCT25AAABBB-BBB", "PERIOD_WINNER", dict(subject="BBB", per="1H"), "QB_GATED", ("AAA", "BBB")),
    ("period_total_2q", "KXNFL2QTOTAL-26OCT25AAABBB-10", "TOTAL", dict(stat="total_points", thr=10.0, per="2Q"), "QB_GATED", ("AAA", "BBB")),
    # NOT here: period both-teams-score (KXNFL1HBTTS) and period touchdowns (KXNFL1QTD). The card cannot price them end to end: the fee schedule
    # has no entry for those series (fee state DEGRADED: net edge unknown), so they never become a line. They are covered at the guard
    # (tests/test_qb_dependency.py) so the day a fee entry exists they are already gated.
    ("half_full", "KXNFL1HFT-26OCT25AAABBB-AAAAAA", "HALF_FULL_RESULT", dict(per="1H"), "QB_GATED", ("AAA", "BBB")),
    ("team_stat_yards", "KXNFLTEAMYDS-26OCT25AAABBB-AAA300", "TEAM_STAT", dict(subject="AAA", stat="team_yards", thr=300.0), "QB_GATED", ("AAA", "BBB")),
    ("team_stat_fg", "KXNFLTEAMFG-26OCT25AAABBB-AAA2", "TEAM_STAT", dict(subject="AAA", stat="team_field_goals", thr=2.0), "QB_GATED", ("AAA", "BBB")),
    ("game_stat_td", "KXNFLGAMETD-26OCT25AAABBB-5", "GAME_STAT", dict(stat="touchdowns_game", thr=5.0), "QB_GATED", ("AAA", "BBB")),
    ("game_event_ot", "KXNFLOT-26OCT25AAABBB-Y", "GAME_EVENT", dict(stat="overtime"), "QB_GATED", ("AAA", "BBB")),
    ("game_event_safety", "KXNFLSAFETY-26OCT25AAABBB-Y", "GAME_EVENT", dict(stat="safety"), "QB_GATED", ("AAA", "BBB")),
    ("combo_parlay", "KXMVENFLSINGLEGAME-26OCT25AAABBB-X", "PARLAY", dict(), "QB_GATED", ("AAA", "BBB")),
    ("qb_passing_yards", "KXNFLPASSYDS-26OCT25AAABBB-AAAQB1-250", "PLAYER_STAT", dict(subject="A QB", stat="passing_yards", thr=250.0), "QB_GATED", ("AAA", "BBB")),
    ("qb_passing_attempts", "KXNFLPASSATT-26OCT25AAABBB-BBBQB1-30", "PLAYER_STAT", dict(subject="B QB", stat="attempts", thr=30.0), "QB_GATED", ("AAA", "BBB")),
    ("receiving_yards", "KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60", "PLAYER_STAT", dict(subject="A Receiver", stat="receiving_yards", thr=60.0), "QB_INDIRECT", ("AAA",)),
    ("receptions", "KXNFLREC-26OCT25AAABBB-BBBWR1-5", "PLAYER_STAT", dict(subject="B Receiver", stat="receptions", thr=5.0), "QB_INDIRECT", ("BBB",)),
    ("anytime_td", "KXNFLANYTD-26OCT25AAABBB-AAAWR1", "PLAYER_STAT", dict(subject="A Receiver", stat="touchdowns", thr=1.0), "QB_INDIRECT", ("AAA",)),
    # NOT here: FIRST_TD_SCORER. card.candidate_record only writes the availability state a RECOMMENDED player-market record needs for PLAYER_STAT, so a
    # first-TD-scorer record is refused by the schema before any QB rule (a separate, pre-existing card limitation; it fails closed). It is
    # covered at the gate (tests/test_qb_dependency.py).
    ("rushing_yards", "KXNFLRSHYDS-26OCT25AAABBB-AAARB1-70", "PLAYER_STAT", dict(subject="A Runner", stat="rushing_yards", thr=70.0), "NOT_GATED", ()),
    ("kicker_fg", "KXNFLFG-26OCT25AAABBB-AAAK1-2", "PLAYER_STAT", dict(subject="A Kicker", stat="field_goals", thr=2.0), "NOT_GATED", ()),
    ("tackles", "KXNFLTKL-26OCT25AAABBB-BBBLB1-8", "PLAYER_STAT", dict(subject="B Backer", stat="tackles", thr=8.0), "NOT_GATED", ()),
    ("longest_fg", "KXNFLLONGFG-26OCT25AAABBB-50", "GAME_STAT", dict(stat="longest_fg", thr=50.0), "NOT_GATED", ()),
]
IDS = [c[0] for c in CASES]


@pytest.mark.parametrize("cid,ticker,family,kw,cls,teams", CASES, ids=IDS)
def test_no_confirmation_source_at_all(tmp_path, cid, ticker, family, kw, cls, teams):
    card = _run(tmp_path, ticker, family, None, **kw)
    if cls == "NOT_GATED":
        assert _line(card)["status"] == BET, _reasons(card)
        assert card["lines"][0]["preflight"]["gates"]["game_level_pit_evidence"]["status"] in ("NOT_APPLICABLE", "PASS")
        return
    line = _line(card)
    assert line["status"] == "BLOCKED", (cid, line["status"])
    r = _reasons(card)
    for t in teams:
        assert f"QB_UNKNOWN:{t}" in r, (cid, r)
    gate = card["lines"][0]["preflight"]["gates"]["game_level_pit_evidence"]
    assert gate["status"] == "FAIL" and "point-in-time evidence not established" in gate["reason"]


@pytest.mark.parametrize("cid,ticker,family,kw,cls,teams", CASES, ids=IDS)
def test_exactly_the_required_quarterbacks_confirmed_makes_a_bet(tmp_path, cid, ticker, family, kw, cls, teams):
    card = _run(tmp_path, ticker, family, _recs(teams=teams or ("AAA", "BBB")), **kw)
    line = _line(card)
    assert line["status"] == BET, (cid, _reasons(card))
    assert line["stake_dollars"] <= 375


GATED_CASES = [c for c in CASES if c[4] == "QB_GATED"]


@pytest.mark.parametrize("cid,ticker,family,kw,cls,teams", GATED_CASES, ids=[c[0] for c in GATED_CASES])
def test_one_of_two_quarterbacks_is_not_enough_for_a_gated_family(tmp_path, cid, ticker, family, kw, cls, teams):
    card = _run(tmp_path, ticker, family, _recs(teams=("AAA",)), **kw)
    assert _line(card)["status"] == "BLOCKED" and "QB_UNKNOWN:BBB" in _reasons(card) and "QB_UNKNOWN:AAA" not in _reasons(card)


INDIRECT_CASES = [c for c in CASES if c[4] == "QB_INDIRECT"]


@pytest.mark.parametrize("cid,ticker,family,kw,cls,teams", INDIRECT_CASES, ids=[c[0] for c in INDIRECT_CASES])
def test_an_indirect_prop_is_blocked_by_its_own_teams_quarterback_only(tmp_path, cid, ticker, family, kw, cls, teams):
    other = "BBB" if teams == ("AAA",) else "AAA"
    card = _run(tmp_path, ticker, family, _recs(teams=(other,)), **kw)
    assert _line(card)["status"] == "BLOCKED" and f"QB_UNKNOWN:{teams[0]}" in _reasons(card) and f"QB_UNKNOWN:{other}" not in _reasons(card)


def test_a_series_the_table_has_never_seen_is_never_a_bet_through_the_card(tmp_path):
    """An unknown series cannot even be priced (no fee-schedule entry: net edge unknown), and if it ever reached the gate it is QB_GATED (tests/test_qb_dependency.py)."""
    card = _run(tmp_path, "KXNFLNOVELPROP-26OCT25AAABBB-AAAWR1-5", "PLAYER_STAT", _recs(), subject="A Player", stat="never_seen", thr=5.0)
    assert card["lines"] == [] and "net edge unknown" in json.dumps(card["theses"][0]["rejected"])
