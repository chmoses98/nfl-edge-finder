"""Aggregate scorecard over the evaluation corpus: where does the model add information beyond the market?

THREE SEPARATIONS THIS MODULE EXISTS TO ENFORCE
-----------------------------------------------

**1. Event probability is not contract value.** The ledger stores `model_event_probability`
(P(football event | on the field)) and `model_contract_value` (E[payout of one YES contract]) as different
numbers, because for a player prop they ARE different: the contract value carries a participation discount that
has nothing to do with football. So they are scored in different spaces and never in the same table:

    EVENT space     model_event_probability vs the 0/1 realisation -> Brier, log loss, calibration buckets.
                    Only rows whose payout is binary qualify: that is exactly when participation semantics let
                    the football event be observed at all.
    CONTRACT space  model_contract_value, the market midpoint and the closing midpoint vs the actual payout ->
                    squared / absolute / signed payout error. No log loss: a $0.07 scalar payout is not a
                    Bernoulli outcome, and calling its error a log loss would be a category mistake.

The market lives in CONTRACT space, because a midpoint is a price. It appears in the event table only for rows
where the two spaces provably coincide (no participation branch), and is labelled as such.

**2. A repeated snapshot is not an independent observation.** The corpus holds every pregame snapshot of every
contract -- 27 snapshots of the same 401 NE-SEA tickers is 9,830 rows describing 401 contracts in one game.
Averaging them into one headline "n" would report a sample size 24x larger than the evidence. So every metric is
computed over an explicit SAMPLE UNIT:

    raw                    all snapshots. Descriptive diagnostics only, labelled as repeated and correlated.
    latest_pregame         one row per (game, ticker): the freshest legitimate pregame prediction. PRIMARY.
    T-24h / T-6h /         one row per (game, ticker) per horizon, chosen by the documented rule below.
      T-90m / T-30m

No "effective N" is computed. The three counts that matter -- observations, contracts, games -- are printed
beside every number.

**3. An empty set reports nothing.** A zero Brier score reads like a measurement. Segments and views with
nothing scoreable report their size and no metrics.
"""
from __future__ import annotations

import math
from collections import defaultdict

from nfl_edge.shadow.evaluation import (
    CLOSE_OK, CLOSE_OK_STALE, DISAGREEMENT_BANDS, HORIZON_BANDS, probability_band,
)

BINARY = "binary"
SETTLED = "SETTLED"

# Sample units. The label is what the report prints; `latest_pregame` is the primary contract-level view.
RAW = "raw"
LATEST_PREGAME = "latest_pregame"

# Canonical research horizons, in minutes before kickoff.
HORIZON_TARGETS = ((1440.0, "T-24h"), (360.0, "T-6h"), (90.0, "T-90m"), (30.0, "T-30m"))
# How far from the target a snapshot may sit and still represent that horizon.
#
# The shadow pricer runs every two hours, so no rule can do better than about one cadence either side of a
# target: demanding closer would report "unavailable" for horizons that were in fact observed as well as the
# cadence allows, and allowing more would let a five-hour-old snapshot be labelled T-90m -- which is exactly the
# silent mislabelling this bound exists to prevent. Every selected row reports its ACTUAL minutes to kickoff and
# the gap, so a reader never has to trust the label alone.
HORIZON_TOLERANCE_MINUTES = 120.0

SEGMENTS = (
    ("family", "family"),
    ("player statistic", "stat"),
    ("contract value band", "contract_value_band"),
    ("event probability band", "event_probability_band"),
    ("disagreement band", "disagreement_band"),
    ("model direction", "model_direction"),
    ("time to kickoff", "horizon_band"),
    ("model version", "model_version"),
    ("week", "week"),
    ("game", "game_id"),
    ("quote width band", "width_band"),
    ("liquidity band", "liquidity_band"),
    ("availability state", "availability_state"),
)
WIDTH_BANDS = ((0.02, "<=2c"), (0.05, "3-5c"), (0.10, "6-10c"), (float("inf"), ">10c"))
LIQUIDITY_BANDS = ((1e-9, "none"), (100.0, "<$100"), (1000.0, "$100-1k"), (float("inf"), ">$1k"))


def _band(v, bands):
    if v is None:
        return None
    for edge, label in bands:
        if v <= edge:          # the last edge is +inf, so a value always lands in a band
            return label
    return bands[-1][1]


def width_band(w):
    return _band(w, WIDTH_BANDS)


def liquidity_band(x):
    return _band(x, LIQUIDITY_BANDS)


def _mean(xs):
    xs = [x for x in xs if x is not None]
    return None if not xs else sum(xs) / len(xs)


# ======================================================================================================
# sample units
# ======================================================================================================

def _contract_key(row):
    return (row.get("game_id"), row.get("ticker"))


def _pregame(row):
    """Strictly pregame, provably. An unknown time to kickoff is not treated as pregame."""
    mtk = row.get("minutes_to_kickoff")
    return mtk is not None and float(mtk) > 0


def _sort_key(row):
    """Deterministic ordering for tie-breaks: newest observation, then prediction id."""
    return (str(row.get("observed_at") or ""), str(row.get("prediction_id") or ""))


def latest_pregame_view(rows) -> tuple[list, dict]:
    """One row per (game, ticker): the LAST legitimate pregame prediction for that contract.

    Deterministic: among rows with a known, positive time to kickoff, the smallest minutes-to-kickoff wins;
    ties break on (observed_at, prediction_id). A contract with no provably pregame row is not represented, and
    is counted as excluded rather than filled with a post-kickoff row.
    """
    groups = defaultdict(list)
    excluded = 0
    for r in rows:
        if _pregame(r):
            groups[_contract_key(r)].append(r)
        else:
            excluded += 1
    out = []
    for key in sorted(groups, key=lambda k: (str(k[0]), str(k[1]))):
        out.append(min(groups[key], key=lambda r: (float(r["minutes_to_kickoff"]), _sort_key(r))))
    meta = {"selection_rule": ("one row per (game, ticker): the smallest positive minutes_to_kickoff, "
                              "ties broken on (observed_at, prediction_id)"),
            "rows_not_provably_pregame_excluded": excluded,
            "actual_minutes_to_kickoff": _distribution([r.get("minutes_to_kickoff") for r in out])}
    return out, meta


def horizon_view(rows, target_minutes: float, *, tolerance: float = HORIZON_TOLERANCE_MINUTES) -> tuple[list, dict]:
    """One row per (game, ticker) representing the state of knowledge `target_minutes` before kickoff.

    The rule, stated once so no report can quietly use a different one:

      * candidates are rows with a known minutes_to_kickoff >= the target -- a snapshot taken LATER than the
        horizon knows things the horizon did not, so it can never represent it;
      * among those, the smallest minutes_to_kickoff wins: the freshest information a decision at T-target
        could have had;
      * the winner is accepted only if it sits within `tolerance` of the target. Otherwise the contract is
        UNAVAILABLE at this horizon, and is reported as such rather than represented by a snapshot from hours
        earlier.

    Ties break on (observed_at, prediction_id). Every selected row keeps its real distance to kickoff.
    """
    groups = defaultdict(list)
    for r in rows:
        if _pregame(r) and float(r["minutes_to_kickoff"]) >= target_minutes:
            groups[_contract_key(r)].append(r)
    all_contracts = {_contract_key(r) for r in rows if _pregame(r)}
    selected, unavailable = [], []
    for key in sorted(all_contracts, key=lambda k: (str(k[0]), str(k[1]))):
        cands = groups.get(key) or []
        if not cands:
            unavailable.append({"contract": list(key), "reason": "no snapshot at or before this horizon"})
            continue
        best = min(cands, key=lambda r: (float(r["minutes_to_kickoff"]), _sort_key(r)))
        gap = float(best["minutes_to_kickoff"]) - target_minutes
        if gap > tolerance:
            unavailable.append({"contract": list(key), "reason": "nearest snapshot is too far from the horizon",
                                "nearest_minutes_to_kickoff": float(best["minutes_to_kickoff"]),
                                "gap_minutes": round(gap, 1)})
            continue
        selected.append(best)
    meta = {"target_minutes": target_minutes, "tolerance_minutes": tolerance,
            "selection_rule": ("freshest snapshot at or before the horizon, within the tolerance; "
                               "ties broken on (observed_at, prediction_id)"),
            "n_selected": len(selected), "n_unavailable": len(unavailable),
            "n_contracts_considered": len(all_contracts),
            "actual_minutes_to_kickoff": _distribution([r.get("minutes_to_kickoff") for r in selected]),
            "unavailable_examples": unavailable[:10]}
    return selected, meta


def _distribution(values):
    vs = sorted(float(v) for v in values if v is not None)
    if not vs:
        return {"n": 0}
    return {"n": len(vs), "min": round(vs[0], 1), "median": round(vs[len(vs) // 2], 1),
            "max": round(vs[-1], 1), "mean": round(sum(vs) / len(vs), 1)}


def sample_unit_counts(rows) -> dict:
    return {"n_observations": len(rows),
            "n_unique_contracts": len({_contract_key(r) for r in rows}),
            "n_games": len({r.get("game_id") for r in rows if r.get("game_id")})}


# ======================================================================================================
# EVENT space: probabilities against a 0/1 realisation
# ======================================================================================================

def _event_rows(rows):
    """Rows where the football event is a valid binary realisation AND an event probability exists."""
    return [r for r in rows
            if r.get("event_binary_valid") and r.get("settled_yes") in (0.0, 1.0, 0, 1)
            and r.get("model_event_probability") is not None]


def probability_metrics(pairs) -> dict:
    """pairs: [(probability, realised 0/1)] -> Brier, log loss, mean predicted, actual rate, n."""
    ps = [(float(p), float(r)) for p, r in pairs if p is not None and r is not None]
    if not ps:
        return {"n": 0}
    brier = _mean([(p - r) ** 2 for p, r in ps])
    ll = _mean([-(r * math.log(max(min(p, 1 - 1e-9), 1e-9)) + (1 - r) * math.log(max(min(1 - p, 1 - 1e-9), 1e-9)))
                for p, r in ps])
    return {"n": len(ps), "brier": round(brier, 6), "log_loss": round(ll, 6),
            "mean_predicted": round(_mean([p for p, _ in ps]), 6),
            "actual_rate": round(_mean([r for _, r in ps]), 6),
            "mean_signed_error": round(_mean([p - r for p, r in ps]), 6)}


def event_calibration(rows, *, width: float = 0.1) -> dict:
    """Calibration of the FOOTBALL model: `model_event_probability` against the realised event.

    The market appears only on the subset where contract value and event probability provably coincide -- i.e.
    contracts with no participation branch. Elsewhere a midpoint is a price that carries the participation
    discount, and scoring it against a football event would penalise it for being a contract.
    """
    er = _event_rows(rows)
    coincide = [r for r in er if r.get("model_contract_value") is not None
                and abs(float(r["model_contract_value"]) - float(r["model_event_probability"])) <= 1e-9]
    buckets = defaultdict(list)
    for r in er:
        buckets[probability_band(r["model_event_probability"], width)].append(r)
    table = []
    for band in sorted(buckets):
        rs = buckets[band]
        table.append({"band": band, "n": len(rs),
                      "mean_event_probability": round(_mean([r["model_event_probability"] for r in rs]), 6),
                      "actual_event_rate": round(_mean([float(r["settled_yes"]) for r in rs]), 6)})
    return {"n_event_realisations": len(er),
            "model_event_probability": probability_metrics(
                [(r["model_event_probability"], r["settled_yes"]) for r in er]),
            "market_where_spaces_coincide": {
                "n_contracts": len(coincide),
                "note": ("market midpoint scored against the event, restricted to contracts whose value equals "
                         "their event probability (no participation branch); elsewhere a price is not an event "
                         "probability"),
                **probability_metrics([(r.get("mid_t"), r["settled_yes"]) for r in coincide])},
            "calibration_by_event_probability": table,
            "excluded": {"no_binary_event_realisation": len(rows) - len(er)}}


# ======================================================================================================
# CONTRACT space: payouts against the actual payout
# ======================================================================================================

def _payout_rows(rows):
    """Rows whose ACTUAL payout is exactly known -- the only rows a payout error may be computed on."""
    return [r for r in rows if r.get("settlement_status") == SETTLED
            and r.get("exact_payout_known") and r.get("settled_yes") is not None]


def payout_metrics(pairs) -> dict:
    """pairs: [(predicted payout, actual payout)] -> squared / absolute / signed error.

    Deliberately no log loss. On purely binary payouts `mean_squared_payout_error` coincides with a Brier score;
    on a scalar payout it is the only one of the two that means anything.
    """
    ps = [(float(p), float(a)) for p, a in pairs if p is not None and a is not None]
    if not ps:
        return {"n": 0}
    return {"n": len(ps),
            "mean_squared_payout_error": round(_mean([(p - a) ** 2 for p, a in ps]), 6),
            "mean_absolute_payout_error": round(_mean([abs(p - a) for p, a in ps]), 6),
            "mean_signed_payout_error": round(_mean([p - a for p, a in ps]), 6),
            "mean_predicted_payout": round(_mean([p for p, _ in ps]), 6),
            "mean_actual_payout": round(_mean([a for _, a in ps]), 6)}


def contract_payout_quality(rows) -> dict:
    """Model contract value, market midpoint and closing midpoint against the ACTUAL payout."""
    pr = _payout_rows(rows)
    closed = [r for r in pr if r.get("close_status") == CLOSE_OK and r.get("close_mid") is not None]
    kinds = defaultdict(int)
    for r in pr:
        kinds[str(r.get("settlement_kind"))] += 1
    excluded_inexact = [r for r in rows if r.get("settlement_status") == SETTLED and not r.get("exact_payout_known")]
    return {"n_exact_payouts": len(pr),
            "by_settlement_kind": dict(sorted(kinds.items())),
            "model_contract_value": payout_metrics([(r.get("model_contract_value"), r["settled_yes"]) for r in pr]),
            "market_at_snapshot": payout_metrics([(r.get("mid_t"), r["settled_yes"]) for r in pr]),
            "on_rows_with_a_usable_close": {
                "n": len(closed),
                "model_contract_value": payout_metrics(
                    [(r.get("model_contract_value"), r["settled_yes"]) for r in closed]),
                "market_at_snapshot": payout_metrics([(r.get("mid_t"), r["settled_yes"]) for r in closed]),
                "market_at_close": payout_metrics([(r["close_mid"], r["settled_yes"]) for r in closed])},
            "excluded": {
                "settled_without_an_exact_payout": len(excluded_inexact),
                "settled_without_an_exact_payout_reasons": _tally(excluded_inexact, "settlement_kind"),
                "not_settled": len([r for r in rows if r.get("settlement_status") != SETTLED])}}


# ======================================================================================================
# closing-line value
# ======================================================================================================

def movement_counts(rows) -> dict:
    out = defaultdict(int)
    for r in rows:
        out[str(r.get("movement"))] += 1
    total_directional = out["toward"] + out["away"]
    return {"counts": dict(sorted(out.items())),
            "toward_share_of_directional": (round(out["toward"] / total_directional, 6)
                                            if total_directional else None),
            "n_directional": total_directional}


def _with_close(rows):
    return [r for r in rows if r.get("close_status") == CLOSE_OK and r.get("close_mid") is not None]


def _clv_block(closed, total) -> dict:
    if not closed:
        return {"n": 0, "excluded_no_usable_close": total}
    return {"n": len(closed),
            "excluded_no_usable_close": total - len(closed),
            "mean_signed_clv_mid": round(_mean([r.get("signed_clv_mid") for r in closed]) or 0.0, 6),
            "mean_signed_clv_executable": round(_mean([r.get("signed_clv_executable") for r in closed]) or 0.0, 6),
            "positive_clv_share": round(_mean([1.0 if (r.get("signed_clv_mid") or 0) > 0 else 0.0
                                               for r in closed]), 6),
            "mean_width_change": (round(_mean([r.get("width_change") for r in closed]), 6)
                                  if any(r.get("width_change") is not None for r in closed) else None),
            "mean_liquidity_change": (round(_mean([r.get("liquidity_change") for r in closed]), 6)
                                      if any(r.get("liquidity_change") is not None for r in closed) else None),
            **movement_counts(closed)}


def clv_metrics(rows) -> dict:
    """CLV against a fresh close, plus a separate block for closes that breached the staleness budget."""
    out = _clv_block(_with_close(rows), len(rows))
    stale = [r for r in rows if r.get("close_status") == CLOSE_OK_STALE and r.get("close_mid") is not None]
    if stale:
        out["on_stale_closes"] = _clv_block(stale, len(stale))
    return out


# ======================================================================================================
# assembly
# ======================================================================================================

def metric_block(rows) -> dict:
    """Every metric, for one sample unit."""
    return {**sample_unit_counts(rows),
            "event_calibration": event_calibration(rows),
            "contract_payout_quality": contract_payout_quality(rows),
            "clv": clv_metrics(rows)}


def _segment_value(row, key):
    if key == "width_band":
        return width_band(row.get("width_t"))
    if key == "liquidity_band":
        return liquidity_band(row.get("liquidity_t"))
    return row.get(key)


def segment(rows, key, *, min_n: int = 1) -> dict:
    groups = defaultdict(list)
    for r in rows:
        groups[str(_segment_value(r, key))].append(r)
    out = {}
    for k, rs in sorted(groups.items()):
        if len(rs) < min_n:
            continue
        er, pr = _event_rows(rs), _payout_rows(rs)
        out[k] = {"n_contracts": len(rs), "n_event_realisations": len(er), "n_exact_payouts": len(pr),
                  "event_brier": probability_metrics(
                      [(r["model_event_probability"], r["settled_yes"]) for r in er]).get("brier"),
                  "model_payout_mse": payout_metrics(
                      [(r.get("model_contract_value"), r["settled_yes"]) for r in pr]).get("mean_squared_payout_error"),
                  "market_payout_mse": payout_metrics(
                      [(r.get("mid_t"), r["settled_yes"]) for r in pr]).get("mean_squared_payout_error"),
                  "clv": clv_metrics(rs)}
    return out


def build_scorecard(rows: list, *, evaluation_version: str | None = None, min_segment_n: int = 1,
                    horizon_tolerance: float = HORIZON_TOLERANCE_MINUTES) -> dict:
    """Everything the weekly research question needs, from the evaluation corpus alone."""
    rows = [r for r in rows if evaluation_version is None or r.get("evaluation_version") == evaluation_version]
    settled = [r for r in rows if r.get("settlement_status") == SETTLED]
    contract_rows, contract_meta = latest_pregame_view(rows)

    sc = {
        "evaluation_version": evaluation_version,
        "primary_sample_unit": LATEST_PREGAME,
        "sample_units": {
            RAW: {**sample_unit_counts(rows),
                  "note": ("every immutable pregame snapshot. These are REPEATED, CORRELATED observations of the "
                           "same contracts -- diagnostics only. The contract count, not the observation count, "
                           "is the sample size.")},
            LATEST_PREGAME: {**sample_unit_counts(contract_rows), **contract_meta,
                             "note": "one row per (game, ticker); the primary contract-level view"},
        },
        "counts": {
            "by_settlement_status": _tally(rows, "settlement_status"),
            "by_settlement_kind": _tally(settled, "settlement_kind"),
            "by_close_status": _tally(rows, "close_status"),
            "by_family": _tally(rows, "family"),
            "by_support_state": _tally(rows, "support_state"),
            "by_model_version": _tally(rows, "model_version"),
            "by_exact_payout_known": _tally(settled, "exact_payout_known"),
        },
        "views": {RAW: metric_block(rows), LATEST_PREGAME: metric_block(contract_rows)},
        "horizons": {},
        "segments": {},
        "bands": {"disagreement": [b[1] for b in DISAGREEMENT_BANDS],
                  "horizon": [b[1] for b in HORIZON_BANDS],
                  "width": [b[1] for b in WIDTH_BANDS],
                  "liquidity": [b[1] for b in LIQUIDITY_BANDS]},
    }
    for target, label in HORIZON_TARGETS:
        sel, meta = horizon_view(rows, target, tolerance=horizon_tolerance)
        sc["horizons"][label] = {**meta, **(metric_block(sel) if sel else sample_unit_counts(sel))}
    sc["horizons"]["latest pregame"] = {**contract_meta, **metric_block(contract_rows),
                                        "note": "the same rows as the primary contract view"}
    # Segments are computed on the CONTRACT view: a segment of repeated snapshots would carry the same
    # sample-size illusion the views exist to remove.
    for label, key in SEGMENTS:
        seg = segment(contract_rows, key, min_n=min_segment_n)
        if seg:
            sc["segments"][label] = seg
    return sc


def _tally(rows, key):
    out = defaultdict(int)
    for r in rows:
        out[str(r.get(key))] += 1
    return dict(sorted(out.items()))


# ======================================================================================================
# report rendering
# ======================================================================================================

def _fmt(v, nd=4):
    if v is None:
        return "-"
    if isinstance(v, float):
        return f"{v:.{nd}f}"
    return str(v)


def _prob_row(name, m):
    return (f"| {name} | {m.get('n', 0)} | {_fmt(m.get('brier'))} | {_fmt(m.get('log_loss'))} | "
            f"{_fmt(m.get('mean_predicted'))} | {_fmt(m.get('actual_rate'))} | {_fmt(m.get('mean_signed_error'))} |")


def _payout_row(name, m):
    return (f"| {name} | {m.get('n', 0)} | {_fmt(m.get('mean_squared_payout_error'), 5)} | "
            f"{_fmt(m.get('mean_absolute_payout_error'), 5)} | {_fmt(m.get('mean_signed_payout_error'), 5)} | "
            f"{_fmt(m.get('mean_predicted_payout'))} | {_fmt(m.get('mean_actual_payout'))} |")


def render_report(sc: dict, *, title: str = "Shadow evaluation scorecard") -> str:
    L = [f"# {title}", ""]
    raw = sc.get("sample_units", {}).get(RAW, {})
    con = sc.get("sample_units", {}).get(LATEST_PREGAME, {})
    if not raw.get("n_observations"):
        L.append("The corpus is empty. There is nothing to report and no numbers are printed: this project "
                 "begins prospectively and nothing is backfilled.")
        return "\n".join(L)
    L += ["## Sample units", "",
          "| unit | observations | contracts | games |", "|---|---|---|---|",
          f"| raw snapshots (correlated) | {raw['n_observations']} | {raw['n_unique_contracts']} | {raw['n_games']} |",
          f"| **latest pregame per contract (primary)** | {con['n_observations']} | {con['n_unique_contracts']} | {con['n_games']} |",
          "",
          f"The raw view holds {raw['n_observations']} snapshots of {raw['n_unique_contracts']} contracts: they "
          "are repeated observations of the same markets and are reported as diagnostics, never as an "
          "independent sample size. No effective N is computed.", ""]

    L += ["## What is in the corpus", "", "| settlement status | n |", "|---|---|"]
    for k, v in sc["counts"]["by_settlement_status"].items():
        L.append(f"| {k} | {v} |")
    L += ["", "| close status | n |", "|---|---|"]
    for k, v in sc["counts"]["by_close_status"].items():
        L.append(f"| {k} | {v} |")
    L.append("")

    view = sc["views"][LATEST_PREGAME]
    ec = view["event_calibration"]
    L += ["## 1. Event-probability calibration (the football model)", "",
          f"`model_event_probability` against the realised football event, on the "
          f"{ec['n_event_realisations']} contracts whose payout is a 0/1 realisation "
          f"({ec['excluded']['no_binary_event_realisation']} excluded: no valid binary realisation).", "",
          "| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |",
          "|---|---|---|---|---|---|---|",
          _prob_row("model event probability", ec["model_event_probability"])]
    mk = ec["market_where_spaces_coincide"]
    if mk.get("n"):
        L.append(_prob_row("market mid (only where value == event probability)", mk))
    L.append("")
    if ec["calibration_by_event_probability"]:
        L += ["| event probability band | n | mean predicted | actual event rate |", "|---|---|---|---|"]
        for row in ec["calibration_by_event_probability"]:
            L.append(f"| {row['band']} | {row['n']} | {_fmt(row['mean_event_probability'])} | "
                     f"{_fmt(row['actual_event_rate'])} |")
        L.append("")

    cp = view["contract_payout_quality"]
    L += ["## 2. Contract-payout quality (the model against the market)", "",
          f"`model_contract_value` and the market against the ACTUAL payout, on the {cp['n_exact_payouts']} "
          f"contracts whose payout is exactly known ({cp['excluded']['settled_without_an_exact_payout']} settled "
          f"without an exact payout, {cp['excluded']['not_settled']} not settled). Squared error, not log loss: "
          "a scalar payout is not a Bernoulli outcome.", "",
          "| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |",
          "|---|---|---|---|---|---|---|",
          _payout_row("model contract value", cp["model_contract_value"]),
          _payout_row("market mid at the same snapshot", cp["market_at_snapshot"]), ""]
    sub = cp["on_rows_with_a_usable_close"]
    if sub["n"]:
        L += [f"On the {sub['n']} of those with a legitimate pregame close, including the market's last word:", "",
              "| forecaster | n | MSE | MAE | mean signed | mean predicted | mean actual |",
              "|---|---|---|---|---|---|---|",
              _payout_row("model contract value", sub["model_contract_value"]),
              _payout_row("market mid at snapshot", sub["market_at_snapshot"]),
              _payout_row("market mid at close", sub["market_at_close"]), ""]
        a = sub["model_contract_value"].get("mean_squared_payout_error")
        b = sub["market_at_close"].get("mean_squared_payout_error")
        if a is not None and b is not None:
            better = "the model" if a < b else "the closing market"
            L += [f"Lower is better: **{better}** is ahead by {abs(a - b):.5f} in squared payout error on this "
                  "set.", ""]

    clv = view["clv"]
    L += ["## 3. Closing-line value and market movement", ""]
    if not clv.get("n"):
        L.append(f"No contract has a close inside the staleness budget "
                 f"({clv.get('excluded_no_usable_close', 0)} excluded), so no headline CLV is reported.")
    else:
        L += [f"On {clv['n']} contracts with a legitimate close "
              f"({clv['excluded_no_usable_close']} excluded for a missing or stale close):", "",
              f"* mean signed CLV (midpoint): **{_fmt(clv['mean_signed_clv_mid'], 5)}**",
              f"* mean signed CLV (executable, crossing the spread): **{_fmt(clv['mean_signed_clv_executable'], 5)}**",
              f"* share with positive midpoint CLV: {_fmt(clv['positive_clv_share'])}",
              f"* movement: {clv['counts']}",
              f"* toward-share of directional moves: {_fmt(clv.get('toward_share_of_directional'))} "
              f"on {clv.get('n_directional', 0)} directional moves", ""]
        L.append("`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.")
        L.append("")
    stale = clv.get("on_stale_closes")
    if stale and stale.get("n"):
        L += [f"Separately, on the {stale['n']} contracts whose last pregame quote breached the staleness budget "
              "(reported, not mixed into the numbers above):", "",
              f"* mean signed CLV (midpoint): {_fmt(stale['mean_signed_clv_mid'], 5)}",
              f"* toward-share of directional moves: {_fmt(stale.get('toward_share_of_directional'))} "
              f"on {stale.get('n_directional', 0)} moves", ""]

    L += ["## 4. Canonical horizons", "",
          f"One row per contract per horizon. Selection: the freshest snapshot at or before the horizon, within "
          f"{HORIZON_TOLERANCE_MINUTES:.0f} minutes of it; otherwise the contract is unavailable at that horizon. "
          "The actual distance to kickoff is reported, so no label has to be trusted on its own.", "",
          "| horizon | contracts | unavailable | actual minutes to kickoff (min/median/max) | event Brier | model payout MSE | market payout MSE |",
          "|---|---|---|---|---|---|---|"]
    for label in [lbl for _, lbl in HORIZON_TARGETS] + ["latest pregame"]:
        h = sc["horizons"].get(label) or {}
        d = h.get("actual_minutes_to_kickoff") or {}
        ecb = (h.get("event_calibration") or {}).get("model_event_probability") or {}
        cpb = (h.get("contract_payout_quality") or {})
        L.append(f"| {label} | {h.get('n_observations', h.get('n_selected', 0))} | "
                 f"{h.get('n_unavailable', '-')} | "
                 f"{_fmt(d.get('min'), 0)}/{_fmt(d.get('median'), 0)}/{_fmt(d.get('max'), 0)} | "
                 f"{_fmt(ecb.get('brier'))} | "
                 f"{_fmt((cpb.get('model_contract_value') or {}).get('mean_squared_payout_error'), 5)} | "
                 f"{_fmt((cpb.get('market_at_snapshot') or {}).get('mean_squared_payout_error'), 5)} |")
    L.append("")

    L += ["## 5. Segmentation (contract view)", ""]
    for label, seg in sc["segments"].items():
        L += [f"### by {label}", "",
              "| segment | contracts | event realisations | exact payouts | event Brier | model payout MSE | market payout MSE | mean CLV (mid) |",
              "|---|---|---|---|---|---|---|---|"]
        for k, s in seg.items():
            L.append(f"| {k} | {s['n_contracts']} | {s['n_event_realisations']} | {s['n_exact_payouts']} | "
                     f"{_fmt(s['event_brier'])} | {_fmt(s['model_payout_mse'], 5)} | "
                     f"{_fmt(s['market_payout_mse'], 5)} | {_fmt(s['clv'].get('mean_signed_clv_mid'), 5)} |")
        L.append("")
    L += ["## Reading this report", "",
          "Nothing here promotes a model change. The sample size is the CONTRACT count, not the observation "
          "count, and one week is a few hundred correlated contracts in a handful of games -- a payout-error or "
          "Brier difference of a few thousandths is not evidence. Segments with small counts are printed "
          "because hiding them would hide the sample size, not because they mean anything yet."]
    return "\n".join(L)
