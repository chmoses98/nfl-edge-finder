#!/usr/bin/env python3
"""How fast does Kalshi reprice after a precisely-timed public information release?

The one 2025 shock whose timing is known rather than assumed is the **inactive release, exactly 90 minutes
before kickoff by league rule**. The horizon grid brackets it: T-90m is the release instant, T-30m is an hour
later, T-0 is kickoff.

Two responses are measured separately:

  DIRECT     the inactive player's own prop ladder. It should collapse toward zero, and how fast it does is
             the market's floor speed for unambiguous news.
  SECONDARY  his position-group teammates' ladders, which should RISE as his opportunity is reallocated.
             This is the economically interesting one: no single quote has to encode a teammate's absence,
             and a market of independent single-contract quotes is least likely to be quick about it.

Control: the same measurements on players in games with no surprise inactive at their position, over the
identical window. Without that control, any pre-kickoff drift common to all props would be read as a
response.

Only players Kalshi actually quoted are counted -- the market defines which absences were newsworthy, not us.
"""
import argparse, glob, json, os, sys
from collections import defaultdict

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.research.clv import clustered_se  # noqa: E402
from nfl_edge.shocks import detect_2025_availability_shocks  # noqa: E402

OUT = os.path.join(ROOT, "research", "shocks"); os.makedirs(OUT, exist_ok=True)
WINDOW = ["T-90m", "T-30m", "T-0"]
MAX_WIDTH = 0.15


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--horizons", default="/home/user/_market_data_wt/data/kalshi/backfill/horizons/*.jsonl")
    a = ap.parse_args()

    log = detect_2025_availability_shocks(ROOT)
    sh = log.to_frame()
    surprise = sh.filter(pl.col("shock_type") == "surprise_inactive")
    print(f"shocks derived: {sh.height}  (surprise inactives {surprise.height})")

    pmap = pl.read_parquet(os.path.join(ROOT, "data/silver/kalshi_player_map_2025.parquet")) \
        .filter(pl.col("gsis_id").is_not_null())
    kid2g = dict(zip(pmap["kalshi_player_id"].to_list(), pmap["gsis_id"].to_list()))

    # quoted ladders in the release window, keyed by (game, gsis, stat)
    quotes = defaultdict(dict)
    meta = {}
    files = glob.glob(a.horizons)
    # Fail closed. This default once pointed at an empty worktree and the study reported 0 direct, 0
    # secondary AND 0 control rungs as "(too few)" -- a silent no-op that looks like a finding.
    if not files:
        sys.exit(f"no horizon files matched {a.horizons!r} -- refusing to report a null from no data")

    for f in files:
        for line in open(f):
            r = json.loads(line)
            if r.get("anchor_kind") != "kickoff" or r.get("family") != "PLAYER_STAT":
                continue
            g = kid2g.get(r.get("player_kalshi_id"))
            if not g or not r.get("game_id") or r.get("threshold") is None:
                continue
            sn = r.get("snaps") or {}
            row = {}
            for h in WINDOW:
                s = sn.get(h)
                if s and s.get("bid") is not None and s.get("ask") is not None:
                    b, ask = s["bid"], s["ask"]
                    if 0 <= b <= ask <= 1 and not (b <= 0 and ask >= 1) and (ask - b) <= MAX_WIDTH:
                        row[h] = (b + ask) / 2.0
            if len(row) == len(WINDOW):
                quotes[(r["game_id"], g)][(r["stat"], float(r["threshold"]))] = row
                meta[(r["game_id"], g)] = r.get("team")

    print(f"players with a complete T-90m/T-30m/T-0 ladder: {len(quotes)}")

    shocked_players = set()
    shocked_games_pos = set()
    beneficiaries = defaultdict(list)
    for r in surprise.iter_rows(named=True):
        shocked_players.add((r["game_id"], r["entity_id"]))
        shocked_games_pos.add((r["game_id"], r["team"], r["entity_position"]))
        for b in (r["affected_players"] or "").split(";"):
            if b:
                beneficiaries[(r["game_id"], b)].append(r["entity_id"])

    direct, secondary, control = [], [], []
    for (gid, g), lad in quotes.items():
        team = meta[(gid, g)]
        is_direct = (gid, g) in shocked_players
        is_secondary = (gid, g) in beneficiaries and not is_direct
        for (stat, k), row in lad.items():
            rec = {"game_id": gid, "gsis": g, "stat": stat, "k": k,
                   "p90": row["T-90m"], "p30": row["T-30m"], "p0": row["T-0"],
                   "d_90_30": row["T-30m"] - row["T-90m"], "d_30_0": row["T-0"] - row["T-30m"],
                   "d_90_0": row["T-0"] - row["T-90m"]}
            (direct if is_direct else secondary if is_secondary else control).append(rec)

    print(f"\nladder rungs in the window:  direct {len(direct)}   secondary {len(secondary)}   "
          f"control {len(control)}")
    res = {"n_shocks": sh.height, "n_surprise": surprise.height, "groups": {}}
    print(f"\nMOVEMENT ACROSS THE 90-MINUTE INACTIVE RELEASE (midpoint, probability points)")
    print(f"  {'group':12s} {'rungs':>7s} {'games':>6s} {'T-90m->T-30m':>14s} {'se':>8s} "
          f"{'T-30m->T-0':>12s} {'se':>8s} {'T-90m->T-0':>12s} {'se':>8s}")
    for name, rows in (("direct", direct), ("secondary", secondary), ("control", control)):
        if len(rows) < 50:
            print(f"  {name:12s} {len(rows):7d}   (too few)")
            continue
        cl = [r["game_id"] for r in rows]
        out = {"n": len(rows), "games": len(set(cl))}
        line = f"  {name:12s} {len(rows):7d} {len(set(cl)):6d}"
        for col, lab in (("d_90_30", "T-90m->T-30m"), ("d_30_0", "T-30m->T-0"), ("d_90_0", "T-90m->T-0")):
            v = np.array([r[col] for r in rows]); se = clustered_se(v, cl)
            out[col] = {"mean": float(v.mean()), "se": se}
            line += f" {v.mean():+14.5f} {se:8.5f}" if col == "d_90_30" else f" {v.mean():+12.5f} {se:8.5f}"
        res["groups"][name] = out
        print(line)

    # the economically meaningful contrast: secondary minus control
    if len(secondary) >= 50 and len(control) >= 50:
        print(f"\nSECONDARY minus CONTROL (does a teammate's absence move the beneficiaries' prices?)")
        for col, lab in (("d_90_30", "T-90m -> T-30m"), ("d_30_0", "T-30m -> T-0"), ("d_90_0", "T-90m -> T-0")):
            vs = np.array([r[col] for r in secondary]); cs = np.array([r[col] for r in control])
            allv = np.concatenate([vs, cs])
            grp = np.concatenate([np.ones(len(vs)), np.zeros(len(cs))])
            cl = [r["game_id"] for r in secondary] + [r["game_id"] for r in control]
            # difference in means with a cluster-robust SE from the pooled regression
            X = np.column_stack([np.ones(len(allv)), grp])
            beta, *_ = np.linalg.lstsq(X, allv, rcond=None)
            resid = allv - X @ beta
            XtXi = np.linalg.pinv(X.T @ X)
            agg = defaultdict(lambda: np.zeros(2))
            for i, c in enumerate(cl):
                agg[c] += X[i] * resid[i]
            meat = np.zeros((2, 2))
            for v in agg.values():
                meat += np.outer(v, v)
            gg = len(agg)
            V = XtXi @ meat @ XtXi * (gg / max(gg - 1, 1))
            se = float(np.sqrt(max(V[1, 1], 0)))
            z = beta[1] / se if se else float("nan")
            print(f"  {lab:16s} diff {beta[1]:+.5f} +- {se:.5f}  (z={z:+.2f})")
            res.setdefault("secondary_minus_control", {})[col] = {"diff": float(beta[1]), "se": se,
                                                                  "z": float(z)}
    log.write(os.path.join(OUT, "shocks_2025.parquet"))
    json.dump(res, open(os.path.join(OUT, "latency_results.json"), "w"), indent=1, default=float)
    return 0


if __name__ == "__main__":
    sys.exit(main())
