import colorlabels as cl
import matplotlib.pyplot as plt

from util import parse_data_from_log, twlda_result_file

from ..model import LOGFILE, twitter_lda


def twlda_multiple_run(min_topics, max_topics, iteration):
    cl.section('Twitter-LDA Multiple Run')

    for topics in range(min_topics, max_topics + 1):
        cl.info('Running with %d topics' % topics)
        twitter_lda(output_desc='test-%d' % topics, topics=topics,
                    iteration=iteration)


def plot_diff_topics(min_topics, max_topics, regex, encoding='utf-8'):
    plt.title('Different Number of Topics')
    plt.xlabel('topics')
    plt.ylabel('perplexity')

    data_x = []
    data_y = []

    for topics in range(min_topics, max_topics + 1):
        logfilename = twlda_result_file('test-%d/%s' % (topics, LOGFILE))
        perplexity = parse_data_from_log(logfilename, encoding=encoding,
                                         regex_y=regex, cast_y=float)[1][-1]
        data_x.append(topics)
        data_y.append(perplexity)

    plt.plot(data_x, data_y)
    plt.show()
