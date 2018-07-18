import functools
import re
import timeit

import colorlabels as cl


def merge_whitespaces(text):
    return re.sub(r'\s+', ' ', text)


def pretty_time(seconds):
    hours = seconds // 3600
    minutes = seconds % 3600 // 60
    seconds = seconds % 60
    return ' '.join(filter(bool, [
        '%d hour(s)' % hours if hours else '',
        '%d minute(s)' % minutes if minutes else '',
        '%.2f second(s)' % seconds if seconds else ''
    ]))


def time_measure(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t_start = timeit.default_timer()
        ret = func(*args, **kwargs)
        t_end = timeit.default_timer()
        time_str = pretty_time(t_end - t_start)
        cl.info("Function '%s' cost time: %s" % (func.__name__, time_str))
        return ret

    return wrapper


class TimeMeasure:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        self.t_start = timeit.default_timer()
        return self

    def __exit__(self, type_, value, trace):
        self.t_end = timeit.default_timer()
        time_str = pretty_time(self.t_end - self.t_start)
        cl.info("Procedure '%s' cost time: %s" % (self.name, time_str))
