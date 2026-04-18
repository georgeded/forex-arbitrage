import math
import requests
import networkx as nx

from config import API_URL
from core.graph import build_graph_from_rates

_last_fetched_data: dict | None = None


def fetch_forex_rates(api_url: str = API_URL) -> tuple[dict[str, float], list[str]]:
    global _last_fetched_data
    response = requests.get(api_url)
    if response.status_code != 200:
        raise Exception(f"Failed to fetch rates. HTTP Status Code: {response.status_code}")
    data = response.json()
    if data == _last_fetched_data:
        return _last_fetched_data["rates"], _last_fetched_data["currencies"]
    _last_fetched_data = data
    return data["rates"], data["currencies"]


def _normalize_cycle(cycle: list[str]) -> tuple[str, ...]:
    nodes = cycle[:-1]
    min_idx = nodes.index(min(nodes))
    rotated = nodes[min_idx:] + nodes[:min_idx]
    rotated.append(rotated[0])
    return tuple(rotated)


def bellman_ford_all_cycles(
    G: nx.DiGraph,
) -> tuple[list[list[str]], float | None, list[tuple[list[str], float]]]:
    nodes = list(G.nodes())
    all_cycles: list[tuple[list[str], float]] = []
    seen_normalized: set[tuple[str, ...]] = set()
    most_negative_cycles: list[list[str]] = []
    most_negative_value = float("inf")

    for source in nodes:
        dist = {node: float("inf") for node in nodes}
        pred: dict[str, str | None] = {node: None for node in nodes}
        dist[source] = 0

        for _ in range(len(nodes) - 1):
            for u, v, data in G.edges(data=True):
                if dist[u] + data["weight"] < dist[v]:
                    dist[v] = dist[u] + data["weight"]
                    pred[v] = u

        for u, v, data in G.edges(data=True):
            if dist[u] + data["weight"] < dist[v]:
                cycle: list[str] = []
                visited: set[str] = set()
                x = v

                while x not in visited:
                    visited.add(x)
                    cycle.append(x)
                    x = pred[x]  # type: ignore[assignment]

                cycle.append(x)
                cycle = cycle[cycle.index(x):]

                try:
                    cycle_weight = sum(
                        G[cycle[i]][cycle[i + 1]]["weight"] for i in range(len(cycle) - 1)
                    )
                except KeyError:
                    cycle.reverse()
                    try:
                        cycle_weight = sum(
                            G[cycle[i]][cycle[i + 1]]["weight"] for i in range(len(cycle) - 1)
                        )
                    except KeyError:
                        continue

                normalized = _normalize_cycle(cycle)
                if normalized in seen_normalized:
                    continue
                seen_normalized.add(normalized)
                all_cycles.append((cycle, cycle_weight))

                if cycle_weight < most_negative_value:
                    most_negative_cycles = [cycle]
                    most_negative_value = cycle_weight
                elif cycle_weight == most_negative_value:
                    most_negative_cycles.append(cycle)

    profit = math.exp(-most_negative_value) if most_negative_cycles else None
    return most_negative_cycles, profit, all_cycles


def detect_arbitrage_opportunities(api_url: str = API_URL) -> dict[tuple[str, ...], dict]:
    try:
        rates, _ = fetch_forex_rates(api_url)
        G = build_graph_from_rates(rates)
        most_negative_cycles, _, _ = bellman_ford_all_cycles(G)

        result: dict[tuple[str, ...], dict] = {}
        for cycle in most_negative_cycles:
            cycle_weight = sum(
                G[cycle[i]][cycle[i + 1]]["weight"] for i in range(len(cycle) - 1)
            )
            cycle_profitability = math.exp(-cycle_weight)
            percentage_profit = (cycle_profitability - 1) * 100
            result[tuple(cycle)] = {
                "percentage_profit": percentage_profit,
                "total_weight": cycle_weight,
            }
        return result
    except Exception as e:
        import logging
        logging.getLogger(__name__).error("Error fetching or processing rates: %s", e)
        return {}
