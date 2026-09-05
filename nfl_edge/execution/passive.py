"""Passive execution research primitives, with the four concepts kept strictly apart.

The temptation in this work is to collapse four different things into one number. They are:

  1. THEORETICAL ECONOMICS    what the EV would be IF filled at price L. Says nothing about filling.
  2. TOUCH                    the quoted book subsequently reached L. Necessary, nowhere near sufficient.
  3. TRADE-AT-LEVEL           a trade actually printed at or through L with the taker on our side of the
                              book, so resting orders at L were being hit. Still an UPPER BOUND on our own
                              fill, because queue position is unobservable historically.
  4. PROSPECTIVE FILL         a shadow order placed before the fact, with a captured book snapshot giving
                              size ahead, evaluated forward. Only this is evidence about our fill.

Historical 2025 data supports 1, 2 and 3. It cannot support 4: Kalshi's trade feed gives price, size, time
and which side the taker hit, but not order identity or queue priority. So nothing here may be called a fill.

Convention for the trade feed: `taker_book_side == "bid"` means the taker SOLD into resting bids, so resting
YES buy orders were the ones executed. A resting YES buy at L is *reachable* by such a trade when it prints
at a YES price <= L. That is the trade-at-level test, and it remains an upper bound.
"""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PassiveOutcome:
    """What happened to a hypothetical resting order. Deliberately has no `filled` field."""
    level: float
    side: str
    placed_at: float                       # epoch seconds
    horizon_s: float
    touched: bool = False                  # the quoted book reached the level
    time_to_touch_s: float | None = None
    trade_at_level: bool = False           # a trade printed at/through the level on our side of the book
    time_to_trade_s: float | None = None
    volume_at_or_through: float = 0.0
    n_trades_at_or_through: int = 0
    price_after: dict = field(default_factory=dict)   # markout horizon -> mid
    close_mid: float | None = None
    settled_yes: float | None = None
    notes: str = ""

    @property
    def fill_upper_bound(self) -> bool:
        """The most permissive honest statement: a trade occurred that could have included us."""
        return self.trade_at_level


def scan_trades_for_level(trades, level, side, t0, t_end):
    """Trades after t0 that would have executed against a resting order at `level`.

    `trades` is an iterable of (epoch_seconds, yes_price, size, taker_book_side) sorted by time.
    For a resting YES buy (side='yes'), the taker must be hitting the bid at a YES price <= level.
    For a resting NO buy (side='no'), the taker must be lifting the ask at a YES price >= 1 - level.
    """
    hits, vol, first = 0, 0.0, None
    for ts, yes_price, size, taker_book_side in trades:
        if ts <= t0 or ts > t_end:
            continue
        if side == "yes":
            reachable = taker_book_side == "bid" and yes_price <= level + 1e-9
        else:
            reachable = taker_book_side == "ask" and yes_price >= (1.0 - level) - 1e-9
        if reachable:
            hits += 1
            vol += size
            if first is None:
                first = ts
    return hits, vol, first


def scan_quotes_for_touch(quote_path, level, side, t0, t_end):
    """First time the quoted book reached the level. `quote_path` is (ts, yes_bid, yes_ask) sorted."""
    for ts, yb, ya in quote_path:
        if ts <= t0 or ts > t_end:
            continue
        if side == "yes" and yb is not None and yb <= level + 1e-9:
            return ts
        if side == "no" and ya is not None and (1.0 - ya) <= level + 1e-9:
            return ts
    return None


def markout(quote_path, t_fill, offsets_s):
    """Midpoint at t_fill + offset for each offset, using the last quote at or before that instant."""
    out = {}
    for off in offsets_s:
        target = t_fill + off
        best = None
        for ts, yb, ya in quote_path:
            if ts <= target and yb is not None and ya is not None:
                best = (yb + ya) / 2.0
            elif ts > target:
                break
        out[off] = best
    return out
