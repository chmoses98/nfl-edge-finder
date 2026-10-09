"""A1B prospective scorer (PREREGISTRATION_ADDENDUM_B_A1B.md). RESEARCH_ONLY -- no output has any authority.

Committed with addendum B, before any A1B record or source snapshot existed. It reuses the frozen Wave-2 scorer's
metric functions (nfl_edge/sim/wave2_score.py, not modified) so A1B is judged exactly like the other arms, and it
reads only A1B records (data/research/wave2_a1b/records/), never A1's: the two are never pooled.

Eligibility (addendum B.5): state OK; generated before kickoff; cutoff in (T-80, T-35]; frozen components; dry_run
false; source qualification QUALIFIED at capture with kickoff after `qualified_at`. Everything else is reported as
excluded with its reason; NO_USABLE_SOURCE / UNUSABLE_IDENTITY records are counted as missing, never imputed.
Primary: mean relative CRPS of the five opportunity statistics, A1B vs A0, on A0's scored rows; the gate is applied
once, on the first 64 eligible games in (kickoff, game_id) order.
"""
from __future__ import annotations

import pandas as pd

from . import a1b as A
from . import backtest as Bt
from . import wave2_eval as E
from . import wave2_score as W

A1B_SCORER_VERSION = "wave2-a1b-score-1.0.0"
MIN_GAMES = 64
ACCEPTED_VERSIONS = (A.A1B_VERSION,)


def parse_record_name(path: str):
    p = A.parse_name(path)
    return (p[1], p[2]) if p and p[0] == "REC" else None


def candidates(records: list, kickoffs: dict | None = None) -> list:
    out = []
    for r in records:
        doc = r["doc"]
        nm = parse_record_name(r["path"])
        for gid, g in (doc.get("games") or {}).items():
            c = {"path": r["path"], "sha256": r["sha256"], "game_id": gid, "rec": g, "generated_at": doc.get("generated_at"),
                 "kickoff": None, "reason": None}
            try:
                kos = [A._ts(x) for x in (g.get("kickoff_utc"), (kickoffs or {}).get(gid)) if x]
                ko = min(kos) if kos else None
            except ValueError as e:
                ko, c["reason"] = None, f"bad kickoff instant: {e}"
            q = g.get("source_qualification") or {}
            if c["reason"]:
                pass
            elif nm is None or nm[0] != gid:
                c["reason"] = "file name does not match its content"
            elif doc.get("research_only") is not True or doc.get("betting_authority") != "NONE":
                c["reason"] = "record does not declare research_only / betting_authority NONE"
            elif doc.get("dry_run"):
                c["reason"] = "dry-run record"
            elif doc.get("a1b_version") not in ACCEPTED_VERSIONS:
                c["reason"] = f"record version {doc.get('a1b_version')} not accepted"
            elif (doc.get("inputs") or {}).get("components_sha256") != W.FROZEN_COMPONENTS_SHA256:
                c["reason"] = "components differ from the frozen components"
            elif g.get("state") != "OK":
                c["reason"] = f"MISSING:{g.get('state')}:{g.get('reason') or ''}".rstrip(":")
            elif ko is None or ko <= A._ts(A.PROSPECTIVE_CUTOFF):
                c["reason"] = "no kickoff or kickoff before the prospective cutoff"
            elif not doc.get("generated_at") or A._ts(doc["generated_at"]) >= ko:
                c["reason"] = "generated at or after kickoff"
            elif not (A.A1B_WINDOW[0] < A.minutes_to(ko, g.get("cutoff")) <= A.A1B_WINDOW[1]):
                c["reason"] = "cutoff outside (T-80, T-35]"
            elif q.get("status") != "QUALIFIED" or not q.get("qualified_at") or ko <= A._ts(q["qualified_at"]):
                c["reason"] = f"source not QUALIFIED at capture ({q.get('status')}): pipeline validation only, not evidence"
            elif not all(a in (g.get("arms") or {}) for a in ("A0", "A1B")):
                c["reason"] = "arm missing"
            c["kickoff"] = ko.isoformat() if ko else None
            out.append(c)
    return out


def select(cands: list) -> tuple[dict, list]:
    """One record per game (write-once); a second record for a game is a collision and is excluded, never chosen."""
    by = {}
    for c in cands:
        by.setdefault(c["game_id"], []).append(c)
    sel, collisions = {}, []
    for gid, cs in by.items():
        if len(cs) > 1:
            collisions.append(gid)
            continue
        if cs[0]["reason"] is None:
            sel[gid] = cs[0]
    return sel, collisions


def player_frame(sel: dict, outcomes: dict) -> tuple[pd.DataFrame, dict]:
    rows, integrity = [], {}
    for gid in sorted(sel):
        c, o = sel[gid], outcomes.get(gid)
        if not W.outcome_ok(o):
            continue
        rec = c["rec"]; a0 = rec["arms"]["A0"]
        avail, a1b_state = rec.get("avail_state") or {}, rec.get("a1b_state") or {}
        inactive_teams = {(a0["players"].get(p) or {}).get("team") for p, s in a1b_state.items() if s == A.INACTIVE_STATE} - {None}
        for pid in sorted(a0.get("players") or {}):
            team = a0["players"][pid].get("team")
            for st in W.PLAYER_STATS:
                d0 = W._player_dist(a0, pid, st)
                if d0 is None or d0[0] < Bt.FLOORS.get(st, 0.0):
                    continue
                row = {"game_id": gid, "kickoff": c["kickoff"], "horizon": "A1B", "team": team, "player_id": pid, "stat": st,
                       "avail_state": avail.get(pid), "a1b_state": a1b_state.get(pid),
                       "team_has_q": team in inactive_teams, "actual": W.player_actual(o, pid, st),
                       "a0_mean": d0[0], "a0_q": d0[1], "a0_pmf": d0[2]}
                d = W._player_dist(rec["arms"]["A1B"], pid, st)
                if d is None:
                    integrity.setdefault(gid, []).append(f"{pid}:{st}")
                    row["A1B_ok"] = False
                else:
                    row["A1B_ok"] = True
                    row["A1B_mean"], row["A1B_q"], row["A1B_pmf"] = d
                rows.append(row)
    return pd.DataFrame(rows), integrity


def score(records: list, outcomes: dict, *, kickoffs: dict | None = None, interim: bool = False) -> dict:
    cands = candidates(records, kickoffs)
    sel, collisions = select(cands)
    final = {g for g in sel if W.outcome_ok(outcomes.get(g))}
    missing_outcome = {g: (outcomes.get(g) or {}).get("reason", "no outcome supplied") for g in sel if g not in final}
    P, integrity = player_frame(sel, outcomes)
    coh = sorted(g for g in final if not all((sel[g]["rec"].get("coherence") or {}).get(a) for a in ("A0", "A1B")))
    elig = sorted((sel[g]["kickoff"], g) for g in final)
    # paired_arm keeps a fixed column list; carry a1b_state through by re-attaching it after pairing
    def ev(gs):
        d = W.paired_arm(W._games(P, gs), "A1B")
        if not d.empty:
            key = P.set_index(["game_id", "player_id", "stat"])["a1b_state"]
            d["a1b_state"] = [key.get((g, p, s)) for g, p, s in zip(d["game_id"], d["player_id"], d["stat"])]
        return _evaluate_paired(d, gs, integrity, coh)
    out = {"development_status": "PROSPECTIVE_CHALLENGER (A1B, addendum B)", "n_eligible_games": len(elig), "n_required": MIN_GAMES}
    if len(elig) < MIN_GAMES:
        out.update(evidence_status="COLLECTING", promotion=None)
        if interim and elig:
            out["interim"] = {"label": "INTERIM -- no status change, gates not applied", **ev([g for _, g in elig])}
    else:
        aset = [g for _, g in elig][:MIN_GAMES]
        res = ev(aset)
        out.update(evidence_status="GATE_APPLIED_AT_MINIMUM", analysis_set=aset, at_minimum=res,
                   promotion="PROMOTION_CANDIDATE" if all(res["gates"].values()) else "NOT_PROMOTED_AT_MINIMUM",
                   promotion_note="a label for a human decision; deploys nothing and grants no authority")
    missing = {c["game_id"]: c["reason"] for c in cands if c["reason"] and c["reason"].startswith("MISSING:")}
    return W.clean({"scorer_version": A1B_SCORER_VERSION, "arm": "A1B", "not_pooled_with": "A1", **W.AUTHORITY,
                    "records": {"seen": [{"path": r["path"], "sha256": r["sha256"]} for r in records],
                                "used": {g: {"path": c["path"], "sha256": c["sha256"], "kickoff": c["kickoff"]} for g, c in sorted(sel.items())},
                                "excluded": [{"path": c["path"], "game_id": c["game_id"], "reason": c["reason"]} for c in cands if c["reason"]],
                                "write_once_collisions": collisions},
                    "missing_observations": missing, "outcomes": {"games_with_outcome": sorted(final), "games_missing_outcome": missing_outcome},
                    "coherence_failures": coh, "integrity_failures": integrity, "A1B": out})


def _evaluate_paired(d: pd.DataFrame, games: list, integrity: dict, coh_fail: list) -> dict:
    G = W.s1_game_sums(d, games)
    prim = W.game_boot(G, W.s1_primary_from_sums)
    others = [s for s in W.PLAYER_STATS if s not in E.S1_STATS]
    lg = W.logo(G, W.s1_primary_from_sums, -1)
    bad = {g: v for g, v in integrity.items() if g in games}
    for g in coh_fail:
        if g in games:
            bad.setdefault(g, []).append("coherence flag false")
    gates = {"primary_interval_excludes_zero_improving": prim["hi"] is not None and prim["hi"] < 0,
             "mae_of_the_five_non_inferior": all(v.get("ok", False) for v in W._ni(d, games, E.S1_STATS, "mae").values()),
             "crps_of_every_other_scored_stat_non_inferior": all(v.get("ok", True) for v in W._ni(d, games, others, "crps").values()),
             "zero_integrity_or_coherence_failures": not bad, "leave_one_game_out": lg["ok"]}
    has = "a1b_state" in d.columns and not d.empty
    secondary = {"questionable_abs_bias_change": W.game_boot(W.a1_game_sums(d, games), W.a1_primary_from_sums) if not d.empty else None,
                 "teammates_of_confirmed_inactives": W.stat_table(d[(d["a1b_state"] != A.INACTIVE_STATE) & d["team_has_q"]]) if has else {},
                 "confirmed_inactive_rows": W.stat_table(d[d["a1b_state"] == A.INACTIVE_STATE]) if has else {},
                 "note": "descriptive; Holm across these three; never a gate"}
    return {"primary": prim, "stats": W.stat_table(d), "logo": lg, "gates": gates, "integrity_failures": bad, "secondary": secondary}
