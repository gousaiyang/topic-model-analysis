import os
import sys

import colorlabels as cl

from scraper import github_issue_org_fetch, twapi_search, twscrape_search
from util import data_source_file, export_csv


def data_retriever(data_source, query, save_filename, lang='', proxy=None,
                   twapi_max=None, twapi_sleep_time=0, twscrape_poolsize=20,
                   twscrape_begindate=None, ghapi_org=None, ghapi_since=None):
    cl.section('Data Retriever')
    cl.info('Starting to retrieve query: %s, or org: %s' % (query, ghapi_org))
    cl.info('From data source: %s' % data_source)
    cl.info('Using proxy: %s' % proxy)

    if proxy:
        os.environ['HTTP_PROXY'] = proxy
        os.environ['HTTPS_PROXY'] = proxy

    if data_source == 'twitter_standard_api':
        data = twapi_search(query, twapi_max, sleep_time=twapi_sleep_time,
                            lang=lang)
    elif data_source == 'twitterscraper':
        data = twscrape_search(query, lang=lang, poolsize=twscrape_poolsize,
                               begindate=twscrape_begindate)
    elif data_source == 'github_api':
        data = github_issue_org_fetch(ghapi_org, ghapi_since)
    else:
        cl.error('Data source %r is not implemented' % data_source)
        sys.exit(-1)

    export_csv(data, data_source_file(save_filename))
