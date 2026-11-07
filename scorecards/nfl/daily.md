## NFL projection scorecard — last 7 days

Generated 2026-11-07T18:39:21Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 9928 across 56 games. Settled: 3470 (void/DNP 253, stat corrections 0).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 180 (14) | Brier 0.1782 | calib -0.033 | log loss 0.5312 | — |  |
| carries | pf-nfl (challenger) | 50 (14) | 4.632 | -0.785 | 3.329 | 78% | — |
| completions | pf-nfl (challenger) | 27 (14) | 6.748 | +2.882 | 4.836 | 63% | — |
| passing_attempts | pf-nfl (challenger) | 27 (14) | 8.258 | +4.412 | 5.952 | 78% | — |
| passing_tds | pf-nfl (challenger) | 27 (14) | 1.004 | +0.076 | 0.640 | 93% | — |
| passing_yards | pf-nfl (challenger) | 27 (14) | 78.947 | +18.077 | 56.744 | 59% | — |
| receiving_yards | pf-nfl (challenger) | 161 (14) | 21.874 | +2.695 | 14.784 | 76% | — |
| receptions | pf-nfl (challenger) | 161 (14) | 1.564 | +0.292 | 1.052 | 77% | — |
| rushing_yards | pf-nfl (challenger) | 50 (14) | 30.368 | -5.258 | 21.655 | 76% | — |
| targets | pf-nfl (challenger) | 161 (14) | 1.919 | +0.429 | 1.314 | 78% | — |
| team_pass_attempts | pf-nfl (challenger) | 28 (14) | 7.182 | +3.586 | 5.124 | 75% | — |
| team_points | pf-nfl (challenger) | 28 (14) | 8.603 | -0.598 | 5.867 | 71% | — |
| team_rush_attempts | pf-nfl (challenger) | 28 (14) | 6.442 | -2.312 | 4.574 | 82% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **INSUFFICIENT** — 50 settled forecasts (< 100)
- completions: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 27 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **INSUFFICIENT** — 50 settled forecasts (< 100)
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 28 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 28 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 28 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 5 (3) | 0.00 | +0.150 | — | [+0.13, +0.16] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 76 (14) | 0.18 | +0.002 | +1.0% | [-0.05, +0.05] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 24 (11) | 0.08 | +0.098 | +117.6% | [-0.01, +0.20] | INSUFFICIENT | monitored (no study band) |
| anytime_td | none_of_the_three | 95 (14) | 0.37 | -0.077 | -20.9% | [-0.14, -0.01] | OK |  |
| carries | new_team_first4 | 3 (3) | 5.00 | +1.021 | +20.4% | [-2.96, +4.51] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 26 (14) | 9.81 | -0.582 | -5.9% | [-3.37, +1.40] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 4 (4) | 12.50 | -2.564 | -20.5% | [-11.36, +5.80] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 22 (13) | 14.91 | -1.390 | -9.3% | [-3.50, +0.63] | INSUFFICIENT |  |
| completions | rookie | 1 (1) | 10.00 | +7.283 | +72.8% | — | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 26 (14) | 18.00 | +2.713 | +15.1% | [-0.54, +6.36] | INSUFFICIENT |  |
| passing_attempts | rookie | 1 (1) | 18.00 | +11.421 | +63.5% | — | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 26 (14) | 28.00 | +4.142 | +14.8% | [+0.28, +7.95] | INSUFFICIENT |  |
| passing_tds | rookie | 1 (1) | 0.00 | +1.058 | — | — | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 26 (14) | 1.42 | +0.039 | +2.7% | [-0.48, +0.58] | INSUFFICIENT |  |
| passing_yards | rookie | 1 (1) | 60.00 | +122.378 | +204.0% | — | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 26 (14) | 212.62 | +14.065 | +6.6% | [-31.43, +54.98] | INSUFFICIENT |  |
| receiving_yards | new_team_first4 | 3 (2) | 5.67 | +14.536 | +256.5% | [+13.80, +14.91] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 60 (14) | 16.38 | +5.640 | +34.4% | [+0.81, +11.66] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 21 (10) | 20.48 | +8.878 | +43.4% | [+0.99, +16.73] | INSUFFICIENT | monitored (no study band) |
| receiving_yards | none_of_the_three | 93 (14) | 40.45 | +0.480 | +1.2% | [-7.47, +7.52] | OK |  |
| receptions | new_team_first4 | 3 (2) | 0.67 | +0.985 | +147.8% | [+0.56, +1.84] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 60 (14) | 1.50 | +0.460 | +30.6% | [+0.08, +0.88] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 21 (10) | 2.10 | +0.358 | +17.1% | [-0.45, +1.38] | INSUFFICIENT | monitored (no study band) |
| receptions | none_of_the_three | 93 (14) | 3.44 | +0.243 | +7.1% | [-0.34, +0.86] | OK |  |
| rushing_yards | new_team_first4 | 3 (3) | 15.33 | +10.963 | +71.5% | [-0.98, +24.52] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 26 (14) | 47.31 | -7.245 | -15.3% | [-20.22, +5.80] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 4 (4) | 44.00 | -3.272 | -7.4% | [-41.95, +38.32] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 22 (13) | 62.05 | -5.589 | -9.0% | [-16.08, +5.34] | INSUFFICIENT |  |
| targets | new_team_first4 | 3 (2) | 1.00 | +1.492 | +149.2% | [+1.14, +2.20] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 60 (14) | 2.35 | +0.686 | +29.2% | [+0.10, +1.24] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 21 (10) | 3.10 | +0.799 | +25.8% | [-0.18, +1.97] | INSUFFICIENT | monitored (no study band) |
| targets | none_of_the_three | 93 (14) | 5.12 | +0.297 | +5.8% | [-0.35, +0.97] | OK |  |

Pooled relative bias (family-n weighted): backup +16.8% (n=308); rookie +49.6% (n=98); none_of_the_three -0.1% (n=522); new_team_first4 +129.1% (n=15)

**DNP (void) rate by pre-game participation call**: CONFIRMED_OUT 100.0% (n=33); LIKELY_ACTIVE 3.0% (n=794); LIKELY_OUT 0.0% (n=4); UNCERTAIN 10.2% (n=108)

**Settled by gate status**: PASS n=764 MAE=8.961; REVIEW n=107 MAE=15.070

**Availability capture** (last run): mean coverage 1.0, participation calls {'LIKELY_ACTIVE': 182, 'CONFIRMED_OUT': 12, 'UNCERTAIN': 22, 'LIKELY_OUT': 2}
