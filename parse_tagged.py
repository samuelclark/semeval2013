


def load_parsed_tweets():
	# the ARK tagger has different tags than the weib polarity set thus we need to create a mapping
	# mapping found --> https://github.com/brendano/ark-tweet-nlp/blob/master/docs/annot_guidelines.md
	tag_map = dict([("N","noun"),("^","noun"),("Z","noun"),("S","noun"),("O","noun"),("L","noun"),
		("V","verb"),("R","adverb"),("A","adj"),("D","anypos"),("T","anypos"),("P","anypos"),("!","anypos")])
	tagger = lambda tag : tag_map[tag] if tag in tag_map else "anypos"

	tweet_file = open("data/tagged_tweets.txt","r")


	tuple_tweet = []

	count = 0
	tweet_dict = {}
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



