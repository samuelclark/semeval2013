from .vote import Vote
import math


class ConfidenceVote(Vote):

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

        # this classifier dict is updated
        # this class will use the alpha_acc property of the classifier to make decisions on untagged tweets.
        # similar to vote class but seperate instance as the super is created to evaluate a known test set
        # the only difference between the classes is that classifier_dict has
        # been updated with alpha_acc values
    def alpha_vote(self, key, beta=.3):

        res_dict = self.alpha_result_dict
        if key not in res_dict:
            res_dict[key] = {}
        for cid in self.scored_tweets[key]:

            score = self.get_score(key, cid)
            label = self.get_label(score)
            diff = abs(score["positive"] - score["negative"])
            alpha_acc = self.classifier_dict[cid].alpha_acc
            if diff == 1.0:
                rounded = 0.9
            else:
                rounded = math.floor(diff * 10) / 10

            # this beta should/will always be less than baseline or this logic
            # is stupid

            if rounded in alpha_acc:
                if rounded not in res_dict[key]:
                    res_dict[key][rounded] = []
                row = list(alpha_acc[rounded])
                row.append(label)
                res_dict[key][rounded].append(row)
            else:
                print "no conf for diff={0} rounded={1}\n".format(diff, rounded)
        # if updating class dict dont need this, not sure yet
        return res_dict

    def get_label(self, score):
        ranked = sorted(score, key=lambda x: score[x], reverse=True)
        return ranked[0]

    def evaluate_results(self):
        agg_dict = {}
        for key in self.alpha_result_dict:
            # print key
            if key not in agg_dict:
                agg_dict[key] = {}
            alphas = self.alpha_result_dict[key]
            for aval in alphas:

                for res_list in self.alpha_result_dict[key][aval]:
                    total, correct, percent, label = res_list
                    if aval != 'beta':
                        votes = self.basic_score_funct(aval, res_list)
                        agg_dict[
                            key][
                            label] = agg_dict[
                            key].get(
                            label,
                            0) + votes
                        # print agg_dict[key]
                    print "\t alpha: {3} votes: {0} confidence: {1}  label: {2} --> actual: {4}".format(total, percent, label, aval, self.instances[key].label)
            # print
        return agg_dict

    def basic_score_funct(self, alpha, res_list):
        total, correct, percent, label = res_list
        votes = percent

        # print votes,alpha,correct,percent
        return votes
