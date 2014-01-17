class Vote:

    """
        This class contains the information and methods that drive to the systems voting behavior
        It is subclassed by ConfidenceVote
    """

    def __init__(self, **kargs):
        self.tweets = kargs["tweets"]
        self.instances = kargs["instances"]
        self.classifier_dict = kargs["classifiers"]
        self.selection = kargs["selection"]
        self.cids = self.classifier_dict.keys()
        self.scored_tweets = {}
        self.classified_tweets = {}
        self.basic_result_dict = {}
        self.weighted_result_dict = {}
        self.training = True
        # self.score_all_classifiers() # scores all classifiers

    def __str__(self):
        return str(self.cids)

    def __get_classifier(self, cid):
        """
            gets classifer, sets its data, returns it
        """
        classifier = self.classifier_dict[cid]
        classifier.tweets = self.tweets
        classifier.instances = self.instances
        return classifier

    def reset(self):
        """
            Resets storage dictionaries
        """
        self.scored_tweets = {}
        self.classified_tweets = {}
        self.basic_result_dict = {}
        self.weighted_result_dict = {}

    def score_tweet(self, key, cid):
        """
            matches classifier <cid> and tweet <key>
            and returns classifier.classify(tweet)
            also returns scored_tweets[key][cid]
        """
        tweet_classifier = self.__get_classifier(cid)
        classification, score = tweet_classifier.classify(key)

        if key not in self.scored_tweets:
            self.scored_tweets[key] = {}
        if key not in self.classified_tweets:
            self.classified_tweets[key] = {}

        self.scored_tweets[key][cid] = score
        self.classified_tweets[key][cid] = classification
        return classification, score

    def build_vote_dicts(self):
        """
            constructs a basic and weighted vote dictionary
        """
        self.basic_result_dict = self.make_basic_vote()
        self.weighted_result_dict = self.make_weighted_vote()

    def score_tweets_bycid(self, cid):
        """
            scores all tweets with classifier specified by <cid>
        """
        print "scoring votes for {0}".format(cid)
        for key in self.tweets.keys():
            c, s = self.score_tweet(key, cid)

    def score_all_classifiers(self):
        """
            calls score_tweets_bycid() on all the classifiers
        """
        for cid in self.cids:
            self.score_tweets_bycid(cid)

    def get_score(self, key, cid):
        """
            returns score for tweet <key> with for <cid>
        """

        res_dict = {}
        s = self.scored_tweets[key][cid]
        for each in s.samples():
            res_dict[each] = s.prob(each)
        return res_dict

    def basic_vote(self, key):
        # puts the classification for each cid in a list per key
        """
            adds the classification for each cid in a list per tweet <key>
            returns the result list
        """
        res_list = []
        for cid in self.classified_tweets[key]:
            res_list.append(self.classified_tweets[key][cid])
        return res_list

    def make_basic_vote(self):
        """
            for each tweet puts the results of a basic vote in a dict by tweet <key>
        """
        result_dict = {}
        for key in self.tweets.keys():
            result_dict[key] = self.basic_vote(key)
            # if 'partial' in result_dict[key]:
            #	print result_dict[key],self.instances[key].label
        return result_dict

    def weighted_vote(self, key):
        """
            adds results of weighted vote by tweet <key>
        """
        res_list = []
        for cid in self.scored_tweets[key]:
            score = self.get_score(key, cid)
            res_list.append(score)
        return res_list

    def make_weighted_vote(self):
        """
            calls weighted_vote on each tweet
        """
        result_dict = {}
        for key in self.tweets.keys():
            result_dict[key] = self.weighted_vote(key)
        return result_dict

    def summarize_weighted_results(self):
        """
            function that summarizes the results of a weihted vote by the classifiers
        """
        summarized_dict = {}
        for key, result in self.weighted_result_dict.iteritems():
            num_classifiers = len(result)
            if key not in summarized_dict:
                summarized_dict[key] = {}
            for score in result:
                for tag, prob in score.items():
                    summarized_dict[key][tag] = summarized_dict[key].get(
                        tag,
                        0) + prob / float(num_classifiers)
        return summarized_dict
