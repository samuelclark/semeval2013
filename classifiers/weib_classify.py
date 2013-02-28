from classify import Classifier
class WeibClassfier(Classifier):
	def __init__(self,**kargs):
		Classifier.__init__(self,tagged_tweets=kargs["tagged_tweets"],instances=kargs["instances"],model=kargs["model"],keys=kargs["keys"])
		self.polarity_dict = kargs["polarity_dict"]
		self.tag_map = kargs["tag_map"]
		self.tagger = lambda tag : self.tag_map[tag] if tag in self.tag_map else "anypos"
		self.id="weib{0}".format(self.num_items)





	def build_feature_vector(self,key):
		# checks for emoticon in tweet -> labels that emoticon:True
		# two ways to do this --> contains any emoticon True/False or specific ones
		# doing binary for now --> THIS SHOULD CHANGE
		# IMPROVMENTS
		# we can create a mapping from many emoticons to 3-4 central ones (as seen in other work)
		features = {}
		tweet = self.tagged_tweets[key]
		for word,tag in tweet:
			each = (word,self.tagger(tag))
			if each in self.polarity_dict:
				features["weib_polarity({0})".format(self.polarity_dict[each].word)] = self.polarity_dict[each].polarity
		return features
