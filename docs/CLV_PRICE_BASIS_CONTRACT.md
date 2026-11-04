# CLV price-basis contract — selection vs execution vs fees

## The critical invariant

**Do not calculate market-movement CLV using Kalshi's fee-inclusive position cost basis.**
A 50¢ exchange fill may display near 51.7¢ as an average cost *after entry fees*.
If the market remains at 50¢, it has **not** moved against the trade by 1.7¢.

Every CLV report must label its **price basis**, **side**, **timestamp**, **quote convention**, **fee basis**, and **provenance**. An unknown basis or a missing valid pre-start quote cannot be silently replaced by an account UI average price, a settled 0/1 mark, a last trade, or a model forecast.

## Keep three distinct measurements

| Measure | Definition (normalize to purchased YES/NO side) | Purpose |
|---|---|---|
| **Selection CLV** | close midpoint − recommendation-time midpoint | Is the recommendation direction followed by market movement? Research, **pre-fee** |
| **Hypothetical entry CLV** | close midpoint − recommendation-time executable ask | Would a taker have beaten the closing consensus at the quoted price? **Pre-fee**, includes half-spread |
| **Actual fill CLV** | close midpoint − quantity-weighted **actual fill price**, fee-exclusive | Was real execution better/worse than the closing consensus? **Pre-fee**, includes execution slippage and spread |
| **Fee-adjusted entry difference** | actual fill CLV − actual exchange entry fees ÷ contracts | Execution economics, **fee counted once** (not pure market-movement CLV) |

All prices are per contract. For NO, normalize both opening and closing quotes to NO prices; do not subtract unlike YES/NO axes. A closing bid (hypothetical liquidation) is a **fourth** metric, not interchangeable with closing midpoint, and a modeled exit must treat actual/hypothetical exit fees explicitly.

## Current NFL implementation caveat

`nfl_edge/evaluation/clv.py` already publishes `clv_mid_toward_model` (selection-like), `clv_exec_toward_model` (hypothetical horizon **ask**, **not actual fill**), and `clv_net_of_fee` (a **modeled entry fee**, not verified real-account P&L). The chosen side is the frozen **model-preferred** side, not necessarily the side of a real wager. Never present its last two metrics as **actual** executed CLV or its model-side CLV as **verified user bet selection CLV** until matched to a timestamped recommendation and real fill.

The real-account router records raw VWAP price, contract count, actual exchange fee, and total cash consumed separately. A subsequent **verified** wager-level join must match recommendation side + market ticker + recommendation timestamp to order fill(s), then to a pre-start closing market quote with source/time and stable spread/quality rules. Missing or ambiguous joins must remain unverified.

## Regression case: 50¢ / fee-inclusive UI 51.7¢ / market still 50¢

- Selection CLV **0.0¢** for unchanged midpoints.
- Actual pre-fee fill-to-close midpoint CLV **0.0¢**, if raw VWAP is confirmed as 50¢.
- Fee-adjusted difference **minus actual fee per contract**.
- Never call the `51.7¢ - 50.0¢` *fee-inclusive cost-basis difference* adverse **market movement**.
- Never subtract the same fee again from an already fee-adjusted number or a cash-spent P&L.

See `tests/test_clv_fee_basis_invariants.py`. This test guards the existing **NFL shadow calculation**; it does not alone certify backfilled cross-sport real-wager reports. Historical audits must separately validate the quote source, recommendation-to-fill linkage, and settlement accounting.
