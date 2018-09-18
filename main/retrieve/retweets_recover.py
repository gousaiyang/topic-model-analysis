import os

import colorlabels as cl

from scraper import twapi
from util import (csv_reader, data_source_file, export_csv, get_exc_line,
                  merge_whitespaces, name_with_title_suffix)


def recover_from_csv(csvfilename):
    progress = 0

    for row in csv_reader(csvfilename):
        progress += 1

        if progress % 1000 == 0:
            cl.progress('%d record(s) have been recovered' % progress)

        yield row

        if int(row['retweets']):
            try:
                retweets = twapi.GetRetweets(int(row['id']), count=100)
            except Exception:
                cl.warning('Error: %s' % get_exc_line())
            else:
                for tweet in retweets:
                    yield {
                        'id': tweet.id_str,
                        'text': row['text'],
                        'timestamp': tweet.created_at,
                        'likes': tweet.favorite_count,
                        'retweets': tweet.retweet_count,
                        'replies': None,
                        'url': None,
                        'html': None,
                        'user': merge_whitespaces(tweet.user.screen_name),
                        'fullname': merge_whitespaces(tweet.user.name)
                    }


def retweets_recover(csvfilename):
    cl.section('Retweets Recover')
    cl.info('Recovering file: %s' % csvfilename)

    csvfilename = data_source_file(csvfilename)
    result = recover_from_csv(csvfilename)
    exportfilename = name_with_title_suffix(csvfilename, '-recovered')
    export_csv(result, exportfilename)
    return os.path.basename(exportfilename)
