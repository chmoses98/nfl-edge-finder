"""The DEFAULT-OFF capture is compared against main by RUNNING BOTH, not by re-deriving main's rule.

`tests/test_capture_isolation.py` pins `plan_book_requests` against a transcription of main's ordering. That
is a useful unit, and it is not the production path: `main()` never calls `plan_book_requests`. It builds its
own candidate list, sorts it and slices it inline. A future edit to those three lines would leave the unit
test green while changing what the live Sunday experiment requests.

So this test runs the REAL `main()` of both revisions -- main's, fetched from the merge-base, and this
branch's -- against one deterministic synthetic board behind a recording client and a frozen clock, and
compares what they actually did:

    * the exact sequence of API calls (path AND order: a different order is a different rate-limit profile)
    * every quote row, byte for byte
    * the capture state that carries into the next run
    * every output file, and the exit code

The only differences permitted are ADDITIVE: manifest keys this branch adds, and the open-set file, both of
which are outside the v2 gate on purpose and neither of which changes a request or an existing field.

Nothing in `capture.py` was refactored to make this test possible.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

# manifest keys this branch adds outside the v2 gate; additive observation only
ADDITIVE_MANIFEST_KEYS = {"books_dropped_by_cap", "openset", "provisional_series", "provisional_file_present",
                          "schema_version", "v2_capture", "capture_mode"}
# The same thing one level down: PER-SERIES manifest keys added outside the v2 gate. `provisional` records
# whether a series came from the discovered-but-not-yet-reviewed list; it is an observation ABOUT the
# capture, never an input to what was requested or how anything was priced.
ADDITIVE_SERIES_KEYS = {"provisional"}
VOLATILE = {"run_id", "started_at", "finished_at", "seconds", "client_stats"}


def _without(d, keys):
    return {k: v for k, v in d.items() if k not in keys}


def series_differences(a_series, b_series):
    """Every way the per-series manifest entries differ, ignoring the ADDITIVE keys ON BOTH SIDES.

    WHY BOTH SIDES, AND WHY THIS WAS WRONG
    --------------------------------------
    This comparison used to strip `provisional` from the HEAD entry only:

        {kk: vv for kk, vv in b[k][s].items() if kk != "provisional"} == a[k][s]

    which was correct exactly while the baseline was a PRE-V2 revision that had no `provisional` key at all.
    `pair` builds its baseline from `git merge-base HEAD origin/main`, so once the v2 capture work merged to
    main the merge base collapsed onto HEAD: both sides became the same file, both emit `provisional`, and
    stripping it from one side alone made the head entry look like it had LOST a key the baseline had. The
    assertion failed reporting `Right contains 1 more item: {'provisional': False}` -- a self-reference
    artifact, not a capture regression.

    The intent was always "ignore the additive key, compare everything else", so it is stripped from both.
    Every other key -- `n`, `complete`, `tier`, `observed_at` -- is still compared exactly, which is what
    keeps this a real check that the manifest change is additive and alters no existing value.
    """
    problems = []
    if set(a_series) != set(b_series):
        problems.append(f"series set changed: {sorted(set(a_series) ^ set(b_series))}")
        return problems
    for s in a_series:
        extra = set(b_series[s]) - set(a_series[s]) - ADDITIVE_SERIES_KEYS
        if extra:
            problems.append(f"series.{s} gained non-additive key(s): {sorted(extra)}")
        lost = set(a_series[s]) - set(b_series[s]) - ADDITIVE_SERIES_KEYS
        if lost:
            problems.append(f"series.{s} lost key(s): {sorted(lost)}")
        x, y = _without(a_series[s], ADDITIVE_SERIES_KEYS), _without(b_series[s], ADDITIVE_SERIES_KEYS)
        for kk in sorted(set(x) & set(y)):
            if x[kk] != y[kk]:
                problems.append(f"series.{s}.{kk} changed: {x[kk]!r} -> {y[kk]!r}")
    return problems


def _merge_base():
    r = subprocess.run(["git", "merge-base", "HEAD", "origin/main"], cwd=ROOT, capture_output=True, text=True)
    return r.stdout.strip() if r.returncode == 0 and r.stdout.strip() else None


def _board():
    """A deterministic board: three series across the three capture tiers, with and without kickoffs."""
    games = [("26SEP13ATLPIT", "ATL", "PIT"), ("26SEP13KCDEN", "KC", "DEN"), ("26SEP14NYJBUF", "NYJ", "BUF")]
    series = {"KXNFLGAME": "FULL_MICROSTRUCTURE", "KXNFL1HSPREAD": "FULL_MICROSTRUCTURE",
              "KXNFLSEASON": "LIGHT", "KXNFLAWARD": "DAILY"}
    by_series, kicks = {}, {}
    n = 0
    for s, _tier in series.items():
        by_series[s] = {}
        for gi, (slug, away, home) in enumerate(games):
            for k in range(6):
                n += 1
                tk = f"{s}-{slug}-{away}{k}" if s.startswith("KXNFLGAME") or s.startswith("KXNFL1H") else f"{s}-27-{away}{k}"
                by_series[s][tk] = {
                    "ticker": tk, "event_ticker": f"{s}-{slug}",
                    "yes_bid_dollars": 0.40 + 0.01 * (n % 9), "yes_ask_dollars": 0.44 + 0.01 * (n % 7),
                    "no_bid_dollars": 0.55, "no_ask_dollars": 0.60, "last_price_dollars": 0.42,
                    # a third of the board has traded since the previous run, a third never traded
                    "volume_fp": float((n * 37) % 400) if n % 3 else 0.0,
                    "open_interest_fp": float(n * 3), "liquidity_dollars": float(n * 11),
                    "yes_bid_size_fp": float(n % 50), "yes_ask_size_fp": float((n * 7) % 50),
                    "status": "active", "result": "", "close_time": "2026-09-13T21:00:00Z",
                    "open_time": "2026-09-01T00:00:00Z", "expected_expiration_time": "2026-09-13T23:00:00Z",
                    "strike_type": None, "cap_strike": None, "custom_strike": None}
                if s in ("KXNFLGAME", "KXNFL1HSPREAD"):
                    kicks[tk] = ("2026-09-13T17:00:00+00:00" if gi < 2 else "2026-09-14T00:20:00+00:00", f"2026_02_{away}_{home}")
    return series, by_series, kicks


def _run(capture_path, out_dir, max_books):
    """Execute one revision's main() against the board; return everything it did."""
    from datetime import datetime, timezone
    series, by_series, kicks = _board()
    requests = []

    class Stats:
        def to_dict(self):
            return {"requests": len(requests)}

    class FakeClient:
        def __init__(self, **kw):
            self.stats = Stats()

        def markets(self, series_ticker=None, status=None, limit=None, max_pages=None):
            requests.append(("markets", series_ticker, status, limit, max_pages))
            d = by_series.get(series_ticker)
            if d is None:
                return [], False, "no such series"
            return list(d.values()), True, None

        def try_get(self, path, params=None):
            requests.append(("try_get", path, json.dumps(params, sort_keys=True)))
            return {"orderbook_fp": hashlib.sha1(path.encode()).hexdigest()[:8]}, None

        def trades(self, ticker=None, min_ts=None, limit=None, max_pages=None):
            requests.append(("trades", ticker, min_ts, limit, max_pages))
            return [{"trade_id": f"{ticker}-1", "created_time": "2026-09-13T00:00:00Z"}], True, None

    import nfl_edge.kalshi.client as CL
    saved = CL.KalshiClient
    CL.KalshiClient = FakeClient
    try:
        spec = importlib.util.spec_from_file_location(f"cap_{os.path.basename(out_dir)}", capture_path)
        cap = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(cap)
        fixed = datetime(2026, 9, 13, 16, 30, 0, tzinfo=timezone.utc)
        cap.now_utc = lambda: fixed
        cap.OUT_ROOT = out_dir
        sched = {}
        for s, d in by_series.items():
            for tk, m in d.items():
                if tk not in kicks:
                    continue
                sem = cap.classify(m)
                if sem.game_date and sem.away_team and sem.home_team:
                    ko, gid = kicks[tk]
                    sched[(sem.game_date, sem.away_team, sem.home_team)] = {
                        "kickoff_utc": ko, "game_id": gid, "season": "2026", "week": "2"}
        cap.load_schedule = lambda p: (sched, "fixture")
        # a registry with all three tiers, written where this revision expects it
        os.makedirs(out_dir, exist_ok=True)
        reg = os.path.join(out_dir, "registry.json")
        json.dump({"series": {s: {"tier": t} for s, t in series.items()}}, open(reg, "w"))
        cap.REG_PATH = reg
        prior = {"fingerprints": {t: "x" * 16 for s in by_series for t in list(by_series[s])[::3]},
                 "volume": {t: float((i * 13) % 300) for s in by_series for i, t in enumerate(by_series[s])},
                 "trade_cursor": {}, "last_daily_run": "2026-09-13T00:00:00+00:00", "last_seen": {}}
        json.dump(prior, open(os.path.join(out_dir, "state.json"), "w"))

        argv = sys.argv
        sys.argv = ["capture.py", "--max-books", str(max_books)]
        import contextlib, io
        try:
            with contextlib.redirect_stdout(io.StringIO()):
                rc = cap.main()
        finally:
            sys.argv = argv
    finally:
        CL.KalshiClient = saved

    day = os.path.join(out_dir, "2026-09-13")
    files = {}
    for fn in sorted(os.listdir(day)):
        suffix = fn.split(".", 1)[1]
        files[suffix] = open(os.path.join(day, fn), "rb").read()
    man = json.loads(files["manifest.json"])
    return {"rc": rc, "requests": requests, "files": files,
            "manifest": {k: v for k, v in man.items() if k not in VOLATILE},
            "state": json.load(open(os.path.join(out_dir, "state.json"))),
            "quotes": files.get("quotes.jsonl", b"").decode().splitlines()}


@pytest.fixture(scope="module")
def pair(tmp_path_factory):
    base = _merge_base()
    if base is None:
        pytest.skip("no origin/main to compare against in this checkout")
    r = subprocess.run(["git", "show", f"{base}:scripts/kalshi/capture.py"], cwd=ROOT,
                       capture_output=True, text=True)
    if r.returncode != 0:
        pytest.skip("main's capture.py is not reachable from this checkout")
    d = tmp_path_factory.mktemp("cap")
    main_py = d / "capture_main.py"
    main_py.write_text(r.stdout)
    return {"main": _run(str(main_py), str(d / "out_main"), 2500),
            "head": _run(os.path.join(ROOT, "scripts", "kalshi", "capture.py"), str(d / "out_head"), 2500)}


def test_the_api_request_sequence_is_identical(pair):
    """Same calls, same order. A reordering is a different rate-limit profile against a live account."""
    a, b = pair["main"]["requests"], pair["head"]["requests"]
    assert len(a) == len(b), f"request COUNT changed: {len(a)} -> {len(b)}"
    for i, (x, y) in enumerate(zip(a, b)):
        assert x == y, f"request {i} diverged: {x!r} -> {y!r}"


def test_the_board_actually_exercises_the_order_book_budget(pair):
    """Guards the guard: a fixture that requested no books would make the comparison meaningless."""
    books = [r for r in pair["main"]["requests"] if r[0] == "try_get"]
    trades = [r for r in pair["main"]["requests"] if r[0] == "trades"]
    assert len(books) >= 10 and len(trades) >= 5


def test_every_quote_row_is_byte_identical(pair):
    assert pair["main"]["quotes"] == pair["head"]["quotes"]


def test_the_carried_capture_state_is_unchanged(pair):
    a, b = pair["main"]["state"], pair["head"]["state"]
    for k in ("fingerprints", "volume", "trade_cursor", "last_seen", "last_daily_run"):
        assert a.get(k) == b.get(k), f"state.{k} changed"


def test_no_output_file_is_lost_or_altered(pair):
    a, b = pair["main"]["files"], pair["head"]["files"]
    assert not (set(a) - set(b)), f"outputs disappeared: {sorted(set(a) - set(b))}"
    for k in a:
        if k == "manifest.json":
            continue                                   # compared structurally below
        assert a[k] == b[k], f"{k} changed"
    assert set(b) - set(a) <= {"openset.json"}, f"unexpected new output: {sorted(set(b) - set(a))}"


def test_the_manifest_gains_only_additive_keys_and_changes_no_existing_value(pair):
    a, b = pair["main"]["manifest"], pair["head"]["manifest"]
    assert not (set(a) - set(b)), f"manifest keys lost: {sorted(set(a) - set(b))}"
    assert set(b) - set(a) <= ADDITIVE_MANIFEST_KEYS, f"unexpected manifest keys: {sorted(set(b) - set(a) - ADDITIVE_MANIFEST_KEYS)}"
    for k in a:
        if k == "series":
            assert series_differences(a[k], b[k]) == []
        else:
            assert a[k] == b[k], f"manifest.{k} changed: {a[k]!r} -> {b[k]!r}"


def test_the_series_comparison_still_catches_a_changed_existing_value():
    """Mutation check on the comparison itself: stripping the additive key must not make it blind.

    Every one of these is a REAL capture regression, and each must still be reported now that `provisional`
    is ignored on both sides.
    """
    base = {"KXNFLGAME": {"n": 18, "complete": True, "tier": "FULL_MICROSTRUCTURE",
                          "observed_at": "2026-09-13T16:30:00+00:00", "provisional": False}}
    assert series_differences(base, base) == []
    # the additive key differing, alone, is not a regression
    flipped = {"KXNFLGAME": dict(base["KXNFLGAME"], provisional=True)}
    assert series_differences(base, flipped) == []
    absent = {"KXNFLGAME": _without(base["KXNFLGAME"], {"provisional"})}
    assert series_differences(base, absent) == [] and series_differences(absent, base) == []
    # every existing value is still compared exactly
    for key, bad in (("n", 17), ("complete", False), ("tier", "LIGHT"),
                     ("observed_at", "2026-09-13T16:31:00+00:00")):
        changed = {"KXNFLGAME": dict(base["KXNFLGAME"], **{key: bad})}
        assert series_differences(base, changed) == [
            f"series.KXNFLGAME.{key} changed: {base['KXNFLGAME'][key]!r} -> {bad!r}"], key
    # and a genuinely new non-additive key, or a lost one, is still caught
    gained = {"KXNFLGAME": dict(base["KXNFLGAME"], surprise=1)}
    assert series_differences(base, gained) == ["series.KXNFLGAME gained non-additive key(s): ['surprise']"]
    lost = {"KXNFLGAME": _without(base["KXNFLGAME"], {"tier"})}
    assert series_differences(base, lost) == ["series.KXNFLGAME lost key(s): ['tier']"]
    # a different series set is a structural change, reported before any value comparison
    assert series_differences(base, {"KXNFLSEASON": base["KXNFLGAME"]})[0].startswith("series set changed")


def test_the_v2_capture_gate_is_default_off_on_the_real_path(pair):
    """The isolation claim that does NOT depend on a baseline revision.

    `pair`'s baseline comes from `git merge-base HEAD origin/main`. That was a genuine cross-revision diff
    while the v2 work sat on a branch; now that it is merged the merge base is HEAD, so the pair comparisons
    above run the SAME file twice and prove self-consistency rather than non-regression. This assertion and
    `test_the_gate_is_load_bearing_on_the_real_path` are the two that still bite regardless: with the gate
    off the run declares itself INCUMBENT, and turning it on demonstrably changes the real path.
    """
    man = pair["head"]["manifest"]
    assert man.get("v2_capture") is False, "the v2 capture must be OFF unless explicitly enabled"
    assert man.get("capture_mode") == "INCUMBENT"
    assert man.get("schema_version") == "capture-1.0.0", "the incumbent schema version, not the v2 one"


def test_the_exit_code_is_unchanged(pair):
    assert pair["main"]["rc"] == pair["head"]["rc"]


def test_the_gate_is_load_bearing_on_the_real_path(pair, tmp_path, monkeypatch):
    """If switching v2 on changed nothing here, the equivalence above would prove nothing."""
    monkeypatch.setenv("NFL_EDGE_V2_CAPTURE", "1")
    v2 = _run(os.path.join(ROOT, "scripts", "kalshi", "capture.py"), str(tmp_path / "out_v2"), 2500)
    assert v2["requests"] != pair["head"]["requests"] or v2["quotes"] != pair["head"]["quotes"], \
        "the v2 gate changed nothing on the real path, so the default-off comparison is vacuous"
