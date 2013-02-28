#!/usr/bin/python

import sys

from polarity import parse_polarity_file, PolarityWord,ScoredTweet,EvaluateScore
from prepare_data import prepare_tweet_data,prepare_prob_dicts
import math
import os
import time
import random

from classifiers.ngram_classify import NgramClassifier
from classifiers.length_classify import LengthClassifier
from classifiers.postag_classify import PosTagClassfier
from classifiers.repeat_classify import RepeatClassfier
from classifiers.emoticon_classify import EmoticonClassfier
from classifiers.model_classify import ModelClassifier
from classifiers.weib_classify import WeibClassfier
from classifiers.context_classify import ContextClassifier
from vote import Vote


def train_model_classifiers(keys):
    # returns classifier_dict
    classifier_dict = {}
    #emottag_classifier = PosTagClassfier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,tag="E",model=False)
   # emottag_classifier.train_classifier()
    #classifier_dict[emottag_classifier.id]=emottag_classifier
    #repeat_classifier = RepeatClassfier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,model=False)
    #repeat_classifier.train_classifier()
    #repeat_classifier.show_features()
    #classifier_dict[repeat_classifier.id]=repeat_classifier
    """"adjtag_classifier = PosTagClassfier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,tag="A",model=False)
        adjtag_classifier.train_classifier()
        advtag_classifier = PosTagClassfier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,tag="R",model=False)
        advtag_classifier.train_classifier()
        classifier_dict[adjtag_classifier.id]=adjtag_classifier
        classifier_dict[advtag_classifier.id]=advtag_classifier"""
     
    emot_classifier = EmoticonClassfier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,merge=True,model=False)
    emot_classifier.train_classifier()
    emot_classifier.show_features()
    classifier_dict[emot_classifier.id]=emot_classifier

    
    unigram_classifier = NgramClassifier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,mode="unigrams",word=True,pos=False,merge=True,model=False)
    unigram_classifier.train_classifier()
    unigram_classifier.show_features()
    classifier_dict[unigram_classifier.id] = unigram_classifier
    ranked_ngrams = unigram_classifier.ranked_ngrams
    context_classifier = ContextClassifier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,mode="unigrams",word=True,pos=False,merge=True,ranked_ngrams=ranked_ngrams,model=False)
    context_classifier.train_classifier()
    classifier_dict[context_classifier.id] = context_classifier
  #  bigram_classifier = NgramClassifier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,mode="bigrams",word=True,pos=False,model=False,context=True)
 #   bigram_classifier.train_classifier()
    #trigram_classifier = NgramClassifier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,mode="trigrams",word=True,pos=True,model=False,context=True)
   # trigram_classifier.train_classifier()


   # classifier_dict[bigram_classifier.id] = bigram_classifier
   # classifier_dict[trigram_classifier.id] = trigram_classifier


    #weib_classifier = WeibClassfier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,polarity_dict=polarity_dict,tag_map=tag_map,model=False)
    #weib_classifier.train_classifier()
    #classifier_dict[weib_classifier.id] = weib_classifier
    return classifier_dict


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
    objectives = [key for key in tagged_tweets if instances[key].label == "objective" or instances[key].label == "neutral"]
    for key in objectives:
        if task == "A":
            tagged_tweets.pop(key)
            instances.pop(key)
        elif task == "B":
            instances[key].label = "neutral"

    dist = {}
    for key in instances:
        dist[instances[key].label] = dist.get(instances[key].label,0) + 1

    keys = tagged_tweets.keys()
    random.shuffle(keys)
    polarity_dict = parse_polarity_file("subclues.tff")
    classifier_dict = train_model_classifiers(keys)
    e = classifier_dict['emoticon1283']

    # ngram_classifier = NgramClassifier(tagged_tweets=tagged_tweets,instances=instances,mode="trigrams",word=False,pos=True,merge=True)#tweet_features = btf)#,all_ngrams = all_ngrams)
    # length_classifier = LengthClassifier(tagged_tweets=tagged_tweets,instances=instances,merge=True)
    # need to train on same shit and test on same shit
    v = Vote(tagged_tweets=tagged_tweets,instances=instances,classifiers=classifier_dict)
    #mc = ModelClassifier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,cids=v.cids,classified_tweets=v.classified_tweets,merge=True,model=False)
   # mc.train_classifier()

    #acc = mc.get_classifier_accuracy()
    #print acc







 

    
    
