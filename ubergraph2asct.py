import argparse
from rdflib import Graph, Literal
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph
import networkx as nx
import csv

def get_all_paths(file):
  g = Graph()
  result = g.parse(file, format='nt')

  G = rdflib_to_networkx_digraph(result)

  G_labels = nx.Graph([(u,v) for u,v in G.edges() if type(v) == Literal])
  G.remove_edges_from(G_labels.edges)

  roots = [ term for term, degree in G.out_degree() if degree == 0 ]
  leaves = [ term for term, degree in G.in_degree() if degree == 0 ]

  all_paths = []
  for leave in leaves:
    for root in roots:
      if nx.has_path(G, leave, root):
        paths = nx.all_simple_paths(G, leave, roots)
        all_paths.extend(paths)

  return all_paths, G_labels.edges()

def to_curie(term):
  return term.replace("http://purl.obolibrary.org/obo/UBERON_", "UBERON:").replace("http://purl.obolibrary.org/obo/CL_", "CL:")

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
    if 'UBERON' in e:
      as_terms.append(e)
    else:
      ct_terms.append(e)
  return len(as_terms), len(ct_terms)

def generate_columns(nb_as_terms, nb_ct_terms):
  header = []
  for i in range(1, nb_as_terms+1):
    header.append(f'AS/{str(i)}')
    header.append(f'AS/{str(i)}/LABEL')
    header.append(f'AS/{str(i)}/ID')

  for i in range(1, nb_ct_terms+1):
    header.append(f'CT/{str(i)}')
    header.append(f'CT/{str(i)}/LABEL')
    header.append(f'CT/{str(i)}/ID')

  return header

def _expand_list(list, size):
  while len(list) < size:
    list.append("")
  return list

def expand_list(list, as_size, ct_size):
  as_terms = []
  ct_terms = []
  
  for e in list:
    if 'UBERON' in e:
      as_terms.append(e)
    else:
      ct_terms.append(e)

  return _expand_list(as_terms, as_size)+_expand_list(ct_terms, ct_size)
  

def search_label(term, labels):
  for k,v in labels:
    if str(k) == term:
      return str(v)

def add_labels(list, labels):
  l = []
  for t in list:
    if t != "":
      l.append(search_label(t, labels))
      l.append(search_label(t, labels))
      l.append(to_curie(t))
    else:
      l.append("")
      l.append("")
      l.append("")
  return l
  
def write_csv(output, data, labels):
  nb_as_terms, nb_ct_terms = find_longest_path(data)
  header = generate_columns(nb_as_terms, nb_ct_terms)

  for i, path in enumerate(data):
    data[i] = add_labels(expand_list(path, nb_as_terms, nb_ct_terms), labels)
    
  with open(output, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)

def main(args):
  paths, labels = get_all_paths(args.input)
  data = transform_paths(paths)
  write_csv(args.output, data, labels)

if __name__ == '__main__':
  parser = argparse.ArgumentParser()
  parser.add_argument('input', help='input triple file')
  parser.add_argument('output', help='output csv file')
  

  args = parser.parse_args()
  main(args)













