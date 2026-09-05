# handicap-data

The **decision** branch. It holds what was decided and what happened, and nothing else.

This branch is deliberately separate from `market-data`:

| branch | holds | write pace |
|---|---|---|
| `market-data` | captures, quotes, the shadow ledger — what the market *did* | machine, every ~10 minutes |
| `handicap-data` | recommendations, executions, evaluations, postmortems — what we *decided* | human/ChatGPT, a few times a week |

Mixing them would put a high-frequency collector in conflict with a human-paced decision log, and would make
it impossible to tell when a decision was recorded from when a price was.

## Layout

```
data/
  recommendations/<season>/week_<NN>/<recommendation_id>.json
  executions/<season>/week_<NN>/<execution_id>.json
  evaluations/<season>/week_<NN>/<evaluation_id>.json
  postmortems/<season>/week_<NN>/<postmortem_id>.json
  runs/<season>/week_<NN>/<handicap_run_id>.json
```

**One record per file.** This is the conflict-avoidance design: two recommendations written minutes apart
touch different paths and cannot collide. There is no shared append-target to serialise against.

## Immutability

A record, once written, is never edited and never deleted.

* Changed your mind? Write a **new** recommendation whose `amends` field carries the original
  `recommendation_id`. The original price, timestamp and reasoning survive exactly as recorded.
* Got a different fill than recommended? That is an **execution** record, not an edit. The recommendation is
  an opinion; the execution is a position.
* Learned something after the fact? That is a **postmortem**, attached by `recommendation_id`.

`nfl_edge/handicap/schema.py::write_record` refuses to overwrite an existing path, so this is enforced rather
than trusted.

## Validation before commit

```bash
python3 scripts/handicap/validate_recommendations.py payload.json                       # dry run
python3 scripts/handicap/validate_recommendations.py payload.json --write \
    --handicap-root /path/to/this/worktree
```

Invalid payloads are refused before anything is written.

## TEST_ONLY

Records carrying `"test_only": true` exist to exercise the pipeline. Every reader excludes them by default,
so they can never contaminate a performance number. They must never be used to represent a real decision.

## What is NOT here

No backfilled history. No reconstructed "what ChatGPT would have said". The ledger begins prospectively; a
retrospective recommendation would answer a question nobody asked and corrupt the one we are actually
running.
