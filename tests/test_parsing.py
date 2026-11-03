"""Unit tests for card parsing and formatting helpers."""

import pytest


def test_parse_cards_basic(fs):
    assert fs.parse_cards("6s7s") == [(6, 3), (7, 3)]


def test_parse_cards_case_insensitive(fs):
    assert fs.parse_cards("AcQh") == fs.parse_cards("acqh") == [(14, 0), (12, 2)]


def test_parse_cards_strips_whitespace(fs):
    assert fs.parse_cards("  6s7s  ") == [(6, 3), (7, 3)]


def test_parse_cards_all_ranks(fs):
    text = "2c3c4c5c6c7c8c9cTcJcQcKcAc"
    cards = fs.parse_cards(text)
    assert [r for r, _ in cards] == list(range(2, 15))


def test_parse_cards_all_suits(fs):
    assert fs.parse_cards("AcAdAhAs") == [(14, 0), (14, 1), (14, 2), (14, 3)]


def test_parse_cards_empty_string(fs):
    assert fs.parse_cards("") == []


def test_parse_cards_odd_length_raises(fs):
    with pytest.raises(ValueError, match="odd number of characters"):
        fs.parse_cards("6s7")


def test_parse_cards_bad_rank_raises(fs):
    with pytest.raises(ValueError, match="not a valid rank"):
        fs.parse_cards("1s")


def test_parse_cards_bad_suit_raises(fs):
    with pytest.raises(ValueError, match="not a valid suit"):
        fs.parse_cards("6x")


def test_parse_hand_valid(fs):
    assert fs.parse_hand("AcQh") == [(14, 0), (12, 2)]


def test_parse_hand_too_few_raises(fs):
    with pytest.raises(ValueError, match="needs exactly 2"):
        fs.parse_hand("Ac")


def test_parse_hand_too_many_raises(fs):
    with pytest.raises(ValueError, match="needs exactly 2"):
        fs.parse_hand("AcQhKd")


def test_card_str_roundtrip(fs):
    for card in fs.FULL_DECK:
        assert fs.parse_cards(fs.card_str(card)) == [card]


def test_card_str_specific(fs):
    # Ranks are uppercase, suits lowercase.
    assert fs.card_str((14, 3)) == "As"
    assert fs.card_str((10, 0)) == "Tc"
    assert fs.card_str((2, 1)) == "2d"


def test_hand_str(fs):
    assert fs.hand_str([(6, 3), (7, 3)]) == "6s 7s"


def test_flop_pattern_str_sorted_ascending(fs):
    # (5,c),(4,h),(14,s) -> ascending rank order, no spaces
    flop = [(5, 0), (4, 2), (14, 3)]
    assert fs.flop_pattern_str(flop) == "4h5cAs"


def test_flop_pattern_str_no_spaces(fs):
    s = fs.flop_pattern_str([(2, 0), (3, 1), (4, 2)])
    assert " " not in s
    assert s == "2c3d4h"


def test_full_deck_has_52_unique_cards(fs):
    assert len(fs.FULL_DECK) == 52
    assert len(set(fs.FULL_DECK)) == 52
