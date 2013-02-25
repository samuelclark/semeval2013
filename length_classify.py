from classify import Classifier


class LengthClassifier(Classifier):
	def __init__(self, **kargs):
		Classifier.__init__(self,tagged_tweets=kargs["tagged_tweets"],instances=kargs["instances"],merge=kargs["merge"])
		


	def build_feature_vector(self,key):
		# this extracts the lenth of the target phrase as a metric
		# ERROR IMPROVEMENTS
		# can we improve this to weight low tweets more towards pos/neg
		# lots of errors in this classification coming from this
		
		return {"target_length":len(self.instances[key])}
	# OTHER METRICS STUFF


	
		



