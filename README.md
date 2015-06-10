semeval2013
===========

Code from SemEval2013 polarity disamgbiguation task

This is the source code for the classification system I submitted to Semeval 2013 Task2. 

The tasks were:
Task A:
"Given a message containing a marked instance of a word or a phrase, determine whether that instance is positive, negative or neutral in that context. The boundaries for the marked instance will be provided, i.e., this  is a classification task, NOT an entity recognition task."

Task B:

"Given a message, decide whether the message is of positive, negative, or neutral sentiment. For messages conveying both a positive and negative sentiment, whichever is the stronger sentiment should be chosen."


Our submission (I worked under the guidance of Richard Wicentowski (Swat CS) focused on combining multiple feature-based niave bayes classifiers by estimating their accuracy at differing alpha levels (where alpha P(positive) - P(negative). An intelligent voting system combined the vote from each classifier to generate a more accurate polarity prediction.


The paper was published in SemEval2013 Volume 2 (http://www.aclweb.org/anthology/S13-2#page=461)
