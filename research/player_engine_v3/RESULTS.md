# Player Engine v3: why the prospective data arm failed, and what fixing it buys (HISTORICAL_RESEARCH)

`scripts/research/player_engine_v3_study.py`. Every model is fitted on seasons <= 2024 and scored on the exact 2025
Kalshi player-prop rungs at the archived horizons (25,000+ rungs, 254 games), against the monotone market midpoint,
with standard errors clustered by game. No 2026 outcome is used anywhere below; 2026 week 2 was used only to
*diagnose* (section 0), never to choose a parameter.

## 0. The prospective symptom (2026 week 2, diagnosis only)

DATA_PLAYER_DIST: Brier 0.1733 vs market 0.1370 (game-level delta +0.0355 +/- 0.0065, 16 games). Its distribution
means were ~60% of the market's on the same player-game (touchdowns ~20%). The autopsy labelled 57,132 rows
SNAP_MISS -- but 67% of them were not large misses at all, and 57,132 rows are 816 player-game-statistics.

## 1. Root cause (Part A: ablation on the held-out 2025 rungs)

| variant (T-90m) | rows | games | Brier - market (clustered) |
|---|---|---|---|
| v2 as historically studied | 17,188 | 253 | +0.0099 +/- 0.0015 |
| **+ target-season lines blanked -> implied_total read as 0** | 17,188 | 253 | **+0.0383 +/- 0.0036** |
| + current-season games excluded (weeks 2-3) | 356 | 30 | +0.0250 +/- 0.0082 |
| both, i.e. what production ran (weeks 2-3) | 356 | 30 | +0.0625 +/- 0.0139 |

`mask_target_season` correctly blanks every target-season closing line (a closing line is never point-in-time);
the data arm then read the NaN implied total and spread through `design()`, which turns NaN into 0.0. A team
expected to score zero points projects almost no volume. **The first defect alone reproduces the whole week-2
deficit (+0.036).** The second -- `load_player_games(range(2013, target_season))` -- meant a week-2 projection
never saw week 1. Neither defect was a modelling choice; both are input wiring, invisible to the historical study
because history always had its lines and its prior weeks.

## 2. v3 (Part B)

v3 = the v2 engine with (a) the market-implied spread/total of the snapshot as the game environment (the same
centre the game engine prices from; never a closing line, never a zero -- no environment means no projection),
(b) completed current-season games (kicked off >= 4 h before the cutoff), (c) the depth-chart QB1 at the cutoff as
the starting quarterback (v2 had no pregame QB source, so every passing statistic was DATA_UNAVAILABLE), and (d)
recency and structural-opportunity features (last-game and last-3 snap / target / carry share, current-season game
count, team change, team volume x share). Distribution families unchanged (Study A of player_engine_v2).

| arm | T-24h | T-6h | T-90m | T-0 |
|---|---|---|---|---|
| v2 | +0.0100 +/- 0.0016 | +0.0099 +/- 0.0016 | +0.0099 +/- 0.0015 | +0.0097 +/- 0.0015 |
| **v3** | +0.0086 +/- 0.0016 | +0.0088 +/- 0.0015 | **+0.0086 +/- 0.0014** | +0.0083 +/- 0.0014 |
| v3 - v2 (paired) | -0.0014 +/- 0.0006 | -0.0011 +/- 0.0006 | -0.0013 +/- 0.0006 | -0.0013 +/- 0.0006 |

By statistic at T-90m (v3 - market): passing TDs -0.0004 +/- 0.0020 (the only statistic at parity), passing yards
+0.0068, receiving yards +0.0096, receptions +0.0139, rushing yards +0.0077, touchdowns +0.0038.

**v3 is a real improvement over v2 and a large one over what production ran, and it is still clearly worse than
the market at every horizon and on every statistic except passing TDs.**

### Hybrids (preregistered protocol: select on 2025 weeks 1-9, confirm on 10-18, T-90m)

| candidate | selection (w1-9) | confirmation (w10-18) |
|---|---|---|
| v3 | +0.0083 +/- 0.0022 | +0.0086 +/- 0.0016 |
| mix 0.5 market | +0.0033 +/- 0.0017 | +0.0022 +/- 0.0009 |
| mix 0.7 market | +0.0014 +/- 0.0010 | +0.0007 +/- 0.0005 |
| mix 0.85 market | +0.0005 +/- 0.0005 | +0.0001 +/- 0.0003 |
| market | 0 (reference) | 0 (reference) |

With the market in the candidate set the protocol selects **the market**. The best hybrid (0.85 market) is
indistinguishable from the market in confirmation and never better. HYBRID_PLAYER_V3 therefore uses 0.85 and is
research: it exists to learn prospectively whether a small data component ever adds information.

## 3. Large disagreement (Part C)

v3 vs market by |v3 - market| at T-90m (2025, held out):

| band | rows | v3 - market |
|---|---|---|
| < 0.5pp | 913 | -0.0001 +/- 0.0001 |
| 0.5-1pp | 935 | -0.0001 +/- 0.0002 |
| 1-2pp | 1,692 | -0.0005 +/- 0.0003 |
| 2-3pp | 1,693 | +0.0006 +/- 0.0005 |
| 3-5pp | 2,983 | +0.0011 +/- 0.0008 |
| 5-10pp | 4,841 | **+0.0045 +/- 0.0014** |
| > 10pp | 4,131 | **+0.0295 +/- 0.0045** |

The same shape appeared prospectively in 2026 week 2 (all arms): 5-10pp +0.0060 +/- 0.0020, >10pp +0.0474 +/- 0.0122.
Large disagreement with the market is where the data model is WORST. `abstention.LARGE_DISAGREEMENT_PP = 5`.

## 4. What this means for production (encoded, not advisory)

* Player props are **market-first**. MARKET_PLAYER_DIST is WATCH (week 2: -0.0005 +/- 0.0003 vs mid, CLV +0.0065,
  net P&L after fees still negative -- it is the market's own ladder, smoothed, not an edge).
* DATA_PLAYER_DIST and HYBRID_PLAYER_DIST are **DISABLED** (known input defect); their records keep being written
  unchanged so their prospective record stays continuous, and no consumer shows their numbers.
* DATA_PLAYER_V3 and HYBRID_PLAYER_V3 are **RESEARCH_ONLY** by construction and every data projection carries
  `ABSTAIN_MODEL_UNVALIDATED` until a statistic earns its way into `abstention.VALIDATED_STATS` through the
  eligibility promotion rules (docs/PRODUCTION_ELIGIBILITY.md).
* Nothing here claims a profitable player-prop model. The honest result is: the market is better, v3 is less bad,
  and the system now says so on every record.
