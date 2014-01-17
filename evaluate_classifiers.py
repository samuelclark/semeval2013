# file to do alpha evaluation from the classifiers using vote dicts
from .dircheck import createDir, checkDir
from .cresults.eval_classifiers import get_classifier_accuracy
import cPickle


def get_baseline(instances):
    """
        Returns a frequency distribution of labels to show what the overall baseline is
    """
    dist = {}
    for key in instances:
        dist[instances[key].label] = dist.get(instances[key].label, 0) + 1

    return dist
    # could return pos/total


def evaluate(results, n=100, fname=None):
    """

        Combines the votes into a prediction
        Saves result in <fname>
        called by evaluate_classifiers()

    """

    # calculates results
    header = "alpha total correct pecent-correct\n"
    if fname:
        print "evaluating to {0}\n".format(fname)
        outf = open(fname, 'wb')
    else:
        print header
    # for top 100 results
    for alpha in range(n):
        if alpha % 10 == 0:
            alpha2 = alpha / 100.0
            res = [a for a in results.values() if abs(a[3]) > alpha2]
            if res:
                num_tot = len(res)
                correct = len([a for a in res if a[0] == a[4]])
                percent = correct / float(num_tot)
                if num_tot:
                    out = "{0} {1} {2} {3}\n".format(
                        alpha2,
                        num_tot,
                        correct,
                        percent)
                else:
                    out = "alpha={0} no results".format(alpha2)
                if fname:
                    outf.write(out)
                else:
                    print out
            else:
                continue
    if fname:
        outf.close()


def evaluate_classifiers(v, test_keys, classifier_dict,
                         selection="all", mode="ngram"):
    """
        This function contains the main logic that evaluates the classifiers
        For each classifier:
            It loads the alpha results, builds vote dictionaries, and calculates accuracy
            test_keys = provided test set. (gold standard or indomain devset)

    """
    print "creating alpha results from classifiers..."
    results = {}
    if not(checkDir(sub="alpha_results", selection=selection, mode=mode)):
        createDir(sub="alpha_results", selection=selection, mode=mode)

    # loop through classifiers
    for cid in classifier_dict:
        print "evaulating cid={0}".format(cid)
        # if checkDir('/cresults/indiv')

        outpath = "cresults/{0}/{1}/{2}/{3}.txt".format("alpha_results",
                                                        selection, mode, cid)

        v.score_tweets_bycid(cid)
        # just need to change here to do combinations of classifiers
        v.build_vote_dicts()
        basic = v.basic_result_dict
        summarized = v.summarize_weighted_results()
        # loop through each 
        for key in test_keys:
            # get positive and negative votes
            pos_votes = basic[key].count("positive")
            neg_votes = basic[key].count("negative")
            actual = v.instances[key].label
            # get summarized scores
            pos_score = summarized[key]["positive"]
            neg_score = summarized[key]["negative"]
            diff = pos_score - neg_score
            # this should be programable to optimize beta!

            score_vote = "positive" if (pos_score > neg_score) else "negative"
            # doesnt work for ties # if certain num negvotes?
            count_vote = "positive" if pos_votes > neg_votes else "negative"
            # save line to key
            line = (
                actual,
                pos_score,
                neg_score,
                diff,
                score_vote,
                pos_votes,
                neg_votes,
                count_vote)
            results[key] = line

        evaluate(results, fname=outpath)
        v.reset()


def update_classifier_accuracy(selection="all", mode="ngram", baseline=0.55):
    """
        Updates classifier accuracy information with regards to selection, mode, and baseline
    """

    updated_dict = {}
    # load pickle and results path 
    pic_path = "cresults/pickles/{0}/{1}/".format(selection, mode)
    outpath = "cresults/{0}/{1}/{2}/".format("alpha_results", selection, mode)
    print "updating classifier results from {0}\tbaseline:{1}\n".format(outpath, baseline)
    a = get_classifier_accuracy(outpath, baseline)
    for class_key, result in a.items():
        if result:
            pic_file = pic_path + class_key + ".pkl"
            cl = cPickle.load(open(pic_file, 'r'))
            cl.alpha_acc = result
            cl.baseline = baseline
            updated_dict[class_key] = cl
            print "updated --> {0}\n".format(pic_file)
        else:
            print "skipping classifier --> {0}\n".format(class_key)
    return updated_dict
