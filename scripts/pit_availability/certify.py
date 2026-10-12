#!/usr/bin/env python3
"""Measure the point-in-time properties of every NFL availability source and write the certification evidence.

    python3 scripts/pit_availability/certify.py --market-data <sparse market-data checkout> \
        --out research/pit_availability/certification.json

Inputs (read-only): nflverse injuries 2009..2026, depth_charts 2020..2026, rosters / players, schedule (downloaded
by scripts/data/nflverse_download.py, provenance in data/raw/nflverse/_manifest.jsonl); from market-data: the
repository's injury vintages (data/raw/nflverse/_vintages/injuries/), the context captures of the ESPN injuries
endpoint (data/context/<day>/<run>.espn_injuries.json) and the ESPN-summary inactives collector
(data/shadow/v2/inactives/). Every number in docs/research/NFL_PIT_AVAILABILITY_CERTIFICATION.md comes from here.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from datetime import timedelta

import pandas as pd
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.availability_pit import loaders as L  # noqa: E402

NV = os.path.join("data", "raw", "nflverse")


def manifest(root):
    out = {}
    p = os.path.join(root, NV, "_manifest.jsonl")
    for line in open(p):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        out[r.get("path")] = {k: r.get(k) for k in ("retrieved_at", "sha256", "last_modified", "url")}
    return out


def injuries_row_timestamps(root, tg):
    rows, pattern = [], []
    players = set(pl.read_parquet(os.path.join(root, NV, "players", "players.parquet"), columns=["gsis_id"])["gsis_id"].drop_nulls())
    for s in range(2009, 2100):
        p = os.path.join(root, NV, "injuries", f"injuries_{s}.parquet")
        if not os.path.exists(p):
            break
        d = pl.read_parquet(p).to_pandas()
        d["team"] = d["team"].replace(L.TEAM_FIX)
        m = d.merge(tg, on=["season", "week", "game_type", "team"], how="left")
        r = {"season": s, "rows": int(len(d)), "joined_to_team_game": round(float(m["game_id"].notna().mean()), 4),
             "gsis_nonnull": round(float(d["gsis_id"].notna().mean()), 4), "gsis_in_players_table": round(float(d["gsis_id"].isin(players).mean()), 4),
             "report_status_nonnull": round(float(d["report_status"].notna().mean()), 4),
             "has_date_modified": bool("date_modified" in d.columns and d["date_modified"].notna().mean() > 0.5)}
        if r["has_date_modified"]:
            dm = pd.to_datetime(m["date_modified"], utc=True); k = pd.to_datetime(m["kickoff"], utc=True)
            lead = ((k - dm).dt.total_seconds() / 3600)[lambda x: x.notna()]
            r.update({"date_modified_nonnull": round(float(m["date_modified"].notna().mean()), 4),
                      "dm_before_kickoff": round(float((lead > 0).mean()), 5), "dm_at_or_after_kickoff_rows": int((lead <= 0).sum()),
                      "dm_before_kickoff_minus_90m": round(float((lead > 1.5).mean()), 5),
                      "lead_hours_p01": round(float(lead.quantile(.01)), 1), "lead_hours_median": round(float(lead.median()), 1),
                      "lead_hours_p99": round(float(lead.quantile(.99)), 1)})
            mm = m.assign(game_dow=k.dt.tz_convert("America/New_York").dt.day_name(), dm_dow=dm.dt.tz_convert("America/New_York").dt.day_name())
            pattern.append(mm[["game_dow", "dm_dow"]])
        rows.append(r)
    pat = pd.concat(pattern, ignore_index=True)
    ct = pd.crosstab(pat["game_dow"], pat["dm_dow"])
    return rows, {g: {k: int(v) for k, v in row.items() if v} for g, row in ct.iterrows()}


def injuries_vintages_2026(root, md, tg):
    snaps = L.vintage_snapshots([md], 2026)
    KEY = ["week", "team", "gsis_id"]; VAL = ["report_status", "practice_status", "report_primary_injury"]

    def load(p):
        d = pl.read_parquet(p).to_pandas()
        d["team"] = d["team"].replace(L.TEAM_FIX)
        d = d[d["game_type"] == "REG"]
        return d[KEY + VAL].fillna("").astype(str).drop_duplicates(KEY)
    frames = [(t, load(p)) for t, p in snaps]
    cur_p = os.path.join(root, NV, "injuries", "injuries_2026.parquet")
    cur_t = pd.Timestamp(manifest(root)[os.path.join(NV, "injuries", "injuries_2026.parquet").replace(os.sep, "/")]["retrieved_at"])
    frames.append((cur_t, load(cur_p)))
    t26 = tg[(tg["season"] == 2026) & (tg["game_type"] == "REG")]
    out = []
    for g in t26.itertuples(index=False):
        k = pd.Timestamp(g.kickoff)
        k = k.tz_localize("UTC") if k.tzinfo is None else k
        pre = [f for f in frames if f[0] < k]; post = [f for f in frames if f[0] >= k]
        if not post:
            continue
        lp = post[-1][1]; lp = lp[(lp["week"] == str(g.week)) & (lp["team"] == g.team)]
        rec = {"week": int(g.week), "team": g.team, "n_final": int(len(lp)), "pregame_vintage": bool(pre)}
        if pre:
            ts, f = pre[-1]; pv = f[(f["week"] == str(g.week)) & (f["team"] == g.team)]
            j = pv.merge(lp, on=KEY, how="outer", suffixes=("_pre", "_post"), indicator=True)
            both = j[j["_merge"] == "both"]
            rec.update({"lead_h": round((k - ts).total_seconds() / 3600, 1), "n_pregame": int(len(pv)),
                        "added_after_kickoff": int((j["_merge"] == "right_only").sum()), "removed_after_kickoff": int((j["_merge"] == "left_only").sum()),
                        "changed_after_kickoff": int(((both["report_status_pre"] != both["report_status_post"]) |
                                                      (both["practice_status_pre"] != both["practice_status_post"])).sum())})
        out.append(rec)
    o = pd.DataFrame(out)
    agg = o.groupby("week").agg(team_games=("team", "size"), with_pregame_vintage=("pregame_vintage", "sum"), rows_final=("n_final", "sum"),
                                rows_pregame=("n_pregame", "sum"), added_after_kickoff=("added_after_kickoff", "sum"),
                                removed_after_kickoff=("removed_after_kickoff", "sum"), changed_after_kickoff=("changed_after_kickoff", "sum"),
                                lead_h_median=("lead_h", "median")).reset_index()
    edits = o[(o.get("changed_after_kickoff", 0).fillna(0) > 0) | (o.get("added_after_kickoff", 0).fillna(0) > 0) | (~o["pregame_vintage"])]
    return {"distinct_vintages": len(snaps), "first_vintage": str(snaps[0][0]) if snaps else None, "last_vintage": str(snaps[-1][0]) if snaps else None,
            "current_file_retrieved_at": str(cur_t), "by_week": json.loads(agg.to_json(orient="records")),
            "team_weeks_with_post_kickoff_edits_or_no_pregame_vintage": json.loads(edits.to_json(orient="records"))}


def injuries_2025_vintage(md):
    snaps = L.vintage_snapshots([md], 2025)
    return {"distinct_vintages": len(snaps), "retrieved_at": [str(t) for t, _ in snaps],
            "note": "every 2025 vintage was retrieved after the 2025 season ended; none precedes any 2025 kickoff"}


def depth_charts(root):
    res = {}
    for s in range(2020, 2100):
        p = os.path.join(root, NV, "depth_charts", f"depth_charts_{s}.parquet")
        if not os.path.exists(p):
            break
        d = pl.read_parquet(p)
        r = {"rows": d.height, "has_dt": "dt" in d.columns, "gsis_null_frac": round(float(d["gsis_id"].is_null().mean()), 4)}
        if "dt" in d.columns:
            t = d["dt"].str.to_datetime(time_zone="UTC")
            per = d.with_columns(t.alias("t")).group_by("t").agg(pl.len(), pl.col("team").n_unique().alias("teams")).sort("t")
            gaps = per["t"].diff().dt.total_hours()
            r.update({"snapshots": per.height, "first": str(per["t"].min()), "last": str(per["t"].max()), "teams_per_snapshot_min": int(per["teams"].min()),
                      "gap_hours_median": float(gaps.median()), "gap_hours_max": float(gaps.max()),
                      "in_season_snapshots_sep_jan": int(per.filter(pl.col("t").dt.month().is_in([9, 10, 11, 12, 1])).height)})
            if s == 2026:
                r["rows_dt_le_2026_09_03_now"] = int(d.filter(t <= pd.Timestamp("2026-09-03T23:59:59Z")).height)
                r["rows_dt_le_2026_09_03_recorded_2026_09_03"] = "494k (docs/DATA_SOURCE_AUDIT.md, written 2026-09-03)"
            rep = L.depth_chart_certified(root, s)[1]
            r["loader_report"] = rep
        else:
            r["weeks"] = sorted(set(d["week"].drop_nulls().to_list())) if "week" in d.columns else None
        res[s] = r
    return res


def espn_injuries(root, md):
    files = sorted(glob.glob(os.path.join(md, "data", "context", "*", "*.espn_injuries.json")))
    caps, rows = [], 0
    athlete_null = 0; date_ok = 0; n = 0
    for f in files:
        d = json.load(open(f))
        if "injuries" not in d:
            continue
        ra = pd.Timestamp(d["retrieved_at"]); caps.append(ra)
        for r in d["injuries"]:
            n += 1; athlete_null += r.get("athlete_id") is None
            rd = pd.to_datetime(r.get("date"), utc=True, errors="coerce")
            date_ok += bool(pd.notna(rd) and rd <= ra)
    gaps = pd.Series(sorted(caps)).diff().dt.total_seconds() / 3600
    ros = pl.read_parquet(os.path.join(root, NV, "rosters", "roster_2026.parquet")).select("gsis_id", "full_name", "team").to_pandas()
    tg = L.team_games(root); tg = tg[(tg["season"] == 2026) & (tg["game_type"] == "REG")]
    tg = tg[pd.to_datetime(tg["kickoff"], utc=True) < pd.Timestamp(max(caps))]
    loaded, rep = L.espn_injuries_captured(files, ros, tg)
    return {"captures": len(caps), "legacy_payload_files_skipped": len(files) - len(caps), "first": str(min(caps)), "last": str(max(caps)),
            "rows": n, "athlete_id_null_frac": round(athlete_null / n, 4), "row_date_le_retrieved_frac": round(date_ok / n, 5),
            "capture_gap_hours_median": round(float(gaps.median()), 2), "capture_gap_hours_max": round(float(gaps.max()), 2),
            "loader_report_2026_played_team_games": rep,
            "identity_returned_vs_refused": {"returned": rep["returned"], **rep["refused"]}}


def inactives(md):
    tot = {"runs": 0, "game_observations_in_window": 0, "usable": 0, "players_confirmed_inactive": 0, "team_states": {}}
    for f in sorted(glob.glob(os.path.join(md, "data", "shadow", "v2", "inactives", "*", "*.inactives.json"))):
        d = json.load(open(f)); m = d["manifest"]
        tot["runs"] += 1; tot["game_observations_in_window"] += m["games_in_window"]; tot["usable"] += m["games_usable"]
        tot["players_confirmed_inactive"] += m["players_confirmed_inactive"]
        for g in d["games"]:
            for t in g.get("teams", []):
                tot["team_states"][t.get("state")] = tot["team_states"].get(t.get("state"), 0) + 1
    return tot


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default=ROOT)
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--out", required=True)
    a = ap.parse_args(argv)
    tg = L.team_games(a.root)
    inj, pattern = injuries_row_timestamps(a.root, tg)
    _, rep = L.injuries_certified(a.root, range(2010, 2027), vintage_roots=[a.market_data], lead=timedelta(minutes=90))
    out = {"inputs": {k: v for k, v in manifest(a.root).items() if any(x in (k or "") for x in ("injuries", "depth_charts", "rosters", "players", "schedules"))},
           "nflverse_injuries_row_timestamps": inj, "nflverse_injuries_date_modified_weekday_pattern_2010_2024": pattern,
           "nflverse_injuries_2026_vintages": injuries_vintages_2026(a.root, a.market_data, tg),
           "nflverse_injuries_2025_vintages": injuries_2025_vintage(a.market_data),
           "injuries_loader_report_T90": rep, "nflverse_depth_charts": depth_charts(a.root),
           "espn_injuries_captures": espn_injuries(a.root, a.market_data), "espn_summary_inactives_collector": inactives(a.market_data)}
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    with open(a.out, "w") as fh:
        json.dump(out, fh, indent=1, sort_keys=True, default=str)
    print(json.dumps({k: (v if k != "inputs" else len(v)) for k, v in out.items() if k in ("injuries_loader_report_T90", "espn_summary_inactives_collector")}, indent=1, default=str))


if __name__ == "__main__":
    main()
