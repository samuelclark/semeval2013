#!/usr/bin/python

import sys

from polarity import parse_polarity_file, PolarityWord,ScoredTweet,EvaluateScore
from prepare_data import prepare_tweet_data,prepare_prob_dicts
import math
import os
import time

from ngram_classify import NgramClassifier
from length_classify import LengthClassifier
from postag_classify import PosTagClassfier
from repeat_classify import RepeatClassfier


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

 #   ngram_classifier = NgramClassifier(tagged_tweets=tagged_tweets,instances=instances,mode="trigrams",word=False,pos=True,merge=True)#tweet_features = btf)#,all_ngrams = all_ngrams)
  #  length_classifier = LengthClassifier(tagged_tweets=tagged_tweets,instances=instances,merge=True)
    #postag_classifier = PosTagClassfier(tagged_tweets=tagged_tweets,instances=instances,merge=True,tag="E")
   # postag_classifier.train_classifier()
    repeat_classifier = RepeatClassfier(tagged_tweets=tagged_tweets,instances=instances,merge=True)
    repeat_classifier.train_classifier()
   # misc_classifier = MiscClassifier(tagged_tweets=tagged_tweets,instances=instances,mode="unigrams",word=False,pos=True,merge=True).miscclassifier

 

    
    
