import sys 
from absl import flags
import pandas as pd 
from reader import * 
from power_inequality import power_inequality
from edge_organizer import esimate_params


flags.DEFINE_string('network_type', 'gender', 'The type of network: gender of affiliation? (defalut gender)')
flags.DEFINE_string('field', 'management', 'The field of study: management, political_science, psychology, economics, aps, cs (default management)')
flags.DEFINE_string('from_year', '1990', 'The year to start the analysis (defalut 1990)')
flags.DEFINE_string('top', '100', 'The cut-off to consider university as elite based on ranking (defalut 100)')
flags.DEFINE_string('delta', '0', 'The preferential attachment parameter')

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
	delta = int(FLAGS.delta)
	print ("** Input **")
	print ("\tNetwork type = {}".format(network_type))
	print ("\tField of study = {}".format(field))
	print ("\tFrom year = {}".format(from_year))
	if network_type == 'affiliation':
		print ("\tElite universities = top-{}".format(top))
	print ("\tDelta = {}".format(delta))
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
		output_str += "_{}".format(top)
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
	yearly_params_adr = "params/yearly/{}".format(output_str) + "_year_{}.pkl"
	params_adr = "params/{}.pkl".format(output_str)
	esimate_params(reader, range(from_year, to_year), delta, yearly_params_adr, params_adr)


