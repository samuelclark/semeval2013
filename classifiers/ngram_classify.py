from nltk.metrics import BigramAssocMeasures
from classify import Classifier,nltk

# feature set = lists of ({<feature_dict>},classification) pairs
# to combine dictionaries dict(d1.items() + d2.items())
# todo --> build a voting system
# seperate classifier for pos|neg|neutral

class NgramClassifier(Classifier):
	def __init__(self, **kargs):
		Classifier.__init__(self,tagged_tweets=kargs["tagged_tweets"],instances=kargs["instances"],model=kargs["model"],keys=kargs["keys"])
		self.mode = kargs["mode"]
		self.inclued_pos = kargs["pos"]
		self.include_word = kargs["word"]
		self.mode= kargs["mode"]
		self.id="ngram{0},m:{1},w:{2},t:{3}".format(self.num_items,self.mode,self.include_word,self.inclued_pos)
		self.debug=False
		self.ngram_dict = self.get_ranked_ngrams()
		self.ranked_ngrams = sorted(self.ngram_dict,key = lambda x: self.ngram_dict[x],reverse=True)
		self.num_ngrams = len(self.ranked_ngrams)
		self.context_dict = self.build_ct_dict() 
		self.prepare_features()




	def build_feature_vector(self,key):


		# create a feature dictionary and return it.
		# features sould be in format of {"feature":value,"feature2",value2}
		# returns <key>,feature_dict for key
		# all the feature methods are added here 

		self.count+=1

		word_features = self.word_features(key)
		return word_features

	
	# NGRAM STUFF
	def get_ranked_ngrams(self,pos=True):
		word_fd = nltk.FreqDist()
		tag_fd = nltk.ConditionalFreqDist()
		for key,tweet in self.tagged_tweets.items():
			word_list = self.ngramify(tweet)
			label = self.instances[key].label
			for ngram in word_list:
				# do we want the tag here
				word_fd.inc(ngram)
				tag_fd[label].inc(ngram)

		num_pos = tag_fd["positive"].N()
		num_neg = tag_fd["negative"].N()
		#num_neu = tag_fd["neutral"].N()
		ngram_dict = {}

		total = num_pos + num_neg# + num_neu
		for ngram,frequency in word_fd.items():
			try:
				pos_metric = BigramAssocMeasures.chi_sq(tag_fd['positive'][ngram],(frequency,num_pos),total)
				neg_metric = BigramAssocMeasures.chi_sq(tag_fd['negative'][ngram],(frequency,num_neg),total)
				#neu_metric = BigramAssocMeasures.chi_sq(tag_fd['neutral'][ngram],(frequency,num_neu),total)
				score =  pos_metric + neg_metric #+ neu_metric
				ngram_dict[ngram] = score
			except:
				continue
		return ngram_dict
		


	def word_features(self,key):
		rank = self.num_ngrams/5

		ngrams = set(self.ranked_ngrams[:rank])
		ngram_list = self.ngramify(self.tagged_tweets[key])
		document_ngrams = set(ngram_list)
		features = {}

		for ngram in ngrams:
		#	if self.mode!="unigrams":
		#		if ngram in document_ngrams:
		#			features["contains(%s)"%str(ngram)]=(ngram in document_ngrams)
		#	else:
			features["%s(%s)"%(self.mode,str(ngram))]=(ngram in document_ngrams)

		return features


	

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
			print context
			target = condict["target"]
			features = {}
			# this just including true features --> should I do this in word_features --> rich!!
			for ngram in ngrams:
				#if ngram in context:
				#	features["context(%s)"%str(ngram)] = (ngram in context)
				features["target(%s)"%str(ngram)] = (ngram in target)

			return features
		return {}



