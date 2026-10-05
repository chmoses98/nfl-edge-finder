"""Five-season walk-forward (2021-2025) of the FROZEN incumbent simulation, with GAME SCRIPT V2 collected from the
very rows that were scored. RESEARCH_ONLY. Preregistered: research/game_script_v2/PREREGISTRATION.md.

``run_season`` is ``scripts/sim/walkforward.py`` for one season -- the same ``fit_priors_for`` -> ``assemble`` ->
``backtest.run_season`` -> ``backtest.evaluate`` calls -- plus a read-only hook that stores, per game:

  * the nine-cell script counts and the marginal-event probabilities (script_v2), the centre and orientation;
  * the (margin, total) of every row and the per-row team volume needed by the script / score-path studies
    (int16, local cache only -- never committed);

and an eligibility / missing-data audit of the evaluation season. Nothing in the hook draws a random number,
so the scored distributions are bit-identical to a run without it (tests/test_five_year.py).
"""
from __future__ import annotations

import json
import os
import time

import numpy as np
import pandas as pd

from . import backtest as B
from . import data as D
from . import script_v2 as V
from . import training as T

EVIDENCE_CLASS = {2021: "RETROSPECTIVE_CHALLENGE", 2022: "RETROSPECTIVE_CHALLENGE", 2023: "RETROSPECTIVE_DEVELOPMENT",
                  2024: "RETROSPECTIVE_DEVELOPMENT", 2025: "RETROSPECTIVE_DEVELOPMENT"}
DEFAULT_OUT = os.path.join(D.ROOT, "data", "cache", "game_script_v2", "baseline")
ROW_KEYS = ("plays", "pass_att", "designed_rush")


class ScriptCollector:
    """The read-only on_game hook: summarises each scored game's rows; never touches a generator."""

    def __init__(self):
        self.games, self.rows = [], {}

    def __call__(self, res, gi):
        cells = V.cell_index(res.margin, res.total, gi.spread_home, gi.total_line)
        ev = V.sim_events(res, gi)
        H, A = res.team[gi.home.team], res.team[gi.away.team]
        rec = {"game_id": gi.game_id, "season": gi.season, "week": gi.week, "home": gi.home.team, "away": gi.away.team,
               "spread_home": float(gi.spread_home), "total_line": float(gi.total_line), "n_rows": int(res.n),
               "cell_counts": np.bincount(cells.astype(np.int64), minlength=V.N_CELLS).tolist(),
               "events": {k: (None if v is None else float(np.mean(v))) for k, v in ev.items()},
               "qb1": {gi.home.team: gi.home.qb1, gi.away.team: gi.away.qb1},
               "team_means": {t: {k: float(np.mean(X[k])) for k in ("plays", "pass_att", "designed_rush", "dropbacks", "targets", "points")}
                              for t, X in ((gi.home.team, H), (gi.away.team, A))}}
        # per-cell team volume means: the script-conditional volume the matrix study reads
        rec["cell_volume"] = {t: {k: np.round(np.bincount(cells.astype(np.int64), weights=np.asarray(X[k], float), minlength=V.N_CELLS)
                                              / np.maximum(rec["cell_counts"], 1), 3).tolist() for k in ROW_KEYS}
                              for t, X in ((gi.home.team, H), (gi.away.team, A))}
        self.games.append(rec)
        self.rows[gi.game_id] = np.stack([np.asarray(res.margin), np.asarray(res.total)]
                                         + [np.asarray(X[k]) for X in (H, A) for k in ROW_KEYS]).astype(np.int16)


def eligibility_audit(frames: dict, season: int) -> dict:
    """Who the simulator could allocate opportunity to, and how much of the realised volume that set covers."""
    e = frames["eligible"]; e = e[e["season"] == season]
    pg = D.load("player_games", [season]).to_pandas(); tg = D.load("team_games", [season]).to_pandas()
    elig = set(zip(e["game_id"], e["player_id"]))
    pg["in_elig"] = [(g, p) in elig for g, p in zip(pg["game_id"], pg["player_id"])]
    vol = pg.groupby("in_elig")[["designed_carries", "targets", "attempts"]].sum()
    def share(col):
        tot = float(vol[col].sum())
        return float(vol.loc[True, col] / tot) if tot and True in vol.index else None
    team_games = e.groupby(["game_id", "team"]).size()
    out = {"eligible_rows": int(len(e)), "team_games_with_eligible_set": int(len(team_games)),
           "team_games_in_season": int(len(tg)),
           "avail_state_counts": {k: int(v) for k, v in e["avail_state"].value_counts().items()},
           "eligible_with_no_prior_history": int((e["n_prior"].fillna(0) == 0).sum()),
           "eligible_without_depth_chart_rank": int(e["dc_rank"].isna().sum()),
           "realized_volume_covered_by_eligible_set": {"designed_carries": share("designed_carries"), "targets": share("targets"),
                                                       "pass_attempts": share("attempts")},
           "players_with_touches_not_in_eligible_set": int(((~pg["in_elig"]) & ((pg["designed_carries"] + pg["targets"] + pg["attempts"]) > 0)).sum())}
    # quarterback starter identification: the simulator's QB1 vs the passer with the most attempts
    return out


def qb_identification(games: list, season: int) -> dict:
    pg = D.load("player_games", [season]).to_pandas()
    top = pg[pg["attempts"] > 0].sort_values("attempts", ascending=False).drop_duplicates(["game_id", "team"])
    top = dict(zip(zip(top["game_id"], top["team"]), top["player_id"]))
    hit = tot = 0
    misses = []
    for g in games:
        for team, q in g["qb1"].items():
            act = top.get((g["game_id"], team))
            if act is None:
                continue
            tot += 1
            if q == act:
                hit += 1
            else:
                misses.append({"game_id": g["game_id"], "team": team, "sim_qb1": q, "actual": act})
    return {"team_games": tot, "sim_qb1_is_actual_starter": hit, "rate": hit / tot if tot else None, "misses": misses}


def run_season(season: int, *, n_sims: int = 10000, out_dir: str = DEFAULT_OUT, history_start: int = 2016,
               limit: int | None = None, verbose=print, arm: dict | None = None, frames_hook=None) -> dict:
    """One evaluation season, strictly walk-forward. Returns the walkforward.json-style record plus audits."""
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    priors = T.fit_priors_for(season, history_start)
    if max(priors.fit_seasons) >= season:
        raise RuntimeError("priors reach the evaluation season")
    frames = T.assemble(range(history_start, season + 1), verbose=lambda *x: None, priors=priors)
    if frames_hook is not None:
        frames = frames_hook(frames, season)
    bundle = T.fit_bundle(season, frames, history_start=history_start, verbose=verbose, arm=arm)
    if max(bundle["train_seasons"]) >= season:
        raise RuntimeError("the bundle trained on the evaluation season")
    col = ScriptCollector()
    info = B.run_season(season, frames, n_sims=n_sims, limit=limit, verbose=verbose, bundle=bundle, out_dir=out_dir, on_game=col)
    ev = B.evaluate(season, frames, out_dir=out_dir)
    rec = {"run": info, "evaluation": ev, "evidence_class": EVIDENCE_CLASS.get(season, "UNCLASSIFIED"),
           "priors_fit_seasons": list(priors.fit_seasons), "train_seasons": bundle["train_seasons"],
           "eligibility": eligibility_audit(frames, season), "qb_identification": qb_identification(col.games, season),
           "seconds_total": time.time() - t0}
    with open(os.path.join(out_dir, f"scripts_{season}.json"), "w") as f:
        json.dump(col.games, f)
    np.savez_compressed(os.path.join(out_dir, f"rows_{season}.npz"), **col.rows)
    e = frames["eligible"]; e = e[e["season"] == season]
    e[["game_id", "team", "player_id", "position", "dc_rank", "avail_state", "n_prior"]].to_parquet(os.path.join(out_dir, f"eligible_{season}.parquet"))
    with open(os.path.join(out_dir, f"wf_{season}.json"), "w") as f:
        json.dump(rec, f, indent=1, default=float)
    return rec
