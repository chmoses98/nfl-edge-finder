"""Structured information shocks, and when they became public.

The research question is no longer whether we can project football better than Kalshi (session 2 settled
that: we cannot). It is whether the market takes measurable time to absorb information that arrives at a
known instant. That requires knowing WHEN a fact became public, which is a data problem before it is a
statistics problem.

**What is and is not timestamped.** nflverse `injuries` carries no timestamp at all -- one row per
player-week with the final designation. So a 2025 injury-report shock cannot be located in time from the data
itself. What *is* exactly timed is the league's own publication calendar, which is fixed, public and
auditable:

  * final game-status report (Out / Doubtful / Questionable): Friday afternoon for a Sunday game
  * **inactives: exactly 90 minutes before kickoff, by rule**

The second is precise to the minute and the horizon grid has T-90m, T-30m and T-0 around it. That makes the
inactive release the one retrospective shock in 2025 whose timing is known rather than assumed, and it is the
basis of the latency work. Shocks whose timing rests on the weekly calendar are labelled `calendar_inferred`
and are never mixed with it.

For 2026 the live capture stream gives real observation timestamps (ESPN / Sleeper state diffs at a 10-minute
cadence), and `ShockLog.from_capture_diff` is the path that will use them.
"""
from __future__ import annotations

import hashlib
import json
import os
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone

import polars as pl

# how the shock's timestamp was established -- never silently mixed
TIMING_EXACT = "exact"                    # observed at a known instant (capture diff, or a by-rule release)
TIMING_CALENDAR = "calendar_inferred"     # inferred from the league's fixed publication calendar
TIMING_UNKNOWN = "unknown"                # the fact is known, the moment is not; unusable for latency


@dataclass
class Shock:
    shock_id: str
    observed_at: str | None            # ISO timestamp, or None when timing is unknown
    timing_basis: str                  # TIMING_EXACT | TIMING_CALENDAR | TIMING_UNKNOWN
    source: str
    shock_type: str
    entity_id: str                     # gsis id, or team abbreviation for team-level shocks
    entity_name: str | None
    entity_position: str | None
    prior_state: str | None
    new_state: str
    game_id: str
    team: str
    affected_players: list = field(default_factory=list)   # teammates plausibly reallocated to
    data_confidence: str = "medium"
    related_market_families: list = field(default_factory=list)
    notes: str = ""

    def to_dict(self):
        return asdict(self)


def _sid(*parts):
    return "shk_" + hashlib.sha1("|".join(str(p) for p in parts).encode()).hexdigest()[:16]


class ShockLog:
    """Append-only collection of shocks with a stable id per (game, entity, transition)."""

    def __init__(self):
        self._by_id: dict[str, Shock] = {}

    def add(self, shock: Shock) -> bool:
        if shock.shock_id in self._by_id:
            return False
        self._by_id[shock.shock_id] = shock
        return True

    def __len__(self):
        return len(self._by_id)

    def shocks(self):
        return list(self._by_id.values())

    def to_frame(self) -> pl.DataFrame:
        rows = [s.to_dict() for s in self._by_id.values()]
        for r in rows:
            r["affected_players"] = ";".join(r["affected_players"])
            r["related_market_families"] = ";".join(r["related_market_families"])
        return pl.DataFrame(rows) if rows else pl.DataFrame()

    def write(self, path):
        os.makedirs(os.path.dirname(path), exist_ok=True)
        f = self.to_frame()
        if f.height:
            f.write_parquet(path)
        return f.height


SKILL = ("QB", "RB", "WR", "TE")


def detect_2025_availability_shocks(root: str, season: int = 2025) -> ShockLog:
    """Derive availability shocks for a settled season from rosters, injury reports and snap counts.

    Two kinds, kept strictly apart:

      `ruled_out_on_report`  -- designated Out on the weekly report. Public by the Friday final report, so
                                its timing is `calendar_inferred` and it is NOT used for latency.
      `surprise_inactive`    -- NOT designated Out, yet took no offensive snap and did not appear in the game.
                                For a player the market was still quoting, that fact becomes public at the
                                inactive release, exactly 90 minutes before kickoff. Timing `exact`.

    The surprise group is the identified natural experiment: a precisely-timed public information release.
    """
    log = ShockLog()
    inj = pl.read_parquet(os.path.join(root, f"data/raw/nflverse/injuries/injuries_{season}.parquet"))
    rost = pl.read_parquet(os.path.join(root, f"data/raw/nflverse/weekly_rosters/roster_weekly_{season}.parquet"))
    games = pl.read_parquet(os.path.join(root, "data/silver/games.parquet")).filter(pl.col("season") == season)
    stats = pl.read_parquet(os.path.join(root, "research/player_distributions/research_table.parquet")) \
        .filter(pl.col("season") == season)

    # the weekly roster carries an explicit INA (inactive) status -- a direct observation, not an inference
    rost = rost.filter(pl.col("position").is_in(SKILL) & (pl.col("gsis_id").is_not_null())
                       & (pl.col("gsis_id") != ""))
    inj_key = {}
    for r in inj.iter_rows(named=True):
        if r.get("gsis_id"):
            inj_key[(int(r["week"]), r["team"], r["gsis_id"])] = r.get("report_status")

    # who actually played, per (game, team) -- the reallocation beneficiaries
    played = {}
    for r in stats.select(["game_id", "team", "player_id", "position", "offense_snaps"]).iter_rows(named=True):
        if (r.get("offense_snaps") or 0) > 0:
            played.setdefault((r["game_id"], r["team"]), []).append(r)

    gidx = {}
    for r in games.iter_rows(named=True):
        gidx[(int(r["week"]), r["home_team"])] = r["game_id"]
        gidx[(int(r["week"]), r["away_team"])] = r["game_id"]

    n_out = n_surprise = 0
    for r in rost.iter_rows(named=True):
        if r.get("status") != "INA":
            continue
        week, team, pid = int(r["week"]), r["team"], r["gsis_id"]
        gid = gidx.get((week, team))
        if not gid:
            continue
        status = inj_key.get((week, team, pid))
        mates = played.get((gid, team), [])
        others = [q["player_id"] for q in mates if q["position"] == r["position"]]
        all_mates = [q["player_id"] for q in mates]
        if status == "Out":
            log.add(Shock(shock_id=_sid(gid, pid, "out"), observed_at=None,
                          timing_basis=TIMING_CALENDAR, source="nflverse_injuries+weekly_roster",
                          shock_type="ruled_out_on_report", entity_id=pid, entity_name=r.get("full_name"),
                          entity_position=r["position"], prior_state="on_report", new_state="inactive",
                          game_id=gid, team=team, affected_players=others, data_confidence="high",
                          related_market_families=["PLAYER_STAT", "FIRST_TD_SCORER"],
                          notes="designated Out and inactive; public by the Friday final report, so the "
                                "moment it became known is not observable in the data"))
            n_out += 1
        else:
            log.add(Shock(shock_id=_sid(gid, pid, "surprise"), observed_at=None,
                          timing_basis=TIMING_EXACT, source="nflverse_weekly_roster+injuries",
                          shock_type="surprise_inactive", entity_id=pid, entity_name=r.get("full_name"),
                          entity_position=r["position"], prior_state=status or "not_on_report",
                          new_state="inactive", game_id=gid, team=team, affected_players=others,
                          data_confidence="medium", related_market_families=["PLAYER_STAT", "FIRST_TD_SCORER"],
                          notes="inactive WITHOUT an Out designation; becomes public at the inactive "
                                "release, exactly 90 minutes before kickoff"))
            n_surprise += 1
    return log
