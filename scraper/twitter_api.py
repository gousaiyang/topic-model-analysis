import json
import os
import re
import time
import urllib

import colorlabels as cl
import twitter
from decouple import config

from util import merge_whitespaces

DEBUG_FILENAME = os.path.join('twdata', 'twdebug.txt')
MAX_COUNT_PER_REQ = 100

credentials = {
    'consumer_key': config('CONSUMER_KEY'),
    'consumer_secret': config('CONSUMER_SECRET'),
    'access_token_key': config('ACCESS_TOKEN_KEY'),
    'access_token_secret': config('ACCESS_TOKEN_SECRET')
}

twapi = twitter.Api(**credentials, application_only_auth=True)


def get_full_text(tweet):
    if tweet.retweeted_status:
        return tweet.retweeted_status.full_text
    else:
        return tweet.full_text


def get_hashtags(tweet):
    for hashtag in tweet.hashtags:
        if hashtag.text:
            yield hashtag.text


def parse_source(source):
    result = re.findall(r'<a href="(.*?)" rel="nofollow">(.*?)</a>', source)[0]
    return '%s(%s)' % (result[1], result[0])


def twapi_search_page(query, count, max_id=None, *, sleep_time, **kwargs):
    debugfile = open(DEBUG_FILENAME, 'a', encoding='utf-8')

    kwargs.update({'q': query, 'count': count, 'max_id': max_id,
                   'result_type': 'recent', 'tweet_mode': 'extended'})
    query = urllib.parse.urlencode(kwargs)

    for tweet in twapi.GetSearch(raw_query=query):
        debugfile.write(json.dumps(tweet.AsDict(), indent=4,
                                   ensure_ascii=False) + '\n')

        yield {
            'id': tweet.id_str,
            'text': merge_whitespaces(get_full_text(tweet)),
            'hashtags': ','.join(get_hashtags(tweet)),
            'created_at': tweet.created_at,
            'retweeting_id': tweet.retweeted_status.id_str
            if tweet.retweeted_status else None,
            'quoting_id': tweet.quoted_status_id_str,
            'replying_id': tweet.in_reply_to_status_id,
            'favorite_count': tweet.favorite_count,
            'retweet_count': tweet.retweet_count,
            'lang': tweet.lang,
            'source': parse_source(tweet.source),
            'user_id': tweet.user.id_str,
            'user_name': merge_whitespaces(tweet.user.name),
            'user_screen_name': merge_whitespaces(tweet.user.screen_name),
            'user_description': merge_whitespaces(tweet.user.description),
            'user_lang': tweet.user.lang,
            'user_location': merge_whitespaces(tweet.user.location),
            'user_verified': int(bool(tweet.user.verified)),
            'user_created_at': tweet.user.created_at,
            'user_favourites_count': tweet.user.favourites_count,
            'user_followers_count': tweet.user.followers_count,
            'user_friends_count': tweet.user.friends_count,
            'user_statuses_count': tweet.user.statuses_count,
        }

    debugfile.close()

    time.sleep(sleep_time)  # Rate limit


def twapi_search(query, count, *, sleep_time=0, **kwargs):
    with open(DEBUG_FILENAME, 'w'):
        pass

    last_id = None
    num_fetched = 0

    while count > 0:
        next_count = min(count, MAX_COUNT_PER_REQ)
        next_id = last_id - 1 if last_id is not None else None
        data = list(twapi_search_page(query, next_count, next_id,
                                      sleep_time=sleep_time, **kwargs))

        if not data:
            cl.warning('No more data can be retrieved, terminating...')
            return

        for item in data:
            last_id = int(item['id'])
            yield item

        num_fetched += len(data)
        count -= len(data)

        cl.info('Current number of records fetched: %d' % num_fetched)
