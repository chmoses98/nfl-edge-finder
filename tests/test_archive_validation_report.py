"""The archive validation's own arithmetic must reconcile, and its claims must be no broader than its evidence.

"Validated against 15,021 real settled markets" is the kind of sentence that quietly becomes false: it can drift
into meaning "we examined 15,021 markets" (we examined 61,557) or "every family is archive-validated" (one is
not). So the committed report is checked here: the buckets must sum to the examined total, the headline rate must
be over the comparable set, and any family with no archived markets must say so in its own coverage row.
"""
import json
import os
import re

from nfl_edge.settlement.settle import SETTLEABLE_FAMILIES

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
RESULTS = os.path.join(ROOT, "research", "settlement_validation", "results.json")
NARRATIVE = os.path.join(ROOT, "research", "settlement_validation", "RESULTS.md")


def load():
    with open(RESULTS) as f:
        return json.load(f)


def test_every_examined_market_is_accounted_for_in_exactly_one_bucket():
    r = load()["reconciliation"]
    assert r["reconciles"] is True
    assert r["accounted_for"] == r["finalized_archive_markets_examined"]
    buckets = ("dropped_unsupported_family", "dropped_no_game_join", "dropped_player_identity_unresolved",
               "dropped_kalshi_outcome_unusable", "dropped_engine_refused_semantics",
               "set_aside_kalshi_late_bulk_settlement", "independently_comparable_settlements")
    assert sum(r[b] for b in buckets) == r["finalized_archive_markets_examined"]


def test_the_headline_rate_is_over_the_comparable_set_not_the_examined_set():
    r = load()["reconciliation"]
    assert r["independently_comparable_settlements"] == r["agreements"] + r["disagreements"]
    assert r["independently_comparable_settlements"] < r["finalized_archive_markets_examined"], (
        "the comparable set is a subset; if these were equal the report would be claiming too much")
    expected = r["agreements"] / r["independently_comparable_settlements"]
    assert abs(r["agreement_on_comparable"] - expected) < 1e-6


def test_every_production_settled_family_has_a_coverage_row():
    cov = load()["family_coverage"]
    assert set(cov) == set(SETTLEABLE_FAMILIES), (
        "a family the engine settles in production with no coverage row is an unstated gap")


def test_a_family_with_no_archived_markets_says_so_instead_of_implying_validation():
    cov = load()["family_coverage"]
    for fam, c in cov.items():
        if c["archive_markets_examined"] == 0:
            assert c["comparable"] == 0 and c["agreement_on_comparable"] is None
            assert "ONLY" in c["evidence"] and "no archived markets" in c["evidence"], fam
        else:
            assert "archive cross-check" in c["evidence"], fam


def test_both_teams_score_is_the_family_with_no_archive_coverage():
    """Named explicitly so the gap cannot be forgotten if the archive later gains the series."""
    c = load()["family_coverage"]["BOTH_TEAMS_SCORE_N"]
    assert c["archive_markets_examined"] == 0, (
        "if KXNFLBOTH has appeared in the archive, this test should be updated and the family re-validated")


def test_per_family_agreement_sums_to_the_overall_figure():
    d = load()
    agree = sum(c["agreements"] for c in d["family_coverage"].values())
    dis = sum(c["disagreements"] for c in d["family_coverage"].values())
    assert (agree, dis) == (d["reconciliation"]["agreements"], d["reconciliation"]["disagreements"])


def test_the_narrative_reports_the_examined_total_beside_the_comparable_total():
    text = open(NARRATIVE).read()
    r = load()["reconciliation"]
    assert f"{r['finalized_archive_markets_examined']:,}" in text, "the examined total must be stated"
    assert f"{r['independently_comparable_settlements']:,}" in text
    assert "independently comparable" in text
    assert "rules text + unit tests ONLY" in text or "rules text + unit tests" in text


def test_the_narrative_never_claims_a_bare_validated_against_count():
    """The specific phrasing the review rejected: a count with no statement of what it is a count OF."""
    text = open(NARRATIVE).read().lower()
    for bad in (r"validated against 15,021 real settled markets",
                r"validated against \d[\d,]* markets\b(?! examined)"):
        assert not re.search(bad, text), f"ambiguous claim found: {bad}"
