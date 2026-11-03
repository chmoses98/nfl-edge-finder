# Confirmed-starter quarterbacks (point-in-time gate input)

The card's `game_level_pit_evidence` gate decides, per market, whether the quarterbacks must be confirmed, using an **explicit table**
(`nfl_edge/postmortem/qb_dependency.py`, tested by `tests/test_qb_dependency.py`): every family the classifier, packet, derived-fair-value set
and schema recognise has an entry, and **anything not in the table is `QB_GATED`** (unknown fails closed). A quarterback becomes confirmed
only through the record rules below.

## Which markets need which quarterbacks

| classification | requirement | families |
|---|---|---|
| `QB_GATED` | **both** teams' QBs `CONFIRMED_STARTER` | game winner, spread, total, team total and every alternate rung; 1H/2H/quarter winner, spread, total, team total, both-teams-score, period TD, half/full-time; winning-margin bucket; both-teams-score-N; race-to-N; total TD count; first-TD team and time; team stats (yards, first downs, TD, FG, sacks, turnovers); game stats (TD, FG, sacks, turnovers, longest reception/TD, shortest TD); game events (overtime, safety, lead changes, 2-pt, 4th-down, comeback, scoreless quarter, non-QB pass, defensive TD, ...); combos and parlays; a quarterback's passing yards/TDs/attempts/completions/interceptions; fantasy points (position unknown); head-to-head passing, receiving and fantasy; game leaders in anything but rushing; any season/week/event-scoped contract (outside RUN NFL's single-game scope); **any family or statistic not in the table** |
| `QB_INDIRECT` | the **player's own team's** QB `CONFIRMED_STARTER` (both when the team cannot be read from the ticker) | receptions, receiving yards, rush+rec yards, longest reception, anytime / 2+ / first / next touchdown scorer. Rationale: the projection layer already treats these as quarterback-dependent and abstains when the QB is uncertain (`context/qb_resolution.is_qb_dependent`); a ticker has no position, so a scorer prop is treated as pass-catcher exposed. The opponent's QB is second-order and not required |
| `NOT_GATED` | none (the player-availability gate and every other gate still apply) | running-back rushing yards/attempts, longest rush, defender tackles/sacks, kicker field goals, longest field goal, head-to-head rushing, rushing-yards/TD game leader |

Known residual gap: a quarterback's *rushing* prop is indistinguishable from a running back's in a ticker and is `NOT_GATED`.
Known card limitations seen while testing (not changed here): period both-teams-score and period-TD series have no fee-schedule entry, so the card
cannot price them (net edge unknown) and they never become a line; a `FIRST_TD_SCORER` record is refused by the schema before any QB rule because the
card only writes the availability state for `PLAYER_STAT`.

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

## Why there is still no automated adapter (2026-11-03 research, stated exactly)

Reachability was tested from the build sandbox, whose egress policy allows GitHub-hosted data only:

| candidate | reachable from the sandbox | what it would provide | counts as confirmation? |
|---|---|---|---|
| nflverse `depth_charts_<season>.csv` (GitHub release) | yes (HTTP 200) | weekly depth-chart rows | **no** - a depth chart, rejected by rule |
| nflverse `injuries_<season>.csv` (GitHub release) | yes (HTTP 200) | `report_status`, practice status | **no** - an injury report, rejected by rule |
| ESPN site / core API | no (`CONNECT tunnel failed, response 403`) | unknown: pregame payload shape never inspected | undetermined |
| Sleeper `players/nfl` | no (403) | depth-chart order, active flag | **no** - rejected by rule even if reachable |
| nfl.com game center / api.nfl.com | no (403) | unknown | undetermined |

Nothing that was reachable names a starter, and for the rest the payload shape has not been seen. Writing a parser for an
unseen payload would be inventing a schema, so none was written. `scripts/handicap/qb_source_probe.py` (workflow
`qb-source-probe.yml`, dispatchable only after merge) asks the unreachable sources, from a GitHub runner, whether any field
looks like a starter designation, and reports key paths and counts only. If it finds one, an adapter is justified and must
still obey the rules above: names the starter, observed before kickoff, with source reference and timestamps. Until then the
human-attested intake below is the only path, and unknown stays `QB_UNKNOWN`.

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

## How a record is used (game-specific validity)

At the card's decision time `T` and the game's kickoff `K`, for one `game_id` and one of that game's two teams:

1. only records for **that game_id and that team**, **captured** at or before `T` and before `K` (hence observed before both), are visible; a
   record for another game, or for a team that is not playing, confirms nothing; history is judged at the stated `T`, never at the wall clock;
2. only the allow-listed sources can confirm (never a depth chart, roster, inactive list, injury report or model; the gate re-checks the source);
3. the **latest observation** decides, so a later `OUT` / `EXPECTED_UNCONFIRMED` / `UNKNOWN` **withdraws** a confirmation
   (`WITHDRAWN_BY_LATER_OUT` / `WITHDRAWN_BY_LATER_RECORD`); on an exact observed-time tie the restrictive record wins;
4. two `CONFIRMED_STARTER` records for different quarterbacks **conflict** (`CONFLICTING_CONFIRMATIONS`, `UNKNOWN`) unless the later one `supersedes` the earlier;
5. **two freshness clocks**, both must hold (owner-adjustable constants in `qb_confirmations.py`, both only ever block):
   * `MAX_AGE_AT_DECISION_MIN` = **24 h**: observed no more than 24 h before `T`, else `STALE_CONFIRMATION`;
   * `MAX_LEAD_BEFORE_KICKOFF_MIN` = **48 h**: observed inside the last 48 h before `K`, else `OBSERVED_TOO_EARLY_BEFORE_KICKOFF`.
   Why: a starter can change through the final injury-report week (designations are final the Friday before a Sunday game; official inactives
   come about 90 minutes before kickoff). A statement older than two days predates the news that can still change it, and one older than a day
   at the decision has had a full news cycle to go stale. This replaces the old blanket 48 h age, which let a Thursday statement stand for a
   Sunday decision. A same-day re-confirmation (a coach's Saturday/Sunday statement, the team's lineup) is the way to a bet; the intake script takes it;
6. a team with no visible record is absent -> `QB_UNKNOWN:<team>` (nothing to cite); otherwise `QB_NOT_CONFIRMED:<team>` plus
   `QB_REASON:<team>:<reason>`, and the gate evidence and the stored record carry the provenance (`record_id`, `source`, `source_ref`,
   `observed_at`, `captured_at`, `as_of`, `kickoff_utc`, `game_id`, `team`, the windows, conflicting / withdrawn record ids).

## Where it is wired

* `.github/workflows/nfl-thesis-card.yml` fetches the ledger (if the branch exists) and passes `--qb-confirmations qb/qb_confirmations` to
  `scripts/handicap/run_card.py`. No branch = no source = fail closed.
* `.github/workflows/run-nfl.yml` reports, per slate, how many games have both quarterbacks confirmed (step summary + a small
  `qb-coverage-*` artifact). It never edits the hash-pinned packet and never fails the run.
* `run_card.py` writes `qb_coverage.json` (counts only) beside `card.json`.

The workflows read `main`, so none of this takes effect until it is merged.
