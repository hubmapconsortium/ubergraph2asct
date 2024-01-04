from .utils.query_utils import query_seed


def get_graph(seed_file, property_file):
    with open(seed_file, "r", encoding="utf-8") as file:
        seed = file.read().splitlines()

    with open(property_file, "r", encoding="utf-8") as file:
        prop = file.read().splitlines()

    g = query_seed(seed, prop)

    return g
