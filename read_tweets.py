#!/usr/bin/python

import sys

from polarity import parse_polarity_file, PolarityWord,ScoredTweet,EvaluateScore
from prepare_data import prepare_tweet_data,prepare_prob_dicts
#from parse_emot_tweets import emot_tagged_tweets,emot_instances
import math
import os
import time
import random
import cPickle

from classifiers.ngram_classify import NgramClassifier
from classifiers.length_classify import LengthClassifier
from classifiers.postag_classify import PosTagClassfier
from classifiers.repeat_classify import RepeatClassfier
from classifiers.emoticon_classify import EmoticonClassfier
from classifiers.model_classify import ModelClassifier
from classifiers.weib_classify import WeibClassfier
from classifiers.context_classify import ContextClassifier
from vote import Vote
from evaluate_classifiers import evaluate_classifiers,update_classifier_accuracy
from dircheck import checkDir,createDir
from confidence_vote import ConfidenceVote


def get_tag_classifiers(keys,tags = ["A","R","E"]):
   # gotta re work these they suck
    # ! interjection
    # ^ common noun
    # N noun
    # O pronoun
    # Z proper noun + posssesive
    # M proper noun + verbal
    # S nominal possesive
    # # hashtag
    # @ mention
    # E emoticon
    # A adjective
    # R adverb
    # V verb
    # & coordinating conjunction

    tags = ["!","N","O","Z","S","M","#","@","E","A","V","&","Y"]

    # returns classifier_dict
    classifier_dict = {}
    for tag in tags:
        tag_classifier = PosTagClassfier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,tag=tag,model=False)
        tag_classifier.train_classifier()
        tag_classifier.show_features()
        classifier_dict[tag_classifier.id]=tag_classifier

    return classifier_dict


def get_misc_classifiers(keys):     

    #weib_classifier = WeibClassfier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,polarity_dict=polarity_dict,tag_map=tag_map,model=False)
    #weib_classifier.train_classifier()
    #classifier_dict[weib_classifier.id] = weib_classifier

    classifier_dict = {}
    emot_classifier = EmoticonClassfier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,merge=True,model=False)
    emot_classifier.train_classifier()
    emot_classifier.show_features()
    classifier_dict[emot_classifier.id]=emot_classifier
    repeat_classifier = RepeatClassfier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,model=False)
    repeat_classifier.train_classifier()
    repeat_classifier.show_features()
    classifier_dict[repeat_classifier.id]=repeat_classifier
  
    return classifier_dict

 
def write_classifier_dict(keys,classifier_dict,mode):
    if not(checkDir(mode,sub='pickles')):
        createDir(mode,sub='pickles')
    for cid,classifier in classifier_dict.items():
        print "pickling cid={0}\n".format(cid)
        #if checkDir('/cresults/indiv')
     
        outpath = "cresults/pickles/{1}/{0}.pkl".format(cid,mode)
        cPickle.dump(classifier,open(outpath,'w'))

 


def get_context_classifiers(keys,word,pos,ranked_ngrams):
     #ranked_ngrams = unigram_classifier.ranked_ngrams
    #context_classifier = ContextClassifier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,mode="unigrams",word=True,pos=False,merge=True,ranked_ngrams=ranked_ngrams,model=False)
    #context_classifier.train_classifier()
    #classifier_dict[context_classifier.id] = context_classifier
    return

def get_ngram_classifiers(keys,word,pos):
    classifier_dict = {}
    unigram_classifier = NgramClassifier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,mode="unigrams",word=word,pos=pos,merge=True,model=False)
    unigram_classifier.train_classifier()
    unigram_classifier.show_features()
    classifier_dict[unigram_classifier.id] = unigram_classifier
   
    bigram_classifier = NgramClassifier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,mode="bigrams",word=word,pos=pos,model=False,context=True)
    bigram_classifier.train_classifier()
    bigram_classifier.show_features()
    classifier_dict[bigram_classifier.id] = bigram_classifier
    """trigram_classifier = NgramClassifier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,mode="trigrams",word=word,pos=pos,model=False,context=True)
    trigram_classifier.train_classifier()
    trigram_classifier.show_features()
    classifier_dict[trigram_classifier.id] = trigram_classifier"""
    #cout = "cresults/pickles/ngram/{0}ngram_pos_word_classifiers_{1}.pkl".format(len(keys),len(classifier_dict))
    # cPickle.dump(classifier_dict,open(cout,"w"))
    return classifier_dict


def get_test_data(test_keys):
    test_tagged_tweets = {}
    test_instances = {}
    for each in test_keys:
        test_tagged_tweets[each] = tagged_tweets[each]
        test_instances[each] = instances[each]
    return test_tagged_tweets,test_instances



def get_classifier_dict(keys,mode="ngram"):
    if mode == "ngram":
        classifier_dict = get_ngram_classifiers(keys, True, False)
    elif mode == "tags":
        classifier_dict = get_tag_classifiers(keys)
    elif mode =="misc":
        classifier_dict = get_misc_classifiers(keys)

    else:
        print "enter a valid mode <ngram,tags,misc>\n"
        return {}
    if classifier_dict:
        write_classifier_dict(keys,classifier_dict, mode)
    return classifier_dict



if __name__=='__main__':
    # so this will eventually be python read_tweets.py <tsvfile> <task> <training> <pickle files if training false>
    # or we can hardcode the best word_prob and length_prob files (i.e the biggest)
    # should we eventually combine multiple word probs into a master ???
    try:
        train = lambda x: True if x == "True" else False
        tsvfile = sys.argv[1]
        task = sys.argv[2]
        dataset= sys.argv[3]


        if task not in ['A', 'B']:
            sys.stderr.write("Must provide task as A or B\n")            
            sys.exit(1)
     
    except IndexError:
        sys.stderr.write("read_tweets.py <tsvfile> <task> <training>")
        sys.exit(1)
    if dataset == "emot":
        # emoticon datset
        tagged_tweets = emot_tagged_tweets
        instances = emot_instances

    else:
        # normal dataset
        tweets,instances,tag_map,tagger,tagged_tweets = prepare_tweet_data(tsvfile,task)

    # lazy cleaning of objective and neutral
    objectives = [key for key in tagged_tweets if instances[key].label == "objective" or instances[key].label == "neutral"]
    for key in objectives:
        if task == "A":
            tagged_tweets.pop(key)
            instances.pop(key)
        elif task == "B":
            instances[key].label = "neutral"

   

    keys = tagged_tweets.keys()
    random.seed(0)
    random.shuffle(keys)
    mode = "ngram" # mode -> feature .... bad name 
    classifier_dict = get_classifier_dict(keys,mode=mode)
    test_keys = classifier_dict.values()[0].test_keys
    test_tagged_tweets,test_instances = get_test_data(test_keys) 
    v = Vote(tagged_tweets=test_tagged_tweets,instances=test_instances,classifiers=classifier_dict)
    evaluate_classifiers(v, test_keys,classifier_dict, mode)
    # need some logic going in --> are we using already classified stuff or making new mode?
#    test_keys = ud.values()[0].test_keys
 #   test_tagged_tweets,test_instances = get_test_data(test_keys) 
    ud = update_classifier_accuracy(mode)
    tmp_keys = test_tagged_tweets.keys()[:10]
    cv = ConfidenceVote(tagged_tweets= test_tagged_tweets, instances=test_instances,classifiers=ud)
    cv.score_all_classifiers()
    for each in tmp_keys:
        cv.alpha_vote(each)



    # this code evaluates classifiers based on alpha / beta = .3
    #polarity_dict = parse_polarity_file("subclues.tff")





