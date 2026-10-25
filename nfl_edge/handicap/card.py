"""RUN NFL: from the full-slate packet to a phone-readable card, with every game accounted for and PASS as a first-class outcome.

    Step A  discovery        every game in the packet, started games excluded WITH a reason; coverage invariants checked, fail closed
    Step B  deep review      a dossier per game (measured / simulation / unavailable), triage ORDERS review, never removes a game
    Step C  theses           analyst theses (nfl_edge/handicap/thesis_schema in docs/NFL_OPERATING_POLICY.md); a game with none is TRIAGED_NO_THESIS
    Step D  scripts          nine scripts from the SAME draws as the fair value, with the contract's result in each
    Step E  expression       every derivable full-game contract, both sides, plus declared contracts, ranked on one footing
    Step F  challenge        ten questions; OPEN or FAIL means PASS
    Step G  staking          evidence ladder (1U-5U) -> risk policy (game / correlation group / slate caps) -> preflight when evidence is present
    Step H  card             Game | Bet | Current Price | Bet Up To | Stake | Reason, then everything not bet and why

The card READS and COMPUTES. It places nothing, writes nothing to Kalshi, and writes nothing to the ledger unless the caller runs the
separate write step. A line is only called a BET when the real preflight (`preflight.preflight_batch`) approved it; without market-data
evidence it is a CANDIDATE and says so. In REHEARSAL mode (an old snapshot replayed as of its own capture time) nothing is executable.
"""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timedelta, timezone

from nfl_edge.handicap import bankroll as BK
from nfl_edge.handicap import challenge as CH
from nfl_edge.handicap import dossier as DS
from nfl_edge.handicap import expression as EX
from nfl_edge.handicap import fairvalue as FV
from nfl_edge.handicap import risk as R
from nfl_edge.handicap import schedule_kickoffs as SK
from nfl_edge.handicap import schema as S
from nfl_edge.handicap import staking as ST
from nfl_edge.handicap import submission as SB

CARD_VERSION = "card-2.0.0"
LIVE, REHEARSAL = "LIVE", "REHEARSAL"
UNIT = ST.UNIT_DOLLARS
MAX_CAPTURE_AGE_MIN = 15.0
MAX_PINNED_PACKET_AGE_H = 12.0   # LIVE with a live venue fetch: the packet supplies the market CENTRE the analyst read; every finalist is re-quoted from the venue
REQUOTE_TOLERANCE = 0.03          # the live ask may differ from the priced ask by at most this before the line is withdrawn (the ceiling already guards the other side)
UNITS_TO_GRADE = {1: "B-", 2: "B", 3: "A-", 4: "A", 5: "A+"}      # each grade's cap in config/risk_policy.json is exactly that many units
ELIG_KEY = {"GAME_WINNER": "game_winner", "SPREAD": "spread", "TOTAL": "total", "TEAM_TOTAL": "team_total", "BOTH_TEAMS_SCORE_N": "both_teams_score"}

# game states (terminal; every packet game ends in exactly one)
G_POST = "POST_KICKOFF_EXCLUDED"
G_BET = "BET"
G_REVIEWED_PASS = "DEEP_REVIEWED_PASS"
G_NO_THESIS = "TRIAGED_NO_THESIS"
G_BLOCKED = "BLOCKED"


def _ts(v):
    if not v:
        return None
    d = datetime.fromisoformat(str(v).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def C_ts(v):
    return _ts(v)


def _cents(p):
    return None if p is None else f"{round(p * 100)}¢"


# ------------------------------------------------------------------------------------------------ Step A

def load_reports(reports_dir: str) -> dict:
    """The `handicap-reports/latest` tree: packet.json, analysis/manifest.json and the analysis shards (loaded lazily)."""
    with open(os.path.join(reports_dir, "packet.json")) as f:
        packet = json.load(f)
    with open(os.path.join(reports_dir, "analysis", "manifest.json")) as f:
        manifest = json.load(f)
    return {"dir": reports_dir, "packet": packet, "manifest": manifest, "_shards": {}}


def shard(run: dict, game_id: str) -> dict:
    if game_id not in run["_shards"]:
        with open(os.path.join(run["dir"], "analysis", "games", f"{game_id}.json")) as f:
            run["_shards"][game_id] = json.load(f)
    return run["_shards"][game_id]


def data_gate(run: dict, as_of: datetime, mode: str, live_requote: bool = False) -> dict:
    """Coverage and freshness. LIVE fails closed; REHEARSAL reports the same findings but is measured at the snapshot's own clock."""
    pk, mf = run["packet"], run["manifest"]
    reasons, warns = [], []
    inv = mf.get("invariants") or {}
    for k in ("rows_total_equals_packet_markets_listed", "no_duplicate_tickers", "zero_silently_omitted"):
        if inv.get(k) is not True:
            reasons.append(f"coverage invariant {k} is not true")
    cap = _ts(((pk.get("games") or [{}])[0].get("data_freshness") or {}).get("ledger_feature_cutoff"))
    built = _ts(pk.get("built_at"))
    age = None if cap is None else (as_of - cap).total_seconds() / 60.0
    if cap is None:
        reasons.append("no capture timestamp on the packet: freshness cannot be established")
    elif live_requote and mode == LIVE and age > MAX_CAPTURE_AGE_MIN:
        if age / 60.0 > MAX_PINNED_PACKET_AGE_H:
            reasons.append(f"packet capture is {age / 60:.1f} h old (limit {MAX_PINNED_PACKET_AGE_H:g} h even with live re-quoting): rebuild the packet and re-read it")
        else:
            warns.append(f"packet capture is {age:.0f} minutes old: prices and the market centre are from the packet the analyst read; every finalist is re-quoted from the venue "
                         f"and withdrawn if the live ask is more than {REQUOTE_TOLERANCE * 100:.0f}c from the priced ask or above the bet-up-to ceiling")
    elif age > MAX_CAPTURE_AGE_MIN:
        (warns if mode == REHEARSAL else reasons).append(f"capture is {age:.0f} minutes old at {as_of.isoformat()} (limit {MAX_CAPTURE_AGE_MIN:.0f})")
    if pk.get("real_money_status") is None:
        warns.append("packet carries no real_money_status")
    return {"status": "BLOCKED" if reasons else (("LIVE_AGED_PACKET_REQUOTING" if mode == LIVE else "REHEARSAL_STALE_ALLOWED") if warns else "OK"), "reasons": reasons, "warnings": warns,
            "capture_time": cap.isoformat() if cap else None, "capture_age_minutes": None if age is None else round(age, 1),
            "packet_built_at": built.isoformat() if built else None, "packet_sha": pk.get("packet_sha"),
            "coverage": {"games": len(pk.get("games", [])), "rows_total": (mf.get("counts") or {}).get("rows_total"),
                         "silently_omitted": ((mf.get("coverage_matrix") or {}).get("totals") or {}).get("silently_omitted")}}


# ------------------------------------------------------------------------------------------------ owner exposure

def owner_open_exposure(handicap_root: str | None, schedule_text: str, season: int) -> dict:
    """Dollars staked on UNSETTLED owner positions per game_id (conservative: gross stake of unsettled buy orders)."""
    if not handicap_root:
        return {"state": "UNAVAILABLE", "by_game": {}}
    from nfl_edge.handicap import position_lifecycle as PL
    from nfl_edge.handicap import store
    wagers = store.read_kind(handicap_root, "imported_wagers", season=season)
    settled = {s.get("source_bet_key") for s in store.read_kind(handicap_root, "wager_settlements", season=season) if s.get("settlement_status") == "SETTLED"}
    ids = SK.game_ids_from_schedule(schedule_text, season)
    by: dict = {}
    for w in wagers:
        if w.get("source_bet_key") in settled or w.get("execution_action") == "SELL":
            continue
        gk = SK.game_key_from_ticker_key(PL.game_key(w.get("market_ticker")))
        gid = ids.get(gk)
        if gid:
            by[gid] = by.get(gid, 0.0) + float(w.get("stake") or 0.0)
    return {"state": "OK", "by_game": {k: round(v, 2) for k, v in by.items()}}


# ------------------------------------------------------------------------------------------------ records

def rec_id(packet_sha, thesis_id, ticker, side) -> str:
    """Deterministic and immutable: the same packet, thesis, contract and side always give the same identifier."""
    return "rec_" + hashlib.sha1(f"{packet_sha}|{thesis_id}|{ticker}|{side}".encode()).hexdigest()[:20]


def candidate_record(*, run: dict, game: dict, row: dict, ev: dict, thesis: dict, units: int, as_of: datetime, challenge: dict, mode: str) -> dict:
    pk = run["packet"]
    cap = _ts(game["data_freshness"]["ledger_feature_cutoff"])
    ko = _ts(game["kickoff_utc"])
    side = ev["side"]
    fl, fh = ev["fair_low"], ev["fair_high"]
    supports = [m.get("claim") for m in (thesis.get("evidence") or {}).get("measured", [])][:6]
    cps = (thesis.get("challenge") or {}).get("fail_modes") or []
    unc = (thesis.get("challenge") or {}).get("uncertainties") or ["fair value is a range conditioned on the thesis shift; see fair_basis"]
    rec = {
        "recommendation_id": rec_id(pk.get("packet_sha"), thesis["thesis_id"], ev["ticker"], side), "schema_version": S.HANDICAP_SCHEMA_VERSION,
        "created_at": as_of.isoformat(), "handicap_run_id": pk.get("handicap_run_id"), "packet_sha": pk.get("packet_sha"),
        "season": game["season"], "week": game["week"], "game_id": game["game_id"], "kickoff_utc": game["kickoff_utc"],
        "market_ticker": ev["ticker"], "market_family": ev["family"], "side": side, "threshold": row.get("threshold"),
        "player_name": row.get("subject") if ev["family"] == "PLAYER_STAT" else None,
        "yes_bid": row.get("yes_bid"), "yes_ask": row.get("yes_ask"), "no_bid": row.get("no_bid"), "no_ask": row.get("no_ask"), "mid": row.get("mid"),
        "width": row.get("width"), "volume": row.get("volume"), "open_interest": row.get("open_interest"),
        "market_timestamp": cap.isoformat(), "minutes_to_kickoff": round((ko - as_of).total_seconds() / 60.0, 1),
        "support_state": S.SUPPORT_QUALITATIVE_ONLY,
        "support_reason": "fair value is the analyst's thesis range (" + str(ev.get("fair_basis")) + "); no validated model prices this contract",
        "probability_low": round(fl, 4), "probability_mid": round(ev["fair_mid"], 4), "probability_high": round(fh, 4),
        "bet_up_to_probability": (ev["ceiling_cents"] or 0) / 100.0, "grade": UNITS_TO_GRADE[units],
        "proposed_stake": units * UNIT, "recommended_stake": units * UNIT, "bankroll_snapshot": None, "decision": S.RECOMMENDED,
        "primary_thesis": f"[{thesis['thesis_id']}] {thesis.get('statement', '')}",
        "key_supporting_factors": supports or ["see thesis"], "counterarguments": cps, "uncertainties": unc,
        "reasoning_tags": [f"thesis:{thesis['thesis_id']}", f"mode:{mode}", f"card:{CARD_VERSION}"],
        "source_freshness": {"packet_built_at": pk.get("built_at"), "ledger_feature_cutoff": game["data_freshness"]["ledger_feature_cutoff"],
                             "context_capture": game["data_freshness"].get("context_capture")},
        "correlation_group": f"{game['game_id']}::{(thesis.get('drivers') or [thesis['thesis_id']])[0]}",
        "correlation_direction": "same", "correlation_strength": "strong (qualitative)", "test_only": mode == REHEARSAL,
    }
    if ev["family"] == "PLAYER_STAT":
        # A player prop settles on the player taking the field: the record carries the availability the packet holds for THIS contract and when that was captured.
        pm = next((m for m in game.get("markets", []) if m["ticker"] == ev["ticker"]), None) or {}
        rec["availability_state"] = pm.get("availability_state")
        cc = game["data_freshness"].get("context_capture")
        try:
            at = datetime.strptime(str(cc), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            at = None
        if at is not None:
            rec["availability_as_of"] = at.isoformat()
            rec["availability_stale_minutes"] = round((as_of - at).total_seconds() / 60.0, 1)
    return rec


def pass_record(*, run: dict, game: dict, row: dict, ev: dict, thesis: dict, as_of: datetime, reason: str, mode: str) -> dict:
    """A PASS is a first-class record: the contract that came CLOSEST to a bet for a thesis that was seriously considered and declined, with why.
    Same immutable-identifier scheme as a recommendation, so a later look can ask whether the passes would have won."""
    cap = _ts(game["data_freshness"]["ledger_feature_cutoff"])
    ko = _ts(game["kickoff_utc"])
    rec = {
        "recommendation_id": rec_id(run["packet"].get("packet_sha"), thesis["thesis_id"], ev["ticker"], ev["side"] + ":PASS"), "schema_version": S.HANDICAP_SCHEMA_VERSION,
        "created_at": as_of.isoformat(), "handicap_run_id": run["packet"].get("handicap_run_id"), "packet_sha": run["packet"].get("packet_sha"),
        "season": game["season"], "week": game["week"], "game_id": game["game_id"], "kickoff_utc": game["kickoff_utc"], "market_ticker": ev["ticker"],
        "market_family": ev["family"], "side": ev["side"], "threshold": row.get("threshold"), "yes_bid": row.get("yes_bid"), "yes_ask": row.get("yes_ask"),
        "no_bid": row.get("no_bid"), "no_ask": row.get("no_ask"), "mid": row.get("mid"), "market_timestamp": cap.isoformat(),
        "minutes_to_kickoff": round((ko - as_of).total_seconds() / 60.0, 1), "support_state": S.SUPPORT_QUALITATIVE_ONLY,
        "support_reason": "closest contract to a bet for a thesis that was declined",
        "probability_low": ev.get("fair_low"), "probability_mid": ev.get("fair_mid"), "probability_high": ev.get("fair_high"),
        "decision": S.PASS, "grade": None, "primary_thesis": f"[{thesis['thesis_id']}] PASS: {reason}",
        "reasoning_tags": [f"thesis:{thesis['thesis_id']}", f"mode:{mode}", f"card:{CARD_VERSION}"], "test_only": mode == REHEARSAL,
    }
    return rec


# ------------------------------------------------------------------------------------------------ the run

def run_card(*, run: dict, theses: list, schedule_text: str, root: str, as_of: datetime, mode: str = LIVE, handicap_root: str | None = None,
             market_data_root: str | None = None, policy: R.RiskPolicy | None = None, fee_schedule=None, replay_segments: dict | None = None,
             draws: int = FV.DEFAULT_DRAWS, submission: dict | None = None, bankroll: dict | None = None, stats=None, snaps=None,
             live_client=None, fee_observations_root: str | None = None, clock=None) -> dict:
    """`theses` is the LEGACY input (a bare list, no review records). `submission` is the analyst's reviewed submission (`submission.py`): review records for
    games plus theses; it is the only input under which a game can end DEEP-REVIEWED. `bankroll` is `bankroll.load(...)`. `live_client` (a read-only Kalshi
    client) turns the preflight into the LIVE path: each finalist's contract is fetched from the venue just before the gates run."""
    pk = run["packet"]
    season = pk["season"]
    policy = policy or R.RiskPolicy.load(root)
    gate = data_gate(run, as_of, mode, live_requote=live_client is not None)
    ref = DS.slate_reference(pk)
    bank, bank_meta = FV.bank_from_schedule(schedule_text, season)
    owner = owner_open_exposure(handicap_root, schedule_text, season)
    elig = (pk.get("production_eligibility") or {})

    games_out, dossiers = [], {}
    for g in pk["games"]:
        ko = _ts(g["kickoff_utc"])
        published = os.path.join(run["dir"], "dossiers", f"{g['game_id']}.json")
        d = None
        if submission is not None and os.path.exists(published):
            # The dossier the analyst READ is the one its evidence ids are checked against (built from this same packet by RUN NFL).
            with open(published) as f:
                d = json.load(f)
            d = d if d.get("version_v2") else None
        if d is not None:
            pass
        elif submission is not None:
            d = DS.build_dossier_v2(g, ref, DS.schedule_row(schedule_text, g["game_id"]), shard(run, g["game_id"])["rows"], stats, snaps, pk.get("week"))
        else:
            d = DS.build_dossier(g, ref, DS.schedule_row(schedule_text, g["game_id"]))
        dossiers[g["game_id"]] = d
        t = DS.triage(g, d)
        state = G_POST if ko <= as_of else None
        games_out.append({"game_id": g["game_id"], "home": g["home_team"], "away": g["away_team"], "kickoff_utc": g["kickoff_utc"], "state": state,
                          "state_reason": "kickoff has passed at the decision time; outside the pregame window" if state else None,
                          "triage": t, "theses": [], "executable_contracts": (g.get("coverage") or {}).get("totals", {}).get("executable")})
    by_id = {x["game_id"]: x for x in games_out}
    order = sorted([x for x in games_out if x["state"] is None], key=lambda x: -x["triage"]["score"])
    for i, x in enumerate(order, 1):
        x["triage_rank"] = i

    if gate["status"] == "BLOCKED":
        for x in games_out:
            x["state"] = x["state"] or G_BLOCKED
            x["state_reason"] = x["state_reason"] or "; ".join(gate["reasons"])
        return _assemble(run, mode, as_of, gate, games_out, [], [], [], dossiers, owner, policy, None, bank_meta, "BLOCKED: " + "; ".join(gate["reasons"]))

    # ---- the analyst's submission: review records decide which games are DEEPLY reviewed and which theses may be priced at all
    review_info = {}
    sub_errors, sub_warnings = [], []
    if submission is not None:
        theses = list(submission.get("theses") or [])
        sub_errors = SB.validate_structure(submission)
        if mode == LIVE and submission.get("packet_sha") != pk.get("packet_sha"):
            sub_errors.append(f"the submission was written against packet {submission.get('packet_sha')!r}, not the current packet {pk.get('packet_sha')!r}: "
                              "the analyst's shifts are relative to the market centre in the packet that was read. Re-read the current packet.")
        elif submission.get("packet_sha") != pk.get("packet_sha"):
            sub_warnings.append(f"submission packet {submission.get('packet_sha')!r} differs from the current packet {pk.get('packet_sha')!r} (allowed outside LIVE)")
        by_game_rv = {r.get("game_id"): r for r in (submission.get("reviews") or []) if isinstance(r, dict)}
        n_theses_by_game: dict = {}
        for t in theses:
            n_theses_by_game[t.get("game_id")] = n_theses_by_game.get(t.get("game_id"), 0) + 1
        for x in games_out:
            if x["state"]:
                continue
            gid, rv, d = x["game_id"], by_game_rv.get(x["game_id"]), dossiers[x["game_id"]]
            if sub_errors:
                info = {"disposition": SB.D_NOT_REVIEWED, "why": ["the submission file is invalid: " + "; ".join(sub_errors)[:300]]}
            elif rv is None:
                info = {"disposition": SB.D_NOT_REVIEWED, "why": ["no review record for this game. Scanning markets is not a review."]}
            elif rv.get("verdict") == "INSUFFICIENT_DATA":
                chk = SB.insufficient_check(rv, d)
                info = ({"disposition": SB.D_INSUFFICIENT, "why": ["; ".join(chk["missing"])], "reasoning": rv.get("reasoning")} if chk["qualifies"]
                        else {"disposition": SB.D_NOT_REVIEWED, "why": ["INSUFFICIENT_DATA claimed without the required specifics: " + "; ".join(chk["problems"])]})
            else:
                chk = SB.deep_review_check(rv, d)
                if not chk["qualifies"]:
                    info = {"disposition": SB.D_NOT_REVIEWED, "why": ["the review record does not meet the deep-review standard: " + "; ".join(chk["problems"])], "check": chk}
                elif rv.get("verdict") == "REJECTED":
                    info = {"disposition": SB.D_REJECTED, "why": [str(rv.get("reasoning"))[:400]], "check": chk, "reasoning": rv.get("reasoning"), "thesis_ready": False}
                elif not n_theses_by_game.get(gid):
                    info = {"disposition": SB.D_NOT_REVIEWED, "why": ["verdict THESIS but no thesis record was filed for this game"], "check": chk}
                else:
                    info = {"disposition": None, "check": chk, "thesis_ready": True, "reasoning": rv.get("reasoning")}
            review_info[gid] = info
            x["review"] = {k: v for k, v in info.items() if k != "check"}
            x["review"]["check_problems"] = (info.get("check") or {}).get("problems")

    def _unresolved(gid):
        d = dossiers[gid]
        return [f"{t}: QB {q.get('qb')} is {q.get('qb_status') or q.get('qb_injury')}" for t, q in (d.get("qb_pressure") or {}).items()
                if q.get("qb_status") not in (None, "Active") or q.get("qb_injury")]

    # theses -> expressions -> challenge -> stake
    accepted, thesis_reports, proposals = [], [], []
    for th in theses:
        gid = th["game_id"]
        if gid not in by_id or by_id[gid]["state"] == G_POST:
            thesis_reports.append({"thesis_id": th.get("thesis_id"), "game_id": gid, "outcome": "EXCLUDED", "reason": "game not in the unstarted slate"})
            continue
        if submission is not None:
            info = review_info.get(gid) or {}
            if not info.get("thesis_ready"):
                thesis_reports.append({"thesis_id": th.get("thesis_id"), "game_id": gid, "outcome": "NOT_PRICED", "statement": th.get("statement"),
                                       "pass_reasons": ["not priced: this game has no qualifying deep-review record with verdict THESIS (" + "; ".join(info.get("why") or ["no review"])[:300] + ")"]})
                continue
            measured, simulation, problems = SB.resolve_thesis_evidence(th, dossiers[gid])
            for ls in th.get("ladder_shifts") or []:
                for i in ls.get("evidence_ids") or []:
                    if i not in (dossiers[gid].get("evidence_index") or {}):
                        problems.append(f"ladder_shifts evidence id {i!r} is not in the dossier for {gid}")
            if problems:
                thesis_reports.append({"thesis_id": th.get("thesis_id"), "game_id": gid, "outcome": "NOT_PRICED", "statement": th.get("statement"),
                                       "pass_reasons": ["not priced: thesis cites evidence that does not resolve: " + "; ".join(problems)[:300]]})
                continue
            th = dict(th, evidence={"measured": measured, "simulation": simulation})
        rep = _evaluate_thesis(th, run, bank, as_of, mode, root, fee_schedule, owner, elig, replay_segments, policy,
                               unresolved_starters=_unresolved(gid) if submission is not None else None, live_requote=live_client is not None)
        if rep.get("outcome") == "PASS" and rep.get("top_ranked"):
            top = rep["top_ranked"][0]
            g = next(x for x in pk["games"] if x["game_id"] == gid)
            row = next((r for r in shard(run, gid)["rows"] if r["ticker"] == top["ticker"]), None)
            if row is not None and top.get("fair_low") is not None:
                rep["pass_record"] = pass_record(run=run, game=g, row=row, ev=top, thesis=th, as_of=as_of, reason="; ".join(rep["pass_reasons"])[:600], mode=mode)
        thesis_reports.append(rep)
        by_id[gid]["theses"].append(th["thesis_id"])
        if rep.get("selected"):
            sel = rep["selected"]
            proposals.append(R.Proposal(recommendation_id=sel["recommendation_id"], proposed_stake=sel["stake_units"] * UNIT, game_id=gid,
                                        correlation_group=sel["record"]["correlation_group"], grade=UNITS_TO_GRADE[sel["stake_units"]]))
            accepted.append(rep)

    # portfolio caps (with the owner's real open exposure folded in)
    outstanding = None
    if owner["state"] == "OK" and owner["by_game"]:
        outstanding = R.OutstandingExposure(by_game=dict(owner["by_game"]), total=round(sum(owner["by_game"].values()), 2),
                                            source="owner's unsettled routed wagers (handicap-data)")
    if bankroll is None and mode == LIVE and submission is not None:
        bankroll = BK.load(as_of, open_exposure_dollars=sum(owner["by_game"].values()) if owner["state"] == "OK" else None)
    bank_total = bankroll.get("total_bankroll_estimate") if (bankroll and mode == LIVE) else None
    report = policy.evaluate(proposals, bank_total, outstanding) if proposals else None
    lines = []
    for rep in accepted:
        sel = rep["selected"]
        v = report.verdict_for(sel["recommendation_id"]) if report else None
        units = int(v.approved_stake // UNIT) if (v and v.is_actionable) else 0
        sel["portfolio"] = v.to_dict() if v else None
        sel["final_units"] = units
        if units == 0:
            rep["outcome"] = "PASS"
            rep["pass_reasons"] = [f"risk policy rejected the position: {'; '.join(v.reasons) if v else 'no verdict'}"]
            sel["record"]["decision"] = S.PASS
            continue
        sel["record"]["proposed_stake"] = sel["stake_units"] * UNIT
        sel["record"]["recommended_stake"] = units * UNIT
        sel["record"]["grade"] = UNITS_TO_GRADE[units]
        lines.append(sel)
    lines.sort(key=lambda s_: (by_id[s_["game_id"]]["kickoff_utc"], s_["recommendation_id"]))

    pre = _preflight(lines, run, as_of, mode, root, market_data_root, handicap_root, policy, live_client=live_client, bank_total=bank_total,
                     fee_observations_root=fee_observations_root, clock=clock)
    live_docs = pre.pop("__evidence_docs__", None)
    for l in lines:
        pf = pre.get(l["recommendation_id"])
        if pf and pf.get("verdict") == "APPROVED" and pf.get("live_ask") is not None:
            priced = l["evaluation"]["ask_cents"] / 100.0
            if abs(float(pf["live_ask"]) - float(priced)) > REQUOTE_TOLERANCE + 1e-9:
                pf["verdict"] = "BLOCKED"
                pf["may_be_shown_as_a_bet"] = False
                pf["blocking_reasons"] = (pf.get("blocking_reasons") or []) + [
                    f"REQUOTE: the venue asks {round(float(pf['live_ask']) * 100)}c now vs {round(float(priced) * 100)}c when priced (tolerance {REQUOTE_TOLERANCE * 100:.0f}c): the market has moved since the packet was read; "
                    "re-read a fresh packet before betting"]
    # stake authorization: available cash must cover the lines the preflight approved, in kickoff order
    auth = {}
    if mode == LIVE:
        ok_lines = [l for l in lines if (pre.get(l["recommendation_id"]) or {}).get("verdict") == "APPROVED"]
        bk = bankroll or {"authorizes_stakes": False, "reasons": ["no bankroll evidence was supplied"]}
        gate_ = BK.stake_gate(bk, [(pre[l["recommendation_id"]].get("approved_stake") or l["final_units"] * UNIT) for l in ok_lines])
        for l, okk in zip(ok_lines, gate_["authorized"]):
            auth[l["recommendation_id"]] = (okk, None if okk else (gate_.get("reason") or "stake not authorized"))
    card_lines = []
    for sel in lines:
        pf = pre.get(sel["recommendation_id"])
        a_ok, a_why = auth.get(sel["recommendation_id"], (None, None))
        card_lines.append(_card_line(sel, by_id, pf, mode, authorized=a_ok, auth_reason=a_why))
        if pf and pf["verdict"] == "BLOCKED":
            by_id[sel["game_id"]]["state"] = G_REVIEWED_PASS
            by_id[sel["game_id"]]["state_reason"] = "preflight BLOCKED: " + "; ".join(pf["blocking_reasons"][:2])
    reviewed = {r["game_id"] for r in thesis_reports if r.get("outcome") != "NOT_PRICED"}
    betting = {l["game_id"] for l in card_lines if l["status"] != "BLOCKED"}
    for x in games_out:
        if x["state"]:
            if submission is not None and x["state"] == G_REVIEWED_PASS:
                x["disposition"] = SB.D_PREFLIGHT_BLOCKED if str(x.get("state_reason", "")).startswith("preflight BLOCKED") else SB.D_REJECTED
                if x["disposition"] == SB.D_PREFLIGHT_BLOCKED:
                    x["state"] = x["disposition"]
            elif submission is not None:
                x["disposition"] = x["state"]
            continue
        if submission is not None:
            info = review_info.get(x["game_id"]) or {}
            if x["game_id"] in betting:
                line = next(l for l in card_lines if l["game_id"] == x["game_id"] and l["status"] != "BLOCKED")
                x["disposition"] = SB.D_BET if line["status"].startswith("BET") else SB.D_CANDIDATE
                x["state"], x["state_reason"] = x["disposition"], "see card: " + line["status"]
            elif info.get("disposition"):
                x["disposition"], x["state"] = info["disposition"], info["disposition"]
                x["state_reason"] = "; ".join(info.get("why") or [])[:420]
            else:
                rs = [r for r in thesis_reports if r["game_id"] == x["game_id"] and r.get("outcome") != "NOT_PRICED"]
                x["disposition"] = x["state"] = SB.D_REJECTED
                x["state_reason"] = "deeply reviewed; thesis priced and not taken: " + " | ".join(
                    f"{r['thesis_id']}: {'; '.join(r.get('pass_reasons') or [r.get('reason', 'no expression cleared')])[:260]}" for r in rs)
            continue
        if x["game_id"] in betting:
            x["state"], x["state_reason"] = G_BET, "see card"
        elif x["game_id"] in reviewed:
            rs = [r for r in thesis_reports if r["game_id"] == x["game_id"]]
            x["state"] = G_REVIEWED_PASS
            x["state_reason"] = " | ".join(f"{r['thesis_id']}: {'; '.join(r.get('pass_reasons') or [r.get('reason', 'no expression cleared')])[:260]}" for r in rs)
        else:
            x["state"] = G_NO_THESIS
            x["state_reason"] = ("no analyst thesis was filed for this game; triage rank " + str(x.get("triage_rank")) +
                                 ". Absence of a thesis is a PASS, not an omission: " + ("; ".join(x["triage"]["reasons"]) or "no standout factor"))
    out = _assemble(run, mode, as_of, gate, games_out, card_lines, thesis_reports, accepted, dossiers, owner, policy, report, bank_meta, None, pre)
    out["review_coverage"] = _review_coverage(games_out, submission, sub_errors, sub_warnings)
    out["bankroll"] = None if bankroll is None else BK.public_view(bankroll, [l["stake_dollars"] for l in card_lines] or None)
    out["_bankroll_private"] = bankroll
    out["_live_evidence"] = live_docs
    return out


def _review_coverage(games_out, submission, errors, warnings) -> dict:
    counts: dict = {}
    for g in games_out:
        k = g.get("disposition") or g["state"]
        counts[k] = counts.get(k, 0) + 1
    unstarted = [g for g in games_out if g["state"] != G_POST]
    allowed = set(SB.DISPOSITIONS) | {G_BET, G_REVIEWED_PASS, G_NO_THESIS, G_BLOCKED}
    return {"submission_supplied": submission is not None, "submission_errors": errors, "submission_warnings": warnings, "counts": counts,
            "unstarted_games": len(unstarted), "every_game_has_one_terminal_disposition": all((g.get("disposition") or g["state"]) in allowed for g in games_out),
            "deeply_reviewed_games": sum(1 for g in unstarted if g.get("disposition") in (SB.D_BET, SB.D_CANDIDATE, SB.D_REJECTED)),
            "not_reviewed_games": sum(1 for g in unstarted if g.get("disposition") in (None, SB.D_NOT_REVIEWED) and submission is not None)}


def _evaluate_thesis(th, run, bank, as_of, mode, root, fee_schedule, owner, elig, replay_segments, policy, unresolved_starters=None, live_requote=False) -> dict:
    from nfl_edge.execution.fees import load_fee_schedule
    pk = run["packet"]
    game = next(g for g in pk["games"] if g["game_id"] == th["game_id"])
    sh = shard(run, th["game_id"])
    rows = {r["ticker"]: r for r in sh["rows"]}
    home, away = game["home_team"], game["away_team"]
    sched = fee_schedule or load_fee_schedule(root)
    cm = game["simulation"]["center"]
    gsim = FV.GameSim(bank, home, away, cm["spread_home"], cm["total"])
    noise = FV.baseline_check(sh["rows"], gsim.draw(0, 0), home, away)
    cap = _ts(game["data_freshness"]["ledger_feature_cutoff"])
    quote_age = (as_of - cap).total_seconds() / 60.0
    rep = {"thesis_id": th["thesis_id"], "game_id": th["game_id"], "statement": th.get("statement"), "drivers": th.get("drivers"),
           "shift": th.get("shift"), "baseline_noise": noise, "outcome": "PASS", "pass_reasons": [], "evaluations": [], "rejected": []}

    if th.get("blocked_reason"):
        # The analyst (or a data check) has already established that this game cannot be priced responsibly: an explicit PASS, with the reason.
        rep["pass_reasons"].append("PASS by thesis: " + str(th["blocked_reason"]))
        rep["n_evaluated"], rep["n_clearing_floor"] = 0, 0
        return rep
    evals = []
    if th.get("shift") and all(x is not None for x in list(th["shift"].get("home_margin") or [None]) + list(th["shift"].get("total") or [None])):
        evals += EX.scan_derivable(sh["rows"], gsim, th["shift"], noise, sched, as_of, home, away)
    else:
        th = dict(th, shift=None)
    ladder_shifts = [ls for ls in (th.get("ladder_shifts") or []) if all(isinstance(x, (int, float)) for x in (ls.get("shift") or [None]))]
    if ladder_shifts:
        evals += EX.scan_ladders(sh["rows"], ladder_shifts, sched, as_of, home, away)
        rep["ladder_shifts"] = [{"selector": ls["selector"], "shift": ls["shift"], "basis": ls.get("basis")} for ls in ladder_shifts]
    for c in th.get("candidates", []):
        r = rows.get(c["ticker"])
        if r is None:
            rep["rejected"].append({"ticker": c["ticker"], "reason": "ticker is not in this game's analysis shard (not listed / wrong game)"})
            continue
        side = c.get("side", "YES")
        fair = c.get("fair")
        if fair:
            # The declared range is the probability that the side BOUGHT wins (what a handicapper naturally states). It is stored on the YES axis.
            fy = {"state": "DECLARED", "p_low": fair["low"], "p_high": fair["high"], "basis": "ANALYST_DECLARED: " + str(fair.get("basis", ""))}
            if side == "NO":
                fy["p_low"], fy["p_high"] = round(1 - fair["high"], 4), round(1 - fair["low"], 4)
            e = EX.evaluate_contract(r, side, fy, sched, as_of, home, away)
            e["scripts"] = {"basis": "ANALYST_DECLARED", "declared": c.get("script_results"), "matrix": [], "winning_scripts": c.get("winning_scripts", 0),
                            "major_scripts": c.get("major_scripts", 0), "single_script_dependent": c.get("single_script_dependent", False), "script_neutral": False}
            evals.append(e)
        elif not th.get("shift"):
            evals.append(EX.evaluate_contract(r, side, {"state": "NONE", "reason": "no defensible fair range was supplied"}, sched, as_of, home, away))
    fams = th.get("families")
    if fams:
        evals = [e for e in evals if e["family"] in fams or e.get("fair_basis", "").startswith("ANALYST") or e.get("ladder_thesis")]
    excl = set(th.get("exclude_tickers") or [])
    evals = [e for e in evals if e["ticker"] not in excl]
    ranked = EX.rank(evals)
    rep["n_evaluated"] = len(ranked)
    rep["n_clearing_floor"] = sum(1 for e in ranked if e.get("rankable", True) and e.get("executable") and (e.get("net_edge_low") or -1) >= EX.MIN_NET_EDGE)
    best = next((e for e in ranked if e.get("executable") and (e.get("net_edge_low") or -1) >= EX.MIN_NET_EDGE), None)
    rep["top_ranked"] = [_slim(e) for e in ranked[:8]]
    # like-for-like: the best clearing expression of this thesis in EACH contract family / period (game lines vs player stats vs period markets)
    rep["by_family"] = [_slim(e) for e in EX.best_by_family(ranked)]
    rep["n_player_ladder_evals"] = sum(1 for e in ranked if e.get("ladder_thesis"))
    rep["rejected"] += [{"ticker": e["ticker"], "side": e["side"], "name": e["name"], "ask_cents": e["ask_cents"], "reason": EX.reason_rejected(e, best)}
                        for e in ranked[:40] if e is not best]
    if best is None and th.get("shift"):
        # How far from a bet is this thesis? Scale the stated ranges until something clears, so the owner can see whether the gap is a rounding error
        # or the thesis is simply too small to trade after fees. (A reading aid: the scaled shifts are NOT the analyst's and nothing is staked on them.)
        for k in (1.5, 2.0, 3.0, 4.0):
            sc = {"home_margin": [x * k for x in th["shift"]["home_margin"]], "total": [x * k for x in th["shift"]["total"]]}
            hit = [e for e in EX.rank(EX.scan_derivable(sh["rows"], gsim, sc, noise, sched, as_of, home, away))
                   if e.get("executable") and (e.get("net_edge_low") or -1) >= EX.MIN_NET_EDGE]
            if hit:
                rep["needed_scale"] = {"factor": k, "scaled_shift": sc, "first_to_clear": _slim(hit[0])}
                break
        else:
            rep["needed_scale"] = {"factor": None, "note": "nothing clears even at 4x the stated shift"}
    if best is None:
        rep["pass_reasons"].append("no contract expressing this thesis clears a 2.0c net edge at the conservative end of the fair range after fees "
                                   f"({rep['n_evaluated']} evaluated, {rep['n_clearing_floor']} clear)")
        return rep

    # try the top expressions in order until one survives the challenge
    tried = []
    for e in [x for x in ranked if x.get("executable") and (x.get("net_edge_low") or -1) >= EX.MIN_NET_EDGE][:3]:
        row = rows[e["ticker"]]
        pm = next((m for m in game.get("markets", []) if m["ticker"] == e["ticker"]), None)
        inj = _player_injury(game, row) if e["family"] == "PLAYER_STAT" else None
        def _usable_alt(x):
            # an alternative whose player is out / unresolved cannot be the "superior expression" that sinks this one: that decision is itself blocked
            if x.get("family") != "PLAYER_STAT":
                return True
            st = (_player_injury(game, rows.get(x["ticker"], {})) or {}).get("status")
            return not (st is not None and str(st).upper() in CH.BAD_AVAILABILITY + ("QUESTIONABLE", "UNKNOWN"))
        ch = CH.challenge(th, next((c for c in th.get("candidates", []) if c["ticker"] == e["ticker"]), {"usage": e.get("usage")}), e, [x for x in ranked if x is not e and _usable_alt(x)],
                          packet_market=pm, player_injury=inj, quote_age_min=quote_age, mode=mode, unresolved_starters=unresolved_starters, live_requote=live_requote,
                          owner_open_units=owner["by_game"].get(th["game_id"], 0.0) / UNIT if owner["state"] == "OK" else 0.0,
                          game_cap_units=policy.max_exposure_per_game_units)
        tried.append({"ticker": e["ticker"], "side": e["side"], "name": e["name"], "cleared": ch["cleared"], "open": ch["open"], "failed": ch["failed"]})
        if not ch["cleared"]:
            continue
        corro = _corroborations(th, e, row, pm, elig, replay_segments)
        depth_units = _depth_units(pm, e)
        depth_ok = depth_units >= 1
        decision = ST.decide(ST.StakeInputs(
            net_edge_low=e["net_edge_low"], fair_low=e["fair_low"], fair_high=e["fair_high"], challenge_clear=True, full_stake_executable=depth_ok,
            price_within_ceiling=(e["ceiling_cents"] is not None and e["ask_cents"] <= e["ceiling_cents"]),
            winning_scripts=(e["scripts"] or {}).get("winning_scripts", 0), script_neutral=bool((e["scripts"] or {}).get("script_neutral")),
            single_script_dependent=bool((e["scripts"] or {}).get("single_script_dependent")), corroborations=tuple(corro["accepted"]),
            family_eligibility=_family_eligibility(elig, e["family"]), model_market_gap=corro.get("model_market_gap")))
        if decision.units > depth_units >= 1:
            decision.notes.append(f"stake cut from {decision.units}U to {depth_units}U: displayed depth on the buy side covers {depth_units}U at {DEPTH_COVER}x")
            decision.units = depth_units
        if decision.units < 1:
            tried[-1]["cleared"] = False
            tried[-1]["stake_blocked"] = decision.blocked
            continue
        rec = candidate_record(run=run, game=game, row=row, ev=e, thesis=th, units=decision.units, as_of=as_of, challenge=ch, mode=mode)
        rep["outcome"] = "SELECTED"
        rep["selected"] = {"recommendation_id": rec["recommendation_id"], "game_id": th["game_id"], "thesis_id": th["thesis_id"], "short_reason": th.get("short_reason"),
                           "evaluation": _slim(e, full=True),
                           "challenge": ch, "stake": decision.to_dict(), "stake_units": decision.units, "corroborations": corro, "record": rec,
                           "runner_up": next((_slim(x) for x in ranked if x is not e and x.get("executable") and (x.get("net_edge_low") or -1) >= EX.MIN_NET_EDGE), None)}
        rep["tried"] = tried
        return rep
    rep["tried"] = tried
    rep["pass_reasons"].append("the top-ranked expression(s) did not survive the independent challenge or the staking ladder: " +
                               "; ".join(f"{t['name']} ({t['side']}): " + (", ".join(t['open'] + t['failed']) or "; ".join(t.get('stake_blocked', []))) for t in tried))
    return rep


def _slim(e: dict, full: bool = False) -> dict:
    keys = ("ticker", "side", "name", "settles", "family", "period", "ladder_thesis", "ask_cents", "bid", "width", "fair_low", "fair_high", "fair_mid", "fair_basis", "net_edge_low", "net_edge_mid",
            "fee_per_contract", "breakeven_price", "ceiling_cents", "roi_low", "edge_per_sd", "executable", "reject")
    out = {k: e.get(k) for k in keys}
    sc = e.get("scripts") or {}
    out["scripts"] = {k: sc.get(k) for k in ("basis", "winning_scripts", "major_scripts", "max_script_share_of_wins", "single_script_dependent")}
    if full:
        out["script_matrix"] = sc.get("matrix")
    return out


def _player_injury(game, row):
    for r in (game.get("injuries") or {}).get("records", []):
        if r.get("player") == row.get("subject"):
            return {"status": r.get("state")}
    return {"status": "Active"} if row.get("subject") else None


DEPTH_COVER = 3


def _depth_units(pm, e) -> int:
    """Whole units the displayed book can fill with `DEPTH_COVER`x cover (the preflight then walks the real book for the real size)."""
    if not pm:
        return 0
    depth = pm.get("book_depth_yes") if e["side"] == "NO" else pm.get("book_depth_no")      # depth is on the side that fills our buy
    return 0 if depth is None else min(5, int(float(depth) // (DEPTH_COVER * UNIT)))


def _family_eligibility(elig, fam):
    key = ELIG_KEY.get(fam)
    if not key:
        return None
    return ((elig.get("families") or {}).get(f"BOARD_V2|{key}") or {}).get("status")


def _corroborations(th, e, row, pm, elig, replay_segments) -> dict:
    accepted, notes = [], []
    mv = ((pm or {}).get("movement") or {}).get("total_move_since_first_capture")
    if mv is not None:
        toward = float(mv) if e["side"] == "YES" else -float(mv)
        if toward >= 0.01 and e.get("width", 1) <= 0.05:
            accepted.append("LINE_MOVE_TOWARD_US"); notes.append(f"price moved {toward * 100:+.0f}c toward this side since first capture")
    inc = (row.get("incumbent") or {})
    gap = None
    if inc.get("support_state") == "SUPPORTED" and inc.get("model_probability") is not None and row.get("mid") is not None:
        mp = float(inc["model_probability"]) if e["side"] == "YES" else 1 - float(inc["model_probability"])
        mid = float(row["mid"]) if e["side"] == "YES" else 1 - float(row["mid"])
        gap = abs(mp - mid)
        if ELIG := _family_eligibility(elig, e["family"]):
            if ELIG in ("WATCH", "LIMITED", "TRUSTED") and mp - (e["ask"] + (e.get("fee_per_contract") or 0)) >= 0 and gap <= 0.10:
                accepted.append("INCUMBENT_AGREES"); notes.append(f"incumbent {mp:.2f} agrees after fees; gap to mid {gap:.2f}; family {ELIG}")
    for c in th.get("corroborations", []):
        k = c.get("kind")
        if k == "TACTICAL_DATA" and any(m.get("market_unmoved") is True for m in (th.get("evidence") or {}).get("measured", [])):
            accepted.append(k); notes.append("tactical/availability fact marked market-unmoved: " + str(c.get("evidence", ""))[:120])
        elif k == "REPLAY_SEGMENT" and replay_segments and (replay_segments.get(e["family"]) or {}).get("qualifies"):
            accepted.append(k); notes.append("replay segment qualifies")
    return {"accepted": sorted(set(accepted)), "notes": notes, "model_market_gap": gap}


# ------------------------------------------------------------------------------------------------ preflight

def _preflight(lines, run, as_of, mode, root, market_data_root, handicap_root, policy, live_client=None, bank_total=None,
               fee_observations_root=None, clock=None) -> dict:
    if not lines:
        return {}
    if mode == REHEARSAL:
        return {l["recommendation_id"]: {"verdict": "NOT_RUN", "reason": "REHEARSAL: the snapshot is replayed as of its own capture time; preflight is meant for the live clock"} for l in lines}
    if not handicap_root or not os.path.isdir(handicap_root) or (live_client is None and (not market_data_root or not os.path.isdir(market_data_root))):
        return {l["recommendation_id"]: {"verdict": "NOT_RUN", "reason": "no market-data / handicap-data checkout (or live client) supplied, so depth, fee and quote gates did not run"} for l in lines}
    from nfl_edge.handicap import live_evidence as LE
    from nfl_edge.handicap import preflight as P
    cands = [dict(l["record"], decision=S.RECOMMENDED) for l in lines]
    capture_index = book_index = None
    docs = []
    decision_at = as_of
    if live_client is not None:
        # THE LIVE PATH: ask the venue about each finalist's contract (two public GETs each), THEN stamp the decision instant, then run the gates.
        for c in cands:
            try:
                docs.append(LE.collect(live_client, c["market_ticker"], side=c.get("side") or "YES", kickoff_utc=c.get("kickoff_utc")))
            except LE.EvidenceError as e:
                docs.append({"market_ticker": c["market_ticker"], "error": str(e)})
        good = [d for d in docs if "error" not in d]
        capture_index, book_index = LE.EvidenceQuoteIndex(good), LE.EvidenceBookIndex(good)
        decision_at = (clock or (lambda: datetime.now(timezone.utc)))()
    res = P.preflight_batch(cands, market_data_root=market_data_root, ledger_root=handicap_root, root=root, approval_as_of=decision_at, policy=policy,
                            bankroll_snapshot=bank_total, capture_index=capture_index, book_index=book_index,
                            fee_observations_root=fee_observations_root or market_data_root)
    out = {}
    for r in res:
        out[r.candidate_id] = {"verdict": r.verdict, "approved_stake": r.approved_stake, "blocking_reasons": r.blocking_reasons, "warnings": r.warnings,
                               "may_be_shown_as_a_bet": r.may_be_shown_as_a_bet, "depth": r.depth, "net_ev": r.net_ev, "decision_at": decision_at.isoformat(),
                               "evidence": "LIVE_TICKER_FETCH" if live_client is not None else "CAPTURE_STREAM"}
    for c, l in zip(cands, lines):
        doc = next((d for d in docs if d.get("market_ticker") == c["market_ticker"]), None)
        pf = out.get(l["recommendation_id"])
        if pf is not None and doc is not None:
            pf["live_error"] = doc.get("error")
            qr = (doc.get("quote_row") or {})
            from nfl_edge.execution import quotes as Q
            sp = Q._side_prices(qr) if qr else {}
            pf["live_ask"] = sp.get("yes_ask") if (c.get("side") or "YES") == "YES" else sp.get("no_ask")
            pf["live_retrieved_at"] = (doc.get("market") or {}).get("retrieved_at")
    if docs:
        out["__evidence_docs__"] = [d for d in docs if "error" not in d]
    return out


# ------------------------------------------------------------------------------------------------ the card

def _card_line(sel, by_id, pf, mode, authorized=None, auth_reason=None) -> dict:
    ev, rec = sel["evaluation"], sel["record"]
    g = by_id[sel["game_id"]]
    units = sel["final_units"]
    if mode == REHEARSAL:
        status = "REHEARSAL (not executable)"
    elif pf is None or pf.get("verdict") == "NOT_RUN":
        status = "CANDIDATE (preflight not run)"
    elif pf["verdict"] == "APPROVED" and authorized is False:
        status = "CANDIDATE (preflight approved; " + str(auth_reason or "stake not authorized")[:200] + ")"
    elif pf["verdict"] == "APPROVED":
        status = "BET (preflight approved)"
    else:
        status = "BLOCKED"
    if pf and pf.get("approved_stake") and pf["verdict"] == "APPROVED":
        units = int(pf["approved_stake"] // UNIT)
    why = sel["evaluation"]
    short = sel.get("short_reason") or rec["primary_thesis"].split("] ", 1)[-1]
    short = short if len(short) <= 150 else short[:147].rsplit(" ", 1)[0] + "…"
    reason = (f"{short} Fair {_cents(ev['fair_low'])}-{_cents(ev['fair_high'])} vs ask {ev['ask_cents']}¢; "
              f"net edge ≥ {ev['net_edge_low'] * 100:.1f}¢ after fees at the low end.")
    return {"game_id": sel["game_id"], "game": f"{g['away']} @ {g['home']}", "kickoff_utc": g["kickoff_utc"], "thesis_id": sel["thesis_id"],
            "bet": ev["name"], "side": ev["side"], "ticker": ev["ticker"], "settles": ev["settles"],
            "current_price_cents": (round(pf["live_ask"] * 100) if (pf or {}).get("live_ask") is not None else ev["ask_cents"]),
            "bet_up_to_cents": ev["ceiling_cents"], "price_at_pricing_cents": ev["ask_cents"], "live_ask": (pf or {}).get("live_ask"), "stake_units": units, "stake_dollars": units * UNIT, "reason": reason, "status": status,
            "recommendation_id": sel["recommendation_id"], "preflight": pf, "fair_range": [ev["fair_low"], ev["fair_high"]],
            "stake_tier": sel["stake"]["tier"], "tier_limits": sel["stake"]["unmet_for_next_tier"][:2], "flags": sel["challenge"]["flags"]}


def _assemble(run, mode, as_of, gate, games_out, card_lines, thesis_reports, accepted, dossiers, owner, policy, report, bank_meta, blocked_msg, preflight=None) -> dict:
    pk = run["packet"]
    return {"card_version": CARD_VERSION, "mode": mode, "as_of": as_of.isoformat(), "blocked": blocked_msg,
            "source": {"packet_sha": pk.get("packet_sha"), "handicap_run_id": pk.get("handicap_run_id"), "packet_built_at": pk.get("built_at"),
                       "season": pk.get("season"), "week": pk.get("week")},
            "data_gate": gate, "policy": {"policy_id": policy.policy_id, "unit_dollars": policy.fixed_unit_dollars, "max_units": policy.max_stake_per_position_units,
                                          "limits": report.limits if report else None},
            "games": games_out, "lines": card_lines, "theses": thesis_reports, "owner_open_exposure": owner, "portfolio": report.to_dict() if report else None,
            "fair_value_engine": {"version": FV.FAIRVALUE_VERSION, "bank": bank_meta}, "dossiers": dossiers,
            "preflight": preflight,
            "disclaimers": ["Nothing here places a wager. Kalshi account interaction is read-only; the owner places bets.",
                            "Fair values are the analyst's thesis ranges run through a market-centred simulation, not validated model probabilities. "
                            "No model in this repository is TRUSTED or LIMITED; research arms are context only."]}


# ------------------------------------------------------------------------------------------------ privacy

def redact_public(card: dict) -> dict:
    """The card as it may be written where a public repository can see it: no owner position sizes by game, no bankroll amounts (none are on the card to begin
    with -- `bankroll` carries a state), and only the fact that a game carries an open owner position."""
    out = dict(card)
    ox = out.get("owner_open_exposure") or {}
    out["owner_open_exposure"] = {"state": ox.get("state"), "games_with_open_owner_position": len(ox.get("by_game") or {}),
                                  "note": "positions and amounts withheld: owner fills are not republished by the card"}
    if out.get("portfolio"):
        out["portfolio"] = dict(out["portfolio"], outstanding="withheld (owner positions are not republished)")
    import copy
    out["theses"] = copy.deepcopy(out.get("theses") or [])
    for t in out["theses"]:
        items = ((t.get("selected") or {}).get("challenge") or {}).get("items") or []
        for it in items:
            if it.get("id") == "C10" and it.get("status") != "CLEAR":
                it["finding"] = "owner exposure on this game, if any, is counted against the game cap (positions and amounts withheld from public output)"
        for tr in (t.get("selected") or {}).get("portfolio", {}) and [t["selected"]["portfolio"]] or []:
            tr.pop("outstanding", None)
    return out


# ------------------------------------------------------------------------------------------------ rendering

def render_markdown(card: dict) -> str:
    L = []
    mode = card["mode"]
    banner = ("**REHEARSAL — replay of an old snapshot at its own capture time. Nothing below is executable.**" if mode == REHEARSAL else
              "**BLOCKED — no bets.** " + str(card["blocked"]) if card["blocked"] else "LIVE card. A line is a BET only when it says *preflight approved*.")
    L += [f"# NFL card — week {card['source']['week']}, {card['as_of'][:16].replace('T', ' ')} UTC", "", banner, "",
          f"packet `{card['source']['packet_sha']}` · data gate **{card['data_gate']['status']}** · capture age {card['data_gate']['capture_age_minutes']} min · "
          f"1U = ${card['policy']['unit_dollars']} · max {card['policy']['max_units']}U", ""]
    live = sorted((g for g in card["games"] if g["state"] != G_POST), key=lambda g: g["kickoff_utc"])
    if live:
        first = live[0]
        mins = (C_ts(first["kickoff_utc"]) - C_ts(card["as_of"])).total_seconds() / 60.0
        L += [f"First kickoff on this slate: **{first['away']} @ {first['home']}**, {first['kickoff_utc'][5:16].replace('T', ' ')} UTC ({mins:.0f} min after this card's clock). "
              "Bets on that game must be placed before it; later games can wait for their inactive lists.", ""]
    if card["data_gate"]["warnings"]:
        L += ["> " + w for w in card["data_gate"]["warnings"]] + [""]
    bk = card.get("bankroll")
    if mode == LIVE and bk is not None:
        L += [("Stake authorization: **OK** (available-cash balance " + str(bk.get("age_hours")) + " h old; covers every line: " + str(bk.get("slate_covered_by_available_cash")) + ")") if bk["authorizes_stakes"]
              else "Stake authorization: **BLOCKED** — " + "; ".join(bk.get("reasons") or ["no bankroll evidence"]) + ". Lines below are CANDIDATES; nothing is authorized to be bet.", ""]
    rc = card.get("review_coverage")
    if rc and rc.get("submission_supplied"):
        L += ["Review coverage: " + ", ".join(f"{k} {v}" for k, v in sorted(rc["counts"].items())) + f" · {rc['deeply_reviewed_games']} of {rc['unstarted_games']} unstarted games deeply reviewed, "
              f"{rc['not_reviewed_games']} NOT_REVIEWED. A game is deeply reviewed only when its review record cites the dossier's evidence in every required category.", ""]
        if rc["submission_errors"]:
            L += ["> Submission errors: " + "; ".join(rc["submission_errors"]), ""]
    actionable = [l for l in card["lines"] if l["status"] != "BLOCKED"]
    blocked = [l for l in card["lines"] if l["status"] == "BLOCKED"]
    if actionable:
        L += ["| Game | Bet | Current price | Bet up to | Stake | Reason |", "|---|---|---|---|---|---|"]
        for l in actionable:
            L.append(f"| {l['game']} | **BUY {l['side']}** {l['bet']}<br><sub>{l['ticker']}</sub> | {l['current_price_cents']}¢ ({l['current_price_cents']}%) | "
                     f"{l['bet_up_to_cents']}¢ | {l['stake_units']}U (${l['stake_dollars']}) | {l['reason']} <br><sub>{l['status']}</sub> |")
        L.append("")
        for l in actionable:
            L.append(f"* `{l['ticker']}` settles: {l['settles']}")
        L.append("")
    if blocked:
        L += ["## Candidates BLOCKED by preflight — do NOT bet", ""]
        L += [f"* {l['game']}: {l['bet']} ({l['side']}) — " + "; ".join((l['preflight'] or {}).get('blocking_reasons', [])[:3]) for l in blocked] + [""]
    if not actionable:
        L += ["## No bets on this card", "", "Every game was reviewed or triaged and nothing cleared the evidence, challenge, price and execution gates. That is an outcome, not an error.", ""]
    L += ["## Every game, one terminal state", "", "| Game | Kickoff (UTC) | State | Why |", "|---|---|---|---|"]
    for g in sorted(card["games"], key=lambda x: x["kickoff_utc"]):
        L.append(f"| {g['away']} @ {g['home']} | {g['kickoff_utc'][5:16].replace('T', ' ')} | {g['state']} | {(g['state_reason'] or '')[:420]} |")
    L.append("")
    for t in card["theses"]:
        if t.get("outcome") == "EXCLUDED":
            continue
        L += [f"## Thesis {t['thesis_id']}: {t.get('statement', '')}", ""]
        if t.get("shift"):
            L.append(f"Shift applied to the market centre (home margin / total, points): {t['shift']['home_margin']} / {t['shift']['total']}. "
                     f"Engine noise vs the market with no thesis (rms): " + ", ".join(f"{k} {v['rms_gap']:.3f}" for k, v in (t.get("baseline_noise") or {}).items()) + ".")
        L.append(f"Evaluated {t.get('n_evaluated')} contract-sides; {t.get('n_clearing_floor')} clear the 2.0¢ conservative net-edge floor. Outcome: **{t['outcome']}**.")
        if t.get("pass_reasons"):
            L += ["", "PASS because: " + " ".join(t["pass_reasons"])]
        ns = t.get("needed_scale")
        if ns:
            if ns.get("factor"):
                f = ns["first_to_clear"]
                L += ["", f"How far from a bet: a contract first clears at {ns['factor']}x the stated shift (home margin {ns['scaled_shift']['home_margin']}, total {ns['scaled_shift']['total']}): "
                          f"{f['name']} ({f['side']}) at {f['ask_cents']}¢. A reading aid, not a position."]
            else:
                L += ["", ns["note"] + "."]
        if t.get("selected"):
            s = t["selected"]; e = s["evaluation"]
            L += ["", f"Best expression: **{e['name']}** ({e['side']}) at {e['ask_cents']}¢, fair {e['fair_low']:.2f}–{e['fair_high']:.2f}, ceiling {e['ceiling_cents']}¢, "
                      f"stake tier {s['stake']['tier']}. " + (f"Runner-up: {s['runner_up']['name']} ({s['runner_up']['side']}) at {s['runner_up']['ask_cents']}¢. " if s.get("runner_up") else ""),
                  "Challenge: " + ", ".join(f"{i['id']} {i['status']}" for i in s["challenge"]["items"]), ""]
            for i in s["challenge"]["items"]:
                if i["status"] in ("FLAG", "OPEN", "FAIL"):
                    L.append(f"* {i['id']} {i['status']}: {i['finding']}")
            if s["stake"]["unmet_for_next_tier"]:
                L.append("* Why not more: " + "; ".join(s["stake"]["unmet_for_next_tier"][:2]))
            L.append("")
            if e.get("script_matrix"):
                L += ["| script | P(script) | P(win \\| script) |", "|---|---|---|"]
                L += [f"| {m['label']} | {m['p_script']:.0%} | {'n/a' if m['p_win_given_script'] is None else format(m['p_win_given_script'], '.0%')} |" for m in e["script_matrix"]]
                L.append("")
        if t.get("by_family"):
            L += ["Best clearing expression in each contract family (like-for-like, same thesis):", "", "| family | contract | side | ask | fair | net edge (low) |", "|---|---|---|---|---|---|"]
            L += [f"| {f['family']}{'/' + f['period'] if f.get('period') not in (None, 'FULL') else ''} | {f['name']} | {f['side']} | {f['ask_cents']}¢ | {f['fair_low']:.2f}–{f['fair_high']:.2f} | {f['net_edge_low'] * 100:+.1f}¢ |" for f in t["by_family"]]
            L.append("")
        if t.get("rejected"):
            L += ["Rejected / not selected (top by rank):", ""]
            L += [f"* {r.get('name', r.get('ticker'))} {r.get('side', '')} {('@' + str(r['ask_cents']) + '¢') if r.get('ask_cents') else ''} — {r['reason']}" for r in t["rejected"][:12]]
            L.append("")
    return "\n".join(L) + "\n"
