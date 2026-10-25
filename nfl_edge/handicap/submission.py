"""The analyst's submission: per-game REVIEW records and THESES, checked against the dossiers they claim to rest on.

The card never decides which football theses deserve betting consideration. The analyst does, in a submission:

    { "submission_version": "1", "analyst": "...", "packet_sha": "<the packet read>", "created_at": "...",
      "reviews": [ one per game, REQUIRED for every unstarted game ],
      "theses":  [ zero or more, each belonging to a reviewed game ] }

Every unstarted game ends in exactly one DISPOSITION:

  REVIEWED_PRICED_BET        deeply reviewed, a defensible thesis, priced, and approved by the real preflight
  REVIEWED_PRICED_CANDIDATE  deeply reviewed, thesis priced, NOT approved to bet (preflight not run or stake authority missing); shown as a candidate
  REVIEWED_PRICED_PREFLIGHT_BLOCKED  deeply reviewed and priced, but the real preflight withdrew the line (price moved, stale availability, depth, schema); not a rejection of the thesis, not a bet
  REVIEWED_REJECTED          deeply reviewed; the thesis was rejected (by the analyst, the challenge, the 2c edge floor or the risk policy)
  INSUFFICIENT_DATA          the analyst could not complete the research for a named reason (missing/conflicting data, unresolved starters)
  NOT_REVIEWED               no qualifying review record. Merely scanning the markets is this.

WHAT COUNTS AS A DEEP REVIEW (`deep_review_check`). A review record must cite evidence IDS that exist in that game's dossier, from each football category
(team matchup, quarterback/line, availability, environment, scripts), cite player evidence (or say in words why no player market is viable), cite the
contract families it examined, and carry the analyst's own reasoning. A record that cites nothing from a category does not qualify -- and a thesis filed
without a qualifying review is not priced. The check verifies that the citations resolve; it cannot verify that the analyst read them, and it does not
pretend to. What it removes is the cheapest way to look thorough: listing markets.
"""
from __future__ import annotations

SUBMISSION_VERSION = "1"

VERDICTS = ("THESIS", "REJECTED", "INSUFFICIENT_DATA")
MIN_REASONING = 120
MIN_REASON_TEXT = 40
MIN_MISSING_ITEM = 20

D_BET = "REVIEWED_PRICED_BET"
D_CANDIDATE = "REVIEWED_PRICED_CANDIDATE"
D_REJECTED = "REVIEWED_REJECTED"
D_INSUFFICIENT = "INSUFFICIENT_DATA"
D_NOT_REVIEWED = "NOT_REVIEWED"
D_PREFLIGHT_BLOCKED = "REVIEWED_PRICED_PREFLIGHT_BLOCKED"
D_POST = "POST_KICKOFF_EXCLUDED"
D_BLOCKED = "BLOCKED"
DISPOSITIONS = (D_BET, D_CANDIDATE, D_PREFLIGHT_BLOCKED, D_REJECTED, D_INSUFFICIENT, D_NOT_REVIEWED, D_POST, D_BLOCKED)


def _cited(coverage: dict, cat: str) -> list:
    v = (coverage or {}).get(cat) or []
    return [v] if isinstance(v, str) else list(v)


def deep_review_check(review: dict, dossier: dict) -> dict:
    """{qualifies, problems, cited} for one review against its game's dossier. Pure and deterministic."""
    from nfl_edge.handicap import dossier as DS
    ix = dossier.get("evidence_index") or {}
    problems, cited_all = [], []
    cov = review.get("coverage") or {}
    all_ids = []
    for v in cov.values():
        all_ids += v if isinstance(v, list) else [v]
    unknown = sorted({i for i in all_ids if i not in ix})
    if unknown:
        problems.append(f"cites evidence ids that are not in this game's dossier: {unknown[:6]}")
    for cat, need in DS.REQUIRED_CATEGORIES:
        ids = [i for i in _cited(cov, cat) if i in ix and ix[i]["category"] == cat]
        cited_all += ids
        if len(set(ids)) < need:
            problems.append(f"category {cat}: needs >= {need} valid dossier id(s) of that category, has {len(set(ids))}")
    pe = [i for c in DS.PLAYER_EVIDENCE_CATEGORIES for i in _cited(cov, c) if i in ix and ix[i]["category"] == c]
    cited_all += pe
    reason = str(review.get("player_markets_reason") or "").strip()
    if len(set(pe)) < DS.PLAYER_MIN_CITATIONS and len(reason) < MIN_REASON_TEXT:
        problems.append(f"player evidence: needs >= {DS.PLAYER_MIN_CITATIONS} ids from {DS.PLAYER_EVIDENCE_CATEGORIES} or a player_markets_reason of >= {MIN_REASON_TEXT} characters")
    fam = [i for i in _cited(cov, "markets") if i in ix and ix[i]["category"] == "markets"]
    cited_all += fam
    game_fam = [i for i in fam if i.startswith("FAM:") and not i.startswith("FAM:PLAYER_STAT")]
    player_fam = [i for i in fam if i.startswith("FAM:PLAYER_STAT") or i.startswith("PM:")]
    if not game_fam:
        problems.append("markets: cite at least one game-line family (FAM:SPREAD|FULL, FAM:TOTAL|FULL, ...) that was examined")
    if not player_fam and len(reason) < MIN_REASON_TEXT:
        problems.append("markets: cite the player-stat families examined (FAM:PLAYER_STAT|FULL or PM:* ladders) or give a player_markets_reason")
    if len(str(review.get("reasoning") or "").strip()) < MIN_REASONING:
        problems.append(f"reasoning: the analyst's own reasoning must be >= {MIN_REASONING} characters")
    return {"qualifies": not problems, "problems": problems, "cited": sorted(set(cited_all))}


def insufficient_check(review: dict, dossier: dict) -> dict:
    ix = dossier.get("evidence_index") or {}
    problems = []
    missing = [m for m in (review.get("missing") or []) if len(str(m).strip()) >= MIN_MISSING_ITEM]
    if not missing:
        problems.append(f"INSUFFICIENT_DATA needs at least one named missing/conflicting item of >= {MIN_MISSING_ITEM} characters")
    ids = [i for v in (review.get("coverage") or {}).values() for i in (v if isinstance(v, list) else [v]) if i in ix]
    if not ids:
        problems.append("INSUFFICIENT_DATA must cite at least one dossier evidence id showing what blocked the review")
    if len(str(review.get("reasoning") or "").strip()) < MIN_REASONING:
        problems.append(f"reasoning: >= {MIN_REASONING} characters")
    return {"qualifies": not problems, "problems": problems, "missing": missing}


def resolve_thesis_evidence(thesis: dict, dossier: dict) -> tuple:
    """(measured_items, simulation_items, problems). Evidence IDS are resolved against the dossier: the dossier's own text and its opponent-adjusted flag are
    used, never the analyst's claim about them. Free-text `evidence.measured` items without an id are kept but marked `uncited`."""
    ix = dossier.get("evidence_index") or {}
    measured, simulation, problems = [], [], []
    unmoved = set(thesis.get("market_unmoved_ids") or [])
    for i in thesis.get("evidence_ids") or []:
        e = ix.get(i)
        if e is None:
            problems.append(f"evidence id {i!r} is not in the dossier for {dossier.get('game_id')}")
            continue
        item = {"id": i, "claim": e["text"], "opponent_adjusted": e["opponent_adjusted"], "market_unmoved": i in unmoved, "category": e["category"], "kind": e["kind"]}
        (simulation if e["kind"] == "SIMULATION" else measured).append(item)
    for m in (thesis.get("evidence") or {}).get("measured", []) or []:
        measured.append(dict(m, uncited=True, opponent_adjusted=None))   # an uncited claim cannot assert that it is opponent-adjusted
    return measured, simulation, problems


def validate_structure(sub: dict) -> list:
    errs = []
    if not isinstance(sub, dict):
        return ["submission must be a JSON object"]
    if str(sub.get("submission_version")) != SUBMISSION_VERSION:
        errs.append(f"submission_version must be {SUBMISSION_VERSION!r}")
    for k in ("reviews", "theses"):
        if not isinstance(sub.get(k), list):
            errs.append(f"{k} must be a list")
    seen = set()
    for r in sub.get("reviews") or []:
        if r.get("verdict") not in VERDICTS:
            errs.append(f"review {r.get('game_id')}: verdict must be one of {VERDICTS}")
        if r.get("game_id") in seen:
            errs.append(f"duplicate review for {r.get('game_id')}")
        seen.add(r.get("game_id"))
    return errs


def from_legacy_theses(theses: list) -> dict:
    """A bare list of theses (the pre-submission format) as a submission with NO review records -- accepted only where the caller allows unreviewed theses."""
    return {"submission_version": SUBMISSION_VERSION, "analyst": "legacy", "reviews": None, "theses": theses}
