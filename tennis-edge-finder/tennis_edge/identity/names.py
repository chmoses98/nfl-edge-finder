"""Player-name normalisation shared by every source.

Why: Sackmann writes "Roger Federer", tennis-data writes "Federer R.", Kalshi
market titles write "R. Federer" or "Federer".  Matching across them needs one
canonical token form that is insensitive to diacritics ("Đoković" ->
"dokovic"), punctuation ("O'Connell" -> "o connell"), hyphens
("Auger-Aliassime" -> "auger aliassime") and generational suffixes ("Jr.").

All functions are pure and never raise on odd input (None/NaN -> "").
"""
from __future__ import annotations

import re
import unicodedata
from typing import Any, Optional

SUFFIX_TOKENS = frozenset({"jr", "sr", "ii", "iii", "iv"})

_PUNCT_TO_SPACE = re.compile(r"[-'’`´.‐-―/,()]")
_NON_ALNUM = re.compile(r"[^a-z0-9 ]")
_WS = re.compile(r"\s+")
# A raw whitespace token that is an initials group: "R.", "S.W.", "An.", "J-L." (already split by then)
_INITIAL_TOKEN_RE = re.compile(r"^(?:[A-Za-z]{1,3}\.)+$")


def strip_diacritics(s: str) -> str:
    """NFKD-decompose and drop combining marks: 'Ćorić' -> 'Coric'.

    A few letters do not decompose (ø, ł, ß, æ); they are mapped by hand so
    that 'Søren' and 'Soren' collapse to the same key.
    """
    s = unicodedata.normalize("NFKD", s)
    s = "".join(ch for ch in s if not unicodedata.combining(ch))
    return s.translate(str.maketrans({"ø": "o", "Ø": "O", "ł": "l", "Ł": "L", "ß": "ss", "æ": "ae", "Æ": "AE",
                                      "œ": "oe", "Œ": "OE", "đ": "d", "Đ": "D", "ð": "d", "þ": "th"}))


def _as_text(s: Any) -> str:
    if s is None:
        return ""
    if isinstance(s, float) and s != s:  # NaN
        return ""
    return str(s)


def normalize_name(s: Any) -> str:
    """Canonical lowercase ASCII token string; '' for empty input.

    Steps: NFKD strip diacritics -> lowercase -> hyphens/apostrophes/periods
    and other punctuation to spaces -> drop non-alphanumerics -> collapse
    whitespace -> drop suffix tokens (jr, sr, ii, iii, iv).
    """
    text = strip_diacritics(_as_text(s)).lower()
    text = _PUNCT_TO_SPACE.sub(" ", text)
    text = _NON_ALNUM.sub("", text)
    tokens = [t for t in _WS.split(text) if t and t not in SUFFIX_TOKENS]
    return " ".join(tokens)


def name_tokens(s: Any) -> tuple[str, ...]:
    """``normalize_name`` split into tokens."""
    n = normalize_name(s)
    return tuple(n.split()) if n else ()


def surname_initials(s: Any) -> tuple[tuple[str, ...], tuple[str, ...]]:
    """Split a tennis-data style name into (surname_tokens, initial_groups).

    tennis-data writes "Surname I." / "Surname I.J." / "Bautista Agut R." /
    "Kuznetsov An." (two-letter group used to disambiguate).  Initials are
    the whitespace tokens that end with a period; when none exist (e.g. a
    full name "Roger Federer"), *trailing* single-letter tokens are treated as
    initials and everything else is surname.  Each group is returned
    lowercase without periods, e.g. "S.W." -> ("s", "w"), "An." -> ("an",).
    """
    raw = strip_diacritics(_as_text(s)).strip()
    if not raw:
        return (), ()
    raw_tokens = raw.split()
    initial_groups: list[str] = []
    surname_raw: list[str] = []
    for tok in raw_tokens:
        if _INITIAL_TOKEN_RE.match(tok):
            initial_groups.extend(g.lower() for g in tok.split(".") if g)
        else:
            surname_raw.append(tok)
    surname_tokens = tuple(name_tokens(" ".join(surname_raw)))
    if initial_groups:
        return surname_tokens, tuple(initial_groups)
    # No period-terminated tokens: fall back to trailing 1-letter tokens.
    toks = list(surname_tokens)
    trailing: list[str] = []
    while toks and len(toks[-1]) == 1 and len(toks) > 1:
        trailing.insert(0, toks.pop())
    return tuple(toks), tuple(trailing)


def player_match_score(td_name: Any, full_name: Any, last_name: Optional[Any] = None) -> float:
    """How well a tennis-data name ("Federer R.") fits a Sackmann full name ("Roger Federer").

    Returns 1.0 for surname + all initial groups matching, 0.9 when the first
    initial matches but later groups do not (or are unavailable), 0.7 for a
    surname-only match (no initials in the source), 0.0 otherwise -- including
    a *wrong* first initial, which is the "Zverev A." vs "Zverev M." case and
    must never be treated as a partial match.

    ``last_name`` (from the player registry) lets the surname be matched
    against the actual last-name field so that a first name equal to another
    player's surname ("Alexander Bublik" vs "Alexander Z.") cannot match.
    """
    sur_tokens, initials = surname_initials(td_name)
    if not sur_tokens:
        return 0.0
    full_tokens = name_tokens(full_name)
    if not full_tokens:
        return 0.0
    if last_name is not None and normalize_name(last_name):
        last_tokens = name_tokens(last_name)
        if not set(sur_tokens) <= set(last_tokens):
            return 0.0
        first_tokens = [t for t in full_tokens if t not in last_tokens]
    else:
        if not set(sur_tokens) <= set(full_tokens):
            return 0.0
        first_tokens = [t for t in full_tokens if t not in sur_tokens]
    if not initials:
        return 0.7
    if not first_tokens:
        return 0.7  # cannot verify initials against a mononym
    if not first_tokens[0].startswith(initials[0]):
        return 0.0
    for group, tok in zip(initials[1:], first_tokens[1:]):
        if not tok.startswith(group):
            return 0.9
    if len(initials) > len(first_tokens):
        return 0.9
    return 1.0


def last_first_initial(name_first: Any, name_last: Any) -> str:
    """Registry -> tennis-data style key: ('Roger', 'Federer') -> 'federer r'."""
    first = name_tokens(name_first)
    last = normalize_name(name_last)
    if not last:
        return ""
    if not first:
        return last
    return f"{last} {first[0][0]}"
