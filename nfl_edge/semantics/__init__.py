"""Semantics engine (SHADOW v2).

A Kalshi contract is a QUESTION asked of a latent distribution. This package turns a classified market into a
`Question` with a named engine, a named statistic, a proven comparison rule and an explicit semantic
confidence, and it holds the FAMILY CATALOG that says, for every (family, period), what the YES rule is, how
pushes, ties and overtime are treated, which engine answers it, and how it is settled.

Nothing here prices anything. The rule this package enforces is the mission's: only PROVEN semantics are
automatically priceable; LIKELY is projectable-not-yet-validated; AMBIGUOUS and UNKNOWN fail closed.
"""
from nfl_edge.semantics.questions import (  # noqa: F401
    Question, contract_question, question_from_market, PROVEN, LIKELY, AMBIGUOUS, UNKNOWN,
)
from nfl_edge.semantics.catalog import FAMILY_CATALOG, catalog_entry  # noqa: F401
