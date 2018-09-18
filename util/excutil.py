import traceback

import colorlabels as cl


def get_exc_line():
    return traceback.format_exc().splitlines()[-1]


def retry_until_success(func, *args, **kwargs):
    ret = None

    while True:
        try:
            try:
                ret = func(*args, **kwargs)
            except KeyboardInterrupt:
                raise
            except Exception:
                cl.error('Error: %s. Retrying...' % get_exc_line())
            else:
                return ret
        except KeyboardInterrupt:
            cl.warning('User hit Ctrl-C, terminating function %r'
                       % func.__name__)
            raise
