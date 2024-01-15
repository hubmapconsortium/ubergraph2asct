from rdflib import Graph

from .utils.query_utils import query_seed, query_label


def get_graph(seed_file, property_file) -> Graph:
    g = Graph()
    with open(seed_file, "r", encoding="utf-8") as file:
        seed = file.read().splitlines()

    with open(property_file, "r", encoding="utf-8") as file:
        prop = file.read().splitlines()

    graph_nt = query_seed(seed, prop)
    graph_nt_label = query_label(seed)

    g.parse(data=graph_nt, format="nt")
    g.parse(data=graph_nt_label, format="nt")

    return g
