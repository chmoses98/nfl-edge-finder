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

11. **The maker fee multiplier is unknown.** Kalshi's series metadata exposes `fee_type` but not the maker
    coefficient, and the published schedule says it defaults to 0 "unless otherwise indicated" without saying
    what the indicated value is for these series. It is carried as `UNKNOWN` and never defaulted, so
    `net_executable_ev` refuses to produce a net EV for a maker order. This costs nothing operationally —
    passive execution is rejected on core game markets by research/passive (Milestone K), so a real
    recommendation is a taker order and
    the taker path is fully known — but it does mean maker-side research must sweep
    `MAKER_MULTIPLIER_SWEEP` rather than report one number.
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
