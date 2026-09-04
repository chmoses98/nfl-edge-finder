"""Kalshi NFL market-family classifier.

Turns a raw Kalshi market record into `MarketSemantics`: what football event the
contract settles on, for which game/team/player/period, with what threshold and
what YES means. Unknown structures are preserved as UNKNOWN_NEEDS_CLASSIFICATION,
never dropped (they still get captured).

Ground truth learned from real markets (tests/fixtures/kalshi_market_samples.json):
  * Ladder rungs use strike_type="greater" with floor_strike = K - 0.5 and a
    ticker suffix "-K" (e.g. KXNFLRECYDS-...-LARDADAMS17-120 has floor 119.5):
    YES  <=>  stat >= K  (integers; no push possible).
  * A few families use strike_type="greater_or_equal" with an integer floor
    (KXNFLWINS-27IND-9 floor 9 => wins >= 9; KXNFLBOTH-...-35 floor 35).
  * Spreads: "-KC8" == "Kansas City wins by over 7.5" (floor 7.5). Both teams get
    their own ladder inside the event. Margin is team score minus opponent.
  * Event ticker for single-game families: {SERIES}-{YY}{MON}{DD}{AWAY}{HOME}
    with Kalshi team codes (LAR, JAC, ARI, ...). No time segment.
  * Player tickers: {TEAM}{INITIAL}{SURNAME}{JERSEY}-{K}; title "Name: K+ stat".
    custom_strike.football_player is Kalshi's own player UUID (stable id).
  * Winning margin: custom_strike {"Winning Margin": "7 to 14" | "tie" | "1 to 6"...}.
  * Period families: 1H/2H/1Q..4Q variants of winner/spread/total/team total.
"""
from __future__ import annotations

import math
import re
from dataclasses import dataclass, field, asdict

KALSHI_TEAM_CODES = ["ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN", "DET", "GB", "HOU", "IND",
                     "JAC", "KC", "LAC", "LAR", "LV", "MIA", "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA",
                     "SF", "TB", "TEN", "WAS"]
KALSHI_TO_NFLVERSE = {c: c for c in KALSHI_TEAM_CODES}
KALSHI_TO_NFLVERSE.update({"JAC": "JAX", "LAR": "LA"})
MONTHS = {m: i + 1 for i, m in enumerate(["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}

UNKNOWN = "UNKNOWN_NEEDS_CLASSIFICATION"

# series ticker -> (family, scope, period, stat)
# period: FULL, 1H, 2H, 1Q, 2Q, 3Q, 4Q ; scope: GAME, SEASON, WEEK, EVENT
PERIOD_RE = re.compile(r"^KXNFL(1H|2H|1Q|2Q|3Q|4Q)(WINNER|SPREAD|TOTAL|TEAMTOTAL|BTTS|TD|FT)?$")
SERIES_FAMILY = {
    "KXNFLGAME": ("GAME_WINNER", "GAME", "FULL", None),
    "KXNFLSPREAD": ("SPREAD", "GAME", "FULL", "margin"),
    "KXNFLTOTAL": ("TOTAL", "GAME", "FULL", "total_points"),
    "KXNFLTEAMTOTAL": ("TEAM_TOTAL", "GAME", "FULL", "team_points"),
    "KXNFLWINMARGIN": ("WIN_MARGIN_BUCKET", "GAME", "FULL", "margin"),
    "KXNFLBOTH": ("BOTH_TEAMS_SCORE_N", "GAME", "FULL", "min_team_points"),
    "KXNFLRACE": ("RACE_TO_N", "GAME", "FULL", "race"),
    "KXNFLTOTALTD": ("TOTAL_TD", "GAME", "FULL", "total_touchdowns"),
    "KXNFLFIRSTTD": ("FIRST_TD_SCORER", "GAME", "FULL", "first_td"),
    "KXNFLFIRSTTDTEAM": ("FIRST_TD_TEAM", "GAME", "FULL", "first_td_team"),
    "KXNFLFIRSTTDTIME": ("FIRST_TD_TIME", "GAME", "FULL", "first_td_time"),
    "KXNFLNEXTTD": ("NEXT_TD_SCORER", "GAME", "FULL", "next_td"),
    "KXNFLTD": ("PLAYER_STAT", "GAME", "FULL", "touchdowns"),
    "KXNFLANYTD": ("PLAYER_STAT", "GAME", "FULL", "touchdowns"),
    "KXNFL2TD": ("PLAYER_STAT", "GAME", "FULL", "touchdowns"),
    "KXNFLPASSYDS": ("PLAYER_STAT", "GAME", "FULL", "passing_yards"),
    "KXNFLPASSTDS": ("PLAYER_STAT", "GAME", "FULL", "passing_tds"),
    "KXNFLPASSATT": ("PLAYER_STAT", "GAME", "FULL", "attempts"),
    "KXNFLPASSCOMP": ("PLAYER_STAT", "GAME", "FULL", "completions"),
    "KXNFLPASSINT": ("PLAYER_STAT", "GAME", "FULL", "interceptions"),
    "KXNFLINT": ("PLAYER_STAT", "GAME", "FULL", "interceptions"),
    "KXNFLRSHYDS": ("PLAYER_STAT", "GAME", "FULL", "rushing_yards"),
    "KXNFLRSHATT": ("PLAYER_STAT", "GAME", "FULL", "carries"),
    "KXNFLRECYDS": ("PLAYER_STAT", "GAME", "FULL", "receiving_yards"),
    "KXNFLREC": ("PLAYER_STAT", "GAME", "FULL", "receptions"),
    "KXNFLRRYDS": ("PLAYER_STAT", "GAME", "FULL", "rush_rec_yards"),
    "KXNFLSACK": ("PLAYER_STAT", "GAME", "FULL", "sacks"),
    "KXNFLTKL": ("PLAYER_STAT", "GAME", "FULL", "tackles"),
    "KXNFLLONGREC": ("PLAYER_STAT", "GAME", "FULL", "longest_reception"),
    "KXNFLLONGRSH": ("PLAYER_STAT", "GAME", "FULL", "longest_rush"),
    "KXNFLLONGESTREC": ("GAME_STAT", "GAME", "FULL", "longest_reception_game"),
    "KXNFLLONGESTTD": ("GAME_STAT", "GAME", "FULL", "longest_td"),
    "KXNFLSHORTESTTD": ("GAME_STAT", "GAME", "FULL", "shortest_td"),
    "KXNFLLONGESTFG": ("GAME_STAT", "GAME", "FULL", "longest_fg"),
    "KXNFLLONGFG": ("GAME_STAT", "GAME", "FULL", "longest_fg"),
    "KXNFLFG": ("PLAYER_STAT", "GAME", "FULL", "field_goals"),
    "KXNFLGAMEFG": ("GAME_STAT", "GAME", "FULL", "field_goals_game"),
    "KXNFLGAMESACK": ("GAME_STAT", "GAME", "FULL", "sacks_game"),
    "KXNFLGAMETD": ("GAME_STAT", "GAME", "FULL", "touchdowns_game"),
    "KXNFLGAMETO": ("GAME_STAT", "GAME", "FULL", "turnovers_game"),
    "KXNFLTEAMTD": ("TEAM_STAT", "GAME", "FULL", "team_touchdowns"),
    "KXNFLTEAMFG": ("TEAM_STAT", "GAME", "FULL", "team_field_goals"),
    "KXNFLTEAMSACK": ("TEAM_STAT", "GAME", "FULL", "team_sacks"),
    "KXNFLTEAMTO": ("TEAM_STAT", "GAME", "FULL", "team_turnovers"),
    "KXNFLTEAMYDS": ("TEAM_STAT", "GAME", "FULL", "team_yards"),
    "KXNFLTEAM1STDOWNS": ("TEAM_STAT", "GAME", "FULL", "team_first_downs"),
    "KXNFLTEAMFIRSTTD": ("FIRST_TD_TEAM", "GAME", "FULL", "first_td_team"),
    "KXNFLOT": ("GAME_EVENT", "GAME", "FULL", "overtime"),
    "KXNFLOTWIN": ("GAME_EVENT", "GAME", "FULL", "overtime_winner"),
    "KXNFLSAFETY": ("GAME_EVENT", "GAME", "FULL", "safety"),
    "KXNFLSFTY": ("GAME_EVENT", "GAME", "FULL", "safety"),
    "KXNFL2PTCONV": ("GAME_EVENT", "GAME", "FULL", "two_point_conversion"),
    "KXNFL4DCONV": ("GAME_EVENT", "GAME", "FULL", "fourth_down_conversion"),
    "KXNFL4DOWNCONV": ("GAME_EVENT", "GAME", "FULL", "fourth_down_conversion"),
    "KXNFLLEADCHANGE": ("GAME_EVENT", "GAME", "FULL", "lead_changes"),
    "KXNFLLARGELEAD": ("GAME_EVENT", "GAME", "FULL", "largest_lead"),
    "KXNFLLARGESTLEAD": ("GAME_EVENT", "GAME", "FULL", "largest_lead"),
    "KXNFLCOMEBACK": ("GAME_EVENT", "GAME", "FULL", "comeback"),
    "KXNFLHIGHSCOREQ": ("GAME_EVENT", "GAME", "FULL", "highest_scoring_quarter"),
    "KXNFLNOSCOREQ": ("GAME_EVENT", "GAME", "FULL", "scoreless_quarter"),
    "KXNFLNONQBPASS": ("GAME_EVENT", "GAME", "FULL", "non_qb_pass"),
    "KXNFLDSTTD": ("GAME_EVENT", "GAME", "FULL", "defensive_st_td"),
    "KXNFL1YDPASS": ("GAME_EVENT", "GAME", "FULL", "one_yard_pass"),
    "KXNFLNEXTINT": ("GAME_EVENT", "GAME", "FULL", "next_interception"),
    "KXNFLEQBTTS": ("GAME_EVENT", "GAME", "FULL", "btts"),
    "KXNFLTIES": ("GAME_EVENT", "GAME", "FULL", "tie"),
    "KXNFLPASSYDSH2H": ("PLAYER_H2H", "GAME", "FULL", "passing_yards"),
    "KXNFLRECYDSH2H": ("PLAYER_H2H", "GAME", "FULL", "receiving_yards"),
    "KXNFLRSHYDSH2H": ("PLAYER_H2H", "GAME", "FULL", "rushing_yards"),
    "KXNFLFFH2H": ("PLAYER_H2H", "GAME", "FULL", "fantasy_points"),
    "KXNFLFFPTS": ("PLAYER_STAT", "GAME", "FULL", "fantasy_points"),
    "KXNFLFF40PTS": ("PLAYER_STAT", "GAME", "FULL", "fantasy_points"),
    "KXNFLFF50PTS": ("PLAYER_STAT", "GAME", "FULL", "fantasy_points"),
    "KXNFLCOMBO": ("COMBO", "GAME", "FULL", None),
    "KXNFLPREPACK": ("PARLAY", "GAME", "FULL", None),
    "KXNFLPREPACK1HFT": ("PARLAY", "GAME", "FULL", None),
    "KXNFLPREPACK1Q1H": ("PARLAY", "GAME", "FULL", None),
    "KXNFLPREPACK2ML": ("PARLAY", "GAME", "FULL", None),
    "KXNFLPREPACK3ML": ("PARLAY", "GAME", "FULL", None),
    "KXNFLPREPACKSGP": ("PARLAY", "GAME", "FULL", None),
    "KXNFLPREPACKSGPSPREAD": ("PARLAY", "GAME", "FULL", None),
    "KXMVENFLSINGLEGAME": ("PARLAY", "GAME", "FULL", None),
    "KXMVENFLMULTIGAME": ("PARLAY", "EVENT", "FULL", None),
    "KXMVENFLMULTIGAMEEXTENDED": ("PARLAY", "EVENT", "FULL", None),
    # weekly
    "KXNFLWINSWEEK": ("TEAM_WINS_BY_WEEK", "WEEK", None, "wins"),
    "KXNFLWEEKMOSTPASSYDS": ("WEEK_LEADER", "WEEK", None, "passing_yards"),
    "KXNFLWEEKMOSTRECYDS": ("WEEK_LEADER", "WEEK", None, "receiving_yards"),
    "KXNFLWEEKMOSTRSHYDS": ("WEEK_LEADER", "WEEK", None, "rushing_yards"),
    "KXNFLWEEKCOMPETE": ("PLAYER_AVAILABILITY", "WEEK", None, "plays"),
    "KXNFLPRIMETIME": ("WEEK_EVENT", "WEEK", None, None),
    "KXNFLFFLEADER": ("SEASON_FANTASY", "SEASON", None, "fantasy_rank"),
    "KXNFLFFLEADERTOP": ("SEASON_FANTASY", "SEASON", None, "fantasy_rank"),
    # season / futures
    "KXNFLWINS": ("SEASON_WINS", "SEASON", None, "wins"),
    "KXNFLEXACTWINS": ("SEASON_WINS_EXACT", "SEASON", None, "wins"),
    "KXNFLSEASONPASSYDS": ("SEASON_PLAYER_STAT", "SEASON", None, "passing_yards"),
    "KXNFLSEASONPASSTDS": ("SEASON_PLAYER_STAT", "SEASON", None, "passing_tds"),
    "KXNFLSEASONRECYDS": ("SEASON_PLAYER_STAT", "SEASON", None, "receiving_yards"),
    "KXNFLSEASONREC": ("SEASON_PLAYER_STAT", "SEASON", None, "receptions"),
    "KXNFLSEASONRECTD": ("SEASON_PLAYER_STAT", "SEASON", None, "receiving_tds"),
    "KXNFLSEASONRSHYDS": ("SEASON_PLAYER_STAT", "SEASON", None, "rushing_yards"),
    "KXNFLSEASONRUSHYDS": ("SEASON_PLAYER_STAT", "SEASON", None, "rushing_yards"),
    "KXNFLSEASONRSHTD": ("SEASON_PLAYER_STAT", "SEASON", None, "rushing_tds"),
    "KXNFLTSPEC": ("SEASON_PLAYER_SPECIAL", "SEASON", None, None),
    "KXNFLMOSTRECYDS": ("SEASON_LEADER", "SEASON", None, "receiving_yards"),
    "KXNFLMOSTRSHYDS": ("SEASON_LEADER", "SEASON", None, "rushing_yards"),
    "KXSB": ("SUPER_BOWL_WINNER", "SEASON", None, None),
    "KXNFLAFCCHAMP": ("CONFERENCE_WINNER", "SEASON", None, None),
    "KXNFLNFCCHAMP": ("CONFERENCE_WINNER", "SEASON", None, None),
    "KXNFLPLAYOFF": ("MAKE_PLAYOFFS", "SEASON", None, None),
    "KXNFLPLAYOFFC": ("MAKE_PLAYOFFS", "SEASON", None, None),
    "KXNFLMVP": ("AWARD", "SEASON", None, "mvp"),
    "KXNFLOPOY": ("AWARD", "SEASON", None, "opoy"), "KXNFLOPOTY": ("AWARD", "SEASON", None, "opoy"),
    "KXNFLDPOY": ("AWARD", "SEASON", None, "dpoy"), "KXNFLDPOTY": ("AWARD", "SEASON", None, "dpoy"),
    "KXNFLOROY": ("AWARD", "SEASON", None, "oroy"), "KXNFLOROTY": ("AWARD", "SEASON", None, "oroy"),
    "KXNFLDROY": ("AWARD", "SEASON", None, "droy"), "KXNFLDROTY": ("AWARD", "SEASON", None, "droy"),
    "KXNFLCOTY": ("AWARD", "SEASON", None, "coty"), "KXNFLCPOTY": ("AWARD", "SEASON", None, "cpoy"),
    "KXNFLSBMVP": ("AWARD", "SEASON", None, "sb_mvp"),
}
SERIES_FAMILY.update({
    "KXNFL1SEED": ("SEASON_SEED", "SEASON", None, None), "KXNFLSEED": ("SEASON_SEED", "SEASON", None, None),
    "KXNFLPLAYOFFHOST": ("SEASON_TEAM_EVENT", "SEASON", None, None), "KXNFLROUNDQUAL": ("SEASON_TEAM_EVENT", "SEASON", None, None),
    "KXNFLSTAGEOFELIM": ("SEASON_TEAM_EVENT", "SEASON", None, None), "KXNFLDIVUNDEFEATED": ("SEASON_TEAM_EVENT", "SEASON", None, None),
    "KXNFLLASTTOLOSE": ("SEASON_TEAM_EVENT", "SEASON", None, None), "KXNFLDRAFT1ST": ("SEASON_TEAM_EVENT", "SEASON", None, None),
    "KXNFLH2HWINS": ("SEASON_TEAM_H2H", "SEASON", None, "wins"), "KXNFLDIVISIONORDER": ("SEASON_DIVISION_ORDER", "SEASON", None, None),
    "KXNFLDIVISIONWINS": ("SEASON_DIVISION_STAT", "SEASON", None, "wins"), "KXNFLDIVMOSTWINS": ("SEASON_DIVISION_STAT", "SEASON", None, "wins"),
    "KXNFLDIVLEASTWINS": ("SEASON_DIVISION_STAT", "SEASON", None, "wins"), "KXNFLTEAMPTS": ("SEASON_TEAM_LEADER", "SEASON", None, "points"),
    "KXNFLTEAMDPTS": ("SEASON_TEAM_LEADER", "SEASON", None, "points_allowed"), "KXNFLMATCHUP": ("SEASON_MATCHUP", "SEASON", None, None),
    "KXNFLALLPRO": ("AWARD", "SEASON", None, "all_pro"), "KXNFLAWARDFIN": ("AWARD", "SEASON", None, "finalist"),
    "KXNFLPROOTY": ("AWARD", "SEASON", None, "protector_oty"), "KXNFLWPMOTY": ("AWARD", "SEASON", None, "wpmoy"),
    "KXNFLEXECOTY": ("AWARD", "SEASON", None, "exec_oty"), "KXNFLHALLOFFAME": ("AWARD", "SEASON", None, "hof"),
    "KXNFLT100": ("AWARD", "SEASON", None, "top100"), "KXNFLT100TOP": ("AWARD", "SEASON", None, "top100"),
    "KXNFLFFH2HSEASON": ("SEASON_FANTASY", "SEASON", None, "fantasy_points"), "KXNFLFFHIGHSCORE": ("SEASON_FANTASY", "SEASON", None, "fantasy_points"),
    "KXNFLFFPLAYERHIGH": ("SEASON_FANTASY", "SEASON", None, "fantasy_points"), "KXNFLFFPTSSEASON": ("SEASON_FANTASY", "SEASON", None, "fantasy_points"),
    "KXNFLFANTASYMOST": ("SEASON_FANTASY", "SEASON", None, "fantasy_points"), "KXNFLFFTOP": ("SEASON_FANTASY", "SEASON", None, "fantasy_rank"),
    "KXNFLGAMESPECIALS": ("SEASON_SPECIAL", "SEASON", None, None), "KXNFLBLOWOUT": ("SEASON_SPECIAL", "SEASON", None, None),
    "KXNFLHIGHSCORE": ("SEASON_SPECIAL", "SEASON", None, None), "KXNFL60YARDFGS": ("SEASON_SPECIAL", "SEASON", None, None),
    "KXNFLWINSTREAK": ("SEASON_SPECIAL", "SEASON", None, None), "KXNFLSZNRECORD": ("SEASON_SPECIAL", "SEASON", None, None),
    "KXNFLRECYDSRECORD": ("SEASON_SPECIAL", "SEASON", None, None), "KXNFLSACKRECORD": ("SEASON_SPECIAL", "SEASON", None, None),
    "KXNFLWORSTTOFIRST": ("SEASON_SPECIAL", "SEASON", None, None), "KXNFLLEASTPENALIZED": ("SEASON_SPECIAL", "SEASON", None, None),
    "KXNFLDEBUT": ("PLAYER_ROLE_EVENT", "SEASON", None, None), "KXNFLFIRSTSTART": ("PLAYER_ROLE_EVENT", "SEASON", None, None),
    "KXNFL53MAN": ("PLAYER_ROLE_EVENT", "SEASON", None, None), "KXNFLRETURN": ("PLAYER_ROLE_EVENT", "SEASON", None, None),
    "KXNFLCOMPETE": ("PLAYER_ROLE_EVENT", "SEASON", None, None), "KXNFLEVERYWEEKCOMPETE": ("PLAYER_ROLE_EVENT", "SEASON", None, None),
    "KXSTARTINGQBWEEK1": ("PLAYER_ROLE_EVENT", "SEASON", None, None), "KXNFLDEPTHPOSITIONCLEQB2": ("PLAYER_ROLE_EVENT", "SEASON", None, None),
    "KXNFLNEXTTEAM": ("TRANSACTION_EVENT", "SEASON", None, None), "KXNFLTRADE": ("TRANSACTION_EVENT", "SEASON", None, None),
    "KXNFLRETIRE": ("TRANSACTION_EVENT", "SEASON", None, None), "KXNFLCONTRACTSIZE": ("TRANSACTION_EVENT", "SEASON", None, None),
    "KXNFLGPICKENSCONTRACT": ("TRANSACTION_EVENT", "SEASON", None, None), "KXTRADEOFFNFL": ("TRANSACTION_EVENT", "SEASON", None, None),
    "KXNFLCOACHOUT": ("COACH_EVENT", "SEASON", None, None), "KXNFLCOACHOUTFIRST": ("COACH_EVENT", "SEASON", None, None),
    "KXNFLNEXTCOACHOUT": ("COACH_EVENT", "SEASON", None, None), "KXCOACHOUTNFL": ("COACH_EVENT", "SEASON", None, None),
    "KXCOACHOUTNFLFIRST": ("COACH_EVENT", "SEASON", None, None), "KXNEXTCOACHOUTNFL": ("COACH_EVENT", "SEASON", None, None),
    "KXNFLHIRECOACH": ("COACH_EVENT", "SEASON", None, None), "KXNFLCOACH": ("COACH_EVENT", "SEASON", None, None),
    "KXNEXTNFLCOACH": ("COACH_EVENT", "SEASON", None, None), "KXNFLASSCOACH": ("COACH_EVENT", "SEASON", None, None),
    "KXNFLDRAFTPICK": ("DRAFT", "SEASON", None, None), "KXNFLDRAFTTOP": ("DRAFT", "SEASON", None, None), "KXNFLDRAFT1": ("DRAFT", "SEASON", None, None),
    "KXNFLFIRSTPICK": ("DRAFT", "SEASON", None, None), "KXNFLSUPDRAFTPICK": ("DRAFT", "SEASON", None, None), "KXNFLSDRAFTTOP": ("DRAFT", "SEASON", None, None),
    "KXNFLENDSTREAK": ("SEASON_TEAM_EVENT", "SEASON", None, None), "KXNFLSBMVPDEF": ("AWARD", "SEASON", None, "sb_mvp"),
    "KXNFLSBMVPPOS": ("AWARD", "SEASON", None, "sb_mvp"), "KXNFLSBMVPQB": ("AWARD", "SEASON", None, "sb_mvp"),
    "KXNFCAFCSB": ("SUPER_BOWL_WINNER", "SEASON", None, None), "KXTEAMSINSB": ("SUPER_BOWL_MATCHUP", "SEASON", None, None),
    "KXNFLNEXTINT": ("TEAM_STAT", "WEEK", None, "interceptions"),
    "KXNFLOWNERSTAKE": ("NFL_BUSINESS_EVENT", "EVENT", None, None), "KXNFLROLE": ("NFL_BUSINESS_EVENT", "EVENT", None, None),
    "KXNFLSELLOUT": ("NFL_BUSINESS_EVENT", "EVENT", None, None), "KXNFLSFPRACFIELD": ("NFL_BUSINESS_EVENT", "EVENT", None, None),
    "KXNFLSTADIUM": ("NFL_BUSINESS_EVENT", "EVENT", None, None), "KXNFLVIEWERSHIP": ("NFL_BUSINESS_EVENT", "EVENT", None, None),
    "KXNFLCOMBINE": ("DRAFT", "SEASON", None, None), "KXNFLCOMBINE40": ("DRAFT", "SEASON", None, None), "KXNFLTEAM1POS": ("DRAFT", "SEASON", None, None),
    "KXNFLLASTPICKPOS": ("DRAFT", "SEASON", None, None), "KXNFLHOFINDUCTEES": ("AWARD", "SEASON", None, "hof"), "KXNFLPROBOWL": ("AWARD", "SEASON", None, "pro_bowl"),
    "KXNFLPROBOWLWIN": ("NFL_BUSINESS_EVENT", "EVENT", None, None), "KXNFLLEADERPINT": ("SEASON_LEADER", "SEASON", None, "interceptions_thrown"),
    "KXLEADERPINT": ("SEASON_LEADER", "SEASON", None, "interceptions_thrown"), "KXAFC": ("CONFERENCE_WINNER", "SEASON", None, None),
    "KXNFC": ("CONFERENCE_WINNER", "SEASON", None, None), "KXWPMOTY": ("AWARD", "SEASON", None, "wpmoy"),
})
# Series that share a prefix with NFL tickers but are unrelated (Starbucks, Netflix, budget resolutions,
# soccer confederations, college). The registry builder uses Kalshi's own `tags` to decide NFL membership;
# this list is the classifier's hard stop so nothing here ever gets an NFL family.
NOT_NFL_PREFIXES = ("KXSBUX", "KXSBUDGET", "KXNFLX", "KXAFCA", "KXAFCC", "KXAFCON", "KXHEISMAN", "KXNCAA", "KXCZEF", "KXFOOTBALL1001")
LEADER_RE = re.compile(r"^KXLEADERNFL")
DIVISION_RE = re.compile(r"^KXNFL(AFC|NFC)(EAST|NORTH|SOUTH|WEST)$")


@dataclass
class MarketSemantics:
    ticker: str
    series_ticker: str
    event_ticker: str
    family: str = UNKNOWN
    scope: str | None = None          # GAME / WEEK / SEASON / EVENT
    period: str | None = None         # FULL / 1H / 2H / 1Q..4Q
    stat: str | None = None
    game_date: str | None = None      # YYYY-MM-DD (local game date as encoded by Kalshi)
    away_kalshi: str | None = None
    home_kalshi: str | None = None
    away_team: str | None = None      # nflverse code
    home_team: str | None = None
    team_kalshi: str | None = None    # subject team (spread side, team total, winner)
    team: str | None = None
    player_name: str | None = None
    player_kalshi_id: str | None = None
    team_kalshi_id: str | None = None
    jersey: int | None = None
    threshold: float | None = None    # K such that YES <=> stat >= K (ladders) ; margin > floor for spreads
    floor_strike: float | None = None
    strike_type: str | None = None
    operator: str | None = None       # ">=" (integer stat >= threshold) | ">" (continuous > floor) | "range" | "event"
    range_lo: float | None = None
    range_hi: float | None = None
    yes_meaning: str | None = None
    is_tie_leg: bool = False
    is_none_leg: bool = False
    confidence: float = 0.0
    notes: list = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


def parse_event_ticker(event_ticker: str) -> dict | None:
    """'KXNFLSPREAD-26SEP14DENKC' -> {date, away, home}. None if not a single-game event."""
    if "-" not in event_ticker:
        return None
    suffix = event_ticker.split("-", 1)[1].split("-")[0]
    m = re.match(r"^(\d{2})([A-Z]{3})(\d{2})([A-Z]+?)(TD\d+)?$", suffix)
    if not m:
        return None
    yy, mon, dd, pair, _extra = m.groups()
    if mon not in MONTHS:
        return None
    splits = [(a, pair[len(a):]) for a in KALSHI_TEAM_CODES if pair.startswith(a) and pair[len(a):] in KALSHI_TEAM_CODES]
    if len(splits) != 1:
        return None
    away, home = splits[0]
    return {"game_date": f"20{yy}-{MONTHS[mon]:02d}-{dd}", "away_kalshi": away, "home_kalshi": home}


def _threshold_from_strike(strike_type, floor_strike):
    """Return (threshold K, operator) for ladder-style strikes."""
    if floor_strike is None:
        return None, None
    f = float(floor_strike)
    if strike_type in ("greater", "structured", None):
        # YES iff stat > f. For integer stats that is stat >= floor(f)+1.
        # (older preseason player props carry strike_type="structured" with a x.5 floor)
        return math.floor(f) + 1, ">="
    if strike_type == "greater_or_equal":
        return f, ">="
    if strike_type == "less":
        return f, "<"
    if strike_type == "less_or_equal":
        return f, "<="
    return None, None


def _team_from_suffix(suffix: str, teams: list[str]) -> tuple[str | None, str]:
    """Split '-KC8' or '-NYG' or '-LARDADAMS17' into (team_code, rest) given candidate teams (longest match)."""
    for t in sorted(teams, key=len, reverse=True):
        if suffix.startswith(t):
            return t, suffix[len(t):]
    return None, suffix


def classify(m: dict) -> MarketSemantics:
    ticker = m.get("ticker") or ""
    event_ticker = m.get("event_ticker") or ticker.rsplit("-", 1)[0]
    series = m.get("series_ticker") or event_ticker.split("-")[0]
    s = MarketSemantics(ticker=ticker, series_ticker=series, event_ticker=event_ticker,
                        strike_type=m.get("strike_type"), floor_strike=m.get("floor_strike"))
    cs = m.get("custom_strike") or {}
    if isinstance(cs, dict):
        s.player_kalshi_id = cs.get("football_player")
        s.team_kalshi_id = cs.get("football_team")
    title = m.get("title") or ""
    suffix = ticker[len(event_ticker) + 1:] if ticker.startswith(event_ticker + "-") else ""

    # ---- family lookup
    if series.startswith(NOT_NFL_PREFIXES):
        s.family = "NOT_NFL"; s.confidence = 1.0
        return s
    fam = SERIES_FAMILY.get(series)
    pm = PERIOD_RE.match(series)
    if fam is None and pm:
        period, kind = pm.groups()
        kind = kind or "WINNER"
        fam = {"WINNER": ("PERIOD_WINNER", "GAME", period, None), "SPREAD": ("SPREAD", "GAME", period, "margin"),
               "TOTAL": ("TOTAL", "GAME", period, "total_points"), "TEAMTOTAL": ("TEAM_TOTAL", "GAME", period, "team_points"),
               "BTTS": ("BOTH_TEAMS_SCORE", "GAME", period, "btts"), "TD": ("PERIOD_TD", "GAME", period, "touchdowns"),
               "FT": ("HALF_FULL_RESULT", "GAME", period, None)}[kind]
    if fam is None and series.startswith("KXNFLEXACTWINS"):
        fam = SERIES_FAMILY["KXNFLEXACTWINS"]
    if fam is None and LEADER_RE.match(series):
        fam = ("SEASON_LEADER", "SEASON", None, series.replace("KXLEADERNFL", "").lower())
    if fam is None and DIVISION_RE.match(series):
        fam = ("DIVISION_WINNER", "SEASON", None, None)
    if fam is None and series.startswith("KXNFLWINS-"):
        fam = SERIES_FAMILY["KXNFLWINS"]
    if fam is None and series.startswith("KXNFLDRAFT"):
        fam = ("DRAFT", "SEASON", None, None)
    if fam is None and (series.startswith("KXSB") or series.startswith("KXSUPERBOWL") or series.startswith("KXPERFORMSUPERBOWL") or series.startswith("KXHALFTIME")):
        fam = ("SUPER_BOWL_EVENT", "EVENT", None, None)
    if fam is None:
        if series.startswith("KXNFL") or series.startswith("KXSB") or "NFL" in series:
            s.family = UNKNOWN; s.scope = "EVENT"; s.notes.append("series not in taxonomy")
        else:
            s.family = "NOT_NFL_OR_UNKNOWN"
        s.confidence = 0.0
        return s
    s.family, s.scope, s.period, s.stat = fam
    s.confidence = 0.5

    # ---- single game context
    ev = parse_event_ticker(event_ticker)
    if ev:
        s.game_date, s.away_kalshi, s.home_kalshi = ev["game_date"], ev["away_kalshi"], ev["home_kalshi"]
        s.away_team, s.home_team = KALSHI_TO_NFLVERSE[s.away_kalshi], KALSHI_TO_NFLVERSE[s.home_kalshi]
        s.confidence = 0.8
    elif s.scope == "GAME":
        # series normally single-game, but this event is season/aggregate scoped (e.g. KXNFLTIES-27-4)
        s.scope = "EVENT"; s.notes.append("no single game in event ticker; treated as aggregate/event scope")
        s.confidence = 0.6

    teams_in_game = [t for t in (s.away_kalshi, s.home_kalshi) if t]
    K, op = _threshold_from_strike(s.strike_type, s.floor_strike)
    fam_name = s.family

    if fam_name in ("GAME_WINNER", "PERIOD_WINNER"):
        if suffix == "TIE":
            s.is_tie_leg = True; s.yes_meaning = f"{s.period or 'FULL'} ends tied"; s.operator = "event"
        else:
            s.team_kalshi = suffix if suffix in KALSHI_TEAM_CODES else None
            s.operator = "event"; s.yes_meaning = f"{s.team_kalshi} wins {s.period or 'game'}"
        if s.team_kalshi or s.is_tie_leg:
            s.confidence = 0.95
    elif fam_name == "SPREAD":
        t, rest = _team_from_suffix(suffix, teams_in_game or KALSHI_TEAM_CODES)
        s.team_kalshi = t
        s.threshold, s.operator = s.floor_strike, ">"   # margin > floor (7.5)
        s.yes_meaning = f"{t} wins {s.period or 'game'} by more than {s.floor_strike}"
        if t and s.floor_strike is not None and s.strike_type == "greater":
            s.confidence = 0.95
    elif fam_name == "TOTAL":
        s.threshold, s.operator = K, ">="
        s.yes_meaning = f"{s.period or 'game'} total points >= {K}"
        if K is not None:
            s.confidence = 0.95
    elif fam_name == "TEAM_TOTAL":
        t, rest = _team_from_suffix(suffix, teams_in_game or KALSHI_TEAM_CODES)
        s.team_kalshi = t; s.threshold, s.operator = K, ">="
        s.yes_meaning = f"{t} {s.period or 'game'} points >= {K}"
        if t and K is not None:
            s.confidence = 0.95
    elif fam_name == "WIN_MARGIN_BUCKET":
        wm = (cs.get("Winning Margin") if isinstance(cs, dict) else None) or ""
        t, rest = _team_from_suffix(suffix, teams_in_game or KALSHI_TEAM_CODES)
        if wm.lower() == "tie" or suffix == "TIE":
            s.is_tie_leg = True; s.operator = "event"; s.yes_meaning = "game ends tied"; s.confidence = 0.95
        else:
            mm = re.match(r"^(\d+)\s*to\s*(\d+)$", wm) or re.match(r"^(\d+)\s*(?:\+|or more)?$", wm)
            s.team_kalshi = t; s.operator = "range"
            if mm:
                s.range_lo = float(mm.group(1)); s.range_hi = float(mm.group(2)) if mm.lastindex == 2 else None
                s.yes_meaning = f"{t} wins by {s.range_lo}..{s.range_hi if s.range_hi is not None else 'inf'} (inclusive)"
                s.confidence = 0.9
            else:
                s.notes.append(f"unparsed winning margin '{wm}'"); s.confidence = 0.4
    elif fam_name == "BOTH_TEAMS_SCORE_N":
        s.threshold, s.operator = K, ">="; s.yes_meaning = f"both teams score >= {K}"; s.confidence = 0.9 if K else 0.4
    elif fam_name == "TOTAL_TD":
        s.threshold, s.operator = K, ">="; s.yes_meaning = f"total touchdowns >= {K}"; s.confidence = 0.9 if K else 0.4
    elif fam_name == "RACE_TO_N":
        # event ticker carries the target: KXNFLRACE-26SEP14DENKC-35 ; market suffix is team code or NONE
        mm = re.search(r"-(\d+)$", event_ticker)
        if mm and (suffix in KALSHI_TEAM_CODES or suffix == "NONE"):
            s.threshold = float(mm.group(1)); s.team_kalshi = suffix if suffix != "NONE" else None
            s.is_none_leg = suffix == "NONE"; s.operator = "event"
            s.yes_meaning = f"{'neither' if s.is_none_leg else s.team_kalshi} first to {s.threshold} points"; s.confidence = 0.9
        else:
            s.notes.append("race target/team not parsed"); s.confidence = 0.4
    elif fam_name in ("FIRST_TD_TEAM",):
        s.team_kalshi = suffix if suffix in KALSHI_TEAM_CODES else None; s.is_none_leg = suffix == "NONE"; s.operator = "event"
        s.yes_meaning = "no TD" if s.is_none_leg else f"{s.team_kalshi} scores first TD"; s.confidence = 0.9
    elif fam_name in ("FIRST_TD_SCORER", "NEXT_TD_SCORER"):
        s.operator = "event"
        if suffix == "NONE":
            s.is_none_leg = True; s.yes_meaning = "no touchdown"; s.confidence = 0.9
        else:
            _parse_player(s, suffix, title, teams_in_game, has_threshold=False)
            s.yes_meaning = f"{s.player_name} scores {'first' if fam_name == 'FIRST_TD_SCORER' else 'next'} TD"
    elif fam_name == "PLAYER_STAT":
        has_k = bool(re.search(r"-\d+$", suffix))
        _parse_player(s, suffix, title, teams_in_game, has_threshold=has_k)
        if K is None and s.stat == "touchdowns" and ("Anytime" in title or series == "KXNFLANYTD"):
            K = 1  # anytime-TD contracts carry no numeric strike: YES iff touchdowns >= 1
        s.threshold, s.operator = K, ">="
        s.yes_meaning = f"{s.player_name} {s.stat} >= {K}"
        if K is None:
            s.confidence = min(s.confidence, 0.4); s.notes.append("no strike")
    elif fam_name == "HALF_FULL_RESULT":
        r1 = cs.get("1st Half Result") if isinstance(cs, dict) else None
        r2 = cs.get("Fulltime Result") if isinstance(cs, dict) else None
        s.operator = "event"; s.yes_meaning = f"{r1} / {r2}"; s.confidence = 0.85 if r1 and r2 else 0.4
    elif fam_name == "SEASON_WINS":
        s.threshold, s.operator = K, ">="
        s.team_kalshi = next((t for t in KALSHI_TEAM_CODES if event_ticker.endswith(t)), None)
        s.yes_meaning = f"{s.team_kalshi} season wins >= {K}"; s.confidence = 0.9 if K is not None else 0.4
    elif fam_name == "TEAM_WINS_BY_WEEK":
        t, rest = _team_from_suffix(suffix, KALSHI_TEAM_CODES)
        s.team_kalshi = t; s.threshold, s.operator = K, ">="
        mm = re.search(r"W(\d+)$", event_ticker)
        s.notes.append(f"through_week={mm.group(1)}" if mm else "week unparsed")
        s.yes_meaning = f"{t} wins >= {K} through week {mm.group(1) if mm else '?'}"; s.confidence = 0.85 if K is not None else 0.4
    elif fam_name == "SEASON_PLAYER_STAT":
        _parse_player(s, suffix, title, KALSHI_TEAM_CODES, has_threshold=True)
        s.threshold, s.operator = K, ">="; s.yes_meaning = f"{s.player_name} season {s.stat} >= {K}"
    else:
        s.operator = "event"; s.yes_meaning = title
        s.confidence = max(s.confidence, 0.6)
    if s.team_kalshi:
        s.team = KALSHI_TO_NFLVERSE.get(s.team_kalshi)
    return s


def _parse_player(s: MarketSemantics, suffix: str, title: str, teams: list[str], has_threshold: bool):
    """'LARDADAMS17-120' + title 'Davante Adams: 120+ receiving yards'."""
    token = suffix.rsplit("-", 1)[0] if has_threshold and "-" in suffix else suffix
    t, rest = _team_from_suffix(token, teams)
    s.team_kalshi = t
    mm = re.match(r"^([A-Z])([A-Z]+?)(\d+)$", rest)
    if mm:
        s.jersey = int(mm.group(3))
    # "Davante Adams: 120+ receiving yards"  vs  "Seattle vs New England: 4th TD: Sam Darnold" (next-TD family)
    parts = [x.strip() for x in title.split(":")] if ":" in title else []
    name = None
    if parts:
        name = parts[-1] if (len(parts) >= 3 or re.search(r"\bTD\b", parts[0])) else parts[0]
        if " vs " in name or re.match(r"^\d", name):
            name = None
    if not name:
        mm2 = re.match(r"^(.*?)\s+(records|scores|to |wins)", title)
        name = mm2.group(1).strip() if mm2 else None
    s.player_name = name
    if name and t:
        s.confidence = max(s.confidence, 0.9)
    elif name:
        s.confidence = max(s.confidence, 0.7); s.notes.append("player team not parsed")
    else:
        s.confidence = min(s.confidence, 0.3); s.notes.append("player name not parsed")


def is_single_game_family(sem: MarketSemantics) -> bool:
    return sem.scope == "GAME" and sem.game_date is not None
