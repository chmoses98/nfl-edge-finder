# Historical Game Flow Intelligence Championship: report pointer (RESEARCH_ONLY)

Reproduce: `python scripts/sim/gf_data.py` (via `gf_eval.py dev0|dev|select|freeze|final|report`). Numbers: `results.json`; coverage: `coverage_manifest.json`; protocol and outcome definitions: `PROTOCOL.md`, `gf_data.py`; registry: `model_registry.json`; leakage test: `perturbation.json`.
Verdict: market-informed trajectory forecasts (G0) are the baseline to use for final-state flow outputs; no challenger validated for those. Team tendency features validated for team opportunity (plays, dropbacks, pass rates) against a market-only baseline. Full discussion is in the session summary.
