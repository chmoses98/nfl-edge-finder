"""The ANALYSIS artifact: the complete slate, one row per executable contract, for a machine to consume.

WHY A SEPARATE SURFACE
----------------------
`packet.json` is the complete record and is ~50MB; `slate.md` is a triage view and is deliberately not a
complete scan; the per-game Markdown files are complete but are ~40k tokens each. None of them is a thing a
ChatGPT session can hold in one hand and answer "did we scan every market for this game?" from.

So: a manifest plus one shard per game.

    analysis/manifest.json          vintages, counts, the coverage matrix, and the shard index
    analysis/games/<game_id>.json   every listed contract of that game, one row each

THE INVARIANT
-------------
Every listed ticker of the packet appears in exactly one shard, exactly once, and the manifest records the
count and the SHA-256 of each shard. `manifest["invariants"]` carries the three checks a reader can re-run:

    rows_total == packet markets listed
    duplicate_tickers == 0
    silently_omitted == 0

A partial publication is detectable rather than silent: a shard whose sha or row count does not match its
manifest entry is a broken artifact, and `verify()` says so by ticker rather than by arithmetic.

WHAT A ROW CARRIES
------------------
Enough to evaluate the contract without another lookup: identity, the exact YES meaning, the executable
quotes on both sides, width, volume, open interest, the capture and confirmation instants, the incumbent's
support state and probability, the coherent simulation's football/market/reconciled probabilities and the
weight that produced the third, Shadow v2's engine, support state and research probability, evidence class,
settlement capability, the accounting state and -- where nothing automated answered -- the manual-review
reason.

WHAT A ROW DOES NOT CARRY
-------------------------
Repeated context objects. Model and engine versions, cutoffs and snapshot ids are the same for thousands of
rows, so they live once in the manifest's `models` block and each row points at them. `reference` on a row
is a key into that block, exactly as in `packet.json`.

AUTHORITY
---------
None. A Shadow v2 or simulation probability in this file is research and is labelled as such on the row;
nothing here is a recommendation, a stake or a preflight input.
"""
from __future__ import annotations

import hashlib
import json
import os

ANALYSIS_SCHEMA_VERSION = "analysis-1.0.0"

# Stated once per shard, never per row.
AUTHORITY_NOTES = {
    "incumbent": ("`incumbent.model_probability` is the only probability produced by a deployed pricer, and "
                  "even it authorises no bet: the model has been shown redundant to the closing market on "
                  "player props and behind it on game outcomes."),
    "coherent_simulation": (
        "RESEARCH. `any_td` is the ONLY statistic with a non-zero deployed reconciliation weight (0.25); "
        "every other family deploys at 0, so its reconciled probability sits at the MARKET mean with the "
        "football shape and is reported but never ranked. A non-zero weight means only that this limited "
        "market/football blend earned non-zero research weight under the preregistered procedure -- fitted "
        "on 2025 weeks 1-9 and confirmed on weeks 10-22. It does NOT make touchdown props validated bets: "
        "the football-only model did not beat the market overall on any family (any_td Brier 0.1583 vs the "
        "market's 0.1570 over 3,720 settled rungs), and where the two disagreed by more than 0.10 the "
        "market won on every family. A large disagreement is a warning, not an opportunity. See "
        "research/simulation_engine/RECONCILIATION.md."),
    "shadow_v2": ("RESEARCH ONLY. Shadow v2 is not validated for real money. "
                  "PROJECTABLE_NOT_YET_VALIDATED means exactly that, and no number here reaches "
                  "recommendation, staking or preflight."),
}

_QUOTE_KEYS = ("yes_bid", "yes_ask", "no_bid", "no_ask", "mid", "width", "volume", "open_interest",
               "minutes_since_price_change", "minutes_to_kickoff")


def _yes_meaning(m: dict) -> str:
    """The exact YES rule, in one line, from the contract's own grammar."""
    who = m.get("player_name") or m.get("team") or ""
    stat = m.get("stat") or ""
    op, k = m.get("operator"), m.get("threshold")
    per = m.get("period") or "FULL"
    if k is not None and op:
        return f"YES iff {who + ' ' if who else ''}{stat} ({per}) {op} {k}".strip()
    if k is not None:
        return f"YES iff {who + ' ' if who else ''}{stat} ({per}) >= {k}".strip()
    return f"YES iff {m.get('family')} ({per}) resolves for {who or 'this strike'}".strip()


def _sim(m: dict) -> dict | None:
    s = m.get("simulation")
    if not s:
        return None
    return {"support_state": s.get("support_state"), "support_reason": s.get("support_reason"),
            "p_football": s.get("p_football"), "p_market": s.get("p_market"),
            "p_reconciled": s.get("p_reconciled"), "reconcile_weight": s.get("reconcile_weight"),
            "ranked": s.get("ranked"),
            "reconciled_disagreement_vs_mid": s.get("reconciled_disagreement_vs_mid"),
            "football_disagreement_vs_mid": s.get("football_disagreement_vs_mid")}


def _v2(m: dict) -> dict | None:
    b = m.get("shadow_v2")
    if not b:
        return None
    out = {"primary_arm": b.get("primary_arm"), "engine": b.get("engine"),
           "support_state": b.get("support_state"), "support_reason": b.get("support_reason"),
           "p_yes": b.get("p_yes"), "contract_value": b.get("contract_value"),
           "provenance": b.get("provenance"), "semantic_confidence": b.get("semantic_confidence"),
           "settlement_reachability": b.get("settlement_reachability")}
    for k in ("information_sync", "quoted_against_different_market", "other_arms"):
        if b.get(k) is not None:
            out[k] = b[k]
    return out


def market_rows(game: dict, packet: dict) -> list:
    """Every listed contract of one game, one row each, ordered by ticker.

    Identity that is the same for every row of the game -- season, week, both teams, kickoff, the ledger
    run and market snapshot the quotes came from, the model versions, the authority notes -- is on the
    SHARD, not repeated eleven thousand times. That is the mission's own rule: no giant repeated context
    object on a row a reference can carry.
    """
    rows = []
    for m in game.get("markets") or []:
        a = m.get("analysis") or {}
        row = {
            "ticker": m.get("ticker"),
            "family": m.get("family"), "period": m.get("period"), "stat": m.get("stat"),
            "subject_kind": ("player" if m.get("player_name") or m.get("player_id")
                             else ("team" if m.get("team") else "game")),
            "subject": m.get("player_name") or m.get("team"),
            "player_id": m.get("player_id"),
            "threshold": m.get("threshold"), "operator": m.get("operator"),
            "yes_meaning": _yes_meaning(m),
            **{k: m.get(k) for k in _QUOTE_KEYS},
            "executable": not m.get("no_real_market"),
            "no_real_market": bool(m.get("no_real_market")),
            "flags": m.get("flags") or [],
            "incumbent": {"support_state": m.get("support_state"), "support_reason": m.get("support_reason"),
                          "model_probability": m.get("model_probability"),
                          "model_uncertainty": m.get("model_uncertainty"),
                          "disagreement_vs_mid": m.get("disagreement_vs_mid")},
            "coherent_simulation": _sim(m),
            "shadow_v2": _v2(m),
            "analysis_state": a.get("analysis_state"),
            "bucket": a.get("bucket"),
            "reason": a.get("reason"),
            "manual_review_reason": a.get("manual_review_reason"),
        }
        rows.append(row)
    rows.sort(key=lambda r: (r["ticker"] or ""))
    return rows


def _sha(payload: str) -> str:
    return hashlib.sha256(payload.encode()).hexdigest()


def build(packet: dict) -> tuple[dict, dict]:
    """(manifest, {game_id: shard}). Nothing is written; the caller owns the filesystem."""
    shards, index = {}, []
    all_tickers, duplicates = set(), []
    for g in packet.get("games") or []:
        rows = market_rows(g, packet)
        for r in rows:
            if r["ticker"] in all_tickers:
                duplicates.append(r["ticker"])
            all_tickers.add(r["ticker"])
        cov = g.get("coverage") or {}
        src = packet.get("sources") or {}
        shard = {"schema_version": ANALYSIS_SCHEMA_VERSION, "game_id": g.get("game_id"),
                 "season": g.get("season"), "week": g.get("week"),
                 "home_team": g.get("home_team"), "away_team": g.get("away_team"),
                 "kickoff_utc": g.get("kickoff_utc"), "game_state": g.get("game_state"),
                 "minutes_to_kickoff": g.get("minutes_to_kickoff"),
                 # every row's quotes and model states came from exactly these, so they are stated once
                 "capture": {"ledger": src.get("ledger"), "ledger_run_id": src.get("ledger_run_id"),
                             "market_snapshot_run_id": src.get("snapshot_run_id"),
                             "packet_built_at": packet.get("built_at"),
                             "incumbent_model_version": src.get("model_version"),
                             "coherent_simulation_run": (src.get("simulation") or {}).get("run_id"),
                             "shadow_v2_snapshot": (src.get("shadow_v2") or {}).get("snapshot_id")},
                 "authority_notes": AUTHORITY_NOTES,
                 "coverage": cov, "shadow_v2": g.get("shadow_v2"),
                 "rows": rows}
        payload = json.dumps(shard, sort_keys=True, default=str)
        shards[g["game_id"]] = shard
        index.append({"game_id": g["game_id"], "path": f"games/{g['game_id']}.json",
                      "rows": len(rows), "sha256": _sha(payload),
                      "silently_omitted": (cov.get("totals") or {}).get("silently_omitted", 0),
                      "buckets": {b: rec.get("n", 0) for b, rec in (cov.get("buckets") or {}).items()}})
    s = packet.get("slate_summary") or {}
    listed = s.get("markets_listed_slate")
    rows_total = sum(i["rows"] for i in index)
    matrix = s.get("coverage_matrix") or {}
    manifest = {
        "schema_version": ANALYSIS_SCHEMA_VERSION,
        "packet_schema_version": packet.get("schema_version"),
        "packet_sha": packet.get("packet_sha"),
        "handicap_run_id": packet.get("handicap_run_id"),
        "built_at": packet.get("built_at"),
        "season": packet.get("season"), "week": packet.get("week"),
        "real_money_status": packet.get("real_money_status"),
        "coverage_contract": s.get("coverage_contract"),
        "models": {
            "incumbent": {"model_version": (packet.get("sources") or {}).get("model_version"),
                          "ledger": (packet.get("sources") or {}).get("ledger"),
                          "ledger_run_id": (packet.get("sources") or {}).get("ledger_run_id"),
                          "market_snapshot_run_id": (packet.get("sources") or {}).get("snapshot_run_id")},
            "coherent_simulation": (packet.get("sources") or {}).get("simulation"),
            "shadow_v2": (packet.get("sources") or {}).get("shadow_v2"),
        },
        "counts": {"games": len(index), "rows_total": rows_total, "packet_markets_listed": listed,
                   "duplicate_tickers": len(duplicates), "unique_tickers": len(all_tickers)},
        "coverage_matrix": matrix,
        "games": sorted(index, key=lambda i: i["game_id"]),
        "invariants": {
            "rows_total_equals_packet_markets_listed": rows_total == listed,
            "no_duplicate_tickers": not duplicates,
            "zero_silently_omitted": (matrix.get("totals") or {}).get("silently_omitted", 0) == 0,
            "duplicate_ticker_examples": sorted(set(duplicates))[:20],
            "note": ("Every listed contract of the packet appears in exactly one shard, exactly once. "
                     "A shard whose sha256 or row count disagrees with its manifest entry is a partial "
                     "publication, which `verify()` detects by identity rather than by arithmetic."),
        },
        "how_to_read": [
            "1. Read manifest.json: `coverage_matrix` says what was scanned and `invariants` says whether "
            "the scan is complete. `zero_silently_omitted` must be true.",
            "2. Open analysis/games/<game_id>.json for each game you handicap. Every executable contract of "
            "that game is one row.",
            "3. On each row, `bucket` is A (validated model), B (coherent/Shadow research), C (handicap by "
            "hand from this packet) or D (explicit PASS, reason on the row).",
            "4. `incumbent.model_probability` is the only probability with production authority, and even "
            "that authorises no bet. `shadow_v2.p_yes` and `coherent_simulation.p_football` are research.",
        ],
    }
    return manifest, shards


def write(out_dir: str, packet: dict) -> dict:
    """Write `analysis/manifest.json` and `analysis/games/<game_id>.json` under `out_dir`. Returns the manifest.

    Shards are written FIRST and the manifest last, so a run that dies half-way leaves a directory with no
    manifest -- which every reader treats as "no analysis artifact" -- rather than a manifest promising
    shards that are not there.
    """
    manifest, shards = build(packet)
    adir = os.path.join(out_dir, "analysis")
    gdir = os.path.join(adir, "games")
    os.makedirs(gdir, exist_ok=True)
    for gid, shard in shards.items():
        with open(os.path.join(gdir, f"{gid}.json"), "w") as f:
            json.dump(shard, f, sort_keys=True, default=str)
    with open(os.path.join(adir, "manifest.json"), "w") as f:
        json.dump(manifest, f, indent=1, default=str)
    return manifest


def verify(out_dir: str) -> dict:
    """Re-read the artifact from disk and check it by identity. Returns {ok, problems: [...]}.

    This is the partial-publication test: a missing shard, a shard whose bytes do not hash to what the
    manifest recorded, a row count that disagrees, a duplicate ticker across shards, or an invariant the
    manifest itself already reports as false.
    """
    adir = os.path.join(out_dir, "analysis")
    mpath = os.path.join(adir, "manifest.json")
    problems = []
    if not os.path.exists(mpath):
        return {"ok": False, "problems": ["analysis/manifest.json is absent"]}
    manifest = json.load(open(mpath))
    seen: dict = {}
    for entry in manifest.get("games") or []:
        path = os.path.join(adir, entry["path"])
        if not os.path.exists(path):
            problems.append(f"{entry['game_id']}: shard {entry['path']} is absent")
            continue
        shard = json.load(open(path))
        sha = _sha(json.dumps(shard, sort_keys=True, default=str))
        if sha != entry["sha256"]:
            problems.append(f"{entry['game_id']}: shard sha256 {sha[:12]} != manifest {entry['sha256'][:12]}")
        rows = shard.get("rows") or []
        if len(rows) != entry["rows"]:
            problems.append(f"{entry['game_id']}: {len(rows)} rows on disk, manifest says {entry['rows']}")
        for r in rows:
            t = r.get("ticker")
            if not t:
                problems.append(f"{entry['game_id']}: a row carries no ticker and cannot be accounted for")
            elif t in seen:
                problems.append(f"duplicate ticker {t} in {seen[t]} and {entry['game_id']}")
            else:
                seen[t] = entry["game_id"]
            if not r.get("analysis_state"):
                problems.append(f"{t}: no analysis state (silently omitted)")
    inv = manifest.get("invariants") or {}
    for k in ("rows_total_equals_packet_markets_listed", "no_duplicate_tickers", "zero_silently_omitted"):
        if not inv.get(k):
            problems.append(f"manifest invariant {k} is false")
    total = (manifest.get("counts") or {}).get("rows_total")
    if total is not None and len(seen) != total:
        problems.append(f"{len(seen)} distinct tickers across shards, manifest counts {total} rows")
    return {"ok": not problems, "problems": problems, "tickers": len(seen),
            "games": len(manifest.get("games") or [])}
