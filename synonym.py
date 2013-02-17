from nltk.corpus import wordnet as wn


class Synonyms:
	def __init__(self,**kargs):
		self.words = kargs["words"]
		#self.synoynm_dict = self.build_synonym_dict()

	def __str__(self):
		buf = 80 * "~"
		class_str = "{0}\nSynonyms: \nWords: {1}\n{0}".format(buf,len(self))
		return class_str

	def __len__(self):
		return len(self.words)

	def build_synonym_dict(self):
		syn_dict = {}
		for word,tag in self.words:
			synset = wn.synsets(word)
			print word,tag,synset
			syns = wn.synset(synset[0])
			print syns

			syn_dict[(word,tag)] = syns
		return syn_dict

