## NFL projection scorecard — last 7 days

Generated 2026-11-03T21:34:47Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 7577 across 41 games. Settled: 3400 (void/DNP 253, stat corrections 0).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 179 (14) | Brier 0.1800 | calib -0.037 | log loss 0.5348 | — |  |
| carries | pf-nfl (challenger) | 51 (14) | 4.859 | -0.906 | 3.418 | 78% | — |
| completions | pf-nfl (challenger) | 27 (14) | 6.718 | +2.094 | 4.838 | 63% | — |
| passing_attempts | pf-nfl (challenger) | 27 (14) | 8.222 | +3.220 | 5.938 | 85% | — |
| passing_tds | pf-nfl (challenger) | 27 (14) | 1.000 | -0.022 | 0.645 | 85% | — |
| passing_yards | pf-nfl (challenger) | 27 (14) | 75.905 | +12.053 | 54.709 | 63% | — |
| receiving_yards | pf-nfl (challenger) | 162 (14) | 21.269 | +1.255 | 14.614 | 79% | — |
| receptions | pf-nfl (challenger) | 162 (14) | 1.612 | +0.129 | 1.097 | 78% | — |
| rushing_yards | pf-nfl (challenger) | 51 (14) | 29.962 | -5.745 | 21.378 | 76% | — |
| targets | pf-nfl (challenger) | 162 (14) | 1.935 | +0.214 | 1.340 | 80% | — |
| team_pass_attempts | pf-nfl (challenger) | 28 (14) | 7.021 | +2.504 | 5.033 | 79% | — |
| team_points | pf-nfl (challenger) | 28 (14) | 8.320 | -0.447 | 5.766 | 71% | — |
| team_rush_attempts | pf-nfl (challenger) | 28 (14) | 6.289 | -1.884 | 4.485 | 82% | — |

**Drift checks**

- anytime_td: **ALERT** — bias -0.037 (95% CI -0.076..-0.000) exceeds 5% of the mean
- carries: **INSUFFICIENT** — 51 settled forecasts (< 100)
- completions: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 27 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **INSUFFICIENT** — 51 settled forecasts (< 100)
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 28 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 28 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 28 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 6 (4) | 0.00 | +0.147 | — | [+0.13, +0.16] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 75 (14) | 0.17 | +0.009 | +5.2% | [-0.05, +0.07] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 21 (10) | 0.10 | +0.098 | +102.8% | [-0.02, +0.21] | INSUFFICIENT | monitored (no study band) |
| anytime_td | none_of_the_three | 95 (14) | 0.39 | -0.089 | -22.8% | [-0.17, -0.02] | OK |  |
| carries | new_team_first4 | 4 (4) | 4.00 | +1.378 | +34.5% | [-1.07, +4.11] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 26 (14) | 8.92 | -0.282 | -3.2% | [-2.53, +1.77] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 4 (4) | 12.50 | -2.564 | -20.5% | [-11.36, +5.80] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 23 (13) | 15.61 | -1.972 | -12.6% | [-4.23, +0.25] | INSUFFICIENT |  |
| completions | none_of_the_three | 27 (14) | 18.70 | +2.094 | +11.2% | [-1.31, +5.56] | INSUFFICIENT |  |
| passing_attempts | none_of_the_three | 27 (14) | 29.04 | +3.220 | +11.1% | [-0.88, +7.38] | INSUFFICIENT |  |
| passing_tds | none_of_the_three | 27 (14) | 1.48 | -0.022 | -1.5% | [-0.52, +0.51] | INSUFFICIENT |  |
| passing_yards | none_of_the_three | 27 (14) | 214.19 | +12.053 | +5.6% | [-31.13, +54.68] | INSUFFICIENT |  |
| receiving_yards | new_team_first4 | 4 (3) | 4.25 | +13.258 | +312.0% | [+10.12, +14.91] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 61 (14) | 16.89 | +4.573 | +27.1% | [+0.39, +9.47] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 18 (9) | 23.56 | +7.535 | +32.0% | [-0.72, +15.51] | INSUFFICIENT | monitored (no study band) |
| receiving_yards | none_of_the_three | 93 (14) | 42.76 | -1.360 | -3.2% | [-10.12, +5.65] | OK |  |
| receptions | new_team_first4 | 4 (3) | 0.50 | +1.132 | +226.4% | [+0.56, +1.84] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 61 (14) | 1.56 | +0.401 | +25.7% | [-0.02, +0.80] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 18 (9) | 2.39 | +0.191 | +8.0% | [-0.64, +1.32] | INSUFFICIENT | monitored (no study band) |
| receptions | none_of_the_three | 93 (14) | 3.72 | -0.003 | -0.1% | [-0.66, +0.68] | OK |  |
| rushing_yards | new_team_first4 | 4 (4) | 12.00 | +11.614 | +96.8% | [+2.42, +22.49] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 26 (14) | 44.73 | -7.601 | -17.0% | [-20.05, +4.72] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 4 (4) | 44.00 | -3.272 | -7.4% | [-41.95, +38.32] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 23 (13) | 63.30 | -6.251 | -9.9% | [-16.28, +3.48] | INSUFFICIENT |  |
| targets | new_team_first4 | 4 (3) | 0.75 | +1.609 | +214.5% | [+1.14, +2.20] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 61 (14) | 2.43 | +0.577 | +23.8% | [+0.10, +1.06] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 18 (9) | 3.56 | +0.524 | +14.7% | [-0.59, +1.85] | INSUFFICIENT | monitored (no study band) |
| targets | none_of_the_three | 93 (14) | 5.47 | -0.009 | -0.2% | [-0.75, +0.81] | OK |  |

Pooled relative bias (family-n weighted): backup +14.6% (n=310); rookie +36.5% (n=83); none_of_the_three -4.3% (n=528); new_team_first4 +176.8% (n=20)

**DNP (void) rate by pre-game participation call**: CONFIRMED_OUT 100.0% (n=33); LIKELY_ACTIVE 3.0% (n=804); LIKELY_OUT 100.0% (n=6); UNCERTAIN 10.4% (n=106)

**Settled by gate status**: PASS n=774 MAE=8.876; REVIEW n=101 MAE=14.539
