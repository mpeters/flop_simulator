"""Functional tests driving main() (and the executable) end to end."""

import os
import subprocess
import sys

import pytest

SCRIPT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "flop_sim"
)


# --- Happy paths through main(argv) ---------------------------------------- #

def test_main_equity_run(fs, capsys):
    fs.main([
        "--hand1", "6s7s", "--hand2", "AcQh",
        "--sims", "20", "--preflop-samples", "200",
        "--seed", "1", "--buckets", "5", "--quiet",
    ])
    out = capsys.readouterr().out
    assert "FLOP EQUITY SIMULATION" in out
    assert "20 flops" in out


def test_main_is_reproducible_with_seed(fs, capsys):
    argv = ["--hand1", "6s7s", "--hand2", "AcQh", "--sims", "30",
            "--preflop-samples", "200", "--seed", "123", "--quiet"]
    fs.main(argv)
    first = capsys.readouterr().out
    fs.main(argv)
    second = capsys.readouterr().out
    assert first == second


def test_main_pattern_only_mode(fs, capsys):
    fs.main([
        "--sims", "200", "--seed", "5", "--quiet",
        "--pattern", ".s.*.s",
    ])
    out = capsys.readouterr().out
    assert "FLOP PATTERN MATCHES" in out
    assert "/200" in out
    # No equity section in pattern-only mode.
    assert "FLOP EQUITY SIMULATION" not in out


def test_main_pattern_with_equity(fs, capsys):
    fs.main([
        "--hand1", "6s7s", "--hand2", "AcQh",
        "--sims", "50", "--preflop-samples", "100", "--seed", "2",
        "--quiet", "--pattern", "4..*5",
    ])
    out = capsys.readouterr().out
    assert "FLOP EQUITY SIMULATION" in out
    assert "FLOP PATTERN MATCHES" in out


def test_main_pattern_or_logic(fs, capsys):
    fs.main([
        "--sims", "300", "--seed", "3", "--quiet",
        "--pattern", "A", "--pattern-or", "s.*s", "--pattern-or", "h.*h",
    ])
    out = capsys.readouterr().out
    assert "matches ANY of:" in out


def test_main_with_dead_cards(fs, capsys):
    fs.main([
        "--hand1", "6s7s", "--hand2", "AcQh",
        "--sims", "20", "--preflop-samples", "100", "--seed", "4",
        "--dead", "2c2d9h", "--quiet",
    ])
    out = capsys.readouterr().out
    assert "FLOP EQUITY SIMULATION" in out


def test_main_progress_indicator_to_stderr(fs, capsys):
    # Without --quiet, progress is written to stderr (every 50 sims).
    fs.main([
        "--hand1", "6s7s", "--hand2", "AcQh",
        "--sims", "50", "--preflop-samples", "100", "--seed", "6",
    ])
    captured = capsys.readouterr()
    assert "simulating flops" in captured.err
    assert "Computing preflop equity" in captured.err


# --- Argument / validation errors (argparse exits with code 2) ------------- #

def test_main_no_hands_no_pattern_errors(fs):
    with pytest.raises(SystemExit):
        fs.main(["--sims", "10", "--quiet"])


def test_main_only_one_hand_errors(fs):
    with pytest.raises(SystemExit):
        fs.main(["--hand1", "6s7s", "--sims", "10", "--quiet"])


def test_main_bad_sims_errors(fs):
    with pytest.raises(SystemExit):
        fs.main(["--hand1", "6s7s", "--hand2", "AcQh", "--sims", "0", "--quiet"])


def test_main_bad_buckets_errors(fs):
    with pytest.raises(SystemExit):
        fs.main(["--hand1", "6s7s", "--hand2", "AcQh",
                 "--sims", "10", "--buckets", "0", "--quiet"])


def test_main_bad_hand_string_errors(fs):
    with pytest.raises(SystemExit):
        fs.main(["--hand1", "1s", "--hand2", "AcQh", "--sims", "10", "--quiet"])


def test_main_duplicate_card_between_hands_errors(fs):
    with pytest.raises(SystemExit):
        fs.main(["--hand1", "AcQh", "--hand2", "AcKd", "--sims", "10", "--quiet"])


def test_main_dead_duplicate_errors(fs):
    with pytest.raises(SystemExit):
        fs.main(["--hand1", "6s7s", "--hand2", "AcQh",
                 "--dead", "2c2c", "--sims", "10", "--quiet"])


def test_main_dead_clashes_with_hand_errors(fs):
    with pytest.raises(SystemExit):
        fs.main(["--hand1", "6s7s", "--hand2", "AcQh",
                 "--dead", "6s", "--sims", "10", "--quiet"])


def test_main_bad_dead_string_errors(fs):
    with pytest.raises(SystemExit):
        fs.main(["--hand1", "6s7s", "--hand2", "AcQh",
                 "--dead", "zz", "--sims", "10", "--quiet"])


def test_main_invalid_regex_pattern_errors(fs):
    with pytest.raises(SystemExit):
        fs.main(["--sims", "10", "--quiet", "--pattern", "("])


def test_main_too_few_live_cards_errors(fs):
    # Remove almost the whole deck via --dead so < 3 live cards remain.
    all_cards = "".join(fs.card_str(c) for c in fs.FULL_DECK)
    cards = fs.parse_cards(all_cards)
    # Keep only 2 cards live: dead = everything except two, minus the 4 hand cards.
    hand_cards = set(fs.parse_cards("6s7sAcQh"))
    dead_cards = [c for c in cards if c not in hand_cards][:-2]  # leave 2 live
    dead_str = "".join(fs.card_str(c) for c in dead_cards)
    with pytest.raises(SystemExit):
        fs.main(["--hand1", "6s7s", "--hand2", "AcQh",
                 "--dead", dead_str, "--sims", "10", "--quiet"])


# --- End-to-end via the executable ----------------------------------------- #

def test_executable_runs_end_to_end():
    result = subprocess.run(
        [sys.executable, SCRIPT,
         "--hand1", "6s7s", "--hand2", "AcQh",
         "--sims", "10", "--preflop-samples", "100", "--seed", "1", "--quiet"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "FLOP EQUITY SIMULATION" in result.stdout


def test_executable_help():
    result = subprocess.run(
        [sys.executable, SCRIPT, "--help"],
        capture_output=True, text=True,
    )
    assert result.returncode == 0
    assert "flop" in result.stdout.lower()
