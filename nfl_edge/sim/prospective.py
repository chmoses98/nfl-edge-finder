"""Prospective projection of a slate at a point in time.

Inputs, all resolved AT OR BEFORE the cutoff and recorded on the run manifest:
  * the incumbent shadow ledger snapshot (the market universe with quotes at ``observed_at``);
  * nflverse weekly rosters for the week, the daily depth chart at the cutoff, the nflverse injury file
    for the week if it exists, and the latest Sleeper availability capture at or before the cutoff;
  * the play-by-play history through the last completed week (features are strictly prior);
  * the fitted bundle for the season (trained on earlier seasons) and the reconciliation weights (fitted
    on the 2025 archive).

Output: one projection row per priced contract with the football-only probability, the market-implied
probability, the reconciled probability, the disagreement, the uncertainty, the stat centre and every
version and timestamp; written once under ``data/shadow/sim/<day>/<run_id>.<version>.projections.jsonl.gz``
and never overwritten.  Contracts the layer cannot price carry a ``support_state`` saying why.
"""
from __future__ import annotations

import glob
import gzip
import hashlib
import json
import os
from datetime import datetime, timezone

import numpy as np
import pandas as pd
import polars as pl

from . import SIM_VERSION
from . import data as D
from . import features as F
from . import inputs as I
from . import simulate as S
from . import reconcile as R
from .simulate import GameInput, TeamInput
from nfl_edge.engines.player.dist import LatticeDistribution
from nfl_edge.engines.player.market_dist import market_distribution
from nfl_edge.settlement.availability import STATE_PLAY_RATES

STAT_MAP = {"passing_yards": "pass_yards", "rushing_yards": "rush_yards", "receiving_yards": "rec_yards",
            "receptions": "receptions", "passing_tds": "pass_td", "touchdowns": "any_td",
            "carries": "carries", "attempts": "attempts", "completions": "completions"}
GRID_MAX = {"pass_yards": 600, "rush_yards": 300, "rec_yards": 300, "receptions": 25, "pass_td": 8, "any_td": 6,
            "carries": 50, "attempts": 75, "completions": 55}
GAME_FAMILIES = ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL")
SLEEPER_OUT = {"Out", "IR", "PUP", "Sus", "COV", "NFI"}
# support states that assert the simulated game's identities held; an incoherent game may not carry them
COHERENCE_DEPENDENT_STATES = ("PRICED", "MARKET_CENTRED_GAME", "FOOTBALL_ONLY_NO_RECONCILIATION")


# ------------------------------------------------------------------------------------- ledger read
def latest_ledger(market_data: str, at_or_before: datetime | None = None) -> tuple[list[dict], dict, str]:
    files = sorted(glob.glob(os.path.join(market_data, "data", "shadow", "ledger", "*", "*.observations.jsonl.gz")))
    if at_or_before is not None:
        stamp = at_or_before.strftime("%Y%m%dT%H%M%SZ")
        files = [f for f in files if os.path.basename(f)[:16] <= stamp]
    if not files:
        raise FileNotFoundError("no ledger snapshot")
    path = files[-1]
    rows = [json.loads(l) for l in gzip.open(path, "rt")]
    run_id = os.path.basename(path)[:16]
    man = json.load(open(path.replace(".observations.jsonl.gz", ".ledger_manifest.json"))) if os.path.exists(path.replace(".observations.jsonl.gz", ".ledger_manifest.json")) else {}
    return rows, man, run_id


def fast_implied_lines(rows: list[dict], home: str, away: str) -> tuple[float | None, float | None, dict]:
    """Interpolate the 50% crossing of the monotone SPREAD and TOTAL midpoints.  A cheap, transparent
    stand-in for the incumbent's grid search; the source is recorded on the record."""
    def crossing(pts):
        # pts: (k, mid) with mid decreasing in k; return k where mid == 0.5
        pts = sorted(pts)
        if len(pts) < 2:
            return None
        ks = np.array([p[0] for p in pts]); ms = np.array([p[1] for p in pts])
        ms = np.minimum.accumulate(ms)  # enforce monotone decreasing
        if ms[0] < 0.5 or ms[-1] > 0.5:
            return None
        j = int(np.argmax(ms <= 0.5))
        k0, k1, m0, m1 = ks[j - 1], ks[j], ms[j - 1], ms[j]
        return float(k0 + (m0 - 0.5) / max(m0 - m1, 1e-9) * (k1 - k0))
    sp, tp = [], []
    for r in rows:
        if r.get("period") not in ("FULL", None) or r.get("yes_bid") is None or r.get("yes_ask") is None:
            continue
        if (r["yes_ask"] - r["yes_bid"]) > 0.08:
            continue
        mid = (r["yes_bid"] + r["yes_ask"]) / 2
        if r.get("family") == "SPREAD" and r.get("floor_strike") is not None:
            # P(team margin > floor) : express as home margin
            fs = float(r["floor_strike"])
            if r.get("team") == home:
                sp.append((fs, mid))
            elif r.get("team") == away:
                sp.append((-fs, 1 - mid))
        elif r.get("family") == "TOTAL" and r.get("threshold") is not None:
            tp.append((float(r["threshold"]), mid))
    s = crossing(sp); t = crossing(tp)
    return s, t, {"n_spread_rungs": len(sp), "n_total_rungs": len(tp)}


# ------------------------------------------------------------------------------ injury vintages
def _download_manifest(root: str) -> dict:
    path = os.path.join(root, "data", "raw", "nflverse", "_manifest.jsonl")
    out = {}
    if not os.path.exists(path):
        return out
    for line in open(path):
        try:
            r = json.loads(line)
        except ValueError:
            continue
        if r.get("path"):
            out[r["path"]] = r
    return out


def injury_vintage(root: str, season: int, cutoff: datetime, extra_roots=()) -> tuple[str | None, dict, str]:
    """The injury parquet a projection at ``cutoff`` may legitimately read, via the content-addressed
    vintage index (``shadow_v2.vintage_snapshots``).

    The nflverse injury release is REBUILT IN PLACE as designations are filed, so reading the mutable file
    re-runs an old cutoff against today's fuller report.  The resolver returns the newest snapshot whose
    retrieval time is at or before the cutoff, and returns NOTHING rather than falling back to the mutable
    file.  Sleeper supplements whatever this returns; it never silently replaces it."""
    from nfl_edge.shadow_v2 import vintage_snapshots as VS
    try:
        path, row, why = VS.resolve_injuries(root, season, cutoff, manifest=_download_manifest(root),
                                             adopt=True, extra_roots=tuple(extra_roots))
    except Exception as exc:                                                   # noqa: BLE001
        return None, {}, f"vintage resolution failed: {type(exc).__name__}: {exc}"
    if path is None or not os.path.exists(path or ""):
        return None, (row or {}), (why or "no injury vintage at or before the cutoff")
    return path, (row or {}), why


# ---------------------------------------------------------------------------------- availability
def sleeper_availability(market_data: str, cutoff: datetime) -> tuple[dict, str | None]:
    """gsis_id -> Sleeper injury status from the newest capture at or before the cutoff."""
    files = sorted(glob.glob(os.path.join(market_data, "data", "context", "*", "*.sleeper.json")))
    stamp = cutoff.strftime("%Y%m%dT%H%M%SZ")
    files = [f for f in files if os.path.basename(f)[:16] <= stamp]
    if not files:
        return {}, None
    d = json.load(open(files[-1]))
    cw = pl.read_parquet(os.path.join(D.ROOT, "data", "silver", "player_crosswalk.parquet")).select(["gsis_id", "sleeper_id"])
    cw = cw.filter(pl.col("sleeper_id").is_not_null())
    s2g = dict(zip(cw["sleeper_id"].cast(pl.Utf8).to_list(), cw["gsis_id"].to_list()))
    out = {}
    for sid, p in (d.get("players") or {}).items():
        g = p.get("gsis_id") or s2g.get(str(sid))
        if g:
            out[g] = {"injury_status": p.get("injury_status"), "status": p.get("status"), "team": p.get("team")}
    return out, os.path.basename(files[-1])[:16]


def avail_state(nfl_status: str | None, sleeper: dict | None) -> str:
    st = nfl_status
    if sleeper:
        s = sleeper.get("injury_status")
        if s in SLEEPER_OUT or sleeper.get("status") == "Inactive":
            return "OUT"
        if s == "Doubtful":
            st = st or "Doubtful"
        elif s == "Questionable":
            st = st or "Questionable"
    if st == "Out":
        return "OUT"
    if st == "Doubtful":
        return "DOUBTFUL"
    if st == "Questionable":
        return "QUESTIONABLE"
    return "EXPECTED_ACTIVE"


# ------------------------------------------------------------------------------------ assembly
def slate_inputs(season: int, week: int, cutoff: datetime, market_data: str, *, ledger_rows: list[dict],
                 history_start: int = 2016, cfg: F.FeatureConfig = F.FEATURE_CONFIG, verbose=print,
                 priors: F.PriorSet | None = None) -> dict:
    """Point-in-time GameInputs for every game of the week whose kickoff is after the cutoff.

    ``priors`` are the frozen shrinkage targets carried on the season's bundle (fitted on seasons strictly
    before it).  They are required: a league mean computed over the frame assembled here would include this
    season's completed games, which is defensible, and its own upcoming ones, which is not."""
    if priors is None:
        raise F.MissingPriors("slate_inputs needs the bundle's PriorSet (bundle['priors'])")
    sched = D.schedule().to_pandas()
    g = sched[(sched["season"] == season) & (sched["week"] == week)].copy()
    g["kickoff"] = pd.to_datetime(g["gameday"] + " " + g["gametime"]).dt.tz_localize("America/New_York").dt.tz_convert("UTC")
    g = g[g["kickoff"] > cutoff]
    # history: every completed game strictly before the cutoff (a game in progress never enters)
    tg = D.load("team_games", range(history_start, season + 1)).to_pandas()
    pg = D.load("player_games", range(history_start, season + 1)).to_pandas()
    done = sched[sched["home_score"].notna()].copy()
    done["kickoff"] = pd.to_datetime(done["gameday"] + " " + done["gametime"].fillna("13:00")).dt.tz_localize("America/New_York").dt.tz_convert("UTC")
    ok_games = set(done[done["kickoff"] + pd.Timedelta(hours=4) <= cutoff]["game_id"])
    tg = tg[tg["game_id"].isin(ok_games)]; pg = pg[pg["game_id"].isin(ok_games)]
    # phantom team rows for the upcoming games
    ph = []
    for r in g.itertuples():
        for team, opp, home in ((r.home_team, r.away_team, True), (r.away_team, r.home_team, False)):
            ph.append({"game_id": r.game_id, "team": team, "opp": opp, "home": home, "season": season, "week": week,
                       "season_type": "REG", "home_team": r.home_team, "away_team": r.away_team})
    tg_all = pd.concat([tg, pd.DataFrame(ph)], ignore_index=True, sort=False)
    tf = F.team_features(tg_all, cfg, priors)
    # eligibility
    depth = F.depth_chart(season, cutoff=cutoff)
    roster = F.weekly_roster(season, week)
    inj_path, inj_row, inj_why = injury_vintage(D.ROOT, season, cutoff, extra_roots=(market_data,))
    inj = F.injury_designations(season, week, root=inj_path) if inj_path else pd.DataFrame(
        columns=["player_id", "report_status", "practice_status"])
    inj_map = dict(zip(inj["player_id"], inj["report_status"])) if len(inj) else {}
    sleeper, sleeper_run = sleeper_availability(market_data, cutoff)
    elig_rows = []
    for r in g.itertuples():
        for team in (r.home_team, r.away_team):
            e = F.eligible_players(season, week, team, depth=depth, roster=roster, injuries=inj)
            if e.empty:
                continue
            e["game_id"] = r.game_id; e["season"] = season; e["week"] = week
            e["avail_state"] = [avail_state(inj_map.get(p), sleeper.get(p)) for p in e["player_id"]]
            e = e[~e["avail_state"].isin(["OUT", "DOUBTFUL"])]
            elig_rows.append(e)
    elig = pd.concat(elig_rows, ignore_index=True)
    pf = F.player_features(pg, tg, cfg, phantom_rows=elig, priors=priors)
    keep = ["game_id", "team", "player_id", "position", "dc_rank", "avail_state"]
    e = elig[keep].merge(pf.drop(columns=["position", "season", "week", "team"]), on=["game_id", "player_id"], how="left")
    frames = {"team": tf, "eligible": e}
    inputs = {}
    for r in g.itertuples():
        obs = [x for x in ledger_rows if x.get("game_id") == r.game_id]
        s_imp, t_imp, diag = fast_implied_lines(obs, r.home_team, r.away_team)
        if s_imp is not None and t_imp is not None:
            spread, total, src = s_imp, t_imp, "kalshi_implied_interpolated"
        else:
            spread, total, src = float(r.spread_line), float(r.total_line), "consensus_line"
        gi = I.historical_game_input(frames, r.game_id, spread_home=spread, total_line=total, center_source=src)
        gi.season, gi.week = season, week
        inputs[r.game_id] = {"input": gi, "kickoff": r.kickoff, "center_diag": diag}
    return {"games": inputs,
            "sources": {"depth_chart_vintage": depth["dc_vintage"].iloc[0] if len(depth) else None,
                        "roster_week": week,
                        "injury_vintage": {"resolved": inj_path is not None,
                                           "snapshot_path": (inj_row or {}).get("snapshot_path"),
                                           "sha256": (inj_row or {}).get("sha256"),
                                           "retrieved_at": (inj_row or {}).get("retrieved_at"),
                                           "reason": inj_why, "rows_for_week": int(len(inj)),
                                           "designations": {k: int(v) for k, v in inj["report_status"].value_counts().items()} if len(inj) else {}},
                        "sleeper_run": sleeper_run,
                        "priors_fit_seasons": list(priors.fit_seasons), "priors_version": priors.version,
                        "history_games": len(ok_games), "latest_history_game": max(ok_games) if ok_games else None},
            "eligible": e}


# ------------------------------------------------------------------------------------- pricing
def _player_dist(arr: np.ndarray, stat: str) -> LatticeDistribution:
    return LatticeDistribution.from_samples(np.round(arr), GRID_MAX[stat])


# The quantiles a projection row carries, and the one the report calls "the model median".  Read off the
# distribution that priced the ladder -- never inferred from where a sparse Kalshi ladder happens to cross
# 0.50, which is how the incumbent ledger-derived median came to be blank for a player the simulation had a
# perfectly good distribution for (Jahmyr Gibbs rushing yards, 2026 week 2: 15 listed rungs, none of them
# crossing 0.50 under the incumbent's own ladder, so the report showed "--" beside a football mean of 95.1).
QUANTILES = ("p05", "p25", "p50", "p75", "p95")
SUMMARY_FIELDS = ("mean", "sd") + QUANTILES


def distribution_fields(prefix: str, d: LatticeDistribution | None) -> dict:
    """``{prefix}_mean/_sd/_p05/_p25/_p50/_p75/_p95`` from the distribution's OWN summary.

    ``LatticeDistribution.summary()`` is the single source: its sd is sqrt(var) and its quantiles are
    ``quantile(q)`` on the same pmf that priced every rung, so the persisted median is the simulation's
    median and not a reconstruction of it.  A ``None`` distribution yields the field names with ``None``
    values, so a row never silently lacks a key.
    """
    if d is None:
        return {f"{prefix}_{k}": None for k in SUMMARY_FIELDS}
    s = d.summary()
    return {f"{prefix}_{k}": float(s[k]) for k in SUMMARY_FIELDS}


def price_slate(slate: dict, ledger_rows: list[dict], bundle: dict, weights: dict | None, *, n_sims: int = 20000,
                run_id: str, observed_at: str, generated_at: datetime, player_map: dict, verbose=print) -> list[dict]:
    """Price every FULL-period contract of the priced families on the slate's games."""
    bank = I.historical_bank(int(next(iter(slate["games"].values()))["input"].season))
    out = []
    w_by_stat = {k: v["weight"] for k, v in (weights or {}).get("fitted", {}).items()}
    for gid, G in slate["games"].items():
        gi: GameInput = G["input"]
        res = S.simulate(gi, bundle, n=n_sims, bank=bank)
        coh = S.coherence_report(res)
        rows = [r for r in ledger_rows if r.get("game_id") == gid and r.get("family") in GAME_FAMILIES + ("PLAYER_STAT",)
                and r.get("period") in ("FULL", None)]
        # market ladders per player/stat
        ladders = {}
        for r in rows:
            if r.get("family") == "PLAYER_STAT" and r.get("stat") in STAT_MAP and r.get("operator") == ">=":
                ladders.setdefault((r.get("player_kalshi_id"), r["stat"]), []).append(
                    {"threshold": r.get("threshold"), "yes_bid": r.get("yes_bid"), "yes_ask": r.get("yes_ask")})
        mkt = {k: market_distribution(k[1], v) for k, v in ladders.items()}
        dists = {}
        for r in rows:
            rec = {"record_id": hashlib.sha1(f"{run_id}|{r['ticker']}|{SIM_VERSION}".encode()).hexdigest()[:20],
                   "run_id": run_id, "ticker": r["ticker"], "family": r.get("family"), "period": r.get("period"), "stat": r.get("stat"),
                   "game_id": gid, "season": gi.season, "week": gi.week, "team": r.get("team"), "player_kalshi_id": r.get("player_kalshi_id"),
                   "player_id": None, "threshold": r.get("threshold"), "floor_strike": r.get("floor_strike"), "operator": r.get("operator"),
                   "kickoff_utc": r.get("kickoff_utc"), "market_observed_at": r.get("observed_at") or observed_at,
                   "generated_at": generated_at.isoformat(), "feature_cutoff": generated_at.isoformat(),
                   "minutes_to_kickoff": r.get("minutes_to_kickoff"),
                   "sim_version": SIM_VERSION, "engine_version": S.ENGINE_VERSION, "models_version": bundle.get("models_version"),
                   "bundle_train_seasons": bundle.get("train_seasons"), "reconcile_version": R.RECONCILE_VERSION,
                   "center_source": gi.center_source, "center_spread_home": gi.spread_home, "center_total": gi.total_line,
                   "yes_bid": r.get("yes_bid"), "yes_ask": r.get("yes_ask"), "mid": r.get("mid"),
                   "incumbent_model_probability": r.get("model_contract_value"), "incumbent_support_state": r.get("support_state"),
                   "p_football": None, "p_market": None, "p_reconciled": None, "reconcile_weight": None, "disagreement_vs_mid": None,
                   "football_mean": None, "market_mean": None, "final_mean": None, "football_sd": None,
                   # the distribution summary (sim-1.1.0).  Declared here so every row carries the keys and a
                   # reader can tell "this artifact does not report a median" from "this row has none".
                   **distribution_fields("football", None),
                   "market_p50": None, "final_p50": None,
                   # ledger identity, carried through so a handicapper reads a name and a machine reads the ids
                   "player_name": r.get("player_name"),
                   "n_sims": n_sims, "support_state": None, "support_reason": None, "coherence_ok": bool(coh["ok"])}
            fam = r.get("family")
            try:
                if fam == "GAME_WINNER":
                    m = res.margin
                    p_win = float(np.mean(m > 0)) if r.get("team") == gi.home.team else float(np.mean(m < 0))
                    rec.update(p_football=p_win + 0.5 * float(np.mean(m == 0)), support_state="MARKET_CENTRED_GAME",
                               support_reason="game centre is the market's; shape is the historical residual bank (no football deviation claimed)")
                elif fam == "SPREAD":
                    x = res.margin if r.get("team") == gi.home.team else -res.margin
                    rec.update(p_football=float(np.mean(x > float(r["floor_strike"]))), support_state="MARKET_CENTRED_GAME",
                               support_reason="game centre is the market's; shape is the historical residual bank")
                elif fam == "TOTAL":
                    rec.update(p_football=float(np.mean(res.total >= float(r["threshold"]))), support_state="MARKET_CENTRED_GAME",
                               support_reason="game centre is the market's; shape is the historical residual bank")
                elif fam == "TEAM_TOTAL":
                    x = res.home_points if r.get("team") == gi.home.team else res.away_points
                    rec.update(p_football=float(np.mean(x >= float(r["threshold"]))), support_state="MARKET_CENTRED_GAME",
                               support_reason="game centre is the market's; shape is the historical residual bank")
                elif fam == "PLAYER_STAT":
                    st = STAT_MAP.get(r.get("stat"))
                    gs = player_map.get(r.get("player_kalshi_id"))
                    rec["player_id"] = gs
                    if st is None:
                        rec.update(support_state="UNSUPPORTED_STAT", support_reason=f"no simulated statistic for {r.get('stat')}")
                    elif not gs:
                        rec.update(support_state="UNSUPPORTED_IDENTITY", support_reason="Kalshi player id not resolved to GSIS")
                    elif gs not in res.player:
                        rec.update(support_state="NOT_ELIGIBLE", support_reason="player not in the point-in-time eligible set (out, doubtful, not on roster/depth chart)")
                    elif r.get("operator") != ">=" or r.get("threshold") is None:
                        rec.update(support_state="UNSUPPORTED_RULES", support_reason=f"operator {r.get('operator')}")
                    else:
                        key = (gs, st)
                        if key not in dists:
                            dists[key] = _player_dist(np.asarray(res.player[gs][st], float), st)
                        d = dists[key]; k = float(r["threshold"])
                        p_active = float(np.mean(res.player[gs]["active"]))
                        pf = d.survival(k)
                        mrec = mkt.get((r.get("player_kalshi_id"), r["stat"]))
                        m_mean = mrec["_dist"].mean() if mrec and mrec.get("identification") not in (None, "NONE") else None
                        w = w_by_stat.get(st)
                        rd, attr = R.reconcile_distribution(d, m_mean, w, st)
                        rec.update(p_football=pf, p_market=r.get("mid"),
                                   # mean, sd AND the quantiles from one call on the pricing distribution
                                   **distribution_fields("football", d),
                                   market_mean=m_mean, market_identification=(mrec or {}).get("identification"),
                                   market_p50=(mrec["_dist"].quantile(0.5) if m_mean is not None else None),
                                   # the reconciled distribution's own median, on the same footing as its mean:
                                   # `rd` IS the football distribution when nothing reconciled it, which is
                                   # exactly when `final_mean` is the football mean, so the two stay consistent
                                   final_p50=float(rd.quantile(0.5)),
                                   p_active=p_active, reconcile_weight=w, final_mean=attr["final_mean"],
                                   p_reconciled=(rd.survival(k) if attr["status"] == "RECONCILED" else None),
                                   support_state=("PRICED" if attr["status"] == "RECONCILED" else "FOOTBALL_ONLY_NO_RECONCILIATION"),
                                   support_reason=(None if attr["status"] == "RECONCILED" else attr["status"]),
                                   attribution={"football_mean": attr["football_mean"], "market_mean": attr["market_mean"],
                                                "final_mean": attr["final_mean"], "weight": attr["weight"],
                                                "components": {"expected_opportunity": None, "note": "component attribution is reported, not additive"}})
                if rec.get("p_football") is not None and r.get("mid") is not None:
                    p_use = rec["p_reconciled"] if rec.get("p_reconciled") is not None else rec["p_football"]
                    rec["disagreement_vs_mid"] = round(float(p_use - r["mid"]), 5)
                    rec["football_disagreement_vs_mid"] = round(float(rec["p_football"] - r["mid"]), 5)
            except Exception as exc:  # noqa: BLE001
                rec.update(support_state="ERROR", support_reason=f"{type(exc).__name__}: {exc}")
            # Fail CLOSED on an incoherent game, as the backtest already does by raising.  A game whose
            # own identities do not hold is a game the engine cannot price, and publishing its rows as
            # PRICED with coherence_ok=false beside them invites a reader to use them anyway.  The
            # probabilities stay on the row for diagnosis; the support state refuses them.
            if not coh["ok"] and rec.get("support_state") in COHERENCE_DEPENDENT_STATES:
                broken = "; ".join(f"{k}={v}" for k, v in coh.items() if k != "ok" and v)
                rec.update(support_state="UNSUPPORTED_COHERENCE",
                           support_reason=f"simulated game violates an engine identity: {broken}"[:400])
            out.append(rec)
        verbose(f"{gid}: {len(rows)} contracts, centre {gi.center_source} ({gi.spread_home:+.1f}, {gi.total_line:.1f}), coherence {coh['ok']}")
    return out


# --------------------------------------------------------------------------------------- store
def write_records(root: str, run_id: str, rows: list[dict], manifest: dict) -> str:
    """Write-once: an existing file for the same run and version is refused, never overwritten."""
    day = f"{run_id[:4]}-{run_id[4:6]}-{run_id[6:8]}"
    d = os.path.join(root, "data", "shadow", "sim", day)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, f"{run_id}.{SIM_VERSION}.projections.jsonl.gz")
    if os.path.exists(path):
        raise FileExistsError(path)
    with gzip.open(path, "wt") as f:
        for r in rows:
            f.write(json.dumps(r, default=_json_default) + "\n")
    with open(path.replace(".projections.jsonl.gz", ".manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, default=_json_default)
    return path


def _json_default(o):
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, (pd.Timestamp, datetime)):
        return o.isoformat()
    raise TypeError(str(type(o)))
