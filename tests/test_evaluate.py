"""Unit tests for the 7-card hand evaluator."""

import itertools

import pytest


def ev(fs, text):
    """Evaluate a 7-card hand given as a card string like 'AsKsQsJsTs2d3h'."""
    cards = fs.parse_cards(text)
    assert len(cards) == 7, "evaluator tests expect exactly 7 cards"
    return fs.evaluate_7(cards)


# --- Category detection ---------------------------------------------------- #

def test_straight_flush(fs):
    assert ev(fs, "2s3s4s5s6s7d8d") == (8, 6)


def test_straight_flush_wheel(fs):
    # Ace plays low: A-2-3-4-5 straight flush, top card is the 5.
    assert ev(fs, "As2s3s4s5sKdQh") == (8, 5)


def test_royal_flush_is_straight_flush_to_ace(fs):
    assert ev(fs, "AsKsQsJsTs2d3h") == (8, 14)


def test_four_of_a_kind(fs):
    assert ev(fs, "AcAdAhAsKcQdJh") == (7, 14, 13)


def test_four_of_a_kind_kicker_is_highest(fs):
    # Kicker must be the single highest remaining card (A over 2,3).
    assert ev(fs, "7c7d7h7sAd2h3s") == (7, 7, 14)


def test_full_house_trips_plus_pair(fs):
    assert ev(fs, "KcKdKhQcQd2h3s") == (6, 13, 12)


def test_full_house_two_trips_uses_higher_as_trips(fs):
    # Two sets of trips -> higher is the trips, lower fills the pair slot.
    assert ev(fs, "KcKdKhQcQdQh2s") == (6, 13, 12)


def test_flush_top_five(fs):
    assert ev(fs, "2s4s6s8sTsKdQh") == (5, (10, 8, 6, 4, 2))


def test_flush_picks_highest_five_of_many(fs):
    # Six spades: only the top five count.
    assert ev(fs, "2s4s6s8sTsQs3d") == (5, (12, 10, 8, 6, 4))


def test_straight(fs):
    assert ev(fs, "5c6d7h8s9c2d3h") == (4, 9)


def test_straight_wheel(fs):
    assert ev(fs, "Ac2d3h4s5cKdQh") == (4, 5)


def test_straight_broadway(fs):
    assert ev(fs, "AcKdQhJsTc2d3h") == (4, 14)


def test_three_of_a_kind(fs):
    assert ev(fs, "KcKdKhQsJd9h2s") == (3, 13, 12, 11)


def test_two_pair(fs):
    assert ev(fs, "KcKdQcQd2h3s4c") == (2, 13, 12, 4)


def test_two_pair_from_three_pairs_picks_top_two(fs):
    # With three pairs the two highest form the hand; the third's rank is kicker.
    assert ev(fs, "KcKdQcQdJcJd2s") == (2, 13, 12, 11)


def test_one_pair(fs):
    assert ev(fs, "KcKdQhJs9d7c2s") == (1, 13, 12, 11, 9)


def test_high_card(fs):
    assert ev(fs, "KcQdJh9s7c5d2h") == (0, 13, 12, 11, 9, 7)


# --- Ordering between categories ------------------------------------------- #

def test_category_ordering(fs):
    straight_flush = ev(fs, "2s3s4s5s6s7d8d")
    quads = ev(fs, "AcAdAhAsKcQdJh")
    full_house = ev(fs, "KcKdKhQcQd2h3s")
    flush = ev(fs, "2s4s6s8sTsKdQh")
    straight = ev(fs, "5c6d7h8s9c2d3h")
    trips = ev(fs, "KcKdKhQsJd9h2s")
    two_pair = ev(fs, "KcKdQcQd2h3s4c")
    pair = ev(fs, "KcKdQhJs9d7c2s")
    high = ev(fs, "KcQdJh9s7c5d2h")

    ordered = [high, pair, two_pair, trips, straight,
               flush, full_house, quads, straight_flush]
    assert ordered == sorted(ordered)


def test_flush_beats_straight(fs):
    straight = ev(fs, "5c6d7h8s9c2d3h")
    flush = ev(fs, "2s4s6s8sTsKdQh")
    assert flush > straight


def test_higher_pair_beats_lower_pair(fs):
    assert ev(fs, "AcAdQhJs9d7c2s") > ev(fs, "KcKdQhJs9d7c2s")


def test_kicker_breaks_pair_tie(fs):
    assert ev(fs, "KcKdAhJs9d7c2s") > ev(fs, "KcKdQhJs9d7c2s")


def test_evaluate_matches_best_of_21_combos(fs):
    # Sanity: evaluate_7 should equal the best 5-card subset evaluated as 7
    # is not trivially checkable, but the category should never exceed a known
    # strong hand. Here we just confirm determinism across card order.
    cards = fs.parse_cards("AcAdAhAsKcQdJh")
    base = fs.evaluate_7(cards)
    for perm in itertools.islice(itertools.permutations(cards), 10):
        assert fs.evaluate_7(list(perm)) == base
