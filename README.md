# forex-arbitrage

A real-time forex arbitrage detector that models currency exchange rates as a directed weighted graph, applies Bellman-Ford negative-cycle detection to find profitable trade cycles, and executes those trades against a simulated portfolio.

---

## How it works

### Graph representation

Each currency (USD, EUR, GBP, …) is a node. Each exchange rate `r` for the pair `A/B` becomes a directed edge `A → B` with weight `-log(r)`. Taking the negative logarithm turns the multiplicative chain of exchange rates into an additive sum of edge weights — a standard trick that lets Bellman-Ford operate on what is otherwise a product.

### Bellman-Ford negative-cycle detection

A currency cycle is profitable if and only if the product of its exchange rates is greater than 1, which is equivalent to the sum of `-log(rate)` along the cycle being **negative**.

Bellman-Ford runs from every source node and relaxes all edges `|V| - 1` times. A final relaxation pass that still finds an improvement indicates a negative-weight cycle — i.e. an arbitrage opportunity. The detector:

1. Collects all unique negative cycles across every source.
2. Tracks the most-negative cycle (highest profit factor).
3. Converts the total negative weight back to a profit multiplier via `exp(-weight)`.

### Simulated trading

Once cycles are ranked, the trader picks the cycle whose starting currency has the highest current balance (maximising absolute gain), then applies the percentage profit to every currency in that cycle.

---

## Architecture

```
forex-arbitrage/
├── api/
│   └── app.py          # Flask server — generates randomised live-ish rates for 25 pairs, refreshed every 5 s
├── core/
│   ├── graph.py        # Builds a NetworkX DiGraph from the rate dict; applies -log(rate) weighting
│   └── detector.py     # Fetches rates, runs Bellman-Ford from every node, deduplicates and ranks cycles
├── portfolio/
│   └── trader.py       # In-memory portfolio (16 currencies, starting balance 1.0 each); executes the best cycle
├── config.py           # API_URL, POLL_INTERVAL (10 s), STARTING_BALANCE
├── main.py             # Entry point: starts API in a daemon thread, then polls in a loop
└── requirements.txt
```

| Layer | Responsibility |
|---|---|
| `api/` | Simulated exchange — provides the `/api/rates` endpoint consumed by the detector |
| `core/` | Graph construction and Bellman-Ford algorithm |
| `portfolio/` | Portfolio state and trade execution logic |

---

## Setup

```bash
python -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

---

## Run

```bash
python main.py
```

`main.py` spins up the Flask rate server on `http://localhost:5000` in a background thread, waits 2 seconds for it to be ready, then enters a polling loop that runs every 10 seconds.

---

## Example output

```
2026-04-19 12:00:02 [INFO] __main__: Forex API started on http://localhost:5000
2026-04-19 12:00:04 [INFO] __main__: Fetching new Forex rates...
2026-04-19 12:00:04 [INFO] portfolio.trader: Full cycle trade execution | profit: 3.47% | weight: -0.0342 | cycle: USD->EUR->GBP->USD
2026-04-19 12:00:04 [INFO] portfolio.trader: Portfolio: USD: 1.0347 | EUR: 1.0347 | GBP: 1.0347 | JPY: 1.0000 | ...
2026-04-19 12:00:14 [INFO] __main__: Fetching new Forex rates...
2026-04-19 12:00:14 [INFO] portfolio.trader: No arbitrage cycle detected.
```

Each log line shows the timestamp, log level, module, and either a successful trade with the cycle path and profit percentage, or a message indicating no opportunity was found in that polling window.
