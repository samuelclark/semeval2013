from .tweet import Tweet
from .instance import Instance
import string
import cPickle
import sys
import re


"""
 This file is a brute force parsing of the provided data files
 It creates Tweet and Instance dictionaries and pickles them
 """

# TASK A PARSING
tsvfile = sys.argv[1]
keep = ["!", "@", "#"]

punct = string.punctuation
for each in keep:
    punct.replace(each, "")
datafile = open(tsvfile.replace(".tsv", ".dat"), "rb")
tweet_dict = {}
instance_dict = {}
task = "A"
for each in datafile:
    try:
        if task == "A":
            sid, uid, startpos, endpos, label, text = each.split("\t")
        elif task == "B":
            sid, uid, keyword, label, text = each.split("\t")
        saved = False
        for letter in string.uppercase:
            if saved == True:
                break
            key = (uid, sid + letter)
            if key not in tweet_dict:
                print "adding {0}\n".format(key)
                # try:
                text = text.decode('utf-8-sig')
                link = re.search(
                    r'(https?://)?([-\w]+\.[-\w\.]+)+\w(:\d+)?((/)?([-\w/_\.]*(\?\S+)?)?)*',
                    text)
                if link:
                    text = re.sub(
                        r'(https?://)?([-\w]+\.[-\w\.]+)+\w(:\d+)?((/)?([-\w/_\.]*(\?\S+)?)?)*',
                        "URL",
                        text)
                    print text
                #text = re.sub(r'/^(https?:\/\/)?([\da-z\.-]+)\.([a-z\.]{2,6})([\/\w \.-]*)*\/?$/',"URL",text)
                # print text
                for each in text:
                    if each in punct:
                        text = text.replace(each, "")
                #text = text.encode("ascii",'ignore')
                tweet_dict[key] = Tweet(uid=uid, sid=sid, key=key, text=text)
                saved = True
                # except:
                    # print "failed encoding text for {0}\n".format(key)
            if key not in instance_dict and saved:
                if task == "A":
                    instance_dict[key] = Instance(
                        uid=uid,
                        sid=sid,
                        task="A",
                        key=key,
                        startpos=startpos,
                        endpos=endpos,
                        label=label)
                elif task == "B":
                    instance_dict[key] = Instance(
                        uid=uid,
                        sid=sid,
                        task="B",
                        key=key,
                        keyword=keyword,
                        label=label)
    except:
        print "failed to parse {0}\n".format(each)


tweet_file = "tweet_" + tsvfile.split("/")[1].replace(".tsv", ".pkl")
instance_file = "instance_" + tsvfile.split("/")[1].replace(".tsv", ".pkl")
cPickle.dump(tweet_dict, open(tweet_file, "wb"))
cPickle.dump(instance_dict, open(instance_file, "wb"))
