"""Kalshi tennis series classification.

The exchange tags tennis series with the literal tag "Tennis" (verified from the full
`GET /series?include_product_metadata=true` catalogue snapshot of 2026-09-10, 13,959 series).
We classify by TAG first, then by title/ticker regex as a secondary net so that an untagged
tennis series is still surfaced -- as a coverage failure to review, never silently.

Tag "Tennis" also covers Pickleball (KXPICKLEBALLMATCH). It is kept in the discovered universe
(it IS a Kalshi 'tennis' contract by the exchange's own taxonomy) but flagged sport=pickleball
so the projection layer refuses it explicitly instead of pricing it as tennis.
"""
from __future__ import annotations

import re

TENNIS_TAG = "Tennis"
TENNIS_TITLE_RE = re.compile(
    r"\b(tennis|ATP|WTA|ITF|Wimbledon|Roland Garros|French Open|Australian Open|US Open|Grand Slam|"
    r"Davis Cup|Billie Jean King|United Cup|Laver Cup|Six Kings|Challenger|Indian Wells|Miami Open|"
    r"Monte[- ]Carlo|Madrid Open|Italian Open|Alcaraz|Sinner|Djokovic|Sabalenka|Swiatek)\b",
    re.I,
)
EXCLUDE_TITLE_RE = re.compile(r"\b(table tennis|ITTF|TT Elite|TT Star|golf|chess|squash|soccer|padel)\b", re.I)
PICKLEBALL_RE = re.compile(r"pickleball", re.I)
NON_TENNIS_TAGS = {"Table Tennis", "Golf", "Chess", "Squash", "Soccer", "Baseball", "Football", "Basketball", "Hockey", "Growth", "Music"}


def classify_series(s: dict) -> dict:
    """Return {'is_tennis': bool, 'sport': str, 'evidence': [...]} for a series record."""
    tags = s.get("tags") or []
    if not isinstance(tags, list):
        tags = [str(tags)]
    title = s.get("title") or ""
    ticker = s.get("ticker") or ""
    ev = []
    if TENNIS_TAG in tags:
        ev.append("tag_tennis")
    if TENNIS_TITLE_RE.search(title) and not EXCLUDE_TITLE_RE.search(title) and not (set(tags) & NON_TENNIS_TAGS):
        ev.append("title_tennis")
    if re.match(r"^KX(ATP|WTA|ITF)", ticker, re.I) and not (set(tags) & NON_TENNIS_TAGS):
        ev.append("ticker_prefix")
    sport = "tennis"
    if PICKLEBALL_RE.search(title) or PICKLEBALL_RE.search(ticker):
        sport = "pickleball"
    non_tennis_tag = bool(set(tags) & NON_TENNIS_TAGS)
    # Tag is authoritative. Without the tag we require the Sports category AND no conflicting tag, so
    # "Wealth tax" (KXWTAX) and "Pro baseball wins Cincinnati" never enter the tennis universe; an
    # untagged Sports series with a tennis title/prefix is surfaced for review (evidence lacks tag_tennis).
    is_tennis = "tag_tennis" in ev or (s.get("category") == "Sports" and not non_tennis_tag and ("ticker_prefix" in ev or "title_tennis" in ev))
    return {"is_tennis": is_tennis, "sport": sport if is_tennis else None, "evidence": ev}


def tennis_series(series: list[dict]) -> list[dict]:
    out = []
    for s in series:
        c = classify_series(s)
        if c["is_tennis"]:
            out.append({**s, "_classification": c})
    out.sort(key=lambda s: s.get("ticker") or "")
    return out
