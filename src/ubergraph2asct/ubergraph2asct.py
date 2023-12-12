"""
Script to transform list of axioms from Ubergraph into ASCT table
"""

import csv
from pathlib import Path

import curies
import networkx as nx
from rdflib import Graph, Literal
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph


def get_all_paths(file):
    g = Graph()
    result = g.parse(file, format="nt")

    net = rdflib_to_networkx_digraph(result)

    net_labels = nx.Graph([(u, v) for u, v in net.edges() if isinstance(v, Literal)])
    net.remove_edges_from(net_labels.edges)

    roots = [term for term, degree in net.out_degree() if degree == 0]
    leaves = [term for term, degree in net.in_degree() if degree == 0]

    all_paths = []
    for leave in leaves:
        for root in roots:
            if nx.has_path(net, leave, root):
                paths = nx.all_simple_paths(net, leave, roots)
                all_paths.extend(paths)

    return all_paths, net_labels.edges()


def transform_paths(all_paths):
    all_paths_str = []

    for path in all_paths:
        path_r = [str(term) for term in reversed(path)]
        all_paths_str.append(path_r)

    return all_paths_str


def find_longest_path(all_paths):
    max_len = 0
    max_path = None
    as_terms = []
    ct_terms = []
    for path in all_paths:
        if len(path) > max_len:
            max_len = len(path)
            max_path = path

    for e in max_path:
        if "UBERON" in e:
            as_terms.append(e)
        else:
            ct_terms.append(e)
    return len(as_terms), len(ct_terms)


def generate_columns(nb_as_terms: int, nb_ct_terms: int):
    header = []
    for i in range(1, nb_as_terms + 1):
        header.append(f"AS/{str(i)}")
        header.append(f"AS/{str(i)}/LABEL")
        header.append(f"AS/{str(i)}/ID")

    for i in range(1, nb_ct_terms + 1):
        header.append(f"CT/{str(i)}")
        header.append(f"CT/{str(i)}/LABEL")
        header.append(f"CT/{str(i)}/ID")

    return header


def _expand_list(entry: list, size):
    while len(entry) < size:
        entry.append("")
    return entry


def expand_list(entry: list, as_size: int, ct_size: int):
    as_terms = []
    ct_terms = []

    for e in entry:
        if "UBERON" in e:
            as_terms.append(e)
        else:
            ct_terms.append(e)

    return _expand_list(as_terms, as_size) + _expand_list(ct_terms, ct_size)


def search_label(term, labels):
    for k, v in labels:
        if str(k) == term:
            return str(v)


def add_labels(entry: list, labels: list):
    row = []
    curie_converter = curies.get_obo_converter()
    for t in entry:
        if t != "":
            row.append(search_label(t, labels))
            row.append(search_label(t, labels))
            row.append(curie_converter.compress(t))
        else:
            row.append("")
            row.append("")
            row.append("")
    return row


def write_csv(output, data, labels):
    nb_as_terms, nb_ct_terms = find_longest_path(data)
    header = generate_columns(nb_as_terms, nb_ct_terms)

    for i, path in enumerate(data):
        data[i] = add_labels(expand_list(path, nb_as_terms, nb_ct_terms), labels)

    with open(output, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


def transform(input_file: Path, output_file: Path):
    paths, labels = get_all_paths(input_file)
    data = transform_paths(paths)
    write_csv(output_file, data, labels)
