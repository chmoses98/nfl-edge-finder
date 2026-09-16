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
            "center_source": row.get("center_source"), "label": "DISAGREEMENT ONLY -- REQUIRES HANDICAP"}


def game_view(game_rows: list, manifest: dict | None) -> dict:
    """Per-game summary: counts by support state, the centre used, and the reconciled disagreements ranked
    (validated weight only)."""
    counts = {}
    for r in game_rows:
        counts[r.get("support_state")] = counts.get(r.get("support_state"), 0) + 1
    priced = [r for r in game_rows if r.get("support_state") in PRICED_STATES and r.get("p_reconciled") is not None and r.get("mid") is not None]
    ranked = sorted(priced, key=lambda r: -abs(r["p_reconciled"] - r["mid"]))
    centre = None
    if game_rows:
        r0 = game_rows[0]
        centre = {"source": r0.get("center_source"), "spread_home": r0.get("center_spread_home"), "total": r0.get("center_total")}
    return {"sim_version": (manifest or {}).get("sim_version"), "run_id": (manifest or {}).get("run_id"),
            "generated_at": (manifest or {}).get("generated_at"), "counts_by_support_state": counts, "center": centre,
            "largest_reconciled_disagreements": [
                {"ticker": r["ticker"], "stat": r.get("stat"), "threshold": r.get("threshold"), "player_id": r.get("player_id"),
                 "mid": r.get("mid"), "p_football": r.get("p_football"), "p_reconciled": r.get("p_reconciled"),
                 "reconcile_weight": r.get("reconcile_weight"), "disagreement_vs_mid": round(r["p_reconciled"] - r["mid"], 5),
                 "football_mean": r.get("football_mean"), "market_mean": r.get("market_mean"), "final_mean": r.get("final_mean"),
                 "label": "DISAGREEMENT ONLY -- REQUIRES HANDICAP"} for r in ranked[:15]],
            "note": ("The simulation's football-only probability is shown for every priced market; only the RECONCILED "
                     "probability -- the football distribution shrunk toward the market by a weight fitted out of sample "
                     "on the 2025 archive -- is ranked, and only where such a weight exists.")}
