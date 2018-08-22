import collections
import re

import colorlabels as cl

from util import (TimeMeasure, csv_reader, data_source_file, export_csv,
                  name_with_title_suffix)


def preprocess_csv(csvfilename):
    cl.progress('Preprocessing file: %s' % csvfilename)

    grouped_tweets = collections.defaultdict(list)

    for row in csv_reader(csvfilename):
        grouped_tweets[row['user']].append(row['text'])

    for user in grouped_tweets:
        yield {
            'id': user,
            'text': ' '.join(grouped_tweets[user])
        }


def text_preprocessor_user(sourcedesc):
    cl.section('Text Preprocessor Grouping By User')

    assert re.fullmatch(r'[-_0-9a-zA-Z+]+', sourcedesc)

    csvfilename = data_source_file('%s.csv' % sourcedesc)

    with TimeMeasure('preprocess_text'):
        result = list(preprocess_csv(csvfilename))

    with TimeMeasure('save_preprocessed'):
        savefilename = name_with_title_suffix(csvfilename, '-user')
        export_csv(result, savefilename)
