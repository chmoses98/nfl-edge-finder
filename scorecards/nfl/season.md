## NFL projection scorecard — season to date

Generated 2026-10-28T20:51:55Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 4426 across 27 games. Settled: 2441 (void/DNP 179, stat corrections 0).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 332 (27) | Brier 0.1750 | calib -0.006 | log loss 0.5252 | — | -0.0080 [-0.0219, +0.0068] (n=158) (Brier) |
| anytime_td (yes/no) | shadow-0.4.0 (incumbent) | 257 (13) | Brier 0.1396 | calib -0.037 | log loss 0.4540 | — |  |
| carries | pf-nfl (challenger) | 81 (27) | 4.474 | +0.005 | 3.115 | 78% | — |
| carries | shadow-0.4.0 (incumbent) | 29 (12) | 6.184 | -5.228 | — | — |  |
| completions | pf-nfl (challenger) | 50 (27) | 4.361 | -0.209 | 3.139 | 84% | — |
| completions | shadow-0.4.0 (incumbent) | 23 (12) | 3.846 | -0.765 | — | — |  |
| passing_attempts | pf-nfl (challenger) | 50 (27) | 6.504 | -0.623 | 4.604 | 90% | — |
| passing_attempts | shadow-0.4.0 (incumbent) | 23 (12) | 6.309 | -2.725 | — | — |  |
| passing_tds | pf-nfl (challenger) | 50 (27) | 0.835 | -0.045 | 0.568 | 86% | — |
| passing_tds | shadow-0.4.0 (incumbent) | 25 (13) | 0.845 | -0.118 | — | — |  |
| passing_yards | pf-nfl (challenger) | 50 (27) | 52.777 | -5.932 | 37.559 | 90% | — |
| passing_yards | shadow-0.4.0 (incumbent) | 25 (13) | 44.300 | +0.347 | — | — |  |
| receiving_yards | pf-nfl (challenger) | 308 (27) | 20.546 | -0.247 | 14.131 | 81% | — |
| receiving_yards | shadow-0.4.0 (incumbent) | 113 (13) | 22.231 | -12.471 | — | — |  |
| receptions | pf-nfl (challenger) | 308 (27) | 1.479 | +0.035 | 1.011 | 82% | — |
| receptions | shadow-0.4.0 (incumbent) | 100 (12) | 2.223 | -1.781 | — | — |  |
| rushing_yards | pf-nfl (challenger) | 81 (27) | 26.357 | +0.340 | 17.645 | 81% | — |
| rushing_yards | shadow-0.4.0 (incumbent) | 66 (13) | 17.607 | -5.586 | — | — |  |
| targets | pf-nfl (challenger) | 308 (27) | 1.897 | +0.004 | 1.317 | 81% | — |
| team_pass_attempts | pf-nfl (challenger) | 54 (27) | 6.254 | -0.288 | 4.357 | 83% | — |
| team_points | pf-nfl (challenger) | 54 (27) | 6.920 | +0.329 | 4.729 | 87% | — |
| team_rush_attempts | pf-nfl (challenger) | 54 (27) | 5.874 | +0.069 | 4.240 | 74% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **INSUFFICIENT** — 81 settled forecasts (< 100)
- completions: **INSUFFICIENT** — 50 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 50 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 50 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 50 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **INSUFFICIENT** — 81 settled forecasts (< 100)
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 54 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 54 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 54 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 12 (11) | 0.17 | +0.029 | +17.3% | [-0.19, +0.19] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 134 (27) | 0.19 | -0.004 | -2.3% | [-0.05, +0.05] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 40 (24) | 0.17 | -0.012 | -6.6% | [-0.13, +0.08] | OK | monitored (no study band) |
| anytime_td | none_of_the_three | 178 (27) | 0.31 | -0.008 | -2.4% | [-0.07, +0.05] | OK |  |
| carries | new_team_first4 | 3 (3) | 7.67 | +2.864 | +37.4% | [+0.67, +5.06] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 40 (26) | 10.55 | -0.540 | -5.1% | [-2.52, +1.20] | OK | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 7 (7) | 7.57 | -2.585 | -34.1% | [-5.14, -0.51] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 40 (26) | 13.30 | +0.424 | +3.2% | [-1.36, +1.97] | OK |  |
| completions | new_team_first4 | 1 (1) | 20.00 | -2.825 | -14.1% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| completions | rookie | 2 (2) | 11.00 | +8.295 | +75.4% | [-3.52, +20.11] | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 47 (27) | 21.49 | -0.516 | -2.4% | [-1.91, +1.05] | OK |  |
| passing_attempts | new_team_first4 | 1 (1) | 28.00 | +2.229 | +8.0% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_attempts | rookie | 2 (2) | 21.50 | +9.492 | +44.1% | [-12.95, +31.94] | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 47 (27) | 33.64 | -1.114 | -3.3% | [-2.96, +0.79] | OK |  |
| passing_tds | new_team_first4 | 1 (1) | 0.00 | +1.190 | — | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_tds | rookie | 2 (2) | 0.50 | +0.654 | +130.8% | [+0.11, +1.20] | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 47 (27) | 1.57 | -0.101 | -6.4% | [-0.43, +0.21] | OK |  |
| passing_yards | new_team_first4 | 1 (1) | 252.00 | -61.266 | -24.3% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_yards | rookie | 2 (2) | 82.00 | +112.732 | +137.5% | [+27.87, +197.60] | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 47 (27) | 239.15 | -9.805 | -4.1% | [-27.39, +8.35] | OK |  |
| receiving_yards | new_team_first4 | 12 (11) | 23.25 | +1.184 | +5.1% | [-9.15, +11.36] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 112 (27) | 19.96 | +0.848 | +4.2% | [-2.19, +4.08] | OK | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 33 (21) | 32.21 | -1.017 | -3.2% | [-10.48, +7.93] | OK | monitored (no study band) |
| receiving_yards | none_of_the_three | 176 (27) | 42.84 | -0.309 | -0.7% | [-4.11, +3.80] | OK |  |
| receptions | new_team_first4 | 12 (11) | 2.42 | -0.092 | -3.8% | [-1.26, +1.04] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 112 (27) | 1.84 | +0.104 | +5.7% | [-0.18, +0.39] | OK | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 33 (21) | 2.70 | -0.165 | -6.1% | [-0.96, +0.49] | OK | monitored (no study band) |
| receptions | none_of_the_three | 176 (27) | 3.74 | +0.055 | +1.5% | [-0.17, +0.34] | OK |  |
| rushing_yards | new_team_first4 | 3 (3) | 29.33 | +11.466 | +39.1% | [-1.47, +20.67] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 40 (26) | 41.60 | +0.208 | +0.5% | [-10.33, +8.33] | OK | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 7 (7) | 35.14 | -14.131 | -40.2% | [-26.00, -3.76] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 40 (26) | 58.40 | +0.004 | +0.0% | [-9.10, +8.90] | OK |  |
| targets | new_team_first4 | 12 (11) | 3.42 | -0.043 | -1.2% | [-1.18, +1.28] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 112 (27) | 2.79 | +0.184 | +6.6% | [-0.15, +0.53] | OK | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 33 (21) | 4.24 | -0.160 | -3.8% | [-0.97, +0.67] | OK | monitored (no study band) |
| targets | none_of_the_three | 176 (27) | 5.69 | -0.087 | -1.5% | [-0.56, +0.39] | OK |  |

Pooled relative bias (family-n weighted): new_team_first4 +7.1% (n=57); backup +2.5% (n=550); rookie -2.7% (n=161); none_of_the_three -1.2% (n=974)

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

**DNP (void) rate by pre-game participation call**: CONFIRMED_ACTIVE 0.0% (n=64); CONFIRMED_OUT 100.0% (n=99); LIKELY_ACTIVE 1.5% (n=1424); LIKELY_OUT 100.0% (n=4); UNCERTAIN 22.1% (n=113); UNVERIFIED 4.5% (n=66)

**Settled by gate status**: PASS n=1440 MAE=8.226; REVIEW n=178 MAE=7.638
