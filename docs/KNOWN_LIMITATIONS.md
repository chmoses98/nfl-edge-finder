# Known limitations (updated 2026-09-07)

> Policy and vocabulary live in [`DECISION_STANDARD.md`](DECISION_STANDARD.md). These are the
> things that remain genuinely unsolved.

1. **No timestamped sportsbook lines.** The only free historical line is the nflverse consensus (near-close, vintage undocumented). Opening/midweek research on game markets must use Kalshi's own history, which we started recording today; historical Kalshi candlesticks (bid/ask, 1-min) exist for the 2025 season via the backfill but there are no historical order books.
2. **Injury feed.** nflverse injuries have no intra-week timestamps and the 2026 file is not published yet. Runner-side probes (2026-09-04) confirmed Sleeper players (injury_status, practice_participation, depth_chart_order) and ESPN injuries are reachable and free; `context-capture.yml` now snapshots them every 3 hours with retrieval timestamps. Official practice-report timing is still only as good as those feeds' update latency, which is unmeasured.
3. **Participation/coverage data arrives after the season.** Matchup features built from it are priors, not current-week features.
4. **GitHub cron is best-effort.** Capture cadence is nominally 10 minutes; expect gaps. `trigger_source` in manifests exposes them. An external dispatcher needs the owner's PAT.
5. **Game model v1 has no edge vs the close** (documented in research/game_model/RESULTS.md). Nothing in this repo is validated for betting.
6. **Player-prop settlement**: an ACTIVE player who takes no snap settles at a pregame fair price (~1% of rungs); an INACTIVE player settles NO. Both are modelled in nfl_edge/settlement/semantics.py.
7. **Sandbox egress** blocks Kalshi/NWS/ESPN/Sleeper/Open-Meteo; all live collection depends on GitHub Actions availability. Weather forecasts (NWS + Open-Meteo, with gusts) are now captured per upcoming game every 3 hours; forecast-vintage history before 2026-09-04 must come from Open-Meteo's historical-forecast/previous-runs archives.
8. **Storage growth** on `market-data` is unmeasured beyond day one (~14 MB after the first discovery+capture); compaction is planned, not built.
9. **Kalshi player UUID map** resolves 121/141 players exactly; 20 are flagged for review and must not be used in pricing until resolved.
10. **Kalshi parlay series** (KXMVENFL*, KXNFLPREPACK*) hold millions of archived multivariate contracts and are excluded from backfill; live capture keeps them at LIGHT tier.

11. **Maker multipliers are unverified for most maker-fee series.** The regulatory Fee Schedule lists both a
    Maker and a Taker Multiplier per listed non-standard series, and `KXNFLGAME` is recorded from it at
    maker 1 / taker 1. The other 24 maker-fee NFL series are not yet transcribed into a schedule window, so
    their maker multiplier is `UNVERIFIED` and `net_executable_ev` refuses to price a maker order on them.
    This costs nothing operationally — passive execution is rejected on core game markets by
    research/passive (Milestone K), so a real recommendation is a taker order and the taker path is fully
    known — but maker-side research on those series must sweep `MAKER_MULTIPLIER_SWEEP`.
18. **The fee schedule's per-series multipliers are operator-attested, not machine-verified.** The session
    that transcribed them could not reach kalshi.com or the Kalshi API (network egress policy).
    `scripts/kalshi/capture_fee_metadata.py` re-reads live metadata from Actions and reports any
    disagreement, and a conflict fails closed rather than resolving by source rank — but until that job has
    run against the live API, the `verified_by: OPERATOR_ATTESTATION` marker on the window is the honest
    description of its provenance.
19. **Order-book depth is only captured for FULL_MICROSTRUCTURE series inside 72h of kickoff.** Outside that
    window the depth behind the top of book is not observable at all, so the full-position executability
    gate fails closed rather than falling back to top-of-book pricing. That is the right failure, but it
    does mean a recommendation on a market outside book coverage cannot currently be written.
12. **No official gameday inactive feed.** `INACTIVE_CONFIRMED` is reserved and unpopulated; no free source
    has been shown to deliver the official T-90m inactive list reliably. `scripts/data/probe_inactives.py`
    reports what candidates actually deliver and is deliberately a probe, not a collector: a broken inactives
    feed does not degrade to "no information", it degrades to "everyone is playing". The gap costs coverage,
    not safety — prop recommendations already fail closed on unresolved availability near kickoff.
13. **Ticker-level quote confirmation is new.** `capture.py` now records `last_seen` per ticker, which gives
    exact confirmation for the decision-time freshness gate. Captures written before this change do not carry
    it, so resolution falls back to series-level manifest confirmation for that history. Series-level is
    strong but coarser: it proves the series was polled successfully, not that the individual ticker came back
    in the page.
14. **Branch protection is unverified.** The append-only property of `handicap-data` is enforced by the
    application and detected by `scripts/handicap/verify_append_only.py`, but the server-side ruleset that
    would *prevent* a force-push has not been confirmed applied — this environment cannot read repository
    protection settings. See `docs/OPERATIONS.md` for the exact ruleset the owner must apply.
15. **The risk policy has never bound on a real bet.** `config/risk_policy.json` is a defensible pilot
    default, not a calibrated one. Its unit fraction and grade caps were chosen conservatively; whether they
    are the right ones is unmeasured, and will stay unmeasured until there is a prospective sample.
16. **Slippage is modelled as zero by default.** `net_executable_ev` takes a `slippage_dollars` term and
    nothing currently estimates it; realised entry slippage is measured after the fact
    (`Evaluation.entry_slippage`) but does not yet feed a prior.
17. **Zero resolved recommendations.** Every metric in the scorecard is structurally correct and empirically
    empty. Nothing is backfilled and nothing will be.
20. **Preflight is a check, not an enforcement mechanism.** `scripts/handicap/preflight_candidate.py` decides
    whether a candidate may be shown as a bet; nothing prevents a human from placing a wager anyway, because
    nothing in this repository can see or reach an order surface. The control is that a blocked candidate is
    never *presented* as a bet and never reaches the ledger as one — not that the bet is impossible.
21. **Outstanding exposure is only as complete as the committed ledger.** Reserved-and-unfilled stake is
    released at kickoff and executed stake at settlement, both established from records on `handicap-data`.
    A fill the owner never reported is invisible to the cap, and a settled position with no `Evaluation`
    keeps consuming budget until one is attached. Both errors are conservative in the safe direction (an
    unreported fill under-counts only its own reserve, which is already held; a missing evaluation
    over-counts), but the definition is a ledger statement, not a broker statement — there is no position
    feed.
22. **The `/series/fee_changes` response shape is unconfirmed.** The endpoint is now ingested and its
    announced effective timestamps are preserved, but this environment could not reach the Kalshi API to see
    a real response. `fetch_fee_changes` therefore accepts several plausible envelopes and keeps every field
    rather than filtering through today's understanding. The first live run from Actions is what will
    confirm the shape; until then a parse that silently returns zero changes is possible, which is why
    schedule freshness *also* rests on the age of the last clean capture rather than on fee-change detection
    alone.
23. **The fee-rounding residual bounds fragmentation, not everything.** `rounding_uncertainty` is a
    worst-case bound on the difference between a fragmented order and its single-fill equivalent, derived
    from the accumulator mechanism. It does not bound a *wrong multiplier*, a schedule that changed without
    announcement, or slippage; those fail closed through other gates. It also assumes fills are at least one
    whole contract, which is true on Kalshi today and is the only reason the fill count is bounded at all.
24. **Realised net P/L will be null for a while.** `net_pnl` requires an observed venue fee on every counted
    fill. Until the owner reports fees per fill, evaluations will carry `gross_pnl` and `estimated_net_pnl`
    with `net_pnl: null`, and the scorecard's desk-level net will be null alongside a
    `fee_reconciliation` block. That is the intended behaviour and not a defect to route around.
25. **The pre-trade transport is complete in this repository and not yet operational end to end.** The
    workflow, the worker, the statuses and the write-back field all exist and are tested against a fake
    Airtable, including the TEST_ONLY probe. Two things cannot be provisioned from a code change and are the
    owner's: the `Preflight Result` field plus the four `PREFLIGHT_*` status options in Airtable, and an
    Airtable Automation holding a fine-grained GitHub token (`Actions: read and write` on this repository
    only) that calls `workflow_dispatch`. Until a live run has succeeded, the leg is designed and untested
    against the real Automation. `docs/AIRTABLE_BRIDGE.md` carries the exact setup and the E2E procedure.
    What keeps this safe while it is missing is that a row that is not `PREFLIGHT_APPROVED` has not been
    approved: an unanswered request is not a bet.
26. **The fee-rounding bound is materially larger than a whole-contract model implied, and correctly so.**
    Kalshi order sizes are fixed-point with a 0.01-contract minimum, so a 16-contract position carries a
    worst-case fragmentation bound of about $0.17 and a 100-contract position about $1.01. On a small pilot
    stake that is a real hurdle — roughly 1.7% of a $10 position. It is not a strategy buffer and cannot be
    tuned; the only levers are evidence (establishing `WHOLE_CONTRACTS_ONLY` for a series from venue
    metadata, which drops the 100-contract bound to $0.02) and observation (a realised fee is not an
    estimate and carries no uncertainty term at all). Until one of those lands, thin edges on small stakes
    will be blocked by transaction-cost uncertainty rather than by the edge itself, and the ledger will
    record that as the reason.
27. **Contract granularity is asserted from documentation, not from captured venue metadata.** No field in
    the current per-series registry establishes whether fractional trading is enabled, so every series sits
    at `UNKNOWN` and is priced as fractional. Wiring a captured metadata field into
    `config/kalshi_fee_schedule.json` — under the same capture/surface/review discipline the fee multipliers
    get — is the work that would let a series legitimately move to `WHOLE_CONTRACTS_ONLY`.
28. **Settlement availability rests on `evaluated_at` for every record written so far.** No evaluation in
    the ledger carries `settlement_observed_at`, because the field is new. `evaluated_at` is the conservative
    fallback — it can only be later than the outcome, never earlier — so exposure is released later than it
    strictly must be, never earlier. Populating the stronger field when the settlement is actually observed
    is a small improvement to exposure accuracy and changes nothing about safety.
