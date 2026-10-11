# PURE_PLAYER_V1 — market-dependency audit of the V3 / V4 / V5 player chain and the coherent simulation

Audited at `origin/main` f16c55f (2026-10-10). Read-only: nothing listed here was edited. Line numbers are at
that commit. Three kinds of dependency are separated, because a switch that removes only the first does not make
a model market-independent:

* **F — feature**: a market quantity (spread, total, implied team total, moneyline, Kalshi-implied centre,
  market ladder, residual against a line) enters a fitted model or a forecast centre.
* **S — sample selection**: whether a row is *trained on* depends on whether a market quantity exists.
* **P — population / availability**: whether a row is *forecast or evaluated at all* depends on market
  listing, quote liquidity or a market environment existing (ticker inventory, `env_known`).

## 1. Upstream edges of the V5 sports features

```
prospective_v3 (inputs)        -> game environment (spread_line / total_line) + current-season rows + QB1
  -> features_v2 / v3 / v4      -> EWMs, shares, recency, teammate absence (sports data)
  -> V4 VolumeModel             -> team pass / rush attempts            [F, S]
  -> SnapModel                  -> snap share                            (sports)
  -> share / stack models       -> targets, carries                      (sports, but driven by the [F,S] volume)
  -> efficiency rates           -> catch rate, ypr, ypc, comp, ypcomp, TD, INT  [F]
  -> distributions (V4Bundle.distributions)
V5 = V4 chain + QB identity features (qb_features.py), fitted with config {"qb_identity": True}
```

### 1.1 Game environment and population (production)

| # | file:line | kind | what |
|---|---|---|---|
| 1 | `scripts/shadow_v2/project_slate_v2.py:242-261` | F, P | `envs[gid]` is built only for games in `by_game` (games with Kalshi quotes, line 243). Centre = Kalshi-implied spread/total from the quoted ladders (`implied_game_lines`, line 250), falling back to the consensus `spread_line`/`total_line` (lines 252-253); no line -> no environment (254-255). |
| 2 | `scripts/shadow_v2/project_slate_v2.py:234-240` | F, S | The residual bank (games with `spread_line` not null) that turns that centre into a game distribution is `result - spread_line`, `total - total_line` over historical games (market residuals). |
| 3 | `nfl_edge/engines/player/prospective_v3.py:54-66` | F | `attach_market_environment`: `spread_line` / `total_line` of every prospective row = the market-implied environment; `env_known` = both present. |
| 4 | `nfl_edge/engines/player/prospective_v3.py:79-83` | P | `usable_rows`: a prospective row gets a data distribution **only if** `env_known` (market environment exists). |
| 5 | `nfl_edge/shadow/prospective.py:10-11, 47-75` | P | `upcoming_from_markets`: "every player Kalshi actually lists a market for ... We never invent a player Kalshi does not price." The forecast population **is the ticker inventory**. It also copies `spread_line`/`total_line` onto each row (73-74). |
| 6 | `nfl_edge/shadow/prospective.py:34-35` | F | `spread_team`, `implied_total` derived from those lines for prospective rows. |
| 7 | `nfl_edge/engines/player/v4/prospective.py:78, 82, 84-86, 103` | P, F | V4 production: population from `upcoming_from_markets`; environment from `attach_market_environment`; refusal "no market-implied game environment"; distributions only for `usable_rows`. |
| 8 | `nfl_edge/engines/player/v5/prospective.py:122, 126, 132-133, 151` | P, F | V5 production: identical to V4 (#7). |
| 9 | `nfl_edge/engines/player/abstention.py:73-74, 129-130` | P | Abstention `ABSTAIN_VOLUME_UNCERTAIN` when there is no market-implied game environment. |
| 10 | `scripts/shadow_v2/project_slate_v2.py:1122-1152` | P, F | V3 data arm: same `attach_market_environment` + ticker-inventory population. |

### 1.2 Historical research frame (what V3/V4/V5 are trained on)

| # | file:line | kind | what |
|---|---|---|---|
| 11 | `nfl_edge/research/player_distributions.py:136-146` | F | `load_player_games` joins the nflverse schedule's consensus **closing** `spread_line`/`total_line` and derives `spread_team`, `implied_total` for every historical row. A closing line is not point-in-time for its own game; it is the training environment of every downstream fit. |
| 12 | `nfl_edge/research/player_distributions.py:147-148` | (PIT) | `qb_starter` = the schedule's realised starting-QB id (hindsight for the game itself; not a market dependency). |
| 13 | `nfl_edge/engines/player/data_dist.py:58-59, 80` | F | V1/V2/V3 data designs include `implied_total` (V3 = V2 + V3_EXTRA, so DATA_PLAYER_V3 is market-featured). |

### 1.3 V4 VolumeModel and the V4/V5 bundle

| # | file:line | kind | what |
|---|---|---|---|
| 14 | `nfl_edge/engines/player/v4/volume.py:26-27` | F | `PASS_FEATURES` / `RUSH_FEATURES` include `implied_total`, `spread_team`. |
| 15 | `nfl_edge/engines/player/v4/volume.py:40` | F | `team_game_table` carries `implied_total`, `spread_team` per team-game. |
| 16 | **`nfl_edge/engines/player/v4/volume.py:74`** | **S** | `tr = teams[(teams.season < target_season) & teams.pa.notna() & teams.implied_total.notna()]` — **unconditional**, executed before `market_env` is consulted (line 80). With `market_env=False` the features are dropped but the training sample is still the set of team-games that have a market line. |
| 17 | `nfl_edge/engines/player/v4/volume.py:83-84` | S | The residual sd (`sd_pa`, `sd_ra`) — the volume uncertainty V4 propagates into every player — is computed on the same market-selected sample. |
| 18 | `nfl_edge/engines/player/v4/model.py:41` | F | `FULL["market_env"] = True` is the default; production and the V5 bundle use it. |
| 19 | `nfl_edge/engines/player/v4/model.py:104-105, 391-393` | F | `_env` / `VolumeModel.fit(..., market_env=cfg["market_env"])`: the switch removes features only. |
| 20 | `nfl_edge/engines/player/v4/model.py:435, 439` | F | catch rate and yards per reception regress on `implied_total`. |
| 21 | `nfl_edge/engines/player/v4/model.py:449` | F | yards per carry on `implied_total`, `spread_team`. |
| 22 | `nfl_edge/engines/player/v4/model.py:457` | F | starting-QB attempts on `implied_total`, `spread_team`. |
| 23 | `nfl_edge/engines/player/v4/model.py:462, 465` | F | completion rate, yards per completion on `implied_total` (+ `spread_team`). |
| 24 | `nfl_edge/engines/player/v4/model.py:470-472` | F | passing TDs, interceptions on `implied_total` (+ `spread_team`). |
| 25 | `nfl_edge/engines/player/v4/model.py:482` | F | anytime TD on `implied_total`. |
| 26 | `nfl_edge/engines/player/v4/prospective.py:39` | (lineage) | `implied_total`, `spread_team`, `env_source` are written into V4 record lineage. |
| 27 | `nfl_edge/engines/player/v5/model.py:24-29` | F, S | V5 = `M.fit_bundle(config={"qb_identity": True})` -> inherits every V4 edge above (market_env stays True). |
| 28 | `nfl_edge/engines/player/hybrid_dist.py` / `HYBRID_PLAYER_V4/V5` | F | 0.85 market pmf mixture by construction (docs/PLAYER_V4.md §10). |

Note on the snap / share / count stages: their features are sports-only, but they are fitted jointly with,
and fed by, the volume layer (`vol_pa`, `vol_ra` enter `l_struct_*` in the count stacks, `model.py:414`),
so the market edges #14-#17 propagate into targets, carries, receptions and yards even with `market_env=False`.

### 1.4 Research evaluation populations

| # | file:line | kind | what |
|---|---|---|---|
| 29 | `scripts/research/player_engine_v4_study.py:161-167, 232-238` | P | V4 evaluation rows = Kalshi 2025 rungs (`keys` from `load_rungs`), and only horizons with a liquid full-game Kalshi SPREAD/TOTAL ladder (`env_known`, lines 69-110, 163). Accuracy is reported on the market-listed, market-environment population only. |
| 30 | `scripts/research/player_engine_v5_study.py:134, 161, 346` | P | V5: the same rung population and `env_known` filter. |
| 31 | `scripts/research/player_engine_v4_study.py:243-244` | F | team environment for scoring = per-horizon Kalshi median. |

## 2. The coherent game simulation (`nfl_edge/sim/`)

| # | file:line | kind | what |
|---|---|---|---|
| 32 | `nfl_edge/sim/simulate.py:57-59, 158` | F | `GameInput.spread_home` / `total_line` is the game centre; `simulate_game(g.spread_home, g.total_line, bank)` draws margin/total around it. Every team-play, pass-rate and player draw is conditional on that row's margin/total (lines 130-141, 220-280). |
| 33 | `nfl_edge/sim/prospective.py:231-236` | F | prospective centre = Kalshi-implied (`fast_implied_lines`, 66-98) else consensus line (`center_source` "kalshi_implied_interpolated" / "consensus_line"). |
| 34 | `nfl_edge/sim/inputs.py:4-6, 42-56` | F | historical inputs use the consensus closing line; the market-free arm passes the DATA_ONLY centre. |
| 35 | `nfl_edge/sim/inputs.py:61-68` | F, S | `ResidualBank` = `result - spread_line`, `total - total_line` over games with `spread_line.notna() & total_line.notna()`: the **shape** of every simulated game, including the "market-free" arm's, is the residual distribution around the closing line, on a market-selected sample. |
| 36 | `nfl_edge/sim/models.py:85-99` | F (via #32) | `PLAYS_FEATURES` / `PASS_RATE_FEATURES` use `game_total`, `team_margin` — in simulation these are the draws around the market centre. |
| 37 | `nfl_edge/sim/script_v2.py:20, 62-113` | F | script cells are oriented by `spread_home` and `total_line` of the centre used ("MARKET_CENTRED_GAME"). |
| 38 | `nfl_edge/sim/prospective.py:308-383` | F | per-contract reconciliation against market ladders (`market_distribution`, `p_market`, `reconcile_weight`). |
| 39 | `nfl_edge/sim/data.py:29, 91-105`; `nfl_edge/data/silver.py:41, 87-88` | F (indirect, **VERIFIED market-informed** — see `PURE_PLAYER_V1_XPASS_VERIFICATION.md`) | `proe`, `neutral_proe`, `proe_early_ng` are built from nflfastR `xpass` / `pass_oe`; `vegas_wp` is read from play-by-play. nflfastR's `vegas_wp` is spread-conditioned by definition; whether nflfastR's expected-pass model takes the spread-adjusted win probability must be verified against its model specification before PROE (used by `nfl_edge/arms/data_only.py:57-60`, `nfl_edge/research/team_ratings.py:29`, `nfl_edge/sim/models.py:87`) is treated as sports-only. PURE_PLAYER_V1 reads no play-by-play and is unaffected. |

## 3. What PURE_PLAYER_V1 does instead (nfl_edge/engines/player/pure_v1/)

| dependency class | V3/V4/V5 | PURE_PLAYER_V1 |
|---|---|---|
| F — environment | Kalshi-implied / closing spread & total, implied team total | football-only EWMs of team / opponent volume and points, EWM point-differential margin, matchup points (`features.add_team_features`) |
| F — efficiency | `implied_total`, `spread_team` in 7 rate models | player EWM rates + opponent's prior-only allowed rates |
| S — training sample | `implied_total.notna()` filter (volume.py:74) | every REG team-game / player-game with a box score, seasons [2014, target) |
| P — forecast population | Kalshi ticker inventory + `env_known` | every QB/RB/WR/TE player-game in nflverse stats/snaps, conditional on own participation; QB passing conditional on starting |
| P — evaluation population | Kalshi rungs with liquid env | same as forecast population; market listing joined only afterwards as a diagnostic |
| schedule columns read | all (incl. spread/total/moneyline/odds) | allowlist `data.SCHEDULE_ALLOWLIST` (no market column); `attest_sports_only` refuses any market-like name |
| injury / depth chart / weather / target-game QB | injury report & roster status (V4), PIT QB resolution (V5) | **abstained**: not proven point-in-time in this repository's committed data (nflverse `injuries_<season>` has no per-row timestamp from 2025; weather is context-only) |

Runtime proof: `tests/test_pure_player_v1.py` (synthetic) and `scripts/research/pure_player_v1_mutation.py`
(real data, `research/pure_player_v1/mutation.json`) rerun the full pipeline with the schedule's market columns
removed, randomised and blanked for 30% of games and require bit-identical forecasts, with V4's VolumeModel as a
negative control that must change.
