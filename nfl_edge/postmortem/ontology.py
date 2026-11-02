"""Market ontology for owner contracts, including cross-category combos.

A Kalshi ``KXMVECROSSCATEGORY*`` contract is a multi-variate combo whose LEGS are not in its ticker. The prior
classifier saw no ``NFL`` in the series and the exposure code grouped it by the opaque event token, which is
wrong in both directions (it is not one game, and it correlates with games it was never linked to). Here a combo
is DECODED only from leg records the caller supplies; otherwise it is ``COMBO_UNDECODED`` with
``MISSING_COMBO_LEGS`` and is reported separately. Legs are never guessed from a ticker suffix.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field

from nfl_edge.kalshi.classifier import PERIOD_RE, SERIES_FAMILY

SINGLE = "SINGLE"
COMBO_DECODED = "COMBO_DECODED"
COMBO_UNDECODED = "COMBO_UNDECODED"
UNCLASSIFIED = "UNCLASSIFIED"

#: Families that settle on the final score and are therefore one "game thesis" for correlation purposes.
SCORE_FAMILIES = ("GAME_WINNER", "SPREAD", "TOTAL", "TEAM_TOTAL")

_EVENT = re.compile(r"^(\d{2}[A-Z]{3}\d{2})([A-Z]+)$")
_COMBO = re.compile(r"^KXMVE[A-Z0-9]*$")


@dataclass(frozen=True)
class Leg:
    ticker: str
    side: str
    ontology: "ContractOntology"


@dataclass(frozen=True)
class ContractOntology:
    ticker: str
    series: str
    kind: str
    family: str | None = None
    period: str | None = None
    game_key: str | None = None          # e.g. 25OCT25SFATL; None for combos and anything without one game
    date_token: str | None = None        # 25OCT25
    teams_token: str | None = None       # SFATL
    subject: str | None = None           # SF3 / ATL20 / player token
    legs: tuple = ()
    flags: tuple = field(default_factory=tuple)

    @property
    def is_score_thesis(self) -> bool:
        return self.kind == SINGLE and self.family in SCORE_FAMILIES

    @property
    def games(self) -> tuple:
        if self.kind == COMBO_DECODED:
            return tuple(sorted({g for leg in self.legs if (g := leg.ontology.game_key)}))
        return (self.game_key,) if self.game_key else ()


def _series_info(series: str):
    m = PERIOD_RE.match(series)
    if m:
        period, kind = m.group(1), m.group(2) or "WINNER"
        fam = {"WINNER": "GAME_WINNER", "SPREAD": "SPREAD", "TOTAL": "TOTAL", "TEAMTOTAL": "TEAM_TOTAL"}.get(kind, "PERIOD_OTHER")
        return fam, period
    row = SERIES_FAMILY.get(series)
    return (row[0], row[2]) if row else (None, None)


def classify_ticker(ticker: str | None, *, legs: list | None = None) -> ContractOntology:
    """``legs``: optional [{"ticker": ..., "side": "YES"|"NO"}] supplied from the router/exchange record. Used only
    for combos; a single-game contract ignores it."""
    t = (ticker or "").strip()
    if not t:
        return ContractOntology("", "", UNCLASSIFIED, flags=("MISSING_TICKER",))
    parts = t.split("-")
    series = parts[0]
    if _COMBO.match(series):
        if not legs:
            return ContractOntology(t, series, COMBO_UNDECODED, family="COMBO", flags=("MISSING_COMBO_LEGS",))
        out, flags = [], []
        for leg in legs:
            lt, ls = (leg or {}).get("ticker"), (leg or {}).get("side")
            if not lt or ls not in ("YES", "NO"):
                flags.append("MALFORMED_COMBO_LEG")
                continue
            sub = classify_ticker(lt)
            if sub.kind != SINGLE:
                flags.append("UNDECODABLE_COMBO_LEG")
            out.append(Leg(lt, ls, sub))
        kind = COMBO_DECODED if out and not flags else COMBO_UNDECODED
        return ContractOntology(t, series, kind, family="COMBO", legs=tuple(out),
                                flags=tuple(sorted(set(flags))) or (() if kind == COMBO_DECODED else ("MISSING_COMBO_LEGS",)))
    family, period = _series_info(series)
    if family is None:
        return ContractOntology(t, series, UNCLASSIFIED, flags=("SERIES_NOT_IN_TAXONOMY",))
    event = parts[1] if len(parts) > 1 else None
    m = _EVENT.match(event or "")
    subject = parts[2] if len(parts) > 2 else None
    return ContractOntology(t, series, SINGLE, family=family, period=period or "FULL",
                            game_key=event if m else None, date_token=m.group(1) if m else None,
                            teams_token=m.group(2) if m else None, subject=subject,
                            flags=() if m else ("NO_GAME_EVENT_TOKEN",))


def spread_team_and_line(ontology: ContractOntology):
    """('SF', 3.0) for a SPREAD subject like SF3 (team covers by MORE than the line). None when not parseable."""
    if ontology.family != "SPREAD" or not ontology.subject:
        return None
    m = re.match(r"^([A-Z]+?)(\d+(?:\.\d+)?)$", ontology.subject)
    return (m.group(1), float(m.group(2))) if m else None
