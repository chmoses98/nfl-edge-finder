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
26. **The fee-rounding bound is dominated by the balance precision, not the fill count.** With the corrected
    $0.000001 trade-fee increment it is about $0.0116 on a 16-contract position and $0.0200 on 100 — mostly
    the one-cent accumulator residual. The `~$0.17` / `~$1.01` figures reported in the previous round were
    computed with an increment a hundred times too large and are withdrawn. It is not a strategy buffer and
    cannot be tuned; it shrinks with evidence (`WHOLE_CONTRACTS_ONLY` for a series) or with observation (a
    realised fee carries no uncertainty term at all).
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
29. **The fee-rounding semantics are operator-attested, not machine-verified.** `docs.kalshi.com` is
    unreachable from this environment (network egress policy), so the trade-fee increment ($0.000001), the
    two balance precisions ($0.01 / $0.0001) and the per-fill rebate cap are recorded from the reviewer's
    reading of the current Fee Rounding page, dated in `config/kalshi_fee_schedule.json`. The **current
    official worked example is now reproduced exactly** (one contract at $0.055: model fee $0.00363825,
    trade fee $0.003639, aligned change -$0.060000, rounding fee $0.001361), which is real evidence — but it
    was transcribed here rather than fetched. This is the third version of these values in this PR; the
    second survived review because the example carried at the time was internally consistent against the
    wrong rule.
30. **Preflight expiry is a judgement, not a measurement.** `MAX_REQUEST_AGE_MIN = 30` bounds how stale the
    HANDICAP may be at approval (the market is re-priced, so it is not the market that ages). Thirty minutes
    is two capture cycles of slack for a delayed Automation and is a defensible default, not a calibrated
    one; nothing has measured how quickly a ChatGPT thesis actually decays, and nothing will until there is
    a prospective sample.
31. **The preflight binding protects the bridge, not the manual writer.** A real `RECOMMENDED` record cannot
    reach the ledger through `sync_airtable.py` without a hash-matched `Approved Payload`. The engineering
    fallback `validate_recommendations.py --write` still admits one on the strength of running the same
    gates itself at the record's own `created_at` — which is the same check, done locally, and is why it is
    allowed; but it is not the same *binding*, and an operator using it is trusted to be an operator.
32. **The approval signature authenticates the worker, not the handicapper.** `PREFLIGHT_SIGNING_KEY`
    proves that the GitHub preflight worker issued exactly this approval for exactly this row, run, pair of
    payloads and instant. It does not prove anything about who wrote the candidate, and it does not defend
    against someone who can already run GitHub Actions in this repository — that is what branch protection
    and the repository's own access control are for. Anyone holding the key can mint approvals, so it is a
    repository secret and nothing else; rotating it invalidates approvals not yet archived, which is
    correct.
33. **The 30-minute request window is enforced in two places and could drift.** `preflight` refuses to
    issue an approval past it and the importer refuses to archive one; both read
    `approval.MAX_REQUEST_AGE`, and a test asserts they are the same number. If a future change gives the
    worker a longer window than the importer accepts, the symptom is an approval the owner acts on and the
    ledger then rejects — visible, but late.
34. **A rejected approval leaves the Airtable row in a state a human must resolve.** The importer marks the
    row ERROR and says why; nothing automatically re-requests preflight, because a bet that failed its
    binding should be looked at rather than retried.
35. **The workflow wiring is proved structurally, not by a live run.** `tests/test_workflow_secret_wiring.py`
    reads the actual YAML and asserts that the step running each script declares every secret that script
    reads from its environment, and that no secret is ever placed on a command line. That is what caught the
    reviewed defect — the importer step passed `AIRTABLE_TOKEN` and not `PREFLIGHT_SIGNING_KEY`, so a
    correctly signed recommendation would have been refused because the runner was wired wrong. What the
    test cannot prove is that the secrets are *configured in the repository*: only a live run can, and that
    is part of the post-merge E2E. Until then a real recommendation is deferred rather than lost.
36. **A deferred row is invisible unless somebody reads the exit code.** A configuration failure leaves the
    row `READY_FOR_SYNC` and exits `2`; a failed scheduled run is visible in the Actions tab and nowhere
    else. Nothing pages anybody, so a missing secret could sit unnoticed for a cycle. The consequence is
    delay, never loss — the row imports unchanged once the secret is present — but the delay is real.
37. **Fee-change supersession is a policy judgement, not a venue statement.** Kalshi's feed does not say
    "this announcement is obsolete". The rule that a reviewed window supersedes every change effective
    before it is ours, and it rests on the window having been checked by a human against the published fee
    schedule. It is sound exactly as far as that review is: a window written carelessly would now silence
    the announcements it postdates rather than colliding with them.
38. **The health job's failure set is scoped to the committed registry.** Every announced change is
    classified and recorded, but only those on series this repository prices (plus exchange-wide ones with
    no series ticker) fail the run. A change on a series we later add to the registry only becomes
    actionable once that addition is committed, so a series added between weekly runs carries one cycle of
    unchecked announcements.
39. **The three-arm experiment has zero prospective evidence.** Every arm record, evaluation and report exists as
    infrastructure only; the first challenger record that counts is the first one written after this code is
    merged, and the opener (`2026_01_NE_SEA`) is excluded permanently. No verdict prints before 64 distinct games.
40. **The CURRENT centre is a replay of the frozen pricer, verified only where a ledger exists.** The pricer is
    frozen Week-1 lineage and records no centre, so the harness replays its game-environment block call for call
    (same seed, same order) and checks the replayed 40,000-row simulation against the ledger's prices to 1e-9 at
    every 2-hourly cycle. At the four canonical horizons the report path publishes no ledger, so the same replay
    runs with nothing to check against and is recorded as `exact_replay_unverified`; it never claims to be the
    recorded production centre. The replay costs the incumbent's own game-environment time (about two minutes).
41. **DATA_ONLY is the research model and nothing more.** No quarterback identity, weather or injury term: none has
    a pre-2026 validated coefficient. They are recorded as unavailable inputs, not silently absent. The historical
    result stands: against the closing line it is worse than the market in every season.
42. **Challenger centres are placed on the half-point grid** before simulation so the residual bank's
    fractional-part structure applies; the unrounded centre is what the centre-accuracy metrics score.
43. **The closing market centre needs six liquid rungs**, like every snapshot centre; a thin close is
    `MISSING_CLOSE` and movement toward it is unscored for that game.
44. **The autopsy's team-volume dimension is built from the same player statistics that settle the props** (sum of
    attempts / carries per team-game vs the team's prior games this season, or last season at week 1); it is a
    diagnosis, and its thresholds are named constants, not calibrated quantities.
45. **The funnel's BET is not a recommendation.** It says the mechanical gates would pass at the model's own number;
    the human handicap, the signed preflight and the risk policy still stand between it and money.
46. **Player anatomy exists only where the ledger exists.** The anatomy corpus is written at the 2-hourly cycle by
    replaying the frozen player path and reconciling to the ledger row; the horizon conductor writes no ledger and
    therefore no anatomy. The autopsy uses the latest pregame anatomy row, which is at most two hours older than
    the last ledger snapshot. A row that does not reproduce the ledger to 1e-9 is `REPRODUCTION_MISMATCH` and is
    excluded from the autopsy, so a library or data drift between the pricer and the collector shows up as
    missing evidence, never as wrong evidence.
47. **Shadow v2 has zero prospective evidence** (docs/SHADOW_V2.md §9). Every v2 engine (period, joint, season, the
    three player arms, margin buckets) writes PROJECTABLE_NOT_YET_VALIDATED records only; the first record that counts
    is the first one main writes after merge. Historically, no hybrid player blend beat the Kalshi ladder and the
    period engine cannot be compared to a market at all (203 archived period contracts).
48. **The period engine under-predicts key-number mass** (|1H margin| = 3: 0.088 predicted vs 0.124 observed); the
    candidate that matches key numbers mis-centres. Chosen by a preregistered rule; both facts are recorded.
49. **Season projections use approximate tie-breakers and consensus centres only where published**; conference and
    Super Bowl winners, race-to-N, first-touchdown team, total touchdowns and team statistics stay RESEARCH_REQUIRED.
50. **Route participation is not in free data**, so the autopsy's ROUTE_PARTICIPATION_MISS is INSUFFICIENT_DATA by
    construction until a route source exists.
51. **CLV is not profit.** Shadow v2's CLV (docs/SHADOW_V2.md §9.2) is an intermediate signal with one pinned sign
    convention; it is computed on the model's side from the horizon ask to the canonical close and never from a
    midpoint as if executable. No model is promoted on CLV.
52. **The canonical close dates confirmation to the last run a ticker was seen open**, not to the exchange's own
    close, and quality tiers cut on that age; a STALE close is reported and segmentable, never pooled with EXCELLENT.
53. **Point-in-time context is as good as the sources on disk at generation time:** weather / Sleeper / ESPN only
    where context captures exist; route participation and red-zone usage are UNKNOWN by construction.
