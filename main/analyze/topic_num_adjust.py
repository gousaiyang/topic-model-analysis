from ..model import twitter_lda

import colorlabels as cl


def twlda_multiple_run(min_topics, max_topics, iteration):
    cl.section('Twitter-LDA Multiple Run')

    for topics in range(min_topics, max_topics + 1):
        cl.info('Running with %d topics' % topics)
        twitter_lda(output_desc='test-%d' % topics, topics=topics,
                    iteration=iteration)


def plot_diff_topics():
    raise NotImplementedError
