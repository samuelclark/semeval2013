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
class WordSynsets:
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



	def build_synset_dict(self):
		syn_dict = {}
		#outfile = open("nosynsets.txt","w")
		for word,tag in self.words:
			synset = wn.synsets(word.lower())

			if synset:
				for each in synset:
					word_pos = self.tag_map.get(tag,"n")
					if each.pos == word_pos:
						# we found our match
						choice = each
						break
				syn_dict[(word,tag)] = choice
			else:
				#outfile.write(word+"\n")
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










