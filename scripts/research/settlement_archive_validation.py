#!/usr/bin/env python3
"""Prove the settlement engine against Kalshi's OWN settlements of the 2025 archive.

The engine in nfl_edge/settlement/settle.py claims to know what each contract pays. That claim is testable
without waiting for a single 2026 game: the market-data branch carries 60k+ finalized 2025 markets, each with
Kalshi's actual `result` (`yes` / `no` / `scalar`) and `settlement_value_dollars`. Re-settling them from
nflverse and comparing is the strongest available evidence that a semantics reading is right -- and the only
thing that can catch a reading that is merely plausible.

Two questions it is built to answer:

  1. Does `stat >= K` / `margin > floor` / `total > floor` reproduce Kalshi's settlements exactly?
  2. Does "touchdowns scored" include return and defensive touchdowns? The rules text says "touchdowns
     scored" without qualification, so the engine sums rushing + receiving + special-teams + defensive. If
     that reading is wrong, anytime-touchdown markets where a player's ONLY touchdown was a return would
     disagree, and this script prints them.

Identity here is name-based (the archive carries `no_sub_title`), which is fine for a research check and is
NOT how production settles: the production path uses the GSIS id resolved at pricing time. Name-resolution
failures are reported separately so they can never be mistaken for a semantics disagreement.

Usage:
  python3 scripts/research/settlement_archive_validation.py --md /tmp/md --season 2025 \
      [--series KXNFLANYTD,KXNFLRECYDS] [--out research/settlement_validation/results.json]
"""
from __future__ import annotations

import argparse
import glob
import json
import os
import re
import sys
import unicodedata
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.kalshi.classifier import classify                                  # noqa: E402
from nfl_edge.settlement import settle as S                                       # noqa: E402
from nfl_edge.settlement.nflverse_results import build_result_book                # noqa: E402

SUFFIX_RE = re.compile(r"\b(jr|sr|ii|iii|iv|v)\.?$", re.I)


def norm_name(n: str | None) -> str:
    if not n:
        return ""
    s = unicodedata.normalize("NFKD", n).encode("ascii", "ignore").decode()
    s = SUFFIX_RE.sub("", s.lower().replace(".", "").replace("'", "").replace("-", " ")).strip()
    return re.sub(r"\s+", " ", s)


def build_indexes(book):
    """(gameday, away, home) -> game_id, and (game_id, normalised name) -> [player_id]."""
    by_date = {}
    for gid, g in book.games.items():
        if g.kickoff_utc and g.home_team and g.away_team:
            by_date[(g.kickoff_utc[:10], g.away_team, g.home_team)] = gid
    names = defaultdict(list)
    for (gid, pid), pr in book.players.items():
        if pr.player_name:
            names[(gid, norm_name(pr.player_name))].append(pid)
    return by_date, names


def find_game(by_date, sem):
    """Kalshi encodes the LOCAL game date; a late kickoff can land on the next UTC day, so allow +-1 day."""
    if not (sem.game_date and sem.away_team and sem.home_team):
        return None
    from datetime import date, timedelta
    y, m, d = (int(x) for x in sem.game_date.split("-"))
    for off in (0, 1, -1):
        key = ((date(y, m, d) + timedelta(days=off)).isoformat(), sem.away_team, sem.home_team)
        if key in by_date:
            return by_date[key]
    return None


def late_bulk(m: dict, g) -> bool:
    """Did Kalshi settle this market long after the game, in a bulk sweep?

    Four 2025 markets contradict the game's own final score -- including "over 0.5 total points" settled NO on
    a game that scored 47. All of them were settled on 2025-12-22, weeks or months after kickoff, in a batch.
    Those are Kalshi's own housekeeping settlements, not a semantics disagreement, so they are counted apart
    rather than quietly averaged into an agreement rate.
    """
    ts = m.get("settlement_ts")
    if not ts or not g or not g.kickoff_utc:
        return False
    from datetime import datetime, timedelta
    try:
        st = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        ko = datetime.fromisoformat(g.kickoff_utc)
    except ValueError:
        return False
    return st > ko + timedelta(hours=48)


def kalshi_truth(m: dict):
    """Kalshi's own outcome as a YES payout in dollars, plus its kind."""
    res = (m.get("result") or "").lower()
    val = m.get("settlement_value_dollars")
    if res == "yes":
        return 1.0, "binary"
    if res == "no":
        return 0.0, "binary"
    if res == "scalar":
        try:
            return float(val), "scalar"
        except (TypeError, ValueError):
            return None, "scalar"
    return None, res or "unknown"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--md", required=True, help="market-data worktree (holds data/kalshi/backfill/markets)")
    ap.add_argument("--season", type=int, default=2025)
    ap.add_argument("--series", default="", help="comma-separated series filter (default: every NFL series present)")
    ap.add_argument("--out", default="")
    ap.add_argument("--max-examples", type=int, default=8)
    a = ap.parse_args()

    book = build_result_book(ROOT, [a.season])
    by_date, names = build_indexes(book)
    print(f"result book: {len(book.games)} games, {len(book.players)} player-games, "
          f"stats for {len(book.games_with_player_stats)} games, snaps for {len(book.games_with_snaps)}", flush=True)

    files = sorted(glob.glob(os.path.join(a.md, "data", "kalshi", "backfill", "markets", "*.jsonl")))
    want = {s.strip() for s in a.series.split(",") if s.strip()}
    per_family = defaultdict(Counter)
    disagreements = defaultdict(list)
    refusals = defaultdict(Counter)
    td_return_only = []

    for f in files:
        series = os.path.basename(f)[:-6]
        if want and series not in want:
            continue
        for line in open(f):
            m = json.loads(line)
            if m.get("status") != "finalized":
                continue
            sem = classify({"ticker": m.get("ticker"), "event_ticker": m.get("event_ticker"),
                            "series_ticker": series, "title": m.get("title") or "",
                            "strike_type": m.get("strike_type"), "floor_strike": m.get("floor_strike"),
                            "custom_strike": m.get("custom_strike")})
            if sem.family not in S.SETTLEABLE_FAMILIES:
                continue
            gid = find_game(by_date, sem)
            if gid is None:
                per_family[sem.family]["no_game_in_schedule"] += 1
                continue
            obs = {"family": sem.family, "period": sem.period, "stat": sem.stat, "threshold": sem.threshold,
                   "operator": sem.operator, "floor_strike": sem.floor_strike, "team": sem.team,
                   "game_id": gid, "direction": "YES", "player_name": m.get("no_sub_title")}
            if sem.family == "PLAYER_STAT":
                cands = names.get((gid, norm_name(m.get("no_sub_title") or sem.player_name)), [])
                if len(cands) != 1:
                    per_family[sem.family]["name_unresolved" if not cands else "name_ambiguous"] += 1
                    continue
                obs["player_id"] = cands[0]
            truth, tkind = kalshi_truth(m)
            if truth is None:
                per_family[sem.family]["kalshi_outcome_unusable"] += 1
                continue
            # The scalar branch settles at Kalshi's own pregame fair price, which is what we are testing
            # against; feeding it back in would be circular. Hand the engine that price and check only that
            # it CHOOSES the scalar branch.
            st = S.settle_observation(obs, book, fair_price=truth if tkind == "scalar" else 0.5)
            fam = sem.family
            if not st.is_settled:
                per_family[fam]["refused"] += 1
                refusals[fam][st.status] += 1
                continue
            g = book.games.get(gid)
            if tkind == "scalar" and abs(truth - 0.5) < 1e-9 and st.kind == S.KIND_TIE_SPLIT:
                # a tied game: Kalshi records result="scalar" with settlement_value 0.50, which is exactly the
                # $0.50-per-side tie rule the engine applies
                per_family[fam]["tie_split_agree"] += 1
                continue
            if tkind == "scalar":
                ok = st.kind == S.KIND_SCALAR_FAIR_PRICE
                if not ok and late_bulk(m, g):
                    per_family[fam]["kalshi_late_bulk_settlement"] += 1
                    continue
                per_family[fam]["scalar_agree" if ok else "scalar_disagree"] += 1
                if not ok and len(disagreements[fam]) < a.max_examples:
                    disagreements[fam].append({"ticker": m.get("ticker"), "kalshi": "scalar",
                                               "engine_kind": st.kind, "engine": st.settled_yes,
                                               "evidence": st.evidence})
                continue
            agree = abs((st.settled_yes or 0.0) - truth) < 1e-9
            if not agree and late_bulk(m, g):
                per_family[fam]["kalshi_late_bulk_settlement"] += 1
                if len(disagreements[fam + " (late bulk)"]) < a.max_examples:
                    disagreements[fam + " (late bulk)"].append(
                        {"ticker": m.get("ticker"), "title": m.get("title"), "kalshi": truth,
                         "engine": st.settled_yes, "settlement_ts": m.get("settlement_ts"),
                         "kickoff_utc": g.kickoff_utc if g else None, "evidence": st.evidence})
                continue
            per_family[fam]["agree" if agree else "disagree"] += 1
            if not agree:
                if len(disagreements[fam]) < a.max_examples:
                    disagreements[fam].append({"ticker": m.get("ticker"), "title": m.get("title"),
                                               "kalshi": truth, "engine": st.settled_yes,
                                               "reason": st.reason, "evidence": st.evidence})
            elif sem.stat == "touchdowns" and truth == 1.0:
                pr = book.player(gid, obs.get("player_id", ""))
                if pr is not None:
                    off = (pr.stats.get("rushing_tds") or 0) + (pr.stats.get("receiving_tds") or 0)
                    other = (pr.stats.get("special_teams_tds") or 0) + (pr.stats.get("def_tds") or 0)
                    if off == 0 and other > 0:
                        td_return_only.append({"ticker": m.get("ticker"), "player": pr.player_name,
                                               "special_teams_tds": pr.stats.get("special_teams_tds"),
                                               "def_tds": pr.stats.get("def_tds")})

    report = {"season": a.season, "families": {}, "touchdown_reading": {
        "columns": list(__import__("nfl_edge.settlement.results", fromlist=["x"]).TOUCHDOWN_COLUMNS),
        "yes_settlements_with_no_rushing_or_receiving_td": td_return_only[:20],
        "n_return_or_defensive_only": len(td_return_only)}}
    total_agree = total_dis = 0
    report["kalshi_late_bulk_examples"] = {k: v for k, v in disagreements.items() if k.endswith("(late bulk)")}
    for fam, c in sorted(per_family.items()):
        agree = c["agree"] + c["scalar_agree"] + c["tie_split_agree"]
        dis = c["disagree"] + c["scalar_disagree"]
        total_agree += agree; total_dis += dis
        report["families"][fam] = {"counts": dict(c), "refusal_reasons": dict(refusals[fam]),
                                  "agreement": round(agree / (agree + dis), 6) if (agree + dis) else None,
                                  "disagreement_examples": disagreements[fam]}
        print(f"{fam:20s} agree={agree:6d} disagree={dis:4d} refused={c['refused']:5d} "
              f"other={sum(v for k, v in c.items() if k not in ('agree','disagree','scalar_agree','scalar_disagree','refused'))}",
              flush=True)
        for k, v in sorted(refusals[fam].items()):
            print(f"    refusal {k}: {v}")
        for d in disagreements[fam][:3]:
            print(f"    DISAGREE {d.get('ticker')}: kalshi={d.get('kalshi')} engine={d.get('engine')} {d.get('reason','')}")
    report["overall"] = {"agree": total_agree, "disagree": total_dis,
                         "agreement": round(total_agree / (total_agree + total_dis), 6) if (total_agree + total_dis) else None}
    print(f"\nOVERALL agreement {report['overall']['agreement']} on {total_agree + total_dis} settled markets")
    print(f"anytime-TD YES settlements whose only touchdown was a return/defensive score: {len(td_return_only)}")
    if a.out:
        os.makedirs(os.path.dirname(a.out), exist_ok=True)
        with open(a.out, "w") as fh:
            json.dump(report, fh, indent=1)
        print("wrote", a.out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
