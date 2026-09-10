"""The player-projection autopsy: deterministic classification on synthetic known cases, honest about missing usage."""
import json
import os

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
