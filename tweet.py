import bs4
import json
import urllib
import StringIO
import csv
import sys


class Tweet(object):

    def __init__(self, uid, sid, key, text):
        self.uid = uid
        self.sid = sid
        self.key = key
        self.text = text
        self.tagged_tweet = None
        self.target = None
        self.other_targets = {}

    def __str__(self):
        buf = 80 * "-"
        class_str = "{3}\nTweet<{0}>\n{1}\n{2}\n{3}\n".format(
            self.key,
            self.target,
            self.context,
            buf)
        return class_str
