"""Kalshi fee semantics, taken from captured series metadata rather than assumed.

`config/kalshi_nfl_series.json` records each series' `fee_type` and `fee_multiplier` as the API reports them.
Across 392 NFL series there are exactly two regimes:

    quadratic                   367 series   taker fee only
    quadratic_with_maker_fees    25 series   taker fee AND a maker fee

That distinction is not cosmetic. The 25 maker-fee series include **every headline NFL market**:
KXNFLGAME, KXNFLSPREAD, KXNFLTOTAL, KXNFLANYTD, KXNFLFIRSTTD, KXNFL2TD. The 98 fee-free
FULL_MICROSTRUCTURE series are the period and quarter derivatives. So a passive strategy on the markets this
project actually studies does **not** get free entry.

The taker formula is Kalshi's published quadratic, ceil(0.07 * C * P * (1-P)) to the cent. The **maker fee
coefficient is not present in the captured metadata** -- only the fee_type is. It is therefore carried as an
explicit, overridable parameter with a documented default and an `uncertain` flag, and every study that uses
it reports results at more than one value rather than pretending one is known.
"""
from __future__ import annotations

import json
import math
import os
from dataclasses import dataclass

TAKER_QUADRATIC_COEF = 0.07          # Kalshi published: ceil(0.07 * C * P * (1-P))
# Kalshi's published maker fee where it applies. NOT present in the captured series metadata, so it is
# treated as uncertain and swept rather than trusted.
MAKER_FEE_PER_CONTRACT_DEFAULT = 0.0025
MAKER_FEE_SWEEP = (0.0, 0.0025, 0.005, 0.01)


@dataclass
class FeeSchedule:
    fee_type_by_series: dict
    maker_fee_per_contract: float = MAKER_FEE_PER_CONTRACT_DEFAULT
    maker_coefficient_is_uncertain: bool = True

    def charges_maker_fee(self, series_ticker: str) -> bool:
        return self.fee_type_by_series.get(series_ticker) == "quadratic_with_maker_fees"

    def fee_type(self, series_ticker: str) -> str | None:
        return self.fee_type_by_series.get(series_ticker)

    def taker_fee(self, price: float, contracts: float = 1.0) -> float:
        if price is None or not (0 < price < 1):
            return 0.0
        return math.ceil(TAKER_QUADRATIC_COEF * contracts * price * (1 - price) * 100) / 100.0

    def maker_fee(self, series_ticker: str, contracts: float = 1.0,
                  per_contract: float | None = None) -> float:
        if not self.charges_maker_fee(series_ticker):
            return 0.0
        rate = self.maker_fee_per_contract if per_contract is None else per_contract
        return rate * contracts

    def describe(self, series_ticker: str) -> str:
        t = self.fee_type(series_ticker)
        if t is None:
            return f"{series_ticker}: fee type UNKNOWN -- treat results as unflagged"
        if t == "quadratic":
            return f"{series_ticker}: taker quadratic, NO maker fee"
        return (f"{series_ticker}: taker quadratic AND maker fee "
                f"(coefficient uncertain, default {self.maker_fee_per_contract:.4f}/contract)")


def load_fee_schedule(root: str, maker_fee_per_contract: float | None = None) -> FeeSchedule:
    path = os.path.join(root, "config", "kalshi_nfl_series.json")
    d = json.load(open(path))
    recs = d.get("series", d)
    items = recs.items() if isinstance(recs, dict) else [(r.get("ticker"), r) for r in recs]
    by = {k: v.get("fee_type") for k, v in items if isinstance(v, dict)}
    fs = FeeSchedule(fee_type_by_series=by)
    if maker_fee_per_contract is not None:
        fs.maker_fee_per_contract = maker_fee_per_contract
    return fs
