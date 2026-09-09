"""Aggregate scorecard over the evaluation corpus: where does the model add information, and where not?

The question this exists to answer is comparative, so nothing is ever reported for the model alone. Every
metric is computed for THREE forecasters on the identical resolved set:

    model     the model's contract value at the snapshot
    market    the market mid at the SAME snapshot   (can the model beat the price it saw?)
    close     the market mid at the pregame close    (can the model beat the price nobody could see yet?)

A model Brier score with nothing beside it answers no question at all. `close` is the demanding comparison: it
is the market's last word, and beating it is the only version of "we know something" that matters.

FOUR REFUSALS BUILT IN
----------------------
* Only `settlement_kind == "binary"` rows enter calibration. A tied game paid $0.50 and a scratched player paid
  the pregame fair price; neither is a 0/1 realisation of a football event, and averaging them into a Brier
  score would move it for reasons that have nothing to do with forecasting. They are counted and reported
  separately.
* Rows whose close is MISSING or STALE are excluded from the headline CLV numbers. A stale close is not
  discarded, though: it is reported in its own block. Dropping it entirely would hide real movement (a rehearsal
  run four hours before kickoff has nothing BUT stale closes), and mixing it in would let an hour-old quote
  masquerade as the market's last word.
* An empty segment reports `n: 0` and no metrics. A zero Brier score reads like a measurement.
* `unchanged` and `no_view` movements are never folded into toward/away (the sign(0) trap documented in
  nfl_edge/research/clv.py).
"""
from __future__ import annotations

import math
from collections import defaultdict

from nfl_edge.shadow.evaluation import (
    CLOSE_OK, CLOSE_OK_STALE, DISAGREEMENT_BANDS, HORIZON_BANDS, probability_band,
)

BINARY = "binary"
# Segments every report slices by. The label is the report heading; the value is the row key.
SEGMENTS = (
    ("family", "family"),
    ("player statistic", "stat"),
    ("model probability band", "probability_band"),
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


def forecast_metrics(pairs) -> dict:
    """pairs: [(probability, realised 0/1)] -> Brier, log loss, mean signed error, n."""
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


def _binary(rows):
    """Rows that are a 0/1 realisation of a football event, with a model probability to score."""
    return [r for r in rows if r.get("settlement_kind") == BINARY and r.get("settled_yes") is not None
            and r.get("model_p") is not None]


def _with_close(rows):
    return [r for r in rows if r.get("close_status") == CLOSE_OK and r.get("close_mid") is not None]


def calibration_table(rows, width: float = 0.1) -> list:
    """Predicted vs actual by probability bucket, for the model and for the contemporaneous market."""
    buckets = defaultdict(list)
    for r in rows:
        buckets[probability_band(r["model_p"], width)].append(r)
    out = []
    for band in sorted(buckets):
        rs = buckets[band]
        out.append({"band": band, "n": len(rs),
                    "mean_model_p": round(_mean([r["model_p"] for r in rs]), 6),
                    "mean_market_mid": (round(_mean([r.get("mid_t") for r in rs]), 6)
                                        if any(r.get("mid_t") is not None for r in rs) else None),
                    "actual_rate": round(_mean([r["settled_yes"] for r in rs]), 6)})
    return out


def movement_counts(rows) -> dict:
    out = defaultdict(int)
    for r in rows:
        out[str(r.get("movement"))] += 1
    total_directional = out["toward"] + out["away"]
    return {"counts": dict(sorted(out.items())),
            "toward_share_of_directional": (round(out["toward"] / total_directional, 6)
                                            if total_directional else None),
            "n_directional": total_directional}


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


def forecaster_block(rows) -> dict:
    """The three-forecaster comparison on the identical resolved set."""
    b = _binary(rows)
    closed = [r for r in b if r.get("close_status") == CLOSE_OK and r.get("close_mid") is not None]
    return {
        "n_binary_settled": len(b),
        "model": forecast_metrics([(r["model_p"], r["settled_yes"]) for r in b]),
        "market_at_snapshot": forecast_metrics([(r.get("mid_t"), r["settled_yes"]) for r in b]),
        # the close comparison is only fair on the subset that HAS a usable close, so the model is re-scored
        # on exactly that subset alongside it
        "on_rows_with_a_usable_close": {
            "n": len(closed),
            "model": forecast_metrics([(r["model_p"], r["settled_yes"]) for r in closed]),
            "market_at_snapshot": forecast_metrics([(r.get("mid_t"), r["settled_yes"]) for r in closed]),
            "market_at_close": forecast_metrics([(r["close_mid"], r["settled_yes"]) for r in closed]),
        },
    }


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
        b = _binary(rs)
        out[k] = {"n": len(rs), "n_binary_settled": len(b),
                  "model": forecast_metrics([(r["model_p"], r["settled_yes"]) for r in b]),
                  "market_at_snapshot": forecast_metrics([(r.get("mid_t"), r["settled_yes"]) for r in b]),
                  "clv": clv_metrics(rs)}
    return out


def build_scorecard(rows: list, *, evaluation_version: str | None = None, min_segment_n: int = 1) -> dict:
    """Everything the weekly research question needs, from the evaluation corpus alone."""
    rows = [r for r in rows if evaluation_version is None or r.get("evaluation_version") == evaluation_version]
    settled = [r for r in rows if r.get("settlement_status") == "SETTLED"]
    binary = _binary(rows)
    sc = {
        "evaluation_version": evaluation_version,
        "n_evaluations": len(rows),
        "n_games": len({r.get("game_id") for r in rows if r.get("game_id")}),
        "counts": {
            "by_settlement_status": _tally(rows, "settlement_status"),
            "by_settlement_kind": _tally(settled, "settlement_kind"),
            "by_close_status": _tally(rows, "close_status"),
            "by_family": _tally(rows, "family"),
            "by_support_state": _tally(rows, "support_state"),
            "by_model_version": _tally(rows, "model_version"),
        },
        "excluded_from_calibration": {
            "not_settled": len([r for r in rows if r.get("settlement_status") != "SETTLED"]),
            "non_binary_settlement": len([r for r in settled if r.get("settlement_kind") != BINARY]),
            "no_model_probability": len([r for r in settled if r.get("model_p") is None]),
        },
        "model_vs_market": forecaster_block(rows),
        "calibration": calibration_table(binary) if binary else [],
        "clv": clv_metrics(rows),
        "segments": {},
    }
    for label, key in SEGMENTS:
        seg = segment(rows, key, min_n=min_segment_n)
        if seg:
            sc["segments"][label] = seg
    sc["bands"] = {"disagreement": [b[1] for b in DISAGREEMENT_BANDS],
                   "horizon": [b[1] for b in HORIZON_BANDS],
                   "width": [b[1] for b in WIDTH_BANDS],
                   "liquidity": [b[1] for b in LIQUIDITY_BANDS]}
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


def _metric_row(name, m):
    return (f"| {name} | {m.get('n', 0)} | {_fmt(m.get('brier'))} | {_fmt(m.get('log_loss'))} | "
            f"{_fmt(m.get('mean_predicted'))} | {_fmt(m.get('actual_rate'))} | {_fmt(m.get('mean_signed_error'))} |")


def render_report(sc: dict, *, title: str = "Shadow evaluation scorecard") -> str:
    L = [f"# {title}", ""]
    L.append(f"Evaluation corpus: **{sc['n_evaluations']} evaluations** across **{sc['n_games']} games**"
             + (f", evaluation version `{sc['evaluation_version']}`" if sc.get("evaluation_version") else ""))
    L.append("")
    if not sc["n_evaluations"]:
        L.append("The corpus is empty. There is nothing to report and no numbers are printed: this project "
                 "begins prospectively and nothing is backfilled.")
        return "\n".join(L)

    L += ["## What is in the corpus", "", "| settlement status | n |", "|---|---|"]
    for k, v in sc["counts"]["by_settlement_status"].items():
        L.append(f"| {k} | {v} |")
    L += ["", "| close status | n |", "|---|---|"]
    for k, v in sc["counts"]["by_close_status"].items():
        L.append(f"| {k} | {v} |")
    ex = sc["excluded_from_calibration"]
    L += ["", f"Excluded from calibration: {ex['not_settled']} not settled, "
              f"{ex['non_binary_settlement']} settled non-binary (tie split / no-snap fair price), "
              f"{ex['no_model_probability']} with no model probability.", ""]

    mv = sc["model_vs_market"]
    L += ["## 1. Calibration, and the model against the market", "",
          f"On the {mv['n_binary_settled']} binary-settled predictions:", "",
          "| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |",
          "|---|---|---|---|---|---|---|",
          _metric_row("model", mv["model"]),
          _metric_row("market mid at the same snapshot", mv["market_at_snapshot"]), ""]
    sub = mv["on_rows_with_a_usable_close"]
    if sub["n"]:
        L += [f"On the {sub['n']} of those with a legitimate pregame close, including the market's last word:", "",
              "| forecaster | n | Brier | log loss | mean predicted | actual rate | mean signed error |",
              "|---|---|---|---|---|---|---|",
              _metric_row("model", sub["model"]),
              _metric_row("market mid at snapshot", sub["market_at_snapshot"]),
              _metric_row("market mid at close", sub["market_at_close"]), ""]
        d = (sub["model"].get("brier"), sub["market_at_close"].get("brier"))
        if None not in d:
            better = "the model" if d[0] < d[1] else "the closing market"
            L.append(f"Lower Brier is better: **{better}** is ahead by {abs(d[0] - d[1]):.5f} on this set.")
            L.append("")
    if sc["calibration"]:
        L += ["### Calibration by probability bucket", "",
              "| model p band | n | mean model p | mean market mid | actual rate |", "|---|---|---|---|---|"]
        for row in sc["calibration"]:
            L.append(f"| {row['band']} | {row['n']} | {_fmt(row['mean_model_p'])} | "
                     f"{_fmt(row['mean_market_mid'])} | {_fmt(row['actual_rate'])} |")
        L.append("")

    clv = sc["clv"]
    L += ["## 2. Closing-line value and market movement", ""]
    if not clv.get("n"):
        L.append(f"No evaluation has a close inside the staleness budget "
                 f"({clv.get('excluded_no_usable_close', 0)} excluded), so no headline CLV is reported.")
    else:
        L += [f"On {clv['n']} evaluations with a legitimate close "
              f"({clv['excluded_no_usable_close']} excluded for a missing or stale close):", "",
              f"* mean signed CLV (midpoint): **{_fmt(clv['mean_signed_clv_mid'], 5)}**",
              f"* mean signed CLV (executable, crossing the spread): **{_fmt(clv['mean_signed_clv_executable'], 5)}**",
              f"* share with positive midpoint CLV: {_fmt(clv['positive_clv_share'])}",
              f"* movement: {clv['counts']}",
              f"* toward-share of directional moves: {_fmt(clv.get('toward_share_of_directional'))} "
              f"on {clv.get('n_directional', 0)} directional moves",
              f"* mean quote-width change: {_fmt(clv.get('mean_width_change'), 5)}; "
              f"mean liquidity change: {_fmt(clv.get('mean_liquidity_change'), 2)}", ""]
        L.append("`unchanged` and `no_view` are counted in their own buckets and never scored as a direction.")
        L.append("")
    stale = clv.get("on_stale_closes")
    if stale and stale.get("n"):
        L += ["Separately, on the {n} evaluations whose last pregame quote breached the staleness budget "
              "(reported, not mixed into the numbers above):".format(n=stale["n"]), "",
              f"* mean signed CLV (midpoint): {_fmt(stale['mean_signed_clv_mid'], 5)}",
              f"* toward-share of directional moves: {_fmt(stale.get('toward_share_of_directional'))} "
              f"on {stale.get('n_directional', 0)} moves", ""]

    L += ["## 3. Segmentation", ""]
    for label, seg in sc["segments"].items():
        L += [f"### by {label}", "",
              "| segment | n | binary settled | model Brier | market Brier | mean CLV (mid) | toward share |",
              "|---|---|---|---|---|---|---|"]
        for k, s in seg.items():
            L.append(f"| {k} | {s['n']} | {s['n_binary_settled']} | {_fmt(s['model'].get('brier'))} | "
                     f"{_fmt(s['market_at_snapshot'].get('brier'))} | "
                     f"{_fmt(s['clv'].get('mean_signed_clv_mid'), 5)} | "
                     f"{_fmt(s['clv'].get('toward_share_of_directional'))} |")
        L.append("")
    L += ["## Reading this report", "",
          "Nothing here promotes a model change. A single week is a handful of games and a Brier difference of "
          "a few thousandths on a few hundred correlated contracts is not evidence; the corpus exists so that "
          "the question can be asked again with more of it. Segments with small `n` are printed because "
          "hiding them would hide the sample size, not because they mean anything yet."]
    return "\n".join(L)
