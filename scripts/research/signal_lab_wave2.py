#!/usr/bin/env python3
"""Football Signal Discovery Lab, Wave 2 (NFL): the prospective research job. RESEARCH ONLY.

    python scripts/research/signal_lab_wave2.py due --existing-from-git origin/market-data [--github-output F]
    python scripts/research/signal_lab_wave2.py run --market-data /tmp/md --out . [--stages observe,enter,settle,report]
    python scripts/research/signal_lab_wave2.py dry-run --week 6 [--market-data /tmp/md]

Stages (each decides for itself what is owed; every record file is WRITE-ONCE under
`data/research/signal_lab_wave2/`, published to `market-data` by the workflow):

  observe  games kicking off in [now+20 min, now+300 min] (2026 REG, week >= 6) without an observation: the frozen
           pregame rows of all three streams (Wave-1 features with phantom rows, ROLE_STABILITY, the frozen ridge
           projection, the WF-TOTAL football features). Market-blind; generated_at < kickoff.
  enter    kicked-off games without an entry: the checkpoint quotes from the change-suppressed capture
           (LAST_VALID_PREKICK_QUOTE_24H for props via close-2.1.0, NFL_PRIMARY_60_180 for totals), identity,
           natural rung, side-specific ask, fee. Only pre-kickoff quote rows are read. A population game with no
           observation becomes a SYSTEM_FAILURE observation -- never reconstructed.
  settle   entered games >= 5 h after kickoff: exchange results (exact), nflverse stats / scores. Written once all
           rows are settled, or after 7 days with the rest SETTLEMENT_PENDING.
  report   cumulative status (reports/<run_id>.status.json) from every record.

`dry-run` evaluates eligibility for a week from pregame inputs only (no outcome, no record written).
Nothing here can place an order, size a position or recommend anything.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import subprocess
import sys
from collections import Counter
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pandas as pd

from nfl_edge.signal_discovery import wave2 as W

GAMES_CSV = ROOT / "data" / "raw" / "nflverse" / "schedules" / "games.csv"


def now_utc() -> datetime:
    return datetime.now(UTC).replace(microsecond=0)


def iso(dt: datetime) -> str:
    return dt.astimezone(UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def parse(s: str) -> datetime:
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=UTC)


def code_sha() -> str | None:
    if os.environ.get("GITHUB_SHA"):
        return os.environ["GITHUB_SHA"]
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except Exception:  # noqa: BLE001
        return None


# --------------------------------------------------------------------------- schedule and record index


REHEARSAL = {"on": False}


def population_games(schedule_csv: Path = GAMES_CSV, weeks: list[int] | None = None) -> pd.DataFrame:
    """The frozen population (2026 REG, week >= 6). `weeks` is for a REHEARSAL only (records marked, never published)."""
    s = pd.read_csv(schedule_csv)
    keep = s["week"].isin(weeks) if weeks else s["week"] >= W.WEEK_ON_OR_AFTER
    s = s[(s["season"] == W.SEASON) & (s["game_type"] == "REG") & keep].copy()
    s["kickoff"] = pd.to_datetime(s["gameday"] + " " + s["gametime"].fillna("13:00")).dt.tz_localize(
        "America/New_York").dt.tz_convert("UTC")
    return s.sort_values(["kickoff", "game_id"]).reset_index(drop=True)


def record_path(kind: str, game_id: str) -> str:
    return f"{W.RECORD_PREFIX}/{W.RECORD_DIRS[kind]}/{W.SEASON}/{game_id}.json"


def existing_records(ref: str | None, market_data: str | None) -> set[str]:
    names: set[str] = set()
    if ref:
        r = subprocess.run(["git", "ls-tree", "-r", "--name-only", ref, W.RECORD_PREFIX], cwd=ROOT,
                           capture_output=True, text=True, timeout=120)
        names |= {x.strip() for x in r.stdout.splitlines() if x.strip()}
    if market_data:
        base = Path(market_data)
        for p in glob.glob(str(base / W.RECORD_PREFIX / "**" / "*.json"), recursive=True):
            names.add(str(Path(p).relative_to(base)))
    return names


def due(now: datetime, games: pd.DataFrame, have: set[str]) -> dict[str, list[str]]:
    """The shared rule (nfl_edge.signal_discovery.wave2_due), so the conductor and this gate never disagree."""
    from nfl_edge.signal_discovery import wave2_due as WD

    rows = [{"game_id": g.game_id, "season": int(g.season), "week": int(g.week), "game_type": g.game_type,
             "kickoff_utc": g.kickoff.to_pydatetime()} for g in games.itertuples()]
    weeks = sorted({int(w) for w in games["week"]}) if REHEARSAL["on"] else None
    return WD.due(rows, now, WD.seen_from_names(have), weeks=weeks)


def capture_days(games: pd.DataFrame, ids: list[str]) -> list[str]:
    days: set[str] = set()
    for g in games[games["game_id"].isin(ids)].itertuples():
        for k in range(8):
            days.add((g.kickoff - pd.Timedelta(days=k)).date().isoformat())
    return sorted(days)


# --------------------------------------------------------------------------- write-once


def write_record(out: Path, kind: str, game_id: str, doc: dict[str, Any], have: set[str]) -> bool:
    rel = record_path(kind, game_id)
    path = out / rel
    if rel in have or path.exists():
        print(f"  refused: {rel} already exists (write-once)")
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(doc, sort_keys=True, indent=1, default=_json_default) + "\n")
    have.add(rel)
    return True


def _json_default(o):
    try:
        import numpy as np

        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, (np.floating,)):
            return None if np.isnan(o) else float(o)
        if isinstance(o, (np.bool_,)):
            return bool(o)
    except Exception:  # noqa: BLE001
        pass
    if isinstance(o, (pd.Timestamp, datetime)):
        return o.isoformat()
    return str(o)


def _clean(v):
    try:
        import math

        if v is None or (isinstance(v, float) and math.isnan(v)):
            return None
    except Exception:  # noqa: BLE001
        pass
    return v


def header(kind: str, g, now: datetime, frozen: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": "nfl_signal_lab_wave2_record/1.0.0", "record": kind, "sport": W.SPORT, "version": W.VERSION,
        "game_id": g.game_id, "season": int(g.season), "week": int(g.week), "home_team": g.home_team,
        "away_team": g.away_team, "kickoff_utc": iso(g.kickoff.to_pydatetime()), "generated_at": iso(now),
        "code_sha": code_sha(), "candidates_sha256": W.CANDIDATES_SHA256, "wf_total_sha256": W.WF_TOTAL_SHA256,
        "prop_models_sha256": W.PROP_MODELS_SHA256, "classifier_sha256": W.CLASSIFIER_SHA256,
        **({"rehearsal": True} if REHEARSAL["on"] else {}),
    }


# --------------------------------------------------------------------------- observe


def pregame(week: int, game_ids: list[str], cutoff: datetime, market_data: str | None, mt=None):
    from nfl_edge.signal_discovery import wave2_pregame as WP

    set1 = json.loads((ROOT / "research" / "signal_discovery_wave1" / "hypotheses_set1.json").read_text())
    gr = WP.game_rows(W.SEASON, week, game_ids, mt)
    pr, meta = WP.player_rows(W.SEASON, week, gr, cutoff, market_data, set1["prop_families"])
    return gr, pr, meta, {f["id"]: f for f in set1["prop_families"]}


def observation_rows(gid: str, gr: pd.DataFrame, pr: pd.DataFrame, meta: dict, fams: dict, frozen: dict) -> list[dict]:
    from nfl_edge.signal_discovery import evaluate_props as EP
    from nfl_edge.signal_discovery.wave2_models import predict_prop

    rows: list[dict] = []
    mine = pr[pr["game_id"] == gid]
    # NFL-PROP-PROS-001: the pregame RB_receptions family (Wave-1 family_rows)
    d = EP.family_rows(mine, fams[W.RB_FAMILY])
    for r in d.to_dict("records"):
        rows.append({"signal_id": W.PROP_001, "status": W.PENDING, "reason": None, "player_id": r["player_id"],
                     "team": r["team"], "position": r["position"], "family": W.RB_FAMILY,
                     "sh_target_l": _clean(float(r["sh_target_l"])), "n_prior": int(r["n_prior"]),
                     "b_season": _clean(float(r["b_season.receptions"])),
                     "role_stability": r["role_stability"], "avail_state": r.get("avail_state")})
    # NFL-PROP-PROS-002: ROLE_CHANGE rows of the eleven families, with the frozen projection
    if not meta["injury_vintage"]["resolved"]:
        rows.append({"signal_id": W.PROP_002, "status": W.SYSTEM_FAILURE, "reason": "INJURY_VINTAGE_UNAVAILABLE",
                     "detail": meta["injury_vintage"].get("reason")})
    else:
        for fid in W.ROLE_FAMILIES:
            fam = fams[fid]
            d = EP.family_rows(mine, fam)
            d = d[d["role_stability"] == "ROLE_CHANGE"]
            params = frozen["props"]["families"].get(fid)
            if d.empty or params is None:
                continue
            pred = predict_prop(params, d)
            for (r, p) in zip(d.to_dict("records"), pred, strict=True):
                rows.append({"signal_id": W.PROP_002, "status": W.PENDING, "reason": None, "player_id": r["player_id"],
                             "team": r["team"], "position": r["position"], "family": fid, "stat": fam["stat"],
                             "kalshi_stat": fam["kalshi_stat"], "pred": float(p),
                             "median_offset": params["median_offset"],
                             "model_median": float(p) + params["median_offset"], "role_stability": "ROLE_CHANGE"})
    # NFL-GAME-PROS-001: football inputs of WF-TOTAL (the market total is joined only at the checkpoint)
    g = gr[gr["game_id"] == gid]
    feats = {}
    if len(g):
        g = g.iloc[0]
        for f in ("baseline.total", "env.plays", "env.sec_per_play", "def_quality_sum.epa", "off_quality_sum.epa"):
            feats[f] = _clean(None if g.get(f) is None else float(g.get(f)))
    ok = len(feats) == 5 and all(v is not None for v in feats.values())
    rows.append({"signal_id": W.GAME_001, "status": W.PENDING if ok else W.EXCLUDED_PROTOCOL,
                 "reason": None if ok else "FOOTBALL_FEATURE_MISSING", "football": feats,
                 "history_through": None if not len(gr[gr["game_id"] == gid]) else gr[gr["game_id"] == gid].iloc[0].get("history_through")})
    return rows


def stage_observe(now, games, ids, market_data, out, have, frozen) -> dict:
    if not ids:
        return {"observed": 0}
    from nfl_edge.signal_discovery import game_features as G

    mt = G.metric_table(range(2012, W.SEASON + 1))
    done, errors = 0, []
    sel = games[games["game_id"].isin(ids)]
    for week, part in sel.groupby("week"):
        try:
            gr, pr, meta, fams = pregame(int(week), part["game_id"].tolist(), now, market_data, mt)
        except Exception as exc:  # noqa: BLE001 -- retried next run; SYSTEM_FAILURE if kickoff passes
            errors.append({"week": int(week), "error": f"{type(exc).__name__}: {exc}"})
            continue
        for g in part.itertuples():
            if now >= g.kickoff.to_pydatetime():
                continue  # never observe at/after kickoff
            doc = header(W.OBSERVATION, g, now, frozen)
            doc.update({"pregame_inputs": meta, "rows": observation_rows(g.game_id, gr, pr, meta, fams, frozen)})
            done += write_record(out, W.OBSERVATION, g.game_id, doc, have)
    return {"observed": done, "errors": errors}


# --------------------------------------------------------------------------- enter


def capture_meta(capture_root: str, gid: str, kickoff: datetime) -> dict[str, dict]:
    """Per ticker: the contract identity fields of its captured rows (from pre-kickoff rows only)."""
    from nfl_edge.shadow.quote_history import capture_days as cdays

    meta: dict[str, dict] = {}
    for day in cdays(capture_root, kickoff.isoformat(), 7):
        for path in sorted(glob.glob(os.path.join(day, "*.quotes.jsonl"))):
            with open(path) as fh:
                for line in fh:
                    if gid not in line:
                        continue
                    r = json.loads(line)
                    if r.get("game_id") != gid:
                        continue
                    ts = r.get("observed_at")
                    if not ts or parse(ts) >= kickoff:
                        continue
                    meta[r["ticker"]] = {k: r.get(k) for k in ("series_ticker", "family", "period", "stat", "team", "player_name",
                                                            "player_kalshi_id", "threshold", "operator", "event_ticker")}
    return meta


def total_checkpoint(ci, runs, ticker: str, kickoff: datetime) -> dict | None:
    """NFL_PRIMARY_60_180: the last complete-run confirmation in [k-180, k-60] and its price row."""
    close = kickoff - timedelta(minutes=W.PRIMARY_CLOSE_MIN)
    conf = runs.confirmation(ticker, W.TOTAL_SERIES, close + timedelta(seconds=1))
    if not conf or conf["confirmed_at_dt"] < kickoff - timedelta(minutes=W.PRIMARY_OPEN_MIN):
        return None
    rows = [q for q in ci.quotes.get(ticker, []) if q.get("observed_ts") is not None
            and q["observed_ts"] <= conf["confirmed_at_dt"].timestamp()]
    if not rows or rows[-1].get("status") not in ("active", "open", None, ""):
        return None
    last = rows[-1]
    return {"yes_bid": last["yes_bid"], "yes_ask": last["yes_ask"], "no_bid": last["no_bid"], "no_ask": last["no_ask"],
            "confirmed_at": conf["confirmed_at"], "price_observed_at": last["observed_at"]}


def stage_enter(now, games, ids, market_data, out, have, frozen) -> dict:
    from nfl_edge.evaluation import close as CL
    from nfl_edge.evaluation import openset as OS
    from nfl_edge.execution.fees import load_fee_schedule
    from nfl_edge.signal_discovery.markets import (
        TEAM_FIX,
        Resolver,
        _jersey_from_ticker,
    )

    capture_root = os.path.join(market_data, "data", "kalshi", "capture")
    runs = CL.CaptureRuns(capture_root)
    led = OS.OpenSetLedger(capture_root)
    led = led if led.runs else None
    fees = load_fee_schedule(str(ROOT))
    resolver = Resolver(W.SEASON)
    written = 0
    for g in games[games["game_id"].isin(ids)].itertuples():
        kickoff = g.kickoff.to_pydatetime()
        obs_rel = record_path(W.OBSERVATION, g.game_id)
        obs_path = Path(market_data) / obs_rel if (Path(market_data) / obs_rel).exists() else out / obs_rel
        if not obs_path.exists():
            doc = header(W.OBSERVATION, g, now, frozen)
            doc["rows"] = [{"signal_id": s, "status": W.SYSTEM_FAILURE, "reason": "NO_OBSERVATION_BEFORE_KICKOFF"} for s in W.STREAMS]
            written += write_record(out, W.OBSERVATION, g.game_id, doc, have)
            continue
        obs = json.loads(obs_path.read_text())
        meta = capture_meta(capture_root, g.game_id, kickoff)
        ci = CL.CloseIndex(capture_root, g.game_id, iso(kickoff), runs=runs, days_back=7, openset=led)
        # prop ladders at LAST_VALID_PREKICK_QUOTE_24H, keyed by (gsis, stat)
        ladders: dict[tuple[str, str], list[dict]] = {}
        id_fail: list[dict] = []
        for t, m in meta.items():
            if m.get("family") != "PLAYER_STAT" or m.get("period") not in ("FULL", None) or m.get("operator") not in (">=", None):
                continue
            team = TEAM_FIX.get(m.get("team"), m.get("team"))
            gsis, how = resolver.resolve(m.get("player_name"), team, _jersey_from_ticker(t))
            if how not in W.ACCEPTED_IDENTITY:
                id_fail.append({"ticker": t, "player_name": m.get("player_name"), "player_kalshi_id": m.get("player_kalshi_id"),
                                "stat": m.get("stat"), "identity": how})
                continue
            c = ci.select(t, series_ticker=m.get("series_ticker"))
            if not W.prop_checkpoint_ok(c, kickoff.timestamp()):
                continue
            ladders.setdefault((gsis, m["stat"]), []).append(
                {"ticker": t, "threshold": m.get("threshold"), "series": m.get("series_ticker"), "player_kalshi_id": m.get("player_kalshi_id"),
                 "yes_bid": c.get("yes_bid"), "yes_ask": c.get("yes_ask"), "no_bid": c.get("no_bid"), "no_ask": c.get("no_ask"),
                 "confirmed_at": c.get("confirmed_at"), "close_quality": c.get("close_quality")})
        offered = {(k[0], k[1]) for k in ladders}
        any_ladder_stats = {m.get("stat") for m in meta.values() if m.get("family") == "PLAYER_STAT"}

        def fee_fn_for(series, as_of):
            def fee_fn(price):
                q = fees.taker_fee(price, 1.0, series, as_of=as_of)
                return (q.amount, q.state) if q.state == "KNOWN" and q.amount is not None else (None, q.state)
            return fee_fn

        rows = []
        for o in obs["rows"]:
            if o["status"] != W.PENDING:
                continue
            sid = o["signal_id"]
            base = {k: o.get(k) for k in ("signal_id", "player_id", "team", "position", "family", "stat", "kalshi_stat",
                                          "pred", "median_offset", "model_median")}
            if sid in (W.PROP_001, W.PROP_002):
                kstat = "receptions" if sid == W.PROP_001 else o["kalshi_stat"]
                rungs = ladders.get((o["player_id"], kstat))
                if not rungs:
                    status = W.MARKET_NOT_OFFERED if kstat not in any_ladder_stats or (o["player_id"], kstat) not in offered else W.ENTRY_UNAVAILABLE
                    rows.append({**base, "status": status, "reason": "NO_LADDER_AT_CHECKPOINT"})
                    continue
                lad = W.ladder(rungs)
                nat = lad["natural"]
                series = rungs[0]["series"]
                entry = {**base, "ladder": {k: lad[k] for k in ("rungs", "valid_rungs", "market_median", "rungs_used")},
                         "market_median": lad["market_median"], "natural": nat, "player_kalshi_id": rungs[0]["player_kalshi_id"],
                         "checkpoint": "LAST_VALID_PREKICK_QUOTE_24H"}
                if sid == W.PROP_001:
                    if nat is None:
                        rows.append({**entry, "status": W.ENTRY_UNAVAILABLE, "reason": "NO_VALID_RUNG"})
                        continue
                    if lad["market_median"] is None:
                        rows.append({**entry, "status": W.ENTRY_UNAVAILABLE, "reason": "NO_MARKET_MEDIAN"})
                        continue
                    c = W.contract(nat, "no", fee_fn_for(series, nat.get("confirmed_at")))
                    # the checkpoint IS the canonical close here, so CLV is recorded but is 0 by construction
                    rows.append({**entry, "contract": c, "ticker": c.get("ticker"), "rung": c.get("threshold"),
                                 "side": "no", "ask": c.get("ask"), "fee": c.get("fee"),
                                 "clv": W.clv(ci.select(c["ticker"], series_ticker=series) if c.get("ticker") else None, c),
                                 "status": c["status"], "reason": c.get("reason")})
                else:
                    if lad["market_median"] is None:
                        rows.append({**entry, "status": W.ENTRY_UNAVAILABLE, "reason": "NO_MARKET_MEDIAN"})
                        continue
                    c = None
                    if nat is not None:  # secondary economics: the Wave-1 pre-registered prop rule, unchanged
                        t = float(nat["threshold"])
                        mm = o["model_median"]
                        side = "yes" if mm >= t * (1 + W.WAVE1_ECON_MARGIN) + 1e-9 else "no" if mm <= t * (1 - W.WAVE1_ECON_MARGIN) - 1e-9 else None
                        c = W.contract(nat, side, fee_fn_for(series, nat.get("confirmed_at"))) if side else {"status": "NO_SIDE_UNDER_WAVE1_RULE"}
                    cl = W.clv(ci.select(c["ticker"], series_ticker=series), c) if c and c.get("ticker") else None
                    rows.append({**entry, "contract": c, "clv": cl, "status": W.ELIGIBLE, "reason": None})
            elif sid == W.GAME_001:
                rungs = []
                for t, m in meta.items():
                    if m.get("series_ticker") != W.TOTAL_SERIES or m.get("family") != "TOTAL":
                        continue
                    q = total_checkpoint(ci, runs, t, kickoff)
                    if q:
                        rungs.append({"ticker": t, "threshold": m.get("threshold"), **q})
                total_offered = any(m.get("series_ticker") == W.TOTAL_SERIES for m in meta.values())
                if not rungs:
                    rows.append({"signal_id": sid, "status": W.ENTRY_UNAVAILABLE if total_offered else W.MARKET_NOT_OFFERED,
                                 "reason": "NO_TOTAL_QUOTE_IN_PRIMARY_60_180", "checkpoint": "NFL_PRIMARY_60_180"})
                    continue
                lad = W.ladder(rungs)
                k_total = lad["market_median"]
                p = W.total_prediction(frozen["wf_total"], o["football"], k_total)
                entry = {"signal_id": sid, "checkpoint": "NFL_PRIMARY_60_180", "market_implied_total": k_total,
                         "ladder": {k: lad[k] for k in ("rungs", "valid_rungs", "rungs_used")}, "prediction": p,
                         "football": o["football"]}
                if p is None:
                    rows.append({**entry, "status": W.ENTRY_UNAVAILABLE, "reason": "NO_MARKET_IMPLIED_TOTAL"})
                    continue
                if abs(p) < W.TOTAL_THRESHOLD:
                    rows.append({**entry, "status": W.EXCLUDED_PROTOCOL, "reason": "ABS_PREDICTION_BELOW_2"})
                    continue
                side = "OVER" if p > 0 else "UNDER"
                c = W.contract(lad["natural"], "yes" if side == "OVER" else "no",
                               fee_fn_for(W.TOTAL_SERIES, (lad["natural"] or {}).get("confirmed_at")))
                rows.append({**entry, "side": side, "contract": c, "ticker": c.get("ticker"), "rung": c.get("threshold"),
                             "ask": c.get("ask"), "fee": c.get("fee"),
                             "clv": W.clv(ci.select(c["ticker"], series_ticker=W.TOTAL_SERIES) if c.get("ticker") else None, c),
                             "status": W.ELIGIBLE, "reason": None})
        doc = header(W.ENTRY, g, now, frozen)
        doc.update({"observation_generated_at": obs["generated_at"], "rows": rows,
                    "identity_failures": id_fail, "capture": {"tickers_seen": len(meta), "close_stats": ci.stats}})
        written += write_record(out, W.ENTRY, g.game_id, doc, have)
    return {"entered": written}


# --------------------------------------------------------------------------- settle


def stage_settle(now, games, ids, market_data, out, have, frozen, *, fetch_exchange=True) -> dict:
    from nfl_edge.settlement import kalshi_settlement as KS
    from nfl_edge.sim import data as D

    pg = pd.DataFrame(D.load("player_games", [W.SEASON]).to_dicts())
    if pg.empty:
        pg = pd.DataFrame(columns=["game_id", "player_id", "offense_snaps"])
    sched = pd.DataFrame(D.schedule().to_dicts())
    written = 0
    for g in games[games["game_id"].isin(ids)].itertuples():
        kickoff = g.kickoff.to_pydatetime()
        rel = record_path(W.ENTRY, g.game_id)
        p = Path(market_data) / rel if (Path(market_data) / rel).exists() else out / rel
        ent = json.loads(p.read_text())
        rows_in = [r for r in ent["rows"] if r["status"] == W.ELIGIBLE]
        tickers = sorted({(r.get("contract") or {}).get("ticker") for r in rows_in if (r.get("contract") or {}).get("ticker")})
        exch: dict[str, float] = {}
        if fetch_exchange and tickers:
            try:
                from nfl_edge.kalshi.client import KalshiClient

                events = sorted({t.rsplit("-", 1)[0] for t in tickers})
                outcome = KS.fetch_game_settlements(KalshiClient(rps=4.0), events, tickers)
                for m in outcome.markets:
                    rec = KS.settlement_record(m, source="KALSHI_LIVE_SETTLED")
                    pay, _ = KS.exact_yes_payout(rec)
                    if pay is not None:
                        exch[m["ticker"]] = float(pay)
            except Exception as exc:  # noqa: BLE001 -- the stat fallback may still settle; else pending
                print(f"::warning::{g.game_id}: exchange settlements unavailable ({type(exc).__name__})")
        mine = pg[pg["game_id"] == g.game_id]
        stats_final = len(mine) > 0
        by_player = {r["player_id"]: r for r in mine.to_dict("records")}
        srow = sched[sched["game_id"] == g.game_id]
        total = None
        if len(srow) and pd.notna(srow.iloc[0]["home_score"]) and pd.notna(srow.iloc[0]["away_score"]):
            total = float(srow.iloc[0]["home_score"]) + float(srow.iloc[0]["away_score"])
        rows, pending = [], 0
        for r in rows_in:
            sid = r["signal_id"]
            c = r.get("contract") or {}
            if sid == W.GAME_001:
                if total is None:
                    rows.append({**_slim(r), "status": W.SETTLEMENT_PENDING})
                    pending += 1
                    continue
                k = r["market_implied_total"]
                sign = 1.0 if r["side"] == "OVER" else -1.0
                value = exch.get(c.get("ticker")) if c.get("ticker") in exch else None
                value = W.contract_value_by_exchange(c, value) if value is not None else (
                    (1.0 if W.contract_pays_by_stat(c, total) else 0.0) if c.get("status") == W.ELIGIBLE else None)
                rows.append({**_slim(r), "status": W.SETTLED, "actual_total": total,
                             "signed_residual": sign * (total - k), "economics": W.economics(c, value)})
                continue
            pl = by_player.get(r["player_id"])
            played = pl is not None and (pl.get("offense_snaps") or 0) >= 1
            if sid == W.PROP_002:
                if not stats_final:
                    rows.append({**_slim(r), "status": W.SETTLEMENT_PENDING})
                    pending += 1
                    continue
                if not played:
                    rows.append({**_slim(r), "status": W.EXCLUDED_PROTOCOL, "reason": "DID_NOT_PLAY"})
                    continue
                actual = float(pl[r["stat"]])
                mm, md = float(r["model_median"]), float(r["market_median"])
                rows.append({**_slim(r), "status": W.SETTLED, "actual": actual,
                             "d": abs(md - actual) - abs(mm - actual), "game_id": g.game_id})
                continue
            # PROP_001: the exchange result first; the stat of a player who played otherwise
            value = None
            if c.get("ticker") in exch:
                value = W.contract_value_by_exchange(c, exch[c["ticker"]])
            elif played:
                value = 1.0 if W.contract_pays_by_stat(c, float(pl["receptions"])) else 0.0
            if value is None:
                rows.append({**_slim(r), "status": W.SETTLEMENT_PENDING, "played": played})
                pending += 1
                continue
            rows.append({**_slim(r), "status": W.SETTLED, "played": played, "game_id": g.game_id,
                         "actual": float(pl["receptions"]) if played else None,
                         "settlement_source": "EXCHANGE" if c.get("ticker") in exch else "NFLVERSE_STAT",
                         "economics": W.economics(c, value)})
        age_h = (now - kickoff).total_seconds() / 3600
        if pending and age_h < W.SETTLEMENT_GIVE_UP_HOURS:
            print(f"  {g.game_id}: {pending} row(s) still pending; settlement deferred")
            continue
        doc = header(W.SETTLEMENT, g, now, frozen)
        doc.update({"entry_generated_at": ent["generated_at"], "rows": rows,
                    "sources": {"exchange_results": len(exch), "nflverse_player_rows": len(mine), "final_total": total}})
        written += write_record(out, W.SETTLEMENT, g.game_id, doc, have)
    return {"settled": written}


def _slim(r: dict) -> dict:
    keep = ("signal_id", "player_id", "team", "position", "family", "stat", "kalshi_stat", "model_median", "market_median",
            "market_implied_total", "prediction", "side", "contract", "ticker", "rung", "ask", "fee", "clv")
    return {k: r.get(k) for k in keep if k in r}


# --------------------------------------------------------------------------- report


def stage_report(now, market_data, out, run_id: str) -> dict:
    docs = {}
    for base in [Path(market_data) if market_data else None, out]:
        if base is None:
            continue
        for p in glob.glob(str(base / W.RECORD_PREFIX / "*" / str(W.SEASON) / "*.json")):
            docs[str(Path(p).relative_to(base))] = json.loads(Path(p).read_text())
    by_kind: dict[str, list[dict]] = {k: [] for k in W.RECORD_DIRS}
    for d in docs.values():
        by_kind[d["record"]].append(d)
    settled_rows = [{**r, "game_id": r.get("game_id") or d["game_id"]} for d in by_kind[W.SETTLEMENT] for r in d["rows"]]
    streams = {}
    for sid in W.STREAMS:
        streams[sid] = {
            "observation_rows": dict(Counter(r["status"] for d in by_kind[W.OBSERVATION] for r in d["rows"] if r["signal_id"] == sid)),
            "observation_reasons": dict(Counter(str(r.get("reason")) for d in by_kind[W.OBSERVATION] for r in d["rows"] if r["signal_id"] == sid and r.get("reason"))),
            "entry_rows": dict(Counter(r["status"] for d in by_kind[W.ENTRY] for r in d["rows"] if r["signal_id"] == sid)),
            "entry_reasons": dict(Counter(str(r.get("reason")) for d in by_kind[W.ENTRY] for r in d["rows"] if r["signal_id"] == sid and r.get("reason"))),
            "settlement_rows": dict(Counter(r["status"] for r in settled_rows if r["signal_id"] == sid)),
            "summary": W.summarize(sid, settled_rows),
        }
    report = {
        "schema": "nfl_signal_lab_wave2_status/1.0.0", "version": W.VERSION, "generated_at": iso(now), "run_id": run_id,
        "candidates_sha256": W.CANDIDATES_SHA256, "population": f"{W.SEASON} REG week >= {W.WEEK_ON_OR_AFTER}",
        "kind": "PROSPECTIVE research state only: no recommendation, no sizing, not read by any pricing or board path.",
        "games": {k: len(v) for k, v in by_kind.items()},
        "identity_failures": sum(len(d.get("identity_failures") or []) for d in by_kind[W.ENTRY]),
        "system_failures": sum(1 for d in by_kind[W.OBSERVATION] for r in d["rows"] if r["status"] == W.SYSTEM_FAILURE),
        "streams": streams, "never_emitted": ["EDGE_CONFIRMED"],
    }
    path = out / W.RECORD_PREFIX / "reports" / f"{run_id}.status.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(report, indent=1, sort_keys=True, default=_json_default) + "\n")
    return report


# --------------------------------------------------------------------------- dry run


def dry_run(week: int, cutoff: datetime, market_data: str | None) -> dict:
    """Eligibility only, from pregame inputs. No outcome is read and no record is written."""
    frozen = W.load_frozen(ROOT)
    s = pd.read_csv(GAMES_CSV)
    s = s[(s["season"] == W.SEASON) & (s["week"] == week)]
    gr, pr, meta, fams = pregame(week, s["game_id"].tolist(), cutoff, market_data)
    per_game = {}
    for gid in s["game_id"]:
        rows = observation_rows(gid, gr, pr, meta, fams, frozen)
        per_game[gid] = dict(Counter(f"{r['signal_id']}:{r['status']}" for r in rows))
    tot = Counter()
    for v in per_game.values():
        tot.update(v)
    return {"week": week, "cutoff": iso(cutoff), "kind": "ELIGIBILITY DRY RUN: pregame inputs only",
            "in_population": week >= W.WEEK_ON_OR_AFTER, "pregame_inputs": meta, "totals": dict(tot), "per_game": per_game}


# --------------------------------------------------------------------------- CLI


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    d = sub.add_parser("due")
    d.add_argument("--existing-from-git", default=None)
    d.add_argument("--now", default=None)
    d.add_argument("--github-output", default=None)
    r = sub.add_parser("run")
    r.add_argument("--market-data", required=True)
    r.add_argument("--out", default=".")
    r.add_argument("--now", default=None)
    r.add_argument("--existing-from-git", default=None)
    r.add_argument("--stages", default="observe,enter,settle,report")
    r.add_argument("--run-id", default=None)
    r.add_argument("--no-exchange-fetch", action="store_true")
    r.add_argument("--rehearsal-weeks", default=None, help="REHEARSAL ONLY: comma list of weeks; records are marked and never published")
    dy = sub.add_parser("days", help="capture days (UTC dates) a rehearsal of these weeks needs")
    dy.add_argument("--weeks", required=True)
    dr = sub.add_parser("dry-run")
    dr.add_argument("--week", type=int, required=True)
    dr.add_argument("--cutoff", default=None)
    dr.add_argument("--market-data", default=None)
    dr.add_argument("--out", default=None)
    a = ap.parse_args(argv)
    if a.cmd == "days":
        weeks = [int(x) for x in a.weeks.split(",")]
        g = population_games(weeks=weeks)
        print(" ".join(capture_days(g, g["game_id"].tolist())))
        return 0
    if a.cmd == "dry-run":
        res = dry_run(a.week, parse(a.cutoff) if a.cutoff else now_utc(), a.market_data)
        text = json.dumps(res, indent=1, sort_keys=True, default=_json_default)
        if a.out:
            Path(a.out).write_text(text + "\n")
        print(json.dumps(res["totals"], indent=1, sort_keys=True))
        return 0
    now = parse(a.now) if a.now else now_utc()
    weeks = [int(x) for x in a.rehearsal_weeks.split(",")] if getattr(a, "rehearsal_weeks", None) else None
    REHEARSAL["on"] = bool(weeks)
    games = population_games(weeks=weeks)
    if a.cmd == "due":
        have = existing_records(a.existing_from_git, None)
        dd = due(now, games, have)
        print(json.dumps({"now": iso(now), **{k: v for k, v in dd.items()}}, indent=1))
        if a.github_output:
            ids = sorted(set(dd["observe"]) | set(dd["enter"]) | set(dd["settle"]))
            with open(a.github_output, "a") as fh:
                fh.write(f"due={'true' if ids else 'false'}\n")
                fh.write(f"observe={'true' if dd['observe'] else 'false'}\n")
                fh.write(f"settle={'true' if dd['settle'] else 'false'}\n")
                fh.write(f"capture_days={' '.join(capture_days(games, dd['enter']))}\n")
        return 0
    frozen = W.load_frozen(ROOT)
    out = Path(a.out)
    have = existing_records(a.existing_from_git, a.market_data)
    dd = due(now, games, have)
    stages = set(a.stages.split(","))
    res: dict[str, Any] = {"now": iso(now), "due": dd}
    if "observe" in stages:
        res["observe"] = stage_observe(now, games, dd["observe"], a.market_data, out, have, frozen)
    if "enter" in stages:
        res["enter"] = stage_enter(now, games, dd["enter"], a.market_data, out, have, frozen)
        dd = due(now, games, have)
    if "settle" in stages:
        res["settle"] = stage_settle(now, games, dd["settle"], a.market_data, out, have, frozen,
                                     fetch_exchange=not a.no_exchange_fetch)
    if "report" in stages:
        rep = stage_report(now, a.market_data, out, a.run_id or now.strftime("%Y%m%dT%H%M%SZ"))
        res["report"] = {sid: v["summary"].get("display") or v["summary"].get("n") for sid, v in rep["streams"].items()}
    print(json.dumps(res, indent=1, sort_keys=True, default=_json_default))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
