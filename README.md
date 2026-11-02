# flop_simulator

A dependency-free (stdlib-only) CLI that simulates flop boards in Texas Hold'em,
compares two hands, and shows how each hand's equity develops after the flop.

For every simulated flop the tool computes **exact** equity by enumerating all
990 possible turn + river runouts, then reports:

- Preflop equity (Monte Carlo) vs. average post-flop equity
- **Equity realization (Δ)** — the difference between the two
- A spread of statistics (mean / median / std / min / max)
- An ASCII histogram of the equity distribution across flops

## Usage

```bash
./flop_sim --hand1 "6s7s" --hand2 "AcQh" --sims 100
```

Cards are two characters each, case-insensitive: rank (`2`-`9`, `T`, `J`, `Q`,
`K`, `A`) + suit (`c`, `d`, `h`, `s`). A hand is two cards, e.g. `6s7s`, `AcQh`.

### Options

| Flag | Default | Description |
|------|---------|-------------|
| `--hand1` / `--hand2` | (required\*) | The two hands to compare (\*optional when only matching `--pattern`) |
| `-n`, `--sims` | `1000` | Number of flops to simulate |
| `--preflop-samples` | `25000` | Monte Carlo samples for preflop equity |
| `--buckets` | `20` | Histogram buckets |
| `--seed` | none | Seed for reproducible runs |
| `--pattern` | none | Regular expression matched against each flop; repeatable, AND-combined (see below) |
| `--pattern-or` | none | Like `--pattern`, but repeats are OR-combined, then AND-ed with `--pattern` |
| `--quiet` | off | Suppress the progress indicator |

### Flop patterns

The `--pattern` option takes a simple regular expression and reports how many
simulated flops match it. Pass `--pattern` multiple times to require **all** of
the patterns at once: a flop is counted only if it matches **every** pattern
(logical AND). The flop is rendered as a single string with **no spaces** and
cards in **ascending rank order** (e.g. `4H5CAS`), and matching is
**case-insensitive**.

```bash
./flop_sim --hand1 "6s7s" --hand2 "AcQh" --sims 3000 \
    --pattern '.s.*.s' --pattern '4..*5'
```

- `.s.*.s` — flops with **at least two spades**
- `4..*5` — flops containing **both a 4 and a 5**
- Both together — flops with at least two spades **and** both a 4 and a 5

Use `--pattern-or` for OR groups. All `--pattern-or` patterns are OR-combined
(the flop satisfies the group if it matches **any** of them), and that group is
then AND-ed with the `--pattern` group. For example:

```bash
./flop_sim --pattern A --pattern K --pattern-or 's.*s' --pattern-or 'h.*h'
```

matches any flop that has an Ace **and** a King **and** (at least two spades
**or** at least two hearts).

If you only want pattern statistics, you can omit `--hand1`/`--hand2` entirely;
the tool then skips the equity comparison and simply counts how often flops
matching all patterns appear across random flops dealt from the full 52-card
deck:

```bash
./flop_sim --sims 10000 --pattern '.s.*.s' --pattern '4..*5'
```

Because the cards are in numerical order with no spaces, write rank-ordered
patterns (a `4` always appears before a `5`) and use `.` for any single
character and `.*` to skip over cards in between.

## Reading the report

Because both hands always go to showdown (no folding), equity is conserved:
average post-flop equity equals preflop equity, so the realization Δ stays near
zero (any gap is sampling noise). The insight is in the **distribution** — the
histogram shows how often a flop makes a hand a big favorite, a coin flip, or
nearly dead, which is the real "equity realization" story for the matchup.
