from .classify import Classifier


class PosTagClassfier(Classifier):

    def __init__(self, **kargs):
        Classifier.__init__(
            self,
            tagged_tweets=kargs["tagged_tweets"],
            instances=kargs["instances"],
            model=kargs["model"],
            keys=kargs["keys"])
        self.tag = kargs["tag"]
        self.id = "tagcount{0},tag{1}".format(self.num_items, self.tag)

    def build_feature_vector(self, key):
        """
                Uses count distribution of part of speech tags in the tweet as tags
        """
        tweet = self.tagged_tweets[key]
        tags = [t for w, t in tweet]
        count = tags.count(self.tag)
        return {"tag_proportion(%s)" % (self.tag): count}

"""
		index of NLTK to ARK tags
		self.tags = dict([("N","noun"),("^","noun"),("Z","noun"),("S","noun"),("O","noun"),("L","noun"),
		("V","verb"),("R","adverb"),("A","adj"),("D","anypos"),("T","anypos"),("P","anypos"),("!","anypos")]).keys()
		r
"""
