"""Player registry (from Sackmann players files) and tennis-data -> Sackmann match linking.

Why linking is conservative: a wrong link silently pairs the wrong closing
odds with a match and corrupts every downstream calibration number.  So a
tennis-data row is only ``MATCHED`` when exactly one Sackmann candidate scores
above ``match_threshold`` *and* the runner-up is below ``runner_up_threshold``;
everything else is ``AMBIGUOUS`` (human/alias-table review) or ``UNMATCHED``.

Candidate scoring (weights sum to 1.0)::

    players    0.50  mean of winner/loser ``player_match_score`` (both must be > 0)
    tournament 0.20  name-token Jaccard | location in tourney_name | alias table
    date       0.15  tennis-data match date vs Sackmann tournament start
    round      0.10  round agreement using Sackmann draw_size to place "Nth Round"
    surface    0.05  surface agreement

Hard filters before scoring: same tour; tennis-data date inside the window
around the Sackmann start date; both player names compatible; and at least
one of tournament/round agreeing (otherwise the candidate is the same pair at
a different event and is discarded rather than counted as a runner-up).

Schema assumptions marked ``ASSUMPTION`` need checking against real data.
"""
from __future__ import annotations

import logging
import math
from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any, Iterable, Optional

import numpy as np
import pandas as pd

from tennis_edge.data.sources import read_csv_gz
from tennis_edge.identity.names import last_first_initial, name_tokens, normalize_name, player_match_score, surname_initials

log = logging.getLogger(__name__)

MATCHED = "MATCHED"
AMBIGUOUS = "AMBIGUOUS"
UNMATCHED = "UNMATCHED"

REGISTRY_COLUMNS = ["player_id", "name_first", "name_last", "name_full", "name_norm", "last_norm",
                    "last_first_initial", "hand", "dob", "ioc", "height", "wikidata_id"]
ALIAS_COLUMNS = ["player_id", "alias", "alias_type"]

LINK_COLUMNS = ["td_key", "status", "match_key", "confidence", "second_match_key", "second_confidence", "n_candidates",
                "score_players", "score_tournament", "score_date", "score_round", "score_surface",
                "winner_id", "loser_id", "winner_name", "loser_name"]

WEIGHTS = {"players": 0.50, "tournament": 0.20, "date": 0.15, "round": 0.10, "surface": 0.05}

# Tokens that carry no identity in tournament names (sponsors are handled by Jaccard being partial).
TOURNAMENT_STOPWORDS = frozenset({
    "open", "atp", "wta", "masters", "championships", "championship", "cup", "international", "internationals",
    "tennis", "classic", "the", "of", "de", "by", "presented", "and", "1000", "500", "250", "series", "tour",
    "world", "grand", "prix", "trophy", "invitational", "men", "mens", "women", "womens", "s", "premier", "tier",
})
# ASSUMPTION: alias table seeded from well-known naming differences; extend
# from the AMBIGUOUS/UNMATCHED report on real data.
TOURNAMENT_ALIASES: dict[str, tuple[str, ...]] = {
    "french open": ("roland garros",),
    "masters cup": ("tour finals", "masters"),
    "atp finals": ("tour finals",),
    "wta finals": ("tour finals", "wta championships"),
    "tour finals": ("masters cup", "atp finals", "wta finals"),
    "bnp paribas open": ("indian wells",),
    "sony ericsson open": ("miami",),
    "miami open": ("miami",),
    "us open": ("us open",),
    "australian open": ("australian open",),
    "wimbledon": ("wimbledon",),
    "olympics": ("olympics", "olympic games"),
}

_SACKMANN_ROUND_STAGE = {"F": 0, "SF": 1, "QF": 2, "R16": 3, "R32": 4, "R64": 5, "R128": 6, "RR": -1, "BR": 1}
_TOURNAMENT_DAYS = {"GRAND_SLAM": 14, "MASTERS_1000": 12, "OLYMPICS": 9}
_DEFAULT_TOURNAMENT_DAYS = 8


# --- registry -----------------------------------------------------------------
def _parse_dob(value: Any) -> Optional[date]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return None
    try:
        s = str(int(float(value)))
        if len(s) != 8:
            return None
        return date(int(s[:4]), int(s[4:6]), int(s[6:8]))
    except (ValueError, TypeError, OverflowError):
        return None


def _str_or_none(v: Any) -> Optional[str]:
    if v is None or (isinstance(v, float) and np.isnan(v)):
        return None
    s = str(v).strip()
    return s or None


def build_registry(players: pd.DataFrame, tour: str) -> pd.DataFrame:
    """Canonical registry from a raw ``atp_players.csv`` / ``wta_players.csv`` frame.

    Rows without a player_id are unusable and dropped with a warning (there
    is no key to quarantine them under).  ``wikidata_id`` is optional because
    older snapshots lack the column.
    """
    if "player_id" not in players.columns:
        raise ValueError("players file lacks 'player_id'")
    df = players.reset_index(drop=True)
    ids = pd.to_numeric(df["player_id"], errors="coerce")
    bad = ids.isna()
    if bad.any():
        log.warning("%s players: %d rows without numeric player_id dropped", tour, int(bad.sum()))
    df = df.loc[~bad].reset_index(drop=True)

    def col(name: str) -> pd.Series:
        return df[name] if name in df.columns else pd.Series([None] * len(df), index=df.index, dtype="object")

    out = pd.DataFrame(index=df.index)
    out["player_id"] = pd.to_numeric(df["player_id"], errors="coerce").astype("Int64")
    out["tour"] = tour.upper()
    out["name_first"] = col("name_first").map(_str_or_none)
    out["name_last"] = col("name_last").map(_str_or_none)
    out["name_full"] = [" ".join(t for t in (f, l) if t) or None for f, l in zip(out["name_first"], out["name_last"])]
    out["name_norm"] = out["name_full"].map(normalize_name)
    out["last_norm"] = out["name_last"].map(normalize_name)
    out["last_first_initial"] = [last_first_initial(f, l) for f, l in zip(out["name_first"], out["name_last"])]
    out["hand"] = col("hand").map(_str_or_none)
    out["dob"] = col("dob").map(_parse_dob).astype("object")
    out["ioc"] = col("ioc").map(_str_or_none)
    out["height"] = pd.to_numeric(col("height"), errors="coerce").astype("Float64")
    out["wikidata_id"] = col("wikidata_id").map(_str_or_none)
    return out[["tour", *REGISTRY_COLUMNS]]


def load_registry(players_path: Path | str, tour: str) -> pd.DataFrame:
    return build_registry(read_csv_gz(players_path), tour)


def build_alias_table(registry: pd.DataFrame, matches: Optional[pd.DataFrame] = None) -> pd.DataFrame:
    """Alias rows (player_id, alias, alias_type) for name lookups.

    Types: ``full`` (normalised registry name), ``last_initial``
    (tennis-data style "federer r"), ``match_name`` (a *different* spelling
    seen in winner_name/loser_name of the match files, which happens when the
    players file and the match file were edited at different times).
    """
    rows: list[tuple[int, str, str]] = []
    for pid, full, lfi in zip(registry["player_id"], registry["name_norm"], registry["last_first_initial"]):
        if pd.isna(pid):
            continue
        if full:
            rows.append((int(pid), full, "full"))
        if lfi:
            rows.append((int(pid), lfi, "last_initial"))
    if matches is not None and len(matches):
        known = {(pid, alias) for pid, alias, _ in rows}
        for side in ("winner", "loser"):
            pairs = matches[[f"{side}_id", f"{side}_name"]].dropna().drop_duplicates()
            for pid, name in zip(pairs[f"{side}_id"], pairs[f"{side}_name"]):
                alias = normalize_name(name)
                if alias and (int(pid), alias) not in known:
                    rows.append((int(pid), alias, "match_name"))
                    known.add((int(pid), alias))
    table = pd.DataFrame(rows, columns=ALIAS_COLUMNS)
    return table.drop_duplicates().reset_index(drop=True)


# --- linking ------------------------------------------------------------------
@dataclass(frozen=True)
class LinkConfig:
    """Tunables for ``link_tennis_data_names``; defaults follow the module docstring."""

    date_window_days: int = 3          # tennis-data date may precede tourney_date by this much (qualifying)
    max_days_after_start: int = 21     # hard cut-off on how far after tourney_date a match may be dated
    match_threshold: float = 0.8
    runner_up_threshold: float = 0.5
    candidate_floor: float = 0.5       # below this a lone candidate is reported as UNMATCHED, not AMBIGUOUS


def _tournament_tokens(name: Any) -> set[str]:
    toks = set(name_tokens(name))
    core = {t for t in toks if t not in TOURNAMENT_STOPWORDS}
    return core or toks


def tournament_score(td_tournament: Any, td_location: Any, sk_tourney_name: Any) -> float:
    """Max of token Jaccard, location containment and alias-table match, in [0, 1]."""
    sk_tokens_all = set(name_tokens(sk_tourney_name))
    if not sk_tokens_all:
        return 0.0
    td_core = _tournament_tokens(td_tournament)
    sk_core = _tournament_tokens(sk_tourney_name)
    jaccard = len(td_core & sk_core) / len(td_core | sk_core) if td_core and sk_core else 0.0
    loc_tokens = set(name_tokens(td_location)) - TOURNAMENT_STOPWORDS
    location = 1.0 if loc_tokens and loc_tokens <= sk_tokens_all else 0.0
    alias = 0.0
    td_norm = normalize_name(td_tournament)
    sk_norm = normalize_name(sk_tourney_name)
    for key, targets in TOURNAMENT_ALIASES.items():
        if key in td_norm and any(t in sk_norm for t in targets):
            alias = 1.0
            break
    return max(jaccard, location, alias)


def round_score(td_round_ordinal: Any, td_round_stage: Any, sk_round: Any, sk_draw_size: Any) -> float:
    """1.0 when rounds agree, 0.5 when off by one, 0.0 otherwise; 0.5 when either side is unknown."""
    sk_stage = _SACKMANN_ROUND_STAGE.get(str(sk_round).upper()) if sk_round is not None else None
    if sk_stage is None:
        return 0.5
    if td_round_stage is not None and not pd.isna(td_round_stage):
        td_stage = int(td_round_stage)
    elif td_round_ordinal is not None and not pd.isna(td_round_ordinal):
        if sk_draw_size is None or pd.isna(sk_draw_size) or int(sk_draw_size) < 2:
            return 0.5
        n_rounds = math.ceil(math.log2(int(sk_draw_size)))
        td_stage = n_rounds - int(td_round_ordinal)
    else:
        return 0.5
    if td_stage == sk_stage:
        return 1.0
    if abs(td_stage - sk_stage) == 1:
        return 0.5
    return 0.0


def date_score(td_date: date, tourney_date: date, level_canonical: Any, cfg: LinkConfig) -> Optional[float]:
    """None when outside the hard window; 1.0 inside the tournament's expected span, decaying outside."""
    diff = (td_date - tourney_date).days
    if diff < -cfg.date_window_days or diff > cfg.max_days_after_start:
        return None
    span = _TOURNAMENT_DAYS.get(str(level_canonical), _DEFAULT_TOURNAMENT_DAYS)
    if 0 <= diff <= span:
        return 1.0
    overshoot = -diff if diff < 0 else diff - span
    return max(0.3, 1.0 - 0.1 * overshoot)


def _candidate_index(matches: pd.DataFrame) -> tuple[dict[tuple[str, str], set[int]], dict[tuple[str, str], set[int]]]:
    """(tour, name token) -> row positions, separately for winner and loser names."""
    w_index: dict[tuple[str, str], set[int]] = defaultdict(set)
    l_index: dict[tuple[str, str], set[int]] = defaultdict(set)
    for pos, (tour, wn, ln) in enumerate(zip(matches["tour"], matches["winner_name"], matches["loser_name"])):
        for tok in name_tokens(wn):
            w_index[(tour, tok)].add(pos)
        for tok in name_tokens(ln):
            l_index[(tour, tok)].add(pos)
    return w_index, l_index


def _surname_key(td_name: Any) -> Optional[str]:
    sur, _ = surname_initials(td_name)
    return sur[-1] if sur else None


def _score_candidate(td: dict[str, Any], sk: dict[str, Any], cfg: LinkConfig) -> Optional[dict[str, float]]:
    """Component scores for one (tennis-data row, Sackmann row) pair; None if a hard filter fails."""
    ds = date_score(td["date"], sk["tourney_date"], sk["level_canonical"], cfg)
    if ds is None:
        return None
    pw = player_match_score(td["winner_name_td"], sk["winner_name"])
    pl = player_match_score(td["loser_name_td"], sk["loser_name"])
    if pw <= 0.0 or pl <= 0.0:
        return None
    ts = tournament_score(td["tournament"], td["location"], sk["tourney_name"])
    rs = round_score(td["round_ordinal"], td["round_stage"], sk["round"], sk["draw_size"])
    if ts == 0.0 and rs == 0.0:
        # Neither the event (name/location/alias) nor the round agrees: this is
        # the same pair meeting at a *different* event in the window, not a
        # plausible alternative, so it must not block a MATCH via the runner-up rule.
        return None
    ss = 1.0 if td["surface"] is not None and sk["surface"] is not None and td["surface"] == sk["surface"] else 0.0
    comp = {"players": (pw + pl) / 2.0, "tournament": ts, "date": ds, "round": rs, "surface": ss}
    comp["confidence"] = sum(WEIGHTS[k] * comp[k] for k in WEIGHTS)
    return comp


def link_tennis_data_names(td_frame: pd.DataFrame, sackmann_matches: pd.DataFrame,
                           config: Optional[LinkConfig] = None) -> pd.DataFrame:
    """Link every tennis-data row to at most one Sackmann ``match_key``.

    One output row per input ``td_key`` (never fewer), with ``status`` in
    {MATCHED, AMBIGUOUS, UNMATCHED}, the best candidate's key/confidence and
    the runner-up's, plus the component scores so reviewers can see *why* a
    row was not matched.
    """
    cfg = config or LinkConfig()
    if len(sackmann_matches) == 0 or len(td_frame) == 0:
        return pd.DataFrame({c: pd.Series(dtype="object") for c in LINK_COLUMNS}).assign(td_key=list(td_frame.get("td_key", [])))
    sk = sackmann_matches.reset_index(drop=True)
    w_index, l_index = _candidate_index(sk)
    sk_records = sk[["match_key", "tour", "tourney_name", "tourney_date", "level_canonical", "surface", "round", "draw_size",
                     "winner_name", "loser_name", "winner_id", "loser_id"]].to_dict("records")
    td_cols = ["td_key", "tour", "date", "tournament", "location", "surface", "round_ordinal", "round_stage", "winner_name_td", "loser_name_td"]
    for c in td_cols:
        if c not in td_frame.columns:
            raise ValueError(f"tennis-data frame lacks column {c!r}")

    out_rows: list[dict[str, Any]] = []
    for td in td_frame[td_cols].to_dict("records"):
        row: dict[str, Any] = {c: None for c in LINK_COLUMNS}
        row.update({"td_key": td["td_key"], "status": UNMATCHED, "n_candidates": 0, "confidence": 0.0, "second_confidence": 0.0})
        wk, lk = _surname_key(td["winner_name_td"]), _surname_key(td["loser_name_td"])
        if td["date"] is None or wk is None or lk is None:
            out_rows.append(row)
            continue
        positions = w_index.get((td["tour"], wk), set()) & l_index.get((td["tour"], lk), set())
        scored = []
        for pos in positions:
            comp = _score_candidate(td, sk_records[pos], cfg)
            if comp is not None:
                scored.append((comp["confidence"], pos, comp))
        scored.sort(key=lambda t: (-t[0], t[1]))
        row["n_candidates"] = len(scored)
        if scored:
            best_conf, best_pos, comp = scored[0]
            best = sk_records[best_pos]
            second_conf = scored[1][0] if len(scored) > 1 else 0.0
            row.update({"match_key": best["match_key"], "confidence": round(best_conf, 4),
                        "second_match_key": sk_records[scored[1][1]]["match_key"] if len(scored) > 1 else None,
                        "second_confidence": round(second_conf, 4),
                        "score_players": comp["players"], "score_tournament": comp["tournament"], "score_date": comp["date"],
                        "score_round": comp["round"], "score_surface": comp["surface"],
                        "winner_id": best["winner_id"], "loser_id": best["loser_id"],
                        "winner_name": best["winner_name"], "loser_name": best["loser_name"]})
            if best_conf > cfg.match_threshold and second_conf < cfg.runner_up_threshold:
                row["status"] = MATCHED
            elif best_conf >= cfg.candidate_floor:
                row["status"] = AMBIGUOUS
            else:
                row["status"] = UNMATCHED
        out_rows.append(row)

    links = pd.DataFrame(out_rows, columns=LINK_COLUMNS)
    counts = links["status"].value_counts().to_dict()
    log.info("tennis-data linking: %s", counts)
    # A Sackmann match claimed by two MATCHED rows is a data problem: demote both to AMBIGUOUS.
    matched = links["status"] == MATCHED
    dup_keys = links.loc[matched, "match_key"].duplicated(keep=False)
    if dup_keys.any():
        idx = links.index[matched][dup_keys.to_numpy()]
        log.warning("%d tennis-data rows share a Sackmann match_key; demoted to AMBIGUOUS", len(idx))
        links.loc[idx, "status"] = AMBIGUOUS
    return links


def link_summary(links: pd.DataFrame) -> dict[str, Any]:
    """Counts per status and confidence quantiles, for run reports."""
    if len(links) == 0:
        return {"rows": 0, "by_status": {}, "confidence_quantiles": {}}
    conf = pd.to_numeric(links["confidence"], errors="coerce").dropna()
    q = conf.quantile([0.1, 0.5, 0.9]).to_dict() if len(conf) else {}
    return {"rows": int(len(links)), "by_status": links["status"].value_counts().to_dict(),
            "confidence_quantiles": {f"p{int(k * 100)}": round(float(v), 4) for k, v in q.items()}}


def registry_lookup(registry: pd.DataFrame, aliases: pd.DataFrame, name: Any) -> list[int]:
    """All player_ids whose alias equals the normalised ``name`` (may be several: ambiguous)."""
    key = normalize_name(name)
    if not key:
        return []
    hits = aliases.loc[aliases["alias"] == key, "player_id"].unique().tolist()
    return [int(h) for h in hits]


def ids_for_names(registry: pd.DataFrame, names: Iterable[Any]) -> dict[str, list[int]]:
    """Convenience: map each raw name to candidate ids via the alias table (bulk)."""
    aliases = build_alias_table(registry)
    return {str(n): registry_lookup(registry, aliases, n) for n in names}
