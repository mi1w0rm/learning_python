import json
import time
from urllib import request

from urllib.error import HTTPError

candidate_proxies = ['10.10.18.133:1080']

for proxy in candidate_proxies:
    print('Trying HTTP proxy %s\t......' % proxy)
    try:
        # test proxy connection
        # result = request.urlopen("http://www.google.com")

        twitter_target = '@AircraftSpots'

        resp = request.urlopen("https://api.twitter.com/1.1/search/tweets.json?q=%s" % twitter_target)

        print('Got %s using proxy %s\t......' % twitter_target, proxy)

        tweet_dic = json.load(resp)

        break
    except HTTPError as httpe:

        print('Exception %s,Trying next proxy in 5 seconds' % httpe.code)

        time.sleep(5)
