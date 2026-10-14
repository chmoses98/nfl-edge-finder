# Minimal integration plan (DESIGN ONLY; no production file has been changed)

Order matters: step 1 fixes an existing defect and is independent of the new block; steps 2-4 add the block behind a flag.

## Step 1: enforce the close-split gate (both repos, small)
nfl-edge-finder
* `nfl_edge/handicap/script_block.py` (`game_script_inputs`, the `tv[team]` dict near line 191): drop `by_close_result` unless the gate artifact says SHOW. Read `research/game_script_v2/close_split_calibration.json` `verdict.show_split` through one helper; absent file or key means False (fail closed). Add `out["calibration_gates"] = {"close_win_split": "SHOW"|"SUPPRESS", ...}` so consumers read the gate instead of guessing.
* `scripts/research_export.py` (the forwarded-key tuple at ~line 1106): add `calibration_gates`.
* Tests: `tests/test_sim_script.py` stays (the simulator still computes the split for audit); add `tests/test_script_gate.py`: split removed when the verdict is False, when the file is missing and when the key is malformed; present when True.
SIFT (`sift-sports-intelligence`)
* `src/lib/scripts.ts` `closeSplit()` (line 229): return null unless `gsi.calibration_gates?.close_win_split === 'SHOW'`; the pooled "Keep It Close" script then appears for every publication. Pass the flag in at the call on line 146.
* `src/views/game/ScriptTab.tsx` lines 39-40: the sentence about the split is shown only when the split is shown.
* Tests: `tests/closeSplit.test.ts`, `tests/intelChain.test.ts`, `e2e/close-split.spec.ts`, `e2e/intel-chain.spec.ts` attach the gate flag when they exercise the split; add a case that the split is hidden without it.
Current state verified 2026-10-14 against local clones and `origin/main` (sift 6f4beef, nfl a978421): nothing reads `show_split` or `close_split_calibration.json`; the split titles ("<team> Win a Close One") render whenever both teams carry `by_close_result`.

## Step 2: trajectory table (nfl-edge-finder)
* New `scripts/data/build_flow_trajectories.py`: port of `scripts/sim/gf_data.py` (outcome definitions, score-swap repair, reliability flag) writing `data/silver/flow_trajectories.parquet` (about 5,900 REG games 2003 onward, ~12 columns, under 1 MB) plus a manifest with sha256 and coverage. First build about 160 s (25 seasons of pbp); a new season about 7 s. Run it where the nflverse pbp refresh already runs.
## Step 3: forecaster and packet wiring (nfl-edge-finder)
* New `nfl_edge/sim/game_flow.py`: `kernel_weights`, `tilt`, `record_from` copied verbatim from `scripts/sim/gf_models.py` (G0 bandwidth 6.0 / 9.0, half-life 6, floor 0.10, fixed; no fitted parameters) and a `build_game_flow(...)` equal to `research/game_flow_integration/reference_impl.py`.
* `nfl_edge/sim/prospective.py` `fast_implied_lines` (line 66): return the latest rung timestamp as `observed_at` in the diagnostics dict and carry it, with `center_source`, into `script_summary`'s `environment.centre` (`nfl_edge/sim/script.py`).
* `nfl_edge/handicap/script_block.py`: build `game_flow` from the packet's `game_environment` (centre and simulation means); fail open to `{"state": "UNAVAILABLE", "reason": ...}` like the existing sections. Forward `rush_att` in `team_volume`. Config flag `GAME_FLOW_ENABLED` (default off).
* `scripts/research_export.py`: add `game_flow` to the forwarded keys. Payload grows by about 1.5 KB per game against the 150 KB event budget.
* Tests: `tests/test_game_flow_contract.py` (schema `game_flow_schema_v1.json`; normalization; home/away mirror; impossible combinations; missing, stale and incomplete inputs each give UNAVAILABLE/STALE without a default; deterministic); `tests/test_game_flow_parity.py` (rebuild 2011 from the trajectory table and match the stored frozen G0_b3 forecasts to 1e-9 before the tilt); extend `tests/test_research_export.py`.
## Step 4: SIFT display (no redesign)
* New `src/lib/gameFlow.ts`: reads `extensions.game_script_inputs.game_flow`, applies `gates` and renders only DISPLAY / DISPLAY_WITH_CAUTION fields.
* `src/views/game/ScriptTab.tsx`: one compact "First half outlook" block under the existing scripts (halftime margin and total ranges, P(lead by 7+) per side). Copy states it is derived from the same market line. It is never used in `scriptFit` / bet explanations.
* Tests: `tests/gameFlow.test.ts`, one e2e that SUPPRESS fields never reach the DOM.

## Cost, freshness, rollback, parameters
* Compute: about 1 ms per game for kernel plus tilt on a 5,900-row table; a 16-game slate under a second. Memory trivial.
* Freshness: centre must be a Kalshi-implied line observed within 180 minutes; otherwise STALE. Validated horizon is the closing consensus line only; no opening-line history exists to validate earlier horizons.
* Rollback: remove the flag (block disappears; SIFT ignores a missing key); step 1 is reverted independently by setting the gate file to SHOW. All changes are additive; `script_version` stays `sim-script-1.1.0`.
* G0 parameters: used directly. They are bandwidths and a half-life, not fitted coefficients. Only the trajectory table is refreshed (append each completed season). Before enabling: run the parity test and a one-off comparison of Kalshi-implied versus consensus centres on the 2025 archive (not done here).
