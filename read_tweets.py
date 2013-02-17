#!/usr/bin/python

import sys
import utils
import cPickle
from instance import Instance
from collections import defaultdict
from tweet import Tweet
from analyze_tweets import AnalyzeTweets
from polarity import parse_polarity_file, PolarityWord,ScoredTweet,EvaluateScore
import nltk
from parse_tagged import load_parsed_tweets, tag_content
import math

# where the tagged tweets currently are -- can change this to command line if preferable
initialtagged = "tagged/tagged_tweeti-a-sub.dist.txt"
b1tagged = "tagged/tagged_b1_tweeti-a-dist.txt"


if __name__=='__main__':
    try:
        tsvfile = sys.argv[1]
        task = sys.argv[2]
        if task not in ['A', 'B']:
            sys.stderr.write("Must provide task as A or B\n")            
            sys.exit(1)
    except IndexError:
        sys.stderr.write("read_tweets.py <tsvfile> <task>")
        sys.exit(1)
        
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
    

    # EVALUATION DATA
    # word_prob is a dictionary of {<word>:{"polarity":probability(0-1)}} pairs 
    # the number of occurences the probabilitiy is based on can be found by word_prob[word]["occurences"]
 
    # length_prob is a dictionary of {<instance_length>:{"polarity":probability(0-1)}} pairs
    # polarity_dict is a dictionary of {<(word,postag)>:<PolarityWordObject>}

    # CONTENT DATA
    # tagged_tweets is a dictionary of {<uid,sid>: <tagged_tweet>}
    # the tagged tweet is a list of tuples [(word1,pos1),(word2,pos2)]



    scored_dict = {}
    analyze = AnalyzeTweets(instances=instances,tweets=tweets,task="A")
    word_prob = analyze.get_word_probabilities()
    once = [key for key in word_prob if word_prob[key]['occurences']==1]
    for o in once:
        word_prob.pop(o)
    length_prob = analyze.get_length_probabilities()
    polarity_dict = parse_polarity_file("subclues.tff")
    total_label_probabilities = {}
    for key,inst in instances.items():
        total_label_probabilities[inst.label] = total_label_probabilities.get(inst.label,0)+1
    for label in total_label_probabilities:
        total_label_probabilities[label] = float(total_label_probabilities[label])/float(len(instances))
    print total_label_probabilities



    for key,tweet in tagged_tweets.items():
        word_score_dict = {"objective":0.,"positive":0.,"negative":0.,"neutral":0.}
        polarity_score_dict = {"objective":0.,"positive":0.,"negative":0.,"neutral":0.,"both":0.}

        for (word,tag) in tweet:
            for label in word_prob.get(word,[]):
                if label!="occurences":
                    overall = total_label_probabilities[label]
                    word_score = word_prob[word][label]
                    log_score = -(math.log(overall/word_score))
                    res_str = "{4} {0} o:{1} w:{2} l:{3} \n".format(label,overall,word_score,log_score,word)
                   # print res_str

                    word_score_dict[label]+= log_score

            new_tag = tagger(tag)
            tag = new_tag  # hmmmmm
            if (word, new_tag) in polarity_dict:
                polarity_score_dict[polarity_dict[(word, new_tag)].polarity]+=1
        length_score_dict = length_prob[len(instances[key])]
        scored_tweet = ScoredTweet(length_prob=length_score_dict,word_prob=word_score_dict,polarity_score=polarity_score_dict,key=key,correct_label = instances[key].label)
        scored_dict[key] = scored_tweet


    """for key,tweet in tagged_tweets.items():
        word_score_dict = {"objective":0.,"positive":0.,"negative":0.,"neutral":0.}
        polarity_score_dict = {"objective":0.,"positive":0.,"negative":0.,"neutral":0.,"both":0.}

        for (word,tag) in tweet:
            for label in word_prob.get(word,[]):
                if label!="occurences":
                    word_score_dict[label]+= word_prob[word][label]

            new_tag = tagger(tag)
            tag = new_tag  # hmmmmm
            if (word, new_tag) in polarity_dict:
                polarity_score_dict[polarity_dict[(word, new_tag)].polarity]+=1
        length_score_dict = length_prob[len(instances[key])]
        scored_tweet = ScoredTweet(length_prob=length_score_dict,word_prob=word_score_dict,polarity_score=polarity_score_dict,key=key,correct_label = instances[key].label)
        scored_dict[key] = scored_tweet
        # scored_dict = {<key>:ScoredTweetInstance}"""
   # es = EvaluateScore(scored_dict=scored_dict)
    #w,r = es.display_keys()
   # es.score_matrix(r)





         
                    






    # THIS COMMAND WRITES TWEETS TO A TXT FILE FOR PARSING WITH TAGGER
    # ./runTagger.sh --output-format conll ../tweet_texts.txt > tagged_tweets.txt
 

    
    
