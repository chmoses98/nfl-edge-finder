# Alternate-spread / alternate-total ladders from the closing line (Milestone G groundwork)

Script `scripts/research/margin_ladder_study.py`. Question: given the consensus closing spread s and total t, how well can
P(margin > k−0.5) and P(total ≥ k) — exactly Kalshi's KXNFLSPREAD / KXNFLTOTAL rung semantics — be modelled without any
football features? Walk-forward, test seasons 2016–2025 (2,639 games), rungs k ∈ [−21, 21] around the spread and [30, 70] for totals.

| market | family | mean Brier over rungs | log loss |
|---|---|---|---|
| spread | empirical residual (pooled last 10 seasons) | **0.14383** | 0.44563 |
| spread | empirical by favourite-size bucket | 0.14390 | 0.44597 |
| spread | normal(s, σ_train) | 0.14406 | 0.44622 |
| total | normal(t, σ_train) | **0.15851** | 0.48408 |
| total | empirical residual | 0.15862 | 0.48425 |

Findings
1. **The residual scale drifted.** σ(margin − spread) was 13.5–14.5 in 2006–2014 and 11.4–13.2 in 2016–2025 (12.7 pooled). A normal fitted on old seasons over-prices tails: at d = +7.5 the normal says 0.292, observed 0.247; at +10.5, 0.222 vs 0.182. Any margin model must use a recent-window or time-decayed σ, and drift in σ is a monitored quantity (docs/DRIFT.md to follow).
2. **Discreteness at the line matters.** P(res > −0.5) = 0.503 but P(res > +0.5) = 0.456: 4.7% of games land within half a point of the spread (2.5% exact pushes on integer lines). The empirical residual distribution captures this and the key numbers (|margin| = 3 in 14.4% of games, 7 in 8.5%); a continuous normal cannot, which is why it loses on rungs near the line and wins nothing elsewhere.
3. Conditioning the residual on favourite size does not help (bucketed empirical ≈ pooled). Totals show no key-number structure, so normal ≈ empirical.
4. Practical rule for the pricer: price spread ladders with an **empirical, recency-weighted margin-residual distribution** centred on the market-implied margin (Kalshi's own winner/spread ladder once liquid, else the consensus line), and total ladders with a normal of recent σ. This is MODEL B (market-as-prior) for the game environment.

Not claimed: any edge. This is a calibration baseline that Kalshi's alternate ladders will be compared against once the 2025 backfill (settled rungs with prices) is in.
