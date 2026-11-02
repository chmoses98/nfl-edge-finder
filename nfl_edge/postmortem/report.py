"""Machine-readable window report + dashboard text. REDACTED BY DEFAULT because this repository is public and the owner's ledger is not.

Redacted form: counts, flag counts, category counts and booleans only. No ticker, key, stake, price, unit size or P&L.
Private form (``redact=False``) is written only to a path OUTSIDE the repository working tree.
"""
from __future__ import annotations

import glob
import json
import os

from . import POSTMORTEM_VERSION
from . import exposure as X
from . import loss_eval as LE
from . import reconcile as R

ITEMS = (   # (id, title, status, note)
    ("1", "Immutable per-contract reconciliation", "DONE", "reconcile.py; missing evidence is a MISSING_* flag; combos without legs are COMBO_UNDECODED"),
    ("1b", "Recommendation / model attribution for the window", "UNRESOLVED", "no real (non-test) recommendation exists on handicap-data for these fills; they are owner-selected, not model picks"),
    ("1c", "Order id / fill ids per fill", "UNRESOLVED", "the routed wager rows carry no exchange order or fill ids (router-side change; see PR note)"),
    ("2", "Fee-inclusive break-even, calibrated fair probability, bet-up-to", "DONE", "fairvalue.py; None whenever calibration or fee is missing"),
    ("2b", "PIT guards (projection, injuries, confirmed QB, quote, kickoff, price provenance)", "DONE_NOT_WIRED", "guards.py is restriction-only; wiring into pinned gates.py/preflight.py needs owner authorization"),
    ("3", "Correlation groups + game/daily exposure flags (>5U, >15U)", "DONE", "exposure.py; flags only, no cap, per NFL_OPERATING_POLICY"),
    ("4", "Key-number distributions + held-out evaluation", "DONE", "research/postmortem_2026-11-02/distribution_eval.json"),
    ("4b", "Matchup evidence (EPA, pace, ST) improves on the closing market", "NOT_DEMONSTRATED", "no held-out gain over market-only; do not activate"),
    ("4c", "Injury / confirmed-QB history for the distribution model", "UNRESOLVED", "no point-in-time injury history before the 2026 availability_pit capture"),
    ("5", "Loss classification", "DONE_PARTIAL", "loss_eval.py; closes for the window are not published, so most losses are INSUFFICIENT_EVIDENCE"),
    ("5b", "Closing prices for weeks 5-8", "UNRESOLVED", "shadow-v2-settle.yml has been cancelled at its job limit (docs/research/ACTUAL_WAGER_DIAGNOSIS_2026-10-25.md)"),
    ("6", "NBA router PR #48", "OTHER_REPO", "see kalshi-bet-router / nba-edge-finder PRs"),
)


def load_ledger(root: str) -> dict:
    def load(kind):
        return [json.load(open(p)) for p in sorted(glob.glob(os.path.join(root, "data", kind, "**", "*.json"), recursive=True))]
    return {"wagers": load("imported_wagers"), "settlements": load("wager_settlements"),
            "amendments": load("wager_settlement_amendments"), "recommendations": load("recommendations")}


def in_window(w: dict, start: str, end: str) -> bool:
    return start <= str(w.get("executed_at", ""))[:10] <= end


def build(ledger: dict, start: str, end: str, *, closes=None, availability=None, kickoffs=None, legs_by_ticker=None, redact=True) -> dict:
    wagers = [w for w in ledger["wagers"] if in_window(w, start, end) and not w.get("test_only")]
    recs = R.reconcile(wagers, ledger["settlements"], ledger["amendments"], recommendations=ledger.get("recommendations"),
                       closes=closes, availability=availability, kickoffs=kickoffs, legs_by_ticker=legs_by_ticker)
    positions = [{"ticker": r.ticker, "side": r.side, "stake": r.stake, "game_date": next((w.get("game_date") for w in wagers if w["source_bet_key"] == r.source_bet_key), None),
                  "executed_at": r.executed_at} for r in recs]
    exp = X.aggregate(positions, legs_by_ticker=legs_by_ticker)
    loss = LE.evaluate(recs)
    out = {"version": POSTMORTEM_VERSION, "window": [start, end], "reconciliation": R.redact(recs),
           "exposure": {"n_game_flags": sum(1 for f in exp["flags"] if f["kind"] == "GAME_OVER_LIMIT"),
                        "n_group_flags": sum(1 for f in exp["flags"] if f["kind"] == "GROUP_OVER_LIMIT"),
                        "n_day_flags": sum(1 for f in exp["flags"] if f["kind"] == "DAY_OVER_LIMIT"),
                        "policy": "flags only; no cap"},
           "loss_evaluation": {"n_losses": loss["n_losses"], "category_counts": loss["category_counts"],
                               "close_coverage": {k: loss["window"].get(k) for k in ("n_settled_single", "n_with_close", "n_without_close")},
                               "min_n_for_family_claim": loss["min_n_for_family_claim"],
                               "family_claims_allowed": {f: v["claim_allowed"] for f, v in loss["family_claims"].items()}},
           "items": [dict(zip(("id", "title", "status", "note"), i)) for i in ITEMS]}
    if not redact:
        out["private"] = {"exposure": exp, "losses": loss["losses"], "window_stats": loss["window"], "records": [r.to_dict() for r in recs]}
    return out


def dashboard(report: dict) -> str:
    rc, lo, ex = report["reconciliation"], report["loss_evaluation"], report["exposure"]
    lines = [f"# NFL postmortem dashboard ({report['window'][0]} .. {report['window'][1]})", "",
             f"Fills reconciled: {rc['n_records']} (settled {rc['settled']}, amended {rc['amended']}); kinds {rc['kinds']}.",
             f"Recommendation states: {rc['recommendation_states']}.",
             f"Exposure flags (flags only, no cap): games {ex['n_game_flags']}, thesis groups {ex['n_group_flags']}, days {ex['n_day_flags']}.",
             f"Loss labels ({lo['n_losses']} losses): {lo['category_counts']}; positions with a close {lo['close_coverage']['n_with_close']} of {lo['close_coverage']['n_settled_single']}.",
             f"No market family may be called profitable or unprofitable below {lo['min_n_for_family_claim']} positions.", "",
             "| # | item | status | note |", "|---|---|---|---|"]
    lines += [f"| {i['id']} | {i['title']} | {i['status']} | {i['note']} |" for i in report["items"]]
    return "\n".join(lines) + "\n"
