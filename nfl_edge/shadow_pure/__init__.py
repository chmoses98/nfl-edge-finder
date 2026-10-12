"""PURE shadow collection (Phase 2): prospective, append-only forecasts of the frozen PURE_PLAYER_V1 arm.

RESEARCH ONLY. Nothing here selects, recommends, stakes, gates or publishes to a production surface. It records,
before kickoff, what the frozen market-independent arms forecast for every eligible NFL skill player-game, keeps
the market listing / quotes and the incumbent market-informed projections in SEPARATE file families, and later
scores matured rows against nflverse box scores.

Record families (all write-once, under one store root; see store.py and docs/research/PURE_SHADOW_NFL.md):

    projections/            pure_forecast.v1 rows, one per (game, player, statistic), arms PURE_PLAYER_V1 and
                            PURE_EWM_BASELINE. Football inputs only; validated with the vendored pure_gate.
    market/                 Kalshi player-stat listings and the latest captured quote at or before the as_of, read
                            from the existing capture outputs (read-only). Never read by the projection code.
    incumbent_diagnostic/   DATA_PLAYER_V4 / DATA_PLAYER_V5 records from the existing shadow-v2 projection outputs,
                            labelled MARKET_INFORMED_DIAGNOSTIC. Their environment is market-implied; they are never
                            mixed into the PURE files or scored as PURE.
    inputs/                 per-capture input manifest: every input file's url, fetched_at, sha256, last-modified.
    outcomes/               nflverse box-score outcomes, one row per player-game-statistic, with fetched_at.
    reconciliation/         projection <-> outcome joins and market-settlement-vs-sports-outcome mismatch flags.
    evaluations/            pure_gate compare scorecards on matured rows (full eligible population and the pregame
                            market-listed cohort).
    manifests/              one manifest per run listing every file it wrote with its sha256 and the sha256 of the
                            previous manifest (a hash chain).
"""
COLLECTOR_VERSION = "nfl-pure-shadow-1.0.0"
SPORT = "NFL"
STORE_SUBDIR = "data/shadow_pure/nfl"

# PURE_PLAYER_V1 is FROZEN: the collector refuses to run if the model package differs from the code the
# preregistered study evaluated (model code frozen at 0441dfc, merged unchanged in 762d69d). The pin is the sha256
# over the package's .py files in sorted order (see frozen.code_sha256).
PURE_V1_FROZEN_GIT = "0441dfc"
PURE_V1_CODE_SHA256 = "c2869ed8a3c91cb513e6cf6bb53b497d97d81c22b85dbc0a9e16d4913b908d58"

# Data window identical to the preregistered study (scripts/research/pure_player_v1_study.py loads 2013..S and
# fits on [2014, S)).
DATA_FIRST_SEASON = 2013

# Capture kinds: (name, earliest minutes before kickoff, latest minutes before kickoff). A (game, kind) pair is
# captured at most once; the as_of of a capture is the instant it ran, not the nominal target.
CAPTURE_WINDOWS = (
    ("DAY_BEFORE", 30 * 60, 18 * 60),
    ("MORNING_OF", 8 * 60, 165),
    ("FINAL_T90", 90, 30),
)
ADHOC = "ADHOC"            # manual / dry-run captures outside the windows (still strictly pregame)
