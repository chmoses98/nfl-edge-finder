"""The settlement of an imported wager. ACCOUNTING, not model evidence.

WHY A SEPARATE KIND RATHER THAN FIELDS ON THE WAGER
----------------------------------------------------
`imported_wagers` is immutable, and the append-only guard covers it, because a
record of money that already moved may not be rewritten. That reasoning does not
stop applying because the new information is welcome: a settlement is a LATER
and SEPARATE observation than the wager it settles, so it is recorded beside it.

WHY THERE IS NO PENDING RECORD
-------------------------------
A market settles once. So a settlement is written once, when it is established,
and a wager with no settlement record is simply unsettled -- which is exactly
what the absence already means to every reader. A PENDING record would have to
be superseded when the market settled, in a ledger whose whole guarantee is that
records are not.

A SETTLED RECORD WITH NO MONEY ON IT IS STILL WORTH WRITING
------------------------------------------------------------
"The market settled and the return could not be established" is a durable fact
with a durable cause -- the exchange published no settlement price, or a fee was
charged on a position covering more than one of the owner's orders. So the
record is written with the figure absent and the REASON recorded, never with a
zero standing in for it.

NOTHING THAT MEASURES MODEL PERFORMANCE MAY READ THIS
------------------------------------------------------
For exactly the reason nothing may read `imported_wagers`: the model had no part
in these bets, so their outcomes are not its record.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field

SCHEMA_VERSION = "nfl_wager_settlement.v1"

SETTLED = "SETTLED"

WON = "WON"
LOST = "LOST"

#: The same fields an imported wager refuses. A settlement proves what the
#: exchange paid; it proves nothing about what recommended the bet.
FORBIDDEN_PROVENANCE_FIELDS = (
    "recommendation_id",
    "evaluation_id",
    "model_fair_probability",
    "model_supported",
    "edge",
    "expected_value",
)


@dataclass
class WagerSettlement:
    """One imported wager's settlement, as far as the exchange establishes it."""

    settlement_id: str
    schema_version: str
    #: The wager this settles, by the venue's own order identity -- so neither
    #: record has to name the other's id to be joined.
    source_bet_key: str
    #: Required for the same reason the wager carries them: the reports are read
    #: by week, and a record filed outside one is invisible to all of them.
    season: int
    week: int
    market_ticker: str
    side: str

    settlement_status: str
    settled_at: str

    #: Absent when the exchange's own outcome is not one this system maps -- a
    #: void, a scalar settlement. Forcing those into a binary would misstate them.
    result: str | None = None

    gross_return: float | None = None
    net_profit_loss: float | None = None
    #: Present exactly when a figure above is absent.
    refusals: list = field(default_factory=list)

    venue: str = "kalshi"

    #: Which router economics contract computed `net_profit_loss`. Absent on every settlement filed before
    #: 2026-09-24, which were all router-settlement-economics.v1 (fee_cost subtracted a second time -- see
    #: `settlement_amendments`). Omitted from the file when absent, so a v1 record's bytes are unchanged.
    economics_version: str | None = None

    def to_dict(self):
        out = asdict(self)
        if out.get("economics_version") is None:
            out.pop("economics_version", None)
        return out


def validate(record: dict) -> list[str]:
    """Every reason this record may not be written. Empty means it may.

    Returns all the problems rather than the first, so a batch reports what is
    wrong with it once instead of over several attempts.
    """
    problems: list[str] = []

    for name in FORBIDDEN_PROVENANCE_FIELDS:
        if name in record:
            problems.append(
                f"{name!r} would assert model provenance this settlement does not have"
            )

    for name in ("settlement_id", "source_bet_key", "market_ticker", "side",
                 "settlement_status", "settled_at"):
        value = record.get(name)
        if not isinstance(value, str) or not value.strip():
            problems.append(f"{name} is required and must be a non-empty string")

    if record.get("settlement_status") != SETTLED:
        problems.append(
            f"settlement_status must be {SETTLED!r}; an unsettled wager is recorded "
            "by having no settlement record at all, not by a record saying so"
        )

    if record.get("side") not in ("YES", "NO"):
        problems.append(f"side must be YES or NO; got {record.get('side')!r}")

    if record.get("result") not in (None, WON, LOST):
        problems.append(
            f"result must be {WON!r}, {LOST!r} or absent; got {record.get('result')!r}"
        )

    for name in ("gross_return", "net_profit_loss"):
        value = record.get(name)
        if value is None:
            continue
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            problems.append(f"{name} must be a number when it is stated at all")

    version = record.get("economics_version")
    if version is not None and version not in ("router-settlement-economics.v1",
                                               "router-settlement-economics.v2"):
        problems.append(f"economics_version {version!r} is not a known settlement economics contract")

    refusals = record.get("refusals")
    if not isinstance(refusals, list):
        problems.append("refusals must be a list, even when empty")
    else:
        missing = [n for n in ("gross_return", "net_profit_loss") if record.get(n) is None]
        if missing and not refusals:
            problems.append(
                f"{', '.join(missing)} absent with no refusal recorded; a null with "
                "no explanation is how an unknown becomes a zero"
            )
        if not missing and refusals:
            problems.append(
                "every figure is established, so a refusal has nothing to refuse"
            )

    return problems
