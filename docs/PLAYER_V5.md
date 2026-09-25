# DATA_PLAYER_V5 / HYBRID_PLAYER_V5

A research challenger that is DATA_PLAYER_V4 with ONE changed input layer: the projected starting quarterback is
resolved **point in time and availability-aware** instead of read off the depth chart. V4 (`data-player-dist-4.0.0`,
`player-inputs-4.0.0`) and V3 are frozen: their code paths, versions, fitted state and records are unchanged (proof
below). Status: **RESEARCH_ONLY** (both arms), by design. Nothing here claims or implies promotion.

| arm | engine version | what it is |
|---|---|---|
| DATA_PLAYER_V5 | `data-player-dist-5.0.0` (inputs `player-inputs-5.0.0`) | V4's snap -> volume -> allocation -> outcome chain, with the resolved QB propagated through it |
| HYBRID_PLAYER_V5 | `hybrid-player-dist-5.0.0` | 0.85-market pmf mixture with DATA_PLAYER_V5 (V4's weight, inherited -- not re-selected) |

Evidence: `research/player_engine_v5/results.json` (`scripts/research/player_engine_v5_study.py`).

## Why

`DepthChartBook.qb1()` answers "who is first on the newest chart at or before the cutoff", whatever his status. ESPN
charts are slow to demote an injured starter: in 2026 Week 2 three of the four QB1 mismatches against the actual
starter were a charted QB1 designated Out at the cutoff (Penix ATL, Murray MIN, Darnold SEA; known limitation #89).
V3 and V4 priced the backup as a non-starter (no passing distributions at all) and the Out starter as the starter,
and every pass-catcher inherited the wrong passing environment. The frozen arms cannot change their inputs in the
middle of their prospective collection, so the fix is a new, versioned arm.

## The resolver (`nfl_edge/context/qb_resolution.py`, `qb-resolution-1.0.0`)

A pure function of (chart QBs in order, availability evidence, cutoff, kickoff). Every piece of evidence it used and
every piece it refused is on its output.

| QB1 state at the cutoff | decision | reason | certainty |
|---|---|---|---|
| no designation / Probable / active | keep QB1 | `CHART_QB1_AVAILABLE` | HIGH |
| Out / IR (RES, PUP, SUS, NON) / inactive | next charted QB who is not himself Out / inactive | `QB1_OUT_PROMOTED_NEXT` | MEDIUM; HIGH when an official inactive list observed pregame and at or before the cutoff names QB1; LOW when the promoted QB is himself Questionable / Doubtful / unknown |
| Out, nobody eligible behind him | no starter; QB-dependent projections abstain | `QB1_OUT_NO_ELIGIBLE_BACKUP` | UNKNOWN |
| Doubtful | keep QB1 as the structural input; **abstain** on every QB-dependent projection of the team | `QB1_DOUBTFUL_ABSTAIN` | LOW |
| Questionable | keep QB1, flagged | `QB1_QUESTIONABLE_RETAINED` | LOW |
| no report / capture at the cutoff | keep QB1, flagged (not listed is NOT healthy) | `QB1_STATUS_UNKNOWN_RETAINED` | LOW |
| no chart QB1 / a chart newer than the cutoff handed in | no starter; abstain | `NO_CHART_QB1` / `CHART_AFTER_CUTOFF_REFUSED` | UNKNOWN |

Why Doubtful abstains rather than promotes: a Doubtful designation is a probability, not an outcome, and the model has
one QB slot per team. Promoting would assert a certainty the report does not give; keeping QB1 silently would repeat
#89 in a milder form. So the structure keeps the chart QB1 (the least-surprising input) and the record says the team's
passing environment is not known well enough to be scored as an opinion. Questionable QBs play in the large majority
of cases, so they are retained and flagged, not abstained. QB-dependent = every QB statistic, a pass-catcher's
receptions / receiving yards / rush+rec yards, a WR / TE anytime TD (`is_qb_dependent`).

Point in time, by construction: evidence observed after the cutoff, at or after kickoff, tagged
POSTGAME_OBSERVATION, or an official inactive list with no capture time is refused; a chart vintage after the cutoff is
refused; the function has no argument through which a realised starter or the schedule's QB ids could enter. In
production the evidence is exactly what V4 already reads at the cutoff: the injury-report VINTAGE the context layer
resolved (`ctx.injuries`, the game's week only), the run's availability captures (AvailabilityBook, the same combined
state V4's overrides read), and the official inactives the run loaded (`ctx.inactives`, already filtered to
observations at or before the cutoff and before kickoff), matched by the charted player's name.

## Propagation (structural, not a perturbation)

V4's model is reused by parameter, never copied: `v4.model.fit_bundle(config={"qb_identity": True},
version="data-player-dist-5.0.0")`. The resolved starter is the ONE changed input and reaches:

* `qb_starter` on the rows -- which QB gets the passing population (attempts, completions, yards, TDs, INTs) and QB
  rushing, and the QB snap model's starter feature (`qb_starter_f`);
* four team-game QB-identity features (`nfl_edge/engines/player/v5/qb_features.py`, strictly prior games): new starter
  vs the previous game's starter, the starter's shrunk yards-per-attempt and completion-rate DELTA vs the previous
  starter (replacement-level prior, 150 pseudo-attempts, half-life 12 games), and his log career attempts;
* appended to exactly four V4 stages (`model.QB_IDENTITY`): team pass / rush volume (hence every pass-catcher's
  targets), the pass-catchers' catch rate, their yards per catch, and the starter's own attempts.

In training the projected starter is the realised one (the analogue of a correctly resolved pregame QB); for a
projected game it is only the resolver's answer. V4's config has no `qb_identity` key, so every V4 stage fits exactly
the features it did.

What the 2014-2024 fit learned (2025 bundle `4bd385b416879f53`): pass attempts +1.24 per +1.0 ypa of starter delta
(a new starter by itself -0.06), WR yards per catch +0.35 and WR catch rate +0.14 per unit of completion-rate delta.
**The learned QB-identity effects are small**: a one-yard-per-attempt worse backup costs about 1.2 team pass
attempts and a third of a yard per WR catch. The big structural change is the passing population (who gets QB
distributions), not the pass-catcher environment.

## Held-out replay (`scripts/research/player_engine_v5_study.py`)

Same protocol as V4 (docs/PLAYER_V4.md, research/player_engine_v4): fits on seasons strictly before the target
(2025 window: 2014-2024; 2026 window: 2014-2025 + 2026 week 1 as completed history), paired Brier against the monotone
market midpoint (quote width <= 10c), standard errors **clustered by game**. Environment: 2025 = that horizon's
Kalshi-implied spread/total; 2026 = the game centre frozen on the Shadow v2 records at that horizon. Arms on the
same rows: V3 and V4 with the chart QB1 at the cutoff (what production runs), V5, and V4_ORACLE (V4 with the REALISED
starter -- the setup of the V4 study, which no pregame model can have; a ceiling, not a model).

QB evidence in the replay: the chart is the newest ESPN scrape at or before each horizon's cutoff; availability is the
week's nflverse injury report and weekly-roster status. Those two files carry no per-row timestamp, so they are
treated as known at every horizon -- the same assumption V4's teammate statuses make; no official inactive list
exists for these seasons, so no promotion is HIGH certainty. The realised starter is used ONLY to score the resolver.

Scope, honestly: the six rung families of the V4 study (passing yards / TDs, rushing yards, receiving yards,
receptions, anytime TD); 2025 weeks 1-18 (510 of 544 team-games have a kickoff anchor in the backfill and are
resolved); 2026 **week 2 only** -- week 1 has no published research export, and week 2's T-90m horizon covers 6 games.
Rows exist only for players who played (the V4 study's population), so an Out QB1's own rungs are never scored.

### The resolution (T-90m; the other horizons are within one team-game)

| window | team-games | chart QB1 = actual starter | V5 QB = actual starter | promotions (correct) | Doubtful abstentions | Questionable retained |
|---|---|---|---|---|---|---|
| 2025 | 510 | 464 (91.0%) | **494 (96.9%)** | 30 (30) | 2 team-games | 13 |
| 2026 wk 2 | 32 | 29 | **31** | 3 (2) | 0 | 1 |

The 2026 miss is ATL: Penix Out, chart QB2 Tagovailoa **Doubtful**, the resolver promoted him with LOW certainty and
Cooper Rush started. The rule as written promotes the next QB who is not definitively out; skipping (or abstaining
on) a Doubtful backup is the obvious refinement, but it was seen on the evaluation data and is NOT applied here --
it is a candidate for a later version, to be tested on data it was not chosen on. The 16 remaining 2025 chart misses
are benchings and surprise starts no availability evidence announces.

### Headline (common rows: every arm priced the rung)

| window / horizon | rows / games / player-games | V3 - mkt | V4 - mkt | **V5 - mkt** | V4_ORACLE - mkt | V5 - V4 |
|---|---|---|---|---|---|---|
| 2025 T-24h | 14,110 / 234 / 2,665 | +0.0085 +/- 0.0016 | +0.0047 +/- 0.0014 | +0.0046 +/- 0.0014 | +0.0046 | -0.0001 +/- 0.0001 |
| 2025 T-6h | 15,279 / 247 / 2,967 | +0.0087 +/- 0.0015 | +0.0042 +/- 0.0013 | +0.0042 +/- 0.0013 | +0.0042 | +0.0000 +/- 0.0001 |
| 2025 T-90m | 16,843 / 247 / 3,286 | +0.0085 +/- 0.0014 | +0.0044 +/- 0.0012 | **+0.0044 +/- 0.0012** | +0.0044 | +0.0000 +/- 0.0001 |
| 2025 T-0 | 18,171 / 247 / 3,291 | +0.0083 +/- 0.0014 | +0.0045 +/- 0.0013 | +0.0045 +/- 0.0013 | +0.0044 | +0.0000 +/- 0.0001 |
| 2026 wk2 T-24h | 3,827 / 16 / 265 | +0.0049 +/- 0.0025 | +0.0029 +/- 0.0026 | +0.0030 +/- 0.0026 | +0.0029 | +0.0001 +/- 0.0002 |
| 2026 wk2 T-6h | 3,998 / 16 / 272 | +0.0052 +/- 0.0025 | +0.0037 +/- 0.0026 | +0.0039 +/- 0.0026 | +0.0037 | +0.0002 +/- 0.0002 |
| 2026 wk2 T-90m | 1,446 / 6 / 104 | +0.0062 +/- 0.0044 | +0.0057 +/- 0.0041 | +0.0061 +/- 0.0040 | +0.0057 | +0.0004 +/- 0.0005 |

2025 T-90m Brier V3 0.1976 / V4 0.1935 / **V5 0.1935** / market 0.1891; log loss 0.5779 / 0.5684 / **0.5684** / 0.5571.
Calibration (ECE, T-90m common rows): 2025 V3 0.019, V4 0.009, V5 0.010, market 0.019; 2026 wk2 V3 0.027, V4 0.030,
V5 0.031, market 0.017 (6 games).

**On the rows every arm prices, V5 is indistinguishable from V4 (|V5 - V4| <= 0.0004, never significant) and, like
V4 and V3, clearly worse than the market at every horizon.** V4 with the realised starter is no better either: on
the common rows, knowing the quarterback is worth ~0.0000 Brier, because on those rows the chart QB1 was almost always
right and the QB-identity effects the structure learns are small.

### Coverage: what V5 prices that V4 cannot (2025 T-90m)

| | V3 | V4 | V5 | V4_ORACLE |
|---|---|---|---|---|
| priced rungs | 16,885 | 18,123 | **18,294** | 18,262 |
| player-games | 3,290 | 3,402 | **3,423** | 3,424 |
| games | 247 | 247 | 247 | 247 |

171 rungs are priced by V5 and not V4 (2026 wk2 T-90m: 20): the promoted backups' passing props, which V4 refuses
because it marks the Out starter as `qb_starter`.

### By statistic (2025 T-90m; common V3/V4/V5 rows, V5 on all its rows in the last column)

| statistic | rows / games | V3 - mkt | V4 - mkt | V5 - mkt | V5 - V4 | V5 all rows |
|---|---|---|---|---|---|---|
| passing TDs | 587 / 88 | -0.0012 +/- 0.0020 | -0.0018 +/- 0.0020 | -0.0018 +/- 0.0020 | -0.0000 | -0.0015 (599) |
| passing yards | 2,129 / 174 | +0.0070 +/- 0.0026 | +0.0043 +/- 0.0019 | +0.0043 +/- 0.0019 | +0.0001 | +0.0040 (2,233) |
| receiving yards | 5,633 / 174 | +0.0091 +/- 0.0021 | +0.0059 +/- 0.0020 | +0.0058 +/- 0.0020 | -0.0000 | +0.0058 (5,633) |
| receptions | 3,631 / 124 | +0.0141 +/- 0.0030 | +0.0051 +/- 0.0023 | +0.0051 +/- 0.0023 | +0.0000 | +0.0051 (3,631) |
| rushing yards | 1,989 / 162 | +0.0076 +/- 0.0041 | +0.0047 +/- 0.0039 | +0.0047 +/- 0.0039 | +0.0001 | +0.0022 (2,846) |
| anytime TD | 2,916 / 246 | +0.0038 +/- 0.0012 | +0.0019 +/- 0.0010 | +0.0019 +/- 0.0010 | +0.0000 | +0.0017 (3,352) |

2026 wk2 T-90m (6 games) by statistic is in results.json; every V5 - V4 difference there is within +/- 0.0011 and
none is significant.

### The rows the resolution changed (teams whose chart QB1 was replaced)

| window / horizon | games | V5 rows (V4 rows) | V5 - mkt | V4 - mkt | V3 - mkt | V4_ORACLE - mkt | V5 - V4 (common) |
|---|---|---|---|---|---|---|---|
| 2025 T-24h | 28 | 818 (682) | +0.0097 +/- 0.0047 | +0.0118 +/- 0.0056 | +0.0123 +/- 0.0044 | +0.0098 | -0.0002 +/- 0.0005 |
| 2025 T-6h | 30 | 864 (717) | +0.0075 +/- 0.0048 | +0.0096 +/- 0.0057 | +0.0115 +/- 0.0047 | +0.0078 | -0.0002 +/- 0.0005 |
| 2025 T-90m | 30 | 961 (790) | +0.0047 +/- 0.0056 | +0.0066 +/- 0.0064 | +0.0065 +/- 0.0057 | +0.0047 | -0.0001 +/- 0.0005 |
| 2025 T-0 | 30 | 1,002 (829) | +0.0084 +/- 0.0058 | +0.0102 +/- 0.0063 | +0.0110 +/- 0.0058 | +0.0085 | -0.0002 +/- 0.0005 |
| 2026 wk2 T-24h | 3 | 354 (314) | -0.0083 +/- 0.0064 | -0.0124 +/- 0.0024 | -0.0029 +/- 0.0072 | -0.0106 | +0.0023 +/- 0.0020 |
| 2026 wk2 T-6h | 3 | 363 (323) | -0.0072 +/- 0.0075 | -0.0113 +/- 0.0033 | -0.0023 +/- 0.0065 | -0.0096 | +0.0025 +/- 0.0020 |
| 2026 wk2 T-90m | 1 | 126 (106) | +0.0046 | -0.0069 | -0.0142 | -0.0005 | +0.0056 (1 game) |

V5 matches the realised-starter oracle on these teams (2025 T-90m +0.0047 vs +0.0047) and prices ~20% more of their
rungs. On the rows V4 also prices, the difference is nil in 2025 and slightly (not significantly) worse in 2026 week 2
(three games, one of them the ATL wrong promotion). The promoted backups' own passing props (2025 T-90m, 14 games):
passing yards -0.0033 +/- 0.0079 vs the market (104 rungs) -- at parity, on rungs no earlier arm prices.

**Abstentions.** 2025: 2 team-games Doubtful-abstained (98 QB-dependent rungs at T-90m); V5 on those rungs was
+0.0251 worse than the market -- the abstention withheld authority exactly where the projection was bad. 2026 wk2:
none. On every team whose quarterback was NOT re-resolved, V5 - V4 is 0.0000 +/- 0.0001 (2025) -- the refit with
the extra features costs nothing elsewhere.

### Verdict

* The resolver does what #89 asked: in 2025 it names the actual starter in 96.9% of team-games against the chart's
  91.0%, with 30 of 30 promotions correct and none from post-cutoff information; in 2026 week 2 it fixes MIN and SEA
  and misses ATL (a Doubtful backup), which is documented, not tuned away.
* The structural effect on pricing is **small**: V5 = V4 on common rows, V5 = the realised-starter oracle on the
  affected teams, and V5 prices the promoted backups' passing props V4 refuses (at parity on 104 rungs).
* V5 is still clearly worse than the market (2025 T-90m +0.0044 +/- 0.0012). It is RESEARCH_ONLY and qualifies for
  prospective collection only; nothing here is evidence for promotion.

## V3 and V4 are unchanged (proof)

* `tests/test_player_v5.py::test_v4_and_v3_outputs_are_byte_identical_to_main`: on the synthetic league the V4 bundle
  sha and every distribution's pmf, and the V3 bundle and its distributions, equal digests computed with the code at
  main `50a62fb` before V5 existed.
* Real-data replay (scratch, not committed): the 2025 V4 bundle fitted on the real 2013-2026 frame with main's code and
  with this branch's code has the same sha (`26a1c7956d34e510`) and all 31,810 distributions are byte-identical
  (sha256 of every pmf).
* `test_v4_stage_features_are_exactly_v4s_without_the_flag`: V4's stage feature lists are exactly main's.
* The projector appends the V5 arms after every existing arm; the shared player context / sidecar is untouched (V5's
  QB fields ride on V5 records only); V4's lean records use the same defaults.

## Production (a separate commit, to be merged when the owner chooses)

`nfl_edge/engines/player/v5/prospective.py` builds the arms inside `project_slate_v2.build_player_arms` after V4
(`build_player_v5`), FAIL-SOFT exactly like V4: a V5 exception leaves the V5 slots empty and every V5 record a
refusal naming the reason; no other arm, record or the board is touched. V5 fits its own bundle from the same
inputs V4 reads (roughly one more V4-sized build per run). The run summary carries `player_v5` (bundle sha,
distributions, QB resolutions by reason, every substitution, seconds, bytes). Records are LEAN like V4's and keep the
five QB fields (`depth_chart_qb1`, `effective_projected_qb`, `qb_availability_state`, `qb_resolution_reason`,
`qb_resolution_certainty`) in the V5 record's player context (`lean.PLAYER_CONTEXT_KEEP_V5`) and feature lineage.
Abstention: `decide_v5` = `decide_v4` + `ABSTAIN_QB_UNCERTAIN`. Eligibility: RESEARCH_BY_DESIGN (research until >= 48
prospective games over >= 3 weeks, then the ordinary per-family rules). RUN NFL shows V5 under `other_arms` after
V4, labelled research, with the QB resolution where it moved off chart QB1; HYBRID_PLAYER_V5 is `market_derived`.
The autopsy covers DATA_PLAYER_V5 and, because its records name the resolved passer, scores QB_ENVIRONMENT_MISS.
