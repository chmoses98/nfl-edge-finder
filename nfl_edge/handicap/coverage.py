"""RUN NFL coverage accounting: every listed contract lands in exactly one analysis state.

THE OPERATING CONTRACT
----------------------
**RUN NFL means every executable Kalshi contract for every requested unstarted NFL game is examined and
accounted for.** `UNSUPPORTED_MODEL` is a statement about one model, never a reason to hide a contract:
it means "this automated model produces no authoritative probability here", and nothing else.

Every listed contract therefore terminates in exactly one ANALYSIS STATE, and each state belongs to one of
the four operator buckets:

    A  MODEL_PRICED                the incumbent validated pricer produced a probability for this contract
    B  COHERENT_SIM_PROJECTED      no incumbent probability, but the coherent game simulation produced a
                                   football probability for this exact ticker (research)
    B  SHADOW_V2_PROJECTED         no incumbent probability, but Shadow v2's independent arm produced a
                                   research projection for this exact ticker
    C  MANUAL_HANDICAP             no automated probability anywhere, but the question is pinned and its
                                   subject is identified, and the packet carries the football and context
                                   data a human or an AI handicapper needs -- so handicap it by hand
    D  RESEARCH_REQUIRED           no defensible automated price and no engine: an explicit PASS with the
                                   reason on the row
    D  SEMANTICS_UNRESOLVED        the settlement rule is not pinned; pricing it would be guessing
    D  IDENTITY_UNRESOLVED         the subject (player / team / game) did not resolve
    D  NON_FOOTBALL                a news / vote / transaction question, not a football simulation question
    -  POST_KICKOFF                the game has started: outside the pregame window this report covers

`SILENTLY_OMITTED` exists only so it can be asserted to be zero. A contract reaching it is a defect in this
module, not a category of market.

PRECEDENCE is A > B > C > D and is evaluated in exactly that order, with POST_KICKOFF ahead of all of them
(a started contract is stale, whatever any model says about it). The precedence is what makes the states a
partition: a contract that the incumbent prices AND Shadow v2 projects is counted once, under A, and its
Shadow v2 number is still on the row.

WHAT THIS MODULE MAY NOT DO
---------------------------
It may not invent a probability, may not upgrade a research state to a priced one, and may not read a
Shadow v2 or simulation number into the incumbent's `model_probability`. It only decides which column of
the coverage matrix a contract is counted in, and names the reason.
"""
from __future__ import annotations

# Module path, never `from nfl_edge.handicap import shadow_v2_block`: `report_isolation.reachable_modules`
# resolves a package-from import to every module in the package, and the report path must not be able to
# reach the Airtable bridge even transitively.
import nfl_edge.handicap.shadow_v2_block as SV2

# ---- analysis states (terminal; exactly one per listed contract)
MODEL_PRICED = "MODEL_PRICED"
COHERENT_SIM_PROJECTED = "COHERENT_SIM_PROJECTED"
SHADOW_V2_PROJECTED = "SHADOW_V2_PROJECTED"
MANUAL_HANDICAP = "MANUAL_HANDICAP"
RESEARCH_REQUIRED = "RESEARCH_REQUIRED"
SEMANTICS_UNRESOLVED = "SEMANTICS_UNRESOLVED"
IDENTITY_UNRESOLVED = "IDENTITY_UNRESOLVED"
NON_FOOTBALL = "NON_FOOTBALL"
POST_KICKOFF = "POST_KICKOFF"
SILENTLY_OMITTED = "SILENTLY_OMITTED"

ANALYSIS_STATES = (MODEL_PRICED, COHERENT_SIM_PROJECTED, SHADOW_V2_PROJECTED, MANUAL_HANDICAP,
                   RESEARCH_REQUIRED, SEMANTICS_UNRESOLVED, IDENTITY_UNRESOLVED, NON_FOOTBALL,
                   POST_KICKOFF, SILENTLY_OMITTED)
BUCKET = {MODEL_PRICED: "A", COHERENT_SIM_PROJECTED: "B", SHADOW_V2_PROJECTED: "B", MANUAL_HANDICAP: "C",
          RESEARCH_REQUIRED: "D", SEMANTICS_UNRESOLVED: "D", IDENTITY_UNRESOLVED: "D", NON_FOOTBALL: "D",
          POST_KICKOFF: "-", SILENTLY_OMITTED: "!"}
BUCKET_LABEL = {"A": "validated/production model view available",
                "B": "coherent / Shadow research model view available",
                "C": "no automated pricing authority; handicap from the football and context data in this packet",
                "D": "cannot defensibly price -- explicit PASS / RESEARCH REQUIRED, with a reason",
                "-": "outside the pregame window (kickoff has passed)",
                "!": "INVARIANT VIOLATION -- a listed contract with no analysis state"}

# incumbent ledger support states, mapped to what they actually mean for coverage
_INCUMBENT_POST_KICKOFF = "POST_KICKOFF_EXCLUDED"
_INCUMBENT_IDENTITY = "UNSUPPORTED_IDENTITY"
_INCUMBENT_RULES = "UNSUPPORTED_RULES"
_INCUMBENT_SUPPORTED = "SUPPORTED"

# families whose question is a news / vote / transaction event rather than a football outcome. Read from
# the catalog so this list cannot drift away from the taxonomy.
_NON_FOOTBALL_SUPPORT = ("NON_FOOTBALL_MODEL", "NEWS_EVENT_MODEL_REQUIRED")


def _catalog(market: dict):
    from nfl_edge.semantics.catalog import catalog_entry
    return catalog_entry(market.get("family"), market.get("period"), market.get("stat"))


def _most_specific_refusal(m: dict, entry) -> str:
    """Why this contract carries no automated probability, in order of how specific the answer is.

    The Shadow v2 arm that actually looked at this ticker knows more than the family catalog does, and the
    catalog knows more than a one-word incumbent state. Reporting the vaguest reason available is how a
    contract ends up labelled "unsupported" with nothing a handicapper can act on.
    """
    sv2, sim = m.get("shadow_v2") or {}, m.get("simulation") or {}
    for cand in (sv2.get("support_reason"), sim.get("support_reason"), m.get("support_reason"),
                 (entry.reason if entry is not None else None)):
        if cand:
            return str(cand)
    return "no engine owns this question yet"


def classify_market(m: dict) -> dict:
    """One listed market row -> {analysis_state, bucket, reason}. Deterministic; every branch names a reason.

    `m` is a packet market row: it already carries the incumbent's `support_state` and `model_probability`,
    the coherent simulation block under `simulation`, and the Shadow v2 block under `shadow_v2`.

    THE CATALOG IS THE AUTHORITY ON SEMANTICS, NOT THE INCUMBENT'S LABEL. The incumbent ledger writes
    `UNSUPPORTED_RULES` for RACE_TO_N ("requires in-game scoring-order simulation; not validated"),
    TEAM_STAT ("team stat ladders not modelled") and HALF_FULL_RESULT ("needs a period-correlated
    simulator") -- every one of which is a MODEL gap wearing a rules label. Reading that label as
    "the settlement rule is not pinned" would file 763 contracts of the 2026 week 2 board under "cannot
    defensibly price" when their rules are pinned in `nfl_edge/semantics/catalog.py` and a handicapper can
    reason about them from this packet. So `SEMANTICS_UNRESOLVED` is decided from the catalog's own
    `semantic_confidence` and from Shadow v2's per-contract question layer, never from the incumbent's
    refusal; the incumbent's reason survives as the manual-review reason.
    """
    sv2 = m.get("shadow_v2")
    sim = m.get("simulation")
    entry = _catalog(m)
    incumbent = m.get("support_state")
    sv2_state = (sv2 or {}).get("support_state")

    def out(state, reason, manual=None):
        r = {"analysis_state": state, "bucket": BUCKET[state], "reason": reason}
        if manual:
            r["manual_review_reason"] = manual
        return r

    if incumbent == _INCUMBENT_POST_KICKOFF or sv2_state == "POST_KICKOFF":
        return out(POST_KICKOFF, "kickoff has passed; this contract is outside the pregame window")
    # ---- A: the incumbent's own validated pricer
    if incumbent == _INCUMBENT_SUPPORTED and m.get("model_probability") is not None:
        return out(MODEL_PRICED, "incumbent pricer produced a probability for this contract")
    # ---- B: a research projection for this exact ticker
    if sim and sim.get("p_football") is not None:
        return out(COHERENT_SIM_PROJECTED,
                   f"coherent game simulation: {sim.get('support_state')} (research; not validated)")
    if SV2.has_probability(sv2):
        return out(SHADOW_V2_PROJECTED,
                   f"Shadow v2 {sv2.get('engine')} engine (provenance {sv2.get('provenance')}): "
                   f"{sv2.get('support_state')} -- research, not validated")
    # ---- D states that are not a handicap opportunity at all
    if entry is not None and entry.model_support in _NON_FOOTBALL_SUPPORT:
        return out(NON_FOOTBALL, entry.reason or "news / vote / transaction event")
    if incumbent == _INCUMBENT_IDENTITY or sv2_state == "IDENTITY_UNRESOLVED":
        return out(IDENTITY_UNRESOLVED, "the contract's subject did not resolve to a known player/team/game")
    if entry is None:
        return out(SEMANTICS_UNRESOLVED,
                   f"family {m.get('family')}/{m.get('period')} has no catalog entry: semantics not inventoried")
    if entry.semantic_confidence in ("AMBIGUOUS", "UNKNOWN"):
        return out(SEMANTICS_UNRESOLVED, entry.reason or f"catalog semantics {entry.semantic_confidence}")
    if sv2_state == "SEMANTICS_AMBIGUOUS":
        return out(SEMANTICS_UNRESOLVED,
                   (sv2 or {}).get("support_reason") or "Shadow v2 could not pin this contract's question")
    # ---- C vs D: the question is pinned and the subject identified. Is there enough here to handicap?
    #
    # C is not "we gave up politely". It is the claim that this packet already carries what a handicapper
    # needs for this contract: the question's rule, both team profiles, the injury and role state, the
    # weather, the market's own ladder and its movement. That is true exactly when the family's semantics
    # are pinned, some engine could in principle own the question, and the contract joined a scheduled game.
    if entry.model_support in ("RESEARCH_REQUIRED", "JOINT_MODEL_REQUIRED", "SHADOW", "PRICED"):
        return out(MANUAL_HANDICAP,
                   f"no automated probability at this snapshot (incumbent {incumbent}); question pinned, "
                   f"subject identified -- handicap from the packet",
                   manual=_most_specific_refusal(m, entry))
    if entry.model_support == "DATA_UNAVAILABLE":
        return out(RESEARCH_REQUIRED, entry.reason or "no free point-in-time data for this statistic")
    return out(RESEARCH_REQUIRED, entry.reason or f"model support {entry.model_support}")


def classify_game(markets: list) -> list:
    """Attach `analysis` to every listed market row, in place, and return the rows."""
    for m in markets:
        m["analysis"] = classify_market(m)
    return markets


def matrix(markets: list) -> dict:
    """The coverage matrix, by (family, period), over the LISTED board.

    Column meanings, in the mission's own words:

        listed              contracts on the board for this family/period
        executable          a real two-sided book (not a 0.00/0.99 quoting artefact)
        incumbent_priced    bucket A
        coherent_sim        bucket B via the coherent game simulation
        shadow_v2           bucket B via Shadow v2
        manual_research     bucket C
        identity_blocked    IDENTITY_UNRESOLVED
        rules_blocked       SEMANTICS_UNRESOLVED
        non_football        NON_FOOTBALL
        research_required   RESEARCH_REQUIRED (bucket D, engine absent)
        post_kickoff        the game started
        silently_omitted    MUST BE ZERO
    """
    cols = ("listed", "executable", "incumbent_priced", "coherent_sim", "shadow_v2", "manual_research",
            "research_required", "rules_blocked", "identity_blocked", "non_football", "post_kickoff",
            "silently_omitted")
    by: dict = {}
    totals = {c: 0 for c in cols}
    state_of = {MODEL_PRICED: "incumbent_priced", COHERENT_SIM_PROJECTED: "coherent_sim",
                SHADOW_V2_PROJECTED: "shadow_v2", MANUAL_HANDICAP: "manual_research",
                RESEARCH_REQUIRED: "research_required", SEMANTICS_UNRESOLVED: "rules_blocked",
                IDENTITY_UNRESOLVED: "identity_blocked", NON_FOOTBALL: "non_football",
                POST_KICKOFF: "post_kickoff", SILENTLY_OMITTED: "silently_omitted"}
    for m in markets:
        key = f"{m.get('family')}|{m.get('period') or ''}"
        row = by.setdefault(key, {c: 0 for c in cols})
        a = (m.get("analysis") or {}).get("analysis_state") or SILENTLY_OMITTED
        for target in ("listed", state_of.get(a, "silently_omitted")):
            row[target] += 1
            totals[target] += 1
        if not m.get("no_real_market"):
            row["executable"] += 1
            totals["executable"] += 1
    return {"columns": cols, "by_family": {k: by[k] for k in sorted(by)}, "totals": totals,
            "buckets": bucket_counts(markets),
            "invariant": "silently_omitted must be 0: every listed contract carries exactly one analysis state"}


def bucket_counts(markets: list) -> dict:
    out = {b: 0 for b in ("A", "B", "C", "D", "-", "!")}
    for m in markets:
        a = (m.get("analysis") or {}).get("analysis_state") or SILENTLY_OMITTED
        out[BUCKET[a]] += 1
    return {b: {"n": n, "meaning": BUCKET_LABEL[b]} for b, n in out.items()}


def merge_matrix(a: dict, b: dict) -> dict:
    """Slate-level matrix from per-game matrices, summed by family/period."""
    cols = a.get("columns") or b.get("columns")
    by = {k: dict(v) for k, v in (a.get("by_family") or {}).items()}
    for k, v in (b.get("by_family") or {}).items():
        if k not in by:
            by[k] = dict(v)
        else:
            for c in cols:
                by[k][c] = by[k].get(c, 0) + v.get(c, 0)
    totals = {c: (a.get("totals") or {}).get(c, 0) + (b.get("totals") or {}).get(c, 0) for c in cols}
    buckets = {}
    for src in (a.get("buckets") or {}, b.get("buckets") or {}):
        for bk, rec in src.items():
            e = buckets.setdefault(bk, {"n": 0, "meaning": rec.get("meaning")})
            e["n"] += rec.get("n", 0)
    return {"columns": cols, "by_family": {k: by[k] for k in sorted(by)}, "totals": totals,
            "buckets": buckets, "invariant": a.get("invariant") or b.get("invariant")}
