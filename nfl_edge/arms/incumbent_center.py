"""The incumbent's game centre, obtained by REPLAYING the incumbent -- never by modifying it.

`scripts/shadow/price_slate.py` is frozen Week-1 evidence lineage and is not touched. It also records neither
the centre it priced each game from nor its source. This module reproduces that centre by executing the
frozen script's own functions in the frozen script's own order, on the same inputs:

    load_latest_quotes (imported from the frozen script)  ->  the same quotes dict, in the same order
    the same `by_game` grouping, in the same insertion order
    the same silver games table, the same residual-bank filter and construction, the SAME seed (11)
    for each game, in the same order:
        implied_game_lines(...)  with the same grids and 12,000 draws   (consumes the bank's generator)
        simulate_game(..., n=40000)                                     (consumes it again)

The bank's generator is one sequential stream shared by every grid search and every simulation, so the
centre of the ninth game depends on everything drawn for the first eight. Replaying the whole sequence is
therefore the ONLY way to reproduce a centre exactly, and it reproduces the incumbent's 40,000-row simulation
of every game as a by-product. When the incumbent's ledger snapshot for the same capture is on disk, the
replayed simulation's prices are compared with the ledger's prices ticker by ticker and the replay is marked
`exact_replay_verified`; without a ledger (the horizon conductor) it is `exact_replay_unverified` -- the same
algorithm, seed, inputs and order, with nothing on disk to check against. A replay whose prices do not match
the ledger is `replay_mismatch`, and the CURRENT arm built from it is DEGRADED. Nothing here pretends a
re-derived centre is the recorded production centre when it is not.

Cost: the incumbent's own game-environment cost (about 160 s for a 30-game capture), paid once per snapshot.
"""
from __future__ import annotations

import glob
import importlib.util
import json
import math
import os
import sys
from datetime import datetime

import numpy as np
import polars as pl

from nfl_edge.arms import registry as R
from nfl_edge.data.nfl_calendar import kickoff_utc
from nfl_edge.pricing.game_env import ResidualBank, simulate_game
from nfl_edge.pricing.market_implied import implied_game_lines
from nfl_edge.settlement import semantics as sem_mod

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
FROZEN_PRICER = os.path.join(ROOT, "scripts", "shadow", "price_slate.py")

# The incumbent's own constants, copied here so a drift in the frozen script is a visible test failure
# (tests/test_incumbent_unchanged.py pins the script's text) rather than a silent divergence.
IMPLIED_SPREAD_GRID = (-17, 17.5, 0.5)
IMPLIED_TOTAL_GRID = (34, 62.5, 0.5)
IMPLIED_NSIMS = 12000
BANK_SEASON_LO = 2016
BANK_HALFLIFE = 3.0
BANK_SEED = 11
MAX_QUOTE_AGE_MIN = 45.0

EXACT_VERIFIED = "exact_replay_verified"
EXACT_UNVERIFIED = "exact_replay_unverified"
MISMATCH = "replay_mismatch"


def frozen_pricer():
    """The frozen script as a module (its top level only defines functions and constants)."""
    spec = importlib.util.spec_from_file_location("_frozen_price_slate", FROZEN_PRICER)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


def _f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def _num(v):
    return None if v is None or (isinstance(v, float) and math.isnan(v)) else float(v)


def incumbent_bank(games: pl.DataFrame, target_season: int) -> tuple[ResidualBank, dict]:
    """price_slate's residual bank, from the same silver table with the same filter, order and seed."""
    g = games.filter((pl.col("game_type") == "REG") & pl.col("result").is_not_null()
                     & pl.col("spread_line").is_not_null() & (pl.col("season") >= BANK_SEASON_LO))
    result = g["result"].cast(pl.Float64).to_numpy()
    spread = g["spread_line"].cast(pl.Float64).to_numpy()
    total = g["total"].cast(pl.Float64).to_numpy()
    total_line = g["total_line"].cast(pl.Float64).to_numpy()
    overtime = g["overtime"].fill_null(0).cast(pl.Int64).to_numpy()
    bank = ResidualBank(result - spread, total - total_line, g["season"].cast(pl.Float64).to_numpy(),
                        ref_season=target_season, spread_lines=spread, total_lines=total_line, overtime=overtime,
                        results=result, halflife=BANK_HALFLIFE, rng=np.random.default_rng(BANK_SEED))
    meta = {"season_lo": int(g["season"].min()) if g.height else None, "season_hi": int(g["season"].max()) if g.height else None,
            "n_pairs": int(g.height), "halflife_seasons": BANK_HALFLIFE, "rng_seed": BANK_SEED,
            "population": "REG games with a result and a spread line, season >= 2016 (silver games.parquet), incumbent order"}
    return bank, meta


def replay_game_environment(market_data: str, root: str, target_season: int, *, limit_games: int = 0,
                            verbose=lambda *_: None) -> dict:
    """Execute the incumbent's game-environment block, call for call, and return everything it produced."""
    P = frozen_pricer()
    capture_root = os.path.join(market_data, "data", "kalshi", "capture")
    quotes, run_ts, ages, confirmed_series = P.load_latest_quotes(capture_root, MAX_QUOTE_AGE_MIN)
    if not quotes:
        raise FileNotFoundError(f"no capture quotes under {capture_root}")
    run_id = run_ts.strftime("%Y%m%dT%H%M%SZ")
    books = P.load_books(capture_root)
    games = pl.read_parquet(os.path.join(root, "data", "silver", "games.parquet"))
    sched = games.filter(pl.col("season") == target_season)
    gidx = {r["game_id"]: r for r in sched.to_dicts()}
    # price_slate builds `rows` from quotes in quote order and groups by game_id in insertion order
    by_game = {}
    for t, q in quotes.items():
        by_game.setdefault(q.get("game_id"), []).append(q)
    bank, bank_meta = incumbent_bank(games, target_season)
    env = {"run_id": run_id, "capture_finished_at": run_ts.isoformat(), "target_season": target_season,
           "game_env_version": "game_env-0.2.0", "n_sims": R.N_SIMS, "center_provenance": "incumbent_replay",
           "residual_bank": bank_meta,
           "implied_line_search": {"spread_grid": list(IMPLIED_SPREAD_GRID), "total_grid": list(IMPLIED_TOTAL_GRID),
                                   "nsims": IMPLIED_NSIMS, "max_width": 0.06, "min_rungs": 6},
           "games": {}, "games_without_environment": {}}
    sims = {}
    gl = [g for g in by_game if g]
    if limit_games:
        gl = gl[:limit_games]
    for gid in gl:
        if gid not in gidx:
            env["games_without_environment"][gid] = "market did not join a scheduled game"
            continue
        row = gidx[gid]
        qs = [{"family": r.get("family"), "period": r.get("period"), "team": r.get("team"), "threshold": r.get("threshold"),
               "floor_strike": r.get("floor_strike"), "yes_bid": _f(r.get("yes_bid_dollars")), "yes_ask": _f(r.get("yes_ask_dollars")),
               "volume": _f(r.get("volume_fp"))} for r in by_game[gid]]
        s_imp, t_imp, diag = implied_game_lines(qs, bank, simulate_game, row["home_team"], row["away_team"],
                                                spread_grid=np.arange(*IMPLIED_SPREAD_GRID), total_grid=np.arange(*IMPLIED_TOTAL_GRID),
                                                nsims=IMPLIED_NSIMS)
        s_use = s_imp if s_imp is not None else _num(row.get("spread_line"))
        t_use = t_imp if t_imp is not None else _num(row.get("total_line"))
        if s_use is None or t_use is None:
            env["games_without_environment"][gid] = "no Kalshi-implied line and no consensus line: " + str(diag.get("reason"))
            continue
        sims[gid] = simulate_game(s_use, t_use, bank, n=R.N_SIMS)          # advances the stream exactly as the incumbent did
        ko = kickoff_utc(str(row.get("gameday") or ""), str(row.get("gametime") or ""))
        env["games"][gid] = {
            "spread_home": float(s_use), "total": float(t_use), "source": "kalshi_implied" if s_imp is not None else "consensus_line",
            "kalshi_implied_spread": s_imp, "kalshi_implied_total": t_imp,
            "implied_diag": {k: (float(v) if isinstance(v, (int, float, np.floating)) else v) for k, v in diag.items()},
            "fallback_reason": None if s_imp is not None else str(diag.get("reason") or "implied lines unavailable"),
            "consensus_spread_line": _num(row.get("spread_line")), "consensus_total_line": _num(row.get("total_line")),
            "home": row["home_team"], "away": row["away_team"], "season": int(row["season"]), "week": int(row["week"]),
            "kickoff_utc": ko.isoformat() if ko else None, "n_sims": R.N_SIMS}
        verbose(f"  replay {gid}: spread {s_use} total {t_use} ({env['games'][gid]['source']})")
    return {"env": env, "sims": sims, "bank": bank, "quotes": quotes, "books": books, "confirmed_series": confirmed_series,
            "run_id": run_id, "run_ts": run_ts, "ages": ages, "gidx": gidx}


def find_ledger_rows(ledger_dir: str, run_id: str):
    """The incumbent's own observations for this capture run, if the pricer wrote them locally. Read only."""
    import gzip
    files = sorted(glob.glob(os.path.join(ledger_dir, "*", f"{run_id}.*.observations.jsonl.gz")))
    if not files:
        return None, None
    return [json.loads(l) for l in gzip.open(files[-1], "rt")], files[-1]


def observation_like_rows(quotes: dict, confirmed_series: set, env: dict, books: dict | None = None) -> list:
    """Capture rows in the ledger-observation shape, with the incumbent's support gating mirrored. Used when no
    ledger snapshot exists for the capture (the horizon conductor). No model price is invented."""
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
        ob = (bk.get("orderbook_fp") or {}) if isinstance(bk, dict) else {}
        def depth(key):
            try:
                return sum(float(x[1]) for x in (ob.get(key) or []))
            except (TypeError, ValueError, IndexError):
                return None
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
                    "book_depth_yes": depth("yes_dollars") if ob else None, "book_depth_no": depth("no_dollars") if ob else None,
                    "support_state": state, "support_reason": why})
    return out
