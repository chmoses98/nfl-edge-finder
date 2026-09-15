"""What the imported-wager ledger says about money. NOT about the model.

`imported_wagers` holds wagers the owner PLACED and this system never
RECOMMENDED. That is the defining property of the kind -- every
recommendation-provenance field is refused outright -- and it is exactly why
`tests/test_imported_wager_accounting.py` forbids the scorecard, the evaluator
and the risk ledger from reading it.

WHY A SUMMARY OF THESE WAGERS NEEDS ITS OWN WARNING
---------------------------------------------------
A won-lost record computed here is indistinguishable, at a glance, from the
number the scorecard produces for the model. The difference is that the model
had no part in any of these bets -- and a difference that exists only in a
docstring is a difference that gets lost the first time somebody pastes the
output into a weekly summary.

So :data:`NOT_MODEL_EVIDENCE` is carried on the summary as a FIELD and printed
as the first line of the report, before any number. A reader who sees only the
output still sees it.

THIS MODULE MEASURES NOTHING ABOUT THE MODEL
--------------------------------------------
It counts wagers and adds up money that already moved. It does not grade, rank,
size or price anything, and it reads no recommendation, evaluation or execution.
"""

from __future__ import annotations

from dataclasses import dataclass, field

#: Stated as DATA, not as a comment. See the module docstring.
NOT_MODEL_EVIDENCE = (
    "ACCOUNTING ONLY. Every wager here was placed by the owner and recommended "
    "by nothing in this repository. This record is evidence about a bankroll "
    "and is not evidence about the NFL model or its scorecard."
)

SETTLED = "SETTLED"


@dataclass
class ImportedWagerSummary:
    """Counts and money, by season. No opinion of any kind."""

    season: int
    wagers: int = 0
    contracts: float = 0.0
    staked: float = 0.0
    fees_paid: float = 0.0

    #: A fee the exchange did not state is a different fact from one it did,
    #: and the schema already refuses a realised P&L built on the first.
    fees_estimated_on: int = 0

    settled: int = 0
    unsettled: int = 0
    won: int = 0
    lost: int = 0
    other_result: int = 0

    realized_profit_loss: float = 0.0
    profit_loss_established: int = 0
    profit_loss_unestablished: int = 0

    by_week: dict = field(default_factory=dict)
    markets: dict = field(default_factory=dict)

    @property
    def not_model_evidence(self) -> str:
        return NOT_MODEL_EVIDENCE

    @property
    def profit_loss_is_complete(self) -> bool:
        """True only when every wager's P&L is established.

        A total assembled from some of the wagers is not the season's, and
        printing it beside the wager count invites reading it as one.
        """
        return self.wagers > 0 and self.profit_loss_unestablished == 0


def summarize(records: list, season: int, settlements: list = ()) -> ImportedWagerSummary:
    """One season of imported wagers, added up. Records are raw dicts.

    SETTLEMENT IS A SEPARATE RECORD, JOINED HERE ON ``source_bet_key``.
    `imported_wagers` is immutable, so a settlement is recorded beside a wager
    rather than edited into it. A wager with no settlement record is unsettled
    -- that absence IS the record, which is why no PENDING record is written.

    A wager carrying its own settlement fields is honoured as a fallback. The
    router never sends one, but the fields exist on the record, and silently
    ignoring a populated field is the same class of defect as silently dropping
    one.
    """
    summary = ImportedWagerSummary(season=season)
    by_key = {
        s.get("source_bet_key"): s for s in settlements
        if isinstance(s, dict) and s.get("source_bet_key")
    }

    for record in records:
        settlement = by_key.get(record.get("source_bet_key")) or record
        summary.wagers += 1
        summary.contracts += _number(record.get("contracts"))
        summary.staked += _number(record.get("stake"))
        summary.fees_paid += _number(record.get("fees_paid"))
        if record.get("fees_are_estimated"):
            summary.fees_estimated_on += 1

        week = record.get("week")
        summary.by_week[week] = summary.by_week.get(week, 0) + 1

        key = (record.get("market_ticker"), record.get("side"))
        summary.markets[key] = summary.markets.get(key, 0) + 1

        if settlement.get("settlement_status") == SETTLED:
            summary.settled += 1
            result = settlement.get("result")
            if result == "WON":
                summary.won += 1
            elif result == "LOST":
                summary.lost += 1
            else:
                summary.other_result += 1
        else:
            summary.unsettled += 1

        profit_loss = settlement.get("net_profit_loss")
        if isinstance(profit_loss, (int, float)) and not isinstance(profit_loss, bool):
            summary.realized_profit_loss += float(profit_loss)
            summary.profit_loss_established += 1
        else:
            summary.profit_loss_unestablished += 1

    return summary


def render(summary: ImportedWagerSummary) -> str:
    """The summary as text. The warning is the first thing printed."""
    lines = [
        NOT_MODEL_EVIDENCE,
        "",
        f"NFL imported wagers -- season {summary.season}",
        f"  wagers recorded: {summary.wagers}",
        f"  contracts:       {summary.contracts:g}",
        f"  staked:          {summary.staked:.2f}",
        f"  fees paid:       {summary.fees_paid:.2f}",
    ]
    if summary.fees_estimated_on:
        lines.append(
            f"  fees ESTIMATED on {summary.fees_estimated_on} wager(s) -- a modelled "
            "fee is not an exchange-stated one"
        )
    lines.append(f"  distinct market/side pairs: {len(summary.markets)}")

    if summary.by_week:
        lines.append("  by week:")
        for week in sorted(summary.by_week, key=lambda value: (value is None, value)):
            lines.append(f"    week {week}: {summary.by_week[week]}")

    lines += [
        "",
        "  settlement:",
        f"    settled:   {summary.settled}",
        f"    unsettled: {summary.unsettled}",
    ]
    if summary.settled:
        lines += [
            f"    won:  {summary.won}",
            f"    lost: {summary.lost}",
            f"    other result: {summary.other_result}",
        ]

    lines += ["", "  realized profit and loss:"]
    if summary.profit_loss_is_complete:
        lines.append(f"    {summary.realized_profit_loss:+.2f} (every wager established)")
    else:
        lines += [
            f"    UNESTABLISHED for {summary.profit_loss_unestablished} of "
            f"{summary.wagers} wagers",
            "    no season total is stated: a total assembled from some of the "
            "wagers is not the season's profit and loss",
        ]
    return "\n".join(lines)


def _number(value) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return 0.0
    return float(value)
