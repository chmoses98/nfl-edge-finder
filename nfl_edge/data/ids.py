"""Entity resolution: canonical player / team / game identifiers.

Canonical player key: nflverse GSIS id (e.g. '00-0033873'). Every other id is a
*crosswalk* attribute, never a join key at prediction time. Sources, in priority
order, each preserved with its provenance so a disagreement is visible:
  1. nflverse players.parquet          (gsis, esb, nfl_id, pfr, pff, otc, espn, smart)
  2. nflverse weekly rosters           (gsis, espn, sportradar, yahoo, rotowire, pff, pfr, fantasy_data, sleeper)
  3. dynastyprocess db_playerids.csv   (mfl, sportradar, fantasypros, gsis, pff, sleeper, nfl, espn, yahoo, cbs, pfr, cfbref, rotowire, ...)

Kalshi player-prop tickers do NOT carry a player id; they carry a name token
(e.g. 'CARADILLON28' = team + surname-ish token + jersey number). Resolution of
those tokens is a separate, auditable step (kalshi.classifier -> ids.resolve_kalshi_player)
that must produce a confidence and never silently fuzzy-match.

Team canonical key: nflverse 3-letter code with relocations normalized to the
CURRENT code (OAK->LV, SD->LAC, STL->LA). Historical franchise identity is kept in
`franchise` where needed.
"""
from __future__ import annotations
import os, re, unicodedata
import polars as pl

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RAW = os.path.join(ROOT, "data", "raw", "nflverse")

TEAM_ALIASES = {
    "OAK": "LV", "SD": "LAC", "STL": "LA", "LAR": "LA", "ARZ": "ARI", "AZ": "ARI", "BLT": "BAL", "CLV": "CLE",
    "HST": "HOU", "JAC": "JAX", "SL": "LA", "WSH": "WAS", "LVR": "LV", "GBP": "GB", "KCC": "KC", "NEP": "NE",
    "NOS": "NO", "SFO": "SF", "TBB": "TB",
}
TEAMS = ["ARI", "ATL", "BAL", "BUF", "CAR", "CHI", "CIN", "CLE", "DAL", "DEN", "DET", "GB", "HOU", "IND", "JAX", "KC",
         "LA", "LAC", "LV", "MIA", "MIN", "NE", "NO", "NYG", "NYJ", "PHI", "PIT", "SEA", "SF", "TB", "TEN", "WAS"]
# Kalshi uses its own team codes in tickers; observed so far (from MLB/CFB experience the code set is
# mostly standard but verify against discovery output): keep an explicit, auditable map.
KALSHI_TEAM_CODES = {t: t for t in TEAMS}
KALSHI_TEAM_CODES.update({"ARZ": "ARI", "LAR": "LA", "WSH": "WAS", "JAC": "JAX"})

# Full names -> codes (Kalshi titles use city or nickname, e.g. "Kansas City" / "Chiefs")
TEAM_NAMES = {
    "ARI": ("Arizona", "Cardinals"), "ATL": ("Atlanta", "Falcons"), "BAL": ("Baltimore", "Ravens"), "BUF": ("Buffalo", "Bills"),
    "CAR": ("Carolina", "Panthers"), "CHI": ("Chicago", "Bears"), "CIN": ("Cincinnati", "Bengals"), "CLE": ("Cleveland", "Browns"),
    "DAL": ("Dallas", "Cowboys"), "DEN": ("Denver", "Broncos"), "DET": ("Detroit", "Lions"), "GB": ("Green Bay", "Packers"),
    "HOU": ("Houston", "Texans"), "IND": ("Indianapolis", "Colts"), "JAX": ("Jacksonville", "Jaguars"), "KC": ("Kansas City", "Chiefs"),
    "LA": ("Los Angeles Rams", "Rams"), "LAC": ("Los Angeles Chargers", "Chargers"), "LV": ("Las Vegas", "Raiders"), "MIA": ("Miami", "Dolphins"),
    "MIN": ("Minnesota", "Vikings"), "NE": ("New England", "Patriots"), "NO": ("New Orleans", "Saints"), "NYG": ("New York Giants", "Giants"),
    "NYJ": ("New York Jets", "Jets"), "PHI": ("Philadelphia", "Eagles"), "PIT": ("Pittsburgh", "Steelers"), "SEA": ("Seattle", "Seahawks"),
    "SF": ("San Francisco", "49ers"), "TB": ("Tampa Bay", "Buccaneers"), "TEN": ("Tennessee", "Titans"), "WAS": ("Washington", "Commanders"),
}


def canon_team(code: str | None) -> str | None:
    if code is None:
        return None
    c = code.strip().upper()
    c = TEAM_ALIASES.get(c, c)
    return c if c in TEAMS else None


def team_from_name(text: str) -> str | None:
    """Resolve a city/nickname mention to a canonical code. Returns None if ambiguous/unknown."""
    t = text.lower()
    hits = set()
    for code, (city, nick) in TEAM_NAMES.items():
        if nick.lower() in t:
            hits.add(code)
    if len(hits) == 1:
        return hits.pop()
    # city match (LA / NY ambiguity handled by requiring nickname above)
    for code, (city, nick) in TEAM_NAMES.items():
        if city.lower() in t and code not in ("LA", "LAC", "NYG", "NYJ"):
            hits.add(code)
    return hits.pop() if len(hits) == 1 else None


def _norm_name(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode()
    s = re.sub(r"[^a-z ]", "", s.lower())
    s = re.sub(r"\b(jr|sr|ii|iii|iv|v)\b", "", s)
    return re.sub(r"\s+", " ", s).strip()


def build_player_crosswalk() -> pl.DataFrame:
    """One row per GSIS id with every external id we can find, plus provenance flags."""
    p = pl.read_parquet(os.path.join(RAW, "players", "players.parquet"))
    base = p.select(
        pl.col("gsis_id"), pl.col("display_name"), pl.col("first_name"), pl.col("last_name"), pl.col("football_name"),
        pl.col("position"), pl.col("position_group"), pl.col("birth_date"), pl.col("height"), pl.col("weight"),
        pl.col("rookie_season"), pl.col("last_season"), pl.col("latest_team"), pl.col("status"), pl.col("draft_year"),
        pl.col("draft_round"), pl.col("draft_pick"), pl.col("college_name"),
        pl.col("esb_id"), pl.col("nfl_id").alias("nfl_id_players"), pl.col("pfr_id").alias("pfr_id_players"),
        pl.col("pff_id").alias("pff_id_players"), pl.col("otc_id"), pl.col("espn_id").alias("espn_id_players"), pl.col("smart_id"),
    ).filter(pl.col("gsis_id").is_not_null())
    # rosters (latest row per gsis)
    ros = []
    for s in range(2016, 2027):
        f = os.path.join(RAW, "rosters", f"roster_{s}.parquet")
        if os.path.exists(f):
            r = pl.read_parquet(f).select(["season", "gsis_id", "espn_id", "sportradar_id", "yahoo_id", "rotowire_id", "pff_id", "pfr_id", "fantasy_data_id", "sleeper_id", "jersey_number", "team"])
            ros.append(r)
    ros = pl.concat(ros, how="diagonal_relaxed").filter(pl.col("gsis_id").is_not_null()).sort("season").group_by("gsis_id").last()
    ros = ros.rename({c: f"{c}_roster" for c in ros.columns if c != "gsis_id"})
    dp = pl.read_csv(os.path.join(RAW, "ff_playerids", "db_playerids.csv"), infer_schema_length=100000)
    dp = dp.filter(pl.col("gsis_id").is_not_null()).select(["gsis_id", "mfl_id", "sportradar_id", "fantasypros_id", "pff_id", "sleeper_id", "nfl_id", "espn_id", "yahoo_id", "cbs_id", "pfr_id", "cfbref_id", "rotowire_id", "rotoworld_id", "ktc_id", "fantasy_data_id", "merge_name"])
    dp = dp.rename({c: f"{c}_dp" for c in dp.columns if c != "gsis_id"}).unique(subset=["gsis_id"])
    x = base.join(ros, on="gsis_id", how="left").join(dp, on="gsis_id", how="left")
    # coalesce with provenance
    def coal(name, cols):
        return [pl.coalesce([pl.col(c).cast(pl.Utf8) for c in cols]).alias(name),
                pl.when(pl.col(cols[0]).is_not_null()).then(pl.lit(cols[0])).otherwise(
                    pl.when(pl.col(cols[1]).is_not_null()).then(pl.lit(cols[1])).otherwise(
                        pl.when(pl.col(cols[2]).is_not_null()).then(pl.lit(cols[2])).otherwise(None) if len(cols) > 2 else None)).alias(f"{name}_src")]
    exprs = []
    exprs += coal("espn_id", ["espn_id_players", "espn_id_roster", "espn_id_dp"])
    exprs += coal("pfr_id", ["pfr_id_players", "pfr_id_roster", "pfr_id_dp"])
    exprs += coal("pff_id", ["pff_id_players", "pff_id_roster", "pff_id_dp"])
    exprs += coal("sleeper_id", ["sleeper_id_roster", "sleeper_id_dp"])
    exprs += coal("sportradar_id", ["sportradar_id_roster", "sportradar_id_dp"])
    exprs += coal("rotowire_id", ["rotowire_id_roster", "rotowire_id_dp"])
    exprs += coal("yahoo_id", ["yahoo_id_roster", "yahoo_id_dp"])
    exprs += coal("fantasy_data_id", ["fantasy_data_id_roster", "fantasy_data_id_dp"])
    x = x.with_columns(exprs)
    # disagreement flags (same id type from two sources but different values)
    x = x.with_columns([
        ((pl.col("espn_id_players").cast(pl.Utf8) != pl.col("espn_id_roster").cast(pl.Utf8)) & pl.col("espn_id_players").is_not_null() & pl.col("espn_id_roster").is_not_null()).alias("espn_id_conflict"),
        ((pl.col("pfr_id_players") != pl.col("pfr_id_roster")) & pl.col("pfr_id_players").is_not_null() & pl.col("pfr_id_roster").is_not_null()).alias("pfr_id_conflict"),
        pl.col("display_name").map_elements(_norm_name, return_dtype=pl.Utf8).alias("name_key"),
    ])
    return x


def build_team_table() -> pl.DataFrame:
    t = pl.read_parquet(os.path.join(RAW, "teams", "teams_colors_logos.parquet"))
    return t.with_columns(pl.col("team_abbr").map_elements(lambda c: canon_team(c) or c, return_dtype=pl.Utf8).alias("team"))


if __name__ == "__main__":
    out = os.path.join(ROOT, "data", "silver")
    os.makedirs(out, exist_ok=True)
    x = build_player_crosswalk()
    x.write_parquet(os.path.join(out, "player_crosswalk.parquet"))
    act = x.filter(pl.col("last_season") >= 2025)
    print("players:", x.height, "active-ish:", act.height)
    print(act.select(pl.col(["espn_id", "pfr_id", "pff_id", "sleeper_id", "sportradar_id", "rotowire_id"]).is_not_null().mean()))
    print("conflicts espn:", x["espn_id_conflict"].sum(), "pfr:", x["pfr_id_conflict"].sum())
    dup = act.group_by("name_key").len().filter(pl.col("len") > 1)
    print("active duplicate name keys:", dup.height)
