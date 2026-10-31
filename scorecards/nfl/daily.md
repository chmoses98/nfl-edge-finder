## NFL projection scorecard — last 7 days

Generated 2026-10-31T17:43:30Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 6541 across 41 games. Settled: 2515 (void/DNP 185, stat corrections 0).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 167 (14) | Brier 0.1840 | calib -0.034 | log loss 0.5410 | — |  |
| carries | pf-nfl (challenger) | 43 (14) | 5.026 | -0.552 | 3.469 | 72% | — |
| completions | pf-nfl (challenger) | 27 (14) | 5.163 | +0.355 | 3.496 | 85% | — |
| passing_attempts | pf-nfl (challenger) | 27 (14) | 6.934 | +1.023 | 4.771 | 89% | — |
| passing_tds | pf-nfl (challenger) | 27 (14) | 0.828 | -0.023 | 0.544 | 81% | — |
| passing_yards | pf-nfl (challenger) | 27 (14) | 54.499 | -3.112 | 39.149 | 85% | — |
| receiving_yards | pf-nfl (challenger) | 157 (14) | 19.935 | +0.701 | 13.560 | 83% | — |
| receptions | pf-nfl (challenger) | 157 (14) | 1.392 | +0.078 | 0.952 | 85% | — |
| rushing_yards | pf-nfl (challenger) | 43 (14) | 31.072 | -5.245 | 20.867 | 74% | — |
| targets | pf-nfl (challenger) | 157 (14) | 1.737 | +0.233 | 1.203 | 87% | — |
| team_pass_attempts | pf-nfl (challenger) | 28 (14) | 6.495 | +1.798 | 4.350 | 89% | — |
| team_points | pf-nfl (challenger) | 28 (14) | 7.757 | +0.033 | 5.166 | 86% | — |
| team_rush_attempts | pf-nfl (challenger) | 28 (14) | 5.962 | -1.479 | 4.233 | 79% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **INSUFFICIENT** — 43 settled forecasts (< 100)
- completions: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 27 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **INSUFFICIENT** — 43 settled forecasts (< 100)
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 28 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 28 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 28 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 7 (7) | 0.29 | -0.088 | -30.8% | [-0.39, +0.17] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 65 (14) | 0.20 | -0.021 | -10.4% | [-0.10, +0.05] | OK | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 20 (11) | 0.15 | +0.010 | +6.8% | [-0.14, +0.14] | INSUFFICIENT | monitored (no study band) |
| anytime_td | none_of_the_three | 91 (14) | 0.36 | -0.048 | -13.1% | [-0.13, +0.04] | OK |  |
| carries | new_team_first4 | 4 (4) | 6.00 | +2.760 | +46.0% | [+1.31, +4.41] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 20 (14) | 10.65 | -0.344 | -3.2% | [-3.64, +2.28] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 3 (3) | 9.67 | -3.992 | -41.3% | [-6.80, +0.74] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 22 (14) | 15.18 | -0.996 | -6.6% | [-3.07, +1.75] | INSUFFICIENT |  |
| completions | new_team_first4 | 1 (1) | 20.00 | -2.825 | -14.1% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| completions | rookie | 1 (1) | 0.00 | +20.108 | — | — | INSUFFICIENT | monitored (no study band) |
| completions | none_of_the_three | 25 (14) | 21.32 | -0.308 | -1.4% | [-2.08, +2.19] | INSUFFICIENT |  |
| passing_attempts | new_team_first4 | 1 (1) | 28.00 | +2.229 | +8.0% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_attempts | rookie | 1 (1) | 0.00 | +31.937 | — | — | INSUFFICIENT | monitored (no study band) |
| passing_attempts | none_of_the_three | 25 (14) | 32.88 | -0.262 | -0.8% | [-2.59, +2.15] | INSUFFICIENT |  |
| passing_tds | new_team_first4 | 1 (1) | 0.00 | +1.190 | — | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_tds | rookie | 1 (1) | 0.00 | +1.195 | — | — | INSUFFICIENT | monitored (no study band) |
| passing_tds | none_of_the_three | 25 (14) | 1.56 | -0.121 | -7.7% | [-0.54, +0.26] | INSUFFICIENT |  |
| passing_yards | new_team_first4 | 1 (1) | 252.00 | -61.266 | -24.3% | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_yards | rookie | 1 (1) | 0.00 | +197.596 | — | — | INSUFFICIENT | monitored (no study band) |
| passing_yards | none_of_the_three | 25 (14) | 233.24 | -8.814 | -3.8% | [-31.09, +16.22] | INSUFFICIENT |  |
| receiving_yards | new_team_first4 | 7 (7) | 9.29 | +7.840 | +84.4% | [-5.80, +16.96] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 57 (14) | 16.96 | +2.642 | +15.6% | [-1.74, +6.56] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 17 (9) | 37.00 | -5.393 | -14.6% | [-17.16, +7.58] | INSUFFICIENT | monitored (no study band) |
| receiving_yards | none_of_the_three | 89 (14) | 42.46 | +1.107 | +2.6% | [-3.76, +6.81] | OK |  |
| receptions | new_team_first4 | 7 (7) | 1.29 | +0.710 | +55.2% | [-0.82, +1.91] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 57 (14) | 1.63 | +0.282 | +17.3% | [-0.09, +0.59] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 17 (9) | 2.76 | -0.204 | -7.4% | [-0.97, +0.58] | INSUFFICIENT | monitored (no study band) |
| receptions | none_of_the_three | 89 (14) | 3.90 | +0.013 | +0.3% | [-0.45, +0.49] | OK |  |
| rushing_yards | new_team_first4 | 4 (4) | 22.50 | +11.991 | +53.3% | [+1.16, +19.87] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 20 (14) | 44.65 | -3.251 | -7.3% | [-20.53, +10.47] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 3 (3) | 45.33 | -22.625 | -49.9% | [-37.16, -1.74] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 22 (14) | 68.18 | -8.163 | -12.0% | [-20.67, +5.69] | INSUFFICIENT |  |
| targets | new_team_first4 | 7 (7) | 2.00 | +0.768 | +38.4% | [-1.03, +2.57] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 57 (14) | 2.44 | +0.457 | +18.7% | [+0.12, +0.83] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 17 (9) | 4.06 | +0.104 | +2.6% | [-1.04, +1.05] | INSUFFICIENT | monitored (no study band) |
| targets | none_of_the_three | 89 (14) | 5.70 | +0.121 | +2.1% | [-0.44, +0.71] | OK |  |

Pooled relative bias (family-n weighted): new_team_first4 +35.8% (n=39); backup +7.4% (n=276); rookie -6.1% (n=77); none_of_the_three -3.0% (n=502)

**DNP (void) rate by pre-game participation call**: CONFIRMED_ACTIVE 0.0% (n=64); CONFIRMED_OUT 100.0% (n=40); LIKELY_ACTIVE 1.8% (n=731); LIKELY_OUT 100.0% (n=10); UNCERTAIN 18.0% (n=61)

**Settled by gate status**: PASS n=764 MAE=8.296; REVIEW n=68 MAE=10.516

**Availability capture** (last run): mean coverage 1.0, participation calls {'LIKELY_ACTIVE': 166, 'UNCERTAIN': 31, 'CONFIRMED_OUT': 7}
