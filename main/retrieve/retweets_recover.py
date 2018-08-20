import csv

import colorlabels as cl

from scraper import twapi
from util import (data_source_file, export_csv, merge_whitespaces,
                  name_with_title_suffix, set_csv_field_size_limit)


def recover_from_csv(csvfilename):
    set_csv_field_size_limit()
    progress = 0

    with open(csvfilename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            progress += 1

            if progress % 1000 == 0:
                cl.progress('%d record(s) have been recovered' % progress)

            yield row

            if int(row['retweets']):
                try:
                    retweets = twapi.GetRetweets(int(row['id']), count=100)
                except Exception as e:
                    cl.warning('Error: %s' % e)
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
