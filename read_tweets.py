#!/usr/bin/python

import sys
from analyze_tweets import AnalyzeTweets
from polarity import parse_polarity_file, PolarityWord,ScoredTweet,EvaluateScore
from prepare_data import prepare_tweet_data
import math
import cPickle
import os
import time



# EVALUATION DATA
# word_prob is a dictionary of {<word>:{"polarity":probability(0-1)}} pairs 
# the number of occurences the probabilitiy is based on can be found by word_prob[word]["occurences"]

# length_prob is a dictionary of {<instance_length>:{"polarity":probability(0-1)}} pairs
# polarity_dict is a dictionary of {<(word,postag)>:<PolarityWordObject>}

# CONTENT DATA
# tagged_tweets is a dictionary of {<uid,sid>: <tagged_tweet>}
# the tagged tweet is a list of tuples [(word1,pos1),(word2,pos2)]



def load_pickle(fname):
    try:
        fptr = open(fname,"r")
        data = cPickle.load(fptr)
        fptr.close()
        return data
    except IOError as e:

        print "loading {0} failed".format(fname)
        print e


def prepare_prob_dicts(tweets,instances,training,tsvfile):
    s = time.time()
    pklfile = tsvfile.split("/")[1]
    word_file = "pickles/word_"+pklfile.replace("tsv","pkl")
    length_file = "pickles/length_"+pklfile.replace("tsv","pkl")
    pickles = os.listdir("pickles/")
    if not training:
        # so this is where we will load our pickled training data word_prob and length_prob to use for evaluation on an untagged set
        # path to master pickle fiels here
        print "Testing using {0}\t{1}".format(word_file,length_file)
        word_prob = load_pickle(word_file)
        length_prob = load_pickle(length_file)

    elif not word_file.split("/")[1] in pickles or not length_file.split("/")[1] in pickles:
        # if we havn't pickled this data yet.
        print "no pickle files for {0}, creating ...".format(tsvfile)
        analyze = AnalyzeTweets(instances=instances,tweets=tweets,task="A",pickle=True)
        word_prob = analyze.get_word_probabilities(word_file)
        length_prob = analyze.get_length_probabilities(length_file)
    else:
        # this is when were doing a training set that is already pickled
        # pickling is faster for current data
        print "loaded word_prob from {0} length_prob from {1}".format(word_file,length_file)
        analyze = AnalyzeTweets(instances=instances,tweets=tweets,task="A",pickle=False)
        word_prob = load_pickle(word_file)
        length_prob = load_pickle(length_file)
    e = time.time()
    elapsed = e-s
    print "created word/length probability dictionaries --> {0} seconds".format(elapsed)
    return analyze,word_prob,length_prob

if __name__=='__main__':
    # so this will eventually be python read_tweets.py <tsvfile> <task> <training> <pickle files if training false>
    # or we can hardcode the best word_prob and length_prob files (i.e the biggest)
    # should we eventually combine multiple word probs into a master ???
    try:
        train = lambda x: True if x == "True" else False
        tsvfile = sys.argv[1]
        task = sys.argv[2]
        training = train(sys.argv[3])


        if task not in ['A', 'B']:
            sys.stderr.write("Must provide task as A or B\n")            
            sys.exit(1)
        if training not in [True,False]:
            sys.stderr.write("Must provide True or False if data is a traning set\n")
            sys.exit(1)
    except IndexError:
        sys.stderr.write("read_tweets.py <tsvfile> <task> <training>")
        sys.exit(1)

    tweets,instances,tag_map,tagger,tagged_tweets = prepare_tweet_data(tsvfile,task)
  
    scored_dict = {}
    polarity_dict = parse_polarity_file("subclues.tff")
    analyze,word_prob,length_prob= prepare_prob_dicts(tweets,instances,training,tsvfile)
   

       # so this seems super slow... but might be my computer :)
       # word_prob = load_pickle(word_file)
       # length_prob = load_pickle(length_file)


    # here we pop all the words that only occur once
    once = [key for key in word_prob if word_prob[key]['occurences']==1]

    print "removing {0}/{1} words from word_prob".format(len(once),len(word_prob))
    for o in once:
        word_prob.pop(o)
    total_label_probabilities = analyze.get_tweet_distribution()



    for key,tweet in tagged_tweets.items():
        word_score_dict = {"objective":0.,"positive":0.,"negative":0.,"neutral":0.}
        polarity_score_dict = {"objective":0.,"positive":0.,"negative":0.,"neutral":0.,"both":0.}

        for (word,tag) in tweet:
            for label in word_prob.get(word,[]):
                if label!="occurences":
                    overall = total_label_probabilities[label]
                    word_score = word_prob[word][label]
                    log_score = -(math.log(overall/word_score))
                    res_str = "{4} {0} o:{1} w:{2} l:{3} \n".format(label,overall,word_score,log_score,word)
                   # print res_str

                    word_score_dict[label]+= log_score

            new_tag = tagger(tag)
            tag = new_tag  # hmmmmm
            if (word, new_tag) in polarity_dict:
                polarity_score_dict[polarity_dict[(word, new_tag)].polarity]+=1
        length_score_dict = length_prob[len(instances[key])]
        scored_tweet = ScoredTweet(length_prob=length_score_dict,word_prob=word_score_dict,polarity_score=polarity_score_dict,key=key,correct_label = instances[key].label)
        scored_dict[key] = scored_tweet


    """for key,tweet in tagged_tweets.items():
        word_score_dict = {"objective":0.,"positive":0.,"negative":0.,"neutral":0.}
        polarity_score_dict = {"objective":0.,"positive":0.,"negative":0.,"neutral":0.,"both":0.}

        for (word,tag) in tweet:
            for label in word_prob.get(word,[]):
                if label!="occurences":
                    word_score_dict[label]+= word_prob[word][label]

            new_tag = tagger(tag)
            tag = new_tag  # hmmmmm
            if (word, new_tag) in polarity_dict:
                polarity_score_dict[polarity_dict[(word, new_tag)].polarity]+=1
        length_score_dict = length_prob[len(instances[key])]
        scored_tweet = ScoredTweet(length_prob=length_score_dict,word_prob=word_score_dict,polarity_score=polarity_score_dict,key=key,correct_label = instances[key].label)
        scored_dict[key] = scored_tweet
        # scored_dict = {<key>:ScoredTweetInstance}"""
   # es = EvaluateScore(scored_dict=scored_dict)
    #w,r = es.display_keys()
   # es.score_matrix(r)




 

    
    
