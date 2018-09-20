import contextlib
import datetime
import os
import time
import zipfile

import colorlabels as cl
from decouple import config

from main import (data_retriever, plot_diff_topics, retweets_recover,
                  text_preprocessor_twlda, twitter_lda, user_info_retriever,
                  visualization_twlda)
from util import (TimeMeasure, csv_reader, data_source_file, pipe_encoding,
                  report_file, retry_until_success)

# Adjust working directory to current script directory (project root).
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Set NO_COLOR=True or NO_COLOR=1 to disable color output.
if config('NO_COLOR', cast=bool, default=False):
    cl.config(color_span=0)

# Parameters
DATEBACK = datetime.timedelta(weeks=1)  # The date range to collect data.
QUERY = '"java"'  # Twitter search query string.
KEYWORD = 'Java'  # Only shown on the final report.
PROXY = None  # The proxy used to collect Twitter data. (None or 'http://xxx')
TWSCRAPE_POOLSIZE = 20  # Number of processes for twitterscraper.
MIN_TOPICS = 6  # Minimum number of topics for training.
MAX_TOPICS = 30  # Maximum number of topics for training.
ITERATIONS = 4000  # The number of iterations for training.
REPORT_ONLY_MINIMA = True  # Whether only to generate reports at minima points.


def get_usernames(tweets_file):
    return list(set(row['user'] for row in
                    csv_reader(data_source_file(tweets_file))))


def compress_report_files(tag, report_files):
    os.chdir(report_file(''))
    zipfilename = 'ldareport-%s.zip' % tag

    with zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in report_files:
            zf.write(f)

    for f in report_files:
        with contextlib.suppress(Exception):
            os.remove(f)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    cl.success('Report files archived into: %s' % zipfilename)
    return zipfilename


def main():
    tag = time.strftime('java-%Y%m%d%H%M%S')
    tweets_file = 'twdata-java.csv'
    userinfo_file = 'twusers-java.csv'
    num_topics_range = list(range(MIN_TOPICS, MAX_TOPICS + 1))

    # Retrieve (Scrape + Recover Retweets + Get User Info)
    data_retriever('twitterscraper', QUERY, tweets_file, lang='en',
                   proxy=PROXY, remove_duplicates=False,
                   twscrape_poolsize=TWSCRAPE_POOLSIZE,
                   twscrape_begindate=datetime.date.today() - DATEBACK)
    tweets_file_recovered = retweets_recover(tweets_file)
    usernames = get_usernames(tweets_file_recovered)
    user_info_retriever(usernames, userinfo_file)

    # Preprocess
    retry_until_success(text_preprocessor_twlda, tweets_file_recovered[:-4],
                        tweet_min_length=2, user_min_tweets=1,
                        remove_duplicates=True)

    # Train (with different number of topics)
    for topics in num_topics_range:
        cl.info('Running with %d topics' % topics)
        retry_until_success(twitter_lda, output_desc='java-%d' % topics,
                            topics=topics, iteration=ITERATIONS,
                            show_console_output=True)

    # Analyze (Perplexity Plot + HTML Reports + Compress)
    report_files = []
    plot_file, minima_points = plot_diff_topics(num_topics_range, 'java',
                                                r'Perplexity is ([\d.]+)',
                                                pipe_encoding)
    report_files.append(plot_file)
    report_points = minima_points if REPORT_ONLY_MINIMA else num_topics_range

    for topics in report_points:
        report_files.append(visualization_twlda(KEYWORD,
                                                'java-%d' % topics,
                                                '%s-%d' % (tag, topics),
                                                userinfo_file,
                                                open_browser=False))
    compress_report_files(tag, report_files)


if __name__ == '__main__':
    with TimeMeasure('task_total'):
        main()
