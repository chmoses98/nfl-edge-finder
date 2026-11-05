# NFL postmortem dashboard (2026-10-22 .. 2026-11-01)

Fills reconciled: 46 (settled 45, amended 0); kinds {'COMBO_UNDECODED': 2, 'SINGLE': 43, 'UNCLASSIFIED': 1}.
Recommendation states: {'NO_RECOMMENDATION_ON_RECORD': 46}.
Exposure flags (flags only, no cap): games 2, thesis groups 2, days 2.
Loss labels (24 losses): {'BAD_EXPRESSION': 1, 'INSUFFICIENT_EVIDENCE': 23}; positions with a close 0 of 42.
No market family may be called profitable or unprofitable below 100 positions.

| # | item | status | note |
|---|---|---|---|
| 1 | Immutable per-contract reconciliation | DONE | reconcile.py; missing evidence is a MISSING_* flag; combos without legs are COMBO_UNDECODED |
| 1b | Recommendation / model attribution for the window | UNRESOLVED | no real (non-test) recommendation exists on handicap-data for these fills; they are owner-selected, not model picks |
| 1c | Order id / fill ids per fill | UNRESOLVED | the routed wager rows carry no exchange order or fill ids yet (router-side change); reconcile.py now accepts order_id / kalshi_order_id / fill_ids / kalshi_fill_ids the moment they appear |
| 2 | Fee-inclusive break-even, calibrated fair probability, bet-up-to | DONE | fairvalue.py; None whenever calibration or fee is missing |
| 2b | PIT guards (projection, injuries, confirmed QB, quote, kickoff, price provenance) | WIRED_PENDING_MERGE | gates.G_PIT via integration.py; restriction-only. Game-level lines are BLOCKED QB_UNKNOWN until run_card.py --qb-confirmations supplies a confirmation with a time (a depth chart is never a confirmation) |
| 2c | Whole-order fee-inclusive ceiling check | WIRED_PENDING_MERGE | gates.G_ORDER_CEILING; can only FAIL a too-high ceiling. Calibrated bet-up-to stays None (MISSING_CALIBRATION): no held-out cells exist for thesis-conditioned fair values |
| 3 | Correlation groups + game/daily exposure flags (>5U, >15U) | WIRED_PENDING_MERGE | card.exposure_flags and PreflightResult.exposure_flags at 1U=$75 ($375/game, $1,125/day); flags only, no cap, per NFL_OPERATING_POLICY |
| 4 | Key-number distributions + held-out evaluation | DONE | research/postmortem_2026-11-02/distribution_eval.json |
| 4b | Matchup evidence (EPA, pace, ST) improves on the closing market | NOT_DEMONSTRATED | no held-out gain over market-only; do not activate |
| 4c | Injury / confirmed-QB history for the distribution model | UNRESOLVED | no point-in-time injury history before the 2026 availability_pit capture |
| 5 | Loss classification | DONE_PARTIAL | loss_eval.py; closes for the window are not published, so most losses are INSUFFICIENT_EVIDENCE |
| 5b | Closing prices for weeks 5-8 | FIX_PROPOSED_NOT_DISPATCHED | run 41513363507 died in the market-data fetch step with No space left on device, skipping close/CLV; shadow-v2-settle.yml lacked the free_runner_disk.sh step its sibling workflows have. Added; unverified until the workflow is dispatched (needs owner approval) |
| 7 | RUN NFL card crashed with no per-game cap | FIXED | challenge.py C10 compared open exposure to a None cap (owner policy 2026-11-01); 18 of the 20 clean-main test failures |
| 6 | NBA router PR #48 | OTHER_REPO | see kalshi-bet-router / nba-edge-finder PRs |
