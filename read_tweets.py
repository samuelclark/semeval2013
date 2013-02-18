#!/usr/bin/python

import sys

from polarity import parse_polarity_file, PolarityWord,ScoredTweet,EvaluateScore
from prepare_data import prepare_tweet_data,prepare_prob_dicts
import math
import os
import time

from synsets import WordSynsets

# EVALUATION DATA
# word_prob is a dictionary of {<word>:{"polarity":probability(0-1)}} pairs 
# the number of occurences the probabilitiy is based on can be found by word_prob[word]["occurences"]

# length_prob is a dictionary of {<instance_length>:{"polarity":probability(0-1)}} pairs
# polarity_dict is a dictionary of {<(word,postag)>:<PolarityWordObject>}

# CONTENT DATA
# tagged_tweets is a dictionary of {<uid,sid>: <tagged_tweet>}
# the tagged tweet is a list of tuples [(word1,pos1),(word2,pos2)]



def build_score_dict(tagged_tweets,length_prob,word_prob,polarity_dict,instances):

    scored_dict = {}

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
    return scored_dict


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
    polarity_dict = parse_polarity_file("subclues.tff")
    analyze,word_prob,length_prob = prepare_prob_dicts(tagged_tweets,instances,training,tsvfile)
    # remove singular occurrences from word_prob ....
    once = [key for key in word_prob if word_prob[key]['occurences']==1]
    print "removing {0}/{1} words from word_prob".format(len(once),len(word_prob))
    for o in once:
        word_prob.pop(o)

    total_label_probabilities = analyze.get_tweet_distribution()
    ct_dict = analyze.build_context_target_dict(tagged_tweets)
    scored_dict = build_score_dict(tagged_tweets,length_prob,word_prob,polarity_dict,instances)


   # print word_prob
    es = EvaluateScore(scored_dict=scored_dict)
    s = WordSynsets(words = word_prob.keys())
    sd = s.synset_dict
    a = sd["Angel","^"]
    m = sd["mother","N"]
    k = ("Angel","^")
    p = s.get_path(k)[0]
    for each,tweet in tagged_tweets.items():
        print tweet
        for word in tweet:
            try:
                syn = sd[word]
                if syn:
                    print syn
            except KeyError as e:
                print "not found: {0}".format(e.message)
        print "\n\n"

    #w,r = es.display_keys()
   # es.score_matrix(r)




 

    
    
