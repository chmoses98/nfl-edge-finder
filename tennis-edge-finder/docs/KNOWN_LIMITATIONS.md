# Known limitations (2026-09-11)

## Blocked / external
* **Sandbox egress**: kalshi.com, docs.kalshi.com, api.elections.kalshi.com, tennis-data.co.uk, atptour.com,
  wtatennis.com, itftennis.com, sofascore/flashscore, wikipedia, GitHub raw content for other repos are all
  denied. Every network step runs on GitHub Actions and lands on the `tennis-data` branch.
* **Upstream Sackmann repos 404**: `JeffSackmann/tennis_atp` and `tennis_wta` were unavailable; data comes from
  public forks (`Kadantte/tennis_atp` max season 2026; `VictorSquidWei/tennis_wta` max season 2026 but WTA
  rows end 2026-04-27). Fork freshness must be re-checked on every bootstrap (manifest `max_season_file`,
  TENNIS-14).
* **tennis-data.co.uk 503** for every request from the runner: ATP 2020-2026 workbooks came from a mirror;
  WTA odds benchmark absent; ATP 2000-2019 odds absent.
* **No first-ball timestamps** anywhere (Kalshi exposes scheduled start and close time only). Strict pregame
  evaluation and executable CLV need a live-score feed; until then closes are SCHEDULED_MINUS_MARGIN.
* **No draw feed**: tournament winner / round advancement markets are parsed but not priced live.
* **Kalshi fee coefficients** (0.07 taker, 0.0175 maker) are from the published schedule as recorded in the
  sibling NFL project, not byte-verified tonight (kalshi.com unreachable).
* **Contract-terms PDFs** downloaded (286) but not parsed; settlement rules come from `important_info` text
  (25 series) and observed settlements.

## Modelling
* Elo and the structural model are **worse than Pinnacle** on every cut (Brier gap ~0.014 and ~0.011; ensemble
  ~0.008). The walk-forward hybrid gives the model a small negative weight. There is no evidence of edge.
* Ratings ignore rest/fatigue/travel/form features (not yet ablated), injuries/withdrawals, court speed,
  indoor/outdoor beyond surface, altitude, weather.
* Serve/return abilities exist only where Sackmann serve stats exist (tour level + some Challengers);
  ITF/WTA-lower projections are Elo-only and flagged by data quality.
* Elo overconfidence: calibration slope ~0.83-0.89 on tour matches for K=180-250; the ensemble is ~1.05.
* Retirement mass is not modelled in derivative pricing (totals/spreads priced on completed-match
  distribution); the exchange settles determined markets and fair-prices the rest.
* Doubles: baseline prior only, unvalidated, not wired to live pricing.
* Cross-source id systems (Sackmann vs TML) are not linked; production uses Sackmann ids only.
* 2020 season gap (COVID) and partial 2025-26 ITF coverage in the forks.
* Same-surname Kalshi events (dup-digit tickers) and 19 events whose derivative-only markets lack both
  full names are excluded from projection (listed in the coverage report).

## Operations
* Scheduled crons cannot run from a non-default branch: capture continuity relies on the self-dispatching
  conductor (`tennis-capture.yml`); a failed dispatch stops the chain. Moving the workflows to the default
  branch enables plain `schedule:` triggers.
* First 5.7 h of capture (06:57-12:38 UTC) were lost to the >100 MB file rejection (fixed: gzip + shards).
* The projection pipeline uses discovery-time quotes when no capture quotes exist; quotes can be hours old.
