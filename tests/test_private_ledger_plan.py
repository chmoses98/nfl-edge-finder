import json
import os

import pytest

from nfl_edge.handicap import ledger_privacy as LP


def _ledger(tmp_path):
    root = tmp_path / "src"
    for kind, n in (("imported_wagers", 2), ("wager_settlements", 2), ("recommendations", 1), ("postmortems", 1)):
        d = root / "data" / kind / "2026" / "week_07"
        d.mkdir(parents=True)
        for i in range(n):
            (d / f"{kind}-{i}.json").write_text(json.dumps({"k": kind, "i": i, "stake": 75}))
    return str(root)


def test_plan_classifies_kinds_and_reports_counts_without_contents(tmp_path):
    p = LP.plan(_ledger(tmp_path))
    assert p["per_kind"]["imported_wagers"]["class"] == "OWNER_PRIVATE" and p["per_kind"]["recommendations"]["class"] == "PUBLIC_OK"
    assert p["review_kinds_present"] == ["postmortems"] and p["owner_private_files"] == 4
    assert "does_not_do" in p and any(c["workflow"] == "preflight.yml" for c in p["consumers"])


def test_manifest_hash_is_stable_and_changes_with_content(tmp_path):
    r = _ledger(tmp_path)
    a = LP.plan(r)["owner_private_manifest_sha256"]
    assert a == LP.plan(r)["owner_private_manifest_sha256"]
    f = next(p for p, _ in LP.plan(r)["private_files"])
    open(os.path.join(r, f), "w").write("{}")
    assert LP.plan(r)["owner_private_manifest_sha256"] != a


def test_copy_refuses_an_unproven_target_and_never_touches_the_source(tmp_path):
    r = _ledger(tmp_path)
    before = LP.plan(r)["owner_private_manifest_sha256"]
    dst = tmp_path / "dst"
    dst.mkdir()
    with pytest.raises(PermissionError):
        LP.copy_private(r, str(dst))
    with pytest.raises(PermissionError):
        LP.copy_private(r, str(dst), target_is_private=lambda d: False)
    assert not any(dst.iterdir()) and LP.plan(r)["owner_private_manifest_sha256"] == before


def test_copy_into_a_verified_private_target_copies_only_private_kinds_and_verifies_hashes(tmp_path):
    r = _ledger(tmp_path)
    dst = tmp_path / "dst"
    dst.mkdir()
    res = LP.copy_private(r, str(dst), target_is_private=lambda d: True)
    assert res["copied"] == 4 and res["hash_mismatches"] == [] and res["source_modified"] is False
    kinds = {p.split("/")[1] for p in (f["path"] for f in json.load(open(dst / "MIGRATION_MANIFEST.json"))["files"])}
    assert kinds == {"imported_wagers", "wager_settlements"}
    assert not (dst / "data" / "recommendations").exists()
    assert LP.plan(str(dst))["owner_private_manifest_sha256"] == res["manifest_sha256"]


def test_copy_into_the_source_is_refused(tmp_path):
    r = _ledger(tmp_path)
    with pytest.raises(ValueError):
        LP.copy_private(r, r, allow_local_target=True)
