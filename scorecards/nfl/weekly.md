## NFL projection scorecard — last 28 days

Generated 2026-10-21T17:35:55Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 1736 across 13 games. Settled: 1521 (void/DNP 108, stat corrections 0).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 163 (13) | Brier 0.1660 | calib +0.020 | log loss 0.5083 | — | -0.0080 [-0.0219, +0.0068] (n=158) (Brier) |
| anytime_td (yes/no) | shadow-0.4.0 (incumbent) | 257 (13) | Brier 0.1396 | calib -0.037 | log loss 0.4540 | — |  |
| carries | pf-nfl (challenger) | 37 (13) | 4.072 | +0.344 | 2.858 | 84% | — |
| carries | shadow-0.4.0 (incumbent) | 29 (12) | 6.184 | -5.228 | — | — |  |
| completions | pf-nfl (challenger) | 23 (13) | 3.716 | -1.170 | 2.876 | 78% | — |
| completions | shadow-0.4.0 (incumbent) | 23 (12) | 3.846 | -0.765 | — | — |  |
| passing_attempts | pf-nfl (challenger) | 23 (13) | 6.608 | -3.305 | 4.664 | 87% | — |
| passing_attempts | shadow-0.4.0 (incumbent) | 23 (12) | 6.309 | -2.725 | — | — |  |
| passing_tds | pf-nfl (challenger) | 23 (13) | 0.891 | -0.084 | 0.615 | 87% | — |
| passing_tds | shadow-0.4.0 (incumbent) | 25 (13) | 0.845 | -0.118 | — | — |  |
| passing_yards | pf-nfl (challenger) | 23 (13) | 47.243 | -5.729 | 34.301 | 96% | — |
| passing_yards | shadow-0.4.0 (incumbent) | 25 (13) | 44.300 | +0.347 | — | — |  |
| receiving_yards | pf-nfl (challenger) | 151 (13) | 19.953 | -0.480 | 13.907 | 81% | — |
| receiving_yards | shadow-0.4.0 (incumbent) | 113 (13) | 22.231 | -12.471 | — | — |  |
| receptions | pf-nfl (challenger) | 151 (13) | 1.606 | -0.072 | 1.096 | 79% | — |
| receptions | shadow-0.4.0 (incumbent) | 100 (12) | 2.223 | -1.781 | — | — |  |
| rushing_yards | pf-nfl (challenger) | 37 (13) | 21.512 | +6.539 | 14.303 | 86% | — |
| rushing_yards | shadow-0.4.0 (incumbent) | 66 (13) | 17.607 | -5.586 | — | — |  |
| targets | pf-nfl (challenger) | 151 (13) | 2.101 | -0.319 | 1.468 | 77% | — |
| team_pass_attempts | pf-nfl (challenger) | 26 (13) | 6.343 | -3.178 | 4.528 | 77% | — |
| team_points | pf-nfl (challenger) | 26 (13) | 6.077 | +0.796 | 4.262 | 88% | — |
| team_rush_attempts | pf-nfl (challenger) | 26 (13) | 5.497 | +1.557 | 4.080 | 73% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **INSUFFICIENT** — 37 settled forecasts (< 100)
- completions: **INSUFFICIENT** — 23 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 23 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 23 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 23 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **INSUFFICIENT** — 37 settled forecasts (< 100)
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 26 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 26 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 26 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 5 (4) | 0.00 | +0.153 | — | [+0.14, +0.16] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 67 (13) | 0.16 | +0.020 | +12.0% | [-0.04, +0.08] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 19 (12) | 0.16 | +0.009 | +5.9% | [-0.14, +0.16] | INSUFFICIENT | monitored (no study band) |
| anytime_td | none_of_the_three | 88 (13) | 0.27 | +0.029 | +10.5% | [-0.06, +0.13] | OK |  |
| carries | backup | 19 (12) | 10.74 | -0.727 | -6.8% | [-2.57, +1.25] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 4 (4) | 6.00 | -1.530 | -25.5% | [-4.04, +0.17] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 18 (12) | 11.83 | +1.474 | +12.5% | [-0.88, +3.40] | INSUFFICIENT |  |
| completions | rookie | 1 (1) | 22.00 | -3.517 | -16.0% | — | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 22 (13) | 22.00 | -1.064 | -4.8% | [-3.16, +1.26] | INSUFFICIENT |  |
| passing_attempts | rookie | 1 (1) | 43.00 | -12.953 | -30.1% | — | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 22 (13) | 35.32 | -2.866 | -8.1% | [-6.09, +0.01] | INSUFFICIENT |  |
| passing_tds | rookie | 1 (1) | 1.00 | +0.113 | +11.3% | — | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 22 (13) | 1.59 | -0.093 | -5.8% | [-0.72, +0.41] | INSUFFICIENT |  |
| passing_yards | rookie | 1 (1) | 164.00 | +27.869 | +17.0% | — | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 22 (13) | 239.86 | -7.257 | -3.0% | [-33.41, +20.39] | INSUFFICIENT |  |
| receiving_yards | new_team_first4 | 5 (4) | 33.20 | -10.666 | -32.1% | [-21.40, +1.80] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 55 (13) | 22.73 | -1.095 | -4.8% | [-4.61, +3.31] | OK | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 15 (11) | 25.20 | +6.149 | +24.4% | [-6.45, +16.40] | INSUFFICIENT | monitored (no study band) |
| receiving_yards | none_of_the_three | 88 (13) | 41.99 | -0.145 | -0.3% | [-4.69, +4.86] | OK |  |
| receptions | new_team_first4 | 5 (4) | 3.40 | -1.256 | -36.9% | [-2.18, -0.07] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 55 (13) | 2.09 | -0.132 | -6.3% | [-0.56, +0.23] | OK | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 15 (11) | 2.60 | -0.082 | -3.1% | [-1.24, +0.99] | INSUFFICIENT | monitored (no study band) |
| receptions | none_of_the_three | 88 (13) | 3.65 | +0.045 | +1.2% | [-0.25, +0.35] | OK |  |
| rushing_yards | backup | 19 (12) | 39.21 | +3.613 | +9.2% | [-5.95, +13.92] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 4 (4) | 27.50 | -7.761 | -28.2% | [-19.49, +4.93] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 18 (12) | 47.56 | +9.628 | +20.2% | [-2.22, +19.68] | INSUFFICIENT |  |
| targets | new_team_first4 | 5 (4) | 4.20 | -1.012 | -24.1% | [-2.50, +0.26] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 55 (13) | 3.16 | -0.115 | -3.6% | [-0.70, +0.43] | OK | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 15 (11) | 4.47 | -0.401 | -9.0% | [-1.81, +1.02] | INSUFFICIENT | monitored (no study band) |
| targets | none_of_the_three | 88 (13) | 5.84 | -0.421 | -7.2% | [-1.08, +0.21] | OK |  |

Pooled relative bias (family-n weighted): backup +0.1% (n=270); rookie +0.8% (n=76); none_of_the_three +1.0% (n=476); new_team_first4 -31.1% (n=15)

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

**DNP (void) rate by pre-game participation call**: CONFIRMED_OUT 100.0% (n=56); LIKELY_ACTIVE 1.2% (n=689); UNCERTAIN 26.9% (n=52); UNVERIFIED 4.5% (n=66)

**Settled by gate status**: PASS n=672 MAE=7.835; REVIEW n=110 MAE=5.944
