"""POINT-IN-TIME CONTEXT for projection records: what was knowable about the player, the game, the market and the
data at the instant the projection was made -- frozen on the record, never reconstructed later.

Every block follows one rule: a value that is not available at generation time is written as the string
"UNKNOWN" next to a `_reason`, never omitted and never filled from a later state. Every source carries its own
timestamp or vintage so a reader can tell what the model knew.

Sources (all already on disk when the projector runs; nothing here fetches):
    nflverse injuries_<season>.parquet   report_status / practice_status / primary injury for the game week (file vintage
                                         = the download's retrieved_at from data/raw/nflverse/_manifest.jsonl)
    nflverse depth_charts_<season>       latest chart `dt` at or before the snapshot instant (never a later chart)
    context captures (market-data)       sleeper / espn availability and NWS + Open-Meteo weather, latest run at or
                                         before the snapshot instant
    capture trades (market-data)         last trade time per ticker from the tape, at or before the snapshot instant
    silver schedule                      rest, division game, roof, surface, stadium, listed QBs
"""
from __future__ import annotations

import glob
import hashlib
import json
import os
from datetime import datetime, timezone

UNKNOWN = "UNKNOWN"
CONTEXT_VERSION = "context-1.1.0"       # 1.1.0: real route participation and red-zone opportunity replace two UNKNOWNs
ROUTE_SOURCE = "nflverse pbp_participation (offense_players per play, 2016-2025) via research/opportunity/player_usage.parquet; point-in-time EWMA over strictly prior games"
ROUTE_MISSING = "no prior game with participation coverage for this player (rookie, or a season the participation release does not cover)"
RZ_SOURCE = "nflverse play-by-play yardline_100 <= 20 (red zone), <= 5 (goal line) opportunity shares; point-in-time EWMA over strictly prior games"
RZ_MISSING = "no prior red-zone opportunity for this player in the participation window"


def _or_unknown(v):
    """A real number, or UNKNOWN. Never a silent zero: no prior data and no usage look identical as 0.0."""
    return UNKNOWN if v is None else v
SKILL = ("QB", "RB", "WR", "TE", "FB")


def _dt(s):
    if not s:
        return None
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _sha(path, n=16):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()[:n]


class ContextSources:
    def __init__(self, root: str, market_data: str, season: int, as_of: datetime, log=print):
        self.root, self.market_data, self.season, self.as_of = root, market_data, season, as_of
        self.log = log
        self.manifest = self._nflverse_manifest()
        self.injuries = self._injuries()
        self.depth = self._depth_charts()
        self.weather = self._weather()
        self.last_trade = self._last_trades()
        self.player_map = self._player_map_meta()

    # ------------------------------------------------------------------ loaders
    def _nflverse_manifest(self) -> dict:
        p = os.path.join(self.root, "data", "raw", "nflverse", "_manifest.jsonl")
        out = {}
        if os.path.exists(p):
            for line in open(p):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                out[r.get("path")] = {"retrieved_at": r.get("retrieved_at"), "last_modified": r.get("last_modified"), "sha256": (r.get("sha256") or "")[:16]}
        return out

    def source_meta(self, rel_path: str) -> dict:
        m = self.manifest.get(rel_path)
        return m or {"retrieved_at": UNKNOWN, "sha256": UNKNOWN, "reason": "not in the nflverse download manifest"}

    def _injuries(self):
        p = os.path.join(self.root, "data", "raw", "nflverse", "injuries", f"injuries_{self.season}.parquet")
        if not os.path.exists(p):
            return None
        try:
            import polars as pl
            d = pl.read_parquet(p)
            by = {}
            for r in d.iter_rows(named=True):
                by[(r.get("gsis_id"), int(r.get("week") or 0))] = {"report_status": r.get("report_status"), "practice_status": r.get("practice_status"),
                                                                    "report_injury": r.get("report_primary_injury"), "practice_injury": r.get("practice_primary_injury"), "team": r.get("team")}
            return {"rows": by, "path": os.path.relpath(p, self.root), "meta": self.source_meta(os.path.relpath(p, self.root))}
        except Exception as e:  # noqa: BLE001
            self.log(f"injuries unavailable: {e}")
            return None

    def _depth_charts(self):
        p = os.path.join(self.root, "data", "raw", "nflverse", "depth_charts", f"depth_charts_{self.season}.parquet")
        if not os.path.exists(p):
            return None
        try:
            import polars as pl
            d = pl.read_parquet(p).select("dt", "team", "gsis_id", "pos_abb", "pos_rank", "player_name")
            vintages = sorted(v for v in d["dt"].unique().to_list() if v and _dt(v) <= self.as_of)
            if not vintages:
                return {"vintage": None, "reason": "no depth chart at or before the snapshot instant", "path": os.path.relpath(p, self.root)}
            latest = vintages[-1]
            sub = d.filter(pl.col("dt") == latest)
            rank = {}; qb1 = {}; by_team = {}
            for r in sub.iter_rows(named=True):
                rank[r["gsis_id"]] = (r["pos_abb"], r["pos_rank"])
                by_team.setdefault(r["team"], []).append((r["gsis_id"], r["pos_abb"], r["pos_rank"]))
                if r["pos_abb"] == "QB" and r["pos_rank"] == 1:
                    qb1[r["team"]] = r["gsis_id"]
            return {"vintage": latest, "rank": rank, "qb1": qb1, "by_team": by_team, "path": os.path.relpath(p, self.root), "meta": self.source_meta(os.path.relpath(p, self.root))}
        except Exception as e:  # noqa: BLE001
            self.log(f"depth charts unavailable: {e}")
            return None

    def _weather(self):
        root = os.path.join(self.market_data, "data", "context")
        out = {}
        if not os.path.isdir(root):
            return out
        for p in sorted(glob.glob(os.path.join(root, "*", "*.weather.jsonl"))):
            run = os.path.basename(p)[:16]
            try:
                run_dt = datetime.strptime(run, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
            except ValueError:
                continue
            if run_dt > self.as_of:
                continue
            for line in open(p):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                gid = r.get("game_id")
                if gid:
                    out[gid] = {"run_id": run, "row": r}          # later runs (still <= as_of) overwrite earlier ones
        return out

    def _last_trades(self):
        root = os.path.join(self.market_data, "data", "kalshi", "capture")
        out = {}
        day_hi = self.as_of.strftime("%Y-%m-%d")
        for p in sorted(glob.glob(os.path.join(root, "*", "*.trades.jsonl"))):
            if os.path.basename(os.path.dirname(p)) > day_hi:
                continue
            for line in open(p):
                try:
                    r = json.loads(line)
                except ValueError:
                    continue
                t, ct = r.get("ticker"), r.get("created_time")
                if not t or not ct:
                    continue
                d = _dt(ct)
                if d and d <= self.as_of and (t not in out or d > out[t]):
                    out[t] = d
        return {t: d.isoformat() for t, d in out.items()}

    def _player_map_meta(self):
        p = os.path.join(self.root, "data", "silver", "kalshi_player_map.parquet")
        if not os.path.exists(p):
            return {"sha256": UNKNOWN, "reason": "player map absent"}
        return {"sha256": _sha(p), "path": os.path.relpath(p, self.root)}

    # ------------------------------------------------------------------ blocks
    def weather_block(self, game_id: str, kickoff: datetime | None) -> dict:
        w = self.weather.get(game_id)
        if not w:
            return {"state": UNKNOWN, "reason": "no context-capture weather row at or before the snapshot instant"}
        row = w["row"]
        out = {"state": "KNOWN", "context_run": w["run_id"], "roof": row.get("roof"), "surface": row.get("surface"), "neutral": row.get("neutral")}
        om = (row.get("open_meteo") or {}).get("hourly") or {}
        times = om.get("time") or []
        if times and kickoff:
            k = kickoff.replace(tzinfo=None)
            i = min(range(len(times)), key=lambda j: abs((datetime.fromisoformat(times[j]) - k).total_seconds()))
            out.update(source="open_meteo", forecast_hour=times[i], temperature_f=(om.get("temperature_2m") or [None] * len(times))[i],
                       wind_mph=(om.get("wind_speed_10m") or [None] * len(times))[i], gust_mph=(om.get("wind_gusts_10m") or [None] * len(times))[i],
                       precipitation_probability=(om.get("precipitation_probability") or [None] * len(times))[i],
                       precipitation=(om.get("precipitation") or [None] * len(times))[i], retrieved_at=((row.get("open_meteo") or {}).get("meta") or {}).get("retrieved_at"))
        else:
            out.update(source=UNKNOWN, reason="context row carries no hourly forecast around kickoff")
        nws = row.get("nws") or {}
        if nws.get("periods"):
            out["nws_generated"] = nws.get("generated"); out["nws_periods_near_kickoff"] = len(nws["periods"])
        return out

    def injury_block(self, gsis: str | None, week: int | None) -> dict:
        if not gsis:
            return {"state": UNKNOWN, "reason": "no player id"}
        if self.injuries is None:
            return {"state": UNKNOWN, "reason": "injury report file absent"}
        r = self.injuries["rows"].get((gsis, int(week or 0)))
        meta = self.injuries["meta"]
        if r is None:
            return {"state": "NOT_LISTED", "report_status": None, "practice_status": None, "source_retrieved_at": meta.get("retrieved_at"), "source_sha256": meta.get("sha256")}
        return {"state": "LISTED", **r, "source_retrieved_at": meta.get("retrieved_at"), "source_sha256": meta.get("sha256")}

    def depth_block(self, gsis: str | None, team: str | None) -> dict:
        if self.depth is None:
            return {"state": UNKNOWN, "reason": "depth chart file absent"}
        if not self.depth.get("vintage"):
            return {"state": UNKNOWN, "reason": self.depth.get("reason")}
        pr = self.depth["rank"].get(gsis)
        return {"state": ("LISTED" if pr else "NOT_LISTED"), "vintage": self.depth["vintage"], "position": (pr[0] if pr else None), "rank": (pr[1] if pr else None),
                "team_qb1": self.depth["qb1"].get(team), "source_retrieved_at": self.depth["meta"].get("retrieved_at")}

    def teammate_block(self, team: str | None, week: int | None, exclude: str | None) -> dict:
        """Skill-position teammates with an injury designation this week, from the same report vintage."""
        if self.injuries is None or not team:
            return {"state": UNKNOWN, "reason": "injury report absent or no team"}
        listed = []
        for (gsis, wk), r in self.injuries["rows"].items():
            if wk == int(week or 0) and r.get("team") == team and gsis != exclude and (r.get("report_status") or r.get("practice_status")):
                listed.append({"gsis_id": gsis, "report_status": r.get("report_status"), "practice_status": r.get("practice_status")})
        out_ids = [x["gsis_id"] for x in listed if (x["report_status"] or "").lower() in ("out", "doubtful")]
        return {"state": "KNOWN", "n_listed": len(listed), "n_out_or_doubtful": len(out_ids), "out_or_doubtful": out_ids[:12], "listed": listed[:20]}

    def lineage_block(self, *, snapshot_id: str, discovery_run: str | None, engine_versions: dict, feature_set: str | None, bundle_sha: str | None,
                      period_bank_fingerprint: str | None, tables: list) -> dict:
        return {"context_version": CONTEXT_VERSION, "capture_run": snapshot_id, "discovery_run": discovery_run, "identity_map": self.player_map,
                "nflverse_sources": {t: self.source_meta(t) for t in tables}, "engine_versions": engine_versions, "feature_set": feature_set,
                "bundle_sha": bundle_sha, "period_bank_fingerprint": period_bank_fingerprint,
                "depth_chart_vintage": (self.depth or {}).get("vintage"), "injury_report_retrieved_at": ((self.injuries or {}).get("meta") or {}).get("retrieved_at"),
                "weather_runs_seen": len(self.weather), "trade_tape_tickers": len(self.last_trade)}


def player_context(src: ContextSources, *, gsis, team, week, game_id, kickoff, feat_row: dict, avail, position) -> dict:
    """Everything needed to explain a player projection later, frozen now."""
    fr = feat_row or {}
    inj = src.injury_block(gsis, week)
    dep = src.depth_block(gsis, team)
    av = {"state": (avail.state if avail else UNKNOWN), "p_plays": (avail.p_plays if avail else None), "p_active_no_snap": (avail.p_active_no_snap if avail else None),
          "sources": ({k: {kk: vv for kk, vv in v.items()} for k, v in avail.sources.items()} if avail else {}), "as_of": (avail.as_of if avail else None),
          "stale_minutes": (avail.stale_minutes if avail else None), "reason": (None if avail else "no availability source loaded for this snapshot")}
    def g(k):
        v = fr.get(k)
        return None if v is None or (isinstance(v, float) and v != v) else v
    return {"context_version": CONTEXT_VERSION, "position": position or g("position") or UNKNOWN, "team": team,
            "availability": av, "injury_report": inj, "depth_chart": dep,
            "qb_identity": {"schedule_listed": g("_schedule_qb"), "depth_chart_qb1": dep.get("team_qb1"), "qb_changed_recent": g("qb_changed_recent")},
            "teammates": src.teammate_block(team, week, gsis),
            # Route participation and red-zone opportunity are REAL, not proxies: nflverse pbp_participation
            # lists the eleven offensive players on the field for every play 2016-2025, so a route is a dropback
            # the player was on the field for, and red-zone / inside-10 / inside-5 opportunity comes from the
            # play-by-play's own yardline. Every value is the point-in-time EWMA over STRICTLY PRIOR games
            # (nfl_edge/features/opportunity.py). UNKNOWN survives only where the cache genuinely has no prior.
            "usage_estimates": {"snap_share": g("ewma_snap_share"), "target_share": g("ewma_target_share"), "carry_share": g("ewma_carry_share"),
                                "route_participation": _or_unknown(g("pit_route_share")), "routes_per_dropback": _or_unknown(g("pit_route_share")),
                                "targets_per_route_run": _or_unknown(g("pit_tprr")), "route_source": ROUTE_SOURCE,
                                "route_participation_reason": (None if g("pit_route_share") is not None else ROUTE_MISSING),
                                "pbp_snap_share": _or_unknown(g("pit_snap_share")), "air_yards_per_target": _or_unknown(g("pit_adot")),
                                "red_zone_target_share": _or_unknown(g("pit_rz_target_share")), "red_zone_carry_share": _or_unknown(g("pit_rz_carry_share")),
                                "inside_5_carry_share": _or_unknown(g("pit_i5_carry_share")), "red_zone_source": RZ_SOURCE,
                                "red_zone_reason": (None if (g("pit_rz_target_share") is not None or g("pit_rz_carry_share") is not None) else RZ_MISSING),
                                "share_recent_delta_target": g("share_recent_delta_target"), "share_recent_delta_carry": g("share_recent_delta_carry")},
            "team_volume_estimates": {"pass_attempts": g("ewma_team_pass_att"), "rush_attempts": g("ewma_team_rush_att"), "snaps": g("ewma_team_snaps"),
                                      "yards_per_attempt": g("ewma_team_ypa"), "pass_rate": g("ewma_team_pass_rate")},
            "player_ewma": {k: g(k) for k in fr if isinstance(k, str) and k.startswith("ewma_") and not k.startswith("ewma_team")},
            "game_environment": {"implied_total": g("implied_total"), "spread_team": g("spread_team"), "home": g("home"), "opponent": g("opponent_team")},
            "sample": {"n_prior_games": g("n_prior"), "effective_weight": g("w_eff"), "shrink_w": g("shrink_w")},
            "weather": src.weather_block(game_id, kickoff)}


def game_context(src: ContextSources, *, game_row, env: dict | None, kickoff, quote_ages: dict, tickers: list, n_quoted: int) -> dict:
    gr = game_row
    def v(k):
        x = gr.get(k) if hasattr(gr, "get") else None
        try:
            return None if x is None or (isinstance(x, float) and x != x) else (x.item() if hasattr(x, "item") else x)
        except Exception:  # noqa: BLE001
            return x
    spread, total = (env or {}).get("spread"), (env or {}).get("total")
    ages = [quote_ages.get(t) for t in tickers if quote_ages.get(t) is not None]
    dep = src.depth or {}
    return {"context_version": CONTEXT_VERSION, "spread_center_home": spread, "total_center": total, "center_source": (env or {}).get("source"),
            "n_liquid_rungs": ((env or {}).get("diag") or {}).get("n_liquid_rungs"),
            "home_implied_points": (None if spread is None or total is None else (total + spread) / 2.0), "away_implied_points": (None if spread is None or total is None else (total - spread) / 2.0),
            "consensus_spread_line": v("spread_line"), "consensus_total_line": v("total_line"),
            "qb_state": {"home_qb_schedule": v("home_qb_id"), "away_qb_schedule": v("away_qb_id"),
                         "home_qb1_depth_chart": (dep.get("qb1") or {}).get(v("home_team")), "away_qb1_depth_chart": (dep.get("qb1") or {}).get(v("away_team")),
                         "depth_chart_vintage": dep.get("vintage")},
            "rest": {"home_rest_days": v("home_rest"), "away_rest_days": v("away_rest"), "rest_differential_home_minus_away": (None if v("home_rest") is None or v("away_rest") is None else v("home_rest") - v("away_rest"))},
            "division_game": v("div_game"), "roof": v("roof"), "surface": v("surface"), "stadium": v("stadium"), "location": v("location"),
            "weather": src.weather_block(v("game_id"), kickoff),
            "availability_summary": {"home": src.teammate_block(v("home_team"), v("week"), None), "away": src.teammate_block(v("away_team"), v("week"), None)},
            "market_freshness": {"n_quoted_contracts": n_quoted, "median_minutes_since_price_change": (sorted(ages)[len(ages) // 2] if ages else None), "max_minutes_since_price_change": (max(ages) if ages else None)},
            "data_freshness": {"schedule": src.source_meta("data/raw/nflverse/schedules/games.csv"), "player_stats": src.source_meta(f"data/raw/nflverse/stats_player/stats_player_week_{src.season - 1}.parquet"),
                               "depth_charts": (dep.get("meta") or {"retrieved_at": UNKNOWN}), "injuries": ((src.injuries or {}).get("meta") or {"retrieved_at": UNKNOWN})}}


def market_state(*, quote: dict, ladder: dict | None, last_trade_at: str | None, snapshot_run: str, series_confirmed_at: str | None, series_complete: bool | None) -> dict:
    """The market environment of one contract at the horizon, plus where the quote came from (provenance)."""
    out = {"context_version": CONTEXT_VERSION, "price_change_run": quote.get("run_id"), "snapshot_run": snapshot_run, "series_confirmed_at": series_confirmed_at,
           "series_complete": series_complete, "price_observed_at": quote.get("observed_at"), "status": quote.get("status"),
           "last_trade_at": (last_trade_at or UNKNOWN), "last_trade_reason": (None if last_trade_at else "no trade for this ticker in the tape at or before the snapshot"),
           "yes_bid_size": quote.get("yes_bid_size_fp"), "yes_ask_size": quote.get("yes_ask_size_fp"), "last_price": quote.get("last_price_dollars")}
    if ladder:
        rungs = ladder.get("rungs") or []
        widths = sorted(r["ask"] - r["bid"] for r in rungs)
        out["ladder"] = {"n_rungs_quoted": ladder.get("n_rungs_quoted"), "n_rungs_used": ladder.get("n_rungs_used"), "n_rungs_excluded": ladder.get("n_rungs_excluded"),
                         "rungs": [{"k": r["k"], "bid": r["bid"], "ask": r["ask"], "width": r["ask"] - r["bid"]} for r in rungs],
                         "median_width": (widths[len(widths) // 2] if widths else None), "identification": ladder.get("identification"),
                         "raw_violations": ladder.get("raw_violations"), "brackets_median": ladder.get("brackets_median"), "has_tail_rung": ladder.get("has_tail_rung")}
    return out


# ------------------------------------------------------------------ compact inline views (the full block lives in the snapshot sidecar)
def compact_player_context(full: dict, cid: str) -> dict:
    inj, dep, av, w, use, tv, smp, qb = (full.get(k) or {} for k in ("injury_report", "depth_chart", "availability", "weather", "usage_estimates", "team_volume_estimates", "sample", "qb_identity"))
    return {"player_context_id": cid, "position": full.get("position"), "team": full.get("team"),
            "availability_state": av.get("state"), "p_plays": av.get("p_plays"), "availability_sources": sorted((av.get("sources") or {}).keys()),
            "injury_state": inj.get("state"), "report_status": inj.get("report_status"), "practice_status": inj.get("practice_status"),
            "depth_chart_rank": dep.get("rank"), "depth_chart_vintage": dep.get("vintage"),
            "qb_schedule": qb.get("schedule_listed"), "qb_depth_chart": qb.get("depth_chart_qb1"), "qb_changed_recent": qb.get("qb_changed_recent"),
            "teammates_out_or_doubtful": (full.get("teammates") or {}).get("n_out_or_doubtful"),
            "snap_share": use.get("snap_share"), "target_share": use.get("target_share"), "carry_share": use.get("carry_share"),
            "route_participation": use.get("route_participation"), "targets_per_route_run": use.get("targets_per_route_run"),
            "red_zone_target_share": use.get("red_zone_target_share"), "red_zone_carry_share": use.get("red_zone_carry_share"),
            "inside_5_carry_share": use.get("inside_5_carry_share"), "air_yards_per_target": use.get("air_yards_per_target"),
            "team_pass_attempts": tv.get("pass_attempts"), "team_rush_attempts": tv.get("rush_attempts"),
            "n_prior_games": smp.get("n_prior_games"), "shrink_w": smp.get("shrink_w"),
            "weather_state": w.get("state"), "wind_mph": w.get("wind_mph"), "temperature_f": w.get("temperature_f"), "precipitation_probability": w.get("precipitation_probability")}


def compact_game_context(full: dict, cid: str) -> dict:
    w, qb, rest, mf = (full.get(k) or {} for k in ("weather", "qb_state", "rest", "market_freshness"))
    return {"game_context_id": cid, "spread_center_home": full.get("spread_center_home"), "total_center": full.get("total_center"), "center_source": full.get("center_source"),
            "n_liquid_rungs": full.get("n_liquid_rungs"), "home_implied_points": full.get("home_implied_points"), "away_implied_points": full.get("away_implied_points"),
            "home_qb": qb.get("home_qb1_depth_chart") or qb.get("home_qb_schedule"), "away_qb": qb.get("away_qb1_depth_chart") or qb.get("away_qb_schedule"),
            "rest_differential": rest.get("rest_differential_home_minus_away"), "division_game": full.get("division_game"), "roof": full.get("roof"), "surface": full.get("surface"),
            "weather_state": w.get("state"), "wind_mph": w.get("wind_mph"), "temperature_f": w.get("temperature_f"), "precipitation_probability": w.get("precipitation_probability"),
            "home_out_or_doubtful": ((full.get("availability_summary") or {}).get("home") or {}).get("n_out_or_doubtful"),
            "away_out_or_doubtful": ((full.get("availability_summary") or {}).get("away") or {}).get("n_out_or_doubtful"),
            "median_minutes_since_price_change": mf.get("median_minutes_since_price_change")}
