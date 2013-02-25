import random
import nltk
import cPickle
class Classifier:
	def __init__(self, **kargs):
		self.tagged_tweets =kargs["tagged_tweets"]
		self.instances = kargs["instances"]
		self.merge = kargs["merge"]
		self.keys = self.tagged_tweets.keys()
		random.shuffle(self.keys)
		self.debug=False
		self.count = 0
		self.num_items = 10000
		self.featureset = None
		self.train_set = None
		self.dev_set = None
		self.test_set = None
		self.split1 = None
		self.split2 = None
		self.classifier = None
		self.classiifer_acc = None
		self.classifier_err = None
		self.informative_features = None

		# this is for testing should be done elsewhere
	

	def prepare_features(self):
		self.featureset = self.build_featureset(self.num_items)
		self.split1,self.split2 = len(self.featureset)/3, 2*len(self.featureset)/3
		if self.debug:
			self.train_set = self.featureset[:self.split1]
			self.dev_set= self.featureset[self.split1:self.split2]
			self.test_set = self.featureset[self.split2:]
		else:
			self.train_set = self.featureset[:len(self.featureset)/2]
			self.test_set = self.featureset[len(self.featureset)/2:]
		print "features built"


	def train_classifier(self):
		if not self.featureset:
			self.prepare_features()
		print "* Training NaiveBayes\tsize(training_set)  = {0}\n".format(len(self.train_set))
		self.classifier = nltk.NaiveBayesClassifier.train(self.train_set)
		self.classifier_acc = self.get_classifier_accuracy(self.classifier)
		if self.debug:
			self.classifier_error = self.collect_errors(self.classifier)
		self.informative_features = self.classifier.most_informative_features(10)
		self.classifier.show_most_informative_features(10)



		#self.word_fd,self.tag_fd = self.create_ranked_ngrams()




	def get_label(self,key,merge=True):
		if merge:
			key_map = {"objective":"objective","neutral":"partial","positive":"partial","negative":"partial"}
			return key_map[self.instances[key].label]
		else:
			return self.instances[key].label



	def get_classifier_accuracy(self,classifier):
		# returns the accuracy of the classifier as determined by the test_set
		acc =  nltk.classify.accuracy(classifier,self.test_set)
		print acc
		return acc


	def collect_errors(self,classifier):
		# helper method to collect the erros using the dev set
		errors = {}
		for fvector,tag in self.dev_set:
			guess = classifier.classify(fvector)
			if guess !=tag:
				#print guess,tag,fvector,"\n\n"
				errors[(guess,tag)] = errors.get((guess,tag),0)+1

		return errors

	def ngramify(self,word_list):
		# creates an ngram from a word_list based on class settings
		mode = self.mode
		pos = self.inclued_pos
		word = self.include_word
		if word and pos:
			selection = [(w.lower(),p) for w,p in word_list]
		elif word:
			selection = [w.lower() for w,p in word_list]
		elif pos:
			selection = [p for w,p in word_list]

		if mode == "unigrams":
			word_list = selection
		elif mode =="bigrams":
			word_list = nltk.bigrams(selection)
		elif mode == "trigrams":
			word_list = nltk.trigrams(selection)
		return word_list 

	def build_featureset(self,num):
		print "creating featureset of {0} tweets\n".format(num)
		# calls self.build_featurevector on each key in the tweet data and returns (feature_dict,label) 
		featureset = [(self.build_feature_vector(key),self.get_label(key)) for key in self.keys[:num]]
		return featureset

	def build_feature_vector(self,key):
		# this  should get overridden
		return

	def save(self,descrip="foo.txt"):
		outfile = open(descrip,"w")
		if self.classifier:
			cPickle.dump(self.classifier,outfile)
		else:
			print "no classifier to pickel\n"



