import rdflib
from rdflib.extras.external_graph_libs import rdflib_to_networkx_digraph
import networkx as nx
import csv

def get_all_paths(file):
  g = rdflib.Graph()
  result = g.parse(file, format='nt')

  G = rdflib_to_networkx_digraph(result)

  roots = [ term for term, degree in G.out_degree() if degree == 0 ]
  leaves = [ term for term, degree in G.in_degree() if degree == 0 ]

  all_paths = []
  for leave in leaves:
    for root in roots:
      if nx.has_path(G, leave, root):
        paths = nx.all_simple_paths(G, leave, roots)
        all_paths.extend(paths)
  
  return all_paths

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
    #header.append("AS/"+str(i))
    header.append("AS/"+str(i)+"/ID")

  #header.append("CT/"+str(i))
  header.append("CT/"+str(i)+"/ID")

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
  
def write_csv(output, data):
  nb_terms = find_longest_path(data)
  header = generate_columns(nb_terms)

  for path in data:
    path = expand_list(path,nb_terms)
    
  with open(output, 'w', encoding='UTF8', newline='') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    writer.writerows(data)

data = transform_paths(get_all_paths('../ccf-kidney-extended.nt'))
write_csv('../asct.csv', data)











