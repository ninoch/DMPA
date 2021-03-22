import random
import numpy as np
import pandas as pd
from scipy.stats import bernoulli

def collect_good_edges(edges, year, seed):
    year_df = edges.reindex(edges.index.repeat(edges.times)).reset_index() # for considering multi-edges 
    edge_added = True
    edge_ordering = []
    while edge_added:
        edge_added = False
        # print ("\t{}".format(len(seed)))
        ind = year_df.loc[year_df['from_author'].isin(seed) | year_df['to_author'].isin(seed)].index
        es = year_df.loc[ind]
        seed.update(es['from_author'])
        seed.update(es['to_author'])
        e = list(zip(es['from_author'], es['to_author'], [year] * len(es)))
        if len(e) > 0:
            edge_added = True
        np.random.shuffle(e)
        edge_ordering.extend(e)
        year_df = year_df.drop(ind)

    nodes = set()
    nodes = set([e[0] for e in edge_ordering]).union(set([e[1] for e in edge_ordering]))

    g = dict(zip(edges['from_author'], edges['from_author_group']))
    g.update(dict(zip(edges['to_author'], edges['to_author_group'])))

    node_attr = dict()
    for n in nodes:
        node_attr[n] = g[n] 

    return nodes, node_attr, edge_ordering, seed 

def get_e3_matrix(ri, ro, bi, bo, counter, r, p, q, delta):
    
    ri, bi = ri / (ri + bi), bi / (ri + bi)
    ro, bo = ro / (ro + bo), bo / (ro + bo)
    
    x = counter[2][1][0] / counter[2][1][1] # rr / ?r - red follower 
    y = counter[2][0][0] / counter[2][0][1] # bb / ?b - blue follower 

    a = (ro + (p + q) * r * delta) * (ri + (p + q) * r * delta)
    b = (bo + (p + q) * (1 - r) * delta) * (ri + (p + q) * r * delta)
    ru_r3 = (b * x) / (a - a * x + b * x)

    a = (bo + (p + q) * (1 - r) * delta) * (bi + (p + q) * (1 - r) * delta)
    b = (ro + (p + q) * r * delta) * (bi + (p + q) * (1 - r) * delta)
    ru_b3 = (b * y) / (a - a * y + b * y)

    E3 = np.array([[ru_b3, 1 - ru_r3], 
          [1 - ru_b3, ru_r3]])

    return E3 

