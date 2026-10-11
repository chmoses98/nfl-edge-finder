"""One capture run: decide what is due, forecast it with the frozen PURE arms, write every family write-once.

    due = (game, kind) pairs whose window contains now and that the store has not captured yet
    PURE projections   <- football inputs only (nflverse files with recorded provenance)
    market / incumbent <- read-only, AFTER the projections are built and validated, into separate files
"""
from __future__ import annotations

import json
import os
import sys
from datetime import datetime, timezone

import pandas as pd

from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, BASELINE_VERSION, MODEL_NAME, VERSION
from nfl_edge.engines.player.pure_v1 import data as D
from nfl_edge.shadow_pure import (ADHOC, CAPTURE_WINDOWS, COLLECTOR_VERSION, DATA_FIRST_SEASON, PURE_V1_FROZEN_GIT, SPORT,
                                  frozen, inputs, prospective, records, store)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GATE_DIR = os.path.join(ROOT, "tools", "pure_gate")


def gate():
    sys.path.insert(0, GATE_DIR)
    import pure_gate  # noqa: E402  (vendored, stdlib only)
    return pure_gate


def captured_pairs(store_root: str) -> set[tuple[str, str]]:
    """(game_id, kind) pairs already captured, from the sealed manifests of the store."""
    out = set()
    d = os.path.join(store_root, store.MANIFEST_DIR)
    if not os.path.isdir(d):
        return out
    for f in os.listdir(d):
        if f.endswith(store.MANIFEST_SUFFIX):
            m = json.load(open(os.path.join(d, f)))
            if m.get("mode") == "capture":
                for g in m.get("captured", []):
                    out.add((g["game_id"], g["kind"]))
    return out


def due_captures(games: pd.DataFrame, now: datetime, done: set) -> list[tuple[str, str]]:
    due = []
    for g in games.itertuples(index=False):
        mins = (pd.Timestamp(g.kickoff) - pd.Timestamp(now)).total_seconds() / 60.0
        for kind, early, late in CAPTURE_WINDOWS:
            if late <= mins <= early and (g.game_id, kind) not in done:
                due.append((g.game_id, kind))
    return due


def windows_open(root: str, now: datetime | None = None) -> list[tuple[str, str]]:
    """Cheap pre-check from the schedule alone: (game, kind) windows containing now, ignoring what is captured."""
    now = now or datetime.now(timezone.utc)
    sched = D.sports_schedule(D.read_schedule(root))
    return due_captures(prospective.upcoming_games(sched, now), now, set())


def run_capture(root: str, store_root: str, *, now: datetime | None = None, md_root: str | None = None,
                map_path: str | None = None, adhoc_games=None, dry_run: bool = False, log=print) -> dict:
    """Returns a summary. adhoc_games: capture these upcoming games now as ADHOC regardless of the windows."""
    now = now or datetime.now(timezone.utc)
    frozen_hash = frozen.assert_frozen()
    if os.path.exists(os.path.join(root, "data", "silver", "player_crosswalk.parquet")):
        raise inputs.ProvenanceError("data/silver/player_crosswalk.parquet would be read but has no recorded provenance; "
                                     "the collector reads the nflverse players table only")
    sched = D.sports_schedule(D.read_schedule(root))
    season = int(sched.loc[sched["kickoff"] > pd.Timestamp(now), "season"].min()) if (sched["kickoff"] > pd.Timestamp(now)).any() else None
    if season is None:
        return {"state": "NO_UPCOMING_GAMES"}
    upcoming = prospective.upcoming_games(sched, now)
    done = captured_pairs(store_root)
    if adhoc_games is not None:
        ids = list(upcoming["game_id"]) if adhoc_games == "ALL" else list(adhoc_games)
        due = [(g, ADHOC) for g in ids if g in set(upcoming["game_id"])]
    else:
        due = due_captures(upcoming, now, done)
    if not due:
        return {"state": "NOTHING_DUE", "now": now.isoformat(), "upcoming": len(upcoming)}
    as_of = datetime.now(timezone.utc) if now is None else now
    seasons = list(range(DATA_FIRST_SEASON, season + 1))
    prov = inputs.input_provenance(root, seasons, as_of=as_of)
    srcs = inputs.sources_block(prov)
    sched_fetched = srcs["nflverse_schedule_nonmarket_columns"]["max_observed_at"]
    games = upcoming[upcoming["game_id"].isin({g for g, _ in due})]
    log(f"capturing {len(due)} (game, kind) pairs over {len(games)} games, as_of {as_of.isoformat()}")

    pg = D.load_player_games(root, seasons)
    syn = prospective.candidates(pg, games, as_of)
    starter_src = {(r.game_id, r.player_id): r.starter_basis for r in syn.itertuples() if isinstance(r.starter_basis, str)}
    rows, t = prospective.build(pg, syn, as_of)
    model, base = prospective.fit(rows, t, season)
    fc = prospective.forecast(rows, t, model, base, as_of)
    kind_of = {g: k for g, k in due}
    run_id = as_of.strftime("%Y%m%dT%H%M%SZ")
    day = as_of.strftime("%Y-%m-%d")
    pg_mod = gate()
    arms = {MODEL_NAME: VERSION, BASELINE_NAME: BASELINE_VERSION}
    out_rows = {}
    for arm, ver in arms.items():
        long = fc["arms"][arm]
        rows_v1 = []
        for kind in sorted(set(kind_of.values())):
            sub = long[long["game_id"].map(kind_of) == kind]
            rows_v1 += records.build_rows(sub, fc["intermediates"], fc["team"], fc["script"], t, model_version=ver,
                                          frozen_hash=frozen_hash, as_of=as_of, sources=srcs, schedule_fetched_at=sched_fetched,
                                          capture_kind=kind, run_id=run_id, starter_source=starter_src)
        summ = pg_mod.validate_file_summary(rows_v1, require_v1=True)        # raises GateError on any violation
        out_rows[arm] = (rows_v1, summ)
    # separate families, read-only sources, built only after the PURE rows exist
    from nfl_edge.shadow_pure import market as MK
    mk = MK.market_rows(md_root, games, as_of, map_path)
    inc = MK.incumbent_rows(md_root, games, as_of)

    w = store.RunWriter(store_root, run_id, meta={"mode": "capture", "collector_version": COLLECTOR_VERSION,
                                                   "dry_run": dry_run, "as_of": as_of.isoformat(),
                                                   "captured": [{"game_id": g, "kind": k} for g, k in due]})
    for arm, (rows_v1, summ) in out_rows.items():
        w.write_jsonl_gz(f"projections/{day}/{run_id}.{arm}.pure_forecast_v1.jsonl.gz", rows_v1)
    w.write_json(f"inputs/{day}/{run_id}.inputs.json", {"as_of": as_of.isoformat(), "files": prov,
                                                        "sources": {k: {**v, "max_observed_at": v["max_observed_at"].isoformat()} for k, v in srcs.items()}})
    w.write_jsonl_gz(f"market/{day}/{run_id}.kalshi_listings.jsonl.gz", mk["contracts"])
    w.write_jsonl_gz(f"market/{day}/{run_id}.listed_cohort.jsonl.gz", mk["cohort"])
    w.write_jsonl_gz(f"incumbent_diagnostic/{day}/{run_id}.v4_v5_market_informed.jsonl.gz", inc["rows"])
    pop = syn.groupby("game_id").size().to_dict()
    summary = {"run_id": run_id, "as_of": as_of.isoformat(), "collector_version": COLLECTOR_VERSION, "dry_run": dry_run,
               "model_frozen_hash": frozen_hash, "frozen_git": PURE_V1_FROZEN_GIT, "sport": SPORT, "season": season,
               "captured": [{"game_id": g, "kind": k, "kickoff": records.iso(games.set_index("game_id").loc[g, "kickoff"]),
                             "candidate_players": int(pop.get(g, 0))} for g, k in due],
               "rows": {arm: {"n": len(r), "validate": s} for arm, (r, s) in out_rows.items()},
               "by_statistic": {arm: fc["arms"][arm]["statistic"].value_counts().to_dict() for arm in out_rows},
               "model_info": model.info, "market_status": mk["status"], "incumbent_status": inc["status"],
               "inputs_fetched_at_max": max(v["max_observed_at"] for v in srcs.values()).isoformat()}
    w.write_json(f"runs/{day}/{run_id}.summary.json", summary)
    man = w.seal()
    summary["manifest_files"] = len(man["files"])
    return summary
