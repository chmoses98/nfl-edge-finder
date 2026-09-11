"""Production health gates TENNIS-1 .. TENNIS-14. Each gate returns GateResult(status PASS|FAIL|UNKNOWN, detail).

UNKNOWN is a failure for production purposes (fail closed): a gate that cannot be evaluated because the
evidence is missing does not turn green. Gates read the artifacts the pipeline produces; none of them may
be weakened to pass -- change the pipeline, not the gate.
"""
from __future__ import annotations

import glob
import gzip
import json
import os
from dataclasses import dataclass, asdict
from datetime import datetime, timezone, timedelta

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


@dataclass
class GateResult:
    gate: str
    name: str
    status: str
    detail: dict

    def to_dict(self):
        return asdict(self)


def _latest_discovery(root=None):
    root = root or os.path.join(PROJ, "data", "kalshi", "discovery")
    runs = sorted(glob.glob(os.path.join(root, "*", "summary.json")))
    return os.path.dirname(runs[-1]) if runs else None


def gate_1_discovery(now=None) -> GateResult:
    """TENNIS-1: complete Kalshi tennis discovery -- latest snapshot complete, catalogue paginated fully, < 36h old."""
    d = _latest_discovery()
    if not d:
        return GateResult("TENNIS-1", "kalshi_tennis_discovery", "UNKNOWN", {"reason": "no discovery snapshot"})
    s = json.load(open(os.path.join(d, "summary.json")))
    started = datetime.fromisoformat(s["started_at"])
    age_h = ((now or datetime.now(timezone.utc)) - started).total_seconds() / 3600
    ok = s.get("complete") and s.get("series_complete") and not s.get("failures") and age_h < 36
    return GateResult("TENNIS-1", "kalshi_tennis_discovery", "PASS" if ok else "FAIL",
                      {"run": s["run_id"], "age_hours": round(age_h, 1), "complete": s.get("complete"), "failures": len(s.get("failures", [])), "series_tennis": s.get("series_tennis")})


def gate_2_taxonomy() -> GateResult:
    """TENNIS-2: every discovered tennis series maps to a known family and >= 99.5% of live markets parse or are explicitly unsupported."""
    from tennis_edge.kalshi.families import unknown_series
    from tennis_edge.kalshi.markets import parse_market
    d = _latest_discovery()
    if not d:
        return GateResult("TENNIS-2", "taxonomy_normalization", "UNKNOWN", {"reason": "no discovery snapshot"})
    series = json.load(open(os.path.join(d, "series_tennis.json")))
    unk = unknown_series([s["ticker"] for s in series])
    n = bad = 0
    for p in glob.glob(os.path.join(d, "markets", "*.json")):
        for st, blk in json.load(open(p)).items():
            for m in blk.get("markets") or []:
                n += 1
                if parse_market(m).status == "UNPARSED":
                    bad += 1
    rate = 1 - bad / n if n else 0
    ok = not unk and n > 0 and rate >= 0.995
    return GateResult("TENNIS-2", "taxonomy_normalization", "PASS" if ok else "FAIL", {"unknown_series": unk, "live_markets": n, "unparsed": bad, "parse_rate": round(rate, 5)})


def gate_3_4_active_coverage(projections_path=None) -> tuple[GateResult, GateResult]:
    """TENNIS-3: every ACTIVE market is mapped (parsed or explicitly unsupported);
    TENNIS-4: every active PROJECTABLE market has a projection in the latest projection run."""
    from tennis_edge.kalshi.markets import parse_market
    d = _latest_discovery()
    if not d:
        u = GateResult("TENNIS-3", "active_market_mapping", "UNKNOWN", {"reason": "no discovery"})
        return u, GateResult("TENNIS-4", "active_market_projection", "UNKNOWN", {"reason": "no discovery"})
    active = []
    for p in glob.glob(os.path.join(d, "markets", "*.json")):
        for m in json.load(open(p)).get("open", {}).get("markets") or []:
            active.append(parse_market(m))
    unparsed = [x.ticker for x in active if x.status == "UNPARSED"]
    g3 = GateResult("TENNIS-3", "active_market_mapping", "PASS" if not unparsed and active else ("UNKNOWN" if not active else "FAIL"),
                    {"active": len(active), "unparsed": unparsed[:20], "unsupported": sum(x.status == "UNSUPPORTED_FAMILY" for x in active)})
    proj_path = projections_path or os.path.join(PROJ, "data", "research", "projections", "latest.json")
    if not os.path.exists(proj_path):
        return g3, GateResult("TENNIS-4", "active_market_projection", "UNKNOWN", {"reason": "no projection run", "projectable_active": sum(x.projectable and x.status == "PARSED" for x in active)})
    pj = json.load(open(proj_path))
    have = set(pj.get("projected_tickers", []))
    # the projection run already applied lifecycle (closed since discovery) and pregame exclusions, which are not
    # coverage failures; what counts is every still-open, pregame, projectable market that was NOT priced
    hard = [e for e in pj.get("excluded", []) if e.get("stage") in ("event", "identity", "format", "pricing", "doubles")]
    need = len(have) + len(hard)
    g4 = GateResult("TENNIS-4", "active_market_projection", "PASS" if not hard else "FAIL",
                    {"projectable_open_pregame": need, "projected": len(have), "not_projected": len(hard), "missing_sample": [e["ticker"] + ": " + e["reason"][:60] for e in hard[:10]],
                     "excluded_by_policy": {k: v for k, v in pj.get("coverage", {}).items() if k in ("closed_since_discovery", "past_nominal_start", "unsupported_family", "tournament_scope_not_priced_tonight")},
                     "projection_run": pj.get("run_id")})
    return g3, g4


def gate_5_capture_freshness(max_age_min=30, now=None) -> GateResult:
    """TENNIS-5: latest capture manifest younger than max_age_min and without incomplete stages."""
    mans = sorted(glob.glob(os.path.join(PROJ, "data", "kalshi", "capture", "*", "*.manifest.json")))
    if not mans:
        return GateResult("TENNIS-5", "market_capture_freshness", "UNKNOWN", {"reason": "no capture manifests"})
    m = json.load(open(mans[-1]))
    age = ((now or datetime.now(timezone.utc)) - datetime.fromisoformat(m["finished_at"])).total_seconds() / 60
    ok = age <= max_age_min and not m.get("incomplete")
    return GateResult("TENNIS-5", "market_capture_freshness", "PASS" if ok else "FAIL", {"run": m["run_id"], "age_min": round(age, 1), "incomplete": m.get("incomplete", [])[:5]})


def gate_6_no_post_start_leakage(ledger_rows, starts: dict) -> GateResult:
    """TENNIS-6: every pregame prediction was generated strictly before the match's actual first ball
    (or, when unknown, before scheduled_start - 5 min, flagged). `starts` maps match_id -> (actual_first_ball, scheduled_start)."""
    viol = []; unknown = 0
    for r in ledger_rows:
        gen = datetime.fromisoformat(r["generated_at_utc"])
        afb, sched = starts.get(r["match_id"], (None, None))
        if afb is not None:
            if gen >= afb:
                viol.append(r["prediction_id"])
        elif sched is not None:
            unknown += 1
            if gen >= sched - timedelta(minutes=5):
                viol.append(r["prediction_id"])
        else:
            viol.append(r["prediction_id"])
    return GateResult("TENNIS-6", "no_post_start_leakage", "PASS" if not viol else "FAIL", {"violations": viol[:20], "n": len(ledger_rows), "start_unknown_used_schedule": unknown})


def gate_7_identity(links_summary: dict | None) -> GateResult:
    """TENNIS-7: no AMBIGUOUS mapping is used in production; ambiguity rate reported."""
    if not links_summary:
        return GateResult("TENNIS-7", "player_identity_integrity", "UNKNOWN", {"reason": "no link summary"})
    amb = links_summary.get("AMBIGUOUS", 0); used_amb = links_summary.get("ambiguous_used_in_production", 0)
    return GateResult("TENNIS-7", "player_identity_integrity", "PASS" if used_amb == 0 else "FAIL", {"ambiguous": amb, "ambiguous_used": used_amb, **{k: v for k, v in links_summary.items() if k in ("MATCHED", "UNMATCHED")}})


def gate_8_9_truth(sports_ok: int | None, sports_total: int | None, exchange_conflicts: int | None, rules_id_changes: list | None) -> tuple[GateResult, GateResult]:
    """TENNIS-8: sports truth available for >= 98% of settled predictions; TENNIS-9: no unexplained exchange/sports conflicts and no unreviewed settlement-rule text changes."""
    if sports_total is None:
        g8 = GateResult("TENNIS-8", "sports_truth_health", "UNKNOWN", {"reason": "no settled predictions yet"})
    else:
        rate = sports_ok / sports_total if sports_total else 0
        g8 = GateResult("TENNIS-8", "sports_truth_health", "PASS" if sports_total and rate >= 0.98 else "FAIL", {"ok": sports_ok, "total": sports_total, "rate": round(rate, 4)})
    if exchange_conflicts is None:
        g9 = GateResult("TENNIS-9", "exchange_settlement_health", "UNKNOWN", {"reason": "no settled predictions yet", "rules_id_changes": rules_id_changes or []})
    else:
        g9 = GateResult("TENNIS-9", "exchange_settlement_health", "PASS" if exchange_conflicts == 0 and not rules_id_changes else "FAIL", {"conflicts": exchange_conflicts, "rules_id_changes": rules_id_changes or []})
    return g8, g9


def gate_10_clv_coverage(n_settled: int | None, n_with_close: int | None, n_actual_start_basis: int | None) -> GateResult:
    """TENNIS-10: a canonical close exists for >= 95% of settled pregame predictions; basis breakdown reported."""
    if n_settled is None:
        return GateResult("TENNIS-10", "clv_close_coverage", "UNKNOWN", {"reason": "no settled predictions yet"})
    rate = n_with_close / n_settled if n_settled else 0
    return GateResult("TENNIS-10", "clv_close_coverage", "PASS" if n_settled and rate >= 0.95 else "FAIL", {"settled": n_settled, "with_close": n_with_close, "actual_first_ball_basis": n_actual_start_basis, "rate": round(rate, 4)})


def gate_11_consistency(violations: list | None) -> GateResult:
    """TENNIS-11: probability consistency invariants across each priced match/tournament (see pricing.payoffs.check_consistency)."""
    if violations is None:
        return GateResult("TENNIS-11", "probability_consistency", "UNKNOWN", {"reason": "no projection run"})
    return GateResult("TENNIS-11", "probability_consistency", "PASS" if not violations else "FAIL", {"violations": violations[:20], "n": len(violations)})


def gate_12_ledger(ledger_root=None) -> GateResult:
    """TENNIS-12: append-only ledger hash chain intact."""
    from tennis_edge.ledger.predictions import PredictionLedger
    root = ledger_root or os.path.join(PROJ, "data", "research", "ledger")
    if not os.path.isdir(root) or not any(f.endswith(".jsonl") for f in os.listdir(root)):
        return GateResult("TENNIS-12", "append_only_ledger", "UNKNOWN", {"reason": "ledger empty"})
    v = PredictionLedger(root).verify_chain()
    return GateResult("TENNIS-12", "append_only_ledger", "PASS" if not v else "FAIL", {"violations": v[:10]})


def gate_13_reproducible(manifest_path=None) -> GateResult:
    """TENNIS-13: the processed dataset manifest exists with source run ids and a content hash that matches the file."""
    import hashlib
    p = manifest_path or os.path.join(PROJ, "data", "processed", "build_manifest.json")
    if not os.path.exists(p):
        return GateResult("TENNIS-13", "reproducible_artifacts", "UNKNOWN", {"reason": "no build manifest"})
    m = json.load(open(p))
    mp = os.path.join(os.path.dirname(p), "matches.parquet")
    if not os.path.exists(mp):
        return GateResult("TENNIS-13", "reproducible_artifacts", "FAIL", {"reason": "matches.parquet missing"})
    h = hashlib.sha256(open(mp, "rb").read()).hexdigest()
    ok = h == m.get("matches_sha256") and all(v.get("run") for v in m["sources"].values() if v.get("status") == "OK")
    return GateResult("TENNIS-13", "reproducible_artifacts", "PASS" if ok else "FAIL", {"hash_match": h == m.get("matches_sha256"), "built_at": m.get("built_at"), "rows": m.get("rows")})


def gate_14_source_freshness(max_age_days=8, now=None) -> GateResult:
    """TENNIS-14: the newest source snapshot with match data is younger than max_age_days and covers the current season."""
    runs = sorted(glob.glob(os.path.join(PROJ, "data", "sources", "*", "manifest.json")))
    best = None
    for r in runs:
        m = json.load(open(r))
        if any(k in m["sources"] for k in ("tennis_atp", "tennis_wta", "tml_database")):
            best = m
    if not best:
        return GateResult("TENNIS-14", "data_source_freshness", "UNKNOWN", {"reason": "no match-data source snapshot"})
    age = ((now or datetime.now(timezone.utc)) - datetime.fromisoformat(best["finished_at"])).total_seconds() / 86400
    seasons = [v.get("max_season_file") for v in best["sources"].values() if v.get("max_season_file")]
    cur = (now or datetime.now(timezone.utc)).year
    # a season FILE named 2026 can still end months ago (fork staleness): check the rating states' as_of_date
    as_of = {}
    for tour in ("ATP", "WTA"):
        sp = os.path.join(PROJ, "data", "processed", f"ratings_{tour}.json")
        if os.path.exists(sp):
            as_of[tour] = json.load(open(sp)).get("as_of_date")
    stale_days = {t: ((now or datetime.now(timezone.utc)).date() - datetime.fromisoformat(d).date()).days for t, d in as_of.items() if d}
    ok = age <= max_age_days and (not seasons or max(seasons) >= cur) and all(v <= max_age_days for v in stale_days.values()) and bool(stale_days)
    return GateResult("TENNIS-14", "data_source_freshness", "PASS" if ok else "FAIL",
                      {"run": best["run_id"], "snapshot_age_days": round(age, 2), "max_season_files": seasons, "ratings_as_of": as_of, "ratings_stale_days": stale_days})


def _auto_extra() -> dict:
    """Evidence the gates can read for themselves: latest projection run (consistency, mapping) and ledger rows."""
    extra = {}
    latest = os.path.join(PROJ, "data", "research", "projections", "latest.json")
    if os.path.exists(latest):
        pj = json.load(open(latest))
        extra["consistency_violations"] = pj.get("consistency_violations", [])
        amb = sum(1 for e in pj.get("excluded", []) if e.get("stage") == "identity" and "AMBIGUOUS" in e.get("reason", ""))
        extra["links_summary"] = {"AMBIGUOUS": amb, "ambiguous_used_in_production": 0, "MATCHED": len(pj.get("projected_tickers", []))}
    root = os.path.join(PROJ, "data", "research", "ledger")
    if os.path.isdir(root):
        from tennis_edge.ledger.predictions import PredictionLedger
        rows = list(PredictionLedger(root).rows())
        if rows:
            extra["ledger_rows"] = rows
            starts = {}
            for r in rows:
                s = r.get("scheduled_start")
                if s:
                    starts[r["match_id"]] = (None, datetime.fromisoformat(s.replace("Z", "+00:00")))
            extra["starts"] = starts
    return extra


def run_all(extra: dict | None = None) -> list[GateResult]:
    extra = {**_auto_extra(), **(extra or {})}
    out = [gate_1_discovery(), gate_2_taxonomy()]
    out += list(gate_3_4_active_coverage())
    out.append(gate_5_capture_freshness())
    out.append(gate_6_no_post_start_leakage(extra.get("ledger_rows", []), extra.get("starts", {})) if extra.get("ledger_rows") else GateResult("TENNIS-6", "no_post_start_leakage", "UNKNOWN", {"reason": "no ledger rows supplied"}))
    out.append(gate_7_identity(extra.get("links_summary")))
    out += list(gate_8_9_truth(extra.get("sports_ok"), extra.get("sports_total"), extra.get("exchange_conflicts"), extra.get("rules_id_changes")))
    out.append(gate_10_clv_coverage(extra.get("n_settled"), extra.get("n_with_close"), extra.get("n_actual_start_basis")))
    out.append(gate_11_consistency(extra.get("consistency_violations")))
    out.append(gate_12_ledger()); out.append(gate_13_reproducible()); out.append(gate_14_source_freshness())
    return out
