# Wave 2 — Amendment B1, erratum 1: 2026_05_PHI_JAX IS in the 1.1.0 qualification set

**RESEARCH_ONLY. `betting_authority: NONE`.** This erratum corrects a factual sentence in
`PREREGISTRATION_AMENDMENT_B1_A1B_SOURCE.md` (B1.3). It changes no rule, criterion, threshold, set or code.
Amendment B1 itself is not edited.

## The error

B1.3 says that 2026_05_PHI_JAX "kicked off before the start and is outside the set". That is false. The facts:

- B1's qualification start is the committer time of the first-parent `main` commit adding the amendment. That commit
  is merge `c332deb0317a9fcdb169bfb5c5b0a984965bdee3`, at **2026-10-11T13:22:54Z**, as read from git by
  `scripts/sim/a1b_qualify.py`.
- PHI@JAX kicked off at 13:30Z, after that start.
- Under the mechanical rule, it is therefore the **first game of the 24-game set**. The set runs from 2026_05_PHI_JAX
  to 2026_06_ARI_LA (2026-10-18 20:05Z).

## Resolution: the rule governs; the sentence does not

The set is not changed after the fact, so PHI@JAX stays in it. It has no `a1b-source-1.1.0` snapshot in
[T−100, T−35]: all eight of its snapshots are 1.0.0, and those are never re-parsed. It is therefore a certain
failure for the source on:

- QA (1 of 24 games);
- QS and QT for both teams (2 of 48 team-games).

PHI@JAX can only count AGAINST qualifying 1.1.0. The pregame observation of it that informed B1's choice of field
therefore cannot help that field pass.

Recorded 2026-10-11, before any 1.1.0 snapshot of a qualification game has been evaluated.
