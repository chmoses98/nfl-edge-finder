"""The 4H-A auditor: does it actually authenticate, and can it actually say FAIL?

The auditor delegates every judgement to `approval.verify`, which has its own test matrix; re-testing that
here would prove nothing new. What is tested here is the part that belongs to the wrapper:

  * it finds the row only among APPROVED rows, so "this row is approved" is established by WHERE it was
    found rather than by a string it compares for itself;
  * its positive path passes on a genuinely signed approval;
  * each of its negative controls REFUSES, and -- the property that matters -- a control that verified
    would be reported as a failure rather than quietly counted as a pass;
  * it writes nothing.

The fixtures sign with a real HMAC over a real canonical message, so the control path exercises the same
code the runner will.
"""
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.join(ROOT, "scripts", "handicap"))

from nfl_edge.handicap import airtable_bridge as AB          # noqa: E402
from nfl_edge.handicap import approval as APPROVAL           # noqa: E402
import audit_preflight_approval as AUDIT                     # noqa: E402

KEY = b"test-key-not-a-production-secret"
REC = "recAUDITFIXTURE01"
RUN = "AUDIT-FIXTURE-RUN"
MANIFEST = "a" * 64
CREATED = "2026-09-14T15:47:00.000Z"
AS_OF = "2026-09-14T15:47:04.200000+00:00"


def _payloads():
    rec = {"recommendation_id": "rec_fixture", "created_at": AS_OF,
           "kickoff_utc": "2026-09-15T00:15:00+00:00"}
    return json.dumps([rec], sort_keys=True), AB.canonical_payload([rec])


def _row(*, key=KEY, manifest=MANIFEST, status=AB.STATUS_PREFLIGHT_APPROVED, run=RUN):
    candidate_raw, approved_raw = _payloads()
    block = APPROVAL.issue(key=key, airtable_record_id=REC, run_id=run,
                           candidate_payload=candidate_raw, approved_payload=approved_raw,
                           approval_as_of=AS_OF, evidence_manifest_sha256=manifest)
    result = dict(block, airtable_record_id=REC, run_id=run, approval_as_of=AS_OF,
                  candidate_payload_sha256=APPROVAL.sha256_text(candidate_raw),
                  approved_payload_sha256=APPROVAL.sha256_text(approved_raw),
                  verdict="APPROVED")
    return {"id": REC, "createdTime": CREATED,
            "fields": {AB.F_RUN_ID: run, AB.F_STATUS: status,
                       AB.F_PAYLOAD: candidate_raw, AB.F_APPROVED_PAYLOAD: approved_raw,
                       AB.F_PREFLIGHT_RESULT: json.dumps(result)}}


class _Client:
    """Only what the auditor uses. Any write attempt is a test failure, not a silent no-op."""

    def __init__(self, rows, *, boom=None):
        self.rows, self.boom, self.calls = rows, boom, []

    def list_by_status(self, status, sport=AB.SPORT_NFL):
        self.calls.append(("list_by_status", status))
        if self.boom:
            raise self.boom
        return [r for r in self.rows if (r["fields"].get(AB.F_STATUS) == status)]

    def set_status(self, *a, **k):        # pragma: no cover - must never be reached
        raise AssertionError("the auditor wrote to Airtable")

    def write_fields(self, *a, **k):      # pragma: no cover - must never be reached
        raise AssertionError("the auditor wrote to Airtable")


@pytest.fixture
def evidence(monkeypatch):
    """The auditor delegates evidence reading to the importer; stub that one seam, not the crypto."""
    monkeypatch.setattr(AB, "read_preflight_evidence", lambda fields, root: ([{"doc": 1}], MANIFEST))


def test_the_control_path_authenticates_a_genuinely_signed_approval(evidence):
    row = _row()
    out = AUDIT.audit(row, record_id=REC, run_id=RUN, evidence_root="/nonexistent", key=KEY)
    assert out["schema"] == APPROVAL.APPROVAL_SCHEMA
    assert out["evidence_manifest_sha256"] == MANIFEST
    assert out["status"] == AB.STATUS_PREFLIGHT_APPROVED


def test_every_negative_control_refuses_the_real_signed_approval(evidence):
    row = _row()
    out = AUDIT.audit(row, record_id=REC, run_id=RUN, evidence_root="/x", key=KEY)
    result, cand, appr, man = out["_inputs"]
    controls = AUDIT.negative_controls(result=result, candidate_raw=cand, approved_raw=appr,
                                       manifest=man, record_id=REC, run_id=RUN, key=KEY)
    assert controls, "the auditor ran no negative controls"
    bad = [c for c in controls if c["outcome"] != "REFUSED"]
    assert not bad, f"a tampered approval was accepted: {bad}"
    names = {c["control"] for c in controls}
    for required in ("tamper_approved_payload", "tamper_candidate_payload", "tamper_approval_as_of",
                     "tamper_manifest", "tamper_record_id", "tamper_run_id"):
        assert required in names, f"the auditor does not run the {required} control"


def test_a_control_that_verified_would_be_reported_not_swallowed(evidence, monkeypatch):
    """The audit's own alarm. If `verify` ever stopped refusing, the run must FAIL, not print PASS."""
    monkeypatch.setattr(APPROVAL, "verify", lambda *a, **k: object())
    row = _row()
    controls = AUDIT.negative_controls(result=json.loads(row["fields"][AB.F_PREFLIGHT_RESULT]),
                                       candidate_raw=row["fields"][AB.F_PAYLOAD],
                                       approved_raw=row["fields"][AB.F_APPROVED_PAYLOAD],
                                       manifest=MANIFEST, record_id=REC, run_id=RUN, key=KEY)
    assert all(c["outcome"] != "REFUSED" for c in controls)
    assert [c for c in controls if c["outcome"] != "REFUSED"], "a leaked control must be visible to main()"


@pytest.mark.parametrize("field,label", [
    (AB.F_PAYLOAD, "candidate payload"),
    (AB.F_APPROVED_PAYLOAD, "approved payload"),
])
def test_an_edited_payload_fails_the_positive_path(evidence, field, label):
    row = _row()
    row["fields"][field] = row["fields"][field] + " "
    with pytest.raises(APPROVAL.ApprovalError):
        AUDIT.audit(row, record_id=REC, run_id=RUN, evidence_root="/x", key=KEY)


def test_a_wrong_manifest_fails_the_positive_path(monkeypatch):
    monkeypatch.setattr(AB, "read_preflight_evidence", lambda f, r: ([{"doc": 1}], "b" * 64))
    with pytest.raises(APPROVAL.ApprovalError):
        AUDIT.audit(_row(), record_id=REC, run_id=RUN, evidence_root="/x", key=KEY)


def test_a_row_with_no_evidence_manifest_is_refused_rather_than_passed(monkeypatch):
    """`(None, None)` means nothing is bound. The auditor must not read that as 'nothing to check'."""
    monkeypatch.setattr(AB, "read_preflight_evidence", lambda f, r: (None, None))
    with pytest.raises(AUDIT.AuditFailure):
        AUDIT.audit(_row(), record_id=REC, run_id=RUN, evidence_root="/x", key=KEY)


def test_the_wrong_run_id_is_refused(evidence):
    with pytest.raises(AUDIT.AuditFailure):
        AUDIT.audit(_row(), record_id=REC, run_id="SOME-OTHER-RUN", evidence_root="/x", key=KEY)


def test_the_wrong_signing_key_is_refused(evidence):
    with pytest.raises(APPROVAL.ApprovalError):
        AUDIT.audit(_row(), record_id=REC, run_id=RUN, evidence_root="/x", key=b"wrong-key")


def test_a_row_that_is_not_approved_is_never_located():
    """Status is established by the query. A BLOCKED row is simply not in the approved list."""
    blocked = _row(status=AB.STATUS_PREFLIGHT_BLOCKED)
    client = _Client([blocked])
    with pytest.raises(AUDIT.AuditFailure) as e:
        AUDIT.find_approved_row(client, REC)
    assert AB.STATUS_PREFLIGHT_APPROVED in str(e.value)
    assert client.calls == [("list_by_status", AB.STATUS_PREFLIGHT_APPROVED)]


def test_a_missing_row_is_refused():
    with pytest.raises(AUDIT.AuditFailure):
        AUDIT.find_approved_row(_Client([]), REC)


def test_an_airtable_read_failure_is_raised_not_reported_as_a_clean_audit():
    client = _Client([], boom=AB.TransientError("airtable is down"))
    with pytest.raises(AB.TransientError):
        AUDIT.find_approved_row(client, REC)


def test_the_auditor_never_writes(evidence):
    """The stub raises on any write. Reaching the end of a full audit proves none was attempted."""
    client = _Client([_row()])
    row = AUDIT.find_approved_row(client, REC)
    AUDIT.audit(row, record_id=REC, run_id=RUN, evidence_root="/x", key=KEY)
    assert client.calls == [("list_by_status", AB.STATUS_PREFLIGHT_APPROVED)]


def test_the_audit_script_issues_no_write_call_and_no_kalshi_call():
    """A guard over the CODE, not the prose.

    An earlier version of this test grepped the raw file and tripped on its own docstring, which says the
    auditor touches no Kalshi endpoint. Scanning text cannot tell a promise from a call, so this walks the
    AST instead: it fails on an actual write or venue call and is indifferent to comments about them.
    """
    import ast                                                            # noqa: PLC0415
    path = os.path.join(ROOT, "scripts", "handicap", "audit_preflight_approval.py")
    tree = ast.parse(open(path).read())

    called = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            f = node.func
            called.add(f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", ""))
    for forbidden in ("set_status", "write_fields", "apply_plan", "run", "check_call", "urlopen"):
        assert forbidden not in called, f"the auditor calls {forbidden!r}"

    imported = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported.update(a.name.split(".")[0] for a in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported.add((node.module or "").split(".")[0])
            imported.update(a.name for a in node.names)
    for forbidden in ("subprocess", "kalshi", "socket", "requests", "urllib"):
        assert forbidden not in imported, f"the auditor imports {forbidden!r}"
    # It reaches Airtable only through the bridge, whose read surface is list_by_status.
    assert "airtable_bridge" in imported or "AB" in imported


def test_the_workflow_is_dispatch_only_and_read_only():
    """Parse the YAML rather than grep it -- the file's comments legitimately discuss `contents: write`."""
    import yaml                                                           # noqa: PLC0415
    path = os.path.join(ROOT, ".github", "workflows", "preflight-approval-audit.yml")
    wf = yaml.safe_load(open(path))

    triggers = wf.get("on") if "on" in wf else wf.get(True)               # YAML reads bare `on` as True
    assert set(triggers) == {"workflow_dispatch"}, f"extra triggers: {sorted(set(triggers))}"
    assert wf["permissions"] == {"contents": "read"}, wf["permissions"]

    steps = wf["jobs"]["audit"]["steps"]
    checkouts = [s for s in steps if str(s.get("uses", "")).startswith("actions/checkout")]
    assert len(checkouts) == 2, "expected exactly the code and evidence checkouts"
    runs = " ".join(s.get("run", "") for s in steps)
    for forbidden in ("git push", "git commit", "gh issue", "gh pr"):
        assert forbidden not in runs, f"the auditor workflow runs {forbidden!r}"
    assert "audit_preflight_approval.py" in runs
