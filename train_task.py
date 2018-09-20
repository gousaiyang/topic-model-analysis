import contextlib
import os
import time
import zipfile

import colorlabels as cl
from decouple import config

from main import (plot_diff_topics, text_preprocessor_twlda, twitter_lda,
                  visualization_twlda)
from util import TimeMeasure, pipe_encoding, report_file, retry_until_success

# Adjust working directory to current script directory (project root).
os.chdir(os.path.dirname(os.path.abspath(__file__)))

# Set NO_COLOR=True or NO_COLOR=1 to disable color output.
if config('NO_COLOR', cast=bool, default=False):
    cl.config(color_span=0)

# Parameters
KEYWORD = 'Java'  # Only shown on the final report.
MIN_TOPICS = 6  # Minimum number of topics for training.
MAX_TOPICS = 30  # Maximum number of topics for training.
ITERATIONS = 4000  # The number of iterations for training.
REPORT_ONLY_MINIMA = True  # Whether only to generate reports at minima points.


def compress_report_files(tag, report_files):
    os.chdir(report_file(''))
    zipfilename = 'ldareport-%s.zip' % tag

    with zipfile.ZipFile(zipfilename, 'w', zipfile.ZIP_DEFLATED) as zf:
        for f in report_files:
            zf.write(f)

    for f in report_files:
        with contextlib.suppress(Exception):
            os.remove(f)

    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    cl.success('Report files archived into: %s' % zipfilename)
    return zipfilename


def main():
    tag = time.strftime('java-%Y%m%d%H%M%S')
    tweets_file_recovered = 'twdata-java-recovered.csv'
    userinfo_file = 'twusers-java.csv'
    num_topics_range = list(range(MIN_TOPICS, MAX_TOPICS + 1))

    # Preprocess
    retry_until_success(text_preprocessor_twlda, tweets_file_recovered[:-4],
                        tweet_min_length=2, user_min_tweets=1,
                        remove_duplicates=True)

    # Train (with different number of topics)
    for topics in num_topics_range:
        cl.info('Running with %d topics' % topics)
        retry_until_success(twitter_lda, output_desc='java-%d' % topics,
                            topics=topics, iteration=ITERATIONS,
                            show_console_output=True)

    # Analyze (Perplexity Plot + HTML Reports + Compress)
    report_files = []
    plot_file, minima_points = plot_diff_topics(num_topics_range, 'java',
                                                r'Perplexity is ([\d.]+)',
                                                pipe_encoding)
    report_files.append(plot_file)
    report_points = minima_points if REPORT_ONLY_MINIMA else num_topics_range

    for topics in report_points:
        report_files.append(visualization_twlda(KEYWORD,
                                                'java-%d' % topics,
                                                '%s-%d' % (tag, topics),
                                                userinfo_file,
                                                open_browser=False))
    compress_report_files(tag, report_files)


if __name__ == '__main__':
    with TimeMeasure('train_task'):
        main()
