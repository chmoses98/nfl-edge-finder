"""APPEND-ONLY AMENDMENTS to the economics of an owner-wager settlement. Accounting, not model evidence.

WHY THIS EXISTS
---------------
kalshi-bet-router's settlement economics v1 computed ``net = gross - stake - fee_cost``. ``stake`` already
includes the entry fee from the order's own fills, and Kalshi's settlement ``fee_cost`` is the market
position's cumulative trading fee (every owner order on the market, both sides). So v1 subtracted each single
order's fee twice and, on a YES+NO pair, the market's combined fee again on each leg: 2026 week 2 was
understated by $112.24. v2 (`router-settlement-economics.v2`) computes ``net = gross - stake`` and only when
the exchange's fee_cost equals those entry fees.

The settlements already filed under v1 are evidence of what was recorded at the time, and they are
immutable. So a v2 figure for a v1 settlement is not written over it; it is written BESIDE it, as an
amendment that names what it supersedes -- the repository's rule for any revision ("a new file with
`amends` pointing at the original"):

    RAW EVIDENCE                 the exchange facts in the wager and settlement (untouched)
    RECORDED ECONOMICS (v1)      the settlement record as filed (untouched)
    CANONICAL ECONOMICS          the settlement, with the newest valid amendment's corrected fields applied

WHAT MAKES AN AMENDMENT ADMISSIBLE (fail closed)
------------------------------------------------
* it amends an existing settlement, found by the settlement's own minted id, in the same season/week;
* the prior economics version is v1 (the record carries none, or says v1) and the amended one is v2;
* ONLY the economics fields differ (`net_profit_loss`, `refusals`): a different result, payout, side, market
  or settlement time is not a fee correction -- it is a CONFLICT, refused;
* the destination re-derives the corrected figure itself: a stated v2 net must equal ``gross_return - stake``
  of the wager this ledger holds, to a hundredth of a cent. A v2 row whose net the destination cannot
  reproduce is refused, whatever the router says;
* one amendment id per (settlement, amended version): a re-delivery of the same correction is a no-op, a
  DIFFERENT correction for the same pair is a CONFLICT.
"""
from __future__ import annotations

import hashlib
import json
import os

SCHEMA_VERSION = "nfl_wager_settlement_amendment.v1"
ID_PREFIX = "amd"
KIND = "wager_settlement_amendments"

ECONOMICS_V1 = "router-settlement-economics.v1"
ECONOMICS_V2 = "router-settlement-economics.v2"
REASON_FEE_DOUBLE_COUNT = "FEE_DOUBLE_COUNT_CORRECTION"

#: The only fields an economics amendment may supersede.
AMENDABLE_FIELDS = ("net_profit_loss", "refusals")
DERIVATION_V2 = ("net_profit_loss = gross_return - stake; stake = contracts x execution price + the entry fee "
                 "the exchange charged on the order's fills; admitted only where the settlement's fee_cost equals "
                 "the entry fees of the owner's orders on the market (the position's cumulative trading fee)")
NET_TOLERANCE = 1e-4


class AmendmentRefused(Exception):
    """This correction cannot be admitted, and admitting it anyway would be worse."""


def economics_version_of(record: dict) -> str:
    return record.get("economics_version") or ECONOMICS_V1


def mint_amendment_id(settlement_id: str, amended_version: str) -> str:
    digest = hashlib.sha256(f"{settlement_id}|{amended_version}".encode("utf-8")).hexdigest()[:24]
    return f"{ID_PREFIX}-{digest}"


def record_sha256(path: str) -> str:
    with open(path, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def _same(a, b) -> bool:
    if isinstance(a, (int, float)) and isinstance(b, (int, float)) and not isinstance(a, bool) \
            and not isinstance(b, bool):
        return abs(float(a) - float(b)) <= 1e-9
    return a == b


def build_amendment(existing: dict, existing_path: str, incoming: dict, wager: dict, *,
                    provenance: str) -> dict:
    """The amendment record for (filed v1 settlement, incoming v2 settlement), or AmendmentRefused."""
    prior, amended = economics_version_of(existing), economics_version_of(incoming)
    if prior != ECONOMICS_V1 or amended != ECONOMICS_V2:
        raise AmendmentRefused(f"an economics amendment goes from {ECONOMICS_V1} to {ECONOMICS_V2}; "
                               f"got {prior} -> {amended}")
    if existing.get("settlement_id") != incoming.get("settlement_id"):
        raise AmendmentRefused("the incoming settlement is not the filed one")
    if (existing.get("season"), existing.get("week")) != (wager.get("season"), wager.get("week")):
        raise AmendmentRefused("the filed settlement is not in its wager's season/week")
    compared = ("source_bet_key", "season", "week", "market_ticker", "side", "settlement_status", "settled_at",
                "result", "gross_return", "venue")
    other = [f for f in compared if not _same(existing.get(f), incoming.get(f))]
    if other:
        raise AmendmentRefused(f"fields other than economics differ ({other}); that is not a fee correction")
    superseded = {f: {"prior": existing.get(f), "corrected": incoming.get(f)}
                  for f in AMENDABLE_FIELDS if not _same(existing.get(f), incoming.get(f))}
    if not superseded:
        raise AmendmentRefused("nothing differs; there is nothing to amend")
    net = incoming.get("net_profit_loss")
    if net is not None:
        gross, stake = incoming.get("gross_return"), wager.get("stake")
        if gross is None or stake is None or abs(float(net) - (float(gross) - float(stake))) > NET_TOLERANCE:
            raise AmendmentRefused("the corrected net does not equal gross_return - stake of the wager this "
                                   "ledger holds; the destination cannot reproduce it")
        if incoming.get("refusals"):
            raise AmendmentRefused("a stated net may not carry a refusal")
    elif not incoming.get("refusals"):
        raise AmendmentRefused("an absent corrected net must carry its refusal")
    settlement_id = existing["settlement_id"]
    return {
        "amendment_id": mint_amendment_id(settlement_id, amended),
        "schema_version": SCHEMA_VERSION,
        "amends": settlement_id,
        "amends_kind": "wager_settlements",
        "source_bet_key": existing.get("source_bet_key"),
        "season": existing.get("season"),
        "week": existing.get("week"),
        "reason_code": REASON_FEE_DOUBLE_COUNT,
        "prior_economics_version": prior,
        "amended_economics_version": amended,
        "superseded_fields": superseded,
        "derivation": DERIVATION_V2,
        "original_record_sha256": record_sha256(existing_path),
        "provenance": provenance,
    }


def same_correction(a: dict, b: dict) -> bool:
    """Two amendments carry the same correction (identity and corrected values; hashes/provenance aside)."""
    keys = ("amendment_id", "amends", "amended_economics_version", "reason_code")
    if any(a.get(k) != b.get(k) for k in keys):
        return False
    fa, fb = a.get("superseded_fields") or {}, b.get("superseded_fields") or {}
    return set(fa) == set(fb) and all(_same(fa[f].get("corrected"), fb[f].get("corrected")) for f in fa)


def validate(record: dict) -> list:
    problems = []
    for name in ("amendment_id", "amends", "source_bet_key", "reason_code", "prior_economics_version",
                 "amended_economics_version", "original_record_sha256"):
        if not isinstance(record.get(name), str) or not record.get(name):
            problems.append(f"{name} is required")
    if record.get("schema_version") != SCHEMA_VERSION:
        problems.append("schema_version")
    fields = record.get("superseded_fields")
    if not isinstance(fields, dict) or not fields or set(fields) - set(AMENDABLE_FIELDS):
        problems.append("superseded_fields must name only economics fields")
    if record.get("amendment_id") != mint_amendment_id(record.get("amends") or "",
                                                       record.get("amended_economics_version") or ""):
        problems.append("amendment_id is not minted from (amends, amended_economics_version)")
    return problems


def read_amendments(root: str) -> dict:
    """settlement_id -> [amendment, ...] from a handicap-data checkout (empty when the kind was never written)."""
    base = os.path.join(root, "data", KIND)
    out: dict = {}
    if not os.path.isdir(base):
        return out
    for directory, _subdirs, names in os.walk(base):
        for name in sorted(names):
            if name.endswith(".json"):
                with open(os.path.join(directory, name), encoding="utf-8") as handle:
                    doc = json.load(handle)
                out.setdefault(doc.get("amends"), []).append(doc)
    return out


VERSION_ORDER = (ECONOMICS_V1, ECONOMICS_V2)


def canonical_settlement(settlement: dict, amendments: list) -> dict:
    """The settlement with its NEWEST amendment's corrected fields applied -- a VIEW, never written back.

    Adds `economics_version` (canonical), `recorded_economics_version`, `amendment_status`
    (ORIGINAL / AMENDED), `amendment_id` and `recorded_<field>` for every superseded field. More than one
    amendment for the same version is impossible by construction (one id per pair); a set of amendments that
    is not totally ordered by version is refused rather than resolved by picking one.
    """
    out = dict(settlement)
    out["recorded_economics_version"] = economics_version_of(settlement)
    out["economics_version"] = economics_version_of(settlement)
    out["amendment_status"] = "ORIGINAL"
    if not amendments:
        return out
    versions = [a.get("amended_economics_version") for a in amendments]
    if len(set(versions)) != len(versions) or any(v not in VERSION_ORDER for v in versions):
        raise AmendmentRefused(f"competing amendments for {settlement.get('settlement_id')}: {versions}")
    newest = max(amendments, key=lambda a: VERSION_ORDER.index(a["amended_economics_version"]))
    for field, change in (newest.get("superseded_fields") or {}).items():
        out[f"recorded_{field}"] = settlement.get(field)
        out[field] = change.get("corrected")
    out["economics_version"] = newest["amended_economics_version"]
    out["amendment_status"] = "AMENDED"
    out["amendment_id"] = newest["amendment_id"]
    return out
