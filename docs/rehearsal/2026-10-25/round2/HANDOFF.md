# Round-2 handoff (2026-10-25, written ~09:15Z; first kickoff PIT @ NO 13:30Z)

Verdict: **PARTIAL.** The analyst-to-card machinery works end to end in production on real data; stake authorization is blocked until the owner finishes the bankroll delivery; the settlement fix is merged and unit/integration-tested but NOT proven in Actions.

## Verified in production (evidence)
* RUN NFL on main publishes `handicap-reports/latest/dossiers/` (14 `.md`+`.json`, `index.md` in deadline order, `submission_template.json`, `ANALYST_GUIDE.md`). Packet `88c047755ecc20cd4a29`, built 08:25Z.
* Issue #189 (`NFL CARD PLUMBING TEST`, owner-authored) rang `nfl-thesis-card.yml` twice (runs 40169006041, 40170087534), LIVE mode: pinned packet, fetched the contract from the venue, ran the real preflight, replied on the issue.
  Run 1 found a real defect (player-prop record had no `availability_state`; fixed in #190). Run 2: preflight APPROVED the line on a live quote (12c vs 11c priced, inside the 3c tolerance), game disposition `REVIEWED_PRICED_CANDIDATE`, stake authorization **BLOCKED** (no bankroll evidence) so it was a CANDIDATE, the other 12 games `NOT_REVIEWED`. Nothing placed.
* Tests: full suite green in CI on #188, #190, #191.

## Not done / blocked
* **Bankroll**: router PR #114 is open and unmerged. Owner steps: create a fine-grained PAT (only `chmoses98/nfl-edge-finder`, Secrets: read/write), store it in `kalshi-bet-router` as `DOWNSTREAM_SECRETS_TOKEN_NFL`, merge #114, dispatch *Publish bankroll to the NFL desk*. Until then every line is a CANDIDATE.
* **The analyst has not produced a real submission**; 13 games are `NOT_REVIEWED` until ChatGPT files review records. Whether ChatGPT's GitHub integration can read `handicap-reports` files and open/edit issues is the existing assumption of the preflight doorbell; it could not be tested from this session.
* **Settlement (#191)**: dispatched run 40171705899 was cancelled at the 120-minute limit: fetch 15 min, the closes step hit its 30-minute step limit (budget was 15), the following publish step never finished, nothing was published to `market-data`. Logs were not retrievable from this environment (the log host is blocked), so the cause is undiagnosed. Suspects: the parallel projection-index build or the first (always-attempted) closes group at 750 files exceeding runner memory/time. Weeks 5-7 closes remain unrestored; CLV coverage unchanged. Not worse than before (the previous runs were also cancelled), but not fixed. Read that run's log in the Actions UI before changing anything.
* **Privacy**: `handicap-data` is still anonymously readable (209 fills/settlements). Migration planner and guide exist (`PRIVATE_LEDGER_MIGRATION.md`); no migration performed.

## Sunday commands
See `docs/SUNDAY_RUNBOOK.md`.
