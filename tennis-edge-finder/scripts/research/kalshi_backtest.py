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

PREGAME_HOURS = float(os.environ.get("PREGAME_HOURS", "7"))
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
    # Model probabilities come from the FROZEN production rating states (Sackmann fork ends 2026-06-01 ATP /
    # 2026-04-27 WTA): every rating predates every market here, so there is no leakage; the model is handicapped
    # by 1-4 months of staleness. Truth = exchange binary result (scalar/fair-price settlements excluded).
    from tennis_edge.pricing.competition import classify_competition, build_surface_lookup, lookup_surface
    from tennis_edge.models.elo import expected as elo_expected
    from tennis_edge.sim.analytic import match_win_prob, point_probs_from_match_prob
    from tennis_edge.rules.formats import resolve_format, FormatResolutionError, TOUR_SINGLES_BO3
    import math
    mtab = pd.read_parquet(os.path.join(PROJ, "data", "processed", "matches.parquet"), columns=["tourney_name", "surface", "season"])
    surf_lookup = build_surface_lookup(mtab)

    def surface_rating(rec, surface, w_max=0.5, n_half=20.0):
        r = rec["elo"]
        if surface and surface in rec.get("surfaces", {}):
            rs, ns = rec["surfaces"][surface]; w = w_max * ns / (ns + n_half); return (1 - w) * r + w * rs
        return r
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
        info = classify_competition(pm_a.competition, pm_a.tour)
        tour = info["tour"] if info["tour"] in ("ATP", "WTA") else ("WTA" if pm_a.series_ticker.startswith(("KXWTA", "KXITFW")) else "ATP")
        res_a = m_a.get("result")
        if res_a not in ("yes", "no"):
            stats["non_binary_settlement"] += 1; continue
        ma, mb = mapper.resolve(tour, names[True], pm_a.competitor_id, date(2026, 9, 11)), mapper.resolve(tour, names[False], sides[False][0].competitor_id, date(2026, 9, 11))
        if ma["status"] != "MAPPED" or mb["status"] != "MAPPED":
            stats["unmapped"] += 1; continue
        sched = ts(m_a.get("occurrence_datetime") or m_a.get("expected_expiration_time"))
        close_t = ts(m_a.get("close_time"))
        if not sched or not close_t:
            stats["no_schedule"] += 1; continue
        # occurrence_datetime is NOT a start time for ITF/Challenger series (it is a nominal session time that
        # usually falls AFTER close_time). Conservative pregame cutoff: at least PREGAME_HOURS before the market
        # closed (a match rarely lasts longer) AND before the nominal start.
        cutoff = min(sched - 300, close_t - PREGAME_HOURS * 3600)
        body = json.load(open(f_a))
        c60 = body.get("candles_60")
        cands = (c60[0] if isinstance(c60, list) else c60) or {}
        candles = cands.get("candlesticks") or []
        q = prestart_quote(candles, cutoff)
        if not q:
            stats["no_prestart_quote"] += 1; continue
        try:
            fmt = resolve_format(tour, info["level"], 2026, info["competition"] if info["level"] == "GRAND_SLAM" else None, "singles")
        except FormatResolutionError:
            stats["format_unresolved"] += 1; continue
        st = states[tour]; ra_rec, rb_rec = st["players"][ma["player_id"]], st["players"][mb["player_id"]]
        surface, _src = lookup_surface(pm_a.competition, info["surface_hint"], surf_lookup)
        ra, rb = surface_rating(ra_rec, surface), surface_rating(rb_rec, surface)
        p_elo_bo3 = elo_expected(ra, rb)
        spw = st["baselines"].get(f"{tour}|{surface}", None) or (0.64 if tour == "ATP" else 0.57)
        p_elo = match_win_prob(*point_probs_from_match_prob(p_elo_bo3, 2 * spw, TOUR_SINGLES_BO3), fmt)
        base = math.log(spw / (1 - spw))
        sr_pa = 1 / (1 + math.exp(-(base + ra_rec["sr_s"] - rb_rec["sr_r"]))); sr_pb = 1 - 1 / (1 + math.exp(-(base + rb_rec["sr_s"] - ra_rec["sr_r"])))
        p_sr = match_win_prob(sr_pa, sr_pb, fmt)
        sr_ok = min(ra_rec["sr_points"], rb_rec["sr_points"]) >= 1000
        z = 0.5 * math.log(p_elo / (1 - p_elo)) + 0.5 * math.log(p_sr / (1 - p_sr)); p_ens = 1 / (1 + math.exp(-z)) if sr_ok else p_elo
        kd = datetime.fromtimestamp(sched, tz=timezone.utc)
        rows.append({"event": ev, "tour": tour, "series": pm_a.series_ticker, "level": info["level"], "surface": surface, "y_a": 1.0 if res_a == "yes" else 0.0,
                     "kalshi_bid": q["bid"], "kalshi_ask": q["ask"], "kalshi_mid": q["mid"], "kalshi_oi": q["oi"], "hours_before_cutoff": q["hours_before_start"], "cutoff_hours_before_close": (close_t - cutoff) / 3600,
                     "p_elo": p_elo, "p_sr": p_sr, "p_ens": p_ens, "sr_ok": sr_ok, "n_min": min(ra_rec["n"], rb_rec["n"]),
                     "days_stale_a": (kd.date() - date.fromisoformat(ra_rec["last_date"][:10])).days if ra_rec.get("last_date") not in (None, "None") else None,
                     "sched": kd.isoformat()})
        stats["linked"] += 1
    df = pd.DataFrame(rows)
    os.makedirs(os.path.join(PROJ, "research", "kalshi_backtest"), exist_ok=True)
    df.to_parquet(os.path.join(PROJ, "research", "kalshi_backtest", "linked.parquet"), index=False)
    L = ["# Model vs KALSHI pre-start price (settled match-winner markets, Jul-Sep 2026)", "", f"Funnel: {dict(stats)}", "",
         f"Kalshi quote = last hourly candle ending before min(nominal start - 5 min, close_time - {PREGAME_HOURS:.0f} h) (occurrence_datetime is NOT a start time for ITF/Challenger: it usually falls after the close), two-sided, spread <= 15c, OI > 0. Model = production rating states FROZEN at the end of the Sackmann fork data (ATP 2026-06-01, WTA 2026-04-27), so ratings predate every market (no leakage) but are 1-4 months stale. Truth = exchange binary result. Orientation randomised.", ""]
    if len(df) == 0:
        L.append("No linked rows.")
    else:
        rng = np.random.default_rng(0); flip = rng.random(len(df)) < 0.5
        y = np.where(flip, 1 - df.y_a, df.y_a)
        def o(col):
            v = df[col].to_numpy(float); return np.where(flip, 1 - v, v)
        mkt = o("kalshi_mid")
        L += [f"n = {len(df)}", "", "| forecaster | brier | log_loss | accuracy | ECE | cal_slope | boot Brier diff vs Kalshi mid [95% CI] |", "|---|---|---|---|---|---|---|"]
        for name in ["kalshi_mid", "p_elo", "p_sr", "p_ens"]:
            p = o(name); s = summary(y, p); b = bootstrap_diff(y, p, mkt, n_boot=500)
            L.append(f"| {name} | {s['brier']:.4f} | {s['log_loss']:.4f} | {s['accuracy']:.4f} | {s['ece']:.4f} | {s['cal_slope']:.3f} | {b['diff']:+.5f} [{b['ci_low']:+.5f}, {b['ci_high']:+.5f}] |")
        # by series/level
        L += ["", "## By series (log-loss)", "", "| series | n | Kalshi | elo | ensemble |", "|---|---|---|---|---|"]
        for sname, g in df.groupby("series").groups.items():
            idx = np.zeros(len(df), bool); idx[np.asarray(list(g))] = True
            if idx.sum() < 50:
                continue
            L.append(f"| {sname} | {int(idx.sum())} | {summary(y[idx], mkt[idx])['log_loss']:.4f} | {summary(y[idx], o('p_elo')[idx])['log_loss']:.4f} | {summary(y[idx], o('p_ens')[idx])['log_loss']:.4f} |")
        # disagreement buckets + hypothetical execution at the ASK with taker fees
        model = o("p_ens"); dlt = model - mkt; ad = np.abs(dlt)
        bid = o("kalshi_bid") if False else None
        # executable: buying the model-favoured side at its ask
        yes_ask = df.kalshi_ask.to_numpy(float); yes_bid = df.kalshi_bid.to_numpy(float)
        ask_a = np.where(flip, 1 - yes_bid, yes_ask)   # ask for side 'A after flip' = 1 - bid of the other side
        ask_b = np.where(flip, yes_ask, 1 - yes_bid)
        L += ["", "## Disagreement buckets |ensemble - Kalshi mid| (buy model-favoured side at its ASK, taker fee)", "",
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
        L += ["", "## Reliability (Kalshi mid vs ensemble)", "", "| bin | n | Kalshi mean p | obs | elo mean p | obs |", "|---|---|---|---|---|---|"]
        rk = reliability_table(y, mkt); rm = reliability_table(y, model)
        for a_, b_ in zip(rk, rm):
            L.append(f"| {a_['bin']} | {a_['n']} | {a_['mean_p'] if a_['mean_p'] is None else round(a_['mean_p'], 3)} | {a_['obs_rate'] if a_['obs_rate'] is None else round(a_['obs_rate'], 3)} | {b_['mean_p'] if b_['mean_p'] is None else round(b_['mean_p'], 3)} | {b_['obs_rate'] if b_['obs_rate'] is None else round(b_['obs_rate'], 3)} |")
        L += ["", f"Median hours between the quote candle and the cutoff: {df.hours_before_cutoff.median():.1f}; median hours between cutoff and market close: {df.cutoff_hours_before_close.median():.1f}; median OI at quote: {df.kalshi_oi.median():.0f}"]
    open(os.path.join(PROJ, "research", "kalshi_backtest", "RESULTS.md"), "w").write("\n".join(L) + "\n")
    print("\n".join(L))


if __name__ == "__main__":
    main()
