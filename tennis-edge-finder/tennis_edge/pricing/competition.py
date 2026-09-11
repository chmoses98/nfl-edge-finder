"""Infer level / competition / surface / format for a Kalshi match market from its competition text.

Kalshi gives e.g. "US Open Men Singles", "ATP Challenger Seville", "M15 Budapest", "W35 Zhengzhou",
"ATP Cincinnati", "WTA Cincinnati", "Wimbledon Women Singles", "United Cup", "Davis Cup". Surface is NOT in
the exchange data: it is looked up from the canonical match table (tournament name -> surface for the
current/previous season) with a static table for the majors and 1000s; unknown surface is flagged and the
Elo surface blend is disabled for that match (overall rating only).
"""
from __future__ import annotations

import re
from tennis_edge.identity.names import normalize_name

SLAMS = {"australian open": ("AUSTRALIAN_OPEN", "Hard"), "french open": ("ROLAND_GARROS", "Clay"), "roland garros": ("ROLAND_GARROS", "Clay"),
         "wimbledon": ("WIMBLEDON", "Grass"), "us open": ("US_OPEN", "Hard")}
MASTERS = {"indian wells": "Hard", "miami": "Hard", "monte carlo": "Clay", "monte-carlo": "Clay", "madrid": "Clay", "rome": "Clay", "italian open": "Clay",
           "canada": "Hard", "montreal": "Hard", "toronto": "Hard", "cincinnati": "Hard", "shanghai": "Hard", "paris": "Hard", "beijing": "Hard", "wuhan": "Hard",
           "dubai": "Hard", "doha": "Hard", "qatar": "Hard"}


def classify_competition(comp: str, tour_hint: str) -> dict:
    """Return {level, competition, discipline, surface_hint, tour}."""
    c = (comp or "").strip(); low = c.lower()
    tour = tour_hint
    discipline = "doubles" if "doubles" in low else "singles"
    if "mixed" in low:
        discipline = "mixed"
    if "women" in low or low.startswith("wta") or low.startswith("w1") or low.startswith("w2") or low.startswith("w3") or low.startswith("w4") or low.startswith("w5") or low.startswith("w6") or low.startswith("w7") or low.startswith("w8") or low.startswith("w9") or low.startswith("w100"):
        tour = "WTA"
    if "men" in low and "women" not in low or low.startswith("atp") or re.match(r"^m\d{2}", low):
        tour = "ATP"
    for k, (name, surf) in SLAMS.items():
        if k in low:
            return {"level": "GRAND_SLAM", "competition": name, "discipline": discipline, "surface_hint": surf, "tour": tour}
    if "challenger" in low:
        return {"level": "CHALLENGER", "competition": c, "discipline": discipline, "surface_hint": None, "tour": "ATP"}
    if re.match(r"^[mw]\d{2,3}\b", low):
        return {"level": "ITF", "competition": c, "discipline": discipline, "surface_hint": None, "tour": "WTA" if low.startswith("w") else "ATP"}
    if "125" in low:
        return {"level": "WTA_125", "competition": c, "discipline": discipline, "surface_hint": None, "tour": "WTA"}
    if any(k in low for k in ("davis cup", "united cup", "billie jean", "bjk cup", "laver cup", "hopman")):
        return {"level": "TEAM", "competition": c, "discipline": discipline, "surface_hint": None, "tour": tour}
    if "finals" in low and ("atp" in low or "wta" in low or "nitto" in low):
        return {"level": "TOUR_FINALS", "competition": c, "discipline": discipline, "surface_hint": "Hard", "tour": tour}
    if "olympic" in low:
        return {"level": "OLYMPICS", "competition": c, "discipline": discipline, "surface_hint": None, "tour": tour}
    for k, surf in MASTERS.items():
        if k in low:
            return {"level": "MASTERS_1000", "competition": c, "discipline": discipline, "surface_hint": surf, "tour": tour}
    if any(k in low for k in ("exhibition", "six kings", "battle of the sexes")):
        return {"level": "OTHER", "competition": c, "discipline": discipline, "surface_hint": None, "tour": tour}
    return {"level": "TOUR_500_250", "competition": c, "discipline": discipline, "surface_hint": None, "tour": tour}


def build_surface_lookup(matches) -> dict:
    """{normalised tournament name: surface} from the two most recent seasons of the canonical table (most common surface)."""
    m = matches[matches.season >= matches.season.max() - 1]
    out = {}
    for name, g in m.groupby("tourney_name"):
        s = g["surface"].dropna()
        if len(s):
            out[normalize_name(name)] = s.mode().iloc[0]
    return out


def lookup_surface(comp: str, hint: str | None, lookup: dict) -> tuple[str | None, str]:
    if hint:
        return hint, "static"
    low = normalize_name(re.sub(r"\b(atp|wta|challenger|men|women|singles|doubles|m\d{2,3}|w\d{2,3})\b", " ", (comp or "").lower()))
    toks = [t for t in low.split() if len(t) > 2]
    for name, surf in lookup.items():
        if toks and all(t in name for t in toks):
            return surf, f"table:{name}"
    for name, surf in lookup.items():
        if toks and any(t in name.split() for t in toks):
            return surf, f"table_partial:{name}"
    return None, "unknown"
