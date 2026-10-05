"""WEATHER, honestly (preregistration section 8). RESEARCH_ONLY; weather never alters a simulated probability.

Two strictly separated parts:

1. HISTORICAL, NON_PIT_DESCRIPTIVE. The nflverse schedule's ``wind`` / ``temp`` are measured AT the game. They
   cannot be known before kickoff, so nothing here may fit or promote a predictive feature; the tables describe
   how realized totals (and, for 2021-2025, realized pass attempts against the simulation's mean) varied with
   OBSERVED weather. ``roof = outdoors`` is a stadium attribute and is the only pregame-known filter used.

2. PROSPECTIVE 2026 (point in time). The kickoff-hour forecast from the newest Open-Meteo vintage retrieved AT OR
   BEFORE the cutoff (``context.weather_vintages``), with its retrieval time and lead time. The preregistered
   hypotheses W1 / W2 accumulate evidence here; this module reports the qualifying sample size only -- no effect
   size is read out in this study.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import data as D
from nfl_edge.context import weather_vintages as WV

WIND_BUCKETS = ((0, 10, "0-9"), (10, 15, "10-14"), (15, 20, "15-19"), (20, 99, "20+"))
TEMP_BUCKETS = ((-99, 32, "<32F"), (32, 50, "32-49F"), (50, 200, "50F+"))
W1_WIND_MPH = 15.0
STATUS_HISTORICAL = "NON_PIT_DESCRIPTIVE"


def pit_forecast(vintages: list, game_id: str, cutoff_iso: str) -> dict | None:
    """The newest vintage retrieved at or before the cutoff; never a later one (asserted, not assumed)."""
    v = WV.latest_before(vintages, game_id, cutoff_iso)
    if v is not None and WV._parse(v["retrieved_at"]) > WV._parse(cutoff_iso):
        raise AssertionError("a forecast retrieved after the cutoff was selected")
    return v


def _bucket(x, buckets):
    for lo, hi, name in buckets:
        if lo <= x < hi:
            return name
    return None


def _mean_ci(x: np.ndarray) -> dict:
    x = np.asarray(x, float)
    if len(x) < 2:
        return {"n": int(len(x)), "mean": float(x.mean()) if len(x) else None}
    se = x.std(ddof=1) / np.sqrt(len(x))
    return {"n": int(len(x)), "mean": float(x.mean()), "lo": float(x.mean() - 1.96 * se), "hi": float(x.mean() + 1.96 * se)}


def historical_descriptive(seasons, sim_team_means: dict | None = None) -> dict:
    """Realized total residual vs the closing total by OBSERVED wind / temperature, outdoor stadiums only."""
    g = D.schedule().to_pandas()
    g = g[g["season"].isin(list(seasons)) & g["result"].notna() & g["total_line"].notna() & (g["roof"] == "outdoors")].copy()
    g["total_resid"] = g["total"] - g["total_line"]
    out = {"status": STATUS_HISTORICAL, "seasons": [int(s) for s in seasons], "n_outdoor_games": int(len(g)),
           "n_with_observed_wind": int(g["wind"].notna().sum()), "wind": {}, "temp": {}}
    for lo, hi, name in WIND_BUCKETS:
        out["wind"][name] = _mean_ci(g.loc[(g["wind"] >= lo) & (g["wind"] < hi), "total_resid"])
    for lo, hi, name in TEMP_BUCKETS:
        out["temp"][name] = _mean_ci(g.loc[(g["temp"] >= lo) & (g["temp"] < hi), "total_resid"])
    if sim_team_means:
        tg = D.load("team_games", sorted(set(g["season"]))).to_pandas().groupby("game_id")["pass_att"].sum()
        rows = []
        for r in g.itertuples():
            m = sim_team_means.get(r.game_id)
            if m is None or r.game_id not in tg.index or pd.isna(r.wind):
                continue
            rows.append({"wind": r.wind, "resid": float(tg[r.game_id]) - sum(v["pass_att"] for v in m.values())})
        d = pd.DataFrame(rows)
        out["combined_pass_att_resid_vs_sim_mean"] = {name: _mean_ci(d.loc[(d["wind"] >= lo) & (d["wind"] < hi), "resid"])
                                                      for lo, hi, name in WIND_BUCKETS} if len(d) else {}
    out["caveat"] = ("observed game-time weather is hindsight: these rows describe, they cannot fit or promote a feature; "
                     "retractable roofs are excluded because open/closed is decided on game day")
    return out


def prospective_accumulation(context_dir: str, season: int = 2026) -> dict:
    """Completed games of ``season`` with a point-in-time kickoff forecast (cutoff = kickoff): counts only."""
    v = WV.load_vintages(context_dir)
    g = D.schedule().to_pandas()
    g = g[(g["season"] == season) & g["result"].notna()].copy()
    g["kickoff"] = pd.to_datetime(g["gameday"] + " " + g["gametime"]).dt.tz_localize("America/New_York").dt.tz_convert("UTC")
    rows = []
    for r in g.itertuples():
        f = pit_forecast(v, r.game_id, r.kickoff.isoformat())
        rows.append({"game_id": r.game_id, "outdoors": r.roof == "outdoors", "has_forecast": f is not None,
                     "lead_hours": None if f is None else f["lead_hours"],
                     "w1_qualifies": bool(f is not None and r.roof == "outdoors" and (f.get("wind_speed_10m") or 0) >= W1_WIND_MPH)})
    d = pd.DataFrame(rows)
    lead = d["lead_hours"].dropna()
    return {"status": "PROSPECTIVE_ACCUMULATING", "season": season, "completed_games": int(len(d)),
            "with_pit_forecast": int(d["has_forecast"].sum()), "outdoor_with_forecast": int((d["has_forecast"] & d["outdoors"]).sum()),
            "w1_w2_qualifying_games": int(d["w1_qualifies"].sum()),
            "lead_hours_of_selected_vintage": {"median": float(lead.median()) if len(lead) else None,
                                               "max": float(lead.max()) if len(lead) else None},
            "n_vintage_rows": len(v), "readout": "NOT_READ: preregistered as accumulate-only in this study"}
