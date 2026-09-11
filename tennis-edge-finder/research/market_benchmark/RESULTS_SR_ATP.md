# Structural serve/return study (ATP, Pinnacle-linked subset, n=13323)

| forecaster | brier | log_loss | cal_slope | boot Brier diff vs market [95% CI] |
|---|---|---|---|---|
| market | 0.2026 | 0.5884 | 1.023 | +0.00000 [+0.00000, +0.00000] |
| elo (k_lo surface) | 0.2169 | 0.6221 | 0.826 | +0.01426 [+0.01231, +0.01611] |
| sr_prior300 | 0.2133 | 0.6135 | 0.917 | +0.01071 [+0.00888, +0.01239] |
| sr_prior600 | 0.2138 | 0.6144 | 1.037 | +0.01123 [+0.00946, +0.01303] |
| sr_prior1200 | 0.2161 | 0.6198 | 1.229 | +0.01348 [+0.01174, +0.01530] |
| avg_logit(elo, sr600) | 0.2111 | 0.6084 | 1.042 | +0.00851 [+0.00702, +0.00976] |

Subset with >= 3000 serve points seen for both players (n=12811):

| forecaster | brier | log_loss |
|---|---|---|
| market | 0.2046 | 0.5931 |
| elo | 0.2180 | 0.6250 |
| sr600 | 0.2155 | 0.6181 |
