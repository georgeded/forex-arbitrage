import math
import networkx as nx


def build_graph_from_rates(rates: dict[str, float]) -> nx.DiGraph:
    G = nx.DiGraph()
    for pair, rate in rates.items():
        base, quote = pair.split("/")
        G.add_edge(base, quote, weight=-math.log(rate))
    return G
