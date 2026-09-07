# Operations

> The decision standard — what a real recommendation must satisfy, and the vocabulary for prices, fees and
> P/L — is [`DECISION_STANDARD.md`](DECISION_STANDARD.md). This file is how the machinery is run.

## Workflows (GitHub Actions, public repo → free minutes)
| workflow | trigger | purpose | output branch |
|---|---|---|---|
| Kalshi NFL Capture Conductor | hourly cron `7 * * * *` + dispatch | loops capture every 10 min for ~5h50m on one runner, hands off to the queued successor | `market-data` |
| Kalshi NFL Capture | dispatch only | single capture pass (manual / external scheduler) | `market-data` |
| Kalshi NFL Discovery | daily 09:17 UTC + dispatch | catalogue refresh, all NFL markets in every status (settlements), endpoint probes; proposes registry additions | `market-data` |
| Kalshi NFL Historical Backfill | dispatch (self-chains) | historical tier market lists + candles + trades | `market-data` |
| Sync handicap runs from Airtable | 12-hourly cron `23 */12 * 9-12,1-2 *` + dispatch | ingests ChatGPT recommendation batches from the `Sports Betting Bridge` Airtable inbox into the immutable ledger | `handicap-data` |

Manual dispatch from the GitHub UI or API (`POST /repos/chmoses98/nfl-edge-finder/actions/workflows/<file>/dispatches`).
Check health: `git fetch origin market-data && git worktree add /tmp/md origin/market-data && python scripts/ops/health.py --market-data-dir /tmp/md`.

## Failure modes and responses
* `partial=true` in a capture manifest → a series fetch failed; the universe for that run is incomplete. Rows are still valid; do not treat missing tickers as closed.
* 429s in `client_stats` → lower `--rps` (default 4) or reduce `--max-books`.
* Publish conflicts (exit 3) → concurrent writers; the next pass retries. Never force-push `market-data`.
* Conductor gap > 20 min with no manifest → dispatch the conductor manually; check GitHub status.
* Registry `proposed_additions` non-empty after discovery → review and move to `series` with a tier.
* Airtable bridge row stuck at `READY_FOR_SYNC` → a transient failure (Airtable or push); the next scheduled run (within 12h) retries. Nothing to do — or dispatch the workflow manually if you want it now.
* Airtable bridge row at `ERROR` → a permanent payload problem; the run log names the field. Fix by creating a **corrected new row**, never by editing the failed one. See `docs/AIRTABLE_BRIDGE.md`.
* Bridge reports a CONFLICT → a recommendation id already exists with different content. Records are immutable; revise with a new id carrying `amends`.
* nflverse 2026 files 404 → expected until the season starts; the downloader records the 404 in the manifest.
* Bridge reports a **GATE FAILURE** → a real recommendation did not survive the decision-time checks: the price went stale, the live ask rose above the stated ceiling, transaction costs were unknown, availability was unresolved, or the portfolio limit bound. The log names the gate and the evidence. This is the system working; the fix is a corrected new row, not a retry.
* Bridge reports **"no gate context was supplied"** → a misconfiguration on the runner, almost always `--market-data` pointing at a directory that is not a `market-data` checkout. The batch is refused rather than written ungated.

## Audit trail: the git history IS the scientific record

`handicap-data` is only worth anything if no recommendation was ever edited after the fact — and the tree
looks identical either way. Three lines of defence, in order of strength:

1. **Application** — `schema.write_record` refuses to overwrite an existing path. Constrains code that goes
   through it, and nothing else. A `git commit --amend`, a force-push or a hand-edited JSON file all bypass it.
2. **Server-side ruleset** — the only real prevention. **Must be configured manually on the GitHub account**
   (see below). It was not applied from a Claude Code session: this environment cannot read or write
   repository protection settings, so its current state is **UNVERIFIED** and should be checked and applied by
   the owner.
3. **Detection** — `scripts/handicap/verify_append_only.py` reads the actual commit history and fails if any
   immutable record was modified, deleted or renamed. Catches what line 2 was not there to prevent.

```bash
git fetch origin handicap-data && git worktree add /tmp/hd origin/handicap-data
python3 scripts/handicap/verify_append_only.py --handicap-root /tmp/hd
```

### The ruleset to apply

Repository → Settings → Rules → **New ruleset**, targeting `handicap-data` and `market-data`:

| setting | value | why |
|---|---|---|
| Restrict deletions | **on** | the branch is the record |
| Block force pushes | **on** | a force-push is how history gets rewritten silently |
| Require linear history | off | the bridge merges the base branch on conflict; a merge commit keeps checkouts valid |
| Require pull request | off | the sync workflow pushes append commits directly and must keep working |
| Bypass list | empty | including for admins — an owner-only bypass is still a bypass |

Equivalent via the API (owner PAT with `administration:write`):

```bash
gh api -X POST repos/chmoses98/nfl-edge-finder/rulesets \
  -f name='ledger-append-only' -f target=branch -f enforcement=active \
  -f 'conditions[ref_name][include][]=refs/heads/handicap-data' \
  -f 'conditions[ref_name][include][]=refs/heads/market-data' \
  -f 'rules[][type]=deletion' -f 'rules[][type]=non_fast_forward'
```

`non_fast_forward` is the force-push block; `deletion` is the branch-deletion block. Neither restricts the
normal append commits the workflows make.

Verify afterwards with `gh api repos/chmoses98/nfl-edge-finder/rulesets`, and record the result in this file.

## Data retention
`market-data` is append-only. Compaction (per-day JSONL → parquet) is planned once a week of data exists; raw JSONL stays as the immutable record.

## Not automated on purpose
Order placement, portfolio access, model promotion, registry tier changes, and **repository protection
settings** (see above — applied by the owner, verified by `verify_append_only.py`).

## Fee-metadata drift

`config/kalshi_nfl_series.json` records each series' fee regime as the API reported it *when the registry was
built*. A Kalshi fee change makes every net-EV number computed from it wrong, in the direction that makes
trades look better than they are.

```bash
python3 scripts/kalshi/capture_fee_metadata.py --out /tmp/md --check
```

Exit 1 means the live metadata disagrees with the committed registry. Review the diff, commit an updated
registry, and do **not** record a real recommendation against a fee regime we know we are no longer
modelling. The script never edits the registry itself.
