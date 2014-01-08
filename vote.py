# TODO
# create a confident,normal,notconfident score for each classification result (-1,0,1)
# like a modified summarize_tweet
# intermediary function like get score which changes prob --> confidence
# see weihted vote
# confidence determined by devition from the mean in either direction?

# work on getting pos/neg classifiers working
# load in emoticon based polarity set?
# use just pos/neg/neutral tweets from this dataset?
# differenct classifiers for pos/neg


# make languge classifiers more accurate
# less features
# many language based classifiers good @ specific task.


# this should be passed a test set !!!!!

# score tweets by cid
# build vote dicts
# can call score_all_classifiers() to use them all
# evaulate in read_tweets
# reset

class Vote:

    def __init__(self, **kargs):
        self.tweets = kargs["tweets"]
        self.instances = kargs["instances"]
        self.classifier_dict = kargs["classifiers"]
        self.selection = kargs["selection"]
        self.cids = self.classifier_dict.keys()
        self.scored_tweets = {}
        # this is lame but could be used for creating a niave bayse out of this
        self.classified_tweets = {}
        self.basic_result_dict = {}
        self.weighted_result_dict = {}
        self.training = True
        # self.score_all_classifiers() # scores all classifiers

    def __str__(self):
        return str(self.cids)

    def __get_classifier(self, cid):
        classifier = self.classifier_dict[cid]
        classifier.tweets = self.tweets
        classifier.instances = self.instances
        return classifier

    def reset(self):
        self.scored_tweets = {}
        self.classified_tweets = {}
        self.basic_result_dict = {}
        self.weighted_result_dict = {}

    def score_tweet(self, key, cid):
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
        self.basic_result_dict = self.make_basic_vote()
        self.weighted_result_dict = self.make_weighted_vote()

    def score_tweets_bycid(self, cid):
        print "scoring votes for {0}".format(cid)
        for key in self.tweets.keys():
            c, s = self.score_tweet(key, cid)

    def score_all_classifiers(self):
        for cid in self.cids:
            self.score_tweets_bycid(cid)

    def get_score(self, key, cid):
        res_dict = {}
        s = self.scored_tweets[key][cid]
        for each in s.samples():
            res_dict[each] = s.prob(each)
        return res_dict

    def basic_vote(self, key):
        # puts the classification for each cid in a list per key
        res_list = []
        for cid in self.classified_tweets[key]:
            res_list.append(self.classified_tweets[key][cid])
        return res_list

    def make_basic_vote(self):
        result_dict = {}
        for key in self.tweets.keys():
            result_dict[key] = self.basic_vote(key)
            # if 'partial' in result_dict[key]:
            #	print result_dict[key],self.instances[key].label
        return result_dict

    def weighted_vote(self, key):
        res_list = []
        for cid in self.scored_tweets[key]:
            score = self.get_score(key, cid)
            res_list.append(score)
        return res_list

    def make_weighted_vote(self):
        result_dict = {}
        for key in self.tweets.keys():
            result_dict[key] = self.weighted_vote(key)
            # if self.instances[key].label!="objective":
            #	print result_dict[key],self.instances[key].label
        return result_dict

    def summarize_weighted_results(self):
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

##########################################################################
# wanted to make an inherited class for this but using vote is easier
