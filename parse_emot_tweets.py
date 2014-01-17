from pattern.db import Datasheet
from .instance import Instance
import subprocess
import os
import cPickle
import csv


def tag_emot_content(content_file, data, task="A"):
    """
        This function used a Twitter specific ARK tagger from CMU
        It is much faster and more accurate than python implementations (NLTK)
        It took a content file and data.
        The output is parsed back into the tweets objects (see load_tweet_objects)
    """
    emot_instances = {}
    script_path = "./ark-tweet-nlp-0.3.2/runTagger.sh --output-format conll"
    tagged_file = "emottagged/{0}".format(content_file.replace("content", "tagged"))
    instance_file = "{0}".format(content_file.replace("content", "instances"))
    instance_file = instance_file.replace(".txt", ".pkl")

    if tagged_file.split("/")[1] in os.listdir(tagged_file.split("/")[0]):
        print "already tagged!"
        instances = load_pickle(instance_file)
        return tagged_file, instances
    else:
        outfile = open(content_file, "w")
        for tweet in data:
            print len(tweet)
            if len(tweet) == 10:
                # unpact tweet
                key = tweet[0]
                keyword = tweet[1]
                label = tweet[2].strip()
                label = str(label)
                text = tweet[3]
                text = text.encode('ascii', 'ignore')
                text = text.strip()

                if text:
                    outline = "{0} {1} {2}\n".format(key, key, text)
                    outfile.write(outline)
                    if task == "A":
                        emot_instances[(
                            str(key),
                            str(key))] = Instance(key,
                                                  key,
                                                  task,
                                                  startpos=0,
                                                  endpos=0,
                                                  label=label)
        outfile.close()
        command = "{0} {1} > {2}".format(
            script_path,
            content_file,
            tagged_file)
        print "calling {0}\n".format(command)

        subprocess.call([command], shell=True)
        print "saving pickle to {0}".format(instance_file)
        cPickle.dump(emot_instances, open(instance_file, "w"))
        return tagged_file, emot_instances


def load_parsed_tweets(taggedfile):
    """
        This function takes the name of a file containing arc tagged tweets and loads it into Tweet objects
        It uses pattern.db.datasheet to help parse the input

            input:
                taggedfile: /path/to/postweets
    """

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
            if uid.isdigit() and sid.isdigit():
                tweet_dict[(uid, sid)] = tuple_tweet
            else:
                print uid, sid
            count = 0
            tuple_tweet = []

    tweet_file.close()
    return tag_map, tagger, tweet_dict


def load_pickle(fname):
    """
        Helper function that loads a pickle from a file and returns it
    """
    try:
        fptr = open(fname, "r")
        data = cPickle.load(fptr)
        fptr.close()
        return data
    except IOError as e:

        print "loading {0} failed".format(fname)
        print e


infile = "testtweets.txt"
content = open(infile, "rb").read().replace('\r', '')
cleaned = "cleaned_{0}".format(infile)
with open(cleaned, "wb") as c:
    for line in content:
        c.write(line)

ds = Datasheet.load(cleaned, separator=",", headers=False)

tagged_file, emot_instances = tag_emot_content(cleaned, ds)
tag_map, tagger, emot_tagged_tweets = load_parsed_tweets(tagged_file)
