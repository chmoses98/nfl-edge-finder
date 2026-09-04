"""Kalshi NFL settlement semantics: what a contract actually pays, as distinct from the football event.

Everything here is grounded in the contracts' own `rules_secondary` text (captured 2026-09-04) and verified
against 61,068 settled archived 2025 markets. See docs/KALSHI_SETTLEMENT.md for the evidence.

THE CENTRAL DISTINCTION
-----------------------
`event_probability`  P(the football event happens), conditional on the player being on the field.
`contract_value`     E[payout of one YES contract], which mixes in participation branches and special
                     settlement rules. These are NOT the same number and must never be conflated.

Player props (KXNFLPASSYDS, KXNFLRECYDS, KXNFLRSHYDS, KXNFLREC, KXNFLTD, KXNFLANYTD, KXNFLPASSTDS, ...):
    "If <player> is active but never takes a snap, the market settles to the (last) fair market price
     before game start. Once <player> takes at least one snap, even if nullified by penalty, the market
     settles based on <stat> recorded."
  Three branches, and the archive shows all of them:
    played (>=1 snap)     -> settles 1 if stat >= K else 0            (the overwhelming majority)
    active, never a snap  -> settles at the pregame fair market price  (result="scalar", 348 player
                             markets in the 2025 archive, median $0.10, range $0.01-$0.95)
    INACTIVE              -> settles NO ($0.00).  The fair-price clause is explicitly conditioned on the
                             player being ACTIVE, and zero-snap players who were not active settled at
                             $0.00 in the archive.  This is the branch that actually costs a YES holder.
  So availability is not a nuisance parameter: it scales the YES contract's value directly.

Game winner (KXNFLGAME): tie -> BOTH teams settle at $0.50 (8 such markets = 4 tied games in the archive).
    Postponed but starting within 48h of the scheduled time -> stays open, settles on the official result.
    Not started within 48h -> settles at a fair price.
Period winner (KXNFL1H/1Q/...): a tied period settles every team strike NO and the Tie strike YES.
First TD scorer: no touchdowns in the game -> "No Touchdown" YES, every player strike NO; the same
    active/no-snap fair-price clause applies to the player strikes (132 scalar settlements observed).
Spread/total ladders: full game includes overtime; 1H markets count first-half points only; 2H markets
    explicitly EXCLUDE overtime.  Total-TD markets count overtime touchdowns.
"""
from __future__ import annotations

from dataclasses import dataclass

# families whose settlement rules are understood well enough to price a contract
SUPPORTED_SETTLEMENT = {
    "PLAYER_STAT", "GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "WIN_MARGIN_BUCKET",
    "PERIOD_WINNER", "TOTAL_TD", "BOTH_TEAMS_SCORE_N", "FIRST_TD_SCORER", "FIRST_TD_TEAM",
}
# families deliberately NOT priced: rules understood but the football model is not ready, or the rule
# itself is not pinned down from free evidence.
UNSUPPORTED_SETTLEMENT_REASON = {
    "RACE_TO_N": "requires in-game scoring-order simulation; not validated",
    "HALF_FULL_RESULT": "joint half/full result; needs a period-correlated simulator",
    "PERIOD_TD": "period touchdown counts not modelled",
    "GAME_EVENT": "heterogeneous one-off events; rules vary per market",
    "GAME_STAT": "game-level leader/extreme statistics not modelled",
    "TEAM_STAT": "team stat ladders not modelled",
    "PLAYER_H2H": "head-to-head player comparison not modelled",
    "NEXT_TD_SCORER": "in-game sequential market",
    "PARLAY": "multivariate contract; correlation model not validated",
    "COMBO": "multivariate contract; correlation model not validated",
}
# overtime treatment per (family, period)
OVERTIME_INCLUDED = {("SPREAD", "FULL"): True, ("TOTAL", "FULL"): True, ("TEAM_TOTAL", "FULL"): True,
                     ("TOTAL_TD", "FULL"): True, ("WIN_MARGIN_BUCKET", "FULL"): True,
                     ("SPREAD", "1H"): False, ("TOTAL", "1H"): False, ("SPREAD", "2H"): False,
                     ("TOTAL", "2H"): False}

PLAYER_STAT_PARTICIPATION = "one_snap"   # >=1 snap, even if nullified by penalty


@dataclass
class ContractValue:
    """Result of turning a football-event probability into an expected contract payout."""
    event_probability: float          # P(stat >= K | player takes a snap)  -- the football question
    contract_value: float             # E[payout] of one YES contract in dollars
    p_plays: float                    # P(takes >= 1 snap)
    p_active_no_snap: float           # P(dressed but never on the field)
    p_inactive: float                 # P(not active)  -> YES pays 0
    fair_price_used: float | None     # price assumed for the no-snap branch
    notes: str = ""

    def to_dict(self):
        return self.__dict__.copy()


def player_prop_contract_value(event_probability: float, p_plays: float, p_active_no_snap: float,
                               fair_price: float | None) -> ContractValue:
    """Expected YES payout for a player prop under Kalshi's three-branch settlement.

    fair_price is Kalshi's "fair market price before game start"; the best available proxy at pricing time
    is the contemporaneous market mid.  When it is unknown we fall back to the event probability, which is
    the neutral assumption (that branch is then EV-neutral rather than silently free or silently worthless).
    """
    p_plays = min(max(p_plays, 0.0), 1.0)
    p_active_no_snap = min(max(p_active_no_snap, 0.0), 1.0 - p_plays)
    p_inactive = max(0.0, 1.0 - p_plays - p_active_no_snap)
    fp = fair_price if fair_price is not None else event_probability
    value = p_plays * event_probability + p_active_no_snap * fp
    return ContractValue(event_probability=event_probability, contract_value=value, p_plays=p_plays,
                         p_active_no_snap=p_active_no_snap, p_inactive=p_inactive, fair_price_used=fp,
                         notes="inactive settles NO; active-but-no-snap settles at pregame fair price")


def game_winner_contract_value(p_win: float, p_tie: float) -> ContractValue:
    """A tie pays $0.50 to BOTH sides, so the contract is worth p_win + 0.5 * p_tie."""
    return ContractValue(event_probability=p_win, contract_value=p_win + 0.5 * p_tie, p_plays=1.0,
                         p_active_no_snap=0.0, p_inactive=0.0, fair_price_used=None,
                         notes="tie settles $0.50 per side")


def binary_contract_value(p: float) -> ContractValue:
    """Families with no special branch: the contract is worth the event probability."""
    return ContractValue(event_probability=p, contract_value=p, p_plays=1.0, p_active_no_snap=0.0,
                         p_inactive=0.0, fair_price_used=None, notes="plain binary settlement")


def settlement_supported(family: str) -> tuple[bool, str | None]:
    if family in SUPPORTED_SETTLEMENT:
        return True, None
    return False, UNSUPPORTED_SETTLEMENT_REASON.get(family, f"settlement semantics not established for {family}")
