"""RUN NFL card: every game accounted for, PASS is real, stakes are 1U-5U of $75, and nothing is invented."""
import json
import os
from datetime import timedelta

import pytest

from nfl_edge.handicap import card as C
from nfl_edge.handicap import schema as S
from card_fixtures import AS_OF, GAME, KICK, build_run, schedule_text, thesis

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
pytestmark = pytest.mark.owner_policy        # the card uses the REAL owner policy


def run(tmp_path, theses, mode=C.REHEARSAL, **kw):
    r = build_run(tmp_path, **{k: v for k, v in kw.items() if k in ("cap_age_min", "kick", "invariants_ok", "player")})
    return C.run_card(run=r, theses=theses, schedule_text=schedule_text(), root=ROOT, as_of=AS_OF, mode=mode, draws=20000)


def test_no_thesis_means_an_explicit_triaged_pass_never_a_silent_omission(tmp_path):
    card = run(tmp_path, [])
    assert [g["state"] for g in card["games"]] == [C.G_NO_THESIS] and card["lines"] == []
    assert "PASS, not an omission" in card["games"][0]["state_reason"]


def test_a_game_that_has_started_is_excluded_with_a_reason(tmp_path):
    card = run(tmp_path, [thesis()], kick=AS_OF - timedelta(minutes=1))
    assert card["games"][0]["state"] == C.G_POST and card["lines"] == []
    assert card["theses"][0]["outcome"] == "EXCLUDED"


def test_a_thesis_with_no_shift_manufactures_no_edge(tmp_path):
    card = run(tmp_path, [thesis(shift_margin=(0.0, 0.0), shift_total=(0.0, 0.0))])
    assert card["lines"] == [] and card["games"][0]["state"] == C.G_REVIEWED_PASS
    assert card["theses"][0]["n_clearing_floor"] == 0


def test_a_large_defensible_shift_produces_a_correctly_formed_line(tmp_path):
    card = run(tmp_path, [thesis()])
    assert len(card["lines"]) == 1
    ln = card["lines"][0]
    assert ln["stake_units"] in (1, 2, 3, 4, 5) and ln["stake_dollars"] == ln["stake_units"] * 75 and ln["stake_units"] <= 5
    assert ln["current_price_cents"] <= ln["bet_up_to_cents"] and ln["side"] in ("YES", "NO")
    assert ln["status"].startswith("REHEARSAL") and "settles" in ln and ln["ticker"].startswith("KXNFL")
    assert card["games"][0]["state"] == C.G_BET


def test_without_independent_corroboration_the_stake_never_exceeds_2U_and_says_why(tmp_path):
    card = run(tmp_path, [thesis()])
    assert card["lines"][0]["stake_units"] <= 2 and "Why not more" in C.render_markdown(card)
    huge = run(tmp_path / "h", [thesis(shift_margin=(8.0, 9.0))])
    assert all(l["stake_units"] <= 2 for l in huge["lines"]), "a larger shift alone must not buy a larger stake"


def test_the_candidate_record_validates_and_carries_the_side_probability(tmp_path):
    card = run(tmp_path, [thesis()])
    rec = card["theses"][0]["selected"]["record"]
    rec = dict(rec, test_only=False)
    S.validate_recommendation(rec)
    ev = card["theses"][0]["selected"]["evaluation"]
    assert rec["probability_low"] == round(ev["fair_low"], 4) and rec["support_state"] == S.SUPPORT_QUALITATIVE_ONLY
    assert rec["bet_up_to_probability"] * 100 == ev["ceiling_cents"] and rec["recommended_stake"] == card["lines"][0]["stake_dollars"]
    assert rec["recommendation_id"].startswith("rec_")


def test_recommendation_ids_are_deterministic(tmp_path):
    a = run(tmp_path / "a", [thesis()])
    b = run(tmp_path / "b", [thesis()])
    assert a["lines"][0]["recommendation_id"] == b["lines"][0]["recommendation_id"]
    assert C.rec_id("p", "t", "T", "YES") != C.rec_id("p", "t", "T", "NO")


def test_an_open_challenge_item_means_pass(tmp_path):
    t = thesis()
    t["challenge"]["fail_modes"] = ["only one"]
    card = run(tmp_path, [t])
    assert card["lines"] == [] and "C1" in " ".join(card["theses"][0]["pass_reasons"])


def test_unadjusted_evidence_fails_the_challenge(tmp_path):
    t = thesis()
    t["evidence"]["measured"] = [{"claim": "raw yards per play", "opponent_adjusted": False}]
    card = run(tmp_path, [t])
    assert card["lines"] == [] and "C4" in " ".join(card["theses"][0]["pass_reasons"])


def test_a_thesis_blocked_by_data_is_an_explicit_pass_with_the_reason(tmp_path):
    card = run(tmp_path, [thesis(blocked_reason="starting quarterback sources conflict")])
    assert card["lines"] == [] and "quarterback sources conflict" in card["games"][0]["state_reason"]


def test_live_mode_fails_closed_on_a_stale_capture(tmp_path):
    card = run(tmp_path, [thesis()], mode=C.LIVE, cap_age_min=40.0)
    assert card["blocked"] and card["lines"] == [] and card["games"][0]["state"] == C.G_BLOCKED
    assert "minutes old" in card["blocked"]


def test_rehearsal_reports_the_same_staleness_as_a_warning_not_an_approval(tmp_path):
    card = run(tmp_path, [thesis()], mode=C.REHEARSAL, cap_age_min=40.0)
    assert card["data_gate"]["status"] == "REHEARSAL_STALE_ALLOWED" and card["lines"][0]["status"].startswith("REHEARSAL")


def test_a_broken_coverage_invariant_blocks_the_card(tmp_path):
    card = run(tmp_path, [thesis()], invariants_ok=False)
    assert card["blocked"] and "invariant" in card["blocked"]


def test_live_without_market_data_is_a_candidate_not_a_bet(tmp_path):
    card = run(tmp_path, [thesis()], mode=C.LIVE)
    assert card["lines"] and card["lines"][0]["status"].startswith("CANDIDATE") and "preflight not run" in card["lines"][0]["status"]


def test_a_player_prop_without_a_declared_fair_range_is_not_rankable(tmp_path):
    t = thesis(candidates=[{"ticker": "KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60", "side": "YES"}], shift=None)
    card = run(tmp_path, [t], player=True)
    assert card["lines"] == []
    rej = card["theses"][0]["rejected"]
    assert any("no defensible fair-value estimate" in r["reason"] for r in rej)


def test_a_declared_prop_range_is_recorded_as_the_analysts_not_a_model(tmp_path):
    t = thesis(shift=None, candidates=[{"ticker": "KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60", "side": "YES",
                                        "fair": {"low": 0.70, "high": 0.80, "basis": "target share 29% over four games with the WR2 out"},
                                        "winning_scripts": 5, "major_scripts": 6}],
               usage={"projected_opportunity": "8 targets", "recent_usage": "9.5/g", "role_stability": "WR1", "teammate_context": "WR2 out"})
    card = run(tmp_path, [t], player=True)
    ev = card["theses"][0]["top_ranked"][0]
    assert ev["fair_basis"].startswith("ANALYST_DECLARED")


def test_every_game_ends_in_exactly_one_terminal_state(tmp_path):
    card = run(tmp_path, [thesis()])
    assert all(g["state"] in (C.G_POST, C.G_BET, C.G_REVIEWED_PASS, C.G_NO_THESIS, C.G_BLOCKED) for g in card["games"])


def test_the_markdown_card_has_the_required_columns_and_exact_semantics(tmp_path):
    md = C.render_markdown(run(tmp_path, [thesis()]))
    assert "| Game | Bet | Current price | Bet up to | Stake | Reason |" in md
    assert "BUY YES" in md or "BUY NO" in md
    assert "settles: YES pays if" in md and "REHEARSAL" in md and "1U = $75" in md


def test_nothing_in_the_card_modules_can_place_an_order():
    for rel in ("nfl_edge/handicap/card.py", "nfl_edge/handicap/expression.py", "nfl_edge/handicap/challenge.py", "nfl_edge/handicap/staking.py",
                "nfl_edge/handicap/fairvalue.py", "nfl_edge/handicap/dossier.py", "scripts/handicap/run_card.py"):
        src = open(os.path.join(ROOT, rel)).read()
        for forbidden in ("create_order", "place_order", "cancel_order", "portfolio/orders", "Authorization", "KALSHI_API_KEY"):
            assert forbidden not in src, f"{rel} mentions {forbidden}"


# ---- the real preflight on a live card --------------------------------------------------------------------------------------

def _capture_for(tmp_path, row, side):
    """A minimal REAL capture tree (manifest + quotes + books + a clean fee observation) for one ticker, 3 minutes before AS_OF."""
    when = AS_OF - timedelta(minutes=3)
    rid = when.strftime("%Y%m%dT%H%M%SZ")
    md = tmp_path / "md"
    day = md / "data" / "kalshi" / "capture" / when.strftime("%Y-%m-%d")
    day.mkdir(parents=True, exist_ok=True)
    series = row["ticker"].split("-")[0]
    (day / f"{rid}.manifest.json").write_text(json.dumps({"run_id": rid, "started_at": when.isoformat(), "finished_at": when.isoformat(),
                                                          "series": {series: {"n": 40, "complete": True, "tier": "FULL", "observed_at": when.isoformat()}}, "partial": False}))
    (day / f"{rid}.quotes.jsonl").write_text(json.dumps({"ticker": row["ticker"], "series_ticker": series, "observed_at": when.isoformat(), "status": "active",
                                                          "yes_bid": row["yes_bid"], "yes_ask": row["yes_ask"], "no_bid": row["no_bid"], "no_ask": row["no_ask"]}) + "\n")
    ask = row["yes_ask"] if side == "YES" else row["no_ask"]
    levels = {"no_dollars": [[f"{1 - ask:.4f}", "100000"]], "yes_dollars": [["0.5000", "10"]]} if side == "YES" else \
             {"yes_dollars": [[f"{1 - ask:.4f}", "100000"]], "no_dollars": [["0.5000", "10"]]}
    (day / f"{rid}.books.jsonl").write_text(json.dumps({"run_id": rid, "observed_at": when.isoformat(), "ticker": row["ticker"], "orderbook_fp": levels}) + "\n")
    fees = md / "data" / "kalshi" / "fees"
    fees.mkdir(parents=True, exist_ok=True)
    (fees / "clean.json").write_text(json.dumps({"retrieved_at": (AS_OF - timedelta(days=1)).isoformat(), "differences": [], "errors": {},
                                                 "fee_changes": {"parsed": True, "changes": []}, "series": {}}))
    return str(md)


def test_live_card_runs_the_real_preflight_and_only_an_approved_line_is_a_bet(tmp_path):
    first = run(tmp_path / "a", [thesis()], mode=C.LIVE)
    ln = first["lines"][0]
    row = next(r for r in json.load(open(tmp_path / "a" / "analysis" / "games" / f"{GAME}.json"))["rows"] if r["ticker"] == ln["ticker"])
    md = _capture_for(tmp_path, row, ln["side"])
    ledger = tmp_path / "ledger"
    (ledger / "data").mkdir(parents=True)
    r = build_run(tmp_path / "a")
    from nfl_edge.handicap import bankroll as BK
    bk = BK.load(AS_OF, env={BK.ENV_CONTEXT: json.dumps({"bankroll": 5000, "observedAt": (AS_OF - timedelta(minutes=5)).isoformat(), "valueType": BK.VALUE_TYPE})})
    card = C.run_card(run=r, theses=[thesis()], schedule_text=schedule_text(), root=ROOT, as_of=AS_OF, mode=C.LIVE, market_data_root=md, handicap_root=str(ledger),
                      draws=20000, bankroll=bk)
    line = card["lines"][0]
    assert line["preflight"]["verdict"] == "APPROVED", line["preflight"]
    assert line["status"] == "BET (preflight approved)" and line["stake_dollars"] == line["stake_units"] * 75
    assert line["preflight"]["may_be_shown_as_a_bet"] is True
    # the same approved line with NO bankroll evidence is a CANDIDATE: stake authorization fails closed, the price work is still shown
    card2 = C.run_card(run=build_run(tmp_path / "a"), theses=[thesis()], schedule_text=schedule_text(), root=ROOT, as_of=AS_OF, mode=C.LIVE, market_data_root=md,
                       handicap_root=str(ledger), draws=20000, bankroll=BK.load(AS_OF, env={}))
    l2 = card2["lines"][0]
    assert l2["preflight"]["verdict"] == "APPROVED" and l2["status"].startswith("CANDIDATE") and "NO STAKE AUTHORIZATION" in l2["status"]
    assert card2["bankroll"]["authorizes_stakes"] is False


def test_live_card_blocks_a_line_when_the_live_book_has_moved_above_the_ceiling(tmp_path):
    first = run(tmp_path / "a", [thesis()], mode=C.LIVE)
    ln = first["lines"][0]
    row = dict(next(r for r in json.load(open(tmp_path / "a" / "analysis" / "games" / f"{GAME}.json"))["rows"] if r["ticker"] == ln["ticker"]))
    # the live capture now asks 15c higher than the packet did
    if ln["side"] == "YES":
        row["yes_ask"] = round(row["yes_ask"] + 0.15, 2)
    else:
        row["no_ask"] = round(row["no_ask"] + 0.15, 2)
    md = _capture_for(tmp_path, row, ln["side"])
    ledger = tmp_path / "ledger"
    (ledger / "data").mkdir(parents=True)
    r = build_run(tmp_path / "a")
    card = C.run_card(run=r, theses=[thesis()], schedule_text=schedule_text(), root=ROOT, as_of=AS_OF, mode=C.LIVE, market_data_root=md, handicap_root=str(ledger), draws=20000)
    line = card["lines"][0]
    assert line["preflight"]["verdict"] == "BLOCKED" and line["status"] == "BLOCKED" and line["preflight"]["may_be_shown_as_a_bet"] is False
    assert card["games"][0]["state"] == C.G_REVIEWED_PASS


def test_a_declined_thesis_leaves_a_valid_immutable_pass_record_on_its_closest_contract(tmp_path):
    card = run(tmp_path, [thesis(shift_margin=(0.0, 0.0), shift_total=(0.0, 0.0))])
    assert card["lines"] == []
    pr = card["theses"][0]["pass_record"]
    S.validate_recommendation(dict(pr, test_only=False))
    assert pr["decision"] == S.PASS and pr["primary_thesis"].startswith(f"[{GAME}::T1] PASS") and pr["recommendation_id"].startswith("rec_")
    again = run(tmp_path / "again", [thesis(shift_margin=(0.0, 0.0), shift_total=(0.0, 0.0))])
    assert again["theses"][0]["pass_record"]["recommendation_id"] == pr["recommendation_id"]


def test_a_declared_range_is_the_probability_the_side_bought_wins():
    from nfl_edge.handicap import expression as EX
    row = {"ticker": "KXNFLRECYDS-26OCT25AAABBB-AAAWR1-60", "family": "PLAYER_STAT", "subject": "A Receiver", "threshold": 60.0, "period": "FULL", "yes_ask": 0.55,
           "yes_bid": 0.53, "no_ask": 0.47, "no_bid": 0.45, "mid": 0.54, "width": 0.02, "executable": True, "yes_meaning": "YES iff A Receiver receiving_yards (FULL) >= 60.0", "stat": "receiving_yards"}
    # buying NO with a declared 60-70% chance that NO wins  =>  YES axis 30-40%
    fy = {"state": "DECLARED", "p_low": round(1 - 0.70, 4), "p_high": round(1 - 0.60, 4), "basis": "x"}
    e = EX.evaluate_contract(row, "NO", fy, __import__("nfl_edge.execution.fees", fromlist=["x"]).load_fee_schedule(ROOT), AS_OF, "BBB", "AAA")
    assert (e["fair_low"], e["fair_high"]) == (0.60, 0.70) and e["ask"] == 0.47


# ---- the LIVE path: each finalist is fetched from the venue just before the real gates ------------------------------------

def _live_client(row, side, *, shift=0.0, seconds_old=20):
    from preflight_fakes import FakeKalshiClient

    class Both(FakeKalshiClient):
        def orderbook(self, ticker, depth=None):
            body = super().orderbook(ticker, depth)
            ask = self.ask
            body["orderbook_fp"] = {"no_dollars": [[f"{1 - ask:.4f}", "100000"]], "yes_dollars": [[f"{ask:.4f}", "100000"]]}
            return body

    return Both(ask=min(0.98, max(0.02, row["yes_ask"] + shift)), retrieved_at=AS_OF - timedelta(seconds=seconds_old))


def _live_card(tmp_path, shift=0.0, **kw):
    from nfl_edge.handicap import bankroll as BK
    first = run(tmp_path / "a", [thesis()], mode=C.LIVE)
    ln = first["lines"][0]
    row = next(r for r in json.load(open(tmp_path / "a" / "analysis" / "games" / f"{GAME}.json"))["rows"] if r["ticker"] == ln["ticker"])
    md = _capture_for(tmp_path, row, ln["side"])
    ledger = tmp_path / "ledger"
    (ledger / "data").mkdir(parents=True)
    bk = BK.load(AS_OF, env={BK.ENV_CONTEXT: json.dumps({"bankroll": 5000, "observedAt": (AS_OF - timedelta(minutes=5)).isoformat(), "valueType": BK.VALUE_TYPE})})
    card = C.run_card(run=build_run(tmp_path / "a"), theses=[thesis()], schedule_text=schedule_text(), root=ROOT, as_of=AS_OF, mode=C.LIVE, handicap_root=str(ledger),
                      draws=20000, bankroll=bk, live_client=_live_client(row, ln["side"], shift=shift), fee_observations_root=md, clock=lambda: AS_OF, **kw)
    return card, ln, row


def test_live_evidence_path_fetches_the_venue_and_a_matching_quote_is_a_bet(tmp_path):
    card, ln, row = _live_card(tmp_path)
    line = card["lines"][0]
    assert line["preflight"]["evidence"] == "LIVE_TICKER_FETCH" and line["preflight"]["verdict"] == "APPROVED", line["preflight"]
    assert line["status"] == "BET (preflight approved)"
    assert card.get("_live_evidence") and card["_live_evidence"][0]["market_ticker"] == ln["ticker"]


def test_live_evidence_path_withdraws_a_line_when_the_venue_has_moved_more_than_the_tolerance(tmp_path):
    # YES asks up 6c or NO asks down 6c: either way the live ask is 6c from the priced ask
    card, ln, row = _live_card(tmp_path, shift=0.06)
    line = card["lines"][0]
    assert line["status"] == "BLOCKED" and any("REQUOTE" in r or "ceiling" in r.lower() or "above" in r.lower() for r in line["preflight"]["blocking_reasons"]), line["preflight"]


def test_a_stale_packet_with_live_requoting_warns_instead_of_blocking_the_whole_slate(tmp_path):
    r = build_run(tmp_path / "s", cap_age_min=45)
    stale_no_live = C.run_card(run=r, theses=[thesis()], schedule_text=schedule_text(), root=ROOT, as_of=AS_OF, mode=C.LIVE, draws=20000)
    assert stale_no_live["data_gate"]["status"] == "BLOCKED"
    from preflight_fakes import FakeKalshiClient
    r2 = build_run(tmp_path / "s2", cap_age_min=45)
    live = C.run_card(run=r2, theses=[thesis()], schedule_text=schedule_text(), root=ROOT, as_of=AS_OF, mode=C.LIVE, draws=20000, live_client=FakeKalshiClient())
    assert live["data_gate"]["status"] != "BLOCKED" and any("re-quoted" in w for w in live["data_gate"]["warnings"])
    c9 = [i for t in live["theses"] for i in ((t.get("selected") or {}).get("challenge") or {}).get("items", []) if i["id"] == "C9"]
    assert all(i["status"] in ("FLAG", "CLEAR") for i in c9)
