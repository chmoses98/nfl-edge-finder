"""Provisional classification of series the static taxonomy does not know.

The registry is reviewed config, and that is right: nothing should gain FULL tier or a pricing family without
a human reading the rules text. But "not reviewed yet" must not mean "not captured": the prior audit found
four series (KXNFLPOTM, KXNFLROTM, KXNFLFFPLAYOFFLEADER, KXNFLFFSEASONTOTAL) that discovery had listed for days
while capture, iterating the registry, never saw them.

This module gives every unknown NFL series a PROVISIONAL record:

    provisional_family     a family guess from the series title / product scope / ticker morphology, or
                           UNKNOWN_NEEDS_CLASSIFICATION when nothing matches -- never a pricing family
    tier                   the SAFE capture tier: LIGHT for series with open markets (quotes every run, no
                           books), DAILY otherwise. Never FULL_MICROSTRUCTURE.
    semantic_confidence    UNKNOWN, always. Provisional series are captured, never priced.
    reason                 the evidence that produced the guess

`capture.py` reads the provisional list alongside the registry (`provisional_series.json`, published by the
discovery job) so a new series is capturable the day after it appears; promotion into the registry stays a
reviewed edit of config/kalshi_nfl_series.json.
"""
from __future__ import annotations

import json
import os
import re
from datetime import datetime, timezone

from nfl_edge.kalshi.classifier import classify

PROVISIONAL_FILE = "provisional_series.json"
UNKNOWN = "UNKNOWN_NEEDS_CLASSIFICATION"

# (compiled pattern on "title | scope | ticker", provisional family, model support hint)
_RULES = [
    (re.compile(r"player of the (month|week)|rookie of the (month|week)|of the year|award|mvp|pro bowl|all-pro|hall of fame", re.I), "AWARD", "NON_FOOTBALL_MODEL"),
    (re.compile(r"fantasy", re.I), "SEASON_FANTASY", "RESEARCH_REQUIRED"),
    (re.compile(r"coach|coordinator", re.I), "COACH_EVENT", "NON_FOOTBALL_MODEL"),
    (re.compile(r"draft|combine", re.I), "DRAFT", "NON_FOOTBALL_MODEL"),
    (re.compile(r"trade|retire|contract|sign|next team|release", re.I), "TRANSACTION_EVENT", "NON_FOOTBALL_MODEL"),
    (re.compile(r"stadium|owner|viewership|ratings|attendance|sellout", re.I), "NFL_BUSINESS_EVENT", "NON_FOOTBALL_MODEL"),
    (re.compile(r"season (wins|record)|win total", re.I), "SEASON_WINS", "RESEARCH_REQUIRED"),
    (re.compile(r"leader|most (passing|rushing|receiving)", re.I), "SEASON_LEADER", "RESEARCH_REQUIRED"),
    (re.compile(r"playoff|seed|division|conference|super bowl|championship", re.I), "SEASON_TEAM_EVENT", "RESEARCH_REQUIRED"),
    (re.compile(r"touchdown|yards|receptions|completions|attempts|sacks|tackles|interceptions|field goal", re.I), "PLAYER_STAT_OR_TEAM_STAT", "RESEARCH_REQUIRED"),
]


def provisional_record(series: dict, open_markets: int, first_seen: str | None = None, now: datetime | None = None) -> dict:
    """One provisional registry record for an NFL-candidate series absent from the reviewed registry."""
    now = now or datetime.now(timezone.utc)
    t = series.get("ticker") or ""
    title = series.get("title") or ""
    scope = ((series.get("product_metadata") or {}).get("scope") or "") if isinstance(series.get("product_metadata"), dict) else ""
    text = f"{title} | {scope} | {t}"
    fam, support, evidence = UNKNOWN, "UNSUPPORTED", "no keyword matched"
    # the static taxonomy might already know it (a registry lag, not an unknown series)
    known = classify({"ticker": f"{t}-X-Y", "event_ticker": f"{t}-X", "series_ticker": t}).family
    if known not in (UNKNOWN, "NOT_NFL_OR_UNKNOWN", "NOT_NFL"):
        fam, support, evidence = known, "CATALOG", "static taxonomy knows the series; the registry lags discovery"
    else:
        for pat, f, s in _RULES:
            if pat.search(text):
                fam, support, evidence = f, s, f"keyword match on {pat.pattern!r}"
                break
    tier = "LIGHT" if open_markets > 0 else "DAILY"
    return {"ticker": t, "title": title, "product_scope": scope, "tags": series.get("tags"),
            "provisional_family": fam, "provisional_model_support": support, "semantic_confidence": "UNKNOWN",
            "tier": tier, "status": "PROVISIONAL", "open_markets_at_discovery": int(open_markets),
            "first_seen": first_seen or now.isoformat(), "last_seen": now.isoformat(), "evidence": evidence,
            "rule": "captured at a safe tier only; promotion to the reviewed registry requires reading the rules text"}


def merge_provisional(existing: dict | None, records: list, registry_series: dict, now: datetime | None = None) -> dict:
    """Append-only merge: a provisional series keeps its first_seen; one now in the registry is retired, never deleted."""
    now = now or datetime.now(timezone.utc)
    out = dict((existing or {}).get("series", {}))
    for r in records:
        prev = out.get(r["ticker"])
        if prev:
            r = {**r, "first_seen": prev.get("first_seen") or r["first_seen"]}
        out[r["ticker"]] = r
    for t, r in out.items():
        if t in registry_series and r.get("status") == "PROVISIONAL":
            r["status"] = "PROMOTED_TO_REGISTRY"
            r["promoted_at"] = now.isoformat()
    return {"generated_at": now.isoformat(), "series": dict(sorted(out.items())),
            "n_provisional": sum(1 for r in out.values() if r.get("status") == "PROVISIONAL")}


def load_provisional(path: str) -> dict:
    if not os.path.exists(path):
        return {"series": {}}
    return json.load(open(path))


def capturable_provisional(prov: dict, registry_series: dict) -> dict:
    """Series -> tier for capture: provisional and not in the reviewed registry."""
    return {t: r.get("tier", "LIGHT") for t, r in (prov or {}).get("series", {}).items()
            if r.get("status") == "PROVISIONAL" and t not in registry_series}
