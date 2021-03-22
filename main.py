import sys 
from absl import flags
import pandas as pd 
import numpy as np
from tqdm import tqdm
from reader import * 
from DMPA import theoretical_power
from power_inequality import power_inequality
from edge_organizer import esimate_params


flags.DEFINE_string('network_type', 'gender', 'The type of network: gender of affiliation? (defalut gender)')
flags.DEFINE_string('field', 'management', 'The field of study: management, political_science, psychology, economics, aps, cs (default management)')
flags.DEFINE_string('from_year', '1990', 'The year to start the analysis (defalut 1990)')
flags.DEFINE_string('top', '100', 'The cut-off to consider university as elite based on ranking (defalut 100)')

FLAGS = flags.FLAGS
FLAGS(sys.argv)


if __name__ == '__main__':
	##########################
	#        Input           #
	##########################
	network_type = FLAGS.network_type
	field = FLAGS.field 
	from_year = int(FLAGS.from_year)
	top = int(FLAGS.top)
	print ("** Input **")
	print ("\tNetwork type = {}".format(network_type))
	print ("\tField of study = {}".format(field))
	print ("\tFrom year = {}".format(from_year))
	if network_type == 'affiliation':
		print ("\tElite universities = top-{}".format(top))
	print ("")

	##########################
	#        Reader          #
	##########################
	print ("** Preparing data reader **")
	reader = None 
	output_str = "{}_{}_{}".format(network_type, field, from_year)
	if network_type == 'gender':
		if field != 'cs':
			reader = BunchGenderReader("data/{}_author_citation_gender.csv".format(field))
		elif field == 'cs':
			reader = YearlyGenderReader("data/cs_gender/cs_author_citations_{}_gender.csv")
	elif network_type == 'affiliation':
		output_str += "_t{}".format(top)
		if field != 'cs':
			reader = BunchAffiliationReader("data/{}_author_citation_ranking.csv".format(field), top)
		elif field == 'cs':
			reader = YearlyAffiliationReader("data/cs_affiliation/cs_author_citations_{}_ranking.csv", top)

	if reader == None:
		print ("-- Bad input --")
		exit()

	print ("\tReading data from: {}".format(reader.adr))
	print ("\tOutput string: {}".format(output_str))
	print ("")

	if field in ['cs', 'aps']:
		to_year = 2019
	else:
		to_year = 2020 
	##########################
	#     Power-inequality   #
	##########################
	power_adr = "power/{}.pkl".format(output_str)
	power_inequality(reader, range(from_year, to_year), power_adr)

	##########################
	#      Organize Edges    #
	##########################
	best_theo_power = float('inf')
	best_delta = None 
	best_ind = None 
	best_params = None 
	large_range = [1, 2, 3, 4, 5, 6, 10, 20, 50, 100, 1000]

	for ind, delta in enumerate(large_range): 
		print ("--------------------------------------------")
		print ("\t\t Delta = {} ".format(delta))
		print ("--------------------------------------------")
		output_str_d = "d{}".format(delta) + "_" + output_str
		yearly_params_adr = "params/yearly/{}".format(output_str_d) + ".pkl"
		params_adr = "params/{}.pkl".format(output_str_d)
		params = esimate_params(reader, range(from_year, to_year), delta, yearly_params_adr, params_adr)

		actual_power = params['power_inequality']

		theo_power, guarantee = theoretical_power(params['R'], params['alpha'], params['beta'], params['E3'][0][0], params['E3'][1][1], delta)

		if guarantee == True and (abs(actual_power - theo_power) < abs(actual_power - best_theo_power)):
			best_theo_power = theo_power
			best_params = params.copy()
			best_delta = delta 
			best_ind = ind 

	print ("==============================================")
	print ("\tDelta = {0} (diff = {1:.3f})".format(best_delta, actual_power - best_theo_power))
	print ("\tT = {0}".format(f"{best_params['N']:,}"))
	print ("\tr = {0:.2f}".format(best_params['R']))
	print ("\tp = {0:.3f}".format(best_params['alpha']))
	print ("\tq = {0:.3f}".format(best_params['beta']))
	print ("\tE: ru_r = {0:.2f}, ru_b = {1:.2f}".format(best_params['E3'][1][1], best_params['E3'][0][0]))
	print ("\tActual Power = {0:.3f}".format(best_params['power_inequality']))
	print ("\tTheoretical Power = {0:.3f}".format(best_theo_power))
	print ("==============================================")