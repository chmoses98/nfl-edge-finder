from nfl_edge.handicap import schedule_kickoffs as K

CSV = """game_id,season,game_type,week,gameday,weekday,gametime,away_team,home_team
2026_01_NE_SEA,2026,REG,1,2026-09-09,Wednesday,20:20,NE,SEA
2026_03_ATL_GB,2026,REG,3,2026-09-27,Sunday,13:00,NE,JAX
2026_04_JAX_CIN,2026,REG,4,2026-10-04,Sunday,13:00,JAX,CIN
2026_05_LA_SF,2026,REG,5,2026-10-11,Sunday,16:25,LA,SF
2026_05_X_Y,2026,REG,5,2026-10-11,Sunday,,BUF,MIA
2025_01_A_B,2025,REG,1,2025-09-07,Sunday,13:00,BUF,MIA
"""


def test_gametime_is_eastern_and_converted_to_utc():
    k = K.kickoffs_from_schedule(CSV, 2026)
    assert k["26SEP09NESEA"] == "2026-09-10T00:20:00+00:00"        # 20:20 ET (EDT) is 00:20Z the next day
    assert k["26OCT04JAXCIN"] == "2026-10-04T17:00:00+00:00"


def test_a_game_without_a_time_gets_no_kickoff_and_other_seasons_are_ignored():
    k = K.kickoffs_from_schedule(CSV, 2026)
    assert "26OCT11BUFMIA" not in k and not any(x.startswith("25") for x in k)


def test_ticker_keys_with_kalshi_team_codes_resolve():
    assert K.game_key_from_ticker_key("26OCT04JACCIN") == "26OCT04JAXCIN"      # Kalshi JAC, nflverse JAX
    assert K.game_key_from_ticker_key("26OCT11LARSF") == "26OCT11LASF"         # Kalshi LAR, nflverse LA
    assert K.game_key_from_ticker_key("26SEP27NEJAC") == "26SEP27NEJAX"        # NE+JAC, not NEJ+AC
    assert K.game_key_from_ticker_key("26SEP10SFLAR") == "26SEP10SFLA"
    assert K.game_key_from_ticker_key("garbage") is None


def test_a_close_kickoff_wins_the_schedule_fills_gaps_and_conflicts_are_reported():
    sched = K.kickoffs_from_schedule(CSV, 2026)
    got, rep = K.kickoffs_for_games(["26OCT04JACCIN", "26SEP09NESEA", "26OCT18XXXYYY"],
                                    {"26SEP09NESEA": "2026-09-10T00:25:00+00:00"}, sched)
    assert got["26SEP09NESEA"] == "2026-09-10T00:25:00+00:00"                 # the close wins ...
    assert rep["conflicts"] and rep["conflicts"][0]["schedule"] == "2026-09-10T00:20:00+00:00"   # ... and the disagreement is reported
    assert got["26OCT04JACCIN"] == "2026-10-04T17:00:00+00:00" and rep["filled_from_schedule"] == ["26OCT04JACCIN"]
    assert "26OCT18XXXYYY" not in got                                           # never a guess
