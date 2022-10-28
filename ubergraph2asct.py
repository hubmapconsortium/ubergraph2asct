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
  for path in all_paths:
    if len(path) > max_len:
      max_len = len(path)

  return max_len

def generate_columns(nb_terms):
  header = []
  for i in range(1, nb_terms):
    header.append("AS/"+str(i))
    header.append("AS/"+str(i)+"/LABEL")
    header.append("AS/"+str(i)+"/ID")

  header.append("CT/1")
  header.append("CT/1/LABEL")
  header.append("CT/1/ID")

  return header

def expand_list(list, size):
  i = len(list) - 1
  while len(list) < size:
    if any('http://purl.obolibrary.org/obo/CL_' in term for term in list):
      list.insert(i, "")
      i += 1
    else:
      list.append("")
  return list

def search_label(term, labels):
  for k,v in labels:
    if str(k) == term:
      return str(v)

def add_labels(list, labels):
  l = []
  for t in list:
    if t != "":
      l.append(search_label(t, labels))
      l.append("")
      l.append(to_curie(t))
    else:
      l.append("")
      l.append("")
      l.append("")
  return l
  
def write_csv(output, data, labels):
  nb_terms = find_longest_path(data)
  header = generate_columns(nb_terms)

  for i, path in enumerate(data):
    data[i] = add_labels(expand_list(path, nb_terms), labels)
    
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













