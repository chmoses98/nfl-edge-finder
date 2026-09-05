#!/usr/bin/env python3
"""Price EVERY supported Kalshi NFL market at the latest capture snapshot and write the shadow ledger.

Market-anchored by construction: the model is compared only to the quotes captured in the SAME snapshot. A
market with no fresh quote is not priced against a stale one -- it is written with support_state=STALE_DATA.

Pipeline
  capture snapshot (market-data)  ->  classify  ->  join game & player identity
  game environment: Kalshi-implied (spread,total) per game -> joint residual simulation -> game family prices
  player: point-in-time features -> fitted mean model + chosen distribution family -> P(stat >= K | plays)
  availability: ESPN/Sleeper/roster state -> P(plays), P(active no snap), P(inactive)
  settlement:   contract value = P(plays)*P(event) + P(no snap)*fair_price   (inactive pays 0)
  ledger:       append-only observation per market, priced or with an explicit unsupported/degraded reason

Nothing is selected and nothing is recommended. Disagreement fields are research quantities.
"""
from __future__ import annotations

import argparse, glob, gzip, hashlib, json, os, sys
from datetime import datetime, timezone, timedelta

import numpy as np
import pandas as pd
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.kalshi.classifier import classify                                    # noqa: E402
from nfl_edge.pricing.game_env import ResidualBank, simulate_game                  # noqa: E402
from nfl_edge.pricing.market_implied import implied_game_lines, market_implied_survival  # noqa: E402
from nfl_edge.research import player_distributions as pdist                        # noqa: E402
from nfl_edge.settlement import semantics as sem_mod                               # noqa: E402
from nfl_edge.settlement.availability import AvailabilityBook, UNKNOWN             # noqa: E402
from nfl_edge.shadow import ledger as L                                            # noqa: E402
from nfl_edge.shadow.models import fit_bundle, KALSHI_STAT_TO_SPEC                 # noqa: E402
from nfl_edge.shadow.prospective import build_prospective_rows, upcoming_from_markets  # noqa: E402
from nfl_edge.features import opportunity  # noqa: E402

GAME_FAMILIES = {"GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL", "WIN_MARGIN_BUCKET", "TOTAL_TD", "BOTH_TEAMS_SCORE_N"}
MODEL_VERSION_DEFAULT = "shadow-0.4.0"


def latest_files(pattern, n=1):
    fs = sorted(glob.glob(pattern))
    return fs[-n:] if fs else []


def load_latest_quotes(capture_root: str, max_age_min: float):
    """Latest quote row per ticker, plus which series were CONFIRMED at the latest run.

    The capture is change-suppressed: a market with an unchanged price writes no row. So the age of the last
    written row is the time since the price last MOVED, not staleness. A quote is current if its series was
    fetched completely in the latest capture run -- that run looked at the market and found the same price.
    Both quantities are kept: `confirmed` (is this the live price?) and `age` (how long since it last moved,
    which is itself a microstructure signal)."""
    files = sorted(glob.glob(os.path.join(capture_root, "*", "*.quotes.jsonl")))
    mans = sorted(glob.glob(os.path.join(capture_root, "*", "*.manifest.json")))
    if not files or not mans:
        return {}, None, {}, set()
    man = json.load(open(mans[-1]))
    run_ts = datetime.fromisoformat(man["finished_at"])
    confirmed_series = {s for s, v in (man.get("series") or {}).items() if v.get("complete")}
    quotes = {}
    for f in reversed(files):                      # newest first
        for line in open(f):
            r = json.loads(line)
            t = r["ticker"]
            if t not in quotes:
                quotes[t] = r
    ages = {}
    for t, r in quotes.items():
        obs = datetime.fromisoformat(r["observed_at"])
        ages[t] = (run_ts - obs).total_seconds() / 60.0
    return quotes, run_ts, ages, confirmed_series


def load_books(capture_root: str):
    books = {}
    for f in sorted(glob.glob(os.path.join(capture_root, "*", "*.books.jsonl"))):
        for line in open(f):
            r = json.loads(line)
            books[r["ticker"]] = r
    return books


def book_summary(book_row):
    if not book_row or not book_row.get("orderbook_fp"):
        return {}
    ob = book_row["orderbook_fp"]
    def side(key):
        lv = ob.get(key) or []
        try:
            depth = sum(float(x[1]) for x in lv)
        except (TypeError, ValueError, IndexError):
            depth = None
        return depth, len(lv)
    dy, ny = side("yes_dollars"); dn, nn = side("no_dollars")
    imb = None
    if dy is not None and dn is not None and (dy + dn) > 0:
        imb = (dy - dn) / (dy + dn)
    return {"book_depth_yes": dy, "book_depth_no": dn, "book_levels_yes": ny, "book_levels_no": nn, "book_imbalance": imb}


def f(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default="/home/user/_md")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "ledger"))
    ap.add_argument("--model-version", default=MODEL_VERSION_DEFAULT)
    # Role features are retired by default (H-20260904-022): they improve a fixed synthetic ladder across all
    # skill players and do NOT improve the traded population. The frozen Week-1 arm shadow-0.3.0 was built
    # with them and must pass --role-features to stay reproducible.
    ap.add_argument("--role-features", action="store_true",
                    help="use opportunity/role features (retired from the default by H-022)")
    ap.add_argument("--calibration-version", default="none-v0")
    ap.add_argument("--target-season", type=int, default=2026)
    ap.add_argument("--max-quote-age-min", type=float, default=45.0)
    ap.add_argument("--max-availability-age-min", type=float, default=600.0)
    ap.add_argument("--limit-games", type=int, default=0)
    a = ap.parse_args()
    t0 = datetime.now(timezone.utc)
    capture_root = os.path.join(a.market_data, "data", "kalshi", "capture")
    quotes, run_ts, ages, confirmed_series = load_latest_quotes(capture_root, a.max_quote_age_min)
    if not quotes:
        print("no capture quotes found"); return 2
    run_id = run_ts.strftime("%Y%m%dT%H%M%SZ")
    books = load_books(capture_root)
    print(f"snapshot {run_id}: {len(quotes)} tickers, {len(books)} books", flush=True)

    games = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet"))
    sched = games.filter(pl.col("season") == a.target_season)
    gidx = sched.to_pandas().set_index("game_id")

    # ---- identity: Kalshi player uuid -> GSIS
    pmap = pl.read_parquet(os.path.join(ROOT, "data/silver/kalshi_player_map.parquet"))
    resolved = pmap.filter(pl.col("gsis_id").is_not_null() & pl.col("status").is_in(
        ["RESOLVED", "RESOLVED_TEAM_UNCONFIRMED", "RESOLVED_PLAYERS_TABLE", "RESOLVED_JERSEY_MISMATCH"]))
    player_map = dict(zip(resolved["kalshi_player_id"].to_list(), resolved["gsis_id"].to_list()))
    not_player = set(pmap.filter(pl.col("status") == "NOT_A_PLAYER")["kalshi_player_id"].to_list())
    players_tbl = pl.read_parquet(os.path.join(ROOT, "data/raw/nflverse/players/players.parquet")).select("gsis_id", "position")
    positions = dict(zip(players_tbl["gsis_id"].to_list(), players_tbl["position"].to_list()))

    # ---- availability from the latest context capture
    ctx_root = os.path.join(a.market_data, "data", "context")
    book_av = AvailabilityBook(run_ts, max_staleness_minutes=a.max_availability_age_min)
    xw = pl.read_parquet(os.path.join(ROOT, "data/silver/player_crosswalk.parquet"))
    sleeper_xw = {str(s): g for s, g in zip(xw["sleeper_id"].to_list(), xw["gsis_id"].to_list()) if s}
    espn_xw = {str(s): g for s, g in zip(xw["espn_id"].to_list(), xw["gsis_id"].to_list()) if s}
    for pat, loader in ((f"{ctx_root}/*/*.sleeper.json", book_av.load_sleeper), (f"{ctx_root}/*/*.espn_injuries.json", book_av.load_espn)):
        fs = latest_files(pat)
        if fs:
            loader(fs[-1], sleeper_xw if "sleeper" in pat else espn_xw)
    rost = os.path.join(ROOT, "data/raw/nflverse/weekly_rosters", f"roster_weekly_{a.target_season}.parquet")
    if os.path.exists(rost):
        r = pl.read_parquet(rost)
        wk = int(sched["week"].min()) if sched.height else 1
        book_av.load_roster(r.filter(pl.col("week") == wk).select("gsis_id", "status").to_dicts(), f"week{wk}")
    book_av.finalize()
    print(f"availability: {len(book_av.by_gsis)} players, sources={list(book_av.source_meta)}, stale={book_av.is_stale()}", flush=True)

    # ---- classify every quoted market once
    rows = []
    for t, q in quotes.items():
        s = classify({"ticker": t, "event_ticker": q.get("event_ticker"), "series_ticker": q.get("series_ticker"),
                      "title": q.get("player_name") or "", "strike_type": None, "floor_strike": q.get("floor_strike")})
        rows.append({**q, "_sem_family": q.get("family"), "_age": ages.get(t)})
    by_game = {}
    for r in rows:
        by_game.setdefault(r.get("game_id"), []).append(r)
    print(f"games with quoted markets: {len([g for g in by_game if g])}", flush=True)

    # ---- game environment: residual bank + Kalshi-implied lines
    hist_games = games.filter((pl.col("game_type") == "REG") & pl.col("result").is_not_null()
                              & pl.col("spread_line").is_not_null() & (pl.col("season") >= 2016)).to_pandas()
    hist_games["mres"] = hist_games.result - hist_games.spread_line
    hist_games["tres"] = hist_games.total - hist_games.total_line
    bank = ResidualBank(hist_games.mres, hist_games.tres, hist_games.season, ref_season=a.target_season,
                        spread_lines=hist_games.spread_line, total_lines=hist_games.total_line,
                        overtime=hist_games.overtime.fillna(0).astype(int), results=hist_games.result,
                        halflife=3.0, rng=np.random.default_rng(11))
    game_env = {}
    gl = [g for g in by_game if g]
    if a.limit_games:
        gl = gl[: a.limit_games]
    for gid in gl:
        if gid not in gidx.index:
            continue
        row = gidx.loc[gid]
        qs = [{"family": r["family"], "period": r["period"], "team": r["team"], "threshold": r["threshold"],
               "floor_strike": r["floor_strike"], "yes_bid": f(r.get("yes_bid_dollars")), "yes_ask": f(r.get("yes_ask_dollars")),
               "volume": f(r.get("volume_fp"))} for r in by_game[gid]]
        s_imp, t_imp, diag = implied_game_lines(qs, bank, simulate_game, row["home_team"], row["away_team"],
                                                spread_grid=np.arange(-17, 17.5, 0.5), total_grid=np.arange(34, 62.5, 0.5),
                                                nsims=12000)
        s_use = s_imp if s_imp is not None else (float(row["spread_line"]) if pd.notna(row["spread_line"]) else None)
        t_use = t_imp if t_imp is not None else (float(row["total_line"]) if pd.notna(row["total_line"]) else None)
        if s_use is None or t_use is None:
            continue
        sim = simulate_game(s_use, t_use, bank, n=40000)
        game_env[gid] = {"sim": sim, "spread": s_use, "total": t_use, "source": "kalshi_implied" if s_imp is not None else "consensus_line",
                         "diag": diag, "home": row["home_team"], "away": row["away_team"],
                         "kickoff": row["gameday"] + " " + str(row["gametime"])}
        print(f"  {gid}: implied spread {s_use} total {t_use} ({game_env[gid]['source']}, {diag.get('n_liquid_rungs')} liquid rungs)", flush=True)

    # ---- player models
    hist = pdist.load_player_games(ROOT, range(2013, a.target_season))
    cfg = json.load(open(os.path.join(ROOT, "research/player_distributions/results.json")))["config"]
    priors = pdist.position_priors(hist, range(2013, 2016))
    qb_ids = {}
    for gid, row in gidx.iterrows():
        s = set()
        for c in ("home_qb_id", "away_qb_id"):
            v = row.get(c)
            if isinstance(v, str) and v:
                s.add(v)
        qb_ids[gid] = s
    upcoming = upcoming_from_markets([r for r in rows if r.get("player_kalshi_id")], player_map, sched, a.target_season, positions, qb_ids)
    print(f"prospective player-game rows: {len(upcoming)}", flush=True)
    bundle = None; feat = None
    if len(upcoming):
        combined = build_prospective_rows(hist, upcoming)
        combined = pdist.add_ewma_features(combined, halflife=cfg["halflife"], season_carry=cfg["season_carry"],
                                           shrink_k=cfg["shrink_k"], priors=priors)
        # Opportunity-engine role features, attached by the same routine the walk-forward study used. A
        # prospective row has no usage outcome, so it receives features built from strictly prior games.
        try:
            combined = opportunity.attach_role_features(combined, halflife=cfg["halflife"],
                                                        season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"])
            print(f"role features attached: {pdist.has_role_features(combined)}", flush=True)
        except FileNotFoundError as exc:
            print(f"::warning::role features unavailable ({exc}); pricing without them", flush=True)
        feat = combined[combined.is_prospective == True].copy()   # noqa: E712
        histf = combined[combined.is_prospective != True].copy()  # noqa: E712
        bundle = fit_bundle(histf, a.target_season, a.model_version,
                            {"ewma": cfg, "min_train_season": 2016, "use_role_features": a.role_features})
        # a count-shape companion for anytime TD, used only to extend the ladder above 1+
        from nfl_edge.shadow.models import CHOSEN_FAMILY as _CF
        _CF_backup = dict(_CF); _CF["anytime_td"] = "negbin"
        cnt_bundle = fit_bundle(histf, a.target_season, a.model_version + "-tdcount",
                                {"ewma": cfg, "min_train_season": 2016, "use_role_features": a.role_features},
                                stats=["anytime_td"], verbose=lambda *_: None)
        _CF.clear(); _CF.update(_CF_backup)
        if "anytime_td" in cnt_bundle.stat_models:
            bundle.stat_models["anytime_td_count"] = cnt_bundle.stat_models["anytime_td"]
        print(f"model bundle {bundle.version} sha={bundle.artifact_sha} stats={list(bundle.stat_models)}", flush=True)

    # ---- price
    out_root = a.out
    writer = L.LedgerWriter(out_root, run_id, model_version=a.model_version)
    feature_cutoff = run_ts.isoformat()
    n_priced = 0
    survival_cache = {}
    for t, q in quotes.items():
        fam = q.get("family"); period = q.get("period")
        age = ages.get(t)
        yb, ya = f(q.get("yes_bid_dollars")), f(q.get("yes_ask_dollars"))
        nb, na = f(q.get("no_bid_dollars")), f(q.get("no_ask_dollars"))
        mid = (yb + ya) / 2.0 if (yb is not None and ya is not None) else None
        obs = L.Observation(
            prediction_id=L.prediction_id(run_id, t, a.model_version, a.calibration_version),
            schema_version=L.LEDGER_SCHEMA_VERSION, run_id=run_id, observed_at=q.get("observed_at"),
            model_version=a.model_version, model_artifact_sha=(bundle.artifact_sha if bundle else ""),
            calibration_version=a.calibration_version, feature_cutoff=feature_cutoff,
            ticker=t, event_ticker=q.get("event_ticker"), series_ticker=q.get("series_ticker"), family=fam,
            period=period, stat=q.get("stat"), threshold=q.get("threshold"), floor_strike=q.get("floor_strike"),
            operator=q.get("operator"), game_id=q.get("game_id"), team=q.get("team"),
            player_kalshi_id=q.get("player_kalshi_id"), player_name=q.get("player_name"),
            kickoff_utc=q.get("kickoff_utc"), minutes_to_kickoff=q.get("minutes_to_kickoff"),
            yes_bid=yb, yes_ask=ya, no_bid=nb, no_ask=na, mid=mid,
            quote_width=(ya - yb) if (yb is not None and ya is not None) else None,
            volume=f(q.get("volume_fp")), open_interest=f(q.get("open_interest_fp")),
            minutes_since_price_change=age,
            last_price=f(q.get("last_price_dollars")), liquidity=f(q.get("liquidity_dollars")),
            game_env_version="game_env-0.2.0", **book_summary(books.get(t)))
        if q.get("game_id") in gidx.index:
            row = gidx.loc[q["game_id"]]
            obs.season = int(row["season"]); obs.week = int(row["week"])
            obs.home_team = row["home_team"]; obs.away_team = row["away_team"]
        ok, reason = sem_mod.settlement_supported(fam)
        if not ok:
            obs.support_state = L.UNSUPPORTED_RULES if fam in sem_mod.UNSUPPORTED_SETTLEMENT_REASON else L.UNSUPPORTED_MODEL
            obs.support_reason = reason
            writer.write(obs); continue
        if q.get("pregame") is False:
            obs.support_state = L.POST_KICKOFF_EXCLUDED; obs.support_reason = "quote observed after kickoff"
            writer.write(obs); continue
        if q.get("series_ticker") not in confirmed_series:
            obs.support_state = L.STALE_DATA
            obs.support_reason = f"series {q.get('series_ticker')} not confirmed complete in the latest capture run"
            writer.write(obs); continue
        gid = q.get("game_id")
        if not gid or gid not in game_env:
            obs.support_state = L.UNSUPPORTED_GAME
            obs.support_reason = "market did not join a scheduled game" if not gid else "no game environment for this game"
            writer.write(obs); continue
        env = game_env[gid]; sim = env["sim"]
        m, tot, hs, aw = sim["margin"], sim["total"], sim["home"], sim["away"]
        p = None
        try:
            if fam == "GAME_WINNER":
                p_win = float(np.mean(m > 0)) if q.get("team") == env["home"] else float(np.mean(m < 0))
                cv = sem_mod.game_winner_contract_value(p_win, float(np.mean(m == 0)))
                p = cv.event_probability; obs.model_contract_value = cv.contract_value
            elif fam == "SPREAD" and period == "FULL":
                x = m if q.get("team") == env["home"] else -m
                p = float(np.mean(x > float(q["floor_strike"]))); obs.model_contract_value = p
            elif fam == "TOTAL" and period == "FULL":
                p = float(np.mean(tot >= float(q["threshold"]))); obs.model_contract_value = p
            elif fam == "TEAM_TOTAL" and period == "FULL":
                x = hs if q.get("team") == env["home"] else aw
                p = float(np.mean(x >= float(q["threshold"]))); obs.model_contract_value = p
            elif fam == "BOTH_TEAMS_SCORE_N":
                k = float(q["threshold"]); p = float(np.mean((hs >= k) & (aw >= k))); obs.model_contract_value = p
            elif fam == "PLAYER_STAT":
                kid = q.get("player_kalshi_id")
                if kid in not_player:
                    obs.support_state = L.UNSUPPORTED_MODEL; obs.support_reason = "team D/ST or non-player leg"
                    writer.write(obs); continue
                gsis = player_map.get(kid)
                if not gsis:
                    obs.support_state = L.UNSUPPORTED_IDENTITY
                    obs.support_reason = "Kalshi player id not resolved to a GSIS id"
                    writer.write(obs); continue
                obs.player_id = gsis
                pos = positions.get(gsis)
                spec_name = KALSHI_STAT_TO_SPEC.get((q.get("stat"), "QB" if pos == "QB" else None)) or \
                            KALSHI_STAT_TO_SPEC.get((q.get("stat"), None))
                if q.get("stat") == "rushing_yards" and pos == "QB":
                    spec_name = "qb_rushing_yards"
                if spec_name is None or (bundle is None):
                    obs.support_state = L.UNSUPPORTED_MODEL; obs.support_reason = f"no model for stat {q.get('stat')}"
                    writer.write(obs); continue
                sub = feat[(feat.player_id == gsis) & (feat.game_id == gid)]
                if not len(sub):
                    obs.support_state = L.DEGRADED_INPUT; obs.support_reason = "no prospective feature row for this player-game"
                    writer.write(obs); continue
                av = book_av.get(gsis)
                obs.availability_state = av.state; obs.p_plays = av.p_plays; obs.p_inactive = av.p_inactive
                if spec_name == "anytime_td":
                    if bundle.td_model is None:
                        obs.support_state = L.UNSUPPORTED_MODEL; obs.support_reason = "TD model unavailable"
                        writer.write(obs); continue
                    p1 = float(bundle.td_model.predict(sub)[0])
                    kk = float(q.get("threshold") or 1)
                    if kk <= 1:
                        p = p1
                    else:
                        # shape from the count family, level anchored on the validated direct 1+ model, so the
                        # ladder stays monotone and consistent with the model we actually trust at 1+.
                        cnt = bundle.stat_models.get("anytime_td_count")
                        if cnt is None:
                            obs.support_state = L.UNSUPPORTED_MODEL
                            obs.support_reason = "multi-touchdown rung needs the count-shape model (not fitted)"
                            writer.write(obs); continue
                        grid, S, _mu = cnt.survival(sub)
                        i1 = int(np.searchsorted(grid, 1.0, side="left")); ik = int(np.searchsorted(grid, kk, side="left"))
                        base = float(S[0][min(i1, len(S[0]) - 1)])
                        p = p1 * (float(S[0][min(ik, len(S[0]) - 1)]) / base) if base > 1e-9 else 0.0
                else:
                    sm = bundle.stat_models.get(spec_name)
                    if sm is None:
                        obs.support_state = L.UNSUPPORTED_MODEL; obs.support_reason = f"no fitted model for {spec_name}"
                        writer.write(obs); continue
                    ck = (spec_name, gsis, gid)
                    if ck not in survival_cache:
                        grid, S, mu = sm.survival(sub)
                        survival_cache[ck] = (grid, S[0], float(mu[0]))
                    grid, S, mu = survival_cache[ck]
                    k = float(q["threshold"])
                    idx = int(np.searchsorted(grid, k, side="left"))
                    p = float(S[min(idx, len(S) - 1)]) if k <= grid[-1] else 0.0
                cv = sem_mod.player_prop_contract_value(p, av.p_plays, av.p_active_no_snap, mid)
                obs.model_contract_value = cv.contract_value
                if av.state == UNKNOWN:
                    obs.quality_flags.append("availability_unknown")
                if av.stale_minutes and av.stale_minutes > a.max_availability_age_min:
                    obs.quality_flags.append("availability_stale")
            elif fam in ("WIN_MARGIN_BUCKET", "TOTAL_TD", "FIRST_TD_TEAM", "FIRST_TD_SCORER", "PERIOD_WINNER"):
                if fam == "TOTAL_TD":
                    obs.support_state = L.UNSUPPORTED_MODEL; obs.support_reason = "game touchdown count not modelled yet"
                elif fam == "WIN_MARGIN_BUCKET":
                    lo = q.get("range_lo"); hi = q.get("range_hi")
                    obs.support_state = L.UNSUPPORTED_MODEL
                    obs.support_reason = "margin-bucket bounds not carried in the capture schema yet"
                else:
                    obs.support_state = L.UNSUPPORTED_MODEL
                    obs.support_reason = f"{fam} model not validated"
                writer.write(obs); continue
            else:
                obs.support_state = L.UNSUPPORTED_MODEL
                obs.support_reason = f"family {fam} period {period} not priced"
                writer.write(obs); continue
        except Exception as e:                                    # fail closed, never write a guessed price
            obs.support_state = L.DEGRADED_INPUT; obs.support_reason = f"pricing error: {type(e).__name__}: {e}"
            writer.write(obs); continue
        if p is None or not (0.0 <= p <= 1.0):
            obs.support_state = L.DEGRADED_INPUT; obs.support_reason = "model produced no valid probability"
            writer.write(obs); continue
        obs.model_event_probability = p
        obs.calibrated_probability = obs.model_contract_value      # identity until a calibration artifact exists
        if mid is not None and obs.model_contract_value is not None:
            obs.model_market_disagreement = obs.model_contract_value - mid
        if ya is not None and obs.model_contract_value is not None:
            obs.raw_yes_disagreement = obs.model_contract_value - ya
        if na is not None and obs.model_contract_value is not None:
            obs.raw_no_disagreement = (1.0 - obs.model_contract_value) - na
        obs.support_state = L.SUPPORTED
        writer.write(obs); n_priced += 1

    # ---- market-implied player distributions (one per player+stat ladder with >=3 rungs)
    ladders = {}
    for t, q in quotes.items():
        if q.get("family") == "PLAYER_STAT" and q.get("player_kalshi_id") and q.get("threshold") is not None:
            ladders.setdefault((q["player_kalshi_id"], q.get("stat"), q.get("game_id")), []).append(
                {"threshold": q["threshold"], "yes_bid": f(q.get("yes_bid_dollars")), "yes_ask": f(q.get("yes_ask_dollars")),
                 "volume": f(q.get("volume_fp"))})
    implied = {}
    for key, rws in ladders.items():
        r = market_implied_survival(rws, side="mid")
        if r:
            implied["|".join(str(x) for x in key)] = r
    man = writer.close({"snapshot_run_id": run_id, "priced": n_priced, "games_with_env": len(game_env),
                        "model_bundle": bundle.to_json() if bundle else None,
                        "availability_sources": book_av.source_meta,
                        "market_implied_ladders": len(implied),
                        "confirmed_series": len(confirmed_series),
                        "minutes_since_price_change": {"max": max(ages.values()) if ages else None,
                                                       "median": float(np.median(list(ages.values()))) if ages else None},
                        "seconds": (datetime.now(timezone.utc) - t0).total_seconds()})
    with gzip.open(os.path.join(writer.dir, f"{run_id}.market_implied.json.gz"), "wt") as fh:
        json.dump(implied, fh)
    print(json.dumps({k: v for k, v in man.items() if k not in ("model_bundle",)}, indent=1, default=str))
    return 0


if __name__ == "__main__":
    sys.exit(main())
