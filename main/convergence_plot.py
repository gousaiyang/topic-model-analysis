import re

import matplotlib.pyplot as plt

from util import log_file


def parse_log(logfilename):
    with open(logfilename, 'r', encoding='utf-8') as logfile:
        text = logfile.read()

    result = re.findall(r'(\S+) per-word bound, (\S+) perplexity', text)
    return [float(item[1]) for item in result]


def plot_one(data, label):
    list_x = list(range(len(data)))
    plt.plot(list_x, data, label=label)


def convergence_plot(modeldescs):
    plt.title('Topic Model Convergence Plot')
    plt.xlabel('passes')
    plt.ylabel('perplexity')

    for modeldesc in modeldescs:
        logfilename = log_file('ldalog-%s.log' % modeldesc)
        data = parse_log(logfilename)
        plot_one(data, modeldesc.split('-')[-1])

    plt.legend()
    plt.show()
