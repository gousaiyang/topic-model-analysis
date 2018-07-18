import os
import sys

import colorlabels as cl

from scraper import twapi_search, twscrape_search
from util import export_csv


def data_retriever(data_source, query, save_filename, lang='', twapi_max=None,
                   twapi_sleep_time=0, twscrape_poolsize=20,
                   twscrape_begindate=None):
    cl.section('Twitter Data Retriever')
    cl.info('Starting to retrieve query: %s' % query)
    cl.info('From data source: %s' % data_source)

    if data_source == 'official_standard_api':
        data = twapi_search(query, twapi_max, sleep_time=twapi_sleep_time,
                            lang=lang)
    elif data_source == 'twitterscraper':
        data = twscrape_search(query, lang=lang, poolsize=twscrape_poolsize,
                               begindate=twscrape_begindate)
    else:
        cl.error('Data source %r is not implemented' % data_source)
        sys.exit(-1)

    export_csv(data, os.path.join('twdata', save_filename))
