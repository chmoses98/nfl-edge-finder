## NFL projection scorecard — last 28 days

Generated 2026-10-25T13:12:30Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 4321 across 27 games. Settled: 1599 (void/DNP 111, stat corrections 0).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 178 (14) | Brier 0.1683 | calib +0.012 | log loss 0.5135 | — | -0.0080 [-0.0219, +0.0068] (n=158) (Brier) |
| anytime_td (yes/no) | shadow-0.4.0 (incumbent) | 257 (13) | Brier 0.1396 | calib -0.037 | log loss 0.4540 | — |  |
| carries | pf-nfl (challenger) | 42 (14) | 4.040 | +0.462 | 2.789 | 86% | — |
| carries | shadow-0.4.0 (incumbent) | 29 (12) | 6.184 | -5.228 | — | — |  |
| completions | pf-nfl (challenger) | 25 (14) | 3.554 | -1.212 | 2.784 | 80% | — |
| completions | shadow-0.4.0 (incumbent) | 23 (12) | 3.846 | -0.765 | — | — |  |
| passing_attempts | pf-nfl (challenger) | 25 (14) | 6.145 | -2.975 | 4.451 | 88% | — |
| passing_attempts | shadow-0.4.0 (incumbent) | 23 (12) | 6.309 | -2.725 | — | — |  |
| passing_tds | pf-nfl (challenger) | 25 (14) | 0.843 | -0.100 | 0.590 | 88% | — |
| passing_tds | shadow-0.4.0 (incumbent) | 25 (13) | 0.845 | -0.118 | — | — |  |
| passing_yards | pf-nfl (challenger) | 25 (14) | 48.625 | -10.433 | 34.688 | 96% | — |
| passing_yards | shadow-0.4.0 (incumbent) | 25 (13) | 44.300 | +0.347 | — | — |  |
| receiving_yards | pf-nfl (challenger) | 164 (14) | 20.570 | -1.342 | 14.352 | 80% | — |
| receiving_yards | shadow-0.4.0 (incumbent) | 113 (13) | 22.231 | -12.471 | — | — |  |
| receptions | pf-nfl (challenger) | 164 (14) | 1.604 | -0.082 | 1.095 | 79% | — |
| receptions | shadow-0.4.0 (incumbent) | 100 (12) | 2.223 | -1.781 | — | — |  |
| rushing_yards | pf-nfl (challenger) | 42 (14) | 20.875 | +6.934 | 13.701 | 88% | — |
| rushing_yards | shadow-0.4.0 (incumbent) | 66 (13) | 17.607 | -5.586 | — | — |  |
| targets | pf-nfl (challenger) | 164 (14) | 2.079 | -0.296 | 1.446 | 78% | — |
| team_pass_attempts | pf-nfl (challenger) | 28 (14) | 6.027 | -2.815 | 4.344 | 79% | — |
| team_points | pf-nfl (challenger) | 28 (14) | 5.761 | +0.627 | 4.130 | 89% | — |
| team_rush_attempts | pf-nfl (challenger) | 28 (14) | 5.504 | +1.751 | 4.072 | 71% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **INSUFFICIENT** — 42 settled forecasts (< 100)
- completions: **INSUFFICIENT** — 25 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 25 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 25 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 25 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **INSUFFICIENT** — 42 settled forecasts (< 100)
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 28 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 28 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 28 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 6 (5) | 0.00 | +0.183 | — | [+0.14, +0.26] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 74 (14) | 0.16 | +0.022 | +13.4% | [-0.04, +0.08] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 20 (13) | 0.20 | -0.033 | -16.7% | [-0.21, +0.11] | INSUFFICIENT | monitored (no study band) |
| anytime_td | none_of_the_three | 95 (14) | 0.29 | +0.008 | +2.6% | [-0.08, +0.11] | OK |  |
| carries | backup | 22 (13) | 9.68 | -0.244 | -2.5% | [-2.02, +1.86] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 4 (4) | 6.00 | -1.530 | -25.5% | [-4.04, +0.17] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 20 (13) | 12.05 | +1.238 | +10.3% | [-0.78, +3.10] | INSUFFICIENT |  |
| completions | rookie | 1 (1) | 22.00 | -3.517 | -16.0% | — | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 24 (14) | 22.08 | -1.115 | -5.1% | [-3.04, +1.03] | INSUFFICIENT |  |
| passing_attempts | rookie | 1 (1) | 43.00 | -12.953 | -30.1% | — | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 24 (14) | 35.04 | -2.559 | -7.3% | [-5.58, -0.05] | INSUFFICIENT |  |
| passing_tds | rookie | 1 (1) | 1.00 | +0.113 | +11.3% | — | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 24 (14) | 1.62 | -0.109 | -6.7% | [-0.65, +0.37] | INSUFFICIENT |  |
| passing_yards | rookie | 1 (1) | 164.00 | +27.869 | +17.0% | — | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 24 (14) | 246.08 | -12.029 | -4.9% | [-37.55, +14.60] | INSUFFICIENT |  |
| receiving_yards | new_team_first4 | 6 (5) | 35.67 | -5.208 | -14.6% | [-17.46, +10.23] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 60 (14) | 22.03 | -0.543 | -2.5% | [-4.38, +4.00] | OK | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 16 (12) | 27.12 | +3.633 | +13.4% | [-7.43, +13.87] | INSUFFICIENT | monitored (no study band) |
| receiving_yards | none_of_the_three | 95 (14) | 43.81 | -2.210 | -5.0% | [-7.81, +3.80] | OK |  |
| receptions | new_team_first4 | 6 (5) | 3.33 | -0.751 | -22.5% | [-1.92, +0.69] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 60 (14) | 1.98 | -0.024 | -1.2% | [-0.46, +0.32] | OK | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 16 (12) | 2.62 | -0.123 | -4.7% | [-1.34, +0.85] | INSUFFICIENT | monitored (no study band) |
| receptions | none_of_the_three | 95 (14) | 3.74 | -0.065 | -1.8% | [-0.43, +0.25] | OK |  |
| rushing_yards | backup | 22 (13) | 35.45 | +5.195 | +14.7% | [-3.71, +14.47] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 4 (4) | 27.50 | -7.761 | -28.2% | [-19.49, +4.93] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 20 (13) | 47.80 | +8.846 | +18.5% | [-1.70, +18.04] | INSUFFICIENT |  |
| targets | new_team_first4 | 6 (5) | 4.50 | -0.655 | -14.6% | [-2.02, +0.68] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 60 (14) | 3.03 | -0.011 | -0.4% | [-0.53, +0.54] | OK | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 16 (12) | 4.44 | -0.441 | -9.9% | [-1.81, +0.81] | INSUFFICIENT | monitored (no study band) |
| targets | none_of_the_three | 95 (14) | 5.84 | -0.466 | -8.0% | [-1.05, +0.14] | OK |  |

Pooled relative bias (family-n weighted): backup +3.4% (n=298); rookie -7.3% (n=80); none_of_the_three -2.2% (n=516); new_team_first4 -17.2% (n=18)

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

**DNP (void) rate by pre-game participation call**: CONFIRMED_OUT 100.0% (n=59); LIKELY_ACTIVE 1.1% (n=757); UNCERTAIN 25.0% (n=56); UNVERIFIED 4.5% (n=66)

**Settled by gate status**: PASS n=740 MAE=7.952; REVIEW n=114 MAE=5.958

**Availability capture** (last run): mean coverage 1.0, participation calls {'LIKELY_ACTIVE': 166, 'UNCERTAIN': 5, 'CONFIRMED_OUT': 10, 'LIKELY_OUT': 1, 'CONFIRMED_ACTIVE': 14}
