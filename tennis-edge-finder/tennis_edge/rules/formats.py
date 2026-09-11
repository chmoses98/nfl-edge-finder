"""Match-format definitions (the rules engine's data model).

Tennis scoring is NOT universal. A format pins down everything the scoring engine needs:

  * best_of            3 or 5 sets
  * tiebreak_at        games score at which a tiebreak is played in a NON-final set (6 -> at 6-6);
                       None means advantage set (must win by two games)
  * tiebreak_to        points to win that tiebreak (7)
  * final_set          how the deciding set ends:
        'TB7_AT_6'      standard 7-point tiebreak at 6-6 (US Open historically; ATP/WTA tour)
        'TB10_AT_6'     10-point tiebreak at 6-6 (all Grand Slams since 2022; AO 2019-2021)
        'TB7_AT_12'     7-point tiebreak at 12-12 (Wimbledon 2019-2021)
        'ADVANTAGE'     play on until two games clear (Roland Garros <=2021, Wimbledon <=2018, AO <=2018, Davis Cup <=2018)
        'MATCH_TB10'    NO third set: a 10-point match tiebreak replaces the deciding set (tour doubles since 2006,
                        many exhibitions, mixed doubles at slams, Laver Cup)
  * no_ad              deuce is decided by one sudden-death point (tour doubles, some exhibitions, NCAA)
  * short_sets / other exotic scoring is NOT modelled; a format the registry cannot resolve is a hard failure
    (fail closed), never a silent fallback to best-of-3.

The registry `resolve_format(tour, level, year, competition=None, discipline='singles')` is DATA-DRIVEN from
config/formats.json so a rule change is a config edit with a dated entry, not a code change.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, asdict

FINAL_SET_KINDS = {"TB7_AT_6", "TB10_AT_6", "TB7_AT_12", "ADVANTAGE", "MATCH_TB10"}


@dataclass(frozen=True)
class MatchFormat:
    best_of: int = 3
    tiebreak_at: int | None = 6
    tiebreak_to: int = 7
    final_set: str = "TB7_AT_6"
    no_ad: bool = False
    name: str = "tour_singles_bo3"

    def __post_init__(self):
        if self.best_of not in (3, 5):
            raise ValueError(f"best_of must be 3 or 5, got {self.best_of}")
        if self.final_set not in FINAL_SET_KINDS:
            raise ValueError(f"unknown final_set kind {self.final_set!r}")
        if self.tiebreak_at is not None and self.tiebreak_at < 1:
            raise ValueError("tiebreak_at must be >= 1 or None")

    @property
    def sets_to_win(self) -> int:
        return self.best_of // 2 + 1

    @property
    def final_set_index(self) -> int:
        """1-based index of the deciding set (3 for bo3, 5 for bo5)."""
        return self.best_of

    def final_set_rule(self) -> tuple[int | None, int]:
        """(tiebreak_at, tiebreak_to) for the deciding set, or (None, 0) for advantage."""
        return {"TB7_AT_6": (6, 7), "TB10_AT_6": (6, 10), "TB7_AT_12": (12, 7), "ADVANTAGE": (None, 0),
                "MATCH_TB10": (0, 10)}[self.final_set]

    def to_dict(self):
        return asdict(self)


# Canonical named formats -------------------------------------------------------------------------
TOUR_SINGLES_BO3 = MatchFormat(3, 6, 7, "TB7_AT_6", False, "tour_singles_bo3")
SLAM_MEN_2022 = MatchFormat(5, 6, 7, "TB10_AT_6", False, "slam_men_bo5_tb10")
SLAM_WOMEN_2022 = MatchFormat(3, 6, 7, "TB10_AT_6", False, "slam_women_bo3_tb10")
TOUR_DOUBLES = MatchFormat(3, 6, 7, "MATCH_TB10", True, "tour_doubles_noad_matchtb")
SLAM_DOUBLES_MEN_BO3_TB10 = MatchFormat(3, 6, 7, "TB10_AT_6", False, "slam_doubles_bo3_tb10")

_REGISTRY_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "config", "formats.json")


class FormatResolutionError(LookupError):
    pass


def _load_registry(path: str = _REGISTRY_PATH) -> list[dict]:
    with open(path) as f:
        return json.load(f)["rules"]


def resolve_format(tour: str, level: str, year: int, competition: str | None = None,
                   discipline: str = "singles", registry: list[dict] | None = None) -> MatchFormat:
    """Resolve the scoring format in force for (tour, level, year, competition, discipline).

    Rules are evaluated in file order; the first rule whose selectors all match wins. Selectors:
      tour (ATP/WTA/*), discipline (singles/doubles/mixed/*), level (canonical level or *),
      competition (slam name like AUSTRALIAN_OPEN or *), year_from/year_to inclusive.
    Raises FormatResolutionError when nothing matches: pricing an unknown format is forbidden.
    """
    rules = registry if registry is not None else _load_registry()
    for r in rules:
        if r.get("tour", "*") not in ("*", tour):
            continue
        if r.get("discipline", "*") not in ("*", discipline):
            continue
        if r.get("level", "*") not in ("*", level):
            continue
        if r.get("competition", "*") not in ("*", competition or ""):
            continue
        if year < r.get("year_from", 0) or year > r.get("year_to", 9999):
            continue
        f = r["format"]
        return MatchFormat(f["best_of"], f.get("tiebreak_at", 6), f.get("tiebreak_to", 7), f["final_set"],
                           f.get("no_ad", False), r.get("name", "registry"))
    raise FormatResolutionError(f"no format rule for tour={tour} level={level} year={year} competition={competition} discipline={discipline}")
