# H-20260904-022: validating the opportunity engine on the population that is actually traded

Reproduce: `python3 scripts/research/listed_validation.py`

The role/opportunity features were validated on a fixed synthetic ladder across every skill-position player.
Kalshi lists a narrow subset — established starters — and places rungs near the money. This is the decisive
re-test on the exact contracts Kalshi listed in 2025: **24,731 settled rungs across 254 games**, identical
observations for every arm, clustered on game.

| arm | Brier | LogLoss | Δ Brier vs base | se | z |
|---|---|---|---|---|---|
| base (no role features) | **0.19983** | 0.58541 | — | — | — |
| + role features | 0.20012 | 0.58547 | **+0.00029** | 0.00072 | +0.41 |
| + opponent defence | 0.19962 | 0.58475 | −0.00021 | 0.00029 | −0.72 |
| + both | 0.19965 | 0.58440 | −0.00017 | 0.00071 | −0.25 |

By statistic, role minus base (negative = role better):

| statistic | n | games | base | role | Δ | z |
|---|---|---|---|---|---|---|
| anytime_td | 3369 | 254 | 0.17124 | 0.16969 | −0.00155 | −1.60 |
| passing_yards | 2757 | 178 | 0.16994 | 0.16818 | −0.00176 | −1.39 |
| rushing_yards | 2821 | 175 | 0.22755 | 0.22651 | −0.00104 | −0.79 |
| receiving_yards | 8892 | 179 | 0.21977 | 0.21965 | −0.00012 | −0.18 |
| passing_tds | 648 | 93 | 0.15273 | 0.15287 | +0.00014 | +0.32 |
| receptions | 6244 | 138 | 0.19241 | 0.19582 | +0.00341 | +1.61 |

## Decision: RETIRED

The preregistered rule was: keep the features only if they reliably improve the traded population. They do
not. Overall +0.00029 ± 0.00072 (z = +0.41), improving in **0 of 6 statistics at |z| > 2**. Opponent defence
is nominally better (−0.00021) but also insignificant, and was already shown to be fully encompassed by the
market price.

**Role features are now OFF by default in the shadow pricer** (`use_role_features`, default `False`). They
are not deleted — the frozen Week-1 arm `shadow-0.3.0` was built with them and passes the flag explicitly so
it stays reproducible for the H-20260904-010 prospective comparison. New pricing runs default to
`shadow-0.4.0` without them.

This is the third confirmation of H-022: a property validated on the full player population failed to
transfer to the traded one. Three for three, still no counterexample.

## A bug this surfaced

Adding `use_role_features` to the bundle config changed the model's `artifact_sha`, and the Week-1 audit
immediately failed with "frozen model does NOT reproduce: 3f17f50c82510604 vs 76facd384b51e817" — on a model
that was in fact bit-identical. The hash was covering an **input directive** rather than a property of the
fitted model, and the outcome was already recorded separately as `role_features`. The directive is now
excluded from the hashed payload and the freeze reproduces exactly again. Without the rebuild check added
earlier in this session, this would have silently broken the frozen arm's identity.
