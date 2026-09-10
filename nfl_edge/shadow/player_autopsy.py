"""Postgame player-projection autopsy: WHICH part of a projection missed, from the intermediates the model froze.

For every settled player-stat projection with schema-1.1.0 intermediates in the ledger, the latest pregame
snapshot is placed against the box score:

    standardised surprise   robust z = (actual - p50) / (IQR / 1.349), from the fitted distribution's own
                            quantiles, so a 40-yard receiving miss and a 2-reception miss are on one scale;
                            plus the percentile of the actual inside the model's quantile grid
    opportunity             projected opportunity mean (muo) vs actual attempts / targets / carries
    efficiency              projected mu / muo vs actual stat / actual opportunity
    availability            P(plays) vs whether the player provably took a snap
    team volume             the team's actual pass attempts or carries vs its own prior-game mean this season
                            (from the same nflverse player statistics; last season when it is week 1)
    market                  the model's contract value vs the market midpoint against the realised payout,
                            on the rung nearest the model's median

and a DETERMINISTIC classification is assigned from fixed thresholds named below. It is a diagnosis. It feeds
no weight, no feature and no threshold anywhere; it exists so "Stevenson missed" becomes "the workload model
put him at 17 carries and he got 8" or "the workload was right and the yards per carry collapsed", and so a
season of those can be read together. No player is special-cased.
"""
from __future__ import annotations

import gzip
import json
import math
import os
from collections import defaultdict
from datetime import datetime, timezone

from nfl_edge.settlement.results import ResultBook

AUTOPSY_VERSION = "autopsy-1.0.0"
SUFFIX = "autopsy"

# Thresholds. Named once; a change is a visible edit to a diagnostic rule, never a tuning.
Z_LARGE = 1.5                     # |robust z| at or above this is a "large miss"
LOG_RATIO_LARGE = math.log(1.5)   # a component is "off" when actual/projected is outside [1/1.5, 1.5]
TEAM_VOLUME_LOG_RATIO = math.log(1.25)
MARKET_DIFF_LARGE = 0.25          # |model payout error| - |market payout error| beyond this is "much worse/better"
IQR_FLOOR = 0.5

OPPORTUNITY_MISS = "OPPORTUNITY_MISS"
EFFICIENCY_MISS = "EFFICIENCY_MISS"
AVAILABILITY_MISS = "AVAILABILITY_MISS"
TEAM_VOLUME_MISS = "TEAM_VOLUME_MISS"
UNEXPLAINED_VARIANCE = "UNEXPLAINED_VARIANCE"
INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
NO_LARGE_MISS = "NO_LARGE_MISS"
MODEL_MUCH_WORSE_THAN_MARKET = "MODEL_MUCH_WORSE_THAN_MARKET"
MODEL_BETTER_THAN_MARKET = "MODEL_BETTER_THAN_MARKET"

# ledger `stat` -> the opportunity column in nflverse player statistics
OPPORTUNITY_OF = {"passing_yards": "attempts", "completions": "attempts", "passing_tds": "attempts",
                  "interceptions": "attempts", "attempts": "attempts", "rushing_yards": "carries", "carries": "carries",
                  "receiving_yards": "targets", "receptions": "targets", "touchdowns": "touches"}
TEAM_VOLUME_OF = {"attempts": "attempts", "targets": "attempts", "carries": "carries", "touches": None}


def _f(x):
    try:
        return None if x is None else float(x)
    except (TypeError, ValueError):
        return None


def load_observations(market_data: str, game_ids, day_lo=None, day_hi=None) -> dict:
    """SUPPORTED player-stat pregame rows per game, from the published ledger. Read only."""
    import glob
    want = set(game_ids)
    out = defaultdict(list)
    for d in sorted(glob.glob(os.path.join(market_data, "data", "shadow", "ledger", "*"))):
        day = os.path.basename(d)
        if (day_lo and day < day_lo) or (day_hi and day > day_hi):
            continue
        for path in sorted(glob.glob(os.path.join(d, "*.observations.jsonl.gz"))):
            with gzip.open(path, "rt") as fh:
                for line in fh:
                    r = json.loads(line)
                    if r.get("game_id") in want and r.get("family") == "PLAYER_STAT" and r.get("support_state") == "SUPPORTED":
                        out[r["game_id"]].append(r)
    return out


def representative_rows(rows: list) -> list:
    """One ledger row per (player, stat): the latest provably pregame snapshot, then the rung nearest the model's
    median (mu for the direct TD model). Deterministic tie-breaks on prediction_id."""
    groups = defaultdict(list)
    for r in rows:
        mtk = r.get("minutes_to_kickoff")
        if mtk is None or float(mtk) <= 0 or r.get("player_id") is None:
            continue
        groups[(r["player_id"], r.get("stat"))].append(r)
    out = []
    for key in sorted(groups):
        rs = groups[key]
        best_run = min(rs, key=lambda r: (float(r["minutes_to_kickoff"]), str(r.get("observed_at")), str(r.get("prediction_id"))))["run_id"]
        snap = [r for r in rs if r["run_id"] == best_run]
        centre = _f((snap[0].get("model_quantiles") or {}).get("p50"))
        if centre is None:
            centre = _f(snap[0].get("projected_stat_mean"))
        if centre is None:
            out.append(min(snap, key=lambda r: str(r.get("prediction_id"))))
            continue
        out.append(min(snap, key=lambda r: (abs(_f(r.get("threshold")) - centre) if _f(r.get("threshold")) is not None else 1e9,
                                            str(r.get("prediction_id")))))
    return out


def team_volume(book: ResultBook, game_id: str, team: str, column: str) -> dict | None:
    """The team's actual pass attempts / carries in this game vs its mean over prior games this season (or all of
    last season at week 1). Computed from the same player statistics that settle the props."""
    g = book.games.get(game_id)
    if g is None or g.season is None or g.week is None or not column:
        return None
    def team_total(gid):
        vals = [p.stats.get(column) for (gg, _pid), p in book.players.items() if gg == gid and p.team == team and p.has_stats_row]
        vals = [v for v in vals if v is not None]
        return sum(vals) if vals else None
    actual = team_total(game_id)
    if actual is None:
        return None
    prior = [og for og, gr in book.games.items() if gr.season == g.season and gr.week is not None and gr.week < g.week
             and team in (gr.home_team, gr.away_team) and og in book.games_with_player_stats]
    basis = "prior games this season"
    if not prior:
        prior = [og for og, gr in book.games.items() if gr.season == g.season - 1 and team in (gr.home_team, gr.away_team)
                 and og in book.games_with_player_stats]
        basis = "all games last season"
    totals = [t for t in (team_total(og) for og in prior) if t is not None]
    if not totals:
        return {"actual": actual, "prior_mean": None, "n_prior": 0, "basis": basis, "log_ratio": None}
    pm = sum(totals) / len(totals)
    return {"actual": actual, "prior_mean": pm, "n_prior": len(totals), "basis": basis,
            "log_ratio": math.log((actual + 0.5) / (pm + 0.5))}


def _percentile(q: dict, actual: float):
    xs = [_f(q.get(k)) for k in ("p05", "p25", "p50", "p75", "p95")]
    ys = [0.05, 0.25, 0.50, 0.75, 0.95]
    if any(x is None for x in xs):
        return None
    if actual <= xs[0]:
        return 0.05 * (actual / xs[0]) if xs[0] > 0 else 0.05
    if actual >= xs[-1]:
        return min(0.99, 0.95 + 0.04 * (actual - xs[-1]) / max(xs[-1] - xs[-2], 1.0))
    for i in range(4):
        if xs[i] <= actual <= xs[i + 1]:
            if xs[i + 1] == xs[i]:
                return ys[i + 1]
            return ys[i] + (ys[i + 1] - ys[i]) * (actual - xs[i]) / (xs[i + 1] - xs[i])
    return None


def diagnose(row: dict, book: ResultBook, *, now: datetime | None = None, version: str = AUTOPSY_VERSION) -> dict:
    """One representative ledger row -> one autopsy record. Deterministic."""
    now = now or datetime.now(timezone.utc)
    gid, pid, stat = row.get("game_id"), row.get("player_id"), row.get("stat")
    out = {"prediction_id": row["prediction_id"], "evaluation_version": version, "evaluated_at": now.isoformat(),
           "run_id": row.get("run_id"), "observed_at": row.get("observed_at"), "minutes_to_kickoff": row.get("minutes_to_kickoff"),
           "game_id": gid, "season": row.get("season"), "week": row.get("week"), "team": row.get("team"),
           "player_id": pid, "player_name": row.get("player_name"), "stat": stat, "stat_spec": row.get("stat_spec"),
           "ticker": row.get("ticker"), "threshold": row.get("threshold"), "model_version": row.get("model_version"),
           "model_artifact_sha": row.get("model_artifact_sha"), "feature_cutoff": row.get("feature_cutoff"),
           "distribution_family": row.get("distribution_family"), "model_quantiles": row.get("model_quantiles"),
           "projected_stat_mean": _f(row.get("projected_stat_mean")), "projected_opportunity": _f(row.get("projected_opportunity_mean")),
           "projected_efficiency": None, "efficiency_feature": row.get("efficiency_feature"),
           "efficiency_decomposition": row.get("efficiency_decomposition"),
           "model_event_probability": row.get("model_event_probability"), "model_contract_value": row.get("model_contract_value"),
           "market_mid": row.get("mid"), "market_yes_ask": row.get("yes_ask"),
           "availability_state": row.get("availability_state"), "p_plays": row.get("p_plays"),
           "ewma_stat": row.get("ewma_stat"), "ewma_opportunity": row.get("ewma_opportunity"),
           "feature_n_prior": row.get("feature_n_prior"), "feature_shrink_w": row.get("feature_shrink_w"),
           "actual_stat": None, "actual_opportunity": None, "actual_efficiency": None, "played": None,
           "snaps": None, "targets": None, "receptions": None, "carries": None, "pass_attempts": None,
           "usage_missing": False, "robust_z": None, "percentile": None, "realised_payout": None,
           "model_vs_market_payout_error_diff": None, "market_verdict": None, "team_volume": None,
           "large_miss": None, "classification": INSUFFICIENT_DATA, "tags": [], "evidence": []}
    mu, muo = out["projected_stat_mean"], out["projected_opportunity"]
    if muo and mu is not None and out["efficiency_decomposition"] == "opportunity_x_efficiency":
        out["projected_efficiency"] = mu / muo
    if mu is None:
        out["evidence"].append("no instrumented intermediates on this ledger row (pre-1.1.0 schema)")
        return out
    pr = book.player(gid, pid) if gid and pid else None
    if pr is None:
        out["usage_missing"] = True
        out["evidence"].append("player has neither a statistics row nor a snap row for this game")
        if out["p_plays"] is not None and float(out["p_plays"]) >= 0.5 and gid in book.games_with_snaps and gid in book.games_with_player_stats:
            out["classification"] = AVAILABILITY_MISS
            out["tags"].append("expected to play, absent from complete usage tables")
        return out
    out.update({"played": pr.played, "snaps": pr.offense_snaps, "targets": pr.stats.get("targets"),
                "receptions": pr.stats.get("receptions"), "carries": pr.stats.get("carries"),
                "pass_attempts": pr.stats.get("attempts")})
    actual = pr.stat_value(stat)
    if actual is None and pr.played:
        actual = 0.0
        out["evidence"].append("took snaps, no recorded value: counted as zero")
    out["actual_stat"] = actual
    opp_col = OPPORTUNITY_OF.get(stat)
    if opp_col == "touches":
        t, c = pr.stats.get("targets"), pr.stats.get("carries")
        out["actual_opportunity"] = None if t is None and c is None else float((t or 0) + (c or 0))
    elif opp_col:
        v = pr.stats.get(opp_col)
        out["actual_opportunity"] = None if v is None else float(v)
    if out["actual_opportunity"] is not None and actual is not None and out["actual_opportunity"] > 0 \
            and out["efficiency_decomposition"] == "opportunity_x_efficiency":
        out["actual_efficiency"] = actual / out["actual_opportunity"]
    # ---- availability first: a projection for a player who did not play is not a football miss ----------
    p_plays = _f(out["p_plays"])
    if pr.played is None:
        out["usage_missing"] = True
        out["evidence"].append("participation unproven from free data")
        return out
    if pr.played is False:
        out["classification"] = AVAILABILITY_MISS if (p_plays is None or p_plays >= 0.5) else NO_LARGE_MISS
        out["evidence"].append(f"active, never took a snap; P(plays) was {p_plays}")
        return out
    if p_plays is not None and p_plays < 0.5:
        out["tags"].append(f"played despite P(plays)={p_plays:.2f}")
    # ---- standardised surprise ------------------------------------------------------------------------------
    q = out["model_quantiles"] or {}
    p50, p25, p75 = _f(q.get("p50")), _f(q.get("p25")), _f(q.get("p75"))
    if actual is not None and None not in (p50, p25, p75):
        scale = max((p75 - p25) / 1.349, IQR_FLOOR)
        out["robust_z"] = (actual - p50) / scale
        out["percentile"] = _percentile(q, actual)
    elif actual is not None and out["distribution_family"] == "direct_binary":
        # a Bernoulli projection: surprise is the standardised residual of the 1+ event
        p = min(max(mu, 1e-6), 1 - 1e-6)
        y = 1.0 if actual >= 1 else 0.0
        out["robust_z"] = (y - p) / math.sqrt(p * (1 - p))
        out["percentile"] = None
    # ---- market comparison on the representative rung --------------------------------------------------------
    thr = _f(row.get("threshold"))
    if thr is not None and actual is not None:
        y = 1.0 if actual >= thr else 0.0
        out["realised_payout"] = y
        cv, mid = _f(row.get("model_contract_value")), _f(row.get("mid"))
        if cv is not None and mid is not None:
            d = abs(cv - y) - abs(mid - y)
            out["model_vs_market_payout_error_diff"] = d
            out["market_verdict"] = (MODEL_MUCH_WORSE_THAN_MARKET if d > MARKET_DIFF_LARGE else
                                     MODEL_BETTER_THAN_MARKET if d < -MARKET_DIFF_LARGE else "SIMILAR")
        else:
            out["market_verdict"] = "NO_MARKET"
    # ---- classification --------------------------------------------------------------------------------------
    # The components are diagnosed whenever they can be: a workload projected at 17 carries that got 8 is an
    # opportunity miss even when the yards happened to land inside the model's range. The standardised surprise
    # decides the RANKING and the `large_miss` flag; the components decide the mechanism.
    z = out["robust_z"]
    out["large_miss"] = bool(z is not None and abs(z) >= Z_LARGE)
    opp_lr = eff_lr = None
    if muo and out["actual_opportunity"] is not None:
        opp_lr = math.log((out["actual_opportunity"] + 0.5) / (muo + 0.5))
        out["opportunity_log_ratio"] = opp_lr
    if out["projected_efficiency"] and out["actual_efficiency"] is not None and out["projected_efficiency"] > 0:
        eff_lr = math.log((out["actual_efficiency"] + 1e-6) / (out["projected_efficiency"] + 1e-6))
        out["efficiency_log_ratio"] = eff_lr
    opp_off = opp_lr is not None and abs(opp_lr) > LOG_RATIO_LARGE
    eff_off = eff_lr is not None and abs(eff_lr) > LOG_RATIO_LARGE
    if opp_off:
        out["tags"].append("opportunity off")
    if eff_off:
        out["tags"].append("efficiency off")
    if opp_off and (not eff_off or abs(opp_lr) >= abs(eff_lr)):
        out["classification"] = OPPORTUNITY_MISS
        out["evidence"].append(f"projected opportunity {muo:.1f}, actual {out['actual_opportunity']:.0f}")
        tv = team_volume(book, gid, out["team"], TEAM_VOLUME_OF.get(opp_col))
        out["team_volume"] = tv
        if tv and tv.get("log_ratio") is not None and abs(tv["log_ratio"]) > TEAM_VOLUME_LOG_RATIO \
                and (tv["log_ratio"] > 0) == (opp_lr > 0):
            out["classification"] = TEAM_VOLUME_MISS
            out["evidence"].append(f"team {TEAM_VOLUME_OF.get(opp_col)} {tv['actual']:.0f} vs prior mean {tv['prior_mean']:.1f} ({tv['basis']})")
    elif eff_off:
        out["classification"] = EFFICIENCY_MISS
        out["evidence"].append(f"projected efficiency {out['projected_efficiency']:.2f}, actual {out['actual_efficiency']:.2f}; opportunity within range")
    elif z is None:
        out["classification"] = INSUFFICIENT_DATA
        out["evidence"].append("no quantiles to standardise the miss and no component out of range")
    elif not out["large_miss"]:
        out["classification"] = NO_LARGE_MISS
    elif opp_lr is None and eff_lr is None:
        out["classification"] = INSUFFICIENT_DATA if out["efficiency_decomposition"] != "none" else UNEXPLAINED_VARIANCE
        out["evidence"].append("no opportunity/efficiency decomposition available for this statistic")
    else:
        out["classification"] = UNEXPLAINED_VARIANCE
        out["evidence"].append("opportunity and efficiency both inside range; the outcome sits in the model's tail")
    return out


def rank(records: list) -> list:
    """Deterministic: largest |robust z| first, ties by game, player, stat; undiagnosable rows last."""
    def key(r):
        z = r.get("robust_z")
        return (0 if z is not None else 1, -(abs(z) if z is not None else 0.0), str(r.get("game_id")),
                str(r.get("player_id")), str(r.get("stat")))
    return sorted(records, key=key)


def autopsy_game(rows: list, book: ResultBook, *, now=None) -> list:
    return rank([diagnose(r, book, now=now) for r in representative_rows(rows)])
