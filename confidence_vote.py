from vote import Vote
import math

class ConfidenceVote(Vote):
	def __init__(self,**kargs):
		Vote.__init__(self,tagged_tweets=kargs["tagged_tweets"],instances=kargs["instances"],classifiers=kargs["classifiers"])
		self.training=False
		self.alpha_result_dict = {}
		# this classifier dict is updated
		# this class will use the alpha_acc property of the classifier to make decisions on untagged tweets.
		# similar to vote class but seperate instance as the super is created to evaluate a known test set
		# the only difference between the classes is that classifier_dict has been updated with alpha_acc values



	def alpha_vote(self,key):
		res_dict = {}
		if key not in res_dict:
			res_dict[key] = {}
		for cid in self.scored_tweets[key]:

				score = self.get_score(key,cid)
				label = self.get_label(score)
				diff = abs(score["positive"] - score["negative"])
				alpha_acc = self.classifier_dict[cid].alpha_acc
				rounded = math.floor(diff*10)/10
				print diff,rounded
				if rounded in alpha_acc:
					if rounded not in res_dict[key]:
						res_dict[key][rounded] = []
					row = list(alpha_acc[rounded])
					row.append(label)
					res_dict[key][rounded].append(row)
				else:
					print "no conf"
		print res_dict
		return res_dict

	def get_label(self,score):
		ranked = sorted(score, key=lambda x:score[x],reverse=True)
		return ranked[0]


