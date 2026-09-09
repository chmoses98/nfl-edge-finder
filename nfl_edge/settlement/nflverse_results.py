"""Build a `ResultBook` from the free nflverse bronze files. No paid source, no scraping.

Three releases carry everything postgame settlement needs:

    schedules/games.csv                final scores, overtime flag, kickoff (US-Eastern -> UTC)
    stats_player/stats_player_week_S   every recorded statistic, per player-game
    snap_counts/snap_counts_S          offence / defence / special-teams snaps, per player-game (PFR)

Only the settlement columns are read, and they are read UNCHANGED -- no imputation, no filling, no rounding.
A column absent from a release stays absent, which the engine turns into a refusal rather than a zero.

IDENTITY. The ledger's canonical player key is the nflverse GSIS id, resolved at PRICING time. Player stats
are keyed by GSIS already. Snap counts are keyed by PFR id, so a crosswalk is needed: the silver
`player_crosswalk.parquet` is preferred when the repo has built one, and `players.parquet` (which carries both
`gsis_id` and `pfr_id`) is the fallback so a settlement run needs no silver build at all.

This module is the only place in the settlement path that imports a third-party library. Everything that
decides a payout is stdlib, so no dependency problem can be the reason a settlement was wrong.
"""
from __future__ import annotations

import os

import polars as pl

from nfl_edge.settlement.results import (
    PARTICIPATION_STAT_COLUMNS, PlayerGameResult, ResultBook, STAT_COLUMNS, TOUCHDOWN_COLUMNS,
    games_from_schedule_text,
)

# Columns read from stats_player_week. Everything the engine may need to prove a value or a snap.
STATS_COLUMNS = sorted(set(STAT_COLUMNS.values()) | set(TOUCHDOWN_COLUMNS) | set(PARTICIPATION_STAT_COLUMNS))
IDENT_COLUMNS = ["player_id", "player_display_name", "position", "season", "week", "game_id", "team"]


def schedule_path(root: str) -> str:
    return os.path.join(root, "data", "raw", "nflverse", "schedules", "games.csv")


def stats_path(root: str, season: int) -> str:
    return os.path.join(root, "data", "raw", "nflverse", "stats_player", f"stats_player_week_{season}.parquet")


def snaps_path(root: str, season: int) -> str:
    return os.path.join(root, "data", "raw", "nflverse", "snap_counts", f"snap_counts_{season}.parquet")


def pfr_to_gsis(root: str) -> tuple[dict, str]:
    """PFR player id -> GSIS id, with the file that provided it."""
    xw = os.path.join(root, "data", "silver", "player_crosswalk.parquet")
    if os.path.exists(xw):
        df = pl.read_parquet(xw).select(["gsis_id", "pfr_id"]).drop_nulls().unique(subset=["pfr_id"], keep="first")
        return dict(zip(df["pfr_id"].to_list(), df["gsis_id"].to_list())), "silver/player_crosswalk.parquet"
    players = os.path.join(root, "data", "raw", "nflverse", "players", "players.parquet")
    if os.path.exists(players):
        df = pl.read_parquet(players)
        cols = df.collect_schema().names()
        pfr = "pfr_id" if "pfr_id" in cols else ("pfr" if "pfr" in cols else None)
        if pfr:
            df = df.select(["gsis_id", pfr]).drop_nulls().unique(subset=[pfr], keep="first")
            return dict(zip(df[pfr].to_list(), df["gsis_id"].to_list())), "nflverse/players/players.parquet"
    return {}, "none"


def build_result_book(root: str, seasons, *, min_hours_after_kickoff: float | None = None,
                      schedule_text: str | None = None) -> ResultBook:
    """Assemble every proven result for `seasons`. Missing per-season files are recorded, never faked."""
    kwargs = {} if min_hours_after_kickoff is None else {"min_hours_after_kickoff": min_hours_after_kickoff}
    book = ResultBook(**kwargs)
    seasons = sorted({int(s) for s in seasons})

    if schedule_text is None:
        p = schedule_path(root)
        if not os.path.exists(p):
            raise FileNotFoundError(f"no nflverse schedule at {p}; settlement cannot prove a final score")
        with open(p) as f:
            schedule_text = f.read()
        book.sources["schedules"] = os.path.relpath(p, root)
    else:
        book.sources["schedules"] = "provided"
    for g in games_from_schedule_text(schedule_text, seasons=seasons):
        book.add_game(g)

    xmap, xsrc = pfr_to_gsis(root)
    book.sources["pfr_crosswalk"] = xsrc

    for season in seasons:
        sp = stats_path(root, season)
        if os.path.exists(sp):
            _load_stats(book, sp, os.path.relpath(sp, root))
        else:
            book.sources.setdefault("missing", []).append(os.path.relpath(sp, root))
        cp = snaps_path(root, season)
        if os.path.exists(cp):
            _load_snaps(book, cp, xmap, os.path.relpath(cp, root))
        else:
            book.sources.setdefault("missing", []).append(os.path.relpath(cp, root))
    return book


def _load_stats(book: ResultBook, path: str, source: str):
    lf = pl.scan_parquet(path)
    have = set(lf.collect_schema().names())
    cols = [c for c in IDENT_COLUMNS if c in have] + [c for c in STATS_COLUMNS if c in have]
    df = lf.select(cols).collect()
    for r in df.iter_rows(named=True):
        gid, pid = r.get("game_id"), r.get("player_id")
        if not gid or not pid:
            continue
        book.games_with_player_stats.add(gid)
        book.add_player(PlayerGameResult(
            player_id=pid, game_id=gid, team=r.get("team"), position=r.get("position"),
            player_name=r.get("player_display_name"), has_stats_row=True,
            stats={c: (None if r.get(c) is None else float(r[c])) for c in STATS_COLUMNS if c in have},
            source=source))


def _load_snaps(book: ResultBook, path: str, xmap: dict, source: str):
    lf = pl.scan_parquet(path)
    have = set(lf.collect_schema().names())
    cols = [c for c in ("game_id", "pfr_player_id", "player", "position", "team",
                        "offense_snaps", "defense_snaps", "st_snaps") if c in have]
    df = lf.select(cols).collect()
    for r in df.iter_rows(named=True):
        gid = r.get("game_id")
        if not gid:
            continue
        book.games_with_snaps.add(gid)
        pid = xmap.get(r.get("pfr_player_id"))
        if not pid:
            continue                      # unresolved PFR id: the settlement engine will refuse on identity
        book.add_player(PlayerGameResult(
            player_id=pid, game_id=gid, team=r.get("team"), position=r.get("position"),
            player_name=r.get("player"), has_snap_row=True,
            offense_snaps=_f(r.get("offense_snaps")), defense_snaps=_f(r.get("defense_snaps")),
            st_snaps=_f(r.get("st_snaps")), source=source))


def _f(v):
    return None if v is None else float(v)
