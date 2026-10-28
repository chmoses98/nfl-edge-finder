## NFL projection scorecard — last 7 days

Generated 2026-10-28T20:51:55Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 4426 across 27 games. Settled: 2441 (void/DNP 179, stat corrections 0).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 169 (14) | Brier 0.1837 | calib -0.032 | log loss 0.5416 | — |  |
| carries | pf-nfl (challenger) | 44 (14) | 4.812 | -0.280 | 3.332 | 70% | — |
| completions | pf-nfl (challenger) | 27 (14) | 4.909 | +0.609 | 3.364 | 93% | — |
| passing_attempts | pf-nfl (challenger) | 27 (14) | 6.416 | +1.662 | 4.554 | 93% | — |
| passing_tds | pf-nfl (challenger) | 27 (14) | 0.788 | -0.011 | 0.528 | 85% | — |
| passing_yards | pf-nfl (challenger) | 27 (14) | 57.492 | -6.105 | 40.334 | 85% | — |
| receiving_yards | pf-nfl (challenger) | 157 (14) | 21.116 | -0.022 | 14.347 | 81% | — |
| receptions | pf-nfl (challenger) | 157 (14) | 1.357 | +0.137 | 0.929 | 86% | — |
| rushing_yards | pf-nfl (challenger) | 44 (14) | 30.431 | -4.873 | 20.455 | 77% | — |
| targets | pf-nfl (challenger) | 157 (14) | 1.702 | +0.315 | 1.171 | 84% | — |
| team_pass_attempts | pf-nfl (challenger) | 28 (14) | 6.171 | +2.395 | 4.199 | 89% | — |
| team_points | pf-nfl (challenger) | 28 (14) | 7.703 | -0.106 | 5.163 | 89% | — |
| team_rush_attempts | pf-nfl (challenger) | 28 (14) | 6.224 | -1.312 | 4.388 | 75% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **INSUFFICIENT** — 44 settled forecasts (< 100)
- completions: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 27 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **INSUFFICIENT** — 44 settled forecasts (< 100)
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 28 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 28 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 28 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 7 (7) | 0.29 | -0.060 | -20.9% | [-0.41, +0.21] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 67 (14) | 0.21 | -0.028 | -13.5% | [-0.09, +0.03] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 21 (12) | 0.19 | -0.030 | -16.0% | [-0.23, +0.11] | INSUFFICIENT | monitored (no study band) |
| anytime_td | none_of_the_three | 90 (14) | 0.36 | -0.043 | -12.2% | [-0.13, +0.04] | OK |  |
| carries | new_team_first4 | 3 (3) | 7.67 | +2.864 | +37.4% | [+0.67, +5.06] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 21 (14) | 10.38 | -0.371 | -3.6% | [-3.04, +2.10] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 3 (3) | 9.67 | -3.992 | -41.3% | [-6.80, +0.74] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 22 (14) | 14.50 | -0.435 | -3.0% | [-2.45, +1.82] | INSUFFICIENT |  |
| completions | new_team_first4 | 1 (1) | 20.00 | -2.825 | -14.1% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| completions | rookie | 1 (1) | 0.00 | +20.108 | — | — | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 25 (14) | 21.04 | -0.033 | -0.2% | [-1.84, +2.11] | INSUFFICIENT |  |
| passing_attempts | new_team_first4 | 1 (1) | 28.00 | +2.229 | +8.0% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_attempts | rookie | 1 (1) | 0.00 | +31.937 | — | — | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 25 (14) | 32.16 | +0.428 | +1.3% | [-1.66, +2.74] | INSUFFICIENT |  |
| passing_tds | new_team_first4 | 1 (1) | 0.00 | +1.190 | — | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_tds | rookie | 1 (1) | 0.00 | +1.195 | — | — | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 25 (14) | 1.56 | -0.108 | -6.9% | [-0.50, +0.24] | INSUFFICIENT |  |
| passing_yards | new_team_first4 | 1 (1) | 252.00 | -61.266 | -24.3% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_yards | rookie | 1 (1) | 0.00 | +197.596 | — | — | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 25 (14) | 238.52 | -12.047 | -5.1% | [-37.40, +15.72] | INSUFFICIENT |  |
| receiving_yards | new_team_first4 | 7 (7) | 16.14 | +9.649 | +59.8% | [-4.19, +19.46] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 57 (14) | 17.30 | +2.722 | +15.7% | [-1.61, +7.23] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 18 (10) | 38.06 | -6.988 | -18.4% | [-19.34, +5.15] | INSUFFICIENT | monitored (no study band) |
| receiving_yards | none_of_the_three | 88 (14) | 43.69 | -0.473 | -1.1% | [-7.69, +5.76] | OK |  |
| receptions | new_team_first4 | 7 (7) | 1.71 | +0.739 | +43.1% | [-0.91, +1.84] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 57 (14) | 1.60 | +0.332 | +20.8% | [-0.05, +0.70] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 18 (10) | 2.78 | -0.234 | -8.4% | [-1.11, +0.41] | INSUFFICIENT | monitored (no study band) |
| receptions | none_of_the_three | 88 (14) | 3.84 | +0.064 | +1.7% | [-0.38, +0.53] | OK |  |
| rushing_yards | new_team_first4 | 3 (3) | 29.33 | +11.466 | +39.1% | [-1.47, +20.67] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 21 (14) | 43.76 | -2.873 | -6.6% | [-21.53, +9.34] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 3 (3) | 45.33 | -22.625 | -49.9% | [-37.16, -1.74] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 22 (14) | 67.27 | -7.870 | -11.7% | [-21.46, +4.63] | INSUFFICIENT |  |
| targets | new_team_first4 | 7 (7) | 2.86 | +0.650 | +22.7% | [-0.93, +2.22] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 57 (14) | 2.44 | +0.473 | +19.4% | [+0.09, +0.84] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 18 (10) | 4.06 | +0.041 | +1.0% | [-0.90, +0.93] | INSUFFICIENT | monitored (no study band) |
| targets | none_of_the_three | 88 (14) | 5.53 | +0.246 | +4.4% | [-0.25, +0.83] | OK |  |

Pooled relative bias (family-n weighted): new_team_first4 +25.2% (n=37); backup +7.4% (n=280); rookie -13.3% (n=81); none_of_the_three -2.5% (n=498)

**DNP (void) rate by pre-game participation call**: CONFIRMED_ACTIVE 0.0% (n=64); CONFIRMED_OUT 100.0% (n=43); LIKELY_ACTIVE 1.8% (n=735); LIKELY_OUT 100.0% (n=4); UNCERTAIN 18.0% (n=61)

**Settled by gate status**: PASS n=768 MAE=8.568; REVIEW n=68 MAE=10.378
