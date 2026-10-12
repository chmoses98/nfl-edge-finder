# PURE_PLAYER_V1_2: held-out results (research only)

* **Preregistration:** `docs/research/PURE_PLAYER_V1_2_PREREGISTRATION.md`, committed alone in **cc452fd** and
  pushed before any V1_2 held-out forecast was scored.
* **Code:** frozen at **7f81ed2**, unchanged afterwards.
* **Command:**
  ```
  python3 scripts/research/pure_player_v1_2_study.py --data-root <root> --cache <dir> --seasons 2024,2025,2026 \
      --label holdout_2024_2025_2026 --arms <dir>/pure_gap_arms_2024_2025.pkl --mutation
  ```
  The full output is `holdout_2024_2025_2026.json`. The V4 arms for 2024 and 2025 are reused from the gap study's
  cache, and their MAE is identical to `research/pure_player_v1/results.json`. V4 for 2026 was fitted in this run.
* **Data:** nflverse files retrieved 2026-10-12T01:53Z. The 2024 and 2025 files are byte-identical to the
  PURE_PLAYER_V1 manifest.

## Verdict (preregistered rule, primary 2024 + 2025, V1_2 − V1): **REJECTED**

| criterion | result | pass |
|---|---|---|
| (a) ΔMAE < 0 on ≥ 6 of 9 | 5 of 9: snap share, targets (−0.0001), carries, rushing yards, passing yards. Passing attempts are identical (Δ 0), because that stage has no new input | no |
| (a) CI < 0 on ≥ 3 | 3: snap share, carries, rushing yards | yes |
| (b) no ΔMAE CI > 0 | **receiving yards +0.026 [+0.001, +0.049]** | no |
| (b) no ΔBrier CI > 0 | **completions +0.0008 [+0.00001, +0.0016]** | no |
| (c) coverage within tolerance | yes; the largest is targets Δ\|cov − 0.8\| CI [+0.0002, +0.0035], against a tolerance of 0.01 | yes |
| (d) 2026 non-inferiority | no statistic significantly worse | yes |

PURE_PLAYER_V1 remains the PURE arm in collection. Nothing is promoted or wired.

## V1_2 vs frozen V1 (Δ = V1_2 − V1; game-clustered 95% CI, B = 1000)

The MAE V1 → V1_2 column and the ΔMAE, ΔBrier and 2024 columns are for the primary pooled 2024 + 2025 window;
the 2025 and 2026 columns are single seasons.

| statistic | n (2024+25) | MAE V1 → V1_2 | ΔMAE [CI] | ΔBrier [CI] | 2024 ΔMAE | 2025 ΔMAE | 2026 wk1-5 ΔMAE (n) |
|---|---|---|---|---|---|---|---|
| snap share | 12,567 | 0.1212 → 0.1206 | **−0.0006** [−0.0009, −0.0003] | **−0.0015** [−0.0022, −0.0007] | −0.0007 * | −0.0005 * | **−0.0018** [−0.0026, −0.0010] (1,506) |
| targets | 11,559 | 1.5597 → 1.5595 | −0.0001 [−0.0024, +0.0024] | +0.0000 | −0.0009 | +0.0006 | −0.0038 [−0.0103, +0.0032] (1,606) |
| receptions | 11,559 | 1.1985 → 1.1992 | +0.0007 [−0.0010, +0.0026] | +0.0000 | +0.0002 | +0.0012 | +0.0008 (1,606) |
| receiving yards | 11,559 | 15.335 → 15.362 | **+0.026** [+0.001, +0.049] | −0.0001 | +0.024 | +0.029 | +0.034 [−0.025, +0.090] (1,606) |
| carries | 4,028 | 3.038 → 3.027 | **−0.011** [−0.020, −0.001] | **−0.0011** [−0.0020, −0.0003] | −0.021 * | −0.001 | −0.009 (567) |
| rushing yards | 4,028 | 18.137 → 18.074 | **−0.063** [−0.116, −0.012] | −0.0001 | −0.083 * | −0.044 | +0.091 [−0.042, +0.240] (567) |
| passing attempts | 1,088 | 6.787 → 6.787 | 0 | 0 | 0 | 0 | 0 (154) |
| completions | 1,088 | 4.689 → 4.692 | +0.003 [−0.013, +0.017] | **+0.0008** [+0.00001, +0.0016] | +0.008 | −0.002 | +0.002 (154) |
| passing yards | 1,088 | 59.26 → 59.25 | −0.01 [−0.40, +0.38] | −0.0006 | −0.28 | +0.26 | −0.29 [−1.06, +0.54] (154) |

\* the season's CI excludes 0.

* **By position group** (2024+2025, ΔMAE):
  * RB carries −0.016 [−0.028, −0.002], RB rushing yards −0.081 [−0.149, −0.012], RB snap share −0.0013;
  * WR snap share −0.0009, other WR statistics level;
  * **TE receiving worse**: yards +0.085 [+0.052, +0.119], receptions +0.0041, targets +0.0037;
  * QB snap share +0.0015 (worse).
* **Against the baseline**, V1_2 has ΔMAE CI < 0 on all 9 statistics, as V1 does.
* **Against the market-informed V4_MARKET_CLOSE** (descriptive), the gap is essentially V1's:
  * targets +0.013, receptions +0.008, receiving yards +0.14, carries +0.039, passing yards +1.04 (all CI > 0);
  * snap share +0.0012;
  * completions −0.032 and passing attempts −0.013 (CIs span 0).

## Reading (not part of the verdict)

The three feature families together moved V1 by less than 1% of MAE on every statistic. Each part reached the
gap differently:

* **(C) Available pool.** It recovered a small, consistent part of the snap-share deficit: −0.0006 of V1's
  +0.0018 gap to V4. The rest of that deficit is V4's injury-report signal, which no box-score persistence feature
  reproduces. The decomposition located the gap in *new* absences and returns, not persistent ones.
* **(B) Positional opponent.** The carry and rushing gains are RB-specific and come from the rushing-side
  features. The TE receiving loss is the clearest failure: the allowed-to-TE rates are the noisiest group rates,
  because TE target volume is small. This matches the decomposition's finding that the opponent channel holds
  little exploitable signal.
* **(A) Environment-conditioned efficiency.** The football-only team-points forecast did not reproduce the market
  environment's yardage-efficiency value. Passing yards moved −0.01 against the +1.05 that the market term is
  worth. PURE's points forecast (MAE 7.37) is not close enough to the closing implied total (7.16) to carry that
  information.

## Runtime non-leakage (real data, 2025)

V1_2's forecasts are **bit-identical**: 29,188 rows, sha256 `8372c7b7…`, under the original, removed and
randomised schedule market columns (`mutation_2025` in the JSON). The synthetic tests in
`tests/test_pure_player_v1_2.py` pass:
* mutation including partial blanking;
* future box score;
* defence features prior-only;
* source scan;
* V1 source sha256 pin.

## Limitations

* **Design contamination.** The primary window was used by the gap decomposition to choose the components; this is
  disclosed in the preregistration. 2026 weeks 1-5 is the untouched guard, but it is small (154 QB rows, 567
  rushing rows).
* **No PIT injuries.** No 2025 source is certified, so the largest sports-only error source (availability) could
  not be tested on this window. Testing it needs the prospective PIT capture from PR #137.
