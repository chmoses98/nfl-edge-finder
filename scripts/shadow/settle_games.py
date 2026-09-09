#!/usr/bin/env python3
"""Convert the pregame shadow observations of FINAL games into immutable evaluation records.

    published ledger (market-data)   every pregame prediction for the game, untouched
  + captured quote history           the last complete quote strictly BEFORE kickoff
  + nflverse final results           score, overtime, player statistics, snap counts
  -> data/shadow/evaluations/<game_id>/<eval_version>.<batch>.evaluations.jsonl.gz

Nothing in the ledger is read for writing, opened for writing, or copied. The evaluation corpus is a SECOND
immutable corpus that points back at the first by `prediction_id`.

ORDER OF OPERATIONS, AND WHY
----------------------------
1. resolve results and decide READINESS per game. A game whose score is published but whose player statistics
   are not is DEFERRED and nothing at all is written for it -- writing "unavailable" now and "settled" later is
   exactly the contradiction the corpus forbids.
2. gather every SUPPORTED pregame observation for the game, across every snapshot. Rows the pricer refused
   (UNSUPPORTED_*, STALE_DATA, DEGRADED_INPUT, POST_KICKOFF_EXCLUDED) carry no model probability, so there is
   no prediction in them to evaluate; they are counted and left where they are.
3. choose the close per TICKER (not per prediction): the last complete quote strictly before kickoff. Every
   snapshot of the same ticker is evaluated against that one close, which is what makes CLV comparable across
   horizons.
4. settle, or refuse with a reason.
5. plan against the existing corpus: new / no-op / conflict. A conflict fails the run and writes nothing.

Usage:
  python3 scripts/shadow/settle_games.py --market-data /tmp/md --out data/shadow/evaluations \
      [--season 2026] [--game 2026_01_NE_SEA] [--dry-run] [--max-games N]
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timezone

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.settlement import settle as S                                        # noqa: E402
from nfl_edge.settlement.nflverse_results import build_result_book                 # noqa: E402
from nfl_edge.settlement.results import READY                                      # noqa: E402
from nfl_edge.shadow import evaluation as E                                        # noqa: E402
from nfl_edge.shadow import evaluation_store as ST                                 # noqa: E402
from nfl_edge.shadow.eval_scorecard import build_scorecard, render_report          # noqa: E402
from nfl_edge.shadow.quote_history import (                                         # noqa: E402
    kalshi_yes_payout, load_game_quotes, load_kalshi_settlements,
)

# Only a SUPPORTED row carries a model probability; everything else records why the pricer refused.
EVALUABLE_SUPPORT_STATES = ("SUPPORTED",)

# The row-level source label is a STABLE constant, not a dump of which files happened to be on disk. The full
# provenance (every path, and anything that was missing) goes in the batch manifest, and the specific file that
# proved each fact is already inside `settlement_evidence`. Putting the file inventory in the row would make an
# identical rerun after another season was downloaded look like a contradicted truth.
SETTLEMENT_SOURCE = "nflverse:schedules+stats_player+snap_counts"


def ledger_files(market_data: str, day_lo: str | None = None, day_hi: str | None = None) -> list:
    """Ledger snapshot files, optionally bounded to a window of capture DAYS.

    The bound is on which days are opened, never on which rows within a day. A prediction made after the last
    candidate game kicked off, or a fortnight before it, cannot be a pregame prediction for that game, and
    reading every snapshot of the season to discover that would make the settle job grow without bound.
    """
    out = []
    for d in sorted(glob.glob(os.path.join(market_data, "data", "shadow", "ledger", "*"))):
        day = os.path.basename(d)
        if day_lo and day < day_lo:
            continue
        if day_hi and day > day_hi:
            continue
        out.extend(sorted(glob.glob(os.path.join(d, "*.observations.jsonl.gz"))))
    return out


def load_observations(market_data: str, game_ids=None, support_states=EVALUABLE_SUPPORT_STATES,
                      day_lo: str | None = None, day_hi: str | None = None):
    """Every pregame observation for the wanted games, grouped by game. Never modifies a ledger file."""
    by_game = defaultdict(list)
    skipped = Counter()
    files = ledger_files(market_data, day_lo, day_hi)
    want = set(game_ids) if game_ids else None
    for path in files:
        with gzip.open(path, "rt") as fh:
            for line in fh:
                row = json.loads(line)
                gid = row.get("game_id")
                if not gid or (want is not None and gid not in want):
                    continue
                if row.get("support_state") not in support_states:
                    skipped[row.get("support_state")] += 1
                    continue
                row["_ledger_file"] = os.path.basename(path)
                by_game[gid].append(row)
    return by_game, skipped, files


def kickoff_ts_of(game, observations):
    """Kickoff, from the schedule when possible and from the predictions themselves otherwise.

    The schedule is authoritative (nflverse gameday + gametime converted from US-Eastern). The ledger's own
    `kickoff_utc` is the fallback and is required to AGREE: if the two differ by more than a minute the run
    refuses to pick one, because a wrong kickoff silently changes which quote is the close.
    """
    sched = None
    if game is not None and game.kickoff_utc:
        sched = datetime.fromisoformat(game.kickoff_utc)
    stamped = {o.get("kickoff_utc") for o in observations if o.get("kickoff_utc")}
    led = None
    if stamped:
        parsed = sorted(datetime.fromisoformat(s.replace("Z", "+00:00")) for s in stamped)
        led = parsed[-1]
    if sched is not None and led is not None and abs((sched - led).total_seconds()) > 60:
        return None, None, (f"kickoff disagreement: schedule {sched.isoformat()} vs ledger {led.isoformat()}")
    ko = sched or led
    if ko is None:
        return None, None, "no kickoff time from the schedule or the ledger"
    return ko, ("schedule" if sched is not None else "ledger"), None


def candidate_games(book, explicit_games, lookback_days: float, now):
    """Which games this run may settle, and the ledger day window that can hold their pregame predictions.

    With `--game` the caller decides. Otherwise: games with a published final score whose kickoff is inside the
    lookback window. The window is what keeps a game that never had a prediction from being retried forever.
    """
    from datetime import timedelta
    if explicit_games:
        chosen = sorted(set(explicit_games))
    else:
        chosen = []
        for gid, g in book.games.items():
            if g.status != "FINAL" or not g.kickoff_utc:
                continue
            ko = datetime.fromisoformat(g.kickoff_utc)
            if now - timedelta(days=lookback_days) <= ko <= now:
                chosen.append(gid)
        chosen.sort()
    kicks = [datetime.fromisoformat(book.games[g].kickoff_utc) for g in chosen
             if g in book.games and book.games[g].kickoff_utc]
    if not kicks:
        return chosen, (None, None)
    lo = (min(kicks) - timedelta(days=21)).date().isoformat()
    hi = (max(kicks) + timedelta(days=1)).date().isoformat()
    return chosen, (lo, hi)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--market-data", required=True, help="market-data worktree (published ledger + capture)")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "shadow", "evaluations"),
                    help="local staging directory for NEW evaluation batches")
    ap.add_argument("--scorecard-out", default=os.path.join(ROOT, "data", "shadow", "scorecards"))
    ap.add_argument("--season", type=int, default=0, help="0 = every season present in the ledger")
    ap.add_argument("--game", action="append", default=[], help="settle only this game_id (repeatable)")
    ap.add_argument("--eval-version", default=E.EVALUATION_VERSION)
    ap.add_argument("--max-games", type=int, default=0)
    ap.add_argument("--days-back", type=int, default=14, help="capture days to scan for a pregame close")
    ap.add_argument("--lookback-days", type=float, default=10.0,
                    help="how far back to look for final games when no --game is given")
    ap.add_argument("--min-hours-after-kickoff", type=float, default=4.0)
    ap.add_argument("--close-max-staleness-min", type=float, default=E.CLOSE_MAX_STALENESS_S / 60.0)
    ap.add_argument("--dry-run", action="store_true", help="plan and report, write nothing")
    ap.add_argument("--no-scorecard", action="store_true")
    ap.add_argument("--no-kalshi-crosscheck", action="store_true",
                    help="skip comparing our proven settlement with Kalshi's own recorded result")
    ap.add_argument("--github-output", default="")
    a = ap.parse_args()
    t0 = datetime.now(timezone.utc)
    now = t0

    # results first: the schedule is three small files and it decides which games are even candidates, which in
    # turn bounds how much of the ledger has to be opened.
    seasons = [a.season] if a.season else sorted({t0.year, t0.year - 1})
    book = build_result_book(ROOT, seasons, min_hours_after_kickoff=a.min_hours_after_kickoff)
    print(f"results: {len(book.games)} scheduled games in {seasons}, stats for "
          f"{len(book.games_with_player_stats)}, snaps for {len(book.games_with_snaps)} "
          f"(sources {book.sources})", flush=True)

    candidates, window = candidate_games(book, a.game, a.lookback_days, now)
    if not candidates:
        print(f"no candidate games (final, kicked off within {a.lookback_days} days)")
        _emit(a.github_output, {"games_ready": 0, "games_deferred": 0, "written": 0, "status": "NOTHING_TO_DO"})
        return 0
    day_lo, day_hi = window
    print(f"candidates: {len(candidates)} game(s) {candidates[:8]}{' ...' if len(candidates) > 8 else ''}; "
          f"ledger days {day_lo}..{day_hi}", flush=True)

    by_game, skipped_states, lfiles = load_observations(a.market_data, candidates, day_lo=day_lo, day_hi=day_hi)
    print(f"ledger: {len(lfiles)} snapshot files, {sum(len(v) for v in by_game.values())} supported pregame "
          f"observations across {len(by_game)} games", flush=True)
    if skipped_states:
        print("  not evaluable (no model probability in the row): "
              + ", ".join(f"{k}={v}" for k, v in skipped_states.most_common()), flush=True)
    if not by_game:
        print("no supported pregame observations found for the candidate games; nothing to settle")
        _emit(a.github_output, {"games_ready": 0, "games_deferred": 0, "written": 0, "status": "NOTHING_TO_DO"})
        return 0

    corpus = ST.EvaluationCorpus(a.out, read_roots=[os.path.join(a.market_data, "data", "shadow", "evaluations")])
    batch = ST.batch_id(now)
    capture_root = os.path.join(a.market_data, "data", "kalshi", "capture")

    ready, deferred, written_total, noop_total, conflicts_total = [], [], 0, 0, 0
    manifests, per_game_report = [], []
    games = sorted(by_game)
    for gid in games:
        obs = by_game[gid]
        need_players = S.needs_player_stats(obs)
        state, reason = book.readiness(gid, needs_player_stats=need_players, now=now)
        if state != READY:
            deferred.append({"game_id": gid, "state": state, "reason": reason, "observations": len(obs)})
            print(f"  DEFER {gid}: {state} -- {reason} ({len(obs)} observations)", flush=True)
            continue
        if a.max_games and len(ready) >= a.max_games:
            deferred.append({"game_id": gid, "state": "SKIPPED_MAX_GAMES", "reason": "--max-games reached",
                             "observations": len(obs)})
            continue
        ready.append(gid)
        rep = settle_game(gid, obs, book, corpus, capture_root, a, batch, now)
        per_game_report.append(rep)
        written_total += rep["written"]
        noop_total += rep["unchanged"]
        conflicts_total += rep["conflicts"]
        if rep.get("manifest"):
            manifests.append(rep["manifest"])
        print(f"  {gid}: {rep['evaluated']} evaluations -> written {rep['written']}, unchanged "
              f"{rep['unchanged']}, conflicts {rep['conflicts']} | settled "
              f"{rep['settlement_counts'].get('SETTLED', 0)} | close "
              f"{rep['close_counts']}", flush=True)

    if conflicts_total:
        print(f"::error::{conflicts_total} evaluation conflict(s); nothing was written for the affected games")
        _emit(a.github_output, {"games_ready": len(ready), "games_deferred": len(deferred),
                                "written": written_total, "conflicts": conflicts_total, "status": "CONFLICT"})
        return 4

    scorecard_path = ""
    if not a.no_scorecard and not a.dry_run:
        rows = ST.read_corpus([a.out, os.path.join(a.market_data, "data", "shadow", "evaluations")])
        if rows:
            sc = build_scorecard(rows, evaluation_version=a.eval_version)
            d = os.path.join(a.scorecard_out, batch)
            os.makedirs(d, exist_ok=True)
            with open(os.path.join(d, "scorecard.json"), "w") as f:
                json.dump(sc, f, indent=1, default=str)
            with open(os.path.join(d, "REPORT.md"), "w") as f:
                f.write(render_report(sc, title=f"Shadow evaluation scorecard ({batch})") + "\n")
            scorecard_path = d
            print(f"scorecard: {sc['n_evaluations']} evaluations over {sc['n_games']} games -> {d}", flush=True)

    summary = {"batch_id": batch, "evaluation_version": a.eval_version,
               "games_ready": len(ready), "games_deferred": len(deferred),
               "written": written_total, "unchanged": noop_total, "conflicts": conflicts_total,
               "ready_games": ready, "deferred": deferred, "per_game": per_game_report,
               "scorecard": scorecard_path, "dry_run": a.dry_run,
               "seconds": (datetime.now(timezone.utc) - t0).total_seconds()}
    # Only when something was actually written. A no-op run must leave the staging directory byte-identical --
    # including this summary -- so "nothing changed" is verifiable rather than asserted.
    if not a.dry_run and written_total:
        os.makedirs(a.out, exist_ok=True)
        with open(os.path.join(a.out, f"_run.{batch}.summary.json"), "w") as f:
            json.dump(summary, f, indent=1, default=str)
    print(json.dumps({k: v for k, v in summary.items() if k != "per_game"}, indent=1, default=str))
    _emit(a.github_output, {"games_ready": len(ready), "games_deferred": len(deferred),
                            "written": written_total, "unchanged": noop_total, "conflicts": 0,
                            "batch_id": batch, "scorecard": scorecard_path,
                            "status": "WROTE" if written_total else "NO_OP"})
    return 0


def settle_game(gid, obs, book, corpus, capture_root, a, batch, now) -> dict:
    game = book.games.get(gid)
    ko, ko_source, ko_problem = kickoff_ts_of(game, obs)
    tickers = sorted({o["ticker"] for o in obs})
    quotes, qstats = ({}, {"files_read": 0, "rows_matched": 0}) if ko_problem else load_game_quotes(
        capture_root, gid, tickers, kickoff_utc=game.kickoff_utc if game else None, days_back=a.days_back)
    kickoff_ts = ko.timestamp() if ko else None
    closes = {}
    for t in tickers:
        qs = quotes.get(t, [])
        # Count PREGAME candidates only. The number of rows loaded for a ticker keeps growing while the capture
        # runs through the evening, so recording it would make an identical rerun the next morning look like a
        # different truth and raise a conflict. The count of quotes before kickoff is fixed the moment the game
        # starts, and it is the number a reader actually wants ("how much of a price history was there?").
        pregame = [q for q in qs if q.get("observed_ts") is not None and kickoff_ts is not None
                   and q["observed_ts"] < kickoff_ts]
        closes[t] = (E.pick_close(qs, kickoff_ts), len(pregame))

    rows, scount, ccount = [], Counter(), Counter()
    for o in obs:
        close, seen = closes.get(o["ticker"], (None, 0))
        # The no-snap branch settles at "the last fair market price before game start", which is exactly the
        # close midpoint -- so a settlement that needs a fair price is only possible where a close exists.
        fair = close.get("mid") if close else None
        st = S.settle_observation(o, book, fair_price=fair)
        ev = E.evaluate(o, close, settlement=st, kickoff_ts=kickoff_ts,
                        evaluation_version=a.eval_version, close_candidates_seen=seen,
                        settlement_source=SETTLEMENT_SOURCE,
                        max_close_staleness_s=a.close_max_staleness_min * 60.0)
        if ko_problem:
            ev.notes = (ev.notes + "; " if ev.notes else "") + f"close not selected: {ko_problem}"
        rows.append(ev.to_dict())
        scount[st.status] += 1
        ccount[ev.close_status] += 1

    cross = ({} if a.no_kalshi_crosscheck else
             crosscheck(rows, load_kalshi_settlements(capture_root, gid, tickers,
                                                     kickoff_utc=game.kickoff_utc if game else None)))
    if cross.get("disagreements"):
        print(f"::warning::{gid}: {len(cross['disagreements'])} settlement(s) disagree with Kalshi's own "
              f"recorded result (ours is written; the disagreement is recorded for review): "
              f"{[d['ticker'] for d in cross['disagreements'][:5]]}", flush=True)

    plan = corpus.plan(rows, gid)
    rep = {"game_id": gid, "evaluated": len(rows), "tickers": len(tickers), "kalshi_crosscheck": {
               k: v for k, v in cross.items() if k != "disagreements"},
           "kickoff_utc": game.kickoff_utc if game else None, "kickoff_source": ko_source,
           "kickoff_problem": ko_problem, "quote_rows_scanned": qstats.get("rows_matched"),
           "settlement_counts": dict(scount), "close_counts": dict(ccount),
           "written": 0, "unchanged": len(plan["noop"]), "conflicts": len(plan["conflicts"]),
           "conflict_detail": plan["conflicts"][:10]}
    if plan["conflicts"]:
        for c in plan["conflicts"][:5]:
            print(f"::error::conflict on {c['prediction_id']} ({gid}): "
                  + ", ".join(f"{k} existing={v[0]!r} new={v[1]!r}" for k, v in list(c["fields"].items())[:4]),
                  flush=True)
        return rep
    if a.dry_run:
        rep["written"] = 0
        rep["would_write"] = len(plan["new"])
        return rep
    man = corpus.write_batch(gid, rows, evaluation_version=a.eval_version, batch=batch, plan=plan,
                             manifest_extra={
                                 "kickoff_utc": game.kickoff_utc if game else None,
                                 "kickoff_source": ko_source,
                                 "game_evidence": game.evidence() if game else None,
                                 "result_sources": book.sources,
                                 "ledger_snapshots": sorted({o.get("run_id") for o in obs}),
                                 "tickers": len(tickers),
                                 "quote_rows_scanned": qstats.get("rows_matched"),
                                 "capture_days_scanned": qstats.get("days"),
                                 "by_settlement_reason": _top_reasons(rows),
                                 "kalshi_crosscheck": {k: v for k, v in cross.items()
                                                       if k != "disagreements"}})
    if cross:
        # written next to the batch, not inside it: Kalshi's result is evidence ABOUT our settlement, never the
        # settlement itself, and it can arrive after the corpus row it comments on.
        with open(os.path.join(ST.game_dir(a.out, gid),
                               f"{a.eval_version}.{batch}.kalshi_crosscheck.json"), "w") as f:
            json.dump({"game_id": gid, "batch_id": batch, **cross}, f, indent=1, default=str)
    rep["written"] = man.get("written", 0)
    rep["manifest"] = man
    return rep


def crosscheck(rows, kalshi: dict) -> dict:
    """Compare our proven settlements against Kalshi's own recorded results, per ticker.

    Reported, never substituted. Agreement is the normal case and is worth counting; a disagreement is either a
    bug in our reading or a Kalshi settlement that contradicts the game (both happened in 2025), and either way
    a human should see it.
    """
    if not kalshi:
        return {}
    seen, agree, disagree, unknown, missing = set(), 0, 0, 0, 0
    details = []
    for r in rows:
        t = r.get("ticker")
        if t in seen:
            continue                      # one comparison per ticker, not per snapshot
        seen.add(t)
        k = kalshi.get(t)
        if k is None:
            missing += 1
            continue
        payout, kind = kalshi_yes_payout(k)
        if r.get("settlement_status") != "SETTLED":
            unknown += 1
            continue
        if payout is None:
            if kind == "scalar" and r.get("settlement_kind") in ("scalar_fair_price", "tie_split"):
                agree += 1
            else:
                unknown += 1
            continue
        if r.get("settled_yes") is not None and abs(float(r["settled_yes"]) - payout) < 1e-9:
            agree += 1
        else:
            disagree += 1
            details.append({"ticker": t, "ours": r.get("settled_yes"), "our_kind": r.get("settlement_kind"),
                            "kalshi_result": k.get("result"), "kalshi_observed_at": k.get("observed_at"),
                            "our_reason": r.get("settlement_reason"),
                            "evidence": r.get("settlement_evidence")})
    return {"tickers_compared": len(seen), "kalshi_results_available": len(kalshi), "agree": agree,
            "disagree": disagree, "not_comparable": unknown, "no_kalshi_result": missing,
            "disagreements": details[:50]}


def _top_reasons(rows, limit=12):
    c = Counter(r.get("settlement_reason") for r in rows if r.get("settlement_status") != "SETTLED")
    return {str(k): v for k, v in c.most_common(limit)}


def _emit(path, values: dict):
    if not path:
        return
    with open(path, "a") as f:
        for k, v in values.items():
            f.write(f"{k}={v}\n")


if __name__ == "__main__":
    sys.exit(main())
