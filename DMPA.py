import numpy as np
import pandas as pd
from scipy.stats import bernoulli
from scipy.stats import pareto
import networkx as nx
import random
import scipy.io
import collections
import sympy as sym


def theoretical_power(RED, ALPHA, BETA, RHO_B, RHO_R, DELTA):
	# Defining Equations 
	GAMMA = 1 - ALPHA - BETA
	R, alpha, beta, gamma, rho_b, rho_r, delta, theta_i, theta_o = sym.symbols('R alpha beta gamma rho_b rho_r delta theta_i theta_o', nonnegative = True)

	p_1_rr = ( (theta_i + (alpha + beta) * R * delta) * rho_r ) / ( 1 + (alpha + beta) * delta - (1 - theta_i + (alpha + beta) * (1 - R) * delta) * rho_b - (theta_i + (alpha + beta) * R * delta) * (1 - rho_r) )
	p_1_br = ( (theta_i + (alpha + beta) * R * delta) * (1 - rho_r) ) / ( 1 + (alpha + beta) * delta - (1 - theta_i + (alpha + beta) * (1 - R) * delta) * (1 - rho_b) - (theta_i + (alpha + beta) * R * delta) * (rho_r) )
	p_2_rr = ( (theta_o + (alpha + beta) * R * delta) * (rho_r) ) / ( 1 + (alpha + beta) * delta - (1 - theta_o + (alpha + beta) * (1 - R) * delta) * (rho_r) - (theta_o + (alpha + beta) * R * delta) * (1 - rho_r) )
	p_2_br = ( (theta_o + (alpha + beta) * R * delta) * (1 - rho_b) ) / ( 1 + (alpha + beta) * delta - (1 - theta_o + (alpha + beta) * (1 - R) * delta) * (1 - rho_b) - (theta_o + (alpha + beta) * R * delta) * (rho_b) )

	star = (1 + (alpha +beta) * delta)**2 - (1 - theta_o + (alpha + beta) * (1 - R) * delta) * (1 - theta_i + (alpha + beta) * (1 - R) * delta) * (1 - rho_b) - (1 - theta_o + (alpha + beta) * (1 - R) * delta) * (theta_i + (alpha + beta) * R * delta) * (rho_r) - (theta_o + (alpha + beta) * R * delta) * (1 - theta_i + (alpha + beta) * (1 - R) * delta) * (rho_b) - (theta_o + (alpha + beta) * R * delta) * (theta_i + (alpha + beta) * R * delta) * (1 - rho_r)

	p_3_rr = ( (theta_o + (alpha + beta) * R * delta) * (theta_i + (alpha + beta) * R * delta) * rho_r) / (star)
	p_3_br = ( (1 - theta_o + (alpha + beta) * (1 - R) * delta) * (theta_i + (alpha + beta) * R * delta) * (1 - rho_r) ) / (star)
	p_3_rb = ( (theta_o + (alpha + beta) * R * delta) * (1 - theta_i + (alpha + beta) * (1 - R) * delta) * (1 - rho_b) ) / (star)

	F_theta_i = alpha * (R * p_1_rr + (1-R) * p_1_br) + beta * R + gamma * (p_3_rr + p_3_br)
	F_theta_o = alpha * R + beta * ((1-R) * p_2_br + R * p_2_rr)  + gamma * (p_3_rr + p_3_rb)

	F_theta = sym.Matrix([F_theta_i, F_theta_o])
	theta = sym.Matrix([theta_i, theta_o])

	J = F_theta.jacobian(theta)

	# Checking guarantee
	x = [] 
	y = []
	z = []
	for THETA_I in np.arange(0.00,1.05,0.1):
		for THETA_O in np.arange(0.00,1.05,0.1):
			J_norm = float(J.subs([(R, RED), (alpha, ALPHA), (beta, BETA), (gamma, GAMMA), (rho_b, RHO_B), (rho_r, RHO_R), (delta, DELTA), (theta_i, THETA_I), (theta_o, THETA_O)]).norm(2))
			x.append(THETA_I)
			y.append(THETA_O)
			z.append(J_norm)

	guarantee = True
	if max(z) >= 1:
		print ("\tNo theoretical convergence with input parameters (Delta = {0}): max(z) = {1:.2f}".format(DELTA, max(z)))
		guarantee = False
		# return -1 

	print ("\tFitting params with max(z) = {0:.2f}".format(max(z)))
	# Fixed point iteration 
	N = 50; #Number of iterations
	theta_recursive = np.array([1.,0.])

	for i in np.arange(1,N,1):
		tmp  = F_theta.subs({theta_i: theta_recursive[0], 
							 theta_o: theta_recursive[1],
							 R: RED,
							 alpha: ALPHA,
							 beta: BETA, 
							 gamma: GAMMA, 
							 rho_b: RHO_B, 
							 rho_r: RHO_R, 
							 delta: DELTA
							})
		theta_recursive = np.array([tmp[0], tmp[1]])

	I = (theta_recursive[1] * (1-theta_recursive[0]))/(theta_recursive[0] * (1-theta_recursive[1]))

	print ("\tTheoretical Power Inequality = {0:.3f}".format(I))
	print ("")

	return I, guarantee


#The dynamic mixed preferential attachment (DMPA) model (by combining elements from Britton, 2018 and Avin et al., 2020)
def generate_edges(e, r, E1, E2, E3, alpha, beta, delta_in, delta_out):
    """
    DMPA is the biased directed preferential attachment model which combines elements from Britton, 2018 and Avin et al., 2020
    
    e: number of edges 
    
    R: Birth rate of red nodes
    
    m: Number of edges extended by a new node at each time instant
    
    Alpha: probability of event 1 (new node joins and chooses a follower)
    E1: Homophily matrix of the event 1 (element i,j denotes the probability of a link i-->j) - columns add upto 1 indicating that the follower makes the decision. Here, the existing node makes the decision. 
    Delta_in: The probability with which a the follower is chosen is i + Delta_i where i is the in degree of the follower
    Beta: probability of event 2 (new node joins and chooses a friend)
    E2: Homophily matrix of the event 2 (element i,j denotes the probability of a link i-->j) - columns add upto 1 indicating that the follower makes the decision. Here, the new node makes the decision.
    Delta_out: The probability with which a the friend is chosen is j + Delta_out where j is the out degree of the follower
    
    Gamma (not specified): probability (1 - Alpha - Beta) of event 3 (an edge is added between two existing nodes)
    E3: Homophily matrix of the event 3 (element i,j denotes the probability of a link i-->j) - columns add upto 1 indicating that the follower makes the decision. 
    The two ends of the edge are chosen independently with probabilities j + Delta_out (starting point with out-degree j) and i + Delta_i (end point with in-degree i)
    """
    event_list = [1, 2, 3]
    
    num_nodes = 2
    edge_list = [(0, 0), (0, 1), (1, 0), (1, 1)]
    
    color = np.array([0, 1])
    in_degrees = np.array([1, 1])
    out_degrees = np.array([1, 1])
    indeg_sum = np.array([0, 0])
    outdeg_sum = np.array([0, 0])
    
    def add_edge(u, v):
        nonlocal edge_list, out_degrees, in_degrees
        edge_list.append((v, u))
        out_degrees[v] += 1
        outdeg_sum[color[v]] += 1

        in_degrees[u] += 1
        indeg_sum[color[u]] += 1
    
    def get_new_node():
        nonlocal num_nodes, in_degrees, out_degrees, color 
        
        num_nodes = num_nodes + 1
        in_degrees = np.append(in_degrees, 0)
        out_degrees = np.append(out_degrees, 0)
        col = np.random.binomial(1, r)
        color = np.append(color, col)
        
        return num_nodes - 1
    
    for itr in range(e):
        in_deg = in_degrees + delta_in
        in_deg = in_deg / in_deg.sum()
        
        out_deg = out_degrees + delta_out
        out_deg = out_deg / out_deg.sum()
        
        #Choosing the event
        event = random.choices(event_list, weights=(alpha, beta, (1 - alpha - beta)), k=1)[0]
        
        edge_added = False
        
        #Event 1 - Choosing a follower
        if event == 1:
            v = get_new_node()
            
            while edge_added == False:
                u = np.random.choice(range(num_nodes - 1), size=1, replace=True, p=in_deg)[0]
                if bernoulli.rvs(E1[color[v],color[u]]) == 1:
                    add_edge(u, v) # v <- u 
                    edge_added = True
                
        #Event 2 - Choosing a friend
        if event == 2:
            v = get_new_node()

            while edge_added == False:
                u = np.random.choice(range(num_nodes - 1), size=1, replace=True, p=out_deg)[0]
                if bernoulli.rvs(E2[color[u],color[v]]) == 1:
                    add_edge(v, u) # u <- v
                    edge_added = True
                            
        #Event 3 - Adding an edge between two existing nodes
        if event == 3:
            while edge_added == False:
                v = np.random.choice(range(num_nodes), size=1, replace=True, p=in_deg)[0]
                u = np.random.choice(range(num_nodes), size=1, replace=True, p=out_deg)[0]
                if bernoulli.rvs(E3[color[u],color[v]]) == 1:
                    add_edge(v, u) # u <- v
                    edge_added = True
    
    I = (indeg_sum[0] * outdeg_sum[1]) / (indeg_sum[1] * outdeg_sum[0]) # (ro * bi) / (ri * bo)
    return num_nodes, color, edge_list, I


RED = 0.5; ALPHA = 0.03; BETA = 0.032; RHO_B = 0.56; RHO_R = 0.55; DELTA = 100
theoretical_power(RED, ALPHA, BETA, RHO_B, RHO_R, DELTA)

