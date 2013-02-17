import subprocess
import os
from instance import Instance
import utils
import time
# analyze = AnalyzeTweets(instances=instances,tweets=tweets,task="A")

def prepare_tweet_data(tsvfile,task):
    s = time.time()
    
        
    tweets_file = tsvfile.replace(".tsv",".dat")

    pickle_file = tsvfile.replace(".tsv",".pkl")
    content_file = "content_{0}".format(tsvfile.split("/")[1])
    tweets = utils.load_tweets(pickle_file)
    tagged_file = tag_content(content_file,tweets)

    # read tagged stuff
    tag_map,tagger,tagged_tweets = load_parsed_tweets(tagged_file)   #probably fix this based on a parameter

    for (key, tagged) in tagged_tweets.items():
        (uid,sid)=key #who cares
        untagged_tweet = tweets[key]
        words = [word for (word, tag) in tagged]
        tags = [tag for (word, tag) in tagged]
        untagged_tweet.set_text_and_tags(words, tags)

    instances = {}
    
    tsvdata = utils.read_tsvfile(tsvfile)

    for row in tsvdata:
        (sid, uid) = row[:2]
        key = (uid, sid)
        tweet = tweets[key]
        if task == 'A':
            instances[key] = Instance(uid, sid, task=task, startpos=int(row[2]), endpos=int(row[3]), label=row[4])
        else:
            instances[key] = Instance(uid, sid, task=task, keyword=row[2], label=row[3].strip('"'))

    e = time.time()
    elapsed = e-s
    print "loading tweets and parsing tags --> {0} seconds".format(elapsed)

    return tweets,instances,tag_map,tagger,tagged_tweets

def tag_content(content_file,tweets):
	# this function writes <uid sid tweet\n> to an out file
	# this outfile is then tagged by the arc tagger

    # outfile = open("tagged/pretag_b1_tweeti-a-dist.txt","w")

    outfile = open(content_file,"w")
    for key,tweet in tweets.items():
        uid,sid = key
        text = tweet.text.encode('ascii','ignore')
        outline ="{0} {1} {2}\n".format(uid,sid,text)
        outfile.write(outline)
    outfile.close()
    script_path = "./ark-tweet-nlp-0.3.2/runTagger.sh --output-format conll"
    tagged_file = "tagged/{0}".format(content_file.replace("content","tagged"))
    if tagged_file.split("/")[1] in os.listdir(tagged_file.split("/")[0]):
    	print "taggedfile {0} already exists".format(tagged_file)
    	return tagged_file

    else:
    	print "data has not been tagged .... running ark script"
    	command = "{0} {1} > {2}".format(script_path,content_file,tagged_file)
    	print "Calling {0}\n".format(command)
    	subprocess.call([command],shell=True)
    return tagged_file

def load_parsed_tweets(taggedfile):
	# this function takes the name of a file containing arc tagged tweets.
	# the ARK tagger has different tags than the weib polarity set thus we need to create a mapping
	# mapping found --> https://github.com/brendano/ark-tweet-nlp/blob/master/docs/annot_guidelines.md

    print "loading tagged tweets from {0}".format(taggedfile)
    tag_map = dict([("N","noun"),("^","noun"),("Z","noun"),("S","noun"),("O","noun"),("L","noun"),
		("V","verb"),("R","adverb"),("A","adj"),("D","anypos"),("T","anypos"),("P","anypos"),("!","anypos")])
    tagger = lambda tag : tag_map[tag] if tag in tag_map else "anypos"

	#tweet_file = open("data/tagged_tweets.txt","r")	
    tuple_tweet = []
    count = 0
    tweet_dict = {}
    tweet_file = open(taggedfile,"r")
    for tweet in tweet_file:
		info = tweet.split()
		if info:
			count+=1
			word,tag,conf = info
			if count == 1:
				uid = word
			elif count == 2:
				sid = word
			else: 
					tuple_tweet.append((word,tag))
		else:
			if uid.isdigit() and sid.isdigit():
				tweet_dict[(uid,sid)] = tuple_tweet
			else:
				print uid,sid
			count = 0
			tuple_tweet = []

    tweet_file.close()
    return tag_map, tagger, tweet_dict



