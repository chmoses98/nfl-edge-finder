# Production eligibility

`nfl_edge/evaluation/eligibility.py` (policy + engine), `scripts/shadow_v2/eligibility_v2.py` (builder),
`data/shadow/v2/eligibility/<stamp>.eligibility.json` + `latest.json` on `market-data` (the document consumers read).

The layer exists so a research arm cannot be treated like a validated input. Every model arm and every
(arm, market family) gets exactly one status, decided by written rules over prospective evidence, and every
consumer -- RUN NFL's packet, the Shadow v2 block, the handicap report -- prints that status beside the number.

## States

| status | meaning | how a consumer uses it |
|---|---|---|
| `TRUSTED` | long prospective record, statistically better than the market, positive CLV, non-negative net P&L | may be relied on as primary evidence (never an automatic bet) |
| `LIMITED` | several weeks of synchronized evidence, not worse than the market within tolerance, calibrated, CLV >= 0 | may inform a handicap beside the market |
| `WATCH` | measurable, not measurably worse than the market | supporting evidence only |
| `RESEARCH_ONLY` | too little evidence, or evidence that it is worse than the market | displayed with its label, never an input |
| `DISABLED` | a known defect makes its output wrong by construction | no number is shown |

A family can never be more trusted than its arm. An arm the document has never measured is `RESEARCH_ONLY`. With
no document at all, nothing is more than `RESEARCH_ONLY` and every known-defect arm is `DISABLED`.

## The unit of evidence is the game

A week of player props is hundreds of thousands of rows (every rung x every snapshot) but only ~16 independent
outcomes' worth of football. Every statistic is computed per game first (the mean of the row-level Brier difference
over that game's rows) and then across games, with the standard error across games. Row counts are reported and
never qualify anything. Only `PROSPECTIVE_FROZEN` rows with a settled outcome and a horizon mid count; synchronization
and close quality are gates on promotion.

## Promotion rules (written before any arm was evaluated against them; not tuned to approve anything)

| to | requires |
|---|---|
| `WATCH` | >= 16 independent games, and the game-level Brier delta vs the market is not measurably worse (z <= 2) |
| `LIMITED` | >= 48 games over >= 3 weeks; 95% upper bound of (model - market) Brier <= +0.002; ECE <= 0.03; mean CLV >= 0; >= 90% of rows synchronized and >= 90% with an EXCELLENT/GOOD close |
| `TRUSTED` | >= 128 games over >= 8 weeks; 95% upper bound < 0 (better than the market); CLV lower bound > 0; game-level net P&L after fees >= 0 |
| demotion | any status falls to `RESEARCH_ONLY` the moment the game-level delta is measurably worse (z > 2) |

Known defects (`KNOWN_DEFECTS`) are `DISABLED` regardless of numbers; research-by-design arms (`RESEARCH_BY_DESIGN`)
cannot pass `RESEARCH_ONLY` before the `LIMITED` sample exists.

## Status at the first build (2026 week 2 evidence, 16 games)

| arm | status | why |
|---|---|---|
| BOARD_V2 | WATCH | -0.0005 +/- 0.0008 vs market, CLV +0.011; one week cannot reach LIMITED |
| BOARD_V2 / period winner 1H, 3Q | RESEARCH_ONLY | measurably worse than the market (z > 2) |
| MARKET_PLAYER_DIST | WATCH | -0.0005 +/- 0.0003; it is the market's ladder, smoothed |
| DATA_PLAYER_V3, HYBRID_PLAYER_V3 | RESEARCH_ONLY | new version, no prospective record; historically worse than the market (research/player_engine_v3) |
| DATA_PLAYER_DIST, HYBRID_PLAYER_DIST | DISABLED | input defect (blanked lines read as a zero-point team; no current season) |
| DATA_PLAYER_V4, HYBRID_PLAYER_V4 (added 2026-09-24) | RESEARCH_ONLY | new version; historically +0.0043 vs the market at T-90m (half of v3's gap, still worse; research/player_engine_v4). Historical results qualify it for prospective collection only |
| DATA_PLAYER_V5, HYBRID_PLAYER_V5 (added 2026-09-24) | RESEARCH_ONLY | new version (V4 + point-in-time, availability-aware starting QB; docs/PLAYER_V5.md). RESEARCH_BY_DESIGN: research until >= 48 prospective games over >= 3 weeks, then the ordinary rules per family; historical results qualify it for prospective collection only |

## Player-projection abstention

Independently of the arm's status, every player projection carries `abstention.state`
(`nfl_edge/engines/player/abstention.py`): `ABSTAIN_IDENTITY`, `ABSTAIN_INJURY_UNCERTAIN`, `ABSTAIN_ROLE_UNCERTAIN`,
`ABSTAIN_VOLUME_UNCERTAIN`, `ABSTAIN_MARKET_INCOMPLETE`, `ABSTAIN_MODEL_UNVALIDATED`, `PROJECTION_LOW_CONFIDENCE`
(|model - market| > 5pp, where the models are historically worst) or `PROJECTION_VALID`. The V4 arms use
`decide_v4`, which adds `ABSTAIN_SNAP_UNCERTAIN`, `ABSTAIN_TEAMMATE_SHOCK` and `ABSTAIN_EXTRAPOLATION` from the
model's own intermediates (docs/PLAYER_V4.md). The V5 arms use `decide_v5` = `decide_v4` plus
`ABSTAIN_QB_UNCERTAIN` where the point-in-time QB resolution abstained (chart QB1 Doubtful, QB1 out with nobody
eligible behind him, no chart QB1) and the statistic runs through the passing environment (docs/PLAYER_V5.md). The probability stays on the
record so the rule itself is scored prospectively; authority does not.
