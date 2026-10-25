# Moving the owner's wager ledger out of public view (option, not performed)

## Status (verified 2026-10-25)

`chmoses98/nfl-edge-finder` is **public**. Its `handicap-data` branch is readable without credentials (`raw.githubusercontent.com/.../handicap-data/README.md` -> 200) and holds, as one JSON
file per record: **209** `imported_wagers` (actual price, contracts, fees, execution time), **209** `wager_settlements`, **18** `wager_settlement_amendments`, 1 `import_receipts`, 2 `executions`.
`postmortems` (2) on `handicap-data`, and the actual-wager postmortems on `market-data`, may carry stakes and P&L. The owner's P&L is therefore publicly reconstructable today. Nothing in
this change makes that worse: the new diagnosis publishes ratios and counts only, the card redacts owner positions, and no workflow log prints a stake or price.

## What was built and tested (no migration was performed)

* `nfl_edge/handicap/ledger_privacy.py` + `scripts/handicap/plan_private_ledger.py` (tests: `tests/test_private_ledger_plan.py`, 5 tests).
  * `plan`: classifies each record kind (OWNER_PRIVATE / REVIEW / PUBLIC_OK), counts files, and prints a sha256 manifest hash (paths and hashes, never contents).
  * `--copy-to <checkout of a PRIVATE repo>`: copies the OWNER_PRIVATE kinds only, verifies every file by hash, writes `MIGRATION_MANIFEST.json`. It refuses a target it cannot show is private
    (GitHub API on the checkout's origin; `--allow-local-target` is for scratch rehearsals), refuses source == target, never modifies or deletes the source, and **never pushes**.
  * Rehearsal against the real ledger into a scratch directory on 2026-10-25: 439 files copied, 0 hash mismatches, source untouched.

## Consumers that must be repointed (before anything is removed from the public branch)

`actual-wagers.yml` (fills/settlements), `preflight.yml` (**an unreadable ledger blocks every approval**), `nfl-thesis-card.yml` (open exposure), `sync-handicap-airtable.yml` (writes), `weekly-research.yml`.
Each checks out `handicap-data` with the default token. A private ledger repository needs a fine-grained PAT (Contents: read, and write for the sync) stored as an Actions secret and passed as
`token:` to those checkouts. The router's delivery of fills must be repointed to the private repository first. Recommendations, evaluations and runs may stay public.

## Reversible sequence (each step independently safe)

1. Owner creates a **private** repository (e.g. `nfl-ledger-private`) and a fine-grained PAT scoped to it; stores the PAT as `LEDGER_PRIVATE_TOKEN` on this repository.
2. Run the planner; run `--copy-to` into a clone of the private repo; review `MIGRATION_MANIFEST.json`; commit and push **by hand**.
3. Repoint the consumers (one PR, tests green) to read the private repository; run the preflight and card workflows once and confirm they read it. Keep the public copy in place meanwhile.
4. Repoint the router delivery so new fills go only to the private repository.
5. Only then, optionally and **irreversibly**: remove the OWNER_PRIVATE kinds from the public branch. Deleting files does not remove them from git history, forks, caches or anyone who already cloned;
   scrubbing history means rewriting `handicap-data` (`git filter-repo`) and force-pushing, and cannot recall copies already taken. If the P&L history itself is the concern, the realistic
   remedy is to treat everything up to the cutover as already public.

The alternative that avoids the whole migration is making the repository private, which breaks anything depending on anonymous reads (the app, ChatGPT's GitHub integration reading dossiers) and
is not recommended while ChatGPT must read the dossiers through GitHub.
