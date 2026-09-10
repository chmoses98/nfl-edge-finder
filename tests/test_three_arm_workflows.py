"""The three-arm automation, asserted against the YAML: cheap gate, publish only after validation, isolation kept."""
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def wf(name):
    with open(os.path.join(ROOT, ".github", "workflows", name)) as f:
        return yaml.safe_load(f)


def steps(doc, job):
    return doc["jobs"][job]["steps"]


def idx(ss, pattern):
    for i, s in enumerate(ss):
        if re.search(pattern, (s.get("run") or "") + " " + str(s.get("uses") or "")):
            return i
    return None


def test_the_horizon_conductor_is_cheap_and_wakes_often():
    d = wf("three-arm-horizons.yml")
    on = d.get(True, d.get("on"))
    assert on["schedule"] == [{"cron": "*/15 * * * *"}]
    gate = steps(d, "gate")
    assert not any("pip install" in (s.get("run") or "") for s in gate), "the gate must not install dependencies"
    assert any("--filter=blob:none" in (s.get("run") or "") for s in gate), "the marker listing must be a blobless fetch"
    assert any("three_arm_horizon_gate.py" in (s.get("run") or "") for s in gate)
    assert d["jobs"]["snapshot"]["needs"] == "gate" and "should_run == 'true'" in d["jobs"]["snapshot"]["if"]
    assert "secrets." not in yaml.safe_dump(d), "the conductor must request no secret"


def test_the_horizon_snapshot_validates_before_it_publishes_and_publishes_only_the_arms():
    ss = steps(wf("three-arm-horizons.yml"), "snapshot")
    build, validate, publish = idx(ss, "three_arm_snapshot.py"), idx(ss, "validate_arms.py"), idx(ss, "publish_market_data.py")
    assert build < validate < publish
    assert "--horizon-ids" in ss[build]["run"] and "--ledger-dir" not in ss[build]["run"], "no ledger exists at a horizon: replay is unverified by design"
    assert "--src data/shadow/arms" in ss[publish]["run"]
    assert not any(p in ss[publish]["run"] for p in ("data/shadow/ledger", "data/kalshi", "data/shadow/evaluations"))
    assert idx(ss, "git config user.name") < publish
    assert ss[-1].get("if") == "always()" and "exit 1" in ss[-1]["run"]


def test_the_shadow_cycle_snapshots_after_pricing_and_cannot_fail_the_ledger():
    ss = steps(wf("shadow-price.yml"), "price")
    price, arms, validate = idx(ss, "price_slate.py"), idx(ss, "three_arm_snapshot.py"), idx(ss, "validate_arms.py")
    ledger_pub, arms_pub = idx(ss, r"publish_market_data.py --src data/shadow/ledger"), idx(ss, r"publish_market_data.py --src data/shadow/arms")
    assert price < arms < validate < ledger_pub < arms_pub
    for i in (arms, validate, arms_pub):
        assert ss[i].get("continue-on-error") is True, ss[i].get("name")
    assert "--ledger-dir data/shadow/ledger" in ss[arms]["run"], "the snapshot verifies its replay against the ledger just written"
    assert "arms_validate.outcome == 'success'" in ss[arms_pub]["if"]
    anatomy, anatomy_pub = idx(ss, "player_anatomy.py"), idx(ss, r"publish_market_data.py --src data/shadow/player_anatomy")
    assert price < anatomy < ledger_pub < anatomy_pub and ss[anatomy].get("continue-on-error") is True
    assert "--ledger-dir data/shadow/ledger" in ss[anatomy]["run"], "anatomy must reconcile against the ledger just written"
    assert "anatomy.outputs.status == 'WROTE'" in ss[anatomy_pub]["if"]


def test_the_report_workflows_still_publish_nothing_to_market_data():
    for name in ("run-nfl.yml", "run-nfl-horizons.yml"):
        src = open(os.path.join(ROOT, ".github", "workflows", name)).read()
        assert "three_arm_snapshot" not in src and "publish_market_data" not in src


def test_the_postgame_job_evaluates_arms_and_autopsies_behind_the_gate_and_validates_before_publishing():
    ss = steps(wf("postgame-settle.yml"), "settle")
    arms, autopsy, validate = idx(ss, "settle_arms.py"), idx(ss, "player_autopsy.py"), idx(ss, "validate_arms.py")
    pub_arms, pub_auto = idx(ss, r"--src data/shadow/arm_evaluations"), idx(ss, r"--src data/shadow/player_autopsy")
    report, pub_rep = idx(ss, "arm_report.py"), idx(ss, r"--src data/shadow/arm_reports")
    assert arms < autopsy < validate < pub_arms < pub_auto < report < pub_rep
    assert "arms_work" in ss[arms]["if"] and "autopsy_work" in ss[autopsy]["if"]
    assert ss[report].get("continue-on-error") is True and ss[validate].get("continue-on-error") is not True
    stats = idx(ss, "stats_player")
    assert "autopsy_work" in ss[stats]["if"], "the autopsy needs the player statistics download"
    assert "arms.outputs.status" in ss[-1]["run"] and "CONFLICT" in ss[-1]["run"]


def test_the_settle_gate_emits_the_outputs_the_workflow_reads():
    src = open(os.path.join(ROOT, "scripts", "shadow", "settle_gate.py")).read()
    assert "arms_work=" in src and "autopsy_work=" in src
