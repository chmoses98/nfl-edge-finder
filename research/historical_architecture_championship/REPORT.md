# Historical Model Architecture Championship (RESEARCH_ONLY)

Reproduce: `python scripts/data/nflverse_download.py --only pbp,schedules --seasons 2001-2025`, then `python scripts/sim/hmac_run.py dev|select|choose|final|report` (frozen protocol in `frozen.json`, committed before the holdout was scored; `final` refuses to run if the code hash changed).

## Verdict
The closing market (as a centre) beats every football-first architecture on every primary metric, in the clean holdout and in 13 further seasons. No football-first or hybrid model beats the best market-centred model. The only model that beats the incumbent residual bank (A1) does so through distribution shape (a favorite-oriented bank), not football information.
Recommendation for SIFT: keep a market-centred architecture; replace the home-oriented residual bank with a favorite-oriented bank (A3) after a separate prospective check; do not build a football-first or possession simulator to improve game-script forecasts.

## Split (frozen before scoring)
burn-in 2001-2002 | development 2006-2007 (534 games) | selection 2008-2009 (534) | FINAL HOLDOUT 2010-2012 (801 games, scored once) | reused evidence 2013-2025 (3,562 games).
SIFT audit: all prior SIFT game-level research starts at 2016 (design on <=2020, evaluation 2021-2025); player models used 2013-2015 as priors only. 2010-2012 was never touched by SIFT game-level research, so it is the least-contaminated holdout. It is NOT untouched by the author of this protocol in general (the dev/selection seasons were viewed, the holdout was not). 2013-2025 is reused historical evidence, not independent confirmation.
Information horizons: market models use the closing line (T-0). Football models use games before the target game plus the T-0 starting-QB identity (known about 90 minutes pre-kickoff); no football model sees any betting line. Hybrids see both.

## Post-hoc items (disclosed)
After the holdout was scored, I ran (a) A2, a market-centred kernel, and (b) the error decomposition. Neither was used for selection. E_mix_A1_ens mixes with F_ens_k2, a predeclared (untuned) bandwidth; family winners were chosen on only two selection seasons.
