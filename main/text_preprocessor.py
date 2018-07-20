import csv
import json
import os
import re
import string

import colorlabels as cl
from nltk.stem.porter import PorterStemmer
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words

from util import TimeMeasure, data_source_file

tokenizer = RegexpTokenizer(r"[-_0-9a-zA-Z#*+&/']+")
stop_words = get_stop_words('en')
p_stemmer = PorterStemmer()


def load_text(csvfilename):
    with open(csvfilename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            yield row['text']


def sanitize_text(text):
    text = re.sub(r'[^\x00-\x7f]+', ' ', text)  # Remove non-ascii characters.
    text = re.sub(r'https?://([-0-9a-z]+\.)*[-0-9a-z]+(/[\x01-\x7e]*)?', ' ',
                  text, flags=re.IGNORECASE)    # Remove URLs.
    text = text.lower()
    text = text.strip()
    return text


def tokenize(text):
    return tokenizer.tokenize(text)


def sanitize_tokens(tokens):
    for token in tokens:
        # Remove '#' in hashtags and '@' in mentions
        if token.startswith('#') or token.startswith('@'):
            token = token[1:]

        # Remove tokens that are only composed of special characters.
        if all(c in string.punctuation for c in token):
            continue

        # Remove tokens that are only composed of numbers.
        if token.isnumeric():
            continue

        yield token


def remove_stop_words(tokens, custom_stop_words=None):
    all_stop_words = stop_words.copy()

    if custom_stop_words:
        all_stop_words += custom_stop_words

    return (t for t in tokens if t not in all_stop_words)


def stem(tokens):
    return (p_stemmer.stem(token) for token in tokens)


def preprocess_text(csvfilename, custom_stop_words=None):
    cl.progress('Preprocessing file: %s' % csvfilename)

    for text in load_text(csvfilename):
        sanitized_text = sanitize_text(text)
        tokenized_text = tokenize(sanitized_text)
        sanitized_tokens = sanitize_tokens(tokenized_text)
        stopped_tokens = remove_stop_words(sanitized_tokens, custom_stop_words)
        stemmed_tokens = stem(stopped_tokens)
        result = list(stemmed_tokens)

        if result:
            yield result


def save_preprocessed(data, csvfilename):
    output_filename = os.path.splitext(csvfilename)[0] + '.prep.json'

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile)

    cl.success('Preprocessed result saved as: %s' % output_filename)


def text_preprocessor(input_filename, custom_stop_words=None):
    cl.section('Text Preprocessor')

    input_filename = data_source_file(input_filename)

    with TimeMeasure('preprocess_text'):
        result = list(preprocess_text(input_filename, custom_stop_words))

    with TimeMeasure('save_preprocessed'):
        save_preprocessed(result, input_filename)
