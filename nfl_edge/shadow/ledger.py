"""The immutable full-universe shadow ledger.

One row per (capture snapshot x Kalshi market) for every market we can price, plus a row for every market we
*cannot* price carrying the reason. Append-only: a later model never rewrites an earlier opinion. Rows are keyed
by `prediction_id = sha1(run_id | ticker | model_version | calibration_version)` so a re-run of the same snapshot
with the same models is idempotent, while a new model version produces a NEW row rather than overwriting.

Support states (fail closed -- never price through a broken input):
  SUPPORTED               priced
  UNSUPPORTED_MODEL       no validated model for this market family
  UNSUPPORTED_RULES       settlement semantics not established
  UNSUPPORTED_IDENTITY    Kalshi player id not resolved to a GSIS id
  UNSUPPORTED_GAME        market did not join a scheduled game
  STALE_DATA              a required input is older than its freshness budget
  DEGRADED_INPUT          an input was present but failed a quality check
  POST_KICKOFF_EXCLUDED   the observation is after kickoff (kept out of the pregame ledger)

Nothing here selects bets. `selected` is always false; the edge fields are research quantities and are named
`model_market_disagreement`, never "edge".
"""
from __future__ import annotations

import gzip
import hashlib
import json
import os
from dataclasses import dataclass, field, asdict
from datetime import datetime, timezone

SUPPORTED = "SUPPORTED"
UNSUPPORTED_MODEL = "UNSUPPORTED_MODEL"
UNSUPPORTED_RULES = "UNSUPPORTED_RULES"
UNSUPPORTED_IDENTITY = "UNSUPPORTED_IDENTITY"
UNSUPPORTED_GAME = "UNSUPPORTED_GAME"
STALE_DATA = "STALE_DATA"
DEGRADED_INPUT = "DEGRADED_INPUT"
POST_KICKOFF_EXCLUDED = "POST_KICKOFF_EXCLUDED"

LEDGER_SCHEMA_VERSION = "1.0.0"


def prediction_id(run_id: str, ticker: str, model_version: str, calibration_version: str) -> str:
    return hashlib.sha1(f"{run_id}|{ticker}|{model_version}|{calibration_version}".encode()).hexdigest()[:20]


@dataclass
class Observation:
    # identity / lineage
    prediction_id: str
    schema_version: str
    run_id: str
    observed_at: str
    model_version: str
    model_artifact_sha: str
    calibration_version: str
    feature_cutoff: str
    # market identity
    ticker: str
    event_ticker: str | None
    series_ticker: str | None
    family: str | None
    period: str | None
    stat: str | None
    threshold: float | None
    floor_strike: float | None
    operator: str | None
    direction: str = "YES"
    # football identity
    game_id: str | None = None
    season: int | None = None
    week: int | None = None
    home_team: str | None = None
    away_team: str | None = None
    team: str | None = None
    player_id: str | None = None            # canonical GSIS
    player_kalshi_id: str | None = None
    player_name: str | None = None
    kickoff_utc: str | None = None
    minutes_to_kickoff: float | None = None
    # model output -- the football question
    model_event_probability: float | None = None
    # model output -- what the contract is worth (settlement branches folded in)
    model_contract_value: float | None = None
    calibrated_probability: float | None = None
    model_uncertainty: float | None = None
    availability_state: str | None = None
    p_plays: float | None = None
    p_inactive: float | None = None
    game_env_version: str | None = None
    weather_vintage: str | None = None
    # market observed AT THIS TIMESTAMP (never a later or earlier price)
    yes_bid: float | None = None
    yes_ask: float | None = None
    no_bid: float | None = None
    no_ask: float | None = None
    mid: float | None = None
    quote_width: float | None = None
    volume: float | None = None
    open_interest: float | None = None
    last_price: float | None = None
    minutes_since_price_change: float | None = None
    liquidity: float | None = None
    book_depth_yes: float | None = None
    book_depth_no: float | None = None
    book_levels_yes: int | None = None
    book_levels_no: int | None = None
    book_imbalance: float | None = None
    # research-only comparison fields (NOT validated edge)
    model_market_disagreement: float | None = None     # contract value - mid
    raw_yes_disagreement: float | None = None          # contract value - yes_ask (cost to buy YES)
    raw_no_disagreement: float | None = None           # (1 - contract value) - no_ask
    market_implied_mean: float | None = None
    # health
    support_state: str = SUPPORTED
    support_reason: str | None = None
    data_health: str = "healthy"
    quality_flags: list = field(default_factory=list)
    selected: bool = False

    def to_dict(self):
        return asdict(self)


class LedgerWriter:
    """Append-only gzip JSONL, one file per (date, run). Refuses to overwrite an existing run file."""

    def __init__(self, root: str, run_id: str, day: str | None = None):
        self.run_id = run_id
        self.day = day or run_id[:4] + "-" + run_id[4:6] + "-" + run_id[6:8]
        self.dir = os.path.join(root, self.day)
        os.makedirs(self.dir, exist_ok=True)
        self.path = os.path.join(self.dir, f"{run_id}.observations.jsonl.gz")
        if os.path.exists(self.path):
            raise FileExistsError(f"ledger file already exists (append-only, never rewritten): {self.path}")
        self._fh = gzip.open(self.path, "wt")
        self._ids = set()
        self.counts = {"written": 0, "duplicate": 0}
        self.by_state = {}
        self.by_family = {}

    def write(self, obs: Observation):
        if obs.prediction_id in self._ids:
            self.counts["duplicate"] += 1
            return False
        self._ids.add(obs.prediction_id)
        self._fh.write(json.dumps(obs.to_dict(), separators=(",", ":")) + "\n")
        self.counts["written"] += 1
        self.by_state[obs.support_state] = self.by_state.get(obs.support_state, 0) + 1
        key = f"{obs.family}|{obs.period}"
        self.by_family[key] = self.by_family.get(key, 0) + 1
        return True

    def close(self, manifest_extra: dict | None = None):
        self._fh.close()
        man = {"run_id": self.run_id, "schema_version": LEDGER_SCHEMA_VERSION,
               "written_at": datetime.now(timezone.utc).isoformat(), "counts": self.counts,
               "by_support_state": self.by_state, "by_family": self.by_family,
               "observations_file": os.path.basename(self.path)}
        man.update(manifest_extra or {})
        with open(os.path.join(self.dir, f"{self.run_id}.ledger_manifest.json"), "w") as f:
            json.dump(man, f, indent=1)
        return man
