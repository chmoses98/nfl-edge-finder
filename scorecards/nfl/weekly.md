## NFL projection scorecard — last 28 days

Generated 2026-11-14T19:12:37Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 13156 across 70 games. Settled: 4446 (void/DNP 349, stat corrections 2).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 707 (57) | Brier 0.1760 | calib -0.011 | log loss 0.5282 | — | -0.0080 [-0.0219, +0.0068] (n=158) (Brier) |
| anytime_td (yes/no) | shadow-0.4.0 (incumbent) | 257 (13) | Brier 0.1396 | calib -0.037 | log loss 0.4540 | — |  |
| carries | pf-nfl (challenger) | 187 (57) | 4.449 | -0.155 | 3.180 | 79% | — |
| carries | shadow-0.4.0 (incumbent) | 29 (12) | 6.184 | -5.228 | — | — |  |
| completions | pf-nfl (challenger) | 106 (57) | 4.577 | +0.526 | 3.330 | 84% | — |
| completions | shadow-0.4.0 (incumbent) | 23 (12) | 3.846 | -0.765 | — | — |  |
| passing_attempts | pf-nfl (challenger) | 106 (57) | 6.440 | +0.733 | 4.596 | 89% | — |
| passing_attempts | shadow-0.4.0 (incumbent) | 23 (12) | 6.309 | -2.725 | — | — |  |
| passing_tds | pf-nfl (challenger) | 106 (57) | 0.895 | -0.021 | 0.601 | 80% | — |
| passing_tds | shadow-0.4.0 (incumbent) | 25 (13) | 0.845 | -0.118 | — | — |  |
| passing_yards | pf-nfl (challenger) | 106 (57) | 60.356 | -2.286 | 42.631 | 82% | — |
| passing_yards | shadow-0.4.0 (incumbent) | 25 (13) | 44.300 | +0.347 | — | — |  |
| receiving_yards | pf-nfl (challenger) | 646 (57) | 20.552 | +0.326 | 14.158 | 80% | — |
| receiving_yards | shadow-0.4.0 (incumbent) | 113 (13) | 22.231 | -12.471 | — | — |  |
| receptions | pf-nfl (challenger) | 646 (57) | 1.473 | +0.092 | 1.013 | 81% | — |
| receptions | shadow-0.4.0 (incumbent) | 100 (12) | 2.223 | -1.781 | — | — |  |
| rushing_yards | pf-nfl (challenger) | 187 (57) | 25.339 | -0.019 | 17.733 | 81% | — |
| rushing_yards | shadow-0.4.0 (incumbent) | 66 (13) | 17.607 | -5.586 | — | — |  |
| targets | pf-nfl (challenger) | 646 (57) | 1.884 | +0.137 | 1.303 | 82% | — |
| team_pass_attempts | pf-nfl (challenger) | 114 (57) | 5.852 | +0.850 | 4.155 | 85% | — |
| team_points | pf-nfl (challenger) | 114 (57) | 7.047 | +0.132 | 4.946 | 83% | — |
| team_rush_attempts | pf-nfl (challenger) | 114 (57) | 5.749 | -0.527 | 4.144 | 80% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **WATCH** — CRPS 115% of historical holdout
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
| anytime_td | new_team_first4 | 22 (18) | 0.09 | +0.085 | +93.9% | [-0.06, +0.17] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 289 (57) | 0.18 | +0.008 | +4.4% | [-0.03, +0.04] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 88 (48) | 0.16 | +0.021 | +13.4% | [-0.05, +0.09] | WATCH | monitored (no study band) |
| anytime_td | none_of_the_three | 379 (57) | 0.34 | -0.029 | -8.6% | [-0.07, +0.01] | OK |  |
| carries | new_team_first4 | 8 (8) | 4.88 | +2.499 | +51.3% | [+0.47, +4.33] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 92 (55) | 9.96 | -0.537 | -5.4% | [-1.72, +0.53] | OK | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 16 (15) | 9.50 | -1.271 | -13.4% | [-4.33, +1.26] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 90 (55) | 13.60 | +0.068 | +0.5% | [-1.02, +1.15] | OK |  |
| completions | new_team_first4 | 3 (3) | 17.67 | +0.722 | +4.1% | [-2.37, +4.93] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| completions | rookie | 3 (3) | 10.67 | +7.958 | +74.6% | [-1.81, +20.11] | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 100 (55) | 20.54 | +0.298 | +1.4% | [-1.06, +1.51] | OK |  |
| passing_attempts | new_team_first4 | 3 (3) | 25.67 | +5.285 | +20.6% | [+2.34, +10.67] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_attempts | rookie | 3 (3) | 20.33 | +10.135 | +49.8% | [-9.09, +31.94] | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 100 (55) | 32.03 | +0.315 | +1.0% | [-1.18, +2.04] | OK |  |
| passing_tds | new_team_first4 | 3 (3) | 0.00 | +1.142 | — | [+1.05, +1.19] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_tds | rookie | 3 (3) | 0.33 | +0.788 | +236.5% | [+0.26, +1.20] | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 100 (55) | 1.56 | -0.080 | -5.1% | [-0.31, +0.16] | OK |  |
| passing_yards | new_team_first4 | 3 (3) | 181.67 | +12.715 | +7.0% | [-46.84, +69.55] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_yards | rookie | 3 (3) | 74.67 | +115.948 | +155.3% | [+42.83, +197.60] | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 100 (55) | 234.88 | -6.283 | -2.7% | [-23.93, +9.59] | OK |  |
| receiving_yards | new_team_first4 | 19 (17) | 17.47 | +5.744 | +32.9% | [-2.84, +12.84] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 238 (57) | 19.23 | +2.055 | +10.7% | [-1.27, +4.61] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 75 (42) | 30.23 | +0.911 | +3.0% | [-4.79, +6.46] | OK | monitored (no study band) |
| receiving_yards | none_of_the_three | 370 (57) | 42.67 | -0.124 | -0.3% | [-3.48, +3.18] | OK |  |
| receptions | new_team_first4 | 19 (17) | 1.79 | +0.334 | +18.7% | [-0.51, +1.17] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 238 (57) | 1.73 | +0.225 | +13.0% | [+0.02, +0.40] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 75 (42) | 2.55 | +0.014 | +0.6% | [-0.44, +0.47] | OK | monitored (no study band) |
| receptions | none_of_the_three | 370 (57) | 3.72 | +0.074 | +2.0% | [-0.17, +0.31] | OK |  |
| rushing_yards | new_team_first4 | 8 (8) | 17.00 | +13.430 | +79.0% | [+6.30, +21.06] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 92 (55) | 42.04 | -2.309 | -5.5% | [-8.05, +3.75] | OK | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 16 (15) | 38.44 | -4.244 | -11.0% | [-17.98, +8.31] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 90 (55) | 56.78 | +1.146 | +2.0% | [-4.48, +6.71] | OK |  |
| targets | new_team_first4 | 19 (17) | 2.53 | +0.597 | +23.6% | [-0.35, +1.50] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 238 (57) | 2.70 | +0.306 | +11.3% | [+0.00, +0.56] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 75 (42) | 3.85 | +0.255 | +6.6% | [-0.30, +0.85] | OK | monitored (no study band) |
| targets | none_of_the_three | 370 (57) | 5.54 | +0.053 | +1.0% | [-0.26, +0.35] | OK |  |

Pooled relative bias (family-n weighted): new_team_first4 +44.5% (n=104); backup +7.2% (n=1187); rookie +8.7% (n=357); none_of_the_three -1.2% (n=2069)

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

**DNP (void) rate by pre-game participation call**: CONFIRMED_ACTIVE 0.0% (n=64); CONFIRMED_OUT 100.0% (n=187); LIKELY_ACTIVE 2.3% (n=3141); LIKELY_OUT 54.2% (n=24); UNCERTAIN 16.3% (n=283); UNVERIFIED 4.5% (n=66)

**Settled by gate status**: PASS n=3094 MAE=8.272; REVIEW n=349 MAE=9.535

**Availability capture** (last run): mean coverage 1.0, participation calls {'LIKELY_ACTIVE': 164, 'UNCERTAIN': 29, 'CONFIRMED_OUT': 8, 'LIKELY_OUT': 1}
