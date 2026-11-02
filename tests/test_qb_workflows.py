"""PR #232: workflow-level properties of the confirmed-starter quarterback plumbing (structure only; nothing is executed)."""
import os
import re

import yaml

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WF = os.path.join(ROOT, ".github", "workflows")


def load(name):
    text = open(os.path.join(WF, name)).read()
    return text, yaml.safe_load(text)


def steps(doc, job):
    return doc["jobs"][job]["steps"]


def test_the_intake_workflow_is_owner_only_and_never_interpolates_an_input_into_a_shell():
    text, doc = load("nfl-qb-confirm.yml")
    job = doc["jobs"]["record"]
    assert job["if"] == "github.actor == github.repository_owner"
    for st in job["steps"]:
        run = st.get("run", "")
        assert "${{ inputs." not in run and "${{ github.event.inputs" not in run, f"input interpolated into a shell: {st.get('name')}"
    # every input reaches the script through env
    appender = next(s for s in job["steps"] if "qb_confirm_append.py" in s.get("run", ""))
    for key in ("GAME_ID", "TEAM", "QB_ID", "STATUS", "SOURCE_TYPE", "SOURCE_REF", "OBSERVED_AT", "SUPERSEDES"):
        assert key in appender["env"]


def test_the_intake_workflow_uses_no_secret_places_no_bet_and_only_appends_to_its_own_branch():
    text, doc = load("nfl-qb-confirm.yml")
    assert "secrets." not in text and "airtable" not in text.lower() and "preflight" not in text.lower()
    assert doc[True]["workflow_dispatch"] is not None            # YAML 1.1 reads the key `on` as True
    pushes = re.findall(r"git [^\n]*\bpush\b[^\n]*|^\s+push -q [^\n]*", text, flags=re.M)
    assert pushes and all("HEAD:qb-confirmations" in p for p in pushes) and "--force" not in text and "-f origin" not in text


def test_the_source_type_choices_include_every_non_confirming_type_so_the_validator_not_the_form_is_the_gate():
    _, doc = load("nfl-qb-confirm.yml")
    opts = set(doc[True]["workflow_dispatch"]["inputs"]["source_type"]["options"])
    from nfl_edge.postmortem import qb_confirmations as Q
    assert Q.CONFIRMING_SOURCE_TYPES <= opts
    assert opts <= (Q.CONFIRMING_SOURCE_TYPES | Q.NON_CONFIRMING_SOURCE_TYPES)


def test_the_card_workflow_passes_the_ledger_only_when_it_exists_and_otherwise_stays_fail_closed():
    text, doc = load("nfl-thesis-card.yml")
    assert "--qb-confirmations qb/qb_confirmations" in text and "if [ -d qb/qb_confirmations ]" in text
    fetch = next(s for s in steps(doc, "card") if "qb-confirmations" in s.get("name", ""))
    assert "no confirmed starters are available" in fetch["run"]      # a missing branch is a notice, not an error
    # the card step must still run when there is no ledger: the option is conditional, never required
    card = next(s for s in steps(doc, "card") if s.get("name") == "Build the card")
    assert 'if [ -d qb/qb_confirmations ]; then EXTRA=' in card["run"]


def test_run_nfl_reports_coverage_without_touching_the_pinned_packet_or_failing_the_run():
    text, doc = load("run-nfl.yml")
    cov = next(s for s in steps(doc, "report") if s.get("id") == "qbcov")
    assert cov.get("continue-on-error") is True
    assert "qb_coverage.py" in cov["run"] and "$RUNNER_TEMP/qbcov" in cov["run"]
    assert "data/handicap_report/qb_coverage" not in text      # never written into the published, hash-checked report directory
    up = next(s for s in steps(doc, "report") if s.get("name") == "Upload the quarterback coverage")
    assert up["with"]["name"].startswith("qb-coverage-") and "handicap_report" not in up["with"]["path"]
    names = [s.get("name") for s in steps(doc, "report")]
    assert names.index("Report confirmed-starter quarterback coverage") > names.index("Build the handicap packet")
