# DATA_ONLY_SRA — QB-conditioned team offence (STARTER_REGIME_ADJUSTED team strength)

> **RESEARCH_ONLY. Not validated. Not wired into any packet, arm, gate, staking or betting path.**
> Model id `DATA_ONLY_SRA`, version `starter-regime-0.1.0`, code `nfl_edge/research/starter_regime.py`,
> tests `tests/test_starter_regime_research.py`. It does **not** modify or overwrite DATA_ONLY
> (`data_only-1.0.0`), Player V3, V4 or V5, the frozen artifact `research/three_arm/data_only_artifact_2026.json`,
> or any preregistered constant of H-20260910-026.
>
> Proposed hypothesis id for the registry: to be assigned by the integrator (next free `H-2026092x-NNN`); this file is
> the full text. Filing it through `research/hypothesis_registry/` is left to the integrator so the registry index and
> its governance tests are regenerated in one place.

## 1. Motivation (generation evidence only — never validation)

2026 Week 3 TNF, ATL @ GB. DATA_ONLY priced GB +7.14 against a market of GB +5.5 at every canonical horizon. The
audit (`research/tnf_audit_2026_w03/FOOTBALL_AUDIT.md`) reproduced that centre bit-for-bit from public data through the
unmodified production code and found:

* ATL's two 2026 games were started by Cooper Rush (W1; W2 with Jack Strand relieving). ATL dropback EPA/play was
  −0.61 and −0.68 in those games. Michael Penix was named the W3 starter on 2026-09-21 (ESPN item timestamped 20:39Z)
  and was chart QB1 with no designation from 2026-09-23T11:49Z.
* DATA_ONLY has no quarterback term (documented: "quarterback identity (no validated coefficient)"); every past game
  is weighted only by recency (half-life 10 weeks) and season (×0.4). The two Rush/Strand games were at full weight.
* Removing ATL's 2026 offensive rows alone moves DATA_ONLY from GB +7.14 to GB +3.85 (−3.28 pts); the ATL-offence
  rating terms contribute +4.18 of the +7.14 total. The DATA_ONLY centre jumped from +4.21 to +7.17 on 2026-09-20 at
  the moment the W2 CAR@ATL game (Rush/Strand) entered the ratings.

One game is an anecdote. It can motivate a hypothesis and define a diagnostic; it cannot select a parameter or count as
evidence for the hypothesis. The grid `w ∈ {1, .5, .25, 0}` computed for ATL@GB
(`research/tnf_audit_2026_w03/sra_retrospective_diagnostic.json`: 7.14 / 5.98 / 5.03 / 3.61) is recorded as a
diagnostic and **must not** be used to choose `w_regime`.

## 2. The change (generic, one parameter)

For each metric in the DATA_ONLY opponent-adjusted ratings regression, offensive team-game rows whose **past-game
starter** (the passer with the most dropbacks in that completed game) differs from the team's **projected starter for
the target game** are multiplied by `w_regime ∈ [0, 1]`. Applies to the ten scrimmage-offence metrics; special-teams
EPA is never adjusted. Defensive ratings are not directly adjusted (the joint regression down-weights what the same row
says about the opponent defence; recorded). A team with no resolved projected starter gets no adjustment. No team,
player or game is special-cased.

Point in time: past-game starters only from games final before the cutoff (`starters_from_pbp` ignores any other game
id; `regime_weights` raises `LeakageError` on a post-cutoff row or starter). The projected starter comes only from the
pregame QB resolver (`nfl_edge/context/qb_resolution.py`, qb-resolution-1.0.0) at the cutoff; the module has no input
through which the target game's realised starter can enter. The margin/total ridge artifact is **unchanged**
(`e544b99917b9d0b1`) — only the ratings feeding it change — so the challenger is DATA_ONLY with one changed input layer.

## 3. Stage A — historical calibration (pre-2026 data only), then FREEZE

* Data: 2018–2025 REG seasons, walk-forward exactly as DATA_ONLY's weekly research snapshot (`ratings_for_week`).
  Realised-starter label for past games from play-by-play (most dropbacks). For the projected starter in the
  historical walk-forward, use the realised starter of the target game **as an oracle upper bound** AND, separately,
  the previous game's starter (a point-in-time naive rule); report both, and state that only the resolver is used
  prospectively.
* Choose `w_regime` from the pre-declared grid {0, 0.25, 0.5, 0.75, 1.0} by walk-forward margin MAE on 2021–2025
  (fit window seasons < evaluation season). Tie-break toward 1.0 (no change). Report every grid point.
* Materiality gate: the chosen w must improve walk-forward margin MAE by ≥ 0.05 pts overall AND on the subset of
  team-games where the projected starter differs from ≥1 of the team's last 4 starters (the "regime-change subset"),
  and must not worsen any single season by > 0.05. Otherwise the hypothesis is REJECTED at Stage A and no prospective
  arm runs.
* FREEZE: write `research/starter_regime/sra_freeze.json` (w_regime, code sha, artifact sha, grid results) and commit
  it **before the first kickoff of the first prospective week**.

## 4. Stage B — prospective test (the only evidence that can validate)

* **Start: 2026 Week 4** (first kickoff Thursday 2026-10-01, US time), **provided the Stage-A freeze is committed before
  that kickoff**. If it is not, the prospective window starts with the first week whose first kickoff is after the
  freeze commit. Week 3 (including ATL@GB) is excluded forever as generation evidence.
* Snapshots: the same canonical horizons as the three-arm experiment (T-24h, T-6h, T-90m, T-30m) and latest-pregame
  (primary), computed as a **separate research record** beside DATA_ONLY; the three-arm snapshot, its CRN draws and its
  registry are not modified.
* Primary endpoint: paired margin absolute-error difference |SRA − actual| − |DATA_ONLY − actual|, latest-pregame, all
  games, game-clustered SE. Secondary: the same on the regime-change subset (projected starter ≠ plurality starter of the
  team's in-window 2026 games); total MAE; deviation-from-market TOWARD/AWAY/UNCHANGED vs close, as in H-20260910-026.
* Minimum sample: no verdict before 64 distinct games AND 12 regime-change team-games; before that every report says
  INSUFFICIENT_EVIDENCE.
* Success: primary difference < 0 with 95% game-clustered interval excluding 0, and the regime-change subset
  directionally consistent. Anything else is NOT_SUPPORTED. There is no partial promotion.
* Authority: none at any outcome. A supported result becomes a proposal for a new versioned arm, reviewed separately.

## 5. Leakage controls (tested)

`tests/test_starter_regime_research.py`: identical to the production solver without weights; w=1 no-op; only the
changed team's offensive rows move; special teams never weighted; unknown starter → no adjustment; post-cutoff rows and
starters refused; poisoning every post-cutoff row does not move the ratings by a bit; `starters_from_pbp` never reads
the target game; and no module under `nfl_edge/handicap`, `nfl_edge/arms`, `nfl_edge/shadow*`, `scripts/handicap`,
`scripts/shadow` references this module.

## 6. Known limitations

* The resolver is only as good as the injury/depth-chart captures; a wrong projected starter makes SRA worse than
  DATA_ONLY for that team (measured in Stage B, not assumed away).
* Most-dropbacks is a coarse starter label (injury exits mid-game are counted as the other QB's game).
* Rush efficiency is included among QB-conditioned metrics by the generic definition (box-count effects), not because
  ATL's W3 rushing looked different; Stage A reports the ablation without `off_rush_epa` for transparency but may not
  choose between the two by the prospective data.
