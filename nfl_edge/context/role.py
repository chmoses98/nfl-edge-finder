"""ROLE CONTEXT: a point-in-time depth-chart book and a per-player role, with its certainty and provenance.

Why this exists
---------------
Every Week-2 2026 player record carried `depth_chart: UNKNOWN`. The context code was correct; the v2 projection
workflows simply never downloaded `depth_charts_<season>.parquet`, so the file was absent on every runner. Two
further defects sat behind that one and would have surfaced the moment the file arrived:

* the per-player rank map was keyed by gsis id and overwritten row by row, so a starting receiver who also
  returns kicks came back as `("KR", 1)` or `("PR", 2)` depending on row order -- a special-teams slot is not an
  offensive role;
* ESPN charts receivers in three columns (X / Z / slot) and a player can appear in several columns and in
  special-teams rows; the position-group order therefore has to be derived from the player's best offensive
  placement, not read off one row.

Point in time
-------------
Two nflverse formats exist and both are handled:

    2025-onward   one row per (dt, team, slot, rank), `dt` = the ESPN scrape instant (UTC). The chart used is the
                  newest `dt <= cutoff` for that team -- a timestamped observation, never a later one.
    <= 2024       one row per (season, week, club, position, depth_team): the weekly pregame chart. Used only for
                  historical research/training, where the week's chart is the pregame one.

Nothing here reads a post-cutoff row. A team with no chart at or before the cutoff is UNKNOWN with a reason.

Role certainty
--------------
`role_certainty` is HIGH / MEDIUM / LOW / UNKNOWN and is a statement about how much the ROLE is known, not about
how good a projection is. It is deliberately conservative:

    HIGH     a fresh chart (<= 8 days) places the player, his recent usage agrees with that placement, he has
             played for this team this season, and no adverse availability designation applies
    MEDIUM   the chart places him and usage does not contradict it, but evidence is thinner (no current-season
             game yet, a Questionable designation, or a chart older than 8 days)
    LOW      chart and usage disagree, the player changed teams, the chart is missing but usage exists, or a
             teammate ahead of him at his position is designated Out / Doubtful (a role that is about to change)
    UNKNOWN  neither a chart placement nor any usage history

Downstream, LOW and UNKNOWN are abstention reasons for a data projection (nfl_edge/engines/player/abstention.py).
"""
from __future__ import annotations

import os
from dataclasses import dataclass, field
from datetime import datetime, timezone

ROLE_VERSION = "role-context-1.0.0"
UNKNOWN = "UNKNOWN"
HIGH, MEDIUM, LOW = "HIGH", "MEDIUM", "LOW"
CERTAINTIES = (HIGH, MEDIUM, LOW, UNKNOWN)

OFFENSE_GROUP = {"QB": "QB", "RB": "RB", "HB": "RB", "FB": "FB", "WR": "WR", "TE": "TE"}
STALE_CHART_DAYS = 8.0
# usage thresholds that make a chart placement and the player's recent usage "agree"
STARTER_MIN_SNAP = 0.45            # a charted starter who took fewer recent snaps than this contradicts the chart
RESERVE_MAX_SNAP = 0.70            # a charted reserve who took more than this is playing a starter's role
ADVERSE_TEAMMATE = ("out", "doubtful")


def _dt(s):
    if s is None:
        return None
    if isinstance(s, datetime):
        return s if s.tzinfo else s.replace(tzinfo=timezone.utc)
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


@dataclass
class DepthEntry:
    gsis_id: str
    team: str
    group: str                 # QB / RB / FB / WR / TE
    slot_rank: int             # rank inside the chart slot (ESPN) or depth_team (legacy)
    group_rank: int            # derived order inside the position group: 1 = first QB / RB / WR / TE
    slot: int | None = None
    pos_abb: str | None = None
    name: str | None = None


@dataclass
class DepthChartBook:
    """The newest chart at or before `cutoff`, per team, offensive skill positions only."""
    cutoff: datetime | None
    entries: dict = field(default_factory=dict)          # gsis -> DepthEntry
    by_team: dict = field(default_factory=dict)          # team -> {group: [DepthEntry in group order]}
    vintage: dict = field(default_factory=dict)          # team -> chart instant (iso) or "<season>-W<week>"
    source: str | None = None
    reason: str | None = None

    # -------------------------------------------------------------------------------------------- building
    @classmethod
    def from_frame(cls, df, cutoff: datetime | None = None, *, season: int | None = None, week: int | None = None,
                   source: str | None = None) -> "DepthChartBook":
        """Build from either nflverse format (a polars or pandas frame)."""
        import polars as pl
        d = df if isinstance(df, pl.DataFrame) else pl.from_pandas(df)
        book = cls(cutoff=_dt(cutoff), source=source)
        if "dt" in d.columns:
            book._from_timestamped(d)
        elif "depth_team" in d.columns:
            book._from_weekly(d, season, week)
        else:
            book.reason = "unrecognised depth-chart schema"
        if not book.entries and not book.reason:
            book.reason = "no offensive depth-chart row at or before the cutoff"
        return book

    @classmethod
    def load(cls, root: str, season: int, cutoff: datetime | None, *, week: int | None = None) -> "DepthChartBook":
        p = os.path.join(root, "data", "raw", "nflverse", "depth_charts", f"depth_charts_{season}.parquet")
        if not os.path.exists(p):
            return cls(cutoff=_dt(cutoff), reason=f"depth chart file absent: {os.path.relpath(p, root)}")
        import polars as pl
        return cls.from_frame(pl.read_parquet(p), cutoff, season=season, week=week, source=os.path.relpath(p, root))

    def _from_timestamped(self, d):
        import polars as pl
        cut = self.cutoff
        d = d.filter(pl.col("pos_abb").is_in(list(OFFENSE_GROUP)) & pl.col("gsis_id").is_not_null() & pl.col("dt").is_not_null())
        if cut is not None:
            iso = cut.astimezone(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
            d = d.filter(pl.col("dt") <= iso)
        if not d.height:
            return
        latest = d.group_by("team").agg(pl.col("dt").max().alias("_latest"))
        d = d.join(latest, on="team").filter(pl.col("dt") == pl.col("_latest"))
        for team, sub in d.group_by("team"):
            team = team[0] if isinstance(team, tuple) else team
            self.vintage[team] = sub["dt"][0]
            rows = [{"gsis_id": r["gsis_id"], "group": OFFENSE_GROUP[r["pos_abb"]], "slot_rank": int(r["pos_rank"] or 99),
                     "slot": (int(r["pos_slot"]) if r.get("pos_slot") is not None else None), "pos_abb": r["pos_abb"],
                     "name": r.get("player_name")} for r in sub.iter_rows(named=True)]
            self._index_team(team, rows)

    def _from_weekly(self, d, season, week):
        import polars as pl
        d = d.filter(pl.col("gsis_id").is_not_null())
        pos_col = "depth_position" if "depth_position" in d.columns else "position"
        d = d.with_columns(pl.col(pos_col).alias("_pos")).filter(pl.col("_pos").is_in(list(OFFENSE_GROUP)))
        if "game_type" in d.columns:
            d = d.filter(pl.col("game_type") == "REG")
        if season is not None and "season" in d.columns:
            d = d.filter(pl.col("season") == season)
        if week is not None:
            d = d.filter(pl.col("week") == week)
        if not d.height:
            return
        if week is None:                       # newest week present
            d = d.filter(pl.col("week") == d["week"].max())
        for team, sub in d.group_by("club_code"):
            team = team[0] if isinstance(team, tuple) else team
            wk = int(sub["week"][0])
            self.vintage[team] = f"{int(sub['season'][0])}-W{wk:02d}"
            rows = [{"gsis_id": r["gsis_id"], "group": OFFENSE_GROUP[r["_pos"]], "slot_rank": int(r["depth_team"] or 99)
                     if str(r.get("depth_team") or "").isdigit() else 99, "slot": None, "pos_abb": r["_pos"],
                     "name": r.get("full_name")} for r in sub.iter_rows(named=True)]
            self._index_team(team, rows)

    def _index_team(self, team, rows):
        """One entry per player: his best (lowest-rank) OFFENSIVE placement; then a derived group order."""
        best = {}
        for r in rows:
            cur = best.get(r["gsis_id"])
            if cur is None or (r["slot_rank"], r["slot"] or 0) < (cur["slot_rank"], cur["slot"] or 0):
                best[r["gsis_id"]] = r
        groups = {}
        for r in best.values():
            groups.setdefault(r["group"], []).append(r)
        self.by_team[team] = {}
        for g, members in groups.items():
            # group order: every slot's rank-1 before any rank-2, ties by slot number (ESPN lists X, Z, slot)
            members.sort(key=lambda r: (r["slot_rank"], r["slot"] if r["slot"] is not None else 0, r["gsis_id"]))
            ordered = []
            for i, r in enumerate(members, start=1):
                e = DepthEntry(gsis_id=r["gsis_id"], team=team, group=g, slot_rank=r["slot_rank"], group_rank=i,
                               slot=r["slot"], pos_abb=r["pos_abb"], name=r["name"])
                ordered.append(e)
                self.entries[r["gsis_id"]] = e
            self.by_team[team][g] = ordered

    # -------------------------------------------------------------------------------------------- reading
    def entry(self, gsis_id: str | None) -> DepthEntry | None:
        return self.entries.get(gsis_id) if gsis_id else None

    def qb1(self, team: str | None) -> str | None:
        qbs = (self.by_team.get(team) or {}).get("QB") or []
        return qbs[0].gsis_id if qbs else None

    def chart_age_days(self, team: str | None) -> float | None:
        v = self.vintage.get(team)
        if not v or self.cutoff is None or "-W" in str(v):
            return None
        return (self.cutoff - _dt(v)).total_seconds() / 86400.0

    def ahead_of(self, gsis_id: str) -> list:
        """Players charted ahead of this one in his own position group."""
        e = self.entry(gsis_id)
        if e is None:
            return []
        return [x.gsis_id for x in (self.by_team.get(e.team) or {}).get(e.group, []) if x.group_rank < e.group_rank]


def starters_expected(group: str) -> int:
    return {"QB": 1, "RB": 1, "FB": 1, "WR": 3, "TE": 1}.get(group, 1)


def role_class(entry: DepthEntry | None, position: str | None, *, recent_snap_share=None) -> str:
    """A readable role label from the chart placement, refined by usage only where the chart cannot say."""
    if entry is None:
        return f"{position}_UNCHARTED" if position else UNKNOWN
    g, r = entry.group, entry.group_rank
    if g == "QB":
        return "QB1" if r == 1 else "QB_BACKUP"
    if g == "RB":
        if r == 1:
            return "RB1_COMMITTEE" if (recent_snap_share is not None and recent_snap_share < 0.50) else "RB1"
        return "RB2" if r == 2 else "RB_DEPTH"
    if g == "WR":
        # ESPN's receiver ranks run across the X / Z / slot columns (1..n for the whole group), so the first
        # three in group order are the starting three; the slot column is 8 in the 2025+ charts
        if r <= 3:
            return "WR_SLOT_STARTER" if entry.slot == 8 else f"WR{r}"
        return "WR_ROTATIONAL" if r <= 5 else "WR_DEPTH"
    if g == "TE":
        return "TE1" if r == 1 else ("TE2" if r == 2 else "TE_DEPTH")
    return f"{g}{r}"


def assess(book: DepthChartBook, *, gsis_id: str | None, team: str | None, position: str | None,
           recent_snap_share=None, n_current_season_games: int | None = None, last_team: str | None = None,
           availability_state: str | None = None, teammate_status: dict | None = None,
           observed_at: str | None = None) -> dict:
    """The structured role context for one player at the book's cutoff. Every field says where it came from.

    teammate_status: gsis -> report/availability status string for this week (for the 'role about to change'
    check). recent_snap_share: the player's snap share in his most recent game(s), or None.
    """
    e = book.entry(gsis_id)
    reasons = []
    age = book.chart_age_days(team) if team else None
    charted_team = e.team if e else None
    if e is None:
        reasons.append("not on the offensive depth chart at or before the cutoff" if book.entries
                       else (book.reason or "no depth chart at or before the cutoff"))
    if e is not None and team and charted_team != team:
        reasons.append(f"charted for {charted_team}, priced for {team}")
    has_usage = recent_snap_share is not None
    starter = bool(e and e.group_rank <= starters_expected(e.group))
    disagree = False
    if e is not None and has_usage:
        if starter and recent_snap_share < STARTER_MIN_SNAP:
            disagree = True; reasons.append(f"charted starter but recent snap share {recent_snap_share:.2f}")
        if not starter and recent_snap_share > RESERVE_MAX_SNAP:
            disagree = True; reasons.append(f"charted reserve but recent snap share {recent_snap_share:.2f}")
    changed_team = bool(last_team and team and last_team != team)
    if changed_team:
        reasons.append(f"last game for {last_team}, now {team}")
    blockers = []
    if e is not None and teammate_status:
        for other in book.ahead_of(gsis_id):
            st = (teammate_status.get(other) or "").lower()
            if any(a in st for a in ADVERSE_TEAMMATE):
                blockers.append(other)
        if blockers:
            reasons.append(f"{len(blockers)} teammate(s) ahead at {e.group} designated Out/Doubtful: role about to change")
    stale = age is not None and age > STALE_CHART_DAYS
    if stale:
        reasons.append(f"chart is {age:.1f} days old")
    adverse_self = (availability_state or "").upper() in ("QUESTIONABLE",)
    if e is None and not has_usage:
        cert = UNKNOWN
    elif e is None or disagree or changed_team or blockers or (charted_team and team and charted_team != team):
        cert = LOW
    elif stale or adverse_self or not n_current_season_games:
        cert = MEDIUM
        if not n_current_season_games:
            reasons.append("no current-season game for this team yet")
        if adverse_self:
            reasons.append("player designated Questionable")
    else:
        cert = HIGH
    return {"role_version": ROLE_VERSION, "team": team, "position": position,
            "depth_chart_state": ("LISTED" if e else UNKNOWN), "depth_group": (e.group if e else None),
            "depth_group_rank": (e.group_rank if e else None), "depth_slot_rank": (e.slot_rank if e else None),
            "depth_slot": (e.slot if e else None), "depth_chart_vintage": book.vintage.get(charted_team or team),
            "depth_chart_age_days": (round(age, 2) if age is not None else None), "depth_chart_source": book.source,
            "role_class": role_class(e, position, recent_snap_share=recent_snap_share), "role_certainty": cert,
            "role_reasons": reasons, "recent_snap_share": recent_snap_share, "n_current_season_games": n_current_season_games,
            "role_change_pending": bool(blockers), "blocking_teammates": blockers[:4],
            "observed_at": observed_at or (book.cutoff.isoformat() if book.cutoff else None)}
