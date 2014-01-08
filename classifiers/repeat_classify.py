from classify import Classifier
import re
class RepeatClassifier(Classifier):
	def __init__(self,**kargs):
		Classifier.__init__(self,tweets=kargs["tweets"],instances=kargs["instances"],model=kargs["model"],keys=kargs["keys"],selection=kargs["selection"])
		self.mode = "ngram"
		self.include_word = True
		self.inclued_pos = True
		self.id="repeat{0},s:{1}".format(self.num_items,self.selection)

		self.repeat_dict = self.get_all_repeats()
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

	def get_all_repeats(self):
		repeat_dict = {}
		for key,tweet in self.tweets.items():
			word_list = tweet.tagged_text
			for word,pos in word_list:
				repeat = self.check_repeat_letters(word)
				if repeat:
					repeat_dict[repeat] = repeat_dict.get(repeat,0) + 1
		return repeat_dict

	def build_feature_vector(self,key):
		features = {}
		words = [word for word,tag in self.get_selected_text(self.tweets[key])]
		for repeat in set(self.repeat_dict.keys()):
			features["repeat--{0}({1})".format(self.selection,repeat)] = (repeat in words)

		return features


