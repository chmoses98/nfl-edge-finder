#!/usr/bin/env python3
"""Build the FULL-BOARD RETROSPECTIVE RESEARCH TABLE and its COVERAGE FUNNEL for a set of weeks.

    python3 scripts/research/board_research.py --season 2026 --weeks 1,2,3 --out data/research/board/2026 \\
        [--md-ref origin/market-data | --market-data /tmp/md] [--repo .]

Reads the capture straight out of git objects by default (`--md-ref`): a capture day is ~0.5 GB of JSON on disk
but ~10 MB as packed objects, so the build never checks the capture out. `git cat-file --batch` streams every
file once, in run order; the builder rejects other weeks' rows before parsing them (nfl_edge/research/board.py).
`--market-data DIR` reads an ordinary checkout instead (tests, local worktrees).

Outputs (derived, rebuildable, never written into any corpus):
    <out>/board_rows.wk<NN>.jsonl.gz       one row per contract x canonical horizon
    <out>/board_coverage.json              the funnel per week x family with exclusion reasons
    <out>/board_build.json                 inputs, versions, counts, runtime, peak memory

RESEARCH ONLY. Nothing here is read by the pricer, the gates, the risk policy or RUN NFL's betting path.
"""
from __future__ import annotations

import argparse
import glob
import gzip
import json
import os
import resource
import subprocess
import sys
import time
from collections import Counter, defaultdict

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, ROOT)

from nfl_edge.research import board as B                                              # noqa: E402

RESOLVED = ("RESOLVED", "RESOLVED_TEAM_UNCONFIRMED", "RESOLVED_PLAYERS_TABLE", "RESOLVED_JERSEY_MISMATCH")


def log(*a):
    print(*a, flush=True)


# ------------------------------------------------------------------------------------------------------ sources
def _git_version(repo) -> tuple:
    try:
        out = subprocess.run(["git", "--version"], cwd=repo, capture_output=True, text=True).stdout
        return tuple(int(x) for x in out.split()[2].split(".")[:2])
    except (OSError, ValueError, IndexError):
        return (0, 0)


class GitSource:
    """Files of one ref, read through `git cat-file --batch` without a checkout."""

    def __init__(self, repo: str, ref: str):
        self.repo, self.ref = repo, ref

    def ls(self, prefix: str) -> list:
        out = subprocess.run(["git", "ls-tree", "-r", self.ref, prefix], cwd=self.repo, capture_output=True, text=True, check=True).stdout
        rows = []
        for line in out.splitlines():
            meta, path = line.split("\t", 1)
            rows.append((path, meta.split()[2]))
        return rows

    def prefetch(self, items, chunk: int = 400) -> int:
        """Bulk-fetch the blobs a blobless clone lacks, a few hundred per request. Without it `cat-file` fetches
        each missing blob lazily, one round trip per file (thousands per week). Returns how many were missing."""
        oids = [o for _p, o in items]
        if not oids:
            return 0
        if _git_version(self.repo) >= (2, 44):
            # GIT_NO_LAZY_FETCH (git 2.44+) makes the presence check itself fetch nothing
            env = {**os.environ, "GIT_NO_LAZY_FETCH": "1"}
            r = subprocess.run(["git", "cat-file", "--batch-check"], cwd=self.repo, input="\n".join(oids) + "\n",
                               capture_output=True, text=True, env=env)
            missing = [line.split()[0] for line in r.stdout.splitlines() if line.endswith(" missing")]
        else:
            missing = oids            # older git would lazily fetch inside the check; ask for all, present ones are no-ops
        for i in range(0, len(missing), chunk):
            subprocess.run(["git", "-c", "fetch.negotiationAlgorithm=noop", "fetch", "--no-tags", "--no-write-fetch-head",
                            "--filter=blob:none", "origin", *missing[i:i + chunk]], cwd=self.repo, check=True,
                           capture_output=True)
        return len(missing)

    def stream(self, items):
        """Yield (path, bytes) for (path, oid) items, in the given order, one process for the whole batch."""
        if not items:
            return
        p = subprocess.Popen(["git", "cat-file", "--batch"], cwd=self.repo, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
        import threading

        def feed():
            for _path, oid in items:
                p.stdin.write((oid + "\n").encode())
            p.stdin.close()
        th = threading.Thread(target=feed, daemon=True)
        th.start()
        for path, _oid in items:
            header = p.stdout.readline().decode().split()
            if len(header) < 3 or header[1] == "missing":
                raise RuntimeError(f"git object missing for {path}: {header}")
            size = int(header[2])
            data = p.stdout.read(size)
            p.stdout.read(1)
            yield path, data
        th.join()
        p.wait()


class DirSource:
    def __init__(self, root: str):
        self.root = root

    def prefetch(self, items, chunk: int = 400) -> int:
        return 0

    def ls(self, prefix: str) -> list:
        base = os.path.join(self.root, prefix)
        out = []
        for dirpath, _dirs, files in os.walk(base):
            for fn in files:
                full = os.path.join(dirpath, fn)
                out.append((os.path.relpath(full, self.root), full))
        return sorted(out)

    def stream(self, items):
        for path, full in items:
            with open(full, "rb") as f:
                yield path, f.read()


# ------------------------------------------------------------------------------------------------------ loaders
def capture_items(src, games: dict, days_back: int):
    from datetime import timedelta
    lo = (min(g.kickoff for g in games.values()) - timedelta(days=days_back)).date().isoformat()
    hi = max(g.kickoff for g in games.values()).date().isoformat()
    allf = src.ls("data/kalshi/capture")
    def day(p):
        parts = p.split("/")
        return parts[3] if len(parts) > 4 else None
    quotes = sorted([(p, o) for p, o in allf if p.endswith(".quotes.jsonl") and day(p) and lo <= day(p) <= hi], key=lambda x: os.path.basename(x[0]))
    mans = [(p, o) for p, o in allf if p.endswith(".manifest.json") and day(p) and lo <= day(p) <= hi]
    state = [(p, o) for p, o in allf if p.endswith("capture/state.json")]
    return quotes, mans, state, (lo, hi)


def discovery_markets(src, run: str | None) -> tuple[dict, str]:
    """ticker -> market record of the newest discovery run (every status; settled records carry the result)."""
    runs = sorted({p.split("/")[3] for p, _o in src.ls("data/kalshi/discovery") if p.endswith("/summary.json")})
    if not runs:
        return {}, None
    use = run or runs[-1]
    items = [(p, o) for p, o in src.ls(f"data/kalshi/discovery/{use}/markets") if p.endswith(".json")]
    src.prefetch(items)
    out = {}
    for _p, data in src.stream(items):
        try:
            mk = json.loads(data)
        except ValueError:
            continue
        for state in ("open", "closed", "settled"):
            for m in ((mk.get(state) or {}).get("markets") or []):
                t = m.get("ticker")
                if t and (t not in out or state == "settled"):
                    out[t] = m
    return out, use


def load_player_map(path: str) -> dict:
    import polars as pl
    if not os.path.exists(path):
        return {}
    m = pl.read_parquet(path).filter(pl.col("gsis_id").is_not_null() & pl.col("status").is_in(list(RESOLVED)))
    return dict(zip(m["kalshi_player_id"].to_list(), m["gsis_id"].to_list()))


def load_positions(root: str) -> dict:
    import polars as pl
    p = os.path.join(root, "data/raw/nflverse/players/players.parquet")
    if not os.path.exists(p):
        return {}
    t = pl.read_parquet(p).select("gsis_id", "position")
    return dict(zip(t["gsis_id"].to_list(), t["position"].to_list()))


def corpus_rows(src, prefix: str, suffix: str, game_ids: set):
    items = [(p, o) for p, o in src.ls(prefix) if p.endswith(suffix) and p.split("/")[3] in game_ids]
    src.prefetch(items)
    for _p, data in src.stream(items):
        for line in gzip.decompress(data).decode().splitlines():
            if line.strip():
                yield json.loads(line)


def account_discovery(disc: dict, captured: set, games: dict, sched_key: dict, season: int, funnel) -> dict:
    """Place EVERY discovery market: a target-week game contract (captured or not), another week's game, a
    non-game contract (season, futures, awards, leaders), or unclassifiable. Target-week contracts that never
    produced a pregame capture row enter the funnel with that reason; nothing is left uncounted."""
    from nfl_edge.kalshi.classifier import classify
    cats = Counter()
    for t, m in disc.items():
        try:
            sem = classify(m)
        except Exception:  # noqa: BLE001
            funnel.add_universe("UNCLASSIFIABLE", None); cats["UNCLASSIFIABLE"] += 1
            continue
        if not (sem.game_date and sem.away_team and sem.home_team):
            funnel.add_universe("NON_GAME (season / futures / awards / leaders)", sem.family); cats["NON_GAME"] += 1
            continue
        gid = sched_key.get((sem.game_date, sem.away_team, sem.home_team))
        g = games.get(gid) if gid else None
        if g is None:
            cat = "GAME_OTHER_WEEKS" if gid else "GAME_NOT_IN_REG_SCHEDULE (preseason / prior season)"
            funnel.add_universe(cat, sem.family); cats[cat] += 1
            continue
        funnel.add_universe("GAME_TARGET_WEEKS", sem.family); cats["GAME_TARGET_WEEKS"] += 1
        if t not in captured:
            funnel.add_discovered_only(g.week, sem.family, "captured_pregame: discovered, never in a pregame capture row "
                                       "(series outside the capture tiers, or listed only after kickoff)")
            cats["GAME_TARGET_WEEKS_NEVER_CAPTURED"] += 1
    return dict(cats)


# ------------------------------------------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--season", type=int, default=2026)
    ap.add_argument("--weeks", default="1,2,3")
    ap.add_argument("--out", default=os.path.join(ROOT, "data", "research", "board", "2026"))
    ap.add_argument("--md-ref", default="origin/market-data")
    ap.add_argument("--repo", default=ROOT)
    ap.add_argument("--market-data", default="", help="read an ordinary market-data checkout instead of git objects")
    ap.add_argument("--discovery-run", default="", help="discovery run for static terms + exchange results (default newest)")
    ap.add_argument("--player-map", default=os.path.join(ROOT, "data", "silver", "kalshi_player_map.parquet"))
    ap.add_argument("--days-back", type=int, default=14)
    ap.add_argument("--no-context", action="store_true", help="skip the arm / anatomy research-context joins")
    a = ap.parse_args()
    t0 = time.time()
    weeks = [int(w) for w in a.weeks.split(",") if w.strip()]
    src = DirSource(a.market_data) if a.market_data else GitSource(a.repo, a.md_ref)

    from nfl_edge.settlement.nflverse_results import build_result_book
    from nfl_edge.settlement.period_results import PeriodBook
    from nfl_edge.settlement.results import games_from_schedule_text, load_schedule_text
    from nfl_edge.execution.fees import load_fee_schedule

    text, sched_src = load_schedule_text(ROOT)
    sched_all = games_from_schedule_text(text, seasons=[a.season])
    games = B.games_from_schedule(sched_all, season=a.season, weeks=weeks)
    import csv
    import io
    sched_key = {}
    gameday = {}
    for r in csv.DictReader(io.StringIO(text)):
        if str(r.get("season")) == str(a.season):
            sched_key[(r["gameday"], r["away_team"], r["home_team"])] = r["game_id"]
            gameday[r["game_id"]] = r["gameday"]
    for gid, g in games.items():
        g.gameday = gameday.get(gid, g.gameday)
    log(f"schedule {sched_src}: {len(games)} games in weeks {weeks}")

    builder = B.BoardBuilder(games)
    quotes, mans, state, (lo, hi) = capture_items(src, games, a.days_back)
    log(f"capture {lo}..{hi}: {len(quotes)} quote files, {len(mans)} manifests")
    log(f"prefetched {src.prefetch(quotes + mans + state)} missing capture blobs")
    for _p, data in src.stream(mans):
        try:
            builder.manifests.add(json.loads(data))
        except ValueError:
            builder.stats["bad_manifests"] += 1
    for _p, data in src.stream(state):
        try:
            builder.last_seen = json.loads(data).get("last_seen") or {}
        except ValueError:
            pass
    nf = 0
    for _p, data in src.stream(quotes):
        builder.feed_quote_lines(data.decode().splitlines())
        nf += 1
        if nf % 250 == 0:
            log(f"  {nf}/{len(quotes)} quote files, {len(builder.contracts)} contracts, rss {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss/1024:.0f} MB")
    builder.finalize()
    log(f"stream done: {dict(builder.stats)}; {len(builder.contracts)} game-linked contracts")

    disc, disc_run = discovery_markets(src, a.discovery_run or None)
    log(f"discovery {disc_run}: {len(disc)} markets")
    book = build_result_book(ROOT, [a.season])
    pbook = PeriodBook()
    pbp = os.path.join(ROOT, "data", "raw", "nflverse", "pbp", f"play_by_play_{a.season}.parquet")
    if os.path.exists(pbp):
        finals = {gid: (g.home_score, g.away_score, g.overtime) for gid, g in book.games.items()}
        pbook.load_pbp(pbp, finals)
    player_map = load_player_map(a.player_map)
    positions = load_positions(ROOT)
    fees = B.FeeCache(load_fee_schedule(ROOT))

    settlements = {}
    for t, c in builder.contracts.items():
        fs = B.football_settlement(c.static, disc.get(t), book, pbook, player_map)
        settlements[t] = {**fs, **B.resolve_settlement(fs)}
    log("settlement: " + json.dumps(Counter((s["settlement_source"], s["settlement_status"]) for s in settlements.values()).most_common(12), default=str))

    arm_c = arm_g = anat = None
    if not a.no_context:
        gids = set(games)
        arm_c = B.arm_contract_index(corpus_rows(src, "data/shadow/arm_evaluations", ".arm_contract_evaluations.jsonl.gz", gids))
        arm_g = B.arm_game_index(corpus_rows(src, "data/shadow/arm_evaluations", ".arm_game_evaluations.jsonl.gz", gids))
        anat = B.anatomy_index(corpus_rows(src, "data/shadow/player_anatomy", ".anatomy.jsonl.gz", gids))
        log("context indexes built")

    os.makedirs(a.out, exist_ok=True)
    funnel = B.CoverageFunnel()
    per_week = Counter()
    by_week_games = defaultdict(list)
    for g in games.values():
        by_week_games[g.week].append(g)
    files = {}
    for wk in sorted(by_week_games):
        path = os.path.join(a.out, f"board_rows.wk{wk:02d}.jsonl.gz")
        def rows():
            for g in sorted(by_week_games[wk], key=lambda g: g.game_id):
                for r in B.assemble_game(builder, g, settlements, fees, positions=positions, arm_contracts=arm_c,
                                         arm_games=arm_g, anatomy=anat, player_map=player_map):
                    funnel.add_row(r)
                    yield r
        n = B.write_jsonl_gz(path, rows())
        per_week[wk] = n
        files[wk] = os.path.relpath(path, a.out)
        log(f"week {wk}: {n} rows -> {path}")
    universe = account_discovery(disc, set(builder.contracts), games, sched_key, a.season, funnel)
    cov = funnel.to_dict()
    cov.update({"board_version": B.BOARD_VERSION, "season": a.season, "weeks": weeks, "discovery_run": disc_run,
                "discovery_universe_summary": universe, "discovery_markets_total": len(disc),
                "note": "contract-level funnel at the PRIMARY horizon (latest_pregame); horizon_states counts every "
                        "contract x horizon row by analysis state"})
    with open(os.path.join(a.out, "board_coverage.json"), "w") as f:
        json.dump(cov, f, indent=1, default=str)
    build = {"board_version": B.BOARD_VERSION, "season": a.season, "weeks": weeks, "rows_by_week": dict(per_week), "files": files,
             "source": a.market_data or f"git:{a.md_ref}", "md_commit": None, "capture_days": [lo, hi], "quote_files": len(quotes),
             "manifests": builder.manifests.n_manifests, "stream_stats": dict(builder.stats), "contracts": len(builder.contracts),
             "discovery_run": disc_run, "schedule_source": sched_src, "result_sources": book.sources,
             "player_map_entries": len(player_map), "runtime_s": round(time.time() - t0, 1),
             "peak_rss_mb": round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1), "betting_authorized": False}
    if not a.market_data:
        try:
            build["md_commit"] = subprocess.run(["git", "rev-parse", a.md_ref], cwd=a.repo, capture_output=True, text=True).stdout.strip()
        except OSError:
            pass
    with open(os.path.join(a.out, "board_build.json"), "w") as f:
        json.dump(build, f, indent=1, default=str)
    log(json.dumps({k: build[k] for k in ("rows_by_week", "contracts", "runtime_s", "peak_rss_mb")}))
    return 0


if __name__ == "__main__":
    sys.exit(main())
