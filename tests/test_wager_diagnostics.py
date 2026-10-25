import json

from nfl_edge.handicap import wager_diagnostics as W


def ep(i, *, week=1, series="spread", price=0.5, qty=100.0, won=False, fees=1.5, game="26SEP13AAABBB", phase="PRE_GAME", clv=None,
       secs=-1800.0, closed_by="HELD_TO_SETTLEMENT", direction="LONG_YES"):
    cost = qty * price + fees
    settle = qty * (1 - price) if won else -qty * price
    return {"position_episode_id": f"ep-{i}", "week": week, "game": game, "game_key": game, "market_ticker": f"{series}-{game}-T{i}",
            "family": series, "direction": direction, "opening_phase": phase, "thesis": "PREGAME_THESIS", "opened_quantity": qty,
            "entry_cost": cost, "fees": fees, "total_episode_pnl": settle - fees, "settlement_pnl": settle, "realized_trading_pnl": 0.0,
            "settlement_state": "SETTLED", "cashout_state": "HELD_TO_SETTLEMENT", "closed_by": closed_by, "reconciliation": "RECONCILED",
            "pregame_entry_clv_per_contract": clv,
            "transactions": [{"price": price, "fee": fees, "seconds_from_scheduled_kickoff": secs, "executed_at": "2026-09-13T16:30:00Z"}]}


def doc(eps):
    return {"totals": {"wagers": len(eps), "settled": len(eps), "pl_unestablished": 0}, "position_lifecycle": {"episodes": eps, "anti_chase": {"flags": []}}}


def test_a_cashout_is_one_position_and_is_not_in_the_held_null():
    eps = [ep(1, won=True), ep(2, won=False)]
    co = ep(3, closed_by="CASHOUT")
    co["cashout_state"] = "FULL_CASHOUT"
    d = W.build_diagnostics(doc(eps + [co]), n_boot=200)
    assert d["integrity"]["independent_position_episodes"] == 3
    assert d["price_null"]["positions"] == 2 and d["buys_vs_cashouts"]["full_cashouts"]["positions"] == 1


def test_totals_reconcile_to_the_episode_sum_and_nothing_is_invented():
    eps = [ep(i, won=(i % 2 == 0)) for i in range(10)]
    d = W.build_diagnostics(doc(eps), n_boot=200)
    assert d["totals"]["pnl"] == round(sum(e["total_episode_pnl"] for e in eps), 2)
    assert d["totals"]["established"] == 10 and d["totals"]["unestablished_or_pending"] == 0
    pend = ep(99); pend["settlement_state"] = "PENDING"; pend["total_episode_pnl"] = None
    d2 = W.build_diagnostics(doc(eps + [pend]), n_boot=200)
    assert d2["totals"]["pnl"] == d["totals"]["pnl"] and d2["integrity"]["pending"] == 1      # pending stays out of ROI


def test_fair_priced_coin_flips_sit_near_the_null_and_fees_are_the_loss():
    eps = [ep(i, price=0.5, won=(i % 2 == 0), game=f"G{i}") for i in range(200)]
    d = W.build_diagnostics(doc(eps), n_boot=200)
    assert abs(d["price_null"]["z_gross_vs_fair_prices"]) < 0.5
    assert d["totals"]["roi"] < 0 and d["totals"]["fees_pct_of_stake"] > 0


def test_buckets_and_over_limit_stakes():
    big = ep(1, price=0.5, qty=2000.0)                      # ~$1,000 = 13.3U
    small = ep(2, price=0.2, qty=100.0)
    d = W.build_diagnostics(doc([big, small]), n_boot=200)
    assert d["sizing"]["positions_over_max_units"] == 1
    assert "OVER 5U (above the owner's maximum)" in d["by_stake_size"]
    assert "15-30c" in d["by_entry_price"] and "45-55c" in d["by_entry_price"]
    assert d["by_entry_timing"]["under 1h before"]["positions"] == 2


def test_parlays_have_no_kickoff_and_no_game_cluster():
    p = ep(1, series="series:KXMVECROSSCATEGORY", phase="UNKNOWN", secs=None)
    p["family"] = "series:KXMVECROSSCATEGORY"
    d = W.build_diagnostics(doc([p, ep(2)]), n_boot=200)
    assert d["by_entry_timing"]["parlay / no kickoff"]["positions"] == 1
    assert d["integrity"]["unknown_phase_of_which_parlays"] == 1


def test_capture_fallback_is_labelled_separately_and_refuses_unusable_quotes():
    e1, e2, e3 = ep(1), ep(2), ep(3)
    good = lambda t, k: {"yes_bid": 0.48, "yes_ask": 0.52, "age_s": 120.0}
    fb = W.capture_fallback_clv([e1], good)
    assert fb["ep-1"]["state"] == "CAPTURE_FALLBACK" and fb["ep-1"]["clv_per_contract"] == 0.0
    stale = lambda t, k: {"yes_bid": 0.48, "yes_ask": 0.52, "age_s": 9999.0}
    assert W.capture_fallback_clv([e2], stale)["ep-2"]["state"] == "CAPTURED_QUOTE_NOT_USABLE"
    wide = lambda t, k: {"yes_bid": 0.30, "yes_ask": 0.60, "age_s": 10.0}
    assert W.capture_fallback_clv([e3], wide)["ep-3"]["state"] == "CAPTURED_QUOTE_NOT_USABLE"
    d = W.build_diagnostics(doc([e1]), quote_at=good, n_boot=200)
    assert d["clv"]["canonical"]["n"] == 0 and d["clv"]["capture_fallback"]["n"] == 1
    no = ep(4, direction="LONG_NO")                            # held NO: close held price is 1 - yes mid
    fb = W.capture_fallback_clv([no], lambda t, k: {"yes_bid": 0.58, "yes_ask": 0.62, "age_s": 5.0})
    assert fb["ep-4"]["close_mid_held_side"] == 0.4 and fb["ep-4"]["clv_per_contract"] == -0.1


def test_redacted_form_carries_no_dollars_tickers_games_or_episode_ids():
    eps = [ep(i, game=f"26SEP13T{i}ZZ", won=(i % 3 == 0)) for i in range(12)]
    red = W.redact(W.build_diagnostics(doc(eps), n_boot=200))
    blob = json.dumps(red)
    for forbidden in ("ep-", "26SEP13", "spread-", '"stake":', '"pnl":', "dollars", "median_stake_units", "avg_stake_units"):
        assert forbidden not in blob
    assert "hypotheses" in red and all("evidence" not in h for h in red["hypotheses"])


def test_every_hypothesis_receives_a_verdict_with_evidence():
    d = W.build_diagnostics(doc([ep(i, won=(i % 2 == 0), game=f"G{i}", clv=-0.005) for i in range(30)]), n_boot=200)
    assert [h["id"] for h in d["hypotheses"]] == [f"H{i}" for i in range(1, 11)]
    assert all(h["verdict"] and h["evidence"] for h in d["hypotheses"])
    assert next(h for h in d["hypotheses"] if h["id"] == "H5")["verdict"] == "NOT_MEASURABLE"      # no provenance, no claim
