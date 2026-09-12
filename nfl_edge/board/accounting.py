"""Board Accounting v1: one terminal state per discovered contract, denominator = the discovered NFL board.

Inputs
    discovery run     every open market of every NFL-candidate series (the board)
    registry          config/kalshi_nfl_series.json (+ provisional list) -> is the series captured, at what tier
    capture state     `last_seen` per ticker -> was the contract actually confirmed open by a capture run
    schedule          kickoff per game -> POST_KICKOFF
    identity          Kalshi player uuid -> GSIS status
    projections       (optional) the v2 projection rows of the reference snapshot -> PROJECTED / PRICED
    ledger            (optional) the incumbent's rows at the same capture, for a before/after comparison

Two independent things are recorded per contract: the FUNNEL stages it passed (in order) and the TERMINAL
state it ended in. Percentages are always over the NFL board.
"""
from __future__ import annotations

import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone

from nfl_edge.board import states as S
from nfl_edge.board.drift import is_nfl_series
from nfl_edge.kalshi.classifier import classify
from nfl_edge.semantics.catalog import (
    DATA_UNAVAILABLE, JOINT_MODEL_REQUIRED, NEWS_EVENT_MODEL_REQUIRED, NON_FOOTBALL_MODEL, PRICED as MODEL_PRICED,
    RESEARCH_REQUIRED, SETTLE_SUPPORTED, SETTLE_UNSUPPORTED, SHADOW, UNSUPPORTED as MODEL_UNSUPPORTED, catalog_entry,
)
from nfl_edge.semantics.questions import AMBIGUOUS, LIKELY, NONE, PROVEN, UNKNOWN, contract_question

ACCOUNTING_VERSION = "board-accounting-1.0.0"
RESOLVED_STATUSES = ("RESOLVED", "RESOLVED_TEAM_UNCONFIRMED", "RESOLVED_PLAYERS_TABLE", "RESOLVED_JERSEY_MISMATCH")


def _dt(s):
    if not s:
        return None
    try:
        d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def classify_contract(m: dict, series: dict, *, registry_series: dict, provisional: dict, capture_seen: set | None,
                      kickoffs: dict, player_status: dict, projection: dict | None, now: datetime) -> dict:
    """One open market -> stages passed + terminal state + reason. Deterministic; every branch names its reason."""
    t = m.get("ticker")
    stages = [S.DISCOVERED]
    out = {"ticker": t, "series": series.get("ticker"), "event_ticker": m.get("event_ticker"), "stages": stages,
           "terminal_state": None, "terminal_reason": None, "family": None, "period": None, "stat": None,
           "engine": None, "semantic_confidence": None, "model_support": None, "settlement": None,
           "captured_tier": None, "confirmed_open": None, "game_id": None, "kickoff_utc": None, "projection_state": None}
    nfl, why = is_nfl_series(series)
    if not nfl:
        out.update(terminal_state=S.EXCLUDED, terminal_reason=f"not an NFL series: {why}")
        return out
    stages.append(S.NFL_BOARD)
    sem = classify(m)
    q = contract_question(sem, m)
    entry = catalog_entry(sem.family, sem.period, sem.stat)
    out.update(family=sem.family, period=sem.period, stat=sem.stat, engine=q.engine, semantic_confidence=q.semantic_confidence,
               model_support=entry.model_support if entry else None, settlement=entry.settlement if entry else None)
    # ---- capture: registry tier, provisional tier, and (when a capture state is given) actual confirmation
    st = series.get("ticker")
    tier = (registry_series.get(st) or {}).get("tier") or (provisional.get(st) or {}).get("tier")
    out["captured_tier"] = tier
    if capture_seen is not None:
        out["confirmed_open"] = t in capture_seen
    # ---- game / kickoff
    kick = None
    if sem.game_date and sem.away_team and sem.home_team:
        kick = kickoffs.get((sem.game_date, sem.away_team, sem.home_team))
    if kick:
        out["game_id"], out["kickoff_utc"] = kick["game_id"], kick["kickoff_utc"]
    # ---- terminal decision, in priority order --------------------------------------------------------------
    if sem.family in ("UNKNOWN_NEEDS_CLASSIFICATION", "NOT_NFL_OR_UNKNOWN"):
        if tier is None or tier == "NOT_CAPTURED":
            out.update(terminal_state=S.NOT_CAPTURED, terminal_reason="unclassified series absent from the registry and the provisional list")
        else:
            stages.append(S.CAPTURED)
            out.update(terminal_state=S.CAPTURE_ONLY, terminal_reason=f"unclassified series captured provisionally at {tier}; semantics UNKNOWN")
        return out
    stages.append(S.CLASSIFIED)
    if tier is None or tier == "NOT_CAPTURED":
        out.update(terminal_state=S.NOT_CAPTURED, terminal_reason=("series in no capture tier" if tier is None else "registry tier NOT_CAPTURED: " + str((registry_series.get(st) or {}).get("reason"))))
        return out
    if capture_seen is not None and t not in capture_seen:
        # the series is polled but this ticker has never come back open: a new market since the last run, or a pagination gap
        out.update(terminal_state=S.NOT_CAPTURED, terminal_reason=f"series {st} is polled at {tier} but this ticker was never confirmed open by a capture run")
        return out
    stages.append(S.CAPTURED)
    ko = _dt(out["kickoff_utc"])
    if ko is not None and now >= ko:
        out.update(terminal_state=S.POST_KICKOFF, terminal_reason="kickoff has passed; pregame projection window closed")
        return out
    if entry is None:
        out.update(terminal_state=S.UNSUPPORTED, terminal_reason=f"family {sem.family}/{sem.period} has no catalog entry")
        return out
    if entry.model_support in (NON_FOOTBALL_MODEL, NEWS_EVENT_MODEL_REQUIRED):
        out.update(terminal_state=S.NON_FOOTBALL_MODEL, terminal_reason=entry.reason or "news / vote / transaction event")
        return out
    if q.semantic_confidence in (AMBIGUOUS, UNKNOWN) or entry.semantic_confidence in (AMBIGUOUS, UNKNOWN):
        out.update(terminal_state=S.SEMANTICS_AMBIGUOUS,
                   terminal_reason=f"question {q.semantic_confidence}, catalog {entry.semantic_confidence}: " + "; ".join(list(q.notes)[:2]))
        return out
    stages.append(S.SEMANTICS_PROVEN if (q.semantic_confidence == PROVEN and entry.semantic_confidence == PROVEN) else "SEMANTICS_LIKELY")
    # ---- identity
    if q.subject_kind == "player":
        pst = player_status.get(sem.player_kalshi_id)
        if sem.player_kalshi_id and pst == "NOT_A_PLAYER":
            out.update(terminal_state=S.UNSUPPORTED, terminal_reason="team D/ST or non-player entity")
            return out
        if pst not in RESOLVED_STATUSES:
            out.update(terminal_state=S.IDENTITY_UNRESOLVED, terminal_reason=f"Kalshi player id {sem.player_kalshi_id} status {pst}")
            return out
    elif q.subject_kind == "team" and q.subject is None:
        out.update(terminal_state=S.IDENTITY_UNRESOLVED, terminal_reason="team not resolved from the ticker")
        return out
    elif sem.scope == "GAME" and sem.game_date and not kick:
        out.update(terminal_state=S.IDENTITY_UNRESOLVED, terminal_reason="market did not join a scheduled game")
        return out
    stages.append(S.IDENTITY_RESOLVED)
    # ---- data / model support
    if entry.model_support == DATA_UNAVAILABLE:
        out.update(terminal_state=S.DATA_UNAVAILABLE, terminal_reason=entry.reason or "no free point-in-time data")
        return out
    stages.append(S.DATA_AVAILABLE)
    if entry.model_support == JOINT_MODEL_REQUIRED:
        out.update(terminal_state=S.JOINT_MODEL_REQUIRED, terminal_reason=entry.reason or "dependence not modelled")
        return out
    if entry.model_support == RESEARCH_REQUIRED:
        out.update(terminal_state=S.RESEARCH_REQUIRED, terminal_reason=entry.reason or "no engine yet")
        return out
    if entry.model_support == MODEL_UNSUPPORTED or q.engine == NONE:
        out.update(terminal_state=S.UNSUPPORTED, terminal_reason=entry.reason or "no engine")
        return out
    stages.append(S.MODEL_SUPPORTED)
    if entry.settlement == SETTLE_UNSUPPORTED:
        out.update(terminal_state=S.SETTLEMENT_UNSUPPORTED, terminal_reason=entry.reason or "no settlement path")
        return out
    # ---- projected?
    if projection is not None:
        ps = projection.get("support_state")
        out["projection_state"] = ps
        if ps in ("PRICED", "PROJECTABLE_NOT_YET_VALIDATED"):
            stages.append(S.PROJECTED)
            if entry.settlement == SETTLE_SUPPORTED:
                stages.append(S.SETTLEMENT_CAPABLE)
            if ps == "PRICED" and q.semantic_confidence == PROVEN and entry.model_support == MODEL_PRICED and entry.settlement == SETTLE_SUPPORTED:
                out.update(terminal_state=S.PRICED, terminal_reason="validated engine, PROVEN semantics, settlement supported")
            else:
                out.update(terminal_state=S.PROJECTABLE_NOT_YET_VALIDATED,
                           terminal_reason=f"projection {ps}; engine {entry.model_support}; semantics {q.semantic_confidence}; settlement {entry.settlement}")
            return out
        out.update(terminal_state=S.CAPTURE_ONLY, terminal_reason=f"engine supports the family but the snapshot wrote {ps}: {projection.get('support_reason')}")
        return out
    # no projection snapshot given: the architectural state
    if entry.settlement == SETTLE_SUPPORTED:
        stages.append(S.SETTLEMENT_CAPABLE)
    out.update(terminal_state=S.PROJECTABLE_NOT_YET_VALIDATED if (entry.model_support == SHADOW or q.semantic_confidence == LIKELY or entry.settlement != SETTLE_SUPPORTED) else S.PRICED,
               terminal_reason=f"architecture: engine {entry.model_support}, semantics {q.semantic_confidence}, settlement {entry.settlement} (no snapshot given)")
    return out


def load_kickoffs(schedule_csv_path: str) -> dict:
    import csv, io
    from nfl_edge.data.nfl_calendar import kickoff_utc
    ko = {}
    with open(schedule_csv_path) as f:
        for row in csv.DictReader(io.StringIO(f.read())):
            k = kickoff_utc((row.get("gameday") or "").strip(), (row.get("gametime") or "").strip())
            if k:
                ko[(row["gameday"], row["away_team"], row["home_team"])] = {"kickoff_utc": k.isoformat(), "game_id": row["game_id"]}
    return ko


def build_board(disc: dict, *, registry_series: dict, provisional: dict | None = None, capture_state: dict | None = None,
                kickoffs: dict | None = None, player_status: dict | None = None, projections: list | None = None,
                now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    provisional = provisional or {}
    kickoffs = kickoffs or {}
    player_status = player_status or {}
    capture_seen = None
    if capture_state is not None:
        capture_seen = set((capture_state.get("last_seen") or {}).keys())
    proj_by_ticker = {}
    for r in projections or []:
        # the strongest state per ticker across arms
        prev = proj_by_ticker.get(r.get("ticker"))
        rank = {"PRICED": 2, "PROJECTABLE_NOT_YET_VALIDATED": 1}.get(r.get("support_state"), 0)
        if prev is None or rank > {"PRICED": 2, "PROJECTABLE_NOT_YET_VALIDATED": 1}.get(prev.get("support_state"), 0):
            proj_by_ticker[r.get("ticker")] = r
    series_by_ticker = {s.get("ticker"): s for s in disc["series_nfl"]}
    rows = []
    for st, mk in disc["markets"].items():
        series = series_by_ticker.get(st) or {"ticker": st}
        for m in (mk.get("open") or {}).get("markets", []):
            rows.append(classify_contract(m, series, registry_series=registry_series, provisional=provisional, capture_seen=capture_seen,
                                          kickoffs=kickoffs, player_status=player_status,
                                          projection=(proj_by_ticker.get(m.get("ticker")) if projections is not None else None), now=now))
    return {"accounting_version": ACCOUNTING_VERSION, "discovery_run": disc.get("run_id"), "generated_at": now.isoformat(),
            "reference_snapshot": (projections[0].get("snapshot_id") if projections else None), "rows": rows, **summarize(rows)}


def summarize(rows: list) -> dict:
    n_disc = len(rows)
    board = [r for r in rows if S.NFL_BOARD in r["stages"]]
    n = len(board)
    term = Counter(r["terminal_state"] for r in board)
    stage_counts = Counter()
    for r in board:
        for s in r["stages"]:
            stage_counts[s] += 1
    by_family = defaultdict(Counter)
    for r in board:
        by_family[f"{r['family']}|{r['period']}"][r["terminal_state"]] += 1
    reasons = Counter((r["terminal_state"], (r["terminal_reason"] or "")[:90]) for r in board)
    unexplained = [r["ticker"] for r in rows if not r["terminal_state"]]
    def pct(x):
        return round(100.0 * x / n, 2) if n else None
    return {"denominator": {"discovered_contracts": n_disc, "excluded_not_nfl": n_disc - n, "nfl_board_contracts": n,
                            "note": "percentages are over the NFL board (discovered contracts of NFL series), never over ledger rows"},
            "stages": {s: {"n": stage_counts.get(s, 0), "pct": pct(stage_counts.get(s, 0))} for s in S.STAGES if s != S.DISCOVERED},
            "terminal_states": {s: {"n": term.get(s, 0), "pct": pct(term.get(s, 0))} for s in S.TERMINAL_STATES},
            "unexplained": {"n": len(unexplained), "tickers": unexplained[:20]},
            "by_family": {k: dict(v) for k, v in sorted(by_family.items())},
            "top_reasons": [{"state": k[0], "reason": k[1], "n": v} for k, v in reasons.most_common(40)]}


def render_board(rep: dict, title: str = "Board Accounting v1") -> str:
    d = rep["denominator"]
    L = [f"# {title}", "", f"Discovery run `{rep['discovery_run']}`; reference snapshot `{rep.get('reference_snapshot')}`; generated {rep['generated_at']}.", "",
         f"Denominator: **{d['nfl_board_contracts']} open NFL contracts** ({d['discovered_contracts']} discovered, {d['excluded_not_nfl']} excluded as not NFL).", "",
         "## Funnel v2", "", "| stage | contracts | % of board |", "|---|---|---|"]
    for s, v in rep["stages"].items():
        L.append(f"| {s} | {v['n']} | {v['pct']} |")
    L += ["", "## Terminal states", "", "| state | contracts | % of board |", "|---|---|---|"]
    for s, v in rep["terminal_states"].items():
        L.append(f"| {s} | {v['n']} | {v['pct']} |")
    L += ["", f"Unexplained (no terminal state): **{rep['unexplained']['n']}**", "", "## By family", "", "| family | period | states |", "|---|---|---|"]
    for k, v in rep["by_family"].items():
        fam, per = k.split("|")
        L.append(f"| {fam} | {per} | " + ", ".join(f"{s} {n}" for s, n in sorted(v.items(), key=lambda x: -x[1])) + " |")
    L += ["", "## Top reasons", "", "| state | reason | n |", "|---|---|---|"]
    for r in rep["top_reasons"]:
        L.append(f"| {r['state']} | {r['reason']} | {r['n']} |")
    return "\n".join(L)
