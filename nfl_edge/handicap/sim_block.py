"""The simulation layer's view of the board, attached to the handicap packet (read-only, stdlib-only).

The packet never computes a probability; it reads the incumbent ledger and, since sim-1.0.0, the newest
simulation projections file at or before the packet's build instant.  Every simulation number carries
three probabilities side by side -- football-only, market, reconciled -- and the reconciliation weight
that produced the third, so a reader can see how much of a disagreement the historical evidence let
stand.  A market the simulation could not price says why.
"""
from __future__ import annotations

import glob
import gzip
import json
import os
from datetime import datetime, timezone

DIRNAME = os.path.join("data", "shadow", "sim")
PRICED_STATES = ("PRICED",)
FOOTBALL_ONLY_STATES = ("FOOTBALL_ONLY_NO_RECONCILIATION", "MARKET_CENTRED_GAME")


def _stamp(dt: datetime | None) -> str | None:
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ") if dt else None


def load_latest(roots, at_or_before: datetime | None = None) -> tuple[dict, dict] | tuple[None, None]:
    """Newest projections file under any of ``roots`` whose run stamp is at or before the instant.
    Returns ({ticker: row}, manifest) or (None, None)."""
    files = []
    for root in roots:
        files += glob.glob(os.path.join(root, DIRNAME, "*", "*.projections.jsonl.gz"))
    stamp = _stamp(at_or_before)
    files = sorted(f for f in files if stamp is None or os.path.basename(f)[:16] <= stamp)
    if not files:
        return None, None
    path = files[-1]
    rows = {}
    with gzip.open(path, "rt") as f:
        for line in f:
            r = json.loads(line)
            rows[r["ticker"]] = r
    mpath = path.replace(".projections.jsonl.gz", ".manifest.json")
    manifest = json.load(open(mpath)) if os.path.exists(mpath) else {}
    manifest["_path"] = path
    return rows, manifest


def market_view(row: dict | None) -> dict | None:
    """The per-market block.  ``disagreement_vs_mid`` here is the RECONCILED probability minus the market
    mid where a validated weight exists, else None -- the raw football disagreement is reported separately
    and never ranked."""
    if not row:
        return None
    return {"sim_version": row.get("sim_version"), "support_state": row.get("support_state"), "support_reason": row.get("support_reason"),
            "p_football": row.get("p_football"), "p_market": row.get("p_market") if row.get("p_market") is not None else row.get("mid"),
            "p_reconciled": row.get("p_reconciled"), "reconcile_weight": row.get("reconcile_weight"),
            "football_mean": row.get("football_mean"), "market_mean": row.get("market_mean"), "final_mean": row.get("final_mean"),
            "football_sd": row.get("football_sd"), "p_active": row.get("p_active"),
            "reconciled_disagreement_vs_mid": (round(row["p_reconciled"] - row["mid"], 5)
                                               if row.get("p_reconciled") is not None and row.get("mid") is not None else None),
            "football_disagreement_vs_mid": row.get("football_disagreement_vs_mid"),
            # at weight 0 the reconciled MEAN is the market's, so whatever gap is left at this rung is the
            # football SHAPE, which has never been confirmed out of sample.  Say so on the row itself.
            "reconciled_disagreement_is_shape_only": (row.get("p_reconciled") is not None
                                                      and not (row.get("reconcile_weight") or 0) > 0),
            "ranked": bool((row.get("reconcile_weight") or 0) > 0),
            "center_source": row.get("center_source"), "label": "DISAGREEMENT ONLY -- REQUIRES HANDICAP"}


def game_view(game_rows: list, manifest: dict | None) -> dict:
    """Per-game summary: counts by support state, the centre used, and the reconciled disagreements ranked
    (validated weight only)."""
    counts = {}
    for r in game_rows:
        counts[r.get("support_state")] = counts.get(r.get("support_state"), 0) + 1
    priced = [r for r in game_rows if r.get("support_state") in PRICED_STATES and r.get("p_reconciled") is not None and r.get("mid") is not None]
    # ONLY a family that earned a non-zero deployed weight may be ranked.  At weight 0 the mean is the
    # market's, so the only thing left that can move p_reconciled away from the mid is the SHAPE
    # substitution -- and no shape claim has ever been confirmed out of sample (RECONCILIATION.md carries
    # it as an untested caveat).  Ranking that gap presents an unearned disagreement as the model's view:
    # on the first live Week 2 slate it put zero-weight families in 41% of the top-15 lists and supplied
    # three of the four reconciled-disagreement priority boosts, with rows whose FOOTBALL probability
    # agreed with the market to 0.003 showing a 0.035 "reconciled disagreement".
    rankable = [r for r in priced if (r.get("reconcile_weight") or 0) > 0]
    ranked = sorted(rankable, key=lambda r: -abs(r["p_reconciled"] - r["mid"]))
    # reported, never ranked -- the information is kept, it just carries no authority
    unranked = sorted((r for r in priced if not (r.get("reconcile_weight") or 0) > 0),
                      key=lambda r: -abs(r["p_reconciled"] - r["mid"]))
    centre = None
    if game_rows:
        r0 = game_rows[0]
        centre = {"source": r0.get("center_source"), "spread_home": r0.get("center_spread_home"), "total": r0.get("center_total")}
    # one line per (player, stat) with a football distribution: the projection table a handicapper reads
    seen = {}
    for r in game_rows:
        if r.get("football_mean") is None or not r.get("player_id"):
            continue
        key = (r["player_id"], r.get("stat"))
        if key not in seen:
            seen[key] = {"player_id": r["player_id"], "player_kalshi_id": r.get("player_kalshi_id"), "team": r.get("team"), "stat": r.get("stat"),
                         "football_mean": r.get("football_mean"), "football_sd": r.get("football_sd"), "market_mean": r.get("market_mean"),
                         "market_identification": r.get("market_identification"), "final_mean": r.get("final_mean"),
                         "reconcile_weight": r.get("reconcile_weight"), "p_active": r.get("p_active"), "n_rungs": 0}
        seen[key]["n_rungs"] += 1
    projections = sorted(seen.values(), key=lambda x: (x["team"] or "", x["stat"] or "", -(x["football_mean"] or 0)))
    return {"sim_version": (manifest or {}).get("sim_version"), "run_id": (manifest or {}).get("run_id"),
            "player_projections": projections,
            "generated_at": (manifest or {}).get("generated_at"), "counts_by_support_state": counts, "center": centre,
            "largest_reconciled_disagreements": [
                {"ticker": r["ticker"], "stat": r.get("stat"), "threshold": r.get("threshold"), "player_id": r.get("player_id"),
                 "mid": r.get("mid"), "p_football": r.get("p_football"), "p_reconciled": r.get("p_reconciled"),
                 "reconcile_weight": r.get("reconcile_weight"), "disagreement_vs_mid": round(r["p_reconciled"] - r["mid"], 5),
                 "football_mean": r.get("football_mean"), "market_mean": r.get("market_mean"), "final_mean": r.get("final_mean"),
                 "label": "DISAGREEMENT ONLY -- REQUIRES HANDICAP"} for r in ranked[:15]],
            "unranked_zero_weight_disagreements": [
                {"ticker": r["ticker"], "stat": r.get("stat"), "threshold": r.get("threshold"), "player_id": r.get("player_id"),
                 "mid": r.get("mid"), "p_football": r.get("p_football"), "p_reconciled": r.get("p_reconciled"),
                 "reconcile_weight": r.get("reconcile_weight"), "disagreement_vs_mid": round(r["p_reconciled"] - r["mid"], 5),
                 "label": "NOT RANKED -- this family earned no weight; the gap is the untested shape substitution"}
                for r in unranked[:15]],
            "ranking_basis": ("Only families with a non-zero DEPLOYED reconciliation weight are ranked. At weight 0 the "
                              "reconciled mean IS the market mean, so any remaining gap against the mid comes from the "
                              "football shape, which has never been confirmed out of sample; those rows are listed "
                              "under unranked_zero_weight_disagreements and carry no authority."),
            "note": ("The simulation's football-only probability is shown for every priced market; only the RECONCILED "
                     "probability -- the football distribution shrunk toward the market by a weight fitted out of sample "
                     "on the 2025 archive -- is ranked, and only where such a weight exists.")}
