import contextlib
import datetime
import os
import sys

import colorlabels as cl
from decouple import config

from main import data_retriever, retweets_recover, user_info_retriever
from util import TimeMeasure, csv_reader, data_source_file

# Adjust working directory to current script directory (project root).
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Set NO_COLOR=True or NO_COLOR=1 to disable color output.
if config('NO_COLOR', cast=bool, default=False):
    cl.config(color_span=0)

# Parameters
DAYS = 7

# Get `DAYS` from `argv`.
if len(sys.argv) > 1:
    with contextlib.suppress(ValueError):
        DAYS = max(int(sys.argv[1]), 1)

DATEBACK = datetime.timedelta(days=DAYS)  # The date range to collect data.
QUERY = '"java"'  # Twitter search query string.
PROXY = None  # The proxy used to collect Twitter data. (None or 'http://xxx')
TWSCRAPE_POOLSIZE = 20  # Number of processes for twitterscraper.


def get_usernames(tweets_file):
    return list(set(row['user'] for row in
                    csv_reader(data_source_file(tweets_file))))


def main():
    tweets_file = 'twdata-java.csv'
    userinfo_file = 'twusers-java.csv'

    # Retrieve (Scrape + Recover Retweets + Get User Info)
    data_retriever('twitterscraper', QUERY, tweets_file, lang='en',
                   proxy=PROXY, remove_duplicates=False,
                   twscrape_poolsize=TWSCRAPE_POOLSIZE,
                   twscrape_begindate=datetime.date.today() - DATEBACK)
    tweets_file_recovered = retweets_recover(tweets_file)
    usernames = get_usernames(tweets_file_recovered)
    user_info_retriever(usernames, userinfo_file)


if __name__ == '__main__':
    with TimeMeasure('crawl_task'):
        main()
