"""Source pins for the files the wired postmortem safeguards depend on (PR #232, owner-approved 2026-11-02).

`gates.py` and `preflight.py` are pinned in tests/test_incumbent_unchanged.py (and gates.py also in tests/test_postgame_workflow.py).
The files below are the rest of what decides whether a real-money line is blocked or flagged: the card that builds the
`pit_evidence` block and the exposure flags, and the postmortem modules the gates call. A change to any of them without
updating this table fails tests/test_postmortem_wiring.py - a deliberate, reviewed edit updates the pin in the same commit,
with the reason. sha256 first 16 hex chars, same convention as the other pin tables.
"""
# DELIBERATE, REVIEWED EDITS (PR #241, 2026-11-03): integration.py / guards.py / qb_confirmations.py changed (explicit QB-dependency table, game-specific
# confirmation validity replacing the blanket 48 h age, reason codes + provenance) and qb_dependency.py is new and pinned. No threshold, fee, depth,
# net-EV, quote-age, stake or exposure rule moved. guards.py: ef34b47c5a316b55 -> 00493f0918bc50e4 (PR #241 first commit) -> 5b08684ed579baa0.
# DELIBERATE, REVIEWED EDITS (PR #241, 2026-11-03, second pass): player_identity.py is new and pinned. qb_dependency.py / integration.py / guards.py now
# classify a contract about ONE named player from the player's VERIFIED identity and position (a QB's own rushing/receiving/TD prop is QB-gated on his own
# confirmed starter; an unverified player is blocked; rushing field markets are QB_GATED), and the guard also re-judges a confirmed row's game, team and named
# quarterback. These only ever ADD blocks; no threshold, fee, depth, net-EV, quote-age, stake or exposure rule moved. card.py is unchanged.
PINS = {
    "nfl_edge/handicap/card.py": "a38a435e5769cd29",
    "nfl_edge/postmortem/integration.py": "0c2bfc2c979cd6a8",
    "nfl_edge/postmortem/guards.py": "5c803e661c2978b6",
    "nfl_edge/postmortem/fairvalue.py": "bc31bf425852e365",
    "nfl_edge/postmortem/exposure.py": "2a6119d4262018c3",
    "nfl_edge/postmortem/common.py": "3801603049d43c8f",
    "nfl_edge/postmortem/ontology.py": "59ef4d0f1171db6b",
    "nfl_edge/postmortem/qb_confirmations.py": "4d5759fc575f1d07",
    "nfl_edge/postmortem/player_identity.py": "364798b76809d69f",
    "nfl_edge/postmortem/qb_dependency.py": "4fa9e92593bb6fdb",
}
