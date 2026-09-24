# DATA_PLAYER_V4 / HYBRID_PLAYER_V4

A structural player-prop challenger that runs **beside** v3 in Shadow v2. v3 (`data-player-dist-3.0.0`,
`hybrid-player-dist-2.0.0`) is a frozen benchmark: its code path, features, versions and records are unchanged.
Evidence: `research/player_engine_v4/RESULTS.md`. Status: **RESEARCH_ONLY** (both arms), by design, until prospective
evidence exists.

| arm | engine version | what it is |
|---|---|---|
| DATA_PLAYER_V4 | `data-player-dist-4.0.0` (inputs `player-inputs-4.0.0`) | snap -> volume -> allocation -> outcome |
| HYBRID_PLAYER_V4 | `hybrid-player-dist-4.0.0` | 0.85-market pmf mixture with DATA_PLAYER_V4 |

## Architecture (`nfl_edge/engines/player/v4/`)

1. **Pregame status of the player and every teammate** (`features.py`). Report OUT / DOUBTFUL / QUESTIONABLE and the
   weekly roster; a player not on an active roster spot is ruled out. Gameday inactives (roster INA) are not used in
   training, so T-24h means the same thing as T-90m. In production the target week's statuses come ONLY from the
   point-in-time injury-report vintage the context layer resolved and the run's availability captures (the more
   severe reading), never from the freshest file on disk.
2. **Teammate pool and redistribution** (`features.py`). Every player who played for the team in its last four games,
   with his recent role (mean target / carry / snap share of his last three games). A *new* absence (ruled out, played
   the team's last game) vacates its role, split into same position group / other groups / offseason departures;
   returning teammates reclaim theirs. Who absorbs it is the player's fraction of the available group's recent role,
   learned pooled across all teams -- no team- or player-specific absence rules from tiny samples.
3. **Snap-share model** (`snap.py`). Ridge per position group on EWMA / last / last-3 / max-of-4 / season-mean snap
   share, sample size, team change, returning / new, questionable, vacated and returning teammate snaps; a second
   ridge on the absolute residual gives the sd; Beta(mean, sd) on [0, 1] with p10 / p90.
4. **Team volume** (`volume.py`). Pass and rush attempts from team EWMAs, opponent-allowed EWMAs, market-implied
   team total and spread, home, roof, QB change; residual sd carried as volume uncertainty.
5. **Role allocation** (`model.py`). Target share (RB / WR / TE) and carry share (QB / RB / WR) from the player's
   share history, the predicted snap share and snap-scaled share, and the redistribution features; reconciled per
   team-game (shares scaled down when they sum past 1).
6. **Opportunity counts**. targets = volume x share, stacked with the raw-count EWMA in a two-feature Poisson GLM
   (research/opportunity: the product alone loses to the EWMA; the two together win).
7. **Outcomes**. Receptions = negative-binomial targets thinned by a shrunk catch rate; receiving / passing yards are
   compound sums of per-catch (per-completion) gammas over the uncertain count; rushing yards a shifted gamma per carry
   (a carry can lose yards); attempts / completions for starting QBs; passing TDs, interceptions and anytime TDs are
   negative binomial on opportunity-driven GLM means. `rush_rec_yards` is the convolution.
8. **Uncertainty propagation**. The latent opportunity cv^2 = (1 + cv_volume^2)(1 + cv_share^2) - 1 from the
   volume and share error models, calibrated by one scalar per statistic (kappa, maximum likelihood on training).
   Historically it adds nothing measurable (RESULTS section 3); kept because it was specified before scoring.
9. **Abstention** (`abstention.decide_v4`). Injury (own designation), role (new / changed team / returning / LOW
   role certainty), teammate shock (>= 10% of the group's opportunity vacated), snap uncertainty (sd > 0.15),
   extrapolation (snap share < 0.15), missing environment / QB1, incomplete ladder (hybrid), model unvalidated, large
   disagreement (> 5pp). `structural_state` ignores the unvalidated stamp so the rule itself can be scored.
10. **Hybrid**. Global 0.85-market mixture (`hybrid_dist.v4_weight`), floored at 0.85; adaptive per-family weights
    were tested and rejected (RESULTS section 4).

Every stage can be switched off (`model.FULL` config) for ablations; off means "what v3 used", never zero.

## Production

`nfl_edge/engines/player/v4/prospective.py` builds the arms inside `project_slate_v2.build_player_arms`, after v3,
fail-soft (a V4 failure refuses V4 records and costs nothing else). Inputs are bounded exactly as v3's
(`prospective_v3`: market-implied environment of the snapshot, completed current-season games, depth-chart QB1),
plus the statuses above. The run summary carries `player_v4` (bundle sha, distributions, overrides, seconds, bytes).

## Lean storage (`nfl_edge/projection/lean.py`, `lean-record-1.0.0`)

A v3 player record is ~8.2 KB; 45% of it (player context, run lineage, market state, game context) is identical
across arms and already in the snapshot's immutable context sidecar. V4 records keep the schema
(`projection-2.3.0`) and every field settlement, the research record, scorecards, eligibility and RUN NFL read, and
replace the shared blocks with the ids that resolve them (`storage.lean` names the version and how each block
resolves). Refusals keep their reason and identity only. Nothing already written is rewritten.

## Promotion

No automatic promotion. The eligibility layer (`nfl_edge/evaluation/eligibility.py`) keeps both arms RESEARCH_ONLY
until >= 48 prospective games over >= 3 weeks; after that the ordinary rules apply per arm and per statistic family
(`player_<stat>`), with a family never exceeding its arm.

### Measured cost (local replay of snapshot 20260923T140254Z, 1,713 player contracts, 4 vCPU)

| | main | with V4 | change |
|---|---|---|---|
| records | 19,128 | 22,554 | +3,426 (two arms) |
| DATA_PLAYER_V3 file (reference) | 672 KB | 672 KB (byte-identical) | 0 |
| DATA_PLAYER_V4 / HYBRID_PLAYER_V4 files | -- | 376 KB / 332 KB | both together = 1.05 v3 arm |
| snapshot projection bytes | 5.21 MB | 5.92 MB | +13.6% |
| projection runtime | 224 s | 253 s | +29 s (v4 build 42 s) |
| peak RSS | 1,580 MB | 1,924 MB | +345 MB |

Weekly growth estimate: production writes ~6.5 snapshots a day and one player arm is ~222 MB/week on market-data
(2026-09-17..23), so the two V4 arms add **~235 MB/week** (full-size records would have added ~445 MB). Settlement
evaluates V4 rows like any player arm (two more arms of evaluation rows per settled game); the autopsy runs for the v2
and v3 data arms only. Every existing arm's records and the context sidecar are byte-identical with and without V4.
