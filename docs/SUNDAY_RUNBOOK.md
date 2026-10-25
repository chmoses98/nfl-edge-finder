# Sunday runbook (NFL card)

All steps read and compute; nothing places a bet. The owner places bets by hand.

1. **Fresh packet + dossiers.** Actions -> *RUN NFL* -> Run workflow (`force_fresh` true). ~20-30 min. It publishes `handicap-reports/latest/` (packet, analysis shards) and
   `latest/dossiers/` (`<game>.md`, `<game>.json`, `submission_template.json`, `ANALYST_GUIDE.md`, `index.md`). The packet sha is in `latest/manifest.json` and in the commit message.
2. **Analyst (ChatGPT) research.** For EVERY unstarted game read `dossiers/<game>.md`, then write ONE submission file following `submission_template.json` (a review record per game; theses for games with a
   defensible view; `INSUFFICIENT_DATA` with a named gap when the research cannot be completed). Start with the 9:30 ET game (PIT @ NO, 13:30Z).
3. **Submit.** Open an issue titled `NFL CARD <anything>` in `chmoses98/nfl-edge-finder` whose body contains the submission as a ```json block (a long file may be posted as a later comment from the same
   account; the last valid block wins). Only issues/comments authored by the repository owner are read.
4. **Card.** `nfl-thesis-card.yml` runs on that event (or Actions -> *NFL thesis card* -> Run workflow with the issue number) and replies on the issue with the card:
   BET (preflight-approved **and** stake-authorized), CANDIDATE (priced, not authorized), PASS/REJECTED, INSUFFICIENT_DATA, NOT_REVIEWED, per game. Edit the issue to re-run after fixing the file.
5. **Inactives (about 90 min before each kickoff).** Questionable players keep their decisions OPEN (C5) until then. Re-run RUN NFL for a fresh packet, re-read the affected games, update the submission (new `packet_sha`),
   edit the issue. The 9:30 game is run first and alone; later games follow their own inactive lists.
6. **Stakes.** Authorization needs the router's available-cash delivery (`KALSHI_BANKROLL_CONTEXT`, <= 30 min). One-time owner setup: create the fine-grained PAT, store it in `kalshi-bet-router` as
   `DOWNSTREAM_SECRETS_TOKEN_NFL`, merge router PR #114, dispatch *Publish bankroll to the NFL desk*. Until then every line is a CANDIDATE saying "NO STAKE AUTHORIZATION".

Local equivalents: `python3 scripts/handicap/build_dossiers.py ...`, `python3 scripts/handicap/run_card.py --reports-dir ... --submission ... --mode REHEARSAL|LIVE [--live-evidence]` (see `docs/NFL_OPERATING_POLICY.md` section 3).
