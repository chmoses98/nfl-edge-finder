"""Kalshi price semantics. Prices are whole cents; a price of 0 or 100 is not quotable.

Every NFL market observed carries `price_level_structure = "linear_cent"`, so the tick is one cent
throughout and there are no coarser bands to special-case. Passive levels must be legal prices: a study that
rests an order at 0.435 is studying a market that does not exist.
"""
from __future__ import annotations

import math

TICK = 0.01
MIN_PRICE = 0.01
MAX_PRICE = 0.99


def is_valid_price(p: float) -> bool:
    if p is None or not (MIN_PRICE - 1e-9 <= p <= MAX_PRICE + 1e-9):
        return False
    return abs(round(p * 100) - p * 100) < 1e-6


def round_to_tick(p: float) -> float | None:
    """Nearest legal price, or None if outside the quotable range."""
    if p is None:
        return None
    v = round(round(p * 100) / 100.0, 2)
    if v < MIN_PRICE - 1e-9 or v > MAX_PRICE + 1e-9:
        return None
    return v


def tick_up(p: float, n: int = 1) -> float | None:
    return round_to_tick(round(p * 100 + n) / 100.0) if p is not None else None


def tick_down(p: float, n: int = 1) -> float | None:
    return round_to_tick(round(p * 100 - n) / 100.0) if p is not None else None


def passive_levels(yes_bid: float, yes_ask: float, side: str):
    """Legal passive prices for a resting order on `side`, from most to least aggressive.

    A YES buyer rests at or below the current best bid+1; resting AT the ask would cross and is a taker, so
    it is not a passive level and is deliberately absent.
    """
    if yes_bid is None or yes_ask is None:
        return {}
    out = {}
    if side == "yes":
        join = round_to_tick(yes_bid)
        improve = tick_up(yes_bid)
        if improve is not None and improve >= yes_ask - 1e-9:
            improve = None                      # improving would cross the spread; not passive
        out = {"join_bid": join, "improve_bid": improve}
    else:                                        # NO buyer rests on the other side of the book
        join = round_to_tick(1.0 - yes_ask)
        improve = tick_up(1.0 - yes_ask)
        if improve is not None and improve >= (1.0 - yes_bid) - 1e-9:
            improve = None
        out = {"join_bid": join, "improve_bid": improve}
    return {k: v for k, v in out.items() if v is not None and is_valid_price(v)}
