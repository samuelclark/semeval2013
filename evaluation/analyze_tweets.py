import nltk
import string
import cPickle
from collections import defaultdict


class AnalyzeTweets(object):

    """
        This class consolidates information contained in <tweets> and <instances>.
        - instances (instances.py) contain the meta-information about each piece of text such as <start_pos, end_post,  known polarity>
        - tweets (tweets.py) contain the text and part of speech tagged text.
        - this class contains methods that extract features from the text and generate summary statistics about the data
    """

    def __init__(self, **kargs):
        self.tagged_tweets = kargs["tagged_tweets"]  # Tweet objects
        self.instances = kargs["instances"]  # Instance objects
        self.num_instances = len(self.instances)
        self.pickle = kargs["pickle"]  # option to load from Pickle File
        if "task" in kargs:
            self.task = kargs["task"]
        else:
            self.task = None

    def __str__(self):
        buf = 80 * "*"
        class_str = "{0}\nTask:{1}\nNum_instances{2}\n{0}\n".format(
            buf,
            self.task,
            self.num_instances)
        return class_str

    def __check_unavailable(self, wlist):
        """
            Checks to see if a Tweet was Unavailable (a very small subset of the provided data)
        """

        return (len(wlist) == 1 and "Unavailable" in wlist)

    def __check_hashtag(self, wlist):
        """
            Returns True if a hashtag exists in the wordlist
        """
        for word in wlist:
            if word.startswith("#"):
                print word
                # print wlist.index(word)
                return True
        return False

    def __check_mention(self, wlist):
        """
            Returns True if a mention exists in the wordlist
        """

        for word in wlist:
            if word.startswith("@"):
                print word
                return True
        return False

    def get_instances_of_phraselength(self, length=-1):
        """
            Returns a list of instance keys with target phrase of given length
            length = endpos - startpos
            default length = -1 returns list of all instance keys
        """

        if length == -1:
            return self.instances.keys()

        inst_list = [key for key in self.instances
                     if len(self.instances[key]) <= length]
        return inst_list

    def get_length_by_label_dict(self):
        """
            builds a dict of {"label":[length of each target phrase]}
            used to estimate the length distribuitions for each label
        """

        length_dict = {"negative": [],
                       "positive": [],
                       "objective": [],
                       "neutral": []}
        for key in self.instances:
            instance = self.instances[key]
            length_dict[instance.label].append(len(instance))
        return length_dict

    def get_length_probabilities(self, pickfile):
        """
            Calculations distribution of sentence length
            Accumulaton results in <sentence_length (words) : count>
            returns {length: count}
        """
        length_probability_dict = defaultdict(list)
        for key, instance in self.instances.items():
            length_probability_dict[len(instance)].append(instance.label)
        for key, result in length_probability_dict.items():
            result_dict = {}
            label_distributions = nltk.FreqDist(result)
            for label, occurences in label_distributions.items():
                result_dict[label] = float(
                    occurences) / float(label_distributions.N())
            result_dict["occurences"] = label_distributions.N()
            length_probability_dict[key] = result_dict
        if self.pickle:
            length_file = open(pickfile, "w")
            print "pickling length probs to to {0}".format(length_file.name)
            cPickle.dump(length_probability_dict, length_file)
            length_file.close()

        return length_probability_dict

    def get_word_probabilities(self, pickfile):
        """
            Calculates the unigram frequency of the entire corpora of provided tweets
            returns {term : count}

        """
        # word_dict = defaultdict(list)
        word_dict = {}
        for key, tweet in self.tagged_tweets.items():
            word_list = tweet

            label = self.instances[key].label
            for word in word_list:
                if word not in word_dict:
                    word_dict[word] = []
                word_dict[word].append(label)
        for key, result in word_dict.items():
            result_dict = {}
            label_distributions = nltk.FreqDist(result)
            for label, occurences in label_distributions.items():
                result_dict[label] = float(
                    occurences) / float(label_distributions.N())
            result_dict["occurences"] = label_distributions.N()
            word_dict[key] = result_dict

        if self.pickle:
            word_file = open(pickfile, "w")
            print "pickling word probs to to {0}".format(word_file.name)
            cPickle.dump(word_dict, word_file)
            word_file.close()
        return word_dict

    def get_tweet_distribution(self):
        """
            Calculates the distribution of <label : count>
            returns {label: count}
        """
        total_label_probabilities = {}
        for key, inst in self.instances.items():
            total_label_probabilities[
                inst.label] = total_label_probabilities.get(
                inst.label,
                0) + 1
        for label in total_label_probabilities:
            total_label_probabilities[label] = float(
                total_label_probabilities[label]) / float(len(self.instances))
        print "overall distribution of {0} tweets = {1}\n".format(self.num_instances, total_label_probabilities)
        return total_label_probabilities

    def clean_word(self, word):
        """
            removes punctuation from tweet (MAJOR BUG EXISTED HERE)
        """
        clean_word = word.translate(
            string.maketrans("", ""), string.punctuation)
        clean_word = clean_word.lower()
        return clean_word

    def build_context_target_dict(self, tweets):
        """
            Strips target text from the tweet and returns what is left.
            returns {tweet_id: (tweet - target)}
        """
        results = {}
        skipped = 0
        for key, tweet_words in tweets.items():
            start = self.instances[key].startpos
            end = self.instances[key].endpos
            try:
                if self.__check_unavailable(tweet_words):
                    pass
                elif start == end:
                    target_phrase = tweet_words[start]
                    context = tweet_words[:end - 1] + tweet_words[:start]
                else:
                    target_phrase = tweet_words[start:end]
                    context = tweet_words[:start] + tweet_words[end:]
                results[key] = {"context": context,
                                "target_phrase": target_phrase}
            except:
                skipped += 1
                # print "PARSING ERROR\t", key, IndexError,
                # "skipped={0}".format(skipped)

        return results
