# Kalshi NFL settlement semantics (evidence-based)

Sources: the contracts' own `rules_primary` / `rules_secondary` text captured 2026-09-04, and 61,068 settled
archived markets from the 2025 season (the historical tier). Implemented in `nfl_edge/settlement/semantics.py`.

## Correction to the 2026-09-04 status report
That report said "inactive players settle props at a fair pre-game price, not NO". **That is wrong.** The
fair-price clause is explicitly conditioned on the player being *active*:

> "If <player> is **active but never takes a snap**, the market settles to the (last) fair market price before
> game start. Once <player> takes at least one snap, even if nullified by penalty, the market settles based on
> <stat> recorded."

An **inactive** player is not covered by that clause and the archive shows those markets settling at $0.00.

## The three branches of a player prop
| branch | settles | archive evidence |
|---|---|---|
| takes ≥ 1 offensive snap | $1 if stat ≥ K else $0 | 30,243 of 30,299 joined 2025 prop rungs |
| **active**, never takes a snap | pregame fair market price (`result="scalar"`) | **348 player markets**, median $0.10, range $0.01–$0.95 |
| **inactive** | $0.00 | zero-snap rungs that did not settle scalar all settled `no` at $0.00 |

The scalar branch is real but rare: 348 of 33,684 settled player rungs = **1.03%**. The economically important
branch is the third one, because a YES holder loses the entire premium when the player is scratched.

Consequence for pricing (`player_prop_contract_value`):

```
contract_value = P(plays) · P(stat ≥ K | plays) + P(active, no snap) · fair_price + P(inactive) · 0
```

with `fair_price` proxied by the contemporaneous market mid. At an event probability of 0.45 a healthy player's
YES contract is worth $0.445 but a Questionable player's is worth $0.331 — a 26% haircut that has nothing to do
with football. **Model event probability and expected contract payoff are stored as separate fields everywhere.**

## Other families (from the rules text)
* **Game winner** — a tie settles **both** sides at $0.50 (8 such markets in the archive = 4 tied games). Postponed
  but starting within 48 h of the scheduled time: stays open and settles on the official result; not started
  within 48 h: settles at a fair price.
* **Period winner (1H/2H/1Q–4Q)** — a tied period settles every team strike NO and the Tie strike YES.
* **First TD scorer** — if the game has no touchdowns, "No Touchdown" settles YES and every player strike NO; the
  active/no-snap fair-price clause also applies to player strikes (132 scalar settlements observed).
* **Spread / total** — full-game markets include overtime; 1H markets count first-half points only; **2H markets
  explicitly exclude overtime**; total-TD markets count overtime touchdowns.
* **Statistic corrections** — the rules do not promise re-settlement after an official stat correction; markets
  finalize 60–120 s after the event (`settlement_timer_seconds`). Treated as a known unmodelled risk.

## Support gate
`settlement_supported(family)` returns False with a reason for families whose rules or model are not established
(race-to-N, half/full result, period TD, game events, team stat ladders, player H2H, next-TD, parlays/combos).
The pricer refuses to write a shadow observation for those, with `support_state=UNSUPPORTED_RULES` or
`UNSUPPORTED_MODEL`.
