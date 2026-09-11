#!/usr/bin/env python3
"""SHADOW v2 slate projector: every captured NFL contract -> a ProjectionRecord from the engine its question names.

    game questions      the incumbent joint (margin, total) simulation from Kalshi-implied lines (frozen game_env /
                        market_implied modules), answered generically (spread, total, team total, winner, margin
                        buckets, both-score, min/max team points ...)
    period questions    the period engine's joint quarter simulation at the SAME implied lines (1H / 1Q / 2H ... winner,
                        spread, total, team total, both-score) + half/full doubles and same-game parlays over score
                        legs through the joint engine
    player questions    three arms on one distribution object: DATA_PLAYER_DIST (opportunity x efficiency, v2
                        features), MARKET_PLAYER_DIST (monotone ladder), HYBRID_PLAYER_DIST (research blend)
    season questions    the season engine's schedule Monte Carlo (wins, division, playoffs)
    everything else     a terminal support state with the reason (never a probability)

Every record is PROSPECTIVE_FROZEN only when both the market observation and this run happen strictly before
kickoff; a contract whose game has kicked off is POST_KICKOFF without a probability. `--allow-historical` marks a
deliberately late run HISTORICAL_RESEARCH instead (local validation only; the workflows never pass it). Real-money
authority: none. Incumbent gates: untouched. Output: data/shadow/v2/projections/<day>/<snapshot>.<arm>.projections.jsonl.gz
(append-only; a re-run of the same snapshot is a no-op or a conflict, never an overwrite).
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import resource
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.data.nfl_calendar import kickoff_utc                                        # noqa: E402
from nfl_edge.engines import coherence as CE, game as GE, joint as JE, period as PE, season as SE  # noqa: E402
from nfl_edge.engines.player import data_dist as DD, hybrid_dist as HD, market_dist as MD   # noqa: E402
from nfl_edge.engines.player.features_v2 import add_v2_features                             # noqa: E402
from nfl_edge.execution.fees import load_fee_schedule                                      # noqa: E402
from nfl_edge.pricing.game_env import ResidualBank, simulate_game                          # noqa: E402
from nfl_edge.pricing.market_implied import implied_game_lines                             # noqa: E402
from nfl_edge.projection import horizons as HZ                                             # noqa: E402
from nfl_edge.projection import quality as QU                                              # noqa: E402
from nfl_edge.projection import record as R                                                # noqa: E402
from nfl_edge.projection.store import DIRNAME, ProjectionConflict, ProjectionStore, context_id, sidecar_path, write_sidecar  # noqa: E402
from nfl_edge.research import player_distributions as pdist                                # noqa: E402
from nfl_edge.semantics import catalog as CAT, questions as Q                              # noqa: E402
from nfl_edge.settlement import semantics as sem_mod                                       # noqa: E402
from nfl_edge.settlement.availability import UNKNOWN, AvailabilityBook, rates_for          # noqa: E402
from nfl_edge.shadow.prospective import build_prospective_rows, upcoming_from_markets      # noqa: E402
from nfl_edge.shadow_v2 import context as CX                                              # noqa: E402
from nfl_edge.shadow_v2.capture_io import (discovery_markets_by_ticker, fnum, latest_discovery_dir,  # noqa: E402
                                           load_books, load_latest_quotes, static_market)

MODEL_VERSION = "shadow-v2-1.0.0"
ARM_BOARD = "BOARD_V2"
ARM_DATA, ARM_MARKET, ARM_HYBRID = "DATA_PLAYER_DIST", "MARKET_PLAYER_DIST", "HYBRID_PLAYER_DIST"
PLAYER_ARMS = (ARM_DATA, ARM_MARKET, ARM_HYBRID)
ENGINE_STATS = {"passing_yards": "passing_yards", "passing_tds": "passing_tds", "interceptions": "interceptions", "attempts": "attempts",
                "completions": "completions", "rushing_yards": "rushing_yards", "carries": "carries", "receiving_yards": "receiving_yards",
                "receptions": "receptions", "touchdowns": "touchdowns", "rush_rec_yards": "rush_rec_yards"}
VOLUME_FEATURE = {"passing_yards": "ewma_team_pass_att", "passing_tds": "ewma_team_pass_att", "interceptions": "ewma_team_pass_att",
                  "attempts": "ewma_team_pass_att", "completions": "ewma_team_pass_att", "receiving_yards": "ewma_team_pass_att",
                  "receptions": "ewma_team_pass_att", "rushing_yards": "ewma_team_rush_att", "carries": "ewma_team_rush_att",
                  "touchdowns": None, "rush_rec_yards": None}
SHARE_FEATURE = {"receiving_yards": "ewma_target_share", "receptions": "ewma_target_share", "rushing_yards": "ewma_carry_share",
                 "carries": "ewma_carry_share"}


def log(*a):
    print(*a, flush=True)


def _dt(s):
    return datetime.fromisoformat(str(s).replace("Z", "+00:00")) if s else None


# ------------------------------------------------------------------------------------------------- support states
def support_state(q: Q.Question, entry, *, pregame: bool, confirmed: bool, answer: dict | None, generated_before_kickoff: bool,
                  allow_historical: bool) -> tuple[str, str | None, float | None, float | None]:
    """(state, reason, p_yes, contract_value). The probability survives only in the two probability states."""
    if not pregame:
        return R.POST_KICKOFF, "market observed after kickoff", None, None
    if not generated_before_kickoff and not allow_historical:
        return R.POST_KICKOFF, "projection generated after kickoff (no hindsight records)", None, None
    if q.semantic_confidence in (Q.AMBIGUOUS, Q.UNKNOWN):
        return R.SEMANTICS_AMBIGUOUS, "; ".join(q.notes) or f"semantics {q.semantic_confidence}", None, None
    if q.engine == Q.NONE:
        st = {CAT.NON_FOOTBALL_MODEL: R.NON_FOOTBALL_MODEL, CAT.NEWS_EVENT_MODEL_REQUIRED: R.NON_FOOTBALL_MODEL, CAT.JOINT_MODEL_REQUIRED: R.JOINT_MODEL_REQUIRED,
              CAT.DATA_UNAVAILABLE: R.DATA_UNAVAILABLE, CAT.RESEARCH_REQUIRED: R.RESEARCH_REQUIRED, CAT.UNSUPPORTED: R.UNSUPPORTED}.get(
            entry.model_support if entry else None, R.UNSUPPORTED)
        return st, (entry.reason if entry else "no engine for this question"), None, None
    if answer is None or answer.get("p_yes") is None:
        reason = (answer or {}).get("reason") or "engine returned no probability"
        st = R.JOINT_MODEL_REQUIRED if (answer or {}).get("status") == JE.JOINT_MODEL_REQUIRED else \
            (R.IDENTITY_UNRESOLVED if (answer or {}).get("status") == "IDENTITY_UNRESOLVED" else
             (R.DATA_UNAVAILABLE if (answer or {}).get("status") == "DATA_UNAVAILABLE" else R.RESEARCH_REQUIRED))
        return st, reason, None, None
    if not confirmed:
        return R.STALE_MARKET, "series not confirmed complete in this capture run", None, None
    p, cv = float(answer["p_yes"]), float(answer.get("contract_value", answer["p_yes"]))
    if q.semantic_confidence == Q.PROVEN and entry is not None and entry.model_support == CAT.PRICED and answer.get("validated", True):
        return R.PRICED, None, p, cv
    return R.PROJECTABLE_NOT_YET_VALIDATED, (f"semantics {q.semantic_confidence}" if q.semantic_confidence != Q.PROVEN else
                                             f"engine/family in shadow ({entry.model_support if entry else 'uncatalogued'})"), p, cv


# ------------------------------------------------------------------------------------------------- period table cache
def period_bank(target_season: int, seasons_lo: int = 2012) -> PE.PeriodBank:
    cache = os.path.join(ROOT, "data", "silver", f"period_scores_{seasons_lo}_{target_season - 1}.parquet")
    if os.path.exists(cache):
        tbl = pl.read_parquet(cache)
    else:
        tbl = PE.build_period_table(ROOT, range(seasons_lo, target_season))
        os.makedirs(os.path.dirname(cache), exist_ok=True)
        tbl.write_parquet(cache)
    return PE.PeriodBank(tbl.filter(pl.col("season") < target_season), ref_season=target_season)


# ------------------------------------------------------------------------------------------------- main
def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default="/home/user/_md")
    ap.add_argument("--out", default=os.path.join(ROOT, "data"), help="root under which shadow/v2/projections is written")
    ap.add_argument("--discovery-dir", default="")
    ap.add_argument("--snapshot-id", default="", help="price this capture run (default: latest)")
    ap.add_argument("--target-season", type=int, default=2026)
    ap.add_argument("--now", default="", help="override the wall clock (tests only)")
    ap.add_argument("--horizon-id", default="", help="<slate>|<trigger>|T-<n>m from the horizon gate; else CYCLE")
    ap.add_argument("--n-sims", type=int, default=40000)
    ap.add_argument("--limit-games", type=int, default=0)
    ap.add_argument("--skip-player", action="store_true")
    ap.add_argument("--skip-season", action="store_true")
    ap.add_argument("--allow-historical", action="store_true", help="mark a post-kickoff run HISTORICAL_RESEARCH instead of refusing (local only)")
    ap.add_argument("--summary-dir", default="", help="where the run summary goes (default <out>/shadow/v2/runs)")
    a = ap.parse_args(argv)
    t0 = time.time()
    now = _dt(a.now) if a.now else datetime.now(timezone.utc)
    capture_root = os.path.join(a.market_data, "data", "kalshi", "capture")
    quotes, run_ts, ages, confirmed, man = load_latest_quotes(capture_root, snapshot_id=a.snapshot_id or None)
    if not quotes:
        log("no capture quotes found"); return 2
    snapshot_id = run_ts.strftime("%Y%m%dT%H%M%SZ")
    books = load_books(capture_root)
    ddir = a.discovery_dir or latest_discovery_dir(a.market_data)
    disc_markets = discovery_markets_by_ticker(ddir) if ddir else {}
    log(f"snapshot {snapshot_id}: {len(quotes)} tickers, {len(books)} books, discovery {os.path.basename(ddir) if ddir else 'none'} ({len(disc_markets)} markets)")

    ctx = CX.ContextSources(ROOT, a.market_data, a.target_season, run_ts, log=log)
    reused = snapshot_reused([a.out, os.path.join(a.market_data, "data")], snapshot_id)
    log(f"context: depth chart vintage {(ctx.depth or {}).get('vintage')}, injuries {'yes' if ctx.injuries else 'no'}, weather games {len(ctx.weather)}, trade-tape tickers {len(ctx.last_trade)}, snapshot reused {reused}")
    games = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet"))
    sched = games.filter(pl.col("season") == a.target_season)
    gidx = sched.to_pandas().set_index("game_id")
    kick = {gid: kickoff_utc(str(r["gameday"]), str(r["gametime"])) for gid, r in gidx.iterrows()}

    # ---- semantics for every quoted contract
    sems, qs = {}, {}
    for t, q in quotes.items():
        m = static_market(q, disc_markets)
        try:
            sem, qq = Q.question_from_market(m)
        except Exception as e:  # noqa: BLE001 -- a parser fault is a refusal, never a crash of the slate
            sem, qq = None, Q.Question(kind=Q.EVENT, engine=Q.NONE, semantic_confidence=Q.UNKNOWN, notes=(f"parser error: {e}",))
        sems[t], qs[t] = sem, qq
    by_game = defaultdict(list)
    for t, q in quotes.items():
        if q.get("game_id"):
            by_game[q["game_id"]].append(t)
    log(f"questions: {Counter(q.engine for q in qs.values())}; confidence {Counter(q.semantic_confidence for q in qs.values())}")

    # ---- game + period environments
    hist_games = games.filter((pl.col("game_type") == "REG") & pl.col("result").is_not_null() & pl.col("spread_line").is_not_null()
                              & (pl.col("season") >= 2016) & (pl.col("season") < a.target_season)).to_pandas()
    hist_games["mres"] = hist_games.result - hist_games.spread_line
    hist_games["tres"] = hist_games.total - hist_games.total_line
    bank = ResidualBank(hist_games.mres, hist_games.tres, hist_games.season, ref_season=a.target_season, spread_lines=hist_games.spread_line,
                        total_lines=hist_games.total_line, overtime=hist_games.overtime.fillna(0).astype(int), results=hist_games.result,
                        halflife=3.0, rng=np.random.default_rng(11))
    pbank = period_bank(a.target_season)
    envs = {}
    gl = sorted(g for g in by_game if g in gidx.index)
    if a.limit_games:
        gl = gl[: a.limit_games]
    for gid in gl:
        row = gidx.loc[gid]
        rows = [{"family": quotes[t]["family"], "period": quotes[t]["period"], "team": quotes[t]["team"], "threshold": quotes[t]["threshold"],
                 "floor_strike": quotes[t]["floor_strike"], "yes_bid": fnum(quotes[t].get("yes_bid_dollars")), "yes_ask": fnum(quotes[t].get("yes_ask_dollars")),
                 "volume": fnum(quotes[t].get("volume_fp"))} for t in by_game[gid]]
        s_imp, t_imp, diag = implied_game_lines(rows, bank, simulate_game, row["home_team"], row["away_team"],
                                                spread_grid=np.arange(-17, 17.5, 0.5), total_grid=np.arange(34, 62.5, 0.5), nsims=12000)
        s_use = s_imp if s_imp is not None else (float(row["spread_line"]) if pd.notna(row["spread_line"]) else None)
        t_use = t_imp if t_imp is not None else (float(row["total_line"]) if pd.notna(row["total_line"]) else None)
        if s_use is None or t_use is None:
            continue
        gsim = simulate_game(s_use, t_use, bank, n=a.n_sims)
        psim = pbank.simulate(s_use, t_use, n=a.n_sims, rng=np.random.default_rng(int.from_bytes(hashlib.sha256(gid.encode()).digest()[:4], "big")))
        envs[gid] = {"gsim": gsim, "psim": psim, "spread": s_use, "total": t_use, "source": "kalshi_implied" if s_imp is not None else "consensus_line",
                     "diag": diag, "home": row["home_team"], "away": row["away_team"], "gap": PE.cross_engine_gap(psim, gsim)}
        log(f"  {gid}: spread {s_use} total {t_use} ({envs[gid]['source']}, {diag.get('n_liquid_rungs')} liquid rungs); 1H/full gap {envs[gid]['gap']}")

    # ---- season engine (schedule Monte Carlo) when any season question is on the board
    season_sim = None
    if not a.skip_season and any(q.engine == Q.SEASON for q in qs.values()):
        reg = sched.filter(pl.col("game_type") == "REG").to_pandas()
        played = defaultdict(lambda: [0, 0, 0])
        remaining, centers = [], {}
        for _, r in reg.iterrows():
            if pd.notna(r["result"]):
                m = float(r["result"])
                for team, sign in ((r["home_team"], 1), (r["away_team"], -1)):
                    played[team][0 if m * sign > 0 else (1 if m * sign < 0 else 2)] += 1
            else:
                remaining.append({"game_id": r["game_id"], "home": r["home_team"], "away": r["away_team"], "week": int(r["week"])})
                if pd.notna(r["spread_line"]):
                    centers[r["game_id"]] = float(r["spread_line"])
        season_sim = SE.simulate_seasons(remaining, {k: tuple(v) for k, v in played.items()}, centers, n=20000, seed_key=f"{a.target_season}:{snapshot_id}")
        season_sim["centers_source"] = f"consensus spread_line for {len(centers)} of {len(remaining)} remaining games; home-field prior elsewhere"
        log(f"season sim: {len(remaining)} remaining games, {season_sim['centers_source']}")

    # ---- player engine (three arms)
    player = None
    if not a.skip_player:
        player = build_player_arms(a, quotes, qs, sched, gidx, run_ts, now)

    lineage = ctx.lineage_block(snapshot_id=snapshot_id, discovery_run=(os.path.basename(ddir) if ddir else None),
                                engine_versions={"game": GE.ENGINE_VERSION, "period": PE.ENGINE_VERSION, "joint": JE.ENGINE_VERSION, "season": SE.ENGINE_VERSION,
                                                 "player_data": DD.VERSION, "player_market": MD.VERSION, "player_hybrid": HD.VERSION, "coherence": CE.ENGINE_VERSION,
                                                 "semantics": Q.SEMANTICS_VERSION, "catalog": CAT.CATALOG_VERSION, "model": MODEL_VERSION, "schema": R.SCHEMA_VERSION},
                                feature_set=("v2" if player and player.bundle else None), bundle_sha=(player.bundle.artifact_sha if player and player.bundle else None),
                                period_bank_fingerprint=pbank.fingerprint,
                                tables=["data/raw/nflverse/schedules/games.csv", f"data/raw/nflverse/stats_player/stats_player_week_{a.target_season - 1}.parquet",
                                        f"data/raw/nflverse/snap_counts/snap_counts_{a.target_season - 1}.parquet", f"data/raw/nflverse/injuries/injuries_{a.target_season}.parquet",
                                        f"data/raw/nflverse/depth_charts/depth_charts_{a.target_season}.parquet", "data/raw/nflverse/players/players.parquet",
                                        f"data/raw/nflverse/rosters/roster_{a.target_season}.parquet"])
    game_ctx_cache, player_ctx_cache = {}, {}
    lineage_id = context_id(lineage)
    store_root = os.path.join(a.out, DIRNAME)
    quoted_by_game = defaultdict(list)
    for t, q in quotes.items():
        if q.get("game_id"):
            quoted_by_game[q["game_id"]].append(t)
    # ---- records
    fee_sched = None
    try:
        fee_sched = load_fee_schedule(ROOT)
    except Exception as e:  # noqa: BLE001
        log(f"fee schedule unavailable: {e}")
    horizon_id = a.horizon_id or None
    board_rows, arm_rows = [], {arm: [] for arm in PLAYER_ARMS}
    gen_iso = now.isoformat()
    coherence_rows = []
    for t, q in quotes.items():
        qq, sem = qs[t], sems[t]
        gid = q.get("game_id")
        ko = kick.get(gid) if gid else None
        entry = CAT.catalog_entry(q.get("family"), q.get("period"), q.get("stat"))
        obs = _dt(q.get("observed_at"))
        pregame = bool(q.get("pregame", True)) and (ko is None or obs < ko)
        gen_before = ko is None or now < ko
        base = dict(snapshot_id=snapshot_id, ticker=t, series_ticker=q.get("series_ticker"), event_ticker=q.get("event_ticker"),
                    market_family=q.get("family"), period=q.get("period") or ("FULL" if gid else None), stat_family=q.get("stat"),
                    question=qq.to_dict(), threshold=qq.k, range_lo=qq.lo, range_hi=qq.hi, operator=qq.op,
                    yes_semantics=(entry.yes_rule if entry else None), semantic_confidence=qq.semantic_confidence,
                    settlement_rule_version=(entry.settlement_rule_version if entry else None), game_id=gid,
                    season=(int(gidx.loc[gid]["season"]) if gid in gidx.index else None), week=(int(gidx.loc[gid]["week"]) if gid in gidx.index else None),
                    home_team=(gidx.loc[gid]["home_team"] if gid in gidx.index else None), away_team=(gidx.loc[gid]["away_team"] if gid in gidx.index else None),
                    subject_kind=qq.subject_kind, subject_id=qq.subject, subject_kalshi_id=q.get("player_kalshi_id"), subject_name=q.get("player_name"),
                    observed_at=q.get("observed_at"), generated_at=gen_iso, kickoff_utc=(ko.isoformat() if ko else None),
                    minutes_to_kickoff=q.get("minutes_to_kickoff"), data_cutoff=run_ts.isoformat(),
                    yes_bid=fnum(q.get("yes_bid_dollars")), yes_ask=fnum(q.get("yes_ask_dollars")), no_bid=fnum(q.get("no_bid_dollars")), no_ask=fnum(q.get("no_ask_dollars")),
                    volume=fnum(q.get("volume_fp")), open_interest=fnum(q.get("open_interest_fp")), liquidity=fnum(q.get("liquidity_dollars")),
                    market_confirmed=q.get("series_ticker") in confirmed,
                    market_quality={"minutes_since_price_change": ages.get(t), "has_book": t in books, "discovery_record": t in disc_markets},
                    evidence_class=(R.PROSPECTIVE_FROZEN if gen_before else R.HISTORICAL_RESEARCH))
        if ko and pregame and horizon_id:
            try:
                base.update(HZ.label_snapshot(obs, ko, horizon_id))
            except ValueError:
                pass
        elif ko and pregame:
            base.update(HZ.label_snapshot(obs, ko, None))
        coherence_rows.append({"ticker": t, "event_ticker": q.get("event_ticker"), "series_ticker": q.get("series_ticker"), "family": q.get("family"),
                               "yes_bid": base["yes_bid"], "yes_ask": base["yes_ask"], "volume": base["volume"], "liquidity": base["liquidity"]})
        # ---- point-in-time context, provenance, horizon quality (frozen on every record, refusals included)
        ser = (man.get("series") or {}).get(q.get("series_ticker")) or {}
        ladder = None
        if player and q.get("family") == "PLAYER_STAT":
            ladder = player.market.get((q.get("player_kalshi_id"), gid, q.get("stat")))
        base["market_state"] = CX.market_state(quote=q, ladder=ladder, last_trade_at=ctx.last_trade.get(t), snapshot_run=snapshot_id,
                                               series_confirmed_at=ser.get("observed_at"), series_complete=ser.get("complete"))
        if gid in gidx.index:
            if gid not in game_ctx_cache:
                full = CX.game_context(ctx, game_row=gidx.loc[gid], env=envs.get(gid), kickoff=ko, quote_ages=ages, tickers=quoted_by_game.get(gid, []),
                                       n_quoted=len(quoted_by_game.get(gid, [])))
                game_ctx_cache[gid] = (context_id(full), full)
            gc_id, full = game_ctx_cache[gid]
            base["game_context"] = CX.compact_game_context(full, gc_id)
        base["lineage"] = {"lineage_id": lineage_id, "capture_run": snapshot_id, "discovery_run": lineage.get("discovery_run"), "identity_map_sha256": (lineage.get("identity_map") or {}).get("sha256"),
                           "engine_versions": lineage.get("engine_versions"), "bundle_sha": lineage.get("bundle_sha"), "period_bank_fingerprint": lineage.get("period_bank_fingerprint"),
                           "depth_chart_vintage": lineage.get("depth_chart_vintage"), "injury_report_retrieved_at": lineage.get("injury_report_retrieved_at"), "sidecar": os.path.basename(sidecar_path(store_root, snapshot_id))}
        base["horizon_quality"] = QU.horizon_quality(base.get("horizon_label"), base.get("horizon_target_min"), base.get("kickoff_utc"), q.get("observed_at"), gen_iso, snapshot_reused=reused)
        # ---- non-player engines -> BOARD arm
        if qq.engine != Q.PLAYER:
            ans, eng_ver, dist_ver = None, "none", "none"
            env = envs.get(gid)
            if qq.engine in (Q.GAME, Q.PERIOD, Q.JOINT) or qq.kind == Q.COMPOSITE:
                if env is None:
                    ans = {"p_yes": None, "reason": "no game environment (no liquid implied lines and no consensus line)", "status": "DATA_UNAVAILABLE"}
                elif qq.kind == Q.COMPOSITE:
                    ans = JE.answer(qq, game_sim=env["gsim"], period_sim=env["psim"], home=env["home"], away=env["away"]); eng_ver, dist_ver = JE.ENGINE_VERSION, PE.DISTRIBUTION_VERSION
                elif qq.engine == Q.GAME:
                    ans = GE.answer(env["gsim"], qq, env["home"], env["away"]); eng_ver, dist_ver = GE.ENGINE_VERSION, "game_env-0.2.0"
                else:
                    ans = PE.answer(env["psim"], qq, env["home"], env["away"]); eng_ver, dist_ver = PE.ENGINE_VERSION, PE.DISTRIBUTION_VERSION
                    if ans.get("p_yes") is not None:
                        ans["validated"] = False                     # period engine: research-validated, never production-validated
            elif qq.engine == Q.SEASON:
                ans = SE.answer(season_sim, qq) if season_sim is not None else {"p_yes": None, "reason": "season engine not run"}
                eng_ver, dist_ver = SE.ENGINE_VERSION, "season-schedule-mc-1.0.0"
                if ans.get("p_yes") is not None:
                    ans["validated"] = False
            st, reason, p, cv = support_state(qq, entry, pregame=pregame, confirmed=base["market_confirmed"], answer=ans,
                                              generated_before_kickoff=gen_before, allow_historical=a.allow_historical)
            base["flags"] = QU.status_flags(support_state=st, semantic_confidence=qq.semantic_confidence, identity_confidence=None, subject_kind=qq.subject_kind,
                                            settlement_support=(entry.settlement if entry else None), engine=qq.engine)
            rec = R.ProjectionRecord(record_id="", model_arm=ARM_BOARD, engine=qq.engine, engine_version=eng_ver, distribution_version=dist_ver,
                                     model_version=MODEL_VERSION, p_yes=p, contract_value=cv, support_state=st, support_reason=reason,
                                     projection_lineage={"game_env": ({"spread": env["spread"], "total": env["total"], "source": env["source"]} if env else None),
                                                         "n_draws": (ans or {}).get("n_draws"), "route": (ans or {}).get("route"),
                                                         "season_centers": (season_sim or {}).get("centers_source") if qq.engine == Q.SEASON else None},
                                     data_quality={"p_tie": (ans or {}).get("p_tie"), "catalog_support": (entry.model_support if entry else None)}, **base)
            rec.record_id = R.record_id(snapshot_id, t, ARM_BOARD, eng_ver, dist_ver)
            board_rows.append(rec.finalize().to_dict())
            continue
        # ---- player engine -> three arms
        for arm in PLAYER_ARMS:
            ans, lineage, feat, dsum = (player.answer(arm, t, q, qq) if player else ({"p_yes": None, "reason": "player engine skipped"}, {}, {}, {}))
            eng_ver = {ARM_DATA: DD.VERSION, ARM_MARKET: MD.VERSION, ARM_HYBRID: HD.VERSION}[arm]
            dist_ver = {ARM_DATA: "lattice-1.0.0", ARM_MARKET: "lattice-1.0.0", ARM_HYBRID: "lattice-1.0.0"}[arm]
            if ans.get("p_yes") is not None:
                ans["validated"] = False                                  # every player arm is shadow / research
            st, reason, p, cv = support_state(qq, entry, pregame=pregame, confirmed=base["market_confirmed"], answer=ans,
                                              generated_before_kickoff=gen_before, allow_historical=a.allow_historical)
            gsis = lineage.get("gsis_id")
            pkey = (gsis or q.get("player_kalshi_id"), gid)
            if pkey not in player_ctx_cache:
                fr = player.feat.get((gsis, gid), {}) if (player and gsis) else {}
                avail = player.avail.get(gsis) if (player and gsis and player.avail) else None
                full = CX.player_context(ctx, gsis=gsis, team=(fr.get("team") or q.get("team")), week=base.get("week"), game_id=gid, kickoff=ko,
                                         feat_row=fr, avail=avail, position=(player.positions.get(gsis) if (player and gsis) else None))
                player_ctx_cache[pkey] = (context_id(full), full)
            pc_id, full = player_ctx_cache[pkey]
            base["player_context"] = CX.compact_player_context(full, pc_id)
            base["flags"] = QU.status_flags(support_state=st, semantic_confidence=qq.semantic_confidence, identity_confidence=lineage.get("identity_confidence"),
                                            subject_kind="player", settlement_support=(entry.settlement if entry else None), engine=Q.PLAYER)
            rec = R.ProjectionRecord(record_id="", model_arm=arm, engine=Q.PLAYER, engine_version=eng_ver, distribution_version=dist_ver,
                                     model_version=MODEL_VERSION, p_yes=p, contract_value=cv, support_state=st, support_reason=reason,
                                     identity_confidence=lineage.get("identity_confidence"), projection_lineage=lineage, feature_lineage=feat,
                                     distribution_summary=dsum, data_quality={"catalog_support": (entry.model_support if entry else None),
                                                                              "availability_sources": (player.availability_sources if player else None)},
                                     p_yes_low=ans.get("p_low"), p_yes_high=ans.get("p_high"), **{**base, "subject_id": lineage.get("gsis_id") or base["subject_id"]})
            rec.record_id = R.record_id(snapshot_id, t, arm, eng_ver, dist_ver)
            arm_rows[arm].append(rec.finalize().to_dict())

    # ---- coherence audit (model-free, on the same snapshot)
    audit = CE.audit_board(coherence_rows, {t: qq for t, qq in qs.items()}, fee_sched, run_ts)
    log(f"coherence: {audit['n_groups']} groups, {audit['by_kind']}, incoherence >2c {audit['n_abs_incoherence_gt_2c']}, executable {audit['n_executable_opportunities']}")

    # ---- write (append-only; conflict = fail closed)
    store = ProjectionStore(store_root)
    written = {}
    perf = {"seconds": time.time() - t0, "max_rss_mb": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, "api_calls": 0}
    extra = {"model_version": MODEL_VERSION, "capture_manifest": man.get("run_id"), "discovery": os.path.basename(ddir) if ddir else None,
             "horizon_id": horizon_id, "generated_at": gen_iso, "n_sims": a.n_sims, "perf": perf}
    try:
        for arm, rows in [(ARM_BOARD, board_rows)] + list(arm_rows.items()):
            if not rows:
                continue
            res = store.write(snapshot_id, arm, rows, manifest_extra=extra)
            written[arm] = {"status": res.get("status"), "path": store.path(snapshot_id, arm), "n": len(rows), "sha256": res.get("sha256")}
            log(f"  {arm}: {res.get('status')} {len(rows)} rows -> {store.path(snapshot_id, arm)}")
        side = write_sidecar(store_root, snapshot_id, {"snapshot_id": snapshot_id, "lineage_id": lineage_id, "lineage": lineage,
                                                        "game_contexts": {cid: full for (cid, full) in game_ctx_cache.values()},
                                                        "player_contexts": {cid: full for (cid, full) in player_ctx_cache.values()}})
        written["CONTEXT_SIDECAR"] = {"status": side.get("status"), "path": side.get("path"), "n": len(game_ctx_cache) + len(player_ctx_cache), "sha256": side.get("sha256")}
        log(f"  context sidecar: {side.get('status')} {len(game_ctx_cache)} game + {len(player_ctx_cache)} player contexts -> {side.get('path')}")
    except ProjectionConflict as e:
        log(f"::error::projection conflict: {e}"); return 4
    if horizon_id and written:
        markers = HZ.write_markers(a.out, [horizon_id], snapshot_id=snapshot_id, status="CAPTURED", now=now)
        log(f"horizon markers: {markers}")
    # ---- summary
    all_rows = board_rows + [r for rs in arm_rows.values() for r in rs]
    summ = {"snapshot_id": snapshot_id, "generated_at": gen_iso, "now_override": bool(a.now), "horizon_id": horizon_id, "n_quotes": len(quotes),
            "n_records": len(all_rows), "by_arm_state": {arm: dict(Counter(r["support_state"] for r in rows)) for arm, rows in [(ARM_BOARD, board_rows)] + list(arm_rows.items())},
            "by_engine_state": _nested(all_rows, "engine", "support_state"), "by_family_state": _nested(board_rows, "market_family", "support_state"),
            "by_stat_arm_state": {arm: _nested(rows, "stat_family", "support_state") for arm, rows in arm_rows.items()},
            "game_envs": {g: {k: v for k, v in e.items() if k in ("spread", "total", "source", "gap")} for g, e in envs.items()},
            "coherence": {k: v for k, v in audit.items() if k != "groups"}, "written": written, "perf": perf,
            "flags": {"has_probability": sum(1 for r in all_rows if (r.get("flags") or {}).get("has_probability")),
                      "has_probability_and_settleable": sum(1 for r in all_rows if (r.get("flags") or {}).get("has_probability") and (r.get("flags") or {}).get("settlement_supported")),
                      "betting_authorized": 0, "execution_supported": 0, "prospectively_validated": 0},
            "settlement_matrix": settlement_matrix(all_rows), "context_coverage": context_coverage(all_rows),
            "horizon_quality": dict(Counter((r.get("horizon_quality") or {}).get("horizon_quality") for r in all_rows)), "snapshot_reused": reused, "lineage": lineage,
            "artifact_bytes": sum(os.path.getsize(w["path"]) for w in written.values() if w.get("path") and os.path.exists(w["path"]))}
    sd = a.summary_dir or os.path.join(a.out, "shadow", "v2", "runs")
    os.makedirs(sd, exist_ok=True)
    json.dump(summ, open(os.path.join(sd, f"{snapshot_id}.summary.json"), "w"), indent=1, default=str)
    json.dump(audit, open(os.path.join(sd, f"{snapshot_id}.coherence.json"), "w"), indent=1, default=str)
    open(os.path.join(sd, f"{snapshot_id}.SUMMARY.md"), "w").write(render_summary(summ))
    log(f"done in {perf['seconds']:.0f}s, rss {perf['max_rss_mb']:.0f} MB, {len(all_rows)} records")
    return 0


def snapshot_reused(roots, snapshot_id: str) -> bool:
    """True when an existing horizon marker (local staging or market-data) already names this capture snapshot."""
    import glob as _g
    for root in roots:
        for p in _g.glob(os.path.join(root, HZ.MARKER_DIR, "*.json")):
            try:
                if json.load(open(p)).get("snapshot_id") == snapshot_id:
                    return True
            except (OSError, ValueError):
                continue
    return False


def settlement_matrix(rows: list) -> list:
    """Per family x period: HAS_PROBABILITY / SETTLEABLE / HISTORICALLY_VALIDATED / BETTABLE are different questions."""
    by = defaultdict(lambda: {"n": 0, "has_probability": 0, "settleable": 0, "historically_validated": 0, "bettable": 0, "engines": set(), "settlement_source": None, "settlement_version": None})
    for r in rows:
        e = CAT.catalog_entry(r.get("market_family"), r.get("period"), r.get("stat_family"))
        k = f"{r.get('market_family')}|{r.get('period')}" + (f"|{r.get('stat_family')}" if r.get("market_family") == "PLAYER_STAT" else "")
        d = by[k]; f = r.get("flags") or {}
        d["n"] += 1; d["has_probability"] += int(bool(f.get("has_probability"))); d["settleable"] += int(bool(f.get("settlement_supported")) and bool(f.get("has_probability")))
        d["historically_validated"] += int(bool(f.get("historically_validated"))); d["engines"].add(r.get("engine"))
        if e:
            d["settlement_source"] = e.settlement_source; d["settlement_version"] = e.settlement_rule_version; d["settlement"] = e.settlement; d["limitations"] = e.reason
    out = []
    for k, d in sorted(by.items()):
        d["engines"] = sorted(x for x in d["engines"] if x); d["family_period"] = k
        d["probability_without_settlement"] = d["has_probability"] - d["settleable"]
        out.append(d)
    return out


def context_coverage(rows: list) -> dict:
    """How much point-in-time context the records actually carry (KNOWN vs UNKNOWN), by block."""
    pl_rows = [r for r in rows if r.get("engine") == "PLAYER" and r.get("p_yes") is not None]
    def frac(pred, rs):
        return (round(100.0 * sum(1 for r in rs if pred(r)) / len(rs), 1) if rs else None)
    pc = lambda r: r.get("player_context") or {}  # noqa: E731
    return {"n_player_probability_rows": len(pl_rows),
            "injury_report_known_pct": frac(lambda r: (pc(r).get("injury_report") or {}).get("state") in ("LISTED", "NOT_LISTED"), pl_rows),
            "depth_chart_known_pct": frac(lambda r: (pc(r).get("depth_chart") or {}).get("state") in ("LISTED", "NOT_LISTED"), pl_rows),
            "availability_known_pct": frac(lambda r: (pc(r).get("availability") or {}).get("state") not in (None, "UNKNOWN"), pl_rows),
            "weather_known_pct": frac(lambda r: (pc(r).get("weather") or {}).get("state") == "KNOWN", pl_rows),
            "team_volume_known_pct": frac(lambda r: (pc(r).get("team_volume_estimates") or {}).get("pass_attempts") is not None, pl_rows),
            "last_trade_known_pct": frac(lambda r: (r.get("market_state") or {}).get("last_trade_at") not in (None, "UNKNOWN"), rows),
            "ladder_state_pct": frac(lambda r: "ladder" in (r.get("market_state") or {}), pl_rows)}


def _nested(rows, k1, k2):
    out = defaultdict(Counter)
    for r in rows:
        out[str(r.get(k1))][r.get(k2)] += 1
    return {k: dict(v) for k, v in out.items()}


def render_summary(s: dict) -> str:
    L = [f"# Shadow v2 run {s['snapshot_id']}", "", f"generated {s['generated_at']} horizon {s['horizon_id'] or 'CYCLE'}; {s['n_quotes']} quotes -> {s['n_records']} records; "
         f"{s['perf']['seconds']:.0f}s, {s['perf']['max_rss_mb']:.0f} MB RSS, {s['artifact_bytes']} bytes written", ""]
    L += ["## Support state by arm", "", "| arm | " + " | ".join(sorted({k for v in s["by_arm_state"].values() for k in v})) + " |"]
    keys = sorted({k for v in s["by_arm_state"].values() for k in v})
    L.append("|---|" + "---|" * len(keys))
    for arm, c in s["by_arm_state"].items():
        L.append(f"| {arm} | " + " | ".join(str(c.get(k, 0)) for k in keys) + " |")
    L += ["", "## Game environments", "", "| game | spread | total | source | 1H margin gap | full margin gap |", "|---|---|---|---|---|---|"]
    for g, e in s["game_envs"].items():
        gap = e.get("gap") or {}
        L.append(f"| {g} | {e['spread']} | {e['total']} | {e['source']} | {gap.get('mean_1h_margin_gap', '-')} | {gap.get('mean_full_margin_gap', '-')} |")
    c = s["coherence"]
    L += ["", "## Coherence audit", "", f"groups {c['n_groups']}: {c['by_kind']}; collectively exhaustive {c['n_collectively_exhaustive']}; "
          f"|sum(mid)-1| > 2c: {c['n_abs_incoherence_gt_2c']}, > 5c: {c['n_abs_incoherence_gt_5c']}; executable opportunities after fees: {c['n_executable_opportunities']}", ""]
    L += ["## Family x state (board arm)", ""]
    for fam, st in sorted(s["by_family_state"].items()):
        L.append(f"- {fam}: " + ", ".join(f"{k} {v}" for k, v in sorted(st.items())))
    return "\n".join(L) + "\n"


# ------------------------------------------------------------------------------------------------- player arms
class PlayerArms:
    def __init__(self):
        self.data = {}          # (gsis, gid, stat) -> LatticeDistribution
        self.feat = {}          # (gsis, gid) -> feature row dict
        self.market = {}        # (kalshi_id, gid, stat) -> market record
        self.identity = {}      # kalshi id -> (gsis or None, confidence)
        self.avail = None
        self.availability_sources = []
        self.bundle = None
        self.qb = {}
        self.positions = {}

    def answer(self, arm, t, q, qq):
        kid, gid, stat = q.get("player_kalshi_id"), q.get("game_id"), q.get("stat")
        gsis, conf = self.identity.get(kid, (None, "UNRESOLVED"))
        lineage = {"identity_confidence": conf, "gsis_id": gsis, "kalshi_player_id": kid, "engine_stat": ENGINE_STATS.get(stat)}
        if conf == "NOT_A_PLAYER":
            return {"p_yes": None, "reason": "team D/ST or non-player leg", "status": "DATA_UNAVAILABLE"}, lineage, {}, {}
        if qq.kind != Q.THRESHOLD or qq.k is None:
            return {"p_yes": None, "reason": f"player question is not an integer threshold ({qq.kind})"}, lineage, {}, {}
        k = float(qq.k)
        if qq.op == ">":
            k = float(np.floor(k) + 1.0)
        av = self.avail.get(gsis) if (self.avail and gsis) else None
        p_plays, p_nosnap = (av.p_plays, av.p_active_no_snap) if av else rates_for(UNKNOWN)
        feat = {"p_plays": p_plays, "p_active_no_snap": p_nosnap, "availability_state": (av.state if av else UNKNOWN)}
        mid = None
        yb, ya = fnum(q.get("yes_bid_dollars")), fnum(q.get("yes_ask_dollars"))
        if yb is not None and ya is not None:
            mid = (yb + ya) / 2.0
        mk = self.market.get((kid, gid, stat))
        if arm == ARM_MARKET:
            if not mk or mk.get("identification") in (None, MD.NONE, MD.UNDERIDENTIFIED):
                return {"p_yes": None, "reason": f"market ladder {(mk or {}).get('identification') or 'absent'}: {(mk or {}).get('reason') or 'too few two-sided rungs'}"}, lineage, feat, {}
            d = mk["_dist"]
            p_ev = d.survival(k)
            b = MD.survival_bounds(mk, k)
            cv = sem_mod.player_prop_contract_value(p_ev, p_plays, p_nosnap, mid)
            lineage.update(identification=mk["identification"], n_rungs_used=mk["n_rungs_used"], dispersion_source=mk.get("dispersion_source"))
            return {"p_yes": p_ev, "contract_value": cv.contract_value, "p_low": b.get("bid_survival"), "p_high": b.get("ask_survival")}, lineage, feat, {**d.summary(), "family": mk.get("family"), "on_ladder": b.get("on_ladder")}
        if gsis is None:
            return {"p_yes": None, "reason": "Kalshi player id not resolved to a GSIS id", "status": "IDENTITY_UNRESOLVED"}, lineage, feat, {}
        est = ENGINE_STATS.get(stat)
        d = self.data.get((gsis, gid, est)) if est else None
        if d is None:
            return {"p_yes": None, "reason": (f"no data distribution for statistic {stat!r}" if est else f"statistic {stat!r} has no data model"), "status": "DATA_UNAVAILABLE"}, lineage, feat, {}
        fr = self.feat.get((gsis, gid), {})
        feat.update(team=fr.get("team"), projected_team_volume=fr.get(VOLUME_FEATURE.get(est) or ""), projected_share=fr.get(SHARE_FEATURE.get(est) or ""),
                    projected_snap_share=fr.get("ewma_snap_share"), projected_qb_id=self.qb.get((gid, fr.get("team"))), n_prior=fr.get("n_prior"),
                    shrink_w=fr.get("shrink_w"), qb_changed_recent=fr.get("qb_changed_recent"))
        if arm == ARM_DATA:
            dist = d
            lineage.update(family=d.meta.get("family"), feature_set=d.meta.get("feature_set"), bundle_sha=(self.bundle.artifact_sha if self.bundle else None))
        else:
            h = HD.hybrid(d, (mk or {}).get("_dist"), market_identification=(mk or {}).get("identification"))
            if h["status"] != "OK":
                return {"p_yes": None, "reason": f"hybrid unavailable: {h['reason']}"}, lineage, feat, {}
            dist = h["dist"]
            lineage.update(structure=h["structure"], w_market=h["w_market"], study_verdict=HD.STUDY_VERDICT)
        p_ev = dist.survival(k)
        cv = sem_mod.player_prop_contract_value(p_ev, p_plays, p_nosnap, mid)
        s = dist.summary()
        s.update(mu=dist.meta.get("mu"), mu_opp=dist.meta.get("mu_opp"), eff=dist.meta.get("eff"),
                 quantiles={"p025": dist.quantile(0.025), "p05": s["p05"], "p25": s["p25"], "p50": s["p50"], "p75": s["p75"], "p95": s["p95"], "p975": dist.quantile(0.975)})
        return {"p_yes": p_ev, "contract_value": cv.contract_value}, lineage, feat, s


def build_player_arms(a, quotes, qs, sched, gidx, run_ts, now) -> PlayerArms:
    P = PlayerArms()
    pmap = pl.read_parquet(os.path.join(ROOT, "data/silver/kalshi_player_map.parquet"))
    for r in pmap.iter_rows(named=True):
        st = r.get("status")
        if st == "NOT_A_PLAYER":
            P.identity[r["kalshi_player_id"]] = (None, "NOT_A_PLAYER")
        elif r.get("gsis_id") and st in ("RESOLVED", "RESOLVED_PLAYERS_TABLE"):
            P.identity[r["kalshi_player_id"]] = (r["gsis_id"], "RESOLVED")
        elif r.get("gsis_id") and st in ("RESOLVED_TEAM_UNCONFIRMED", "RESOLVED_JERSEY_MISMATCH"):
            P.identity[r["kalshi_player_id"]] = (r["gsis_id"], "RESOLVED_UNCONFIRMED")
    player_map = {k: v[0] for k, v in P.identity.items() if v[0]}
    players_tbl = pl.read_parquet(os.path.join(ROOT, "data/raw/nflverse/players/players.parquet")).select("gsis_id", "position")
    positions = dict(zip(players_tbl["gsis_id"].to_list(), players_tbl["position"].to_list()))
    P.positions = positions
    # availability from context captures when present (none locally -> UNKNOWN, recorded as such)
    ctx_root = os.path.join(a.market_data, "data", "context")
    P.avail = AvailabilityBook(run_ts, max_staleness_minutes=600.0)
    xw_path = os.path.join(ROOT, "data/silver/player_crosswalk.parquet")
    if os.path.isdir(ctx_root) and os.path.exists(xw_path):
        import glob as _g
        xw = pl.read_parquet(xw_path)
        sl = {str(s): g for s, g in zip(xw["sleeper_id"].to_list(), xw["gsis_id"].to_list()) if s}
        es = {str(s): g for s, g in zip(xw["espn_id"].to_list(), xw["gsis_id"].to_list()) if s}
        for pat, loader, m in ((f"{ctx_root}/*/*.sleeper.json", P.avail.load_sleeper, sl), (f"{ctx_root}/*/*.espn_injuries.json", P.avail.load_espn, es)):
            fs = sorted(_g.glob(pat))
            if fs:
                loader(fs[-1], m); P.availability_sources.append(os.path.basename(fs[-1]))
    P.avail.finalize()
    # market ladders per (player, game, stat)
    ladders = defaultdict(list)
    for t, q in quotes.items():
        if q.get("family") == "PLAYER_STAT" and q.get("player_kalshi_id") and q.get("game_id") and q.get("threshold") is not None:
            ladders[(q["player_kalshi_id"], q["game_id"], q["stat"])].append({"threshold": q["threshold"], "yes_bid": fnum(q.get("yes_bid_dollars")),
                                                                                "yes_ask": fnum(q.get("yes_ask_dollars")), "volume": fnum(q.get("volume_fp"))})
    for key, lad in ladders.items():
        P.market[key] = MD.market_distribution(ENGINE_STATS.get(key[2], key[2]), lad)
    log(f"market ladders: {len(P.market)}; identification {Counter(m.get('identification') for m in P.market.values())}")
    # data arm: prospective rows + v2 features + walk-forward bundle
    hist = pdist.load_player_games(ROOT, range(2013, a.target_season))
    cfg = json.load(open(os.path.join(ROOT, "research/player_distributions/results.json")))["config"]
    priors = pdist.position_priors(hist, range(2013, 2016))
    qb_ids = {}
    for gid, row in gidx.iterrows():
        for c, side in (("home_qb_id", "home_team"), ("away_qb_id", "away_team")):
            v = row.get(c)
            if isinstance(v, str) and v:
                qb_ids.setdefault(gid, set()).add(v); P.qb[(gid, row[side])] = v
    prows = [q for q in quotes.values() if q.get("family") == "PLAYER_STAT" and q.get("player_kalshi_id") and q.get("game_id") in gidx.index]
    upcoming = upcoming_from_markets(prows, player_map, sched, a.target_season, positions, qb_ids)
    log(f"prospective player-game rows: {len(upcoming)}")
    if not len(upcoming):
        return P
    combined = build_prospective_rows(hist, upcoming)
    combined = pdist.add_ewma_features(combined, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"], priors=priors)
    combined = add_v2_features(combined, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"])
    combined = DD.ensure_columns(combined)
    feat = combined[combined.is_prospective == True].reset_index(drop=True)   # noqa: E712
    histf = combined[combined.is_prospective != True]                          # noqa: E712
    stats_needed = sorted({ENGINE_STATS[k[2]] for k in ladders if k[2] in ENGINE_STATS})
    P.bundle = DD.fit_bundle(histf, a.target_season, feature_set="v2", stats=stats_needed, verbose=log)
    keep = [c for c in feat.columns if c.startswith("ewma_") or c.startswith("share_recent") or c in
            ("team", "position", "opponent_team", "home", "implied_total", "spread_team", "qb_changed_recent", "n_prior", "shrink_w", "w_eff", "qb_starter")]
    for i, r in feat.iterrows():
        row = {c: r[c] for c in keep}
        row["_schedule_qb"] = P.qb.get((r["game_id"], r["team"]))
        P.feat[(r["player_id"], r["game_id"])] = row
    for stat, model in P.bundle.models.items():
        pm = pdist.population_mask(feat, model.spec.pop)
        rows = feat[pm]
        if not len(rows):
            continue
        dists = model.distributions(rows)
        for (pid, gid), d in zip(zip(rows.player_id, rows.game_id), dists):
            P.data[(pid, gid, stat)] = d
    log(f"data distributions: {len(P.data)} (bundle {P.bundle.artifact_sha})")
    return P


if __name__ == "__main__":
    sys.exit(main())
