"""
Script to transform list of axioms from Ubergraph into ASCT table
"""

import csv
from pathlib import Path

import curies
import networkx as nx
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph
from rdflib.term import Literal
from .query import get_graph


def get_all_paths(graph):
    net = rdflib_to_networkx_digraph(graph)
    net = nx.transitive_reduction(net)
    net_labels = nx.Graph([(u, v) for u, v in net.edges() if isinstance(v, Literal)])

    roots = [term for term, degree in net.out_degree() if degree == 1]
    leaves = [
        term
        for term, degree in net.in_degree()
        if degree == 0 and not isinstance(term, Literal)
    ]

    as_paths = []
    ct_paths = []
    for leave in leaves:
        for root in roots:
            if nx.has_path(net, leave, root):
                paths = nx.all_simple_paths(net, leave, root)
                if "UBERON" in str(root):
                    as_paths.extend(paths)
                else:
                    ct_paths.extend(paths)

    return as_paths, ct_paths, net_labels.edges()


def transform_paths(all_paths):
    all_paths_str = []

    for path in all_paths:
        path_r = [str(term) for term in reversed(path)]
        all_paths_str.append(path_r)

    return all_paths_str


def find_longest_path(paths, term_type):
    max_len = 0
    len_type = []

    # Get max len depending on term_type for each path
    for path in paths:
        len_type.append(len([e for e in path if term_type in str(e)]))

    # Get max found in paths
    if len_type:
        max_len = max(len_type)

    return max_len


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


def write_csv(output, data, labels, nb_as_terms, nb_ct_terms):
    header = generate_columns(nb_as_terms, nb_ct_terms)
    for i, path in enumerate(data):
        data[i] = add_labels(expand_list(path, nb_as_terms, nb_ct_terms), labels)

    with open(output, "w", encoding="UTF8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(data)


def transform(seed_file: Path, property_file: Path, output_file: Path):
    input_graph = get_graph(seed_file, property_file)
    as_paths, ct_paths, labels = get_all_paths(input_graph)
    nb_as_terms = find_longest_path(as_paths, "UBERON")
    nb_ct_terms = find_longest_path(ct_paths, "CL")
    data = transform_paths(as_paths) + transform_paths(ct_paths)

    write_csv(output_file, data, labels, nb_as_terms, nb_ct_terms)
