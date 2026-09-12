#!/usr/bin/env python3
"""Capture order-book DEPTH at the projection horizons, for the contracts the model actually prices.

    python3 scripts/shadow_v2/capture_depth_v2.py --market-data <md> --out data/shadow/v2 --budget 4000

WHY A SEPARATE JOB
------------------
The 10-minutely capture already fetches books, but it is capacity-bound in a way that quietly destroys the
question this data has to answer. Measured on the live board (2026-09-10 discovery): 10,591 book candidates per
run against a 2,500 cap, and 9,948 unique probability-carrying tickers of which only 16.4% ended up with a book
at the horizon. The other 83.6% are not thin markets -- they are unobserved markets, and the difference is the
whole point.

Depth is not needed every ten minutes. It is needed AT THE HORIZONS, for the games in that horizon's window.
That is a much smaller and entirely feasible job: 7,723 probability-carrying tickers sit inside the 72-hour book
window across 29 games, so one horizon touching a single Sunday's games is a few thousand requests -- about 16
minutes at 4 req/s, inside a dedicated workflow timeout, and it never competes with the quote capture the
incumbent experiment depends on.

THE PRIORITY FUNCTION DELIBERATELY IGNORES OUR OWN EDGE
-------------------------------------------------------
The obvious ordering -- capture depth where the model disagrees most with the market -- would poison the
research it exists to serve. Depth-conditional results would then be computed on a sample selected by the very
quantity under study, and "edges survive size" would be indistinguishable from "we only measured size where we
had an edge". So the priority uses MARKET properties only:

    1. the game kicks off soonest          (closest to the horizon being frozen)
    2. whole LADDERS move together         (a half-captured player ladder cannot be read as a distribution)
    3. traded before untraded              (volume is a market fact, not a model opinion)
    4. ticker, alphabetically              (a deterministic, reproducible tie-break)

Nothing in that list is a function of `contract_value`, disagreement, or arm. A contract's chance of being
captured is therefore independent of whether the model liked it, which is what makes the resulting
depth-conditional analysis honest.

EVERYTHING SKIPPED IS RECORDED WITH ITS REASON
----------------------------------------------
A missing book must never read as an absent or thin market. Every candidate that does not get one is written to
the manifest under DROPPED_BY_BUDGET / OUTSIDE_BOOK_WINDOW / SERIES_TIER_NOT_FULL / FETCH_FAILED, and the
per-ladder completeness is recorded so research can require whole ladders. Depth coverage is reported
separately, by disagreement band, so any residual selection effect is visible rather than assumed away.

Writes (never to market-data from a branch run):
    <out>/depth/<YYYY-MM-DD>/<run_id>.depth.jsonl.gz     one row per captured book
    <out>/depth/<YYYY-MM-DD>/<run_id>.depth_manifest.json attempted / captured / skipped with reasons + budget
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sys
import time
from datetime import datetime, timedelta, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.kalshi.client import KalshiClient                                            # noqa: E402
from nfl_edge.shadow_v2 import pit
from nfl_edge.shadow_v2.capture_io import load_latest_quotes                               # noqa: E402

DEPTH_CAPTURE_VERSION = "depth-capture-1.0.0"
BOOK_DEPTH = 10                                    # levels per side, the same depth the incumbent capture asks for
SKIP_BUDGET = "DROPPED_BY_BUDGET"
SKIP_WINDOW = "OUTSIDE_BOOK_WINDOW"
SKIP_TIER = "SERIES_TIER_NOT_FULL"
SKIP_FAILED = "FETCH_FAILED"
SKIP_NO_TIME = "INSUFFICIENT_TIME_BEFORE_KICKOFF"
SKIP_POST_KICKOFF = "RESPONSE_AFTER_KICKOFF"
# never start a request within this many seconds of kickoff
KICKOFF_SAFETY_S = 60.0
# the instant each horizon aims at, in minutes before kickoff. The TARGET and the ACTUAL
# observation are separate facts and both are written on every row.
HORIZON_TARGET_MIN = {"T-24h": 1440.0, "T-6h": 360.0, "T-90m": 90.0, "T-30m": 30.0}


def horizon_quality_of(actual_min, target_min):
    """How close this observation actually landed to the horizon it was aiming at."""
    if actual_min is None:
        return "NO_KICKOFF"
    if target_min is None:
        return "UNTARGETED"
    d = target_min - actual_min          # positive = later than the target
    if abs(d) <= 10.0:
        return "ON_TIME"
    if d > 0:
        return "LATE_ACCEPTABLE" if d <= 45.0 else "LATE_DEGRADED"
    return "EARLY"


def log(m):
    print(m, flush=True)


_NOW_OVERRIDE = None


def now_utc():
    """The wall clock, or the rehearsal instant. Only --now (offline planning) ever overrides it."""
    return _NOW_OVERRIDE or datetime.now(timezone.utc)


def priority(row) -> tuple:
    """Market properties only. See the module docstring: the model's own view is deliberately absent."""
    mtk = row.get("minutes_to_kickoff")
    return (0 if mtk is not None else 1,                       # games before undated season markets
            mtk if mtk is not None else 1e9,                   # soonest kickoff first
            row.get("event_ticker") or "",                     # ladders contiguous
            row.get("series_ticker") or "",
            0 if (row.get("volume") or 0) > 0 else 1,          # traded before untraded
            row.get("ticker") or "")


def candidates(quotes: dict, priced: set, *, window_min: float) -> tuple[list, list]:
    """Probability-carrying tickers inside the book window, ordered; plus everything excluded with its reason."""
    take, skip = [], []
    for t, q in quotes.items():
        if priced and t not in priced:
            continue
        # recomputed from the kickoff and the CURRENT instant: the snapshot's own minutes_to_kickoff is as old
        # as the snapshot, and using it would size the window against a market observation rather than now.
        ko = pit.as_utc(q.get("kickoff_utc"))
        mtk = ((ko - now_utc()).total_seconds() / 60.0) if ko else None
        row = {"ticker": t, "event_ticker": q.get("event_ticker"), "series_ticker": q.get("series_ticker"),
               "game_id": q.get("game_id"), "kickoff_utc": q.get("kickoff_utc"), "minutes_to_kickoff": mtk,
               "volume": float(q.get("volume_fp") or 0) if q.get("volume_fp") not in (None, "") else 0.0}
        if mtk is not None and (mtk < 0 or mtk > window_min):
            skip.append({**row, "reason": SKIP_WINDOW})
            continue
        take.append(row)
    take.sort(key=priority)
    return take, skip


def ladder_key(row):
    return (row.get("event_ticker"), row.get("series_ticker"))


def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "v2"))
    ap.add_argument("--snapshot-id", default=None)
    ap.add_argument("--budget", type=int, default=4000, help="maximum order-book requests this run")
    ap.add_argument("--window-hours", type=float, default=72.0)
    ap.add_argument("--rps", type=float, default=4.0)
    ap.add_argument("--horizon-label", default=None)
    ap.add_argument("--priced-from", default=None, help="a projections jsonl.gz to restrict to priced tickers")
    ap.add_argument("--dry-run", action="store_true", help="plan and report capacity without fetching anything")
    ap.add_argument("--now", default="", help="rehearsal only: stand at this instant when judging the window and "
                                              "the kickoff safety rule, so a Sunday cluster can be measured offline")
    a = ap.parse_args(argv)
    global _NOW_OVERRIDE
    if a.now:
        _NOW_OVERRIDE = pit.as_utc(a.now)
        if not a.dry_run:
            raise SystemExit("--now is a rehearsal device and may only be used with --dry-run")
    t0 = time.time()
    run_id = now_utc().strftime("%Y%m%dT%H%M%SZ")
    capture_root = os.path.join(a.market_data, "data", "kalshi", "capture")
    quotes, run_ts, ages, confirmed, man = load_latest_quotes(capture_root, snapshot_id=a.snapshot_id or None)
    if not quotes:
        log("no capture quotes found")
        return 2
    tiers = {s: (v or {}).get("tier") for s, v in (man.get("series") or {}).items()}
    priced = set()
    for p in sorted(glob.glob(a.priced_from or "")):
        for line in gzip.open(p, "rt"):
            r = json.loads(line)
            if (r.get("flags") or {}).get("has_probability"):
                priced.add(r["ticker"])
    take, skip = candidates(quotes, priced, window_min=a.window_hours * 60)
    # a series the capture does not poll at FULL tier has no book to ask for at any price
    keep = []
    for r in take:
        if tiers.get(r.get("series_ticker")) != "FULL_MICROSTRUCTURE":
            skip.append({**r, "reason": SKIP_TIER})
        else:
            keep.append(r)
    # The budget cuts at LADDER boundaries, never inside one. A player threshold ladder with a hole in it
    # cannot be read as a distribution, so half a ladder is worth much less than none of it plus a whole one
    # elsewhere -- and a hole whose position depends on where the cap happened to fall is a selection effect in
    # the shape of the ladder itself.
    ladders, order = {}, []
    for r in keep:
        k = ladder_key(r)
        if k not in ladders:
            ladders[k] = {"n": 0, "planned": 0}
            order.append(k)
        ladders[k]["n"] += 1
    admitted, spent = set(), 0
    for k in order:                                   # priority order; stop at the first ladder that does not fit
        if spent + ladders[k]["n"] > a.budget:
            break
        admitted.add(k)
        spent += ladders[k]["n"]
    planned = [r for r in keep if ladder_key(r) in admitted]
    dropped = [r for r in keep if ladder_key(r) not in admitted]
    for r in dropped:
        skip.append({**r, "reason": SKIP_BUDGET})
    for r in planned:
        ladders[ladder_key(r)]["planned"] += 1
    whole = sum(1 for v in ladders.values() if v["planned"] == v["n"])
    partial = sum(1 for v in ladders.values() if 0 < v["planned"] < v["n"])
    log(f"snapshot {run_ts:%Y%m%dT%H%M%SZ}: {len(quotes)} tickers, {len(keep)} in-window candidates"
        f"{' (restricted to priced)' if priced else ''}, budget {a.budget} -> {len(planned)} planned, {len(dropped)} dropped;"
        f" ladders whole {whole}/{len(ladders)} (partial {partial})")
    est_s = len(planned) / max(a.rps, 0.1)
    log(f"estimated fetch time {est_s / 60:.1f} min at {a.rps} req/s")
    day = os.path.join(a.out, "depth", run_ts.strftime("%Y-%m-%d"))
    os.makedirs(day, exist_ok=True)
    manifest = {"depth_capture_version": DEPTH_CAPTURE_VERSION, "run_id": run_id, "snapshot_id": run_ts.strftime("%Y%m%dT%H%M%SZ"),
                "horizon_label": a.horizon_label, "started_at": now_utc().isoformat(), "budget": a.budget,
                "window_hours": a.window_hours, "candidates": len(keep), "planned": len(planned), "dropped": len(dropped),
                "priority_rule": "kickoff proximity, then ladder, then traded, then ticker -- never the model's own disagreement",
                "ladders_total": len(ladders), "ladders_whole": whole, "ladders_partial": partial, "dry_run": bool(a.dry_run),
                "estimated_seconds": round(est_s, 1), "priced_restricted": bool(priced)}
    if a.dry_run:
        manifest.update(captured=0, failed=0, finished_at=now_utc().isoformat(), seconds=round(time.time() - t0, 1),
                        skipped_by_reason=_counts(skip))
        p = os.path.join(day, f"{run_id}.depth_manifest.json")
        json.dump(manifest, open(p, "w"), separators=(",", ":"))
        log(f"DRY RUN -> {p}")
        print(json.dumps({k: v for k, v in manifest.items() if k != "series"}, default=str))
        return 0
    c = KalshiClient(rps=a.rps)
    captured = failed = crossed = 0
    out_p = os.path.join(day, f"{run_id}.depth.jsonl.gz")
    # LADDER-LEVEL KICKOFF SAFETY. A ladder is entered only if, at this moment and this rate, the WHOLE ladder
    # can finish before its game starts. A ladder that cannot is skipped entirely with a reason rather than
    # half-fetched across kickoff, because a distribution with a post-kickoff hole in it is worse than none.
    by_ladder = {}
    for r in planned:
        by_ladder.setdefault(ladder_key(r), []).append(r)
    with gzip.open(out_p, "wt") as fh:
        for k, rows_in in by_ladder.items():
            ko = pit.as_utc(rows_in[0].get("kickoff_utc"))
            need_s = len(rows_in) / max(a.rps, 0.1)
            if ko is not None and (now_utc() + timedelta(seconds=need_s + KICKOFF_SAFETY_S)) >= ko:
                for r in rows_in:
                    skip.append({**r, "reason": SKIP_NO_TIME,
                                 "detail": f"{len(rows_in)} contracts need ~{need_s:.0f}s and kickoff is "
                                           f"{(ko - now_utc()).total_seconds():.0f}s away"})
                continue
            for r in rows_in:
                obs = now_utc()
                # per-request guard: never send a request that could return after kickoff
                if ko is not None and obs >= ko - timedelta(seconds=KICKOFF_SAFETY_S):
                    skip.append({**r, "reason": SKIP_NO_TIME, "detail": "kickoff reached mid-ladder"})
                    continue
                body, err = c.try_get(f"markets/{r['ticker']}/orderbook", {"depth": BOOK_DEPTH})
                got = now_utc()
                if err or body is None:
                    failed += 1
                    skip.append({**r, "reason": SKIP_FAILED, "error": str(err)[:120]})
                    continue
                # THE RESPONSE IS DATED WHEN IT ARRIVED, and a response that arrived at or after kickoff is not
                # pregame evidence whatever the job was aiming at. It is recorded as post-kickoff and excluded.
                if ko is not None and got >= ko:
                    crossed += 1
                    skip.append({**r, "reason": SKIP_POST_KICKOFF,
                                 "detail": f"response observed {(got - ko).total_seconds():.0f}s after kickoff"})
                    continue
                mtk = ((ko - got).total_seconds() / 60.0) if ko is not None else None
                target = HORIZON_TARGET_MIN.get(a.horizon_label)
                fh.write(json.dumps({
                    "depth_capture_version": DEPTH_CAPTURE_VERSION, "run_id": run_id,
                    "observed_at": got.isoformat(), "ticker": r["ticker"],
                    "series_ticker": r.get("series_ticker"), "event_ticker": r.get("event_ticker"),
                    "game_id": r.get("game_id"), "kickoff_utc": (ko.isoformat() if ko else None),
                    # recomputed from THIS observation, never inherited from the quote snapshot
                    "minutes_to_kickoff": (round(mtk, 3) if mtk is not None else None),
                    "target_horizon": a.horizon_label, "target_horizon_min": target,
                    "horizon_delta_min": (round(mtk - target, 3) if (mtk is not None and target is not None) else None),
                    "horizon_quality": horizon_quality_of(mtk, target),
                    "ladder_event_ticker": k[0], "ladder_series_ticker": k[1],
                    "ladder_size": len(rows_in), "ladder_complete": True,
                    "orderbook_fp": (body or {}).get("orderbook_fp"), "error": None},
                    separators=(",", ":")) + "\n")
                captured += 1
    manifest.update(captured=captured, failed=failed, post_kickoff_rejected=crossed, finished_at=now_utc().isoformat(),
                    seconds=round(time.time() - t0, 1), skipped_by_reason=_counts(skip),
                    client_stats=c.stats.to_dict(), depth_file=os.path.basename(out_p),
                    coverage_of_candidates=round(captured / max(len(keep), 1), 4))
    json.dump(manifest, open(os.path.join(day, f"{run_id}.depth_manifest.json"), "w"), separators=(",", ":"))
    # every skipped candidate keeps its reason: absent depth must never read as an absent market
    with gzip.open(os.path.join(day, f"{run_id}.depth_skipped.jsonl.gz"), "wt") as fh:
        for s in skip:
            fh.write(json.dumps(s, separators=(",", ":")) + "\n")
    log(f"captured {captured}, failed {failed}, skipped {len(skip)} -> {out_p}")
    print(json.dumps(manifest, default=str))
    return 0


def _counts(rows):
    out = {}
    for r in rows:
        out[r.get("reason")] = out.get(r.get("reason"), 0) + 1
    return out


if __name__ == "__main__":
    raise SystemExit(main())
