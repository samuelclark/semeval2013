import nltk
import math
class TweetFeatures:
	def __init__(self,**kargs):


		self.tagged_tweets = kargs["tagged_tweets"]
		self.instances = kargs["instances"]
		self.total_distribution = self.get_tweet_distribution()
		self.mode = kargs["mode"]
		self.pos = kargs["pos"]
		self.word = kargs["word"]
		self.ngram_prob = self.get_ngram_prob()
		self.scored_ngrams = self.score_ngram_dict(self.ngram_prob)
		self.display = True


	def __str__(self):
		self.eval_ranked(self.scored_ngrams)
		return "TweetFeaturesObj\n"




	def get_tweet_distribution(self):
	    total_label_probabilities = {}
	    for key,inst in self.instances.items():
	        total_label_probabilities[inst.label] = total_label_probabilities.get(inst.label,0)+1
	    for label in total_label_probabilities:
	        total_label_probabilities[label] = float(total_label_probabilities[label])/float(len(self.instances))
	    return total_label_probabilities


	def ranked(self,d):
		rank = sorted(d,key =lambda x: d[x],reverse=True)
		return rank
	def eval_ranked(self,d):
		right = 0
		wrong = 0 
		for key,score in d.items():
			correct = self.instances[key].label
			ranked = self.ranked(score)
			choice = ranked[0]
			answer = choice == correct
			if answer:
				right+=1
			else:
				wrong+=1
			if self.display:
				if not answer:
					print "***key = {0}***\n".format(key)
					print "guess: {0}\ncorrect: {1}\nanswer: {2}\n".format(choice,correct,answer)

			if self.display:
				if not answer:
					for rank,each in enumerate(ranked):
						print rank,each,score[each]
					tw = self.ngramify(self.tagged_tweets[key])
					for each in tw:
						print each,"\t",self.ngram_prob[each]


		print "result = {0}/{1}\n".format(right,wrong)
		return right,wrong





	def ngramify(self,word_list):
		if self.word and self.pos:
			selection = word_list
		elif self.word:
			selection = [w for w,p in word_list]
		elif self.pos:
			selection = [p for w,p in word_list]

		if self.mode == "unigrams":
			word_list = selection
		elif self.mode =="bigrams":
			word_list = nltk.bigrams(selection)
		elif self.mode == "trigrams":
			word_list = nltk.trigrams(selection)
		return word_list
	


	def get_ngram_prob(self):
        # word_dict = defaultdict(list)
	    word_dict = {}
	    for key,tweet in self.tagged_tweets.items():
	        
	    	word_list = self.ngramify(tweet)

	        label = self.instances[key].label
	        for ngram in word_list:
	            if ngram not in word_dict:
	                word_dict[ngram] = []
	            word_dict[ngram].append(label)
	    for key,result in word_dict.items():
	        result_dict = {}
	        label_distributions = nltk.FreqDist(result)
	        for label,occurences in label_distributions.items():
	            raw_score = float(occurences)/float(label_distributions.N())
	            overall = self.total_distribution[label]
	            logscore = math.log(raw_score/overall)
	            result_dict[label] = logscore
	        result_dict["occurences"] = label_distributions.N()
	        word_dict[key] = result_dict
	    return word_dict

	def score_ngram_dict(self,prob_dict):
		total_dict = {}

		for key,tweet in self.tagged_tweets.items():
			word_list = self.ngramify(tweet)
			score_dict = {"objective":0.,"positive":0.,"negative":0.,"neutral":0.}

			for ngram in word_list:
				for label in prob_dict.get(ngram,[]):
					if label != "occurences" and label!="neutral":
						score_dict[label]+=prob_dict[ngram][label]
			total_dict[key]= score_dict
		return total_dict
