#!/usr/bin/env python3
"""Player Engine v2: historical walk-forward evidence (HISTORICAL_RESEARCH). Two studies in one run.

STUDY A -- family choice on the v2 features (walk-forward, test seasons 2020-2025, prop-relevant subset)
    For every statistic, every research family conditioned on the v2 opportunity x efficiency mean model; the
    family with the lowest ladder Brier is recorded as the v2 choice, next to the v1-feature choice, so the
    decision is out of sample and auditable. Also: does the v2 mean model beat the v1 mean model (MAE)?

STUDY B -- the head-to-head on the exact 2025 Kalshi-listed rungs, at every archived horizon
    old player model (v1 features + v1 families; the incumbent's family)   from research/kalshi_2025
    DATA_PLAYER_DIST v2 (fitted on <= 2024)
    MARKET_PLAYER_DIST (the ladder at T-24h / T-6h / T-90m / T-0, PAV + family fit)
    HYBRID_PLAYER_DIST candidates (location blend / mixture, w in {0.3, 0.5, 0.7}); w chosen on weeks 1-9, confirmed on 10-18
    Metrics: Brier, log loss, clustered by game; by statistic; the market is scored with its own monotone mid.
    The rung population is the market's (Kalshi's rungs), so a data model that only knows its own history is being
    asked the market's question -- exactly the prospective situation.

Nothing here touches 2026 outcomes. Outputs research/player_engine_v2/{results.json, RESULTS.md}.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import defaultdict

import numpy as np
import pandas as pd
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.engines.player import data_dist as DD, hybrid_dist as HD, market_dist as MD   # noqa: E402
from nfl_edge.engines.player.dist import LatticeDistribution                                  # noqa: E402
from nfl_edge.engines.player.features_v2 import add_v2_features                              # noqa: E402
from nfl_edge.kalshi.classifier import classify                                              # noqa: E402
from nfl_edge.research import player_distributions as pdist                                  # noqa: E402

OUT = os.path.join(ROOT, "research", "player_engine_v2")
STAT_MAP = {"passing_yards": "passing_yards", "rushing_yards": "rushing_yards", "receiving_yards": "receiving_yards", "receptions": "receptions",
            "passing_tds": "passing_tds", "touchdowns": "touchdowns"}
HORIZONS = ["T-24h", "T-6h", "T-90m", "T-0"]
WEIGHTS = [0.3, 0.5, 0.7]
FAMILIES = {"yards": ["normal", "hurdle_gamma", "negbin", "scale_emp_binned"], "count": ["normal", "poisson", "negbin", "scale_emp_binned"],
            "td": ["poisson", "negbin", "scale_emp_binned"]}


def cse(v, cl):
    v = np.asarray(v, float); n = len(v)
    by = defaultdict(float)
    for x, c in zip(v - v.mean(), cl):
        by[c] += x
    g = len(by)
    return float(np.sqrt(sum(t * t for t in by.values()) / (n * n) * (g / (g - 1.0)))) if g > 1 else float("nan")


def load_table():
    cfg = json.load(open(os.path.join(ROOT, "research/player_distributions/results.json")))["config"]
    df = pdist.load_player_games(ROOT, range(2013, 2026))
    priors = pdist.position_priors(df, range(2013, 2016))
    df = pdist.add_ewma_features(df, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"], priors=priors)
    df = add_v2_features(df, halflife=cfg["halflife"], season_carry=cfg["season_carry"], shrink_k=cfg["shrink_k"])
    return DD.ensure_columns(df)


# ---------------------------------------------------------------------------------------------------- study A
def study_a(df, test_seasons):
    res = {}
    for stat in ["receiving_yards", "rushing_yards", "passing_yards", "receptions", "carries", "attempts", "completions",
                 "passing_tds", "interceptions", "touchdowns", "rush_rec_yards"]:
        spec = DD._spec(stat)
        fams = FAMILIES[spec.kind]
        pooled = {fs: {f: [] for f in fams} for fs in ("v1", "v2")}
        mae = {"v1": [], "v2": [], "ewma": []}
        n_rows = 0
        for S in test_seasons:
            pm = pdist.population_mask(df, spec.pop)
            te = df[pm & (df.season == S)]
            elig = te[f"ewma_{spec.opp}"].to_numpy(float) >= spec.elig_min_opp
            te = te[elig]
            if not len(te):
                continue
            y = np.clip(te[spec.col].to_numpy(float), 0, None)
            for fs in ("v1", "v2"):
                for f in fams:
                    try:
                        m = DD.fit_stat(df, stat, f, fs, S)
                    except ValueError:
                        continue
                    F, im = m.cdf_grid(te)
                    ev = pdist.evaluate_cdf(F, m.grid, y, spec.thresholds)
                    pooled[fs][f].append({"season": S, "n": int(len(y)), "brier": ev["brier"], "crps": ev["crps"], "ece": ev["ece"],
                                          "tail_ratio": (ev["buckets"].get("tail") or ev["buckets"].get("mid") or {}).get("ratio")})
                    if f == fams[0]:
                        mae[fs].append((float(np.mean(np.abs(im["mu"] - y))), len(y)))
            mae["ewma"].append((float(np.mean(np.abs(te[f"ewma_{spec.col}"].to_numpy(float) - y))), len(y)))
            n_rows += len(y)
        out = {"n_rows": n_rows, "families": {}}
        for fs in ("v1", "v2"):
            out["families"][fs] = {}
            for f in fams:
                rows = pooled[fs][f]
                if not rows:
                    continue
                n = np.array([r["n"] for r in rows], float)
                out["families"][fs][f] = {k: float(np.sum(n * np.array([r[k] if r[k] is not None else np.nan for r in rows])) / n.sum())
                                          for k in ("brier", "crps", "ece", "tail_ratio")}
            best = min(out["families"][fs], key=lambda f: out["families"][fs][f]["brier"]) if out["families"][fs] else None
            out[f"chosen_{fs}"] = best
        out["mae"] = {k: float(sum(a * n for a, n in v) / max(1, sum(n for _, n in v))) for k, v in mae.items() if v}
        res[stat] = out
        print(f"  A {stat}: v1 best {out['chosen_v1']} {out['families']['v1'].get(out['chosen_v1'], {}).get('brier')} | v2 best {out['chosen_v2']} "
              f"{out['families']['v2'].get(out['chosen_v2'], {}).get('brier')} | MAE v1 {out['mae'].get('v1'):.3f} v2 {out['mae'].get('v2'):.3f}", flush=True)
    return res


# ---------------------------------------------------------------------------------------------------- study B
def load_2025_rungs(md):
    pmap = pl.read_parquet(os.path.join(ROOT, "data/silver/kalshi_player_map_2025.parquet")).filter(pl.col("gsis_id").is_not_null())
    kid2gsis = dict(zip(pmap["kalshi_player_id"].to_list(), pmap["gsis_id"].to_list()))
    games = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet")).filter(pl.col("season") == 2025)
    gk = {(r["gameday"], r["away_team"], r["home_team"]): (r["game_id"], r["week"]) for r in games.select("gameday", "away_team", "home_team", "game_id", "week").to_dicts()}
    rows = []
    for f in glob.glob(os.path.join(md, "data/kalshi/backfill/horizons/*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if r.get("family") != "PLAYER_STAT" or r.get("result") not in ("yes", "no") or r.get("stat") not in STAT_MAP or r.get("threshold") is None:
                continue
            gw = gk.get((r["game_date"], r["away_team"], r["home_team"]))
            gs = kid2gsis.get(r.get("player_kalshi_id"))
            if not gw or not gs:
                continue
            snaps = {h: (r.get("snaps") or {}).get(h) for h in HORIZONS}
            rows.append({"ticker": r["ticker"], "game_id": gw[0], "week": int(gw[1]), "player_id": gs, "stat": STAT_MAP[r["stat"]], "k": float(r["threshold"]),
                         "y": 1.0 if r["result"] == "yes" else 0.0, "snaps": snaps})
    return rows


def study_b(df, rungs, md):
    old = {r["ticker"]: r["model_p"] for r in pl.read_parquet(os.path.join(ROOT, "research/kalshi_2025/prop_model_probs_2025.parquet")).iter_rows(named=True)}
    # DATA v2 distributions for every (player, game, stat) that has a rung
    keyset = {(r["player_id"], r["game_id"], r["stat"]) for r in rungs}
    te2025 = df[df.season == 2025].reset_index(drop=True)
    idx = {(p, g): i for i, (p, g) in enumerate(zip(te2025.player_id, te2025.game_id))}
    dists = {}
    for stat in sorted({k[2] for k in keyset}):
        try:
            m = DD.fit_stat(df, stat, DD.DEFAULT_FAMILY[DD.STATS.get(stat, stat)], "v2", 2025)
        except ValueError as e:
            print("  skip", stat, e); continue
        want = sorted({(p, g) for p, g, s in keyset if s == stat and (p, g) in idx})
        if not want:
            continue
        rows = te2025.iloc[[idx[w] for w in want]]
        F, im = m.cdf_grid(rows)
        for j, w in enumerate(want):
            dists[(w[0], w[1], stat)] = LatticeDistribution.from_cdf(F[j], meta={"mu": float(im["mu"][j])})
        print(f"  B data v2 {stat}: {len(want)} player-games", flush=True)
    # ladders per (player, game, stat, horizon) from the archived quotes
    ladders = defaultdict(list)
    for r in rungs:
        for h in HORIZONS:
            s = r["snaps"].get(h)
            if s and s.get("bid") is not None and s.get("ask") is not None:
                ladders[(r["player_id"], r["game_id"], r["stat"], h)].append({"threshold": r["k"], "yes_bid": s["bid"], "yes_ask": s["ask"]})
    market = {}
    for key, lad in ladders.items():
        market[key] = MD.market_distribution(key[2], lad)
    # score every rung under every arm at every horizon
    recs = []
    for r in rungs:
        dk = (r["player_id"], r["game_id"], r["stat"])
        d = dists.get(dk)
        for h in HORIZONS:
            mk = market.get(dk + (h,))
            if not mk or mk.get("identification") in (None, "NONE"):
                continue
            s = r["snaps"].get(h)
            if not s or s.get("bid") is None or s.get("ask") is None or (s["ask"] - s["bid"]) > 0.10:
                continue
            mid = (s["bid"] + s["ask"]) / 2.0
            mono = next((x["mid_monotone"] for x in mk["rungs"] if abs(x["k"] - r["k"]) < 1e-9), mid)
            rec = {"ticker": r["ticker"], "game_id": r["game_id"], "week": r["week"], "stat": r["stat"], "k": r["k"], "y": r["y"], "horizon": h,
                   "market_mid": mid, "market_mono": mono, "market_ident": mk["identification"], "old": old.get(r["ticker"]),
                   "data_v2": d.survival(r["k"]) if d is not None else None}
            if d is not None and mk["identification"] != "UNDERIDENTIFIED":
                for w in WEIGHTS:
                    hb = HD.hybrid(d, mk["_dist"], market_identification=mk["identification"], w_market=w, structure=HD.LOCATION_BLEND)
                    rec[f"hyb_loc_{w}"] = hb["dist"].survival(r["k"]) if hb["status"] == "OK" else None
                    hm = HD.hybrid(d, mk["_dist"], market_identification=mk["identification"], w_market=w, structure=HD.MIXTURE)
                    rec[f"hyb_mix_{w}"] = hm["dist"].survival(r["k"]) if hm["status"] == "OK" else None
            recs.append(rec)
    R = pd.DataFrame(recs)
    print(f"  B scored rows: {len(R)} over {R.game_id.nunique()} games", flush=True)
    arms = ["old", "data_v2", "market_mono"] + [f"hyb_loc_{w}" for w in WEIGHTS] + [f"hyb_mix_{w}" for w in WEIGHTS]
    out = {"n_rows": int(len(R)), "n_games": int(R.game_id.nunique()), "by_horizon": {}, "by_stat_T0": {}, "by_stat_T24h": {}, "weight_selection": {}}
    def score(sub, arm):
        s = sub[sub[arm].notna()]
        if not len(s):
            return None
        p = np.clip(s[arm].to_numpy(float), 1e-4, 1 - 1e-4); y = s["y"].to_numpy(float)
        b = (p - y) ** 2; ll = -(y * np.log(p) + (1 - y) * np.log(1 - p))
        return {"n": int(len(s)), "games": int(s.game_id.nunique()), "brier": float(b.mean()), "log_loss": float(ll.mean()), "mean_p": float(p.mean()), "obs": float(y.mean())}
    def paired(sub, a, b_):
        s = sub[sub[a].notna() & sub[b_].notna()]
        if len(s) < 50:
            return None
        pa = np.clip(s[a].to_numpy(float), 1e-4, 1 - 1e-4); pb = np.clip(s[b_].to_numpy(float), 1e-4, 1 - 1e-4); y = s["y"].to_numpy(float)
        d = (pa - y) ** 2 - (pb - y) ** 2
        se = cse(d, s.game_id.to_list())
        return {"n": int(len(s)), "games": int(s.game_id.nunique()), "diff": float(d.mean()), "se": se, "z": float(d.mean() / se) if se else None}
    for h in HORIZONS:
        sub = R[R.horizon == h]
        out["by_horizon"][h] = {"arms": {a: score(sub, a) for a in arms}, "paired_vs_market": {a: paired(sub, a, "market_mono") for a in arms if a != "market_mono"}}
    for h, key in (("T-0", "by_stat_T0"), ("T-24h", "by_stat_T24h")):
        for stat in sorted(R.stat.unique()):
            sub = R[(R.horizon == h) & (R.stat == stat)]
            out[key][stat] = {"arms": {a: score(sub, a) for a in ("old", "data_v2", "market_mono", "hyb_loc_0.7")},
                              "paired_vs_market": {a: paired(sub, a, "market_mono") for a in ("old", "data_v2", "hyb_loc_0.7")},
                              "data_v2_vs_old": paired(sub, "data_v2", "old")}
    # preregistration of w: choose on weeks 1-9 at T-90m (the shadow's most common decision horizon), confirm on 10-18
    sel = R[(R.horizon == "T-90m") & (R.week <= 9)]; conf = R[(R.horizon == "T-90m") & (R.week >= 10)]
    cands = [f"hyb_loc_{w}" for w in WEIGHTS] + [f"hyb_mix_{w}" for w in WEIGHTS] + ["market_mono", "data_v2"]
    sel_scores = {a: score(sel, a) for a in cands}
    best = min((a for a in cands if sel_scores[a]), key=lambda a: sel_scores[a]["brier"])
    out["weight_selection"] = {"selection_weeks": "1-9", "confirmation_weeks": "10-18", "horizon": "T-90m",
                               "selection_brier": {a: (sel_scores[a] or {}).get("brier") for a in cands}, "selected": best,
                               "confirmation": {a: score(conf, a) for a in cands}, "confirmation_paired_vs_market": {a: paired(conf, a, "market_mono") for a in cands if a != "market_mono"}}
    out["market_identification"] = R.groupby("horizon")["market_ident"].value_counts().unstack(fill_value=0).to_dict()
    return out, R


def render(A, B):
    L = ["# Player Engine v2: historical walk-forward evidence (HISTORICAL_RESEARCH)", "",
         "`scripts/research/player_engine_v2_study.py`. Nothing here uses a 2026 outcome. Study A chooses the distribution family per "
         "statistic out of sample on the v2 opportunity x efficiency features (test seasons 2020-2025, prop-relevant subset). Study B is the "
         "head-to-head on the exact 2025 Kalshi-listed rungs at every archived horizon, clustered by game.", "",
         "## A. Family choice on v2 features (ladder Brier, prop-relevant subset, pooled 2020-2025)", "",
         "| statistic | rows | v1 best family (Brier) | v2 best family (Brier) | MAE ewma / v1 / v2 |", "|---|---|---|---|---|"]
    for stat, r in A.items():
        f1, f2 = r["chosen_v1"], r["chosen_v2"]
        b1 = r["families"]["v1"].get(f1, {}).get("brier"); b2 = r["families"]["v2"].get(f2, {}).get("brier")
        m = r["mae"]
        L.append(f"| {stat} | {r['n_rows']} | {f1} ({b1:.5f}) | {f2} ({b2:.5f}) | {m.get('ewma', float('nan')):.3f} / {m.get('v1', float('nan')):.3f} / {m.get('v2', float('nan')):.3f} |")
    L += ["", "Per-family detail (Brier / CRPS / ECE / tail ratio) is in results.json.", "",
          "## B. Head-to-head on the 2025 Kalshi rungs", "",
          f"{B['n_rows']} rung x horizon rows over {B['n_games']} games (books quoted within 10 cents). Arms: OLD = the incumbent's family on v1 features "
          "(research/kalshi_2025); DATA_V2 = this engine on v2 features (fitted <= 2024); MARKET = the monotone ladder midpoint; HYB_LOC(w) = location "
          "blend, HYB_MIX(w) = pmf mixture, w = market weight.", ""]
    for h, v in B["by_horizon"].items():
        L += [f"### {h}", "", "| arm | n | games | Brier | log loss | mean p | observed | Brier vs MARKET (clustered) | z |", "|---|---|---|---|---|---|---|---|---|"]
        for a, s in v["arms"].items():
            if not s:
                continue
            pv = (v["paired_vs_market"] or {}).get(a)
            L.append(f"| {a} | {s['n']} | {s['games']} | {s['brier']:.5f} | {s['log_loss']:.5f} | {s['mean_p']:.3f} | {s['obs']:.3f} | "
                     + (f"{pv['diff']:+.5f} ± {pv['se']:.5f}" if pv else "-") + " | " + (f"{pv['z']:+.1f}" if pv and pv.get('z') is not None else "-") + " |")
        L.append("")
    for key, title in (("by_stat_T0", "By statistic at T-0 (the close)"), ("by_stat_T24h", "By statistic at T-24h")):
        L += [f"### {title}", "", "| statistic | n | OLD Brier | DATA_V2 Brier | MARKET Brier | HYB_LOC(0.7) Brier | DATA_V2 − MARKET | DATA_V2 − OLD |", "|---|---|---|---|---|---|---|---|"]
        for stat, v in B[key].items():
            a = v["arms"]; pm = v["paired_vs_market"].get("data_v2"); po = v["data_v2_vs_old"]
            def b(x):
                return f"{a[x]['brier']:.5f}" if a.get(x) else "-"
            L.append(f"| {stat} | {a['market_mono']['n'] if a.get('market_mono') else 0} | {b('old')} | {b('data_v2')} | {b('market_mono')} | {b('hyb_loc_0.7')} | "
                     + (f"{pm['diff']:+.5f} ± {pm['se']:.5f} (z {pm['z']:+.1f})" if pm else "-") + " | " + (f"{po['diff']:+.5f} ± {po['se']:.5f} (z {po['z']:+.1f})" if po else "-") + " |")
        L.append("")
    ws = B["weight_selection"]
    L += ["### Hybrid weight preregistration", "", f"Selection on weeks {ws['selection_weeks']} at {ws['horizon']}: " +
          ", ".join(f"{a} {v:.5f}" for a, v in ws["selection_brier"].items() if v is not None) + f". **Selected: {ws['selected']}**.", "",
          f"Confirmation on weeks {ws['confirmation_weeks']} (paired Brier vs MARKET, clustered):", "", "| arm | n | Brier | vs MARKET | z |", "|---|---|---|---|---|"]
    for a, s in ws["confirmation"].items():
        if not s:
            continue
        pv = ws["confirmation_paired_vs_market"].get(a)
        L.append(f"| {a} | {s['n']} | {s['brier']:.5f} | " + (f"{pv['diff']:+.5f} ± {pv['se']:.5f}" if pv else "-") + " | " + (f"{pv['z']:+.1f}" if pv and pv.get('z') is not None else "-") + " |")
    L += ["", "Market-ladder identification by horizon: " + json.dumps(B["market_identification"]), "",
          "## Reading", "",
          "* The market is scored on ITS OWN rungs with its own monotone midpoint; a data arm that beats it here would be beating the close, which "
          "the encompassing result (research/model_vs_market) says the old model could not do. Where the market wins, it says so above.",
          "* The hybrid weight is preregistered from weeks 1-9 and confirmed on weeks 10-18 of 2025; it is not tuned on 2026.",
          "* All arms stay shadow-only prospectively; this study decides structure and weights, not authority."]
    return "\n".join(L) + "\n"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default="/home/user/_md")
    ap.add_argument("--test-seasons", default="2020-2025")
    ap.add_argument("--skip-a", action="store_true")
    a = ap.parse_args()
    lo, hi = (int(x) for x in a.test_seasons.split("-"))
    df = load_table()
    print(f"research table {df.shape}", flush=True)
    A = {} if a.skip_a else study_a(df, range(lo, hi + 1))
    rungs = load_2025_rungs(a.market_data)
    print(f"2025 rungs joined: {len(rungs)}", flush=True)
    B, R = study_b(df, rungs, a.market_data)
    os.makedirs(OUT, exist_ok=True)
    json.dump({"study_a": A, "study_b": B}, open(os.path.join(OUT, "results.json"), "w"), indent=1, default=str)
    R.to_parquet(os.path.join(OUT, "rung_scores_2025.parquet"))
    open(os.path.join(OUT, "RESULTS.md"), "w").write(render(A, B))
    print(open(os.path.join(OUT, "RESULTS.md")).read())


if __name__ == "__main__":
    main()
