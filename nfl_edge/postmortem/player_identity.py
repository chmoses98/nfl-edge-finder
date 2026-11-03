"""VERIFIED player identity and position for the quarterback gate. Unknown or conflicting -> UNVERIFIED -> the gate fails CLOSED.

WHY
The first QB-dependency table (qb_dependency.py) classified a rushing prop NOT_GATED because a running back's rushing volume does not
depend on who throws, and recorded one residual gap: "a QUARTERBACK's rushing prop looks like a running-back rushing prop in a ticker".
A ticker does not carry a position, so the family could not tell a QB's rushing / receiving / scrambling prop from an RB's, and a QB
whose starter was unconfirmed (or who was the backup) could be bet. This module closes the gap by resolving WHO the player in a market is,
from the repository's own player data, and what POSITION he plays, with provenance:

    nflverse players table       data/raw/nflverse/players/players.parquet          gsis_id, position, latest_team, display_name
    nflverse weekly rosters      data/raw/nflverse/weekly_rosters/roster_weekly_<season>.parquet   gsis_id, team, position, week
    ff_playerids (dynastyprocess) data/raw/nflverse/ff_playerids/db_playerids.csv    gsis_id, position, team, name

(the same files scripts/data/nflverse_download.py fetches and nfl_edge/arms/player_anatomy.py reads). The market's player id is the GSIS id
the packet carries (resolved by the Kalshi->GSIS player map; an unresolved id is already blocked by the identity gate).

WHAT "VERIFIED" MEANS (every condition; any miss -> UNVERIFIED with a stable reason code)
* the market carries a GSIS player id, and an identity source was supplied (``NO_IDENTITY_SOURCE`` otherwise);
* the id is in at least one source, and at least one source gives a recognised position (``PLAYER_NOT_IN_IDENTITY_SOURCE`` / ``POSITION_UNKNOWN``);
* the sources AGREE on whether he is a quarterback (``POSITION_CONFLICT``): a player one table calls QB and another calls RB is not verified;
* his team is read from the latest weekly-roster row at or before the game's week (point in time; a later week is never used), else from the
  players table and ff_playerids, which must then agree (``TEAM_UNKNOWN`` / ``TEAM_CONFLICT``);
* that team is one of the game's two teams (``TEAM_NOT_IN_GAME``) and equals the team the ticker's subject segment names when it names one
  (``TEAM_MISMATCH_WITH_TICKER``): a stale table that has a traded player on his old team can never verify him.

PROVENANCE: every verified or unverified result carries the sources it used (file, sha256, row count, season, the roster week actually used,
and whether the file itself is dated: the nflverse players table and ff_playerids are undated snapshots, so ``snapshot_dated`` is False and
the ``as_of`` is the DECISION time the verification was done at, never a claimed publication time).

Pure functions apart from ``load_book`` (reads files); no clock; nothing here supplies a missing fact.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime

from .common import parse_ts

SCHEMA = "nfl-player-identity.v1"
IDENTITY_VERSION = "nfl-player-identity-2026-11-03.1"
#: A verified identity older than this at the time a gate judges it is refused (owner-adjustable; only ever blocks).
MAX_AGE_AT_DECISION_MIN = 24 * 60.0

SRC_PLAYERS = "NFLVERSE_PLAYERS"
SRC_ROSTER = "NFLVERSE_WEEKLY_ROSTER"
SRC_FFIDS = "FF_PLAYERIDS"
SOURCES = (SRC_PLAYERS, SRC_ROSTER, SRC_FFIDS)

QB = "QB"
_GROUPS = {
    "QB": "QB",
    "RB": "RB", "FB": "RB", "HB": "RB",
    "WR": "WR", "TE": "TE",
    "K": "K", "PK": "K", "P": "P", "LS": "LS",
    "DE": "DEF", "DT": "DEF", "NT": "DEF", "DL": "DEF", "EDGE": "DEF", "LB": "DEF", "ILB": "DEF", "OLB": "DEF", "MLB": "DEF",
    "DB": "DEF", "CB": "DEF", "S": "DEF", "SS": "DEF", "FS": "DEF", "SAF": "DEF",
    "OL": "OL", "T": "OL", "G": "OL", "C": "OL", "OT": "OL", "OG": "OL",
}
_TEAM_ALIAS = {"LAR": "LA", "JAC": "JAX", "WSH": "WAS"}

# reason codes (stable strings; the gate prefixes them PLAYER_IDENTITY_UNVERIFIED:)
R_NO_PLAYER_ID = "NO_PLAYER_ID"
R_NO_SOURCE = "NO_IDENTITY_SOURCE"
R_NOT_IN_SOURCE = "PLAYER_NOT_IN_IDENTITY_SOURCE"
R_POSITION_UNKNOWN = "POSITION_UNKNOWN"
R_POSITION_CONFLICT = "POSITION_CONFLICT"
R_TEAM_UNKNOWN = "TEAM_UNKNOWN"
R_TEAM_CONFLICT = "TEAM_CONFLICT"
R_TEAM_NOT_IN_GAME = "TEAM_NOT_IN_GAME"
R_TEAM_MISMATCH_TICKER = "TEAM_MISMATCH_WITH_TICKER"
R_NO_TEAMS = "GAME_TEAMS_UNKNOWN"
R_MALFORMED = "IDENTITY_MALFORMED"
R_NO_PROVENANCE = "IDENTITY_WITHOUT_PROVENANCE"
R_AFTER_DECISION = "IDENTITY_AFTER_DECISION"
R_STALE = "IDENTITY_STALE"
R_NO_CLOCK = "IDENTITY_CLOCK_MISSING"


def position_group(pos) -> str | None:
    """Normalised position group, or None for blank / unrecognised (never guessed)."""
    if not isinstance(pos, str) or not pos.strip():
        return None
    return _GROUPS.get(pos.strip().upper())


def norm_team(t) -> str | None:
    if not isinstance(t, str) or not t.strip():
        return None
    t = t.strip().upper()
    return _TEAM_ALIAS.get(t, t)


# ----------------------------------------------------------------------------------------------------------------------------- the book
class IdentityBook:
    """Observations per GSIS id, each tagged with the source that gave it, plus the provenance of every source loaded."""

    def __init__(self):
        self.obs: dict = {}          # gsis -> [ {source, position, team, week, name} ]
        self.sources: list = []      # [ {source, file, sha256, rows, season, snapshot_dated, max_week} ]
        self.errors: list = []

    def __bool__(self):
        return bool(self.obs)

    def add_source(self, source: str, rows, *, file: str, sha256: str, season=None, snapshot_dated: bool = False) -> int:
        n, mw = 0, None
        for r in rows or []:
            g = r.get("gsis_id")
            if not isinstance(g, str) or not g.strip():
                continue
            wk = r.get("week")
            try:
                wk = None if wk is None else int(wk)
            except (TypeError, ValueError):
                wk = None
            self.obs.setdefault(g.strip(), []).append({"source": source, "position": r.get("position"), "team": r.get("team"), "week": wk,
                                                       "name": r.get("name")})
            n += 1
            if wk is not None:
                mw = wk if mw is None else max(mw, wk)
        self.sources.append({"source": source, "file": file, "sha256": sha256, "rows": n, "season": season,
                             "snapshot_dated": snapshot_dated, "max_week": mw})
        return n

    def summary(self) -> dict:
        return {"schema": SCHEMA, "version": IDENTITY_VERSION, "players": len(self.obs), "sources": list(self.sources), "errors": list(self.errors)}


def _rows_sha(rows) -> str:
    return hashlib.sha256(json.dumps(rows, sort_keys=True, default=str).encode()).hexdigest()


def book_from_rows(*, players=None, rosters=None, ffids=None, season=None) -> IdentityBook:
    """Build a book from in-memory rows (tests, or a caller that already read the tables). ``players`` rows: gsis_id, position, latest_team,
    display_name; ``rosters``: gsis_id, team, position, week; ``ffids``: gsis_id, position, team, name. File = ``<inline>``."""
    b = IdentityBook()
    if players is not None:
        b.add_source(SRC_PLAYERS, [{"gsis_id": r.get("gsis_id"), "position": r.get("position"), "team": r.get("latest_team"),
                                    "name": r.get("display_name")} for r in players], file="<inline>", sha256=_rows_sha(players), season=season)
    if rosters is not None:
        b.add_source(SRC_ROSTER, [{"gsis_id": r.get("gsis_id"), "position": r.get("position"), "team": r.get("team"), "week": r.get("week"),
                                   "name": r.get("full_name")} for r in rosters], file="<inline>", sha256=_rows_sha(rosters), season=season)
    if ffids is not None:
        b.add_source(SRC_FFIDS, [{"gsis_id": r.get("gsis_id"), "position": r.get("position"), "team": r.get("team"), "name": r.get("name")}
                                 for r in ffids], file="<inline>", sha256=_rows_sha(ffids), season=season)
    return b


def _file_sha(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def load_book(raw_root: str | None, season: int | None) -> IdentityBook:
    """Read whichever of the three tables exist under ``raw_root`` (data/raw/nflverse). A missing or unreadable table is recorded in
    ``errors`` and contributes nothing: an empty book verifies nobody (fail closed); it never raises into the card."""
    b = IdentityBook()
    if not raw_root or not os.path.isdir(raw_root):
        b.errors.append("NO_RAW_ROOT")
        return b
    try:
        import polars as pl
    except ImportError:                                        # pragma: no cover - polars is a test/runtime dependency
        b.errors.append("POLARS_UNAVAILABLE")
        return b
    specs = (
        (SRC_PLAYERS, os.path.join("players", "players.parquet"), "parquet"),
        (SRC_ROSTER, os.path.join("weekly_rosters", f"roster_weekly_{season}.parquet"), "parquet"),
        (SRC_FFIDS, os.path.join("ff_playerids", "db_playerids.csv"), "csv"),
    )
    for src, rel, kind in specs:
        path = os.path.join(raw_root, rel)
        if not os.path.isfile(path):
            b.errors.append(f"{src}:MISSING:{rel}")
            continue
        try:
            df = pl.read_parquet(path) if kind == "parquet" else pl.read_csv(path, infer_schema_length=0)
            cols = set(df.columns)
            rows = df.to_dicts()
            if src == SRC_PLAYERS:
                need = {"gsis_id", "position"}
                mapped = lambda r: {"gsis_id": r.get("gsis_id"), "position": r.get("position"), "team": r.get("latest_team"),  # noqa: E731
                                    "name": r.get("display_name")}
            elif src == SRC_ROSTER:
                need = {"gsis_id", "position", "team", "week"}
                mapped = lambda r: {"gsis_id": r.get("gsis_id"), "position": r.get("position"), "team": r.get("team"),  # noqa: E731
                                    "week": r.get("week"), "name": r.get("full_name")}
            else:
                need = {"gsis_id", "position", "team"}
                mapped = lambda r: {"gsis_id": r.get("gsis_id"), "position": r.get("position"), "team": r.get("team"),  # noqa: E731
                                    "name": r.get("name")}
            if not need <= cols:
                b.errors.append(f"{src}:MISSING_COLUMNS:{','.join(sorted(need - cols))}")
                continue
            b.add_source(src, [mapped(r) for r in rows], file=rel, sha256=_file_sha(path), season=season if src == SRC_ROSTER else None)
        except Exception as exc:                               # a corrupt table must not take the card down; it simply verifies nobody
            b.errors.append(f"{src}:UNREADABLE:{type(exc).__name__}")
    return b


# ----------------------------------------------------------------------------------------------------------------------------- verify
def _unverified(reason: str, *, player_id=None, as_of=None, week=None, detail=None, sources=None) -> dict:
    out = {"schema": SCHEMA, "version": IDENTITY_VERSION, "verified": False, "reason": reason, "gsis_id": player_id, "position": None,
           "position_group": None, "is_qb": None, "team": None, "game_week": week,
           "as_of": as_of.isoformat() if isinstance(as_of, datetime) else None, "sources": sources or []}
    if detail:
        out["detail"] = detail
    return out


def verify(book: IdentityBook | None, *, player_id, game_teams, game_week, ticker_team=None, as_of) -> dict:
    """Resolve one market's player to (identity, position, team) with provenance, or UNVERIFIED with a reason. ``game_teams`` is the game's
    [home, away] (nflverse codes); ``ticker_team`` the team the ticker's subject names when it can be read (else None); ``as_of`` the decision time."""
    dec = parse_ts(as_of)
    pid = player_id.strip() if isinstance(player_id, str) and player_id.strip() else None
    wk = None
    try:
        wk = None if game_week is None else int(game_week)
    except (TypeError, ValueError):
        wk = None
    if pid is None:
        return _unverified(R_NO_PLAYER_ID, as_of=dec, week=wk)
    if book is None or not book:
        return _unverified(R_NO_SOURCE, player_id=pid, as_of=dec, week=wk,
                           detail=list(book.errors) if book is not None else None)
    obs = book.obs.get(pid)
    if not obs:
        return _unverified(R_NOT_IN_SOURCE, player_id=pid, as_of=dec, week=wk)
    teams = [norm_team(t) for t in (game_teams or []) if norm_team(t)]
    if len(teams) != 2:
        return _unverified(R_NO_TEAMS, player_id=pid, as_of=dec, week=wk)
    by_src = {s["source"]: s for s in book.sources}

    def prov(used):
        return [{k: by_src[s].get(k) for k in ("source", "file", "sha256", "rows", "season", "snapshot_dated", "max_week")} | {
            "observation": o} for s, o in used if s in by_src]

    # roster rows are point in time: the latest week at or before the game's week; players / ff rows are undated snapshots
    roster = [o for o in obs if o["source"] == SRC_ROSTER and o["week"] is not None and (wk is None or o["week"] <= wk)]
    roster_obs = max(roster, key=lambda o: o["week"]) if roster else None
    snaps = [o for o in obs if o["source"] in (SRC_PLAYERS, SRC_FFIDS)]
    used = ([roster_obs] if roster_obs else []) + snaps
    used_prov = prov([(o["source"], o) for o in used])
    # --- position: at least one recognised group; sources must agree on QB-ness
    groups = [(o, position_group(o["position"])) for o in used]
    known = [(o, g) for o, g in groups if g is not None]
    if not known:
        return _unverified(R_POSITION_UNKNOWN, player_id=pid, as_of=dec, week=wk, sources=used_prov)
    if len({g == QB for _, g in known}) > 1:
        return _unverified(R_POSITION_CONFLICT, player_id=pid, as_of=dec, week=wk, sources=used_prov,
                           detail=sorted(f"{o['source']}={o['position']}" for o, _ in known))
    # a source that names a position we do not recognise could be hiding a QB: it does not verify, it vetoes
    if any(g is None and isinstance(o["position"], str) and o["position"].strip() for o, g in groups):
        return _unverified(R_POSITION_UNKNOWN, player_id=pid, as_of=dec, week=wk, sources=used_prov,
                           detail="an unrecognised position string in " + ",".join(sorted({o["source"] for o, g in groups if g is None})))
    primary_obs, primary_group = next(((o, g) for o, g in known if o["source"] == SRC_ROSTER), known[0])
    # --- team
    if roster_obs is not None and norm_team(roster_obs["team"]):
        team = norm_team(roster_obs["team"])
    else:
        cand = {norm_team(o["team"]) for o in snaps if norm_team(o["team"])}
        if not cand:
            return _unverified(R_TEAM_UNKNOWN, player_id=pid, as_of=dec, week=wk, sources=used_prov)
        if len(cand) > 1:
            return _unverified(R_TEAM_CONFLICT, player_id=pid, as_of=dec, week=wk, sources=used_prov, detail=sorted(cand))
        team = next(iter(cand))
    if team not in teams:
        return _unverified(R_TEAM_NOT_IN_GAME, player_id=pid, as_of=dec, week=wk, sources=used_prov, detail=team)
    if ticker_team is not None and norm_team(ticker_team) != team:
        return _unverified(R_TEAM_MISMATCH_TICKER, player_id=pid, as_of=dec, week=wk, sources=used_prov, detail=f"table={team} ticker={norm_team(ticker_team)}")
    name = next((o["name"] for o in used if o.get("name")), None)
    return {"schema": SCHEMA, "version": IDENTITY_VERSION, "verified": True, "reason": None, "gsis_id": pid, "name": name,
            "position": primary_obs["position"], "position_group": primary_group, "is_qb": primary_group == QB, "team": team, "game_week": wk,
            "as_of": dec.isoformat() if dec else None, "sources": used_prov}


def accept(identity, *, teams, decision_time, max_age_min: float = MAX_AGE_AT_DECISION_MIN) -> tuple[bool, str | None, dict | None]:
    """Re-judge an identity block the gate was handed (it may have travelled through a record). (ok, reason, normalised). A block that says
    ``verified`` but lacks provenance, a recognised position, a team in this game, or a clock at/before the decision is NOT accepted."""
    if not isinstance(identity, dict):
        return False, R_NO_SOURCE, None
    if identity.get("verified") is not True:
        return False, identity.get("reason") or R_NO_SOURCE, None
    pid, grp, team = identity.get("gsis_id"), identity.get("position_group"), norm_team(identity.get("team"))
    if not (isinstance(pid, str) and pid.strip()) or grp not in set(_GROUPS.values()) or team is None or identity.get("schema") != SCHEMA:
        return False, R_MALFORMED, None
    if not identity.get("sources") or not all(isinstance(s, dict) and s.get("source") in SOURCES and s.get("sha256") for s in identity["sources"]):
        return False, R_NO_PROVENANCE, None
    if identity.get("is_qb") is not (grp == QB):
        return False, R_MALFORMED, None
    if team not in {norm_team(t) for t in (teams or []) if norm_team(t)}:
        return False, R_TEAM_NOT_IN_GAME, None
    at, dec = parse_ts(identity.get("as_of")), parse_ts(decision_time)
    if at is None:
        return False, R_NO_CLOCK, None
    if dec is None:                       # no decision clock supplied by the caller (structural check only; the gate that has the clock judges age)
        return True, None, {"gsis_id": pid.strip(), "position_group": grp, "is_qb": grp == QB, "team": team}
    if at > dec:
        return False, R_AFTER_DECISION, None
    if (dec - at).total_seconds() / 60.0 > max_age_min:
        return False, R_STALE, None
    return True, None, {"gsis_id": pid.strip(), "position_group": grp, "is_qb": grp == QB, "team": team}

