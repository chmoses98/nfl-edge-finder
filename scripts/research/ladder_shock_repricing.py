#!/usr/bin/env python3
"""Does the market-implied MARGIN DISTRIBUTION change shape after a precisely-timed shock, or only shift?

Session 3 asked whether prices move after the inactive release. This asks a structural question the
single-contract work cannot: when a team loses a player it expected to have, does the whole implied
distribution over game margin translate (location), widen (scale), or fatten at the blowout end (tail)?

Those are different economic claims. A pure translation says the market treats the absence as a change in
expected strength. A widening says it treats it as a change in *uncertainty*. A tail change says it prices a
different failure mode. Only a ladder can tell them apart, and Kalshi's KXNFLSPREAD series is a ladder: every
rung is P(TEAM margin > strike) at a half-point strike, listed for both teams, so the two sides compose into
a complete survival curve over signed home margin.

  home rung, strike s  ->  S(s)  = P(M > s)
  away rung, strike s  ->  S(-s) = 1 - P(-M > s), exact because M is an integer and -s is not attainable

The shock instant is the inactive release: kickoff - 90 minutes, exactly, by league rule. It is the one 2025
event whose timing is known rather than inferred, and the surprise population is the corrected one -- a
player active in his most recent prior week and inactive now (see nfl_edge/shocks/engine.py; the ungated
version was 69% non-events).

WHAT THIS SCRIPT IS FOR. The 2025 KXNFLSPREAD candle archive covers 21 games -- week 18 and the playoffs.
That yields on the order of seventeen treated games and four controls. **That is not enough to support an
inference and this script does not claim one.** It exists to (a) build and test the machinery, (b) report
descriptives with the sample stated next to them, and (c) fix the decision thresholds in advance, so that
2026 answers the question rather than a threshold chosen after seeing 2026.
"""
import argparse
import glob
import json
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)
from nfl_edge.pricing.market_implied import pav_monotone_decreasing  # noqa: E402
from nfl_edge.shocks import detect_2025_availability_shocks  # noqa: E402

OUT = os.path.join(ROOT, "research", "ladder_shocks")
os.makedirs(OUT, exist_ok=True)

MONTHS = {m: i + 1 for i, m in enumerate(
    ["JAN", "FEB", "MAR", "APR", "MAY", "JUN", "JUL", "AUG", "SEP", "OCT", "NOV", "DEC"])}

SHOCK_LEAD_S = 90 * 60          # inactive release, by rule
OFFSETS = [("pre", -5 * 60), ("post", 0), ("+10m", 10 * 60), ("+30m", 30 * 60), ("+60m", 60 * 60)]
MAX_STALE_S = 15 * 60           # a quote older than this is not "the price at t"
MAX_WIDTH = 0.10                # a 10-cent book carries no usable distributional information
MIN_RUNGS = 6                   # fewer points than this cannot pin location, scale and tail at once
TAIL_X = 13.5                   # blowout threshold: |margin| > two touchdowns

# ---- PREREGISTERED 2026 DECISION THRESHOLDS ---------------------------------------------------------
# Fixed here, before 2026 data exists, so the 2026 answer cannot be produced by choosing a threshold.
MIN_TREATED_GAMES = 40          # below this the study reports descriptives only, never a verdict
MIN_CONTROL_GAMES = 40
ALPHA = 0.01                    # three structural components tested; deliberately strict


def kickoff_utc(gameday: str, gametime: str) -> datetime:
    """Kalshi's NFL dates are Eastern. Week 18 and the playoffs are entirely inside EST (UTC-5)."""
    d = datetime.strptime(f"{gameday} {gametime}", "%Y-%m-%d %H:%M")
    return d.replace(tzinfo=timezone.utc) + timedelta(hours=5)


def load_series(path):
    """ticker -> sorted [(ts, mid)] from minute candles, skipping empty and wide books."""
    d = json.load(open(path))
    out = []
    for c in (d.get("m1") or []):
        if not c:
            continue
        b, a = c.get("yes_bid") or {}, c.get("yes_ask") or {}
        try:
            yb, ya = float(b.get("close")), float(a.get("close"))
        except (TypeError, ValueError):
            continue
        if yb <= 0.0 and ya >= 1.0:      # empty book, not a 100-cent spread
            continue
        if not (0.0 < yb <= ya < 1.0) or (ya - yb) > MAX_WIDTH:
            continue
        out.append((int(c["end_period_ts"]), (yb + ya) / 2.0))
    out.sort()
    return out


def quote_at(series, ts):
    """Most recent mid at or before ts, provided it is not stale. No forward looking, ever."""
    lo, hi, best = 0, len(series) - 1, None
    while lo <= hi:
        mid = (lo + hi) // 2
        if series[mid][0] <= ts:
            best = series[mid]; lo = mid + 1
        else:
            hi = mid - 1
    if best is None or ts - best[0] > MAX_STALE_S:
        return None
    return best[1]


def survival_curve(rungs, home, ts):
    """[(x, S(x))] over signed HOME margin, monotone. rungs: (team, strike, series)."""
    pts = []
    for team, strike, series in rungs:
        q = quote_at(series, ts)
        if q is None:
            continue
        pts.append((strike, q) if team == home else (-strike, 1.0 - q))
    if len(pts) < MIN_RUNGS:
        return None
    pts.sort()
    xs = np.array([p[0] for p in pts], float)
    ss = np.array([p[1] for p in pts], float)
    # duplicate x (both teams quoting the same strike) -> average before enforcing monotonicity
    ux = np.unique(xs)
    us = np.array([ss[xs == x].mean() for x in ux])
    return ux, np.asarray(pav_monotone_decreasing(ux, us), float)


def _invert(xs, S, level):
    """x where S(x) = level, by linear interpolation on a decreasing curve. None if not bracketed."""
    for i in range(len(xs) - 1):
        a, b = S[i], S[i + 1]
        if (a >= level >= b) and a != b:
            return xs[i] + (a - level) / (a - b) * (xs[i + 1] - xs[i])
    return None


def _S_at(xs, S, x):
    """S(x) by interpolation. None outside the quoted strike range -- never extrapolated into a tail."""
    if x < xs[0] or x > xs[-1]:
        return None
    return float(np.interp(x, xs, S))


def summarise(curve):
    """location, scale and tail -- the three structural components, from one curve."""
    if curve is None:
        return None
    xs, S = curve
    med = _invert(xs, S, 0.50)
    q25, q75 = _invert(xs, S, 0.75), _invert(xs, S, 0.25)
    hi, lo = _S_at(xs, S, TAIL_X), _S_at(xs, S, -TAIL_X)
    if med is None or q25 is None or q75 is None:
        return None
    return {
        "location": float(med),                       # implied median home margin
        "scale": float(q75 - q25),                    # implied interquartile width
        "tail": None if (hi is None or lo is None) else float(hi + (1.0 - lo)),  # P(|margin| > 13.5)
        "n_rungs": int(len(xs)),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--candles", default="/home/user/_md/data/kalshi/backfill/candles/KXNFLSPREAD")
    ap.add_argument("--season", type=int, default=2025)
    a = ap.parse_args()

    files = sorted(glob.glob(os.path.join(a.candles, "*.json")))
    if not files:
        sys.exit(f"no KXNFLSPREAD candles under {a.candles!r} -- refusing to report from no data")

    games = pl.read_parquet(os.path.join(ROOT, "data/silver/games.parquet")) \
              .filter(pl.col("season") == a.season).to_dicts()

    # ladder code (26JAN04BALPIT) -> game row
    by_code = {(g["gameday"], g["away_team"] + g["home_team"]): g for g in games}

    rungs_by_code = {}
    for f in files:
        base = os.path.basename(f)[:-5].split("-")     # KXNFLSPREAD, 26JAN04BALPIT, PIT9
        if len(base) < 3:
            continue
        code, leg = base[1], base[2]
        team = "".join(ch for ch in leg if not ch.isdigit())
        num = "".join(ch for ch in leg if ch.isdigit())
        if not num:
            continue
        s = load_series(f)
        if s:
            rungs_by_code.setdefault(code, []).append((team, float(num) + 0.5, s))

    shocks = detect_2025_availability_shocks(ROOT).to_frame()
    surprise = shocks.filter(pl.col("shock_type") == "surprise_inactive")
    n_surp = {}
    for gid in surprise["game_id"].to_list():
        n_surp[gid] = n_surp.get(gid, 0) + 1

    rows, unmapped = [], []
    for code, rungs in sorted(rungs_by_code.items()):
        day = f"20{int(code[:2]):02d}-{MONTHS[code[2:5]]:02d}-{int(code[5:7]):02d}"
        g = by_code.get((day, code[7:]))
        if g is None:
            unmapped.append(code); continue
        ko = kickoff_utc(g["gameday"], g["gametime"]).timestamp()
        shock_ts = ko - SHOCK_LEAD_S
        home = g["home_team"]
        rec = {"code": code, "game_id": g["game_id"], "week": g["week"],
               "treated": n_surp.get(g["game_id"], 0) > 0, "n_surprise": n_surp.get(g["game_id"], 0),
               "n_rung_markets": len(rungs)}
        for name, off in OFFSETS:
            rec[name] = summarise(survival_curve(rungs, home, shock_ts + off))
        rec["close"] = summarise(survival_curve(rungs, home, ko - 60))
        rows.append(rec)

    print(f"KXNFLSPREAD ladder games with minute candles: {len(rungs_by_code)}  "
          f"(mapped {len(rows)}, unmapped {unmapped})")

    complete = [r for r in rows if r["pre"] and r["+60m"]]
    tre = [r for r in complete if r["treated"]]
    con = [r for r in complete if not r["treated"]]
    print(f"games with a reconstructable pre AND +60m ladder: {len(complete)}  "
          f"(treated {len(tre)}, control {len(con)})")

    print("\nSAMPLE GATE (preregistered): treated >= "
          f"{MIN_TREATED_GAMES} and control >= {MIN_CONTROL_GAMES}")
    gated = len(tre) >= MIN_TREATED_GAMES and len(con) >= MIN_CONTROL_GAMES
    print(f"  treated {len(tre)} / control {len(con)}  ->  "
          f"{'INFERENCE PERMITTED' if gated else 'DESCRIPTIVE ONLY, NO VERDICT'}")

    def delta(r, comp, a_="pre", b_="+60m"):
        if not r.get(a_) or not r.get(b_):
            return None
        x, y = r[a_][comp], r[b_][comp]
        return None if (x is None or y is None) else y - x

    print("\nSTRUCTURAL RESPONSE ACROSS THE 90-MINUTE INACTIVE RELEASE  (pre -> +60m)")
    print(f"{'component':10s} {'group':8s} {'n':>4s} {'mean delta':>12s} {'se':>10s}")
    summary = {"n_games": len(rows), "n_complete": len(complete), "n_treated": len(tre),
               "n_control": len(con), "gate_passed": gated,
               "min_treated_games": MIN_TREATED_GAMES, "min_control_games": MIN_CONTROL_GAMES,
               "alpha": ALPHA, "components": {}}
    for comp in ("location", "scale", "tail"):
        summary["components"][comp] = {}
        for label, grp in (("treated", tre), ("control", con)):
            d = [delta(r, comp) for r in grp]
            d = [x for x in d if x is not None]
            if not d:
                print(f"{comp:10s} {label:8s} {0:4d}   (no reconstructable pair)")
                summary["components"][comp][label] = {"n": 0}
                continue
            m = float(np.mean(d)); se = float(np.std(d, ddof=1) / np.sqrt(len(d))) if len(d) > 1 else float("nan")
            print(f"{comp:10s} {label:8s} {len(d):4d} {m:+12.4f} {se:10.4f}")
            summary["components"][comp][label] = {"n": len(d), "mean": m, "se": se}

    print("\nPER-GAME TRAJECTORY (implied median home margin at each offset)")
    print(f"{'game':20s} {'trt':>4s} {'pre':>8s} {'post':>8s} {'+10m':>8s} {'+30m':>8s} {'+60m':>8s} {'close':>8s}")
    for r in sorted(complete, key=lambda z: (not z["treated"], z["game_id"])):
        cells = []
        for k in ("pre", "post", "+10m", "+30m", "+60m", "close"):
            v = r.get(k)
            cells.append(f"{v['location']:+8.2f}" if v else f"{'--':>8s}")
        print(f"{r['game_id']:20s} {('Y' if r['treated'] else 'n'):>4s} " + " ".join(cells))

    with open(os.path.join(OUT, "ladder_shock_results.json"), "w") as f:
        json.dump({"summary": summary, "games": rows}, f, indent=1, default=str)

    print("\nVERDICT: " + ("inference permitted" if gated else
          f"NO VERDICT -- {len(tre)} treated and {len(con)} control games is below the preregistered "
          f"{MIN_TREATED_GAMES}/{MIN_CONTROL_GAMES} gate. Structural repricing is UNTESTED, not disproved."))


if __name__ == "__main__":
    main()
