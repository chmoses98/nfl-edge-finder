# Modeling

## Latent structure
PLAYER STATE (Elo overall + surface, serve ability s, return ability r) → point-win probabilities
(pa = P(A wins point on serve), pb = P(A wins point on return)) → exact DP over game / tiebreak / set /
match under the resolved MatchFormat → every Kalshi payoff. Tournament markets reuse P(a beats b) in the
bracket DP.

## Models implemented
| model | inputs | update | notes |
|---|---|---|---|
| naive rank | pre-tournament ranks (log-rank difference, fixed slope) | -- | ATP Brier 0.2142 / LL 0.6182; WTA 0.2196 / 0.6304 |
| elo_plain | results | K = 250/(n+5)^0.4 | best log-loss on all-level corpora |
| elo_levelprior | + level-dependent initial rating | same | marginally best on ATP/WTA all-level |
| elo_surface | + surface rating partially pooled (w_max 0.5, n_half 20) | same | slightly worse on all-level corpora, best on tour-only (2000-2026 TML study) |
| elo_surface_levelk | + level K multipliers | same | best-calibrated Elo (slope 0.97) |
| elo_surface_k_lo (production) | K0 = 180 | same | calibrated (slope 1.07 ATP / 1.28 WTA), lowest sharpness; chosen for the tour-level Pinnacle test where it was best among Elo variants |
| structural serve/return (sr_prior300/600) | Sackmann serve stats, opponent-adjusted, shrunk with n_prior points, tau 365 d | chronological | beats Elo on tour matches (Brier 0.2133 vs 0.2169) |
| ENSEMBLE (production fair value) | logit average of Elo and structural (bo3 basis), falls back to Elo without serve evidence | -- | Brier 0.2111 on the Pinnacle-linked ATP set |
| doubles baseline | mean singles Elo per team, blend prior | -- | unvalidated; grade capped C |

## Walk-forward results (symmetric orientation)
ATP all levels 1990-2026, eval 2015+ (n = 321,480, single id system): elo_levelprior Brier 0.2000 / LL 0.5836;
elo_plain 0.2001 / 0.5837; elo_surface_k_lo 0.2042 / 0.5934 (slope 1.07); naive rank 0.2142 / 0.6182.
WTA all levels (n = 299,185, after the ITF match-tiebreak parser fix): elo_levelprior 0.1933 / 0.5667; elo_surface_k_lo 0.2004 / 0.5850; naive rank 0.2196 / 0.6304.
By level (elo_plain LL): ITF 0.556-0.564 (favourite-heavy), Challenger 0.628, tour 0.607-0.630, slams 0.589-0.591.

## Versus bookmaker (Pinnacle, ATP 2020-2026, n = 13,323 linked)
| forecaster | Brier | log-loss | slope |
|---|---|---|---|
| Pinnacle (vig-free) | 0.2026 | 0.5884 | 1.02 |
| ensemble (elo + sr600) | 0.2111 | 0.6084 | 1.04 |
| structural sr_prior300 | 0.2133 | 0.6135 | 0.92 |
| elo_surface_k_lo | 0.2169 | 0.6221 | 0.83 |
Paired bootstrap Brier(model) − Brier(market): +0.0143 [+0.0123, +0.0160] (Elo); +0.0085 [+0.0070, +0.0098] (ensemble).
Walk-forward hybrid weights (fit on seasons < t): w_market ≈ 1.04-1.08, w_model ≈ −0.04 to −0.07; the hybrid is
NOT better than the market (+0.0002 Brier, CI excludes an improvement). Large disagreements (|Δ| > 20 pp) are
model error: the model-favoured side wins 32.5 % when the market says 35 %.

## Versus Kalshi (settled match-winner markets Jul-Sep 2026, n = 1,869 with a conservative pregame quote)
Kalshi mid Brier 0.1871 / LL 0.5503 / slope 1.01 vs ensemble 0.2060 / 0.5974 (ratings frozen 1-4 months earlier).
Every disagreement bucket has negative net ROI at the ask after fees. On KXATPMATCH only (n = 167) the ensemble's
log-loss equals Kalshi's (0.5736 vs 0.5735) -- too small to mean anything, worth a prospective look.

## Calibration
Elo with K0 ≥ 250 is over-confident on tour matches (slope 0.83-0.89); K0 = 180 or the ensemble is close to 1.
Platt/isotonic recalibration was not applied in production: the slope is already ≈ 1 for the ensemble and the
market is better on every cut, so recalibrating the model cannot create edge. Calibration fitting, when used,
must be walk-forward (implemented in the hybrid study as the market-recalibration control).

## Features not (yet) in the model
Rest / recent load / surface switch / rank were ablated on the Pinnacle-linked set
(research/market_benchmark/RESULTS_ABLATION_ATP.md); see MORNING_REPORT for the outcome. Fatigue minutes,
travel, altitude, indoor, weather, injuries, tiebreak skill: not implemented.

## What would have to change for the model to matter
The market's information advantage (injury/withdrawal news, form, scheduling, in-play) is exactly what free,
weekly-refreshed match data does not carry. Candidate directions with real upside: (1) same-day data freshness
(currently 1-4 months stale), (2) a first-ball feed so the model is scored against a true close, (3) serve/return
features on Challenger/ITF where the market is thinner (Kalshi Challenger LL 0.604 vs ITF 0.525 suggests ITF is
already efficient), (4) derivative markets (totals/spreads) where the DP distribution might beat a crowd that mostly
trades the winner -- untested for lack of settled derivative histories with a clean pregame quote.
