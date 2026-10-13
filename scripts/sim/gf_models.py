"""Game Flow Intelligence Championship (RESEARCH_ONLY): forecasters.

Every forecaster returns, per game, a RECORD built from one weighted set of (simulated or historical) game trajectories, so all
events of one game are jointly coherent by construction:
   pm  pmf of the halftime home margin (-50..50)      pt  pmf of the halftime total (0..80)
   pe  probabilities [comp4q, lead14, comeback10, lc4, home_lead7_ht, away_lead7_ht, drought20]     mh2  expected second-half total
Pregame information only: closing spread / total (the market centre, T-0, as in the earlier championships), strictly prior
team features, and models fitted on seasons < Y.  Nothing from the target game's play-by-play enters a forecast.
"""
from __future__ import annotations
import os, sys, warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scripts.sim import gf_data as GD, hmac_features as H, hmac_models as M, gsdl_features as GF

ROOT = GD.D.ROOT
OUT = os.path.join(ROOT, "research", "historical_game_flow_championship")
RES = os.path.join(OUT, "cache")
TRAIN_START = 2003
OCOLS = ["ht_m", "ht_t", "comp4q", "lead14", "comeback10", "lc4", "home_lead7_ht", "away_lead7_ht", "drought20", "h2_t"]
EV = ["comp4q", "lead14", "comeback10", "lc4", "home_lead7_ht", "away_lead7_ht", "drought20"]
NPM, NPT = 101, 81
SEED = 20261014
BW = {"b1": (2.5, 4.0), "b2": (4.0, 6.5), "b3": (6.0, 9.0)}


def flow_table() -> pd.DataFrame:
    G, T, _ = GD.build(); G = G[GD.recon_ok(G)].copy(); G["h2_t"] = G["reg_t"] - G["ht_t"]
    s = GF.schedule_frame(); s = s[s.game_type == "REG"][["game_id", "spread_line", "total_line", "home_team", "away_team", "week", "overtime"]]
    return G.merge(s, on="game_id", how="inner").dropna(subset=["spread_line", "total_line"]).reset_index(drop=True)


def _tri(d, h):
    return np.clip(1 - np.abs(d) / h, 0, None)


def record_from(O, w):
    w = w / w.sum(); pm = np.bincount(np.clip(np.round(O[:, 0]) + 50, 0, 100).astype(int), w, NPM); pt = np.bincount(np.clip(np.round(O[:, 1]), 0, 80).astype(int), w, NPT)
    return {"pm": pm, "pt": pt, "pe": w @ O[:, 2:9], "mh2": float(w @ O[:, 9])}


def kernel_weights(tr, sp, tl, Y, hs, ht, hl=6.0, floor=0.10):
    ws = 0.5 ** ((Y - tr["season"].to_numpy(float)) / hl); ds, dt = tr["spread_line"].to_numpy(float) - sp, tr["total_line"].to_numpy(float) - tl
    w = ws * _tri(ds, hs) * _tri(dt, ht); wide = ws * _tri(ds, 3 * hs) * _tri(dt, 3 * ht)
    if w.sum() < 1e-8:
        w = wide
    return (1 - floor) * w / w.sum() + floor * wide / wide.sum()


def loo_means(tr, hs, ht, Y, cols, chunk=400):
    """Leave-one-game-out kernel means of ``cols`` for every training game (the residual-learning target)."""
    sp, tl = tr["spread_line"].to_numpy(float), tr["total_line"].to_numpy(float); ws = 0.5 ** ((Y - tr["season"].to_numpy(float)) / 6.0); O = tr[cols].to_numpy(float)
    out = np.zeros((len(tr), len(cols)))
    for a in range(0, len(tr), chunk):
        b = min(len(tr), a + chunk); ds = sp[a:b, None] - sp[None, :]; dt = tl[a:b, None] - tl[None, :]
        W = ws[None, :] * _tri(ds, hs) * _tri(dt, ht); W[np.arange(b - a), np.arange(a, b)] = 0.0
        Wd = ws[None, :] * _tri(ds, 3 * hs) * _tri(dt, 3 * ht); Wd[np.arange(b - a), np.arange(a, b)] = 0.0
        W = 0.9 * W / np.maximum(W.sum(1, keepdims=True), 1e-12) + 0.1 * Wd / np.maximum(Wd.sum(1, keepdims=True), 1e-12)
        out[a:b] = W @ O
    return out


def tilt(O, w, target_mean, dims, iters=12):
    X = O[:, dims]; th = np.zeros(len(dims)); q = w
    for _ in range(iters):
        z = X @ th; z -= z.max(); q = w * np.exp(z); q /= q.sum(); mean = q @ X; g = mean - target_mean
        if np.abs(g).max() < 1e-7:
            break
        cov = (X * q[:, None]).T @ X - np.outer(mean, mean)
        th = np.clip(th - np.linalg.solve(cov + 1e-6 * np.eye(len(dims)), g), -2.0, 2.0)
    return q


# ----------------------------------------------------------------------------------------------- feature families
SIT = ["pass_trail", "pass_lead", "pass_slope"]
FAMS = {
    "G1": (["mf_plays", "sf_plays", "mf_sec_per_play", "sf_sec_per_play", "mf_neutral_pass_rate", "sf_neutral_pass_rate", "mf_epa_play", "sf_epa_play",
            "mf_success_rate", "sf_success_rate", "mf_pass_epa", "sf_pass_epa", "mf_rush_epa", "sf_rush_epa", "mf_points", "sf_points", "mf_sack_rate", "sf_sack_rate"]),
    "G2": (["d_pass_trail", "s_pass_trail", "d_pass_lead", "s_pass_lead", "d_pass_slope", "s_pass_slope", "f_cnew_diff", "f_cnew_sum", "f_clog_diff", "f_clog_sum"]),
    "G3": (["i_pass_m", "i_pass_s", "i_rush_m", "i_rush_s", "i_pace_m", "i_pace_s", "i_expl_m", "i_expl_s", "mf_expl_pass", "sf_expl_pass", "mf_expl_rush", "sf_expl_rush"]),
}
RES_TARGETS = ["ht_m", "ht_t", "comp4q", "lead14", "comeback10", "lc4"]
CLIP = {"ht_m": 3.0, "ht_t": 3.0, "comp4q": 0.12, "lead14": 0.12, "comeback10": 0.08, "lc4": 0.08}


def situational_table(T=None) -> pd.DataFrame:
    """Prior-only EWMA of score-dependent play calling (pass rate when trailing / leading by 7+), per (game_id, team).
    ``T`` (tests only) overrides the team-flow table and bypasses the cache."""
    p = os.path.join(GD.CACHE, "situational.parquet"); override = T is not None
    if os.path.exists(p) and not override:
        return pd.read_parquet(p)
    if T is None:
        G, T, _ = GD.build()
    s = GF.schedule_frame()[["game_id", "week", "gameday"]]
    t = T.merge(s, on="game_id").sort_values(["team", "season", "week", "game_id"]).reset_index(drop=True)
    for k in ("trail7", "lead7"):
        t[f"x_{k}"] = t[f"db_{k}"]; t[f"n_{k}"] = (t[f"db_{k}"] + t[f"dr_{k}"]).astype(float)
    base = t[t.season <= 2005]; pr = {k: base[f"x_{k}"].sum() / max(1, base[f"n_{k}"].sum()) for k in ("trail7", "lead7")}; pn = {k: base[f"n_{k}"].mean() for k in ("trail7", "lead7")}
    K = 4.0
    for k in ("trail7", "lead7"):
        idx, S, N, n = GF._ewma(t, "team", [f"x_{k}", f"n_{k}"], 8.0)
        t.loc[idx, f"pass_{k[:-1] if False else k}"] = (S[:, 0] + pr[k] * K * pn[k]) / (S[:, 1] + K * pn[k])
    t = t.rename(columns={"pass_trail7": "pass_trail", "pass_lead7": "pass_lead"}); t["pass_slope"] = t["pass_trail"] - t["pass_lead"]
    out = t[["game_id", "team", "pass_trail", "pass_lead", "pass_slope"]]
    if not override:
        out.to_parquet(p)
    return out


def frame_for(Y: int) -> pd.DataFrame:
    g = H.build(Y, verbose=lambda *_: None).copy(); sit = situational_table(); new = {}
    for side, tcol in (("h", "home_team"), ("a", "away_team")):
        a = sit.rename(columns={"team": tcol, **{c: f"{side}_{c}" for c in ("pass_trail", "pass_lead", "pass_slope")}})
        g = g.merge(a, on=["game_id", tcol], how="left")
    for c in ("pass_trail", "pass_lead", "pass_slope"):
        new[f"d_{c}"] = g[f"h_{c}"] - g[f"a_{c}"]; new[f"s_{c}"] = g[f"h_{c}"] + g[f"a_{c}"]
    return pd.concat([g, pd.DataFrame(new, index=g.index)], axis=1)


# ---------------------------------------------------------------------------------------------------- drive chain
class DriveChain:
    EDGES_M = [-17, -9, -4, 0.5, 4.5, 9.5, 17.5]; EDGES_S = [-7, -3, 0, 3, 7]
    def __init__(self, drives, flow, Y, min_cell=40):
        gm = flow[(flow.season >= TRAIN_START) & (flow.season < Y)][["game_id", "spread_line", "total_line"]]
        d = drives.merge(gm, on="game_id").dropna(subset=["start", "dur", "m_before", "dm", "dtot"]).reset_index(drop=True); sgn = np.where(d.side == 0, 1.0, -1.0)
        self.q = np.quantile(gm.total_line, [1 / 3, 2 / 3]); self.min_cell = min_cell
        tb = np.clip((d.start // 300).astype(int), 0, 11); mb = np.digitize(sgn * d.m_before, self.EDGES_M); sb = np.digitize(sgn * d.spread_line, self.EDGES_S); t3 = np.digitize(d.total_line, self.q)
        self.keys = [((tb * 8 + mb) * 6 + sb) * 3 + t3, (tb * 8 + mb) * 6 + sb, tb * 8 + mb, tb]
        self.sizes = [12 * 8 * 6 * 3, 12 * 8 * 6, 12 * 8, 12]
        self.vals = np.c_[d.dur.to_numpy(float), (sgn * d.dm).to_numpy(float), d.dtot.to_numpy(float)]
        self.tab = []
        for k, size in zip(self.keys, self.sizes):
            order = np.argsort(k.to_numpy(), kind="stable"); cnt = np.bincount(k.to_numpy(), minlength=size); off = np.r_[0, np.cumsum(cnt)[:-1]]
            self.tab.append((order, cnt, off))

    def draw(self, tb, mb, sb, t3, rng):
        n = len(tb); ks = [((tb * 8 + mb) * 6 + sb) * 3 + t3, (tb * 8 + mb) * 6 + sb, tb * 8 + mb, tb]; idx = np.full(n, -1)
        for lvl, k in enumerate(ks):
            order, cnt, off = self.tab[lvl]; c = cnt[k]; use = (idx < 0) & (c >= self.min_cell)
            pick = off[k][use] + np.minimum((rng.random(use.sum()) * c[use]).astype(int), c[use] - 1); idx[use] = order[pick]
        miss = idx < 0
        if miss.any():
            order, cnt, off = self.tab[3]; c = np.maximum(cnt[ks[3][miss]], 1); idx[miss] = order[np.minimum(off[ks[3][miss]] + (rng.random(miss.sum()) * c).astype(int), len(order) - 1)]
        return self.vals[idx]

    def simulate(self, sp, tl, n=2000, seed=0):
        rng = np.random.default_rng(seed); t3 = int(np.digitize(tl, self.q)); e = np.zeros(n); m = np.zeros(n); tot = np.zeros(n)
        open_side = (rng.random(n) < 0.5).astype(int); side = open_side.copy(); done = np.zeros(n, bool); ht_m = np.full(n, np.nan); ht_t = np.full(n, np.nan); q3_m = np.full(n, np.nan)
        mx_h = np.zeros(n); mx_a = np.zeros(n); sgn_last = np.zeros(n); lc = np.zeros(n); last_score = np.zeros(n); drought = np.zeros(n); drives_h = np.zeros(n); drives_a = np.zeros(n)
        for _ in range(45):
            act = ~done
            if not act.any():
                break
            sgn = np.where(side == 0, 1.0, -1.0); tb = np.clip((e // 300).astype(int), 0, 11); mb = np.digitize(sgn * m, self.EDGES_M); sb = np.digitize(sgn * sp, self.EDGES_S)
            v = self.draw(tb[act], mb[act], sb[act], np.full(act.sum(), t3), rng); dur, dm, dt = v[:, 0], v[:, 1] * sgn[act], v[:, 2]
            ea = e[act]; new_e = ea + np.maximum(dur, 1.0); first = ea < 1800; cross_h = first & (new_e >= 1800); fin = (~first) & (new_e >= 3600)
            new_e = np.where(cross_h, 1800.0, np.where(fin, 3600.0, new_e))
            q3 = (ea < 2700) & (ea + np.maximum(dur, 1.0) > 2700); ia = np.where(act)[0]
            q3_m[ia[q3]] = m[ia[q3]]
            m_new = m[act] + dm; tot_new = tot[act] + dt
            scored = dt > 0; gap = new_e - last_score[act]; drought[ia] = np.maximum(drought[ia], np.where(scored, gap, 0.0)); last_score[ia] = np.where(scored, new_e, last_score[act])
            in_q4 = new_e > 2700; s_new = np.sign(m_new); sl = sgn_last[act]
            lc[ia] += (in_q4 & (s_new != 0) & (sl != 0) & (s_new != sl))
            sgn_last[ia] = np.where(s_new != 0, s_new, sl)
            mx_h[ia] = np.maximum(mx_h[ia], m_new); mx_a[ia] = np.maximum(mx_a[ia], -m_new)
            hom = side[act] == 0; drives_h[ia] += hom; drives_a[ia] += ~hom
            e[ia] = new_e; m[ia] = m_new; tot[ia] = tot_new
            ht_m[ia[cross_h]] = m_new[cross_h]; ht_t[ia[cross_h]] = tot_new[cross_h]
            side[ia] = np.where(cross_h, 1 - open_side[ia], 1 - side[ia]); done[ia[fin]] = True
        # paths that never crossed (data-poor): fill with the final state
        ht_m = np.where(np.isnan(ht_m), m, ht_m); ht_t = np.where(np.isnan(ht_t), tot, ht_t); q3_m = np.where(np.isnan(q3_m), m, q3_m)
        drought = np.maximum(drought, 3600 - last_score)
        win = np.where(m != 0, np.sign(m), np.where(rng.random(n) < 0.5, 1.0, -1.0))
        comeback = ((mx_a >= 10) & (win > 0)) | ((mx_h >= 10) & (win < 0))
        O = np.c_[ht_m, ht_t, np.abs(q3_m) <= 8, np.maximum(mx_h, mx_a) >= 14, comeback, lc >= 1, ht_m >= 7, ht_m <= -7, drought >= 1200, tot - ht_t]
        return O.astype(float), np.full(n, 1.0 / n), float(np.mean(drives_h + drives_a))


def forecast_season(Y, models, flow, drives, verbose=print):
    """Records for every REG game of season Y (with a closing line and reliable reconstruction) for the requested models."""
    g = frame_for(Y); te = flow[flow.season == Y].reset_index(drop=True); fe = g[g.game_id.isin(te.game_id)].set_index("game_id")
    tr = flow[(flow.season >= TRAIN_START) & (flow.season < Y)].reset_index(drop=True); O = tr[OCOLS].to_numpy(float)
    recs = {m: [] for m in models}; ctx = {}
    chain = DriveChain(drives, flow, Y) if any(m.startswith("G4") for m in models) else None
    trg = g.set_index("game_id").reindex(tr.game_id) if any(m[:2] in ("G1", "G2", "G3") for m in models) else None
    for mid in models:
        parts = mid.split("_"); kind = parts[0]; bw = parts[1] if len(parts) > 1 and parts[1] in BW else "b2"
        hs, ht = BW[bw]
        if kind == "GU":                                   # unconditional historical distribution (no market information)
            for sp, tl in zip(te.spread_line, te.total_line):
                ws = 0.5 ** ((Y - tr["season"].to_numpy(float)) / 6.0); recs[mid].append(record_from(O, ws / ws.sum()))
        elif kind == "G0":
            for sp, tl in zip(te.spread_line, te.total_line):
                recs[mid].append(record_from(O, kernel_weights(tr, sp, tl, Y, hs, ht)))
        elif kind in ("G1", "G2", "G3"):
            key = ("loo", bw)
            if key not in ctx:
                ctx[key] = loo_means(tr, hs, ht, Y, RES_TARGETS)
            cols = FAMS[kind]; Xtr = trg[cols].to_numpy(float); Xte = fe.loc[te.game_id, cols].to_numpy(float); s_tr = tr["season"].to_numpy()
            shifts = {}
            for k, tname in enumerate(RES_TARGETS):
                r = tr[tname].to_numpy(float) - ctx[key][:, k]; sh, _ = M.ridge_cv(Xtr, r, s_tr, Xte, lams=(300.0, 3000.0, 30000.0)); shifts[tname] = np.clip(sh, -CLIP[tname], CLIP[tname])
            for i, (sp, tl) in enumerate(zip(te.spread_line, te.total_line)):
                w = kernel_weights(tr, sp, tl, Y, hs, ht); mu = w @ O[:, :6]; tgt = mu + np.array([shifts[t][i] for t in RES_TARGETS])
                tgt[2:] = np.clip(tgt[2:], 0.01, 0.99); q = tilt(O, w, tgt, [0, 1, 2, 3, 4, 5]); recs[mid].append(record_from(O, q))
        elif kind == "G4":
            for i, (sp, tl) in enumerate(zip(te.spread_line, te.total_line)):
                Os, w, _ = chain.simulate(float(sp), float(tl), n=2000, seed=SEED + Y * 1000 + i); recs[mid].append(record_from(Os, w))
        verbose(f"  {Y} {mid} done")
    out = {}
    for mid, rs in recs.items():
        out[mid] = {"game_id": te.game_id.to_numpy(), "pm": np.stack([r["pm"] for r in rs]), "pt": np.stack([r["pt"] for r in rs]), "pe": np.stack([r["pe"] for r in rs]), "mh2": np.array([r["mh2"] for r in rs])}
    return out


def run(models, seasons, verbose=print):
    os.makedirs(RES, exist_ok=True); flow = flow_table(); drives = pd.read_parquet(os.path.join(GD.CACHE, "drives.parquet"))
    for Y in seasons:
        out = forecast_season(Y, models, flow, drives, verbose)
        for mid, r in out.items():
            np.savez_compressed(os.path.join(RES, f"{mid}_{Y}.npz"), **r)
