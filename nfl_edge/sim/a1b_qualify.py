"""A1B source qualification (PREREGISTRATION_ADDENDUM_B_A1B.md section B.4, as restarted by amendment B1
PREREGISTRATION_AMENDMENT_B1_A1B_SOURCE.md) -- mechanical, source behaviour only.

Committed with addendum B, before any source snapshot existed. It reads this repository's snapshots of the source
and, for criterion QT only, nflverse's POSTGAME `INA` list to check that the source named the right players. No
projection, prediction or game outcome is read. Decision: QUALIFIED only if every criterion passes; BLOCKED
otherwise; AWAITING_GAMES / AWAITING_TRUTH while the qualification set is incomplete (no partial decision).

Amendment B1 (1.1.0): only snapshots of the current source version count, and QR is evaluable for a team only when
its early snapshot is a 200 response (an OUTAGE shows nothing about whether a list was already there).
"""
from __future__ import annotations

from datetime import timedelta

from . import a1b as A

QUALIFY_VERSION = "a1b-qualify-1.1.0"
N_GAMES = 24
EARLY_BEFORE_MIN = 110.0
FREEZE_MIN = 35.0
THRESHOLDS = {"QA": 0.90, "QR": 0.90, "QS": 0.90, "QT": 0.90, "QM": 0.98}
QR_MIN_EVALUABLE = 12
JACCARD_MIN = 0.80


def _team_state(snap, side):
    return (snap["teams"].get(side) or {}).get("reading", {}) if snap else {}


def _side_of(game, team):
    return "home" if game["home_team"] == team else "away"


def _jaccard(a: set, b: set) -> float:
    return 1.0 if not a and not b else len(a & b) / len(a | b)


def evaluate(games: list, snaps_by_game: dict, truth: dict, gsis_of_espn: dict, *, now) -> dict:
    """`games`: the qualification set (first 24 post-activation games), each with game_id, kickoff_utc, home_team,
    away_team. `truth`: {(game_id, team): set of gsis} from nflverse postgame INA, missing key = not yet published."""
    now = A._ts(now)
    if len(games) < N_GAMES or any(A._ts(g["kickoff_utc"]) >= now for g in games):
        return {"version": QUALIFY_VERSION, "decision": "AWAITING_GAMES", "n_games": len(games)}
    per_game, per_team = [], []
    mapped_ids = total_ids = 0
    for g in games:
        ko = A._ts(g["kickoff_utc"])
        snaps = sorted(A.current_version(snaps_by_game.get(g["game_id"], [])), key=lambda s: s.get("retrieved_at") or "")
        freeze = ko - timedelta(minutes=FREEZE_MIN)
        game_cut, _ = A.choose_snapshot(snaps, freeze)
        per_game.append({"game_id": g["game_id"], "QA": game_cut is not None, "n_snapshots": len(snaps)})
        pre = [s for s in snaps if s.get("retrieved_at") and A._ts(s["retrieved_at"]) < ko]
        for team in (g["home_team"], g["away_team"]):
            side = _side_of(g, team)
            in_win = [s for s in pre if ko - timedelta(minutes=A.RELEASE_FLOOR_MIN) <= A._ts(s["retrieved_at"]) <= freeze
                      and _team_state(s, side).get("state") == A.USABLE]
            cut = in_win[-1] if in_win else None
            first = in_win[0] if in_win else None
            early = [s for s in pre if A._ts(s["retrieved_at"]) < ko - timedelta(minutes=EARLY_BEFORE_MIN)]
            row = {"game_id": g["game_id"], "team": team}
            # QR: release, not an echo of a week-long roster status
            if early and _team_state(early[-1], side).get("state") not in (None, A.OUTAGE):
                e = _team_state(early[-1], side)
                row["QR_evaluable"] = True
                row["QR"] = first is not None and (len(e.get("inactive_espn_ids") or []) == 0 or
                                                   set(e.get("inactive_espn_ids") or []) != set(_team_state(first, side)["inactive_espn_ids"]))
            else:
                row["QR_evaluable"], row["QR"] = False, None
            # QS: the list frozen at T-35 is the list right before kickoff
            last = pre[-1] if pre else None
            row["QS"] = (cut is not None and _team_state(last, side).get("state") == A.USABLE
                         and set(_team_state(last, side)["inactive_espn_ids"]) == set(_team_state(cut, side)["inactive_espn_ids"]))
            # QT / QM: the frozen list against nflverse's postgame INA (source validation only)
            ids = set(_team_state(cut, side).get("inactive_espn_ids") or []) if cut else set()
            mapped = {gsis_of_espn[i] for i in ids if i in gsis_of_espn}
            total_ids += len(ids); mapped_ids += len(mapped)
            t = truth.get((g["game_id"], team))
            if t is None:
                return {"version": QUALIFY_VERSION, "decision": "AWAITING_TRUTH",
                        "reason": f"nflverse has no postgame INA for {g['game_id']} {team} yet", "n_games": len(games)}
            row["jaccard"] = round(_jaccard(mapped, set(t)), 4) if cut else None
            row["QT"] = cut is not None and _jaccard(mapped, set(t)) >= JACCARD_MIN
            row["n_inactive_frozen"], row["n_inactive_truth"] = len(ids), len(t)
            per_team.append(row)
    rate = lambda xs: (sum(1 for x in xs if x) / len(xs)) if xs else 0.0   # noqa: E731
    qr_rows = [r["QR"] for r in per_team if r["QR_evaluable"]]
    crit = {"QA": rate([r["QA"] for r in per_game]), "QR": rate(qr_rows), "QS": rate([r["QS"] for r in per_team]),
            "QT": rate([r["QT"] for r in per_team]), "QM": (mapped_ids / total_ids) if total_ids else 0.0}
    passed = {k: crit[k] >= THRESHOLDS[k] for k in crit}
    passed["QR"] = passed["QR"] and len(qr_rows) >= QR_MIN_EVALUABLE
    return {"version": QUALIFY_VERSION, "decision": "QUALIFIED" if all(passed.values()) else "BLOCKED",
            "rates": crit, "thresholds": THRESHOLDS, "passed": passed, "qr_evaluable": len(qr_rows),
            "games": [g["game_id"] for g in games], "per_game": per_game, "per_team": per_team,
            "research_only": True, "betting_authority": "NONE"}
