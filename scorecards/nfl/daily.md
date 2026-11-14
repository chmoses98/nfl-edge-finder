## NFL projection scorecard — last 7 days

Generated 2026-11-14T19:12:37Z. Research only; nothing here is a betting signal.

Archived pregame forecasts: 13156 across 70 games. Settled: 4446 (void/DNP 349, stat corrections 2).

| Stat | Model | n (games) | MAE | Bias | CRPS | 80% range caught | vs incumbent (CRPS) |
|---|---|---|---|---|---|---|---|
| anytime_td (yes/no) | pf-nfl (challenger) | 182 (15) | Brier 0.1740 | calib +0.007 | log loss 0.5278 | — |  |
| carries | pf-nfl (challenger) | 52 (15) | 4.127 | +0.281 | 3.113 | 73% | — |
| completions | pf-nfl (challenger) | 27 (15) | 2.767 | -0.049 | 2.164 | 100% | — |
| passing_attempts | pf-nfl (challenger) | 27 (15) | 4.402 | +0.200 | 3.198 | 96% | — |
| passing_tds | pf-nfl (challenger) | 27 (15) | 0.902 | -0.043 | 0.628 | 85% | — |
| passing_yards | pf-nfl (challenger) | 27 (15) | 58.484 | -14.279 | 39.353 | 89% | — |
| receiving_yards | pf-nfl (challenger) | 164 (15) | 19.826 | -0.690 | 13.920 | 85% | — |
| receptions | pf-nfl (challenger) | 164 (15) | 1.331 | +0.085 | 0.950 | 87% | — |
| rushing_yards | pf-nfl (challenger) | 52 (15) | 19.370 | +3.726 | 14.627 | 83% | — |
| targets | pf-nfl (challenger) | 164 (15) | 1.794 | +0.191 | 1.244 | 87% | — |
| team_pass_attempts | pf-nfl (challenger) | 30 (15) | 3.848 | +0.832 | 2.892 | 97% | — |
| team_points | pf-nfl (challenger) | 30 (15) | 6.133 | +0.445 | 4.642 | 87% | — |
| team_rush_attempts | pf-nfl (challenger) | 30 (15) | 5.130 | -0.098 | 3.726 | 87% | — |

**Drift checks**

- anytime_td: **OK** — within expectations
- carries: **INSUFFICIENT** — 52 settled forecasts (< 100)
- completions: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_attempts: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_tds: **INSUFFICIENT** — 27 settled forecasts (< 100)
- passing_yards: **INSUFFICIENT** — 27 settled forecasts (< 100)
- receiving_yards: **OK** — within expectations
- receptions: **OK** — within expectations
- rushing_yards: **INSUFFICIENT** — 52 settled forecasts (< 100)
- targets: **OK** — within expectations
- team_pass_attempts: **INSUFFICIENT** — 30 settled forecasts (< 100)
- team_points: **INSUFFICIENT** — 30 settled forecasts (< 100)
- team_rush_attempts: **INSUFFICIENT** — 30 settled forecasts (< 100)

### NFL monitoring lines (research only; pre-registered corrections are NOT adopted)

| Stat | Segment | n (games) | Mean actual | Bias (model - actual) | Relative | 95% CI | Status | Study (dev) |
|---|---|---|---|---|---|---|---|---|
| anytime_td | new_team_first4 | 4 (3) | 0.00 | +0.162 | — | [+0.13, +0.21] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| anytime_td | backup | 74 (15) | 0.16 | +0.025 | +15.5% | [-0.09, +0.12] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| anytime_td | rookie | 24 (13) | 0.21 | -0.000 | -0.1% | [-0.15, +0.14] | INSUFFICIENT | monitored (no study band) |
| anytime_td | none_of_the_three | 98 (15) | 0.32 | +0.000 | +0.1% | [-0.08, +0.08] | OK |  |
| carries | new_team_first4 | 1 (1) | 0.00 | +5.885 | — | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| carries | backup | 24 (14) | 9.79 | -0.918 | -9.4% | [-2.86, +1.34] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| carries | rookie | 5 (4) | 9.80 | +1.603 | +16.4% | [-2.17, +4.12] | INSUFFICIENT | monitored (no study band) |
| carries | none_of_the_three | 26 (15) | 12.35 | +1.303 | +10.6% | [-0.31, +3.18] | INSUFFICIENT |  |
| completions | new_team_first4 | 2 (2) | 16.50 | +2.495 | +15.1% | [+0.06, +4.93] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| completions | none_of_the_three | 25 (13) | 20.92 | -0.252 | -1.2% | [-1.99, +1.33] | INSUFFICIENT |  |
| passing_attempts | new_team_first4 | 2 (2) | 24.50 | +6.812 | +27.8% | [+2.96, +10.67] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_attempts | none_of_the_three | 25 (13) | 32.48 | -0.329 | -1.0% | [-2.56, +1.61] | INSUFFICIENT |  |
| passing_tds | new_team_first4 | 2 (2) | 0.00 | +1.118 | — | [+1.05, +1.19] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_tds | none_of_the_three | 25 (13) | 1.64 | -0.136 | -8.3% | [-0.69, +0.35] | INSUFFICIENT |  |
| passing_yards | new_team_first4 | 2 (2) | 146.50 | +49.706 | +33.9% | [+29.86, +69.55] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| passing_yards | none_of_the_three | 25 (13) | 248.92 | -19.397 | -7.8% | [-46.11, +9.17] | INSUFFICIENT |  |
| receiving_yards | new_team_first4 | 3 (3) | 12.00 | +13.967 | +116.4% | [+5.86, +25.84] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receiving_yards | backup | 61 (15) | 21.38 | +0.535 | +2.5% | [-7.37, +7.35] | OK | +7% to +18% (development, pre-registered, not adopted) |
| receiving_yards | rookie | 21 (11) | 36.86 | -4.027 | -10.9% | [-13.30, +5.05] | INSUFFICIENT | monitored (no study band) |
| receiving_yards | none_of_the_three | 93 (15) | 43.94 | +0.226 | +0.5% | [-6.41, +6.33] | OK |  |
| receptions | new_team_first4 | 3 (3) | 1.00 | +0.976 | +97.6% | [-0.35, +2.30] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| receptions | backup | 61 (15) | 1.80 | +0.184 | +10.2% | [-0.24, +0.67] | WATCH | +7% to +18% (development, pre-registered, not adopted) |
| receptions | rookie | 21 (11) | 2.76 | -0.048 | -1.7% | [-0.45, +0.49] | INSUFFICIENT | monitored (no study band) |
| receptions | none_of_the_three | 93 (15) | 3.83 | +0.107 | +2.8% | [-0.31, +0.51] | OK |  |
| rushing_yards | new_team_first4 | 1 (1) | 0.00 | +26.586 | — | — | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| rushing_yards | backup | 24 (14) | 40.21 | -3.057 | -7.6% | [-13.64, +8.19] | INSUFFICIENT | +7% to +18% (development, pre-registered, not adopted) |
| rushing_yards | rookie | 5 (4) | 38.60 | +8.821 | +22.9% | [-11.88, +27.53] | INSUFFICIENT | monitored (no study band) |
| rushing_yards | none_of_the_three | 26 (15) | 49.58 | +8.797 | +17.7% | [+1.45, +17.63] | INSUFFICIENT |  |
| targets | new_team_first4 | 3 (3) | 1.33 | +1.808 | +135.6% | [-0.30, +3.57] | INSUFFICIENT | +14% to +37% (development, pre-registered, not adopted) |
| targets | backup | 61 (15) | 2.95 | +0.101 | +3.4% | [-0.56, +0.69] | OK | +7% to +18% (development, pre-registered, not adopted) |
| targets | rookie | 21 (11) | 4.00 | +0.363 | +9.1% | [-0.36, +1.16] | INSUFFICIENT | monitored (no study band) |
| targets | none_of_the_three | 93 (15) | 5.52 | +0.273 | +5.0% | [-0.23, +0.74] | OK |  |

Pooled relative bias (family-n weighted): backup +5.7% (n=305); rookie +1.2% (n=97); none_of_the_three +2.0% (n=529); new_team_first4 +80.2% (n=15)

**DNP (void) rate by pre-game participation call**: CONFIRMED_OUT 100.0% (n=55); LIKELY_ACTIVE 3.3% (n=859); LIKELY_OUT 30.0% (n=10); UNCERTAIN 17.2% (n=58)

**Settled by gate status**: PASS n=826 MAE=7.900; REVIEW n=60 MAE=5.352

**Availability capture** (last run): mean coverage 1.0, participation calls {'LIKELY_ACTIVE': 164, 'UNCERTAIN': 29, 'CONFIRMED_OUT': 8, 'LIKELY_OUT': 1}
