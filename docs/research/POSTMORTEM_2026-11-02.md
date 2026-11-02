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

## Not done / needs the owner
* Guards and the bet-up-to calculation are **not wired** into `handicap/gates.py`, `preflight.py` or `card.py` (hash-pinned real-money sources, `tests/test_incumbent_unchanged.py`).
  Wiring is a one-call change plus a deliberate pin update. Authorization required.
* The distribution model is research-only: not connected to any pricer, card or model registry.
* The window's fills carry no recommendation, order id or fill ids, and closes for weeks 5-8 are unpublished, so most losses are `INSUFFICIENT_EVIDENCE`.
  That is stated, not filled in. `KXNFLRSHYDSPROT` is not in `kalshi/classifier.py`'s taxonomy.
* Pre-existing on `main`: 20 failing tests (`test_card.py` etc.). Identical set before and after this change.
