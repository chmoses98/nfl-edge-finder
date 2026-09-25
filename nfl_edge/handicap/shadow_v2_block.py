"""Shadow v2's view of the board, attached to the handicap packet (read-only, stdlib-only).

WHY THIS EXISTS
---------------
Shadow v2 already carried a research projection for thousands of contracts the RUN NFL report printed as
`UNSUPPORTED_MODEL` and nothing else. On the 2026 week 2 board that was every 1H / 2H / 1Q-4Q spread,
total, team total, period winner and both-teams-score contract -- about 3,100 rows -- against 2,790
`PROJECTABLE_NOT_YET_VALIDATED` period-engine projections sitting in `market-data` at the same instant.
An operator reading the game file saw a price and a refusal, and had no way to know the repository already
held a legitimate projection for that exact ticker. That is a reporting defect, not a modelling one.

WHAT IT IS NOT
--------------
It is **not** a promotion. A Shadow v2 probability never becomes `model_probability`, is never mixed into
the incumbent's disagreement ranking, and never reaches recommendation, staking or preflight. It is
reported next to the incumbent's own state, carrying its engine, engine version, model version, snapshot,
data cutoff, evidence class and support state, so the reader can see exactly what kind of number it is.
`PROJECTABLE_NOT_YET_VALIDATED` is printed as `PROJECTABLE_NOT_YET_VALIDATED`; nothing here relabels it.

THE ARMS, AND WHY NONE OF THEM IS "THE" NUMBER
----------------------------------------------
A Shadow v2 snapshot writes one file per model arm. `BOARD_V2` answers the game / period / season / joint
families from their own engines; the three player arms answer the player ladders from three different
distributions of the same statistic:

    DATA_PLAYER_DIST      opportunity x efficiency fitted on football data only      independent view
    MARKET_PLAYER_DIST    the distribution reconstructed FROM the Kalshi ladder       market-derived
    HYBRID_PLAYER_DIST    the two blended                                             partly market-derived

Choosing one and calling it "the model" would silently present a market-derived number as an independent
football opinion, which is the exact error the reconciliation work exists to prevent. So every arm that
produced a row is reported, and `primary_arm` points at the only arm that is an independent football view
of that question -- `BOARD_V2` for everything it owns, `DATA_PLAYER_DIST` for the player ladders -- with
the market-derived arms beside it and labelled.

POINT IN TIME
-------------
All arms of ONE snapshot, never a mixture: arms are written in the same run from the same capture, and
taking the newest file per arm independently would let one arm read a later market than another and
produce a row whose numbers were never simultaneously true. The snapshot is chosen by its run stamp at or
before the packet's build instant, exactly as `sim_block.load_latest` chooses a simulation run.

Two further refusals, applied per row rather than per snapshot:

  * a row that is not `PROSPECTIVE_FROZEN` never contributes a probability -- a walk-forward research
    reconstruction is not a pregame projection and must not be readable as one;
  * a row whose `flags.betting_authorized` is anything but false is dropped entirely and named in
    `refused_rows`, because the only correct value is false and a true one means the artifact is not what
    this reader believes it is.

`POST_KICKOFF` rows carry no probability by construction (`ProjectionRecord.finalize` refuses one), so a
started game cannot leak a projection through this path.
"""
from __future__ import annotations

import glob
import gzip
import json
import os
from datetime import datetime, timezone

import nfl_edge.evaluation.eligibility as EL          # stdlib-only; module paths for the report-isolation audit
import nfl_edge.evaluation.research_record as RR       # family_group(): the key eligibility is decided on

DIRNAME = os.path.join("data", "shadow", "v2", "projections")
BOARD_ARM = "BOARD_V2"
PLAYER_ARMS = ("DATA_PLAYER_DIST", "MARKET_PLAYER_DIST", "HYBRID_PLAYER_DIST", "DATA_PLAYER_V3", "HYBRID_PLAYER_V3",
               "DATA_PLAYER_V4", "HYBRID_PLAYER_V4", "DATA_PLAYER_V5", "HYBRID_PLAYER_V5")
ARMS = (BOARD_ARM,) + PLAYER_ARMS
# the arm that is an INDEPENDENT football view of the question, per engine, in order of preference. Anything not
# named here falls back to BOARD_V2, which is the arm that owns every non-player family. DATA_PLAYER_V3 first:
# DATA_PLAYER_DIST carries a known input defect (nfl_edge/evaluation/eligibility.py KNOWN_DEFECTS) and is primary
# only on a snapshot written before v3 existed -- where its probability is withheld as DISABLED. DATA_PLAYER_V4 is a
# challenger reported beside v3 (never promoted into the primary slot by being newer): it is primary only on a
# snapshot with no v3 row at all. Primary says nothing about authority either way. DATA_PLAYER_V5 (point-in-time QB,
# docs/PLAYER_V5.md) is supporting research exactly like V4: after V4, primary only when neither v3 nor v4 answered.
INDEPENDENT_ARMS_BY_ENGINE = {"PLAYER": ("DATA_PLAYER_V3", "DATA_PLAYER_V4", "DATA_PLAYER_V5", "DATA_PLAYER_DIST")}
MARKET_DERIVED_ARMS = ("MARKET_PLAYER_DIST", "HYBRID_PLAYER_DIST", "HYBRID_PLAYER_V3", "HYBRID_PLAYER_V4", "HYBRID_PLAYER_V5")
# the V5 arms carry the team's quarterback resolution; RUN NFL prints its reason only where it says something
V5_ARMS = ("DATA_PLAYER_V5", "HYBRID_PLAYER_V5")
PROBABILITY_STATES = ("PRICED", "PROJECTABLE_NOT_YET_VALIDATED")
PROSPECTIVE_FROZEN = "PROSPECTIVE_FROZEN"
RESEARCH_ONLY = "RESEARCH ONLY -- a Shadow v2 projection is not validated and authorises nothing"

# Provenance that is CONSTANT for an (arm, engine, engine version, distribution version) within one
# snapshot. It is registered once in a per-packet table and referenced by key from each market row.
# Repeating it on every row of every arm is what took `packet.json` from 43MB to 96MB on the 2026 week 2
# slate -- past the point where the report branch can be published at all -- for eleven thousand copies of
# the same fifteen strings.
# WHAT MAY BE SHARED AND WHAT MAY NOT. `_PROVENANCE_ID` is the KEY: two rows share a provenance entry only
# when every one of these agrees, and `evidence_class` is among them for a reason that cost a wrong artifact
# to find. It is NOT constant within an arm -- a post-kickoff game's rows are HISTORICAL_RESEARCH while the
# pregame slate's are PROSPECTIVE_FROZEN -- so keying without it let whichever row was read first stamp its
# evidence class on every other row of the same arm, and a table built from a 16-game board reported all
# seven entries as HISTORICAL_RESEARCH while 7,830 genuinely prospective probabilities pointed at them.
#
# `observed_at` is the per-TICKER market observation instant and can never be shared at all, so it is not in
# the table; a row whose own market observation differs from the packet's says so through
# `quoted_against_different_market`.
_PROVENANCE_ID = ("model_arm", "engine", "engine_version", "distribution_version", "model_version",
                  "evidence_class", "horizon_label")
_PROVENANCE_KEYS = _PROVENANCE_ID + ("schema_version", "snapshot_id", "data_cutoff")

def _stamp(dt: datetime | None) -> str | None:
    return dt.astimezone(timezone.utc).strftime("%Y%m%dT%H%M%SZ") if dt else None


def _arm_of(path: str) -> str:
    return os.path.basename(path).split(".")[1]


def _snapshot_of(path: str) -> str:
    return os.path.basename(path).split(".")[0]


def latest_snapshot_id(roots, at_or_before: datetime | None = None) -> str | None:
    """The newest Shadow v2 snapshot stamp at or before the instant, over all roots.

    Chosen on the BOARD arm, which every snapshot writes: a snapshot whose board file is absent is an
    incomplete publication and must not be selected on the strength of a player arm alone.
    """
    stamp = _stamp(at_or_before)
    stamps = set()
    for root in roots:
        for path in glob.glob(os.path.join(root, DIRNAME, "*", f"*.{BOARD_ARM}.projections.jsonl.gz")):
            s = _snapshot_of(path)
            if stamp is None or s <= stamp:
                stamps.add(s)
    return max(stamps) if stamps else None


def load_snapshot(roots, snapshot_id: str, *, game_ids=None) -> tuple[dict, dict]:
    """Every arm of ONE snapshot -> ({ticker: {arm: row}}, manifest).

    `game_ids`, when given, restricts the rows kept to that set of games; season/week filtering is left to
    the caller because a projection row carries both and the packet already knows which it wants.
    """
    by_ticker: dict = {}
    arms_seen, files, refused = {}, [], []
    for root in roots:
        for arm in ARMS:
            if arm in arms_seen:
                continue                     # first root wins: the corpus is write-once, so copies are identical
            matches = glob.glob(os.path.join(root, DIRNAME, "*", f"{snapshot_id}.{arm}.projections.jsonl.gz"))
            if not matches:
                continue
            path = matches[0]
            files.append(path)
            n = 0
            with gzip.open(path, "rt") as f:
                for line in f:
                    r = json.loads(line)
                    if game_ids is not None and r.get("game_id") not in game_ids:
                        continue
                    if (r.get("flags") or {}).get("betting_authorized"):
                        refused.append({"ticker": r.get("ticker"), "arm": arm,
                                        "reason": "flags.betting_authorized is not false"})
                        continue
                    by_ticker.setdefault(r["ticker"], {})[arm] = r
                    n += 1
            arms_seen[arm] = {"path": path, "rows_kept": n}
    manifest = {"snapshot_id": snapshot_id, "arms": arms_seen, "arms_missing": [a for a in ARMS if a not in arms_seen],
                "tickers": len(by_ticker), "refused_rows": refused[:50], "refused_row_count": len(refused)}
    return by_ticker, manifest


def load_latest(roots, at_or_before: datetime | None = None, *, game_ids=None) -> tuple[dict, dict] | tuple[None, None]:
    """The newest complete Shadow v2 snapshot at or before the instant. ({ticker: {arm: row}}, manifest)."""
    snap = latest_snapshot_id(roots, at_or_before)
    if snap is None:
        return None, None
    return load_snapshot(roots, snap, game_ids=game_ids)


def _probability(row: dict) -> tuple[float | None, float | None, str | None]:
    """(p_yes, contract_value, withheld_reason). A number is shown only when the row is entitled to one."""
    if row.get("support_state") not in PROBABILITY_STATES:
        return None, None, None                                  # the state itself is the explanation
    if row.get("evidence_class") != PROSPECTIVE_FROZEN:
        return None, None, f"evidence class {row.get('evidence_class')!r} is not a pregame projection"
    if row.get("p_yes") is None:
        return None, None, "row carries the state but no probability"
    return row.get("p_yes"), row.get("contract_value"), None


def provenance_key(row: dict) -> str:
    """The identity of one row's shareable provenance: arm, engine, every version, evidence class, horizon."""
    return "|".join(str(row.get(k) or "") for k in _PROVENANCE_ID)


def register_provenance(row: dict, table: dict) -> str:
    """Record this row's constant provenance once and return the SHORT id the market row points at.

    The table is `{short_id: {...}}` and the short id is what appears on eleven thousand market rows, so it
    is `v2p0`, not a seventy-character version string repeated five times per contract.
    """
    key = provenance_key(row)
    by_key = table.setdefault("_by_key", {})
    if key not in by_key:
        sid = f"v2p{len(by_key)}"
        by_key[key] = sid
        table[sid] = {k: row.get(k) for k in _PROVENANCE_KEYS}
    return by_key[key]


def arm_view(row: dict, table: dict, eligibility: dict | None = None) -> dict:
    """One arm's answer for one contract: only what varies per contract, plus a provenance id.

    Everything that is the same for every contract this arm answered -- the engine and its version, the
    distribution version, the model version, the schema, the snapshot, the evidence class, the market
    observation instant and the data cutoff -- lives once in the provenance table and is reached through
    `provenance`. `contract_value` is written only when it differs from `p_yes` (it differs exactly where a
    settlement branch is folded in), and `reason` only where there is no probability to explain.
    """
    p, cv, withheld = _probability(row)
    # PRODUCTION ELIGIBILITY (nfl_edge/evaluation/eligibility.py): every arm answer says what authority it has.
    # A DISABLED arm (a known defect) shows no number at all; every other status is printed beside the number.
    elig = EL.status_for(eligibility, row.get("model_arm") or "", RR.family_group(row))
    if elig["status"] == EL.DISABLED and p is not None:
        p, cv, withheld = None, None, f"arm DISABLED: {elig['reason'][:160]}"
    out = {"state": row.get("support_state"), "p_yes": p, "provenance": register_provenance(row, table),
           "eligibility": elig["status"]}
    ab = row.get("abstention") or {}
    if ab.get("state"):
        out["abstention"] = ab["state"]
    if cv is not None and (p is None or abs(float(cv) - float(p)) > 1e-12):
        out["contract_value"] = cv
    if p is None and row.get("support_reason"):
        out["reason"] = row["support_reason"][:200]
    if withheld:
        out["probability_withheld_reason"] = withheld
    if row.get("p_yes_low") is not None or row.get("p_yes_high") is not None:
        out["p_yes_low"], out["p_yes_high"] = row.get("p_yes_low"), row.get("p_yes_high")
    if _arm_is_market_derived(row):
        out["market_derived"] = True
    if row.get("model_arm") in V5_ARMS:
        # research label for the point-in-time QB challenger, and the team's QB resolution where it moved off chart QB1
        out["research_arm"] = "V5 point-in-time QB challenger: supporting research, never authority"
        qr = ab.get("qb_resolution") or {k: (row.get("player_context") or {}).get(k)
                                         for k in ("qb_resolution_reason", "effective_projected_qb", "qb_resolution_certainty")}
        if qr.get("qb_resolution_reason") not in (None, "CHART_QB1_AVAILABLE"):
            out["qb_resolution"] = {"reason": qr.get("qb_resolution_reason"), "effective_projected_qb": qr.get("effective_projected_qb"),
                                    "certainty": qr.get("qb_resolution_certainty")}
    return out


def _arm_is_market_derived(row: dict) -> bool:
    return row.get("model_arm") in MARKET_DERIVED_ARMS


def market_view(arms: dict | None, table: dict | None = None, *, packet_mid: float | None = None,
                eligibility: dict | None = None) -> dict | None:
    """The per-market Shadow v2 block: the independent arm's answer, plus any other arm that answered.

    `support_state` is the PRIMARY arm's state and nothing else. Taking the best state across arms would
    let the market-derived arm supply a probability the independent football view refused, which is
    precisely the substitution this report must never make silently.

    WHAT IS OMITTED, AND WHAT OMISSION MEANS
    ----------------------------------------
    This block is carried by every listed contract of a sixteen-game slate, so anything constant is
    referenced rather than repeated: repeating it took `packet.json` from 43MB to 96MB, past the size at
    which the report branch can be published at all. Three keys are written only when they say something:

        `contract_value`                only when it differs from `p_yes`
        `support_reason`                only where there is no probability to explain
        `information_sync`              only when it is NOT `SYNCHRONIZED` -- i.e. only when the model read
                                        information the market it is quoted against had not yet seen
        `quoted_against_different_market`   only when the Shadow v2 snapshot's own mid for this contract
                                        differs from the packet's by at least a cent

    Absence of each is stated here and in the game-level block (`information_sync_default`), so a reader
    never has to guess whether a missing key means "normal" or "unknown".

    `table` collects the constant provenance; pass the same dict for a whole packet and publish it once.
    """
    if not arms:
        return None
    table = {} if table is None else table
    engines = {arm: (row.get("engine") or "NONE") for arm, row in arms.items()}
    engine = next((e for e in engines.values() if e and e != "NONE"), next(iter(engines.values()), None))
    primary = next((a for a in INDEPENDENT_ARMS_BY_ENGINE.get(engine, (BOARD_ARM,)) if a in arms),
                   INDEPENDENT_ARMS_BY_ENGINE.get(engine, (BOARD_ARM,))[0])
    if primary not in arms:
        # the engine's independent arm did not answer this contract: report the board arm if it did, and
        # otherwise say which arms are present rather than promoting a market-derived one into the slot.
        primary = BOARD_ARM if BOARD_ARM in arms else None
    prow = arms.get(primary) or {}
    pv = arm_view(prow, table, eligibility) if primary else {}
    out = {
        "primary_arm": primary,
        "support_state": pv.get("state"),
        "p_yes": pv.get("p_yes"),
        "engine": prow.get("engine"),
        "provenance": pv.get("provenance"),
        "semantic_confidence": prow.get("semantic_confidence"),
        "settlement_reachability": (prow.get("settlement_reachability") or {}).get("state"),
        "eligibility": pv.get("eligibility"),
    }
    if pv.get("abstention"):
        out["abstention"] = pv["abstention"]
    for k in ("contract_value", "reason", "probability_withheld_reason", "p_yes_low", "p_yes_high"):
        if k in pv:
            out["support_reason" if k == "reason" else k] = pv[k]
    sync = (prow.get("information_sync") or {}).get("synchronization_state")
    if sync and sync != "SYNCHRONIZED":
        out["information_sync"] = sync
    others = {arm: arm_view(row, table, eligibility) for arm, row in sorted(arms.items()) if arm != primary}
    if others:
        out["other_arms"] = others
    v2mid = prow.get("mid")
    if packet_mid is not None and v2mid is not None and abs(float(v2mid) - float(packet_mid)) >= 0.01:
        out["quoted_against_different_market"] = {
            "v2_mid": v2mid, "packet_mid": packet_mid, "v2_observed_at": prow.get("observed_at"),
            "note": ("the Shadow v2 projection was made against a different market observation than the "
                     "price printed beside it")}
    return out


def has_probability(block: dict | None) -> bool:
    """Does the PRIMARY (independent) arm carry a probability a reader may use as a research view?"""
    return bool(block and block.get("p_yes") is not None)


def any_arm_probability(block: dict | None) -> bool:
    return bool(block and any(v.get("p_yes") is not None for v in (block.get("arms") or {}).values()))


PRIMARY_ARM_BASIS = ("BOARD_V2 owns every non-player family; DATA_PLAYER_V3 is the player arm that is an "
                     "independent football view of the statistic (DATA_PLAYER_DIST, its defective predecessor, "
                     "is primary only on snapshots written before v3 and is DISABLED). MARKET_PLAYER_DIST is "
                     "reconstructed FROM the Kalshi ladder and the HYBRID arms blend the two: they are reported, "
                     "flagged `market_derived`, and never promoted into the primary slot. Being primary says "
                     "nothing about authority: every arm answer carries its production-eligibility status, and "
                     "on the current evidence the MARKET is the better player-prop distribution.")


def game_view(blocks: list, manifest: dict | None, *, listed: list | None = None) -> dict:
    """Per-game Shadow v2 summary, with the LISTED board as the denominator.

    `listed` is the game's listed market rows. A listed ticker the snapshot produced no row for at all is
    counted under `NOT_IN_SNAPSHOT` rather than vanishing: Shadow v2's universe is the daily discovery run,
    and a market Kalshi opened after that run has no v2 row however well the engine supports its family.
    """
    counts: dict = {}
    by_engine: dict = {}
    for b in blocks:
        st = (b or {}).get("support_state") or "NO_PRIMARY_ARM"
        counts[st] = counts.get(st, 0) + 1
        eng = (b or {}).get("engine") or "NONE"
        e = by_engine.setdefault(eng, {"projected": 0, "refused": 0})
        e["projected" if has_probability(b) else "refused"] += 1
    n_listed = len(listed) if listed is not None else len(blocks)
    not_in_snapshot = max(0, n_listed - len(blocks))
    return {
        "snapshot_id": (manifest or {}).get("snapshot_id"),
        "information_sync_default": ("SYNCHRONIZED -- a market row carries `information_sync` only when it "
                                     "is NOT synchronized, i.e. only when the model read information the "
                                     "market it is quoted against had not yet seen"),
        "primary_arm_basis": PRIMARY_ARM_BASIS,
        "arms_present": sorted((manifest or {}).get("arms") or {}),
        "arms_missing": (manifest or {}).get("arms_missing") or [],
        "listed_contracts": n_listed,
        "with_v2_row": len(blocks),
        "not_in_snapshot": not_in_snapshot,
        "not_in_snapshot_reason": ("Shadow v2 prices the universe of the latest daily discovery run; a contract "
                                   "Kalshi opened after that run has no v2 row at this snapshot"),
        "projected": sum(1 for b in blocks if has_probability(b)),
        "counts_by_support_state": dict(sorted(counts.items())),
        "by_engine": {k: by_engine[k] for k in sorted(by_engine)},
        "authority": ("RESEARCH ONLY. Shadow v2 is not validated for real money and no probability here "
                      "reaches recommendation, staking or preflight."),
    }
