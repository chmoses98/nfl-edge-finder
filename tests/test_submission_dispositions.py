"""The analyst's submission: deep-review standard, the five dispositions, ladder pricing, bankroll fail-closed, and public redaction."""
import json
import os
from datetime import timedelta

import pytest

from nfl_edge.handicap import bankroll as BK
from nfl_edge.handicap import card as C
from nfl_edge.handicap import dossier as DS
from nfl_edge.handicap import ladder_fair as LF
from nfl_edge.handicap import submission as SB
from card_fixtures import AS_OF, GAME, build_run, schedule_text, thesis

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pytestmark = pytest.mark.owner_policy

# the fixture packet has no injuries/script sections, so it can only supply these evidence categories; the knob is the module constant
FIXTURE_CATEGORIES = (("team_matchup", 2), ("qb_ol", 1), ("environment", 1))


@pytest.fixture(autouse=True)
def _fixture_categories(monkeypatch):
    monkeypatch.setattr(DS, "REQUIRED_CATEGORIES", FIXTURE_CATEGORIES)


def review(verdict="THESIS", **kw):
    r = {"game_id": GAME, "verdict": verdict,
         "coverage": {"team_matchup": ["TM:AAA:proe", "TM:BBB:proe"], "qb_ol": ["OL:AAA"], "environment": ["ENV:weather"], "markets": ["FAM:SPREAD|FULL"]},
         "player_markets_reason": "No player market in this game has a priced ladder with three usable rungs; none was viable.",
         "reasoning": "x" * 130}
    r.update(kw)
    return r


def sub(reviews, theses=(), sha=None):
    return {"submission_version": "1", "analyst": "t", "packet_sha": sha, "reviews": list(reviews), "theses": list(theses)}


def go(tmp_path, submission, mode=C.REHEARSAL, **kw):
    r = build_run(tmp_path)
    submission = dict(submission, packet_sha=submission.get("packet_sha") or r["packet"].get("packet_sha"))
    return C.run_card(run=r, theses=[], schedule_text=schedule_text(), root=ROOT, as_of=AS_OF, mode=mode, draws=20000, submission=submission, **kw)


def dossier_for(tmp_path):
    r = build_run(tmp_path)
    g = r["packet"]["games"][0]
    return DS.build_dossier_v2(g, DS.slate_reference(r["packet"]), DS.schedule_row(schedule_text(), g["game_id"]), C.shard(r, g["game_id"])["rows"], None, None, r["packet"].get("week"))


# ---------------------------------------------------------------- the deep-review standard
def test_a_review_that_cites_real_evidence_in_every_category_qualifies(tmp_path):
    assert SB.deep_review_check(review(), dossier_for(tmp_path))["qualifies"]


@pytest.mark.parametrize("mutate,needle", [
    (lambda r: r["coverage"].pop("qb_ol"), "qb_ol"),
    (lambda r: r["coverage"].update(team_matchup=["TM:AAA:proe"]), "team_matchup"),
    (lambda r: r["coverage"].update(environment=["ENV:made-up"]), "not in this game's dossier"),
    (lambda r: r.update(reasoning="short"), "reasoning"),
    (lambda r: r["coverage"].update(markets=[]), "game-line family"),
    (lambda r: r.update(player_markets_reason=""), "player"),
])
def test_scanning_or_thin_reviews_do_not_qualify(tmp_path, mutate, needle):
    r = review()
    mutate(r)
    chk = SB.deep_review_check(r, dossier_for(tmp_path))
    assert not chk["qualifies"] and needle in " ".join(chk["problems"])


def test_an_id_from_the_wrong_category_does_not_count(tmp_path):
    r = review()
    r["coverage"]["qb_ol"] = ["ENV:weather"]
    assert not SB.deep_review_check(r, dossier_for(tmp_path))["qualifies"]


# ---------------------------------------------------------------- dispositions
def test_no_review_record_is_not_reviewed_even_with_a_thesis_present(tmp_path):
    card = go(tmp_path, sub([], [thesis()]))
    g = card["games"][0]
    assert g["disposition"] == SB.D_NOT_REVIEWED and card["lines"] == []
    assert card["theses"][0]["outcome"] == "NOT_PRICED"
    assert card["review_coverage"]["not_reviewed_games"] == 1


def test_a_thin_review_leaves_the_game_not_reviewed_and_the_thesis_unpriced(tmp_path):
    card = go(tmp_path, sub([review(reasoning="x")], [thesis()]))
    assert card["games"][0]["disposition"] == SB.D_NOT_REVIEWED and card["theses"][0]["outcome"] == "NOT_PRICED"
    assert "deep-review standard" in card["games"][0]["state_reason"]


def test_rejected_review_is_reviewed_rejected(tmp_path):
    card = go(tmp_path, sub([review("REJECTED")]))
    assert card["games"][0]["disposition"] == SB.D_REJECTED and card["lines"] == []


def test_insufficient_data_needs_a_named_item_and_a_cited_id(tmp_path):
    ok = review("INSUFFICIENT_DATA", missing=["starting quarterback unresolved between two sources"])
    ok["coverage"] = {"qb_ol": ["OL:AAA"]}
    assert go(tmp_path, sub([ok]))["games"][0]["disposition"] == SB.D_INSUFFICIENT
    bad = review("INSUFFICIENT_DATA", missing=[])
    assert go(tmp_path / "b", sub([bad]))["games"][0]["disposition"] == SB.D_NOT_REVIEWED


def test_thesis_verdict_without_a_thesis_is_not_reviewed(tmp_path):
    assert go(tmp_path, sub([review("THESIS")]))["games"][0]["disposition"] == SB.D_NOT_REVIEWED


def test_a_priced_thesis_resting_only_on_raw_statistics_is_rejected_by_the_challenge(tmp_path):
    th = dict(thesis(), evidence_ids=["TM:AAA:proe", "TM:BBB:proe"])
    th.pop("evidence")
    card = go(tmp_path, sub([review()], [th]))
    rep = card["theses"][0]
    assert card["lines"] == [] and card["games"][0]["disposition"] == SB.D_REJECTED, card["games"][0]
    assert "C4" in json.dumps(rep["pass_reasons"]) or rep["pass_reasons"]


def test_reviewed_and_priced_thesis_is_a_candidate_in_rehearsal_and_never_a_bet(tmp_path, monkeypatch):
    adjusted = [{"id": "TM:X", "claim": "adjusted pass offence +0.10", "opponent_adjusted": True, "market_unmoved": False, "category": "team_matchup", "kind": "MEASURED"}]
    monkeypatch.setattr(SB, "resolve_thesis_evidence", lambda th, d: (adjusted, [], []))
    card = go(tmp_path, sub([review()], [thesis()]))
    g = card["games"][0]
    assert card["lines"] and g["disposition"] == SB.D_CANDIDATE
    assert card["lines"][0]["status"].startswith("REHEARSAL")
    assert card["review_coverage"]["deeply_reviewed_games"] == 1


def test_live_submission_for_another_packet_is_refused(tmp_path):
    r = build_run(tmp_path)
    s = sub([review()], [thesis()], sha="not-this-packet")
    s["packet_sha"] = "not-this-packet"
    card = C.run_card(run=r, theses=[], schedule_text=schedule_text(), root=ROOT, as_of=AS_OF, mode=C.LIVE, draws=20000, submission=s)
    assert card["games"][0]["disposition"] == SB.D_NOT_REVIEWED and "Re-read the current packet" in card["games"][0]["state_reason"] + json.dumps(card["review_coverage"])


def test_unresolvable_thesis_evidence_id_is_not_priced(tmp_path):
    th = dict(thesis(), evidence_ids=["TM:NOPE"])
    card = go(tmp_path, sub([review()], [th]))
    assert card["theses"][0]["outcome"] == "NOT_PRICED" and "does not resolve" in card["theses"][0]["pass_reasons"][0]


def test_thesis_evidence_is_resolved_from_the_dossier_not_from_the_analysts_claim(tmp_path):
    d = dossier_for(tmp_path)
    th = {"game_id": GAME, "evidence_ids": ["TM:AAA:proe"], "evidence": {"measured": [{"claim": "trust me", "opponent_adjusted": True}]}}
    measured, _sim, problems = SB.resolve_thesis_evidence(th, d)
    cited = next(m for m in measured if m.get("id") == "TM:AAA:proe")
    assert cited["opponent_adjusted"] is False and not problems       # the dossier says raw; the analyst cannot overrule it
    assert next(m for m in measured if m.get("uncited"))["opponent_adjusted"] is None


# ---------------------------------------------------------------- ladders
def _ladder_rows(medians=(3.5, 4.5, 5.5, 6.5, 7.5), probs=(0.85, 0.65, 0.45, 0.27, 0.12)):
    return [{"ticker": f"T{k}", "family": "PLAYER_STAT", "period": "FULL", "subject": "P One", "stat": "receptions", "operator": ">=", "threshold": k, "mid": p,
             "yes_bid": round(p - 0.01, 2), "yes_ask": round(p + 0.01, 2), "no_bid": round(1 - p - 0.01, 2), "no_ask": round(1 - p + 0.01, 2), "width": 0.02,
             "executable": True, "no_real_market": False, "volume": 100, "yes_meaning": f"P One {k}+ receptions", "subject_kind": "player"}
            for k, p in zip(medians, probs)]


def test_ladder_shift_gives_a_consistent_range_on_every_rung():
    rows = _ladder_rows()
    lad = LF.build_ladders(rows)[LF.ladder_key(rows[0])]
    up = LF.fair_range_for_row(rows[2], lad, (0.8, 1.2))     # +1 reception: P(X>=5.5) rises toward the 4.5 rung's price
    assert up["state"] == "DERIVED" and up["p_low"] < 0.65 - 0.0 and up["p_high"] > 0.45 and up["p_central"] > 0.45
    assert up["buffer"] == LF.BUFFER_PLAYER


def test_ladder_does_not_extrapolate_past_its_priced_range():
    rows = _ladder_rows()
    lad = LF.build_ladders(rows)[LF.ladder_key(rows[0])]
    assert LF.fair_range_for_row(rows[-1], lad, (-2.0, -1.0))["state"] == "NOT_DERIVABLE"


def test_a_ladder_with_fewer_than_three_rungs_is_not_derivable():
    rows = _ladder_rows()[:2]
    lad = LF.build_ladders(rows)[LF.ladder_key(rows[0])]
    assert LF.fair_range_for_row(rows[0], lad, (0.0, 1.0))["state"] == "NOT_DERIVABLE"


def test_isotonic_fit_removes_inverted_rungs():
    rows = _ladder_rows(probs=(0.85, 0.50, 0.60, 0.27, 0.12))
    lad = LF.build_ladders(rows)[LF.ladder_key(rows[0])]
    assert all(lad.s[i] >= lad.s[i + 1] - 1e-12 for i in range(len(lad.s) - 1))


def test_script_summary_marks_single_script_dependence():
    s = LF.script_summary({"FAVORITE_CONTROL": "WIN", "COMPETITIVE": "LOSE", "UNDERDOG_CONTROL": "LOSE"})
    assert s["single_script_dependent"] is True and s["winning_scripts"] == 3
    s2 = LF.script_summary({"FAVORITE_CONTROL": "WIN", "COMPETITIVE": "WIN", "UNDERDOG_CONTROL": "MIXED"})
    assert s2["single_script_dependent"] is False and s2["winning_scripts"] == 7


def test_scan_ladders_prices_both_sides_and_carries_the_thesis():
    from nfl_edge.handicap import expression as EX
    from nfl_edge.execution.fees import load_fee_schedule
    rows = _ladder_rows()
    ev = EX.scan_ladders(rows, [{"selector": {"family": "PLAYER_STAT", "subject": "P One", "stat": "receptions"}, "shift": [1.5, 2.5], "basis": "role",
                                 "script_results": {"FAVORITE_CONTROL": "WIN", "COMPETITIVE": "WIN", "UNDERDOG_CONTROL": "MIXED"}}],
                        load_fee_schedule(ROOT), AS_OF, "AAA", "BBB")
    assert ev and {e["side"] for e in ev} == {"YES", "NO"} and all(e["ladder_thesis"]["shift"] == [1.5, 2.5] for e in ev)
    over = [e for e in ev if e["side"] == "YES"]
    assert max(e["fair_low"] for e in over) > 0.5          # a +2 shift makes the overs materially likelier than the market has them


# ---------------------------------------------------------------- challenge
def test_c5_is_open_for_a_game_line_when_a_starting_qb_is_unresolved():
    from nfl_edge.handicap import challenge as CH
    ev = {"side": "YES", "family": "SPREAD", "scripts": {"script_neutral": True}, "net_edge_low": 0.05, "executable": True, "width": 0.02, "edge_per_sd": 0.1, "ceiling_cents": 60, "ask_cents": 50}
    th = {"challenge": {"fail_modes": ["a", "b"], "market_already_priced": "x", "matchup_check": "y"}, "evidence": {"measured": [{"claim": "c", "opponent_adjusted": True}]}}
    out = CH.challenge(th, {}, ev, [], packet_market=None, player_injury=None, quote_age_min=3, mode="LIVE", owner_open_units=0, unresolved_starters=["AAA: QB X is Questionable"])
    assert "C5" in out["open"] and not out["cleared"]
    out2 = CH.challenge(th, {}, ev, [], packet_market=None, player_injury=None, quote_age_min=3, mode="LIVE", owner_open_units=0)
    assert "C5" not in out2["open"]


# ---------------------------------------------------------------- bankroll
def _ctx(cash, mins_old, vt=BK.VALUE_TYPE):
    return json.dumps({"bankroll": cash, "observedAt": (AS_OF - timedelta(minutes=mins_old)).isoformat(), "valueType": vt})


def test_bankroll_missing_stale_wrong_type_and_ok():
    assert BK.load(AS_OF, env={})["state"] == BK.MISSING
    assert BK.load(AS_OF, env={BK.ENV_CONTEXT: _ctx(900, 45)})["state"] == BK.STALE
    assert BK.load(AS_OF, env={BK.ENV_CONTEXT: _ctx(900, 5, "PORTFOLIO_VALUE")})["state"] == BK.INVALID
    assert BK.load(AS_OF, env={BK.ENV_CONTEXT: "not json"})["state"] == BK.INVALID
    ok = BK.load(AS_OF, env={BK.ENV_CONTEXT: _ctx(900, 5)}, open_exposure_dollars=300)
    assert ok["state"] == BK.OK and ok["available_cash"] == 900 and ok["total_bankroll_estimate"] == 1200


def test_unusable_bankroll_exposes_no_amount_and_authorizes_nothing():
    b = BK.load(AS_OF, env={BK.ENV_CONTEXT: _ctx(900, 90)})
    assert b["authorizes_stakes"] is False and b["available_cash"] is None
    assert BK.stake_gate(b, [75])["authorized"] == [False]


def test_stake_gate_refuses_lines_beyond_available_cash_without_rescaling():
    b = BK.load(AS_OF, env={BK.ENV_CONTEXT: _ctx(300, 5)})
    g = BK.stake_gate(b, [150, 150, 75])
    assert g["authorized"] == [True, True, False]


def test_public_view_has_no_amounts():
    b = BK.load(AS_OF, env={BK.ENV_CONTEXT: _ctx(1234.56, 5)})
    txt = json.dumps(BK.public_view(b, [75]))
    assert "1234" not in txt and '"available_cash"' not in txt


def test_redact_public_strips_owner_positions():
    card = {"owner_open_exposure": {"state": "OK", "by_game": {"G1": 225.0}}, "games": [], "theses": [], "portfolio": {"outstanding": {"total": 225}}}
    red = C.redact_public(card)
    assert "225" not in json.dumps(red) and red["owner_open_exposure"]["games_with_open_owner_position"] == 1


# ---------------------------------------------------------------- the issue channel
def _fence(obj):
    return "text\n```json\n" + json.dumps(obj) + "\n```\n"


def test_issue_submission_comes_only_from_the_owner_and_the_last_block_wins():
    from nfl_edge.handicap import issue_submission as IS
    issue = {"user": {"login": "owner"}, "body": _fence({"submission_version": "1", "reviews": [], "theses": [], "analyst": "first"})}
    comments = [{"id": 1, "user": {"login": "stranger"}, "body": _fence({"submission_version": "1", "reviews": [], "theses": [], "analyst": "evil"})},
                {"id": 2, "user": {"login": "owner"}, "body": _fence({"submission_version": "1", "reviews": [], "theses": [], "analyst": "second"})}]
    r = IS.extract(issue, comments, "owner")
    assert r["submission"]["analyst"] == "second" and r["ignored_foreign_blocks"] == 1


def test_issue_without_an_owner_block_is_refused_with_a_reason():
    from nfl_edge.handicap import issue_submission as IS
    r = IS.extract({"user": {"login": "stranger"}, "body": _fence({"submission_version": "1"})}, [], "owner")
    assert r["submission"] is None and r["errors"]
    r2 = IS.extract({"user": {"login": "owner"}, "body": "```json\n{not json, \"submission_version\"}\n```"}, [], "owner")
    assert r2["submission"] is None and "not valid JSON" in r2["errors"][0]


def _script(name):
    import importlib.util
    spec = importlib.util.spec_from_file_location(name, os.path.join(ROOT, "scripts", *name.split("/")) + ".py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_card_from_issue_reads_paginated_comment_pages_and_refuses_a_foreign_issue(tmp_path, capsys):
    m = _script("handicap/card_from_issue")
    good = {"submission_version": "1", "analyst": "a", "packet_sha": "x", "reviews": [], "theses": []}
    issue = {"user": {"login": "owner"}, "title": "NFL CARD wk7", "body": "no block here"}
    (tmp_path / "i.json").write_text(json.dumps(issue))
    (tmp_path / "c.json").write_text(json.dumps([{"id": 1, "user": {"login": "owner"}, "body": "x"}]) + json.dumps([{"id": 2, "user": {"login": "owner"}, "body": _fence(good)}]))
    assert m.main(["--issue", str(tmp_path / "i.json"), "--comments", str(tmp_path / "c.json"), "--owner", "owner", "--out", str(tmp_path / "s.json")]) == 0
    assert json.load(open(tmp_path / "s.json"))["analyst"] == "a"
    (tmp_path / "i2.json").write_text(json.dumps({"user": {"login": "stranger"}, "title": "NFL CARD", "body": _fence(good)}))
    assert m.main(["--issue", str(tmp_path / "i2.json"), "--owner", "owner", "--out", str(tmp_path / "s2.json")]) == 4 and not (tmp_path / "s2.json").exists()
    (tmp_path / "i3.json").write_text(json.dumps({"user": {"login": "owner"}, "title": "something else", "body": _fence(good)}))
    assert m.main(["--issue", str(tmp_path / "i3.json"), "--owner", "owner", "--out", str(tmp_path / "s3.json")]) == 4


def test_pin_packet_selects_latest_artifact_or_missing(tmp_path, capsys):
    m = _script("ci/pin_packet")
    hr = tmp_path / "hr"
    (hr / "latest").mkdir(parents=True)
    (hr / "history").mkdir()
    (hr / "latest" / "packet.json").write_text(json.dumps({"packet_sha": "a" * 20}))
    (hr / "history" / "index.jsonl").write_text(json.dumps({"packet_sha": "b" * 20, "artifact_name": "run-nfl-2026-w07-123"}) + "\n")
    for sha, want in (("a" * 20, "LATEST"), ("b" * 20, "run-nfl-2026-w07-123"), ("c" * 20, "MISSING"), ("zz", "LATEST")):
        (tmp_path / "s.json").write_text(json.dumps({"packet_sha": sha}))
        m.main(["--submission", str(tmp_path / "s.json"), "--reports", str(hr)])
        assert capsys.readouterr().out.strip() == want


def test_compose_reply_covers_all_three_outcomes(tmp_path):
    m = _script("handicap/compose_card_reply")
    (tmp_path / "e.json").write_text(json.dumps({"errors": ["no block"]}))
    m.main(["--extract-rc", "4", "--run-url", "U", "--extract", str(tmp_path / "e.json"), "--out", str(tmp_path / "r.md")])
    assert "no submission was read" in open(tmp_path / "r.md").read()
    (tmp_path / "CARD.md").write_text("# card")
    m.main(["--extract-rc", "0", "--run-url", "U", "--card", str(tmp_path / "CARD.md"), "--out", str(tmp_path / "r.md")])
    assert open(tmp_path / "r.md").read().startswith("# card") and "Placed nothing" in open(tmp_path / "r.md").read()
    m.main(["--extract-rc", "0", "--card-rc", "5", "--run-url", "U", "--card", str(tmp_path / "none.md"), "--out", str(tmp_path / "r.md")])
    assert "could not be built" in open(tmp_path / "r.md").read()


def test_a_player_prop_record_carries_the_packets_availability_so_the_schema_does_not_refuse_it(tmp_path):
    from nfl_edge.handicap import schema as S
    r = build_run(tmp_path, player=True)
    g = r["packet"]["games"][0]
    tk = "KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60"
    pm = next(m for m in g["markets"] if m["ticker"] == tk)
    pm["availability_state"] = "EXPECTED_ACTIVE"
    g["data_freshness"]["context_capture"] = (AS_OF - timedelta(minutes=40)).strftime("%Y%m%dT%H%M%SZ")
    row = next(x for x in C.shard(r, GAME)["rows"] if x["ticker"] == tk)
    ev = {"ticker": tk, "side": "YES", "family": "PLAYER_STAT", "fair_low": 0.5, "fair_high": 0.6, "fair_mid": 0.55, "ceiling_cents": 60, "fair_basis": "t"}
    rec = C.candidate_record(run=r, game=g, row=row, ev=ev, thesis=thesis(), units=1, as_of=AS_OF, challenge={}, mode=C.LIVE)
    assert rec["availability_state"] == "EXPECTED_ACTIVE" and rec["availability_as_of"] and 39 < rec["availability_stale_minutes"] < 41
    try:
        S.validate_recommendation(rec)
    except S.ValidationError as e:
        assert "availability" not in str(e), e          # any other refusal is not about availability
    pm["availability_state"] = None
    rec2 = C.candidate_record(run=r, game=g, row=row, ev=ev, thesis=thesis(), units=1, as_of=AS_OF, challenge={}, mode=C.LIVE)
    with pytest.raises(S.ValidationError, match="availability_state"):                   # unknown availability is refused, not guessed
        S.validate_recommendation(rec2)
