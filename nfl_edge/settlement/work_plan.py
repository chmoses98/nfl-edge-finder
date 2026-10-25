"""Bounded, resumable partitioning of the postgame drivers' per-game work.

WHY THIS EXISTS. The settlement and close drivers used to take every owed game, in game-id order, and stream
each one from every projection file that holds it. A snapshot file holds every game on the board, so a slate of N
owed games decompressed the same files N times, and a run had no upper bound: 33 owed games at ~4 minutes each
(measured on run 40144005725) is two hours, the job timeout, and the write-once batches the run had already
produced were never published because the publishing steps come after. Nothing here changes WHAT is settled or
paired; it only decides HOW MUCH is attempted in one run and in what order:

  * games are taken OLDEST KICKOFF FIRST, so the backlog drains in the order the evidence ages out;
  * games that already hold their immutable batch are never in the list (the drivers filter them by file name
    before they call this), so a rerun does only the remainder -- that is the resume;
  * the games of one run are partitioned into GROUPS that are streamed together in one pass over the projection
    files, each group bounded by the rows it will hold in memory;
  * a run stops STARTING groups when its wall-clock budget is spent (or its game cap is reached), reports what it
    postponed, and the next scheduled run picks the remainder up. The first group is always attempted, so a
    single game larger than the whole budget cannot be starved forever.

The cost model is deliberately coarse and conservative; it is only used to refuse to START a group that cannot
finish inside the budget. The hard stop remains the workflow step's own timeout.
"""
from __future__ import annotations

import time

# Measured, see docs/POSTGAME_SETTLEMENT.md "Bounded runs". Seconds to decompress and prefilter one projection
# file (~29k lines, ~230 MB raw): 0.3 s on the Actions runner, 0.45-0.7 s on a slower box; rounded up.
SCAN_SECONDS_PER_FILE = 0.8
# Seconds per probability row to parse, settle, diagnose and plan. Before nfl_edge/settlement/team_game_index.py the
# autopsy scanned every player row of the book per record: the 2026_04_ATL_NO game (111,644 settlement rows + 44,324
# autopsies) took ~19 minutes beyond its scan on the runner, ~7 ms per row. Now ~0.25 ms per settlement row and
# ~0.7 ms per autopsy (measured on real 2026_06_SEA_DEN rows); rounded up ~4x so the estimate stays conservative.
SETTLE_SECONDS_PER_ROW = 0.002
# Closes: one canonical-close selection per ticker plus a CLV record per row; a fraction of a settlement.
CLOSE_SECONDS_PER_ROW = 0.0015
# Rows held in memory by one group (new settlement rows + autopsies, or close + CLV rows). 150k rows held the
# runner at ~1 GB (rss 1047 MB with the 111,644-row game above); the same budget keeps a group of ordinary games
# (400-700 rows each) to a single pass over the files.
DEFAULT_MAX_GROUP_ROWS = 150_000
# The close driver holds one close record (and a CLV record) for EVERY projection row of a game - refusals included -
# and a game's rows run to ~100-300k by the time the archive spans three weeks, so its group is sized in rows of the
# index's per-game `n`. A close/CLV pair is lighter than a settlement + autopsy row.
DEFAULT_MAX_GROUP_ROWS_CLOSES = 600_000


def oldest_first(games: dict, game_ids) -> list:
    """`game_ids` ordered by first kickoff (unknown kickoff last), then by id. `games` is ProjectionIndex.games()."""
    def key(gid):
        ko = (games.get(gid) or {}).get("kickoff_utc") or "9999"
        return (str(ko), gid)
    return sorted(dict.fromkeys(game_ids), key=key)


def partition(game_ids, games: dict, *, max_rows: int = DEFAULT_MAX_GROUP_ROWS, row_key: str = "prob") -> list:
    """Consecutive games into groups, each holding at most `max_rows` of `row_key` rows (a lone larger game is its own
    group). Order is preserved, so the oldest games are in the earliest groups."""
    groups, cur, held = [], [], 0
    for gid in game_ids:
        n = int((games.get(gid) or {}).get(row_key) or 0)
        if cur and held + n > max_rows:
            groups.append(cur)
            cur, held = [], 0
        cur.append(gid)
        held += n
    if cur:
        groups.append(cur)
    return groups


def estimate_seconds(group, games: dict, *, row_key: str = "prob", per_row: float = SETTLE_SECONDS_PER_ROW) -> float:
    """Scan (one pass over the union of the group's files) plus per-row work."""
    files = set()
    rows = 0
    for gid in group:
        g = games.get(gid) or {}
        files.update(g.get("files") or ())
        rows += int(g.get(row_key) or 0)
    return len(files) * SCAN_SECONDS_PER_FILE + rows * per_row


class Budget:
    """A run's wall-clock budget. `minutes <= 0` means unbounded. `clock` is injectable so tests need no sleeping."""

    def __init__(self, minutes: float = 0.0, *, clock=time.monotonic, started: float | None = None):
        self.minutes = float(minutes or 0.0)
        self.clock = clock
        self.t0 = clock() if started is None else started

    @property
    def bounded(self) -> bool:
        return self.minutes > 0

    def elapsed(self) -> float:
        return self.clock() - self.t0

    def remaining(self) -> float:
        return float("inf") if not self.bounded else self.minutes * 60.0 - self.elapsed()

    def allows(self, estimate_s: float, *, first: bool = False) -> bool:
        """May a unit of work estimated at `estimate_s` seconds START now? The first unit of a run always may."""
        return True if (first or not self.bounded) else self.remaining() >= estimate_s


def select_groups(groups: list, games: dict, budget: Budget, *, max_games: int = 0, row_key: str = "prob",
                  per_row: float = SETTLE_SECONDS_PER_ROW):
    """Generator over the groups this run should process, stopping at the game cap or when the budget cannot hold the
    next group. Yields (group, postponed_after) lazily so the budget is checked against the CLOCK AT THE TIME the
    group would start, not when the plan was made. Call .postponed on the returned object after exhausting it."""
    return _Selection(groups, games, budget, max_games, row_key, per_row)


class _Selection:
    def __init__(self, groups, games, budget, max_games, row_key, per_row):
        self.groups, self.games, self.budget = groups, games, budget
        self.max_games, self.row_key, self.per_row = int(max_games or 0), row_key, per_row
        self.taken: list = []
        self.postponed: list = []
        self.reason = None

    def __iter__(self):
        n_taken = 0
        for i, group in enumerate(self.groups):
            if self.max_games and n_taken >= self.max_games:
                self._postpone(self.groups[i:], f"game cap {self.max_games} reached")
                return
            if self.max_games and n_taken + len(group) > self.max_games:
                group = group[: self.max_games - n_taken]
                self._postpone([self.groups[i][len(group):]] + self.groups[i + 1:], f"game cap {self.max_games} reached")
                n_taken += len(group)
                self.taken += group
                yield group
                return
            est = estimate_seconds(group, self.games, row_key=self.row_key, per_row=self.per_row)
            if not self.budget.allows(est, first=not self.taken):
                self._postpone(self.groups[i:], f"time budget: ~{est / 60:.0f} min needed for the next group, "
                                                f"{max(self.budget.remaining(), 0) / 60:.0f} min left")
                return
            n_taken += len(group)
            self.taken += group
            yield group

    def _postpone(self, groups, reason):
        self.postponed = [g for grp in groups for g in grp]
        self.reason = reason
