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
| `--hand1` / `--hand2` | (required) | The two hands to compare |
| `-n`, `--sims` | `1000` | Number of flops to simulate |
| `--preflop-samples` | `25000` | Monte Carlo samples for preflop equity |
| `--buckets` | `20` | Histogram buckets |
| `--seed` | none | Seed for reproducible runs |
| `--quiet` | off | Suppress the progress indicator |

## Reading the report

Because both hands always go to showdown (no folding), equity is conserved:
average post-flop equity equals preflop equity, so the realization Δ stays near
zero (any gap is sampling noise). The insight is in the **distribution** — the
histogram shows how often a flop makes a hand a big favorite, a coin flip, or
nearly dead, which is the real "equity realization" story for the matchup.
