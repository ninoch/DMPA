import pandas as pd 

class Reader(object):

	def __init__(self, address):
		self.adr = address 

	def read_year(self, year):
		raise NotImplementedError

	def clean_dataframe(self, df):
		raise NotImplementedError


class GenderReader(Reader):
	def __init__(self, address):
		super(GenderReader, self).__init__(address)

		self.known_genders = ['male', 'female', 'mostly_male', 'mostly_female', 'andy'] # female as minority group 
		self.reduce_gender = {
			'male': 'majority',
			'female': 'minority',
			'mostly_female': 'minority',
			'mostly_male': 'majority',
			'andy': 'minority'
		}

	def read_year(self, year):
		raise NotImplementedError

	def clean_dataframe(self, df):
		df = df.loc[df['from_author_gender'].isin(self.known_genders)]
		df = df.loc[df['to_author_gender'].isin(self.known_genders)]

		df = df.replace({"from_author_gender": self.reduce_gender, "to_author_gender": self.reduce_gender})

		df = df.rename(columns={
			'from_author_gender': 'from_author_group',
			'to_author_gender': 'to_author_group'
		})

		return df 


class AffiliationReader(Reader):
	def __init__(self, address, top_rank):
		super(AffiliationReader, self).__init__(address)

		self.top = top_rank 
		self.reduce_rank = dict()
		for ind in range(1, 102):
			if ind <= self.top: # elite authors 
				self.reduce_rank[ind] = 'minority'
			else:
				self.reduce_rank[ind] = 'majority'

	def read_year(self, year):
		raise NotImplementedError

	def clean_dataframe(self, df):
		df = df.replace({"from_author_rank": self.reduce_rank, "to_author_rank": self.reduce_rank})

		df = df.rename(columns={
			'from_author_rank': 'from_author_group',
			'to_author_rank': 'to_author_group'
		})

		return df 

class YearlyGenderReader(GenderReader):
	def __init__(self, address):
		super(YearlyGenderReader, self).__init__(address)

	def read_year(self, year):
		df = pd.read_csv(self.adr.format(year))
		df = self.clean_dataframe(df) 
		return df 

class YearlyAffiliationReader(AffiliationReader):
	def __init__(self, address, top_rank):
		super(YearlyAffiliationReader, self).__init__(address, top_rank)

	def read_year(self, year):
		df = pd.read_csv(self.adr.format(year))
		df = self.clean_dataframe(df) 
		return df 

class BunchGenderReader(GenderReader):
	def __init__(self, address):
		super(BunchGenderReader, self).__init__(address)
		self.df = pd.read_csv(self.adr)
		self.df = self.clean_dataframe(self.df) 

	def read_year(self, year):
		sub_df = self.df.loc[self.df['year'] == year]
		return sub_df

class BunchAffiliationReader(AffiliationReader):
	def __init__(self, address, top_rank):
		super(BunchAffiliationReader, self).__init__(address, top_rank)
		self.df = pd.read_csv(self.adr)
		self.df = self.clean_dataframe(self.df)

	def read_year(self, year):
		sub_df = self.df.loc[self.df['year'] == year]
		return sub_df