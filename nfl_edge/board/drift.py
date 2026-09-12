"""Discovery -> registry drift report.

    NEW_SERIES             NFL-candidate series in the discovery run that the reviewed registry does not hold
    NEW_MARKET_STRUCTURES  (family, strike_type, custom-strike keys) combinations never seen in the fixture corpus
                           or whose question parse is AMBIGUOUS / UNKNOWN on a family the catalog calls PROVEN
    UNCLASSIFIED           series whose family is UNKNOWN_NEEDS_CLASSIFICATION
    REGISTRY_LAG           days between a series' first discovery appearance and now, while absent from the registry
    CAPTURE_GAP            open contracts (and their series) that no capture run has ever confirmed open
"""
from __future__ import annotations

import glob
import json
import os
from collections import Counter, defaultdict
from datetime import datetime, timezone

from nfl_edge.kalshi.classifier import NOT_NFL_PREFIXES, classify
from nfl_edge.semantics.catalog import catalog_entry
from nfl_edge.semantics.questions import PROVEN, contract_question

# the registry builder's NFL membership rule, re-used here so drift and registry agree on what "NFL" means
try:
    from scripts.kalshi.build_series_registry import COLLEGE_COACH, EXCLUDE_PREFIX, NFL_TITLE_RE
except Exception:  # pragma: no cover - scripts may not be importable as a package in every context
    COLLEGE_COACH, EXCLUDE_PREFIX, NFL_TITLE_RE = (), NOT_NFL_PREFIXES, None


def is_nfl_series(s: dict) -> tuple[bool, str]:
    t = s.get("ticker") or ""
    tags = s.get("tags") or []
    if t.startswith(EXCLUDE_PREFIX) or t in COLLEGE_COACH:
        return False, "excluded prefix (college / other sport / unrelated)"
    if t.startswith("KXNFL"):
        return True, "KXNFL prefix"
    if ("Football" in tags) and NFL_TITLE_RE is not None and NFL_TITLE_RE.search(s.get("title") or ""):
        return True, "Football tag + NFL title"
    if t.startswith(("KXSB", "KXSUPERBOWL", "KXPERFORMSUPERBOWL", "KXHALFTIMESHOW", "KXLEADERNFL", "KXLEADERPINT", "KXNEXTTEAMNFL",
                     "KXTRADEOFFNFL", "KXCOACHOUTNFL", "KXNEXTCOACHOUTNFL", "KXNEXTNFLCOACH", "KXWPMOTY", "KXSTARTINGQBWEEK1",
                     "KXTEAMSINSB", "KXNFCAFCSB")) and not t.startswith(("KXAFC", "KXNFC")):
        return True, "known NFL prefix"
    if t in ("KXAFC", "KXNFC"):
        return True, "conference series"
    return False, "no NFL evidence"


def load_discovery(discovery_dir: str) -> dict:
    series_nfl = json.load(open(os.path.join(discovery_dir, "series_nfl.json")))
    summary = json.load(open(os.path.join(discovery_dir, "summary.json")))
    markets = {}
    for f in sorted(glob.glob(os.path.join(discovery_dir, "markets", "*.json"))):
        markets[os.path.basename(f)[:-5]] = json.load(open(f))
    return {"run_id": summary.get("run_id"), "finished_at": summary.get("finished_at"), "series_nfl": series_nfl,
            "summary": summary, "markets": markets, "dir": discovery_dir}


def first_seen_index(discovery_root: str) -> dict:
    """series ticker -> first discovery run (from the series_nfl.json of every run under the root)."""
    out = {}
    for d in sorted(glob.glob(os.path.join(discovery_root, "*"))):
        p = os.path.join(d, "series_nfl.json")
        if not os.path.isfile(p):
            continue
        run = os.path.basename(d)
        try:
            for s in json.load(open(p)):
                out.setdefault(s.get("ticker"), run)
        except (ValueError, OSError):
            continue
    return out


def _run_to_dt(run_id: str):
    try:
        return datetime.strptime(run_id, "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def drift_report(disc: dict, registry_series: dict, *, capture_state: dict | None = None, first_seen: dict | None = None,
                 known_structures: set | None = None, now: datetime | None = None) -> dict:
    now = now or datetime.now(timezone.utc)
    seen_tickers = set()
    if capture_state:
        seen_tickers = set((capture_state.get("last_seen") or {}).keys()) | set((capture_state.get("fingerprints") or {}).keys())
    new_series, unclassified, lag, capture_gap = [], [], [], []
    structures = Counter()
    new_structures = []
    per_series_open = {}
    for s in disc["series_nfl"]:
        t = s.get("ticker")
        nfl, why = is_nfl_series(s)
        mk = disc["markets"].get(t) or {}
        n_open = (mk.get("open") or {}).get("n", 0)
        per_series_open[t] = n_open
        if not nfl:
            continue
        fam = classify({"ticker": f"{t}-X-Y", "event_ticker": f"{t}-X", "series_ticker": t}).family
        if fam in ("UNKNOWN_NEEDS_CLASSIFICATION", "NOT_NFL_OR_UNKNOWN"):
            unclassified.append({"series": t, "title": s.get("title"), "open_markets": n_open})
        if t not in registry_series:
            fs = (first_seen or {}).get(t)
            fs_dt = _run_to_dt(fs) if fs else None
            days = round((now - fs_dt).total_seconds() / 86400.0, 1) if fs_dt else None
            new_series.append({"series": t, "title": s.get("title"), "family": fam, "open_markets": n_open, "first_seen_run": fs,
                               "registry_lag_days": days, "tags": s.get("tags"), "evidence": why})
            if n_open:
                lag.append({"series": t, "open_markets": n_open, "registry_lag_days": days})
        # structures and capture gap over the OPEN markets
        gap_here = 0
        for m in (mk.get("open") or {}).get("markets", []):
            sem = classify(m)
            cs = m.get("custom_strike")
            keys = tuple(sorted(cs.keys())) if isinstance(cs, dict) else ()
            structures[(sem.family, m.get("strike_type"), keys)] += 1
            q = contract_question(sem, m)
            e = catalog_entry(sem.family, sem.period, sem.stat)
            if e is not None and e.semantic_confidence == PROVEN and q.semantic_confidence != PROVEN:
                new_structures.append({"ticker": m.get("ticker"), "family": sem.family, "period": sem.period, "strike_type": m.get("strike_type"),
                                       "custom_strike_keys": list(keys), "parse": q.semantic_confidence, "notes": list(q.notes)[:3]})
            if capture_state is not None and m.get("ticker") not in seen_tickers:
                gap_here += 1
        if capture_state is not None and gap_here:
            capture_gap.append({"series": t, "open_markets": n_open, "never_confirmed_open": gap_here,
                                "in_registry": t in registry_series, "tier": (registry_series.get(t) or {}).get("tier")})
    unseen_structures = []
    if known_structures is not None:
        for (fam, st, keys), n in structures.items():
            if (fam, st, keys) not in known_structures:
                unseen_structures.append({"family": fam, "strike_type": st, "custom_strike_keys": list(keys), "n": n})
    return {"discovery_run": disc.get("run_id"), "generated_at": now.isoformat(),
            "registry_series": len(registry_series), "nfl_candidate_series": len(disc["series_nfl"]),
            "NEW_SERIES": sorted(new_series, key=lambda r: -r["open_markets"]),
            "NEW_MARKET_STRUCTURES": {"unparsed_on_proven_families": new_structures[:200],
                                      "n_unparsed_on_proven_families": len(new_structures),
                                      "structures_not_in_fixture_corpus": sorted(unseen_structures, key=lambda r: -r["n"])},
            "UNCLASSIFIED": sorted(unclassified, key=lambda r: -r["open_markets"]),
            "REGISTRY_LAG": sorted(lag, key=lambda r: -(r["registry_lag_days"] or 0)),
            "CAPTURE_GAP": sorted(capture_gap, key=lambda r: -r["never_confirmed_open"]),
            "totals": {"new_series": len(new_series), "new_series_open_markets": sum(r["open_markets"] for r in new_series),
                       "unclassified_series": len(unclassified), "capture_gap_contracts": sum(r["never_confirmed_open"] for r in capture_gap),
                       "capture_gap_contracts_outside_registry": sum(r["never_confirmed_open"] for r in capture_gap if not r["in_registry"])}}


def known_structures_from_fixture(path: str) -> set:
    """(family, strike_type, custom-strike keys) triples present in the real-market fixture corpus."""
    out = set()
    for m in json.load(open(path)):
        sem = classify(m)
        cs = m.get("custom_strike")
        keys = tuple(sorted(cs.keys())) if isinstance(cs, dict) else ()
        out.add((sem.family, m.get("strike_type"), keys))
    return out


def render_drift(rep: dict) -> str:
    L = [f"# Discovery -> registry drift ({rep['discovery_run']})", "",
         f"Registry holds {rep['registry_series']} series; discovery lists {rep['nfl_candidate_series']} NFL candidates.", "",
         "| quantity | n |", "|---|---|"]
    for k, v in rep["totals"].items():
        L.append(f"| {k} | {v} |")
    L += ["", "## NEW_SERIES (not in the reviewed registry)", "", "| series | family | open | first seen | lag (days) | title |", "|---|---|---|---|---|---|"]
    for r in rep["NEW_SERIES"][:60]:
        L.append(f"| {r['series']} | {r['family']} | {r['open_markets']} | {r['first_seen_run']} | {r['registry_lag_days']} | {(r['title'] or '')[:60]} |")
    L += ["", "## UNCLASSIFIED", "", "| series | open | title |", "|---|---|---|"]
    for r in rep["UNCLASSIFIED"]:
        L.append(f"| {r['series']} | {r['open_markets']} | {(r['title'] or '')[:70]} |")
    L += ["", "## CAPTURE_GAP (open contracts never confirmed open by any capture run)", "", "| series | open | never seen | in registry | tier |", "|---|---|---|---|---|"]
    for r in rep["CAPTURE_GAP"][:60]:
        L.append(f"| {r['series']} | {r['open_markets']} | {r['never_confirmed_open']} | {r['in_registry']} | {r['tier']} |")
    ns = rep["NEW_MARKET_STRUCTURES"]
    L += ["", f"## NEW_MARKET_STRUCTURES: {ns['n_unparsed_on_proven_families']} contracts on PROVEN families did not parse PROVEN", ""]
    for r in ns["unparsed_on_proven_families"][:20]:
        L.append(f"* {r['ticker']} ({r['family']}/{r['period']}, {r['strike_type']}): {r['parse']} {r['notes']}")
    if ns["structures_not_in_fixture_corpus"]:
        L += ["", "Structures absent from the fixture corpus:", ""]
        for r in ns["structures_not_in_fixture_corpus"][:30]:
            L.append(f"* {r['family']} / {r['strike_type']} / {r['custom_strike_keys']}: {r['n']}")
    return "\n".join(L)
