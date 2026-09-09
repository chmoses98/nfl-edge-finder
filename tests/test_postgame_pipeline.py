"""End to end: a published ledger plus a captured quote history become an immutable evaluation corpus.

This runs the real `scripts/shadow/settle_games.py` over a `market-data` tree built in a temp directory, with
REAL nflverse final results for 2025 week 1 Dallas at Philadelphia. Only the result book is injected (so the
test needs no parquet reader); the ledger reading, close selection, settlement, store planning, manifest,
cross-check, scorecard and exit codes are the production code paths.

Four properties are asserted that no unit test can establish on its own:

  * a game whose evidence is incomplete produces NOTHING, not a batch of refusals;
  * the shadow ledger is byte-identical after the run -- the corpus is a second corpus, not an edit of the first;
  * a rerun writes nothing and leaves every file untouched;
  * a rerun whose evidence CHANGED fails with a conflict and still writes nothing.
"""
import copy
import glob
import gzip
import hashlib
import importlib.util
import json
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FIXTURE = os.path.join(ROOT, "tests", "fixtures", "postgame", "dal_phi_2025_w1.results.json")

GAME = "2025_01_DAL_PHI"
PENDING_GAME = "2026_01_NE_SEA"
KICKOFF = "2025-09-05T00:20:00+00:00"          # 20:20 US-Eastern on 2025-09-04
KICKOFF_TS = 1757031600.0
HURTS, LAMB, BARKLEY = "00-0036389", "00-0036358", "00-0034844"
NOBODY = "00-0000001"
DRESSED = "00-0009999"          # listed in the snap table with zero snaps on every unit: the scalar branch


def load_script(name):
    path = os.path.join(ROOT, "scripts", "shadow", f"{name}.py")
    spec = importlib.util.spec_from_file_location(f"_script_{name}", path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


settle_games = load_script("settle_games")
validate_evaluations = load_script("validate_evaluations")
KS = settle_games.KS


# ---------------------------------------------------------------------------- the market-data tree
def observation(pid, ticker, *, run_id, observed_at, minutes_to_kickoff, family, model_p, yes_bid, yes_ask,
                game_id=GAME, support_state="SUPPORTED", **kw):
    o = {"prediction_id": pid, "schema_version": "1.0.0", "run_id": run_id, "observed_at": observed_at,
         "model_version": "shadow-0.4.0", "model_artifact_sha": "abc123", "calibration_version": "none-v0",
         "feature_cutoff": observed_at, "ticker": ticker,
         "event_ticker": ticker.rsplit("-", 1)[0], "series_ticker": ticker.split("-")[0],
         "family": family, "period": "FULL", "stat": None, "threshold": None, "floor_strike": None,
         "operator": ">=", "direction": "YES", "game_id": game_id, "season": 2025, "week": 1,
         "home_team": "PHI", "away_team": "DAL", "team": None, "player_id": None, "player_kalshi_id": None,
         "player_name": None, "kickoff_utc": KICKOFF, "minutes_to_kickoff": minutes_to_kickoff,
         "model_event_probability": model_p, "model_contract_value": model_p,
         "calibrated_probability": model_p, "availability_state": "EXPECTED_ACTIVE", "p_plays": 0.98,
         "p_inactive": 0.01, "yes_bid": yes_bid, "yes_ask": yes_ask, "no_bid": 1 - yes_ask,
         "no_ask": 1 - yes_bid, "mid": (yes_bid + yes_ask) / 2, "quote_width": yes_ask - yes_bid,
         "volume": 1000.0, "open_interest": 900.0, "last_price": yes_ask, "liquidity": 250.0,
         "minutes_since_price_change": 3.0, "support_state": support_state, "support_reason": None,
         "data_health": "healthy", "quality_flags": [], "selected": False}
    o.update(kw)
    return o


SNAPSHOTS = [("20250903T200000Z", "2025-09-03T20:00:00+00:00", 1700.0),     # T-28h
             ("20250904T180000Z", "2025-09-04T18:00:00+00:00", 380.0),      # T-6h20
             ("20250904T235000Z", "2025-09-04T23:50:00+00:00", 30.0)]       # T-30m

# One prediction per (snapshot, market). The model probabilities are deliberately a mixture of good and bad so
# the scorecard has something to distinguish.
MARKETS = [
    dict(ticker="KXNFLGAME-25SEP04DALPHI-PHI", family="GAME_WINNER", operator="event", team="PHI",
         model_p=0.62, yes_bid=0.57, yes_ask=0.59),
    dict(ticker="KXNFLSPREAD-25SEP04DALPHI-PHI4", family="SPREAD", operator=">", floor_strike=3.5, team="PHI",
         model_p=0.55, yes_bid=0.50, yes_ask=0.52),
    dict(ticker="KXNFLTOTAL-25SEP04DALPHI-45", family="TOTAL", threshold=45, model_p=0.48,
         yes_bid=0.51, yes_ask=0.53),
    dict(ticker="KXNFLTEAMTOTAL-25SEP04DALPHI-PHI24", family="TEAM_TOTAL", threshold=24, team="PHI",
         model_p=0.52, yes_bid=0.47, yes_ask=0.49),
    dict(ticker="KXNFLBOTH-25SEP04DALPHI-20", family="BOTH_TEAMS_SCORE_N", threshold=20, model_p=0.60,
         yes_bid=0.62, yes_ask=0.64),
    dict(ticker="KXNFLPASSYDS-25SEP04DALPHI-PHIJHURTS1-150", family="PLAYER_STAT", stat="passing_yards",
         threshold=150, player_id=HURTS, player_name="Jalen Hurts", model_p=0.58, yes_bid=0.54, yes_ask=0.56),
    dict(ticker="KXNFLANYTD-25SEP04DALPHI-PHIJHURTS1", family="PLAYER_STAT", stat="touchdowns", threshold=1,
         player_id=HURTS, player_name="Jalen Hurts", model_p=0.45, yes_bid=0.42, yes_ask=0.45),
    dict(ticker="KXNFLREC-25SEP04DALPHI-DALCLAMB88-8", family="PLAYER_STAT", stat="receptions", threshold=8,
         player_id=LAMB, player_name="CeeDee Lamb", model_p=0.40, yes_bid=0.36, yes_ask=0.39),
    dict(ticker="KXNFLRSHYDS-25SEP04DALPHI-PHISBARKLEY26-60", family="PLAYER_STAT", stat="rushing_yards",
         threshold=60, player_id=BARKLEY, player_name="Saquon Barkley", model_p=0.50, yes_bid=0.48,
         yes_ask=0.51),
    # a scratched-or-benched player: absent from the complete snap table, so settlement is refused
    dict(ticker="KXNFLRECYDS-25SEP04DALPHI-PHIGHOST99-30", family="PLAYER_STAT", stat="receiving_yards",
         threshold=30, player_id=NOBODY, player_name="Never Played", model_p=0.30, yes_bid=0.10,
         yes_ask=0.14),
    # active, never took a snap: settles at the exchange's own scalar value and at nothing else
    dict(ticker="KXNFLREC-25SEP04DALPHI-PHIDRESSED88-2", family="PLAYER_STAT", stat="receptions", threshold=2,
         player_id=DRESSED, player_name="Dressed Never Played", model_p=0.22, yes_bid=0.18, yes_ask=0.21),
    # a family the pricer prices but settlement cannot prove
    dict(ticker="KXNFLWINMARGIN-25SEP04DALPHI-PHI1", family="WIN_MARGIN_BUCKET", operator="range",
         team="PHI", model_p=0.20, yes_bid=0.18, yes_ask=0.22),
]


# Kalshi's own recorded settlement per ticker, as a post-game capture row would carry it. It agrees with the
# real result everywhere, so a test that changes one entry is testing disagreement handling and nothing else.
KALSHI_RESULT = {
    "KXNFLGAME-25SEP04DALPHI-PHI": "yes",
    "KXNFLSPREAD-25SEP04DALPHI-PHI4": "yes",
    "KXNFLTOTAL-25SEP04DALPHI-45": "no",
    "KXNFLTEAMTOTAL-25SEP04DALPHI-PHI24": "yes",
    "KXNFLBOTH-25SEP04DALPHI-20": "yes",
    "KXNFLPASSYDS-25SEP04DALPHI-PHIJHURTS1-150": "yes",
    "KXNFLANYTD-25SEP04DALPHI-PHIJHURTS1": "yes",
    "KXNFLREC-25SEP04DALPHI-DALCLAMB88-8": "no",
    "KXNFLRSHYDS-25SEP04DALPHI-PHISBARKLEY26-60": "yes",
    "KXNFLRECYDS-25SEP04DALPHI-PHIGHOST99-30": "no",
    "KXNFLREC-25SEP04DALPHI-PHIDRESSED88-2": "scalar",
    "KXNFLWINMARGIN-25SEP04DALPHI-PHI1": "no",
}
# the exchange's published scalar value for the no-snap market. Deliberately nowhere near the pregame midpoint
# (0.195), so a test that passes cannot be passing because the two happen to agree.
SCALAR_VALUE = "0.0400"


def pin_snapshot(md, *, kalshi_result=None, scalar_value=SCALAR_VALUE, markets=None, status="finalized"):
    """Write a settlement snapshot as a previous run would have pinned it, into the published corpus."""
    kalshi_result = KALSHI_RESULT if kalshi_result is None else kalshi_result
    recs = {}
    for t in (markets if markets is not None else list(kalshi_result)):
        res = kalshi_result.get(t)
        if not res:
            continue
        rec = {"ticker": t, "result": res, "status": status, "source": "kalshi_settlement_snapshot",
               "settlement_ts": "2025-09-05T04:30:00Z"}
        if res == "scalar" and scalar_value is not None:
            rec["settlement_value_dollars"] = scalar_value
        recs[t] = rec
    d = os.path.join(md, "data", "shadow", "evaluations", GAME)
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, "eval-1.0.0.PINNED.kalshi_settlement_snapshot.json")
    with open(path, "w") as f:
        json.dump({"game_id": GAME, "captured_at": "2025-09-05T05:00:00+00:00", "markets": recs,
                   "n_markets": len(recs), "fetch_meta": [{"note": "fixture"}]}, f)
    return path


def build_market_data(tmp_path, *, kalshi_result=None, markets=None):
    kalshi_result = KALSHI_RESULT if kalshi_result is None else kalshi_result
    markets = MARKETS if markets is None else markets
    md = tmp_path / "md"
    ledger_root = md / "data" / "shadow" / "ledger"
    capture_root = md / "data" / "kalshi" / "capture"
    preds = []
    for run_id, observed_at, mtk in SNAPSHOTS:
        day = observed_at[:10]
        os.makedirs(ledger_root / day, exist_ok=True)
        rows = []
        for i, m in enumerate(markets):
            pid = hashlib.sha1(f"{run_id}|{m['ticker']}".encode()).hexdigest()[:20]
            rows.append(observation(pid, run_id=run_id, observed_at=observed_at, minutes_to_kickoff=mtk,
                                    **{k: v for k, v in m.items() if k != "ticker"}, ticker=m["ticker"]))
            preds.append(pid)
        # rows the pricer refused: no model probability, so nothing to evaluate
        rows.append(observation("unsup-" + run_id, "KXNFLRACE-25SEP04DALPHI-35", run_id=run_id,
                                observed_at=observed_at, minutes_to_kickoff=mtk, family="RACE_TO_N",
                                model_p=None, yes_bid=0.2, yes_ask=0.3, support_state="UNSUPPORTED_RULES"))
        rows.append(observation("stale-" + run_id, "KXNFLTOTAL-25SEP04DALPHI-51", run_id=run_id,
                                observed_at=observed_at, minutes_to_kickoff=mtk, family="TOTAL",
                                model_p=0.3, yes_bid=0.2, yes_ask=0.3, support_state="STALE_DATA"))
        # a different game, still pending: its predictions must produce nothing at all
        rows.append(observation("pending-" + run_id, "KXNFLGAME-26SEP09NESEA-SEA", run_id=run_id,
                                observed_at=observed_at, minutes_to_kickoff=mtk, family="GAME_WINNER",
                                model_p=0.6, yes_bid=0.61, yes_ask=0.62, game_id=PENDING_GAME,
                                operator="event", team="SEA", kickoff_utc="2026-09-10T00:20:00+00:00"))
        with gzip.open(ledger_root / day / f"{run_id}.shadow-0.4.0.observations.jsonl.gz", "wt") as f:
            for r in rows:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")

    # capture: a pregame path per ticker, an in-game quote that must never be the close, and Kalshi's own
    # settlement afterwards
    def quote(ticker, day, hhmm, yb, ya, **kw):
        row = {"run_id": f"{day.replace('-', '')}T{hhmm.replace(':', '')}00Z",
               "observed_at": f"{day}T{hhmm}:00+00:00", "ticker": ticker, "game_id": GAME,
               "event_ticker": ticker.rsplit("-", 1)[0], "series_ticker": ticker.split("-")[0],
               "yes_bid_dollars": f"{yb:.4f}", "yes_ask_dollars": f"{ya:.4f}",
               "no_bid_dollars": f"{1 - ya:.4f}", "no_ask_dollars": f"{1 - yb:.4f}",
               "last_price_dollars": f"{ya:.4f}", "volume_fp": "5000.00", "open_interest_fp": "4000.00",
               "liquidity_dollars": "300.0000", "status": "active", "result": "", "kickoff_utc": KICKOFF,
               "pregame": True}
        row.update(kw)
        return row

    files = {}
    for m in markets:
        t = m["ticker"]
        yb, ya = m["yes_bid"], m["yes_ask"]
        files.setdefault("2025-09-03", []).append(quote(t, "2025-09-03", "20:05", yb - 0.03, ya - 0.03))
        files.setdefault("2025-09-04", []).extend([
            quote(t, "2025-09-04", "18:05", yb, ya),
            quote(t, "2025-09-04", "23:55", yb + 0.04, ya + 0.04),          # THE close, 25 minutes out
            quote(t, "2025-09-05", "00:45", 0.95, 0.97, pregame=False),     # in-game
        ])
        files.setdefault("2025-09-05", []).append(
            quote(t, "2025-09-05", "05:00", 0.99, 1.0, pregame=False, status="finalized",
                  result=kalshi_result.get(t, "no")))
    for day, rows in files.items():
        os.makedirs(capture_root / day, exist_ok=True)
        by_run = {}
        for r in rows:
            by_run.setdefault(r["run_id"], []).append(r)
        for run, rs in by_run.items():
            with open(capture_root / day / f"{run}.quotes.jsonl", "w") as f:
                for r in rs:
                    f.write(json.dumps(r, separators=(",", ":")) + "\n")
    return str(md), preds


def result_book(*, score_override=None, complete=True):
    from nfl_edge.settlement.results import result_book_from_records
    with open(FIXTURE) as f:
        rec = json.load(f)
    rec["game_id"] = GAME
    if score_override:
        lines = rec["schedule_csv"].splitlines()
        h = lines[0].split(",")
        ia, ih, ir, it = h.index("away_score"), h.index("home_score"), h.index("result"), h.index("total")
        out = []
        for line in lines[1:]:
            c = line.split(",")
            if c[0] == GAME:
                c[ia], c[ih] = str(score_override[0]), str(score_override[1])
                c[ir] = str(score_override[1] - score_override[0])
                c[it] = str(sum(score_override))
            out.append(",".join(c))
        rec["schedule_csv"] = "\n".join([lines[0]] + out)
    if not complete:
        rec["games_with_player_stats"] = []
    rec.setdefault("snaps", []).append(
        {"player_id": DRESSED, "game_id": GAME, "player_name": "Dressed Never Played", "team": "PHI",
         "offense_snaps": 0.0, "defense_snaps": 0.0, "st_snaps": 0.0})
    return result_book_from_records(rec, min_hours_after_kickoff=4.0)


def run_settle(monkeypatch, md, out, *extra, book=None):
    """Run the real main(). Both network readers are switched OFF: a test must never depend on the exchange or
    on ESPN being reachable, and the evidence they would supply is injected as fixtures instead."""
    monkeypatch.setattr(settle_games, "build_result_book", lambda *a, **k: book or result_book())
    argv = ["settle_games.py", "--market-data", md, "--out", str(out),
            "--scorecard-out", str(out) + "-scorecards", "--game", GAME, "--game", PENDING_GAME,
            "--no-espn-final", "--no-exchange-fetch", *extra]
    monkeypatch.setattr(sys, "argv", argv)
    return settle_games.main()


def tree_digest(root):
    return {os.path.relpath(p, root): hashlib.sha256(open(p, "rb").read()).hexdigest()
            for p in sorted(glob.glob(os.path.join(root, "**", "*"), recursive=True)) if os.path.isfile(p)}


def corpus_rows(out):
    from nfl_edge.shadow import evaluation_store as ST
    return ST.read_corpus([str(out)])


# ---------------------------------------------------------------------------- tests
@pytest.fixture
def built(tmp_path, monkeypatch):
    md, preds = build_market_data(tmp_path)
    pin_snapshot(md)
    out = tmp_path / "evaluations"
    before = tree_digest(md)
    rc = run_settle(monkeypatch, md, out)
    return {"md": md, "out": out, "preds": preds, "rc": rc, "ledger_before": before}


def test_the_run_settles_the_final_game_and_writes_one_batch(built):
    assert built["rc"] == 0
    rows = corpus_rows(built["out"])
    assert len(rows) == len(MARKETS) * len(SNAPSHOTS)
    assert {r["game_id"] for r in rows} == {GAME}
    batches = glob.glob(os.path.join(str(built["out"]), GAME, "*.evaluations.jsonl.gz"))
    assert len(batches) == 1
    assert os.path.exists(batches[0].replace(".evaluations.jsonl.gz", ".evaluation_manifest.json"))


def test_a_game_that_is_not_final_produces_nothing_at_all(built):
    assert not os.path.exists(os.path.join(str(built["out"]), PENDING_GAME)), (
        "a deferred game must not get a directory, a batch, or a row of refusals")
    assert PENDING_GAME not in {r["game_id"] for r in corpus_rows(built["out"])}


def test_rows_the_pricer_refused_are_not_evaluated(built):
    tickers = {r["ticker"] for r in corpus_rows(built["out"])}
    assert "KXNFLRACE-25SEP04DALPHI-35" not in tickers, "an UNSUPPORTED_RULES row carries no prediction"
    assert "KXNFLTOTAL-25SEP04DALPHI-51" not in tickers, "a STALE_DATA row carries no prediction"


def test_every_settlement_matches_the_real_result(built):
    by_ticker = {}
    for r in corpus_rows(built["out"]):
        by_ticker.setdefault(r["ticker"], []).append(r)
    expected = {
        "KXNFLGAME-25SEP04DALPHI-PHI": 1.0,                        # PHI won 24-20
        "KXNFLSPREAD-25SEP04DALPHI-PHI4": 1.0,                     # by 4, more than 3.5
        "KXNFLTOTAL-25SEP04DALPHI-45": 0.0,                        # 44 points
        "KXNFLTEAMTOTAL-25SEP04DALPHI-PHI24": 1.0,                 # PHI scored 24
        "KXNFLBOTH-25SEP04DALPHI-20": 1.0,                         # DAL 20, PHI 24
        "KXNFLPASSYDS-25SEP04DALPHI-PHIJHURTS1-150": 1.0,          # Hurts 152
        "KXNFLANYTD-25SEP04DALPHI-PHIJHURTS1": 1.0,                # two rushing touchdowns
        "KXNFLREC-25SEP04DALPHI-DALCLAMB88-8": 0.0,                # Lamb 7 receptions
        "KXNFLRSHYDS-25SEP04DALPHI-PHISBARKLEY26-60": 1.0,         # Barkley 60 rushing yards
    }
    for ticker, payout in expected.items():
        for r in by_ticker[ticker]:
            assert r["settlement_status"] == "SETTLED", (ticker, r["settlement_reason"])
            assert r["settled_yes"] == payout, ticker
            assert r["settlement_kind"] == "binary"
            assert r["settlement_evidence"]["home_score"] == 24.0


def test_what_cannot_be_proven_is_refused_with_a_reason_and_no_payout(built):
    rows = {r["ticker"]: r for r in corpus_rows(built["out"])}
    ghost = rows["KXNFLRECYDS-25SEP04DALPHI-PHIGHOST99-30"]
    assert ghost["settlement_status"] == "REFUSED_PARTICIPATION_UNPROVEN"
    assert ghost["settled_yes"] is None and "INACTIVE" in ghost["settlement_reason"]
    margin = rows["KXNFLWINMARGIN-25SEP04DALPHI-PHI1"]
    assert margin["settlement_status"] == "REFUSED_UNSUPPORTED_FAMILY" and margin["settled_yes"] is None


def test_the_recorded_candidate_count_is_the_pregame_history_only(built):
    rows = [r for r in corpus_rows(built["out"]) if r["ticker"] == "KXNFLGAME-25SEP04DALPHI-PHI"]
    # three pregame quotes were captured for each ticker; the in-game and post-game rows are not candidates
    assert {r["close_candidates_seen"] for r in rows} == {3}


def test_the_close_is_the_last_pregame_quote_and_clv_is_signed_by_our_view(built):
    rows = [r for r in corpus_rows(built["out"])
            if r["ticker"] == "KXNFLGAME-25SEP04DALPHI-PHI"]
    assert {r["close_observed_at"] for r in rows} == {"2025-09-04T23:55:00+00:00"}, (
        "every snapshot of a ticker is evaluated against the same, single close")
    for r in rows:
        assert r["close_status"] == "OK" and r["close_is_stale"] is False
        assert 24.0 < r["close_minutes_to_kickoff"] < 26.0
        assert r["close_mid"] == pytest.approx(0.62)
        # the model was above the mid and the market moved up: movement toward us, positive CLV
        assert r["movement"] == "toward" and r["signed_clv_mid"] > 0
        assert r["model_direction"] == "yes"
        assert r["signed_clv_executable"] == pytest.approx(0.63 - 0.59)


def test_each_snapshot_is_banded_by_its_own_distance_to_kickoff(built):
    rows = [r for r in corpus_rows(built["out"]) if r["ticker"] == "KXNFLTOTAL-25SEP04DALPHI-45"]
    # the snapshots sit 1700, 380 and 30 minutes out
    assert {r["horizon_band"] for r in rows} == {">24h", "6-24h", "30-90m"}
    assert all(r["disagreement_band"] for r in rows)


def test_the_original_ledger_and_capture_are_byte_identical_afterwards(built):
    assert tree_digest(built["md"]) == built["ledger_before"], (
        "the settle run must only READ the published ledger and capture")


def test_the_manifest_records_provenance_and_checksums(built):
    man_path = glob.glob(os.path.join(str(built["out"]), GAME, "*.evaluation_manifest.json"))[0]
    man = json.load(open(man_path))
    from nfl_edge.shadow import evaluation_store as ST
    batch = man_path.replace(".evaluation_manifest.json", ".evaluations.jsonl.gz")
    assert man["evaluations_sha256"] == ST.sha256_file(batch)
    assert man["written"] == len(MARKETS) * len(SNAPSHOTS)
    assert man["kickoff_utc"] == KICKOFF and man["kickoff_source"] == "schedule"
    assert man["game_evidence"]["home_score"] == 24.0
    assert sorted(man["ledger_snapshots"]) == [s[0] for s in SNAPSHOTS]
    # nine binary settlements plus the exchange-scalar one; the two refusals are counted under their own status
    assert man["by_settlement_status"]["SETTLED"] == 10 * len(SNAPSHOTS)
    assert man["result_sources"] and man["by_settlement_reason"]


def test_the_exchanges_own_settlements_are_cross_checked_but_never_substituted(built):
    path = glob.glob(os.path.join(str(built["out"]), GAME, "*.kalshi_crosscheck.json"))
    assert path, "the cross-check artifact is written next to the batch"
    cross = json.load(open(path[0]))
    assert cross["tickers_compared"] == len(MARKETS)
    assert cross["agree"] == 10 and cross["disagree"] == 0
    assert cross["not_comparable"] == 2, "the two refusals cannot be compared to a payout"
    rows = corpus_rows(built["out"])
    assert all((r.get("settlement_source") or "").startswith("nflverse") for r in rows
               if r["settlement_status"] == "SETTLED" and r["settlement_kind"] == "binary"), (
        "a binary settlement is proven from nflverse; the exchange is never its source of truth")


def test_an_exchange_settlement_that_contradicts_the_result_is_surfaced_not_adopted(tmp_path, monkeypatch):
    """The exchange settled four 2025 markets against their games' own final scores. Ours must stand, visibly."""
    wrong = dict(KALSHI_RESULT, **{"KXNFLTOTAL-25SEP04DALPHI-45": "yes"})   # 44 points is not 45+
    md, _ = build_market_data(tmp_path)
    pin_snapshot(md, kalshi_result=wrong)
    out = tmp_path / "evaluations"
    assert run_settle(monkeypatch, md, out) == 0
    cross = json.load(open(glob.glob(os.path.join(str(out), GAME, "*.kalshi_crosscheck.json"))[0]))
    assert cross["disagree"] == 1
    assert cross["disagreements"][0]["ticker"] == "KXNFLTOTAL-25SEP04DALPHI-45"
    assert cross["disagreements"][0]["ours"] == 0.0 and cross["disagreements"][0]["exchange_result"] == "yes"
    rows = [r for r in corpus_rows(out) if r["ticker"] == "KXNFLTOTAL-25SEP04DALPHI-45"]
    assert {r["settled_yes"] for r in rows} == {0.0}, "the proven settlement is what gets written"


# ---------------------------------------------------------------------------- the scalar branch
SCALAR_TICKER = "KXNFLREC-25SEP04DALPHI-PHIDRESSED88-2"


def test_the_no_snap_branch_settles_at_the_exchanges_exact_value_not_a_midpoint(built):
    rows = [r for r in corpus_rows(built["out"]) if r["ticker"] == SCALAR_TICKER]
    assert rows
    for r in rows:
        assert r["settlement_status"] == "SETTLED" and r["settlement_kind"] == "scalar_exact"
        assert r["settled_yes"] == 0.04, "the exchange's published settlement_value_dollars, and nothing else"
        assert r["settlement_evidence"]["participation_branch"] == "active_no_snap_proven"
        assert r["exact_payout_known"] is True
        assert r["exact_payout_source"] == "kalshi_settlement_snapshot"
        # the midpoint is 0.195 and is still recorded -- as a quote, never as the payout
        assert r["mid_t"] == pytest.approx(0.195)
        assert abs(r["settled_yes"] - r["mid_t"]) > 0.15, (
            "the exact payout is nowhere near the midpoint, so this test cannot pass by coincidence")
        assert r["close_mid"] is not None, "the pregame close stays in the close fields as research evidence"


def test_a_scalar_dependent_game_defers_while_the_exchange_has_no_terminal_settlement(tmp_path, monkeypatch, capsys):
    """The retryability rule. One player needs the exchange's scalar; nothing terminal is available; so the whole
    game waits. Writing a permanent "unavailable" for a market that is about to settle would be a lie frozen in
    an immutable corpus, and the next scheduled run costs nothing."""
    md, _ = build_market_data(tmp_path)                     # no pinned snapshot, and fetching is disabled
    out = tmp_path / "evaluations"
    assert run_settle(monkeypatch, md, out) == 0
    assert not glob.glob(os.path.join(str(out), "*", "*.evaluations.jsonl.gz")), (
        "no batch may be written for a game whose exchange evidence is still pending")
    assert not glob.glob(os.path.join(str(out), "*", f"*.{KS.SNAPSHOT_SUFFIX}")), (
        "and nothing may be pinned: a failed acquisition is not evidence")
    printed = capsys.readouterr().out
    assert "DEFER_EXCHANGE_SETTLEMENT_PENDING" in printed


def test_a_game_with_no_scalar_dependency_evaluates_even_when_the_exchange_is_unreachable(tmp_path, monkeypatch):
    """Binary football truth is nflverse-derived, so an exchange outage must not hold it hostage."""
    without_scalar = [m for m in MARKETS if m["ticker"] != SCALAR_TICKER]
    md, _ = build_market_data(tmp_path, markets=without_scalar)
    out = tmp_path / "evaluations"

    def unreachable(*a, **k):
        raise OSError("no route to host")
    monkeypatch.setattr(settle_games.KS, "fetch_game_settlements", unreachable)
    argv = ["settle_games.py", "--market-data", md, "--out", str(out),
            "--scorecard-out", str(out) + "-sc", "--game", GAME, "--game", PENDING_GAME, "--no-espn-final"]
    monkeypatch.setattr(settle_games, "build_result_book", lambda *a, **k: result_book())
    monkeypatch.setattr(sys, "argv", argv)
    assert settle_games.main() == 0
    rows = corpus_rows(out)
    assert len(rows) == len(without_scalar) * len(SNAPSHOTS), "the game settles in full"
    assert not glob.glob(os.path.join(str(out), "*", f"*.{KS.SNAPSHOT_SUFFIX}")), (
        "an unreachable exchange pins nothing, and nothing needed it")
    assert {r["settlement_status"] for r in rows} >= {"SETTLED"}


def test_a_network_failure_never_pins_an_empty_snapshot(tmp_path, monkeypatch):
    md, _ = build_market_data(tmp_path)
    out = tmp_path / "evaluations"

    def unreachable(*a, **k):
        raise OSError("connection reset")
    monkeypatch.setattr(settle_games.KS, "fetch_game_settlements", unreachable)
    argv = ["settle_games.py", "--market-data", md, "--out", str(out),
            "--scorecard-out", str(out) + "-sc", "--game", GAME, "--no-espn-final"]
    monkeypatch.setattr(settle_games, "build_result_book", lambda *a, **k: result_book())
    monkeypatch.setattr(sys, "argv", argv)
    assert settle_games.main() == 0
    assert not glob.glob(os.path.join(str(out), "*", "*")), (
        "a transient failure must leave no artifact at all -- not a batch, and not an empty snapshot")


def test_a_partial_exchange_read_is_not_frozen_as_complete(tmp_path, monkeypatch):
    """Some markets coming back is not completeness. A partial page is a retryable state."""
    md, _ = build_market_data(tmp_path)
    out = tmp_path / "evaluations"

    def partial(*a, **k):
        # the scalar market is terminal and present, but the read itself did not complete
        return KS.FetchOutcome(markets=[{"ticker": SCALAR_TICKER, "result": "scalar", "status": "finalized",
                                        "settlement_value_dollars": "0.0400"}],
                              meta=[{"event_ticker": "E", "complete": False}], complete=False, errors=0)
    monkeypatch.setattr(settle_games.KS, "fetch_game_settlements", partial)
    argv = ["settle_games.py", "--market-data", md, "--out", str(out),
            "--scorecard-out", str(out) + "-sc", "--game", GAME, "--no-espn-final"]
    monkeypatch.setattr(settle_games, "build_result_book", lambda *a, **k: result_book())
    monkeypatch.setattr(sys, "argv", argv)
    assert settle_games.main() == 0
    assert not glob.glob(os.path.join(str(out), "*", "*")), "an incomplete read pins nothing and writes nothing"


def test_a_determined_but_not_finalized_market_defers_rather_than_settling(tmp_path, monkeypatch, capsys):
    """`result=scalar` on a DETERMINED market is not settlement evidence: it can still be amended."""
    md, _ = build_market_data(tmp_path)
    pin_snapshot(md, status="determined")
    out = tmp_path / "evaluations"
    assert run_settle(monkeypatch, md, out) == 0
    assert not glob.glob(os.path.join(str(out), "*", "*.evaluations.jsonl.gz"))
    assert "DEFER_EXCHANGE_SETTLEMENT_PENDING" in capsys.readouterr().out


def test_the_next_run_settles_the_same_game_once_the_finalized_scalar_appears(tmp_path, monkeypatch):
    """The point of deferring instead of refusing: the game is still evaluable later."""
    md, _ = build_market_data(tmp_path)
    out = tmp_path / "evaluations"
    assert run_settle(monkeypatch, md, out) == 0
    assert not glob.glob(os.path.join(str(out), "*", "*.evaluations.jsonl.gz")), "first run defers"

    pin_snapshot(md)                                        # the exchange finalises; a later run finds it
    assert run_settle(monkeypatch, md, out) == 0
    rows = corpus_rows(out)
    assert len(rows) == len(MARKETS) * len(SNAPSHOTS), "the second run writes the whole game"
    scalar = [r for r in rows if r["ticker"] == SCALAR_TICKER]
    assert {r["settled_yes"] for r in scalar} == {0.04}
    assert {r["settlement_kind"] for r in scalar} == {"scalar_exact"}


def test_a_terminally_finalized_scalar_with_no_published_value_is_refused_not_deferred(tmp_path, monkeypatch):
    """A terminal evidence deficiency, not a transient one: the exchange finished and published no number."""
    md, _ = build_market_data(tmp_path)
    pin_snapshot(md, scalar_value=None)                     # finalized, result=scalar, no value
    out = tmp_path / "evaluations"
    assert run_settle(monkeypatch, md, out) == 0
    rows = [r for r in corpus_rows(out) if r["ticker"] == SCALAR_TICKER]
    assert rows, "the game is NOT deferred: nothing more will arrive"
    for r in rows:
        assert r["settlement_status"] == "REFUSED_EXACT_SCALAR_PAYOUT_UNAVAILABLE"
        assert r["settled_yes"] is None
        assert r["settlement_evidence"]["participation_branch"] == "active_no_snap_proven"


def test_a_pinned_snapshot_records_the_tickers_it_had_to_cover(built):
    """Completeness is a claim the snapshot makes explicitly, so a partial fetch cannot imply it."""
    md_snaps = glob.glob(os.path.join(built["md"], "data", "shadow", "evaluations", GAME,
                                     f"*.{KS.SNAPSHOT_SUFFIX}"))
    assert md_snaps, "the fixture pins one"
    man = json.load(open(glob.glob(os.path.join(str(built["out"]), GAME,
                                               "*.evaluation_manifest.json"))[0]))
    ev = man["exchange_evidence"]
    assert ev["scalar_dependent_tickers"] == [SCALAR_TICKER]
    assert ev["terminal_records_held"] >= len(MARKETS)
    assert ev["snapshot_pinned_this_batch"] is False, "the pinned evidence was reused, not re-frozen"


def test_the_pinned_snapshot_is_not_refetched_on_a_later_run(built, monkeypatch):
    """Pinned evidence is read, never re-read from the network: that is what makes a refusal reproducible."""
    calls = []

    def _boom(*a, **k):
        calls.append(1)
        return [], []
    monkeypatch.setattr(settle_games.KS, "fetch_game_settlements", _boom)
    before = tree_digest(str(built["out"]))
    assert run_settle(monkeypatch, built["md"], built["out"]) == 0
    assert calls == [], "a pinned snapshot must not trigger another exchange read"
    assert tree_digest(str(built["out"])) == before


def test_the_scorecard_reports_sample_units_and_scores_both_spaces(built):
    d = glob.glob(os.path.join(str(built["out"]) + "-scorecards", "*"))
    assert d, "a scorecard directory is written"
    sc = json.load(open(os.path.join(d[0], "scorecard.json")))
    raw, con = sc["sample_units"]["raw"], sc["sample_units"]["latest_pregame"]
    assert raw["n_observations"] == len(MARKETS) * len(SNAPSHOTS)
    assert raw["n_unique_contracts"] == len(MARKETS) and raw["n_games"] == 1
    assert con["n_observations"] == len(MARKETS), "one row per contract in the primary view"
    assert sc["primary_sample_unit"] == "latest_pregame"
    view = sc["views"]["latest_pregame"]
    assert view["event_calibration"]["model_event_probability"]["n"] > 0
    assert "brier" in view["event_calibration"]["model_event_probability"]
    payout = view["contract_payout_quality"]
    assert payout["model_contract_value"]["n"] > 0
    assert "mean_squared_payout_error" in payout["model_contract_value"]
    assert "log_loss" not in payout["model_contract_value"], "a payout error is not a log loss"
    assert payout["market_at_snapshot"]["n"] == payout["model_contract_value"]["n"]
    assert set(sc["horizons"]) >= {"T-24h", "T-6h", "T-90m", "T-30m", "latest pregame"}
    report = open(os.path.join(d[0], "REPORT.md")).read()
    assert "Event-probability calibration" in report and "Contract-payout quality" in report
    assert "Canonical horizons" in report and "No effective N is computed" in report


def test_the_validator_passes_on_what_the_run_produced(built, monkeypatch):
    monkeypatch.setattr(sys, "argv", ["validate_evaluations.py", "--root", str(built["out"]),
                                      "--market-data", built["md"], "--require-rows"])
    assert validate_evaluations.main() == 0


def test_the_validator_rejects_a_refusal_that_carries_a_payout(built, monkeypatch, tmp_path):
    """The defect that would poison every calibration number: a guess wearing a refusal's label."""
    from nfl_edge.shadow import evaluation_store as ST
    path = glob.glob(os.path.join(str(built["out"]), GAME, "*.evaluations.jsonl.gz"))[0]
    rows = ST.read_rows(path)
    for r in rows:
        if r["settlement_status"] != "SETTLED":
            r["settled_yes"] = 0.0
            r["content_hash"] = ST.content_hash(r)
    with gzip.open(path, "wt") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    man_path = path.replace(".evaluations.jsonl.gz", ".evaluation_manifest.json")
    man = json.load(open(man_path))
    man["evaluations_sha256"] = ST.sha256_file(path)
    json.dump(man, open(man_path, "w"))
    monkeypatch.setattr(sys, "argv", ["validate_evaluations.py", "--root", str(built["out"])])
    assert validate_evaluations.main() == 2


def _tamper(built, mutate):
    """Rewrite the published batch through a mutation, keeping hashes and the manifest self-consistent, so the
    validator is tested on its invariants rather than on a checksum mismatch."""
    from nfl_edge.shadow import evaluation_store as ST
    path = glob.glob(os.path.join(str(built["out"]), GAME, "*.evaluations.jsonl.gz"))[0]
    rows = ST.read_rows(path)
    for r in rows:
        mutate(r)
        r["content_hash"] = ST.content_hash(r)
    with gzip.open(path, "wt") as f:
        for r in rows:
            f.write(json.dumps(r, sort_keys=True) + "\n")
    man_path = path.replace(".evaluations.jsonl.gz", ".evaluation_manifest.json")
    man = json.load(open(man_path))
    man["evaluations_sha256"] = ST.sha256_file(path)
    json.dump(man, open(man_path, "w"))


def _drop_scalar_source(r):
    if r.get("settlement_kind") == "scalar_exact":
        r["exact_payout_source"] = None


def _drop_final_proofs(r):
    ev = r.get("settlement_evidence") or {}
    if ev.get("final_proofs"):
        ev["final_proofs"] = []


def _claim_exact_on_a_refusal(r):
    if r.get("settlement_status") != "SETTLED":
        r["exact_payout_known"] = True


def _erase_the_event_probability(r):
    r["model_event_probability"] = None


@pytest.mark.parametrize("mutate,expected", [
    (_drop_scalar_source, "no exchange source"),
    (_drop_final_proofs, "no final-status proof"),
    (_claim_exact_on_a_refusal, "claims an exact payout"),
    (_erase_the_event_probability, "no event probability"),
], ids=["scalar payout with no provenance", "settled with no final proof",
        "refusal claiming an exact payout", "contract value with no event probability"])
def test_the_validator_rejects_each_way_a_row_could_lie(built, monkeypatch, mutate, expected):
    _tamper(built, mutate)
    monkeypatch.setattr(sys, "argv", ["validate_evaluations.py", "--root", str(built["out"])])
    assert validate_evaluations.main() == 2, f"the validator accepted a row it should reject ({expected})"


def test_a_rerun_with_identical_evidence_writes_nothing(built, monkeypatch):
    before = tree_digest(str(built["out"]))
    rc = run_settle(monkeypatch, built["md"], built["out"])
    assert rc == 0
    assert tree_digest(str(built["out"])) == before, (
        "a no-op rerun must leave the corpus byte-identical -- not even a run summary")


def test_a_rerun_after_more_captures_arrived_is_still_a_no_op(built, monkeypatch, tmp_path):
    """The capture keeps writing through the evening. A rerun the next morning sees MORE rows for the game, and
    must still recognise its own work: anything counted from "how many rows are on disk now" would turn an
    identical truth into a conflict."""
    md = built["md"]
    day = os.path.join(md, "data", "kalshi", "capture", "2025-09-05")
    with open(os.path.join(day, "20250905T090000Z.quotes.jsonl"), "w") as f:
        for m in MARKETS:                                  # post-game rows, arriving after the first run
            f.write(json.dumps({"run_id": "20250905T090000Z", "observed_at": "2025-09-05T09:00:00+00:00",
                                "ticker": m["ticker"], "game_id": GAME, "yes_bid_dollars": "0.9900",
                                "yes_ask_dollars": "1.0000", "status": "finalized", "result": "yes",
                                "kickoff_utc": KICKOFF, "pregame": False}, separators=(",", ":")) + "\n")
    before = tree_digest(str(built["out"]))
    assert run_settle(monkeypatch, md, built["out"]) == 0
    after = tree_digest(str(built["out"]))
    assert {k for k in after if k.endswith(".evaluations.jsonl.gz")} == \
        {k for k in before if k.endswith(".evaluations.jsonl.gz")}


def test_a_rerun_with_a_differently_populated_result_book_is_still_a_no_op(built, monkeypatch):
    """Downloading another season changes which files the result book lists as present or missing. That is
    provenance about the RUN, not about the prediction, so it must not sit inside the hashed row."""
    book = result_book()
    book.sources["missing"] = ["data/raw/nflverse/stats_player/stats_player_week_2024.parquet"]
    book.sources["pfr_crosswalk"] = "silver/player_crosswalk.parquet"
    before = tree_digest(str(built["out"]))
    assert run_settle(monkeypatch, built["md"], built["out"], book=book) == 0
    assert tree_digest(str(built["out"])) == before


def test_a_rerun_whose_evidence_changed_fails_with_a_conflict_and_writes_nothing(built, monkeypatch):
    before = tree_digest(str(built["out"]))
    rc = run_settle(monkeypatch, built["md"], built["out"], book=result_book(score_override=(31, 3)))
    assert rc == 4, "a contradicted truth must fail the run"
    after = tree_digest(str(built["out"]))
    batches_before = {k for k in before if k.endswith(".evaluations.jsonl.gz")}
    batches_after = {k for k in after if k.endswith(".evaluations.jsonl.gz")}
    assert batches_after == batches_before
    for k in batches_before:
        assert after[k] == before[k]
    rows = corpus_rows(built["out"])
    assert {r["settled_yes"] for r in rows if r["ticker"] == "KXNFLGAME-25SEP04DALPHI-PHI"} == {1.0}


def test_the_validator_reports_when_it_could_not_check_the_published_ledger(built, monkeypatch, capsys):
    monkeypatch.setattr(sys, "argv", ["validate_evaluations.py", "--root", str(built["out"]),
                                      "--market-data", built["md"]])
    assert validate_evaluations.main() == 0
    out = capsys.readouterr().out
    assert '"published_ledger": "not_a_git_worktree"' in out, (
        "a check that did not run must never look like a check that passed")


def test_a_game_whose_player_statistics_are_pending_is_deferred_whole(tmp_path, monkeypatch):
    """Not "settle the team markets now and the player markets later": the game waits, entire."""
    md, _ = build_market_data(tmp_path)
    pin_snapshot(md)
    out = tmp_path / "evaluations"
    rc = run_settle(monkeypatch, md, out, book=result_book(complete=False))
    assert rc == 0
    assert not glob.glob(os.path.join(str(out), "*", "*.evaluations.jsonl.gz"))


def test_a_dry_run_reports_and_writes_nothing(tmp_path, monkeypatch):
    md, _ = build_market_data(tmp_path)
    pin_snapshot(md)
    out = tmp_path / "evaluations"
    rc = run_settle(monkeypatch, md, out, "--dry-run")
    assert rc == 0
    assert not glob.glob(os.path.join(str(out), "*", "*.evaluations.jsonl.gz"))


def test_a_kickoff_disagreement_stops_the_close_from_being_chosen(tmp_path, monkeypatch):
    """A wrong kickoff silently changes which quote is the close, so a disagreement refuses to pick one."""
    md, _ = build_market_data(tmp_path)
    pin_snapshot(md)
    ledger = glob.glob(os.path.join(md, "data", "shadow", "ledger", "*", "*.observations.jsonl.gz"))
    for path in ledger:
        rows = [json.loads(line) for line in gzip.open(path, "rt")]
        for r in rows:
            if r["game_id"] == GAME:
                r["kickoff_utc"] = "2025-09-04T17:00:00+00:00"      # three hours early
        with gzip.open(path, "wt") as f:
            for r in rows:
                f.write(json.dumps(r, separators=(",", ":")) + "\n")
    out = tmp_path / "evaluations"
    assert run_settle(monkeypatch, md, out) == 0
    rows = corpus_rows(out)
    assert rows and all(r["close_status"] == "MISSING_CLOSE" for r in rows)
    assert all("kickoff disagreement" in (r["notes"] or "") for r in rows)
    assert all(r["signed_clv_mid"] is None for r in rows)


def test_candidate_selection_only_looks_at_final_games_in_the_window():
    from datetime import datetime, timedelta, timezone
    book = result_book()
    now = datetime.fromisoformat(KICKOFF) + timedelta(days=2)
    chosen, (lo, hi) = settle_games.candidate_games(book, [], lookback_days=10.0, now=now)
    assert chosen == [GAME] and lo < KICKOFF[:10] <= hi
    later = datetime.now(timezone.utc)
    assert settle_games.candidate_games(book, [], lookback_days=10.0, now=later)[0] == [], (
        "a game outside the lookback window is not retried forever")


def test_the_observations_loader_never_opens_a_ledger_file_for_writing(tmp_path):
    md, _ = build_market_data(tmp_path)
    by_game, skipped, files = settle_games.load_observations(md, [GAME])
    assert len(by_game[GAME]) == len(MARKETS) * len(SNAPSHOTS)
    assert skipped["UNSUPPORTED_RULES"] == len(SNAPSHOTS) and skipped["STALE_DATA"] == len(SNAPSHOTS)
    for path in files:
        assert os.access(path, os.R_OK)
    original = copy.deepcopy(by_game[GAME][0])
    assert original["support_state"] == "SUPPORTED"
