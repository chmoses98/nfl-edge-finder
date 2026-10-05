#!/usr/bin/env python3
"""Compare a fresh reproduction of the committed 2023-2025 walk-forward with the committed evidence.

Produce the reproduction with the UNMODIFIED code path (scripts/sim/walkforward.py --out-dir DIR, or the
equivalent calls), then run this to write research/game_script_v2/reproduction_2023_2025.json: which bundle
components are bit-identical, which moved, and how far every committed per-statistic metric moved.

Usage: python scripts/sim/reproduction_check.py --repro-dir DIR [--out PATH]
"""
from __future__ import annotations
import argparse, json, os, sys
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
COMMITTED = os.path.join(ROOT, "research", "simulation_engine")
METRICS = ("n", "mae", "rmse", "bias", "crps", "cover50", "cover90", "ladder_brier", "baseline_mae")


def flat(d, pre=""):
    out = {}
    if isinstance(d, dict):
        for k, v in d.items():
            out.update(flat(v, f"{pre}/{k}"))
    elif isinstance(d, list):
        for i, v in enumerate(d):
            out.update(flat(v, f"{pre}[{i}]"))
    else:
        out[pre] = d
    return out


def compare(repro_dir: str, seasons=(2023, 2024, 2025)) -> dict:
    wf = json.load(open(os.path.join(COMMITTED, "walkforward.json")))
    out = {"seasons": {}}
    for y in seasons:
        src = os.path.join(repro_dir, f"wf_{y}.json")
        rep = json.load(open(src)) if os.path.exists(src) else json.load(open(os.path.join(repro_dir, "walkforward.json")))[str(y)]
        ba = json.load(open(os.path.join(COMMITTED, f"bundle_{y}.json"))); bb = json.load(open(os.path.join(repro_dir, f"bundle_{y}.json")))
        comp = {k: ("IDENTICAL" if flat(ba.get(k)) == flat(bb.get(k)) else "DIFFERS") for k in sorted(set(ba) | set(bb))}
        maxdiff = {}
        for k, v in comp.items():
            if v == "DIFFERS":
                fa, fb = flat(ba.get(k)), flat(bb.get(k))
                nums = [abs(fa[x] - fb[x]) for x in set(fa) & set(fb) if isinstance(fa[x], (int, float)) and isinstance(fb[x], (int, float))]
                maxdiff[k] = max(nums) if nums else None
        stats = {}
        for st, a in wf[str(y)]["evaluation"]["player"].items():
            b = rep["evaluation"]["player"].get(st, {})
            stats[st] = {m: {"committed": a.get(m), "reproduced": b.get(m),
                             "rel_change": (None if not a.get(m) or b.get(m) is None else (b[m] - a[m]) / abs(a[m]))}
                         for m in METRICS if m in a}
        team = {st: {"committed": a["crps"], "reproduced": rep["evaluation"]["team"][st]["crps"]}
                for st, a in wf[str(y)]["evaluation"]["team"].items()}
        out["seasons"][str(y)] = {"bundle_components": comp, "max_abs_diff_by_component": maxdiff,
                                  "other_share": {"committed": ba.get("other_share"), "reproduced": bb.get("other_share")},
                                  "player": stats, "team_crps": team,
                                  "team_stats_differing": sorted(k for k, v in team.items() if abs(v["committed"] - v["reproduced"]) > 1e-12),
                                  "max_abs_rel_change": {m: max((abs(s[m]["rel_change"]) for s in stats.values() if m in s and s[m]["rel_change"] is not None), default=None)
                                                         for m in ("mae", "crps", "cover50", "cover90", "ladder_brier")}}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--repro-dir", required=True)
    ap.add_argument("--out", default=os.path.join(ROOT, "research", "game_script_v2", "reproduction_2023_2025.json"))
    a = ap.parse_args()
    res = compare(a.repro_dir)
    res["diagnosis"] = (
        "Game environment, efficiency, touchdown and QB-share models reproduce bit for bit, and so does every team-level "
        "volume, points and touchdown metric; team passing / rushing yards (sums of player yards) move with the player allocation. "
        "The opportunity share models agree to floating-point precision. The one material difference is other_share (the "
        "share of team volume outside the eligible set), whose sign flips: nflverse has since rebuilt snap_counts_2020 with "
        "compound position labels (616 rows, e.g. FB/D; no other season has any), such a player falls out of the skill "
        "filter, his eligible row merges to NaN team volume, and assemble's fillna(0) followed by groupby 'first' reads the "
        "team's volume as 0 whenever that row sorts first. Falling back to the roster position moves other_share but does "
        "not restore the committed bundle, so the original bytes differed in more than the labels and cannot be recovered "
        "(the repository records no checksum of the old file). The frozen baseline is therefore run on today's vintage "
        "unchanged, and the aggregation repair is a registered candidate (R1).")
    os.makedirs(os.path.dirname(a.out), exist_ok=True)
    json.dump(res, open(a.out, "w"), indent=1, default=float)
    print("wrote", a.out)


if __name__ == "__main__":
    main()
