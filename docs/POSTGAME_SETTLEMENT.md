# Postgame settlement and evaluation

After a game is FINAL, the pregame shadow observations for it become a SECOND immutable corpus: one evaluation
record per prediction, carrying what the contract paid, what the market's last pregame word was, and how far the
model was from both. The shadow ledger is read and never written.

```
market-data: data/shadow/ledger/<day>/<run>.<model>.observations.jsonl.gz    the predictions (untouched)
market-data: data/kalshi/capture/<day>/<run>.quotes.jsonl                    the quote history (untouched)
nflverse:    schedules/games.csv, stats_player_week_S, snap_counts_S         the result
      |
      v
market-data: data/shadow/evaluations/<game_id>/<eval_version>.<batch>.evaluations.jsonl.gz
                                              <eval_version>.<batch>.evaluation_manifest.json
                                              <eval_version>.<batch>.kalshi_crosscheck.json
market-data: data/shadow/scorecards/<batch>/{scorecard.json,REPORT.md}
```

| piece | file |
|---|---|
| proven results, readiness gate | `nfl_edge/settlement/results.py` |
| nflverse loaders | `nfl_edge/settlement/nflverse_results.py` |
| contract settlement, refusals | `nfl_edge/settlement/settle.py` |
| quote history, close candidates, Kalshi's own result | `nfl_edge/shadow/quote_history.py` |
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
| `REFUSED_PARTICIPATION_UNPROVEN` | the player is absent from a complete snap table, so he took no snap — but INACTIVE settles $0.00 and ACTIVE-but-never-played settles at the pregame fair price, and free data cannot say which |
| `REFUSED_PLAYER_IDENTITY` | the Kalshi player was never resolved to a GSIS id |
| `REFUSED_AMBIGUOUS_SEMANTICS` | no threshold parsed (every `KXNFL2TD` ticker), or a touchdown COUNT that two columns might double-count |
| `REFUSED_NO_FAIR_PRICE` | the no-snap branch applies but no legitimate pregame close exists to be the fair price |
| `REFUSED_RESULT_INCONSISTENT` | the schedule row contradicts itself (`result != home - away`) |
| `REFUSED_GAME_NOT_FINAL`, `REFUSED_GAME_IDENTITY`, `REFUSED_STAT_UNAVAILABLE`, `REFUSED_DIRECTION` | as named |

**A refusal never carries a payout.** `scripts/shadow/validate_evaluations.py` fails the run if one does.

Rows the pricer itself refused (`UNSUPPORTED_*`, `STALE_DATA`, `DEGRADED_INPUT`, `POST_KICKOFF_EXCLUDED`) hold no
model probability, so there is no prediction in them to evaluate. They are counted in the run summary and left
where they are.

## Readiness: why a game sometimes produces nothing

An evaluation is immutable, so a record written from half the evidence is a permanent defect. The trap is a game
whose SCORE is published within minutes while its PLAYER STATISTICS take hours: settling the team markets now and
recording "unavailable" for the player markets would produce refusals that a later run wants to replace with
settlements, which is exactly the contradiction the corpus forbids.

So readiness is decided per game, before anything is written:

* `READY` — final, plausibly finished (4 h past kickoff), and every table its predictions need is populated;
* `DEFER_NOT_FINAL`, `DEFER_STATS_PENDING`, `DEFER_SNAPS_PENDING` — write nothing, report, try again next poll;
* `DEGRADED_INCONSISTENT` — the schedule row contradicts itself.

A deferred game is deferred **whole**. The next run writes its entire truth at once.

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

## Kalshi's own settlements are a cross-check, never the truth

Post-game capture rows carry each market's `result`, so the exchange's actual payout is available for free. It is
written to a separate `kalshi_crosscheck.json` and disagreements are surfaced as warnings — never adopted. The
2025 archive shows why: four markets were settled in a December sweep against their games' own final scores
(including "over **0.5** total points" settled NO on a game that scored 47), and on 2025-09-07 twelve
anytime-touchdown markets paid the no-snap fair price to players who had taken offensive snaps. See
`research/settlement_validation/RESULTS.md`.

That same validation is the evidence the engine is right: **15,009 of 15,021** finalized 2025 markets reproduced
exactly, including every full-game team market.

## Research output

`scripts/shadow/eval_report.py` builds the weekly and cumulative report. Three forecasters on the identical
resolved set — model, market mid at the same snapshot, market mid at the close — with Brier, log loss,
calibration by probability bucket, midpoint and executable CLV, movement toward/away/unchanged/no_view, and
segmentation by family, player statistic, probability band, disagreement band (<3%, 3-5%, 5-10%, 10-20%, 20%+),
direction, time to kickoff (<30m, 30-90m, 90m-6h, 6-24h, >24h), model version, week, game, quote width and
liquidity.

Only `settlement_kind == "binary"` rows enter calibration. A tied game paid $0.50 and a scratched player paid the
pregame fair price; neither is a 0/1 realisation of a football event. They are counted separately.

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
