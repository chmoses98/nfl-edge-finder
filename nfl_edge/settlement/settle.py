"""Turn a proven result into the YES payout of one Kalshi contract -- or refuse.

Two things are settled here and they are not the same:

    the football fact       Seattle scored 24, Stevenson rushed for 47 yards
    the contract payout     what one YES contract of THIS ticker pays, in dollars

The second needs the first PLUS the exact contract semantics, and the semantics come from the ledger row the
prediction was written with (`family`, `period`, `stat`, `threshold`, `operator`, `floor_strike`, `team`,
`player_id`) cross-checked against the rules text recorded in docs/KALSHI_SETTLEMENT.md and
nfl_edge/settlement/semantics.py.

REFUSAL IS A RESULT
-------------------
Every path that cannot prove a payout returns a REFUSED_* status with the reason, and never a number. A
refusal is written into the immutable evaluation record exactly like a settlement, because "we could not
prove this" is the finding that tells us where the corpus has holes. What must never happen is a guessed 0 or
1: a fabricated settlement contaminates every calibration number computed from the corpus afterwards.

THE SCALAR BRANCH
-----------------
A player who is active but never takes a snap settles at a value the EXCHANGE computes. `semantics.py` uses a
contemporaneous midpoint as a pricing-time PROXY for that branch, which is the right thing to do when pricing;
recording that proxy as the payout would be inventing a settlement. So this module accepts only the exchange's
own published `settlement_value_dollars` (see `kalshi_settlement.py`) and refuses with
`REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE` when it is absent -- while still recording that the participation
branch itself was proven.

The families settled here are the families the pricer actually prices. Coverage is deliberately NOT widened
beyond that: a family with no model probability has nothing to evaluate, and a family whose settlement rule
is not pinned down from free evidence (period markets' quarter-by-quarter scores, total touchdowns, first-TD
ordering) is refused with that reason rather than approximated.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from nfl_edge.settlement.results import DOUBLE_COUNT_RISK_COLUMNS, FINAL, ResultBook, STAT_COLUMNS

SETTLED = "SETTLED"
REFUSED_UNSUPPORTED_FAMILY = "REFUSED_UNSUPPORTED_FAMILY"
REFUSED_UNSUPPORTED_PERIOD = "REFUSED_UNSUPPORTED_PERIOD"
REFUSED_UNSUPPORTED_STAT = "REFUSED_UNSUPPORTED_STAT"
REFUSED_GAME_IDENTITY = "REFUSED_GAME_IDENTITY"
REFUSED_GAME_NOT_FINAL = "REFUSED_GAME_NOT_FINAL"
REFUSED_TEAM_IDENTITY = "REFUSED_TEAM_IDENTITY"
REFUSED_PLAYER_IDENTITY = "REFUSED_PLAYER_IDENTITY"
REFUSED_AMBIGUOUS_SEMANTICS = "REFUSED_AMBIGUOUS_SEMANTICS"
REFUSED_PARTICIPATION_UNPROVEN = "REFUSED_PARTICIPATION_UNPROVEN"
REFUSED_STAT_UNAVAILABLE = "REFUSED_STAT_UNAVAILABLE"
REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE = "REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE"
REFUSED_DIRECTION = "REFUSED_DIRECTION"
REFUSED_RESULT_INCONSISTENT = "REFUSED_RESULT_INCONSISTENT"

# How a settled payout was produced. Only `binary` rows are a 0/1 realisation of the football event, so only
# they may enter a Brier score or a calibration curve.
KIND_BINARY = "binary"
KIND_TIE_SPLIT = "tie_split"                 # game winner, tied game: both sides pay $0.50
KIND_SCALAR_EXACT = "scalar_exact"           # active player, never took a snap: pays the exchange's own scalar

# Families this engine can prove from final results. Same set the pricer prices, minus the two it writes as
# UNSUPPORTED_MODEL (WIN_MARGIN_BUCKET, TOTAL_TD), which therefore carry no probability to evaluate.
SETTLEABLE_FAMILIES = {"GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "BOTH_TEAMS_SCORE_N", "PLAYER_STAT"}

# Why a family we see in the ledger is NOT settled here. Recorded verbatim on the refusal so the gap is
# visible in the corpus rather than being an absence.
UNSETTLEABLE_FAMILY_REASON = {
    "WIN_MARGIN_BUCKET": "margin-bucket bounds are not carried in the capture schema, so the winning band cannot be proven",
    "TOTAL_TD": "game touchdown count needs play-by-play with defensive/special-teams attribution rules that are not established",
    "PERIOD_WINNER": "period scores are not carried in the free schedule feed",
    "FIRST_TD_SCORER": "first-touchdown ORDER needs play-by-play sequencing that is not established here",
    "FIRST_TD_TEAM": "first-touchdown ORDER needs play-by-play sequencing that is not established here",
    "BOTH_TEAMS_SCORE": "period both-teams-score needs period scores, which the free schedule feed omits",
    "PERIOD_TD": "period touchdown counts are not established",
    "RACE_TO_N": "requires in-game scoring order",
    "HALF_FULL_RESULT": "requires period results",
    "NEXT_TD_SCORER": "in-game sequential market",
    "GAME_EVENT": "heterogeneous one-off events; rules vary per market",
    "GAME_STAT": "game-level leader/extreme statistics are not established",
    "TEAM_STAT": "team stat ladders are not established",
    "PLAYER_H2H": "head-to-head comparison semantics are not established",
    "PARLAY": "multivariate contract",
    "COMBO": "multivariate contract",
}

# Player statistics whose settlement column is proven. Keys are the ledger's `stat` values.
SETTLEABLE_PLAYER_STATS = set(STAT_COLUMNS) | {"touchdowns"}

FULL_GAME = "FULL"


@dataclass
class Settlement:
    status: str
    settled_yes: float | None = None
    kind: str | None = None
    reason: str | None = None
    evidence: dict = field(default_factory=dict)

    @property
    def is_settled(self) -> bool:
        return self.status == SETTLED

    def to_dict(self):
        return {"settlement_status": self.status, "settled_yes": self.settled_yes,
                "settlement_kind": self.kind, "settlement_reason": self.reason,
                "settlement_evidence": self.evidence}


def _refuse(status, reason, evidence=None, **extra):
    """`evidence` is the proof dict (game/player), `extra` the field(s) that made this a refusal."""
    ev = dict(evidence or {})
    ev.update(extra)
    return Settlement(status=status, reason=reason, evidence=ev)


def _threshold_met(value: float, threshold: float | None, operator: str | None,
                   floor_strike: float | None) -> tuple[bool | None, dict, str | None]:
    """Apply the contract's own comparison. Returns (met, evidence, refusal_reason).

    Two shapes appear in real NFL markets and both are honoured literally:
      operator '>='  YES iff value >= threshold   ("records 350+ Passing Yards", "collectively score 25+")
      operator '>'   YES iff value >  floor_strike ("wins by more than 23.5 points")
    Anything else is refused. A half-point floor makes a push impossible; an integer floor with '>' means
    exactly-the-floor loses, which is what "more than" says.
    """
    if operator == ">=":
        if threshold is None:
            return None, {}, "operator '>=' with no threshold"
        return value >= float(threshold), {"comparison": f"{value} >= {threshold}"}, None
    if operator == ">":
        if floor_strike is None:
            return None, {}, "operator '>' with no floor_strike"
        return value > float(floor_strike), {"comparison": f"{value} > {floor_strike}"}, None
    return None, {}, f"comparison operator {operator!r} is not an established settlement rule"


def settle_observation(obs: dict, book: ResultBook, *, exact_scalar_payout: float | None = None,
                       exact_scalar_source: str | None = None,
                       exact_scalar_unavailable_reason: str | None = None) -> Settlement:
    """Settle one immutable shadow observation.

    `exact_scalar_payout` is the EXCHANGE'S OWN published `settlement_value_dollars` for this ticker, and is the
    only value this function will ever record for the active-but-never-played branch. There is deliberately no
    parameter for a price: a midpoint, bid, ask or last trade cannot be passed in, so the pricing-time fair-price
    proxy cannot become settlement truth by accident. Without the exact value the branch is refused.
    """
    family = obs.get("family")
    period = obs.get("period")
    game_id = obs.get("game_id")
    direction = (obs.get("direction") or "YES").upper()

    if direction != "YES":
        return _refuse(REFUSED_DIRECTION, f"observation direction {direction!r} is not YES; payout undefined")
    if family not in SETTLEABLE_FAMILIES:
        reason = UNSETTLEABLE_FAMILY_REASON.get(
            family, f"settlement for family {family!r} is not established from free final results")
        return _refuse(REFUSED_UNSUPPORTED_FAMILY, reason, family=family)
    if period not in (FULL_GAME, None):
        return _refuse(REFUSED_UNSUPPORTED_PERIOD,
                       f"only full-game settlement is established; this contract covers {period}",
                       family=family, period=period)
    if not game_id:
        return _refuse(REFUSED_GAME_IDENTITY, "observation did not join a scheduled game", family=family)
    g = book.games.get(game_id)
    if g is None:
        return _refuse(REFUSED_GAME_IDENTITY, f"{game_id} is not in the resolved schedule", game_id=game_id)
    if g.inconsistency:
        return _refuse(REFUSED_RESULT_INCONSISTENT, g.inconsistency, g.evidence())
    if g.status != FINAL:
        return _refuse(REFUSED_GAME_NOT_FINAL,
                       g.provisional_reason or f"{game_id} has no final score", g.evidence())
    # The readiness gate already refuses a game that is not independently proven complete. This is the same
    # check inside the engine, so a caller that settles without gating cannot bypass it: a populated score is
    # not a final status, and this is the last place to say so.
    verdict = book.final_verdict(game_id) if hasattr(book, "final_verdict") else None
    if verdict is not None and verdict.contradictions:
        return _refuse(REFUSED_RESULT_INCONSISTENT, "; ".join(verdict.contradictions), g.evidence())
    if verdict is not None and not verdict.proven:
        return _refuse(REFUSED_GAME_NOT_FINAL,
                       f"{game_id} looks final but nothing independent attests that it is complete",
                       g.evidence())

    if family == "PLAYER_STAT":
        return _settle_player_stat(obs, book, g, exact_scalar_payout, exact_scalar_source,
                                   exact_scalar_unavailable_reason)
    return _settle_game_family(obs, g)


def _settle_game_family(obs: dict, g) -> Settlement:
    family = obs.get("family")
    ev = {"family": family, "period": obs.get("period"), **g.evidence()}
    threshold, operator, floor = obs.get("threshold"), obs.get("operator"), obs.get("floor_strike")

    if family == "GAME_WINNER":
        team = obs.get("team")
        if team is None:
            # the TIE leg carries no team; the ledger does not currently mark it, so refuse rather than guess
            return _refuse(REFUSED_TEAM_IDENTITY,
                           "game-winner leg carries no team (tie legs are not distinguished in the ledger schema)", ev)
        margin = g.margin_for(team)
        if margin is None:
            return _refuse(REFUSED_TEAM_IDENTITY, f"team {team!r} is not in {g.game_id}", ev, team=team)
        ev["team"] = team
        ev["margin_for_team"] = margin
        if margin == 0:
            # a tie pays $0.50 to BOTH sides (docs/KALSHI_SETTLEMENT.md; 8 archived markets, 4 tied games)
            return Settlement(SETTLED, 0.5, KIND_TIE_SPLIT, "tied game settles $0.50 per side", ev)
        return Settlement(SETTLED, 1.0 if margin > 0 else 0.0, KIND_BINARY,
                          f"{team} {'won' if margin > 0 else 'lost'} by {abs(margin):g}", ev)

    if family == "SPREAD":
        team = obs.get("team")
        margin = g.margin_for(team)
        if margin is None:
            return _refuse(REFUSED_TEAM_IDENTITY, f"spread team {team!r} is not in {g.game_id}", ev, team=team)
        met, cev, bad = _threshold_met(margin, threshold, operator, floor)
        if bad:
            return _refuse(REFUSED_AMBIGUOUS_SEMANTICS, bad, ev, team=team, margin_for_team=margin)
        ev.update(cev); ev["team"] = team; ev["margin_for_team"] = margin
        return Settlement(SETTLED, 1.0 if met else 0.0, KIND_BINARY,
                          f"{team} margin {margin:g} vs line", ev)

    if family == "TOTAL":
        total = g.total_points
        met, cev, bad = _threshold_met(total, threshold, operator, floor)
        if bad:
            return _refuse(REFUSED_AMBIGUOUS_SEMANTICS, bad, ev, total_points=total)
        ev.update(cev)
        return Settlement(SETTLED, 1.0 if met else 0.0, KIND_BINARY, f"game total {total:g}", ev)

    if family == "TEAM_TOTAL":
        team = obs.get("team")
        pts = g.team_points(team)
        if pts is None:
            return _refuse(REFUSED_TEAM_IDENTITY, f"team-total team {team!r} is not in {g.game_id}", ev, team=team)
        met, cev, bad = _threshold_met(pts, threshold, operator, floor)
        if bad:
            return _refuse(REFUSED_AMBIGUOUS_SEMANTICS, bad, ev, team=team, team_points=pts)
        ev.update(cev); ev["team"] = team; ev["team_points"] = pts
        return Settlement(SETTLED, 1.0 if met else 0.0, KIND_BINARY, f"{team} scored {pts:g}", ev)

    if family == "BOTH_TEAMS_SCORE_N":
        lo = None if (g.home_score is None or g.away_score is None) else min(g.home_score, g.away_score)
        met, cev, bad = _threshold_met(lo, threshold, operator, floor)
        if bad:
            return _refuse(REFUSED_AMBIGUOUS_SEMANTICS, bad, ev, lower_team_points=lo)
        ev.update(cev); ev["lower_team_points"] = lo
        return Settlement(SETTLED, 1.0 if met else 0.0, KIND_BINARY,
                          f"lower team scored {lo:g}", ev)

    return _refuse(REFUSED_UNSUPPORTED_FAMILY, f"no settlement branch for family {family!r}", ev)


def _settle_player_stat(obs: dict, book: ResultBook, g, exact_scalar_payout: float | None = None,
                        exact_scalar_source: str | None = None,
                        exact_scalar_unavailable_reason: str | None = None) -> Settlement:
    stat = obs.get("stat")
    player_id = obs.get("player_id")
    threshold, operator, floor = obs.get("threshold"), obs.get("operator"), obs.get("floor_strike")
    ev = {"family": "PLAYER_STAT", "stat": stat, "player_id": player_id,
          "player_name": obs.get("player_name"), **g.evidence()}

    if not player_id:
        return _refuse(REFUSED_PLAYER_IDENTITY,
                       "no canonical player id on the observation; the Kalshi player was never resolved to a GSIS id",
                       ev)
    if stat not in SETTLEABLE_PLAYER_STATS:
        return _refuse(REFUSED_UNSUPPORTED_STAT,
                       f"settlement column for player statistic {stat!r} is not established", ev)
    pr = book.player(g.game_id, player_id)
    if pr is None:
        complete = g.game_id in book.games_with_snaps and g.game_id in book.games_with_player_stats
        if complete:
            # This is the scratched-or-benched case, and it is genuinely undecidable from free data. The player
            # is absent from a COMPLETE snap table, so he took no snap -- but Kalshi settles an INACTIVE player
            # at $0.00 and an ACTIVE player who never took a snap at the pregame fair price, and nothing in
            # nflverse says which he was. Guessing picks between $0.00 and (often) $0.10-0.20 of payout.
            return _refuse(REFUSED_PARTICIPATION_UNPROVEN,
                           "player is absent from a complete snap table, so he took no snap; whether he was "
                           "INACTIVE (settles $0.00) or ACTIVE-but-never-played (settles at the pregame fair "
                           "price) is not provable from free data, and those settle differently",
                           ev, snap_table_complete=True)
        return _refuse(REFUSED_PARTICIPATION_UNPROVEN,
                       "player has neither a statistics row nor a snap-count row for this game, so neither "
                       "participation nor inactivity is proven (absence is not evidence)",
                       ev, snap_table_complete=False)
    ev.update(pr.evidence(stat))
    played = pr.played
    if played is None:
        return _refuse(REFUSED_PARTICIPATION_UNPROVEN,
                       "participation is unproven: no snap count and no recorded statistic for this player-game",
                       ev)
    if played is False:
        # PROVEN: active (the snap table lists him) and never on the field. The football fact is settled.
        # NOT PROVEN by that alone: the payout, which is the exchange's own scalar settlement value.
        branch = {**ev, "participation_branch": "active_no_snap_proven"}
        if exact_scalar_payout is None:
            return _refuse(REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE,
                           "active-but-never-played is PROVEN, and this branch settles at the exchange's own "
                           "scalar value, which is not available: " +
                           (exact_scalar_unavailable_reason or "no exchange settlement evidence for this ticker") +
                           ". A pregame midpoint is a pricing-time proxy for this branch, not the payout, so no "
                           "number is recorded",
                           branch, exact_scalar_payout_available=False)
        v = float(exact_scalar_payout)
        if not (0.0 <= v <= 1.0):
            return _refuse(REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE,
                           f"the exchange scalar value {v} is outside [0, 1] and cannot be a contract payout",
                           branch, exact_scalar_payout=v)
        return Settlement(SETTLED, v, KIND_SCALAR_EXACT,
                          "active, never took a snap: settles at the exchange's published scalar value",
                          {**branch, "exact_scalar_payout": v,
                           "exact_scalar_source": exact_scalar_source or "unspecified"})

    value = pr.stat_value(stat)
    if value is None and pr.has_snap_row and not pr.has_stats_row and g.game_id in book.games_with_player_stats:
        # The statistics table for this game IS published and does not list the player, while the snap counts
        # prove he was on the field. nflverse only lists players who recorded something, so absence from a
        # COMPLETE table is a proven zero -- the same explicit zero-row rule the pricing side already uses
        # (nfl_edge/research/player_distributions.load_player_games). Without it every player who took snaps
        # and recorded nothing would be refused, which is precisely the population a ladder's low rungs are
        # about.
        value = 0.0
        ev["zero_row"] = "took snaps, absent from a published statistics table: recorded none of this statistic"
    if value is None:
        return _refuse(REFUSED_STAT_UNAVAILABLE,
                       f"player took a snap but the published statistics do not carry {stat!r} for this game", ev)
    if stat == "touchdowns" and threshold is not None and float(threshold) >= 2:
        risky = [c for c in DOUBLE_COUNT_RISK_COLUMNS if (pr.stats.get(c) or 0) > 0]
        if len(risky) > 1:
            return _refuse(REFUSED_AMBIGUOUS_SEMANTICS,
                           f"a multi-touchdown threshold cannot be proven: {risky} may both credit the same "
                           "end-zone fumble recovery, so the touchdown COUNT is ambiguous", ev, stat_value=value)
    met, cev, bad = _threshold_met(value, threshold, operator, floor)
    if bad:
        return _refuse(REFUSED_AMBIGUOUS_SEMANTICS, bad, ev, stat_value=value)
    ev.update(cev)
    return Settlement(SETTLED, 1.0 if met else 0.0, KIND_BINARY,
                      f"{obs.get('player_name') or player_id} recorded {value:g} {stat}", ev)


def needs_player_stats(observations) -> bool:
    """Does this game's prediction set include anything that can only be settled from player statistics?"""
    return any(o.get("family") == "PLAYER_STAT" for o in observations)


def needs_exact_scalar(obs: dict, book: ResultBook) -> bool:
    """Does settling THIS observation depend on the exchange's own scalar value?

    True only for a player prop whose player is PROVEN to have been active and never on the field -- the one
    branch football evidence cannot price. Decidable from the result book alone, before any exchange read, which
    is what lets a game with no such dependency settle while the exchange is unreachable.
    """
    if obs.get("family") != "PLAYER_STAT" or (obs.get("period") not in (FULL_GAME, None)):
        return False
    gid, pid = obs.get("game_id"), obs.get("player_id")
    if not gid or not pid:
        return False
    g = book.games.get(gid)
    if g is None or g.status != FINAL:
        return False
    pr = book.player(gid, pid)
    return pr is not None and pr.played is False


def exact_scalar_dependencies(observations, book: ResultBook) -> set:
    """The TICKERS whose immutable evaluation needs terminal exchange evidence. Usually empty."""
    return {o["ticker"] for o in observations if o.get("ticker") and needs_exact_scalar(o, book)}
