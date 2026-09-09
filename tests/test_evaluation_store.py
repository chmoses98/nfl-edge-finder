"""The evaluation corpus is append-only, idempotent, and refuses to hold two truths about one prediction.

The failure this guards against is not a crash. It is a rerun that quietly replaces last week's settlement with
a different one -- because a statistic was corrected, or a close was recomputed from a longer capture window --
leaving a corpus whose numbers cannot be reproduced and whose history cannot be recovered. So a rerun with
identical evidence must write nothing at all, and a rerun with different evidence must fail loudly.
"""
import glob
import gzip
import json
import os

import pytest

from nfl_edge.shadow import evaluation_store as ST

GAME = "2025_01_DAL_PHI"


def row(pid="p1", **kw):
    d = {"prediction_id": pid, "evaluation_version": "eval-1.0.0", "schema_version": "1.0.0",
         "ticker": "KXNFLTOTAL-25SEP04DALPHI-44", "model_version": "shadow-0.4.0", "game_id": GAME,
         "settlement_status": "SETTLED", "settled_yes": 1.0, "settlement_kind": "binary",
         "close_status": "OK", "close_mid": 0.52, "model_p": 0.6,
         "evaluated_at": "2026-09-09T00:00:00+00:00"}
    d.update(kw)
    return d


@pytest.fixture
def corpus(tmp_path):
    return ST.EvaluationCorpus(str(tmp_path / "evaluations"))


def test_a_first_write_creates_one_batch_and_a_manifest_that_matches_it(corpus, tmp_path):
    man = corpus.write_batch(GAME, [row("p1"), row("p2")], evaluation_version="eval-1.0.0", batch="B1")
    assert man["status"] == "WRITTEN" and man["written"] == 2
    d = os.path.join(str(tmp_path / "evaluations"), GAME)
    batch = os.path.join(d, "eval-1.0.0.B1.evaluations.jsonl.gz")
    assert os.path.exists(batch) and os.path.exists(os.path.join(d, "eval-1.0.0.B1.evaluation_manifest.json"))
    assert man["evaluations_sha256"] == ST.sha256_file(batch)
    assert man["by_settlement_status"] == {"SETTLED": 2}
    assert ST.verify_batches(corpus.read_roots)["ok"]


def test_an_identical_rerun_is_a_complete_no_op(corpus, tmp_path):
    corpus.write_batch(GAME, [row("p1")], evaluation_version="eval-1.0.0", batch="B1")
    before = sorted(glob.glob(os.path.join(str(tmp_path), "**", "*"), recursive=True))
    digests = {p: ST.sha256_file(p) for p in before if os.path.isfile(p)}
    # a later run recomputes the same evidence; only the wall clock differs
    again = corpus.write_batch(GAME, [row("p1", evaluated_at="2026-12-25T00:00:00+00:00")],
                               evaluation_version="eval-1.0.0", batch="B2")
    assert again["status"] == "NO_OP" and again["written"] == 0 and again["unchanged"] == 1
    after = sorted(glob.glob(os.path.join(str(tmp_path), "**", "*"), recursive=True))
    assert after == before, "a no-op rerun must not create a file"
    assert {p: ST.sha256_file(p) for p in after if os.path.isfile(p)} == digests


def test_only_the_genuinely_new_rows_are_written_on_a_later_run(corpus):
    corpus.write_batch(GAME, [row("p1")], evaluation_version="eval-1.0.0", batch="B1")
    man = corpus.write_batch(GAME, [row("p1"), row("p2")], evaluation_version="eval-1.0.0", batch="B2")
    assert (man["written"], man["unchanged"]) == (1, 1)
    rows = ST.read_corpus(corpus.read_roots, GAME)
    assert sorted(r["prediction_id"] for r in rows) == ["p1", "p2"]


def test_a_rerun_that_contradicts_a_published_truth_fails_and_writes_nothing(corpus, tmp_path):
    corpus.write_batch(GAME, [row("p1", settled_yes=1.0)], evaluation_version="eval-1.0.0", batch="B1")
    before = sorted(glob.glob(os.path.join(str(tmp_path), "**", "*"), recursive=True))
    with pytest.raises(ST.EvaluationConflict) as e:
        corpus.write_batch(GAME, [row("p1", settled_yes=0.0)], evaluation_version="eval-1.0.0", batch="B2")
    assert "settled_yes" in str(e.value)
    assert sorted(glob.glob(os.path.join(str(tmp_path), "**", "*"), recursive=True)) == before


def test_a_conflict_names_every_field_that_changed(corpus):
    corpus.write_batch(GAME, [row("p1", settled_yes=1.0, close_mid=0.52)],
                       evaluation_version="eval-1.0.0", batch="B1")
    plan = corpus.plan([row("p1", settled_yes=0.0, close_mid=0.61)], GAME)
    assert len(plan["conflicts"]) == 1
    fields = plan["conflicts"][0]["fields"]
    assert set(fields) >= {"settled_yes", "close_mid"}
    assert fields["settled_yes"] == (1.0, 0.0)


def test_a_new_evaluation_version_is_a_new_truth_not_a_replacement(corpus):
    corpus.write_batch(GAME, [row("p1", settled_yes=1.0)], evaluation_version="eval-1.0.0", batch="B1")
    man = corpus.write_batch(GAME, [row("p1", evaluation_version="eval-2.0.0", settled_yes=0.0)],
                             evaluation_version="eval-2.0.0", batch="B2")
    assert man["written"] == 1, "a different evaluation version coexists with the old one"
    rows = ST.read_corpus(corpus.read_roots, GAME)
    assert {(r["evaluation_version"], r["settled_yes"]) for r in rows} == {("eval-1.0.0", 1.0), ("eval-2.0.0", 0.0)}


def test_a_batch_path_is_never_overwritten(corpus):
    corpus.write_batch(GAME, [row("p1")], evaluation_version="eval-1.0.0", batch="B1")
    with pytest.raises(FileExistsError):
        corpus.write_batch(GAME, [row("p9")], evaluation_version="eval-1.0.0", batch="B1")


def test_the_same_prediction_offered_twice_in_one_batch_is_written_once(corpus):
    man = corpus.write_batch(GAME, [row("p1"), row("p1")], evaluation_version="eval-1.0.0", batch="B1")
    assert man["written"] == 1


def test_identity_is_deterministic_and_version_scoped():
    a = ST.evaluation_id("pred-abc", "eval-1.0.0")
    assert a == ST.evaluation_id("pred-abc", "eval-1.0.0")
    assert a != ST.evaluation_id("pred-abc", "eval-2.0.0")
    assert a != ST.evaluation_id("pred-abd", "eval-1.0.0")
    assert ST.stamp(row("p1"))["evaluation_id"] == ST.evaluation_id("p1", "eval-1.0.0")


def test_the_content_hash_ignores_when_a_row_was_computed_and_nothing_else():
    a, b = row("p1"), row("p1", evaluated_at="2030-01-01T00:00:00+00:00")
    assert ST.content_hash(a) == ST.content_hash(b)
    assert ST.content_hash(a) != ST.content_hash(row("p1", settlement_reason="different"))
    assert ST.content_hash(a) != ST.content_hash(row("p1", close_observed_at="2025-09-05T00:00:00+00:00"))


def test_verification_catches_a_batch_edited_after_it_was_written(corpus, tmp_path):
    corpus.write_batch(GAME, [row("p1")], evaluation_version="eval-1.0.0", batch="B1")
    path = os.path.join(str(tmp_path / "evaluations"), GAME, "eval-1.0.0.B1.evaluations.jsonl.gz")
    rows = ST.read_rows(path)
    rows[0]["settled_yes"] = 0.0                      # tamper, leaving the recorded content hash behind
    with gzip.GzipFile(path, "wb", mtime=0) as f:
        f.write((json.dumps(rows[0], sort_keys=True) + "\n").encode())
    v = ST.verify_batches(corpus.read_roots)
    assert not v["ok"]
    assert any("content hash" in p or "sha256" in p for p in v["problems"])


def test_verification_catches_two_batches_disagreeing_about_one_prediction(corpus, tmp_path):
    corpus.write_batch(GAME, [row("p1", settled_yes=1.0)], evaluation_version="eval-1.0.0", batch="B1")
    # write a contradicting batch directly, bypassing plan(), which is what a broken publisher would do
    d = os.path.join(str(tmp_path / "evaluations"), GAME)
    bad = ST.stamp(row("p1", settled_yes=0.0))
    path = os.path.join(d, "eval-1.0.0.B2.evaluations.jsonl.gz")
    with gzip.GzipFile(path, "wb", mtime=0) as f:
        f.write((json.dumps(bad, sort_keys=True) + "\n").encode())
    with open(path.replace(".evaluations.jsonl.gz", ".evaluation_manifest.json"), "w") as f:
        json.dump({"written": 1, "evaluations_sha256": ST.sha256_file(path)}, f)
    v = ST.verify_batches(corpus.read_roots)
    assert not v["ok"] and any("different content" in p for p in v["problems"])


def test_a_published_corpus_is_consulted_before_writing_a_local_batch(tmp_path):
    """The run stages new rows locally but must not duplicate what market-data already holds."""
    published = str(tmp_path / "published")
    ST.EvaluationCorpus(published).write_batch(GAME, [row("p1")], evaluation_version="eval-1.0.0", batch="B1")
    staging = ST.EvaluationCorpus(str(tmp_path / "staging"), read_roots=[published])
    man = staging.write_batch(GAME, [row("p1"), row("p2")], evaluation_version="eval-1.0.0", batch="B2")
    assert (man["written"], man["unchanged"]) == (1, 1)
    assert [r["prediction_id"] for r in ST.read_corpus([str(tmp_path / "staging")], GAME)] == ["p2"]


def test_the_corpus_lists_the_games_it_holds(corpus):
    corpus.write_batch(GAME, [row("p1")], evaluation_version="eval-1.0.0", batch="B1")
    corpus.write_batch("2025_01_KC_LAC", [row("p2", game_id="2025_01_KC_LAC")],
                       evaluation_version="eval-1.0.0", batch="B1")
    assert corpus.games() == ["2025_01_DAL_PHI", "2025_01_KC_LAC"]
    assert corpus.evaluated_prediction_ids(GAME) == {"p1"}
