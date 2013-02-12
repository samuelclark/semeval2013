
def create_pretag_content(fname,tweets):
	# this function writes <uid sid tweet\n> to an out file
	# this outfile is then tagged by the arc tagger

    # outfile = open("tagged/pretag_b1_tweeti-a-dist.txt","w")
    outfile = open(fname,"w")
    for key,tweet in tweets.items():
        uid,sid = key
        text = tweet.text.encode('ascii','ignore')
        outline ="{0} {1} {2}\n".format(uid,sid,text)
        print outline
        outfile.write(outline)
    outfile.close()

def load_parsed_tweets(taggedfile):
	# this function takes the name of a file containing arc tagged tweets.
	# the ARK tagger has different tags than the weib polarity set thus we need to create a mapping
	# mapping found --> https://github.com/brendano/ark-tweet-nlp/blob/master/docs/annot_guidelines.md

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



