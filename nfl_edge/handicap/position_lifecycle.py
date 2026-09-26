"""POSITION LIFECYCLE: the owner's imported ORDERS read back as POSITION EPISODES. DERIVED, never written back.

WHY THIS EXISTS
---------------
`imported_wagers` holds one record per ORDER (kalshi-bet-router's production unit). An order is a
transaction, not a bet. On Thursday 2026-09-24 (ATL@GB) the owner bought 91.41 YES on a Jordan Love passing
rung and later "cashed out because I didn't think it was going to hit": a second order of 91.41 on the
complementary side. The ledger holds two records -- YES WON +66.41, NO LOST -62.66 -- and every downstream
report counted them as two independent wagers with two CLV observations. Economically it was ONE position:
opened, then closed by trading, with one P&L of +3.75.

Kalshi keeps ONE signed position per market (kalshi-bet-router `accounting/position.py`): buying NO while
long YES reduces the YES position; it does not open a second one. This module replays the orders on that
signed YES axis and names what each one did:

    OPEN           from flat
    ADD            same direction, larger
    REDUCE         same direction, smaller (a PARTIAL cashout)
    CASHOUT_CLOSE  back to flat by trading (a FULL cashout)
    REVERSE        through zero into the opposite direction (closes one episode, opens another)
    SETTLEMENT     the exchange closed whatever remained, at expiry

An EPISODE is flat -> flat on one market. The episode, not the order, is the independent position.

DIRECTION AND THE BUY/SELL VERB
-------------------------------
An `imported_wager.v1` record states the side and the price of the contract whose exposure the order created,
with `stake = contracts x price + entry fee`, and the side is replayed as the exposure the order created. The router
also sends `execution_action`, the verb the exchange REPORTED, which is shown as a label and never used for
direction: the owner's cashouts carry action=sell with a side the public trade tape confirms is their exposure
(docs/POSITION_LIFECYCLE.md). A record without the verb says `action_source = SIDE_AS_EXPOSURE_V1`.

PHASE
-----
The repository's pregame boundary is the SCHEDULED kickoff: the canonical close (`nfl_edge.evaluation.close`)
is the last valid observation strictly before it. A transaction at or after scheduled kickoff is LIVE; before
is PRE_GAME; after a supplied final instant is POST_FINAL; no kickoff is UNKNOWN. A transaction in the first
`NEAR_KICKOFF_S` seconds after scheduled kickoff carries the flag NEAR_SCHEDULED_KICKOFF: the actual first
snap is not a field this repository captures, so "LIVE" there is the standard's verdict, not a claim about the
game clock.

CLV IS FOR ENTRIES
------------------
PRE_GAME_ENTRY_CLV = canonical close price of the held side - the price paid, per contract, over the
pregame OPEN/ADD quantity of the episode. One observation per episode. Exits (REDUCE, CASHOUT_CLOSE, the
closing half of a REVERSE) are never compared with the pregame close. A position opened after kickoff has no
pregame CLV (NOT_APPLICABLE_LIVE_ENTRY). A live exit is compared with the contemporaneous executable quote
(`LIVE_EXIT_VALUE`) when one no older than `LIVE_BENCHMARK_MAX_AGE_S` exists, otherwise
NO_VALID_LIVE_EXIT_BENCHMARK.

CASH IS FOR EVERYTHING
----------------------
Every execution and every fee stays in cash P&L. The episode's total P&L is computed twice -- from the orders'
own settlement figures (gross - stake, summed) and from the lifecycle (realized trading P&L + settlement P&L -
fees) -- and the two must agree to the cent (`reconciliation`), or the episode says so.

Reporting only. Nothing here reads or feeds a model, changes a record, recommends, sizes or blocks a wager.
"""
from __future__ import annotations

import hashlib
import math
from datetime import datetime, timezone

LIFECYCLE_VERSION = "position-lifecycle-1.0.0"

# Transaction roles
OPEN, ADD, REDUCE, CASHOUT_CLOSE, REVERSE, SETTLEMENT = (
    "OPEN", "ADD", "REDUCE", "CASHOUT_CLOSE", "REVERSE", "SETTLEMENT")
# Phases
PRE_GAME, LIVE, POST_FINAL, UNKNOWN = "PRE_GAME", "LIVE", "POST_FINAL", "UNKNOWN"

ENTRY_ROLES = (OPEN, ADD)
EXIT_ROLES = (REDUCE, CASHOUT_CLOSE)

NEAR_KICKOFF_S = 10 * 60
LIVE_BENCHMARK_MAX_AGE_S = 5 * 60
QTY_EPS = 1e-9
MONEY_TOL = 0.005

ACTION_REPORTED = "REPORTED_BY_ROUTER"
ACTION_ASSUMED = "SIDE_AS_EXPOSURE_V1"

CLOSE_USABLE = ("CLOSE_OK",)
USABLE_QUALITY = ("EXCELLENT", "GOOD")

HEADER = (
    "POSITION LIFECYCLE -- ACCOUNTING ONLY. An order is a transaction, not a bet: orders on one market are "
    "replayed on Kalshi's single signed position, and each flat-to-flat EPISODE is one independent position. "
    "A cashout is position management, not a second wager. Nothing here is model evidence or a recommendation."
)


def _num(x):
    if isinstance(x, bool) or x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if math.isfinite(v) else None


def _r(v, n=4):
    return None if v is None else round(v, n)


def _dt(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _iso(d):
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ") if d else None


def game_key(ticker: str | None) -> str:
    """The event code's game (26SEP24ATLGB): shared by every series on one game."""
    parts = (ticker or "").split("-")
    return parts[1] if len(parts) >= 2 else (ticker or "UNKNOWN")


def phase_of(executed_at, kickoff, final_at=None) -> tuple:
    """(phase, seconds_from_scheduled_kickoff, flags)."""
    t, k, f = _dt(executed_at), _dt(kickoff), _dt(final_at)
    if t is None or k is None:
        return UNKNOWN, None, ["NO_KICKOFF"] if k is None else ["NO_EXECUTION_TIME"]
    delta = (t - k).total_seconds()
    if delta < 0:
        return PRE_GAME, delta, []
    if f is not None and t >= f:
        return POST_FINAL, delta, []
    return LIVE, delta, (["NEAR_SCHEDULED_KICKOFF"] if delta < NEAR_KICKOFF_S else [])


def _sign(x):
    return 1 if x > QTY_EPS else (-1 if x < -QTY_EPS else 0)


def classify(before: float, after: float) -> str:
    if _sign(before) == 0:
        return OPEN
    if _sign(after) == 0:
        return CASHOUT_CLOSE
    if _sign(after) != _sign(before):
        return REVERSE
    return ADD if abs(after) > abs(before) else REDUCE


def _action(row) -> tuple:
    a = row.get("execution_action")
    if isinstance(a, str) and a.upper() in ("BUY", "SELL"):
        return a.upper(), ACTION_REPORTED
    return "BUY", ACTION_ASSUMED


def _yes_axis_price(side, price):
    if price is None:
        return None
    return price if side == "YES" else 1.0 - price


def _settlement_value(rows) -> tuple:
    """The YES payout per contract, from the exchange-stated per-order returns (gross / contracts on the side
    held). Rows that disagree are refused rather than averaged."""
    values = []
    for r in rows:
        g, c = _num(r.get("gross_return")), _num(r.get("contracts"))
        if r.get("settlement_state") != "SETTLED" or g is None or not c:
            continue
        per = g / c
        values.append(per if r.get("side") == "YES" else 1.0 - per)
    if not values:
        return None, "NOT_SETTLED"
    if max(values) - min(values) > 1e-6:
        return None, "SETTLEMENT_VALUES_DISAGREE"
    return values[0], "SETTLED"


def _held_close_price(close, direction):
    """Canonical close price of the held contract, or (None, state)."""
    if close is None:
        return None, "NO_CANONICAL_CLOSE", None
    if close.get("close_status") not in CLOSE_USABLE:
        return None, str(close.get("close_status") or "CLOSE_MISSING"), close.get("close_quality")
    held = _num(close.get("mid")) if direction > 0 else _num(close.get("no_mid"))
    if held is None:
        return None, "CLOSE_PRICE_UNAVAILABLE_FOR_SIDE", close.get("close_quality")
    return held, "OK", close.get("close_quality")


def episode_id(ticker, opening_key) -> str:
    return "ep-" + hashlib.sha256(f"{ticker}|{opening_key}".encode()).hexdigest()[:20]


def _benchmark(quote_at, ticker, t, direction_exiting, *, entering=False):
    """Contemporaneous executable YES-axis price for trading AGAINST (exit) or INTO (entry) a position.

    Exit of a long YES sells YES: benchmark = yes_bid. Exit of a long NO buys YES back: benchmark = yes_ask.
    Entry into long YES buys YES: yes_ask; entry into long NO sells YES: yes_bid."""
    if quote_at is None:
        return None, "NO_QUOTE_SOURCE", None
    q = quote_at(ticker, t)
    if not q:
        return None, "NO_QUOTE_AT_OR_BEFORE", None
    age = q.get("age_s")
    if age is None or age > LIVE_BENCHMARK_MAX_AGE_S:
        return None, "QUOTE_STALE", age
    sells_yes = (direction_exiting > 0) != entering
    px = _num(q.get("yes_bid")) if sells_yes else _num(q.get("yes_ask"))
    if px is None:
        return None, "QUOTE_SIDE_EMPTY", age
    return px, "SYNCHRONIZED", age


def build_episodes(rows: list, *, kickoffs: dict | None = None, closes: dict | None = None,
                   finals: dict | None = None, quote_at=None) -> list:
    """Replay order rows (from `actual_wager_postmortem.wager_row`, plus `executed_at`) into episodes.

    kickoffs / finals: game_key -> ISO instant. closes: ticker -> canonical close row. quote_at(ticker, dt)
    -> {"yes_bid", "yes_ask", "age_s"} or None (the contemporaneous live benchmark; optional).
    Returns episode dicts; each row also gains lifecycle annotations (mutated in place)."""
    kickoffs, closes, finals = kickoffs or {}, closes or {}, finals or {}
    by_market: dict = {}
    for r in rows:
        by_market.setdefault(r.get("market_ticker"), []).append(r)
    episodes = []
    for ticker in sorted(by_market, key=lambda t: str(t)):
        mrows = sorted(by_market[ticker], key=lambda r: (str(r.get("executed_at") or ""),
                                                         str(r.get("imported_wager_id") or "")))
        gk = game_key(ticker)
        value, value_state = _settlement_value(mrows)
        pos, avg, cur = 0.0, None, None

        def new_ep(r, direction):
            return {"position_episode_id": episode_id(ticker, r.get("source_bet_key") or r.get("imported_wager_id")),
                    "market_ticker": ticker, "game_key": gk, "game": r.get("game"), "family": r.get("family"),
                    "week": r.get("week"), "season": r.get("season"),
                    "direction": "LONG_YES" if direction > 0 else "LONG_NO", "_dir": direction,
                    "transactions": [], "entry_timestamp": r.get("executed_at"), "exit_timestamp": None,
                    "opening_phase": None, "opened_quantity": 0.0, "closed_quantity": 0.0, "peak_quantity": 0.0,
                    "entry_cost": 0.0, "cashout_proceeds": 0.0, "fees": 0.0, "realized_trading_pnl": 0.0,
                    "fee_ambiguous": False, "_orders": [], "_pregame_entry": [0.0, 0.0], "_capital": 0.0,
                    "peak_capital_at_risk": 0.0, "_order_net": 0.0, "_order_net_complete": True}

        for r in mrows:
            side, qty, price = r.get("side"), _num(r.get("contracts")), _num(r.get("execution_price"))
            fee = _num(r.get("fees")) or 0.0
            action, action_source = _action(r)
            phase, dk, flags = phase_of(r.get("executed_at"), kickoffs.get(gk), finals.get(gk))
            if side not in ("YES", "NO") or qty is None or qty <= 0 or price is None:
                r.update(transaction_role="UNREPLAYABLE", transaction_phase=phase, clv_eligible=False)
                continue
            signed = qty if side == "YES" else -qty
            ypx = _yes_axis_price(side, price)
            before, after = pos, pos + signed
            role = classify(before, after)
            opened = qty if role in ENTRY_ROLES else (abs(after) if role == REVERSE else 0.0)
            closed = qty if role in EXIT_ROLES else (abs(before) if role == REVERSE else 0.0)
            txn = {"imported_wager_id": r.get("imported_wager_id"), "source_bet_key": r.get("source_bet_key"),
                   "executed_at": r.get("executed_at"), "execution_action": action, "action_source": action_source,
                   "outcome_side": side, "signed_quantity": _r(signed, 6), "quantity": qty,
                   "price": price, "yes_axis_price": _r(ypx, 6), "fee": fee,
                   "position_before": _r(before, 6), "position_after": _r(after, 6), "transaction_role": role,
                   "transaction_phase": phase, "seconds_from_scheduled_kickoff": _r(dk, 1), "flags": flags,
                   "opened_quantity": _r(opened, 6), "closed_quantity": _r(closed, 6)}
            realized = None
            if role == OPEN:
                cur = new_ep(r, _sign(after))
                avg = ypx
            elif role in EXIT_ROLES or role == REVERSE:
                realized = (ypx - avg) * closed * _sign(before)
            if role == ADD:
                avg = (avg * abs(before) + ypx * qty) / abs(after)
            txn["realized_trading_pnl"] = _r(realized, 6)
            # Cash: an exit sells the held contract at (held-side price) = 1 - price of the contract bought.
            if role in ENTRY_ROLES:
                cur["entry_cost"] += price * qty + fee
                cur["opened_quantity"] += qty
                cur["fees"] += fee
                cur["_capital"] += price * qty + fee
            elif role in EXIT_ROLES:
                cur["closed_quantity"] += qty
                cur["cashout_proceeds"] += (1.0 - price) * qty
                cur["fees"] += fee
                cur["realized_trading_pnl"] += realized
                cur["_capital"] -= (avg_held(avg, cur["_dir"])) * qty
            cur["peak_quantity"] = max(cur["peak_quantity"], abs(after))
            cur["peak_capital_at_risk"] = max(cur["peak_capital_at_risk"], cur["_capital"])
            if role == REVERSE:
                # One execution spans two episodes. The fee is not split (no rule is documented); both are
                # marked, and the whole fee is charged once to the incoming episode's cash.
                cur["closed_quantity"] += closed
                cur["cashout_proceeds"] += (1.0 - price) * closed
                cur["realized_trading_pnl"] += realized
                cur["fee_ambiguous"] = True
                cur["transactions"].append(dict(txn, closed_quantity=_r(closed, 6), opened_quantity=0.0))
                cur["exit_timestamp"] = r.get("executed_at")
                cur["_orders"].append(r)
                episodes.append(_finish(cur, closes.get(ticker), (value, value_state), "CLOSED_BY_REVERSAL", quote_at, 0.0))
                cur = new_ep(r, _sign(after))
                avg = ypx
                cur["entry_cost"] += price * abs(after) + fee
                cur["opened_quantity"] += abs(after)
                cur["fees"] += fee
                cur["fee_ambiguous"] = True
                cur["_capital"] = price * abs(after) + fee
                cur["peak_capital_at_risk"] = cur["_capital"]
                cur["peak_quantity"] = abs(after)
                txn = dict(txn, closed_quantity=0.0, opened_quantity=_r(abs(after), 6))
            if cur["opening_phase"] is None:
                cur["opening_phase"] = phase
            if role in ENTRY_ROLES or role == REVERSE:
                if phase == PRE_GAME:
                    q_open = qty if role in ENTRY_ROLES else abs(after)
                    cur["_pregame_entry"][0] += q_open
                    cur["_pregame_entry"][1] += q_open * price
            cur["transactions"].append(txn)
            cur["_orders"].append(r)
            r.update(transaction_role=role, transaction_phase=phase, position_episode_id=cur["position_episode_id"],
                     execution_action=action, action_source=action_source, position_before=_r(before, 6),
                     position_after=_r(after, 6),
                     clv_eligible=(role in ENTRY_ROLES and phase == PRE_GAME))
            pos = after
            if role == CASHOUT_CLOSE:
                cur["exit_timestamp"] = r.get("executed_at")
                episodes.append(_finish(cur, closes.get(ticker), (value, value_state), "CLOSED_BY_TRADING", quote_at, 0.0))
                cur, avg, pos = None, None, 0.0
        if cur is not None:
            remaining = abs(pos)
            episodes.append(_finish(cur, closes.get(ticker), (value, value_state), "HELD_TO_SETTLEMENT",
                                    quote_at, remaining, avg=avg))
    return episodes


def avg_held(avg_yes, direction):
    return avg_yes if direction > 0 else 1.0 - avg_yes


def _finish(ep, close, settlement, how, quote_at, remaining, avg=None) -> dict:
    d = ep["_dir"]
    txns = ep["transactions"]
    # Settlement of whatever remained.
    settlement_pnl, settled = 0.0, True
    ep["settlement_state"] = "NOT_APPLICABLE"
    if how == "HELD_TO_SETTLEMENT":
        value, state = settlement
        ep["settlement_state"] = state
        if remaining > QTY_EPS:
            if value is None:
                settlement_pnl, settled = None, False
            else:
                held_value = value if d > 0 else 1.0 - value
                settlement_pnl = (held_value - avg_held(avg, d)) * remaining
                ep["settlement_value_yes"] = _r(value, 6)
                ep["settlement_payout"] = _r(held_value * remaining, 6)
                txns.append({"transaction_role": SETTLEMENT, "transaction_phase": POST_FINAL,
                             "quantity": _r(remaining, 6), "yes_axis_price": _r(value, 6),
                             "position_before": _r(remaining * d, 6), "position_after": 0.0,
                             "realized_trading_pnl": None, "settlement_pnl": _r(settlement_pnl, 6)})
    elif settlement and settlement[0] is not None and ep["closed_quantity"] > QTY_EPS:
        # HINDSIGHT ONLY: what the exited contracts would have paid at settlement. Not exit quality -- the
        # owner could not know the result -- and never part of any P&L figure.
        value = settlement[0]
        held_value = value if d > 0 else 1.0 - value
        ep["settlement_value_yes"] = _r(value, 6)
        ep["hindsight_hold_payout_of_exited"] = _r(held_value * ep["closed_quantity"], 6)
        ep["hindsight_cashout_vs_hold"] = _r(ep["cashout_proceeds"] - held_value * ep["closed_quantity"], 6)
    ep["remaining_position"] = _r(remaining, 6)
    ep["settlement_pnl"] = _r(settlement_pnl, 6)
    ep["realized_trading_pnl"] = _r(ep["realized_trading_pnl"], 6)
    ep["fees"] = _r(ep["fees"], 6)
    ep["entry_cost"] = _r(ep["entry_cost"], 6)
    ep["cashout_proceeds"] = _r(ep["cashout_proceeds"], 6)
    ep["peak_capital_at_risk"] = _r(ep["peak_capital_at_risk"], 6)
    ep["total_episode_pnl"] = (None if settlement_pnl is None
                               else _r(ep["realized_trading_pnl"] + settlement_pnl - ep["fees"], 6))
    # Cross-check against the orders' own settlement figures (gross - stake, summed).
    order_net = [(_num(o.get("gross_return")), _num(o.get("stake"))) for o in ep["_orders"]]
    if all(g is not None and s is not None for g, s in order_net) and order_net:
        cash = sum(g - s for g, s in order_net)
        ep["cash_pnl_from_orders"] = _r(cash, 6)
        if ep["total_episode_pnl"] is None:
            ep["reconciliation"] = "LIFECYCLE_PNL_UNESTABLISHED"
        elif ep["fee_ambiguous"]:
            ep["reconciliation"] = "FEE_ALLOCATION_AMBIGUOUS_REVERSAL"
        else:
            ep["reconciliation"] = ("RECONCILED" if abs(cash - ep["total_episode_pnl"]) <= MONEY_TOL
                                    else "MISMATCH")
    else:
        ep["cash_pnl_from_orders"] = None
        ep["reconciliation"] = "ORDER_SETTLEMENTS_INCOMPLETE"

    roles = [t["transaction_role"] for t in txns]
    n_red = roles.count(REDUCE)
    ep["adds"] = roles.count(ADD)
    ep["reductions"] = n_red
    ep["cashouts"] = roles.count(CASHOUT_CLOSE) + (1 if how == "CLOSED_BY_REVERSAL" else 0)
    ep["closed_by"] = how
    exit_phases = [t["transaction_phase"] for t in txns if t["transaction_role"] in EXIT_ROLES + (REVERSE,)]
    ep["exit_phase"] = exit_phases[-1] if exit_phases else None
    if how == "HELD_TO_SETTLEMENT":
        ep["cashout_state"] = "PARTIAL_CASHOUT" if n_red else "HELD_TO_SETTLEMENT"
    elif how == "CLOSED_BY_REVERSAL":
        ep["cashout_state"] = "REVERSED"
    else:
        ep["cashout_state"] = "FULL_CASHOUT"
    op = ep["opening_phase"] or UNKNOWN
    if ep["cashout_state"] == "HELD_TO_SETTLEMENT":
        cls = f"{'PREGAME' if op == PRE_GAME else op}_POSITION_HELD_TO_SETTLEMENT"
    else:
        exit_ph = "LIVE" if ep["exit_phase"] == LIVE else (ep["exit_phase"] or UNKNOWN)
        cls = f"{'PREGAME' if op == PRE_GAME else op}_POSITION_{ep['cashout_state']}_{exit_ph}"
    ep["position_classification"] = cls
    ep["thesis"] = "PREGAME_THESIS" if op == PRE_GAME else ("LIVE_THESIS" if op == LIVE else "UNKNOWN_THESIS")

    # ENTRY QUALITY: pregame entry CLV, one observation per episode.
    q, notional = ep["_pregame_entry"]
    held_close, cstate, quality = _held_close_price(close, d)
    if q <= QTY_EPS:
        ep["entry_clv_state"] = ("NOT_APPLICABLE_LIVE_ENTRY" if op in (LIVE, POST_FINAL)
                                 else "PHASE_UNKNOWN_NO_PREGAME_CLV")
        ep["pregame_entry_clv_per_contract"] = None
    elif held_close is None:
        ep["entry_clv_state"] = cstate
        ep["pregame_entry_clv_per_contract"] = None
    else:
        clv = held_close - notional / q
        ep["pregame_entry_clv_per_contract"] = _r(clv, 6)
        ep["pregame_entry_clv_dollars"] = _r(clv * q, 6)
        ep["pregame_entry_quantity"] = _r(q, 6)
        ep["close_price_held_side"] = held_close
        ep["entry_clv_state"] = "CLV_VALID" if quality in USABLE_QUALITY else f"CLV_{quality}_CLOSE"

    # EXIT QUALITY: live exits against the contemporaneous executable quote. Never the pregame close.
    exits = []
    for t in txns:
        if t["transaction_role"] not in EXIT_ROLES + (REVERSE,):
            continue
        if t["transaction_phase"] != LIVE:
            exits.append({"executed_at": t["executed_at"], "state": f"EXIT_{t['transaction_phase']}_NO_LIVE_BENCHMARK"})
            continue
        bench, bstate, age = _benchmark(quote_at, ep["market_ticker"], _dt(t["executed_at"]), d)
        e = {"executed_at": t["executed_at"], "exit_yes_axis_price": t["yes_axis_price"], "quantity": t["closed_quantity"],
             "benchmark_yes_axis_price": bench, "benchmark_age_s": _r(age, 1)}
        if bench is None:
            e["state"] = "NO_VALID_LIVE_EXIT_BENCHMARK"
            e["reason"] = bstate
        else:
            # Selling YES (exiting long YES): higher is better. Buying YES back (exiting long NO): lower is better.
            per = (t["yes_axis_price"] - bench) * d
            e.update(state="LIVE_EXIT_VALUE", live_exit_value_per_contract=_r(per, 6),
                     live_exit_value_dollars=_r(per * (t["closed_quantity"] or 0.0), 6))
        exits.append(e)
    ep["exit_quality"] = exits
    # Live entries: descriptive comparison with the contemporaneous quote (not CLV).
    live_entries = []
    for t in txns:
        if t["transaction_role"] in ENTRY_ROLES and t["transaction_phase"] == LIVE:
            bench, bstate, age = _benchmark(quote_at, ep["market_ticker"], _dt(t["executed_at"]), d, entering=True)
            le = {"executed_at": t["executed_at"], "benchmark_yes_axis_price": bench, "benchmark_age_s": _r(age, 1)}
            if bench is None:
                le.update(state="NO_VALID_LIVE_ENTRY_BENCHMARK", reason=bstate)
            else:
                le.update(state="LIVE_ENTRY_VS_QUOTE",
                          live_entry_value_per_contract=_r((bench - t["yes_axis_price"]) * d, 6))
            live_entries.append(le)
    ep["live_entry_quality"] = live_entries
    ep["transaction_count"] = sum(1 for t in txns if t["transaction_role"] != SETTLEMENT)
    for k in ("_dir", "_orders", "_pregame_entry", "_capital", "_order_net", "_order_net_complete"):
        ep.pop(k, None)
    return ep


def summarise(episodes: list) -> dict:
    """The economically meaningful record: counts of independent positions, not of orders."""
    n = len(episodes)
    clv = [e for e in episodes if e.get("entry_clv_state") == "CLV_VALID"]
    vals = [e["pregame_entry_clv_per_contract"] for e in clv]
    pnl = [e.get("total_episode_pnl") for e in episodes]
    complete = n > 0 and all(p is not None for p in pnl)
    pos = [e for e in episodes if (e.get("total_episode_pnl") or 0) > 0]
    exits = [x for e in episodes for x in e.get("exit_quality") or []]
    exit_valued = [x for x in exits if x.get("state") == "LIVE_EXIT_VALUE"]
    return {
        "independent_position_episodes": n,
        "transactions": sum(e.get("transaction_count", 0) for e in episodes),
        "pregame_thesis_count": sum(1 for e in episodes if e.get("thesis") == "PREGAME_THESIS"),
        "live_thesis_count": sum(1 for e in episodes if e.get("thesis") == "LIVE_THESIS"),
        "unknown_phase_thesis_count": sum(1 for e in episodes if e.get("thesis") == "UNKNOWN_THESIS"),
        "near_scheduled_kickoff_openings": sum(
            1 for e in episodes if e["transactions"] and "NEAR_SCHEDULED_KICKOFF" in (e["transactions"][0].get("flags") or [])),
        "full_cashout_count": sum(1 for e in episodes if e.get("cashout_state") == "FULL_CASHOUT"),
        "partial_cashout_count": sum(1 for e in episodes if e.get("cashout_state") == "PARTIAL_CASHOUT"),
        "reversal_count": sum(1 for e in episodes if e.get("cashout_state") == "REVERSED"),
        "held_to_settlement_count": sum(1 for e in episodes if e.get("cashout_state") == "HELD_TO_SETTLEMENT"),
        "classifications": _count(e.get("position_classification") for e in episodes),
        "complete": complete,
        "total_pnl": _r(sum(pnl), 4) if complete else None,
        "positive_episodes": len(pos),
        "non_positive_episodes": (n - len(pos)) if complete else None,
        "entry_cost": _r(sum(e.get("entry_cost") or 0.0 for e in episodes), 4),
        "cashout_proceeds": _r(sum(e.get("cashout_proceeds") or 0.0 for e in episodes), 4),
        "fees": _r(sum(e.get("fees") or 0.0 for e in episodes), 4),
        "realized_trading_pnl": _r(sum(e.get("realized_trading_pnl") or 0.0 for e in episodes), 4),
        "settlement_pnl": (_r(sum(e.get("settlement_pnl") or 0.0 for e in episodes), 4) if complete else None),
        "pregame_entry_clv": {
            "valid": len(vals),
            "mean_per_contract": _r(sum(vals) / len(vals), 6) if vals else None,
            "positive_rate": _r(sum(1 for v in vals if v > 0) / len(vals), 4) if vals else None,
            "states": _count(e.get("entry_clv_state") for e in episodes)},
        "live_exit_benchmark": {"exits": len(exits), "valued": len(exit_valued),
                                "states": _count(x.get("state") for x in exits)},
        "reconciliation": _count(e.get("reconciliation") for e in episodes),
    }


def _count(it) -> dict:
    out: dict = {}
    for k in it:
        out[str(k)] = out.get(str(k), 0) + 1
    return dict(sorted(out.items()))


def exposure(orders: list, episodes: list) -> dict:
    """GROSS TRANSACTION VOLUME vs CAPITAL AT RISK, per game.

    ORIGINAL CASH OUTLAY   cost + fees of every OPEN (the first money committed to each position)
    ADDITIONAL CASH ADDED  cost + fees of every ADD
    CASHOUT PROCEEDS       what exits returned (held-side price x quantity, before exit fees)
    GROSS TRANSACTION VOLUME  the sum of every order's `stake` -- turnover, NOT risk. A cashout bought on the
                           complementary side carries a large `stake` while returning cash.
    MAX SIMULTANEOUS CAPITAL AT RISK  the peak, over the game's transaction timeline, of the cost basis (plus
                           entry fees) of everything open at once. For a Kalshi long that is the maximum loss.
    MAX LOSS (at peak)     identical to the above for long binary positions.
    CONTRACT NOTIONAL      peak contracts x $1 of the same timeline.
    NET DIRECTIONAL EXPOSURE is not summed across markets: different contracts are not one direction.
    """
    by_game: dict = {}
    for o in orders:
        by_game.setdefault(game_key(o.get("market_ticker")), []).append(o)
    out = {}
    for g, rows in sorted(by_game.items()):
        eps = [e for e in episodes if e.get("game_key") == g]
        vol = sum(_num(r.get("stake")) or 0.0 for r in rows)
        opening = sum((_num(r.get("stake")) or 0.0) for r in rows if r.get("transaction_role") == OPEN)
        added = sum((_num(r.get("stake")) or 0.0) for r in rows if r.get("transaction_role") == ADD)
        # Timeline of open capital: per market, basis moves with each entry/exit.
        events = []
        for e in eps:
            for t in e["transactions"]:
                if t.get("executed_at"):
                    events.append((t["executed_at"], e["position_episode_id"], t))
        events.sort(key=lambda x: x[0])
        basis: dict = {}
        qty: dict = {}
        peak, peak_at, peak_q = 0.0, None, 0.0
        for ts, eid, t in events:
            role = t["transaction_role"]
            b, q = basis.get(eid, 0.0), qty.get(eid, 0.0)
            if role in ENTRY_ROLES or (role == OPEN):
                b += t["price"] * t["quantity"] + (t.get("fee") or 0.0)
                q += t["quantity"]
            elif role in EXIT_ROLES:
                frac = (t["quantity"] / q) if q > QTY_EPS else 1.0
                b -= b * min(1.0, frac)
                q = max(0.0, q - t["quantity"])
            elif role == REVERSE:
                b, q = t["price"] * (t["opened_quantity"] or 0.0) + (t.get("fee") or 0.0), t["opened_quantity"] or 0.0
            basis[eid], qty[eid] = b, q
            total = sum(basis.values())
            if total > peak + 1e-9:
                peak, peak_at, peak_q = total, ts, sum(qty.values())
        out[g] = {
            "orders": len(rows), "position_episodes": len(eps),
            "original_cash_outlay": _r(opening, 4), "additional_cash_added": _r(added, 4),
            "cashout_proceeds": _r(sum(e.get("cashout_proceeds") or 0.0 for e in eps), 4),
            "gross_transaction_volume": _r(vol, 4),
            "recycled_capital_in_volume": _r(vol - opening - added, 4),
            "max_simultaneous_capital_at_risk": _r(peak, 4), "peak_at": peak_at,
            "max_loss_at_peak": _r(peak, 4), "contract_notional_at_peak": _r(peak_q, 4),
            "total_pnl": (_r(sum(e["total_episode_pnl"] for e in eps), 4)
                          if eps and all(e.get("total_episode_pnl") is not None for e in eps) else None),
        }
    return out


# ------------------------------------------------------------------ live benchmark source

class CaptureQuoteLookup:
    """Contemporaneous quotes from the 10-minute Kalshi capture on `market-data`, for LIVE_EXIT_VALUE.

    `list_runs(date) -> [quote file paths]` and `read(path) -> iterable of JSON lines` abstract the storage (a
    checkout, or `git show` against a blobless clone so only the one or two files needed are fetched). The quote
    used is the latest row for the ticker observed AT OR BEFORE the transaction; its age is reported and
    `_benchmark` refuses one older than LIVE_BENCHMARK_MAX_AGE_S. The capture is change-suppressed, so an old
    row may still have been the live price -- that is not assumed: stale is refused."""

    def __init__(self, list_runs, read, runs_back: int = 3):
        self.list_runs, self.read, self.runs_back = list_runs, read, runs_back
        self._cache: dict = {}

    def _runs_before(self, t):
        import datetime as _d
        paths = []
        for day in (t - _d.timedelta(days=1), t):
            paths.extend(self.list_runs(day.strftime("%Y-%m-%d")) or [])

        def run_dt(p):
            try:
                return datetime.strptime(p.rsplit("/", 1)[-1][:16], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            except ValueError:
                return None
        runs = sorted((run_dt(p), p) for p in paths if run_dt(p) is not None and run_dt(p) <= t)
        return [p for _, p in runs[-self.runs_back:]]

    def __call__(self, ticker, t):
        if t is None:
            return None
        best = None
        needle = f'"ticker":"{ticker}"'
        for path in self._runs_before(t):
            if path not in self._cache:
                self._cache[path] = list(self.read(path) or [])
            for line in self._cache[path]:
                if needle not in line:
                    continue
                try:
                    import json as _json
                    row = _json.loads(line)
                except ValueError:
                    continue
                if row.get("ticker") != ticker:
                    continue
                obs = _dt(row.get("observed_at"))
                if obs is None or obs > t:
                    continue
                if best is None or obs > best[0]:
                    best = (obs, row)
        if best is None:
            return None
        obs, row = best
        return {"yes_bid": _num(row.get("yes_bid_dollars")), "yes_ask": _num(row.get("yes_ask_dollars")),
                "observed_at": _iso(obs), "age_s": (t - obs).total_seconds()}


# ------------------------------------------------------------------ anti-chase governance (report only)

ANTI_CHASE_NOTE = (
    "ANTI-CHASE GOVERNANCE -- REPORTING ONLY. Previous losses are sunk: past P&L never changes the probability of "
    "a new wager and a past loss never justifies a larger stake. These flags describe what the transaction "
    "timeline shows; nothing here blocks, sizes or recommends a wager."
)


def anti_chase(episodes: list, *, stake_escalation_ratio: float = 1.5,
               single_game_capital_share: float = 0.5, exposures: dict | None = None) -> list:
    """CHASE_RISK, STAKE_ESCALATION_AFTER_LOSS, REPEATED_ADD_AFTER_ADVERSE_MOVE, SINGLE_GAME_EXPOSURE_HIGH,
    CORRELATED_EXPOSURE_HIGH -- each with the evidence that fired it.

    A LOSS IS KNOWN at a trading exit's own timestamp. A settlement's loss time is not captured here (the
    router's `settled_at` is a delivery instant), so settled losses are not used as a trigger: the flags can
    only under-fire, never invent a loss the owner could not have seen."""
    flags = []
    ordered = sorted(episodes, key=lambda e: str(e.get("entry_timestamp") or ""))
    losses = [(e.get("exit_timestamp"), e) for e in episodes
              if e.get("closed_by") in ("CLOSED_BY_TRADING", "CLOSED_BY_REVERSAL")
              and (e.get("total_episode_pnl") or 0) < 0 and e.get("exit_timestamp")]
    for e in ordered:
        t0 = str(e.get("entry_timestamp") or "")
        prior_losses = [x for ts, x in losses if str(ts) < t0]
        if prior_losses:
            same_game = [x for x in prior_losses if x.get("game_key") == e.get("game_key")]
            if same_game:
                flags.append({"code": "CHASE_RISK", "subject": e["position_episode_id"], "market": e["market_ticker"],
                              "detail": f"opened after {len(same_game)} realized trading loss(es) in the same game"})
            last = max(prior_losses, key=lambda x: str(x.get("exit_timestamp")))
            if (last.get("entry_cost") or 0) > 0 and (e.get("entry_cost") or 0) > stake_escalation_ratio * last["entry_cost"]:
                flags.append({"code": "STAKE_ESCALATION_AFTER_LOSS", "subject": e["position_episode_id"],
                              "market": e["market_ticker"],
                              "detail": f"cash outlay {e['entry_cost']:.2f} > {stake_escalation_ratio}x the last "
                                        f"realized loser's {last['entry_cost']:.2f}"})
        d = 1 if e.get("direction") == "LONG_YES" else -1
        avg, q = None, 0.0
        for t in e["transactions"]:
            if t["transaction_role"] == OPEN:
                avg, q = t["yes_axis_price"], t["quantity"]
            elif t["transaction_role"] == ADD and avg is not None:
                if (t["yes_axis_price"] - avg) * d < 0:
                    flags.append({"code": "REPEATED_ADD_AFTER_ADVERSE_MOVE", "subject": e["position_episode_id"],
                                  "market": e["market_ticker"],
                                  "detail": f"added at {t['yes_axis_price']:.4f} (YES axis) against an average "
                                            f"entry of {avg:.4f}"})
                avg = (avg * q + t["yes_axis_price"] * t["quantity"]) / (q + t["quantity"])
                q += t["quantity"]
    if exposures:
        peaks = {g: x.get("max_simultaneous_capital_at_risk") or 0.0 for g, x in exposures.items()}
        total = sum(peaks.values())
        for g, p in sorted(peaks.items()):
            if len(peaks) > 1 and total > 0 and p / total > single_game_capital_share:
                flags.append({"code": "SINGLE_GAME_EXPOSURE_HIGH", "subject": g,
                              "detail": f"peak capital at risk {p:.2f} is {100 * p / total:.1f}% of the sum of "
                                        f"per-game peaks (> {100 * single_game_capital_share:.0f}%)"})
            n_eps = exposures[g].get("position_episodes") or 0
            if n_eps >= 3:
                flags.append({"code": "CORRELATED_EXPOSURE_HIGH", "subject": g,
                              "detail": f"{n_eps} position episodes on one game settle on one game state"})
    return flags


def build(rows: list, *, kickoffs=None, closes=None, finals=None, quote_at=None) -> dict:
    episodes = build_episodes(rows, kickoffs=kickoffs, closes=closes, finals=finals, quote_at=quote_at)
    ex = exposure(rows, episodes)
    return {"lifecycle_version": LIFECYCLE_VERSION, "header": HEADER, "summary": summarise(episodes),
            "episodes": episodes, "exposure_by_game": ex,
            "anti_chase": {"note": ANTI_CHASE_NOTE, "flags": anti_chase(episodes, exposures=ex)}}


# ------------------------------------------------------------------ rendering

def _m(v):
    return "—" if v is None else f"{v:,.2f}"


def render_section(doc: dict | None) -> list:
    if not doc:
        return []
    s = doc["summary"]
    L = ["## POSITION EPISODES (the economically meaningful record)", "", f"> {doc['header']}", "",
         f"* Independent position episodes: **{s['independent_position_episodes']}** (from {s['transactions']} "
         f"transactions/orders)",
         f"* Pregame thesis: {s['pregame_thesis_count']} · live thesis: {s['live_thesis_count']} · unknown phase: "
         f"{s['unknown_phase_thesis_count']} · opened within 10 min after scheduled kickoff: "
         f"{s['near_scheduled_kickoff_openings']}",
         f"* Full cashouts: {s['full_cashout_count']} · partial cashouts: {s['partial_cashout_count']} · reversals: "
         f"{s['reversal_count']} · held to settlement: {s['held_to_settlement_count']}",
         f"* Total P&L (all executions and fees): {_m(s['total_pnl'])} = realized trading {_m(s['realized_trading_pnl'])}"
         f" + settlement {_m(s['settlement_pnl'])} - fees {_m(s['fees'])}",
         f"* PREGAME ENTRY CLV (one observation per pregame-opened episode; exits and live entries excluded): "
         f"{s['pregame_entry_clv']['valid']} valid, mean "
         f"{'—' if s['pregame_entry_clv']['mean_per_contract'] is None else format(s['pregame_entry_clv']['mean_per_contract'], '+.4f')}"
         f"/contract, positive {'—' if s['pregame_entry_clv']['positive_rate'] is None else format(100 * s['pregame_entry_clv']['positive_rate'], '.1f') + '%'}; "
         f"states {s['pregame_entry_clv']['states']}",
         f"* Live exit benchmark: {s['live_exit_benchmark']}",
         f"* Lifecycle vs order-settlement reconciliation: {s['reconciliation']}", "",
         "| episode | market | opened | phase | side | opened qty | entry cost | adds | reductions | cashouts | "
         "final qty | settlement | fees | realized trading | settlement P&L | total P&L | entry CLV | exit benchmark | class |",
         "|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for e in doc["episodes"]:
        clv = (format(e["pregame_entry_clv_per_contract"], "+.4f") if e.get("pregame_entry_clv_per_contract") is not None
               else e.get("entry_clv_state"))
        ex = ", ".join(x.get("state") + (f" {x['live_exit_value_per_contract']:+.4f}" if x.get("live_exit_value_per_contract") is not None else "")
                       for x in e.get("exit_quality") or []) or "—"
        L.append(f"| {e['position_episode_id']} | {e['market_ticker']} | {e['entry_timestamp']} | {e['opening_phase']} | "
                 f"{e['direction']} | {e['opened_quantity']:g} | {_m(e['entry_cost'])} | {e['adds']} | {e['reductions']} | "
                 f"{e['cashouts']} | {e['remaining_position']:g} | {e['settlement_state']} | {_m(e['fees'])} | "
                 f"{_m(e['realized_trading_pnl'])} | {_m(e['settlement_pnl'])} | {_m(e['total_episode_pnl'])} | {clv} | "
                 f"{ex} | {e['position_classification']} |")
    L.extend(["", "### Transactions (chronological, per market)", "",
              "| market | executed | action | side | qty | price | fee | before | after | role | phase | flags |",
              "|---|---|---|---|---|---|---|---|---|---|---|---|"])
    for e in doc["episodes"]:
        for t in e["transactions"]:
            L.append(f"| {e['market_ticker']} | {t.get('executed_at') or '(settlement)'} | "
                     f"{t.get('execution_action', '—')}{'*' if t.get('action_source') == ACTION_ASSUMED else ''} | "
                     f"{t.get('outcome_side', '—')} | {t.get('quantity')} | {t.get('price', t.get('yes_axis_price'))} | "
                     f"{t.get('fee', '—')} | {t.get('position_before')} | {t.get('position_after')} | "
                     f"{t['transaction_role']} | {t['transaction_phase']} | {', '.join(t.get('flags') or []) or '—'} |")
    L.extend(["", "`*` the verb was not delivered (pre-`execution_action` record); the side is replayed as the exposure "
              "it states. Position before/after are on Kalshi's signed YES axis (+ long YES, - long NO).", "",
              "### Exposure: turnover vs capital at risk", "",
              "| game | orders | episodes | original cash outlay | added | cashout proceeds | gross transaction volume | "
              "recycled in volume | max simultaneous capital at risk | at | total P&L |",
              "|---|---|---|---|---|---|---|---|---|---|---|"])
    for g, x in doc["exposure_by_game"].items():
        L.append(f"| {g} | {x['orders']} | {x['position_episodes']} | {_m(x['original_cash_outlay'])} | "
                 f"{_m(x['additional_cash_added'])} | {_m(x['cashout_proceeds'])} | {_m(x['gross_transaction_volume'])} | "
                 f"{_m(x['recycled_capital_in_volume'])} | {_m(x['max_simultaneous_capital_at_risk'])} | {x['peak_at']} | "
                 f"{_m(x['total_pnl'])} |")
    L.extend(["", "Gross transaction volume is the sum of order stakes (turnover). It is NOT capital at risk: an exit "
              "bought on the complementary side carries a large stake while returning cash.", "",
              "### Anti-chase governance", "", f"> {doc['anti_chase']['note']}", ""])
    fl = doc["anti_chase"]["flags"]
    if not fl:
        L.append("No flags.")
    else:
        L.extend(["| code | subject | market | detail |", "|---|---|---|---|"])
        for f in fl:
            L.append(f"| {f['code']} | {f['subject']} | {f.get('market', '—')} | {f['detail']} |")
    L.append("")
    return L
