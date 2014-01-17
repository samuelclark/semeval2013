from .classify import Classifier


class ModelClassifier(Classifier):

    """
            This was an attempt to build a classifier from combinding different models as features
            This was not used in production, it was replaced by a voting system
    """

    def __init__(self, **kargs):
        Classifier.__init__(
            self,
            tagged_tweets=kargs["tagged_tweets"],
            instances=kargs["instances"],
            model=kargs["model"],
            keys=kargs["keys"])
        self.cids = kargs["cids"]  # classifier ids for score lookups
        self.classified_tweets = kargs["classified_tweets"]
        self.id = "model{0}".format(self.num_items)

    def build_feature_vector(self, key):
        features = {}
        for cid in self.cids:
            result = self.classified_tweets[key][cid]
            features["cid={0}".format(cid)] = result
        return features
