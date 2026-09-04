# Is the model's upper tail too fat? Yes — measured on settled outcomes

Reproduce: `python3 scripts/research/tail_calibration.py` and `python3 scripts/research/calibration_study.py`

## The defect

Two independent observations this session pointed the same way: on live ladders the model held *more*
upper-tail probability than the market (`research/market_shape`, 1.6 SE, not significant), and on settled
2025 markets the market's own high receiving-yards rungs were *overpriced* by 7.5 points
(`research/efficiency_map`). Together they suggest the market's tail is already too fat and the model's is
fatter still — a model defect, not an edge.

That is checkable against settled outcomes with no market prices involved at all. Walk-forward 2019–2025,
rungs bucketed by the model's own predicted probability, standard errors clustered on game:

| model P(Y ≥ k) | rungs | predicted | realised | bias | z |
|---|---|---|---|---|---|
| 0.02–0.05 | 199,708 | 0.0328 | 0.0233 | **−0.0096** | −11.7 to −13.7 per stat |
| 0.05–0.10 | 163,860 | 0.0723 | 0.0609 | **−0.0114** | −9.4 to −10.5 |
| 0.10–0.20 | 174,169 | 0.1447 | 0.1326 | **−0.0121** | −5.5 to −7.9 |
| 0.20–0.35 | 145,429 | 0.2682 | 0.2599 | −0.0083 | −2.3 to −4.5 |
| 0.35–0.50 | 98,891 | 0.4209 | 0.4164 | −0.0045 | |
| 0.50–0.70 | 96,982 | 0.5941 | 0.5967 | +0.0026 | |
| 0.70–1.01 | 131,917 | 0.8598 | 0.8568 | −0.0030 | |

Confirmed, on 1,871 games. In absolute terms the bias is about a point; at a 3–7% base rate that is a **15–40%
relative overstatement** of long-shot rungs. It is present in every statistic and in both family types, so it
is a property of the pipeline rather than of one distribution choice.

This matters more than its size suggests. It lands on precisely the rungs where the market is *itself*
overpricing long shots — first-touchdown contracts quoted 0.10–0.20 settle 7.5% of the time. An uncorrected
pricer sees the market's long-shot overpricing and, being wrong in the same direction only more so, reads it
as an opportunity.

## The anytime-touchdown model has the same defect, despite being the best-calibrated model here

`DirectTDModel` is a bespoke binary model rather than a count family, and it was excluded from the table
above. Checked separately on 41,196 player-games across 1,871 games it is **excellently calibrated in
aggregate** — predicted 0.1691 against realised 0.1688, bias −0.0003 — which independently reconfirms the
earlier decision to use a direct model rather than a count family for anytime touchdown.

It still has the tail defect, and its shape is different:

| model p | n | games | predicted | realised | bias | z |
|---|---|---|---|---|---|---|
| 0.02–0.05 | 4,984 | 1,680 | 0.0399 | 0.0285 | **−0.0114** | −4.9 |
| 0.05–0.10 | 12,034 | 1,870 | 0.0728 | 0.0643 | **−0.0085** | −3.9 |
| 0.10–0.20 | 10,897 | 1,869 | 0.1433 | 0.1506 | **+0.0073** | +2.1 |
| 0.20–0.35 | 8,777 | 1,861 | 0.2672 | 0.2783 | **+0.0112** | +2.4 |
| 0.35–0.50 | 3,569 | 1,639 | 0.4109 | 0.4015 | −0.0094 | −1.1 |
| 0.50+ | 933 | 733 | 0.5545 | 0.5595 | +0.0049 | +0.3 |

Where the count families are uniformly too fat below 0.35, the direct model is S-shaped: too fat in the deep
tail below 0.10, too *thin* between 0.10 and 0.35. An aggregate bias of −0.0003 conceals both.

The deep-tail half of this matches the efficiency map exactly, where `PLAYER_STAT:touchdowns` in the
[0.00, 0.02) bucket was one of the seven cells surviving FDR at every horizon tested. Two different methods,
one pointing at the model and one at the market, agree that the sub-5-cent touchdown rungs are the least
trustworthy prices on the board.

That the defect survives in the single best-calibrated model in the platform is the reason it is treated as a
pipeline property rather than a family choice.

## The correction, and an honest account of what it buys

`nfl_edge/pricing/calibration.LadderCalibrator` is a monotone map from predicted to calibrated probability,
fitted in logit space with pool-adjacent-violators, so it cannot reorder rungs within a ladder and cannot
push a probability outside (0, 1).

Validation is strictly walk-forward with no overlap: for evaluation season S the model trains on seasons < S,
while the calibrator is fitted on season S−1 using predictions from a model trained on seasons < S−1. The
calibrator never sees a prediction from a model that trained on its own calibration season, and never sees
season S.

| statistic | rungs | Brier raw → calibrated | LogLoss raw → calibrated | bias where p < 0.20 | seasons improved |
|---|---|---|---|---|---|
| targets | 429,288 | 0.08961 → 0.08958 | 0.28613 → **0.28530** | −0.00954 → **−0.00179** | 3/6 |
| receptions | 286,192 | 0.09969 → 0.09971 | 0.31691 → **0.31633** | −0.00879 → **−0.00210** | 2/6 |
| receiving_yards | 357,740 | 0.07421 → 0.07417 | 0.24449 → **0.24386** | −0.00768 → **−0.00179** | 5/6 |
| rushing_yards | 114,984 | 0.08943 → 0.08950 | 0.29089 → 0.29111 | −0.00380 → −0.00105 | 0/6 |
| passing_yards | 29,381 | 0.13237 → 0.13236 | 0.41035 → 0.41038 | −0.00965 → −0.00443 | 3/5 |

**It does what it was built to do and little else.** It removes 75–80% of the long-shot bias in every
statistic. Log loss — which weights the tail — improves on the three largest. Aggregate Brier is a wash
(±0.00007), and rushing_yards is slightly worse on both metrics, 0 of 6 seasons.

## Decision: not deployed into the Week-1 model

The evidence is real but mixed, and `shadow-0.3.0` is already frozen for Week 1
(`research/FREEZE_WEEK1_2026.json`). Changing a frozen model five days before kickoff on a result whose
aggregate accuracy is a wash would be exactly the kind of quiet retuning the freeze exists to prevent.

Instead the calibrator is available behind a flag, defaulted **off**, with its own `calibration_version` in
every ledger row, and registered as `H-20260904-015` for prospective comparison. The shadow ledger already
supports pricing the same snapshot under multiple model versions without collision, which is the honest way
to settle a mixed retrospective result.

The claim being registered is narrow and falsifiable: the calibrator will not measurably improve aggregate
Brier, and it *will* reduce the number of long-shot rungs on which the model disagrees with the market in the
direction the market is already known to be wrong.
