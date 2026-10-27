# Analyst guide: from dossier to card

The card never decides which football theses deserve betting consideration. You do. The code prices, challenges and sizes what you submit and refuses what
does not hold; it never invents a shift, a probability or a script.

## For every unstarted game (dossiers/<GAME>.json, one file per game)
1. Read the dossier: team matchup advantages (opponent-adjusted where marked), QB/offensive-line status, availability, environment, scripts, the
   player-market section (measured usage, opponent-allowed production, market ladders) and `contract_families` (how each family can be priced).
2. Write ONE review record in the submission file (`submission_template.json`): `verdict` is THESIS, REJECTED or INSUFFICIENT_DATA, and `coverage` lists the
   evidence ids (the keys of `evidence_index`) you actually used in each category. The check resolves every id against the dossier; a record that cites nothing
   from a category does not qualify and the game is recorded NOT_REVIEWED, exactly as if you had only scanned the markets.
3. `reasoning` is yours: >= 120 characters of why. INSUFFICIENT_DATA needs a named missing/conflicting item (>= 20 characters) and at least one cited id.

## A thesis (only for verdict THESIS)
Start from `thesis_template` in the game's dossier. State the football claim, cite `evidence_ids`, then give SHIFTS as ranges:
* `shift`: full-game home-margin and total shift ranges (points) from the market centre. Prices every derivable full-game contract on both sides.
* `ladder_shifts`: for player-stat, period and alternate ladders: `selector` (family, subject, stat, period), `shift` range in units of the stat (positive = more
  than the market has it), `basis`, `evidence_ids`, `script_results` (WIN/MIXED/LOSE for FAVORITE_CONTROL, COMPETITIVE, UNDERDOG_CONTROL) and `usage`
  (projected_opportunity, recent_usage, role_stability, teammate_context).
* `candidates`: contracts you want priced with a fair range you declare yourself (`fair.low/high` = probability the side you buy wins, with a `basis`).
* `challenge`: fail_modes (>= 2), market_already_priced, matchup_check.
Ranges must be honest ranges. The card widens them by a measured noise buffer and requires a 2.0 cent net edge at the conservative end after fees. A thesis too small to
trade after fees is a PASS; that is a correct outcome.

## Submit
Commit the file to a branch / PR, or paste it into a GitHub issue titled `NFL CARD`; the workflow `nfl-thesis-card.yml` runs only for the repository owner's issues.
