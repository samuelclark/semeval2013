from nltk.corpus import wordnet as wn


#{ Part-of-speech constants
#ADJ, ADJ_SAT, ADV, NOUN, VERB = 'a', 's', 'r', 'n', 'v'
#}


# path_similarity
# wup_similarity

# lch_similarity


#path_similarity

#hypernym_paths

#common_hypernyms


# found = 56386 ~55%
# not_found = 45717 ~45%

class WordSynsets:
	# class to wrape the nltk wordnet synset object
	# takes in [(word,pos)]
	# synset_dict = {(word,pos):synset}

	def __init__(self,**kargs):
		self.tag_map = dict([("N","n"),("^","n"),("Z","n"),("S","n"),("O","n"),("L","n"),("V","v"),("R","r"),("A","a"),("D","n"),("T","n"),("P","n"),("!","n"),("$","n"),("&","n")])
		self.words =  kargs["words"]
		self.synset_dict = self.build_synset_dict()
		self.hyper = lambda s:s.hypernyms()
		self.hypo = lambda s:s.hypornyms()

	def __str__(self):
		buf = 80 * "~"
		class_str = "{0}\nSynonyms: \nWords: {1}\n{0}".format(buf,len(self))
		return class_str

	def __len__(self):
		return len(self.words)

	def synset(self,word):
		return wn.synsets(word)

	def lemmas(self,syn):
		lem = [l.name for s in syn for l in s.lemmas]
		return lem


	def build_synset_dict(self):
		syn_dict = {}
		#outfile = open("nosynset_b1.txt","w")
		for word,tag in self.words:
			synset = wn.synsets(word.lower(),pos = self.tag_map.get(tag,"n"))

			if synset:
				choice = synset[0]
				syn_dict[(word,tag)] = choice
			else:
				#res_str = "{0}\t{1}\n".format(word.lower(),self.tag_map.get(tag,"n"))
				#outfile.write(res_str)
				syn_dict[(word,tag)] = None
		#outfile.close()
		return syn_dict


	def get_path(self,key):
		p = self.synset_dict[key].hypernym_paths()
		first = p[0]
		print "key = ",key
		print "ROOT:"
		for num,syn in enumerate(first):
			ind = "->\t" *num
			print "{0}{1}:{2}".format(ind,num,syn.name)
		print "END"
		return p


""" tweet_syn_dict = {}
    es = EvaluateScore(scored_dict=scored_dict)
    s = WordSynsets(words = word_prob.keys())
    sd = s.synset_dict
    a = sd["Angel","^"]
    k = ("Angel","^")
    p = s.get_path(k)[0]
    for each,tweet in tagged_tweets.items():
        tweet_syn_dict[each] = []
        for word in tweet:
            try:
                syn = sd[word]
                tweet_syn_dict[each].append(syn)

            except KeyError as e:
                continue
               # print "not found: {0}".format(e.message)
    tsd = tweet_syn_dict"""









