"""Unit tests for the formatting/reporting helpers."""

import re


def test_pct_formatting(fs):
    assert fs.pct(0.5) == "50.00%"
    assert fs.pct(1.0) == "100.00%"
    assert fs.pct(0.0) == " 0.00%"


def test_histogram_line_count_matches_buckets(fs):
    lines = fs.histogram([0.1, 0.5, 0.9], buckets=10)
    assert len(lines) == 10


def test_histogram_counts_sum_to_n(fs):
    equities = [0.05, 0.15, 0.25, 0.95]
    lines = fs.histogram(equities, buckets=10)
    counts = [int(re.search(r"\|.*?(\d+) \(", line).group(1)) for line in lines]
    assert sum(counts) == len(equities)


def test_histogram_equity_of_one_goes_in_last_bucket(fs):
    # An equity of exactly 1.0 must be clamped into the final bucket.
    lines = fs.histogram([1.0], buckets=4)
    last = lines[-1]
    assert re.search(r"1 \(", last)


def test_histogram_single_bucket(fs):
    lines = fs.histogram([0.1, 0.9], buckets=1)
    assert len(lines) == 1
    assert "2" in lines[0]


def test_print_report_contains_key_sections(fs, capsys):
    hand1 = fs.parse_cards("6s7s")
    hand2 = fs.parse_cards("AcQh")
    equities = [0.3, 0.5, 0.7, 0.9, 0.1]
    fs.print_report(hand1, hand2, 0.4, equities, buckets=5)
    out = capsys.readouterr().out
    assert "FLOP EQUITY SIMULATION" in out
    assert "Preflop" in out
    assert "Realization" in out
    assert "6s 7s" in out
    assert "Ac Qh" in out


def test_print_report_hand_labels_present(fs, capsys):
    hand1 = fs.parse_cards("6s7s")
    hand2 = fs.parse_cards("AcQh")
    fs.print_report(hand1, hand2, 0.4, [0.5, 0.5], buckets=4)
    out = capsys.readouterr().out
    assert fs.hand_str(hand1) in out
    assert fs.hand_str(hand2) in out


def test_print_report_crush_and_dust_stats(fs, capsys):
    hand1 = fs.parse_cards("6s7s")
    hand2 = fs.parse_cards("AcQh")
    equities = [0.9, 0.85, 0.1, 0.05, 0.5]
    fs.print_report(hand1, hand2, 0.5, equities, buckets=5)
    out = capsys.readouterr().out
    assert "ahead (>50%)" in out
    assert "crushing (>=80%)" in out
    assert "in the dust (<=20%)" in out


def test_print_pattern_report_empty_prints_nothing(fs, capsys):
    fs.print_pattern_report([], [], 0, 100)
    assert capsys.readouterr().out == ""


def test_print_pattern_report_with_and_patterns(fs, capsys):
    patterns = [("4..*5", None)]
    fs.print_pattern_report(patterns, [], 25, 100)
    out = capsys.readouterr().out
    assert "FLOP PATTERN MATCHES" in out
    assert "4..*5" in out
    assert "25/100" in out
    assert "25.0%" in out


def test_print_pattern_report_with_or_patterns(fs, capsys):
    patterns = [("A", None)]
    or_patterns = [("s.*s", None), ("h.*h", None)]
    fs.print_pattern_report(patterns, or_patterns, 10, 100)
    out = capsys.readouterr().out
    assert "matches ANY of:" in out
    assert "s.*s" in out
    assert "h.*h" in out
