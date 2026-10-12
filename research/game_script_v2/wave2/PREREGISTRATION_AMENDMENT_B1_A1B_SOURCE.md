# Wave 2 — Amendment B1 to addendum B (A1B): source candidate 1.0.0 closed, candidate 1.1.0 preregistered

**RESEARCH_ONLY. `betting_authority: NONE`.** Addendum B (`PREREGISTRATION_ADDENDUM_B_A1B.md`, sha256 `b1f153cd…`)
is unchanged and stays frozen. This amendment does not change any criterion, threshold or set of addendum B. Instead
it does two things:

- It closes addendum B's source candidate (`a1b-source-1.0.0`).
- It preregisters a NEW candidate (`a1b-source-1.1.0`), which gets a fresh qualification set of its own.

Committed 2026-10-11, before any 1.1.0 snapshot exists. A1 (the frozen Wave-2 arm) and every A1 record are
untouched.

## B1.1 What was observed (pregame data only; no projection, outcome or postgame list was read)

The first live A1B game was 2026_05_PHI_JAX (kickoff 2026-10-11 13:30Z, ESPN event 401872981). It produced 8
write-once snapshots on market-data under `data/research/wave2_a1b/sources/2026-10-11/`, retrieved by this
repository about every 12 minutes:

| retrieved (our clock) | T− (min) | roster endpoint | entries (PHI / JAX) | `active == true` | `didNotPlay == true` (PHI / JAX) |
|---|---|---|---|---|---|
| 11:02, 11:14, 11:26 | 148–124 | HTTP 404 | – | – | – |
| 11:38 | 112 | 200 | 55 / 55 | 0 | 0 / 0 |
| 11:50 | 100 | 200 | 58 / 56 | 0 | 0 / 0 |
| 12:02, 12:14, 12:30 | 88–60 | 200 | 58 / 56 | 0 | **7 / 7** |

Reading these results:

- **The `active` flag named in addendum B is not a game-day signal.** It is `false` for EVERY roster entry before
  kickoff. The 1.0.0 parser therefore read 55–58 "inactives" per team. It failed closed (`IMPLAUSIBLE`), and at
  T−45 the capture wrote a counted `NO_USABLE_SOURCE` / `NOT_PUBLISHED_OR_IMPLAUSIBLE` record. That record
  (`records/2026-10-11/2026_05_PHI_JAX.A1B.20261011T124501Z.a1b.json.gz`) stays exactly as written. It is never
  re-read or relabeled.
- **`didNotPlay` behaves like a game-day inactive list.** The same response carries a `didNotPlay` boolean on every
  entry. It was `true` for no one at T−112 and T−100, and for exactly 7 players per team from T−88 on. That matches
  the NFL's ~T−90 inactive release and the usual 7 inactives.

This is one game, and this amendment does not claim the field is right. Whether the field is accurate is decided
only by the qualification in B1.3, on games that kick off after this amendment.

## B1.2 Candidate 1.0.0 is closed: BLOCKED

`a1b-source-1.0.0` (the `active` flag) is structurally unable to pass QA: no snapshot can be USABLE when every entry
is flagged. It is recorded as **BLOCKED** now, on that structural ground, rather than after 24 games that could not
change the result.

Its snapshots and records stay on market-data as written. They never count toward any qualification or any primary
analysis. They are never re-parsed under 1.1.0: re-deriving an old observation under a new rule is not allowed,
even when the raw bytes would permit it.

## B1.3 Candidate 1.1.0: the `didNotPlay` flag, with a fresh qualification

* **Field.** A player is named inactive only if their roster entry has `didNotPlay == true` (a boolean). The `active`
  flag is ignored.
* **What stays exactly as in addendum B:**
  - the response classes OUTAGE / NOT_PUBLISHED (200 with no one flagged) / IMPLAUSIBLE (outside 4–12, or a flagged
    player without an ESPN id) / USABLE;
  - the windows, the T−100 release floor, the (T−80, T−35] cutoff and T−45 missingness;
  - identity handling and the treatment;
  - the endpoint, the 64-game sample and the scorer (B.3, B.5, B.6).
* **Version gate.** Only snapshots whose `a1b_source_version` is `a1b-source-1.1.0` can be chosen at a capture or
  count in qualification (`nfl_edge/sim/a1b.py`, `current_version`).
* **Qualification start.** The committer time of the first-parent commit on `main` that adds THIS file (the merge
  that puts 1.1.0 on main). It is read from git by `scripts/sim/a1b_qualify.py`, so it cannot be chosen. The
  qualification set is the first 24 games kicking off after it. 2026_05_PHI_JAX, which informed the field choice,
  kicked off before the start and is outside the set.
* **Criteria and thresholds.** QA, QR, QS, QT and QM, with the thresholds of B.4, unchanged, with one clarification
  made before any 1.1.0 snapshot exists:
  - **QR** is evaluable for a team-game only if its last pre-T−110 snapshot is an HTTP 200 response (NOT_PUBLISHED,
    IMPLAUSIBLE or USABLE).
  - An OUTAGE (for example the 404 seen before ~T−115) shows nothing about whether a list already existed, so it no
    longer counts as an "empty early list".
  - This makes QR harder to pass, never easier. The evaluator is `nfl_edge/sim/a1b_qualify.py`, `a1b-qualify-1.1.0`.
* **Decision.** As in B.4 and addendum C: QUALIFIED only if every criterion passes, otherwise BLOCKED.
  - If 1.1.0 is BLOCKED, A1B stays inactive and A1 continues on T24.
  - No further candidate may be preregistered without a new amendment, which would get its own fresh set.

## B1.4 Eligibility and pooling

Eligibility is unchanged from B.5:

- An A1B record counts only if it was captured with `SOURCE_STATUS.json` QUALIFIED and the game kicked off after
  `qualified_at`.
- No record captured under 1.0.0, and no record captured while QUALIFYING, can ever be evidence.
- A1B never pools with A1.

## B1.5 What this amendment does not change

- A1, the Wave-2 preregistration, addendum A, the frozen components (`353541d1…`), `wave2_score.py`, the Wave-1
  README, and every existing record and snapshot.
- Research authority: `research_only: true`, `betting_authority: NONE`.
- Wagering, staking, model weights, market priors, SIFT recommendations, and promotion or activation of any arm.
