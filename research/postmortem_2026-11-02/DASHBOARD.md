# NFL postmortem dashboard (2026-10-22 .. 2026-11-01)

Fills reconciled: 46 (settled 45, amended 0); kinds {'SINGLE': 43, 'UNCLASSIFIED': 1, 'COMBO_UNDECODED': 2}.
Recommendation states: {'NO_RECOMMENDATION_ON_RECORD': 46}.
Exposure flags (flags only, no cap): games 2, thesis groups 2, days 2.
Loss labels (24 losses): {'INSUFFICIENT_EVIDENCE': 23, 'BAD_EXPRESSION': 1}; positions with a close 0 of 42.
No market family may be called profitable or unprofitable below 100 positions.

| # | item | status | note |
|---|---|---|---|
| 1 | Immutable per-contract reconciliation | DONE | reconcile.py; missing evidence is a MISSING_* flag; combos without legs are COMBO_UNDECODED |
| 1b | Recommendation / model attribution for the window | UNRESOLVED | no real (non-test) recommendation exists on handicap-data for these fills; they are owner-selected, not model picks |
| 1c | Order id / fill ids per fill | UNRESOLVED | the routed wager rows carry no exchange order or fill ids (router-side change; see PR note) |
| 2 | Fee-inclusive break-even, calibrated fair probability, bet-up-to | DONE | fairvalue.py; None whenever calibration or fee is missing |
| 2b | PIT guards (projection, injuries, confirmed QB, quote, kickoff, price provenance) | DONE_NOT_WIRED | guards.py is restriction-only; wiring into pinned gates.py/preflight.py needs owner authorization |
| 3 | Correlation groups + game/daily exposure flags (>5U, >15U) | DONE | exposure.py; flags only, no cap, per NFL_OPERATING_POLICY |
| 4 | Key-number distributions + held-out evaluation | DONE | research/postmortem_2026-11-02/distribution_eval.json |
| 4b | Matchup evidence (EPA, pace, ST) improves on the closing market | NOT_DEMONSTRATED | no held-out gain over market-only; do not activate |
| 4c | Injury / confirmed-QB history for the distribution model | UNRESOLVED | no point-in-time injury history before the 2026 availability_pit capture |
| 5 | Loss classification | DONE_PARTIAL | loss_eval.py; closes for the window are not published, so most losses are INSUFFICIENT_EVIDENCE |
| 5b | Closing prices for weeks 5-8 | UNRESOLVED | shadow-v2-settle.yml has been cancelled at its job limit (docs/research/ACTUAL_WAGER_DIAGNOSIS_2026-10-25.md) |
| 6 | NBA router PR #48 | OTHER_REPO | see kalshi-bet-router / nba-edge-finder PRs |
