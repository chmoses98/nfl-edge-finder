"""Regression tests for the Week 3 player-autopsy gap (2026-10-01).

Root causes reproduced here:

  1. The three-arm report was rebuilt only after a run that WROTE evidence, from a FRESH full checkout of
     market-data (/tmp/md3) on top of /tmp/md, /tmp/md2 and the publisher's own checkout. Three runs in a row the
     runner died creating it; the evidence (1,012 Week 3 autopsies) was published and the report never caught
     up. The gate now reports a stale report as work, and the workflow refreshes ONE checkout in place.
  2. The autopsy picked its "latest pregame" row by quote time, then prediction id. The pricer re-prices a
     game's last pregame quote for days after kickoff, with availability read at run time, so the pick could be
     a postgame computation (86 of 3,021 records). The pick now requires the computation itself to precede kickoff.
  3. A unit diagnosed twice (a later representative row) was counted twice by the report (26 units).
"""
import os
import re
import sys

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "shadow"))

from nfl_edge.shadow import player_autopsy as PA  # noqa: E402

KO = "2026-09-22T00:15:00+00:00"


def anat(run_id, pid="P1", stat="receiving_yards", mtk=87.5, thr=70, pred=None, p_plays=0.78, evaluated_at=None, obs="2026-09-21T22:47:28+00:00"):
    return {"prediction_id": pred or f"{run_id}-{pid}-{stat}-{thr}", "run_id": run_id, "game_id": "2026_02_NYG_LA",
            "season": 2026, "week": 2, "team": "NYG", "player_id": pid, "stat": stat, "threshold": thr, "ticker": f"T-{thr}",
            "minutes_to_kickoff": mtk, "observed_at": obs, "kickoff_utc": KO, "evaluated_at": evaluated_at,
            "projected_stat_mean": 74.0, "projected_opportunity_mean": 7.0, "efficiency_decomposition": "opportunity_x_efficiency",
            "model_quantiles": {"p05": 20, "p25": 50, "p50": 70, "p75": 95, "p95": 140}, "p_plays": p_plays,
            "anatomy_status": "OK"}


# ---------------------------------------------------------------- 2. pregame computation, not just pregame quote
def test_rows_computed_after_kickoff_never_represent_a_unit():
    rows = [anat("20260921T232253Z", pred="zzz-pre", p_plays=0.78),
            # the same stale pregame quote re-priced the morning after the game, availability now OUT
            anat("20260922T051130Z", pred="aaa-post", p_plays=0.005),
            anat("20260924T133700Z", pred="bbb-post", p_plays=0.78)]
    rep = PA.representative_rows(rows)
    assert [r["prediction_id"] for r in rep] == ["zzz-pre"], (
        "1.0.0 broke this tie by prediction id and picked the postgame computation 'aaa-post'")


def test_the_latest_pregame_computation_wins_a_quote_tie():
    rows = [anat("20260921T193247Z", pred="aaa"), anat("20260921T232253Z", pred="zzz")]
    assert PA.representative_rows(rows)[0]["run_id"] == "20260921T232253Z"


def test_evaluated_at_after_kickoff_disqualifies_a_row_even_with_a_pregame_run_id():
    rows = [anat("20260921T232253Z", evaluated_at="2026-09-22T03:00:00+00:00")]
    assert PA.representative_rows(rows) == []
    assert PA.excluded_rows(rows) == {"computed at or after kickoff (re-priced stale pregame quote)": 1}


def test_unparseable_generation_time_is_not_trusted():
    r = anat("not-a-stamp")
    assert PA.generated_at(r) is None and PA.representative_rows([r]) == []
    assert PA.excluded_rows([r]) == {"generation time unknown": 1}


# ---------------------------------------------------------------- 3. one diagnosis per unit
def rec(pred, run_id, version="autopsy-1.1.0", cls="NO_LARGE_MISS", pid="P1", stat="receiving_yards", gid="2026_02_NYG_LA",
        generated=None, evaluated_at="2026-09-29T04:41:48+00:00"):
    r = {"prediction_id": pred, "evaluation_version": version, "run_id": run_id, "game_id": gid, "week": 2, "player_id": pid,
         "stat": stat, "minutes_to_kickoff": 87.5, "observed_at": "2026-09-21T22:47:28+00:00", "classification": cls,
         "robust_z": 0.1, "evaluated_at": evaluated_at}
    if generated:
        r["generated_at"] = generated
    return r


def test_canonical_takes_one_record_per_unit_and_ignores_the_postgame_autopsy_time():
    recs = [rec("a", "20260921T232253Z", version="autopsy-1.0.0", cls="AVAILABILITY_MISS"),
            rec("b", "20260924T133700Z", version="autopsy-1.0.0", cls="INSUFFICIENT_DATA")]   # postgame computation
    out = PA.canonical_autopsies(recs)
    assert [r["prediction_id"] for r in out] == ["a"], (
        "a record's own evaluated_at is the postgame diagnosis time; reading it as the projection time drops everything")


def test_newest_rule_version_wins_for_the_whole_game():
    recs = [rec("a", "20260921T232253Z", version="autopsy-1.0.0", pid="P1"),
            rec("b", "20260921T232253Z", version="autopsy-1.0.0", pid="P2"),
            rec("c", "20260921T232253Z", version="autopsy-1.1.0", pid="P1", generated="2026-09-21T23:22:53+00:00")]
    out = PA.canonical_autopsies(recs)
    assert [r["prediction_id"] for r in out] == ["c"], "never a mix of rule versions inside one game"


def test_duplicate_units_count_once():
    recs = [rec("a", "20260921T193247Z"), rec("b", "20260921T232253Z"), rec("c", "20260921T232253Z", pid="P2")]
    out = PA.canonical_autopsies(recs)
    assert sorted(r["prediction_id"] for r in out) == ["b", "c"]


# ---------------------------------------------------------------- coverage manifest
def week3_schedule():
    games = ["ATL_GB", "ARI_SF", "BAL_DAL", "CAR_CLE", "CIN_PIT", "HOU_IND", "KC_MIA", "LAC_BUF", "LA_DEN", "LV_NO",
             "MIN_TB", "NE_JAX", "NYJ_DET", "PHI_CHI", "SEA_WAS", "TEN_NYG"]
    return [{"game_id": f"2026_03_{g}", "status": "FINAL"} for g in games]


def test_a_week_with_only_one_diagnosed_game_cannot_look_complete():
    sched = week3_schedule()
    canonical = [rec(f"x{i}", "20260924T232253Z", gid="2026_03_ATL_GB", pid=f"P{i}") for i in range(69)]
    m = PA.coverage_manifest(sched, None, canonical)
    assert m["expected_games"] == 16 and m["diagnosed_games"] == 1 and m["excluded_games"] == 15
    assert {g["exclusion_reason"] for g in m["games"] if not g["included"]} == {PA.EXCLUDE_NOT_DIAGNOSED}
    assert "excluded 15" in PA.render_coverage(m)


def test_exclusion_reasons_are_named_never_silent():
    sched = [{"game_id": "G_FINAL_NO_ANAT", "status": "FINAL"}, {"game_id": "G_SCHEDULED", "status": "SCHEDULED"},
             {"game_id": "G_POSTGAME_ONLY", "status": "FINAL"}, {"game_id": "G_OK", "status": "FINAL"}]
    anatomy = {"G_POSTGAME_ONLY": {"anatomy_rows": 40, "eligible_units": 0, "eligible_unit_ids": [], "excluded_rows": {"x": 40}},
               "G_OK": {"anatomy_rows": 10, "eligible_units": 1, "eligible_unit_ids": ["P1|receiving_yards"], "excluded_rows": {}}}
    canonical = [rec("a", "20260921T232253Z", gid="G_OK")]
    m = PA.coverage_manifest(sched, anatomy, canonical)
    why = {g["game_id"]: g["exclusion_reason"] for g in m["games"]}
    assert why == {"G_FINAL_NO_ANAT": PA.EXCLUDE_NO_ANATOMY, "G_SCHEDULED": PA.EXCLUDE_NOT_FINAL,
                   "G_POSTGAME_ONLY": PA.EXCLUDE_NO_ELIGIBLE, "G_OK": None}
    assert m["eligible_not_diagnosed"] == 0 and m["diagnosed_games"] == 1


# ---------------------------------------------------------------- 1. the gate and the workflow
def _touch(path, text="x"):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        f.write(text)


def test_a_report_older_than_its_evidence_is_work(tmp_path):
    import settle_gate as SG
    md = str(tmp_path)
    sh = os.path.join(md, "data", "shadow")
    _touch(os.path.join(sh, "arm_reports", "20260928T043505Z", "cumulative.REPORT.md"))
    _touch(os.path.join(sh, "player_autopsy", "2026_03_ATL_GB", "autopsy-1.0.0.20260925T121348Z.autopsy.jsonl.gz"))
    assert SG.report_staleness(md)["stale"] is False
    _touch(os.path.join(sh, "player_autopsy", "2026_03_KC_MIA", "autopsy-1.0.0.20260928T112411Z.autopsy.jsonl.gz"))
    st = SG.report_staleness(md)
    assert st == {"stale": True, "newest_evidence_batch": "20260928T112411Z", "newest_report_batch": "20260928T043505Z"}
    # a half-written report directory (no cumulative report) does not count as a rebuild
    os.makedirs(os.path.join(sh, "arm_reports", "20260928T112411Z"))
    assert SG.report_staleness(md)["stale"] is True
    _touch(os.path.join(sh, "arm_reports", "20260928T112411Z", "cumulative.REPORT.md"))
    assert SG.report_staleness(md)["stale"] is False


def _wf():
    with open(os.path.join(ROOT, ".github", "workflows", "postgame-settle.yml")) as f:
        return f.read()


def test_the_postgame_job_holds_one_market_data_checkout_not_four():
    text = _wf()
    assert len(re.findall(r"git worktree add", text)) == 1, (
        "every extra `git worktree add` is another full multi-GB copy of market-data; the fourth killed the runner")
    assert "/tmp/md2" not in text and "/tmp/md3" not in text
    script = open(os.path.join(ROOT, "scripts", "ci", "refresh_market_data_worktree.sh")).read()
    code = "\n".join(l for l in script.splitlines() if not l.lstrip().startswith("#"))
    assert "worktree add" not in code and "checkout -q -f --detach origin/market-data" in code


def test_the_report_rebuild_runs_when_the_gate_finds_it_stale():
    steps = yaml.safe_load(_wf())["jobs"]["settle"]["steps"]
    by = {s.get("name"): s for s in steps}
    rebuild = by["Rebuild the three-arm per-slate, weekly and cumulative reports"]
    assert "steps.gate.outputs.report_work == 'true'" in rebuild["if"]
    assert "steps.gate.outputs.report_batch" in rebuild["run"], "a repair run with no new batch still needs a report id"
    publish = by["Publish the three-arm reports"]
    assert "steps.arm_report.outcome == 'success'" in publish["if"]
    install = by["Install the dependencies the settlement scripts import"]
    assert "report_work" in install["if"], "arm_report imports numpy; a report-only run must install it"
