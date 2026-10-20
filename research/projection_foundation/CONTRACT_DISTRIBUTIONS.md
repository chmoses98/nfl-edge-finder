# Projection distributions artifact — `sift.projection_distributions.v1` (NFL)

Companion to `CONTRACT.md` (which is recorded research and is not edited). Published by the Projection Foundation's `projection-data`
branch beside `projections/nfl/latest.json`:

| Path | Kind | Written by |
|---|---|---|
| `projections/nfl/distributions/latest.json` | rewritable view; never regresses to an older projection | `python -m nfl.live.distributions_artifact` |
| `projections/nfl/distributions/<YYYY-MM-DDTHHMMZ>.json.gz` | write-once copy, only when the content changed | same |

Nothing under `forecasts/`, `outcomes/`, `settlements/`, `corrections/` or `availability/` is written, and the code that writes `latest.json`
is not touched: the artifact is derived from what is already archived (the player rows of `latest.json` and, for each row, the pmf archived
write-once in `forecasts/nfl/`).

## Why a second artifact

SIFT's Prop Explorer draws a projection's distribution from its published quantiles and prices a line from published line probabilities.
`latest.json` carries mean, median, p10/p90 and the study's three rungs (e.g. receptions 3+, 5+, 7+): no quantiles, and no probability for the
other lines a market lists (Kittle's main line is 6+). Both come from the one pmf each row is summarised from, so they are read from it again,
exactly, and published separately and versioned instead of editing the protected research code.

## Shape

```jsonc
{
  "schema": "sift.projection_distributions.v1", "sport": "NFL",
  "projection": {"schema": "sift.projections.v1", "generated_utc": "2026-10-19T01:34:27Z", "data_asof_utc": "...", "model_version": "...", "players": 72},
  "distribution": {"basis": "integer pmf ...", "quantile_rule": "smallest integer x with P(X <= x) >= level, from the same integer pmf as the mean and the threshold probabilities",
                   "levels": [0.05, 0.1, 0.25, 0.5, 0.75, 0.9, 0.95]},
  "built_utc": "...",
  "rows": [{
    "player_id": "00-0033288", "family": "receptions", "game_id": "2026_06_WAS_SF",
    "forecast_id": "...", "forecast_generated_utc": "...",           // the archived forecast (write-once) the pmf was read from
    "mean": 5.077, "median": 5, "p10": 2, "p90": 8,                   // equal to the published row
    "quantiles": {"p05": 1, "p10": 2, "p25": 3, "p50": 5, "p75": 7, "p90": 8, "p95": 10},
    "survival": {"1": 0.99, "2": 0.9658, "3": 0.8495, "4": 0.7, "5": 0.5505, "6": 0.4, "7": 0.264, "...": 0.0},   // P(X >= k)
    "support": [0, 29]
  }],
  "excluded": [{"player_id": "...", "family": "...", "game_id": "...", "why": "..."}]
}
```

* **`survival`**: for count and binary families (receptions, targets, completions, passing attempts, carries, passing TDs, anytime TD) every integer
  line with 0.001 <= P(X >= k) <= 0.999, and the study's rungs always; for yardage families only the rungs `latest.json` publishes.
* **A row appears only if its pmf reproduces the published row**: mean (to its 3 published decimals, allowing for the archive's 7-decimal pmf
  rounding), median, p10, p90, every published threshold (to 4 decimals), and the row's own quantiles, ladder and range cohere
  (`nfl/live/distribution.py::validate_row`: ordered, finite, non-negative, integer; `p50 = median`, `p10`/`p90` = the range; ladder is one survival
  function and consistent with every quantile: `k <= q_a => P(X >= k) > 1 - a`, `k > q_a => P(X >= k) <= 1 - a`). Otherwise it is listed under
  `excluded` with the reason and readers say "no published distribution". Nothing is interpolated, invented or patched.
* **Matching**: a reader joins `rows` to the player rows of the `latest.json` it reads on `(player_id, family, game_id)` and MUST ignore the
  artifact when `projection.generated_utc` differs from that document's `generated_utc`.
* The artifact is built in the same workflow run, after the projection is published and before the archive commit, so both land in one commit.
