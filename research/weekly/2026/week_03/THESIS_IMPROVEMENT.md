# THESIS IMPROVEMENT — 2026 week 3

> RESEARCH ONLY. Nothing in this report selects, sizes, gates or authorises a wager, changes a model, a threshold or a stake, or promotes any research arm. Patterns here are hypothesis-generating unless the hypothesis registry says otherwise.

## 1. Pay attention to, before the games

- WHO gets the ball matters more than how many plays there are: 46% of meaningful player misses were a player's share or an uncertain role with team volume on expectation; 5% were team volume a different game script explains. Anytime-TD props drive much of the share figure: without them, share + role is 38% and efficiency 40%. Check depth-chart, snap and target-share changes before props.
- Efficiency explains 29% of meaningful misses with opportunity on expectation: a yardage thesis that needs efficiency above the player's norm is the most fragile kind.
- Cost, not mispricing, is the default: buying at the ask lost in 3 of 20 side × price bands of the whole board after fees. A position needs a reason the mid is wrong, not just a view.
- Modest DATA_ONLY disagreement predicts movement toward it (H-20261001-B04) was the strongest information lead in discovery (+0.082, CI [+0.021, +0.145]); it is under prospective test, not proven.
- A large incumbent player-model OVER view marks an underpriced YES (H-20261001-B11) was the strongest information lead in discovery (+0.078, CI [+0.022, +0.135]); it is under prospective test, not proven.
- Treat a stack of positions on one thesis bucket (spread + QB attempts + several passing rungs) as ONE bet in sizing.

## 2. What should NOT change

- The market prior. The CURRENT (market-centred) arm beats DATA_ONLY on margin and total MAE over Weeks 1–3; DATA_ONLY is a research signal and its disagreement only a context feature (three-arm experiment, no verdict before 64 games).
- Production model weights, staking limits, bankroll policy and betting authority: nothing in Weeks 1–3 supports a change, and every pattern here is discovery-only.
- The incumbent's price buckets as rules: the 10–20c full-game YES lead is not distinguishable from noise once clustered by game, and Week 3 showed none of it. It is preregistered (B01), not adopted.

## 3. Hypotheses under test (preregistered; context only)

- **H-20261001-B01** Full-game longshot YES underpriced at the mid — PREREGISTERED; tag `PRICE_BUCKET_RESEARCH_CANDIDATE`; prospective: no future week yet
- **H-20261001-B02** Full-game YES at 60-70c overpriced at the mid — PREREGISTERED; tag `PRICE_BUCKET_RESEARCH_CANDIDATE`; prospective: no future week yet
- **H-20261001-B03** Sides priced 90c+ lose after fees — PREREGISTERED; tag `PRICE_BUCKET_RESEARCH_CANDIDATE`; prospective: no future week yet
- **H-20261001-B04** Modest DATA_ONLY disagreement predicts movement toward it — PREREGISTERED; tag `DISAGREEMENT_RESEARCH_CANDIDATE`; prospective: no future week yet
- **H-20261001-B05** Adjacent yardage rungs beat the main rung after fees — PREREGISTERED; tag `LADDER_RESEARCH_CANDIDATE`; prospective: no future week yet
- **H-20261001-B06** Team total beats spread as the expression of an offensive thesis — PREREGISTERED; tag `EXPRESSION_RESEARCH_CANDIDATE`; prospective: no future week yet
- **H-20261001-B07** Uncertain roles are priced worse than certain roles — PREREGISTERED; tag `ROLE_RESEARCH_CANDIDATE`; prospective: no future week yet
- **H-20261001-B08** Player-prop NO at 80c+ loses after fees — PREREGISTERED; tag `PRICE_BUCKET_RESEARCH_CANDIDATE`; prospective: no future week yet
- **H-20261001-B09** Player-prop YES longshots lose after fees — PREREGISTERED; tag `PRICE_BUCKET_RESEARCH_CANDIDATE`; prospective: no future week yet
- **H-20261001-B10** Chasing a pregame move loses — PREREGISTERED; tag `MOVEMENT_RESEARCH_CANDIDATE`; prospective: no future week yet
- **H-20261001-B11** A large incumbent player-model OVER view marks an underpriced YES — PREREGISTERED; tag `DISAGREEMENT_RESEARCH_CANDIDATE`; prospective: no future week yet

## 4. Research tags for the coming week

RUN NFL marks markets that fall under a hypothesis above with its tag (PRICE_BUCKET_RESEARCH_CANDIDATE, DISAGREEMENT_RESEARCH_CANDIDATE, MOVEMENT_RESEARCH_CANDIDATE …). A tag means "this is the kind of contract a test is watching". It is not evidence and changes no state, edge, threshold or stake.

## 5. Expression autopsy of the actual positions

36 position episodes (orders folded into positions; a cashout is the same position closing) expressing **16 inferred theses**.

| classification | positions | P&L |
|---|---|---|
| SCRIPT_RIGHT/EXPRESSION_RIGHT | 16 | 710.13 |
| SCRIPT_WRONG | 7 | -383.46 |
| SCRIPT_PARTIAL/EXPRESSION_WRONG | 6 | -316.49 |
| SCRIPT_PARTIAL/EXPRESSION_RIGHT | 4 | 265.45 |
| SCRIPT_RIGHT/EXPRESSION_WRONG | 2 | -90.50 |
| SCRIPT_UNJUDGEABLE | 1 | -50.00 |

Flags: CORRELATED_STACK 20, VARIANCE_ONLY 4, PRICE_ERROR 2, EFFICIENCY_ERROR 1, VOLUME_ERROR 1, ROLE_ERROR 1.

| thesis bucket | positions | script | stake | P&L | types |
|---|---|---|---|---|---|
| `2026_03_NYJ_DET|NYJ|+` | 6 ⚠ stack | SCRIPT_RIGHT | 91.98 | 72.34 | PLAYER:receiving_yards |
| `2026_03_LA_DEN|LA|+` | 4 ⚠ stack | SCRIPT_RIGHT | 280.73 | 249.13 | MARGIN, OFFENSE, PLAYER:passing_yards |
| `2026_03_PHI_CHI|PHI|+` | 4 ⚠ stack | SCRIPT_WRONG | 255.98 | -255.98 | MARGIN, PLAYER:attempts, PLAYER:passing_yards |
| `2026_03_BAL_DAL|BAL|+` | 3 ⚠ stack | SCRIPT_PARTIAL | 145.99 | -97.69 | MARGIN, PLAYER:rushing_yards |
| `2026_03_KC_MIA|KC|+` | 3 ⚠ stack | SCRIPT_PARTIAL | 253.50 | 65.25 | MARGIN, OFFENSE:1H, PLAYER:rushing_yards |
| `2026_03_ATL_GB|ATL|-` | 2 | SCRIPT_WRONG | 69.99 | -69.99 | OFFENSE:1H, PLAYER:receiving_yards |
| `2026_03_ATL_GB|GB|+` | 2 | SCRIPT_RIGHT | 45.00 | -16.25 | MARGIN, PLAYER:passing_yards |
| `2026_03_LAC_BUF|BUF|+` | 2 | SCRIPT_RIGHT | 168.99 | 177.70 | MARGIN |
| `2026_03_LV_NO|NO|+` | 2 | SCRIPT_PARTIAL | 126.00 | -29.65 | MARGIN, OFFENSE |
| `2026_03_NYJ_DET|DET|+` | 2 | SCRIPT_PARTIAL | 115.00 | 11.04 | OFFENSE, PLAYER:receptions |
| `2026_03_ATL_GB|GB|-` | 1 | SCRIPT_RIGHT | 24.99 | 36.52 | PLAYER:rushing_yards |
| `2026_03_BAL_DAL|DAL|+` | 1 | SCRIPT_RIGHT | 23.00 | 18.26 | OFFENSE:1H |
| `2026_03_PHI_CHI|CHI|+` | 1 | SCRIPT_RIGHT | 42.98 | 39.87 | PLAYER:receiving_yards |
| `2026_03_SEA_WAS|SEA|+` | 1 | SCRIPT_WRONG | 57.50 | -57.50 | MARGIN |
| `2026_03_TEN_NYG|TEN|+` | 1 | SCRIPT_RIGHT | 40.00 | 42.06 | PLAYER:receptions |

_thesis buckets are INFERRED from what each contract pays on unless the handicap record supplied one; script is judged from the headline rung of each thesis ladder, never from the wager's result._

## 6. Limitations

- Weeks 1–3 are 48 games: every board pattern is hypothesis-generating; nothing is confirmatory before the preregistered window.
- The market mid is the benchmark; the board table settles from football only the families the production engines settle (the exchange-only tier is outside the canonical analysis).
- Weeks 1–3 have no frozen team-volume projection; their script autopsy compares against a QB pass-attempts ladder median or the team's prior-game mean. From Week 4 the simulation's script summary is the expectation.
- Script labels describe the final score progression; the simulator does not draw score-state paths (it reports pass rate conditional on the final margin as the nearest proxy).
- Thesis buckets of actual positions are INFERRED from what each contract pays on unless a thesis was recorded.
- The role-certainty proxy is P(plays) and the prior-game count from the incumbent's anatomy, not a role model.

