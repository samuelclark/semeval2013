"""
A simple archive format for downloaded tweets.

Allows for restoring/recreating a pickle file should the Tweet class change.
"""

import cPickle
import os
import tweet as twlib

class ArchivedTweet(object):
    def __init__(self, tsvline, rawhtml):
        self.tsvline = tsvline
        self.rawhtml = rawhtml

    def get_tweet(self):
        (uid, sid) = self.get_key()
        tweet = twlib.Tweet(uid, sid)
        tweet.set_html(self.rawhtml)

    def get_key(self):
        fields = self.tsvline.rstrip('\n').split('\t')
        (sid, uid) = fields[:2]
        return (uid, sid)


def read_archive_file(pickle_file):
    archive = []
    if os.path.exists(pickle_file):
        pickle_in = open(pickle_file, 'rb')
        archive = cPickle.load(pickle_in)
        pickle_in.close()
    return archive

def save_archive_file(pickle_file, archived_tweet_list):
    pkl = open(pickle_file, 'wb')
    cPickle.dump(archived_tweet_list, pkl, -1)
    pkl.close()

def recreate_tweet_pickle(archived_tweet_list, tweet_pickle_file):
    pkl = open(tweet_pickle_file, 'wb')
    tweet_cache = {}
    for archived in archived_tweet_list:
        tweet = archived.get_tweet()
        key = archived.get_key()
        tweet_cache[key] = tweet

    cPickle.dump(tweet_cache, pkl, -1)
    pkl.close()
