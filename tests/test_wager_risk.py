"""Risk and concentration of the owner's actual placed wagers (nfl_edge/handicap/wager_risk.py).

Week 2 of 2026 put most of its stake on one game through a YES and a NO on the same spread contract plus a
player prop on that game -- three tickers, one exposure. The properties pinned here are what make that
visible without anyone asking:

  * grouping is by what the money depends on, not by ticker: same game, same market, same ladder (one
    underlying variable), YES+NO on one contract, and same-game correlation, with explicit rules;
  * warning thresholds are named, configurable and fire strictly above them;
  * shares of stake and of net P&L sum to 100%, and the net basis used is stated;
  * no bankroll is guessed, the output is deterministic, and the public log carries counts only.
"""
from __future__ import annotations

import gzip
import json
import os
import random
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.handicap import actual_wager_postmortem as PM  # noqa: E402
from nfl_edge.handicap import wager_risk as WR  # noqa: E402
from nfl_edge.handicap.import_routed_settlements import import_rows as import_settlements  # noqa: E402
from nfl_edge.handicap.import_routed_wagers import import_rows as import_wagers  # noqa: E402

import actual_wager_postmortem as PM_SCRIPT  # noqa: E402


def row(wid, ticker, side="YES", stake=10.0, net=None, recon=None, game=None, contracts=20.0, price=0.5,
        gross=None, close=None, result=None):
    return {"imported_wager_id": wid, "market_ticker": ticker, "side": side, "stake": stake,
            "family": PM.family_of(ticker), "game": game or PM.event_of(ticker), "contracts": contracts,
            "execution_price": price, "gross_return": gross, "net_profit_loss": net, "net_fee_reconciled": recon,
            "close_price": close, "result": result, "settlement_state": "SETTLED" if net is not None else "PENDING",
            "clv_state": "CLV_VALID" if close is not None else "NO_CANONICAL_CLOSE",
            "clv_per_contract": (round(close - price, 6) if close is not None else None)}


def clusters(risk):
    return {w["imported_wager_id"]: w["cluster"] for w in risk["wager_exposure"]}


def codes(risk):
    return [(w["code"], w["subject"]) for w in risk["warnings"]]


# ------------------------------------------------------------------------------------------ parsing & grouping

def test_ticker_parsing_finds_game_ladder_and_player():
    p = WR.parse_ticker("KXNFLSPREAD-26SEP20INDKC-KC5")
    assert p["game_key"] == "26SEP20INDKC" and p["ladder"] == "KXNFLSPREAD-26SEP20INDKC" and p["player"] is None
    p = WR.parse_ticker("KXNFLRSHYDS-26SEP13BALIND-BALDHENRY22-80")
    assert p["ladder"] == "KXNFLRSHYDS-26SEP13BALIND-BALDHENRY22"
    assert p["player"] == "BALDHENRY22" and p["player_team"] == "BAL"
    assert WR.parse_ticker("KXNFLTD-26SEP20INDKC-KCKWALKER9-1")["player_team"] == "KC"
    assert WR.parse_ticker("KXNFLMOSTRECYDS-26SEP13BUFHOU-HOUNCOLLINS12")["player"] == "HOUNCOLLINS12"
    assert WR.parse_ticker("KXNFLTEAMTOTAL-26SEP20NOBAL-BAL29")["ladder"] == "KXNFLTEAMTOTAL-26SEP20NOBAL-BAL"
    assert WR.parse_ticker("KXNFLTEAMTOTAL-26SEP20NOBAL-BAL29")["player"] is None
    assert WR.parse_ticker("KXNFLGAME-26SEP20JACDEN-JAC")["player"] is None
    assert WR.parse_ticker(None)["game_key"] == "UNKNOWN"


def test_same_game_wagers_on_different_tickers_are_one_correlated_cluster():
    rows = [row("a", "KXNFLSPREAD-26SEP20INDKC-KC5"), row("b", "KXNFLGAME-26SEP20INDKC-KC"),
            row("c", "KXNFLTEAMTOTAL-26SEP20INDKC-KC27"), row("d", "KXNFLSPREAD-26SEP20LVLAC-LAC7")]
    risk = WR.assess(rows)
    c = clusters(risk)
    assert c["a"] == c["b"] == c["c"] != c["d"]
    top = risk["groups"]["cluster"][0]
    assert top["wagers"] == 3 and "SAME_GAME_CORRELATED" in top["links"]
    assert {g["key"]: g["wagers"] for g in risk["groups"]["game"]} == {"26SEP20INDKC": 3, "26SEP20LVLAC": 1}


def test_same_market_and_yes_no_pair_are_detected():
    rows = [row("y", "KXNFLSPREAD-26SEP20INDKC-KC5", "YES", stake=540.0, contracts=1000, price=0.54),
            row("n", "KXNFLSPREAD-26SEP20INDKC-KC5", "NO", stake=970.0, contracts=1000, price=0.97),
            row("x", "KXNFLSPREAD-26SEP20LVLAC-LAC7")]
    risk = WR.assess(rows)
    m = {g["key"]: g for g in risk["groups"]["market"]}
    assert m["KXNFLSPREAD-26SEP20INDKC-KC5"]["wagers"] == 2
    links = risk["groups"]["cluster"][0]["links"]
    assert "SAME_MARKET" in links and "OPPOSING_POSITION_PAIR" in links
    (pair,) = risk["opposing_pairs"]
    assert pair["matched_contracts"] == 1000 and pair["combined_price_per_matched_contract"] == 1.51
    assert pair["locked_pl_before_fees"] == -510.0          # 1000 x (1 - 1.51), whatever the game does
    assert ("OPPOSING_POSITION_PAIR", "KXNFLSPREAD-26SEP20INDKC-KC5") in codes(risk)


def test_rungs_of_one_ladder_are_one_underlying_variable():
    rows = [row("a", "KXNFLTOTAL-26SEP17DETBUF-61"), row("b", "KXNFLTOTAL-26SEP17DETBUF-70"),
            row("c", "KXNFLRSHYDS-26SEP13BALIND-BALDHENRY22-80"), row("d", "KXNFLRSHYDS-26SEP13BALIND-BALDHENRY22-100"),
            row("e", "KXNFLRSHYDS-26SEP13BALIND-INDJTAYLOR28-70")]
    risk = WR.assess(rows, thresholds=WR.RiskThresholds(same_game_linked_families=()))
    lad = {g["key"]: g["wagers"] for g in risk["groups"]["ladder"]}
    assert lad == {"KXNFLTOTAL-26SEP17DETBUF": 2, "KXNFLRSHYDS-26SEP13BALIND-BALDHENRY22": 2,
                   "KXNFLRSHYDS-26SEP13BALIND-INDJTAYLOR28": 1}
    c = clusters(risk)
    # With same-game linking switched off, only the ladder joins wagers: Henry's rungs yes, Taylor no.
    assert c["a"] == c["b"] and c["c"] == c["d"] != c["e"]
    assert {g["key"]: g["wagers"] for g in risk["groups"]["player"]} == {"BALDHENRY22": 2, "INDJTAYLOR28": 1}


def test_same_game_linking_is_configurable_and_never_crosses_games():
    rows = [row("a", "KXNFLSPREAD-26SEP20INDKC-KC5"), row("b", "KXNFLTD-26SEP20INDKC-KCKWALKER9-1"),
            row("c", "KXNFLGAME-26SEP20INDKC-KC"), row("d", "KXNFLGAME-26SEP20JACDEN-JAC")]
    narrow = WR.assess(rows, thresholds=WR.RiskThresholds(same_game_linked_families=("spread", "game_winner")))
    c = clusters(narrow)
    assert c["a"] == c["c"] != c["b"] and c["d"] not in (c["a"], c["b"])
    c = clusters(WR.assess(rows))
    assert c["a"] == c["b"] == c["c"] != c["d"]


# ------------------------------------------------------------------------------------------ thresholds & warnings

def _week():
    # 60% on one game (a spread + a game winner), four 10% single wagers on four other games.
    return [row("a", "KXNFLSPREAD-26SEP20INDKC-KC5", stake=30.0, net=-30.0, recon=-29.0),
            row("b", "KXNFLGAME-26SEP20INDKC-KC", stake=30.0, net=-30.0, recon=-29.0),
            row("c", "KXNFLSPREAD-26SEP20LVLAC-LAC7", stake=10.0, net=8.0, recon=9.0),
            row("d", "KXNFLSPREAD-26SEP20MIASF-SF8", stake=10.0, net=-10.0, recon=-10.0),
            row("e", "KXNFLSPREAD-26SEP20GBNYJ-GB4", stake=10.0, net=8.0, recon=9.0),
            row("f", "KXNFLSPREAD-26SEP20MINCHI-CHI4", stake=10.0, net=-10.0, recon=-10.0)]


def test_default_thresholds_fire_on_a_dominant_correlated_game():
    risk = WR.assess(_week())
    got = {c for c, _ in codes(risk)}
    assert got == {"CONCENTRATION_HIGH", "CORRELATED_EXPOSURE_HIGH", "SINGLE_GAME_DOMINATES_WEEK"}
    assert risk["warning_counts"]["OPPOSING_POSITION_PAIR"] == 0
    w = next(w for w in risk["warnings"] if w["code"] == "SINGLE_GAME_DOMINATES_WEEK")
    assert w["value"] == 0.6 and w["threshold"] == round(1 / 3, 6)


def test_a_diversified_week_raises_no_warning():
    rows = [row(str(i), f"KXNFLSPREAD-26SEP20T{i}A{i}B-T{i}A3", stake=10.0, net=1.0) for i in range(8)]
    risk = WR.assess(rows)
    assert risk["warnings"] == [] and all(v == 0 for v in risk["warning_counts"].values())


def test_thresholds_are_configurable_and_strictly_greater_fires():
    loose = WR.RiskThresholds(concentration_high_share=0.6, correlated_exposure_high_share=0.6,
                              single_game_dominates_share=0.6)
    assert WR.assess(_week(), thresholds=loose)["warnings"] == []          # 0.6 is not > 0.6
    tight = WR.RiskThresholds(concentration_high_share=0.05, single_game_dominates_share=0.05)
    risk = WR.assess(_week(), thresholds=tight)
    assert sum(1 for c, _ in codes(risk) if c == "CONCENTRATION_HIGH") == 5   # every cluster > 5%
    assert risk["thresholds"]["concentration_high_share"] == 0.05


def test_postmortem_build_accepts_thresholds():
    doc = PM.build([], [], [], season=2026, risk_thresholds=WR.RiskThresholds(concentration_high_share=0.9))
    assert doc["risk"]["thresholds"]["concentration_high_share"] == 0.9 and doc["risk"]["wagers"] == 0


# ------------------------------------------------------------------------------------------ percentages & basis

def test_stake_and_net_shares_sum_to_one_on_every_partition():
    risk = WR.assess(_week())
    for key in ("cluster", "game", "market", "ladder", "family"):
        gs = risk["groups"][key]
        assert abs(sum(g["stake_share"] for g in gs) - 1.0) < 1e-5, key
        for b in ("net_fee_reconciled", "net_profit_loss"):
            assert abs(sum(g["share_of_net"][b] for g in gs) - 1.0) < 1e-5, (key, b)


def test_the_net_accessor_prefers_canonical_then_reconciled_then_recorded():
    r = {"net_profit_loss": -3.0, "net_fee_reconciled": -2.0}
    assert WR.net_figure(r) == (-2.0, "net_fee_reconciled")
    assert WR.net_figure(dict(r, net_canonical=-1.0)) == (-1.0, "net_canonical")
    assert WR.net_figure({"net_profit_loss": -3.0}) == (-3.0, "net_profit_loss")
    assert WR.net_figure({}) == (None, None)


def test_the_primary_basis_is_the_most_preferred_one_every_wager_has():
    rows = _week()
    assert WR.assess(rows)["net_basis"]["primary"] == "net_fee_reconciled"
    rows[0]["net_fee_reconciled"] = None                   # one wager does not reconcile
    risk = WR.assess(rows)
    assert risk["net_basis"]["primary"] == "net_profit_loss"
    assert risk["totals"]["net"]["net_fee_reconciled"]["complete"] is False
    assert risk["totals"]["net"]["net_profit_loss"]["net"] == -64.0
    rows[1]["net_profit_loss"] = None
    rows[1]["net_fee_reconciled"] = None
    assert WR.assess(rows)["net_basis"]["primary"] is None


def test_decomposition_is_an_identity_with_caveats():
    rows = [row("a", "KXNFLSPREAD-26SEP20INDKC-KC5", stake=10.3, contracts=20, price=0.5, close=0.55, gross=0.0,
                net=-10.3, recon=-10.3, result="LOST")]
    d = WR.assess(rows)["decomposition"][0]
    assert d["entry_quality"]["clv_dollars"] == 1.0 and d["entry_quality"]["sign"] == "POSITIVE"
    assert d["outcome_variance"]["residual_vs_close"] == -11.0      # 0 - 20 x 0.55
    assert d["friction"] == 0.3                                       # the entry fee inside the stake
    assert round(d["entry_quality"]["clv_dollars"] + d["outcome_variance"]["residual_vs_close"] - d["friction"], 6) == d["net"]
    assert any("CANNOT be perfectly separated" in c for c in WR.assess(rows)["decomposition_caveats"])


def test_bankroll_share_is_never_guessed():
    risk = WR.assess(_week())
    assert risk["bankroll"]["state"] == "NOT_AVAILABLE"
    assert all(g["bankroll_share"] is None for g in risk["groups"]["game"])
    assert WR.assess(_week(), bankroll={"starting_bankroll": 1000.0})["bankroll"]["state"] == "NOT_AVAILABLE"
    ok = WR.assess(_week(), bankroll={"starting_bankroll": 1000.0, "source": "test evidence"})
    assert ok["bankroll"]["state"] == "AVAILABLE" and ok["largest"]["game"]["bankroll_share"] == 0.06


def test_output_is_deterministic_whatever_the_input_order():
    rows = _week() + [row("g", "KXNFLSPREAD-26SEP20INDKC-KC5", "NO", stake=5.0, net=1.0, recon=1.0)]
    base = json.dumps(WR.assess(rows), sort_keys=True)
    for seed in range(5):
        shuffled = list(rows)
        random.Random(seed).shuffle(shuffled)
        assert json.dumps(WR.assess(shuffled), sort_keys=True) == base
    stakes = [g["stake"] for g in WR.assess(rows)["groups"]["cluster"]]
    assert stakes == sorted(stakes, reverse=True)


def test_the_render_section_names_basis_warnings_and_caveat():
    doc = PM.build([], [], [], season=2026)
    doc["risk"] = WR.assess(_week())
    text = PM.render(doc)
    assert "## RISK & CONCENTRATION" in text and "net_fee_reconciled" in text
    assert "SINGLE_GAME_DOMINATES_WEEK" in text and "CANNOT be perfectly separated" in text
    assert "NOT_AVAILABLE" in text


# ------------------------------------------------------------------------------------------ the public log

def test_the_script_writes_risk_json_and_logs_no_economics(tmp_path, capsys):
    root = str(tmp_path / "hd")
    games = [{"game_id": "2026_02_IND_KC", "season": 2026, "week": 2, "game_type": "REG", "gameday": "2026-09-20",
              "away_team": "IND", "home_team": "KC", "kickoff_utc": None, "has_result": True}]
    base = {"import_batch_id": "kalshi-router-v1", "entry_method": "IMPORTED_RECEIPT", "game_date": "2026-09-20",
            "market_ticker": "KXNFLSPREAD-26SEP20INDKC-KC5", "executed_at": "2026-09-20T15:00:00Z",
            "fees_are_estimated": False, "fee_state": "ACTUAL_API_FILL", "venue": "kalshi"}
    wagers = [dict(base, source_bet_key="kalshi:v1:y1", side="YES", contracts=100.0, actual_price=0.54,
                   stake=55.77, fees_paid=1.77),
              dict(base, source_bet_key="kalshi:v1:n1", side="NO", contracts=100.0, actual_price=0.97,
                   stake=97.13, fees_paid=0.13)]
    import_wagers(root, wagers, games=games)
    import_settlements(root, [
        {"source_bet_key": "kalshi:v1:y1", "market_ticker": base["market_ticker"], "side": "YES",
         "settlement_status": "SETTLED", "settled_at": "2026-09-21T00:00:00Z", "result": "LOST",
         "gross_return": 0.0, "net_profit_loss": -57.67, "refusals": []},
        {"source_bet_key": "kalshi:v1:n1", "market_ticker": base["market_ticker"], "side": "NO",
         "settlement_status": "SETTLED", "settled_at": "2026-09-21T00:00:00Z", "result": "WON",
         "gross_return": 100.0, "net_profit_loss": 0.97, "refusals": []}])
    closes = tmp_path / "closes" / "2026_02_IND_KC"
    closes.mkdir(parents=True)
    with gzip.open(closes / "close-2.1.0.x.closes_v2.jsonl.gz", "wt") as f:
        f.write(json.dumps({"ticker": base["market_ticker"], "game_id": "2026_02_IND_KC", "close_status": "CLOSE_OK",
                            "close_quality": "EXCELLENT", "close_id": "c1", "mid": 0.535, "no_mid": 0.465}) + "\n")
    rc = PM_SCRIPT.main(["--handicap-root", root, "--closes-root", str(tmp_path / "closes"), "--season", "2026",
                         "--out", str(tmp_path / "out")])
    assert rc == 0
    printed = capsys.readouterr().out
    for sensitive in ("KXNFL", "INDKC", "IND_KC", "55.77", "97.13", "57.67", "0.54", "0.97", "152.9", "%", "$"):
        assert sensitive not in printed, sensitive
    assert "OPPOSING_POSITION_PAIR': 1" in printed and "bankroll NOT_AVAILABLE" in printed
    risk = json.load(open(tmp_path / "out" / "2026" / "week_02.risk.json"))
    assert risk["groups"]["cluster"][0]["key"] == "2026_02_IND_KC#1"
    assert risk["groups"]["game"][0]["label"] == "2026_02_IND_KC"
    assert risk["net_basis"]["primary"] == "net_fee_reconciled"
    assert "RISK & CONCENTRATION" in open(tmp_path / "out" / "2026" / "week_02.ACTUAL_WAGERS.md").read()
