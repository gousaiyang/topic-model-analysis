import os
import sys

import colorlabels as cl

from scraper import (github_issue_org_fetch, soapi_search, twapi_search,
                     twscrape_search)
from util import (data_source_file, export_csv, get_exc_line,
                  name_with_title_suffix)


def iterator_aggregate_list(data):
    if hasattr(data, '__next__'):
        result = []

        try:
            result.extend(data)
        except Exception:
            cl.warning('Exception happened while collecting data: %s'
                       % get_exc_line())
        except KeyboardInterrupt:
            cl.warning('User hit Ctrl-C. Will not collect more data.')

        return result
    elif isinstance(data, list):
        return data
    else:
        return list(data)


def remove_duplicate_text(data):
    seen = set()

    for item in data:
        if item['text'] not in seen:
            seen.add(item['text'])
            yield item


def data_retriever(data_source, query, save_filename, *, lang='', proxy=None,
                   remove_duplicates=False, twapi_max=None, twapi_sleep_time=0,
                   twscrape_poolsize=20, twscrape_begindate=None,
                   ghapi_org=None, ghapi_since=None, soapi_begindate=None):
    cl.section('Data Retriever')
    cl.info('Starting to retrieve query: %s, or org: %s' % (query, ghapi_org))
    cl.info('From data source: %s' % data_source)
    cl.info('Using proxy: %s' % proxy)
    cl.info('Remove duplicates: %s' % remove_duplicates)

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
    elif data_source == 'stackoverflow_api':
        data = soapi_search(query, begindate=soapi_begindate)
    else:
        cl.error('Data source %r is not implemented' % data_source)
        sys.exit(-1)

    if remove_duplicates:
        data = iterator_aggregate_list(data)
        data_no_duplicate_text = remove_duplicate_text(data)
        cl.info('Exporting data without duplicate text')
        export_csv(data_no_duplicate_text, data_source_file(save_filename))

        save_filename_full = name_with_title_suffix(save_filename, '-full')
        cl.info('Exporting full data')
        export_csv(data, data_source_file(save_filename_full))
    else:
        export_csv(data, data_source_file(save_filename))
