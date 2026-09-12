"""OPEN-SET EVIDENCE: was this exact contract open at this exact moment, and if not, why not?

The capture fetches `status=open` per series, and writes a quote row only when the price fingerprint moved. So
a ticker's absence from a run's quote file means nothing at all, and the ticker-level ledger the capture already
keeps (`state.json.last_seen[ticker] = run_id`) answers only "when was it last seen", never "was it open at run
R" for any earlier R. That is enough to pick a close and not enough to defend one: a contract that vanished 38
minutes before kickoff has a legitimate close at its last live observation, but a contract missing because its
series fetch half-failed has no close at all, and after the fact the two look identical.

So the open set is recorded per run, deterministically, at the only moment it is knowable -- inside the capture,
which holds it in memory anyway. It is stored as a DELTA against the previous run because the full set is ~18k
tickers and the run cadence is ~10 minutes: writing the set every run would cost ~540 KB per run and ~75 MB a
day, while the tickers that actually open or close between two runs number in the handful. A full list is
anchored whenever the chain cannot be trusted -- no previous run, the anchor is a day old, or the delta has
grown past half the set -- so any run's set is reconstructed by replaying a bounded number of small deltas.

    <capture_root>/<YYYY-MM-DD>/<run_id>.openset.json
        {schema_version, run_id, observed_at, n_open, open_set_sha256, prev_run_id, base_run_id,
         full: [...] | null, added: [...], removed: [...]}

`open_set_sha256` is the hash of the reconstructed set, so a replay that drifts from what the capture actually
saw is detected rather than trusted (`verify()`).

The six presence states are deliberately distinct, because they carry opposite meanings for research:

    OPEN                            the ticker was in the open set of that run
    CLOSED                          absent, series fetched completely, and the contract's own close_time had passed
    DELISTED                        absent, series fetched completely, close_time not yet reached -- the exchange
                                    pulled it. Its last live observation is a legitimate close.
    NOT_RETURNED_DUE_PARTIAL_FETCH  absent, but the series fetch did not complete: ABSENCE IS NOT EVIDENCE
    SERIES_NOT_POLLED               the series was not fetched in that run at all (DAILY tier, or not in the registry)
    UNKNOWN                         no open-set record for that run (a run captured before this file existed)

Only OPEN, CLOSED and DELISTED are statements about the market. The other three are statements about the
capture, and must never be read as a market event.

Schema version: openset-1.0.0.
"""
from __future__ import annotations

import bisect
import glob
import hashlib
import json
import os
from datetime import datetime, timezone

OPENSET_VERSION = "openset-1.0.0"
OPEN = "OPEN"
CLOSED = "CLOSED"
DELISTED = "DELISTED"
PARTIAL_FETCH = "NOT_RETURNED_DUE_PARTIAL_FETCH"
SERIES_NOT_POLLED = "SERIES_NOT_POLLED"
UNKNOWN = "UNKNOWN"
MARKET_STATES = (OPEN, CLOSED, DELISTED)          # the three that say something about the market itself

ANCHOR_EVERY_RUNS = 144                            # ~1 day at a 10-minute cadence
ANCHOR_IF_DELTA_EXCEEDS = 0.5                      # a delta past half the set is not worth encoding as a delta


def _dt(s):
    if not s:
        return None
    d = datetime.fromisoformat(str(s).replace("Z", "+00:00"))
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def set_hash(tickers) -> str:
    return hashlib.sha256("\n".join(sorted(tickers)).encode()).hexdigest()[:32]


# ---------------------------------------------------------------------------------------------- writer
def build_record(run_id: str, observed_at: str, open_now, *, last_seen: dict, prev_run_id: str | None,
                 base_run_id: str | None, runs_since_anchor: int) -> dict:
    """The open-set record for one capture run.

    `last_seen` is the capture's own ticker -> last run_id ledger BEFORE this run folds itself in, so the
    previous run's open set is exactly {t : last_seen[t] == prev_run_id} -- no second copy of the set has to be
    carried in the capture state to diff against.
    """
    open_now = set(open_now)
    prev = {t for t, r in (last_seen or {}).items() if r == prev_run_id} if prev_run_id else set()
    added, removed = sorted(open_now - prev), sorted(prev - open_now)
    anchor = (not prev_run_id or not base_run_id or runs_since_anchor >= ANCHOR_EVERY_RUNS
              or (len(added) + len(removed)) > ANCHOR_IF_DELTA_EXCEEDS * max(len(open_now), 1))
    rec = {"schema_version": OPENSET_VERSION, "run_id": run_id, "observed_at": observed_at,
           "n_open": len(open_now), "open_set_sha256": set_hash(open_now),
           "prev_run_id": prev_run_id, "base_run_id": run_id if anchor else base_run_id,
           "full": sorted(open_now) if anchor else None, "added": added, "removed": removed}
    return rec


def write_record(day_dir: str, rec: dict) -> str:
    path = os.path.join(day_dir, f"{rec['run_id']}.openset.json")
    with open(path, "w") as fh:
        json.dump(rec, fh, separators=(",", ":"))
    return path


def record_open_set(day_dir: str, run_id: str, observed_at: str, open_now, state: dict) -> dict:
    """Write the run's open set and advance the anchor bookkeeping held in the capture state.

    Called by the capture immediately before `last_seen` is updated. Never raises into the capture: an
    open-set failure must not cost the run its quotes.
    """
    try:
        rec = build_record(run_id, observed_at, open_now, last_seen=state.get("last_seen") or {},
                           prev_run_id=state.get("openset_last_run"), base_run_id=state.get("openset_anchor_run"),
                           runs_since_anchor=int(state.get("openset_runs_since_anchor") or 0))
        write_record(day_dir, rec)
        state["openset_last_run"] = run_id
        state["openset_anchor_run"] = rec["base_run_id"]
        state["openset_runs_since_anchor"] = 0 if rec["full"] is not None else int(state.get("openset_runs_since_anchor") or 0) + 1
        return {"written": True, "run_id": run_id, "n_open": rec["n_open"], "anchor": rec["full"] is not None,
                "added": len(rec["added"]), "removed": len(rec["removed"])}
    except (OSError, ValueError, TypeError) as exc:
        return {"written": False, "error": f"{type(exc).__name__}: {exc}"}


# ---------------------------------------------------------------------------------------------- reader
class OpenSetLedger:
    """Every run's open set, replayed once into per-ticker open intervals.

    Reconstructing 18k tickers x 144 runs as sets would be wasteful and is unnecessary: the chain is replayed
    once, and each ticker is recorded as the half-open run-index intervals during which it was open. A presence
    question is then a binary search, and the whole index costs one interval per ticker per listing episode.
    """

    def __init__(self, capture_root: str, *, run_ids=None):
        self.root = capture_root
        self.records: dict = {}
        for p in sorted(glob.glob(os.path.join(capture_root, "*", "*.openset.json"))):
            try:
                r = json.load(open(p))
            except (OSError, ValueError):
                continue
            rid = r.get("run_id") or os.path.basename(p)[:16]
            if run_ids is None or rid in run_ids:
                self.records[rid] = r
        self.runs = sorted(self.records)
        self.run_at = {r: _dt(self.records[r].get("observed_at")) for r in self.runs}
        self._index = None
        self.manifests: dict = {}
        for p in sorted(glob.glob(os.path.join(capture_root, "*", "*.manifest.json"))):
            try:
                m = json.load(open(p))
            except (OSError, ValueError):
                continue
            self.manifests[m.get("run_id") or os.path.basename(p)[:16]] = m

    # ---- replay
    def _build(self):
        if self._index is not None:
            return
        intervals: dict = {}
        live: dict = {}
        broken = []
        for i, rid in enumerate(self.runs):
            rec = self.records[rid]
            if rec.get("full") is not None:
                for t in list(live):                      # an anchor restates the truth: close anything it drops
                    if t not in set(rec["full"]):
                        intervals.setdefault(t, []).append((live.pop(t), i))
                for t in rec["full"]:
                    live.setdefault(t, i)
            else:
                prev = rec.get("prev_run_id")
                if prev is not None and (i == 0 or self.runs[i - 1] != prev):
                    broken.append(rid)                    # a gap in the chain: the replay from here is unproven
                for t in rec.get("removed") or ():
                    if t in live:
                        intervals.setdefault(t, []).append((live.pop(t), i))
                for t in rec.get("added") or ():
                    live.setdefault(t, i)
        n = len(self.runs)
        for t, s in live.items():
            intervals.setdefault(t, []).append((s, n))
        for t in intervals:
            intervals[t].sort()
        self._index = intervals
        self.chain_breaks = broken

    def verify(self) -> dict:
        """Replay every run and compare the reconstructed set against the hash the capture recorded."""
        self._build()
        ok, bad, no_hash = 0, [], 0
        cur = set()
        for i, rid in enumerate(self.runs):
            rec = self.records[rid]
            if rec.get("full") is not None:
                cur = set(rec["full"])
            else:
                cur -= set(rec.get("removed") or ())
                cur |= set(rec.get("added") or ())
            want = rec.get("open_set_sha256")
            if not want:
                no_hash += 1
            elif set_hash(cur) == want:
                ok += 1
            else:
                bad.append({"run_id": rid, "replayed_n": len(cur), "recorded_n": rec.get("n_open")})
        return {"runs": len(self.runs), "verified": ok, "mismatched": bad, "no_hash": no_hash,
                "chain_breaks": list(self.chain_breaks)}

    def open_at(self, ticker: str, run_id: str) -> bool | None:
        self._build()
        i = bisect.bisect_left(self.runs, run_id)
        if i >= len(self.runs) or self.runs[i] != run_id:
            return None
        for s, e in self._index.get(ticker, ()):
            if s <= i < e:
                return True
        return False

    def runs_in(self, start=None, end=None) -> list:
        """Run ids whose observation instant lies in [start, end)."""
        out = []
        for r in self.runs:
            t = self.run_at.get(r)
            if t is None:
                continue
            if (start is None or t >= start) and (end is None or t < end):
                out.append(r)
        return out

    # ---- the question this module exists for
    def presence(self, ticker: str, run_id: str, *, series_ticker: str | None = None, close_time=None) -> dict:
        """Was this exact contract open at this exact run, and if not, which of the five reasons applies?"""
        base = {"ticker": ticker, "run_id": run_id, "observed_at": None, "openset_version": OPENSET_VERSION}
        obs = self.run_at.get(run_id)
        base["observed_at"] = obs.isoformat() if obs else None
        got = self.open_at(ticker, run_id)
        if got is None:
            return {**base, "state": UNKNOWN, "reason": "no open-set record for this capture run"}
        if got:
            return {**base, "state": OPEN, "reason": None}
        series = series_ticker or ticker.rsplit("-", 2)[0]
        man = self.manifests.get(run_id) or {}
        smap = man.get("series") or {}
        s = smap.get(series)
        if s is None:
            return {**base, "state": SERIES_NOT_POLLED, "reason": f"series {series} was not fetched in this run", "series_ticker": series}
        if not s.get("complete"):
            return {**base, "state": PARTIAL_FETCH, "reason": f"series {series} fetch did not complete: absence is not evidence",
                    "series_ticker": series, "series_n": s.get("n")}
        ct = _dt(close_time)
        if ct is not None and obs is not None and obs >= ct:
            return {**base, "state": CLOSED, "reason": f"contract close_time {ct.isoformat()} had passed", "series_ticker": series}
        return {**base, "state": DELISTED, "reason": "series fetched completely and the contract was not in the open set"
                                                     + (f"; close_time {ct.isoformat()} had not been reached" if ct else ""),
                "series_ticker": series}

    def last_open_run(self, ticker: str, *, before=None) -> str | None:
        self._build()
        hi = len(self.runs)
        if before is not None:
            hi = 0
            for i, r in enumerate(self.runs):
                t = self.run_at.get(r)
                if t is not None and t < before:
                    hi = i + 1
        best = None
        for s, e in self._index.get(ticker, ()):
            if s < hi:
                best = min(e, hi) - 1
        return self.runs[best] if best is not None and 0 <= best < len(self.runs) else None

    def disappearance(self, ticker: str, *, after_run: str | None, until, series_ticker: str | None = None,
                      close_time=None) -> dict:
        """Why does no later pre-kickoff observation of this contract exist?

        Classifies every run between the confirming run and kickoff. The answer a close needs is the FIRST
        market-meaningful state after the last open run: DELISTED means the close stands on its last live
        observation, PARTIAL_FETCH or SERIES_NOT_POLLED mean the gap is the capture's and nothing can be
        concluded from the absence.
        """
        runs = self.runs_in(self.run_at.get(after_run), until) if after_run else self.runs_in(None, until)
        runs = [r for r in runs if (after_run is None or r > after_run)]
        counts, first = {}, None
        for r in runs:
            st = self.presence(ticker, r, series_ticker=series_ticker, close_time=close_time)["state"]
            counts[st] = counts.get(st, 0) + 1
            if first is None and st != OPEN:
                first = {"run_id": r, "state": st, "observed_at": self.run_at[r].isoformat() if self.run_at.get(r) else None}
        # No later runs at all means the confirming run WAS the last pre-kickoff run: nothing is missing, so
        # nothing needs explaining. An absence is unexplained only when the first thing after the last sighting
        # is a capture failure rather than a market event.
        return {"runs_examined": len(runs), "by_state": counts, "first_non_open": first,
                "still_open_at_last_run": counts.get(OPEN, 0) == len(runs),
                "explained": first is None or first["state"] in MARKET_STATES}
