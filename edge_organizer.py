import pickle
import igraph 
import pandas as pd
from tqdm import tqdm
from collections import Counter

from reader import * 
from utils import get_e_matrices, collect_good_edges

def init_params(begin, begin_attr):
    new_nodes = set()
    new_nodes.add(begin)

    red_nodes = set()
    if begin_attr == 'minority':
        red_nodes.add(begin_attr)

    init_params = {
        'cnt': 0,
        'new_nodes': new_nodes,
        'red_nodes': red_nodes,
        'alpha_agg': 0,
        'beta_agg': 0,
        'not_al_be_agg': 0,
        'ri': 0,
        'ro': 0,
        'bi': 0,
        'bo': 0,
        'counter_agg': [[[0, 0], [0, 0]], [[0, 0], [0, 0]], [[0, 0], [0, 0]]]
    }
    return init_params

def get_first_node(reader, from_year):
    tmp = reader.read_year(from_year)
    tuples = list(zip(tmp['from_author'], tmp['to_author']))
    G = igraph.Graph.TupleList(tuples, directed = False)
    begin = G.clusters().giant().vs[0]['name']
    if len(tmp.loc[tmp['from_author'] == begin]) > 0: 
        begin_attr = list(tmp.loc[tmp['from_author'] == begin]['from_author_group'])[0]
    else:
        begin_attr = list(tmp.loc[tmp['to_author'] == begin]['to_author_group'])[0]

    return begin, begin_attr 

def get_year_edges(reader, seed, year):
    df = reader.read_year(year)

    y_nodes, y_node_attr, y_edge_ordering, seed = collect_good_edges(df, year, seed)

    return y_nodes, y_node_attr, y_edge_ordering, seed 


def update_params_year(nodes, node_attr, edge_ordering, params):
    for u, v, year in edge_ordering:
        params['cnt'] += 1
        event_index = None 
        if u in params['new_nodes'] and v in params['new_nodes']: # Event 3
            params['not_al_be_agg'] += 1
            event_index = 3
        elif v in params['new_nodes'] and not u in params['new_nodes']: # Event 2 
            params['beta_agg'] += 1
            event_index = 2
            params['new_nodes'].add(u)
            if node_attr[u] == 'minority':
                params['red_nodes'].add(u)
        elif u in params['new_nodes'] and not v in params['new_nodes']: # Event 1
            params['alpha_agg'] += 1
            event_index = 1
            params['new_nodes'].add(v)
            if node_attr[v] == 'minority':
                params['red_nodes'].add(v)
        else:
            print (">>>>>> Bad Input: {} and {} are both new nodes!".format(u, v))
            break
        
        params['counter_agg'][event_index - 1][int(node_attr[u] != 'majority')][1] += 1
        if node_attr[u] == node_attr[v]:
            params['counter_agg'][event_index - 1][int(node_attr[u] != 'majority')][0] += 1

        # Update ri, ro, bi, bo - Considering flow of information
        if node_attr[v] != 'majority': params['ro'] += 1
        if node_attr[u] != 'majority': params['ri'] += 1
        if node_attr[v] == 'majority': params['bo'] += 1
        if node_attr[u] == 'majority': params['bi'] += 1

    E1, E2, E3 = get_e_matrices(params['ri'], params['ro'], params['bi'], params['bo'], params['counter_agg'])

    year_params = {
        'N': params['cnt'],
        'R': len(params['red_nodes']) / len(params['new_nodes']),
        'alpha': params['alpha_agg'] / params['cnt'],
        'beta': params['beta_agg'] / params['cnt'],
        'E1': E1, 
        'E2': E2,
        'E3': E3
    }
    return year_params, params 

def esimate_params(reader, years, output_yearly, output):
    print ("** Estimating parameters of DMPA model **")
    begin, begin_attr = get_first_node(reader, years[0])

    seed = set([begin])
    params = init_params(begin, begin_attr)
    for year in tqdm(years):
        nodes, node_attr, edge_ordering, seed = get_year_edges(reader, seed, year)
        year_params, params = update_params_year(nodes, node_attr, edge_ordering, params)
        # pickle.dump([year_params, params], open(output_yearly.format(year), "wb"))

    print ("")
    print ("** Estimated parameters: **")
    print ("\t--------------------------------")
    print("\tT = {0}\n\tr = {1:.2f}".format(f"{year_params['N']:,}", year_params['R']))
    print ("\tp = {0:.3f}\n\tq = {1:.3f}".format(year_params['alpha'], year_params['beta']))
    print ("\tE1: ru_b = {0:.2f}, ru_r = {1:.2f}".format(year_params['E1'][0][0], year_params['E1'][1][1]))
    print ("\tE2: ru_b = {0:.2f}, ru_r = {1:.2f}".format(year_params['E2'][0][0], year_params['E2'][1][1]))
    print ("\tE3: ru_b = {0:.2f}, ru_r = {1:.2f}".format(year_params['E3'][0][0], year_params['E3'][1][1]))
    print ("\t--------------------------------")
    print ("")
    pickle.dump([year_params, params], open(output, "wb"))

