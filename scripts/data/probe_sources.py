#!/usr/bin/env python3
"""Probe candidate free live sources FROM THE RUNNER (the only environment that will actually use them) and record
status, latency, payload shape and a content sample. Output: data/kalshi/probes/<run_id>.json on market-data.
Read-only GETs, one request per source, generous User-Agent per NWS policy."""
import json, os, sys, time, urllib.request, urllib.error
from datetime import datetime, timezone
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
UA = "nfl-edge-finder/0.1 (research; github.com/chmoses98/nfl-edge-finder)"
PROBES = {
    "nws_points_arrowhead": "https://api.weather.gov/points/39.0489,-94.4839",
    "nws_hourly_arrowhead": "https://api.weather.gov/gridpoints/EAX/44,53/forecast/hourly",
    "open_meteo_forecast": "https://api.open-meteo.com/v1/forecast?latitude=39.0489&longitude=-94.4839&hourly=temperature_2m,wind_speed_10m,wind_gusts_10m,precipitation_probability&forecast_days=7&wind_speed_unit=mph",
    "open_meteo_previous_runs": "https://previous-runs-api.open-meteo.com/v1/forecast?latitude=39.0489&longitude=-94.4839&hourly=wind_speed_10m_previous_day1,wind_speed_10m_previous_day3&wind_speed_unit=mph&past_days=2&forecast_days=1",
    "open_meteo_historical_forecast": "https://historical-forecast-api.open-meteo.com/v1/forecast?latitude=39.0489&longitude=-94.4839&start_date=2025-09-07&end_date=2025-09-08&hourly=wind_speed_10m,wind_gusts_10m,temperature_2m,precipitation&wind_speed_unit=mph",
    "sleeper_players": "https://api.sleeper.app/v1/players/nfl",
    "sleeper_state": "https://api.sleeper.app/v1/state/nfl",
    "espn_site_scoreboard": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
    "espn_site_web_scoreboard": "https://site.web.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard",
    "espn_cdn_scoreboard": "https://cdn.espn.com/core/nfl/scoreboard?xhr=1",
    "espn_core_injuries_kc": "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/teams/12/injuries",
    "espn_site_injuries": "https://site.api.espn.com/apis/site/v2/sports/football/nfl/injuries",
    "espn_depth_kc": "https://sports.core.api.espn.com/v2/sports/football/leagues/nfl/seasons/2026/teams/12/depthcharts",
    "nfl_static_schedule": "https://static.www.nfl.com/",
    "polymarket_gamma": "https://gamma-api.polymarket.com/markets?limit=5&tag=nfl",
    "nflverse_release": "https://github.com/nflverse/nflverse-data/releases/download/schedules/games.csv",
}


def main():
    run_id = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = {"run_id": run_id, "results": {}}
    for name, url in PROBES.items():
        t0 = time.time(); rec = {"url": url}
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "application/json, text/csv, */*"})
            with urllib.request.urlopen(req, timeout=40) as r:
                raw = r.read(); rec["status"] = r.status; rec["bytes"] = len(raw); rec["content_type"] = r.headers.get("Content-Type")
                txt = raw[:20000].decode("utf-8", "replace")
                rec["sample"] = txt[:600]
                try:
                    j = json.loads(raw); rec["json_keys"] = list(j.keys())[:25] if isinstance(j, dict) else f"list[{len(j)}]"
                except Exception:
                    pass
        except urllib.error.HTTPError as e:
            rec["status"] = e.code; rec["error"] = e.read()[:300].decode("utf-8", "replace")
        except Exception as e:
            rec["status"] = "error"; rec["error"] = str(e)[:300]
        rec["seconds"] = round(time.time() - t0, 2)
        out["results"][name] = rec
        print(name, rec.get("status"), rec.get("bytes"), rec["seconds"], flush=True)
        time.sleep(1.0)
    d = os.path.join(ROOT, "data", "kalshi", "probes"); os.makedirs(d, exist_ok=True)
    json.dump(out, open(os.path.join(d, f"{run_id}.json"), "w"), indent=1)


if __name__ == "__main__":
    main()
