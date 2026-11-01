## NFL projection scorecard — last 7 days

Generated 2026-11-01T15:10:01Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 7461 across 41 games. Settled: 2515 (void/DNP 185, stat corrections 0).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 155 (13) | Brier 0.1859 | calib -0.042 | log loss 0.5437 | — |  |
| carries | pf-nfl (challenger) | 39 (13) | 5.361 | -0.632 | 3.657 | 69% | — |
| completions | pf-nfl (challenger) | 25 (13) | 5.149 | +0.594 | 3.500 | 80% | — |
| passing_attempts | pf-nfl (challenger) | 25 (13) | 7.176 | +1.077 | 4.935 | 88% | — |
| passing_tds | pf-nfl (challenger) | 25 (13) | 0.851 | -0.069 | 0.562 | 72% | — |
| passing_yards | pf-nfl (challenger) | 25 (13) | 56.122 | -2.279 | 40.319 | 84% | — |
| receiving_yards | pf-nfl (challenger) | 145 (13) | 20.062 | +0.646 | 13.611 | 84% | — |
| receptions | pf-nfl (challenger) | 145 (13) | 1.361 | +0.094 | 0.925 | 86% | — |
| rushing_yards | pf-nfl (challenger) | 39 (13) | 32.084 | -5.975 | 21.676 | 74% | — |
| targets | pf-nfl (challenger) | 145 (13) | 1.726 | +0.253 | 1.193 | 88% | — |
| team_pass_attempts | pf-nfl (challenger) | 26 (13) | 6.677 | +1.764 | 4.465 | 85% | — |
| team_points | pf-nfl (challenger) | 26 (13) | 7.682 | -0.636 | 5.160 | 85% | — |
| team_rush_attempts | pf-nfl (challenger) | 26 (13) | 5.966 | -1.758 | 4.276 | 77% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **INSUFFICIENT** — 39 settled forecasts (< 100)
- completions: **INSUFFICIENT** — 25 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 25 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 25 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 25 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **INSUFFICIENT** — 39 settled forecasts (< 100)
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 26 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 26 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 26 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 6 (6) | 0.33 | -0.140 | -41.9% | [-0.47, +0.16] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 61 (13) | 0.20 | -0.019 | -9.8% | [-0.10, +0.05] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 18 (10) | 0.17 | -0.011 | -6.3% | [-0.17, +0.13] | INSUFFICIENT | monitored (no study band) |
| anytime_td | none_of_the_three | 84 (13) | 0.38 | -0.061 | -16.1% | [-0.15, +0.02] | OK |  |
| carries | new_team_first4 | 3 (3) | 5.00 | +3.626 | +72.5% | [+2.45, +4.79] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 18 (13) | 10.89 | -0.596 | -5.5% | [-4.37, +2.29] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 3 (3) | 9.67 | -3.992 | -41.3% | [-6.80, +0.74] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 20 (13) | 15.50 | -0.949 | -6.1% | [-3.60, +1.73] | INSUFFICIENT |  |
| completions | new_team_first4 | 1 (1) | 20.00 | -2.825 | -14.1% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| completions | rookie | 1 (1) | 0.00 | +20.108 | — | — | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 23 (13) | 21.04 | -0.106 | -0.5% | [-2.06, +2.22] | INSUFFICIENT |  |
| passing_attempts | new_team_first4 | 1 (1) | 28.00 | +2.229 | +8.0% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_attempts | rookie | 1 (1) | 0.00 | +31.937 | — | — | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 23 (13) | 32.78 | -0.315 | -1.0% | [-2.79, +2.45] | INSUFFICIENT |  |
| passing_tds | new_team_first4 | 1 (1) | 0.00 | +1.190 | — | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_tds | rookie | 1 (1) | 0.00 | +1.195 | — | — | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 23 (13) | 1.61 | -0.179 | -11.1% | [-0.60, +0.19] | INSUFFICIENT |  |
| passing_yards | new_team_first4 | 1 (1) | 252.00 | -61.266 | -24.3% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_yards | rookie | 1 (1) | 0.00 | +197.596 | — | — | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 23 (13) | 232.22 | -8.404 | -3.6% | [-35.91, +16.34] | INSUFFICIENT |  |
| receiving_yards | new_team_first4 | 6 (6) | 3.33 | +14.308 | +429.2% | [+10.18, +18.46] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 53 (13) | 16.68 | +3.049 | +18.3% | [-1.30, +7.79] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 15 (8) | 39.33 | -8.432 | -21.4% | [-21.53, +4.57] | INSUFFICIENT | monitored (no study band) |
| receiving_yards | none_of_the_three | 82 (13) | 42.60 | +1.160 | +2.7% | [-4.03, +6.64] | OK |  |
| receptions | new_team_first4 | 6 (6) | 0.50 | +1.485 | +297.1% | [+1.00, +2.10] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 53 (13) | 1.53 | +0.379 | +24.8% | [+0.00, +0.66] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 15 (8) | 2.80 | -0.316 | -11.3% | [-1.25, +0.47] | INSUFFICIENT | monitored (no study band) |
| receptions | none_of_the_three | 82 (13) | 3.91 | -0.002 | -0.1% | [-0.50, +0.50] | OK |  |
| rushing_yards | new_team_first4 | 3 (3) | 16.33 | +17.767 | +108.8% | [+13.56, +20.67] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 18 (13) | 47.00 | -4.918 | -10.5% | [-23.92, +9.91] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 3 (3) | 45.33 | -22.625 | -49.9% | [-37.16, -1.74] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 20 (13) | 69.70 | -8.178 | -11.7% | [-23.39, +5.39] | INSUFFICIENT |  |
| targets | new_team_first4 | 6 (6) | 1.33 | +1.507 | +113.0% | [+0.11, +2.82] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 53 (13) | 2.36 | +0.539 | +22.9% | [+0.15, +0.91] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 15 (8) | 4.13 | -0.070 | -1.7% | [-1.15, +0.92] | INSUFFICIENT | monitored (no study band) |
| targets | none_of_the_three | 82 (13) | 5.71 | +0.118 | +2.1% | [-0.53, +0.74] | OK |  |

Pooled relative bias (family-n weighted): new_team_first4 +160.5% (n=33); backup +10.2% (n=256); rookie -13.1% (n=69); none_of_the_three -3.7% (n=462)

**DNP (void) rate by pre-game participation call**: CONFIRMED_OUT 100.0% (n=40); LIKELY_ACTIVE 1.8% (n=731); LIKELY_OUT 100.0% (n=10); UNCERTAIN 18.0% (n=61)

**Settled by gate status**: PASS n=700 MAE=8.414; REVIEW n=68 MAE=10.516

**Availability capture** (last run): mean coverage 1.0, participation calls {'LIKELY_ACTIVE': 168, 'UNCERTAIN': 30, 'CONFIRMED_OUT': 7}
