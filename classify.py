import nltk
from nltk.corpus import names
import random

# feature set = lists of ({<feature_dict>},classification) pairs
# to combine dictionaries dict(d1.items() + d2.items())

class TweetClassifier:
	def __init__(self, **kargs):
		self.tagged_tweets =kargs["tagged_tweets"]
		self.instances = kargs["instances"]
		self.tweet_features = kargs["tweet_features"] # contains data using prior tweet knowledge
		self.keys = self.instances.keys()
		# I think keys are already random but incase the hash is the same or something...
		random.shuffle(self.keys)


		self.featureset = self.build_featureset()
		self.split1,self.split2 = len(self.featureset)/3, 2*len(self.featureset)/3
		# self.train_keys = self.keys[:self.split1]
		# self.dev_keys = self.keys[self.split1:self.split2]
		# self.test_keys = self.keys[self.split2:]
		self.train_set = self.featureset[:self.split1]
		self.dev_set= self.featureset[self.split1:self.split2]
		self.test_set = self.featureset[self.split2:]

		# this is for testing should be done elsewhere
		self.nbclassifier = self.train_nbclassifier()
		self.nbacc = self.get_classifier_accuracy(self.nbclassifier)
		self.nberr = self.collect_errors(self.nbclassifier)
		self.word_fd,self.tag_fd = self.create_ranked_ngrams()



	def build_featurevector(self,key):

		# create a feature dictionary and return it.
		# features sould be in format of {"feature":value,"feature2",value2}
		# returns <key>,feature_dict for key
		# all the feature methods are added here 

		target_length = self.get_length_feature(key)
		emoti_count = self.get_tagcount_feature(key,"E")
		emo_feature = self.get_emoticon_feature(key)

		#obj_feature,pos_feature,neg_feature,neu_feature = self.get_ngram_features(key)	
		#return emoti_count
		return emo_feature

	def get_label(self,key):
		return self.instances[key].label

	def train_nbclassifier(self):
		# trains nbclassifier using self.train_set
		print "* Training NaiveBayes\ttraining_set  = {0} ...\n".format(len(self.train_set))
		nbclassifier = nltk.NaiveBayesClassifier.train(self.train_set)
		print nbclassifier.show_most_informative_features(5)
		return nbclassifier


	def get_classifier_accuracy(self,classifier):
		# returns the accuracy of the classifier as determined by the test_set
		acc =  nltk.classify.accuracy(classifier,self.test_set)
		print acc
		return acc

	def build_featureset(self):
		# calls self.build_featurevector on each key in the tweet data and returns (feature_dict,label) 
		featureset = [(self.build_featurevector(key),self.get_label(key)) for key in self.keys]
		return featureset

	def collect_errors(self,classifier):
		# helper method to collect the erros using the dev set
		errors = {}
		for fvector,tag in self.dev_set:
			guess = classifier.classify(fvector)
			if guess !=tag:
				if (guess,tag) not in errors:
					errors[(guess,tag)] = []
				errors[(guess,tag)].append(fvector)

		return errors



	# FEATURE METHODS --> NEED TO ADD TO buld_featureset() to add to classifier
	# should really make this a new class if i get the chance

	def get_length_feature(self,key):
		# this extracts the lenth of the target phrase as a metric

		# ERROR IMPROVEMENTS
		# can we improve this to weight low tweets more towards pos/neg
		# lots of errors in this classification coming from this
		return {"target_length":len(self.instances[key])}

	def get_emoticon_feature(self,key):
		e_dict = {}
		emots = [":)",":("]
		tweet = self.tagged_tweets[key]
		for emo in emots:
			 e_dict["emo_feature(%s)"%emo] = (emo in [t[0] for t in tweet])
		return e_dict




	def get_tagcount_feature(self,key,tag="E"):
		# checks for emoticon in tweet -> labels that emoticon:True
		# two ways to do this --> contains any emoticon True/False or specific ones
		# doing binary for now --> THIS SHOULD CHANGE
		# IMPROVMENTS
		# we can create a mapping from many emoticons to 3-4 central ones (as seen in other work)
		tweet = self.tagged_tweets[key]
		tags = [t for w,t in tweet]
		return {"tag_count(%s)"%tag:tags.count(tag)}


	def create_ranked_ngrams(self):
		word_fd = nltk.FreqDist()
		tag_fd = nltk.ConditionalFreqDist()
		for key,tweet in self.tagged_tweets.items():
			label = self.instances[key].label
			for word,tag in tweet:
				# do we want the tag here
				word = word.lower()
				word_fd.inc(word)
				tag_fd[label].inc(word)

		return word_fd,tag_fd




#### this ngram stuff is not working well hrm.
#		result = dict(obj_feature.items() + pos_feature.items() + neg_feature.items()  + neu_feature.items() + target_length.items())
	def get_ngrams_scores(self,key,prob_dict):
		# aggregates values for each tweet by iterating through tweets and 
		# finding the corresponding value in self.ngram_prob
		score_dict = {"objective":0.,"positive":0.,"negative":0.,"neutral":0.}
		for ngram in self.tagged_tweets[key]:
		#	word_list = self.ngramify(tweet)
			# could add "occurences":0 here and then where the if != occurences
				#print ngram
			if ngram in prob_dict:
				for label in prob_dict[ngram]:
					if label != "occurences": # and label!="neutral":
						# can add occurences here
						score_dict[label]+=prob_dict[ngram][label]
			else:
				# no ngram found could keep track of these --> self.missing_ngrams
				#print ngram
				continue
		print score_dict
		return score_dict

	def get_ngram_features(self,key):
		score_dict = self.get_ngrams_scores(key,self.tweet_features.ngram_prob)
		obj_feature = {"obj_ngram_score":score_dict["objective"]}
		pos_feature = {"pos_ngram_score":score_dict["positive"]}
		neg_feature = {"neg_ngram_score":score_dict["negative"]}
		neu_feature = {"neu_ngram_score":score_dict["neutral"]}
		return (obj_feature,pos_feature,neg_feature,neu_feature)


	def ngramify(self,word_list,mode="unigrams",pos=True,word=True):
		# creates an ngram from a word_list based on class settings
		if word and pos:
			selection = word_list
		elif word:
			selection = [w for w,p in word_list]
		elif pos:
			selection = [p for w,p in word_list]

		if mode == "unigrams":
			word_list = selection
		elif mode =="bigrams":
			word_list = nltk.bigrams(selection)
		elif mode == "trigrams":
			word_list = nltk.trigrams(selection)
		return word_list


