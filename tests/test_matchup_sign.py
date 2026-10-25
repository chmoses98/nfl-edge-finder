"""The matchup block's sign convention: ratings come from y = off_t + def_opp, so expected edge is offence + defence.

A defence rating is EPA ALLOWED above average (positive = worse). Until 2026-10-25 the packet subtracted it, which made a good defence
look like a gift to the offence on six of the seven pairs.
"""
from nfl_edge.handicap.packet import matchup_advantages


def prof(off_epa, def_epa, off_sack=0.0, def_sack=0.0):
    return {"adjusted": {"off_db_epa": off_epa, "def_db_epa": def_epa, "off_rush_epa": 0.0, "def_rush_epa": 0.0, "off_ed_epa": 0.0, "def_ed_epa": 0.0,
                         "off_explosive": 0.0, "def_explosive": 0.0, "off_epa": off_epa, "def_epa": def_epa, "off_epa_ng": 0.0, "def_epa_ng": 0.0,
                         "off_sack_rate": off_sack, "def_sack_rate": def_sack}}


def pair(out, label, offense):
    return next(p for p in out["pairs"] if p["matchup"] == label and p["offense"] == offense)


def test_a_good_defence_reduces_the_offences_edge_and_a_bad_one_increases_it():
    good_d = matchup_advantages({"A": prof(0.10, 0.0), "B": prof(0.0, -0.10)}, "A", "B")        # B's defence allows 0.10 LESS EPA than average
    bad_d = matchup_advantages({"A": prof(0.10, 0.0), "B": prof(0.0, +0.10)}, "A", "B")
    assert pair(good_d, "pass offense vs pass defense", "A")["advantage_to_offense"] == 0.0     # +0.10 offence, -0.10 defence
    assert pair(bad_d, "pass offense vs pass defense", "A")["advantage_to_offense"] == 0.2


def test_the_sack_pair_is_still_oriented_against_the_offence():
    out = matchup_advantages({"A": prof(0, 0, off_sack=0.02, def_sack=0.0), "B": prof(0, 0, off_sack=0.0, def_sack=0.03)}, "A", "B")
    assert pair(out, "pass protection vs pass rush", "A")["advantage_to_offense"] == -0.05     # allows more sacks than average AND faces a pass rush
