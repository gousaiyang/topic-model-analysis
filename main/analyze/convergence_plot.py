import matplotlib.pyplot as plt

from util import parse_data_from_log


def convergence_plot(logfiles, labels, *, regex_x=None, regex_y):
    plt.title('Topic Model Convergence Plot')
    plt.xlabel('iterations')
    plt.ylabel('perplexity')

    for logfile, label in zip(logfiles, labels):
        data_x, data_y = parse_data_from_log(logfile, regex_x=regex_x,
                                             regex_y=regex_y, cast_x=int,
                                             cast_y=float)
        plt.plot(data_x, data_y, label=label)

    plt.legend()
    plt.show()
