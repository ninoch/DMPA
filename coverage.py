import sys 
import pickle 
import pandas as pd
import numpy as np
from collections import Counter
import matplotlib.pyplot as plt 
import seaborn as sns
import glob 
import json
import ast

fields = ['management', 'psychology', 'political_science', 'economics', 'cs', 'aps']
cp = sns.color_palette("Set1")
field_color = {
    'economics': cp[0],
    'management': cp[1],
    'psychology': cp[7],
    'aps': cp[3],
    'political_science': cp[2],
    'cs': cp[4]
}
field_label = {
    'economics': 'Economics',
    'management': 'Management',
    'psychology': 'Psychology',
    'aps': 'Physics (APS)',
    'political_science': 'Political Science',
    'cs': 'Computer Science'
}
field_marker = {
    'economics': 'o',
    'management': 's',
    'psychology': '^',
    'aps': '>',
    'political_science': 'd',
    'cs': '<'
    
}

# for field in ['aps']:
#     print (field) 
#     known = [] 
#     if field == 'aps':
#         aff_year = pickle.load(open("params/aps_affs.pkl", "rb"))
#         years = range(1990, max(aff_year.keys()) + 1)
#         for y in years: 
#             print ("\t{}".format(y))

#             cnt = Counter(aff_year[y].values()) 
#             known.append(1.0 - (float(cnt['unknown']) / len(aff_year[y])))

#         pickle.dump([years, known], open("params/coverage_aff_{}.pkl".format(field), "wb"))

#     else:
#         df = pd.read_csv("/Users/nalipour/Desktop/Data/MACROSCORE/MAG/merged dataframes/{}.csv".format(field))
#         years = range(1990, max(df['Y']) + 1)

#         for year in years:
#             print ("\t{}".format(year))
#             year_df = df.loc[df['Y'] == year]
#             aa = year_df.sort_values('Y')['AA'].dropna()

#             id_to_aff = dict()
#             for rec in aa:
#                 tmp = ast.literal_eval(rec)
#                 for el in tmp:
#                     if 'AfId' in el and el['AfId'] != None: 
#                         id_to_aff[el['AuId']] = 'known'
#                     else:
#                         id_to_aff[el['AuId']] = 'unknown'

#             cnt = Counter(id_to_aff.values()) 
#             known.append(1.0 - (float(cnt['unknown'] / len(id_to_aff))))

#         pickle.dump([years, known], open("params/coverage_aff_{}.pkl".format(field), "wb"))

#     plt.plot(years, known, label=field_label[field], color = field_color[field], marker = field_marker[field])

# years = range(1990, 2021)
# plt.xticks(years, years, rotation=90, fontsize=20)
# ytck = np.arange(0.90, 1.01, 0.02)
# plt.yticks(ytck, ["{0:.2f}".format(y) for y in ytck], fontsize=20)
# plt.savefig("figures/coverage_aff.pdf", bbox_inches='tight')
# plt.show()




# dir_name = "/Users/nazaninalipourfard/Desktop/Graph Embedding/APS data/{}"
# file_li = glob.glob(dir_name.format("aps-dataset-metadata-2018/*/*/*.json"))
# aut_aff = dict() 

# for ind, file_name in enumerate(file_li):
#     print ("{0:.0f}K outof {1:.0f}K".format(ind / 1000, len(file_li) / 1000))
#     dct = json.load(open(file_name, "r"))
#     pap_affs = dict()
#     if 'affiliations' in dct:
#         for a in dct['affiliations']:
#             pap_affs[a['id']] = a['name']
#     year = int(dct['date'][:4])
#     if year not in aut_aff:
#         aut_aff[year] = dict() 
#     if 'authors' in dct:
#         for a in dct['authors']:
#             try:
#                 first_name_norm = a['firstname'].lower().replace('\u2009', ' ')
#                 first_name_norm = first_name_norm.replace('-', '')
#                 first_name_norm = [x for x in first_name_norm.split(' ') if len(x) > 1 and x[-1] != '.'][0]
#                 # print ("\t", a['firstname'], "->", first_name_norm)
#                 # if first_name_norm in name_gender:
#                 #     print ("\t\t", name_gender[first_name_norm])
#                 a_id = "{}_{}".format(first_name_norm, a['surname']).lower()
#                 if not a_id in aut_aff[year]:
#                     if 'affiliationIds' in a and a['affiliationIds'][0] in pap_affs:
#                         aut_aff[year][a_id] = 'known'
#                     else:
#                         aut_aff[year][a_id] = 'unknown'
#             except:
#                 print ("BAD!")
#                 continue 

# pickle.dump(aut_aff, open("params/aps_affs.pkl", "wb"))
# import IPython; IPython.embed()
#############
#   GENDER  #
#############

# name_gender_df = pd.read_csv("clean_name_gender.csv") 
# name_gender = dict(zip(name_gender_df['name'], name_gender_df['gender']))

for field in ['cs']:
    print (field)
    known = []

    if field == 'aps':
        gen_year = pickle.load(open("params/aps_gender.pkl", "rb"))
        years = range(1990, max(gen_year.keys()) + 1)
        for y in years: 
            print ("\t{}".format(y))

            cnt = Counter(gen_year[y].values()) 
            known.append(1.0 - (float(cnt['unknown']) / len(gen_year[y])))

        pickle.dump([years, known], open("params/coverage_{}.pkl".format(field), "wb"))

    else:

        if field != 'cs':
            df = pd.read_csv("/Users/nalipour/Desktop/Data/Fairness/fields gender/{}_author_citation_gender.csv".format(field))
            years = range(1990, max(df['year']) + 1)
        else:
            years = range(1990, 2019)
        for y in years:
            print ("\t{}".format(y))
            if field != 'cs':
                year_df = df.loc[df['year'] == y]
            else:
                year_df = pd.read_csv("/Users/nalipour/Desktop/Data/Fairness/fields gender/cs_author_citations_{}_gender.csv".format(y))
            gen = dict(zip(year_df['from_author'], year_df['from_author_gender']))
            gen.update(dict(zip(year_df['to_author'], year_df['to_author_gender'])))

            cnt = Counter(gen.values()) 
            known.append(1.0 - (float(cnt['unknown'] + cnt['not_in_db']) / len(gen)))

            import IPython; IPython.embed()

        pickle.dump([years, known], open("params/coverage_{}.pkl".format(field), "wb"))

    
    plt.plot(years, known, label = field_label[field], color = field_color[field], marker = field_marker[field])


# years = range(1990, 2020)
# plt.xticks(years, years, rotation=90, fontsize=20)
# ytck = np.arange(0.90, 1.01, 0.02)
# plt.yticks(ytck, ["{0:.2f}".format(y) for y in ytck], fontsize=20)
# plt.savefig("figures/coverage.pdf", bbox_inches='tight')
# plt.show()

# dir_name = "/Users/nazaninalipourfard/Desktop/Graph Embedding/APS data/{}"

# ### Getting Gender Affiliation ### 
# gen_year = dict() 
# file_li = glob.glob(dir_name.format("aps-dataset-metadata-2018/*/*/*.json"))

# bad_cnt = 0 
# # gender_not_found = []
# for ind, file_name in enumerate(file_li):
#     print ("{0:.0f}K outof {1:.0f}K".format(ind / 1000, len(file_li) / 1000))
#     dct = json.load(open(file_name, "r"))
#     year = int(dct['date'][:4])

#     if not year in gen_year:
#         gen_year[year] = dict()  

#     if 'authors' in dct:
#         for a in dct['authors']:
#             try:
#                 first_name_norm = a['firstname'].lower().replace('\u2009', ' ')
#                 first_name_norm = first_name_norm.replace('-', '')
#                 first_name_norm = [x for x in first_name_norm.split(' ') if len(x) > 1 and x[-1] != '.'][0]

#                 a_id = "{}_{}".format(first_name_norm, a['surname']).lower()
#                 if (not a_id in gen_year[year]) or (not a_id in aut_aff):
#                     if first_name_norm in name_gender and name_gender[first_name_norm] != 'unknown':
#                         gen_year[year][a_id] = name_gender[first_name_norm]
#                     else:
#                         gen_year[year][a_id] = 'unknown'
#             except:    
#                 bad_cnt += 1 
#                 print ("bad count = {}".format(bad_cnt))
#                 continue


# pickle.dump(gen_year, open("params/aps_gender.pkl", "wb"))
# import IPython; IPython.embed()
