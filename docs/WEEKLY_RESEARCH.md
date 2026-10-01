# The weekly research loop

> RESEARCH ONLY. Nothing here selects, sizes, gates or authorises a wager, changes a model, a threshold or a
> stake, or promotes a research arm. RUN NFL works exactly as before without any of it.

```
pregame evidence ─► thesis ─► market expression ─► wager (position episode)
        ▲                                                  │
        │                                                  ▼
 next week's research ◄─ expression autopsy ◄─ player/team autopsy ◄─ realized game script
```

## What runs, when

`.github/workflows/weekly-research.yml`, Tuesdays 15:43 UTC (after Monday night has settled and been autopsied)
and on demand. A stdlib gate (`scripts/research/weekly_research_gate.py`) finds the newest COMPLETE week (every
game FINAL, the last kickoff ≥ 30 h old) and does nothing if its reports are already on `market-data`. Otherwise:

1. `scripts/research/board_research.py` rebuilds the full-board table for every completed week, streaming the
   capture out of git objects (`docs/BOARD_RESEARCH.md`);
2. `scripts/research/weekly_research.py` writes, for the newest week and cumulatively,

| report | answers |
|---|---|
| `BOARD_EDGE_DISCOVERY.md` | What did the board teach? Coverage with every exclusion reason; families; price bands by ask AND by quoted mid; conditional patterns with clustering, multiplicity and week stability; ladders; preregistered tests (discovery vs prospective); rejected patterns; patterns worth testing |
| `SCRIPT_AUTOPSY.md` | What kind of game happened? Game-centre errors; realized script labels; team-volume errors; player misses by the layer that left expectation first; which misses better scripting could plausibly have prevented; recurring failure modes; autopsy coverage |
| `THESIS_IMPROVEMENT.md` | What to pay attention to before games; what should NOT change; hypotheses under test and their RUN NFL tags; the expression autopsy of the actual positions; limitations |

to `data/research/weekly/<season>/week_NN/` and `.../cumulative_wkLO-HI/` (plus `research.json.gz`), and the board
table to `data/research/board/<season>/`, all on `market-data`. Derived and rebuildable; rendering is a pure
function of the evidence (no clock in the markdown), so a rebuild of the same evidence is byte-identical.

The canonical Weeks 1–3 versions are committed on `main` under `research/weekly/2026/` for review.

## The hierarchy, and where each expectation comes from

GAME ENVIRONMENT → TEAM VOLUME → PLAYER OPPORTUNITY → EFFICIENCY → MARKET EXPRESSION.

| level | expectation (never rebuilt with hindsight) | realized |
|---|---|---|
| game environment | the board's latest-pregame ladder medians: home margin, total, team points | final score, quarter-end margins, lead changes |
| team volume | the simulation's script summary (Week 4+); else the QB pass-attempts ladder median; else the team's prior-game mean (point-in-time) — the source is printed on every row | play-by-play plays, dropbacks, pass attempts, sacks, scrambles, designed rushes, QB designed runs |
| player opportunity | the incumbent's frozen projected opportunity (player anatomy) | targets / carries / attempts from the box score |
| efficiency | the incumbent's frozen mu / muo | stat / opportunity |

**Realized script labels** (`nfl_edge/research/script_autopsy.py`, deterministic, thresholds named in the module):
COMPETITIVE_THROUGHOUT, FAVORITE_CONTROL, UNDERDOG_CONTROL, UPSET, EARLY_BLOWOUT, BLOWOUT, LATE_COMEBACK,
SHOOTOUT, LOW_SCORING, LOW_POSSESSION, HIGH_VOLUME_PASSING, RUN_HEAVY_CONTROL. They read the score progression and
the PREGAME market favourite / total only; the function has no parameter that could carry a wager (pinned by test).

## Connecting the script to the player autopsy

Every canonical player autopsy (`player_autopsy.canonical_autopsies`, rule autopsy-1.1.0) gets a **miss layer** —
the first level of the hierarchy that left expectation:

| layer | meaning |
|---|---|
| GAME_SCRIPT_DROVE_TEAM_VOLUME | team volume missed ≥ 25% in the miss's direction AND the realized script explains it by the volume model's own mechanism (trailing → more passing, leading → more rushing, low-possession game → less of everything) |
| TEAM_VOLUME_NOT_EXPLAINED_BY_SCRIPT | team volume missed in the miss's direction, the script does not explain it |
| PLAYER_SHARE_WITH_TEAM_VOLUME_ON_EXPECTATION | the team got its volume; the player's share was wrong |
| ROLE_UNCERTAINTY | as above, for a player with P(plays) < 0.75 or < 4 prior games |
| EFFICIENCY_WITH_OPPORTUNITY_ON_EXPECTATION | opportunity on expectation, efficiency off |
| AVAILABILITY / VARIANCE_ONLY / NO_LARGE_MISS / INSUFFICIENT_DATA | as the autopsy classified |

Weeks 1–3 (2,980 units, 1,810 meaningful misses): player share 41%, efficiency 29%, team volume not explained by
script 11%, role uncertainty 6%, **script-driven team volume 6%**. The owner's "most error is upstream of
efficiency" holds; the refinement is that upstream mostly means WHO got the ball, not how many plays the game
had. **Sensitivity:** anytime-touchdown props are 549 of the 1,810 and read almost entirely as share; without them
efficiency is the largest single layer (42%), share 34%, team volume 17% (7% script-driven), role 3% — upstream is
still a narrow majority, not two-thirds.

## The expression autopsy (`nfl_edge/research/expression_autopsy.py`)

Positions, not orders: the owner's imported orders are folded into position episodes
(`handicap/position_lifecycle.py`) — a cashout is the same position closing. Each episode is placed in an
INFERRED thesis bucket (game × beneficiary × polarity), so PHI spread + Hurts attempts + three Hurts passing
rungs are one thesis. The script is judged from the HEADLINE rung of each thesis ladder at latest pregame (did
the team beat the market's median margin / points, did the player beat the market's median line), never from the
wager's result. Classifications: SCRIPT_RIGHT/EXPRESSION_RIGHT, SCRIPT_RIGHT/EXPRESSION_WRONG,
SCRIPT_PARTIAL/EXPRESSION_RIGHT or _WRONG, SCRIPT_WRONG (+ WON_DESPITE_WRONG_SCRIPT), SCRIPT_UNJUDGEABLE; flags
PRICE_ERROR (paid ≥ 5c worse than the close on the held side), ROLE_ERROR / VOLUME_ERROR / EFFICIENCY_ERROR /
VARIANCE_ONLY (lost player positions, from the miss layer), CORRELATED_STACK (≥ 3 positions on one bucket).

Week 3 reproduces the owner's own reading without being told it: LAR–DEN script right, Stafford passing and the
Rams team total EXPRESSION_RIGHT, the Rams moneyline EXPRESSION_WRONG; LV–NO script partial, Saints team total
right and Saints spread wrong; KC–MIA spread right, the 1H team total and Johnson rushing wrong; PHI–CHI one
SCRIPT_WRONG bucket of four correlated positions.

## Thesis metadata (`nfl_edge/research/thesis.py`) — optional, no new chore

`primary_thesis_id`, `correlation_bucket`, `script_dependency`, `market_expression_reason`, `failure_mode`,
`hard_bet_up_to`, `role_uncertainty_note`. Filled automatically from recommendation records
(`primary_thesis`, `correlation_group`, `bet_up_to_probability`, and `reasoning_tags` written as
`script:<X>`, `expression:<X>`, `failure:<X>`, `role:<text>`); optionally from
`data/handicap/theses/<season>/week_NN.json` on handicap-data ({ticker or episode id: fields}). Nothing is
required: a missing field is normal, a malformed one warns and never blocks ingestion, and the schema of every
existing record is unchanged. **Limitation:** imported wagers (the owner's real orders) still carry no thesis by
themselves; until one is recorded, buckets are INFERRED and say so.

## Limitations

* Weeks 1–3 are 48 games; every pattern is hypothesis-generating until its preregistered window.
* Weeks 1–3 have no frozen team-volume projection; Week 4 is the first week the simulation's script summary
  (`nfl_edge/sim/script.py`) is the expectation.
* The simulator draws final margin and total, not score paths; script labels describe the final progression and
  the packet reports pass rate conditional on the final margin as the nearest proxy.
* Red-zone trips, routes and snaps are not simulated.
