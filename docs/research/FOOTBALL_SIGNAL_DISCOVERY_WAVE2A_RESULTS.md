# Football Signal Discovery Lab — Wave 2A (NFL): retrospective replay results

**Kind: RETROSPECTIVE.** These are replays of the frozen Wave-2 rules on earlier games. They are never pooled with
Wave 2, and they change nothing in it: every stream stays `PROSPECTIVE_TRACKING` with NO SETTLED SAMPLE.

* **Protocol:** `FOOTBALL_SIGNAL_DISCOVERY_WAVE2A_PROTOCOL.md`, committed first at `876b453e`.
* **Outputs:** `research/signal_discovery_wave2a/`.
* **Code:**
  * `nfl_edge/signal_discovery/wave2a.py`;
  * `scripts/research/signal_lab_wave2a.py` (`replay` → `report` → `history`);
  * `tests/test_signal_discovery_wave2a_nfl.py` (18 tests).

## 1. Verdict

| Stream | 2026 replay | Replay verdict (pre-registered rule) | Independence |
|---|---|---|---|
| NFL-PROP-PROS-001 RB receptions NO | 83 settled: **ROI +11.7 %** [−9.4 %, +33.2 %], 47–36 | `SUPPORTIVE` | **DISCOVERY-CONTAMINATED.** Wave 1 proposed it from 2025 and 2026 weeks 1–5. |
| NFL-PROP-PROS-002 ROLE_CHANGE | 8 player-games (22 ladders): **model worse**, mean d −7.20 [−17.9, +0.8] | `INSUFFICIENT_REPLAY_DATA` | Partially independent |
| NFL-GAME-PROS-001 totals | 7 qualifying games (all OVER): **2–5**, signed residual −3.99, ROI −45.5 % | `INSUFFICIENT_REPLAY_DATA` | Out-of-time replay |

The RB-NO pattern did carry into 2026 at the frozen checkpoint and the actual NO ask. It beats every comparator
built on the same games:

| Comparator (same games) | ROI |
|---|---|
| NO on every valid rung | +0.4 % |
| NO on the WR/TE receptions natural rung | −1.9 % |
| NO on every stream-stat natural rung | −2.3 % |
| YES on the same natural rung | −20.3 % |

But it is **fragile**: removing the top 5 players gives −7.1 %, and removing the top 5 teams gives −9.5 %. It is
also not independent evidence.

## 2. Population and integrity

* **Population.** Replay games are 2026 REG weeks 1–4 plus the one week-5 game played before this replay
  (TB @ DAL, Oct 8): **65 games**.
  * The other 14 week-5 games (Oct 11–12) had not been played. They belong to neither the replay nor the Wave-2
    population (week ≥ 6).
* **How the frozen job was run.** The replay calls the Wave-2 job's own `stage_observe` / `stage_enter` /
  `stage_settle`, game by game:
  * **observe** at **kickoff − 300 min**. Every observation is generated before kickoff (tested).
  * **enter** at kickoff + 5 min, with close-2.1.0 reading pre-kickoff rows only.
  * **settle** at kickoff + 8 days.
* **Injury input.** It is the timestamped vintage from `market-data`'s vintage index, never the mutable file.
  * Resolved for 63 of 65 games; median retrieval 2.5 h before the cutoff, at most 9.2 h.
  * 62 of the 63 contained the target week's report.
  * The two week-1 games before 2026-09-13 have no vintage: their ROLE_CHANGE rows are
    `INJURY_VINTAGE_UNAVAILABLE`.
* **Depth chart.** The daily snapshot with `dt` ≤ the cutoff.
* **Weekly roster: `ROSTER_NEAR_PIT`, declared.** The roster is the final nflverse file, which carries game-day
  `INA` designations: published before kickoff, but after the observe instant.
  * Across the 65 games it removed 264 skill players who were on the cutoff depth chart (35 RBs).
  * 8 of those 264 had a receptions ladder at the checkpoint, so at most 8 RB-receptions rows could be affected.
* **Settlement.**
  * Contracts use the **exchange's own result**, read from the `market-data` discovery archive
    (`20261008T163830Z`, 66,834 settled KXNFL* markets; the Kalshi API is unreachable here). Labelled
    `EXCHANGE_RESULT_FROM_DISCOVERY_ARCHIVE`.
  * ROLE_CHANGE uses the nflverse stat of players who played.
  * Totals use the final score.
* **Outcome-blind membership.** Doctoring the target game's own player and team rows leaves its frozen observation
  identical (`test_membership_does_not_depend_on_the_target_outcome`, run locally with the data). Observation and
  entry rows carry no outcome field (tested).
* **Frozen code and pins.**
  * The frozen artifacts reproduce (`signal_lab_wave2_artifacts.py --check`).
  * The WF-TOTAL hash `37baf8ec…` is checked.
  * No fitting code exists in Wave 2A (tested).
  * The classifier hash `eeec3777…` is checked.
* **Isolation.** Records live in a scratch directory and in `research/signal_discovery_wave2a/`. Nothing is
  published to `market-data:data/research/signal_lab_wave2/` (tested).

## 3. Coverage

| Step | PROP-001 | PROP-002 | GAME-001 |
|---|---|---|---|
| Games | 65 | 65 | 65 |
| Frozen pregame rows | 118 RB_receptions family rows | 50 ROLE_CHANGE ladder rows (+2 games `INJURY_VINTAGE_UNAVAILABLE`) | 65 with all five football inputs |
| Market at checkpoint | 105 (13 `NO_MARKET`) | 26 (24 `NO_MARKET`) | 65 total ladders in NFL_PRIMARY_60_180 |
| Valid natural rung / median | 86 (19 `NO_EXECUTABLE_QUOTE`: no median) | 22 (4 no median) | 65 centres |
| Rule-eligible | 86 | 22 | **7** (58 `NOT_ELIGIBLE`: \|p\| < 2) |
| Fee known | 86 (KXNFLREC KNOWN) | — | 7 |
| Settled | **83** (3 TB @ DAL `SETTLEMENT_UNAVAILABLE`: no exchange result or stats yet) | **22 ladders / 8 player-games** | **7** |

Identity failures: 0. The identity rule is the Wave-1 resolver (accepted only as NAME_TEAM or NAME_TEAM_JERSEY).

## 4. NFL-PROP-PROS-001: 2025 characterisation (`RETROSPECTIVE_DISCOVERY_CORPUS`)

* **The exact rule is `HISTORICAL_REPLAY_UNAVAILABLE` in 2025.** The archive holds only YES bid/ask candles at
  fixed horizons, with no captured NO ask and no last-pre-kick quote.
* **What is characterised instead** is the Wave-1 basis:
  * NO ask = 1 − YES bid;
  * Wave-1 player rows (players who appeared);
  * the frozen natural rung with the lowest-threshold tie-break;
  * fee engine KNOWN;
  * settlement by the exchange `result`.
* **Wave-1 discovery figures** were always-NO +9.1 % (2025) and +13.4 % (2026).

| 2025 (weeks 9–18) | T-90m (Wave-1 checkpoint) | T-0 |
|---|---|---|
| **Frozen natural-rung NO, RB family** | n 140, ROI **+8.5 %** [−6.1, +22.8], win 59.3 % | n 160, **+7.2 %** [−6.3, +20.5], win 58.1 % |
| ALWAYS_NO on every valid rung (same ladders) | n 574, +3.1 % | n 655, +0.8 % |
| ALWAYS_YES on the natural rung (same ladders) | n 140, **−25.1 %** [−39.8, −10.1] | n 160, −23.6 % |
| ALWAYS_NO on the WR/TE receptions natural rung | n 590, −3.5 % | n 636, −0.8 % |
| Without the top 5 players / top 5 teams | −0.0 % / −0.9 % | −1.9 % / −3.5 % |
| Leave-one-week-out range | +5.2 % … +13.1 % | +4.3 % … +10.3 % |

## 5. NFL-PROP-PROS-001: 2026 replay (weeks 2–4 produced rows)

* **Headline:**
  * 83 contracts, NO at the captured NO ask (mean $0.487) plus a $0.02 fee.
  * 47 wins (56.6 % [45.9, 66.8]); break-even 50.7 %.
  * P/L **+$4.91** on $42.09; ROI **+11.7 %** [−9.4 %, +33.2 %], game-clustered over 44 games.
  * Every contract was settled by the exchange's own result.
* **Concentration:**
  * By week: wk2 +3.4 % (23), wk3 +24.7 % (32), wk4 +3.8 % (28).
  * Leave-one-week-out ranges from +3.6 % (without wk3) to +15.8 %.
  * Leave-one-team-out ranges from +7.0 % (without PIT) to +15.4 %.
  * Without the top player +8.1 %; **without the top 5 players −7.1 %**; **without the top 5 teams −9.5 %**.
  * The top player accounts for 3.6 % of rows; the top 5 players for 18 %.
* **By threshold:** ≥2 −8.5 % (24), ≥3 +18.5 % (35), ≥4 +13.8 % (13), ≥5 +48 % (9).
* **By NO price:** $0.40s +35.4 % (43), $0.50s −10.2 % (32).
* **CLV.** The checkpoint *is* the canonical close (close-2.1.0), so CLV is 0 by construction and not informative.

## 6. Market-structure diagnosis (descriptive)

1. **Is it bid/ask structure?** No.
   * The natural rungs are tight: a 1¢ YES spread on 72 of 83, and a YES ask + NO ask of $1.01 on 72 of 83
     (mean $1.011).
   * NO won because the outcomes fell short: mean actual 2.70 receptions against a mean threshold of 3.04, with
     NO winning 56.6 % at a mean price of $0.487.
   * The mirror ALWAYS_YES on the same rungs lost 20.3 % in 2026 and 25.1 % in 2025: YES is over-priced on this
     ladder.
2. **Concentrated at thresholds or prices?** Thresholds ≥ 3 and NO asks in the $0.40s carried the 2026 result,
   and ≥ 2 lost. The 2025 pattern differs (≥ 2 +10.7 %, $0.40s +12.4 %, $0.50s −9.9 %). These are inconsistent
   subsets, and they are recorded only in the future-hypotheses file.
3. **Stable across 2025 and 2026?** The sign is the same: +8.5 % (2025, Wave-1 basis) and +11.7 % (2026, frozen
   basis). Both intervals include 0, and both disappear when the top 5 players are removed.
4. **Does the natural-rung rule beat ALWAYS_NO?** In both seasons:
   * 2026: +11.7 % against every-valid-rung NO +0.4 %, WR/TE natural NO −1.9 % and all-stat natural NO −2.3 %.
   * 2025: +8.5 % against +3.1 % and −3.5 %.

   It is not a generic NO bias, but the margin is within noise.
5. **Does it survive fees?** Yes on the point estimate: the fee is $0.02 per contract, already included.
6. **A convention creating it?** No settlement or convention artefact was found: there were no pushes, every
   contract had an exchange `result`, and the threshold means ≥ t. What does stand out is a tight market that
   leans to YES on low-volume RB receiving lines.

## 7. NFL-PROP-PROS-002: data reconstruction

* **2016–2025.** All 1,406 Wave-1 ROLE_CHANGE rows were classified with the final weekly injury report, because
  no timestamped vintage exists before 2026-09-13. They are **`INJURY_VINTAGE_UNAVAILABLE`, 0 usable.** Kalshi
  ladders existed only in 2025 anyway.
* **2026 weeks 1–5.**
  * 50 ROLE_CHANGE ladder rows were frozen pregame with a timestamp-safe vintage; 2 games had no vintage.
  * 26 had a ladder at the checkpoint, 22 had a median, and all 22 settled.
  * That is **8 player-games**: 5 QB and 3 RB.

## 8. NFL-PROP-PROS-002: 2026 replay

| | Value |
|---|---|
| n (player-games / ladders) | 8 / 22 |
| Model MAE / market MAE | 30.6 / 23.4 (per player-game mean absolute error over its ladders) |
| Mean d / median d | **−7.20** / −4.25 [−17.9, +0.8]; model better in 37.5 % |
| By family | QB pass yards −24.6 (5) · attempts −4.9 (4) · completions −0.5 (5) · RB rush yards −7.0 (2) · carries −1.0 (2) · receptions +0.1 (2) · rec yards −1.2 (2) |
| Position | QB −11.0 (5), RB −0.8 (3) |
| Concentration | the top player is 37.5 % of rows; without the top team −8.6 |

Descriptive: on QB role changes the frozen projection sat far below the market median, by 44–82 passing yards.

**Secondary economics** (the Wave-1 side rule already in the frozen job): 17 contracts (16 NO), +9.6 %
[−58 %, +79 %]. That is noise; no rule is created.

## 9. NFL-GAME-PROS-001: independence audit

| Question | Answer |
|---|---|
| Were 2026 weeks 1–5 used to fit the frozen model? | **No.** The artifact is the 2026 fold, trained 2015–2025 (n 2,985), and reproduces Wave-1's procedure. |
| Used to choose the features? | **No.** The five features were fixed in Wave-1 set 1 (`e8959411`) before any line was joined. |
| Used to choose \|p\| ≥ 2? | **No.** `pick_threshold_points: 2.0` is in set 1. |
| Used to decide the sign / fade reading? | **No.** It comes from the 2018–2025 folds. |
| Inspected during Wave 1 before the freeze? | **No WF-TOTAL result for 2026 was computed.** Game evaluation covered 2015–2025; 2026 rows existed only as features. Other 2026 game-level research existed in the repo (weekly boards, H2-GC-TOTAL generated from week 2), but none tested WF-TOTAL. |
| Caveat | The Kalshi-ladder translation (market_implied_total at NFL_PRIMARY_60_180) is the new Wave-2 test condition. Wave 1 used the nflverse close. |
| **Label** | **`OUT_OF_TIME_REPLAY`** |

## 10. NFL-GAME-PROS-001: 2026 replay

* **Coverage.** All 65 games had a total ladder center in NFL_PRIMARY_60_180. **7 qualified, all OVER.**

| Game | Wk | Kalshi center | p | Side / contract | Ask + fee | Actual | Signed residual | P/L | CLV |
|---|---|---|---|---|---|---|---|---|---|
| LV @ LAC | 2 | 43.88 | +2.44 | OVER / YES ≥44 | 0.50 + 0.02 | 40 | −3.88 | −0.52 | 0.00 |
| PIT @ NE | 2 | 41.88 | +2.04 | OVER / YES ≥42 | 0.50 + 0.02 | 23 | −18.88 | −0.52 | −0.01 |
| MIN @ TB | 3 | 43.12 | +2.51 | OVER / YES ≥43 | 0.51 + 0.02 | 39 | −4.12 | −0.53 | 0.00 |
| NE @ JAX | 3 | 46.62 | +2.72 | OVER / YES ≥47 | 0.49 + 0.02 | 41 | −5.62 | −0.51 | +0.03 |
| KC @ LV | 4 | 47.90 | +2.54 | OVER / YES ≥48 | 0.50 + 0.02 | 57 | +9.10 | +0.48 | −0.01 |
| LAC @ SEA | 4 | 43.33 | +2.71 | OVER / YES ≥43 | 0.52 + 0.02 | 53 | +9.67 | +0.46 | 0.00 |
| MIA @ MIN | 4 | 39.17 | +2.24 | OVER / YES ≥39 | 0.51 + 0.02 | 25 | −14.17 | −0.53 | 0.00 |

* **Qualified results.** 2–5 (28.6 % [8.2, 64.1]). Mean signed residual −3.99 [−11.1, +3.5], median −4.12.
  P/L −$1.67 on $3.67 (ROI −45.5 %). CLV: 7 of 7 have a close, mean +$0.001.
* **All 65 games, taking the model's direction (comparison only, not a rule):** 37–28 (56.9 %), mean +2.64
  [−0.61, +5.93]; 54 OVER, 11 UNDER.
* **By week (all games):** wk1 +7.68, wk2 −5.87, wk3 +6.56, wk4 +2.95.
* **History (reproducibility).** The Wave-1 folds at \|p\| ≥ 2 against the nflverse close, assumed −110:

  | Season | n | ATS | Mean |
  |---|---|---|---|
  | 2018 | 53 | 54.9 % | +1.58 |
  | 2019 | 23 | 69.6 % | +3.24 |
  | 2020 | 21 | 57.1 % | +6.52 |
  | 2021 | 45 | 56.8 % | +1.39 |
  | 2022 | 40 | 52.5 % | −0.78 |
  | 2023 | 18 | 55.6 % | +0.86 |
  | 2024 | 26 | 57.7 % | +1.83 |
  | 2025 | 17 | 41.2 % | +2.09 |
  | **All** | **243** | **134–106–3, 55.8 %** | **+1.75 [+0.09, +3.45]** |

  The artifact procedure reproduces every fold coefficient exactly.

## 11. Reproducibility

```
python scripts/research/signal_lab_wave2a.py replay --market-data MD --scratch DIR
python scripts/research/signal_lab_wave2a.py report --scratch DIR
python scripts/research/signal_lab_wave2a.py history --market-data MD
```

* `MD` is a `market-data` checkout at `4f049279`.
* nflverse files were downloaded 2026-10-08, with the 2026 schedule refreshed 2026-10-09T04:44Z.
* Bootstrap: seed 20261015, 4,000 draws.
* The raw records and the descriptive baseline ladders are committed (`replay_records_2026.jsonl.gz`,
  `baseline_ladders_2026.jsonl.gz`). Every report carries `code_sha` and the frozen pins.
* The 2025 characterisation needs the gitignored Wave-1 `player_features.parquet` (rebuilt by the Wave-1 script).
