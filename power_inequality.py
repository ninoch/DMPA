import pickle
from tqdm import tqdm
import pandas as pd
from collections import Counter
from reader import * 

def power_inequality(reader, years, file_name): 
	homophily = dict()
	freq = dict()
	all_groups = dict()
	num_edges = 0 
	print ("** Calculating power-inequality over years {}-{} **".format(years[0], years[-1]))
	for year in tqdm(years):
		groups = dict()
		res = pd.DataFrame(columns=['from_author_group', 'to_author_group', 'times'])

		df = reader.read_year(year)

		res = res.append(df.groupby(['from_author_group', 'to_author_group'], as_index=False).agg('sum')[['from_author_group', 'to_author_group', 'times']])

		groups = dict(zip(df['from_author'], df['from_author_group']))
		groups.update(dict(zip(df['to_author'], df['to_author_group'])))

		num_edges += sum(df['times'])
		all_groups.update(dict(zip(df['from_author'], df['from_author_group'])))
		all_groups.update(dict(zip(df['to_author'], df['to_author_group'])))

		homophily[year] = res.groupby(['from_author_group', 'to_author_group']).agg('sum').to_dict()
		freq[year] = dict(Counter(groups.values()))

	print ("")
	print ("** Network Info **")
	print ("\tNumber of nodes = " + f"{len(all_groups):,}")
	print ("\tNumber of edges = " + f"{num_edges:,}")
	print ("\tEdge density = {}".format(num_edges / (len(all_groups) * (len(all_groups) - 1))))
	print ("\tMinority = {0:.2f} %".format(100.0 * (dict(Counter(all_groups.values()))['minority'] / len(all_groups))))
	print ("")

	pickle.dump([homophily, freq, all_groups, num_edges], open(file_name, "wb"))
