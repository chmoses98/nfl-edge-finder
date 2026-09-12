"""Settlement v2: deterministic, idempotent, contradiction-aware payout of v2 questions, or a named refusal."""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.semantics import question_from_market                                          # noqa: E402
from nfl_edge.settlement import settle_v2 as S2                                              # noqa: E402
from nfl_edge.settlement.period_results import PeriodBook, PeriodResult                     # noqa: E402
from nfl_edge.settlement.results import result_book_from_records                             # noqa: E402

FIX = json.load(open(os.path.join(ROOT, "tests", "fixtures", "postgame", "dal_phi_2025_w1.results.json")))
GAME = "2026_02_DEN_KC"


def schedule_csv(home=27, away=20, week="2", season="2026", games=None):
    lines = FIX["schedule_csv"].splitlines()
    h = lines[0].split(",")
    out = [lines[0]]
    for gid, hs, aws, wk in (games or [(GAME, home, away, week)]):
        row = {k: "" for k in h}
        row.update({"game_id": gid, "season": season, "game_type": "REG", "week": wk, "gameday": "2026-09-13", "gametime": "13:00",
                    "away_team": gid.split("_")[2], "home_team": gid.split("_")[3], "away_score": str(aws) if aws is not None else "",
                    "home_score": str(hs) if hs is not None else "", "result": str(hs - aws) if hs is not None else "",
                    "total": str(hs + aws) if hs is not None else "", "overtime": "0"})
        out.append(",".join(row[k] for k in h))
    return "\n".join(out)


def book(home=27, away=20, complete=True, players=None, snaps=None, games=None):
    rec = {"schedule_csv": schedule_csv(home, away, games=games), "players": players or [], "snaps": snaps or [], "game_id": GAME,
           "games_with_player_stats": [GAME] if complete else [], "games_with_snaps": [GAME] if complete else []}
    return result_book_from_records(rec, min_hours_after_kickoff=0)


def pbook(hq=(7, 6, 7, 7), aq=(7, 3, 0, 10), inconsistency=None):
    pb = PeriodBook()
    pr = PeriodResult(GAME, {**{f"hq{i+1}": float(v) for i, v in enumerate(hq)}, **{f"aq{i+1}": float(v) for i, v in enumerate(aq)}},
                      home_reg=float(sum(hq)), away_reg=float(sum(aq)), complete=True, inconsistency=inconsistency, source="test")
    pb.games[GAME] = pr
    return pb


def rec(m, gid=GAME, **extra):
    sem, q = question_from_market(m)
    r = {"question": q.to_dict(), "market_family": sem.family, "period": sem.period or "FULL", "game_id": gid,
         "semantic_confidence": q.semantic_confidence, "subject_id": q.subject, "stat_family": sem.stat}
    r.update(extra)
    return r


def wm(side_suffix, rules):
    return {"ticker": f"KXNFLWINMARGIN-26SEP13DENKC-{side_suffix}", "event_ticker": "KXNFLWINMARGIN-26SEP13DENKC", "series_ticker": "KXNFLWINMARGIN",
            "strike_type": "custom", "custom_strike": {"Winning Margin": side_suffix}, "rules_primary": rules, "title": ""}


def test_margin_bucket_settles_each_side_and_the_tie_leg():
    b = book(27, 20)
    yes = S2.settle_projection(rec(wm("KC7TO14", "If Kansas City has a positive point differential of between 7 and 14 points against Denver in the full game (including overtime)")), b)
    assert yes.status == S2.SETTLED and yes.settled_yes == 1.0
    no = S2.settle_projection(rec(wm("KC1TO6", "If Kansas City has a positive point differential of between 1 and 6 points against Denver in the full game (including overtime)")), b)
    assert no.settled_yes == 0.0
    tie = S2.settle_projection(rec(wm("TIE", "If the game ends in a tie")), b)
    assert tie.settled_yes == 0.0 and tie.kind == S2.KIND_BINARY


def test_period_markets_settle_from_quarter_scores_with_evidence():
    b = book(27, 20); pb = pbook()
    total = S2.settle_projection(rec({"ticker": "KXNFL1HTOTAL-26SEP13DENKC-24", "event_ticker": "KXNFL1HTOTAL-26SEP13DENKC", "series_ticker": "KXNFL1HTOTAL",
                                      "strike_type": "greater", "floor_strike": 23.5, "title": ""}), b, pb)
    assert total.status == S2.SETTLED and total.settled_yes == 0.0 and total.evidence["home_period_points"] == 13.0
    q1 = S2.settle_projection(rec({"ticker": "KXNFL1Q-26SEP13DENKC-TIE", "event_ticker": "KXNFL1Q-26SEP13DENKC", "series_ticker": "KXNFL1Q", "title": ""}), b, pb)
    assert q1.settled_yes == 1.0, "7-7 after one quarter: the tie leg pays"
    hw = S2.settle_projection(rec({"ticker": "KXNFL1Q-26SEP13DENKC-KC", "event_ticker": "KXNFL1Q-26SEP13DENKC", "series_ticker": "KXNFL1Q", "title": ""}), b, pb)
    assert hw.settled_yes == 0.0, "a tied period settles the team legs NO (tie leg exists); never $0.50"


def test_half_full_double_is_the_conjunction_of_its_legs():
    b = book(27, 20); pb = pbook()
    m = {"ticker": "KXNFL1HFT-26SEP13DENKC-KCKC", "event_ticker": "KXNFL1HFT-26SEP13DENKC", "series_ticker": "KXNFL1HFT", "strike_type": "custom",
         "custom_strike": {"1st Half Result": "Kansas City wins 1st Half", "Fulltime Result": "Kansas City wins game"}, "title": ""}
    s = S2.settle_projection(rec(m), b, pb)
    assert s.status == S2.SETTLED and s.settled_yes == 1.0 and len(s.evidence["legs"]) == 2


def test_refusals_name_their_reason_and_never_invent_a_payout():
    m = {"ticker": "KXNFL1HTOTAL-26SEP13DENKC-24", "event_ticker": "KXNFL1HTOTAL-26SEP13DENKC", "series_ticker": "KXNFL1HTOTAL", "strike_type": "greater", "floor_strike": 23.5, "title": ""}
    assert S2.settle_projection(rec(m), book(27, 20), None).status == S2.REFUSED_PERIOD_UNAVAILABLE
    assert S2.settle_projection(rec(m), book(27, 20), pbook(inconsistency="quarters disagree")).status == S2.REFUSED_INCONSISTENT
    assert S2.settle_projection(rec(m), book(None, None), pbook()).status in (S2.REFUSED_NOT_FINAL, S2.REFUSED_INCONSISTENT)
    assert S2.settle_projection(rec(m), book(27, 20, complete=False), pbook()).status == S2.REFUSED_NOT_FINAL
    amb = rec(m); amb["semantic_confidence"] = "AMBIGUOUS"
    assert S2.settle_projection(amb, book(27, 20), pbook()).status == S2.REFUSED_SEMANTICS
    other = rec(m, gid="2026_02_X_Y")
    assert S2.settle_projection(other, book(27, 20), pbook()).status == S2.REFUSED_GAME
    weird = rec(m); weird["market_family"] = "COIN_TOSS"
    assert S2.settle_projection(weird, book(27, 20), pbook()).status == S2.REFUSED_UNSUPPORTED


def test_settlement_is_idempotent_and_deterministic():
    m = {"ticker": "KXNFL1H-26SEP13DENKC-KC", "event_ticker": "KXNFL1H-26SEP13DENKC", "series_ticker": "KXNFL1H", "title": ""}
    a = S2.settle_projection(rec(m), book(27, 20), pbook()).to_dict()
    b = S2.settle_projection(rec(m), book(27, 20), pbook()).to_dict()
    assert a == b and a["settled_yes"] == 1.0


def test_season_wins_refuses_until_every_game_is_final_then_counts():
    games = [(f"2026_{w:02d}_DEN_KC", 24, 20, str(w)) for w in range(1, 18)]
    b = book(games=games)
    m = {"ticker": "KXNFLWINS-26KC-11", "event_ticker": "KXNFLWINS-26KC", "series_ticker": "KXNFLWINS", "strike_type": "greater_or_equal", "floor_strike": 11, "title": ""}
    r = rec(m, gid=None, season=2026, subject_id="KC")
    s = S2.settle_projection(r, b)
    assert s.status == S2.SETTLED and s.settled_yes == 1.0 and s.evidence["wins"] == 17
    partial = book(games=games[:-1] + [("2026_17_DEN_KC", None, None, "17")])
    assert S2.settle_projection(r, partial).status == S2.REFUSED_SEASON_INCOMPLETE


def test_rush_rec_yards_is_the_sum_of_two_proven_columns():
    players = [{"player_id": "p1", "team": "H", "position": "RB", "has_stats_row": True, "stats": {"carries": 12.0, "rushing_yards": 48.0, "targets": 4.0, "receptions": 3.0, "receiving_yards": 30.0}}]
    snaps = [{"player_id": "p1", "team": "H", "offense_snaps": 40.0, "defense_snaps": 0.0, "st_snaps": 0.0}]
    b = book(27, 20, players=players, snaps=snaps)
    r = {"question": {"kind": "THRESHOLD", "op": ">=", "k": 75}, "market_family": "PLAYER_STAT", "period": "FULL", "game_id": GAME,
         "semantic_confidence": "PROVEN", "subject_id": "p1", "stat_family": "rush_rec_yards"}
    s = S2.settle_projection(r, b)
    assert s.status == S2.SETTLED and s.settled_yes == 1.0 and s.evidence["total"] == 78.0
    r["question"]["k"] = 80
    assert S2.settle_projection(r, b).settled_yes == 0.0
