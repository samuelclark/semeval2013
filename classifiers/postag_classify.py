from classify import Classifier

# seperate classifier for pos|neg|neutral
		#self.tags = dict([("N","noun"),("^","noun"),("Z","noun"),("S","noun"),("O","noun"),("L","noun"),
		#("V","verb"),("R","adverb"),("A","adj"),("D","anypos"),("T","anypos"),("P","anypos"),("!","anypos")]).keys()
		#r
class PosTagClassfier(Classifier):
	def __init__(self,**kargs):
		Classifier.__init__(self,tagged_tweets=kargs["tagged_tweets"],instances=kargs["instances"],model=kargs["model"],keys=kargs["keys"])
		self.tag = kargs["tag"]
		self.id="tagcount{0},tag{1},merged{2}".format(self.num_items,self.tag,self.merge)




	def build_feature_vector(self,key):
		# checks for emoticon in tweet -> labels that emoticon:True
		# two ways to do this --> contains any emoticon True/False or specific ones
		# doing binary for now --> THIS SHOULD CHANGE
		# IMPROVMENTS
		# we can create a mapping from many emoticons to 3-4 central ones (as seen in other work)
		tweet = self.tagged_tweets[key]
		tags = [t for w,t in tweet]
		return {"tag_count(%s)"%self.tag:tags.count(self.tag)}
