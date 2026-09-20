"""RUN NFL's coverage contract, and the adversarial cases it exists to catch.

**RUN NFL means every executable Kalshi contract for every requested unstarted NFL game is examined and
accounted for.** `UNSUPPORTED_MODEL` is a statement about one model, never a reason to hide a contract.

Before this layer existed, a 1H total read `market price + UNSUPPORTED_MODEL` while Shadow v2's period
engine held a legitimate research projection for that exact ticker in `market-data`. These tests pin the
join, the accounting and the operator artifact, and each of the adversarial ones names the failure it is
defending against:

  * a period projection missing from the operator join -> counted as NOT_IN_SNAPSHOT, never dropped
  * an extra or duplicate ticker -> reported, never allowed to reconcile away a missing one
  * a Shadow v2 probability labelled as production -> impossible: separate fields, separate states
  * an unsupported market disappearing from the analysis artifact -> the artifact's row set IS the board
  * a partial shard publication -> detected by sha256 and row count, by identity
  * a stale capture presented as current -> a post-kickoff contract is POST_KICKOFF, not "unsupported"
  * later information entering an earlier projection -> a non-PROSPECTIVE_FROZEN row carries no probability
"""
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import nfl_edge.handicap.analysis as ANALYSIS  # noqa: E402
import nfl_edge.handicap.coverage as COV  # noqa: E402
import nfl_edge.handicap.shadow_v2_block as SV2  # noqa: E402


# ------------------------------------------------------------------ builders

def v2_row(ticker="KXNFL1HTOTAL-26SEP20CINHOU-11", arm="BOARD_V2", engine="PERIOD",
           state="PROJECTABLE_NOT_YET_VALIDATED", p=0.92, **kw):
    r = {"ticker": ticker, "model_arm": arm, "engine": engine, "engine_version": "period-engine-2.0.0",
         "distribution_version": "period-residual-bank-1.0.0", "model_version": "shadow-v2-1.0.0",
         "schema_version": "projection-2.2.0", "evidence_class": "PROSPECTIVE_FROZEN",
         "snapshot_id": "20260920T043756Z", "observed_at": "2026-09-20T04:24:46+00:00",
         "data_cutoff": "2026-09-20T04:37:56+00:00", "horizon_label": "CYCLE",
         "market_family": "TOTAL", "period": "1H", "stat_family": "total_points",
         "semantic_confidence": "PROVEN", "support_state": state, "support_reason": None,
         "p_yes": p, "contract_value": p, "mid": 0.93,
         "settlement_reachability": {"state": "DISPATCHABLE"},
         "information_sync": {"synchronization_state": "SYNCHRONIZED"},
         "flags": {"betting_authorized": False, "has_probability": p is not None}}
    r.update(kw)
    return r


def market(ticker="KXNFL1HTOTAL-26SEP20CINHOU-11", family="TOTAL", period="1H",
           support="UNSUPPORTED_MODEL", model_p=None, v2=None, sim=None, **kw):
    m = {"ticker": ticker, "family": family, "period": period, "stat": "total_points",
         "threshold": 11.0, "operator": ">=", "support_state": support, "support_reason": "family TOTAL period 1H not priced",
         "yes_bid": 0.92, "yes_ask": 0.94, "no_bid": 0.06, "no_ask": 0.08, "mid": 0.93, "width": 0.02,
         "volume": 2045.0, "open_interest": 2045.0, "no_real_market": False, "flags": [],
         "simulation": sim, "shadow_v2": v2}
    if model_p is not None:
        m["model_probability"] = model_p
    m.update(kw)
    return m


# ------------------------------------------------------------------ the join

def test_the_v2_join_is_by_ticker_identity_and_carries_its_provenance():
    table = {}
    block = SV2.market_view({"BOARD_V2": v2_row()}, table, packet_mid=0.93)
    assert block["support_state"] == "PROJECTABLE_NOT_YET_VALIDATED"
    assert block["p_yes"] == 0.92 and block["engine"] == "PERIOD"
    prov = table[block["provenance"]]
    assert prov["engine_version"] == "period-engine-2.0.0"
    assert prov["snapshot_id"] == "20260920T043756Z" and prov["model_arm"] == "BOARD_V2"


def test_a_market_derived_player_arm_is_never_the_primary_view():
    """MARKET_PLAYER_DIST is reconstructed FROM the Kalshi ladder. Promoting it would present the market
    back to the reader as an independent football opinion -- the exact substitution reconciliation exists
    to prevent."""
    arms = {"DATA_PLAYER_DIST": v2_row(arm="DATA_PLAYER_DIST", engine="PLAYER", p=0.41),
            "MARKET_PLAYER_DIST": v2_row(arm="MARKET_PLAYER_DIST", engine="PLAYER", p=0.55),
            "HYBRID_PLAYER_DIST": v2_row(arm="HYBRID_PLAYER_DIST", engine="PLAYER", p=0.48)}
    b = SV2.market_view(arms, {})
    assert b["primary_arm"] == "DATA_PLAYER_DIST" and b["p_yes"] == 0.41
    assert b["other_arms"]["MARKET_PLAYER_DIST"]["market_derived"] is True
    assert b["other_arms"]["HYBRID_PLAYER_DIST"]["market_derived"] is True


def test_a_row_that_is_not_prospectively_frozen_carries_no_probability_into_the_report():
    """Later information must not enter an earlier projection. A walk-forward research reconstruction is
    not a pregame projection and may not be read as one."""
    b = SV2.market_view({"BOARD_V2": v2_row(evidence_class="HISTORICAL_RESEARCH")}, {})
    assert b["p_yes"] is None
    assert "not a pregame projection" in b["probability_withheld_reason"]
    assert not SV2.has_probability(b)


def test_a_row_claiming_betting_authority_is_dropped_and_named(tmp_path):
    """The only correct value of `flags.betting_authorized` is false. A true one means the artifact is not
    what this reader believes it is, so the row is refused rather than quietly used."""
    import gzip
    d = tmp_path / "data" / "shadow" / "v2" / "projections" / "2026-09-20"
    d.mkdir(parents=True)
    good, bad = v2_row(), v2_row(ticker="KXNFL1HTOTAL-26SEP20CINHOU-18")
    bad["flags"] = {"betting_authorized": True}
    with gzip.open(d / "20260920T043756Z.BOARD_V2.projections.jsonl.gz", "wt") as f:
        for r in (good, bad):
            f.write(json.dumps(r) + "\n")
    rows, man = SV2.load_latest([str(tmp_path)])
    assert set(rows) == {good["ticker"]}
    assert man["refused_row_count"] == 1
    assert man["refused_rows"][0]["ticker"] == bad["ticker"]


def test_only_one_snapshot_is_ever_loaded(tmp_path):
    """All arms of ONE snapshot. Taking the newest file per arm independently would let one arm read a
    later market than another and produce numbers that were never simultaneously true."""
    import gzip
    d = tmp_path / "data" / "shadow" / "v2" / "projections" / "2026-09-20"
    d.mkdir(parents=True)
    for snap, p in (("20260920T043756Z", 0.92), ("20260920T063756Z", 0.61)):
        with gzip.open(d / f"{snap}.BOARD_V2.projections.jsonl.gz", "wt") as f:
            f.write(json.dumps(v2_row(snapshot_id=snap, p=p)) + "\n")
    # a player arm exists ONLY for the older snapshot: it must not be mixed into the newer one
    with gzip.open(d / "20260920T043756Z.DATA_PLAYER_DIST.projections.jsonl.gz", "wt") as f:
        f.write(json.dumps(v2_row(ticker="KXNFLRECYDS-X", arm="DATA_PLAYER_DIST", engine="PLAYER")) + "\n")
    rows, man = SV2.load_latest([str(tmp_path)])
    assert man["snapshot_id"] == "20260920T063756Z"
    assert list(rows) == ["KXNFL1HTOTAL-26SEP20CINHOU-11"]
    assert "DATA_PLAYER_DIST" in man["arms_missing"]
    # ... and an at-or-before instant selects the older one, whole
    from datetime import datetime, timezone
    rows2, man2 = SV2.load_latest([str(tmp_path)], at_or_before=datetime(2026, 9, 20, 5, 0, tzinfo=timezone.utc))
    assert man2["snapshot_id"] == "20260920T043756Z" and len(rows2) == 2


# ------------------------------------------------------------------ the accounting

def test_every_listed_contract_terminates_in_exactly_one_accounting_state():
    table = {}
    markets = [
        market(ticker="A", support="SUPPORTED", model_p=0.61),
        market(ticker="B", v2=SV2.market_view({"BOARD_V2": v2_row(ticker="B")}, table)),
        market(ticker="C", family="TEAM_STAT", period="FULL", support="UNSUPPORTED_RULES"),
        market(ticker="D", support="UNSUPPORTED_IDENTITY"),
        market(ticker="E", support="POST_KICKOFF_EXCLUDED"),
        market(ticker="F", family="AWARD", period="SEASON"),
        market(ticker="G", sim={"p_football": 0.4, "support_state": "FOOTBALL_ONLY_NO_RECONCILIATION"}),
    ]
    COV.classify_game(markets)
    states = [m["analysis"]["analysis_state"] for m in markets]
    assert states == [COV.MODEL_PRICED, COV.SHADOW_V2_PROJECTED, COV.MANUAL_HANDICAP,
                      COV.IDENTITY_UNRESOLVED, COV.POST_KICKOFF, COV.NON_FOOTBALL,
                      COV.COHERENT_SIM_PROJECTED]
    mx = COV.matrix(markets)
    assert mx["totals"]["listed"] == 7
    assert mx["totals"]["silently_omitted"] == 0
    assert sum(mx["totals"][c] for c in
               ("incumbent_priced", "coherent_sim", "shadow_v2", "manual_research", "research_required",
                "rules_blocked", "identity_blocked", "non_football", "post_kickoff", "silently_omitted")) == 7


def test_unsupported_rules_from_the_incumbent_is_not_read_as_unpinned_semantics():
    """The incumbent ledger writes UNSUPPORTED_RULES for RACE_TO_N ("requires in-game scoring-order
    simulation; not validated"), TEAM_STAT ("team stat ladders not modelled") and HALF_FULL_RESULT ("needs
    a period-correlated simulator"). Every one of those is a MODEL gap wearing a rules label, and reading
    it literally filed 763 contracts of the 2026 week 2 board under "cannot defensibly price"."""
    markets = [market(ticker=t, family=f, period=p, support="UNSUPPORTED_RULES")
               for t, f, p in (("a", "RACE_TO_N", "FULL"), ("b", "TEAM_STAT", "FULL"))]
    COV.classify_game(markets)
    for m in markets:
        assert m["analysis"]["analysis_state"] == COV.MANUAL_HANDICAP, m["analysis"]
        assert m["analysis"]["bucket"] == "C"
        assert m["analysis"]["manual_review_reason"]


def test_a_post_kickoff_contract_is_never_reported_as_merely_unsupported():
    """A stale capture presented as current. The incumbent ledger checks family support BEFORE kickoff, so
    69 DET @ BUF contracts of the 2026 week 2 board carried UNSUPPORTED_RULES / UNSUPPORTED_MODEL for a
    game played two days earlier. The accounting takes the union of the two lifecycle verdicts, so Shadow
    v2 saying POST_KICKOFF is enough."""
    m = market(support="UNSUPPORTED_RULES",
               v2=SV2.market_view({"BOARD_V2": v2_row(state="POST_KICKOFF", p=None,
                                                      support_reason="market observed after kickoff")}, {}))
    COV.classify_game([m])
    assert m["analysis"]["analysis_state"] == COV.POST_KICKOFF


def test_a_shadow_v2_probability_never_becomes_the_incumbents():
    m = market(v2=SV2.market_view({"BOARD_V2": v2_row(p=0.92)}, {}))
    COV.classify_game([m])
    assert "model_probability" not in m, "a research projection must not populate the production field"
    assert m["support_state"] == "UNSUPPORTED_MODEL", "the incumbent's own state is unchanged"
    assert m["shadow_v2"]["p_yes"] == 0.92
    assert m["analysis"]["analysis_state"] == COV.SHADOW_V2_PROJECTED
    assert "research, not validated" in m["analysis"]["reason"]


def test_a_priced_state_is_never_invented_for_a_research_projection():
    for state in ("PROJECTABLE_NOT_YET_VALIDATED", "RESEARCH_REQUIRED", "JOINT_MODEL_REQUIRED"):
        b = SV2.market_view({"BOARD_V2": v2_row(state=state, p=(0.5 if state == "PROJECTABLE_NOT_YET_VALIDATED" else None))}, {})
        assert b["support_state"] == state, "the state is reported verbatim, never relabelled"


# ------------------------------------------------------------------ the operator artifact

def _packet(markets, game_id="2026_02_CIN_HOU"):
    COV.classify_game(markets)
    g = {"game_id": game_id, "season": 2026, "week": 2, "home_team": "HOU", "away_team": "CIN",
         "kickoff_utc": "2026-09-20T17:00:00+00:00", "game_state": "PREGAME", "minutes_to_kickoff": 600.0,
         "counts": {"markets_listed": len(markets)}, "markets": markets,
         "coverage": COV.matrix(markets), "shadow_v2": {"snapshot_id": "20260920T043756Z"}}
    return {"schema_version": "1.2.0", "packet_sha": "x", "handicap_run_id": "r", "built_at": "2026-09-20T06:00:00+00:00",
            "season": 2026, "week": 2, "sources": {"model_version": "shadow-0.4.0"}, "games": [g],
            "slate_summary": {"markets_listed_slate": len(markets), "coverage_matrix": COV.matrix(markets)}}


def test_the_analysis_artifact_holds_every_listed_contract_exactly_once(tmp_path):
    markets = [market(ticker=f"T{i}") for i in range(5)]
    man = ANALYSIS.write(str(tmp_path), _packet(markets))
    assert man["counts"]["rows_total"] == 5 and man["counts"]["duplicate_tickers"] == 0
    assert man["invariants"]["zero_silently_omitted"] is True
    res = ANALYSIS.verify(str(tmp_path))
    assert res["ok"] and res["tickers"] == 5


def test_an_unsupported_market_does_not_disappear_from_the_analysis_artifact(tmp_path):
    """The artifact's row set IS the listed board. A contract nothing can price is a row with a reason."""
    markets = [market(ticker="PRICED", support="SUPPORTED", model_p=0.6),
               market(ticker="NOTHING", family="GAME_EVENT", period="FULL", support="UNSUPPORTED_RULES")]
    ANALYSIS.write(str(tmp_path), _packet(markets))
    shard = json.load(open(tmp_path / "analysis" / "games" / "2026_02_CIN_HOU.json"))
    by = {r["ticker"]: r for r in shard["rows"]}
    assert set(by) == {"PRICED", "NOTHING"}
    assert by["NOTHING"]["bucket"] == "D" and by["NOTHING"]["reason"]
    assert by["NOTHING"]["yes_meaning"].startswith("YES iff")


def test_a_duplicate_ticker_cannot_reconcile_away_a_missing_one(tmp_path):
    markets = [market(ticker="A"), market(ticker="A"), market(ticker="B")]
    man = ANALYSIS.write(str(tmp_path), _packet(markets))
    assert man["counts"]["duplicate_tickers"] == 1
    assert man["invariants"]["no_duplicate_tickers"] is False
    res = ANALYSIS.verify(str(tmp_path))
    assert not res["ok"]
    assert any("duplicate" in p for p in res["problems"])


def test_a_partial_shard_publication_is_detected_by_identity(tmp_path):
    markets = [market(ticker=f"T{i}") for i in range(3)]
    ANALYSIS.write(str(tmp_path), _packet(markets))
    assert ANALYSIS.verify(str(tmp_path))["ok"]
    # a shard that lost a row: the sha and the row count both disagree with the manifest
    p = tmp_path / "analysis" / "games" / "2026_02_CIN_HOU.json"
    shard = json.load(open(p))
    shard["rows"] = shard["rows"][:-1]
    json.dump(shard, open(p, "w"), sort_keys=True)
    res = ANALYSIS.verify(str(tmp_path))
    assert not res["ok"]
    assert any("sha256" in x for x in res["problems"]) and any("rows on disk" in x for x in res["problems"])
    # ... and an absent shard entirely
    os.remove(p)
    res2 = ANALYSIS.verify(str(tmp_path))
    assert not res2["ok"] and any("is absent" in x for x in res2["problems"])


def test_a_contract_with_no_accounting_state_is_reported_not_hidden(tmp_path):
    """SILENTLY_OMITTED exists only so it can be asserted to be zero. If one ever appears, every surface
    has to say so rather than presenting a short board as a complete one."""
    m = market(ticker="ORPHAN")
    m["analysis"] = {}                       # what a classifier bug looks like from here
    mx = COV.matrix([m])
    assert mx["totals"]["silently_omitted"] == 1
    assert mx["buckets"]["!"]["n"] == 1
    packet = {"schema_version": "1.2.0", "packet_sha": "x", "handicap_run_id": "r",
              "built_at": "t", "season": 2026, "week": 2, "sources": {},
              "games": [{"game_id": "G", "counts": {"markets_listed": 1}, "markets": [m],
                         "coverage": mx, "shadow_v2": {}}],
              "slate_summary": {"markets_listed_slate": 1, "coverage_matrix": mx}}
    man = ANALYSIS.write(str(tmp_path), packet)
    assert man["invariants"]["zero_silently_omitted"] is False
    res = ANALYSIS.verify(str(tmp_path))
    assert not res["ok"]
    assert any("silently omitted" in p for p in res["problems"])


def test_a_listed_contract_the_v2_snapshot_never_saw_is_counted_not_dropped():
    """Shadow v2 prices the universe of the latest DAILY discovery run. A contract Kalshi opened after that
    run has no v2 row however well the engine supports its family -- on the 2026 week 2 board that was
    exactly one period ticker, `KXNFL1HTEAMTOTAL-26SEP20PITNE-PIT9`, absent from the last four discovery
    runs and present in the capture."""
    seen = market(ticker="SEEN", v2=SV2.market_view({"BOARD_V2": v2_row(ticker="SEEN")}, {}))
    unseen = market(ticker="UNSEEN", v2=None)
    COV.classify_game([seen, unseen])
    view = SV2.game_view([m["shadow_v2"] for m in (seen, unseen) if m.get("shadow_v2")],
                         {"snapshot_id": "s", "arms": {"BOARD_V2": {}}, "arms_missing": []},
                         listed=[seen, unseen])
    assert view["listed_contracts"] == 2 and view["with_v2_row"] == 1 and view["not_in_snapshot"] == 1
    assert "discovery run" in view["not_in_snapshot_reason"]
    assert unseen["analysis"]["analysis_state"] == COV.MANUAL_HANDICAP


# ------------------------------------------------------------------ the authority boundary

REAL_MONEY_MODULES = (
    "nfl_edge/handicap/schema.py",          # the recommendation record
    "nfl_edge/handicap/gates.py",           # the real-money gates
    "nfl_edge/handicap/risk.py",            # sizing and the risk policy
    "nfl_edge/handicap/preflight.py",       # the pre-trade check
    "nfl_edge/handicap/approval.py",
    "nfl_edge/handicap/airtable_bridge.py",
)
RESEARCH_NAMES = ("shadow_v2", "SHADOW_V2_PROJECTED", "PROJECTABLE_NOT_YET_VALIDATED", "p_yes",
                  "coherent_simulation", "COHERENT_SIM_PROJECTED", "analysis_state")


def test_no_research_projection_field_is_readable_from_the_real_money_path():
    """A Shadow v2 or coherent-simulation probability must not reach recommendation, staking or preflight.

    Checked as a static property of the modules that decide real money rather than as a convention: if one
    of them ever learns the name of a research field, that is the moment to notice, not after a stake has
    been sized from a PROJECTABLE_NOT_YET_VALIDATED number.
    """
    found = []
    for rel in REAL_MONEY_MODULES:
        src = open(os.path.join(ROOT, rel)).read()
        for name in RESEARCH_NAMES:
            if name in src:
                found.append(f"{rel} names {name!r}")
    assert not found, ("the real-money path gained a reference to a research projection field:\n  "
                       + "\n  ".join(found))


def test_the_negative_control_for_that_audit_actually_fails(tmp_path):
    """The audit above is only worth having if it can fail. Same check, over a file that does name one."""
    fake = tmp_path / "gates.py"
    fake.write_text("def size(rec):\n    return rec['shadow_v2']['p_yes']\n")
    src = fake.read_text()
    assert any(n in src for n in RESEARCH_NAMES)


def test_a_research_row_in_the_analysis_artifact_is_labelled_as_research(tmp_path):
    markets = [market(ticker="R", v2=SV2.market_view({"BOARD_V2": v2_row(ticker="R")}, {}))]
    ANALYSIS.write(str(tmp_path), _packet(markets))
    shard = json.load(open(tmp_path / "analysis" / "games" / "2026_02_CIN_HOU.json"))
    row = shard["rows"][0]
    assert row["incumbent"]["model_probability"] is None
    assert row["shadow_v2"]["support_state"] == "PROJECTABLE_NOT_YET_VALIDATED"
    notes = shard["authority_notes"]
    assert "not validated" in notes["shadow_v2"]
    assert "PROJECTABLE_NOT_YET_VALIDATED means exactly that" in notes["shadow_v2"]
    assert "did not beat the market overall" in notes["coherent_simulation"]
