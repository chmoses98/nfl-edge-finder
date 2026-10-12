"""Outcomes, reconciliation and scoring of matured shadow rows (append-only outputs).

outcomes        one row per forecast (game, player, statistic) whose game has a published box score, from nflverse
                stats_player_week + snap_counts (source + fetched_at on every row). `played` follows the forecast's
                condition: own participation (>= 1 offensive snap or a box-score line) and, for QB passing
                statistics, having started (schedule starter, else the QB with the most attempts -- the frozen
                package's own rule). A snap-share outcome is written only when the game's snap counts exist.
reconciliation  projection <-> outcome per capture row, the pregame listed-cohort flag, and market-settlement vs
                sports-outcome mismatch flags where a captured Kalshi result exists.
evaluation      pure_gate compare (PURE_EWM_BASELINE champion, PURE_PLAYER_V1 challenger) per capture kind on
                (a) the entire eligible population and (b) the pregame market-listed cohort, game-clustered.
"""
from __future__ import annotations

import glob
import json
import os
from collections import defaultdict
from datetime import datetime, timezone

import numpy as np
import pandas as pd

from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, MODEL_NAME
from nfl_edge.engines.player.pure_v1 import data as D
from nfl_edge.engines.player.pure_v1 import features as F
from nfl_edge.engines.player.pure_v1 import model as M
from nfl_edge.shadow_pure import SPORT, inputs, store

QB_PASS = ("passing_attempts", "completions", "passing_yards")


def load_projections(store_root: str) -> dict:
    """{arm: [rows]} over every projection file in the store."""
    out = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(store_root, "projections", "*", "*.pure_forecast_v1.jsonl.gz"))):
        arm = os.path.basename(f).split(".")[1]
        out[arm] += store.read_jsonl(f)
    return out


def load_outcomes(store_root: str) -> dict:
    """Latest outcome per (game, player, statistic) across outcome files (stat corrections supersede)."""
    best = {}
    for f in sorted(glob.glob(os.path.join(store_root, "outcomes", "*", "*.outcomes.jsonl.gz"))):
        for r in store.read_jsonl(f):
            best[(r["game_id"], r["player_id"], r["statistic"])] = r
    return best


def build_outcomes(root: str, keys: set, seasons, *, fetched: dict) -> list[dict]:
    """Sports outcomes for forecast keys whose game has a box score. `fetched` = {source_id: fetched_at iso}."""
    if not keys:
        return []
    games = {k[0] for k in keys}
    pg = D.load_player_games(root, seasons)
    pg = pg[pg["game_id"].isin(games)]
    if not len(pg):
        return []
    t = F.team_games(pg)
    pg = pg.merge(t[["team", "game_id", "team_snaps"]], on=["team", "game_id"], how="left")
    pg["snap_share"] = pg["offense_snaps"] / pg["team_snaps"].where(pg["team_snaps"] > 0)
    have_box = set(pg["game_id"])
    have_snaps = set(pg.loc[pg["offense_snaps"].notna(), "game_id"])
    idx = pg.set_index(["game_id", "player_id"])
    idx = idx[~idx.index.duplicated()]
    out = []
    for g, p, stat in sorted(keys):
        if g not in have_box or (stat == "snap_share" and g not in have_snaps):
            continue
        src = "nflverse_snap_counts" if stat == "snap_share" else "nflverse_stats_player_week"
        if (g, p) in idx.index:
            r = idx.loc[(g, p)]
            played = bool(r["played"]) and (bool(r["qb_starter"]) if stat in QB_PASS else True)
            val = float(r[M.OUTCOME[stat]]) if pd.notna(r[M.OUTCOME[stat]]) else (0.0 if stat != "snap_share" else np.nan)
            if not np.isfinite(val):
                continue
        else:
            played, val = False, 0.0
        out.append({"sport": SPORT, "game_id": g, "player_id": p, "statistic": stat, "actual": round(val, 6), "played": played,
                    "source": src, "observed_at": fetched[src]})
    return out


def reconcile(proj: dict, outcomes: dict, cohort: set, settlements: dict | None = None) -> list[dict]:
    rows = []
    a = {(r["game_id"], r["player_id"], r["statistic"], r["as_of"]): r for r in proj.get(MODEL_NAME, [])}
    b = {(r["game_id"], r["player_id"], r["statistic"], r["as_of"]): r for r in proj.get(BASELINE_NAME, [])}
    for k in sorted(set(a) | set(b)):
        o = outcomes.get(k[:3])
        ra, rb = a.get(k), b.get(k)
        r0 = ra or rb
        row = {"game_id": k[0], "player_id": k[1], "statistic": k[2], "as_of": k[3], "kickoff": r0["kickoff"],
               "capture_kind": r0.get("x_capture", {}).get("capture_kind"),
               "mean_pure_v1": ra and ra["projection"]["mean"], "mean_baseline": rb and rb["projection"]["mean"],
               "matured": o is not None, "actual": o and o["actual"], "played_condition_met": o and o["played"],
               "listed_pregame": (k[0], k[1], k[2], k[3]) in cohort}
        if settlements:
            mism = []
            for s in settlements.get(k[:3], []):
                if o is None or s.get("threshold") is None or s.get("result") not in ("yes", "no"):
                    continue
                sports_yes = float(o["actual"]) >= float(s["threshold"])
                if sports_yes != (s["result"] == "yes"):
                    mism.append(s["ticker"])
            row["market_vs_sports_mismatch_tickers"] = mism
        rows.append(row)
    return rows


def cohort_keys(store_root: str) -> set:
    """(game, player, statistic, as_of) of the pregame market-listed cohort, per capture run."""
    out = set()
    for f in sorted(glob.glob(os.path.join(store_root, "market", "*", "*.listed_cohort.jsonl.gz"))):
        run = os.path.basename(f).split(".")[0]
        as_of = datetime.strptime(run, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
        for r in store.read_jsonl(f):
            if r.get("listed_pregame"):
                out.add((r["game_id"], r["player_id"], r["statistic"], as_of))
    return out


def score(gate, proj: dict, outcomes: dict, cohort: set, *, bootstrap: int = 1000, seed: int = 20261010) -> dict:
    """pure_gate compare per capture kind, full eligible population and pregame listed cohort."""
    res = {}
    kinds = sorted({r.get("x_capture", {}).get("capture_kind") for r in proj.get(MODEL_NAME, [])} - {None})
    for kind in kinds:
        for label in ("full_eligible_population", "pregame_market_listed_cohort"):
            def sel(rows):
                keep = [r for r in rows if r.get("x_capture", {}).get("capture_kind") == kind
                        and (r["game_id"], r["player_id"], r["statistic"]) in outcomes]
                if label == "pregame_market_listed_cohort":
                    keep = [r for r in keep if (r["game_id"], r["player_id"], r["statistic"], r["as_of"]) in cohort]
                # one row per player-game-statistic per kind: the earliest capture of that kind
                first = {}
                for r in sorted(keep, key=lambda r: r["as_of"]):
                    first.setdefault((r["game_id"], r["player_id"], r["statistic"]), r)
                return list(first.values())
            champ, chal = sel(proj.get(BASELINE_NAME, [])), sel(proj.get(MODEL_NAME, []))
            keys = {(r["game_id"], r["player_id"], r["statistic"]) for r in champ} | {(r["game_id"], r["player_id"], r["statistic"]) for r in chal}
            outs = [outcomes[k] for k in sorted(keys)]
            if not champ or not chal:
                res[f"{kind}/{label}"] = {"state": "NO_MATURED_ROWS", "n_champion": len(champ), "n_challenger": len(chal)}
                continue
            sc = gate.compare(champ, chal, outs, bootstrap=bootstrap, seed=seed)
            sc["n_games"] = len({r["game_id"] for r in chal})
            res[f"{kind}/{label}"] = sc
    return res


def fetched_map(root: str, seasons, as_of) -> dict:
    prov = inputs.input_provenance(root, seasons, as_of=as_of)
    out = {}
    for r in prov:
        if r.get("status") == "PRESENT":
            out[r["source_id"]] = max(out.get(r["source_id"], r["fetched_at"]), r["fetched_at"])
    return out


def discovery_settlements(md_root: str | None, map_path: str | None, keys: set) -> dict:
    """(game, player, statistic) -> [{ticker, threshold, result}] from the newest discovery's settled markets."""
    if not md_root:
        return {}
    from nfl_edge.kalshi.classifier import classify
    from nfl_edge.shadow_pure import market as MK
    disc = MK.latest_discovery(md_root, datetime.now(timezone.utc))
    if not disc:
        return {}
    pmap = MK.player_map(map_path)
    games = {k[0] for k in keys}
    out = defaultdict(list)
    for f in sorted(glob.glob(os.path.join(disc, "markets", "*.json"))):
        try:
            doc = json.load(open(f))
        except ValueError:
            continue
        for state in ("settled", "closed"):
            for m in (doc.get(state) or {}).get("markets", []):
                s = classify(m)
                if s.family != "PLAYER_STAT" or s.stat not in MK.STAT_MAP or not m.get("result"):
                    continue
                gsis = pmap.get(s.player_kalshi_id)
                for g in games:
                    if g.endswith(f"_{s.away_team}_{s.home_team}") and gsis:
                        out[(g, gsis, MK.STAT_MAP[s.stat])].append({"ticker": m.get("ticker"), "threshold": s.threshold,
                                                                     "result": str(m.get("result")).lower()})
    return out


def settle_and_evaluate(root: str, store_root: str, gate, *, now=None, md_root=None, map_path=None,
                        bootstrap: int = 1000, force: bool = False) -> dict:
    now = now or datetime.now(timezone.utc)
    proj = load_projections(store_root)
    allrows = proj.get(MODEL_NAME, []) + proj.get(BASELINE_NAME, [])
    matured = {(r["game_id"], r["player_id"], r["statistic"]) for r in allrows
               if pd.Timestamp(r["kickoff"]) + pd.Timedelta(hours=D.GAME_DURATION_HOURS) < pd.Timestamp(now)}
    if not matured:
        return {"state": "NO_MATURED_ROWS", "projection_rows": len(allrows)}
    seasons = sorted({int(k[0][:4]) for k in matured})
    fetched = fetched_map(root, seasons, now)
    prior = load_outcomes(store_root)
    fresh = build_outcomes(root, matured, seasons, fetched=fetched)
    new = [o for o in fresh if (k := (o["game_id"], o["player_id"], o["statistic"])) not in prior
           or (prior[k]["actual"], prior[k]["played"]) != (o["actual"], o["played"])]
    if not new and not force:
        return {"state": "NOTHING_NEW", "matured_keys": len(matured), "outcomes_known": len(prior)}
    run_id = now.strftime("%Y%m%dT%H%M%SZ"); day = now.strftime("%Y-%m-%d")
    outcomes = dict(prior)
    for o in new:
        outcomes[(o["game_id"], o["player_id"], o["statistic"])] = o
    cohort = cohort_keys(store_root)
    sett = discovery_settlements(md_root, map_path, matured)
    rec = reconcile(proj, outcomes, cohort, sett)
    ev = score(gate, proj, outcomes, cohort, bootstrap=bootstrap)
    w = store.RunWriter(store_root, run_id, meta={"mode": "settle", "as_of": now.isoformat()})
    if new:
        w.write_jsonl_gz(f"outcomes/{day}/{run_id}.outcomes.jsonl.gz", new)
    w.write_jsonl_gz(f"reconciliation/{day}/{run_id}.reconciliation.jsonl.gz", rec)
    summary = {"run_id": run_id, "evaluated_at": now.isoformat(), "new_outcomes": len(new), "outcomes_total": len(outcomes),
               "matured_keys": len(matured), "settlement_contracts_seen": sum(len(v) for v in sett.values()),
               "market_vs_sports_mismatches": sum(len(r.get("market_vs_sports_mismatch_tickers") or []) for r in rec),
               "policy": "DESCRIPTIVE ONLY. No promotion, no authority, no staking, no publication to production.",
               "scorecards": ev}
    w.write_json(f"evaluations/{day}/{run_id}.evaluation.json", summary)
    w.seal()
    return {k: v for k, v in summary.items() if k != "scorecards"} | {"scorecard_keys": sorted(ev)}
