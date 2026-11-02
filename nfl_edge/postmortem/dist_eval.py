"""Walk-forward, point-in-time evaluation of key-number-aware distributions against the existing baselines.

SPLITS (fixed in code, not tuned on the test seasons):
  * features: ``sim.opponent_adjust`` matchup expectations (own offence vs opponent defence, ridge-adjusted for schedule
    quality, strictly earlier games only), for EPA/play, plays, seconds/play, TD/drive, plus special-teams EPA/game
    (kicking-team EPA on kickoffs, punts, FGs, PATs, adjusted by the same solver). No havoc metric.
  * calibration seasons 2022-2023 pick the ridge strength and kernel bandwidth multiplier (fit on 2019-2021).
  * held-out TEST seasons 2024 and 2025: every game is predicted from a model fit only on earlier seasons.
BASELINES: (a) MARKET-ONLY: same machinery, location from the closing spread/total only; (b) INCUMBENT: the repo's
ResidualBank simulation (``sim.key_numbers.m0_draws``) for final margin / final total / team points.
ANCHOR CAVEAT: the market centre is the CLOSING consensus line, because nflverse carries no historical Kalshi 1Q/1H/team-
total quotes. This measures whether the evidence improves the SHAPE and LOCATION of the distribution given the market
centre; it is not a profit backtest and says nothing about Kalshi prices.
NOT INCLUDED (blocker, stated in the report): injuries and confirmed-QB status have no point-in-time history in this repo
beyond the 2026 availability_pit capture, so they enter only through the market line that already prices them.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from . import distributions as DS

CAL_SEASONS = (2022, 2023)
TEST_SEASONS = (2024, 2025)
FIT_START = 2019
METRICS = ("epa_play", "plays", "sec_per_play", "td_per_drive", "st_epa")
LAMBDA = 8.0                              # the middle of the repo's own grid (opponent_adjust.LAMBDAS); not tuned here
RIDGE_GRID = (1.0, 10.0, 100.0)
BANDWIDTH_MULT_GRID = (0.35, 0.6, 1.0)    # kernel bandwidth = mult * residual sd of the location model

TARGETS = {   # name: (kind, lo, hi, ladder half-range)
    "final_total": ("total", 0, 110, 14), "final_margin": ("margin", -60, 60, 10), "team_pts": ("team", 0, 70, 10),
    "h1_total": ("total", 0, 75, 8), "q1_total": ("total", 0, 40, 5), "h1_margin": ("margin", -45, 45, 8), "h1_team_pts": ("team", 0, 50, 6),
}


def build_tables(seasons=range(2018, 2026)):
    import polars as pl
    from nfl_edge.sim import data as D
    from nfl_edge.sim import opponent_adjust as OA
    seasons = list(seasons)
    mt = OA.metric_table(seasons)
    st_rows, per_rows = [], []
    for s in seasons:
        d = D._read_pbp(s)
        st = (d.filter(pl.col("play_type").is_in(["kickoff", "punt", "field_goal", "extra_point"]) & pl.col("posteam").is_not_null()
                       & pl.col("season_type").is_in(["REG", "POST"]))
              .group_by(["game_id", "posteam"]).agg(pl.col("epa").sum().alias("st_epa")).rename({"posteam": "team"}))
        st_rows.append(st.to_pandas())
        qd = d.filter(pl.col("season_type").is_in(["REG", "POST"])).group_by("game_id").agg([
            pl.col("total_home_score").filter(pl.col("qtr") <= 1).max().alias("q1_home"),
            pl.col("total_away_score").filter(pl.col("qtr") <= 1).max().alias("q1_away"),
            pl.col("total_home_score").filter(pl.col("qtr") <= 2).max().alias("h1_home"),
            pl.col("total_away_score").filter(pl.col("qtr") <= 2).max().alias("h1_away")])
        per_rows.append(qd.to_pandas())
    mt = mt.merge(pd.concat(st_rows), on=["game_id", "team"], how="left")
    mt["st_epa"] = mt["st_epa"].fillna(0.0)
    per = pd.concat(per_rows)
    g = D.schedule().to_pandas()
    g = g[g["season"].isin(seasons) & g["result"].notna() & g["spread_line"].notna() & g["total_line"].notna() & (g["game_type"] == "REG")]
    g = g.merge(per, on="game_id", how="inner")
    return mt, g


def matchup_frame(mt: pd.DataFrame, seasons) -> pd.DataFrame:
    from nfl_edge.sim import opponent_adjust as OA
    lw = OA._last_weeks(mt)
    lams = {m: LAMBDA for m in METRICS}
    parts = [OA.snapshot_matchups(mt, int(s), int(w), lams, lw, METRICS) for s in seasons for w in sorted(mt.loc[mt["season"] == s, "week"].unique())]
    return pd.concat(parts, ignore_index=True)


def target_rows(g: pd.DataFrame, mx: pd.DataFrame) -> dict:
    """{target: DataFrame[game_id, season, week, y, market (list), extra (list)]} with identical games for every model."""
    m = mx.set_index(["game_id", "team"])
    out = {k: [] for k in TARGETS}
    for r in g.itertuples():
        try:
            h, a = m.loc[(r.game_id, r.home_team)], m.loc[(r.game_id, r.away_team)]
        except KeyError:
            continue
        vals = np.array([h[f"mx_{k}"] for k in METRICS] + [a[f"mx_{k}"] for k in METRICS], float)
        if not np.isfinite(vals).all():
            continue
        s, T = float(r.spread_line), float(r.total_line)
        hv = {k: float(h[f"mx_{k}"]) for k in METRICS}; av = {k: float(a[f"mx_{k}"]) for k in METRICS}
        base = dict(game_id=r.game_id, season=int(r.season), week=int(r.week))
        tot_x = [hv["epa_play"] + av["epa_play"], hv["plays"] + av["plays"], (hv["sec_per_play"] + av["sec_per_play"]) / 2,
                 hv["td_per_drive"] + av["td_per_drive"], hv["st_epa"] + av["st_epa"]]
        mar_x = [hv["epa_play"] - av["epa_play"], hv["plays"] - av["plays"], hv["td_per_drive"] - av["td_per_drive"], hv["st_epa"] - av["st_epa"]]
        for name, y in (("final_total", r.total), ("h1_total", r.h1_home + r.h1_away), ("q1_total", r.q1_home + r.q1_away)):
            out[name].append(dict(base, y=float(y), market=[T, abs(s)], extra=tot_x))
        for name, y in (("final_margin", r.result), ("h1_margin", r.h1_home - r.h1_away)):
            out[name].append(dict(base, y=float(y), market=[s], extra=mar_x))
        for name, hy, ay in (("team_pts", r.home_score, r.away_score), ("h1_team_pts", r.h1_home, r.h1_away)):
            for own, opp, y, sgn, ih in ((hv, av, hy, 1.0, 1.0), (av, hv, ay, -1.0, 0.0)):
                out[name].append(dict(base, y=float(y), market=[T, sgn * s, ih],
                                      extra=[own["epa_play"], own["plays"], own["td_per_drive"], own["st_epa"],
                                             (own["sec_per_play"] + opp["sec_per_play"]) / 2, opp["plays"]], team_row=int(ih)))
    return {k: pd.DataFrame(v) for k, v in out.items()}


class LocationModel:
    """mu = intercept + market (unpenalised) + standardised matchup extras (ridge). ``use_extra=False`` is the market-only baseline."""

    def __init__(self, use_extra: bool, alpha: float):
        self.use_extra, self.alpha = use_extra, alpha

    def _X(self, df):
        M = np.array(df["market"].tolist(), float)
        X = np.column_stack([np.ones(len(df)), M])
        if self.use_extra:
            E = (np.array(df["extra"].tolist(), float) - self.emu) / self.esd
            X = np.column_stack([X, E])
        return X

    def fit(self, df):
        if self.use_extra:
            self.emu, self.esd = DS.standardize_fit(np.array(df["extra"].tolist(), float))
        X = self._X(df)
        k_market = 1 + len(df["market"].iloc[0])
        pen = np.r_[np.zeros(k_market), np.full(X.shape[1] - k_market, self.alpha)]
        self.beta = DS.fit_ridge(X, df["y"].to_numpy(float), pen)
        self.resid_sd = float(np.std(df["y"].to_numpy(float) - X @ self.beta))
        return self

    def predict(self, df):
        return self._X(df) @ self.beta


def score_rows(train: pd.DataFrame, test: pd.DataFrame, model: LocationModel, mult: float, name: str):
    kind, lo, hi, half = TARGETS[name]
    mu_tr = model.predict(train); mu_te = model.predict(test)
    ytr, str_ = train["y"].to_numpy(float), train["season"].to_numpy(float)
    ref = int(test["season"].max())
    h = max(mult * model.resid_sd, 0.25)
    offs = np.arange(-half - 0.5, half + 0.51, 1.0)
    recs = []
    for i, r in enumerate(test.itertuples()):
        sup, pmf, info = DS.kernel_pmf(mu_tr, ytr, str_, float(mu_te[i]), ref, h, lo=lo, hi=hi)
        recs.append(dict(game_id=r.game_id, season=r.season, y=r.y, mu=float(mu_te[i]), ls=DS.log_score(sup, pmf, r.y),
                         events=DS.ladder_events(sup, pmf, float(mu_te[i]), r.y, offs), pmf=pmf, support=sup))
    return recs


def summarize(recs):
    ev = [e for r in recs for e in r["events"]]
    rel, ece = DS.reliability(ev)
    return {"n": len(recs), "mean_log_score": float(np.mean([r["ls"] for r in recs])), "ladder_brier": DS.brier(ev), "ece": ece, "reliability": rel}


def key_report(train, test_recs, name):
    kind = TARGETS[name][0]
    keys = DS.emergent_keys(train["y"].to_numpy(float), absolute=(kind == "margin"))
    rows = {}
    ys = np.array([r["y"] for r in test_recs])
    realised = float(np.mean([(abs(y) if kind == "margin" else y) in keys for y in ys]))
    def mass(r):
        sup, pmf = r["support"], r["pmf"]
        if kind == "margin":
            return float(sum(pmf[(sup == k) | (sup == -k)].sum() for k in keys))
        return DS.key_mass(sup, pmf, keys)
    return {"keys_from_training": keys, "realised_share": realised, "predicted_share": float(np.mean([mass(r) for r in test_recs]))}


def incumbent_recs(name, test_games: pd.DataFrame, hist: pd.DataFrame, Y: int, n=4000):
    from nfl_edge.sim import key_numbers as KN
    kind, lo, hi, half = TARGETS[name]
    offs = np.arange(-half - 0.5, half + 0.51, 1.0)
    recs = []
    for i, g in enumerate(test_games.itertuples()):
        d = KN.m0_draws(hist, float(g.spread_line), float(g.total_line), Y, n, seed=11 + i)
        if name == "final_margin":
            ys = [(g.result, d["margin"])]
        elif name == "final_total":
            ys = [(g.total, d["total"])]
        else:
            ys = [(g.home_score, d["home"]), (g.away_score, d["away"])]
        for y, draws in ys:
            sup, pmf = DS.pmf_from_draws(draws, lo, hi)
            recs.append(dict(game_id=g.game_id, season=g.season, y=float(y), mu=float(np.mean(draws)), ls=DS.log_score(sup, pmf, y),
                             events=DS.ladder_events(sup, pmf, float(np.mean(draws)), float(y), offs), pmf=pmf, support=sup))
    return recs


def run(seasons=range(2018, 2026), with_incumbent=True, log=print):
    mt, g = build_tables(seasons)
    mx = matchup_frame(mt, sorted(set(mt["season"])))
    T = target_rows(g, mx)
    report = {"splits": {"fit_start": FIT_START, "calibration": CAL_SEASONS, "test": TEST_SEASONS}, "metrics": METRICS, "lambda": LAMBDA, "targets": {}}
    for name, df in T.items():
        df = df[df["season"] >= FIT_START]
        # --- calibration: choose alpha / bandwidth on 2022-23 using models fit on 2019-21 only
        tr, ca = df[df["season"] < CAL_SEASONS[0]], df[df["season"].isin(CAL_SEASONS)]
        best = {}
        for label, use_extra, alphas in (("market_only", False, (0.0,)), ("candidate", True, RIDGE_GRID)):
            cands = []
            for a in alphas:
                mdl = LocationModel(use_extra, a).fit(tr)
                for m in BANDWIDTH_MULT_GRID:
                    cands.append((summarize(score_rows(tr, ca, mdl, m, name))["mean_log_score"], a, m))
            best[label] = max(cands)
        entry = {"calibration_choice": {k: {"alpha": v[1], "bandwidth_mult": v[2], "cal_log_score": v[0]} for k, v in best.items()}, "test": {}}
        pooled = {"market_only": [], "candidate": [], "incumbent": []}
        for Y in TEST_SEASONS:
            trn, tst = df[df["season"] < Y], df[df["season"] == Y]
            recs = {}
            for label, use_extra in (("market_only", False), ("candidate", True)):
                _, a, m = best[label]
                mdl = LocationModel(use_extra, a).fit(trn)
                recs[label] = score_rows(trn, tst, mdl, m, name)
            if with_incumbent and name in ("final_margin", "final_total", "team_pts"):
                from nfl_edge.sim import key_numbers as KN
                tg = g[(g["season"] == Y) & g["game_id"].isin(set(tst["game_id"]))]
                recs["incumbent"] = incumbent_recs(name, tg, KN.history(Y - 1), Y)
            for k, v in recs.items():
                pooled[k] += v
            entry["test"][str(Y)] = {k: summarize(v) for k, v in recs.items()}
            entry["test"][str(Y)]["key_numbers"] = {k: key_report(trn, v, name) for k, v in recs.items()}
            log(f"{name} {Y} " + " ".join(f"{k}={entry['test'][str(Y)][k]['mean_log_score']:.4f}" for k in recs))
        # paired differences on pooled test rows (same rows, same order)
        def paired(a, b):
            ka = {(r["game_id"], i): r for i, r in enumerate(pooled[a])}
            d = [x["ls"] - y["ls"] for x, y in zip(pooled[a], pooled[b])] if len(pooled[a]) == len(pooled[b]) else None
            if d is None:
                return None
            return DS.paired_bootstrap_ci(d, [r["game_id"] for r in pooled[a]])
        entry["paired_log_score_diff"] = {"candidate_minus_market_only": paired("candidate", "market_only"),
                                          "candidate_minus_incumbent": paired("candidate", "incumbent") if pooled["incumbent"] else None,
                                          "market_only_minus_incumbent": paired("market_only", "incumbent") if pooled["incumbent"] else None}
        by_season = {}
        for Y in TEST_SEASONS:
            c = entry["test"][str(Y)]
            by_season[str(Y)] = c["candidate"]["mean_log_score"] - c["market_only"]["mean_log_score"]
        d = entry["paired_log_score_diff"]["candidate_minus_market_only"]
        entry["verdict_vs_market_only"] = ("EVIDENCE_IMPROVES" if d and d["lo"] > 0 and all(v > 0 for v in by_season.values())
                                           else "EVIDENCE_HURTS" if d and d["hi"] < 0 else "NOT_DEMONSTRATED")
        entry["season_diffs"] = by_season
        report["targets"][name] = entry
    return report
