from .classify import Classifier


class EmoticonClassifier(Classifier):
    """
        Constructs a feature vector from emoticon frequency counts in the tweets
    """

    def __init__(self, **kargs):
        Classifier.__init__(
            self,
            tweets=kargs["tweets"],
            instances=kargs["instances"],
            model=kargs["model"],
            keys=kargs["keys"],
            selection=kargs["selection"])
        self.mode = "ngram"
        self.include_word = True
        self.inclued_pos = True
        self.emoticons = self.get_all_emoticons()
        self.prepare_features()
        self.id = "emoticon{0},s:{1}".format(self.num_items, self.selection)

    def build_feature_vector(self, key):
        """ 
            sub classed from classify.py
        """
        features = {}
        words = [word for word,
                 tag in self.get_selected_text(
                     self.tweets[key])]
        for emot in set(self.emoticons.keys()):
            features[
                "emoticon-{0}({1})".format(self.selection, emot)] = (emot in words)
        return features

    def get_all_emoticons(self):
        """
            gets all the emoticons in a sentence
        """
        emoticons = {}
        for key, tweet in self.tweets.items():
            word_list = tweet.tagged_text
            for word, tag in word_list:
                if tag == "E":
                    emoticons[word] = emoticons.get(word, 0) + 1
        return emoticons
