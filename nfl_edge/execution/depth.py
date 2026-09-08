"""Full-position executability: what the APPROVED STAKE actually costs, not what one contract costs.

The top of book proves a price exists. It does not prove your position exists at that price.

    approved stake   $50
    best ask         56c for 1 contract
    next liquidity   59c, then 60c

Calling that a "56c position" is false, and it is false in the direction that flatters the trade: the
displayed price is the cheapest contract you will buy, and every other one costs more. A desk that sizes
against top-of-book is systematically paying more than it recorded, on exactly the thin books where it
thought it had found something.

So for every RECOMMENDED position this module walks the observed book and returns the economics of the WHOLE
approved stake -- top ask, size at top ask, contracts required, full-position VWAP, worst consumed price,
dollar slippage against the displayed top, and whether the book can fill it at all.

BOOK SEMANTICS
--------------
Kalshi's orderbook returns RESTING BIDS on each side, ascending by price, so the best bid is LAST:

    yes_dollars   [[price, size], ...]   YES bids   -> best YES bid  = last
    no_dollars    [[price, size], ...]   NO  bids   -> best NO  bid  = last

There are no ask ladders, because an ask on one side IS a bid on the other. To BUY YES you lift the NO bids,
and a NO bid at q is a YES ask at (1 - q). Walking the NO ladder from its highest price downward therefore
walks the YES ask ladder from its lowest price upward, which is the direction a buyer consumes.

This orientation is not assumed. It was verified against 126 tickers captured in one run by reconstructing
`yes_bid` and `yes_ask` from the book and comparing with the separately-captured quote row; it reproduces
both. The residual mismatches are all timing -- books are fetched ~13 seconds after quotes in the same run,
in every one of the 126 cases -- which is also why the book's OWN `observed_at` is what this module uses for
freshness rather than the quote's or the run's.

FAIL CLOSED
-----------
No book, a book from after the decision, a book too old, or a book too thin to fill the stake all produce a
non-executable result. None of them fall back to top-of-book pricing, because "we could not see the depth"
and "the depth is there" are the two cases this module exists to keep apart.
"""
from __future__ import annotations

import glob
import json
import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

# A book is a much heavier object than a quote and is captured only for FULL_MICROSTRUCTURE series inside
# 72h of kickoff, so its cadence is the capture cadence but its coverage is narrower. The window is the same
# 15 minutes the quote gate uses: the same market, the same staleness question.
DEFAULT_MAX_BOOK_AGE_MIN = 15.0

EXECUTABLE = "EXECUTABLE"          # the full approved stake fills from observed liquidity
INSUFFICIENT_DEPTH = "INSUFFICIENT_DEPTH"   # the book is real but cannot fill the stake
NO_BOOK = "NO_BOOK"                # no order book captured at or before the decision
STALE_BOOK = "STALE_BOOK"          # a book exists but predates the freshness window


@dataclass
class DepthResult:
    """The full-position execution picture, with every price it took to get there."""
    ticker: str
    side: str
    state: str
    requested_stake: float
    top_ask: float | None = None                 # the displayed price
    size_at_top_ask: float | None = None
    contracts_required: float | None = None      # to fill the stake AT THE VWAP, not at the top
    contracts_available: float | None = None     # across every level we can see
    vwap: float | None = None                    # full-position average price actually paid
    worst_price: float | None = None             # the last, most expensive level consumed
    levels_consumed: list = field(default_factory=list)   # [(price, contracts)]
    slippage_dollars: float | None = None        # cost at VWAP minus cost at the displayed top ask
    slippage_probability: float | None = None    # vwap - top_ask, in price units
    fillable_stake: float | None = None          # what the book COULD absorb, when it cannot take it all
    book_observed_at: str | None = None
    book_age_minutes: float | None = None
    as_of: str | None = None
    capture_run_id: str | None = None
    reason: str | None = None

    @property
    def is_executable(self) -> bool:
        return self.state == EXECUTABLE and self.vwap is not None

    def to_dict(self) -> dict:
        return dict(self.__dict__)


def _iso(t):
    if not t:
        return None
    if isinstance(t, datetime):
        return t if t.tzinfo else t.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(str(t).replace("Z", "+00:00"))
    except (ValueError, TypeError):
        return None
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def _levels(raw) -> list:
    out = []
    for entry in raw or []:
        try:
            price, size = float(entry[0]), float(entry[1])
        except (TypeError, ValueError, IndexError):
            continue
        if 0.0 < price < 1.0 and size > 0:
            out.append((price, size))
    return out


def ask_ladder(orderbook: dict, side: str) -> list:
    """The ASK ladder on our side, cheapest first -- derived from the opposite side's bids.

    Buying YES lifts NO bids: a NO bid at q is a YES ask at (1 - q). The highest NO bid is therefore the
    cheapest YES ask, so descending the NO ladder ascends the YES ask ladder.
    """
    key = "no_dollars" if (side or "YES").upper() == "YES" else "yes_dollars"
    opposite = _levels((orderbook or {}).get(key))
    opposite.sort(key=lambda x: -x[0])            # best (highest) bid first
    return [(round(1.0 - price, 6), size) for price, size in opposite]


def walk_book(ladder: list, stake_dollars: float) -> dict:
    """Consume the ask ladder until `stake_dollars` is spent. Returns the full-position economics.

    Spend, not contract count, is the budget: the approved stake is a dollar amount, and how many contracts
    it buys is an OUTPUT of the walk because later contracts cost more than earlier ones. Sizing by
    `stake / top_ask` first and then walking would ask for too many contracts and overstate the shortfall.
    """
    remaining = float(stake_dollars)
    consumed, contracts, spent = [], 0.0, 0.0
    for price, size in ladder:
        if remaining <= 1e-9:
            break
        level_cost = price * size
        if level_cost <= remaining + 1e-9:
            take = size
        else:
            take = remaining / price
        if take <= 0:
            continue
        consumed.append((price, round(take, 6)))
        contracts += take
        spend = take * price
        spent += spend
        remaining -= spend

    available_contracts = sum(size for _p, size in ladder)
    available_stake = sum(p * s for p, s in ladder)
    filled = remaining <= 1e-6
    return {
        "filled": filled,
        "levels_consumed": consumed,
        "contracts": round(contracts, 6),
        "spent": round(spent, 6),
        "vwap": round(spent / contracts, 6) if contracts > 0 else None,
        "worst_price": consumed[-1][0] if consumed else None,
        "contracts_available": round(available_contracts, 6),
        "fillable_stake": round(available_stake, 6),
    }


class BookIndex:
    """Read-only view over the captured order books, newest-first with a decision-time cutoff."""

    def __init__(self, md_root: str, max_runs: int = 200):
        self.md_root = md_root
        self.max_runs = max_runs

    def _root(self) -> str:
        return os.path.join(self.md_root, "data", "kalshi", "capture")

    def latest_book(self, ticker: str, as_of: datetime) -> dict | None:
        """The newest book row for a ticker observed AT OR BEFORE the decision.

        Its own `observed_at` is what decides both cutoff and age: books are fetched after quotes within a
        run, so a run-level timestamp would claim the book existed before it did.
        """
        files = sorted(glob.glob(os.path.join(self._root(), "*", "*.books.jsonl")))
        best = None
        for path in reversed(files[-self.max_runs:]):
            try:
                with open(path) as f:
                    for line in f:
                        if ticker not in line:
                            continue
                        try:
                            r = json.loads(line)
                        except ValueError:
                            continue
                        if r.get("ticker") != ticker or not r.get("orderbook_fp"):
                            continue
                        ts = _iso(r.get("observed_at"))
                        if ts is None or ts > as_of:
                            continue
                        if best is None or ts > _iso(best["observed_at"]):
                            best = r
            except OSError:
                continue
            if best is not None:
                return best
        return best


def resolve_full_position(index: "BookIndex", ticker: str, side: str, stake_dollars: float, *,
                          as_of: datetime, bet_up_to: float | None = None,
                          max_age_minutes: float = DEFAULT_MAX_BOOK_AGE_MIN) -> DepthResult:
    """Whether the approved stake is executable, and at what average price.

    A result is EXECUTABLE only when a book observed at or before the decision, inside the freshness window,
    holds enough liquidity to absorb the whole stake. Everything else names which of those failed.
    """
    side = (side or "YES").upper()
    res = DepthResult(ticker=ticker, side=side, state=NO_BOOK, requested_stake=float(stake_dollars),
                      as_of=as_of.isoformat())

    row = index.latest_book(ticker, as_of)
    if row is None:
        res.reason = (f"no order book for {ticker} captured at or before {as_of.isoformat()}. Books are "
                      "captured for FULL_MICROSTRUCTURE series inside 72h of kickoff; outside that the "
                      "depth behind the top of book is simply not observable, and top-of-book is not a "
                      "substitute for it.")
        return res

    res.book_observed_at = row.get("observed_at")
    res.capture_run_id = row.get("run_id")
    observed = _iso(res.book_observed_at)
    res.book_age_minutes = round((as_of - observed).total_seconds() / 60.0, 2)

    ladder = ask_ladder(row.get("orderbook_fp") or {}, side)
    if not ladder:
        res.state = NO_BOOK
        res.reason = f"the captured book for {ticker} holds no {side} ask liquidity at all"
        return res

    res.top_ask, res.size_at_top_ask = ladder[0][0], ladder[0][1]

    if res.book_age_minutes > max_age_minutes:
        res.state = STALE_BOOK
        res.reason = (f"the newest pre-decision book for {ticker} is {res.book_age_minutes:.1f} min older "
                      f"than the decision, beyond the {max_age_minutes:.0f} min window; its depth is not "
                      "evidence of what was available when the call was made")
        return res

    walk = walk_book(ladder, stake_dollars)
    res.contracts_available = walk["contracts_available"]
    res.fillable_stake = walk["fillable_stake"]
    res.levels_consumed = walk["levels_consumed"]
    res.contracts_required = walk["contracts"]
    res.vwap = walk["vwap"]
    res.worst_price = walk["worst_price"]

    if res.vwap is not None and res.top_ask is not None:
        res.slippage_probability = round(res.vwap - res.top_ask, 6)
        # What the walk actually costs, against what the displayed top price pretends it costs for the same
        # number of contracts.
        res.slippage_dollars = round(res.contracts_required * res.slippage_probability, 6)

    if not walk["filled"]:
        res.state = INSUFFICIENT_DEPTH
        res.reason = (f"the observable book can absorb only ${walk['fillable_stake']:.2f} of the "
                      f"${float(stake_dollars):.2f} approved stake "
                      f"({walk['contracts_available']:.2f} contracts across {len(ladder)} level(s))")
        return res

    if bet_up_to is not None and res.worst_price is not None and res.worst_price > float(bet_up_to) + 1e-9:
        res.state = INSUFFICIENT_DEPTH
        res.reason = (f"filling the ${float(stake_dollars):.2f} stake walks the book up to "
                      f"{res.worst_price}, above bet_up_to_probability {bet_up_to}. The position is only "
                      "available at prices this record does not authorise.")
        return res

    res.state = EXECUTABLE
    return res
