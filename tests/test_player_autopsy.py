"""The player-projection autopsy: deterministic classification on synthetic known cases, honest about missing usage."""
import json
import math
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
from nfl_edge.settlement.results import result_book_from_records                              # noqa: E402
from nfl_edge.shadow import player_autopsy as PA                                              # noqa: E402

HEADER = open(os.path.join(ROOT, "tests", "fixtures", "postgame", "dal_phi_2025_w1.results.json")).read()
GAME = "2026_02_A_H"


def schedule_csv():
    fix = json.loads(HEADER)
    lines = fix["schedule_csv"].splitlines()
    h = lines[0].split(",")
    row = {k: "" for k in h}
    row.update({"game_id": GAME, "season": "2026", "game_type": "REG", "week": "2", "gameday": "2026-09-13", "gametime": "13:00",
                "away_team": "A", "home_team": "H", "away_score": "20", "home_score": "27", "result": "7", "total": "47", "overtime": "0"})
    return "\n".join([lines[0], ",".join(row[k] for k in h)])


def book(players, snaps, complete=True):
    rec = {"schedule_csv": schedule_csv(), "players": players, "snaps": snaps, "game_id": GAME,
           "games_with_player_stats": [GAME] if complete else [], "games_with_snaps": [GAME] if complete else []}
    return result_book_from_records(rec, min_hours_after_kickoff=0)


def ledger_row(pid, stat, *, mu, muo, eff, q, threshold, name="P", run="r1", mtk=30.0, cv=0.55, mid=0.5, p_plays=0.97, team="H",
               family="scale_emp_binned", decomposition="opportunity_x_efficiency", pred="x"):
    return {"prediction_id": f"{pred}|{pid}|{stat}|{threshold}|{run}", "run_id": run, "observed_at": "2026-09-13T16:00:00+00:00",
            "minutes_to_kickoff": mtk, "game_id": GAME, "season": 2026, "week": 2, "team": team, "player_id": pid, "player_name": name,
            "stat": stat, "stat_spec": stat, "ticker": f"T-{pid}-{stat}-{threshold}", "threshold": threshold, "model_version": "v",
            "model_artifact_sha": "s", "feature_cutoff": "c", "distribution_family": family, "model_quantiles": q,
            "projected_stat_mean": mu, "projected_opportunity_mean": muo, "projected_efficiency": eff, "efficiency_feature": "ypc",
            "efficiency_decomposition": decomposition, "model_event_probability": cv, "model_contract_value": cv, "mid": mid,
            "yes_ask": mid + 0.01, "availability_state": "EXPECTED_ACTIVE", "p_plays": p_plays}


Q_RUSH = {"p05": 25.0, "p25": 50.0, "p50": 68.0, "p75": 88.0, "p95": 125.0}


def player(pid, carries, rush_yds, team="H", name="P"):
    return {"player_id": pid, "player_name": name, "position": "RB", "team": team, "has_stats_row": True,
            "stats": {"carries": float(carries), "rushing_yards": float(rush_yds), "attempts": 0.0, "targets": 0.0, "receptions": 0.0}}


def snap(pid, n, team="H"):
    return {"player_id": pid, "game_id": GAME, "team": team, "offense_snaps": float(n), "defense_snaps": 0.0, "st_snaps": 0.0}


def test_an_opportunity_miss_is_classified_as_such():
    """Projected 17 carries, actual 8, yards per carry roughly as projected: the workload model missed."""
    b = book([player("p1", 8, 34)], [snap("p1", 30)])
    row = ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70)
    r = PA.diagnose(row, b)
    assert r["classification"] == PA.OPPORTUNITY_MISS
    assert r["actual_opportunity"] == 8 and r["projected_efficiency"] == 4.0 and r["actual_efficiency"] == 4.25
    # 34 yards sits inside the model's own range (z about -1.2): the mechanism is still diagnosable, the miss is not "large"
    assert r["large_miss"] is False and r["realised_payout"] == 0.0


def test_an_efficiency_miss_is_classified_as_such():
    """Projected 17 carries, actual 18, yards per carry collapsed: the workload was right."""
    b = book([player("p1", 18, 30)], [snap("p1", 40)])
    row = ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70)
    r = PA.diagnose(row, b)
    assert r["classification"] == PA.EFFICIENCY_MISS and "efficiency off" in r["tags"] and "opportunity off" not in r["tags"]


def test_a_team_volume_collapse_reclassifies_an_opportunity_miss():
    """The whole team ran 8 times against a prior mean of 26: the miss is the game script, not the player's share."""
    prior_rows = []
    fix = json.loads(HEADER)
    lines = fix["schedule_csv"].splitlines(); h = lines[0].split(",")
    def game_row(gid, week):
        row = {k: "" for k in h}
        row.update({"game_id": gid, "season": "2026", "game_type": "REG", "week": str(week), "gameday": "2026-09-06", "gametime": "13:00",
                    "away_team": "A", "home_team": "H", "away_score": "20", "home_score": "27", "result": "7", "total": "47", "overtime": "0"})
        return ",".join(row[k] for k in h)
    csv = "\n".join([lines[0], game_row("2026_01_A_H", 1), game_row(GAME, 2)])
    rec = {"schedule_csv": csv, "game_id": GAME, "games_with_player_stats": ["2026_01_A_H", GAME], "games_with_snaps": ["2026_01_A_H", GAME],
           "players": [dict(player("p1", 8, 34), game_id=GAME), dict(player("p9", 0, 0), game_id=GAME),
                       dict(player("p1", 20, 90), game_id="2026_01_A_H"), dict(player("p9", 6, 20), game_id="2026_01_A_H")],
           "snaps": [snap("p1", 30)]}
    b = result_book_from_records(rec, min_hours_after_kickoff=0)
    row = ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70)
    r = PA.diagnose(row, b)
    assert r["classification"] == PA.TEAM_VOLUME_MISS and r["team_volume"]["actual"] == 8 and r["team_volume"]["prior_mean"] == 26


def test_availability_miss_when_an_expected_starter_never_played():
    b = book([], [snap("p1", 0)])
    r = PA.diagnose(ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70), b)
    assert r["classification"] == PA.AVAILABILITY_MISS and r["played"] is False
    b2 = book([], [])
    r2 = PA.diagnose(ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70), b2)
    assert r2["classification"] == PA.AVAILABILITY_MISS and r2["usage_missing"] is True


def test_missing_usage_is_explicit_never_a_zero():
    b = book([], [], complete=False)
    r = PA.diagnose(ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70), b)
    assert r["classification"] == PA.INSUFFICIENT_DATA and r["usage_missing"] and r["actual_stat"] is None


def test_a_row_without_intermediates_is_insufficient_data():
    b = book([player("p1", 18, 30)], [snap("p1", 40)])
    row = ledger_row("p1", "rushing_yards", mu=None, muo=None, eff=None, q=None, threshold=70)
    assert PA.diagnose(row, b)["classification"] == PA.INSUFFICIENT_DATA


def test_usage_joins_on_the_gsis_id_not_the_name():
    b = book([player("p1", 8, 34, name="Same Name"), player("p2", 18, 30, name="Same Name")], [snap("p1", 30), snap("p2", 40)])
    r1 = PA.diagnose(ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70, name="Same Name"), b)
    r2 = PA.diagnose(ledger_row("p2", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70, name="Same Name"), b)
    assert r1["actual_opportunity"] == 8 and r2["actual_opportunity"] == 18
    assert r1["classification"] == PA.OPPORTUNITY_MISS and r2["classification"] == PA.EFFICIENCY_MISS


def test_a_result_inside_the_model_range_is_not_a_miss_and_the_market_verdict_is_recorded():
    b = book([player("p1", 16, 70)], [snap("p1", 40)])
    r = PA.diagnose(ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70, cv=0.55, mid=0.50), b)
    assert r["classification"] == PA.NO_LARGE_MISS and r["market_verdict"] == "SIMILAR" and abs(r["robust_z"]) < PA.Z_LARGE
    assert r["large_miss"] is False


def test_ranking_is_deterministic_and_by_standardised_surprise():
    b = book([player("p1", 8, 34), player("p2", 18, 30), player("p3", 16, 70)], [snap("p1", 30), snap("p2", 40), snap("p3", 40)])
    rows = [ledger_row(p, "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70) for p in ("p3", "p1", "p2")]
    rows += [ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=50)]        # another rung, same projection
    a = PA.autopsy_game(rows, b); b2 = PA.autopsy_game(list(reversed(rows)), b)
    assert [r["player_id"] for r in a] == [r["player_id"] for r in b2]
    assert len(a) == 3, "one diagnosis per (player, stat), the rung nearest the model median"
    zs = [abs(r["robust_z"]) for r in a]
    assert zs == sorted(zs, reverse=True)
    assert a[0]["threshold"] == 70                                  # 68 is the median; 70 is the nearest rung


# ---------------------------------------------------------------------------------------------------------------
# NEGATIVE AND ZERO EFFICIENCY
#
# Real NFL outcomes go backwards. A sack, a tackle for loss, a lateral: the yardage is negative, so actual
# efficiency is negative, so `actual / projected` is not positive and has NO real logarithm. The incumbent
# autopsy called `math.log` on it unconditionally and the scheduled postgame workflow died mid-run:
#
#     File "nfl_edge/shadow/player_autopsy.py", line 264, in diagnose
#       eff_lr = math.log((out["actual_efficiency"] + 1e-6) / (out["projected_efficiency"] + 1e-6))
#     ValueError: math domain error
#
# Shadow v2 met this first and settled the semantics (nfl_edge/engines/player/autopsy_v2.py): the component is a
# miss of unbounded size, the ratio stays None, and no tiny positive number is substituted to keep the logarithm
# running. These pin the same treatment here, and pin that nothing about the ordinary positive case moved -- the
# autopsy corpus is write-once, so a changed diagnosis of an already-published row is a hard conflict.
# ---------------------------------------------------------------------------------------------------------------
def receiver(pid, targets, rec_yds, receptions=None, team="H", name="R"):
    return {"player_id": pid, "player_name": name, "position": "WR", "team": team, "has_stats_row": True,
            "stats": {"carries": 0.0, "rushing_yards": 0.0, "attempts": 0.0, "targets": float(targets),
                      "receptions": float(targets if receptions is None else receptions),
                      "receiving_yards": float(rec_yds)}}


Q_REC = {"p05": 10.0, "p25": 30.0, "p50": 45.0, "p75": 62.0, "p95": 95.0}


def test_negative_rushing_yards_are_diagnosed_instead_of_raising():
    """Five carries for minus six yards against a projection of 4.0 per carry."""
    b = book([player("p1", 5, -6)], [snap("p1", 30)])
    r = PA.diagnose(ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70), b)
    assert r["actual_efficiency"] == -1.2 and r["projected_efficiency"] == 4.0
    assert r["efficiency_log_ratio"] is None, "no real logarithm exists; none may be invented"
    assert r["classification"] == PA.EFFICIENCY_MISS
    assert "efficiency off" in r["tags"] and "efficiency ratio undefined" in r["tags"]
    assert any("not positive" in e and "no real log ratio" in e for e in r["evidence"]), \
        "the evidence must say WHY the ratio is absent, not leave a silent null"


def test_negative_receiving_yards_are_diagnosed_instead_of_raising():
    b = book([receiver("p2", 4, -3)], [snap("p2", 35)])
    row = ledger_row("p2", "receiving_yards", mu=45.0, muo=6.0, eff=7.5, q=Q_REC, threshold=45, name="R")
    r = PA.diagnose(row, b)
    assert r["actual_efficiency"] == -0.75 and r["efficiency_log_ratio"] is None
    assert r["classification"] == PA.EFFICIENCY_MISS and "efficiency ratio undefined" in r["tags"]


def test_an_undefined_efficiency_ratio_outranks_a_finite_opportunity_miss():
    """Its magnitude is unbounded, so it cannot lose a comparison of magnitudes to a finite one."""
    b = book([player("p1", 8, -10)], [snap("p1", 30)])          # workload also missed: 8 carries against 17
    r = PA.diagnose(ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70), b)
    assert r["opportunity_log_ratio"] is not None and abs(r["opportunity_log_ratio"]) > PA.LOG_RATIO_LARGE
    assert "opportunity off" in r["tags"]
    assert r["classification"] == PA.EFFICIENCY_MISS and r["efficiency_log_ratio"] is None


def test_zero_efficiency_keeps_a_real_finite_log_ratio():
    """Zero is not the broken case: with the epsilon the ratio is still positive, so the logarithm is real."""
    b = book([player("p1", 16, 0)], [snap("p1", 40)])
    r = PA.diagnose(ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70), b)
    assert r["actual_efficiency"] == 0.0
    assert r["efficiency_log_ratio"] is not None and r["efficiency_log_ratio"] < -PA.LOG_RATIO_LARGE
    assert r["classification"] == PA.EFFICIENCY_MISS
    assert "efficiency ratio undefined" not in r["tags"], "a real logarithm exists here; nothing is undefined"


def test_an_ordinary_positive_efficiency_miss_is_untouched():
    b = book([player("p1", 18, 30)], [snap("p1", 40)])
    r = PA.diagnose(ledger_row("p1", "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70), b)
    assert r["actual_efficiency"] == pytest.approx(30 / 18)
    assert r["efficiency_log_ratio"] == pytest.approx(math.log((30 / 18 + 1e-6) / (4.0 + 1e-6)))
    assert r["classification"] == PA.EFFICIENCY_MISS
    assert "efficiency ratio undefined" not in r["tags"]
    assert any("opportunity within range" in e for e in r["evidence"]), "the existing evidence wording is unchanged"


def test_the_positive_fixtures_classify_exactly_as_they_did():
    """The autopsy corpus is write-once: a re-diagnosis that moved would conflict with what is published."""
    b = book([player("p1", 8, 34), player("p2", 18, 30), player("p3", 16, 70)],
             [snap("p1", 30), snap("p2", 40), snap("p3", 40)])
    got = {p: PA.diagnose(ledger_row(p, "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70), b)
           for p in ("p1", "p2", "p3")}
    assert got["p1"]["classification"] == PA.OPPORTUNITY_MISS
    assert got["p2"]["classification"] == PA.EFFICIENCY_MISS
    assert got["p3"]["classification"] == PA.NO_LARGE_MISS
    for r in got.values():
        assert "efficiency ratio undefined" not in r["tags"]
        assert r["efficiency_log_ratio"] is not None


def test_a_whole_game_autopsy_survives_a_player_with_negative_yardage():
    """The failure took the entire settlement step with it, not just the one row that caused it."""
    b = book([player("p1", 5, -6), player("p2", 18, 30), player("p3", 16, 70)],
             [snap("p1", 30), snap("p2", 40), snap("p3", 40)])
    rows = [ledger_row(p, "rushing_yards", mu=68.0, muo=17.0, eff=4.0, q=Q_RUSH, threshold=70) for p in ("p1", "p2", "p3")]
    out = PA.autopsy_game(rows, b)
    assert len(out) == 3
    assert {r["player_id"] for r in out} == {"p1", "p2", "p3"}
