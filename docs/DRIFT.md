# Drift watch

Quantities that changed materially across seasons and must be monitored before any model is trusted:

| quantity | 2006–2015 | 2016–2025 | note |
|---|---|---|---|
| σ(margin − closing spread) | 13.5–14.5 (pooled 13.7) | 11.4–13.7 (pooled 12.7) | scoring variance / line sharpness drift; a normal with old σ over-prices alternate-spread tails by 3–4 points of probability at ±7.5 |
| σ(total − closing total) | 12.0–14.1 | 12.5–14.2 | stable |
| P(|margin| = 3) | 10–18% by season | 10–17% | noisy; key-number mass must be estimated from ≥8 seasons |
| home-field residual | ≈ 0 | ≈ 0 (2019–2020 negative: −1.9, −1.0) | the line adapts; do not hard-code HFA |

Rule: every calibration artifact records its training window; a σ or key-number estimate older than 3 seasons is
flagged. Kalshi-side drift (liquidity, spreads by family, fee schedule changes) is measured from the capture
manifests and the microstructure snapshot series (`research/market_microstructure/`).
