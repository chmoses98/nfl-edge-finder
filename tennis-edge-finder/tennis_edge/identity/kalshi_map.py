"""Map Kalshi competitor names (full names in rules_primary, plus the exchange's competitor UUID) to canonical
player ids. Exact-normalised full-name match against the registry of a tour; ambiguous or absent -> UNMAPPED
(fail closed). Successful mappings are cached by competitor UUID in config/kalshi_competitor_map.json so a
player is resolved once and the cache is reviewable.

Confidence: 1.0 for a unique exact normalised full-name hit that also played in the last 24 months;
0.9 for a unique exact hit with no recent activity (could be a namesake); 0.0 otherwise.
"""
from __future__ import annotations

import json
import os
from datetime import date, timedelta

from tennis_edge.identity.names import normalize_name

PROJ = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CACHE = os.path.join(PROJ, "config", "kalshi_competitor_map.json")


class KalshiPlayerMapper:
    def __init__(self, states: dict, cache_path: str = CACHE):
        """states: {'ATP': ratings_state, 'WTA': ratings_state} (tennis_edge.models.state artifacts)."""
        self.index = {}
        for tour, st in states.items():
            idx = {}
            for pid, rec in st["players"].items():
                nm = normalize_name(rec.get("name") or "")
                if nm:
                    idx.setdefault(nm, []).append((pid, rec))
            self.index[tour] = idx
        self.cache_path = cache_path
        self.cache = json.load(open(cache_path)) if os.path.exists(cache_path) else {}

    def resolve(self, tour: str, full_name: str, competitor_id: str | None = None, today: date | None = None) -> dict:
        today = today or date.today()
        if competitor_id and competitor_id in self.cache and self.cache[competitor_id].get("tour") == tour:
            return dict(self.cache[competitor_id], source="cache")
        nm = normalize_name(full_name or "")
        hits = self.index.get(tour, {}).get(nm, [])
        if not hits:
            return {"status": "UNMAPPED", "reason": "no exact full-name match", "player_id": None, "confidence": 0.0, "name": full_name, "tour": tour}
        if len(hits) > 1:
            # prefer the single recently-active namesake; otherwise ambiguous
            recent = [(pid, r) for pid, r in hits if r.get("last_date") and r["last_date"] != "None" and date.fromisoformat(r["last_date"][:10]) >= today - timedelta(days=730)]
            if len(recent) != 1:
                return {"status": "AMBIGUOUS", "reason": f"{len(hits)} namesakes, {len(recent)} recently active", "player_id": None, "confidence": 0.0, "name": full_name, "tour": tour,
                        "candidates": [pid for pid, _ in hits]}
            hits = recent
        pid, rec = hits[0]
        active = rec.get("last_date") and rec["last_date"] != "None" and date.fromisoformat(rec["last_date"][:10]) >= today - timedelta(days=730)
        out = {"status": "MAPPED", "player_id": pid, "confidence": 1.0 if active else 0.9, "name": full_name, "tour": tour, "canonical_name": rec.get("name"), "last_date": rec.get("last_date")}
        if competitor_id:
            self.cache[competitor_id] = out
        return out

    def save_cache(self):
        os.makedirs(os.path.dirname(self.cache_path), exist_ok=True)
        json.dump(self.cache, open(self.cache_path, "w"), indent=1, sort_keys=True)
