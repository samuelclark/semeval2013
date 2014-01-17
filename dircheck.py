import os


def checkDir(path=os.getcwd(), main="cresults",
             sub="pickles", selection="all", mode="ngram"):
    """
        Helper function to check whether a pickle result exists
    """
    results_path = "{0}/{1}/{2}/{3}".format(main, sub, selection, mode)
    print results_path
    return os.path.isdir(results_path)


def createDir(path=os.getcwd(), main="cresults",
              sub="pickles", selection="all", mode="ngram"):
    """
        Helper function to create a diretory for results
    """
    results_path = "{0}/{1}/{2}/{3}".format(main, sub, selection, mode)
    try:
        print "creating {0}\n".format(results_path)
        os.mkdir(results_path)
    except OSError as error:
        print results_path
        print error
