#!/usr/bin/env python3
"""Freeze the shadow model that will price 2026 Week 1, before any 2026 regular-season outcome exists.

This is a lineage record, not a deliverable to trade from. It pins the exact code, configuration, fitted
bundle hash and research artifacts behind every Week-1 shadow price, so that when the games are played the
predictions can be scored against a model nobody could have quietly adjusted afterwards.

Kickoff of the first 2026 regular-season game is 2026-09-09. Any change after that goes in a NEW file.
"""
import glob, hashlib, json, os, sys
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
KICKOFF = "2026-09-09"

CODE = [
    "nfl_edge/shadow/models.py", "nfl_edge/shadow/ledger.py", "nfl_edge/shadow/prospective.py",
    "nfl_edge/research/player_distributions.py", "nfl_edge/features/opportunity.py",
    "nfl_edge/settlement/semantics.py", "nfl_edge/settlement/availability.py",
    "nfl_edge/pricing/market_implied.py", "scripts/shadow/price_slate.py",
    "scripts/shadow/ledger_report.py",
]
RESEARCH = [
    "research/opportunity/RESULTS.md", "research/opportunity/results.json",
    "research/ladder_role/RESULTS.md", "research/ladder_role/results.json",
    "research/efficiency_map/RESULTS.md", "research/shadow/RESULTS.md",
    "research/availability/RESULTS.md", "research/anytime_td/RESULTS.md",
    "research/player_distributions/results.json", "docs/KALSHI_SETTLEMENT.md",
]


def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()


def entry(rel):
    p = os.path.join(ROOT, rel)
    if not os.path.exists(p):
        return None
    return {"sha256": sha(p), "bytes": os.path.getsize(p)}


def main():
    mans = sorted(glob.glob(os.path.join(ROOT, "data/shadow/ledger", "*", "*.ledger_manifest.json")))
    if not mans:
        print("no ledger manifest; run price_slate.py first"); return 1
    man = json.load(open(mans[-1]))
    bundle = man["model_bundle"]
    out = {
        "frozen_at": datetime.now(timezone.utc).isoformat(),
        "first_2026_kickoff": KICKOFF,
        "rule": ("Everything listed here existed before any 2026 regular-season outcome. Week-1 shadow "
                 "predictions are scored against THIS model. A later change requires a new freeze file, "
                 "never an overwrite of this one."),
        "real_money_status": "NOT VALIDATED - no real-money authorization, no production bet recommendations",
        "model": {
            "version": bundle["version"],
            "artifact_sha": bundle["artifact_sha"],
            "target_season": bundle["target_season"],
            "train_seasons": bundle["train_seasons"],
            "role_features": bundle["config"].get("role_features"),
            "role_feature_list": None,
            "stat_families": {k: v["family"] for k, v in bundle["stat_models"].items()},
            "ewma": {k: bundle["config"]["ewma"][k] for k in ("halflife", "season_carry", "shrink_k")
                     if k in bundle["config"].get("ewma", {})},
        },
        "pre_kickoff_ledger_snapshots": [os.path.relpath(m, ROOT) for m in mans],
        "code": {}, "research": {},
        "prospective_hypotheses": ["H-20260904-010", "H-20260904-011", "H-20260904-012"],
        "known_limitations": [
            "The 2025 market-efficiency map is incomplete: the horizon backfill is refetching after a "
            "candle-field parse bug, so player-prop families are not yet covered.",
            "Ladder gains are measured on historical settled outcomes; none has been shown to survive the "
            "~2.5 point cost of crossing the Kalshi spread.",
            "Availability play rates are measured from official injury reports; the 2026 live path reads "
            "ESPN and Sleeper, which is a different source and is not yet prospectively validated.",
        ],
    }
    try:
        sys.path.insert(0, ROOT)
        from nfl_edge.research import player_distributions as pdist
        out["model"]["role_feature_list"] = list(pdist.ROLE_FEATURES)
    except Exception:
        pass
    for rel in CODE:
        e = entry(rel)
        if e:
            out["code"][rel] = e
    for rel in RESEARCH:
        e = entry(rel)
        if e:
            out["research"][rel] = e
    dest = os.path.join(ROOT, "research", "FREEZE_WEEK1_2026.json")
    if os.path.exists(dest):
        print(f"refusing to overwrite {dest}; a freeze is immutable -- write a new file"); return 2
    json.dump(out, open(dest, "w"), indent=1)
    print(f"wrote {os.path.relpath(dest, ROOT)}")
    print(f"  model {out['model']['version']} sha {out['model']['artifact_sha']} "
          f"role_features={out['model']['role_features']}")
    print(f"  {len(out['code'])} code files, {len(out['research'])} research artifacts, "
          f"{len(out['pre_kickoff_ledger_snapshots'])} pre-kickoff ledger snapshots")
    return 0


if __name__ == "__main__":
    sys.exit(main())
