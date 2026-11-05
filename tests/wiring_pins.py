"""Source pins for the files the wired postmortem safeguards depend on (PR #232, owner-approved 2026-11-02).

`gates.py` and `preflight.py` are pinned in tests/test_incumbent_unchanged.py (and gates.py also in tests/test_postgame_workflow.py).
The files below are the rest of what decides whether a real-money line is blocked or flagged: the card that builds the
`pit_evidence` block and the exposure flags, and the postmortem modules the gates call. A change to any of them without
updating this table fails tests/test_postmortem_wiring.py - a deliberate, reviewed edit updates the pin in the same commit,
with the reason. sha256 first 16 hex chars, same convention as the other pin tables.
"""
PINS = {
    "nfl_edge/handicap/card.py": "a38a435e5769cd29",
    "nfl_edge/postmortem/integration.py": "bf33982d4d706fdb",
    "nfl_edge/postmortem/guards.py": "ef34b47c5a316b55",
    "nfl_edge/postmortem/fairvalue.py": "bc31bf425852e365",
    "nfl_edge/postmortem/exposure.py": "2a6119d4262018c3",
    "nfl_edge/postmortem/common.py": "3801603049d43c8f",
    "nfl_edge/postmortem/ontology.py": "59ef4d0f1171db6b",
    "nfl_edge/postmortem/qb_confirmations.py": "3fb3e452ef950e73",
}
