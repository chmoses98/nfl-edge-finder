"""Accounting for wagers that were EXECUTED but never RECOMMENDED.

WHY THIS IS NOT AN Execution
----------------------------
``Execution`` requires a ``recommendation_id``. That is correct for what it
models: a fill against a position this system recommended, whose performance
belongs in the scorecard.

A wager imported from an exchange receipt has no such parent. A Kalshi
execution proves the owner placed a bet; it proves nothing about what
recommended it. Synthesising a recommendation id to satisfy the field would
manufacture exactly the provenance the record is supposed to lack -- and would
then be indistinguishable, downstream, from a bet this system actually called.

WHY A NEW KIND RATHER THAN A FLAG ON THE OLD ONE
------------------------------------------------
``scripts/handicap/scorecard.py`` and ``nfl_edge/handicap/risk.py`` both read
``executions``. A flag would put these rows in front of both and rely on every
present and future reader to check it. A separate kind cannot be read by
accident.

This follows the precedent already set by ``import_receipts``, which the store
documents as "transport provenance, not a decision record: nothing in the
scorecard reads it and a receipt never stands in for a recommendation". An
imported wager is the same shape of thing: real, worth recording, and not
evidence about the model.

ACCOUNTING AUTHORITY IS NOT MODEL AUTHORITY
-------------------------------------------
Recording these wagers says the owner's bankroll moved. It does not say the NFL
model was consulted, was right, or should be trusted. Nothing here may be read
as model performance, and a test asserts the scorecard does not read it.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, field

SCHEMA_VERSION = "imported_wager.v1"

#: How the wager reached this ledger. One value today, named rather than
#: implied so a second source cannot arrive without saying so.
ENTRY_METHOD_IMPORTED_RECEIPT = "IMPORTED_RECEIPT"

#: Fields a recommendation-backed record carries and this one must NEVER grow.
#: Asserted by a test rather than left to review: the whole point of this kind
#: is that it cannot claim provenance it does not have.
FORBIDDEN_PROVENANCE_FIELDS = (
    "recommendation_id",
    "evaluation_id",
    "model_fair_probability",
    "model_supported",
    "edge",
    "expected_value",
)


@dataclass
class ImportedWager:
    """One wager, reconstructed from exchange fills. One ORDER, not one fill.

    ``Execution`` models one fill because a recommendation is routinely filled
    in pieces and each piece is its own immutable record. This models one
    ORDER, because that is the unit the owner actually decided on: the pieces
    are an artefact of how the venue matched it, and summing them is not an
    approximation but the actual wager.

    ``actual_price`` is therefore a genuine quantity-weighted average over the
    order's own fills, and is labelled as such. It is not a stored guess at a
    price nobody paid.
    """

    imported_wager_id: str
    schema_version: str
    #: Stable, venue-derived, and opaque. Re-importing the same order produces
    #: the same key, which is what makes a repeated backfill a no-op.
    source_bet_key: str
    #: The batch that brought it in. Part of the identity, so a re-run of the
    #: same batch lands on the same record rather than a second one.
    import_batch_id: str
    entry_method: str

    season: int
    week: int
    #: The contest's own date, established from event evidence. Never derived
    #: from a market close timestamp, which is a UTC instant and puts a Sunday
    #: night game on Monday.
    game_date: str
    market_ticker: str
    side: str

    executed_at: str
    contracts: float
    #: Quantity-weighted average across this order's fills, in dollars.
    actual_price: float
    stake: float
    fees_paid: float | None = None
    fees_are_estimated: bool = False
    fee_state: str | None = None

    #: Settlement, when the venue or the season results establish one. Absent
    #: means not yet known -- never zero, which would read as "settled at nil".
    settlement_status: str | None = None
    result: str | None = None
    gross_return: float | None = None
    net_profit_loss: float | None = None

    venue: str = "kalshi"
    notes: str = ""
    test_only: bool = False
    #: Free-form links to the event this wager was on, when established.
    event_refs: dict = field(default_factory=dict)

    def to_dict(self):
        return asdict(self)


def validate(record: dict) -> list[str]:
    """Reasons this record may not be written. Empty means it may.

    Returns every problem rather than the first, so a batch reports what is
    wrong with it once instead of over several attempts.
    """
    problems: list[str] = []

    for name in FORBIDDEN_PROVENANCE_FIELDS:
        if name in record:
            problems.append(
                f"{name!r} is recommendation provenance and an imported wager has none"
            )

    for name in ("imported_wager_id", "source_bet_key", "import_batch_id",
                 "market_ticker", "side", "game_date", "executed_at"):
        value = record.get(name)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{name} is required and must be a non-empty string")

    if record.get("entry_method") != ENTRY_METHOD_IMPORTED_RECEIPT:
        problems.append(
            f"entry_method must be {ENTRY_METHOD_IMPORTED_RECEIPT!r}; "
            f"got {record.get('entry_method')!r}"
        )

    if record.get("side") not in ("YES", "NO"):
        problems.append(f"side must be YES or NO; got {record.get('side')!r}")

    for name in ("contracts", "actual_price", "stake"):
        value = record.get(name)
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            problems.append(f"{name} is required and must be a number")
        elif value < 0:
            problems.append(f"{name} may not be negative")

    # A fee that was MODELLED is a fine input to an estimate and an
    # unacceptable input to a realised-P/L claim. The schema already
    # distinguishes them; this refuses the combination that hides it.
    if record.get("fees_are_estimated") and record.get("net_profit_loss") is not None:
        problems.append(
            "net_profit_loss may not be stated from estimated fees; "
            "that is a modelled number wearing a realised one's clothes"
        )

    return problems
