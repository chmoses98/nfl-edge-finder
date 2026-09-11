#!/usr/bin/env python3
"""THE central question, tested on real Kalshi prices: do walk-forward model probabilities carry information
the Kalshi pre-start price does not?

Data: discovery phase-2 60-minute candles for settled MATCH_WINNER markets (July-Sept 2026), the market
records (rules, scheduled start, exchange result), the canonical match table (Sackmann ids) and the
walk-forward Elo predictions (research/elo_study/predictions_<tour>.parquet; ratings use only earlier matches).

Kalshi 'pre-start quote' = yes_bid/yes_ask close of the last hourly candle that ENDS at or before the
scheduled start (occurrence_datetime) minus 5 minutes -- an hourly proxy for the canonical close (no first-ball
truth; a delayed match may have traded further after this point, which only makes the market LESS informed
than its true close, i.e. this test is generous to the model). Requires a two-sided quote with spread <= 0.15
and positive open interest by that time.

Outputs research/kalshi_backtest/RESULTS.md + linked parquet.
"""
from __future__ import annotations
import glob, json, os, sys, re
from collections import defaultdict
from datetime import datetime, timezone, date, timedelta
import numpy as np, pandas as pd
HERE = os.path.dirname(os.path.abspath(__file__)); PROJ = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, PROJ)
from tennis_edge.kalshi.markets import parse_market
from tennis_edge.kalshi.families import SERIES
from tennis_edge.identity.kalshi_map import KalshiPlayerMapper
from tennis_edge.models.state import load_state
from tennis_edge.eval.metrics import summary, bootstrap_diff, reliability_table
from tennis_edge.pricing.fees import taker_fee, FeeSchedule
from tennis_edge.health.gates import _latest_discovery

MATCH_SERIES = [tk for tk, (fam, tour, lvl, disc) in SERIES.items() if fam == "MATCH_WINNER" and disc == "singles" and tour in ("ATP", "WTA")]


def ts(s):
    return int(datetime.fromisoformat(s.replace("Z", "+00:00")).timestamp()) if s else None


def prestart_quote(candles, cutoff_ts):
    best = None
    for c in candles:
        if c.get("end_period_ts", 0) <= cutoff_ts:
            best = c
    if not best:
        return None
    try:
        bid = float(best["yes_bid"]["close_dollars"]); ask = float(best["yes_ask"]["close_dollars"]); oi = float(best.get("open_interest_fp") or 0)
    except (KeyError, TypeError, ValueError):
        return None
    if not (0 < bid <= ask < 1) or ask - bid > 0.15 or oi <= 0:
        return None
    return {"bid": bid, "ask": ask, "mid": 0.5 * (bid + ask), "oi": oi, "candle_end_ts": best["end_period_ts"], "hours_before_start": (cutoff_ts - best["end_period_ts"]) / 3600}


def main():
    d = _latest_discovery()
    states = {t: load_state(os.path.join(PROJ, "data", "processed", f"ratings_{t}.json")) for t in ("ATP", "WTA")}
    mapper = KalshiPlayerMapper(states, cache_path=os.path.join(PROJ, "data", "research", "kalshi_backtest_map_cache.json"))
    # market records by ticker (settled + historical)
    recs = {}
    for tk in MATCH_SERIES:
        for path in (os.path.join(d, "markets", f"{tk}.json"), os.path.join(d, "historical_markets", f"{tk}.json")):
            if not os.path.exists(path):
                continue
            obj = json.load(open(path))
            blocks = obj.values() if "markets" not in obj else [obj]
            for blk in blocks:
                for m in blk.get("markets") or []:
                    recs[m["ticker"]] = m
    # group by event, keep markets that have candles
    by_event = defaultdict(list)
    for tk in MATCH_SERIES:
        for f in glob.glob(os.path.join(d, "candles", tk, "*.json")):
            t = os.path.basename(f)[:-5]
            if t in recs:
                by_event[recs[t]["event_ticker"]].append((t, f))
    matches = pd.read_parquet(os.path.join(PROJ, "data", "processed", "matches.parquet"), columns=["match_key", "tour", "tourney_date", "winner_id", "loser_id", "level_canonical", "id_system", "outcome_type"])
    matches = matches[matches.id_system == "sackmann"]
    matches["tourney_date"] = pd.to_datetime(matches["tourney_date"])
    pair_idx = defaultdict(list)
    for r in matches[matches.tourney_date >= "2026-05-01"].itertuples(index=False):
        pair_idx[frozenset((r.winner_id, r.loser_id))].append(r)
    preds = {}
    for t in ("ATP", "WTA"):
        p = os.path.join(PROJ, "research", "elo_study", f"predictions_{t}.parquet")
        if os.path.exists(p):
            preds[t] = pd.read_parquet(p).set_index("match_key")
    rows = []; stats = defaultdict(int)
    for ev, lst in by_event.items():
        stats["events"] += 1
        pms = [(parse_market(recs[t]), recs[t], f) for t, f in lst]
        pms = [x for x in pms if x[0].status == "PARSED"]
        if len(pms) != 2:
            stats["not_two_parsed_sides"] += 1; continue
        names = {}; sides = {}
        for pm, m, f in pms:
            names[pm.subject_is_a] = pm.subject; sides[pm.subject_is_a] = (pm, m, f)
        if True not in names or False not in names:
            stats["missing_side"] += 1; continue
        pm_a, m_a, f_a = sides[True]
        tour = "WTA" if pm_a.series_ticker.startswith(("KXWTA", "KXITFW")) else "ATP"
        if pm_a.series_ticker == "KXITFWMATCH":
            tour = "WTA"
        res_a = m_a.get("result")
        if res_a not in ("yes", "no"):
            stats["non_binary_settlement"] += 1; continue
        ma, mb = mapper.resolve(tour, names[True], pm_a.competitor_id, date(2026, 9, 11)), mapper.resolve(tour, names[False], sides[False][0].competitor_id, date(2026, 9, 11))
        if ma["status"] != "MAPPED" or mb["status"] != "MAPPED":
            stats["unmapped"] += 1; continue
        sched = ts(m_a.get("occurrence_datetime") or m_a.get("expected_expiration_time"))
        if not sched:
            stats["no_schedule"] += 1; continue
        body = json.load(open(f_a))
        c60 = body.get("candles_60")
        cands = (c60[0] if isinstance(c60, list) else c60) or {}
        candles = cands.get("candlesticks") or []
        q = prestart_quote(candles, sched - 300)
        if not q:
            stats["no_prestart_quote"] += 1; continue
        # canonical match: same pair, tournament started within 20 days before the scheduled date
        kd = datetime.fromtimestamp(sched, tz=timezone.utc)
        cands_m = [r for r in pair_idx.get(frozenset((ma["player_id"], mb["player_id"])), []) if (kd.date() - r.tourney_date.date()).days in range(-1, 21)]
        if not cands_m:
            stats["no_canonical_match"] += 1; continue
        if len(cands_m) > 1:
            cands_m.sort(key=lambda r: abs((kd.date() - r.tourney_date.date()).days))
        cm = cands_m[0]
        if cm.outcome_type == "WALKOVER":
            stats["walkover"] += 1; continue
        y_a = 1.0 if res_a == "yes" else 0.0
        # sports truth cross-check: exchange winner == canonical winner?
        sports_a_won = cm.winner_id == ma["player_id"]
        if bool(sports_a_won) != bool(y_a == 1.0):
            stats["exchange_vs_sports_conflict"] += 1; continue
        pr = preds.get(tour)
        if pr is None or cm.match_key not in pr.index:
            stats["no_walkforward_prediction"] += 1; continue
        prow = pr.loc[cm.match_key]
        # p_winner columns are P(actual winner); orient to side A
        def orient(col):
            v = float(prow[col]); return v if sports_a_won else 1 - v
        rows.append({"event": ev, "tour": tour, "series": pm_a.series_ticker, "level": cm.level_canonical, "match_key": cm.match_key, "y_a": y_a,
                     "kalshi_bid": q["bid"], "kalshi_ask": q["ask"], "kalshi_mid": q["mid"], "kalshi_oi": q["oi"], "hours_before_start": q["hours_before_start"],
                     "p_elo_plain": orient("p_elo_plain"), "p_elo_levelprior": orient("p_elo_levelprior"), "p_elo_surface_k_lo": orient("p_elo_surface_k_lo"),
                     "p_elo_surface_levelk": orient("p_elo_surface_levelk"), "n_min": float(prow["n_min_elo_plain"]), "sched": kd.isoformat()})
        stats["linked"] += 1
    df = pd.DataFrame(rows)
    os.makedirs(os.path.join(PROJ, "research", "kalshi_backtest"), exist_ok=True)
    df.to_parquet(os.path.join(PROJ, "research", "kalshi_backtest", "linked.parquet"), index=False)
    L = ["# Model vs KALSHI pre-start price (settled match-winner markets, Jul-Sep 2026)", "", f"Funnel: {dict(stats)}", "",
         "Kalshi quote = last hourly candle ending >= 5 min before scheduled start, two-sided, spread <= 15c, OI > 0. Model = walk-forward Elo (ratings from matches strictly before each match). Orientation: side A of the event; symmetric by construction (both sides listed).", ""]
    if len(df) == 0:
        L.append("No linked rows.")
    else:
        rng = np.random.default_rng(0); flip = rng.random(len(df)) < 0.5
        y = np.where(flip, 1 - df.y_a, df.y_a)
        def o(col):
            v = df[col].to_numpy(float); return np.where(flip, 1 - v, v)
        mkt = o("kalshi_mid")
        L += [f"n = {len(df)}", "", "| forecaster | brier | log_loss | accuracy | ECE | cal_slope | boot Brier diff vs Kalshi mid [95% CI] |", "|---|---|---|---|---|---|---|"]
        for name in ["kalshi_mid", "p_elo_plain", "p_elo_levelprior", "p_elo_surface_k_lo", "p_elo_surface_levelk"]:
            p = o(name); s = summary(y, p); b = bootstrap_diff(y, p, mkt, n_boot=500)
            L.append(f"| {name} | {s['brier']:.4f} | {s['log_loss']:.4f} | {s['accuracy']:.4f} | {s['ece']:.4f} | {s['cal_slope']:.3f} | {b['diff']:+.5f} [{b['ci_low']:+.5f}, {b['ci_high']:+.5f}] |")
        # by series/level
        L += ["", "## By series (log-loss)", "", "| series | n | Kalshi | elo_plain | elo_surface_k_lo |", "|---|---|---|---|---|"]
        for sname, g in df.groupby("series").groups.items():
            idx = np.zeros(len(df), bool); idx[np.asarray(list(g))] = True
            if idx.sum() < 50:
                continue
            L.append(f"| {sname} | {int(idx.sum())} | {summary(y[idx], mkt[idx])['log_loss']:.4f} | {summary(y[idx], o('p_elo_plain')[idx])['log_loss']:.4f} | {summary(y[idx], o('p_elo_surface_k_lo')[idx])['log_loss']:.4f} |")
        # disagreement buckets + hypothetical execution at the ASK with taker fees
        model = o("p_elo_plain"); dlt = model - mkt; ad = np.abs(dlt)
        bid = o("kalshi_bid") if False else None
        # executable: buying the model-favoured side at its ask
        yes_ask = df.kalshi_ask.to_numpy(float); yes_bid = df.kalshi_bid.to_numpy(float)
        ask_a = np.where(flip, 1 - yes_bid, yes_ask)   # ask for side 'A after flip' = 1 - bid of the other side
        ask_b = np.where(flip, yes_ask, 1 - yes_bid)
        L += ["", "## Disagreement buckets |elo_plain - Kalshi mid| (buy model-favoured side at its ASK, taker fee)", "",
              "| bucket | n | model brier | Kalshi brier | model-side win% | avg ask paid | net ROI per $1 after fees |", "|---|---|---|---|---|---|---|"]
        edges = [0, 0.025, 0.05, 0.10, 0.15, 0.20, 1.01]
        for lo, hi in zip(edges, edges[1:]):
            idx = (ad >= lo) & (ad < hi)
            if idx.sum() == 0:
                continue
            fav_a = dlt[idx] > 0
            won = np.where(fav_a, y[idx], 1 - y[idx]); price = np.where(fav_a, ask_a[idx], ask_b[idx])
            fee = np.array([taker_fee(p, 1.0) for p in price])
            pnl = won * 1.0 - price - fee
            L.append(f"| {lo:.3f}-{min(hi, 1):.3f} | {int(idx.sum())} | {np.mean((model[idx] - y[idx]) ** 2):.4f} | {np.mean((mkt[idx] - y[idx]) ** 2):.4f} | {won.mean():.3f} | {price.mean():.3f} | {pnl.sum() / price.sum():+.3f} |")
        L += ["", "## Reliability (Kalshi mid vs elo_plain)", "", "| bin | n | Kalshi mean p | obs | elo mean p | obs |", "|---|---|---|---|---|---|"]
        rk = reliability_table(y, mkt); rm = reliability_table(y, model)
        for a_, b_ in zip(rk, rm):
            L.append(f"| {a_['bin']} | {a_['n']} | {a_['mean_p'] if a_['mean_p'] is None else round(a_['mean_p'], 3)} | {a_['obs_rate'] if a_['obs_rate'] is None else round(a_['obs_rate'], 3)} | {b_['mean_p'] if b_['mean_p'] is None else round(b_['mean_p'], 3)} | {b_['obs_rate'] if b_['obs_rate'] is None else round(b_['obs_rate'], 3)} |")
        L += ["", f"Median hours between the quote candle and scheduled start: {df.hours_before_start.median():.1f}; median OI at quote: {df.kalshi_oi.median():.0f}"]
    open(os.path.join(PROJ, "research", "kalshi_backtest", "RESULTS.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
