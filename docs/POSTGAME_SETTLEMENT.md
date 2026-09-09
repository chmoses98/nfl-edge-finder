# Postgame settlement and evaluation

After a game is FINAL, the pregame shadow observations for it become a SECOND immutable corpus: one evaluation
record per prediction, carrying what the contract paid, what the market's last pregame word was, and how far the
model was from both. The shadow ledger is read and never written.

```
market-data: data/shadow/ledger/<day>/<run>.<model>.observations.jsonl.gz    the predictions (untouched)
market-data: data/kalshi/capture/<day>/<run>.quotes.jsonl                    the quote history (untouched)
nflverse:    schedules/games.csv, stats_player_week_S, snap_counts_S         the result
espn:        scoreboard?dates=YYYYMMDD                                       an independent "complete" flag
kalshi:      GET /markets (public, read-only)                                the exchange's own settlement
      |
      v
market-data: data/shadow/evaluations/<game_id>/<eval_version>.<batch>.evaluations.jsonl.gz
                                              <eval_version>.<batch>.evaluation_manifest.json
                                              <eval_version>.<batch>.kalshi_crosscheck.json
                                              <eval_version>.<batch>.kalshi_settlement_snapshot.json
market-data: data/shadow/scorecards/<batch>/{scorecard.json,REPORT.md}
```

| piece | file |
|---|---|
| proven results, readiness gate | `nfl_edge/settlement/results.py` |
| independent final-status proof (ESPN, postgame tables) | `nfl_edge/settlement/final_status.py` |
| the exchange's own settlement, incl. exact scalar payouts | `nfl_edge/settlement/kalshi_settlement.py` |
| nflverse loaders | `nfl_edge/settlement/nflverse_results.py` |
| contract settlement, refusals | `nfl_edge/settlement/settle.py` |
| quote history and close candidates | `nfl_edge/shadow/quote_history.py` |
| evaluation record, CLV, bands | `nfl_edge/shadow/evaluation.py` |
| append-only store, conflicts | `nfl_edge/shadow/evaluation_store.py` |
| research scorecard and report | `nfl_edge/shadow/eval_scorecard.py` |
| cheap poll gate | `scripts/shadow/settle_gate.py` |
| the settle run | `scripts/shadow/settle_games.py` |
| pre-publish validation | `scripts/shadow/validate_evaluations.py` |
| weekly / cumulative report | `scripts/shadow/eval_report.py` |
| workflow | `.github/workflows/postgame-settle.yml` (every 3 hours, `19 */3 * * *`) |

## What is settled, and what is refused

Settled (full game only), from nflverse final results:

| family | rule | proof |
|---|---|---|
| `GAME_WINNER` | team margin > 0; a tie pays **$0.50 to both sides** | final score |
| `SPREAD` | margin > floor ("wins by more than 3.5") | final score |
| `TOTAL` | total >= K, or > floor | final score |
| `TEAM_TOTAL` | team points >= K | final score |
| `BOTH_TEAMS_SCORE_N` | min(home, away) >= K | final score |
| `PLAYER_STAT` | stat >= K, given a proven snap | `stats_player_week` + `snap_counts` |
| `PLAYER_STAT`, active but never played | the exchange's own `settlement_value_dollars` | a pinned settlement snapshot |

Player statistics with an established settlement column: passing yards, attempts, completions, passing
touchdowns, interceptions, rushing yards, carries, receiving yards, receptions, rushing/receiving touchdowns,
and `touchdowns` (anytime) as the sum of rushing + receiving + special-teams + defensive + **fumble-recovery**
touchdowns.

Refused, with the reason recorded in the row:

| refusal | why |
|---|---|
| `REFUSED_UNSUPPORTED_FAMILY` | `WIN_MARGIN_BUCKET` (bucket bounds are not in the capture schema), `TOTAL_TD` (needs play-by-play attribution rules), `FIRST_TD_SCORER` / `FIRST_TD_TEAM` (need scoring ORDER), `PERIOD_WINNER`, `RACE_TO_N`, `HALF_FULL_RESULT`, `TEAM_STAT`, `GAME_STAT`, `PLAYER_H2H`, `PARLAY`, `COMBO` |
| `REFUSED_UNSUPPORTED_PERIOD` | 1H / 2H / quarter markets: the free schedule feed has no period scores |
| `REFUSED_UNSUPPORTED_STAT` | sacks, tackles, longest reception/rush, field goals, fantasy points, rush+rec yards |
| `REFUSED_PARTICIPATION_UNPROVEN` | the player is absent from a complete snap table, so he took no snap — but INACTIVE settles $0.00 and ACTIVE-but-never-played settles at a scalar value, and free data cannot say which |
| `REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE` | active-but-never-played is **proven**, and the exchange's scalar value is not available. See below |
| `REFUSED_PLAYER_IDENTITY` | the Kalshi player was never resolved to a GSIS id |
| `REFUSED_AMBIGUOUS_SEMANTICS` | no threshold parsed (every `KXNFL2TD` ticker), or a touchdown COUNT that two columns might double-count |
| `REFUSED_RESULT_INCONSISTENT` | the schedule row contradicts itself (`result != home - away`) |
| `REFUSED_GAME_NOT_FINAL`, `REFUSED_GAME_IDENTITY`, `REFUSED_STAT_UNAVAILABLE`, `REFUSED_DIRECTION` | as named |

**A refusal never carries a payout.** `scripts/shadow/validate_evaluations.py` fails the run if one does.

Rows the pricer itself refused (`UNSUPPORTED_*`, `STALE_DATA`, `DEGRADED_INPUT`, `POST_KICKOFF_EXCLUDED`) hold no
model probability, so there is no prediction in them to evaluate. They are counted in the run summary and left
where they are.

## The scalar branch: an exact payout or nothing

A player who is **active but never takes a snap** settles at a value the EXCHANGE computes and publishes
(`settlement_value_dollars`). Nothing in nflverse knows that number.

`nfl_edge/settlement/semantics.py` uses a contemporaneous midpoint as a pricing-time PROXY for this branch, which
is the right thing to do when pricing. Recording that proxy as the payout would put a number this project
invented into an immutable corpus and then score the model against it. So:

* `settle_observation` has **no parameter that accepts a price** — not a midpoint, bid, ask or last trade. The
  proxy cannot become a settlement by accident, and a test asserts the signature stays that way;
* the exact value is read only from the exchange: a **settlement snapshot** captured at settle time from the
  public `GET /markets` surface, or the historical archive on `market-data` for older seasons;
* without it the row is `REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE` with `settled_yes = null`, while
  `settlement_evidence.participation_branch = "active_no_snap_proven"` records that the football fact WAS
  proven. The legitimate pregame close stays in the close fields as research evidence.

**The snapshot is pinned.** It is written once per game, into the game's evaluation directory, and every later run
reads that file instead of re-reading the exchange. A run that could not reach the exchange still writes a
snapshot — an empty one, recording the failure — so the absence of an exact payout is pinned too and a rerun
reproduces the same refusal rather than contradicting it.

The 10-minutely capture is not a source for this: it fetches `status=open`, so a settled market has already left
the set it looks at. Across 1,211,807 captured NFL quote rows every one carries `status="active"` and none carries
a settlement.

## Readiness: why a game sometimes produces nothing

An evaluation is immutable, so a record written from half the evidence is a permanent defect. The trap is a game
whose SCORE is published within minutes while its PLAYER STATISTICS take hours: settling the team markets now and
recording "unavailable" for the player markets would produce refusals that a later run wants to replace with
settlements, which is exactly the contradiction the corpus forbids.

So readiness is decided per game, before anything is written:

* `READY` — final is PROVEN, and every table its predictions need is populated;
* `DEFER_NOT_FINAL` — no scores, or scores without the postgame-only fields (a provisional row);
* `DEFER_FINAL_UNPROVEN` — the score fields look final but nothing independent attests the game is complete;
* `DEFER_STATS_PENDING`, `DEFER_SNAPS_PENDING` — write nothing, report, try again next poll;
* `DEGRADED_INCONSISTENT` — the evidence contradicts itself, or two sources disagree.

A deferred game is deferred **whole**. The next run writes its entire truth at once.

## What counts as FINAL

A populated score is not a final status and elapsed time is not evidence: nflverse rebuilds `games.csv` on a
schedule, so a row can carry a score while the game is still being played. FINAL requires **all** of:

1. `home_score` and `away_score` present;
2. the postgame-only fields present and agreeing with them — `result == home - away`, `total == home + away`, and
   an `overtime` flag. nflverse computes these when it processes a finished game, so their absence beside a
   populated score is the signature of a provisional row: that defers, whatever the clock says;
3. at least 4 h past kickoff (necessary, never sufficient);
4. an **independent attestation** that the game is complete:
   * `postgame_tables` — the game appears in the postgame-only `stats_player_week` AND `snap_counts` releases
     (primary; needs no network beyond the downloads the job already makes), or
   * `espn_scoreboard` — ESPN's explicit `status.type.completed`, joined by the schedule's own `espn` event id.

ESPN can only ADD a proof or REVEAL A CONTRADICTION; it is never required. An ESPN outage cannot stop settlement,
and an ESPN disagreement about the score or the completion state stops it cold. Which source proved it travels
into every settled row as `settlement_evidence.final_proofs`, and the pre-publish validator rejects a settled row
that carries none.

## The close

The last **complete** quote **strictly before** kickoff, chosen per ticker from the 10-minutely capture (not from
the 2-hourly ledger, whose last pregame snapshot can be two hours old). Every snapshot of a ticker is scored
against that one close, which is what makes CLV comparable across horizons.

* a post-kickoff quote is never a close — `validate_evaluations.py` re-checks this on every published row;
* one-sided quotes are skipped: half a book cannot make a midpoint;
* no valid pregame quote is `MISSING_CLOSE`, recorded, with no CLV invented;
* a close more than an hour before kickoff is `OK_STALE`: kept, flagged, excluded from the headline CLV numbers
  and reported in its own block. Neither hidden nor mixed in.

Kickoff comes from the schedule (`gameday` + `gametime`, US-Eastern → UTC via `nfl_edge/data/nfl_calendar.py`).
If it disagrees with the kickoff stamped on the predictions by more than a minute, no close is chosen at all: a
wrong kickoff silently changes which quote is the close.

## Immutability and reruns

Identity is `(prediction_id, evaluation_version)`; `evaluation_id = sha1(prediction_id|evaluation_version)`.
Each run writes a NEW batch file containing only rows the corpus does not already have, so every published file
is write-once and the corpus is the union of its batches.

| rerun sees | outcome |
|---|---|
| nothing new | **NO-OP** — no file created, existing bytes untouched |
| new predictions | only those are written, in a new batch |
| a different truth for an existing prediction | **CONFLICT** — the run fails (exit 4), nothing is written, every changed field is named |

A conflict is resolved by fixing the input that changed, or by bumping `evaluation_version` — which records the
new reading *alongside* the old one rather than replacing it. `evaluated_at` is excluded from the content hash,
so recomputing the same evidence at a different time is a no-op rather than a conflict.

Manifests carry counts, the batch sha256, hashes over the prediction ids and content hashes, the game's result
evidence, the kickoff and its source, the ledger snapshots consumed, and the result-source provenance.

## The exchange's own settlements are a cross-check, never the truth

The pinned settlement snapshot is compared with our proven settlements per ticker, written to a separate
`kalshi_crosscheck.json`, and disagreements are surfaced as warnings — never adopted. The 2025 archive shows why:
five markets were settled in bulk sweeps against their games' own final scores (including "over **0.5** total
points" settled NO on a game that scored 47), and on 2025-09-07 twelve anytime-touchdown markets paid the no-snap
scalar to players who had taken offensive snaps.

The one thing the exchange IS authoritative for is its own scalar settlement value, because that value is not a
football fact — it is a number the exchange computes. That is the only place its word is used as truth.

`research/settlement_validation/RESULTS.md` carries the evidence, with every bucket reconciled: **61,557**
finalized 2025 archive markets examined, **15,021** independently comparable settlements, **15,009** agreements
(0.99920). `BOTH_TEAMS_SCORE_N` has no archived markets at all, so its evidence is the rules text and the unit
tests and the report says so.

## Research output: two spaces, three sample units

`scripts/shadow/eval_report.py` builds the weekly and cumulative report.

**Two spaces, never one table.** The ledger stores `model_event_probability` (P(football event | on the field))
and `model_contract_value` (E[payout of one YES contract]) as different numbers, because for a player prop they
are different: the contract value carries a participation discount that has nothing to do with football.

| block | what is scored | metrics |
|---|---|---|
| event-probability calibration | `model_event_probability` vs the 0/1 realisation, on rows whose payout is binary (which is exactly when participation semantics let the event be observed) | Brier, log loss, calibration by probability bucket, actual event rate |
| contract-payout quality | `model_contract_value`, the market midpoint and the closing midpoint vs the ACTUAL payout, on rows whose payout is exactly known | mean squared / absolute / signed payout error. **No log loss** — a $0.07 scalar payout is not a Bernoulli outcome |

The market lives in contract space, because a midpoint is a price. It appears in the event table only for the
subset where the two spaces provably coincide (no participation branch), and is labelled as such.

**Three sample units, and no effective N.** The corpus holds every pregame snapshot: 27 snapshots of the same 401
NE-SEA tickers is 9,830 rows describing 401 contracts in one game. Every metric is computed over an explicit unit:

| unit | definition |
|---|---|
| `raw` | all snapshots. Descriptive diagnostics, labelled as repeated and correlated — never a sample size |
| `latest_pregame` | **primary.** One row per (game, ticker): the smallest positive `minutes_to_kickoff`, ties broken on `(observed_at, prediction_id)` |
| `T-24h` / `T-6h` / `T-90m` / `T-30m` | one row per (game, ticker) per horizon, by the rule below |

The horizon rule, stated once so no report can quietly use another: candidates are snapshots with
`minutes_to_kickoff >= target` (a later snapshot knows things the horizon did not); among those the smallest
`minutes_to_kickoff` wins — the freshest information a decision at T-target could have had; and the winner counts
only if it is within **120 minutes** of the target, which is the shadow pricer's own 2-hourly cadence. Otherwise
the contract is **unavailable** at that horizon and is reported as such. Every selected row keeps and reports its
ACTUAL distance to kickoff, so no label has to be trusted on its own.

Observations, unique contracts and games are printed beside every number. Nothing computes an "effective N".

Segmentation (on the contract view) by family, player statistic, contract-value band, event-probability band,
disagreement band (<3%, 3-5%, 5-10%, 10-20%, 20%+), direction, time to kickoff, model version, week, game, quote
width and liquidity.

Availability state, `p_plays` and `p_inactive` are copied onto every row so ruled-out-player shocks,
replacement-role changes and post-injury-news movement can be studied later against
`data/shocks/` — without re-deriving anything.

**Nothing here promotes a model change.** One week is a handful of games and a Brier difference of a few
thousandths on a few hundred correlated contracts is not evidence.

## Running it by hand

```bash
git worktree add -f /tmp/md origin/market-data
python3 scripts/data/nflverse_download.py --only schedules,stats_player,snap_counts,players --seasons 2026-2026

python3 scripts/shadow/settle_gate.py --market-data /tmp/md            # is there anything to do?
python3 scripts/shadow/settle_games.py --market-data /tmp/md --dry-run # plan, write nothing
python3 scripts/shadow/settle_games.py --market-data /tmp/md --game 2026_01_NE_SEA
python3 scripts/shadow/validate_evaluations.py --root data/shadow/evaluations --market-data /tmp/md --require-rows
python3 scripts/ci/publish_market_data.py --src data/shadow/evaluations --message "shadow evaluations ..."
python3 scripts/shadow/eval_report.py --market-data /tmp/md --week 1 --out data/shadow/scorecards/manual
```
