# tw_search.py

import json, sys
import config
from datetime import datetime as dt
import pytz
from requests_oauthlib import OAuth1Session
from numpy import random as nrnd


API_KEY = config.API_KEY
API_SECRET = config.API_SECRET
ACCESS_TOKEN = config.ACCESS_TOKEN
ACCESS_TOKEN_SECRET = config.ACCESS_TOKEN_SECRET
twitter = OAuth1Session(API_KEY, API_SECRET, ACCESS_TOKEN, ACCESS_TOKEN_SECRET)


def parse_date(date_original):
    date_formatted = dt.strptime(date_original, "%a %b %d %H:%M:%S %z %Y")
    return date_formatted

def search_tweets(keyword):
    url = "https://api.twitter.com/1.1/search/tweets.json"
    req = twitter.get(url, params={'q': keyword})

    if req.status_code == 200:
        timeline = json.loads(req.text)
        return timeline
    else:
        print("ERROR: %d" % req.status_code)

def find_tweet(tw_id):
    url = "https://api.twitter.com/1.1/statuses/show.json"
    req = twitter.get(url, params={'id': tw_id})
    if req.status_code == 200:
        tweet = json.loads(req.text)
        return tweet
    else:
        print("ERROR: %d" % req.status_code)

def get_rter_list(target_url, deadline):
    target_id = str(target_url[(target_url.rfind("/") + 1): ])
    target_tweet = find_tweet(target_id)
    tweeter_sn = target_tweet['user']['screen_name']
    # first page
    keyword = target_tweet['text'] + " filter:retweets @" + tweeter_sn + " since_id:" + target_id + " until:" + deadline
    rts = search_tweets(keyword)
    rter_ids = []
    for rt in rts['statuses']:
        rter_ids.append(rt['user']['screen_name'])
    max_id = str(rts['statuses'][-1]['id'] - 1)
    max_time = parse_date(rts['statuses'][0]['created_at'])
    # rest pages
    while True:
        keyword = target_tweet['text'] + " filter:retweets @" + tweeter_sn + " since_id:" + target_id + ' max_id:' + max_id + " until:" + deadline
        rts = search_tweets(keyword)
        tmp_n_found = 0
        for rt in rts['statuses']:
            rter_ids.append(rt['user']['screen_name'])
            tmp_n_found += 1
        # print(tmp_n_found)
        if tmp_n_found > 0:
            max_id = str(rts['statuses'][-1]['id'] - 1)
            max_time = parse_date(rts['statuses'][0]['created_at'])
        else:
            break
        # print(max_time)
    return rter_ids


if __name__ == '__main__':
    DEADLINE = "2018-12-31_23:59:59_JST"
    argvs = sys.argv
    if len(argvs) != 2:
        print("引数で調べたいツイートのURLを指定してください")
    else:
        rter_ids = get_rter_list(argvs[1], DEADLINE)
        # print(rter_ids)
        n_rter = len(rter_ids)
        print("%d人がRTしました" % n_rter)
        winner = rter_ids[nrnd.randint(n_rter)]
        print("おめでとうございます！%sさんが当選されました" % winner)