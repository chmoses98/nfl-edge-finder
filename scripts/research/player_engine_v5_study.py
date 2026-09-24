#!/usr/bin/env python3
"""Player Engine v5: does a point-in-time, availability-aware starting quarterback help V4's structure?

HISTORICAL_RESEARCH, the V4 protocol (scripts/research/player_engine_v4_study.py) with one question added: what
changes when the projected starter is resolved from what was known at the cutoff instead of read off the chart?

    held out    2025 regular season, Kalshi player-prop rungs (every model fitted on seasons <= 2024)
                2026 week 2, the Shadow v2 research export's MARKET_PLAYER_DIST rows (fitted on seasons <= 2025,
                with 2026 week 1 as completed current-season history). 2026 week 1 has no published research
                export, so it is not replayed.
    horizons    2025: T-24h, T-6h, T-90m, T-0 (anchor = the backfill's kickoff); 2026: T-24h, T-6h, T-90m (the
                records' own cutoffs)
    environment 2025: that horizon's Kalshi-implied spread / total (V4 study); 2026: the game centre frozen on the
                records at that horizon. No closing line anywhere.
    benchmark   the monotone market midpoint (width <= 10c), paired Brier / log loss, clustered by GAME.

Arms (all on the SAME rows; "common" = every arm priced the rung):
    V3        DATA_PLAYER_V3, `qb_starter` = chart QB1 at the cutoff (what production runs)
    V4        DATA_PLAYER_V4, `qb_starter` = chart QB1 at the cutoff (what production runs)
    V5        DATA_PLAYER_V5, `qb_starter` and the QB-identity features from the point-in-time resolution
    V4_ORACLE V4 with the REALISED starter (the V4 study's setup; it knows who started, which no pregame model can).
              Reported as a ceiling for "knowing the quarterback", never as a model.
    market    the monotone midpoint

Point in time, per (team, game, horizon): the chart is the newest nflverse ESPN chart scraped at or before the
cutoff (DepthChartBook). The availability evidence is the week's nflverse injury report (report_status) and the
week's weekly-roster status (IR / PUP / suspended / non-football -> out; gameday INA is excluded), exactly the
statuses the V4 study treats as pregame for every teammate. They carry no timestamp inside the file, so they are
treated as known at every horizon -- the same assumption V4's teammate-status features make, and stated in the
results. No official inactive list exists for these seasons, so no promotion is HIGH certainty. The realised
starter is used only to SCORE the resolution (how often chart / V5 named the actual starter), never as an input.

    python3 scripts/research/player_engine_v5_study.py --market-data <md> --frame <frame.pkl> --research-2026 <dir>

Outputs research/player_engine_v5/results.json (aggregates only).
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import time
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "research"))
from nfl_edge.context import qb_resolution as QR                         # noqa: E402
from nfl_edge.context.role import DepthChartBook                         # noqa: E402
from nfl_edge.engines.player import data_dist as DD                      # noqa: E402
from nfl_edge.engines.player.dist import LatticeDistribution             # noqa: E402
from nfl_edge.engines.player.v4 import features as F4                    # noqa: E402
from nfl_edge.engines.player.v4 import model as M                        # noqa: E402
from nfl_edge.engines.player.v4.volume import QB_TEAM_COLS, team_game_table  # noqa: E402
from nfl_edge.engines.player.v5 import model as M5                       # noqa: E402
from nfl_edge.engines.player.v5 import qb_features as QF                 # noqa: E402
from nfl_edge.research import player_distributions as pdist              # noqa: E402
import player_engine_v3_study as V3S                                     # noqa: E402
import player_engine_v4_study as V4S                                     # noqa: E402

OFFSETS = {"T-24h": timedelta(hours=24), "T-6h": timedelta(hours=6), "T-90m": timedelta(minutes=90), "T-0": timedelta(0)}
STATS = ["passing_yards", "rushing_yards", "receiving_yards", "receptions", "passing_tds", "touchdowns"]
ARMS = ("V3", "V4", "V5", "V4_ORACLE")


# ------------------------------------------------------------------------------------------------ point-in-time QB
def qb_chart_frame(season: int) -> pd.DataFrame:
    p = os.path.join(ROOT, "data/raw/nflverse/depth_charts", f"depth_charts_{season}.parquet")
    d = pd.read_parquet(p)
    return d[(d.pos_abb == "QB") & d.gsis_id.notna() & d.dt.notna()].reset_index(drop=True)


class ChartCache:
    """QB chart order per team at a cutoff: newest scrape at or before it (DepthChartBook), cached by cutoff."""

    def __init__(self, season):
        self.d = qb_chart_frame(season)
        self.cache = {}

    def at(self, cutoff: datetime):
        k = cutoff.strftime("%Y-%m-%dT%H:%M:%SZ")
        if k not in self.cache:
            b = DepthChartBook.from_frame(self.d, cutoff)
            self.cache[k] = {t: ([e.gsis_id for e in g.get("QB", [])], b.vintage.get(t)) for t, g in b.by_team.items()}
        return self.cache[k]


def status_evidence(season: int) -> tuple[dict, set]:
    """(week, team) -> [QbEvidence] from the week's injury report and weekly roster; and the team-weeks covered."""
    fr = F4.status_frame(ROOT, [season])
    ev, known = defaultdict(list), set()
    for s, w, t, p, rep, ros in fr[["season", "week", "team", "player_id", "report", "roster"]].itertuples(index=False):
        known.add((int(w), t))
        if isinstance(rep, str) and rep:
            ev[(int(w), t)].append(QR.QbEvidence(p, rep, QR.SRC_INJURY_REPORT, None))
        if isinstance(ros, str) and ros in F4.ROSTER_OUT:
            ev[(int(w), t)].append(QR.QbEvidence(p, ros, QR.SRC_AVAILABILITY, None))
    return ev, known


def resolve_all(team_games, kick: dict, charts: ChartCache, evidence, known, horizons, cutoffs=None) -> dict:
    """(horizon, team, game) -> resolution. `cutoffs` overrides kickoff - offset per (game, horizon) (2026 records)."""
    out = {}
    for team, gid, week in team_games:
        ko = kick.get(gid)
        if ko is None:
            continue
        for h in horizons:
            cut = (cutoffs or {}).get((gid, h)) or (ko - OFFSETS[h])
            qbs, vint = charts.at(cut).get(team, ([], None))
            out[(h, team, gid)] = QR.resolve_team_qb(team=team, chart_qbs=qbs, cutoff=cut, kickoff=ko, chart_vintage=vint,
                                                     evidence=evidence.get((int(week), team), []), status_known=(int(week), team) in known)
    return out


# ------------------------------------------------------------------------------------------------ arms
def fit_v3(frame, target, stats):
    out = {}
    for stat in stats:
        out[stat] = DD.fit_stat(frame, stat, DD.DEFAULT_FAMILY[DD.STATS.get(stat, stat)], "v3", target)
    return out


def v3_apply(models, rows_by_h, keys):
    out = {}
    for stat, m in models.items():
        for h, rows in rows_by_h.items():
            want = rows[rows.env_known]
            sub = want[pdist.population_mask(want, m.spec.pop)]
            sub = sub[[(p, g, stat) in keys for p, g in zip(sub.player_id, sub.game_id)]]
            if not len(sub):
                continue
            F, _ = m.cdf_grid(sub)
            for j, (p, g) in enumerate(zip(sub.player_id, sub.game_id)):
                out[(p, g, stat, h)] = LatticeDistribution.from_cdf(F[j])
    return out


def with_starters(rows, starters):
    """qb_starter from a {(team, game): gsis} map (rows of games not in the map: no starter)."""
    r = rows.copy()
    q = pd.Series([starters.get((t, g)) for t, g in zip(r.team, r.game_id)], index=r.index, dtype=object)
    r["qb_starter"] = (r.player_id == q) & q.notna()
    return r


def teams_with_env(base_teams, rows):
    env = rows.drop_duplicates(["team", "game_id"])[["team", "game_id", "implied_total", "spread_team"]]
    return base_teams.drop(columns=["implied_total", "spread_team"]).merge(env, on=["team", "game_id"], how="left")


def replay(label, frame, target, te, rungs, market, envs_fn, horizons, kick, charts, evidence, known, cutoffs=None, log=print):
    """One held-out window -> aggregates."""
    t0 = time.time()
    keys = {(r["player_id"], r["game_id"], r["stat"]) for r in rungs}
    team_games = sorted({(t, g, int(w)) for t, g, w in zip(te.team, te.game_id, te.week)})
    res = resolve_all(team_games, kick, charts, evidence, known, horizons, cutoffs)
    real = QF.realised_starters(frame)
    rows0 = {h: envs_fn(te, h) for h in horizons}
    chart_st = {h: {(t, g): (res.get((h, t, g)) or {}).get("depth_chart_qb1") for t, g, _ in team_games} for h in horizons}
    v5_st = {h: {(t, g): (res.get((h, t, g)) or {}).get("effective_projected_qb") for t, g, _ in team_games} for h in horizons}
    rows_chart = {h: with_starters(rows0[h], chart_st[h]) for h in horizons}
    log(f"[{label}] {len(team_games)} team-games resolved x {len(horizons)} horizons; {time.time() - t0:.0f}s")
    # ---- V3 (chart QB1) and V4 (chart QB1, and the realised-starter oracle)
    d3 = v3_apply(fit_v3(frame, target, sorted({k[2] for k in keys})), rows_chart, keys)
    base_teams = team_game_table(frame)
    b4 = M.fit_bundle(frame, target, teams=base_teams, verbose=lambda *a: None)
    d4, _ = V4S.v4_dists(b4, {h: teams_with_env(base_teams, rows0[h]) for h in horizons}, rows_chart, keys, horizons=horizons)
    d4o, _ = V4S.v4_dists(b4, {h: teams_with_env(base_teams, rows0[h]) for h in horizons}, rows0, keys, horizons=horizons)
    log(f"[{label}] v3 / v4 priced; {time.time() - t0:.0f}s")
    # ---- V5: fitted on realised QB identity (training rows only), applied with the resolved starter per horizon
    f5 = QF.add_qb_identity_features(frame)
    teams5 = team_game_table(f5)
    b5 = M5.fit_bundle(f5, target, teams=teams5, verbose=lambda *a: None)
    tg_keys = {(t, g) for t, g, _ in team_games}
    d5, inter5 = {}, {}
    for h in horizons:
        feats = QF.team_game_qb_features(frame, {k: v for k, v in v5_st[h].items() if k in tg_keys})
        feats = feats[[k in tg_keys for k in zip(feats.team, feats.game_id)]]
        r5 = with_starters(rows0[h].drop(columns=[c for c in QF.QB_ID_COLS if c in rows0[h].columns]), v5_st[h])
        r5 = r5.merge(feats, on=["team", "game_id"], how="left")
        t5 = teams_with_env(teams5, rows0[h]).set_index(["team", "game_id"])
        fi = feats.set_index(["team", "game_id"])
        for c in QB_TEAM_COLS:
            t5.loc[fi.index.intersection(t5.index), c] = fi.loc[fi.index.intersection(t5.index), c]
        dd, ii = V4S.v4_dists(b5, {h: t5.reset_index()}, {h: r5}, keys, horizons=[h])
        d5.update(dd); inter5.update(ii)
    log(f"[{label}] v5 priced; {time.time() - t0:.0f}s")
    R = V4S.score(rungs, market, {"V3": d3, "V4": d4, "V5": d5, "V4_ORACLE": d4o})
    R = R[R.horizon.isin(horizons)].reset_index(drop=True)
    team_of = dict(zip(zip(te.player_id, te.game_id), te.team))
    R["team"] = [team_of.get((p, g)) for p, g in zip(R.player_id, R.game_id)]
    reason = [(res.get((h, t, g)) or {}).get("qb_resolution_reason") for h, t, g in zip(R.horizon, R.team, R.game_id)]
    R["qb_reason"] = reason
    R["qb_swapped"] = R.qb_reason == QR.QB1_OUT_PROMOTED_NEXT
    R["qb_abstain"] = [bool((res.get((h, t, g)) or {}).get("qb_dependent_abstain")) and QR.is_qb_dependent(s, _pos(frame, p))
                       for h, t, g, s, p in zip(R.horizon, R.team, R.game_id, R.stat, R.player_id)]
    R["common"] = R[list(ARMS)].notna().all(axis=1)
    R["common_345"] = R[["V3", "V4", "V5"]].notna().all(axis=1)
    return summarize(label, R, res, real, team_games, horizons, t0)


_POS = {}


def _pos(frame, pid):
    if not _POS:
        _POS.update(dict(zip(frame.player_id, frame.position)))
    return _POS.get(pid)


def summarize(label, R, res, real, team_games, horizons, t0):
    P = V4S.paired
    out = {"window": label, "horizons": horizons}
    # ---- the resolution itself (per horizon), scored against the realised starter (evaluation only)
    qb = {}
    for h in horizons:
        c = Counter(); chart_ok = v5_ok = n = 0; swaps = []
        for t, g, _ in team_games:
            r = res.get((h, t, g))
            if not r:
                continue
            n += 1
            c[r["qb_resolution_reason"]] += 1
            a = real.get((t, g))
            chart_ok += int(a is not None and r["depth_chart_qb1"] == a)
            v5_ok += int(a is not None and r["effective_projected_qb"] == a)
            if r["qb_resolution_reason"] == QR.QB1_OUT_PROMOTED_NEXT:
                swaps.append({"team": t, "game_id": g, "chart_qb1": r["depth_chart_qb1"], "effective": r["effective_projected_qb"],
                              "certainty": r["qb_resolution_certainty"], "effective_was_actual_starter": r["effective_projected_qb"] == a})
        qb[h] = {"team_games": n, "by_reason": dict(c), "chart_qb1_was_actual_starter": chart_ok, "v5_qb_was_actual_starter": v5_ok,
                 "substitutions": len(swaps), "substitutions_correct": sum(s["effective_was_actual_starter"] for s in swaps),
                 "abstained_team_games": sum(1 for (hh, t, g), r in res.items() if hh == h and r.get("qb_dependent_abstain")),
                 "substitution_list": swaps}
    out["qb_resolution"] = qb
    # ---- headline per horizon: common rows (every arm priced) and V3/V4/V5-common rows
    out["by_horizon"] = {}
    for h in horizons:
        T = R[R.horizon == h]
        out["by_horizon"][h] = {"common_all_arms": {a: P(T[T.common], a) for a in ARMS},
                                "common_v3_v4_v5": {a: P(T[T.common_345], a) for a in ("V3", "V4", "V5")},
                                "V5_vs_V4": P(T[T.common_345], "V5", "V4"), "V5_vs_V3": P(T[T.common_345], "V5", "V3"),
                                "coverage": {"rows": int(len(T)), **{a: int(T[a].notna().sum()) for a in ARMS},
                                             "v5_only_rows": int((T.V5.notna() & T.V4.isna()).sum()),
                                             "player_games": {a: int(T[T[a].notna()][["player_id", "game_id"]].drop_duplicates().shape[0]) for a in ARMS},
                                             "games": {a: int(T[T[a].notna()].game_id.nunique()) for a in ARMS}}}
    H = "T-90m"
    T = R[R.horizon == H]
    out["by_stat_T90"] = {s: {"common_v3_v4_v5": {a: P(T[(T.stat == s) & T.common_345], a) for a in ("V3", "V4", "V5")},
                              "V5_vs_V4": P(T[(T.stat == s) & T.common_345], "V5", "V4"),
                              "V5_all_rows": P(T[T.stat == s], "V5")} for s in sorted(T.stat.unique())}
    # ---- the rows the resolution changed: teams whose chart QB1 was replaced at this horizon
    S = R[R.qb_swapped]
    out["substituted_team_rows"] = {h: {"V5": P(S[(S.horizon == h)], "V5"), "V4": P(S[(S.horizon == h)], "V4"),
                                        "V3": P(S[(S.horizon == h)], "V3"), "V4_ORACLE": P(S[(S.horizon == h)], "V4_ORACLE"),
                                        "V5_vs_V4_common": P(S[(S.horizon == h) & S.V4.notna()], "V5", "V4"),
                                        "rows": int((S.horizon == h).sum()), "v5_rows": int(((S.horizon == h) & S.V5.notna()).sum()),
                                        "v4_rows": int(((S.horizon == h) & S.V4.notna()).sum()),
                                        "games": int(S[S.horizon == h].game_id.nunique()),
                                        "by_stat": {s: {"V5": P(S[(S.horizon == h) & (S.stat == s)], "V5"),
                                                        "n_v5": int(((S.horizon == h) & (S.stat == s) & S.V5.notna()).sum()),
                                                        "n_v4": int(((S.horizon == h) & (S.stat == s) & S.V4.notna()).sum())}
                                                    for s in sorted(S.stat.unique())}}
                                    for h in horizons}
    A = R[R.qb_abstain]
    out["qb_abstained_rows"] = {h: {"rows": int((A.horizon == h).sum()), "V5": P(A[A.horizon == h], "V5"),
                                    "games": int(A[A.horizon == h].game_id.nunique())} for h in horizons}
    # everything else: rows on teams whose QB was NOT re-resolved (the refit's effect alone)
    U = R[~R.qb_swapped & ~R.qb_abstain & R.common_345]
    out["unchanged_team_rows"] = {h: {"V5_vs_V4": P(U[U.horizon == h], "V5", "V4"), "V5": P(U[U.horizon == h], "V5"),
                                      "V4": P(U[U.horizon == h], "V4")} for h in horizons}
    # calibration (T-90m, common V3/V4/V5 rows): reliability by decile
    C = T[T.common_345]
    out["calibration_T90"] = {}
    for a in ("V3", "V4", "V5", "market_mono"):
        p = np.clip(C[a].to_numpy(float), 1e-4, 1 - 1e-4); y = C.y.to_numpy(float)
        idx = np.minimum((p * 10).astype(int), 9)
        out["calibration_T90"][a] = {"ece": V4S.ece(p, y) if len(p) else None,
                                     "bins": [{"bin": b, "n": int((idx == b).sum()), "p_mean": float(p[idx == b].mean()), "y_mean": float(y[idx == b].mean())}
                                              for b in range(10) if (idx == b).any()]}
    out["runtime_s"] = round(time.time() - t0, 1)
    return out


# ------------------------------------------------------------------------------------------------ 2026 week 2
def load_2026(research_dir: str):
    cols = ["model_arm", "ticker", "subject_id", "stat_family", "threshold", "operator", "horizon_label", "h_yes_bid", "h_yes_ask",
            "settled_yes", "game_id", "week", "kickoff_utc", "generated_at", "game_spread_center_home", "game_total_center", "evidence_class"]
    parts = [pd.read_parquet(p, columns=cols) for p in sorted(glob.glob(os.path.join(research_dir, "2026_wk02.research*.parquet")))]
    a = pd.concat(parts, ignore_index=True)
    m = a[(a.model_arm == "MARKET_PLAYER_DIST") & a.horizon_label.isin(["T-24h", "T-6h", "T-90m"]) & (a.evidence_class == "PROSPECTIVE_FROZEN")
          & a.settled_yes.notna() & a.stat_family.isin(STATS) & a.threshold.notna() & a.subject_id.notna()]
    m = m.drop_duplicates(["ticker", "horizon_label"])
    rungs = defaultdict(lambda: None)
    for r in m.itertuples():
        k = float(r.threshold) if r.operator == ">=" else float(np.floor(r.threshold) + 1.0)
        key = r.ticker
        if rungs[key] is None:
            rungs[key] = {"ticker": r.ticker, "game_id": r.game_id, "week": int(r.week), "player_id": r.subject_id, "stat": r.stat_family,
                          "k": k, "y": float(r.settled_yes), "snaps": {h: None for h in V3S.HORIZONS}}
        rungs[key]["snaps"][r.horizon_label] = {"bid": r.h_yes_bid, "ask": r.h_yes_ask}
    envs, cutoffs, kick = {}, {}, {}
    for (g, h), sub in m.groupby(["game_id", "horizon_label"]):
        sp, tt = sub.game_spread_center_home.median(), sub.game_total_center.median()
        if pd.notna(sp) and pd.notna(tt):
            envs[(g, h)] = {"spread": float(sp), "total": float(tt)}
        cutoffs[(g, h)] = datetime.fromisoformat(str(sub.generated_at.min()).replace("Z", "+00:00"))
        kick[g] = datetime.fromisoformat(str(sub.kickoff_utc.iloc[0]).replace("Z", "+00:00"))
    return [v for v in rungs.values() if v], envs, cutoffs, kick


def kickoffs_2025(md_root) -> dict:
    kick = {}
    for f in glob.glob(os.path.join(md_root, "data/kalshi/backfill/horizons/*.jsonl")):
        for line in open(f):
            r = json.loads(line)
            if str(r.get("season")) == "2025" and r.get("anchor_kind") == "kickoff" and r.get("anchor_ts") and r.get("game_id"):
                kick.setdefault(r["game_id"], datetime.fromtimestamp(int(r["anchor_ts"]), tz=timezone.utc))
    return kick


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default=os.environ.get("NFL_EDGE_MARKET_DATA", "/tmp/md"))
    ap.add_argument("--frame", default="/tmp/pe4/frame.pkl")
    ap.add_argument("--research-2026", default=None, help="directory holding 2026_wk02.research*.parquet (market-data data/shadow/v2/research)")
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "player_engine_v5"))
    a = ap.parse_args()
    t0 = time.time()
    V3S.MD_ROOT = a.market_data
    frame = pd.read_pickle(a.frame)
    out = {"protocol": {"train": "2025 window: seasons 2014-2024; 2026 window: seasons 2014-2025 (+ 2026 week 1 as history)",
                        "test": "2025 weeks 1-18 Kalshi player rungs; 2026 week 2 Shadow v2 MARKET_PLAYER_DIST rows (prospective, settled)",
                        "environment": "2025: per-horizon Kalshi-implied spread/total; 2026: the frozen game centre on the records",
                        "benchmark": "monotone market midpoint (width <= 10c)", "cluster": "game",
                        "qb_evidence": "newest ESPN chart scraped <= cutoff; the week's nflverse injury report + weekly roster (untimestamped, "
                                       "treated as known at every horizon, as V4's teammate statuses are); no official inactives exist for these seasons",
                        "stats": STATS}}
    # ---------------- 2025 held out
    rungs = V3S.load_rungs()
    market = V3S.market_table(rungs)
    envs = V4S.horizon_environments(a.market_data)
    te = frame[frame.season == 2025]
    ev, known = status_evidence(2025)
    out["2025"] = replay("2025", frame, 2025, te, rungs, market, lambda rows, h: V4S.with_env(rows, envs, h), ["T-24h", "T-6h", "T-90m", "T-0"],
                         kickoffs_2025(a.market_data), ChartCache(2025), ev, known)
    print(json.dumps(out["2025"]["by_horizon"]["T-90m"], default=str)[:2500], flush=True)
    # ---------------- 2026 week 2
    if a.research_2026:
        r26, env26, cut26, kick26 = load_2026(a.research_2026)
        m26 = V3S.market_table(r26)
        te26 = frame[(frame.season == 2026) & (frame.week == 2)]
        ev26, known26 = status_evidence(2026)
        out["2026_wk02"] = replay("2026_wk02", frame[(frame.season < 2026) | (frame.week <= 2)], 2026, te26, r26, m26,
                                  lambda rows, h: V4S.with_env(rows, env26, h), ["T-24h", "T-6h", "T-90m"], kick26, ChartCache(2026),
                                  ev26, known26, cutoffs=cut26)
        print(json.dumps(out["2026_wk02"]["qb_resolution"], default=str)[:2500], flush=True)
    out["runtime_s"] = round(time.time() - t0, 1)
    os.makedirs(a.out, exist_ok=True)
    json.dump(out, open(os.path.join(a.out, "results.json"), "w"), indent=1, default=str)


if __name__ == "__main__":
    main()
