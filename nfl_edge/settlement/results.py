"""Proven final results: what actually happened, with the evidence that proves it.

This is the truth side of postgame settlement. Nothing here knows about Kalshi contracts; it answers only
football questions -- did this game finish, what was the score, did this player take a snap, what did the
player record -- and it refuses to answer when the free evidence does not prove it.

WHY A SEPARATE READINESS STATE
------------------------------
An evaluation record is immutable, so a record written from incomplete evidence is a permanent defect. The
dangerous shape is not a missing game: it is a game whose SCORE is published (schedules updates within
minutes) while its PLAYER STATS are not (the nflverse stats release lags by hours). Settling the game
families immediately and the player props "unavailable" would write refusals that a later run would want to
replace with settlements -- exactly the contradiction the corpus forbids.

So readiness is a per-game gate, evaluated BEFORE anything is written:

    READY                 final is PROVEN, and every table this game's predictions need is populated
    DEFER_NOT_FINAL       the score fields are absent, incomplete, or look provisional
    DEFER_FINAL_UNPROVEN  the score fields look final but nothing independent attests the game is complete
    DEFER_STATS_PENDING   final, but the player-stats release does not contain this game yet
    DEFER_SNAPS_PENDING   final, stats present, but snap counts (participation proof) are not
    DEFER_EXCHANGE_SETTLEMENT_PENDING  a prediction needs the exchange's own scalar value and that market has not
                          terminally settled yet, or could not be read: retryable, so nothing is written
    DEGRADED_INCONSISTENT the evidence contradicts itself (result != home - away, or a source disagrees)

A deferred game writes NOTHING and is reported. The next run writes the whole truth at once.

WHAT COUNTS AS FINAL
--------------------
A populated score is NOT a final status, and elapsed time is not evidence. nflverse rebuilds `games.csv` on a
schedule, so a row can carry a score while the game is still being played. FINAL therefore requires ALL of:

  * `home_score` and `away_score` present;
  * the POSTGAME-ONLY fields present and agreeing with them: `result == home - away`, `total == home + away`,
    and an `overtime` flag. nflverse computes these when it processes a finished game, so their absence beside
    a populated score is the signature of a provisional row -- that case is `DEFER_NOT_FINAL`, whatever the
    clock says;
  * at least this long past kickoff (necessary, never sufficient);
  * an INDEPENDENT attestation that the game is complete -- see `final_status.py`: presence in the
    postgame-only nflverse releases, or ESPN's explicit `status.type.completed`.

Any contradiction between sources fails closed.

PARTICIPATION
-------------
Kalshi player props settle on "at least one snap, even if nullified by penalty" (see
docs/KALSHI_SETTLEMENT.md). Two independent proofs of a snap are accepted:

  * a snap-count row with offense + defense + special-teams snaps >= 1;
  * a recorded counting stat > 0 -- a player cannot record a reception without being on the field.

Absence of a snap-count row is NOT proof of absence: nflverse snap counts come from PFR game pages, and a
missing row can mean inactive, or can mean the page did not list the player. `played` is therefore a
tri-state (True / False / None) and None means unproven, which the settlement engine turns into a refusal.
"""
from __future__ import annotations

import csv
import io
import math
import os
from dataclasses import dataclass, field

from nfl_edge.data.nfl_calendar import SCHEDULE_URL, kickoff_utc, schedule_candidates, season_type_of

FINAL = "FINAL"
NOT_FINAL = "NOT_FINAL"

READY = "READY"
DEFER_NOT_FINAL = "DEFER_NOT_FINAL"
DEFER_FINAL_UNPROVEN = "DEFER_FINAL_UNPROVEN"
# A prediction needs the exchange's own scalar value and that market has not terminally settled (or could not be
# read). Retryable: the schedule tries again rather than freezing "unavailable" into the corpus.
DEFER_EXCHANGE_SETTLEMENT_PENDING = "DEFER_EXCHANGE_SETTLEMENT_PENDING"
DEFER_STATS_PENDING = "DEFER_STATS_PENDING"
DEFER_SNAPS_PENDING = "DEFER_SNAPS_PENDING"
DEGRADED_INCONSISTENT = "DEGRADED_INCONSISTENT"

# A game is not treated as plausibly finished until this long after kickoff, even if a score is published.
# An NFL game runs a little over three hours; four is the honest rounding used by nfl_calendar.
MIN_HOURS_AFTER_KICKOFF = 4.0

# Canonical stat name -> the nflverse stats_player_week column that proves it.
# `touchdowns` is deliberately absent: it is a SUM over several columns and is resolved by `player_touchdowns`.
STAT_COLUMNS = {
    "passing_yards": "passing_yards",
    "attempts": "attempts",
    "completions": "completions",
    "passing_tds": "passing_tds",
    "interceptions": "passing_interceptions",
    "rushing_yards": "rushing_yards",
    "carries": "carries",
    "receiving_yards": "receiving_yards",
    "receptions": "receptions",
    "rushing_tds": "rushing_tds",
    "receiving_tds": "receiving_tds",
}
# Columns summed for "touchdowns scored" (KXNFLANYTD / KXNFLTD / KXNFL2TD).
#
# The rules text is "the market settles based on touchdowns scored", not "rushing or receiving touchdowns",
# so every way a player can be credited with a touchdown counts. `special_teams_tds` covers kick and punt
# returns, `def_tds` interception returns, `fumble_recovery_tds` a fumble recovered in the end zone.
#
# `fumble_recovery_tds` is here because the archive cross-check found it, not because it was guessed. Two
# 2025 anytime-touchdown markets settled YES on players nflverse credits with NO rushing, receiving, return
# or defensive touchdown -- Woody Marks (2025_15_ARI_HOU) and Tyler Lockett (2025_05_TEN_ARI). Both recovered
# a fumble in the end zone. Without this column the engine would have called Kalshi's correct settlement
# wrong, on exactly the kind of play a reading built from the common cases never sees.
# See scripts/research/settlement_archive_validation.py.
TOUCHDOWN_COLUMNS = ("rushing_tds", "receiving_tds", "special_teams_tds", "def_tds", "fumble_recovery_tds")
# A defensive fumble recovered in the end zone can plausibly be credited in BOTH `def_tds` and
# `fumble_recovery_tds` (one 2025 player-game shows both non-zero). Summing is right for "did he score at
# all"; for a 2+ touchdown contract it could double-count one play, so that case is refused rather than
# settled -- see settle._settle_player_stat.
DOUBLE_COUNT_RISK_COLUMNS = ("def_tds", "fumble_recovery_tds")
# Any of these being > 0 proves the player was on the field.
PARTICIPATION_STAT_COLUMNS = (
    "attempts", "completions", "passing_yards", "carries", "rushing_yards", "targets", "receptions",
    "receiving_yards", "passing_tds", "rushing_tds", "receiving_tds", "passing_interceptions",
    "def_tackles_solo", "def_sacks", "def_interceptions", "fg_att", "pat_att", "pt_att",
    "punt_returns", "kickoff_returns", "special_teams_tds", "def_tds", "fumble_recovery_tds",
)


def _num(v):
    """Blank-tolerant float. nflverse csv writes empty strings for unplayed games."""
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return None if isinstance(v, float) and math.isnan(v) else float(v)
    s = str(v).strip()
    if not s or s.upper() in ("NA", "NAN", "NONE"):
        return None
    try:
        return float(s)
    except ValueError:
        return None


@dataclass
class GameResult:
    """One finished (or unfinished) game, with the schedule row that proves it."""
    game_id: str
    season: int | None = None
    week: int | None = None
    game_type: str | None = None
    season_type: str | None = None
    home_team: str | None = None
    away_team: str | None = None
    home_score: float | None = None
    away_score: float | None = None
    overtime: int | None = None
    kickoff_utc: str | None = None
    status: str = NOT_FINAL
    source: str | None = None
    inconsistency: str | None = None
    # the postgame-only schedule fields, kept as read so a provisional row can be told from a finished one
    result_field: float | None = None
    total_field: float | None = None
    espn_game_id: str | None = None
    provisional_reason: str | None = None
    final_proofs: list = field(default_factory=list)
    final_contradictions: list = field(default_factory=list)

    @property
    def total_points(self):
        if self.home_score is None or self.away_score is None:
            return None
        return self.home_score + self.away_score

    @property
    def margin_home(self):
        if self.home_score is None or self.away_score is None:
            return None
        return self.home_score - self.away_score

    def team_points(self, team: str | None):
        if team is None:
            return None
        if team == self.home_team:
            return self.home_score
        if team == self.away_team:
            return self.away_score
        return None

    def margin_for(self, team: str | None):
        """Team score minus opponent score, or None when the team is not in this game."""
        if team is None or self.margin_home is None:
            return None
        if team == self.home_team:
            return self.margin_home
        if team == self.away_team:
            return -self.margin_home
        return None

    def evidence(self) -> dict:
        ev = {"game_id": self.game_id, "game_status": self.status, "home_team": self.home_team,
              "away_team": self.away_team, "home_score": self.home_score, "away_score": self.away_score,
              "total_points": self.total_points, "margin_home": self.margin_home,
              "overtime": self.overtime, "kickoff_utc": self.kickoff_utc, "source": self.source,
              "final_proofs": list(self.final_proofs)}
        if self.final_contradictions:
            ev["final_contradictions"] = list(self.final_contradictions)
        if self.provisional_reason:
            ev["provisional_reason"] = self.provisional_reason
        return ev


@dataclass
class PlayerGameResult:
    """One player's proven participation and recorded statistics in one game."""
    player_id: str
    game_id: str
    team: str | None = None
    position: str | None = None
    player_name: str | None = None
    offense_snaps: float | None = None
    defense_snaps: float | None = None
    st_snaps: float | None = None
    has_stats_row: bool = False
    has_snap_row: bool = False
    stats: dict = field(default_factory=dict)
    source: str | None = None

    @property
    def total_snaps(self):
        vals = [v for v in (self.offense_snaps, self.defense_snaps, self.st_snaps) if v is not None]
        return sum(vals) if vals else None

    @property
    def recorded_anything(self) -> bool:
        return any((self.stats.get(c) or 0) > 0 for c in PARTICIPATION_STAT_COLUMNS)

    @property
    def played(self):
        """Tri-state: True (a snap is proven), False (dressed and provably never on the field), None (unproven)."""
        if self.recorded_anything:
            return True
        snaps = self.total_snaps
        if snaps is not None and snaps >= 1:
            return True
        if self.has_snap_row and snaps == 0:
            return False           # PFR listed the player with zero snaps on every unit: active, never played
        return None

    def stat_value(self, stat: str):
        """Canonical stat name -> recorded value, or None when this game's evidence cannot produce it."""
        if stat == "touchdowns":
            vals = [self.stats.get(c) for c in TOUCHDOWN_COLUMNS]
            present = [v for v in vals if v is not None]
            return float(sum(present)) if present else None
        col = STAT_COLUMNS.get(stat)
        if col is None:
            return None
        v = self.stats.get(col)
        return None if v is None else float(v)

    def evidence(self, stat: str | None = None) -> dict:
        out = {"player_id": self.player_id, "game_id": self.game_id, "team": self.team,
               "offense_snaps": self.offense_snaps, "defense_snaps": self.defense_snaps,
               "st_snaps": self.st_snaps, "has_stats_row": self.has_stats_row,
               "has_snap_row": self.has_snap_row, "played": self.played, "source": self.source}
        if stat:
            out["stat"] = stat
            out["stat_value"] = self.stat_value(stat)
            out["stat_columns"] = list(TOUCHDOWN_COLUMNS) if stat == "touchdowns" else [STAT_COLUMNS.get(stat)]
        return out


class ResultBook:
    """Every proven result the settlement engine may consult, plus which tables were actually populated.

    `games_with_player_stats` / `games_with_snaps` are the completeness facts that make readiness decidable.
    A game absent from them is pending, never "the player recorded nothing".
    """

    def __init__(self, min_hours_after_kickoff: float = MIN_HOURS_AFTER_KICKOFF):
        self.games: dict[str, GameResult] = {}
        self.players: dict[tuple, PlayerGameResult] = {}
        self.games_with_player_stats: set = set()
        self.games_with_snaps: set = set()
        self.sources: dict = {}
        self.min_hours_after_kickoff = min_hours_after_kickoff
        # espn event id -> FinalAttestation. Optional corroboration: it can add a proof or expose a
        # contradiction, and its absence never blocks a game the postgame tables already attest.
        self.final_attestations: dict = {}

    # ---------------------------------------------------------------- loading
    def add_game(self, g: GameResult):
        self.games[g.game_id] = g

    def add_player(self, p: PlayerGameResult):
        key = (p.game_id, p.player_id)
        prev = self.players.get(key)
        if prev is not None:                       # merge a snap row into a stats row (or vice versa)
            p = _merge_player(prev, p)
        self.players[key] = p

    def player(self, game_id: str, player_id: str):
        return self.players.get((game_id, player_id))

    def add_final_attestations(self, attestations: dict):
        self.final_attestations.update(attestations or {})

    def final_verdict(self, game_id: str):
        """Is this game independently proven complete? Recomputed from the evidence, never cached as truth."""
        from nfl_edge.settlement.final_status import verify_final
        g = self.games.get(game_id)
        if g is None:
            return None
        in_tables = game_id in self.games_with_player_stats and game_id in self.games_with_snaps
        att = self.final_attestations.get(g.espn_game_id) if g.espn_game_id else None
        v = verify_final(g, in_postgame_tables=in_tables, attestation=att)
        g.final_proofs = list(v.proofs)
        g.final_contradictions = list(v.contradictions)
        return v

    # ---------------------------------------------------------------- readiness
    def readiness(self, game_id: str, *, needs_player_stats: bool, now=None) -> tuple[str, str]:
        """Is this game safe to write immutable evaluations for? Returns (state, human reason).

        Order matters: the cheapest and most damning checks first, so the reported reason is the real one.
        """
        g = self.games.get(game_id)
        if g is None:
            return DEFER_NOT_FINAL, f"{game_id} is not in the schedule"
        if g.inconsistency:
            return DEGRADED_INCONSISTENT, g.inconsistency
        if g.status != FINAL:
            return DEFER_NOT_FINAL, g.provisional_reason or f"{game_id} has no final score published"
        if now is not None and g.kickoff_utc:
            from datetime import datetime, timedelta
            try:
                ko = datetime.fromisoformat(g.kickoff_utc)
            except ValueError:
                ko = None
            if ko is not None and now < ko + timedelta(hours=self.min_hours_after_kickoff):
                return (DEFER_NOT_FINAL,
                        f"{game_id} has a score but kicked off less than {self.min_hours_after_kickoff}h ago")
        if needs_player_stats:
            if game_id not in self.games_with_player_stats:
                return DEFER_STATS_PENDING, f"player statistics for {game_id} have not been published yet"
            if game_id not in self.games_with_snaps:
                return DEFER_SNAPS_PENDING, f"snap counts for {game_id} have not been published yet"
        # Independent proof that the game is COMPLETE, not merely that a score exists. Last because it is the
        # check most likely to be satisfied by evidence the steps above already required.
        v = self.final_verdict(game_id)
        if v is not None and v.contradictions:
            return DEGRADED_INCONSISTENT, "; ".join(v.contradictions)
        if v is None or not v.proven:
            return (DEFER_FINAL_UNPROVEN,
                    f"{game_id} looks final but nothing independent attests that it is complete "
                    "(no postgame-only nflverse tables for it, and no ESPN completion)")
        return READY, f"final proven by {'+'.join(g.final_proofs)}, with every table this game's predictions need"


def _merge_player(a: PlayerGameResult, b: PlayerGameResult) -> PlayerGameResult:
    stats = dict(a.stats); stats.update({k: v for k, v in b.stats.items() if v is not None})
    return PlayerGameResult(
        player_id=a.player_id, game_id=a.game_id, team=a.team or b.team,
        position=a.position or b.position, player_name=a.player_name or b.player_name,
        offense_snaps=a.offense_snaps if a.offense_snaps is not None else b.offense_snaps,
        defense_snaps=a.defense_snaps if a.defense_snaps is not None else b.defense_snaps,
        st_snaps=a.st_snaps if a.st_snaps is not None else b.st_snaps,
        has_stats_row=a.has_stats_row or b.has_stats_row, has_snap_row=a.has_snap_row or b.has_snap_row,
        stats=stats, source="+".join(sorted({s for s in (a.source, b.source) if s})))


# ======================================================================================================
# schedule parsing (nflverse games.csv) -- the proof of a final score
# ======================================================================================================

def game_from_schedule_row(row: dict, source: str = "nflverse/schedules/games.csv") -> GameResult:
    """One games.csv row -> GameResult, distinguishing a FINISHED game from a row that merely has a score.

    nflverse publishes `result` (home - away), `total` and `overtime` when it processes a COMPLETED game. A row
    with scores but without them is provisional as far as this code is concerned, and is reported that way
    rather than settled: `status` stays NOT_FINAL with a `provisional_reason`.

    When those fields ARE present they are cross-checked against the scores. A contradiction in the source is
    exactly the case where guessing is worst, so it becomes `inconsistency` and blocks settlement.
    """
    hs, aws = _num(row.get("home_score")), _num(row.get("away_score"))
    res, tot = _num(row.get("result")), _num(row.get("total"))
    ot = _num(row.get("overtime"))
    ko = kickoff_utc((row.get("gameday") or "").strip(), (row.get("gametime") or "").strip())
    g = GameResult(
        game_id=(row.get("game_id") or "").strip(),
        season=int(_num(row.get("season"))) if _num(row.get("season")) is not None else None,
        week=int(_num(row.get("week"))) if _num(row.get("week")) is not None else None,
        game_type=(row.get("game_type") or "REG").strip().upper(),
        home_team=(row.get("home_team") or "").strip() or None,
        away_team=(row.get("away_team") or "").strip() or None,
        home_score=hs, away_score=aws,
        overtime=int(ot) if ot is not None else None,
        kickoff_utc=ko.isoformat() if ko else None,
        source=source, result_field=res, total_field=tot,
        espn_game_id=(str(row.get("espn")).strip() or None) if row.get("espn") not in (None, "") else None)
    g.season_type = season_type_of(g.game_type)
    if hs is None or aws is None:
        g.status = NOT_FINAL
        return g
    missing = [name for name, v in (("result", res), ("total", tot), ("overtime", ot)) if v is None]
    if missing:
        # A score with no postgame-only fields beside it is what a live or provisional row looks like. Elapsed
        # time cannot rescue it: settling from this row is exactly the failure this branch exists to prevent.
        g.status = NOT_FINAL
        g.provisional_reason = (
            f"scores are populated but the postgame-only field(s) {missing} are not, so this row is not proven "
            "to describe a completed game")
        return g
    if abs(res - (hs - aws)) > 1e-9:
        g.inconsistency = f"schedule result {res} != home {hs} - away {aws}"
    elif abs(tot - (hs + aws)) > 1e-9:
        g.inconsistency = f"schedule total {tot} != home {hs} + away {aws}"
    g.status = FINAL
    return g


def games_from_schedule_text(text: str, seasons=None, source: str = "nflverse/schedules/games.csv") -> list:
    out = []
    for row in csv.DictReader(io.StringIO(text)):
        s = _num(row.get("season"))
        if seasons is not None and (s is None or int(s) not in set(seasons)):
            continue
        g = game_from_schedule_row(row, source=source)
        if g.game_id:
            out.append(g)
    return out


def result_book_from_records(rec: dict, *, min_hours_after_kickoff: float | None = None) -> ResultBook:
    """Build a ResultBook from plain records: `schedule_csv` text plus `players` / `snaps` lists.

    Stdlib only, so the settlement path can be exercised -- in a test, or in a manual recovery -- without a
    parquet reader. The completeness sets are explicit (`games_with_player_stats`, `games_with_snaps`) because
    "which tables are populated" is a fact the caller must state rather than something inferred from how many
    rows happen to be present.
    """
    kwargs = {} if min_hours_after_kickoff is None else {"min_hours_after_kickoff": min_hours_after_kickoff}
    book = ResultBook(**kwargs)
    for g in games_from_schedule_text(rec.get("schedule_csv") or "", source=rec.get("source", {}).get(
            "schedules", "records")):
        book.add_game(g)
    for p in rec.get("players") or []:
        book.add_player(PlayerGameResult(
            player_id=p["player_id"], game_id=p.get("game_id") or rec.get("game_id") or "",
            team=p.get("team"), position=p.get("position"), player_name=p.get("player_name"),
            has_stats_row=p.get("has_stats_row", True), stats=dict(p.get("stats") or {}),
            source=p.get("source", "records")))
    for s in rec.get("snaps") or []:
        book.add_player(PlayerGameResult(
            player_id=s["player_id"], game_id=s.get("game_id") or rec.get("game_id") or "",
            team=s.get("team"), position=s.get("position"), player_name=s.get("player_name"),
            has_snap_row=True, offense_snaps=_num(s.get("offense_snaps")),
            defense_snaps=_num(s.get("defense_snaps")), st_snaps=_num(s.get("st_snaps")),
            source=s.get("source", "records")))
    book.games_with_player_stats |= set(rec.get("games_with_player_stats") or [])
    book.games_with_snaps |= set(rec.get("games_with_snaps") or [])
    book.sources.update(rec.get("source") or {})
    return book


def load_schedule_text(root: str, *, market_data: str | None = None, path: str | None = None,
                       allow_download: bool = False, timeout: int = 60) -> tuple[str, str]:
    """Raw games.csv TEXT plus the source it came from, most authoritative first.

    `nfl_calendar.load_schedule` parses the calendar fields and drops the scores, so settlement needs the text
    itself. The candidate order is shared with the calendar so the two never disagree about which copy of the
    schedule is authoritative. Raises rather than returning empty: a settlement run that cannot read the
    schedule must not conclude that no game is final.
    """
    tried = []
    for p in ([path] if path else schedule_candidates(root, market_data)):
        if p and os.path.exists(p):
            with open(p) as f:
                return f.read(), p
        tried.append(p)
    if allow_download:
        import urllib.request
        req = urllib.request.Request(SCHEDULE_URL, headers={"User-Agent": "nfl-edge-finder settlement"})
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode(), SCHEDULE_URL
    raise FileNotFoundError("no NFL schedule available; looked at " + ", ".join(str(t) for t in tried))
