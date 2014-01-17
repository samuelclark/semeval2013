from nltk.metrics import BigramAssocMeasures
from .classify import Classifier, nltk


class NgramClassifier(Classifier):

    """
            This classifier builds featuresets from unigram, bigram, and trigram.
            It is the most impactful classifier
    """

    def __init__(self, **kargs):
        Classifier.__init__(
            self,
            tweets=kargs["tweets"],
            instances=kargs["instances"],
            model=kargs["model"],
            keys=kargs["keys"],
            selection=kargs["selection"])
        self.mode = kargs["mode"]
        self.inclued_pos = kargs["pos"]  # use part of speech
        self.include_word = kargs["word"]  # use mode
        self.mode = kargs["mode"]
        self.id = "ngram{0},m:{1},w:{2},t:{3},s:{4}".format(
            self.num_items,
            self.mode,
            self.include_word,
            self.inclued_pos,
            self.selection)  # construct an id
        self.debug = False
        self.ngram_dict = self.get_ranked_ngrams()  # rank top ngrams
        self.ranked_ngrams = sorted(
            self.ngram_dict,
            key=lambda x: self.ngram_dict[x],
            reverse=True)  # we only want to get the top xfeatures
        self.num_ngrams = len(self.ranked_ngrams)
        self.rank = self.num_ngrams / 3
        self.prepare_features()

    def __str__(self):
        s = "{0} | {1} | {2}\n".format(self.id, self.num_ngrams, self.rank)
        return s

    def build_feature_vector(self, key):

        # create a feature dictionary and return it.
        # features sould be in format of {"feature":value,"feature2",value2}
        # returns <key>,feature_dict for key
        # all the feature methods are added here
        self.count += 1

        word_features = self.word_features(key)
        return word_features

    # NGRAM STUFF
    def get_ranked_ngrams(self, wlist="all", pos=True):
        """
                turn ngram into term: chi_sq associatoin metric
        """

        word_fd = nltk.FreqDist()
        tag_fd = nltk.ConditionalFreqDist()
        for key, tweet in self.tweets.items():
            word_list = self.get_selected_text(tweet)
            label = self.instances[key].label
            for ngram in word_list:
                # do we want the tag here
                word_fd.inc(ngram)
                tag_fd[label].inc(ngram)

        num_pos = tag_fd["positive"].N()
        num_neg = tag_fd["negative"].N()
        # num_neu = tag_fd["neutral"].N() # ignore neutral tweets
        ngram_dict = {}

        total = num_pos + num_neg  # + num_neu
        for ngram, frequency in word_fd.items():
            try:
                # build chi_sq metrics for both positive and negative tags
                pos_metric = BigramAssocMeasures.chi_sq(
                    tag_fd['positive'][ngram], (frequency, num_pos), total)
                neg_metric = BigramAssocMeasures.chi_sq(
                    tag_fd['negative'][ngram], (frequency, num_neg), total)

                #neu_metric = BigramAssocMeasures.chi_sq(tag_fd['neutral'][ngram],(frequency,num_neu),total)
                score = pos_metric + neg_metric
                ngram_dict[ngram] = score  # append score
            except:
                continue
        return ngram_dict

    def word_features(self, key):
        """
                Determines which feaature to pull from text depending on <key>
        """

        ngrams = set(self.ranked_ngrams[:self.rank])

        ngram_list = self.get_selected_text(self.tweets[key])
        document_ngrams = set(ngram_list)
        features = {}

        for ngram in ngrams:
        #	if self.mode!="unigrams":
        #		if ngram in document_ngrams:
        #			features["contains(%s)"%str(ngram)]=(ngram in document_ngrams)
        #	else:

            features["%s-%s(%s)" % (self.mode, self.selection, str(ngram))
                     ] = (ngram in document_ngrams)

        return features
