## NFL projection scorecard — last 28 days

Generated 2026-11-12T21:08:16Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 12013 across 70 games. Settled: 4378 (void/DNP 349, stat corrections 2).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 694 (56) | Brier 0.1758 | calib -0.011 | log loss 0.5279 | — | -0.0080 [-0.0219, +0.0068] (n=158) (Brier) |
| anytime_td (yes/no) | shadow-0.4.0 (incumbent) | 257 (13) | Brier 0.1396 | calib -0.037 | log loss 0.4540 | — |  |
| carries | pf-nfl (challenger) | 183 (56) | 4.427 | -0.216 | 3.151 | 79% | — |
| carries | shadow-0.4.0 (incumbent) | 29 (12) | 6.184 | -5.228 | — | — |  |
| completions | pf-nfl (challenger) | 104 (56) | 4.561 | +0.641 | 3.332 | 84% | — |
| completions | shadow-0.4.0 (incumbent) | 23 (12) | 3.846 | -0.765 | — | — |  |
| passing_attempts | pf-nfl (challenger) | 104 (56) | 6.456 | +0.855 | 4.614 | 88% | — |
| passing_attempts | shadow-0.4.0 (incumbent) | 23 (12) | 6.309 | -2.725 | — | — |  |
| passing_tds | pf-nfl (challenger) | 104 (56) | 0.893 | -0.006 | 0.598 | 81% | — |
| passing_tds | shadow-0.4.0 (incumbent) | 25 (13) | 0.845 | -0.118 | — | — |  |
| passing_yards | pf-nfl (challenger) | 104 (56) | 60.030 | -0.844 | 42.508 | 82% | — |
| passing_yards | shadow-0.4.0 (incumbent) | 25 (13) | 44.300 | +0.347 | — | — |  |
| receiving_yards | pf-nfl (challenger) | 635 (56) | 20.523 | +0.344 | 14.152 | 80% | — |
| receiving_yards | shadow-0.4.0 (incumbent) | 113 (13) | 22.231 | -12.471 | — | — |  |
| receptions | pf-nfl (challenger) | 635 (56) | 1.475 | +0.089 | 1.013 | 81% | — |
| receptions | shadow-0.4.0 (incumbent) | 100 (12) | 2.223 | -1.781 | — | — |  |
| rushing_yards | pf-nfl (challenger) | 183 (56) | 25.534 | -0.235 | 17.809 | 81% | — |
| rushing_yards | shadow-0.4.0 (incumbent) | 66 (13) | 17.607 | -5.586 | — | — |  |
| targets | pf-nfl (challenger) | 635 (56) | 1.871 | +0.130 | 1.297 | 82% | — |
| team_pass_attempts | pf-nfl (challenger) | 112 (56) | 5.913 | +0.909 | 4.189 | 85% | — |
| team_points | pf-nfl (challenger) | 112 (56) | 7.127 | +0.178 | 4.986 | 83% | — |
| team_rush_attempts | pf-nfl (challenger) | 112 (56) | 5.783 | -0.505 | 4.170 | 79% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **WATCH** — CRPS 114% of historical holdout
- completions: **OK** — within expectations
- passing_attempts: **OK** — within expectations
- passing_tds: **OK** — within expectations
- passing_yards: **OK** — within expectations
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **OK** — within expectations
- targets: **OK** — within expectations
- team_pass_attempts: **OK** — within expectations
- team_points: **OK** — within expectations
- team_rush_attempts: **OK** — within expectations

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 21 (17) | 0.10 | +0.083 | +87.4% | [-0.08, +0.17] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 284 (56) | 0.18 | +0.004 | +2.3% | [-0.03, +0.04] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 86 (47) | 0.15 | +0.029 | +19.1% | [-0.04, +0.09] | WATCH | monitored (no study band) |
| anytime_td | none_of_the_three | 373 (56) | 0.33 | -0.026 | -7.8% | [-0.07, +0.02] | OK |  |
| carries | new_team_first4 | 8 (8) | 4.88 | +2.499 | +51.3% | [+0.47, +4.33] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 90 (54) | 10.07 | -0.706 | -7.0% | [-1.83, +0.33] | OK | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 16 (15) | 9.50 | -1.271 | -13.4% | [-4.33, +1.26] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 88 (54) | 13.58 | +0.111 | +0.8% | [-0.95, +1.19] | OK |  |
| completions | new_team_first4 | 3 (3) | 17.67 | +0.722 | +4.1% | [-2.37, +4.93] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| completions | rookie | 3 (3) | 10.67 | +7.958 | +74.6% | [-1.81, +20.11] | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 98 (54) | 20.49 | +0.414 | +2.0% | [-0.89, +1.86] | OK |  |
| passing_attempts | new_team_first4 | 3 (3) | 25.67 | +5.285 | +20.6% | [+2.34, +10.67] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_attempts | rookie | 3 (3) | 20.33 | +10.135 | +49.8% | [-9.09, +31.94] | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 98 (54) | 31.98 | +0.436 | +1.4% | [-1.06, +2.24] | OK |  |
| passing_tds | new_team_first4 | 3 (3) | 0.00 | +1.142 | — | [+1.05, +1.19] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_tds | rookie | 3 (3) | 0.33 | +0.788 | +236.5% | [+0.26, +1.20] | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 98 (54) | 1.55 | -0.065 | -4.2% | [-0.32, +0.19] | OK |  |
| passing_yards | new_team_first4 | 3 (3) | 181.67 | +12.715 | +7.0% | [-46.84, +69.55] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_yards | rookie | 3 (3) | 74.67 | +115.948 | +155.3% | [+42.83, +197.60] | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 98 (54) | 234.14 | -4.834 | -2.1% | [-20.55, +12.57] | OK |  |
| receiving_yards | new_team_first4 | 18 (16) | 18.44 | +4.628 | +25.1% | [-4.07, +11.77] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 234 (56) | 19.41 | +1.805 | +9.3% | [-1.14, +4.55] | OK | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 73 (41) | 29.63 | +1.171 | +4.0% | [-4.01, +6.84] | OK | monitored (no study band) |
| receiving_yards | none_of_the_three | 365 (56) | 42.48 | +0.032 | +0.1% | [-3.52, +3.10] | OK |  |
| receptions | new_team_first4 | 18 (16) | 1.89 | +0.225 | +11.9% | [-0.62, +1.02] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 234 (56) | 1.74 | +0.207 | +11.9% | [-0.01, +0.42] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 73 (41) | 2.55 | -0.011 | -0.4% | [-0.46, +0.41] | OK | monitored (no study band) |
| receptions | none_of_the_three | 365 (56) | 3.71 | +0.086 | +2.3% | [-0.11, +0.33] | OK |  |
| rushing_yards | new_team_first4 | 8 (8) | 17.00 | +13.430 | +79.0% | [+6.30, +21.06] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 90 (54) | 42.66 | -2.946 | -6.9% | [-8.80, +2.98] | OK | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 16 (15) | 38.44 | -4.244 | -11.0% | [-17.98, +8.31] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 88 (54) | 56.65 | +1.320 | +2.3% | [-5.05, +7.29] | OK |  |
| targets | new_team_first4 | 18 (16) | 2.67 | +0.432 | +16.2% | [-0.47, +1.31] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 234 (56) | 2.71 | +0.283 | +10.5% | [-0.01, +0.57] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 73 (41) | 3.88 | +0.185 | +4.8% | [-0.42, +0.70] | OK | monitored (no study band) |
| targets | none_of_the_three | 365 (56) | 5.52 | +0.071 | +1.3% | [-0.23, +0.41] | OK |  |

Pooled relative bias (family-n weighted): new_team_first4 +39.3% (n=100); backup +5.8% (n=1166); rookie +9.8% (n=349); none_of_the_three -0.8% (n=2036)

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

**DNP (void) rate by pre-game participation call**: CONFIRMED_ACTIVE 0.0% (n=64); CONFIRMED_OUT 100.0% (n=187); LIKELY_ACTIVE 2.4% (n=3086); LIKELY_OUT 76.5% (n=17); UNCERTAIN 16.3% (n=283); UNVERIFIED 4.5% (n=66)

**Settled by gate status**: PASS n=3039 MAE=8.243; REVIEW n=342 MAE=9.684

**Availability capture** (last run): mean coverage 1.0, participation calls {'LIKELY_ACTIVE': 215, 'CONFIRMED_OUT': 1, 'LIKELY_OUT': 2}
