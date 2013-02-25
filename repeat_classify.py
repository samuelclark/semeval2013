from classify import Classifier
import re
class RepeatClassfier(Classifier):
	def __init__(self,**kargs):
		Classifier.__init__(self,tagged_tweets=kargs["tagged_tweets"],instances=kargs["instances"],merge=kargs["merge"])
		self.prepare_features()



	def check_repeat_letters(self,word):
		word = word.lower()
		if "http" in word or "@" in word:
			return []
		res = re.findall(r'((\w)\2{2,})',word)
		if res:
			new = re.sub(r'([a-z])\1+', r'\1\1', word)
			rep = res[0][0]

			if rep.isdigit():
				return []
			if rep == "www":
				return []
		
			#print word,res
			return new
		return [] 

	def get_repeat_feature(self,key):
		rep_list = []
		tweet = self.tagged_tweets[key]
		for word,pos in tweet:
			repeat = self.check_repeat_letters(word)
			if repeat:
				rep_list.append(repeat)
		return rep_list


	def build_feature_vector(self,key):
		features = {}
		rep_list = self.get_repeat_feature(key)
		if rep_list:
			for repeat in rep_list:
				features["contains({0})".format(repeat)] = True


		return features


