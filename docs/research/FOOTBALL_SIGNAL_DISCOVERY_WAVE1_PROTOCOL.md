# Football Signal Discovery Lab — Wave 1 (NFL): pre-registered protocol

Status: **PRE-REGISTERED**

This protocol was committed before any closing line, Kalshi ladder or game/player outcome was joined to the Wave 1
feature tables. The runner (`scripts/research/signal_discovery_wave1.py`) refuses to screen or evaluate unless this
file names the canonical SHA-256 of the hypothesis file it is about to use, and the feature/ladder tables still match
their manifests.

| Item | Value |
|---|---|
| Base main | `e6fb9e1d69c81f14c4e1a582f7830a5fce62bbd2` |
| Research version | `nfl-signal-discovery-wave1/1.0.0` |
| **Hypothesis set 1** | `research/signal_discovery_wave1/hypotheses_set1.json` (game hypotheses, thresholds, walk-forward, status rule, prop families, prop model) |
| **Set 1 canonical SHA-256** | **`83861082cc3702875ef0e96b97abcc80cd13b29d7167d384f7068568e285afe1`** |
| Game features | `research/signal_discovery_wave1/game_features.parquet`, frame SHA-256 `5816ff74…7b95b7` (3,300 games 2015–2026) |
| Player features | rebuilt deterministically (`player-features` stage; 62,920 rows, frame SHA-256 `7ea44393…b8bb90`; 31 MB, not committed) |
| Prop ladders | `research/signal_discovery_wave1/prop_ladders.parquet`, frame SHA-256 `e6cf6be1…788f196` (from `market-data` @ `912aac02`) |
| Kind of study | **RETROSPECTIVE DISCOVERY / VALIDATION.** No production methodology, projection, pricer, board, gate, settlement, app export, router or workflow changes. |

## 1. Questions

As in CFB, three questions are kept separate for every candidate:

* **A. Football:** does the candidate predict a football outcome (winner, margin, total, first-half margin, player stat)?
* **B. Market:** does it predict the outcome *relative to the offered line* (closing spread, total or moneyline; Kalshi
  prop ladder median)?
* **C. Economic:** is it profitable at an executable or listed price after vig and fees?

## 2. Honest provenance

Nothing here is a sealed holdout:

| Data | Already seen by |
|---|---|
| nflverse 2006–2025 game level | `research/game_model` (H-001 opponent-adjusted EPA vs the close: REJECTED), `edge_lab` (rest, Thursday, divisional, QB change: priced), `game_script_v2` (2021–25) |
| Player stats 2016–2025 | `player_distributions`, `opportunity`, `role_features`, player engines v2–v5, sim walk-forward 2021–25 |
| Kalshi 2025 archive | heavily mined (`efficiency_map`, `model_vs_market`, `residual_pit`, reconciliation weights) |
| Kalshi 2026 weeks 1–3 | weekly research and board-miner hypothesis generation; weeks 4–5 partly clean |

**Every result is labelled RETROSPECTIVE.** Block B (2020–2025) is only "not used to choose set-2 candidates".

## 3. Features (market-blind, outcome-blind)

### Game layer

The repository's preregistered opponent-adjustment solver (`nfl_edge.sim.opponent_adjust.solve`, `sim-oppadj-1.0.0`)
is used unchanged:

* a weighted ridge of offence + opponent defence + home on the three previous seasons plus earlier weeks;
* 8-week half-life, 0.5 season carry;
* the ridge strength per metric is chosen on seasons Y−2 and Y−1 only;
* it is solved at every (season, week) snapshot on strictly earlier games.

Sixteen metrics are adjusted:

* the solver's own 11;
* early-down EPA;
* explosive pass rate and explosive rush rate;
* points;
* pressure rate (from participation, 2016–2025; **no in-season 2026 file**, so not prospectively reproducible).

Features per game:

* matchup expectations `mx_<side>.<m>`;
* home-perspective nets;
* unit qualities in league SDs;
* pace, tempo and pass-rate environment;
* an opponent-adjusted scoring baseline (expected margin and total, **from football only**);
* a raw (unadjusted) EPA comparator;
* rest, division and roof;
* QB change, derived from the schedule's realised starter ids. This is **NEAR_PIT**: starters are announced pregame,
  but a surprise start is possible.

### Claims and flags (outcome-blind thresholds)

Thresholds come from the distribution of |net EPA/play| over 2015–2026 feature rows:

| Claim or flag | Rule |
|---|---|
| CLOSENESS | \|net\| ≤ 0.025 (≈ P20) |
| MODERATE CONTROL | 0.075 ≤ \|net\| < 0.115 (≈ P60–P80) |
| STRONG CONTROL | \|net\| ≥ 0.115 (≈ P80) |
| Run-leaning | adjusted neutral pass rate ≤ 0.597 (the median) |
| Defensive suppression | both defences ≥ +0.5 SD on EPA allowed |
| Short week | rest ≤ 5 against an opponent's ≥ 6 |
| Off a bye | rest ≥ 13 against ≤ 8 |
| Indoor | dome or closed roof |

### Player layer

The repository's point-in-time sim features (`nfl_edge.sim.features`) are reused unchanged:

* decayed target, carry, attempt, red-zone and snap shares at two half-lives;
* last-game shares;
* exposure-weighted per-touch rates shrunk to **frozen position priors fitted on 2012–2015 only**;
* team volume EWMAs.

These are joined to the team-perspective game context: expected plays, expected script (the football baseline
margin), opponent pass, rush and explosive defence, pass rush against protection, and QB efficiency.

**ROLE_STABILITY** classes (pregame only):

| Class | Rule |
|---|---|
| INSUFFICIENT_ROLE_HISTORY | fewer than 3 prior games |
| INJURY_DEPENDENT | own Q/D designation, or a higher-share same-position teammate listed Out/Doubtful. The final weekly report is NEAR_PIT. |
| ROLE_CHANGE | short-window vs long-window primary share ≥ 0.10, or snap share ≥ 0.15 |
| STABLE_ROLE | otherwise |

Player rows exist only for players who appeared (**conditional on playing**).

## 4. Markets

* **Game lines.** nflverse schedule consensus closing spread, total and moneyline.
  * Untimestamped; spread odds are almost always −110.
  * Spread and total economics use a standard −110. Moneylines use the listed odds.
* **Kalshi props.** One ladder per (game, player, stat); the market median is the interpolated 50 % threshold of valid
  mids (≤ 10¢ wide).

  | Season | Checkpoint | Asks | Families |
  |---|---|---|---|
  | 2025 | `T-90m` | YES bid/ask only; NO ask = 1 − YES bid (stated) | receiving yards, receptions, rushing yards, passing yards, passing TDs |
  | 2026 | `LAST_PREGAME` within 24 h of kickoff | both asks captured; NO is never 1 − YES | adds attempts, completions, carries, interceptions |

  * Identity: Kalshi player → GSIS, following the repository's rule order (name+team, then jersey, then unique name).
    Display name alone is never used.
  * Fee: ceiling to the cent of 0.07·p(1−p), at the entry ask.

## 5. Design

* **Game set 1 (this commit):** 31 specs, including baselines and two DATA_UNAVAILABLE entries.
  * Evaluated once on 2015–2025, with block A (2015–19) and block B (2020–25) shown.
  * Evaluated with the CFB evaluator's arithmetic and status rule, ported unchanged.
* **Game Stage A screen:** block A only (the runner enforces this). Set 2 (≤ 8 candidates) is written down and hashed
  into §10 before block B is used to judge it.
* **Props:** 14 position × stat families.
  * Walk-forward by season: train 2016…Y−1, test Y, for Y = 2018…2026.
  * Baselines: same-season average, decayed EWMA, usage-only (share × team volume × rate).
  * Opportunity model: ridge (λ = 1) on a fixed feature list (`PROP_MODEL`).
  * Feature-group ablations (PACE, SCRIPT, PASS_DEF, RUSH_DEF, PRESSURE, QB_EFF, PASS_TENDENCY, ROLE_RECENCY, HOME)
    plus pre-registered interactions. Each is an out-of-sample MAE change with a game-clustered bootstrap CI.
  * Interval coverage (50 / 80 %), role-stability slices, top-10-player removal, season stability.
* **Prop market tests:**
  * actual − ladder median (bias);
  * slope of that residual on (model median − market median), with a game-clustered SE;
  * the slope on each group's lead feature;
  * economics on the natural rung (closest to 50 %): YES if model median ≥ t·1.10, NO if ≤ t·0.90, at the captured
    executable ask, taker fee included.
* **Game script → props:** realised lead/trail share and realised plays (descriptive, post hoc) next to the pregame
  expected script and plays (predictive).
* **Correlations:** out-of-sample residual correlations across prop families within a team-game.

## 6. Multiple testing and status

| Family | Correction |
|---|---|
| Game | BH over football tests and over market tests (sets 1 + 2); Holm reported |
| Prop group ablations | BH over all (family, group) tests |
| Prop market tests | BH over all market tests |

* **Game status:** same rule as CFB (protocol §7 there). VALUE_WATCH is unreachable without executable game prices;
  EDGE_CONFIRMED is never assigned.
* **Prop group status:**
  * FOOTBALL_VALIDATED: q < 0.05, MAE gain > 0, gain positive in ≥ 60 % of test seasons.
  * DISCOVERY_ONLY: q < 0.10.
  * Otherwise REJECTED.
* **Prop market:** reported with q values. A positive economic result on Kalshi 2026 alone (≤ 5 weeks) is never more
  than VALUE_WATCH-eligible, and is labelled DISCOVERY_ONLY when n < 100.

## 7. Walk-forward (fixed)

| Model | Specification |
|---|---|
| WF-ATS | OLS of home ATS residual on 7 football nets/gaps; train < N, test N = 2018…2025 |
| WF-TOTAL | same, on 5 features |
| WF-ML | logistic on market logit + 2 football features (ridge 1.0); train 2015…N−1, test 2018…2025 |

## 8. Leakage tests

`tests/test_signal_discovery_nfl.py`:

* week-W features are invariant to doctoring week W and later; doctoring earlier weeks moves them;
* appending a future season changes nothing;
* no line, odds or score column is read by the game layer;
* the feature modules cannot import the market, outcome or evaluator modules;
* the PIT primitive excludes the row itself;
* ladder, fee and identity checks;
* NO is never 1 − YES when both asks were captured;
* the evaluator's orientation is correct;
* the runner refuses unregistered hypothesis files.

## 9. Prospective requirement

Same as CFB. Nothing becomes usable without a frozen, pre-kickoff, no-backfill prospective test that records signal
id/version, feature snapshot, contract, executable price, timestamp, settlement, code SHA and protocol SHA.

## 10. Set 2 registration (appended after the game Stage A screen)

_Pending._

## 11. Deviations

Listed in the results document.
