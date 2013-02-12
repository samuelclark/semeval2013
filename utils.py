import cPickle
import os
import itertools
import sys
import tweet as twlib


def load_tweets(pickle_file):
    if os.path.exists(pickle_file):
        pickle_in = open(pickle_file, 'rb')
        cache = cPickle.load(pickle_in)
        pickle_in.close()
        return cache
    else:
        return {}

def save_tweets(pickle_file, cache):
    pickle_out = open(pickle_file, 'wb')
    cPickle.dump(cache, pkl, -1)
    pickle_out.close()

def fetch(uid, sid):
    tweet = twlib.Tweet(uid, sid)
    tweet.fetch()
    return tweet

def get_tweet(uid, sid, cache=None, retry=False):
    if cache == None:
        return fetch(uid, sid)

    cache_key = (uid, sid)
    tweet = cache.get(cache_key, None)
    if (tweet is None) or (retry==True and tweet.fetched()==False):
        if tweet is not None:
            print "RETRYING {0}".format(str(cache_key))
        else:
            print "NOT FOUND IN CACHE: {0}".format(str(cache_key))
        tweet = fetch(uid, sid)

        cache[cache_key] = tweet
        
    return tweet

def read_tsvfile(tsvfile):
    tsvdata = []
    for line in open(tsvfile):
        fields = line.rstrip('\n').split('\t')
        tsvdata.append(fields)
    return tsvdata


def alternative_names(filename):
    #HT http://goo.gl/G8nHf
    yield filename
    base, ext = os.path.splitext(filename)
    for i in itertools.count(1):
        yield base + ext + "({0})".format(i)

def get_alternate_name(filename):
    target_name = next(alt_name for alt_name in alternative_names(filename) \
     if not os.path.exists(alt_name))

    return target_name

def rename_alternate(filename):
    old_file = get_alternate_name(filename)
    sys.stderr.write("Renaming file as {0}\n".format(old_file))
    try:
        os.rename(filename, old_file)
    except OSError:
        sys.stderr.write("File renaming failed. Exiting.\n")
        sys.exit(1)

