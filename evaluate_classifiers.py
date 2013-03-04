# file to do alpha evaluation from the classifiers using vote dicts
from dircheck import createDir, checkDir
from cresults.eval_classifiers import get_classifier_accuracy
import cPickle
def get_baseline(instances):
	dist = {}
	for key in instances:
		dist[instances[key].label] = dist.get(instances[key].label,0) + 1

	return dist
	# could return pos/total

def evaluate(results,n=100,fname=None):
    # calculates results
    header = "alpha total correct pecent-correct\n"
    if fname:
        print "evaluating to {0}\n".format(fname)
        outf = open(fname,'wb')
    else:
        print header
    for alpha in range(n):
        if alpha%5 == 0:
            alpha2 = alpha/100.0
            res = [a for a in results.values() if abs(a[3])>alpha2]
            if res:
                num_tot = len(res)
                correct = len([a for a in res if a[0] == a[4]])
                percent = correct/float(num_tot)
                if num_tot:
                    out= "{0} {1} {2} {3}\n".format(alpha2,num_tot,correct,percent)
                else:
                    out ="alpha={0} no results".format(alpha2)
                if fname:
                    outf.write(out)
                else:
                    print out
            else:
                print "no res :(....\n"
    if fname:
        outf.close()



def evaluate_classifiers(v,test_keys,classifier_dict,mode="ngram"):
    results = {}
    if not(checkDir(mode)):
        createDir(mode)
    for cid in classifier_dict:
        print "evaulating cid={0}\n".format(cid)
        #if checkDir('/cresults/indiv')
     
        outpath = "cresults/indiv/{1}/{0}.txt".format(cid,mode)

        v.score_tweets_bycid(cid)
        # just need to change here to do combinations of classifiers
        v.build_vote_dicts()
        basic = v.basic_result_dict
        weighted = v.weighted_result_dict
        summarized = v.summarize_weighted_results()
        for key in test_keys:
            pos_votes = basic[key].count("positive")
            neg_votes = basic[key].count("negative")
            actual = v.instances[key].label
            pos_score = summarized[key]["positive"]
            neg_score = summarized[key]["negative"]
            diff = pos_score-neg_score
            beta=.3
            # this should be programable to optimize beta! 
            score_vote = "positive" if (pos_score > neg_score and not(diff<=beta)) else "negative"
            count_vote = "positive" if pos_votes > neg_votes else "negative" # doesnt work for ties # if certain num negvotes?
            line = (actual,pos_score,neg_score,pos_score - neg_score,score_vote,pos_votes,neg_votes,count_vote)
            results[key] = line 

        evaluate(results,fname=outpath)
        v.reset()


def update_classifier_accuracy(mode,baseline=0.8):

    # this should be mode 
    updated_dict = {}
    pic_path = "cresults/pickles/{0}/".format(mode)
    dir_path = "cresults/indiv/{0}/".format(mode)
    print "classifier results from {0}\tbaseline:{1}\n".format(dir_path,baseline)
    a = get_classifier_accuracy(dir_path, baseline)
    for class_key,result in a.items():
        if result:
            pic_file = pic_path + class_key +".pkl"
            cl = cPickle.load(open(pic_file,'r'))
            cl.alpha_acc = result
            cl.baseline = baseline
            print cl.alpha_acc
            updated_dict[class_key] = cl
            print "updated --> {0}\n".format(pic_file)
        else:
            print "skipping classifier --> {0}\n".format(class_key)
    return updated_dict