"""
Script to transform list of axioms from Ubergraph into ASCT table
"""

import csv
from pathlib import Path

import curies
import networkx as nx
from rdflib import Graph
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph
from rdflib.term import Literal


def get_all_paths(file):
    g = Graph()
    result = g.parse(file, format="nt")

    net = rdflib_to_networkx_digraph(result)

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


def find_longest_path(all_paths):
    max_len = 0
    max_path = []
    len_as = []
    len_ct = []
    max_len_as = 0
    max_len_ct = 0

    # Find size of longest path
    for path in all_paths:
        if len(path) > max_len:
            max_len = len(path)

    # Get all paths with longest size
    for path in all_paths:
        if len(path) == max_len:
            max_path.append(path)

    # Split AS and CT paths
    for path in max_path:
        len_as.append(len([e for e in path if "UBERON" in str(e)]))
        len_ct.append(len([e for e in path if "CL" in str(e)]))

    # Last check if AS and CT were found in the paths
    # Get max AS found in paths
    if len_as:
        max_len_as = max(len_as)

    # Get max CT found in paths
    if len_ct:
        max_len_ct = max(len_ct)

    return max_len_as, max_len_ct


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


def transform(input_file: Path, output_file: Path):
    as_paths, ct_paths, labels = get_all_paths(input_file)
    as_path_nb_as_terms, as_path_nb_ct_terms = find_longest_path(as_paths)
    _, ct_path_nb_ct_terms = find_longest_path(ct_paths)
    nb_as_terms = as_path_nb_as_terms
    nb_ct_terms = max(as_path_nb_ct_terms, ct_path_nb_ct_terms)
    data = transform_paths(as_paths) + transform_paths(ct_paths)

    write_csv(output_file, data, labels, nb_as_terms, nb_ct_terms)
