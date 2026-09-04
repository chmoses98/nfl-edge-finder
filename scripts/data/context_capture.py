#!/usr/bin/env python3
"""Context capture (runs in GitHub Actions): weather forecasts, availability, injuries — timestamped vintages.

Every run writes append-only files under data/context/<YYYY-MM-DD>/<run_id>.*.jsonl(.json):
  weather.jsonl   one row per upcoming outdoor/unknown-roof game within 7 days: NWS hourly forecast periods around
                  kickoff (temperature, wind speed/gust text, precip prob) + Open-Meteo hourly (wind, gusts, precip)
  sleeper.json    full Sleeper players snapshot fields relevant to availability (injury_status, injury_body_part,
                  practice_participation, depth_chart_order/position, status, team), keyed by sleeper_id
  espn_injuries.json  ESPN site injuries endpoint (all teams)
  manifest.json   retrieval times, statuses, counts, fail-closed flags
Nothing here is interpreted; interpretation (availability state machine) is downstream and point-in-time by run_id.
"""
import csv, io, json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone, timedelta

WEATHER_LOOKAHEAD_DAYS = 10
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UA = "nfl-edge-finder/0.1 (research; github.com/chmoses98/nfl-edge-finder)"
OUT = os.path.join(ROOT, "data", "context")
SCHEDULE_URL = "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv"


def get(url, timeout=60):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/csv, */*"})
    t0 = time.time()
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
    return raw, {"status": 200, "bytes": len(raw), "seconds": round(time.time() - t0, 2), "retrieved_at": datetime.now(timezone.utc).isoformat()}


def try_get(url, timeout=60):
    try:
        return get(url, timeout)
    except urllib.error.HTTPError as e:
        return None, {"status": e.code, "error": e.read()[:200].decode("utf-8", "replace"), "retrieved_at": datetime.now(timezone.utc).isoformat()}
    except Exception as e:
        return None, {"status": "error", "error": str(e)[:200], "retrieved_at": datetime.now(timezone.utc).isoformat()}


def main():
    import hashlib
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"); now = datetime.now(timezone.utc)
    d = os.path.join(OUT, now.strftime("%Y-%m-%d")); os.makedirs(d, exist_ok=True)
    man = {"run_id": run_id, "sources": {}, "failed_closed": []}
    state_path = os.path.join(OUT, "state.json")
    state = json.load(open(state_path)) if os.path.exists(state_path) else {}
    stadiums = json.load(open(os.path.join(ROOT, "config", "stadiums.json")))
    # schedule
    raw, meta = try_get(SCHEDULE_URL); man["sources"]["schedule"] = meta
    games = []
    if raw:
        for row in csv.DictReader(io.StringIO(raw.decode())):
            if not row.get("gametime") or row.get("result"):
                continue
            try:
                dt = datetime.strptime(row["gameday"] + " " + row["gametime"], "%Y-%m-%d %H:%M")
            except ValueError:
                continue
            nov1 = datetime(dt.year, 11, 1); dst_end = nov1 + timedelta(days=(6 - nov1.weekday()) % 7)
            mar1 = datetime(dt.year, 3, 1); dst_start = mar1 + timedelta(days=(6 - mar1.weekday()) % 7 + 7)
            kick = (dt + timedelta(hours=4 if dst_start <= dt < dst_end else 5)).replace(tzinfo=timezone.utc)
            # 10 days, not 7. A Sunday game is 9-10 days out when the previous Sunday's slate finishes, so a
            # 7-day window never records a 7-day-lead forecast vintage for the games that matter most -- on
            # 2026-09-04 it captured 2 of Week 1's 16 games. Open-Meteo serves 16 days; forecast_days below
            # must stay >= this window or the kickoff hour falls outside the returned range.
            if now - timedelta(hours=6) <= kick <= now + timedelta(days=WEATHER_LOOKAHEAD_DAYS):
                games.append({**row, "kickoff_utc": kick.isoformat()})
    else:
        man["failed_closed"].append("schedule unavailable: no weather rows written")
    # weather per game
    with open(os.path.join(d, f"{run_id}.weather.jsonl"), "w") as f:
        for g in games:
            st = stadiums.get(g["home_team"])
            row = {"run_id": run_id, "game_id": g["game_id"], "home_team": g["home_team"], "away_team": g["away_team"], "kickoff_utc": g["kickoff_utc"],
                   "roof": g.get("roof"), "surface": g.get("surface"), "stadium_schedule": g.get("stadium"), "stadium_config": st and st["stadium"],
                   "neutral": g.get("location") == "Neutral"}
            if not st or (g.get("location") == "Neutral" and st["stadium"] != g.get("stadium")):
                row["note"] = "no coordinates for this site"; f.write(json.dumps(row) + "\n"); continue
            lat, lon = st["lat"], st["lon"]
            # NWS: points -> hourly forecast (two calls); keep periods within +/- 6h of kickoff
            pts, m1 = try_get(f"https://api.weather.gov/points/{lat:.4f},{lon:.4f}")
            nws = None
            if pts:
                try:
                    url = json.loads(pts)["properties"]["forecastHourly"]
                    hf, m2 = try_get(url)
                    if hf:
                        periods = json.loads(hf)["properties"]["periods"]
                        k = datetime.fromisoformat(g["kickoff_utc"])
                        nws = {"generated": json.loads(hf)["properties"].get("generatedAt"), "updated": json.loads(hf)["properties"].get("updateTime"),
                               "periods": [p for p in periods if abs((datetime.fromisoformat(p["startTime"]) - k).total_seconds()) <= 6 * 3600]}
                        nws["meta"] = m2
                except Exception as e:
                    nws = {"error": str(e)[:200]}
            row["nws"] = nws or {"meta": m1}
            om, m3 = try_get(f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&hourly=temperature_2m,wind_speed_10m,wind_gusts_10m,wind_direction_10m,precipitation_probability,precipitation,relative_humidity_2m&forecast_days=11&wind_speed_unit=mph&temperature_unit=fahrenheit&timezone=UTC")
            if om:
                j = json.loads(om); k = datetime.fromisoformat(g["kickoff_utc"]).replace(tzinfo=None)
                idx = [i for i, t in enumerate(j["hourly"]["time"]) if abs((datetime.fromisoformat(t) - k).total_seconds()) <= 6 * 3600]
                row["open_meteo"] = {"meta": m3, "hourly": {key: [vals[i] for i in idx] for key, vals in j["hourly"].items()}}
            else:
                row["open_meteo"] = {"meta": m3}
            f.write(json.dumps(row) + "\n"); time.sleep(0.5)
    man["sources"]["weather_games"] = len(games)
    # Sleeper players (availability)
    raw, meta = try_get("https://api.sleeper.app/v1/players/nfl", timeout=120); man["sources"]["sleeper_players"] = meta
    if raw:
        keep = ("player_id", "full_name", "team", "position", "status", "injury_status", "injury_body_part", "injury_notes", "injury_start_date",
                "practice_participation", "practice_description", "depth_chart_order", "depth_chart_position", "active", "gsis_id", "espn_id", "number")
        players = json.loads(raw)
        slim = {pid: {k: p.get(k) for k in keep} for pid, p in players.items() if isinstance(p, dict) and p.get("team") and p.get("position") in ("QB", "RB", "WR", "TE", "K", "OL", "T", "G", "C", "DL", "DE", "DT", "LB", "CB", "S", "DB", "OLB", "ILB", "FB", "P")}
        blob = json.dumps(slim, sort_keys=True, separators=(",", ":")); h = hashlib.sha1(blob.encode()).hexdigest()
        man["sources"]["sleeper_players"]["content_sha1"] = h; man["sources"]["sleeper_players"]["changed"] = state.get("sleeper_sha1") != h
        if state.get("sleeper_sha1") != h:
            json.dump({"run_id": run_id, "retrieved_at": meta["retrieved_at"], "players": slim}, open(os.path.join(d, f"{run_id}.sleeper.json"), "w"), separators=(",", ":"))
            state["sleeper_sha1"] = h
        man["sources"]["sleeper_players"]["kept"] = len(slim)
        man["sources"]["sleeper_players"]["with_injury_status"] = sum(1 for p in slim.values() if p.get("injury_status"))
    else:
        man["failed_closed"].append("sleeper unavailable")
    raw, meta = try_get("https://api.sleeper.app/v1/state/nfl"); man["sources"]["sleeper_state"] = meta
    if raw:
        man["sleeper_state"] = json.loads(raw)
    # ESPN injuries
    raw, meta = try_get("https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries", timeout=120); man["sources"]["espn_injuries"] = meta
    if raw:
        j = json.loads(raw)
        slim = []
        for team in j.get("injuries", []):
            for inj in team.get("injuries", []):
                ath = inj.get("athlete") or {}; det = inj.get("details") or {}
                slim.append({"team": team.get("displayName"), "team_id": team.get("id"), "athlete_id": ath.get("id"), "name": ath.get("displayName"),
                             "position": (ath.get("position") or {}).get("abbreviation"), "status": inj.get("status"), "date": inj.get("date"),
                             "type": (inj.get("type") or {}).get("description"), "injury": det.get("type"), "location": det.get("location"), "detail": det.get("detail"),
                             "side": det.get("side"), "return_date": det.get("returnDate"), "fantasy_status": (det.get("fantasyStatus") or {}).get("description"),
                             "short_comment": (inj.get("shortComment") or "")[:200]})
        blob = json.dumps(slim, sort_keys=True, separators=(",", ":")); h = hashlib.sha1(blob.encode()).hexdigest()
        man["sources"]["espn_injuries"]["content_sha1"] = h; man["sources"]["espn_injuries"]["changed"] = state.get("espn_sha1") != h
        if state.get("espn_sha1") != h:
            json.dump({"run_id": run_id, "retrieved_at": meta["retrieved_at"], "injuries": slim}, open(os.path.join(d, f"{run_id}.espn_injuries.json"), "w"), separators=(",", ":"))
            state["espn_sha1"] = h
        man["sources"]["espn_injuries"]["teams"] = len(j.get("injuries", [])); man["sources"]["espn_injuries"]["rows"] = len(slim)
    else:
        man["failed_closed"].append("espn injuries unavailable")
    json.dump(state, open(state_path, "w"))
    json.dump(man, open(os.path.join(d, f"{run_id}.manifest.json"), "w"), indent=1)
    print(json.dumps(man, default=str)[:1500])
    return 0 if not man["failed_closed"] else 2


if __name__ == "__main__":
    sys.exit(main())
