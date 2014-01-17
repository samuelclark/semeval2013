

class Instance(object):

    """
        This class wraps the Tweet instance meta-data provided in the TSV files
        Instances are indexed by a uid_sid key
    """

    def __init__(self, uid, sid, task='A', startpos=None,
                 endpos=None, key=None, keyword=None, label=None):
        self.uid = uid
        self.sid = sid
        self.key = key
        if task == 'A':
            # these determine the polarity context
            self.startpos = int(startpos)
            self.endpos = int(endpos)
            self.keyword = None
        else:

            self.length = None
            self.keyword = keyword

        self.label = label
        self.task = task

    def __len__(self):
        if self.startpos and self.endpos:
            return int(self.endpos) - int(self.startpos)
        else:
            return 0

    def __str__(self):
        buf = 80 * "*"
        resstr = "{0}\n{1}\t{2}\t{3}\t{4}-{5}\t{6}\t{7}\t{8}\n".format(
            buf,
            self.uid,
            self.sid,
            self.task,
            self.startpos,
            self.endpos,
            len(self),
            self.keyword,
            self.label)
        return resstr
