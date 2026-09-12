"""THE POINT-IN-TIME CONTRACT. One rule, written once, enforced once.

    source_observed_or_retrieved_at <= projection.data_cutoff

The market snapshot is the research cutoff. A projection frozen against it is a claim about what was knowable
at that instant, and information that arrived later must not be able to influence it -- not the probability,
not the context, not the executability.

WHY THIS MODULE EXISTS AT ALL
-----------------------------
The rule was previously implemented ad hoc, per source, and the implementations diverged. The audit found the
same defect in four places and its correct counterpart in four others, sometimes in the same file:

    weather        filtered its capture runs on `run_dt > as_of: continue`          -- correct
    availability   took `sorted(glob(...))[-1]`                                     -- no cutoff at all
    trade tape     filtered directory AND row                                       -- correct
    injuries       read the whole season file                                       -- no cutoff at all
    books          bounded by run id only, while its docstring claimed observed_at   -- half correct
    quotes         bounded files by name, never rows, and nothing on the default path

Four correct implementations did not prevent four wrong ones, because each was written next to its own source
instead of next to the rule. So the rule now lives here, the selection helpers live here, and every loader
calls them. A source that cannot answer "when was this true?" does not get to be used as if it could.

THE THREE THINGS THIS MODULE PROVIDES
-------------------------------------
1. `pick_at_or_before` / `files_at_or_before` -- the replacement for `sorted(glob(...))[-1]`. Selection is
   always "the newest evidence whose vintage is at or before the cutoff", never "the newest evidence".

2. `VintageLedger` -- every time-sensitive source a run actually consumed, with the vintage it was read at.
   The ledger is the audit trail: it is frozen onto the record's lineage, so a record carries the evidence
   needed to re-check its own compliance long after the files have been overwritten.

3. The invariants -- `assert_not_from_the_future`, `outcome_leak` and `assert_clean` -- applied at the
   granularity each one belongs to. See below: they are not the same rule, and conflating them either stops the
   system running or lets a replay fabricate evidence.

THREE OUTCOMES, AND ONLY ONE OF THEM IS A BREACH
------------------------------------------------
    NO evidence at or before the cutoff     the value is UNKNOWN with a reason. Normal, honest and common
                                            early in a season. Never an error.

    SKEW: a source dated after the market   recorded, not refused. In normal operation this is unavoidable and
    snapshot but before kickoff             routine -- the capture conductor writes a snapshot, the projection
                                            job starts afterwards and downloads nflverse at that point, so the
                                            nflverse vintage is always a little later than the market's.
                                            Measured on a real run: 2,234 seconds. Nothing about the outcome
                                            can live in that gap, and refusing it would refuse every run. The
                                            gap is published as the record's `information_frontier`.

    OUTCOME LEAK: a source dated at or      refused, per game. A file retrieved after the game contains the
    after the kickoff it predicts           result, so a "prospective" record built on it is fiction. This is
                                            what a replay hits every time -- projecting a week-1 snapshot today
                                            reads nflverse files that post-date the games by months. The
                                            affected records lose their probability and are relabelled; records
                                            for a LATER kickoff are untouched, because a file dated after the
                                            1pm game says nothing about the 4pm one.

A source dated after the run's own wall clock is impossible and fails the whole run.

STATIC SOURCES
--------------
A source with no defensible vintage must be declared `static=True` with the reason it is safe -- meaning its
content cannot encode anything about the outcome being predicted (a stadium's roof type, a division map). The
declaration is recorded in the ledger so the assumption is reviewable rather than implicit.

Version: pit-1.0.0.
"""
from __future__ import annotations

import glob as _glob
import os
import re
from dataclasses import dataclass, field
from datetime import datetime, timezone

PIT_VERSION = "pit-1.0.0"

# a compact capture/context run id: 20260911T005211Z
RUN_ID_RE = re.compile(r"(\d{8}T\d{6}Z)")
UNKNOWN = "UNKNOWN"


class PointInTimeViolation(RuntimeError):
    """A time-sensitive source was consumed at a vintage later than the projection's data cutoff."""


def as_utc(v):
    """A timezone-aware UTC datetime from a datetime, an ISO string, or a compact run id. None stays None."""
    if v is None or v == "":
        return None
    if isinstance(v, datetime):
        return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
    s = str(v)
    m = RUN_ID_RE.fullmatch(s.strip())
    if m:
        return datetime.strptime(s.strip(), "%Y%m%dT%H%M%SZ").replace(tzinfo=timezone.utc)
    try:
        d = datetime.fromisoformat(s.replace("Z", "+00:00"))
    except ValueError:
        return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def run_id_of(path: str):
    """The run id embedded in a capture/context filename, as a datetime. None when the name carries none."""
    m = RUN_ID_RE.search(os.path.basename(path))
    return as_utc(m.group(1)) if m else None


def dir_run_id_of(path: str):
    """The run id of the file's PARENT DIRECTORY (context captures are `<date>/<run_id>.<kind>.json`)."""
    m = RUN_ID_RE.search(os.path.basename(os.path.dirname(path)))
    return as_utc(m.group(1)) if m else None


# ---------------------------------------------------------------------------------------------- selection
def pick_at_or_before(candidates, cutoff, *, vintage=None):
    """The newest candidate whose vintage is at or before `cutoff`, or (None, None).

    `candidates` is an iterable of items; `vintage` maps an item to its instant (default: treat the item as a
    path and read the run id from its filename). This is the function that replaces `sorted(glob(...))[-1]`
    everywhere -- the difference between the two is the whole point of this module.
    """
    vin = vintage or run_id_of
    cut = as_utc(cutoff)
    best, best_v = None, None
    for c in candidates:
        v = as_utc(vin(c))
        if v is None or (cut is not None and v > cut):
            continue
        if best_v is None or v > best_v:
            best, best_v = c, v
    return best, best_v


def files_at_or_before(pattern: str, cutoff, *, vintage=None) -> list:
    """Every file matching `pattern` whose vintage is at or before the cutoff, oldest first."""
    vin = vintage or run_id_of
    cut = as_utc(cutoff)
    out = []
    for p in _glob.glob(pattern):
        v = as_utc(vin(p))
        if v is None or (cut is not None and v > cut):
            continue
        out.append((v, p))
    return [p for _v, p in sorted(out)]


def newest_file_at_or_before(pattern: str, cutoff, *, vintage=None):
    fs = files_at_or_before(pattern, cutoff, vintage=vintage)
    if not fs:
        return None, None
    vin = vintage or run_id_of
    return fs[-1], as_utc(vin(fs[-1]))


# ---------------------------------------------------------------------------------------------- the ledger
@dataclass
class SourceUse:
    name: str
    vintage: str | None          # ISO instant the source's content was true / retrieved
    kind: str                    # capture | context | nflverse | derived | registry
    path: str | None = None
    static: bool = False
    static_reason: str | None = None
    detail: dict = field(default_factory=dict)

    def to_dict(self):
        d = {"name": self.name, "vintage": self.vintage, "kind": self.kind, "path": self.path}
        if self.static:
            d.update(static=True, static_reason=self.static_reason)
        if self.detail:
            d["detail"] = self.detail
        return d


class VintageLedger:
    """Every time-sensitive source one projection run consumed, and whether any of them read the future."""

    def __init__(self, cutoff, *, label: str = ""):
        self.cutoff = as_utc(cutoff)
        self.label = label
        self.uses: list = []

    def record(self, name: str, vintage, *, kind: str = "capture", path: str | None = None, **detail) -> SourceUse:
        v = as_utc(vintage)
        u = SourceUse(name=name, vintage=v.isoformat() if v else None, kind=kind, path=path, detail=detail or {})
        self.uses.append(u)
        return u

    def record_static(self, name: str, reason: str, *, kind: str = "registry", path: str | None = None) -> SourceUse:
        """Declare a source safe without a vintage, and say why. The claim is recorded, not assumed."""
        u = SourceUse(name=name, vintage=None, kind=kind, path=path, static=True, static_reason=reason)
        self.uses.append(u)
        return u

    def record_absent(self, name: str, reason: str, *, kind: str = "capture") -> SourceUse:
        """No evidence at or before the cutoff. Honest missing information, never a violation."""
        u = SourceUse(name=name, vintage=None, kind=kind, detail={"absent_reason": reason})
        self.uses.append(u)
        return u

    def sources_after_cutoff(self) -> list:
        """Sources whose vintage is later than the market snapshot. This is SKEW, not a breach -- see below.

        Deliberately not called `violations`: in normal operation the projection job starts after the capture
        run it prices and downloads nflverse at that point, so this list is routinely non-empty and means only
        that the information frontier is later than the market observation. The breach is `outcome_leak`.
        """
        if self.cutoff is None:
            return []
        out = []
        for u in self.uses:
            v = as_utc(u.vintage)
            if v is not None and not u.static and v > self.cutoff:
                out.append({"name": u.name, "vintage": u.vintage, "cutoff": self.cutoff.isoformat(),
                            "skew_seconds": round((v - self.cutoff).total_seconds(), 3), "path": u.path})
        return out

    # ---- the two invariants, and why they are not the same one
    #
    # A projection mixes sources with different vintages, and only some of the differences are dangerous.
    #
    #   SKEW is the gap between a source's vintage and the market snapshot. In normal operation it is positive
    #   and unavoidable: the capture conductor writes a snapshot, the projection job starts afterwards and
    #   downloads nflverse at that point, so the nflverse files are always a few dozen minutes "after" the
    #   market. Measured on a real run: the injury file was retrieved 2,234s after the snapshot. Nothing about
    #   the outcome can be in that gap, and refusing it would refuse every production run.
    #
    #   AN OUTCOME LEAK is a source dated at or after the KICKOFF it is being used to predict. That is the real
    #   boundary. A file retrieved after the game contains the result, and a "prospective" record built on it
    #   is fiction. This is the case that replay hits every time: projecting a week-1 snapshot today reads
    #   nflverse files that post-date the games by months.
    #
    # So skew is measured and recorded; an outcome leak is refused. Conflating them either lets replay
    # fabricate evidence or stops the system running at all.
    def max_vintage(self):
        """The projection's real information frontier: the newest source it actually consumed."""
        vs = [as_utc(u.vintage) for u in self.uses if u.vintage and not u.static]
        return max(vs) if vs else None

    def skews(self) -> list:
        if self.cutoff is None:
            return []
        out = []
        for u in self.uses:
            v = as_utc(u.vintage)
            if v is not None and not u.static:
                out.append({"name": u.name, "vintage": u.vintage,
                            "skew_seconds": round((v - self.cutoff).total_seconds(), 1)})
        return sorted(out, key=lambda d: -d["skew_seconds"])

    def outcome_leak(self, kickoff) -> list:
        """Sources dated at or after this kickoff. Non-empty means a record for that game cannot be prospective."""
        k = as_utc(kickoff)
        if k is None:
            return []
        out = []
        for u in self.uses:
            v = as_utc(u.vintage)
            if v is not None and not u.static and v >= k:
                out.append({"name": u.name, "vintage": u.vintage, "kickoff": k.isoformat(),
                            "after_kickoff_seconds": round((v - k).total_seconds(), 1)})
        return out

    def assert_not_from_the_future(self, now, *, what: str = "any record") -> None:
        """No source may be dated after this run itself. A file from the future is a broken clock or a bug."""
        n = as_utc(now)
        bad = [{"name": u.name, "vintage": u.vintage} for u in self.uses
               if u.vintage and not u.static and as_utc(u.vintage) > n]
        if bad:
            raise PointInTimeViolation(
                f"{len(bad)} source(s) are dated after this run ({n.isoformat()}); refusing to write {what}: {bad}")

    def assert_clean(self, *, what: str = "PROSPECTIVE_FROZEN records", max_skew_seconds: float | None = None) -> None:
        """Fail closed on skew beyond a declared tolerance. Outcome leaks are refused per record, not here."""
        if max_skew_seconds is None:
            return
        bad = [s for s in self.skews() if s["skew_seconds"] > max_skew_seconds]
        if bad:
            lines = "\n".join(f"  {b['name']}: vintage {b['vintage']} is {b['skew_seconds']:.0f}s after the "
                              f"market snapshot" for b in bad)
            raise PointInTimeViolation(
                f"{len(bad)} source(s) exceed the {max_skew_seconds:.0f}s vintage-skew tolerance; refusing to "
                f"write {what}.\n{lines}\n"
                "Beyond this gap the record is not honestly a view of the snapshot it names.")

    def to_block(self) -> dict:
        """Frozen onto the record's lineage so the compliance claim survives the files being overwritten."""
        mv = self.max_vintage()
        return {"pit_version": PIT_VERSION, "data_cutoff": self.cutoff.isoformat() if self.cutoff else None,
                "information_frontier": mv.isoformat() if mv else None,
                "sources": [u.to_dict() for u in self.uses], "skews": self.skews(),
                "n_sources": len(self.uses),
                "n_absent": sum(1 for u in self.uses if u.vintage is None and not u.static)}

    def summary(self) -> dict:
        by_kind = {}
        for u in self.uses:
            by_kind[u.kind] = by_kind.get(u.kind, 0) + 1
        sk = self.skews()
        mv = self.max_vintage()
        return {"pit_version": PIT_VERSION, "cutoff": self.cutoff.isoformat() if self.cutoff else None,
                "information_frontier": mv.isoformat() if mv else None,
                "sources": len(self.uses), "by_kind": by_kind,
                "max_skew_seconds": (sk[0]["skew_seconds"] if sk else 0.0),
                "max_skew_source": (sk[0]["name"] if sk else None),
                "absent": sum(1 for u in self.uses if u.vintage is None and not u.static)}


# ---------------------------------------------------------------------------------------------- row guards
def row_at_or_before(row: dict, cutoff, *, key: str = "observed_at") -> bool:
    """Is this row's own observation instant at or before the cutoff? A row with no instant is REFUSED."""
    v = as_utc(row.get(key))
    cut = as_utc(cutoff)
    if v is None:
        return False
    return cut is None or v <= cut


def strictly_before_kickoff(row: dict, kickoff, *, key: str = "observed_at") -> bool:
    """Pregame means strictly before kickoff, judged on the row's OWN instant -- never on which file it is in.

    The incumbent capture decides `pregame` when it builds its candidate list and fetches books minutes later,
    so `books.jsonl` demonstrably contains rows observed after kickoff (646 of 677,253 measured, worst 3.9
    minutes past). A consumer that trusts the filename inherits that defect; one that checks the row does not.
    """
    v = as_utc(row.get(key))
    k = as_utc(kickoff)
    if v is None or k is None:
        return False
    return v < k
