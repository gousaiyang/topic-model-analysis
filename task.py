import datetime
import time

import colorlabels as cl
from decouple import config

from main import (data_retriever, plot_diff_topics, retweets_recover,
                  text_preprocessor_twlda, twitter_lda, user_info_retriever,
                  visualization_twlda)
from util import (TimeMeasure, csv_reader, data_source_file, pipe_encoding,
                  retry_until_success)

if config('NO_COLOR', cast=bool, default=False):
    cl.config(color_span=0)

DATEBACK = datetime.timedelta(weeks=1)
QUERY = '"java"'
KEYWORD = 'java'
PROXY = None
TWSCRAPE_POOLSIZE = 20
MIN_TOPICS = 6
MAX_TOPICS = 30
ITERATIONS = 4000


def get_usernames(tweets_file):
    return list(set(row['user'] for row in
                    csv_reader(data_source_file(tweets_file))))


def main():
    tag = time.strftime('java-%Y%m%d%H%M%S')
    tweets_file = 'twdata-%s.csv' % tag
    userinfo_file = 'twusers-%s.csv' % tag
    num_topics_range = list(range(MIN_TOPICS, MAX_TOPICS + 1))

    # Retrieve
    retry_until_success(data_retriever, 'twitterscraper', QUERY, tweets_file,
                        lang='en', proxy=PROXY, remove_duplicates=False,
                        twscrape_poolsize=TWSCRAPE_POOLSIZE,
                        twscrape_begindate=datetime.date.today() - DATEBACK)
    tweets_file_recovered = retry_until_success(retweets_recover, tweets_file)
    usernames = retry_until_success(get_usernames, tweets_file_recovered)
    retry_until_success(user_info_retriever, usernames, userinfo_file)

    # Preprocess
    retry_until_success(text_preprocessor_twlda, tweets_file_recovered[:-4],
                        tweet_min_length=2, user_min_tweets=1,
                        remove_duplicates=True)

    # Train
    for topics in num_topics_range:
        retry_until_success(twitter_lda, output_desc='%s-%d' % (tag, topics),
                            topics=topics, iteration=ITERATIONS,
                            show_console_output=False)

    # Analyze
    retry_until_success(plot_diff_topics, num_topics_range, tag,
                        r'Perplexity is ([\d.]+)', pipe_encoding)
    for topics in num_topics_range:
        retry_until_success(visualization_twlda, KEYWORD,
                            '%s-%d' % (tag, topics), '%s-%d' % (tag, topics),
                            userinfo_file, open_browser=False)


if __name__ == '__main__':
    with TimeMeasure('task_total'):
        main()
