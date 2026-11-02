# Postmortem repairs, 2026-11-02 (issue #231)

Public repository: this document and `research/postmortem_2026-11-02/` carry **counts, flags and held-out statistics only**.
Per-position detail (tickers, stakes, P&L) is produced only with `--private-out` to a path outside the repository.

## Verification of the issue's figures
Recomputed locally from the `handicap-data` ledger (imported wagers + settlements + amendments, canonical net = gross - stake): the
window 2026-10-22..2026-11-01 has 45 settled positions (46 fills, one open), net loss and the SF spread-ladder loss **match the
issue**. The two SF rungs were one thesis (`MARGIN:SF`) held at more than 5U combined; `exposure.py` now reports exactly that.
Stake already contains the entry fee (router-settlement-economics.v2); fees are **not** subtracted again.

## What was added (`nfl_edge/postmortem/`, all pure, no network, no writes)
| module | purpose |
|---|---|
| `ontology.py` | contract classification. `KXMVECROSSCATEGORY*` combos are `COMBO_UNDECODED` unless leg records are supplied; legs are never guessed |
| `reconcile.py` | frozen per-fill record: recommendation link (`attribution.link_fill`), model/availability evidence, fills+fees, canonical vs as-filed settlement, close and CLV; `MISSING_*` flags; sha256 per record |
| `fairvalue.py` | whole-order fee-inclusive break-even (real `FeeSchedule.entry_fee`), calibrated fair probability with bounds from held-out reliability cells, bet-up-to; `None` when calibration or fee is missing |
| `guards.py` | restriction-only point-in-time guards for game-level markets: projection, injuries, **confirmed** QB for both teams, quote age/provenance (captured vs executable), kickoff |
| `exposure.py` | thesis axes (`MARGIN:<team>`, `TOTAL:*`, `TEAMSCORE:<team>:*`), cross-axis links, game and daily units; **flags** > 5U/game and > 15U/day, never caps |
| `distributions.py`, `dist_eval.py` | integer-support key-number distributions and the walk-forward held-out evaluation |
| `loss_eval.py`, `report.py` | loss decision tree, window null test with clustered bootstrap, redacted JSON + dashboard |

## Held-out distribution results (`research/postmortem_2026-11-02/distribution_eval.json`)
Fit 2019 onward; ridge strength and bandwidth chosen on 2022-23; **test 2024 and 2025**, every game predicted from earlier seasons only.
Mean exact-outcome log score, paired difference per game with 90% game-clustered bootstrap interval:

* Key-number kernel (market location) **vs the incumbent residual bank**: final margin +0.177 [0.123, 0.231], team points +0.176
  [0.143, 0.208], game total +0.061 [0.015, 0.108]. On final margin the predicted mass on training-emergent key numbers is 34-36% (realised 32-38%); the incumbent
  predicts 23-24%.
* **Opponent-adjusted EPA / pace / schedule / special-teams evidence vs market-only location: no held-out gain on any target** (game total and
  1H team points are slightly worse, the rest not distinguishable from zero). The closing line already prices this information.
  Verdict `NOT_DEMONSTRATED`; nothing here should be activated on that basis.
* Anchor caveat: the centre is the closing consensus line (no historical Kalshi 1Q/1H/team-total quotes exist in nflverse). This is a shape and
  location test, not a profit backtest. Injury and confirmed-QB history for 2019-2025 is not available point-in-time in this repo, so it enters only via the line.

## Wired into RUN NFL (owner-approved on PR #232, 2026-11-02)

Restriction-only: these can turn an approval into a block or add a flag; they cannot add a bet, raise a stake or a ceiling, or re-rank anything.
Logic lives in `nfl_edge/postmortem/integration.py`; `gates.py`, `preflight.py` and `card.py` only call it. 1U = $75 (one constant).

| where | what |
|---|---|
| `card.py` `candidate_record` | every record carries a `pit_evidence` block: `projection_as_of`, `injuries_as_of` (from the packet's own timestamps; None if absent), `qb` (ONLY from `run["qb_confirmations"]`), `bet_up_to_provenance`, key-number-distribution provenance |
| `gates.py` `game_level_pit_evidence` | projection <= 180 min, injuries <= 180 min, BOTH quarterbacks `CONFIRMED_STARTER` with a time before the decision, executable ask <= 15 min old (judged from the gate's own resolved quote, never a capture), kickoff. Player markets keep `player_availability_resolved` |
| `gates.py` `order_size_fee_inclusive_ceiling` | the record's `bet_up_to_probability` must not exceed the whole-order, fee-inclusive bound from the analyst's declared fair range (2.0c margin = the existing `MIN_NET_EDGE`). FAIL only; UNAVAILABLE if the range, stake or fee schedule is missing. Labelled `ANALYST_DECLARED_UNCALIBRATED`; a calibrated bet-up-to is `None` (`MISSING_CALIBRATION`) because no held-out cells exist for thesis-conditioned fair values |
| `card.py` / `preflight.py` | `exposure_flags`: > 5U ($375) per game, > 15U ($1,125) per day, > 5U per thesis axis, including the owner's open book; flags only. Public card keeps flag kinds and locations, withholds amounts |
| `scripts/handicap/run_card.py` | new optional `--qb-confirmations FILE` (`{TEAM: {status: CONFIRMED_STARTER, confirmed_at, source}}`) |

**Consequence the owner should expect:** with no `--qb-confirmations`, every game-level score line is BLOCKED `QB_UNKNOWN:<team>`. That is the intended fail-closed
behaviour, not a bug. No source of confirmed starters exists in the repo yet (the depth chart is not a confirmation and is never relabelled as one), and
`run-nfl.yml` does not pass the file. Until a confirmation feed is wired into the workflow, RUN NFL will show candidates but no game-level BET.
Records written before `pit_evidence` existed are not re-judged, so replaying history cannot change a historical verdict.

Pins updated deliberately (separate commit): `gates.py` 2821835860e32f3e -> a0d03cb7af6bab98, `preflight.py` b32665e82cf0b994 -> a606567c3bfdb841,
`risk.py` in `test_postgame_workflow.py` e7af977ea69a524b -> 54fb66955d79705b (re-sync to the owner-reviewed 2026-11-01 pin; `risk.py` itself is unchanged),
plus `tests/wiring_pins.py` for `card.py` and the postmortem modules the gates call.

## A production crash found and fixed on the way

`challenge.py` item C10 compared open exposure to `game_cap_units`, which is `None` under the owner's 2026-11-01 policy (`risk.py` already handled `None`).
`run_card` therefore raised `TypeError` for every thesis that reached the challenge. This is 18 of the 20 clean-main test failures. With no cap, open
exposure is now a FLAG (never a FAIL); the 5U thesis-group limit and the > 5U/game review flag still apply. See `tests/known_failures_2026-11-02.txt`.

## Closing prices (weeks 5-8)

Run 41513363507 of `shadow-v2-settle.yml` died in its market-data fetch step ("error: unable to write file data/shadow/v2/projections/...", "No space left on
device"), so the close/CLV step and everything after it was skipped. The workflow was the one in its family without the `scripts/ci/free_runner_disk.sh` step.
It is added (with a test that it precedes the fetch). **Not dispatched and unverified**: whether it restores closes needs one run, which is the owner's call.
The earlier "cancelled at its job limit" explanation applied to October and was already addressed by the bounded drivers.

## Not done / needs the owner
* A confirmed-quarterback feed (inactive list / team announcement) wired into `run-nfl.yml` and passed as `--qb-confirmations`. Until then game-level lines block.
* Dispatching `shadow-v2-settle.yml` to verify the disk fix, then re-running the loss classification with the closes.
* The distribution model is research-only: not connected to any pricer, card or model registry (`key_number_distribution.used_by_card` is `False` on every record).
* The window's fills carry no recommendation, order id or fill ids (router side); `reconcile.py` now accepts `order_id`, `kalshi_order_id`, `fill_ids`, `kalshi_fill_ids`
  the moment they appear. `KXNFLRSHYDSPROT` is still not in `kalshi/classifier.py`'s taxonomy: nothing in this repo establishes what it settles on, so it is not guessed.
