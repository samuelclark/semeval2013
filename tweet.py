import utils
import bs4
import json
import urllib
import StringIO
import csv
import sys


def get_tweet_text(tweet_html):
    text = None

    if tweet_html == None:
        return text
    
    try:
        html = tweet_html.replace("</html>", "") + "</html>"
        soup = bs4.BeautifulSoup(html)

        ### NEW CODE
        for html in soup.find_all("p", "js-tweet-text"):
                text = html.get_text()
                break

        for j in soup.find_all("input", "json-data", id="init-data"):
                js = json.loads(j['value'])
                if(js.has_key("embedData")):
                        tweet = js["embedData"]["status"]
                        text  = js["embedData"]["status"]["text"]
                        break
    except Exception as e:
        sys.stderr.write("get_tweet_text()::Exception({0}): {1}\n".format(e.errno, e.strerr))

    if text is None:
        return None

    text = text.replace("\n","&#10;")
    return text



def as_csv(data):
    #HT http://goo.gl/gS5QM
    si = StringIO.StringIO();
    cw = csv.writer(si);
    cw.writerow(data);
    return si.getvalue().strip('\r\n');


class Tweet(object):

    def __init__(self, uid, sid):
        self.uid = uid
        self.sid = sid
        self.raw_html = None
        self.text = None
        self.tags = None
        self.url = "http://twitter.com/{0}/status/{1}".format(self.uid, self.sid)

    def __str__(self):

        if self.tags is None:
            text = self.text
        else:
            words = self.get_word_list()
            s = []
            for i in range(len(words)):
                s.append('{0}/{1}'.format(words[i], self.tags[i]))
            text = ' '.join(s)

        return as_csv([self.uid, self.sid, text])

    def get_html(self):
        return self.raw_html

    def set_html(self, raw_html):
        self.raw_html = raw_html
        self.set_text(get_tweet_text(self.raw_html))

    def get_text(self):
        return self.text

    def set_text(self, text):
        self.text = "Unavailable" if text is None else text

    def set_tags(self, tags):
        self.tags = [] if tags is None else tags

    def set_text_and_tags(self, wordlist, tags):
        text = ' '.join(wordlist)
        assert len(wordlist) == len(tags)
        self.set_text(text)
        self.set_tags(tags)

    def fetch(self):
        try:
            self.set_html(urllib.urlopen(self.url).read())
        except Exception as e:
            sys.stderr.write("tweet.fetch()::Exception({0}): {1}\n".format(e.errno, e.strerr))

    def fetched(self):
        if self.raw_html is None:
            return False

        return get_tweet_text(self.raw_html) is not None

    def get_tag_list(self):
        if self.tags:
            return self.tags[:]
        else:
            return None

    def get_word_list(self):
        if self.text:
            word_list = self.text.split()
            return word_list
        else:
            return None





