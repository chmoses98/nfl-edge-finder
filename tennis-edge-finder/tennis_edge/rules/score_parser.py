"""Robust parsing of tennis score strings into structured set/game data.

Why this exists
---------------
Every upstream source encodes results as free text ("7-6(5) 3-6 6-3", "6-3 RET",
"W/O", "Played and unfinished", ...).  Downstream modules (ratings, simulators,
market pricing) need clean integers plus an *outcome type* so that walkovers,
retirements and unfinished matches are handled explicitly rather than being
mistaken for straight-sets wins.  Centralising the parsing here means the
edge cases are enumerated once and covered by tests once.

Winner-first convention
-----------------------
``winner_is_first`` documents the assumption baked into the parse: Sackmann
(and tennis-data) write the score from the *match winner's* perspective, so the
first number of every set belongs to the winner.  A set like ``3-6`` therefore
means the winner *lost* that set 3-6.  Sets/games are accumulated under this
assumption; a source that writes scores player-A-first would need to swap the
tuples before interpreting ``sets_w``/``sets_l``.

Validity rules (what counts as IMPOSSIBLE)
------------------------------------------
* A set is *complete* when one side has 6 with the other <= 4, or 7 with the
  other 5 or 6 (7-6 implies a tiebreak), or >7 with a margin of exactly 2
  (old-style advantage final sets, e.g. 8-6, 70-68) -> ``advantage_set``.
* Tiebreak detail in parentheses is only legal on a 7-6 set (or a 6-6 set
  still in progress when the match was cut short).
* ``[10-8]`` bracket = match tiebreak (super tiebreak replacing a final set):
  counts as a *set* but contributes no games.
* Any incomplete set (6-5, 2-1, 6-6, 0-0) is legal only as the *last* set of a
  match that ended RET / DEF / UNFINISHED.  Otherwise the score is impossible.
* A COMPLETED match must end exactly when the winner reaches the target number
  of sets (2 or 3); superfluous or missing sets are impossible.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from typing import Optional

log = logging.getLogger(__name__)

# --- outcome vocabulary -------------------------------------------------------
COMPLETED = "COMPLETED"
RETIRED = "RETIRED"
WALKOVER = "WALKOVER"
DEFAULT = "DEFAULT"
UNFINISHED = "UNFINISHED"
UNKNOWN = "UNKNOWN"
OUTCOME_TYPES = (COMPLETED, RETIRED, WALKOVER, DEFAULT, UNFINISHED, UNKNOWN)

# Status tokens, longest/most specific first so that e.g. "played and unfinished"
# is consumed before the bare word "unfinished".  Matched case-insensitively
# against the lowercased, whitespace-collapsed score.
_STATUS_PATTERNS: tuple[tuple[str, str], ...] = (
    (r"played\s+and\s+(?:unfinished|abandoned)", UNFINISHED),
    (r"in\s+progress", UNFINISHED),
    (r"\bunfinished\b", UNFINISHED),
    (r"\babandoned\b", UNFINISHED),
    (r"\babn\b|\babd\b", UNFINISHED),
    (r"\(?\bretired\b\)?|\bret'?d?\.?(?=\s|$)", RETIRED),
    (r"\bwalkover\b|\bw/o\b|\bwo\b|\bw\.o\.?", WALKOVER),
    (r"\bdefault(?:ed)?\b|\bdef\.?(?=\s|$)|\bdisq(?:ualified)?\b|\bdq\b", DEFAULT),
    (r"\bunp\b|\bunk\b|\bunknown\b", UNKNOWN),
)

# "6-4", "7-6(5)", "7-6(11-9)", "6-6(3)" -- optional tiebreak detail.
_SET_RE = re.compile(r"^(\d{1,3})-(\d{1,3})(?:\((\d{1,3})(?:-(\d{1,3}))?\))?$")
# "[10-8]" -- match tiebreak.
_MTB_RE = re.compile(r"^\[(\d{1,3})-(\d{1,3})\]$")


@dataclass(frozen=True)
class ScoreParse:
    """Structured result of parsing one score string.

    ``set_scores`` are (winner_games, loser_games) tuples in playing order
    (match tiebreaks included as e.g. (10, 8) with a matching ``True`` entry in
    ``match_tiebreak_flags``).  ``tiebreak_loser_points`` holds, per set, the
    points scored by the tiebreak *loser* (``None`` when no tiebreak or when
    the source omitted the detail).
    """

    raw: str
    sets_w: int = 0
    sets_l: int = 0
    games_w: int = 0
    games_l: int = 0
    set_scores: tuple[tuple[int, int], ...] = ()
    tiebreak_loser_points: tuple[Optional[int], ...] = ()
    match_tiebreak_flags: tuple[bool, ...] = ()
    completed: bool = False
    outcome_type: str = UNKNOWN
    tiebreaks_played: int = 0
    match_tiebreak_played: bool = False
    advantage_set: bool = False
    last_set_incomplete: bool = False
    parse_error: bool = False
    error_reason: Optional[str] = None
    winner_is_first: bool = True  # documented source convention, see module doc
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def n_sets(self) -> int:
        return len(self.set_scores)


# --- helpers ------------------------------------------------------------------
def _normalise(raw: str) -> str:
    """Lowercase, unify dashes, remove commas, glue tiebreak parens to the set."""
    s = raw.replace("–", "-").replace("—", "-").replace("−", "-")
    s = s.replace(",", " ").replace(";", " ")
    s = re.sub(r"\s+", " ", s).strip().lower()
    # "7-6 (5)" -> "7-6(5)" ; "[10 - 8]" -> "[10-8]"
    s = re.sub(r"(\d)\s+\((\d)", r"\1(\2", s)
    s = re.sub(r"\s*-\s*", "-", s)
    s = re.sub(r"\[\s*", "[", s)
    s = re.sub(r"\s*\]", "]", s)
    return s


def _extract_status(s: str) -> tuple[str, Optional[str]]:
    """Return (score text without status tokens, outcome or None)."""
    outcome: Optional[str] = None
    for pattern, kind in _STATUS_PATTERNS:
        new_s, n = re.subn(pattern, " ", s)
        if n:
            if outcome is None:
                outcome = kind
            elif outcome != kind:
                # e.g. "6-3 RET W/O" -- contradictory; keep the first, note it.
                log.debug("conflicting status tokens in %r", s)
            s = new_s
    return re.sub(r"\s+", " ", s).strip(), outcome


@dataclass
class _SetInfo:
    w: int
    l: int  # noqa: E741 - mirrors the w/l naming of the source columns
    complete: bool
    tiebreak: bool
    tb_loser_points: Optional[int]
    advantage: bool
    match_tiebreak: bool
    error: Optional[str] = None


def _classify_set(w: int, l: int, tb_a: Optional[int], tb_b: Optional[int]) -> _SetInfo:  # noqa: E741
    """Decide whether a (w, l) set is complete/tiebreak/advantage/impossible.

    ``tb_a``/``tb_b`` are the parenthesised numbers: a single number is the
    loser's tiebreak points; two numbers ("7-6(11-9)") are both players' points.
    """
    hi, lo = max(w, l), min(w, l)
    tb_points: Optional[int] = None
    if tb_a is not None:
        tb_points = min(tb_a, tb_b) if tb_b is not None else tb_a

    if hi == 7 and lo == 6:
        return _SetInfo(w, l, True, True, tb_points, False, False)
    if tb_points is not None and not (hi == 6 and lo == 6):
        # Tiebreak detail on a set that cannot have had a tiebreak.
        return _SetInfo(w, l, False, False, tb_points, False, False, error=f"TIEBREAK_ON_NON_TIEBREAK_SET:{w}-{l}")
    if hi == 6 and lo <= 4:
        return _SetInfo(w, l, True, False, None, False, False)
    if hi == 7 and lo == 5:
        return _SetInfo(w, l, True, False, None, False, False)
    if hi > 7 and hi - lo == 2:
        return _SetInfo(w, l, True, False, None, True, False)
    if hi > 7 and hi - lo > 2:
        return _SetInfo(w, l, False, False, None, False, False, error=f"IMPOSSIBLE_SET:{w}-{l}")
    # 6-6 (tiebreak in progress or not yet played), 6-5, 5-5, 2-1, 0-0 ...
    return _SetInfo(w, l, False, hi == 6 and lo == 6 and tb_points is not None, tb_points, False, False)


def _classify_match_tiebreak(a: int, b: int) -> _SetInfo:
    """Match tiebreak [10-8]: first to 10 (or 7 in some events) by two."""
    hi, lo = max(a, b), min(a, b)
    complete = hi >= 7 and hi - lo >= 2 and (hi == 7 or hi == 10 or hi - lo == 2)
    return _SetInfo(a, b, complete, False, None, False, True)


def _target_sets(sets_seq: list[tuple[int, int]]) -> Optional[int]:
    """Infer best-of from the sequence of set winners (2 -> best of 3, 3 -> best of 5)."""
    w = sum(1 for a, b in sets_seq if a > b)
    l = sum(1 for a, b in sets_seq if b > a)  # noqa: E741
    hi = max(w, l)
    if hi in (2, 3):
        return hi
    return None


# --- public API ---------------------------------------------------------------
def parse_score(raw: Optional[str]) -> ScoreParse:
    """Parse a score string.  Never raises; problems are reported via ``parse_error``.

    Empty / null input is *not* an error: it yields outcome ``UNKNOWN`` so the
    caller can decide whether an unknown score is acceptable for its purpose.
    """
    if raw is None or (isinstance(raw, float) and raw != raw):  # NaN guard
        raw = ""
    raw = str(raw)
    s = _normalise(raw)
    if not s:
        return ScoreParse(raw=raw, outcome_type=UNKNOWN, notes=("EMPTY_SCORE",))

    body, status = _extract_status(s)
    infos: list[_SetInfo] = []
    notes: list[str] = []
    for tok in body.split():
        m = _SET_RE.match(tok)
        if m:
            w, l, tb_a, tb_b = (int(x) if x is not None else None for x in m.groups())  # noqa: E741
            infos.append(_classify_set(w, l, tb_a, tb_b))
            continue
        m = _MTB_RE.match(tok)
        if m:
            infos.append(_classify_match_tiebreak(int(m.group(1)), int(m.group(2))))
            continue
        return ScoreParse(raw=raw, outcome_type=status or UNKNOWN, parse_error=True,
                          error_reason=f"UNPARSEABLE_TOKEN:{tok}")

    return _assemble(raw, infos, status, notes)


def _assemble(raw: str, infos: list[_SetInfo], status: Optional[str], notes: list[str]) -> ScoreParse:
    """Turn per-set classifications into the final ScoreParse with validity checks."""
    set_scores = tuple((i.w, i.l) for i in infos)
    tb_points = tuple(i.tb_loser_points for i in infos)
    mtb_flags = tuple(i.match_tiebreak for i in infos)
    error: Optional[str] = next((i.error for i in infos if i.error), None)

    # Incomplete sets are only legal as the *last* set of a cut-short match.
    for idx, info in enumerate(infos):
        if info.complete or info.error:
            continue
        is_last = idx == len(infos) - 1
        if not is_last:
            error = error or f"INCOMPLETE_SET_NOT_LAST:{info.w}-{info.l}"
        elif status not in (RETIRED, DEFAULT, UNFINISHED, WALKOVER):
            error = error or f"INCOMPLETE_SET_WITHOUT_STATUS:{info.w}-{info.l}"

    sets_w = sum(1 for i in infos if i.complete and i.w > i.l)
    sets_l = sum(1 for i in infos if i.complete and i.l > i.w)
    games_w = sum(i.w for i in infos if not i.match_tiebreak)
    games_l = sum(i.l for i in infos if not i.match_tiebreak)
    last_incomplete = bool(infos) and not infos[-1].complete and infos[-1].error is None

    # Completion logic.
    outcome = status
    completed = False
    if outcome is None:
        if not infos:
            outcome = UNKNOWN
        elif error is None and _winner_closed_out(infos):
            outcome, completed = COMPLETED, True
        else:
            outcome = UNKNOWN
            error = error or "SETS_DO_NOT_FORM_A_COMPLETED_MATCH"
    elif outcome == WALKOVER and infos:
        notes.append("WALKOVER_WITH_SETS")
    elif outcome == COMPLETED:  # not produced by the status regexes, kept for symmetry
        completed = True

    return ScoreParse(
        raw=raw,
        sets_w=sets_w,
        sets_l=sets_l,
        games_w=games_w,
        games_l=games_l,
        set_scores=set_scores,
        tiebreak_loser_points=tb_points,
        match_tiebreak_flags=mtb_flags,
        completed=completed,
        outcome_type=outcome,
        tiebreaks_played=sum(1 for i in infos if i.tiebreak),
        match_tiebreak_played=any(i.match_tiebreak for i in infos),
        advantage_set=any(i.advantage for i in infos),
        last_set_incomplete=last_incomplete,
        parse_error=error is not None,
        error_reason=error,
        notes=tuple(notes),
    )


def _winner_closed_out(infos: list[_SetInfo]) -> bool:
    """True iff the first-listed player reaches 2 or 3 sets exactly on the last set."""
    if not all(i.complete for i in infos):
        return False
    seq = [(i.w, i.l) for i in infos]
    target = _target_sets(seq)
    if target is None:
        return False
    w = l = 0  # noqa: E741
    for idx, (a, b) in enumerate(seq):
        if a > b:
            w += 1
        else:
            l += 1  # noqa: E741
        reached = w == target or l == target
        if reached and idx != len(seq) - 1:
            return False  # superfluous sets after the match was decided
    return w == target and l < target


def is_valid_score(raw: Optional[str]) -> bool:
    """Convenience predicate: parseable and not impossible (unknown/empty counts as valid)."""
    return not parse_score(raw).parse_error
