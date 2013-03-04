import os

# curr base_line with 1283 train set = .706

def get_classifier_accuracy(dir_path,baseline):
	dir_path = dir_path
	baseline = float(baseline)
	data_files = os.listdir(dir_path)
	acc_classifiers = {}
	for each in data_files:
		print each
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
	return acc_classifiers




#	with 
