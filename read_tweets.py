#!/usr/bin/python

import sys

from polarity import parse_polarity_file, PolarityWord,ScoredTweet,EvaluateScore
from prepare_data import prepare_tweet_data,prepare_prob_dicts
import math
import os
import time

from classify import TweetClassifier


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
    #polarity_dict = parse_polarity_file("subclues.tff")

    classifier = TweetClassifier(tagged_tweets=tagged_tweets,instances=instances)#tweet_features = btf)#,all_ngrams = all_ngrams)

 

    
    
