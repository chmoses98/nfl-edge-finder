## NFL projection scorecard — season to date

Generated 2026-11-03T21:34:47Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 7577 across 41 games. Settled: 3400 (void/DNP 253, stat corrections 0).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 511 (41) | Brier 0.1768 | calib -0.017 | log loss 0.5286 | — | -0.0080 [-0.0219, +0.0068] (n=158) (Brier) |
| anytime_td (yes/no) | shadow-0.4.0 (incumbent) | 257 (13) | Brier 0.1396 | calib -0.037 | log loss 0.4540 | — |  |
| carries | pf-nfl (challenger) | 132 (41) | 4.622 | -0.347 | 3.232 | 80% | — |
| carries | shadow-0.4.0 (incumbent) | 29 (12) | 6.184 | -5.228 | — | — |  |
| completions | pf-nfl (challenger) | 77 (41) | 5.187 | +0.598 | 3.735 | 78% | — |
| completions | shadow-0.4.0 (incumbent) | 23 (12) | 3.846 | -0.765 | — | — |  |
| passing_attempts | pf-nfl (challenger) | 77 (41) | 7.107 | +0.724 | 5.072 | 87% | — |
| passing_attempts | shadow-0.4.0 (incumbent) | 23 (12) | 6.309 | -2.725 | — | — |  |
| passing_tds | pf-nfl (challenger) | 77 (41) | 0.893 | -0.037 | 0.595 | 82% | — |
| passing_tds | shadow-0.4.0 (incumbent) | 25 (13) | 0.845 | -0.118 | — | — |  |
| passing_yards | pf-nfl (challenger) | 77 (41) | 60.887 | +0.374 | 43.573 | 81% | — |
| passing_yards | shadow-0.4.0 (incumbent) | 25 (13) | 44.300 | +0.347 | — | — |  |
| receiving_yards | pf-nfl (challenger) | 470 (41) | 20.795 | +0.271 | 14.297 | 80% | — |
| receiving_yards | shadow-0.4.0 (incumbent) | 113 (13) | 22.231 | -12.471 | — | — |  |
| receptions | pf-nfl (challenger) | 470 (41) | 1.525 | +0.067 | 1.041 | 80% | — |
| receptions | shadow-0.4.0 (incumbent) | 100 (12) | 2.223 | -1.781 | — | — |  |
| rushing_yards | pf-nfl (challenger) | 132 (41) | 27.750 | -2.011 | 19.087 | 80% | — |
| rushing_yards | shadow-0.4.0 (incumbent) | 66 (13) | 17.607 | -5.586 | — | — |  |
| targets | pf-nfl (challenger) | 470 (41) | 1.910 | +0.077 | 1.325 | 81% | — |
| team_pass_attempts | pf-nfl (challenger) | 82 (41) | 6.516 | +0.665 | 4.588 | 82% | — |
| team_points | pf-nfl (challenger) | 82 (41) | 7.398 | +0.064 | 5.083 | 82% | — |
| team_rush_attempts | pf-nfl (challenger) | 82 (41) | 6.016 | -0.598 | 4.324 | 77% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **WATCH** — CRPS 117% of historical holdout
- completions: **INSUFFICIENT** — 77 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 77 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 77 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 77 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **WATCH** — CRPS 114% of historical holdout
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 82 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 82 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 82 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 18 (15) | 0.11 | +0.068 | +61.5% | [-0.10, +0.18] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 209 (41) | 0.18 | +0.001 | +0.3% | [-0.04, +0.03] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 61 (34) | 0.15 | +0.026 | +17.7% | [-0.07, +0.11] | WATCH | monitored (no study band) |
| anytime_td | none_of_the_three | 273 (41) | 0.34 | -0.036 | -10.5% | [-0.09, +0.01] | OK |  |
| carries | new_team_first4 | 7 (7) | 5.57 | +2.015 | +36.2% | [-0.34, +3.88] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 66 (40) | 9.91 | -0.438 | -4.4% | [-1.74, +0.81] | OK | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 11 (11) | 9.36 | -2.578 | -27.5% | [-6.39, +0.82] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 63 (39) | 14.14 | -0.451 | -3.2% | [-1.86, +0.83] | OK |  |
| completions | new_team_first4 | 1 (1) | 20.00 | -2.825 | -14.1% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| completions | rookie | 2 (2) | 11.00 | +8.295 | +75.4% | [-3.52, +20.11] | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 74 (41) | 20.47 | +0.437 | +2.1% | [-1.03, +2.09] | OK |  |
| passing_attempts | new_team_first4 | 1 (1) | 28.00 | +2.229 | +8.0% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_attempts | rookie | 2 (2) | 21.50 | +9.492 | +44.1% | [-12.95, +31.94] | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 74 (41) | 31.96 | +0.467 | +1.5% | [-1.39, +2.54] | OK |  |
| passing_tds | new_team_first4 | 1 (1) | 0.00 | +1.190 | — | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_tds | rookie | 2 (2) | 0.50 | +0.654 | +130.8% | [+0.11, +1.20] | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 74 (41) | 1.54 | -0.072 | -4.7% | [-0.40, +0.20] | OK |  |
| passing_yards | new_team_first4 | 1 (1) | 252.00 | -61.266 | -24.3% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_yards | rookie | 2 (2) | 82.00 | +112.732 | +137.5% | [+27.87, +197.60] | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 74 (41) | 230.04 | -1.829 | -0.8% | [-20.08, +19.23] | OK |  |
| receiving_yards | new_team_first4 | 16 (14) | 18.50 | +4.203 | +22.7% | [-5.18, +12.75] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 173 (41) | 18.88 | +2.161 | +11.4% | [-0.23, +4.96] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 51 (30) | 29.16 | +2.002 | +6.9% | [-4.79, +8.24] | OK | monitored (no study band) |
| receiving_yards | none_of_the_three | 269 (41) | 42.81 | -0.673 | -1.6% | [-4.65, +2.96] | OK |  |
| receptions | new_team_first4 | 16 (14) | 1.94 | +0.214 | +11.0% | [-0.71, +1.10] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 173 (41) | 1.74 | +0.209 | +12.0% | [-0.04, +0.44] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 51 (30) | 2.59 | -0.039 | -1.5% | [-0.62, +0.56] | OK | monitored (no study band) |
| receptions | none_of_the_three | 269 (41) | 3.74 | +0.035 | +0.9% | [-0.27, +0.34] | OK |  |
| rushing_yards | new_team_first4 | 7 (7) | 19.43 | +11.550 | +59.5% | [+3.27, +19.75] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 66 (40) | 42.83 | -2.869 | -6.7% | [-10.46, +4.52] | OK | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 11 (11) | 38.36 | -10.183 | -26.5% | [-24.77, +6.07] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 63 (39) | 60.19 | -2.279 | -3.8% | [-9.90, +5.99] | OK |  |
| targets | new_team_first4 | 16 (14) | 2.75 | +0.370 | +13.5% | [-0.61, +1.29] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 173 (41) | 2.66 | +0.323 | +12.1% | [+0.01, +0.64] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 51 (30) | 4.00 | +0.081 | +2.0% | [-0.58, +0.73] | OK | monitored (no study band) |
| targets | none_of_the_three | 269 (41) | 5.61 | -0.060 | -1.1% | [-0.45, +0.28] | OK |  |

Pooled relative bias (family-n weighted): new_team_first4 +30.1% (n=83); backup +6.4% (n=860); rookie +6.7% (n=244); none_of_the_three -2.6% (n=1502)

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

**DNP (void) rate by pre-game participation call**: CONFIRMED_ACTIVE 0.0% (n=64); CONFIRMED_OUT 100.0% (n=132); LIKELY_ACTIVE 2.0% (n=2228); LIKELY_OUT 100.0% (n=10); UNCERTAIN 16.4% (n=219); UNVERIFIED 4.5% (n=66)

**Settled by gate status**: PASS n=2214 MAE=8.453; REVIEW n=279 MAE=10.136
