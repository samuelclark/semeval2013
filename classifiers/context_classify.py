from classify import Classifier,nltk

class ContextClassifier(Classifier):
	def __init__(self, **kargs):
		Classifier.__init__(self,tagged_tweets=kargs["tagged_tweets"],instances=kargs["instances"],model=kargs["model"],keys=kargs["keys"])
		self.mode = kargs["mode"]
		self.inclued_pos = kargs["pos"]
		self.include_word = kargs["word"]
		self.mode= kargs["mode"]
		self.id="context{0},m:{1},w:{2},t:{3}".format(self.num_items,self.mode,self.include_word,self.inclued_pos)
		self.debug=False
		self.ranked_ngrams = kargs["ranked_ngrams"]
		self.num_ngrams = len(self.ranked_ngrams)
		self.context_dict = self.build_ct_dict() 
		self.prepare_features()





	def build_feature_vector(self,key):

		context_features = self.context_features(key)
		return context_features


	# CONTEXT STUFF
	def build_ct_dict(self):
		# builds a context target dict
		# see analyze tweets original for details
		results = {}
		for key,tweet in self.tagged_tweets.items():
		 	start = self.instances[key].startpos
		 	end = self.instances[key].endpos
		 	if end < len(tweet):

			 	if start == end:
			 		target_phrase = tweet[end]
			 		
					context = tweet[:start] + tweet[:end]
				 	context = self.ngramify(context)
				else:

					target_phrase = self.ngramify(tweet[start:end])
					context = tweet[:start] + tweet[end:]
					context= self.ngramify(context)
				results[key] = {"target":target_phrase,"context":context}
			else:
				context = tweet
				results[key] = {"target":[],"context":context}


		return results

	def context_features(self,key):
		# seperate context, target features?
		rank = self.num_ngrams/4
		ngrams = set(self.ranked_ngrams[:rank])
		if key in self.context_dict:
			condict = self.context_dict[key]
			context = condict["context"]
			target = condict["target"]
			features = {}
			# this just including true features --> should I do this in word_features --> rich!!
			for ngram in ngrams:
				#if ngram in context:
				#	features["context(%s)"%str(ngram)] = (ngram in context)
				features["target(%s)"%str(ngram)] = (ngram in target)

			return features
		return {}
