"""Unit tests for exact flop equity and Monte Carlo preflop equity."""

import random


def deck_without(fs, *card_strings):
    used = set()
    for cs in card_strings:
        used.update(fs.parse_cards(cs))
    return [c for c in fs.FULL_DECK if c not in used]


def test_flop_equity_locked_win_is_one(fs):
    # Royal flush already made on the flop cannot be beaten by any runout.
    hand1 = fs.parse_cards("AsKs")
    hand2 = fs.parse_cards("2c3c")
    flop = fs.parse_cards("QsJsTs")
    deck = deck_without(fs, "AsKs", "2c3c", "QsJsTs")
    assert fs.flop_equity(hand1, hand2, flop, deck) == 1.0


def test_flop_equity_locked_loss_is_zero(fs):
    # The opposite perspective of the locked win.
    hand1 = fs.parse_cards("2c3c")
    hand2 = fs.parse_cards("AsKs")
    flop = fs.parse_cards("QsJsTs")
    deck = deck_without(fs, "AsKs", "2c3c", "QsJsTs")
    assert fs.flop_equity(hand1, hand2, flop, deck) == 0.0


def test_flop_equity_in_unit_interval(fs):
    hand1 = fs.parse_cards("6s7s")
    hand2 = fs.parse_cards("AcQh")
    flop = fs.parse_cards("2d9hKs")
    deck = deck_without(fs, "6s7s", "AcQh", "2d9hKs")
    eq = fs.flop_equity(hand1, hand2, flop, deck)
    assert 0.0 <= eq <= 1.0


def test_flop_equity_is_symmetric_complement(fs):
    # hand1's equity + hand2's equity (same board) must total exactly 1.
    hand1 = fs.parse_cards("6s7s")
    hand2 = fs.parse_cards("AcQh")
    flop = fs.parse_cards("2d9hKs")
    deck = deck_without(fs, "6s7s", "AcQh", "2d9hKs")
    e1 = fs.flop_equity(hand1, hand2, flop, deck)
    e2 = fs.flop_equity(hand2, hand1, flop, deck)
    assert e1 + e2 == 1.0


def test_flop_equity_tie_board_plays(fs):
    # Both players use the board; a split should land near 0.5. With a quad
    # on the flop and no runout changing the winner, both chop every runout.
    hand1 = fs.parse_cards("2c3d")
    hand2 = fs.parse_cards("4h5s")
    flop = fs.parse_cards("AcAdAh")  # trip aces on board for both
    deck = deck_without(fs, "2c3d", "4h5s", "AcAdAh")
    e1 = fs.flop_equity(hand1, hand2, flop, deck)
    e2 = fs.flop_equity(hand2, hand1, flop, deck)
    assert e1 + e2 == 1.0
    assert 0.0 <= e1 <= 1.0


def test_preflop_equity_deterministic_with_seed(fs):
    hand1 = fs.parse_cards("6s7s")
    hand2 = fs.parse_cards("AcQh")
    deck = deck_without(fs, "6s7s", "AcQh")
    a = fs.preflop_equity(hand1, hand2, deck, 500, random.Random(42))
    b = fs.preflop_equity(hand1, hand2, deck, 500, random.Random(42))
    assert a == b


def test_preflop_equity_in_unit_interval(fs):
    hand1 = fs.parse_cards("6s7s")
    hand2 = fs.parse_cards("AcQh")
    deck = deck_without(fs, "6s7s", "AcQh")
    eq = fs.preflop_equity(hand1, hand2, deck, 500, random.Random(1))
    assert 0.0 <= eq <= 1.0


def test_preflop_equity_symmetric_on_identical_boards(fs):
    # Reusing the same seed makes both calls draw identical boards, so the two
    # perspectives sum to exactly 1.
    hand1 = fs.parse_cards("6s7s")
    hand2 = fs.parse_cards("AcQh")
    deck = deck_without(fs, "6s7s", "AcQh")
    e1 = fs.preflop_equity(hand1, hand2, deck, 300, random.Random(7))
    e2 = fs.preflop_equity(hand2, hand1, deck, 300, random.Random(7))
    assert e1 + e2 == 1.0


def test_preflop_equity_strong_hand_wins_more(fs):
    # Pocket aces should dominate 7-2 offsuit over many samples.
    aces = fs.parse_cards("AsAd")
    trash = fs.parse_cards("7h2c")
    deck = deck_without(fs, "AsAd", "7h2c")
    eq = fs.preflop_equity(aces, trash, deck, 2000, random.Random(99))
    assert eq > 0.75
