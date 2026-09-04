# Do the role features improve the ladder, or only the mean?

Reproduce: `python3 scripts/research/ladder_role_study.py` (add `--family <name>` to refit every statistic
with one family). Output: `research/ladder_role/results.json`.

A better conditional mean does not automatically make a better ladder — Kalshi consumes P(Y ≥ k) at each
rung, and a sharper centre can leave the tails worse. This refits the whole pipeline (mean model,
opportunity model, distribution family) walk-forward 2019–2025, with and without the opportunity-engine role
features, and scores the rungs the exchange actually lists.

## Result: every statistic improves

| statistic | family | rungs | Brier base → role | Δ | LogLoss base → role | Δ | seasons improved |
|---|---|---|---|---|---|---|---|
| targets | negbin | 494,352 | 0.09409 → **0.09052** | −0.00357 (−3.8%) | 0.30468 → **0.28884** | −5.2% | **7/7** |
| receptions | negbin | 329,568 | 0.10324 → **0.10044** | −0.00281 (−2.7%) | 0.33316 → **0.31916** | −4.2% | **7/7** |
| passing_yards | normal | 34,958 | 0.13533 → **0.13405** | −0.00128 (−0.9%) | 0.41899 → **0.41510** | −0.9% | **6/6** |
| carries | negbin | 122,056 | 0.09961 → **0.09892** | −0.00069 (−0.7%) | 0.32785 → **0.32375** | −1.3% | 6/7 |
| rushing_yards | scale_emp_binned | 133,152 | 0.08976 → **0.08948** | −0.00028 | 0.29101 → **0.29087** | −0.05% | **7/7** |
| receiving_yards | scale_emp_binned | 411,960 | 0.07566 → **0.07542** | −0.00024 | 0.24851 → **0.24800** | −0.2% | **7/7** |

Six of six statistics improve on both Brier and log loss, and the sign is the same in essentially every
season. The gains are concentrated in the count ladders (targets, receptions) — which is where the route and
target-share data should help most, and it does. The yards ladders move only marginally: their family already
absorbs most of what a sharper centre offers.

## A scoring bug that produced the opposite answer, and how it was caught

Before the fix this study reported the reverse — that role features *degraded* the count ladders by +0.011
Brier, 0/7 seasons, which read as a clean structural finding about parametric families. It was an artifact.

The live-rung filter was `0.02 < predicted probability < 0.98`, **computed from each arm's own predictions**.
The two arms were therefore scored on different sets of rungs: mean predicted probability 0.257 for the
baseline against 0.291 for the role arm, on outcome base rates of 0.235 against 0.272. The comparison was
measuring the change of subset, not the change of skill.

The tell was that the role arm was better on every direct measure while losing on the aggregate: mean
absolute error on receptions fell 1.261 → 1.219 and the correlation with the outcome rose 0.617 → 0.655,
and its reliability curve was *better* calibrated (bias +0.019 against +0.022), yet its pooled Brier was
0.012 worse. Skill improving on every component while the total gets worse means the totals are over
different denominators.

The filter now comes from the **training** outcome rate at each rung — model-independent, shared by both
arms, and invisible to either at test time.

Two hypotheses were tested and rejected along the way, and both are worth recording because each looked
convincing:

* *"The Poisson IRLS is numerically unstable with unscaled features"* (shares ~0.1 against team dropbacks
  ~35 under an `exp` link with a 1e-6 ridge). Standardising every column and using a real ridge changed the
  result by less than 0.00002 Brier. The fix was kept — it is correct regardless — but it explained nothing.
* *"The family's dispersion is fitted on in-sample `mu`, whose residual is smaller than it will be live, so
  extra features wrongly tighten the tails."* Leave-one-season-out cross-fitting of the family was
  implemented to test this. It changes the pooled Brier by under 0.0002 and improves the baseline in only
  2 of 6 statistics. The concern is real in principle and negligible here; the cross-fitted arms are kept in
  the output so the claim stays checkable.

## What is adopted

`ROLE_FEATURES` in `nfl_edge/research/player_distributions.py` — route share, targets per route run, snap
share, red-zone target share, aDOT, carry share, red-zone and inside-5 carry share, and the team's
point-in-time dropback and rush-attempt volume — enter the mean model alongside the raw-count EWMA, never
instead of it. `predict_mean` reads the `role` flag out of the fitted model, so a model cannot be scored
with a different design than the one it was fitted with.

Team volume enters as the team's own point-in-time EWMA rather than a fitted projection. An earlier version
used a nested walk-forward projection that was only defined on 2019+, so on 2016–2018 training rows it was
null → 0 while test rows carried ≈35; that alone cost 0.012 Brier on the receptions ladder.
`tests/test_opportunity_leakage.py` now asserts every role feature is populated on pre-2019 rows.

## The gains do not transfer to the contracts Kalshi actually lists

The table above evaluates on a fixed synthetic ladder across the whole skill-position population. The
contracts that matter are narrower on both counts: Kalshi lists a subset of players, and it places rungs near
the money rather than on a fixed grid. Scored on the **exact 2025 Kalshi rungs** — 12,553 settled contracts
with a tradable closing book — the role arm is **not better**:

| | Brier | log loss | mean p |
|---|---|---|---|
| base (no role features) | **0.20034** | **0.58549** | 0.3775 |
| role features | 0.20151 | 0.58732 | 0.3960 |
| realised | | | 0.3770 |

Role minus base: **+0.00117 ± 0.00104** (z = +1.1) — directionally worse, not significantly so. The base
model's mean probability (0.3775) sits almost exactly on the realised rate (0.3770) while the role arm
overpredicts at 0.3960.

Splitting the 2025 fixed-ladder evaluation by whether Kalshi listed that player-game locates the reason:

| statistic | population | rungs | role − base Brier | z |
|---|---|---|---|---|
| receptions | **not listed** | 21,360 | **−0.00505 ± 0.00048** | **−10.4** |
| receptions | Kalshi-listed | 27,224 | −0.00010 ± 0.00068 | −0.2 |
| receiving_yards | not listed | 26,700 | −0.00006 ± 0.00008 | −0.7 |
| receiving_yards | Kalshi-listed | 34,030 | −0.00028 ± 0.00017 | −1.7 |
| rushing_yards | not listed | 8,088 | +0.00025 ± 0.00020 | +1.3 |
| rushing_yards | Kalshi-listed | 11,244 | −0.00036 ± 0.00043 | −0.8 |

**The improvement is concentrated in the players Kalshi does not list.** That is consistent with the
mechanism the engine was built on: route share and red-zone share pay off where a player's raw counting
history misrepresents his current role — backups, promotions, committee changes. Kalshi lists established
starters, whose raw EWMA already captures their role, so there is little left for the decomposition to add.

This is a real qualification to the headline result above, not a footnote. The 6/6 improvement is genuine on
the population it was measured on; **it is worth approximately nothing on the population that is traded**,
and on Kalshi's own rung placement it is very slightly negative.

It also puts a question mark over freezing `shadow-0.3.0` (role features on) as the Week-1 model rather than
the 0.2.0 feature set. The difference is +0.00117 ± 0.00104 — not significant in either direction — so the
freeze is left standing rather than re-cut on evidence that cannot distinguish the two. `H-20260904-010`
now carries this as its primary open question, with the prediction it was registered on already in doubt.

## Not yet established

These are calibration gains on historical settled outcomes. Whether they translate into
model-market disagreement that survives the ~2.5-point cost of crossing the Kalshi spread
(`research/efficiency_map/RESULTS.md`) is a separate question, and the shadow ledger is the only honest way
to answer it — prospectively, on markets priced before kickoff.
