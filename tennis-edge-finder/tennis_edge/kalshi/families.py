"""Canonical Kalshi tennis market FAMILIES and the series that belong to each.

Derived from the live series catalogue (2026-09-10/11 snapshots, 143 tennis-tagged series) and the
market records of every family (165k live + archived markets). A series not listed here is an
UNKNOWN family: discovery surfaces it as a coverage failure (health gate TENNIS-2) -- it is never
silently ignored.

Family = what the payoff depends on. Scope = which object the payoff is a function of.
  MATCH scope   -> priced from one MatchDistribution (tennis_edge.sim.analytic)
  TOURNAMENT scope -> priced from a draw simulation (tennis_edge.futures)
  SEASON/OTHER scope -> not priceable from match/draw distributions (rankings, brand deals, mentions)
"""
from __future__ import annotations

# family -> dict(scope, payoff, discipline, projectable, note)
FAMILIES = {
    "MATCH_WINNER": {"scope": "MATCH", "projectable": True},
    "SET_WINNER": {"scope": "MATCH", "projectable": True},
    "EXACT_SET_SCORE": {"scope": "MATCH", "projectable": True},
    "GAME_SPREAD": {"scope": "MATCH", "projectable": True},
    "TOTAL_GAMES": {"scope": "MATCH", "projectable": True},
    "TOTAL_SETS": {"scope": "MATCH", "projectable": True},
    "SET_SPREAD": {"scope": "MATCH", "projectable": True},
    "TIEBREAK_OCCURS": {"scope": "MATCH", "projectable": True},
    "ANY_SET_WINNER": {"scope": "MATCH", "projectable": True},
    "PLAYER_ACES": {"scope": "MATCH", "projectable": False, "note": "needs ace-rate model; not built"},
    "GAME_WINNER_INPLAY": {"scope": "MATCH_INPLAY", "projectable": False, "note": "in-play game markets; pregame engine does not price"},
    "TOURNAMENT_WINNER": {"scope": "TOURNAMENT", "projectable": True},
    "ROUND_ADVANCE": {"scope": "TOURNAMENT", "projectable": True},
    "ROUND_OF_ELIMINATION": {"scope": "TOURNAMENT", "projectable": True},
    "NATIONALITY_STAGE_COUNT": {"scope": "TOURNAMENT", "projectable": False, "note": "draw-sim derivable later"},
    "NATIONALITY_WINNER": {"scope": "TOURNAMENT", "projectable": False},
    "SET_SWEEP": {"scope": "TOURNAMENT", "projectable": False},
    "COMBO_TOURNAMENT_WINNERS": {"scope": "TOURNAMENT_COMBO", "projectable": False, "note": "product of two draws; buildable"},
    "TEAM_COMPETITION_WINNER": {"scope": "TOURNAMENT", "projectable": False, "note": "team-tie model not built"},
    "TEAM_ADVANCE": {"scope": "TOURNAMENT", "projectable": False},
    "SEASON_RANKING": {"scope": "SEASON", "projectable": False},
    "SEASON_QUALIFICATION": {"scope": "SEASON", "projectable": False},
    "SEASON_MAJORS": {"scope": "SEASON", "projectable": False},
    "PLAYER_PARTICIPATION": {"scope": "OTHER", "projectable": False},
    "CAREER_OR_NOVELTY": {"scope": "OTHER", "projectable": False},
    "NOT_TENNIS": {"scope": "OTHER", "projectable": False, "note": "tagged Tennis by the exchange but not tennis (pickleball)"},
}

# series ticker -> (family, tour, level, discipline)
#   tour: ATP / WTA / MIXED / ANY;  level: TOUR / CHALLENGER / ITF / SLAM / TEAM / EXHIBITION / ANY
SERIES = {
    # ---- match winner
    "KXATPMATCH": ("MATCH_WINNER", "ATP", "TOUR", "singles"),
    "KXWTAMATCH": ("MATCH_WINNER", "WTA", "TOUR", "singles"),
    "KXATPCHALLENGERMATCH": ("MATCH_WINNER", "ATP", "CHALLENGER", "singles"),
    "KXCHALLENGERMATCH": ("MATCH_WINNER", "ATP", "CHALLENGER", "singles"),
    "KXWTACHALLENGERMATCH": ("MATCH_WINNER", "WTA", "CHALLENGER", "singles"),
    "KXITFMATCH": ("MATCH_WINNER", "ATP", "ITF", "singles"),
    "KXITFWMATCH": ("MATCH_WINNER", "WTA", "ITF", "singles"),
    "KXATPGAME": ("MATCH_WINNER", "ATP", "TOUR", "singles"),
    "KXWTAGAME": ("MATCH_WINNER", "WTA", "TOUR", "singles"),
    "KXUNITEDCUPMATCH": ("MATCH_WINNER", "MIXED", "TEAM", "singles"),
    "KXDAVISCUPMATCH": ("MATCH_WINNER", "ATP", "TEAM", "singles"),
    "KXTENNISEXHIBITION": ("MATCH_WINNER", "ANY", "EXHIBITION", "singles"),
    "KXEXHIBITIONMEN": ("MATCH_WINNER", "ATP", "EXHIBITION", "singles"),
    "KXEXHIBITIONWOMEN": ("MATCH_WINNER", "WTA", "EXHIBITION", "singles"),
    "KXSIXKINGSSLAMMATCH": ("MATCH_WINNER", "ATP", "EXHIBITION", "singles"),
    "KXSIXKINGSMATCH": ("MATCH_WINNER", "ATP", "EXHIBITION", "singles"),
    "KXBATTLEOFSEXES": ("MATCH_WINNER", "MIXED", "EXHIBITION", "singles"),
    "KXBATTLEOFSEXESSET": ("SET_WINNER", "MIXED", "EXHIBITION", "singles"),
    "KXATPDOUBLES": ("MATCH_WINNER", "ATP", "TOUR", "doubles"),
    "KXWTADOUBLES": ("MATCH_WINNER", "WTA", "TOUR", "doubles"),
    "KXATPCHALLENGERDOUBLES": ("MATCH_WINNER", "ATP", "CHALLENGER", "doubles"),
    "KXITFDOUBLES": ("MATCH_WINNER", "ATP", "ITF", "doubles"),
    "KXITFWDOUBLES": ("MATCH_WINNER", "WTA", "ITF", "doubles"),
    "KXMIXEDDOUBLESMATCH": ("MATCH_WINNER", "MIXED", "TOUR", "mixed"),
    "KXPICKLEBALLMATCH": ("NOT_TENNIS", "ANY", "ANY", "singles"),
    # ---- match derivatives
    "KXATPSETWINNER": ("SET_WINNER", "ATP", "ANY", "singles"),
    "KXWTASETWINNER": ("SET_WINNER", "WTA", "ANY", "singles"),
    "KXATPANYSET": ("ANY_SET_WINNER", "ATP", "ANY", "singles"),
    "KXATPEXACTMATCH": ("EXACT_SET_SCORE", "ATP", "ANY", "singles"),
    "KXWTAEXACTMATCH": ("EXACT_SET_SCORE", "WTA", "ANY", "singles"),
    "KXATPEXACTSETS": ("EXACT_SET_SCORE", "ATP", "ANY", "singles"),
    "KXATPGSPREAD": ("GAME_SPREAD", "ATP", "ANY", "singles"),
    "KXATPGAMESPREAD": ("GAME_SPREAD", "ATP", "ANY", "singles"),
    "KXATPGTOTAL": ("TOTAL_GAMES", "ATP", "ANY", "singles"),
    "KXATPGAMETOTAL": ("TOTAL_GAMES", "ATP", "ANY", "singles"),
    "KXWTAGTOTAL": ("TOTAL_GAMES", "WTA", "ANY", "singles"),
    "KXATPTOTALSETS": ("TOTAL_SETS", "ATP", "ANY", "singles"),
    "KXATPSSPREAD": ("SET_SPREAD", "ATP", "ANY", "singles"),
    "KXATPTIEBREAK": ("TIEBREAK_OCCURS", "ATP", "ANY", "singles"),
    "KXATPACES": ("PLAYER_ACES", "ATP", "ANY", "singles"),
    "KXWTAACES": ("PLAYER_ACES", "WTA", "ANY", "singles"),
    "KXATPGWINNER": ("GAME_WINNER_INPLAY", "ATP", "ANY", "singles"),
    "KXATPS1GWINNER": ("GAME_WINNER_INPLAY", "ATP", "ANY", "singles"),
    "KXATPS2GWINNER": ("GAME_WINNER_INPLAY", "ATP", "ANY", "singles"),
    "KXATPS3GWINNER": ("GAME_WINNER_INPLAY", "ATP", "ANY", "singles"),
    "KXATPS4GWINNER": ("GAME_WINNER_INPLAY", "ATP", "ANY", "singles"),
    "KXATPS5GWINNER": ("GAME_WINNER_INPLAY", "ATP", "ANY", "singles"),
    # ---- tournament scope
    "KXATP": ("TOURNAMENT_WINNER", "ATP", "ANY", "singles"),
    "KXWTA": ("TOURNAMENT_WINNER", "WTA", "ANY", "singles"),
    "KXATPMEN": ("TOURNAMENT_WINNER", "ATP", "ANY", "singles"),
    "KXWTATOURNWIN": ("CAREER_OR_NOVELTY", "WTA", "ANY", "singles"),  # "wins any WTA tournament in 2026"
    "KXATPADVANCE": ("ROUND_ADVANCE", "ATP", "ANY", "singles"),
    "KXWTAADVANCE": ("ROUND_ADVANCE", "WTA", "ANY", "singles"),
    "KXATPROUND": ("ROUND_ADVANCE", "ATP", "ANY", "singles"),
    "KXWTAROE": ("ROUND_OF_ELIMINATION", "WTA", "ANY", "singles"),
    "KXATPNATSTAGE": ("NATIONALITY_STAGE_COUNT", "ATP", "ANY", "singles"),
    "KXWTANATSTAGE": ("NATIONALITY_STAGE_COUNT", "WTA", "ANY", "singles"),
    "KXATPNATWINNER": ("NATIONALITY_WINNER", "ATP", "ANY", "singles"),
    "KXATPSETSWEEP": ("SET_SWEEP", "ATP", "ANY", "singles"),
    "KXATPWTA": ("COMBO_TOURNAMENT_WINNERS", "MIXED", "ANY", "singles"),
    "KXATPGRANDSLAMFIELD": ("TOURNAMENT_WINNER", "ATP", "SLAM", "singles"),
    "KXMIXEDDOUBLES": ("TOURNAMENT_WINNER", "MIXED", "SLAM", "mixed"),
    "KXIWMENDOUBLES": ("TOURNAMENT_WINNER", "ATP", "TOUR", "doubles"),
    "KXROMENSDOUBLES": ("TOURNAMENT_WINNER", "ATP", "TOUR", "doubles"),
    "KXDAVISCUP": ("TEAM_COMPETITION_WINNER", "ATP", "TEAM", "team"),
    "KXUNITEDCUP": ("TEAM_COMPETITION_WINNER", "MIXED", "TEAM", "team"),
    "KXLAVERCUP": ("TEAM_COMPETITION_WINNER", "ATP", "TEAM", "team"),
    "KXDAVISCUPADVANCE": ("TEAM_ADVANCE", "ATP", "TEAM", "team"),
    "KXUNITEDCUPADVANCE": ("TEAM_ADVANCE", "MIXED", "TEAM", "team"),
    "KXSIXKINGSSLAM": ("TOURNAMENT_WINNER", "ATP", "EXHIBITION", "singles"),
    "KXSIXKINGSQUARTER": ("ROUND_ADVANCE", "ATP", "EXHIBITION", "singles"),
    "KXSIXKINGSSEMI": ("ROUND_ADVANCE", "ATP", "EXHIBITION", "singles"),
    "KXATPFINALS": ("TOURNAMENT_WINNER", "ATP", "TOUR", "singles"),
    "KXWTAFINALS": ("TOURNAMENT_WINNER", "WTA", "TOUR", "singles"),
    "KXATPNEXTGEN": ("TOURNAMENT_WINNER", "ATP", "TOUR", "singles"),
    # ---- season scope
    "KXATP1RANK": ("SEASON_RANKING", "ATP", "ANY", "singles"),
    "KXATPRANK": ("SEASON_RANKING", "ATP", "ANY", "singles"),
    "KXWTA1RANK": ("SEASON_RANKING", "WTA", "ANY", "singles"),
    "KXATPFINALSQUAL": ("SEASON_QUALIFICATION", "ATP", "ANY", "singles"),
    "KXWTAFINALSQUAL": ("SEASON_QUALIFICATION", "WTA", "ANY", "singles"),
    "KXATPGRANDSLAM": ("SEASON_MAJORS", "ATP", "SLAM", "singles"),
    "KXWTAGRANDSLAM": ("SEASON_MAJORS", "WTA", "SLAM", "singles"),
    "KXTENNISGRANDSLAM": ("SEASON_MAJORS", "ANY", "SLAM", "singles"),
    "KXGRANDSLAM": ("SEASON_MAJORS", "ANY", "SLAM", "singles"),
    # ---- participation / novelty
    "KXATPRETURN": ("PLAYER_PARTICIPATION", "ATP", "ANY", "singles"),
    "KXATPCOMPETE": ("PLAYER_PARTICIPATION", "ATP", "ANY", "singles"),
    "KXATPRETIRE": ("PLAYER_PARTICIPATION", "ATP", "ANY", "singles"),
    "KXCALCFO": ("PLAYER_PARTICIPATION", "ATP", "ANY", "singles"),
    "KXWTASERENA": ("PLAYER_PARTICIPATION", "WTA", "ANY", "singles"),
    "KXSINNERFINISH": ("PLAYER_PARTICIPATION", "ATP", "ANY", "singles"),
    "KXPLAYERDEAL": ("CAREER_OR_NOVELTY", "ANY", "ANY", "singles"),
    "KXALCARAZCOACH": ("CAREER_OR_NOVELTY", "ATP", "ANY", "singles"),
    "KXHONEYDEUCE": ("CAREER_OR_NOVELTY", "ANY", "ANY", "singles"),
    "KXATPNOVAK25": ("CAREER_OR_NOVELTY", "ATP", "ANY", "singles"),
    "KXGRANDSLAMJFONSECA": ("CAREER_OR_NOVELTY", "ATP", "ANY", "singles"),
    "KXGRANDSLAMSINNERALCARAZ": ("CAREER_OR_NOVELTY", "ATP", "ANY", "singles"),
    "KXTENNISMAJORDJOKOVIC": ("CAREER_OR_NOVELTY", "ATP", "ANY", "singles"),
    "KXFIRSTUSOPEN": ("CAREER_OR_NOVELTY", "ANY", "SLAM", "singles"),
    "KXGOLFTENNISMAJORS": ("CAREER_OR_NOVELTY", "ANY", "ANY", "singles"),
}

# Tournament-specific winner series (one series per event/year). Grouped by the same family.
_TOURNAMENT_WINNER_SERIES = {
    # slams
    "KXAOMEN": "ATP", "KXAOMENSINGLES": "ATP", "KXAOWOMEN": "WTA",
    "KXFOMEN": "ATP", "KXFOMENSINGLES": "ATP", "KXFOPENMENSINGLE": "ATP", "KXFOWOMEN": "WTA", "KXFOWOMENSINGLES": "WTA", "KXFOPENWMENSINGLE": "WTA",
    "KXWIMMEN": "ATP", "KXWMENSINGLES": "ATP", "KXWIMWOMEN": "WTA", "KXWWOMENSINGLES": "WTA",
    "KXUSOMENSINGLES": "ATP", "KXUSOWOMENSINGLES": "WTA",
    # masters / 1000 / 500 / 250
    "KXIWMEN": "ATP", "KXIWWOMEN": "WTA", "KXATPIWO": "ATP", "KXWTAIWO": "WTA",
    "KXMOMEN": "ATP", "KXMOWOMEN": "WTA", "KXATPMIA": "ATP", "KXWTAMIA": "WTA",
    "KXMCMEN": "ATP", "KXMCMMEN": "ATP", "KXATPMC": "ATP",
    "KXMADMEN": "ATP", "KXMADWOMEN": "WTA", "KXATPMAD": "ATP", "KXWTAMAD": "WTA",
    "KXATPIT": "ATP", "KXWTAIT": "WTA",
    "KXATPAMT": "ATP", "KXATPMCO": "ATP", "KXROMENSSINGLES": "ATP", "KXQEMOMENSSINGLES": "ATP", "KXO13MENSINGLES": "ATP",
    "KXDDFMENSINGLES": "ATP", "KXDDFWOMENSINGLES": "WTA", "KXATPWDDF": "ATP", "KXWTADDF": "WTA",
    "KXQOWOMENSINGLES": "WTA", "KXWTAATX": "WTA", "KXWTAMOA": "WTA",
}
for _tk, _tour in _TOURNAMENT_WINNER_SERIES.items():
    SERIES[_tk] = ("TOURNAMENT_WINNER", _tour, "ANY", "singles")


def series_family(series_ticker: str) -> tuple[str, str, str, str] | None:
    return SERIES.get(series_ticker)


def unknown_series(series_tickers) -> list[str]:
    """Series present on the exchange but absent from SERIES -> TENNIS-2 coverage failure."""
    return sorted(t for t in series_tickers if t not in SERIES)
