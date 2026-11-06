"""Recovery infrastructure v3 (#246): priority ordering, lazy per-ticker restore, publish manifest, candle storage, throttle stop, independent verification
with quarantine, exact legacy manifest and the before/after coverage report.  No network."""
import json, os, subprocess, sys, tempfile, unittest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.insert(0, ROOT); sys.path.insert(0, os.path.join(ROOT, "scripts", "kalshi"))
from nfl_edge.kalshi import tape as T          # noqa: E402
import tape_repair as TR                       # noqa: E402
import tape_verify as TV                       # noqa: E402
import tape_coverage_report as CR              # noqa: E402
import legacy_manifest as LM                   # noqa: E402

ANCHOR = 1_760_000_000


def iso(t):
    from datetime import datetime, timezone
    return datetime.fromtimestamp(t, timezone.utc).isoformat().replace("+00:00", "Z")


def trade(i, t):
    return dict(trade_id=f"id{i}", ticker="X", created_time=iso(t), yes_price_dollars="0.4200", no_price_dollars="0.5800", count_fp="3.00", taker_side="no")


def mk(series, n, close, result="yes"):
    return {"ticker": f"{series}-25SEP07AAABBB-{n}", "result": result, "open_time": iso(ANCHOR - 99999), "close_time": iso(close)}


class Sem:
    game_date = "2025-09-07"; away_team = "AAA"; home_team = "BBB"


KO = {("2025-09-07", "AAA", "BBB"): (ANCHOR, "g", "2025", "1")}


class Fake:
    def __init__(self, trades, throttle_after=None):
        self.all = sorted(trades, key=lambda x: x["created_time"], reverse=True)
        self.paths, self.throttle_after = [], throttle_after
        class S:  # noqa
            requests = 0; http_429 = 0; http_5xx = 0
            def to_dict(s): return {"requests": s.requests, "http_429": s.http_429}
        self.stats = S()

    def try_get(self, path, params):
        self.paths.append(path); self.stats.requests += 1
        if self.throttle_after is not None and self.stats.requests > self.throttle_after:
            self.stats.http_429 += 1
            return None, "429"
        if path.endswith("/candlesticks"):
            return {"candlesticks": [dict(end_period_ts=ANCHOR - 3600, price=dict(low=None, high=None), volume="0")]}, None
        rows = [t for t in self.all if T.to_ts(t["created_time"]) <= params["max_ts"]]
        start = int(params["cursor"]) if params.get("cursor") else 0
        chunk = rows[start:start + 1000]
        nxt = start + 1000
        return {"trades": chunk, "cursor": str(nxt) if nxt < len(rows) else ""}, None


def run(d, markets, client, **kw):
    series = sorted({m["ticker"].split("-")[0] for m in markets})
    return TR.run(client, out=d, series=series, markets_by_series={s: [m for m in markets if m["ticker"].startswith(s + "-")] for s in series},
                  kickoffs=KO, classify=lambda x: Sem(), budget=kw.pop("budget", 1000), page_budget=kw.pop("page_budget", 5), **kw)


class Ordering(unittest.TestCase):
    def todo(self, ms):
        return [(m["ticker"].split("-")[0], m, ANCHOR, "kickoff") for m in ms]

    def test_capped_legacy_first_then_quote_bearing_round_robin_then_no_quote(self):
        a = [mk("KXNFLTOTAL", i, ANCHOR + i) for i in range(4)]
        b = [mk("KXNFLTEAMTOTAL", i, ANCHOR + i) for i in range(4)]
        c = mk("KXNFLGAME", 9, ANCHOR - 5)
        manifest = {c["ticker"]: {"capped": True}}
        quotes = {m["ticker"] for m in a + b} - {a[0]["ticker"]}
        state = {"tickers": {}}
        o = [x[1]["ticker"] for x in TR.order_todo(self.todo(a + b + [c]), state, manifest, quotes)]
        self.assertEqual(o[0], c["ticker"])                                               # capped legacy tape first
        self.assertEqual(o[-1], a[0]["ticker"])                                           # the only no-quote contract last
        fams = [t.split("-")[0] for t in o[1:-1]]
        self.assertEqual(fams[:4], ["KXNFLTOTAL", "KXNFLTEAMTOTAL", "KXNFLTOTAL", "KXNFLTEAMTOTAL"][:4] if fams[0] == "KXNFLTOTAL" else ["KXNFLTEAMTOTAL", "KXNFLTOTAL", "KXNFLTEAMTOTAL", "KXNFLTOTAL"])  # interleaved

    def test_least_covered_family_goes_first(self):
        a, b = [mk("KXNFLTOTAL", i, ANCHOR) for i in range(3)], [mk("KXNFLTEAMTOTAL", i, ANCHOR) for i in range(3)]
        state = {"tickers": {f"KXNFLTOTAL-x{i}": {"status": "COMPLETE", "n": 5} for i in range(5)}}          # TOTAL already well covered
        o = TR.order_todo(self.todo(a + b), state, {}, None)
        self.assertEqual(o[0][0], "KXNFLTEAMTOTAL")

    def test_per_series_cap_applies_outside_the_capped_group_only(self):
        cap = [mk("KXNFLGAME", i, ANCHOR + i) for i in range(5)]
        oth = [mk("KXNFLTOTAL", i, ANCHOR + i) for i in range(5)]
        o = TR.order_todo(self.todo(cap + oth), {"tickers": {}}, {m["ticker"]: {"capped": True} for m in cap}, None, per_series=2)
        self.assertEqual([x[0] for x in o].count("KXNFLGAME"), 5)
        self.assertEqual([x[0] for x in o].count("KXNFLTOTAL"), 2)


class LazyRestore(unittest.TestCase):
    def test_only_the_touched_ticker_is_restored_and_published(self):
        m1, m2 = mk("KXNFLTOTAL", 1, ANCHOR + 2), mk("KXNFLTOTAL", 2, ANCHOR + 1)
        with tempfile.TemporaryDirectory() as d:
            # tape for m1 was recovered earlier (1,000 prints, resumable); it lives only "on the branch", not on this runner
            branch = os.path.join(d, "branch"); os.makedirs(branch)
            prior = [trade(i, ANCHOR - 10 - i) for i in range(1000)]
            open(os.path.join(branch, "m1.jsonl"), "w").write("".join(json.dumps(x) + "\n" for x in prior))
            os.makedirs(os.path.join(d, "out"))
            json.dump({"tickers": {m1["ticker"]: {"status": "INCOMPLETE_RESUMABLE", "cursor": "1000", "n": 1000, "anchor_ts": ANCHOR, "anchor_kind": "kickoff", "tier": "historical"}}, "runs": []},
                      open(os.path.join(d, "out", "tape_state.json"), "w"))
            asked = []
            def restore(rel):
                asked.append(rel)
                if rel.endswith(m1["ticker"] + ".jsonl"):
                    os.makedirs(os.path.dirname(os.path.join(d, "out", rel)), exist_ok=True)
                    open(os.path.join(d, "out", rel), "w").write(open(os.path.join(branch, "m1.jsonl")).read())
                    return True
                return False
            c = Fake(prior + [trade(5000 + i, ANCHOR - 5000 - i) for i in range(300)])
            r = run(os.path.join(d, "out"), [m1], c, fetch_existing=restore, quotes=None)
            self.assertEqual(asked, [os.path.join("trades_v2", "KXNFLTOTAL", m1["ticker"] + ".jsonl")])
            lines = open(os.path.join(d, "out", "trades_v2", "KXNFLTOTAL", m1["ticker"] + ".jsonl")).read().splitlines()
            self.assertEqual(len(lines), 1300); self.assertEqual(len({json.loads(x)["trade_id"] for x in lines}), 1300)        # appended, no dup, nothing lost
            man = open(os.path.join(d, "out", "publish_manifest.txt")).read().split()
            self.assertIn(os.path.join("trades_v2", "KXNFLTOTAL", m1["ticker"] + ".jsonl"), man)
            self.assertFalse([p for p in man if m2["ticker"] in p])                                                             # untouched ticker not published

    def test_unrestorable_ticker_is_skipped_never_restarted(self):
        m1 = mk("KXNFLTOTAL", 1, ANCHOR)
        with tempfile.TemporaryDirectory() as d:
            json.dump({"tickers": {m1["ticker"]: {"status": "INCOMPLETE_RESUMABLE", "cursor": "1000", "n": 1000, "anchor_ts": ANCHOR, "anchor_kind": "kickoff", "tier": "historical"}}, "runs": []},
                      open(os.path.join(d, "tape_state.json"), "w"))
            c = Fake([trade(i, ANCHOR - 5 - i) for i in range(10)])
            r = run(d, [m1], c, fetch_existing=lambda rel: False)
            self.assertEqual((r["restore_failed"], r["tickers_attempted"], c.stats.requests), (1, 0, 0))
            self.assertFalse(os.path.exists(os.path.join(d, "trades_v2", "KXNFLTOTAL", m1["ticker"] + ".jsonl")))


class Candles(unittest.TestCase):
    def test_candles_stored_for_contracts_without_legacy_candles_only(self):
        a, b = mk("KXNFLTOTAL", 1, ANCHOR + 2), mk("KXNFLTOTAL", 2, ANCHOR + 1)
        with tempfile.TemporaryDirectory() as d:
            run(d, [a, b], Fake([trade(1, ANCHOR - 100)]), manifest={b["ticker"]: {"has_candles": True, "capped": False}})
            self.assertTrue(os.path.exists(os.path.join(d, "candles_v2", "KXNFLTOTAL", a["ticker"] + ".json")))
            self.assertFalse(os.path.exists(os.path.join(d, "candles_v2", "KXNFLTOTAL", b["ticker"] + ".json")))
            c = json.load(open(os.path.join(d, "candles_v2", "KXNFLTOTAL", a["ticker"] + ".json")))
            self.assertEqual((c["anchor_ts"], len(c["h60"]), len(c["m1"])), (ANCHOR, 1, 1))


class CandleOnly(unittest.TestCase):
    def test_complete_ticker_without_candles_gets_a_two_request_candle_job_and_no_trade_refetch(self):
        m = mk("KXNFLTOTAL", 1, ANCHOR)
        with tempfile.TemporaryDirectory() as d:
            json.dump({"tickers": {m["ticker"]: {"status": "COMPLETE", "n": 7, "cursor": None, "anchor_ts": ANCHOR, "anchor_kind": "kickoff", "tier": "historical"}}, "runs": []},
                      open(os.path.join(d, "tape_state.json"), "w"))
            c = Fake([])
            r = run(d, [m], c)
            self.assertEqual((r["candle_only"], c.stats.requests, r["tickers_attempted"]), (1, 2, 0))
            self.assertFalse([p for p in c.paths if "trades" in p])
            self.assertTrue(os.path.exists(os.path.join(d, "candles_v2", "KXNFLTOTAL", m["ticker"] + ".json")))
            self.assertIn(os.path.join("candles_v2", "KXNFLTOTAL", m["ticker"] + ".json"), open(os.path.join(d, "publish_manifest.txt")).read().split())
            c2 = Fake([]); self.assertEqual(run(d, [m], c2)["candle_only"], 0)               # flagged: never repeated

    def test_legacy_candles_and_empty_tapes_need_no_job(self):
        a, b = mk("KXNFLTOTAL", 1, ANCHOR), mk("KXNFLTOTAL", 2, ANCHOR)
        with tempfile.TemporaryDirectory() as d:
            json.dump({"tickers": {a["ticker"]: {"status": "COMPLETE", "n": 7, "anchor_ts": ANCHOR, "anchor_kind": "kickoff", "tier": "historical"},
                                   b["ticker"]: {"status": "COMPLETE", "n": 0, "anchor_ts": ANCHOR, "anchor_kind": "kickoff", "tier": "historical", "tiers_checked": ["historical", "live"]}}, "runs": []},
                      open(os.path.join(d, "tape_state.json"), "w"))
            c = Fake([])
            self.assertEqual(run(d, [a, b], c, manifest={a["ticker"]: {"has_candles": True}})["candle_only"], 0)
            self.assertEqual(c.stats.requests, 0)


class Throttle(unittest.TestCase):
    def test_run_stops_when_throttled_and_saves_progress(self):
        ms = [mk("KXNFLTOTAL", i, ANCHOR + i) for i in range(5)]
        with tempfile.TemporaryDirectory() as d:
            c = Fake([trade(i, ANCHOR - 5 - i) for i in range(10)], throttle_after=2)
            r = run(d, ms, c, max_throttle=2)
            self.assertEqual(r["stopped"], "throttled")
            self.assertLess(r["tickers_attempted"], 5)
            self.assertTrue(os.path.exists(os.path.join(d, "tape_state.json")))


class Verify(unittest.TestCase):
    def _setup(self, d, prints, anchor):
        m = mk("KXNFLGAME", 1, ANCHOR)
        os.makedirs(os.path.join(d, "trades_v2", "KXNFLGAME"))
        fp = os.path.join(d, "trades_v2", "KXNFLGAME", m["ticker"] + ".jsonl")
        open(fp, "w").write("".join(json.dumps(trade(i, t)) + "\n" for i, t in enumerate(prints)))
        json.dump({"tickers": {m["ticker"]: {"status": "COMPLETE", "n": len(prints), "anchor_ts": anchor, "anchor_kind": "kickoff"}}, "runs": []}, open(os.path.join(d, "tape_state.json"), "w"))
        return m, fp

    def test_clean_tape_passes(self):
        with tempfile.TemporaryDirectory() as d:
            m, fp = self._setup(d, [ANCHOR - 10, ANCHOR - 20], ANCHOR)
            rep = TV.verify(d, {m["ticker"]: m}, KO, lambda x: Sem())
            self.assertEqual((rep["checked"], rep["passed"], rep["quarantined"]), (1, 1, []))
            self.assertTrue(os.path.exists(fp))

    def test_post_kickoff_print_is_quarantined_and_state_reset(self):
        with tempfile.TemporaryDirectory() as d:
            m, fp = self._setup(d, [ANCHOR + 500, ANCHOR - 20], ANCHOR)
            rep = TV.verify(d, {m["ticker"]: m}, KO, lambda x: Sem())
            self.assertEqual(rep["passed"], 0); self.assertEqual(rep["quarantined"][0]["post_kickoff"], 1)
            self.assertFalse(os.path.exists(fp))
            self.assertTrue(os.path.exists(os.path.join(d, rep["quarantined"][0]["quarantine_path"])))
            self.assertNotIn(m["ticker"], json.load(open(os.path.join(d, "tape_state.json")))["tickers"])

    def test_wrong_stored_anchor_is_caught_even_if_prints_look_clean(self):
        with tempfile.TemporaryDirectory() as d:
            m, fp = self._setup(d, [ANCHOR - 10], ANCHOR + 9999)         # collector claimed a later anchor (e.g. close_time)
            rep = TV.verify(d, {m["ticker"]: m}, KO, lambda x: Sem())
            self.assertEqual(len(rep["quarantined"]), 1)

    def test_no_independent_kickoff_is_unverifiable_not_passed(self):
        with tempfile.TemporaryDirectory() as d:
            m, fp = self._setup(d, [ANCHOR - 10], ANCHOR)
            rep = TV.verify(d, {m["ticker"]: m}, {}, lambda x: type("S", (), {"game_date": None, "away_team": None, "home_team": None})())
            self.assertEqual((rep["checked"], rep["unverifiable"]), (0, [m["ticker"]])); self.assertTrue(os.path.exists(fp))


class PublisherLists(unittest.TestCase):
    def test_only_from_and_remove_from(self):
        pub = os.path.join(ROOT, "scripts", "ci", "publish_market_data.py")
        with tempfile.TemporaryDirectory() as d:
            g = lambda *a, cwd: subprocess.run(["git", *a], cwd=cwd, text=True, capture_output=True, check=True)
            origin, other, repo = (os.path.join(d, x) for x in ("origin.git", "other", "repo"))
            subprocess.run(["git", "init", "-q", "--bare", origin], check=True)
            g("config", "uploadpack.allowFilter", "true", cwd=origin); g("config", "uploadpack.allowAnySHA1InWant", "true", cwd=origin)
            subprocess.run(["git", "clone", "-q", origin, other], check=True)
            for k, v in (("user.name", "t"), ("user.email", "t@e"), ("commit.gpgsign", "false")):
                g("config", k, v, cwd=other)
            open(os.path.join(other, "seed"), "w").write("s"); g("add", "-A", cwd=other); g("commit", "-q", "-m", "s", cwd=other); g("branch", "-M", "main", cwd=other); g("push", "-q", "origin", "main", cwd=other)
            g("checkout", "-q", "-b", "market-data", cwd=other)
            base = os.path.join(other, "data", "b", "trades_v2"); os.makedirs(base)
            open(os.path.join(base, "bad.jsonl"), "w").write("contaminated\n"); open(os.path.join(base, "keep.jsonl"), "w").write("keep\n")
            g("add", "-A", cwd=other); g("commit", "-q", "-m", "md", cwd=other); g("push", "-q", "origin", "market-data", cwd=other)
            subprocess.run(["git", "clone", "-q", "-b", "main", f"file://{origin}", repo], check=True)
            for k, v in (("user.name", "t"), ("user.email", "t@e"), ("commit.gpgsign", "false")):
                g("config", k, v, cwd=repo)
            src = os.path.join(repo, "data", "b"); os.makedirs(os.path.join(src, "trades_v2")); os.makedirs(os.path.join(src, "trades_v2_quarantine"))
            open(os.path.join(src, "trades_v2", "new.jsonl"), "w").write("new\n")
            open(os.path.join(src, "trades_v2_quarantine", "bad.verify-1.jsonl"), "w").write("contaminated\n")
            open(os.path.join(src, "trades_v2", "stray.jsonl"), "w").write("not listed\n")
            open(os.path.join(src, "m.txt"), "w").write("trades_v2/new.jsonl\ntrades_v2_quarantine/bad.verify-1.jsonl\ntrades_v2/bad.jsonl\n")
            open(os.path.join(src, "r.txt"), "w").write("trades_v2/bad.jsonl\n")
            r = subprocess.run([sys.executable, pub, "--src", "data/b", "--sparse", "--only-from", os.path.join(src, "m.txt"), "--remove-from", os.path.join(src, "r.txt"), "--message", "m"], cwd=repo, text=True, capture_output=True)
            self.assertEqual(r.returncode, 0, r.stdout + r.stderr)
            tree = set(g("ls-tree", "-r", "--name-only", "market-data", cwd=origin).stdout.split())
            self.assertIn("data/b/trades_v2/new.jsonl", tree); self.assertIn("data/b/trades_v2_quarantine/bad.verify-1.jsonl", tree)
            self.assertIn("data/b/trades_v2/keep.jsonl", tree)                                # untouched file stays
            self.assertNotIn("data/b/trades_v2/bad.jsonl", tree)                              # removed from the branch tip (old content stays in history)
            self.assertNotIn("data/b/trades_v2/stray.jsonl", tree)                            # unlisted file not published


class Manifest(unittest.TestCase):
    def test_exact_lines_cap_and_candle_presence(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "trades", "S")); os.makedirs(os.path.join(d, "candles", "S"))
            line = json.dumps(dict(trade_id="a", created_time="2026-01-01T00:00:00.5Z")) + "\n"
            open(os.path.join(d, "trades", "S", "CAP.jsonl"), "w").write(line * 10000)
            open(os.path.join(d, "trades", "S", "NEAR.jsonl"), "w").write(line * 9999)
            open(os.path.join(d, "trades", "S", "EMPTY.jsonl"), "w").close()
            open(os.path.join(d, "candles", "S", "CAP.json"), "w").write("{}")
            m = LM.build(d)
            self.assertEqual(m["totals"], dict(files=3, capped=1, empty=1, size_band_ge_2_9MB=0))
            self.assertTrue(m["tickers"]["CAP"]["capped"] and m["tickers"]["CAP"]["has_candles"]); self.assertFalse(m["tickers"]["NEAR"]["capped"])
            self.assertEqual(m["tickers"]["CAP"]["oldest_created"], "2026-01-01T00:00:00.5Z")


class CoverageV2(unittest.TestCase):
    def test_measured_legacy_capped_recovery_collection_and_history(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "markets")); os.makedirs(os.path.join(d, "horizons"))
            ms = [{"ticker": f"KXNFLGAME-{i}", "result": "yes"} for i in range(3)]
            open(os.path.join(d, "markets", "KXNFLGAME.jsonl"), "w").write("".join(json.dumps(m) + "\n" for m in ms))
            man = {f"KXNFLGAME-{i}": dict(series="KXNFLGAME", lines=10000 if i < 2 else 500, bytes=3_000_000 if i < 2 else 100, capped=i < 2, empty=False, has_candles=True) for i in range(3)}
            json.dump({"tickers": man}, open(os.path.join(d, "legacy_manifest.json"), "w"))
            row = lambda t, st, n, ver: dict(ticker=t, series="KXNFLGAME", status=st, total_prints_on_disk=n, tier="historical", tiers_checked=["historical"], anchor_kind="kickoff", candle_check={"verified": ver})
            open(os.path.join(d, "tape_meta.jsonl"), "w").write(json.dumps(row("KXNFLGAME-0", "COMPLETE", 20000, True)) + "\n" + json.dumps(row("KXNFLGAME-1", "INCOMPLETE_RESUMABLE", 5000, False)) + "\n")
            json.dump({"tickers": {}, "unanchored": {}, "runs": [{"trades_written": 25000, "client_stats": {"requests": 30, "retries": 2, "http_429": 1, "http_5xx": 0}}, {"trades_written": 1, "stopped": "throttled", "client_stats": {"requests": 4}}]},
                      open(os.path.join(d, "tape_state.json"), "w"))
            rep = CR.report(d); e = rep["series"]["KXNFLGAME"]; t = rep["totals"]
            self.assertEqual((e["legacy_tape_files"], e["legacy_tape_capped_at_10000"], e["legacy_capped_basis"]), (3, 2, "exact_lines_manifest"))
            self.assertEqual((e["recovered_tape"]["capped_legacy_recovered"], e["recovered_tape"]["capped_legacy_recovered_verified"], e["recovered_tape"]["capped_legacy_in_progress"]), (1, 1, 1))
            self.assertEqual((t["legacy_measured"], t["legacy_capped_exact"], t["legacy_capped_recovered"], t["legacy_capped_remaining"]), (True, 2, 1, 1))
            self.assertEqual((rep["collection"]["requests"], rep["collection"]["retries"], rep["collection"]["runs"], rep["collection"]["throttled_runs"]), (34, 2, 2, 1))
            h = CR.history_row(rep)
            self.assertEqual(h["families"]["KXNFLGAME"]["capped_recovered"], 1)

    def test_unmeasured_stays_unmeasured_without_manifest_or_trades(self):
        with tempfile.TemporaryDirectory() as d:
            os.makedirs(os.path.join(d, "markets"))
            open(os.path.join(d, "markets", "KXNFLGAME.jsonl"), "w").write(json.dumps({"ticker": "a", "result": "yes"}) + "\n")
            rep = CR.report(d)
            self.assertIsNone(rep["totals"]["legacy_capped_exact"]); self.assertEqual(rep["series"]["KXNFLGAME"]["legacy_capped_basis"], "not_measured")


if __name__ == "__main__":
    unittest.main()


class CommittedCappedList(unittest.TestCase):
    def test_committed_list_is_the_exact_baseline_and_drives_priority(self):
        m = TR.load_committed_capped_list()
        self.assertEqual(sum(1 for e in m.values() if e["capped"]), 439)
        self.assertEqual(len(m), 1007)
        self.assertTrue(all(e["has_candles"] for e in m.values()))
        capped = next(t for t, e in m.items() if e["capped"])
        other = mk("KXNFLTOTAL", 1, ANCHOR + 5)
        cm = {"ticker": capped, "result": "yes", "open_time": iso(ANCHOR - 9), "close_time": iso(ANCHOR - 5)}
        o = TR.order_todo([("KXNFLTOTAL", other, ANCHOR, "kickoff"), (capped.split("-")[0], cm, ANCHOR, "kickoff")], {"tickers": {}}, m, None)
        self.assertEqual(o[0][1]["ticker"], capped)

    def test_missing_file_means_no_manifest_not_a_crash(self):
        self.assertIsNone(TR.load_committed_capped_list("/nonexistent/x.json"))
