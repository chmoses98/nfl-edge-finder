# NFL pre-trade preflight: fast, event-driven, pre-kickoff, replayable

This is the operating description of the **pre-trade leg** after the 2026-09-13 latency incident. The
Airtable transport contract lives in `docs/AIRTABLE_BRIDGE.md`; this document is about how the verdict is
produced, how quickly, and on what evidence.

---

## What went wrong on 2026-09-13

A single real request for `KXNFLSPREAD-26SEP13BALIND-BAL4` (BAL −3.5, YES, ceiling 0.47) failed three
separate ways, and only one of them was visible at the time.

**1. The doorbell did not ring.** The owner opened issue #12 titled

```
PREFLIGHT NFL
```

The workflow's guard required the title to begin `[PREFLIGHT NFL]`. Actions run `34770096817` was created
from the `issues` event and the job was **skipped**. A skipped job is silent by design — that silence is
exactly what makes the guard safe against strangers on a public repository — so nothing told the owner.

**2. The manual repair was slower than the game.** The owner dispatched preflight by hand. Run
`34770222726` started at `16:59:34Z`. The `market-data` checkout began fetching around `16:59:43Z`, finished
fetching around `17:00:40Z`, and wrote ~17,491 files until about `17:01:23Z`. The worker itself did not start
until ~`17:01:25Z`; Airtable was answered at `17:01:30.488776Z`. **Kickoff was `17:00:00Z`.** The pre-trade
control answered after the game had started.

**3. The evidence it read was already nearly stale when it was published.** The newest market-data commit
before the decision was `cde237cce36534d7c4cf959d6b236ca7ef5496e3`, "kalshi capture 2026-09-13T16:56:45Z
(conductor pass 15)" — but that run's id was `20260913T164331Z`. The pass began at `16:43:31Z` and did not
publish until `16:56:45Z`. A nominally ten-minute conductor is ~13–14 minutes end to end, because it polls
the whole series universe and then walks thousands of order books before publishing anything. Preflight
inherits whatever is left of its fifteen-minute window.

The verdict was **`PREFLIGHT_BLOCKED`**, and it was correct: the newest confirmed quote for BAL −3.5 was
17.1 minutes old. The gate did its job.

**But it did its job by coincidence.** Quote freshness answers *"was this price real?"*. It is satisfied by
a four-minute-old capture — which is perfectly compatible with a game that kicked off two minutes ago. One
on-time conductor pass and the same post-kickoff clock would have produced an **approval**.

---

## What the leg does now

```
Airtable PREFLIGHT_REQUESTED
  → owner opens `PREFLIGHT NFL` or `[PREFLIGHT NFL]` (opened OR edited)
  → preflight.yml: checkout main + ledger + SPARSE data/kalshi/fees
  → for each UNIQUE candidate ticker:
        GET /markets/{ticker}                      ← stamped with its real retrieval time
        GET /markets/{ticker}/orderbook?depth=10    ← stamped with its own real retrieval time
  → write that evidence to the append-only `preflight-evidence` branch, commit, push
  → READ IT BACK off the store
  → *** NOW *** stamp the decision instant (approval_as_of)      ← after the evidence exists, never before
  → the existing gates, unchanged, plus decision_before_kickoff
  → stamp answered_at, separately, for observability only
  → PREFLIGHT_APPROVED / PREFLIGHT_BLOCKED in Airtable, signed over the evidence manifest
```

### The decision instant is taken LAST, and that is load-bearing

Every resolver here treats evidence dated after the decision as **invisible** — it is information the
decision did not have. So the order of the two clocks is not cosmetic:

| timestamp | when it is taken | what it is for |
|---|---|---|
| evidence retrieval | by the client, when each response actually arrived | freshness is measured backwards from the decision to this |
| `approval_as_of` | **after** fetch + persist + read-back, immediately before the gates | the decision; `created_at` of every approved record; what the signature covers |
| `answered_at` | after the gates | observability only — nothing is judged at it |

Stamping `approval_as_of` at the top of the row loop — which an earlier draft of this rebuild did — inverts
that rule: the live quote necessarily returns *after* the moment the loop was entered, so every preflight
would block on "retrieved after the approval instant". Fail-closed, and useless.
`_assert_evidence_predates` proves the ordering held rather than assuming it; a violation is an **ERROR**,
not a verdict about the market.

**Target: under 30 seconds request-to-verdict, and materially under 20 in the normal case.**

The capture stream is no longer on the live decision path at all. It keeps its two real jobs — immutable
market history, and the source for anything asking what the market *was* — and neither is changed here.

---

## The three fixes

### 1. The trigger accepts both title forms, and honours edits

Owner-authored issues start the worker when the title begins with **either**

```
[PREFLIGHT NFL]        or        PREFLIGHT NFL
```

case-insensitively (GitHub's `startsWith` has always been case-insensitive; that is recorded rather than
fought). `issues: [opened, edited]` — so correcting a malformed title rings the doorbell instead of
requiring a second issue and another round trip against the clock.

**Nothing about authorisation moved.** `github.event.issue.user.login == github.repository_owner` is the
security control, and it reads the issue's **author**, not whoever edited it. An outsider's issue is refused
with any title; a skipped job never starts, spends nothing and reveals nothing.

The guard exists twice on purpose: as the workflow's `if:` (the only boundary that can stop a job before it
holds a secret) and as `nfl_edge/handicap/preflight_trigger.may_start_worker`.
`tests/test_preflight_issue_trigger.py` evaluates the **actual YAML expression** and asserts the Python copy
agrees on every case, so the two cannot drift.

### 2. `decision_before_kickoff` — an explicit, replayable deadline

A new real-money gate, run first, and a pure function of the record:

| situation | result |
|---|---|
| approval strictly before `kickoff_utc` | PASS |
| approval **exactly at** `kickoff_utc` | FAIL |
| approval after `kickoff_utc` | FAIL |
| `kickoff_utc` missing or unparseable | UNAVAILABLE — which **blocks**, exactly as FAIL does |

Blocker text: `decision_before_kickoff: approval occurred at or after kickoff; a pregame position can no
longer be authorized`.

`gates.pre_kickoff_gate` is called from two places and implemented once: `evaluate_gates` (so the importer
replays it) and `preflight._one` (before structural validation, so a post-kickoff request comes back named
rather than as a schema exception about `minutes_to_kickoff`). It reads `kickoff_utc` and the decision clock
directly — **not** the requester-supplied `minutes_to_kickoff`, which preflight only recomputes when a fresh
quote could be confirmed, so the case that matters most is exactly the one where a stale self-reported figure
would otherwise survive.

### 3. Live, candidate-specific evidence — stored before it is trusted

`nfl_edge/handicap/live_evidence.py` makes **two public, unauthenticated GETs per unique ticker** and builds
one evidence document. It cannot scan a universe: `series_list`, `paginate`, `markets()` and `events()` do
not appear in it, and a test asserts that.

The document embeds two rows shaped exactly like capture rows, so `quotes.resolve_decision_quote` and
`depth.resolve_full_position` — the functions the importer replays — read the live evidence through the same
interface they read the capture stream through. **The gate code did not change.**

Refusals, all of them blocking:

* a failed market fetch, a failed book fetch, an empty book, a response with no retrieval timestamp;
* a market whose status is not `active` / `open` / `initialized`;
* no midpoint is ever produced, and no depth is ever approximated.

---

## The `preflight-evidence` branch

An orphan branch holding **public market data only**. Example path:

```
data/preflight_evidence/2026/week_01/recoeC5wilnbBrvsT/20260913T170123456789Z_KXNFLSPREAD-26SEP13BALIND-BAL4.json
```

Each file holds the market ticker and series, both retrieval timestamps, yes/no bid/ask, market status, the
depth requested and the order book at that depth, the request and run identifiers, SHA-256 of each raw API
body, and the raw bodies themselves. The file's bytes **are** the canonical JSON, so `sha256(file)` is the
document hash with no re-serialisation step in between for anyone to get wrong.

**Never on this branch:** account data, credentials, positions, fills, stakes, theses, probabilities,
bankroll. `tests/test_preflight_evidence.py` scans the written files for every one of those.

**Append-only, and enforced.** Every path carries the retrieval instant and the ticker, so nothing collides.
If a path somehow repeats, identical bytes are an idempotent replay and *different* bytes raise.
`GitBranchEvidenceStore` refuses to publish to any branch but `preflight-evidence`, so the workflow's
`contents: write` grant cannot reach `main`, `market-data` or `handicap-data`.

**Order of operations is the control:**

```
collect → stage → commit → push → READ BACK → verify hash → gate → approve
```

The gates run against the bytes that came back **off the store**, not the ones in memory. An unstorable,
unpushable, unreadable or changed document answers the row `PREFLIGHT_ERROR`, and an errored request is not
an approval.

### The approval names its evidence

`preflight-approval/2` adds one signed field, `evidence_manifest_sha256` — a hash over the sorted
`{path, sha256}` list plus the storage kind and commit. So the HMAC now authenticates *what was approved*,
*when*, **and** *the exact market documents it was computed from*. `preflight-approval/1` still verifies, so
approvals signed before this change still archive; new approvals are only ever issued as v2.

### The delayed importer replays it, and cannot decline to

`sync_airtable.py --preflight-evidence ../preflight-evidence` makes the twelve-hourly importer read the
documents the approval names, re-verify every hash, recompute the manifest and feed it into the signature
check — and then run `evaluate_gates`, the same function, against that evidence.

**There is no fallback.** A `preflight-approval/2` approval is archived against its own evidence or it is
not archived. "The evidence checkout is missing, so replay from the capture stream instead" would re-decide
the bet on different, older market data and call that a reproduction — the exact substitution this whole
mechanism exists to prevent. Preflight prices from a fetch made seconds before the decision; the conductor's
capture of the same contract may be ten minutes older and at a different price.

The two failure classes are kept apart, and neither archives anything:

| what happened | class | effect |
|---|---|---|
| no `--preflight-evidence` root, or a root that lacks the document | `ConfigurationError` | row stays `READY_FOR_SYNC`, nothing written, exit 2. A **runner** problem — it imports unchanged once the checkout is right, so a misconfigured importer cannot destroy a signed recommendation. |
| hash mismatch, substituted document, manifest that does not reconstruct | `BridgeError` | row marked `ERROR`. The evidence is present and wrong; that is not a configuration problem under any reading. |
| `preflight-approval/1` (legacy) | — | no evidence to read; replays from the capture stream as it always did. |

The sync workflow tells apart the only two states that matter: **no `preflight-evidence` branch at all**
(no v2 approval has ever been issued — a notice, and legacy rows import normally) and **the branch exists
but could not be checked out** (a hard error, because a v2 row would otherwise silently defer).

For an ad-hoc check outside the importer:

```bash
python3 scripts/handicap/replay_preflight_evidence.py \
    --result preflight_result.json \
    --approved-payload approved_payload.json \
    --evidence-root ../preflight-evidence \
    --handicap-root ../ledger
```

Exit 0 = the replay agrees; 1 = it disagrees on a deterministic gate; 2 = the evidence could not be read.

---

## Observability

Every run writes a job summary: trigger type, request count, time to load code, time to obtain market
evidence, time to persist it, time in the ledger and gates, time to write the verdict, total
request-to-verdict (measured from **Airtable's own `createdTime`**, which is when the owner actually asked),
and per candidate the minutes to kickoff at approval, the quote age and the book age.

The page carries **no ticker, price, stake, probability or thesis**. The repository is public; the Airtable
row is the only place the verdict and the candidate live.

---

## What was deliberately NOT changed

* `DEFAULT_MAX_QUOTE_AGE_MIN` is still **15**. It is the gate that caught the incident. Widening it to make
  the symptom go away would have made the desk worse; the fix is to give it something fresh to look at.
* `DEFAULT_MAX_BOOK_AGE_MIN` is still **15**.
* Fee validation, full-position depth validation, positive net-EV, and every portfolio limit: untouched.
* No wager is placed. Nothing on this path can reach an order endpoint.
* No account or bet history is written to a public repository.
* Model probabilities are not touched, the handicap is not recomputed. **Preflight refreshes market state.**
* The conductor's capture semantics and its immutable history are unchanged.
* The incumbent research experiment is unchanged.

`tests/test_preflight_no_weakening.py` pins all of the above in one readable file.

---

## Operator: one-time setup

1. `preflight-evidence` needs no manual creation — the store creates the orphan branch on first use.
2. Nothing else changes. `AIRTABLE_TOKEN` and `PREFLIGHT_SIGNING_KEY` are the same two secrets.
3. The preflight workflow now needs `contents: write` (evidence publishing only). This is in the workflow
   file; no repository setting changes.

## Operator: the acceptance test

See "TEST_ONLY end-to-end" in `docs/AIRTABLE_BRIDGE.md`, and the pre-slate rehearsal in the pull request
that introduced this document.
