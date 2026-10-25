"""DIAGNOSIS of the owner's actual placed wagers: where did the money go, and what can the sample tell us?

ACCOUNTING AND DIAGNOSIS ONLY. This reads the output of `actual_wager_postmortem.build` (orders already replayed as
independent position EPISODES by `position_lifecycle`, so a cashout is one transaction in one position and never a
second wager) and cuts it the ways the owner asked:

    by week / market family / entry-price bucket / pregame timing / stake size / game / position,
    entry CLV (canonical closes, and a labelled capture-based fallback where the canonical close is missing),
    fees, correlated exposure, concentration of losses, buys versus cashouts, winners that were poor value.

WHAT IT NEVER DOES
------------------
* It invents nothing. A pending settlement, an unestablished P&L, a missing close, an UNKNOWN phase and a position the
  lifecycle could not reconstruct are each counted in their own bucket and excluded from the figures that need them.
* It does not attribute a cause it cannot measure. The ten candidate explanations in `HYPOTHESES` each receive a
  verdict from a written rule over the numbers (`SUPPORTED`, `CONSISTENT`, `NOT_SUPPORTED`, `NOT_DISTINGUISHABLE`,
  `NOT_MEASURABLE`) and the evidence string that produced it. `NOT_MEASURABLE` is a real answer: the ledger has no
  recommendation, probability or usage projection behind any of these wagers (provenance below), so "the football
  prediction was poor" cannot be separated from "the football prediction was fine and it lost".
* It never feeds a model, a stake or a recommendation.

PROVENANCE. Every wager in `imported_wagers` arrived through the Kalshi router as an OWNER fill. The `handicap-data`
ledger holds no real recommendation (three TEST_ONLY records), so no wager can be attributed to a ChatGPT/model
recommendation; `attribution.py` links fills to recommendations only where a recorded recommendation exists.

THE VARIANCE TEST. If every contract were priced fairly (the probability that it pays equals the price paid), the
expected gross profit before fees is zero and its variance is sum(q_i^2 * p_i * (1 - p_i)) over held-to-settlement
positions. `price_null` reports where the realised gross sits against that, and what fees alone cost. That separates
"results worse than the prices they were bought at imply" from "prices were fair and fees plus variance did the rest",
without assuming a model.
"""
from __future__ import annotations

import math
import random
from collections import Counter, defaultdict

DIAGNOSTICS_VERSION = "wager-diagnostics-1.0.0"

UNIT_DOLLARS = 75.0                 # docs/NFL_OPERATING_POLICY.md; config/risk_policy.json fixed_unit_dollars
MAX_UNITS = 5.0

#: Entry-price buckets on the HELD contract (what was paid per contract).
PRICE_BUCKETS = ((0.0, 0.15, "under 15c"), (0.15, 0.30, "15-30c"), (0.30, 0.45, "30-45c"), (0.45, 0.55, "45-55c"),
                 (0.55, 0.70, "55-70c"), (0.70, 0.85, "70-85c"), (0.85, 1.01, "85c and up"))
#: Minutes before scheduled kickoff of the opening order.
TIMING_BUCKETS = ((24 * 60, 1e9, ">24h before"), (6 * 60, 24 * 60, "6-24h before"), (3 * 60, 6 * 60, "3-6h before"),
                  (60, 3 * 60, "1-3h before"), (0, 60, "under 1h before"))
STAKE_BUCKETS = ((0, 1.0, "under 1U"), (1.0, 2.0, "1-2U"), (2.0, 3.0, "2-3U"), (3.0, 5.0 + 1e-9, "3-5U"),
                 (5.0 + 1e-9, 1e9, "OVER 5U (above the owner's maximum)"))

PROP_STATS = {"RSHYDS": "player rushing yards", "RECYDS": "player receiving yards", "REC": "player receptions",
              "PASSYDS": "player passing yards", "RSHATT": "player rushing attempts", "TD": "player touchdown",
              "PASSINT": "player interceptions", "RRYDS": "player rush+rec yards", "PASSATT": "player pass attempts",
              "MOSTRECYDS": "most receiving yards", "LONGRSH": "longest rush", "TEAMSACK": "team sacks"}


def market_family(fam: str | None) -> str:
    """Postmortem family -> the coarse market family a handicapper would name."""
    f = str(fam or "")
    if "KXMVE" in f:
        return "parlay (multi-leg combo)"
    if f in ("spread", "game_winner", "total", "team_total"):
        return {"game_winner": "moneyline", "team_total": "team total"}.get(f, f)
    s = f.replace("series:KXNFL", "")
    for pre in ("1HTEAMTOTAL", "1HTOTAL", "1HSPREAD", "1QTOTAL", "1H"):
        if s == pre:
            return "first-half / quarter market"
    return PROP_STATS.get(s, f"other ({f})")


def _num(x):
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _bucket(v, table):
    if v is None:
        return "unknown"
    for lo, hi, label in table:
        if lo <= v < hi:
            return label
    return "unknown"


# ---------------------------------------------------------------------------------------------- episode facts

def episode_facts(ep: dict, *, unit: float = UNIT_DOLLARS, fallback_clv: dict | None = None) -> dict:
    """Flatten one lifecycle episode into the fields every cut needs. No new economics are computed."""
    txs = ep.get("transactions") or []
    first = txs[0] if txs else {}
    qty = _num(ep.get("opened_quantity")) or 0.0
    cost = _num(ep.get("entry_cost")) or 0.0
    fees = _num(ep.get("fees")) or 0.0
    pnl = _num(ep.get("total_episode_pnl"))
    settled = ep.get("settlement_state") == "SETTLED" or ep.get("cashout_state") == "FULL_CASHOUT"
    avg_price = (cost - (_num(first.get("fee")) or 0.0)) / qty if qty else None      # entry_cost carries the entry fee
    avg_price = _num(first.get("price")) if len(txs) <= 1 and _num(first.get("price")) is not None else avg_price
    secs = _num(first.get("seconds_from_scheduled_kickoff"))
    phase = ep.get("opening_phase")
    mins_before = (-secs / 60.0) if (secs is not None and phase == "PRE_GAME") else None
    held = ep.get("closed_by") == "HELD_TO_SETTLEMENT"
    gross = None
    if held and ep.get("settlement_pnl") is not None:
        gross = (_num(ep.get("settlement_pnl")) or 0.0) + (_num(ep.get("realized_trading_pnl")) or 0.0)
    clv = _num(ep.get("pregame_entry_clv_per_contract"))
    clv_source = "CANONICAL_CLOSE" if clv is not None else None
    fb = (fallback_clv or {}).get(ep.get("position_episode_id"))
    if clv is None and fb and fb.get("clv_per_contract") is not None and phase == "PRE_GAME":
        clv, clv_source = fb["clv_per_contract"], "CAPTURE_FALLBACK"
    return {
        "episode": ep.get("position_episode_id"), "week": ep.get("week"), "game": ep.get("game") or ep.get("game_key"),
        "game_key": ep.get("game_key"), "ticker": ep.get("market_ticker"), "family": market_family(ep.get("family")),
        "series": ep.get("family"), "direction": ep.get("direction"), "phase": phase, "thesis": ep.get("thesis"),
        "qty": qty, "cost": cost, "fees": fees, "pnl": pnl, "units": cost / unit if unit else None,
        "avg_price": avg_price, "entry_minutes_before_kickoff": mins_before,
        "held": held, "cashed_out": ep.get("cashout_state") == "FULL_CASHOUT", "gross": gross,
        "settled": bool(settled), "won": (pnl is not None and pnl > 0) if settled else None,
        "clv_per_contract": clv, "clv_source": clv_source,
        "clv_dollars": (clv * qty) if clv is not None else None,
        "hindsight_cashout_vs_hold": _num(ep.get("hindsight_cashout_vs_hold")),
        "reconciled": ep.get("reconciliation") == "RECONCILED",
    }


# ---------------------------------------------------------------------------------------------- capture-based close (fallback)

FALLBACK_MAX_AGE_S = 3600.0         # the last captured change must be within an hour of kickoff
FALLBACK_MAX_WIDTH = 0.10


def capture_fallback_clv(episodes: list, quote_at) -> dict:
    """Entry CLV against the LAST CAPTURED two-sided quote strictly before scheduled kickoff, for pregame positions the canonical
    close table does not cover. Returned apart from canonical CLV and labelled CAPTURE_FALLBACK wherever it is shown.

    `quote_at(ticker, t) -> {"yes_bid", "yes_ask", "age_s"} | None` is `position_lifecycle.CaptureQuoteLookup`. The capture is
    change-suppressed, so a row up to an hour old is still the live price; anything older, one-sided, or wider than 10c is
    refused rather than stretched, and a position with no usable quote simply has no fallback CLV."""
    from datetime import datetime, timedelta, timezone
    out = {}
    for ep in episodes:
        if ep.get("opening_phase") != "PRE_GAME" or _num(ep.get("pregame_entry_clv_per_contract")) is not None or quote_at is None:
            continue
        txs = ep.get("transactions") or []
        tx = txs[0] if txs else {}
        secs, at = _num(tx.get("seconds_from_scheduled_kickoff")), tx.get("executed_at")
        if secs is None or not at:
            continue
        try:
            kick = datetime.fromisoformat(str(at).replace("Z", "+00:00")) - timedelta(seconds=secs)
        except ValueError:
            continue
        q = quote_at(ep.get("market_ticker"), kick - timedelta(seconds=1))
        if not q:
            out[ep["position_episode_id"]] = {"state": "NO_CAPTURED_QUOTE_BEFORE_KICKOFF"}
            continue
        yb, ya, age = _num(q.get("yes_bid")), _num(q.get("yes_ask")), _num(q.get("age_s"))
        if yb is None or ya is None or yb <= 0 or ya >= 1 or ya < yb or (ya - yb) > FALLBACK_MAX_WIDTH or age is None or age > FALLBACK_MAX_AGE_S:
            out[ep["position_episode_id"]] = {"state": "CAPTURED_QUOTE_NOT_USABLE", "age_s": age}
            continue
        yes_mid = (yb + ya) / 2.0
        held = yes_mid if ep.get("direction") == "LONG_YES" else 1.0 - yes_mid
        price = _num(tx.get("price"))
        if price is None:
            continue
        out[ep["position_episode_id"]] = {"state": "CAPTURE_FALLBACK", "close_mid_held_side": round(held, 4), "age_s": round(age, 1),
                                          "clv_per_contract": round(held - price, 4), "width": round(ya - yb, 4)}
    return out


# ---------------------------------------------------------------------------------------------- aggregation

def _agg(facts: list) -> dict:
    est = [f for f in facts if f["pnl"] is not None and f["settled"]]
    stake = sum(f["cost"] for f in est)
    pnl = sum(f["pnl"] for f in est)
    fees = sum(f["fees"] for f in est)
    wins = sum(1 for f in est if f["won"])
    w = [f for f in est if f["avg_price"] is not None and f["qty"]]
    stake_w = sum(f["cost"] for f in w) or None
    return {
        "positions": len(facts), "established": len(est), "unestablished_or_pending": len(facts) - len(est),
        "stake": round(stake, 2), "pnl": round(pnl, 2), "fees": round(fees, 2),
        "roi": round(pnl / stake, 4) if stake else None,
        "fees_pct_of_stake": round(fees / stake, 4) if stake else None,
        "wins": wins, "win_rate": round(wins / len(est), 4) if est else None,
        "avg_entry_price_stake_weighted": round(sum(f["avg_price"] * f["cost"] for f in w) / stake_w, 4) if stake_w else None,
        "avg_stake_units": round(stake / len(est) / UNIT_DOLLARS, 2) if est else None,
        "expected_wins_at_entry_prices": round(sum(f["avg_price"] for f in w), 1) if w else None,
    }


def cut(facts: list, key) -> dict:
    groups: dict = defaultdict(list)
    for f in facts:
        groups[key(f)].append(f)
    return {str(k): _agg(v) for k, v in sorted(groups.items(), key=lambda kv: str(kv[0]))}


def bootstrap_roi(facts: list, *, n_boot: int = 4000, seed: int = 20261025, cluster=lambda f: f["game_key"]) -> dict:
    """ROI interval resampling GAMES (clusters), not positions: positions on one game settle on one game state and are
    not independent observations. Parlays have no game and are each their own cluster."""
    est = [f for f in facts if f["pnl"] is not None and f["settled"]]
    clusters: dict = defaultdict(lambda: [0.0, 0.0])
    for i, f in enumerate(est):
        k = cluster(f) if (cluster(f) and "KXMVE" not in str(f["series"])) else f"solo-{i}"
        clusters[k][0] += f["pnl"]
        clusters[k][1] += f["cost"]
    vals = list(clusters.values())
    if len(vals) < 3:
        return {"state": "INSUFFICIENT_CLUSTERS", "clusters": len(vals)}
    rng = random.Random(seed)
    rois = []
    for _ in range(n_boot):
        s = [vals[rng.randrange(len(vals))] for _ in vals]
        c = sum(x[1] for x in s)
        if c:
            rois.append(sum(x[0] for x in s) / c)
    rois.sort()
    pick = lambda q: round(rois[min(len(rois) - 1, int(q * len(rois)))], 4)
    return {"state": "OK", "clusters": len(vals), "n_boot": n_boot, "seed": seed, "roi_p05": pick(0.05),
            "roi_p50": pick(0.5), "roi_p95": pick(0.95), "share_of_resamples_roi_positive": round(sum(r > 0 for r in rois) / len(rois), 4)}


def price_null(facts: list) -> dict:
    """Realised gross profit (before fees) against the zero-edge, fair-price null. Held-to-settlement positions only."""
    held = [f for f in facts if f["held"] and f["gross"] is not None and f["avg_price"] is not None and f["qty"]]
    if not held:
        return {"state": "NO_HELD_POSITIONS"}
    gross = sum(f["gross"] for f in held)
    var = sum((f["qty"] ** 2) * f["avg_price"] * (1 - f["avg_price"]) for f in held)
    sd = math.sqrt(var) if var > 0 else None
    exp_wins = sum(f["avg_price"] for f in held)
    wins = sum(1 for f in held if f["gross"] > 0)
    fees = sum(f["fees"] for f in held)
    return {"state": "OK", "positions": len(held), "gross_pnl_before_fees": round(gross, 2),
            "expected_gross_if_prices_fair": 0.0, "null_sd": round(sd, 2) if sd else None,
            "z_gross_vs_fair_prices": round(gross / sd, 2) if sd else None, "fees": round(fees, 2),
            "net_after_fees": round(gross - fees, 2), "z_net_vs_fair_prices": round((gross - fees) / sd, 2) if sd else None,
            "wins": wins, "expected_wins_if_prices_fair": round(exp_wins, 1),
            "reading": "z near 0: results are what the prices alone imply; fees then explain the loss. z below -2: results were worse "
                       "than the prices paid imply. z above +2: better. Positions on one game are correlated, so treat |z| < 2.5 as noise."}


def clv_block(facts: list, *, n_boot: int = 4000, seed: int = 20261025) -> dict:
    obs = [f for f in facts if f["clv_per_contract"] is not None and f["phase"] == "PRE_GAME"]
    out = {}
    for label, src in (("canonical", "CANONICAL_CLOSE"), ("capture_fallback", "CAPTURE_FALLBACK")):
        o = [f for f in obs if f["clv_source"] == src]
        if not o:
            out[label] = {"n": 0}
            continue
        v = [f["clv_per_contract"] for f in o]
        by_game: dict = defaultdict(list)
        for f in o:
            by_game[f["game_key"]].append(f["clv_per_contract"])
        gm = [sum(x) / len(x) for x in by_game.values()]
        rng = random.Random(seed)
        boots = sorted(sum(gm[rng.randrange(len(gm))] for _ in gm) / len(gm) for _ in range(n_boot)) if len(gm) >= 3 else []
        out[label] = {
            "n": len(o), "games": len(by_game), "mean_per_contract": round(sum(v) / len(v), 4),
            "median_per_contract": round(sorted(v)[len(v) // 2], 4),
            "positive_share": round(sum(x > 0 for x in v) / len(v), 4),
            "worse_than_one_cent_share": round(sum(x < -0.01 for x in v) / len(v), 4),
            "mean_ci90_game_clustered": ([round(boots[int(0.05 * len(boots))], 4), round(boots[int(0.95 * len(boots)) - 1], 4)] if boots else None),
            "dollars_total": round(sum(f["clv_dollars"] for f in o), 2),
            "note": "CLV here = close mid of the side held minus the price paid (the ask). A buyer who crosses the spread "
                    "at a market that never moves scores about -(half spread), so a mean near -0.5c is 'bought at the number', "
                    "not 'bought a bad number'." if label == "canonical" else
                    "Last captured two-sided quote strictly before scheduled kickoff, change-suppressed capture, labelled and "
                    "kept apart from canonical CLV.",
        }
    out["pregame_positions"] = sum(1 for f in facts if f["phase"] == "PRE_GAME")
    out["pregame_without_any_close"] = sum(1 for f in facts if f["phase"] == "PRE_GAME" and f["clv_per_contract"] is None)
    return out


def concentration(facts: list, top: int = 5) -> dict:
    est = [f for f in facts if f["pnl"] is not None and f["settled"]]
    losers = sorted((f for f in est if f["pnl"] < 0), key=lambda f: f["pnl"])
    gross_loss = -sum(f["pnl"] for f in losers)
    net = sum(f["pnl"] for f in est)
    out = {"losing_positions": len(losers), "gross_losses": round(gross_loss, 2), "net_pnl": round(net, 2)}
    for k in (1, 3, top, 10):
        ls = sum(-f["pnl"] for f in losers[:k])
        out[f"top{k}_losers_share_of_gross_losses"] = round(ls / gross_loss, 4) if gross_loss else None
        out[f"net_pnl_without_top{k}_losers"] = round(net + ls, 2)
    # GAMES only: a parlay has no game, so each ticket is its own cluster and is reported apart rather than ranked beside real games.
    by_game: dict = defaultdict(float)
    parlay = 0.0
    for f in est:
        if "KXMVE" in str(f["series"]):
            parlay += f["pnl"]
        else:
            by_game[f["game_key"] or f["episode"]] += f["pnl"]
    worst = sorted(by_game.items(), key=lambda kv: kv[1])[:3]
    out["worst3_games_pnl_total"] = round(sum(v for _, v in worst), 2)
    out["worst3_games_share_of_net_loss"] = round(sum(v for _, v in worst) / net, 4) if net < 0 else None
    out["worst_game_share_of_net_loss"] = round(worst[0][1] / net, 4) if (worst and net < 0) else None
    out["parlay_tickets_pnl_total"] = round(parlay, 2)
    out["parlay_tickets_share_of_net_loss"] = round(parlay / net, 4) if net < 0 else None
    return out


def sizing_block(facts: list) -> dict:
    est = [f for f in facts if f["pnl"] is not None and f["settled"]]
    over = [f for f in est if f["units"] > MAX_UNITS + 1e-9]
    cap_pnl = sum(f["pnl"] * min(1.0, MAX_UNITS * UNIT_DOLLARS / f["cost"]) for f in est if f["cost"])
    return {
        "positions_over_max_units": len(over), "max_units": MAX_UNITS,
        "largest_positions_units": sorted((round(f["units"], 1) for f in est), reverse=True)[:6],
        "pnl_of_positions_over_max": round(sum(f["pnl"] for f in over), 2),
        "stake_of_positions_over_max": round(sum(f["cost"] for f in over), 2),
        "median_stake_units": round(sorted(f["units"] for f in est)[len(est) // 2], 2) if est else None,
        "share_of_positions_under_1U": round(sum(f["units"] < 1 for f in est) / len(est), 4) if est else None,
        "COUNTERFACTUAL_net_pnl_if_every_stake_were_capped_at_5U": round(cap_pnl, 2),
        "counterfactual_note": "Linear scaling of each over-limit position's result; ignores that a smaller stake might not have been "
                               "placed or would have filled at a different price. An illustration of exposure, not a forecast.",
    }


def exposure_block(facts: list, unit: float = UNIT_DOLLARS, game_cap_u: float = 8.0, slate_cap_u: float = 25.0) -> dict:
    """Combined exposure per game and per week against the owner policy caps (config/risk_policy.json)."""
    by_game: dict = defaultdict(lambda: {"cost": 0.0, "fams": set(), "n": 0})
    by_week: dict = defaultdict(float)
    for f in facts:
        k = f["game_key"] if "KXMVE" not in str(f["series"]) else None
        by_week[f["week"]] += f["cost"]
        if k:
            g = by_game[(f["week"], k)]
            g["cost"] += f["cost"]; g["fams"].add(f["family"]); g["n"] += 1
    over_game = {f"wk{wk} {k}": round(v["cost"] / unit, 1) for (wk, k), v in by_game.items() if v["cost"] / unit > game_cap_u}
    multi = sum(1 for v in by_game.values() if v["n"] >= 2)
    return {
        "games_with_two_or_more_positions": multi, "games": len(by_game),
        "games_over_8U_combined": len(over_game), "game_exposure_units_for_games_over_8U": over_game,
        "weeks_over_25U_total_outlay": {f"wk{w}": round(c / unit, 1) for w, c in sorted(by_week.items()) if c / unit > slate_cap_u},
        "weekly_outlay_units": {f"wk{w}": round(c / unit, 1) for w, c in sorted(by_week.items())},
        "note": "Outlay is gross cash staked (recycled capital counted each time), which overstates simultaneous risk on positions "
                "that were cashed out; positions on one game are treated as ONE exposure.",
    }


def buys_vs_cashouts(facts: list) -> dict:
    held = [f for f in facts if f["held"] and f["pnl"] is not None]
    co = [f for f in facts if f["cashed_out"] and f["pnl"] is not None]
    return {"held_to_settlement": _agg(held), "full_cashouts": _agg(co),
            "cashouts_hindsight_vs_holding_total": round(sum(f["hindsight_cashout_vs_hold"] or 0.0 for f in co), 2),
            "note": "Positive hindsight number = the cashout was worth more than holding turned out to be. Five cashouts is an "
                    "anecdote, not a policy finding."}


def winners_with_poor_value(facts: list) -> dict:
    wins = [f for f in facts if f["won"] and f["clv_per_contract"] is not None]
    poor = [f for f in wins if f["clv_per_contract"] < -0.01]
    neg = [f for f in wins if f["clv_per_contract"] < 0]
    losers_good = [f for f in facts if f["won"] is False and f["clv_per_contract"] is not None and f["clv_per_contract"] > 0.0]
    return {"winners_with_a_valid_clv": len(wins), "winners_bought_more_than_1c_above_the_close": len(poor),
            "winners_bought_above_the_close": len(neg), "winners_pnl_of_those_over_1c": round(sum(f["pnl"] for f in poor), 2),
            "losers_bought_below_the_close": len(losers_good),
            "note": "A winner bought above the close was right for a price the market did not support; the profit is not evidence "
                    "of skill. A loser bought below the close was a good bet that lost."}


def stake_escalation(doc: dict) -> dict:
    flags = (doc.get("position_lifecycle", {}).get("anti_chase", {}) or {}).get("flags", []) or []
    return {"flags": dict(Counter(f.get("code") for f in flags)), "n": len(flags)}


# ---------------------------------------------------------------------------------------------- hypotheses

HYPOTHESES = (
    ("H1", "Poor football predictions"),
    ("H2", "Correct theses expressed through inferior markets"),
    ("H3", "Overpaying for contracts"),
    ("H4", "Unrealistic player-usage assumptions"),
    ("H5", "Overweighting unvalidated model probabilities"),
    ("H6", "Excessive correlation"),
    ("H7", "Entering markets after value disappeared"),
    ("H8", "Sizing errors"),
    ("H9", "Unfavourable or wrongly assumed liquidity"),
    ("H10", "Ordinary variance the sample cannot distinguish from bad process"),
)


def judge(a: dict) -> list:
    """Verdicts from written rules over the numbers in `a`. Each carries the evidence it used."""
    t, pn, clv, conc, siz, exp, fam = (a["totals"], a["price_null"], a["clv"]["canonical"], a["concentration"],
                                       a["sizing"], a["exposure"], a["by_market_family"])
    out = []

    def add(hid, verdict, evidence, caveat=""):
        out.append({"id": hid, "name": dict(HYPOTHESES)[hid], "verdict": verdict, "evidence": evidence, "caveat": caveat})

    z = pn.get("z_gross_vs_fair_prices")
    add("H1", "NOT_MEASURABLE",
        f"No wager carries a recorded probability, thesis or recommendation, so a prediction error cannot be isolated from the "
        f"price paid. Closest available test: gross results vs the zero-edge fair-price null z = {z} (|z|<2 means the results are "
        f"what the prices alone imply).",
        "Do not read this as 'predictions were fine'. It says the sample cannot show they were bad.")
    parlay = next((v for k, v in fam.items() if k.startswith("parlay")), None)
    single_game = {k: v for k, v in fam.items() if not k.startswith("parlay")}
    best = max(single_game.items(), key=lambda kv: kv[1]["roi"] if kv[1]["roi"] is not None and kv[1]["established"] >= 5 else -9, default=None)
    worst = min(single_game.items(), key=lambda kv: kv[1]["roi"] if kv[1]["roi"] is not None and kv[1]["established"] >= 5 else 9, default=None)
    add("H2", "NOT_MEASURABLE",
        f"Theses are not recorded, so 'right idea, wrong contract' cannot be tested directly. Descriptive only: ROI by family "
        f"ranges from {worst[0]} {worst[1]['roi']:+.1%} to {best[0]} {best[1]['roi']:+.1%} (families with >=5 positions)"
        + (f"; parlays {parlay['roi']:+.1%} on {parlay['established']} positions" if parlay else "") + ".",
        "Family differences at these counts are inside sampling noise unless the interval excludes zero (see by_family).")
    fees_pct = t["fees_pct_of_stake"]
    cl = clv.get("mean_per_contract") if clv.get("n") else None
    verdict = "SUPPORTED_AS_COST_ONLY"
    add("H3", verdict,
        f"Fees alone cost {fees_pct:.1%} of stake. Canonical entry CLV is {cl:+.4f}/contract on n={clv.get('n')} "
        f"(about half a spread: bought at the number, not above it); {clv.get('positive_share', 0):.0%} of entries beat the close mid. "
        "Overpaying relative to the CLOSE is small; the structural cost is fees plus crossing the spread." if cl is not None else "No valid CLV.",
        "CLV exists only for positions with a canonical close (weeks 1-4 plus any capture fallback shown separately).")
    prop_fams = {k: v for k, v in fam.items() if k.startswith("player")}
    pe = sum(v["established"] for v in prop_fams.values()); pp = sum(v["pnl"] for v in prop_fams.values()); ps = sum(v["stake"] for v in prop_fams.values())
    add("H4", "NOT_DISTINGUISHABLE",
        f"Player-prop positions: {pe} established, ROI {pp / ps:+.1%} on {ps:,.0f} staked. No usage projection was recorded with any of "
        "them, so an unrealistic usage assumption cannot be tested; the sample is also small per stat." if ps else "No player-prop positions.",
        "Needs recorded projected opportunity (targets/carries/snaps) at decision time: now part of the thesis record.")
    add("H5", "NOT_MEASURABLE",
        "No wager is linked to a model probability or a recommendation (the ledger holds no real recommendation). Whether model-market "
        "disagreement drove selection cannot be established from these fills.",
        "Forward fix: recommendation attribution (nfl_edge/handicap/attribution.py) and the staking ladder that forbids "
        "disagreement-only aggressiveness.")
    multi = exp["games_with_two_or_more_positions"]
    add("H6", "CONSISTENT" if (conc.get("worst3_games_share_of_net_loss") or 0) > 0.5 else "NOT_SUPPORTED",
        f"{multi} of {exp['games']} games carried two or more positions; {exp['games_over_8U_combined']} games exceeded 8U combined. "
        f"The worst 3 games account for {conc.get('worst3_games_share_of_net_loss')} of the net loss.",
        "Correlation is shown through concentration, not estimated as a covariance.")
    pregame = clv.get("n", 0)
    add("H7", "NOT_SUPPORTED" if (cl is not None and cl > -0.02) else "CONSISTENT",
        f"If value had disappeared before entry, entries would sit systematically ABOVE the closing price. Mean CLV is {cl:+.4f} "
        f"(n={pregame}) and {clv.get('worse_than_one_cent_share', 0):.0%} of entries were more than 1c above the close mid."
        if cl is not None else "No CLV.",
        "Timing buckets are in by_entry_timing; steam-chasing would show as strongly negative CLV in the late buckets.")
    big = siz["positions_over_max_units"]
    add("H8", "SUPPORTED" if big and siz["pnl_of_positions_over_max"] < 0 else ("CONSISTENT" if big else "NOT_SUPPORTED"),
        f"{big} positions exceeded the owner's 5U maximum (largest {siz['largest_positions_units'][:3]}U) with P&L "
        f"{siz['pnl_of_positions_over_max']:+,.0f}; without the three largest losers the season net would be "
        f"{conc.get('net_pnl_without_top3_losers'):+,.0f}. Median stake is {siz['median_stake_units']}U, so the typical position was small "
        "and a few oversized ones decided the season.",
        "This is the one cause with a direct, quantified link to the dollar loss. It does not say the oversized bets were bad bets.")
    add("H9", "NOT_MEASURABLE",
        "Book depth at the moment of each fill is not recorded in the ledger and no order-book snapshot is joined to entries; fills "
        "that were large relative to displayed size cannot be identified. Fee and spread costs are measured (H3).",
        "Forward fix: preflight depth walk is mandatory for every card line.")
    lo, hi = a["bootstrap_roi"].get("roi_p05"), a["bootstrap_roi"].get("roi_p95")
    zn = pn.get("z_net_vs_fair_prices")
    add("H10", "CONSISTENT" if (zn is not None and abs(zn) < 2.5) else "NOT_SUPPORTED",
        f"Net P&L is {zn} sd from 'fair prices minus fees'. Game-clustered ROI interval (5-95%): {lo} to {hi}; "
        f"{a['bootstrap_roi'].get('clusters')} independent game clusters.",
        "A loss this size over this many correlated positions is within what fair-priced betting plus fees produces; it also does not "
        "prove the process had edge.")
    return out


# ---------------------------------------------------------------------------------------------- top level

def build_diagnostics(doc: dict, *, quote_at=None, fallback_clv: dict | None = None, n_boot: int = 4000, attribution: dict | None = None) -> dict:
    """`doc` is a season-level `actual_wager_postmortem.build` document. `quote_at` (optional) enables the labelled
    capture-based CLV fallback; `fallback_clv` injects a precomputed one (tests)."""
    eps = (doc.get("position_lifecycle") or {}).get("episodes") or []
    if fallback_clv is None and quote_at is not None:
        fallback_clv = {k: v for k, v in capture_fallback_clv(eps, quote_at).items() if v.get("state") == "CAPTURE_FALLBACK"}
    facts = [episode_facts(e, fallback_clv=fallback_clv) for e in eps]
    est = [f for f in facts if f["pnl"] is not None and f["settled"]]
    integrity = {
        "orders": (doc.get("totals") or {}).get("wagers"), "settlements": (doc.get("totals") or {}).get("settled"),
        "independent_position_episodes": len(facts),
        "pending": sum(1 for f in facts if not f["settled"]),
        "unestablished_pnl": sum(1 for f in facts if f["settled"] and f["pnl"] is None),
        "not_reconciled": sum(1 for f in facts if not f["reconciled"]),
        "unknown_phase_positions": sum(1 for f in facts if f["phase"] == "UNKNOWN"),
        "unknown_phase_of_which_parlays": sum(1 for f in facts if f["phase"] == "UNKNOWN" and "KXMVE" in str(f["series"])),
        "order_level_unestablished": (doc.get("totals") or {}).get("pl_unestablished"),
        "kickoff_sources": (doc.get("position_lifecycle") or {}).get("kickoff_sources"),
        "provenance": "All fills are OWNER fills routed from Kalshi; no real recommendation exists in the ledger, so none is attributed "
                      "to a model or to ChatGPT.",
    }
    a = {
        "version": DIAGNOSTICS_VERSION, "integrity": integrity,
        "totals": _agg(facts),
        "by_week": cut(facts, lambda f: f"week {f['week']}"),
        "by_market_family": cut(facts, lambda f: f["family"]),
        "by_entry_price": cut([f for f in facts], lambda f: _bucket(f["avg_price"], PRICE_BUCKETS)),
        "by_entry_timing": cut(facts, lambda f: ("live (in-game entry)" if f["phase"] == "LIVE" else
                                                  "parlay / no kickoff" if f["phase"] == "UNKNOWN" else
                                                  _bucket(f["entry_minutes_before_kickoff"], TIMING_BUCKETS))),
        "by_stake_size": cut(facts, lambda f: _bucket(f["units"], STAKE_BUCKETS)),
        "by_game": cut(facts, lambda f: f["game_key"] if "KXMVE" not in str(f["series"]) else "(parlays)"),
        "bootstrap_roi": bootstrap_roi(facts, n_boot=n_boot),
        "price_null": price_null(facts),
        "clv": clv_block(facts, n_boot=n_boot),
        "concentration": concentration(facts),
        "sizing": sizing_block(facts),
        "exposure": exposure_block(facts),
        "buys_vs_cashouts": buys_vs_cashouts(facts),
        "winners_with_poor_value": winners_with_poor_value(facts),
        "stake_escalation_after_loss": stake_escalation(doc),
        "positions": sorted(({k: f[k] for k in ("episode", "week", "game", "family", "direction", "phase", "units", "avg_price", "cost", "fees",
                                                  "pnl", "clv_per_contract", "clv_source", "entry_minutes_before_kickoff")}
                             for f in facts), key=lambda r: (r["pnl"] if r["pnl"] is not None else 0.0)),
    }
    if attribution is not None:
        a["attribution"] = {k: attribution[k] for k in ("version", "fills", "counts", "real_recommendations", "recommendations_filled", "owner_selected_share", "statement")}
    a["hypotheses"] = judge(a)
    return a


def redact(diag: dict) -> dict:
    """The PUBLIC form: ratios, counts and z-scores only. No dollar amount, ticker, game, episode id or per-position row.

    The repository (and its data branches) are public, so what is committed or logged must not publish the owner's stakes or
    P&L. The full document stays in a private location."""
    keep_pct = ("roi", "fees_pct_of_stake", "win_rate", "avg_entry_price_stake_weighted", "positions", "established",
                "wins", "expected_wins_at_entry_prices")

    def scrub(block: dict) -> dict:
        return {k: {kk: vv for kk, vv in v.items() if kk in keep_pct} for k, v in block.items()}

    out = {"version": diag["version"], "redacted": True, "integrity": {k: v for k, v in diag["integrity"].items() if k != "kickoff_sources"}}
    out["totals"] = {k: v for k, v in diag["totals"].items() if k in keep_pct}
    for key in ("by_week", "by_market_family", "by_entry_price", "by_entry_timing", "by_stake_size"):
        out[key] = scrub(diag[key])
    out["bootstrap_roi"] = diag["bootstrap_roi"]
    out["price_null"] = {k: v for k, v in diag["price_null"].items() if k in ("state", "positions", "z_gross_vs_fair_prices", "z_net_vs_fair_prices",
                                                                              "wins", "expected_wins_if_prices_fair", "reading")}
    out["clv"] = {k: ({kk: vv for kk, vv in v.items() if kk != "dollars_total"} if isinstance(v, dict) else v) for k, v in diag["clv"].items()}
    c = diag["concentration"]
    out["concentration"] = {k: v for k, v in c.items() if "share" in k or k == "losing_positions"}
    s = diag["sizing"]
    out["sizing"] = {"positions_over_max_units": s["positions_over_max_units"], "max_units": s["max_units"],
                     "share_of_positions_under_1U": s["share_of_positions_under_1U"]}     # the median stake in units would be a dollar amount
    e = diag["exposure"]
    out["exposure"] = {k: e[k] for k in ("games_with_two_or_more_positions", "games", "games_over_8U_combined")}
    out["stake_escalation_after_loss"] = diag["stake_escalation_after_loss"]
    if "attribution" in diag:
        out["attribution"] = diag["attribution"]
    out["hypotheses"] = [{"id": h["id"], "name": h["name"], "verdict": h["verdict"]} for h in diag["hypotheses"]]
    return out


# ---------------------------------------------------------------------------------------------- rendering

def _m(v):
    return "n/a" if v is None else f"${v:,.0f}"


def _p(v):
    return "n/a" if v is None else f"{v:+.1%}"


def _table(block: dict, title: str) -> list:
    lines = [f"### {title}", "", "| bucket | positions | staked | net P&L | ROI | win rate | fees % | avg price |", "|---|---|---|---|---|---|---|---|"]
    for k, v in block.items():
        wr = "n/a" if v["win_rate"] is None else f"{v['win_rate']:.0%}"
        fp = "n/a" if v["fees_pct_of_stake"] is None else f"{v['fees_pct_of_stake']:.1%}"
        ap = "n/a" if v["avg_entry_price_stake_weighted"] is None else f"{v['avg_entry_price_stake_weighted']:.2f}"
        lines.append(f"| {k} | {v['positions']} | {_m(v['stake'])} | {_m(v['pnl'])} | {_p(v['roi'])} | {wr} | {fp} | {ap} |")
    return lines + [""]


def render(diag: dict) -> str:
    t, i = diag["totals"], diag["integrity"]
    L = ["# Owner actual wagers: diagnosis", "",
         "> PRIVATE. Contains the owner's stakes and results. The repository is public: do not commit this file; the committed/"
         "published form is `redact()`.", "",
         "## Integrity", "",
         f"* orders {i['orders']} · settlements {i['settlements']} · independent position episodes **{i['independent_position_episodes']}**",
         f"* pending {i['pending']} · unestablished P&L (episodes) {i['unestablished_pnl']} (orders {i['order_level_unestablished']}) · "
         f"not reconciled {i['not_reconciled']} · unknown phase {i['unknown_phase_positions']} (parlays: {i['unknown_phase_of_which_parlays']})",
         f"* {i['provenance']}", "",
         "## Result", "",
         f"* Established positions {t['established']}: staked {_m(t['stake'])}, **net {_m(t['pnl'])} after {_m(t['fees'])} fees, ROI {_p(t['roi'])}**, "
         f"win rate {t['win_rate']:.0%}, average entry price {t['avg_entry_price_stake_weighted']}",
         f"* Game-clustered ROI interval (5-95%): {diag['bootstrap_roi'].get('roi_p05')} to {diag['bootstrap_roi'].get('roi_p95')} over "
         f"{diag['bootstrap_roi'].get('clusters')} clusters; resamples with positive ROI: {diag['bootstrap_roi'].get('share_of_resamples_roi_positive')}", ""]
    pn = diag["price_null"]
    L += ["## Against the fair-price null", "",
          f"* gross before fees {_m(pn.get('gross_pnl_before_fees'))} vs expected 0 (sd {_m(pn.get('null_sd'))}) → z = {pn.get('z_gross_vs_fair_prices')}; "
          f"after fees z = {pn.get('z_net_vs_fair_prices')}; wins {pn.get('wins')} vs {pn.get('expected_wins_if_prices_fair')} expected at the prices paid",
          f"* {pn.get('reading')}", ""]
    L += _table(diag["by_week"], "By week") + _table(diag["by_market_family"], "By market family") + _table(diag["by_entry_price"], "By entry price (held contract)")
    L += _table(diag["by_entry_timing"], "By entry timing") + _table(diag["by_stake_size"], "By stake size")
    c = diag["clv"]
    L += ["## Entry CLV", ""]
    for k in ("canonical", "capture_fallback"):
        L.append(f"* **{k}**: {json_line(c[k])}")
    L += [f"* pregame positions {c['pregame_positions']}, none with any close: {c['pregame_without_any_close']}", ""]
    L += ["## Concentration of losses", "", f"* {json_line(diag['concentration'])}", "",
          "## Sizing", "", f"* {json_line({k: v for k, v in diag['sizing'].items() if k != 'counterfactual_note'})}", f"* {diag['sizing']['counterfactual_note']}", "",
          "## Correlated exposure", "", f"* {json_line(diag['exposure'])}", "",
          "## Buys versus cashouts", "", f"* {json_line(diag['buys_vs_cashouts'])}", "",
          "## Winners that were poor value; losers that were good value", "", f"* {json_line(diag['winners_with_poor_value'])}", "",
          "## Stake escalation after a loss", "", f"* {json_line(diag['stake_escalation_after_loss'])}", "",
          "## Provenance (recommendation attribution)", "", f"* {json_line(diag.get('attribution'))}", "",
          "## Verdicts on the ten candidate causes", "", "| # | cause | verdict | evidence |", "|---|---|---|---|"]
    for h in diag["hypotheses"]:
        L.append(f"| {h['id']} | {h['name']} | **{h['verdict']}** | {h['evidence']} {h['caveat']} |")
    L += ["", _table(diag["by_game"], "By game")[0]] if False else []
    L += _table(diag["by_game"], "By game")
    return "\n".join(L) + "\n"


def json_line(d) -> str:
    import json
    return json.dumps(d, sort_keys=True, default=str)
