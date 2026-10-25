"""Test-wide setup.

RISK POLICY FIXTURE. The gate-mechanics tests (preflight, transport, evidence, importer) were written against the
PILOT policy (`pilot-2026-v1`: 0.5%-of-bankroll units, whole-dollar stakes of $10 against a $2,000 bankroll). Those
tests prove that depth, fee, quote-age, ceiling and cap MECHANICS work; the stake numbers in them are fixtures,
not the owner's preferences. The live `config/risk_policy.json` is now the OWNER policy ($75 units, 1U-5U), so by
default `RiskPolicy.load` is pointed at a frozen copy of the pilot file. Nothing about that copy is presented as
policy anywhere: it lives under tests/fixtures and is named for what it is.

Tests of the REAL policy opt out with `@pytest.mark.owner_policy` (see tests/test_owner_policy.py), and
`test_incumbent_unchanged.py` pins the hash of the real file, so the owner policy cannot drift unnoticed.
"""
import os

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PILOT_FIXTURE = os.path.join(ROOT, "tests", "fixtures", "risk_policy_pilot_2026_v1.json")


def pytest_configure(config):
    config.addinivalue_line("markers", "owner_policy: run against the real config/risk_policy.json (owner staking policy)")


@pytest.fixture(autouse=True)
def _pilot_risk_policy_fixture(request, monkeypatch):
    if request.node.get_closest_marker("owner_policy"):
        yield
        return
    from nfl_edge.handicap import risk as R
    monkeypatch.setattr(R, "DEFAULT_POLICY_PATH", PILOT_FIXTURE)   # absolute path: os.path.join(root, abs) == abs
    yield
