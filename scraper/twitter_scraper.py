import datetime

from twitterscraper import query_tweets

from util import merge_whitespaces


def twscrape_search(query, *, count=None, begindate=datetime.date(2006, 3, 21),
                    enddate=datetime.date.today(), poolsize=20, lang=''):
    result = query_tweets(query, limit=count, begindate=begindate,
                          enddate=enddate, poolsize=poolsize, lang=lang)

    data = ({
        'id': item.id,
        'text': merge_whitespaces(item.text),
        'timestamp': item.timestamp,
        'likes': item.likes,
        'retweets': item.retweets,
        'replies': item.replies,
        'url': item.url,
        'html': merge_whitespaces(item.html),
        'user': item.user,
        'fullname': merge_whitespaces(item.fullname)
    } for item in result)

    return sorted(data, key=lambda x: int(x['id']), reverse=True)
