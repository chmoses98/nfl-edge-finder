"""The family catalog: for every (family, period) what is proven, which engine answers it, and how it settles.

Read this before adding a family. A family is FULLY supported only when all four columns are green:

    semantic_confidence   PROVEN          the YES rule, push/tie, boundary and overtime treatment are pinned
    engine                != NONE         a latent distribution exists that the question is a function of
    model_support         SHADOW/PRICED   the engine has a validated (PRICED) or research (SHADOW) projection
    settlement            SUPPORTED       a deterministic settlement from free authoritative data exists

Anything else is recorded with the reason and terminates in the board accounting under the matching state
(`nfl_edge/board/states.py`). No family is "supported" here because it would be convenient.

The rules-text evidence is the 2026-09-10 discovery run (`rules_primary` / `rules_secondary` of live markets),
the 2025 archive (61,068 settled markets, docs/KALSHI_SETTLEMENT.md) and, for the winning-margin grammar, the
exhaustive check in tests/test_semantics_questions.py over every open margin contract on the board.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

from nfl_edge.semantics.questions import (
    AMBIGUOUS, GAME, JOINT, LIKELY, NONE, PERIOD, PLAYER, PROVEN, SEASON, UNKNOWN,
)

# model support states
CATALOG_VERSION = "catalog-1.1.0"       # 1.1.0: season settlement (wins-through-week, division, playoffs) is SUPPORTED
PRICED = "PRICED"                       # validated engine; automatic pricing (incumbent game families)
SHADOW = "SHADOW"                       # research engine; projections written as shadow-only
RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
JOINT_MODEL_REQUIRED = "JOINT_MODEL_REQUIRED"
NON_FOOTBALL_MODEL = "NON_FOOTBALL_MODEL"
NEWS_EVENT_MODEL_REQUIRED = "NEWS_EVENT_MODEL_REQUIRED"
UNSUPPORTED = "UNSUPPORTED"

# settlement support
SETTLE_SUPPORTED = "SUPPORTED"
SETTLE_PLANNED = "PLANNED"              # rule pinned and data identified, engine not built yet
SETTLE_UNSUPPORTED = "UNSUPPORTED"


@dataclass(frozen=True)
class FamilyEntry:
    family: str
    period: str                          # FULL | 1H | 2H | 1Q | 2Q | 3Q | 4Q | SEASON | WEEK | EVENT | ANY
    engine: str
    stat_family: str | None
    semantic_confidence: str
    yes_rule: str
    push_rule: str
    tie_rule: str
    overtime: str
    model_support: str
    settlement: str
    settlement_source: str
    settlement_rule_version: str
    evidence: str
    reason: str = ""

    def to_dict(self):
        return asdict(self)


def _e(*a, **k):
    return FamilyEntry(*a, **k)


_GAME_OT = "INCLUDED (full game incl. overtime per rules_primary)"
_PERIOD_RULES = "rules_secondary: 'Only points scored during the <period> of play count towards this market'"
_SCHED = "nflverse schedules/games.csv final scores (proven complete via postgame tables / ESPN)"
_PBP_Q = "nflverse play-by-play: last post-play score of each quarter (reproduces 256/256 2024 finals)"
_STATS = "nflverse stats_player_week + snap_counts (participation proven)"

FAMILY_CATALOG: dict = {}


def _add(entry: FamilyEntry):
    FAMILY_CATALOG[(entry.family, entry.period)] = entry


# ---------------------------------------------------------------- GAME engine: functions of the final score
_add(_e("GAME_WINNER", "FULL", GAME, "margin", PROVEN, "team margin > 0", "n/a", "tie pays $0.50 per side (8 archived markets)",
        _GAME_OT, PRICED, SETTLE_SUPPORTED, _SCHED, "settle-1.0.0", "rules + 2025 archive"))
_add(_e("SPREAD", "FULL", GAME, "margin", PROVEN, "team margin > floor (x.5)", "no push at x.5 floors", "n/a",
        _GAME_OT, PRICED, SETTLE_SUPPORTED, _SCHED, "settle-1.0.0", "rules + 2025 archive (3,000+ markets)"))
_add(_e("TOTAL", "FULL", GAME, "total", PROVEN, "total >= K (floor K-0.5)", "no push", "n/a",
        _GAME_OT, PRICED, SETTLE_SUPPORTED, _SCHED, "settle-1.0.0", "rules + 2025 archive"))
_add(_e("TEAM_TOTAL", "FULL", GAME, "team_points", PROVEN, "team points >= K", "no push", "n/a",
        _GAME_OT, PRICED, SETTLE_SUPPORTED, _SCHED, "settle-1.0.0", "rules + 2025 archive"))
_add(_e("BOTH_TEAMS_SCORE_N", "FULL", GAME, "min_team_points", PROVEN, "min(team points) >= K", "no push", "n/a",
        _GAME_OT, PRICED, SETTLE_SUPPORTED, _SCHED, "settle-1.0.0", "rules"))
_add(_e("WIN_MARGIN_BUCKET", "FULL", GAME, "margin", PROVEN,
        "lo <= team margin <= hi (inclusive; 15+ open above); TIE leg iff margin == 0",
        "buckets partition the integers: no push", "TIE strike YES, team strikes NO",
        _GAME_OT, SHADOW, SETTLE_SUPPORTED, _SCHED, "settle-2.0.0",
        "2026 rules_primary 'between 7 and 14 points' / 'at least 15' / 'exactly 0'; 2025 archive '(inclusive)'; ticker grammar verified over all 105 open contracts",
        reason="score-derived; new in v2, shadow until a prospective sample exists"))
_add(_e("TOTAL_TD", "FULL", GAME, "total_touchdowns", LIKELY, "touchdowns by both teams >= K, incl. overtime", "no push", "n/a",
        _GAME_OT, RESEARCH_REQUIRED, SETTLE_PLANNED, "nflverse play-by-play touchdown plays", "settle-2.0.0",
        "rules_secondary: 'Touchdowns recorded in overtime count'", reason="not a function of the final score; scoring-composition model required"))
_add(_e("RACE_TO_N", "FULL", GAME, "race", PROVEN, "first team to reach N points; NONE leg iff neither reaches N", "n/a", "n/a",
        _GAME_OT, RESEARCH_REQUIRED, SETTLE_PLANNED, "nflverse play-by-play scoring sequence", "settle-2.0.0",
        "rules_secondary", reason="needs the scoring ORDER; the final-score simulation carries no order"))
_add(_e("FIRST_TD_TEAM", "FULL", GAME, "first_td", PROVEN, "team scores the first touchdown (any kind, incl. OT); NONE leg iff no touchdown", "n/a", "n/a",
        _GAME_OT, RESEARCH_REQUIRED, SETTLE_PLANNED, "nflverse play-by-play first touchdown play", "settle-2.0.0",
        "rules_secondary", reason="needs the scoring ORDER"))
_add(_e("FIRST_TD_SCORER", "FULL", PLAYER, "first_td", LIKELY, "player scores the first TD; NONE leg iff no TD; active/no-snap fair-price clause", "n/a", "n/a",
        _GAME_OT, RESEARCH_REQUIRED, SETTLE_PLANNED, "nflverse play-by-play + player id", "settle-2.0.0", "rules + 132 scalar settlements", reason="scoring order + player identity"))
_add(_e("NEXT_TD_SCORER", "FULL", PLAYER, "first_td", LIKELY, "in-game sequential market", "n/a", "n/a", _GAME_OT, UNSUPPORTED, SETTLE_UNSUPPORTED,
        "n/a", "n/a", "rules", reason="in-game market; never pregame"))
_add(_e("GAME_EVENT", "FULL", NONE, None, LIKELY, "heterogeneous one-off events", "varies", "varies", "varies", UNSUPPORTED, SETTLE_UNSUPPORTED,
        "n/a", "n/a", "titles only", reason="rules vary per market"))
_add(_e("GAME_STAT", "FULL", NONE, None, LIKELY, "game-level extreme statistics", "varies", "varies", "varies", UNSUPPORTED, SETTLE_UNSUPPORTED,
        "n/a", "n/a", "titles only", reason="not modelled"))
_add(_e("TEAM_STAT", "FULL", NONE, "team_stat", LIKELY, "team stat >= K (touchdowns, field goals, sacks, yards)", "no push", "n/a", _GAME_OT,
        RESEARCH_REQUIRED, SETTLE_PLANNED, "nflverse play-by-play / team stats", "settle-2.0.0", "rules_primary", reason="team stat ladders need their own latent model"))

# ---------------------------------------------------------------- PERIOD engine
for p in ("1H", "1Q"):
    _add(_e("PERIOD_WINNER", p, PERIOD, "margin", PROVEN, f"team scores the most points in the {p}; TIE leg iff equal", "n/a",
            "tied period: team strikes NO, TIE strike YES", "NA", SHADOW, SETTLE_SUPPORTED, _PBP_Q, "settle-2.0.0", _PERIOD_RULES))
    _add(_e("SPREAD", p, PERIOD, "margin", PROVEN, f"team {p} margin > floor (x.5)", "no push at x.5", "n/a", "NA", SHADOW, SETTLE_SUPPORTED,
            _PBP_Q, "settle-2.0.0", _PERIOD_RULES))
    _add(_e("TOTAL", p, PERIOD, "total", PROVEN, f"{p} total points >= K", "no push", "n/a", "NA", SHADOW, SETTLE_SUPPORTED, _PBP_Q, "settle-2.0.0", _PERIOD_RULES))
    _add(_e("TEAM_TOTAL", p, PERIOD, "team_points", PROVEN, f"team {p} points >= K", "no push", "n/a", "NA", SHADOW, SETTLE_SUPPORTED, _PBP_Q, "settle-2.0.0", _PERIOD_RULES))
    _add(_e("BOTH_TEAMS_SCORE", p, PERIOD, "min_team_points", PROVEN, f"both teams score >= 1 point in the {p}", "n/a", "n/a", "NA", SHADOW,
            SETTLE_SUPPORTED, _PBP_Q, "settle-2.0.0", "rules_primary"))
for p in ("2Q", "3Q"):
    for fam, st in (("PERIOD_WINNER", "margin"), ("SPREAD", "margin"), ("TOTAL", "total"), ("TEAM_TOTAL", "team_points"), ("BOTH_TEAMS_SCORE", "min_team_points")):
        _add(_e(fam, p, PERIOD, st, PROVEN, f"{fam} on {p} points only", "no push", "tied period: TIE leg YES", "NA", SHADOW, SETTLE_SUPPORTED,
                _PBP_Q, "settle-2.0.0", _PERIOD_RULES, reason="lower priority (illiquid); priced from the same joint quarter simulation"))
for p in ("2H", "4Q"):
    for fam, st in (("PERIOD_WINNER", "margin"), ("SPREAD", "margin"), ("TOTAL", "total"), ("TEAM_TOTAL", "team_points"), ("BOTH_TEAMS_SCORE", "min_team_points")):
        _add(_e(fam, p, PERIOD, st, PROVEN, f"{fam} on {p} points only; overtime EXCLUDED", "no push", "tied period: TIE leg YES",
                "EXCLUDED", SHADOW, SETTLE_SUPPORTED, _PBP_Q, "settle-2.0.0", _PERIOD_RULES + "; 2H markets explicitly exclude overtime (docs/KALSHI_SETTLEMENT.md)",
                reason="lower priority (illiquid)"))
_add(_e("HALF_FULL_RESULT", "1H", JOINT, "margin", PROVEN, "1H result AND full-game result (incl. OT) both correct", "n/a", "TIE legs per period",
        "INCLUDED for the full-game leg", SHADOW, SETTLE_SUPPORTED, _PBP_Q + " + " + _SCHED, "settle-2.0.0", "rules_secondary",
        reason="priced only from a simulation that carries both periods jointly (the period engine); never as a product"))
_add(_e("PERIOD_TD", "ANY", NONE, "touchdowns", LIKELY, "period touchdown count", "no push", "n/a", "NA", RESEARCH_REQUIRED, SETTLE_PLANNED,
        "nflverse play-by-play", "settle-2.0.0", "titles", reason="period TD counts not modelled"))

# ---------------------------------------------------------------- PLAYER engine
_PLAYER_RULE = "stat >= K once the player takes >= 1 snap; active-never-snap settles at the pregame fair price; inactive settles $0"
_PLAYER_EV = "rules_secondary + 61,068 archived settlements (docs/KALSHI_SETTLEMENT.md)"
for st, support, settle in (
    ("passing_yards", SHADOW, SETTLE_SUPPORTED), ("passing_tds", SHADOW, SETTLE_SUPPORTED), ("interceptions", SHADOW, SETTLE_SUPPORTED),
    ("attempts", SHADOW, SETTLE_SUPPORTED), ("completions", SHADOW, SETTLE_SUPPORTED),
    ("rushing_yards", SHADOW, SETTLE_SUPPORTED), ("carries", SHADOW, SETTLE_SUPPORTED),
    ("receiving_yards", SHADOW, SETTLE_SUPPORTED), ("receptions", SHADOW, SETTLE_SUPPORTED),
    ("touchdowns", SHADOW, SETTLE_SUPPORTED), ("rush_rec_yards", SHADOW, SETTLE_SUPPORTED),
    ("longest_reception", RESEARCH_REQUIRED, SETTLE_PLANNED), ("longest_rush", RESEARCH_REQUIRED, SETTLE_PLANNED),
    ("field_goals", RESEARCH_REQUIRED, SETTLE_PLANNED), ("sacks", DATA_UNAVAILABLE, SETTLE_PLANNED), ("tackles", DATA_UNAVAILABLE, SETTLE_PLANNED),
    ("fantasy_points", RESEARCH_REQUIRED, SETTLE_PLANNED),
):
    src = _STATS if settle == SETTLE_SUPPORTED else "nflverse play-by-play (longest plays) / pfr advanced stats (defense)"
    reason = {"longest_reception": "distribution of the maximum of per-target gains; not a marginal stat model",
              "longest_rush": "distribution of the maximum of per-carry gains",
              "field_goals": "kicker attempts depend on drive outcomes; no validated model",
              "sacks": "defensive stats: free per-game data lags (PFR advanced stats are weekly, not point-in-time)",
              "tackles": "defensive stats: no point-in-time free feed",
              "fantasy_points": "composite of several stats; D/ST rows are team entities",
              "rush_rec_yards": "sum of two modelled stats; joint distribution of one player's rushing and receiving required (v2 supports it from the same player simulation)"}.get(st, "")
    _add(_e("PLAYER_STAT:" + st, "FULL", PLAYER, st, PROVEN, _PLAYER_RULE, "no push (integer ladder)", "n/a", _GAME_OT, support, settle, src,
            "settle-1.0.0" if settle == SETTLE_SUPPORTED and st != "rush_rec_yards" else "settle-2.0.0", _PLAYER_EV, reason=reason))
_add(_e("PLAYER_H2H", "FULL", JOINT, None, LIKELY, "player A stat > player B stat", "tie rule unknown", "UNKNOWN", _GAME_OT, JOINT_MODEL_REQUIRED,
        SETTLE_PLANNED, _STATS, "settle-2.0.0", "titles", reason="joint distribution of two players; tie rule not pinned"))

# ---------------------------------------------------------------- SEASON engine
_add(_e("SEASON_WINS", "SEASON", SEASON, "season_wins", LIKELY, "regular-season wins >= K", "no push", "a tie is not a win (LIKELY)", "NA",
        SHADOW, SETTLE_SUPPORTED, _SCHED + " (season aggregate; settles only once every regular-season game of the team is FINAL)", "settle-2.0.0",
        "rules_primary 'wins at least K games in the regular season'", reason="schedule Monte Carlo; tie treatment not pinned by the rules text"))
_add(_e("SEASON_WINS_EXACT", "SEASON", SEASON, "season_wins", LIKELY, "regular-season wins == K", "n/a", "LIKELY", "NA", SHADOW, SETTLE_SUPPORTED,
        _SCHED + " (season aggregate; settles only once every regular-season game of the team is FINAL)", "settle-2.0.0", "titles"))
_add(_e("TEAM_WINS_BY_WEEK", "SEASON", SEASON, "wins_through_week", LIKELY, "wins through week W >= K", "no push",
        "both readings evaluated (a tie is 0 wins / half a win); settles only where they agree", "NA", SHADOW, SETTLE_SUPPORTED,
        _SCHED + " (the team's own games through week W; settles early once no remaining game can change the answer)", "season-settle-1.0.0", "titles"))
_add(_e("MAKE_PLAYOFFS", "SEASON", SEASON, "playoffs", LIKELY, "team is one of the 14 qualifiers", "n/a", "no tie-break is run: the bracket is read, not computed", "NA",
        SHADOW, SETTLE_SUPPORTED, "nflverse schedules/games.csv postseason games: presence proves qualification, absence from a structurally complete bracket proves elimination",
        "season-settle-1.0.0", "rules_primary", reason="projection tie-breaks are approximate (LIKELY); settlement never uses them"))
_add(_e("DIVISION_WINNER", "SEASON", SEASON, "division", LIKELY, "team wins its division", "n/a", "no tie-break is run: the league's own seeding is read back", "NA", SHADOW, SETTLE_SUPPORTED,
        "nflverse schedules/games.csv postseason bracket: seeds 1-4 of a conference are its division winners, i.e. {wild-card hosts} + {bye teams}, cross-checked against the divisions' W-L-T",
        "season-settle-1.0.0", "rules_primary"))
_add(_e("CONFERENCE_WINNER", "SEASON", SEASON, "conference", LIKELY, "team wins the conference championship", "n/a", "n/a", "NA", SHADOW, SETTLE_PLANNED,
        "playoff results", "settle-2.0.0", "rules_primary"))
_add(_e("SUPER_BOWL_WINNER", "SEASON", SEASON, "super_bowl", LIKELY, "team wins the Super Bowl", "n/a", "n/a", "NA", SHADOW, SETTLE_PLANNED,
        "playoff results", "settle-2.0.0", "rules_primary"))
_add(_e("SEASON_SEED", "SEASON", SEASON, "seed", AMBIGUOUS, "team holds seed N of its conference", "n/a", "tie-breakers", "NA", RESEARCH_REQUIRED, SETTLE_PLANNED,
        "final standings", "settle-2.0.0", "titles", reason="seed grammar in the event ticker unverified; tie-breakers"))
for fam in ("SEASON_LEADER", "SEASON_PLAYER_STAT", "SEASON_FANTASY", "SEASON_PLAYER_SPECIAL", "SEASON_TEAM_EVENT", "SEASON_TEAM_H2H",
            "SEASON_DIVISION_STAT", "SEASON_TEAM_LEADER", "SEASON_MATCHUP", "SUPER_BOWL_MATCHUP", "SEASON_DIVISION_ORDER", "SEASON_SPECIAL",
            "WEEK_LEADER", "WEEK_EVENT", "PLAYER_AVAILABILITY"):
    _add(_e(fam, "SEASON", NONE, None, LIKELY, "season / week aggregate read from the title", "varies", "varies", "NA", RESEARCH_REQUIRED, SETTLE_UNSUPPORTED,
            "n/a", "n/a", "titles", reason="football-modelable in principle; no engine yet"))

# ---------------------------------------------------------------- JOINT
for fam in ("PARLAY", "COMBO"):
    _add(_e(fam, "FULL", JOINT, None, LIKELY, "every associated leg resolves YES on its stated side", "n/a", "per leg", "per leg", JOINT_MODEL_REQUIRED,
            SETTLE_PLANNED, "per-leg settlement", "settle-2.0.0", "custom_strike 'Associated Markets' / 'Associated Market Sides'",
            reason="legs are dependent; priced only where every leg is a function of ONE shared simulation (shadow), never as a product"))

# ---------------------------------------------------------------- non-football
for fam in ("AWARD", "DRAFT", "COACH_EVENT", "TRANSACTION_EVENT", "PLAYER_ROLE_EVENT", "NFL_BUSINESS_EVENT", "SUPER_BOWL_EVENT"):
    _add(_e(fam, "EVENT", NONE, None, LIKELY, "news / vote / transaction event", "n/a", "n/a", "NA", NON_FOOTBALL_MODEL, SETTLE_UNSUPPORTED,
            "n/a", "n/a", "titles", reason="not a football simulation question"))
_add(_e("NOT_NFL", "ANY", NONE, None, UNKNOWN, "not an NFL contract", "n/a", "n/a", "NA", UNSUPPORTED, SETTLE_UNSUPPORTED, "n/a", "n/a", "series prefix", reason="excluded"))
_add(_e("NOT_NFL_OR_UNKNOWN", "ANY", NONE, None, UNKNOWN, "unknown", "n/a", "n/a", "NA", UNSUPPORTED, SETTLE_UNSUPPORTED, "n/a", "n/a", "none", reason="unclassified"))
_add(_e("UNKNOWN_NEEDS_CLASSIFICATION", "ANY", NONE, None, UNKNOWN, "unknown", "n/a", "n/a", "NA", UNSUPPORTED, SETTLE_UNSUPPORTED, "n/a", "n/a", "none",
        reason="series not in the taxonomy: provisional classification required"))


def catalog_entry(family: str | None, period: str | None, stat: str | None = None) -> FamilyEntry | None:
    """Most specific entry: PLAYER_STAT is keyed by statistic; periods fall back to ANY / SEASON / EVENT."""
    if family is None:
        return None
    if family == "PLAYER_STAT":
        e = FAMILY_CATALOG.get((f"PLAYER_STAT:{stat}", "FULL"))
        if e is None:
            return FamilyEntry("PLAYER_STAT:" + str(stat), "FULL", PLAYER, stat, LIKELY, _PLAYER_RULE, "no push", "n/a", _GAME_OT,
                               DATA_UNAVAILABLE, SETTLE_UNSUPPORTED, "n/a", "n/a", "not inventoried", reason=f"player statistic {stat!r} not in the catalog")
        return e
    for p in (period or "FULL", "FULL", "SEASON", "EVENT", "ANY"):
        e = FAMILY_CATALOG.get((family, p))
        if e is not None:
            return e
    return None


def families_by_engine() -> dict:
    out: dict = {}
    for (fam, per), e in FAMILY_CATALOG.items():
        out.setdefault(e.engine, []).append({"family": fam, "period": per, "semantic_confidence": e.semantic_confidence,
                                             "model_support": e.model_support, "settlement": e.settlement, "reason": e.reason})
    return out
