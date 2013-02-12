#!/usr/bin/python

import sys
import urllib
import re
import json

from bs4 import BeautifulSoup

cache = {}

for line in open(sys.argv[1]):
	fields = line.rstrip('\n').split('\t')
	sid = fields[0]
	uid = fields[1]

	#url = 'http://twitter.com/%s/status/%s' % (uid, sid)
	#print url

        tweet = None
	text = "Unavailable"
	if cache.has_key(sid):
		text = cache[sid]
	else:
                try:
                        f = urllib.urlopen("http://twitter.com/%s/status/%s" % (uid, sid))
                        #Thanks to Arturo!
                        html = f.read().replace("</html>", "") + "</html>"
                        soup = BeautifulSoup(html)

                        for html in soup.find_all("p", "js-tweet-text"):
                                text = html.get_text()
                                cache[sid] = text
                                break

                        for j in soup.find_all("input", "json-data", id="init-data"):
                                js = json.loads(j['value'])
                                if(js.has_key("embedData")):
                                        tweet = js["embedData"]["status"]
                                        text  = js["embedData"]["status"]["text"]
                                        cache[sid] = text
                                        break
                except Exception:
                        continue

        if(tweet != None and tweet["id_str"] != sid):
                text = "Unavailable"
                cache[sid] = "Unavailable"
        text = text.replace('\n', ' ',)
        text = re.sub(r'\s+', ' ', text)
        #print json.dumps(tweet, indent=2)
        print "\t".join(fields + [text]).encode('utf-8')
