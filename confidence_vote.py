from .vote import Vote
import math


class ConfidenceVote(Vote):

    """
        This class uses the estimated classification accuracy (from the classifier)
        to make decisions about unknown tweets. Each classifier gets a 'vote of confidence in the prediction'

        It takes a series of classifiers and implements a voting system to combine them

    """

    def __init__(self, **kargs):
        Vote.__init__(
            self,
            tweets=kargs["tweets"],
            instances=kargs["instances"],
            classifiers=kargs["classifiers"],
            selection=kargs["selection"])
        self.training = False
        self.tmp_keys = self.tweets.keys()[:10]
        self.alpha_result_dict = {}

    def alpha_vote(self, key, beta=.3):
        """
            get the difference between predicted positive and negative score --> alpha
            get each classfiers accuracy at alpha --> classifier.classifieres.acc
            users that value from each classifer to inform result
        """

        res_dict = self.alpha_result_dict
        res_dict[key] = res_dict.get(key, {})
        # get a score for each tweet
        for cid in self.scored_tweets[key]:
            score = self.get_score(key, cid)
            label = self.get_label(score)
            diff = abs(score["positive"] - score["negative"])
            alpha_acc = self.classifier_dict[cid].alpha_acc
            if diff == 1.0:
                rounded = 0.9
            else:
                rounded = math.floor(diff * 10) / 10

            if rounded in alpha_acc:
                if rounded not in res_dict[key]:
                    res_dict[key][rounded] = []
                row = list(alpha_acc[rounded])
                row.append(label)
                res_dict[key][rounded].append(row)
            else:
                print "no conf for diff={0} rounded={1}\n".format(diff, rounded)
        return res_dict

    def get_label(self, score):
        """
            Ranks the probabilities and returns the top result
            Takes a dict of scores from each classifier
        """
        ranked = sorted(score, key=lambda x: score[x], reverse=True)
        return ranked[0]

    def evaluate_results(self):
        """
            Aggregates the results from each clasifier
            Prints results for each classifier
        """
        agg_dict = {}
        for key in self.alpha_result_dict:
            # print key
            if key not in agg_dict:
                agg_dict[key] = {}
            alphas = self.alpha_result_dict[key]
            # for each alpha value in results...
            for aval in alphas:

                for res_list in self.alpha_result_dict[key][aval]:
                    # unpack results
                    total, correct, percent, label = res_list
                    if aval != 'beta':
                        votes = self.basic_score_funct(aval, res_list)
                        agg_dict[
                            key][
                            label] = agg_dict[
                            key].get(
                            label,
                            0) + votes
                    print "\t alpha: {3} votes: {0} confidence: {1}  label: {2} --> actual: {4}".format(total, percent, label, aval, self.instances[key].label)
        return agg_dict

    def basic_score_funct(self, alpha, res_list):
        """
            Future work could include adding a more complex score function
        """
        total, correct, percent, label = res_list
        votes = percent

        # print votes,alpha,correct,percent
        return votes
