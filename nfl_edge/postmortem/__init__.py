"""Betting postmortem repairs (issue #231, 2026-11-02). Pure, typed, fail-closed, stdlib + numpy only.

Nothing in this package places, sizes, ranks or promotes a bet, and nothing in it rewrites a historical record.
Restriction-only code (guards) can only REMOVE actionability. Anything that could add or re-rank a bet is absent.
Missing evidence is reported as an explicit ``MISSING_*`` flag and is never inferred.
"""
POSTMORTEM_VERSION = "postmortem-1.0.0"
