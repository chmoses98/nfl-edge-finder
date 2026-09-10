"""The incumbent's game centre, re-derived from a capture snapshot with the incumbent's own estimator.

The 2-hourly shadow cycle writes a `game_env` sidecar with the EXACT centre every game was priced from, and the
three-arm snapshot reads it. The decision-horizon conductor runs between those cycles, with no ledger snapshot
of its own (the RUN NFL report path never publishes to market-data, by design and by test). At a horizon the
CURRENT centre is therefore re-derived here, step for step as `scripts/shadow/price_slate.py` derives it:

    liquid full-game winner / spread / total quotes  ->  `implied_game_lines` grid search (same grids, 12,000
    sims, width <= 0.06, >= 6 liquid rungs)  ->  else the nflverse consensus line  ->  else no environment

on the same residual bank. It is the incumbent's estimator on the incumbent's inputs; what differs is the
random stream of the grid search, so an implied line can differ from the cycle's by one half-point grid step
in a close call. Every record says which of the two provenances it carries, and the reproduction check is
recorded as unavailable rather than faked.

The SUPPORT gating is mirrored too, so the contract universe is the one the incumbent would have priced:
settlement semantics established, quote pregame, series confirmed complete in the capture, a game environment,
and a full-game family the joint simulation prices.
"""
from __future__ import annotations

import glob
import json
import os
from datetime import datetime

import numpy as np
import pandas as pd

from nfl_edge.arms import registry as R
from nfl_edge.data.nfl_calendar import kickoff_utc
from nfl_edge.pricing.game_env import simulate_game
from nfl_edge.pricing.market_implied import implied_game_lines
from nfl_edge.settlement import semantics as sem_mod

SPREAD_GRID = np.arange(-17, 17.5, 0.5)
TOTAL_GRID = np.arange(34, 62.5, 0.5)
IMPLIED_NSIMS = 12000


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def load_capture_snapshot(capture_root: str) -> dict:
    """Latest quote per ticker plus the manifest of the latest run -- as price_slate.load_latest_quotes does."""
    files = sorted(glob.glob(os.path.join(capture_root, "*", "*.quotes.jsonl")))
    mans = sorted(glob.glob(os.path.join(capture_root, "*", "*.manifest.json")))
    if not files or not mans:
        raise FileNotFoundError(f"no capture quotes/manifests under {capture_root}")
    man = json.load(open(mans[-1]))
    run_ts = datetime.fromisoformat(man["finished_at"])
    confirmed = {s for s, v in (man.get("series") or {}).items() if v.get("complete")}
    quotes = {}
    for f in reversed(files):
        for line in open(f):
            r = json.loads(line)
            if r["ticker"] not in quotes:
                quotes[r["ticker"]] = r
    return {"quotes": quotes, "run_ts": run_ts, "run_id": run_ts.strftime("%Y%m%dT%H%M%SZ"),
            "confirmed_series": confirmed, "manifest_path": mans[-1]}


def game_environment(quotes: dict, games, target_season: int, bank) -> dict:
    """price_slate's game-environment block, producing the same sidecar shape (centres only, no simulation)."""
    sched = games.filter(games["season"] == target_season) if hasattr(games, "filter") else games
    gidx = sched.to_pandas().set_index("game_id") if hasattr(sched, "to_pandas") else sched.set_index("game_id")
    by_game = {}
    for t, q in quotes.items():
        if q.get("game_id"):
            by_game.setdefault(q["game_id"], []).append(q)
    env = {"games": {}, "games_without_environment": {}, "target_season": target_season, "n_sims": R.N_SIMS,
           "game_env_version": "game_env-0.2.0", "center_provenance": "incumbent_estimator_rerun",
           "implied_line_search": {"spread_grid": [-17.0, 17.0, 0.5], "total_grid": [34.0, 62.0, 0.5],
                                   "nsims": IMPLIED_NSIMS, "max_width": 0.06, "min_rungs": 6}}
    for gid in sorted(by_game):
        if gid not in gidx.index:
            env["games_without_environment"][gid] = "market did not join a scheduled game"
            continue
        row = gidx.loc[gid]
        qs = [{"family": r.get("family"), "period": r.get("period"), "team": r.get("team"), "threshold": r.get("threshold"),
               "floor_strike": r.get("floor_strike"), "yes_bid": _f(r.get("yes_bid_dollars")), "yes_ask": _f(r.get("yes_ask_dollars")),
               "volume": _f(r.get("volume_fp"))} for r in by_game[gid]]
        s_imp, t_imp, diag = implied_game_lines(qs, bank, simulate_game, row["home_team"], row["away_team"],
                                                spread_grid=SPREAD_GRID, total_grid=TOTAL_GRID, nsims=IMPLIED_NSIMS)
        s_use = s_imp if s_imp is not None else (float(row["spread_line"]) if pd.notna(row["spread_line"]) else None)
        t_use = t_imp if t_imp is not None else (float(row["total_line"]) if pd.notna(row["total_line"]) else None)
        if s_use is None or t_use is None:
            env["games_without_environment"][gid] = "no Kalshi-implied line and no consensus line: " + str(diag.get("reason"))
            continue
        ko = kickoff_utc(str(row["gameday"]), str(row["gametime"]))
        env["games"][gid] = {
            "spread_home": float(s_use), "total": float(t_use), "source": "kalshi_implied" if s_imp is not None else "consensus_line",
            "kalshi_implied_spread": s_imp, "kalshi_implied_total": t_imp,
            "implied_diag": {k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in diag.items()},
            "fallback_reason": None if s_imp is not None else str(diag.get("reason") or "implied lines unavailable"),
            "consensus_spread_line": float(row["spread_line"]) if pd.notna(row["spread_line"]) else None,
            "consensus_total_line": float(row["total_line"]) if pd.notna(row["total_line"]) else None,
            "home": row["home_team"], "away": row["away_team"], "season": int(row["season"]), "week": int(row["week"]),
            "kickoff_utc": ko.isoformat() if ko else None, "n_sims": R.N_SIMS}
    return env


def observation_like_rows(quotes: dict, confirmed_series: set, env: dict, books: dict | None = None) -> list:
    """Capture rows in the ledger-observation shape the snapshot builder consumes, with the incumbent's support
    gating mirrored. No prices are modelled here: `model_contract_value` is None (nothing to reproduce against)."""
    books = books or {}
    out = []
    for t, q in quotes.items():
        fam, period = q.get("family"), q.get("period")
        if fam not in R.GAME_FAMILIES_PRICED:
            continue
        yb, ya, nb, na = _f(q.get("yes_bid_dollars")), _f(q.get("yes_ask_dollars")), _f(q.get("no_bid_dollars")), _f(q.get("no_ask_dollars"))
        gid = q.get("game_id")
        ok, reason = sem_mod.settlement_supported(fam)
        state, why = "SUPPORTED", None
        if not ok:
            state, why = "UNSUPPORTED_RULES", reason
        elif q.get("pregame") is False:
            state, why = "POST_KICKOFF_EXCLUDED", "quote observed after kickoff"
        elif q.get("series_ticker") not in confirmed_series:
            state, why = "STALE_DATA", "series not confirmed complete in the latest capture run"
        elif not gid or gid not in env.get("games", {}):
            state, why = "UNSUPPORTED_GAME", "no game environment for this game"
        elif fam in ("SPREAD", "TOTAL", "TEAM_TOTAL") and period != "FULL":
            state, why = "UNSUPPORTED_MODEL", f"family {fam} period {period} not priced"
        bk = books.get(t) or {}
        out.append({"prediction_id": None, "ticker": t, "event_ticker": q.get("event_ticker"), "series_ticker": q.get("series_ticker"),
                    "family": fam, "period": period, "stat": q.get("stat"), "threshold": q.get("threshold"),
                    "floor_strike": q.get("floor_strike"), "operator": q.get("operator"), "direction": "YES",
                    "game_id": gid, "team": q.get("team"), "kickoff_utc": q.get("kickoff_utc"),
                    "minutes_to_kickoff": q.get("minutes_to_kickoff"), "observed_at": q.get("observed_at"),
                    "model_event_probability": None, "model_contract_value": None,
                    "yes_bid": yb, "yes_ask": ya, "no_bid": nb, "no_ask": na,
                    "mid": (yb + ya) / 2.0 if yb is not None and ya is not None else None,
                    "quote_width": (ya - yb) if yb is not None and ya is not None else None,
                    "volume": _f(q.get("volume_fp")), "open_interest": _f(q.get("open_interest_fp")),
                    "liquidity": _f(q.get("liquidity_dollars")), "minutes_since_price_change": None,
                    "book_depth_yes": bk.get("book_depth_yes"), "book_depth_no": bk.get("book_depth_no"),
                    "support_state": state, "support_reason": why})
    return out
