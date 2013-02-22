#!/usr/bin/python

import sys
import urllib
import re
import json
import cPickle
import bs4
import os
import archive

#my utilties
import utils
from tweet import Tweet

debug_level = 0
retry=False

#We need an archival format independent of the Tweet class.
#We will save a text file with all the TSV fields followed by the raw HTML


if __name__=='__main__':
    tsvfile = sys.argv[1]
    pickle_file = tsvfile.replace(".tsv",".pkl")
    archive_file= tsvfile.replace(".tsv",".arc")

    #tweet_cache will be empty if the pickle_file doesn't exist
    tweet_cache = utils.load_tweets(pickle_file)
    print tweet_cache

    """
    tweets_file = tsvfile.replace(".tsv",".dat")
    if os.path.exists(tweets_file):
        utils.rename_alternate(tweets_file)
    else:
        sys.stderr.write("Creating new .dat file: {0}\n".format(tweets_file))
    tweets_out = open(tweets_file, 'wb')
    """

    if os.path.exists(archive_file):
        utils.rename_alternate(archive_file)

    archive_list = []

    tsvdata = utils.read_tsvfile(tsvfile)
    for row in tsvdata:
        (sid, uid) = row[:2]
        cache_key = (uid,sid)
        try:
            tweet = utils.get_tweet(uid, sid, tweet_cache, retry=retry)
            archive_list.append(archive.ArchivedTweet("\t".join(row), tweet.get_html()))
        except:
            print "error --> saving/pickling at row = {0}".format(row)
            archive.save_archive_file(archive_file, archive_list)
            pkl = open(pickle_file, 'wb')
            cPickle.dump(tweet_cache, pkl, -1)
            pkl.close()
            break

        #text = tweet.get_text()
        #output = ("\t".join(row)) + "\t" + text + "\n"
        #tweets_out.write(output)

       # if debug_level > 0:
           # sys.stderr.write(output)



    #tweets_out.close()
    
    archive.save_archive_file(archive_file, archive_list)
    
    #Maybe there should be a check to see if the pickle has changed?
    pkl = open(pickle_file, 'wb')
    cPickle.dump(tweet_cache, pkl, -1)
    pkl.close()
