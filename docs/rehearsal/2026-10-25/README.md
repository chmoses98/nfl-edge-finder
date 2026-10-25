# RUN NFL rehearsal: Sunday 2026-10-25 (week 7)

A live-style replay of the `handicap-reports/latest` packet built 2026-10-25T02:13Z (capture 01:41Z), decided at **01:45:47Z** (capture + 4 minutes),
about 11 hours before the earliest kickoff (PIT @ NO, Stade de France, 13:30Z = 9:30 a.m. ET).

* `CARD.md`, `card.json`: the output of `scripts/handicap/run_card.py --mode REHEARSAL` against that snapshot with `theses_wk07.json`
* `theses_wk07.json`: four analyst theses written for the rehearsal. **They are illustrative readings of the packet's data, not validated edges and not
  recommendations.** One is an explicit PASS-by-thesis (TB's quarterback is Questionable until the inactive list), three are shift-range theses that the engine priced. (An earlier snapshot of the same morning had a BAL quarterback source conflict; the later packet resolved it, and that thesis was withdrawn rather than carried forward: a stale PASS is as wrong as a stale bet.)
* `dossier_index.md`: the triage order for all 14 games (the Thursday game has started and is excluded with a reason).

What it proves, and what it does not:

| proved | not proved |
|---|---|
| 14 games discovered, the 13 unstarted ones each ending in an explicit state; the earliest kickoff identified | that any thesis here is right |
| 160 / 154 / 150 contract-sides priced per thesis on one footing; every one rejected with a reason | live preflight against the real book (a replay is not executable; the live path is exercised in `tests/test_card.py`) |
| the outcome is **no bets**: nothing clears 2.0c net edge after fees at the conservative end of the range | that the ladder would size a real edge correctly: it has no corroborated edge to size (see `tests/test_staking_expression_challenge.py`) |

The result is a PASS card. That is the evidence-based answer to these theses, not a failure of the rehearsal.
