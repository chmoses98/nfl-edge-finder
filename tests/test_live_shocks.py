"""Live shock ingestion: what we knew, and when we knew it.

Two rules matter more than the detection itself and both are asserted here. A shock must never be backdated
to when the event probably happened -- only to the capture where we observed it. And one real-world event
seen through two sources must not be counted as two events.
"""
import json
import os

from nfl_edge.shocks.live import (DEDUP_WINDOW_S, INACTIVE_CONFIRMED, QB_STATUS, SKILL_STATUS,
                                  WEATHER_WIND, dedupe, diff_captures)


def _sleeper(tmp_path, name, retrieved, players):
    p = tmp_path / name
    p.write_text(json.dumps({"run_id": name[:16], "retrieved_at": retrieved, "players": players}))
    return str(p)


def player(**kw):
    base = {"player_id": "1", "full_name": "A Player", "team": "SEA", "position": "WR",
            "status": "Active", "injury_status": None, "active": True, "depth_chart_order": 1,
            "gsis_id": "00-0011111"}
    base.update(kw)
    return base


def test_detects_an_injury_status_transition(tmp_path):
    a = _sleeper(tmp_path, "a.sleeper.json", "2026-09-10T12:00:00Z", {"1": player()})
    b = _sleeper(tmp_path, "b.sleeper.json", "2026-09-10T12:10:00Z",
                 {"1": player(injury_status="Out")})
    s = diff_captures(a, b, "sleeper")
    assert len(s) == 1
    assert s[0].prior_state == "none" and s[0].new_state == "Out"
    assert s[0].shock_family == SKILL_STATUS


def test_first_seen_at_is_the_observing_capture_never_backdated(tmp_path):
    a = _sleeper(tmp_path, "a.sleeper.json", "2026-09-10T12:00:00Z", {"1": player()})
    b = _sleeper(tmp_path, "b.sleeper.json", "2026-09-10T12:10:00Z", {"1": player(injury_status="Out")})
    s = diff_captures(a, b, "sleeper")[0]
    assert s.first_seen_at.startswith("2026-09-10T12:10"), \
        "the shock must be stamped at the capture that observed it, not the earlier one"
    assert s.timing_basis == "exact"
    assert s.source_timestamp is None, "no source event time exists; it must not be invented"


def test_a_quarterback_change_is_classified_separately(tmp_path):
    a = _sleeper(tmp_path, "a.sleeper.json", "2026-09-10T12:00:00Z", {"1": player(position="QB")})
    b = _sleeper(tmp_path, "b.sleeper.json", "2026-09-10T12:10:00Z",
                 {"1": player(position="QB", injury_status="Out")})
    assert diff_captures(a, b, "sleeper")[0].shock_family == QB_STATUS


def test_becoming_inactive_is_its_own_family(tmp_path):
    a = _sleeper(tmp_path, "a.sleeper.json", "2026-09-10T12:00:00Z", {"1": player()})
    b = _sleeper(tmp_path, "b.sleeper.json", "2026-09-10T12:10:00Z", {"1": player(active=False)})
    s = diff_captures(a, b, "sleeper")[0]
    assert s.new_state == "False" and s.confidence == "high"


def test_a_new_player_appearing_is_not_a_state_change(tmp_path):
    a = _sleeper(tmp_path, "a.sleeper.json", "2026-09-10T12:00:00Z", {})
    b = _sleeper(tmp_path, "b.sleeper.json", "2026-09-10T12:10:00Z", {"1": player(injury_status="Out")})
    assert diff_captures(a, b, "sleeper") == []


def test_one_event_seen_twice_becomes_one_canonical_shock(tmp_path):
    a = _sleeper(tmp_path, "a.sleeper.json", "2026-09-10T12:00:00Z", {"1": player()})
    b = _sleeper(tmp_path, "b.sleeper.json", "2026-09-10T12:03:00Z", {"1": player(injury_status="Out")})
    first = diff_captures(a, b, "sleeper")
    second = [s for s in diff_captures(a, b, "sleeper")]
    for s in second:                       # simulate the same transition seen through another source
        s.source = "espn"
        s.shock_id = s.shock_id + "_espn"
    canonical, observations = dedupe(first + second)
    assert len(canonical) == 1, "the same transition from two sources must collapse to one canonical shock"
    assert len(observations) == 2, "both source observations must be preserved"
    assert canonical[0].first_seen_at == min(o.first_seen_at for o in observations)


def test_distinct_transitions_are_not_merged(tmp_path):
    a = _sleeper(tmp_path, "a.sleeper.json", "2026-09-10T12:00:00Z",
                 {"1": player(), "2": player(player_id="2", gsis_id="00-0022222")})
    b = _sleeper(tmp_path, "b.sleeper.json", "2026-09-10T12:10:00Z",
                 {"1": player(injury_status="Out"),
                  "2": player(player_id="2", gsis_id="00-0022222", injury_status="Questionable")})
    canonical, _ = dedupe(diff_captures(a, b, "sleeper"))
    assert len(canonical) == 2


def test_small_weather_moves_are_not_shocks(tmp_path):
    def wx(name, wind):
        p = tmp_path / name
        p.write_text(json.dumps({"run_id": name[:16], "game_id": "2026_01_A_B", "roof": "outdoors",
                                 "home_team": "B",
                                 "open_meteo": {"hourly": {"wind_speed_10m": [wind],
                                                           "precipitation": [0.0]}}}) + "\n")
        return str(p)
    small = diff_captures(wx("a.weather.jsonl", 8.0), wx("b.weather.jsonl", 10.0), "weather")
    assert small == [], "a 2 mph forecast wiggle must not be recorded as an information shock"
    big = diff_captures(wx("c.weather.jsonl", 8.0), wx("d.weather.jsonl", 18.0), "weather")
    assert len(big) == 1 and big[0].shock_family == WEATHER_WIND


def test_indoor_games_produce_no_weather_shocks(tmp_path):
    def wx(name, wind):
        p = tmp_path / name
        p.write_text(json.dumps({"run_id": name[:16], "game_id": "g", "roof": "dome", "home_team": "B",
                                 "open_meteo": {"hourly": {"wind_speed_10m": [wind],
                                                           "precipitation": [0.0]}}}) + "\n")
        return str(p)
    assert diff_captures(wx("a.weather.jsonl", 5.0), wx("b.weather.jsonl", 30.0), "weather") == []
