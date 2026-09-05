# Information shocks and repricing latency

Reproduce: `python3 scripts/research/repricing_latency.py`
Shock log: `research/shocks/shocks_2025.parquet` (also published to `market-data`).

## What can and cannot be timed

The research needs to know *when* a fact became public. That is a data problem before it is a statistics
problem, and the answer for 2025 is restrictive:

* **nflverse `injuries` carries no timestamp at all** — one row per player-week with the final designation.
  A 2025 injury-report shock therefore cannot be located in time from the data. Those shocks are labelled
  `calendar_inferred` and are **excluded from latency work**.
* **The inactive release is exact**: by league rule, inactives are published exactly 90 minutes before
  kickoff. The horizon grid brackets it — T−90m is the release instant, T−30m an hour later, T−0 kickoff.

`nfl_edge/shocks/engine.py` records every shock with a `timing_basis` of `exact`, `calendar_inferred` or
`unknown`, and the three are never mixed. Full schema: shock_id, observed_at, timing_basis, source,
shock_type, entity, prior state, new state, game, team, affected players, data confidence, related market
families.

## Correction (session 4): the treatment group was 69% non-events

Session 3 called every non-Out inactive a surprise and flagged its own treatment group as noisy, concluding
that "without a real observation timestamp there is no way to keep only the absences the market did not
already expect." **That conclusion was wrong.** Separating an expected scratch from a genuine surprise needs
no timestamp at all — it needs the player's own prior week.

A player inactive in his most recent earlier ACT/INA week is inactive again as his *expected* state. Applying
that single backward-looking gate:

| | session 3 | corrected |
|---|---|---|
| surprise inactives | 888 | **279** |
| routine (repeat) inactives | counted as surprises | 541 |
| expectation unestablished (no prior ACT/INA week) | counted as surprises | 68 |
| ruled out on report | 355 | 355 |

696 of 1,243 inactives (56%; **72% at QB**) followed another inactive week. The old surprise set was led by
Tommy DeVito (20 times), Stetson Bennett (20), Case Keenum (18) and Philip Rivers — career backups for whom
being inactive is the normal weekly condition. The corrected set's most frequent name appears 4 times.

**1,243 shocks derived for 2025**: 279 surprise inactives (timing exact), 541 routine, 68 unestablished and
355 ruled-out-on-report (calendar-inferred). Only the surprise group carries `timing_basis = exact`; the
others are `unknown` and cannot enter a latency population. By position the surprise inactives are WR 118,
RB 66, TE 53, QB 42 — QB falls from 237 to 42, which is where the contamination was worst.

## Finding 1: the direct response is unmeasurable, and that is itself the answer

Of the players with a complete T−90m / T−30m / T−0 ladder, **essentially none belonged to a player who was
then inactive.** Kalshi does not carry quoted ladders through the inactive release for players who do not
dress — the markets are gone or were never listed. Unchanged by the correction.

So the "how fast does the direct market reprice" question **cannot be asked of 2025 data**, and the reason is
economically informative: there is no stale direct quote to trade against, because the exchange removes it.
Any strategy premised on picking off a doomed player's prop after the inactive list drops has no inventory.

## Finding 2: on genuine surprises the secondary effect is gone

Same design, same windows, same control definition — only the treatment population is corrected.

| group | rungs | games | T−90m → T−30m | T−30m → T−0 | T−90m → T−0 |
|---|---|---|---|---|---|
| secondary | 339 | 30 | +0.00053 ± 0.00170 | +0.00260 ± 0.00117 | +0.00313 ± 0.00240 |
| control | 4,251 | 59 | +0.00099 ± 0.00034 | +0.00164 ± 0.00035 | +0.00263 ± 0.00048 |

Difference (secondary − control), cluster-robust on game:

| window | session 3 (contaminated) | corrected | |
|---|---|---|---|
| T−90m → T−30m | **+0.00064 ± 0.00029, z = +2.17** | −0.00046 ± 0.00169 | **z = −0.27** |
| T−30m → T−0 | −0.00037 ± 0.00026, z = −1.43 | +0.00096 ± 0.00112 | z = +0.86 |
| T−90m → T−0 | +0.00026 ± 0.00040, z = +0.65 | +0.00050 ± 0.00236 | z = +0.21 |

**The one nominally significant result in the session-3 shock work does not survive.** Its point estimate
changes sign, and no window reaches |z| > 0.9.

### What this does and does not establish

It does **not** prove the effect is zero. The corrected sample is 20× smaller (339 secondary rungs against
6,852) and its standard errors are ~5.6× wider, so the old point estimate of +0.00064 sits comfortably inside
the corrected interval. The corrected test cannot exclude an effect that size.

What it establishes is narrower and still decisive for how the result should be used: **the significance was
manufactured by the contamination.** A z of +2.17 computed on a population that is 69% non-events is not
evidence about how the market absorbs news, because most of those observations carried no news to absorb.
After the gate there is no support for the effect and the sign flips.

Either way the magnitude argument from session 3 stands and is unaffected by sample size: 0.064 probability
points against a 5–6 cent spread is ~1% of the cost of entry. Even the contaminated effect, taken at face
value, was never tradable.

## Honest limits of this test

* 279 surprises across 172 games, of which only 30 games contribute a secondary rung — the corrected test is
  underpowered and is reported as such, not as a null result.
* The gate is one prespecified rule (prior ACT/INA week). It was not tuned, and it is not swept over
  thresholds; a looser or stricter version was not searched for a better answer.
* Three windows were examined in both versions.
* 2025 only, and the horizon grid gives three points across 90 minutes — enough to see a bump, not enough to
  characterise a decay curve.

The 2026 capture stream improves on this further: ESPN and Sleeper state diffs arrive with real observation
timestamps at a 10-minute cadence, so the *moment* of a surprise is observed rather than inferred from the
league calendar. Registered as `H-20260904-021` for prospective testing.

## Finding 3: no position-specific response either (Part VIII)

Splitting the secondary contrast by the position of the *absent* player, same estimator, cluster-robust on
game, T−90m → T−30m:

| position of absent player | rungs | games | diff | se | z | p |
|---|---|---|---|---|---|---|
| QB | 64 | 7 | +0.00010 | 0.00164 | +0.06 | 0.949 |
| RB | 78 | 12 | +0.00190 | 0.00155 | +1.23 | 0.220 |
| WR | 151 | 13 | −0.00155 | 0.00335 | −0.46 | 0.643 |
| TE | 46 | — | below the 50-rung floor, not reported | | | |

Benjamini–Hochberg at q = 0.10 across the three reported positions: **nothing passes** (smallest p = 0.220
against a critical value of 0.033). No position-specific response is established.

The four-way split is exactly the kind of repeated look that manufactured the session-3 result, so it is
corrected for rather than reported raw — and the correction is not what kills it. None of the three would
reach significance uncorrected either.

**Offensive line is not testable here at all.** Kalshi lists no OL props, so an OL absence has neither a
direct nor a secondary prop ladder to measure. That is a limit of the venue, not a modelling choice, and it
means the position where an absence plausibly has the largest *structural* effect on a game is the one this
design cannot see. The ladder study (`research/ladder_shocks/`) is the route to it, since an OL absence would
show up in the margin distribution rather than in anyone's prop.

Power: 7–13 games per position cell. These are not evidence of absence; they are an absence of evidence, and
the corrected pooled test is already underpowered before splitting.
