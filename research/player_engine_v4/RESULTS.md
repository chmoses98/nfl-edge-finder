# Player Engine v4: a structural challenger, and how far it closes the gap to the market (HISTORICAL_RESEARCH)

Reproduce: `python3 scripts/research/player_engine_v4_study.py --market-data <market-data> --frame <frame.pkl>` and
`python3 scripts/research/player_engine_v4_upstream.py --frame <frame.pkl>` (the frame -- the 2013-2025 player-game
table with v2 / v3 / v4 features -- is built by `scripts/research/player_engine_v4_frame.py`). Outputs `results.json`, `upstream.json`.

**Protocol.** Every model is fitted on seasons 2014-2024 (EWMA features from 2013); nothing from 2025 or 2026 enters a
fit. The test set is the 2025 regular season's Kalshi player-prop rungs (26,510 rungs, 247 games with an environment).
Scores are paired Brier differences against the monotone market midpoint (quote width <= 10c), **clustered by game**
(thousands of rungs from one game are not independent); a player-game cluster is also recorded in `results.json`.

**Environment, point in time (new).** v3's study priced every horizon from the nflverse closing spread/total -- a
close is not available at T-24h. Here each horizon's game environment is the median of *that horizon's* Kalshi
full-game SPREAD and TOTAL ladders; a horizon with no liquid game ladder gets no environment and no data distribution
(v3 and v4 alike), as in production. v3 is re-scored under the same environment (its close-environment number is
kept only to reproduce the v3 study: +0.0086 at T-90m, identical). 2026 is not used anywhere below.

## 1. Headline (common rows: both v3 and v4 priced the rung)

| horizon | rows / games | v3 - market | **v4 - market** | v4 - v3 | ECE v3 / v4 / market |
|---|---|---|---|---|---|
| T-24h | 14,207 / 234 | +0.0085 +/- 0.0016 | **+0.0046 +/- 0.0014** | -0.0039 +/- 0.0010 | 0.019 / 0.008 / 0.015 |
| T-6h | 15,388 / 247 | +0.0087 +/- 0.0015 | **+0.0042 +/- 0.0012** | -0.0045 +/- 0.0010 | 0.020 / 0.007 / 0.016 |
| T-90m | 16,982 / 247 | +0.0084 +/- 0.0014 | **+0.0043 +/- 0.0012** | -0.0041 +/- 0.0010 | 0.019 / 0.008 / 0.018 |
| T-0 | 18,327 / 247 | +0.0083 +/- 0.0014 | **+0.0045 +/- 0.0012** | -0.0039 +/- 0.0009 | 0.019 / 0.009 / 0.020 |

T-90m Brier: v3 0.1973, **v4 0.1931**, market 0.1888. Log loss: v3 0.5771, v4 0.5674, market 0.5562.

**v4 halves v3's deficit (about four standard errors, at every horizon) and is better calibrated than both v3 and
the market's own midpoint -- and it is still worse than the market at every horizon.** v4 also prices 1,280 more
T-90m rungs than v3 (quarterback rushing yards and QB anytime-TD, which v3's population masks exclude).

## 2. By statistic (T-90m, common rows)

| statistic | rows / games | v3 - market | v4 - market | better than market? |
|---|---|---|---|---|
| passing TDs | 592 / 89 | -0.0007 +/- 0.0020 | **-0.0013 +/- 0.0020** | parity (not significant) |
| passing yards | 2,221 / 176 | +0.0067 +/- 0.0025 | +0.0035 +/- 0.0019 | no |
| receiving yards | 5,633 / 174 | +0.0091 +/- 0.0021 | +0.0059 +/- 0.0020 | no |
| **receptions** | 3,631 / 124 | +0.0141 +/- 0.0030 | **+0.0051 +/- 0.0023** | no (gap cut by 64%) |
| rushing yards | 1,989 / 162 | +0.0076 +/- 0.0041 | +0.0046 +/- 0.0039 | no |
| rushing yards incl. QBs (v4 only) | 2,834 / 164 | -- | +0.0021 +/- 0.0031 | no |
| touchdowns | 2,916 / 246 | +0.0038 +/- 0.0012 | +0.0019 +/- 0.0010 | no |

No statistic got worse. Receptions -- the clearest v3 weakness -- improved the most. Only passing TDs is at parity,
as it was for v3.

## 3. Ablations (T-90m, v4 - market, each refits the bundle with one stage switched to what v3 used)

| configuration | v4 - market | ECE |
|---|---|---|
| v3 (reference) | +0.0084 | 0.019 |
| structural chain with every stage off (EWMA snap, EWMA shares, team-EWMA volume, constant dispersion) | +0.0073 | 0.015 |
| + snap model and role allocation | +0.0054 | 0.005 |
| + team-volume model | +0.0050 | 0.004 |
| + teammate redistribution | +0.0043 | 0.004 |
| + uncertainty propagation (= full v4) | +0.0043 | 0.008 |
| full minus role allocation | +0.0071 | 0.015 |
| full minus game environment (market spread / total) | +0.0062 | 0.011 |
| full minus teammate redistribution | +0.0051 | 0.010 |
| full minus team-volume model | +0.0049 | 0.012 |
| full minus snap model | +0.0045 | 0.008 |
| full minus uncertainty propagation | +0.0043 | 0.004 |

* **Role allocation is the largest single contributor** (+0.0028 when removed), then the market game environment
  (+0.0019; mostly passing statistics), teammate redistribution (+0.0008), team volume (+0.0006), snap (+0.0002).
* **Uncertainty propagation adds nothing measurable** (0.0000) and its calibration is slightly worse (ECE 0.008 vs
  0.004). It is kept in the frozen v4 because it was specified before scoring; removing it on this evidence would be
  selecting on the test set. It is the first candidate for a v4.1.
* The snap model's large upstream gain (section 5) buys little Brier on its own: the allocation model already sees the
  player's recency, so predicted snaps mostly re-express information the share model has.

## 4. Hybrid (preregistered: select on 2025 weeks 1-9, confirm on 10-18, T-90m)

| candidate | selection w1-9 | confirmation w10-18 | all T-90m |
|---|---|---|---|
| v4 | +0.0060 +/- 0.0021 | +0.0039 +/- 0.0014 | |
| mix 0.5 market | +0.0024 +/- 0.0017 | +0.0003 +/- 0.0008 | |
| mix 0.7 market | +0.0009 +/- 0.0010 | -0.0003 +/- 0.0005 | |
| **mix 0.85 market (HYBRID_PLAYER_V4)** | +0.0003 +/- 0.0005 | **-0.0003 +/- 0.0003** | -0.0003 +/- 0.0002 |
| HYBRID_PLAYER_V3 (mix 0.85 of v3) | +0.0005 +/- 0.0005 | +0.0001 +/- 0.0003 | +0.0001 +/- 0.0002 |
| adaptive (per-family weight in {0.5, 0.7, 0.85, 1.0}) | chose 1.0 for 4 of 5 families | -0.0002 +/- 0.0001 | -0.0002 +/- 0.0001 |

With the market in the candidate set, the protocol again selects **the market**. The best hybrid (0.85 market) is
indistinguishable from it (z about -1), marginally better than HYBRID_PLAYER_V3 -- a small, unproven improvement.
The adaptive blend collapsed to the pure market for four of five families and is no better than the global blend,
so it was rejected. **HYBRID_PLAYER_V4 = global 0.85-market pmf mixture**, floored at 0.85.

## 5. Upstream diagnostics (every 2025 player-game; `upstream.json`)

**Snap share** (V3 = the EWMA snap share v3 uses):

| slice | n | V3 MAE | **V4 MAE** | V3 RMSE | V4 RMSE |
|---|---|---|---|---|---|
| all | 6,381 | 0.154 | **0.120** | 0.200 | 0.166 |
| QB | 674 | 0.184 | **0.083** | 0.282 | 0.163 |
| RB | 1,416 | 0.127 | 0.107 | 0.160 | 0.141 |
| WR | 2,629 | 0.167 | 0.137 | 0.208 | 0.183 |
| TE | 1,662 | 0.144 | 0.120 | 0.179 | 0.158 |
| v4 high certainty (sd <= median) | 3,191 | 0.130 | 0.095 | | |
| v4 low certainty (sd > median) | 3,190 | 0.178 | 0.145 | | |
| returning from absence | 398 | 0.199 | 0.141 | | |
| new to the team | 427 | 0.279 | 0.172 | | |
| teammate vacated > 20% of snaps | 801 | 0.196 | 0.159 | | |
| stable role | 4,772 | 0.138 | 0.113 | | |

The same gain holds walk-forward in 2023 (0.155 -> 0.120) and 2024 (0.156 -> 0.121). V3's snap estimate is biased
+0.19 for new-to-team players and +0.10 for returning players; v4's is within +/-0.02. The 80% snap interval covers
71% (under-dispersed; the sd calibration is in-sample).

**Team volume** (2025 team-games, 544):

| metric | V3 (team EWMA) | V4 | league constant |
|---|---|---|---|
| pass attempts: bias / MAE | +0.75 / 6.16 | +0.47 / 6.09 | +0.88 / 6.36 |
| rush attempts: bias / MAE | -0.95 / 5.84 | -0.34 / 5.76 | -1.57 / 6.00 |
| plays: bias / MAE | -0.20 / 6.66 | +0.12 / 6.72 | |

Team volume remains close to unpredictable (research/opportunity found the same). **The "~11% team-volume
under-projection" seen in 2026 production was not a volume-input defect**: the team EWMA was within 2% of the 2026
week-1/2 actuals; the 11% came from the v2 opportunity GLM reading a zero implied total (fixed in v3). V4 removes most
of the remaining rush-attempt bias; it does not make volume predictable.

**Allocation**: target-share MAE 0.0492 -> **0.0443** (no redistribution 0.0448); carry-share 0.0501 -> 0.0438
(0.0447). On teammate-absence rows: target share 0.0573 -> 0.0514 (without redistribution 0.0530, bias -0.0135 ->
-0.0033); carry share 0.1178 -> **0.0977** (without redistribution 0.1106, bias -0.0525 -> -0.0237). Counts: targets
MAE 1.688 -> 1.537, carries (RB) 3.736 -> 3.368, receptions 1.264 -> 1.175. Reconciliation: before the cap, the
predicted target shares of a team-game exceeded 1 in 34% of team-games (carries 47%); after it the mean sum is 0.935
against a realised 0.940.

## 6. Teammate absence

Sample: 2014-2024 fits; 2025 has 565 receiving and 174 rushing player-games with a new same-group absence (>5% of
the group's share vacated), 1,366 T-90m rungs in 122 games. Method: the recent role of every teammate ruled out
pregame (report OUT / DOUBTFUL, or not on the active roster; gameday inactives excluded so T-24h means the same
thing) whose last game was the team's last game; who absorbs it is learned from each player's share of the available
group, pooled across all teams (no team- or player-specific absence rules). Result: V3 +0.0266 -> V4 +0.0122 vs the
market on those rungs (still clearly worse than the market); carry-share error on absence rows -12% vs no
redistribution. Weak: returning players (+0.0283 vs market) and the tail of large role shocks remain poor.

## 7. Where v4 is and is not useful (T-90m segments, v4 - market; v3 in brackets)

stable role +0.0025 (+0.0061); starter +0.0032 (+0.0078); rotational +0.0069 (+0.0097); committee RB +0.0080
(+0.0094); teammate absence +0.0122 (+0.0266); returning +0.0283 (+0.0333); changed team -0.0007 +/- 0.0087 (n 106);
questionable -0.0039 +/- 0.0106 (n 89). **V4 is closest to the market for stable starters and worst for role
transitions.**

## 8. Disagreement and abstention

v4 by |v4 - market|: < 5pp about the market (-0.0002 .. +0.0002); 5-10pp +0.0036 +/- 0.0014; > 10pp **+0.0165 +/-
0.0054** (v3: +0.0042 / +0.0294). Large disagreement is less damaging than for v3 and **still where the model is
worst** -- it stays a caution (PROJECTION_LOW_CONFIDENCE), never an edge.

**Does anything separate useful disagreement from model failure?** Within the 8,401 T-90m rungs where v4 differs from
the market by more than 5pp (+0.0084 +/- 0.0024 overall):

| split | yes | no |
|---|---|---|
| stable role | +0.0041 +/- 0.0032 | +0.0131 +/- 0.0035 |
| low snap uncertainty (sd <= 0.12) | +0.0038 +/- 0.0029 | +0.0118 +/- 0.0035 |
| starter (snap >= 0.6) | +0.0056 +/- 0.0026 | +0.0142 +/- 0.0046 |
| teammate absence | +0.0216 +/- 0.0098 | +0.0072 +/- 0.0025 |
| returning player | +0.0505 +/- 0.0174 | +0.0072 +/- 0.0025 |
| model above the market | +0.0110 +/- 0.0034 | +0.0066 +/- 0.0033 |

Role stability and snap certainty explain *where the damage is*, but no subgroup makes large disagreement
better than the market: the best (stable role, low snap sd) is still +0.004 worse, just not significantly. There is
no validated "useful disagreement", so large disagreement remains an abstention condition for every v4 row.

Abstention v4 (`abstention.decide_v4`, thresholds set before scoring): accepted (structurally valid, <= 5pp)
7,790 rungs at **+0.0001 +/- 0.0003** (parity, partly by construction of the 5pp rule); abstained 10,472 at +0.0066.
By reason: role uncertain +0.0217, teammate shock +0.0171, snap uncertain +0.0057, large disagreement +0.0045.

## 9. Verdict

* DATA_PLAYER_V4 is a real, structural improvement on v3: every statistic, every horizon, better calibration.
* It is still worse than the market. It is RESEARCH_ONLY, and historical results qualify it for prospective
  collection only -- never for promotion.
* HYBRID_PLAYER_V4 (0.85 market) is indistinguishable from the market; it is research.
* Prospective collection starts with this PR; promotion requires the eligibility layer's prospective evidence
  (>= 48 games over >= 3 weeks, upper-95 Brier delta <= 0.002, calibration, CLV), per family.
