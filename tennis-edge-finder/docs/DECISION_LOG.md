# Decision log (2026-09-11 overnight session, UTC)

| time | decision | why | alternative |
|---|---|---|---|
| 06:30 | Build inside the existing `nfl-edge-finder` repo as `tennis-edge-finder/` on the designated branch; reuse its read-only Kalshi client and publish pattern | sandbox cannot reach Kalshi or tennis sites; the repo's Actions runners can | separate local repo with no way to fetch data |
| 06:33 | Use the NFL project's full series-catalogue snapshot to design the taxonomy offline | 13,959-series catalogue already on `market-data` | wait for runner |
| 06:35 | Trigger workflows by pushing a trigger file; later self-dispatch for the capture chain | `workflow_dispatch`/`schedule` need the default branch | push to main (forbidden) |
| 06:46 | Fetch upstream data via codeload zip without git credentials | Actions token leaked into other-repo clones (`could not read Username`) | git clone |
| 07:06 | Discover live forks of the Sackmann repos with the GitHub search API (`fork:true`) and verify season files | upstream `tennis_atp`/`tennis_wta` 404 | hard-code a fork (stale) |
| 07:10 | Add TML-Database and the gmalbert mirror (tennis-data xlsx + TML challenger + odds merges) | tennis-data.co.uk returned 503 to every request | Kaggle (needs auth) |
| 07:15 | Exact DP scoring engine as the pricing core; Monte Carlo only for validation | exact, fast (ms per match), invariant by construction | pure simulation |
| 07:20 | Tag-based Kalshi tennis classification with title/prefix nets and explicit NOT_TENNIS (pickleball) | exchange's own taxonomy is authoritative; silent omission forbidden | regex only |
| 07:25 | Parse payoffs from `rules_primary` and cross-check ticker side codes and `floor_strike` | UI labels are not contracts | ticker-only parsing |
| 07:40 | Capture the GLOBAL trade tape filtered to tennis instead of per-ticker polling | one paginated request covers every tennis trade | per-market polling (10k requests) |
| 12:40 | gzip + shard capture streams; publisher skips > 95 MB | 163 MB candle file rejected every push for 5.7 h | LFS |
| 13:20 | Player ids are strings, one id system (Sackmann) for production ratings; TML rows kept with `id_system` | TML ids are alphanumeric and unlinked; mixed replay duplicated players | fuzzy id merge |
| 13:30 | Production Elo config K0 = 180 + surface pooling; ensemble = logit average with structural | best calibration on the tour-level Pinnacle test; ensemble best Brier | elo_plain (best all-level LL) |
| 13:40 | Kalshi backtest cutoff = min(nominal − 5 min, close − 7 h) | `occurrence_datetime` is not a start time for ITF/Challenger (it falls after close); first test leaked in-play prices | trust occurrence_datetime |
| 13:45 | Pregame policy in `run_tennis`: fresh capture universe, refuse ≤ 5 min to nominal start, flag ITF/Challenger as NOMINAL_UNRELIABLE and never actionable | no first-ball truth | price everything |
| 13:47 | Doubles priced with the singles-Elo baseline, grade capped C, unvalidated | coverage over silence; explicit uncertainty | exclude doubles |
| 13:50 | Report every model beside the market and state "no edge" | Pinnacle and Kalshi beat every model; hybrid weight on model negative | present model-only numbers |
