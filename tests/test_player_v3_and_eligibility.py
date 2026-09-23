"""DATA_PLAYER_V3 inputs, abstention and production eligibility.

The properties pinned here are the ones the 2026 week-2 failure turned on:

  * a prospective row gets its game environment from the MARKET at the cutoff, never a zero (the v2 defect), and a
    game with no environment gets no data distribution at all;
  * current-season games enter the history only once they are complete before the cutoff -- never a game that has
    not finished, never the game being projected;
  * the starting quarterback is the depth-chart QB1 at the cutoff;
  * a large model-market disagreement is a warning, never an edge;
  * eligibility counts GAMES, not rows: a thousand rungs from three games are three observations;
  * a known-defect arm is DISABLED whatever its numbers say, and nothing unmeasured is ever TRUSTED.
"""
import os
import sys
from datetime import datetime, timedelta, timezone

import numpy as np
import pandas as pd
import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
from nfl_edge.engines.player import abstention as AB                    # noqa: E402
from nfl_edge.engines.player import data_dist as DD                     # noqa: E402
from nfl_edge.engines.player import prospective_v3 as PV3               # noqa: E402
from nfl_edge.engines.player.features_v3 import V3_EXTRA, add_v3_features  # noqa: E402
from nfl_edge.evaluation import eligibility as EL                      # noqa: E402

CUT = datetime(2026, 9, 20, 12, 0, tzinfo=timezone.utc)


# ------------------------------------------------------------------------------------------------ v3 inputs
def test_the_environment_comes_from_the_market_and_a_missing_one_refuses():
    up = pd.DataFrame({"player_id": ["a", "b"], "game_id": ["g1", "g2"], "team": ["KC", "BUF"], "home": [True, False],
                       "spread_line": [np.nan, np.nan], "total_line": [np.nan, np.nan]})
    out = PV3.attach_market_environment(up, {"g1": {"spread": -3.5, "total": 47.5, "source": "kalshi_implied"}})
    assert out.loc[0, "spread_line"] == -3.5 and out.loc[0, "total_line"] == 47.5 and bool(out.loc[0, "env_known"])
    assert not bool(out.loc[1, "env_known"]) and np.isnan(out.loc[1, "total_line"])
    assert list(PV3.usable_rows(out)) == [True, False]


def test_the_v2_defect_is_visible_in_design_and_v3_never_feeds_it_a_zero_total():
    """design() maps NaN to 0.0 -- which is how a blanked line became a zero-point team. v3 rows reach design()
    only with a known environment (usable_rows), so the NaN path is never taken for a v3 distribution."""
    spec = DD._spec("receiving_yards")
    row = pd.DataFrame([{**{c: 1.0 for c in DD.V3_DESIGN}, "ewma_receiving_yards": 50.0, "ewma_targets": 6.0,
                         "implied_total": np.nan}])
    X = DD.design(row, spec, "receiving_yards", "v2")
    assert X[0, 1 + DD.V2_DESIGN.index("implied_total")] == 0.0          # the defect, pinned so it cannot hide
    feat = PV3.attach_market_environment(pd.DataFrame({"player_id": ["a"], "game_id": ["g"], "team": ["KC"], "home": [True],
                                                       "spread_line": [np.nan], "total_line": [np.nan]}), {})
    assert not PV3.usable_rows(feat).any()


def test_current_season_history_is_bounded_to_completed_games():
    kick = {"w1": CUT - timedelta(days=7), "w2_thu": CUT - timedelta(hours=3), "w2_sun": CUT + timedelta(hours=5)}
    hist = pd.DataFrame({"season": [2025, 2026, 2026, 2026], "game_id": ["old", "w1", "w2_thu", "w2_sun"], "player_id": ["p"] * 4})
    kept, info = PV3.completed_current_season(hist, 2026, kick, CUT, exclude_games={"w2_sun"})
    assert set(kept.game_id) == {"old", "w1"}                 # Thursday kicked off 3h ago: not provably complete
    assert info["target_season_games_used"] == 1 and info["target_season_rows_dropped"] == 2


def test_a_played_game_with_listed_props_is_history_not_a_prospect():
    """Regression (first production run, 2026-09-23 12:22): every game with a quoted player market was treated as
    upcoming, so the played week-1/2 games -- whose props were still listed -- were excluded from history and the
    arm used 0 current-season games. Only games that have not kicked off are prospects."""
    kick = {"w1": CUT - timedelta(days=7), "w2": CUT - timedelta(days=1), "w3": CUT + timedelta(days=1)}
    pre = PV3.pregame_games(kick, CUT)
    assert pre == {"w3"}
    hist = pd.DataFrame({"season": [2026, 2026], "game_id": ["w1", "w2"], "player_id": ["p", "p"]})
    kept, info = PV3.completed_current_season(hist, 2026, kick, CUT, exclude_games=pre)
    assert set(kept.game_id) == {"w1", "w2"} and info["target_season_games_used"] == 2


def test_the_starting_quarterback_is_the_depth_chart_qb1():
    up = pd.DataFrame({"player_id": ["qbA", "qbB", "wr"], "team": ["KC", "KC", "KC"], "game_id": ["g"] * 3})
    out = PV3.depth_qb_starters(up, {"KC": "qbA"})
    assert list(out.qb_starter) == [True, False, False] and out.qb1_known.all()
    none = PV3.depth_qb_starters(up, {})
    assert not none.qb_starter.any() and not none.qb1_known.any()


def test_v3_recency_features_are_strictly_prior():
    rows = []
    for w, snaps in ((1, 0.30), (2, 0.90), (3, None)):
        rows.append({"player_id": "p", "season": 2026, "week": w, "team": "KC", "game_id": f"g{w}",
                     "snap_share": snaps, "target_share": (0.1 if snaps else None), "carry_share": 0.0,
                     "ewma_snap_share": 0.5, "ewma_target_share": 0.15, "ewma_carry_share": 0.0,
                     "ewma_team_pass_att": 35.0, "ewma_team_rush_att": 25.0,
                     "targets": (5.0 if snaps else None), "carries": (0.0 if snaps else None), "offense_snaps": (50.0 if snaps else None)})
    f = add_v3_features(pd.DataFrame(rows))
    assert all(c in f.columns for c in V3_EXTRA)
    last = f[f.week == 3].iloc[0]
    assert last.last_snap_share == 0.90 and last.last3_snap_share == pytest.approx(0.60) and last.n_cur_season == 2
    first = f[f.week == 1].iloc[0]
    assert first.last_snap_share == 0.5                     # no prior game: the EWMA, never a zero
    assert f[f.week == 2].iloc[0].last_snap_share == 0.30   # week 2 sees week 1 only, never itself
    assert last.proj_targets_struct == pytest.approx(35.0 * 0.15)


def test_v3_is_its_own_model_version():
    assert DD.VERSION == "data-player-dist-2.0.0"
    assert DD.VERSION_BY_FEATURE_SET["v3"] == "data-player-dist-3.0.0"
    assert DD.V3_DESIGN[:len(DD.V2_DESIGN)] == DD.V2_DESIGN


# ------------------------------------------------------------------------------------------------ abstention
def _decide(**kw):
    base = dict(arm="DATA_PLAYER_V3", engine_version="data-player-dist-3.0.0", stat="receiving_yards", identity_confidence="RESOLVED",
                availability_state="EXPECTED_ACTIVE", role_certainty="HIGH", game_env_known=True, qb_starter_known=True,
                ladder_identification="FULL", disagreement_pp=1.0)
    base.update(kw)
    return AB.decide(**base)


def test_an_unvalidated_data_statistic_is_never_production_eligible():
    d = _decide()
    assert d["state"] == AB.ABSTAIN_MODEL_UNVALIDATED and not d["production_eligible"]


def test_abstention_order_and_reasons(monkeypatch):
    monkeypatch.setattr(AB, "VALIDATED_STATS", frozenset({("data-player-dist-3.0.0", "receiving_yards")}))
    assert _decide()["state"] == AB.PROJECTION_VALID and _decide()["production_eligible"]
    assert _decide(identity_confidence="RESOLVED_UNCONFIRMED")["state"] == AB.ABSTAIN_IDENTITY
    assert _decide(availability_state="QUESTIONABLE")["state"] == AB.ABSTAIN_INJURY_UNCERTAIN
    assert _decide(availability_state=None)["state"] == AB.ABSTAIN_INJURY_UNCERTAIN            # unknown is not healthy
    assert _decide(role_certainty="LOW")["state"] == AB.ABSTAIN_ROLE_UNCERTAIN
    assert _decide(game_env_known=False)["state"] == AB.ABSTAIN_VOLUME_UNCERTAIN
    assert _decide(stat="passing_yards", qb_starter_known=False)["state"] == AB.ABSTAIN_VOLUME_UNCERTAIN
    big = _decide(disagreement_pp=-12.0)
    assert big["state"] == AB.PROJECTION_LOW_CONFIDENCE and big["large_disagreement"] and not big["production_eligible"]
    assert _decide(disagreement_pp=4.9)["state"] == AB.PROJECTION_VALID


def test_the_market_arm_is_judged_on_what_it_depends_on():
    d = _decide(arm="MARKET_PLAYER_DIST", engine_version="market-player-dist-1.0.0", role_certainty="UNKNOWN", market_arm=True,
                disagreement_pp=0.2)
    assert d["state"] == AB.PROJECTION_VALID                                   # role data is not an input of the ladder
    assert _decide(arm="MARKET_PLAYER_DIST", market_arm=True, ladder_identification="UNDERIDENTIFIED")["state"] == AB.ABSTAIN_MARKET_INCOMPLETE


# ------------------------------------------------------------------------------------------------ eligibility
def _rows(arm, fam, games, rows_per_game, model_err, market_err, week=2):
    out = []
    rng = np.random.default_rng(0)
    for g in range(games):
        for i in range(rows_per_game):
            y = float(rng.random() < 0.5)
            out.append({"evidence_class": "PROSPECTIVE_FROZEN", "model_arm": arm, "family_group": fam, "game_id": f"g{week}_{g}",
                        "week": week, "settled_yes": y, "contract_value": abs(y - model_err), "h_mid": abs(y - market_err),
                        "synchronization_state": "SYNCHRONIZED", "close_quality": "EXCELLENT", "clv_mid_toward_model": 0.001,
                        "exec_pnl_net": -0.01})
    return out


def test_many_rows_from_few_games_are_few_observations():
    acc = EL.Accumulator()
    for r in _rows("BOARD_V2", "spread", games=3, rows_per_game=400, model_err=0.3, market_err=0.4):
        acc.add(r)
    doc = EL.build(acc, as_of="t", sources=["x"])
    fam = doc["families"]["BOARD_V2|spread"]
    assert fam["n_rows"] == 1200 and fam["n_games"] == 3
    assert fam["status"] == EL.RESEARCH_ONLY and "3 independent games" in fam["reasons"][0]


def test_state_transitions_follow_the_written_policy():
    acc = EL.Accumulator()
    # 16 games, one week, slightly better than the market -> WATCH, never LIMITED on one week
    for r in _rows("BOARD_V2", "total", games=16, rows_per_game=20, model_err=0.35, market_err=0.36):
        acc.add(r)
    doc = EL.build(acc, as_of="t", sources=["x"])
    assert doc["families"]["BOARD_V2|total"]["status"] == EL.WATCH
    # measurably worse than the market -> RESEARCH_ONLY
    acc2 = EL.Accumulator()
    for r in _rows("BOARD_V2", "period_x", games=20, rows_per_game=20, model_err=0.45, market_err=0.30):
        acc2.add(r)
    d2 = EL.build(acc2, as_of="t", sources=["x"])["families"]["BOARD_V2|period_x"]
    assert d2["status"] == EL.RESEARCH_ONLY and "worse than the market" in d2["reasons"][0]
    # 3 weeks x 16 games, calibrated-ish and not worse -> LIMITED is reachable
    acc3 = EL.Accumulator()
    for wk in (2, 3, 4):
        for r in _rows("BOARD_V2", "spread", games=16, rows_per_game=10, model_err=0.30, market_err=0.31, week=wk):
            acc3.add(r)
    d3 = EL.metrics(acc3)[("BOARD_V2", "spread")]
    assert d3["n_games"] == 48 and d3["n_weeks"] == 3
    st, _ = EL.decide(dict(d3, ece=0.01))
    assert st in (EL.LIMITED, EL.TRUSTED) and st != EL.TRUSTED              # 3 weeks can never be TRUSTED


def test_known_defects_are_disabled_whatever_the_numbers():
    acc = EL.Accumulator()
    for r in _rows("DATA_PLAYER_DIST", "player_receptions", games=40, rows_per_game=5, model_err=0.1, market_err=0.4):
        acc.add(r)
    doc = EL.build(acc, as_of="t", sources=["x"])
    assert doc["arms"]["DATA_PLAYER_DIST"] == EL.DISABLED
    assert EL.status_for(doc, "DATA_PLAYER_DIST", "player_receptions")["status"] == EL.DISABLED


def test_unmeasured_is_research_only_and_the_accumulator_round_trips():
    assert EL.status_for(None, "BOARD_V2")["status"] == EL.RESEARCH_ONLY
    assert EL.status_for(None, "HYBRID_PLAYER_DIST")["status"] == EL.DISABLED
    acc = EL.Accumulator()
    for r in _rows("MARKET_PLAYER_DIST", "player_receptions", games=4, rows_per_game=3, model_err=0.3, market_err=0.3):
        acc.add(r)
    back = EL.Accumulator.from_json(acc.to_json())
    assert EL.metrics(back) == EL.metrics(acc)
    # rows that are not prospective, or not settled, never count
    acc.add({"evidence_class": "HISTORICAL_RESEARCH", "model_arm": "X", "family_group": "f", "game_id": "g", "settled_yes": 1.0,
             "contract_value": 0.9, "h_mid": 0.5})
    acc.add({"evidence_class": "PROSPECTIVE_FROZEN", "model_arm": "X", "family_group": "f", "game_id": "g", "settled_yes": None,
             "contract_value": 0.9, "h_mid": 0.5})
    assert ("X", "f") not in EL.metrics(acc)
