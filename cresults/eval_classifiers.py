import os

# curr base_line with 1283 train set = .706

def get_classifier_accuracy(dir_path,baseline=.5):
	dir_path = dir_path
	baseline = float(baseline)
	data_files = os.listdir(dir_path)
	acc_classifiers = {}
	for each in data_files:
		class_key = each.replace(".txt","")
		acc_classifiers[class_key] = {}
		data_path = dir_path+each
		with open(data_path) as data:
			for row in data:
				results = row.split(" ")
				if len(results) == 4:
					alpha = float(results[0])
					num_total = int(results[1])
					num_correct = int(results[2])
					percent = float(results[3])
				if percent >= baseline:
					acc_classifiers[class_key][alpha] = (num_total,num_correct,percent)
					#print "key: {0}\n \t--->alpha: {1}  tot: {2}  cor: {3}  percent {4}".format(class_key,alpha,num_total,num_correct,percent)
				else:
					print "get_classifier_accuracy rejecting {0}".format(row)
	return acc_classifiers


def get_existing_classifiers(sub="pickles",selection="all",mode="ngram"):
	try:
	    pic_path = "cresults/{0}/{1}/{2}".format(sub,selection,mode)
	    data_files = os.listdir(pic_path)
	    data_files =[each.replace(".pkl","") for each in data_files]
	except:
	 	print "no existing found @ {0}\n".format(pic_path)
	 	data_files = []
	return data_files

#	with 
