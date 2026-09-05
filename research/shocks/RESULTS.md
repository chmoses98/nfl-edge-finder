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

**1,243 shocks derived for 2025**: 888 surprise inactives (inactive on the weekly roster *without* an Out
designation — timing exact) and 355 ruled-out-on-report (timing calendar-inferred). By position, surprise
inactives are WR 268, QB 237, RB 219, TE 164.

## Finding 1: the direct response is unmeasurable, and that is itself the answer

Of 3,787 players with a complete T−90m / T−30m / T−0 ladder, **exactly 2 rungs belonged to a player who was
then inactive.** Kalshi does not carry quoted ladders through the inactive release for players who do not
dress — the markets are gone or were never listed.

So the "how fast does the direct market reprice" question **cannot be asked of 2025 data**, and the reason is
economically informative: there is no stale direct quote to trade against, because the exchange removes it.
Any strategy premised on picking off a doomed player's prop after the inactive list drops has no inventory.

## Finding 2: secondary reallocation — a marginal first-hour bump that does not persist

Teammates at the same position who did play (the reallocation beneficiaries), against a control of players in
games with no surprise inactive at their position, over the identical window:

| group | rungs | games | T−90m → T−30m | T−30m → T−0 | T−90m → T−0 |
|---|---|---|---|---|---|
| secondary | 6,852 | 243 | +0.00139 ± 0.00026 | +0.00092 ± 0.00024 | +0.00231 ± 0.00037 |
| control | 12,773 | 263 | +0.00075 ± 0.00019 | +0.00130 ± 0.00018 | +0.00205 ± 0.00025 |

Difference (secondary − control), cluster-robust on game:

| window | difference | z |
|---|---|---|
| **T−90m → T−30m** | **+0.00064 ± 0.00029** | **+2.17** |
| T−30m → T−0 | −0.00037 ± 0.00026 | −1.43 |
| T−90m → T−0 (net) | +0.00026 ± 0.00040 | +0.65 |

Beneficiaries' prices rise faster than control in the first hour after the release, then give most of it back;
across the full window the difference is indistinguishable from zero. The first-hour effect is **z = 2.17
across three windows tested**, so it is weak before any multiplicity adjustment.

And the magnitude settles it regardless: **0.064 probability points, against a 5–6 cent spread.** Even taken
at face value the effect is roughly 1% of the cost of entry.

## Honest limits of this test

* The treatment group is noisy. "Inactive without an Out designation" includes routine healthy scratches and
  third quarterbacks whose absence was never news; 237 of the 888 are QBs. Without a real observation
  timestamp there is no way to keep only the absences the market did not already expect, and that
  attenuates any true effect toward zero.
* Three windows were examined. The one significant result is the first of them.
* 2025 only, and the horizon grid gives three points across 90 minutes — enough to see a bump, not enough to
  characterise a decay curve.

The 2026 capture stream removes the first limitation: ESPN and Sleeper state diffs arrive with real
observation timestamps at a 10-minute cadence, so a genuine surprise can be distinguished from a scratch that
everyone expected. Registered as `H-20260904-021` for prospective testing.
