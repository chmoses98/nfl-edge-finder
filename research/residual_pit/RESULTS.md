# Point-in-time residual research: the market moves toward us, and we are still not right

Reproduce: `python3 scripts/research/pit_residual_study.py`
Dataset: `research/residual_pit/pit_dataset_p_base.parquet` — **98,169 point-in-time observations across 254
games**, every 2025 player-prop contract at every horizon where both that horizon and the close were quoted
within 10 cents.

## The specification, and why it matters

Regressing `price_close − price_T` on `(model − price_T)` puts `price_T` on both sides with opposite signs.
Noise in `price_T` alone then produces a positive slope with no information present — ordinary mean
reversion, reported as "the market moves toward us". On a model that knows literally nothing, that
specification returns **z = +11.8**.

Everything below uses the honest form, with model and price entering as separate regressors:

`price_close − price_T ~ a + b·model_T + c·price_T`, cluster-robust on game.

Only `b` is evidence; `c` absorbs the mean reversion. `nfl_edge/research/clv.py`, pinned by
`tests/test_clv.py`, which asserts both that an information-free model gives `b ≈ 0` in the honest form and
that the naive form manufactures a large positive slope on the same data.

## A. The model does predict subsequent market movement

| horizon | n | games | b_model | se | z | naive b | naive z | share toward (of moved) | unchanged |
|---|---|---|---|---|---|---|---|---|---|
| T−72h | 748 | 25 | +0.0322 | 0.0267 | +1.20 | +0.0269 | +1.25 | 0.512 | 7% |
| T−48h | 5,709 | 114 | +0.0279 | 0.0150 | +1.86 | +0.0248 | +1.82 | 0.520 | 11% |
| **T−24h** | 13,562 | 240 | **+0.0333** | 0.0118 | **+2.82** | +0.0307 | +2.78 | 0.530 | 14% |
| **T−12h** | 14,099 | 253 | **+0.0317** | 0.0111 | **+2.85** | +0.0290 | +2.75 | 0.539 | 17% |
| T−6h | 14,790 | 253 | +0.0240 | 0.0104 | +2.30 | +0.0218 | +2.21 | 0.524 | 21% |
| T−3h | 15,873 | 253 | +0.0190 | 0.0095 | +2.00 | +0.0178 | +1.96 | 0.521 | 26% |
| T−90m | 16,479 | 253 | +0.0067 | 0.0021 | +3.24 | +0.0063 | +3.33 | 0.510 | 33% |
| T−30m | 16,909 | 254 | +0.0020 | 0.0012 | +1.69 | +0.0018 | +1.60 | 0.508 | 48% |

Positive at every horizon, peaking a day out. Honest and naive coefficients agree closely here (+0.0333 vs
+0.0307) because the width filter keeps prices tight enough that mean reversion is small — the contamination
is real but not what is driving this.

**Signed CLV** (movement in our direction, probability points): +0.00204 ± 0.00055 at T−24h (z = +3.68),
+0.00206 ± 0.00047 at T−12h (z = +4.34), decaying to +0.00013 by T−30m.

## The dose-response, and the placebo that validates it

CLV by **pre-specified** disagreement bucket at T−24h (buckets fixed before looking, never re-cut):

| \|model − mid\| | n | games | width | CLV | z | executable net after fees | z |
|---|---|---|---|---|---|---|---|
| 0.00–0.02 | 2338 | 204 | 0.060 | −0.00000 | −0.0 | −0.0527 ± 0.0244 | −2.2 |
| 0.02–0.05 | 3256 | 222 | 0.060 | +0.00077 | +1.6 | −0.0487 ± 0.0104 | −4.7 |
| 0.05–0.10 | 4032 | 223 | 0.060 | +0.00199 | +4.0 | −0.0299 ± 0.0103 | −2.9 |
| 0.10–0.15 | 2036 | 192 | 0.060 | +0.00289 | +3.1 | −0.0614 ± 0.0133 | −4.6 |
| 0.15+ | 1900 | 184 | 0.070 | +0.00591 | +2.3 | −0.0529 ± 0.0212 | −2.5 |

Monotone in disagreement, which is what a real signal looks like. Because that is also what mean reversion in
`mid_t` would look like, it was checked against a placebo: model probabilities shuffled **within statistic**,
preserving the marginal distribution but destroying the link to the specific contract.

| | 0.00–0.02 | 0.02–0.05 | 0.05–0.10 | 0.10–0.15 | 0.15+ |
|---|---|---|---|---|---|
| **real model** | −0.00000 | +0.00077 | **+0.00199** | **+0.00289** | **+0.00591** |
| placebo 1 | +0.00114 | −0.00029 | +0.00052 | −0.00048 | +0.00021 |
| placebo 2 | +0.00021 | +0.00147 | +0.00027 | +0.00044 | +0.00047 |
| placebo 3 | −0.00037 | −0.00023 | +0.00190 | +0.00067 | +0.00030 |

No placebo is monotone and none exceeds z = +3.2 in a single bucket. **The dose-response is real.**

## B. And yet the model still never beats the price on the outcome

The encompassing test, run at every horizon rather than only at the close:

| horizon | n | model coefficient | z | market coefficient | z |
|---|---|---|---|---|---|
| T−72h | 748 | −0.2392 ± 0.3671 | −0.65 | +1.0616 | +3.7 |
| T−24h | 13,562 | −0.0607 ± 0.0905 | −0.67 | +0.9894 | +11.8 |
| T−12h | 14,099 | −0.0567 ± 0.0844 | −0.67 | +0.9768 | +12.4 |
| T−6h | 14,790 | −0.0316 ± 0.0830 | −0.38 | +0.9662 | +12.3 |
| T−90m | 16,479 | −0.0254 ± 0.0767 | −0.33 | +0.9639 | +13.4 |
| T−30m | 16,909 | −0.0127 ± 0.0781 | −0.16 | +0.9489 | +13.0 |

**The model is encompassed at every horizon, not just at the close.** The session-2 result was not an artefact
of looking only at closing prices.

## How both can be true

The model holds information the market at T−24h has not yet priced, and that the market at close has. So the
market drifts in the direction the model already pointed — genuine CLV. But the model is noisier than the
closing price, so it never beats the outcome. **We are directionally early and absolutely wrong**: useful for
predicting the market, useless for predicting football better than the market.

## Early week versus close: less efficient, and more expensive by more than the difference

| horizon | n | games | median width | market Brier | signed CLV | executable net | CLV ÷ half-spread |
|---|---|---|---|---|---|---|---|
| T−72h | 748 | 25 | 0.070 | 0.1950 | +0.00098 | −0.0397 ± 0.0322 | 0.028 |
| T−48h | 5,709 | 114 | 0.070 | 0.1926 | +0.00137 | −0.0370 ± 0.0116 | 0.039 |
| **T−24h** | 13,562 | 240 | 0.060 | 0.1897 | **+0.00204** | −0.0446 ± 0.0087 | **0.068** |
| **T−12h** | 14,099 | 253 | 0.060 | 0.1890 | **+0.00206** | −0.0425 ± 0.0083 | **0.069** |
| T−6h | 14,790 | 253 | 0.060 | 0.1889 | +0.00133 | −0.0403 ± 0.0081 | 0.044 |
| T−3h | 15,873 | 253 | 0.050 | 0.1894 | +0.00080 | −0.0370 ± 0.0077 | 0.032 |
| T−90m | 16,479 | 253 | 0.050 | 0.1885 | +0.00024 | −0.0369 ± 0.0073 | 0.010 |
| T−30m | 16,909 | 254 | 0.050 | 0.1891 | +0.00013 | −0.0336 ± 0.0076 | 0.005 |

Three things at once. The market's own accuracy **barely improves** across three days — Brier 0.1950 at
T−72h against 0.1891 at T−30m. Our CLV **peaks a day out** and is essentially gone by kickoff, which is what
information being gradually absorbed looks like. And the book is **wider exactly when the CLV is largest**:
7 cents at T−48h against 5 cents at T−30m.

So the answer to "are early prices meaningfully less efficient once the wider spread is accounted for?" is
**no**. The extra inefficiency available early is about 0.2 probability points; the extra width costs about 2.
Executable net is negative at every horizon without exception (−0.034 to −0.045).

## The economics kill it

| | value |
|---|---|
| median quoted width at T−24h | 0.0600 |
| half-spread paid to enter | 0.0300 |
| mean signed CLV captured | 0.00204 |
| **CLV ÷ half-spread** | **0.068** |

We capture about **7% of the cost of entry**. The signal is roughly **15× too small** to pay the spread, and
executable net returns are negative in every disagreement bucket (−0.030 to −0.061, all significant).

This is the first genuine positive signal the project has produced: statistically real, correctly signed,
monotone in dose, placebo-controlled — and economically dead by more than an order of magnitude. Registered as
`H-20260904-020`.
