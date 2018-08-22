import collections
import os
import re
import shutil
import string

import colorlabels as cl

from util import TimeMeasure, csv_reader, data_source_file, is_bad_filename

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


def preprocess_csv(csvfilename):
    cl.progress('Preprocessing file: %s' % csvfilename)
    preprocessor = TWLDAPreprocessor()
    grouped_tweets = collections.defaultdict(list)

    for row in csv_reader(csvfilename):
        result = preprocessor.preprocess(row['text'])
        grouped_tweets[row['user']].append(result)

    return grouped_tweets


def save_preprocessed(data, sourcedesc):
    output_dir = data_source_file('twlda-%s' % sourcedesc)
    shutil.rmtree(output_dir, ignore_errors=True)
    os.mkdir(output_dir)

    for user, tweets in data.items():
        output_filename = sanitize_filename(user) + '.txt'
        output_filename = os.path.join(output_dir, output_filename)

        with open(output_filename, 'w', encoding='utf-8') as outfile:
            for tweet in tweets:
                outfile.write('%s\n' % tweet)

    manifest_filename = data_source_file('twlda-manifest-%s.txt' % sourcedesc)
    with open(manifest_filename, 'w', encoding='utf-8') as manifestfile:
        for name in os.listdir(output_dir):
            manifestfile.write('%s\n' % name)

    cl.success('Preprocessed result saved in folder: %s' % output_dir)


def text_preprocessor_twlda(sourcedesc):
    cl.section('Text Preprocessor For Twitter-LDA')

    assert re.fullmatch(r'[-_0-9a-zA-Z+]+', sourcedesc)

    input_filename = data_source_file('%s.csv' % sourcedesc)

    with TimeMeasure('preprocess_text'):
        result = preprocess_csv(input_filename)

    with TimeMeasure('save_preprocessed'):
        save_preprocessed(result, sourcedesc)
