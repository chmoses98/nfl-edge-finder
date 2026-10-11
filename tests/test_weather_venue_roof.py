"""Weather context: the venue a forecast is fetched for, and the roof that decides whether it can matter.

Two upstream defects this pins (weather is NOT_IN_MODEL; this is packet/context data only):

1. nflverse leaves `roof` blank for a retractable-roof stadium until the open/closed call is made. A blank
   roof was read as outdoors, so State Farm Stadium got an 85F / 25 mph desert forecast flagged material.
   The physical roof type now comes from config/stadiums.json: a dome never gets outdoor weather, and a
   retractable stadium with an unannounced roof shows the outside forecast as context, never material.
2. nflverse marks 2026_05_PHI_JAX (Tottenham Hotspur Stadium, London) as a Home game with the home team's
   stadium id, so the capture asked the US weather service about Jacksonville. The venue is now checked by
   the scheduled stadium name regardless of the Neutral flag.
"""
import csv
import importlib.util
import io
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from nfl_edge.context import venues as VEN  # noqa: E402
from nfl_edge.handicap import packet as P  # noqa: E402
from nfl_edge.handicap import render as R  # noqa: E402

STADIUMS = VEN.load_stadiums()


def _load(rel, name):
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, rel))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


CC = _load("scripts/data/context_capture.py", "_context_capture_venue_under_test")


# ===================================================================== config: authoritative roof type

def test_every_team_has_an_authoritative_roof_type_stadium_id_and_provenance():
    raw = json.load(open(os.path.join(ROOT, "config", "stadiums.json")))
    assert "roof_type" in raw["_roof_type_note"] and "nflverse" in raw["_roof_type_note"]
    assert len(STADIUMS) == 32
    for team, st in STADIUMS.items():
        assert st.get("roof_type") in VEN.ROOF_TYPES, team
        assert st.get("stadium_id"), team


def test_roof_types_match_the_physical_stadiums():
    by = {rt: {t for t, st in STADIUMS.items() if st["roof_type"] == rt} for rt in VEN.ROOF_TYPES}
    assert by["retractable"] == {"ARI", "ATL", "DAL", "HOU", "IND"}
    assert by["dome"] == {"DET", "LA", "LAC", "LV", "MIN", "NO"}
    assert len(by["open"]) == 21


# ===================================================================== venue check

@pytest.mark.parametrize("home,stadium,sid,verdict", [
    ("JAX", "Tottenham Hotspur Stadium", "JAX00", VEN.OTHER_VENUE),     # nflverse: location Home, home id
    ("WAS", "Tottenham Hotspur Stadium", "LON02", VEN.OTHER_VENUE),     # nflverse: Neutral
    ("ATL", "Bernabeu", "MAD01", VEN.OTHER_VENUE),
    ("JAX", "EverBank Stadium", "JAX00", VEN.HOME_STADIUM),
    ("HOU", "Reliant Stadium", "HOU00", VEN.HOME_STADIUM),              # nflverse 2026 uses the old name
    ("SF", "Levi’s Stadium", "SFO01", VEN.HOME_STADIUM),           # curly apostrophe
    ("CHI", "", "", VEN.UNVERIFIED),
    ("XXX", "Somewhere", "X00", VEN.NO_CONFIG),
])
def test_venue_check_ignores_the_neutral_flag_and_uses_the_scheduled_stadium(home, stadium, sid, verdict):
    v = VEN.venue_check(home, stadium, sid, STADIUMS)
    assert v["venue"] == verdict
    if verdict == VEN.OTHER_VENUE:
        assert v["reason"] and stadium in v["reason"]


# ===================================================================== packet: weather_state

KICK = "2026-10-11T20:25:00+00:00"


def _row(game_id, home, roof, stadium, *, temp=85, wind="25 mph", pop=0, neutral=False):
    per = {"startTime": "2026-10-11T20:00:00+00:00", "endTime": "2026-10-11T21:00:00+00:00",
           "temperature": temp, "windSpeed": wind, "windDirection": "W", "shortForecast": "Sunny",
           "probabilityOfPrecipitation": {"value": pop}}
    return {"game_id": game_id, "home_team": home, "kickoff_utc": KICK, "roof": roof, "surface": "grass",
            "stadium_schedule": stadium, "stadium_config": STADIUMS[home]["stadium"], "neutral": neutral,
            "nws": {"generated": "2026-10-11T10:00:00+00:00", "periods": [per]}}


def _ws(row):
    return P.weather_state([{"run_id": "20261011T120000Z", "weather": [row]}], row["game_id"])


def test_retractable_stadium_with_unannounced_roof_is_context_never_material():
    w = _ws(_row("2026_06_SEA_ARI", "ARI", "", "State Farm Stadium"))
    assert w["roof_type"] == "retractable" and w["roof_status"] == "UNKNOWN"
    assert w["temperature_f"] == 85 and w["wind"] == "25 mph", "the outside forecast stays as context"
    assert w["material"] is False
    assert "retractable" in w["note"]


def test_retractable_stadium_with_unannounced_roof_never_material_even_when_it_changed():
    prev = _row("2026_06_SEA_ARI", "ARI", "", "State Farm Stadium", wind="5 mph")
    cur = _row("2026_06_SEA_ARI", "ARI", "", "State Farm Stadium", wind="30 mph", pop=90)
    w = P.weather_state([{"run_id": "a", "weather": [prev]}, {"run_id": "b", "weather": [cur]}], cur["game_id"])
    assert w["changed_since_previous_capture"] is True and w["material"] is False


def test_retractable_stadium_with_the_roof_announced_open_is_judged_as_outdoors():
    w = _ws(_row("2026_06_SEA_ARI", "ARI", "open", "State Farm Stadium"))
    assert w["roof_status"] == "OPEN" and w["material"] is True


def test_retractable_stadium_with_the_roof_announced_closed_gets_no_weather():
    w = _ws(_row("2026_06_SEA_ATL", "ATL", "closed", "Mercedes-Benz Stadium"))
    assert w["roof_status"] == "CLOSED" and w["material"] is False and "temperature_f" not in w


@pytest.mark.parametrize("roof", ["", "outdoors", "dome"])
def test_a_dome_never_gets_outdoor_weather_whatever_nflverse_says(roof):
    w = _ws(_row("2026_06_GB_DET", "DET", roof, "Ford Field"))
    assert w["roof_type"] == "dome" and w["roof_status"] == "CLOSED"
    assert w["material"] is False and "temperature_f" not in w and "wind" not in w


def test_an_open_stadium_with_a_windy_forecast_is_still_material():
    w = _ws(_row("2026_06_GB_CHI", "CHI", "outdoors", "Soldier Field"))
    assert w["roof_type"] == "open" and w["roof_status"] == "OPEN" and w["material"] is True


def test_an_open_stadium_with_a_blank_roof_is_still_treated_as_outdoors():
    w = _ws(_row("2026_06_GB_CHI", "CHI", "", "Soldier Field"))
    assert w["roof_status"] == "OPEN" and w["material"] is True


def test_a_game_away_from_the_home_stadium_never_shows_the_home_stadium_forecast():
    """A row captured before the fix carries Jacksonville's forecast for a London game; it must not be shown."""
    w = _ws(_row("2026_05_PHI_JAX", "JAX", "outdoors", "Tottenham Hotspur Stadium"))
    assert w["venue_is_home_stadium"] is False
    assert w["material"] is False and "temperature_f" not in w and "wind" not in w
    assert w["neutral_site"] is True, "a game away from both teams' stadiums is a neutral site"
    assert "Tottenham Hotspur Stadium" in w["note"]


def test_a_home_game_keeps_the_schedule_neutral_flag():
    w = _ws(_row("2026_06_GB_CHI", "CHI", "outdoors", "Soldier Field"))
    assert w["venue_is_home_stadium"] is True and w["neutral_site"] is False


def test_the_renderer_shows_the_note_and_the_context_forecast_for_an_unknown_roof():
    w = _ws(_row("2026_06_SEA_ARI", "ARI", "", "State Farm Stadium"))
    lines = R._weather_lines(w)
    text = "\n".join(lines)
    assert "retractable" in text and "85" in text and "material: **False**" in text


def test_the_renderer_shows_only_the_note_for_a_dome():
    w = _ws(_row("2026_06_GB_DET", "DET", "", "Ford Field"))
    assert R._weather_lines(w) == [w["note"]]


# ===================================================================== capture: what is fetched

def _schedule_csv(now):
    day = (now + timedelta(days=3)).strftime("%Y-%m-%d")
    cols = ["game_id", "season", "week", "gameday", "gametime", "home_team", "away_team", "result", "location",
            "roof", "surface", "stadium_id", "stadium"]
    rows = [
        ["2026_05_PHI_JAX", "2026", "5", day, "09:30", "JAX", "PHI", "", "Home", "outdoors", "grass", "JAX00",
         "Tottenham Hotspur Stadium"],
        ["2026_05_GB_CHI", "2026", "5", day, "13:00", "CHI", "GB", "", "Home", "outdoors", "grass", "CHI98",
         "Soldier Field"],
        ["2026_05_DAL_WAS", "2026", "5", day, "09:30", "WAS", "DAL", "", "Neutral", "outdoors", "grass", "LON02",
         "Tottenham Hotspur Stadium"],
    ]
    buf = io.StringIO()
    w = csv.writer(buf)
    w.writerow(cols)
    w.writerows(rows)
    return buf.getvalue().encode()


def test_the_capture_never_fetches_the_home_stadium_forecast_for_a_game_played_elsewhere(tmp_path, monkeypatch):
    now = datetime.now(timezone.utc)
    urls = []

    def try_get(url, timeout=60):
        urls.append(url)
        if "games.csv" in url:
            body = _schedule_csv(now)
        elif "players/nfl" in url or "state/nfl" in url:
            body = b"{}"
        elif "injuries" in url:
            body = b'{"injuries": []}'
        else:
            return None, {"status": 503, "error": "offline test", "retrieved_at": now.isoformat()}
        return body, {"status": 200, "bytes": len(body), "retrieved_at": now.isoformat()}

    monkeypatch.setattr(CC, "OUT", str(tmp_path / "context"))
    monkeypatch.setattr(CC, "try_get", try_get)
    monkeypatch.setattr(CC.time, "sleep", lambda s: None)
    CC.main([])
    rows = {r["game_id"]: r for f in (tmp_path / "context").glob("*/*.weather.jsonl")
            for r in map(json.loads, f.read_text().splitlines())}
    assert set(rows) == {"2026_05_PHI_JAX", "2026_05_GB_CHI", "2026_05_DAL_WAS"}

    jax = STADIUMS["JAX"]
    assert not [u for u in urls if f"{jax['lat']:.4f}" in u or f"latitude={jax['lat']}" in u], \
        "the London game was looked up at Jacksonville's coordinates"
    london = rows["2026_05_PHI_JAX"]
    assert london["venue_check"] == VEN.OTHER_VENUE and "Tottenham Hotspur Stadium" in london["note"]
    assert "nws" not in london and "open_meteo" not in london
    assert london["neutral"] is False, "the raw nflverse flag is kept as captured"
    assert london["neutral_site_derived"] is True
    assert london["stadium_id_schedule"] == "JAX00"
    assert rows["2026_05_DAL_WAS"]["venue_check"] == VEN.OTHER_VENUE

    chi = rows["2026_05_GB_CHI"]
    assert chi["venue_check"] == VEN.HOME_STADIUM and chi["roof_type_config"] == "open"
    assert chi["neutral_site_derived"] is False
    assert any("api.weather.gov/points/41.8623" in u for u in urls), "a home game is still fetched"
