"""Shared constants and tiny helpers. Policy numbers are OWNER-ADJUSTABLE DEFAULTS, named and documented here only."""
from __future__ import annotations

from datetime import datetime, timezone

#: 1U in dollars (docs/NFL_OPERATING_POLICY.md section 1: fixed, not a bankroll fraction).
UNIT_DOLLARS = 75.0
#: Correlated-thesis budget (policy: strict 5U per thesis). Used by exposure FLAGS only; never a cap here.
GAME_EXPOSURE_FLAG_UNITS = 5.0
#: Daily aggregate flag. Owner-requested review threshold (issue #231), a FLAG not a cap: the operating policy
#: deliberately has no slate cap, so nothing here refuses or resizes a bet.
DAILY_EXPOSURE_FLAG_UNITS = 15.0
#: Existing quote-age policy (gates.py DEFAULT_MAX_QUOTE_AGE_MIN); duplicated by value, asserted equal in tests.
MAX_QUOTE_AGE_MIN = 15.0
#: Projection / injury freshness defaults for GAME-LEVEL markets (owner-adjustable). Player markets keep S.MAX_AVAILABILITY_STALE_MIN.
MAX_PROJECTION_AGE_MIN = 180.0
MAX_INJURY_AGE_MIN = 180.0
#: A bet must clear break-even by at least this much on the CONSERVATIVE fair probability to have a bet-up-to.
MIN_CONSERVATIVE_MARGIN = 0.0


def parse_ts(value) -> datetime | None:
    """ISO-8601 (Z or offset) or datetime to an aware UTC datetime; None for missing/garbled. Never guesses a zone."""
    if value is None or value == "":
        return None
    if isinstance(value, datetime):
        dt = value
    else:
        try:
            dt = datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        except ValueError:
            return None
    if dt.tzinfo is None:
        return None            # a naive timestamp has no provable instant; refuse rather than assume UTC
    return dt.astimezone(timezone.utc)


def num(x):
    if isinstance(x, bool) or x is None:
        return None
    try:
        v = float(x)
    except (TypeError, ValueError):
        return None
    return v if v == v and abs(v) != float("inf") else None
