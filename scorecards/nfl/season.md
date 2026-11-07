## NFL projection scorecard — season to date

Generated 2026-11-07T18:39:21Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 9928 across 56 games. Settled: 3470 (void/DNP 253, stat corrections 0).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 525 (42) | Brier 0.1767 | calib -0.018 | log loss 0.5283 | — | -0.0080 [-0.0219, +0.0068] (n=158) (Brier) |
| anytime_td (yes/no) | shadow-0.4.0 (incumbent) | 257 (13) | Brier 0.1396 | calib -0.037 | log loss 0.4540 | — |  |
| carries | pf-nfl (challenger) | 135 (42) | 4.573 | -0.323 | 3.206 | 80% | — |
| carries | shadow-0.4.0 (incumbent) | 29 (12) | 6.184 | -5.228 | — | — |  |
| completions | pf-nfl (challenger) | 79 (42) | 5.196 | +0.723 | 3.729 | 78% | — |
| completions | shadow-0.4.0 (incumbent) | 23 (12) | 3.846 | -0.765 | — | — |  |
| passing_attempts | pf-nfl (challenger) | 79 (42) | 7.136 | +0.916 | 5.073 | 86% | — |
| passing_attempts | shadow-0.4.0 (incumbent) | 23 (12) | 6.309 | -2.725 | — | — |  |
| passing_tds | pf-nfl (challenger) | 79 (42) | 0.893 | -0.014 | 0.591 | 82% | — |
| passing_tds | shadow-0.4.0 (incumbent) | 25 (13) | 0.845 | -0.118 | — | — |  |
| passing_yards | pf-nfl (challenger) | 79 (42) | 60.996 | +1.813 | 43.751 | 80% | — |
| passing_yards | shadow-0.4.0 (incumbent) | 25 (13) | 44.300 | +0.347 | — | — |  |
| receiving_yards | pf-nfl (challenger) | 482 (42) | 20.799 | +0.672 | 14.238 | 80% | — |
| receiving_yards | shadow-0.4.0 (incumbent) | 113 (13) | 22.231 | -12.471 | — | — |  |
| receptions | pf-nfl (challenger) | 482 (42) | 1.522 | +0.095 | 1.034 | 80% | — |
| receptions | shadow-0.4.0 (incumbent) | 100 (12) | 2.223 | -1.781 | — | — |  |
| rushing_yards | pf-nfl (challenger) | 135 (42) | 27.639 | -1.461 | 18.929 | 80% | — |
| rushing_yards | shadow-0.4.0 (incumbent) | 66 (13) | 17.607 | -5.586 | — | — |  |
| targets | pf-nfl (challenger) | 482 (42) | 1.914 | +0.118 | 1.323 | 81% | — |
| team_pass_attempts | pf-nfl (challenger) | 84 (42) | 6.568 | +0.857 | 4.606 | 81% | — |
| team_points | pf-nfl (challenger) | 84 (42) | 7.374 | +0.021 | 5.054 | 82% | — |
| team_rush_attempts | pf-nfl (challenger) | 84 (42) | 5.969 | -0.680 | 4.293 | 77% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **WATCH** — CRPS 116% of historical holdout
- completions: **INSUFFICIENT** — 79 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 79 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 79 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 79 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **WATCH** — CRPS 113% of historical holdout
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 84 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 84 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 84 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 18 (15) | 0.11 | +0.068 | +61.5% | [-0.10, +0.18] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 215 (42) | 0.18 | +0.002 | +1.0% | [-0.03, +0.04] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 64 (35) | 0.14 | +0.030 | +21.0% | [-0.05, +0.12] | WATCH | monitored (no study band) |
| anytime_td | none_of_the_three | 281 (42) | 0.34 | -0.039 | -11.4% | [-0.08, +0.01] | OK |  |
| carries | new_team_first4 | 7 (7) | 5.57 | +2.015 | +36.2% | [-0.34, +3.88] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 68 (41) | 10.01 | -0.403 | -4.0% | [-1.79, +0.90] | OK | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 11 (11) | 9.36 | -2.578 | -27.5% | [-6.39, +0.82] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 64 (40) | 14.11 | -0.433 | -3.1% | [-1.78, +0.93] | OK |  |
| completions | new_team_first4 | 1 (1) | 20.00 | -2.825 | -14.1% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| completions | rookie | 3 (3) | 10.67 | +7.958 | +74.6% | [-1.81, +20.11] | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 75 (42) | 20.41 | +0.481 | +2.4% | [-0.99, +2.24] | OK |  |
| passing_attempts | new_team_first4 | 1 (1) | 28.00 | +2.229 | +8.0% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_attempts | rookie | 3 (3) | 20.33 | +10.135 | +49.8% | [-9.09, +31.94] | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 75 (42) | 31.88 | +0.530 | +1.7% | [-1.37, +2.62] | OK |  |
| passing_tds | new_team_first4 | 1 (1) | 0.00 | +1.190 | — | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_tds | rookie | 3 (3) | 0.33 | +0.788 | +236.5% | [+0.26, +1.20] | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 75 (42) | 1.53 | -0.062 | -4.0% | [-0.34, +0.19] | OK |  |
| passing_yards | new_team_first4 | 1 (1) | 252.00 | -61.266 | -24.3% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_yards | rookie | 3 (3) | 74.67 | +115.948 | +155.3% | [+42.83, +197.60] | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 75 (42) | 230.20 | -1.911 | -0.8% | [-21.60, +16.65] | OK |  |
| receiving_yards | new_team_first4 | 16 (14) | 18.50 | +4.203 | +22.7% | [-5.18, +12.75] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 177 (42) | 18.49 | +2.579 | +13.9% | [-0.00, +5.69] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 54 (31) | 27.65 | +2.831 | +10.2% | [-3.81, +8.76] | WATCH | monitored (no study band) |
| receiving_yards | none_of_the_three | 277 (42) | 42.25 | -0.241 | -0.6% | [-4.20, +3.65] | OK |  |
| receptions | new_team_first4 | 16 (14) | 1.94 | +0.214 | +11.0% | [-0.71, +1.10] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 177 (42) | 1.71 | +0.239 | +14.0% | [+0.02, +0.48] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 54 (31) | 2.46 | +0.039 | +1.6% | [-0.51, +0.63] | OK | monitored (no study band) |
| receptions | none_of_the_three | 277 (42) | 3.69 | +0.063 | +1.7% | [-0.23, +0.34] | OK |  |
| rushing_yards | new_team_first4 | 7 (7) | 19.43 | +11.550 | +59.5% | [+3.27, +19.75] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 68 (41) | 42.69 | -2.046 | -4.8% | [-9.71, +5.10] | OK | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 11 (11) | 38.36 | -10.183 | -26.5% | [-24.77, +6.07] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 64 (40) | 59.70 | -1.963 | -3.3% | [-9.43, +5.33] | OK |  |
| targets | new_team_first4 | 16 (14) | 2.75 | +0.370 | +13.5% | [-0.61, +1.29] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 177 (42) | 2.61 | +0.376 | +14.4% | [+0.10, +0.72] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 54 (31) | 3.80 | +0.213 | +5.6% | [-0.47, +0.90] | OK | monitored (no study band) |
| targets | none_of_the_three | 277 (42) | 5.55 | -0.021 | -0.4% | [-0.39, +0.34] | OK |  |

Pooled relative bias (family-n weighted): new_team_first4 +30.1% (n=83); backup +8.1% (n=882); rookie +12.5% (n=260); none_of_the_three -2.2% (n=1540)

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

**DNP (void) rate by pre-game participation call**: CONFIRMED_ACTIVE 0.0% (n=64); CONFIRMED_OUT 100.0% (n=132); LIKELY_ACTIVE 2.0% (n=2282); LIKELY_OUT 71.4% (n=14); UNCERTAIN 16.0% (n=225); UNVERIFIED 4.5% (n=66)

**Settled by gate status**: PASS n=2268 MAE=8.408; REVIEW n=289 MAE=10.404

**Availability capture** (last run): mean coverage 1.0, participation calls {'LIKELY_ACTIVE': 182, 'CONFIRMED_OUT': 12, 'UNCERTAIN': 22, 'LIKELY_OUT': 2}
