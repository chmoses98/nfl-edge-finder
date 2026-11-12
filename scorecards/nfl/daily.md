## NFL projection scorecard — last 7 days

Generated 2026-11-12T21:08:16Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 12013 across 70 games. Settled: 4378 (void/DNP 349, stat corrections 2).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 183 (15) | Brier 0.1733 | calib +0.007 | log loss 0.5258 | — |  |
| carries | pf-nfl (challenger) | 51 (15) | 3.921 | +0.122 | 2.942 | 80% | — |
| completions | pf-nfl (challenger) | 27 (15) | 2.774 | +0.761 | 2.181 | 93% | — |
| passing_attempts | pf-nfl (challenger) | 27 (15) | 4.602 | +1.229 | 3.306 | 93% | — |
| passing_tds | pf-nfl (challenger) | 27 (15) | 0.893 | +0.082 | 0.605 | 78% | — |
| passing_yards | pf-nfl (challenger) | 27 (15) | 57.587 | -4.317 | 39.473 | 85% | — |
| receiving_yards | pf-nfl (challenger) | 165 (15) | 19.748 | +0.554 | 13.739 | 82% | — |
| receptions | pf-nfl (challenger) | 165 (15) | 1.333 | +0.152 | 0.933 | 87% | — |
| rushing_yards | pf-nfl (challenger) | 51 (15) | 19.799 | +4.360 | 14.501 | 84% | — |
| targets | pf-nfl (challenger) | 165 (15) | 1.760 | +0.283 | 1.217 | 87% | — |
| team_pass_attempts | pf-nfl (challenger) | 30 (15) | 4.265 | +1.576 | 3.100 | 90% | — |
| team_points | pf-nfl (challenger) | 30 (15) | 6.385 | +0.491 | 4.722 | 83% | — |
| team_rush_attempts | pf-nfl (challenger) | 30 (15) | 5.148 | -0.252 | 3.749 | 87% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **INSUFFICIENT** — 51 settled forecasts (< 100)
- completions: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 27 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **INSUFFICIENT** — 51 settled forecasts (< 100)
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 30 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 30 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 30 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 3 (2) | 0.00 | +0.173 | — | [+0.15, +0.21] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 75 (15) | 0.17 | +0.014 | +8.3% | [-0.10, +0.10] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 25 (13) | 0.16 | +0.036 | +22.4% | [-0.09, +0.16] | INSUFFICIENT | monitored (no study band) |
| anytime_td | none_of_the_three | 100 (15) | 0.31 | +0.001 | +0.5% | [-0.07, +0.08] | OK |  |
| carries | new_team_first4 | 1 (1) | 0.00 | +5.885 | — | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 24 (14) | 10.50 | -1.444 | -13.8% | [-2.86, +0.45] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 5 (4) | 9.80 | +1.603 | +16.4% | [-2.17, +4.12] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 25 (15) | 12.16 | +1.525 | +12.5% | [+0.05, +3.27] | INSUFFICIENT |  |
| completions | new_team_first4 | 2 (2) | 16.50 | +2.495 | +15.1% | [+0.06, +4.93] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| completions | rookie | 1 (1) | 10.00 | +7.283 | +72.8% | — | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 24 (13) | 20.54 | +0.345 | +1.7% | [-1.44, +1.96] | INSUFFICIENT |  |
| passing_attempts | new_team_first4 | 2 (2) | 24.50 | +6.812 | +27.8% | [+2.96, +10.67] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_attempts | rookie | 1 (1) | 18.00 | +11.421 | +63.5% | — | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 24 (13) | 32.04 | +0.339 | +1.1% | [-1.78, +2.67] | INSUFFICIENT |  |
| passing_tds | new_team_first4 | 2 (2) | 0.00 | +1.118 | — | [+1.05, +1.19] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_tds | rookie | 1 (1) | 0.00 | +1.058 | — | — | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 24 (13) | 1.58 | -0.045 | -2.8% | [-0.56, +0.47] | INSUFFICIENT |  |
| passing_yards | new_team_first4 | 2 (2) | 146.50 | +49.706 | +33.9% | [+29.86, +69.55] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_yards | rookie | 1 (1) | 60.00 | +122.378 | +204.0% | — | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 24 (13) | 246.79 | -14.098 | -5.7% | [-41.27, +16.30] | INSUFFICIENT |  |
| receiving_yards | new_team_first4 | 2 (2) | 18.00 | +8.029 | +44.6% | [+5.86, +10.19] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 61 (15) | 20.90 | +0.793 | +3.8% | [-6.64, +8.20] | OK | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 22 (11) | 30.73 | -0.756 | -2.5% | [-10.86, +8.96] | INSUFFICIENT | monitored (no study band) |
| receiving_yards | none_of_the_three | 96 (15) | 41.55 | +2.006 | +4.8% | [-5.06, +8.03] | OK |  |
| receptions | new_team_first4 | 2 (2) | 1.50 | +0.317 | +21.1% | [-0.35, +0.99] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 61 (15) | 1.75 | +0.201 | +11.4% | [-0.20, +0.68] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 22 (11) | 2.45 | +0.055 | +2.2% | [-0.48, +0.67] | INSUFFICIENT | monitored (no study band) |
| receptions | none_of_the_three | 96 (15) | 3.62 | +0.229 | +6.3% | [-0.15, +0.65] | OK |  |
| rushing_yards | new_team_first4 | 1 (1) | 0.00 | +26.586 | — | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 24 (14) | 42.17 | -3.158 | -7.5% | [-15.14, +8.49] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 5 (4) | 38.60 | +8.821 | +22.9% | [-11.88, +27.53] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 25 (15) | 47.72 | +10.391 | +21.8% | [+2.99, +20.33] | INSUFFICIENT |  |
| targets | new_team_first4 | 2 (2) | 2.00 | +0.928 | +46.4% | [-0.30, +2.15] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 61 (15) | 2.84 | +0.171 | +6.0% | [-0.53, +0.94] | OK | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 22 (11) | 3.59 | +0.425 | +11.8% | [-0.30, +1.24] | INSUFFICIENT | monitored (no study band) |
| targets | none_of_the_three | 96 (15) | 5.24 | +0.439 | +8.4% | [-0.04, +0.90] | OK |  |

Pooled relative bias (family-n weighted): backup +4.6% (n=306); rookie +13.0% (n=104); none_of_the_three +4.9% (n=534); new_team_first4 +31.5% (n=12)

**DNP (void) rate by pre-game participation call**: CONFIRMED_OUT 100.0% (n=55); LIKELY_ACTIVE 3.3% (n=858); LIKELY_OUT 42.9% (n=7); UNCERTAIN 15.6% (n=64)

**Settled by gate status**: PASS n=825 MAE=7.681; REVIEW n=63 MAE=7.684

**Availability capture** (last run): mean coverage 1.0, participation calls {'LIKELY_ACTIVE': 215, 'CONFIRMED_OUT': 1, 'LIKELY_OUT': 2}
