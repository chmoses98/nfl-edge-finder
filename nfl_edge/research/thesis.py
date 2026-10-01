"""STRUCTURED THESIS METADATA: optional, derived where possible, never a new chore. RESEARCH ONLY.

The feedback loop the owner wants is

    pregame evidence -> thesis -> market expression -> wager -> realized script -> player/team autopsy
      -> expression autopsy -> next week's research

and the weak link is the second arrow: an imported wager (the owner's real bet) carries no thesis at all
(`position_lifecycle` episodes say UNKNOWN_THESIS). This module does NOT add a manual step. It defines the
optional fields once, fills them automatically from what already exists, and accepts more only if the owner
chooses to supply them:

    primary_thesis_id        a stable id for "the one belief" several positions express
    correlation_bucket       the bucket positions share (from the record, else inferred by the expression autopsy)
    script_dependency        what the game must look like for the thesis to pay (e.g. SHOOTOUT, FAVORITE_CONTROL)
    market_expression_reason why THIS market expresses it (e.g. team total over spread: offence, not margin)
    failure_mode             what would make it wrong (e.g. QB_EXIT, BLOWOUT_TRAIL)
    hard_bet_up_to           the price ceiling the handicap set
    role_uncertainty_note    free text about role / usage risk

Sources, in order:

  1. a RECOMMENDATION record (handicap schema): `primary_thesis`, `correlation_group`, `bet_up_to_probability`
     map directly; `reasoning_tags` of the form `script:<X>`, `expression:<X>`, `failure:<X>`, `role:<text>` map to
     the structured fields. Nothing in the schema changes, and a record without such tags simply has fewer fields.
  2. an OPTIONAL owner file `data/handicap/theses/<season>/week_<NN>.json` (on handicap-data): {ticker or episode
     id: {field: value}}. Absent is normal; unknown keys are ignored and reported; nothing ever fails ingestion
     because a field is missing.
  3. otherwise the expression autopsy INFERS the bucket and labels it INFERRED.
"""
from __future__ import annotations

import hashlib
import json
import os

THESIS_VERSION = "thesis-metadata-1.0.0"
THESIS_FIELDS = ("primary_thesis_id", "correlation_bucket", "script_dependency", "market_expression_reason",
                 "failure_mode", "hard_bet_up_to", "role_uncertainty_note")
TAG_PREFIX = {"script": "script_dependency", "expression": "market_expression_reason", "failure": "failure_mode",
              "role": "role_uncertainty_note"}
OWNER_FILE = os.path.join("data", "handicap", "theses")


def thesis_id(text: str, game_id: str | None) -> str:
    norm = " ".join(str(text or "").lower().split())
    return "th-" + hashlib.sha256(f"{game_id}|{norm}".encode()).hexdigest()[:12]


def from_recommendation(rec: dict) -> dict:
    """Structured thesis fields from an existing recommendation record. Missing fields stay missing."""
    out = {}
    if rec.get("primary_thesis"):
        out["primary_thesis_id"] = thesis_id(rec["primary_thesis"], rec.get("game_id"))
    if rec.get("correlation_group"):
        out["correlation_bucket"] = rec["correlation_group"]
    if rec.get("bet_up_to_probability") is not None:
        out["hard_bet_up_to"] = rec["bet_up_to_probability"]
    for tag in rec.get("reasoning_tags") or []:
        if not isinstance(tag, str) or ":" not in tag:
            continue
        k, v = tag.split(":", 1)
        field = TAG_PREFIX.get(k.strip().lower())
        if field and v.strip():
            out[field] = v.strip()
    return out


def validate(meta: dict) -> list:
    """Warnings only (a thesis record never blocks ingestion): unknown keys, wrong types."""
    warn = []
    for k, v in (meta or {}).items():
        if k not in THESIS_FIELDS:
            warn.append(f"unknown thesis field {k!r} ignored")
        elif k == "hard_bet_up_to":
            try:
                x = float(v)
                if not 0.0 < x < 1.0:
                    warn.append("hard_bet_up_to outside (0, 1)")
            except (TypeError, ValueError):
                warn.append("hard_bet_up_to is not a number")
        elif v is not None and not isinstance(v, str):
            warn.append(f"{k} should be text")
    return warn


def clean(meta: dict) -> dict:
    return {k: v for k, v in (meta or {}).items() if k in THESIS_FIELDS and v not in (None, "")}


def load_owner_file(root: str, season: int, week: int) -> tuple[dict, list]:
    """{ticker or episode id: thesis fields} from the optional owner file; ({}, []) when absent."""
    path = os.path.join(root, OWNER_FILE, str(season), f"week_{int(week):02d}.json")
    if not os.path.exists(path):
        return {}, []
    try:
        doc = json.load(open(path))
    except (OSError, ValueError) as e:
        return {}, [f"owner thesis file unreadable ({e}); ignored"]
    out, warns = {}, []
    for key, meta in (doc or {}).items():
        if isinstance(meta, dict):
            warns += [f"{key}: {w}" for w in validate(meta)]
            out[key] = clean(meta)
    return out, warns


def collect(*, recommendations=(), owner: dict | None = None, ticker_of_rec=lambda r: r.get("ticker")) -> dict:
    """Merge the sources: owner file entries win over recommendation-derived fields, field by field."""
    out = {}
    for rec in recommendations or ():
        t = ticker_of_rec(rec)
        if t:
            out.setdefault(t, {}).update(from_recommendation(rec))
    for k, meta in (owner or {}).items():
        out.setdefault(k, {}).update(meta)
    return out
