# Structural serve/return study (ATP, Pinnacle-linked subset, n=13383)

| forecaster | brier | log_loss | cal_slope | boot Brier diff vs market [95% CI] |
|---|---|---|---|---|
| market | 0.2023 | 0.5876 | 1.023 | +0.00000 [+0.00000, +0.00000] |
| elo (k_lo surface) | 0.2166 | 0.6216 | 0.830 | +0.01426 [+0.01239, +0.01598] |
| sr_prior300 | 0.2129 | 0.6125 | 0.922 | +0.01057 [+0.00904, +0.01242] |
| sr_prior600 | 0.2135 | 0.6136 | 1.043 | +0.01112 [+0.00955, +0.01291] |
| sr_prior1200 | 0.2158 | 0.6191 | 1.237 | +0.01344 [+0.01173, +0.01537] |
| avg_logit(elo, sr600) | 0.2108 | 0.6077 | 1.048 | +0.00844 [+0.00690, +0.00990] |

Subset with >= 3000 serve points seen for both players (n=12855):

| forecaster | brier | log_loss |
|---|---|---|
| market | 0.2042 | 0.5921 |
| elo | 0.2178 | 0.6245 |
| sr600 | 0.2152 | 0.6175 |
