# Confirmed-starter quarterbacks (point-in-time gate input)

The card's `game_level_pit_evidence` gate blocks every game-level score market (game winner, spread, total, team total, 1Q/1H)
unless **both** quarterbacks of the game are `CONFIRMED_STARTER` with a time. This is the only way a quarterback becomes confirmed.
Player props are not touched by this rule.

## What counts

A source that **names the starting quarterback**, announced before kickoff:

| `source_type` | meaning |
|---|---|
| `TEAM_OFFICIAL_ANNOUNCEMENT` | the team states who starts |
| `HEAD_COACH_STATEMENT_ON_RECORD` | the head coach states who starts, on the record |
| `NFL_OFFICIAL_LINEUP_NAMING_STARTER` | an official lineup that literally names the starter |

These do **not** confirm, whatever status a record claims, and are rejected if they try:
`DEPTH_CHART`, `SLEEPER_DEPTH_CHART`, `ACTIVE_ROSTER`, `SLEEPER_ACTIVE`, `ESPN_ROSTER_ACTIVE`, `INACTIVE_LIST`, `INJURY_REPORT`,
`MODEL_EXPECTATION`. They may record `EXPECTED_UNCONFIRMED`, `OUT` or `UNKNOWN`, so the evidence is visible and a declared-out
quarterback blocks.

## There is no automated feed

`nfl_edge/availability_pit` stores injuries and ESPN per-event *active* flags with our retrieval time. Those are inactive-list
evidence ("NOT certified and nothing reads it as availability"); nothing fetched automatically names a starter. So confirmations
are **human-attested**: someone records what a named source said and when. The validator checks shape, allowlist, clock and
conflicts; it cannot check that the source said it. Until someone records a confirmation, every game is blocked `QB_UNKNOWN`, and
RUN NFL says so.

## Recording one

Actions -> **NFL QB confirm** (owner only), or locally:

```bash
python3 scripts/handicap/qb_confirm_append.py --ledger-dir qb/qb_confirmations --packet <packet.json> \
  --game-id 2026_09_SF_ATL --team SF --qb-player-id <gsis id> --status CONFIRMED_STARTER \
  --source-type HEAD_COACH_STATEMENT_ON_RECORD --source-ref <url> --observed-at 2026-11-04T18:30:00Z --captured-by owner
```

Append-only ledger on the orphan branch `qb-confirmations` (`qb_confirmations/<season>.jsonl`); the workflow creates the branch on
first use. Re-submitting the same assertion is a no-op. A change of mind is a new record with `--supersedes <record_id>`.
Refused (nothing written): bad status/source, a depth chart claiming `CONFIRMED_STARTER`, naive or garbled timestamps, observed
after captured, observed in the future, game/team not in the packet, capture at or after kickoff.

## How a record is used

At the card's decision time `T` and the game's kickoff `K`:

1. only records **captured** at or before `T` and before `K` are visible;
2. the **latest observation** for the team and game decides, so a later `OUT` / `EXPECTED_UNCONFIRMED` withdraws a confirmation;
3. two `CONFIRMED_STARTER` records for different quarterbacks **conflict** (`UNKNOWN`) unless the later one `supersedes` the earlier;
4. a confirmation older than `CONFIRMATION_MAX_AGE_MIN` (48 h, owner-adjustable) is **stale** (`UNKNOWN`);
5. a team with no usable record is absent -> `QB_UNKNOWN:<team>`; otherwise `QB_NOT_CONFIRMED:<team>`.

## Where it is wired

* `.github/workflows/nfl-thesis-card.yml` fetches the ledger (if the branch exists) and passes `--qb-confirmations qb/qb_confirmations` to
  `scripts/handicap/run_card.py`. No branch = no source = fail closed.
* `.github/workflows/run-nfl.yml` reports, per slate, how many games have both quarterbacks confirmed (step summary + a small
  `qb-coverage-*` artifact). It never edits the hash-pinned packet and never fails the run.
* `run_card.py` writes `qb_coverage.json` (counts only) beside `card.json`.

The workflows read `main`, so none of this takes effect until it is merged.
