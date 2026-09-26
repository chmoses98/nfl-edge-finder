# Addendum 1 to ACCOUNTING_POSTMORTEM.md: the exchange-reported verb on the cashout

Recorded 2026-09-26 after the postmortem was merged. That document is append-only and is not edited; this file
supersedes only the limitation bullet about the buy/sell verb.

- `BUY*` in its transaction ledger is the replay's default label, used because no filed record stored the verb.
- kalshi-bet-router's first production delivery after #94 showed that the exchange REPORTED order #6 (the Love 275
  cashout at 02:43:34Z, 91.41) as `action=sell`. The same is true for the week-2 KC-5 (1,794.08) and CLE/TB 1H
  total (246.08) cashouts.
- Their filed side (NO) is the exposure. Evidence: a single public trade at the same second with the same count and
  price, taker direction NO; a fee equal to the taker formula to the cent; and the owner's own account. The
  position math, the episode count, entry CLV and every P&L figure in the postmortem are unchanged.
- #94 derived the side from the legacy verb rule (sell-NO means toward YES). That produced CONFLICTs on those three
  filed records, and #96 withdrew it. The router now sends the verb only as evidence (`execution_action`). Kalshi's
  sell sign convention remains an open question for the router's accounting engine (`accounting/position.py`).
