from classify import Classifier
class EmoticonClassfier(Classifier):
	def __init__(self,**kargs):
		Classifier.__init__(self,tagged_tweets=kargs["tagged_tweets"],instances=kargs["instances"],model=kargs["model"],keys=kargs["keys"])
		self.emoticons =self.get_all_emoticons()
		self.prepare_features()
		self.id = "emoticon{0}".format(self.num_items)


	def build_feature_vector(self,key):
		# so we want to create a binary mapping here ?
		features = {}

		words = [word for word,tag in self.tagged_tweets[key]]
		for emot in set(self.emoticons.keys()):
			features["emoticon({0})".format(emot)] = (emot in words)
		return features

	def get_all_emoticons(self):
		emoticons = {}
		for key,tweet in self.tagged_tweets.items():
			for word,tag in tweet:
				if tag == "E":
					emoticons[word] = emoticons.get(word,0) +1
		return emoticons




