# Identity

Names are aliases, never ids.

* **Canonical player id** = Sackmann id (string) for the production rating universe. TML rows carry ATP-site
  alphanumeric ids (a second id system); the builder keeps `id_system` per row and production ratings use
  `sackmann` only, so no cross-system merge is ever implied. A verified crosswalk (name + DOB + country) is
  future work.
* **Registry** (`identity/players.py`): player_id, name_first/last/full, normalised forms, `last_first_initial`
  ("federer r"), hand, dob, ioc, height, wikidata_id; alias table (full, last_initial, match_name spellings).
* **Normalisation** (`identity/names.py`): NFKD diacritic stripping, lowercase, hyphen/apostrophe/period ->
  space, suffix tokens (jr/sr/ii/iii) dropped, "Kwon S.W." / "Bautista Agut R." parsed to surname + initials.
* **tennis-data linking** (`link_tennis_data_names`): candidates must agree on tour, date window (tournament
  start + span), tournament (token overlap / location / alias table) and both players (surname + initial;
  a wrong first initial scores 0). MATCHED only when best > 0.8 and runner-up < 0.5; AMBIGUOUS otherwise;
  two rows claiming one match key demote both. ATP 2020-2026 mirror workbooks: 14,195 MATCHED / 593
  AMBIGUOUS / 373 UNMATCHED (93.6 %).
* **Kalshi competitors** (`identity/kalshi_map.py`): exact normalised full-name match against the tour's
  rating state; namesakes resolved only if exactly one was active in the last 24 months; else AMBIGUOUS
  (fail closed). Results cached by the exchange's competitor UUID in `config/kalshi_competitor_map.json`
  (reviewable, versioned).
* **Match identity**: `match_key = tour:tourney_id:match_num`; cross-source dedupe key = tour | tourney_date |
  round | normalised winner | normalised loser (rematches in different rounds/dates stay distinct).
* **Doubles teams**: `team_key = sorted(player ids)`.

Gate TENNIS-7 fails if any AMBIGUOUS mapping reaches production.
