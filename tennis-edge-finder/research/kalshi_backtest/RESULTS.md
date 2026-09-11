# Model vs KALSHI pre-start price (settled match-winner markets, Jul-Sep 2026)

Funnel: {'events': 3921, 'no_canonical_match': 2599, 'unmapped': 769, 'non_binary_settlement': 49, 'no_prestart_quote': 503, 'not_two_parsed_sides': 1}

Kalshi quote = last hourly candle ending >= 5 min before scheduled start, two-sided, spread <= 15c, OI > 0. Model = walk-forward Elo (ratings from matches strictly before each match). Orientation: side A of the event; symmetric by construction (both sides listed).

No linked rows.
