"""Tape-recovery tests (#246): pagination past the old 10k cap, stop conditions, duplicates, partial windows, rate-limit resilience,
no post-anchor lookahead, side orientation, candle verification, resumable state, serialization."""
import json, os, sys, tempfile, unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "scripts", "kalshi"))
from nfl_edge.kalshi import tape as T                      # noqa: E402
import tape_repair as TR                                   # noqa: E402

ANCHOR = 1_760_000_000


def mk_trade(i, ts, yes=0.42, n=3.0, side="no"):
    return {"trade_id": f"t{i}", "created_time": T_iso(ts), "yes_price_dollars": f"{yes:.4f}", "no_price_dollars": f"{1 - yes:.4f}", "count_fp": f"{n:.2f}",
            "taker_side": side, "is_block_trade": False, "ticker": "TK"}


def T_iso(ts):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(ts, timezone.utc).strftime("%Y-%m-%dT%H:%M:%S.000000Z")


class FakeClient:
    """Newest-first paged tape with opaque cursors; can fail on a given page, ignore max_ts, or inject duplicates."""
    def __init__(self, trades, page=1000, fail_pages=(), ignore_max_ts=False, dup_boundary=False):
        self.all = sorted(trades, key=lambda t: t["created_time"], reverse=True)
        self.page, self.fail_pages, self.ignore, self.dup = page, set(fail_pages), ignore_max_ts, dup_boundary
        self.calls = 0
        class S:  # noqa
            requests = 0
            def to_dict(s): return {"requests": s.requests}
        self.stats = S()

    def try_get(self, path, params):
        self.calls += 1; self.stats.requests += 1
        rows = self.all if self.ignore or params.get("max_ts") is None else [t for t in self.all if T.to_ts(t["created_time"]) <= params["max_ts"]]
        start = int(params["cursor"]) if params.get("cursor") else 0
        if start // self.page in self.fail_pages and self.calls not in (0,):
            self.fail_pages.discard(start // self.page)
            return None, "429: rate limited"
        chunk = rows[start:start + self.page + (1 if self.dup and start else 0)] if not self.dup else rows[max(0, start - 1):start + self.page]
        nxt = start + self.page
        return {"trades": chunk, "cursor": str(nxt) if nxt < len(rows) else ""}, None


class Pagination(unittest.TestCase):
    def test_pages_past_the_old_10k_cap_and_marks_complete(self):
        tr = [mk_trade(i, ANCHOR - 10 - i) for i in range(25_500)]
        r = T.fetch_tape(FakeClient(tr), "TK", anchor_ts=ANCHOR, market_open_ts=ANCHOR - 40_000)
        self.assertEqual((r.n, r.pages, r.stop_reason, r.tape_complete), (25_500, 26, T.EXHAUSTED, True))
        self.assertIsNone(r.cursor)

    def test_page_budget_is_incomplete_and_resumable(self):
        tr = [mk_trade(i, ANCHOR - 10 - i) for i in range(5_000)]
        c = FakeClient(tr)
        r1 = T.fetch_tape(c, "TK", anchor_ts=ANCHOR, page_budget=2)
        self.assertEqual((r1.n, r1.stop_reason, r1.tape_complete), (2000, T.PAGE_BUDGET, False)); self.assertEqual(r1.cursor, "2000")
        r2 = T.fetch_tape(c, "TK", anchor_ts=ANCHOR, resume_cursor=r1.cursor, page_budget=10, known_ids={t["trade_id"] for t in r1.trades})
        self.assertEqual((r2.n, r2.tape_complete), (3000, True)); self.assertEqual(r1.n + r2.n, 5000)

    def test_rate_limit_error_keeps_the_failed_cursor_never_skips_a_page(self):
        tr = [mk_trade(i, ANCHOR - 10 - i) for i in range(3_000)]
        c = FakeClient(tr, fail_pages={1})
        r1 = T.fetch_tape(c, "TK", anchor_ts=ANCHOR)
        self.assertEqual((r1.n, r1.stop_reason, r1.tape_complete, r1.cursor), (1000, T.ERROR, False, "1000")); self.assertIn("429", r1.error)
        r2 = T.fetch_tape(c, "TK", anchor_ts=ANCHOR, resume_cursor=r1.cursor)
        self.assertEqual((r2.n, r2.tape_complete), (2000, True))

    def test_duplicates_across_page_boundaries_are_dropped_and_counted(self):
        tr = [mk_trade(i, ANCHOR - 10 - i) for i in range(2_500)]
        r = T.fetch_tape(FakeClient(tr, dup_boundary=True), "TK", anchor_ts=ANCHOR)
        self.assertEqual(r.n, 2_500); self.assertGreater(r.duplicates_dropped, 0)

    def test_no_post_anchor_lookahead_even_if_server_ignores_max_ts(self):
        tr = [mk_trade(i, ANCHOR - 100 + i) for i in range(200)]          # 100 before, 100 after the anchor
        r = T.fetch_tape(FakeClient(tr, ignore_max_ts=True), "TK", anchor_ts=ANCHOR)
        self.assertEqual(r.n, 101); self.assertTrue(all(T.to_ts(t["created_time"]) <= ANCHOR for t in r.trades))
        self.assertEqual(r.post_anchor_dropped, 99)

    def test_empty_tape_is_complete_not_an_error(self):
        r = T.fetch_tape(FakeClient([]), "TK", anchor_ts=ANCHOR)
        self.assertEqual((r.n, r.tape_complete, r.stop_reason), (0, True, T.EMPTY_PAGE))

    def test_side_orientation_is_preserved_verbatim(self):
        tr = [mk_trade(1, ANCHOR - 5, yes=0.30, side="no"), mk_trade(2, ANCHOR - 6, yes=0.31, side="yes")]
        r = T.fetch_tape(FakeClient(tr), "TK", anchor_ts=ANCHOR)
        got = {t["trade_id"]: (t["taker_side"], t["yes_price_dollars"], t["no_price_dollars"]) for t in r.trades}
        self.assertEqual(got["t1"], ("no", "0.3000", "0.7000")); self.assertEqual(got["t2"], ("yes", "0.3100", "0.6900"))


class CandleCheck(unittest.TestCase):
    def _candle(self, end, lo, hi, vol):
        return {"end_period_ts": end, "price": {"low": f"{lo:.4f}", "high": f"{hi:.4f}"}, "volume": f"{vol:.2f}"}

    def test_exact_agreement_is_verified(self):
        h = (ANCHOR // 3600 - 3) * 3600
        tr = [mk_trade(1, h - 1800, yes=0.40, n=5), mk_trade(2, h - 900, yes=0.45, n=7)]
        v = T.hourly_candle_vs_tape([self._candle(h, 0.40, 0.45, 12)], tr, ANCHOR)
        self.assertTrue(v["verified"]); self.assertEqual(v["hours_checked"], 1)

    def test_candle_volume_missing_from_tape_exposes_a_source_gap(self):
        h = (ANCHOR // 3600 - 3) * 3600
        tr = [mk_trade(1, h - 1800, yes=0.40, n=5)]
        v = T.hourly_candle_vs_tape([self._candle(h, 0.40, 0.40, 5), self._candle(h - 3600, 0.38, 0.39, 40)], tr, ANCHOR)
        self.assertFalse(v["verified"]); self.assertEqual(v["hours_candle_volume_not_in_tape"], 1)
        r = T.TapeResult(ticker="TK", tape_complete=True, stop_reason=T.EXHAUSTED)
        st = T.final_status(r, v)
        self.assertEqual(st["status"], "COMPLETE_WITH_SOURCE_GAP"); self.assertEqual(st["irrecoverable_window"], [h - 3600 - 3600, h - 3600])

    def test_post_anchor_prints_are_ignored(self):
        h = (ANCHOR // 3600 - 3) * 3600
        tr = [mk_trade(1, h - 10, yes=0.40, n=5), mk_trade(2, ANCHOR + 50, yes=0.90, n=99)]
        self.assertTrue(T.hourly_candle_vs_tape([self._candle(h, 0.40, 0.40, 5)], tr, ANCHOR)["verified"])


class Runner(unittest.TestCase):
    def test_resume_state_and_additive_outputs(self):
        class Sem:  # noqa
            game_date = None; away_team = None; home_team = None
        tr = [mk_trade(i, ANCHOR - 100 - i) for i in range(3_000)]
        m = {"ticker": "TK", "result": "yes", "open_time": T_iso(ANCHOR - 99999), "close_time": T_iso(ANCHOR)}
        with tempfile.TemporaryDirectory() as d:
            kw = dict(out=d, series=["KXNFLGAME"], markets_by_series={"KXNFLGAME": [m]}, kickoffs={}, classify=lambda x: Sem(), budget=1000)
            c = FakeClient(tr)
            r1 = TR.run(c, page_budget=2, **kw)
            self.assertEqual((r1["incomplete"], r1["remaining"]), (1, 1))
            st = json.load(open(os.path.join(d, "tape_state.json")))["tickers"]["TK"]; self.assertEqual((st["status"], st["cursor"]), ("INCOMPLETE_RESUMABLE", "2000"))
            r2 = TR.run(c, page_budget=5, **kw)
            self.assertEqual((r2["complete"], r2["remaining"]), (1, 0))
            lines = open(os.path.join(d, "trades_v2", "KXNFLGAME", "TK.jsonl")).read().splitlines()
            self.assertEqual(len(lines), 3000); self.assertEqual(len({json.loads(x)["trade_id"] for x in lines}), 3000)
            meta = [json.loads(x) for x in open(os.path.join(d, "tape_meta.jsonl"))]
            self.assertEqual([x["status"] for x in meta][-1], "COMPLETE"); self.assertEqual(meta[-1]["anchor_kind"], "close_time")
            self.assertEqual(TR.run(c, page_budget=5, **kw)["tickers_attempted"], 0)        # completed tickers are not refetched


class CaptureGaps(unittest.TestCase):
    def test_capped_fetch_advances_cursor_and_records_an_explicit_gap(self):
        nxt, gap = T.plan_after_fetch(1000, [5000, 4990, 4900], False, "r1")
        self.assertEqual(nxt, 5001); self.assertEqual(gap, {"from": 1000, "to": 4900, "run_id": "r1"})

    def test_complete_fetch_leaves_no_gap(self):
        self.assertEqual(T.plan_after_fetch(1000, [1200, 1100], True, "r1"), (1201, None))
        self.assertEqual(T.plan_after_fetch(1000, [], True, "r1"), (1001, None))

    def test_failed_fetch_keeps_cursor_and_records_nothing_it_cannot_bound(self):
        self.assertEqual(T.plan_after_fetch(1000, [], False, "r1"), (1000, None))

    def test_gap_shrinks_then_closes(self):
        g = {"from": 1000, "to": 4900, "run_id": "r1"}
        g2 = T.shrink_gap(g, [4890, 3000, 2500], False)
        self.assertEqual(g2["to"], 2500)
        self.assertIsNone(T.shrink_gap(g2, [2400, 1500], True))
        self.assertIsNone(T.shrink_gap(g2, [1000], False))          # oldest fetched reached the gap start


if __name__ == "__main__":
    unittest.main()


def test_main_exits_2_when_no_markets_were_restored(tmp_path, monkeypatch, capsys):
    """Run 41978608349 restored nothing, saw todo=0 and exited 0: a green no-op. Zero markets must be an error."""
    import importlib.util, sys as _sys
    spec = importlib.util.spec_from_file_location("tape_repair_main", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "scripts", "kalshi", "tape_repair.py"))
    mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
    monkeypatch.setattr(_sys, "argv", ["tape_repair.py", "--series", "KXNFLGAME", "--out", str(tmp_path)])
    assert mod.main() == 2
    assert "MARKETS_MISSING" in capsys.readouterr().out
