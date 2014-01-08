import nltk
import math
import re
# todo
# fix log scores
# score matrix functionality
# add mention, hashtag,emoticon


class TweetFeatures:

    def __init__(self, **kargs):

        self.tagged_tweets = kargs["tagged_tweets"]
        self.instances = kargs["instances"]
        self.total_distribution = self.get_tweet_distribution()
        self.mode = kargs["mode"]
        self.pos = kargs["pos"]
        self.word = kargs["word"]
        self.display = False
        self.usage = self.__usage__

        # NGRAM -- DETERMINED BY KARGS
        self.ngram_prob = self.get_ngram_prob()  # ngram {distribution}
        # key : {ngram scores}
        self.ngram_scores = self.score_ngram_dict(self.ngram_prob)

        # LENGTH
        self.length_prob = self.get_length_prob()  # length {distribution}
        # key :{length scores}
        self.length_score = self.score_length_dict(self.length_prob)

        # CONTEXT
        self.ct_dict = self.build_ct_dict()  # context target dict
        self.context_scores, self.target_scores = self.score_context()

        # HASHTAG AND MENTION
        self.hashtag_prob, self.mention_prob = self.get_hash_mention_prob()
        self.hashtag_score, self.mention_score = self.score_hash_mention_dict()

        # EMOTICONS

        self.emoticon_prob = self.get_emoticon_prob()
        self.emoticon_score = self.score_emoticon_dict()

        # REPEAT LETTERS:

        self.repeat_prob, self.repeat_dist = self.get_repeat_letter_prob()

    def __usage__(self):
        m = "mode: <unigrams> <bigrams> <trigrams>\n"
        w = "word: <True> <False>\n"
        p = "pos: <True> <False>\n"
        print "Usage:\n{0}{1}{2}".format(m, w, p)

    def __str__(self):
        res_str = "TweetFeaturesObject:\ninstances: {0}\nmode: {1}\nword: {2}\npos: {3}\n".format(
            len(self.instances),
            self.mode,
            self.word,
            self.pos)
        return res_str

    def get_tweet_distribution(self):
        # returns the overall distiribution of tweet --> assigned to
        # self.total_distribtuion
        total_label_probabilities = {}
        for key, inst in self.instances.items():
            total_label_probabilities[
                inst.label] = total_label_probabilities.get(
                inst.label,
                0) + 1
            for label in total_label_probabilities:
                total_label_probabilities[label] = float(
                    total_label_probabilities[label]) / float(len(self.instances))
        return total_label_probabilities

    def ranked(self, d):
        # returns reversed ranked dict by key
        rank = sorted(d, key=lambda x: d[x], reverse=True)
        return rank

    def ngramify(self, word_list):
        # creates an ngram from a word_list based on class settings
        if self.word and self.pos:
            selection = word_list
        elif self.word:
            selection = [w for w, p in word_list]
        elif self.pos:
            selection = [p for w, p in word_list]

        if self.mode == "unigrams":
            word_list = selection
        elif self.mode == "bigrams":
            word_list = nltk.bigrams(selection)
        elif self.mode == "trigrams":
            word_list = nltk.trigrams(selection)
        return word_list

    def get_hash_mention_prob(self):
        hashlist = []
        mentionlist = []
        for key, tweet in self.tagged_tweets.items():
            for word, tag in tweet:
                label = self.instances[key].label
                if tag == "#":
                    hashlist.append(label)
                elif tag == "@":
                    mentionlist.append(label)
        hash_distributions = nltk.FreqDist(hashlist)
        mention_distributions = nltk.FreqDist(mentionlist)
        hash_dict = self.calc_label_distributions(hash_distributions)
        mention_dict = self.calc_label_distributions(mention_distributions)
        return hash_dict, mention_dict

    def score_hash_mention_dict(self):
        hash_dict = {}
        mention_dict = {}
        for key, tweet in self.tagged_tweets.items():
            score_dict = {
                "objective": 0.,
                "positive": 0.,
                "negative": 0.,
                "neutral": 0.}
            if self.check_hash(key):
                hash_dict[key] = self.hashtag_prob
            else:
                hash_dict[key] = score_dict
            if self.check_mention(key):
                mention_dict[key] = self.mention_prob
            else:
                mention_dict[key] = score_dict
        return hash_dict, mention_dict

    def check_hash(self, key):
        tags = [tag for word, tag in self.tagged_tweets[key]]
        return "#" in tags

    def check_mention(self, key):
        tags = [tag for word, tag in self.tagged_tweets[key]]
        return "@" in tags

    def get_emoticon_prob(self):
        emot_dict = {}
        for key, tweet in self.tagged_tweets.items():
            for word, tag in tweet:
                label = self.instances[key].label
                if tag == "E":
                    if (word, tag) not in emot_dict:
                        emot_dict[(word, tag)] = []
                    emot_dict[(word, tag)].append(label)
        for key, result in emot_dict.items():
            emot_dist = nltk.FreqDist(result)
            result_dict = self.calc_label_distributions(emot_dist)
            emot_dict[key] = result_dict
        return emot_dict

    def score_emoticon_dict(self):
        total_dict = {}
        for key, tweet in self.tagged_tweets.items():
            score_dict = {
                "objective": 0.,
                "positive": 0.,
                "negative": 0.,
                "neutral": 0.}
            for each in tweet:
                for label in self.emoticon_prob.get(each, []):
                    if label != "occurences":
                        score_dict[label] += self.emoticon_prob[each][label]
            total_dict[key] = score_dict
        return total_dict

    def get_ngram_prob(self):
        # calculates the polarity distribution for each ngram
        # the length of the ngram and pos/word inclusion determine by class
        # settigs

        word_dict = {}
        for key, tweet in self.tagged_tweets.items():

            word_list = self.ngramify(tweet)

            label = self.instances[key].label
            for ngram in word_list:
                if ngram not in word_dict:
                    word_dict[ngram] = []
                word_dict[ngram].append(label)
        for key, result in word_dict.items():
            label_distributions = nltk.FreqDist(result)
            result_dict = self.calc_label_distributions(label_distributions)
            word_dict[key] = result_dict
        return word_dict

    def calc_label_distributions(self, label_distributions, log=True):
            # helper function to create results for length and ngram probs
        result_dict = {}
        for label, occurences in label_distributions.items():
            raw_score = float(occurences) / float(label_distributions.N())
            overall = self.total_distribution[label]
            if log:
                logscore = math.log(raw_score / overall)
                result_dict[label] = logscore
            else:
                result_dict[label] = raw_score
        result_dict["occurences"] = label_distributions.N()
        return result_dict

    def score_ngram_dict(self, prob_dict):
        # aggregates values for each tweet by iterating through tweets and
        # finding the corresponding value in self.ngram_prob
        total_dict = {}

        for key, tweet in self.tagged_tweets.items():
            word_list = self.ngramify(tweet)
            # could add "occurences":0 here and then where the if != occurences
            score_dict = {
                "objective": 0.,
                "positive": 0.,
                "negative": 0.,
                "neutral": 0.}

            for ngram in word_list:
                if ngram in prob_dict:
                    for label in prob_dict[ngram]:
                        if label != "occurences":  # and label!="neutral":
                        # can add occurences here
                            score_dict[label] += prob_dict[ngram][label]
                else:
                    # no ngram found:
                    continue

            total_dict[key] = score_dict
        return total_dict

    def eval_ngrams(self):
        # printing function to evaluate ngram work
        right = 0
        wrong = 0
        buf = 80 * "~"
        if self.display:
            print "{0}\nNGRAM EVALUATION\n".format(buf)
        for key, score in self.ngram_scores.items():
            correct = self.instances[key].label
            ranked = self.ranked(score)
            choice = ranked[0]
            answer = choice == correct
            if answer:
                right += 1
            else:
                wrong += 1

            if self.display:
                if not answer:
                    print "k {0}\t g={1}\tc={2}".format(key, choice, correct)

            # if self.display:
            #	if not answer:
            # print rank,each,score[each]
                #	tw = self.ngramify(self.tagged_tweets[key])
                #	for each in tw:
                #		print each,"\t",self.ngram_prob[each]

        if self.display:
            print "NGRAM RESULTS:\nright: {0}\nwrong :{1}\n{2}\n".format(right, wrong, buf)
        return right, wrong

    def build_ct_dict(self):
        # builds a context target dict
        # see analyze tweets original for details
        results = {}
        for key, tweet in self.tagged_tweets.items():
            start = self.instances[key].startpos
            end = self.instances[key].endpos
            if end < len(tweet):

                if start == end:
                    target_phrase = tweet[end]

                    context = tweet[:start] + tweet[:end]
                    context = self.ngramify(context)
                else:

                    target_phrase = self.ngramify(tweet[start:end])
                    context = tweet[:start] + tweet[end:]
                    context = self.ngramify(context)
                results[key] = {"target": target_phrase, "context": context}
        return results

    def get_length_prob(self):
        # creates a dictionary keyed by target length
        # the values represent the distribution of polarity for a given phrase
        # length

        length_dict = {}
        for key, instance in self.instances.items():
            if len(instance) not in length_dict:
                length_dict[len(instance)] = []
            length_dict[len(instance)].append(instance.label)
        for key, result in length_dict.items():
            label_distributions = nltk.FreqDist(result)

            result_dict = self.calc_label_distributions(label_distributions)
            length_dict[key] = result_dict
        return length_dict

    def score_length_dict(self, length_dict):
        # assigns a length score to each key in tagged_tweet
        # length dict from self.get_length_prob()
        total_dict = {}
        for key, tweet in self.tagged_tweets.items():
            val = length_dict[len(self.instances[key])]
            if "occurences" in val:
                val.pop("occurences")
            total_dict[key] = val
        return total_dict

    def score_context(self):
        total_context = {}
        total_target = {}
        for key, parts in self.ct_dict.items():
            context_score_dict = {
                "objective": 0.,
                "positive": 0.,
                "negative": 0.,
                "neutral": 0.}
            target_score_dict = {
                "objective": 0.,
                "positive": 0.,
                "negative": 0.,
                "neutral": 0.}
            context = parts["context"]
            target = parts["target"]
            for ngram in context:
                for label in self.ngram_prob.get(ngram, []):
                    if label != "occurences":
                        context_score_dict[
                            label] += self.ngram_prob[ngram][label]
            for ngram in target:
                for label in self.ngram_prob.get(ngram, []):
                    if label != "occurences":
                        target_score_dict[
                            label] += self.ngram_prob[ngram][label]
            total_context[key] = context_score_dict
            total_target[key] = target_score_dict
        return total_context, total_target

    def eval_contexts(self):
        buf = 80 * "-"
        if self.display:
            print "{0}\nCONTEXT / TARGET EVALUATION".format(buf)

        cor_context = 0
        cor_target = 0
        cor_both = 0
        wrong = 0
        for key in self.context_scores:
            correct = self.instances[key].label
            context_label = self.ranked(self.context_scores[key])[0]
            target_label = self.ranked(self.target_scores[key])[0]
            if context_label == correct and target_label == correct:
                cor_both += 1
            elif context_label == correct:
                cor_context += 1
            elif target_label == correct:
                cor_target += 1
            else:
                terr = self.ct_dict[key]["target"]
                cerr = self.ct_dict[key]["context"]
                wrong += +1
                if self.display:
                    print "MISCLASSIFED key= {3}\nc: {0}\tt: {1}\tans: {2}\n".format(context_label, target_label, correct, key)
                    # print "c = {0}\n\nt = {1}\n".format(cerr,terr)
        right = cor_context + cor_target + cor_both
        if self.display:
            print "context_target results:"
            print "cor_both: {0}\ncor_context: {1}\ncor_target: {2}\ntotalright: {4}\nwrong: {3}\n{5}\n".format(cor_both, cor_context, cor_target, wrong, right, buf)
        # return (cor_context,cor_target,cor_both,right,wrong)
        return right, wrong

    def check_repeat_letters(self, word):
        if "http" in word or "@" in word:
            return []
        res = re.findall(r'((\w)\2{2,})', word)
        if res:
            rep = res[0][0]

            if rep.isdigit():
                return []
            if rep == "www":
                return []
            print word, res
        return res

    def get_repeat_letter_prob(self):
        repeat_dict = {}
        dist_dict = {}
        for key, tweet in self.tagged_tweets.items():
            label = self.instances[key].label
            for word, tag in tweet:
                if self.check_repeat_letters(word.lower()):
                    if word not in repeat_dict:
                        repeat_dict[word] = []
                    repeat_dict[word].append(label)

        for key, result in repeat_dict.items():
            label_dist = nltk.FreqDist(result)
            result_dict = self.calc_label_distributions(label_dist)
            dist_dict[key] = result_dict

        return repeat_dict, dist_dict
