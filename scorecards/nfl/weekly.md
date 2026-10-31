## NFL projection scorecard — last 28 days

Generated 2026-10-31T17:43:30Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 6541 across 41 games. Settled: 2515 (void/DNP 185, stat corrections 0).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 345 (28) | Brier 0.1759 | calib -0.010 | log loss 0.5268 | — | -0.0080 [-0.0219, +0.0068] (n=158) (Brier) |
| anytime_td (yes/no) | shadow-0.4.0 (incumbent) | 257 (13) | Brier 0.1396 | calib -0.037 | log loss 0.4540 | — |  |
| carries | pf-nfl (challenger) | 85 (28) | 4.539 | -0.051 | 3.133 | 79% | — |
| carries | shadow-0.4.0 (incumbent) | 29 (12) | 6.184 | -5.228 | — | — |  |
| completions | pf-nfl (challenger) | 52 (28) | 4.390 | -0.398 | 3.154 | 83% | — |
| completions | shadow-0.4.0 (incumbent) | 23 (12) | 3.846 | -0.765 | — | — |  |
| passing_attempts | pf-nfl (challenger) | 52 (28) | 6.554 | -0.899 | 4.617 | 90% | — |
| passing_attempts | shadow-0.4.0 (incumbent) | 23 (12) | 6.309 | -2.725 | — | — |  |
| passing_tds | pf-nfl (challenger) | 52 (28) | 0.835 | -0.060 | 0.566 | 87% | — |
| passing_tds | shadow-0.4.0 (incumbent) | 25 (13) | 0.845 | -0.118 | — | — |  |
| passing_yards | pf-nfl (challenger) | 52 (28) | 51.675 | -6.631 | 37.004 | 90% | — |
| passing_yards | shadow-0.4.0 (incumbent) | 25 (13) | 44.300 | +0.347 | — | — |  |
| receiving_yards | pf-nfl (challenger) | 321 (28) | 20.260 | -0.343 | 13.965 | 82% | — |
| receiving_yards | shadow-0.4.0 (incumbent) | 113 (13) | 22.231 | -12.471 | — | — |  |
| receptions | pf-nfl (challenger) | 321 (28) | 1.500 | -0.003 | 1.025 | 82% | — |
| receptions | shadow-0.4.0 (incumbent) | 100 (12) | 2.223 | -1.781 | — | — |  |
| rushing_yards | pf-nfl (challenger) | 85 (28) | 26.033 | +0.773 | 17.326 | 82% | — |
| rushing_yards | shadow-0.4.0 (incumbent) | 66 (13) | 17.607 | -5.586 | — | — |  |
| targets | pf-nfl (challenger) | 321 (28) | 1.912 | -0.037 | 1.327 | 82% | — |
| team_pass_attempts | pf-nfl (challenger) | 56 (28) | 6.261 | -0.508 | 4.347 | 84% | — |
| team_points | pf-nfl (challenger) | 56 (28) | 6.759 | +0.330 | 4.648 | 88% | — |
| team_rush_attempts | pf-nfl (challenger) | 56 (28) | 5.733 | +0.136 | 4.152 | 75% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **INSUFFICIENT** — 85 settled forecasts (< 100)
- completions: **INSUFFICIENT** — 52 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 52 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 52 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 52 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **INSUFFICIENT** — 85 settled forecasts (< 100)
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 56 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 56 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 56 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 13 (12) | 0.15 | +0.037 | +24.1% | [-0.15, +0.18] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 139 (28) | 0.18 | +0.002 | +1.0% | [-0.05, +0.05] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 40 (24) | 0.17 | -0.012 | -6.6% | [-0.13, +0.08] | OK | monitored (no study band) |
| anytime_td | none_of_the_three | 186 (28) | 0.33 | -0.019 | -5.9% | [-0.08, +0.05] | OK |  |
| carries | new_team_first4 | 4 (4) | 6.00 | +2.760 | +46.0% | [+1.31, +4.41] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 42 (27) | 10.14 | -0.292 | -2.9% | [-2.18, +1.35] | OK | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 7 (7) | 7.57 | -2.585 | -34.1% | [-5.14, -0.51] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 42 (27) | 13.69 | +0.068 | +0.5% | [-1.73, +1.66] | OK |  |
| completions | new_team_first4 | 1 (1) | 20.00 | -2.825 | -14.1% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| completions | rookie | 2 (2) | 11.00 | +8.295 | +75.4% | [-3.52, +20.11] | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 49 (28) | 21.69 | -0.703 | -3.2% | [-2.15, +0.85] | OK |  |
| passing_attempts | new_team_first4 | 1 (1) | 28.00 | +2.229 | +8.0% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_attempts | rookie | 2 (2) | 21.50 | +9.492 | +44.1% | [-12.95, +31.94] | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 49 (28) | 33.94 | -1.387 | -4.1% | [-3.36, +0.43] | OK |  |
| passing_tds | new_team_first4 | 1 (1) | 0.00 | +1.190 | — | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_tds | rookie | 2 (2) | 0.50 | +0.654 | +130.8% | [+0.11, +1.20] | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 49 (28) | 1.59 | -0.115 | -7.2% | [-0.47, +0.19] | OK |  |
| passing_yards | new_team_first4 | 1 (1) | 252.00 | -61.266 | -24.3% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_yards | rookie | 2 (2) | 82.00 | +112.732 | +137.5% | [+27.87, +197.60] | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 49 (28) | 239.53 | -10.389 | -4.3% | [-29.22, +6.52] | OK |  |
| receiving_yards | new_team_first4 | 13 (12) | 21.46 | +1.818 | +8.5% | [-8.48, +11.37] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 117 (28) | 19.56 | +1.009 | +5.2% | [-1.74, +4.11] | OK | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 33 (21) | 32.21 | -1.017 | -3.2% | [-10.48, +7.93] | OK | monitored (no study band) |
| receiving_yards | none_of_the_three | 184 (28) | 43.16 | -0.606 | -1.4% | [-4.23, +3.30] | OK |  |
| receptions | new_team_first4 | 13 (12) | 2.23 | +0.036 | +1.6% | [-1.11, +1.12] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 117 (28) | 1.81 | +0.125 | +6.9% | [-0.16, +0.39] | OK | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 33 (21) | 2.70 | -0.165 | -6.1% | [-0.96, +0.49] | OK | monitored (no study band) |
| receptions | none_of_the_three | 184 (28) | 3.82 | -0.028 | -0.7% | [-0.33, +0.31] | OK |  |
| rushing_yards | new_team_first4 | 4 (4) | 22.50 | +11.991 | +53.3% | [+1.16, +19.87] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 42 (27) | 39.83 | +1.173 | +2.9% | [-7.84, +9.51] | OK | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 7 (7) | 35.14 | -14.131 | -40.2% | [-26.00, -3.76] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 42 (27) | 58.48 | -0.063 | -0.1% | [-10.44, +8.26] | OK |  |
| targets | new_team_first4 | 13 (12) | 3.15 | +0.111 | +3.5% | [-1.00, +1.27] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 117 (28) | 2.74 | +0.217 | +7.9% | [-0.13, +0.59] | OK | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 33 (21) | 4.24 | -0.160 | -3.8% | [-0.97, +0.67] | OK | monitored (no study band) |
| targets | none_of_the_three | 184 (28) | 5.77 | -0.182 | -3.2% | [-0.63, +0.29] | OK |  |

Pooled relative bias (family-n weighted): new_team_first4 +13.6% (n=63); backup +4.3% (n=574); rookie -2.7% (n=161); none_of_the_three -2.9% (n=1018)

**Rung Brier at the incumbent's listed thresholds (lower is better)**

| Stat | rungs (games) | challenger | shadow-0.4.0 | diff (95% CI) | shadow-0.5.0 | challenger (same rungs) |
|---|---|---|---|---|---|---|
| anytime_td | 380 (13) | 0.0692 | 0.0727 | -0.0036 [-0.0093, +0.0025] | 0.0727 | 0.0692 |
| carries | 69 (12) | 0.2263 | 0.2948 | -0.0686 [-0.1651, +0.0259] | 0.2703 | 0.2263 |
| completions | 63 (12) | 0.1606 | 0.1673 | -0.0067 [-0.0197, +0.0029] | 0.1660 | 0.1606 |
| passing_attempts | 63 (12) | 0.2325 | 0.2110 | +0.0215 [+0.0008, +0.0390] | 0.2168 | 0.2325 |
| passing_tds | 96 (13) | 0.1474 | 0.1443 | +0.0031 [-0.0076, +0.0159] | 0.1443 | 0.1474 |
| passing_yards | 206 (13) | 0.1533 | 0.1422 | +0.0111 [-0.0019, +0.0224] | 0.1422 | 0.1533 |
| receiving_yards | 840 (13) | 0.1490 | 0.1806 | -0.0316 [-0.0493, -0.0146] | 0.1806 | 0.1490 |
| receptions | 663 (12) | 0.1436 | 0.2065 | -0.0629 [-0.0837, -0.0392] | 0.1746 | 0.1436 |
| rushing_yards | 344 (13) | 0.1501 | 0.1634 | -0.0132 [-0.0550, +0.0182] | 0.1634 | 0.1501 |

**DNP (void) rate by pre-game participation call**: CONFIRMED_ACTIVE 0.0% (n=64); CONFIRMED_OUT 100.0% (n=99); LIKELY_ACTIVE 1.4% (n=1488); LIKELY_OUT 100.0% (n=10); UNCERTAIN 21.4% (n=117); UNVERIFIED 4.5% (n=66)

**Settled by gate status**: PASS n=1504 MAE=8.127; REVIEW n=182 MAE=7.661

**Availability capture** (last run): mean coverage 1.0, participation calls {'LIKELY_ACTIVE': 166, 'UNCERTAIN': 31, 'CONFIRMED_OUT': 7}
