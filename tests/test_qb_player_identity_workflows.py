"""PR #241: every workflow that runs scripts/handicap/run_card.py must build the player identity book, or every player prop blocks NO_IDENTITY_SOURCE
(rushing / kicker / defender props that main leaves NOT_GATED would regress to blocked). Pinned as text, per workflow."""
import glob
import os

import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
WF = os.path.join(ROOT, ".github", "workflows")
RUNNERS = sorted(p for p in glob.glob(os.path.join(WF, "*.yml")) if "scripts/handicap/run_card.py" in open(p).read())


def test_the_known_card_workflows_are_covered():
    names = {os.path.basename(p) for p in RUNNERS}
    assert names == {"nfl-thesis-card.yml"}, names          # the only workflow that runs the card; a new one must be added to the pins


@pytest.mark.parametrize("path", RUNNERS, ids=[os.path.basename(p) for p in RUNNERS])
def test_the_card_workflow_supplies_the_identity_tables(path):
    src = open(path).read()
    assert "polars" in src.split("run_card.py")[0], "polars is needed to read the parquet identity tables"
    assert "nflverse_download.py" in src and all(t in src for t in ("players", "weekly_rosters", "ff_playerids")), "the identity tables are not downloaded"
    assert "--raw-root" in src or "--player-identity-root" in src, "run_card.py is not told where the identity tables are"
