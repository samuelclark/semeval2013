


def parse_polarity_file(fname):
	# parses subclues.tff
	# returns {word:<PolarityWord Instance>}
	polarity_dict = {}
	with open(fname) as f:
		for line in f:
			try:
				word_info = line.split()
				if word_info.count("len1=1")>1:
					word_info.remove("len1=1")
				cleaned_info = [element.split("=")[1] for element in word_info if len(element.split("="))==2]
				typ,length,word,pos,stem,polarity = cleaned_info
				polarity_word = PolarityWord(type=typ,length=length,word=word,pos=pos,stem=stem,polarity=polarity,source="weibe")
				polarity_dict[(polarity_word.word,polarity_word.pos)] = polarity_word
				

			except ValueError as e:
				print e
		s = "loaded polarity dict from {0}\n".format(f)
		print s
		return polarity_dict


class PolarityWord(object):
	# This class is a wrapper for each word object in the Weib subj corpus

	def __init__(self,**kargs):
		self.type = kargs["type"]
		self.length = kargs["length"]
		self.word = kargs["word"]
		self.pos = kargs["pos"]
		self.stem = kargs["stem"]
		self.polarity = kargs["polarity"]
		self.source = kargs["source"]
		self.usage_polarity = []

		self.value = 0 #THIS NEEDS TO BE UPDATED
		self.__set_initial_value() # his updates it 

	def __str__(self,buf=80*"-"):
		class_str = "{0}\nword:{1}\npolarity:{2}\nvalue:{3}\ntype:{4}\nlen:{5}\npos:{6}\nstem:{7}\n".format(buf,self.word,self.polarity,self.value,self.type,self.length,self.pos,self.stem)
		return class_str

	def __set_initial_value(self):
		if self.polarity == "positive":
			self.value = 1
		elif self.polarity == "negative":
			self.value = -1

if __name__ == '__main__':
	pdic = parse_polarity_file("subclues.tff")




class ScoredTweet(object):

	def __init__(self,**kargs):
		self.key = kargs["key"]
		self.word_score = kargs["word_prob"]
		self.length_score= kargs["length_prob"]
		self.polarity_score = kargs["polarity_score"]
		self.correct_label = kargs["correct_label"]
		self.ratio_score = self._get_word_score_ratios()
		self.ranked_dict = self._rank_all_scores()

	def __str__(self):
		buf = "~"*80
		class_str = "{3}\nScoredTweet:\nkey:{4}\nword_score:{0}\nlength_score{1}\npolarity_score{2}\ncorrect_label:{5}\n".format(self.word_score,self.length_score,self.polarity_score,buf,self.key,self.correct_label)
		return class_str


	def _get_word_score_ratios(self):
		# uses self.word score to show the ratio of <polairt>/total
		# useful in helping understand the word_scores
		# generally ratios >.5 indicate a likely polarity lable other than objective.

		result = {}
		total = sum(self.word_score.values())
		for each in self.word_score:

			result[each] = result.get(each,0)+(self.word_score[each]/total)
		return result

	def _rank_score_dict(self,target_dict):
		# method to sort {"poliarty":value} dicts into [(key1,val1),(key2,val2),etc...]
		 sorted_keys = sorted(target_dict,key = lambda x: target_dict[x],reverse = True)
		 rank_list = [(key,target_dict[key]) for key in sorted_keys]
		 return rank_list

	def _rank_all_scores(self):
		# dict containing all the ranked dictionaries belonging to the ScoredTweet class
		ranked_words = self._rank_score_dict(self.word_score)
		ranked_length = self._rank_score_dict(self.length_score)
		ranked_length = ranked_length[1:] # ugly way to get rid of "occurences":value
		ranked_polarity = self._rank_score_dict(self.polarity_score)
		ranked_ratios = self._rank_score_dict(self.ratio_score)
		return {"ranked_words":ranked_words,"ranked_length":ranked_length,"ranked_polarity":ranked_polarity,"ranked_ratios":ranked_ratios}




class EvaluateScore(object):

	def __init__(self,**kargs):
		self.scored_dict = kargs["scored_dict"]


	def __str__(self):
		score_list =[str(scored) for key,scored in self.scored_dict.items()]
		return "\n".join(score_list)

	def get_score_bykey(self,key):
		try:
			return self.scored_dict[key]
		except:
			err = "key {0} not in scored_dict\n".format(key)
			print err

	def evaluate_by_ratio(self):
		outfile = open("ratio_results.txt","w")
		outfile.write("guessed_tag\tratio_value\tactual_tag\tcorrect\n")
		count = 0
		total = len(self.scored_dict)
		for key,scored in self.scored_dict.items():
			correct = scored.correct_label
			if scored.ratio_score["objective"]<.8:
				guess,value = scored.ranked_dict["ranked_ratios"][1]
			else:
				guess,value = scored.ranked_dict["ranked_ratios"][0]
			result = (guess == correct)
			if result:
				count+=1
			score_str = "{0}\t{1}\t{2}\t{3}\n".format(guess,value,correct,result)
			print score_str
			outfile.write(score_str)
		percent_right = float(count)/float(total)
		final_str =  "RATIO RESULT {0}/{1} = {2}%\n".format(count,total,percent_right)
		print final_str
		outfile.write(final_str)
		outfile.close()

	def evaluate_by_length(self):
		outfile = open("lenth_results.txt","w")
		outfile.write("guessed_tag\tlength_value\tactual_tag\tcorrect\n")
		count = 0
		total = len(self.scored_dict)
		for key,scored in self.scored_dict.items():
			correct = scored.correct_label
			if scored.length_score["objective"]<.7:
				guess,value = scored.ranked_dict["ranked_length"][1]
			else:
				guess,value = scored.ranked_dict["ranked_length"][0]
			result = (guess == correct)
			if result:
				count+=1
			score_str = "{0}\t{1}\t{2}\t{3}\n".format(guess,value,correct,result)
			print score_str
			outfile.write(score_str)
		percent_right = float(count)/float(total)
		final_str =  "RATIO RESULT {0}/{1} = {2}%\n".format(count,total,percent_right)
		print final_str
		outfile.write(final_str)
		outfile.close()











