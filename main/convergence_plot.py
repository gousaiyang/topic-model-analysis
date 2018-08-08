import re

import matplotlib.pyplot as plt

from util import log_file


def parse_metrics(logfilename):
    with open(logfilename, 'r', encoding='utf-8') as logfile:
        text = logfile.read()

    result = re.findall(r'(\S+) per-word bound, (\S+) perplexity', text)
    return [float(item[1]) for item in result]


def plot_metric(data, metric_name, modeldesc):
    list_x = list(range(len(data)))
    plt.plot(list_x, data)
    plt.xlabel('passes')
    plt.ylabel(metric_name)
    plt.title('Topic Model Convergence Plot\nModel: %s' % modeldesc)
    plt.show()


def convergence_plot(modeldesc):
    logfilename = log_file('ldalog-%s.log' % modeldesc)
    data = parse_metrics(logfilename)
    plot_metric(data, 'perplexity', modeldesc)
