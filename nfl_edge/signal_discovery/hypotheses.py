"""Pre-registered NFL hypotheses (Stage B, set 1). RESEARCH ONLY.

Written and committed BEFORE any closing line, Kalshi ladder or outcome was joined to these feature rows.
Tier / regime thresholds are round numbers read off the OUTCOME-BLIND distribution of the feature itself
(``THRESHOLDS``, recorded with the quantile they approximate); none was chosen by looking at a result.

Game kinds reuse the CFB evaluator's vocabulary (SIDE, TOTAL, SLOPE_SIDE, SLOPE_TOTAL, SLOPE_TEAMPTS,
FOOTBALL_ONLY, UNAVAILABLE) so both sports are judged by identical arithmetic and the same status rule.
"""

from __future__ import annotations

from typing import Any

#: filled from the outcome-blind feature distribution (2015-2026), see FOOTBALL_SIGNAL_DISCOVERY_WAVE1_PROTOCOL.md
THRESHOLDS: dict[str, Any] = {}

GAME_SET1: list[dict[str, Any]] = []  # populated by build_game_set1() once THRESHOLDS are fixed


def build_game_set1(th: dict[str, float]) -> list[dict[str, Any]]:
    mod, strong, close = th["control_moderate"], th["control_strong"], th["closeness"]
    return [
        {"id": "NFL-GAME-001", "name": "Efficiency CONTROL (|net EPA| >= moderate) -> winner / moneyline", "family": "CONTROL",
         "kind": "SIDE", "population": {"rule": "control", "strength": None}, "side": "control", "primary_market": "ML",
         "markets": ["ML", "ATS"],
         "interpretation": "The side whose offence-vs-defence EPA matchup is better should win more (prompt 39.1)."},
        {"id": "NFL-GAME-002", "name": "MODERATE efficiency CONTROL -> closing spread", "family": "CONTROL", "kind": "SIDE",
         "population": {"rule": "control", "strength": "MODERATE"}, "side": "control", "primary_market": "ATS", "markets": ["ATS", "ML"],
         "interpretation": f"|net EPA/play| in [{mod}, {strong}): a smaller, less visible efficiency edge (CFB analogue)."},
        {"id": "NFL-GAME-003", "name": "STRONG efficiency CONTROL -> closing spread", "family": "CONTROL", "kind": "SIDE",
         "population": {"rule": "control", "strength": "STRONG"}, "side": "control", "primary_market": "ATS", "markets": ["ATS", "ML"],
         "interpretation": f"|net EPA/play| >= {strong}: the most visible edge; expected to be priced."},
        {"id": "NFL-GAME-004", "name": "Opponent-adjusted EPA net (continuous) -> margin / ATS", "family": "SUSTAINED_EFFICIENCY",
         "kind": "SLOPE_SIDE", "population": {"rule": "all"}, "feature": "net.epa_play", "expected_sign": 1, "primary_market": "ATS",
         "markets": ["ATS"], "interpretation": "Prompt 39.1/39.2: overall efficiency vs winner and vs spread."},
        {"id": "NFL-GAME-005", "name": "QB / dropback efficiency mismatch -> margin / ATS", "family": "QB_EFFICIENCY",
         "kind": "SLOPE_SIDE", "population": {"rule": "all"}, "feature": "net.dropback_epa", "expected_sign": 1, "primary_market": "ATS",
         "markets": ["ATS"], "interpretation": "Prompt 39.3: the passing game drives NFL margins."},
        {"id": "NFL-GAME-006", "name": "Pass offence x pass defence, beyond overall efficiency -> margin / ATS", "family": "PASSING",
         "kind": "SLOPE_SIDE", "population": {"rule": "all"}, "feature": "net.dropback_epa", "controls": ["net.epa_play"],
         "expected_sign": 1, "primary_market": "ATS", "markets": ["ATS"],
         "interpretation": "Prompt 39.4. CFB found the market OVER-rates passing edges given efficiency (CFB-SIG-014): a cross-sport test."},
        {"id": "NFL-GAME-007", "name": "Rush offence x rush defence, beyond overall efficiency -> margin / ATS", "family": "RUSHING",
         "kind": "SLOPE_SIDE", "population": {"rule": "all"}, "feature": "net.designed_rush_epa", "controls": ["net.epa_play"],
         "expected_sign": 1, "primary_market": "ATS", "markets": ["ATS"],
         "interpretation": "Prompt 39.5. CFB found rushing edges UNDER-priced given efficiency (CFB-SIG-015): a cross-sport replication test."},
        {"id": "NFL-GAME-008", "name": "Pressure x protection (sack-rate matchup net) -> margin / ATS", "family": "PRESSURE",
         "kind": "SLOPE_SIDE", "population": {"rule": "all"}, "feature": "net.sack_rate", "expected_sign": 1, "primary_market": "ATS",
         "markets": ["ATS"], "interpretation": "Prompt 39.6: a pass rush meeting weak protection kills drives."},
        {"id": "NFL-GAME-009", "name": "Pressure-rate matchup (participation, 2016-2025 only) -> ATS", "family": "PRESSURE",
         "kind": "SLOPE_SIDE", "population": {"rule": "all"}, "feature": "net.pressure_rate", "controls": ["net.sack_rate"],
         "expected_sign": 1, "primary_market": "ATS", "markets": ["ATS"],
         "interpretation": "Pressure beyond sacks. NOT prospectively reproducible: nflverse publishes no in-season 2026 participation file."},
        {"id": "NFL-GAME-010", "name": "Explosive offence x explosive prevention -> margin / ATS", "family": "EXPLOSIVENESS",
         "kind": "SLOPE_SIDE", "population": {"rule": "all"}, "feature": "net.explosive_rate", "expected_sign": 1, "primary_market": "ATS",
         "markets": ["ATS"], "interpretation": "Prompt 39.7."},
        {"id": "NFL-GAME-011", "name": "Expected pace (both teams' adjusted plays) -> total residual", "family": "PACE",
         "kind": "SLOPE_TOTAL", "population": {"rule": "all"}, "feature": "env.plays", "expected_sign": 1, "primary_market": "TOTAL",
         "markets": ["TOTAL"], "interpretation": "Prompt 39.8: more snaps, more points."},
        {"id": "NFL-GAME-012", "name": "Tempo (adjusted seconds per play) -> total residual", "family": "PACE",
         "kind": "SLOPE_TOTAL", "population": {"rule": "all"}, "feature": "env.sec_per_play", "expected_sign": -1,
         "primary_market": "TOTAL", "markets": ["TOTAL"], "interpretation": "Slower teams, fewer possessions."},
        {"id": "NFL-GAME-013", "name": "DEFENSIVE SUPPRESSION (both defences >= +0.5 SD on EPA allowed) -> under", "family": "DEFENSIVE_SUPPRESSION",
         "kind": "TOTAL", "population": {"rule": "flag", "column": "flag.def_suppression"}, "direction": -1, "primary_market": "TOTAL",
         "markets": ["TOTAL"], "interpretation": "Prompt 39.9."},
        {"id": "NFL-GAME-014", "name": "Defensive quality sum (continuous) -> total residual", "family": "DEFENSIVE_SUPPRESSION",
         "kind": "SLOPE_TOTAL", "population": {"rule": "all"}, "feature": "def_quality_sum.epa", "expected_sign": -1,
         "primary_market": "TOTAL", "markets": ["TOTAL"], "interpretation": "Prompt 39.9 continuous."},
        {"id": "NFL-GAME-015", "name": "CONTROL style: efficiency favourite that is run-leaning -> under", "family": "GAME_SCRIPT",
         "kind": "TOTAL", "population": {"rule": "flag", "column": "flag.control_run_style"}, "direction": -1, "primary_market": "TOTAL",
         "markets": ["TOTAL", "ATS"],
         "interpretation": "Prompt 39.10: a team that owns the matchup and leans on the run should shorten the game."},
        {"id": "NFL-GAME-016", "name": "Football scoring-baseline margin vs closing spread disagreement -> ATS", "family": "MARKET_DISAGREEMENT",
         "kind": "SLOPE_SIDE", "population": {"rule": "all"}, "feature": "gap.margin", "expected_sign": 1, "primary_market": "ATS",
         "markets": ["ATS"], "interpretation": "Does the opponent-adjusted football baseline hold information the spread lacks?"},
        {"id": "NFL-GAME-017", "name": "Football scoring-baseline total vs closing total disagreement -> total residual",
         "family": "MARKET_DISAGREEMENT", "kind": "SLOPE_TOTAL", "population": {"rule": "all"}, "feature": "gap.total", "expected_sign": 1,
         "primary_market": "TOTAL", "markets": ["TOTAL"], "interpretation": "As 016 for totals."},
        {"id": "NFL-GAME-018", "name": "Team scoring expectation vs DERIVED implied home team total", "family": "TEAM_TOTAL",
         "kind": "SLOPE_TEAMPTS", "population": {"rule": "all"}, "feature": "gap.home_team_total", "expected_sign": 1,
         "primary_market": "TEAM_TOTAL_DERIVED", "markets": ["TEAM_TOTAL_DERIVED"],
         "interpretation": "No historical team-total line in nflverse; implied = (total - home spread)/2. DERIVED."},
        {"id": "NFL-GAME-019", "name": "Rest differential -> home ATS", "family": "CONTEXT", "kind": "SLOPE_SIDE",
         "population": {"rule": "all"}, "feature": "ctx.rest_diff", "expected_sign": 1, "primary_market": "ATS", "markets": ["ATS"],
         "interpretation": "Section 13 context: is extra rest priced?"},
        {"id": "NFL-GAME-020", "name": "Short-week team (rest <= 5 vs opponent >= 6) -> ATS", "family": "CONTEXT", "kind": "SIDE",
         "population": {"rule": "flag", "column": "flag.short_week_side"}, "side": "column:flag.short_week_side", "expected_sign": -1,
         "primary_market": "ATS", "markets": ["ATS"], "interpretation": "Short week hurts preparation and recovery. Expected NEGATIVE."},
        {"id": "NFL-GAME-021", "name": "Off-bye team (rest >= 13 vs opponent <= 8) -> ATS", "family": "CONTEXT", "kind": "SIDE",
         "population": {"rule": "flag", "column": "flag.bye_side"}, "side": "column:flag.bye_side", "primary_market": "ATS",
         "markets": ["ATS"], "interpretation": "Extra preparation."},
        {"id": "NFL-GAME-022", "name": "Divisional game: market underdog ATS", "family": "CONTEXT", "kind": "SIDE",
         "population": {"rule": "flag", "column": "div_game"}, "side": "market_underdog", "primary_market": "ATS", "markets": ["ATS"],
         "interpretation": "Familiarity compresses margins."},
        {"id": "NFL-GAME-023", "name": "QB change (starter differs from previous game; NEAR_PIT) -> ATS of that team", "family": "CONTEXT",
         "kind": "SIDE", "population": {"rule": "flag", "column": "flag.qb_change_side"}, "side": "column:flag.qb_change_side",
         "expected_sign": -1, "primary_market": "ATS", "markets": ["ATS"],
         "interpretation": "Realised starter ids (announced pregame in practice). Previously REJECTED_AT_CLOSE in H-005."},
        {"id": "NFL-GAME-024", "name": "Indoor (dome/closed roof) -> total residual", "family": "CONTEXT", "kind": "TOTAL",
         "population": {"rule": "flag", "column": "flag.indoor"}, "direction": 1, "primary_market": "TOTAL", "markets": ["TOTAL"],
         "interpretation": "No weather. (Forecast weather vintages exist only from 2026-09; observed game weather is post hoc.)"},
        {"id": "NFL-GAME-025", "name": "CLOSENESS (|net EPA| below the closeness threshold) -> market underdog ATS", "family": "CLOSENESS",
         "kind": "SIDE", "population": {"rule": "flag", "column": "closeness"}, "side": "market_underdog", "primary_market": "ATS",
         "markets": ["ATS"], "football_outcome": "close8",
         "interpretation": f"|net EPA/play| <= {close}: even matchup, the points should be worth more."},
        {"id": "NFL-GAME-026", "name": "Efficiency CONTROL -> first-half margin (football only)", "family": "CONTROL", "kind": "FOOTBALL_ONLY",
         "population": {"rule": "control", "strength": None}, "side": "control", "football_outcome": "margin_1h", "primary_market": None,
         "markets": [], "interpretation": "Kalshi 1H lines exist only for 2025-26 and are thin."},
        {"id": "NFL-GAME-027", "name": "Weather (forecast vintages)", "family": "CONTEXT", "kind": "UNAVAILABLE",
         "reason": "Forecast vintages exist only from 2026-09-04; historical temp/wind in the schedule are observed (post hoc). Not tested.",
         "primary_market": None, "markets": [], "interpretation": "Wind suppresses passing and kicking."},
        {"id": "NFL-GAME-028", "name": "Line / injury shocks (OL, skill, defensive injuries)", "family": "CONTEXT", "kind": "UNAVAILABLE",
         "reason": "No timestamped historical injury vintages before 2026-09-13; the final weekly report cannot be aligned to the closing line. Not tested at game level.",
         "primary_market": None, "markets": [], "interpretation": "Injuries change true team strength."},
        {"id": "NFL-BASE-001", "name": "BASELINE: home team ATS", "family": "BASELINE", "kind": "SIDE", "population": {"rule": "not_neutral"},
         "side": "home", "primary_market": "ATS", "markets": ["ATS", "ML"], "interpretation": "Reference."},
        {"id": "NFL-BASE-002", "name": "BASELINE: market favourite ATS", "family": "BASELINE", "kind": "SIDE", "population": {"rule": "all"},
         "side": "market_favorite", "primary_market": "ATS", "markets": ["ATS", "ML"], "interpretation": "Reference."},
        {"id": "NFL-BASE-003", "name": "BASELINE: RAW (unadjusted) EPA net -> margin / ATS", "family": "BASELINE", "kind": "SLOPE_SIDE",
         "population": {"rule": "all"}, "feature": "raw.epa_net", "expected_sign": 1, "primary_market": "ATS", "markets": ["ATS"],
         "interpretation": "Raw comparator for NFL-GAME-004."},
    ]


WALK_FORWARD = {
    "WF-ATS": {"target": "home_ats_resid",
               "features": ["net.epa_play", "net.dropback_epa", "net.designed_rush_epa", "net.sack_rate", "net.explosive_rate", "gap.margin", "ctx.rest_diff"],
               "first_test_season": 2018, "pick_threshold_points": 2.0},
    "WF-TOTAL": {"target": "total_resid", "features": ["gap.total", "env.plays", "env.sec_per_play", "def_quality_sum.epa", "off_quality_sum.epa"],
                 "first_test_season": 2018, "pick_threshold_points": 2.0},
    "WF-ML": {"target": "home_win", "market_feature": "logit.ml_home_novig", "features": ["net.epa_play", "baseline.home_margin"],
              "first_test_season": 2018, "train_first_season": 2015},
}

STATUS_RULE = {
    "q_football": 0.05, "q_market": 0.05, "q_market_watch": 0.10, "min_n_market": 100,
    "min_seasons_same_sign_share": 0.6, "efficient_ci_halfwidth_cover": 0.05,
    "blocks": {"A": [2015, 2016, 2017, 2018, 2019], "B": [2020, 2021, 2022, 2023, 2024, 2025]},
}

# ------------------------------------------------------------------------------------------------ props
#: prop families. share_col / min_share define the eligible (pregame) population.
PROP_FAMILIES = [
    {"id": "QB_pass_yards", "positions": ["QB"], "stat": "pass_yards", "share_col": "sh_attempt_l", "min_share": 0.5, "kalshi_stat": "passing_yards"},
    {"id": "QB_attempts", "positions": ["QB"], "stat": "attempts", "share_col": "sh_attempt_l", "min_share": 0.5, "kalshi_stat": "attempts"},
    {"id": "QB_completions", "positions": ["QB"], "stat": "completions", "share_col": "sh_attempt_l", "min_share": 0.5, "kalshi_stat": "completions"},
    {"id": "QB_pass_td", "positions": ["QB"], "stat": "pass_td", "share_col": "sh_attempt_l", "min_share": 0.5, "kalshi_stat": "passing_tds"},
    {"id": "QB_ints", "positions": ["QB"], "stat": "ints", "share_col": "sh_attempt_l", "min_share": 0.5, "kalshi_stat": "interceptions"},
    {"id": "QB_rush_yards", "positions": ["QB"], "stat": "rush_yards", "share_col": "sh_attempt_l", "min_share": 0.5, "kalshi_stat": "rushing_yards"},
    {"id": "RB_carries", "positions": ["RB"], "stat": "carries", "share_col": "sh_carry_l", "min_share": 0.20, "kalshi_stat": "carries"},
    {"id": "RB_rush_yards", "positions": ["RB"], "stat": "rush_yards", "share_col": "sh_carry_l", "min_share": 0.20, "kalshi_stat": "rushing_yards"},
    {"id": "RB_receptions", "positions": ["RB"], "stat": "receptions", "share_col": "sh_target_l", "min_share": 0.05, "kalshi_stat": "receptions"},
    {"id": "RB_rec_yards", "positions": ["RB"], "stat": "rec_yards", "share_col": "sh_target_l", "min_share": 0.05, "kalshi_stat": "receiving_yards"},
    {"id": "WR_receptions", "positions": ["WR"], "stat": "receptions", "share_col": "sh_target_l", "min_share": 0.10, "kalshi_stat": "receptions"},
    {"id": "WR_rec_yards", "positions": ["WR"], "stat": "rec_yards", "share_col": "sh_target_l", "min_share": 0.10, "kalshi_stat": "receiving_yards"},
    {"id": "TE_receptions", "positions": ["TE"], "stat": "receptions", "share_col": "sh_target_l", "min_share": 0.08, "kalshi_stat": "receptions"},
    {"id": "TE_rec_yards", "positions": ["TE"], "stat": "rec_yards", "share_col": "sh_target_l", "min_share": 0.08, "kalshi_stat": "receiving_yards"},
]

#: the opportunity model's fixed feature list (TEAM VOLUME -> PLAYER SHARE -> EFFICIENCY -> MATCHUP/CONTEXT)
PROP_MODEL = {
    "model_features": [
        # baselines as inputs (the model must beat them, not ignore them)
        "b_ewma.{stat}", "b_usage.{stat}",
        # player share / role
        "sh_target_s", "sh_target_l", "sh_carry_s", "sh_carry_l", "sh_attempt_s", "sh_attempt_l", "snap_share_s", "snap_share_l",
        "last_sh_target", "last_sh_carry", "last_snap_share", "sh_rz_target_l", "sh_rz_carry_l",
        # player efficiency (shrunk to frozen position priors)
        "rt_ypt", "rt_catch_rate", "rt_adot", "rt_ypc", "rt_ypa", "rt_comp_rate", "rt_int_rate", "rt_pass_td_rate", "rt_scramble_rate",
        # team volume (own EWMA)
        "off_pass_att", "off_rush_att", "off_plays", "off_neutral_pass_rate",
        # opponent-adjusted matchup context (game layer)
        "ctx.team_plays", "ctx.env_plays", "ctx.team_neutral_pass_rate", "ctx.expected_script", "ctx.team_points",
        "ctx.opp_pass_def_q", "ctx.opp_rush_def_q", "ctx.opp_expl_pass_def_q", "ctx.team_sack_rate", "ctx.opp_pass_rush_q",
        "ctx.team_protection_q", "ctx.team_qb_q", "ctx.team_dropback_epa", "ctx.team_rush_epa", "ctx.is_home",
    ],
    "groups": {
        "PACE": ["ctx.team_plays", "ctx.env_plays"],
        "SCRIPT": ["ctx.expected_script", "ctx.team_points"],
        "PASS_DEF": ["ctx.opp_pass_def_q", "ctx.opp_expl_pass_def_q"],
        "RUSH_DEF": ["ctx.opp_rush_def_q"],
        "PRESSURE": ["ctx.team_sack_rate", "ctx.opp_pass_rush_q", "ctx.team_protection_q"],
        "QB_EFF": ["ctx.team_qb_q", "ctx.team_dropback_epa"],
        "PASS_TENDENCY": ["ctx.team_neutral_pass_rate", "off_neutral_pass_rate"],
        "ROLE_RECENCY": ["sh_target_s", "sh_carry_s", "sh_attempt_s", "snap_share_s", "last_sh_target", "last_sh_carry", "last_snap_share"],
        "HOME": ["ctx.is_home"],
    },
    #: section 19 interactions, per family: (a, b, name)
    "interactions": {
        "QB_pass_yards": [("ctx.env_plays", "ctx.opp_pass_def_q", "IX_PACE_x_PASSDEF"), ("ctx.team_sack_rate", "ctx.opp_pass_def_q", "IX_PRESSURE_x_PASSDEF")],
        "QB_attempts": [("ctx.env_plays", "ctx.expected_script", "IX_PACE_x_SCRIPT")],
        "WR_receptions": [("sh_target_l", "ctx.opp_pass_def_q", "IX_SHARE_x_PASSDEF"), ("sh_target_l", "ctx.expected_script", "IX_SHARE_x_SCRIPT")],
        "WR_rec_yards": [("sh_target_l", "ctx.opp_pass_def_q", "IX_SHARE_x_PASSDEF"), ("sh_target_l", "ctx.team_qb_q", "IX_SHARE_x_QBEFF")],
        "TE_receptions": [("sh_target_l", "ctx.opp_pass_def_q", "IX_SHARE_x_PASSDEF")],
        "TE_rec_yards": [("sh_target_l", "ctx.opp_pass_def_q", "IX_SHARE_x_PASSDEF")],
        "RB_carries": [("sh_carry_l", "ctx.expected_script", "IX_SHARE_x_SCRIPT"), ("sh_carry_l", "ctx.opp_rush_def_q", "IX_SHARE_x_RUSHDEF")],
        "RB_rush_yards": [("sh_carry_l", "ctx.expected_script", "IX_SHARE_x_SCRIPT"), ("sh_carry_l", "ctx.opp_rush_def_q", "IX_SHARE_x_RUSHDEF")],
        "RB_receptions": [("sh_target_l", "ctx.expected_script", "IX_SHARE_x_SCRIPT"), ("sh_target_l", "ctx.team_sack_rate", "IX_SHARE_x_PRESSURE")],
    },
    #: pre-registered expected direction of each group's football effect, used only for interpretation
    "economic_rule": {"relative_margin": 0.10, "checkpoints": {"2025": "T-90m", "2026": "LAST_PREGAME (<= 24h before kickoff)"}},
}


# --------------------------------------------------------------------------------------------------------------------
# GAME SET 2 -- written AFTER the Stage A screen (block A 2015-2019 only) and BEFORE block B judged them.
# --------------------------------------------------------------------------------------------------------------------
GAME_SET2: list[dict[str, Any]] = [
    {"id": "NFL-DSC-001", "name": "Within STRONG CONTROL: control side's neutral pass-rate advantage -> control-side ATS (negative)",
     "family": "STYLE", "kind": "SLOPE_SIDE", "population": {"rule": "control", "strength": "STRONG"}, "side": "control",
     "feature": "ctrl.offdiff_neutral_pass_rate", "expected_sign": -1, "primary_market": "ATS", "markets": ["ATS"],
     "screen_evidence": "block A within STRONG: -2.26 pts/SD, z -2.73, whole-screen q 0.027 (n 245)",
     "interpretation": "A strong efficiency side that is ALSO the pass-heavier offence may be over-priced (cf. CFB-SIG-014 / CFB-DSC-003)."},
    {"id": "NFL-DSC-002", "name": "Offensive success-rate quality difference -> home ATS",
     "family": "SUSTAINED_EFFICIENCY", "kind": "SLOPE_SIDE", "population": {"rule": "all"}, "feature": "offdiff.success_rate",
     "expected_sign": 1, "primary_market": "ATS", "markets": ["ATS"],
     "screen_evidence": "block A: +0.81 pts/SD, z +2.27, q 0.091, 5/5 seasons",
     "interpretation": "Down-to-down success (staying on schedule) is less visible than EPA/points and may be under-priced."},
    {"id": "NFL-DSC-003", "name": "Defences that slow opponents (adjusted seconds/play allowed, both teams) -> total residual (under)",
     "family": "PACE", "kind": "SLOPE_TOTAL", "population": {"rule": "all"}, "feature": "defsum.sec_per_play",
     "expected_sign": -1, "primary_market": "TOTAL", "markets": ["TOTAL"],
     "screen_evidence": "block A: -0.85 pts/SD, z -2.27, q 0.091, 4/5 seasons",
     "interpretation": "Possession count depends on both teams' tempo; totals may price offences' tempo but not the defensive side of it."},
    {"id": "NFL-DSC-004", "name": "Efficiency mismatch size |net EPA| -> total residual (under)",
     "family": "GAME_SCRIPT", "kind": "SLOPE_TOTAL", "population": {"rule": "all"}, "feature": "abs_net.epa_play",
     "expected_sign": -1, "primary_market": "TOTAL", "markets": ["TOTAL"],
     "screen_evidence": "block A: -0.78 pts/SD, z -2.13, q 0.124, 5/5 seasons",
     "interpretation": "Lopsided matchups produce leading-team clock control in the second half: fewer possessions than a total built from two scoring rates."},
    {"id": "NFL-DSC-005", "name": "Neutral pass-rate difference (unconditional) -> home ATS (negative) -- cross-sport test of CFB-DSC-003",
     "family": "STYLE", "kind": "SLOPE_SIDE", "population": {"rule": "all"}, "feature": "offdiff.neutral_pass_rate",
     "expected_sign": -1, "primary_market": "ATS", "markets": ["ATS"],
     "screen_evidence": "not selected from the NFL screen; registered to test whether the CFB pass-tendency over-pricing replicates",
     "interpretation": "The pass-heavier side may be over-rated by a market that anchors on passing production."},
]
