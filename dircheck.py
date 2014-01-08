import os


def checkDir(path=os.getcwd(), main="cresults",
             sub="pickles", selection="all", mode="ngram"):
    results_path = "{0}/{1}/{2}/{3}".format(main, sub, selection, mode)
    print results_path
    return os.path.isdir(results_path)


def createDir(path=os.getcwd(), main="cresults",
              sub="pickles", selection="all", mode="ngram"):
    results_path = "{0}/{1}/{2}/{3}".format(main, sub, selection, mode)
    try:
        print "creating {0}\n".format(results_path)
        os.mkdir(results_path)
    except OSError as error:
        print results_path
        print error
