import colorlabels as cl
import matplotlib.pyplot as plt

from util import parse_data_from_log, report_file, twlda_result_file

from ..model import LOGFILE, twitter_lda


def twlda_multiple_run(num_topics_range, iteration, desc_prefix,
                       show_console_output=True):
    cl.section('Twitter-LDA Multiple Run')

    for topics in num_topics_range:
        cl.info('Running with %d topics' % topics)
        twitter_lda(output_desc='%s-%d' % (desc_prefix, topics), topics=topics,
                    iteration=iteration,
                    show_console_output=show_console_output)


def plot_diff_topics(num_topics_range, desc_prefix, regex, encoding='utf-8'):
    plt.title('Perplexity under Different Number of Topics')
    plt.xlabel('topics')
    plt.ylabel('perplexity')

    data_x = []
    data_y = []

    num_topics_range = list(num_topics_range)

    for topics in num_topics_range:
        logfilename = twlda_result_file('%s-%d/%s' % (desc_prefix, topics,
                                                      LOGFILE))
        perplexity = parse_data_from_log(logfilename, encoding=encoding,
                                         regex_y=regex, cast_y=float)[1][-1]
        data_x.append(topics)
        data_y.append(perplexity)

    minima_points = [data_x[x] for x in range(1, len(data_x) - 1)
                     if data_y[x - 1] > data_y[x]
                     and data_y[x] < data_y[x + 1]]

    plt.plot(data_x, data_y)
    plt.xticks(num_topics_range)
    plt.figtext(0.5, 0, '* Minima points indicate possibly better training '
                'results.', wrap=True, horizontalalignment='center',
                fontsize=9)

    plot_filename = 'ldaplot-%s.png' % desc_prefix
    plt.savefig(report_file(plot_filename), bbox_inches='tight')
    return plot_filename, minima_points
