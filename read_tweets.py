#!/usr/bin/python

import sys

from .polarity import parse_polarity_file, PolarityWord, ScoredTweet, EvaluateScore
from .prepare_data import prepare_tweet_data, prepare_prob_dicts
#from parse_emot_tweets import emot_tagged_tweets,emot_instances
import math
import os
import time
import random
import cPickle

from .classifiers.ngram_classify import NgramClassifier
from .classifiers.length_classify import LengthClassifier
from .classifiers.postag_classify import PosTagClassfier
from .classifiers.repeat_classify import RepeatClassifier
from .classifiers.emoticon_classify import EmoticonClassifier
from .classifiers.model_classify import ModelClassifier
from .classifiers.weib_classify import WeibClassfier
from .vote import Vote
from .evaluate_classifiers import evaluate_classifiers, update_classifier_accuracy, get_baseline
from .cresults.eval_classifiers import get_existing_classifiers
from .dircheck import checkDir, createDir
from .confidence_vote import ConfidenceVote


def write_classifier_dict(keys, classifier_dict, selection, mode):
    print "writing classifier dict"
    if not(checkDir(mode=mode, sub='pickles', selection=selection)):
        createDir(mode=mode, sub="pickles", selection=selection)
    for cid, classifier in classifier_dict.items():
        print "pickling cid={0}".format(cid)
        # if checkDir('/cresults/indiv')

        outpath = "cresults/pickles/{0}/{1}/{2}.pkl".format(selection,
                                                            mode, cid)
        cPickle.dump(classifier, open(outpath, 'w'))


def get_test_data(test_keys):
    test_tweets = {}
    test_instances = {}
    for each in test_keys:
        test_tweets[each] = tweets[each]
        test_instances[each] = instances[each]
    return test_tweets, test_instances


def get_ngram_classifiers(
        keys, existing_class={}, word=True, pos=False, selection="target"):

    classifier_dict = {}
    unigram_classifier = NgramClassifier(
        tweets=tweets,
        instances=instances,
        keys=keys,
        mode="unigrams",
        word=word,
        pos=pos,
        merge=True,
        model=False,
        selection=selection)
    if unigram_classifier.id in existing_class:
        print unigram_classifier.id + "already evaluated\n"

    else:
        unigram_classifier.train_classifier()
        unigram_classifier.show_features(20)
        classifier_dict[unigram_classifier.id] = unigram_classifier

    bigram_classifier = NgramClassifier(
        tweets=tweets,
        instances=instances,
        keys=keys,
        mode="bigrams",
        word=word,
        pos=pos,
        merge=True,
        model=False,
        selection=selection)
    if bigram_classifier.id in existing_class:
        print bigram_classifier.id + "already evaluated"
    else:
        bigram_classifier.train_classifier()
        bigram_classifier.show_features(20)
        classifier_dict[bigram_classifier.id] = bigram_classifier
    """trigram_classifier = NgramClassifier(tweets=tweets,instances=instances,keys=keys,mode="trigrams",word=word,pos=pos,merge=True,model=False,selection=selection)
    trigram_classifier.train_classifier()
    trigram_classifier.show_features(20)"""

    #classifier_dict[trigram_classifier.id] = trigram_classifier
    #cout = "cresults/pickles/ngram/{0}ngram_pos_word_classifiers_{1}.pkl".format(len(keys),len(classifier_dict))
    # cPickle.dump(classifier_dict,open(cout,"w"))
    return classifier_dict


def train_ngram_classifiers(
        mode="ngram", selection="target", word=True, pos=False):
    existing_classifiers = get_existing_classifiers(
        sub="pickles",
        selection=selection,
        mode=mode)
    ngram_classifiers = get_ngram_classifiers(
        keys,
        existing_classifiers,
        word=word,
        pos=pos,
        selection=selection)
    classifier_dict = ngram_classifiers
    if classifier_dict:
        print "evaluating classifier alpha_results for {0}\n".format(classifier_dict.keys())
        write_classifier_dict(
            keys=keys,
            classifier_dict=classifier_dict,
            selection=selection,
            mode=mode)
        test_keys = classifier_dict.values()[0].test_keys
        test_tweets, test_instances = get_test_data(test_keys)
        v = Vote(
            tweets=test_tweets,
            instances=test_instances,
            classifiers=classifier_dict,
            selection=selection)
        evaluate_classifiers(
            v,
            test_keys,
            classifier_dict,
            mode=mode,
            selection=selection)

    # AT THIS POINT CLASSIFIERS ARE TRAINED
    # need some logic going in --> are we using already classified stuff or
    # making new mode?
    else:
        print "already trained {0}".format(existing_classifiers)


def train_all_ngrams():

    # word
    train_ngram_classifiers(selection="target", word=True, pos=False)

    # word + pos
    # train_ngram_classifiers(selection="all",word=True,pos=True)


def get_misc_classifiers(keys, existing_class={}, selection="target"):

    #weib_classifier = WeibClassfier(tagged_tweets=tagged_tweets,instances=instances,keys=keys,polarity_dict=polarity_dict,tag_map=tag_map,model=False)
    # weib_classifier.train_classifier()
    #classifier_dict[weib_classifier.id] = weib_classifier

    classifier_dict = {}
    emot_classifier = EmoticonClassifier(
        tweets=tweets,
        instances=instances,
        keys=keys,
        merge=True,
        model=False,
        selection=selection)
    if emot_classifier.id in existing_class:
        print emot_classifier.id + " already evaluated"
    else:
        emot_classifier.train_classifier()
        emot_classifier.show_features()
        classifier_dict[emot_classifier.id] = emot_classifier
    repeat_classifier = RepeatClassifier(
        tweets=tweets,
        instances=instances,
        keys=keys,
        merge=True,
        model=False,
        selection=selection)
    if repeat_classifier.id in existing_class:
        print repeat_classifier.id + " already evaluated"
    else:
        repeat_classifier.train_classifier()
        repeat_classifier.show_features()
        classifier_dict[repeat_classifier.id] = repeat_classifier

    return classifier_dict


def train_misc_classifiers(selection="all", mode="misc"):
    # ask rich about evaluating votes on training keys instead of testing keys
    existing_classifiers = get_existing_classifiers(
        sub="pickles",
        selection=selection,
        mode=mode)
    print "existing {0}".format(existing_classifiers)
    misc_classifiers = get_misc_classifiers(
        keys,
        existing_class=existing_classifiers,
        selection="all")
    classifier_dict = misc_classifiers
    if classifier_dict:
        print "evaluating classifier alpha_results for {0}\n".format(classifier_dict.keys())
        write_classifier_dict(
            keys=keys,
            classifier_dict=classifier_dict,
            selection=selection,
            mode=mode)
        test_keys = classifier_dict.values()[0].test_keys
        train_keys = classifier_dict.values()[0].train_keys
        test_tweets, test_instances = get_test_data(test_keys)
        train_tweets, train_instances = get_test_data(train_keys)
        v = Vote(
            tweets=test_tweets,
            instances=test_instances,
            classifiers=classifier_dict,
            selection=selection)
        evaluate_classifiers(
            v,
            test_keys,
            classifier_dict,
            mode=mode,
            selection=selection)
    else:
        print "no classifiers to train!\n"
    # need some logic going in --> are we using already classified stuff or making new mode?
    #  AT THIS POINT WE HAVE TRAINED THE CLASSIFIERS
    # update classifier_accuracy loads classifiers from pickles with their
    # corresponding accuracy


def train_all_misc():

    # emoticon, repeat classifiers
    train_misc_classifiers(selection="target")


def use_trained_classifiers(
        selection="all", mode="ngram", test_tweets={}, test_instances={}):

    ud = update_classifier_accuracy(selection=selection, mode=mode)
    print "loaded classifiers for testing:\n{0}".format(ud.keys())
    cv = ConfidenceVote(
        tweets=test_tweets,
        instances=test_instances,
        classifiers=ud,
        selection=selection)
    cv.score_all_classifiers()
    for each in test_tweets.keys():
        cv.alpha_vote(each)
    alpha_vote_dict = cv.evaluate_results()
    return alpha_vote_dict, test_tweets.keys()


if __name__ == '__main__':
    # so this will eventually be python read_tweets.py <tsvfile> <task> <training> <pickle files if training false>
    # or we can hardcode the best word_prob and length_prob files (i.e the biggest)
    # should we eventually combine multiple word probs into a master ???
    try:
        train = lambda x: True if x == "True" else False
        tsvfile = sys.argv[1]
        testfile = sys.argv[2]
        task = sys.argv[3]

        if task not in ['A', 'B']:
            sys.stderr.write("Must provide task as A or B\n")
            sys.exit(1)

    except IndexError:
        sys.stderr.write("read_tweets.py <tsvfile> <task> <training>")
        sys.exit(1)
    # if dataset == "emot":
        # emoticon datset
     ##  instances = emot_instances

        # normal dataset
    tweets, instances = prepare_tweet_data(tsvfile, task)
    testset_tweets, testset_instances = prepare_tweet_data(testfile, task)
    # lazy cleaning of objective and neutral
    objectives = [
        key for key in tweets if instances[
            key].label == "objective" or instances[
            key].label == "neutral"]
    popped = 0
    tpopped = 0
    tneu = 0
    neu_count = 0
    for key in objectives:
        if instances[key].label == "neutral":
            neu_count += 1
        if task == "A":
            instances.pop(key)
            tweets.pop(key)
            popped += 1
        elif task == "B":
            instances[key].label = "neutral"
    test_obj = [
        key for key in testset_tweets if testset_instances[
            key].label == "objective" or testset_instances[
            key].label == "neutral"]
    for key in test_obj:
        if testset_instances[key] == "neutral":
            tneu += 1
        if task == "A":
            testset_instances.pop(key)
            testset_tweets.pop(key)
            tpopped += 1

    print "removed {0} total {1} neutral from training dataset\n".format(popped, neu_count)
    # print "removed {0} total {1} neutral from testing
    # dataset\n".format(tpopped,tneu)

    keys = tweets.keys()
    random.seed(0)
    random.shuffle(keys)
    dist = get_baseline(instances)
    #combined_misc,used_keys = combine_evaluated_misc()
    #combined_ngrames,used_ngrams = combine_evaluated_ngrams()

    # train_all_ngrams()
    # ngrams
    mode = "ngram"

    target_alpha_vote_dict, tweet_keys = use_trained_classifiers(
        selection="target", mode=mode, test_tweets=testset_tweets, test_instances=testset_instances)
    ta = target_alpha_vote_dict
    for key in tweet_keys:
        print key
        actual = testset_instances[key].label
        tar = "tar: {0}".format(ta[key])
        act = "**act: {0}".format(actual)
        print tar
        print act
        print




  #  combined_ngrams = dict(allgram.items() + allposgram.items() +targgram.items() + targposgram.items() + congram.items() + conposgram.items())



    # this code evaluates classifiers based on alpha / beta = .3
    #polarity_dict = parse_polarity_file("subclues.tff")
