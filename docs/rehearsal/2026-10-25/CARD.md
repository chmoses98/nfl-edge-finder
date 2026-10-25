# NFL card — week 7, 2026-10-25 01:45 UTC

**REHEARSAL — replay of an old snapshot at its own capture time. Nothing below is executable.**

packet `889d4eb7aefafc751f20` · data gate **OK** · capture age 4.0 min · 1U = $75 · max 5U

First kickoff on this slate: **PIT @ NO**, 10-25 13:30 UTC (704 min after this card's clock). Bets on that game must be placed before it; later games can wait for their inactive lists.

## No bets on this card

Every game was reviewed or triaged and nothing cleared the evidence, challenge, price and execution gates. That is an outcome, not an error.

## Every game, one terminal state

| Game | Kickoff (UTC) | State | Why |
|---|---|---|---|
| NE @ CHI | 10-23 00:15 | POST_KICKOFF_EXCLUDED | kickoff has passed at the decision time; outside the pregame window |
| PIT @ NO | 10-25 13:30 | TRIAGED_NO_THESIS | no analyst thesis was filed for this game; triage rank 6. Absence of a thesis is a PASS, not an omission: largest adjusted offence-v-defence gap 0.10 EPA/play; 714 executable contracts |
| CIN @ BAL | 10-25 17:00 | TRIAGED_NO_THESIS | no analyst thesis was filed for this game; triage rank 12. Absence of a thesis is a PASS, not an omission: rest differential 7 v 14 days; 708 executable contracts |
| CLE @ TEN | 10-25 17:00 | TRIAGED_NO_THESIS | no analyst thesis was filed for this game; triage rank 7. Absence of a thesis is a PASS, not an omission: largest adjusted offence-v-defence gap 0.20 EPA/play; 648 executable contracts |
| IND @ MIN | 10-25 17:00 | TRIAGED_NO_THESIS | no analyst thesis was filed for this game; triage rank 2. Absence of a thesis is a PASS, not an omission: largest adjusted offence-v-defence gap 0.26 EPA/play; rest differential 14 v 7 days; 656 executable contracts |
| MIA @ NYJ | 10-25 17:00 | TRIAGED_NO_THESIS | no analyst thesis was filed for this game; triage rank 13. Absence of a thesis is a PASS, not an omission: rest differential 7 v 14 days; 631 executable contracts |
| NYG @ HOU | 10-25 17:00 | DEEP_REVIEWED_PASS | 2026_07_NYG_HOU::T1: no contract expressing this thesis clears a 2.0c net edge at the conservative end of the fair range after fees (160 evaluated, 0 clear) |
| SF @ ATL | 10-25 17:00 | TRIAGED_NO_THESIS | no analyst thesis was filed for this game; triage rank 9. Absence of a thesis is a PASS, not an omission: largest adjusted offence-v-defence gap 0.13 EPA/play; 664 executable contracts |
| TB @ CAR | 10-25 17:00 | DEEP_REVIEWED_PASS | 2026_07_TB_CAR::T0: PASS by thesis: Baker Mayfield (QB, TB) is Questionable. Participation resolves at the inactive list about 90 minutes before the 17:00Z kickoff (about 15:30Z); until then the option value of waiting exceeds any edge, and a player-status-dependent price is not  |
| DEN @ ARI | 10-25 20:05 | TRIAGED_NO_THESIS | no analyst thesis was filed for this game; triage rank 3. Absence of a thesis is a PASS, not an omission: largest adjusted offence-v-defence gap 0.13 EPA/play; rest differential 7 v 10 days; 683 executable contracts |
| GB @ DET | 10-25 20:25 | DEEP_REVIEWED_PASS | 2026_07_GB_DET::T1: no contract expressing this thesis clears a 2.0c net edge at the conservative end of the fair range after fees (154 evaluated, 0 clear) |
| LA @ LV | 10-25 20:25 | TRIAGED_NO_THESIS | no analyst thesis was filed for this game; triage rank 10. Absence of a thesis is a PASS, not an omission: largest adjusted offence-v-defence gap 0.14 EPA/play; 572 executable contracts |
| KC @ SEA | 10-26 00:20 | DEEP_REVIEWED_PASS | 2026_07_KC_SEA::T1: no contract expressing this thesis clears a 2.0c net edge at the conservative end of the fair range after fees (150 evaluated, 0 clear) |
| DAL @ PHI | 10-27 00:15 | TRIAGED_NO_THESIS | no analyst thesis was filed for this game; triage rank 11. Absence of a thesis is a PASS, not an omission: largest adjusted offence-v-defence gap 0.12 EPA/play; 583 executable contracts |

## Thesis 2026_07_NYG_HOU::T1: NYG's offence is the worst matchup on the slate against HOU's defence, while NYG's secondary is depleted: expect HOU to win by slightly more than the market has it and NYG to score less.

Shift applied to the market centre (home margin / total, points): [0.5, 2.0] / [-1.5, 0.5]. Engine noise vs the market with no thesis (rms): BOTH_TEAMS_SCORE_N 0.010, GAME_WINNER 0.002, SPREAD 0.021, TEAM_TOTAL 0.037, TOTAL 0.025.
Evaluated 160 contract-sides; 0 clear the 2.0¢ conservative net-edge floor. Outcome: **PASS**.

PASS because: no contract expressing this thesis clears a 2.0c net edge at the conservative end of the fair range after fees (160 evaluated, 0 clear)

How far from a bet: a contract first clears at 4.0x the stated shift (home margin [2.0, 8.0], total [-6.0, 2.0]): Texans -10.5 (YES) at 49¢. A reading aid, not a position.
Rejected / not selected (top by rank):

* Texans -7.5 YES @58¢ — net edge at the conservative end is -1.1c per contract after fees (needs >= 2.0c); ceiling would be 54c vs ask 58c
* Texans -3.5 YES @72¢ — net edge at the conservative end is -1.9c per contract after fees (needs >= 2.0c); ceiling would be 68c vs ask 72c
* Texans -4.5 YES @69¢ — net edge at the conservative end is -2.6c per contract after fees (needs >= 2.0c); ceiling would be 64c vs ask 69c
* Giants to NOT win outright (opponent win or tie) NO @81¢ — net edge at the conservative end is -2.3c per contract after fees (needs >= 2.0c); ceiling would be 76c vs ask 81c
* Texans moneyline YES @81¢ — net edge at the conservative end is -2.5c per contract after fees (needs >= 2.0c); ceiling would be 76c vs ask 81c
* Texans -10.5 YES @49¢ — net edge at the conservative end is -3.5c per contract after fees (needs >= 2.0c); ceiling would be 43c vs ask 49c
* Texans -5.5 YES @67¢ — net edge at the conservative end is -3.5c per contract after fees (needs >= 2.0c); ceiling would be 61c vs ask 67c
* Texans -6.5 YES @64¢ — net edge at the conservative end is -4.1c per contract after fees (needs >= 2.0c); ceiling would be 57c vs ask 64c
* Texans -9.5 YES @55¢ — net edge at the conservative end is -4.8c per contract after fees (needs >= 2.0c); ceiling would be 48c vs ask 55c
* Game total Over 58.5 YES @12¢ — net edge at the conservative end is -3.4c per contract after fees (needs >= 2.0c); ceiling would be 6c vs ask 12c
* Texans +2.5 NO @85¢ — net edge at the conservative end is -2.5c per contract after fees (needs >= 2.0c); ceiling would be 80c vs ask 85c
* Texans +1.5 NO @84¢ — net edge at the conservative end is -3.9c per contract after fees (needs >= 2.0c); ceiling would be 77c vs ask 84c

## Thesis 2026_07_GB_DET::T1: Two pass-first offences in a closed dome with DET safety Joseph and GB pass rusher Parsons out: scoring should exceed the market total.

Shift applied to the market centre (home margin / total, points): [-0.5, 0.5] / [0.5, 2.5]. Engine noise vs the market with no thesis (rms): BOTH_TEAMS_SCORE_N 0.013, GAME_WINNER 0.001, SPREAD 0.020, TEAM_TOTAL 0.047, TOTAL 0.036.
Evaluated 154 contract-sides; 0 clear the 2.0¢ conservative net-edge floor. Outcome: **PASS**.

PASS because: no contract expressing this thesis clears a 2.0c net edge at the conservative end of the fair range after fees (154 evaluated, 0 clear)

How far from a bet: a contract first clears at 1.5x the stated shift (home margin [-0.75, 0.75], total [0.75, 3.75]): Game total Over 43.5 (YES) at 79¢. A reading aid, not a position.
Rejected / not selected (top by rank):

* Packers team total Over 17.5 YES @77¢ — net edge at the conservative end is +1.9c per contract after fees (needs >= 2.0c); ceiling would be 76c vs ask 77c
* Packers team total Over 20.5 YES @68¢ — net edge at the conservative end is +0.8c per contract after fees (needs >= 2.0c); ceiling would be 66c vs ask 68c
* Packers -7.5 YES @15¢ — net edge at the conservative end is +0.9c per contract after fees (needs >= 2.0c); ceiling would be 14c vs ask 15c
* Packers team total Over 24.5 YES @51¢ — net edge at the conservative end is +0.8c per contract after fees (needs >= 2.0c); ceiling would be 49c vs ask 51c
* Game total Over 37.5 YES @89¢ — net edge at the conservative end is +0.3c per contract after fees (needs >= 2.0c); ceiling would be 87c vs ask 89c
* Game total Over 40.5 YES @86¢ — net edge at the conservative end is -0.2c per contract after fees (needs >= 2.0c); ceiling would be 83c vs ask 86c
* Game total Over 34.5 YES @93¢ — net edge at the conservative end is -0.2c per contract after fees (needs >= 2.0c); ceiling would be 90c vs ask 93c
* Packers +6.5 NO @60¢ — net edge at the conservative end is -0.8c per contract after fees (needs >= 2.0c); ceiling would be 57c vs ask 60c
* Game total Over 43.5 YES @79¢ — net edge at the conservative end is -0.5c per contract after fees (needs >= 2.0c); ceiling would be 76c vs ask 79c
* Game total Over 46.5 YES @73¢ — net edge at the conservative end is -0.7c per contract after fees (needs >= 2.0c); ceiling would be 70c vs ask 73c
* Packers team total Over 28.5 YES @35¢ — net edge at the conservative end is -1.1c per contract after fees (needs >= 2.0c); ceiling would be 31c vs ask 35c
* Packers team total Over 21.5 YES @65¢ — net edge at the conservative end is -1.0c per contract after fees (needs >= 2.0c); ceiling would be 61c vs ask 65c

## Thesis 2026_07_KC_SEA::T1: SEA's pass rush meets a KC line missing both starting tackles and a quarterback who loses 0.87 EPA/dropback under pressure: SEA should be a little better than the market has it and the game a little lower-scoring.

Shift applied to the market centre (home margin / total, points): [0.0, 1.5] / [-1.5, 0.0]. Engine noise vs the market with no thesis (rms): BOTH_TEAMS_SCORE_N 0.046, GAME_WINNER 0.011, SPREAD 0.021, TEAM_TOTAL 0.036, TOTAL 0.037.
Evaluated 150 contract-sides; 0 clear the 2.0¢ conservative net-edge floor. Outcome: **PASS**.

PASS because: no contract expressing this thesis clears a 2.0c net edge at the conservative end of the fair range after fees (150 evaluated, 0 clear)

nothing clears even at 4x the stated shift.
Rejected / not selected (top by rank):

* Seahawks -7.5 YES @27¢ — net edge at the conservative end is +1.9c per contract after fees (needs >= 2.0c); ceiling would be 26c vs ask 27c
* Seahawks +13.5 NO @88¢ — net edge at the conservative end is -0.6c per contract after fees (needs >= 2.0c); ceiling would be 85c vs ask 88c
* Seahawks +1.5 NO @60¢ — net edge at the conservative end is -1.2c per contract after fees (needs >= 2.0c); ceiling would be 56c vs ask 60c
* Seahawks -10.5 YES @22¢ — net edge at the conservative end is -1.6c per contract after fees (needs >= 2.0c); ceiling would be 18c vs ask 22c
* Seahawks +2.5 NO @63¢ — net edge at the conservative end is -1.4c per contract after fees (needs >= 2.0c); ceiling would be 59c vs ask 63c
* Seahawks +14.5 NO @90¢ — net edge at the conservative end is -1.1c per contract after fees (needs >= 2.0c); ceiling would be 86c vs ask 90c
* Seahawks -4.5 YES @41¢ — net edge at the conservative end is -2.9c per contract after fees (needs >= 2.0c); ceiling would be 36c vs ask 41c
* Chiefs to NOT win outright (opponent win or tie) NO @59¢ — net edge at the conservative end is -2.1c per contract after fees (needs >= 2.0c); ceiling would be 54c vs ask 59c
* Seahawks -9.5 YES @25¢ — net edge at the conservative end is -2.9c per contract after fees (needs >= 2.0c); ceiling would be 20c vs ask 25c
* Seahawks moneyline YES @59¢ — net edge at the conservative end is -2.3c per contract after fees (needs >= 2.0c); ceiling would be 54c vs ask 59c
* Seahawks -3.5 YES @44¢ — net edge at the conservative end is -2.4c per contract after fees (needs >= 2.0c); ceiling would be 39c vs ask 44c
* Seahawks -14.5 YES @14¢ — net edge at the conservative end is -2.6c per contract after fees (needs >= 2.0c); ceiling would be 9c vs ask 14c

## Thesis 2026_07_TB_CAR::T0: TB's quarterback is questionable and three TB starters are out; the price depends on the inactive list.

Evaluated 0 contract-sides; 0 clear the 2.0¢ conservative net-edge floor. Outcome: **PASS**.

PASS because: PASS by thesis: Baker Mayfield (QB, TB) is Questionable. Participation resolves at the inactive list about 90 minutes before the 17:00Z kickoff (about 15:30Z); until then the option value of waiting exceeds any edge, and a player-status-dependent price is not a bet. Re-run at the T-90m horizon.
