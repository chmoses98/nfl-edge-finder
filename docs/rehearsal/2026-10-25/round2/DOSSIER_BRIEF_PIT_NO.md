# PIT @ NO — 2026_07_PIT_NO

Kickoff 2026-10-25T13:30:00+00:00 UTC. Cite evidence by the id in backticks. Full detail: `dossiers/2026_07_PIT_NO.json`.

## Questions the data raises

* Jordyn Tyson (WR, NO) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
* Ben Skowronek (WR, PIT) is ruled out. Is the market's price on his replacement's usage already reflecting the redistributed role, or still anchored to a committee?
* 1 skill players are Questionable (Rico Dowdle (RB)). These resolve at the inactive release 90 minutes before kickoff — is any current price worth taking before that, or is the option value of waiting larger than the move you expect?
* KXNFLRECYDS-26OCT25PITNO-PITDMETCALF4-60 moved +0.150 since first capture. Is that move explained by public injury news already in this packet, or is it information we do not have?
* The model disagrees by -0.677 on KXNFLREC-26OCT25PITNO-PITGBERNARD17-3 (Germie Bernard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
* The model disagrees by -0.625 on KXNFLREC-26OCT25PITNO-PITGBERNARD17-4 (Germie Bernard). Is that a mean disagreement the market has historically handled better, or a genuine shape difference? Note the model was shown redundant to the market on player props.
* KXNFLREC-26OCT25PITNO-NODVELE14-2 sits at a market price of 0.89 — a tail rung. The tail of the model's distribution is the least validated part of it. Is this rung relying on shape the model is known to miscalibrate?

## Team matchup (advantage to the offence; schedule-adjusted where marked)

* `TM:NO>PIT:pass_offence_v_pass_defence` — NO offence v PIT defence, pass offence v pass defence: advantage to the offence -0.070 (offence -0.046, defence allowed -0.025; schedule-adjusted) [adjusted]
* `TM:NO>PIT:run_offence_v_run_defence` — NO offence v PIT defence, run offence v run defence: advantage to the offence -0.033 (offence -0.038, defence allowed +0.006; schedule-adjusted) [adjusted]
* `TM:NO>PIT:neutral_script_efficiency` — NO offence v PIT defence, neutral-script efficiency: advantage to the offence -0.045 (offence -0.044, defence allowed -0.001; schedule-adjusted) [adjusted]
* `TM:NO>PIT:early_down_efficiency` — NO offence v PIT defence, early-down efficiency: advantage to the offence -0.072 (offence -0.050, defence allowed -0.022; schedule-adjusted) [adjusted]
* `TM:NO>PIT:explosive_plays` — NO offence v PIT defence, explosive plays: advantage to the offence -0.008 (offence -0.016, defence allowed +0.008; schedule-adjusted) [adjusted]
* `TM:NO>PIT:sack_rate` — NO offence v PIT defence, sack rate: advantage to the offence +0.005 (offence -0.007, defence allowed +0.002; schedule-adjusted) [adjusted]
* `TM:NO>PIT:success_rate` — NO offence v PIT defence, success rate: advantage to the offence -0.020 (offence -0.014, defence allowed -0.006; schedule-adjusted) [adjusted]
* `TM:NO:proe` — NO neutral-script pass rate over expected -2.91503 (adjusted -0.89793; slate mean -1.0447) [RAW]
* `TM:PIT>NO:pass_offence_v_pass_defence` — PIT offence v NO defence, pass offence v pass defence: advantage to the offence -0.043 (offence -0.068, defence allowed +0.025; schedule-adjusted) [adjusted]
* `TM:PIT>NO:run_offence_v_run_defence` — PIT offence v NO defence, run offence v run defence: advantage to the offence +0.101 (offence +0.072, defence allowed +0.029; schedule-adjusted) [adjusted]
* `TM:PIT>NO:neutral_script_efficiency` — PIT offence v NO defence, neutral-script efficiency: advantage to the offence +0.021 (offence -0.015, defence allowed +0.036; schedule-adjusted) [adjusted]
* `TM:PIT>NO:early_down_efficiency` — PIT offence v NO defence, early-down efficiency: advantage to the offence +0.041 (offence -0.001, defence allowed +0.042; schedule-adjusted) [adjusted]
* `TM:PIT>NO:explosive_plays` — PIT offence v NO defence, explosive plays: advantage to the offence -0.002 (offence -0.001, defence allowed -0.001; schedule-adjusted) [adjusted]
* `TM:PIT>NO:sack_rate` — PIT offence v NO defence, sack rate: advantage to the offence +0.000 (offence -0.000, defence allowed +0.000; schedule-adjusted) [adjusted]
* `TM:PIT>NO:success_rate` — PIT offence v NO defence, success rate: advantage to the offence +0.012 (offence -0.009, defence allowed +0.021; schedule-adjusted) [adjusted]
* `TM:PIT:proe` — PIT neutral-script pass rate over expected 4.62264 (adjusted 2.25795; slate mean -1.0447) [RAW]

## Quarterback and offensive line

* `QB:NO` — NO QB Tyler Shough (Active): EPA/dropback clean 0.12955 vs under pressure -0.88604 (248 dropbacks); opposing QB-hit rate 0.15657, sack rate 0.07706 (slate means 0.1533, 0.0629) [RAW]
* `QB:PIT` — PIT QB Aaron Rodgers (Active): EPA/dropback clean 0.04193 vs under pressure -0.86845 (250 dropbacks); opposing QB-hit rate 0.12465, sack rate 0.06345 (slate means 0.1533, 0.0629) [RAW]
* `OL:NO` — NO offensive line not active/listed: [('Cesar Ruiz', 'Questionable')]; no OL quality metric is captured
* `OL:PIT` — PIT offensive line not active/listed: none; no OL quality metric is captured

## Availability

* `AV:NO` — NO injury report (non-active): Cesar Ruiz G Questionable; Nathan Shepherd DT Questionable; Jordyn Tyson WR Injured Reserve
* `AV:PIT` — PIT injury report (non-active): Ben Skowronek WR Out; Brandin Echols CB Out; DeShon Elliott S Questionable; Rico Dowdle RB Questionable; Sebastian Joseph-Day DT Injured Reserve

## Environment and market centre

* `ENV:rest` — rest days: home 7, away 7
* `ENV:weather` — venue {'venue': 'Stade de France', 'roof': 'dome', 'surface': 'sportturf', 'neutral_site': True}; weather {'roof_status': 'CLOSED', 'temperature_f': None, 'wind': None, 'precipitation_probability': None, 'short_forecast': None, 'material': False, 'note': "played at Stade de France, not NO's home stadium -- no forecast for this venue is captured, and the home stadium's forecast is not shown (scheduled stadium id PAR0…
* `ENV:market` — market centre (midpoints, not executable): home margin -2.95, total 44.1, win probability {'PIT': 0.605, 'NO': 0.395}

## Game scripts and team volume

* `TV:NO` — NO simulated plays 64.3, pass rate 0.608; by final margin: {'lead14+': {'share_of_rows': 0.1024, 'pass_rate_mean': 0.5065, 'pass_att_mean': 29.59, 'rush_att_mean': 33.61, 'plays_mean': 65.3}, 'lead7-13': {'share_of_rows': 0.1098, 'pass_rate_mean': 0.559, 'pass_att_mean': 32.67, 'rush_att_mean': 30.26, 'plays_mean': 65.26}, 'within6': {'share_of_rows': 0.4368, 'pass_rate_mean': 0.6015, 'pass_att_mean': 35.16, 'rush_a…
* `TV:PIT` — PIT simulated plays 62.8, pass rate 0.612; by final margin: {'lead14+': {'share_of_rows': 0.1752, 'pass_rate_mean': 0.5272, 'pass_att_mean': 30.25, 'rush_att_mean': 30.41, 'plays_mean': 63.05}, 'lead7-13': {'share_of_rows': 0.1758, 'pass_rate_mean': 0.5812, 'pass_att_mean': 33.43, 'rush_att_mean': 27.23, 'plays_mean': 63.3}, 'within6': {'share_of_rows': 0.4368, 'pass_rate_mean': 0.6242, 'pass_att_mean': 35.99, 'rush…
* `SC:competitive_normal_scoring` — script competitive / normal scoring: 32% (market-centred simulation, research)
* `SC:favorite_control_normal_scoring` — script favourite controls / normal scoring: 15% (market-centred simulation, research)
* `SC:competitive_high_scoring` — script competitive / high scoring: 12% (market-centred simulation, research)
* `SC:competitive_low_scoring` — script competitive / low scoring: 10% (market-centred simulation, research)
* `SC:underdog_control_normal_scoring` — script underdog controls / normal scoring: 9% (market-centred simulation, research)

## Simulated player opportunity (research, context only)

* `PO:NO:kendre_miller` — Kendre Miller (NO RB) simulated targets 1.7 (50% range [0.0, 2.0]), carries 10.2, p_active 0.9758, role uncertainty MEDIUM
* `PO:NO:00_0033906` — 00-0033906 (NO RB) simulated targets 3.4 (50% range [1.0, 5.0]), carries 8.2, p_active 0.976, role uncertainty MEDIUM
* `PO:NO:chris_olave` — Chris Olave (NO WR) simulated targets 8.8 (50% range [5.0, 12.0]), carries 0.1, p_active 0.975, role uncertainty MEDIUM
* `PO:NO:devaughn_vele` — Devaughn Vele (NO WR) simulated targets 6.0 (50% range [3.0, 8.0]), carries 0.1, p_active 0.9738, role uncertainty HIGH
* `PO:NO:juwan_johnson` — Juwan Johnson (NO TE) simulated targets 4.9 (50% range [2.0, 7.0]), carries 0.0, p_active 0.9748, role uncertainty HIGH
* `PO:PIT:jaylen_warren` — Jaylen Warren (PIT RB) simulated targets 4.9 (50% range [2.0, 7.0]), carries 13.8, p_active 0.9729, role uncertainty MEDIUM
* `PO:PIT:dk_metcalf` — DK Metcalf (PIT WR) simulated targets 8.8 (50% range [5.0, 12.0]), carries 0.2, p_active 0.9751, role uncertainty MEDIUM
* `PO:PIT:00_0036139` — 00-0036139 (PIT RB) simulated targets 2.6 (50% range [0.0, 4.0]), carries 5.7, p_active 0.7769, role uncertainty HIGH
* `PO:PIT:germie_bernard` — Germie Bernard (PIT WR) simulated targets 6.2 (50% range [3.0, 9.0]), carries 0.2, p_active 0.9765, role uncertainty HIGH
* `PO:PIT:00_0036894` — 00-0036894 (PIT TE) simulated targets 4.7 (50% range [2.0, 7.0]), carries 0.3, p_active 0.9738, role uncertainty HIGH

## Measured player usage (last four games, share of team)

* `US:chris_olave` — Chris Olave last 4 weeks [3, 4, 5, 6]: {'targets': 9.5, 'receptions': 6.25, 'receiving_yards': 78.0, 'carries': 0.0, 'rushing_yards': 0.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.27, carry share 0.0, offense snap % 0.797 [RAW]
* `US:daniel_carlson` — Daniel Carlson last 4 weeks [3, 4, 5, 6]: {'targets': 0.0, 'receptions': 0.0, 'receiving_yards': 0.0, 'carries': 0.0, 'rushing_yards': 0.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.0, carry share 0.0, offense snap % 0.0 [RAW]
* `US:devaughn_vele` — Devaughn Vele last 4 weeks [3, 4, 5, 6]: {'targets': 6.75, 'receptions': 4.0, 'receiving_yards': 40.25, 'carries': 0.0, 'rushing_yards': 0.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.191, carry share 0.0, offense snap % 0.912 [RAW]
* `US:juwan_johnson` — Juwan Johnson last 4 weeks [3, 4, 5, 6]: {'targets': 5.75, 'receptions': 4.5, 'receiving_yards': 32.0, 'carries': 0.0, 'rushing_yards': 0.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.163, carry share 0.0, offense snap % 0.655 [RAW]
* `US:kendre_miller` — Kendre Miller last 4 weeks [3, 4, 5, 6]: {'targets': 2.0, 'receptions': 1.5, 'receiving_yards': 3.75, 'carries': 10.0, 'rushing_yards': 30.75, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.057, carry share 0.392, offense snap % 0.3 [RAW]
* `US:tyler_shough` — Tyler Shough last 4 weeks [3, 4, 5, 6]: {'targets': 0.0, 'receptions': 0.0, 'receiving_yards': 0.0, 'carries': 2.0, 'rushing_yards': 18.25, 'attempts': 36.25, 'completions': 22.75, 'passing_yards': 195.25}; target share 0.0, carry share 0.078, offense snap % 0.992 [RAW]
* `US:aaron_rodgers` — Aaron Rodgers last 4 weeks [3, 4, 5, 6]: {'targets': 0.0, 'receptions': 0.0, 'receiving_yards': 0.0, 'carries': 1.25, 'rushing_yards': 3.75, 'attempts': 38.5, 'completions': 24.0, 'passing_yards': 269.75}; target share 0.0, carry share 0.058, offense snap % 0.992 [RAW]
* `US:chris_boswell` — Chris Boswell last 4 weeks [3, 4, 5, 6]: {'targets': 0.0, 'receptions': 0.0, 'receiving_yards': 0.0, 'carries': 0.0, 'rushing_yards': 0.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.0, carry share 0.0, offense snap % 0.0 [RAW]
* `US:dk_metcalf` — DK Metcalf last 4 weeks [3, 4, 5, 6]: {'targets': 8.25, 'receptions': 5.5, 'receiving_yards': 62.75, 'carries': 0.25, 'rushing_yards': 2.75, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.229, carry share 0.012, offense snap % None [RAW]
* `US:germie_bernard` — Germie Bernard last 4 weeks [3, 4, 5, 6]: {'targets': 6.0, 'receptions': 5.0, 'receiving_yards': 48.0, 'carries': 0.25, 'rushing_yards': 1.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.167, carry share 0.012, offense snap % 0.633 [RAW]
* `US:jaylen_warren` — Jaylen Warren last 4 weeks [3, 4, 5, 6]: {'targets': 5.0, 'receptions': 3.5, 'receiving_yards': 49.25, 'carries': 15.75, 'rushing_yards': 92.75, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.139, carry share 0.733, offense snap % 0.873 [RAW]
* `US:pat_freiermuth` — Pat Freiermuth last 4 weeks [3, 4, 5, 6]: {'targets': 4.75, 'receptions': 3.0, 'receiving_yards': 25.5, 'carries': 0.5, 'rushing_yards': 0.5, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.132, carry share 0.023, offense snap % 0.688 [RAW]
* `US:alvin_kamara` — Alvin Kamara last 4 weeks [3, 4, 5, 6]: {'targets': 3.5, 'receptions': 2.5, 'receiving_yards': 17.25, 'carries': 6.5, 'rushing_yards': 26.25, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.099, carry share 0.255, offense snap % 0.307 [RAW]
* `US:bryce_lance` — Bryce Lance last 4 weeks [3, 4, 5, 6]: {'targets': 3.75, 'receptions': 0.75, 'receiving_yards': 4.0, 'carries': 0.0, 'rushing_yards': 0.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.106, carry share 0.0, offense snap % 0.622 [RAW]
* `US:noah_fant` — Noah Fant last 4 weeks [2, 3, 5, 6]: {'targets': 1.5, 'receptions': 1.25, 'receiving_yards': 10.0, 'carries': 0.0, 'rushing_yards': 0.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.048, carry share 0.0, offense snap % 0.565 [RAW]
* `US:darnell_washington` — Darnell Washington last 4 weeks [3, 4, 5, 6]: {'targets': 4.5, 'receptions': 3.0, 'receiving_yards': 32.75, 'carries': 0.0, 'rushing_yards': 0.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.125, carry share 0.0, offense snap % 0.703 [RAW]
* `US:rico_dowdle` — Rico Dowdle last 4 weeks [1, 2, 6]: {'targets': 3.67, 'receptions': 2.33, 'receiving_yards': 12.33, 'carries': 7.33, 'rushing_yards': 25.67, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.093, carry share 0.333, offense snap % 0.37 [RAW]
* `US:cj_donaldson` — CJ Donaldson last 4 weeks [3, 4, 5, 6]: {'targets': 1.0, 'receptions': 0.75, 'receiving_yards': 3.0, 'carries': 3.5, 'rushing_yards': 18.75, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.028, carry share 0.137, offense snap % 0.323 [RAW]
* `US:barion_brown` — Barion Brown last 4 weeks [2, 4, 5, 6]: {'targets': 0.25, 'receptions': 0.25, 'receiving_yards': 1.25, 'carries': 0.25, 'rushing_yards': -1.25, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.008, carry share 0.01, offense snap % 0.083 [RAW]
* `US:oscar_delp` — Oscar Delp last 4 weeks [2, 4, 5, 6]: {'targets': 0.75, 'receptions': 0.75, 'receiving_yards': 4.5, 'carries': 0.0, 'rushing_yards': 0.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.023, carry share 0.0, offense snap % 0.33 [RAW]
* `US:kaden_wetjen` — Kaden Wetjen last 4 weeks [3, 4, 5, 6]: {'targets': 0.0, 'receptions': 0.0, 'receiving_yards': 0.0, 'carries': 0.0, 'rushing_yards': 0.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.0, carry share 0.0, offense snap % 0.0 [RAW]
* `US:robert_tonyan` — Robert Tonyan last 4 weeks [3]: {'targets': 1.0, 'receptions': 1.0, 'receiving_yards': 2.0, 'carries': 0.0, 'rushing_yards': 0.0, 'attempts': 0.0, 'completions': 0.0, 'passing_yards': 0.0}; target share 0.032, carry share 0.0, offense snap % 0.062 [RAW]

## Production the opponent allows to each position group (RAW, not schedule-adjusted)

* `DEF:PIT:WR` — PIT defence allows to WRs per game (index vs league mean): targets 20.33 (1.09x), receptions 11.67 (1.01x), receiving_yards 142.0 (0.94x), carries 0.17 (0.3x), rushing_yards 1.0 (0.35x) [RAW]
* `DEF:PIT:TE` — PIT defence allows to TEs per game (index vs league mean): targets 5.67 (0.74x), receptions 4.17 (0.76x), receiving_yards 45.5 (0.85x), carries 0.17 (1.84x), rushing_yards 0.17 (0.95x) [RAW]
* `DEF:PIT:RB` — PIT defence allows to RBs per game (index vs league mean): targets 6.17 (1.08x), receptions 4.67 (1.06x), receiving_yards 35.0 (1.13x), carries 21.83 (1.0x), rushing_yards 86.17 (0.96x) [RAW]
* `DEF:PIT:QB` — PIT defence allows to QBs per game (index vs league mean): attempts 33.5 (0.99x), completions 20.67 (0.96x), passing_yards 222.0 (0.94x), carries 3.33 (0.86x), rushing_yards 15.83 (0.92x) [RAW]
* `DEF:NO:QB` — NO defence allows to QBs per game (index vs league mean): attempts 33.33 (0.99x), completions 22.17 (1.03x), passing_yards 256.0 (1.09x), carries 4.33 (1.12x), rushing_yards 19.67 (1.15x) [RAW]
* `DEF:NO:WR` — NO defence allows to WRs per game (index vs league mean): targets 17.83 (0.96x), receptions 11.17 (0.96x), receiving_yards 149.67 (1.0x), carries 0.33 (0.59x), rushing_yards 1.5 (0.53x) [RAW]
* `DEF:NO:RB` — NO defence allows to RBs per game (index vs league mean): targets 4.33 (0.76x), receptions 4.0 (0.91x), receiving_yards 30.5 (0.98x), carries 24.17 (1.1x), rushing_yards 116.83 (1.3x) [RAW]
* `DEF:NO:TE` — NO defence allows to TEs per game (index vs league mean): targets 9.5 (1.24x), receptions 7.0 (1.27x), receiving_yards 75.83 (1.41x), carries 0.0 (0.0x), rushing_yards 0.0 (0.0x) [RAW]

## Contract families and player ladders (id -> how it can be priced)

* `FAM:BOTH_TEAMS_SCORE_N|FULL` — BOTH_TEAMS_SCORE_N|FULL: 4 listed, 2 executable; DERIVED from the market-centred simulation shifted by a thesis `shift` range (full-game margin/total)
* `FAM:GAME_EVENT|FULL` — GAME_EVENT|FULL: 4 listed, 4 executable; DECLARED fair range only (no ladder, or fewer than 3 usable rungs); cannot be ranked without one
* `FAM:PLAYER_STAT|FULL` — PLAYER_STAT|FULL: 398 listed, 388 executable; LADDER SHIFT: 54 ladder(s) with >= 3 usable rungs; price with a thesis `ladder_shifts` entry (units of the quantity)
* `FAM:FIRST_TD_SCORER|FULL` — FIRST_TD_SCORER|FULL: 25 listed, 25 executable; DECLARED fair range only (no ladder, or fewer than 3 usable rungs); cannot be ranked without one
* `FAM:FIRST_TD_TEAM|FULL` — FIRST_TD_TEAM|FULL: 28 listed, 7 executable; DECLARED fair range only (no ladder, or fewer than 3 usable rungs); cannot be ranked without one
* `FAM:GAME_WINNER|FULL` — GAME_WINNER|FULL: 2 listed, 2 executable; DERIVED from the market-centred simulation shifted by a thesis `shift` range (full-game margin/total)
* `FAM:GAME_PLAYER_LEADER|FULL` — GAME_PLAYER_LEADER|FULL: 13 listed, 12 executable; DECLARED fair range only (no ladder, or fewer than 3 usable rungs); cannot be ranked without one
* `FAM:RACE_TO_N|FULL` — RACE_TO_N|FULL: 15 listed, 7 executable; DECLARED fair range only (no ladder, or fewer than 3 usable rungs); cannot be ranked without one
* `FAM:SPREAD|FULL` — SPREAD|FULL: 25 listed, 25 executable; DERIVED from the market-centred simulation shifted by a thesis `shift` range (full-game margin/total)
* `FAM:TEAM_STAT|FULL` — TEAM_STAT|FULL: 20 listed, 1 executable; DECLARED fair range only (no ladder, or fewer than 3 usable rungs); cannot be ranked without one
* `FAM:TEAM_TOTAL|FULL` — TEAM_TOTAL|FULL: 27 listed, 27 executable; DERIVED from the market-centred simulation shifted by a thesis `shift` range (full-game margin/total)
* `FAM:TOTAL|FULL` — TOTAL|FULL: 19 listed, 19 executable; DERIVED from the market-centred simulation shifted by a thesis `shift` range (full-game margin/total)
* `FAM:WIN_MARGIN_BUCKET|FULL` — WIN_MARGIN_BUCKET|FULL: 7 listed, 7 executable; DERIVED from the market-centred simulation shifted by a thesis `shift` range (full-game margin/total)
* `PM:chris_olave:receiving_yards` — Chris Olave receiving_yards ladder: 13 usable rungs, market median 76.5, 13 executable
* `PM:chris_olave:receptions` — Chris Olave receptions ladder: 11 usable rungs, market median 6.38, 11 executable
* `PM:chris_olave:touchdowns` — Chris Olave touchdowns ladder: 3 usable rungs, market median None, 3 executable
* `PM:devaughn_vele:receiving_yards` — Devaughn Vele receiving_yards ladder: 9 usable rungs, market median 43.93, 9 executable
* `PM:devaughn_vele:receptions` — Devaughn Vele receptions ladder: 9 usable rungs, market median 4.44, 9 executable
* `PM:juwan_johnson:receiving_yards` — Juwan Johnson receiving_yards ladder: 8 usable rungs, market median 33.1, 8 executable
* `PM:juwan_johnson:receptions` — Juwan Johnson receptions ladder: 8 usable rungs, market median 3.92, 8 executable
* `PM:kendre_miller:carries` — Kendre Miller carries ladder: 3 usable rungs, market median 11.94, 3 executable
* `PM:kendre_miller:receiving_yards` — Kendre Miller receiving_yards ladder: 7 usable rungs, market median None, 7 executable
* `PM:kendre_miller:receptions` — Kendre Miller receptions ladder: 7 usable rungs, market median 1.32, 7 executable
* `PM:kendre_miller:rushing_yards` — Kendre Miller rushing_yards ladder: 10 usable rungs, market median 36.94, 10 executable
* `PM:kendre_miller:touchdowns` — Kendre Miller touchdowns ladder: 3 usable rungs, market median None, 3 executable
* `PM:tyler_shough:attempts` — Tyler Shough attempts ladder: 3 usable rungs, market median 36.5, 3 executable
* `PM:tyler_shough:completions` — Tyler Shough completions ladder: 3 usable rungs, market median 23.36, 3 executable
* `PM:tyler_shough:interceptions` — Tyler Shough interceptions ladder: 3 usable rungs, market median 1.13, 3 executable
* `PM:tyler_shough:passing_tds` — Tyler Shough passing_tds ladder: 4 usable rungs, market median 1.72, 4 executable
* `PM:tyler_shough:passing_yards` — Tyler Shough passing_yards ladder: 9 usable rungs, market median 220.83, 9 executable
* `PM:tyler_shough:rushing_yards` — Tyler Shough rushing_yards ladder: 7 usable rungs, market median 14.44, 7 executable
* `PM:aaron_rodgers:attempts` — Aaron Rodgers attempts ladder: 3 usable rungs, market median 35.48, 3 executable
* `PM:aaron_rodgers:completions` — Aaron Rodgers completions ladder: 3 usable rungs, market median 22.44, 3 executable
* `PM:aaron_rodgers:interceptions` — Aaron Rodgers interceptions ladder: 3 usable rungs, market median None, 3 executable
* `PM:aaron_rodgers:passing_tds` — Aaron Rodgers passing_tds ladder: 4 usable rungs, market median 1.98, 4 executable
* `PM:aaron_rodgers:passing_yards` — Aaron Rodgers passing_yards ladder: 9 usable rungs, market median 232.03, 9 executable
* `PM:aaron_rodgers:rushing_yards` — Aaron Rodgers rushing_yards ladder: 5 usable rungs, market median None, 5 executable
* `PM:dk_metcalf:receiving_yards` — DK Metcalf receiving_yards ladder: 11 usable rungs, market median 59.47, 11 executable
* `PM:dk_metcalf:receptions` — DK Metcalf receptions ladder: 9 usable rungs, market median 5.3, 9 executable
* `PM:dk_metcalf:touchdowns` — DK Metcalf touchdowns ladder: 3 usable rungs, market median None, 3 executable
* `PM:germie_bernard:receiving_yards` — Germie Bernard receiving_yards ladder: 12 usable rungs, market median 56.07, 12 executable
* `PM:germie_bernard:receptions` — Germie Bernard receptions ladder: 9 usable rungs, market median 5.5, 9 executable
* `PM:germie_bernard:touchdowns` — Germie Bernard touchdowns ladder: 3 usable rungs, market median None, 3 executable
* `PM:jaylen_warren:carries` — Jaylen Warren carries ladder: 3 usable rungs, market median 14.94, 3 executable
* `PM:jaylen_warren:receiving_yards` — Jaylen Warren receiving_yards ladder: 7 usable rungs, market median 25.32, 7 executable
* `PM:jaylen_warren:receptions` — Jaylen Warren receptions ladder: 7 usable rungs, market median 3.61, 7 executable
* `PM:jaylen_warren:rush_rec_yards` — Jaylen Warren rush_rec_yards ladder: 3 usable rungs, market median None, 3 executable
* `PM:jaylen_warren:rushing_yards` — Jaylen Warren rushing_yards ladder: 11 usable rungs, market median 65.91, 11 executable
* `PM:jaylen_warren:touchdowns` — Jaylen Warren touchdowns ladder: 3 usable rungs, market median None, 3 executable
* `PM:pat_freiermuth:receiving_yards` — Pat Freiermuth receiving_yards ladder: 11 usable rungs, market median 31.25, 11 executable
* `PM:pat_freiermuth:receptions` — Pat Freiermuth receptions ladder: 7 usable rungs, market median 3.67, 7 executable
* `PM:pat_freiermuth:touchdowns` — Pat Freiermuth touchdowns ladder: 3 usable rungs, market median None, 3 executable
* `PM:alvin_kamara:receiving_yards` — Alvin Kamara receiving_yards ladder: 4 usable rungs, market median None, 4 executable
* `PM:alvin_kamara:receptions` — Alvin Kamara receptions ladder: 6 usable rungs, market median 3.17, 6 executable
* `PM:alvin_kamara:rush_rec_yards` — Alvin Kamara rush_rec_yards ladder: 3 usable rungs, market median 35.8, 3 executable
* `PM:alvin_kamara:rushing_yards` — Alvin Kamara rushing_yards ladder: 7 usable rungs, market median 16.96, 7 executable
* `PM:bryce_lance:receiving_yards` — Bryce Lance receiving_yards ladder: 8 usable rungs, market median 14.09, 8 executable
* `PM:bryce_lance:receptions` — Bryce Lance receptions ladder: 4 usable rungs, market median None, 4 executable
* `PM:noah_fant:receiving_yards` — Noah Fant receiving_yards ladder: 4 usable rungs, market median None, 4 executable
* `PM:noah_fant:receptions` — Noah Fant receptions ladder: 4 usable rungs, market median 2.06, 4 executable
* `PM:darnell_washington:receiving_yards` — Darnell Washington receiving_yards ladder: 10 usable rungs, market median 25.0, 10 executable
* `PM:darnell_washington:receptions` — Darnell Washington receptions ladder: 6 usable rungs, market median 3.02, 6 executable
* `PM:darnell_washington:touchdowns` — Darnell Washington touchdowns ladder: 3 usable rungs, market median None, 3 executable
* `PM:rico_dowdle:receiving_yards` — Rico Dowdle receiving_yards ladder: 4 usable rungs, market median None, 4 executable
* `PM:rico_dowdle:rushing_yards` — Rico Dowdle rushing_yards ladder: 10 usable rungs, market median 29.17, 10 executable
* `PM:rico_dowdle:touchdowns` — Rico Dowdle touchdowns ladder: 3 usable rungs, market median None, 3 executable
* `PM:cj_donaldson:rushing_yards` — CJ Donaldson rushing_yards ladder: 6 usable rungs, market median 10.86, 6 executable
* (+24 period/other families: see `contract_families` in the JSON; price them with `ladder_shifts` or declare a fair range)

## Not captured

defensive coverage scheme (man/zone) and per-receiver coverage assignment; blitz rate and pressure-by-package splits (only sack and QB-hit rates are captured); boundary versus slot receiver splits and route-level data (routes run, targets per route); inside versus outside run splits, gap and zone-scheme data; defensive run fits; offensive-line pass-block and run-block grades, continuity, pass-rush win rate (only the injury list); snap counts per play and in-game substitution patterns (depth-chart order is a stated intention, not a snap share); travel distance and time-zone burden (rest days only); score-state paths, lead changes, red-zone trip counts, drive counts (not simulated)
