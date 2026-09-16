#!/usr/bin/env python3
"""DEVELOPMENT / DIAGNOSTIC scoring of the simulation layer on 2026 Week 1.

Week 1 2026 was inspected before and during this build, so nothing here is validation.  It answers the
diagnostic questions the rebuild was asked to answer: which families the incumbent failed worst, whether
the simulation's football-only view is closer, how the largest disagreements fared, and whether the
reconciled probability (weights fitted on 2025, no 2026 outcome) sits where it should.

For every Week-1 game the market universe is the newest incumbent ledger snapshot at or before
kickoff - 75 minutes; features use only games completed four hours before that instant (Thursday's game
informs Sunday's); settlement is the official box score from nflverse.

Writes research/simulation_engine/WEEK1_2026_DIAGNOSTIC.md and week1_2026_diagnostic.json.
"""
from __future__ import annotations
import argparse, json, os, sys
from datetime import timedelta
import numpy as np, pandas as pd, polars as pl
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.sim import data as D, prospective as P, backtest as B, reconcile as R

STAT_OF = P.STAT_MAP


def settle(rec: dict, pg: pd.DataFrame, tg: pd.DataFrame, sched: pd.DataFrame) -> float | None:
    g = sched[sched["game_id"] == rec["game_id"]]
    if g.empty or pd.isna(g.iloc[0]["home_score"]):
        return None
    g = g.iloc[0]; home, away = g["home_team"], g["away_team"]
    hs, as_ = float(g["home_score"]), float(g["away_score"]); margin = hs - as_
    fam = rec["family"]
    if fam == "GAME_WINNER":
        win = (margin > 0) if rec["team"] == home else (margin < 0)
        return 0.5 if margin == 0 else float(win)
    if fam == "SPREAD":
        x = margin if rec["team"] == home else -margin
        return float(x > float(rec["floor_strike"]))
    if fam == "TOTAL":
        return float(hs + as_ >= float(rec["threshold"]))
    if fam == "TEAM_TOTAL":
        x = hs if rec["team"] == home else as_
        return float(x >= float(rec["threshold"]))
    if fam == "PLAYER_STAT":
        st = STAT_OF.get(rec["stat"]); pid = rec.get("player_id")
        if st is None or not pid:
            return None
        row = pg[(pg["game_id"] == rec["game_id"]) & (pg["player_id"] == pid)]
        if row.empty:
            return None  # did not appear: Kalshi voids or settles NO per its rules; excluded here
        return float(row.iloc[0][st] >= float(rec["threshold"]))
    return None


def brier(p, y):
    p = np.asarray(p, float); y = np.asarray(y, float); ok = np.isfinite(p) & np.isfinite(y)
    return float(np.mean((p[ok] - y[ok]) ** 2)) if ok.any() else None, int(ok.sum())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default="/home/user/_market_data_wt")
    ap.add_argument("--n-sims", type=int, default=10000)
    ap.add_argument("--lead-minutes", type=int, default=75)
    a = ap.parse_args()
    sched = D.schedule().to_pandas(); wk = sched[(sched["season"] == 2026) & (sched["week"] == 1)].copy()
    wk["kickoff"] = pd.to_datetime(wk["gameday"] + " " + wk["gametime"]).dt.tz_localize("America/New_York").dt.tz_convert("UTC")
    bundle = json.load(open(os.path.join(B.OUT, "bundle_2026.json")))
    wpath = os.path.join(B.OUT, "reconciliation_weights.json")
    weights = R.load_weights(wpath) if os.path.exists(wpath) else None
    pmap = pl.read_parquet(os.path.join(ROOT, "data", "silver", "kalshi_player_map.parquet"))
    pmap = pmap.filter(pl.col("gsis_id").is_not_null() & pl.col("status").str.starts_with("RESOLVED"))
    player_map = dict(zip(pmap["kalshi_player_id"].to_list(), pmap["gsis_id"].to_list()))
    pg = D.load("player_games", [2026]).to_pandas(); tg = D.load("team_games", [2026]).to_pandas()
    all_rows = []
    for kick, grp in wk.groupby("kickoff"):
        cutoff = kick.to_pydatetime() - timedelta(minutes=a.lead_minutes)
        try:
            ledger_rows, man, run_id = P.latest_ledger(a.market_data, at_or_before=cutoff)
        except FileNotFoundError:
            continue
        observed_at = max((r.get("observed_at") or "") for r in ledger_rows)
        slate = P.slate_inputs(2026, 1, cutoff, a.market_data, ledger_rows=ledger_rows, verbose=lambda *x: None)
        keep = set(grp["game_id"])
        slate["games"] = {k: v for k, v in slate["games"].items() if k in keep}
        if not slate["games"]:
            continue
        rows = P.price_slate(slate, ledger_rows, bundle, weights, n_sims=a.n_sims, run_id=run_id, observed_at=observed_at,
                             generated_at=cutoff, player_map=player_map, verbose=lambda *x: None)
        for r in rows:
            r["cutoff"] = cutoff.isoformat(); r["y"] = settle(r, pg, tg, sched)
        all_rows += rows
        print(f"{kick}: {len(slate['games'])} games, ledger {run_id}, {len(rows)} contracts", flush=True)
    df = pd.DataFrame(all_rows)
    df = df[df["y"].notna() & df["mid"].notna()]
    df["p_inc"] = df["incumbent_model_probability"]
    out = {"label": "DEVELOPMENT / DIAGNOSTIC -- Week 1 2026 was inspected before this layer was built; not validation",
           "n_contracts": int(len(df)), "families": {}, "player_stats": {}, "disagreement_bands": {}, "largest_football_disagreements": []}
    pr = df[df["family"] == "PLAYER_STAT"]

    def block(g):
        return {"n": int(len(g)), "brier_market_mid": brier(g["mid"], g["y"])[0], "brier_incumbent": brier(g["p_inc"], g["y"])[0],
                "n_incumbent": brier(g["p_inc"], g["y"])[1], "brier_football": brier(g["p_football"], g["y"])[0],
                "brier_reconciled": brier(g["p_reconciled"], g["y"])[0], "n_reconciled": brier(g["p_reconciled"], g["y"])[1],
                "mean_mid": float(g["mid"].mean()), "mean_football": float(g["p_football"].mean()),
                "mean_incumbent": float(g["p_inc"].mean()) if g["p_inc"].notna().any() else None, "rate": float(g["y"].mean())}
    for fam, g in df.groupby("family"):
        g = g[g["p_football"].notna()]
        if len(g):
            out["families"][fam] = block(g)
    for st, g in pr.groupby("stat"):
        g = g[g["p_football"].notna()]
        if len(g):
            out["player_stats"][st] = block(g)
    p2 = pr[pr["p_football"].notna()].copy()
    p2["dis_f"] = (p2["p_football"] - p2["mid"]).abs(); p2["dis_i"] = (p2["p_inc"] - p2["mid"]).abs()
    for lo, hi in ((0, 0.05), (0.05, 0.10), (0.10, 0.20), (0.20, 1.01)):
        m = (p2["dis_f"] >= lo) & (p2["dis_f"] < hi)
        mi = (p2["dis_i"] >= lo) & (p2["dis_i"] < hi)
        out["disagreement_bands"][f"{lo:.2f}-{hi:.2f}"] = {
            "football_band": {"n": int(m.sum()), "brier_football": brier(p2.loc[m, "p_football"], p2.loc[m, "y"])[0],
                              "brier_market": brier(p2.loc[m, "mid"], p2.loc[m, "y"])[0], "brier_reconciled": brier(p2.loc[m, "p_reconciled"], p2.loc[m, "y"])[0]},
            "incumbent_band": {"n": int(mi.sum()), "brier_incumbent": brier(p2.loc[mi, "p_inc"], p2.loc[mi, "y"])[0],
                               "brier_market": brier(p2.loc[mi, "mid"], p2.loc[mi, "y"])[0]}}
    top = p2.sort_values("dis_f", ascending=False).head(15)
    out["largest_football_disagreements"] = top[["ticker", "stat", "threshold", "mid", "p_football", "p_reconciled", "p_inc", "y",
                                                 "football_mean", "market_mean"]].to_dict("records")
    topi = p2.sort_values("dis_i", ascending=False).head(15)
    out["largest_incumbent_disagreements"] = topi[["ticker", "stat", "threshold", "mid", "p_inc", "p_football", "p_reconciled", "y"]].to_dict("records")
    os.makedirs(B.OUT, exist_ok=True)
    json.dump(out, open(os.path.join(B.OUT, "week1_2026_diagnostic.json"), "w"), indent=1, default=str)
    df.drop(columns=["attribution"], errors="ignore").to_parquet(os.path.join(B.OUT, "week1_2026_diagnostic_rows.parquet"))
    # markdown
    L = [f"# Week 1 2026 -- {out['label']}", "",
         "Universe: the newest incumbent ledger snapshot at or before kickoff - 75 min for each kickoff cluster; features from games "
         "completed 4 h before that instant; settlement from the nflverse box score.  Market = quoted midpoint (research, not executable).", ""]
    L += ["## By family", "", "| family | n | market mid | incumbent | football-only | reconciled (n) |", "|---|---|---|---|---|---|"]
    for fam, b in out["families"].items():
        L.append(f"| {fam} | {b['n']} | {b['brier_market_mid']:.4f} | {b['brier_incumbent'] if b['brier_incumbent'] is None else round(b['brier_incumbent'], 4)} | "
                 f"{b['brier_football']:.4f} | {b['brier_reconciled'] if b['brier_reconciled'] is None else round(b['brier_reconciled'], 4)} ({b['n_reconciled']}) |")
    L += ["", "## Player statistics (Brier)", "", "| stat | n | market mid | incumbent | football-only | reconciled | mean mid / football / incumbent / rate |", "|---|---|---|---|---|---|---|"]
    for st, b in out["player_stats"].items():
        L.append(f"| {st} | {b['n']} | {b['brier_market_mid']:.4f} | {b['brier_incumbent'] if b['brier_incumbent'] is None else round(b['brier_incumbent'], 4)} | "
                 f"{b['brier_football']:.4f} | {b['brier_reconciled'] if b['brier_reconciled'] is None else round(b['brier_reconciled'], 4)} | "
                 f"{b['mean_mid']:.3f} / {b['mean_football']:.3f} / {b['mean_incumbent'] if b['mean_incumbent'] is None else round(b['mean_incumbent'], 3)} / {b['rate']:.3f} |")
    L += ["", "## By |disagreement vs mid| band (player props)", "", "| band | football: n | football Brier | market Brier | reconciled Brier | incumbent: n | incumbent Brier | market Brier |", "|---|---|---|---|---|---|---|---|"]
    for band, b in out["disagreement_bands"].items():
        f, i = b["football_band"], b["incumbent_band"]
        L.append(f"| {band} | {f['n']} | {f['brier_football']} | {f['brier_market']} | {f['brier_reconciled']} | {i['n']} | {i['brier_incumbent']} | {i['brier_market']} |")
    L += ["", "## Largest football-only disagreements", "", "| ticker | stat | k | mid | football | reconciled | incumbent | settled | football mean | market mean |", "|---|---|---|---|---|---|---|---|---|---|"]
    for r in out["largest_football_disagreements"]:
        L.append(f"| `{r['ticker']}` | {r['stat']} | {r['threshold']} | {r['mid']:.3f} | {r['p_football']:.3f} | {r['p_reconciled'] if r['p_reconciled'] is None else round(r['p_reconciled'], 3)} | "
                 f"{r['p_inc'] if r['p_inc'] is None or (isinstance(r['p_inc'], float) and np.isnan(r['p_inc'])) else round(r['p_inc'], 3)} | {r['y']:.0f} | {r['football_mean']:.1f} | {r['market_mean'] if r['market_mean'] is None or (isinstance(r['market_mean'], float) and np.isnan(r['market_mean'])) else round(r['market_mean'], 1)} |")
    L += ["", "## Largest incumbent disagreements (the Week-1 failure mode)", "", "| ticker | stat | k | mid | incumbent | football | reconciled | settled |", "|---|---|---|---|---|---|---|---|"]
    for r in out["largest_incumbent_disagreements"]:
        L.append(f"| `{r['ticker']}` | {r['stat']} | {r['threshold']} | {r['mid']:.3f} | {round(r['p_inc'], 3)} | {r['p_football']:.3f} | {r['p_reconciled'] if r['p_reconciled'] is None else round(r['p_reconciled'], 3)} | {r['y']:.0f} |")
    open(os.path.join(B.OUT, "WEEK1_2026_DIAGNOSTIC.md"), "w").write("\n".join(L) + "\n")
    print(json.dumps(out["player_stats"], indent=0, default=str)[:3000])


if __name__ == "__main__":
    main()
