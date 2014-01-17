import random
import nltk
import cPickle


class Classifier:

    """
        An abstraction of the nltk.classifier class.
        Features are extracted from <weets and labels are drawn from <instances>
        The classifier (NLTKNaiveBayesClassifier) in self.classifier

        see kargs in evaluate_classifier for input description
    """

    def __init__(self, **kargs):
        self.tweets = kargs["tweets"]
        self.instances = kargs["instances"]
        self.keys = kargs["keys"]
        self.selection = kargs["selection"]
        self.debug = False  # True for more detailed output
        if "model" in kargs:
            self.model = kargs["model"]
        else:
            self.model = False
        self.model = False
        self.count = 0
        self.num_items = len(self.keys)
        # the list of {feature: label} combintions for each tweet
        self.featureset = None
        # training set 70-80% of documents(bumped to 100% in production) --
        # defined by split in prepare_features
        self.train_set = None
        # ~10-15%
        self.dev_set = None
        # 10%
        self.test_set = None
        self.split1 = None
        self.split2 = None
        self.classifier = None
        # metrics for classifier performance
        self.test_keys = None
        self.train_keys = None
        self.trained = False
        self.classiifer_acc = None
        self.classifier_err = None
        self.best_features = None
        # voting information
        self.alpha_acc = None
        self.baseline = None

        # this is for testing should be done elsewhere

    def prepare_features(self, split=.8):
        """
            Prepares the featureset to be used by the classifier
            Partitions documents into train, dev, test sets

            input:
                split = % of documents to allocate to training set
        """

        self.featureset = self.build_featureset(self.num_items)
        self.split1, self.split2 = len(
            self.featureset) / 3, 2 * len(self.featureset) / 3
        if self.debug:
            self.train_set = self.featureset[:self.split1]
            self.dev_set = self.featureset[self.split1:self.split2]
            self.test_set = self.featureset[self.split2:]
            self.test_keys = self.keys[self.split2:]
        elif self.model:
            # set feature_set and training_keys
            # training_keys determine the keys used for training
            self.train_set = self.featureset
            self.test_set = []
            self.test_keys = []
            self.train_keys = self.keys
        else:
            # partition
            splitidx = int(split * len(self.featureset))
            self.train_set = self.featureset[:splitidx]
            self.test_set = self.featureset[splitidx:]
            self.test_keys = self.keys[splitidx:]
            self.train_keys = self.keys[:splitidx]

    def train_classifier(self):
        """
            Trains classifier using training set, results in a trained self.classifier objects
        """

        # make sure we have a featureset
        if not self.featureset:
            self.prepare_features()
        print "* Training {1}\tsize(training_set)  = {0}\n".format(len(self.train_set), self.id)
        # Initialize a classifier
        self.classifier = nltk.NaiveBayesClassifier.train(self.train_set)
        if not self.model:
            # get classifier accuracy and top features
            self.classifier_acc = self.get_classifier_accuracy()
            print self.classifier_acc
            if self.debug:
                self.classifier_error = self.collect_errors(self.classifier)
            self.best_features = self.classifier.most_informative_features(25)
            if self.debug:
                self.classifier.show_most_informative_features(10)
        # indicate that the classifier has finished training
        self.trained = True

    def create_validation_sets(self, featureset, folds):
        """
            partition featureset into cross validation sets

            input:
                 feature_set: list of features
                folds: number of coss-validation folds
        """

        fsets = {}
        split = len(featureset) / folds
        startidx = 0
        for segment in range(1, folds + 1):
            splitidx = split * segment
            print startidx, splitidx
            fsets[segment] = featureset[startidx:splitidx]
            startidx = splitidx

        return fsets

    def cross_validate(self, folds=5):
        """
            cross validate results across n folds

            input:
                folds: # of folds
        """

        results = []
        fsets = self.create_validation_sets(self.featureset, folds)
        for idx in fsets.keys():
            train_set = []
            for key in fsets.keys():
                if key == idx:
                    test_set = fsets[idx]
                else:
                    train_set += fsets[idx]
            classifier = nltk.NaiveBayesClassifier.train(train_set)
            accuracy = nltk.classify.accuracy(classifier, test_set)
            results.append(accuracy)
        return results

        # build train set
            # for each key, pair all other 4 as training set
            # for key in keys if not this key add to training
        # build test set
        # train
        # test
        # accuracy
        # {num: <set>}

    def show_features(self, num=10):
        self.classifier.show_most_informative_features(num)

    def get_label(self, key):
        return self.instances[key].label

    def get_classifier_accuracy(self):
        # returns the accuracy of the classifier as determined by the test_set
        acc = nltk.classify.accuracy(self.classifier, self.test_set)
        return acc

    def collect_errors(self, classifier):
        # helper method to collect the erros using the dev set
        errors = {}
        for fvector, tag in self.dev_set:
            guess = classifier.classify(fvector)
            if guess != tag:
                # print guess,tag,fvector,"\n\n"
                errors[(guess, tag)] = errors.get((guess, tag), 0) + 1

        return errors

    def ngramify(self, word_list):
        """
            Tranforms word_list into unigrams, bigrams, trigrams

            input:
                list of words
        """

        # creates an ngram from a word_list based on class settings
        mode = self.mode
        pos = self.inclued_pos
        word = self.include_word
        if word and pos:
            selection = [(w.lower(), p) for w, p in word_list]
        elif word:
            selection = [w.lower() for w, p in word_list]
        elif pos:
            selection = [p for w, p in word_list]

        if mode == "unigrams":
            word_list = selection
        elif mode == "bigrams":
            word_list = nltk.bigrams(selection)
        elif mode == "trigrams":
            word_list = nltk.trigrams(selection)
        return word_list

    def get_selected_text(self, tweet):
        """
            get ngramlists for either (1) whole tweet (2) the target (3) the context
        """
        if self.selection == "all":
            word_list = self.ngramify(tweet.tagged_text)
        elif self.selection == "target":
            word_list = self.ngramify(tweet.target)
        elif self.selection == "context":
            word_list = self.ngramify(tweet.context)
        return word_list

    def classify(self, key, prob=True):
        """
            returns a classification score from the trained model
            set prop = False for binary return
        """
        if self.trained:
            feature_vector = self.build_feature_vector(key)
            classification, score = self.classifier.classify(
                feature_vector), self.classifier.prob_classify(feature_vector)
            return classification, score
        else:
            print "{0} NOT TRAINED!".format(self.id)

    def build_featureset(self, num, keys=[]):
        """
            Constructs a feature_vector for each tweet.
                This calls build_feature_vector which is subclassed for each
                feature

                input:
                    num = limiting number of tweets
        """
        print "creating featureset of {0} tweets\n".format(num)
        if not keys:
            featureset = [(self.build_feature_vector(key), self.get_label(key))
                          for key in self.keys[:num]]
        else:
            featureset = [(self.build_feature_vector(key), self.get_label(key))
                          for key in keys]

        # returns (feature_dict,label)
        return featureset

    def build_feature_vector(self, key):
        # this should get overridden when subclassed!
        # see classifiers/
        return

    def save(self, descrip="foo.txt"):
        """
            saves a classifier to a pickle file
            after fully trained different instances of these are saved as production instances
            and then used in combination with eachother
        """

        outfile = open(descrip, "w")
        if self.classifier:
            cPickle.dump(self.classifier, outfile)
        else:
            print "no classifier to pickel\n"
