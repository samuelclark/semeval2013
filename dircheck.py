import os
def checkDir(dirname, path=os.getcwd(),sub='indiv'):
	results_path = os.path.join(path, 'cresults/{0}'.format(sub))
	print results_path
	pathtotest = os.path.join(results_path,dirname)
	print pathtotest
	return os.path.isdir(pathtotest)


def createDir(dirname, path=os.getcwd(),sub='indiv'):
	results_path = os.path.join(path, 'cresults/{0}'.format(sub))
	dirpath = os.path.join(results_path, dirname)
	try:
		print "creating {0}\n".format(dirpath)
		os.mkdir(dirpath)
	except OSError as error:
		print dirpath
		print error

