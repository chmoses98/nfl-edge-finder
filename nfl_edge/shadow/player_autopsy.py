"""Postgame player-projection autopsy: WHICH part of a projection missed, from the frozen anatomy corpus.

The incumbent ledger records only P(stat >= K) and the contract value. The intermediates come from the SEPARATE
player-anatomy corpus (`nfl_edge/arms/player_anatomy.py`, data/shadow/player_anatomy/<game_id>/), written at the
same pregame snapshot by replaying the frozen pricer and reconciled to the ledger row within 1e-9. Only anatomy
rows whose status is OK are evidence; a REPRODUCTION_MISMATCH row is INSUFFICIENT_DATA here, by construction.

For every anatomy row of a final game, the latest pregame snapshot is placed against the box score:

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

import math
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone

from nfl_edge.settlement.results import ResultBook

# 1.1.0 (2026-10-01): the representative row must have been GENERATED before kickoff, not merely carry a pregame
# quote (see `generated_at` below), and ties are broken by the latest pre-kickoff generation instead of by the
# prediction id. 1.0.0 records stay in the corpus untouched; readers take one record per unit through
# `canonical_autopsies`, which prefers the newest rule version.
AUTOPSY_VERSION = "autopsy-1.1.0"
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
OK_STATUS = "OK"
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


ANATOMY_SUFFIX = "anatomy"


def load_anatomy(roots, game_ids) -> dict:
    """Anatomy rows per game from the published (and any staged) anatomy corpus. Read only."""
    from nfl_edge.shadow.evaluation_store import read_corpus
    want = set(game_ids)
    out = defaultdict(list)
    for r in read_corpus(list(roots) if not isinstance(roots, str) else [roots], suffix=ANATOMY_SUFFIX):
        if r.get("game_id") in want:
            out[r["game_id"]].append(r)
    return out


# the generation-time helpers live in a neutral module the board research shares (re-exported here)
from nfl_edge.shadow.pregame_time import _ts, generated_at, generated_pregame, kickoff_of  # noqa: E402,F401


def representative_rows(rows: list) -> list:
    """One anatomy row per (player, stat): the latest provably pregame snapshot, then the rung nearest the model's
    median (mu for the direct TD model). Deterministic tie-breaks.

    "Provably pregame" means BOTH the quote and the computation precede kickoff (`generated_pregame`). Among the
    rows quoting the latest pregame price, the run that computed latest before kickoff wins; the prediction id
    only breaks a tie inside one run. (autopsy-1.0.0 broke the tie by prediction id alone, which on a game the
    pricer kept re-pricing after kickoff could select a postgame computation: 86 of 3,021 records.)"""
    groups = defaultdict(list)
    for r in rows:
        mtk = r.get("minutes_to_kickoff")
        if mtk is None or float(mtk) <= 0 or r.get("player_id") is None or not generated_pregame(r):
            continue
        groups[(r["player_id"], r.get("stat"))].append(r)
    out = []
    for key in sorted(groups):
        rs = groups[key]
        best = min(rs, key=lambda r: (float(r["minutes_to_kickoff"]), -generated_at(r).timestamp(),
                                      str(r.get("observed_at")), str(r.get("prediction_id"))))
        best_run = best["run_id"]
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


def excluded_rows(rows: list) -> dict:
    """Why anatomy rows of a game are NOT eligible to represent a unit (counts by reason). Never silent."""
    out = defaultdict(int)
    for r in rows:
        mtk = r.get("minutes_to_kickoff")
        if r.get("player_id") is None:
            out["no player identity"] += 1
        elif mtk is None or float(mtk) <= 0:
            out["quote not pregame"] += 1
        elif generated_at(r) is None:
            out["generation time unknown"] += 1
        elif not generated_pregame(r):
            out["computed at or after kickoff (re-priced stale pregame quote)"] += 1
    return dict(out)


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
    """One representative anatomy row -> one autopsy record. Deterministic."""
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
           "model_event_probability": row.get("ledger_event_probability", row.get("model_event_probability")),
           "model_contract_value": row.get("ledger_contract_value", row.get("model_contract_value")),
           "market_mid": row.get("mid"), "market_yes_ask": row.get("yes_ask"),
           "availability_state": row.get("availability_state"), "p_plays": row.get("p_plays"),
           "ewma_stat": row.get("ewma_stat"), "ewma_opportunity": row.get("ewma_opportunity"),
           "feature_n_prior": row.get("feature_n_prior"), "feature_shrink_w": row.get("feature_shrink_w"),
           "actual_stat": None, "actual_opportunity": None, "actual_efficiency": None, "played": None,
           "snaps": None, "targets": None, "receptions": None, "carries": None, "pass_attempts": None,
           "usage_missing": False, "robust_z": None, "percentile": None, "realised_payout": None,
           "model_vs_market_payout_error_diff": None, "market_verdict": None, "team_volume": None,
           "large_miss": None, "classification": INSUFFICIENT_DATA, "tags": [], "evidence": []}
    out["anatomy_status"] = row.get("anatomy_status")
    mu, muo = out["projected_stat_mean"], out["projected_opportunity"]
    if muo and mu is not None and out["efficiency_decomposition"] == "opportunity_x_efficiency":
        out["projected_efficiency"] = mu / muo
    if row.get("anatomy_status", OK_STATUS) != OK_STATUS:
        out["evidence"].append(f"anatomy row is {row.get('anatomy_status')}: {row.get('reason')}; not authoritative evidence")
        return out
    if mu is None:
        out["evidence"].append("no intermediates on this anatomy row")
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
        cv, mid = _f(out["model_contract_value"]), _f(row.get("mid"))
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
    eff_undefined = False
    if muo and out["actual_opportunity"] is not None:
        opp_lr = math.log((out["actual_opportunity"] + 0.5) / (muo + 0.5))
        out["opportunity_log_ratio"] = opp_lr
    if out["projected_efficiency"] and out["actual_efficiency"] is not None and out["projected_efficiency"] > 0:
        ratio = (out["actual_efficiency"] + 1e-6) / (out["projected_efficiency"] + 1e-6)
        if ratio > 0:
            eff_lr = math.log(ratio)
            out["efficiency_log_ratio"] = eff_lr
        else:
            # Real football produces negative yardage: a sack, a tackle for loss, a lateral. Against a positive
            # projected efficiency the ratio is zero or negative and has no real logarithm -- and `math.log` of
            # it raised `ValueError: math domain error`, which took the whole autopsy step of the postgame
            # workflow with it. What the missing logarithm would have measured is a miss of UNBOUNDED size, not
            # a small one, so the component is recorded as materially off and the ratio stays None. Clamping to
            # a tiny positive number to keep `math.log` running would invent a finite number that no evidence
            # supports. Shadow v2 reached the same conclusion first (nfl_edge/engines/player/autopsy_v2.py).
            eff_undefined = True
            out["efficiency_log_ratio"] = None      # stated, not left to be inferred from an absent key
    opp_off = opp_lr is not None and abs(opp_lr) > LOG_RATIO_LARGE
    eff_off = eff_undefined or (eff_lr is not None and abs(eff_lr) > LOG_RATIO_LARGE)
    # an undefined ratio outranks any finite opportunity miss, because its magnitude is unbounded
    eff_mag = float("inf") if eff_undefined else (abs(eff_lr) if eff_lr is not None else None)
    if opp_off:
        out["tags"].append("opportunity off")
    if eff_off:
        out["tags"].append("efficiency off")
    if eff_undefined:
        out["tags"].append("efficiency ratio undefined")
    if opp_off and (not eff_off or abs(opp_lr) >= eff_mag):
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
        if eff_undefined:
            out["evidence"].append(
                f"projected efficiency {out['projected_efficiency']:.2f}, actual {out['actual_efficiency']:.2f} on "
                f"{out['actual_opportunity']:.0f} opportunities: the ratio is not positive, so no real log ratio exists; "
                f"recorded as a large efficiency miss with no ratio invented")
        else:
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
    out = []
    for r in representative_rows(rows):
        rec = diagnose(r, book, now=now)
        rec["generated_at"] = generated_at(r).isoformat()
        out.append(rec)
    return rank(out)


def _version_key(v) -> tuple:
    try:
        return tuple(int(x) for x in str(v).rsplit("-", 1)[-1].split("."))
    except ValueError:
        return (0,)


def record_generated_at(rec: dict):
    """The generation instant of the projection an AUTOPSY record diagnoses. An autopsy record's own
    `evaluated_at` is the postgame diagnosis time and must never be read as this: 1.1.0 records carry the
    projection's `generated_at`; 1.0.0 records only carry the pricing `run_id`."""
    return _ts(rec.get("generated_at")) or _ts(rec.get("run_id"))


def record_generated_pregame(rec: dict) -> bool:
    g, ko = record_generated_at(rec), kickoff_of(rec)
    return g is not None and ko is not None and g < ko


def canonical_autopsies(records: list) -> list:
    """ONE diagnosis per (game, player, statistic) for every report.

    The corpus is append-only and keyed by prediction id, so a unit can legitimately hold several records: the
    same unit under a newer rule version, or a newer representative row once a later pregame anatomy file was
    published. Counting all of them double-counts a player (26 units did, Weeks 1-3). The reader therefore takes
    the newest rule version present for the GAME (never a mix of rules inside one game), drops any record whose projection was computed at or after
    kickoff, and then the latest pregame quote, latest pregame computation, prediction id. Deterministic, and
    the dropped records stay in the corpus."""
    top = {}
    for r in records:
        g, v = r.get("game_id"), _version_key(r.get("evaluation_version"))
        top[g] = max(top.get(g, v), v)
    units = defaultdict(list)
    for r in records:
        if _version_key(r.get("evaluation_version")) == top[r.get("game_id")]:
            units[(r.get("game_id"), r.get("player_id"), r.get("stat"))].append(r)
    out = []
    for key in sorted(units, key=lambda k: tuple(str(x) for x in k)):
        rs = units[key]
        pre = [r for r in rs if record_generated_pregame(r)]
        if not pre:
            continue
        out.append(min(pre, key=lambda r: (float(r.get("minutes_to_kickoff") or 0), -record_generated_at(r).timestamp(),
                                           str(r.get("prediction_id")))))
    return rank(out)


# ======================================================================================================
# coverage: which games of a week were (and were not) diagnosed, and why
# ======================================================================================================
EXCLUDE_NOT_FINAL = "game not final (or no kickoff) when the report was built"
EXCLUDE_NO_ANATOMY = "no player-anatomy corpus for this game (no instrumented pregame projection)"
EXCLUDE_NO_ELIGIBLE = "anatomy exists, but no row was both quoted and computed before kickoff"
EXCLUDE_NOT_DIAGNOSED = "eligible pregame projections exist but no autopsy batch covers them yet (postgame job pending/failed)"


def anatomy_units(rows: list) -> dict:
    """Per game: how many (player, stat) units are eligible to be diagnosed, and why the other rows are not."""
    rep = representative_rows(rows)
    return {"anatomy_rows": len(rows), "eligible_units": len(rep),
            "eligible_unit_ids": sorted(f"{r['player_id']}|{r.get('stat')}" for r in rep),
            "excluded_rows": excluded_rows(rows)}


def coverage_manifest(schedule: list, anatomy: dict | None, canonical: list, raw_records: list | None = None) -> dict:
    """The week's autopsy coverage, game by game: expected (the schedule), eligible (instrumented pregame
    projections), diagnosed (canonical autopsies), excluded (with a reason). A report that cannot show this
    for its week is not allowed to look complete.

    `schedule` rows: {game_id, status, kickoff_utc}. `anatomy` maps game_id -> anatomy_units(...) (None when the
    caller did not read the anatomy corpus: eligibility is then inferred from diagnosis alone, and said so)."""
    by_game = defaultdict(list)
    for r in canonical:
        by_game[r.get("game_id")].append(r)
    raw = defaultdict(int)
    for r in raw_records or []:
        raw[r.get("game_id")] += 1
    games, excluded = [], []
    for g in sorted(schedule, key=lambda g: g["game_id"]):
        gid = g["game_id"]
        recs = by_game.get(gid, [])
        an = (anatomy or {}).get(gid)
        row = {"game_id": gid, "status": g.get("status"), "diagnosed_units": len(recs),
               "raw_autopsy_records": raw.get(gid, 0),
               "units_with_box_score": sum(1 for r in recs if r.get("actual_stat") is not None),
               "by_classification": dict(sorted(Counter(r.get("classification") for r in recs).items())),
               "autopsy_versions": sorted({str(r.get("evaluation_version")) for r in recs})}
        if an is not None:
            row.update({"anatomy_rows": an["anatomy_rows"], "eligible_units": an["eligible_units"],
                        "excluded_anatomy_rows": an["excluded_rows"]})
            ids = {f"{r.get('player_id')}|{r.get('stat')}" for r in recs}
            row["eligible_not_diagnosed"] = len(set(an["eligible_unit_ids"]) - ids)
        reason = None
        if g.get("status") != "FINAL":
            reason = EXCLUDE_NOT_FINAL
        elif anatomy is not None and an is None and not recs:
            reason = EXCLUDE_NO_ANATOMY
        elif an is not None and an["eligible_units"] == 0:
            reason = EXCLUDE_NO_ELIGIBLE
        elif not recs:
            reason = EXCLUDE_NOT_DIAGNOSED if (an is None or an["eligible_units"]) else EXCLUDE_NO_ELIGIBLE
        row["included"] = reason is None
        row["exclusion_reason"] = reason
        (games if reason is None else excluded).append(row)
    allrows = games + excluded
    return {"expected_games": len(schedule),
            "eligible_games": sum(1 for r in allrows if (r.get("eligible_units") or r["diagnosed_units"]) > 0),
            "diagnosed_games": len(games), "excluded_games": len(excluded),
            "projection_units": sum(r["diagnosed_units"] for r in games),
            "units_with_box_score": sum(r["units_with_box_score"] for r in games),
            "eligible_units": (sum(r.get("eligible_units", 0) for r in allrows) if anatomy is not None else None),
            "eligible_not_diagnosed": (sum(r.get("eligible_not_diagnosed", 0) for r in allrows) if anatomy is not None else None),
            "anatomy_read": anatomy is not None,
            "games": sorted(allrows, key=lambda r: r["game_id"])}


def render_coverage(m: dict, *, title: str = "Player-autopsy coverage") -> str:
    lines = [f"## {title}", "",
             f"Expected games {m['expected_games']} · eligible {m['eligible_games']} · diagnosed {m['diagnosed_games']} · "
             f"excluded {m['excluded_games']} · canonical projection units {m['projection_units']} "
             f"({m['units_with_box_score']} with a box-score value)"
             + (f" · eligible units {m['eligible_units']}, eligible but undiagnosed {m['eligible_not_diagnosed']}" if m["anatomy_read"]
                else " · anatomy not read: eligibility inferred from diagnoses only"), "",
             "| game | included | diagnosed units | raw records | eligible units | undiagnosed | rule | exclusion reason |",
             "|---|---|---|---|---|---|---|---|"]
    for r in m["games"]:
        lines.append(f"| {r['game_id']} | {'yes' if r['included'] else 'NO'} | {r['diagnosed_units']} | {r['raw_autopsy_records']} | "
                     f"{r.get('eligible_units', '—')} | {r.get('eligible_not_diagnosed', '—')} | {', '.join(r['autopsy_versions']) or '—'} | "
                     f"{r['exclusion_reason'] or ''} |")
    return "\n".join(lines) + "\n"
