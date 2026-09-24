#!/usr/bin/env python3
"""Player Engine v4: does a structural snap -> volume -> allocation -> outcome model close the gap to the market?

HISTORICAL_RESEARCH on the 2025 Kalshi player-prop rungs, every model fitted on seasons <= 2024 (nothing from 2025
or 2026 enters a fit). Scored against the monotone market midpoint at each archived horizon, clustered by GAME
(thousands of ladder rungs from one game are not independent; a player-game cluster is reported alongside).

GAME ENVIRONMENT, POINT IN TIME. The v3 study priced every horizon from the nflverse closing spread/total. This study
does not: each horizon's environment is the median of that horizon's own Kalshi full-game SPREAD and TOTAL ladders
(the market-implied centre available at that instant). A horizon with no liquid game ladder gets no environment and
therefore no data distribution (both v3 and v4 refuse), exactly like production. v3 is re-scored under the same
environment so the comparison is fair; v3 under the closing line is kept only to reproduce the v3 study.

    python3 scripts/research/player_engine_v4_study.py --market-data <market-data checkout> --frame /tmp/pe4/frame.pkl

Outputs research/player_engine_v4/results.json (small: aggregates only, never row dumps).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
from collections import defaultdict

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "research"))
from nfl_edge.engines.player import data_dist as DD                     # noqa: E402
from nfl_edge.engines.player import hybrid_dist as HD                   # noqa: E402
from nfl_edge.engines.player.dist import LatticeDistribution            # noqa: E402
from nfl_edge.engines.player.v4 import model as M                       # noqa: E402
from nfl_edge.engines.player.v4.volume import team_game_table           # noqa: E402
from nfl_edge.research import player_distributions as pdist             # noqa: E402
import player_engine_v3_study as V3S                                    # noqa: E402

HORIZONS = ["T-24h", "T-6h", "T-90m", "T-0"]
V4_STAT = {"passing_yards": "passing_yards", "rushing_yards": "rushing_yards", "receiving_yards": "receiving_yards",
           "receptions": "receptions", "passing_tds": "passing_tds", "touchdowns": "touchdowns"}
ABLATIONS = {
    "full": {},
    "no_snap": {"snap": False},
    "no_volume": {"volume": False},
    "no_redistribution": {"redistribution": False},
    "no_allocation": {"allocation": False},
    "no_propagation": {"propagate": False},
    "no_market_env": {"market_env": False},
    "base_structural_only": {"snap": False, "volume": False, "redistribution": False, "allocation": False, "propagate": False},
    "base+snap_alloc": {"volume": False, "redistribution": False, "propagate": False},
    "base+snap_alloc+volume": {"redistribution": False, "propagate": False},
    "base+snap_alloc+volume+redistribution": {"propagate": False},
}


# ------------------------------------------------------------------------------------------------ environment
def horizon_environments(md_root: str) -> dict:
    """(game_id, horizon) -> {spread (home margin), total} from the FULL-game Kalshi ladders at that horizon."""
    pts = defaultdict(lambda: {"s": [], "t": []})
    for f in glob.glob(os.path.join(md_root, "data/kalshi/backfill/horizons/*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if r.get("family") not in ("SPREAD", "TOTAL") or r.get("period") != "FULL" or str(r.get("season")) != "2025":
                continue
            fs = r.get("floor_strike")
            if fs is None:
                continue
            for h in HORIZONS:
                s = (r.get("snaps") or {}).get(h)
                if not s or s.get("bid") is None or s.get("ask") is None or s["ask"] - s["bid"] > 0.12 or s["ask"] <= 0.02 or s["bid"] >= 0.98:
                    continue
                mid = (s["bid"] + s["ask"]) / 2.0
                if r["family"] == "TOTAL":
                    pts[(r["game_id"], h)]["t"].append((float(fs), mid))
                else:
                    # P(team margin > x): home rung -> P(home margin > x); away rung -> P(home margin > -x) = 1 - p
                    if r.get("team") == r.get("home_team"):
                        pts[(r["game_id"], h)]["s"].append((float(fs), mid))
                    elif r.get("team") == r.get("away_team"):
                        pts[(r["game_id"], h)]["s"].append((-float(fs), 1.0 - mid))
    out = {}
    for k, v in pts.items():
        s, t = _median(v["s"]), _median(v["t"])
        if s is not None and t is not None:
            out[k] = {"spread": s, "total": t}
    return out


def _median(points):
    """x where the monotone-smoothed P(Y > x) crosses 0.5; None without rungs on both sides of the median."""
    if len(points) < 2:
        return None
    p = sorted(points)
    xs = np.array([a for a, _ in p]); ys = np.minimum.accumulate(np.array([b for _, b in p]))
    if ys.max() < 0.5 or ys.min() > 0.5:
        return None
    i = int(np.argmax(ys < 0.5))
    if i == 0:
        return None
    x0, x1, y0, y1 = xs[i - 1], xs[i], ys[i - 1], ys[i]
    return float(x0 + (y0 - 0.5) / max(y0 - y1, 1e-9) * (x1 - x0))


def with_env(rows: pd.DataFrame, envs: dict, horizon: str) -> pd.DataFrame:
    r = rows.copy()
    sp = r.game_id.map(lambda g: (envs.get((g, horizon)) or {}).get("spread"))
    tt = r.game_id.map(lambda g: (envs.get((g, horizon)) or {}).get("total"))
    r["spread_line"] = pd.to_numeric(sp, errors="coerce"); r["total_line"] = pd.to_numeric(tt, errors="coerce")
    r["spread_team"] = np.where(r["home"], r["spread_line"], -r["spread_line"])
    r["implied_total"] = (r["total_line"] + r["spread_team"]) / 2.0
    r["env_known"] = r["spread_line"].notna() & r["total_line"].notna()
    return r


# ------------------------------------------------------------------------------------------------ metrics
def cse(v, cl):
    return V3S.cse(v, cl)


def paired(R, a, b="market_mono", cluster="game_id"):
    s = R[R[a].notna() & R[b].notna()]
    if len(s) < 30:
        return None
    pa = np.clip(s[a].to_numpy(float), 1e-4, 1 - 1e-4); pb = np.clip(s[b].to_numpy(float), 1e-4, 1 - 1e-4); y = s.y.to_numpy(float)
    d = (pa - y) ** 2 - (pb - y) ** 2
    ll = -(y * np.log(pa) + (1 - y) * np.log(1 - pa)); llb = -(y * np.log(pb) + (1 - y) * np.log(1 - pb))
    se = cse(d, s[cluster].to_list())
    pg = (s.player_id + "|" + s.game_id).to_list()
    return {"n": int(len(s)), "games": int(s.game_id.nunique()), "player_games": int(len(set(pg))), "brier": float(((pa - y) ** 2).mean()),
            "mkt_brier": float(((pb - y) ** 2).mean()), "diff": float(d.mean()), "se_game": se, "se_player_game": cse(d, pg),
            "logloss": float(ll.mean()), "mkt_logloss": float(llb.mean()), "ece": ece(pa, y), "mkt_ece": ece(pb, y)}


def ece(p, y, bins=10):
    p = np.asarray(p); y = np.asarray(y)
    idx = np.minimum((p * bins).astype(int), bins - 1)
    tot = 0.0
    for b in range(bins):
        m = idx == b
        if m.any():
            tot += m.sum() * abs(p[m].mean() - y[m].mean())
    return float(tot / len(p))


# ------------------------------------------------------------------------------------------------ arms
def v3_dists(frame, rows_by_h, keys):
    """DATA_PLAYER_V3 (data-player-dist-3.0.0, feature set v3, Study-A families) under each horizon's environment."""
    out = {}
    for stat in sorted({k[2] for k in keys}):
        est = stat if stat != "touchdowns" else "touchdowns"
        fam = DD.DEFAULT_FAMILY[DD.STATS.get(est, est)]
        m = DD.fit_stat(frame, est, fam, "v3", 2025)
        for h, rows in rows_by_h.items():
            want = rows[rows.env_known]
            pm = pdist.population_mask(want, m.spec.pop)
            sub = want[pm]
            sub = sub[[(p, g, stat) in keys for p, g in zip(sub.player_id, sub.game_id)]]
            if not len(sub):
                continue
            F, _ = m.cdf_grid(sub)
            for j, (p, g) in enumerate(zip(sub.player_id, sub.game_id)):
                out[(p, g, stat, h)] = LatticeDistribution.from_cdf(F[j])
    return out


def v4_dists(bundle, teams_by_h, rows_by_h, keys, horizons=HORIZONS):
    out, inter = {}, {}
    need = defaultdict(set)
    for p, g, s in keys:
        need[(p, g)].add(s)
    for h in horizons:
        rows = rows_by_h[h]
        rows = rows[rows.env_known & rows.set_index(["player_id", "game_id"]).index.isin(list(need))]
        if not len(rows):
            continue
        I = bundle.intermediates(rows, teams_by_h[h])
        for r in I.to_dict("records"):
            ss = need[(r["player_id"], r["game_id"])]
            D = bundle.distributions(r, stats=list(ss))
            for s, dist in D.items():
                out[(r["player_id"], r["game_id"], s, h)] = dist
            inter[(r["player_id"], r["game_id"], h)] = r
    return out, inter


def score(rungs, market, arms: dict, extra=None):
    recs = []
    for r in rungs:
        for h in HORIZONS:
            mk = market.get((r["player_id"], r["game_id"], r["stat"], h))
            if not mk or mk.get("identification") in (None, "NONE"):
                continue
            s = r["snaps"].get(h)
            if not s or s.get("bid") is None or s.get("ask") is None or (s["ask"] - s["bid"]) > 0.10:
                continue
            mid = (s["bid"] + s["ask"]) / 2.0
            mono = next((x["mid_monotone"] for x in mk["rungs"] if abs(x["k"] - r["k"]) < 1e-9), mid)
            rec = {"game_id": r["game_id"], "player_id": r["player_id"], "week": r["week"], "stat": r["stat"], "k": r["k"], "y": r["y"],
                   "horizon": h, "market_mono": mono, "market_ident": mk["identification"]}
            for name, dd in arms.items():
                d = dd.get((r["player_id"], r["game_id"], r["stat"], h))
                rec[name] = d.survival(r["k"]) if d is not None else None
            recs.append(rec)
    return pd.DataFrame(recs)


def hybrid_col(R, arm, dists, market, w_fn, name):
    vals = []
    for r in R.itertuples():
        d = dists.get((r.player_id, r.game_id, r.stat, r.horizon)); m = market.get((r.player_id, r.game_id, r.stat, r.horizon))
        if d is None or m is None or m.get("identification") in (None, "NONE", "UNDERIDENTIFIED"):
            vals.append(None); continue
        w = w_fn(r)
        h = HD.hybrid(d, m["_dist"], market_identification=m["identification"], w_market=w, structure=HD.MIXTURE)
        vals.append(h["dist"].survival(r.k) if h["status"] == "OK" else None)
    R[name] = vals


# ------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default=os.environ.get("NFL_EDGE_MARKET_DATA", "/tmp/md"))
    ap.add_argument("--frame", default="/tmp/pe4/frame.pkl")
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "player_engine_v4"))
    ap.add_argument("--quick", action="store_true", help="T-90m only for the ablations")
    a = ap.parse_args()
    t0 = time.time()
    V3S.MD_ROOT = a.market_data
    frame = pd.read_pickle(a.frame)
    rungs = V3S.load_rungs()
    market = V3S.market_table(rungs)
    envs = horizon_environments(a.market_data)
    keys = {(r["player_id"], r["game_id"], r["stat"]) for r in rungs}
    te = frame[frame.season == 2025]
    rows_by_h = {h: with_env(te, envs, h) for h in HORIZONS}
    base_teams = team_game_table(frame)

    def teams_for(h):
        env = rows_by_h[h].drop_duplicates(["team", "game_id"])[["team", "game_id", "implied_total", "spread_team"]]
        t = base_teams.drop(columns=["implied_total", "spread_team"]).merge(env, on=["team", "game_id"], how="left")
        return t
    teams_by_h = {h: teams_for(h) for h in HORIZONS}
    print(f"rungs {len(rungs)}; env coverage {sum(1 for k in envs)} (game,horizon); {time.time() - t0:.0f}s", flush=True)
    out = {"protocol": {"train": "seasons 2014-2024 (EWMA features from 2013)", "test": "2025 weeks 1-18 Kalshi player rungs",
                        "environment": "per-horizon median of the FULL-game Kalshi SPREAD/TOTAL ladders (no closing line)",
                        "benchmark": "monotone market midpoint (spread <= 10c)", "cluster": "game (primary), player-game (secondary)",
                        "env_coverage": {h: int(sum(1 for (g, hh) in envs if hh == h)) for h in HORIZONS}}}

    # ---------------- arms: v3 (horizon env), v3 (closing env: reproduces the v3 study), v4 full
    d3 = v3_dists(frame, rows_by_h, keys)
    close_rows = {"T-90m": te.assign(env_known=True)}
    d3c = {(p, g, s, "T-90m"): v for (p, g, s, h), v in v3_dists(frame, close_rows, keys).items()}
    full = M.fit_bundle(frame, 2025, teams=base_teams)
    d4, inter = v4_dists(full, teams_by_h, rows_by_h, keys)
    arms = {"V3": d3, "V4": d4}
    R = score(rungs, market, arms)
    Rc = score(rungs, market, {"V3_CLOSE_ENV": d3c})
    R = R.merge(Rc[["player_id", "game_id", "stat", "k", "horizon", "V3_CLOSE_ENV"]], on=["player_id", "game_id", "stat", "k", "horizon"], how="left")
    print(f"scored {len(R)} rows; {time.time() - t0:.0f}s", flush=True)
    # common rows: both v3 and v4 priced (the fair comparison); v4-only rows reported separately
    R["common"] = R.V3.notna() & R.V4.notna()
    out["by_horizon"] = {h: {arm: paired(R[(R.horizon == h) & R.common], arm) for arm in ("V3", "V4")} | {"V4_vs_V3": paired(R[(R.horizon == h) & R.common], "V4", "V3")}
                         for h in HORIZONS}
    out["v3_close_env_T90"] = paired(R[(R.horizon == "T-90m")], "V3_CLOSE_ENV")
    out["coverage_T90"] = {"rows": int((R.horizon == "T-90m").sum()), "v3": int(R[(R.horizon == "T-90m")].V3.notna().sum()),
                           "v4": int(R[(R.horizon == "T-90m")].V4.notna().sum()),
                           "v4_only": int(((R.horizon == "T-90m") & R.V4.notna() & R.V3.isna()).sum())}
    T = R[R.horizon == "T-90m"]
    out["by_stat_T90"] = {s: {"V3": paired(T[(T.stat == s) & T.common], "V3"), "V4": paired(T[(T.stat == s) & T.common], "V4"),
                              "V4_all_rows": paired(T[T.stat == s], "V4")} for s in sorted(T.stat.unique())}

    # ---------------- hybrids: preregistered selection (weeks 1-9) / confirmation (10-18), T-90m
    for w in (0.5, 0.7, 0.85):
        hybrid_col(R, "V4", d4, market, lambda r, w=w: w, f"V4_MIX_{w}")
        hybrid_col(R, "V3", d3, market, lambda r, w=w: w, f"V3_MIX_{w}")
    sel = R[(R.horizon == "T-90m") & (R.week <= 9)]; conf = R[(R.horizon == "T-90m") & (R.week >= 10)]
    cands = ["V4", "V4_MIX_0.5", "V4_MIX_0.7", "V4_MIX_0.85", "V3_MIX_0.85"]
    out["hybrid_select_w1_9"] = {c: paired(sel[sel.common], c) for c in cands}
    out["hybrid_confirm_w10_18"] = {c: paired(conf[conf.common], c) for c in cands}
    # adaptive (interpretable, small): one market weight per stat family in {0.5, 0.7, 0.85, 1.0}, chosen on weeks 1-9
    fam_w = {}
    for s in sorted(sel.stat.unique()):
        best, bw = None, 1.0
        for w in (0.5, 0.7, 0.85):
            p = paired(sel[(sel.stat == s) & sel.common], f"V4_MIX_{w}")
            if p and (best is None or p["diff"] < best):
                best, bw = p["diff"], w
        fam_w[s] = bw if (best is not None and best < 0) else 1.0
    out["adaptive_family_weights"] = fam_w
    hybrid_col(R, "V4", d4, market, lambda r: fam_w.get(r.stat, 1.0), "V4_ADAPTIVE")
    conf = R[(R.horizon == "T-90m") & (R.week >= 10)]
    out["hybrid_confirm_w10_18"]["V4_ADAPTIVE"] = paired(conf[conf.common], "V4_ADAPTIVE")
    out["hybrid_by_stat_confirm"] = {s: {c: paired(conf[(conf.stat == s) & conf.common], c) for c in ("V4_MIX_0.85", "V3_MIX_0.85", "V4_ADAPTIVE")}
                                     for s in sorted(conf.stat.unique())}
    out["hybrid_full_T90"] = {c: paired(R[(R.horizon == "T-90m") & R.common], c) for c in ("V4_MIX_0.85", "V3_MIX_0.85", "V4_ADAPTIVE")}

    # ---------------- disagreement bands (v4 vs market) and whether anything distinguishes useful disagreement
    T = R[(R.horizon == "T-90m")].copy()
    T["dis"] = 100 * (T.V4 - T.market_mono).abs()
    T["band"] = pd.cut(T.dis, [0, 1, 2, 3, 5, 10, 100], right=False)
    out["disagreement_bands_V4_T90"] = {str(b): paired(sub, "V4") for b, sub in T.groupby("band", observed=True)}
    T["dis3"] = 100 * (T.V3 - T.market_mono).abs()
    T["band3"] = pd.cut(T.dis3, [0, 1, 2, 3, 5, 10, 100], right=False)
    out["disagreement_bands_V3_T90"] = {str(b): paired(sub, "V3") for b, sub in T.groupby("band3", observed=True)}

    # ---------------- segments (T-90m) from the v4 intermediates (all pregame)
    seg = []
    for r in T.itertuples():
        i = inter.get((r.player_id, r.game_id, "T-90m")) or {}
        stable = (i.get("n_cur_season", 0) or 0) >= 2 and abs((i.get("last_snap_share") or 0) - (i.get("ewma_snap_share") or 0)) < 0.1 \
            and not i.get("own_q") and not i.get("self_returning") and not i.get("changed_team") and not i.get("self_new")
        seg.append({"snap_sd_hi": (i.get("snap_sd") or 0) > 0.12, "starter": (i.get("snap_mean") or 0) >= 0.6,
                    "rotational": 0.3 <= (i.get("snap_mean") or 0) < 0.6, "questionable": bool(i.get("own_q")),
                    "teammate_absence": (i.get("vac_same_t") or 0) + (i.get("vac_same_c") or 0) > 0.05,
                    "returning": bool(i.get("self_returning")), "changed_team": bool(i.get("changed_team")) or bool(i.get("self_new")),
                    "committee_rb": i.get("pgroup") == "RB" and 0.3 <= (i.get("share_c") or 0) < 0.55, "stable_role": bool(stable)})
    S = pd.concat([T.reset_index(drop=True), pd.DataFrame(seg)], axis=1)
    out["segments_T90"] = {}
    for c in ("stable_role", "snap_sd_hi", "starter", "rotational", "committee_rb", "questionable", "teammate_absence", "returning", "changed_team"):
        out["segments_T90"][c] = {"yes": {"V4": paired(S[S[c] & S.common], "V4"), "V3": paired(S[S[c] & S.common], "V3")},
                                  "no": {"V4": paired(S[~S[c] & S.common], "V4"), "V3": paired(S[~S[c] & S.common], "V3")}}
    # what (if anything) separates useful large disagreement from model failure: within |V4 - market| > 5pp only
    L = S[(100 * (S.V4 - S.market_mono).abs() > 5) & S.V4.notna()].copy()
    L["model_above"] = L.V4 > L.market_mono
    out["large_disagreement_explained_T90"] = {"n_rows": int(len(L)), "all": paired(L, "V4")}
    for c in ("stable_role", "snap_sd_hi", "starter", "teammate_absence", "returning", "model_above"):
        out["large_disagreement_explained_T90"][c] = {"yes": paired(L[L[c]], "V4"), "no": paired(L[~L[c]], "V4")}
    out["large_disagreement_explained_T90"]["by_stat"] = {st: paired(L[L.stat == st], "V4") for st in sorted(L.stat.unique())}
    # abstention preview: v4 rows the V4 abstention rule would refuse vs accept (see abstention.decide_v4)
    from nfl_edge.engines.player import abstention as AB
    states = []
    for r in S.itertuples():
        i = inter.get((r.player_id, r.game_id, "T-90m")) or {}
        states.append(AB.decide_v4(i, stat=r.stat, p_model=r.V4, p_market=r.market_mono)["structural_state"] if r.V4 == r.V4 and r.V4 is not None else None)
    S["abst"] = states
    out["abstention_T90"] = {"counts": S["abst"].value_counts().to_dict(),
                             "by_state": {st: paired(S[S.abst == st], "V4") for st in S["abst"].dropna().unique()},
                             "accepted": paired(S[S.abst == "PROJECTION_VALID"], "V4"),
                             "abstained": paired(S[S.abst.notna() & (S.abst != "PROJECTION_VALID")], "V4")}

    # ---------------- ablations (T-90m; each refits the bundle with one stage switched to what v3 used)
    out["ablations_T90"] = {}
    for name, cfg in ABLATIONS.items():
        b = full if name == "full" else M.fit_bundle(frame, 2025, cfg, teams=base_teams, verbose=lambda *x: None)
        dd, _ = v4_dists(b, teams_by_h, rows_by_h, keys, horizons=["T-90m"])
        Ra = score(rungs, market, {"A": dd, "V3": d3})
        Ra = Ra[(Ra.horizon == "T-90m") & Ra.A.notna() & Ra.V3.notna()]
        out["ablations_T90"][name] = {"vs_market": paired(Ra, "A"), "vs_full_v4_rows_by_stat": {s: paired(Ra[Ra.stat == s], "A") for s in sorted(Ra.stat.unique())}}
        print(f"  ablation {name}: {out['ablations_T90'][name]['vs_market'] and round(out['ablations_T90'][name]['vs_market']['diff'], 5)}  {time.time() - t0:.0f}s", flush=True)
    out["bundle"] = full.summary()
    out["runtime_s"] = round(time.time() - t0, 1)
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "results.json"), "w"), indent=1, default=str)
    print(json.dumps({k: out[k] for k in ("by_horizon", "coverage_T90")}, indent=1, default=str)[:3000])


if __name__ == "__main__":
    main()
