import subprocess
import os
from .instance import Instance
from . import utils
import time
import cPickle
# from analyze_tweets import AnalyzeTweets
#analyze = AnalyzeTweets(instances=instances,tweets=tweets,task="A")


def prepare_tweet_data(tsvfile, task):
    # this function is a wrapper for getting the tweets and tagged data ready
    # calls many helperfunctions
    # returns all the core data to read_tweets
    tsvfile = tsvfile.split("/")[1]
    tweets_file = "tweet_" + tsvfile.replace(".tsv", ".pkl")
    instance_file = "instance_" + tsvfile.replace(".tsv", ".pkl")
    content_file = "content_{0}".format(tsvfile)
    content_file = "content_{0}".format(tsvfile)
    tweets = cPickle.load(open(tweets_file, "rb"))
    instances = cPickle.load(open(instance_file, "rb"))
    tagged_file = tag_content(content_file, tweets)

    # read tagged stuff
    # probably fix this based on a parameter
    tag_map, tagger, tagged_tweets = load_parsed_tweets(tagged_file)
    # apply tags
    targeted_tweets = find_tweet_targets(tweets, instances)
    finished_tweets = assign_target_phrase(
        targeted_tweets,
        instances,
        tagged_tweets)
    #tweets = set_tagged_target_context(tweets, instances, tagged_tweets)

    return finished_tweets, instances


def get_target_context(word_list, sidx, eidx):
    if sidx == eidx:
        target = word_list[sidx:eidx]
        context = word_list[:sidx] + word_list[eidx:]
    else:
        target = word_list[sidx:eidx + 1]
        context = word_list[:sidx] + word_list[eidx:]
    return target, context


def find_tweet_targets(tweets, instances):
    new_tweets = {}
    grouped_tweets = {}
    for uid, key in tweets:
        if uid not in grouped_tweets:
            grouped_tweets[uid] = []
        grouped_tweets[uid].append((uid, key))
    for key, tweet in tweets.items():
        uid, sid = key
        for other in grouped_tweets[uid]:
            if other != key:
                tweet.other_targets[sid] = (
                    instances[other].startpos,
                    instances[other].endpos)
        new_tweets[key] = tweet
    return new_tweets
        # other = {sid (spos,enddpos)}

        # ["This","is","targetA","less","than",'targetB',"fuck you"]


def assign_target_phrase(tweets, instances, tagged_tweets):
    print "extracting target phrases for this key"
    assigned_tweets = {}
    for key, tweet in tweets.items():
        tagged_text = tagged_tweets[key]
        other_targets = tweet.other_targets
        curr_sidx = instances[key].startpos
        curr_eidx = instances[key].endpos
        new_target = []
        # does the target phrase have anything before it?
        before = False
        after = False
        ordered_other = sorted(
            other_targets,
            key=lambda x: other_targets[x][0])
        new_target = []
        before_end = 0
        after_start = 0
        for each in ordered_other:
            sidx, eidx = other_targets[each]
            if sidx < curr_sidx:
                before = True
                before_end = eidx
            if sidx > curr_eidx:
                after_start = sidx
                after = True
            if before and after:
                break

        if before and after:
            new_target = tagged_text[before_end:after_start]

        elif before:
            new_target = tagged_text[before_end:]
        elif after:
            new_target = tagged_text[:after_start]
        else:
            new_target = tagged_text[:]
        tweet.target = new_target
        assigned_tweets[key] = tweet
    return assigned_tweets


def tag_content(content_file, tweets):
    # content_file: destination for pre-tag output
    # tweets : dict of tweets
        # this function writes <uid sid tweet\n> to content_file
        # this content_file is then tagged by the arc tagger

    script_path = "./ark-tweet-nlp-0.3.2/runTagger.sh --output-format conll"
    tagged_file = "tagged/{0}".format(content_file.replace("content", "tagged"))
    tag_dir = os.listdir(tagged_file.split("/")[0])
    if tagged_file.split("/")[1] in tag_dir:
        print "taggedfile {0} already exists".format(tagged_file)
        return tagged_file

    else:
        print "files searched:\n{0}\n".format(tag_dir)
        print "data has not been tagged .... preparing output and running ark script"
        outfile = open(content_file, "w")
        for key, tweet in tweets.items():
            uid, sid = key
            text = tweet.text
            if text:
                try:
                    text = text.encode('ascii', 'ignore')
                except:
                    print text
                outline = "{0} {1} {2}\n".format(uid, sid, text)
                outfile.write(outline)
            else:
                print "no text {0}\n".format(key)
        outfile.close()
        command = "{0} {1} > {2}".format(
            script_path,
            content_file,
            tagged_file)
        print "Calling {0}\n".format(command)
        subprocess.call([command], shell=True)
    return tagged_file


def load_parsed_tweets(taggedfile):
        # this function takes the name of a file containing arc tagged tweets.
        # the ARK tagger has different tags than the weib polarity set thus we need to create a mapping
        # mapping found -->
        # https://github.com/brendano/ark-tweet-nlp/blob/master/docs/annot_guidelines.md

    print "loading tagged tweets from {0}".format(taggedfile)
    tag_map = dict(
        [("N", "noun"), ("^", "noun"), ("Z", "noun"), ("S", "noun"), ("O", "noun"), ("L", "noun"),
         ("V", "verb"), ("R", "adverb"), ("A", "adj"), ("D", "anypos"), ("T", "anypos"), ("P", "anypos"), ("!", "anypos")])
    tagger = lambda tag: tag_map[tag] if tag in tag_map else "anypos"

        #tweet_file = open("data/tagged_tweets.txt","r")
    tuple_tweet = []
    count = 0
    tweet_dict = {}
    tweet_file = open(taggedfile, "r")
    for tweet in tweet_file:
        info = tweet.split()
        if info:
            count += 1
            word, tag, conf = info
            if count == 1:
                uid = word
            elif count == 2:
                sid = word
            else:
                tuple_tweet.append((word, tag))
        else:
            if (uid, sid) not in tweet_dict:
                tweet_dict[(uid, sid)] = tuple_tweet
            # print tweet_dict[(uid,sid)]
            count = 0
            tuple_tweet = []

    tweet_file.close()
    return tag_map, tagger, tweet_dict


def load_pickle(fname):
    # loads a pickle from a file and returns it
    try:
        fptr = open(fname, "r")
        data = cPickle.load(fptr)
        fptr.close()
        return data
    except IOError as e:

        print "loading {0} failed".format(fname)
        print e


def prepare_prob_dicts(tagged_tweets, instances, training, tsvfile):
    # builds word probability and length probability dicts
    # tweets: dict of tweets
    # instances: dict of instances
    # training: boolean
    # tsvfile: datafile
    # returns <AnalyzeTweetObj> word_prob length_prob
    s = time.time()
    pklfile = tsvfile.split("/")[1]
    word_file = "pickles/word_" + pklfile.replace("tsv", "pkl")
    length_file = "pickles/length_" + pklfile.replace("tsv", "pkl")
    pickles = os.listdir("pickles/")
    if not training:
        # so this is where we will load our pickled training data word_prob and length_prob to use for evaluation on an untagged set
        # path to master pickle fiels here
        print "Testing using {0}\t{1}".format(word_file, length_file)
        word_prob = load_pickle(word_file)
        length_prob = load_pickle(length_file)

    elif not word_file.split("/")[1] in pickles or not length_file.split("/")[1] in pickles:
        # if we havn't pickled this data yet.
        print "no pickle files for {0}, creating ...".format(tsvfile)
        # should reset pickle to true here
        analyze = AnalyzeTweets(
            instances=instances,
            tagged_tweets=tagged_tweets,
            task="A",
            pickle=True)
        word_prob = analyze.get_word_probabilities(word_file)
        length_prob = analyze.get_length_probabilities(length_file)
    else:
        # this is when were doing a training set that is already pickled
        # pickling is faster for current data
        print "loaded word_prob from {0} length_prob from {1}".format(word_file, length_file)
        analyze = AnalyzeTweets(
            instances=instances,
            tagged_tweets=tagged_tweets,
            task="A",
            pickle=False)
        word_prob = load_pickle(word_file)
        length_prob = load_pickle(length_file)
    e = time.time()
    elapsed = e - s
    print "created word/length probability dictionaries --> {0} seconds !!!".format(elapsed)
    return analyze, word_prob, length_prob
