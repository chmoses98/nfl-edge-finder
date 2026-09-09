"""Independent proof that a game is OVER, separate from proof of what the score was.

A populated score is not a final status. nflverse rebuilds `games.csv` on a schedule and a row can carry a
score while the game is still being played; "four hours have passed" is a plausibility guard, not evidence. So
FINAL is proven by two independent things:

    the score fields agree with themselves   result == home - away, total == home + away  (results.py)
    something else says the game is COMPLETE  an attestation, from here

Two attestation sources, both free and both already used by this repo:

`postgame_tables`  the game appears in nflverse's `stats_player_week` AND `snap_counts` releases. Those are
                   built from finished games only, so presence is positive evidence that the game was played
                   to completion. This needs no network beyond the downloads the settle job already makes,
                   which is why it is the primary attestation.
`espn_scoreboard`  ESPN's public scoreboard (`site.api.espn.com/.../scoreboard?dates=YYYYMMDD`, probed and
                   recorded as usable in scripts/data/probe_sources.py) carries an explicit
                   `status.type.completed` boolean plus per-competitor scores. The schedule's own `espn`
                   column gives the event id, so the join needs no name matching.

ESPN can only ever ADD a proof or REVEAL A CONTRADICTION -- it is never required. An ESPN outage must not be
able to stop settlement, and an ESPN disagreement about the score must be able to stop it. That asymmetry is
the whole design: a source that can only block is a source whose failure mode is safe.
"""
from __future__ import annotations

import json
import urllib.error
import urllib.request
from dataclasses import dataclass, field
from datetime import datetime, timezone

SCOREBOARD_URL = "https://site.api.espn.com/apis/site/v2/sports/football/nfl/scoreboard"
USER_AGENT = ("nfl-edge-finder settlement final-status (read-only research; "
              "github.com/chmoses98/nfl-edge-finder)")

POSTGAME_TABLES = "postgame_tables"
ESPN_SCOREBOARD = "espn_scoreboard"


@dataclass
class FinalAttestation:
    """One source's statement about whether a game finished, and with what score."""
    source: str
    event_id: str | None = None
    completed: bool | None = None
    state: str | None = None                 # espn: pre | in | post
    detail: str | None = None
    home_team: str | None = None
    away_team: str | None = None
    home_score: float | None = None
    away_score: float | None = None
    retrieved_at: str | None = None

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v is not None}


def _f(v):
    try:
        return float(v)
    except (TypeError, ValueError):
        return None


def attestations_from_espn_scoreboard(payload: dict, *, retrieved_at: str | None = None) -> dict:
    """ESPN scoreboard JSON -> {espn event id: FinalAttestation}.

    Only the fields that matter are read, and nothing is inferred: an event with no explicit `completed`
    boolean produces `completed=None`, which proves nothing rather than proving absence.
    """
    out = {}
    for ev in (payload or {}).get("events") or []:
        eid = str(ev.get("id")) if ev.get("id") is not None else None
        if not eid:
            continue
        comp = (ev.get("competitions") or [{}])[0] or {}
        status = (comp.get("status") or ev.get("status") or {})
        st = status.get("type") or {}
        att = FinalAttestation(source=ESPN_SCOREBOARD, event_id=eid,
                               completed=st.get("completed") if isinstance(st.get("completed"), bool) else None,
                               state=st.get("state"), detail=st.get("detail") or st.get("description"),
                               retrieved_at=retrieved_at)
        for c in comp.get("competitors") or []:
            side, abbr, score = c.get("homeAway"), (c.get("team") or {}).get("abbreviation"), _f(c.get("score"))
            if side == "home":
                att.home_team, att.home_score = abbr, score
            elif side == "away":
                att.away_team, att.away_score = abbr, score
        out[eid] = att
    return out


def fetch_espn_scoreboard(dates, *, timeout: int = 45, verbose=None) -> tuple[dict, list]:
    """Best-effort: attestations for one or more YYYYMMDD dates, plus a provenance list.

    Never raises. A failure returns no attestations and records why, because the caller must be able to settle
    from the primary attestation when ESPN is unavailable.
    """
    atts, meta = {}, []
    for date in dates:
        url = f"{SCOREBOARD_URL}?dates={date}"
        t0 = datetime.now(timezone.utc).isoformat()
        try:
            req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                body = r.read()
            payload = json.loads(body)
            got = attestations_from_espn_scoreboard(payload, retrieved_at=t0)
            atts.update(got)
            meta.append({"url": url, "status": 200, "bytes": len(body), "events": len(got), "retrieved_at": t0})
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError, TimeoutError, OSError) as e:
            meta.append({"url": url, "status": None, "error": f"{type(e).__name__}: {str(e)[:200]}",
                         "retrieved_at": t0})
        if verbose:
            verbose(f"  espn scoreboard {date}: {meta[-1].get('events', meta[-1].get('error'))}")
    return atts, meta


@dataclass
class FinalVerdict:
    proven: bool = False
    proofs: list = field(default_factory=list)
    contradictions: list = field(default_factory=list)

    def to_dict(self):
        return {"final_proven": self.proven, "final_proofs": list(self.proofs),
                "final_contradictions": list(self.contradictions)}


def verify_final(game, *, in_postgame_tables: bool, attestation: FinalAttestation | None = None,
                 score_tolerance: float = 0.0) -> FinalVerdict:
    """Is this game independently proven complete? Contradictions are collected, never smoothed over.

    `game` is a `results.GameResult` whose own score fields have already been checked for self-consistency.
    """
    v = FinalVerdict()
    if in_postgame_tables:
        v.proofs.append(POSTGAME_TABLES)
    if attestation is not None:
        if attestation.completed is True:
            v.proofs.append(ESPN_SCOREBOARD)
        elif attestation.completed is False or attestation.state in ("pre", "in"):
            v.contradictions.append(
                f"{attestation.source} reports the game as not complete "
                f"(state={attestation.state!r}, detail={attestation.detail!r})")
        # scores are compared whatever the completion flag says: a source that agrees the game is over but
        # disagrees about the score is the most dangerous kind of agreement.
        for side, ours, theirs in (("home", game.home_score, attestation.home_score),
                                   ("away", game.away_score, attestation.away_score)):
            if ours is not None and theirs is not None and abs(ours - theirs) > score_tolerance:
                v.contradictions.append(
                    f"{attestation.source} {side} score {theirs:g} != schedule {ours:g}")
    v.proven = bool(v.proofs) and not v.contradictions
    return v
