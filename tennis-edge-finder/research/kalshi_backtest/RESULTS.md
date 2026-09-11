# Model vs KALSHI pre-start price (settled match-winner markets, Jul-Sep 2026)

Funnel: {'events': 3921, 'linked': 1869, 'unmapped': 769, 'non_binary_settlement': 49, 'no_prestart_quote': 1233, 'not_two_parsed_sides': 1}

Kalshi quote = last hourly candle ending before min(nominal start - 5 min, close_time - 7 h) (occurrence_datetime is NOT a start time for ITF/Challenger: it usually falls after the close), two-sided, spread <= 15c, OI > 0. Model = production rating states FROZEN at the end of the Sackmann fork data (ATP 2026-06-01, WTA 2026-04-27), so ratings predate every market (no leakage) but are 1-4 months stale. Truth = exchange binary result. Orientation randomised.

n = 1869

| forecaster | brier | log_loss | accuracy | ECE | cal_slope | boot Brier diff vs Kalshi mid [95% CI] |
|---|---|---|---|---|---|---|
| kalshi_mid | 0.1871 | 0.5503 | 0.7095 | 0.0162 | 1.010 | +0.00000 [+0.00000, +0.00000] |
| p_elo | 0.2062 | 0.5982 | 0.6763 | 0.0155 | 0.954 | +0.01907 [+0.01278, +0.02527] |
| p_sr | 0.2178 | 0.6229 | 0.6356 | 0.0199 | 0.992 | +0.03070 [+0.02411, +0.03774] |
| p_ens | 0.2060 | 0.5974 | 0.6672 | 0.0166 | 1.097 | +0.01890 [+0.01308, +0.02520] |

## By series (log-loss)

| series | n | Kalshi | elo | ensemble |
|---|---|---|---|---|
| KXATPCHALLENGERMATCH | 431 | 0.6039 | 0.6287 | 0.6150 |
| KXATPMATCH | 167 | 0.5735 | 0.5798 | 0.5736 |
| KXITFMATCH | 540 | 0.5249 | 0.5959 | 0.5956 |
| KXITFWMATCH | 485 | 0.5376 | 0.5972 | 0.6014 |
| KXWTACHALLENGERMATCH | 76 | 0.5832 | 0.6209 | 0.6348 |
| KXWTAMATCH | 170 | 0.4937 | 0.5383 | 0.5534 |

## Disagreement buckets |ensemble - Kalshi mid| (buy model-favoured side at its ASK, taker fee)

| bucket | n | model brier | Kalshi brier | model-side win% | avg ask paid | net ROI per $1 after fees |
|---|---|---|---|---|---|---|
| 0.000-0.025 | 288 | 0.1829 | 0.1824 | 0.434 | 0.456 | -0.088 |
| 0.025-0.050 | 257 | 0.1824 | 0.1791 | 0.405 | 0.431 | -0.102 |
| 0.050-0.100 | 453 | 0.1928 | 0.1868 | 0.375 | 0.384 | -0.070 |
| 0.100-0.150 | 361 | 0.2114 | 0.2002 | 0.357 | 0.355 | -0.044 |
| 0.150-0.200 | 207 | 0.2376 | 0.2061 | 0.300 | 0.309 | -0.088 |
| 0.200-1.000 | 303 | 0.2397 | 0.1704 | 0.261 | 0.245 | -0.004 |

## Reliability (Kalshi mid vs ensemble)

| bin | n | Kalshi mean p | obs | elo mean p | obs |
|---|---|---|---|---|---|
| 0.0-0.1 | 130 | 0.071 | 0.046 | 0.068 | 0.057 |
| 0.1-0.2 | 147 | 0.153 | 0.184 | 0.155 | 0.135 |
| 0.2-0.3 | 181 | 0.248 | 0.26 | 0.256 | 0.203 |
| 0.3-0.4 | 221 | 0.348 | 0.362 | 0.353 | 0.364 |
| 0.4-0.5 | 271 | 0.448 | 0.432 | 0.45 | 0.459 |
| 0.5-0.6 | 257 | 0.55 | 0.549 | 0.549 | 0.562 |
| 0.6-0.7 | 204 | 0.649 | 0.672 | 0.645 | 0.636 |
| 0.7-0.8 | 191 | 0.753 | 0.728 | 0.746 | 0.747 |
| 0.8-0.9 | 155 | 0.848 | 0.865 | 0.843 | 0.892 |
| 0.9-1.0 | 112 | 0.933 | 0.929 | 0.927 | 0.958 |

Median hours between the quote candle and the cutoff: 0.5; median hours between cutoff and market close: 7.0; median OI at quote: 204
