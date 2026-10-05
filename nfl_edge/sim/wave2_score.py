"""Wave-2 PROSPECTIVE scorer. RESEARCH_ONLY -- nothing here, and nothing it writes, has any authority.

Implements research/game_script_v2/wave2/PROSPECTIVE_PROTOCOL.md against the gates and minimum samples frozen in
PREREGISTRATION.md (section 7) and PREREGISTRATION_ADDENDUM.md (A.2, A.3). Committed, with tests on synthetic
records, BEFORE any Wave-2 prospective record existed; after the first real record is scored the metric code here is
frozen (I/O fixes allowed and logged; a metric change is a DEVIATION).

Pipeline (pure functions; the I/O lives in scripts/sim/wave2_score.py):

  candidates()      every (game, window) record found, each either valid or carrying an exclusion reason
  select()          per game the LAST valid pre-kickoff record, LATE preferred over EARLY; never reconstructed
  player_frame()    the incumbent A0's scored rows (A0 predictive mean >= backtest.FLOORS) with every arm's metrics
                    computed from the STORED pregame distributions on exactly those rows
  margin_frame()    M0 vs M1 game metrics from the stored margin / total pmfs and cell probabilities
  score()           per-arm sample sizes, (interim-only) metrics, and -- once an arm's analysis set reaches its frozen
                    minimum -- the preregistered gate on the FIRST minimum-many eligible games in kickoff order

Interpretations fixed here, before any prospective record existed (no outcome can have influenced them):
  * Analysis set: an arm's gate is evaluated ONCE, on its first N_min eligible games ordered by (kickoff, game_id);
    later games are reported as DESCRIPTIVE and never re-run the gate (no optional stopping).
  * "Interval excluding zero" = the 95% percentile interval of 2,000 game-clustered resamples (seed 20261005).
  * Non-inferiority "+0.5% relative bound" = the interval's upper bound of (sum candidate / sum incumbent - 1) <= 0.005.
  * Mechanism checks need the randomized PIT, which the records define only for pmf statistics; a statistic whose
    PIT is not defined counts as NOT passing (S1: chi-square must fall for >= 3 of the 5, yardage counts as not falling).
  * A candidate row missing for an A0-population row, or an arm's coherence flag false, is an INTEGRITY failure of
    that game: the game stays in N and the arm's "zero coherence failures" gate fails. Rows are never dropped quietly.
  * Count-statistic pmfs are stored rounded to 5 decimals; they are renormalised to sum to one before use.
"""
from __future__ import annotations

import gzip
import hashlib
import json
from datetime import datetime

import numpy as np
import pandas as pd

from . import backtest as Bt
from . import baseline_report as BR
from . import script_v2 as V
from . import wave2_eval as E
from .risk1 import PROSPECTIVE_CUTOFF

SCORER_VERSION = "wave2-score-1.0.0"
B, SEED = 2000, 20261005
WINDOWS = ("EARLY", "LATE")
ACCEPTED_RECORD_VERSIONS = ("wave2-prospective-1.1.0",)
FROZEN_COMPONENTS_SHA256 = "353541d18e7e77f4cb06de4233f1b33ef0ff9772941c7792044f55a936ea7008"   # addendum A.4
DEV_STATUS = {"S1": "PROSPECTIVE_CHALLENGER", "A1": "PROSPECTIVE_CHALLENGER", "M1": "PROSPECTIVE_CHALLENGER",
              "Q1": "REJECTED_AT_DEVELOPMENT", "RISK1": "COLLECTING"}                         # addendum A.2
MIN_GAMES = {"S1": 64, "A1": 64, "M1": 672, "RISK1": 397}                                     # addendum A.3
NI_MARGIN = 0.005
LOGO_MAX_SHARE = 0.10
PMF_STATS = ("carries", "targets", "receptions", "attempts", "completions", "pass_td", "any_td")
YARD_STATS = ("rush_yards", "rec_yards", "pass_yards")
PLAYER_STATS = PMF_STATS + YARD_STATS
PLAYER_ARMS = ("S1", "Q1", "A1")
A1_STATS = ("carries", "targets")
A1_TEAMMATE_STATS = ("carries", "targets", "receptions", "rec_yards", "rush_yards")
AUTHORITY = {"research_only": True, "betting_authority": "NONE", "staking_authority": "NONE", "bet_pass_authority": "NONE",
             "price_limit_authority": "NONE", "unit_size_authority": "NONE", "reconciliation_weight_authority": "NONE",
             "model_probability_authority": "NONE"}


def _ts(x) -> datetime:
    t = datetime.fromisoformat(str(x).replace("Z", "+00:00"))
    if t.tzinfo is None:
        raise ValueError(f"timezone-naive instant {x!r}")
    return t


# ------------------------------------------------------------------------------------------ records
def read_record(path: str) -> dict:
    """Read one record file WITHOUT modifying it; returns the parsed document and the sha256 of its bytes."""
    with open(path, "rb") as f:
        raw = f.read()
    return {"path": path, "sha256": hashlib.sha256(raw).hexdigest(), "doc": json.loads(gzip.decompress(raw))}


def parse_name(path: str):
    """<game_id>.<window>.<run_id>.wave2.json.gz -> (game_id, window, run_id) or None."""
    parts = path.replace("\\", "/").split("/")[-1].split(".")
    if len(parts) >= 5 and parts[1] in WINDOWS and parts[-3:] == ["wave2", "json", "gz"]:
        return parts[0], parts[1], parts[2]
    return None


def _schema_problem(g: dict) -> str | None:
    arms = g.get("arms") or {}
    for arm in ("A0", "S1", "Q1", "A1", "M1"):
        if arm not in arms:
            return f"arm {arm} missing"
    if "avail_state" not in g or "m1k_exact_margin_pmf" not in g:
        return "record schema incomplete (avail_state / m1k_exact_margin_pmf)"
    for arm in ("A0", "M1"):
        if not all(k in arms[arm] for k in ("margin_pmf", "total_pmf", "v2_cells")):
            return f"record schema incomplete ({arm} margin / total pmf or cells)"
    if not g.get("home_team") or not g.get("away_team"):
        return "record schema incomplete (teams)"
    return None


def candidates(records: list, kickoffs: dict | None = None, cutoff: str = PROSPECTIVE_CUTOFF) -> list:
    """One entry per (record file, game) with `reason` None when usable. `kickoffs` (game_id -> ISO instant from the
    schedule) is checked as well as the record's own kickoff; the EARLIER of the two is the kickoff used."""
    pc = _ts(cutoff)
    out = []
    for r in records:
        doc, nm = r["doc"], parse_name(r["path"])
        for gid, g in (doc.get("games") or {}).items():
            c = {"path": r["path"], "sha256": r["sha256"], "game_id": gid, "window": g.get("window"),
                 "generated_at": doc.get("generated_at"), "cutoff": g.get("cutoff") or doc.get("cutoff"),
                 "kickoff_utc": g.get("kickoff_utc"), "horizon": g.get("horizon"), "rec": g, "doc_meta": {
                     k: doc.get(k) for k in ("wave2_version", "run_id", "season", "week", "versions", "inputs")}, "reason": None}
            reason = None
            ko = None
            try:
                kos = [_ts(x) for x in (g.get("kickoff_utc"), (kickoffs or {}).get(gid)) if x]
                ko = min(kos) if kos else None
            except ValueError as e:
                reason = f"bad kickoff instant: {e}"
            if reason is None:
                if nm is None or nm[0] != gid or nm[1] != g.get("window"):
                    reason = "file name does not match its content (game / window)"
                elif doc.get("research_only") is not True or doc.get("betting_authority") != "NONE":
                    reason = "record does not declare research_only / betting_authority NONE"
                elif doc.get("dry_run"):
                    reason = "dry-run record"
                elif doc.get("wave2_version") not in ACCEPTED_RECORD_VERSIONS:
                    reason = f"record version {doc.get('wave2_version')} not accepted by {SCORER_VERSION}"
                elif g.get("window") not in WINDOWS:
                    reason = "unknown window"
                elif g.get("state") != "OK":
                    reason = f"capture state {g.get('state')}"
                elif ko is None:
                    reason = "no kickoff instant"
                elif ko <= pc:
                    reason = "game kicked off before the PROSPECTIVE CUTOFF"
                elif not doc.get("generated_at") or _ts(doc["generated_at"]) >= ko:
                    reason = "generated at or after kickoff"
                elif not c["cutoff"] or _ts(c["cutoff"]) >= ko:
                    reason = "feature cutoff at or after kickoff"
                elif (doc.get("inputs") or {}).get("components_sha256") != FROZEN_COMPONENTS_SHA256:
                    reason = "components differ from the frozen components (addendum A.4)"
                else:
                    reason = _schema_problem(g)
            c["reason"] = reason
            c["kickoff"] = ko.isoformat() if ko is not None else None
            out.append(c)
    return out


def select(cands: list) -> tuple[dict, list]:
    """Per game: the last valid record generated before kickoff, LATE preferred over EARLY. Returns
    (game_id -> selected candidate, superseded valid candidates). Nothing is reconstructed: a game with no valid
    record is simply absent."""
    by = {}
    for c in cands:
        if c["reason"] is None:
            by.setdefault(c["game_id"], []).append(c)
    sel, superseded = {}, []
    for gid, cs in by.items():
        late = [c for c in cs if c["window"] == "LATE"]
        pool = late or [c for c in cs if c["window"] == "EARLY"]
        best = max(pool, key=lambda c: (_ts(c["generated_at"]), c["path"]))
        sel[gid] = best
        superseded += [c for c in cs if c is not best]
    return sel, superseded


# ------------------------------------------------------------------------------------------ distributions
def dense_pmf(d: dict, size: int) -> np.ndarray:
    """A stored {lo, p} pmf as a dense, renormalised vector on 0..size-1 (mass above the grid folded onto its top)."""
    p = np.zeros(size)
    lo = int(d["lo"])
    for k, v in enumerate(d["p"]):
        p[min(lo + k, size - 1)] += float(v)
    s = p.sum()
    if s <= 0:
        raise ValueError("empty pmf")
    return p / s


def pmf_quantiles(p: np.ndarray, levels: np.ndarray = Bt.QLEVELS) -> np.ndarray:
    """Generalised inverse CDF of an integer pmf at the stored quantile levels."""
    cdf = np.cumsum(p)
    return np.searchsorted(cdf, levels - 1e-12, side="left").clip(0, len(p) - 1).astype(float)


def _player_dist(arm_rec: dict, pid: str, stat: str):
    """(mean, quantiles at QLEVELS, dense pmf or None) from the stored record; None if absent."""
    pl = (arm_rec.get("players") or {}).get(pid)
    if pl is None or stat not in pl:
        return None
    d = pl[stat]
    if stat in PMF_STATS:
        pm = dense_pmf(d, Bt.STAT_GRID[stat] + 1)
        return float((np.arange(len(pm)) * pm).sum()), pmf_quantiles(pm), pm
    q = np.asarray(d["q"], float)
    if len(q) != len(Bt.QLEVELS):
        return None
    return float(d["mean"]), q, None


# ------------------------------------------------------------------------------------------ outcomes
def outcome_ok(o: dict | None) -> bool:
    return bool(o) and o.get("status") == "FINAL"


def player_actual(o: dict, pid: str, stat: str) -> float:
    """Backtest semantics: a player absent from a FINAL box score recorded zero."""
    return float(((o.get("players") or {}).get(pid) or {}).get(stat, 0.0) or 0.0)


# ------------------------------------------------------------------------------------------ player rows
def player_frame(sel: dict, outcomes: dict) -> tuple[pd.DataFrame, dict]:
    """The A0 population (A0 mean >= floor) of every selected game with a FINAL outcome; for each candidate arm its
    metrics on exactly those rows. Returns (frame, integrity) where integrity[arm][game] lists missing rows."""
    rows, integrity = [], {a: {} for a in PLAYER_ARMS}
    for gid in sorted(sel):
        c = sel[gid]; o = outcomes.get(gid)
        if not outcome_ok(o):
            continue
        rec = c["rec"]; a0 = rec["arms"]["A0"]
        avail = rec.get("avail_state") or {}
        q_teams = {(a0["players"].get(p) or {}).get("team") for p, st in avail.items() if st == "QUESTIONABLE"} - {None}
        for pid in sorted(a0.get("players") or {}):
            team = a0["players"][pid].get("team")
            for st in PLAYER_STATS:
                d0 = _player_dist(a0, pid, st)
                if d0 is None or d0[0] < Bt.FLOORS.get(st, 0.0):
                    continue
                row = {"game_id": gid, "kickoff": c["kickoff"], "horizon": c["horizon"], "team": team, "player_id": pid,
                       "stat": st, "avail_state": avail.get(pid), "team_has_q": team in q_teams, "actual": player_actual(o, pid, st),
                       "a0_mean": d0[0], "a0_q": d0[1], "a0_pmf": d0[2]}
                for arm in PLAYER_ARMS:
                    d = _player_dist(rec["arms"][arm], pid, st)
                    if d is None:
                        integrity[arm].setdefault(gid, []).append(f"{pid}:{st}")
                        row[f"{arm}_ok"] = False
                        continue
                    row[f"{arm}_ok"] = True
                    row[f"{arm}_mean"], row[f"{arm}_q"], row[f"{arm}_pmf"] = d
                rows.append(row)
    return pd.DataFrame(rows), integrity


PAIRED_COLUMNS = ["game_id", "kickoff", "horizon", "team", "player_id", "stat", "avail_state", "team_has_q", "actual", "a0_mean",
                  "arm_mean"] + [f"{p}{m}" for p in ("a0_", "arm_") for m in ("crps", "ae", "err", "in50", "in90", "rpit")]


def _games(P: pd.DataFrame, games: list) -> pd.DataFrame:
    return P[P["game_id"].isin(games)] if not P.empty else P


def paired_arm(P: pd.DataFrame, arm: str) -> pd.DataFrame:
    """The wave2_eval.paired column layout (a0_* / arm_*) for one candidate on the A0 population of the games in P.
    Built per evaluated game set, rows ordered (stat, game_id, player_id), so the randomized-PIT uniforms of a fixed
    analysis set never change when later games arrive. Rows where the candidate is missing are kept out of the paired
    metrics but recorded as integrity failures by player_frame."""
    if P.empty or not P[f"{arm}_ok"].any():
        return pd.DataFrame(columns=PAIRED_COLUMNS)
    P = P[P[f"{arm}_ok"]].sort_values(["stat", "game_id", "player_id"]).reset_index(drop=True)
    out = []
    for st, g in P.groupby("stat", sort=True):
        g = g.reset_index(drop=True)
        y = g["actual"].to_numpy(float)
        m = {}
        for pre, col in (("a0_", "a0"), ("arm_", arm)):
            Q = np.vstack(g[f"{col}_q"].to_numpy()); mu = g[f"{col}_mean"].to_numpy(float)
            m[f"{pre}crps"] = BR.crps_rows(Q, y)
            m[f"{pre}ae"] = np.abs(mu - y); m[f"{pre}err"] = mu - y
            m[f"{pre}in50"] = (y >= Q[:, BR.I25]) & (y <= Q[:, BR.I75])
            m[f"{pre}in90"] = (y >= Q[:, BR.I05]) & (y <= Q[:, BR.I95])
            if st in PMF_STATS:
                # same seed, same row order for both arms: common uniforms (wave2_eval._metrics semantics)
                m[f"{pre}rpit"] = BR.randomized_pit(np.vstack(g[f"{col}_pmf"].to_numpy()), y, st)
            else:
                m[f"{pre}rpit"] = np.full(len(g), np.nan)
        base = g[["game_id", "kickoff", "horizon", "team", "player_id", "stat", "avail_state", "team_has_q", "actual"]].copy()
        base["a0_mean"] = g["a0_mean"].to_numpy(float); base["arm_mean"] = g[f"{arm}_mean"].to_numpy(float)
        out.append(pd.concat([base, pd.DataFrame(m)], axis=1))
    return pd.concat(out, ignore_index=True)


def stat_table(d: pd.DataFrame) -> dict:
    """wave2_eval.stat_table, with PIT summaries set to None where the record defines no pmf (yardage)."""
    if d.empty:
        return {}
    t = E.stat_table(d)
    for st in t:
        if st not in PMF_STATS:
            for k in ("chi2_a0", "chi2_arm", "low_decile_a0", "low_decile_arm", "high_decile_a0", "high_decile_arm"):
                t[st][k] = None
    return t


# ------------------------------------------------------------------------------------------ game margins (M1)
def _pmf_dict(d: dict, offset: int = 0) -> dict:
    p = np.asarray(d["p"], float); p = p / p.sum()
    return {int(d["lo"]) + k - offset: float(v) for k, v in enumerate(p)}


def margin_frame(sel: dict, outcomes: dict) -> pd.DataFrame:
    """Per selected game with a FINAL score: M0 (incumbent bank draws) vs M1 (M1-K) as in key_numbers.evaluate_season --
    exact-margin log score floored at 1e-4 (M1-K from its exact pmf, M0 from its draws), spread-ladder Brier on the
    same pmfs, total-ladder Brier and GAME SCRIPT V2 multiclass Brier from the stored draws. Probabilities are read,
    never modified."""
    from . import key_numbers as K
    rows = []
    for gid in sorted(sel):
        c = sel[gid]; o = outcomes.get(gid)
        if not outcome_ok(o):
            continue
        g = c["rec"]; s, T = float(g["centre"]["spread_home"]), float(g["centre"]["total"])
        m = float(o["home_score"]) - float(o["away_score"]); t = float(o["home_score"]) + float(o["away_score"])
        cell = V.CELLS.index(V.classify(m, t, s, T))
        row = {"game_id": gid, "kickoff": c["kickoff"], "margin": m, "total": t, "cell": cell,
               "coherent_M0": bool(g["coherence"].get("A0")), "coherent_M1": bool(g["coherence"].get("M1"))}
        for mdl, arm in (("M0", "A0"), ("M1", "M1")):
            a = g["arms"][arm]
            draws_pmf = _pmf_dict(a["margin_pmf"], offset=80)
            pmf = {int(k): float(v) for k, v in g["m1k_exact_margin_pmf"].items()} if mdl == "M1" else draws_pmf
            sc = K.score_game(pmf, s, m)
            tp = _pmf_dict(a["total_pmf"])
            ks = np.floor(T) + K.TOTAL_OFFSETS
            tv = np.array(list(tp.keys()), float); tpv = np.array(list(tp.values()), float)
            surv = np.array([tpv[tv > k].sum() for k in ks])
            cells = np.asarray(a["v2_cells"], float)
            onehot = np.zeros(len(cells)); onehot[cell] = 1.0
            row.update({f"{mdl}_log_score": sc["log_score"], f"{mdl}_p_exact": sc["p_exact"], f"{mdl}_ladder_brier": sc["ladder_brier"],
                        f"{mdl}_total_ladder_brier": float(np.mean((surv - (t > ks)) ** 2)),
                        f"{mdl}_v2_brier": float(np.sum((cells - onehot) ** 2))})
        rows.append(row)
    return pd.DataFrame(rows)


# ------------------------------------------------------------------------------------------ bootstrap
def game_boot(G: np.ndarray, fn, B_: int = B, seed: int = SEED) -> dict:
    """Game-clustered percentile interval: G is one row of sufficient statistics PER GAME (games are the resampling
    unit, never player rows); fn maps the column sums to the statistic."""
    G = np.asarray(G, float)
    n = len(G)
    est = fn(G.sum(axis=0))
    if n == 0:
        return {"mean": None, "lo": None, "hi": None, "n_games": 0}
    rng = np.random.default_rng(seed)
    bs = np.empty(B_)
    with np.errstate(all="ignore"):
        for b in range(B_):
            w = np.bincount(rng.integers(0, n, n), minlength=n)
            bs[b] = fn(w @ G)
    if not np.isfinite(bs).any():
        return {"mean": float(est), "lo": None, "hi": None, "n_games": int(n)}
    return {"mean": float(est), "lo": float(np.nanquantile(bs, 0.025)), "hi": float(np.nanquantile(bs, 0.975)), "n_games": int(n)}


def logo(G: np.ndarray, fn, improve_sign: int) -> dict:
    """Leave-one-game-out: largest single-game share of the improvement, and whether the sign survives every removal."""
    G = np.asarray(G, float)
    tot = G.sum(axis=0); full = fn(tot)
    if len(G) < 2 or not np.isfinite(full) or improve_sign * full <= 0:
        return {"max_single_game_share": None, "sign_stable": False, "ok": False}
    loo = np.array([fn(tot - G[i]) for i in range(len(G))])
    share = (full - loo) / full
    stable = bool(np.all(improve_sign * loo > 0))
    mx = float(np.max(share))
    return {"max_single_game_share": mx, "sign_stable": stable, "ok": bool(stable and mx <= LOGO_MAX_SHARE)}


def _ratio(a, b):
    return a / b - 1.0 if b else np.nan


# sufficient statistics per game -------------------------------------------------------------------------------
def s1_game_sums(d: pd.DataFrame, games: list) -> np.ndarray:
    """Columns: for each S1 statistic, (sum arm CRPS, sum A0 CRPS)."""
    G = np.zeros((len(games), 2 * len(E.S1_STATS)))
    ix = {g: i for i, g in enumerate(games)}
    x = d[d["stat"].isin(E.S1_STATS)]
    for (gid, st), g in x.groupby(["game_id", "stat"]):
        if gid in ix:
            j = E.S1_STATS.index(st)
            G[ix[gid], 2 * j] += g["arm_crps"].sum(); G[ix[gid], 2 * j + 1] += g["a0_crps"].sum()
    return G


def s1_primary_from_sums(v) -> float:
    r = [v[2 * j] / v[2 * j + 1] - 1 for j in range(len(E.S1_STATS)) if v[2 * j + 1] > 0]
    return float(np.mean(r)) if r else float("nan")


def a1_game_sums(d: pd.DataFrame, games: list) -> np.ndarray:
    """Columns: (n questionable rows, sum A0 error, sum A1 error) over QUESTIONABLE players' carries + targets."""
    G = np.zeros((len(games), 3)); ix = {g: i for i, g in enumerate(games)}
    x = d[(d["avail_state"] == "QUESTIONABLE") & d["stat"].isin(A1_STATS)]
    for gid, g in x.groupby("game_id"):
        if gid in ix:
            G[ix[gid]] += [len(g), g["a0_err"].sum(), g["arm_err"].sum()]
    return G


def a1_primary_from_sums(v) -> float:
    return float(abs(v[2] / v[0]) - abs(v[1] / v[0])) if v[0] > 0 else float("nan")


def q1_game_sums(d: pd.DataFrame, games: list) -> np.ndarray:
    """Columns per pmf Q1 statistic (attempts, completions): (n, A0 rPIT < 0.10 count, Q1 rPIT < 0.10 count)."""
    st_ = [s for s in E.Q1_STATS if s in PMF_STATS]
    G = np.zeros((len(games), 3 * len(st_))); ix = {g: i for i, g in enumerate(games)}
    for (gid, st), g in d[d["stat"].isin(st_)].groupby(["game_id", "stat"]):
        if gid in ix:
            j = st_.index(st)
            G[ix[gid], 3 * j:3 * j + 3] += [len(g), (g["a0_rpit"] < 0.1).sum(), (g["arm_rpit"] < 0.1).sum()]
    return G


def q1_primary_from_sums(v) -> float:
    r = [abs(v[3 * j + 2] / v[3 * j] - 0.1) - abs(v[3 * j + 1] / v[3 * j] - 0.1) for j in range(len(v) // 3) if v[3 * j] > 0]
    return float(np.mean(r)) if r else float("nan")


def ratio_game_sums(d: pd.DataFrame, games: list, stat: str, arm_col: str, a0_col: str) -> np.ndarray:
    G = np.zeros((len(games), 2)); ix = {g: i for i, g in enumerate(games)}
    for gid, g in d[d["stat"] == stat].groupby("game_id"):
        if gid in ix:
            G[ix[gid]] += [g[arm_col].sum(), g[a0_col].sum()]
    return G


def ratio_fn(v) -> float:
    return _ratio(v[0], v[1])


# ------------------------------------------------------------------------------------------ per-arm evaluation
def _analysis_set(eligible: list, n_min: int) -> list:
    """The first n_min eligible games in (kickoff, game_id) order -- fixed, so the gate is applied once."""
    return [g for _, g in sorted(eligible)][:n_min]


def _ni(d, games, stats, kind) -> dict:
    out = {}
    for st in stats:
        if not (d["stat"] == st).any():
            out[st] = {"status": "NO_ROWS"}
            continue
        cols = ("arm_crps", "a0_crps") if kind == "crps" else ("arm_ae", "a0_ae")
        b = game_boot(ratio_game_sums(d, games, st, *cols), ratio_fn)
        out[st] = {**b, "ok": b["hi"] is not None and b["hi"] <= NI_MARGIN}
    return out


def evaluate_s1(P: pd.DataFrame, games: list, integrity: dict) -> dict:
    d = paired_arm(_games(P, games), "S1")
    G = s1_game_sums(d, games)
    prim = game_boot(G, s1_primary_from_sums)
    st = stat_table(d)
    chi_fall = sum(1 for s in E.S1_STATS if s in st and st[s]["chi2_a0"] is not None and st[s]["chi2_arm"] < st[s]["chi2_a0"])
    others = [s for s in PLAYER_STATS if s not in E.S1_STATS]
    gates = {"primary_interval_excludes_zero_improving": prim["hi"] is not None and prim["hi"] < 0,
             "mae_of_the_five_non_inferior": all(v.get("ok", False) for v in _ni(d, games, E.S1_STATS, "mae").values()),
             "crps_of_every_other_scored_stat_non_inferior": all(v.get("ok", True) for v in _ni(d, games, others, "crps").values()),
             "mechanism_chi2_falls_for_at_least_3_of_5": chi_fall >= 3,
             "zero_integrity_or_coherence_failures": not integrity,
             "leave_one_game_out": logo(G, s1_primary_from_sums, -1)["ok"]}
    return {"primary": prim, "stats": st, "non_inferiority": {"mae": _ni(d, games, E.S1_STATS, "mae"), "crps_other": _ni(d, games, others, "crps")},
            "chi2_falls_count_of_5": chi_fall, "logo": logo(G, s1_primary_from_sums, -1), "gates": gates}


def evaluate_a1(P: pd.DataFrame, games: list, integrity: dict) -> dict:
    d = paired_arm(_games(P, games), "A1")
    G = a1_game_sums(d, games)
    prim = game_boot(G, a1_primary_from_sums)
    teammates = d[(d["avail_state"] != "QUESTIONABLE") & d["team_has_q"]]
    ni = _ni(teammates, games, A1_TEAMMATE_STATS, "crps")
    gates = {"primary_interval_excludes_zero_improving": prim["hi"] is not None and prim["hi"] < 0,
             "teammates_crps_non_inferior": all(v.get("ok", True) for v in ni.values()),
             "zero_integrity_or_coherence_failures": not integrity,
             "leave_one_game_out": logo(G, a1_primary_from_sums, -1)["ok"]}
    return {"primary": prim, "questionable_rows": int(G[:, 0].sum()),
            "questionable_players": stat_table(d[d["avail_state"] == "QUESTIONABLE"]),
            "teammates_of_questionable": stat_table(teammates), "non_inferiority": {"teammates_crps": ni},
            "logo": logo(G, a1_primary_from_sums, -1), "gates": gates}


def evaluate_q1(P: pd.DataFrame, games: list) -> dict:
    d = paired_arm(_games(P, games), "Q1")
    return {"primary_lower_decile_attempts_completions": game_boot(q1_game_sums(d, games), q1_primary_from_sums),
            "stats": stat_table(d),
            "note": "passing yards has no stored pmf, so its randomized PIT is not defined from the record; Q1 cannot be promoted"}


M1_NI = ("ladder_brier", "total_ladder_brier", "v2_brier")


def evaluate_m1(mf: pd.DataFrame, games: list) -> dict:
    x = mf.set_index("game_id").loc[games]
    G = (x["M1_log_score"] - x["M0_log_score"]).to_numpy()[:, None]
    mean_fn = lambda v, n=len(games): float(v[0] / n)   # noqa: E731
    prim = game_boot(G, mean_fn)
    ni = {}
    for k in M1_NI:
        b = game_boot(x[[f"M1_{k}", f"M0_{k}"]].to_numpy(), ratio_fn)
        ni[k] = {**b, "ok": b["hi"] is not None and b["hi"] <= NI_MARGIN}
    # the bootstrap of a mean needs the resample size: n is constant under resampling with replacement
    lg = logo(G, lambda v: float(v[0]), +1)
    gates = {"primary_interval_excludes_zero_improving": prim["lo"] is not None and prim["lo"] > 0,
             "ladders_and_v2_brier_non_inferior": all(v["ok"] for v in ni.values()),
             "coherent_on_every_game": bool(x["coherent_M1"].all()),
             "leave_one_game_out": lg["ok"]}
    return {"primary_log_score_M1_minus_M0": prim, "non_inferiority": ni, "logo": lg, "gates": gates,
            "means": {c: float(x[c].mean()) for c in x.columns if c.startswith(("M0_", "M1_"))},
            "realized_abs3_share": float((x["margin"].abs() == 3).mean())}


# ------------------------------------------------------------------------------------------ status
def arm_status(arm: str, eligible: list, evaluate, interim: bool) -> dict:
    """`eligible` is a list of (kickoff, game_id). Below the frozen minimum: COLLECTING (metrics only when an interim
    look is requested, labelled INTERIM, never a status change). At the minimum: the preregistered gate, once, on the
    analysis set; later games are DESCRIPTIVE."""
    n_min = MIN_GAMES[arm]
    out = {"development_status": DEV_STATUS[arm], "n_eligible_games": len(eligible), "n_required": n_min}
    if len(eligible) < n_min:
        out["evidence_status"] = "COLLECTING"
        out["promotion"] = None
        if interim and eligible:
            out["interim"] = {"label": "INTERIM -- no status change, gates not applied", **evaluate([g for _, g in sorted(eligible)])}
        return out
    aset = _analysis_set(eligible, n_min)
    res = evaluate(aset)
    passed = all(res["gates"].values())
    out.update({"evidence_status": "GATE_APPLIED_AT_MINIMUM", "analysis_set": aset, "at_minimum": res,
                "promotion": "PROMOTION_CANDIDATE" if passed else "NOT_PROMOTED_AT_MINIMUM",
                "promotion_note": "PROMOTION_CANDIDATE is a label for a human decision; it deploys nothing and grants no authority"})
    if len(eligible) > n_min:
        out["descriptive_all_eligible"] = {"label": "DESCRIPTIVE -- the gate is not re-applied", **evaluate([g for _, g in sorted(eligible)])}
    return out


def risk1_registered_test(obs: pd.DataFrame, n_games: int) -> dict:
    """RISK1's registered hypothesis test. Refuses below the frozen minimum; at the minimum it runs risk1.primary_test
    on the first 397 eligible games' observations (the caller passes exactly those)."""
    if n_games < MIN_GAMES["RISK1"]:
        raise PermissionError(f"RISK1 registered test refused: {n_games} eligible games < {MIN_GAMES['RISK1']}")
    from . import risk1 as R
    return R.primary_test(obs)


def clean(o):
    """JSON-safe: NaN / inf -> None, numpy scalars -> Python."""
    if isinstance(o, dict):
        return {str(k): clean(v) for k, v in o.items()}
    if isinstance(o, (list, tuple)):
        return [clean(v) for v in o]
    if isinstance(o, (np.floating, float)):
        return float(o) if np.isfinite(o) else None
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, np.bool_):
        return bool(o)
    return o


def score(records: list, outcomes: dict, *, kickoffs: dict | None = None, interim: bool = False,
          risk1_eligible: list | None = None, risk1_obs: pd.DataFrame | None = None) -> dict:
    """The whole scoring run as one JSON-able dict (no I/O)."""
    cands = candidates(records, kickoffs)
    sel, superseded = select(cands)
    final = {g for g in sel if outcome_ok(outcomes.get(g))}
    missing = {g: (outcomes.get(g) or {}).get("reason", "no outcome supplied") for g in sel if g not in final}
    P, integrity = player_frame(sel, outcomes)
    mf = margin_frame(sel, outcomes)
    elig_all = sorted((sel[g]["kickoff"], g) for g in final)
    elig_t0 = [(k, g) for k, g in elig_all if sel[g]["horizon"] == "T0_INACTIVES"]
    elig_t24 = [(k, g) for k, g in elig_all if sel[g]["horizon"] != "T0_INACTIVES"]
    coh_fail = {arm: sorted(g for g in final if not sel[g]["rec"]["coherence"].get(arm, False)) for arm in ("A0", "S1", "Q1", "A1", "M1")}

    def integ(arm, games):
        bad = {g: v for g, v in integrity[arm].items() if g in games}
        for g in coh_fail[arm]:
            if g in games:
                bad.setdefault(g, []).append("coherence flag false")
        return bad

    arms = {
        "S1": arm_status("S1", elig_all, lambda gs: evaluate_s1(P, gs, integ("S1", set(gs))), interim),
        "A1": arm_status("A1", elig_t0, lambda gs: evaluate_a1(P, gs, integ("A1", set(gs))), interim),
        "M1": arm_status("M1", elig_all, lambda gs: evaluate_m1(mf, gs), interim),
        "Q1": {"development_status": DEV_STATUS["Q1"], "evidence_status": "DESCRIPTIVE_ONLY", "promotion": None,
               "n_eligible_games": len(elig_all),
               "note": "REJECTED_AT_DEVELOPMENT: cannot become a promotion candidate under this preregistration"},
    }
    if interim and elig_all:
        arms["Q1"]["descriptive"] = evaluate_q1(P, [g for _, g in elig_all])
    # A1 T24: the honest earlier horizon, scored separately and never entering the T0 primary
    arms["A1"]["horizon_primary"] = "T0_INACTIVES"
    arms["A1"]["t24_diagnostic"] = {"n_games": len(elig_t24), "label": "T24 earlier-horizon diagnostic; never enters the T0 primary"}
    if interim and elig_t24:
        arms["A1"]["t24_diagnostic"].update(evaluate_a1(P, [g for _, g in elig_t24], {}))
    # RISK1
    r_el = sorted(risk1_eligible or [])
    risk = {"development_status": DEV_STATUS["RISK1"], "n_eligible_games": len(r_el), "n_required": MIN_GAMES["RISK1"]}
    if len(r_el) < MIN_GAMES["RISK1"]:
        risk.update({"evidence_status": "COLLECTING", "result": None,
                     "note": "the registered hypothesis is not tested (risk1_registered_test refuses) below the minimum"})
    else:
        aset = [g for _, g in r_el][:MIN_GAMES["RISK1"]]
        o = risk1_obs[risk1_obs["game_id"].isin(aset)] if risk1_obs is not None else pd.DataFrame()
        risk.update({"evidence_status": "TEST_AT_MINIMUM", "analysis_set": aset, "result": risk1_registered_test(o, len(aset))})
    return clean({
        "scorer_version": SCORER_VERSION, "prospective_cutoff": PROSPECTIVE_CUTOFF, **AUTHORITY,
        "records": {"seen": [{"path": r["path"], "sha256": r["sha256"]} for r in records],
                    "used": {g: {"path": c["path"], "sha256": c["sha256"], "window": c["window"], "generated_at": c["generated_at"],
                                 "kickoff": c["kickoff"], "horizon": c["horizon"]} for g, c in sorted(sel.items())},
                    "excluded": [{"path": c["path"], "game_id": c["game_id"], "window": c["window"], "reason": c["reason"]}
                                 for c in cands if c["reason"] is not None],
                    "superseded": [{"path": c["path"], "game_id": c["game_id"], "window": c["window"]} for c in superseded]},
        "outcomes": {"games_with_outcome": sorted(final), "games_missing_outcome": dict(sorted(missing.items()))},
        "coherence_failures": {a: v for a, v in coh_fail.items() if v},
        "integrity_failures": {a: {g: v for g, v in integrity[a].items()} for a in PLAYER_ARMS if integrity[a]},
        "horizons": {"T0_INACTIVES": len(elig_t0), "T24": len(elig_t24)},
        "arms": arms, "RISK1": risk,
    })
