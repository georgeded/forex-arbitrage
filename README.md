# forex-arbitrage

Detects forex arbitrage opportunities using Bellman-Ford negative cycle detection on a live-simulated currency rate graph, then executes simulated trades against a virtual portfolio.

## Install

```bash
pip install -r requirements.txt
```

## Run

```bash
python main.py
```

The Flask API starts automatically on `http://localhost:5000`. The trading loop polls for rates every 10 seconds, detects negative cycles, and updates portfolio balances.
