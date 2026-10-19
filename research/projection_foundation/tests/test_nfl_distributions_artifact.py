"""The NFL distribution artifact (nfl/live/distributions_artifact.py): `projections/nfl/distributions/latest.json`.

The archive in tests/fixtures/nfl_dist/archive is REAL: the `projections/nfl/latest.json` the live run published at 2026-10-19T01:34:27Z (WAS @ SF,
72 player rows) and every challenger forecast file archived for that game (forecasts/nfl/2026-10-20/*.jsonl.gz, byte-identical, several versions of
each forecast). The builder reads them and writes a second artifact beside latest.json; it never edits an archived file or the protected research code.
"""
import copy
import gzip
import json
import os
import shutil
import subprocess
import sys

import pytest

PF = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, PF)

from pf_core import archive_guard  # noqa: E402
from nfl.live import distribution as DI  # noqa: E402
from nfl.live import distributions_artifact as DA  # noqa: E402

REAL_ARCHIVE = os.path.join(os.path.dirname(__file__), "fixtures", "nfl_dist", "archive")
KITTLE, MCCAFFREY = "00-0033288", "00-0033280"


@pytest.fixture
def archive(tmp_path):
    dst = tmp_path / "archive"
    shutil.copytree(REAL_ARCHIVE, dst)
    subprocess.run(["git", "init", "-q", str(dst)], check=True)
    subprocess.run(["git", "-C", str(dst), "-c", "user.email=a@b", "-c", "user.name=t", "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(dst), "-c", "user.email=a@b", "-c", "user.name=t", "commit", "-q", "-m", "real archive"], check=True)
    return str(dst)


def latest(a):
    return json.load(open(os.path.join(a, "projections", "nfl", "latest.json")))


def set_latest(a, doc):
    json.dump(doc, open(os.path.join(a, "projections", "nfl", "latest.json"), "w"))


def row_of(art, pid, fam):
    return next(r for r in art["rows"] if r["player_id"] == pid and r["family"] == fam)


def test_every_row_of_the_real_feed_is_reproduced_from_its_archived_pmf(archive):
    res = DA.build(archive)
    art, st = res["artifact"], res["stats"]
    assert art["schema"] == "sift.projection_distributions.v1" and art["sport"] == "NFL"
    assert st["published_rows"] == 72 and st["rows"] == 72 and st["excluded"] == 0, st
    assert art["projection"]["generated_utc"] == latest(archive)["generated_utc"]            # the artifact names the feed it describes
    assert art["excluded"] == []
    assert {r["family"] for r in art["rows"]} >= {"receptions", "completions", "targets", "receiving_yards", "anytime_td"}


def test_kittle_and_mccaffrey_receptions_carry_the_distribution_the_feed_prices_from(archive):
    art = DA.build(archive)["artifact"]
    pub = {(p["player_id"], p["family"]): p for p in latest(archive)["players"]}
    for pid, q in ((KITTLE, {"p05": 1, "p10": 2, "p25": 3, "p50": 5, "p75": 7, "p90": 8, "p95": 10}),
                   (MCCAFFREY, {"p05": 1, "p10": 2, "p25": 3, "p50": 5, "p75": 6, "p90": 8, "p95": 9})):
        r, p = row_of(art, pid, "receptions"), pub[(pid, "receptions")]
        assert r["quantiles"] == q
        assert (r["mean"], r["median"], r["p10"], r["p90"]) == (p["mean"], p["median"], p["p10"], p["p90"])
        assert {k: r["survival"][k] for k in p["thresholds"]} == p["thresholds"]                 # the published rungs, unchanged
        ks = sorted(int(k) for k in r["survival"])
        assert ks == list(range(ks[0], ks[-1] + 1)) and "6" in r["survival"]                     # every integer line, incl. the 6+ main line
        assert DI.validate_row({**r, "thresholds": r["survival"]}) == []
        assert r["forecast_id"] and r["forecast_generated_utc"] <= art["projection"]["generated_utc"]


def test_yardage_and_binary_families_publish_quantiles_without_inventing_a_ladder(archive):
    art = DA.build(archive)["artifact"]
    pub = {(p["player_id"], p["family"]): p for p in latest(archive)["players"]}
    y = row_of(art, KITTLE, "receiving_yards")
    assert set(y["survival"]) == set(pub[(KITTLE, "receiving_yards")]["thresholds"])          # only the study's rungs
    assert DI.validate_row({**y, "thresholds": y["survival"]}) == []
    td = row_of(art, KITTLE, "anytime_td")
    assert set(td["survival"]) == {"1"} and td["quantiles"]["p05"] in (0, 1)


def test_the_newest_pregame_forecast_is_used_and_a_later_one_is_not(archive):
    """Forecasts generated after the projection (or at/after the start) are never used for it."""
    fc = DA.load_forecasts(archive, "2026-10-19T01:34:27Z")
    assert fc and all(r["generated_utc"] <= "2026-10-19T01:34:27Z" for r in fc.values())
    early = DA.load_forecasts(archive, "2026-10-18T05:00:00Z")
    assert all(r["generated_utc"] <= "2026-10-18T05:00:00Z" for r in early.values())
    assert DA.load_forecasts(archive, "2026-10-17T00:00:00Z") == {}


def test_a_row_whose_pmf_does_not_reproduce_the_published_row_is_left_out_not_patched(archive):
    doc = latest(archive)
    k = next(p for p in doc["players"] if p["player_id"] == KITTLE and p["family"] == "receptions")
    c = next(p for p in doc["players"] if p["player_id"] == MCCAFFREY and p["family"] == "receptions")
    k["mean"] = 5.6                        # a different expected value than the archived pmf's
    c["thresholds"]["5"] = 0.70            # a published probability the pmf does not give
    c2 = copy.deepcopy(doc["players"][0])
    c2["player_id"], c2["name"] = "00-NOARCHIVE", "No Archive"
    doc["players"].append(c2)              # a published row with no archived forecast
    set_latest(archive, doc)
    res = DA.build(archive)
    why = {(e["player_id"], e["family"]): e["why"] for e in res["artifact"]["excluded"]}
    assert "mean" in why[(KITTLE, "receptions")]
    assert "P(X>=5)" in why[(MCCAFFREY, "receptions")]
    assert why[("00-NOARCHIVE", c2["family"])] == "no archived forecast for this row"
    assert not any(r["player_id"] == KITTLE and r["family"] == "receptions" for r in res["artifact"]["rows"])
    assert res["stats"]["excluded"] == 3 and res["stats"]["rows"] == 72 - 2


def test_median_p10_p90_must_match_too(archive):
    doc = latest(archive)
    for p in doc["players"]:
        if p["player_id"] == KITTLE and p["family"] == "receptions":
            p["p90"] = 9
    set_latest(archive, doc)
    why = {(e["player_id"], e["family"]): e["why"] for e in DA.build(archive)["artifact"]["excluded"]}
    assert "p90" in why[(KITTLE, "receptions")]


def test_a_corrupt_archived_pmf_is_left_out(archive, tmp_path):
    # rewrite the newest forecast file of the archive with a pmf that does not sum to 1 for one row
    d = os.path.join(archive, "forecasts", "nfl", "2026-10-20")
    f = sorted(os.listdir(d))[1]
    rows = [json.loads(line) for line in gzip.open(os.path.join(d, f), "rt")]
    target = next(r for r in rows if r["entity_id"] == KITTLE and r["family"] == "receptions")
    target["probs"] = [0.5] + target["probs"][1:]
    # a corrupt row dated after every real one wins "newest": it must be rejected, not silently skipped to an older version
    target["generated_utc"] = "2026-10-19T01:34:00Z"
    with gzip.open(os.path.join(d, "013400Z_corrupt.jsonl.gz"), "wt") as g:
        g.write(json.dumps(target) + "\n")
    res = DA.build(archive)
    why = {(e["player_id"], e["family"]): e["why"] for e in res["artifact"]["excluded"]}
    assert "probability distribution" in why[(KITTLE, "receptions")]


def test_write_is_idempotent_write_once_and_never_regresses(archive):
    art = DA.build(archive)["artifact"]
    w1 = DA.write(archive, art)
    assert w1["written"] and w1["latest"] == "projections/nfl/distributions/latest.json" and w1["copy"].endswith("2026-10-19T0134Z.json.gz")
    assert os.path.exists(os.path.join(archive, w1["copy"])) and os.path.exists(os.path.join(archive, w1["latest"]))
    saved = open(os.path.join(archive, w1["copy"]), "rb").read()
    again = DA.build(archive)["artifact"]                       # only `built_utc` differs
    assert DA.write(archive, again) == {"written": False, "why": "unchanged"}
    assert open(os.path.join(archive, w1["copy"]), "rb").read() == saved                  # the timestamped copy is never rewritten
    older = copy.deepcopy(again)
    older["projection"]["generated_utc"] = "2026-10-18T01:34:27Z"
    older["rows"] = older["rows"][:3]
    assert DA.write(archive, older)["written"] is False         # an older projection never replaces the newer artifact
    assert json.load(open(os.path.join(archive, w1["latest"])))["projection"]["generated_utc"] == "2026-10-19T01:34:27Z"
    # the bytes of the gz copy are a pure function of the content
    with gzip.open(os.path.join(archive, w1["copy"]), "rt") as f:
        assert json.load(f)["rows"] == art["rows"]


def test_nothing_archived_or_published_is_modified_and_the_archive_guard_is_clean(archive):
    before = {}
    for root, _, files in os.walk(archive):
        if ".git" in root:
            continue
        for f in files:
            p = os.path.join(root, f)
            before[p] = open(p, "rb").read()
    art = DA.build(archive)["artifact"]
    DA.write(archive, art)
    for p, b in before.items():
        assert open(p, "rb").read() == b, p                   # latest.json, every forecast file: byte-identical
    assert archive_guard.violations(archive) == []
    new = [os.path.relpath(os.path.join(r, f), archive) for r, _, fs in os.walk(archive) if ".git" not in r for f in fs
           if os.path.join(r, f) not in before]
    assert sorted(new) == ["projections/nfl/distributions/2026-10-19T0134Z.json.gz", "projections/nfl/distributions/latest.json"]


def test_no_projection_document_means_nothing_to_publish(tmp_path):
    res = DA.build(str(tmp_path))
    assert res["artifact"] is None
    bad = tmp_path / "projections" / "nfl"
    bad.mkdir(parents=True)
    json.dump({"schema": "sift.projections.v2", "sport": "NFL", "players": []}, open(bad / "latest.json", "w"))
    assert DA.build(str(tmp_path))["artifact"] is None


def test_cli_check_writes_nothing_and_reports(archive, capsys, tmp_path):
    out = tmp_path / "s.json"
    assert DA.main(["--archive", archive, "--check", "--summary-out", str(out)]) == 0
    assert not os.path.exists(os.path.join(archive, "projections", "nfl", "distributions"))
    s = json.load(open(out))
    assert s["rows"] == 72 and s["excluded"] == 0 and s["write"]["why"] == "--check"
    assert DA.main(["--archive", archive]) == 0
    assert os.path.exists(os.path.join(archive, "projections", "nfl", "distributions", "latest.json"))
