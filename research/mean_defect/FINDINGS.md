# NFL player mean projection: structural defects, root causes and repairs (2026-10-17)

Trigger: research/intelligence found `shadow-0.4.0` under-predicts receptions, receiving yards and touchdowns on the
2026 prospective corpus (receptions: mean model P 0.199 vs hit rate 0.352 over 4,081 settled contracts).
Method: market-free wherever possible (box score only), strict chronology, incumbent files byte-pinned
(`tests/test_incumbent_unchanged.py`) and untouched. Reproduce with `scripts/research/mean_defect_study.py`.

## Hypotheses tested

| Hypothesis | Verdict | Evidence |
|---|---|---|
| Settlement interpretation | **RULED OUT** | 2026 evaluation `settled_yes` equals `box score >= threshold` for 100% of 20,3xx matched contracts in every stat (1 touchdown row differs) |
| Threshold semantics (>= k vs > k) | **RULED OUT** | pricer reads `S[searchsorted(grid, k)]` = P(Y >= k) on an integer grid; rungs agree with Kalshi's `>=` operator |
| Market-to-player mapping | **RULED OUT** | ticker name token matches `player_name` for 4,040/4,040 autopsied rows |
| Distribution/tail family | partial | the negbin family is fit on mu; its error follows the mean error (see D2 tail) |
| Opportunity/usage assumptions | **CONFIRMED (D1, D2)** | below |
| Calibration | not applied | no probability was recalibrated toward market prices |

## D1 — this season's results never reached the live features (dominant 2026 defect)

`scripts/shadow/price_slate.py` loads `load_player_games(range(2013, target_season))`; completed games of the target season
are never in the history. Each week the player's EWMA just decays and `shrink_w` rises. Autopsy rows for Travis Kelce,
2026 weeks 1-4 (actual targets 5, 11, 2, 4): production `ewma_opportunity` 4.91, 4.80, 4.69, 4.58 and `shrink_w`
0.41, 0.44, 0.47, 0.49; the same features rebuilt with completed games: 4.91, 4.84, 5.76, 5.10 and 0.41, 0.36, 0.32, 0.30.
Across 721 receptions autopsies, week-1 features match exactly (0.468 vs 0.468) and diverge from week 2 (0.491 vs 0.391, 0.548 vs 0.317 by week 4).

## D2 — `shrink_w` is a calendar variable, and the exp link explodes in the usage tail

`add_ewma_features` halves its weights at every season boundary, so `shrink_w` is ~0.41 in weeks 1-6 for EVERY player and
~0.32 late. The count (Poisson) mean models fit it as a feature on whole seasons, where it is mostly a "thin sample" signal,
so established players are cut early in the season. Market-free walk-forward (fit on seasons < T, score box scores,
players with EWMA targets >= 3), weeks 1-6, **frozen design v1**: realised/predicted target gap of -11% to -14% in 2021, 2022, 2023, 2024, 2025
and -18% in 2026; late-season bias about zero. The same model over-projects the top bucket (EWMA 8+: projected 15.6 vs realised 9.6).
Repair (`design="v2"`, count specs only): calendar-free thinness `3/(min(n_prior,16)+3)` and `log1p` usage terms.
Yardage OLS and TD models were tested and **not** changed (no benefit: yardage MAE worse under log terms; TD Brier identical).

### Chronological evidence (ladder Brier on P(Y>=k), listed-like population; lower is better)

| stat | window | player-games | v1 (frozen) | v2 | bias pp v1 -> v2 |
|---|---|---|---|---|---|
| receptions | selection 2021-24, weeks 1-6 | 3,141 | 0.1241 | 0.1193 | -4.4 -> -0.9 |
| receptions | confirmation 2025, weeks 1-6 | 737 | 0.1191 | 0.1148 | -5.0 -> -1.2 |
| receptions | 2026 weeks 1-6 | 665 | 0.1265 | 0.1206 | -6.2 -> -2.6 |
| targets | selection 2021-24 / 2025 / 2026 | 8,878 / 2,150 / 665 | 0.1301 / 0.1265 / 0.1376 | 0.1259 / 0.1228 / 0.1299 | -2.9 / -2.3 / -7.4 -> -0.5 / +0.4 / -2.3 |
| carries | selection 2021-24 / 2025 / 2026 | 3,128 / 767 / 232 | 0.1384 / 0.1276 / 0.1431 | 0.1348 / 0.1249 / 0.1351 | -3.0 / -2.7 / -7.9 -> -1.2 / -1.1 / -4.6 |

v2 wins in every stat and window, including the 2021-24 window in which it was chosen. 2025 and 2026 had been seen when the
defect was diagnosed, so they are confirmation, not untouched; the untouched test is weeks 5+ of 2026 (below).

### Effect on the real 2026 contracts (weeks 1-4, tradable, settled; clusters = player-stat-games)

Features rebuilt point-in-time (completed games included), model fit on seasons < 2026:

| stat | clusters | Brier incumbent (as run) | challenger | market | challenger - incumbent | challenger - market | encompassing b_model | EV at ask |
|---|---|---|---|---|---|---|---|---|
| receptions | 737 | 0.2031 | 0.1765 | 0.1634 | -0.0265 (z -7.9) | +0.0132 (z 4.2) | +0.04 ± 0.13 | -0.014 ± 0.011 |
| carries | 241 | 0.2958 | 0.2571 | 0.2134 | -0.0388 (z -4.9) | +0.0436 (z 3.8) | +0.09 ± 0.18 | -0.016 ± 0.024 |
| receiving_yards | 739 | 0.1829 | 0.1728 | 0.1615 | -0.0101 (z -4.9) | +0.0112 (z 4.3) | +0.01 ± 0.14 | -0.032 ± 0.011 |
| rushing_yards | 358 | 0.1750 | 0.1765 | 0.1532 | +0.0015 (z 0.3) | +0.0233 (z 4.2) | +0.08 ± 0.09 | -0.008 ± 0.014 |

## What this does and does not establish

* Projection ACCURACY: verified improvement for receptions, carries, targets and receiving yards; rushing yards unchanged.
* The market is still better in every stat and the repaired model still carries no incremental information
  (encompassing coefficient indistinguishable from 0, EV at the ask negative). **No betting value is created or claimed.**
* A residual under-prediction remains (receptions: challenger mean P 0.285 vs hit rate 0.352 on listed contracts). It is NOT recalibrated
  away. The listed (traded) population has roles the nflverse-only features do not see (injury-vacated targets, depth chart); that is
  Phase 4C (pre-registered role/availability joins).
* Touchdowns: no design defect found in the TD model; its 2026 shortfall is attributable to D1 and a league-wide TD-rate dip
  (listed-like players, 2026: -5.5pp early, -2 to -6pp in 2024-25 early weeks).
* Frozen baseline: shadow-0.4.0 code and archive are unchanged and pinned; the challenger is `shadow-0.5.0`
  (`scripts/shadow/price_slate_challenger.py`, ledger `data/shadow/ledger_challenger`), wired as a non-blocking step of
  `shadow-price.yml`. Promotion rule: untouched weeks 5+ of 2026, paired cluster Brier vs the incumbent AND no worse vs market; no
  authority change.

---

## Addendum (2026-10-17, later): remaining receptions under-prediction — development data only (2026 weeks 1-4 + 2016-2025)

Weeks 5+ were not used. 737 listed player-games (weeks 1-4), challenger `shadow-0.5.0` mean model:

| component | projected | realised | read |
|---|---|---|---|
| targets (opportunity) | 3.87 | 4.46 (-13%) | the whole gap |
| catch rate | 0.667 | 0.685 | fine |
| receptions | 2.58 | 3.06 | follows targets |

* **Where:** low/mid usage (EWMA 2-4 targets: projected 1.84 / 3.14 vs realised 2.59 / 3.97); the top bucket is right (8.22 vs 8.12). By position RB -29%, TE -16%, WR -8%.
* **Why (evidence, not a fit):** listed players realise **1.113x** their own EWMA targets vs 1.036x for veterans with EWMA >= 3 in weeks 1-4 of 2021-25, and the same veteran population ran 1.071x in 2026. So two things, neither a model-code defect: a **listing-selection effect** (the exchange lists players with realised roles the nflverse-only features cannot see: injury-vacated targets, depth chart) of about +7%, and a **2026 league level shift** of about +3.5% (listed targets per team-game 25.7 realised vs 22.3 projected).
* **Player-level effects:** none (week 1-2 vs 3-4 residual correlation across 175 players = 0.046).
* **Distribution shape:** with the mean right, historical listed-like ladders are calibrated within -0.3 to -1pp (v2, 2021-24) — no shape defect.
* **A population floor** (train only on EWMA >= 1.5 / 2.5 / 3.5) was tested market-free: Poisson deviance moves 0.6% at best (1.787 -> 1.777 on 2021-24, 1.712 -> 1.700 on 2025) and the sign of the bias flips with the floor. That is tuning, not a verified defect, so **it was not adopted**.

**Decision:** no further change to the mean model on development evidence. Two pre-registered hypotheses are carried to the validation weeks (5-8) with the rule frozen now, and the holdout (9+) stays untouched:
1. *H-RECV-1*: the challenger's mean (outcome - model probability) on receptions is smaller in absolute value than the incumbent's in weeks 5-8 (paired, cluster-robust). 
2. *H-RECV-2*: the 2026 level shift persists: realised/EWMA targets for veterans with EWMA >= 3 stays above 1.04 in weeks 5-8.
If H-RECV-2 holds and a role/availability feature (depth-chart or injury-vacated targets, point-in-time) explains the listing effect on development data, that is the next structural candidate; nothing is recalibrated toward market prices.
