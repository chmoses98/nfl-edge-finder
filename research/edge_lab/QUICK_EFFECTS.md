# Edge-lab quick effect sizes vs the closing line (descriptive; 2010–2025 regular season)

`scripts/research/quick_effects.py`. Each row: mean residual of the outcome against the closing line with a
bootstrap 95% CI. A factor the market already prices shows a residual near zero. Observed wind/temperature are
**post hoc** (game-time readings), so weather rows are an upper bound on what a pregame forecast could capture.

| factor | n | mean residual | 95% CI | reading |
|---|---|---|---|---|
| team starting a different QB than its previous game (team margin − spread) | 766 | −0.50 | [−1.43, +0.44] | close absorbs QB changes on average; sign suggests slight over-reaction is not present, residual ≈ 0 |
| wind 0–5 mph (total − line, outdoors) | 614 | +1.22 | [+0.13, +2.33] | calm games run over slightly |
| wind 5–10 | 1,235 | +0.70 | [−0.04, +1.46] | |
| wind 10–15 | 641 | −0.91 | [−1.85, +0.03] | close lowers the total (44.9 → 44.1 → 43.8) but not fully |
| wind 15–20 | 255 | −1.33 | [−2.93, +0.27] | |
| wind 20+ | 81 | +0.07 | [−2.74, +2.90] | too few games |
| temperature buckets | — | all within ±0.5 | CIs include 0 | no residual temperature effect |
| home rest advantage ≥ 4 days / disadvantage | 221 / 253 | −0.18 / −0.33 | include 0 | priced |
| Thursday games (total) | 268 | +0.44 | [−1.21, +2.03] | priced |
| neutral/international site (home margin) | 60 | −0.09 | wide | priced / too few |
| divisional games (total) | 1,536 | −0.24 | [−0.89, +0.45] | priced |
| all games home residual | 4,175 | +0.06 | [−0.33, +0.45] | line is unbiased |

Verdict: nothing here is an edge by itself. Wind is the only candidate with a monotone pattern (≈ −1 point of total per
10–20 mph bucket beyond the line), and it must be re-tested with **forecast vintages** (Open-Meteo previous-runs
archive from 2024, NWS prospective from now) before it can count. Registry: H-006 → PROMISING (forecast test required); H-005 QB change → residual ≈ 0 at the close; the live question moves to *early-week* Kalshi prices (H-002).
