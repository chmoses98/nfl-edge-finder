"""Which market families depend on WHO PLAYS QUARTERBACK, as an explicit, tested table. FAIL CLOSED for anything not in it.

WHY A TABLE
The first QB gate was a short list of ticker families (guards.QB_GATED_FAMILIES) and every family it forgot was approved with an unknown
quarterback: both-teams-score-N, winning margin, race-to-N, period lines, team stats, QB passing props. An allow-list of "gated" families
fails OPEN on whatever the author did not think of. This module inverts that: EVERY family the classifier (nfl_edge/kalshi/classifier.py),
the packet (handicap/packet.py), the derived-fair-value set (handicap/fairvalue.DERIVABLE) and the schema (handicap/schema.py) recognise has
an entry here, tests/test_qb_dependency.py fails if one is missing, and a family or statistic that is NOT in the table resolves to
QB_GATED with rule UNCLASSIFIED_FAIL_CLOSED. Unknown can only ever block.

CLASSIFICATIONS (2026-11-03)
QB_GATED     the outcome is materially a function of both offences, i.e. of who throws: every score-determined game-level market (winner,
             spread, total, team total, winning margin, both-teams-score-N, race-to-N, period and half/full lines, touchdown counts,
             first-TD team/time), team and game statistics, game events, a quarterback's own passing statistics, combos/parlays (a leg
             can be any of these), and anything outside the single-game RUN NFL scope (a game confirmation cannot satisfy it).
             Requires BOTH teams' quarterbacks CONFIRMED_STARTER.
QB_INDIRECT  a player prop whose production runs THROUGH the passing game (receptions, receiving yards, rush+rec yards, longest
             reception, anytime / first / next touchdown scorer). Decision: GATED ON THE PLAYER'S OWN TEAM'S QUARTERBACK ONLY (both when the
             team cannot be read from the ticker). Rationale: the repository's own projection layer already treats exactly these as
             quarterback-dependent and abstains when the quarterback is uncertain (context/qb_resolution.is_qb_dependent: pass-catcher
             receptions / receiving yards / rush+rec, and WR/TE touchdowns; an RB's rushing and touchdown rate is "carried mainly by his
             carries"). A Kalshi ticker does not carry the player's position, so a touchdown-scorer prop is treated as pass-catcher
             exposed (fail closed). The opponent's quarterback is second-order for a pass-catcher and is NOT required.
NOT_GATED    unrelated to the quarterback or only second-order: kicker props, defender tackles/sacks, running-back rushing volume/yards,
             longest rush, longest field goal. These keep their own player-availability gate (G_AVAILABILITY) and every other gate.
             A NOT_GATED statistic is only ever NOT_GATED for a player whose identity AND position were VERIFIED from the repository's own player
             data (player_identity.py) as a non-quarterback (2026-11-03: closes the former "a QB's rushing prop looks like a running-back rushing prop"
             gap). A QUARTERBACK's own rushing / receiving / scrambling / touchdown prop is QB_GATED on his own team: that team's quarterback must be
             CONFIRMED_STARTER *and be that player* (a backup's prop is blocked). If identity or position cannot be verified the prop is blocked
             outright (PLAYER_IDENTITY_UNVERIFIED): no confirmation can show that the player is not the quarterback. Field markets across both
             teams' players (game rushing leader, rushing head-to-head) can be won by a quarterback and are QB_GATED on both teams.

The classification of a ticker is the STRICTEST of what its series says and what the record's own ``market_family`` says.

Pure functions; no I/O; no clock.
"""
from __future__ import annotations

from dataclasses import dataclass

from nfl_edge.kalshi import classifier as K

from . import player_identity as PI

TABLE_VERSION = "nfl-qb-dependency-2026-11-03.2"

QB_GATED = "QB_GATED"
QB_INDIRECT = "QB_INDIRECT"
NOT_GATED = "NOT_GATED"
CLASSIFICATIONS = (QB_GATED, QB_INDIRECT, NOT_GATED)

SCOPE_BOTH = "BOTH_TEAMS"
SCOPE_OWN = "OWN_TEAM"

RULE_FAMILY = "FAMILY"
RULE_STAT = "FAMILY_STAT"
RULE_OUT_OF_SCOPE = "OUT_OF_SINGLE_GAME_SCOPE"
RULE_UNCLASSIFIED = "UNCLASSIFIED_FAIL_CLOSED"
RULE_NO_TICKER = "NO_TICKER_FAIL_CLOSED"
RULE_PLAYER_UNVERIFIED = "PLAYER_IDENTITY_UNVERIFIED_FAIL_CLOSED"
RULE_QB_OWN_PROP = "QB_OWN_PROP_STARTER_MUST_BE_THE_PLAYER"

#: Families whose contract is ABOUT ONE NAMED PLAYER (the packet market row carries his GSIS id). For these, the table's class is applied only
#: after the player's identity and position are verified (player_identity.verify); see ``requirement``.
PLAYER_SCOPED_FAMILIES = ("PLAYER_STAT", "FIRST_TD_SCORER", "NEXT_TD_SCORER", "ANYTIME_TD")

_G, _I, _N = QB_GATED, QB_INDIRECT, NOT_GATED

# ----------------------------------------------------------------------------------------------------------------- family-level entries
#: family -> (classification, rationale). Used whenever the statistic does not change the answer.
FAMILY_TABLE: dict = {
    # --- score-determined game lines (full game and periods)
    "GAME_WINNER": (_G, "settles on the score; the starter moves the line exactly as he moves a total"),
    "PERIOD_WINNER": (_G, "1H/2H/quarter winner settles on that period's score"),
    "SPREAD": (_G, "settles on the score margin"),
    "TOTAL": (_G, "settles on total points"),
    "TEAM_TOTAL": (_G, "settles on one team's points; the opponent's QB sets the pace and the defence it faces"),
    "WIN_MARGIN_BUCKET": (_G, "settles on the margin bucket"),
    "BOTH_TEAMS_SCORE_N": (_G, "settles on min(team points); the card derives and prices it (fairvalue.DERIVABLE)"),
    "BOTH_TEAMS_SCORE": (_G, "period both-teams-score settles on the period score"),
    "RACE_TO_N": (_G, "settles on scoring order; both offences"),
    "TOTAL_TD": (_G, "touchdown count is the scoring rate of both offences"),
    "PERIOD_TD": (_G, "period touchdown count"),
    "HALF_FULL_RESULT": (_G, "half-time/full-time result settles on two score states"),
    "FIRST_TD_TEAM": (_G, "which offence scores first"),
    "FIRST_TD_TIME": (_G, "scoring pace of both offences"),
    "GAME_EVENT": (_G, "game events (overtime, safety, lead changes, 2-pt, 4th-down, comeback, scoreless quarter, non-QB pass, defensive TD, "
                       "...) are functions of the score path or of the quarterback's own play; default for game-level markets is gated"),
    "TEAM_STAT": (_G, "team yards / first downs / touchdowns / field goals / sacks / turnovers: team passing and scoring volume run through the QB"),
    # --- combos
    "COMBO": (_G, "a combination can contain any leg, including a score line; legs are not read from the ticker, so it is gated"),
    "PARLAY": (_G, "a parlay can contain any leg, including a score line; legs are not read from the ticker, so it is gated"),
    # --- scorer props (position is not in a ticker: treated as pass-catcher exposed)
    "FIRST_TD_SCORER": (_I, "scorer may be a WR/TE; pass-catcher touchdowns are QB-dependent in context/qb_resolution; gated on the player's own QB"),
    "NEXT_TD_SCORER": (_I, "same as first-TD scorer"),
    "ANYTIME_TD": (_I, "same as first-TD scorer (schema family name for anytime touchdown)"),
    # --- recognised, but outside single-game RUN NFL scope or not a football market: cannot be satisfied by a game confirmation -> blocked
    "UNKNOWN_NEEDS_CLASSIFICATION": (_G, "the classifier could not place the series; unknown fails closed"),
    "NOT_NFL": (_G, "not an NFL contract; fails closed"),
    "NOT_NFL_OR_UNKNOWN": (_G, "not recognised as NFL; fails closed"),
}

#: Families that are not single-game contracts. The card cannot emit them (it prices one game at a time); if one ever reaches a gate it is
#: QB_GATED, because no per-game QB confirmation exists for it, so it can never pass this gate.
OUT_OF_SCOPE_FAMILIES = (
    "AWARD", "COACH_EVENT", "CONFERENCE_WINNER", "DIVISION_WINNER", "DRAFT", "MAKE_PLAYOFFS", "NFL_BUSINESS_EVENT", "PLAYER_AVAILABILITY",
    "PLAYER_ROLE_EVENT", "SEASON_DIVISION_ORDER", "SEASON_DIVISION_STAT", "SEASON_FANTASY", "SEASON_LEADER", "SEASON_MATCHUP",
    "SEASON_PLAYER_SPECIAL", "SEASON_PLAYER_STAT", "SEASON_SEED", "SEASON_SPECIAL", "SEASON_TEAM_EVENT", "SEASON_TEAM_H2H",
    "SEASON_TEAM_LEADER", "SEASON_WINS", "SEASON_WINS_EXACT", "SUPER_BOWL_EVENT", "SUPER_BOWL_MATCHUP", "SUPER_BOWL_WINNER",
    "TEAM_WINS_BY_WEEK", "TRANSACTION_EVENT", "WEEK_EVENT", "WEEK_LEADER",
)
for _f in OUT_OF_SCOPE_FAMILIES:
    FAMILY_TABLE[_f] = (_G, "season/week/event-scoped, not a single-game RUN NFL contract: no game confirmation can satisfy it, so it is blocked")

# ----------------------------------------------------------------------------------------------------------------- stat-level entries
#: (family, statistic) -> (classification, rationale) for the families whose answer depends on the statistic.
STAT_TABLE: dict = {
    # --- player statistics (a QUARTERBACK's own line, or ambiguous between a QB and a defender)
    ("PLAYER_STAT", "passing_yards"): (_G, "a quarterback's passing line: who throws is the whole question"),
    ("PLAYER_STAT", "passing_tds"): (_G, "a quarterback's passing line"),
    ("PLAYER_STAT", "attempts"): (_G, "passing attempts: team passing volume"),
    ("PLAYER_STAT", "completions"): (_G, "passing completions: team passing volume"),
    ("PLAYER_STAT", "interceptions"): (_G, "interceptions thrown (or caught) depend on the quarterbacks; the ticker does not say which, so gated"),
    ("PLAYER_STAT", "fantasy_points"): (_G, "fantasy points of an unknown position; a quarterback's are entirely QB-dependent"),
    # --- pass-catchers
    ("PLAYER_STAT", "receiving_yards"): (_I, "pass-catcher production runs through the passing game; own team's QB (context/qb_resolution)"),
    ("PLAYER_STAT", "receptions"): (_I, "pass-catcher production; own team's QB"),
    ("PLAYER_STAT", "rush_rec_yards"): (_I, "rush+rec is in context/qb_resolution.PASS_CATCHER_QB_STATS; own team's QB"),
    ("PLAYER_STAT", "longest_reception"): (_I, "a reception needs a thrower; own team's QB"),
    ("PLAYER_STAT", "touchdowns"): (_I, "anytime-TD: a WR/TE touchdown is QB-dependent (qb_resolution.is_qb_dependent); position not in ticker; own team's QB"),
    # --- unrelated or second-order
    ("PLAYER_STAT", "rushing_yards"): (_N, "running-back volume is carried by his carries (context/qb_resolution.is_qb_dependent); only for a VERIFIED non-quarterback"),
    ("PLAYER_STAT", "carries"): (_N, "running-back volume; only for a VERIFIED non-quarterback"),
    ("PLAYER_STAT", "longest_rush"): (_N, "a rushing play; only for a VERIFIED non-quarterback"),
    ("PLAYER_STAT", "sacks"): (_N, "a defender's pass rush; the opposing QB is second-order and the defender's own availability gate applies (verified non-QB)"),
    ("PLAYER_STAT", "tackles"): (_N, "defender volume; unrelated to who plays quarterback"),
    ("PLAYER_STAT", "field_goals"): (_N, "kicker prop; unrelated to the quarterback"),
    # --- head-to-head player props (two players, usually two teams; the ticker does not name both teams)
    ("PLAYER_H2H", "passing_yards"): (_G, "two quarterbacks' passing lines"),
    ("PLAYER_H2H", "receiving_yards"): (_G, "two pass-catchers, usually on different teams; both quarterbacks matter and the ticker does not name both teams"),
    ("PLAYER_H2H", "fantasy_points"): (_G, "fantasy points of unknown positions"),
    ("PLAYER_H2H", "rushing_yards"): (_G, "two players' rushing lines; either may be a quarterback and the ticker names no positions (2026-11-03: was NOT_GATED)"),
    # --- game-level statistics
    ("GAME_STAT", "field_goals_game"): (_G, "field goals are the stalled-drive complement of touchdowns: score-determined"),
    ("GAME_STAT", "sacks_game"): (_G, "sacks suffered by two quarterbacks"),
    ("GAME_STAT", "touchdowns_game"): (_G, "touchdown count of both offences"),
    ("GAME_STAT", "turnovers_game"): (_G, "turnovers include the quarterbacks' interceptions"),
    ("GAME_STAT", "longest_reception_game"): (_G, "longest reception in the game: passing-game big play of either offence"),
    ("GAME_STAT", "longest_td"): (_G, "longest touchdown: big plays of either offence"),
    ("GAME_STAT", "shortest_td"): (_G, "shortest touchdown: red-zone play-calling of either offence"),
    ("GAME_STAT", "longest_fg"): (_N, "a kicker's range; unrelated to the quarterback"),
    # --- who leads the game in a statistic: a field of both teams' players
    ("GAME_PLAYER_LEADER", "receiving_yards"): (_G, "game receiving-yards leader across both teams: both passing games"),
    ("GAME_PLAYER_LEADER", "passing_yards"): (_G, "game passing-yards leader: both quarterbacks"),
    ("GAME_PLAYER_LEADER", "receptions"): (_G, "game receptions leader across both teams"),
    ("GAME_PLAYER_LEADER", "rush_rec_yards"): (_G, "includes receiving; both teams"),
    ("GAME_PLAYER_LEADER", "touchdowns"): (_G, "touchdown leader across both teams"),
    ("GAME_PLAYER_LEADER", "fantasy_points"): (_G, "fantasy leader across both teams"),
    ("GAME_PLAYER_LEADER", "receiving_tds"): (_G, "receiving-touchdown leader across both teams"),
    ("GAME_PLAYER_LEADER", "passing_tds"): (_G, "passing-touchdown leader: both quarterbacks"),
    ("GAME_PLAYER_LEADER", "rushing_yards"): (_G, "the game's rushing leader can be a quarterback; the field spans both teams (2026-11-03: was NOT_GATED)"),
    ("GAME_PLAYER_LEADER", "rushing_tds"): (_G, "the game's rushing-touchdown leader can be a quarterback; the field spans both teams (2026-11-03: was NOT_GATED)"),
}
#: Families whose entry is stat-level (a stat missing from STAT_TABLE for one of these is UNCLASSIFIED -> gated).
STAT_LEVEL_FAMILIES = tuple(sorted({f for f, _ in STAT_TABLE}))

# classification strictness for merging two views of the same contract
_STRICT = {_N: 0, _I: 1, _G: 2}


@dataclass(frozen=True)
class QbRequirement:
    classification: str
    rule: str                    # FAMILY | FAMILY_STAT | OUT_OF_SINGLE_GAME_SCOPE | UNCLASSIFIED_FAIL_CLOSED | NO_TICKER_FAIL_CLOSED
    family: str | None
    stat: str | None
    scope: str                   # BOTH_TEAMS | OWN_TEAM (meaningful only when a confirmation is required)
    rationale: str
    teams_required: tuple        # the team codes whose quarterback must be CONFIRMED_STARTER ( () when none )
    identity_block: str | None = None       # player-scoped contract whose player identity / position is NOT verified: reason code; ALWAYS blocks
    starter_player_id: str | None = None    # verified quarterback prop: the confirmed starter of ``starter_team`` must be exactly this GSIS id
    starter_team: str | None = None
    player_position_group: str | None = None

    @property
    def requires_confirmation(self) -> bool:
        return self.classification in (QB_GATED, QB_INDIRECT) or self.identity_block is not None

    def to_dict(self) -> dict:
        return {"classification": self.classification, "rule": self.rule, "family": self.family, "stat": self.stat, "scope": self.scope,
                "teams_required": list(self.teams_required), "rationale": self.rationale, "table_version": TABLE_VERSION,
                "identity_block": self.identity_block, "starter_player_id": self.starter_player_id, "starter_team": self.starter_team,
                "player_position_group": self.player_position_group}


def lookup(family, stat=None) -> tuple:
    """(classification, rule, rationale) for a (family, stat); the table, then fail closed."""
    if (family, stat) in STAT_TABLE:
        c, why = STAT_TABLE[(family, stat)]
        return c, RULE_STAT, why
    if family in STAT_LEVEL_FAMILIES:
        return QB_GATED, RULE_UNCLASSIFIED, f"statistic {stat!r} of {family} is not in the QB-dependency table; unknown fails closed"
    if family in FAMILY_TABLE:
        c, why = FAMILY_TABLE[family]
        return c, (RULE_OUT_OF_SCOPE if family in OUT_OF_SCOPE_FAMILIES else RULE_FAMILY), why
    return QB_GATED, RULE_UNCLASSIFIED, f"family {family!r} is not in the QB-dependency table; unknown fails closed"


def _from_ticker(ticker: str):
    """(family, stat) the classifier assigns to a ticker's series, or (None, None). Only the SERIES decides here; nothing about the
    teams or the strike is needed, so fixtures with invented team codes classify the same as real ones."""
    series = ticker.split("-")[0]
    parts = ticker.split("-")
    event = "-".join(parts[:2]) if len(parts) > 1 else series
    sem = K.classify({"ticker": ticker, "event_ticker": event, "series_ticker": series})
    row = K.SERIES_FAMILY.get(series)
    fam, stat = sem.family, sem.stat
    if row is not None and row[1] != "GAME":          # the series itself is season/week/event scoped
        return fam, stat, True
    return fam, stat, False


def _kalshi_codes(team: str) -> tuple:
    out = {team}
    for k, v in K.KALSHI_TO_NFLVERSE.items():
        if v == team:
            out.add(k)
    return tuple(sorted(out, key=len, reverse=True))


def own_team(ticker: str, teams) -> str | None:
    """The one of ``teams`` (nflverse codes) whose Kalshi code starts the ticker's subject segment, or None when it cannot be told apart."""
    parts = (ticker or "").split("-")
    if len(parts) < 3 or not teams or len(teams) != 2:
        return None
    subject = parts[2]
    best = {}
    for t in teams:
        if not t:
            continue
        n = max((len(c) for c in _kalshi_codes(t) if subject.startswith(c)), default=0)
        if n:
            best[t] = n
    if not best:
        return None
    top = max(best.values())                      # LAC vs LA: the longer code that matches is the team ("LACWR1" is LAC, not LA)
    winners = [t for t, n in best.items() if n == top]
    return winners[0] if len(winners) == 1 else None


def requirement(ticker: str | None, *, family: str | None = None, teams=None, player=None, decision_time=None) -> QbRequirement:
    """What this contract needs from the quarterbacks. ``family`` is the record's own market_family (the strictest of the two views wins).
    ``teams`` is the game's [home, away] (nflverse codes); only used to narrow a QB_INDIRECT requirement to the player's own team.
    ``player`` is the VERIFIED player identity block (player_identity.verify) for a contract about one named player; ``decision_time`` the
    clock it is judged against. A player-scoped contract with no accepted identity is blocked (identity_block); a verified quarterback's prop
    is gated on his own team and requires him to be that team's confirmed starter; a verified non-quarterback keeps the table's class."""
    teams = [t for t in (teams or []) if t]
    t = (ticker or "").strip()
    views = []
    if t:
        fam, stat, out_scope = _from_ticker(t)
        if out_scope:
            views.append((QB_GATED, RULE_OUT_OF_SCOPE, fam, stat, "series is not a single-game contract; no game confirmation can satisfy it"))
        else:
            c, rule, why = lookup(fam, stat)
            views.append((c, rule, fam, stat, why))
    else:
        views.append((QB_GATED, RULE_NO_TICKER, family, None, "no ticker to classify; unknown fails closed"))
    if family:                                         # the record's own family, with no statistic: a stat-level family resolves fail-closed here
        c, rule, why = lookup(family, None)
        if not (t and views[0][2] == family):          # when the ticker already resolved this same family WITH its statistic, that is the finer view
            views.append((c, rule, family, None, why))
    best = max(views, key=lambda v: _STRICT[v[0]])
    cls, rule, fam, stat, why = best
    scoped = any(v[2] in PLAYER_SCOPED_FAMILIES for v in views) and rule != RULE_OUT_OF_SCOPE
    if scoped:
        ok, reason, ident = PI.accept(player, teams=teams, decision_time=decision_time)
        if not ok:
            return QbRequirement(QB_GATED, RULE_PLAYER_UNVERIFIED, fam, stat, SCOPE_BOTH,
                                 f"the player's identity or position is not verified ({reason}); a confirmation cannot show he is not the "
                                 "quarterback, so the prop is blocked (fail closed)", tuple(teams), identity_block=reason)
        if ident["is_qb"]:
            tm = ident["team"]
            if cls == QB_GATED:                        # a quarterback's passing prop: both quarterbacks, and he must be his team's starter
                return QbRequirement(QB_GATED, rule, fam, stat, SCOPE_BOTH, why + " (verified quarterback: he must be his team's confirmed starter)",
                                     tuple(teams), starter_player_id=ident["gsis_id"], starter_team=tm, player_position_group=ident["position_group"])
            return QbRequirement(QB_GATED, RULE_QB_OWN_PROP, fam, stat, SCOPE_OWN,
                                 "a quarterback's own rushing / receiving / scrambling / touchdown prop: his team's confirmed starter must be this player",
                                 (tm,), starter_player_id=ident["gsis_id"], starter_team=tm, player_position_group=ident["position_group"])
        # verified non-quarterback: the table's class; a pass-catcher prop is gated on the VERIFIED team's quarterback
        if cls == NOT_GATED:
            return QbRequirement(cls, rule, fam, stat, SCOPE_BOTH, why, (), player_position_group=ident["position_group"])
        if cls == QB_INDIRECT:
            return QbRequirement(cls, rule, fam, stat, SCOPE_OWN, why, (ident["team"],), player_position_group=ident["position_group"])
        return QbRequirement(cls, rule, fam, stat, SCOPE_BOTH, why, tuple(teams), player_position_group=ident["position_group"])
    if cls == NOT_GATED:
        return QbRequirement(cls, rule, fam, stat, SCOPE_BOTH, why, ())
    if cls == QB_INDIRECT:
        mine = own_team(t, teams)
        if mine is not None:
            return QbRequirement(cls, rule, fam, stat, SCOPE_OWN, why, (mine,))
        return QbRequirement(cls, rule, fam, stat, SCOPE_BOTH, why + " (player's team not readable from the ticker: both teams required)", tuple(teams))
    return QbRequirement(cls, rule, fam, stat, SCOPE_BOTH, why, tuple(teams))


def is_player_scoped(ticker: str | None, family: str | None = None) -> bool:
    """Whether the contract is about one named player (so its identity must be verified before its class applies)."""
    fams = []
    if family:
        fams.append(family)
    if ticker:
        fams.append(_from_ticker(ticker.strip())[0])
    return any(f in PLAYER_SCOPED_FAMILIES for f in fams)


def gated_family_names() -> tuple:
    """Family names whose family-level entry is QB_GATED (compat view for callers that held guards.QB_GATED_FAMILIES)."""
    return tuple(sorted(f for f, (c, _) in FAMILY_TABLE.items() if c == QB_GATED))
