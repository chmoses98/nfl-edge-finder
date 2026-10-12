"""Accuracy and betting-value scorecards on matured PURE shadow rows (research only, descriptive, append-only).

Runs inside `evaluate.settle_and_evaluate`, ALONGSIDE the pure_gate compare scorecards (which are unchanged), and
uses the vendored, unmodified `tools/pure_gate/accuracy_scorecard.py` and `value_scorecard.py` (see
tools/pure_gate/SCORECARDS.md).

accuracy_scorecard   challenger PURE_PLAYER_V1, `statistical_baseline` PURE_EWM_BASELINE, and the incumbent
                     market-informed DATA_PLAYER_V4 / V5 records as the labelled `market_informed_benchmark` (a
                     price-of-independence diagnostic) wherever a record meets the projection contract (mean, median,
                     p10, p90). The incumbent records published so far carry p05 / p50 / p95 only, so they are counted
                     as NOT_SCOREABLE, never approximated. Populations: the full eligible population (every
                     player-game-statistic either PURE arm forecast for a matured game) and the pregame market-listed
                     cohort (market listing opened AND observed by our records at or before the forecast's as_of).
                     Missing forecasts, forecasts without an outcome, conditional DNP exclusions and missed capture
                     windows are counted, never dropped. Zero matured rows gives INSUFFICIENT_SAMPLE, not an error.
value_scorecard      DRY-RUN DIAGNOSTIC only, under the committed preregistration
                     docs/research/PURE_SHADOW_NFL_VALUE_PREREG.json (explained in the .md beside it). Only the PURE
                     arm named there is eligible for an independent-value verdict; the market-informed incumbents are
                     evaluated with market_informed_source=True and so always read NOT_INDEPENDENT_EVIDENCE.

Nothing here reads a live venue, places or sizes an order, or touches wagering, staking, routing or any production
surface. Every output is a write-once file in the research store.
"""
from __future__ import annotations

import glob
import hashlib
import importlib.util
import json
import math
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

from nfl_edge.engines.player.pure_v1 import BASELINE_NAME, MODEL_NAME
from nfl_edge.shadow_pure import SPORT, store

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
GATE_DIR = os.path.join(ROOT, "tools", "pure_gate")
PREREG_PATH = os.path.join(ROOT, "docs", "research", "PURE_SHADOW_NFL_VALUE_PREREG.json")
ACCURACY_MIN_GAMES = 20          # accuracy_scorecard sets few_game_clusters_warning below 20 game clusters
POP_FULL, POP_COHORT = "full_eligible", "pregame_market_listed"
VALUE_MODE = "DRY_RUN_DIAGNOSTIC"
NO_WAGERING = ("diagnostic only: no order is placed or sized, no stake, no routing, no production surface; the verdict "
               "is a statement about a recorded evaluation window, not wagering authority")


# ------------------------------------------------------------------------------------------------ vendored modules
def vendored(name: str):
    """tools/pure_gate/<name>.py (vendored, stdlib only), imported from its file. accuracy_scorecard loads pure_gate.py
    from the same directory."""
    path = os.path.join(GATE_DIR, f"{name}.py")
    mod = sys.modules.get(name)
    if mod is not None and os.path.abspath(getattr(mod, "__file__", "") or "") == os.path.abspath(path):
        return mod
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    try:
        spec.loader.exec_module(mod)
    except Exception:
        sys.modules.pop(name, None)
        raise
    return mod


# ------------------------------------------------------------------------------------------------ small helpers
def _utc(s) -> datetime | None:
    if s in (None, ""):
        return None
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def _iso(d: datetime) -> str:
    return d.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def _run_as_of(path: str) -> datetime | None:
    try:
        return datetime.strptime(os.path.basename(path)[:16], "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def _price(v) -> float | None:
    if v in (None, ""):
        return None
    try:
        x = float(v)
    except (TypeError, ValueError):
        return math.nan
    return x if math.isfinite(x) else math.nan


def kalshi_at_least(threshold, operator: str | None = ">=", *, integer_ladder: bool = True) -> float | None:
    """A Kalshi player-stat strike in the at_least representation of the PURE ladder (SCORECARDS.md).

    Kalshi "K+" / `>= K` is the event X >= K. The PURE_PLAYER_V1 ladder publishes P(X >= k) at integer k, so on that
    ladder the event is the rung at_least = K exactly (on a half-integer ladder it would be K - 0.5). A `> f` strike on
    an integer statistic is X >= floor(f) + 1. Anything else (no strike, less-than, ranges) is None, which the caller
    counts; the value scorecard matches strikes exactly, so a strike off the ladder is a missing quote, never an
    approximation."""
    if threshold in (None, ""):
        return None
    t = float(threshold)
    if not math.isfinite(t):
        return None
    if operator in (">=", "AT_LEAST", "greater_or_equal", None):
        k = t
    elif operator in (">", "GREATER_THAN", "greater", "gt"):
        k = float(math.floor(t) + 1)
    else:
        return None
    return k if integer_ladder else k - 0.5


def file_sha256(path: str) -> str:
    with open(path, "rb") as fh:
        return hashlib.sha256(fh.read()).hexdigest()


def load_prereg(path: str = PREREG_PATH) -> dict:
    with open(path, encoding="utf-8") as fh:
        pr = json.load(fh)
    if not isinstance(pr, dict):
        raise ValueError("preregistration must be a JSON object")
    return pr


# ------------------------------------------------------------------------------------------------ accuracy
def sample_state(report: dict, challenger: str, min_games: int = ACCURACY_MIN_GAMES) -> dict:
    """Per population: INSUFFICIENT_SAMPLE (no scored challenger rows, or fewer game clusters than the scorecard's own
    warning threshold) or DESCRIPTIVE_SAMPLE. Neither is a promotion signal."""
    out = {}
    for pop in (POP_FULL, POP_COHORT):
        body = (report.get("populations") or {}).get(pop)
        if body is None:
            out[pop] = {"state": "INSUFFICIENT_SAMPLE", "reason": "population not reported (no market family supplied)"}
            continue
        acc = body["accounting"]["arms"].get(challenger, {})
        pooled = body["all_statistics_scale_free"].get(challenger, {})
        n, g = int(acc.get("scored_rows", 0)), int(pooled.get("n_games", 0))
        if n == 0:
            state, why = "INSUFFICIENT_SAMPLE", "no matured, scored challenger rows"
        elif g < min_games:
            state, why = "INSUFFICIENT_SAMPLE", f"{g} game clusters < {min_games}: CIs unstable, read descriptively only"
        else:
            state, why = "DESCRIPTIVE_SAMPLE", f"{g} game clusters; descriptive only, never an automatic promotion"
        out[pop] = {"state": state, "reason": why, "scored_rows": n, "games": g,
                    **{k: int(acc.get(k, 0)) for k in ("eligible_identities", "forecast_rows", "missing_forecast",
                                                        "missing_forecast_with_outcome", "forecast_rows_missing_outcome",
                                                        "conditional_dnp_excluded")}}
    return out


def eligible_rows(arm_rows: list[list[dict]]) -> list[dict]:
    """The full eligible population: every identity any PURE arm forecast, at its earliest as_of."""
    first: dict[tuple, str] = {}
    for rows in arm_rows:
        for r in rows:
            k = (r["sport"], r["game_id"], str(r["player_id"]), r["statistic"])
            if k not in first or r["as_of"] < first[k]:
                first[k] = r["as_of"]
    return [{"sport": k[0], "game_id": k[1], "player_id": k[2], "statistic": k[3], "as_of": t} for k, t in sorted(first.items())]


def run_accuracy(challenger_rows, outcome_rows, *, comparators: dict, market_rows: list[dict], eligible: list[dict],
                 breakdowns: dict, challenger_label: str, bootstrap: int, seed: int = 20261010) -> dict:
    A = vendored("accuracy_scorecard")
    rep = A.score(challenger_rows, outcome_rows, comparators=comparators, market_rows=market_rows, eligible_rows=eligible,
                  breakdowns=breakdowns, cluster_by=("game", "player"), bootstrap=bootstrap,
                  breakdown_bootstrap=min(200, bootstrap), seed=seed, challenger_label=challenger_label)
    return {"sample_state": sample_state(rep, challenger_label), "scorecard": rep}


# ------------------------------------------------------------------------------------------------ value
def probability_rows(rows: list[dict], *, basis: str, market_informed: bool = False) -> list[dict]:
    """One value_scorecard probability row per ladder rung: p_yes = P(actual >= at_least) exactly as published."""
    out = []
    for r in rows:
        for t in (r.get("projection") or {}).get("thresholds") or []:
            out.append({"sport": r["sport"], "game_id": r["game_id"], "player_id": str(r["player_id"]),
                        "statistic": r["statistic"], "at_least": float(t["at_least"]), "as_of": r["as_of"],
                        "kickoff": r.get("kickoff"), "p_yes": float(t["probability"]), "probability_basis": basis,
                        "model_version": r.get("model_version"), "market_informed": bool(market_informed)})
    return out


def evaluate_value(prob_rows, quote_rows, outcome_rows, prereg: dict, *, market_informed: bool,
                   dnp_policy: str | None = None) -> dict:
    """value_scorecard.evaluate with every setting taken from the preregistration (nothing chosen at run time)."""
    V = vendored("value_scorecard")
    rule = V.RULES[prereg["rule"]](float(prereg["min_edge"]))
    fees = V.FeeModel(role=prereg["role"], contracts=int(prereg["contracts"]), multiplier=float(prereg["fee_multiplier"]),
                      slippage=float(prereg["slippage"]), tick=float(prereg["tick"]))
    thresholds = {k: prereg[k] for k in V.DEFAULT_THRESHOLDS if k in prereg}
    return V.evaluate(prob_rows, quote_rows, outcome_rows, rule=rule,
                      rule_name=f"{prereg['rule']}(min_edge={float(prereg['min_edge']):g})", fees=fees,
                      thresholds=thresholds, prereg=prereg, market_informed_source=market_informed,
                      cluster_by=tuple(prereg.get("cluster", ["game"])), bootstrap=int(prereg["bootstrap"]),
                      seed=int(prereg["seed"]), as_of_policy=prereg["as_of_policy"],
                      dnp_policy=dnp_policy or prereg["dnp_policy"],
                      max_quote_age_seconds=prereg.get("max_quote_age_seconds"),
                      calibration_fit_end=prereg.get("calibration_fit_end"))


def value_entry(report: dict, *, arm: str, window: str, role: str, eligible: bool, market_informed: bool,
                dnp_policy: str) -> dict:
    v = report["verdict"]
    return {"arm": arm, "capture_window": window, "role": role, "dnp_policy": dnp_policy,
            "eligible_for_independent_value_verdict": eligible, "market_informed_source": market_informed,
            "verdict": v["verdict"], "verdict_reasons": v.get("reasons"),
            "verdict_counts_toward_preregistered_decision": bool(eligible and role == "primary"),
            "n_decisions": report["decisions_summary"].get("n_decisions", 0),
            "n_games": report["decisions_summary"].get("n_games", 0), "report": report}


# ------------------------------------------------------------------------------------------------ NFL store adapters
def _kind(r: dict) -> str | None:
    return (r.get("x_capture") or {}).get("capture_kind")


def listing_rows(store_root: str) -> list[tuple[datetime | None, dict]]:
    """(capture as_of, row) for every row of every market/<day>/<run>.kalshi_listings.jsonl.gz (the separate family)."""
    out = []
    for f in sorted(glob.glob(os.path.join(store_root, "market", "*", "*.kalshi_listings.jsonl.gz"))):
        at = _run_as_of(f)
        out += [(at, r) for r in store.read_jsonl(f)]
    return out


def market_family(listings: list[tuple[datetime | None, dict]], kickoff: dict) -> tuple[list[dict], list[dict], dict]:
    """The NFL market family mapped to (accuracy cohort rows, value_scorecard quote rows, counts).

    cohort rows   {sport, game_id, player_id (gsis), statistic, open_time, observed_at}: listing time only.
    quote rows    + at_least (kalshi_at_least: the NFL rows' `threshold` K is the event X >= K, rung at_least K),
                  yes_bid / yes_ask in DOLLARS (the capture's *_dollars fields), ticker, market (series), kickoff.
    A row observed after the as_of of the capture that recorded it is dropped and counted (it cannot have been
    known then); the scorecard itself also only ever enters at the latest quote observed at or before each as_of."""
    c = Counter()
    cohort, quotes, seen = [], [], set()
    for at, r in listings:
        c["listing_rows"] += 1
        pid = r.get("gsis_id")
        if not pid:
            c["dropped_unmapped_player"] += 1
            continue
        obs = _utc(r.get("observed_at"))
        if obs is None:
            c["dropped_no_observed_at"] += 1
            continue
        if at is not None and obs > at:
            c["dropped_observed_after_capture_as_of"] += 1
            continue
        base = {"sport": SPORT, "game_id": r["game_id"], "player_id": str(pid), "statistic": r["statistic"]}
        cohort.append({**base, "open_time": r.get("open_time"), "observed_at": r.get("observed_at")})
        k = kalshi_at_least(r.get("threshold"), ">=")
        if k is None:
            c["quote_dropped_no_strike"] += 1
            continue
        bid, ask = _price(r.get("yes_bid")), _price(r.get("yes_ask"))
        if any(x is not None and (math.isnan(x) or not 0.0 <= x <= 1.0) for x in (bid, ask)):
            c["quote_dropped_invalid_price"] += 1
            continue
        if bid is not None and ask is not None and bid > ask:
            c["quote_dropped_crossed"] += 1
            continue
        key = (r.get("ticker"), r.get("observed_at"), bid, ask)
        if key in seen:
            c["quote_duplicate_across_captures"] += 1
            continue
        seen.add(key)
        t = r.get("ticker") or ""
        quotes.append({**base, "at_least": k, "observed_at": r.get("observed_at"), "open_time": r.get("open_time"),
                       "yes_bid": bid, "yes_ask": ask, "price_unit": "dollars", "ticker": r.get("ticker"),
                       "market": t.split("-")[0] if "-" in t else None, "kickoff": kickoff.get(r["game_id"]),
                       "source": r.get("source")})
    c["cohort_rows"], c["quote_rows"] = len(cohort), len(quotes)
    return cohort, quotes, dict(sorted(c.items()))


def incumbent_records(store_root: str, kind_of: dict) -> list[dict]:
    """incumbent_diagnostic V4/V5 records with the as_of of the capture that copied them and its capture kind."""
    out = []
    for f in sorted(glob.glob(os.path.join(store_root, "incumbent_diagnostic", "*", "*.v4_v5_market_informed.jsonl.gz"))):
        at = _run_as_of(f)
        if at is None:
            continue
        a = _iso(at)
        for r in store.read_jsonl(f):
            out.append({**r, "_as_of": a, "_kind": kind_of.get((r.get("game_id"), a))})
    return out


def _q(ds: dict, name: str):
    v = ds.get(name)
    if v is None:
        v = (ds.get("quantiles") or {}).get(name)
    return v


def incumbent_benchmark(recs: list[dict]) -> tuple[dict[str, list[dict]], dict]:
    """projection_only rows for the market_informed_benchmark, per arm, from records that carry mean, p10, p50 and
    p90. A record without them is counted NOT_SCOREABLE (never approximated from p05 / p95)."""
    rows, c = defaultdict(list), Counter()
    for r in recs:
        c["records"] += 1
        ds = r.get("distribution_summary") or {}
        mean, med, p10, p90 = ds.get("mean"), _q(ds, "p50"), _q(ds, "p10"), _q(ds, "p90")
        if None in (mean, med, p10, p90):
            c["not_scoreable_missing_mean_p10_p50_p90"] += 1
            continue
        if not (p10 <= med <= p90) or not r.get("kickoff") or _utc(r["_as_of"]) >= _utc(r["kickoff"]):
            c["not_scoreable_invalid"] += 1
            continue
        th = sorted({float(x["at_least"]): float(x["p_yes"]) for x in r.get("ladder") or []}.items())
        mono = all(b <= a + 1e-9 for (_, a), (_, b) in zip(th, th[1:]))
        rows[r["arm"]].append({"sport": SPORT, "game_id": r["game_id"], "player_id": str(r["player_id"]),
                               "statistic": r["statistic"], "as_of": r["_as_of"], "kickoff": _iso(_utc(r["kickoff"])),
                               "conditional_on_playing": True,
                               "projection": {"mean": float(mean), "median": float(med), "p10": float(p10), "p90": float(p90),
                                              "thresholds": [{"at_least": t, "probability": p} for t, p in th] if mono else []}})
        c["scoreable"] += 1
    return dict(rows), dict(sorted(c.items()))


def incumbent_probability_rows(recs: list[dict]) -> list[dict]:
    """value_scorecard probability rows from the V4/V5 Kalshi-strike ladders (P(X >= K), K the integer strike),
    flagged market_informed: they can never be independent evidence."""
    out = []
    for r in recs:
        if not r.get("kickoff") or _utc(r["_as_of"]) >= _utc(r["kickoff"]):
            continue
        for x in r.get("ladder") or []:
            k = kalshi_at_least(x.get("at_least"), ">=")
            if k is None or x.get("p_yes") is None:
                continue
            out.append({"sport": SPORT, "game_id": r["game_id"], "player_id": str(r["player_id"]), "statistic": r["statistic"],
                        "at_least": k, "as_of": r["_as_of"], "kickoff": _iso(_utc(r["kickoff"])), "p_yes": float(x["p_yes"]),
                        "probability_basis": "market_informed_incumbent", "model_version": r.get("arm"),
                        "market_informed": True, "_arm": r.get("arm"), "_kind": r.get("_kind")})
    return out


def missed_windows(store_root: str, games: set) -> list[dict]:
    """Capture windows recorded as missed (manifest `missed` lists) for the given games."""
    out = []
    d = os.path.join(store_root, store.MANIFEST_DIR)
    for f in sorted(glob.glob(os.path.join(d, "*" + store.MANIFEST_SUFFIX))):
        for m in json.load(open(f)).get("missed", []):
            if m.get("game_id") in games:
                out.append({"game_id": m["game_id"], "kind": m["kind"]})
    return out


def build(store_root: str, proj: dict, outcomes: dict, matured_games: set, *, evaluated_at: datetime, run_id: str,
          bootstrap: int = 1000, prereg_path: str = PREREG_PATH) -> tuple[dict, dict]:
    """(accuracy_scorecard record, value_scorecard record) for one evaluation run. Works with zero matured rows."""
    chal = [r for r in proj.get(MODEL_NAME, []) if r["game_id"] in matured_games]
    base = [r for r in proj.get(BASELINE_NAME, []) if r["game_id"] in matured_games]
    idents = {(r["game_id"], r["player_id"], r["statistic"]) for r in chal + base}
    outs = [outcomes[k] for k in sorted(idents) if k in outcomes]
    kickoff = {r["game_id"]: r["kickoff"] for r in chal + base}
    kind_of = {(r["game_id"], r["as_of"]): _kind(r) for r in chal + base}
    cohort_rows, quote_rows, qcounts = market_family(
        [(a, r) for a, r in listing_rows(store_root) if r.get("game_id") in matured_games], kickoff)
    recs = [r for r in incumbent_records(store_root, kind_of) if r.get("game_id") in matured_games]
    bench, bcounts = incumbent_benchmark(recs)
    comparators = {BASELINE_NAME: {"rows": base, "role": "statistical_baseline"}}
    for arm, rows in sorted(bench.items()):
        comparators[f"{arm}_market_informed"] = {"rows": rows, "role": "market_informed_benchmark",
                                                 "contract": "projection_only"}
    missed = missed_windows(store_root, matured_games)
    captured = sorted({(r["game_id"], _kind(r)) for r in chal + base})
    acc = run_accuracy(chal, outs, comparators=comparators, market_rows=cohort_rows, eligible=eligible_rows([chal, base]),
                       breakdowns={"capture_kind": lambda ctx: _kind(ctx["forecast"]),
                                   "position_group": lambda ctx: (ctx["forecast"].get("x_capture") or {}).get("position_group"),
                                   "capture_window": vendored("accuracy_scorecard").capture_window},
                       challenger_label=MODEL_NAME, bootstrap=bootstrap)
    accuracy = {
        "record": "accuracy_scorecard", "record_version": 1, "sport": SPORT, "run_id": run_id,
        "evaluated_at": evaluated_at.isoformat(), "status": "DESCRIPTIVE_ONLY_NOT_AUTOMATIC_PROMOTION",
        "arms": {MODEL_NAME: "challenger", BASELINE_NAME: "statistical_baseline",
                 **{n: "market_informed_benchmark" for n in comparators if n.endswith("_market_informed")}},
        "matured_games": len(matured_games), "matured_forecast_rows": {MODEL_NAME: len(chal), BASELINE_NAME: len(base)},
        "collection_accounting": {"captured_game_kinds": len(captured), "missed_capture_windows": len(missed),
                                  "missed_capture_windows_list": missed[:200],
                                  "note": "a missed (game, kind) window has no forecasts at all; it is counted here because "
                                          "its eligible players are unknown"},
        "market_informed_benchmark": {
            "family": "DATA_PLAYER_V4 / DATA_PLAYER_V5 (incumbent_diagnostic, MARKET_INFORMED_DIAGNOSTIC)",
            "role": "market_informed_benchmark: PRICE_OF_INDEPENDENCE_DIAGNOSTIC, never evidence of betting value",
            "state": "SCORED" if bench else ("NOT_SCOREABLE" if recs else "NO_RECORDS_FOR_MATURED_GAMES"),
            "counts": bcounts,
            "note": "the projection contract needs mean, median, p10 and p90; records carrying only p05/p50/p95 are not "
                    "scored and are not approximated"},
        "market_family_mapping": qcounts,
        "scorecards": {"conditional_on_playing": acc},
        "note": "Accuracy only, alongside the pure_gate compare scorecards; never evidence of betting value.",
    }
    # ---- value (dry-run diagnostic, preregistered)
    pr = load_prereg(prereg_path)
    outs_all = outs
    evals = {}
    primary_kind = pr["primary_capture_window"]
    kinds = sorted(({_kind(r) for r in chal} - {None}) | {primary_kind})
    for kind in kinds:
        rows = [r for r in chal if _kind(r) == kind]
        rep = evaluate_value(probability_rows(rows, basis="conditional_on_playing"), quote_rows, outs_all, pr,
                             market_informed=False)
        role = "primary" if kind == primary_kind else "secondary_descriptive"
        evals[f"{MODEL_NAME}/{kind}"] = value_entry(rep, arm=MODEL_NAME, window=kind, role=role,
                                                    eligible=(MODEL_NAME == pr["primary_arm"] and kind == primary_kind),
                                                    market_informed=False, dnp_policy=pr["dnp_policy"])
    rows = [r for r in chal if _kind(r) == primary_kind]
    alt = pr.get("dnp_sensitivity_policy")
    if alt:
        rep = evaluate_value(probability_rows(rows, basis="conditional_on_playing"), quote_rows, outs_all, pr,
                             market_informed=False, dnp_policy=alt)
        evals[f"{MODEL_NAME}/{primary_kind}/dnp_{alt}"] = value_entry(rep, arm=MODEL_NAME, window=primary_kind,
                                                                      role="dnp_sensitivity", eligible=False,
                                                                      market_informed=False, dnp_policy=alt)
    brows = [r for r in base if _kind(r) == primary_kind]
    rep = evaluate_value(probability_rows(brows, basis="conditional_on_playing"), quote_rows, outs_all, pr, market_informed=False)
    evals[f"{BASELINE_NAME}/{primary_kind}"] = value_entry(rep, arm=BASELINE_NAME, window=primary_kind,
                                                           role="secondary_descriptive", eligible=False,
                                                           market_informed=False, dnp_policy=pr["dnp_policy"])
    inc = incumbent_probability_rows(recs)
    for arm in pr.get("market_informed_arms", []):
        prows = [{k: v for k, v in r.items() if not k.startswith("_")} for r in inc
                 if r["_arm"] == arm and r["_kind"] == primary_kind]
        rep = evaluate_value(prows, quote_rows, outs_all, pr, market_informed=True)
        evals[f"{arm}/{primary_kind}"] = value_entry(rep, arm=arm, window=primary_kind, role="market_informed_diagnostic",
                                                     eligible=False, market_informed=True, dnp_policy=pr["dnp_policy"])
    prim = evals[f"{pr['primary_arm']}/{primary_kind}"]
    value = {
        "record": "value_scorecard", "record_version": 1, "sport": SPORT, "run_id": run_id,
        "evaluated_at": evaluated_at.isoformat(), "mode": VALUE_MODE, "wagering": NO_WAGERING,
        "preregistration": {"id": pr.get("preregistration_id"), "path": os.path.relpath(prereg_path, ROOT),
                            "file_sha256": file_sha256(prereg_path)},
        "primary": {"arm": pr["primary_arm"], "capture_window": primary_kind, "verdict": prim["verdict"],
                    "verdict_reasons": prim["verdict_reasons"], "n_decisions": prim["n_decisions"], "n_games": prim["n_games"]},
        "quote_mapping": qcounts, "evaluations": evals,
        "note": "Betting value only, separate from accuracy promotion. Only the preregistered PURE arm at the "
                "preregistered window is eligible for an independent-value verdict.",
    }
    return accuracy, value


def summary(accuracy: dict, value: dict) -> dict:
    """Compact stdout view of the two records."""
    return {"accuracy_scorecard": {lab: {p: s["state"] for p, s in sc["sample_state"].items()}
                                   for lab, sc in accuracy["scorecards"].items()},
            "market_informed_benchmark": accuracy["market_informed_benchmark"]["state"],
            "value_scorecard": {"mode": value["mode"], "primary": value["primary"],
                                "verdicts": {k: e["verdict"] for k, e in value["evaluations"].items()}}}


def build_safe(*args, **kwargs) -> tuple[dict, dict]:
    """`build`, but a scorecard failure never stops the collector: it is recorded as an ERROR record (fail closed,
    visible) and the pure_gate scorecards, outcomes and captures of the run are written as before."""
    try:
        return build(*args, **kwargs)
    except Exception as exc:  # noqa: BLE001 - recorded, never swallowed silently
        err = f"{type(exc).__name__}: {exc}"[:2000]
        base = {"record_version": 1, "sport": SPORT, "run_id": kwargs.get("run_id"),
                "evaluated_at": kwargs["evaluated_at"].isoformat() if kwargs.get("evaluated_at") else None,
                "state": "ERROR", "error": err}
        return ({"record": "accuracy_scorecard", **base, "scorecards": {}},
                {"record": "value_scorecard", **base, "mode": VALUE_MODE, "wagering": NO_WAGERING, "evaluations": {}})


def summary_safe(accuracy: dict, value: dict) -> dict:
    if accuracy.get("state") == "ERROR" or value.get("state") == "ERROR":
        return {"scorecards_state": "ERROR", "error": accuracy.get("error") or value.get("error")}
    return summary(accuracy, value)
