"""Why did the losing positions lose? An auditable decision tree over PREGAME evidence and closing prices.

Categories (one per losing settled position, first rule that applies wins):

  INSUFFICIENT_EVIDENCE  an undecoded combo, or no close quote on record. Nothing is inferred.
  BAD_EXPRESSION         the position was an incremental rung of a ladder already holding the same thesis (same game, same
                         primary axis, see exposure.axis_of), or a strictly cheaper expression of the same truth condition was
                         supplied. Detectable from the ledger alone; independent of the outcome.
  BAD_HANDICAP           a pregame model probability is ON RECORD for the side, it exceeded the close-implied probability by more
                         than ``HANDICAP_GAP``, and the close moved against the side. (Owner-selected fills carry no projection,
                         so this is reported as HANDICAP_UNASSESSABLE_NO_PROJECTION instead of being guessed.)
  BAD_PRICING            net CLV (close mid of the side held minus price paid minus fee per contract) <= -``CLV_TOLERANCE``: the
                         position paid more than the market ended up valuing it, fees included.
  VARIANCE               price at or better than the close (net CLV above -tolerance): the loss is an ordinary draw from the
                         probability the close implied.

Window-level inference never rests on per-position stories: ``fair_price_null`` compares actual wins to the sum of close-implied
probabilities with a game-clustered bootstrap interval for ROI. A short window (tens of positions) cannot declare any market
family profitable or unprofitable and the report says so via ``min_n_for_family_claim``.
"""
from __future__ import annotations

import math
from collections import Counter, defaultdict

import numpy as np

from .common import UNIT_DOLLARS
from .exposure import axis_of
from .ontology import COMBO_UNDECODED, SINGLE, classify_ticker

INSUFFICIENT, BAD_EXPRESSION, BAD_HANDICAP, BAD_PRICING, VARIANCE = (
    "INSUFFICIENT_EVIDENCE", "BAD_EXPRESSION", "BAD_HANDICAP", "BAD_PRICING", "VARIANCE")
CLV_TOLERANCE = 0.02          # 2 cents per contract, owner-adjustable
HANDICAP_GAP = 0.03           # model must exceed the close by 3 probability points to count as a handicap claim
MIN_N_FOR_FAMILY_CLAIM = 100  # positions per market family before any profitability statement is allowed


def _net(rec):
    return rec.settlement.get("net_canonical")


def classify_losses(records: list, *, model_probability: dict | None = None, cheaper_alt: dict | None = None) -> list:
    """records: reconcile.ContractRecord list. model_probability: {source_bet_key: p(side wins)} from a recorded pregame
    projection. cheaper_alt: {source_bet_key: ticker} when a strictly cheaper expression of the same event was quoted."""
    model_probability, cheaper_alt = model_probability or {}, cheaper_alt or {}
    first_on_axis = {}
    ordered = sorted([r for r in records if r.kind == SINGLE], key=lambda r: (r.executed_at or "", r.source_bet_key))
    axis_of_rec = {}
    for r in ordered:
        ax, _ = axis_of(classify_ticker(r.ticker), r.side)
        axis_of_rec[r.source_bet_key] = (r.game_key, ax)
        key = (r.game_key, ax)
        if ax and key not in first_on_axis:
            first_on_axis[key] = r.source_bet_key
    out = []
    for r in records:
        n = _net(r)
        if n is None or n >= 0:
            continue
        row = {"source_bet_key": r.source_bet_key, "family": r.family, "period": r.period, "net": n, "game_key": r.game_key}
        why = []
        if r.kind == COMBO_UNDECODED:
            row.update(category=INSUFFICIENT, reasons=["COMBO_LEGS_UNKNOWN"])
        elif r.clv.get("state") != "OK" and not (r.source_bet_key in cheaper_alt):
            ax = axis_of_rec.get(r.source_bet_key, (None, None))
            stacked = ax[1] and first_on_axis.get(ax) != r.source_bet_key
            if stacked:
                row.update(category=BAD_EXPRESSION, reasons=["LADDER_RUNG_ON_ALREADY_HELD_THESIS", "MISSING_CLOSE"])
            else:
                row.update(category=INSUFFICIENT, reasons=["MISSING_CLOSE"])
        else:
            ax = axis_of_rec.get(r.source_bet_key, (None, None))
            stacked = ax[1] and first_on_axis.get(ax) != r.source_bet_key
            if stacked:
                why.append("LADDER_RUNG_ON_ALREADY_HELD_THESIS")
            if r.source_bet_key in cheaper_alt:
                why.append("CHEAPER_EQUIVALENT_EXPRESSION:" + cheaper_alt[r.source_bet_key])
            if why:
                row.update(category=BAD_EXPRESSION, reasons=why)
            else:
                clv_net, mid = r.clv.get("clv_net_of_fee"), r.clv.get("close_mid_side")
                mp = model_probability.get(r.source_bet_key)
                if mp is None:
                    why.append("HANDICAP_UNASSESSABLE_NO_PROJECTION")
                elif mid is not None and mp - mid > HANDICAP_GAP and (r.clv.get("clv") or 0) < 0:
                    row.update(category=BAD_HANDICAP, reasons=["MODEL_ABOVE_CLOSE_AND_CLOSE_MOVED_AGAINST"])
                if "category" not in row:
                    if clv_net is not None and clv_net <= -CLV_TOLERANCE:
                        row.update(category=BAD_PRICING, reasons=why + ["NET_CLV_BELOW_TOLERANCE"])
                    elif clv_net is not None:
                        row.update(category=VARIANCE, reasons=why + ["PRICE_AT_OR_BETTER_THAN_CLOSE"], p_win_close=mid)
                    else:
                        row.update(category=INSUFFICIENT, reasons=why + ["NET_CLV_UNAVAILABLE"])
        out.append(row)
    return out


def fair_price_null(records: list, *, B=2000, seed=20261102) -> dict:
    """Held-to-settlement positions with a close: actual wins vs sum of close-implied win probabilities (z), and a game-clustered
    bootstrap interval for net ROI on outlay. Positions without a close are counted, not imputed."""
    rows = [r for r in records if r.kind == SINGLE and _net(r) is not None]
    with_close = [r for r in rows if r.clv.get("state") == "OK"]
    out = {"n_settled_single": len(rows), "n_with_close": len(with_close), "n_without_close": len(rows) - len(with_close)}
    if rows:
        outlay = np.array([r.stake or 0.0 for r in rows]); net = np.array([_net(r) for r in rows])
        games = np.array([r.game_key for r in rows])
        uniq, inv = np.unique(games, return_inverse=True)
        sn = np.bincount(inv, weights=net, minlength=len(uniq)); so = np.bincount(inv, weights=outlay, minlength=len(uniq))
        rng = np.random.default_rng(seed)
        roi = []
        for _ in range(B):
            p = rng.integers(0, len(uniq), len(uniq))
            roi.append(sn[p].sum() / max(so[p].sum(), 1e-9))
        out["roi_on_outlay"] = {"point": float(net.sum() / max(outlay.sum(), 1e-9)), "lo90": float(np.quantile(roi, 0.05)),
                                "hi90": float(np.quantile(roi, 0.95)), "n_game_clusters": int(len(uniq))}
    if with_close:
        p = np.array([r.clv["close_mid_side"] for r in with_close])
        wins = np.array([1.0 if (r.settlement.get("gross_return") or 0) > 0 else 0.0 for r in with_close])
        var = float((p * (1 - p)).sum())
        out["close_implied"] = {"expected_wins": float(p.sum()), "actual_wins": float(wins.sum()),
                                "z": float((wins.sum() - p.sum()) / math.sqrt(var)) if var > 0 else None}
    return out


def evaluate(records: list, **kw) -> dict:
    losses = classify_losses(records, **{k: v for k, v in kw.items() if k in ("model_probability", "cheaper_alt")})
    cat = Counter(l["category"] for l in losses)
    net_by = defaultdict(float)
    for l in losses:
        net_by[l["category"]] += l["net"]
    fam = defaultdict(lambda: {"n": 0, "net": 0.0})
    for r in records:
        if r.kind == SINGLE and _net(r) is not None:
            fam[r.family]["n"] += 1; fam[r.family]["net"] += _net(r)
    return {"n_losses": len(losses), "category_counts": dict(cat),
            "category_net_units": {k: round(v / UNIT_DOLLARS, 3) for k, v in net_by.items()},
            "window": fair_price_null(records),
            "family_claims": {f: {"n": v["n"], "claim_allowed": v["n"] >= MIN_N_FOR_FAMILY_CLAIM} for f, v in sorted(fam.items(), key=lambda kv: str(kv[0]))},
            "min_n_for_family_claim": MIN_N_FOR_FAMILY_CLAIM,
            "notes": ["Categories are decision-tree labels over available evidence, not causal proofs.",
                      "No family is declared profitable or unprofitable below min_n_for_family_claim positions."],
            "losses": losses}
