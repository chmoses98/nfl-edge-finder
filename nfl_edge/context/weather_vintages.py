"""Kickoff-hour weather forecast, as it was known at each capture time.

The existing wind study (H-006) used the wind that was *observed* during the game. That is post hoc: it
cannot be known before kickoff, so no prospective claim can rest on it, and the apparent effect could as
easily be the market failing to price a forecast as the market failing to price the weather.

Every context capture stores the full hourly forecast for each upcoming game together with the run id that
produced it, so the captures accumulate **vintages**: the same kickoff seen from 7 days out, 3 days out, 1
day out, and so on. This module extracts the kickoff-hour forecast from each vintage, which is what a
prospective study needs.
"""
from __future__ import annotations

import glob
import json
import os
from datetime import datetime, timezone

FIELDS = ["temperature_2m", "wind_speed_10m", "wind_gusts_10m", "wind_direction_10m",
          "precipitation_probability", "precipitation", "relative_humidity_2m"]


def _parse(ts: str) -> datetime:
    d = datetime.fromisoformat(ts.replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def kickoff_forecast(record: dict) -> dict | None:
    """The forecast for the hour containing kickoff, from one capture of one game."""
    om = record.get("open_meteo") or {}
    hourly = om.get("hourly") or {}
    times = hourly.get("time") or []
    if not times or not record.get("kickoff_utc"):
        return None
    ko = _parse(record["kickoff_utc"])
    best, best_gap = None, None
    for i, t in enumerate(times):
        gap = abs((_parse(t if t.endswith("Z") or "+" in t else t + "+00:00") - ko).total_seconds())
        if best_gap is None or gap < best_gap:
            best, best_gap = i, gap
    if best is None or best_gap > 3 * 3600:
        return None
    run = record.get("run_id") or ""
    try:
        retrieved = datetime.strptime(run, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        lead_hours = (ko - retrieved).total_seconds() / 3600.0
    except ValueError:
        retrieved, lead_hours = None, None
    out = {"game_id": record.get("game_id"), "run_id": run, "kickoff_utc": record["kickoff_utc"],
           "roof": record.get("roof"), "neutral": record.get("neutral"),
           "retrieved_at": retrieved.isoformat() if retrieved else None,
           "lead_hours": lead_hours, "forecast_hour": times[best], "hour_gap_s": best_gap}
    for f in FIELDS:
        v = hourly.get(f)
        out[f] = v[best] if isinstance(v, list) and best < len(v) else None
    return out


def load_vintages(context_dir: str) -> list[dict]:
    """Every (game, capture) kickoff-hour forecast under a context capture directory."""
    rows = []
    for path in sorted(glob.glob(os.path.join(context_dir, "*", "*.weather.jsonl"))):
        for line in open(path):
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            f = kickoff_forecast(rec)
            if f:
                f["source_file"] = os.path.basename(path)
                rows.append(f)
    return rows


def latest_before(vintages: list[dict], game_id: str, cutoff_iso: str) -> dict | None:
    """The most recent vintage for a game that existed at `cutoff_iso` -- the point-in-time accessor."""
    cut = _parse(cutoff_iso)
    best = None
    for v in vintages:
        if v["game_id"] != game_id or not v.get("retrieved_at"):
            continue
        if _parse(v["retrieved_at"]) <= cut and (best is None or _parse(v["retrieved_at"]) > _parse(best["retrieved_at"])):
            best = v
    return best
