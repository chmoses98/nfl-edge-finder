"""Hand-written interpretation for RESULTS_NFL.md. Numbers are pulled from the results at render time."""
from __future__ import annotations


def bottom_line(summary, wf):
    return ""


def design_text(summary):
    sp = summary["splits"]
    return "\n".join([
        f"- **Splits (chronological, frozen before evaluation):** development {sp['development']}; validation {sp['validation']}; "
        f"holdout {sp['holdout']}; {sp['check_2026']}; {sp['embargo']}. All tuning (shrinkage k, EWMA halflife, elasticities, stack weights, "
        "distribution parameters) uses development rows only; validation picks the model and the distribution family; the holdout was scored once "
        "after `results/nfl_frozen_selection.json` was written.",
        "- **Point-in-time features:** every feature at game g uses only games that kicked off earlier (pf_core.pit.lagged_features shifts within "
        "player/team; rolling ridge opponent ratings are refitted before every (season, week) block; positional priors are expanding means over "
        "earlier weeks). Pregame market context = closing spread/total from the nflverse schedule. `tests/test_nfl_pf.py` asserts that changing "
        "a game's outcome cannot change any feature of that game or earlier.",
        "- **Walk-forward:** A-D are formula models evaluated sequentially with frozen hyperparameters; E (LightGBM) is refitted before every "
        "season on all earlier seasons (2013+), so every 2016-2026 prediction is out-of-sample; the incumbents are refitted the same way "
        "(seasons 2016..T-1) with their own code.",
        "- **Availability:** player metrics are conditional on participation (>= 1 offensive snap or a stat line), the prop-settlement "
        "convention (DNP = void). 'Did he play' is post-game, so it is never a feature; the participation question is modelled separately "
        "from the final injury designation (see Availability).",
        "- **Populations (point-in-time):** receiving families = RB/WR/TE averaging >= 2 targets over their previous 4 games played; "
        "rushing families = RBs averaging >= 4 carries; QB families = the scheduled starter; anytime TD = RB/WR/TE meeting either role rule. "
        "A player's first career game is outside these populations by construction (no history); rookies enter after one game.",
        "- **Metrics:** MAE/RMSE/bias of the mean; CRPS and log score of the full integer distribution; randomised-PIT coverage; Brier at "
        "Kalshi-like rungs. Every comparison is paired on identical player-games with a game-clustered bootstrap (pf_core.metrics).",
    ])


def family_note(fam, wf):
    return ""


def holdout_note(wf):
    return ""


def errors_text(wf):
    return ""


def targets_bias_text(wf):
    return ""


def opponent_text(summary, wf):
    return ""


def opportunity_text(summary, wf):
    return ""


def calibration_text(summary, wf):
    return ""


def availability_text(wf):
    return ""


def gate_text(wf):
    return ""


def limitations_text():
    return "\n".join([
        "- Injury designations carry no timestamp in nflverse (rebuilt in place); they are treated as near-pregame (final Friday report). "
        "A timestamped vintage exists only from the 2026 context capture.",
        "- Conditional-on-participation evaluation: a consumer that does not void DNPs must use the participation hurdle (Availability section).",
        "- No route participation / personnel data was used (not downloaded); prior repo research found route share helps raw-EWMA targets.",
        "- The incumbent replay uses the research frame (current-season games included), so it measures the incumbent's design, not the live "
        "D1 history defect; its 2026 live error was larger (research/mean_defect).",
        "- pf_core issue (reported, not edited): `DistBatch._index` clips outcomes outside the support to the boundary, so `crps`/`logpmf` "
        "understate the loss of out-of-support outcomes. Worked around here by giving yards families supports down to -20/-30, by dropping 0-based "
        "NB from the yards candidates, and by left-padding the incumbents' 0-based pmfs before scoring.",
        "- 2026 weeks >= 5 are the untouched market holdout and are never scored here; forward projections for them are archived by the workflow.",
    ])
