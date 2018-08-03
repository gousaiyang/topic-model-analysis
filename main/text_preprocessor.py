import csv
import json
import os
import re
import string

import colorlabels as cl
from nltk.stem.wordnet import WordNetLemmatizer
from nltk.tokenize import RegexpTokenizer
from stop_words import get_stop_words

from util import (TimeMeasure, data_source_file, name_replace_ext,
                  remove_emails, remove_html_comments,
                  remove_markdown_codeblocks, remove_non_asciiprintable,
                  remove_twitter_pic_urls, remove_urls,
                  set_csv_field_size_limit)


class TextPreprocessor:
    _token_regex = r'\w+'
    _lang = 'en'
    _lem_ignore_patterns = []

    def __init__(self, *, token_regex=None, lang=None, custom_stop_words=None,
                 lem_ignore_patterns=None):
        self._tokenizer = RegexpTokenizer(token_regex or self._token_regex)
        self._stop_words = get_stop_words(lang or self._lang)

        if custom_stop_words:
            self._stop_words.extend(custom_stop_words)

        self._lemmatizer = WordNetLemmatizer()

        if lem_ignore_patterns:
            self._lem_ignore_patterns.extend(lem_ignore_patterns)

    def _text_sanitizer(self, text):
        return text

    def _text_tokenizer(self, text):
        return self._tokenizer.tokenize(text)

    def _token_sanitizer(self, tokens):
        return tokens

    def _stop_words_remover(self, tokens):
        return (t for t in tokens if t not in self._stop_words)

    def _word_lemmatizer(self, tokens):
        for token in tokens:
            if any(re.fullmatch(p, token) for p in self._lem_ignore_patterns):
                yield token
            else:
                yield self._lemmatizer.lemmatize(token)

    def preprocess(self, text):
        sanitized_text = self._text_sanitizer(text)
        tokenized_text = self._text_tokenizer(sanitized_text)
        sanitized_tokens = self._token_sanitizer(tokenized_text)
        stopped_tokens = self._stop_words_remover(sanitized_tokens)
        lemmatized_tokens = self._word_lemmatizer(stopped_tokens)
        result = tuple(lemmatized_tokens)
        return result


class TwitterPreprocessor(TextPreprocessor):
    _token_regex = r"[-0-9a-zA-Z#+&']+"
    _lem_ignore_patterns = [r'\ws']

    def _text_sanitizer(self, text):
        text = remove_non_asciiprintable(text, ' ')
        text = remove_urls(text, ' ')
        text = remove_twitter_pic_urls(text, ' ')
        text = remove_emails(text, ' ')
        text = text.lower()
        text = text.strip()
        return text

    def _token_sanitizer(self, tokens):
        for token in tokens:
            # Remove '#' in hashtags.
            if token.startswith('#'):
                token = token[1:]

            # Remove "'s" and "'d" at end of token.
            if token.endswith("'s") or token.endswith("'d"):
                token = token[:-2]

            # Remove tokens that are only composed of special characters.
            if all(c in string.punctuation for c in token):
                continue

            # Remove tokens that are only composed of numbers.
            if token.isnumeric():
                continue

            # Remove one-character tokens, except 'c' and 'r'.
            if len(token) == 1 and token not in ('c', 'r'):
                continue

            yield token


class GitHubPreprocessor(TextPreprocessor):
    _token_regex = r"[-0-9a-zA-Z#+&']+"
    _lem_ignore_patterns = [r'\ws']

    def _text_sanitizer(self, text):
        text = remove_non_asciiprintable(text, ' ')
        text = remove_urls(text, ' ')
        text = remove_emails(text, ' ')
        text = remove_html_comments(text, ' ')
        text = remove_markdown_codeblocks(text, ' ')
        text = text.lower()
        text = text.strip()
        return text

    def _token_sanitizer(self, tokens):
        for token in tokens:
            # Remove '#' in hashtags.
            if token.startswith('#'):
                token = token[1:]

            # Remove "'s" and "'d" at end of token.
            if token.endswith("'s") or token.endswith("'d"):
                token = token[:-2]

            # Remove quotes at start and end of token.
            token = token.strip('\'"')

            # Remove tokens that are only composed of special characters.
            if all(c in string.punctuation for c in token):
                continue

            # Remove tokens that are only composed of numbers.
            if token.isnumeric():
                continue

            # Remove one-character tokens, except 'c' and 'r'.
            if len(token) == 1 and token not in ('c', 'r'):
                continue

            yield token


def preprocess_csv(csvfilename, *, preprocessor_cls=TextPreprocessor,
                   custom_stop_words=None, lem_ignore_patterns=None):
    cl.progress('Preprocessing file: %s' % csvfilename)

    preprocessor = preprocessor_cls(custom_stop_words=custom_stop_words,
                                    lem_ignore_patterns=lem_ignore_patterns)

    set_csv_field_size_limit()

    with open(csvfilename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            result = preprocessor.preprocess(row['text'])

            if result:
                yield row['id'], result


def remove_duplicate_text(data):
    seen = set()

    for item in data:
        if item[1] not in seen:
            seen.add(item[1])
            yield item


def save_preprocessed(data, csvfilename):
    output_filename = name_replace_ext(csvfilename, '.prep.json')

    with open(output_filename, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile)

    cl.success('Preprocessed result saved as: %s' % output_filename)


def text_preprocessor(input_filename, *, preprocessor_cls='TextPreprocessor',
                      custom_stop_words=None, lem_ignore_patterns=None):
    cl.section('Text Preprocessor')

    input_filename = data_source_file(input_filename)
    preprocessor_cls = globals()[preprocessor_cls]

    with TimeMeasure('preprocess_text'):
        result = preprocess_csv(input_filename,
                                preprocessor_cls=preprocessor_cls,
                                custom_stop_words=custom_stop_words,
                                lem_ignore_patterns=lem_ignore_patterns)
        result = remove_duplicate_text(result)
        result = tuple(result)
        cl.info('Effective data size: %d' % len(result))

    with TimeMeasure('save_preprocessed'):
        save_preprocessed(result, input_filename)
