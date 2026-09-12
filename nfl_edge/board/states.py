"""Terminal states and funnel stages of the full-board accounting.

Every discovered contract reaches exactly one TERMINAL state. The states are the mission's, with two additions
made explicit so nothing can hide inside another state:

    NOT_CAPTURED          the series is discovered but no capture tier reaches it (the invisible-market bug)
    JOINT_MODEL_REQUIRED  legs understood, dependence not modelled

The funnel v2 stages are ordered; a contract is counted at every stage it passed and terminates at the first
it failed. `unexplained` is the count of contracts with no terminal state, and it must be zero.
"""
from __future__ import annotations

PRICED = "PRICED"
PROJECTABLE_NOT_YET_VALIDATED = "PROJECTABLE_NOT_YET_VALIDATED"
CAPTURE_ONLY = "CAPTURE_ONLY"
NOT_CAPTURED = "NOT_CAPTURED"
RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
SEMANTICS_AMBIGUOUS = "SEMANTICS_AMBIGUOUS"
DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
IDENTITY_UNRESOLVED = "IDENTITY_UNRESOLVED"
UNSUPPORTED = "UNSUPPORTED"
NON_FOOTBALL_MODEL = "NON_FOOTBALL_MODEL"
JOINT_MODEL_REQUIRED = "JOINT_MODEL_REQUIRED"
EXCLUDED = "EXCLUDED"
POST_KICKOFF = "POST_KICKOFF"
SETTLEMENT_UNSUPPORTED = "SETTLEMENT_UNSUPPORTED"

TERMINAL_STATES = (PRICED, PROJECTABLE_NOT_YET_VALIDATED, CAPTURE_ONLY, NOT_CAPTURED, RESEARCH_REQUIRED, SEMANTICS_AMBIGUOUS,
                   DATA_UNAVAILABLE, IDENTITY_UNRESOLVED, UNSUPPORTED, NON_FOOTBALL_MODEL, JOINT_MODEL_REQUIRED, EXCLUDED,
                   POST_KICKOFF, SETTLEMENT_UNSUPPORTED)

# funnel v2 stages, in order
DISCOVERED = "DISCOVERED"
NFL_BOARD = "NFL_BOARD"                  # passed the NFL membership rule (the denominator)
CLASSIFIED = "CLASSIFIED"                # family known
CAPTURED = "CAPTURED"                    # a capture tier polls the series (and the ticker was actually seen, when the capture state is given)
SEMANTICS_PROVEN = "SEMANTICS_PROVEN"
IDENTITY_RESOLVED = "IDENTITY_RESOLVED"
DATA_AVAILABLE = "DATA_AVAILABLE"
MODEL_SUPPORTED = "MODEL_SUPPORTED"      # an engine owns the question (PRICED or SHADOW support)
PROJECTED = "PROJECTED"                  # a projection row with a probability exists at the reference snapshot
SETTLEMENT_CAPABLE = "SETTLEMENT_CAPABLE"
MARKET_EXECUTABLE = "MARKET_EXECUTABLE"  # a real two-sided book (reserved for the funnel; not a projection stage)
STAGES = (DISCOVERED, NFL_BOARD, CLASSIFIED, CAPTURED, SEMANTICS_PROVEN, IDENTITY_RESOLVED, DATA_AVAILABLE, MODEL_SUPPORTED,
          PROJECTED, SETTLEMENT_CAPABLE)
