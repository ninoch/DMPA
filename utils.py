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

def get_e_matrices(ri, ro, bi, bo, counter):
    
    ri, bi = ri / (ri + bi), bi / (ri + bi)
    ro, bo = ro / (ro + bo), bo / (ro + bo)
    
    x = counter[0][1][0] / (counter[0][1][0] + counter[0][0][1] - counter[0][0][0]) # rr / (rr + br)
    y = counter[0][0][0] / (counter[0][0][0] + counter[0][1][1] - counter[0][1][0]) # bb / (bb + rb)
#     ru_r1 = (x * (bo - y * ro - y * bo)) / (ro * (1 - x - y))
#     ru_b1 = (y * (ro - x * ro - x * bo)) / (bo * (1 - x - y))
    
    ru_r1 = (x * (bo - y)) / (ro * (1 - x - y))
    ru_b1 = (y * (ro - x)) / (bo * (1 - x - y))
    
    # print ("\t Event 1: x = {0:.3f}, y = {1:.3f}, ru_r1 = {2:.3f}, ru_b1 = {3:.3f}, ro = {4:.3f}, bo = {5:.3f}".format(x, y, ru_r1, ru_b1, ro, bo))
    
    
    a = counter[1][1][0] / counter[1][1][1] # rr / r?
    b = counter[1][0][0] / counter[1][0][1] # bb / b? 
    ru_r2 = (a * bi) / (a * bi + (1 - a) * ri) 
    ru_b2 = (b * ri) / (b * ri + (1 - b) * bi)
    # print ("\t Event 2: a = {0:.3f}, b = {1:.3f}, ru_r2 = {2:.3f}, ru_b2 = {3:.3f}, ri = {4:.3f}, bi = {5:.3f}".format(a, b, ru_r2, ru_b2, ri, bi))
    
    
    a_ = counter[2][1][0] / counter[2][1][1] # rr / r?
    b_ = counter[2][0][0] / counter[2][0][1] # bb / b? 
    ru_r3 = (a_ * bi) / (a_ * bi + (1 - a_) * ri) 
    ru_b3 = (b_ * ri) / (b_ * ri + (1 - b_) * bi)
    # print ("\t Event 3: a = {0:.3f}, b = {1:.3f}, ru_r2 = {2:.3f}, ru_b2 = {3:.3f}, ri = {4:.3f}, bi = {5:.3f}, ro = {6:.3f}, bo = {7:.3f}".format(a_, b_, ru_r3, ru_b3, ri, bi, ro, bo))

    
    
    E1 = np.array([[ru_b1, 1 - ru_r1], 
          [1 - ru_b1, ru_r1]])
    E2 = np.array([[ru_b2, 1 - ru_r2], 
          [1 - ru_b2, ru_r2]])
    E3 = np.array([[ru_b3, 1 - ru_r3], 
          [1 - ru_b3, ru_r3]])

    return E1, E2, E3 

