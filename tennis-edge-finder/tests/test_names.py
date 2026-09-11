import pytest

from tennis_edge.identity.names import (
    last_first_initial, name_tokens, normalize_name, player_match_score, strip_diacritics, surname_initials,
)


@pytest.mark.parametrize("raw,expected", [
    ("Roger Federer", "roger federer"),
    ("Novak Đoković", "novak dokovic"),
    ("Borna Ćorić", "borna coric"),
    ("Félix Auger-Aliassime", "felix auger aliassime"),
    ("Christopher O'Connell", "christopher o connell"),
    ("Federer R.", "federer r"),
    ("Kwon S.W.", "kwon s w"),
    ("  Rafael   Nadal  ", "rafael nadal"),
    ("Alexander Zverev Jr.", "alexander zverev"),
    ("John Smith III", "john smith"),
    ("Søren Hess-Olesen", "soren hess olesen"),
    ("Łukasz Kubot", "lukasz kubot"),
    ("", ""),
    (None, ""),
    (float("nan"), ""),
])
def test_normalize_name(raw, expected):
    assert normalize_name(raw) == expected


def test_strip_diacritics_handles_non_decomposing_letters():
    assert strip_diacritics("Øystein Ærø ß") == "Oystein AEro ss"


def test_name_tokens():
    assert name_tokens("Alex De Minaur") == ("alex", "de", "minaur")
    assert name_tokens(None) == ()


@pytest.mark.parametrize("raw,surname,initials", [
    ("Federer R.", ("federer",), ("r",)),
    ("Kwon S.W.", ("kwon",), ("s", "w")),
    ("De Minaur A.", ("de", "minaur"), ("a",)),
    ("Bautista Agut R.", ("bautista", "agut"), ("r",)),
    ("Auger-Aliassime F.", ("auger", "aliassime"), ("f",)),
    ("O'Connell C.", ("o", "connell"), ("c",)),
    ("Kuznetsov An.", ("kuznetsov",), ("an",)),
    ("Zverev A", ("zverev",), ("a",)),          # period dropped: trailing single letter
    ("Roger Federer", ("roger", "federer"), ()),  # full name: no initials
    ("Nadal", ("nadal",), ()),
    ("", (), ()),
    (None, (), ()),
])
def test_surname_initials(raw, surname, initials):
    assert surname_initials(raw) == (surname, initials)


@pytest.mark.parametrize("td_name,full,expected", [
    ("Federer R.", "Roger Federer", 1.0),
    ("Nadal R.", "Rafael Nadal", 1.0),
    ("Zverev A.", "Alexander Zverev", 1.0),
    ("Zverev A.", "Mischa Zverev", 0.0),           # wrong initial is never partial credit
    ("Zverev M.", "Mischa Zverev", 1.0),
    ("Kwon S.W.", "Soon Woo Kwon", 1.0),
    ("Kwon S.", "Soon Woo Kwon", 0.9),             # fewer initials than first-name tokens
    ("Kwon S.X.", "Soon Woo Kwon", 0.9),           # first initial ok, second wrong
    ("Kuznetsov An.", "Andrey Kuznetsov", 1.0),
    ("Kuznetsov An.", "Alexey Kuznetsov", 0.0),    # two-letter group disambiguates
    ("Kuznetsov A.", "Alexey Kuznetsov", 1.0),
    ("De Minaur A.", "Alex De Minaur", 1.0),
    ("Bautista Agut R.", "Roberto Bautista Agut", 1.0),
    ("Auger-Aliassime F.", "Félix Auger-Aliassime", 1.0),
    ("O'Connell C.", "Christopher O'Connell", 1.0),
    ("Federer", "Roger Federer", 0.7),             # surname only
    ("Federer R.", "Rafael Nadal", 0.0),
    ("Federer R.", "", 0.0),
    ("", "Roger Federer", 0.0),
])
def test_player_match_score(td_name, full, expected):
    assert player_match_score(td_name, full) == expected


def test_player_match_score_with_registry_last_name():
    # "Alexander" is a first name here, not a surname, so it must not match "Alexander Z."
    assert player_match_score("Alexander Z.", "Alexander Bublik", last_name="Bublik") == 0.0
    assert player_match_score("Bublik A.", "Alexander Bublik", last_name="Bublik") == 1.0
    assert player_match_score("Bautista Agut R.", "Roberto Bautista Agut", last_name="Bautista Agut") == 1.0


def test_last_first_initial():
    assert last_first_initial("Roger", "Federer") == "federer r"
    assert last_first_initial("Félix", "Auger-Aliassime") == "auger aliassime f"
    assert last_first_initial(None, "Nadal") == "nadal"
    assert last_first_initial("Roger", None) == ""
