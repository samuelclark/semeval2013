import random
import nltk
import cPickle
class Classifier:
	def __init__(self, **kargs):
		self.tagged_tweets =kargs["tagged_tweets"]
		self.instances = kargs["instances"]
		self.keys = kargs["keys"]
		self.debug=False
		if "model" in kargs:
			self.model = kargs["model"]
		else:
			self.model = False
		self.model = False
		self.count = 0
		self.num_items = len(self.keys)
		self.featureset = None
		self.train_set = None
		self.dev_set = None
		self.test_set = None
		self.split1 = None
		self.split2 = None
		self.classifier = None
		self.classiifer_acc = None
		self.classifier_err = None
		self.best_features = None
		self.test_keys = None
		self.trained=False
		self.alpha_acc = None
		self.baseline = None

		# this is for testing should be done elsewhere
	

	def prepare_features(self):
		self.featureset = self.build_featureset(self.num_items)
		self.split1,self.split2 = len(self.featureset)/3, 2*len(self.featureset)/3
		if self.debug:
			self.train_set = self.featureset[:self.split1]
			self.dev_set= self.featureset[self.split1:self.split2]
			self.test_set = self.featureset[self.split2:]
			self.test_keys = self.keys[self.split2:]
		elif self.model:
			self.train_set = self.featureset
			self.test_set = []
			self.test_keys = []
		else:
			self.train_set = self.featureset[:len(self.featureset)/2]
			self.test_set = self.featureset[len(self.featureset)/2:]
			self.test_keys = self.keys[len(self.featureset)/2:]



	def train_classifier(self):
		if not self.featureset:
			self.prepare_features()
		print "* Training {1}\tsize(training_set)  = {0}\n".format(len(self.train_set),self.id)
		self.classifier = nltk.NaiveBayesClassifier.train(self.train_set)
		if not self.model:
			self.classifier_acc = self.get_classifier_accuracy()
			print self.classifier_acc
			if self.debug:
				self.classifier_error = self.collect_errors(self.classifier)
			self.best_features = self.classifier.most_informative_features(25)
			if self.debug:
				self.classifier.show_most_informative_features(10)
		self.trained=True

	def create_validation_sets(self,featureset,folds):
		fsets = {}
		split = len(featureset)/folds
		startidx = 0
		for segment in range(1,folds+1):
			splitidx = split * segment
			print startidx,splitidx
			fsets[segment] = featureset[startidx:splitidx]
			startidx=splitidx

		return fsets




	def cross_validate(self,folds=5):
		results = []
		fsets = self.create_validation_sets(self.featureset, folds)
		for idx in fsets.keys():
			train_set = []
			for key in fsets.keys():
				if key == idx:
					test_set = fsets[idx]
				else:
					train_set +=fsets[idx]
			classifier = nltk.NaiveBayesClassifier.train(train_set)
			accuracy = nltk.classify.accuracy(classifier,test_set)
			results.append(accuracy)
		return results

			

			# build train set
				# for each key, pair all other 4 as training set
				# for key in keys if not this key add to training
			# build test set
			# train
			# test
			# accuracy

		# {num: <set>}



	def show_features(self,num=10):
		self.classifier.show_most_informative_features(num)



		#self.word_fd,self.tag_fd = self.create_ranked_ngrams()




	def get_label(self,key):
			return self.instances[key].label



	def get_classifier_accuracy(self):
		# returns the accuracy of the classifier as determined by the test_set
		acc =  nltk.classify.accuracy(self.classifier,self.test_set)
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

	def classify(self,key,prob=True):
		if self.trained:
			feature_vector = self.build_feature_vector(key)
			classification,score = self.classifier.classify(feature_vector),self.classifier.prob_classify(feature_vector)
			return classification,score
		else:
			print "{0} NOT TRAINED!".format(self.id)
	def build_featureset(self,num,keys=[]):
		print "creating featureset of {0} tweets\n".format(num)
		# calls self.build_featurevector on each key in the tweet data and returns (feature_dict,label) 
		if not keys:
			featureset = [(self.build_feature_vector(key),self.get_label(key)) for key in self.keys[:num]]
		else:
			featureset = [(self.build_feature_vector(key),self.get_label(key)) for key in keys]
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



