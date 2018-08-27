import collections
import os
import re
import shutil

import colorlabels as cl

from util import (TimeMeasure, csv_reader, data_source_file, file_write_lines,
                  is_bad_filename, twlda_data_file, twlda_source_file)

from .text_preprocessor import TwitterPreprocessor


def sanitize_filename(filename):
    if is_bad_filename(filename):
        return 'renamed-%s' % filename.encode().hex()
    else:
        return filename


class TWLDAPreprocessor(TwitterPreprocessor):
    def preprocess(self, text):
        sanitized_text = self._text_sanitizer(text)
        tokenized_text = self._text_tokenizer(sanitized_text)
        sanitized_tokens = self._token_sanitizer(tokenized_text)
        return ' '.join(sanitized_tokens)


def preprocess_csv(csvfilename, tweet_min_length, user_min_tweets,
                   remove_duplicates):
    cl.progress('Preprocessing file: %s' % csvfilename)
    preprocessor = TWLDAPreprocessor()
    grouped_tweets = collections.defaultdict(list)

    for row in csv_reader(csvfilename):
        user = row['user']
        result = preprocessor.preprocess(row['text'])

        if len(result) >= tweet_min_length:
            if remove_duplicates and result in grouped_tweets[user]:
                continue

            grouped_tweets[user].append(result)

    grouped_tweets = {u: t for u, t in grouped_tweets.items()
                      if len(t) >= user_min_tweets}
    return grouped_tweets


def save_preprocessed(data):
    output_dir = twlda_source_file('test')
    shutil.rmtree(output_dir, ignore_errors=True)
    os.mkdir(output_dir)

    for user, tweets in data.items():
        output_filename = sanitize_filename(user) + '.txt'
        output_filename = os.path.join(output_dir, output_filename)
        file_write_lines(output_filename, tweets)

    manifest_filename = twlda_data_file('filelist_test.txt')
    file_write_lines(manifest_filename, os.listdir(output_dir))

    cl.success('Preprocessed result saved in folder: %s' % output_dir)


def text_preprocessor_twlda(sourcedesc, *, tweet_min_length=3,
                            user_min_tweets=1, remove_duplicates=False):
    cl.section('Text Preprocessor For Twitter-LDA')

    assert re.fullmatch(r'[-_0-9a-zA-Z+]+', sourcedesc)

    input_filename = data_source_file('%s.csv' % sourcedesc)

    with TimeMeasure('preprocess_text'):
        result = preprocess_csv(input_filename, tweet_min_length,
                                user_min_tweets, remove_duplicates)

    with TimeMeasure('save_preprocessed'):
        save_preprocessed(result)
