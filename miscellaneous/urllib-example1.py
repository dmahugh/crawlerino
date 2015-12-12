# https://www.youtube.com/watch?v=GEshegZzt3M
# Only handles a single page.

import urllib.request
import urllib.parse
import re

url = 'http://mahugh.com'

req = urllib.request.Request(url)
resp = urllib.request.urlopen(req)
respData = resp.read()

paragraphs = re.findall(r'<p>(.*?)</p>', str(respData))

for eachP in paragraphs:
    print(eachP)
