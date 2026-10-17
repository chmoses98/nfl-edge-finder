"""The forward-projection state (the stage-1 frame of the validated walk-forward) for live operation.

The state is the SAME object the committed study builds (`nfl.run_walkforward.stage1`): team and player feature frames,
the A..F ladder predictions for every historical row and for the upcoming week's candidate rows. Nothing about the
models changes in live operation; what changes between pregame runs of one week is only availability (injury
designations, depth charts, inactives), which is applied afterwards (live.project) through the study's own
`diagnostics.corrections(S, inj)` and `gate_nfl`.

Cost: a cold build is ~45-60 minutes (rolling opponent ridge ratings + walk-forward LightGBM for every season, which the
frozen stack weights need). Two policies:
  fresh  rebuild everything from the freshly downloaded nflverse data (the heavy, once-per-morning run);
  reuse  load the state saved by the latest fresh run IF it is for the same upcoming block and the same state code
         (the cheap, minutes-long refresh runs near kickoff, which only need newer availability).
"""
from __future__ import annotations

import hashlib
import json
import os
import pickle
import sys
import time

import numpy as np
import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
PF_ROOT = os.path.dirname(os.path.dirname(HERE))
if PF_ROOT not in sys.path:
    sys.path.insert(0, PF_ROOT)

from nfl import data as D  # noqa: E402
from nfl import pipeline as P  # noqa: E402
from nfl import project as PR  # noqa: E402

STATE_FILE = os.path.join(D.CACHE, "live_state.pkl")
# files whose content defines the state: a change to any of them invalidates a saved state
STATE_CODE = ["nfl/data.py", "nfl/features.py", "nfl/ladder.py", "nfl/pipeline.py", "nfl/project.py", "nfl/qb_fix.py",
              "nfl/diagnostics.py", "nfl/run_walkforward.py", "pf_core/MANIFEST.json", "results/nfl_frozen_selection.json"]


def code_fingerprint() -> str:
    h = hashlib.sha256()
    for rel in STATE_CODE:
        with open(os.path.join(PF_ROOT, rel), "rb") as f:
            h.update(rel.encode() + b"\0" + f.read())
    return h.hexdigest()[:16]


def _hide(sched: pd.DataFrame, tg: pd.DataFrame, pg: pd.DataFrame, hide: set[str]):
    """Replay support: pretend the given (finished) games have not been played - blank their results everywhere."""
    sched = sched.copy()
    m = sched.game_id.isin(hide)
    sched.loc[m, ["home_score", "away_score"]] = np.nan
    tg = tg.copy()
    mt = tg.game_id.isin(hide)
    for c in [c for c in tg.columns if c.startswith("tm_")] + ["points", "opp_points"]:
        tg.loc[mt, c] = np.nan
    tg["played"] = tg.points.notna()
    pg = pg[~pg.game_id.isin(hide)].reset_index(drop=True)
    return sched, tg, pg


def build_state(rebuild: bool = True, hide_games=(), cache_tag: str = "", log=print) -> dict:
    """Same as run_walkforward.stage1, with optional replay of a finished game as 'upcoming' (hide_games)."""
    t0 = time.time()
    hide = set(hide_games)
    sched = D.load_schedule()
    tg = D.cached("team_games", lambda: D.team_games(sched), force=rebuild)
    pg = D.cached("player_games", lambda: D.player_games(sched), force=rebuild)
    if hide:
        sched, tg, pg = _hide(sched, tg, pg, hide)
    blk, mode = PR.upcoming_block(sched)
    up = PR.upcoming_rows(sched, pg, blk, mode) if mode == "upcoming_week" else None
    log(f"forward block {blk} ({mode}): {0 if up is None else len(up)} candidate player rows")
    tf, tpreds, tparams, pf = P.build_frames(up, blk if mode == "upcoming_week" else None, log=log, force=rebuild,
                                             tg=tg, pg=pg, cache_tag=cache_tag)
    if mode != "upcoming_week":
        pf.loc[pf.block == blk, "split"] = "forward"
        tf.loc[tf.block == blk, "split"] = "forward"
    preds, params, pops = P.player_ladder(pf, log=log)
    return {"forward_mode": mode, "forward_block": blk, "tf": tf, "tpreds": tpreds, "tparams": tparams, "pf": pf,
            "preds": preds, "params": params, "pops": pops, "seconds": time.time() - t0,
            "built_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()), "code_fp": code_fingerprint(),
            "data_asof_utc": PR._asof(),
            "hidden_games": sorted(hide)}


def save_state(S: dict, path: str = STATE_FILE) -> str:
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".part"
    with open(tmp, "wb") as f:
        pickle.dump(S, f, protocol=4)
    os.replace(tmp, path)
    return path


def load_state(path: str = STATE_FILE) -> dict | None:
    if not os.path.exists(path):
        return None
    try:
        with open(path, "rb") as f:
            return pickle.load(f)
    except Exception:  # noqa: BLE001 - a corrupt cache is a miss, never a crash
        return None


def valid_for(S: dict | None, sched: pd.DataFrame) -> tuple[bool, str]:
    if S is None:
        return False, "no saved state"
    if S.get("code_fp") != code_fingerprint():
        return False, "state code changed since the saved state was built"
    blk, mode = PR.upcoming_block(sched)
    if S.get("forward_block") != blk or S.get("forward_mode") != mode:
        return False, f"saved state is for block {S.get('forward_block')}, schedule's upcoming block is {blk}"
    return True, "ok"


def get_state(policy: str = "reuse", path: str = STATE_FILE, log=print, allow_fresh: bool = True) -> tuple[dict, dict]:
    """policy 'reuse' (fall back to a fresh build when the saved state is missing/stale, unless allow_fresh is False: a
    near-kickoff refresh run must fail loudly rather than spend an hour rebuilding) or 'fresh'."""
    sched = D.load_schedule()
    info = {"policy": policy}
    if policy == "reuse":
        S = load_state(path)
        ok, why = valid_for(S, sched)
        info["reuse_check"] = why
        if ok:
            info.update(source="saved_state", built_utc=S.get("built_utc"))
            return S, info
        if not allow_fresh:
            raise RuntimeError(f"no usable saved state for a refresh run ({why}); the morning fresh run has to produce it")
        log(f"state: cannot reuse ({why}); building fresh")
    S = build_state(rebuild=True, log=log)
    save_state(S, path)
    info.update(source="fresh_build", built_utc=S["built_utc"], build_seconds=round(S["seconds"]))
    return S, info
