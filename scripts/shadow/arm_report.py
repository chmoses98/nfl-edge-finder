#!/usr/bin/env python3
"""Per-slate, weekly and cumulative three-arm reports, rebuilt entirely from durable evidence.

    python3 scripts/shadow/arm_report.py --market-data /tmp/md --out data/shadow/arm_reports/<batch> [--week N]

Inputs: the arm-evaluation corpus, the player-autopsy corpus and the funnel sidecars on market-data (plus any
local staging roots). No model, no network, no re-settlement: two people running it on the same corpus get the
same files. Every report says loudly when the sample is too small.
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import sys
from collections import defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.arms import evaluation as AE, registry as R                          # noqa: E402
from nfl_edge.arms.report import render_autopsy, render_funnel, render_scorecard   # noqa: E402
from nfl_edge.arms.scorecard import build_arm_scorecard                            # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                 # noqa: E402
from nfl_edge.shadow.eval_scorecard import latest_pregame_view                     # noqa: E402
from nfl_edge.shadow.player_autopsy import SUFFIX as AUTOPSY_SUFFIX, rank         # noqa: E402


def load_funnels(roots, season=None, week=None, game_ids=None) -> list:
    out = []
    for root in roots:
        for path in sorted(glob.glob(os.path.join(root, "*", "*.funnel.json"))):
            try:
                out.append(json.load(open(path)))
            except ValueError:
                continue
    return out


def _write(out_dir, stem, sc, md):
    with open(os.path.join(out_dir, f"{stem}.scorecard.json"), "w") as f:
        json.dump(sc, f, indent=1, default=str)
    with open(os.path.join(out_dir, f"{stem}.REPORT.md"), "w") as f:
        f.write(md + "\n")


def build(games, contracts, autopsies, funnels, *, title, eval_version=None):
    sc = build_arm_scorecard(games, contracts, evaluation_version=eval_version)
    latest, _ = latest_pregame_view([g for g in games if g.get("record_status") == R.OK])
    md = render_scorecard(sc, title=title, game_rows=latest)
    md += "\n" + render_autopsy(rank(autopsies)) + "\n" + render_funnel(funnels)
    sc["autopsy_summary"] = {"n": len(autopsies),
                             "classifications": dict(sorted(defaultdict(int, {}).items()))}
    counts = defaultdict(int)
    for a in autopsies:
        counts[a.get("classification")] += 1
    sc["autopsy_summary"]["classifications"] = dict(sorted(counts.items()))
    sc["funnel_summary"] = {"n_snapshots": len(funnels),
                            "newest": {k: funnels[-1].get(k) for k in ("run_id", "n_markets", "terminal_states", "stages")} if funnels else None}
    return sc, md


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", default="")
    ap.add_argument("--eval-root", action="append", default=[], help="extra arm-evaluation roots (local staging)")
    ap.add_argument("--autopsy-root", action="append", default=[])
    ap.add_argument("--arms-root", action="append", default=[], help="extra arm snapshot roots (funnel sidecars)")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "arm_reports", "report"))
    ap.add_argument("--season", type=int, default=0)
    ap.add_argument("--week", type=int, default=0)
    ap.add_argument("--eval-version", default="")
    a = ap.parse_args()
    eroots, aroots, froots = list(a.eval_root), list(a.autopsy_root), list(a.arms_root)
    if a.market_data:
        eroots.append(os.path.join(a.market_data, "data", "shadow", "arm_evaluations"))
        aroots.append(os.path.join(a.market_data, "data", "shadow", "player_autopsy"))
        froots.append(os.path.join(a.market_data, "data", "shadow", "arms"))
    games = ST.read_corpus(eroots, suffix=AE.GAME_SUFFIX)
    contracts = ST.read_corpus(eroots, suffix=AE.CONTRACT_SUFFIX)
    autopsies = ST.read_corpus(aroots, suffix=AUTOPSY_SUFFIX)
    funnels = load_funnels(froots)
    if a.season:
        games = [g for g in games if g.get("season") == a.season]; contracts = [c for c in contracts if c.get("season") == a.season]
        autopsies = [x for x in autopsies if x.get("season") == a.season]
    os.makedirs(a.out, exist_ok=True)
    ver = a.eval_version or None
    sc, md = build(games, contracts, autopsies, funnels, title="Three-arm game-centre experiment — season to date (cumulative)", eval_version=ver)
    _write(a.out, "cumulative", sc, md)
    weeks = sorted({(g.get("season"), g.get("week")) for g in games if g.get("week") is not None})
    if a.week:
        weeks = [w for w in weeks if w[1] == a.week] or [(a.season or None, a.week)]
    for season, week in weeks:
        gw = [g for g in games if g.get("week") == week and (season is None or g.get("season") == season)]
        cw = [c for c in contracts if c.get("week") == week and (season is None or c.get("season") == season)]
        aw = [x for x in autopsies if x.get("week") == week and (season is None or x.get("season") == season)]
        scw, mdw = build(gw, cw, aw, [], title=f"Three-arm game-centre experiment — {season} week {week}", eval_version=ver)
        _write(a.out, f"week{int(week):02d}", scw, mdw)
        # per-slate: one file per game of the week, the game's own rows only
        for gid in sorted({g.get("game_id") for g in gw}):
            gg = [g for g in gw if g.get("game_id") == gid]; cg = [c for c in cw if c.get("game_id") == gid]
            ag = [x for x in aw if x.get("game_id") == gid]
            scg, mdg = build(gg, cg, ag, [], title=f"Three-arm game record — {gid}", eval_version=ver)
            os.makedirs(os.path.join(a.out, "games"), exist_ok=True)
            _write(os.path.join(a.out, "games"), gid, scg, mdg)
    print(f"arm report: {len(games)} game evaluations, {len(contracts)} contract evaluations, {len(autopsies)} autopsies, "
          f"{len(funnels)} funnel snapshots, weeks {weeks} -> {a.out}; evidence: {sc['headline_evidence']} ({sc['headline_n_games']} games)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
