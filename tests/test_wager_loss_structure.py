"""NFL wager loss-structure research: statistics, selection rules, point-in-time joins and redaction.

Deterministic, no network, no market-data checkout: every input is synthetic and built here.
"""
import json
import math
import os
import random
import sys

import numpy as np
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "research"))
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.research import wager_loss_structure as L          # noqa: E402
from nfl_edge.research import wager_selection_rules as WR        # noqa: E402
import nfl_wager_loss_structure as RUN                           # noqa: E402


def pos(ep, game, pnl, cost, *, fees=None, family="spread", price=0.5, week=1, t="2026-09-13T17:00:00Z", phase="PRE_GAME",
        series="KXNFLSPREAD", side="YES", held=True, outcome=None, units=None, ticker="T", qty=None, **kw):
    fees = cost * 0.03 if fees is None else fees
    qty = (cost - fees) / price if qty is None else qty
    return dict(episode=ep, game_key=game, pnl=pnl, cost=cost, fees=fees, family=family, price=price, avg_price=price, week=week, t=t,
                phase=phase, series=series, side=side, held=held, settled=True, outcome=outcome, units=cost / 75 if units is None else units,
                ticker=ticker, qty=qty, team=kw.get("team"), line=kw.get("line"), player=None, clv=kw.get("clv"), cashed_out=False,
                gross=None, minutes_before_kickoff=30.0)


# ------------------------------------------------------------------------------------------------------------- statistics

def test_clustered_interval_is_wider_than_naive_when_positions_share_a_game():
    rng = random.Random(1)
    rows = []
    for g in range(40):
        shock = rng.choice([-1.0, 1.0])
        for i in range(5):                                     # five positions per game, all moving together
            rows.append(pos(f"{g}-{i}", f"G{g}", shock * 10.0, 100.0))
    clustered = L.boot_ratio(rows, "pnl", "cost", n_boot=800)
    naive = L.boot_ratio(rows, "pnl", "cost", cluster=lambda r: r["episode"], n_boot=800)
    assert (clustered["hi95"] - clustered["lo95"]) > 1.8 * (naive["hi95"] - naive["lo95"])
    assert clustered["clusters"] == 40 and naive["clusters"] == 200


def test_a_row_without_a_game_is_its_own_cluster():
    rows = [pos(f"p{i}", None, 1.0, 10.0) for i in range(6)]
    assert L.boot_ratio(rows, "pnl", "cost", n_boot=50)["clusters"] == 6


def test_fair_null_is_zero_when_outcomes_match_prices_and_flags_invalid_normal_approximation():
    # 10 contracts at 0.5 paying exactly half the time -> zero excess
    rows = [dict(game_key=f"G{i}", qty=10.0, price=0.5, outcome=i % 2, fees=0.17) for i in range(40)]
    fn = L.fair_null(rows)
    assert abs(fn["excess_over_fair_per_outlay"]) < 1e-9 and fn["normal_approximation_valid"]
    assert fn["fees_per_outlay"] > 0
    # fifteen longshots, none wins: the z is withheld and the exact tail is reported instead
    shots = [dict(game_key=f"L{i}", qty=100.0, price=0.05, outcome=0, fees=0.3) for i in range(15)]
    fs = L.fair_null(shots)
    assert fs["z_cluster"] is None and not fs["normal_approximation_valid"]
    assert fs["p_wins_at_or_below_observed_if_prices_fair"] == pytest.approx(0.95 ** 15, abs=1e-5)


def test_poisson_binomial_tails_sum_correctly():
    lo, hi = L._poisson_binomial_tails([0.5, 0.5], 1)
    assert lo == pytest.approx(0.75) and hi == pytest.approx(0.75)


def test_bonferroni_and_labels():
    assert L.bonferroni_alpha(10) == pytest.approx(0.005)
    assert L.label(0.001, 10).startswith("clears Bonferroni")
    assert "LEAD" in L.label(0.001, 10)               # a cell chosen after the result is never called proven
    assert L.label(0.2, 10) == "does not clear Bonferroni"
    assert L.label(None, 10) == "INSUFFICIENT"


def test_roi_counts_fees_once():
    # stake 100 (price*contracts + fee), fee 3, net -100 on a loss: ROI -1.0; before fees: -0.97
    b = L.roi_block([pos("a", "G1", -100.0, 100.0, fees=3.0), pos("b", "G2", 50.0, 100.0, fees=3.0)])
    assert b["roi"] == pytest.approx(-0.25)
    assert b["roi_before_fees"] == pytest.approx((-97.0 + 53.0) / 200.0)
    assert b["fees_per_outlay"] == pytest.approx(0.03)


def test_breakeven_includes_the_fee_per_contract():
    row = pos("a", "G1", 10.0, 52.0, fees=2.0, price=0.5, outcome=1)       # 100 contracts, fee 2c each
    out = L.breakeven_block([row], lambda r: "x")["x"]
    assert out["fee_per_contract"] == pytest.approx(0.02)
    assert out["breakeven_hit_rate"] == pytest.approx(0.52)


# ------------------------------------------------------------------------------------------------------------- tickers, results

def test_ticker_parsing_and_rung_semantics():
    sp = L.parse_ticker("KXNFLSPREAD-26SEP20LVLAC-LAC7")
    assert (sp["team"], sp["line"]) == ("LAC", 7.0)
    assert L.parse_ticker("KXNFLTOTAL-26SEP17DETBUF-61")["line"] == 61.0
    assert L.parse_ticker("KXNFLTEAMTOTAL-26SEP20NOBAL-BAL29")["team"] == "BAL"
    assert L.parse_ticker("KXMVECROSSCATEGORY-S2026ABC-XYZ")["team"] is None
    assert L.parse_ticker("KXNFLGAME-26SEP20JACDEN-JAC")["team"] == "JAX"           # franchise code normalised to the schedule's


def games_fixture():
    rows = [{"season": "2026", "week": "3", "gameday": "2026-09-20", "gametime": "13:00", "away_team": "LV", "home_team": "LAC",
             "away_score": "10", "home_score": "17", "spread_line": "3.5", "total_line": "44.5", "away_qb_name": "A", "home_qb_name": "B"},
            {"season": "2026", "week": "4", "gameday": "2026-09-27", "gametime": "13:00", "away_team": "LV", "home_team": "KC",
             "away_score": "", "home_score": "", "spread_line": "7", "total_line": "47", "away_qb_name": "C", "home_qb_name": "D"}]
    return L.load_games(rows, 2026)


def test_outcomes_follow_the_exchange_rule_x_ge_n():
    games = games_fixture()
    g = games[L.canon_game_key("26SEP20LVLAC")]
    ticker = lambda s, tail: L.parse_ticker(f"{s}-26SEP20LVLAC-{tail}")             # noqa: E731
    assert L.outcome_yes("KXNFLSPREAD", ticker("KXNFLSPREAD", "LAC7"), g) == 1       # won by exactly 7 -> "wins by >= 7" pays
    assert L.outcome_yes("KXNFLSPREAD", ticker("KXNFLSPREAD", "LAC8"), g) == 0
    assert L.outcome_yes("KXNFLSPREAD", ticker("KXNFLSPREAD", "LV1"), g) == 0
    assert L.outcome_yes("KXNFLTOTAL", ticker("KXNFLTOTAL", "27"), g) == 1           # 27 total points
    assert L.outcome_yes("KXNFLTOTAL", ticker("KXNFLTOTAL", "28"), g) == 0
    assert L.outcome_yes("KXNFLTEAMTOTAL", ticker("KXNFLTEAMTOTAL", "LAC17"), g) == 1
    assert L.outcome_yes("KXNFLGAME", ticker("KXNFLGAME", "LAC"), g) == 1
    assert L.outcome_yes("KXNFLSPREAD", ticker("KXNFLSPREAD", "LAC7"), games[L.canon_game_key("26SEP27LVKC")]) is None   # not played
    assert L.outcome_yes("KXNFLRECYDS", {"line": 5, "team": None}, g) is None                                        # props not derivable


def test_qb_change_is_relative_to_the_teams_previous_game():
    games = games_fixture()
    flags = L.qb_change_flags(games)
    assert flags[(L.canon_game_key("26SEP20LVLAC"), "LV")] is False                  # first game of the year: no previous starter
    assert flags[(L.canon_game_key("26SEP27LVKC"), "LV")] is True                    # A -> C


# ------------------------------------------------------------------------------------------------------------- margin model

def synthetic_history(n=4000, seed=3):
    rng = np.random.default_rng(seed)
    out = []
    for i in range(n):
        L0 = float(rng.choice([-7, -3.5, -1, 0, 2.5, 6, 10]))
        m = int(round(rng.normal(L0, 13)))
        if rng.random() < 0.10:                        # a spike at the key numbers: pull 10% of games onto 3 or 7 in the right direction
            m = int(np.sign(m or 1) * rng.choice([3, 7]))
        out.append({"season": 2000 + i % 20, "result": float(m), "spread_line": L0})
    return out


def test_key_number_aware_model_beats_plain_normal_out_of_sample_and_is_a_distribution():
    hist = synthetic_history()
    rep, model = L.holdout_margin_model(hist, train_max_season=2013)
    assert rep["gain_loglik_per_game"] > 0 and rep["gain_ci95"][0] > 0
    p = L.margin_pmf(model, 3.0)
    assert p.sum() == pytest.approx(1.0)
    assert p[model["ms"] == 3][0] > L.margin_pmf(model, 3.0, key_adjusted=False)[model["ms"] == 3][0]
    # tail identity: P(home >= k) + P(home <= k-1) = 1
    assert L.p_margin_ge(model, 3.0, 4) + float(p[model["ms"] <= 3].sum()) == pytest.approx(1.0)


# ------------------------------------------------------------------------------------------------------------- selection rules

def test_rules_scale_cost_pnl_and_fees_together_and_never_touch_other_positions():
    f = [pos("a", "G1", -300.0, 600.0, fees=18.0)]                       # 8U
    out = WR.rule_cap_bet(f, 5.0)[0]
    k = 5.0 / 8.0
    assert (out["cost"], out["pnl"], out["fees"]) == pytest.approx((600 * k, -300 * k, 18 * k))
    assert WR.rule_cap_bet([pos("b", "G1", 1.0, 100.0)])[0]["cost"] == 100.0


def test_cap_game_keeps_the_earliest_positions_and_truncates_the_one_that_crosses():
    f = [pos("late", "G1", -10.0, 300.0, t="2026-09-13T18:00:00Z"), pos("early", "G1", -10.0, 300.0, t="2026-09-13T16:00:00Z"),
         pos("other", "G2", -10.0, 300.0)]                                 # 4U each
    out = {x["episode"]: x for x in WR.rule_cap_game(f, 5.0)}
    assert out["early"]["keep"] == 1.0 and out["late"]["keep"] == pytest.approx(0.25) and out["other"]["keep"] == 1.0


def test_one_position_per_game_and_parlays_are_untouched_by_it():
    f = [pos("a", "G1", 1, 10, t="1"), pos("b", "G1", 1, 10, t="2"), pos("p", None, 1, 10, family=WR.PARLAY)]
    out = {x["episode"]: x["keep"] for x in WR.rule_one_position_per_game(f)}
    assert out == {"a": 1.0, "b": 0.0, "p": 1.0}
    assert {x["episode"]: x["keep"] for x in WR.rule_no_parlays(f)}["p"] == 0.0


def test_price_floor_live_and_game_market_rules():
    f = [pos("cheap", "G1", 1, 10, price=0.1), pos("ok", "G2", 1, 10, price=0.5), pos("live", "G3", 1, 10, phase="LIVE"),
         pos("prop", "G4", 1, 10, family="player rushing yards")]
    assert {x["episode"]: x["keep"] for x in WR.rule_min_price(f)} == {"cheap": 0.0, "ok": 1.0, "live": 1.0, "prop": 1.0}
    assert {x["episode"]: x["keep"] for x in WR.rule_no_live_entries(f)}["live"] == 0.0
    assert {x["episode"]: x["keep"] for x in WR.rule_game_markets_only(f)}["prop"] == 0.0


def test_key_number_guard_only_touches_positions_that_carry_a_book_edge():
    f = [dict(pos("s1", "G1", 1, 10), book_edge_key=0.01), dict(pos("s2", "G2", 1, 10), book_edge_key=0.05), pos("t", "G3", 1, 10)]
    assert {x["episode"]: x["keep"] for x in WR.rule_key_number_edge_guard(f)} == {"s1": 0.0, "s2": 1.0, "t": 1.0}


def test_rule_replay_uses_the_chronological_split_and_reports_recovery():
    rows = []
    for i in range(30):                                # weeks 1-4: parlays lose, other bets break even
        rows.append(pos(f"w{i}", f"G{i}", -50.0 if i % 3 == 0 else 0.0, 100.0, week=1 + i % 4,
                        family=WR.PARLAY if i % 3 == 0 else "spread"))
    for i in range(30, 60):
        rows.append(pos(f"w{i}", f"G{i}", -50.0 if i % 3 == 0 else 0.0, 100.0, week=5 + i % 4,
                        family=WR.PARLAY if i % 3 == 0 else "spread"))
    rep = L.rule_replay(rows, {"no_parlays": WR.rule_no_parlays}, split_week=4, n_boot=200)["no_parlays"]
    assert rep["train"]["positions"] == 30 and rep["test"]["positions"] == 30
    assert rep["train"]["roi_points_recovered"] > 0 and rep["test"]["roi_points_recovered"] > 0
    assert rep["train"]["retained_roi"] == pytest.approx(0.0, abs=1e-9)
    assert rep["bonferroni_m"] == 1


# ------------------------------------------------------------------------------------------------------------- shadow join (point in time)

def obs(cut, p=0.6, mid=0.5, state="SUPPORTED"):
    return {"feature_cutoff": cut, "support_state": state, "model_event_probability": p, "mid": mid, "family": "SPREAD"}


def test_shadow_join_never_uses_an_observation_from_after_the_fill_or_a_stale_one():
    r = pos("a", "G1", 1, 10, ticker="T1", side="YES", outcome=1)
    r["t"] = "2026-09-13T17:00:00Z"
    o = {"T1": [obs("2026-09-13T17:00:01+00:00", p=0.9),           # after the fill: forbidden
                obs("2026-09-13T12:00:00+00:00", p=0.7),           # latest legal one
                obs("2026-09-13T09:00:00+00:00", p=0.4),
                obs("2026-09-13T16:30:00+00:00", p=0.99, state="POST_KICKOFF_EXCLUDED")]}
    m = L.shadow_join([r], o)
    assert len(m) == 1 and m[0]["p_side"] == 0.7
    assert L.shadow_join([r], {"T1": [obs("2026-09-13T08:00:00+00:00")]}) == []                    # older than 6h
    no = dict(r, side="NO")
    assert L.shadow_join([no], {"T1": [obs("2026-09-13T12:00:00+00:00", p=0.7, mid=0.6)]})[0]["p_side"] == pytest.approx(0.3)


def test_shadow_block_is_insufficient_below_ten_matched_positions_and_states_provenance():
    out = L.shadow_block([], 20)
    assert out["label"] == "INSUFFICIENT" and "NOT the owner's" in out["provenance"]


# ------------------------------------------------------------------------------------------------------------- ladder, structure

def ladder_row(game, series, line, team, y, mid, week=1):
    return dict(game_key=game, week=week, series=series, line=line, team=team, y=y, mid=mid, yes_ask=mid + 0.005, no_ask=1 - mid + 0.005,
                width=0.01, ticker="T", minutes_before_kickoff=5.0)


def test_ladder_calibration_flags_small_groups_and_reports_both_sides_net_of_fee():
    rows = [ladder_row(f"G{i}", "KXNFLSPREAD", 4, "A", i % 2, 0.5) for i in range(60)]
    out = L.ladder_calibration(rows, lambda r: "g")["g"]
    assert out["n"] == 60 and abs(out["mean_outcome_minus_mid"]) < 1e-9
    assert out["buy_yes_at_ask_roi"] < 0 and out["buy_no_at_ask_roi"] < 0                 # crossing plus fee costs both sides
    assert L.ladder_calibration(rows[:5], lambda r: "g")["g"]["label"] == "INSUFFICIENT"


def test_selection_vs_structure_excludes_the_owners_own_game_and_adds_up():
    lad = [ladder_row(f"G{i}", "KXNFLSPREAD", 4, "A", 0, 0.5) for i in range(1, 40)]            # every control rung loses
    owner = pos("a", "G0", 90.0, 100.0, price=0.5, outcome=1, qty=100.0, fees=0.0, side="YES", held=True)
    owner["series"] = "KXNFLSPREAD"
    out = L.selection_vs_structure([owner], lad, min_control=15)
    assert out["n"] == 1
    assert out["structure_control_excess_per_outlay"]["estimate"] == pytest.approx(-0.505 * 100 / 100)
    s = out["owner_excess_before_fees_per_outlay"]["estimate"] - out["structure_control_excess_per_outlay"]["estimate"]
    assert s == pytest.approx(out["selection_excess_per_outlay"]["estimate"])
    # the owner's own game is never part of its control
    lad_own = lad + [ladder_row("G0", "KXNFLSPREAD", 4, "A", 1, 0.5) for _ in range(40)]
    assert L.selection_vs_structure([owner], lad_own, min_control=15)["structure_control_excess_per_outlay"]["estimate"] == \
        pytest.approx(out["structure_control_excess_per_outlay"]["estimate"])


def test_rung_groups():
    assert L.spread_rung_group(3.0) == "key rung (3 or 7)"
    assert L.spread_rung_group(4.0) == "just past 3 / 7 (4 or 8)"
    assert L.spread_rung_group(10.0) == "secondary key rung (6, 10, 14)"


# ------------------------------------------------------------------------------------------------------------- end to end, redaction

def episode(i, week, ticker, family, direction, price, qty, pnl, game, *, series_family=None):
    fee = round(0.07 * price * (1 - price) * qty, 4)
    return {"position_episode_id": f"ep-{i}", "week": week, "game": game, "game_key": game, "market_ticker": ticker, "family": series_family or family,
            "direction": direction, "opening_phase": "PRE_GAME", "opened_quantity": qty, "entry_cost": price * qty + fee, "fees": fee,
            "total_episode_pnl": pnl, "settlement_state": "SETTLED", "closed_by": "HELD_TO_SETTLEMENT",
            "settlement_pnl": pnl, "realized_trading_pnl": 0.0, "cashout_state": None, "reconciliation": "RECONCILED",
            "pregame_entry_clv_per_contract": -0.005,
            "transactions": [{"executed_at": "2026-09-20T16:30:00Z", "price": price, "fee": fee, "seconds_from_scheduled_kickoff": -1800}]}


def test_end_to_end_report_has_no_ticker_dollar_or_game_code(tmp_path):
    eps = [episode(0, 3, "KXNFLSPREAD-26SEP20LVLAC-LAC7", "spread", "LONG_YES", 0.5, 100, 50.0, "26SEP20LVLAC"),
           episode(1, 3, "KXNFLTOTAL-26SEP20LVLAC-27", "total", "LONG_YES", 0.5, 100, 50.0, "26SEP20LVLAC")]
    doc = {"totals": {"wagers": 2, "settled": 2}, "position_lifecycle": {"episodes": eps}}
    sched = [{"season": "2026", "week": "3", "gameday": "2026-09-20", "gametime": "13:00", "away_team": "LV", "home_team": "LAC",
              "away_score": "10", "home_score": "17", "spread_line": "3.5", "total_line": "44.5", "away_qb_name": "A", "home_qb_name": "B",
              "result": "7"}]
    rep = RUN.build_report(doc, sched, {}, {}, n_boot=100)
    text = json.dumps(rep, default=str)
    for forbidden in ("KX", "26SEP20", "LVLAC", "ep-0"):
        assert forbidden not in text
    assert rep["data"]["model_probability_recorded_with_owner_wagers"] is False
    assert rep["data"]["derived_outcome_vs_settlement"] == {"compared": 2, "agree": 2}
    assert rep["headline"]["positions"] == 2
    out = tmp_path / "r.json"
    # the CLI path refuses to write anything ticker-like: exercise it through the file writer with a doc cache
    doc_path, sched_path = tmp_path / "doc.json", tmp_path / "sched.csv"
    doc_path.write_text(json.dumps(doc))
    import csv
    with open(sched_path, "w", newline="") as h:
        w = csv.DictWriter(h, fieldnames=list(sched[0].keys()))
        w.writeheader()
        w.writerows(sched)
    (tmp_path / "closes").mkdir()
    rc = RUN.main(["--handicap-root", str(tmp_path), "--closes-root", str(tmp_path / "closes"), "--schedule-csv", str(sched_path),
                   "--doc-cache", str(doc_path), "--out-public", str(out), "--n-boot", "100"])
    assert rc == 0 and json.loads(out.read_text())["headline"]["positions"] == 2


def test_the_selection_rules_are_not_wired_into_any_card_or_workflow():
    """Research only: nothing outside this module, the runner and the tests may import the rules."""
    needle = "wager_selection_rules"
    allowed = {os.path.join(ROOT, p) for p in ("nfl_edge/research/wager_selection_rules.py", "nfl_edge/research/wager_loss_structure.py",
                                              "scripts/research/nfl_wager_loss_structure.py", "tests/test_wager_loss_structure.py")}
    for base in ("nfl_edge", "scripts", ".github"):
        for dp, dn, fn in os.walk(os.path.join(ROOT, base)):
            dn[:] = [d for d in dn if d != "__pycache__"]
            for f in fn:
                path = os.path.join(dp, f)
                if path in allowed or not f.endswith((".py", ".yml", ".yaml")):
                    continue
                with open(path, encoding="utf-8", errors="ignore") as h:
                    assert needle not in h.read(), f"{path} imports a research-only rule set"
