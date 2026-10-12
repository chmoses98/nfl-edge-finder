"""SEPARATE FAMILIES: Kalshi listings / quotes and the incumbent market-informed projections. Read-only reuse.

Nothing in this module is imported by prospective.py or records.py (tests/test_shadow_pure.py checks the import
graph), and nothing here writes into the PURE projection files. It reads what the repository's existing jobs already
store on the `market-data` branch:

    data/kalshi/discovery/<run>/markets/<SERIES>.json      kalshi-discover.yml (daily): every market with
                                                           created_time / open_time and the player uuid
    data/kalshi/capture/<day>/<run>.quotes.jsonl           kalshi capture/conductor (~10 min, change-suppressed)
    data/silver/kalshi_player_map.parquet                  scripts/kalshi/build_player_map.py (uuid -> gsis)
    data/shadow/v2/projections/<day>/<snap>.DATA_PLAYER_V{4,5}.projections.jsonl.gz   shadow-v2-project.yml

LISTING TIME and the PREGAME MARKET-LISTED COHORT. A player-game-statistic is in the cohort of a capture iff some
contract on it has `open_time <= as_of` AND was observed by one of our own records (a discovery run or a capture
quote) at or before as_of. It is defined from pregame records only -- never from settlement or from what traded.
"""
from __future__ import annotations

import glob
import gzip
import json
import os
from datetime import datetime, timedelta, timezone

# Kalshi PLAYER_STAT stat name (repo classifier) -> PURE statistic
STAT_MAP = {"receptions": "receptions", "receiving_yards": "receiving_yards", "rushing_yards": "rushing_yards",
            "carries": "carries", "passing_yards": "passing_yards", "completions": "completions", "attempts": "passing_attempts"}
INCUMBENT_ARMS = ("DATA_PLAYER_V4", "DATA_PLAYER_V5")
FAMILY_LABEL = "MARKET_INFORMED_DIAGNOSTIC"


def _utc(s):
    if s in (None, ""):
        return None
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _run_dt(run_id: str):
    try:
        return datetime.strptime(run_id[:15], "%Y%m%dT%H%M%S").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def game_lookup(games) -> dict:
    """(home, away) -> game_id for the capture's target games (one pairing per week)."""
    return {(g.home_team, g.away_team): g.game_id for g in games.itertuples(index=False)}


def player_map(path: str | None) -> dict:
    if not path or not os.path.exists(path):
        return {}
    import polars as pl
    df = pl.read_parquet(path)
    cols = df.columns
    kid = "kalshi_player_id" if "kalshi_player_id" in cols else cols[0]
    gid = "gsis_id" if "gsis_id" in cols else None
    if gid is None:
        return {}
    return {k: g for k, g in zip(df[kid].to_list(), df[gid].to_list()) if k and g}


def latest_discovery(md_root: str, as_of: datetime) -> str | None:
    runs = sorted(d for d in glob.glob(os.path.join(md_root, "data", "kalshi", "discovery", "*")) if os.path.isdir(d))
    ok = [d for d in runs if (_run_dt(os.path.basename(d)) or as_of) < as_of]
    return ok[-1] if ok else None


def discovery_listings(disc_dir: str, games, as_of: datetime) -> list[dict]:
    from nfl_edge.kalshi.classifier import classify
    look = game_lookup(games)
    disc_at = _run_dt(os.path.basename(disc_dir))
    out = []
    for f in sorted(glob.glob(os.path.join(disc_dir, "markets", "*.json"))):
        try:
            doc = json.load(open(f))
        except ValueError:
            continue
        for state in ("open", "unopened"):
            for m in (doc.get(state) or {}).get("markets", []):
                s = classify(m)
                if s.family != "PLAYER_STAT" or s.stat not in STAT_MAP or s.period not in (None, "FULL"):
                    continue
                gid = look.get((s.home_team, s.away_team))
                if not gid:
                    continue
                out.append({"source": "kalshi_discovery", "discovery_run": os.path.basename(disc_dir),
                            "observed_at": disc_at.isoformat(), "ticker": m.get("ticker"), "game_id": gid,
                            "kalshi_player_id": s.player_kalshi_id, "player_name": s.player_name, "statistic": STAT_MAP[s.stat],
                            "threshold": s.threshold, "open_time": m.get("open_time"), "created_time": m.get("created_time"),
                            "status_at_discovery": state, "yes_bid": m.get("yes_bid_dollars"), "yes_ask": m.get("yes_ask_dollars"),
                            "last": m.get("last_price_dollars")})
    return out


def capture_quotes(md_root: str, games, as_of: datetime, lookback_hours: float = 12.0) -> list[dict]:
    """Latest captured quote per ticker with observed_at <= as_of, over the lookback window (change-suppressed feed)."""
    gids = set(games["game_id"])
    lo = as_of - timedelta(hours=lookback_hours)
    files = []
    for day in sorted(glob.glob(os.path.join(md_root, "data", "kalshi", "capture", "20*"))):
        for f in glob.glob(os.path.join(day, "*.quotes.jsonl")):
            rd = _run_dt(os.path.basename(f))
            if rd and lo <= rd <= as_of:
                files.append(f)
    latest: dict[str, dict] = {}
    for f in sorted(files):
        for line in open(f):
            try:
                q = json.loads(line)
            except ValueError:
                continue
            if q.get("family") != "PLAYER_STAT" or q.get("stat") not in STAT_MAP or q.get("game_id") not in gids:
                continue
            obs = _utc(q.get("observed_at"))
            if obs is None or obs > as_of:
                continue
            t = q["ticker"]
            prev = latest.get(t)
            if prev is None or obs >= _utc(prev["observed_at"]):
                latest[t] = {"source": "kalshi_capture", "capture_run": q.get("run_id"), "observed_at": obs.isoformat(),
                             "ticker": t, "game_id": q["game_id"], "kalshi_player_id": q.get("player_kalshi_id"),
                             "player_name": q.get("player_name"), "statistic": STAT_MAP[q["stat"]], "threshold": q.get("threshold"),
                             "open_time": q.get("open_time"), "status": q.get("status"), "yes_bid": q.get("yes_bid_dollars"),
                             "yes_ask": q.get("yes_ask_dollars"), "last": q.get("last_price_dollars"), "volume": q.get("volume_fp")}
    return list(latest.values())


def market_rows(md_root: str | None, games, as_of: datetime, map_path: str | None, *, lookback_hours: float = 12.0) -> dict:
    """{'contracts': per-ticker rows, 'cohort': per (game, player, statistic) listing rows, 'status': {...}}."""
    status = {"market_data_root": bool(md_root and os.path.isdir(md_root))}
    if not status["market_data_root"]:
        return {"contracts": [], "cohort": [], "status": {**status, "state": "MARKET_DATA_UNAVAILABLE"}}
    pmap = player_map(map_path)
    disc = latest_discovery(md_root, as_of)
    rows = discovery_listings(disc, games, as_of) if disc else []
    rows += capture_quotes(md_root, games, as_of, lookback_hours)
    status.update({"discovery_run": os.path.basename(disc) if disc else None, "player_map_entries": len(pmap),
                   "n_discovery_rows": sum(r["source"] == "kalshi_discovery" for r in rows),
                   "n_capture_rows": sum(r["source"] == "kalshi_capture" for r in rows), "lookback_hours": lookback_hours})
    cohort: dict[tuple, dict] = {}
    for r in rows:
        r["gsis_id"] = pmap.get(r.get("kalshi_player_id"))
        r["family"] = "KALSHI_PLAYER_STAT_LISTING"
        ot, ob = _utc(r.get("open_time")), _utc(r.get("observed_at"))
        r["listed_at_or_before_as_of"] = bool(ot and ob and ot <= as_of and ob <= as_of)
        if not r["gsis_id"]:
            continue
        k = (r["game_id"], r["gsis_id"], r["statistic"])
        c = cohort.setdefault(k, {"game_id": k[0], "player_id": k[1], "statistic": k[2], "listed_pregame": False,
                                  "earliest_open_time": None, "n_contracts": 0, "tickers": []})
        if r["ticker"] not in c["tickers"]:
            c["tickers"].append(r["ticker"]); c["n_contracts"] += 1
        if r["listed_at_or_before_as_of"]:
            c["listed_pregame"] = True
            if c["earliest_open_time"] is None or ot < _utc(c["earliest_open_time"]):
                c["earliest_open_time"] = ot.isoformat()
    status["n_unmapped_rows"] = sum(1 for r in rows if not r["gsis_id"])
    status["state"] = "OK" if rows else "NO_PLAYER_STAT_LISTINGS_FOUND"
    for c in cohort.values():
        c["tickers"] = sorted(c["tickers"])
    return {"contracts": rows, "cohort": sorted(cohort.values(), key=lambda c: (c["game_id"], c["player_id"], c["statistic"])),
            "status": status}


def incumbent_rows(md_root: str | None, games, as_of: datetime, *, lookback_days: int = 4) -> dict:
    """Latest DATA_PLAYER_V4 / V5 record per (game, player, statistic) with data_cutoff <= as_of, as a diagnostic."""
    if not (md_root and os.path.isdir(md_root)):
        return {"rows": [], "status": {"state": "MARKET_DATA_UNAVAILABLE"}}
    gids = set(games["game_id"])
    out, seen_snap = {}, {}
    files = []
    for arm in INCUMBENT_ARMS:
        for f in glob.glob(os.path.join(md_root, "data", "shadow", "v2", "projections", "*", f"*.{arm}.projections.jsonl.gz")):
            rd = _run_dt(os.path.basename(f))
            if rd and as_of - timedelta(days=lookback_days) <= rd <= as_of:
                files.append((rd, arm, f))
    for rd, arm, f in sorted(files):
        with gzip.open(f, "rt") as fh:
            for line in fh:
                r = json.loads(line)
                if r.get("game_id") not in gids or r.get("stat_family") not in STAT_MAP:
                    continue
                cut = _utc(r.get("data_cutoff"))
                if cut is None or cut > as_of or not r.get("subject_id"):
                    continue
                k = (arm, r["game_id"], r["subject_id"], STAT_MAP[r["stat_family"]])
                snap = r.get("snapshot_id")
                if k in seen_snap and seen_snap[k] > snap:
                    continue
                if seen_snap.get(k) != snap:
                    out[k] = {"family": FAMILY_LABEL, "arm": arm, "engine_version": r.get("engine_version"),
                              "game_id": r["game_id"], "player_id": r["subject_id"], "statistic": k[3], "snapshot_id": snap,
                              "data_cutoff": r.get("data_cutoff"), "kickoff": r.get("kickoff_utc"),
                              "environment_source": (r.get("feature_lineage") or {}).get("env_source"),
                              "distribution_summary": None, "ladder": []}
                    seen_snap[k] = snap
                o = out[k]
                if r.get("distribution_summary") and o["distribution_summary"] is None:
                    o["distribution_summary"] = r["distribution_summary"]
                if r.get("p_yes") is not None and r.get("threshold") is not None:
                    o["ladder"].append({"at_least": r["threshold"], "p_yes": r["p_yes"]})
    rows = sorted(out.values(), key=lambda o: (o["arm"], o["game_id"], o["player_id"], o["statistic"]))
    for o in rows:
        o["ladder"] = sorted({x["at_least"]: x for x in o["ladder"]}.values(), key=lambda x: x["at_least"])
    st = {"state": "OK" if rows else "NO_INCUMBENT_RECORD_AT_OR_BEFORE_AS_OF", "n_files_read": len(files),
          "note": "V4/V5 are market-informed (Kalshi-implied / consensus game environment, market-selected training "
                  "sample and population); recorded for diagnosis only, never scored as PURE"}
    return {"rows": rows, "status": st}
