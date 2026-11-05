"""RESEARCH ONLY: structural selection / exposure rules for NFL wagers, as pure functions over position facts.

Nothing in this module is imported by the card builder, the staking ladder, the risk policy or any workflow. It exists so that a
rule can be written down, unit-tested and replayed on settled positions BEFORE anyone considers activating it. Activating a rule
is an owner decision (it can only remove or shrink positions, so it is a restriction, but it still changes real exposure).

A "position fact" is a dict with at least:
    cost       dollars at risk including the entry fee (stake = price * contracts + fees: fees counted once)
    pnl        realised net profit/loss in dollars (fees already inside), or None when not established
    fees       entry + settlement fees inside `pnl`
    game_key   shared by every market on one game; None for parlays
    family     coarse market family ("spread", "total", "team total", "moneyline", "first-half / quarter market",
               a player-prop label, or "parlay (multi-leg combo)")
    avg_price  price paid per contract on the held side (0-1)
    phase      "PRE_GAME" | "LIVE" | "UNKNOWN"
    t          sortable entry time (ISO string); used so "earliest wins" is deterministic and point-in-time
    units      cost / one unit (the owner's 1U)

Every rule returns a new list of facts with `cost`, `pnl`, `fees` scaled by `keep` in [0, 1] (`keep` = 0 removes the position).
Scaling is LINEAR in the position, which is an assumption: a smaller order could have filled at a different price or not at all, and
the exchange's fee rounding is not linear. The result is an illustration of exposure, never a forecast.
"""
from __future__ import annotations

PARLAY = "parlay (multi-leg combo)"
GAME_MARKETS = ("spread", "total", "team total", "moneyline", "first-half / quarter market")


def _scaled(f: dict, keep: float) -> dict:
    g = dict(f)
    g["keep"] = f.get("keep", 1.0) * keep
    for k in ("cost", "pnl", "fees", "units"):
        if g.get(k) is not None:
            g[k] = f[k] * keep
    return g


def _is_parlay(f: dict) -> bool:
    return f.get("family") == PARLAY


def rule_no_parlays(facts: list) -> list:
    """Parlay tickets carry the heaviest fee load and no identifiable game; drop them."""
    return [_scaled(f, 0.0 if _is_parlay(f) else 1.0) for f in facts]


def rule_cap_bet(facts: list, max_units: float = 5.0) -> list:
    """No single position above `max_units` (the owner's existing per-bet maximum)."""
    out = []
    for f in facts:
        u = f.get("units") or 0.0
        out.append(_scaled(f, min(1.0, max_units / u) if u > max_units else 1.0))
    return out


def rule_cap_game(facts: list, max_units: float = 5.0) -> list:
    """Combined outlay on one game (all its markets are one game state) is capped; earlier positions keep their size and the
    position that crosses the cap is truncated. Parlays have no game and are untouched."""
    spent: dict = {}
    out = []
    for f in sorted(facts, key=lambda x: (str(x.get("t") or ""), str(x.get("episode") or ""))):
        g = f.get("game_key")
        u = f.get("units") or 0.0
        if _is_parlay(f) or not g or u <= 0:
            out.append(_scaled(f, 1.0))
            continue
        room = max(0.0, max_units - spent.get(g, 0.0))
        keep = min(1.0, room / u)
        spent[g] = spent.get(g, 0.0) + u * keep
        out.append(_scaled(f, keep))
    return out


def rule_one_position_per_game(facts: list) -> list:
    """Only the earliest position on a game survives. Parlays are untouched (they have no game)."""
    seen: set = set()
    out = []
    for f in sorted(facts, key=lambda x: (str(x.get("t") or ""), str(x.get("episode") or ""))):
        g = f.get("game_key")
        if _is_parlay(f) or not g:
            out.append(_scaled(f, 1.0))
        elif g in seen:
            out.append(_scaled(f, 0.0))
        else:
            seen.add(g)
            out.append(_scaled(f, 1.0))
    return out


def rule_min_price(facts: list, floor: float = 0.30) -> list:
    """No contract bought below `floor`: the Kalshi fee is proportional to p(1-p), so a cheap contract pays the largest share of
    its price in fees, and the longshot tail is where a hit-rate shortfall is hardest to see."""
    return [_scaled(f, 0.0 if (f.get("avg_price") is not None and f["avg_price"] < floor) else 1.0) for f in facts]


def rule_no_live_entries(facts: list) -> list:
    return [_scaled(f, 0.0 if f.get("phase") == "LIVE" else 1.0) for f in facts]


def rule_game_markets_only(facts: list) -> list:
    """Keep spreads, totals, team totals, moneylines and first-half/quarter markets; drop player props and parlays."""
    return [_scaled(f, 1.0 if f.get("family") in GAME_MARKETS else 0.0) for f in facts]


def rule_key_number_edge_guard(facts: list, min_edge: float = 0.02) -> list:
    """Drop a spread position whose KEY-NUMBER-AWARE edge over the sportsbook closing line (`book_edge_key`, held side, after the price
    actually paid) is below `min_edge` (default 2c: about the fee plus half a spread). Positions with no `book_edge_key` (every non-spread
    market) are untouched. A plain-Normal fair value sees a phantom edge on the rung just past a key number; this guard does not.

    Caveat carried by the field, not by this function: the sportsbook CLOSING line is a stand-in for the line known when the order was placed."""
    return [_scaled(f, 0.0 if (f.get("book_edge_key") is not None and f["book_edge_key"] < min_edge) else 1.0) for f in facts]


def compose(*rules):
    def run(facts: list) -> list:
        for r in rules:
            facts = r(facts)
        return facts
    return run


#: The rule set that was written down BEFORE the chronological hold-out (weeks 5-8) was read. Order is the Bonferroni family.
RULES = {
    "no_parlays": rule_no_parlays,
    "cap_bet_5U": rule_cap_bet,
    "cap_game_5U": rule_cap_game,
    "one_position_per_game": rule_one_position_per_game,
    "min_price_30c": rule_min_price,
    "no_live_entries": rule_no_live_entries,
    "game_markets_only": rule_game_markets_only,
    "structural_policy (no parlays + 5U/bet + 5U/game)": compose(rule_no_parlays, rule_cap_bet, rule_cap_game),
    "spread_key_number_guard (>= 2c key-aware edge)": rule_key_number_edge_guard,
}
