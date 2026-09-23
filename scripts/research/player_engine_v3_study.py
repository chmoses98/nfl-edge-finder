#!/usr/bin/env python3
"""Player Engine v3: why the prospective data arm failed, and whether the fix closes the gap to the market.

HISTORICAL_RESEARCH on the 2025 Kalshi player-prop rungs (archived horizons T-24h / T-6h / T-90m / T-0), every model
fitted on seasons <= 2024 (walk-forward: nothing from 2025 or 2026 enters a fit). Game-clustered paired Brier
differences against the monotone market midpoint, exactly as research/player_engine_v2 did.

    python3 scripts/research/player_engine_v3_study.py --market-data <market-data checkout> [--cache /tmp/pe3]

Part A -- ablation of the production defects on the v2 engine:
    HIST        v2 as studied (consensus lines, current-season games in the EWMAs)
    ZERO_LINES  target-season lines blanked -> implied_total NaN -> 0.0 in design()   (the prospective defect)
    NO_CUR      current-season outcomes hidden from the features                   (the prospective defect)
    PROD        both
Part B -- v3 (market-implied environment in production; current season; recency + structural opportunity) vs v2,
          hybrid mixtures of v3 with the market (selection weeks 1-9, confirmation 10-18, T-90m).
Part C -- v3 performance by |v3 - market| band (the large-disagreement guard).

Nothing here touches a 2026 outcome. Outputs research/player_engine_v3/results.json.
"""

import glob, json, os, sys, pickle
from collections import defaultdict
import numpy as np, pandas as pd, polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.engines.player import data_dist as DD, market_dist as MD
from nfl_edge.engines.player.dist import LatticeDistribution
from nfl_edge.engines.player.features_v2 import add_v2_features
from nfl_edge.research import player_distributions as pdist

MD_ROOT = os.environ.get("NFL_EDGE_MARKET_DATA", "/tmp/md")
STAT_MAP = {"passing_yards": "passing_yards", "rushing_yards": "rushing_yards", "receiving_yards": "receiving_yards",
            "receptions": "receptions", "passing_tds": "passing_tds", "touchdowns": "touchdowns"}
HORIZONS = ["T-24h", "T-6h", "T-90m", "T-0"]
CFG = json.load(open(os.path.join(ROOT, "research/player_distributions/results.json")))["config"]
CACHE = os.environ.get("NFL_EDGE_STUDY_CACHE", "/tmp/player_engine_v3_cache")
os.makedirs(CACHE, exist_ok=True)


def cse(v, cl):
    v = np.asarray(v, float); n = len(v)
    by = defaultdict(float)
    for x, c in zip(v - v.mean(), cl):
        by[c] += x
    g = len(by)
    return float(np.sqrt(sum(t * t for t in by.values()) / (n * n) * (g / (g - 1.0)))) if g > 1 else float("nan")


def features(df, blank_current=None):
    """blank_current: season whose OUTCOMES are hidden from every row's features (production defect 2)."""
    priors = pdist.position_priors(df, range(2013, 2016))
    d = df.copy()
    if blank_current is not None:
        # the target rows keep their outcomes for scoring, but the EWMA inputs of that season are hidden
        keep = d[pdist.BASE_STATS].copy()
        d.loc[d.season == blank_current, pdist.BASE_STATS] = np.nan
    d = pdist.add_ewma_features(d, halflife=CFG["halflife"], season_carry=CFG["season_carry"], shrink_k=CFG["shrink_k"], priors=priors)
    d = add_v2_features(d, halflife=CFG["halflife"], season_carry=CFG["season_carry"], shrink_k=CFG["shrink_k"])
    if blank_current is not None:
        d[pdist.BASE_STATS] = keep.reindex(d.index).to_numpy()
    return DD.ensure_columns(d)


def load_rungs():
    pmap = pl.read_parquet(os.path.join(ROOT, "data/silver/kalshi_player_map_2025.parquet")).filter(pl.col("gsis_id").is_not_null())
    kid2gsis = dict(zip(pmap["kalshi_player_id"].to_list(), pmap["gsis_id"].to_list()))
    rows = []
    for f in glob.glob(os.path.join(MD_ROOT, "data/kalshi/backfill/horizons/*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if r.get("family") != "PLAYER_STAT" or r.get("result") not in ("yes", "no") or r.get("stat") not in STAT_MAP or r.get("threshold") is None:
                continue
            if str(r.get("season")) != "2025" or int(r.get("week") or 0) > 18:
                continue
            gs = kid2gsis.get(r.get("player_kalshi_id"))
            if not gs:
                continue
            rows.append({"ticker": r["ticker"], "game_id": r["game_id"], "week": int(r["week"]), "player_id": gs, "stat": STAT_MAP[r["stat"]],
                         "k": float(r["threshold"]), "y": 1.0 if r["result"] == "yes" else 0.0, "snaps": {h: (r.get("snaps") or {}).get(h) for h in HORIZONS}})
    return rows


def market_table(rungs):
    ladders = defaultdict(list)
    for r in rungs:
        for h in HORIZONS:
            s = r["snaps"].get(h)
            if s and s.get("bid") is not None and s.get("ask") is not None:
                ladders[(r["player_id"], r["game_id"], r["stat"], h)].append({"threshold": r["k"], "yes_bid": s["bid"], "yes_ask": s["ask"]})
    return {k: MD.market_distribution(k[2], lad) for k, lad in ladders.items()}


def dists_for(df, rungs, feature_set="v2", mutate=None, families=None):
    keyset = {(r["player_id"], r["game_id"], r["stat"]) for r in rungs}
    te = df[df.season == 2025].reset_index(drop=True)
    if mutate:
        te = mutate(te)
    idx = {(p, g): i for i, (p, g) in enumerate(zip(te.player_id, te.game_id))}
    out, mus = {}, {}
    for stat in sorted({k[2] for k in keyset}):
        fam = (families or {}).get(stat) or DD.DEFAULT_FAMILY[DD.STATS.get(stat, stat)]
        m = DD.fit_stat(df, stat, fam, feature_set, 2025)
        want = sorted({(p, g) for p, g, s in keyset if s == stat and (p, g) in idx})
        rows = te.iloc[[idx[w] for w in want]]
        pm = pdist.population_mask(rows, m.spec.pop)
        rows = rows[pm]; want = [w for w, ok in zip(want, pm) if ok]
        if not len(rows):
            continue
        F, im = m.cdf_grid(rows)
        for j, w in enumerate(want):
            out[(w[0], w[1], stat)] = LatticeDistribution.from_cdf(F[j])
            mus[(w[0], w[1], stat)] = (float(im["mu"][j]), float(im["muo"][j]))
    return out, mus


def score_rows(rungs, market, arms: dict):
    recs = []
    for r in rungs:
        dk = (r["player_id"], r["game_id"], r["stat"])
        for h in HORIZONS:
            mk = market.get(dk + (h,))
            if not mk or mk.get("identification") in (None, "NONE"):
                continue
            s = r["snaps"].get(h)
            if not s or s.get("bid") is None or s.get("ask") is None or (s["ask"] - s["bid"]) > 0.10:
                continue
            mid = (s["bid"] + s["ask"]) / 2.0
            mono = next((x["mid_monotone"] for x in mk["rungs"] if abs(x["k"] - r["k"]) < 1e-9), mid)
            rec = {"ticker": r["ticker"], "game_id": r["game_id"], "player_id": r["player_id"], "week": r["week"], "stat": r["stat"], "k": r["k"], "y": r["y"],
                   "horizon": h, "market_mono": mono, "market_ident": mk["identification"],
                   "market_mean": (mk["_dist"].mean() if mk.get("_dist") is not None else None)}
            for name, dd in arms.items():
                d = dd.get(dk)
                rec[name] = d.survival(r["k"]) if d is not None else None
            recs.append(rec)
    return pd.DataFrame(recs)


def paired(R, a, b="market_mono"):
    s = R[R[a].notna() & R[b].notna()]
    if len(s) < 30:
        return None
    pa = np.clip(s[a].to_numpy(float), 1e-4, 1 - 1e-4); pb = np.clip(s[b].to_numpy(float), 1e-4, 1 - 1e-4); y = s.y.to_numpy(float)
    d = (pa - y) ** 2 - (pb - y) ** 2
    se = cse(d, s.game_id.to_list())
    return {"n": len(s), "games": s.game_id.nunique(), "brier": float(((pa - y) ** 2).mean()), "mkt": float(((pb - y) ** 2).mean()),
            "diff": float(d.mean()), "se": se, "z": float(d.mean() / se) if se else None}


def base_table():
    p = os.path.join(CACHE, "hist.pkl")
    if os.path.exists(p):
        return pd.read_pickle(p)
    df = pdist.load_player_games(ROOT, range(2013, 2026))
    df.to_pickle(p)
    return df




def band_table(R, arm="V3", horizon="T-90m"):
    R = R[R.horizon == horizon].copy()
    R["dis"] = 100 * (R[arm] - R.market_mono).abs()
    R["band"] = pd.cut(R.dis, [0, 0.5, 1, 2, 3, 5, 10, 100], right=False)
    return {str(b): paired(sub, arm) for b, sub in R.groupby("band", observed=True)}


def main():
    import argparse
    from nfl_edge.engines.player import hybrid_dist as HD
    from nfl_edge.engines.player.features_v3 import add_v3_features
    global MD_ROOT
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default=MD_ROOT)
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "player_engine_v3"))
    args = ap.parse_args()
    MD_ROOT = args.market_data
    raw = base_table()
    rungs = load_rungs()
    market = market_table(rungs)
    f_hist = features(raw)
    f_nocur = features(raw, blank_current=2025)

    def zero_lines(te):
        te = te.copy(); te["implied_total"] = np.nan; te["spread_team"] = np.nan
        return te
    A = {"HIST": dists_for(f_hist, rungs)[0], "ZERO_LINES": dists_for(f_hist, rungs, mutate=zero_lines)[0],
         "NO_CUR": dists_for(f_nocur, rungs)[0], "PROD": dists_for(f_nocur, rungs, mutate=zero_lines)[0]}
    RA = score_rows(rungs, market, A)
    out = {"part_a_ablation": {h: {k: paired(RA[RA.horizon == h], k) for k in A} for h in HORIZONS},
           "part_a_weeks_2_3_T90": {k: paired(RA[(RA.horizon == "T-90m") & RA.week.isin([2, 3])], k) for k in A}}
    f = add_v3_features(f_hist)
    arms = {"V2": dists_for(f, rungs, feature_set="v2")[0], "V3": dists_for(f, rungs, feature_set="v3")[0]}
    R = score_rows(rungs, market, arms)
    for w in (0.5, 0.7, 0.85):
        vals = []
        for r in R.itertuples():
            d = arms["V3"].get((r.player_id, r.game_id, r.stat)); m = market.get((r.player_id, r.game_id, r.stat, r.horizon))
            if d is None or m is None or m.get("identification") in (None, "NONE", "UNDERIDENTIFIED"):
                vals.append(None); continue
            h = HD.hybrid(d, m["_dist"], market_identification=m["identification"], w_market=w, structure=HD.MIXTURE)
            vals.append(h["dist"].survival(r.k) if h["status"] == "OK" else None)
        R[f"V3_MIX_{w}"] = vals
    cand = ["V2", "V3", "V3_MIX_0.5", "V3_MIX_0.7", "V3_MIX_0.85"]
    out["part_b_by_horizon"] = {h: {**{a: paired(R[R.horizon == h], a) for a in cand}, "V3_vs_V2": paired(R[R.horizon == h], "V3", "V2")} for h in HORIZONS}
    sel = R[(R.horizon == "T-90m") & (R.week <= 9)]; conf = R[(R.horizon == "T-90m") & (R.week >= 10)]
    out["part_b_select_w1_9"] = {a: paired(sel, a) for a in cand}
    out["part_b_confirm_w10_18"] = {a: paired(conf, a) for a in cand}
    out["part_b_by_stat_T90"] = {s: {a: paired(R[(R.horizon == "T-90m") & (R.stat == s)], a) for a in ("V2", "V3", "V3_MIX_0.85")}
                                 for s in sorted(R.stat.unique())}
    out["part_c_disagreement_bands_T90"] = band_table(R)
    os.makedirs(args.out, exist_ok=True)
    json.dump(out, open(os.path.join(args.out, "results.json"), "w"), indent=1, default=str)
    print(json.dumps(out, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main()
